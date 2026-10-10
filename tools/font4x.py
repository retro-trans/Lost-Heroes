"""Native 4x Latin glyphs for Font14 / Font10 / FontStaff (SRW MX approach, adapted).

The 1x fonts (tools/build_font.py) stay as they are; this appends extra pages
to each font .tpc holding every Latin glyph at 4x (the exact canvas its 1x glyph
was box-filtered from, so ink sits at 4x the 1x placement and the VWF advances
stay valid). The pages have the same geometry and format as the originals
(256x512, 4-bit, palette index = alpha), so the game's own font loader
(0x144378) creates a texture for each one, and glyphs-per-page (computed from
the page size) is unchanged. tools/eboot_font4x.py hooks the glyph draw to
sample these pages with 4x source rectangles at the original on-screen size.

Writes work/output/font/<Font>.tpc (1x pages + 4x pages, idempotent: existing
4x pages are dropped first) and <Font>.4x.json (code -> 4x slot, page layout).

Usage:
    python tools/font4x.py
"""
import json
import os
import struct
import sys

import numpy as np
from PIL import Image, ImageFont

import build_font

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "work/output/font")
TTF = os.path.join(ROOT, "incoming/genei-latin/GenEiLatin-Separate_v2.1/GenEiLateGoP_v2.ttf")
PAGE_W, PAGE_H = 256, 512
TAG = "_4x_"
# file, build_font profile, font index in the game's font table
FONTS = [("Font14", "font14", 0), ("Font10", "font10", 1), ("FontStaff", "staff", 2)]


def read_pages(tpc):
    d = tpc[0x80:]
    count, start, _align = struct.unpack_from("<III", d, 4)
    out = []
    for i in range(count):
        e = d[16 + i * 140:16 + (i + 1) * 140]
        name = e[:128].split(b"\0")[0].decode("ascii")
        off, _u, size = struct.unpack_from("<III", e, 128)
        out.append((name, d[start + off:start + off + size]))
    return out


def write_tpc(header, pages):
    n = len(pages)
    start = (16 + n * 140 + 15) & ~15
    table = bytearray(b"2NBF" + struct.pack("<III", n, start, 16))
    body = bytearray()
    for name, blob in pages:
        e = bytearray(140)
        e[:len(name)] = name.encode("ascii")
        struct.pack_into("<III", e, 128, len(body), 0, len(blob))
        table += e
        body += blob
    table += bytes(start - len(table))
    head = bytearray(header[:0x80])
    data = table + body
    struct.pack_into("<I", head, 4, len(data))    # GFPT: size of the 2NBF block
    return bytes(head + data)


def page_blob(template, name, px):
    """Clone a 1x page (header + 16-entry palette) and put 4-bit pixels px (H x W) in it."""
    blob = bytearray(template)
    nm = name.encode("ascii")[:31]
    blob[0x20:0x40] = nm + bytes(32 - len(nm))
    flat = px.reshape(-1)
    packed = (flat[0::2] | (flat[1::2] << 4)).astype(np.uint8).tobytes()
    blob[0x70:0x70 + len(packed)] = build_font.swizzle(packed, PAGE_W // 2, PAGE_H)
    return bytes(blob)


def build(fname, kind):
    path = os.path.join(OUT, fname + ".tpc")
    tpc = open(path, "rb").read()
    pages = [(n, b) for n, b in read_pages(tpc) if TAG not in n]
    prof = build_font.PROFILES[kind]
    s = build_font.SCALE
    cw4, ch4 = prof["cw"] * s, prof["ch"] * s
    cols, rows = PAGE_W // cw4, PAGE_H // ch4
    per_page = cols * rows
    font = ImageFont.truetype(TTF, prof["px"] * s)

    slot_of, canvases = {}, {}
    codes = {}
    for idx, ch in build_font.slots(kind):
        if ch == " ":
            continue
        if ch not in slot_of:
            slot_of[ch] = len(slot_of)
            canvases[ch] = build_font.render_glyph(font, ch, prof)[2]
        codes[idx + 1] = slot_of[ch]
    n_pages = -(-len(slot_of) // per_page)
    sheets = [np.zeros((PAGE_H, PAGE_W), dtype=np.uint8) for _ in range(n_pages)]
    for ch, n in slot_of.items():
        p, i = divmod(n, per_page)
        r, c = divmod(i, cols)
        lum = (np.array(canvases[ch]) / 255.0) ** prof["gamma"]
        sheets[p][r * ch4:(r + 1) * ch4, c * cw4:(c + 1) * cw4] = np.rint(lum * 15)
    first = len(pages)
    template = pages[0][1]
    for p, px in enumerate(sheets):
        pages.append((f"{fname}{TAG}{p:02d}.bmp", page_blob(template, f"{fname}{TAG}{p:02d}", px)))
    assert len(pages) <= 12, "font table holds 12 page textures"
    open(path, "wb").write(write_tpc(tpc, pages))
    layout = {"font": fname, "cell4x": [cw4, ch4], "cols": cols, "per_page": per_page,
              "first_page": first, "pages": len(pages), "glyphs": len(slot_of),
              "codes": {str(k): v for k, v in sorted(codes.items())}}
    json.dump(layout, open(os.path.join(OUT, fname + ".4x.json"), "w"), indent=1)
    sheet = np.concatenate(sheets, axis=1)
    Image.fromarray((sheet * 17).astype(np.uint8)).save(os.path.join(OUT, fname + ".4x.png"))
    return layout


def main():
    for fname, kind, _idx in FONTS:
        lay = build(fname, kind)
        print(f"{fname}: {lay['glyphs']} glyphs in {lay['pages'] - lay['first_page']} 4x pages "
              f"(cells {lay['cell4x']}, {lay['per_page']}/page), {len(lay['codes'])} codes")


if __name__ == "__main__":
    sys.exit(main())
