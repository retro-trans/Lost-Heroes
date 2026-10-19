"""Find where the sprites of a relabelled texture page are drawn on a game screenshot.

Renders the page as tex_edit builds it (composites and moved sprites included),
then slides each candidate sprite's alpha mask over the screenshot (scaled to
480x272) and reports the best normalised correlation. Used to lay out composites
(labels the game assembles from several sprites) without a sprite-draw log.

Candidates: --sprites 12,13 or, by default, every sprite that overlaps a text box
of the spec and is at most 24 px tall. A score above ~0.8 is a reliable match;
low scores usually mean the sprite is not on this screen.

Usage:
    python tools/sprite_match.py <spec.json> <screenshot> [--sprites a,b,...]
           [--region x0 y0 x1 y1] [--min 0.8] [--all] [--dark]
"""
import argparse
import json
import os

import numpy as np
from PIL import Image

import tex_edit

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ALLRES = os.path.join(ROOT, "work/source/iso/PSP_GAME/USRDIR/ALLRES.PCK")


def page(spec):
    blob = next(b for v, b in tex_edit.read_tpc(ALLRES, spec["tpc"]).items()
                if spec["page"] in {n for n, _ in tex_edit.tpc_pages(b)}
                and (not spec.get("exact") or v.split("::")[-1] == spec["tpc"]))
    if spec.get("gtx"):
        rects = list(tex_edit.composite_rects(ALLRES, spec))
        _, img, moved = tex_edit.apply_spec(spec, blob, rects)
        for k, v in moved.items():
            rects[k] = v
        return img, rects
    _, img = tex_edit.apply_spec(spec, blob)
    return img, []


def ncc_map(shot, mask):
    """Normalised cross-correlation of mask at every position of shot."""
    h, w = mask.shape
    win = np.lib.stride_tricks.sliding_window_view(shot, (h, w))
    m = mask - mask.mean()
    mn = np.sqrt((m * m).sum()) + 1e-9
    wm = win - win.mean(axis=(2, 3), keepdims=True)
    num = (wm * m).sum(axis=(2, 3))
    den = np.sqrt((wm * wm).sum(axis=(2, 3))) * mn + 1e-9
    return num / den


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("spec")
    ap.add_argument("shot")
    ap.add_argument("--sprites")
    ap.add_argument("--region", nargs=4, type=int, default=[0, 0, 480, 272])
    ap.add_argument("--min", type=float, default=0.0)
    ap.add_argument("--all", action="store_true", help="every position above --min, not just the best")
    ap.add_argument("--dark", action="store_true", help="the label is dark text on a light background")
    a = ap.parse_args()
    spec = json.load(open(a.spec, encoding="utf-8"))
    img, rects = page(spec)
    if a.sprites:
        cands = [int(s) for s in a.sprites.split(",")]
    else:
        cands = sorted({k for k, (x, y, w, h) in enumerate(rects) if h <= 24 for b in spec.get("boxes", [])
                        if b.get("text") and x < b["x"] + b["w"] and x + w > b["x"] and y < b["y"] + b["h"] and y + h > b["y"]})
    shot = Image.open(a.shot).convert("L").resize((480, 272), Image.BILINEAR)
    x0, y0, x1, y1 = a.region
    shot = np.asarray(shot, dtype=float)[y0:y1, x0:x1]
    if a.dark:
        shot = 255 - shot
    alpha = np.asarray(img)[:, :, 3].astype(float) / 255
    for k in cands:
        x, y, w, h = rects[k]
        mask = alpha[y:y + h, x:x + w]
        if mask.std() < 0.05 or h > shot.shape[0] or w > shot.shape[1]:
            continue
        c = ncc_map(shot, mask)
        while True:
            iy, ix = np.unravel_index(np.argmax(c), c.shape)
            if c[iy, ix] < a.min:
                break
            print(f"sprite {k:3d} rect {x},{y},{w},{h} -> screen {ix + x0},{iy + y0} score {c[iy, ix]:.3f}")
            if not a.all:
                break
            c[max(0, iy - h // 2):iy + h // 2 + 1, max(0, ix - w // 2):ix + w // 2 + 1] = -1   # suppress this peak


if __name__ == "__main__":
    main()
