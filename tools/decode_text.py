"""Decode every unique MTBL message table to JSON working files.

Output: work/source/text/<logical path>.json  (local only, contains Japanese)
    {"file": logical path, "sources": [virtual paths...],
     "rows": [{"id": "b.e", "jp": "...", "codes": n}, ...]}
Line breaks (0x8001) become "\n"; other control codes become {XXXX} tags.

Usage:
    python tools/decode_text.py <ALLRES.PCK>
"""
import json
import os
import sys

import charmap
import count_text
import legacy_map
import mbb
import walk_assets

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "work", "source", "text")


def main():
    m = charmap.load()
    with open(sys.argv[1], "rb") as f:
        root = f.read()
    files = {}
    for vpath, blob in walk_assets.walk("", root):
        if blob[:4] == b"TBB1" and b"MTBL" in blob[:0x200]:
            lp = count_text.logical_path(vpath)
            entry = files.setdefault(lp, {"blob": blob, "sources": []})
            entry["sources"].append(vpath)
    legacy = {}
    if os.path.exists(legacy_map.OUT):
        legacy = {int(a, 16): int(b, 16) for a, b in json.load(open(legacy_map.OUT)).items()}
    unknown = {}
    for lp, entry in sorted(files.items()):
        rows = []
        status = "dead" if lp in legacy_map.DEAD else "legacy" if lp in legacy_map.LIVE else "ok"
        for b, e, codes in mbb.messages(entry["blob"]):
            if codes is None:
                continue
            if status != "ok":
                codes = [legacy.get(c, c) if legacy_map.is_kanji(c) else c for c in codes]
            text = charmap.decode(codes, m)
            if "{?" in text:
                for c in codes:
                    if c not in m and not (0x8000 <= c <= 0x80FF) and c < 0x2000:
                        unknown[c] = unknown.get(c, 0) + 1
            rows.append({"id": f"{b}.{e}", "jp": text})
        dest = os.path.join(OUT, lp + ".json")
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        json.dump({"file": lp, "category": count_text.category(lp), "status": status,
                   "sources": entry["sources"], "rows": rows},
                  open(dest, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"{len(files)} files -> {OUT}")
    if unknown:
        print("unmapped codes:", {hex(k): v for k, v in sorted(unknown.items())})


if __name__ == "__main__":
    main()
