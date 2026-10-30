#!/usr/bin/env python3
"""Time each drum hit near a predicted beat, then least-squares fit the grid to the hits.
usage: hits.py <wav> <first_hit_s> <period_s> <n_beats> [--band lo hi] [--every k]
For each beat k (every --every beats), find the steepest rise of the band's level (dB, 12 ms frames, 1.5 ms hop)
within +-60 ms of the prediction. Prints the fitted period/phase and residuals; hits with a weak rise are dropped."""
import subprocess, sys
import numpy as np
SR = 22050
wav, t0, p, nb = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), int(sys.argv[4])
lo, hi = (30, 130)
if "--band" in sys.argv:
    i = sys.argv.index("--band"); lo, hi = float(sys.argv[i + 1]), float(sys.argv[i + 2])
every = int(sys.argv[sys.argv.index("--every") + 1]) if "--every" in sys.argv else 1
a, b = t0 - 0.5, t0 + nb * p + 0.5
x = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-ss", str(max(0, a)), "-t", str(b - a), "-i", wav, "-ac", "1",
                                  "-ar", str(SR), "-f", "f32le", "-"], capture_output=True, check=True).stdout, np.float32)
a = max(0, a)
N, H = 1024, 32
win = np.hanning(N).astype(np.float32)
n = 1 + (len(x) - N) // H
fr = np.lib.stride_tricks.as_strided(x, (n, N), (x.strides[0] * H, x.strides[0]))
P = np.abs(np.fft.rfft(fr * win, axis=1)) ** 2
f = np.fft.rfftfreq(N, 1 / SR)
lv = 10 * np.log10(P[:, (f >= lo) & (f < hi)].sum(axis=1) + 1e-9)
t = a + (np.arange(n) * H + N / 2) / SR
d = np.gradient(lv) / (H / SR)          # dB per second
ks, ts, rises = [], [], []
for k in range(0, nb + 1, every):
    pt = t0 + k * p
    m = (t > pt - 0.06) & (t < pt + 0.06)
    if not m.any(): continue
    j = np.flatnonzero(m)[d[m].argmax()]
    # rise over the next 30 ms must be big: a real hit
    j2 = min(len(lv) - 1, j + int(0.03 * SR / H)); j0 = max(0, j - int(0.03 * SR / H))
    rise = lv[j2] - lv[j0]
    ks.append(k); ts.append(t[j]); rises.append(rise)
ks, ts, rises = map(np.array, (ks, ts, rises))
good = rises > max(6.0, 0.35 * np.median(rises))
A = np.vstack([ks[good], np.ones(good.sum())]).T
(pp, ph), *_ = np.linalg.lstsq(A, ts[good], rcond=None)
res = 1000 * (ts[good] - (ph + pp * ks[good]))
print(f"hits used {good.sum()}/{len(ks)}  period {pp:.6f} s = {60/pp:.3f} bpm  beat0 {ph:.4f} s  resid median|{np.median(np.abs(res)):.1f}| max|{np.abs(res).max():.1f}| ms")
print("dropped beats:", [int(k) for k in ks[~good]])
