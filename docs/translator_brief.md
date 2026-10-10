# Translator brief: Lost Heroes (PSP) → English

You translate one **slice** of 80 rows. Read this file, `BASE_RULES.md` (repo root; all of its rules apply), and the glossary `work/glossary/names.json` before starting.

## The game
Crossover dungeon RPG (Bandai Namco, 2012). Heroes from **Kamen Rider**, **Ultraman** and **Gundam** are pulled into the *Gaia Cubes*, pieces of their worlds fused together by **Regis**, an alliance of all three worlds' villains. The heroes have lost most of their power ("Lost Heroes") and must win it back.

- Gundams are characters named by their machine (00, Nu Gundam, Seravee...). Each speaks with its pilot's personality (see the glossary notes). Never swap in pilot names unless the Japanese uses them.
- Use English names exactly as the glossary gives them, in dialogue and in speaker labels. A name missing from the glossary: use the franchise's established English name. If you're unsure, romanize it and list it in your report.

## Input
`work/slices/<pass>/<slice>.json` → `{"slice": ..., "rows": [{"key", "jp", "speaker", "speaker_en", "legacy"?}]}`

- `speaker` / `speaker_en`: who says the line, recovered from the event script. Missing = not recovered. It may be narration, a party-dependent speaker, or a branch the extractor didn't follow. Infer it from context and say so in notes when it matters. `?party` = whichever party member the game picks.
- **Party-leader variant blocks:** many events contain runs of near-identical rows, one per possible party leader (only the current leader's line plays). They are labelled `?party` or not labelled. Voice each one from its wording (polite = OOO or Mebius, rough = Shotaro, Momotaros or Zero, curt = Heero or Setsuna...). Identical Japanese gets identical English.
- `\n` in `jp` is a line break inside one text box. **Do not reproduce Japanese line breaks.** Write one flowing English line; a script rewraps it later. The exception is deliberate layouts (lists, a two-line title, `Name\nTitle`), where you may use `\n`.
- `legacy: true` rows come from 8 tables stored in an older font encoding. A few kanji may still be mis-decoded. Infer the meaning from context, and note any row where you had to guess.
- Neighbouring slices (`<pass>_NNN±1`) are there for context. Read them when a line's referent or speaker is unclear.

## Output
Write `work/translation/en/<pass>/<slice>.en.json`:

```json
{"slice": "story_001", "rows_in_slice": 80, "rows_examined": 80,
 "rows": [{"key": "...", "en": "..."}, ...],
 "notes": [{"key": "...", "note": "..."}],
 "report": "short summary: flagged rows, uncertain calls, names not in glossary"}
```

- Exactly one output row per input row, same keys, same order. Never merge or split rows.
- **No Japanese script in the output file** (romanized names are fine). Quote nothing in Japanese in notes; describe it instead.
- If you can't translate a row, set `"en": null` and explain in notes.

## Control codes and placeholders
- `{XXXX}` tags (e.g. `{8074}`, `{806D}`, `{8004}`, `{8090}`) are control codes or variables. Keep every tag, in the position that matches the English wording.
- A tag followed by a run of full-width spaces (`{8073}　　　　　　　　　　　`) is a **name variable plus reserved padding**. In English write the tag only (`{8073}`); the build tool restores the padding. Example: `{8074}　　　　　　　たちは、\nキャンプに移動した。` → `{8074} and the team moved to camp.`
- Keep `?` `!` `……` meaning. Write ellipses as `...` and interrobangs as `!?`. Full-width `！！` becomes `!!` (or `!` if that reads better).

## Length
Story text boxes hold 2 lines of about 330 px. With the variable-width font that is roughly **50 characters per line, about 100 per box**. Write the full meaning first (BASE_RULES). Aim for ≤ 100 characters per row and flag rows over 110. Menus, item names and other UI rows: the slice will say if a tighter limit applies.

## Style reminders (BASE_RULES has the full list)
- Spoken, lively English that fits each character (Zero is cocky, Heero curt, Ankh rude, Mr. Bushido archaic, Den-O's Imagin each have their voice). Keep catchphrases recognisable.
- Restore dropped subjects and verbs where the scene settles who. Check the direction of 頼む/よろしく.
- Don't soften insults or threats. Don't assume gender for unknown people; use the glossary `g` field (`n` = they/it).
- Thought lines: `Name (thought...)` style only applies to speaker labels; inside text, use parentheses as the source does.
