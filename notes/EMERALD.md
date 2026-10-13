# Pokémon Emerald NDS: the third version of HoennB2 (emerald_wp0, 2026-10-12)

Emerald is built from the same tree as Sapphire and Ruby (decision 2026-10-11, notes/EMERALD_PLAN.md option (a)):

    HOENN_VERSION=emerald zsh b2tools/rebuild_slice.sh          (the lead: world_emerald + rom_emerald)
    HOENN_VERSION=emerald HOENN_AGENT=<you> HOENN_SKIP_UNBUILT_ROOMS=1 zsh b2tools/story_build.sh
                                                                -> work/agents/<you>/rom_emerald/hoenn.nds

Read with notes/EMERALD_PLAN.md (what Emerald changes, measured; the phases) and notes/RUBY.md (the overlay machinery
Emerald reuses: "WP0 layout"). The plan's section 4 decisions are in notes/DECISIONS.md (2026-10-11).

## Phase 0 (this note): what an Emerald build is today

**Sapphire's world, story, trainers and rooms, with Emerald's version strings, title figure and wild tables.**
Every map, room, scene, trainer, item and text is Sapphire's; Emerald's own data comes in phase by phase (the TODO
hooks below). What already differs automatically in the Emerald ROM:
- version strings and numbers: `version.NAME` Emerald, `GAME_VERSION` 3 (pokeemerald VERSION_EMERALD), `GAME_CODE`
  BPEE, `PUBLIC_NAME` "Pokémon Emerald NDS", `RELEASE_STEM` Pokemon_Emerald_NDS (metadata for the release kit);
  field scripts are assembled with `-D HOENN_EMERALD -D HOENN_VERSION_ID=3`;
- the title: Rayquaza's cry on Start (species 384; Black 2's still 7680 / palette 7698 for the still and MCSS
  styles); the bottom scene stays Sapphire's Kyogre scene and the logo Sapphire's until emerald_art puts
  `data/title/emerald/logo.png` + `strip.png` in place (patches/title.py falls back to Sapphire's logo, it says so in the
  build log). ov162 is tuned to the same 15,204 compressed bytes as Sapphire's (`FILL` emerald: mcss 332; scene 260
  with Sapphire's scene, which emerald_art retuned to 146 for Emerald's own scene, `title_art.EMERALD_SCENE`);
- **wild tables: pokeemerald's** on the maps Sapphire has: 26 files in `src/encounters/emerald/` (16 outdoor, 10 caves)
  where Emerald's table differs from Sapphire's (the list is in "Results" below); the other tables are the same;
- every Emerald overlay emerald_art adds (outfits, Steven's back, the NEW-set sheets) is installed by the same
  loaders as Ruby's: `src/sprites/<kind>/emerald/`, `src/sprites_gen5/<kind>/emerald/`.

## How the version works

`b2tools/version.py` is the only reader of `HOENN_VERSION` (sapphire | ruby | emerald). Besides Ruby's API it has:

| Name | What |
|---|---|
| `EMERALD`, `is_emerald()` | the switch |
| `OVERLAY` / `OVERLAYS` / `has_overlay()` | the version's overlay folder: None (Sapphire), `ruby`, `emerald`. `has_overlay()` = "a version whose generators write only what differs from Sapphire's, into its own folders" (Ruby and Emerald). Code that meant "not Sapphire" now asks `has_overlay()`; code that means Ruby's content (Magma as the villain, Groudon) still asks `is_ruby()`, so Emerald gets Sapphire's there |
| `DECOMP`, `decomp(v)` | the version's decomp: external/pokeruby (Sapphire, Ruby) or external/pokeemerald (Emerald) |
| `decomp_map(name, v)` | the map folder of the version's decomp that plays Sapphire map `name` (Emerald's renames, data/versions.json "maps"); None for a map Emerald dropped |
| `gba_dump(v)` | the user's own cartridge dump of the version (roms/emerald_original.gba for Emerald; Sapphire's for Ruby, whose songs are the same) |
| `world_dir()` | HOENN_WORLD_DIR, else work/world (Sapphire, Ruby) or work/world_emerald (Emerald) |
| `build_dir()` | HOENN_BUILD_DIR, else work/rom, work/rom_ruby, work/rom_emerald |
| `wild_label_ok(label, 'emerald')` | every label (pokeemerald has one table per map, no `_Sapphire`/`_Ruby` suffix) |
| `EXPAND_VERSION` (emerald) | pokeruby's placeholders as Sapphire's (VERSION = EMERALD) plus pokeemerald's own fixed ones ({AQUA} {MAGMA} {ARCHIE} {MAXIE} {KYOGRE} {GROUDON}, charmap FD 08-0D) for gen3text |
| `_TABLE['emerald']` | legendary/island/roamer/orb/weather: **Sapphire's values until phase 3** (Kyogre, Latios on the island, Latias roaming, Blue Orb, thunderstorm); title: species 384, still 7680, pal 7698, `data/title/emerald` |
| `resolve_ifdef` | pokeruby's `.ifdef SAPPHIRE` branch for Emerald (where Emerald still reads pokeruby) |

`data/versions.json`:
- `rooms`: a room's versions as a string or a list. The Aqua Hideout is `["sapphire", "emerald"]` (Emerald has it);
  Ruby's Magma Hideout (1F/B1F/B2F) stays `"ruby"` (Emerald's hideout is other maps, below).
- `maps.emerald` (written by `converter/gen_emerald_maps.py`, `--check` to test): `alias` (43 Sapphire folders Emerald
  renamed: Underwater1 -> Underwater_Route124, CaveOfOrigin_B4F -> CaveOfOrigin_B1F, Sapphire's Magma Hideout ->
  AquaHideout_UnusedRubyMap1-3, ...), `gone` (7: three contest lobbies/halls, LilycoveCity_EmptyMap), `new` (131
  Emerald-only maps in 12 groups: battle_frontier 58, event_islands 27 (already in HoennB2), battle_tents 9,
  magma_hideout 8, trainer_hill 7, terra_marine_cave 5, mirage_tower 4, underwater 3, artisan_cave 2, safari_expansion
  2, mystery_events_house 2, other 4: DesertUnderpass, EverGrandeCity_PokemonLeague_2F, MeteorFalls_StevensCave,
  UnionRoom), `name_clash` (3 Emerald-only maps whose folder name is a different Sapphire/Ruby map: MagmaHideout_1F,
  SafariZone_Northeast, SafariZone_Southeast), `ground` (118 kept maps whose Emerald blocks differ, 28 of them resized:
  the phase-2 work list).
- `doors.emerald`, `room_variants.emerald`: none yet (the hooks Ruby uses: phase 2).

### Overlay folders (Emerald's; the rule is Ruby's: same key = replaces, new key = added)

| What | Shared (Sapphire) | Emerald overlay | Loader |
|---|---|---|---|
| field scripts | `src/field_scripts/NNNN_*.s` | `src/field_scripts/emerald/` | patches/scripts.py |
| scene includes | `src/field_scripts/scenes/*.inc` | none: `#ifdef HOENN_EMERALD` first, then the Ruby/Sapphire test (`src/include/hoenn_version.inc`) | clang |
| script / system text | `src/text/{script,system}/NNNN_*.txt` | `src/text/{script,system}/emerald/` | patches/text.py |
| text line overrides | `src/text/overrides*.json` | `src/text/emerald/overrides*.json` | patches/text.py |
| wild tables | `src/encounters/NNNN_*.s` | `src/encounters/emerald/` (generated, same sizes) | patches/encounters.py |
| trainers | `src/trainers/NNNN_*.s` | `src/trainers/emerald/` | patches/trainers.py |
| trainer data json | `data/hoenn_trainer_*.json`, `data/sprite_map.json` | `data/emerald/<same name>.json` (deep-merged) | version.load_json |
| overworld / fronts / backs | `src/sprites/<kind>/<n>-<name>/` | `src/sprites/<kind>/emerald/` (emerald_art: Brendan/May outfits 0/1, 231-236..., Steven's back 5) | patches/sprites.py |
| NEW (Gen 5) set | `src/sprites_gen5/<kind>/` | `src/sprites_gen5/<kind>/emerald/` (new: scanned only with HOENN_SPRITES_GEN5, i.e. by sprite_switch's NEW set; it wins over the classic Emerald folder, which wins over the shared NEW one) | patches/sprites.py |
| title logo | `data/title/logo.png`, `strip.png` | `data/title/emerald/` (emerald_art) | title_art.DATA |
| interior zones | `data/interiors/<zone>.json` | `data/interiors/emerald/` | patches/interiors.py, zone_effects, hoenn_world, checkers |
| story objects | `data/story/*.json` (`model`) | `data/story/emerald/<name>.json` replaces a file; `"model_emerald": N` on an object | patches/story.py |
| room variants | `data/cave_layouts/<Map>.json` | `<Map>_Emerald.json` with `alt_of` + `room_variants.emerald` | patches/interiors.py |
| map plans | `data/plans/<Map>.json` | `data/plans/emerald/<Map>.json` (every Emerald plan, from pokeemerald) | version.plan_path (world.py, outdoor_check) |
| metatile labels | `converter/metatiles.json`, `data/labels/gTileset_*.json` | `data/labels/emerald/carry_<ts>.json` (generated) + `<ts>.json` (by eye); Emerald's tilesets take only these | converter/plan_map.py |
| world settings | `data/hoenn_world.json`, `hoenn_standalone.json`, `hoenn_zones.json`, `hoenn_interiors.json`, `hoenn_weather.json` | `data/emerald/<same name>.json` (deep-merged) | version.load_json (world.py, allocate_*, fixed_weather) |
| map additions | `data/hoenn_map_additions.json` | `data/emerald/hoenn_map_additions.json` (replaces it: `crop`, layouts, `warps`, events) | gba.world_repo |
| town settings | `data/towns/<Map>.json` | `data/towns/emerald/<Map>.json` (deep-merged; a new map's own; `prop_moves`, `retile`) | world.py load |

The empty folders carry a `.gitkeep` (no loader reads it). Sapphire's and Ruby's builds never read `emerald/`.

### Builds
- `rebuild_slice.sh`: `HOENN_VERSION=emerald` puts the world in **work/world_emerald** (HOENN_WORLD_DIR wins; phase 0
  builds it from Sapphire's maps), runs the shared generators as always, then Emerald's block: `gen_encounters.py` and
  `gen_caves.py` in Emerald mode (src/encounters/emerald/), `gen_trainers.py`'s Emerald report (writes nothing), then the
  ROM in **work/rom_emerald**. Interiors stay shared (`work/interiors`): Emerald's rooms come as variants (phase 2).
- `story_build.sh` / `agent_build.sh`: `rom_emerald/`; story_build reads work/world_emerald, or work/world while that
  is not built (phase 0: the same maps). `build_rom.py` does the same when HOENN_WORLD_DIR is unset.
- `rebuild_interiors.sh` (fixed in passing): `O` is made absolute; the truck step runs in b2tools/ and wrote the truck
  into `b2tools/work/interiors/truck` while ToNsbmd converted the old `work/interiors/truck` (harmless while that old one
  existed and matched; a fresh tree failed). Output unchanged (the regression builds below).
- Savestates: an Emerald ROM needs its own (savestates carry arm9: RUBY.md WP2/WP1 findings); phase 0's layout matches
  Sapphire's (title FILL tuned), but test with states made on the Emerald ROM.

### Readers (the generators' Emerald inputs)
| Generator | Emerald mode | Writes |
|---|---|---|
| `converter/gen_encounters.py` | `wild_tables('emerald')`: pokeemerald gWildMonHeaders, per Sapphire map through `decomp_map` | `src/encounters/emerald/NNNN_auto_<Map>.s` that differ |
| `converter/gen_caves.py` | `sapphire_table(name, 'emerald')` (the same reader); only the wild tables (`ruby_encounters`, now any overlay version) | `src/encounters/emerald/NNNN_cave_<Map>.s` that differ |
| `converter/gen_trainers.py` | pokeemerald's trainers, scripts, texts, maps, money, class names; `emerald_ids` (registry), `PIC_EMERALD` / `EMERALD_CLASS` / `EMERALD_SPRITE`, `SPLIT_EMERALD`, `STEVEN_PARTNER`; `install_emerald` (`--check`) | `src/trainers/emerald/`, `src/text/system/emerald/0381-0383, 0485`, `data/emerald/hoenn_trainers.json` (registry), `hoenn_trainer_data.json`, `hoenn_trainer_classes.json`, `hoenn_trainer_msgs.json`, `src/include/hoenn_trainers_emerald.h` (phase 1) |
| `converter/sapphire_data.py` | `HOENN_VERSION=emerald python3 sapphire_data.py ../external/pokeemerald <Sapphire map> ...` | `data/sapphire/emerald/` |
| `converter/gen3text.py` | Emerald's placeholders (version.py) | - |
| `converter/level_scaling.py` | `emerald_check`: refits the curve on Emerald's parties and wild tables in Sapphire's story order and compares | nothing (the verdict: reuse Sapphire's curve) |
| `converter/gen_items.py` | `main_emerald` (`--check`): item_ball_scripts.inc + map objects, pairs balls by tile; `tutors_emerald` | `data/emerald/hoenn_items.json`, `src/field_scripts/emerald/1240_items.s`, `data/emerald/move_tutors.json` |
| `converter/gen_hidden_items.py` | `main_emerald` (`--check`): map.json bg_events, pairs by flag or tile | `data/emerald/hoenn_hidden_items.json`, `src/field_scripts/emerald/1241_hidden_items.s`, `data/story/emerald/hidden_items.json` |
| `b2tools/shops_data.py` | `main_emerald` (`--check`): pokeemerald's mart of each shop id | `data/emerald/hoenn_shops.json` (no list differs) |
| `converter/gen_dex_text.py` | `main_emerald` (`--install`): pokedex_text.h / pokedex_entries.h, two pages per entry | `src/text/emerald/overrides_hoenn_dex.json`, `src/text/system/emerald/0443_dex_page2.txt` |
| `converter/gen_emerald_maps.py` | (new) the two decomps' maps | `data/versions.json` "maps" -> "emerald" |
| `converter/gba.py` | already reads pokeemerald maps and tilesets (event islands) | - |
| `converter/gen_map_content.py`, `converter/gen_trainer_npcs.py` | Emerald mode written (emerald_s0, notes/EMERALD_STORY.md 2.4.1 S0-1/S0-3): pokeemerald's events, text and trainers on Emerald's world; refuses to run until `work/world_emerald/world.json` exists (dry-run checked on Sapphire's world) | `src/field_scripts/emerald/NNNN_auto_*`, `src/text/script/emerald/NNNN_auto_*`, `data/emerald/hoenn_content.json`, `data/emerald/hoenn_trainer_npcs.json` |
| `converter/plan_map.py`, `b2tools/world.py`, `terrain/*`, `outdoor_check.py`, `walk_diff.py` | through `gba.world_repo()`: Emerald's maps (phase 2, emerald_world) | `data/plans/emerald/`, the world (`work/world_emerald`) |
| `converter/allocate_zones.py`, `allocate_interiors.py` | Emerald mode: only the Emerald-only maps/rooms (never the shared files) | `data/emerald/hoenn_zones.json`, `hoenn_interiors.json` |
| `converter/emerald_labels.py` (new), `emerald_settings_check.py` (new) | labels carried over from Sapphire's; per-map settings checked on Emerald's maps | `data/labels/emerald/carry_*.json`; a report |
| everything else (gen_interiors, ship_hideouts_rooms) | Sapphire's (the shared run); `ship_hideouts_rooms.py` stops in an Emerald run | - |

## TODO hooks (phases 1-5; the code says `TODO EMERALD-<phase>` where it waits)

**EMERALD-1, data** (EMERALD_PLAN.md phase 1): **done by emerald_data (2026-10-12), see "Phase 1 results" below**; what
stays open is listed there. The original task list:
- Trainers: turn `gen_trainers.emerald_report` into an Emerald run that writes `src/trainers/emerald/`,
  `src/text/system/emerald/0381-0383, 0485`, `data/emerald/hoenn_trainer_data.json`, `data/emerald/hoenn_trainer_classes.json`
  (Ruby's install_ruby is the model). The report today: of the 605 Sapphire registry ids, 249 keep the same party in
  Emerald, 144 the same Pokémon at other levels, 161 another party, 50 slots hold another trainer (Emerald reused R/S's
  slots); 250 Emerald slots have no Black 2 id (rematch tiers, new trainers, Frontier). Needs: Emerald's own registry
  for its new trainers (Black 2 has ~33 ids left: rematches out, decision 3A), Emerald's trainer pics
  (TRAINER_PIC_LEADER_ROXANNE ...) in PIC_SPRITE, Magma's classes beside Aqua's (both teams are villains).
- Levels: `level_scaling.py` refuses Emerald: refit with Emerald's trainers or reuse the curve.
- Items, hidden items, marts, tutors: `gen_items.py`, `gen_hidden_items.py`, `shops_data.py` in Emerald mode (map.json
  objects and scripts of `decomp_map(name)`), into overlays.
- Pokédex text: `gen_dex_text.py` from pokeemerald src/data/pokemon/pokedex_text.h -> `src/text/emerald/overrides_hoenn_dex.json`
  and `src/text/system/emerald/0443_dex_page2.txt` (Emerald's entries are one page: check the 3-line window).

**EMERALD-2, world and maps**
- Outdoor world: **done by emerald_world (2026-10-12), see "Phase 2: Emerald's outdoor world" below** (readers, labels,
  the seam, the new outdoor maps; rebuild_slice.sh runs the shared generators on Sapphire's world only and builds Emerald's
  world in its Emerald block; `build_rom.py` / `story_build.sh` read work/world_emerald and only fall back to work/world,
  with a warning, until the lead has built it). Its work list (rooms, models, story) is there.
- Rooms: Emerald's changed rooms as variants (`data/cave_layouts/<Map>_Emerald.json` / interior recipes, `alt_of`,
  `room_variants.emerald`); Emerald-only rooms in `data/interiors/emerald/<zone>.json` with `rooms: {name: "emerald"}`;
  the 3 `name_clash` maps need HoennB2 names of their own (e.g. `MagmaHideout_1F_Emerald`); `gen_caves.py` and
  `ship_hideouts_rooms.py` get Emerald runs (now: wild tables only / stop). Doors: `doors.emerald`.
- Emerald-only maps' wild tables: gen_encounters gives a table to every built map that has one in pokeemerald.

**EMERALD-3, story and text**
- Scenes: `#ifdef HOENN_EMERALD` before the Ruby/Sapphire test; whole rooms in `src/field_scripts/emerald/`;
  `src/text/script/emerald/`; `data/story/emerald/` and `model_emerald`; `gen_map_content.py`/`gen_trainer_npcs.py` in
  Emerald mode (they read pokeruby's scripts today).
- `version.py _TABLE['emerald']` and `src/include/hoenn_version.inc`: both legendaries (Kyogre at Seafloor Cavern,
  Groudon in the Magma Hideout), the Sootopolis weather swap, the Lati choice (island/roamer), the orb.
- `data/hoenn_music.json` `zone_rules.crisis_song`: an "emerald" key (mus_abnormal_weather; until then Sapphire's).
  Done (emerald_art, 2026-10-12): `data/emerald/hoenn_music.json` has it, merged by `patches/hoenn_music._mapping()`.
- **TODO EMERALD-3/4, Emerald's three other zone-music rules** (pokeemerald src/overworld.c GetLocationMusic /
  ShouldLegendaryMusicPlayAtLocation; emerald_art 2026-10-12). Their zones exist in the build, but the story variables
  that switch them do not yet (they come with the Sootopolis sequence and the Space Center scenes), so nothing is wired:
  1. Routes 129, 130, 131 also play the crisis song (mus_abnormal_weather) once `VAR_SOOTOPOLIS_CITY_STATE` >= 4
     (Emerald adds them to the crisis maps; Sapphire's crisis zones are patches/weather.py `crisis_zones`).
  2. Sootopolis City (the city map only) is silent (MUS_NONE) while `VAR_SKY_PILLAR_STATE` == 1 (NoMusicInSootopolisWithLegendaries).
  3. Mossdeep Space Center 1F and 2F play mus_encounter_magma while `VAR_MOSSDEEP_CITY_STATE` is 1 or 2 (Magma holds it).
  How: `patches/hoenn_music.py zone_rules()` + `hoenn_music.c Music_ZoneBGM` (the Weather Institute rule is the model:
  a zone list, a work id from src/include/hoenn.h, a song), Emerald-only rows in `data/emerald/hoenn_music.json`
  `zone_rules`, once the three variables have Black 2 work ids in hoenn.h.

**EMERALD-4, mechanics**: the tag battle, the Sootopolis sequence, Mirage Tower, rotating tiles, the new Regi puzzles,
abnormal-weather caves, two-trainer double battles, move tutors, closed Frontier/Tent/Trainer Hill doors: patches gated
by `version.EMERALD` (no new switch needed). Done 2026-10-12 (emerald_mech): the tag battle, two-trainer doubles, move
tutors, closed doors ("Phase 4 mechanics" below); the others are planned there.

**EMERALD-5, art and music** (emerald_art): done 2026-10-12. Title: `data/title/emerald/logo.png` + `strip.png`
(draft 3), Rayquaza's scene (`title_art.py` "Emerald"), `FILL['scene']['emerald']` tuned, Rayquaza's cry. Sprites:
`src/sprites/*/emerald/`, `src/sprites_gen5/*/emerald/` (b2tools/sprite_emerald.py, sprite_community_emerald.py), Steven's
back on back sprite 5 (the tag battle needs Steven's class pointed at it: EMERALD-4). Music: `b2tools/m4a_emerald.py`
reads the user's Emerald dump; `data/emerald/hoenn_music.json` (4 new songs, 6 shared songs taken from Emerald, slots,
wild 151 (Mew), crisis song, gains; Rayquaza keeps Sapphire's mus_vs_kyogre_groudon: Emerald's mus_vs_rayquaza is the
same music note for note) merged by `hoenn_music._mapping()`, converted by `m4a_emerald.convert_all`;
`music_slots.py` counts the overlay's slots as taken.

**Phase 6**: savestates from the Emerald ROM, release kit with `version.RELEASE_STEM` (Pokemon_Emerald_NDS_v1).

## Results (emerald_wp0, 2026-10-12)

**Regression guard: Sapphire and Ruby build byte-identical to the v16.5 release ROMs.** Method: snapshot trees of HEAD
3bd18ab (= v16.5 + a notes line) under `work/agents/emerald_wp0/` (git archive of b2tools/converter/data/src + links to
external/tools/roms; their own world, interiors, buildings, java and ROM folders), the full `rebuild_slice.sh` run in each
(`work/agents/emerald_wp0/tools/run_slice.sh TREE VERSION`, which points the tree's two `cd` lines at the tree, as
release_vNN.sh does for the lead worktree):

| Build | SHA-1 | v16.5 release |
|---|---|---|
| Sapphire, HEAD unchanged (baseline) | 691d0d8bb18554566d357d709d774a007eca1b98 | 691d0d8b... same |
| Sapphire, HEAD + emerald_wp0's files | 691d0d8bb18554566d357d709d774a007eca1b98 | same |
| Ruby, HEAD + emerald_wp0's files | e86ffd46bec302919b899c1eeb27adb48ff34ea3 | e86ffd46... same |
| Emerald, HEAD + emerald_wp0's files | 7a9538849163f500c9ac91edef680a47ac91a4a1 | (new) |

Also: every generated file of both runs (src/, data/, Ruby's overlays) equals HEAD's except `data/hoenn_content.json`,
which equals the v16.5 release worktree's (~/HoennB2_lead) regenerated copy (finding below); the final
`gen_encounters.py`/`gen_caves.py` (after a cache was added to the Emerald branch) rewrite Sapphire's and Ruby's tables
byte for byte. Checkers: Sapphire and Emerald rooms_check {b 4, e 118, g 1, h 12, k 7, m 18}, caves_check {t 42},
script_check 0 open, walk_diff 713 open (all the same as the baseline); save margin 28,896 B in all three.
emerald_art's later edits of `patches/title.py`, `title_art.py` and `title_scene.c` (made in the main tree after these
builds: Emerald's own title scene) were not part of them: rerun the Sapphire/Ruby SHA-1 check after merging those.

**The Emerald ROM** (`work/agents/emerald_wp0/wp0/work/rom_emerald/hoenn.nds`): `rom_layout_diff.py --content` against
Sapphire's: LAYOUT IDENTICAL (header, FNT, FAT 662, OVT 344); 4 files differ inside their entries: ov162 (Rayquaza's
cry), a/1/2/7 (the wild tables), a/1/7/6 and a/2/9/6 (the Pokédex habitat data hoenn_pokedex derives from them).
work/world_emerald equals Sapphire's world (only batch.txt's paths differ). Booted in DeSmuME (muted): the title (Sapphire's
logo and scene: no data/title/emerald yet in this tree; RAM ov162+0x1B0 = 384, Rayquaza's cry) -> new game -> truck ->
house -> Littleroot: `screenshots/emerald_wp0/emerald_title.png`, `emerald_littleroot.png`; a state outside the house:
`work/agents/emerald_wp0/boot/base_littleroot.dst` (made on the Emerald ROM).

**Emerald's wild tables** (src/encounters/emerald/, generated): 16 outdoor (Routes 101-104, 110-114, 116, 117,
120, 121, 123, Petalburg Woods, Mt. Pyre exterior) and 10 caves (Fiery Path, Meteor Falls x4, Sky Pillar 1F/3F/5F,
Victory Road B1F/B2F). E.g. Route 101 keeps Sapphire's species in Emerald's slot order; Route 103 adds Wingull;
Victory Road has Lairon/Mawile for Medicham/Meditite; Meteor Falls Solrock. Same file ids and sizes as Sapphire's.

**Findings for the lead**
- `converter/gen_map_content.py` regenerates `data/hoenn_content.json` without v165_fixes' hand edit of
  `Route115_EventScript_15092E` ("move": 3, "_move": ...): the committed file has it, the file the v16.5 release was
  built from (the lead worktree after rebuild_slice) does not, so **v16.5 ships without that edit**. Make the generator
  keep it (or put it in the generator's input), then rebuild.
- `rebuild_interiors.sh`'s truck went to `b2tools/work/interiors/truck` (fixed above; the old work/interiors/truck equals
  a fresh one, so no ROM changed).
- pokeemerald renamed 5 trainer classes (COOLTRAINER, RIVAL, PKMN_RANGER, PKMN_BREEDER, PKMN_TRAINER_1:
  gen_trainers.CLASS_EMERALD) and its trainer pics (TRAINER_PIC_LEADER_ROXANNE ...): phase 1 maps the pics.

## Phase 1 results (emerald_data, 2026-10-12)

All five generators have an Emerald run (the Readers table) and `rebuild_slice.sh`'s Emerald block runs them. Sapphire's and
Ruby's generated files are unchanged (each regenerated and compared with HEAD; `HOENN_VERSION=ruby gen_trainers.py --check`).

**Trainers.** Emerald's scripts battle 543 trainers first (rematch tiers left out, decision 3A); with Liza (Tate & Liza are
two trainers, as in Sapphire: Tate Claydol + Solrock, Liza Xatu + Lunatone, so the battle opens with Emerald's two leads) and
Steven as the Space Center partner (pokeemerald battle_tower.c sStevenMons; `TRAINER_STEVEN_PARTNER`, for emerald_mech's
multi battle) the registry has 545. 377 sit in a slot Emerald shares with Sapphire and take that Sapphire trainer's Black 2
id, so Sapphire's NPCs, scenes and defeat flags reach Emerald's trainer of that place; 38 of these slots hold another
person in Emerald (renamed gym trainers, Wallace -> Juan, Steven -> Champion Wallace, but also Mt. Chimney's Matt slot =
Zander, Archie 3 = Leah, Brianna = a Space Center grunt: Sapphire's scenes for those, still in the Emerald build until
phase 3, now battle Emerald's person). The 168 new ones take ids no Emerald trainer uses: Sapphire's 223 rematch-tier ids
(never battled in HoennB2), then the 33 never-given ids. **Black 2 ids left for Emerald: 88** (55 rematch-tier + 33
never given). Names that mean another trainer in pokeruby: `TRAINER_WALLACE_EMERALD` (Champion), `TRAINER_STEVEN_EMERALD`
(Meteor Falls) in the data file and header. Levels: Sapphire's curve (below). Messages: 1,717 of a/0/8/9's 2,326 records.
**Classes**: every picture both games have keeps Sapphire's class; Juan = class 119 with Black 2's Juan (sprite 126),
Champion Wallace = 193 with Black 2's Wallace (140), Steven = spare class 230 (sprite 139, "PKMN Trainer", rival music),
**Team Magma beside Team Aqua**: Maxie 186, Tabitha 195, grunts 235 / 40 (Black 2's Colress/N classes, all in arm9
SPECIAL_TRAINER_CLASSES, so they get the Plasma battle music groups 9/7 like Aqua's; Magma's encounter music via
hoenn_music). Tabitha's front: `src/sprites/trainer/front/emerald/169-tabitha` = Ruby's Tabitha (pixel-identical to
pokeemerald's magma_admin.png) on 152's parts (`mcss_from`), in slot 169 (Black 2's Brycen Jet). Spare classes left: 15.
`b2tools/patches/hoenn_music.py` class_songs: a review row's `music_pic` (Emerald only) names the pokeruby picture whose
songs a class takes (Juan: a leader's, Champion Wallace: the Champion's, Steven: the rival's).
Not placed yet: 19 trainers on Emerald-only maps (Magma Hideout 1F-4F 18, Steven's cave 1) and 29 on Sapphire maps
HoennB2 has not built (Trick House puzzles 2-8, S.S. Tidal): `data/emerald/hoenn_trainer_data.json` "unbuilt". Trainer NPCs
are still Sapphire's (gen_trainer_npcs in Emerald mode is EMERALD-3).

**Levels: Sapphire's curve is reused** (`HOENN_VERSION=emerald python3 converter/level_scaling.py`, report in
work/agents/emerald_data/level_scaling_emerald.txt). Refitted on Emerald's own parties and wild tables, the curve comes out
1 level higher at most levels (2 at a few, e.g. the Champion's ace 64 vs 66), but it keeps Emerald's level gaps only 0.09
level better (rms 0.40 vs 0.50): less than the model's own uncertainty (5 or 20 instead of 10 wild battles per route move
the curve 1-2 levels) and the check leaves out Emerald's extra battles, which would pull a refit back down. One curve for
all three versions; Emerald's wild tables already used it.

**Items.** Item balls: 161 (110 on a Sapphire ball's tile, all with the same item, keep its slot; 51 new places have new
slots up to 184 of 400; 23 Sapphire balls are not in Emerald; 3 pokeemerald ball scripts no object runs). Placing them is
gen_map_content's (EMERALD-3: it should read `data/emerald/hoenn_items.json` by pokeemerald label); in the phase-0 world
the Sapphire balls give Emerald's items. Hidden items: 112 (95 as in Sapphire, 17 new, 3 of Sapphire's gone), placed by
the story patch where the map exists; 9 are on maps Sapphire's world lacks: Artisan Cave (4) and S.S. Tidal (1) are skipped,
the Safari expansion's 4 (SafariZone_*_Emerald) follow emerald_world's map config (zone 38) once it is in the tree. Marts: every pokeemerald list
equals Sapphire's at the same shop id (only TM names differ), so `data/emerald/hoenn_shops.json` has none; for later:
Battle Frontier Mart and Trainer Hill (2 lists): ids 23/25 are free (patches/shops.py and trade_evos.py read
data/hoenn_shops.json with json.load: switch to version.load_json if an Emerald list ever differs). Berry trees: still
Sapphire's spots (Emerald's new_game.inc names its trees; unchecked).
**Move tutors** (`data/emerald/move_tutors.json`, for emerald_mech): Swagger (Slateport Fan Club), Rollout (Mauville),
Fury Cutter (Verdanturf Center), Mimic (Lavaridge house), Metronome (Fallarbor Mart), Sleep Talk (Fortree house 2),
Substitute (Lilycove rooftop), Dynamic Punch (Mossdeep), Double-Edge (Sootopolis Center), Explosion (Pacifidlog Center):
map, tile, local id, graphics, flag, the four lines, learners. All 10 maps are built.

**Pokédex text.** Every Emerald entry (one page of 4 Gen 3 lines) is longer than Black 2's 3-line window, so each is
wrapped to 222 px and split in two pages like Sapphire's: 377 between two sentences, 9 one long sentence cut at a line
end; page 1 in 0442 (128 KB of its 159 KB slot; three full lines on page 1 would not fit: 167 KB), page 2 in 0443 (73 of
89 KB). Categories, heights and weights equal Sapphire's.

**Test** (work/agents/emerald_data/test_results.txt; screenshots/emerald_data/): ROM d512a08f... (story_build, test trainers
Calvin + Roxanne in Littleroot, HOENN_TEST_CHRP=2), from a fresh state of that ROM (work/agents/emerald_data/boot/:
emerald_wp0's state shows a black screen at the first door on the current ROM). Calvin sent out Poochyena Lv5 (Emerald;
Sapphire: Zigzagoon) with Tackle/Howl; Roxanne's party read from the battle in RAM: Geodude 12, Geodude 12, Nosepass 15
with Emerald's moves; Mudkip's Pokédex entry shows Emerald's text on two pages. Save margin 28,896 B (unchanged).

## Phase 2: Emerald's outdoor world (emerald_world, 2026-10-12)

**The Emerald ROM now stands on Emerald's own outdoor maps**: every outdoor map HoennB2 builds is read from pokeemerald
(the 118 changed maps' ground, the Route 103 seam, the renamed maps, ~1,150 new labels), plus Emerald's three new outdoor
maps (the Safari Zone's two new areas, the Battle Frontier's east half). Rooms and caves are still Sapphire's (work list
below). Sapphire and Ruby build exactly as before (proofs below).

### How it works
- **One switch**: `converter/gba.py world_repo()` is `Repo(pokeruby)` for Sapphire and Ruby and, with
  HOENN_VERSION=emerald, the **Emerald view** (`Repo(root, emerald=True)`). HoennB2 keeps Sapphire's map names: the view
  reads `version.decomp_map(name)`'s pokeemerald folder (BattleTower_Outside = BattleFrontier_OutsideWest, SafariZone_Northeast
  = SafariZone_North, ...), an Emerald-only map whose folder is another Sapphire map's name as `<folder>_Emerald`
  (`SafariZone_Northeast_Emerald`, `MagmaHideout_1F_Emerald`), and gives every MAP_ id of a map.json as HoennB2 knows it
  (Sapphire's id where Sapphire has the map, `MAP_<FOLDER>_EMERALD` for a name clash, else Emerald's). Event islands
  read as in Sapphire's world. Its readers: `plan_map.py`, `world.py`, `terrain/heights.py`, `ground.py`, `water.py`,
  `outdoor_check.py`, `walk_diff.py` (outdoor maps; rooms always pokeruby's), `allocate_zones.py` / `allocate_interiors.py`
  (Emerald mode, below), `emerald_labels.py`. Nothing changes for Sapphire/Ruby (`Repo(root)` is untouched).
- **Outputs**: plans `data/plans/emerald/<Map>.json` (`version.plan_path`), the world `HOENN_WORLD_DIR` or
  `work/world_emerald` (`version.world_dir`). This round's world: `work/agents/emerald_world/world_emerald` (the lead
  moves it to `work/world_emerald`, or rebuilds it: `HOENN_VERSION=emerald rebuild_slice.sh`).
- **Emerald's settings** (overlays read by `version.load_json`, deep-merged; Sapphire/Ruby never read them):
  `data/emerald/hoenn_world.json` (alt layouts' Emerald names), `hoenn_standalone.json` (the new maps in their groups;
  `order`: the Frontier's east half puts its doors first), `hoenn_zones.json` (`allocate_zones.py` Emerald mode: a new map
  shares the zone of its neighbour: Safari expansion = zones 38/40, Frontier east = 17; own zones need their own scripts,
  wild table, music: phase 1/3), `hoenn_interiors.json` (`allocate_interiors.py` Emerald mode: the 54 Emerald-only rooms
  behind Emerald's outdoor doors, status `todo`, no zone: their doors stay closed), `hoenn_map_additions.json` (Emerald's
  own, in place of Sapphire's: `crop`, the Altering Cave layout, `warps` overrides), `hoenn_weather.json` (Route 111's
  desert part), `data/towns/emerald/<Map>.json` (buildings for new doors, `prop_moves`, `retile`, props). Nothing is
  copied from Sapphire's settings: they apply to Emerald's map of the same name; `converter/emerald_settings_check.py`
  compares every position-keyed setting (props, covers, alt-layout boxes, terrain-module boxes) on both maps' plans and
  lists what moved (fixed in the overlays: Rustboro's two lamps, Sootopolis' two door-less houses; the rest checked).
- **Labels**: `converter/emerald_labels.py` writes `data/labels/emerald/carry_<tileset>.json`: Sapphire's label where the
  metatile behaves as Sapphire's and is drawn the same (1,359) or stands where Sapphire has that id in that map (1,660);
  the other 1,144 used metatiles are labelled by eye in `data/labels/emerald/<tileset>.json` (316 of towns and routes, 828
  of the Battle Frontier; sheets: `work/agents/emerald_world/tools/label_sheets.py`, `frontier_labels.py`). Check: the 51
  outdoor maps Emerald did not change get plans identical to Sapphire's.
- **Route 103 seam** (EMERALD_PLAN 1.1): Emerald's Route 103 is read as its first 20 rows (`crop`): rows 18-19 are
  Sapphire's own, rows 20-21 only repeat them (path to Oldale, forest, sea). The world grid stays Sapphire's: no conflicts.
- **Door numbers of the shared rooms**: rooms are Sapphire's and their exits name a zone's door index. Emerald keeps them:
  a door to a room not built yet is a closed placeholder in Sapphire's order (the Battle Tents stand where the Contest
  Halls were); the Frontier's east half comes first in zone 17, so the Battle Tower door stays door 0
  (`data/versions.json` `door_plays` + `version.door_alias`; `patches/standalone.py` uses it). `check_exits` on Emerald's
  world: 0 outdoor exits differ (as Sapphire's). Doors that moved a tile (Mossdeep's Space Center and House 2, Verdanturf's
  tent, Route 103's Altering Cave mouth, Sky Pillar top) keep their index.
- **world.py additions** (all inert for Sapphire/Ruby): `retile_map` (a map's own `retile` rules), `moved_props`,
  Emerald signboards (a solid sign tile no Sapphire sign stands on gets Black 2's signboard, res 152, as scenery until
  phase 3 ports Emerald's signs), closed placeholder doors (status `todo` rooms). `ground.py`: the Frontier island is
  paved (both halves) and its plaza walls are walls (Emerald only).
- **PWT**: decision 1A closes the six facilities but the Battle Tower, so the PWT's door is the **Ranking Hall** next to
  the Battle Tower (`data/emerald/hoenn_map_additions.json` warps; one entry to move it elsewhere). Tested in game.
- **Weather**: Route 111's desert part recomputed on Emerald's map with the weather agent's own flood fill: its east strip
  ends at row 107, so Trainer Hill has Route 111's weather. Route 119/123's sunny ends (v166_fixes) come out the same on
  Emerald's maps and triggers (`work/agents/emerald_world/tools/cycle_parts_emerald.py`): no change.

### Proofs and checks (work/agents/emerald_world/)
- Sapphire and Ruby, HEAD (415b375) vs HEAD + these files (`tools/proof_sapphire.sh`, `proof/proof.txt`): plans, world
  cells, world.json, alt plans, world report, `allocate_zones` / `allocate_interiors` output, `fixed_weather.data()`,
  outdoor_check: all identical (and equal to HEAD's tracked plans/zones/interiors). ROMs built from the two trees
  (`tools/proof_rom.sh`, `proof_refresh.sh`; same world, rooms, inputs): Sapphire 1f2165bd... both, Ruby 05f8932b... both
  (`proof/rom_proof.txt`). `version.door_alias` changes no Sapphire/Ruby room exit (checked on all 23 warp-only exits).
- Emerald world: outdoor_check place/size/walk/door/bld/zone/tex **0 open** (Emerald's accepted: closed doors of unbuilt
  rooms, the rocket gantries over Mossdeep's sea, the Magma Hideout mouth); walk_diff outdoor OPEN 32 (Sapphire 33);
  door_check 165 doors, 0 findings; check_exits 0 outdoor exits differ; walk_diff all families OPEN 712 (Sapphire 713).
  Geometry kinds (`out/outdoor_check_geometry.txt`): layer 40, cull 243, hole 23 (Sapphire after v16.4's sweep: 36 / 232
  / 21); the new ones are in the new areas (the Frontier: layer 5, cull 15, hole 1) and Route 125 north of Mossdeep
  (holes 36 + 59 px at world (753, 127-129), (749, 147-148)): for the glitch-check agents.
- Boot test (muted DeSmuME, `tools/boot_test.py`): cold boot -> Littleroot; Route 103 across the seam into Oldale;
  Route 111's desert (Mirage Tower); the Battle Frontier: Battle Tower in and out, the plaza, the PWT door into Black 2's
  PWT lobby. Shots: `screenshots/emerald_world/`. Save margin 28,896 B (pack 0 unchanged).

### New outdoor areas (one glitch-check agent each, standing rule)
1. Route 103: the seam with Oldale and Emerald's redrawn east half (+ the Altering Cave mouth layout after the game).
2. Route 111: the Mirage Tower (stand-in: a rock mound with a cave mouth, door closed), Trainer Hill (stand-in building
   res 332 on the plateau, cave-mouth entrance, closed), the desert's new south edge.
3. The Battle Frontier island (BattleTower_Outside + BattleFrontier_OutsideEast): stand-in buildings, Tower and PWT open.
4. The Safari Zone's expansion (SafariZone_Northeast_Emerald, SafariZone_Southeast_Emerald) and the changed north/south areas.
5. Changed towns and routes: Mossdeep (Space Center area), Slateport (market, harbour, Battle Tent), Verdanturf and
   Fallarbor (Battle Tents), Sootopolis (Mystery Events House, closed), Rustboro, Lilycove, Jagged Pass (Magma Hideout
   door), Mt. Chimney, Sky Pillar outside/top, Routes 105-134 (Terra Cave doors on 113-116 and 118, the Marine Cave
   areas of 125/127, Route 110's and 120's bridges).

### Work list (left for the next agents)
**Rooms and caves** (none built for Emerald yet; the shared Sapphire rooms stand in):
- Emerald-only rooms behind outdoor doors (`data/emerald/hoenn_interiors.json`, status `todo`; give each a zone and a
  room, then its door opens by itself): Battle Tent lobbies x3 (closed by decision 2), Trainer Hill (7, closed),
  Mirage Tower 1F-4F, Terra Cave (entrance, end; doors on Routes 113-116, 118), Magma Hideout 1F_Emerald-4F (8, door on
  Jagged Pass), Artisan Cave 1F/B1F, Mystery Events House (left out, decision 5), the Frontier's buildings (closed:
  facilities, lounges, Center, Mart, Scott's house, gate, Ranking Hall = PWT). Also new but behind rooms or Dive (not in
  that list): Desert Underpass (Route 114 tunnel), Meteor Falls Steven's Cave, Marine Cave + Underwater_MarineCave,
  Underwater_Route105/125/129, Sky Pillar's clean layouts, Pokémon League 2F.
- Changed rooms (versions.json `ground`, 78 rooms/caves): the 8 Gyms with their puzzles, the 8 Trick House puzzles,
  every Center 2F (+1 row), the Marts (2 blocks), Birch's lab, May's house 1F/2F, Brendan's 2F, Devon 1F/3F, Rustboro
  Flat 1 2F, Slateport Fan Club, Mossdeep Game Corner, Lilycove Contest Lobby / elevator / unused mart, the Battle Tower
  rooms, Cave of Origin (Emerald's B1F = R/S B4F, 154 blocks), Seafloor Cavern entrance/2/3/6/7, Meteor Falls 1F_1R/2R,
  Mt. Pyre 2F/3F/6F, Victory Road B1F/B2F, Aqua Hideout B1F, Magma Hideout B1F (Ruby's), Route 114 Fossil Maniac's tunnel,
  Underwater3 (Route 127, 518 blocks). The 3 name clashes: SafariZone_Northeast/Southeast_Emerald are built (outdoor);
  MagmaHideout_1F_Emerald is a room still to build.
**Models** (stand-ins today): the Battle Tents (Contest Hall res 362), Trainer Hill (res 332), the Mirage Tower (rock
  mound), the Frontier's seven facilities and its houses (League 409, Weather Institute 407, Fan Club 342, Harbor 345, Game
  Corner 349, Flat 324, Motel 385, Sootopolis block 471; the Battle Tower is Sapphire's tower 473, Emerald's is 17 wide:
  stone walls fill its sides), Mossdeep's Space Center rocket and gantries (the gantries over the sea are solid sea),
  Slateport's moored sailboats (sea rocks), the Safari entrance building's Emerald wing (wall blocks).
**Story (phase 3)** in the changed maps: signs and people still stand at Sapphire's places (data/sapphire); Emerald's own
  signs show a plain signboard; scripted coordinates to redo: the ferry to the Frontier (`h_sail_ferry` 19+17, 23+18 is
  Sapphire's island: Emerald's dock is at the west half's south pier), Mossdeep's Space Center scenes (2 rows south), Sky
  Pillar top (door 1 row south), Route 103's Altering Cave (mouth at x 45, was 47), Sootopolis; the Sky Pillar door is
  open (Emerald keeps it shut until Wallace); the island's place name is the Battle Tower's line.
**Phase 4**: the closed-door message (emerald_mech's script 2291) on the closed doors listed above; the Mirage Tower's
  collapse (LAYOUT_ROUTE111_NO_MIRAGE_TOWER: an alt layout + a free map-replace event); the Safari expansion's and the
  Frontier east half's own zones (wild tables, music) once they have scripts.

## Phase 4 mechanics (emerald_mech, 2026-10-12)

Four mechanics story and world scripts can call now; Emerald builds only. Files: `b2tools/patches/emerald_mech.py` + `.c`
(last in the patch lists of story_build.sh / rebuild_slice.sh; Sapphire and Ruby: returns "nothing"),
`src/include/hoenn_emerald.inc` (the macros), `src/field_scripts/emerald/1236_global_2280.s` (Black 2's global file 1236,
its own tutors 2280-2288 byte for byte, plus globals 2289-2292), `src/text/emerald/overrides_emerald_mech.json` (5 lines
appended to that file's text 615). Include `hoenn_emerald.inc` after hoenn_story.inc (and `hoenn_trainers_emerald.h` for
Emerald's trainer names). Tested on an Emerald story build (proofs `screenshots/emerald_mech/`).

| Mechanic | Call | What it does |
|---|---|---|
| Space Center tag battle | `em_tag_battle TRAINER_STEVEN_PARTNER, TRAINER_MAXIE_MOSSDEEP, TRAINER_TABITHA_MOSSDEEP, L_NotReady` (close the NPC's window first) | Emerald's ChooseHalfPartyForBattle in one party menu: Black 2's battle-entry screen (the Battle Subway's: ENTER marks FIRST / SECOND / THIRD, NO ENTRY takes one out and the later ones move up, "No more than three Pokémon may enter.", an Egg cannot be entered, CONFIRM / CANCEL), 1 to 3 Pokémon, any level. A fainted pick "can't participate" (the menu again). CANCEL / B with nothing marked -> `L_NotReady`; with picks marked Emerald's "Cancel the battle?": YES -> `L_NotReady`, NO -> the menu again with the same picks. The picks lead in that order beside Steven (back sprite 5), only they are in the battle (1, 2 or 3); afterwards the party is in its old order again with the battle's HP/exp kept. Won: falls through, both foes' flags set. Lost: the whiteout (Emerald's SetCB2WhiteOut) |
| Two trainers at once | nothing: place both as ordinary eye-contact trainers (gen_trainer_npcs, script 3000 + id) | Black 2 does it itself (EventTrainerEye_CheckAll: with 2+ Pokémon able to battle, a second trainer who sees the player joins: global 1239 L_124E, both walk up and speak, `CallTrainerBattle a, b`, both flags; with one able Pokémon only the first battles, as Emerald). 82 trainer pairs in Emerald's maps can see a common tile (geometry with the layouts' collision, work/agents/emerald_mech/tools/emerald_pairs.txt): a checklist for the Emerald trainer placement |
| Move tutor | a whole NPC script: `em_move_tutor SWAGGER, FLAG_MOVE_TUTOR_TAUGHT_SWAGGER, Teach, Once, WhichMon, Declined, Taught` (line numbers of the zone's text: data/emerald/move_tutors.json "lines" + Emerald's common "This move can be learned only once. Is that okay?") | Emerald's flow (taught already -> Taught; YES/NO twice; party menu; "X and Y are not compatible." / "X already knows Y." close it as Emerald does; else Black 2's own learning sequence, forgetting a move if it knows four; taught -> flag + Taught, else Declined). Who can learn: pokeemerald's sTutorLearnsets, read at build time (the 10 town tutors; Gen 4/5 species take their Gen 3 family's entry, 29 species) |
| Closed door | a sign on the door tile with `"script": 2291` (story json; no zone script or text), or `em_closed_door` in a zone script | "This building is still under construction. Please come back when the work is completed." (Emerald's own unused Battle Tower words), nothing opens. Give the door no warp (or move it off: ObjInitWarpGPos n, 0, 0, 0) |

Doors to close (pokeemerald warps; decision 1A/2): Battle Frontier East warp 1 Arena (39,29), 2 Palace (45,56), 3 Pyramid
(58,14); West warp 0 Pike (42,27), 1 Dome (19,17), 2 Factory (11,38) (East 0 = the Battle Tower stays open); Battle Tents:
SlateportCity warp 3 (10,12), VerdanturfTown warp 0 (3,7), FallarborTown warp 1 (8,7); Trainer Hill: Route111 warp 4
(31,113). The Frontier's lounges, Ranking Hall, Exchange Corner, Mart, Center, Scott's house, gate: the world agent's choice.

**Code** (emerald_mech.c, ITCM after the other ITCM patches, 2,302 B): script commands 533 `EmPartySwap a, b`, 281
`EmTutorCheck var, slot, tutor` and 686 `EmPickParty var` (three commands no Black 2 or Hoenn script used, argument kinds
unchanged, so script_check still decodes them). EmPickParty runs the Battle Institute's own team-selection event
(ov012 func_ov012_02161c88: field closed, the ov165 party screen in mode 22 = the Subway's entry screen, field
reopened) with the regulation inside its data changed to Emerald's multi rule (arc 106 file 22, then min 1, max 3,
no level rule, no clauses); its result: the screen's picked[] (party slots from 1, in pick order) and index 7/8 = left
with CANCEL/B (Black 2's own reading, func_ov012_02162ccc). ov036 0x021a1e2c (BtlSetup_SetTrainerLocal ->
SetTrainer2v2, battles with a partner) -> the battle's copy of the player's party keeps its first n, n = bits 12-15 of
the partner id global 2290 passes (tested: without it Black 2 let a 4th Pokémon join, and with 2 picks the 3rd party
slot joined); ov166 0x0219cf6e (after a local battle, the battle's party copied back over the player's) -> a shorter
battle party goes back into the first slots, every other battle as before; arm9 TRAINER_CLASS_BACK_SPRITES {37, 5} ->
{Steven's class from the Emerald trainer data (230), 5}. ITCM and ov012 change: savestates of other ROMs lack the
commands (cold-boot states).

**Planned, not built (each needs its maps first):**
- **Mirage Tower** (Route 111): Emerald shows it on half of the visits (SetMirageTowerVisibility: Random() & 1, always
  after FLAG_FORCE_MIRAGE_TOWER_VISIBLE, never once VAR_MIRAGE_TOWER_STATE is set). Route 111's zone init: `h_random`
  -> a flag, the tower a 3D object hidden by that flag (or a map replace event, as the Sky Pillar islet), its door warp
  moved off when hidden. The collapse after the fossil (MirageTower_4F, VAR_MIRAGE_TOWER_STATE 1 -> 2): `EvCameraShake`
  (Black 2 command, used in 0246.s), a white flash/fade, the state var hides it for good, the player lands in the desert.
- **Rotating tiles** (Mossdeep Gym, Trick House 7: pokeemerald rotating_tile_puzzle.c): arrow tiles push the player
  (step triggers + scripted walks, `h_applymovement 255`), the switch tiles turn every arrow by 90 degrees: the floor in
  four layouts as map replace events (Black 2 has only ten, 3-9 already Hoenn's: STORY_COMMON.md) or the arrows as 3D objects whose
  model/flag changes; the trigger scripts read one work (the rotation) to pick the push direction. A layout swap shows
  after a map change (Sub_MG_Redraw's way), so 3D objects are the smoother choice.
  **Correction (emerald_rooms, measured in rotating_tile_puzzle.c):** the arrows do not push the player. Each colored
  switch moves every object standing on an arrow square of that color one square counter-clockwise and turns it; the
  pads (behavior 0x0E) teleport the player and keep the objects where they are. Built that way: "Rooms" below.
- **New Regi puzzles** (Emerald: Regirock = Rock Smash two right and two down of the braille's centre, Registeel =
  Flash in the centre, Regice = a lap around the room along the walls; the Sealed Chamber is Sapphire's): Rock Smash and
  Flash are hm_free's field-move globals: give them a hook that runs a zone script when the player stands on the right
  tile (check zone + tile before the default); the lap = step triggers along the wall that count in order in a map work
  (Emerald's own step counter), the last one opens the door (the door's warp moved in with ObjInitWarpGPos).
- **Abnormal weather / Terra and Marine Cave** (post-game): CreateAbnormalWeatherEvent picks one of 16 routes
  (VAR_ABNORMAL_WEATHER_LOCATION, after Kyogre/Groudon only the other), cleared by a step counter. In Black 2: a story
  work set at the Weather Institute and on a new day (the midnight reset, flags 2720-2819); each of the 16 routes' zone
  init compares it: the weather (patches/weather.py already answers per zone for Sootopolis's crisis: one more rule
  reading the work) and the cave entrance (a 3D object + a warp moved in, or Marine Cave's dive spot through dive.py's
  table).
- **Sootopolis sequence** (Emerald's Kyogre vs Groudon, Rayquaza): camera pans (`EvCameraMoveTo` / `EvCameraReturn`,
  Black 2 commands), the weather swapping during the scene (`FieldSetWeather`, command 310: allowed in normal scripts,
  only not in a zone init; weather.py's crisis hook for the rest of the visit), the legends as NPC models (Kyogre already
  uses Pokémon sprite code 4511; Groudon and Rayquaza the same way), the music (emerald_art's mus_abnormal_weather,
  mus_rayquaza_appears), the layout change as a map replace event.


## Integration (emerald_integrate, 2026-10-12): the generator run on Emerald's world, the Jagged Pass mouth, sprites

**The Emerald ROM now has Emerald's own people, signs, item balls and trainers on Emerald's outdoor maps**, and every
story builder's Emerald scene entries land on the numbers they were written for.
- **World**: `work/world_emerald` = emerald_world's copy (`cp -c -R`), then rebuilt in place by world.py after the
  generator run (52-80 s + ToNsbmd). `rebuild_slice.sh`'s Emerald block now runs, after Emerald's first world.py:
  `sapphire_data.py` (Emerald) for every map of Emerald's world but the hand-made Littleroot / Route 101 / Oldale,
  `gen_map_content.py` and `gen_trainer_npcs.py` (Emerald), then world.py again.
- **Generator run** (S0-1/S0-3): pokeemerald's events of 69 maps in `data/sapphire/emerald/`; 383 simple signs / people /
  item balls in 55 maps (`data/emerald/hoenn_content.json`, 30 script and 33 text overlays `*_auto_*`); 285 outdoor
  trainer NPCs in 34 zones (`data/emerald/hoenn_trainer_npcs.json`; Sapphire 197). The scene numbers, checked in the
  preprocessed files: Petalburg 9 Em_PB_Scott / 10 Em_PB_WalkToWallysHouse, Rustboro 25 Em_RB_RivalTrigger, Route 104
  9/10, Slateport 29-32, Mt. Chimney 15/16 + its route sign = Script_17 (message 27), Jagged Pass 1-4, Mt. Pyre summit 9
  = MPS_EmInit (`0059` init overlay).
- **Fixes the run needed** (all inert for Sapphire and Ruby): world.py reads `data/emerald/hoenn_content.json` and
  `data/sapphire/emerald/<Map>.json` in Emerald (the hand-made zones keep Sapphire's events: their settings name
  pokeruby's labels; `HAND_MADE_EVENTS`); `gen_map_content.py` names a zone's file after its FIRST map (Emerald's zones 17,
  38, 40 hold two maps: the Frontier's east half / the Safari expansion took the file, dropping BattleTower_Outside's and
  the Safari scenes, and zone 40's person 7 ran a script that did not exist = a crash); `gen_trainer_npcs.py` keeps
  story objects' uids free (Route 111's Claw Fossil 135 = 100 + Sapphire's object 35 = Emerald's Tyron); `sapphire_data.py`
  reads the name-clash maps (`SafariZone_*_Emerald`).
- **Jagged Pass mouth** (EMERALD_STORY.md 6.4): the map's own layout is the sealed one (in-place edit
  `LAYOUT_JAGGED_PASS`, both mouth tiles rock wall 0x274), the open one `LAYOUT_JAGGED_PASS_HIDEOUT_OPEN`
  (`data/emerald/hoenn_map_additions.json`) swaps in while **map replace event 1** is set (`data/emerald/hoenn_world.json`
  alt_layouts; work 0x4032 == 0x224, `data/story_ids.json` WORK_MAP_REPLACE_1_JAGGED_PASS). Jagged Pass is a warp-only
  map, so `world.py group_alts` (new) builds alt cells for a standalone group (1 cell changes) and `patches/hoenn_world.py`
  writes their a/0/1/0 entries on the group's own matrix; Black 2 sets event 1 from no script or code, but its own four
  event-1 entries would load Unova rooms over matrices 342/343/347/350 (our Glass Workshop, Fossil Maniac's house, Day
  Care, Weather Institute 2F), so a build that uses event 1 drops them. `scenes/JaggedPass.inc`: `JP_HIDEOUT_WARP 6`
  (zone 18's 2 Black 2 warps + world door 4), the zone init re-asserts the event at state 2, the opening scene sets it and
  redraws by a map change to the player's own trigger tile (`Sub_JP_Redraw`, entry 4 `JP_FadeIn`, as Mauville Gym's).
  Played: sealed -> "This boulder is shaking..." -> the mouth opens; the door stays parked until the hideout is built.
- **Map replace event 1 has three users** (emerald_ch10, 2026-10-12): Jagged Pass's mouth, Sootopolis' legends-battle lake
  (`LAYOUT_SOOTOPOLIS_CITY_LEGENDS_BATTLE`, rough water drawn as sea) and the clean Sky Pillar top (`LAYOUT_SKY_PILLAR_TOP_CLEAN`),
  all `alt_layouts` of warp-only groups (each patches only its own matrix); each zone init sets or clears it on entry. Labels
  `data/labels/emerald/gTileset_Sootopolis.json`. Details: EMERALD_STORY.md section 8. A world rebuild (world.py + ToNsbmd) adds
  their cells.
- **Contest rooms**: Slateport / Verdanturf / Fallarbor lobbies and halls are Sapphire's and Ruby's only
  (`data/versions.json` rooms). The Battle Tent doors were already parked by hoenn_world.py (no warp on the door tile,
  checked in the ROM); their door entries stay so the later doors keep the indices the shared rooms' exits name.
- **Sprites**: Juan = Black 2's PWT 276 with its X frames filled by `sprite_pwt.py 276` (Steven's/Wallace's method),
  written to `src/sprites/overworld/emerald/276-juan` (Emerald only: Sapphire and Ruby show Black 2's 276 only in the
  PWT, standing). Tabitha = Ruby NDS's sheet copied onto code 290 (`sprite_emerald_story.py build tabitha`; 290 is Scott's
  289's twin, used only by a replaced Unova script), `data/story/ch5.json` model_emerald 290. Played: both walk in all
  four directions; Tabitha at Mt. Chimney.
- **Checkers fixed**: rooms_check (B1's #ifdef before the house's defines broke its Littleroot scenarios for every
  version; rooms a version leaves out are not reported), scene_walks (macros that end a script, h_msgbox_npc ...: it
  followed Petalburg's Wally's mom into the Emerald Scott scene placed after her).
- **Proof, Sapphire and Ruby unchanged** (`work/agents/emerald_integrate/proof.sh`, `proof/proof.txt`): HEAD 07ce9af vs HEAD +
  these files, each tree with its own Sapphire world and the Sapphire generators rerun: world 422 cells and world.json
  identical, generated scripts/text/content/trainer NPCs identical; full ROMs Sapphire 1e8c1f55... and Ruby 74e18639...
  in both trees (= the published v16.6 ROMs), save margin 28,896 B.
- **Emerald build** (main tree, `work/agents/emerald_integrate/rom_emerald/hoenn.nds`, SHA-1 f12a6c86...; it includes the
  Frontier agents' unfinished edits of that moment): save margin 28,896 B. Checkers: outdoor_check 0 open, door_check 165
  doors 0 findings, check_exits 0 outdoor exits differ, walk_diff OPEN 712 (as emerald_world's), rooms_check = the
  Sapphire baseline {b 4, e 118, g 1, h 12, k 7, m 18}, script_check open ent 3 / path 2 / mapc 2 (all story placements
  on Emerald's changed maps, by owner in emerald_integrate's report), scene_walks 90 (Sapphire 0, Ruby 0: Scott's
  Petalburg exits, the rival's 2F approach, the Ch13 May's house walk, Cave of Origin B4F's Kyogre on a stand-in room).
- **Played** (muted DeSmuME, `work/agents/emerald_integrate/tests/em_places.py`, `em_sprites.py`; shots
  `screenshots/emerald_integrate/`): new game to Littleroot, Oldale into Route 103 across the seam, Route 103's Emerald
  east half (its new trainers battle), Scott in Petalburg, Mt. Chimney (Tabitha's battle, Maxie's battle won, Archie's
  thanks), the Jagged Pass mouth opening, Juan's and Tabitha's walks.

## Caves and dungeons (emerald_caves, 2026-10-12)

**Emerald's own caves and the caves Emerald changed are built, Emerald build only** (Sapphire's and Ruby's rooms and
files unchanged: the shared generators give them the same output, checked without a build: below).

### How it works
- **Reading Emerald's maps**: a cave recipe whose `"map"` is `"emerald/<Map>"` is read through Emerald's world view
  (`b2tools/models_cave.py sapphire()` -> `converter/gba.py Repo(pokeruby, emerald=True)`: HoennB2 map names and MAP_ ids,
  pokeemerald's layouts; `"layout"` may name an Emerald layout or one of `data/emerald/hoenn_map_additions.json`). It sits
  beside emerald_rooms' `"pokeemerald/<Folder>"` (pokeemerald read directly, for room variants). Its arches look up
  destinations in Emerald's world (`emerald_dest_name/_outside`; MAP_DYNAMIC counts as outdoors); its tileset table is
  `data/cave_tiles.json "emerald_view:<tileset>"` (Emerald's metatiles: Ruby's boulder ids are cliff pieces in Emerald's
  gTileset_Cave; sheets `work/agents/emerald_caves/sheets/`). The checkers read the same name (caves_check, walk_diff).
- **Zones**: `HOENN_VERSION=emerald python3 converter/allocate_interiors.py --claim [--skip N] MAP ...` gives Emerald-only
  rooms of `data/emerald/hoenn_interiors.json` a zone and their own script/text numbers (main()'s pool, never a zone
  another Emerald room claimed; re-reads the file before writing). Its walk now also follows the warps out of Sapphire's
  rooms and Emerald's Dive links (dive/emerge connections, setdivewarp), so the Desert Underpass, Steven's Cave, the
  Marine Cave and the three new underwater maps are listed. Claimed: zones 349, 352-354, 356-364, 366, 367, 369, 371-373,
  375, 377, 379, 382, 386 (own scripts 1978-2025, own texts 1004-1027).
- **Zone files**: `HOENN_VERSION=emerald python3 converter/gen_caves.py --emerald` (or ROOM names) =
  `converter/gen_caves_emerald.py` (gen_caves.main's rules on Emerald's maps): `data/interiors/emerald/<zone>.json`,
  `src/field_scripts/emerald/<n>_room_<Map>.s` (+ `_init` for underwater maps), the wild table in
  `src/encounters/emerald/` with its file in `data/emerald/hoenn_encounters.json` (identical tables share; a/1/2/7 had
  no free file left after Sapphire's caves, so Emerald appends files 135-137 inside the archive's fixed reserve:
  `patches/encounters.py` Emerald only; 97 and 98 were still free). The plain Emerald `gen_caves.py` (no names) still
  writes only the shared caves' Emerald tables and keeps these files. `rebuild_slice.sh`'s Emerald block runs
  `--emerald` after Emerald's world.py (the exits name its doors), then `b2tools/emerald_caves_rooms.py`.
- **Variants of Sapphire's caves**: `data/cave_layouts/<Map>_Emerald.json` (`"alt_of"`, installed for the map by
  `data/versions.json room_variants.emerald`). With `"emerald_zone": true` its zone json is Emerald's
  (`data/interiors/emerald/<the Sapphire zone>.json`, `"room"` the Sapphire name, the variant swapped in by
  patches/interiors.py); the zone's script file stays the shared one when Emerald's step scripts are Sapphire's (Meteor
  Falls 1F, Seafloor Rooms 2/3, Underwater3), else an Emerald copy (`src/field_scripts/emerald/`: Cave of Origin 1F/B4F)
  whose story part is copied from the shared file and whose generated scripts are padded to Sapphire's count, so every
  story entry keeps its number. Room-builder variants: `b2tools/emerald_caves_rooms.py` (emerald_rooms' convention).
- **Place names** (system text 0109, `src/text/emerald/overrides_emerald_caves.json`): Magma Hideout 91, Mirage Tower 107,
  Artisan Cave 110, Desert Underpass 111, Terra Cave 112, Marine Cave 113 (lines no zone of the Emerald build shows);
  the underwater maps use Sapphire's "Underwater" (55). Music: each Emerald-only room plays its pokeemerald map's song
  (`patches/hoenn_music.py zone_songs`, Emerald only: Magma Hideout mus_aqua_magma_hideout, Mirage Tower and the Desert
  Underpass mus_mt_chimney, Terra/Marine/Artisan mus_petalburg_woods (pokeemerald's own choice), Steven's Cave
  mus_cave_of_origin, underwater mus_underwater).
- **zone_effects** now clears Black 2's own entries (darkness, gimmicks, city sounds) for Emerald's zones too (Challenger's
  Cave 352-354 were dark: the Magma Hideout's 2F rooms showed the Flash circle) [test].
- **Dive** (`patches/dive.py`, Emerald only): Emerald's maps for the grids and `LINKS_EMERALD`: MarineCave_Entrance <->
  Underwater_MarineCave (Emerald's setdivewarp spots) and surfacing from Underwater_Route105/125/129. Sapphire's table is
  byte-identical to HEAD's (checked).

### What is built (zones; all Emerald only)
| Map | Zone | Built | Notes |
|---|---|---|---|
| Magma Hideout 1F (MagmaHideout_1F_Emerald), 2F_1R/2R/3R, 3F_1R/2R/3R, 4F | 349, 352-354, 356-359 | cave, look in81 (Reversal Mountain), lava pools = Ruby's lava textures | Jagged Pass door 4 (its zone init opens it at VAR_JAGGED_PASS_STATE 2); 1F's three Strength boulders close the west corridor as in Emerald; 7 item balls; 16 grunts + Tabitha, Maxie, Groudon (asleep/awake) left for the story |
| Mirage Tower 1F-4F | 360-363 | cave, look d0 | Route 111 door; 1F-4F ladders; 2F/3F cracked floors drop to the floor below (walking; the Mach Bike crosses); the two fossils (4F) left for the story |
| Terra Cave entrance, end | 364, 366 | cave, d0; the end's lava pool | the 10 route doors (Routes 113 x2, 114 x2, 115 x2, 116 x2, 118 x2) lead in but are **parked** (`"doors_parked"` in data/emerald/hoenn_interiors.json: world.py gives the door, patches/hoenn_world.py parks it off the map; the abnormal weather's zone init must move the open one in with ObjInitWarpGPos <index>); the exit is a dynamic warp (back to the door you came by) |
| Marine Cave entrance, end; Underwater_MarineCave | 367, 369, 371 | cave d0 (Kyogre's blocked pool drawn as water); underwater look `uw` | entrance <-> Underwater_MarineCave by Dive; Underwater_MarineCave's exit is dynamic |
| Underwater_Route105/125/129 | 379, 382, 386 | look uw | their two doors each lead to Underwater_MarineCave; surfacing to the route; their dive spots are the abnormal weather's (Phase 4) |
| Artisan Cave 1F, B1F | 372, 373 | cave d0, B1F's two levels | Battle Frontier east door (zone 17 door 15) -> 1F, ladder, B1F -> Frontier west (door 26); 2 item balls, 4 hidden items listed |
| Desert Underpass | 375 | cave d0, 5x1 chunks | the Fossil Maniac's tunnel's north door (below) |
| Meteor Falls Steven's Cave | 377 | cave d0 (Meteor Falls' rock piles) | Meteor Falls 1F warp 5 (below); Steven left for the story |
| Cave of Origin 1F / B1F (Emerald's B1F = R/S B4F zone 103) | 95, 103 | variants `CaveOfOrigin_1F_Emerald` (lit: Emerald's 1F needs no Flash), `CaveOfOrigin_B4F_Emerald` (Emerald's B1F redrawn: no pool) | 1F's ladder leads to zone 103; B1F's back to 1F; R/S B1F-B3F (zones 100-102) are unreachable in Emerald |
| Seafloor Cavern Rooms 2, 3 | 183, 184 | variants (Room 2 is a new 18x12 room; Room 3 redrawn) | their boulders/rocks Emerald's; the Entrance and Rooms 6/7 differ only in art the builder doesn't draw: Sapphire's rooms |
| Meteor Falls 1F_1R | 128 | variant with Steven's Cave's mouth drawn open (layout `LAYOUT_METEOR_FALLS_1F_1R_STEVENS_CAVE`) | warp 5 -> Steven's Cave; Clay Tunnel's rock (code 206) on (4,3) until FLAG_SYS_GAME_CLEAR (Emerald opens it with setmetatile after the game; Black 2 can't) |
| Victory Road B1F, B2F | 171, 172 | variants (Emerald opens (13,16)-(13,18) and (10,24)-(10,26)) | Sapphire's zone jsons; Emerald's two new double-battle pairs left for the story |
| Underwater3 (Underwater_Route127) | 218 | variant (518 blocks redrawn) | two doors to Underwater_MarineCave; the link to Underwater4 stays warp 0 |
| Mt. Pyre 2F/3F/6F | 342, 346, 376 | room variants (`facilities_pyre.py`'s recipe on Emerald's map: gravestones moved) | Sapphire's zone jsons; ch8b's Dez & Luke (2F, Sapphire (2,8)/(3,8)) stand on Emerald's gravestones: the story's `at_emerald` |
| Aqua Hideout B1F | 5 | room variant (7 tiles on another level) | |
| Route 114 Fossil Maniac's tunnel | 558 | room variant, its north door open; Emerald zone json | warp 2 -> Desert Underpass; a boulder (0x2004, no script: cannot be pushed) on Sapphire (6,3) until FLAG_SYS_GAME_CLEAR (Clay Tunnel's rock 206 blocked but was not drawn in this room zone [test]) |
| Sky Pillar 1F-5F | 164-168 | room variants: Emerald's clean floors (no rubble, no cracked floor), Emerald zone jsons for 2F/4F without the falls | installed for the whole game: the cracked floors after Rayquaza need the story's state (below) |

### Left for the story and Phase 4
- **Sky Pillar after Rayquaza** (B7): Emerald shows the cracked floors once VAR_SKY_PILLAR_STATE >= 2. Black 2 has no
  free map replace event, but one can serve several rooms when each room's zone init sets it on every load (emerald_rooms'
  Lab/Mauville Gym pattern): add `"alt_rooms": [{"room": "SkyPillar_<n>F", "event": E}]` (Sapphire's cracked room) to
  `data/interiors/emerald/<zone>.json` of each floor, a zone init that sets event E from the state, and the 2F/4F falls
  (Sapphire's zone json's triggers) with a work condition. The Top's clean layout is an outdoor alternate layout (world).
- **Mirage Tower**: the visibility at random, the collapse, the fossils (B6, Phase 4). **Terra/Marine Cave**: the
  abnormal weather picks a route and moves its parked door in (Terra) / adds the dive spot (Marine: dive.py has no
  per-day switch; the spots are known: data/scripts/abnormal_weather.inc) (B8, Phase 4); Groudon/Kyogre objects and
  triggers; Steven (B8). **Magma Hideout** (B4): grunts, Tabitha, Maxie, Groudon; 4F's scene. (**done 2026-10-12, emerald_ch8_hideout: EMERALD_STORY.md 6.5**) **Cave of Origin** (B7):
  Wallace on B1F; Sapphire's ch10 triggers there (Kyogre's cry (13,9)/(5,9) stand on rock in Emerald's B1F; (9,13) runs
  Sapphire's Kyogre scene) need `skip_emerald`. **Seafloor Room 3**: Shelly and a grunt at Emerald's (9,5)/(5,5)
  (ch10's Shelly stands at Sapphire's (10,5)).

### Checks and proofs (work/agents/emerald_caves/)
- caves_check abceistwx on the 32 cave recipes: 0 walkability (w), event (e: only Sapphire's ch10 Kyogre-cry triggers on
  rock in Emerald's B1F), ladder, object, size findings; t = the accepted rim-fade / cliff-stretch classes, plus 18 faces
  of the Desert Underpass's chunks 3-4 whose texture coordinates pass the DS's +-2048 texels (smeared rock faces: for its
  glitch check); fh: 3 holes of 6-11 px (Seafloor Room 2, Victory Road B2F, Meteor Falls 1F). rooms_check on the 10
  room variants: only ch8b's Dez & Luke on Emerald's Mt. Pyre 2F gravestones (story). walk_diff interior/cave/dive: 0
  new open findings (Aqua Hideout B1F = Sapphire's 11; Sky Pillar's "unblock" tiles intended). check_exits: 0 outdoor
  or dynamic exits differ. door_check (world): 165 doors, 0 findings. Logs: caves_check_*.txt, rooms_check*.txt,
  walk_diff*.txt, check_exits.txt, door_check.txt.
- Played (muted DeSmuME, `tools/ec_test.py`, harness copied from emerald_integrate; shots `screenshots/emerald_caves/`):
  Jagged Pass door <-> Magma Hideout 1F and all eight rooms' warps; Route 111 -> Mirage Tower 1F-4F ladders up and down,
  a 2F cracked floor dropping to 1F, back out; Terra Cave entrance <-> end (+ its dynamic exit); Marine Cave entrance <->
  end; the tunnel's boulder before the game is clear, then the Desert Underpass and back; Steven's Cave's rock before the
  game is clear, the cave after it and back; Battle Frontier -> Artisan Cave 1F -> B1F -> Frontier west; Cave of Origin
  entrance -> 1F (lit) -> Emerald's B1F -> 1F; Seafloor Rooms 2 and 3 in and out; Victory Road B1F/B2F through Emerald's
  openings; Mt. Pyre 2F <-> 3F, 6F -> 5F; Aqua Hideout B1F -> B2F; Sky Pillar 1F -> 4F clean floors, 4F -> 5F -> the top.
  Not played: the four underwater maps (no Dive spot leads to them before Phase 4; renders `interiors/<Map>/preview.png`).
- Sapphire/Ruby without a build: Sapphire caves rebuilt with the new models_cave.py are byte-identical to work/interiors
  (Granite 1F, Meteor Falls 1F, Underwater3, Cave of Origin B4F); gen_caves' Sapphire recipe list = HEAD's; dive.py's
  Sapphire table = HEAD code's (SHA-1 48bb4070...); zone_effects' Sapphire and Ruby zone sets = HEAD's; every other
  change is behind `version.is_emerald()`, an `emerald/` file or an Emerald-only key.
- Emerald test ROM (HOENN_TEST_WARP + NO_WILD): rom_emerald/hoenn.nds c52d0c24...; menu save margin 28,896 B.

### New areas for the glitch-check agents
Magma Hideout (8 rooms, Jagged Pass door); Mirage Tower 1F-4F (Route 111 door); Terra Cave entrance/end; Marine Cave
entrance/end + Underwater_MarineCave; Underwater_Route105/125/129; Artisan Cave 1F/B1F (Frontier doors); Desert
Underpass (+ the tunnel's north door); Meteor Falls Steven's Cave (+ 1F's new mouth); Cave of Origin 1F/B1F (Emerald);
Seafloor Rooms 2/3 (Emerald); Victory Road B1F/B2F (Emerald); Underwater3 (Emerald); Mt. Pyre 2F/3F/6F, Aqua Hideout B1F
(Emerald); Sky Pillar 1F-5F clean floors.

## Rooms (emerald_rooms, 2026-10-12)

**The rooms Emerald redrew are built as Emerald-only variants** (Sapphire's and Ruby's rooms, scripts and files
unchanged: checked without a build, below). Generator: `b2tools/emerald_rooms.py` (+ `b2tools/emerald_gyms.py` for the
Gyms); `python3 emerald_rooms.py` rewrites every file below, `--check` only says what would change (nothing, today).

### How it works
- **Variants**: `data/interior_layouts/<Room>_Emerald.json` with `"map": "pokeemerald/<Folder>"` (pokeemerald read
  directly: `models_interior.map_source`; emerald_caves' `"emerald/<Map>"` is the Emerald view), the gyms_league /
  centers recipe rules applied to Emerald's map. `data/versions.json room_variants.emerald` installs a variant for its
  room; `"rooms"` lists every variant as `"emerald"`, so no Sapphire/Ruby build or checker sees it.
- **Zone jsons**: where Emerald moved warps or people, `data/interiors/emerald/<zone>.json` (Sapphire's json + the
  changes, positions in Emerald map tiles; written by the generator). Other layouts of a room are `"alt_rooms"` there
  (the Lab's table, Mauville's beams), switched by a map replace event that the zone init sets on **every** load, which
  lets two rooms share one event (all ten are taken): event 4 = Mauville Gym "off" and the Lab's table.
- **People**: Sapphire's story objects get `at_emerald` / `dir_emerald` / `move_emerald` / `skip_emerald` where Emerald
  moved them (a trainer matched by its Black 2 trainer id in `data/emerald/hoenn_trainers.json`); Emerald's extra Gym
  trainers are new objects in `data/story/emerald/e_rooms.json` (script 3000 + id, defeat flag id + 1520), and
  `hoenn_story.inc h_set_gym_trainers` marks them beaten with the leader (Emerald branch). Report:
  `work/agents/emerald_rooms/gyms_people.txt`.
- **Scripts**: Emerald-only entries are `#ifdef HOENN_EMERALD` blocks between `// >>> emerald_rooms <name>` and
  `// <<< emerald_rooms <name>` lines in the Gym's own script file (0050 Dewford, 0478 Mauville, 0290/0296 Lavaridge,
  0046 Sootopolis, 0644 Mossdeep) and `src/include/hoenn_story.inc`; the generator rewrites them. League 2F is a new
  Emerald room: zone 344, scripts 688/689, text 556 (`src/field_scripts/emerald/0688_...`, `data/emerald/hoenn_interiors.json`).

### What is built (Emerald build only)
| Room | What Emerald changes, as built |
|---|---|
| Rustboro Gym | Emerald's maze; Josh/Tommy moved, Marc new |
| Dewford Gym | Emerald's room; the darkness shrinks per trainer beaten (`Sub_DG_FlashTargetEm`: 24 px + 8 px per trainer, 6 trainers); Cristian/Lilith/Brenden new; the 2 statue signs off |
| Mauville Gym | Emerald's beams from Sapphire's Special2/3 logic on Emerald's map (normal / alt / off as alt rooms), **4 switches** (the 4th `MG_Switch4Em` at (8,9)); Angelo new |
| Lavaridge Gym 1F/B1F | Emerald's 17x19 floors; 24 holes drop to B1F, vents blow back up (step triggers `EL_Hole`/`EL_Vent`, Emerald's warp order in the overlays 145/148); Keegan moved to B1F; Jace/Jeff/Eli new |
| Petalburg Gym | Emerald's room; Norman one row up on the mat |
| Fortree Gym | Emerald's room (no rotating gates: none are built in any version); Humberto/Darius new |
| Mossdeep Gym | Emerald's 26x36 floating rooms, **the rotating-tile puzzle** (below); 6 new trainers; 4 Sapphire signs off; statues = rock objects (Black 2 has no statue person) |
| Sootopolis Gym 1F/B1F | Emerald's thin ice (5 new triggers, 7 Sapphire ones off; 3rd ramp at 67 steps, Sapphire 69), wider B1F (origin (1,-4)), fountains; Daphne/Annika new; **Wallace still stands where Emerald has Juan (story)** |
| Birch's Lab | variant + table layout (alt room, event 4); Johto starters switched on (`EMJ_JOHTO_ON 1`, `data/story/emerald/e_ch11_johto.json`) |
| 15 Center 2Fs | Emerald's 2F (+1 row: counters and the escalator one row down), warps trimmed to Emerald's 3 |
| League 1F + new 2F | escalator to the new 2F (zone 344, Center 2F layout, bgm 1060), plants, table |
| Devon 1F/3F, Flat 1 2F, Fan Club, May's 2F | Emerald's furniture (Devon 1F displays, Flat 1's rug and table, May's pink rug) |
| Mossdeep Game Corner | Emerald's 1F (boards, blocked counter; signs off); its basement warp is moved off the map by the zone init |
| Contest Lobby | Emerald's 31x12 lobby; ch8a's 5 people `at_emerald` |
| Lilycove elevator, BT elevator, BT lobby | Emerald's floors; the lobby's 4 booths, warps and 4 people moved |
| Trick House puzzle 1 | Emerald's fences/boxes, scroll at (3,16), an item ball (flag 1266) |

**Mossdeep's puzzle** (`emerald_gyms.py mossdeep`, measured in rotating_tile_puzzle.c): the pads are step triggers that
set the player on the partner pad with `ActorSetGPos 255` (a map change to the same zone hangs), so objects stay put, as
Emerald; each color switch (`EMG_Switch<Color>`) walks every object on that color's 2x2 arrow squares one tile
counter-clockwise and turns it, from the color's press count (works 0x4011-0x4015, cleared on entering, as Emerald resets
the objects): positions follow from the counts, nothing is read at run time. Solvable route found offline
(`work/agents/emerald_rooms/tools/mossdeep_solve.py`) and walked in game (117 steps to Tate & Liza).

### Not built (and why)
- **Marts**: Emerald's only change is the Mystery Gift questionnaire sheet (Black 2 has no such feature). **May's 1F,
  Brendan's 2F**: nothing visible changes in Black 2's art. **Lilycove unused mart**: unreachable in both games.
- **Trick House puzzles 2-8**, Fortree's rotating gates (no version has them), the Battle Tower lobby's other 3
  receptionists, Emerald's link attendants / record boards / Mystery Gift man / Devon display signs (story or Phase 4).

### For the story agents (Emerald positions, map tiles)
- Leaders: Brawly (4,3), Wattson (5,2), Flannery (13,9), Norman (4,2), Winona (15,2), Tate & Liza (23,7)/(24,7) (on the
  solid dais, talked to from row 8), Wallace -> **Juan** at Sootopolis (8,2) still to do. Guides moved: Rustboro (3,18),
  Lavaridge (12,16), Fortree (15,21), Mossdeep (5,33).
- Mossdeep: ch9's trigger (12,3) is at (21,6); `MG_ENTRANCE` is (7,30). Mauville: ch3b's switch triggers at (0,15)
  (4,12) (3,9) + (8,9). Contest Lobby: ch8a uids 1, 2, 6, 10, 14 moved (`at_emerald`). Center 2F attendants still
  say Sapphire's "not ready" lines.

### Checks and proofs (work/agents/emerald_rooms/)
- Checkers on the Emerald ROM (`tools/checks.sh`, logs `checks/`): check_exits 0 outdoor/dynamic differ (12 room-to-room
  report-only: Lavaridge's Emerald warp order, 3 Littleroot by hand); door_check 165 doors, 0 findings; walk_diff OPEN 665
  (baseline 712); script_check ent 8 / mapc 15 / path 120 (Mossdeep's ~110 paths = the checker replaying every
  press-count branch from the start tile; Lavaridge mapc = Sapphire's unused warp scripts; Lab balls on the table and
  Tate & Liza on the dais are on solid tiles by design; the rest are other agents'); rooms_check e 36 (baseline 118),
  new: Game Corner basement warp (moved off-map at run time), Lab balls in the normal layout (shown only with the
  table), people cut by low walls (Dewford/Fortree, the known class), the Lilycove elevator head at (0,3);
  scene_walks 2 (Mossdeep branch artifact, truck skip).
- Played (muted DeSmuME, `tests/em_rooms.py <place>`, shots `screenshots/emerald_rooms/`): every changed Gym through its
  puzzle to the leader (Rustboro, Dewford darkness, Mauville switch -> beams swap, Lavaridge hole -> B1F -> vent -> 1F,
  Fortree, Petalburg, Sootopolis 7 thin-ice tiles -> ramp, Mossdeep full route), the Lab's Johto starters (table,
  Cyndaquil, "leave the others alone"), a Center 2F (counter, escalator down/up), League 1F -> 2F, Contest Lobby, BT
  lobby, Game Corner. The kit needs a test ROM `rom_emerald/emr_test.nds` (HOENN_TEST_WARP=563,6,7 HOENN_TEST_CHJOHTO=1
  HOENN_TEST_PARTY=1 HOENN_TEST_NO_WILD=1) and `states/base_littleroot.dst`; `beat()` marks a Gym's trainers beaten so a
  walk tests the room, not the battle bot.
- Sapphire/Ruby without a build: the 292 field scripts that see an emerald_rooms block, assembled for Sapphire and Ruby
  with and without the blocks: 581 assemblies, 0 differ; ch1/2/3b/5/7/8a/9/10.json equal HEAD's without `_emerald` keys;
  every Python change is behind `version.is_emerald()` or an Emerald-only room name.
- Emerald ROM `rom_emerald/hoenn.nds` 8fe0c1a4...; menu save margin 28,896 B (unchanged).

### New areas for the glitch-check agents
The 8 Gyms (Emerald), 15 Center 2Fs, League 1F + 2F, Birch's Lab (table), Contest Lobby, Lilycove and Battle Tower
elevators, Battle Tower lobby, Mossdeep Game Corner, Devon 1F/3F, Flat 1 2F, Slateport Fan Club, May's 2F, Trick House 1.

## Cave polish (emerald_polish_caves, 2026-10-12)
Emerald's new and changed caves checked (caves_check abcefhistwx, rooms_check, walk_diff, a muted DeSmuME sweep from
several spots per room: `screenshots/emerald_polish_caves/before|after/`) and fixed. Every builder change is behind
`Cave.emerald` (recipes `"emerald/<Map>"`); Sapphire/Ruby caves rebuilt with the new models_cave.py are byte-identical to
work/interiors (12 checked: Fiery Path, Granite, Victory Road, Meteor Falls, Cave of Origin + Ruby B4F, Underwater3,
Seafloor Room 9, Navel Rock, Rusturf).
- **Smeared rock faces** (Desert Underpass chunks 3-4, 18 faces): `centre_uv(m, sizes)` moves a triangle still past
  the DS's +-2048 texels on its own by whole repeats (face u runs +x on north walls and -x on south walls: no single
  shift fits a far chunk).
- **Door tops** (Magma Hideout 1F, 2F_1R, 2F_3R, 3F_1R, 3F_3R): Lavaridge's doors are 2 tiles tall; the walkable upper
  tile was drawn as floor and the arch opened into a black square: recipe `void`. caves_check: a door tile is left
  southwards only (report-only checker; Sapphire's w findings unchanged).
- **North doors floated 32 units up** (in81 `arch_n`, chunk 740's floor is at 32): `_looks.json` `"base_y": 32`
  (only Emerald's Magma Hideout uses that template).
- **Up-ladder notches** stood out of the wall as 2-tier boxes with a black lid (Cave of Origin B1F, Artisan B1F,
  Mirage Tower 1F/3F, Victory Road B1F/B2F): `ladder_up_notch` follows the rock beside it (stairs to the first tier's
  top, side walls between the stairs and the rock). A ladder whose top tile stands free (Mirage Tower 2F (18,11),
  Victory Road B1F (42,25)) keeps it as rock with the short flight (it was a hollow black box on the floor).
- **Exit arches at the map's edge** (Terra Cave entrance, Mirage Tower 1F, ...) hung their tunnel/white ground past
  the edge as a box over the black: template vertices pressed onto the map's extent.
- **Seams** (black pixel dots on floors, thin lines on rock tops: T-junctions): `seam_cover` - a floor copy 2 under
  merged column-wise, a rock-top copy 4 under (the mist caves' cover; underwater maps have their own backdrop).
- **Mt. Pyre 2F**: Dez & Luke `at_emerald` (2,9)/(3,9) (they stood in Emerald's gravestones).
- Magma Hideout story objects (16 grunts, Tabitha, Maxie, both Groudons, 7 balls, 3 boulders): every one on Emerald's
  tile, on flat floor (no raised ground in the hideout), sight lines the same tiles as Emerald; Groudon in the lava
  pool (cell -8). Nothing to move.
- **All versions since v16.7** (work/agents/emerald_polish_caves/v167.patch, on v16.6 + rods/dewford/music): the
  ladder notches, lone ladder tops, map-edge exits and seam cover are no longer Emerald-only (Sapphire/Ruby: 60 cave
  chunks change, a/0/0/8 only); Victory Road B1F's recipe `"seam_cover": false` (its chunk 1 passed the 110,600-byte
  buffer with it; a dark cave); Aqua Hideout B1F `unblock` 12 tiles beside its furniture (ship_hideouts_rooms.py; the
  Emerald variant inherits them): walk_diff OPEN 11 -> 0.
- Left: exit arches over a lower rock show the template's top as a glow/hump with 1-3 px white specks beside outside
  exits (all versions: the rock beside an exit would have to rise to the template's 32 units); 6-13 px holes only in the
  checker's yaw +-20 views (the game camera is yaw 0); Ruby's Magma Hideout rooms' blocked tiles beside furniture.

## Outdoor polish (emerald_polish_outdoor, 2026-10-12)
Areas: Route 103's east half and the Oldale seam, the Jagged Pass mouth (sealed/open), Route 111 (Mirage Tower, Trainer Hill,
the desert's south edge, Desert Ruins), the Safari expansion, the Terra/Marine spots' default ground. All changes Emerald
only (gates: `version.EMERALD`; proof without a build: work/agents/emerald_polish_outdoor/proof/sapphire_ruby_gate.txt).
- **Cave mouths** (terrain/cave_mouth.py): `span()` gives a mouth Sapphire's 1-tile opening (OPENING 1 geometry) where the
  rock beside the door is under 2 tiles wide: the Magma Hideout mouth's Black 2 frame stood half over the stairs and in the
  open beside the 3-wide outcrop. **Pillar mouths**: a door in a free-standing 3x2 rock block with open ground behind
  (the Mirage Tower stand-in) is a 2-tier block with a doorway (`_doorway`: dark back, floor, lid, rock over the opening);
  the portal template had left 85 px of holes and see-through faces and its back wall stood out of the block's top.
- **heights.py** (Emerald, maps in POLISH_MAPS / MOUTH_ROW_MAPS): 9a' a boulder tile lower than the rest of its boulder by the
  sea is drawn at the boulder's height (Route 103 (40,6): a tan lip ring in the sea); 9c'' a boulder whose walkable
  neighbours stand at one height above it rises to them (Jagged Pass (18,15): it sat in a 16-deep pit by the mouth, the
  "odd rock piece"); step 10 rock with no walkable tile, by the sea at the sea's level, takes rocky ground by its own land's
  majority (Route 103's grass corner on pink rock); 9d leaves the row behind a mouth's door to the mouth on Route 111 (the
  Desert Ruins showed two tan squares inside the opening: world.py's ground came up under the cut).
- **Trainer Hill** (data/towns/emerald/Route111.json): its footprint is retiled as the hill (rock), so the stand-in stands on
  the hilltop (it stood in a pit with sand strips beside it).
- outdoor_check.py: a warp-only group's other layout is its own frame (`alt_JaggedPass`); its door-top tile accepted.
- Checks (HEAD + these files, world work/agents/emerald_polish_outdoor/world_snap): outdoor_check open place/size/walk/door/
  bld/zone/tex 0; layer 40 -> 41 (alt_JaggedPass now checked: its ledge-lip seam, the sealed frame's own), cull 243 -> 242,
  hole 24 -> 22; walk_diff OPEN 32 -> 32 (all Sapphire's own leftovers); door_check 165 doors 0. Emulator (one pass per area,
  screenshots/emerald_polish_outdoor/): Magma Emblem scene, open mouth, door -> Magma Hideout 1F; Mirage Tower door -> 1F;
  every Jagged Pass actor stands on its ground. Save margin 28,896 B.
- **Open bug for the story agents**: Route 103's Altering Cave door (45,6) fires before the game is clear in Emerald (its
  approach row 7 is walkable land in Emerald's map; Sapphire's has the sea): walking north into the cliff at world
  (213,286) warps into an unbuilt zone (zone 0, a Unova street, in a test build). Park it in Sub_AC_Door's Emerald pre-clear
  branch (scenes/Route103_AlteringCave.inc) with ObjInitWarpGPos, as Jagged Pass's JP_HIDEOUT_WARP.
- **v16.7 (Sapphire/Ruby)**: work/agents/emerald_polish_outdoor/v167.patch (after rods, dewford, music) ungates two of these
  for every version: 9d leaves the row behind every mouth's door to the mouth (the light squares in the Desert Ruins'
  opening), and ground.py gives a mouth's door tile the approach's sand (the green edge under the floor's transparent
  front notches on sand). Main tree: the same, ungated. The step-10 sea-rock rule stays Emerald-only (ungated it turns
  1,594 sea-side rock tiles of 30 Sapphire maps rocky: unreviewed, so Sapphire's Route 103 grass corner stays open).
