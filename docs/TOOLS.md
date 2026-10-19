# Tools

All tools are Python 3 scripts run from the project root (`python tools/<name>.py ...`); each one documents its
arguments in its own docstring. Requirements: Pillow, numpy, capstone and keystone (EBOOT work), websockets
(PPSSPP debugger tools). Texture and font tools need the GenEi Latin font in `incoming/genei-latin/` (OFL,
see `docs/licenses/`).

## Build order

1. `extract`: `iso_extract.py`, then `decode_text.py` / `scope.py` (local, writes `work/source/`, never committed)
2. Fonts: `build_font.py` (1x Latin glyphs + VWF widths), then `font4x.py` (native 4x Latin pages)
3. EBOOT: `eboot_decrypt.py`, then `eboot_patch.py` (VWF trims + 4x glyph hook from `eboot_font4x.py`)
4. Archive: `apply_en.py <ALLRES.PCK> work/output/ALLRES.PCK` (text, staff roll, fonts, UI textures)
5. Disc: `iso_patch.py` for `PSP_GAME/USRDIR/ALLRES.PCK`, then `PSP_GAME/SYSDIR/EBOOT.BIN` in place

## Reference

| Tool | Purpose |
| --- | --- |
| `apply_en.py` | Encode translated English and build a patched ALLRES.PCK. |
| `boottest.py` | Boot an ISO in the isolated portable PPSSPP (work/build/ppsspp_test) and screenshot it. |
| `build_font.py` | Replace the Latin glyphs in a game font (.tpc) with GenEi Latin, rendered at 4x and box-filtered down to the native cell (supersampled anti-aliasing), and write the per-code advance widths a VWF routine will need. |
| `charmap.py` | Build and use the glyph-code <-> character table. |
| `check_en.py` | Validate translated slices and measure English against the text boxes. |
| `consistency.py` | Cross-table consistency: identical Japanese translated differently. |
| `count_text.py` | Count translatable Japanese text in every MTBL message table. |
| `decode_text.py` | Decode every unique MTBL message table to JSON working files. |
| `disasm.py` | Disassemble the decrypted EBOOT (relocatable PRX, file offset = address + 0xC0). |
| `eboot_decrypt.py` | Decrypt the game's EBOOT.BIN (~PSP, tag 0xD91613F0, PRX type 2) to a plain ELF. |
| `eboot_font4x.py` | Hook the glyph draw to use the native 4x Latin pages (tools/font4x.py). |
| `eboot_patch.py` | Variable-width font for Lost Heroes: patch the glyph trim tables in the EBOOT. |
| `font4x.py` | Native 4x Latin glyphs for Font14 / Font10 / FontStaff (SRW MX approach, adapted). |
| `font_render.py` | Render the game font pages (Font/*.tpc) to PNG for inspection. |
| `glyph_sheet.py` | Contact sheet of game glyphs (Font14) with their code and, optionally, the mapped character rendered beside each for visual verification. |
| `gtx_rects.py` | List the sprite rectangles (GFUV) the game samples from a texture page. |
| `iso_extract.py` | List or extract files from a PSP UMD ISO (plain ISO9660, 2048-byte sectors). |
| `iso_patch.py` | Replace one file inside the UMD ISO image. |
| `latin.py` | Shared English character -> game code table (font slots for Latin text). |
| `legacy_fix.py` | Turn context corrections for the live legacy tables into old-code overrides. |
| `legacy_map.py` | Recover the older kanji glyph order used by a few stale message tables. |
| `lua51.py` | Minimal Lua 5.1 bytecode reader for the event scripts (.bla). |
| `make_slices.py` | Cut in-scope rows into translation slices (80 rows each, BASE_RULES). |
| `mbb.py` | Parse TBB1 containers and their MTBL message tables. |
| `mbb_write.py` | Rebuild TBB1/MTBL message tables with new strings. |
| `name_fix.py` | Glossary name sweep over finished English (BASE_RULES: run AFTER agent fixes). |
| `ocr_glyphs.py` | OCR the game font atlas (Font14) by template matching against Japanese system fonts, producing candidate characters per glyph code. |
| `pck_extract.py` | List or extract the "2NBF" ALLRES.PCK archive from USRDIR. |
| `ppsspp_dbg.py` | Minimal client for the PPSSPP remote debugger (WebSocket, JSON events). |
| `preview_vwf.py` | Typeset sample English with a built font page + width table, comparing the game's fixed advance with VWF. Output is zoomed for inspection. |
| `quest_copy_fill.py` | Fill QuestEventMessNNN rows from the matching DG_QUESTNNN_pk translation. |
| `repack.py` | Write changed files back into ALLRES.PCK through nested 2NBF/ZIP layers. |
| `scope.py` | Decide which message tables need translating and pick a canonical copy. |
| `script_refs.py` | List message tables referenced by event scripts (.bla, compiled Lua). |
| `speakers.py` | Attach speakers to event dialogue rows by replaying the event scripts. |
| `sprite_match.py` | Find where a texture page's sprites are drawn on a game screenshot (normalised correlation of each sprite's alpha mask; `--all` for every position, `--dark` for dark-on-light labels). Used to lay out composites without a sprite-draw log. |
| `sprite_log.py` | Log sprite draws (texture object, sprite index, x, y) via a PPSSPP logging breakpoint on the sprite routine 0x13c42c. Module base 0x08804000 (PPSSPP). |
| `strip_jp.py` | Remove Japanese script from committed translation files (AGENTS.md rule). |
| `table_status.py` | Classify every message table: packed / script-referenced / scrambled. |
| `talkspk.py` |  |
| `tex_edit.py` | Relabel UI textures: replace Japanese labels baked into GFXT pages with English. |
| `tex_grid.py` | Zoomed view of a texture PNG with a pixel grid and coordinates (for writing tex_edit specs). |
| `tex_render.py` | Render GFPT/GFXT textures (.tpc) to PNG for inspection. |
| `tm_fill.py` | Translation memory: fill slices whose rows are all exact repeats. |
| `walk_assets.py` | Recursively walk ALLRES.PCK, unpacking nested .cmp (ZIP) and .pck (2NBF) containers, and yield every leaf file with its virtual path. |
