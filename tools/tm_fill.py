"""Translation memory: fill slices whose rows are all exact repeats.

Builds jp -> en from every finished slice (pairing slice rows with their
English by key). For each untranslated slice of the given pass, if every
row's Japanese is already in memory (one consistent English), writes the
.en.json directly; otherwise reports how many rows are covered.

Usage:
    python tools/tm_fill.py <pass> [--apply]
"""
import collections
import glob
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def memory():
    tm = collections.defaultdict(collections.Counter)
    for en_path in glob.glob(os.path.join(ROOT, "work/translation/en/*/*.en.json")):
        p = os.path.basename(os.path.dirname(en_path))
        name = os.path.basename(en_path)[:-len(".en.json")]
        src = os.path.join(ROOT, "work/slices", p, name + ".json")
        if not os.path.exists(src):
            continue
        jp = {r["key"]: r["jp"] for r in json.load(open(src, encoding="utf-8"))["rows"]}
        for r in json.load(open(en_path, encoding="utf-8"))["rows"]:
            if r.get("en") is not None and r["key"] in jp:
                tm[jp[r["key"]]][r["en"]] += 1
    return {k: c.most_common(1)[0][0] for k, c in tm.items()}


def main():
    pass_name = sys.argv[1]
    apply = "--apply" in sys.argv
    tm = memory()
    out_dir = os.path.join(ROOT, "work/translation/en", pass_name)
    os.makedirs(out_dir, exist_ok=True)
    full = partial = 0
    for src in sorted(glob.glob(os.path.join(ROOT, "work/slices", pass_name, "*.json"))):
        name = os.path.basename(src)[:-5]
        if os.path.exists(os.path.join(out_dir, name + ".en.json")):
            continue
        rows = json.load(open(src, encoding="utf-8"))["rows"]
        hit = [r for r in rows if r["jp"] in tm]
        if len(hit) == len(rows):
            full += 1
            print(f"{name}: fully covered ({len(rows)} rows)")
            if apply:
                json.dump({"slice": name, "rows_in_slice": len(rows), "rows_examined": len(rows),
                           "rows": [{"key": r["key"], "en": tm[r["jp"]]} for r in rows],
                           "notes": [], "report": "filled from translation memory (all rows exact repeats)"},
                          open(os.path.join(out_dir, name + ".en.json"), "w", encoding="utf-8"),
                          ensure_ascii=False, indent=1)
        elif hit:
            partial += 1
            print(f"{name}: {len(hit)}/{len(rows)} rows covered")
    print(f"{full} slices fully covered{' (written)' if apply else ''}, {partial} partially; memory {len(tm)} strings")


if __name__ == "__main__":
    main()
