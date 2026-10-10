English fan translation of **Lost Heroes** for PSP (**NPJH50647**, v1.01). This is the first public build.

### Apply

**Recommended:** Use the latest [Retro Trans](https://github.com/retro-trans/retro-trans-tools) app. Click **Refresh catalog**, open **Automatic**, select your original Japanese ISO, choose **0.1.9** (or **Latest**), and select a new output filename. The app downloads the matching patch and verifies the result.

**Manual patching:** [DeltaPatcher](https://github.com/marco-calautti/DeltaPatcher) and [xdelta3](https://github.com/jmacd/xdelta) accept the same asset:

| Your source image | Patch |
| --- | --- |
| Original Japanese ISO | `LostHeroes-English-0.1.9.xdelta` |

```text
xdelta3 -d -s "Lost Heroes (Japan) (v1.01).iso" LostHeroes-English-0.1.9.xdelta "Lost Heroes English 0.1.9.iso"
```

Original Japanese ISO: 1,145,667,584 bytes; SHA-256 `8c4b3f19aedc5d04b7df31ee1ecfa3257515af7dd958bca3f72fe469b5defbc9`.

Release output: 1,598,521,344 bytes; SHA-256 `22f0393ccc7583771710f0b51d15e43903890f8c2646a80bce9f36573a3ec52e`.

The exact source, output and patch hashes are in `BUILD-MANIFEST.json`. `VALIDATION.json` records the patch round trip, and `SHA256SUMS.txt` covers the downloads. Manual patchers require the unpacked ISO.

### What's included

* **Text:** story events, quests, base conversations, tutorials and system text (menus, items, skills, Forces, chips, enemies, library) in English, 57,473 text rows in all. Includes dungeon events that the game loads without a script reference, such as Desert Cube's "There's something here!!".
* **Staff roll:** role titles and company names in English; personal names keep their original glyphs.
* **Font:** a variable-width Latin font, plus a native 4x Latin font patched into the EBOOT. At 2x or higher emulator resolution the English text stays sharp, with the same layout as at 1x.
* **Images:** English labels for base, camp, options, chip database and shared menus; stat, battle-command, Ride battle and result labels; area names and Cube cards; minigames; Game Over and save screens; tutorial screenshots; the in-engine opening narration.
* **Camp menu:** Use Skill, Skill Tree, Equip Force and Check Quests, rebuilt from the game's multi-sprite rows.

See the [changelog](https://github.com/retro-trans/Lost-Heroes/blob/main/docs/CHANGELOG.md).

### Release status

**This is an early build. Further proofreading and full in-game playtesting are needed.** File and patch verification shows that the intended data is included and that the patch reproduces the release image. It does not certify emulator or console behavior. Testing so far used PPSSPP: boot, title, opening dialogue, dungeon, base and Camp menus.

Known limitations:

* A few menu labels assembled from several images still read oddly: Chara Catalog, Force Data spacing, Main/Sub Quest tabs, Sound Test, Custom Track Sound and a condensed Depot label.
* The save-data details on the Load/Save screen (play time, "Save Data", hero names) are still Japanese. The katakana title logo is kept; it already carries "LOST HEROES".
* The 4x font is designed for emulators at 2x resolution or higher. At native 1x resolution, including real PSP hardware, English text is slightly rougher than a plain 1x font. Battle screens and the staff roll have not been checked with it.
* Story text after the first chapters has not had a second proofreading pass.

**Boot the patched ISO fresh and load a normal save.** Save states keep the old text, fonts and textures in memory.

### How it was translated

This is a **machine translation**, produced with large language models and then reviewed and edited using scene context and a researched glossary. Names and terms follow [akurasu.net](https://akurasu.net) where it has an entry. Sources keep review notes and open questions. Human proofreading and playtesting are welcome.

### Acknowledgements

* **GenEi Latin** by o_tamon, used for the English glyphs (SIL Open Font License 1.1).
* **PPSSPP**, whose PRX decryption code was ported for the EBOOT tools and whose debugger was used for testing.

### Source code

Translation text, glossaries and tools are available in the [project repository](https://github.com/retro-trans/Lost-Heroes). GitHub's source archives contain the repository snapshot at the release tag. Use the `.xdelta` asset to patch the game.

### Contribute

Bug reports, proofreading and playtesting are welcome at **[discord.gg/MssepShjmB](https://discord.gg/MssepShjmB)**.

No complete game images are included. Apply the patch to your own disc image.
