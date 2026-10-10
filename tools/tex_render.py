"""Render GFPT/GFXT textures (.tpc) to PNG for inspection.

GFXT page: "GFXT", u16 format at +0x10, u16 width/height at +0x14/+0x16,
header 0x50 bytes; paletted formats put the palette (16-bit 5551/4444 or
32-bit 8888 entries) right after the header, then the pixels. Pixels are
PSP-swizzled (16-byte x 8-row blocks).

Formats seen: 2 = RGBA5551, 3 = RGBA4444, 4 = RGBA8888, 9 = 4-bit paletted,
10 = 8-bit paletted (palette entry format from the page name suffix).

Usage:
    python tools/tex_render.py <ALLRES.PCK> <out_dir> <path prefix> [...]
"""
import os
import struct
import sys

from PIL import Image

import pck_extract
import walk_assets

BPP = {2: 16, 3: 16, 4: 32, 7: 4, 9: 4, 10: 8}


def unswizzle(data, width_bytes, height):
    out = bytearray(width_bytes * height)
    i = 0
    for by in range((height + 7) // 8):
        for bx in range(width_bytes // 16):
            for row in range(8):
                y = by * 8 + row
                if y < height and i + 16 <= len(data):
                    dst = y * width_bytes + bx * 16
                    out[dst:dst + 16] = data[i:i + 16]
                i += 16
    return bytes(out)


def color(v, kind):
    if kind == "5551":
        c5 = lambda x: (x << 3) | (x >> 2)
        return (c5(v & 31), c5(v >> 5 & 31), c5(v >> 10 & 31), 255 if v >> 15 else 0)
    if kind == "4444":
        return ((v & 15) * 17, (v >> 4 & 15) * 17, (v >> 8 & 15) * 17, (v >> 12 & 15) * 17)
    return (v & 255, v >> 8 & 255, v >> 16 & 255, v >> 24 & 255)


def page_image(name, page):
    fmt, _u, w, h = struct.unpack_from("<HHHH", page, 0x10)
    if fmt not in BPP:
        return None
    kind = "8888" if "8888" in name else "4444" if "4444" in name else "5551"
    pos = 0x50
    pal = []
    if fmt in (7, 9, 10):
        n = 256 if fmt == 10 else 16
        esz = 4 if kind == "8888" else 2
        for i in range(n):
            v = int.from_bytes(page[pos + i * esz:pos + (i + 1) * esz], "little")
            pal.append(color(v, kind))
        pos += n * esz
    wb = w * BPP[fmt] // 8
    pix = unswizzle(page[pos:pos + wb * h], wb, h)
    img = Image.new("RGBA", (w, h))
    px = img.load()
    for y in range(h):
        row = pix[y * wb:(y + 1) * wb]
        for x in range(w):
            if fmt in (7, 9):
                b = row[x // 2]
                px[x, y] = pal[(b >> 4) if x & 1 else (b & 15)]
            elif fmt == 10:
                px[x, y] = pal[row[x]]
            elif fmt == 4:
                px[x, y] = color(int.from_bytes(row[x * 4:x * 4 + 4], "little"), "8888")
            else:
                px[x, y] = color(int.from_bytes(row[x * 2:x * 2 + 2], "little"), kind)
    return img


def main():
    src, out = sys.argv[1], sys.argv[2]
    prefixes = sys.argv[3:]
    os.makedirs(out, exist_ok=True)
    f = open(src, "rb")
    for name, off, size in pck_extract.read_table(f):
        if not any(name.startswith(p) for p in prefixes):
            continue
        f.seek(off)
        data = f.read(size)
        for vpath, blob in walk_assets.walk(name, data):
            if blob[:4] != b"GFPT":
                continue
            for pname, page in walk_assets.nbf_entries(blob[0x80:]):
                img = page_image(pname, page)
                if img is None:
                    print("skip", vpath, pname, struct.unpack_from("<H", page, 0x10)[0])
                    continue
                safe = vpath.replace("/", "_").replace(":", "_") + "__" + pname.rsplit(".", 1)[0]
                bg = Image.new("RGBA", img.size, (40, 40, 60, 255))
                bg.alpha_composite(img)
                bg.convert("RGB").save(os.path.join(out, safe + ".png"))


if __name__ == "__main__":
    main()
