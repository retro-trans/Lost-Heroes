"""OCR the game font atlas (Font14) by template matching against Japanese
system fonts, producing candidate characters per glyph code.

Each glyph's ink bounding box is resized to an NxN tile (blurred, zero-mean,
unit-norm) and correlated against every cp932 double-byte character rendered
in several fonts. An aspect-ratio penalty separates 一/ー/口 style shapes.

Usage:
    python tools/ocr_glyphs.py <font_png_prefix> <out_json> [first_idx] [last_idx]
        font_png_prefix: e.g. work/source/font/f14  (pages _0.._3)
"""
import json
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

CW, CH, COLS, PER_PAGE = 14, 16, 18, 576
N = 24
FONTS = [
    ("C:/Windows/Fonts/msgothic.ttc", 0),
    ("C:/Windows/Fonts/meiryo.ttc", 0),
    ("C:/Windows/Fonts/YuGothM.ttc", 0),
    ("C:/Windows/Fonts/BIZ-UDGothicR.ttc", 0),
    ("C:/Windows/Fonts/BIZ-UDGothicB.ttc", 0),
    ("C:/Windows/Fonts/NotoSansJP-VF.ttf", 0),
]


def candidates():
    out = []
    for hi in list(range(0x81, 0xA0)) + list(range(0xE0, 0xEB)):
        for lo in list(range(0x40, 0x7F)) + list(range(0x80, 0xFD)):
            try:
                ch = bytes([hi, lo]).decode("cp932")
            except UnicodeDecodeError:
                continue
            if len(ch) == 1 and not ch.isspace():
                out.append(ch)
    return out


def tile(img):
    """img: L image. Returns (vector, aspect) or None if blank."""
    a = np.asarray(img, dtype=np.float32)
    ys, xs = np.nonzero(a > 20)
    if len(xs) == 0:
        return None
    crop = img.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))
    w, h = crop.size
    t = crop.resize((N, N), Image.BILINEAR).filter(ImageFilter.GaussianBlur(1.0))
    v = np.asarray(t, dtype=np.float32).ravel()
    v = v - v.mean()
    n = np.linalg.norm(v)
    return (v / n if n else v), np.log((w + 1) / (h + 1))


def game_glyphs(prefix, first, last):
    pages = {}
    out = {}
    for idx in range(first, last + 1):
        p, i = divmod(idx, PER_PAGE)
        if p not in pages:
            pages[p] = Image.open(f"{prefix}_{p}.png").convert("L")
        r, c = divmod(i, COLS)
        g = pages[p].crop((c * CW, r * CH, (c + 1) * CW, (r + 1) * CH))
        # upscale before tiling so small glyphs keep detail
        t = tile(g.resize((CW * 4, CH * 4), Image.BICUBIC))
        if t:
            out[idx] = t
    return out


def render_candidates(chars):
    vecs, asp, owner = [], [], []
    for path, index in FONTS:
        font = ImageFont.truetype(path, 56, index=index)
        for ch in chars:
            im = Image.new("L", (80, 80), 0)
            ImageDraw.Draw(im).text((8, 4), ch, font=font, fill=255)
            t = tile(im)
            if t:
                vecs.append(t[0]); asp.append(t[1]); owner.append(ch)
    return np.stack(vecs), np.array(asp), owner


def main():
    prefix, out = sys.argv[1], sys.argv[2]
    first = int(sys.argv[3], 0) if len(sys.argv) > 3 else 0x17C
    last = int(sys.argv[4], 0) if len(sys.argv) > 4 else 0x8FF
    chars = candidates()
    C, CA, owner = render_candidates(chars)
    glyphs = game_glyphs(prefix, first, last)
    idxs = sorted(glyphs)
    C = C.astype(np.float32)
    CA = CA.astype(np.float32)
    result = {}
    for start in range(0, len(idxs), 100):
        chunk = idxs[start:start + 100]
        G = np.stack([glyphs[i][0] for i in chunk]).astype(np.float32)
        GA = np.array([glyphs[i][1] for i in chunk], dtype=np.float32)
        S = G @ C.T - 0.35 * np.abs(GA[:, None] - CA[None, :])
        rank(S, chunk, owner, result)
    json.dump(result, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    print(f"{len(result)} glyphs OCR'd -> {out}")


def rank(S, idxs, owner, result):
    for row, idx in enumerate(idxs):
        best = {}
        for j in np.argsort(-S[row])[:60]:
            ch = owner[j]
            if ch not in best:
                best[ch] = float(S[row, j])
            if len(best) == 5:
                break
        cands = sorted(best.items(), key=lambda kv: -kv[1])
        result[f"0x{idx + 1:04X}"] = [[c, round(s, 3)] for c, s in cands]


if __name__ == "__main__":
    main()
