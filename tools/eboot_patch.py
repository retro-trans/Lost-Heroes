"""Variable-width font for Lost Heroes: patch the glyph trim tables in the EBOOT.

The game is already proportional. Each font is registered (0x144334) with a
glyph table (u16 char, u8 col, u8 row per code) and a trim table (s8 left,
s8 right per code); the renderer advances the pen by cell width - left -
right (0x144898, used by the text loop at 0x100990) and crops the glyph to
[x + left, x + cell - right]. The original half-width ASCII (codes 0xEA-0x146)
already has trims, but there is no half-width space: English spaces use 0x0001
(U+3000), which advances a full cell.

This tool sets the trims of every code that tools/build_font.py redrew with
GenEi LateGo (work/output/font/<font>.tpc.widths.json): left 0, right = cell -
advance. Code 0x0001 becomes a narrow space. Input is the plain ELF from
tools/eboot_decrypt.py; the output goes on the ISO as PSP_GAME/SYSDIR/EBOOT.BIN.

Then tools/eboot_font4x.py adds the native 4x Latin glyph hook.

Usage:
    python tools/eboot_patch.py <EBOOT.elf> <EBOOT.BIN out>
"""
import json
import os
import struct
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEXT_FILE_OFFSET = 0xC0          # module address -> file offset (first PT_LOAD at 0xC0)

# (font name, cell width, glyph table, trim table, glyph count) from the
# registration calls at 0x1028 / 0x104C
FONTS = [
    ("Font14", 14, 0x1ADC68, 0x1AFD24, 0x82F),
    ("Font10", 10, 0x1B0D82, 0x1B2E3E, 0x82F),
]


def patch(elf):
    out = bytearray(elf)
    report = {}
    for name, cell, _glyphs, trims, count in FONTS:
        widths = json.load(open(os.path.join(ROOT, "work/output/font", name + ".tpc.widths.json")))["widths"]
        n = 0
        for key, adv in widths.items():
            code = int(key, 16)
            if not 1 <= code <= count:
                continue
            adv = max(1, min(cell, int(adv)))
            struct.pack_into("<bb", out, TEXT_FILE_OFFSET + trims + (code - 1) * 2, 0, cell - adv)
            n += 1
        report[name] = n
    return bytes(out), report


def main():
    src, dst = sys.argv[1], sys.argv[2]
    elf = open(src, "rb").read()
    if elf[:4] != b"\x7fELF":
        raise SystemExit("input must be the decrypted ELF (tools/eboot_decrypt.py)")
    out, report = patch(elf)
    # native 4x Latin pages (tools/font4x.py): hook the glyph draw
    import eboot_font4x
    out, font4x = eboot_font4x.patch(out)
    open(dst, "wb").write(out)
    print(f"wrote {dst}; trims set: {report}; 4x hook: {font4x}")


if __name__ == "__main__":
    main()
