"""Fill QuestEventMessNNN rows from the matching DG_QUESTNNN_pk translation.

Table/Event/Quest/QuestEventMessNNN.mbb is a copy of Event/Quest/DG_QUESTNNN_pk
(same row ids). For each untranslated quest slice, a row whose Japanese equals
the DG_QUEST row with the same id reuses that English; otherwise translation
memory (tm_fill) is tried. Slices fully covered are written; others are reported.

Usage:
    python tools/quest_copy_fill.py [--apply]
"""
import glob
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tm_fill  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    apply = "--apply" in sys.argv
    jp, en = {}, {}
    for src in glob.glob(os.path.join(ROOT, "work/slices/quest/*.json")):
        for r in json.load(open(src, encoding="utf-8"))["rows"]:
            jp[r["key"]] = r["jp"]
    for p in glob.glob(os.path.join(ROOT, "work/translation/en/*/*.en.json")):
        for r in json.load(open(p, encoding="utf-8"))["rows"]:
            if r.get("en") is not None:
                en[r["key"]] = r["en"]
    tm = tm_fill.memory()
    out_dir = os.path.join(ROOT, "work/translation/en/quest")
    for src in sorted(glob.glob(os.path.join(ROOT, "work/slices/quest/*.json"))):
        name = os.path.basename(src)[:-5]
        if os.path.exists(os.path.join(out_dir, name + ".en.json")):
            continue
        rows = json.load(open(src, encoding="utf-8"))["rows"]
        out, miss = [], 0
        for r in rows:
            m = re.match(r"Table/Event/Quest/QuestEventMess(\d+)\.mbb#(.+)$", r["key"])
            twin = f"Event/Quest/DG_QUEST{m.group(1)}_pk#{m.group(2)}" if m else None
            if twin and twin in en and jp.get(twin) == r["jp"]:
                out.append({"key": r["key"], "en": en[twin]})
            elif r["jp"] in tm:
                out.append({"key": r["key"], "en": tm[r["jp"]]})
            else:
                out.append({"key": r["key"], "en": None}); miss += 1
        print(f"{name}: {len(rows) - miss}/{len(rows)} covered")
        if apply and not miss:
            json.dump({"slice": name, "rows_in_slice": len(rows), "rows_examined": len(rows), "rows": out,
                       "notes": [], "report": "filled from the DG_QUEST twin rows / translation memory"},
                      open(os.path.join(out_dir, name + ".en.json"), "w", encoding="utf-8"),
                      ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
