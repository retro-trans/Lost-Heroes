# Texture task: relabel one UI texture page in English

Fan translation of the PSP game **Lost Heroes**. Project root: `E:\Projects\Lost Heroes`. Your prompt names a texture (`tpc` path) and one or more page names. Japanese labels are baked into these pages; replace them with English.

How it works: `tools/tex_edit.py` reads a spec `work/ui/tex/<spec>.json` listing label boxes on a page. It wipes each box and draws English with GenEi LateGo, then re-encodes the page byte-exactly and injects every copy. Read `docs/texture_survey.md`, the spec format at the top of `tools/tex_edit.py`, and the finished example `work/ui/tex/base_equip_status.json`.

1. Render the page: `python tools/tex_render.py work/source/iso/PSP_GAME/USRDIR/ALLRES.PCK <your scratch dir> <tpc path>`. Then make a zoomed view with coordinates: `python tools/tex_grid.py <page png> <out png> <zoom> [x0 y0 x1 y1]`. Crop large pages into regions and view each one.
2. Find every Japanese label, i.e. a word or a run of glyphs that the game shows as one unit. Its box is the area the original ink occupies. Assume the game samples that exact rectangle, so English must stay inside it. Leave Latin labels, icons and frames untouched.
3. Choose the English:
   - Use the glossary `work/glossary/names.json` (`ui`, `terms`) and the wording already used in the translated menus (`work/translation/en/system/*.en.json`), so that a menu label on screen matches the text the game prints.
   - Keep labels short: use abbreviations like the existing ones (P.ATK, R.DEF, SPD, Lv, HP, x2).
   - Area and Cube names follow the glossary (e.g. "Begins Cube", "Desert Cube", "Shocker Cube").
4. Write `work/ui/tex/<tpc base>__<page base>.json` with `defaults` (one font size and colour for consistent labels), `clear` rectangles for leftover strokes, and the boxes. Text colour should match the original label (sample it from the render).
5. Preview with `python tools/tex_edit.py preview work/source/iso/PSP_GAME/USRDIR/ALLRES.PCK <spec> <out.png>` and view the result. Iterate until:
   - no Japanese stroke is left,
   - every label is readable at 1x,
   - nothing spills outside its box.
Extra tools and options (2026-10-09):
- `python tools/gtx_rects.py <ALLRES.PCK> <path substring> [page substring]` lists the sprite rectangles the game samples from each page (GFUV in the `.gtx`). Use them as label boxes: English must stay inside the sprite rect, and a sprite may be one piece of a row that the game puts together (e.g. "Skill" + "Use").
- Text is drawn bold by default (`weight` 0.4 = extra stroke in px), sized to fill the box. Avoid setting `size` unless labels must match.
- Options: `glow` [r,g,b] + `glow_radius` (soft halo, title cards); `stroke` + `stroke_width` (hard outline); `bg` (opaque fill); `condense` (minimum horizontal squeeze, default 0.75).
- When the first word of a multi-sprite row sits in a left-aligned menu, left-align it. Right-align only the first half of a word split across sprites (Data|base).
- Same-named textures in different packs can hold different pictures (e.g. `Graph/Adv/eff/550/ADV_EFF.tpc` ... `560`). For those, set `"exact": true` and the full leaf path in `tpc` (e.g. `"tpc": "Graph/Adv/eff/550/ADV_EFF.tpc"`), one spec per path.
- Pages with no Japanese: skip them and list nothing for them.

6. Do not edit tools, other specs or translation files. If a label is impossible to fit or its meaning is unclear, keep the best effort and report it.

Final reply: **at most 8 lines**. Give the spec file(s) written, labels replaced vs found, any label you could not fit or were unsure of, and English terms you chose that are not in the glossary.
