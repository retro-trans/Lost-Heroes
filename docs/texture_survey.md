# Japanese in textures (survey, 2026-10-09)

The text tables are fully translated: every table that an event script loads, plus the system tables, is English. The Japanese still drawn in the game is baked into UI textures. `tools/tex_render.py <ALLRES.PCK> <out_dir> <prefix...>` renders GFPT/GFXT textures to PNG (formats: 2 = RGBA5551, 3 = RGBA4444, 4 = RGBA8888, 7/9 = 4-bit paletted, 10 = 8-bit paletted; PSP-swizzled).

Surveyed prefixes: Graph/Base/UI, Graph/Bat/UI, Graph/Bat/BST, Graph/Camp/UI, Graph/Common, Graph/CutScene/GTix, Graph/Dg/Start, Graph/Dg/UI, Graph/Dg/Cmn, Graph/Minigame, Graph/RideSetup, Graph/Title, Graph/Logo, Graph/STARTUP_pk.cmp. Not yet surveyed: Graph/Dg/Fld packs (per-area title cards), Graph/CutScene/AssistSkill, Graph/Adv, Graph/Bat/Chara and .gim textures.

## Textures with Japanese

| Area | Texture page | What it holds |
|---|---|---|
| Base | UI_psp_BaseWindow_4444 | Base menu labels (Quest Room, facilities, chip/item menus, Battle Arena...) |
| Base | UI_psp_EQUIP_status_4444 | Stat labels (HP SP 物攻 間攻 物防 間防 速度 技術 腕力 気力 集中 精神 運) |
| Battle | UI_result_up_4444 | Result screen hero names (ライダー1号 電王 セブン ...) |
| Battle | UI_bat_moji_4444 | Battle command labels (コンボ スキル フィニッシュ, ride weapons 主砲 弾幕 装甲 ...) |
| Battle | UI_ride_win_4444, UI_bat_arrow_4444 | Ride battle labels (装甲 エネルギー 主砲 EN回復 シールド), resistances |
| Camp | UI_psp_CampWindow_4444 | Camp menu (習得・強化 フォース アクセサリ ステータス ...) |
| Camp | UI_psp_CampWindow1_4444 | Options (メッセージスピード BGM SE音量 カスタムトラック データインストール ...) |
| Camp | UI_3ds_Chipdb_4444 | Chip database labels (撃破数 ドロップボーナス エネミーキャラクター ガーディアン 出典) |
| Common | UI_MENU_CMN01_4444, UI_MENU_CMN02_4444, UI_MENU_CMN00_5551 | Shared menu labels (決定 戻る 編成終了 キャンプ ..., stats, 所持数) |
| Common | UI_Common_window_4444, UI_Common_ItemAP_4444 | Field window labels (次のエリアへ アイテム 話す 調べる, ダメージ床 エンカウント) |
| Common | UI_common_AREA_c1..c8 | Area/floor name strips per Cube |
| Common | UI_map_defaultdown01_4444/5551, UI_map_defaultdownBG_4444 | Map screen labels and area names |
| Dungeon | DG_START_logo_c01..c08 | Stylised Cube names on the dungeon start card |
| Dungeon | dg_title01/02 (C01A01, more per area in Graph/Dg/Fld) | Area subtitle ("不穏な曇天") |
| Minigame | Minigame_CMN01/02, UI_Poker_4444, UI_Memory_4444 | Poker hand names, スタート, はい/いいえ |
| Ride setup | UI_3ds_Ride_4444/5551 | Ride machine setup labels |
| Title | Title_logo03_4444 | Copyright lines (legal; usually kept) |
| Logo | LOGO_psp_copy_8888 | Anti-piracy notice screen |

The official logo (ロストヒーローズ / LOST HEROES) already carries English.

## What translating them takes

For each page: decide the English labels (glossary `ui` section), erase the Japanese, draw English in a matching style within the same rectangles (the UI code samples fixed UV boxes, so labels cannot grow), re-encode in the page's own format and palette, swizzle, and inject every copy (top-level `.tpc`, `.cmp` and pack copies). A `tex_render.py` encode path and an injection hook in `apply_en.py` are needed.
