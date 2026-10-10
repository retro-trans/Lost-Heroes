"""List message tables referenced by event scripts (.bla, compiled Lua).

A table is "live" if some script names its path. Writes
work/source/script_table_refs.json and prints coverage for event tables.

Usage:
    python tools/script_refs.py
"""
import collections
import glob
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAT = re.compile(rb"Table[/\\][A-Za-z0-9_/\\]+\.(?:mbb|pck|tbb)")


def collect():
    refs = collections.Counter()
    for p in glob.glob(os.path.join(ROOT, "work/source/flat/**/*.bla"), recursive=True):
        if os.path.isfile(p):
            for m in PAT.findall(open(p, "rb").read()):
                refs[m.decode().replace("\\", "/")] += 1
    return refs


def main():
    refs = collect()
    tables = {r for r in refs if not r.endswith(".tbb")}
    json.dump(sorted(tables), open(os.path.join(ROOT, "work/source/script_table_refs.json"), "w"), indent=0)
    files = {}
    for p in glob.glob(os.path.join(ROOT, "work/source/text/**/*.json"), recursive=True):
        d = json.load(open(p, encoding="utf-8"))
        files[d["file"]] = d
    ev = [f for f in files if f.startswith("Table/Event/")]
    live = [f for f in ev if f in tables]
    print(f"script-referenced tables: {len(tables)}; event tables {len(ev)}, referenced {len(live)}")
    print("referenced but missing:", sorted(r for r in tables if r not in files)[:20])
    groups = collections.Counter(f.rsplit("/", 1)[0] for f in ev if f not in tables)
    print("unreferenced event tables by folder:", groups.most_common())


if __name__ == "__main__":
    main()
