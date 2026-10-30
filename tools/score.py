#!/usr/bin/env python3
"""Put one of the five score cards under the film: every cut and beat re-timed to that track.

usage: python3 tools/score.py deep-house | spy-lounge | synthwave | amapiano | city-pop

The film is 32 beats: the opener 8, three looks 4 each, the wording card 6, the end card 6. Each cut sits on the
frame at or before its beat. Writes film.html, assets/beats.json, assets/bed.wav, and each shot's length (D) and
start on the film (AT) in scenes/. A bed in scores/ starts 1 s before the film's first beat ("in"), already
loudness-matched, so the clip's media fragment picks the window and nothing is re-encoded."""
import json, math, re, shutil, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SHOTS = [(1, 0), (2, 8), (3, 12), (4, 16), (5, 20), (6, 26)]   # (shot, its first beat)
BEATS, FPS = 32, 30

scores = json.loads((ROOT / "scores" / "scores.json").read_text())
if len(sys.argv) != 2 or sys.argv[1] not in scores:
    raise SystemExit("usage: python3 tools/score.py " + " | ".join(scores))
name = sys.argv[1]
s = scores[name]
p, length = s["period"], BEATS * s["period"]
on_frame = lambda t: math.floor(t * FPS + 1e-6) / FPS
cut = {n: round(on_frame(k * p), 3) for n, k in SHOTS}
ends = {n: (cut[n + 1] if n < 6 else round(length, 3)) for n, _ in SHOTS}

def setnum(path, key, val):
    text = path.read_text()
    new, n = re.subn(rf"(\b{key}\s*[:=]\s*)\d+(?:\.\d+)?", lambda m: f"{m.group(1)}{val:.3f}", text, count=1)
    if n != 1:
        raise SystemExit(f"{path.name}: no {key}")
    path.write_text(new)

for n, _ in SHOTS:
    page = ROOT / "scenes" / f"shot-{n}.html"
    setnum(page, "D", ends[n] - cut[n])
    if n > 1:
        setnum(page, "AT", cut[n])

(ROOT / "assets" / "beats.json").write_text(json.dumps({
    "score": s["card"], "bpm": s["bpm"], "period": p,
    "note": "fitted to the track's own drum hits (tools/beat); beat k of the film is at k * period",
    "beats": [round(k * p, 4) for k in range(BEATS + 4)]}, indent=1) + "\n")
shutil.copyfile(ROOT / "scores" / f"{name}.wav", ROOT / "assets" / "bed.wav")

lines = ['<!doctype html>', '<html>', '<head>', '<meta charset="utf-8">', '<meta name="viewport" content="width=1920, height=1080">',
         '</head>', '<body>', '<section>']
lines += [f'  <iframe src="scenes/shot-{n}.html"' + (f' at="{cut[n]:.3f}"' if n > 1 else '') + '></iframe>' for n, _ in SHOTS]
lines += ['</section>', '<section>',
          f'  <audio id="bed" src="assets/bed.wav#t={s["in"]:.3f},{s["in"] + length:.3f}" overrides=\'[{{"fade":[0.02,1.2]}}]\'></audio>',
          '</section>', '</body>', '</html>']
(ROOT / "film.html").write_text("\n".join(lines) + "\n")
print(f"{s['card']}: {s['bpm']} bpm, {length:.3f} s, cuts at " + ", ".join(f"{cut[n]:.3f}" for n, _ in SHOTS[1:]))
