# Post-game additions (postgame_scripts, 2026-10-07)

The user's queued post-game content (notes/DECISIONS.md 2026-10-07; notes/EVENTS.md "Other event content"), except
Mirage Island and Altering Cave (postgame_maps). Proofs: screenshots/postgame_scripts/. Ids: data/story_ids.json chapter
"Postgame" (converter/gen_story_ids.py ORDER has it). Story objects: data/story/postgame.json.

## What the player sees
| Item | Where / when | Source |
|---|---|---|
| Lati news | the player's own house TV after the Hall of Fame: the bulletin ("a red Flying Pokémon"), Latias starts roaming | Sapphire tv.inc EventScript_1A6F0B (InitRoamer) |
| National Pokédex | first time in Littleroot after the Hall of Fame (after ch13's S.S. Ticket scene): Birch "!", "I have something to show you", the Lab, the upgrade (Black 2's PokeDexGiveNational); the beasts and birds start roaming | Emerald BeginDexUpgradeScene + UpgradeToNationalDex, word for word |
| Enigma Berry | Norman, Petalburg Gym, after the Hall of Fame, once (not while the Bag holds one) | Sapphire ShouldGiveEnigmaBerry / GiveEnigmaBerry without the e-Reader check |
| Jirachi Lv 5 | the scientist at (2,2) in the Mossdeep Space Center 1F, after the Hall of Fame | NEW lines (user to approve), Sapphire's Castform gift as the template |
| Celebi Lv 10 | Petalburg Woods, the north-east clearing (Sapphire (36,4)), once the National Dex is there; caught or knocked out = gone | Emerald's static legendary shape (cry, battle, "The X flew away!") |
| Roamers | Latias Lv 44 (Sapphire 40), Raikou / Entei / Suicune / Articuno / Zapdos / Moltres Lv 55 (FRLG 50), levels on data/level_scaling.json's curve; Sapphire's 20 routes (110, 111, 117-134) | Sapphire roamer.c, seven at once |

## Roamers: what Black 2 has and what was added (b2tools/patches/roamers.py has the addresses)
- Black 2 keeps BW1's roaming battle (two save slots in the encounter block, FieldEncount_RndCheckRoaming /
  SetupRoaming / GenRoamingPkm, battle flag 8 -> AI flag 11: the roamer flees unless trapped) but nothing that writes a
  roamer: no start, no move, no HP/capture update; the zone-change hook and the game-clear hook are empty functions, the
  two roamer script commands (434/435) are unused by Black 2's scripts. The Pokédex area page reads no roamer data.
- Seven roamers in 42 bytes of the encounter block (6 each: HP, location, status, a seed for PID/IVs/nature), the code
  in ITCM after hoenn_world's ZoneLookup (`roamers` patch, after hoenn_world; roamers.c compiled with clang, linked by
  roamers.py). A route = the zone header's place name (every zone of a Sapphire map has it; the desert's weather zones
  copy Route 111's). Encounter: Sapphire's 1 in 4 on the roamer's route; several there: one at random.
- Moves: every map load (FieldMapControl_InitSpawn: warps of all kinds, fly, blackout, Continue) = Sapphire's warp move
  (another random set); walking into another place's zone = Sapphire's RoamerMove (a neighbour, 1 in 16 a jump, never
  where the player was two maps ago; history in VAR_ROAMER_PLACE_HISTORY). After a roaming battle: HP and status kept,
  another set; caught = gone; knocked out = gone until the next Hall of Fame (user decision, the Gen 4+ rule; Sapphire
  keeps it gone): the location byte's bit 7 marks it, and Black 2's emptied BW1 game-clear hook (ov012 EventGameClear_Create
  -> func_ov012_02159220) now runs PG_OnGameClear: full HP, the same Pokémon (seed), a random location. Tested
  (screenshots/postgame_scripts/09: Suicune knocked out on Route 101 in a test build, the Hall of Fame, it roams again).
- Scripts: `pg_roamer_start k[, loc]`, `pg_roamer_get var, k` (scenes/postgame_lib.inc).

## Files
scenes/postgame_lib.inc, LittlerootTown_Postgame.inc (Script_26 of 0778, condition in 0779, PG_LittlerootInit from the
zone init), BirchLab_Postgame.inc (0792 script 14, PG_LabInit, Birch's state-2 line), PetalburgCity_Gym_Postgame.inc
(inside ch6's Ch6_NormanPostBattle), MossdeepCity_SpaceCenter_1F_Postgame.inc (0670 entry 1), PetalburgWoods_Postgame.inc
(entry 5 and the zone init of ch1's PetalburgWoods.inc), players_house_1f_postgame.inc (Script_6 of 0780/0784),
postgame_test.inc; text appended to 0618, 0625, 0619/0621, 0187, 0547, scenes/PetalburgWoods.txt.

## Testing
Build: work/agents/postgame_scripts/build.sh (story_build.sh's list + `roamers`); `rebuild.sh` also makes a cold-boot
Littleroot state (the roamer code is in ITCM and ov012, both resident: old states run the old code).
`HOENN_TEST_CH13=1 HOENN_TEST_CHPOSTGAME=1` (scenes/postgame_test.inc): Littleroot's town sign = the state after the Hall
of Fame + Norman beaten + 20 Master Balls; Birch's house sign = also the National Dex and all seven roamers (at
`HOENN_TEST_CHPOSTGAME_LOC`, re-placed after the warp). Both warp to `HOENN_TEST_CHPOSTGAME_W` (default a sentinel the
tests overwrite in a ROM clone: tests/lib.py patched_rom). `HOENN_TEST_ROAMER_ALWAYS=1`: every encounter on a roamer's
route is the roamer; `HOENN_TEST_ROAMER_NOFLEE=1` (no roaming AI, so one can be knocked out) and
`HOENN_TEST_ROAMER_PLACE0=14` (location 0 = Route 101, next to Littleroot); Littleroot's Lab sign = the town sign's state, then
the Hall of Fame scene. Tests: work/agents/postgame_scripts/tests/t1-t7.
