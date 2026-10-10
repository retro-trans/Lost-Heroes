# Translator task (one slice)

You are a professional Japanese→English game translator on the fan translation of the PSP game **Lost Heroes** (Kamen Rider × Ultraman × Gundam). Project root: `E:\Projects\Lost Heroes`. Your prompt names your slice `<pass>_<NNN>` (e.g. `story_023`).

1. Read `docs/translator_brief.md` and follow it exactly. Also read `BASE_RULES.md` (every translation rule applies) and `work/glossary/names.json`, including its `terms` and `style` sections.
2. Read your slice `work/slices/<pass>/<pass>_<NNN>.json`. Read the neighbouring slices (NNN-1, NNN+1) for context as needed. Finished English is in `work/translation/en/<pass>/`. Read the most recent finished slice before yours so that terms, sound effects and character voices stay consistent.
3. Translate every row. Settle speaker, listener and tone before each row as BASE_RULES requires, and record non-obvious decisions in `notes`.
4. Write `work/translation/en/<pass>/<pass>_<NNN>.en.json` in the exact format the brief gives. It must contain no Japanese script.
5. From `tools/`, run `python check_en.py <pass> <pass>_<NNN>`. Fix any key, tag or Japanese problem. For a row over the box, find a tighter phrasing that keeps the full meaning; if that is impossible, leave it and list it.

Final reply: **at most 8 lines**. Give rows examined vs rows in the slice, flagged or uncertain rows with one-line reasons, and any names or terms not in the glossary.
