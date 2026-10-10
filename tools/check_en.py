"""Validate translated slices and measure English against the text boxes.

For each work/translation/en/<pass>/*.en.json: same keys/order as the slice,
no Japanese script, every {XXXX} tag of the source kept, then word-wrap with
the VWF widths (Font14) and flag rows needing more lines than the box has.

Box metrics (from the Japanese line lengths, 14 px per full-width glyph):
    story/quest/talk: 2 lines x 336 px
Name-variable tags ({8073}, {8074}, {806D}, {806E}...) count as 96 px.

Usage:
    python tools/check_en.py <pass> [slice ...]
"""
import glob
import json
import os
import re
import sys

import latin

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BOX = {"story": (336, 2), "quest": (336, 2), "talk": (336, 2), "system": (336, 4), "extra": (336, 2), "extrasys": (336, 4)}
TAG = re.compile(r"\{[0-9A-F]{4}\}")
JP = re.compile(r"[぀-ヿ一-鿿]")
NAME_TAGS = {"{8073}", "{8074}", "{806D}", "{806E}"}


def widths():
    w = json.load(open(os.path.join(ROOT, "work/output/font/Font14.tpc.widths.json")))["widths"]
    return {ch: w[f"0x{code:04X}"] for ch, code in latin.CODES.items() if f"0x{code:04X}" in w}


def text_width(s, W):
    total = 0
    for part in TAG.split(s):
        total += sum(W.get(ch, 14) for ch in part)
    total += sum(96 for t in TAG.findall(s) if t in NAME_TAGS)
    return total


def wrap(s, W, width):
    lines = []
    for para in s.split("\n"):
        cur = ""
        for word in para.split(" "):
            trial = word if not cur else cur + " " + word
            if text_width(trial, W) <= width or not cur:
                cur = trial
            else:
                lines.append(cur)
                cur = word
        lines.append(cur)
    return lines


def check(pass_name, name, W):
    src = json.load(open(os.path.join(ROOT, "work/slices", pass_name, name + ".json"), encoding="utf-8"))
    path = os.path.join(ROOT, "work/translation/en", pass_name, name + ".en.json")
    if not os.path.exists(path):
        return None
    out = json.load(open(path, encoding="utf-8"))
    problems = []
    if [r["key"] for r in out["rows"]] != [r["key"] for r in src["rows"]]:
        problems.append(("keys", "row keys/order differ from slice"))
    over = 0
    for s, o in zip(src["rows"], out["rows"]):
        en = o.get("en")
        if en is None:
            problems.append((o["key"], "untranslated (null)"))
            continue
        if JP.search(en):
            problems.append((o["key"], "Japanese script in English"))
        missing = sorted(set(TAG.findall(s["jp"])) - set(TAG.findall(en)))
        if missing:
            problems.append((o["key"], f"missing tags {missing}"))
        width, maxlines = (s.get("max_px", BOX[pass_name][0]), s.get("max_lines", BOX[pass_name][1]))
        # a row may use as many lines as its Japanese does (choice menus, 3-line descriptions)
        maxlines = max(maxlines, s["jp"].count(chr(10)) + 1)
        n = len(wrap(en, W, width))
        if n > maxlines:
            over += 1
            problems.append((o["key"], f"{n} lines > {maxlines}: {en[:60]}"))
    return len(src["rows"]), over, problems


def main():
    pass_name = sys.argv[1]
    names = sys.argv[2:] or sorted(os.path.basename(p)[:-5] for p in
                                   glob.glob(os.path.join(ROOT, "work/slices", pass_name, "*.json")))
    W = widths()
    done = rows = overs = 0
    for name in names:
        r = check(pass_name, name, W)
        if r is None:
            continue
        done += 1
        n, over, problems = r
        rows += n
        overs += over
        for key, msg in problems:
            print(f"{name} {key}: {msg}")
    print(f"{pass_name}: {done} slices checked, {rows} rows, {overs} over box")


if __name__ == "__main__":
    main()
