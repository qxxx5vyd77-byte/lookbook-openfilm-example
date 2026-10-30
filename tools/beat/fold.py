#!/usr/bin/env python3
"""Fold band envelopes modulo the beat to see where kick, bass and hats sit inside one beat.
usage: fold.py <wav> <from> <to> <period> <phase0>   (phase0: any beat time from a fit; bins are 1/24 beat after it)"""
import subprocess, sys
import numpy as np
SR = 22050
wav, a, b, p, ph = sys.argv[1], *map(float, sys.argv[2:6])
x = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-ss", str(a), "-t", str(b - a), "-i", wav, "-ac", "1",
                                  "-ar", str(SR), "-f", "f32le", "-"], capture_output=True, check=True).stdout, np.float32)
N, H = 512, 64
win = np.hanning(N).astype(np.float32)
n = 1 + (len(x) - N) // H
fr = np.lib.stride_tricks.as_strided(x, (n, N), (x.strides[0] * H, x.strides[0]))
P = np.abs(np.fft.rfft(fr * win, axis=1)) ** 2
f = np.fft.rfftfreq(N, 1 / SR)
t = a + (np.arange(n) * H + N / 2) / SR
B = {"sub<130": (30, 130), "mid300-2k": (300, 2000), "hi6-11k": (6000, 11000)}
nb = 24
ph_bin = (((t - ph) / p) % 1 * nb).astype(int)
print("bin  frac  " + "  ".join(f"{k:>10}" for k in B))
prof = {k: np.array([10 * np.log10(P[ph_bin == i][:, (f >= lo) & (f < hi)].sum(axis=1).mean() + 1e-12) for i in range(nb)]) for k, (lo, hi) in B.items()}
for i in range(nb):
    print(f"{i:3d}  {i/nb:4.2f}  " + "  ".join(f"{prof[k][i] - prof[k].max():10.1f}" for k in B))
