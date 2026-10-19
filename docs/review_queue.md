# Translation review queue

Decisions translators could not settle from the source. Each entry gives the key, the issue and what was done for now. Resolve in proofreading.

| Key | Issue | Current rendering |
|---|---|---|
| MainEventMess0112#0.14–0.15 | Source contradicts itself: 0.4–0.5 have Bogal about to eat Spider Man, but 0.14 says Twin Tail is being eaten, and the victim lines are labelled Twin Tail. | Translated as written ("Twin Tail", "its"). |
| MainEventMess0128#0.6, 0.9 | This copy has the speaker (Zero, from the Base twin 0902) call Hikari "big brother"; the Base version just says "Hikari". Check which version the game shows. | "Brother Hikari...!" |
| MainEventMess0112#0.21 | Kamen Rider W term for excessive Gaia Memory compatibility. No confirmed English term. | "someone with excessive compatibility" |
| OP MainEventMess01#0.95/0.97/0.102 · 0111#0.40 | Hub facility names ("base", "Hangar", "regeneration capsule") must match the UI translation. | Kept the source quotation marks. |
| MainEventMess0101#0.3–0.8 etc. | Rows with no recovered speaker (branch lines). Translators inferred them; check in-game. | Speaker-neutral where possible. |
| MainEventMess0301/0308/0311/0312 | The script passes speaker id 9 (Wing Zero) for lines whose content is Shotaro's (he calls Skull "oyassan"). Translated by content; check in-game which name label shows. | Voiced as Shotaro. |
| Glossary sweep | "Oyassan" (story_045) vs glossary "Boss"; "Alien Cool" (story_080) vs "Alien Kool"; "Senpai"/"Sempai" mix in early slices; "Solar Furnace" vs "GN Drive". Fix with a name script after proofreading (BASE_RULES order). | Glossary is the reference. |
| MainEventMess0253#0.173–0.174 | Script expects a second line at #0.174 for Zero's variant, but the table ends at #0.173. | Check in-game. |
| MainEventMess0340#0.1, 0343#0.1–0.4 (also 0218, 0225, 0231, 0240) | Old-font kanji in tables not flagged as legacy; meaning guessed from context (weakest: 0343#0.4 'Den-Metal'). Re-decode with the legacy mapper and re-check in proofreading. | Contextual guesses. |
| Speaker labels after empty table entries | My monotonic shift is right for 0205 (+2 after empty entry 36) but wrong for 0441 (still +1 after empty 0.86, per content). Labels after an empty entry are unreliable; proofreaders should check speakers by content in tables listed as shift_adjusted by speakers.py. | Translators voiced by content. |
| ChipLib enemy names (system_031/032) | Unverified romanizations: Gavadon, Baricane, Anf, Fanton, Cubrican, Sharkwhale, King Crab, Solitula, Grost, Digarug, Kroizel, Eledortus, Alien Shapley, Skullmaster, Empuras, Birugamo, Gigantes Hades, Alpha Azieru (official: α Azieru?), Helion Velvetum (system_036 #1.39, unidentified), Jin (system_045 #3.55, unidentified). Check against Ultraman Wiki / Kamen Rider Wiki / Gundam Wiki before release. | As guessed. |
| Name consistency across tables | The same Japanese name can get different English in different tables (e.g. Kuwagata Yummy vs Stag Beetle Yummy; Pteranodon Yummy (M)/(F) shortened). Before release: report every jp string with more than one English rendering across all slices (from the translation-memory data) and unify it with name_fix.py. | Pending. |

## From story 108–122 / system 060–064
- 0640 #0.81–85: speaker label "W (Shotaro)" is wrong; per 0640.bla check order these are Taro, Seven, Ultraman, Zero, Mebius (party-leader variants). Fix speaker metadata if displayed.
- 0587 #0.173/175/177: likely the missing 15th party-leader variant (God Gundam?) for the 14-row blocks; verify against the script.
- Regnant: the glossary gender is n; the pilot is Louise (female). Decide whether to use "she" when Louise is meant.
- Four Symbols items (system_060): "Genbu Shell" is romanized, while Blue Dragon Scale, White Tiger Fang and Yellow Dragon Whisker are translated. Unify (suggest Black Tortoise Shell).
- Unverified item spellings: Magnelium Medicalizer (#4.15), Tri-Ride Vendor (7.18), Maquette Kaiju, Execution Ground Key (R)/(L).
- system_062 6.49: the meaning of "goes down after a set time" is unclear.
- Speaker labels in 0618/0640 leader blocks are offset or placeholder (W (Shotaro)); translators used the script order. If speaker names are ever shown, regenerate them from the .bla branches.
- 0629#0.214–215: the last index of the script's leader chain points past the table end; check which line is shown.
- Unused lines (never called by scripts): 0640 #0.33–45, #0.72, #0.89–102; 0629 #0.173. They are translated anyway.
- story_125 0642 #0.207, #0.251–252: per story_124's script check these rough lines are Den-O (Momotaros). Add Momotaros tics in proofreading.
- 0646/0647/0648 (story_126–127): speaker labels appear one row late. Speakers were inferred from wording; story_126 #0646 0.3–8 should match the wording of story_127 #0.9–17.
- 0649 #0.70 (story_129) and #0.122 (story_130, unused copy) are the same Japanese line with different English; unify in proofreading. 0649 speaker labels are off by one; the story_130 notes give speakers from 0649.bla.
- speakers.py shift bug: labels are one entry off in 0646–0650 and 0661 (and possibly others). Labels are metadata only (not in the build), but fix shift_map before proofreading reuses them.
- 0701 (story_144): speaker labels look swapped between Seravee's Voice and the leader/Ankh. The lines were translated by content.
- Cross-table consistency: `tools/consistency.py --max-len 20` currently reports 254 short Japanese strings with more than one English rendering (99 in system). Resolve them in the proofreading pass, starting with skill names (Ray/Beam, Rebound Ray/Beam, Chain Combo/Combo Chain, God Shadow variants).
- Element passive names: system_087 uses '<Element> Element ATK Up'; system_086 2.75/2.76 use 'Fire Attack Up'/'Lightning Attack Up'. Unify (check width). Also check 'Cure Dark' vs Blind, and 'Cure Knockdown'.
- DECISION (2026-10-09): the staff roll (`Table/StaffRoll/StaffRoll.mbb`, 159 rows) stays in Japanese for now. It uses its own sequential font (`Font/FontStaff.tpc`, glyph sheet rendered to `work/source/font/staff/`): code − 1 = cell index, and code 11 is the name separator space. Translating it means romanizing real staff names (readings can't be confirmed from kanji) and rebuilding FontStaff with Latin glyphs. Revisit if official romanizations are found. Rows are `en: null` in system_093–096 and skipped by apply_en.
- 0718 #0.2–7 (story_154) should reuse story_155's "It's more concentrated than anything we've seen so far..."; 0721 #0.43–47 ("But") vs #0.48–57 ("No,"): check during proofreading.
- 0726/0727/0728: the last Ankh MessWinSet points one entry past the table end (e.g. 0727 MTBL has 4 entries [empty + 3]). This is an original-game quirk with no text to translate; check in-game that nothing breaks.
- story_024 0207 #0.2 is a 4-option choice menu (4 lines in the Japanese too); the 2-line story box check doesn't apply.
- MainEventMess0905/0906/0909 (story_178): old-encoding NC03 copies without the legacy flag; meaning taken from the Base copies (story_181) and story_060. Check scope.json status for these tables.
- 0915 #0.2 is Rider 1 per its script (story_184); story_055's copy of the same line guessed Rider 2. Check the speaker/voice in proofreading.
- Staff roll (2026-10-09): role titles and company names translated in `work/translation/en/staffroll.json`; people's names keep their original glyphs (readings unverified). Unverified company romanizations: Junks Inc. (ジャンクス), Arc Angel Ltd., Lancers Ltd., Layup Inc., Smartel (スマーテル, 0.113), MUTAN. Supersedes the earlier "staff roll stays in Japanese" decision.
- Eleking roar: story_090 has "Pikiiiiiiii!!!", while the glossary and story_178/179 use "Kiiiiiiiiiiih!!". Check whether the Japanese differs before unifying. Taka Candroid cries ("Kreeeee!!" / "Peep") are not in style.roars.
- Texture Camp.tpc UI_psp_CampWindow_4444: the 00 sprite (149,187,45,9) contains the W sprite (148,187,27,9), so the 00 label reads "W 00". Fix needs Camp.gtx GFUV sprite #31 changed to (175,187,19,9).
- Texture labels to check in game: split labels (Combo|Skill, Part|Repair...), poker "Royal S Flush" (original's S abbreviation), Z Gundam on the result screen, guessed menu words (Edit/Bulk/Info), area-name abbreviations (Sand, Wastes, Top/Mid/Low).

## Added 2026-10-09 (0.1.6)
- extra_008 0257#0.2: town "Yumemi Town" (romanized; franchise unconfirmed). 0261#0.24 minion cry "Veh-veh!!" (no established spelling).
- extra 0254: "senpai" toward RX dropped per glossary; 0735#0.20/0.21 remote voices, speaker unconfirmed.
- Unreferenced old-font tables left Japanese (NC03/0318, 0332; NC04/0416-0426, 0907-0910; NC05/0536-0550, 0577; NC06/0613; OP/1100). If one ever shows in game, decode it with a legacy map first.
- Tutorial captures: 551 CAP00 faded chip-report names approximated as "Chip"; tiny 4-6 px HUD text partly approximate (550 CAP02, 553 drop list); 553 "Reinf." cut at sprite edge; 558 typewriter frames truncated by design. Flat `bg` patches slightly off on gradient rows.
- Ride Dungeon intro panel (`ride_bg02`): 4th bullet wording guessed ("Plenty of custom parts, and much more").
- Title katakana logo (ロストヒーローズ) kept; it already carries "LOST HEROES".
- Camp menu two-word rows keep a gap (fixed sprite pieces: "Skill   Tree").

## Added 2026-10-09 (0.1.7)
- Native 4x font at 1x internal resolution / real PSP: point-sampled 4x texture is rougher than the 1x font (no mipmaps). Options if this matters: mipmap levels for the 4x pages, or ship the 1x-only EBOOT as an alternative patch.
- 4x font not yet seen in battle screens or the staff roll (FontStaff loads only for the credits).

## Added 2026-10-09 (0.1.8)
- Other split labels seen in game (same composite fix applies): Database submenu "Chara Catalog", Quest tabs "SubQuest", Options "Sound Test" / "Custom TrackSound"; Item Lab "Depot" is condensed.
- Save-data screen (Load/Save): play time label, "Save Data", hero names are Japanese (strings in the EBOOT / PARAM.SFO).
- Menu labels are textures, not the font: native 4x is impossible (PSP max texture 512 px); 2x is possible per page with a source-rect hook in 0x13c42c, but CampWindow is now 256x512 and cannot double.

## Added 2026-10-11 (0.1.10)
- (fixed 0.1.12: Base header) The Gate Port header has a stray "P" after "Gate Port".
- Cube select cards: the description block is tiny unreadable text.
- extra_012 0633 map label "High-Energy Reading Site" is the translator's coinage; check against the map UI. 0306 decoded with a wrong kanji (read from context).
- Other Shocker kaijin keep the "X Man" form (Bat Man, Mantis Man...); decide whether they follow Man Spider.

## Added 2026-10-17 (0.1.15)
- Display buffers: BattleMess (battle help banner) holds 63 characters. Other battle tables have English longer than their longest Japanese (Enemy/SystemMessage, Enemy/SkillName, Skill/SkillHelpMessage, AwardName...) and look fine so far; watch for lines cut short in battle.
- extra_015: speaker labels in MainEventMess0701/0706/0707 tag Ankh where Seravee (via Veda) speaks; Base info lines 0993-0995 newly written; 0717#0.16 speaker unknown.
