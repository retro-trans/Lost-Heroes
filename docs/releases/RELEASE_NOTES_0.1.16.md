English fan translation of **Lost Heroes** for PSP (**NPJH50647**, v1.01).

### Apply

**Recommended:** Use the latest [Retro Trans](https://github.com/retro-trans/retro-trans-tools) app. Click **Refresh catalog**, open **Automatic**, select your original Japanese ISO or the published English v0.1.12 ISO, choose **0.1.16** (or **Latest**), and select a new output filename. The app downloads the matching patch and verifies the result.

**Manual patching:** [DeltaPatcher](https://github.com/marco-calautti/DeltaPatcher) and [xdelta3](https://github.com/jmacd/xdelta) accept the same assets:

| Your source image | Patch |
| --- | --- |
| Original Japanese ISO | `LostHeroes-English-0.1.16.xdelta` |
| Published English v0.1.12 ISO | `LostHeroes-English-0.1.12-to-0.1.16.xdelta` |

```text
xdelta3 -d -s "Lost Heroes (Japan) (v1.01).iso" LostHeroes-English-0.1.16.xdelta "Lost Heroes English 0.1.16.iso"
```

To upgrade from the published v0.1.12 image:

```text
xdelta3 -d -s "Lost Heroes English 0.1.12.iso" LostHeroes-English-0.1.12-to-0.1.16.xdelta "Lost Heroes English 0.1.16.iso"
```

Both patches produce the same release image. The upgrade patch requires the exact published v0.1.12 image (SHA-256 `f1770b3fdc2620522b85a6c6636d3e8d3dd94bfee1f01ae3cc4ef054a6dbe5e4`); use the original disc if yours does not match.

Original Japanese ISO: 1,145,667,584 bytes; SHA-256 `8c4b3f19aedc5d04b7df31ee1ecfa3257515af7dd958bca3f72fe469b5defbc9`.

Release output: 1,598,537,728 bytes; SHA-256 `313783b8e216b183e60587f08af65b5e2fbea867c5789b3b29a8f1aa14f45b33`.

The exact source, output and patch hashes are in `BUILD-MANIFEST.json`. `VALIDATION.json` records the patch round trips, and `SHA256SUMS.txt` covers the downloads. Manual patchers require the unpacked ISO.

### What changed since v0.1.12

* **Battle banner text no longer cut off:** the banner for skill help and battle messages holds 63 characters once names and numbers are filled in, so lines such as "...for a set number of tu" and "...main cannon charge reset to" lost their ends. 22 lines were shortened, and every banner line is now checked with names and numbers at their longest.
* **Missing last lines:** 44 lines that stayed Japanese are now in English, including "Ride Machine took ... damage!", the last line of several scenes, Base info lines and two Ride Machine skill helps.
* **Ride "Armor" label:** the first letter was cut off in both the Ride battle and the Ride Dungeon displays.
* **Save data details in English:** the PSP's Load/Save screen shows "Lost Heroes", "Save Data" or "Suspend Data", the area, play time and hero level in English, as do the install data details. Existing saves keep their Japanese details until saved again.
* **Title screen copyright line** is in English.

Retains all v0.1.12 content: story, quest, base and system text, battle and field messages, staff roll, the variable-width and native 4x Latin fonts, and the translated textures. See the [changelog](https://github.com/retro-trans/Lost-Heroes/blob/main/docs/CHANGELOG.md).

### Release status

**This is an early build. Further proofreading and full in-game playtesting are needed.** File and patch verification shows that the intended data is included and that the patches reproduce the release image. It does not certify emulator or console behavior. In PPSSPP, the save details on the Load/Save screen and the Ride Dungeon "Armor" label were checked. The shortened banner lines and the newly translated last lines are verified in the built files but have not all been seen in game.

Known limitations:

* Some menu labels assembled from several images still read oddly: Chara Catalog, Force Data spacing, Main/Sub Quest tabs, Sound Test, Custom Track Sound and a condensed Depot label. The Gate Port header has a stray letter.
* Small text on the Cube cards is hard to read. The katakana title logo is kept; it already carries "LOST HEROES".
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
