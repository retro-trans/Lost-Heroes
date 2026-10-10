# Contributing

Keep translation files under `work/translation/<language-code>/`, shared terminology under `work/glossary/`, and
texture-label specs under `work/ui/tex/`. Preserve row keys, `{XXXX}` control-code tags and glossary terms. Read
adjacent lines and the [translation rules](BASE_RULES.md); record uncertainty in `docs/review_queue.md` instead of
inventing context.

Never commit Japanese script text (dialogue, descriptions, source lines). Names and UI terms in Japanese are
allowed in the glossary and specs. Run `python tools/strip_jp.py` before committing; slices, extracted text and
reports that pair Japanese with English stay local (see `.gitignore`).

Check every changed slice with `python tools/check_en.py <pass> <slice>` (keys, tags, no Japanese, fits the text
box). For a texture, preview it with `python tools/tex_edit.py preview <ALLRES.PCK> <spec> <out.png>`.

Include the table/row keys or texture spec, the changed English, and what you checked in game. Add an entry to
`docs/CHANGELOG.md` and give local test builds an unused `0.x.y` version. Test a fresh boot and a normal save in
PPSSPP; save states can retain old resources. Do not commit disc data, memory dumps, saves, screenshots or
local builds.
