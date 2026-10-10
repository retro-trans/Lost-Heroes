"""Encode translated English and build a patched ALLRES.PCK.

For each scope unit with English rows (work/translation/en/<pass>/*.en.json):
  * normalise punctuation to the font's ASCII set,
  * {XXXX} tags -> control codes; a name-variable tag gets back the padding
    (run of 0x0001) that followed it in the Japanese,
  * word-wrap to the box with VWF widths, line breaks = 0x8001,
  * encode with latin.CODES, rebuild the table (mbb_write) for every copy.
Untranslated rows keep their Japanese codes.

Usage:
    python tools/apply_en.py <ALLRES.PCK> <out ALLRES.PCK> [--dry-run]
"""
import glob
import json
import os
import re
import sys

import check_en
import charmap
import latin
import mbb
import mbb_write
import repack

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TAG = re.compile(r"\{([0-9A-F]{4})\}")
NORMALISE = {"’": "'", "‘": "'", "“": '"', "”": '"', "—": "-", "–": "-",
             "…": "...", "é": "e", "è": "e", "à": "a", " ": " ", "→": "->",
             "×": "x", "☆": "*", "★": "*", "「": '"', "」": '"', "！": "!", "？": "?"}
PASS_BOX = {"story": "story", "quest": "quest", "talk": "talk", "system": "system", "extra": "extra", "extrasys": "extrasys"}


def load_english():
    out = {}
    for p in glob.glob(os.path.join(ROOT, "work/translation/en/*/*.en.json")):
        pass_name = os.path.basename(os.path.dirname(p))
        src = os.path.join(ROOT, "work/slices", pass_name, os.path.basename(p)[:-len(".en.json")] + ".json")
        box = {}
        if os.path.exists(src):
            for r in json.load(open(src, encoding="utf-8"))["rows"]:
                if "max_px" in r:
                    box[r["key"]] = (r["max_px"], r["max_lines"])
        for r in json.load(open(p, encoding="utf-8"))["rows"]:
            if r.get("en") is not None:
                unit, rid = r["key"].rsplit("#", 1)
                out.setdefault(unit, {})[rid] = (r["en"], pass_name, box.get(r["key"]))
    return out


def padding_after_tags(jp_codes):
    pads, i = {}, 0
    while i < len(jp_codes):
        c = jp_codes[i]
        if c >= 0x8000:
            n, j = 0, i + 1
            while j < len(jp_codes) and jp_codes[j] == 0x0001:
                n, j = n + 1, j + 1
            pads.setdefault(c, n)
            i = j
        else:
            i += 1
    return pads


def encode(en, jp_codes, pass_name, W, unknown, box=None):
    for a, b in NORMALISE.items():
        en = en.replace(a, b)
    width, maxlines = box or check_en.BOX[PASS_BOX[pass_name]]
    pads = padding_after_tags(jp_codes)
    if MARKUP.search(en):
        return encode_markup(en, W, width, unknown), False
    lines = check_en.wrap(en, W, width)
    codes = []
    for li, line in enumerate(lines):
        if li:
            codes.append(0x8001)
        pos = 0
        for m in TAG.finditer(line):
            codes += enc_plain(line[pos:m.start()], unknown)
            tag = int(m.group(1), 16)
            codes.append(tag)
            codes += [0x0001] * pads.get(tag, 0)
            pos = m.end()
        codes += enc_plain(line[pos:], unknown)
    jp_lines = 1 + sum(1 for c in jp_codes if c == 0x8001)
    return codes, len(lines) > max(maxlines, jp_lines)


# Enemy battle tables carry inline ASCII markup (<act_ch>, <tag_chr>, <br>...)
# stored as raw u16 ASCII values and expanded by the game at runtime.
MARKUP = re.compile(r"<([A-Za-z_]+)>")


def encode_markup(en, W, width, unknown):
    codes = []
    for li, seg in enumerate(en.split("<br>")):
        if li:
            codes += [ord(c) for c in "<br>"]
        for wi, line in enumerate(check_en.wrap(seg, W, width) if seg else [""]):
            if wi:
                codes += [ord(c) for c in "<br>"]
            pos = 0
            for m in MARKUP.finditer(line):
                codes += enc_plain(line[pos:m.start()], unknown)
                codes += [ord(c) for c in m.group(0)]
                pos = m.end()
            codes += enc_plain(line[pos:], unknown)
    return codes


_REV = None


def symbol_code(ch):
    """Non-ASCII symbols (♪ ☆ ～ ※ → ①...) reuse the original font glyph."""
    global _REV
    if _REV is None:
        _REV = {}
        for code, c in charmap.load().items():
            if 0xEA <= code < 0x16C or code >= 0x16C and not ("一" <= c <= "鿿"):
                _REV.setdefault(c, code)
    return _REV.get(ch)


def enc_plain(s, unknown):
    out = []
    for ch in s:
        if ch in latin.CODES:
            out.append(latin.CODES[ch])
        elif symbol_code(ch):
            out.append(symbol_code(ch))
        else:
            unknown[ch] = unknown.get(ch, 0) + 1
            out.append(latin.CODES["?"])
    return out


STAFF_TABLE = "Table/StaffRoll/StaffRoll.mbb"
STAFF_NAME = re.compile(r"[^　*()]+　[^　*()]+(?=\(|$)")


def apply_staffroll(src, index, changes, unknown):
    """Staff roll: own sequential font (code = glyph cell + 1, see
    work/source/font/staff/staff_glyphs.txt). Translated rows come from
    work/translation/en/staffroll.json; Latin uses the glyphs build_font.py
    adds to FontStaff, names keep their original glyphs. Also injects the
    rebuilt FontStaff.tpc (top level and inside FontStaff.cmp)."""
    import build_font
    seq_path = os.path.join(ROOT, "work/source/font/staff/staff_glyphs.txt")
    font_path = os.path.join(ROOT, "work/output/font/FontStaff.tpc")
    tr_path = os.path.join(ROOT, "work/translation/en/staffroll.json")
    if not (os.path.exists(seq_path) and os.path.exists(font_path) and os.path.exists(tr_path)):
        return 0
    seq = open(seq_path, encoding="utf-8").read().rstrip("\n")
    rows = json.load(open(tr_path, encoding="utf-8"))["rows"]
    off, size = index[STAFF_TABLE]
    with open(src, "rb") as f:
        f.seek(off)
        blob = f.read(size)
    strings = mbb_write.strings_of(blob)
    done = 0
    for bi, entries in strings.items():
        for ei, codes in enumerate(entries):
            en = rows.get(f"{bi}.{ei}")
            if not codes or en is None:
                continue
            orig = "".join(seq[c] if c < len(seq) else "?" for c in codes)
            if "{name}" in en:
                m = STAFF_NAME.search(orig)
                en = en.replace("{name}", m.group(0) if m else "")
            stars = len(en) - len(en.lstrip("*"))
            new = [2] * stars
            for ch in en[stars:]:
                if " " <= ch <= "~":
                    new.append(build_font.staff_code(ch))
                elif ch in seq[1:]:
                    new.append(seq.index(ch, 1))
                else:
                    unknown[ch] = unknown.get(ch, 0) + 1
                    new.append(build_font.staff_code("?"))
            entries[ei] = new
            done += 1
    changes[STAFF_TABLE] = mbb_write.rebuild(blob, strings)
    font = open(font_path, "rb").read()
    changes["Font/FontStaff.tpc"] = font
    changes["Font/FontStaff.cmp::FontStaff.tpc"] = font
    return done


def main():
    src, dst = sys.argv[1], sys.argv[2]
    dry = "--dry-run" in sys.argv
    scope = json.load(open(os.path.join(ROOT, "work/source/scope.json"), encoding="utf-8"))
    english = load_english()
    W = check_en.widths()
    changes, unknown, over, rows_done = {}, {}, 0, 0
    with open(src, "rb") as f:
        import pck_extract
        index = {name: (off, size) for name, off, size in pck_extract.read_table(f)}
    import walk_assets
    for unit, rows in english.items():
        u = scope[unit]
        for copy in u["copies"]:
            text = json.load(open(os.path.join(ROOT, "work/source/text", copy + ".json"), encoding="utf-8"))
            for vpath in text["sources"]:
                outer = vpath.split("::")[0]
                off, size = index[outer]
                with open(src, "rb") as f:
                    f.seek(off)
                    blob = dict(walk_assets.walk(outer, f.read(size)))[vpath] if "::" in vpath else f.read(size)
                blob = changes.get(vpath, blob)
                strings = mbb_write.strings_of(blob)
                for bi, entries in strings.items():
                    for ei, codes in enumerate(entries):
                        rid = f"{bi}.{ei}"
                        if codes and rid in rows:
                            en, pass_name, box = rows[rid]
                            new, too_long = encode(en, codes, pass_name, W, unknown, box)
                            entries[ei] = new
                            over += too_long
                            rows_done += 1
                changes[vpath] = mbb_write.rebuild(blob, strings)
    staff_rows = apply_staffroll(src, index, changes, unknown)
    # GenEi Latin fonts (tools/build_font.py); their advances go into the EBOOT
    # trim tables (tools/eboot_patch.py).
    for font in ("Font14", "Font10"):
        path = os.path.join(ROOT, "work/output/font", font + ".tpc")
        if os.path.exists(path):
            blob = open(path, "rb").read()
            changes[f"Font/{font}.tpc"] = blob
            changes[f"Font/{font}.cmp::{font}.tpc"] = blob
            # the boot pack carries its own copy of both fonts
            changes[f"Graph/STARTUP_pk.cmp::pack.pck::Font/{font}.tpc"] = blob
    # UI textures relabelled in English (specs in work/ui/tex, tools/tex_edit.py)
    import tex_edit
    tex = tex_edit.changes(src)
    changes.update(tex)
    print(f"textures relabelled: {len(tex)} copies")
    print(f"units {len(english)}, table copies {len(changes)}, rows written {rows_done}, over box {over}, "
          f"staff roll rows {staff_rows}")
    if unknown:
        print("characters without a glyph (written as '?'):", unknown)
    if not dry:
        repack.repack_file(src, dst, changes)
        print("wrote", dst)


if __name__ == "__main__":
    main()
