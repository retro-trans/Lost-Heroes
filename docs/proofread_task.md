# Proofreading task (one slice)

You proofread one finished slice of the fan translation of the PSP game **Lost Heroes** (Kamen Rider × Ultraman × Gundam). Project root: `E:\Projects\Lost Heroes`. Your prompt names the slice `<pass>_<NNN>`.

The early story slices were translated before two fixes: a kanji-decoding correction round and speaker-label corrections. Some English may follow a misread kanji or a wrong speaker.

1. Read `docs/translator_brief.md`, `BASE_RULES.md` and `work/glossary/names.json` (including `terms` and `style`).
2. Read the source `work/slices/<pass>/<pass>_<NNN>.json` and the English `work/translation/en/<pass>/<pass>_<NNN>.en.json` side by side. Read the neighbouring slices for context as needed.
3. Check every row:
   - **Meaning:** the English says what the Japanese says, with nothing dropped, added or reversed. Restored pro-drop subjects and objects are correct, and the 頼む/よろしく direction is right.
   - **Speaker and voice:** the speaker labels can be wrong. Where a line makes no sense for its labelled speaker, check the event script (`work/source/flat/.../<table number>.bla`; `MessWinSet(TextIdOffset+N)` usually plays entry N+1). Each character keeps the voice set by the glossary and later slices.
   - **Terms:** names and terms match the glossary exactly.
   - **Format:** tags, line breaks and the box limits are respected.
4. Fix errors in place, in the `en` field only. Do not restyle lines that are already correct; this is a correction pass, not a rewrite. Add a short `notes` entry for each changed row: `proofread: <why>`.
5. From `tools/`, run `python check_en.py <pass> <pass>_<NNN>` and fix any problem it reports.

Final reply: **at most 8 lines**. Give rows checked, rows changed, the most important corrections in one line each, and any open question you could not settle.
