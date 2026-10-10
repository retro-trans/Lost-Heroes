"""Typeset sample English with a built font page + width table, comparing the
game's fixed advance with VWF. Output is zoomed for inspection.

Usage:
    python tools/preview_vwf.py <page0.png> <widths.json> <cw> <ch> <cols> <out.png> [text]
"""
import json
import sys

from PIL import Image

sys.path.insert(0, __file__.rsplit("tools", 1)[0] + "tools")
import latin  # noqa: E402


def code_for(ch):
    return latin.CODES[ch]


def main():
    page, wjson, cw, chh, cols, out = sys.argv[1:7]
    cw, chh, cols = int(cw), int(chh), int(cols)
    text = sys.argv[7] if len(sys.argv) > 7 else (
        "Daisuke (thought...) Where are we? This place...|"
        "Ultraman, Kamen Rider and Gundam: Lost Heroes!|"
        "HP 1234/5678  SP 90  Atk+15% \"Mission\" [OK]")
    atlas = Image.open(page).convert("L")
    widths = {int(k, 16): v for k, v in json.load(open(wjson))["widths"].items()}
    lines = text.split("|")
    W = 480
    img = Image.new("L", (W, (chh + 2) * len(lines) * 2 + 8), 24)
    y = 2
    for mode in ("fixed", "vwf"):
        for line in lines:
            x = 2
            for ch in line:
                code = code_for(ch)
                idx = code - 1
                r, c = divmod(idx, cols)
                g = atlas.crop((c * cw, r * chh, (c + 1) * cw, (r + 1) * chh))
                img.paste(g, (x, y), g) if x + cw <= W else None
                x += cw if mode == "fixed" else widths[code]
            y += chh + 2
        y += 4
    img = img.resize((img.width * 3, img.height * 3), Image.NEAREST)
    img.save(out)


if __name__ == "__main__":
    main()
