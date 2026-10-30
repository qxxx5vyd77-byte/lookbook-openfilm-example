#!/usr/bin/env python3
"""Per-bar band energy map of a song on its fitted grid. usage: bars.py <wav> <grid.json>
Prints one row per bar: bar index, start s, dB in sub (30-120 Hz), low-mid (120-400), mid (400-2k), presence (2k-5k), air (5k-14k)."""
import json, subprocess, sys
import numpy as np
SR = 22050
wav, grid = sys.argv[1], json.load(open(sys.argv[2]))
x = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", wav, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                                 capture_output=True, check=True).stdout, np.float32)
N, H = 2048, 512
win = np.hanning(N).astype(np.float32)
n = 1 + (len(x) - N) // H
fr = np.lib.stride_tricks.as_strided(x, (n, N), (x.strides[0] * H, x.strides[0]))
P = (np.abs(np.fft.rfft(fr * win, axis=1)) ** 2).astype(np.float64)
f = np.fft.rfftfreq(N, 1 / SR)
bands = {"sub": (30, 120), "lowmid": (120, 400), "mid": (400, 2000), "pres": (2000, 5000), "air": (5000, 11000)}
E = {k: P[:, (f >= a) & (f < b)].sum(axis=1) for k, (a, b) in bands.items()}
t = (np.arange(n) * H + N / 2) / SR
bar, d0 = grid["bar"], grid["downbeat0"]
first = -int(d0 // bar)
k = first
print("bar   start  " + "  ".join(f"{b:>6}" for b in bands))
while d0 + k * bar < t[-1]:
    a, b = d0 + k * bar, d0 + (k + 1) * bar
    m = (t >= a) & (t < b)
    if m.any():
        print(f"{k:3d} {a:7.2f}  " + "  ".join(f"{10*np.log10(E[q][m].mean()+1e-12):6.1f}" for q in bands))
    k += 1
