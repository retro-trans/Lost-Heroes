"""Attach speakers to event dialogue rows by replaying the event scripts.

Script pattern (Lua 5.1, see lua51.py):
    CharaNameIn(slot, CHARA_NAME[id], side)   -> speaker = id
    MessWinSet(TextIdOffset + n)              -> shows entry n + shift, where shift is
        normally TextIdOffset+1, but empty entries inside a table push later lines
        down (e.g. 0205); see shift_map.
    CharaNameOut()                            -> no speaker (narration)
CHARA_NAME[id] == id; the shown name is CharacterName.mbb block 3, entry id+1.
A non-constant speaker (e.g. a party-dependent GetCharaID call) is "?party".

Writes work/source/speakers.json: {table path in script: {row_id: speaker}}
Usage:
    python tools/speakers.py
"""
import collections
import glob
import json
import os
import re

import lua51

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def speaker_names():
    d = json.load(open(os.path.join(ROOT, "work/source/text/Table/Common/CharacterName.mbb.json"),
                       encoding="utf-8"))
    return {int(r["id"].split(".")[1]) - 1: r["jp"] for r in d["rows"] if r["id"].startswith("3.")}


def trace(path):
    f = lua51.load(open(path, "rb").read())
    g = lua51.run_globals(f)
    offset = int(g.get("TextIdOffset") or 0)
    table = g.get("MBB_FILENAME") or next(
        (c for c in all_consts(f) if isinstance(c, str) and re.match(r"Table/.*\.mbb$", c)), None)
    events, speaker = [], None
    for _d, fn, args in lua51.calls(f):
        if fn == "CharaNameIn" and len(args) >= 2:
            a = args[1]
            if isinstance(a, tuple) and str(a[1]).startswith("CHARA_NAME."):
                speaker = int(float(str(a[1]).split(".", 1)[1]))
            else:
                speaker = "?party"
        elif fn == "CharaNameOut":
            speaker = None
        elif fn == "MessWinSet" and args:
            a = args[0]
            text = lua51.fmt(a) if isinstance(a, tuple) else ""
            m = re.match(r"TextIdOffset\+(\d+)(\+)?", text)
            if m:
                # "TextIdOffset+3+k": k picks a party-leader variant at runtime,
                # so the speaker is whoever leads, not the last constant name.
                events.append((int(m.group(1)), "?party" if m.group(2) else speaker))
    return table, offset, events


def shift_map(offset, events, entries):
    """Map each used n to an entry index. Base is n + TextIdOffset + 1, but
    some tables contain empty entries the script's numbering does not count
    (0205: lines 0-34 -> +1, 35+ -> +2 across the empty entry 36). Walk the
    used n in order and bump the shift whenever it would land on an empty
    entry. Returns ({n: index}, adjusted?)."""
    shift, out, adjusted = offset + 1, {}, False
    for n in sorted({n for n, _ in events}):
        while 0 <= n + shift < len(entries) and not entries[n + shift]:
            shift += 1
            adjusted = True
        out[n] = n + shift
    return out, adjusted


def table_entries(table):
    """Non-empty flags per entry of block 0 of the decoded table."""
    path = os.path.join(ROOT, "work/source/text", table + ".json")
    if not os.path.exists(path):
        alt = [p for p in glob.glob(os.path.join(ROOT, "work/source/text/**/" + os.path.basename(table) + ".json"),
                                    recursive=True)]
        if not alt:
            return None
        path = alt[0]
    rows = {r["id"]: r["jp"] for r in json.load(open(path, encoding="utf-8"))["rows"]}
    ids = [int(k.split(".")[1]) for k in rows if k.startswith("0.")]
    if not ids:
        return None
    n = max(ids) + 1
    return [bool(rows.get(f"0.{i}")) for i in range(n)]


def all_consts(f):
    yield from f["consts"]
    for p in f["protos"]:
        yield from all_consts(p)


def main():
    names = speaker_names()
    out, seen = {}, set()
    stats = collections.Counter()
    for p in sorted(glob.glob(os.path.join(ROOT, "work/source/flat/Event/**/*.bla"), recursive=True)):
        key = os.path.relpath(p, os.path.join(ROOT, "work/source/flat")).split(os.sep)[-1]
        if not os.path.isfile(p) or key in seen:
            continue
        seen.add(key)
        try:
            table, offset, events = trace(p)
        except Exception as e:  # noqa: BLE001
            stats["parse_error"] += 1
            continue
        if not table or not events:
            continue
        entries = table_entries(table)
        if entries is None:
            stats["table_missing"] += 1
            continue
        index, adjusted = shift_map(offset, events, entries)
        stats["shift_adjusted" if adjusted else "shift_declared"] += 1
        rows = {}
        for n, sp in events:
            rows.setdefault(f"0.{index[n]}", sp)
        named = {}
        for rid, sp in rows.items():
            if isinstance(sp, int):
                named[rid] = names.get(sp, f"#{sp}")
                stats["named"] += 1
            else:
                named[rid] = sp
                stats["narration" if sp is None else "party"] += 1
        out.setdefault(table, {}).update(named)
    json.dump(out, open(os.path.join(ROOT, "work/source/speakers.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=0)
    print(f"{len(out)} tables; rows: {dict(stats)}")


if __name__ == "__main__":
    main()
