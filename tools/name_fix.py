"""Glossary name sweep over finished English (BASE_RULES: run AFTER agent fixes).

Rules are whole-word replacements of known wrong spellings -> glossary form.
Default is a dry run that prints every change; --apply writes the files.

Usage:
    python tools/name_fix.py [--apply]
"""
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# wrong spelling (regex, whole word) -> glossary spelling
RULES = [
    (r"\bOyassan\b", "Boss"),
    (r"\bGreat Shocker\b", "Dai-Shocker"),
    (r"\bImperializer\b", "Imperizer"),
    (r"\bSharkwhale\b", "Samekujira"),
    (r"\bSea Anemone Jaguar\b", "Isoginjaguar"),
    (r"\bU Killersaurus\b", "U-Killersaurus"),
    (r"\bUltimate D\b(?!opant)", "Ultimate Dopant"),
    (r"\bBirugamo\b", "Bilgamo"),
    (r"\bAlien Cool\b", "Alien Kool"),
    # specific before general: "pseudo-Solar Furnace" must not become "pseudo-GN Drive"
    (r"\bpseudo-Solar Furnaces\b", "GN Drive Taus"),
    (r"\bpseudo-Solar Furnace\b", "GN Drive Tau"),
    (r"GN Drive \[T\]", "GN Drive Tau"),
    (r"\b[Pp]seudo[- ]GN Drives\b", "GN Drive Taus"),
    (r"\b[Pp]seudo[- ]GN Drive\b", "GN Drive Tau"),
    # official Gundam Wing English is "Planet Defensor"
    (r"\bPlan(?:ate|et) Defens[eo]rs?\b", "Planet Defensor"),
    (r"\bTrigar Shot\b", "Tri-Gar Shot"),
    (r"\bStand Firm\b", "Defiant Stance"),
    (r"\bFinalusion\b", "Finalfusion"),
    (r"\bUltra Ice Spot\b", "Ultra Eye Spot"),
    (r"\bMonster Road\b", "Monsload"),
    # アイス is always Ankh's ice candy (canon: ice pops), never ice cream
    # Alien Baltan's laugh: "Fofofo" -> "Fo, fo, fo" (same syllable count)
    (r"\bFo(?:fo){2,}\b", lambda m: ", ".join(["Fo"] + ["fo"] * (len(m.group(0)) // 2 - 1))),
    (r"\b[Uu]niversal translator\b", "Pan-Space Interpreter"),
    (r"\bIce Cream\b", "Ice Pop"),
    (r"\bice cream\b", "ice pop"),
    (r"\bMagnelium Medicali[sz]er\b", "Magnerium Medicalizer"),
    (r"\bRevol Crush\b", "Revolcrash"),
    (r"\bDissolder\b", "Disolder"),
    (r"\bCrit\. Normal\b", "Crit Normal"),
    (r"\bSolar Furnaces\b", "GN Drives"),
    (r"\bSolar Furnace\b", "GN Drive"),
    (r"\bSenpai\b", "Sempai"),
    (r"\bBound Dog\b", "Bound Doc"),
    (r"\b[Ll]iving core unit\b", "Life Core"),
    (r"\b[Bb]iological unit\b", "Life Core"),
    (r"\bBemstar \(Modified\)", "Modified Bemstar"),
    (r"\bStatus Resist Up\b", "Status Res Up"),
    (r"\bElemental Resist Up\b", "Element Res Up"),
    (r"\bCure Dark\b", "Cure Blind"),
]


def main():
    apply = "--apply" in sys.argv
    total = 0
    for p in sorted(glob.glob(os.path.join(ROOT, "work/translation/en/*/*.en.json"))):
        d = json.load(open(p, encoding="utf-8"))
        changed = False
        for r in d["rows"]:
            en = r.get("en")
            if not en:
                continue
            new = en
            for pat, rep in RULES:
                new = re.sub(pat, rep, new)
            if new != en:
                total += 1
                print(f"{os.path.basename(p)} {r['key']}:\n  - {en}\n  + {new}")
                r["en"] = new
                changed = True
        if changed and apply:
            json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"{total} rows {'changed' if apply else 'would change'}")


if __name__ == "__main__":
    main()
