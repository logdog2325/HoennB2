# Sapphire story split for parallel chapter agents

Regenerated 2026-10-06 (second version, after the first copy in /private/tmp was lost) from pokeruby (`external/pokeruby/data/maps/*/scripts.inc`, `data/scripts/*.inc`, `data/event_scripts.s`, `map.json`) against the current build data: outdoor maps = `data/hoenn_zones.json` zones present in `work/world/world.json`; standalone outdoor maps = `data/hoenn_standalone.json` (groups defined, `"build"` list empty = not in the main build; the standalone agent's test ROM has all 15, proofs in `work/agents/standalone/proofs/`); rooms = `data/hoenn_interiors.json` + `data/interiors/<zone>.json` (hand/auto/center/b2/big-with-file = built; cave with a room file = built by `converter/gen_caves.py` (commit bb4ec6e: Granite Cave x4, Rusturf Tunnel, Fiery Path); cave without file = not built; link = left out). Story ids: `data/story_ids.json` / `src/include/hoenn.h` (Black 2 id shown next to every name below).

Status words: **built**; **in progress** (exists in an agent's build but not in the main build yet: counts as not blocking); **NOT BUILT** (blocks).

Conventions
- **Owner**: every Sapphire map file has exactly one owning chapter, which ports the whole `scripts.inc` (story beats, NPCs, trainers, signs). Beats of another chapter that live in that file are **foreign beats**: the beat's chapter writes them as `src/field_scripts/scenes/<map>.inc`-style includes (as `scenes/Route103.inc` does) and the owner reserves ScriptEntry slots / includes them.
- **Lines** = non-blank script lines of the labels assigned to the chapter (owned files minus foreign ranges plus the chapter's own foreign ranges; labels of shared files by file, by hand-routing or by map-name prefix). Text lines (`text.inc` of owned maps) are listed separately.
- **Trainers** = `trainerbattle*` commands (single/double/no_intro/rematch/rematch_double/raw) in those labels; "unique" = distinct TRAINER_ constants. `.ifdef SAPPHIRE` blocks are counted with their Ruby twins (Mt. Chimney, Mt. Pyre summit double).
- Flags/vars exclude temporaries (FLAG_TEMP_*, VAR_TEMP_*, VAR_0x80xx, VAR_RESULT, VAR_FACING, VAR_LAST_TALKED, VAR_OBJ_GFX_ID_*). `(C)` = pokeruby's C engine also uses it. `[id]` = its Black 2 id in data/story_ids.json (`0x40xx` work, decimal flag, `engine` = badge/system equivalent per story_ids.json "engine", `item ball` = converter/gen_items.py flag 1100+n).
- Link rooms (Center 2F -> Trade Center/Colosseums/Record Corner, contest lobbies -> LinkContestRoom*) are left out of the map tables; see S_optional.
- `removeobject`/`addobject` also set/clear an object's hide flag; those writes are not counted as "set" (they show up as the map's object flags).

## 1. Chapters at a glance

| Ch | Story | Badge | State | Blocking maps (NOT BUILT, main path) | In progress (main path) | Script lines | Trainers (cmds/unique) | Flags | Vars |
|---|---|---|---|---|---|---|---|---|---|
| Ch0 | Opening (DONE): truck, Littleroot, Route 101 rescue, starter | - | **DONE** | - | - | 1707 | 0/0 | 49 | 11 |
| Ch1 | Rival on Route 103, Pokedex, Petalburg (Norman, Wally), Petalburg Woods, Rustboro: Roxanne | Stone Badge (1) | **UNBLOCKED** | - | PetalburgWoods | 3573 | 37/26 | 73 | 13 |
| Ch2 | Devon Goods (Route 116, Rusturf Tunnel), Mr. Stone, Mr. Briney, Dewford: Brawly, Granite Cave: Steven | Knuckle Badge (2) | **UNBLOCKED** | - | - | 3333 | 35/29 | 82 | 9 |
| Ch3 | Slateport (museum, Capt. Stern), Route 110 rival, Mauville: Wattson, Verdanturf, Rusturf reunion | Dynamo Badge (3) | **UNBLOCKED** | - | - | 7228 | 63/52 | 109 | 29 |
| Ch4 | Route 111-115, Fiery Path, Fallarbor, Meteor Falls (Prof. Cozmo, Meteorite) | - | **BLOCKED** | MeteorFalls_1F_1R | - | 2322 | 62/42 | 77 | 9 |
| Ch5 | Cable car, Mt. Chimney (Aqua vs Magma), Jagged Pass, Lavaridge: Flannery | Heat Badge (4) | **UNBLOCKED** | - | MtChimney, JaggedPass | 1200 | 22/16 | 23 | 4 |
| Ch6 | Norman, Surf, and the Surf side areas (Routes 105-108, Abandoned Ship, New Mauville) | Balance Badge (5) | **UNBLOCKED** | - | - | 1489 | 30/25 | 51 | 3 |
| Ch7 | Route 118-120, Weather Institute, Fortree: Winona (Kecleon, Devon Scope) | Feather Badge (6) | **UNBLOCKED** | - | - | 1667 | 61/51 | 67 | 4 |
| Ch8 | Route 121-123, Lilycove (rival), Mt. Pyre (orb stolen), Slateport sub theft, Aqua Hideout | - | **UNBLOCKED** | - | MtPyre_Exterior, MtPyre_Summit, AquaHideout_1F, AquaHideout_B1F, AquaHideout_B2F | 4733 | 46/35 | 109 | 13 |
| Ch9 | Route 124-127, Mossdeep: Tate & Liza, Steven gives Dive, Shoal Cave | Mind Badge (7) | **UNBLOCKED** | - | - | 1592 | 36/30 | 50 | 2 |
| Ch10 | Seafloor Cavern (Kyogre awakens), Route 128, Sootopolis, Cave of Origin (Kyogre), Wallace | Rain Badge (8) | **BLOCKED** | Underwater4, Underwater_SeafloorCavern, SeafloorCavern_Entrance, SeafloorCavern_Room1, SeafloorCavern_Room2, SeafloorCavern_Room3, SeafloorCavern_Room4, SeafloorCavern_Room5, SeafloorCavern_Room6, SeafloorCavern_Room7, SeafloorCavern_Room8, SeafloorCavern_Room9, Underwater2, Underwater_SootopolisCity, CaveOfOrigin_Entrance, CaveOfOrigin_1F, CaveOfOrigin_B1F, CaveOfOrigin_B2F, CaveOfOrigin_B3F, CaveOfOrigin_B4F | SootopolisCity | 1814 | 22/19 | 59 | 7 |
| Ch11 | Ever Grande, Victory Road (Wally), Elite Four, Champion Steven, Hall of Fame | - | **BLOCKED** | VictoryRoad_1F, VictoryRoad_B1F, VictoryRoad_B2F, EverGrandeCity_HallOfFame | - | 926 | 18/17 | 34 | 3 |
| Ch12 | Southern seas (optional, pre-League): Routes 129-134, Pacifidlog; Regi puzzle | - | **UNBLOCKED** | - | - | 822 | 26/25 | 20 | 0 |
| Ch13 | Post-game (optional): S.S. Ticket, S.S. Tidal, Battle Tower, Southern Island, Sky Pillar (Rayquaza), Beldum | - | **BLOCKED (optional chapter)** | BattleTower_Corridor, BattleTower_Elevator, SSTidalCorridor, SSTidalLowerDeck, SSTidalRooms, SkyPillar_1F, SkyPillar_2F, SkyPillar_3F, SkyPillar_4F, SkyPillar_5F, SkyPillar_Entrance | BattleTower_Outside, SkyPillar_Outside, SkyPillar_Top, SouthernIsland_Exterior, SouthernIsland_Interior | 1701 | 9/8 | 30 | 5 |
| S_common | Common scripts every chapter calls (lead, before the chapters start) | - | - | - | - | 1923 | 0 | 15 | 1 |
| S_optional | Optional systems (decide per system; Black 2 has no equivalent for most) | - | - | - | - | 2619 | 0 | 26 | 6 |
| S_debug | Debug menu scripts (not ported; ignored for setters/readers) | - | - | - | - | 511 | 0 | 3 | 1 |
| S_unused | Unused / other version | - | - | - | - | 103 | 6 | 13 | 0 |

Total parsed script lines: 39263 (maps 30626, shared files 8770); trainerbattle commands in map scripts: 453.

Suggested agents: Ch6+Ch12 together (small); Ch3 as 3a/3b(+3T); Ch8 as 8a/8b; one agent per other chapter. Chapters waiting only for "in progress" maps can start now and test those maps in the standalone agent's build (HOENN_STANDALONE).

### Maps that block a main path (NOT BUILT), in story order

- **Ch4**: MeteorFalls_1F_1R (NOT BUILT (cave; zone 128 allocated, no room file))
- **Ch10**: Underwater4 (NOT BUILT (in no zone list)); Underwater_SeafloorCavern (NOT BUILT (in no zone list)); SeafloorCavern_Entrance (NOT BUILT (in no zone list)); SeafloorCavern_Room1 (NOT BUILT (in no zone list)); SeafloorCavern_Room2 (NOT BUILT (in no zone list)); SeafloorCavern_Room3 (NOT BUILT (in no zone list)); SeafloorCavern_Room4 (NOT BUILT (in no zone list)); SeafloorCavern_Room5 (NOT BUILT (in no zone list)); SeafloorCavern_Room6 (NOT BUILT (in no zone list)); SeafloorCavern_Room7 (NOT BUILT (in no zone list)); SeafloorCavern_Room8 (NOT BUILT (in no zone list)); SeafloorCavern_Room9 (NOT BUILT (in no zone list)); Underwater2 (NOT BUILT (in no zone list)); Underwater_SootopolisCity (NOT BUILT (in no zone list)); CaveOfOrigin_Entrance (NOT BUILT (cave; zone 110 allocated, no room file)); CaveOfOrigin_1F (NOT BUILT (cave; zone 95 allocated, no room file)); CaveOfOrigin_B1F (NOT BUILT (cave; zone 100 allocated, no room file)); CaveOfOrigin_B2F (NOT BUILT (cave; zone 101 allocated, no room file)); CaveOfOrigin_B3F (NOT BUILT (cave; zone 102 allocated, no room file)); CaveOfOrigin_B4F (NOT BUILT (cave; zone 103 allocated, no room file))
- **Ch11**: VictoryRoad_1F (NOT BUILT (cave; zone 170 allocated, no room file)); VictoryRoad_B1F (NOT BUILT (cave; zone 171 allocated, no room file)); VictoryRoad_B2F (NOT BUILT (cave; zone 172 allocated, no room file)); EverGrandeCity_HallOfFame (NOT BUILT (status link = left out; zone 57))
- **Ch13**: BattleTower_Corridor (NOT BUILT (in no zone list)); BattleTower_Elevator (NOT BUILT (in no zone list)); SSTidalCorridor (NOT BUILT (in no zone list)); SSTidalLowerDeck (NOT BUILT (in no zone list)); SSTidalRooms (NOT BUILT (in no zone list)); SkyPillar_1F (NOT BUILT (cave; zone 164 allocated, no room file)); SkyPillar_2F (NOT BUILT (cave; zone 165 allocated, no room file)); SkyPillar_3F (NOT BUILT (cave; zone 166 allocated, no room file)); SkyPillar_4F (NOT BUILT (cave; zone 167 allocated, no room file)); SkyPillar_5F (NOT BUILT (cave; zone 168 allocated, no room file)); SkyPillar_Entrance (NOT BUILT (cave; zone 169 allocated, no room file))

### Main-path maps in progress (not blocking, but not in the main build yet)

- **Ch1**: PetalburgWoods
- **Ch5**: MtChimney, JaggedPass
- **Ch8**: MtPyre_Exterior, MtPyre_Summit, AquaHideout_1F, AquaHideout_B1F, AquaHideout_B2F
- **Ch10**: SootopolisCity
- **Ch13**: BattleTower_Outside, SkyPillar_Outside, SkyPillar_Top, SouthernIsland_Exterior, SouthernIsland_Interior

Maps in no zone list at all: AbandonedShip_HiddenFloorCorridors, AbandonedShip_HiddenFloorRooms, AbandonedShip_Underwater1, AbandonedShip_Underwater2, BattleTower_Corridor, BattleTower_Elevator, Route110_TrickHousePuzzle2, Route110_TrickHousePuzzle3, Route110_TrickHousePuzzle4, Route110_TrickHousePuzzle5, Route110_TrickHousePuzzle6, Route110_TrickHousePuzzle7, Route110_TrickHousePuzzle8, SSTidalCorridor, SSTidalLowerDeck, SSTidalRooms, SeafloorCavern_Entrance, SeafloorCavern_Room1, SeafloorCavern_Room2, SeafloorCavern_Room3, SeafloorCavern_Room4, SeafloorCavern_Room5, SeafloorCavern_Room6, SeafloorCavern_Room7, SeafloorCavern_Room8, SeafloorCavern_Room9, SealedChamber_InnerRoom, SealedChamber_OuterRoom, ShoalCave_HighTideEntranceRoom, ShoalCave_HighTideInnerRoom, Underwater1, Underwater2, Underwater3, Underwater4, Underwater_Route134, Underwater_SeafloorCavern, Underwater_SealedChamber, Underwater_SootopolisCity

## 2. Cross-chapter dependencies (flags/vars written in one chapter, read in another)

| id | Black 2 id | written in | read in |
|---|---|---|---|
| FLAG_ADVENTURE_STARTED | 134 | Ch1 | Ch0 |
| FLAG_SYS_POKEDEX_GET (C) | 2070 | Ch1 | Ch3 |
| FLAG_RESCUED_BIRCH | 110 | Ch0 | - |
| FLAG_DEFEATED_RIVAL_ROUTE103 | 135 | Ch1 | Ch0 |
| VAR_BIRCH_LAB_STATE | 0x4051 | Ch0, Ch1 | - |
| VAR_LITTLEROOT_STATE | 0x4054 | Ch0, Ch1 | - |
| VAR_LITTLEROOT_HOUSES_STATE | 0x404F | Ch0, Ch13 | - |
| VAR_LITTLEROOT_HOUSES_STATE_2 | 0x4050 | Ch0, Ch13 | - |
| VAR_LITTLEROOT_RIVAL_STATE | 0x4053 | Ch0, Ch1 | - |
| VAR_OLDALE_STATE | 0x4058 | Ch1 | Ch0 |
| VAR_ROUTE102_ACCESSIBLE | 0x405C | Ch1 | - |
| VAR_PETALBURG_GYM_STATE | 0x4059 | Ch1, Ch2, Ch3, Ch5, Ch6 | Ch0 |
| VAR_PETALBURG_STATE | 0x405A | Ch1 | - |
| VAR_BIRCH_STATE (C) | 0x403B | (C engine / new game only) | Ch0 |
| FLAG_BADGE01_GET (C) | engine | Ch1 | Ch2, S_common |
| FLAG_BADGE02_GET (C) | engine | Ch2 | - |
| FLAG_BADGE03_GET (C) | engine | Ch3 | Ch1, S_common |
| FLAG_BADGE04_GET (C) | engine | Ch5 | Ch3, S_common |
| FLAG_BADGE05_GET (C) | engine | Ch6 | Ch0, Ch1, Ch3 |
| FLAG_BADGE06_GET (C) | engine | Ch7 | Ch3, Ch8, Ch10, Ch11 |
| FLAG_BADGE07_GET (C) | engine | Ch9 | Ch3, Ch8 |
| FLAG_BADGE08_GET (C) | engine | Ch10 | Ch3, Ch8 |
| VAR_RUSTBORO_STATE | 0x405E | Ch1, Ch2 | - |
| FLAG_DEVON_GOODS_STOLEN | 259 | Ch2 | - |
| FLAG_RECOVERED_DEVON_GOODS | 308 | Ch2 | - |
| FLAG_RETURNED_DEVON_GOODS | 309 | Ch2 | - |
| FLAG_RECEIVED_POKENAV | 302 | Ch2 | - |
| FLAG_DELIVERED_STEVEN_LETTER | 258 | Ch2 | - |
| FLAG_DELIVERED_DEVON_GOODS | 340 | Ch3 | Ch2 |
| VAR_BRINEY_LOCATION | 0x4067 | Ch2 | - |
| VAR_BRINEY_HOUSE_STATE | 0x4066 | Ch2 | - |
| VAR_BOARD_BRINEY_BOAT_ROUTE104_STATE | 0x4065 | Ch2 | Ch1 |
| VAR_RUSTURF_TUNNEL_STATE (C) | 0x406B | Ch2, Ch3 | - |
| VAR_ROUTE116_STATE | 0x406A | Ch2 | - |
| FLAG_HIDE_MR_BRINEY_ROUTE104_HOUSE | 282 | Ch2, S_common | - |
| FLAG_HIDE_PEEKO_BRINEY_HOUSE | 284 | Ch2, S_common | - |
| FLAG_HIDE_RIVAL_RUSTBORO | 286 | Ch2 | - |
| FLAG_HIDE_EVIL_TEAM_ROUTE110 | 352 | Ch3 | - |
| FLAG_HIDE_WALLY_WANDAS_HOUSE | 382 | Ch3, Ch5 | - |
| FLAG_HIDE_WATTSON_MAUVILLE | 383 | Ch3, Ch6 | - |
| FLAG_HIDE_SLUDGE_BOMB_MAN_DEWFORD_HALL | 544 | Ch6 | Ch2 |
| VAR_NEW_MAUVILLE_STATE | 0x40B1 | Ch6 | Ch3 |
| FLAG_HIDE_GRUNTS_BLOCKING_CABLE_CAR | 461 | Ch4 | - |
| FLAG_DEFEATED_EVIL_TEAM_MT_CHIMNEY | 507 | Ch5 | Ch4 |
| FLAG_HIDE_PROF_COSMO_FALLARBOR | 513 | Ch5 | Ch4 |
| VAR_LAVARIDGE_RIVAL_STATE | 0x40A7 | Ch5 | - |
| FLAG_RECEIVED_HM_SURF | 553 | Ch6 | Ch11 |
| FLAG_RECEIVED_DEVON_SCOPE | 606 | Ch7 | - |
| FLAG_MET_RIVAL_LILYCOVE | 687 | Ch8 | Ch0 |
| VAR_MT_PYRE_STATE | 0x40C9 | Ch8, Ch10 | - |
| VAR_SLATEPORT_STATE | 0x40CD | Ch8 | Ch3 |
| VAR_SLATEPORT_HARBOR_STATE | 0x40CC | Ch8 | Ch3 |
| FLAG_HIDE_GRUNT_1_BLOCKING_HIDEOUT | 662 | Ch8 | S_unused |
| FLAG_EVIL_TEAM_ESCAPED_IN_SUBMARINE | 646 | Ch8 | - |
| FLAG_HIDE_GRUNTS_LILYCOVE | 658 | Ch8 | - |
| VAR_STEVENS_HOUSE_STATE | 0x40D8 | Ch9, Ch10, Ch11 | - |
| FLAG_HIDE_BRINEY_SLATEPORT_SHIPYARD | 755 | Ch9, Ch11 | Ch3 |
| FLAG_HIDE_WORKERS_SLATEPORT_HARBOR | 682 | Ch8, Ch9 | Ch3 |
| FLAG_SYS_WEATHER_CTRL (C) | 903 | Ch10 | Ch8, Ch9, Ch11 |
| FLAG_LEGENDARY_BATTLE_COMPLETED | 2074 | Ch10 | Ch8 |
| VAR_SOOTOPOLIS_STATE | 0x40ED | Ch10 | - |
| VAR_ROUTE128_STATE | 0x40E2 | Ch10 | - |
| FLAG_HIDE_SOOTOPOLIS_RESIDENTS | 874 | Ch10 | - |
| FLAG_DEFEATED_WALLY_VICTORY_ROAD | 988 | Ch11 | Ch3, Ch6 |
| FLAG_SYS_GAME_CLEAR (C) | engine 2400 | (C engine / new game only) | Ch1, Ch3, Ch6, Ch8, Ch9, Ch13, S_common, S_optional |
| FLAG_RECEIVED_SS_TICKET | 1509 | Ch13 | Ch11 |
| FLAG_HIDE_NORMAN_LITTLEROOT | 2064 | Ch13 | Ch0 |
| FLAG_REGI_DOORS_OPENED | 1069 | Ch12 | Ch4, Ch6, Ch7 |

Chapter-to-chapter edges (ids written in the row chapter and read in the column chapter; temporaries and item flags excluded):

| writer \ reader | Ch0 | Ch1 | Ch2 | Ch3 | Ch4 | Ch5 | Ch6 | Ch7 | Ch8 | Ch9 | Ch10 | Ch11 | Ch12 | Ch13 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Ch0 | . | 4 |  |  |  |  |  |  |  |  |  |  |  |  |
| Ch1 | 9 | . | 3 | 3 |  | 1 | 1 |  |  |  |  |  |  |  |
| Ch2 | 1 | 5 | . | 1 | 1 | 1 | 1 |  |  |  |  |  |  |  |
| Ch3 | 1 | 2 | 6 | . |  | 1 | 1 |  | 2 |  |  |  |  |  |
| Ch4 |  |  | 1 | 4 | . | 2 |  | 5 | 3 |  |  |  |  |  |
| Ch5 | 1 | 1 | 1 | 4 | 5 | . | 1 |  |  |  |  |  |  |  |
| Ch6 | 2 | 5 | 3 | 6 |  | 1 | . | 1 | 1 |  | 1 | 1 | 1 | 1 |
| Ch7 |  |  |  | 1 |  |  | 1 | . | 2 | 1 | 2 | 1 | 1 | 1 |
| Ch8 | 4 |  |  | 9 |  |  | 1 | 1 | . |  | 1 |  | 1 | 1 |
| Ch9 |  |  |  | 3 |  |  |  | 2 | 1 | . |  | 1 |  | 1 |
| Ch10 |  |  |  | 1 |  |  | 1 | 1 | 8 | 3 | . | 1 | 1 | 1 |
| Ch11 |  | 1 |  | 3 |  |  | 1 |  | 1 | 2 |  | . |  | 2 |
| Ch12 |  |  |  |  | 1 |  | 2 | 2 | 1 |  | 1 |  | . | 1 |
| Ch13 | 4 |  |  |  |  |  | 1 | 1 | 1 | 1 | 1 | 2 | 1 | . |

## 3. Chapters in detail

### Ch0 - Opening (DONE): truck, Littleroot, Route 101 rescue, starter

**DONE**

Size: 1707 script lines in 218 labels (+509 text lines in owned maps); 0 trainerbattle commands, 0 unique trainers; 49 flags, 11 vars.

New-game init (`data/scripts/new_game.inc` EventScript_ResetAllMapFlags) sets 132 hide flags/vars; they are counted in the chapters whose maps show those objects.

Story beats (in order; `map: label`):

1. `InsideOfTruck`: `InsideOfTruck_EventScript_15FC29` - truck ride, step out (0788_truck.s / scenes/truck.inc)
2. `LittlerootTown`: `LittlerootTown_EventScript_GoInsideWithMom` - Mom, moving in, clock, TV, rival's house (0778, scenes/players_house_*.inc)
3. `LittlerootTown`: `LittlerootTown_EventScript_GoSaveBirchTrigger` - twin at the north exit
4. `Route101`: `Route101_EventScript_14EA7F` - Birch rescue, starter from the Bag, Poochyena battle (0634_route_101.s)
5. `LittlerootTown_ProfessorBirchsLab`: `LittlerootTown_ProfessorBirchsLab_EventScript_GiveStarterEvent` - keep the starter, nickname, "go see the rival" (0792_birch_lab.s)

Other chapters' beats inside this chapter's files (reserve slots for them):

- Ch1: `LittlerootTown` from `LittlerootTown_EventScript_SetRivalLeftForRoute103` - rival-left / rival-moved-from-Oldale states
- Ch1: `LittlerootTown` from `LittlerootTown_EventScript_GiveRunningShoesTrigger0` - Mom stops you: Running Shoes (+ Mom walk-back movement)
- Ch1: `LittlerootTown_ProfessorBirchsLab` from `LittlerootTown_ProfessorBirchsLab_EventScript_GivePokedexEvent` - Pokedex event (OnFrame)
- Ch1: `LittlerootTown_ProfessorBirchsLab` from `LittlerootTown_ProfessorBirchsLab_EventScript_152D9A` - Pokedex + rival's Poke Balls
- Ch1: `LittlerootTown_ProfessorBirchsLab` from `LittlerootTown_ProfessorBirchsLab_EventScript_Rival` - rival in the lab after the Pokedex
- Ch1: `LittlerootTown_BrendansHouse_1F` from `LittlerootTown_BrendansHouse_1F_EventScript_CheckShowShoesManual` - Running Shoes manual on the table
- Ch1: `LittlerootTown_MaysHouse_1F` from `LittlerootTown_MaysHouse_1F_EventScript_CheckShowShoesManual` - Running Shoes manual on the table
- Ch1: `LittlerootTown_MaysHouse_1F` from `RivalsHouse_1F_EventScript_RivalMom` - rival's mom after the rival left
- Ch6: `data/scripts/players_house.inc` from `LittlerootTown_BrendansHouse_1F_EventScript_1B6C3D` - Mom gives the Amulet Coin after the Balance Badge
- Ch8: `LittlerootTown_MaysHouse_2F` from `RivalsHouse_2F_EventScript_RivalPostLilycove` - rival at home after Lilycove
- Ch13: `data/scripts/players_house.inc` from `PlayersHouse_1F_EventScript_GetSSTicketAndSeeLatiTV` - Dad brings the S.S. Ticket, Lati TV report
- Ch13: `LittlerootTown` from `LittlerootTown_EventScript_SetExitedHouseAfterLatiSSTicketEvent` - state after the S.S. Ticket scene
- Ch13: `LittlerootTown` from `LittlerootTown_EventScript_BeginDexUpgradeScene` - dex-upgrade state hook

Maps (10): owned (port the whole file) / touched (warps, flags, foreign beats):

| map | role | status |
|---|---|---|
| InsideOfTruck | owned, main path | built (hand, zone 394 truck: data/interiors/394.json) |
| LittlerootTown | owned, main path | built (outdoor zone 389) |
| LittlerootTown_BrendansHouse_1F | owned, main path | built (room hand, zone 390) |
| LittlerootTown_BrendansHouse_2F | owned, main path | built (room hand, zone 391) |
| LittlerootTown_MaysHouse_1F | owned, main path | built (room hand, zone 392) |
| LittlerootTown_MaysHouse_2F | owned, main path | built (room hand, zone 393) |
| LittlerootTown_ProfessorBirchsLab | owned, main path | built (room hand, zone 396) |
| Route101 | owned, main path | built (outdoor zone 317) |
| PetalburgCity | scripted warp/ref, owner Ch1 | built (outdoor zone 439) |
| Route103 | objects/triggers switched by this chapter, owner Ch1 | built (outdoor zone 326) |

Flags used (49; 0 item-ball flags; 29 have this chapter as home):

<details><summary>flag list</summary>

FLAG_ADVENTURE_STARTED [134, home Ch1], FLAG_BADGE05_GET [engine, C, home Ch6], FLAG_BIRCH_AIDE_MET [102], FLAG_DECORATION_10 [home S_optional], FLAG_DECORATION_11 [home S_optional], FLAG_DECORATION_12 [home S_optional], FLAG_DECORATION_13 [home S_optional], FLAG_DECORATION_2 [C, home S_optional], FLAG_DECORATION_3 [home S_optional], FLAG_DECORATION_4 [home S_optional], FLAG_DECORATION_5 [home S_optional], FLAG_DECORATION_6 [home S_optional], FLAG_DECORATION_7 [home S_optional], FLAG_DECORATION_8 [home S_optional], FLAG_DECORATION_9 [home S_optional], FLAG_DEFEATED_RIVAL_ROUTE103 [135, home Ch1], FLAG_HIDE_BIRCH_BATTLE_POOCHYENA [2059], FLAG_HIDE_BIRCH_IN_LAB [103], FLAG_HIDE_BIRCH_ROUTE101 [104], FLAG_HIDE_BIRCH_ROUTE103 [107], FLAG_HIDE_BIRCH_STARTERS_BAG [2060], FLAG_HIDE_BOY_ROUTE101 [108], FLAG_HIDE_BRENDAN_MOM [2052], FLAG_HIDE_BRENDAN_MOM_DOWNSTAIRS [2054], FLAG_HIDE_BRENDAN_UPSTAIRS [2053], FLAG_HIDE_FAT_MAN_LITTLEROOT [2069], FLAG_HIDE_MACHOKE_MOVER_1 [2061], FLAG_HIDE_MACHOKE_MOVER_2 [2062], FLAG_HIDE_MAP_NAME_POPUP [2049, C], FLAG_HIDE_MAY_MOM [2056], FLAG_HIDE_MAY_MOM_DOWNSTAIRS [2050], FLAG_HIDE_MAY_PICHU_DOLL [2065, home Ch8], FLAG_HIDE_MAY_UPSTAIRS [2057], FLAG_HIDE_MOM_LITTLEROOT [2068], FLAG_HIDE_MOM_UPSTAIRS [2063], FLAG_HIDE_MOVING_TRUCK_BRENDAN [2055], FLAG_HIDE_MOVING_TRUCK_MAY [2051], FLAG_HIDE_NORMAN_LITTLEROOT [2064, home Ch13], FLAG_HIDE_POOCHYENA_ROUTE101 [109], FLAG_HIDE_RIVAL_BIRCH_LAB [200, home Ch1], FLAG_MET_RIVAL_LILYCOVE [687, home Ch8], FLAG_MET_RIVAL_MOM [2067], FLAG_RECEIVED_RUNNING_SHOES [218, home Ch1], FLAG_RESCUED_BIRCH [110], FLAG_SET_WALL_CLOCK [2066], FLAG_SYS_POKEMON_GET [engine 2401, C], FLAG_SYS_TV_HOME [111, C], FLAG_UNKNOWN_BIRCH_380 [112], FLAG_VISITED_LITTLEROOT_TOWN [113, C]

</details>

Vars used (11): VAR_BIRCH_LAB_STATE [0x4051], VAR_BIRCH_STATE [0x403B, C], VAR_LITTLEROOT_HOUSES_STATE [0x404F], VAR_LITTLEROOT_HOUSES_STATE_2 [0x4050], VAR_LITTLEROOT_INTRO_STATE [0x404E], VAR_LITTLEROOT_RIVAL_STATE [0x4053], VAR_LITTLEROOT_STATE [0x4054], VAR_OLDALE_STATE [0x4058, home Ch1], VAR_PETALBURG_GYM_STATE [0x4059, home Ch1], VAR_ROUTE101_STATE [0x4052], VAR_SECRET_BASE_INITIALIZED [0x403C, C]

Reads ids written by other chapters:

- from Ch1: FLAG_ADVENTURE_STARTED, FLAG_DEFEATED_RIVAL_ROUTE103, FLAG_HIDE_RIVAL_BIRCH_LAB, FLAG_RECEIVED_RUNNING_SHOES, VAR_BIRCH_LAB_STATE, VAR_LITTLEROOT_RIVAL_STATE, VAR_LITTLEROOT_STATE, VAR_OLDALE_STATE, VAR_PETALBURG_GYM_STATE
- from Ch2: VAR_PETALBURG_GYM_STATE
- from Ch3: VAR_PETALBURG_GYM_STATE
- from Ch5: VAR_PETALBURG_GYM_STATE
- from Ch6: FLAG_BADGE05_GET, VAR_PETALBURG_GYM_STATE
- from Ch8: FLAG_HIDE_BRENDAN_UPSTAIRS, FLAG_HIDE_MAY_PICHU_DOLL, FLAG_HIDE_MAY_UPSTAIRS, FLAG_MET_RIVAL_LILYCOVE
- from Ch13: FLAG_HIDE_NORMAN_LITTLEROOT, VAR_LITTLEROOT_HOUSES_STATE, VAR_LITTLEROOT_HOUSES_STATE_2, VAR_LITTLEROOT_INTRO_STATE

- Note: Ported already (notes/OPENING.md). Later beats that live in these files are listed as foreign beats of Ch1/Ch6/Ch8/Ch13 below.

### Ch1 - Rival on Route 103, Pokedex, Petalburg (Norman, Wally), Petalburg Woods, Rustboro: Roxanne

**UNBLOCKED** | in progress: PetalburgWoods | badge: Stone Badge (1)

Size: 3573 script lines in 566 labels (+1136 text lines in owned maps); 37 trainerbattle commands, 26 unique trainers; 73 flags, 13 vars.

Story beats (in order; `map: label`):

1. `OldaleTown`: `OldaleTown_EventScript_MartEmployee` - Mart employee walks you to the Mart, Potion (FLAG_RECEIVED_POTION_OLDALE)
2. `OldaleTown`: `OldaleTown_EventScript_BlockedPath` - Route 102 blocked until the Pokedex (VAR_ROUTE102_ACCESSIBLE)
3. `Route103`: `Route103_EventScript_14EB92` - rival on Route 103 (trainerbattle_no_intro TRAINER_MAY_x/BRENDAN_x by VAR_STARTER_MON) **[DONE: ported and tested]**
4. `Route103`: `Route103_EventScript_14ED46` - after the battle: FLAG_DEFEATED_RIVAL_ROUTE103, VAR_BIRCH_LAB_STATE, VAR_OLDALE_STATE **[DONE: ported and tested]**
5. `OldaleTown`: `OldaleTown_EventScript_RivalTrigger1` - rival walks you through Oldale (VAR_OLDALE_STATE 1) -> OldaleTown_EventScript_RivalFinish **[DONE: ported and tested]**
6. `LittlerootTown_ProfessorBirchsLab`: `LittlerootTown_ProfessorBirchsLab_EventScript_GivePokedexEvent` - Birch gives the Pokedex, rival gives Poke Balls (GivePokedex / ReceivePokedex: FLAG_SYS_POKEDEX_GET, FLAG_ADVENTURE_STARTED) **[DONE: ported and tested]**
7. `LittlerootTown`: `LittlerootTown_EventScript_GiveRunningShoesTrigger0` - Mom gives the Running Shoes (VAR_LITTLEROOT_STATE 3 -> FLAG_SYS_B_DASH)
8. `PetalburgCity`: `PetalburgCity_EventScript_ShowGymToPlayer0` - Petalburg arrival (VAR_PETALBURG_STATE 0)
9. `PetalburgCity_Gym`: `PetalburgCity_Gym_EventScript_Norman` - meet Norman (no badge branch), Wally walks in
10. `PetalburgCity_Gym`: `PetalburgCity_Gym_EventScript_BeginWallyTutorial` - Norman lends Wally a Zigzagoon, walk out with Wally
11. `PetalburgCity`: `PetalburgCity_EventScript_WallyTutorial` - Wally catches Ralts (special ScrSpecial_StartWallyTutorialBattle), warp back to the gym
12. `PetalburgCity_Gym`: `PetalburgCity_Gym_EventScript_ReturnFromWallyTutorial` - Norman: "go to Rustboro" (VAR_PETALBURG_GYM_STATE)
13. `Route104`: `Route104_EventScript_14F172` - Route 104 south trainers
14. `PetalburgWoods`: `PetalburgWoods_EventScript_15CCA8` - Devon researcher + Team Aqua grunt (coord triggers, TRAINER_PETALBURG_WOODS_GRUNT; also 15CD42)
15. `PetalburgWoods`: `PetalburgWoods_EventScript_15CEDC` - Miracle Seed
16. `Route104_PrettyPetalFlowerShop`: `Route104_PrettyPetalFlowerShop_EventScript_15BE0B` - flower shop: Wailmer Pail, daily berry
17. `RustboroCity_Gym`: `RustboroCity_Gym_EventScript_Roxanne` - Roxanne -> RoxanneDefeated (FLAG_BADGE01_GET, VAR_RUSTBORO_STATE=1 arms the theft scene) -> GiveRockTomb
18. `RustboroCity_CuttersHouse`: `RustboroCity_CuttersHouse_EventScript_Cutter` - HM01 Cut
19. `RustboroCity_PokemonSchool`: `RustboroCity_PokemonSchool_EventScript_Teacher` - Quick Claw

Foreign beats this chapter writes into other chapters' files (scene includes):

- `LittlerootTown` [LittlerootTown_EventScript_SetRivalLeftForRoute103 .. LittlerootTown_EventScript_SetExitedHouseAfterLatiSSTicketEvent) ~7 lines - rival-left / rival-moved-from-Oldale states
- `LittlerootTown` [LittlerootTown_EventScript_GiveRunningShoesTrigger0 .. end of file) ~453 lines - Mom stops you: Running Shoes (+ Mom walk-back movement)
- `LittlerootTown_ProfessorBirchsLab` [LittlerootTown_ProfessorBirchsLab_EventScript_GivePokedexEvent .. LittlerootTown_ProfessorBirchsLab_EventScript_Aide) ~15 lines - Pokedex event (OnFrame)
- `LittlerootTown_ProfessorBirchsLab` [LittlerootTown_ProfessorBirchsLab_EventScript_152D9A .. LittlerootTown_ProfessorBirchsLab_EventScript_Machine) ~66 lines - Pokedex + rival's Poke Balls
- `LittlerootTown_ProfessorBirchsLab` [LittlerootTown_ProfessorBirchsLab_EventScript_Rival .. LittlerootTown_ProfessorBirchsLab_EventScript_PC) ~16 lines - rival in the lab after the Pokedex
- `LittlerootTown_BrendansHouse_1F` [LittlerootTown_BrendansHouse_1F_EventScript_CheckShowShoesManual .. LittlerootTown_BrendansHouse_1F_OnTransition) ~8 lines - Running Shoes manual on the table
- `LittlerootTown_MaysHouse_1F` [LittlerootTown_MaysHouse_1F_EventScript_CheckShowShoesManual .. LittlerootTown_MaysHouse_1F_OnTransition) ~8 lines - Running Shoes manual on the table
- `LittlerootTown_MaysHouse_1F` [RivalsHouse_1F_EventScript_RivalMom .. LittlerootTown_MaysHouse_1F_EventScript_GoSeeRoom) ~23 lines - rival's mom after the rival left

Other chapters' beats inside this chapter's files (reserve slots for them):

- Ch2: `Route104` from `Route104_EventScript_14EFD5` - Mr. Briney's boat: board on Route 104, sail to Dewford
- Ch6: `PetalburgCity_Gym` from `PetalburgCity_Gym_EventScript_NormanPostBattle` - Norman battle, Facade TM, gym rooms, doors, 7 gym trainers

Maps (40): owned (port the whole file) / touched (warps, flags, foreign beats):

| map | role | status |
|---|---|---|
| OldaleTown | owned, main path | built (outdoor zone 397) |
| PetalburgCity | owned, main path | built (outdoor zone 439) |
| PetalburgCity_Gym | owned, main path | built (room big, zone 452) |
| PetalburgWoods | owned, main path | **in progress (standalone map, zone 37: built in the standalone agent's test ROM, proof work/agents/standalone/proofs/PetalburgWoods.png; not in the main build yet, hoenn_standalone.json "build" is empty)** |
| Route102 | owned, main path | built (outdoor zone 321) |
| Route103 | owned, main path | built (outdoor zone 326) |
| Route104 | owned, main path | built (outdoor zone 329) |
| RustboroCity_Gym | owned, main path | built (room auto, zone 583) |
| OldaleTown_House1 | owned | built (room auto, zone 380) |
| OldaleTown_House2 | owned | built (room auto, zone 381) |
| OldaleTown_Mart | owned | built (room auto, zone 384) |
| OldaleTown_PokemonCenter_1F | owned | built (room center, zone 398) |
| OldaleTown_PokemonCenter_2F | owned | built (room center, zone 385) |
| PetalburgCity_House1 | owned | built (room auto, zone 462) |
| PetalburgCity_House2 | owned | built (room auto, zone 464) |
| PetalburgCity_Mart | owned | built (room auto, zone 471) |
| PetalburgCity_PokemonCenter_1F | owned | built (room center, zone 413) |
| PetalburgCity_PokemonCenter_2F | owned | built (room center, zone 494) |
| Route104_PrettyPetalFlowerShop | owned | built (room auto, zone 505) |
| RustboroCity_CuttersHouse | owned | built (room auto, zone 572) |
| RustboroCity_Flat1_1F | owned | built (room auto, zone 578) |
| RustboroCity_Flat1_2F | owned | built (room auto, zone 579) |
| RustboroCity_Flat2_1F | owned | built (room auto, zone 580) |
| RustboroCity_Flat2_2F | owned | built (room auto, zone 581) |
| RustboroCity_Flat2_3F | owned | built (room auto, zone 582) |
| RustboroCity_House1 | owned | built (room auto, zone 585) |
| RustboroCity_House2 | owned | built (room auto, zone 587) |
| RustboroCity_House3 | owned | built (room auto, zone 588) |
| RustboroCity_Mart | owned | built (room auto, zone 589) |
| RustboroCity_PokemonCenter_1F | owned | built (room center, zone 425) |
| RustboroCity_PokemonCenter_2F | owned | built (room center, zone 590) |
| RustboroCity_PokemonSchool | owned | built (room auto, zone 591) |
| LittlerootTown_ProfessorBirchsLab | foreign beat, main path | built (room hand, zone 396) |
| RustboroCity | main path | built (outdoor zone 113) |
| LittlerootTown | foreign beat | built (outdoor zone 389) |
| LittlerootTown_BrendansHouse_1F | foreign beat | built (room hand, zone 390) |
| LittlerootTown_MaysHouse_1F | foreign beat | built (room hand, zone 392) |
| MauvilleCity | scripted warp/ref, owner Ch3 | built (outdoor zone 406) |
| PetalburgCity_WallysHouse | warp from an owned map, owner Ch6 | built (room auto, zone 500) |
| Route104_MrBrineysHouse | warp from an owned map, owner Ch2 | built (room auto, zone 503) |

Flags used (73; 12 item-ball flags; 50 have this chapter as home):

<details><summary>flag list</summary>

FLAG_ADVENTURE_STARTED [134], FLAG_BADGE01_GET [engine, C], FLAG_BADGE03_GET [engine, C, home Ch3], FLAG_BADGE05_GET [engine, C, home Ch6], FLAG_DAILY_RECEIVED_BERRY_FLOWER_SHOP [2744], FLAG_DEFEATED_PETALBURG_GYM [540, home Ch6], FLAG_DEFEATED_RIVAL_ROUTE103 [135], FLAG_DEFEATED_RUSTBORO_GYM [139], FLAG_DONT_TRANSITION_MUSIC [140, C], FLAG_HIDDEN_ITEM_25 [engine], FLAG_HIDDEN_ITEM_2C [engine], FLAG_HIDDEN_ITEM_3A [engine], FLAG_HIDDEN_ITEM_3B [engine], FLAG_HIDDEN_ITEM_3C [engine], FLAG_HIDDEN_ITEM_3D [engine], FLAG_HIDDEN_ITEM_3E [engine], FLAG_HIDDEN_ITEM_55 [engine], FLAG_HIDDEN_ITEM_58 [engine], FLAG_HIDDEN_ITEM_5F [engine], FLAG_HIDE_BIRCH_ROUTE103 [107, home Ch0], FLAG_HIDE_DEVON_PETALBURG_WOODS [142], FLAG_HIDE_EVIL_TEAM_PETALBURG_WOODS [143], FLAG_HIDE_FLOWER_SHOP_WORKER_OUTSIDE [144], FLAG_HIDE_MAP_NAME_POPUP [2049, C, home Ch0], FLAG_HIDE_MR_BRINEY_BOAT_ROUTE104 [278, home Ch2], FLAG_HIDE_MR_BRINEY_ROUTE104 [281, home Ch2], FLAG_HIDE_NORMAN_PETALBURG_GYM [145], FLAG_HIDE_PETALBURG_GYM_GUIDE [543, home Ch6], FLAG_HIDE_RIVAL_BIRCH_LAB [200], FLAG_HIDE_RIVAL_OLDALE_TOWN [201], FLAG_HIDE_RIVAL_ROUTE103 [202], FLAG_HIDE_WALLY_FATHER_PETALBURG [203], FLAG_HIDE_WALLY_MOM_PETALBURG_1 [204], FLAG_HIDE_WALLY_MOTHER_PETALBURG [205], FLAG_HIDE_WALLY_PETALBURG [206], FLAG_HIDE_WALLY_PETALBURG_GYM [207], FLAG_LANDMARK_FLOWER_SHOP [208, C], FLAG_MET_DEVON_EMPLOYEE [294, home Ch2], FLAG_MET_PRETTY_PETAL_SHOP_OWNER [209], FLAG_PETALBURG_MART_EXPANDED_ITEMS [550, home Ch6], FLAG_RECEIVED_CHESTO_BERRY_ROUTE104 [210], FLAG_RECEIVED_HM01 [211], FLAG_RECEIVED_MIRACLE_SEED [212], FLAG_RECEIVED_POTION_OLDALE [213], FLAG_RECEIVED_PREMIER_BALL_RUSTBORO [216], FLAG_RECEIVED_QUICK_CLAW [217], FLAG_RECEIVED_RUNNING_SHOES [218], FLAG_RECEIVED_TM09 [219], FLAG_RECEIVED_TM_ROCK_TOMB [220], FLAG_RECEIVED_WAILMER_PAIL [221], FLAG_RECEIVED_WHITE_HERB [222], FLAG_RIVAL_LEFT_FOR_ROUTE103 [223], FLAG_RUSTBORO_NPC_TRADE_COMPLETED [224], FLAG_SYS_B_DASH [engine 2403, C], FLAG_SYS_CHAT_USED [2076, C], FLAG_SYS_EXDATA_ENABLE [228, C], FLAG_SYS_GAME_CLEAR [engine 2400, C], FLAG_SYS_POKEDEX_GET [2070, C], FLAG_UNKNOWN_BIRCH_380 [112, home Ch0], FLAG_VISITED_OLDALE_TOWN [229, C], FLAG_VISITED_PETALBURG_CITY [230, C]

</details>

Vars used (13): VAR_BIRCH_LAB_STATE [0x4051, home Ch0], VAR_BOARD_BRINEY_BOAT_ROUTE104_STATE [0x4065, home Ch2], VAR_CABLE_CLUB_STATE [0x4057], VAR_LITTLEROOT_RIVAL_STATE [0x4053, home Ch0], VAR_LITTLEROOT_STATE [0x4054, home Ch0], VAR_OLDALE_STATE [0x4058], VAR_PETALBURG_GYM_STATE [0x4059], VAR_PETALBURG_STATE [0x405A], VAR_PETALBURG_WOODS_STATE [0x405B], VAR_ROUTE102_ACCESSIBLE [0x405C], VAR_ROUTE103_STATE [0x405D], VAR_RUSTBORO_STATE [0x405E], VAR_STARTER_MON [0x4030, C]

Reads ids written by other chapters:

- from Ch0: FLAG_HIDE_BIRCH_ROUTE103, FLAG_UNKNOWN_BIRCH_380, VAR_BIRCH_LAB_STATE, VAR_LITTLEROOT_RIVAL_STATE
- from Ch2: FLAG_HIDE_MR_BRINEY_BOAT_ROUTE104, FLAG_HIDE_MR_BRINEY_ROUTE104, FLAG_MET_DEVON_EMPLOYEE, VAR_BOARD_BRINEY_BOAT_ROUTE104_STATE, VAR_PETALBURG_GYM_STATE
- from Ch3: FLAG_BADGE03_GET, VAR_PETALBURG_GYM_STATE
- from Ch5: VAR_PETALBURG_GYM_STATE
- from Ch6: FLAG_BADGE05_GET, FLAG_DEFEATED_PETALBURG_GYM, FLAG_HIDE_PETALBURG_GYM_GUIDE, FLAG_PETALBURG_MART_EXPANDED_ITEMS, VAR_PETALBURG_GYM_STATE
- from Ch11: FLAG_HIDE_PETALBURG_GYM_GUIDE

Trainers: TRAINER_ALLEN, TRAINER_AMY_AND_LIV_1, TRAINER_ANDREW, TRAINER_BILLY, TRAINER_BRENDAN_1, TRAINER_BRENDAN_4, TRAINER_BRENDAN_7, TRAINER_CALVIN_1, TRAINER_CINDY_1, TRAINER_DAISY, TRAINER_GINA_AND_MIA_1, TRAINER_HALEY_1, TRAINER_IVAN, TRAINER_JAMES_1, TRAINER_JOSH, TRAINER_LYLE, TRAINER_MAY_1, TRAINER_MAY_4, TRAINER_MAY_7, TRAINER_MIGUEL_1, TRAINER_PETALBURG_WOODS_GRUNT, TRAINER_RICK, TRAINER_ROXANNE, TRAINER_TIANA, TRAINER_TOMMY, TRAINER_WINSTON_1

- Note: Worked example already ported and tested (story_infra agent): Route 103 rival (scenes/Route103.inc), Oldale rival trigger (0794/0795), lab Pokedex (0792/0793).
- Note: Takes over the remaining parts of the Ch0 files (Pokedex, Running Shoes): add them as scenes/*.inc to the Ch0 zone files.
- Note: Owns PetalburgCity_Gym (its Norman battle + gym rooms are Ch6 beats in the same file: reserve ScriptEntry slots for Ch6).
- Note: RustboroCity itself is Ch2 (theft scene); Rustboro townspeople are already generated, so the gym is reachable without it.

### Ch2 - Devon Goods (Route 116, Rusturf Tunnel), Mr. Stone, Mr. Briney, Dewford: Brawly, Granite Cave: Steven

**UNBLOCKED** | badge: Knuckle Badge (2)

Size: 3333 script lines in 416 labels (+1246 text lines in owned maps); 35 trainerbattle commands, 29 unique trainers; 82 flags, 9 vars.

Story beats (in order; `map: label`):

1. `RustboroCity`: `RustboroCity_EventScript_StolenGoodsScene` - Aqua grunt steals the Devon Goods (coord StolenGoodsTrigger0-4, VAR_RUSTBORO_STATE 1)
2. `RustboroCity`: `RustboroCity_EventScript_EmployeeAskToGetGoods` - Devon employee asks for help (HelpGetGoodsTrigger, VAR_RUSTBORO_STATE 2)
3. `Route116`: `Route116_EventScript_150B6E` - Route 116 chase / Briney looking for Peeko (VAR_ROUTE116_STATE)
4. `RusturfTunnel`: `RusturfTunnel_EventScript_15C9EA` - grunt battle (TRAINER_RUSTURF_TUNNEL_GRUNT), Peeko freed, goods recovered (FLAG_RECOVERED_DEVON_GOODS)
5. `RustboroCity`: `RustboroCity_EventScript_ReturnGoods` - return the goods, warp to Devon 3F (ReturnGoodsTrigger, VAR_RUSTBORO_STATE 4)
6. `RustboroCity_DevonCorp_3F`: `RustboroCity_DevonCorp_3F_EventScript_MeetPresident` - Mr. Stone: PokeNav (FLAG_SYS_POKENAV_GET), letter for Steven, goods for Capt. Stern
7. `RustboroCity`: `RustboroCity_EventScript_RivalEncounter` - rival in Rustboro (FLAG_MET_RIVAL_RUSTBORO)
8. `Route104_MrBrineysHouse`: `Route104_MrBrineysHouse_EventScript_15BD0E` - Mr. Briney agrees to sail (FLAG_MR_BRINEY_SAILING_INTRO) -> 15BDAB
9. `Route104`: `Route104_EventScript_14EFD5` - board the boat, sail to Dewford (Ch1 file, foreign beat)
10. `DewfordTown`: `DewfordTown_EventScript_GiveOldRod` - Old Rod
11. `DewfordTown_Gym`: `DewfordTown_Gym_EventScript_Brawly` - Brawly (dark gym) -> BrawlyDefeated (FLAG_BADGE02_GET) -> GiveBulkUp
12. `GraniteCave_1F`: `GraniteCave_1F_EventScript_15CBA7` - HM05 Flash
13. `GraniteCave_StevensRoom`: `GraniteCave_StevensRoom_EventScript_15CBFA` - Steven: letter delivered (FLAG_DELIVERED_STEVEN_LETTER), TM Steel Wing
14. `RustboroCity_DevonCorp_3F`: `RustboroCity_DevonCorp_3F_EventScript_GiveExpShare` - Exp. Share from Mr. Stone after the letter (the hack's Gen 6 Exp. Share key item)
15. `DewfordTown`: `DewfordTown_EventScript_SailToSlateport` - Briney sails to Route 109 (needs the goods still undelivered) -> Route109_EventScript_14F548
16. `Route109_SeashoreHouse`: `Route109_SeashoreHouse_EventScript_160F09` - Seashore House: beat the 3 trainers, Soda Pop

Foreign beats this chapter writes into other chapters' files (scene includes):

- `Route104` [Route104_EventScript_14EFD5 .. Route104_EventScript_14F172) ~263 lines - Mr. Briney's boat: board on Route 104, sail to Dewford

Other chapters' beats inside this chapter's files (reserve slots for them):

- Ch3: `RusturfTunnel` from `RusturfTunnel_EventScript_15C7D1` - Rock Smash opens the tunnel: Wanda + boyfriend reunite, HM04 Strength
- Ch4: `RustboroCity_DevonCorp_2F` from `RustboroCity_DevonCorp_2F_EventScript_FossilScientist` - fossil revival (Root/Claw fossil from the Route 111 desert)
- Ch6: `DewfordTown_Hall` from `DewfordTown_Hall_EventScript_SludgeBombMan` - Sludge Bomb man (appears after Norman)

Maps (34): owned (port the whole file) / touched (warps, flags, foreign beats):

| map | role | status |
|---|---|---|
| DewfordTown | owned, main path | built (outdoor zone 465) |
| DewfordTown_Gym | owned, main path | built (room auto, zone 25) |
| GraniteCave_1F | owned, main path | built (cave room, zone 118: data/interiors/118.json from converter/gen_caves.py) |
| GraniteCave_B1F | owned, main path | built (cave room, zone 124: data/interiors/124.json from converter/gen_caves.py) |
| GraniteCave_B2F | owned, main path | built (cave room, zone 125: data/interiors/125.json from converter/gen_caves.py) |
| GraniteCave_StevensRoom | owned, main path | built (cave room, zone 126: data/interiors/126.json from converter/gen_caves.py) |
| Route104_MrBrineysHouse | owned, main path | built (room auto, zone 503) |
| Route106 | owned, main path | built (outdoor zone 337) |
| Route109 | owned, main path | built (outdoor zone 365) |
| Route116 | owned, main path | built (outdoor zone 423) |
| RustboroCity | owned, main path | built (outdoor zone 113) |
| RustboroCity_DevonCorp_1F | owned, main path | built (room auto, zone 575) |
| RustboroCity_DevonCorp_2F | owned, main path | built (room auto, zone 576) |
| RustboroCity_DevonCorp_3F | owned, main path | built (room auto, zone 577) |
| RusturfTunnel | owned, main path | built (cave room, zone 134: data/interiors/134.json from converter/gen_caves.py) |
| DewfordTown_Hall | owned | built (room auto, zone 26) |
| DewfordTown_House1 | owned | built (room auto, zone 30) |
| DewfordTown_House2 | owned | built (room auto, zone 31) |
| DewfordTown_PokemonCenter_1F | owned | built (room center, zone 1) |
| DewfordTown_PokemonCenter_2F | owned | built (room center, zone 32) |
| Route109_SeashoreHouse | owned | built (room auto, zone 509) |
| Route116_TunnelersRestHouse | owned | built (room auto, zone 560) |
| Route104 | foreign beat, main path | built (outdoor zone 329) |
| RustboroCity_CuttersHouse | warp from an owned map, owner Ch1 | built (room auto, zone 572) |
| RustboroCity_Flat1_1F | warp from an owned map, owner Ch1 | built (room auto, zone 578) |
| RustboroCity_Flat2_1F | warp from an owned map, owner Ch1 | built (room auto, zone 580) |
| RustboroCity_Gym | warp from an owned map, owner Ch1 | built (room auto, zone 583) |
| RustboroCity_House1 | warp from an owned map, owner Ch1 | built (room auto, zone 585) |
| RustboroCity_House2 | warp from an owned map, owner Ch1 | built (room auto, zone 587) |
| RustboroCity_House3 | warp from an owned map, owner Ch1 | built (room auto, zone 588) |
| RustboroCity_Mart | warp from an owned map, owner Ch1 | built (room auto, zone 589) |
| RustboroCity_PokemonCenter_1F | warp from an owned map, owner Ch1 | built (room center, zone 425) |
| RustboroCity_PokemonSchool | warp from an owned map, owner Ch1 | built (room auto, zone 591) |
| VerdanturfTown | warp from an owned map, owner Ch3 | built (outdoor zone 120) |

Flags used (82; 13 item-ball flags; 62 have this chapter as home):

<details><summary>flag list</summary>

FLAG_BADGE01_GET [engine, C, home Ch1], FLAG_BADGE02_GET [engine, C], FLAG_DEFEATED_DEWFORD_GYM [255], FLAG_DEFEATED_PETALBURG_GYM [540, home Ch6], FLAG_DEFEATED_SEASHORE_HOUSE_TRAINERS [256], FLAG_DELIVERED_DEVON_GOODS [340, home Ch3], FLAG_DELIVERED_STEVEN_LETTER [258], FLAG_DEVON_GOODS_STOLEN [259], FLAG_DONT_TRANSITION_MUSIC [140, C, home Ch1], FLAG_HIDDEN_ITEM_2D [engine], FLAG_HIDDEN_ITEM_2E [engine], FLAG_HIDDEN_ITEM_2F [engine], FLAG_HIDDEN_ITEM_30 [engine], FLAG_HIDDEN_ITEM_31 [engine], FLAG_HIDDEN_ITEM_32 [engine], FLAG_HIDDEN_ITEM_33 [engine], FLAG_HIDDEN_ITEM_34 [engine], FLAG_HIDDEN_ITEM_3F [engine], FLAG_HIDDEN_ITEM_40 [engine], FLAG_HIDDEN_ITEM_5A [engine], FLAG_HIDDEN_ITEM_5B [engine], FLAG_HIDDEN_ITEM_BLACK_GLASSES [engine, C], FLAG_HIDE_BOYFRIEND_RUSTURF_TUNNEL [260], FLAG_HIDE_BRINEY_ROUTE116 [261], FLAG_HIDE_BRINEY_RUSTURF_TUNNEL [262], FLAG_HIDE_DEVON_EMPLOYEE_ROUTE116 [345, home Ch3], FLAG_HIDE_DEVON_RUSTBORO [263], FLAG_HIDE_EMPLOYEE_DEVON_CORP_3F [264], FLAG_HIDE_GIRLFRIEND_RUSTURF_TUNNEL [268], FLAG_HIDE_GRUNT_RUSTBORO [269], FLAG_HIDE_GRUNT_RUSTURF_TUNNEL [270], FLAG_HIDE_LOST_GLASSES_MAN [271], FLAG_HIDE_MR_BRINEY_BOAT_DEWFORD [277], FLAG_HIDE_MR_BRINEY_BOAT_ROUTE104 [278], FLAG_HIDE_MR_BRINEY_BOAT_ROUTE109 [279], FLAG_HIDE_MR_BRINEY_DEWFORD_TOWN [280], FLAG_HIDE_MR_BRINEY_ROUTE104 [281], FLAG_HIDE_MR_BRINEY_ROUTE104_HOUSE [282], FLAG_HIDE_MR_BRINEY_ROUTE109 [283], FLAG_HIDE_PEEKO_BRINEY_HOUSE [284], FLAG_HIDE_PEEKO_RUSTURF_TUNNEL [285], FLAG_HIDE_RIVAL_RUSTBORO [286], FLAG_HIDE_RUSTURF_TUNNEL_ROCK_1 [287, C], FLAG_HIDE_RUSTURF_TUNNEL_ROCK_2 [288, C], FLAG_HIDE_SLUDGE_BOMB_MAN_DEWFORD_HALL [544, home Ch6], FLAG_HIDE_STEVEN_GRANITE_CAVE [289], FLAG_HIDE_TUNNER_DIGGER_ROUTE116 [290], FLAG_LANDMARK_MR_BRINEY_HOUSE [291, C], FLAG_LANDMARK_SEASHORE_HOUSE [292, C], FLAG_LANDMARK_TUNNELERS_REST_HOUSE [293, C], FLAG_MET_DEVON_EMPLOYEE [294], FLAG_MET_RIVAL_RUSTBORO [295], FLAG_MR_BRINEY_SAILING_INTRO [296], FLAG_RECEIVED_6_SODA_POP [297], FLAG_RECEIVED_EXP_SHARE [298], FLAG_RECEIVED_HM05 [299], FLAG_RECEIVED_OLD_ROD [300], FLAG_RECEIVED_POKENAV [302], FLAG_RECEIVED_REPEAT_BALL [304], FLAG_RECEIVED_SILK_SCARF [305], FLAG_RECEIVED_SOFT_SAND [306], FLAG_RECEIVED_TM_BULK_UP [307], FLAG_RECOVERED_DEVON_GOODS [308], FLAG_RETURNED_DEVON_GOODS [309], FLAG_RUSTURF_TUNNEL_OPENED [415, C, home Ch3], FLAG_SYS_POKENAV_GET [310, C], FLAG_UNKNOWN_9F [311], FLAG_VISITED_DEWFORD_TOWN [312, C], FLAG_VISITED_RUSTBORO_CITY [313, C]

</details>

Vars used (9): VAR_BOARD_BRINEY_BOAT_ROUTE104_STATE [0x4065], VAR_BRINEY_HOUSE_STATE [0x4066], VAR_BRINEY_LOCATION [0x4067], VAR_DEVON_CORP_3F_STATE [0x4068], VAR_FOSSIL_RESURRECTION_STATE [0x4069], VAR_PETALBURG_GYM_STATE [0x4059, home Ch1], VAR_ROUTE116_STATE [0x406A], VAR_RUSTBORO_STATE [0x405E, home Ch1], VAR_RUSTURF_TUNNEL_STATE [0x406B, C]

Reads ids written by other chapters:

- from Ch1: FLAG_BADGE01_GET, VAR_PETALBURG_GYM_STATE, VAR_RUSTBORO_STATE
- from Ch3: FLAG_DELIVERED_DEVON_GOODS, FLAG_HIDE_DEVON_EMPLOYEE_ROUTE116, FLAG_HIDE_EMPLOYEE_DEVON_CORP_3F, FLAG_RUSTURF_TUNNEL_OPENED, VAR_PETALBURG_GYM_STATE, VAR_RUSTURF_TUNNEL_STATE
- from Ch4: VAR_FOSSIL_RESURRECTION_STATE
- from Ch5: VAR_PETALBURG_GYM_STATE
- from Ch6: FLAG_DEFEATED_PETALBURG_GYM, FLAG_HIDE_SLUDGE_BOMB_MAN_DEWFORD_HALL, VAR_PETALBURG_GYM_STATE

Trainers: TRAINER_ALICE, TRAINER_BRAWLY, TRAINER_CARMEN, TRAINER_CARTER, TRAINER_CLARK, TRAINER_DAVID, TRAINER_DOUGLAS, TRAINER_DWAYNE, TRAINER_EDMOND, TRAINER_ELLIOT_1, TRAINER_GWEN, TRAINER_HIDEKI, TRAINER_HUEY, TRAINER_JANICE, TRAINER_JERRY_1, TRAINER_JOEY, TRAINER_JOHANNA, TRAINER_JOSE, TRAINER_KAREN_1, TRAINER_LAURA, TRAINER_LOLA_1, TRAINER_MEL_AND_PAUL, TRAINER_MIKE_2, TRAINER_NED, TRAINER_NICOLE, TRAINER_RICKY_1, TRAINER_RUSTURF_TUNNEL_GRUNT, TRAINER_SIMON, TRAINER_TESSA

- Note: Owns RusturfTunnel: its HM04/Wanda reunion part is a Ch3 beat (scene include).
- Note: Mr. Briney's location logic is shared: event_scripts.s EventScript_ResetMrBriney / Common_EventScript_UpdateBrineyLocation (VAR_BRINEY_LOCATION) - port with this chapter.
- Note: The caves have room files from converter/gen_caves.py whose report lists what is "left for the story agents" (Steven, Flash hiker, Rusturf story objects, coord events).

### Ch3 - Slateport (museum, Capt. Stern), Route 110 rival, Mauville: Wattson, Verdanturf, Rusturf reunion

**UNBLOCKED** | badge: Dynamo Badge (3)

Size: 7228 script lines in 1136 labels (+2581 text lines in owned maps); 63 trainerbattle commands, 52 unique trainers; 109 flags, 29 vars.

- optional block **Trick House (side quest gated by badges, 3T)**: 2294 lines, 21 trainerbattle cmds in owned files; NOT BUILT: Route110_TrickHousePuzzle2, Route110_TrickHousePuzzle3, Route110_TrickHousePuzzle4, Route110_TrickHousePuzzle5, Route110_TrickHousePuzzle6, Route110_TrickHousePuzzle7, Route110_TrickHousePuzzle8
- optional block **HM04 Strength (Rusturf reunion; Strength is needed later for Seafloor Cavern / Victory Road)**: 196 lines, 0 trainerbattle cmds in owned files; NOT BUILT: -

Possible split into separate agents:

- **3a Slateport (museum, Stern, harbor, fan club, contest lobby)**: 1497 lines, 2 trainerbattle cmds
- **3b Route 110, Mauville, Route 117, Verdanturf**: 2329 lines, 40 trainerbattle cmds
- **3T Trick House**: 2294 lines, 21 trainerbattle cmds

Story beats (in order; `map: label`):

1. `SlateportCity`: `SlateportCity_EventScript_EnterSlateport` - arrive in Slateport (FLAG_VISITED_SLATEPORT_CITY)
2. `SlateportCity_SternsShipyard_1F`: `SlateportCity_SternsShipyard_1F_EventScript_Dock` - Dock: Stern is at the museum (FLAG_DOCK_REJECTED_DEVON_GOODS shows the Aqua line)
3. `SlateportCity_OceanicMuseum_1F`: `SlateportCity_OceanicMuseum_1F_EventScript_CheckMoneyForFee` - museum fee (coord PayEntranceFee*, VAR_SLATEPORT_MUSEUM_1F_STATE)
4. `SlateportCity_OceanicMuseum_1F`: `SlateportCity_OceanicMuseum_1F_EventScript_FamiliarGrunt` - the Rusturf grunt gives TM46 Thief
5. `SlateportCity_OceanicMuseum_2F`: `SlateportCity_OceanicMuseum_2F_EventScript_CaptStern` - Capt. Stern, 2 Aqua grunt battles, Archie, goods delivered (FLAG_DELIVERED_DEVON_GOODS)
6. `SlateportCity_ContestLobby`: `SlateportCity_ContestLobby_EventScript_LittleGirl` - Pokeblock Case
7. `SlateportCity_PokemonFanClub`: `SlateportCity_PokemonFanClub_EventScript_ChairmanFirstAssessment` - Fan Club chairman, scarves, Soothe Bell
8. `Route110`: `Route110_EventScript_14FD13` - rival trigger on Route 110 -> battle 14FDE0 (TRAINER_MAY_5/8/2 | BRENDAN_5/8/2) -> 14FEB2 (VAR_ROUTE110_STATE)
9. `Route110_SeasideCyclingRoadNorthEntrance`: `Route110_SeasideCyclingRoadNorthEntrance_EventScript_1634F7` - Cycling Road gate (FLAG_SYS_CYCLING_ROAD)
10. `MauvilleCity`: `MauvilleCity_EventScript_Wally` - Wally + uncle: battle TRAINER_WALLY_2 -> DefeatedWally (Wally moves to Wanda's house)
11. `MauvilleCity_Gym`: `MauvilleCity_Gym_EventScript_Wattson` - Wattson (switch barriers) -> WattsonDefeated (FLAG_BADGE03_GET) -> GiveShockWave
12. `MauvilleCity_BikeShop`: `MauvilleCity_BikeShop_EventScript_YesFar` - Rydel's bike (FLAG_RECEIVED_BIKE)
13. `MauvilleCity_House1`: `MauvilleCity_House1_EventScript_RockSmashHMMan` - HM06 Rock Smash
14. `VerdanturfTown_WandasHouse`: `VerdanturfTown_WandasHouse_EventScript_Wally` - Wally at Wanda's house
15. `RusturfTunnel`: `RusturfTunnel_EventScript_15C7D1` - tunnel opened: reunion, HM04 Strength (Ch2 file, foreign beat)
16. `Route117_PokemonDayCare`: `Route117_PokemonDayCare_MapScript1_15C31F` - Day Care (data/scripts/day_care.inc)
17. `Route110_TrickHouseEntrance`: `Route110_TrickHouseEntrance_EventScript_BeginChallenge` - (optional 3T) Trick House: find the Trick Master, puzzles 1-8 by badge count

Foreign beats this chapter writes into other chapters' files (scene includes):

- `RusturfTunnel` [RusturfTunnel_EventScript_15C7D1 .. RusturfTunnel_EventScript_15C9AB) ~196 lines - Rock Smash opens the tunnel: Wanda + boyfriend reunite, HM04 Strength

Other chapters' beats inside this chapter's files (reserve slots for them):

- Ch6: `MauvilleCity` from `MauvilleCity_EventScript_Wattson` - Wattson: Basement Key, New Mauville, TM24 Thunderbolt
- Ch6: `SlateportCity_Harbor` from `SlateportCity_Harbor_EventScript_CaptSternFerryOrScannerComment` - Scanner from the Abandoned Ship -> Deep Sea Tooth/Scale
- Ch8: `SlateportCity` from `SlateportCity_EventScript_CaptStern` - Capt. Stern on TV / at the harbor after the orb theft
- Ch8: `SlateportCity_Harbor` from `SlateportCity_Harbor_EventScript_ReadyEvilTeamEscapeScene` - Aqua steal Stern's submarine
- Ch8: `SlateportCity_Harbor` from `SlateportCity_Harbor_EventScript_CaptStern` - Stern after the theft ("need Dive")
- Ch9: `SlateportCity_SternsShipyard_1F` from `SlateportCity_SternsShipyard_1F_EventScript_Briney` - Mr. Briney helps build the ferry (after the Mind Badge)
- Ch13: `SlateportCity_Harbor` from `SlateportCity_Harbor_EventScript_FerryAttendant` - S.S. Tidal ferry from Slateport
- Ch13: `SlateportCity_SternsShipyard_1F` from `SlateportCity_SternsShipyard_1F_EventScript_FerryReady` - ferry finished

Maps (52): owned (port the whole file) / touched (warps, flags, foreign beats):

| map | role | status |
|---|---|---|
| MauvilleCity | owned, main path | built (outdoor zone 406) |
| MauvilleCity_Gym | owned, main path | built (room auto, zone 239) |
| Route110 | owned, main path | built (outdoor zone 368) |
| SlateportCity | owned, main path | built (outdoor zone 448) |
| SlateportCity_OceanicMuseum_1F | owned, main path | built (room auto, zone 9) |
| SlateportCity_OceanicMuseum_2F | owned, main path | built (room auto, zone 11) |
| SlateportCity_SternsShipyard_1F | owned, main path | built (room auto, zone 14) |
| MauvilleCity_BikeShop | owned | built (room auto, zone 236) |
| MauvilleCity_GameCorner | owned | built (room auto, zone 237) |
| MauvilleCity_House1 | owned | built (room auto, zone 251) |
| MauvilleCity_House2 | owned | built (room auto, zone 252) |
| MauvilleCity_Mart | owned | built (room auto, zone 273) |
| MauvilleCity_PokemonCenter_1F | owned | built (room center, zone 115) |
| MauvilleCity_PokemonCenter_2F | owned | built (room center, zone 274) |
| Route110_SeasideCyclingRoadNorthEntrance | owned | built (room auto, zone 510) |
| Route110_SeasideCyclingRoadSouthEntrance | owned | built (room auto, zone 511) |
| Route110_TrickHouseCorridor | owned, optional: Trick House | built (room auto, zone 512) |
| Route110_TrickHouseEnd | owned, optional: Trick House | built (room auto, zone 513) |
| Route110_TrickHouseEntrance | owned, optional: Trick House | built (room auto, zone 514) |
| Route110_TrickHousePuzzle1 | owned, optional: Trick House | built (room auto, zone 552) |
| Route110_TrickHousePuzzle2 | owned, optional: Trick House | **NOT BUILT (in no zone list)** |
| Route110_TrickHousePuzzle3 | owned, optional: Trick House | **NOT BUILT (in no zone list)** |
| Route110_TrickHousePuzzle4 | owned, optional: Trick House | **NOT BUILT (in no zone list)** |
| Route110_TrickHousePuzzle5 | owned, optional: Trick House | **NOT BUILT (in no zone list)** |
| Route110_TrickHousePuzzle6 | owned, optional: Trick House | **NOT BUILT (in no zone list)** |
| Route110_TrickHousePuzzle7 | owned, optional: Trick House | **NOT BUILT (in no zone list)** |
| Route110_TrickHousePuzzle8 | owned, optional: Trick House | **NOT BUILT (in no zone list)** |
| Route117 | owned | built (outdoor zone 437) |
| Route117_PokemonDayCare | owned | built (room auto, zone 561) |
| SlateportCity_ContestHall | owned | built (room auto, zone 594) |
| SlateportCity_ContestLobby | owned | built (room auto, zone 595) |
| SlateportCity_Harbor | owned | built (room auto, zone 596) |
| SlateportCity_House1 | owned | built (room auto, zone 614) |
| SlateportCity_House2 | owned | built (room auto, zone 3) |
| SlateportCity_Mart | owned | built (room auto, zone 4) |
| SlateportCity_PokemonCenter_1F | owned | built (room center, zone 435) |
| SlateportCity_PokemonCenter_2F | owned | built (room center, zone 12) |
| SlateportCity_PokemonFanClub | owned | built (room auto, zone 13) |
| SlateportCity_SternsShipyard_2F | owned | built (room auto, zone 22) |
| VerdanturfTown | owned | built (outdoor zone 120) |
| VerdanturfTown_ContestHall | owned | built (room auto, zone 59) |
| VerdanturfTown_ContestLobby | owned | built (room auto, zone 60) |
| VerdanturfTown_FriendshipRatersHouse | owned | built (room auto, zone 61) |
| VerdanturfTown_House | owned | built (room auto, zone 67) |
| VerdanturfTown_Mart | owned | built (room auto, zone 68) |
| VerdanturfTown_PokemonCenter_1F | owned | built (room center, zone 454) |
| VerdanturfTown_PokemonCenter_2F | owned | built (room center, zone 69) |
| VerdanturfTown_WandasHouse | owned | built (room auto, zone 70) |
| NewMauville_Entrance | warp from an owned map, owner Ch6 | **NOT BUILT (cave; zone 132 allocated, no room file)** |
| Route116 | objects/triggers switched by this chapter, owner Ch2 | built (outdoor zone 423) |
| RustboroCity_DevonCorp_3F | objects/triggers switched by this chapter, owner Ch2 | built (room auto, zone 577) |
| RusturfTunnel | foreign beat, optional: HM04 Strength | built (cave room, zone 134: data/interiors/134.json from converter/gen_caves.py) |

Flags used (109; 14 item-ball flags; 74 have this chapter as home):

<details><summary>flag list</summary>

FLAG_BADGE03_GET [engine, C], FLAG_BADGE04_GET [engine, C, home Ch5], FLAG_BADGE05_GET [engine, C, home Ch6], FLAG_BADGE06_GET [engine, C, home Ch7], FLAG_BADGE07_GET [engine, C, home Ch9], FLAG_BADGE08_GET [engine, C, home Ch10], FLAG_DECLINED_BIKE [336], FLAG_DECLINED_WALLY_BATTLE_MAUVILLE [337], FLAG_DEFEATED_LAVARIDGE_GYM [508, home Ch5], FLAG_DEFEATED_MAUVILLE_GYM [338], FLAG_DEFEATED_WALLY_MAUVILLE [339], FLAG_DEFEATED_WALLY_VICTORY_ROAD [988, home Ch11], FLAG_DELIVERED_DEVON_GOODS [340], FLAG_DOCK_REJECTED_DEVON_GOODS [341], FLAG_GOT_TM_THUNDERBOLT_FROM_WATTSON [542, home Ch6], FLAG_HIDDEN_ITEM_1 [engine], FLAG_HIDDEN_ITEM_35 [engine], FLAG_HIDDEN_ITEM_36 [engine], FLAG_HIDDEN_ITEM_37 [engine], FLAG_HIDDEN_ITEM_41 [engine], FLAG_HIDDEN_ITEM_48 [engine], FLAG_HIDE_BOYFRIEND_WANDAS_HOUSE [342], FLAG_HIDE_BRINEY_SLATEPORT_SHIPYARD [755, home Ch9], FLAG_HIDE_CONTEST_REPORTER_SLATEPORT [343], FLAG_HIDE_CONTEST_REPORTER_VERDANTURF [344], FLAG_HIDE_DEVON_EMPLOYEE_ROUTE116 [345], FLAG_HIDE_EMPLOYEE_DEVON_CORP_3F [264, home Ch2], FLAG_HIDE_EVIL_TEAM_LEADER_OCEANIC_MUSEUM_2F [346], FLAG_HIDE_EVIL_TEAM_OCEANIC_MUSEUM [347], FLAG_HIDE_EVIL_TEAM_ROUTE110 [352], FLAG_HIDE_EVIL_TEAM_SLATEPORT [355], FLAG_HIDE_GABBY_AND_TY_SLATEPORT [656, home Ch8], FLAG_HIDE_GIRLFRIEND_WANDAS_HOUSE [357], FLAG_HIDE_GRUNT_1_OCEANIC_MUSEUM_2F [361], FLAG_HIDE_GRUNT_1_SLATEPORT_HARBOR [663, home Ch8], FLAG_HIDE_GRUNT_2_OCEANIC_MUSEUM_2F [362], FLAG_HIDE_GRUNT_2_SLATEPORT_HARBOR [665, home Ch8], FLAG_HIDE_OCEANIC_MUSEUM_VISITORS [363], FLAG_HIDE_RIVAL_ON_BIKE_ROUTE110 [364], FLAG_HIDE_RIVAL_ROUTE110 [365], FLAG_HIDE_SCARED_GRUNT_OCEANIC_MUSEUM [366], FLAG_HIDE_SS_TIDAL_SLATEPORT_HARBOR [367], FLAG_HIDE_STERN_OCEANIC_MUSEUM_2F [368], FLAG_HIDE_STERN_SLATEPORT [677, home Ch8], FLAG_HIDE_STERN_SLATEPORT_HARBOR [678, home Ch8], FLAG_HIDE_SUBMARINE_SHADOW_SLATEPORT_HARBOR [681, home Ch8], FLAG_HIDE_TM_SALESMAN_SLATEPORT [467, home Ch4], FLAG_HIDE_TRICKMASTER_ENTRANCE [375], FLAG_HIDE_TRICK_HOUSE_END_MAN [376], FLAG_HIDE_WALLY_FATHER_MAUVILLE [377], FLAG_HIDE_WALLY_FATHER_WANDAS_HOUSE [378], FLAG_HIDE_WALLY_MAUVILLE [381], FLAG_HIDE_WALLY_WANDAS_HOUSE [382], FLAG_HIDE_WATTSON_MAUVILLE [383], FLAG_HIDE_WATTSON_MAUVILLE_GYM [384], FLAG_HIDE_WORKERS_SLATEPORT_HARBOR [682, home Ch8], FLAG_LANDMARK_POKEMON_DAYCARE [385, C], FLAG_LANDMARK_TRICK_HOUSE [386, C], FLAG_MAUVILLE_GYM_BARRIERS_STATE [387], FLAG_OCEANIC_MUSEUM_MET_REPORTER [388], FLAG_PENDING_DAYCARE_EGG [389, C], FLAG_RECEIVED_20_COINS [390], FLAG_RECEIVED_BIKE [391], FLAG_RECEIVED_BLUE_SCARF [392], FLAG_RECEIVED_COIN_CASE [393], FLAG_RECEIVED_GREEN_SCARF [394], FLAG_RECEIVED_HM04 [395], FLAG_RECEIVED_HM06 [404], FLAG_RECEIVED_PINK_SCARF [405], FLAG_RECEIVED_POKEBLOCK_CASE [406], FLAG_RECEIVED_RED_SCARF [407], FLAG_RECEIVED_SECRET_POWER [485, C, home Ch4], FLAG_RECEIVED_SOOTHE_BELL [408], FLAG_RECEIVED_STARTER_DOLL [409], FLAG_RECEIVED_TM41 [410], FLAG_RECEIVED_TM45 [411], FLAG_RECEIVED_TM46 [412], FLAG_RECEIVED_TM_SHOCK_WAVE [413], FLAG_RECEIVED_YELLOW_SCARF [414], FLAG_RUSTURF_TUNNEL_OPENED [415, C], FLAG_SYS_CYCLING_ROAD [416, C], FLAG_SYS_GAME_CLEAR [engine 2400, C, home Ch1], FLAG_SYS_HIPSTER_MEET [418, C], FLAG_SYS_POKEDEX_GET [2070, C, home Ch1], FLAG_SYS_TV_START [419, C], FLAG_TRICK_HOUSE_PUZZLE_7_SWITCH_1 [421], FLAG_TRICK_HOUSE_PUZZLE_7_SWITCH_2 [422], FLAG_TRICK_HOUSE_PUZZLE_7_SWITCH_3 [423], FLAG_TRICK_HOUSE_PUZZLE_7_SWITCH_4 [424], FLAG_TRICK_HOUSE_PUZZLE_7_SWITCH_5 [425], FLAG_TV_EXPLAINED [426], FLAG_VISITED_MAUVILLE_CITY [2071, C], FLAG_VISITED_SLATEPORT_CITY [427, C], FLAG_VISITED_VERDANTURF_TOWN [428, C], FLAG_WALLY_SPEECH [429]

</details>

Vars used (29): VAR_CABLE_CLUB_STATE [0x4057, home Ch1], VAR_CONTEST_LOCATION [0x4072], VAR_CYCLING_CHALLENGE_STATE [0x4075, C], VAR_LINK_CONTEST_ROOM_STATE [0x4076], VAR_MAUVILLE_GYM_STATE [0x4077], VAR_NEW_MAUVILLE_STATE [0x40B1, home Ch6], VAR_PETALBURG_GYM_STATE [0x4059, home Ch1], VAR_ROUTE110_STATE [0x4079], VAR_RUSTURF_TUNNEL_STATE [0x406B, C, home Ch2], VAR_SLATEPORT_FAN_CLUB_STATE [0x407A], VAR_SLATEPORT_HARBOR_STATE [0x40CC, home Ch8], VAR_SLATEPORT_MUSEUM_1F_STATE [0x407B], VAR_SLATEPORT_STATE [0x40CD, home Ch8], VAR_STARTER_MON [0x4030, C, home Ch1], VAR_TRICK_HOUSE_ENTRANCE_STATE [0x407C], VAR_TRICK_HOUSE_ENTRANCE_STATE_2 [0x407D], VAR_TRICK_HOUSE_ENTRANCE_STATE_3 [0x407E], VAR_TRICK_HOUSE_PRIZE_PICKUP [0x407F], VAR_TRICK_HOUSE_PUZZLE_1_STATE [0x4080], VAR_TRICK_HOUSE_PUZZLE_2_STATE [0x4081], VAR_TRICK_HOUSE_PUZZLE_3_STATE [0x4082], VAR_TRICK_HOUSE_PUZZLE_4_STATE [0x4083], VAR_TRICK_HOUSE_PUZZLE_5_STATE [0x4084], VAR_TRICK_HOUSE_PUZZLE_6_STATE [0x4086], VAR_TRICK_HOUSE_PUZZLE_7_STATE [0x4087], VAR_TRICK_HOUSE_PUZZLE_7_STATE_2 [0x4088], VAR_TRICK_HOUSE_PUZZLE_8_STATE [0x4089], VAR_TRICK_HOUSE_ROOMS_COMPLETED [0x408B], VAR_TRICK_HOUSE_STATE [0x408C]

Reads ids written by other chapters:

- from Ch1: FLAG_SYS_POKEDEX_GET, VAR_CABLE_CLUB_STATE, VAR_PETALBURG_GYM_STATE
- from Ch2: VAR_PETALBURG_GYM_STATE
- from Ch4: FLAG_HIDE_CONTEST_REPORTER_SLATEPORT, FLAG_HIDE_CONTEST_REPORTER_VERDANTURF, FLAG_HIDE_TM_SALESMAN_SLATEPORT, FLAG_RECEIVED_SECRET_POWER
- from Ch5: FLAG_BADGE04_GET, FLAG_DEFEATED_LAVARIDGE_GYM, FLAG_HIDE_WALLY_WANDAS_HOUSE, VAR_PETALBURG_GYM_STATE
- from Ch6: FLAG_BADGE05_GET, FLAG_GOT_TM_THUNDERBOLT_FROM_WATTSON, FLAG_HIDE_WATTSON_MAUVILLE, FLAG_HIDE_WATTSON_MAUVILLE_GYM, VAR_NEW_MAUVILLE_STATE, VAR_PETALBURG_GYM_STATE
- from Ch7: FLAG_BADGE06_GET
- from Ch8: FLAG_HIDE_GABBY_AND_TY_SLATEPORT, FLAG_HIDE_GRUNT_1_SLATEPORT_HARBOR, FLAG_HIDE_GRUNT_2_SLATEPORT_HARBOR, FLAG_HIDE_STERN_SLATEPORT, FLAG_HIDE_STERN_SLATEPORT_HARBOR, FLAG_HIDE_SUBMARINE_SHADOW_SLATEPORT_HARBOR, FLAG_HIDE_WORKERS_SLATEPORT_HARBOR, VAR_SLATEPORT_HARBOR_STATE, VAR_SLATEPORT_STATE
- from Ch9: FLAG_BADGE07_GET, FLAG_HIDE_BRINEY_SLATEPORT_SHIPYARD, FLAG_HIDE_WORKERS_SLATEPORT_HARBOR
- from Ch10: FLAG_BADGE08_GET
- from Ch11: FLAG_DEFEATED_WALLY_VICTORY_ROAD, FLAG_HIDE_BRINEY_SLATEPORT_SHIPYARD, FLAG_HIDE_SS_TIDAL_SLATEPORT_HARBOR

Trainers: TRAINER_ABIGAIL_1, TRAINER_ALAN, TRAINER_ALEXIS, TRAINER_ANNA_AND_MEG_1, TRAINER_ANTHONY, TRAINER_BEN, TRAINER_BENJAMIN_1, TRAINER_BENNY, TRAINER_BRENDAN_2, TRAINER_BRENDAN_5, TRAINER_BRENDAN_8, TRAINER_CORA, TRAINER_DALE, TRAINER_DEREK, TRAINER_DYLAN_1, TRAINER_EDDIE, TRAINER_EDWARD, TRAINER_EDWIN_1, TRAINER_ELAINE, TRAINER_GEORGIA, TRAINER_ISAAC_1, TRAINER_ISABEL_1, TRAINER_JACLYN, TRAINER_JACOB, TRAINER_JASMINE, TRAINER_JILL, TRAINER_JOSHUA, TRAINER_JUSTIN, TRAINER_KIRK, TRAINER_LEROY, TRAINER_LYDIA_1, TRAINER_MARIA_1, TRAINER_MARTHA, TRAINER_MAY_2, TRAINER_MAY_5, TRAINER_MAY_8, TRAINER_MUSEUM_2F_GRUNT_1, TRAINER_MUSEUM_2F_GRUNT_2, TRAINER_PATRICIA, TRAINER_PAUL, TRAINER_ROBIN, TRAINER_SALLY, TRAINER_SEBASTIAN, TRAINER_SHAWN, TRAINER_SOPHIA, TRAINER_TED, TRAINER_TIMMY, TRAINER_VINCENT, TRAINER_VIVIAN, TRAINER_WALLY_2, TRAINER_WATTSON, TRAINER_YUJI

- Note: Owns SlateportCity / SlateportCity_Harbor / SternsShipyard_1F: their later beats (Ch6 Scanner trade, Ch8 Aqua sub theft, Ch9 Briney at the shipyard, Ch13 ferry) are scene includes.
- Note: Owns MauvilleCity: Wattson's New Mauville request (Basement Key, TM24) is a Ch6 beat.
- Note: Contest lobbies/halls (Slateport, Verdanturf): NPCs only; the contest system itself is the optional "Contests" block (see S).

### Ch4 - Route 111-115, Fiery Path, Fallarbor, Meteor Falls (Prof. Cozmo, Meteorite)

**BLOCKED** - blocked by: MeteorFalls_1F_1R

Size: 2322 script lines in 398 labels (+755 text lines in owned maps); 62 trainerbattle commands, 42 unique trainers; 77 flags, 9 vars.

- optional block **Meteor Falls back rooms**: 39 lines, 6 trainerbattle cmds in owned files; NOT BUILT: MeteorFalls_1F_2R, MeteorFalls_B1F_1R, MeteorFalls_B1F_2R

Story beats (in order; `map: label`):

1. `Route111`: `Route111_EventScript_1501F3` - Winstrate family gauntlet (4 battles) -> Macho Brace
2. `Route112`: `Route112_MapScript1_150508` - Route 112: grunts block the cable car (FLAG_HIDE_GRUNTS_BLOCKING_CABLE_CAR)
3. `FieryPath`: `FieryPath_MapScript1_15D31E` - Fiery Path (the only way north)
4. `Route113_GlassWorkshop`: `Route113_GlassWorkshop_EventScript_163565` - Glass Workshop, Soot Sack, ash flutes (VAR_ASH_GATHER_COUNT)
5. `FallarborTown_House1`: `FallarborTown_CozmosHouse_EventScript_ProfCozmo` - Prof. Cozmo taken to Meteor Falls
6. `FallarborTown_PokemonCenter_1F`: `FallarborTown_PokemonCenter_1F_EventScript_LanetteExited` - Lanette in the Center
7. `Route114_LanettesHouse`: `Route114_LanettesHouse_EventScript_15C262` - Lanette's PC (FLAG_SYS_PC_LANETTE)
8. `Route114_FossilManiacsHouse`: `Route114_FossilManiacsHouse_EventScript_15C1C3` - TM28 Dig
9. `MeteorFalls_1F_1R`: `MeteorFalls_1F_1R_EventScript_15C49C` - Aqua take the Meteorite, Magma chase them (VAR_METEOR_FALLS_STATE; frees the cable car)
10. `MeteorFalls_1F_1R`: `MeteorFalls_1F_1R_EventScript_15C656` - Prof. Cozmo (FLAG_MET_PROF_COSMO)
11. `Route111`: `Route111_EventScript_150023` - (after Go-Goggles) desert fossil choice -> Devon Corp 2F revival (foreign beat in Ch2 file)

Foreign beats this chapter writes into other chapters' files (scene includes):

- `RustboroCity_DevonCorp_2F` [RustboroCity_DevonCorp_2F_EventScript_FossilScientist .. end of file) ~106 lines - fossil revival (Root/Claw fossil from the Route 111 desert)

Other chapters' beats inside this chapter's files (reserve slots for them):

- Ch5: `FallarborTown_House1` from `FallarborTown_CozmosHouse_EventScript_PlayerHasMeteorite` - return the Meteorite to Cozmo: TM27 Return

Maps (34): owned (port the whole file) / touched (warps, flags, foreign beats):

| map | role | status |
|---|---|---|
| FallarborTown | owned, main path | built (outdoor zone 6) |
| FieryPath | owned, main path | built (cave room, zone 117: data/interiors/117.json from converter/gen_caves.py) |
| MeteorFalls_1F_1R | owned, main path | **NOT BUILT (cave; zone 128 allocated, no room file)** |
| Route111 | owned, main path | built (outdoor zone 370) |
| Route112 | owned, main path | built (outdoor zone 374) |
| Route113 | owned, main path | built (outdoor zone 378) |
| Route114 | owned, main path | built (outdoor zone 383) |
| FallarborTown_ContestHall | owned | built (room auto, zone 80) |
| FallarborTown_ContestLobby | owned | built (room auto, zone 93) |
| FallarborTown_House1 | owned | built (room auto, zone 97) |
| FallarborTown_House2 | owned | built (room auto, zone 104) |
| FallarborTown_Mart | owned | built (room auto, zone 105) |
| FallarborTown_PokemonCenter_1F | owned | built (room center, zone 41) |
| FallarborTown_PokemonCenter_2F | owned | built (room center, zone 106) |
| MeteorFalls_1F_2R | owned, optional: Meteor Falls back rooms | **NOT BUILT (cave; zone 129 allocated, no room file)** |
| MeteorFalls_B1F_1R | owned, optional: Meteor Falls back rooms | **NOT BUILT (cave; zone 130 allocated, no room file)** |
| MeteorFalls_B1F_2R | owned, optional: Meteor Falls back rooms | **NOT BUILT (cave; zone 131 allocated, no room file)** |
| Route111_OldLadysRestStop | owned | built (room auto, zone 553) |
| Route111_WinstrateFamilysHouse | owned | built (room auto, zone 554) |
| Route112_CableCarStation | owned | built (room auto, zone 555) |
| Route113_GlassWorkshop | owned | built (room auto, zone 556) |
| Route114_FossilManiacsHouse | owned | built (room auto, zone 557) |
| Route114_FossilManiacsTunnel | owned | built (room auto, zone 558) |
| Route114_LanettesHouse | owned | built (room auto, zone 559) |
| Route115 | owned | built (outdoor zone 387) |
| DesertRuins | warp from an owned map, owner Ch12 | **NOT BUILT (cave; zone 116 allocated, no room file)** |
| JaggedPass | warp from an owned map, owner Ch5 | **in progress (standalone map, zone 18: built in the standalone agent's test ROM, proof work/agents/standalone/proofs/JaggedPass.png; not in the main build yet, hoenn_standalone.json "build" is empty)** |
| LilycoveCity_ContestLobby | objects/triggers switched by this chapter, owner Ch8 | built (room auto, zone 161) |
| Route118 | objects/triggers switched by this chapter, owner Ch7 | built (outdoor zone 446) |
| Route120 | objects/triggers switched by this chapter, owner Ch7 | built (outdoor zone 474) |
| RustboroCity_DevonCorp_2F | foreign beat | built (room auto, zone 576) |
| SlateportCity | objects/triggers switched by this chapter, owner Ch3 | built (outdoor zone 448) |
| SlateportCity_ContestLobby | objects/triggers switched by this chapter, owner Ch3 | built (room auto, zone 595) |
| VerdanturfTown_ContestLobby | objects/triggers switched by this chapter, owner Ch3 | built (room auto, zone 60) |

Flags used (77; 19 item-ball flags; 51 have this chapter as home):

<details><summary>flag list</summary>

FLAG_CONTEST_SKETCH_CREATED [447], FLAG_DAILY_RECEIVED_BERRY_ROUTE111 [2745], FLAG_DAILY_RECEIVED_BERRY_ROUTE114 [2746], FLAG_DEFEATED_EVIL_TEAM_MT_CHIMNEY [507, home Ch5], FLAG_HIDDEN_ITEM_1E [engine], FLAG_HIDDEN_ITEM_2 [engine], FLAG_HIDDEN_ITEM_2A [engine], FLAG_HIDDEN_ITEM_3 [engine], FLAG_HIDDEN_ITEM_38 [engine], FLAG_HIDDEN_ITEM_39 [engine], FLAG_HIDDEN_ITEM_4 [engine], FLAG_HIDDEN_ITEM_61 [engine], FLAG_HIDDEN_ITEM_FALLARBOR_TOWN_NUGGET [engine], FLAG_HIDE_AZURILL_FALLARBOR [448], FLAG_HIDE_CLAW_FOSSIL [449], FLAG_HIDE_CONTEST_REPORTER_FALLARBOR [450], FLAG_HIDE_CONTEST_REPORTER_SLATEPORT [343, home Ch3], FLAG_HIDE_CONTEST_REPORTER_VERDANTURF [344, home Ch3], FLAG_HIDE_GABBY_AND_TY_ROUTE111_1 [451], FLAG_HIDE_GABBY_AND_TY_ROUTE111_2 [452], FLAG_HIDE_GABBY_AND_TY_ROUTE111_3 [453], FLAG_HIDE_GABBY_AND_TY_ROUTE118_1 [454], FLAG_HIDE_GABBY_AND_TY_ROUTE118_2 [455], FLAG_HIDE_GABBY_AND_TY_ROUTE118_3 [456], FLAG_HIDE_GABBY_AND_TY_ROUTE120_1 [457], FLAG_HIDE_GABBY_AND_TY_ROUTE120_2 [459], FLAG_HIDE_GRUNTS_BLOCKING_CABLE_CAR [461], FLAG_HIDE_GRUNTS_METEOR_FALLS_1F [462], FLAG_HIDE_LANETTE [2073], FLAG_HIDE_LANETTE_FALLARBOR [2072], FLAG_HIDE_LILYCOVE_CONTEST_HALL_REPORTER [463], FLAG_HIDE_OTHER_TEAM_METEOR_FALLS_1F [464], FLAG_HIDE_PROF_COSMO_FALLARBOR [513, home Ch5], FLAG_HIDE_PROF_COSMO_METEOR_FALLS [514, home Ch5], FLAG_HIDE_ROOT_FOSSIL [465], FLAG_HIDE_SECRET_POWER_MAN [466], FLAG_HIDE_TM_SALESMAN_SLATEPORT [467], FLAG_HIDE_VICKI_WINSTRATE [468], FLAG_HIDE_VICTORIA_WINSTRATE [469], FLAG_HIDE_VICTOR_WINSTRATE [470], FLAG_HIDE_VIVI_WINSTRATE [471], FLAG_LANDMARK_FIERY_PATH [472, C], FLAG_LANDMARK_FOSSIL_MANIACS_HOUSE [473, C], FLAG_LANDMARK_GLASS_WORKSHOP [474, C], FLAG_LANDMARK_LANETTES_HOUSE [476, C], FLAG_LANDMARK_OLD_LADY_REST_SHOP [477, C], FLAG_LANDMARK_WINSTRATE_FAMILY [478, C], FLAG_MET_PROF_COSMO [479], FLAG_RECEIVED_DOLL_LANETTE [481], FLAG_RECEIVED_FOSSIL_MON [482], FLAG_RECEIVED_MACHO_BRACE [483], FLAG_RECEIVED_SECRET_POWER [485, C], FLAG_RECEIVED_TM05 [486], FLAG_RECEIVED_TM28 [487], FLAG_RECEIVED_TM_RETURN [522, home Ch5], FLAG_REGI_DOORS_OPENED [1069, home Ch12], FLAG_SYS_PC_LANETTE [488, C], FLAG_VISITED_FALLARBOR_TOWN [489, C]

</details>

Vars used (9): VAR_ASH_GATHER_COUNT [0x4097, C], VAR_CABLE_CAR_STATION_STATE [0x4099], VAR_CONTEST_LOCATION [0x4072, home Ch3], VAR_FOSSIL_RESURRECTION_STATE [0x4069, home Ch2], VAR_GLASS_WORKSHOP_STATE [0x409A], VAR_JAGGED_PASS_ASH_WEATHER [0x409B], VAR_LINK_CONTEST_ROOM_STATE [0x4076, home Ch3], VAR_METEOR_FALLS_STATE [0x409C], VAR_WHICH_FOSSIL_REVIVED [0x409D]

Reads ids written by other chapters:

- from Ch2: VAR_FOSSIL_RESURRECTION_STATE
- from Ch5: FLAG_DEFEATED_EVIL_TEAM_MT_CHIMNEY, FLAG_HIDE_PROF_COSMO_FALLARBOR, FLAG_HIDE_PROF_COSMO_METEOR_FALLS, FLAG_RECEIVED_TM_RETURN, VAR_CABLE_CAR_STATION_STATE
- from Ch12: FLAG_REGI_DOORS_OPENED

Trainers: TRAINER_514, TRAINER_BECKY, TRAINER_BERNIE_1, TRAINER_BRICE, TRAINER_BROOKE_1, TRAINER_CAROL, TRAINER_CLAUDE, TRAINER_CLIFF, TRAINER_CYNDY_1, TRAINER_DAISUKE, TRAINER_DILLON, TRAINER_DREW, TRAINER_DUSTY_1, TRAINER_GABBY_AND_TY_1, TRAINER_GABBY_AND_TY_4, TRAINER_HEIDI, TRAINER_IRENE, TRAINER_JOHN_AND_JAY_1, TRAINER_KOICHI, TRAINER_LAO_1, TRAINER_LARRY, TRAINER_LENNY, TRAINER_LUCAS_1, TRAINER_LUNG, TRAINER_MADELINE_1, TRAINER_NANCY, TRAINER_NEAL, TRAINER_NICOLAS_1, TRAINER_NOB_1, TRAINER_NOLAN, TRAINER_SHANE, TRAINER_STEVE_1, TRAINER_TIMOTHY_1, TRAINER_TORI_AND_TIA, TRAINER_TRAVIS, TRAINER_TRENT_1, TRAINER_TYRA_AND_IVY, TRAINER_VICKY, TRAINER_VICTOR, TRAINER_VICTORIA, TRAINER_VIVI, TRAINER_WILTON_1

- Note: The Route 111 desert (sandstorm, fossils, Desert Ruins entrance) needs the Go-Goggles from Ch5; port it here, gated by FLAG_RECEIVED_GO_GOGGLES.
- Note: Owns Route112_CableCarStation: the cable car ride itself is Ch5's first beat (plain content, no foreign range needed).

### Ch5 - Cable car, Mt. Chimney (Aqua vs Magma), Jagged Pass, Lavaridge: Flannery

**UNBLOCKED** | in progress: MtChimney, JaggedPass | badge: Heat Badge (4)

Size: 1200 script lines in 174 labels (+417 text lines in owned maps); 22 trainerbattle commands, 16 unique trainers; 23 flags, 4 vars.

Story beats (in order; `map: label`):

1. `Route112_CableCarStation`: `Route112_CableCarStation_EventScript_15C068` - cable car up (VAR_CABLE_CAR_STATION_STATE; Ch4 file, plain content) _(file owned by Ch4)_
2. `MtChimney`: `MtChimney_EventScript_15D110` - summit: Aqua grunts vs Magma grunts, 2 grunt battles (take the `.ifdef SAPPHIRE` branches)
3. `data/scripts/magma_chimney.inc`: `MtChimney_EventScript_1B2C95` - the other team's leader (Maxie in Sapphire) asks you to stop them (FLAG_EVIL_LEADER_PLEASE_STOP)
4. `data/scripts/magma_chimney.inc`: `MtChimney_EventScript_1B2CCB` - Archie at the meteorite machine: battle, FLAG_DEFEATED_EVIL_TEAM_MT_CHIMNEY, teams leave, Cozmo goes home
5. `MtChimney`: `MtChimney_EventScript_15D17D` - Meteorite from the machine
6. `JaggedPass`: `JaggedPass_MapScript1_15D274` - Jagged Pass down (ash weather VAR_JAGGED_PASS_ASH_WEATHER, trainers)
7. `LavaridgeTown`: `LavaridgeTown_EventScript_RivalGiveGoGoggles` - rival gives the Go-Goggles (VAR_LAVARIDGE_RIVAL_STATE)
8. `LavaridgeTown`: `LavaridgeTown_EventScript_EggWoman` - Wynaut egg
9. `LavaridgeTown_Gym_1F`: `LavaridgeTown_Gym_1F_EventScript_Flannery` - Flannery -> FlanneryDefeated (FLAG_BADGE04_GET) -> GiveOverheat
10. `FallarborTown_House1`: `FallarborTown_CozmosHouse_EventScript_PlayerHasMeteorite` - Meteorite back to Cozmo: TM27 Return (Ch4 file, foreign beat)

Foreign beats this chapter writes into other chapters' files (scene includes):

- `FallarborTown_House1` [FallarborTown_CozmosHouse_EventScript_PlayerHasMeteorite .. FallarborTown_CozmosHouse_EventScript_CozmosWife) ~31 lines - return the Meteorite to Cozmo: TM27 Return

Maps (15): owned (port the whole file) / touched (warps, flags, foreign beats):

| map | role | status |
|---|---|---|
| JaggedPass | owned, main path | **in progress (standalone map, zone 18: built in the standalone agent's test ROM, proof work/agents/standalone/proofs/JaggedPass.png; not in the main build yet, hoenn_standalone.json "build" is empty)** |
| LavaridgeTown | owned, main path | built (outdoor zone 62) |
| LavaridgeTown_Gym_1F | owned, main path | built (room auto, zone 145) |
| LavaridgeTown_Gym_B1F | owned, main path | built (room auto, zone 148) |
| MtChimney | owned, main path | **in progress (standalone map, zone 19: built in the standalone agent's test ROM, proof work/agents/standalone/proofs/MtChimney.png; not in the main build yet, hoenn_standalone.json "build" is empty)** |
| MtChimney_CableCarStation | owned, main path | built (room auto, zone 340) |
| LavaridgeTown_HerbShop | owned | built (room auto, zone 149) |
| LavaridgeTown_House | owned | built (room auto, zone 152) |
| LavaridgeTown_Mart | owned | built (room auto, zone 153) |
| LavaridgeTown_PokemonCenter_1F | owned | built (room center, zone 99) |
| LavaridgeTown_PokemonCenter_2F | owned | built (room center, zone 156) |
| FallarborTown_House1 | foreign beat | built (room auto, zone 97) |
| MeteorFalls_1F_1R | objects/triggers switched by this chapter, owner Ch4 | **NOT BUILT (cave; zone 128 allocated, no room file)** |
| Route112 | warp from an owned map, owner Ch4 | built (outdoor zone 374) |
| VerdanturfTown_WandasHouse | objects/triggers switched by this chapter, owner Ch3 | built (room auto, zone 70) |

Flags used (23; 1 item-ball flags; 21 have this chapter as home):

<details><summary>flag list</summary>

FLAG_BADGE04_GET [engine, C], FLAG_DEFEATED_EVIL_TEAM_MT_CHIMNEY [507], FLAG_DEFEATED_LAVARIDGE_GYM [508], FLAG_EVIL_LEADER_PLEASE_STOP [509], FLAG_HIDDEN_ITEM_4C [engine], FLAG_HIDDEN_ITEM_4D [engine], FLAG_HIDDEN_ITEM_LAVARIDGE_TOWN_ICE_HEAL [engine], FLAG_HIDE_EVIL_TEAM_MT_CHIMNEY [510], FLAG_HIDE_MT_CHIMNEY_PEOPLE [511], FLAG_HIDE_OTHER_TEAM_MT_CHIMNEY [512], FLAG_HIDE_PROF_COSMO_FALLARBOR [513], FLAG_HIDE_PROF_COSMO_METEOR_FALLS [514], FLAG_HIDE_RIVAL_LAVARIDGE_1 [515], FLAG_HIDE_RIVAL_LAVARIDGE_2 [516], FLAG_HIDE_WALLY_WANDAS_HOUSE [382, home Ch3], FLAG_RECEIVED_CHARCOAL [517], FLAG_RECEIVED_GO_GOGGLES [518], FLAG_RECEIVED_LAVARIDGE_EGG [519], FLAG_RECEIVED_METEORITE [520], FLAG_RECEIVED_TM_OVERHEAT [521], FLAG_RECEIVED_TM_RETURN [522], FLAG_VISITED_LAVARIDGE_TOWN [523, C]

</details>

Vars used (4): VAR_CABLE_CAR_STATION_STATE [0x4099, home Ch4], VAR_JAGGED_PASS_ASH_WEATHER [0x409B, home Ch4], VAR_LAVARIDGE_RIVAL_STATE [0x40A7], VAR_PETALBURG_GYM_STATE [0x4059, home Ch1]

Reads ids written by other chapters:

- from Ch1: VAR_PETALBURG_GYM_STATE
- from Ch2: VAR_PETALBURG_GYM_STATE
- from Ch3: VAR_PETALBURG_GYM_STATE
- from Ch4: VAR_CABLE_CAR_STATION_STATE, VAR_JAGGED_PASS_ASH_WEATHER
- from Ch6: VAR_PETALBURG_GYM_STATE

Trainers: TRAINER_ANDY, TRAINER_AXLE, TRAINER_COLE, TRAINER_DIANA_1, TRAINER_ERIC, TRAINER_ETHAN_1, TRAINER_FLANNERY, TRAINER_MELISSA, TRAINER_MT_CHIMNEY_GRUNT_1, TRAINER_MT_CHIMNEY_GRUNT_2, TRAINER_MT_CHIMNEY_GRUNT_3, TRAINER_SADIE, TRAINER_SHEILA, TRAINER_SHELBY_1, TRAINER_SHIRLEY, TRAINER_ZANE

### Ch6 - Norman, Surf, and the Surf side areas (Routes 105-108, Abandoned Ship, New Mauville)

**UNBLOCKED** | badge: Balance Badge (5)

Size: 1489 script lines in 237 labels (+224 text lines in owned maps); 30 trainerbattle commands, 25 unique trainers; 51 flags, 3 vars.

- optional block **Abandoned Ship (Route 108; hidden floor needs Dive)**: 382 lines, 6 trainerbattle cmds in owned files; NOT BUILT: AbandonedShip_Deck, AbandonedShip_CaptainsOffice, AbandonedShip_Corridors_1F, AbandonedShip_Corridors_B1F, AbandonedShip_Rooms_1F, AbandonedShip_Rooms_B1F, AbandonedShip_Rooms2_1F, AbandonedShip_Rooms2_B1F, AbandonedShip_Room_B1F, AbandonedShip_HiddenFloorCorridors, AbandonedShip_HiddenFloorRooms, AbandonedShip_Underwater1, AbandonedShip_Underwater2
- optional block **New Mauville (Wattson's request)**: 236 lines, 0 trainerbattle cmds in owned files; NOT BUILT: NewMauville_Entrance, NewMauville_Inside

Story beats (in order; `map: label`):

1. `PetalburgCity_Gym`: `PetalburgCity_Gym_EventScript_Norman` - Norman with 4 badges -> gym rooms (7 trainers, sliding doors) (Ch1 file) _(file owned by Ch1)_
2. `PetalburgCity_Gym`: `PetalburgCity_Gym_EventScript_NormanBattle` - TRAINER_NORMAN -> FLAG_BADGE05_GET, shows Wattson in Mauville + Sludge Bomb man -> GiveFacade2
3. `PetalburgCity_WallysHouse`: `PetalburgCity_WallysHouse_EventScript_WallysDad` - Wally's dad: HM03 Surf (GiveHMSurf, FLAG_RECEIVED_HM_SURF)
4. `data/scripts/players_house.inc`: `LittlerootTown_BrendansHouse_1F_EventScript_1B6C3D` - Mom: Amulet Coin (Ch0 file)
5. `MauvilleCity`: `MauvilleCity_EventScript_Wattson` - Wattson: Basement Key (Ch3 file)
6. `NewMauville_Entrance`: `NewMauville_Entrance_EventScript_15E4DC` - New Mauville entrance (VAR_NEW_MAUVILLE_STATE)
7. `NewMauville_Inside`: `NewMauville_Inside_EventScript_15E876` - generator switched off
8. `MauvilleCity`: `MauvilleCity_EventScript_CompletedNewMauville` - TM24 Thunderbolt (Ch3 file)
9. `AbandonedShip_Corridors_B1F`: `AbandonedShip_Corridors_B1F_EventScript_StorageRoomDoor` - Abandoned Ship: Storage Key, Scanner (hidden floor via Dive)
10. `SlateportCity_Harbor`: `SlateportCity_Harbor_EventScript_AskToTradeScanner` - Stern trades the Scanner (Ch3 file)
11. `Route105`: `Route105_EventScript_14F2BB` - Surf trainers on Routes 105/107/108

Foreign beats this chapter writes into other chapters' files (scene includes):

- `PetalburgCity_Gym` [PetalburgCity_Gym_EventScript_NormanPostBattle .. PetalburgCity_Gym_EventScript_GymGuide) ~569 lines - Norman battle, Facade TM, gym rooms, doors, 7 gym trainers
- `data/scripts/players_house.inc` [LittlerootTown_BrendansHouse_1F_EventScript_1B6C3D .. LittlerootTown_BrendansHouse_1F_EventScript_1B6C72) ~10 lines - Mom gives the Amulet Coin after the Balance Badge
- `DewfordTown_Hall` [DewfordTown_Hall_EventScript_SludgeBombMan .. end of file) ~16 lines - Sludge Bomb man (appears after Norman)
- `MauvilleCity` [MauvilleCity_EventScript_Wattson .. end of file) ~30 lines - Wattson: Basement Key, New Mauville, TM24 Thunderbolt
- `SlateportCity_Harbor` [SlateportCity_Harbor_EventScript_CaptSternFerryOrScannerComment .. end of file) ~65 lines - Scanner from the Abandoned Ship -> Deep Sea Tooth/Scale

Other chapters' beats inside this chapter's files (reserve slots for them):

- Ch11: `PetalburgCity_WallysHouse` from `PetalburgCity_WallysHouse_EventScript_GiveHMSurfAfterVictoryRoad` - Wally's dad after Victory Road

Maps (28): owned (port the whole file) / touched (warps, flags, foreign beats):

| map | role | status |
|---|---|---|
| PetalburgCity_WallysHouse | owned, main path | built (room auto, zone 500) |
| AbandonedShip_CaptainsOffice | owned, optional: Abandoned Ship | **NOT BUILT (cave; zone 71 allocated, no room file)** |
| AbandonedShip_Corridors_1F | owned, optional: Abandoned Ship | **NOT BUILT (cave; zone 72 allocated, no room file)** |
| AbandonedShip_Corridors_B1F | owned, optional: Abandoned Ship | **NOT BUILT (cave; zone 73 allocated, no room file)** |
| AbandonedShip_Deck | owned, optional: Abandoned Ship | **NOT BUILT (cave; zone 74 allocated, no room file)** |
| AbandonedShip_HiddenFloorCorridors | owned, optional: Abandoned Ship | **NOT BUILT (in no zone list)** |
| AbandonedShip_HiddenFloorRooms | owned, optional: Abandoned Ship | **NOT BUILT (in no zone list)** |
| AbandonedShip_Room_B1F | owned, optional: Abandoned Ship | **NOT BUILT (cave; zone 88 allocated, no room file)** |
| AbandonedShip_Rooms2_1F | owned, optional: Abandoned Ship | **NOT BUILT (cave; zone 89 allocated, no room file)** |
| AbandonedShip_Rooms2_B1F | owned, optional: Abandoned Ship | **NOT BUILT (cave; zone 90 allocated, no room file)** |
| AbandonedShip_Rooms_1F | owned, optional: Abandoned Ship | **NOT BUILT (cave; zone 91 allocated, no room file)** |
| AbandonedShip_Rooms_B1F | owned, optional: Abandoned Ship | **NOT BUILT (cave; zone 92 allocated, no room file)** |
| AbandonedShip_Underwater1 | owned, optional: Abandoned Ship | **NOT BUILT (in no zone list)** |
| AbandonedShip_Underwater2 | owned, optional: Abandoned Ship | **NOT BUILT (in no zone list)** |
| NewMauville_Entrance | owned, optional: New Mauville | **NOT BUILT (cave; zone 132 allocated, no room file)** |
| NewMauville_Inside | owned, optional: New Mauville | **NOT BUILT (cave; zone 133 allocated, no room file)** |
| Route105 | owned | built (outdoor zone 331) |
| Route107 | owned | built (outdoor zone 345) |
| Route108 | owned | built (outdoor zone 348) |
| PetalburgCity_Gym | foreign beat, main path | built (room big, zone 452) |
| DewfordTown_Hall | foreign beat | built (room auto, zone 26) |
| IslandCave | warp from an owned map, owner Ch12 | **NOT BUILT (cave; zone 127 allocated, no room file)** |
| LittlerootTown_BrendansHouse_1F | ref, owner Ch0 | built (room hand, zone 390) |
| MauvilleCity | foreign beat | built (outdoor zone 406) |
| MauvilleCity_Gym | objects/triggers switched by this chapter, owner Ch3 | built (room auto, zone 239) |
| PetalburgCity | warp from an owned map, owner Ch1 | built (outdoor zone 439) |
| Route110 | warp from an owned map, owner Ch3 | built (outdoor zone 368) |
| SlateportCity_Harbor | foreign beat | built (room auto, zone 596) |

Flags used (51; 16 item-ball flags; 30 have this chapter as home):

<details><summary>flag list</summary>

FLAG_BADGE05_GET [engine, C], FLAG_DEFEATED_PETALBURG_GYM [540], FLAG_DEFEATED_WALLY_VICTORY_ROAD [988, home Ch11], FLAG_EXCHANGED_SCANNER [541], FLAG_GOT_TM_THUNDERBOLT_FROM_WATTSON [542], FLAG_HIDDEN_ITEM_56 [engine], FLAG_HIDDEN_ITEM_59 [engine], FLAG_HIDDEN_ITEM_ABANDONED_SHIP_RM_1_KEY [engine, C], FLAG_HIDDEN_ITEM_ABANDONED_SHIP_RM_2_KEY [engine, C], FLAG_HIDDEN_ITEM_ABANDONED_SHIP_RM_4_KEY [engine, C], FLAG_HIDDEN_ITEM_ABANDONED_SHIP_RM_6_KEY [engine, C], FLAG_HIDE_PETALBURG_GYM_GUIDE [543], FLAG_HIDE_SLUDGE_BOMB_MAN_DEWFORD_HALL [544], FLAG_HIDE_VOLTORB_1_NEW_MAUVILLE [545], FLAG_HIDE_VOLTORB_2_NEW_MAUVILLE [546], FLAG_HIDE_VOLTORB_3_NEW_MAUVILLE [547], FLAG_HIDE_WATTSON_MAUVILLE [383, home Ch3], FLAG_HIDE_WATTSON_MAUVILLE_GYM [384, home Ch3], FLAG_LANDMARK_ABANDONED_SHIP [548, C], FLAG_LANDMARK_NEW_MAUVILLE [549, C], FLAG_PETALBURG_MART_EXPANDED_ITEMS [550], FLAG_RECEIVED_AMULET_COIN [551], FLAG_RECEIVED_BASEMENT_KEY [552], FLAG_RECEIVED_HM_SURF [553], FLAG_RECEIVED_TM42 [554], FLAG_RECEIVED_TM_SLUDGE_BOMB [555], FLAG_REGI_DOORS_OPENED [1069, home Ch12], FLAG_SYS_CTRL_OBJ_DELETE [556, C], FLAG_SYS_GAME_CLEAR [engine 2400, C, home Ch1], FLAG_THANKED_FOR_PLAYING_WITH_WALLY [557], FLAG_USED_ROOM_1_KEY [558], FLAG_USED_ROOM_2_KEY [559], FLAG_USED_ROOM_4_KEY [560], FLAG_USED_ROOM_6_KEY [561], FLAG_USED_STORAGE_KEY [562]

</details>

Vars used (3): VAR_ENIGMA_BERRY_AVAILABLE [0x40B0, C], VAR_NEW_MAUVILLE_STATE [0x40B1], VAR_PETALBURG_GYM_STATE [0x4059, home Ch1]

Reads ids written by other chapters:

- from Ch1: VAR_PETALBURG_GYM_STATE
- from Ch2: VAR_PETALBURG_GYM_STATE
- from Ch3: VAR_PETALBURG_GYM_STATE
- from Ch5: VAR_PETALBURG_GYM_STATE
- from Ch7: FLAG_SYS_CTRL_OBJ_DELETE
- from Ch8: FLAG_SYS_CTRL_OBJ_DELETE
- from Ch10: FLAG_SYS_CTRL_OBJ_DELETE
- from Ch11: FLAG_DEFEATED_WALLY_VICTORY_ROAD
- from Ch12: FLAG_REGI_DOORS_OPENED, FLAG_SYS_CTRL_OBJ_DELETE
- from Ch13: FLAG_SYS_CTRL_OBJ_DELETE

Trainers: TRAINER_AUSTIN, TRAINER_BERKE, TRAINER_BETH, TRAINER_BEVERLY, TRAINER_CHARLIE, TRAINER_DARRIN, TRAINER_DAWN, TRAINER_DENISE, TRAINER_DUNCAN, TRAINER_FOSTER, TRAINER_GEORGE, TRAINER_JEROME, TRAINER_JODY, TRAINER_LISA_AND_RAY, TRAINER_LOIS_AND_HAL_1, TRAINER_LORI, TRAINER_LUIS, TRAINER_MARY, TRAINER_MATTHEW, TRAINER_MISSY, TRAINER_NORMAN, TRAINER_PARKER, TRAINER_RANDALL, TRAINER_TARA, TRAINER_TONY_1

- Note: Little own script: mostly beats inside Ch1/Ch3 files plus the Surf side areas. Good candidate to merge with Ch12 for one agent.

### Ch7 - Route 118-120, Weather Institute, Fortree: Winona (Kecleon, Devon Scope)

**UNBLOCKED** | badge: Feather Badge (6)

Size: 1667 script lines in 304 labels (+610 text lines in owned maps); 61 trainerbattle commands, 51 unique trainers; 67 flags, 4 vars.

- optional block **Scorched Slab (TM11)**: 6 lines, 0 trainerbattle cmds in owned files; NOT BUILT: ScorchedSlab

Story beats (in order; `map: label`):

1. `Route118`: `Route118_EventScript_150F5E` - Good Rod
2. `Route118`: `Route118_EventScript_151004` - Steven on Route 118 (coord 150FAE/150FCE/150FE4, VAR_ROUTE118_STATE)
3. `Route119_WeatherInstitute_1F`: `Route119_WeatherInstitute_1F_EventScript_163C94` - Aqua take over the Weather Institute (5 grunts on 1F/2F)
4. `Route119_WeatherInstitute_2F`: `Route119_WeatherInstitute_2F_EventScript_163D45` - Aqua admin leaves (VAR_WEATHER_INSTITUTE_STATE)
5. `Route119_WeatherInstitute_2F`: `Route119_WeatherInstitute_2F_EventScript_163D7A` - Castform
6. `Route119`: `Route119_EventScript_1511C5` - rival trigger -> battle 15128D (TRAINER_MAY_6/9/3 | BRENDAN_6/9/3) -> 151362 -> HM02 Fly (151352)
7. `FortreeCity`: `FortreeCity_EventScript_Kecleon` - invisible Kecleon blocks the gym
8. `Route120`: `Route120_EventScript_151908` - Steven: Devon Scope (FLAG_RECEIVED_DEVON_SCOPE); Kecleon battle 15189D
9. `FortreeCity`: `FortreeCity_EventScript_UseDevonScope` - Devon Scope: Kecleon flees (FLAG_KECLEON_FLED_FORTREE)
10. `FortreeCity_Gym`: `FortreeCity_Gym_EventScript_Winona` - Winona -> WinonaDefeated (FLAG_BADGE06_GET) -> GiveAerialAce2
11. `FortreeCity_House4`: `FortreeCity_House4_EventScript_Boy` - Wingull mail errand (ends in Mossdeep, Ch9)

Maps (20): owned (port the whole file) / touched (warps, flags, foreign beats):

| map | role | status |
|---|---|---|
| FortreeCity | owned, main path | built (outdoor zone 16) |
| FortreeCity_Gym | owned, main path | built (room auto, zone 119) |
| Route118 | owned, main path | built (outdoor zone 446) |
| Route119 | owned, main path | built (outdoor zone 463) |
| Route119_WeatherInstitute_1F | owned, main path | built (room auto, zone 563) |
| Route119_WeatherInstitute_2F | owned, main path | built (room auto, zone 564) |
| Route120 | owned, main path | built (outdoor zone 474) |
| FortreeCity_DecorationShop | owned | built (room auto, zone 114) |
| FortreeCity_House1 | owned | built (room auto, zone 121) |
| FortreeCity_House2 | owned | built (room auto, zone 137) |
| FortreeCity_House3 | owned | built (room auto, zone 140) |
| FortreeCity_House4 | owned | built (room auto, zone 141) |
| FortreeCity_House5 | owned | built (room auto, zone 142) |
| FortreeCity_Mart | owned | built (room auto, zone 143) |
| FortreeCity_PokemonCenter_1F | owned | built (room center, zone 65) |
| FortreeCity_PokemonCenter_2F | owned | built (room center, zone 144) |
| Route119_House | owned | built (room auto, zone 562) |
| ScorchedSlab | owned, optional: Scorched Slab | **NOT BUILT (cave; zone 135 allocated, no room file)** |
| AncientTomb | warp from an owned map, owner Ch12 | **NOT BUILT (cave; zone 94 allocated, no room file)** |
| MossdeepCity_House2 | objects/triggers switched by this chapter, owner Ch9 | built (room auto, zone 324) |

Flags used (67; 13 item-ball flags; 45 have this chapter as home):

<details><summary>flag list</summary>

FLAG_BADGE06_GET [engine, C], FLAG_DAILY_RECEIVED_BERRY_ROUTE120 [2747], FLAG_DEFEATED_FORTREE_GYM [579], FLAG_FORTREE_NPC_TRADE_COMPLETED [580], FLAG_HIDDEN_ITEM_42 [engine], FLAG_HIDDEN_ITEM_43 [engine], FLAG_HIDDEN_ITEM_44 [engine], FLAG_HIDDEN_ITEM_45 [engine], FLAG_HIDDEN_ITEM_46 [engine], FLAG_HIDDEN_ITEM_47 [engine], FLAG_HIDDEN_ITEM_5 [engine], FLAG_HIDDEN_ITEM_54 [engine], FLAG_HIDDEN_ITEM_57 [engine], FLAG_HIDDEN_ITEM_6 [engine], FLAG_HIDE_EVIL_TEAM_WEATHER_INSTITUTE [581], FLAG_HIDE_GABBY_AND_TY_ROUTE118_1 [454, home Ch4], FLAG_HIDE_GABBY_AND_TY_ROUTE118_2 [455, home Ch4], FLAG_HIDE_GABBY_AND_TY_ROUTE118_3 [456, home Ch4], FLAG_HIDE_GABBY_AND_TY_ROUTE120_1 [457, home Ch4], FLAG_HIDE_GABBY_AND_TY_ROUTE120_2 [459, home Ch4], FLAG_HIDE_KECLEON_FORTREE [582], FLAG_HIDE_KECLEON_ROUTE119_1 [583], FLAG_HIDE_KECLEON_ROUTE119_2 [584], FLAG_HIDE_KECLEON_ROUTE120_1 [585], FLAG_HIDE_KECLEON_ROUTE120_2 [586], FLAG_HIDE_KECLEON_ROUTE120_3 [587], FLAG_HIDE_KECLEON_ROUTE120_4 [588], FLAG_HIDE_KECLEON_ROUTE120_5 [589], FLAG_HIDE_KECLEON_ROUTE120_6 [590], FLAG_HIDE_KECLEON_ROUTE120_7 [591], FLAG_HIDE_RIVAL_ROUTE119 [592], FLAG_HIDE_RIVAL_ROUTE119_ON_BIKE [593], FLAG_HIDE_STEVEN_ROUTE118 [594], FLAG_HIDE_STEVEN_ROUTE120 [595], FLAG_HIDE_WEATHER_INSTITUTE_WORKERS_1F [596], FLAG_HIDE_WEATHER_INSTITUTE_WORKERS_2F [597], FLAG_HIDE_WINGULL_FORTREE_HOUSE [777, home Ch9], FLAG_HIDE_WINGULL_MOSSDEEP_HOUSE [598], FLAG_KECLEON_FLED_FORTREE [599], FLAG_LANDMARK_SCORCHED_SLAB [600, C], FLAG_MET_HIDDEN_POWER_GIVER [601], FLAG_NOT_READY_FOR_BATTLE_ROUTE120 [602], FLAG_RECEIVED_CASTFORM [603], FLAG_RECEIVED_DEVON_SCOPE [606], FLAG_RECEIVED_GOOD_ROD [608], FLAG_RECEIVED_HM02 [609], FLAG_RECEIVED_MENTAL_HERB [610], FLAG_RECEIVED_TM10 [611], FLAG_RECEIVED_TM_AERIAL_ACE [612], FLAG_REGI_DOORS_OPENED [1069, home Ch12], FLAG_SYS_CTRL_OBJ_DELETE [556, C, home Ch6], FLAG_VISITED_FORTREE_CITY [616, C], FLAG_WINGULL_DELIVERED_MAIL [812, home Ch9], FLAG_WINGULL_SENT_ON_ERRAND [617]

</details>

Vars used (4): VAR_ROUTE118_STATE [0x40B9], VAR_ROUTE119_STATE [0x40BA], VAR_STARTER_MON [0x4030, C, home Ch1], VAR_WEATHER_INSTITUTE_STATE [0x40BB, C]

Reads ids written by other chapters:

- from Ch4: FLAG_HIDE_GABBY_AND_TY_ROUTE118_1, FLAG_HIDE_GABBY_AND_TY_ROUTE118_2, FLAG_HIDE_GABBY_AND_TY_ROUTE118_3, FLAG_HIDE_GABBY_AND_TY_ROUTE120_1, FLAG_HIDE_GABBY_AND_TY_ROUTE120_2
- from Ch6: FLAG_SYS_CTRL_OBJ_DELETE
- from Ch8: FLAG_SYS_CTRL_OBJ_DELETE
- from Ch9: FLAG_HIDE_WINGULL_FORTREE_HOUSE, FLAG_WINGULL_DELIVERED_MAIL
- from Ch10: FLAG_SYS_CTRL_OBJ_DELETE
- from Ch12: FLAG_REGI_DOORS_OPENED, FLAG_SYS_CTRL_OBJ_DELETE
- from Ch13: FLAG_SYS_CTRL_OBJ_DELETE

Trainers: TRAINER_ANGELICA, TRAINER_BARNY, TRAINER_BRANDON_1, TRAINER_BRENDAN_3, TRAINER_BRENDAN_6, TRAINER_BRENDAN_9, TRAINER_BRENT, TRAINER_CARLOS, TRAINER_CATHERINE_1, TRAINER_CHESTER, TRAINER_CHIP, TRAINER_CLARISSA, TRAINER_COLIN, TRAINER_DALTON_1, TRAINER_DONALD, TRAINER_DOUG, TRAINER_EUGENE, TRAINER_GABBY_AND_TY_2, TRAINER_GABBY_AND_TY_3, TRAINER_GABBY_AND_TY_5, TRAINER_GABBY_AND_TY_6, TRAINER_GREG, TRAINER_HIDEO_2, TRAINER_HUGH, TRAINER_JACKSON_1, TRAINER_JARED, TRAINER_JENNA, TRAINER_JENNIFER, TRAINER_KEIGO, TRAINER_KENT, TRAINER_KYLEE, TRAINER_MAY_3, TRAINER_MAY_6, TRAINER_MAY_9, TRAINER_PERRY, TRAINER_PHIL, TRAINER_ROBERT_1, TRAINER_ROSE_1, TRAINER_TAKASHI, TRAINER_TAYLOR, TRAINER_TERRELL, TRAINER_TSUNAO, TRAINER_WADE, TRAINER_WEATHER_INSTITUTE_GRUNT_1, TRAINER_WEATHER_INSTITUTE_GRUNT_2, TRAINER_WEATHER_INSTITUTE_GRUNT_3, TRAINER_WEATHER_INSTITUTE_GRUNT_4, TRAINER_WEATHER_INSTITUTE_GRUNT_5, TRAINER_WILL, TRAINER_WINONA, TRAINER_YASU

### Ch8 - Route 121-123, Lilycove (rival), Mt. Pyre (orb stolen), Slateport sub theft, Aqua Hideout

**UNBLOCKED** | in progress: MtPyre_Exterior, MtPyre_Summit, AquaHideout_1F, AquaHideout_B1F, AquaHideout_B2F

Size: 4733 script lines in 779 labels (+1600 text lines in owned maps); 46 trainerbattle commands, 35 unique trainers; 109 flags, 13 vars.

- optional block **Safari Zone**: 253 lines, 0 trainerbattle cmds in owned files; NOT BUILT: -; in progress: SafariZone_Northeast, SafariZone_Northwest, SafariZone_Southeast, SafariZone_Southwest
- optional block **Mt. Pyre tower floors 2F-6F**: 62 lines, 9 trainerbattle cmds in owned files; NOT BUILT: -

Possible split into separate agents:

- **8a Lilycove city and its buildings**: 2919 lines, 6 trainerbattle cmds
- **8b Routes 121-123, Safari Zone, Mt. Pyre, Aqua Hideout (+ Slateport foreign beats)**: 1321 lines, 34 trainerbattle cmds

Story beats (in order; `map: label`):

1. `Route121`: `Route121_EventScript_151B25` - Aqua grunts on Route 121 head for Mt. Pyre (VAR_ROUTE121_STATE)
2. `LilycoveCity`: `LilycoveCity_EventScript_Rival` - rival outside the Dept. Store: battle (TRAINER_MAY/BRENDAN_LILYCOVE_*) -> DefeatedMay/Brendan -> RivalFlyAway
3. `LilycoveCity`: `LilycoveCity_EventScript_WailmerTrainerGrunt` - Aqua grunt at the cove (hideout entrance)
4. `MtPyre_1F`: `MtPyre_1F_EventScript_15D323` - Cleanse Tag
5. `MtPyre_Summit`: `MtPyre_Summit_EventScript_15D4BD` - summit trigger (VAR_MT_PYRE_STATE 0) -> 15D4E1 Archie takes the Blue Orb (old couple gives the Red Orb)
6. `MtPyre_Summit`: `MtPyre_Summit_EventScript_15D57A` - sets FLAG_MT_PYRE_ORB_STOLEN, VAR_SLATEPORT_STATE/VAR_SLATEPORT_HARBOR_STATE (Slateport scene armed)
7. `SlateportCity`: `SlateportCity_EventScript_CaptStern` - Slateport: Stern's interview (Ch3 file)
8. `SlateportCity_Harbor`: `SlateportCity_Harbor_EventScript_EvilTeamEscapeScene` - Aqua steal the submarine; frees the hideout entrance (FLAG_HIDE_GRUNT_*_BLOCKING_HIDEOUT) (Ch3 file)
9. `AquaHideout_1F`: `MagmaHideout_1F_EventScript_15D80C` - Aqua Hideout (Sapphire uses AquaHideout_*; MagmaHideout_* are Ruby-only): grunts, Electrode (static_pokemon.inc)
10. `AquaHideout_B2F`: `AquaHideout_B2F_EventScript_15D8FD` - Archie escapes in the submarine (FLAG_EVIL_TEAM_ESCAPED_IN_SUBMARINE), Master Ball item
11. `LittlerootTown_MaysHouse_2F`: `RivalsHouse_2F_EventScript_RivalPostLilycove` - rival at home after Lilycove (Ch0 file)
12. `LilycoveCity_LilycoveMuseum_2F`: `LilycoveCity_LilycoveMuseum_2F_EventScript_ShowExhibitHall` - museum curator (contest paintings)
13. `Route121_SafariZoneEntrance`: `Route121_SafariZoneEntrance_EventScript_15C3B3` - (optional) Safari Zone entry (safari_zone.inc)

Foreign beats this chapter writes into other chapters' files (scene includes):

- `SlateportCity` [SlateportCity_EventScript_CaptStern .. SlateportCity_EventScript_Ty) ~139 lines - Capt. Stern on TV / at the harbor after the orb theft
- `SlateportCity_Harbor` [SlateportCity_Harbor_EventScript_ReadyEvilTeamEscapeScene .. SlateportCity_Harbor_EventScript_FerryAttendant) ~124 lines - Aqua steal Stern's submarine
- `SlateportCity_Harbor` [SlateportCity_Harbor_EventScript_CaptStern .. SlateportCity_Harbor_EventScript_CaptSternFerryOrScannerComment) ~27 lines - Stern after the theft ("need Dive")
- `LittlerootTown_MaysHouse_2F` [RivalsHouse_2F_EventScript_RivalPostLilycove .. RivalsHouse_2F_EventScript_MayWhereShouldIGoNext) ~19 lines - rival at home after Lilycove

Other chapters' beats inside this chapter's files (reserve slots for them):

- Ch10: `MtPyre_Summit` from `MtPyre_Summit_EventScript_15D669` - return the orbs at the Mt. Pyre summit after Kyogre

Maps (53): owned (port the whole file) / touched (warps, flags, foreign beats):

| map | role | status |
|---|---|---|
| AquaHideout_1F | owned, main path | **in progress (big room, zone 2, no room file yet)** |
| AquaHideout_B1F | owned, main path | **in progress (big room, zone 5, no room file yet)** |
| AquaHideout_B2F | owned, main path | **in progress (big room, zone 10, no room file yet)** |
| LilycoveCity | owned, main path | built (outdoor zone 96) |
| MtPyre_1F | owned, main path | built (room auto, zone 341) |
| MtPyre_Exterior | owned, main path | **in progress (standalone map, zone 20: built in the standalone agent's test ROM, proof work/agents/standalone/proofs/MtPyre_Exterior.png; not in the main build yet, hoenn_standalone.json "build" is empty)** |
| MtPyre_Summit | owned, main path | **in progress (standalone map, zone 29: built in the standalone agent's test ROM, proof work/agents/standalone/proofs/MtPyre_Summit.png; not in the main build yet, hoenn_standalone.json "build" is empty)** |
| Route121 | owned, main path | built (outdoor zone 475) |
| Route122 | owned, main path | built (outdoor zone 551) |
| LilycoveCity_ContestHall | owned | built (room big, zone 160) |
| LilycoveCity_ContestLobby | owned | built (room auto, zone 161) |
| LilycoveCity_CoveLilyMotel_1F | owned | built (room auto, zone 178) |
| LilycoveCity_CoveLilyMotel_2F | owned | built (room auto, zone 180) |
| LilycoveCity_DepartmentStoreElevator | owned | built (room auto, zone 181) |
| LilycoveCity_DepartmentStoreRooftop | owned | built (room auto, zone 182) |
| LilycoveCity_DepartmentStore_1F | owned | built (room auto, zone 196) |
| LilycoveCity_DepartmentStore_2F | owned | built (room auto, zone 197) |
| LilycoveCity_DepartmentStore_3F | owned | built (room auto, zone 199) |
| LilycoveCity_DepartmentStore_4F | owned | built (room auto, zone 200) |
| LilycoveCity_DepartmentStore_5F | owned | built (room auto, zone 201) |
| LilycoveCity_House1 | owned | built (room auto, zone 206) |
| LilycoveCity_House2 | owned | built (room auto, zone 207) |
| LilycoveCity_House3 | owned | built (room auto, zone 208) |
| LilycoveCity_House4 | owned | built (room auto, zone 209) |
| LilycoveCity_LilycoveMuseum_1F | owned | built (room auto, zone 210) |
| LilycoveCity_LilycoveMuseum_2F | owned | built (room auto, zone 211) |
| LilycoveCity_MoveDeletersHouse | owned | built (room auto, zone 212) |
| LilycoveCity_PokemonCenter_1F | owned | built (room center, zone 109) |
| LilycoveCity_PokemonCenter_2F | owned | built (room center, zone 213) |
| LilycoveCity_PokemonTrainerFanClub | owned | built (room auto, zone 214) |
| MtPyre_2F | owned, optional: Mt. Pyre tower floors 2F-6F | built (room auto, zone 342) |
| MtPyre_3F | owned, optional: Mt. Pyre tower floors 2F-6F | built (room auto, zone 346) |
| MtPyre_4F | owned, optional: Mt. Pyre tower floors 2F-6F | built (room auto, zone 350) |
| MtPyre_5F | owned, optional: Mt. Pyre tower floors 2F-6F | built (room auto, zone 351) |
| MtPyre_6F | owned, optional: Mt. Pyre tower floors 2F-6F | built (room auto, zone 376) |
| Route121_SafariZoneEntrance | owned, optional: Safari Zone | built (room auto, zone 569) |
| Route123 | owned | built (outdoor zone 154) |
| Route123_BerryMastersHouse | owned | built (room auto, zone 570) |
| SafariZone_Northeast | owned, optional: Safari Zone | **in progress (standalone map, zone 38: built in the standalone agent's test ROM, proof work/agents/standalone/proofs/SafariZone_Northeast.png; not in the main build yet, hoenn_standalone.json "build" is empty)** |
| SafariZone_Northwest | owned, optional: Safari Zone | **in progress (standalone map, zone 39: built in the standalone agent's test ROM, proof work/agents/standalone/proofs/SafariZone_Northwest.png; not in the main build yet, hoenn_standalone.json "build" is empty)** |
| SafariZone_RestHouse | owned, optional: Safari Zone | built (room auto, zone 592) |
| SafariZone_Southeast | owned, optional: Safari Zone | **in progress (standalone map, zone 40: built in the standalone agent's test ROM, proof work/agents/standalone/proofs/SafariZone_Southeast.png; not in the main build yet, hoenn_standalone.json "build" is empty)** |
| SafariZone_Southwest | owned, optional: Safari Zone | **in progress (standalone map, zone 64: built in the standalone agent's test ROM, proof work/agents/standalone/proofs/SafariZone_Southwest.png; not in the main build yet, hoenn_standalone.json "build" is empty)** |
| SlateportCity | foreign beat, main path | built (outdoor zone 448) |
| SlateportCity_Harbor | foreign beat, main path | built (room auto, zone 596) |
| FallarborTown_ContestLobby | ref, owner Ch4 | built (room auto, zone 93) |
| LilycoveCity_Harbor | warp from an owned map, owner Ch13 | built (room auto, zone 203) |
| LittlerootTown_BrendansHouse_2F | objects/triggers switched by this chapter, owner Ch0 | built (room hand, zone 391) |
| LittlerootTown_MaysHouse_2F | foreign beat | built (room hand, zone 393) |
| MagmaHideout_1F | objects/triggers switched by this chapter, owner S_unused | **in progress (big room, zone 228, no room file yet)** |
| MagmaHideout_B1F | objects/triggers switched by this chapter, owner S_unused | **in progress (big room, zone 231, no room file yet)** |
| SlateportCity_ContestLobby | ref, owner Ch3 | built (room auto, zone 595) |
| VerdanturfTown_ContestLobby | ref, owner Ch3 | built (room auto, zone 60) |

Flags used (109; 20 item-ball flags; 75 have this chapter as home):

<details><summary>flag list</summary>

FLAG_BADGE06_GET [engine, C, home Ch7], FLAG_BADGE07_GET [engine, C, home Ch9], FLAG_BADGE08_GET [engine, C, home Ch10], FLAG_BEAUTY_PAINTING_MADE [640], FLAG_COOL_PAINTING_MADE [641], FLAG_CUTE_PAINTING_MADE [642], FLAG_DAILY_PICKED_LOTTO_TICKET [2748], FLAG_DAILY_RECEIVED_BERRY_FALLARBOR [2749], FLAG_DAILY_RECEIVED_BERRY_FROM_BERRYMASTER [2750], FLAG_DAILY_RECEIVED_BERRY_FROM_BERRYMASTER_WIFE [2751], FLAG_DAILY_RECEIVED_BERRY_LILYCOVE [2752], FLAG_DECLINED_RIVAL_BATTLE_LILYCOVE [643], FLAG_EVIL_TEAM_ESCAPED_IN_SUBMARINE [646], FLAG_EVIL_TEAM_ESCAPED_STERN_SPOKE [647], FLAG_HIDDEN_ITEM_1B [engine], FLAG_HIDDEN_ITEM_1D [engine], FLAG_HIDDEN_ITEM_27 [engine], FLAG_HIDDEN_ITEM_28 [engine], FLAG_HIDDEN_ITEM_29 [engine], FLAG_HIDDEN_ITEM_49 [engine], FLAG_HIDDEN_ITEM_4A [engine], FLAG_HIDDEN_ITEM_4E [engine], FLAG_HIDDEN_ITEM_4F [engine], FLAG_HIDDEN_ITEM_50 [engine], FLAG_HIDDEN_ITEM_7 [engine], FLAG_HIDDEN_ITEM_LILYCOVE_CITY_POKE_BALL [engine], FLAG_HIDDEN_ITEM_LILYCOVE_CITY_PP_UP [engine], FLAG_HIDE_ARTIST_LILCOVE_CONTEST [648], FLAG_HIDE_BRENDAN_UPSTAIRS [2053, home Ch0], FLAG_HIDE_ELECTRODE_1_HIDEOUT [649], FLAG_HIDE_ELECTRODE_2_HIDEOUT [650], FLAG_HIDE_FANCLUB_BOY [651, C], FLAG_HIDE_FANCLUB_LADY [652, C], FLAG_HIDE_FANCLUB_LITTLE_BOY [653, C], FLAG_HIDE_FANCLUB_OLD_LADY [655, C], FLAG_HIDE_GABBY_AND_TY_SLATEPORT [656], FLAG_HIDE_GRUNTS_HIDEOUTS [657], FLAG_HIDE_GRUNTS_LILYCOVE [658], FLAG_HIDE_GRUNTS_MT_PYRE_SUMMIT [659], FLAG_HIDE_GRUNTS_ROUTE121 [661], FLAG_HIDE_GRUNT_1_BLOCKING_HIDEOUT [662], FLAG_HIDE_GRUNT_1_SLATEPORT_HARBOR [663], FLAG_HIDE_GRUNT_2_BLOCKING_HIDEOUT [664], FLAG_HIDE_GRUNT_2_SLATEPORT_HARBOR [665], FLAG_HIDE_LEADER_MT_PYRE_SUMMIT [666], FLAG_HIDE_LILYCOVE_CONTEST_ATTENDENT_1 [668], FLAG_HIDE_LILYCOVE_CONTEST_HALL_REPORTER [463, home Ch4], FLAG_HIDE_LILYCOVE_MOTEL_PEOPLE [999, home Ch11], FLAG_HIDE_LILYCOVE_MUSEUM_CURATOR [669], FLAG_HIDE_LILYCOVE_MUSEUM_PATRON_1 [670], FLAG_HIDE_LILYCOVE_MUSEUM_PATRON_2 [671], FLAG_HIDE_LILYCOVE_MUSEUM_PATRON_3 [672], FLAG_HIDE_LILYCOVE_MUSEUM_PATRON_4 [673], FLAG_HIDE_LILYCOVE_MUSEUM_TOURISTS [674], FLAG_HIDE_MAY_PICHU_DOLL [2065], FLAG_HIDE_MAY_UPSTAIRS [2057, home Ch0], FLAG_HIDE_RIVAL_LILYCOVE_MART [675], FLAG_HIDE_ROOFTOP_LADY_LILYCOVE_MART [676], FLAG_HIDE_STERN_SLATEPORT [677], FLAG_HIDE_STERN_SLATEPORT_HARBOR [678], FLAG_HIDE_SUBMARINE_SHADOW_HIDEOUT [680], FLAG_HIDE_SUBMARINE_SHADOW_SLATEPORT_HARBOR [681], FLAG_HIDE_WORKERS_SLATEPORT_HARBOR [682], FLAG_LANDMARK_BERRY_MASTERS_HOUSE [684, C], FLAG_LEGENDARY_BATTLE_COMPLETED [2074, home Ch10], FLAG_LEGEND_ESCAPED_SEAFLOOR_CAVERN [2075, home Ch10], FLAG_MET_RIVAL_IN_HOUSE_AFTER_LILYCOVE [685], FLAG_MET_RIVAL_LILYCOVE [687], FLAG_MET_WAILMER_TRAINER [688], FLAG_MT_PYRE_ORB_STOLEN [689], FLAG_RECEIVED_BELUE_BERRY [690], FLAG_RECEIVED_CLEANSE_TAG [696], FLAG_RECEIVED_CONTEST_PASS [home S_optional], FLAG_RECEIVED_DURIN_BERRY [698], FLAG_RECEIVED_GLASS_ORNAMENT [699], FLAG_RECEIVED_PAMTRE_BERRY [700], FLAG_RECEIVED_RED_OR_BLUE_ORB [703], FLAG_RECEIVED_SPELON_BERRY [704], FLAG_RECEIVED_TM19 [705], FLAG_RECEIVED_TM44 [706], FLAG_RECEIVED_WATMEL_BERRY [707], FLAG_RETURNED_RED_OR_BLUE_ORB [902, home Ch10], FLAG_SMART_PAINTING_MADE [708], FLAG_SYS_CTRL_OBJ_DELETE [556, C, home Ch6], FLAG_SYS_GAME_CLEAR [engine 2400, C, home Ch1], FLAG_SYS_RIBBON_GET [709, C], FLAG_SYS_WEATHER_CTRL [903, C, home Ch10], FLAG_TOUGH_PAINTING_MADE [711], FLAG_VISITED_LILYCOVE_CITY [713, C]

</details>

Vars used (13): VAR_CONTEST_LOCATION [0x4072, home Ch3], VAR_DEPT_STORE_FLOOR [0x40C2, C], VAR_LILYCOVE_CONTEST_LOBBY_STATE [0x40C3], VAR_LILYCOVE_FAN_CLUB_STATE [0x40C5, C], VAR_LILYCOVE_MUSEUM_2F_STATE [0x40C7], VAR_LINK_CONTEST_ROOM_STATE [0x4076, home Ch3], VAR_LOTTERY_PRIZE [0x40C8, C], VAR_MT_PYRE_STATE [0x40C9], VAR_ROUTE121_STATE [0x40CA], VAR_SAFARI_ZONE_STATE [0x40CB], VAR_SLATEPORT_HARBOR_STATE [0x40CC], VAR_SLATEPORT_STATE [0x40CD], VAR_STARTER_MON [0x4030, C, home Ch1]

Reads ids written by other chapters:

- from Ch3: VAR_CONTEST_LOCATION, VAR_LINK_CONTEST_ROOM_STATE
- from Ch4: FLAG_HIDE_LILYCOVE_CONTEST_HALL_REPORTER, VAR_CONTEST_LOCATION, VAR_LINK_CONTEST_ROOM_STATE
- from Ch6: FLAG_SYS_CTRL_OBJ_DELETE
- from Ch7: FLAG_BADGE06_GET, FLAG_SYS_CTRL_OBJ_DELETE
- from Ch9: FLAG_BADGE07_GET
- from Ch10: FLAG_BADGE08_GET, FLAG_HIDE_LEADER_MT_PYRE_SUMMIT, FLAG_LEGENDARY_BATTLE_COMPLETED, FLAG_LEGEND_ESCAPED_SEAFLOOR_CAVERN, FLAG_RETURNED_RED_OR_BLUE_ORB, FLAG_SYS_CTRL_OBJ_DELETE, FLAG_SYS_WEATHER_CTRL, VAR_MT_PYRE_STATE
- from Ch11: FLAG_HIDE_LILYCOVE_MOTEL_PEOPLE
- from Ch12: FLAG_SYS_CTRL_OBJ_DELETE
- from Ch13: FLAG_SYS_CTRL_OBJ_DELETE

Trainers: TRAINER_ATSUSHI, TRAINER_BRENDAN_LILYCOVE_MUDKIP, TRAINER_BRENDAN_LILYCOVE_TORCHIC, TRAINER_BRENDAN_LILYCOVE_TREECKO, TRAINER_CAMERON_1, TRAINER_CLYDE, TRAINER_DEZ_AND_LUKE, TRAINER_HIDEOUT_1F_GRUNT, TRAINER_HIDEOUT_B1F_GRUNT_1, TRAINER_HIDEOUT_B1F_GRUNT_2, TRAINER_HIDEOUT_B1F_GRUNT_3, TRAINER_HIDEOUT_B2F_GRUNT_1, TRAINER_HIDEOUT_B2F_GRUNT_2, TRAINER_HIDEOUT_B2F_GRUNT_3, TRAINER_JACKI_1, TRAINER_JESSICA_1, TRAINER_KATE_AND_JOY, TRAINER_KAYLA, TRAINER_KINDRA, TRAINER_MARK, TRAINER_MAY_LILYCOVE_MUDKIP, TRAINER_MAY_LILYCOVE_TORCHIC, TRAINER_MAY_LILYCOVE_TREECKO, TRAINER_MIU_AND_YUKI, TRAINER_MT_PYRE_SUMMIT_GRUNT_1, TRAINER_MT_PYRE_SUMMIT_GRUNT_2, TRAINER_MT_PYRE_SUMMIT_GRUNT_3, TRAINER_TAMMY, TRAINER_TASHA, TRAINER_VALERIE_1, TRAINER_VANESSA, TRAINER_VIOLET, TRAINER_WALTER_1, TRAINER_WENDY, TRAINER_WILLIAM

- Note: LilycoveCity_ContestLobby (676 lines) + ContestHall: NPCs here, the contest flow belongs to the optional Contests block.
- Note: MagmaHideout_1F/B1F/B2F are Ruby's hideout (zones 228/231/234 allocated "big"): not needed for Sapphire.

### Ch9 - Route 124-127, Mossdeep: Tate & Liza, Steven gives Dive, Shoal Cave

**UNBLOCKED** | badge: Mind Badge (7)

Size: 1592 script lines in 296 labels (+513 text lines in owned maps); 36 trainerbattle commands, 30 unique trainers; 50 flags, 2 vars.

- optional block **Shoal Cave (Shell Bell, Focus Band)**: 286 lines, 0 trainerbattle cmds in owned files; NOT BUILT: ShoalCave_LowTideEntranceRoom, ShoalCave_LowTideInnerRoom, ShoalCave_LowTideStairsRoom, ShoalCave_LowTideLowerRoom, ShoalCave_LowTideIceRoom, ShoalCave_HighTideEntranceRoom, ShoalCave_HighTideInnerRoom

Story beats (in order; `map: label`):

1. `Route124_DivingTreasureHuntersHouse`: `Route124_DivingTreasureHuntersHouse_EventScript_163E04` - shard trader
2. `MossdeepCity`: `MossdeepCity_EventScript_VisitedMossdeep` - arrive in Mossdeep
3. `MossdeepCity_Gym`: `MossdeepCity_Gym_EventScript_TateAndLiza` - Tate & Liza (double battle, switch floor) -> TateAndLizaDefeated (FLAG_BADGE07_GET) -> GiveCalmMind2
4. `MossdeepCity_StevensHouse`: `MossdeepCity_StevensHouse_EventScript_StevenGivesDive` - Steven gives HM08 Dive (VAR_STEVENS_HOUSE_STATE)
5. `MossdeepCity_SpaceCenter_1F`: `MossdeepCity_SpaceCenter_1F_EventScript_SunStoneMan` - Sun Stone
6. `MossdeepCity_House2`: `MossdeepCity_House2_EventScript_Wingull` - Wingull mail delivered (from Fortree)
7. `ShoalCave_LowTideEntranceRoom`: `ShoalCave_LowTideEntranceRoom_EventScript_15E176` - (optional) Shoal Cave tides, Shoal Salt/Shell -> Shell Bell

Foreign beats this chapter writes into other chapters' files (scene includes):

- `SlateportCity_SternsShipyard_1F` [SlateportCity_SternsShipyard_1F_EventScript_Briney .. end of file) ~3 lines - Mr. Briney helps build the ferry (after the Mind Badge)

Other chapters' beats inside this chapter's files (reserve slots for them):

- Ch13: `MossdeepCity_StevensHouse` from `MossdeepCity_StevensHouse_EventScript_BeldumPokeball` - Steven's Beldum
- Ch13: `MossdeepCity_StevensHouse` from `MossdeepCity_StevensHouse_EventScript_Letter` - Steven's letter

Maps (29): owned (port the whole file) / touched (warps, flags, foreign beats):

| map | role | status |
|---|---|---|
| MossdeepCity | owned, main path | built (outdoor zone 107) |
| MossdeepCity_Gym | owned, main path | built (room big, zone 322) |
| MossdeepCity_StevensHouse | owned, main path | built (room auto, zone 339) |
| Route124 | owned, main path | built (outdoor zone 157) |
| MossdeepCity_GameCorner_1F | owned | built (room auto, zone 277) |
| MossdeepCity_GameCorner_B1F | owned | built (room auto, zone 278) |
| MossdeepCity_House1 | owned | built (room auto, zone 323) |
| MossdeepCity_House2 | owned | built (room auto, zone 324) |
| MossdeepCity_House3 | owned | built (room auto, zone 325) |
| MossdeepCity_House4 | owned | built (room auto, zone 332) |
| MossdeepCity_Mart | owned | built (room auto, zone 333) |
| MossdeepCity_PokemonCenter_1F | owned | built (room center, zone 122) |
| MossdeepCity_PokemonCenter_2F | owned | built (room center, zone 334) |
| MossdeepCity_SpaceCenter_1F | owned | built (room auto, zone 335) |
| MossdeepCity_SpaceCenter_2F | owned | built (room auto, zone 338) |
| Route124_DivingTreasureHuntersHouse | owned | built (room auto, zone 571) |
| Route125 | owned | built (outdoor zone 194) |
| Route126 | owned | built (outdoor zone 198) |
| Route127 | owned | built (outdoor zone 205) |
| ShoalCave_HighTideEntranceRoom | owned, optional: Shoal Cave | **NOT BUILT (in no zone list)** |
| ShoalCave_HighTideInnerRoom | owned, optional: Shoal Cave | **NOT BUILT (in no zone list)** |
| ShoalCave_LowTideEntranceRoom | owned, optional: Shoal Cave | **NOT BUILT (cave; zone 138 allocated, no room file)** |
| ShoalCave_LowTideIceRoom | owned, optional: Shoal Cave | **NOT BUILT (cave; zone 139 allocated, no room file)** |
| ShoalCave_LowTideInnerRoom | owned, optional: Shoal Cave | **NOT BUILT (cave; zone 146 allocated, no room file)** |
| ShoalCave_LowTideLowerRoom | owned, optional: Shoal Cave | **NOT BUILT (cave; zone 162 allocated, no room file)** |
| ShoalCave_LowTideStairsRoom | owned, optional: Shoal Cave | **NOT BUILT (cave; zone 163 allocated, no room file)** |
| FortreeCity_House4 | objects/triggers switched by this chapter, owner Ch7 | built (room auto, zone 141) |
| SlateportCity_Harbor | objects/triggers switched by this chapter, owner Ch3 | built (room auto, zone 596) |
| SlateportCity_SternsShipyard_1F | foreign beat | built (room auto, zone 14) |

Flags used (50; 13 item-ball flags; 30 have this chapter as home):

<details><summary>flag list</summary>

FLAG_BADGE07_GET [engine, C], FLAG_DEFEATED_MOSSDEEP_GYM [752], FLAG_HIDE_BELDUM_BALL_STEVENS_HOUSE [1095, home Ch13], FLAG_HIDE_BRINEY_SLATEPORT_SHIPYARD [755], FLAG_HIDE_STEVENS_LETTER [1005, home Ch11], FLAG_HIDE_STEVEN_STEVENS_HOUSE [877, home Ch10], FLAG_HIDE_TOOK_SHOAL_SALT_1 [757], FLAG_HIDE_TOOK_SHOAL_SALT_2 [759], FLAG_HIDE_TOOK_SHOAL_SALT_3 [760], FLAG_HIDE_TOOK_SHOAL_SALT_4 [763], FLAG_HIDE_TOOK_SHOAL_SHELL_1 [764], FLAG_HIDE_TOOK_SHOAL_SHELL_2 [765], FLAG_HIDE_TOOK_SHOAL_SHELL_3 [766], FLAG_HIDE_TOOK_SHOAL_SHELL_4 [776], FLAG_HIDE_WINGULL_FORTREE_HOUSE [777], FLAG_HIDE_WINGULL_MOSSDEEP_HOUSE [598, home Ch7], FLAG_HIDE_WORKERS_SLATEPORT_HARBOR [682, home Ch8], FLAG_LANDMARK_HUNTERS_HOUSE [778, C], FLAG_MET_DIVING_TREASURE_HUNTER [779], FLAG_MOSSDEEP_GYM_SWITCH_1 [780], FLAG_MOSSDEEP_GYM_SWITCH_2 [781], FLAG_MOSSDEEP_GYM_SWITCH_3 [783], FLAG_MOSSDEEP_GYM_SWITCH_4 [786], FLAG_OMIT_DIVE_FROM_STEVEN_LETTER [787], FLAG_RECEIVED_FOCUS_BAND [788], FLAG_RECEIVED_HM08 [789], FLAG_RECEIVED_KINGS_ROCK [790], FLAG_RECEIVED_SUN_STONE_MOSSDEEP [791], FLAG_RECEIVED_SUPER_ROD [793], FLAG_RECEIVED_TM_CALM_MIND [799], FLAG_SYS_GAME_CLEAR [engine 2400, C, home Ch1], FLAG_SYS_SHOAL_ITEM [803], FLAG_SYS_SHOAL_TIDE [804, C], FLAG_SYS_WEATHER_CTRL [903, C, home Ch10], FLAG_UNKNOWN_393 [806], FLAG_VISITED_MOSSDEEP_CITY [807, C], FLAG_WINGULL_DELIVERED_MAIL [812]

</details>

Vars used (2): VAR_GAME_CORNER_STATE [0x40D7], VAR_STEVENS_HOUSE_STATE [0x40D8]

Reads ids written by other chapters:

- from Ch7: FLAG_HIDE_WINGULL_MOSSDEEP_HOUSE
- from Ch10: FLAG_HIDE_STEVEN_STEVENS_HOUSE, FLAG_SYS_WEATHER_CTRL, VAR_STEVENS_HOUSE_STATE
- from Ch11: FLAG_HIDE_STEVENS_LETTER, VAR_STEVENS_HOUSE_STATE
- from Ch13: FLAG_HIDE_BELDUM_BALL_STEVENS_HOUSE

Trainers: TRAINER_BARRY, TRAINER_BRENDA, TRAINER_BYRON, TRAINER_CALEB, TRAINER_CHAD, TRAINER_CODY, TRAINER_CONNOR, TRAINER_DEAN, TRAINER_ERNEST_1, TRAINER_FRITZ, TRAINER_GRACE, TRAINER_HANNAH, TRAINER_HENRY, TRAINER_JENNY_1, TRAINER_JONAH, TRAINER_KIM_AND_IRIS, TRAINER_KOJI, TRAINER_MAURA, TRAINER_NIKKI, TRAINER_PRESTON, TRAINER_RITA_AND_SAM_1, TRAINER_ROGER, TRAINER_ROLAND, TRAINER_SAMANTHA, TRAINER_SHARON, TRAINER_SPENCER, TRAINER_STAN, TRAINER_TANYA, TRAINER_TATE_AND_LIZA, TRAINER_VIRGIL

- Note: Dive itself (HM08) needs an engine answer before Ch10 (Gen 5 has no Dive).

### Ch10 - Seafloor Cavern (Kyogre awakens), Route 128, Sootopolis, Cave of Origin (Kyogre), Wallace

**BLOCKED** - blocked by: Underwater4, Underwater_SeafloorCavern, SeafloorCavern_Entrance, SeafloorCavern_Room1, SeafloorCavern_Room2, SeafloorCavern_Room3, SeafloorCavern_Room4, SeafloorCavern_Room5, SeafloorCavern_Room6, SeafloorCavern_Room7, SeafloorCavern_Room8, SeafloorCavern_Room9, Underwater2, Underwater_SootopolisCity, CaveOfOrigin_Entrance, CaveOfOrigin_1F, CaveOfOrigin_B1F, CaveOfOrigin_B2F, CaveOfOrigin_B3F, CaveOfOrigin_B4F | in progress: SootopolisCity | badge: Rain Badge (8)

Size: 1814 script lines in 251 labels (+651 text lines in owned maps); 22 trainerbattle commands, 19 unique trainers; 59 flags, 7 vars.

Story beats (in order; `map: label`):

1. `Underwater_SeafloorCavern`: `Underwater_SeafloorCavern_MapScript1_15D9AE` - Dive on Route 128 (Underwater4) to the stolen submarine
2. `SeafloorCavern_Room1`: `SeafloorCavern_Room1_EventScript_15DA6D` - Seafloor Cavern grunts (Rooms 1/3/4), Strength + Rock Smash puzzles
3. `SeafloorCavern_Room9`: `SeafloorCavern_Room9_EventScript_15DAFA` - Archie wakes Kyogre with the Blue Orb; Maxie arrives; weather crisis (FLAG_SYS_WEATHER_CTRL)
4. `Route128`: `Route128_EventScript_15213F` - Archie, Maxie and Steven on Route 128 (VAR_ROUTE128_STATE)
5. `Underwater_SootopolisCity`: `Underwater_SootopolisCity_MapScript1_15CAEA` - Dive under Route 126 into Sootopolis
6. `SootopolisCity`: `SootopolisCity_EventScript_LeadPlayerCaveOfOrigin` - Steven leads you to Wallace, Wallace to the Cave of Origin (VAR_SOOTOPOLIS_STATE)
7. `CaveOfOrigin_B4F`: `CaveOfOrigin_B4F_EventScript_15DDD7` - Kyogre battle (FLAG_LEGENDARY_BATTLE_COMPLETED), weather ends, Wallace back to the gym
8. `SootopolisCity_Gym_1F`: `SootopolisCity_Gym_1F_EventScript_Wallace` - Wallace (ice floor puzzle) -> WallaceDefeated (FLAG_BADGE08_GET) -> GiveWaterPulse2
9. `MtPyre_Summit`: `MtPyre_Summit_EventScript_15D669` - orbs returned at Mt. Pyre (Ch8 file)

Foreign beats this chapter writes into other chapters' files (scene includes):

- `MtPyre_Summit` [MtPyre_Summit_EventScript_15D669 .. end of file) ~152 lines - return the orbs at the Mt. Pyre summit after Kyogre

Maps (39): owned (port the whole file) / touched (warps, flags, foreign beats):

| map | role | status |
|---|---|---|
| CaveOfOrigin_1F | owned, main path | **NOT BUILT (cave; zone 95 allocated, no room file)** |
| CaveOfOrigin_B1F | owned, main path | **NOT BUILT (cave; zone 100 allocated, no room file)** |
| CaveOfOrigin_B2F | owned, main path | **NOT BUILT (cave; zone 101 allocated, no room file)** |
| CaveOfOrigin_B3F | owned, main path | **NOT BUILT (cave; zone 102 allocated, no room file)** |
| CaveOfOrigin_B4F | owned, main path | **NOT BUILT (cave; zone 103 allocated, no room file)** |
| CaveOfOrigin_Entrance | owned, main path | **NOT BUILT (cave; zone 110 allocated, no room file)** |
| Route128 | owned, main path | built (outdoor zone 230) |
| SeafloorCavern_Entrance | owned, main path | **NOT BUILT (in no zone list)** |
| SeafloorCavern_Room1 | owned, main path | **NOT BUILT (in no zone list)** |
| SeafloorCavern_Room2 | owned, main path | **NOT BUILT (in no zone list)** |
| SeafloorCavern_Room3 | owned, main path | **NOT BUILT (in no zone list)** |
| SeafloorCavern_Room4 | owned, main path | **NOT BUILT (in no zone list)** |
| SeafloorCavern_Room5 | owned, main path | **NOT BUILT (in no zone list)** |
| SeafloorCavern_Room6 | owned, main path | **NOT BUILT (in no zone list)** |
| SeafloorCavern_Room7 | owned, main path | **NOT BUILT (in no zone list)** |
| SeafloorCavern_Room8 | owned, main path | **NOT BUILT (in no zone list)** |
| SeafloorCavern_Room9 | owned, main path | **NOT BUILT (in no zone list)** |
| SootopolisCity | owned, main path | **in progress (standalone map, zone 319: built in the standalone agent's test ROM, proof work/agents/standalone/proofs/SootopolisCity.png; not in the main build yet, hoenn_standalone.json "build" is empty)** |
| SootopolisCity_Gym_1F | owned, main path | built (room auto, zone 23) |
| SootopolisCity_Gym_B1F | owned, main path | built (room auto, zone 24) |
| Underwater2 | owned, main path | **NOT BUILT (in no zone list)** |
| Underwater4 | owned, main path | **NOT BUILT (in no zone list)** |
| Underwater_SeafloorCavern | owned, main path | **NOT BUILT (in no zone list)** |
| Underwater_SootopolisCity | owned, main path | **NOT BUILT (in no zone list)** |
| SootopolisCity_House1 | owned | built (room auto, zone 27) |
| SootopolisCity_House2 | owned | built (room auto, zone 44) |
| SootopolisCity_House3 | owned | built (room auto, zone 45) |
| SootopolisCity_House4 | owned | built (room auto, zone 46) |
| SootopolisCity_House5 | owned | built (room auto, zone 48) |
| SootopolisCity_House6 | owned | built (room auto, zone 49) |
| SootopolisCity_House7 | owned | built (room auto, zone 50) |
| SootopolisCity_House8 | owned | built (room auto, zone 54) |
| SootopolisCity_Mart | owned | built (room auto, zone 55) |
| SootopolisCity_PokemonCenter_1F | owned | built (room center, zone 443) |
| SootopolisCity_PokemonCenter_2F | owned | built (room center, zone 56) |
| Underwater1 | owned | **NOT BUILT (in no zone list)** |
| Underwater3 | owned | **NOT BUILT (in no zone list)** |
| MossdeepCity_StevensHouse | objects/triggers switched by this chapter, owner Ch9 | built (room auto, zone 339) |
| MtPyre_Summit | foreign beat | **in progress (standalone map, zone 29: built in the standalone agent's test ROM, proof work/agents/standalone/proofs/MtPyre_Summit.png; not in the main build yet, hoenn_standalone.json "build" is empty)** |

Flags used (59; 2 item-ball flags; 54 have this chapter as home):

<details><summary>flag list</summary>

FLAG_BADGE06_GET [engine, C, home Ch7], FLAG_BADGE08_GET [engine, C], FLAG_DAILY_RECEIVED_BERRY_SOOTOPOLIS [2753], FLAG_DEFEATED_SOOTOPOLIS_GYM [841], FLAG_HIDDEN_ITEM_10 [engine], FLAG_HIDDEN_ITEM_11 [engine], FLAG_HIDDEN_ITEM_12 [engine], FLAG_HIDDEN_ITEM_13 [engine], FLAG_HIDDEN_ITEM_14 [engine], FLAG_HIDDEN_ITEM_15 [engine], FLAG_HIDDEN_ITEM_16 [engine], FLAG_HIDDEN_ITEM_17 [engine], FLAG_HIDDEN_ITEM_18 [engine], FLAG_HIDDEN_ITEM_19 [engine], FLAG_HIDDEN_ITEM_1A [engine], FLAG_HIDDEN_ITEM_24 [engine], FLAG_HIDDEN_ITEM_26 [engine], FLAG_HIDDEN_ITEM_5C [engine], FLAG_HIDDEN_ITEM_5D [engine], FLAG_HIDDEN_ITEM_5E [engine], FLAG_HIDDEN_ITEM_8 [engine], FLAG_HIDDEN_ITEM_9 [engine], FLAG_HIDDEN_ITEM_A [engine], FLAG_HIDDEN_ITEM_B [engine], FLAG_HIDDEN_ITEM_C [engine], FLAG_HIDDEN_ITEM_D [engine], FLAG_HIDDEN_ITEM_E [engine], FLAG_HIDDEN_ITEM_F [engine], FLAG_HIDE_AWAKENED_MON_SEAFLOOR_CAVERN [844], FLAG_HIDE_CAVE_OF_ORIGIN_ENTRANCE_WOMAN_1 [845], FLAG_HIDE_CAVE_OF_ORIGIN_ENTRANCE_WOMAN_2 [846], FLAG_HIDE_EVIL_LEADER_ROUTE128 [847], FLAG_HIDE_EVIL_LEADER_SEAFLOOR_CAVERN [849], FLAG_HIDE_EVIL_TEAM_GRUNTS_SEAFLOOR_CAVERN [852], FLAG_HIDE_LEADER_MT_PYRE_SUMMIT [666, home Ch8], FLAG_HIDE_LEGEND_MON_CAVE_OF_ORIGIN [858], FLAG_HIDE_OTHER_LEADER_ROUTE128 [867], FLAG_HIDE_OTHER_LEADER_SEAFLOOR_CAVERN [868], FLAG_HIDE_OTHER_TEAM_GRUNTS_SEAFLOOR_CAVERN [869], FLAG_HIDE_SLEEPING_MON_SEAFLOOR_CAVERN [870], FLAG_HIDE_SOOTOPOLIS_RESIDENTS [874], FLAG_HIDE_STEVEN_ROUTE128 [875], FLAG_HIDE_STEVEN_SOOTOPOLIS [876], FLAG_HIDE_STEVEN_STEVENS_HOUSE [877], FLAG_HIDE_UNDERWATER_SUBMARINE_INTERACTION [879], FLAG_HIDE_WALLACE_SOOTOPOLIS [881], FLAG_HIDE_WALLACE_SOOTOPOLIS_GYM [884], FLAG_LANDMARK_SEAFLOOR_CAVERN [885, C], FLAG_LEGENDARY_BATTLE_COMPLETED [2074], FLAG_LEGEND_ESCAPED_SEAFLOOR_CAVERN [2075], FLAG_RECEIVED_TM31 [887], FLAG_RECEIVED_TM_WATER_PULSE [899], FLAG_RECEIVED_WAILMER_DOLL [901], FLAG_RETURNED_RED_OR_BLUE_ORB [902], FLAG_SYS_CTRL_OBJ_DELETE [556, C, home Ch6], FLAG_SYS_WEATHER_CTRL [903, C], FLAG_VISITED_SOOTOPOLIS_CITY [905, C]

</details>

Vars used (7): VAR_CAVE_OF_ORIGIN_B4F_STATE [0x40DF], VAR_ICE_STEP_COUNT [0x40E0, C], VAR_MT_PYRE_STATE [0x40C9, home Ch8], VAR_ROUTE128_STATE [0x40E2], VAR_SEAFLOOR_CAVERN_STATE [0x40E3], VAR_SOOTOPOLIS_STATE [0x40ED], VAR_STEVENS_HOUSE_STATE [0x40D8, home Ch9]

Reads ids written by other chapters:

- from Ch6: FLAG_SYS_CTRL_OBJ_DELETE
- from Ch7: FLAG_BADGE06_GET, FLAG_SYS_CTRL_OBJ_DELETE
- from Ch8: FLAG_SYS_CTRL_OBJ_DELETE
- from Ch12: FLAG_SYS_CTRL_OBJ_DELETE
- from Ch13: FLAG_SYS_CTRL_OBJ_DELETE

Trainers: TRAINER_ALEXA, TRAINER_ANDREA, TRAINER_BRIANNA_2, TRAINER_BRIDGET, TRAINER_CONNIE, TRAINER_CRISSY, TRAINER_ISAIAH_1, TRAINER_KATELYN_1, TRAINER_MARISSA, TRAINER_OLIVIA, TRAINER_RUBEN, TRAINER_SEAFLOOR_CAVERN_GRUNT_1, TRAINER_SEAFLOOR_CAVERN_GRUNT_2, TRAINER_SEAFLOOR_CAVERN_GRUNT_3, TRAINER_SEAFLOOR_CAVERN_GRUNT_4, TRAINER_SEAFLOOR_CAVERN_GRUNT_5, TRAINER_TIFFANY, TRAINER_WALLACE, TRAINER_WAYNE

- Note: Needs Dive (no Gen 5 equivalent) for Underwater1-4 and both entrances; or a redesign (e.g. warp tiles).

### Ch11 - Ever Grande, Victory Road (Wally), Elite Four, Champion Steven, Hall of Fame

**BLOCKED** - blocked by: VictoryRoad_1F, VictoryRoad_B1F, VictoryRoad_B2F, EverGrandeCity_HallOfFame

Size: 926 script lines in 166 labels (+341 text lines in owned maps); 18 trainerbattle commands, 17 unique trainers; 34 flags, 3 vars.

Story beats (in order; `map: label`):

1. `EverGrandeCity`: `EverGrandeCity_EventScript_SetVisitedEverGrande` - arrive at Ever Grande
2. `VictoryRoad_1F`: `VictoryRoad_1F_EventScript_WallyTrigger0` - Wally at the Victory Road entrance -> WallyApproachPlayer (TRAINER_WALLY_1)
3. `VictoryRoad_1F`: `VictoryRoad_1F_EventScript_Wally` - Wally rematch inside (TRAINER_WALLY_3)
4. `EverGrandeCity_PokemonLeague`: `EverGrandeCity_PokemonLeague_1F_EventScript_DoorGuard` - badge check (FLAG_ENTERED_ELITE_FOUR)
5. `EverGrandeCity_SidneysRoom`: `EverGrandeCity_SidneysRoom_EventScript_Sidney` - Sidney, Phoebe, Glacia, Drake (elite_four.inc, VAR_ELITE_4_STATE)
6. `EverGrandeCity_ChampionsRoom`: `EverGrandeCity_ChampionsRoom_EventScript_Steven` - Champion Steven -> rival + Birch arrive (BirchArrivesExitForHoF, Pokedex rating)
7. `EverGrandeCity_HallOfFame`: `EverGrandeCity_HallOfFame_EventScript_EnterHallOfFame` - Hall of Fame -> SetGameClearFlags (hall_of_fame.inc) -> credits

Foreign beats this chapter writes into other chapters' files (scene includes):

- `PetalburgCity_WallysHouse` [PetalburgCity_WallysHouse_EventScript_GiveHMSurfAfterVictoryRoad .. PetalburgCity_WallysHouse_EventScript_GiveHMSurf) ~4 lines - Wally's dad after Victory Road

Other chapters' beats inside this chapter's files (reserve slots for them):

- Ch13: `data/scripts/hall_of_fame.inc` from `EverGrandeCity_HallOfFame_EventScript_ShowStevensBeldum` - post-game state set at the Hall of Fame (Beldum, HM08 ball, S.S. Ticket event, Lati TV)

Maps (26): owned (port the whole file) / touched (warps, flags, foreign beats):

| map | role | status |
|---|---|---|
| EverGrandeCity | owned, main path | built (outdoor zone 412) |
| EverGrandeCity_ChampionsRoom | owned, main path | built (room auto, zone 34) |
| EverGrandeCity_Corridor1 | owned, main path | built (room auto, zone 35) |
| EverGrandeCity_Corridor2 | owned, main path | built (room auto, zone 36) |
| EverGrandeCity_Corridor3 | owned, main path | built (room auto, zone 42) |
| EverGrandeCity_Corridor4 | owned, main path | built (room big, zone 43) |
| EverGrandeCity_Corridor5 | owned, main path | built (room auto, zone 47) |
| EverGrandeCity_DrakesRoom | owned, main path | built (room auto, zone 51) |
| EverGrandeCity_GlaciasRoom | owned, main path | built (room auto, zone 53) |
| EverGrandeCity_HallOfFame | owned, main path | **NOT BUILT (status link = left out; zone 57)** |
| EverGrandeCity_PhoebesRoom | owned, main path | built (room auto, zone 123) |
| EverGrandeCity_PokemonLeague | owned, main path | built (room auto, zone 77) |
| EverGrandeCity_SidneysRoom | owned, main path | built (room auto, zone 79) |
| VictoryRoad_1F | owned, main path | **NOT BUILT (cave; zone 170 allocated, no room file)** |
| VictoryRoad_B1F | owned, main path | **NOT BUILT (cave; zone 171 allocated, no room file)** |
| VictoryRoad_B2F | owned, main path | **NOT BUILT (cave; zone 172 allocated, no room file)** |
| EverGrandeCity_PokemonCenter_1F | owned | built (room center, zone 8) |
| EverGrandeCity_PokemonCenter_2F | owned | built (room center, zone 66) |
| LilycoveCity_CoveLilyMotel_2F | objects/triggers switched by this chapter, owner Ch8 | built (room auto, zone 180) |
| LilycoveCity_Harbor | objects/triggers switched by this chapter, owner Ch13 | built (room auto, zone 203) |
| MossdeepCity_StevensHouse | objects/triggers switched by this chapter, owner Ch9 | built (room auto, zone 339) |
| PetalburgCity_Gym | objects/triggers switched by this chapter, owner Ch1 | built (room big, zone 452) |
| PetalburgCity_WallysHouse | foreign beat | built (room auto, zone 500) |
| SSTidalCorridor | objects/triggers switched by this chapter, owner Ch13 | **NOT BUILT (in no zone list)** |
| SlateportCity_Harbor | objects/triggers switched by this chapter, owner Ch3 | built (room auto, zone 596) |
| SlateportCity_SternsShipyard_1F | objects/triggers switched by this chapter, owner Ch3 | built (room auto, zone 14) |

Flags used (34; 5 item-ball flags; 19 have this chapter as home):

<details><summary>flag list</summary>

FLAG_BADGE06_GET [engine, C, home Ch7], FLAG_DEFEATED_ELITE_4_DRAKE [962], FLAG_DEFEATED_ELITE_4_GLACIA [966], FLAG_DEFEATED_ELITE_4_PHOEBE [967], FLAG_DEFEATED_ELITE_4_SYDNEY [987], FLAG_DEFEATED_WALLY_VICTORY_ROAD [988], FLAG_ENTERED_ELITE_FOUR [990], FLAG_HIDDEN_ITEM_51 [engine], FLAG_HIDDEN_ITEM_52 [engine], FLAG_HIDDEN_ITEM_53 [engine], FLAG_HIDE_BIRCH_CHAMPIONS_ROOM [997], FLAG_HIDE_BRINEY_AND_PEEKO_SS_TIDAL [998], FLAG_HIDE_BRINEY_SLATEPORT_SHIPYARD [755, home Ch9], FLAG_HIDE_LILYCOVE_MOTEL_PEOPLE [999], FLAG_HIDE_PETALBURG_GYM_GUIDE [543, home Ch6], FLAG_HIDE_RIVAL_CHAMPIONS_ROOM [1000], FLAG_HIDE_SS_TIDAL_LILYCOVE_HARBOR [1002], FLAG_HIDE_SS_TIDAL_SLATEPORT_HARBOR [367, home Ch3], FLAG_HIDE_STEVENS_LETTER [1005], FLAG_HIDE_WALLY_BATTLE_VICTORY_ROAD [1006], FLAG_HIDE_WALLY_DEFEATED_VICTORY_ROAD [1012], FLAG_LATIOS_OR_LATIAS_ROAMING [home S_optional], FLAG_RECEIVED_BELDUM [1506, home Ch13], FLAG_RECEIVED_HM08 [789, home Ch9], FLAG_RECEIVED_HM_SURF [553, home Ch6], FLAG_RECEIVED_SS_TICKET [1509, home Ch13], FLAG_SYS_POKEMON_LEAGUE_FLY [1013, C], FLAG_SYS_WEATHER_CTRL [903, C, home Ch10], FLAG_VISITED_EVER_GRANDE_CITY [1015, C]

</details>

Vars used (3): VAR_ELITE_4_STATE [0x40F4], VAR_STEVENS_HOUSE_STATE [0x40D8, home Ch9], VAR_VICTORY_ROAD_1F_STATE [0x40F5]

Reads ids written by other chapters:

- from Ch6: FLAG_RECEIVED_HM_SURF
- from Ch7: FLAG_BADGE06_GET
- from Ch9: FLAG_RECEIVED_HM08
- from Ch10: FLAG_SYS_WEATHER_CTRL
- from Ch13: FLAG_RECEIVED_BELDUM, FLAG_RECEIVED_SS_TICKET

Trainers: TRAINER_ALBERT, TRAINER_CAROLINE, TRAINER_DRAKE, TRAINER_EDGAR, TRAINER_GLACIA, TRAINER_HOPE, TRAINER_JULIE, TRAINER_MICHELLE, TRAINER_OWEN, TRAINER_PHOEBE, TRAINER_SAMUEL, TRAINER_SHANNON, TRAINER_SIDNEY, TRAINER_STEVEN, TRAINER_VITO, TRAINER_WALLY_1, TRAINER_WALLY_3

- Note: EverGrandeCity_HallOfFame is status "link" (left out) in data/hoenn_interiors.json: it must be built for the ending.

### Ch12 - Southern seas (optional, pre-League): Routes 129-134, Pacifidlog; Regi puzzle

**UNBLOCKED**

Size: 822 script lines in 158 labels (+140 text lines in owned maps); 26 trainerbattle commands, 25 unique trainers; 20 flags, 0 vars.

- optional block **Regi puzzle (Dive + braille)**: 414 lines, 0 trainerbattle cmds in owned files; NOT BUILT: Underwater_Route134, Underwater_SealedChamber, SealedChamber_OuterRoom, SealedChamber_InnerRoom, DesertRuins, IslandCave, AncientTomb

Story beats (in order; `map: label`):

1. `PacifidlogTown`: `PacifidlogTown_OnTransition` - Pacifidlog (fly point)
2. `PacifidlogTown_House2`: `PacifidlogTown_House2_EventScript_FanClubYoungerBrother` - weekly Return/Frustration TM
3. `PacifidlogTown_House3`: `PacifidlogTown_House3_EventScript_Trader` - in-game trade
4. `SealedChamber_InnerRoom`: `SealedChamber_InnerRoom_EventScript_15F1E8` - (optional) Sealed Chamber: Relicanth + Wailord opens the Regi doors (FLAG_REGI_DOORS_OPENED)
5. `DesertRuins`: `DesertRuins_EventScript_15CB85` - (optional) Regirock; IslandCave_EventScript_15EF9D Regice; AncientTomb_EventScript_15F050 Registeel

Other chapters' beats inside this chapter's files (reserve slots for them):

- Ch13: `Route131` from `Route131_MapScript1_152444` - Sky Pillar appears after the Hall of Fame (setmaplayoutindex)

Maps (25): owned (port the whole file) / touched (warps, flags, foreign beats):

| map | role | status |
|---|---|---|
| PacifidlogTown | owned, main path | built (outdoor zone 458) |
| Route129 | owned, main path | built (outdoor zone 238) |
| Route130 | owned, main path | built (outdoor zone 240) |
| Route131 | owned, main path | built (outdoor zone 444) |
| Route132 | owned, main path | built (outdoor zone 456) |
| Route133 | owned, main path | built (outdoor zone 461) |
| Route134 | owned, main path | built (outdoor zone 7) |
| AncientTomb | owned, optional: Regi puzzle | **NOT BUILT (cave; zone 94 allocated, no room file)** |
| DesertRuins | owned, optional: Regi puzzle | **NOT BUILT (cave; zone 116 allocated, no room file)** |
| IslandCave | owned, optional: Regi puzzle | **NOT BUILT (cave; zone 127 allocated, no room file)** |
| PacifidlogTown_House1 | owned | built (room auto, zone 405) |
| PacifidlogTown_House2 | owned | built (room auto, zone 414) |
| PacifidlogTown_House3 | owned | built (room auto, zone 418) |
| PacifidlogTown_House4 | owned | built (room auto, zone 430) |
| PacifidlogTown_House5 | owned | built (room auto, zone 440) |
| PacifidlogTown_PokemonCenter_1F | owned | built (room center, zone 407) |
| PacifidlogTown_PokemonCenter_2F | owned | built (room center, zone 450) |
| SealedChamber_InnerRoom | owned, optional: Regi puzzle | **NOT BUILT (in no zone list)** |
| SealedChamber_OuterRoom | owned, optional: Regi puzzle | **NOT BUILT (in no zone list)** |
| Underwater_Route134 | owned, optional: Regi puzzle | **NOT BUILT (in no zone list)** |
| Underwater_SealedChamber | owned, optional: Regi puzzle | **NOT BUILT (in no zone list)** |
| Route105 | warp from an owned map, owner Ch6 | built (outdoor zone 331) |
| Route111 | warp from an owned map, owner Ch4 | built (outdoor zone 370) |
| Route120 | warp from an owned map, owner Ch7 | built (outdoor zone 474) |
| SkyPillar_Entrance | warp from an owned map, owner Ch13 | **NOT BUILT (cave; zone 169 allocated, no room file)** |

Flags used (20; 3 item-ball flags; 16 have this chapter as home):

<details><summary>flag list</summary>

FLAG_HIDE_REGICE [1059], FLAG_HIDE_REGIROCK [1060], FLAG_HIDE_REGISTEEL [1061], FLAG_LANDMARK_ANCIENT_TOMB [1062, C], FLAG_LANDMARK_DESERT_RUINS [1063, C], FLAG_LANDMARK_ISLAND_CAVE [1064, C], FLAG_LANDMARK_SEALED_CHAMBER [1065, C], FLAG_MET_FANCLUB_YOUNGER_BROTHER [1066], FLAG_PACIFIDLOG_NPC_TRADE_COMPLETED [1067], FLAG_RECEIVED_FANCLUB_TM_THIS_WEEK [1068], FLAG_REGI_DOORS_OPENED [1069], FLAG_SYS_BRAILLE_DIG [1070, C], FLAG_SYS_BRAILLE_FLY [1071, C], FLAG_SYS_BRAILLE_STRENGTH [1072, C], FLAG_SYS_BRAILLE_WAIT [1073, C], FLAG_SYS_CTRL_OBJ_DELETE [556, C, home Ch6], FLAG_VISITED_PACIFIDLOG_TOWN [1074, C]

</details>

Vars used (0): 

Reads ids written by other chapters:

- from Ch6: FLAG_SYS_CTRL_OBJ_DELETE
- from Ch7: FLAG_SYS_CTRL_OBJ_DELETE
- from Ch8: FLAG_SYS_CTRL_OBJ_DELETE
- from Ch10: FLAG_SYS_CTRL_OBJ_DELETE
- from Ch13: FLAG_SYS_CTRL_OBJ_DELETE

Trainers: TRAINER_AARON, TRAINER_ALEX, TRAINER_ALLISON, TRAINER_BECK, TRAINER_CHASE, TRAINER_DANA, TRAINER_DEBRA, TRAINER_FRANKLIN, TRAINER_GILBERT, TRAINER_HERMAN, TRAINER_HITOSHI, TRAINER_JACK, TRAINER_KARA, TRAINER_KATIE, TRAINER_KIYO, TRAINER_LAUREL, TRAINER_LINDA, TRAINER_REED, TRAINER_RELI_AND_IAN, TRAINER_RICHARD, TRAINER_RODNEY, TRAINER_RONALD, TRAINER_SUSIE, TRAINER_TISHA, TRAINER_WARREN

- Note: Routes 129-134 are trainers + currents only; reached from Route 128 (Ch10 area). Small: merge with Ch6 for one agent.
- Note: Route131 holds the Sky Pillar appearance check (FLAG_SYS_GAME_CLEAR): Ch13 beat.

### Ch13 - Post-game (optional): S.S. Ticket, S.S. Tidal, Battle Tower, Southern Island, Sky Pillar (Rayquaza), Beldum

**BLOCKED (optional chapter)** - blocked by: BattleTower_Corridor, BattleTower_Elevator, SSTidalCorridor, SSTidalLowerDeck, SSTidalRooms, SkyPillar_1F, SkyPillar_2F, SkyPillar_3F, SkyPillar_4F, SkyPillar_5F, SkyPillar_Entrance | in progress: BattleTower_Outside, SkyPillar_Outside, SkyPillar_Top, SouthernIsland_Exterior, SouthernIsland_Interior

Size: 1701 script lines in 259 labels (+406 text lines in owned maps); 9 trainerbattle commands, 8 unique trainers; 30 flags, 5 vars.

- optional block **S.S. Tidal + harbors**: 463 lines, 9 trainerbattle cmds in owned files; NOT BUILT: SSTidalCorridor, SSTidalLowerDeck, SSTidalRooms
- optional block **Battle Tower**: 702 lines, 0 trainerbattle cmds in owned files; NOT BUILT: BattleTower_Elevator, BattleTower_Corridor; in progress: BattleTower_Outside
- optional block **Southern Island (Eon Ticket)**: 144 lines, 0 trainerbattle cmds in owned files; NOT BUILT: -; in progress: SouthernIsland_Exterior, SouthernIsland_Interior
- optional block **Sky Pillar (Rayquaza)**: 62 lines, 0 trainerbattle cmds in owned files; NOT BUILT: SkyPillar_Entrance, SkyPillar_1F, SkyPillar_2F, SkyPillar_3F, SkyPillar_4F, SkyPillar_5F; in progress: SkyPillar_Outside, SkyPillar_Top

Story beats (in order; `map: label`):

1. `data/scripts/hall_of_fame.inc`: `EverGrandeCity_HallOfFame_EventScript_ReadyReceiveSSTicketEvent` - after the credits: Norman at home
2. `data/scripts/players_house.inc`: `PlayersHouse_1F_EventScript_GetSSTicketAndSeeLatiTV` - S.S. Ticket + roaming Lati TV report (Ch0 file)
3. `SlateportCity_Harbor`: `SlateportCity_Harbor_EventScript_FerryAttendant` - S.S. Tidal: Slateport <-> Lilycove / Battle Tower (Ch3 file); LilycoveCity_Harbor same
4. `SSTidalCorridor`: `SSTidalCorridor_MapScript2_15FC9A` - S.S. Tidal cabins, trainers, arrival
5. `BattleTower_Lobby`: `BattleTower_Lobby_MapScript1_160293` - Battle Tower (the PWT is planned here: notes/RESEARCH_PWT.md)
6. `SouthernIsland_Interior`: `SouthernIsland_Interior_EventScript_160BA7` - Eon Ticket: the island Lati (the other one roams after the Hall of Fame)
7. `SkyPillar_Top`: `SkyPillar_Top_EventScript_15F316` - Rayquaza
8. `MossdeepCity_StevensHouse`: `MossdeepCity_StevensHouse_EventScript_BeldumPokeball` - Beldum (Ch9 file)

Foreign beats this chapter writes into other chapters' files (scene includes):

- `data/scripts/players_house.inc` [PlayersHouse_1F_EventScript_GetSSTicketAndSeeLatiTV .. end of file) ~136 lines - Dad brings the S.S. Ticket, Lati TV report
- `data/scripts/hall_of_fame.inc` [EverGrandeCity_HallOfFame_EventScript_ShowStevensBeldum .. end of file) ~14 lines - post-game state set at the Hall of Fame (Beldum, HM08 ball, S.S. Ticket event, Lati TV)
- `LittlerootTown` [LittlerootTown_EventScript_SetExitedHouseAfterLatiSSTicketEvent .. LittlerootTown_EventScript_MoveMomToMaysDoor) ~4 lines - state after the S.S. Ticket scene
- `LittlerootTown` [LittlerootTown_EventScript_BeginDexUpgradeScene .. LittlerootTown_EventScript_FatMan) ~5 lines - dex-upgrade state hook
- `SlateportCity_Harbor` [SlateportCity_Harbor_EventScript_FerryAttendant .. SlateportCity_Harbor_EventScript_Sailor) ~87 lines - S.S. Tidal ferry from Slateport
- `SlateportCity_SternsShipyard_1F` [SlateportCity_SternsShipyard_1F_EventScript_FerryReady .. SlateportCity_SternsShipyard_1F_EventScript_GoFindStern) ~12 lines - ferry finished
- `MossdeepCity_StevensHouse` [MossdeepCity_StevensHouse_EventScript_BeldumPokeball .. MossdeepCity_StevensHouse_EventScript_RockDisplay) ~31 lines - Steven's Beldum
- `MossdeepCity_StevensHouse` [MossdeepCity_StevensHouse_EventScript_Letter .. MossdeepCity_StevensHouse_EventScript_DiveItemBall) ~10 lines - Steven's letter
- `Route131` [Route131_MapScript1_152444 .. Route131_EventScript_152452) ~6 lines - Sky Pillar appears after the Hall of Fame (setmaplayoutindex)

Maps (31): owned (port the whole file) / touched (warps, flags, foreign beats):

| map | role | status |
|---|---|---|
| BattleTower_BattleRoom | owned, optional: Battle Tower | built (room auto, zone 15) |
| BattleTower_Corridor | owned, optional: Battle Tower | **NOT BUILT (in no zone list)** |
| BattleTower_Elevator | owned, optional: Battle Tower | **NOT BUILT (in no zone list)** |
| BattleTower_Lobby | owned, optional: Battle Tower | built (room auto, zone 21) |
| BattleTower_Outside | owned, optional: Battle Tower | **in progress (standalone map, zone 17: built in the standalone agent's test ROM, proof work/agents/standalone/proofs/BattleTower_Outside.png; not in the main build yet, hoenn_standalone.json "build" is empty)** |
| LilycoveCity_EmptyMap | owned, optional: S.S. Tidal + harbors | built (room auto, zone 202) |
| LilycoveCity_Harbor | owned, optional: S.S. Tidal + harbors | built (room auto, zone 203) |
| SSTidalCorridor | owned, optional: S.S. Tidal + harbors | **NOT BUILT (in no zone list)** |
| SSTidalLowerDeck | owned, optional: S.S. Tidal + harbors | **NOT BUILT (in no zone list)** |
| SSTidalRooms | owned, optional: S.S. Tidal + harbors | **NOT BUILT (in no zone list)** |
| SkyPillar_1F | owned, optional: Sky Pillar | **NOT BUILT (cave; zone 164 allocated, no room file)** |
| SkyPillar_2F | owned, optional: Sky Pillar | **NOT BUILT (cave; zone 165 allocated, no room file)** |
| SkyPillar_3F | owned, optional: Sky Pillar | **NOT BUILT (cave; zone 166 allocated, no room file)** |
| SkyPillar_4F | owned, optional: Sky Pillar | **NOT BUILT (cave; zone 167 allocated, no room file)** |
| SkyPillar_5F | owned, optional: Sky Pillar | **NOT BUILT (cave; zone 168 allocated, no room file)** |
| SkyPillar_Entrance | owned, optional: Sky Pillar | **NOT BUILT (cave; zone 169 allocated, no room file)** |
| SkyPillar_Outside | owned, optional: Sky Pillar | **in progress (standalone map, zone 98: built in the standalone agent's test ROM, proof work/agents/standalone/proofs/SkyPillar_Outside.png; not in the main build yet, hoenn_standalone.json "build" is empty)** |
| SkyPillar_Top | owned, optional: Sky Pillar | **in progress (standalone map, zone 108: built in the standalone agent's test ROM, proof work/agents/standalone/proofs/SkyPillar_Top.png; not in the main build yet, hoenn_standalone.json "build" is empty)** |
| SouthernIsland_Exterior | owned, optional: Southern Island | **in progress (standalone map, zone 111: built in the standalone agent's test ROM, proof work/agents/standalone/proofs/SouthernIsland_Exterior.png; not in the main build yet, hoenn_standalone.json "build" is empty)** |
| SouthernIsland_Interior | owned, optional: Southern Island | **in progress (standalone map, zone 112: built in the standalone agent's test ROM, proof work/agents/standalone/proofs/SouthernIsland_Interior.png; not in the main build yet, hoenn_standalone.json "build" is empty)** |
| EverGrandeCity_HallOfFame | ref, owner Ch11 | **NOT BUILT (status link = left out; zone 57)** |
| InsideOfTruck | objects/triggers switched by this chapter, owner Ch0 | built (hand, zone 394 truck: data/interiors/394.json) |
| LilycoveCity | scripted warp/ref, owner Ch8 | built (outdoor zone 96) |
| LittlerootTown | foreign beat | built (outdoor zone 389) |
| LittlerootTown_BrendansHouse_1F | objects/triggers switched by this chapter, owner Ch0 | built (room hand, zone 390) |
| LittlerootTown_MaysHouse_1F | objects/triggers switched by this chapter, owner Ch0 | built (room hand, zone 392) |
| MossdeepCity_StevensHouse | foreign beat | built (room auto, zone 339) |
| PetalburgCity | scripted warp/ref, owner Ch1 | built (outdoor zone 439) |
| Route131 | foreign beat, optional: Sky Pillar | built (outdoor zone 444) |
| SlateportCity_Harbor | foreign beat, optional: S.S. Tidal + harbors | built (room auto, zone 596) |
| SlateportCity_SternsShipyard_1F | foreign beat | built (room auto, zone 14) |

Flags used (30; 1 item-ball flags; 24 have this chapter as home):

<details><summary>flag list</summary>

FLAG_DEFEATED_SS_TIDAL_TRAINERS [1091], FLAG_ENCOUNTERED_LATIAS_OR_LATIOS [1092], FLAG_HIDDEN_ITEM_23 [engine], FLAG_HIDE_AWARD_MAN_BATTLE_TOWER [1093], FLAG_HIDE_BATTLE_TOWER_OPPONENT [1094], FLAG_HIDE_BELDUM_BALL_STEVENS_HOUSE [1095], FLAG_HIDE_BRINEY_AND_PEEKO_SS_TIDAL [998, home Ch11], FLAG_HIDE_FERRY_ATTENDANT_LILYCOVE [1096], FLAG_HIDE_FERRY_SAILOR_LILYCOVE [1097], FLAG_HIDE_LATIOS_OR_LATIAS_FLYING [1098], FLAG_HIDE_LATIOS_OR_LATIAS_STATIONARY [1099], FLAG_HIDE_NORMAN_LITTLEROOT [2064], FLAG_HIDE_RAYQUAZA [1500], FLAG_HIDE_REPORTER_BATTLE_TOWER [1501], FLAG_HIDE_SS_TIDAL_LILYCOVE_HARBOR [1002, home Ch11], FLAG_HIDE_TM_49_GIVER_SS_TIDAL [1502], FLAG_LANDMARK_BATTLE_TOWER [1503, C], FLAG_LANDMARK_SKY_PILLAR [1504, C], FLAG_LANDMARK_SOUTHERN_ISLAND [1505, C], FLAG_OMIT_DIVE_FROM_STEVEN_LETTER [787, home Ch9], FLAG_RECEIVED_BELDUM [1506], FLAG_RECEIVED_GOLD_SHIELD [1507], FLAG_RECEIVED_SILVER_SHIELD [1508], FLAG_RECEIVED_SS_TICKET [1509], FLAG_RECEIVED_TM49 [1510], FLAG_SYS_CTRL_OBJ_DELETE [556, C, home Ch6], FLAG_SYS_GAME_CLEAR [engine 2400, C, home Ch1], FLAG_SYS_HAS_EON_TICKET [1511, C], FLAG_SYS_TV_LATI [1512, C]

</details>

Vars used (5): VAR_BRAVO_TRAINER_BATTLE_TOWER_ON [0x4102, C], VAR_LITTLEROOT_HOUSES_STATE [0x404F, home Ch0], VAR_LITTLEROOT_HOUSES_STATE_2 [0x4050, home Ch0], VAR_LITTLEROOT_INTRO_STATE [0x404E, home Ch0], VAR_PORTHOLE_STATE [0x4103, C]

Reads ids written by other chapters:

- from Ch6: FLAG_SYS_CTRL_OBJ_DELETE
- from Ch7: FLAG_SYS_CTRL_OBJ_DELETE
- from Ch8: FLAG_SYS_CTRL_OBJ_DELETE
- from Ch9: FLAG_OMIT_DIVE_FROM_STEVEN_LETTER
- from Ch10: FLAG_SYS_CTRL_OBJ_DELETE
- from Ch11: FLAG_HIDE_BRINEY_AND_PEEKO_SS_TIDAL, FLAG_HIDE_SS_TIDAL_LILYCOVE_HARBOR
- from Ch12: FLAG_SYS_CTRL_OBJ_DELETE

Trainers: TRAINER_ANETTE, TRAINER_COLTON, TRAINER_GARRET, TRAINER_LEA_AND_JED, TRAINER_LEONARD, TRAINER_PHILLIP, TRAINER_THOMAS, TRAINER_TUCKER

## 4. Shared scripts and systems (not chapters)

### S_common - Common scripts every chapter calls (lead, before the chapters start)

Files: `data/event_scripts.s` (1520), `data/scripts/std_msgbox.inc` (31), `data/scripts/trainer_battle.inc` (120), `data/scripts/obtain_item.inc` (140), `data/scripts/pkmn_center_nurse.inc` (51), `data/scripts/movement.inc` (57), `data/scripts/dynamic_npc_graphics.inc` (52), `data/scripts/set_gym_trainers.inc` (66), `data/item_ball_scripts.inc` (405), `data/field_move_scripts.inc` (253), `data/scripts/surf.inc` (16), `data/scripts/pc.inc` (58), `data/scripts/berry_tree.inc` (161), `data/scripts/cave_hole.inc` (29), `data/scripts/static_pokemon.inc` (158)

Lines kept in this group (labels not routed to a chapter): 1923; flags 15, vars 1.

Flags: FLAG_BADGE01_GET [engine], FLAG_BADGE03_GET [engine], FLAG_BADGE04_GET [engine], FLAG_HIDE_MR_BRINEY_BOAT_DEWFORD [277], FLAG_HIDE_MR_BRINEY_BOAT_ROUTE104 [278], FLAG_HIDE_MR_BRINEY_BOAT_ROUTE109 [279], FLAG_HIDE_MR_BRINEY_DEWFORD_TOWN [280], FLAG_HIDE_MR_BRINEY_ROUTE104 [281], FLAG_HIDE_MR_BRINEY_ROUTE104_HOUSE [282], FLAG_HIDE_MR_BRINEY_ROUTE109 [283], FLAG_HIDE_PEEKO_BRINEY_HOUSE [284], FLAG_POKERUS_EXPLAINED [2343], FLAG_SYS_GAME_CLEAR [engine 2400], FLAG_SYS_PC_LANETTE [488], FLAG_SYS_USE_STRENGTH [2344]

Vars: VAR_ICE_STEP_COUNT [0x40E0]

### S_optional - Optional systems (decide per system; Black 2 has no equivalent for most)

Files: `data/scripts/contest_hall.inc` (1168), `data/scripts/secret_base.inc` (613), `data/scripts/shared_secret_base.inc` (164), `data/scripts/secret_power_tm.inc` (64), `data/scripts/check_furniture.inc` (21), `data/scripts/tv.inc` (84), `data/scripts/gabby_and_ty.inc` (271), `data/scripts/record_mix.inc` (21), `data/scripts/cable_club.inc` (723), `data/scripts/mystery_event_club.inc` (94)

Maps: LinkContestRoom1 (357, NOT BUILT), LinkContestRoom2 (0, NOT BUILT), LinkContestRoom3 (0, NOT BUILT), LinkContestRoom4 (0, NOT BUILT), LinkContestRoom5 (0, NOT BUILT), LinkContestRoom6 (0, NOT BUILT), SecretBase_BlueCave1 (0, NOT BUILT), SecretBase_BlueCave2 (0, NOT BUILT), SecretBase_BlueCave3 (0, NOT BUILT), SecretBase_BlueCave4 (0, NOT BUILT), SecretBase_BrownCave1 (0, NOT BUILT), SecretBase_BrownCave2 (0, NOT BUILT), SecretBase_BrownCave3 (0, NOT BUILT), SecretBase_BrownCave4 (0, NOT BUILT), SecretBase_RedCave1 (0, NOT BUILT), SecretBase_RedCave2 (0, NOT BUILT), SecretBase_RedCave3 (0, NOT BUILT), SecretBase_RedCave4 (0, NOT BUILT), SecretBase_YellowCave1 (0, NOT BUILT), SecretBase_YellowCave2 (0, NOT BUILT), SecretBase_YellowCave3 (0, NOT BUILT), SecretBase_YellowCave4 (0, NOT BUILT), SecretBase_Shrub1 (0, NOT BUILT), SecretBase_Shrub2 (0, NOT BUILT), SecretBase_Shrub3 (0, NOT BUILT), SecretBase_Shrub4 (0, NOT BUILT), SecretBase_Tree1 (0, NOT BUILT), SecretBase_Tree2 (0, NOT BUILT), SecretBase_Tree3 (0, NOT BUILT), SecretBase_Tree4 (0, NOT BUILT), TradeCenter (2, NOT BUILT), SingleBattleColosseum (2, NOT BUILT), DoubleBattleColosseum (2, NOT BUILT), RecordCorner (2, NOT BUILT)

Lines kept in this group (labels not routed to a chapter): 2619; flags 26, vars 6.

Flags: FLAG_CONTEST_SKETCH_CREATED [447], FLAG_DECORATION_1, FLAG_DECORATION_10, FLAG_DECORATION_11, FLAG_DECORATION_12, FLAG_DECORATION_13, FLAG_DECORATION_14, FLAG_DECORATION_15, FLAG_DECORATION_2, FLAG_DECORATION_3, FLAG_DECORATION_4, FLAG_DECORATION_5, FLAG_DECORATION_6, FLAG_DECORATION_7, FLAG_DECORATION_8, FLAG_DECORATION_9, FLAG_LATIOS_OR_LATIAS_ROAMING, FLAG_LINK_CONTEST_ROOM_POKEBALL, FLAG_RECEIVED_CONTEST_PASS, FLAG_RECEIVED_SECRET_POWER [485], FLAG_SECRET_BASE_REGISTRY_ENABLED, FLAG_SYS_GAME_CLEAR [engine 2400], FLAG_SYS_RIBBON_GET [709], FLAG_SYS_TV_LATI [1512], FLAG_SYS_TV_START [419], FLAG_SYS_TV_WATCH

Vars: VAR_CONTEST_LOCATION [0x4072], VAR_CONTEST_PRIZE_PICKUP, VAR_INIT_SECRET_BASE, VAR_LILYCOVE_CONTEST_LOBBY_STATE [0x40C3], VAR_LINK_CONTEST_ROOM_STATE [0x4076], VAR_SECRET_BASE_INITIALIZED [0x403C]

### S_debug - Debug menu scripts (not ported; ignored for setters/readers)

Files: `data/scripts/debug.inc` (512)

Lines kept in this group (labels not routed to a chapter): 511; flags 3, vars 1.

Flags: FLAG_LEGENDARY_BATTLE_COMPLETED [2074], FLAG_LEGEND_ESCAPED_SEAFLOOR_CAVERN [2075], FLAG_SYS_GAME_CLEAR [engine 2400]

Vars: VAR_NEW_MAUVILLE_STATE [0x40B1]

### S_unused - Unused / other version

Maps: Route104_Prototype (83, NOT BUILT), Route104_PrototypePrettyPetalFlowerShop (5, NOT BUILT), LilycoveCity_UnusedMart (2, NOT BUILT), MagmaHideout_1F (2, in progress), MagmaHideout_B1F (9, in progress), MagmaHideout_B2F (2, in progress), UnknownMap_25_29 (0, NOT BUILT), UnknownMap_25_30 (0, NOT BUILT), UnknownMap_25_31 (0, NOT BUILT), UnknownMap_25_32 (0, NOT BUILT), UnknownMap_25_33 (0, NOT BUILT), UnknownMap_25_34 (0, NOT BUILT)

Lines kept in this group (labels not routed to a chapter): 103; flags 13, vars 0.

Flags: FLAG_HIDE_ELECTRODE_1_HIDEOUT [649], FLAG_HIDE_ELECTRODE_2_HIDEOUT [650], FLAG_HIDE_GRUNTS_HIDEOUTS [657], FLAG_HIDE_GRUNT_1_BLOCKING_HIDEOUT [662], FLAG_HIDE_GRUNT_2_BLOCKING_HIDEOUT [664], FLAG_HIDE_SUBMARINE_SHADOW_HIDEOUT [680], FLAG_ITEM_MAGMA_HIDEOUT_B1F_1 [item ball], FLAG_ITEM_MAGMA_HIDEOUT_B1F_2 [item ball], FLAG_ITEM_MAGMA_HIDEOUT_B1F_3 [item ball], FLAG_ITEM_MAGMA_HIDEOUT_B2F_1 [item ball], FLAG_ROUTE104_PROTOTYPE_COMPLETED_1, FLAG_ROUTE104_PROTOTYPE_COMPLETED_2, FLAG_SYS_CTRL_OBJ_DELETE [556]

Vars: -

Labels of shared files whose name starts with a map name (e.g. event_scripts.s `SlateportCity_OceanicMuseum_1F_EventScript_*`, static_pokemon.inc `Route120_EventScript_HideKecleon*`) are counted in that map's chapter; some unprefixed ones are routed by hand (Mr. Briney's location scripts -> Ch2, Go-Goggles rival -> Ch5, ferry -> Ch13, Kecleon/Devon Scope -> Ch7, ...). Chapter-owned shared files: `data/scripts/players_house.inc` -> Ch0, `data/scripts/prof_birch.inc` -> Ch0, `data/scripts/new_game.inc` -> Ch0, `data/scripts/day_care.inc` -> Ch3, `data/scripts/mauville_man.inc` -> Ch3, `data/scripts/magma_chimney.inc` -> Ch5, `data/scripts/magma_summit.inc` -> Ch8, `data/scripts/safari_zone.inc` -> Ch8, `data/scripts/pokeblocks.inc` -> Ch8, `data/scripts/cave_of_origin.inc` -> Ch10, `data/scripts/elite_four.inc` -> Ch11, `data/scripts/hall_of_fame.inc` -> Ch11

## 5. Ids defined in flags.h / vars.h that no map script uses

**shared scripts only (data/scripts, event_scripts.s)** (32):

FLAG_DAILY_RECEIVED_BERRY_FALLARBOR, FLAG_EVIL_LEADER_PLEASE_STOP, FLAG_LATIOS_OR_LATIAS_ROAMING, FLAG_OCEANIC_MUSEUM_MET_REPORTER, FLAG_POKERUS_EXPLAINED, FLAG_RECEIVED_AMULET_COIN, FLAG_RECEIVED_SS_TICKET, FLAG_SECRET_BASE_REGISTRY_ENABLED, FLAG_SET_WALL_CLOCK, FLAG_SYS_CHAT_USED, FLAG_SYS_EXDATA_ENABLE, FLAG_SYS_HIPSTER_MEET, FLAG_SYS_TV_HOME, FLAG_SYS_TV_LATI, FLAG_SYS_TV_WATCH, FLAG_SYS_USE_STRENGTH, FLAG_UNKNOWN_2E1, FLAG_UNKNOWN_2EB, FLAG_UNKNOWN_2EC, FLAG_UNKNOWN_2ED, FLAG_UNKNOWN_2F4, FLAG_UNKNOWN_30E, FLAG_UNKNOWN_30F, FLAG_UNKNOWN_337, FLAG_UNKNOWN_34B, FLAG_UNKNOWN_34C, FLAG_UNKNOWN_34F, FLAG_UNKNOWN_363, VAR_BIRCH_STATE, VAR_CABLE_CLUB_STATE, VAR_CONTEST_PRIZE_PICKUP, VAR_INIT_SECRET_BASE

**C code only** (34):

FLAG_DAILY_UNKNOWN_8C2, FLAG_HIDDEN_ITEMS_START, FLAG_SYS_CLOCK_SET, FLAG_SYS_CRUISE_MODE, FLAG_SYS_ENC_DOWN_ITEM, FLAG_SYS_ENC_UP_ITEM, FLAG_SYS_MIX_RECORD, FLAG_SYS_NATIONAL_DEX, FLAG_SYS_POPWORD_INPUT, FLAG_SYS_RESET_RTC_ENABLE, FLAG_SYS_SAFARI_MODE, FLAG_SYS_USE_FLASH, VAR_BARBOACH_SIZE_RECORD, VAR_CRUISE_STEP_COUNT, VAR_CURRENT_SECRET_BASE, VAR_CYCLING_ROAD_RECORD_COLLISIONS, VAR_CYCLING_ROAD_RECORD_TIME_H, VAR_CYCLING_ROAD_RECORD_TIME_L, VAR_DAYS, VAR_FANCLUB_UNKNOWN_1, VAR_FANCLUB_UNKNOWN_2, VAR_HAPPINESS_STEP_COUNTER, VAR_LOTTERY_RND_H, VAR_LOTTERY_RND_L, VAR_MIRAGE_RND_H, VAR_MIRAGE_RND_L, VAR_NATIONAL_DEX, VAR_PACIFIDLOG_TM_RECEIVED_DAY, VAR_POISON_STEP_COUNTER, VAR_RECYCLE_GOODS, VAR_REPEL_STEP_COUNT, VAR_RESET_RTC_ENABLE, VAR_SECRET_BASE_MAP, VAR_SHROOMISH_SIZE_RECORD

**debug menu only** (3):

FLAG_SYS_CAVE_BATTLE, FLAG_SYS_CAVE_SHIP, FLAG_SYS_CAVE_WONDER

**nowhere (unused)** (0):

-

**Used by map scripts AND the C engine** (107): see story_ids.json "engine" for the ones mapped to Black 2 equivalents (badges, Running Shoes, game clear, ...):

FLAG_BADGE01_GET [engine], FLAG_BADGE02_GET [engine], FLAG_BADGE03_GET [engine], FLAG_BADGE04_GET [engine], FLAG_BADGE05_GET [engine], FLAG_BADGE06_GET [engine], FLAG_BADGE07_GET [engine], FLAG_BADGE08_GET [engine], FLAG_DECORATION_2, FLAG_DONT_TRANSITION_MUSIC [140], FLAG_HIDDEN_ITEM_ABANDONED_SHIP_RM_1_KEY [engine], FLAG_HIDDEN_ITEM_ABANDONED_SHIP_RM_2_KEY [engine], FLAG_HIDDEN_ITEM_ABANDONED_SHIP_RM_4_KEY [engine], FLAG_HIDDEN_ITEM_ABANDONED_SHIP_RM_6_KEY [engine], FLAG_HIDDEN_ITEM_BLACK_GLASSES [engine], FLAG_HIDE_FANCLUB_BOY [651], FLAG_HIDE_FANCLUB_LADY [652], FLAG_HIDE_FANCLUB_LITTLE_BOY [653], FLAG_HIDE_FANCLUB_OLD_LADY [655], FLAG_HIDE_MAP_NAME_POPUP [2049], FLAG_HIDE_RUSTURF_TUNNEL_ROCK_1 [287], FLAG_HIDE_RUSTURF_TUNNEL_ROCK_2 [288], FLAG_LANDMARK_ABANDONED_SHIP [548], FLAG_LANDMARK_ANCIENT_TOMB [1062], FLAG_LANDMARK_BATTLE_TOWER [1503], FLAG_LANDMARK_BERRY_MASTERS_HOUSE [684], FLAG_LANDMARK_DESERT_RUINS [1063], FLAG_LANDMARK_FIERY_PATH [472], FLAG_LANDMARK_FLOWER_SHOP [208], FLAG_LANDMARK_FOSSIL_MANIACS_HOUSE [473], FLAG_LANDMARK_GLASS_WORKSHOP [474], FLAG_LANDMARK_HUNTERS_HOUSE [778], FLAG_LANDMARK_ISLAND_CAVE [1064], FLAG_LANDMARK_LANETTES_HOUSE [476], FLAG_LANDMARK_MR_BRINEY_HOUSE [291], FLAG_LANDMARK_NEW_MAUVILLE [549], FLAG_LANDMARK_OLD_LADY_REST_SHOP [477], FLAG_LANDMARK_POKEMON_DAYCARE [385], FLAG_LANDMARK_SCORCHED_SLAB [600], FLAG_LANDMARK_SEAFLOOR_CAVERN [885], FLAG_LANDMARK_SEALED_CHAMBER [1065], FLAG_LANDMARK_SEASHORE_HOUSE [292], FLAG_LANDMARK_SKY_PILLAR [1504], FLAG_LANDMARK_SOUTHERN_ISLAND [1505], FLAG_LANDMARK_TRICK_HOUSE [386], FLAG_LANDMARK_TUNNELERS_REST_HOUSE [293], FLAG_LANDMARK_WINSTRATE_FAMILY [478], FLAG_PENDING_DAYCARE_EGG [389], FLAG_RECEIVED_SECRET_POWER [485], FLAG_RUSTURF_TUNNEL_OPENED [415], FLAG_SECRET_BASE_REGISTRY_ENABLED, FLAG_SYS_BRAILLE_DIG [1070], FLAG_SYS_BRAILLE_FLY [1071], FLAG_SYS_BRAILLE_STRENGTH [1072], FLAG_SYS_BRAILLE_WAIT [1073], FLAG_SYS_B_DASH [engine 2403], FLAG_SYS_CHAT_USED [2076], FLAG_SYS_CTRL_OBJ_DELETE [556], FLAG_SYS_CYCLING_ROAD [416], FLAG_SYS_EXDATA_ENABLE [228], FLAG_SYS_GAME_CLEAR [engine 2400], FLAG_SYS_HAS_EON_TICKET [1511], FLAG_SYS_HIPSTER_MEET [418], FLAG_SYS_PC_LANETTE [488], FLAG_SYS_POKEDEX_GET [2070], FLAG_SYS_POKEMON_GET [engine 2401], FLAG_SYS_POKEMON_LEAGUE_FLY [1013], FLAG_SYS_POKENAV_GET [310], FLAG_SYS_RIBBON_GET [709], FLAG_SYS_SHOAL_TIDE [804], FLAG_SYS_TV_HOME [111], FLAG_SYS_TV_LATI [1512], FLAG_SYS_TV_START [419], FLAG_SYS_TV_WATCH, FLAG_SYS_USE_STRENGTH [2344], FLAG_SYS_WEATHER_CTRL [903], FLAG_VISITED_DEWFORD_TOWN [312], FLAG_VISITED_EVER_GRANDE_CITY [1015], FLAG_VISITED_FALLARBOR_TOWN [489], FLAG_VISITED_FORTREE_CITY [616], FLAG_VISITED_LAVARIDGE_TOWN [523], FLAG_VISITED_LILYCOVE_CITY [713], FLAG_VISITED_LITTLEROOT_TOWN [113], FLAG_VISITED_MAUVILLE_CITY [2071], FLAG_VISITED_MOSSDEEP_CITY [807], FLAG_VISITED_OLDALE_TOWN [229], FLAG_VISITED_PACIFIDLOG_TOWN [1074], FLAG_VISITED_PETALBURG_CITY [230], FLAG_VISITED_RUSTBORO_CITY [313], FLAG_VISITED_SLATEPORT_CITY [427], FLAG_VISITED_SOOTOPOLIS_CITY [905], FLAG_VISITED_VERDANTURF_TOWN [428], VAR_ASH_GATHER_COUNT [0x4097], VAR_BIRCH_STATE [0x403B], VAR_BRAVO_TRAINER_BATTLE_TOWER_ON [0x4102], VAR_CYCLING_CHALLENGE_STATE [0x4075], VAR_DEPT_STORE_FLOOR [0x40C2], VAR_ENIGMA_BERRY_AVAILABLE [0x40B0], VAR_ICE_STEP_COUNT [0x40E0], VAR_INIT_SECRET_BASE, VAR_LILYCOVE_FAN_CLUB_STATE [0x40C5], VAR_LOTTERY_PRIZE [0x40C8], VAR_PORTHOLE_STATE [0x4103], VAR_RUSTURF_TUNNEL_STATE [0x406B], VAR_SECRET_BASE_INITIALIZED [0x403C], VAR_STARTER_MON [0x4030], VAR_WEATHER_INSTITUTE_STATE [0x40BB]

## 6. Ids: allocation status (data/story_ids.json)

686 distinct non-temporary ids have a home chapter here (82 vars, 604 flags; item-ball flags excluded). In data/story_ids.json: 553 have a fixed Black 2 id, 109 are "engine" (Black 2 equivalents: badges via TrainerCardAddBadge, hidden items left for a hidden-item converter, system flags), 24 have neither.

Without an id (homes in groups story_ids.json does not allocate, e.g. S_optional / S_unused):

- S_optional: FLAG_DECORATION_1, FLAG_DECORATION_10, FLAG_DECORATION_11, FLAG_DECORATION_12, FLAG_DECORATION_13, FLAG_DECORATION_14, FLAG_DECORATION_15, FLAG_DECORATION_2, FLAG_DECORATION_3, FLAG_DECORATION_4, FLAG_DECORATION_5, FLAG_DECORATION_6, FLAG_DECORATION_7, FLAG_DECORATION_8, FLAG_DECORATION_9, FLAG_LATIOS_OR_LATIAS_ROAMING, FLAG_LINK_CONTEST_ROOM_POKEBALL, FLAG_RECEIVED_CONTEST_PASS, FLAG_SECRET_BASE_REGISTRY_ENABLED, FLAG_SYS_TV_WATCH, VAR_CONTEST_PRIZE_PICKUP, VAR_INIT_SECRET_BASE
- S_unused: FLAG_ROUTE104_PROTOTYPE_COMPLETED_1, FLAG_ROUTE104_PROTOTYPE_COMPLETED_2

Listed under another chapter in story_ids.json than the home computed here (ids hoenn.h already had before the split, kept under Ch0; only the label differs, the id is fixed): FLAG_HIDE_LANETTE (story_ids Ch0, home here Ch4), FLAG_HIDE_LANETTE_FALLARBOR (story_ids Ch0, home here Ch4), FLAG_HIDE_MAY_PICHU_DOLL (story_ids Ch0, home here Ch8), FLAG_HIDE_NORMAN_LITTLEROOT (story_ids Ch0, home here Ch13), FLAG_LEGENDARY_BATTLE_COMPLETED (story_ids Ch0, home here Ch10), FLAG_LEGEND_ESCAPED_SEAFLOOR_CAVERN (story_ids Ch0, home here Ch10), FLAG_SYS_CHAT_USED (story_ids Ch0, home here Ch1), FLAG_SYS_POKEDEX_GET (story_ids Ch0, home here Ch1), FLAG_VISITED_MAUVILLE_CITY (story_ids Ch0, home here Ch3), VAR_STARTER_MON (story_ids Ch0, home here Ch1)

Works are not short any more (277 free saved works outside Unova, per story_ids.json "free"); each chapter also has spare ids in story_ids.json "reserved".

