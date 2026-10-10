"""Shared English character -> game code table (font slots for Latin text).

The game's full ASCII block runs '!'(0x00EA) .. '{'(0x0144); it has no '|',
'}' is 0x0145 and '~' is 0x0146 (the original '"' slot 0x00EB is blank and
gets a glyph from build_font.py). '|' uses the box-drawing bar 0x014E.
Space is 0x0001. Codes 0x0002-0x0040 (first block) also hold ? 0-9 A-Z a-z.
"""

SPACE = 0x0001
CODES = {" ": SPACE}
for _c in range(0x21, 0x7C):            # '!' .. '{'
    CODES[chr(_c)] = 0x00EA + _c - 0x21
CODES["}"] = 0x0145
CODES["~"] = 0x0146
CODES["|"] = 0x014E

# First-block duplicates (same glyphs, used by some original UI strings).
FIRST_BLOCK = " ?0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
FIRST_BLOCK_CODES = {0x0001 + i: ch for i, ch in enumerate(FIRST_BLOCK)}


def glyph_slots():
    """(glyph_index, char) pairs to render: every code above."""
    seen = set()
    for ch, code in list(CODES.items()) + [(c, k) for k, c in FIRST_BLOCK_CODES.items()]:
        if code not in seen:
            seen.add(code)
            yield code - 1, ch
