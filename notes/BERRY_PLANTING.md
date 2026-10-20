# Berry planting (Gen 3's berry trees) — `HOENN_BERRY_PLANTING=1`

User goal 2026-10-18: real berry planting as in Ruby, Sapphire and Emerald, in all three versions, instead of the daily
berry spots (notes/DECISIONS.md 2026-10-06 / 2026-10-08). Built behind a switch that is **off by default**: without
`HOENN_BERRY_PLANTING=1` every build is byte-identical to before (checked: section 8). The user turns it on after the
melonDS test (section 9).

Rules: pokeemerald / pokeruby `src/berry.c` (the same rules and numbers in both: checked), `data/scripts/berry_tree.inc`
(S_BerryTree / BerryTreeScript), `data/scripts/new_game.inc` (EventScript_ResetAllBerryTrees), `gBerryTrees` = the
berry tree objects of `data/maps/*/map.json`.

## 1. What the player gets

- **88 trees per version** at their Gen 3 spots: Gen 3's tree ids 1-89 (pokeruby has no 57). Sapphire/Ruby from
  pokeruby, Emerald from pokeemerald (only difference: Emerald's three Route 115 trees stand one tile east,
  (12-14, 5) instead of (11-13, 5)).
- **A new game (and an old save, section 4)** starts as Gen 3's new game: the 80 trees Gen 3 plants carry their berries
  fully grown (BERRY_STAGE_BERRIES, Gen 3's yield of an unwatered tree), the 8 others are soft soil. A tree waits, fully
  grown, until the player has seen it (Gen 3's `stopGrowth` + SetBerryTreesSeen): here, until its actor is made (the
  player enters its zone) or it is talked to.
- **Talking to a tree** (Gen 3's script, Sapphire's lines):
  - soil: "It's soft, loamy soil." / with a Gen 3 berry in the Bag: "...Want to plant a Berry?" -> the Bag opens on the
    Berries pocket -> "<player> planted one Oran Berry in the soft, loamy soil." (the berry leaves the Bag);
  - planted / sprouted / taller / flowering: "One Oran Berry was planted here." / "Oran Berry has sprouted." / "This Oran
    Berry plant is growing taller." / "These Oran Berry flowers are blooming cutely/prettily/very beautifully." (by the
    times watered: 0 cutely, 4 very beautifully, else prettily), then with the Wailmer Pail: "Want to water the Oran Berry
    with the Wailmer Pail?" -> "<player> watered the Oran Berry." "The plant seems to be delighted.";
  - berries: "There are 3 Oran Berries! Do you want to pick the Oran Berries?" -> the berry fanfare, "...put away the Oran
    Berries in the Bag's Berries Pocket. The soil returned to its soft and loamy state." (the tree is soil again);
    "The Bag's Berries Pocket is full..." / "...left the Oran Berries unpicked." as in Gen 3.
- **Growth** (pokeemerald BerryTreeTimeUpdate / BerryTreeGrow / CalcBerryYield): each stage lasts the berry's
  stageDuration hours (Cheri, Pecha, Oran... 3 h; Leppa 4 h; Razz, Bluk, Nanab, Wepear, Pinap 1 h; Lum 12 h; Spelon to
  Belue 18 h; Liechi to Enigma 24 h): planted -> sprouted -> taller -> flowering -> berries. Berries stay 4 stage
  lengths, then fall: the tree goes back to sprouted (watering cleared) and grows again; the tenth time it is gone (soil).
  Yield = minYield unwatered, up to maxYield watered at all four stages (Gen 3's random rounding). A clock jump of 71
  stage lengths or more kills a growing tree (Gen 3). Watering counts once per stage (planted, sprouted, taller,
  flowering).
- **The Wailmer Pail**: already given by the Pretty Petal flower shop lady on Route 104 (Gen 3's giver in all three
  versions; `src/field_scripts/1010_room_Route104_PrettyPetalFlowerShop.s`, FLAG_RECEIVED_WAILMER_PAIL), the key item
  Black 2's Sprayduck renamed (data/hoenn_key_items.json: ITEM_WAILMER_PAIL -> ITEM_SPRAYDUCK 448).
- **Berries**: Gen 3's 43 berries are Black 2's items 149-183 (Cheri-Belue) and 201-208 (Liechi-Enigma), the same
  items (data/hoenn_items.json maps nothing for them: same names). Gen 4's berries (Occa-Chilan 184-200, Micle-Rowap
  209-212) have no Gen 3 tree: the Bag lets the player pick them (Black 2's Bag lists every pocket), the script then
  says "The Occa Berry can't be planted here." and keeps it. The Enigma Berry grows as Gen 3's Enigma (24 h stages, the
  Durin tree picture; no e-Reader data).

## 2. Save storage (the hard part 1)

**Black 2's save block 0x47 (Pokéstar Studios, 996 bytes)** holds the trees. Why there:
- Free works/flags: far too few. 88 trees x 6 bytes = 528 bytes = 264 works; the daily spots already used six spare
  works. The flags are all claimed by the story (data/story_ids.json).
- Padding of a block (the Frontier's way in Emerald, notes/SAVE_PKHEX.md): the game neither writes nor checks padding
  without save_compat-style hooks, and it breaks PKHeX's checks unless done with an own CRC. Not needed here.
- A whole Black 2 block nobody uses in Hoenn: its bytes are inside the block's size, so Black 2 saves, loads, compares
  and CRC-checks them itself, the save's CRC table and PKHeX's checks stay valid (the block keeps Black 2's size), and
  no layout moves. Candidates (sizes from the arm9 save table 0x0208F160; users found by scanning every module for
  `SaveControl_GetBlockPtr(save, id)` and the blocks' accessors, `work/agents/berries/tools/callers.py`):

  | block | Black 2 use | size | users | verdict |
  |---|---|---|---|---|
  | 0x47 | Pokéstar Studios progress (func_02011040, pokewood.h) | 996 | ov062 PokewoodCmd (the studios' scripts), ov023 / ov136 / ov324 (the movie shoot, its cast, msg 313/329), ov012 func_ov012_02169b78 (a read for a progress count) | **used**: only the studios write it; no Hoenn zone is the studios |
  | 0x43 | Join Avenue | 5800 | visitors arrive from passers-by | no (written outside its place) |
  | 0x3d | Passerby survey | 644 | updated by tag-log contacts | no |
  | 0x44 | Medal Box | 1174 | medals can be awarded anywhere | no |
  | 0x40 / 0x41 / 0x42 / 0x45 / 0x46 / 0x48 | various | 128-364 | — | too small (6-byte Gen 3 records) |

  Hoenn has no Pokéstar Studios (Virbank is gone; no Hoenn map warps there). What the block held (movie flags, best
  results, fame) is Black 2 data nothing in Hoenn shows.
- Layout (berries.c): `+0 u32 magic "BRY3"`, `+4 u32 the clock of the last growth update` (minutes since 2000),
  `+8 u8 the version that set it up`, `+12 BerryTree[128]` = Gen 3's own struct (6 bytes: berry, stage | stopGrowth << 7,
  u16 minutes until the next stage, yield, regrowth count | watered bits << 4), indexed by Gen 3's tree id. 780 bytes.
- PKHeX: opens the save as before (the block's CRC is Black 2's own and correct). PKHeX has no Pokéstar editor, so
  nothing shows or edits the trees there.

## 3. Existing saves (no migration step)

A save made before this update has Black 2's Pokéstar data in block 0x47, not the magic. The first time the code needs
the trees (a tree zone, a tree's script) it sets them up as **Gen 3's new game**: every Gen 3 starting tree fully grown
with its berries, the soil spots empty, waiting until seen. The choice between "every tree fully grown as now" and
"Gen 3's starting trees" disappears: they are the same set (the 80 daily spots are exactly the 80 trees Gen 3's new
game plants, with the same berries). Today's "picked today" bits (VAR_BERRY_PICKED_*) are not carried over: such a
tree is back with berries, a one-time gift, and the old daily system's works and flags are simply no longer used.
The set-up is written with the next in-game save. A save made with berry planting and loaded in a build without it:
the daily spots work as before (their works/flags are untouched); block 0x47 is Pokéstar's again for Black 2 (unused).

## 4. Time (the hard part 2)

Gen 3 (pokeemerald clock.c UpdatePerMinute): `minutes = local time - lastBerryTreeUpdate`; if > 0 the trees grow by it
and the time is stored; if < 0 nothing happens and the stored time stays.
Here the clock is the DS's real-time clock as Black 2 reads it (gfl rtc_cache: RTC_GetCachedDateTime 0x02044210,
NitroSDK RTC_ConvertDateToDay 0x0207d0b4): minutes since 2000-01-01, as Gen 4/5 do. The update runs whenever the code
touches the trees: each tree actor being made (zone entry), each tree script, and the tree zones' inits (global
8297/8298, which ran the daily reset before). Gen 3 also updated every ~68 s while walking; here a tree's picture
changes when its actor is made again (zone entry) or when it is talked to (the script refreshes it first).
**Clock changes**:
- forward (melonDS's Date and time, a DS's settings): the trees grow by the jump, as a Gen 3 cartridge whose clock was
  reset forward, and as Gen 4/5's berries; a jump of 71 stage lengths kills growing trees (Gen 3).
- backward: nothing grows and the stored time stays, so the trees wait until the clock passes it again (Gen 3's rule).
  Moving the clock back and forth therefore gives nothing beyond the forward moves: no exploit beyond Gen 3's.
- Black 2's own "clock changed" penalty (24 h without daily events after a change in the DS settings) does not stop
  the trees (Gen 4's berries ignored it too).
- No crash: the difference is a signed 32-bit number of minutes (2000-2099 fits), a clock that is not read yet (month 0)
  is skipped, Gen 3's loop ends after at most 71 stages per tree.

## 5. Visuals (the hard part 3)

- Pictures: `b2tools/berry_planting_art.py` -> `src/sprites/berry_planting/` (93 folders + pictures.json; review sheet
  `screenshots/berry_planting/review.png`). Sapphire's own pixels 1:1 from the decomp graphics (the same way
  models_objects.py made the daily trees): `pics/berry_trees/dirt_pile.png` (planted), `sprout.png` frame 0
  (sprouted), `<tree>.png` frames 0 / 2 / 4 (taller / flowering / berries: the first frame of each of Gen 3's sway
  animations; the berries frame is the one the daily trees show), each in its stage's OBJ palette
  (gBerryTreePaletteSlotTablePointers, slot k = palette k - 2). pokeemerald's tables, pictures and palettes are
  identical to pokeruby's (checked by the generator), so one set serves the three versions. 30 tree pictures x 3
  stages + the dirt pile + the sprout = 92 pictures, + a blank one.
- **Soft soil**: Gen 3 draws no sprite for an empty tree (SetBerryTreeGraphics: stage 0 = invisible object); the soil
  is the map's own metatile. Here the world already draws Sapphire's soil tiles as the berry soil decal (Accumula's tree
  pit, b2tools/terrain/ground.py `other:berry_soil`) on every tree tile, and makes them solid; the tree actor shows the
  blank picture there (talkable, solid, nothing drawn). The planted stage is Gen 3's dirt pile sprite.
- Black 2: one-frame 32x32 billboards (controller 4, Black 2's own kind for small objects), the Gen 3 frame bottom-
  aligned and centred as the daily trees. Each picture = its own object code (0x0E00 + i) = a record appended to
  a/0/4/7 + a sheet appended to a/0/4/8 (patches/berries.py apply; arm9 GetIndexOfObjID learns the range).
- Which picture: every tree actor's object code is `0x0F00 + tree id`; Black 2 resolves an actor's code when the actor
  is made (ov012 GetWKOBJCODENPCOBJCODE, which already turns codes 162-177 into works' values). berries.c hooks it and
  returns the picture of the tree's berry and stage. After planting / picking (and when a tree grew while the player
  stood there) the script deletes and re-adds the actor (ActorDelete / ActorAdd by uid), which resolves it again.
- **Budget** (notes/NPC_LIMIT.md): one picture = one material (of 32) and 544 B of texture VRAM while shown; at worst
  every tree of a zone shows another picture. npc_check counts the tree codes that way (BERRY_TREES); fullest: Route 123
  (18 trees): 8 other codes + 18 + 2 player = 28/32; Route 120 26, Route 104 27, Route 111 25. Emerald's Route 123
  has 13 other codes (its Emerald-only trainers): 33, so Emerald's cache is 40 (notes/NPC_LIMIT.md "Emerald Route
  123": with 18 different pictures the player's Surf sprite had found no entry). VRAM goes down
  compared with the daily trees (one-frame sheets instead of 12-frame ones). Field heap: unchanged (sheets live in VRAM,
  the code in ITCM; nothing loads into the field heap).
- Left out: Gen 3's sway animations (the daily trees were still too), the sparkle when a stage changes, the watering
  animation (Black 2 has no such player pose).

## 6. Scripts and code (the hard parts 4-5)

- Script: `src/field_scripts/common/berry_planting.inc` (+ `_defs.inc`), included in file 1241 (`1241_hidden_items.s`,
  generated by converter/gen_hidden_items.py) under `#ifdef HOENN_BERRY_PLANTING`: Script_300 = global 8299, every
  tree's script. The tree zones' init entries (global 8297 / 8298, Script_298 / 299) run `BerryCmd BT_OP_UPDATE`
  instead of the daily reset. Lines: script text 208, 34-45 (`src/text/berries/overrides_berry_planting.json`).
- Choosing a berry: Black 2's script command CallBag (334) with mode 1 = the bag mode of Black 2's gourmet item
  collector (file 1270: the Bag returns the picked item to the script), wrapped as Black 2 does (fade, FieldClose,
  CallBag, FieldOpen, fade); in that mode A on an item closes the Bag and returns it (self-test). Before it, berries.c
  sets the Bag cursor's last pocket (u16 +24, func_020088a4; the Bag keeps its last pocket there) to Berries.
- Specials: script command 612 (Black 2's HollowRivalCmd_0264, used by no Black 2 or Hoenn script; permission 7)
  -> `Berry_Cmd`: `BerryCmd op, arg` with op GET / PLANT / WATER / PICK / HAS_BERRIES / BAG_POCKET / UPDATE, results in
  the local works 0x8004-0x800d (Gen 3's VAR_0x8004-6 meanings). The tree is the one standing on the talked-to actor's
  tile (kTreeX/kTreeZ, the trees' world tiles); OP_GET keeps it in 0x800d and the actor's uid in 0x8009 for the later
  ops and the refresh (across the Bag's FieldClose/FieldOpen). Why not the uid: Black 2's actor save keeps a uid in
  8 bits, so after Continue an actor made with uid 403 comes back as 147 (self-test). The tree actors' uids are
  250 - their index on the map (233-250, free in every tree zone; < 256 so ActorDelete/ActorAdd find them after
  Continue too).
- Code: `b2tools/patches/berries.c` (2,996 B, ITCM after the other patches' code), `berries.py` (records, sheets,
  tables, hooks; all checked against Black 2's bytes). Data tables per version in berries_data.h: gBerries'
  stageDuration/maxYield/minYield, the picture of each berry's stages, the new-game berry of each tree
  (data/hoenn_berry_trees.json, Emerald data/emerald/hoenn_berry_trees.json).
- Objects: `data/story/berries/berry_trees.json` (Emerald `data/story/berries/emerald/`): 88 actors, uid 250 - index on
  the map, code 0x0F00 + tree id, script 8299; patches/story.py places them instead of data/story/berry_spots.json when the
  switch is on. Mirage Island's Liechi tree keeps its hide flag (FLAG_BERRY_TREE_PICKED_73): scenes/Route130.inc hides
  it while the island is away and (with the switch) shows it whenever the island is there.

## 7. Files

New: b2tools/berry_planting_art.py, b2tools/patches/berries.py, b2tools/patches/berries.c,
src/field_scripts/common/berry_planting.inc, berry_planting_defs.inc, src/sprites/berry_planting/ (93 pictures),
src/text/berries/overrides_berry_planting.json, data/hoenn_berry_trees.json, data/emerald/hoenn_berry_trees.json,
data/story/berries/berry_trees.json, data/story/berries/emerald/berry_trees.json, screenshots/berry_planting/review.png,
this file; work/agents/berries/ (build_test_rom.sh, make_patch.sh, tools/).
Changed (switch-guarded): converter/gen_hidden_items.py (+ the regenerated 1241_hidden_items.s, Sapphire's and
Emerald's), b2tools/build_rom.py (appends `berries`), b2tools/patches/scripts.py (-D HOENN_BERRY_PLANTING),
text.py (the lines), story.py (the objects), src/field_scripts/scenes/Route130.inc (Mirage), b2tools/npc_check.py
(tree codes), b2tools/script_check.py (tree uids, the soil-tile acceptance).
Release branch: `b2tools/release_kit/next/berries.patch` (applies to sapphire-ruby; `work/agents/berries/make_patch.sh`
remakes it).

## 8. Checks

- Default builds byte-identical: file 1241 (Sapphire's) and 0480 (Route 130) assemble to the same bytes as git HEAD's
  without the switch; text.py / story.py / scripts.py / build_rom.py change nothing without it; npc_check / script_check
  only report.
- berries.c compiles and links for Sapphire/Ruby (pokeruby tables) and Emerald (pokeemerald tables): 2,996 B.
  ITCM: Sapphire/Ruby had 14,976 B left -> about 11.9 KB after; Emerald 6,272 B -> about 3.2 KB.
- Every tree tile (work/agents/berries/tools/soil_check.py, Sapphire on the lead's work/world_rel, Emerald on
  work/world_emerald): 87 of 88 trees on the world's solid soil class with a walkable neighbour; the 88th is Mirage
  Island's (the main world is sea there, the island's layout has the land: story.py's alt_land height, as the daily tree).
  outdoor_check / rooms_check: nothing to re-check (no world or room changes).
- The test ROM (2026-10-18, sapphire-ruby c101c56 + berries.patch, sha1 302972be...): patch berries: 93 pictures =
  records 1008-1100, sheets 1042-1134 (after sprite_switch's), 2348 B of ITCM at 0x1ffc580 (12,608 B left); npc_check
  367 zones, 0 over a limit, fullest Route123 28/32, Route104 27/32, Route120 26/32 materials; script_check on the 16 tree
  zones: 0 open findings (the trees' solid soil tiles accepted); the menu save keeps 28,768 B of field heap (pack 0
  unchanged).

## 8b. Self-test (DeSmuME, muted; 2026-10-18, test ROM sha1 17b2fe91...) — PASS

`work/agents/berries/tests/run_selftest.sh` (driver bt.py on the freeze_fix/surf_under2 harness): cold boot, new game,
the sign's kit, then every step below with in-game saves and cold boots; the DS clock set per run through TZ
(BT_AT, DeSmuME reads the host's local time). Log `work/agents/berries/tests/selftest.log`, screenshots
`screenshots/berry_planting/selftest/` (stages.png: the column through every stage).
1. Sign -> Route 104 (52,262); tree actors: soil = blank code 0xE00, the Oran tree 0xE17, the Cheri tree 0xE05.
2. Soil: "Want to plant a Berry?" YES -> the Bag on the Berries pocket (Cheri selected) -> Razz, A -> "planted one Razz
   Berry": the dirt pile (0xE01), Razz 5 -> 4; watered (bit 1).
3. The Oran tree: "There are 2 Oran Berries!" (Gen 3's unwatered new-game yield) -> picked, soil again (blank);
   replanted with a Bluk (5 -> 4).
4. Occa: "The Occa Berry can't be planted here.", the soil stays, Occa 1 -> 1.
5. In-game save, then cold boot + Continue at +1 h: both sprouted; +2 h: taller; clock set back 22 min: nothing grows,
   the last update stays; +3 h: flowering ("blooming cutely" unwatered Bluk, "prettily"/"very beautifully" for the
   Razz by its waterings); +4 h: berries: Bluk 3 (unwatered = minYield 3), Razz 6 (watered at all four stages: 5-6);
   the Bluk picked (4 -> 7), the Razz "left ... unpicked".
6. Cold boot + Continue: the Razz still has its 6 berries, the Bluk's spot is soil; picked (4 -> 10). The battery
   file: PKHeX's B2W2 checks pass (all 73 blocks), both copies pass Black 2's load check, block 0x47 holds the trees.
Found and fixed by the self-test: the Bag opened on ITEMS (the cursor's last pocket is u16 +24, not +26); the
refusal line named "None" (the tree's item had replaced the Bag's choice); after Continue the tree script found no
tree (Black 2's actor save keeps uids in 8 bits: 403 came back as 147) -> trees found by tile, uids 233-250.

## 9. User test (melonDS, sound muted)

Build: `zsh work/agents/berries/build_test_rom.sh` (needs 1.5 GB free) -> `~/Desktop/Sapphire_BERRIES_TEST.nds`.
New game; in Littleroot read the town sign: a Lv 100 Groudon, the Wailmer Pail, berries (Cheri, Oran, Pecha 5 each;
Razz, Bluk, Nanab, Wepear, Pinap 5 each: one-hour stages; one Occa Berry, which cannot be planted), and a warp to
Route 104 next to the flower shop: four soil tiles in a column on your left (Route 104 (3,22)-(3,25)).
1. Press Left: soil. "Want to plant a Berry?" Yes -> the Bag (Berries pocket) -> pick a Razz Berry -> "planted one Razz
   Berry": a dirt pile appears. Talk again: "One Razz Berry was planted here." + "Want to water...?" Yes.
2. Walk down: the Oran tree (fully grown, Gen 3's start): pick it -> fanfare, soil again; plant something there.
   Try the Occa Berry once: "can't be planted", it stays in the Bag.
3. Save in game. melonDS: System -> Stop; Config -> Date and time: set the clock **1 hour later**; start, Continue,
   talk to the Razz tree (the script shows the new picture first) or go into the flower shop and out again: a sprout.
   +1 h: taller; +1 h: flowering ("blooming ..." by your watering); +1 h: berries (Razz: 3 unwatered, up to 6 watered
   at all four stages). (After Continue, Black 2 restores the field's people as saved, so a tree that grew while the
   game was off shows its old picture until it is talked to or the zone is entered again.)
4. Setting the clock back makes the trees wait until that time comes again (Gen 3's rule): only move it forward.
5. Optional: a save made with v17 before this test ROM (copy, never move): every tree has berries, the soil spots are
   empty.

## On by default (2026-10-18)
The self-test passed (section 8b), and the lead switched berry planting on by default (the user's rule: a passing self-test
is enough). HOENN_BERRY_PLANTING=0 builds the old daily trees.
