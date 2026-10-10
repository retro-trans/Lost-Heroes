"""Classify every message table: packed / script-referenced / scrambled.

scramble score = share of adjacent-kanji pairs in the table that occur in no
other table. Correct text scores ~0.02 (median); tables encoded against an
older font build score far higher, and their ellipsis "……" decodes as a
doubled kanji (相相, 復復, 連連, 形形 ...).

Writes work/source/table_status.json and prints scrambled tables that look live.

Usage:
    python tools/table_status.py
"""
import collections
import glob
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
K = re.compile(r"[一-鿿々]")
DOUBLED = re.compile(r"([一-鿿])\1")


def main():
    refs = set(json.load(open(os.path.join(ROOT, "work/source/script_table_refs.json"))))
    files = {}
    for p in glob.glob(os.path.join(ROOT, "work/source/text/**/*.json"), recursive=True):
        d = json.load(open(p, encoding="utf-8"))
        files[d["file"]] = d
    pairs, bg = {}, collections.Counter()
    for f, d in files.items():
        ps = []
        for r in d["rows"]:
            s = r["jp"]
            ps += [s[i:i + 2] for i in range(len(s) - 1) if K.match(s[i]) and K.match(s[i + 1])]
        pairs[f] = ps
        bg.update(set(ps))
    out = {}
    for f, d in files.items():
        ps = pairs[f]
        score = sum(1 for p in ps if bg[p] <= 1) / len(ps) if len(ps) >= 5 else 0.0
        doubled = collections.Counter(m.group(0) for r in d["rows"] for m in DOUBLED.finditer(r["jp"]))
        packed = any("::" in s for s in d["sources"])
        out[f] = dict(score=round(score, 3), kanji_pairs=len(ps), packed=packed,
                      referenced=f in refs, status=d.get("status", "ok"),
                      doubled=doubled.most_common(2))
    json.dump(out, open(os.path.join(ROOT, "work/source/table_status.json"), "w",
                        encoding="utf-8"), ensure_ascii=False, indent=1)
    sus = sorted(((v["score"], f, v) for f, v in out.items() if v["score"] >= 0.25), reverse=True)
    print(f"{len(sus)} tables with score >= 0.25")
    for s, f, v in sus:
        print(f"{s:.2f} {v['kanji_pairs']:4d} packed={int(v['packed'])} ref={int(v['referenced'])} "
              f"{v['status']:6s} {f}  {v['doubled']}")


if __name__ == "__main__":
    main()
