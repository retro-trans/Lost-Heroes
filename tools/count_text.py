"""Count translatable Japanese text in every MTBL message table.

Walks ALLRES.PCK recursively (see walk_assets.py), parses every TBB1/MTBL
file (.mbb, plus the quest tables stored as .pck), de-duplicates copies of
the same logical file that appear in several packs, and reports strings and
characters per category.

Code ranges (u16, code = font glyph index + 1):
    0x0001-0x0040  ASCII (space, ?, 0-9, A-Z, a-z)
    0x0041-0x00E9  kana
    0x00EA-0x017C  symbols / full-width ASCII / Japanese punctuation
    0x017D-0x0900  kanji glyphs (custom order)
    0x8000-0x80FF  control codes (0x8001 = line break)
    other >=0x3000 raw Unicode (kana / kanji / full-width)

Usage:
    python tools/count_text.py <ALLRES.PCK> <out_json>
"""
import collections
import json
import sys

import mbb
import walk_assets

CATEGORIES = [
    # (prefix of logical path, category)
    ("Table/Event/Dungeon/", "Story events (dungeon)"),
    ("Table/Event/Base/", "Town/base conversations"),
    ("Table/Event/Quest/", "Quest events"),
    ("Event/Quest/", "Quest events"),
    ("Graph/Dg/Fld/", "Dungeon field messages"),
    ("Table/Event/Battle/", "Battle events"),
    ("Table/Event/Tutorial/", "Tutorials"),
    ("Table/Event/OP/", "Opening"),
    ("Table/Event/", "Other events"),
    ("Table/Quest/", "Quests"),
    ("Table/CutScene/", "Cut-scene captions"),
    ("Graph/CutScene/", "Cut-scene captions"),
    ("Table/Item/", "Items"),
    ("Table/Skill/", "Skills"),
    ("Table/Enemy/", "Enemies"),
    ("Table/Battle/", "Battle UI"),
    ("Table/ChipLib/", "Library / glossary"),
    ("Table/StaffRoll/", "Staff roll"),
    ("Table/TestData/", "Debug / test (skip)"),
    ("Table/", "System / menus"),
]


def is_control(c):
    return 0x8000 <= c <= 0x80FF or c in (0xA000, 0xF000)


def is_japanese(c):
    if is_control(c):
        return False
    return 0x41 <= c <= 0xE9 or 0x17D <= c <= 0x900 or c >= 0x3000


def logical_path(vpath):
    parts = vpath.split("::")
    leaf = parts[-1]
    if "Table/" in leaf:
        return leaf[leaf.index("Table/"):]
    if leaf.startswith("Caption_"):
        return "Graph/CutScene/" + leaf
    if leaf.endswith("DungeonMess.mbb"):
        # Graph/Dg/Fld/NC01/A01/DG_NC01A01_pk.cmp::pack.pck::DungeonMess.mbb
        return parts[0].rsplit("/", 1)[0] + "/DungeonMess.mbb"
    # Quest tables: Event/Quest/DG_QUESTnnn_pk.cmp::DG_QUESTnnn_pk.pck
    return parts[0].rsplit(".", 1)[0]


def category(lpath):
    for prefix, cat in CATEGORIES:
        if lpath.startswith(prefix):
            return cat
    return "Other"


def main():
    pck, out = sys.argv[1], sys.argv[2]
    with open(pck, "rb") as f:
        root = f.read()

    # logical path -> set of distinct file contents
    files = collections.defaultdict(dict)
    for vpath, blob in walk_assets.walk("", root):
        if blob[:4] == b"TBB1" and b"MTBL" in blob[:0x200]:
            files[logical_path(vpath)].setdefault(blob, []).append(vpath)

    per_file = {}
    variants = {}
    for lpath, versions in files.items():
        if len(versions) > 1:
            variants[lpath] = [len(v) for v in versions.values()]
        # Use the largest variant as the canonical copy.
        blob = max(versions, key=len)
        slots = empty = jp = ascii_only = chars = lines = 0
        texts = []
        for _b, _e, codes in mbb.messages(blob):
            slots += 1
            if not codes:
                empty += 1
                continue
            visible = [c for c in codes if not is_control(c)]
            if any(is_japanese(c) for c in visible):
                jp += 1
                chars += len(visible)
                lines += 1 + codes.count(0x8001)
                texts.append(tuple(codes))
            else:
                ascii_only += 1
        per_file[lpath] = dict(
            category=category(lpath), slots=slots, empty=empty,
            japanese=jp, non_japanese=ascii_only, chars=chars, lines=lines,
            texts=texts,
        )

    cats = collections.OrderedDict()
    all_unique = set()
    for lpath in sorted(per_file):
        r = per_file[lpath]
        c = cats.setdefault(r["category"], dict(
            files=0, slots=0, empty=0, japanese=0, non_japanese=0,
            chars=0, lines=0, unique=set()))
        c["files"] += 1
        for k in ("slots", "empty", "japanese", "non_japanese", "chars", "lines"):
            c[k] += r[k]
        c["unique"].update(r["texts"])
        all_unique.update(r["texts"])

    def uniq_chars(s):
        return sum(len([c for c in t if not is_control(c)]) for t in s)

    report = {
        "logical_files": len(per_file),
        "files_with_differing_copies": variants,
        "categories": {
            k: dict({kk: vv for kk, vv in v.items() if kk != "unique"},
                    unique_strings=len(v["unique"]),
                    unique_chars=uniq_chars(v["unique"]))
            for k, v in cats.items()
        },
        "totals": {
            "slots": sum(r["slots"] for r in per_file.values()),
            "empty": sum(r["empty"] for r in per_file.values()),
            "japanese": sum(r["japanese"] for r in per_file.values()),
            "non_japanese": sum(r["non_japanese"] for r in per_file.values()),
            "chars": sum(r["chars"] for r in per_file.values()),
            "lines": sum(r["lines"] for r in per_file.values()),
            "unique_strings": len(all_unique),
            "unique_chars": uniq_chars(all_unique),
        },
        "files": {k: {kk: vv for kk, vv in v.items() if kk != "texts"}
                  for k, v in sorted(per_file.items())},
    }
    with open(out, "w", encoding="utf-8") as o:
        json.dump(report, o, indent=1)

    print(f"{'category':28s} {'files':>5s} {'JP str':>7s} {'unique':>7s} {'chars':>8s} {'uniq ch':>8s}")
    for k, v in report["categories"].items():
        print(f"{k:28s} {v['files']:5d} {v['japanese']:7d} {v['unique_strings']:7d} {v['chars']:8d} {v['unique_chars']:8d}")
    t = report["totals"]
    print(f"{'TOTAL':28s} {len(per_file):5d} {t['japanese']:7d} {t['unique_strings']:7d} {t['chars']:8d} {t['unique_chars']:8d}")
    print(f"slots {t['slots']}, empty {t['empty']}, non-japanese {t['non_japanese']}, lines {t['lines']}")
    print(f"files whose copies differ: {len(variants)}")


if __name__ == "__main__":
    main()
