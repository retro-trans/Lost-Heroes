"""Contact sheet of game glyphs (Font14) with their code and, optionally, the
mapped character rendered beside each for visual verification.

Usage:
    python tools/glyph_sheet.py <font_png_prefix> <first_code> <count> <out.png> [charmap.json]
"""
import json
import sys

from PIL import Image, ImageDraw, ImageFont

CW, CH, COLS, PER_PAGE = 14, 16, 18, 576
Z = 4
PER_LINE = 10
LABEL = ImageFont.truetype("C:/Windows/Fonts/consola.ttf", 13)
JP = ImageFont.truetype("C:/Windows/Fonts/YuGothM.ttc", 50)


def main():
    prefix, first, count, out = sys.argv[1], int(sys.argv[2], 0), int(sys.argv[3]), sys.argv[4]
    cmap = json.load(open(sys.argv[5], encoding="utf-8")) if len(sys.argv) > 5 else {}
    pages = {}
    cell_w, cell_h = CW * Z * 2 + 12, CH * Z + 18
    lines = -(-count // PER_LINE)
    sheet = Image.new("L", (cell_w * PER_LINE, cell_h * lines), 40)
    d = ImageDraw.Draw(sheet)
    for n in range(count):
        code = first + n
        idx = code - 1
        p, i = divmod(idx, PER_PAGE)
        if p not in pages:
            pages[p] = Image.open(f"{prefix}_{p}.png").convert("L")
        r, c = divmod(i, COLS)
        g = pages[p].crop((c * CW, r * CH, (c + 1) * CW, (r + 1) * CH)).resize((CW * Z, CH * Z), Image.NEAREST)
        x, y = (n % PER_LINE) * cell_w, (n // PER_LINE) * cell_h
        sheet.paste(g, (x + 2, y + 16))
        d.text((x + 2, y + 1), f"{code:04X}", font=LABEL, fill=255)
        ch = cmap.get(f"0x{code:04X}")
        if isinstance(ch, list):
            ch = ch[0][0] if ch and isinstance(ch[0], list) else (ch[0] if ch else None)
        if ch:
            d.text((x + CW * Z + 6, y + 18), ch, font=JP, fill=170)
    sheet.save(out)


if __name__ == "__main__":
    main()
