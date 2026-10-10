"""Cut in-scope rows into translation slices (80 rows each, BASE_RULES).

Passes:
  story  : OP/MainEventMess01, dungeon events (by number), Base/MainEventMess*
  quest  : quest events
  talk   : Base/TalkMess*
  system : everything else (menus, items, skills, library, enemies, ...)
Rows keep file order; empty rows are skipped. Each row:
  {"key": "<unit>#<row id>", "speaker": jp, "speaker_en": en, "jp": text}
Slices (contain Japanese, local only): work/slices/<pass>/<pass>_NNN.json
English output expected at: work/translation/en/<pass>/<pass>_NNN.en.json

Usage:
    python tools/make_slices.py <pass>
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SIZE = 80


def glossary_map():
    g = json.load(open(os.path.join(ROOT, "work/glossary/names.json"), encoding="utf-8"))
    return {e["jp"]: e["en"] for sec in ("heroes", "villains") for e in g[sec]}


def units_for(pass_name, scope):
    def num(k):
        m = re.search(r"(\d+)\.mbb$", k)
        return int(m.group(1)) if m else 0
    if pass_name == "story":
        op = [k for k in scope if k == "Table/Event/OP/MainEventMess01.mbb"]
        dg = sorted((k for k, u in scope.items() if u["category"] == "Story events (dungeon)"), key=num)
        base = sorted((k for k in scope if k.startswith("Table/Event/Base/MainEventMess")), key=num)
        return op + dg + base
    if pass_name == "quest":
        return sorted(k for k, u in scope.items() if u["category"] == "Quest events")
    if pass_name == "talk":
        return sorted(k for k in scope if k.startswith("Table/Event/Base/TalkMess"))
    taken = set(units_for("story", scope) + units_for("quest", scope) + units_for("talk", scope))
    return sorted(k for k, u in scope.items() if k not in taken and not u["category"].startswith("Debug"))


def main():
    pass_name = sys.argv[1]
    scope = json.load(open(os.path.join(ROOT, "work/source/scope.json"), encoding="utf-8"))
    speakers = json.load(open(os.path.join(ROOT, "work/source/speakers.json"), encoding="utf-8"))
    names = glossary_map()
    rows = []
    for unit in units_for(pass_name, scope):
        u = scope[unit]
        d = json.load(open(os.path.join(ROOT, "work/source/text", u["canonical"] + ".json"), encoding="utf-8"))
        sp = {}
        names_ = {c.rsplit("/", 1)[-1] for c in u["copies"]} if unit.startswith("MainEventMess") else set()
        for t, rows_ in speakers.items():
            if t in u["copies"] or t.rsplit("/", 1)[-1] in names_:
                for k, v in rows_.items():
                    sp.setdefault(k, v)
        # System rows get the table's widest Japanese line (14 px per glyph) and
        # its maximum line count as their English budget.
        widths = [len(re.sub(r"\{[0-9A-F]{4}\}", "", ln))
                  for r in d["rows"] if r["jp"] for ln in r["jp"].split("\n")]
        table_px = max(widths or [1]) * 14
        table_lines = max([r["jp"].count("\n") + 1 for r in d["rows"] if r["jp"]] or [1])
        for r in d["rows"]:
            if not r["jp"]:
                continue
            s = sp.get(r["id"])
            row = {"key": f"{unit}#{r['id']}", "jp": r["jp"]}
            if s:
                row["speaker"] = s
                row["speaker_en"] = names.get(s, "?party" if s == "?party" else ("Alien Kool" if s == "#276" else f"[{s}]"))
            if u["status"] == "legacy":
                row["legacy"] = True
            if pass_name == "system":
                row["max_px"] = table_px
                row["max_lines"] = table_lines
            rows.append(row)
    out = os.path.join(ROOT, "work/slices", pass_name)
    os.makedirs(out, exist_ok=True)
    n = 0
    for i in range(0, len(rows), SIZE):
        n += 1
        json.dump({"slice": f"{pass_name}_{n:03d}", "rows": rows[i:i + SIZE]},
                  open(os.path.join(out, f"{pass_name}_{n:03d}.json"), "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)
    print(f"{pass_name}: {len(rows)} rows -> {n} slices in {out}")


if __name__ == "__main__":
    main()
