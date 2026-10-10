# Handoff: how to continue the translation

Goal: translate the whole game (story first), then build an English patch.

**Status (2026-10-09):** all slices are translated (story 194, system 97, quest 57, talk 12) and `name_fix.py --apply` has run once. Build 0.1.1 has the EBOOT decrypted (`tools/eboot_decrypt.py`) and the VWF trim tables patched (`tools/eboot_patch.py`). Latest local build 0.1.9 (`work/output/LostHeroes_EN_v0.1.9.iso`, Camp menu composites via `tex_edit` + `tools/sprite_log.py`; 0.1.7: native 4x Latin font via `tools/font4x.py` + `tools/eboot_font4x.py`; 0.1.6 content below): unreferenced-but-live dungeon tables, in-engine opening narration, tutorial screenshots and remaining menu textures in English; texture labels drawn heavier (see CHANGELOG). Remaining: emulator test by the user, proofreading story 019+, review_queue items. Build order: build_font.py -> font4x.py -> eboot_patch.py -> apply_en.py -> iso_patch.py (ALLRES, then EBOOT in place).

## State lives on disk
- Slices to translate: `work/slices/<pass>/<pass>_NNN.json` (story 194, quest 57, talk 12, system 97).
- Finished English: `work/translation/en/<pass>/<pass>_NNN.en.json`. A slice is done when this file exists and `python tools/check_en.py <pass> <slice>` passes.
- Find what's left: compare the two folders.

## Launching translators
- Story / quest / talk: general-purpose agent (Opus); prompt `Translate slice story_NNN. Follow E:\Projects\Lost Heroes\docs\translator_task.md exactly.` (quest/talk: same task file, slice name quest_NNN / talk_NNN).
- System/UI: same, with model `sonnet` and `docs/translator_task_system.md`.
- Before launching a batch, run `python tools/tm_fill.py <pass> --apply` to fill slices that are 100% exact repeats for free.
- Keep about 10–12 running. Check `get_usage`; stop launching near 90–95% of the 5-hour window. When it is exhausted, wait with a background `sleep` until the reset.
- After each report: add new terms to `work/glossary/names.json` (terms/style/ui), log open issues in `docs/review_queue.md`, and add spelling fixes to `tools/name_fix.py` (dry run only until proofreading).

## After all slices are done
1. Proofreading pass (agents fix meaning). Focus on story_001–035 (written before the kanji fix round 2 and the speaker-label fixes) and the review_queue items.
2. `python tools/name_fix.py --apply` (names only AFTER agent fixes, per BASE_RULES).
3. Cross-table name consistency: the same Japanese string with different English (see review_queue).
4. `python tools/strip_jp.py --check`, then `python tools/check_en.py` for all passes.
5. Build: `tools/apply_en.py` → `work/output/ALLRES.PCK`, then `tools/iso_patch.py` (path `PSP_GAME/USRDIR/ALLRES.PCK`).
6. Blocker for a playable build: VWF/EBOOT patch. It needs `NPJH50647.BIN` (decrypted EBOOT dumped by PPSSPP) in `incoming/`. Font assets are ready in `work/output/font/` (1x pages + native 4x Latin atlas, SRW MX approach).
7. Version the first test build 0.1.0 and update the changelog. No GitHub release without explicit permission.
