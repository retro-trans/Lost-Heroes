# Changelog

## 0.1.16 (local test build, 2026-10-19, not released)
- **Battle banner text no longer cut off.** The banner that shows skill help and battle messages holds 63 characters counted after names and numbers are filled in (the Ride Machine's name made "...main cannon charge reset to" lose its end). 22 lines shortened (SkillHelpMessage, BattleMess, SkillMessage, Enemy/SkillMessage); new `tools/check_banner.py` checks every banner table with names at their longest (12 heroes / Ride Machine, 20 enemies) and numbers at 5 digits.
- **Ride Dungeon "Armor" label**: this HUD uses the shared window page (sprite 72 at x=57), not the Ride battle page; the box started at x=54, cutting the A.

## 0.1.15 (local test build, 2026-10-17, not released)
- **"ライドマシン took 738 damage!" and 43 more last lines.** The 32 tables whose entry 0 is a marker never had their uncounted last entry read (the marker hid it), so the last line of several scenes, the Base info lines, two Ride Machine skill helps, CharacterName 16 (Ride Machine) and others stayed Japanese. 17 filled from translation memory (`extra_014`), 27 translated (`extra_015`).
- **Ride battle "Armor" label**: the game samples it from about x=6 of the page, cutting the A; the label now sits at x=7-24 (smaller, lighter so it stays readable).
- **Ride battle help banner** shows at most 63 characters (the longest Japanese line in Table/Battle/BattleMess.mbb): "...flinch and" was cut. Shortened BattleMess 0.32 (barrage help) and 0.87 (main cannon out of charge) to 62.

## 0.1.14 (local test build, 2026-10-15, not released)
- Save details: the level label is " Lv", so a name too long for dot leaders still reads "Nu Gundam Lv1". Verified 0.1.13's save screen in PPSSPP after re-saving: Lost Heroes / Save Data / Base: Briefing Room / Play Time / Zero....Lv1.

## 0.1.13 (local test build, 2026-10-15, not released)
- **Save-data details in English.** The game writes UTF-8 strings from the EBOOT into PARAM.SFO, which the PSP's own save/load screen shows: title "Lost Heroes", "Save Data" / "Suspend Data", "Play Time h:mm:ss", ": " after the area, "." leaders, "Lv" and half-width digits; the data-install title and description too (`eboot_patch.py` SFO_STRINGS, each checked against the original and its slot). Existing saves keep their old Japanese details until saved again.
- **Title-screen copyright line in English** (`work/ui/tex/Title__copyright.json`): (c)Ishimori Pro, TV Asahi, ADK, Toei / (c)Ishimori Pro, Toei / (c)Sotsu, Sunrise / (c)Sotsu, Sunrise, MBS / (c)Tsuburaya Pro. The screen overlays sprite 14 from the Sotsu-Sunrise line onto the Sotsu-Sunrise-MBS line, so both lines share an identical prefix.

## Release 0.1.12 (2026-10-15)
- Public release of build 0.1.12: `LostHeroes-English-0.1.12.xdelta` (from the original ISO) and `LostHeroes-English-0.1.9-to-0.1.12.xdelta` (from the published 0.1.9 image, recreated from its patch and checked against its SHA-256). Notes and canonical metadata in `docs/releases/`.

## 0.1.12 (local test build, 2026-10-15, not released)
- Base screen header read "Ba se": the game draws it from two fixed-size sprites (32 and 33) 4 px apart, which shared pixels with the larger "Base HQ" label. Now a big cyan "B" plus small-capital "ASE" on the same baseline, matching the game's own CAMP/STATUS/ITEM headers; both sprites moved to free space on the page. (Widening a sprite rect does not help: the UI keeps each sprite's on-screen size and squeezes it.)
- `tex_edit` composites accept `valign: bottom`.

## 0.1.11 (local test build, 2026-10-11, not released)
- Title screen footer, as in SRW Z3: `v0.1.11` and `github.com/retro-trans`, right-aligned in the bottom right of the press-start background (`work/ui/tex/Title__footer.json`). The version comes from the new `VERSION` file; `tex_edit` gained `overlay` boxes (draw over opaque art) and the `{version}` placeholder.
- Includes all 0.1.10 fixes.

## 0.1.10 (local test build, 2026-10-11, not released)
- **Battle name plate fixed** (every hero showed "Rider 1"). An MTBL entry offset smaller than the offset table (1, 2, ...) is a marker the game relies on, not a string; `Table/Enemy/PlayerName.mbb` uses 1. `mbb` now reads such entries as `Mark` values and `mbb_write` writes them back (32 tables carry markers). Verified live in PPSSPP by restoring the marker in memory: each hero's plate shows its own name. PlayerName's hidden entry 16 (Ride Machine) is now translated.
- **"Rider 1attacked!" fixed.** The message formatter (0xdc3c4) deletes every 0x0001 after a name tag (Japanese name padding), and English spaces were 0x0001. Spaces now use 0x00EB, the font's own half-width space (glyph-table char U+0020); '"' moved to 0x014F. Fonts, 4x pages and EBOOT trims rebuilt.
- **Single-message tables translated** (e.g. the Begins/Desert Cube "Something's here!", cross inscriptions, door and capsule messages). About 140 tables count only empty entries and keep their one string in the uncounted extra slot; `mbb.entry_total` now reads it. 91 rows translated (`extra_011`/`012`); NC02/MainEventMess0226 and 0249 are legacy-encoded live tables.
- **Battle textures relabelled.** `tex_edit` only scanned `Graph/` paths, so the copies battles load from `Battle/Btl_*_pk.cmp` stayed Japanese (INFO panel stat labels and others). It now scans every pack (104 texture copies).
- Names: Spider Man -> **Man Spider**, Bogal -> **Bogarl** (project lead's decision; `docs/glossary_decisions.md`), 96 rows.

## Release 0.1.9 (2026-10-10)
- First public release: build 0.1.9 as `LostHeroes-English-0.1.9.xdelta` (full patch from the original NPJH50647 v1.01 ISO), packaged with the Retro Trans release builder (game ID `lost-heroes`, platform PSP, edition `NPJH50647`). Notes and canonical metadata in `docs/releases/`.

## Repository (2026-10-10)
- Public repository at https://github.com/retro-trans/Lost-Heroes (MIT). `tools/eboot_decrypt.py` is a port of PPSSPP code and is relicensed GPL-2.0-or-later (header + `docs/licenses/GPL-2.0.txt`).

## 0.1.9 (local test build, 2026-10-09, not released)
- Camp menu "Equip Force": the separator dot (sprite 51) is blanked, and both words share one size (the descender in "Equip" had made it render smaller). The whole-"Force" sprite 52 (Database > Force Data) moved to its own spot in the enlarged page, so the Camp row no longer needs extra spacing. Composites accept `line_h` and a fixed `style.size`.

## 0.1.8 (local test build, 2026-10-09, not released)
- **Camp menu rows reworded and re-laid out**: "Use Skill", "Skill Tree" (no wide gap), "Equip · Force", "Check Quests". The game assembles these rows from several sprites drawn side by side (found with `tools/sprite_log.py`, a PPSSPP logging breakpoint on the sprite routine 0x13c42c). New `tex_edit` spec features:
  - `composites`: render the whole phrase once, cut it into the pieces' rectangles; words are nudged so the 1 px screen seams between pieces never cut a glyph.
  - pieces whose pixels are shared with other sprites are moved to free space and their GFUV rect repointed in every copy of the `.gtx` (Camp.gtx: sprites 44, 59, 112).
  - `grow`: CampWindow_4444 is now 256x512 (the extra rows hold moved pieces; verified in game).
- Fix: `font4x.py` now writes the GFPT size field properly (it is the u32 size of the 2NBF block, not page counts; earlier output happened to be correct).

## 0.1.7 (local test build, 2026-10-09, not released)
- **Native 4x Latin font** (SRW MX approach, adapted to this engine). `tools/font4x.py` appends the GenEi Latin glyphs at 4x (the exact canvases the 1x glyphs are box-filtered from) as extra 256x512 pages in Font14 (3 pages, 56x64 cells), Font10 (2 pages, 40x40) and FontStaff (3 pages, 60x64). The game's font loader (0x144378) creates a texture for every page, so no loader change is needed; glyphs-per-page is unchanged (576 / 1275).
- `tools/eboot_font4x.py` (run by `eboot_patch.py`): the single glyph draw path (0x14464c) calls 0x144a30 for the page texture at 0x1447e0; that jal now goes to `latin_tex`, which for Latin codes rewrites the caller's source rect to the 4x cell and returns the 4x page's texture. Destination size, VWF advances and line layout are unchanged; Japanese glyphs use the original path. 56 instructions + 1,157 bytes of code->slot tables appended after segment 1's BSS (BSS written out as zeros; module memory +1.4 KB); 7 type-A relocations added and the hook's R_MIPS_26 retargeted to segment 1.
- Verified in an isolated portable PPSSPP (`work/build/ppsspp_test`, `tools/boottest.py`, `tools/ppsspp_dbg.py`): boots, font table holds 7/4 page textures, the hook code runs (JIT-compiled), title/menus/dialogue render; at 4x internal resolution English text is sharp (was pixelated in 0.1.6) with identical spacing. At 1x internal resolution (and on real hardware) the 4x texture is point-sampled without mipmaps, so text is slightly rougher than 0.1.6. Battle screens and the staff roll were not reached in the test.
- Tools: `tools/disasm.py` (EBOOT disassembly / call sites).

## 0.1.6 (local test build, 2026-10-09, not released)
- **Unreferenced dungeon tables translated.** The game shows tables no script names (e.g. NC02/MainEventMess0261, "There's something here!!"), so "unreferenced = unused" was wrong. 13 such tables that decode cleanly are now scope units (707 rows: 521 from translation memory in `extra_007`, 186 translated in `extra_008`-`010`). The remaining unreferenced tables are encoded against older font builds (garbled kanji even in Japanese) and stay untouched; the NC06/NC07 copies of MainEventMess05xx are unused older drafts (scripts load the NC05 copies). 57,473 rows written.
- **In-engine opening narration in English** (`Graph/Adv/eff/999` OP_moji00-02: "Suddenly lost in a mysterious world...", "Despair Strikes"). The `opening.pmf` movie has only English credits and the bilingual logo, so it is unchanged.
- **Texture labels heavier and larger.** `tex_edit.py` now draws supersampled text with an extra 0.4 px stroke by default (closer to the original 2 px pixel font) and fills each box; new options `weight`, `glow`, `condense`, and spec-level `exact` for same-named textures with different content.
- Camp menu: first words of split rows (Skill|Use, Skill|Tree, Chip|...) left-aligned so rows line up.
- New texture specs (96 copies relabelled, was 81): tutorial screenshots (14 pages in `Graph/Adv/eff/550`-`560`), battle INFO stat labels (Phys./Rng. + ATK/DEF halves), Game Over, save slot, camp banner/owned counter, Ride Dungeon intro panel.
- `tools/gtx_rects.py` lists the GFUV sprite rectangles of any texture page.

## 0.1.5 (local test build, 2026-10-09, not released)
- The 536 last entries uncovered by the 0.1.4 fix are translated (427 dialogue rows in `extra`, 109 system rows in `extrasys`); all pass `check_en.py`. 56,467 rows written.

## 0.1.4 (local test build, 2026-10-09, not released)
- **Freeze fix.** Every MTBL message table holds one more entry than its header counts (slot n). The parser stopped at the count, so 647 tables lost their last entry on rebuild, and the engine then read string bytes as that entry's offset and hung (first seen after Zero's thought in the opening dungeon scene). `mbb.entry_total` now reads the extra slot, and `mbb_write` keeps it while writing the original header count; all 1,380 tables round-trip with identical strings.
- The 536 last lines this uncovered are being translated (passes `extra` / `extrasys`); until then they show their original Japanese.

## 0.1.3 (local test build, 2026-10-09, not released)
- **UI textures in English.** `tools/tex_edit.py` relabels baked-in Japanese from per-page specs in `work/ui/tex/` (41 specs, 81 texture copies across the archive and its packs): base, camp, options, chip database and shared menus; equipment and stat labels; battle commands, Ride battle and result names; area-name strips, map labels and Cube start cards; minigames; Ride setup; the boot-time anti-piracy notice. Box positions come from the game's own sprite maps (`.gtx` GFUV) where available. The encoder round-trips every page format byte-exactly (5551, 4444, 8888, 4-bit and 8-bit paletted).
- Known texture issues are listed in `docs/review_queue.md` (00/W sprite overlap in the camp menu, split labels, abbreviations).

## 0.1.2 (local test build, 2026-10-09, not released)
- Fix: `Graph/STARTUP_pk.cmp` carries its own Font14/Font10; the GenEi fonts are now injected there too (0.1.1 only replaced the top-level copies, so the boot pack could still load the old glyphs with the new trims).
- Proofreading fixes for story 001-018 included.
- Survey of the remaining Japanese: no in-use text table is left (the NC04 loose copies and OP 0801-0805/1100 are unused drafts or old-font copies; see review queue). The remaining Japanese is baked into UI textures (`tools/tex_render.py` renders them).

## 0.1.1 (local test build, 2026-10-09, not released)
- **EBOOT decrypted** without an external dump: `tools/eboot_decrypt.py` ports PPSSPP's PRX type-2 path (tag 0xD91613F0, KIRK CMD7 code 0x5D + CMD1) and checks the header SHA-1. Output `work/source/EBOOT.elf` (plain ELF, 2,421,413 bytes).
- **VWF**: the engine is already proportional. Each font has a trim table (s8 left, s8 right per glyph); the text loop advances by cell - left - right. `tools/eboot_patch.py` writes trims for the 158 GenEi glyphs of Font14 and Font10 (left 0, right = cell - advance) and makes 0x0001 a narrow space (4 px instead of 14). The patched plain ELF replaces `PSP_GAME/SYSDIR/EBOOT.BIN`.
- GenEi Font14/Font10 textures injected (top-level `.tpc` and inside `.cmp`).
- **Staff roll translated**: role titles and company names in English (`work/translation/en/staffroll.json`); people's names keep their original glyphs. `tools/build_font.py staff` adds printable ASCII to `Font/FontStaff.tpc` (cells from 391; the staff font is 15x16 cells, 17 per row, code = cell + 1); `apply_en.py` encodes the rows and injects the font.
- `check_en.py`/`apply_en.py`: a row may use as many lines as its Japanese (choice menus, 3-line descriptions); 0 rows over box in all passes.
- Proofreading pass started: story 001-010 checked (12 small fixes; roar spellings unified).
- Not yet verified in an emulator. The native 4x Latin atlas (SRW MX approach) is not wired into the renderer yet.

## 0.1.0 (local test build, 2026-10-09, not released)
- First complete translation: story 194, system 97, quest 57 and talk 12 slices (28,659 rows). All pass `check_en.py` except 6 rows whose Japanese also uses more lines (choice menus, 3-line quest descriptions).
- `name_fix.py --apply` run once (176 rows unified).
- Built `work/output/ALLRES.PCK` (55,360 rows written across 1,084 table copies; no characters without a glyph) and `work/output/LostHeroes_EN_v0.1.0.iso`.
- Known limitation: the EBOOT VWF patch is not in yet (needs the decrypted `NPJH50647.BIN`), so English renders with the fixed-width font and long lines will overflow. The staff roll stays in Japanese.

## Unreleased

### 2026-10-09: Initial analysis
- Added extraction tools: `iso_extract.py`, `pck_extract.py`, `walk_assets.py` (recursive 2NBF/ZIP walker), `mbb.py` (TBB1/MTBL parser), `font_render.py`, `count_text.py`.
- Worked out the text encoding (glyph index + 1) and the font layout (14×16 cells, 18 per row, 4bpp swizzled).
- Counted translatable text. See `docs/text_inventory.md`.

### 2026-10-09: Font groundwork for VWF
- Font cell geometry confirmed: Font14 = 14×16 cells, 18×32 per page, 4 pages (2,304 glyphs = codes up to 0x900); Font10 = 10×10 cells, 25×51 per page, 2 pages.
- Added `tools/build_font.py`: renders GenEi LateGo P v2 (SIL OFL 1.1) at 4× and box-filters it down into the native cells (16-level AA, per-font gamma/emboldening), re-swizzles into the original `.tpc`, and writes per-code advance widths (`*.widths.json`) for the VWF routine.
- Added `tools/preview_vwf.py` (fixed-advance vs VWF comparison).
- English text will use the full ASCII glyph block: space = 0x0001, `!`..`~` = 0x00EA..0x0147.
- Output in `work/output/font/` (not yet injected; waits for the EBOOT VWF patch).
- OFL license copied to `docs/licenses/GenEiLatin-OFL-1.1.txt`; it must ship with any release.

### 2026-10-09: Native 4x Latin atlas (replaces "supersampled only")
- My earlier claim that a 4x font can't run natively was wrong. It only holds for scaling the whole 2,304-glyph atlas. Following SRW MX (`tools/native_font4x.py`, docs/vwf.md there), English gets a separate Latin-only 4x atlas, and the renderer samples it with 4x UVs at the original on-screen size. No texture replacement.
- `tools/build_font.py` now also writes `<font>.native4x.{bin,png,json}`. Font14: 94 glyphs, 56×64 cells, 9 per row, 512×704 sheet (each row is a legal 512×64 strip). Font10: 40×40 cells, 12 per row, 512×320.
- The 4x ink is the exact canvas each 1x glyph is box-filtered from, so the 1x VWF widths stay valid.
- The renderer patch still needs the decrypted EBOOT (`NPJH50647.BIN` from PPSSPP).

### 2026-10-09: Text fully decoded; translation pipeline
- **Kanji table**: all 1,651 Font14 kanji (0x016C-0x07DE, plus staff-name glyphs to 0x082F) transcribed from glyph sheets (`tools/glyph_sheet.py`) and verified against context. Corrections from context are listed in `work/source/font/kanji_sheets.txt`. Symbol fixes: 0x0149 is the sentence-ending `!`, and 0x0147/0x0148 are the Japanese comma and full stop. `tools/charmap.py` builds `work/glossary/charmap.json`; `tools/decode_text.py` exports every table.
- **Old font encodings**: some tables were written against earlier font builds (kanji permuted). Stale copies are excluded. The 8 live NC02 tables (0208/0209/0211/0223/0224/0228/0246/0247) are remapped by `tools/legacy_map.py` (twin-string votes + n-gram solver + context overrides via `tools/legacy_fix.py`). A few kanji there are still uncertain, and translators are warned.
- **Scope** (`tools/script_refs.py`, `tools/table_status.py`, `tools/scope.py`): dungeon event tables are looked up by file name, so they count as live only if a script loads that name; each name is translated once and written to every copy. 617 units, 28,659 rows: story 15,520 / quest 4,536 / town talk 898 / system 7,705.
- Fixed a `logical_path` bug: 38 DungeonMess tables had collapsed into one entry. Total strings: 33,934.
- **Speakers**: `tools/lua51.py` (Lua 5.1 bytecode reader) + `tools/speakers.py` replay the event scripts. 7,595 lines are attributed and 905 are narration. Names come from CharacterName.mbb block 3 (id+1).
- **Glossary** `work/glossary/names.json`: 193 speakers + key terms, with gender and voice notes. リジェス = "Regis" (Gematsu, LH2 coverage).
- Translation tooling: `tools/make_slices.py` (80-row slices), `docs/translator_brief.md`, `tools/check_en.py` (keys/tags/VWF box fit), `tools/strip_jp.py`, `.gitignore`.
- Latin slot table moved to `tools/latin.py`: `}` 0x0145, `~` 0x0146, `|` 0x014E, `"` fills the blank 0x00EB. `、` (0x0147) is no longer overwritten.

### 2026-10-09: Translation underway; tooling fixes
- Story translation running: 80-row slices, one translator agent each, brief in `docs/translator_task.md`. Slices 001–036 are done and pass `check_en.py`.
- Speaker extraction fixes (`tools/speakers.py`): each script's own `TextIdOffset` (0110: −7), plus a monotonic shift across empty table entries (0205: lines after empty entry 36 shift by +2). 89 tables were affected, so slices 001–025 must be re-checked against the corrected labels in proofreading.
- Kanji fixes found from context (round 2): 0x419 愛, 0x507 慣, 0x5DA 讐, 0x645 噛, 0x6E3 掻, 0x707 昂, 0x709 懺, 0x737 厭, 0x752 冑, 0x787 暑, 0x7D1 剤. Slices 001–035 were translated before this fix, so proofreading must check rows with these characters.
- Insertion side: `tools/mbb_write.py` (table writer; all 1,380 tables round-trip with identical strings), `tools/repack.py` (nested NBF/ZIP rebuild, streamed outer archive; a no-change rebuild is byte-identical) and `tools/apply_en.py` (encode, wrap, write every copy).
- Glossary grew to ~90 terms plus style rules (honorifics, sound effects, Den-O belt calls, catchphrases). Open questions are in `docs/review_queue.md`.
- Known old-encoding live tables beyond the 8 remapped ones: 0218, 0225, 0231, 0240 (isolated kanji). Translators reconstructed these from clean twins.

### 2026-10-09: End-to-end build pipeline verified (unversioned test)
- `tools/iso_patch.py`: replaces a file in the UMD image, in place if it fits, otherwise appended at the end, updating its directory record and the PVD volume size.
- `tools/apply_en.py`: symbols outside ASCII (♪ ～ ※ ① ...) reuse the original font glyphs.
- Pipeline run on 75 finished story slices: 159 tables, 356 copies, 13,209 rows → `work/output/ALLRES.PCK` (+350 KB, appended at LBA 559408) → `work/output/LostHeroes_EN_test.iso`. Reading back MainEventMess0101 from the patched archive gives the English text.
- Not a release candidate: the VWF/EBOOT patch is still pending (needs the decrypted EBOOT dump), so Latin text would render at the fixed 14 px advance. No version number assigned yet.

### 2026-10-09: Story translation, first half done
- Story slices 001–097 of 194 translated (7,760 rows). All pass `check_en.py` apart from a handful of rows flagged over the box.
- Speaker extraction: computed-index lines (`TextIdOffset+a+k`, party-leader variants) are now labelled `?party`. Speakers are merged by table base name. Speaker id #276 is Alien Kool. Translators take leader-variant order from each script's `Pt_Chara_Check` sequence.
- Glossary grew to about 150 terms plus style rules: roars, honorifics ("Lord X", "Brother X"), venue cards, prompts.
- `tools/name_fix.py`: glossary name sweep (dry run until proofreading is done). `tools/iso_patch.py`: path handling fixed for Git Bash.
- Paused at 88% of the 5-hour usage window. Resume with story_098.

### 2026-10-09: System pass started
- System/UI slices now carry per-row budgets (`max_px` = widest Japanese line in the table × 14 px, `max_lines`), and `check_en.py` enforces them. The brief is `docs/translator_task_system.md`; these slices run on Sonnet (about 1/3 of the quota cost per slice).
- `tools/tm_fill.py`: translation memory. 13 system slices (dungeon-message tables, all exact repeats) were filled automatically.
- System slices 001–040 of 97 are done. The glossary gained a `ui` section (stats, statuses, facilities, features).
- Paused at 93% of the 5-hour window. Next: story_098+, system_029+, quest, talk.

### 2026-10-09: Story 098–122, system 041–066
- Story slices up to 122 of 194 and system slices up to 066 of 97 are translated.
- Enemy battle tables (`Table/Enemy/SkillMessage`, `SystemMessage`, `EnemyInfo`, `SkillName`) use inline ASCII markup (`<act_ch>`, `<tag_chr>`, `<hit_damage>`, `<get_Recover>`, `<use_skill>`, `<enemy_name>`, `<party_name>`, `<itemFull>`, `<br>`) stored as raw u16 ASCII. It was mis-decoded as kana. The 74 affected rows were rewritten to keep the markup, and `apply_en.py` now writes it back as raw ASCII (with `<br>` as the line break in these rows).
- `apply_en.py` now wraps system rows with each row's own `max_px`/`max_lines` instead of the generic box.
- Glossary: new `ui`/`terms` entries (Status Res Up, Element Res Up, Blind, monster-drop materials, Innovator, Terminal Unit, Veda...). `name_fix.py` gained rules for Status/Elemental Resist Up and Cure Dark.

### 2026-10-09: System pass complete
- All 97 system/UI slices (7,705 rows) are translated and pass `check_en.py` (0 over box). The only untranslated rows are the 159 staff-roll rows, which stay in Japanese by decision (own sequential font `FontStaff.tpc`; see review queue).
- `tools/consistency.py`: reports identical Japanese with differing English across tables, for the proofreading pass.
- `tools/name_fix.py`: more unification rules (GN Drive Tau, Planate Defenser, Tri-Gar Shot, Defiant Stance, Finalfusion, Disolder, Crit Normal, Ultra Eye Spot, Revolcrash, Monsload).
- The full-width `＜act_chr＞`/`＜home_btn＞` placeholders in player tables are kept as full-width glyphs, exactly as the original text has them.
- Quest pass started.

### 2026-10-09: Story 123–171, quest 001–004
- Story slices up to 171 of 194 and quest slices 001–004 of 57 are translated; all pass `check_en.py`.
- Translators now verify speakers against the event scripts (`MessWinSet TextIdOffset+N` plays entry N+1; leader-check order can change between blocks in one script). Extracted labels are often one or more rows late. The labels are metadata only and not part of the build.
- Glossary: roars (Birdon, Gundam Head, Geronimon...), Monsload, Memory Memory, Volcano Monster Bird, Monster Chief.
- `apply_en.py`: the full-width padding after a tag is restored for any control tag (≥ 0x8000), not only 0x80xx.
- Paused at 89% of the 5-hour window; resume after 01:50 UTC with story_172, quest_005, talk_001.

### 2026-10-09: Story and talk passes complete, quest pass nearly complete
- Story: all 194 slices (15,520 rows) translated. Talk: all 12 slices translated.
- Quest: `Table/Event/Quest/QuestEventMessNNN.mbb` turned out to be copies of `Event/Quest/DG_QUESTNNN_pk` (same row ids). Added `tools/quest_copy_fill.py`, which fills the copy rows from their translated twin (falling back to translation memory); 24 slices (030–052, 055) were filled automatically instead of retranslated.
- `tools/talkspk.py <Room>`: base-talk speaker mapping from the Talk*.bla scripts (the extracted labels were mostly wrong or missing).
- Style decisions: アイス = "ice pop" (Ankh's ice candy; quest title "The Ultimate Ice Pop"); 全宇宙翻訳機 = "Pan-Space Interpreter", and speech through it is ALL CAPS; Pigmon's "ppi" = "-pi" suffix; Alien Baltan's laugh = "Fo, fo, fo..."; Gundam Wing's shield = "Planet Defensor" (official). All are enforced by `tools/name_fix.py` rules (dry run until proofreading).
- Known original-game script quirks (a message index past the table end) are logged in the review queue.
