# Secret Bases and decorations (v18.4 / Emerald v1.5)

Faithful per version: pokeruby `src/secret_base.c`, `decoration.c`, `decoration_inventory.c`, `fldeff_decoration.c`,
`data/scripts/secret_base.inc`, `shared_secret_base.inc`; pokeemerald's equivalents. The 24 layouts, the 75 spots and the
decoration table are the same in both (`python3 b2tools/secret_base_data.py check`); the shops and gifts differ.

## How it is built
| Part | Where |
|---|---|
| Generated data, recipes, models, text | `b2tools/secret_base_data.py` (`header`, `rooms`, `spots`, `text`, `models`, `sheet`, `check`) |
| Hooks that must always be loaded | decomp `src/hoennb2/resident/secret_base.c` |
| Menus' logic, Gen 3's rules, cursor, mats | decomp overlay 348, `src/hoennb2/secret_base/sb_main.c`; loaded by gimmick 30 in a base, by the first script command elsewhere |
| Scripts | `src/field_scripts/1281_secret_bases.s` (global 10735-10745), `common/secret_base_defs.inc` |
| Text | `src/text/script/0436_secret_bases.txt` (431 lines: names, in-use names, descriptions, categories, Gen 3's lines) |
| Build patches | `b2tools/patches/secret_bases.py` (before `interiors`), `secret_bases_late.py` (last) |
| Offline checks | `b2tools/secret_base_check.py` |

## Rooms
24 zones, one chunk each, built by `models_cave.py` (Black 2's cave with Gen 3's colours through look key `tint`; the tree has a
wooden floor), area 299. Zones in layout order: see `ZONES` in secret_base_data.py. The bedrooms move to area 300. Both areas load
prop pack 17. Headers: no bike, Escape Rope or Fly (flags 0x4883), Gen 3's music (Fortree), place "Secret Base". The exit is
Black 2's own dynamic warp, destination warp 256 = GameData's next zone, which the spot's `FieldSetNextZoneHere` sets; it is in
the save, so saving in a base and continuing still gets the player out. A whiteout goes to the last Center, as in Gen 3.

## Placed decorations are props, not actors
A decoration is a Black 2 build model: one quad with Gen 3's own pixels (the floor pixels of its metatiles left out, found by
comparing two styles).
- A card leans back 6 units a row, so it covers its footprint from the game's camera and hides what walks behind it, as Gen 3's top
  rows do; mats and the board lie flat; posters lie on the wall tile's face; dolls and cushions stand nearly upright.
- `HoennB2_SB_LoadResBundle` reads only the models a room shows; the pack has 134 (limit 127 in a bundle, 100 KB).
- `HoennB2_SB_InstantiateProps` adds the fixtures and the placed decorations to the chunk's props and writes their cells into the
  chunk's terrain in memory. After placing or putting away, the script closes and reopens the field.
- People-sprite limit: untouched in a base. A fully decorated base uses 2 of 32 materials (the player's) and no actors.

## Save
Block 0x46 (Funfest), first 212 of 240 usable bytes (`SBSave`, magic "HSB3"; a save without it starts empty). Works 0x41A2
(first-entrance pending), 0x41A3 (spot being visited). No flags. Only `FestRecords_GetFromSave` reaches the block; its callers are
Funfest's overlays, and the trainer card reads +0xF4 only (which stays 0).

## Spots
`data/story/secret_bases.json`: actors uid 160 + index, code 0x0D00 + index; `HoennB2_SB_ResolveCode` picks the closed or open picture
(5 kinds x 2, after the berry trees' 93 in `src/sprites/berry_planting/pictures.json`, so they need berry planting on).

## Left out or approximated
See the "ready" report; the list is repeated in the release notes when the lead writes them.
