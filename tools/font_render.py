"""Render the game font pages (Font/*.tpc) to PNG for inspection.

Each .tpc is "GFPT" + 0x70 bytes, then a 2NBF archive of GFXT pages.
GFXT page: 0x70-byte header, then a 4bpp (16-gray) 256x512 bitmap stored as
PSP-swizzled 16x8-byte blocks.

Usage:
    python tools/font_render.py <font.tpc> <out_prefix> [cell] [--grid]
"""
import struct
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, __file__.rsplit("tools", 1)[0] + "tools")
import walk_assets  # noqa: E402


def unswizzle(data, width_bytes, height):
    out = bytearray(len(data))
    blocks_x = width_bytes // 16
    i = 0
    for by in range(height // 8):
        for bx in range(blocks_x):
            for row in range(8):
                dst = (by * 8 + row) * width_bytes + bx * 16
                out[dst:dst + 16] = data[i:i + 16]
                i += 16
    return bytes(out)


def page_image(blob, swizzled=True):
    w, h = struct.unpack_from("<HH", blob, 0x14)
    pix = blob[0x70:0x70 + w * h // 2]
    if swizzled:
        pix = unswizzle(pix, w // 2, h)
    img = Image.new("L", (w, h))
    px = img.load()
    for y in range(h):
        for x in range(0, w, 2):
            b = pix[y * (w // 2) + x // 2]
            px[x, y] = (b & 0xF) * 17
            px[x + 1, y] = (b >> 4) * 17
    return img


def main():
    tpc, prefix = sys.argv[1], sys.argv[2]
    cell = int(sys.argv[3]) if len(sys.argv) > 3 and sys.argv[3].isdigit() else 0
    data = open(tpc, "rb").read()
    for n, (name, blob) in enumerate(walk_assets.nbf_entries(data[0x80:])):
        img = page_image(blob).convert("RGB")
        if cell:
            d = ImageDraw.Draw(img)
            for x in range(0, img.width, cell):
                d.line([(x, 0), (x, img.height)], fill=(90, 0, 0))
            for y in range(0, img.height, cell):
                d.line([(0, y), (img.width, y)], fill=(90, 0, 0))
        img.save(f"{prefix}_{n}.png")
        print(name, img.size)


if __name__ == "__main__":
    main()
