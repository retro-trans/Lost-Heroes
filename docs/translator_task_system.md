# Translator task: system/UI slice

You translate one **system** slice (menus, items, skills, enemies, library entries, battle messages, dungeon messages, save/load, staff roll) for the PSP game **Lost Heroes** (Kamen Rider × Ultraman × Gundam). Project root: `E:\Projects\Lost Heroes`.

1. Read `docs/translator_brief.md` (format, tags and placeholders), `BASE_RULES.md`, and `work/glossary/names.json`. Use its `ui` section for stat and menu vocabulary (ATK, DEF, Physical/Ranged, Null, Reflect, Support Unit...) so every table matches.
2. Read your slice `work/slices/system/system_<NNN>.json` and its neighbours for context. Each row has `max_px` (pixel width per line) and `max_lines`. They come from the widest Japanese line in that table, at 14 px per Japanese character. English uses a variable-width font: lowercase letters average about 6.5 px, capitals about 9 px, a space about 4 px.
3. Translate every row:
   - **Names must match the glossary exactly**: characters, machines, monsters, terms. A franchise name missing from the glossary: use the established English name.
   - Items, skills and attacks: use official franchise English where one exists (e.g. "Specium Ray", "Rider Kick", "God Finger"). Otherwise write a short, punchy game-style name. Keep naming consistent within the table.
   - Descriptions and messages: clear and concise, with abbreviations allowed (HP, SP, ATK, DEF, Lv, Dmg, x2...). Keep every `{XXXX}` tag; a name-variable tag followed by full-width spaces is written as the tag alone.
   - Debug/test rows (obviously dev text): translate literally and keep them short.
   - Rows that are only numbers, symbols or ASCII: copy them unchanged.
4. Write `work/translation/en/system/system_<NNN>.en.json` in the brief's format, with no Japanese script.
5. From `tools/`, run `python check_en.py system system_<NNN>`. Rows over budget: shorten or abbreviate without dropping meaning. Leave a row over budget and list it only if that is impossible.

Final reply: **at most 8 lines**. Give rows examined vs rows in the slice, rows left over budget, uncertain calls, and new terms not in the glossary.
