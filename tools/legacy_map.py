"""Recover the older kanji glyph order used by a few stale message tables.

44 tables are encoded against an earlier font build: kana/ASCII are the same,
kanji codes are permuted. 36 of them are dead drafts (no script loads them):
NC04/MainEventMess01xx (old copies of NC01/01xx) and OP/MainEventMess0801-0805.
The 10 NC02 tables listed in LIVE are loaded by their event scripts (0226 and 0249
are single-message tables found once mbb.entry_total read the extra slot of empty tables).

Old->new kanji pairs are voted from "twin" strings: rows with identical
non-kanji skeletons in correctly encoded tables. Manual overrides (from
context reading) go in work/glossary/legacy_overrides.json.

    python tools/legacy_map.py <ALLRES.PCK>   -> work/glossary/legacy_kanji_map.json
"""
import collections
import json
import os
import sys

import count_text
import mbb
import walk_assets

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "work", "glossary", "legacy_kanji_map.json")
OVERRIDES = os.path.join(ROOT, "work", "glossary", "legacy_overrides.json")

LIVE = [f"Table/Event/Dungeon/NC02/MainEventMess{n}.mbb"
        for n in ("0208", "0209", "0211", "0223", "0224", "0226", "0228", "0246", "0247", "0249")]
DEAD = ([f"Table/Event/Dungeon/NC04/MainEventMess01{n:02d}.mbb" for n in range(0, 100)]
        + [f"Table/Event/OP/MainEventMess080{n}.mbb" for n in range(1, 6)])
LEGACY = set(LIVE) | set(DEAD)


def is_kanji(c):
    return 0x16C <= c < 0x900


def skeleton(codes):
    return tuple(-1 if is_kanji(c) else c for c in codes)


def load_tables(pck):
    with open(pck, "rb") as f:
        root = f.read()
    tables = {}
    for vpath, blob in walk_assets.walk("", root):
        if blob[:4] == b"TBB1" and b"MTBL" in blob[:0x200]:
            tables.setdefault(count_text.logical_path(vpath), blob)
    return {lp: [c for _, _, c in mbb.messages(b) if c] for lp, b in tables.items()}


def solve_rest(tables, mapping):
    """Fill unmapped old codes used by LIVE tables.

    Candidates come from run interpolation (old order is the new order with
    shifted runs, so a mapped neighbour a±k -> b±k implies a -> b) and every
    new kanji code; each is scored by how often the resulting character
    bigrams/trigrams occur in the correctly encoded corpus. Most confident
    assignments are fixed first and the loop repeats.
    """
    import math
    bi, tri = collections.Counter(), collections.Counter()
    for lp, rows in tables.items():
        if lp in LEGACY:
            continue
        for c in rows:
            bi.update(zip(c, c[1:]))
            tri.update(zip(c, c[1:], c[2:]))
    all_new = {x for (x, _y) in bi if is_kanji(x)} | {y for (_x, y) in bi if is_kanji(y)}
    occ = collections.defaultdict(list)
    for lp in LIVE:
        for c in tables.get(lp, []):
            for i, x in enumerate(c):
                if is_kanji(x):
                    occ[x].append((c, i))

    def cur(c, i):
        if i < 0 or i >= len(c):
            return None
        x = c[i]
        return mapping.get(x) if is_kanji(x) else x

    while True:
        todo = [a for a in occ if a not in mapping]
        if not todo:
            return
        used = set(mapping.values())
        best = []
        for a in todo:
            cands = set()
            for k in range(1, 6):
                for s in (-k, k):
                    if a + s in mapping:
                        cands.add(mapping[a + s] - s)
            cands |= all_new
            cands -= used
            scored = []
            for b in cands:
                s = 0.0
                for c, i in occ[a]:
                    l1, l2, r1, r2 = cur(c, i - 1), cur(c, i - 2), cur(c, i + 1), cur(c, i + 2)
                    if l1 is not None:
                        s += math.log1p(bi[(l1, b)])
                        if l2 is not None:
                            s += 1.5 * math.log1p(tri[(l2, l1, b)])
                    if r1 is not None:
                        s += math.log1p(bi[(b, r1)])
                        if r2 is not None:
                            s += 1.5 * math.log1p(tri[(b, r1, r2)])
                    if l1 is not None and r1 is not None:
                        s += 1.5 * math.log1p(tri[(l1, b, r1)])
                prior = any(mapping.get(a + d) == b + d for d in (-2, -1, 1, 2))
                scored.append((s + (2.0 if prior else 0.0), b))
            scored.sort(reverse=True)
            if not scored or scored[0][0] <= 0:
                continue
            margin = scored[0][0] - (scored[1][0] if len(scored) > 1 else 0)
            best.append((margin, a, scored[0][1]))
        if not best:
            return
        best.sort(reverse=True)
        for margin, a, b in best[:max(1, len(best) // 5)]:
            if b not in set(mapping.values()):
                mapping[a] = b


def main():
    tables = load_tables(sys.argv[1])
    normal = collections.defaultdict(set)
    for lp, rows in tables.items():
        if lp not in LEGACY:
            for c in rows:
                if any(is_kanji(x) for x in c):
                    normal[skeleton(c)].add(tuple(c))
    votes = collections.defaultdict(collections.Counter)
    for lp, rows in tables.items():
        if lp not in LEGACY:
            continue
        for c in rows:
            twins = normal.get(skeleton(c))
            if not twins or len(twins) > 1:
                continue                      # ambiguous skeleton: skip
            twin = next(iter(twins))
            for a, b in zip(c, twin):
                if is_kanji(a):
                    votes[a][b] += 1
    mapping = {}
    for a, cnt in votes.items():
        (b, n), *rest = cnt.most_common()
        if not rest or n >= 2 * rest[0][1]:
            mapping[a] = b
    solve_rest(tables, mapping)
    if os.path.exists(OVERRIDES):
        for a, b in json.load(open(OVERRIDES)).items():
            mapping[int(a, 16)] = int(b, 16)
    json.dump({f"0x{a:04X}": f"0x{b:04X}" for a, b in sorted(mapping.items())},
              open(OUT, "w"), indent=0)
    need = collections.Counter(x for lp in LIVE for c in tables.get(lp, []) for x in c if is_kanji(x))
    missing = {a: n for a, n in need.items() if a not in mapping}
    print(f"mapped {len(mapping)} old codes; live tables use {len(need)} kanji codes, "
          f"{len(missing)} unmapped ({sum(missing.values())} occurrences)")


if __name__ == "__main__":
    main()
