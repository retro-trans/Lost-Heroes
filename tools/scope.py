"""Decide which message tables need translating and pick a canonical copy.

The engine appears to look tables up by file name (NC08 scripts name NC07
paths; 0416.bla loads MainEventMess0414), so for dungeon events the unit is
the base name (other folders reuse names like MainEventMess0001 for different
tables, so they keep their full path):
  * dungeon event tables (Table/Event/Dungeon/...): live if a script names
    that base name;
  * everything else (system, base, battle, tutorial, OP, quest, DungeonMess,
    captions): live, except dead drafts and stale old-font copies.
Canonical copy per base name: the copy inside its own event pack
(DG_EVENT_*<number>_pk), else any packed copy, else the cleanest copy
(lowest scramble score). English is later written to every copy with that name.

Writes work/source/scope.json: {unit: {canonical, copies, category, status, score}}

Usage:
    python tools/scope.py
"""
import collections
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def stale_scrambled(v):
    """Old-font encoding outside the remapped legacy set: ellipsis decodes as a
    doubled kanji, with a high scramble score."""
    return v["status"] == "ok" and v["score"] >= 0.3 and sum(n for _, n in v["doubled"]) >= 1


def main():
    st = json.load(open(os.path.join(ROOT, "work/source/table_status.json"), encoding="utf-8"))
    refs = json.load(open(os.path.join(ROOT, "work/source/script_table_refs.json")))
    ref_names = {r.rsplit("/", 1)[-1] for r in refs}
    texts = {}
    for f in st:
        d = json.load(open(os.path.join(ROOT, "work/source/text", f + ".json"), encoding="utf-8"))
        texts[f] = d
    units = collections.defaultdict(list)
    for f in st:
        key = f.rsplit("/", 1)[-1] if f.startswith("Table/Event/Dungeon/") else f
        units[key].append(f)
    out, dropped = {}, []
    for key, copies in sorted(units.items()):
        dungeon = all(c.startswith("Table/Event/Dungeon/") for c in copies)
        if dungeon and key not in ref_names:
            dropped.append(key)
            continue
        usable = [c for c in copies if st[c]["status"] != "dead" and not stale_scrambled(st[c])]
        if not usable:
            dropped.append(key)
            continue
        copies_all, copies = copies, usable
        num = re.findall(r"(\d{4})\.mbb$", key)

        def rank(f):
            srcs = texts[f]["sources"]
            own = bool(num) and any(f"{num[0]}_pk" in s and "::" in s for s in srcs)
            return (not own, not st[f]["packed"], st[f]["status"] == "dead", st[f]["score"])

        best = sorted(copies, key=rank)[0]
        out[key] = dict(canonical=best, copies=copies_all, category=texts[best]["category"],
                        status=st[best]["status"], score=st[best]["score"],
                        rows=sum(1 for r in texts[best]["rows"] if r["jp"]))
    json.dump(out, open(os.path.join(ROOT, "work/source/scope.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    cats = collections.Counter()
    for u in out.values():
        cats[u["category"]] += u["rows"]
    print(f"{len(out)} units in scope, {len(dropped)} event names never loaded by a script")
    for c, n in cats.most_common():
        print(f"  {c:28s} {n:6d} rows")
    sus = [(u["score"], k, u["canonical"], u["status"]) for k, u in out.items() if u["score"] >= 0.3]
    print("canonical copies still suspicious:", sorted(sus, reverse=True))


if __name__ == "__main__":
    main()
