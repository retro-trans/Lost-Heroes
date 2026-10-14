"""Shared English character -> game code table (font slots for Latin text).

The game's half-width block runs '!'(0x00EA) .. '~'(0x0146) in ASCII order, except
that 0x00EB (where '"' would be) is the half-width SPACE: the EBOOT glyph table
gives it character U+0020. '|' uses the box-drawing bar 0x014E.

Space is 0x00EB, not the full-width space 0x0001: the message formatter (0xdc3c4)
deletes every 0x0001 that follows a name tag (Japanese pads names with it), so
"{name} attacked!" lost its space. 0x0001 stays the name-padding code.
'"' has no slot of its own and uses 0x014F (the corner bracket, never needed in
English; apply_en maps the corner brackets to '"' anyway); build_font.py redraws it.
Codes 0x0002-0x0040 (first block) also hold ? 0-9 A-Z a-z.
"""

SPACE = 0x00EB
CODES = {" ": SPACE}
for _c in range(0x21, 0x7C):            # '!' .. '{'
    CODES[chr(_c)] = 0x00EA + _c - 0x21
CODES['"'] = 0x014F
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
