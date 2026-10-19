"""Check English that the battle help/message banner shows against its 63-character buffer.

The banner (skill help, battle messages) holds 63 u16 codes including line breaks,
counted AFTER the game expands names and numbers; longer text is cut off ("...set
number of tu"). Name tags count as the longest name they can hold (players and the
Ride Machine 12, enemies 20), numbers as 5 digits.

Usage:
    python tools/check_banner.py
"""
import glob
import json
import os
import re

import check_en

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIMIT = 63
TABLES = ["Table/Skill/SkillHelpMessage.mbb", "Table/Battle/BattleMess.mbb", "Table/Skill/SkillMessage.mbb",
          "Table/Enemy/SkillMessage.mbb", "Table/Enemy/SystemMessage.mbb"]
# {8073} enemy name, {806D}/{806E}/{8074} hero (or Ride Machine) name, {806F} number
TAGS = {"{806D}": 12, "{806E}": 12, "{8074}": 12, "{8073}": 20, "{806F}": 5}
MARKUP = {"<tag_chr>": 20, "<act_ch>": 20, "<enemy_name>": 20, "<use_skill>": 20, "<hit_damage>": 5, "<br>": 1}


def shown_length(en, W):
    if "<" in en:
        t = en
        for k, v in MARKUP.items():
            t = t.replace(k, "x" * v)
        return len(re.sub(r"<[a-z_]+>", "x" * 16, t))
    lines = check_en.wrap(en, W, 336)
    n = sum(len(re.sub(r"\{[0-9A-F]{4}\}", "", ln)) for ln in lines) + len(lines) - 1
    return n + sum(TAGS.get(t, 0) for t in re.findall(r"\{[0-9A-F]{4}\}", en))


def main():
    W = check_en.widths()
    bad = 0
    for p in sorted(glob.glob(os.path.join(ROOT, "work/translation/en/*/*.en.json"))):
        for r in json.load(open(p, encoding="utf-8"))["rows"]:
            en = r.get("en")
            if en and any(r["key"].startswith(t + "#") for t in TABLES):
                n = shown_length(en, W)
                if n > LIMIT:
                    bad += 1
                    print(f"{os.path.basename(p)} {r['key']}: {n} > {LIMIT}: {en}")
    print(f"banner check: {bad} row(s) over {LIMIT}")


if __name__ == "__main__":
    main()
