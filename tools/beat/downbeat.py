#!/usr/bin/env python3
"""Which beat of the bar is 1? Chords and bass notes change most on the downbeat: score each beat class (k mod 4) by the
spectral change across it (log-magnitude 80-2000 Hz, one beat before vs one beat after, cosine distance).
usage: downbeat.py <wav> <from> <to> <period> <beat_time>"""
import subprocess, sys
import numpy as np
SR = 22050
wav, a, b, p, bt = sys.argv[1], *map(float, sys.argv[2:6])
x = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", wav, "-af", f"atrim=start={a}:end={b}", "-ac", "1",
                                  "-ar", str(SR), "-f", "f32le", "-"], capture_output=True, check=True).stdout, np.float32)
N, H = 4096, 512
win = np.hanning(N).astype(np.float32)
n = 1 + (len(x) - N) // H
fr = np.lib.stride_tricks.as_strided(x, (n, N), (x.strides[0] * H, x.strides[0]))
mag = np.abs(np.fft.rfft(fr * win, axis=1))
f = np.fft.rfftfreq(N, 1 / SR)
L = np.log1p(50 * mag[:, (f >= 80) & (f < 2000)])
t = a + (np.arange(n) * H + N / 2) / SR
k0 = int(np.ceil((a + p - bt) / p)); k1 = int(np.floor((b - p - bt) / p))
nov = {}
for k in range(k0, k1 + 1):
    c = bt + k * p
    pre, post = L[(t >= c - p) & (t < c)].mean(axis=0), L[(t >= c) & (t < c + p)].mean(axis=0)
    nov[k] = 1 - np.dot(pre, post) / (np.linalg.norm(pre) * np.linalg.norm(post) + 1e-9)
sc = [np.mean([v for k, v in nov.items() if k % 4 == r]) for r in range(4)]
best = int(np.argmax(sc))
print("class scores (beat_time + k*period, k mod 4):", [round(s * 1000, 2) for s in sc], "-> downbeats at", round(bt + best * p, 4), "+ n*", round(4 * p, 4))
sc8 = [np.mean([v for k, v in nov.items() if k % 8 == r]) for r in range(8)]
print("k mod 8:", [round(s * 1000, 2) for s in sc8])
