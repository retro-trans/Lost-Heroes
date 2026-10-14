English fan translation of **Lost Heroes** for PSP (**NPJH50647**, v1.01).

### Apply

**Recommended:** Use the latest [Retro Trans](https://github.com/retro-trans/retro-trans-tools) app. Click **Refresh catalog**, open **Automatic**, select your original Japanese ISO or the published English v0.1.9 ISO, choose **0.1.12** (or **Latest**), and select a new output filename. The app downloads the matching patch and verifies the result.

**Manual patching:** [DeltaPatcher](https://github.com/marco-calautti/DeltaPatcher) and [xdelta3](https://github.com/jmacd/xdelta) accept the same assets:

| Your source image | Patch |
| --- | --- |
| Original Japanese ISO | `LostHeroes-English-0.1.12.xdelta` |
| Published English v0.1.9 ISO | `LostHeroes-English-0.1.9-to-0.1.12.xdelta` |

```text
xdelta3 -d -s "Lost Heroes (Japan) (v1.01).iso" LostHeroes-English-0.1.12.xdelta "Lost Heroes English 0.1.12.iso"
```

To upgrade from the published v0.1.9 image:

```text
xdelta3 -d -s "Lost Heroes English 0.1.9.iso" LostHeroes-English-0.1.9-to-0.1.12.xdelta "Lost Heroes English 0.1.12.iso"
```

Both patches produce the same release image. The upgrade patch requires the exact published v0.1.9 image (SHA-256 `22f0393ccc7583771710f0b51d15e43903890f8c2646a80bce9f36573a3ec52e`); use the original disc if yours does not match.

Original Japanese ISO: 1,145,667,584 bytes; SHA-256 `8c4b3f19aedc5d04b7df31ee1ecfa3257515af7dd958bca3f72fe469b5defbc9`.

Release output: 1,598,535,680 bytes; SHA-256 `f1770b3fdc2620522b85a6c6636d3e8d3dd94bfee1f01ae3cc4ef054a6dbe5e4`.

The exact source, output and patch hashes are in `BUILD-MANIFEST.json`. `VALIDATION.json` records the patch round trips, and `SHA256SUMS.txt` covers the downloads. Manual patchers require the unpacked ISO.

### What changed since v0.1.9

* **Battle name plate:** every hero was shown as "Rider 1". The name table carries a marker the game relies on, and the rebuild had replaced it. Each hero now shows their own name.
* **Battle messages:** "Rider 1attacked!" lost its space because the game deletes the padding code after a name, and English used the same code for spaces. Spaces now use the font's own half-width space.
* **Battle screens:** the copies of the battle textures loaded from the battle packs are now relabelled too: INFO panel stats (Phys./Rng. ATK/DEF), result screen hero names, weakness and resistance labels.
* **Field messages:** 91 more lines in English, such as "Something's here!", the inscriptions on the crosses, locked doors and capsule contents. These single-message tables keep their one line in a slot the table header does not count, so they were missed before.
* **Menus:** Camp rows read Use Skill, Skill Tree, Equip Force and Check Quests with even spacing. The Base header reads BASE in the game's own big-initial style. Menu texture labels are drawn heavier.
* **Names:** Spider Man is now **Man Spider** and Bogal is now **Bogarl** (also Bogarl Monst).
* **Title screen:** shows the build version and `github.com/retro-trans` in the bottom right.

Retains all v0.1.9 content: story, quest, base and system text, staff roll, the variable-width and native 4x Latin fonts, and the translated textures. See the [changelog](https://github.com/retro-trans/Lost-Heroes/blob/main/docs/CHANGELOG.md).

### Release status

**This is an early build. Further proofreading and full in-game playtesting are needed.** File and patch verification shows that the intended data is included and that the patches reproduce the release image. It does not certify emulator or console behavior. In PPSSPP, the title screen, base and Camp menus, and a Begins Cube battle were checked; the battle name plate fix was confirmed live in that battle. The other battle and field-message fixes in this release are verified in the built files but have not yet been seen in game.

Known limitations:

* Some menu labels assembled from several images still read oddly: Chara Catalog, Force Data spacing, Main/Sub Quest tabs, Sound Test, Custom Track Sound and a condensed Depot label. The Gate Port header has a stray letter.
* The save-data details on the Load/Save screen (play time, "Save Data", hero names) are still Japanese. The katakana title logo is kept; it already carries "LOST HEROES".
* The 4x font is designed for emulators at 2x resolution or higher. At native 1x resolution, including real PSP hardware, English text is slightly rougher than a plain 1x font.
* Story text after the first chapters has not had a second proofreading pass.

**Boot the patched ISO fresh and load a normal save.** Save states keep the old text, fonts and textures in memory.

### How it was translated

This is a **machine translation**, produced with large language models and then reviewed and edited using scene context and a researched glossary. Names and terms follow [akurasu.net](https://akurasu.net) where it has an entry; project decisions are recorded in the repository. Sources keep review notes and open questions. Human proofreading and playtesting are welcome.

### Acknowledgements

* **GenEi Latin** by o_tamon, used for the English glyphs (SIL Open Font License 1.1).
* **PPSSPP**, whose PRX decryption code was ported for the EBOOT tools and whose debugger was used for testing.

### Source code

Translation text, glossaries and tools are available in the [project repository](https://github.com/retro-trans/Lost-Heroes). GitHub's source archives contain the repository snapshot at the release tag. Use the `.xdelta` assets to patch the game.

### Contribute

Bug reports, proofreading and playtesting are welcome at **[discord.gg/MssepShjmB](https://discord.gg/MssepShjmB)**.

No complete game images are included. Apply the patches to your own disc image.
