"""Cross-table consistency: identical Japanese translated differently.

Groups every finished row by its Japanese (from the slices) and reports
strings that have more than one distinct English rendering. Short strings
(names, skills, items) matter most, so --max-len filters by Japanese length.

Writes work/translation/en/consistency_report.json (contains Japanese, local only).

Usage:
    python tools/consistency.py [--max-len N] [--pass system]
"""
import collections
import glob
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    max_len = int(sys.argv[sys.argv.index("--max-len") + 1]) if "--max-len" in sys.argv else 10 ** 9
    only = sys.argv[sys.argv.index("--pass") + 1] if "--pass" in sys.argv else None
    groups = collections.defaultdict(lambda: collections.defaultdict(list))
    for en_path in sorted(glob.glob(os.path.join(ROOT, "work/translation/en/*/*.en.json"))):
        pass_name = os.path.basename(os.path.dirname(en_path))
        if only and pass_name != only:
            continue
        name = os.path.basename(en_path)[:-len(".en.json")]
        src = os.path.join(ROOT, "work/slices", pass_name, name + ".json")
        if not os.path.exists(src):
            continue
        jp = {r["key"]: r["jp"] for r in json.load(open(src, encoding="utf-8"))["rows"]}
        for r in json.load(open(en_path, encoding="utf-8"))["rows"]:
            if r.get("en") is not None and r["key"] in jp and len(jp[r["key"]]) <= max_len:
                groups[jp[r["key"]]][r["en"]].append(f"{name}:{r['key']}")
    report = [{"jp": k, "variants": {en: keys for en, keys in v.items()}}
              for k, v in groups.items() if len(v) > 1]
    report.sort(key=lambda e: -sum(len(x) for x in e["variants"].values()))
    out = os.path.join(ROOT, "work/translation/en/consistency_report.json")
    json.dump(report, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"{len(report)} Japanese strings with more than one English rendering -> {out}")


if __name__ == "__main__":
    main()
