English fan translation of **Lost Heroes** for PSP (**NPJH50647**, v1.01).

### Apply

**Recommended:** Use the latest [Retro Trans](https://github.com/retro-trans/retro-trans-tools) app. Click **Refresh catalog**, open **Automatic**, select your original Japanese ISO or the published English v0.1.16 ISO, choose **0.1.20** (or **Latest**), and select a new output filename. The app downloads the matching patch and verifies the result.

**Manual patching:** [DeltaPatcher](https://github.com/marco-calautti/DeltaPatcher) and [xdelta3](https://github.com/jmacd/xdelta) accept the same assets:

| Your source image | Patch |
| --- | --- |
| Original Japanese ISO | `LostHeroes-English-0.1.20.xdelta` |
| Published English v0.1.16 ISO | `LostHeroes-English-0.1.16-to-0.1.20.xdelta` |

```text
xdelta3 -d -s "Lost Heroes (Japan) (v1.01).iso" LostHeroes-English-0.1.20.xdelta "Lost Heroes English 0.1.20.iso"
```

To upgrade from the published v0.1.16 image:

```text
xdelta3 -d -s "Lost Heroes English 0.1.16.iso" LostHeroes-English-0.1.16-to-0.1.20.xdelta "Lost Heroes English 0.1.20.iso"
```

Both patches produce the same release image. The upgrade patch requires the exact published v0.1.16 image (SHA-256 `313783b8e216b183e60587f08af65b5e2fbea867c5789b3b29a8f1aa14f45b33`); use the original disc if yours does not match.

Original Japanese ISO: 1,145,667,584 bytes; SHA-256 `8c4b3f19aedc5d04b7df31ee1ecfa3257515af7dd958bca3f72fe469b5defbc9`.

Release output: 1,598,539,776 bytes; SHA-256 `f3df12d79120b533028f7bd055c7b583f3a273cc15a63fd9c02a496631bfc3fe`.

The exact source, output and patch hashes are in `BUILD-MANIFEST.json`. `VALIDATION.json` records the patch round trips, and `SHA256SUMS.txt` covers the downloads. Manual patchers require the unpacked ISO.

### What changed since v0.1.16

* **Battle crash fixed:** choosing a Crossover Skill partner could crash the game ("Bad Execution Address"). The target prompt and the target's name share a 31-character buffer, and "Select a target." plus a long English enemy name overran it and corrupted memory. The prompt now reads "Target:", which leaves room for the longest name.
* **Camp menu:** all rows use the same text size, baseline and left edge, without the wide gaps in "Use Skill" and "Check Quests".
* **Base menus:** the labels are drawn at full size instead of squeezed. Item Lab **Box** (was Depot), Briefing Room **Idle Play** and **Chips Claim**, Quest Room **Sub-Quest Take** / **Sub-Quest Claim** (was "Sub Quest Ro"), and the Sub Quest header without a gap. The quest reward label reads **Prize:**.
* **Gate Port:** the stray letter after the header is gone; the rows read **Cube**, **Maint.** and **Random • Cube**.
* **Random Cube screen:** the header reads **Random Cube Entry** (was "Select Cul Entce"), the banner reads **Random • Cube Challenge**, and cube names no longer have a double space.

Retains all v0.1.16 content: story, quest, base and system text, battle and field messages, save-data details, staff roll, the variable-width and native 4x Latin fonts, and the translated textures. See the [changelog](https://github.com/retro-trans/Lost-Heroes/blob/main/docs/CHANGELOG.md).

### Release status

**This is an early build. Further proofreading and full in-game playtesting are needed.** File and patch verification shows that the intended data is included and that the patches reproduce the release image. It does not certify emulator or console behavior. In PPSSPP, the Camp menu, Briefing Room, Item Lab, Quest Room, Gate Port and Random Cube screens were checked. The crash was reproduced and its cause confirmed in emulator memory; the fixed prompt has not yet been replayed in that battle.

Known limitations:

* Some menu labels assembled from several images still read oddly: Chara Catalog, the Main/Sub Quest tabs, Sound Test and Custom Track Sound.
* English names can be almost twice as long as the Japanese ones. The target prompt was one place where a name overflowed a fixed buffer; other places that copy a name have not all been checked.
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
