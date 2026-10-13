# Ruby version of HoennB2: scoping (ruby_scope, 2026-10-07)

Read-only survey. Nothing in the project was changed except this file. Sources: `external/pokeruby` (5784633, builds Ruby and Sapphire),
`converter/`, `b2tools/`, `data/`, `src/`, `notes/` of the working tree on 2026-10-07. The tree has about 20 uncommitted modified files from the post-game agents
(`git status`: among them `b2tools/world.py`, `patches/interiors.py`, `patches/story.py`, `converter/gen_caves.py`, `gen_encounters.py`, `allocate_zones.py`,
`data/hoenn_*.json`), so line numbers below can drift. "Checked" = I ran/grepped it; "[unchecked]" = not verified. No Ruby ROM is needed (`roms/` has only Black 2 and Sapphire rev1):
every Ruby datum is in the decomp source and graphics folder.

## 0. Result in brief
- Ruby = Sapphire with the two teams, their leaders and the two legendaries swapped. 85 asm `.ifdef` blocks in 22 files, 69 text placeholders in
  19 files, 28 trainer aliases, 33 of 97 wild tables, 2 layout swaps, 3 Ruby-only maps (Magma Hideout), the title screen (logo, Groudon, cry), a few C/graphics bits we do not use.
- Only 7 scenes change flow or an item (Magma Hideout B2F, Seafloor Room 9, Cave of Origin B4F, Route 128, Lilycove entrance, Southern Island,
  Mt. Pyre's orb) plus the weather and roamer patches. Everything else is **text + which trainer/sprite plays the evil team**. Our hand-ported scenes index their text by line
  number, so a line-for-line Ruby text layer needs **no scene edits** for text (tested, section 3).
- Sapphire is selected today by hard-coded Python (`cond = name == 'SAPPHIRE'`, `endswith('Sapphire')`, `EXPAND` table), by hand-ported scenes
  with Aqua baked in, and by literals (Kyogre 382, thunderstorm, Latias). There is no single define.
- Proposal: `HOENN_VERSION=sapphire|ruby` (default sapphire) read by one helper; assembler `-D HOENN_RUBY`; version overlay folders `ruby/` next to the
  shared files (invisible to today's non-recursive globs, so Sapphire stays byte-identical); a generated Ruby text/trainer/encounter layer.
- Art needed: Tabitha and Courtney (battle + overworld, 4 sheets) and a Ruby title logo. Maxie, Magma grunts M/F (battle and overworld) and Archie
  already exist; Groudon needs no new art (Black 2's own still and field model 4512).
- Five work packages (section 5), four of them parallel after the infrastructure step.

## 1. Every Ruby/Sapphire difference in pokeruby

### 1.0 How pokeruby switches (counts from grep over `external/pokeruby`, English only; `-de` copies ignored)
| Mechanism | Where | Count |
|---|---|---|
| `GAME_VERSION ?= RUBY` in `config.mk`; `--defsym RUBY=1`/`SAPPHIRE=1` (asm) and `-D RUBY`/`-D SAPPHIRE` (C) in `Makefile:94-95` | build | 1 |
| asm `.ifdef/.ifndef SAPPHIRE` | 21 map/script files + `data/event_scripts.s` | 85 blocks, 22 files |
| `constants/version.inc` (included by `src/crt0.s`, so by every script) | aliases | GAME_VERSION + 5 alias groups (below) |
| text placeholders `{EVIL_TEAM} {GOOD_TEAM} {EVIL_LEADER} {GOOD_LEADER}` (charmap FD 08-0B, table in `src/string_util.c:477`) | English map text | 69 uses, 19 files (`{EVIL_TEAM}` 56, `{GOOD_LEADER}` 6, `{GOOD_TEAM}` 4, `{EVIL_LEADER}` 3). `{EVIL_LEGENDARY}/{GOOD_LEGENDARY}/{VERSION}` have no English use |
| C `#ifdef SAPPHIRE/RUBY` | `title_screen.c` 5, `intro.c` 5, `strings.c` 4, `slot_machine.c` 4, `data/graphics.c` 4, `credits_en.h` 2, `string_util.c`, `species.h` (ROAMER_SPECIES), `overworld.c:53` (LEGENDARY_MUSIC), `mystery_event_script.c:32`, `global.h` | about 30 |
| runtime `gGameVersion` | `battle_setup.c:604` (Groudon: shards transition / Kyogre: ripple), `battle_bg.c` (5 tests, cave vs water background), `battle/anim/battle_intro.c:51`, `pokemon_1.c:1429` (met game), `link.c:295`; the summary screen only tests the value | about 10 |
| wild table labels `*_Ruby` / `*_Sapphire`, template `wild_encounters.json.txt:28-83` | `src/data/wild_encounters.json` | 194 entries = 97 maps x 2 |
| `setmaplayoutindex N` in OnTransition | 2 maps | 2 |
| `OBJ_EVENT_GFX_VAR_n` filled by `Common_EventScript_SetupEvilTeamGfxIds` / `SetupLegendaryGfxIds` (`data/scripts/dynamic_npc_graphics.inc`) | map.json objects | 57 maps (30 with story objects, 24 secret bases, 3 decoration rooms) |
| Pokédex text `#ifdef SAPPHIRE` | `src/data/pokedex_entries_en.h` | 203 blocks |
| `map.json`, `layouts.json`, tilesets | none: `grep -w SAPPHIRE\|RUBY` finds nothing in them | 0 |

`constants/version.inc` (checked): `GAME_VERSION` 1/2; `MUS_EVIL_TEAM/GOOD_TEAM` = ENCOUNTER_AQUA/MAGMA swapped; `ITEM_RED_OR_BLUE_ORB`;
`SPECIES_GROUDON_OR_KYOGRE`; `SPECIES_LATIAS_OR_LATIOS` (Sapphire: Latios, Ruby: Latias; roamer is the other one: `ROAMER_SPECIES`);
28 `TRAINER_*` aliases (1.2). The Sapphire side is Aqua = evil, Magma = good; Ruby is the mirror.

### 1.1 Map scripts and text
Flow differences (not just words), all checked in `scripts.inc`:
| Map / file | Blocks | What differs |
|---|---|---|
| `AquaHideout_B2F` (aliased by `MagmaHideout_B2F`) | 5 | escape scene: the submarine shadow's object id (VAR_0x8009 4 in Aqua B2F, 3 in Magma B2F; object 1 is the admin in both), the admin's turn (left vs right) and the submarine's path (`Movement_15D958` vs `_15D95D`): the Magma map has other geometry (triggers at y=16 x=4-7 vs x=28 y=16-17) |
| `SeafloorCavern_Room9` | 18 | **layout 157 vs 327** (1.4); 15 text pairs; two glow colours (`VAR_RESULT` 1/0, cosmetic: our port uses one white flash) |
| `CaveOfOrigin_B4F` | 4 | **layout 163 vs 313**; 2 text pairs; glow colour; fight is Groudon/Kyogre Lv 45 (same level) |
| `Route128` | 2 | Ruby only: `special sub_807E25C` (screen brightens, `field_weather_effects.c:290`) before Maxie/Archie scene; 1 text pair |
| `LilycoveCity` OnLoad | 1 | Ruby repaints the hideout entrance 12 metatiles (x 69-72, y 4-6) one tile east; warp (71,5) goes to `MagmaHideout_1F`, (70,5) to `AquaHideout_1F` (both warps exist in `map.json` in both versions) |
| `SouthernIsland_Interior` | 1 | object gfx Latios vs Latias; `setwildbattle SPECIES_LATIAS_OR_LATIOS, 50, ITEM_SOUL_DEW` |
| `event_scripts.s:862` `SetLegendaryWeather` | 1 | `WEATHER_RAIN_HEAVY` vs `WEATHER_DROUGHT` |
| `data/scripts/tv.inc:44` | 1 | text of the news that starts the roaming Latias/Latios (`InitRoamer`) |
| `Route110_TrickHouse*` (2), `Route114_LanettesHouse` | 3 | decoration prizes Red/Blue Tent, Seedot/Lotad Doll (we have no decorations: nothing to do) |
| `Route115` | 1 | trainer 514 = Hector 1 (Zangoose) vs Hector 2 (Seviper) + his 3 lines |
| `dynamic_npc_graphics.inc` | 2 | gfx roles (below) |

Text-only blocks (message label differs, structure identical), counts of Ruby-only message labels that have a Sapphire twin (checked, 76 pairs in all):
`MtChimney` 16, `MtPyre_Summit` 12, `SeafloorCavern_Room9` 15, `SootopolisCity` 8, `magma_summit.inc` 9, `magma_chimney.inc` 7,
`CaveOfOrigin_B4F` 2, `Route115` 3, and 1 each in `MeteorFalls_1F_1R`, `Route128`, `SlateportCity_OceanicMuseum_2F`, `tv.inc`. The Ruby strings sit in
`data/text/magma_{awakening,chimney,settled,summit}.inc` (412 lines); Sapphire's in `data/text/aqua_*.inc` + `aqua_misc.s` (426 lines).
Placeholder uses (map -> uses): MeteorFalls_1F_1R 15, LilycoveCity 9, Route128 7, Route119_WeatherInstitute_2F 5, Route110 4, PetalburgWoods 4,
AquaHideout_1F 4, FallarborTown_House1 3, SlateportCity 3, SlateportCity_Harbor 3, Underwater_SeafloorCavern 2, OceanicMuseum_1F 2,
CoveLilyMotel_1F 2, 1 each in OceanicMuseum_2F, RustboroCity, SeafloorCavern_Room3, WeatherInstitute_1F, AquaHideout_B1F, and the
region-map name `{EVIL_TEAM} HIDEOUT`.

Gfx roles from `dynamic_npc_graphics.inc` (`Common_EventScript_SetupEvilTeamGfxIds`): VAR_1/2 = evil team M/F (Aqua / Magma), VAR_4/5 = good team M/F,
VAR_6 = evil leader (Archie / Maxie), VAR_7 = good leader, VAR_8/9 = Kyogre / Groudon. 30 story maps use them: AquaHideout_1F/B1F/B2F,
MagmaHideout_1F/B1F/B2F, CaveOfOrigin_B4F, LilycoveCity, MeteorFalls_1F_1R, MtChimney, MtPyre_Summit, PetalburgWoods, Route110, Route112, Route119,
Route119_WeatherInstitute_1F/2F, Route121, Route128, RustboroCity, RusturfTunnel, SeafloorCavern_Room1/3/4/9, SlateportCity, SlateportCity_Harbor,
SlateportCity_OceanicMuseum_1F/2F, SouthernIsland_Interior.

### 1.2 Trainers and parties (28 aliases; every party/stat read from `trainers_en.h` / `trainer_parties.h`)
| Role | Sapphire -> Ruby | Party difference |
|---|---|---|
| 21 grunts | e.g. GRUNT_9 -> GRUNT_36 (Petalburg Woods), 15 -> 42 (Rusturf), 19/20 -> 46/47 (Museum), 13 -> 40 (Chimney), 1 -> 28 (hideout 1F), 2/3/26 -> 29/30/53 (B1F), 4/27 -> 31/54 (B2F), 5/6/7 -> 32/33/34 (Seafloor), 22/23/24 -> 49/50/51 (Pyre), 16/25/17/18 -> 43/52/44/45 (Weather Institute) | 14 swap Carvanha -> Numel (levels unchanged); 7 identical parties (9/36, 15/42, 13/40, 1/28, 27/54, 22/49, 16/43); class TEAM_AQUA -> TEAM_MAGMA, pic AQUA_GRUNT_M/F -> MAGMA_GRUNT_M/F |
| 4 admins | MATT_1/2 -> TABITHA_1/2, SHELLY_1/2 -> COURTNEY_1/2 | Carvanha/Sharpedo -> Numel/Camerupt (L20 Chimney, L32 hideout, L28 Institute, L38 Seafloor); class AQUA_ADMIN -> MAGMA_ADMIN, pics MAGMA_ADMIN_M/F |
| 2 leaders | ARCHIE_2/3 -> MAXIE_2/3 | Sharpedo -> Camerupt (L43, L25); class AQUA_LEADER -> MAGMA_LEADER |
| Route 115 | HECTOR_1 -> HECTOR_2 (Collector) | Zangoose -> Seviper, L20 |
Same Sapphire script slot = same Black 2 trainer id is possible: `data/level_scaling.json` already has all 693 pokeruby trainers, and the Aqua/Magma
twins have equal scaled levels (checked MATT_1/TABITHA_1 34, SHELLY_2/COURTNEY_2 41, ARCHIE_2/MAXIE_2 45/45/47, GRUNT_1/28 34, MATT_2/TABITHA_2 20,
HECTOR 20). Messages: the Ruby labels are the `.else` branches in 1.1 (Mt. Chimney, Pyre summit grunts) or the neutral grunt texts with placeholders.
Rematch tiers (`gTrainerEyeTrainers`) contain no team trainer.

### 1.3 Wild encounters and exclusives
97 maps have a Ruby and a Sapphire table; slot odds and encounter rates are identical in all (checked); **33 maps differ**, always in species or level of
a few slots, so each Ruby file has the same shape and size as Sapphire's (the a/1/2/7 fixed-size rule holds).
| Ruby / Sapphire | Maps |
|---|---|
| Seedot / Lotad | Route 102 (slots 4,5), Route 114 (1,4) |
| Nuzleaf / Lombre | Route 114 (6,7) |
| Zangoose / Seviper | Route 114 (5,8,9,10) |
| Minun, Plusle weights swapped (both appear in both games) | Route 110 (4,6 vs 10,11) |
| Illumise / Volbeat | Route 117 (6-10) |
| Duskull / Shuppet | Mt. Pyre 1F-6F, Exterior, Summit, Route 121 (1,3), Route 123 (1,3); on 4F-6F and Summit the other species fills slots 7/8-11 |
| Dusclops / Banette | Sky Pillar 1F, 3F, 5F (slots 5,6) |
| Mawile / Sableye | Granite Cave B1F, B2F; Cave of Origin 1F, B1F, B2F, B3F; Victory Road B2F; Sky Pillar 1F, 3F, 5F |
| Solrock / Lunatone | Meteor Falls 1F_1R, 1F_2R, B1F_1R, B1F_2R (land and surf) |
| Koffing / Grimer | Fiery Path (1,6 vs 10,11) |
| Magikarp / Tentacool | Sootopolis fishing slot 1 |
| levels only | Jagged Pass (Sapphire +2 on all 12), Route 129 Wailord 35-40 vs 25-30, Safari Southwest Doduo 25 vs 27 |
Static: Cave of Origin Groudon/Kyogre Lv 45; Southern Island Latias/Latios Lv 50 (+ Soul Dew); roamer Latios/Latias Lv 40. No other gifts differ
(`item_ball_scripts.inc`, `static_pokemon.inc`, marts, TM tables: no `.ifdef`).

### 1.4 Map layouts and events
- **No map.json difference** (positions, warps, music, weather: identical). Events differ only through the gfx roles and flag-hidden objects.
- **Magma Hideout** = three Ruby-only maps with their own layouts (`MagmaHideout_1F` 28x30 like Aqua's, `B1F` 62x24 vs Aqua 51x24, `B2F` 34x24), objects at
  other tiles, scripts that alias the Aqua labels (`MagmaHideout_1F_EventScript_15D80C` is the same code as `AquaHideout_1F_...`, and its texts say
  `{EVIL_TEAM}`). The Lilycove entrance is a cave mouth in both versions.
- **Layout swaps** (setmaplayoutindex, tiles compared from `layouts.json`/`map.bin`):
  | Map | Sapphire layout | Ruby layout | Tiles that differ |
  |---|---|---|---|
  | SeafloorCavern_Room9 (27x46) | LAYOUT_SEAFLOOR_CAVERN_ROOM9 | LAYOUT_UNKNOWN_MAP_083041B4 | 95, of which **65 change collision**, 2 elevation (x 12-23, y 31-42: Sapphire's water basin becomes a rock/land basin) |
  | CaveOfOrigin_B4F (19x19) | LAYOUT_CAVE_OF_ORIGIN_B4F | LAYOUT_UNKNOWN_MAP_082FF894 | 43, **0 collision/elevation change** (water pool tiles 0x14e/0x14f become 0x364/0x35f, walls re-drawn: visual only) |
  | LilycoveCity | entrance in the layout at x 69-71 | OnLoad repaints x 69-72, y 4-6 | 12 metatiles |
- Ruby tile ids (0x35f-0x373 of gTileset_Cave) are not in `data/cave_tiles.json`; the cave builder classifies by collision and behaviour, so they need a look.

### 1.5 Items and gifts
Orbs (Mt. Pyre summit, `ITEM_RED_OR_BLUE_ORB` x2 in `MtPyre_Summit/scripts.inc`; Black 2 has both items, `gen_key_items.py` maps them "same"); Trick House
and Lanette decorations (we have none); Eon Ticket/Mystery Event version mask (`VERSION_MASK` 1<<7 vs 1<<8: not used, we give event tickets in game).
Shops, item balls, hidden items, TMs, berries: identical.

### 1.6 Graphics and audio
| What | Ruby vs Sapphire | Used by us |
|---|---|---|
| `graphics/title_screen/` | `pokemon_ruby.png`, `rubyversion.png`, `logo_ruby.pal`, `groudon*.{png,pal}`, `groudon_map.bin` vs sapphire/kyogre set; `title_screen.c`: Kyogre red markings vs Groudon blue, palette index 26/21 | **no** (our title is new art + Black 2's Kyogre still, `patches/title.py`) |
| `graphics/intro/` | `intro2_latias.png` vs `intro2_latios.png` (+ `CycleSceneryPalette(0/1)`) | no (our intro is Prof. Birch + Azurill) |
| `graphics/trainers/` | `aqua_{grunt,admin}_{m,f}`, `archie` vs `magma_{grunt,admin}_{m,f}`, `maxie` (all 8 present in the folder; **Tabitha = `magma_admin_m`, Courtney = `magma_admin_f`**) | yes (art source) |
| `graphics/object_events/pics/` | `aqua_member_{m,f}`, `archie` vs `magma_member_{m,f}`, `maxie`; `pokemon/{groudon,kyogre}.png`, `latias_latios.png` | yes |
| `battle_bg.c`, `graphics/battle_environment/{cave/groudon,water/kyogre}.pal` | Groudon cave vs Kyogre water background | no (Black 2 legendary battle) |
| slot machine palettes (`slot_machine/*ruby*|*sapphire*`, `graphics/unknown/ruby_*|sapphire_*`) | 14 palette files | no |
| credits | `Text_Version` "POKéMON RUBY VERSION" | no (Black 2 credits, our memory photos) |
| audio | `MUS_EVIL_TEAM` = ENCOUNTER_MAGMA, `LEGENDARY_MUSIC` = MUS_WEATHER_GROUDON; no sound file differs (`grep` of `sound/`: 0) | no (Black 2 tracks; our eye-contact BGM for AQUA and MAGMA is the same, 1127) |

### 1.7 Pokédex and other
`pokedex_entries_en.h`: 203 per-version description blocks. **Unused by us** (Black 2 keeps its own Pokédex text; grep over `converter b2tools src notes`: 0 hits).
Default player names (Sean/Marina vs Landon/Terra, `strings.c`): unused (Black 2's naming screen; grep 0). Easy-chat words "SAPPHIRE"/"RUBY", Mauville Bard
sounds: unused. Link/summary "met game", slot machine, Secret Bases: not in the port.

## 2. Where each group lands in our pipeline
"carries" = already handles the Ruby side; "hard-codes" = Sapphire literal; "branch" = needs a Ruby path.
| Group | Our files | State today | Needs |
|---|---|---|---|
| Selection of the version | `converter/gen_trainers.py:55-62` and `level_scaling.py:52-59` (`sapphire_lines`: `cond = m.group(2) == 'SAPPHIRE'`, two copies), `level_scaling.py:70` `load_aliases` (version.inc), `gen_encounters.py:49`, `gen_caves.py:110` (`endswith('Sapphire')`), `sapphire_data.py:80` (`_Sapphire`, else any non-Ruby), `gen3text.py:46` `EXPAND` (VERSION=SAPPHIRE, EVIL_TEAM=AQUA, GOOD_TEAM=MAGMA, ...), `allocate_zones.py:35` (`{EVIL_TEAM}` -> 'AQUA ' for place names) | hard-codes | one version helper (3) |
| Readers that ignore `.ifdef` (they see both branches) | `gen_map_content.py ruby_scripts`, `gen_caves.map_scripts/hole_warp`, `allocate_interiors.py`, `gen_interiors.py`, `centers_rooms.py`, `shops_data.py`, `gen_hidden_items.py` | harmless: a script with both branches has two `msgbox` and is treated as "story" in both versions | the resolver only for `setmaplayoutindex` (cave layouts) |
| Text | `src/text/scenes/*.txt` (12 files with team words), `src/text/script/*.txt` (23), `src/text/system/0381`, `0383`, `0485` | hard-codes (expanded at port time with Sapphire's words) | Ruby text layer; class names Team Magma / Magma Leader / Magma Admin (0383/0485 lines 187-192) |
| Trainers | `converter/gen_trainers.py` (604 trainers, registry `data/hoenn_trainers.json` keyed by Sapphire constant, `PIC_SPRITE`/`KEEP_CLASS` Aqua rows, `EYE_BGM` already has MAGMA), `data/hoenn_trainer_classes.json` (classes 187/188/189/191/192 = Team Plasma rows edited into Aqua), `src/trainers/*.s`, `src/include/hoenn_trainers.h`, `patches/trainers.py` | Aqua only; the 28 Ruby trainers are `null` in the registry | Ruby outputs in the same Black 2 ids, Magma class rows |
| Level scaling | `data/level_scaling.json` | **carries** all 693 trainers; `wild` has Sapphire tables only; the curve table is species-independent | reuse the curve; no refit |
| Wild tables | `converter/gen_encounters.py`, `gen_caves.py`, `src/encounters/NNNN_*.s`, `data/hoenn_encounters.json` (file ids) | Sapphire only | 33 Ruby files, same ids and sizes |
| Scenes | `src/field_scripts/scenes/*.inc`, room files `NNNN_room_*.s`, `data/story/*.json` | Aqua baked in; **90 story objects** use team/legend models (Aqua grunt M 60, F 5, Archie 6, Maxie 4, Magma grunt M 6, F 1, Matt 2, Shelly 2, Kyogre 3, Latios 1); 14 Aqua trainer constants named in 10 files; no `HOENN_RUBY` branch anywhere | 7 scenes with an `#ifdef` (list in section 4) |
| Sprites | `src/sprites/{trainer/front,overworld}`, `b2tools/sprite_upgrade.py` (CHARS), `data/sprite_map.json` | **carries** Maxie (front 148 / ow 303), Magma grunt M (154 / 302), F (156 / 192), Archie (151 / 353), Matt (152 / 88), Shelly (153 / 92). **Missing: Tabitha, Courtney** (`sprite_upgrade.py:12` says so) | 4 new sheets (WP4) |
| Maps | `b2tools/ship_hideouts_rooms.py` (`--magma`), `data/interior_layouts/MagmaHideout_*.json` (**recipes built**), `data/hoenn_interiors.json` (zones 228/231/234, scripts 456.., status "big"), `b2tools/world.py:533` big-room doors, `scenes/LilycoveCity.inc:69` (`LC_HIDEOUT_WARP 27`), `data/cave_layouts/{SeafloorCavern_Room9,CaveOfOrigin_B4F}.json` | recipes carry; **no zone files** (`data/interiors/228,231,234.json` absent), no room scripts/text; caves built from the Sapphire layout only | zone files, 3 room scripts, 2 layout variants, door filter |
| Title | `b2tools/patches/title.py` (species literal 382 at ov162 0x1B0; Kyogre front 7640/palette 7658), `b2tools/title_art.py:32` (`KYOGRE_STILL, KYOGRE_PAL`), `data/title/logo.png`, `strip.png` (Sapphire logo, sea-blue strip and backdrop) | hard-codes | Ruby logo + red strip; Groudon: 383, front 7660, palette 7678 (formula `species*20`, `+18`, from `title_art.py`; [unchecked] files) |
| Weather | `b2tools/patches/weather.py` (`THUNDERSTORM = 6`, crisis maps, flag 903), `src/field_scripts/common/legendary_weather.inc` | hard-codes Kyogre | Groudon weather: Black 2 has **no drought id** (ids found: 0 sunny, 1 snow, 2 rain, 3 sandstorm, 6 thunderstorm, 7 heavy rain, 8 diamond dust, 9-14 fog/haze/cloud): needs a look decision |
| Roamers / TV | `b2tools/patches/roamers.py:55` (`('LATIAS', 40)`), `scenes/SouthernIsland_Interior.inc` (`SPECIES_LATIOS`, uid 102, model 4510), `data/story/ch13.json` | hard-codes | Ruby: roamer Latios, island Latias (Black 2 field model table `a/2/0/8`: Latias 4509, Latios 4510, Kyogre 4511, **Groudon 4512**; checked in the table, sheet render [unchecked]) |
| Orb | `scenes/MtPyre_Summit.inc:102`, `MtPyre_Summit_Ch10.inc:21` (`ITEM_BLUE_ORB`), `scenes/ch10_test.inc`, `ch8b_test.inc` | hard-codes | `ITEM_RED_OR_BLUE_ORB` alias |
| Place names | `data/hoenn_zones.json:266` "Aqua Hideout" (written to the place-name text by `patches/text.py`) | hard-codes | "Magma Hideout" |
| Pokédex, intro, credits, default names, battle bg | - | n/a (Black 2's) | nothing |

Chapter ownership of the 90 team objects (`data/story/*.json`): ch1 1, ch2 2, ch3a 20, ch3b 5, ch4 7, ch5 13, ch7 7, ch8a 5, ch8b 16, ch10 13, ch13 1.

## 3. Proposed design

### 3.1 The switch
- **`HOENN_VERSION=sapphire|ruby`**, default `sapphire`, anything else is an error. One helper `b2tools/version.py` (imported by `converter/*.py` through its
  existing `sys.path` setup) exports: `VERSION`, `is_ruby()`, `SUFFIX` ('Sapphire'/'Ruby' for wild labels), `EXPAND` (the 7 placeholders),
  `resolve_ifdef(path)` (replaces the two `sapphire_lines` copies), `overlay_files(dir, pattern)`, `OUT_DIR` suffix. Same naming as the existing
  `HOENN_*` variables (`HOENN_WORLD_DIR`, `HOENN_BUILD_DIR`, `HOENN_TEST_*`), so agents' build scripts pass it through the environment unchanged.
- **Assembler**: `patches/scripts.py` adds `-D HOENN_RUBY` (Ruby) or `-D HOENN_SAPPHIRE`; it already assembles with `clang -x assembler-with-cpp` and passes
  `-D HOENN_TEST_*`. Scenes use `#ifdef HOENN_RUBY ... #else ... #endif` (same as pokeruby's `.ifdef SAPPHIRE` reading). New `src/include/hoenn_version.inc`
  mirrors `constants/version.inc` (`SPECIES_GROUDON_OR_KYOGRE`, `SPECIES_LATIAS_OR_LATIOS`, `ITEM_RED_OR_BLUE_ORB`, `TRAINER_MT_CHIMNEY_GRUNT_1..`
  aliases) so scenes stop naming Kyogre/Blue Orb literally. Scenes keep their `ScriptEntry` count identical in both versions (only bodies branch).
- **Overlay folders `ruby/`** next to the shared files: `src/field_scripts/ruby/` (Magma Hideout rooms), `src/text/{script,system}/ruby/`,
  `src/encounters/ruby/`, `src/trainers/ruby/`, `src/sprites/{trainer/front,overworld}/ruby/`, `data/story/ruby/` if ever needed. A file with the same number or
  name in `ruby/` replaces the shared one; others are shared. Loaders today use non-recursive `glob('*.s')`/`('*.txt')` (checked in `scripts.py`, `text.py`,
  `encounters.py`, `trainers.py`), so the folder is invisible to Sapphire builds. `patches/sprites.py folders()` (line 46) globs every entry of the kind folder
  but skips names whose first part is not a number, so a `ruby/` folder is ignored there too; its `sprite.json` already supports `"copy_of": N`, which
  fits the art swap below (resolve `copy_of` against the shared set, so 293 and 302 can trade places).
- **Generators** (`gen_trainers`, `gen_encounters`, `gen_caves`, `gen3text`, `level_scaling`, `allocate_zones`, `sprite_upgrade`) take the version from the helper;
  for `ruby` they write only the files that differ into the `ruby/` folders (Sapphire output stays byte-identical, `git diff` empty). Generated Ruby files are
  committed like the Sapphire ones; a `--check` run in the rebuild script proves they are current.
- **Outputs**: `HOENN_BUILD_DIR` defaults to `work/rom_ruby` when ruby; `builds/hoenn_ruby_vNN.nds`; release `release/HoennB2_Ruby_vNN.bps` (notes/RELEASE.md).
  The world (`work/world`, terrain, buildings) and interiors are shared: **a Ruby ROM is `HOENN_VERSION=ruby HOENN_AGENT=ruby zsh b2tools/story_build.sh`
  on the lead's world**, as every chapter agent builds (checked: `story_build.sh` reads `work/world` and `work/interiors` read-only).

### 3.2 Per area
| Area | How |
|---|---|
| **Text** | New `converter/gen_ruby_text.py`: for every line of `src/text/{script,scenes,system}` that equals the converted Sapphire string of a pokeruby label (`gen3text.convert(raw, expand=True)`), emit the Ruby twin at the **same line index** into `src/text/script/ruby/NNNN_*.txt` (whole-file replacement, as `text.py` already replaces by file number). Twin = (a) the `.else` label of the same `.ifdef` position (76 pairs) or (b) the same label re-expanded with Ruby's `EXPAND` (53 labels). Scene code needs no edit: the `MC_T_*` indices stay valid. **Tested read-only on the current tree**: of 110 team-word lines in `script` + `system`, 94 match a pokeruby label verbatim; the other 16 are 10 class-name lines (187-192 of 0383/0485: fixed by hand/class table), 4 trainer messages of 0381 (made by `gen_trainers`, not by hand) and the 2 hand-written Cave of Origin B4F lines. The tool builds 129 twin entries (108 differ from their Sapphire string); **161 of our lines in 36 files match one (12 scene sources, 23 merged script files, 0381)**; net +157 characters over all 108, widest Ruby line 43 characters vs 49 in Sapphire's. Run it after `gen_map_content.py` (it merges scenes into `script/*.txt`). |
| **Trainers** | `gen_trainers.py` for ruby: the 28 Ruby aliases take the **Black 2 id of their Sapphire twin** (registry untouched), parties/names/messages/levels from the Ruby branch and `level_scaling.json`; `hoenn_trainer_classes.json` gets a `ruby` section pointing classes 187/188/189/191/192 to MAGMA_GRUNT_M/F, MAXIE, MAGMA_ADMIN_F/M with names "Team Magma", "Magma Leader", "Magma Admin" (0383/0485) and the existing front slots 154/156/148 + Tabitha/Courtney in slots 152/153 (overlay). `trainers.py` selects the section. Scenes keep `TRAINER_MATT_2` etc. (the id now holds Tabitha); `hoenn_version.inc` adds readable aliases. Assertion in the tool: same message record list (types, count) as the Sapphire twin, so `a/0/8/9`, `a/0/9/0` keep their size. |
| **Wild** | `gen_encounters.py`/`gen_caves.py`/`sapphire_data.py` use `SUFFIX`; 33 maps write `src/encounters/ruby/NNNN_<Map>.s` (same file id from `data/hoenn_encounters.json`, same size). Level curve unchanged (it maps level to level; checked that rates and slot odds are equal in all 97 maps). |
| **Models / sprites** | Keep the *role -> Black 2 code* of Sapphire and swap the **art** per version: Ruby overworld overlay puts Magma grunt M art on code 293, F on 294, Maxie on 353, Tabitha on 88, Courtney on 92, and Aqua grunt M/F/Archie art on 302/192/303 (the "good team" objects). Result: **0 edits to `data/story/*.json`, zone entity tables or the 30-sprite-per-zone budget** (`npc_check.py` counts codes). `sprite_upgrade.py --version ruby` writes the overlay by copying/swapping existing sheets and drawing only Tabitha/Courtney. The legendaries are Pokémon field-model codes (records of `a/2/0/8`), not sheets, so they cannot be art-swapped: add a `model_ruby` key read by `patches/story.py` to 4 objects: Kyogre 4511 -> Groudon 4512 (`ch10.json`: Cave of Origin B4F uid 1, Seafloor Room 9 uids 1 and 7) and Latios 4510 -> Latias 4509 (`ch13.json`, 1 object). |
| **Maps** | `data/versions.json` `rooms`: `AquaHideout_*` -> sapphire only, `MagmaHideout_*` -> ruby only. `world.py:533` (big-room doors), the `interiors`, `scripts`, `text` patches skip the other version's rooms, so each ROM has exactly **one** hideout door and `LC_HIDEOUT_WARP 27` stays (the door is the 14th door either way; verify in the built ROM). `ship_hideouts_rooms.py --magma` becomes the Ruby default. Layout variants: `data/cave_layouts/<Map>.json` gets `"variants": {"ruby": {"layout": "LAYOUT_UNKNOWN_MAP_083041B4"}}`; `models_cave.py` builds `<Map>` for Sapphire and the variant for Ruby from the layout named by the Ruby branch of `setmaplayoutindex` (resolver); the `interiors` patch picks per version. B4F is visual only (lava pool instead of water in `pools`); Room 9 changes 65 collision tiles. Lilycove terrain: keep the one cave mouth for both (the one-tile shift of the painted entrance is cosmetic). |
| **Title** | `title_art.py` constants become a per-version table `{sapphire: (382, 7640, 7658, 'data/title/logo.png'), ruby: (383, 7660, 7678, 'data/title/ruby/logo.png')}`; `title.py` patch literal 0x1B0 and the sea-blue backdrop follow it. New art: Ruby logo + strip (the user agreed new art for the logo only, DECISIONS 2026-10-06). |
| **Weather / roamers** | `weather.py`: per-version `(weather id, crisis maps)`; roamer list from the version table. Drought look is an open question (section 6). |
| **Savestates** | Both ROMs share `RESERVE` sizes, so the NDS file table should be identical and `work/emu/base_*.dst` interchangeable. Not assumed: acceptance test below. |

### 3.3 Acceptance tests (WP0 builds them)
1. `HOENN_VERSION` unset and `=sapphire` produce a ROM with the same SHA-1 as before the change (same tree, before/after).
2. New `b2tools/rom_layout_diff.py` (none exists; grep of `b2tools` finds no file-table comparer): NDS file table (offset, size per file) of the Ruby ROM equals Sapphire's.
3. `rooms_check.py`, `caves_check.py`, `npc_check.py`, `outdoor_check.py` pass on the Ruby ROM; the existing `HOENN_TEST_CH<n>` switches run unchanged on it.
4. Census: in the Ruby ROM's text, "Aqua" appears only for the good team (Meteor Falls, Chimney, Room 9) and "Magma" everywhere Sapphire says "Aqua"; no "Kyogre", "Blue Orb", "Archie" in an evil-team line.

## 4. Scene inventory for WP2 (our files, team/legend references counted by grep; test files excluded)
Flow changes (need `#ifdef HOENN_RUBY`): `0020_room_AquaHideout_B2F.s` (12; becomes Magma B2F: other ids/movements/triggers), `0380_room_SeafloorCavern_Room9.s` (56; layout, optional red flash),
`0206_room_CaveOfOrigin_B4F.s` (13; Groudon, red orb, 4512), `scenes/Route128.inc` (36; brighten effect), `scenes/SouthernIsland_Interior.inc` (16; Latias),
`scenes/LilycoveCity.inc` (8; hideout door), `scenes/MtPyre_Summit.inc` + `_Ch10.inc` (29 + 18; Red Orb), the weather/roamer patches (not scenes).
Text + role only (nothing to edit once the text layer and trainer ids exist; test, don't touch): `scenes/MtChimney.inc` (84), `0256_room_MeteorFalls_1F_1R.s` (24),
`0022_room_SlateportCity_OceanicMuseum_2F.s` (14), `0004/0010_room_AquaHideout_1F/B1F`, `scenes/SlateportCity*.inc`, `Route110.inc`, `Route110_Grunt1.inc`, `PetalburgWoods.inc`,
`RustboroCity.inc`, `RusturfTunnel_Ch3.inc`/`0268_room_RusturfTunnel.s`, `Route112/119/121.inc`, `1126/1128_room_Route119_WeatherInstitute_*`, `SootopolisCity.inc`,
`0358_room_SeafloorCavern_Room1.s`, `0442_room_Underwater_SeafloorCavern.s`, `0356_room_LilycoveCity_CoveLilyMotel_1F.s`, `0194_room_FallarborTown_House1.s`.

## 5. Work packages
| WP | Scope | Size | Needs | Parallel with |
|---|---|---|---|---|
| **WP0 Infrastructure** (Opus) | `version.py`, `versions.json`, `hoenn_version.inc`, loaders with `ruby/` overlay (`scripts, text, encounters, trainers, sprites, interiors`), `-D HOENN_RUBY`, version table in `title`, `weather`, `roamers`, output dirs, `world.py:533` door filter, `models_cave` variant hook, `story_build.sh`/`rebuild_slice.sh` pass-through, tests 1-2 | about 28 files (2 new + a test script; edits of 5-30 lines each): converters `gen_trainers level_scaling gen_encounters gen_caves sapphire_data gen3text allocate_zones`; patches `scripts text encounters trainers sprites interiors story title weather roamers`; `world.py build_rom.py title_art.py ship_hideouts_rooms.py sprite_upgrade.py models_cave.py`, the two build scripts | **do not start while the zone-rectangle work edits `world.py`** (RESUME order: release -> zone rectangles -> Ruby); also cover the patches v15 adds (`trade_evos`; `roamers` is not yet in the patch list of `rebuild_slice.sh`) | nothing; blocks WP1-3 for the helper API only. Smallest package by content, but it touches the files every chapter builds with |
| **WP1 Data and text** (Sonnet) | `gen_ruby_text.py`; trainers (28, classes, 0383/0485, messages); 33 encounter files; place name; `PIC_SPRITE/KEEP_CLASS` Magma rows; roamer/TV data | 1 new script, 7 generator edits, about 33 + 28 generated files, 161 text lines in 36 files | WP0 helper; sprite slot decision (152/153 reuse) | WP2, WP3, WP4 |
| **WP2 Scenes** (Sonnet, one agent) | the 7 scenes of section 4; run each team scene with the chapter test switches on the Ruby ROM (about 14 `*_test.inc` files exist) | about 8 files edited, about 25 scenes re-tested | WP0, WP1 text | WP3, WP4 |
| **WP3 Maps** (Opus) | Magma Hideout: `--magma` zone files (228/231/234), 3 room scripts+text (copy Aqua's, Magma geometry/ids/triggers, 7+ trainers incl. Tabitha), door filter check, Electrodes/items; Room 9 variant (65 collision tiles); B4F variant (visual); Lilycove check; cave/room checkers | 3 rooms (about 12 new files), 2 cave variants, about 6 existing files; the heaviest part | WP0 (`world.py` filter, `models_cave` hook) | WP1, WP2, WP4 |
| **WP4 Art** (Opus/image agent) | Tabitha + Courtney: `sprite_upgrade.py` CHARS entries, `tabitha_frame`/`courtney_frame` (as `matt_frame`/`shelly_frame`, lines 509-560), battle fronts (slots 152/153 overlay) + overworld sheets (codes 88/92 overlay), review sheet; the swap overlay (293/294/353/302/192/303); Ruby title logo + strip | 4 sprites, 2 title images, 1 script | none (can start now; slot plan above) | everything |
| Integration (lead) | build, test 1-4, savestates if the layout differs, per-scene walk, release patch | one pass | all | - |

## 6. Risks and open questions
- **Savestate/ROM layout**: all padded archives keep their `RESERVE` size (checked list in `build_rom.py:27`), but archives not in it must keep their size too: trainer messages (`a/0/8/9`, `a/0/9/0`: same record list per twin, asserted in WP1), title NARC (padded inside to 24436 B: the Ruby logo must fit 512 tiles and one palette), zone entities, sprite tables. If test 2 fails, remake `work/emu/base_*.dst` for Ruby (about 90 s each, `make_states.py` with an output folder). A save made on one ROM is not portable to the other (same flags, different teams): say so in the release notes.
- **System text slots** (`patches/text.py fixed_slots`: vanilla + 1/16 + 64 bytes): 0381 is 20% under vanilla (136k vs 172k chars), 0382 +176 vs 466 allowed, 0383 +28 vs 174, 0485 +86 vs 191 (characters; checked); Ruby adds a few characters (Tabitha +3, Courtney +2, Magma +1), so no risk. Script text `a/0/0/3`: ours about 0.57 MB of a 1 MB reserve, Ruby +157 characters.
- **Text boxes**: Black 2 breaks lines at Sapphire's `\n`; the Ruby twins come with their own breaks and are not wider (43 vs 49). Add a width check to the census.
- **Sapphire regressions**: the infrastructure touches loaders every chapter uses; test 1 (identical SHA-1) is the guard. The working tree is shared with running agents.
- **Hideout geometry**: Magma B1F is 62x24 (Aqua 51x24): chunk count and the 32-models-per-chunk limit (`INTERIORS.md`: "MagmaHideout_B1F's crates are wall"); B2F triggers differ; Electrodes and items at other tiles.
- **Room 9 layout** changes collision in 65 tiles (surfable water vs land basin?): [unchecked] how the Sapphire recipe/`rooms_check` treat that pool; check before estimating.
- **Open for the user**: (1) Groudon's drought: Black 2 has no harsh-sun weather id in the table I read (ids above); options: plain sun (no visible effect), a haze id 9-14, or sandstorm: needs a look test. (2) Ruby title logo: new art again (same permission as the Sapphire logo)? (3) Two release files (`HoennB2_Sapphire` / `HoennB2_Ruby`)? (4) Good-team scenes show the *other* team (Aqua in Ruby's Meteor Falls/Chimney): confirm that is wanted (it is pokeruby's behaviour).
- **Not checked**: that Black 2's Groudon front still (7660/7678) and field model 4512 render; the Black 2 weather ids 9-14; savestate interchange (reasoned from `RESERVE`, not tested); full text diff of every Ruby branch against ours beyond the exact-line match; effort numbers are file counts, not measured.
- Decisions to record when approved: the Ruby build flag, and that the Magma Hideout is installed in the Ruby ROM only (supersedes "Magma Hideout not installed", DECISIONS 2026-10-06, for Ruby). Order in `RESUME.md`: v15 release -> zone rectangles -> Ruby.
- Reproduce: the twin test is a read-only Python snippet over `converter/gen_trainers.load_texts()` and `gen3text.convert(expand=True)` (scratch); trainer/wild/layout diffs are pure reads of `trainers_en.h`, `trainer_parties.h`, `wild_encounters.json`, `layouts.json`/`map.bin`.

## WP0 layout (ruby_infra, 2026-10-08): the contract for WP1-WP4
Switch: `HOENN_VERSION=sapphire|ruby` (unset/empty = sapphire, anything else stops). Only `b2tools/version.py` reads it; every tool asks
`version` (`VERSION`, `is_ruby()`, `POKERUBY`, `SUFFIX`, `EXPAND_VERSION`, `TABLE`, `resolve_ifdef()`, `overlay()`, `overlay_dir()`,
`load_json()`, `room_in_version()`, `build_dir()`). Converters reach it through their existing `sys.path.insert(0, ROOT/b2tools)`.

**Overlay rule**: a `ruby/` folder next to the shared files. In a Ruby build a file in `ruby/` with the same key replaces the shared
one, a new key is added, all else is shared. Key = the leading number (`NNNN_` of sources, `<n>-` of sprite folders, `<zone>.json`).
Sapphire never reads `ruby/` (the loaders' globs are not recursive), so it stays byte-identical. Generators write Ruby output with
`version.overlay_dir(d)` (= `d/ruby` when ruby) and write only the files that differ from Sapphire's.

| What | Shared (Sapphire) | Ruby overlay | Loader | Owner |
|---|---|---|---|---|
| field scripts (rooms, zone inits) | `src/field_scripts/NNNN_*.s` | `src/field_scripts/ruby/NNNN_*.s` (Magma Hideout rooms 0456-0469 go **only** here) | patches/scripts.py, `source_for()` | WP2, WP3 |
| scene includes | `src/field_scripts/scenes/*.inc` | none: branch inside with `#ifdef HOENN_RUBY ... #else ... #endif` (`-D HOENN_RUBY` or `-D HOENN_SAPPHIRE`, + `HOENN_VERSION_ID` 1/2); aliases in `src/include/hoenn_version.inc` | clang | WP2 |
| script / system text | `src/text/{script,system}/NNNN_*.txt` | `src/text/{script,system}/ruby/NNNN_*.txt` (whole file, same line indices) | patches/text.py | WP1 |
| text line overrides | `src/text/overrides*.json` | `src/text/ruby/overrides*.json` (applied after the shared ones) | patches/text.py | WP1 |
| wild tables | `src/encounters/NNNN_*.s` | `src/encounters/ruby/NNNN_*.s` (same size: asserted) | patches/encounters.py | WP1 |
| trainers | `src/trainers/NNNN_*.s` | `src/trainers/ruby/NNNN_*.s` | patches/trainers.py | WP1 |
| trainer data json | `data/hoenn_trainer_*.json`, `data/sprite_map.json` | `data/ruby/<same name>.json`: only the keys that differ, deep-merged (`version.load_json`) | patches/trainers.py | WP1 |
| overworld sheets | `src/sprites/overworld/<code>-<name>/` | `src/sprites/overworld/ruby/<code>-<name>/` | patches/sprites.py | WP4 |
| trainer fronts / backs | `src/sprites/trainer/{front,back}/<slot>-<name>/` | `src/sprites/trainer/{front,back}/ruby/<slot>-<name>/` | patches/sprites.py | WP4 |
| title logo | `data/title/logo.png`, `strip.png` | `data/title/ruby/logo.png`, `strip.png` (same format, one shared palette, 512 tiles) | title_art.DATA | WP4 |
| title figure / cry / backdrop | `version.py` `_TABLE['sapphire']['title']` | `_TABLE['ruby']['title']`: species 383, still 7660, pal 7678, `at`, `backdrop` (WP4 may tune `at`/`backdrop` there) | title_art.py, patches/title.py | WP0 (WP4 tunes) |
| interior zones | `data/interiors/<zone>.json` | `data/interiors/ruby/<zone>.json` (Magma Hideout 228/231/234 go **only** here) | patches/interiors.py | WP3 |
| rooms per version | - | `data/versions.json` `"rooms": {"AquaHideout_1F": "sapphire", "MagmaHideout_1F": "ruby", ...}` | `version.room_in_version()` | WP0 (WP3 fills) |
| hideout door | Lilycove's Aqua door | same door (same index, `LC_HIDEOUT_WARP 27`), retargeted to Magma 1F in Ruby: `data/versions.json` `"doors"` | patches/hoenn_world.py | WP0 |
| story objects | `data/story/*.json` `model` | add `"model_ruby": N` to an object (Kyogre 4511 -> Groudon 4512, Latios 4510 -> Latias 4509) | patches/story.py | WP2 |
| legend / roamer / orb / weather | `version.py` `_TABLE` (`legendary*`, `island*`, `roamer`, `orb`, `weather`) | `_TABLE['ruby']` | roamers.py, weather.py, hoenn_version.inc | WP0 |
| cave layout variants | `data/cave_layouts/<Map>.json` | `"variants": {"ruby": {...}}` in the same file | models_cave.py hook | WP3 |

Sprite overlay details (patches/sprites.py): a `ruby/` folder with `sprite.json` `{"copy_of": N}` copies the **shared** (Sapphire) folder N,
so swaps need no art copies: e.g. `overworld/ruby/293-magma-grunt-m/sprite.json = {"copy_of": 302}` and `ruby/302-aqua-grunt-m = {"copy_of": 293}`.
A Ruby art folder (Tabitha, Courtney) is a full folder as `sprite_upgrade.py` writes it (`sprite.json` with its own `code`/`side`).
`sprite_upgrade.py` is WP4's: it writes Ruby characters into `version.overlay_dir(SRC/<kind>)`. Done by WP4 (2026-10-08): fronts 152 Tabitha,
153 Courtney; overworld 88/92 and the 6 swaps. **Battle fronts of the Magma classes: WP1 points classes 187/188/189/191/192 at the existing
fronts 154/156/148 through the class table (`data/ruby/hoenn_trainer_classes.json`, deep-merged); no copy_of on fronts 149-151** (agreed with
WP4: both would swap twice).

Outputs: `version.build_dir()` = `HOENN_BUILD_DIR`, else `work/rom_ruby` for Ruby (never `work/rom`). Build a Ruby test ROM as any agent does:
`HOENN_VERSION=ruby HOENN_AGENT=<you> HOENN_SKIP_UNBUILT_ROOMS=1 zsh b2tools/story_build.sh` -> `work/agents/<you>/rom_ruby/hoenn.nds`
(your Sapphire ROM in `rom/` is left alone; `agent_build.sh` does the same). The lead: `HOENN_VERSION=ruby zsh b2tools/rebuild_slice.sh` builds
the shared world and Sapphire files as always (HOENN_VERSION is unset for those steps), then Ruby's overlay generators, then the ROM in `work/rom_ruby`.

Rooms and doors (WP3):
- Magma Hideout: `HOENN_VERSION=ruby python3 b2tools/ship_hideouts_rooms.py` (or `--magma`) writes the 3 rooms' zone files, scripts and text
  **into the ruby/ overlays only** (a Ruby run skips every shared room). Their exit to Lilycove names Sapphire warp 14, which `version.door_alias`
  maps to the one hideout door (warp 6, door index 13 = warp 27 of zone 96). `patches/hoenn_world.py` retargets that door to Magma 1F
  (zone 228, warp 0) in Ruby once `data/interiors/ruby/228.json` exists; `patches/interiors.py`, `story.py`, `trainers.py` leave out the other
  version's rooms (`data/versions.json` `rooms`), so Ruby has no Aqua Hideout and Sapphire no Magma Hideout. The rooms themselves are already
  built in `work/interiors/MagmaHideout_*` (rebuild_interiors.sh builds every recipe). Do not put Magma zone files in the shared
  `data/interiors/`: `world.py` would then add a second door to the shared world.
- Cave layout variants (Seafloor Room 9, Cave of Origin B4F): no new code. A recipe `data/cave_layouts/<Map>_Ruby.json` with `"map": "<Map>"`,
  `"layout": "LAYOUT_UNKNOWN_MAP_..."` and `"alt_of": "<Map>"` (models_cave.py already reads `map`/`layout`, as Shoal Cave's high tide; `alt_of`
  keeps gen_caves.py from giving it a zone) is built by rebuild_interiors.sh; add `"<Map>": "<Map>_Ruby"` to `data/versions.json`
  `room_variants.ruby` and the interiors patch installs it in Ruby (only once built). Keep the room's origin (story objects use the Sapphire room's).

Generators (WP1): pokeruby's `.ifdef` is resolved by `version.resolve_ifdef` (gen_trainers and level_scaling `sapphire_lines` now call it; same
output on all 406 pokeruby scripts); `gen3text.EXPAND` takes the 7 placeholders from `version.EXPAND_VERSION`; wild labels by `version.wild_label_ok`.
With HOENN_VERSION=ruby: `converter/gen_encounters.py` writes `src/encounters/ruby/NNNN_auto_<Map>.s` only for maps whose table lines differ
from Sapphire's (same file ids; the registry is read only); `converter/gen_caves.py` does only that for the caves (`ruby_encounters`: zones,
scripts, text stay shared); `gen_trainers.py` refuses until WP1 adds its Ruby output (a dry run with `HOENN_GEN_OUT=<dir>` works);
`level_scaling.py` refuses (its json already carries every Ruby trainer). `sapphire_data.py` writes to `data/sapphire/ruby/`. Run every other
converter without HOENN_VERSION (their output is shared; story_build.sh's `GEN=1` does).
Place name "Magma Hideout": `src/text/ruby/overrides.json` on the place-name line (`text.py` applies Ruby's overrides after the shared ones,
before the place names' setdefault), no allocate_zones.py change needed.

### WP0 results (ruby_infra, 2026-10-08)
- Test 1: HEAD 97333f5 built from a clean copy: `51d57ac0f3af3138e8c88dd5e4fd5e06b43590e4`; the same HEAD + WP0, `HOENN_VERSION` unset and
  `=sapphire`: the same SHA-1. The Sapphire runs of gen_encounters, gen_caves and ship_hideouts_rooms write byte-identical files with and
  without WP0 (and the two `sapphire_lines` copies equal `version.resolve_ifdef` on all 406 pokeruby scripts).
- Test 2: `b2tools/rom_layout_diff.py SAPPHIRE RUBY --content`: header tables, FNT, FAT (662 files) and OVT (344 overlays) identical (Ruby =
  WP0 + WP4 art + the generated Ruby wild tables + the Magma Hideout rooms). Ruby's changes sit inside padded files: a/0/0/2, 3, 8, 9, 0/1/2,
  0/4/8, 0/5/6, 0/7/1, 1/2/6, 1/2/7, 1/7/5, 2/2/6 (RESERVE), a/0/2/6 (title.py pads to Black 2's size: 912 B spare in Ruby's), a/1/0/9 (same
  size). Code: ov162 (cry 383) recompressed to the same size; arm9 4 bytes smaller (boot only, not in the FAT). **Watch ov162**: a one-byte code
  change recompresses the whole overlay; it fit this time, but if a later title edit makes Sapphire's and Ruby's ov162 differ in size, the FAT
  differs (states then need a Ruby set).
  Since the animated title (title_anim, 2026-10-08; notes/RESEARCH_TITLE.md section 8) this is held on purpose: patches/title.py keeps
  `FILL[version]` bytes of Black 2's dead TitleG3D code (the rest zero) so that dsd compresses ov162 to exactly 15204 B in both versions
  (v15.1's size; with `hoenn_intro`, the other ov162 patch). After any ov162 edit: `HOENN_VERSION=sapphire|ruby python3 patches/title.py
  tune RIG_DIR` (about 2.5 min each, a scratch rig ROM) and update `FILL`.
- Test 3: the Ruby ROM boots to the Ruby title (WP4's logo, Groudon's still and cry) and plays the opening to Littleroot (make_states.py's inputs):
  screenshots/ruby_infra/ruby_title.png, ruby_opening.png.
- Ruby wild tables: 26 files (11 outdoor + 15 caves). The plan's 33 maps minus Mt. Pyre 1F-6F (no wild table in our build at all, Sapphire
  too: status `auto` rooms without an encounter file) and Sootopolis (only the Old/Good Rod slot differs; Black 2's one rod uses the Super Rod
  group). Generate them on the world the committed Sapphire files were made from (zone_edges' world): the shared work/world (00:44) predates
  afd5990 and lets Lilycove/Petalburg borrow route grass, which made 2 extra files.
- Groudon's weather: stand-ins rendered in Sootopolis (Ruby test ROM, HOENN_TEST_CH10=2, the hook's weather id poked per run):
  screenshots/ruby_infra/weather_A_plain_sun_id0.png, weather_B_mist_id9.png, weather_B2_light_haze_id11.png, weather_C_sandstorm_id3.png,
  weather_C2_desert_sandstorm_id12.png, weather_all_ids.png (0, 3, 6, 9-14; 6 = Sapphire's storm for reference). The user picks; then set
  `_TABLE['ruby']['weather']` in b2tools/version.py (0 until then).
- Built: Sapphire `work/agents/ruby_infra/rom_sapphire/hoenn.nds` (51d57ac0…), Ruby `work/agents/ruby_infra/rom_ruby/hoenn.nds` (2ff06a1a…), from
  `work/agents/ruby_infra/rtree` (HEAD + WP0 + WP4's art + the generated overlays, for WP1/WP3 to compare: src/encounters/ruby/ 26 files,
  data/interiors/ruby/228,231,234.json, src/field_scripts/ruby/0456/0462/0468, src/text/script/ruby/0290/0293; none of these are in the shared
  tree). The Lilycove door in that ROM: Sapphire warp 27 -> zone 2 warp 0, Ruby -> zone 228 warp 0; Magma 1F's exit -> (96, 27) (read back
  from both ROMs' a/1/2/6).
- For WP2 (from WP4): Groudon's field model 4512 (a/0/4/8 file 771, 6 frames of 64x64 like Kyogre's 770) renders; its a/2/0/8 record has
  sceneNodeType 10 where Kyogre's and the Latis' have 11: check it in the Cave of Origin B4F scene.

### WP2 results (ruby_scenes, 2026-10-08)
Corrections to this note: (1) Ruby's Magma Hideout B2F has **no Groudon scene**: pokeruby's `MagmaHideout_B2F` only repeats AquaHideout_B2F's labels, so it is the same
submarine escape with Tabitha (the other legendary scenes are Room 9 and Cave of Origin B4F); (2) the island legendary of Ruby is **Latias**
(`constants/version.inc`: SPECIES_LATIAS_OR_LATIOS = Latias in Ruby; the roamer is Latios), not Latios.
- Switch: every scene file below stays assembly-identical for Sapphire (binary SHA of the 6 changed script files unchanged, Sapphire ROM byte-identical, see below);
  Ruby reads the version-neutral names of `src/include/hoenn_version.inc` or `#ifdef HOENN_RUBY`.
| Scene | File | Ruby |
|---|---|---|
| Magma Hideout B2F | `src/field_scripts/ruby/0468_room_MagmaHideout_B2F.s` (story part), `src/text/script/ruby/0293_*.txt` lines 1-2, `data/story/ruby/ruby_scenes.json` (Tabitha (8,19) model 88, grunts (31,11) and (13,3), 4 triggers (4..7,16) as one 4x1 trigger) | new scene: the exclamation turns Tabitha UP, after the battle she turns RIGHT and the shadow (object 3, no sprite) leaves right |
| Seafloor Room 9 | `0380_room_SeafloorCavern_Room9.s` | names only (R9_EVIL_LEADER ...), `TRAINER_SEAFLOOR_CAVERN_GRUNT_5`; Groudon = `model_ruby` 4512 in `data/story/ch10.json` (uids 1, 7); layout + glow colour not scripted (below) |
| Cave of Origin B4F | `0206_room_CaveOfOrigin_B4F.s` | `SPECIES_GROUDON_OR_KYOGRE` (cry, battle), `model_ruby` 4512 |
| Route 128 | `scenes/Route128.inc` | `#ifdef HOENN_RUBY`: `special sub_807E25C` = `FadeOutWhiteQ` + slow `FadeInWhite` before the leaders' scene |
| Lilycove entrance | `scenes/LilycoveCity.inc` (comment only) | nothing to change: the cave mouth is terrain, the door is the same world.json door (LC_HIDEOUT_WARP 27), retargeted to Magma 1F by WP0; checked in the ROM (zone 96 warp 27 -> zone 228 warp 0, back to (96,27)) |
| Southern Island | `scenes/SouthernIsland_Interior.inc` | `SPECIES_LATIAS_OR_LATIOS`, `model_ruby` 4509 in `data/story/ch13.json` |
| Mt. Pyre orb | `scenes/MtPyre_Summit.inc`, `MtPyre_Summit_Ch10.inc`, tests `ch10_test.inc`, `ch8b_test.inc` | `ITEM_RED_OR_BLUE_ORB` |
- Gaps (Black 2): Sapphire's/Ruby's coloured glow (sub_80818A4: red for the Red Orb, blue for the Blue Orb; Room 9 Sapphire red / Ruby blue, B4F Sapphire blue / Ruby red) is
  the one white flash in both versions (Black 2's fades have no colour); Ruby's Route 128 brightening (sub_807E25C) is a white-out and a slow fade-in; Black 2's Groudon has the
  ability Drought in battle (the battle shows "The sunlight turned harsh!"), as Kyogre's Drizzle.
  Groudon's field model 4512 (a/0/4/7 record sceneNodeType 10, Kyogre's 11) renders and moves like Kyogre's in Room 9 and B4F (WP4's open question): no change needed.
- Tested on the Ruby ROM (proof: `screenshots/ruby_scenes/`, 01-24): Room 9 -> Route 128 (Maxie, Groudon asleep and rising, Archie and Aqua grunts, orange sand haze weather 3, glare), Cave
  of Origin B4F (Red Orb text, Groudon Lv 49 battle, "settled into sleep again"), Mt. Pyre both scenes (Maxie takes the Blue Orb, Red Orb handed out and back), Southern Island (Latias Lv 55),
  Magma B2F (Tabitha, battle, escape lines, a grunt), Lilycove plaza grunt (Magma), Mt. Chimney (Maxie, Tabitha, Aqua grunts). Method: one built ROM, then
  `work/agents/ruby_scenes/tools/quickpatch.py` re-assembles scene files into it with the chapter's test switch (HOENN_TEST_CH10 / CH8B / CH13 / CH8A / CH5) and a
  copy of Littleroot's sign script that runs the start state and warps (`tools/mk0778.py`); states: `tools/make_base.py` (own base state of each ROM).
- Sapphire: HEAD f0d0624 and HEAD + these files (the ruby/ overlay files too) built from clean snapshot trees give the same ROM, SHA-1 `42d8c008d08a16736300e4d29e88de11836ebae2`.
- Findings for the lead: (a) **savestates carry arm9**: `work/emu/base_*.dst` hold the Sapphire ROM's arm9 (weather patch id 6, trainer class tables), so on a Ruby ROM Groudon's
  weather showed the thunderstorm; make base states from the Ruby ROM (60 s) for any Ruby test; (b) on both ROMs the ch10 test party of `Test_Ch10Start` (Tyranitar + Swampert added in the
  zone init of Room 9) crashes the emulator when Archie_2 / Maxie_2 sends out the first Pokémon (a G3D render call through a NULL state); a lead lent by the town-sign script
  (Swampert or Tyranitar alone), the other Room 9 trainers and the same trainer in Littleroot do not crash: a test-party problem, not a Ruby one, not understood; the ROM scenes were
  run with `HOENN_TEST_CH10_SKIP=1` (trainer counted as beaten) for the rest of the scene and with a Swampert lead for the battle start.

### WP1 results (ruby_data, 2026-10-08): data and text
Run after `gen_map_content.py`; all three are idempotent and have `--check` (nothing written, exit 1 when the committed files are stale):
`python3 converter/gen_ruby_text.py`, `HOENN_VERSION=ruby python3 converter/gen_trainers.py`, `HOENN_VERSION=ruby python3 converter/gen_encounters.py` + `gen_caves.py` (WP0's).
`rebuild_slice.sh` (Ruby block) runs them; `story_build.sh` with `GEN=1` and `HOENN_VERSION=ruby` reruns `gen_ruby_text.py`.
- **Text** (`converter/gen_ruby_text.py`, every string pokeruby's own): finds the Ruby twin of each Sapphire line of `src/text/script/*.txt` by (a) the `.else` label of the
  same `.ifdef SAPPHIRE` position (76 pairs, counts equal in all 64 blocks) or (b) the same label expanded with Ruby's placeholders, and writes whole-file copies
  `src/text/script/ruby/NNNN_*.txt` with the line replaced at the same index. 108 Sapphire lines are worded differently in Ruby: **99 lines in 23 script files** here (the same
  lines are 55 lines of 11 `src/text/scenes/*.txt`, which `gen_map_content.py` merges into them; the Aqua Hideout room 0005 is included although Ruby does not install it, so the
  census is clean) and **13 trainer messages** in 0381. The two Cave of Origin B4F lines, the Meteor Falls Archie lines, the Sootopolis rain/sun lines, Mt. Pyre's orbs, the TV news
  ("blue Flying Pokémon", 0619/0621 line 35) all matched exactly: no hand-made Ruby text exists, every team/legend/orb line of ours got its twin (`--report` lists any that would not).
  Also `src/text/ruby/overrides.json`: place-name line 69 "Magma Hideout" (WP0's file was a ruby_infra test copy, not in the tree). Widest changed line 43 characters, +276 characters over all
  99 lines. ruby_maps' `0287/0290/0293` and ruby_scenes' lines are never written by this tool (they have no Sapphire file of the same name).
- **Trainers** (`gen_trainers.py`, Ruby mode): the 28 aliases of constants/version.inc take the **Black 2 id of their Sapphire twin** (registry read only, so scenes, zone scripts, defeat
  flags and `TRAINER_*` names are unchanged: id 44/45 is Matt 1/2 in Sapphire and Tabitha 1/2 in Ruby, 46/47 Shelly/Courtney, 133/134 Archie/Maxie, 640 Hector 1/Hector 2 ...). The
  whole set is generated into a scratch folder and only what differs from the Sapphire files is written: 21 `src/trainers/ruby/NNNN_*.s` (Carvanha/Sharpedo -> Numel/Camerupt,
  Zangoose -> Seviper, the admins' AI flags 7/11 swapped; the 7 grunts with equal parties need no file), `src/text/system/ruby/0381` (13 messages) `0382` (Tabitha, Courtney, Maxie x2: 6 lines)
  `0383` + `0485` (Team Magma, Magma Leader, Magma Admin: 5 + 5 lines), `data/ruby/hoenn_trainer_classes.json` (classes 187/188/189 sprite 154/156/148; 191/192 keep 153/152, which are
  Tabitha's and Courtney's art in `src/sprites/trainer/front/ruby/`; names) and `data/ruby/hoenn_trainer_data.json` (the 28 entries under the Sapphire constant and under Ruby's
  own, so `HOENN_TEST_TRAINER=TRAINER_GRUNT_46+TRAINER_TABITHA_2` works). Asserted: same trainer set, the same scaled levels for each twin (`data/level_scaling.json` already holds all
  Ruby trainers: `level_scaling.py` stays Sapphire-only on purpose), and the same message record list (so a/0/8/9, a/0/9/0 and `hoenn_trainer_msgs.json` are shared).
  `PIC_SPRITE`/`KEEP_CLASS` got the Magma rows (MAGMA_GRUNT_M/F, MAXIE, MAGMA_ADMIN_M/F). `level_scaling.load_aliases` and `gen3text.convert` take an optional version.
- **Wild tables**: 26 Ruby files in `src/encounters/ruby/` (11 outdoor, 15 caves), generated on the current work/world (Sapphire's committed files regenerate byte-identical on it). Against
  the plan's 33: Mt. Pyre 1F-6F (6: no table in our build for either version, status `auto` rooms without an encounter file: a gap in both ROMs, not Ruby's) and Sootopolis (the
  Old/Good Rod slot only; Black 2 has one rod, so nothing differs) make the other 7. The 26 are exactly the plan's list minus those two (Routes 102, 110, 114, 117, 121, 123, 129,
  Jagged Pass, Safari SW, Mt. Pyre Exterior/Summit, Granite Cave B1F/B2F, Fiery Path, Cave of Origin 1F-B3F, Meteor Falls x4, Sky Pillar 1F/3F/5F, Victory Road B2F); each has the same size as its
  Sapphire file (the encounters patch asserts it), Route 102's Seedot slots and Meteor Falls' Solrock slots were read and seen in the emulator.
- **Roamer / TV**: the roamer is Latios Lv 44 in the Ruby ROM (WP0's `version.py` row; the build log says so) and the TV bulletin names the blue Flying Pokémon (text above). The Southern
  Island legendary is Latias in Ruby (`SPECIES_LATIAS_OR_LATIOS`), the roamer the other one: ruby_scenes' note, not the brief, is right.
- **Acceptance** (clean snapshot trees of HEAD c2b2be1 in `work/agents/ruby_data/{base,wp1}`; wp1 = base + WP1's files only): Sapphire SHA-1 before and after
  `42d8c008d08a16736300e4d29e88de11836ebae2` (identical, twice: also after the last edit); Sapphire dry runs of `gen_trainers.py` and the real run of `gen_encounters.py` reproduce every
  committed file byte for byte. Ruby ROM `ee6e37b94834ad3601d3450ddc4f5f904d55a6ef`; `rom_layout_diff.py --content`: **LAYOUT IDENTICAL** (header, FNT, FAT 662, OVT 344; text 0381-0485 fit the fixed
  system slots: a/0/0/2 has 160612 B spare in both). Census of both ROMs' text (a/0/0/2 + a/0/0/3 unpacked): Aqua 93 -> 31 (21 are Aqua Ring/Tail/Jet and Pokémon names, the rest the good-team
  lines), Magma 35 -> 97, Archie 20 -> 13 (all Aqua leader lines), Maxie 13 -> 20, Kyogre 23 -> 12 (Pokémon names and Pokédex text), Groudon 7 -> 16.
- **Emulator proofs** (`screenshots/ruby_data/`, Ruby test ROM with `HOENN_TEST_TRAINER`, `HOENN_TEST_WARP=128,14,30` from Littleroot's sign, `HOENN_TEST_PARTY`, `HOENN_TEST_CH4=1` (its start state
  runs on Route 111 and is not needed here), driven by `work/agents/ruby_data/` states): `magma_grunt_battle.png` (Ruby Grunt 46 = Sapphire Grunt 19, id 36: "Team Magma Grunt", front 154, Numel Lv 15),
  `magma_grunt_f_battle.png` (front 156), `magma_admin_tabitha_battle.png` / `magma_admin_courtney_battle.png` ("Magma Admin Tabitha / Courtney", fronts 152 / 153, their own lines),
  `text_scene_meteor_falls.png` (the Meteor Falls scene: Magma grunts, Archie, "Team Magma" / "Team Aqua" wording, no scene edit), `wild_solrock_meteor_falls.png` (Solrock Lv 14, Sapphire's
  Lunatone slot). Not battled: Maxie (class 189, front 148: the test NPC did not trigger); the class table in the Ruby ROM's RAM reads 154/156/148/153/152 for 187/188/189/191/192.
- Findings for the lead: (1) **a savestate carries arm9**: `work/emu/base_*.dst` hold the Sapphire ROM's `TRAINER_CLASS_RESOURCES`, so on a Ruby ROM every Magma class showed the Aqua front (149)
  until the states were remade on the Ruby ROM (`work/agents/ruby_data/make_states_ruby.py`, 1 min; same finding as ruby_scenes' weather note): Ruby tests need Ruby-made states. (2) The Sapphire
  `hoenn_trainers.h` still names only Sapphire constants; `hoenn_version.inc` keeps the aliases, nothing Ruby-named exists for scenes (they use the Sapphire constant: its id holds the Ruby trainer).
  (3) `sprite_map.json`'s `_trainer_front` rows for the Magma pics still say "Sapphire never battles Team Magma" (documentation only). (4) Mt. Pyre 1F-6F wild tables are missing in both
  versions (see above): the lead may want them for Sapphire too (Shuppet/Duskull are in the real game's tables).

### WP3 results (ruby_maps, 2026-10-08): maps
- **Magma Hideout** (Ruby only, `data/versions.json` rooms): `HOENN_VERSION=ruby python3 b2tools/ship_hideouts_rooms.py` wrote
  `data/interiors/ruby/228,231,234.json` (pokeruby's warps in order, item balls: B1F Master Ball (26,10), Nugget (26,11), Max Elixir
  (14,18), B2F Nest Ball (31,20); furniture signs) and the heads of `src/field_scripts/ruby/0456/0462/0468`; a rerun keeps every story
  part (checked: byte-identical rerun). Story parts (mine, as ch8b's Aqua ones, with the Magma map's objects): 0456 the two door guards
  (FLAG_MT_PYRE_ORB_STOLEN lines, text `src/text/script/ruby/0287` lines 1-4, "Team Magma"), 0462 the two Electrodes (27,10)/(27,11)
  (h_static_battle, FLAG_HIDE_ELECTRODE_1/2_HIDEOUT). Objects: `data/story/ruby/ruby_maps.json` (Ruby-only file name): 1F guards
  (13,19)/(14,19), 1F trainer (20,3) script 3004, B1F trainers (33,3) 3005, (41,17) 3006, (33,19) 3042, Electrodes uids 6/8; pokeruby
  gives the 1F/B1F trainers no hide flag (Aqua's have FLAG_HIDE_GRUNTS_HIDEOUTS), kept so. B2F (Tabitha, its two grunts, the 4
  triggers, lines 1-2 of 0293) is ruby_scenes' (WP2). With B2F's 2 grunts and Tabitha: 7 trainers, as pokeruby.
- **Cave variants**: `data/cave_layouts/SeafloorCavern_Room9_Ruby.json` (LAYOUT_UNKNOWN_MAP_083041B4) and `CaveOfOrigin_B4F_Ruby.json`
  (LAYOUT_UNKNOWN_MAP_082FF894), `alt_of` their Sapphire map, installed by `room_variants.ruby`. Both are Groudon's lava pools in
  Ruby (metatiles 0x35f/0x364 + edges 0x365-0x367, 0x370-0x373: rendered, `screenshots/ruby_maps/layout_*`). Room 9: the 65 walkable
  water tiles of the basin (x 13-23, y 33-41) are solid lava (0x01/0x81), every floor tile unchanged; B4F: no collision change. Drawn
  as a `pools` entry with a metatile list and `look_over` = Reversal Mountain's lava (notes/CAVES.md "Other recipe keys"; opt-in
  builder keys in models_cave.py / models_cave_levels.py: all 72 older cave recipes rebuild byte-identically, checked).
  `converter/gba.py layout_grid` reads width*height blocks: UnknownMap_082FF894/map.bin has one extra trailing block (the game ignores it).
- **Checkers** made version-aware (`HOENN_VERSION=ruby` reads `data/interiors/ruby/`, `data/story/ruby/`, Ruby's door alias):
  rooms_check.py, rooms_check_more.py, caves_check.py, check_exits.py (Sapphire output unchanged, checked). Ruby counts: caves_check
  abcefhistwx 2 (t) rim fades (the accepted class; Sapphire's own rooms have the same); rooms_check 12, all Magma B1F and all in the lead's
  report since the recipes were built (2 b: pcdesk02_2 over (38,17)/(38,19); 9 f: east panel grid's warp01 rings 0.97 from the inner
  walls' south faces; 1 h: black at (18,17)-(18,18)): generator polish for ship_hideouts_rooms.py, not done; check_exits 0 outdoor
  exits differ (575 room, 300 outdoor); npc_check 0 over a limit (228: 3, 231: 8, 234: 4 NPCs).
- **Tested** (DeSmuME, Ruby test ROM with a kit that lives only in my tree, `screenshots/ruby_maps/01-08`): Lilycove's cove door
  surfing in -> Magma 1F (surfing arrival) -> past the guards' stairs -> 1F stairs -> B1F -> panel (8,5) -> (14,8) -> stairs ->
  B2F; B1F Electrode battle (Lv 30) and the Master Ball; the 1F grunt spots the player; B2F panel (17,13) -> (12,13), Tabitha's
  notice at (5,16); Room 9 and B4F in lava, blocked, their scene triggers still fire. Note for tests: Lilycove's zone init moves the
  hideout door off the map once the Mind Badge is owned (test kits that give 8 badges see a dead door).
- Sapphire: 42d8c008... before and after (HEAD e0e67ca + my files, my snapshot tree); Ruby 806d75ab...; rom_layout_diff: LAYOUT
  IDENTICAL (14 files differ inside padded entries). Door check (a/1/2/6 read back): zone 96 warp 27 -> Aqua 1F (Sapphire) / Magma
  1F (Ruby), one hideout door each; Magma 1F exit -> (96, 27). Chunks: Magma 1F 30,184 B, B1F 28,120, B2F 23,832, B4F Ruby 37,912,
  Room 9 Ruby 82,152 (Sapphire's 80,808).

### Ruby glitch check (check_ruby, 2026-10-08): Magma Hideout, Room 9 / B4F Ruby layouts
Built from a snapshot of e3555cd + the two files below (`work/agents/check_ruby/tree`, own interiors copy); proofs `screenshots/check_ruby/01-12`.
- **Fixed in `b2tools/ship_hideouts_rooms.py`** (only `data/interior_layouts/MagmaHideout_B1F.json` changes; `--recipes` regenerates the
  other 14 recipes, Aqua's included, byte-identically; zone files, scripts and texts unchanged, checked with a Ruby rerun):
  (b) `FAC_CONSOLE` + 0x248 (the left half of B1F's computer-less desk (37,18): it was a wall block and the right half a desk turned
  along z over (38,17)/(38,19)); `FAC_CARPET` + 0x240 ((37,17) was a metal patch in the carpet); (f) `hideout(..., banks=)`: B1F's three
  rock mounds in the east panel grid get 4-unit rims on their north/south edges (0x3E2/0x26D/0x26F/0x079) like their west/east ends,
  not 16-unit inner-wall blocks whose south faces stood 0.97 units from the warp01 rings (the rings reach 3 units into the next tile);
  B1F only, since Aqua/Magma 1F use 0x26D/0x26F along their south walls; (h) inner-wall junctions: a thin-wall tile with an inner-wall
  tile (not floor) on one side, B1F (18,17)-(18,18), joins the inner walls (the builder's rule again with the first pass counted as
  floor, as rooms_check_more (h) does); only rooms that have one get an explicit `inner_walls.tiles` (only B1F), the builder is untouched.
  B1F chunks 22,892 / 28,108 -> 22,668 / 25,388 B.
- **Checkers (Ruby)**: rooms_check (a-l, incl. rooms_check_more): Magma 12 -> 0 (2 b, 9 f, 1 h); the other 21 lines are the lead's known
  ones (Corridors_B1F stairs, Fortree/Hall of Fame notches, Steven's balls, Day-Care/Devon doorways), identical in a Sapphire run. With
  `--rom` (Ruby ROM): no Magma finding; Aqua's (i)/(g)/(e) rows are expected (Ruby does not install zones 2/5/10). caves_check abcefhistwx on
  Room 9 / B4F, both layouts: only the accepted (t) rim fades (Room 9 Ruby 42 faces vs Sapphire's 35: 4 more rim cells at (24-26,27-29)
  in the rock, from the changed wall art). check_exits 0 outdoor differences; npc_check 0 over a limit (build log).
- **Emulator (Ruby ROM, kit with file 778 padded, see TESTING.md)**: Lilycove door (6 badges) -> 1F surfing in -> B1F: both Electrodes
  (battle), Master Ball, Nugget, Max Elixir; **every warp panel and stairs of B1F (28) and B2F (8), 55 traversals, each arrival on the
  pokeruby destination tile**; trainers spot and battle (B2F (13,3), B1F (33,19)); B2F: the notice, Tabitha's battle (Ruby party), her
  lines, talking again; out B2F -> B1F -> 1F -> surf -> Lilycove. B4F Ruby: all 36 tiles (not the warp (12,5) and the awakening trigger (9,13)), 80 moves,
  60 bumps into the lava/rim: none walkable; Room 9 Ruby: all 227 reachable tiles (not the warp (5,4), the trigger (17,42), the story
  people's and the ball's tiles), 694 moves, 36 bumps around the lava: none walkable; Groudon stands in the lava in both.
- **Accepted / for the lead** (not Ruby-specific): (1) in the mist zones (Cave of Origin B2F-B4F, Room 9; fixed_weather, the same zones in
  both versions) the background past the map's edge is the fog's light blue instead of black, and 1-pixel T-junction cracks / specks in
  the rock tops show light blue (Room 9 around rows 31-32, x 9-15: `12_room9_crack_lines_in_mist.png`); the cave builder's known
  "T-junction cracks not checked" class (CAVES.md), only visible against the light background. (2) B1F's crates stay walls (black tops,
  ship_hideouts' 32-models-a-chunk decision; set 379 has no crate texture). (3) Room 9 Ruby lacks Sapphire's two drock02 boulders at the
  pool's NE rim (Ruby's wall art there differs) and its pool corners get the builder's rim stones: cosmetic. (4) The Tabitha notice only
  turns her (pokeruby too); the battle starts when you talk to her.
- Layout: `rom_layout_diff.py` Sapphire vs Ruby (both from this tree): LAYOUT IDENTICAL. Sapphire is unaffected by construction: the Magma
  rooms are Ruby-only (versions.json), and the shared generator change leaves every Aqua/ship recipe byte-identical (above).
