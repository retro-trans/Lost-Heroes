"""Replace the Latin glyphs in a game font (.tpc) with GenEi Latin, rendered
at 4x and box-filtered down to the native cell (supersampled anti-aliasing),
and write the per-code advance widths a VWF routine will need.

Glyph slots rewritten: every code in latin.py (space, the full ASCII block
used for English text, and the first-block ? 0-9 A-Z a-z duplicates).

Usage:
    python tools/build_font.py <font14|font10|staff> <in.tpc> <font.ttf> <out_dir>
"""
import json
import os
import struct
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

import latin

SCALE = 4

# cell_w, cell_h, cols, baseline row (last ink row of capitals), px size,
# stroke (emboldening, in 4x pixels), gamma (<1 brightens thin strokes)
PROFILES = {
    "font14": dict(cw=14, ch=16, cols=18, baseline=12, px=13.8, stroke=0, gamma=0.85),
    "font10": dict(cw=10, ch=10, cols=25, baseline=7, px=8.75, stroke=1, gamma=0.6),
    "staff": dict(cw=15, ch=16, cols=17, baseline=12, px=13.8, stroke=0, gamma=0.85),
}

# FontStaff: the staff roll only has the glyphs its Japanese credits use
# (cells 0-387; 15x16 cells, 17 per row). Printable ASCII goes into free cells from STAFF_LATIN_CELL on;
# the staff-roll code of a character is its cell + 1.
STAFF_LATIN_CELL = 391  # row 23, col 0 (17 cells per row); cells 0-387 hold the credits


def staff_code(ch):
    return STAFF_LATIN_CELL + (ord(ch) - 0x20) + 1


def slots(kind="font14"):
    """Yield (glyph_index, char); the Font14/Font10 code table lives in latin.py."""
    if kind == "staff":
        for i in range(0x20, 0x7F):
            yield STAFF_LATIN_CELL + (i - 0x20), chr(i)
        return
    yield from latin.glyph_slots()


def swizzle(lin, width_bytes, height):
    out = bytearray(len(lin))
    i = 0
    for by in range(height // 8):
        for bx in range(width_bytes // 16):
            for row in range(8):
                src = (by * 8 + row) * width_bytes + bx * 16
                out[i:i + 16] = lin[src:src + 16]
                i += 16
    return bytes(out)


def unswizzle(sw, width_bytes, height):
    out = bytearray(len(sw))
    i = 0
    for by in range(height // 8):
        for bx in range(width_bytes // 16):
            for row in range(8):
                dst = (by * 8 + row) * width_bytes + bx * 16
                out[dst:dst + 16] = sw[i:i + 16]
                i += 16
    return bytes(out)


def pages(tpc):
    """Return [(abs_offset_of_pixels, w, h)] for each GFXT page in a .tpc."""
    base = 0x80
    count, data_start, _ = struct.unpack_from("<III", tpc, base + 4)
    out = []
    for i in range(count):
        e = base + 16 + i * 140
        off, _u, _size = struct.unpack_from("<III", tpc, e + 128)
        page = base + data_start + off
        w, h = struct.unpack_from("<HH", tpc, page + 0x14)
        out.append((page + 0x70, w, h))
    return out


def render_glyph(font, ch, prof):
    """Render one glyph at 4x into a cell, downsample. Returns (L image, advance)."""
    cw, chh = prof["cw"] * SCALE, prof["ch"] * SCALE
    big = Image.new("L", (cw, chh), 0)
    d = ImageDraw.Draw(big)
    ascent, _ = font.getmetrics()
    baseline = (prof["baseline"] + 1) * SCALE
    x0 = 0
    if ch != " ":
        l, _t, _r, _b = font.getbbox(ch, anchor="ls")
        if l < 0:
            x0 = -l
    d.text((x0 + prof["stroke"], baseline), ch, font=font, fill=255, anchor="ls",
           stroke_width=prof["stroke"], stroke_fill=255)
    small = big.resize((prof["cw"], prof["ch"]), Image.BOX)
    adv = font.getlength(ch) + x0 + 2 * prof["stroke"]
    return small, max(1, int(round(adv / SCALE))), big


def main():
    kind, tpc_path, ttf, out_dir = sys.argv[1:5]
    prof = PROFILES[kind]
    os.makedirs(out_dir, exist_ok=True)
    font = ImageFont.truetype(ttf, prof["px"] * SCALE)
    tpc = bytearray(open(tpc_path, "rb").read())
    pg = pages(tpc)
    per_page = prof["cols"] * (pg[0][2] // prof["ch"])

    # Decode pages to linear 4bpp nibble arrays.
    canvases = []
    for off, w, h in pg:
        lin = unswizzle(bytes(tpc[off:off + w * h // 2]), w // 2, h)
        a = np.frombuffer(lin, dtype=np.uint8)
        px = np.empty(w * h, dtype=np.uint8)
        px[0::2] = a & 0xF
        px[1::2] = a >> 4
        canvases.append(px.reshape(h, w))

    widths, clipped, native = {}, [], {}
    for idx, ch in slots(kind):
        small, adv, big = render_glyph(font, ch, prof)
        native.setdefault(ch, big)
        ink = np.nonzero(np.array(big))
        if len(ink[1]) and (ink[1].max() >= prof["cw"] * SCALE - 1 or ink[0].max() >= prof["ch"] * SCALE - 1):
            clipped.append(ch)
        p, i = divmod(idx, per_page)
        r, c = divmod(i, prof["cols"])
        lum = (np.array(small) / 255.0) ** prof["gamma"]
        cell = np.rint(lum * 15).astype(np.uint8)
        canvases[p][r * prof["ch"]:(r + 1) * prof["ch"],
                    c * prof["cw"]:(c + 1) * prof["cw"]] = cell
        widths[idx + 1] = min(adv, prof["cw"])

    for (off, w, h), px in zip(pg, canvases):
        flat = px.reshape(-1)
        packed = (flat[0::2] | (flat[1::2] << 4)).astype(np.uint8).tobytes()
        tpc[off:off + w * h // 2] = swizzle(packed, w // 2, h)

    name = os.path.basename(tpc_path)
    open(os.path.join(out_dir, name), "wb").write(tpc)
    for n, px in enumerate(canvases):
        Image.fromarray((px * 17).astype(np.uint8)).save(
            os.path.join(out_dir, f"{name}_{n}.png"))
    json.dump({"font": os.path.basename(ttf), "px": prof["px"], "scale": SCALE,
               "cell": [prof["cw"], prof["ch"]],
               "widths": {f"0x{k:04X}": v for k, v in sorted(widths.items())}},
              open(os.path.join(out_dir, name + ".widths.json"), "w"), indent=1)
    write_native4x(native, prof, os.path.join(out_dir, name + ".native4x"))
    print(f"{name}: {len(widths)} glyphs, clipped: {''.join(clipped) or 'none'}")


def write_native4x(native, prof, prefix):
    """Native 4x Latin atlas (same idea as SRW MX tools/native_font4x.py).

    Each glyph is the 4x canvas its 1x glyph was box-filtered from, so ink sits
    at exactly 4x the 1x placement and the 1x VWF advances stay valid. Cells are
    (cw*4)x(ch*4), packed into a 512 px wide sheet; every cell row is a legal
    512 x (ch*4) PSP texture strip. Pixels: linear (unswizzled) 4bpp.
    """
    cw, chh = prof["cw"] * SCALE, prof["ch"] * SCALE
    per_row = 512 // cw
    chars = [c for c in native if c != " "]
    rows = -(-len(chars) // per_row)
    sheet = np.zeros((rows * chh, 512), dtype=np.uint8)
    index = {}
    for n, ch in enumerate(chars):
        r, c = divmod(n, per_row)
        lum = (np.array(native[ch]) / 255.0) ** prof["gamma"]
        sheet[r * chh:(r + 1) * chh, c * cw:(c + 1) * cw] = np.rint(lum * 15)
        index[ch] = n
    flat = sheet.reshape(-1)
    open(prefix + ".bin", "wb").write(
        (flat[0::2] | (flat[1::2] << 4)).astype(np.uint8).tobytes())
    Image.fromarray(sheet * 17).save(prefix + ".png")
    json.dump({"cell": [cw, chh], "per_row": per_row, "rows": rows,
               "sheet": [512, rows * chh], "format": "4bpp linear",
               "slot": {f"U+{ord(c):04X}": n for c, n in index.items()}},
              open(prefix + ".json", "w"), indent=1)


if __name__ == "__main__":
    main()
