# Pokémon Emerald NDS: Phase 3 (story) scope (emerald_story_scope, 2026-10-12)

Read-only scoping. Nothing was built, no emulator was run, nothing was downloaded, and this is the only file written.
Facts come from: notes/EMERALD_AGENT_BRIEF.md, EMERALD.md, EMERALD_PLAN.md (1.2, 4), DECISIONS.md (end), RUBY.md (WP0-WP3),
STORY_CHAPTERS.md, STORY_PORTING.md, STORY_COMMON.md, `work/agents/emerald_plan/story_beats.md` (cited **SB §n**), the scene
files in `src/field_scripts/scenes/` and `src/text/scenes/`, the Ruby overlays (`src/field_scripts/ruby`, `src/text/script/ruby`,
`data/story/ruby`), `data/versions.json`, `converter/gen_map_content.py`, `gen_interiors.py`, `b2tools/patches/story.py`, and
pokeemerald's scripts. `E:Map:123` = `external/pokeemerald/data/maps/Map/scripts.inc` line 123; `Es:` = `data/scripts/`.

**How sizes were measured.** A throw-away script (scratchpad, not in the repo) parsed pokeemerald's scripts.inc files and
counted, for each entry script, the commands of every label it reaches in the same file: **L** = script commands (movement lists
and text excluded), **T** = `.string` text lines. One Emerald L line becomes about 1.0 to 1.3 port lines (checked on Mt. Chimney:
pokeruby 95 L, the HoennB2 port about 85 lines with comments, movement included). Reach counts can include a few helper labels, so
read them as "about". Text-pass numbers (same / near / new lines) are SB's `out/text.json`, an upper bound.

**What I read (in full or the key parts):** the Ruby machinery, `gen_map_content.py`, `story.py`, HoennB2's Mt. Chimney / Mt. Pyre / Sootopolis /
Sky Pillar Top / game-clear / post-game National Dex scenes, and Emerald's Petalburg Scott, Route 104 + Rustboro rival, Slateport
Scott, Mt. Chimney (first 130 lines), Mt. Pyre Summit, Magma Hideout 4F Maxie, Jagged Pass, Space Center 2F Steven, Room 9
(end), Cave of Origin Wallace, Sootopolis map scripts, Sky Pillar Outside/Top, Route 131, Mirage Tower 4F + Route 111 sinking,
Wally's dad, Mom/Lati TV, hall_of_fame.inc, the Regi puzzle C code, the Rival 2F scenes. Everything else is from SB's tables plus
the entry/size listing (so label, file:line and L/T are measured, the one-line description is SB's).

---

## 0. Result in plain words

1. **About 320 of Emerald's ~560 story scenes are Sapphire scenes HoennB2 already carries** (SB §1). Of the rest, ~54 are
   changed and ~184 are new, but 98 of the new ones are post-game and 87 of those sit in the Battle Frontier / Trainer Hill /
   Pyramid maps, which the user's decisions keep closed.
   What is left for Phase 3 is **about 60 new or changed scenes: roughly 3,000 Emerald script lines (L) and 1,300 text lines (T)**,
   plus a **text pass** over ~2,000 reworded lines in scenes and NPCs that stay as they are.
2. **Aqua places stay Sapphire, Magma places become Ruby's.** Emerald uses Aqua as the villain at Petalburg Woods, Rustboro,
   Rusturf, Slateport, Route 110, Weather Institute, Route 121, Mt. Pyre, Lilycove, Aqua Hideout, Seafloor Cavern; Magma at Route
   112, Meteor Falls, Mt. Chimney, Jagged Pass, the new Magma Hideout and the Space Center (SB §1, table "Who appears where").
   So Ruby's flow is the base for three scenes (Route 112, Meteor Falls, Mt. Chimney), but **Ruby's machinery cannot be reused
   as is** (section 2.2): Ruby swaps both teams everywhere, Emerald swaps them per place.
3. **The biggest single block is Chapter 10** (~1,150 L, ~500 T): Sootopolis City alone is 678 L in Emerald against 222 L in
   pokeruby. Then Ch9 (~290 L, with the Steven tag battle), Ch13 without the Frontier (~370 L), Ch0 (~250 L), Ch4 (~210 L).
4. **Three things must exist before any chapter builder starts (section 2.4, "S0")**: (a) an Emerald mode of the three
   generators that write every ordinary NPC, sign and trainer NPC (`gen_map_content.py`, `gen_trainer_npcs.py`,
   `gen_interiors.py`: they read pokeruby only today, and EMERALD.md's TODO EMERALD-3 names only the first two); (b) scene
   `ScriptEntry` counting per version (otherwise adding one Emerald-only trigger renumbers Sapphire's generated NPCs); (c) the
   ids / trainer constants / sprite rows for Emerald-only characters.
5. **Chapters that need no new map go first**: Ch0, 1, 2, 3, 6, 7, 11, the team swaps of Ch4 and Ch5, and Mt. Pyre in Ch8
   (~1,000 L). Chapters waiting on the world agent or on Phase 4: Magma Hideout (Ch8), Space Center and Mossdeep Gym (Ch9),
   Mirage Tower (Ch4), everything in Sootopolis / Sky Pillar (Ch10), Steven's Cave / Marine and Terra Cave / Safari expansion
   (Ch13), the Regi puzzles (Ch12).
6. **Biggest risk: trainer ids.** Of the 518 Emerald trainers named in the Ch0-Ch12 map scripts, **161 have no Sapphire slot**
   (106 route / cave trainers, 30 grunts, 15 gym trainers, 6 rival fights, 4 Maxie / Tabitha) and HoennB2's registry has 33
   spare ids. Phase 1's Emerald registry has to re-use the ids of Sapphire trainers that Emerald drops; no scene that names a new
   trainer can be finished before it exists (Appendix B).

---

## 1. The user's decisions that shape the story

(DECISIONS 2026-10-11, EMERALD_PLAN §4, all recommendations accepted.)
- **1A**: Emerald's Frontier island with our Battle Tower and the PWT; the other six facilities stand but are closed. So Scott's
  Frontier lines stay, and `BattleFrontier_ReceptionGate` / Frontier Pass are story (Ch13), the Frontier facilities are not.
- **2**: Trainer Hill and the three Battle Tents are closed buildings. Their Scott scenes (`E:SlateportCity:835`, Verdanturf :249,
  Fallarbor :238) go with them.
- **3A**: no Match Call list, no rematches. The ~15 "Registered X in the PokéNav" moments and the 7 `pokenavcall`s play as plain
  messages; the 76 `register_matchcall` lines on route trainers are dropped (no-ops).
- **5**: Emerald's story places yes (Magma Hideout, Space Center tag battle, Sky Pillar and Sootopolis, Juan, Mirage Tower, Desert
  Underpass, new Regi puzzles), post-game yes (Steven in Meteor Falls, Marine / Terra Cave, Safari expansion, National Dex +
  Johto starters, Lati by colour); Contests, Union Room / Mystery Events House, Berry Crush, Walda, Fan Club TV left out.
  The Walda's-dad wallpaper phrase NPC (`E:RustboroCity_Flat1_2F:4`, 45 L / 62 T) becomes a plain talker.
- **8**: same house rules as HoennB2 (Birch's four questions, Exp. Share, HMs without the move, levels on the curve).
- Dive / event islands / roamers / Hoenn music etc. are unchanged shared systems.

---

## 2. How Emerald branches get written

### 2.1 What Ruby did (the precedent, measured)

| Piece | How Ruby did it |
|---|---|
| Scene code | scenes keep the **same ScriptEntry list in both versions**; only `scenes/Route128.inc` has `#ifdef HOENN_RUBY` (brighten effect). All else reads `src/include/hoenn_version.inc` aliases: `SPECIES_GROUDON_OR_KYOGRE`, `SPECIES_LATIAS_OR_LATIOS`, `ITEM_RED_OR_BLUE_ORB`, `MODEL_*` (used by `0206_room_CaveOfOrigin_B4F.s`, `MtPyre_Summit.inc`, `MtPyre_Summit_Ch10.inc`, `SouthernIsland_Interior.inc`, `LilycoveCity_Harbor_Ch13.inc`) and 28 trainer aliases (`TRAINER_MT_CHIMNEY_GRUNT_3` ...) |
| Text | `converter/gen_ruby_text.py` pairs every Sapphire line with its Ruby twin (pokeruby's `.else` of the same `.ifdef`) and writes whole-file copies `src/text/script/ruby/NNNN_*.txt` at the **same line indices** (99 lines in 23 files + 13 trainer messages) |
| Trainers | the 28 Ruby aliases **take the Black 2 id of their Sapphire twin** (`src/trainers/ruby/` 21 files; classes 187-192 turn into Magma through `data/ruby/hoenn_trainer_classes.json`) |
| Art | a **global swap** of Aqua and Magma art codes (`overworld/ruby/...copy_of`), so `data/story/*.json` needed 0 edits; `model_ruby` on 4 legendary objects |
| Rooms | `src/field_scripts/ruby/0456/0462/0468` (Magma Hideout 1F/B1F/B2F), `data/story/ruby/ruby_maps.json`, `ruby_scenes.json`, `room_variants.ruby` for Room 9 / B4F |

### 2.2 Why it does not carry over to Emerald

1. **Team per place, not per game.** Emerald needs Aqua at Petalburg Woods and Magma at Mt. Chimney in the same ROM. A global art
   swap is wrong; the 13 + 7 team objects of Ch5 / Ch4 (`data/story/ch5.json`, `ch4.json`) need a **per-object `model_emerald`**
   (the key exists in `patches/story.py`: `model_<version>`). Ch5's Mt. Chimney: Archie 353, Maxie 303, Matt 88 + 7 Aqua grunts 293
   + 3 Magma grunts 302 swap roles; Ch4: Route 112 (2 grunts) and Meteor Falls (5 objects). Everything in Aqua places keeps
   Sapphire's models.
2. **Text is Emerald's own.** Emerald's Mt. Chimney contains only 35% of pokeruby's Ruby-side text (SB §1), so Ruby's twin files
   are a wording guide, not a source. Emerald text comes from pokeemerald labels through `gen_trainers.load_texts(root)`
   (already takes a decomp root) + `gen3text.convert(expand=True)` with `HOENN_VERSION=emerald` (its `{AQUA} {MAGMA} {ARCHIE}
   {MAXIE} {KYOGRE} {GROUDON}` placeholders exist, EMERALD.md).
3. **Emerald adds scenes; Ruby never did.** Adding a trigger to a generated outdoor map changes `n_story` in
   `gen_map_content.py` (`scene_files()` counts `ScriptEntry` lines by regex, `#ifdef` ignored), which renumbers every generated NPC of
   that zone in **all** versions. See S0-2.
4. **Trainers cannot be role-twins by slot alone.** Emerald's Maxie at Mt. Chimney is #602, not Sapphire's #35 (`TRAINER_ARCHIE_3`).
   Phase 1's Emerald registry decides which Black 2 id holds him (Ruby gave him #35's id); the scenes then need an Emerald alias
   block in `hoenn_version.inc`.
5. **Both teams need classes and art at once** (Ruby's Magma classes replace Aqua's): Phase 1 class slots + Phase 5 art for
   Tabitha (Ruby's art lives in Ruby-only folders; Matt keeps code 88 in Emerald, so Tabitha needs another code).

### 2.3 Rules for Emerald branches (so parallel builders do not collide)

- **Scene bodies:** `#ifdef HOENN_EMERALD` first, then the Ruby / Sapphire test (EMERALD.md). Big Emerald-only scenes go in a new
  file `src/field_scripts/scenes/emerald/<Name>.inc`, included from the shared scene under `#ifdef HOENN_EMERALD`, so the shared
  file diff stays small. Sapphire / Ruby output must stay byte-identical (brief): rerun the generators in Sapphire mode and diff.
- **ScriptEntry lists:** Emerald-only entries go **at the end** of the list under `#ifdef HOENN_EMERALD`; S0-2 makes the generator
  count per version. Rooms (`NNNN_room_*.s`, numbers in `data/story/*.json`) have no such problem.
- **Text:** `src/text/scenes/emerald/<Map>.txt` (replaces the Sapphire scene text in an Emerald run: Sapphire's lines at their
  indices, reworded lines replaced, Emerald-only lines appended) and `src/text/script/emerald/NNNN_*.txt` (loader exists).
- **Story objects:** a **new file** `data/story/emerald/e_<chapter>.json` adds objects (new key = added, `patches/story.py` +
  `version.overlay`); `model_emerald` on shared objects; a same-named file replaces a whole chapter file (avoid).
- **Rooms:** whole rooms Emerald-only or with a different generated head live in `src/field_scripts/emerald/NNNN_room_*.s`;
  S0-3 must make the generator copy the shared file's `// ---- story` tail so the story code is not duplicated.
- **Coordinates:** `data/story/*.json` places an object by Sapphire map + Sapphire tile. For maps whose ground changed (`maps.emerald.ground`: 118 maps, 28 resized,
  e.g. Route 103, Route 109, the Gyms, Mossdeep) a new Emerald object must use pokeemerald's own x, y plus the offset emerald_world states for that map; builders must not
  assume Sapphire's tiles there (the chapter lists name the affected maps under "Needs").
- **Ids:** claim from the chapter's reserved block (`data/story_ids.json`, `gen_story_ids.py`); Emerald's renamed ids map to
  HoennB2's through aliases in `hoenn_version.inc` (list per chapter below).
- **Never** put Emerald code outside `#ifdef`/`emerald/` folders; each builder builds in its own folder with
  `HOENN_VERSION=emerald HOENN_AGENT=<you> HOENN_SKIP_UNBUILT_ROOMS=1 zsh b2tools/story_build.sh`, makes savestates on the
  Emerald ROM (a state carries arm9: RUBY.md), and reports the save margin and the a/0/5/6 and a/0/0/3 fill (RESERVE 1 MB each,
  `build_rom.py:68` stops if exceeded).

### 2.4 S0: the shared work that comes first

| # | Task | Why | Size |
|---|---|---|---|
| S0-1 | `gen_map_content.py` Emerald mode: reads pokeemerald's map.json + scripts through `data/sapphire/emerald/<Map>.json` (`sapphire_data.py` already has it), writes `src/field_scripts/emerald/NNNN_auto_*.s` + `_init.s`, `src/text/script/emerald/NNNN_auto_*.txt`, `data/emerald/hoenn_content.json`; `b2tools/world.py:72` reads `data/hoenn_content.json` directly, so the Emerald world needs the overlay read (world.py is emerald_world's file: coordinate) | every ordinary talker, sign, item ball of ~100 outdoor zones; 819 lines are new and 606 reworded (SB / EMERALD_PLAN 1.2) | M |
| S0-2 | version-aware `ScriptEntry` count: replace the regex in `scene_files()` / `scene_sign()` by `clang -E -P -D SCENE_ENTRIES -D HOENN_<V>` (the assembler already uses clang); Sapphire / Ruby counts must come out unchanged | Emerald-only triggers (Scott x4, rival x8, Jagged Pass has no scene file at all in Sapphire, Sootopolis 15 entries -> ~25: Emerald's map has 19 distinct scripts plus 3-4 frame / init scripts) | S |
| S0-3 | `gen_interiors.py` (rooms' people, signs, scripts, text) and `gen_trainer_npcs.py` Emerald modes. EMERALD.md assigns rooms to EMERALD-2 and lists `gen_trainer_npcs` under EMERALD-3; `gen_interiors` appears only as "Sapphire's (the shared run)" in its readers table, in no TODO EMERALD-n. Proposal: S0 owns scripts / text, emerald_world owns geometry (`data/interiors/emerald/*.json`) | rooms' NPC lines, trainers' placement | M |
| S0-4 | ids: one **"Emerald" reserved block** of ~150 flags and ~40 works carved out of the unused reserves of S_common / Events / Postgame / Postgame_maps / Berry_trees / Battle_tower (`gen_story_ids.py` gives every chapter only 16 flags / 6 works; Ch0, 4, 8, 9, 10, 13 need more, section 5.3); Emerald additions in `hoenn.h`; Emerald `Sub_NewGameFlags` generated from `E:data/scripts/new_game.inc:115` (~150 setflag; today `scenes/new_game_flags.inc` is generated from pokeruby); alias table for renamed Emerald ids | all chapters | S |
| S0-5 | `hoenn_version.inc` Emerald block (trainer constants once Phase 1 names them, Lati / orb values), `data/emerald/sprite_map.json` rows (Scott, Tabitha, Juan, Magma / Aqua unswapped; Sapphire's sprite_map has no SCOTT, JUAN, TABITHA), `model_emerald` rows | all chapters | S |
| S0-6 | test harness: `HOENN_TEST_CH<n>` start states for Emerald (flag chains differ), Emerald base savestates, `script_check.py` and `progression_check.py` runs on the Emerald ROM (both are version-aware) | acceptance of every chapter | S |

### 2.4.1 S0 status (emerald_s0, 2026-10-12)

Done and checked (Sapphire and Ruby unchanged: proofs in emerald_s0's report, `work/agents/emerald_s0/`):
- **S0-2 done.** `converter/gen_map_content.py` reads each scene's ScriptEntry list through the preprocessor, as the ROM
  does (`scene_entry_lines(name, version)`: `clang -E -P -C -D SCENE_ENTRIES -D HOENN_<V>`), so an entry under
  `#ifdef HOENN_EMERALD` counts in Emerald only. A Sapphire run stops if a scene's Ruby list differs from Sapphire's (both
  assemble the same generated file). Rule for builders: Emerald-only entries go **last**, under `#ifdef HOENN_EMERALD`;
  they take effect in the Emerald build only once the Emerald run of the generator has written that zone's
  `src/field_scripts/emerald/` file (S0-1). (Rooms count nothing: their numbers are in `data/story/*.json`.)
- **S0-4 done.** `converter/gen_story_ids.py` has the group **Emerald**: 152 flags and 40 works carved once from unused
  reserves (S_common, Events, Postgame, Postgame_maps, Berry_trees, Battle_tower keep 2 flags / 1 work each; Ch0-Ch12 gave
  their 5 highest unused flags; 6 flags / 15 works no group held; the test kits' marker flags 539, 750, 1513, 2432, 2433,
  3042 are never carved). Claim Emerald ids with `python3 converter/gen_story_ids.py --claim Emerald NAME ...` (pokeemerald's
  names; a chapter's own reserve still works: `--claim Ch5 NAME`). Already claimed (cross-chapter): `VAR_SCOTT_STATE`,
  `VAR_SCOTT_PETALBURG_ENCOUNTER`, `VAR_SS_TIDAL_SCOTT_STATE`, `VAR_ROAMER_POKEMON`, the five `FLAG_MET_SCOTT_*` and the ten
  `FLAG_HIDE_*_SCOTT` of the places Emerald keeps. `scenes/new_game_flags.inc` adds, in an Emerald build only, pokeemerald's
  new-game flags that are Emerald ids (5 Scott hide flags today; a claimed name in pokeemerald's list joins on the next run).
  Not done: an alias table for pokeemerald's renamed Sapphire ids (`VAR_LITTLEROOT_TOWN_STATE` = `VAR_LITTLEROOT_STATE`...):
  builders use HoennB2's names, or add `#define` aliases in their Emerald branches.
- **S0-5 done.** `src/include/hoenn_version.inc` Emerald block: legendaries (`MODEL_KYOGRE/GROUDON/RAYQUAZA`), Lati
  (`SPECIES_LATIAS_OR_LATIOS` = the island one for `VAR_ROAMER_POKEMON` 0, `*_LATI_ISLAND_IF_BLUE` for 1), orbs
  (`ITEM_RED_OR_BLUE_ORB` stays Blue for the shared scenes; `ITEM_ORB_OF_AQUA` Red, `ITEM_ORB_OF_MAGMA` Blue; no Magma
  Emblem item yet), `#include "hoenn_trainers_emerald.h"` (emerald_data's names) and the 28 role aliases pointed at Emerald's
  trainers (25 are the same Black 2 id; Mt. Chimney's three are Tabitha, `GRUNT_MT_CHIMNEY_2`, Maxie). `scenes/MtChimney.inc`
  names `TRAINER_ARCHIE_3` directly: B2 switches it to `TRAINER_MT_CHIMNEY_GRUNT_3`.
  `data/emerald/sprite_map.json`: Scott = code 289 (Emerald's own sprite resized, `src/sprites/overworld/emerald/289-scott`,
  `b2tools/sprite_emerald_story.py`; a Black 2 sheet no Hoenn build used), Juan = Black 2's PWT 276 as it is (its up / step
  frames are Black 2's X placeholders; Emerald's Juan only faces down in his Gym), Tabitha = 302 (Emerald draws her with
  the Magma grunt sprite; Ruby's 088 sheet stays Ruby-only), both teams on the shared codes (no swap), Wallace 288,
  Steven 287. Review: `screenshots/emerald_s0/story_sprites_review.png`; in game (Emerald ROM with `HOENN_TEST_SPRITES=345,289`, Littleroot's town sign): Scott walks down, right, up and left, `screenshots/emerald_s0/scott_ingame_*.png`. `model_emerald` on the 20 team objects of
  `data/story/ch4.json` (Route 112, Meteor Falls) and `ch5.json` (Mt. Chimney: Maxie at the machine, Archie asking, Tabitha,
  Magma grunts, Aqua as the other team), matched to pokeemerald's objects by local id and tile. Emerald's grunt 22 stands
  at (9,16), Sapphire's at (9,15); Emerald's object 29 (a female Magma grunt, `TRAINER_GRUNT_MT_CHIMNEY_1`) is new (B2's).
- **S0-6 done as far as the story is known.** `scenes/emerald_test_chain.inc` (`em_test_chain AT`) adds Emerald's own
  state of the earlier chapters (today Scott's chain) to every `scenes/ch*_test.inc` in an Emerald build (all 64 files
  that include a kit assemble with `HOENN_TEST_CH<n>` in Emerald mode). Builders add their beats there when they claim ids.
  `script_check.py` runs on the Emerald ROM: 2 open, both Emerald-only hidden items (Route 105 Big Pearl, Route 123 PP Up)
  that emerald_data placed at Emerald tiles on Sapphire's world (they wait for the Emerald world). **`progression_check.py`
  cannot run on any ROM**: the committed file has no command line and `MaySolver.solve` calls a `View()` it does not have
  (the 2026-10-08 agent was stopped); needs a repair task before the Emerald acceptance step C can use it. Emerald base
  savestate: emerald_data's `work/agents/emerald_data/boot/base_littleroot.dst` (Emerald ROM from HEAD).

Written, not run on Emerald's world yet (it is still being built; run them the day `work/world_emerald/world.json` exists):
**Run on Emerald's world 2026-10-12 (emerald_integrate; notes/EMERALD.md "Integration"): every item below is done, rebuild_slice.sh runs them.**
- **S0-1 (code path written).** `HOENN_VERSION=emerald python3 converter/gen_map_content.py`: pokeemerald's events
  (`data/sapphire/emerald/<Map>.json`: first `cd converter && HOENN_VERSION=emerald python3 sapphire_data.py
  ../external/pokeemerald <every map of Emerald's zones>`), pokeemerald's text, Emerald's world and zones, Emerald item balls,
  Emerald scene counts and `src/text/scenes/emerald/<Map>.txt`; writes only `src/field_scripts/emerald/NNNN_auto_*`,
  `src/text/script/emerald/NNNN_auto_*` (a file equal to the shared one, comments aside, is not written) and
  `data/emerald/hoenn_content.json`. It refuses to run without Emerald's `world.json`. Dry run on Sapphire's world in
  `work/agents/emerald_s0/t_gen`: 342 events in 52 maps, 8 script / 26 text overlays, Emerald's wording (e.g. "Dewford is a
  tiny island community."); a Sapphire run afterwards still gives HEAD's files. Still needed: (1) **world.py must read
  `data/emerald/hoenn_content.json` instead of the shared one** in an Emerald build (`version.overlay_file`, whole file, not
  merged: the labels are pokeemerald's; world.py:72 is emerald_world's), (2) done: `data/emerald/sprite_map.json` `"_gfx_alias"` maps pokeemerald's 16 renamed people (EXPERT_M = Sapphire's OLD_MAN_1, POKEFAN_F = WOMAN_2, NINJA_BOY = LITTLE_BOY_1 ...: same id number and the same drawing, checked side by side in `screenshots/emerald_s0/gfx_alias_candidates.png`); with it the dry run places 342 events and skips 87 for "no Black 2 sprite", the same count as Sapphire's run; Emerald's Vigoroth movers, Route 101 Zigzagoon, dolls, Mystery Gift man and Trick House statue still need rows of their own, (3) rebuild_slice.sh's Emerald block (a shared builder): after Emerald's world.py run, `sapphire_data.py`, `gen_map_content.py` and `gen_trainer_npcs.py` in Emerald mode, then Emerald's world.py once more to place what they made (as the shared block does for Sapphire).
- **S0-3, trainers (code path written).** `HOENN_VERSION=emerald python3 converter/gen_trainer_npcs.py`: Emerald's trainers
  (each once, under its Emerald name), pokeemerald's ranges, Emerald's zones / rooms / world -> `data/emerald/hoenn_trainer_npcs.json`
  (its lists replace Sapphire's in `patches/trainers.py`). Dry run on Sapphire's world: 285 outdoor trainer NPCs (none left without a sprite). Refuses to run without Emerald's world.
- **S0-3, rooms (`gen_interiors.py`): not written.** Its Emerald mode depends on how emerald_world lays out Emerald's rooms
  (variants vs. `data/interiors/emerald/<zone>.json`, `room_variants.emerald`, the name clashes); proposal unchanged (S0 the
  people / scripts / text, emerald_world the geometry), to be done with emerald_world's room round.

### 2.4.2 B3 status (emerald_ch11_gameclear, 2026-10-12): Champion Wallace, Hall of Fame, Scott at Ever Grande, the Lati colour, Johto starters

What exists in an Emerald build (Sapphire / Ruby: their scripts assemble byte for byte as before, proofs in `work/agents/emerald_ch11_gameclear/sr/`):
- **Champion Wallace.** `0068_room_EverGrandeCity_ChampionsRoom.s` battles `TRAINER_WALLACE_EMERALD` (Black 2 trainer id 457, the same id Sapphire's Steven has; emerald_data's party,
  class 193, Black 2's Wallace picture). The object is Wallace's model (`data/story/ch11.json` `model_emerald` 288); the speech, the defeat lines, Birch's Pokédex rating and "come with me" are
  Emerald's, as an overlay `src/text/script/emerald/0041_*.txt` (same rows as Sapphire's file). Played: speech, battle (won with six Lv 100 Groudon), the rival, Birch, Wallace leads you to
  the Hall of Fame; a forced loss (party Lv 1 / 1 HP) ends in the whiteout at home and the player walks again.
- **Hall of Fame + game clear.** `0114_room_EverGrandeCity_HallOfFame.s`: Wallace walks in (`data/interiors/emerald/57.json`, text `0066`), then `HF_EmeraldFlags` adds Emerald's own
  `SetGameClearFlags` lines (`FLAG_IS_CHAMPION`, the five event legends fightable again, `VAR_FOSSIL_MANIAC_STATE` 1, Wally, Safari Zone expansion shown / workers hidden, Steven's house
  ninja boy, Lilycove rival hidden, the Littleroot bedrooms, `VAR_DEX_UPGRADE_JOHTO_STARTER_STATE` 1). `scenes/ch13_gameclear.inc` (`Sub_Ch13_GameClear`) no longer sets `FLAG_SYS_TV_LATI` in
  Emerald (the Lati news is Mom's scene). Played to the credits, THE END, the Emerald title, Continue (the player's room), down the stairs, the S.S. Ticket scene, out of the house: Birch and
  the rival at the door, the Lab, the National Dex upgrade. Ids claimed (group Emerald): `FLAG_IS_CHAMPION`, `VAR_FOSSIL_MANIAC_STATE`, `FLAG_HIDE_SAFARI_ZONE_SOUTH_CONSTRUCTION_WORKERS`,
  `_SOUTH_EAST_EXPANSION`, `FLAG_HIDE_LILYCOVE_CITY_RIVAL`, `FLAG_HIDE_MOSSDEEP_CITY_STEVENS_HOUSE_INVISIBLE_NINJA_BOY`, `FLAG_HIDE_LITTLEROOT_TOWN_BRENDANS/MAYS_HOUSE_RIVAL_BEDROOM`,
  `FLAG_HIDE_SOUTHERN_ISLAND_UNCHOSEN_EON_DUO_MON`, the three Birch's Lab ball flags. **Steven's house:** the shared state stays 1 after the Hall of Fame (this port's 1 is Emerald's 2: Steven
  stands in his house); the Mossdeep builder (B5) renumbers when he rewrites the Dive scene. Nothing in B3's scenes makes Steven the Champion; he is a post-game boss in Meteor Falls (B8).
- **Scott at Ever Grande.** An Emerald overlay of the Center, `src/field_scripts/emerald/0016_room_EverGrandeCity_PokemonCenter_1F.s` (+ `0017_..._init.s`, text row 9 of `0014`): the shared
  Center's scripts 1-5 unchanged (copy a generator change there), script 6 = Scott (object uid 4 in `data/story/emerald/e_ch11.json`, model 289), script 7 = the zone init that shows him once
  the Feather Badge is owned. He cheers you on, walks out of the door (Emerald's two walks by the way you face), `VAR_SCOTT_STATE` +1, `FLAG_MET_SCOTT_IN_EVERGRANDE`. Entering Sidney's room
  (`0158` zone init) sets the same flags, as Emerald. Played.
- **Lati by colour + S.S. Ticket.** `scenes/players_house_1f_ch13.inc` includes `scenes/emerald/players_house_1f_ch13.inc` in Emerald: Dad's ticket (Emerald's shorter lines), Mom walks over,
  "Dad should stay longer", the TV flash (a window: Black 2's TV has no screen), "what color did the announcer say?" with a Red / Blue list (`VAR_ROAMER_POKEMON` 0 / 1), then the roamer:
  `pg_roamer_start 0` (Latias) or `pg_roamer_start 0x100` (Latios). `b2tools/patches/roamers.c` + `.py`: `-DPG_LATI_BY_SEED` (Emerald builds only: Sapphire / Ruby compile to the same bytes,
  checked) keeps the choice in bit 0 of roamer 0's seed and makes `species_of()` pick Latios; the save layout is unchanged. Southern Island (`scenes/emerald/SouthernIsland_Interior.inc`)
  shows the OTHER one: var 0 -> Latios, var 1 -> Latias (two story objects: ch13.json 102 Latios, `e_ch11.json` 103 Latias). Text rows T(24)-T(35) of `0619` / `0621` (new rows 36-40).
  Played: Red path and Blue path (the list, Blue picked, the record's seed bit 1, Latias on the island); Red: Latios on the island. Not played in battle: a roaming Latios.
- **Johto starters: the scene is built, switched off.** `scenes/emerald/BirchLab_JohtoStarters.inc` (hooks: `BirchLab_Postgame.inc` `PG_LabInit`, `0792` entries 15-18, `0793` condition,
  `0625` rows 38-48): states 4-6, Birch's speech, three ball scripts (Lv 5, nickname, "leave the others alone"). `EMJ_JOHTO_ON 0`: Emerald draws the Lab with a table for this
  (`LAYOUT_..._BIRCHS_LAB_WITH_TABLE`: three solid table tiles at (8..10, 4) where this port's room has boxes at (9,4) (10,4)). The balls' objects wait in
  `data/story/emerald/e_ch11_johto.json.off`. Played with `HOENN_TEST_CHJOHTO=1` (state 4 forced): the walk up, Birch's lines, state 5, Birch's repeat line; the ball scripts were NOT played
  (needs the objects: see the test switches below).
  **Now on (emerald_rooms, 2026-10-12):** `EMJ_JOHTO_ON 1`, `data/story/emerald/e_ch11_johto.json` (renamed from `.off`), the table layout is the alt room
  `LittlerootTown_ProfessorBirchsLab_Emerald_Table` of zone 396 on map replace event 4 (`EMJ_EVENT_TABLE`, shared with Mauville Gym's off state: both
  rooms set it on every load). Played: table shown at state 4, Cyndaquil taken, "leave the others alone" (notes/EMERALD.md "Rooms").
- **Test switches (Emerald, test builds only):** `HOENN_TEST_CH11W=1` (one Lv 5 Magikarp instead of six Groudon), `HOENN_TEST_CHJOHTO=1` (Lab state 4), `HOENN_TEST_CHROAM=1`
  (Mom answered Blue, the roamer started at location 0; with `HOENN_TEST_ROAMER_PLACE0=14 HOENN_TEST_ROAMER_ALWAYS=1` it roams on Route 101), `HOENN_EXTRA_STORY=<e_ch11_johto.json.off>`;
  `emerald_test_chain.inc` at 130 sets the Hall of Fame's Emerald flags. `work/agents/emerald_ch11_gameclear/build.sh` + `tests/`.

**Waits for others:**
- ~~emerald_world: a Lab room variant with Emerald's table~~ (done by emerald_rooms, above);
  the S.S. Tidal corridor room (Scott's invitation, `E:SSTidalCorridor:185`, 18 L; `FLAG_HIDE_SS_TIDAL_CORRIDOR_SCOTT`, `VAR_SS_TIDAL_SCOTT_STATE`, `FLAG_MET_SCOTT_ON_SS_TIDAL` exist). The
  League's 2F is not needed by any B3 scene. If a generator later writes `data/interiors/emerald/57.json` or `src/text/script/emerald/0014 / 0041 / 0066 / 0619 / 0621 / 0625`, keep B3's rows
  (`work/agents/emerald_ch11_gameclear/tools/mk_text.py` rebuilds them in place).
- Phase 4 / hoenn_pokedex: the Pokédex area page still marks the roaming Lati as Latias (its species table is fixed): after a Blue answer Latios roams but its page shows no marker.
- B1: Mom's talk after the ticket scene is Emerald's normal talk (`players_house_1f.inc` skips the Sapphire "Dad should stay longer" line in Emerald).

### 2.5 What HoennB2 already has that Emerald reuses

- The National Dex scene from Emerald (`BirchLab_Postgame.inc`, `LittlerootTown_Postgame.inc`), the event islands, tickets and ferry (`LilycoveCity_Harbor_Events.inc`,
  `FarawayIsland_*`, `BirthIsland_*`, `NavelRock_*`), Altering Cave, roamers and Jirachi / Celebi (`postgame_lib.inc`): all written from Emerald's scripts already.
- The alternate-layout machinery (`MapReplaceSetEvent`, `world.json alt_cells`, `alt_rooms`): Mirage Island (event 2), the Sky Pillar islet and Altering Cave mouth (event 7). Sootopolis'
  legends layout, Route 111 without the tower and the six clean Sky Pillar floors are more users of it (Phase 2 / 4 deliver, the story only sets the event).
- The "step trigger that uses the field move for you" (`ch12_lib.inc` `h_field_move_user`) for the Regi doors; Room 9's Archie scene as the template for Maxie waking Groudon;
  closed doors by moving the warp off the map (Lilycove's hideout door, Sootopolis' houses in Sapphire).
- `model_<version>` / `data/story/<version>/` / `hoenn_version.inc`, the overlay loaders and `progression_check.py` / `script_check.py` (both read the ROM's version).

---

## 3. Which team plays the villain, place by place (Emerald)

| Place | Villain | Base for the Emerald scene |
|---|---|---|
| Petalburg Woods, Rustboro theft, Rusturf, Slateport museum + harbor, Route 110, Route 119 + Weather Inst., Route 121, Mt. Pyre, Lilycove, Aqua Hideout, Seafloor Cavern | Aqua | Sapphire (HoennB2 as is, Emerald text) |
| Route 112 cable car, Meteor Falls (steals; Archie chases), Mt. Chimney (Maxie + Tabitha; Archie asks you to stop them) | Magma | Ruby flow, Emerald text, per-object models |
| Jagged Pass guard, Magma Hideout (8 maps), Mossdeep Space Center | Magma | new (Emerald) |
| Seafloor Room 9, Route 128, Sootopolis | both | Room 9 / Route 128 Sapphire (90% same text), Sootopolis new |

---

## 4. Chapter by chapter

Template: **Reuse** (works unchanged, only Emerald text) / **Ruby** / **Emerald branch** (`#ifdef`, same scene) / **New** /
**Flags** / **Needs** (Phase 2 = maps, Phase 4 = mechanics, others) / **Size**. "HoennB2:" names the Sapphire port file to branch.
"Text pass" = lines worded differently in the chapter's maps (SB text.json: near + new, includes the new scenes' own text).

### Ch0 Opening
- **Reuse:** truck ride (`scenes/truck.inc`; `E:InsideOfTruck:16`, 28 L), Littleroot step-off, Mom, moving in, clock, TV,
  Petalburg report (`0778_littleroot_town.s`, `players_house_1f.inc` / `_2f.inc`; `E:LittlerootTown:110` 38 L, `E:BrendansHouse_1F:57,73,80`),
  Route 101 rescue + Birch's bag + Poochyena (`0634_route_101.s`; `E:Route101:19` 22 L, `:214`), keep the starter (`0792_birch_lab.s`;
  `E:Lab:107`, 27 L / 28 T), the Pokédex event (Ch1 owner; `E:Lab:144`). Twin at the north exit and Mom lines: reworded only
  (`E:LittlerootTown:248`, 22 L / 14 T).
- **Ruby:** none.
- **Emerald branch:** the rival's introduction. HoennB2's `players_house_2f.inc` Script_21 (rival at her notebook, "Who are you?")
  is replaced by Emerald's four entry points, two per house: the rival walks in the front door when you step on the 1F stair
  triggers (`E:BrendansHouse_1F:119-137` MeetRival0/1/2; `E:MaysHouse_1F:152-170`), or appears when you examine the Poké Ball in
  the 2F room (`E:BrendansHouse_2F` / `E:MaysHouse_2F:48` RivalsPokeBall -> MeetMay with 4 facings, then `VAR_LITTLEROOT_RIVAL_STATE`
  3). Plus the rival's mom (`E:MaysHouse_1F:86` YoureNewNeighbor, `:110` RivalMom), the new rival sibling NPC (`:136`, 6 L), the 2F
  "getting ready" talk (`E:MaysHouse_2F:224`), the post-Lilycove lines (`:242`, HoennB2 `players_house_2f_ch8.inc`). About 100 L
  unique (53 per entry, mostly shared) + movement + text.
- **New:** Mom registers you in the PokéNav (`Es:players_house.inc:293-300`): under 3A a message + jingle, and the Amulet Coin stays
  on HoennB2's after-badge-5 flow (`players_house_1f_ch6.inc`); Emerald gates it on `FLAG_ENABLE_MOM_MATCH_CALL`. **Johto starters:**
  once `HasAllHoennMons` (`src/pokedex.c:4387`) after the dex upgrade, the lab takes the "with table" layout and shows Cyndaquil /
  Totodile / Chikorita balls (`E:Lab:30-46, 247-305`; ball 51 L / 18 T x3, ChooseJohtoStarter 6 L / 15 T, `showmonpic`). HoennB2
  already has the National Dex part (`BirchLab_Postgame.inc`, `LittlerootTown_Postgame.inc`, written from `E:Lab:160-199` and its note
  says Johto starters are not ported). Needs `VAR_DEX_UPGRADE_JOHTO_STARTER_STATE` 4-6 (HoennB2 uses 1-3).
- **Flags:** new `VAR_SCOTT_STATE`, `VAR_SCOTT_PETALBURG_ENCOUNTER` (used by Ch1), `VAR_OLDALE_RIVAL_STATE`; skipped under 3A:
  `FLAG_ENABLE_MOM_MATCH_CALL`, `VAR_REGISTER_BIRCH_STATE`, `FLAG_ENABLE_PROF_BIRCH_MATCH_CALL`, `FLAG_SCOTT_CALL_BATTLE_FRONTIER`.
  Renamed (use hoenn.h): `VAR_LITTLEROOT_TOWN_STATE` = `VAR_LITTLEROOT_STATE`, `VAR_LITTLEROOT_HOUSES_STATE_BRENDAN` / `_MAY` =
  `VAR_LITTLEROOT_HOUSES_STATE` / `_2` (check which is which), `VAR_OLDALE_TOWN_STATE` = `VAR_OLDALE_STATE`, the 41 renamed
  `FLAG_HIDE_LITTLEROOT_TOWN_*`.
- **Needs:** Phase 2: ground changes in Brendan 2F, May 1F / 2F, Lab (SB / `maps.emerald.ground`) and the Lab "with table"
  variant (only for Johto starters); Phase 5: the rival's NPC sheet in Emerald's outfit (rival model code 162, `h_setup_rival_gfx`).
  Phase 4: none.
- **Size:** ~250 L / ~140 T new or changed (the four rival entries and the three starter balls share most code). Text pass 79
  lines.

### Ch1 Rival on Route 103, Pokédex, Petalburg, Woods, Roxanne
- **Reuse:** Oldale Mart employee + Route 102 block (`E:OldaleTown:36,200`; HoennB2 `0794/0795`), Route 103 rival (`E:Route103:20`,
  89 L / 36 T; `scenes/Route103.inc`; trainers #520-#535 = Sapphire's slots), Oldale rival walk, Pokédex + Poké Balls, Running
  Shoes, Petalburg arrival + Norman + Wally tutorial (`E:PetalburgCity:235`, `E:PetalburgCity_Gym:101`, `LoadWallyZigzagoon` =
  `PutZigzagoonInPlayerParty`; `PetalburgCity.inc`, `PetalburgCity_Gym_ch6.inc`), Petalburg Woods grunt (#10 both; `PetalburgWoods.inc`),
  Roxanne (`E:RustboroCity_Gym:4`, 29 L / 58 T), Cutter, Quick Claw, flower shop.
- **Ruby:** none (Aqua is the villain here, as Sapphire).
- **Emerald branch:** text only (SB: 26 SAME / 2 CHANGED).
- **New:** **Scott** watches you in Petalburg: 4 coord triggers at x=4, y=10-13, `VAR_SCOTT_PETALBURG_ENCOUNTER` 0 (`E:PetalburgCity:486-517`, Scott0-3
  -> shared `ScottScene` 47 L / 11 T). Scott at the Pokémon School (`E:RustboroCity_PokemonSchool:159`, 27 L / 40 T, before and after
  the Stone Badge, `FLAG_MET_SCOTT_RUSTBORO`, `FLAG_MET_SCOTT_AFTER_OBTAINING_STONE_BADGE`). Roxanne's call (`E:RustboroCity_Gym:93`,
  `pokenavcall`): a message. The Walda NPC (see section 1).
- **Flags:** new `FLAG_MET_SCOTT_RUSTBORO`, `FLAG_MET_SCOTT_AFTER_OBTAINING_STONE_BADGE`; renamed `FLAG_RECEIVED_HM_CUT` = HM01,
  `FLAG_RECEIVED_TM_FACADE`/`_BULLET_SEED` (check vs TM09 / TM_ROCK_TOMB), `VAR_PETALBURG_CITY_STATE` (0-5, set at
  `E:PetalburgCity_Gym:183,435`, `E:PetalburgCity:47`, `E:PetalburgCity_WallysHouse:25`; HoennB2 has `VAR_PETALBURG_STATE` and `VAR_PETALBURG_GYM_STATE` for the same scenes: check the mapping, Wally's walk is state 4, Ch6).
- **Needs:** Phase 2: Route 103 resized (80x20 -> 80x22) and Oldale / Rustboro / Petalburg Gym ground: Emerald's own
  coordinates for any trigger there; **Phase 5: Scott's overworld sheet (no SCOTT row in `data/sprite_map.json`)**.
- **Size:** ~75 L / ~50 T. Text pass 226 lines (mostly generated NPCs, S0-1).

### Ch2 Devon Goods, Mr. Stone, Mr. Briney, Brawly, Steven
- **Reuse:** the whole theft chain: the grunt steals the goods (`E:RustboroCity:231`), employee asks for help (`:452`), Route 116
  (`E:Route116:132,140`), Rusturf grunt #16 (`E:RusturfTunnel:287`), goods returned (`:526`), Mr. Stone + Exp. Share
  (`E:RustboroCity_DevonCorp_3F:28`), Briney, Dewford, Brawly (`E:DewfordTown_Gym:135`; HoennB2 `0050`), Granite Cave Steven
  (`E:GraniteCave_StevensRoom:4`), Seashore House. HoennB2: `RustboroCity.inc` (24 entries), `Route104_ch2.inc`, `DewfordTown.inc`.
- **Ruby:** none.
- **Emerald branch:** `RB_Rival` (script 21 of `RustboroCity.inc`) body: Sapphire's no-battle meeting becomes Emerald's **optional
  rival battle** (below).
- **New:** **the rival battle**: `E:RustboroCity:614-853`: eight coord triggers (12-19, 53) while `VAR_RUSTBORO_CITY_STATE` 7
  (shared `RivalEncounter` `:722`, 120 L / 61 T), or on Route 104 when the rival leaves Briney's cottage (`E:Route104:47`, 128 L /
  54 T; states `VAR_ROUTE104_STATE` 1 -> 2, `FLAG_REGISTER_RIVAL_POKENAV`, `FLAG_DEFEATED_RIVAL_RUSTBORO`, `FLAG_DEFEATED_RIVAL_ROUTE_104`).
  Six new trainer ids (#592, #593, #599, #600, #768, #769: Appendix B). `VAR_RUSTBORO_CITY_STATE` runs 1 (Roxanne won), 2 / 3 (theft, `:288,482`), 4
  (goods recovered, `E:RusturfTunnel:323`), 5 (returned, `:563`), 6 (Mr. Stone, `E:RustboroCity_DevonCorp_3F:68`), 7 (the Devon scientist's Match Call
  tutorial, `E:RustboroCity:31,88`, which also sets `VAR_ROUTE104_STATE` 1), 8 (rival done). Under 3A the scientist scene (56 L / 18 T) is dropped:
  Mr. Stone's scene sets 7 and `VAR_ROUTE104_STATE` 1 itself. The "registered in the PokéNav" lines become a message; Norman's call on the boat
  (`E:Route104:355-367`) a message.
- **Flags:** new `VAR_ROUTE104_STATE`, `FLAG_DEFEATED_RIVAL_RUSTBORO`, `FLAG_DEFEATED_RIVAL_ROUTE_104`, `FLAG_MET_RIVAL_RUSTBORO`
  (exists), `FLAG_INTERACTED_WITH_DEVON_EMPLOYEE_GOODS_STOLEN`. Renamed: `VAR_RUSTBORO_CITY_STATE` = `VAR_RUSTBORO_STATE` (new values 6,
  7, 8), `VAR_BOARD_BRINEY_BOAT_STATE` = `VAR_BOARD_BRINEY_BOAT_ROUTE104_STATE`, `FLAG_RECEIVED_HM_FLASH/_STRENGTH`,
  `FLAG_DEFEATED_SEASHORE_HOUSE` = `_TRAINERS`.
- **Needs:** Phase 1: the six rival ids + their (gendered) parties; Phase 2: Rustboro / Route 109 (resized) / Route 116 ground;
  Phase 4: none.
- **Size:** ~180 L / ~115 T (rival ~150 L). Text pass 165.

### Ch3 Slateport, Route 110, Mauville, Verdanturf, Trick House
- **Reuse:** arrive in Slateport (`E:SlateportCity:13`), Stern at the shipyard (`E:SlateportCity_SternsShipyard_1F:4`), museum fee +
  familiar grunt (`E:...OceanicMuseum_1F:8,138`, reworded), Stern + two grunts + Archie (`E:...OceanicMuseum_2F:4`, 84 L / 67 T; slots #20 / #21
  both), Route 110 rival (`E:Route110:351`, 101 L / 36 T), Cycling Road gate, Wally in Mauville (`E:MauvilleCity:84`, 102 L /
  60 T, #656), Wattson (`E:MauvilleCity_Gym:76`), bike, Rock Smash, Wally at Wanda's, Rusturf reunion + Strength, Trick House 1
  (**puzzles 2-8 are not built in any HoennB2 version**, only `Route110_TrickHousePuzzle1` exists: nothing to do for Emerald's
  rotating-tile puzzle 7).
- **Ruby:** none.
- **Emerald branch:** text only. The Pokéblock Case moves: Sapphire gives it at the Slateport lobby (`1190_room_SlateportCity_ContestLobby.s:69-74`),
  which Emerald replaces with a Battle Tent; Emerald gives it at the Lilycove lobby (`Es:contest_hall.inc:7-18`): do it in Ch8's
  lobby room (the Slateport / Verdanturf / Fallarbor contest rooms must be listed as not-Emerald in `versions.json` `rooms`).
- **New:** **Scott in Slateport**: frame scene while `VAR_SLATEPORT_OUTSIDE_MUSEUM_STATE` 1 (`E:SlateportCity:53`, 31 L / 22 T) +
  a queue of 11 Aqua grunts outside the museum (talkers of 7 L each, the one who reads the sign `E:SlateportCity:414`, 21 L / 9 T;
  `FLAG_HIDE_SLATEPORT_CITY_TEAM_AQUA` hides them from Stern's shipyard, `E:SlateportCity_SternsShipyard_1F:16`). `VAR_SLATEPORT_OUTSIDE_MUSEUM_STATE`
  is set to 1 by the Museum 2F scene (`E:...OceanicMuseum_2F:75`), 2 by Scott's scene, 3 by the tent scene or the Mauville Gym win (`E:MauvilleCity_Gym:91`). Scott after the Wally battle (`E:MauvilleCity:144-163`, ~15 L).
  Birch's Route 110 call (`E:Route110:559-607`, 56 L / 20 T; registration only): message or drop. **Three closed Battle
  Tent doors** (Slateport, Verdanturf; Fallarbor in Ch4), one generic "not open yet" line (new text: ask the user). The Berry
  Powder clerk / Berry Crush sign (`E:SlateportCity:677,884`): left out. Move tutors Swagger (`Es:move_tutors.inc:1`, Slateport
  Fan Club), Rollout (`:27`, Mauville), Fury Cutter (Verdanturf Center): 26 L each, see 5.4.
- **Flags:** new `VAR_SLATEPORT_OUTSIDE_MUSEUM_STATE`, `FLAG_MET_SCOTT_*` (Slateport via `VAR_SCOTT_STATE`), `VAR_SLATEPORT_CITY_STATE`
  (Emerald's name for the Stern-interview state; HoennB2 `VAR_SLATEPORT_STATE`), `FLAG_MET_SLATEPORT_FANCLUB_CHAIRMAN`; renamed
  `FLAG_RECEIVED_HM_ROCK_SMASH`, `FLAG_RECEIVED_TM_THIEF`; skipped: Powder Jar, Tent flags.
- **Needs:** Phase 2: Slateport (market redone, 271 blocks), Route 110 (48), Mauville Gym, `versions.json` rooms; Phase 1: tutors; Phase 5: Scott.
- **Size:** ~130 L / ~60 T. Text pass 278.

### Ch4 Routes 111-115, Fallarbor, Meteor Falls
- **Reuse:** Winstrate family, Fiery Path, Glass Workshop, Lanette (TM Dig), Cozmo taken away (`E:FallarborTown_CozmosHouse:4`), Cozmo in Meteor
  Falls (`E:MeteorFalls_1F_1R:212`), move relearner, Metronome tutor (`E:FallarborTown_Mart`).
- **Ruby (base):** Route 112 cable car blocked by **Magma** grunts (`E:Route112:10`, 27 L / 8 T: 2 objects, flag
  `FLAG_HIDE_ROUTE_112_TEAM_MAGMA`; HoennB2 `Route112.inc`, 3 entries); **Meteor Falls**: Magma steals the Meteorite, Archie + Aqua
  chase (`E:MeteorFalls_1F_1R:16-81`, `MagmaStealsMeteoriteScene` 67 L / 41 T, trigger (14,18) `VAR_METEOR_FALLS_STATE` 0,
  `FLAG_MET_ARCHIE_METEOR_FALLS`; HoennB2 `0256_room_MeteorFalls_1F_1R.s` + `data/story/ch4.json` objects 5-9). The flow equals
  Ruby's; what differs is text and the per-object models (Aqua 293 <-> Magma 302, Maxie 303 <-> Archie 353) via `model_emerald`.
- **Emerald branch:** **the fossil** moves from the Route 111 desert sand (HoennB2 `Route111.inc`, 348 lines) to the Mirage Tower: remove
  the sand pickup under `#ifdef`, `FLAG_CHOSE_ROOT_FOSSIL` / `_CLAW_` set at the tower; Devon fossil revival (`RustboroCity_DevonCorp_2F_Fossil.inc`) checks the new flags.
- **New:** **Mirage Tower** (Phase 2 maps MirageTower_1F..4F + Route 111 layouts): 1F transition sets `FLAG_ENTERED_MIRAGE_TOWER`
  / `FLAG_FORCE_MIRAGE_TOWER_VISIBLE` (`E:MirageTower_1F:5`), 2F / 3F cave-hole floors (`Es:cave_hole.inc`), 4F two fossil
  objects (`E:MirageTower_4F:4`, 29 L / 5 T each: "if taken the ground crumbles", `special DoMirageTowerCeilingCrumble`, warp to Route
  111 (19,59)), Route 111's `Route111_EventScript_MirageTowerDisappear` (`E:Route111:107`, six Mirage specials: shake, player falls,
  disintegrate, fossil falls and sinks, `VAR_MIRAGE_TOWER_STATE` 1 -> 2). Visible on a map load at 1 in 2 (`src/mirage_tower.c:317-339`). Desert
  Underpass (the other fossil, opens at game clear; Ch13). Fossil Maniac's tunnel hint (`E:Route114_FossilManiacsTunnel:16-30`,
  `VAR_FOSSIL_MANIAC_STATE`). **Jagged Pass guard** is Ch5's. Fallarbor Battle Tent door (closed); Trainer Hill door on Route 111.
  Route 111 Rock Smash tip man (`E:Route111:398`, text).
- **Flags:** new `VAR_MIRAGE_TOWER_STATE`, `FLAG_MIRAGE_TOWER_VISIBLE`, `FLAG_FORCE_MIRAGE_TOWER_VISIBLE`, `FLAG_ENTERED_MIRAGE_TOWER`,
  `FLAG_CHOSE_ROOT_FOSSIL` / `_CLAW_`, `FLAG_MET_ARCHIE_METEOR_FALLS`, `VAR_FOSSIL_MANIAC_STATE`, `VAR_METEOR_FALLS_STATE`, `FLAG_MET_PROF_COZMO`
  (check); renamed `FLAG_RECEIVED_TM_DIG` / `_ROAR`.
- **Needs:** Phase 2 Mirage Tower 4 maps + Route 111 / 113-115 layouts, Meteor Falls 1F (13 blocks, no walk change), Fossil Maniac's tunnel (53
  tiles); **Phase 4 Mirage Tower mechanics** (random visibility, ceiling crumble, sinking); Phase 1 trainer ids; Phase 5 Archie / Maxie sheets already exist.
- **Size:** team swaps ~105 L / 65 T (small, no new maps); Mirage Tower ~110 L / 40 T; Fallarbor / Route 114 hints ~40 L. Text pass 149.

### Ch5 Mt. Chimney, Jagged Pass, Lavaridge
- **Reuse:** cable car (`E:Route112_CableCarStation:31`), Meteorite machine and Cozmo (flags `FLAG_DEFEATED_EVIL_TEAM_MT_CHIMNEY`
  etc. identical), Jagged Pass descent, Lavaridge (Go-Goggles, Wynaut egg, Flannery `E:LavaridgeTown_Gym_1F:46`), Cozmo's TM27. Mimic
  tutor (`E:LavaridgeTown_House`).
- **Ruby (base):** **Mt. Chimney**: `E:MtChimney:14` Archie asks you to stop Team Magma (`FLAG_EVIL_LEADER_PLEASE_STOP`), `:33` Maxie scene
  (intro, `trainerbattle_no_intro TRAINER_MAXIE_MT_CHIMNEY` #602, Maxie and Magma leave, Archie thanks you) = HoennB2's `MC_Archie`
  (battle) + `MC_Maxie` (the one who asks) with roles swapped; plus Tabitha #597 as an ordinary eye-contact trainer (the role
  Matt, object 103, plays in HoennB2's `scenes/MtChimney.inc`; SB gives her at `E:MtChimney:385`, not re-read).
  `scenes/MtChimney.inc` (240 lines) needs no flow change: `model_emerald` on the 13 team objects, Emerald trainer constants,
  Emerald text (24 `MC_T_*` lines, `src/text/scenes/emerald/MtChimney.txt`). 184 L / 191 T in the Emerald map (60 messages with
  the grunts), only ~57 L / 65 T of it the scene.
- **Emerald branch:** none besides above.
- **New:** **Jagged Pass**: `E:JaggedPass:65` guard (`TRAINER_GRUNT_JAGGED_PASS` #570, `FLAG_BEAT_MAGMA_GRUNT_JAGGED_PASS`), the cave mouth stays
  a rock wall until you own the Magma Emblem (`OnResume` -> `VAR_JAGGED_PASS_STATE` 1, then the trigger scene `:39`: shake,
  `setmetatile` opens it, state 2). HoennB2 has **no scene file for Jagged Pass** (generated zone, `0036_auto_JaggedPass.s`), so this
  creates `scenes/JaggedPass.inc` (S0-2). The door is used in Ch8.
- **Flags:** new `VAR_JAGGED_PASS_STATE`, `FLAG_BEAT_MAGMA_GRUNT_JAGGED_PASS`; `FLAG_HIDE_JAGGED_PASS_MAGMA_GUARD` (clear at new game, **set** by
  Mt. Pyre's scene, `E:MtPyre_Summit:60`: the guard leaves once you hold the Emblem), `VAR_LAVARIDGE_TOWN_STATE`, `FLAG_WHITEOUT_TO_LAVARIDGE`.
- **Needs:** Phase 1: Maxie #602, Tabitha #597, grunts #146 / #579, Magma classes; Phase 5: Tabitha sheet (not code 88); Phase 2: Mt. Chimney
  (7 blocks) / Jagged Pass (30 collision tiles) / Lavaridge Gym (resized, new puzzle) / the hidden Jagged Pass cave mouth (HoennB2 pattern: a door whose warp is moved off the map, as Lilycove's).
- **Size:** ~100 L / ~80 T. Text pass 111.

### Ch6 Norman, Surf, Routes 105-108, Abandoned Ship, New Mauville
- **Reuse:** Norman + Facade (`E:PetalburgCity_Gym:360`), Mom's Amulet Coin (Ch0 file), Wattson's Basement Key + New Mauville
  (`E:MauvilleCity:398`, `E:NewMauville_Inside:143`), Abandoned Ship, Scanner trade, Routes 105 / 107 / 108 trainers.
- **Ruby:** none.
- **Emerald branch:** **Wally's dad** gives Surf: after the badge (`E:PetalburgCity_Gym:435`, `VAR_PETALBURG_CITY_STATE` 4) he walks
  you from the town into his house (`E:PetalburgCity:57-76`, `opendoor`, 23 L), `E:PetalburgCity_WallysHouse:7-23` gives `ITEM_HM_SURF` (8 L / 17 T).
  HoennB2: `PetalburgCity_Gym_ch6.inc` (424 lines, its post-battle Surf part) -> branch there.
- **New:** nothing else. Tutors none.
- **Flags:** `FLAG_THANKED_FOR_PLAYING_WITH_WALLY`, `VAR_PETALBURG_CITY_STATE` 4 / 5; `FLAG_DEFEATED_VOLTORB_1..3_NEW_MAUVILLE` (the three statics; Sapphire's names differ).
- **Needs:** Phase 2: Petalburg Gym (234 blocks), Wally's house door; Phase 4 none.
- **Size:** ~35 L / ~17 T. Text pass 170 (mostly gym trainer and route lines: generated).

### Ch7 Routes 118-120, Weather Institute, Fortree
- **Reuse:** Good Rod, Steven on Route 118 (`E:Route118:62`, reworded), Aqua takes the Institute + Shelly #32 (`E:Route119_WeatherInstitute_2F:41`),
  Castform, rival + HM02 Fly (`E:Route119:29`), Kecleon, Steven + Devon Scope (`E:Route120:154`), Winona (`E:FortreeCity_Gym:19`), Wingull mail. Sleep Talk tutor (`E:FortreeCity_House2`).
- **Ruby:** none (Aqua is the villain at the Weather Institute).
- **Emerald branch:** none.
- **New:** Scott on Route 119 after the rival leaves (`E:Route119:152`, ~15 L) and his Fortree call (`E:Route119:461`, message). The Institute's
  post-game abnormal-weather scientist (`E:Route119_WeatherInstitute_2F:124-147`) is Ch13.
- **Flags:** `FLAG_SCOTT_CALL_FORTREE_GYM`, `VAR_SCOTT_FORTREE_CALL_STEP_COUNTER` (skip); `FLAG_RECEIVED_HM_FLY`.
- **Needs:** Phase 2: Fortree Gym (410 blocks), Route 118-120 ground; Phase 5: Scott.
- **Size:** ~10 L / ~13 T. Text pass 66.

### Ch8 Lilycove, Mt. Pyre, Magma Hideout, Slateport submarine, Aqua Hideout
- **Reuse:** Route 121 grunts (`E:Route121:16`), Lilycove rival (`E:LilycoveCity:227`, 113 L / 97 T, #661-666 = Sapphire's), Cove grunt, Slateport
  harbor theft + Archie (`E:SlateportCity_Harbor:23-72`, 41 L / 16 T x4 triggers; HoennB2 `SlateportCity_Harbor_Ch8.inc`), Aqua Hideout 1F / B1F /
  B2F (shared room in both versions; B2F Matt #30 + submarine: `E:AquaHideout_B2F:23-45`), Substitute tutor.
- **Ruby:** none (Mt. Pyre is rewritten below; the Magma Hideout is new).
- **Emerald branch:** **Mt. Pyre summit** (`MtPyre_Summit.inc`, 183 lines, 8 entries): `E:MtPyre_Summit:14` (3 triggers, `TeamAquaExits`, 47 L / 26 T): Archie says
  they have the orb and leaves with the 4 Aqua grunts (eye-contact trainers `GRUNT_MT_PYRE_1-4`, #569 is the new 4th; the scene removes them); the old lady gives the **Magma Emblem** (`giveitem ITEM_MAGMA_EMBLEM`, `FLAG_RECEIVED_RED_OR_BLUE_ORB`,
  `FLAG_HIDE_JAGGED_PASS_MAGMA_GUARD`); no orb for you. The three state-2 triggers (`:171`, 75 L / 3 T, HoennB2 entries 6-8 /
  `MtPyre_Summit_Ch10.inc`) become **Archie and Maxie return both orbs** (`VAR_MT_PYRE_STATE` 2 -> 3, old lady `:145`, 18 L / 29 T).
  Same ScriptEntry count, new bodies. **Slateport trigger moves**: HoennB2 sets `VAR_SLATEPORT_STATE` / `_HARBOR_STATE` in `MtPyre_Summit.inc:93,96`; Emerald does it at the end of the Magma Hideout (`E:MagmaHideout_4F:53-57`,
  `VAR_SLATEPORT_CITY_STATE` 1, `VAR_SLATEPORT_HARBOR_STATE` 1, Stern + Gabby & Ty appear). Pokéblock Case given in Lilycove's lobby (Ch3 note). Safari Zone stays 4 areas until the Hall
  of Fame (Ch13).
- **New:** **Magma Hideout** (8 maps; Jagged Pass door, `VAR_JAGGED_PASS_STATE` 2): only 4F has a story script, the Maxie scene
  (`E:MagmaHideout_4F:4`, 63 L / 33 T): Blue Orb + `dofieldeffectsparkle`, `DoOrbEffect`, Groudon wakes and leaves, two shakes, Maxie asks if you did something, battle
  `TRAINER_MAXIE_MAGMA_HIDEOUT` #601, he goes after Groudon, `FLAG_GROUDON_AWAKENED_MAGMA_HIDEOUT`. Template: HoennB2's Room 9 Archie scene
  (`0380_room_SeafloorCavern_Room9.s`). The rest is generated: 16 grunts #716-731 + Tabitha #732 (all eye-contact trainers, text 4-13 lines), 7 item balls
  (Rare Candy, Max Elixir, Full Restore, Nugget, PP Max, Escape Rope, Max Revive), Strength boulders on 1F, Groudon sleeping / awake objects (model 4512 exists). Scott in the
  Cove Lily Motel (`E:LilycoveCity_CoveLilyMotel_2F:53`, 11 L / 18 T). Contest hall: counters only.
- **Flags:** new `FLAG_GROUDON_AWAKENED_MAGMA_HIDEOUT`, `FLAG_HIDE_MAGMA_HIDEOUT_GRUNTS` (one flag hides every grunt), `FLAG_HIDE_MAGMA_HIDEOUT_4F_GROUDON` / `_ASLEEP`, `FLAG_MET_SCOTT_IN_LILYCOVE`,
  `VAR_MT_PYRE_STATE` 3 (new value), `FLAG_SOOTOPOLIS_ARCHIE_MAXIE_LEAVE` (set in Ch10), `FLAG_KYOGRE_ESCAPED_SEAFLOOR_CAVERN` (HoennB2 `FLAG_LEGEND_ESCAPED_SEAFLOOR_CAVERN`, rename),
  `FLAG_DEFEATED_ELECTRODE_1/2_AQUA_HIDEOUT`; item-ball flags of the Hideout come from `gen_items` Emerald mode. `ITEM_MAGMA_EMBLEM` needs a key-item row in `src/include/hoenn_key_items.h` (a new "reuse" slot + name / description text; the key-item text install moves
  system messages and invalidates savestates: STORY_COMMON "Key items").
- **Needs:** **Phase 2: Magma Hideout 8 maps** (name clash with Ruby's `MagmaHideout_1F`: `maps.emerald.name_clash`), their zone ids / script file numbers, `versions.json` rooms, Jagged Pass ground; Lilycove (4 blocks), Mt. Pyre 2F / 3F / 6F;
  Phase 1: 17 + 1 trainer ids, Magma classes; Phase 4: none special (`DoOrbEffect` / `FadeOutOrbEffect` = HoennB2 Room 9's flash: one white flash, as Ruby); Phase 5: Maxie sheets exist, Tabitha.
- **Size:** Mt. Pyre ~140 L / ~110 T (no maps), Magma Hideout story ~65 L / 35 T + 17 generated trainers, motel ~10 L. Text pass 292.

### Ch9 Mossdeep, Space Center, Dive
- **Reuse:** shard trader, arrive in Mossdeep (`E:MossdeepCity:71`), Sun Stone man (`E:...SpaceCenter_1F:101` + a Magma variant `:119`), Wingull mail, Shoal Cave (per-item flags `FLAG_RECEIVED_SHOAL_SALT_1-4`...), Dynamic Punch tutor (`E:MossdeepCity`).
  Tate & Liza: the leader script (`E:MossdeepCity_Gym:51`, 51 L / 70 T) is SAME apart from the win flags (`VAR_MOSSDEEP_CITY_STATE` 1, `VAR_MOSSDEEP_SPACE_CENTER_STATE` 1, `:77-79`).
- **Ruby:** none (Emerald's Space Center is new, not Ruby's).
- **Emerald branch:** Steven's house: **Dive only after the Space Center** (HoennB2's `0678_room_MossdeepCity_StevensHouse.s` gives it on first entry, Sapphire's OnFrame state 0; Emerald `E:MossdeepCity_StevensHouse:28`, `VAR_STEVENS_HOUSE_STATE` 1 set at `E:SpaceCenter_2F:288` per SB, 19 L / 16 T).
  Gym (see Needs).
- **New:** **Space Center** (rooms exist as `MossdeepCity_SpaceCenter_1F/2F`): Maxie + 4 grunts walk in (`E:MossdeepCity:76`, 23 L, trigger once the gym is won); 1F Magma grunts #22, #116, #586, #587 and the stair guard
  (`E:SpaceCenter_1F:207`, `VAR_MOSSDEEP_SPACE_CENTER_STAIR_GUARD_STATE`), Steven (`:178`); 2F three-grunt gauntlet (`E:SpaceCenter_2F:31-61`, #588-590, refusing warps you out); **Steven's multi battle**
  (`:170-290`, 100 L / 43 T): `SavePlayerParty`, `ChooseHalfPartyForBattle` (3 of 6), `ReducePlayerPartyToSelectedMons`, `frontier_set` / `frontier_saveparty`, `SPECIAL_BATTLE_STEVEN` via `DoSpecialTrainerBattle` (partner = Steven's fixed 3 (`src/battle_tower.c:772`),
  opponents #734 Maxie / #514 Tabitha), `SetCB2WhiteOut` on a loss; win: `FLAG_DEFEATED_MAGMA_SPACE_CENTER`, `VAR_MOSSDEEP_CITY_STATE` 3, Magma objects hidden. Scott in Mossdeep (`E:MossdeepCity:249`, 18 L / 11 T). The rival's "Rayquaza"
  PokéNav call after 250 outdoor steps (`src/field_specials.c:453-475`, `E:SpaceCenter_2F:322-338`): a message (HoennB2 has no step hook; use a Mossdeep trigger or drop).
- **Flags:** new `VAR_MOSSDEEP_CITY_STATE`, `VAR_MOSSDEEP_SPACE_CENTER_STATE`, `VAR_MOSSDEEP_SPACE_CENTER_STAIR_GUARD_STATE`, `FLAG_DEFEATED_MAGMA_SPACE_CENTER`, `FLAG_INTERACTED_WITH_STEVEN_SPACE_CENTER`, `FLAG_DEFEATED_GRUNT_SPACE_CENTER_1F`; changed meaning: `VAR_STEVENS_HOUSE_STATE` (1 = Dive due).
- **Needs:** **Phase 4: the tag battle** (`CallTrainerMultiBattle` = FieldCommand 134 exists; the 3-of-6 selection, a partner party and the `SetCB2WhiteOut` path do not: EMERALD_PLAN §5 "check"), and rotating tiles for the redesigned Mossdeep Gym (20 commands, resized to 26x36; HoennB2's Sapphire gym is the warp-tile puzzle:
  `0644_room_MossdeepCity_Gym.s`); Phase 2: Mossdeep (178 collision tiles in the east part around the Center), Gym; Phase 1: 9 Magma trainer slots + Steven's partner party; Phase 5: Steven's back sprite is done.
- **Size:** ~290 L / ~180 T. Text pass 122.

### Ch10 Seafloor, Route 128, Sootopolis crisis, Cave of Origin, Sky Pillar, Juan
The largest rewrite (SB §2 Ch10). HoennB2's Sapphire port is a different state machine (`VAR_SOOTOPOLIS_STATE`, a Kyogre battle in Cave of Origin B4F), so most of `SootopolisCity.inc` (373 lines, 15 entries) and `ch10_lib.inc` is replaced.
- **Reuse:** Dive to the sub, Seafloor Rooms 1-8 grunts (slots same; `E:SeafloorCavern_Room*`), Route 128 Archie / Maxie / Steven (`E:Route128:14-67`, 55 L / 43 T; HoennB2 `Route128.inc`, which has the `#ifdef HOENN_RUBY` brighten effect: Emerald takes Sapphire's flow here), Room 9 text (90% Sapphire's), Double-Edge tutor.
- **Ruby:** none (Room 9 and Route 128 are Sapphire's flow; Ruby's Groudon / drought variants do not apply, Emerald has both legendaries).
- **Emerald branch:** **Room 9** (`E:SeafloorCavern_Room9:4`, 123 L / 70 T vs HoennB2 `0380`): same scene, **Kyogre escapes**, and the end now sets about 25 flags / vars (`:99-125`: `VAR_SOOTOPOLIS_CITY_STATE` 1, `FLAG_LEGENDARIES_IN_SOOTOPOLIS`, `FLAG_KYOGRE_ESCAPED_SEAFLOOR_CAVERN`, `FLAG_SYS_WEATHER_CTRL`, Steven leaves his house `VAR_STEVENS_HOUSE_STATE` 2, warp
  to Route 128 (38,22)). Seafloor Entrance grunt hint (`E:SeafloorCavern_Entrance:10`, 32 L / 24 T: Magma is near Mossdeep; `VAR_HAS_TALKED_TO_SEAFLOOR_CAVERN_ENTRANCE_GRUNT`). **Juan** replaces Wallace in the Gym (`E:SootopolisCity_Gym_1F:81`, 49 L / 87 T; slot #272; `VAR_SOOTOPOLIS_CITY_STATE` 6; HoennB2
  `0046_room_SootopolisCity_Gym_1F.s`). Mt. Pyre's orb return is Ch8's.
- **New (all of it, from `E:SootopolisCity` 678 L / 223 T):** (1) **map scripts** (`:9-165`, 102 L): door locks by `setmetatile`, `LAYOUT_SOOTOPOLIS_CITY_LEGENDS_BATTLE`, `WEATHER_DOWNPOUR` at state 1 then `WEATHER_ABNORMAL`, battle spectators, positions per `VAR_SOOTOPOLIS_CITY_STATE` 0-6 / `VAR_SKY_PILLAR_STATE` / `VAR_SOOTOPOLIS_WALLACE_STATE`; (2) **the legends scene** (`:171-455`, from the Center or from Dive: 138 L): Groudon vs Kyogre with
  `SpawnCameraObject` / `RemoveCameraObject`, `ShakeCamera`, Steven guides you to the Cave (`:857`, 48 L / 37 T); (3) **Cave of Origin B1F**: Wallace asks where Rayquaza is (`E:CaveOfOrigin_B1F:4`, 42 L / 45 T, `multichoice MULTI_WHERES_RAYQUAZA` loop, only "Sky Pillar" ends it: `FLAG_WALLACE_GOES_TO_SKY_PILLAR`, `VAR_SOOTOPOLIS_CITY_STATE` 3); there is no legendary battle here (R/S B2F-B4F unused; HoennB2's `0200-0207` rooms are Sapphire-only, the Emerald room is the old B4F, 154 blocks changed);
  (4) **Sky Pillar** (now main story): Outside (`E:SkyPillar_Outside:33`, 49 L / 21 T: Wallace opens the door, earthquake, `WEATHER_ABNORMAL`, `VAR_SOOTOPOLIS_CITY_STATE` 4), floors 1F-5F + Top in **clean** layouts until `VAR_SKY_PILLAR_STATE` 2 (`E:SkyPillar_1F:6` ... `SkyPillar_Top:18`), Top `AwakenRayquaza` (`:87`, 38 L: camera pan, two cries, shakes, Rayquaza flies off, `VAR_SOOTOPOLIS_CITY_STATE` 5, `VAR_SKY_PILLAR_STATE` 1) and Rayquaza (`:43`, catchable at Lv 70 right after, no game-clear check: replaces HoennB2's post-game `SkyPillar_Top.inc` / Ch13 gate);
  (5) **Rayquaza scene** (`E:SootopolisCity:456-560`, 124 L, `Script_DoRayquazaScene`, `warpwhitefade`, `VAR_SKY_PILLAR_STATE` 2 / 3, clears `FLAG_SYS_WEATHER_CTRL`); (6) Wallace after (`:1248`, Waterfall `:1258`), Maxie / Archie NPCs (`:1302,1317`), the gym door (`:1335`), 11 citizens with 2-3 states each (`:678-1250`, 179 L / 111 T), Lotad and Seedot house (`E:...LotadAndSeedotHouse`, size contest renamed), Kiri's berries. Route 131's Sky Pillar islet
  is **always** present in Emerald (`E:Route131:5-12`: `setmaplayoutindex LAYOUT_ROUTE131_SKY_PILLAR` unconditionally; HoennB2 `Route131.inc` waits for the game clear), the Sky Pillar door opens at `FLAG_WALLACE_GOES_TO_SKY_PILLAR` (`E:SkyPillar_Outside:20-27`).
  **HM07 Waterfall** is now Wallace's gift (`E:SootopolisCity:1258`), not the Cave of Origin B3F item ball: `gen_items` Emerald mode must drop that ball.
- **Flags:** new `VAR_SKY_PILLAR_STATE`, `VAR_SKY_PILLAR_RAYQUAZA_CRY_DONE`, `VAR_SOOTOPOLIS_WALLACE_STATE`, `FLAG_STEVEN_GUIDES_TO_CAVE_OF_ORIGIN`, `FLAG_WALLACE_GOES_TO_SKY_PILLAR`, `FLAG_LEGENDARIES_IN_SOOTOPOLIS`, `FLAG_MET_ARCHIE_SOOTOPOLIS`, `FLAG_MET_MAXIE_SOOTOPOLIS`, `FLAG_DEFEATED_RAYQUAZA`, `FLAG_SOOTOPOLIS_ARCHIE_MAXIE_LEAVE`
  (+ 23 new-looking hide flags, ~17 for really new objects: Wallace at Cave of Origin / Sky Pillar, Archie / Maxie at Room 9, Route 128 and Sootopolis, the Groudon / Kyogre objects, Rayquaza still / awake, the stolen submarine). Changed meaning: `VAR_SOOTOPOLIS_STATE` (HoennB2) -> Emerald's `VAR_SOOTOPOLIS_CITY_STATE` 0-6; `FLAG_SYS_WEATHER_CTRL`; `VAR_SEAFLOOR_CAVERN_STATE`.
- **Needs:** **Phase 2:** Seafloor Room 2 (resized 18x21 -> 18x12) and Room 3 (121 blocks), Rooms 6 / 7, Sootopolis (43 blocks) **plus the LEGENDS_BATTLE layout** (alt cells + a `MapReplaceSetEvent` id: HoennB2 uses ids 2 and 7 so far, `ch13_gameclear.inc`, `Route130.inc`), Sootopolis Gym (150 blocks, rebuilt tileset), Cave of Origin as Entrance / 1F / B1F only,
  **Sky Pillar 1F-5F + Top clean variants** (`room_variants.emerald`, 6 rooms; Outside + Top ground changed 304 blocks) and Route 131 always-on; **Phase 4:** the whole Sootopolis sequence: two crisis weathers (HoennB2's `weather` patch has one id per version: thunderstorm 6 / Ruby drought 3; Emerald needs downpour *and* abnormal, switched by script; the user picks the look as for Groudon's drought), camera object scenes (`EvCamera*` exist), door-closing without `setmetatile` (HoennB2 pattern: warps moved off-map + "closed" signs), legend objects (models 4511 / 4512 / 4513 exist);
  Phase 1: Juan (class + front 126), Wallace as Champion; Phase 5: music `mus_abnormal_weather`, `mus_rayquaza_appears`, `mus_vs_rayquaza` (emerald_art; stand-ins until then).
- **Size:** ~1,150 L / ~500 T (Sootopolis ~600 of it). Text pass 171. Split in two builders (section 6).

### Ch11 Victory Road, Elite Four, Champion, Hall of Fame
- **Reuse:** Ever Grande, Wally at the entrance (#519, `E:VictoryRoad_1F:20-36`) and post-game (#657), the door guard (`E:EverGrandeCity_PokemonLeague_1F:48`, 38 L / 10 T), Sidney, Phoebe, Glacia, Drake (`Es:elite_four.inc`).
- **Ruby:** none.
- **Emerald branch:** **Champion Wallace** replaces Steven (`E:EverGrandeCity_ChampionsRoom:23`, 93 L / 93 T vs 122 L; slot #335): party / text swap in HoennB2's `0068/0069`; the Champion trainer class gets Black 2's Wallace picture (Phase 1). Hall of Fame (`E:...HallOfFame:18`) and **`Sub_Ch13_GameClear`** (`scenes/ch13_gameclear.inc`) get an Emerald block from `Es:hall_of_fame.inc:1-25,40-50`:
  legend reset flags (`FLAG_DEFEATED_MEW` etc.), Desert Underpass comment (`VAR_FOSSIL_MANIAC_STATE` 1), E4 reset, Safari expansion shown / workers hidden, Lilycove rival hidden, S.S. Ticket (Mom + Dad scene), Beldum, dex upgrade armed (`VAR_DEX_UPGRADE_JOHTO_STARTER_STATE` 1; HoennB2 arms it from Littleroot's zone init instead), Lilycove motel designers, Steven's house ninja boy. About 25 flag lines.
- **New:** Scott in the Ever Grande Center (`E:EverGrandeCity_PokemonCenter_1F:32`, 18 L / 9 T; he appears once the 6th badge is owned, `:12` `FLAG_BADGE06_GET`, and is gone after you enter Sidney's room, `E:EverGrandeCity_SidneysRoom:9`).
- **Flags:** `FLAG_MET_SCOTT_IN_EVERGRANDE`, `FLAG_DEFEATED_ELITE_4_SIDNEY` (rename), `VAR_SS_TIDAL_SCOTT_STATE`; `FLAG_IS_CHAMPION`.
- **Needs:** Phase 2: League split 1F / 2F (new map `EverGrandeCity_PokemonLeague_2F`), Victory Road B1F / B2F (6 blocks); Phase 1: Wallace #335 party, E4 same.
- **Size:** ~190 L / ~110 T. Text pass 115.

### Ch12 Southern seas, Pacifidlog, Regis
- **Reuse:** Pacifidlog houses and the trader (reworded), Sealed Chamber (Relicanth + Wailord opens the doors: `E:SealedChamber_InnerRoom:4,26`, `DoSealedChamberShakingEffect_Short/_Long`), Regi battles (`StartRegiBattle`: `CallWildBattle ... 1`), Mirage Island watcher, Explosion tutor. Rooms: HoennB2 `0188 AncientTomb`, `0232 DesertRuins`, `0254 IslandCave`, `0408/0430 SealedChamber_*`, `ch12_lib.inc`.
- **Ruby:** none.
- **Emerald branch:** the three opening puzzles change (C code in Emerald, `src/braille_puzzles.c`): Regirock = **Rock Smash** at (5-7, 23); Registeel = **Flash** at (8, 25); Regice = **run a lap** of 36 perimeter tiles (`sRegicePathCoords`, `VAR_REGICE_STEPS_1-3` bitmasks, back to (8,21)); none uses Strength / Fly / wait. HoennB2's pattern already exists: a step trigger that uses the move for you
  (`h_field_move_user` in `ch12_lib.inc`; "Black 2's party menu cannot be hooked per tile"). So Regirock / Registeel are two trigger scripts with new tile numbers and badge / machine checks; Regice needs 36 triggers or a step hook (Phase 4 choice).
- **New:** none; flags `FLAG_SYS_REGIROCK_PUZZLE_COMPLETED`, `FLAG_SYS_REGISTEEL_PUZZLE_COMPLETED`, `FLAG_SYS_BRAILLE_REGICE_COMPLETED`, `FLAG_TEMP_REGICE_PUZZLE_STARTED/_FAILED`, `VAR_REGICE_STEPS_1-3` (ids replace `FLAG_SYS_BRAILLE_STRENGTH/FLY/WAIT`), braille messages (24 `braillemsgbox`, new Emerald text).
- **Needs:** Phase 4 (Regice lap hook, Rock Smash / Flash use at the tile); Phase 2: Desert Ruins, Ancient Tomb ground (1 block each, no walk change), Island Cave; Route 131-134 ground.
- **Size:** ~45 L script + 24 braille texts; C-side is Phase 4. Text pass 31.

### Ch13 Post-game
- **Reuse:** the event islands (Faraway / Birth / Navel Rock, tickets, ferry: already Emerald's code in HoennB2, `FarawayIsland_*.inc`, `BirthIsland_*.inc`, `LilycoveCity_Harbor_Events.inc`), Beldum, Southern Island scene (the Lati opposite to the roamer), National Dex (done), Enigma Berry / Jirachi / Celebi / roamers (`postgame_lib.inc`).
- **Ruby:** none.
- **Emerald branch:** **Lati by colour** (`Es:players_house.inc:392-450`, `PlayersHouse_1F_EventScript_GetSSTicketAndSeeLatiTV`, 114 L; HoennB2 `players_house_1f_ch13.inc`, 125 lines): Mom asks the colour (`multichoice 22,8 MULTI_TV_LATI`), `special InitRoamer` roams Latias or Latios (`src/roamer.c:84-89`), `VAR_ROAMER_POKEMON`; the island one is the other. HoennB2's macros `SPECIES_LATIAS_OR_LATIOS` / `MODEL_*` are per version, not per save: Emerald needs a var test in `SouthernIsland_Interior.inc` (two story objects, models 4509 / 4510, one hidden) and in `postgame_lib.inc`'s `pg_roamer_start 0` (Phase 4: roamers patch takes the species from the var).
  S.S. Tidal / ferry: Slateport harbor (`E:SlateportCity_Harbor:173-202`) and Lilycove (`E:LilycoveCity_Harbor:9`, 304 L) gain a "Battle Frontier" destination = the Battle Tower island; Scott on the ship (`E:SSTidalCorridor:185`, 18 L / 18 T) invites you.
- **New (no Frontier):** Steven's Cave in Meteor Falls (`E:MeteorFalls_1F_1R:5-14` opens on `FLAG_SYS_GAME_CLEAR`; `E:MeteorFalls_StevensCave:4`, 17 L / 23 T, `TRAINER_STEVEN` #804); **Marine Cave / Terra Cave** (Kyogre / Groudon `E:MarineCave_End:25`, `E:TerraCave_End:25`, 28 L each) reached from 16 spots picked by `CreateAbnormalWeatherEvent` after the Weather Institute scientist (`E:Route119_WeatherInstitute_2F:124-147`, `Es:abnormal_weather.inc` 168 L; `src/field_specials.c:3445-3465`, 8 Terra spots on Routes 114 / 115 / 116 / 118, 8 Marine on 105 / 125 / 127 / 129);
  Desert Underpass (`E:DesertUnderpass:9`, the unchosen fossil); Safari Zone expansion (2 new areas shown at the Hall of Fame); Altering Cave (HoennB2 has it); Frontier island: the Reception Gate Scott scene (`E:BattleFrontier_ReceptionGate:14-34`, Frontier Pass), the six closed facility doors, Artisan Cave and Sudowoodo (`E:BattleFrontier_OutsideEast:104-140`) **closed / left out** by decision 1A unless the user adds them;
  gym leader rematches (out, 3A); Mystery Events House (out). Move tutors none left.
- **Flags:** new `FLAG_DEFEATED_METEOR_FALLS_STEVEN`, `FLAG_DEFEATED_KYOGRE`, `FLAG_DEFEATED_GROUDON`, `VAR_ABNORMAL_WEATHER_LOCATION`, `VAR_SHOULD_END_ABNORMAL_WEATHER`, `VAR_ROAMER_POKEMON`, `FLAG_MET_SCOTT_ON_SS_TIDAL`, `VAR_SS_TIDAL_SCOTT_STATE`, `FLAG_SYS_FRONTIER_PASS`, `FLAG_HIDE_SAFARI_ZONE_SOUTH_CONSTRUCTION_WORKERS` + `_SOUTH_EAST_EXPANSION`.
- **Needs:** **Phase 2:** Steven's Cave, Marine Cave 3 maps, Terra Cave 2, Safari NE / SE, Desert Underpass, the Frontier island (Tower + PWT; ground 56x72) + Reception Gate, Terra Cave doors on 10 routes, Marine Cave dive spots on 4 underwater routes (`Underwater_MarineCave` + 3 new underwater maps);
  **Phase 4:** abnormal-weather caves and the 16-spot picker, roamer by var; Phase 5: Scott.
- **Size:** ~370 L / ~40 T for the above (the Weather Institute event alone 168 L is Phase 4 plumbing). Frontier would be 87 scenes (not in scope). Text pass 160 + Frontier.

---

## 5. Cross-cutting lists

### 5.1 Scott (all new; `VAR_SCOTT_STATE` counts meetings)
Petalburg (Ch1, 47 L / 11 T, 4 triggers) - Rustboro school before / after badge 1 (Ch1, 27 L / 40 T) - Slateport (Ch3, 31 L / 22 T) - Mauville after Wally (Ch3, ~15 L) - Route 119 (Ch7, ~15 L + a call) - Lilycove motel (Ch8, 11 L / 18 T) - Mossdeep (Ch9, 18 L / 11 T) - Ever Grande Center (Ch11, 18 L / 9 T) - S.S. Tidal (Ch13, 18 L / 18 T) - Frontier gate (Ch13). Tent scenes (Slateport :835, Verdanturf, Fallarbor) out.
Needs one Scott overworld sheet + Black 2 code (Phase 5) and an `e_` story json row per meeting.

### 5.2 Match Call under decision 3A (every site, so builders do not rediscover them)
Messages / dropped: Mom registers (`Es:players_house.inc:293`); Devon scientist tutorial (`E:RustboroCity:31`); rival (`E:Route104:87-127`, Rustboro); Roxanne (`E:RustboroCity_Gym:93`); Norman (`E:Route104:355-367`); Steven (`E:GraniteCave_StevensRoom:22`); Brawly (Dewford Gym); Scott (`E:SlateportCity:73`); Birch (`E:Route110:559-607`); Wattson, Wally (`E:MauvilleCity:430-440`);
Flannery; Winona (`E:FortreeCity_Gym:47`); Scott's Fortree call (`E:Route119:461`); Tate & Liza; Juan (`E:SootopolisCity_Gym_1F:113`); rival Rayquaza call (`E:...SpaceCenter_2F:322-338`); Scott's Frontier call (`E:Lab:644`). 76 `register_matchcall` on route trainers: ignore. These reference the "POKéNAV"; HoennB2's item is the PokéNav (Xtransceiver), so wording can stay.

### 5.3 Flags and vars: how many, and where from
- **Measured** (names in the Ch0-12 maps' scripts.inc / map.json, minus temporaries, item balls, hidden items and `FLAG_SYS_*`; compared with
  `src/include/hoenn.h` and pokeruby's flags.h / vars.h): **405 distinct names Emerald uses that neither has**: 238 `FLAG_HIDE_*`, 42 in systems that
  are left out (Match Call, contests, Frontier, Tents, Trick House, Powder / Pokélot, Fan Club), 134 others (95 flags + 39 vars).
- Most are **renames** of ids HoennB2 already has: ~30 `FLAG_RECEIVED_HM_* / _TM_*`, the `VAR_*_STATE` family (`VAR_LITTLEROOT_TOWN_STATE`,
  `VAR_RUSTBORO_CITY_STATE`, `VAR_OLDALE_TOWN_STATE`, `VAR_BOARD_BRINEY_BOAT_STATE` ...), the daily berry flags, and about half of the hide flags (a crude token match
  pairs ~140 of them with Sapphire's; Ch0's `FLAG_HIDE_LITTLEROOT_TOWN_*` are all renames). Builders use HoennB2's name through an alias block in `hoenn_version.inc`.
- **Really new** (my estimate, not an exact count): **about 60-70 flags and 25-30 vars** for story state (the chapter lists in section 4), plus **about 60-100 hide flags**
  for Emerald-only objects (Scott x9, the Slateport queue, Magma Hideout / Space Center, Sootopolis legends and crowd, Mirage Tower fossils ...).
- **Pool** (`data/story_ids.json`): 874 free flags / 277 works at the start; unused today: **~309 reserved flags, 106 reserved works**, plus 6 flags / 56 works unreserved.
  Enough in total, but **the per-chapter blocks are too small**: every chapter got 16 flags / 6 works and Ch10 has 14 flags / 4 works left, while Sootopolis alone needs
  ~10 flags, ~17 hide flags and 4+ vars (S0-4: one Emerald block carved from the unused reserves). Emerald-only ids exist unused in Sapphire / Ruby builds (harmless; Ruby-only objects already do this).
- **Changed meaning** of existing ids (written elsewhere or with other values in Emerald): `VAR_SLATEPORT_STATE` / `_HARBOR_STATE` (writer moves from Mt. Pyre to Magma Hideout 4F), `VAR_MT_PYRE_STATE` (0-3 with the double return), `VAR_STEVENS_HOUSE_STATE` (Dive after the Space Center, 2 at Room 9), `VAR_SOOTOPOLIS_STATE` (0-6 + the Sky Pillar var), `VAR_RUSTBORO_STATE` (6-8), `FLAG_RECEIVED_RED_OR_BLUE_ORB` (now the Magma Emblem), `FLAG_SYS_WEATHER_CTRL` (also set at Sky Pillar, cleared by Rayquaza).
- Emerald's new-game flags: ~150 `setflag` at `E:data/scripts/new_game.inc:115` (S0-4).

### 5.4 Move tutors (10, one move each, one-time, 26 L)
Swagger (Slateport Fan Club), Rollout (Mauville), Fury Cutter (Verdanturf Center), Metronome (Fallarbor Mart), Mimic (Lavaridge house), Sleep Talk (Fortree house 2), Substitute (Lilycove Dept. Store roof), Dynamic Punch (Mossdeep), Double-Edge (Sootopolis Center), Explosion (Pacifidlog Center); `Es:move_tutors.inc`. Phase 1 supplies the move list (Gen 5 availability) and cost; each chapter builder adds its tutor with Black 2's tutor commands (STORY_SPECIALS 136 / 137).

### 5.5 Closed buildings (decision 2 / 1A)
Battle Tents x3 (Slateport, Verdanturf, Fallarbor), Trainer Hill (Route 111), Frontier facilities x6, Artisan Cave: each a door that does not open + one line. Needs one wording decision from the user (section 7).

### 5.6 Sprites and classes the story needs (Phase 1 / 5)
Scott; Tabitha (overworld + front, not code 88); Juan (Gym Leader, Black 2's 276 / 126 exist); Champion Wallace (class row, Black 2 Wallace 288 / 140); Magma grunt / leader classes beside Aqua's (Ruby swapped 5 classes; Emerald needs both at once: ~5 spare classes, unchecked); rival NPC sheet (code 162) in Emerald outfits; Groudon / Kyogre / Rayquaza objects (4511-4513) and Lati (4509 / 4510) exist.

### 5.7 Text pass sizes (SB `text.json`, near + new lines of the chapter's maps, Emerald vs pokeruby)
Ch0 79 - Ch1 226 - Ch2 165 - Ch3 278 - Ch4 149 - Ch5 111 - Ch6 170 - Ch7 66 - Ch8 292 - Ch9 122 - Ch10 171 - Ch11 115 - Ch12 31 - Ch13 160 (+ Frontier). About 1,975 lines for Ch0-12. The NPC / trainer share is regenerated by S0-1 / S0-3 / Phase 1; the rest (scene text) the chapter builder writes. The split was not measured.

---

## 6. Proposed builders and order

| # | Builder | Contents | Needs first | Size (L) |
|---|---|---|---|---|
| S0 | **emerald_story_infra** (Opus, per the 2026-10-07 rule for infrastructure; touches shared generators, Sapphire / Ruby outputs must diff clean) | S0-1 to S0-6 | Phase 0 (done); coordinate `world.py` read of the Emerald content json with emerald_world; sprite / class rows with emerald_art / emerald_data | ~1 day |
| B1 | **emerald_ch0_3** | Ch0 rival scenes + Mom + twin text, Ch1 Scott x2, Ch2 Rustboro / Route 104 rival battle, Ch3 Scott + queue + closed tents + Pokéblock note, Ch6 Wally's dad / Surf, Ch7 Scott; text pass of those scenes | S0; Phase 1 rival ids #592-769 (6); Scott sheet. **No new maps** | ~600 |
| B2 | **emerald_ch45_magma** | Ch4 Route 112 + Meteor Falls swap, Ch5 Mt. Chimney (13 `model_emerald` swaps) + Jagged Pass guard / door | S0; Phase 1 Maxie / Tabitha / grunt ids, Magma classes; Tabitha sheet. **No new maps** (Jagged Pass mouth is an alt-door question for emerald_world) | ~210 |
| B3 | **emerald_ch11_gameclear** | Ch11 Champion Wallace, Hall of Fame + `Sub_Ch13_GameClear` Emerald block, Scott at Ever Grande, Lati-colour TV + S.S. Ticket, Johto starters (needs lab layout), S.S. Tidal Scott | S0; Phase 1 Wallace #335; **small Phase 2 pieces** (League 2F, lab table) only for the last two items | ~350 |
| B4 | **emerald_ch8** | Mt. Pyre summit + orb return (Ch10 entries), Slateport trigger move, Scott motel, Pokéblock Case move, then Magma Hideout 4F Maxie scene | S0; Phase 1 Magma ids + `ITEM_MAGMA_EMBLEM`; **Magma Hideout maps** for the last item (Mt. Pyre part can start with B1) | ~215 |
| B5 | **emerald_ch9** | Space Center 1F / 2F, Steven's tag battle, Dive gate, Scott, Mossdeep Gym win flags / rotating-tile gym | **Phase 4 tag battle + rotating tiles**, Mossdeep ground, Phase 1 Magma slots | ~290 |
| B6 | **emerald_ch4_mirage** | Mirage Tower fossils, collapse, Route 111 sinking, Desert Underpass, Fossil Maniac hints, closed Trainer Hill / Fallarbor tent | **4 Mirage maps + Route 111 layouts + Phase 4 Mirage mechanics** | ~150 |
| B7a | **emerald_ch10_seafloor** | Seafloor entrance hint, Room 9 branch, Route 128 check, Cave of Origin B1F Wallace, Juan, Waterfall, Mt. Pyre return check | Seafloor Room 2 / 3 ground, Cave of Origin B1F room, Gym 150 blocks, Juan class | ~330 |
| B7b | **emerald_ch10_sootopolis** | Sootopolis City (map scripts, legends scene, Rayquaza scene, citizens, Steven / Wallace / Archie / Maxie), Sky Pillar Outside / Top / floors, Route 131 always-on | **LEGENDS_BATTLE layout, 6 clean Sky Pillar variants, Phase 4 sequence (weather x2, camera, door lock)** | ~800 |
| B8 | **emerald_ch12_13** | Regi puzzle triggers; Steven's Cave, Marine / Terra Cave, abnormal-weather glue, Safari expansion shown, Frontier gate scene + closed doors, roamer-by-var | Phase 2 post-game maps, Phase 4 weather event + roamer + Regice hook | ~450 |
| C | **per new area, a separate glitch-check agent** (standing rule), then `script_check` + `progression_check` on the Emerald ROM, forced-loss test for every battle scene (Mt. Chimney, Hideout, Space Center), save test, refresh `release/` | after each builder | |

Every builder: Sapphire and Ruby generated files unchanged (diff), `script_check` 0 open, the chapter's `HOENN_TEST_CH<n>` start state played once through
its main beats (rival, villain scene, boss, key items; a forced loss on each battle), proofs in `screenshots/<you>/`, and the save margin reported.

Order: **S0 -> (B1, B2, B3 in parallel) -> B4 (Mt. Pyre part) -> B6 / B4 (Hideout) / B5 as maps and mechanics land -> B7a -> B7b -> B8**. B1-B3 can start the day S0-1/S0-2/S0-5 are in; B4's Mt. Pyre half can run with them. If S0 slips, B1-B3 can still write their scene bodies in `scenes/emerald/` files and test with `HOENN_TEST_CH<n>` start states, since scenes that sit in rooms (Scott in the School, Wally's house, Champion's room) need no renumbering.

---

## 7. Open questions (for the lead / user)

1. **Trainer ids** (section 0.6, Appendix B): confirm Phase 1 will build an Emerald registry that re-uses freed Sapphire ids by number where the slot is the same trainer and by role-twin elsewhere. Without it nothing naming a new trainer finishes.
2. **Closed-building wording** (tents, Trainer Hill, six Frontier buildings, Artisan Cave): one generic HoennB2 line is new text, not Emerald's. Proposal: "The doors are locked. It doesn't seem to be open yet." Needs the user's word-for-word rule applied.
3. **Keep the "Registered X in the PokéNav" lines** (flavor, no list) or cut them? Proposal: keep (3A says calls become messages).
4. **Rival Rustboro / Route 104 battle** is optional in Emerald and needs six trainer ids for a fight a player can skip. Keep (proposal) or reduce to the no-battle meeting Sapphire has?
5. **Rayquaza** is catchable right after the Sootopolis scene at Sky Pillar (no game-clear check). Proposal: as Emerald.
6. **Weather look** for Emerald's "abnormal" weather (the user picked id 3 for Groudon's drought by looking at stand-ins): same kind of choice needed.
7. **Who writes `gen_interiors` Emerald mode** (S0 or emerald_world).
8. The first Emerald story build should print the a/0/5/6 and a/0/0/3 fill (both RESERVE 1 MB; Emerald adds ~3,000 script lines and ~1,300 text lines on top of 57k lines / 306k characters today) and the menu-save margin (28,896 B in v16.5, must stay above ~10 KB: brief).

---

## Appendix A: size of the new / changed Emerald scene groups (measured; L / T = script commands / text lines, shared helpers counted once per group)

| Ch | Group | Entry label (file:line) | L | T |
|---|---|---|---|---|
| 0 | Rival meets you (4 entries) | `E:LittlerootTown_BrendansHouse_1F:119-137`, `E:MaysHouse_2F:48` | 216* | 46 |
| 0 | Rival mom / sibling / neighbour / 2F | `E:MaysHouse_1F:86,110,136`, `E:MaysHouse_2F:224` | 66 | 60 |
| 0 | Johto starters + table lab | `E:Lab:247` ChooseJohtoStarter, balls | 150* | 41 |
| 0 | Mom registers you (message) | `Es:players_house.inc:293` | 31 | 0 |
| 1 | Scott Petalburg | `E:PetalburgCity:486-518` | 47 | 11 |
| 1 | Scott School | `E:RustboroCity_PokemonSchool:159` | 27 | 40 |
| 2 | Rival battle Rustboro + Route 104 | `E:RustboroCity:634-722`, `E:Route104:47,81` | 248* | 115 |
| 3 | Scott Slateport + queue | `E:SlateportCity:53,414` | 72 | 40 |
| 3 | Birch call (drop) | `E:Route110:559` | 56 | 20 |
| 4 | Route 112 Magma grunts | `E:Route112:10` | 27 | 8 |
| 4 | Meteor Falls Magma steals | `E:MeteorFalls_1F_1R:16`, `:212` | 77 | 57 |
| 4 | Mirage Tower fossils / collapse / sink | `E:MirageTower_4F:4`, `E:Route111:107` | 71 | 14 |
| 4 | Fossil Maniac + Desert Underpass | `E:Route114_FossilManiacsTunnel:24`, `E:DesertUnderpass:9` | 38 | 28 |
| 5 | Mt. Chimney Maxie + Archie | `E:MtChimney:14,33` | 57 | 65 |
| 5 | Jagged Pass guard + door | `E:JaggedPass:39,65` | 44 | 13 |
| 6 | Wally's dad + Surf | `E:PetalburgCity:57`, `E:PetalburgCity_WallysHouse:7-23` | 34 | 17 |
| 7 | Scott call Route 119 | `E:Route119:461` | 7 | 13 |
| 8 | Mt. Pyre summit | `E:MtPyre_Summit:14,145` | 65 | 55 |
| 8 | Magma Hideout 4F Maxie | `E:MagmaHideout_4F:4` | 63 | 33 |
| 8 | Scott motel | `E:LilycoveCity_CoveLilyMotel_2F:53` | 11 | 18 |
| 9 | Magma enters Space Center | `E:MossdeepCity:76` | 23 | 0 |
| 9 | Space Center 1F | `E:...SpaceCenter_1F:6,101,178` | 54 | 22 |
| 9 | Space Center 2F + Steven multi battle | `E:...SpaceCenter_2F:31,170` | 129 | 60 |
| 9 | Steven gives Dive | `E:MossdeepCity_StevensHouse:28` | 19 | 16 |
| 9 | Scott Mossdeep | `E:MossdeepCity:249` | 18 | 11 |
| 9 | Tate & Liza | `E:MossdeepCity_Gym:51` | 51 | 70 |
| 10 | Seafloor entrance hint | `E:SeafloorCavern_Entrance:10` | 32 | 24 |
| 10 | Room 9 | `E:SeafloorCavern_Room9:4` | 123 | 70 |
| 10 | Route 128 Kyogre scene | `E:Route128:14` | 55 | 43 |
| 10 | Sootopolis legends scene | `E:SootopolisCity:171` | 138 | 0 |
| 10 | Sootopolis Rayquaza scene | `E:SootopolisCity:456` | 124 | 0 |
| 10 | Steven guides | `E:SootopolisCity:857` | 48 | 37 |
| 10 | Wallace / Maxie / Archie | `E:SootopolisCity:1248,1302,1317` | 64 | 61 |
| 10 | Citizens | `E:SootopolisCity:678-1250` | 179 | 111 |
| 10 | Sootopolis map scripts | `E:SootopolisCity:9-165` | 102 | 0 |
| 10 | Cave of Origin B1F Wallace | `E:CaveOfOrigin_B1F:4` | 42 | 45 |
| 10 | Sky Pillar Outside | `E:SkyPillar_Outside:33` | 49 | 21 |
| 10 | Sky Pillar Top | `E:SkyPillar_Top:18,43,87` | 82 | 1 |
| 10 | Mt. Pyre orb return | `E:MtPyre_Summit:171` | 75 | 3 |
| 10 | Juan | `E:SootopolisCity_Gym_1F:81` | 49 | 87 |
| 11 | Champion Wallace | `E:EverGrandeCity_ChampionsRoom:23` | 93 | 93 |
| 11 | Hall of Fame + game-clear flags | `E:...HallOfFame:18`, `Es:hall_of_fame.inc:1` | 81 | 10 |
| 11 | Scott Ever Grande | `E:EverGrandeCity_PokemonCenter_1F:32` | 18 | 9 |
| 13 | Lati TV + S.S. Ticket | `Es:players_house.inc:392` | 114 | 0 |
| 13 | S.S. Tidal Scott | `E:SSTidalCorridor:185` | 18 | 18 |
| 13 | Steven's Cave | `E:MeteorFalls_StevensCave:4` | 17 | 23 |
| 13 | Marine / Terra Cave | `E:MarineCave_End:25`, `E:TerraCave_End:25` | 56 | 0 |
| 13 | Abnormal-weather event | `Es:abnormal_weather.inc:173` | 168 | 0 |

(* entries that share most of their code are summed, so these overstate the unique work by ~2x.)
Chapter totals of the groups: Ch0 463 / 147, Ch1 74 / 51, Ch2 248 / 115, Ch3 128 / 60, Ch4 213 / 107, Ch5 101 / 78, Ch6 34 / 17, Ch7 7 / 13, Ch8 139 / 106, Ch9 294 / 179, Ch10 1,162 / 503, Ch11 192 / 112, Ch13 373 / 41.

## Appendix B: Emerald trainers named in Ch0-Ch12 map scripts that have no Sapphire slot (by number)

Method: every `TRAINER_*` in `trainerbattle_*` lines of the Ch0-12 maps, number from pokeemerald `opponents.h`, compared with the numbers of the 604 trainers in `data/hoenn_trainers.json` (numbers are the same in both decomps, SB §1). 518 distinct; **161 without a slot**: 106 route / cave, 30 grunts, 15 gym trainers, 6 rival fights, 4 Maxie / Tabitha (+ #734 / #514 for the Space Center battle, not a script line).
Story-critical ones to name in Phase 1 first:

| Scene | Emerald trainer (#) | Sapphire role-twin |
|---|---|---|
| Rustboro / Route 104 rival | `{BRENDAN,MAY}_RUSTBORO_{TREECKO,TORCHIC,MUDKIP}` (#592 593 599 600 768 769) | none |
| Mt. Chimney | `MAXIE_MT_CHIMNEY` #602, `TABITHA_MT_CHIMNEY` #597, `GRUNT_MT_CHIMNEY_1/2` #146 #579 | Sapphire's `ARCHIE_3` (#35) / `MATT_2`, Ruby gave Maxie #35's id |
| Jagged Pass | `GRUNT_JAGGED_PASS` #570 | none |
| Mt. Pyre | 4th Aqua grunt #569 | `GRUNT_22-24` |
| Magma Hideout | `MAXIE_MAGMA_HIDEOUT` #601, `TABITHA_MAGMA_HIDEOUT` #732, `GRUNT_MAGMA_HIDEOUT_1-16` #716-731 | none (Ruby's hideout trainers are other numbers) |
| Space Center | `GRUNT_SPACE_CENTER_1,3-7` #22 #586-590 (+2 = #116), Maxie #734, Tabitha #514 | none |
| Weather Institute / Seafloor / Aqua Hideout | 5th grunt #596, `GRUNT_SEAFLOOR_CAVERN_5` #567, `GRUNT_AQUA_HIDEOUT_7/8` #192 #193 | same roles, new numbers |
| Gyms | `NORMAN_1` #269 etc. same; 15 gym trainers with no slot: Rustboro #571, Dewford #572-574, Mossdeep #575 #582-585 #591, Mauville #802, Fortree #402 #803, Sootopolis #115 #502 | |
| Champion / Gym 8 / post-game | `WALLACE` #335 (= Sapphire `STEVEN`), `JUAN_1` #272 (= `WALLACE`), `STEVEN` #804 | role swap on the same id |

## Appendix C: Phase 4 mechanics the story calls (with the line that needs it)

| Mechanic | Where | Notes |
|---|---|---|
| Tag battle with Steven, 3 of 6 chosen | `E:SpaceCenter_2F:223-244` | `CallTrainerMultiBattle` (FieldCommand 134) exists; selection, partner party, loss path new |
| Legends scene: camera object, shakes, weather swap, layout swap | `E:SootopolisCity:9-165,171-455,456-560` | `EvCamera*`, `EvCameraShake` exist (STORY_SPECIALS 54, 206); alt layout via `MapReplaceSetEvent` (ids 2, 7 used) |
| Two crisis weathers | `E:SootopolisCity:84-96`, `Common_EventScript_SetAbnormalWeather` on 10+ maps | `patches/weather.py` has one id per version |
| Closed doors without `setmetatile` | `E:SootopolisCity:18-30`, `E:JaggedPass:30-37`, `E:SkyPillar_Outside:20-27` | HoennB2 pattern: warp moved off-map + sign |
| Clean / cracked room variants | `E:SkyPillar_1F:6` ... `SkyPillar_Top:18` | `room_variants.emerald` + runtime selection (precedent: Shoal Cave tides, Mauville Gym `alt_rooms`) |
| Mirage Tower visibility, crumble, sink | `src/mirage_tower.c:317-339`, `E:Route111:107`, `E:MirageTower_4F:44-61` | 6 specials |
| Rotating tiles | Mossdeep Gym (20 commands) | Trick House P7 not built |
| Regi puzzles | `src/braille_puzzles.c:167-340` | step-trigger pattern exists (`h_field_move_user`); Regice 36 tiles |
| Abnormal weather picker | `src/field_specials.c:3445-3465`, `Es:abnormal_weather.inc` | post-game |
| Roamer / island Lati by var | `Es:players_house.inc:443-446`, `src/roamer.c:84-89` | `roamers.py` + 2 story objects |
| Orb flash (Magma Hideout 4F, Room 9) | `DoOrbEffect`, `FadeOutOrbEffect` | one white flash (as Ruby / Sapphire in HoennB2) |

---

## 6. Magma chapters, builder B2 + B4's map-free half (emerald_ch45_magma, 2026-10-12)

Built and played on an Emerald ROM (Sapphire's world with Emerald's scripts, text, models and trainers). Sapphire and Ruby: their
assembled field scripts are byte for byte the same with and without these files (`work/agents/emerald_ch45_magma/ident_*.txt`:
521 Sapphire and 524 Ruby scripts, SHA-1 of each), no shared text file changed, `patches/story.py` ignores every `_emerald` key.

### 6.1 What each scene does now (Emerald)
| Scene | Files | What it does |
|---|---|---|
| Route 112 cable car guards | `scenes/Route112.inc` (R112_MagmaTalk), `src/text/scenes/emerald/Route112.txt` | two Magma grunts (models swapped by S0) talk to each other, four lines, each turns to the other (pokeemerald `MagmaGrunts`); talking to either runs it |
| Meteor Falls | `0256_room_MeteorFalls_1F_1R.s` branches, `src/text/script/emerald/0147_...txt` | Ruby's flow with Emerald's lines: Magma steals the Meteorite, Archie and two Aqua grunts arrive and chase them; encounter songs; movement lists of pokeemerald (7 tiles, player ends facing right) |
| Mt. Chimney | `scenes/MtChimney.inc`, `scenes/em_magma_lib.inc`, `src/text/scenes/emerald/MtChimney.txt`, `data/story/ch5.json` (`*_emerald` keys), `data/story/emerald/e_ch5.json` | Maxie at the machine (battle `TRAINER_MT_CHIMNEY_GRUNT_3` = Emerald's Maxie), Archie asks you to stop him, Tabitha + 2 grunts as eye-contact trainers, six different Magma grunt lines (2 Emerald-only entries 15, 16), Poochyena lines swapped, the Lava Cookie lady appears after Maxie, Sawyer joins the trainers |
| Jagged Pass | `scenes/JaggedPass.inc`, `JaggedPass_init.inc`, `text/scenes/emerald/JaggedPass.txt`, `e_ch5.json` | guard in front of the cave mouth (talk, "!", battle `TRAINER_GRUNT_JAGGED_PASS`, after-line), Magma Emblem check on entering (`VAR_JAGGED_PASS_STATE` 0 -> 1), five trigger tiles run the shaking scene (state 1 -> 2) |
| Mt. Pyre summit | `scenes/MtPyre_Summit.inc` (+ `_Em.inc`, `_init.inc`), `text/scenes/emerald/MtPyre_Summit.txt`, `ch8b.json`, `e_ch8.json` | state 0: Archie takes the Red Orb, four Aqua grunts leave with him, the old woman gives the **Magma Emblem** (key item = Black 2's Magma Stone) and the Jagged Pass guard leaves; state 2 (Ch10 sets it): Archie and Maxie walk past you, Maxie speaks, they return both Orbs (state 3); old man's new tale after Sootopolis; Maxie / Archie stand side by side from the zone init |
| Slateport trigger move | same Mt. Pyre file | NOT set at Mt. Pyre any more (see the work list) |
| Scott at the Cove Lily Motel | `0360_room_LilycoveCity_CoveLilyMotel_2F.s`, `0238_...txt`, `e_ch8.json` | Scott dozes (object visible from the start): first talk `VAR_SCOTT_STATE` +1 and `FLAG_MET_SCOTT_IN_LILYCOVE`, later talks his contest remark |
| Pokéblock Case | `0322_room_LilycoveCity_ContestLobby.s`, `1190_room_SlateportCity_ContestLobby.s`, `0219_...txt` | the Lilycove receptionist gives it at the first visit; the Slateport girl no longer does |
| Aqua Hideout 1F guards | `0004_room_AquaHideout_1F.s`, `0005_...txt` | Emerald's three hints (before Mt. Pyre / after the Emblem / after Groudon wakes) instead of Sapphire's `FLAG_MT_PYRE_ORB_STOLEN` |

Shared pieces added: `b2tools/patches/story.py` `version_keys` (`"<key>_emerald"` replaces `"<key>"` in an Emerald build: `script_emerald`,
`at_emerald`, `flag_emerald`, `p0_emerald`, `skip_emerald`; Ruby's `model_ruby` is the same rule), `ITEM_MAGMA_EMBLEM` in `hoenn_version.inc` (+
`src/text/emerald/overrides_magma_emblem.json`), ids claimed from the Emerald block (`FLAG_HIDE_MT_CHIMNEY_LAVA_COOKIE_LADY`, `FLAG_HIDE_MT_PYRE_SUMMIT_MAXIE`,
`VAR_JAGGED_PASS_STATE`, `FLAG_BEAT_MAGMA_GRUNT_JAGGED_PASS`, `FLAG_HIDE_JAGGED_PASS_MAGMA_GUARD`, `FLAG_SOOTOPOLIS_ARCHIE_MAXIE_LEAVE`,
`FLAG_GROUDON_AWAKENED_MAGMA_HIDEOUT`), test-kit lines (`ch5_test.inc`, `ch8b_test.inc`, switches `HOENN_TEST_CH5_SKIP`, `HOENN_TEST_CH5_EMBLEM`).
Text overlays are produced by `work/agents/emerald_ch45_magma/gen_em_text.py` from pokeemerald's strings (`--check` compares).

### 6.2 What the Emerald generator run must see (for the lead, the day work/world_emerald exists)
- `gen_map_content.py` in Emerald mode must be run after `sapphire_data.py` for MtChimney, Route112, JaggedPass, MtPyre_Summit: Mt. Chimney's zone has 16 story
  entries in Emerald (14 + the two Emerald-only 15 / 16), so its generated sign becomes Script_17 with message 27; Jagged Pass has 3 entries (no generated
  people) and its init file includes `scenes/JaggedPass_init.inc`; Mt. Pyre summit has 9 entries (the 9th is the zone init, `MapScript 2, 9` in
  `scenes/MtPyre_Summit_init.inc`). Until that run an Emerald build uses Sapphire's generated files: only these three zones are affected (Mt. Chimney's route
  sign and its two extra Magma grunts point at wrong scripts / lines, Jagged Pass and the Pyre init do nothing).
- A Sapphire / Ruby run of the generator rewrites two shared files (text only, same assembled bytes): `0037_auto_JaggedPass_init.s`, `0059_auto_MtPyre_Summit_init.s`.

### 6.3 Tests (Emerald ROM built from a snapshot of HEAD + these files, muted DeSmuME, Lv 100 Swampert from the chapter kits)
Proofs are in `screenshots/emerald_ch45_magma/` (256x192 frames; storyboards are sheets of them): Route 112 guards `route112_grunts.png`;
Meteor Falls `meteor_storyboard.png`; Mt. Chimney: `chimney_cablecar.png` (ride up), `chimney_foot_talkers.png` (Aqua grunt, the two Poochyena, Magma grunt),
`chimney_tabitha_storyboard.png` (Tabitha's battle, won), `chimney_maxie_storyboard.png` (whole Maxie scene, battle won, Archie thanks you),
`chimney_loss_storyboard.png` + `chimney_loss_final_384.png` + `chimney_loss_after_walk.png` (the same battle lost: whiteout to the house, the player walks
on), `chimney_after_machine_lady.png`, `chimney_lady_after_reload.png` (the Lava Cookie lady sells a cookie after the map reloaded); Jagged Pass
`jagged_guard_storyboard.png`, `jagged_open_storyboard.png`; Mt. Pyre `pyre0_storyboard.png`, `pyre0_emblem_detail.png` ("obtained the Magma Emblem!"),
`pyre2_storyboard.png`; `motel_storyboard.png` (Scott); `lobby_storyboard.png` (Pokéblock Case).
The new Magma grunt (F) at Mt. Chimney and the fourth Aqua grunt on Mt. Pyre fought with Emerald's lines. `script_check` on the zones 2, 18, 19, 29, 128, 161,
180, 374: 0 open. A whole-ROM `script_check` of the Emerald test ROM with the final scripts patched in (`work/agents/emerald_ch45_magma/script_check_em_work_full.txt`): 2 open, the two
known Emerald hidden items (Route 105, Route 123), as S0 reported. Save margin of the Emerald build: 28,896 B (unchanged: no model or pack-0 change).
Test switches added (builds with `HOENN_TEST_CH5=1` ...): `HOENN_TEST_CH5_SKIP=1|2` (Mt. Chimney's grunts / also Tabitha count as beaten),
`HOENN_TEST_CH5_WEAK` (a Lv 2 Magikarp party: the loss test), `HOENN_TEST_CH5_EMBLEM` (Jagged Pass gives the Emblem), `HOENN_TEST_CH8B=3` (Mt. Pyre summit in state 2).
Quick re-test without a full build: `work/agents/emerald_ch45_magma/qp.py` re-assembles single scripts into a ROM copy (a/0/5/6 is padded to a fixed size),
`t_places.py` plays a place after a `HOENN_TEST_WARP` patch of Littleroot's sign script.
Findings while testing: (1) Sapphire's terrain (the world used until emerald_world's Emerald world exists) keeps the Jagged Pass guard's tile (16,19)
out of reach: a ledge at (16,20); the guard test moved him to a reachable tile in the ROM copy. (2) The Meteorite machine can only be read from the tile south
of it (the sign's height; as in Sapphire).

### 6.4 Work list: what waits for new maps
**emerald_world (Phase 2):**
- **Done (emerald_integrate 2026-10-12, notes/EMERALD.md "Integration": sealed layout, open alt layout on map replace event 1, `JP_HIDEOUT_WARP 6`).** Jagged Pass: the cave mouth at (16,17)-(16,18) is OPEN in pokeemerald's layout (metatiles 0x256 / 0x25e) and OnLoad covers it with rock wall (0x274) while
  `VAR_JAGGED_PASS_STATE` < 2. The Emerald world needs a closed variant of those two tiles as the default and the open one as an alternate layout for state 2 (like
  Route 131's islet, event number to be claimed), and the warp (16,18) elevation 0 -> MagmaHideout_1F warp 0, switched off until state 2 (`JP_HIDEOUT_WARP` in
  `scenes/JaggedPass.inc`, `ObjInitWarpGPos n, 0, 0, 0` as `scenes/LilycoveCity.inc` does). Until then the opening scene only shakes the screen and sets the state.
- Magma Hideout: the 8 maps (`maps.emerald.new`, names clash with Ruby's: give them `_Emerald` names), their zone / script / text numbers, `versions.json` rooms.
- **Done (emerald_integrate).** Contest lobbies / halls of Slateport, Verdanturf, Fallarbor are 'gone' in Emerald: list them as not-Emerald in `data/versions.json` rooms (the Slateport lobby script is
  guarded anyway).
**B4 (the Magma Hideout scenes), template `0380_room_SeafloorCavern_Room9.s` (Archie wakes Kyogre):**
(**Done 2026-10-12 by emerald_ch8_hideout: items 1-4 below, see 6.5.**)
1. `E:MagmaHideout_4F:4-60` (Maxie, 63 L / 33 T): `em_bgm_magma` (scenes/em_magma_lib.inc), sleeping Groudon object swapped for the awake one (`MODEL_GROUDON` 4512),
   `dofieldeffectsparkle 18,42` and `DoOrbEffect` / `FadeOutOrbEffect` = Room 9's single white flash, Groudon's approach and exit, two `EvCameraShake` (parameters of
   `scenes/JaggedPass.inc` JP_OpenHideout), `trainerbattle_no_intro TRAINER_MAXIE_MAGMA_HIDEOUT` (403), Maxie leaves.
2. The scene's last lines set (HoennB2 names): clear `FLAG_HIDE_STERN_SLATEPORT` and `FLAG_HIDE_GABBY_AND_TY_SLATEPORT`, `VAR_SLATEPORT_STATE` 1,
   `VAR_SLATEPORT_HARBOR_STATE` 1, set `FLAG_GROUDON_AWAKENED_MAGMA_HIDEOUT` (claimed, id 639), set `FLAG_HIDE_MAGMA_HIDEOUT_GRUNTS` (claim), remove Maxie, the three
   grunts and Tabitha. These are exactly what Sapphire's Mt. Pyre scene set (plus `FLAG_MT_PYRE_ORB_STOLEN`, which only the Sapphire / Ruby hideout guards read: Emerald's
   Aqua Hideout 1F guards use `FLAG_GROUDON_AWAKENED_MAGMA_HIDEOUT` now).
3. Magma Hideout trainers: `TRAINER_GRUNT_MAGMA_HIDEOUT_1..16`, `TRAINER_TABITHA_MAGMA_HIDEOUT` (src/include/hoenn_trainers_emerald.h); item balls from the Emerald
   items run; the Strength boulders on 1F.
4. Enter from Jagged Pass: test with `HOENN_TEST_CH5_EMBLEM=1` (Emblem + state 1), then walk to the door.
**Ch10 (B7):** at Sootopolis (`E:SootopolisCity:1336-1337`) set `VAR_MT_PYRE_STATE` 2, clear `FLAG_HIDE_LEADER_MT_PYRE_SUMMIT` (= pokeemerald's
`FLAG_HIDE_MT_PYRE_SUMMIT_ARCHIE`) and `FLAG_HIDE_MT_PYRE_SUMMIT_MAXIE`, and set `FLAG_SOOTOPOLIS_ARCHIE_MAXIE_LEAVE` (claimed, id 638). The summit scene (entries 6-8) sets
state 3 and the old woman's talk sets `FLAG_RETURNED_RED_OR_BLUE_ORB`. `MtPyre_Summit_Ch10.inc` is Sapphire's only (Emerald's file is `MtPyre_Summit_Em.inc`).
**B6 (Mirage Tower):** Route 112's OnTransition also clears `FLAG_FORCE_MIRAGE_TOWER_VISIBLE` (a comment marks the place in `scenes/Route112.inc` R112_Init).
**Lead:** run the Emerald generator once `work/world_emerald` exists (section 6.2); the Fallarbor Battle Tent Scott flag and `FLAG_MET_ARCHIE_METEOR_FALLS` (Match Call
only) were left out under decisions 2 and 3A.

### 6.5 Magma Hideout story: builder B4's second half (emerald_ch8_hideout, 2026-10-12)

**What the Emerald build does now** (all Emerald only; Sapphire and Ruby read none of it: the new files sit in `emerald/` folders or are keys of the Emerald block):
- **Jagged Pass to the door.** Unchanged from 6.1 (guard, Emblem check, five trigger tiles, the shaking scene opens the cave mouth, `VAR_JAGGED_PASS_STATE` 2). Played together with the
  door for the first time: the mouth opens, the player walks down the ledge and stairs to the door and arrives in 1F at (10,34). The door only works in a world that has the Hideout rooms:
  **the lead's `work/world_emerald` is older than the caves and still has the door unresolved (`dest_zone` null, parked off the map); `rebuild_slice.sh`'s Emerald block rebuilds it** (emerald_caves'
  `work/agents/emerald_caves/world_emerald` already has door 4 -> zone 349 and is what this builder tested on).
- **1F needs Strength.** The way on from the entrance is the corridor with three Strength boulders (5,22) (7,22) (6,23), as in pokeemerald: push (6,23) left, step up to (6,22), push (5,22)
  left, walk up the column x=5 (each push takes two steps: the boulder moves first). Past it: the middle and east of 1F and the door (25,34) to 2F_1R. The north-east of 1F (warp (31,3), where
  2F_2R comes out), the north-west pocket (grunt 1 at (4,5) and the Rare Candy at (3,20)) and the platform of the 2F_3R warp (20,22) are not reachable from the entrance: you come to them from
  2F_2R, and the platform only from 2F_3R, leaving by a one-way ledge (checked with a breadth-first search on pokeemerald's own collision: the same 299 tiles from the entrance as in the built
  rooms). The main way to Maxie is 1F -> 2F_1R (17,33) -> 3F_1R (7,21) -> 4F (46,7), then round the lava pool to his west side; 4F's second entrance (20,21) is the shortcut out.
- **The 16 grunts and Tabitha** stand in their rooms as eye-contact trainers (Black 2's own trainer scripts 3000 + trainer id, `evtype 1`, sight, facing and walking patterns from pokeemerald through
  `b2tools/move_codes.py`), hidden together by `FLAG_HIDE_MAGMA_HIDEOUT_GRUNTS`. Data: `data/story/emerald/e_ch8_hideout.json` (generated by `work/agents/emerald_ch8_hideout/tools/mk_story_json.py`
  from pokeemerald's eight map.json files and `data/emerald/hoenn_trainer_data.json`; rooms are placed by "zone" + pokeemerald tile because story.py reads Sapphire's `hoenn_interiors.json` and an
  Emerald-only room has no entry there; the rooms' origin is (0,0)). Their lines are the trainers' own messages (intro, defeat, after: all three exist for every one of them).
- **Maxie on 4F** (`0718_room_MagmaHideout_4F.s`, script 2, text `src/text/script/emerald/0571_room_MagmaHideout_4F.txt` made by `converter/gen_emerald_magma_text.py`): talk to him from his west side and
  the pokeemerald scene plays: Magma music, "Groudon... Blue Orb", the sound and one white flash (Room 9's), the sleeping Groudon (object 7) is swapped for the awake one (object 1, Black 2 model
  4512, both at (16,17)), it walks two tiles down and back up out of sight with the two camera shakes (pokeemerald's exact movement lists), Maxie looks around and says "What's wrong?", the player
  turns, "Oh, so it was you?", the battle (`TRAINER_MAXIE_MAGMA_HIDEOUT`, Lv 40-42 trio), his farewell, then the flags below, a fade, and Maxie, the three 4F grunts and Tabitha are gone.
  **Flags the scene sets** (6.4's list): `VAR_SLATEPORT_STATE` 1, `VAR_SLATEPORT_HARBOR_STATE` 1, `FLAG_HIDE_STERN_SLATEPORT` and `FLAG_HIDE_GABBY_AND_TY_SLATEPORT` cleared (Sapphire's Pyre
  scene did this), `FLAG_GROUDON_AWAKENED_MAGMA_HIDEOUT`, `FLAG_HIDE_MAGMA_HIDEOUT_GRUNTS`; Groudon's two objects end hidden (`FLAG_HIDE_MAGMA_HIDEOUT_4F_GROUDON` / `_ASLEEP`).
  **A loss** ends as every scripted battle (whiteout, the player walks again at the respawn point). The sleeping Groudon stays gone (its remove set its flag, as in pokeemerald), so the scene
  replays when you talk to Maxie again with the awake Groudon appearing from nothing: played, it runs through to the end.
- **Item balls** (Rare Candy 1F, Max Elixir and Full Restore 2F_2R, Nugget 3F_1R, PP Max 3F_2R, Escape Rope 3F_3R, Max Revive 4F): the ones emerald_caves placed from emerald_data's list; all seven picked up in game.
- **Ids claimed** (group Emerald): `FLAG_HIDE_MAGMA_HIDEOUT_GRUNTS` 748, `FLAG_HIDE_MAGMA_HIDEOUT_4F_GROUDON` 835 (a pokeemerald new-game flag: `scenes/new_game_flags.inc` sets it, checked on a real
  new game), `FLAG_HIDE_MAGMA_HIDEOUT_4F_GROUDON_ASLEEP` 836.
- **Test kits.** `HOENN_TEST_CH8B=<stage>` now also runs from Jagged Pass's zone init (`scenes/JaggedPass.inc`, test builds only): stage 2 = six badges, HM01-04, the Magma Emblem (the Hideout needs
  Strength). `emerald_test_chain.inc` sets the Hideout's end state from AT 90 on (Groudon awake and gone, grunts hidden, Maxie beaten); the Ch5 and Ch8b kits set the new-game hide flag for
  states made before it. The Ch8b kit's stage 2 still arms Slateport in Emerald as before (the shared kit was left alone): in the game that happens at the end of this scene.

**Tests** (muted DeSmuME, `work/agents/emerald_ch8_hideout/tests/`, proofs `screenshots/emerald_ch8_hideout/01..09_*.png`; ROM `rom_emerald/emh8.nds` = HEAD 2ea8bc3 + these files, built with
`HOENN_TEST_CH5=2 HOENN_TEST_CH5_EMBLEM=1 HOENN_TEST_NO_WILD=1 HOENN_TEST_WARP=563,6,7`, then Jagged Pass re-assembled with `HOENN_TEST_CH8B=2` by `tools/qp.py`; a Lv 100 Swampert, PP refilled in RAM
before Maxie because the battle bot drains it): the Jagged Pass scene and the door -> 1F -> the boulder puzzle -> 2F_1R -> 3F_1R -> 4F -> Maxie (the bot fought all 17 trainers: both 1F
grunts, the four in 2F_1R (two of them walkers), the four in 2F_2R, both in 3F_1R, grunt 10 in 3F_2R, the three on 4F and Tabitha); the win, a forced loss (party Lv 1 / 1 HP: whiteout, walks again), the replay after a
loss; the way out after the scene (4F -> 3F_3R -> 2F_3R -> the 1F platform, ledge down; every grunt gone); all seven item balls. Flags before/after the scene read from RAM
(Slateport vars 0/0 -> 1/1, Stern and Gabby & Ty hidden -> shown). `script_check` on the eight rooms and Jagged Pass: 0 open (its one accepted line, Groudon walking on its lava pool, joined the
Room 9 Kyogre rule in `b2tools/script_check.py`); `scene_walks` on 0718 / 0036: 0; every kit user (52 files) and the production assembly of both files assemble in Emerald mode
(`tools/asm_kits.py`). Save margin 28,896 B (unchanged), a/0/5/6 46.9 % used, a/0/0/3 83.9 % used.

---

## 7. Ch9 Mossdeep Space Center and the Mirage Tower: builders B5 + B6 (emerald_ch9_mirage, 2026-10-12)

**Built (Emerald only; Sapphire / Ruby assemble to the same bytes, checked file by file without a build: `work/agents/emerald_ch9_mirage/tools/same_sr.py`).**
- **Ids** (group Emerald): `VAR_MOSSDEEP_CITY_STATE`, `VAR_MOSSDEEP_SPACE_CENTER_STATE`, `VAR_MOSSDEEP_SPACE_CENTER_STAIR_GUARD_STATE`, `VAR_MIRAGE_TOWER_STATE`, the Space Center flags (`FLAG_DEFEATED_MAGMA_SPACE_CENTER`, `FLAG_INTERACTED_WITH_STEVEN_SPACE_CENTER`, `FLAG_DEFEATED_GRUNT_SPACE_CENTER_1F`, the `FLAG_HIDE_MOSSDEEP_CITY_*` set), the Mirage Tower's (`FLAG_FORCE_MIRAGE_TOWER_VISIBLE`, `FLAG_MIRAGE_TOWER_VISIBLE`, `FLAG_CHOSE_ROOT/CLAW_FOSSIL`, `FLAG_HIDE_MIRAGE_TOWER_ROOT/CLAW_FOSSIL`, `FLAG_HIDE_ROUTE_111_DESERT_FOSSIL`, `FLAG_HIDE_DESERT_UNDERPASS_FOSSIL`) and `FLAG_HIDE_SEAFLOOR_CAVERN_ENTRANCE_AQUA_GRUNT`; the new-game ones join `Sub_NewGameFlags` by themselves.
- **Gym win** (`0644` Emerald block): Magma moves in (state 1, three hide flags cleared, 1F Steven hidden, 2F Steven shown).
- **Mossdeep City** (`scenes/emerald/MossdeepCity_Magma.inc`, scripts 4-7): six trigger tiles (pokeemerald's coord events, state 1) start Maxie + four grunts walking off to the Space Center (pokeemerald's exact lists; state 2); Scott (+1 `VAR_SCOTT_STATE`); the Sailor and the Pokefan F (lines by `FLAG_RECEIVED_HM08` = pokeemerald's `FLAG_RECEIVED_HM_DIVE`). The King's Rock boy's after-line is Emerald's (`src/text/scenes/emerald/MossdeepCity.txt`).
- **Space Center 1F / 2F** (`src/field_scripts/emerald/0670 / 0671 / 0676 / 0677`, whole-file Emerald overlays of the shared rooms; their text `0547 / 0550`): every person with Emerald's lines and Magma branches, the three grunts that see you (Black 2's own trainer scripts), the stair guard (steps aside), the notice, Steven (1F, before the Gym), the 2F gauntlet (three grunts one after the other, "outnumbered" YES / NO), Steven's talk with Maxie, "Are you ready?" and **the tag battle** (`em_tag_battle TRAINER_STEVEN_PARTNER, TRAINER_MAXIE_MOSSDEEP, TRAINER_TABITHA_MOSSDEEP, L_SC2_ReadyPrompt`), the aftermath (Maxie gives up, everyone leaves, Steven thanks you and goes home: `VAR_STEVENS_HOUSE_STATE` 1). The zone inits move the civilians and the defeated grunts as pokeemerald's OnTransition. Not built: the rival's Rayquaza call 250 steps later (no step hook), the data pad's metatile.
- **Steven's house** (`0678 / 0679`, `#ifdef HOENN_EMERALD`): pokeemerald's numbering `VAR_STEVENS_HOUSE_STATE` 0 (not yet) / 1 (the Dive is due, set by the Space Center) / 2 (given); the Hall of Fame's Emerald block sets 2; a state 1 left after the Dive was received is just finished. Text `0551` (Emerald's lines).
- **Music**: `b2tools/patches/hoenn_music.c / .py` rule `EM_MAGMA_RULE`: zones 335 / 338 play `mus_encounter_magma` while `VAR_MOSSDEEP_CITY_STATE` is 1 or 2 (the TODO of EMERALD.md "EMERALD-3/4" rule 3).
- **Mirage Tower**: on Route 111 the tower's cells are Black 2 **map replace event 0** (work 0x4031 == 0x1220: no Hoenn script or Black 2 entry of a Hoenn matrix uses it; found free, `data/story_ids.json` engine `WORK_MAP_REPLACE_0_MIRAGE_TOWER`), alt layout `LAYOUT_ROUTE111_NO_MIRAGE_TOWER` = cell (8,3) (`data/emerald/hoenn_world.json`). `scenes/emerald/Route111_Mirage.inc`: the zone init rolls pokeemerald's `SetMirageTowerVisibility` (never once `VAR_MIRAGE_TOWER_STATE` is set, always after `FLAG_FORCE_MIRAGE_TOWER_VISIBLE` (the tower's 1F sets it, Route 112's zone init clears it), else 50 %), sets the event with reload and parks the door warp (`ObjInitWarpGPos`, zone 370 warp 6) while the tower is hidden. 4F (`0726`): the two fossils (take one: both hide flags, `FLAG_CHOSE_*`, a camera shake, state 1, warp to the tower's foot); Route 111's map-script condition at state 1 plays the collapse (camera shake, white flash and the plain-sand cells, the other fossil falls and sinks, state 2 -> 3 on the next entry, the Desert Underpass fossil shown, "The X Fossil disappeared into the sand..."); the **Desert Underpass** fossil (`0750`) gives the other one. Sapphire's two Route 111 surface fossils are `skip_emerald`.
- **Test chain** (`emerald_test_chain.inc` at 100): the Space Center won + the Dive from Steven.

**Left / for the lead.** The rival's Rayquaza call; the tower's colour pulse, the falling player sprite and the pixel disintegration (a shake + one flash instead); the Dynamic Punch tutor in Mossdeep and the Fossil Maniac hints (not asked); `emerald_ch10`'s Room 9 must set `VAR_STEVENS_HOUSE_STATE` **2** in Emerald (the shared line says 1; Steven's house copes: a 1 after the Dive just ends); the glitch checks of the new areas.

**Tested** (muted DeSmuME, Emerald test ROM `work/agents/emerald_ch9_mirage/rom_emerald/em9t.nds` SHA-1 0b10f397..., menu save margin 28,896 B unchanged; shots `screenshots/emerald_ch9_mirage/`, scripts `work/agents/emerald_ch9_mirage/tests/`): Magma walks off (state 1 -> 2); 1F with Magma inside (people moved, grunts, the stair guard fought and steps aside); 2F's three grunts (YES; one lost battle there whited out at home, no softlock); Steven's two talks, the one-menu pick and the tag battle won (Tyranitar + Steven's Aggron vs Camerupt / Mightyena, 9 turns), the aftermath (state 3, Steven home, Scott hidden); Steven's house Dive scene (HM06, state 2); Scott's exit; Route 111 with the tower shown (door leads into 1F) and hidden (plain sand, no door), the fossil taken on 4F, the collapse on Route 111 (state 2, the tower gone), the Desert Underpass fossil (the Claw Fossil after the Root Fossil). script_check on that ROM: open ent 8 / mapc 15 / path 121 (baseline 120; the +1 is Scott's east exit, which walks fine in game); scene_walks: no finding in the new scenes.
**Not played**: the forced loss of the tag battle (Steven's team carries a weak party, as pokeemerald; the loss path is `em_tag_battle`'s, tested by emerald_mech), the NO answers (the harness answered YES), the walk-in redraw trigger from Route 112's seam (the trigger of `e_ch9_mirage.json` / `R111_EmRedraw` is NOT in the data yet: add it only if the stale tower shows on a walk in from Route 112), the bike climb through 2F / 3F (started on 4F), the Sailor / Pokefan F lines, the Magma music (muted: the rule is in the ROM tables, not auditioned).

## 8. Ch10 Seafloor, Sootopolis crisis, Cave of Origin, Sky Pillar, Juan: builders B7a + B7b (emerald_ch10, 2026-10-12)
**Built (Emerald only; Sapphire / Ruby script bytes unchanged).** Room 9: Kyogre escapes with Emerald's text; the end sets
Emerald's flags (`VAR_SOOTOPOLIS_STATE` 1, the legends and leaders unhidden, `FLAG_SYS_WEATHER_CTRL`, `VAR_STEVENS_HOUSE_STATE` **2**,
pokeemerald's numbering). The crisis weather: `emerald_mech.c` `EM_ZoneWeather` + a per-frame tick (`EM_WeatherTickShim`)
switch Sapphire's rainstorm (6) and Ruby's drought (3) every 300 field frames (10 s) on the crisis zones, Sootopolis
downpours at state 1 / sky pillar 1; the crisis song on Routes 129-131 and Sootopolis' silence (Hoenn music option only,
`hoenn_music` `EM_ZONE_RULES`). Sootopolis (`scenes/emerald/SootopolisCity.inc`, 21 entries): door locks, spectators,
positions per state, the legends scene from the Center and from Dive (camera pans, point shakes), Steven's guide, the
Rayquaza scene (white warp), Maxie / Archie leave (Mt. Pyre state 2), Wallace gives HM Waterfall, the Gym opens.
Cave of Origin B1F Wallace and the Rayquaza multichoice; Sky Pillar Outside (Wallace opens the door, earthquake);
clean floors until `VAR_SKY_PILLAR_STATE` 2 (event 3: the cracked rooms after; clean 4F keeps Emerald's 5 falls), Top:
Rayquaza wakes, then the Lv 78 battle (flies off if you run). Juan (Rain Badge, TM03 Psyshock, the registered line).
Route 131's islet always there. Reusable helpers: `scenes/emerald/em_ch10_lib.inc` (camera, point shake, weather).
Test kit: `HOENN_TEST_CH10E` 2-10 (+ `_WEAK`) in `scenes/ch10_test.inc`.

**Tested** (muted DeSmuME, ROM from `work/agents/emerald_ch10/build2.sh` SHA-1 ede90726..., stage clones by `tools/qp.py`;
menu save margin **28,896 B** unchanged; shots `screenshots/emerald_ch10/`): Room 9 + Route 128, the weather cycle, both
legends scenes, Steven's guide, Cave of Origin Wallace, Sky Pillar Outside, the clean climb (4F fall to 3F, 5F, top),
Rayquaza waking, the Rayquaza scene, Maxie / Archie / Wallace / Waterfall / Gym door, the Rayquaza catch (Master Ball),
the cracked floors after, Juan win and loss (whiteout home). script_check: zone 108 only the fly-off path (Rayquaza
flies into the edge, harmless). scene_walks: SE_Steven findings come from guessed starts (the played guide walks right).

**Left / for the lead.**
- (Built since, emerald_ch10 resumed: the two layouts, below.) The top's camera point uses height 0, the ground is 32 (the
  view still frames Rayquaza).
- World rebuild: Sootopolis' generated signs are now scripts 22-25 (were 16-19); my world copy remaps them, the main
  `work/world_emerald` needs world.py rerun.
- At build time others' `data/story/emerald/e_ch12/e_ch13/e_ch9_mirage.json` broke the main-tree build (KeyError
  'MeteorFalls_StevensCave'); I built from a snapshot without them.
- ITCM is nearly full (~256 B after `rods`).
- Not reproduced: Emerald's full-screen specials of the legends' fight and Rayquaza's arrival; the spectators stand
  instead of Emerald's movement types; the camera shakes while panned are point shakes.

**The two layouts (emerald_ch10 resumed, 2026-10-12).** Both are `alt_layouts` of `data/emerald/hoenn_world.json` on map
replace **event 1**, now shared by three users that each set it on every zone entry (reload only when it changed):
Jagged Pass's mouth (on from `VAR_JAGGED_PASS_STATE` 2), Sootopolis' legends layout (`SE_EVENT`, states 1-4 and 5 before
Rayquaza's scene) and the clean Sky Pillar top (`SPT_EVENT`, `VAR_SKY_PILLAR_STATE` < 2). The last two are both "the crisis",
so the climb from a crisis Sootopolis loads the clean top with no reload. Sootopolis and the top are warp-only groups
(`world.py group_alts`): Sootopolis 3 cells, the top 4.
- `LAYOUT_SOOTOPOLIS_CITY_LEGENDS_BATTLE`: the lake as rough water (`METATILE_Sootopolis_RoughWater` 0x290 = MB_OCEAN_WATER) and
  its rough shores. New labels `data/labels/emerald/gTileset_Sootopolis.json` (each rough metatile takes the class of the tile it
  replaces); the look comes from the behaviour: `terrain/water.py` draws ocean water as sea (`sea_mizu1`, darker, two layers)
  where the calm lake (MB_POND_WATER) is a pond (`ike01`). Only the lake box may change height.
- `LAYOUT_SKY_PILLAR_TOP_CLEAN`: no cracked floor, Emerald's other rubble; `scenes/SkyPillar_Top.inc` `SPT_Init` sets the event.
- **For emerald_art (the full-screen cutscene, pokeemerald `src/rayquaza_scene.c`):** pokeemerald calls `special
  Script_DoRayquazaScene` only in `data/maps/SootopolisCity/scripts.inc`, four times: `_LegendariesSceneFromPokeCenter` and
  `_LegendariesSceneFromDive` (`VAR_0x8004` FALSE: Groudon and Kyogre's fight only, right after the fade to black and
  `setweather WEATHER_ABNORMAL`), `_RayquazaSceneFromPokeCenter` and `_RayquazaSceneFromDive` (`VAR_0x8004` TRUE: Rayquaza
  comes down, right after the fade, removing Groudon / Kyogre and adding Rayquaza). None in the Sky Pillar maps. In
  `src/field_scripts/scenes/emerald/SootopolisCity.inc` both branches share one place each: `SE_LegendsScene`'s `h_delay 90`
  after `em_weather_zone 1` (screen black) and `SE_RayquazaScene`'s `h_delay 90` after `h_playbgm_hoenn
  MUS_EM_RAYQUAZA_APPEARS` (screen black, Rayquaza added); replace those delays with the cutscene call.

