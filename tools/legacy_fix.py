"""Turn context corrections for the live legacy tables into old-code overrides.

work/source/legacy_corrections.json (local; contains Japanese):
    [["wrong substring", "right substring"], ...]   (equal length, kanji-only changes)
For every occurrence in a LIVE legacy table (decoded with the current legacy
map), each differing character's OLD code is pinned to the new code of the
right character. Conflicts (one old code needing two answers) are reported
and skipped. Result: work/glossary/legacy_overrides.json, then re-run
legacy_map.py and decode_text.py.

Usage:
    python tools/legacy_fix.py <ALLRES.PCK>
"""
import collections
import json
import os
import sys

import charmap
import legacy_map

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CORR = os.path.join(ROOT, "work", "source", "legacy_corrections.json")


def main():
    m = charmap.load()
    rev = collections.defaultdict(list)
    for k, v in m.items():
        if legacy_map.is_kanji(k) or v in "ⅠⅡⅢ":
            rev[v].append(k)
    tables = legacy_map.load_tables(sys.argv[1])
    cur = {int(a, 16): int(b, 16) for a, b in json.load(open(legacy_map.OUT)).items()}
    pins = collections.defaultdict(collections.Counter)
    unused = []
    for wrong, right in json.load(open(CORR, encoding="utf-8")):
        assert len(wrong) == len(right), (wrong, right)
        hits = 0
        for lp in legacy_map.LIVE:
            for old in tables.get(lp, []):
                chars = [charmap.decode([cur.get(c, c) if legacy_map.is_kanji(c) else c], m)
                         for c in old]
                text = "".join(ch if len(ch) == 1 else "\0" for ch in chars)
                start = text.find(wrong)
                while start >= 0:
                    hits += 1
                    for i, (w, r) in enumerate(zip(wrong, right)):
                        if w != r:
                            targets = rev.get(r)
                            if not targets:
                                print("no glyph for", r)
                                continue
                            pins[old[start + i]][targets[0]] += 1
                    start = text.find(wrong, start + 1)
        if not hits:
            unused.append(wrong)
    overrides, conflicts = {}, []
    for old, cnt in pins.items():
        if len(cnt) > 1:
            conflicts.append((hex(old), {m[k]: n for k, n in cnt.items()}))
            continue
        overrides[f"0x{old:04X}"] = f"0x{next(iter(cnt)):04X}"
    json.dump(overrides, open(legacy_map.OVERRIDES, "w"), indent=0)
    print(f"{len(overrides)} overrides; conflicts: {conflicts}; unmatched: {unused}")


if __name__ == "__main__":
    main()
