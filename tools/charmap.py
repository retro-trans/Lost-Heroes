"""Build and use the glyph-code <-> character table.

    python tools/charmap.py build   -> work/glossary/charmap.json

Codes (u16) = Font14 glyph index + 1. Kanji come from the hand transcription
in work/source/font/kanji_sheets.txt (10 per line from 0x016C). Control codes
0x8000-0x80FF decode to {XXXX} tags; raw Unicode (>= 0x2000 outside that
range) decodes to itself.
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHEETS = os.path.join(ROOT, "work", "source", "font", "kanji_sheets.txt")
OUT = os.path.join(ROOT, "work", "glossary", "charmap.json")

SYMBOLS_147 = "、。！ー／＼～｜「」±×÷∞∴″☆○●◎◇◆♬■△▲▽▼※〒→←↑↓♭♪"


def build():
    m = {}
    m[0x01] = "　"
    for i, ch in enumerate("?0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"):
        m[0x02 + i] = ch
    for i in range(0x3041, 0x3094):          # ぁ..ん
        m[0x41 + i - 0x3041] = chr(i)
    for i in range(0x30A1, 0x30F7):          # ァ..ヶ
        m[0x94 + i - 0x30A1] = chr(i)
    for i in range(0xFF01, 0xFF5C):          # ！..｛
        m[0xEA + i - 0xFF01] = chr(i)
    m[0x145] = "｝"
    m[0x146] = "￣"
    for i, ch in enumerate(SYMBOLS_147):
        m[0x147 + i] = ch
    code = 0x16C
    for line in open(SHEETS, encoding="utf-8"):
        line = line.rstrip("\n")
        if not line or line.startswith("#"):
            continue
        for ch in line:
            m[code] = ch
            code += 1
    return m


def load():
    data = json.load(open(OUT, encoding="utf-8"))
    return {int(k, 16): v for k, v in data.items()}


def decode(codes, m):
    out = []
    for c in codes:
        if c in m and m[c] not in ("？",):
            out.append(m[c])
        elif 0x8000 <= c <= 0x80FF or c in (0xA000, 0xF000):
            out.append("\n" if c == 0x8001 else "{%04X}" % c)
        elif c >= 0x2000:
            out.append(chr(c))
        else:
            out.append("{?%04X}" % c)
    return "".join(out)


def main():
    if sys.argv[1] == "build":
        m = build()
        os.makedirs(os.path.dirname(OUT), exist_ok=True)
        json.dump({f"0x{k:04X}": v for k, v in sorted(m.items())},
                  open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
        print(f"{len(m)} codes, last 0x{max(m):04X} -> {OUT}")


if __name__ == "__main__":
    main()
