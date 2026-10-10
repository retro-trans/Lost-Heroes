# Lost Heroes — English patch

Fan translation of the PSP game *Lost Heroes* (NPJH50647, v1.01) into English. The patch will be distributed as
an xdelta file that you apply to your own disc image. This repository contains translation text, glossaries,
texture-label specs and tools; disc images, extracted game data, Japanese source text and screenshots are excluded.

## Status

Early public builds; further proofreading and playtesting are needed. The latest release has:

- all story, quest, base-talk and system text in English, including the staff roll
- a variable-width Latin font, plus a native 4x Latin font that is sharp at higher emulator resolutions
- English UI textures (menus, battle labels, tutorial pictures, opening narration)

See [the changelog](docs/CHANGELOG.md) for every build and [the review queue](docs/review_queue.md) for known issues.

## Applying the patch

Use [Retro Trans](https://github.com/retro-trans/retro-trans-tools/releases/latest) for automatic patching: click
**Refresh catalog**, open **Automatic**, select your original Japanese ISO, leave **Target** on **Latest** and choose
a new output filename. The app downloads the matching patch and verifies the result.

For manual patching, download `LostHeroes-English-<version>.xdelta` from
[Releases](https://github.com/retro-trans/Lost-Heroes/releases/latest) and apply it to your own dump:

- `Lost Heroes (Japan) (v1.01).iso`, 1,145,667,584 bytes
- SHA-256 `8c4b3f19aedc5d04b7df31ee1ecfa3257515af7dd958bca3f72fe469b5defbc9`

```bash
xdelta3 -d -s "Lost Heroes (Japan) (v1.01).iso" LostHeroes-English-<version>.xdelta "Lost Heroes English <version>.iso"
```

Compare the output SHA-256 with the release notes, then play it in PPSSPP. Boot it fresh and load a normal save;
save states keep the old text in memory.

## Build it yourself

Put your own dump at the project root as `Lost Heroes (Japan) (v1.01).iso` and follow
[the tool guide](docs/TOOLS.md). In short: extract the disc, build the fonts (`build_font.py`, `font4x.py`), patch
the EBOOT (`eboot_decrypt.py`, `eboot_patch.py`), write the archive (`apply_en.py`) and patch the ISO
(`iso_patch.py`). Local builds go under `work/output/`.

## Repository layout

- `docs/` — changelog, tool guide, translator briefs, texture survey and review queue
- `tools/` — extraction, text encoding, font, EBOOT, texture and disc tools
- `work/glossary/` — names and terms every translation follows (main source: akurasu.net), plus the font map
- `work/translation/en/` — the English text: translation slices keyed by table and row ID, and the staff roll
- `work/ui/tex/` — texture-label specs (boxes, multi-sprite composites) applied by `tools/tex_edit.py`

Read [the translation rules](BASE_RULES.md) and [the contribution guide](CONTRIBUTING.md) before editing.

## Credits

| Role | Contributors |
| --- | --- |
| Translation and tools | retro-trans contributors |

Latin glyphs use GenEi Latin by o_tamon ([SIL OFL 1.1](docs/licenses/GenEiLatin-OFL-1.1.txt)).

## License

Translation text and tools: [MIT](LICENSE), except `tools/eboot_decrypt.py`, a port of PPSSPP code
licensed [GPL-2.0-or-later](docs/licenses/GPL-2.0.txt). The game and its assets belong to Bandai Namco Games / Banpresto and
the respective rights holders of Kamen Rider, Ultraman and Gundam. Bring your own disc image; this license does not
cover the game or its assets.
