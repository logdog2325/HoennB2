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
| Celebi Lv 10 | Petalburg Woods, the north-east clearing (Sapphire (36,4)), once the National Dex is there; caught = gone, knocked out = back after the next Hall of Fame (user 2026-10-19: 0114 clears FLAG_DEFEATED_CELEBI) | Emerald's static legendary shape (cry, battle, "The X flew away!") |
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

## Post-game dex completion (postgame_dex, 2026-11-09; user decisions 2026-11-09, notes/DECISIONS.md)
Every version exclusive and both unchosen starters can be had after the Champion, without trading. Report with the
tables, the NEW lines and the test plan: work/agents/postgame_dex/REPORT.md.
- **Wild exclusives:** a zone's encounter file has a post-game twin read once FLAG_SYS_GAME_CLEAR is set (the decomp's
  src/hoennb2/resident/postgame_enc.c: EncData_Load asks HoennB2_ZoneEncID; decomp change: work/agents/postgame_dex/
  postgame_decomp.patch until it is merged). Slot edits per version: data/hoenn_postgame_encounters.json (Sapphire, the
  twin ids) + data/ruby/ + data/emerald/ ("maps" replaced whole); twins: converter/gen_postgame_encounters.py ->
  src/encounters[/ruby|/emerald]/NNNN_pg_*.s (rerun it for a version after its gen_encounters/gen_caves); the {file ->
  twin} pairs and the area page's post-game cells: b2tools/patches/postgame_encounters.py (build_rom adds it when our C is
  on); the area page: hoenn_pokedex's ITCM HabitatRead calls HoennB2_PostgameHabitat.
- **The other weather legend (S/R):** Sapphire's Groudon / Ruby's Kyogre sleeps in Seafloor Cavern Room 9 at (17,38)
  (scenes/SeafloorCavern_Room9_Postgame.inc, Lv 49); FLAG_CAUGHT_OTHER_LEGEND / FLAG_DEFEATED_OTHER_LEGEND. The hint (user,
  2026-11-09): the Weather Institute 2F scientist (Castform's, Emerald's weather reporter) says the readings under the sea off
  Route 128 after the Champion while it sleeps there (1128 L_WI2_AlreadyGave, text 0365 line 7, + ruby/).
  After the Champion the room looks as in the other version (user 2026-11-10): Sapphire shows Ruby's lava basin, Ruby
  Sapphire's water pool (Room 9's "alt_rooms" in data/cave_layouts/SeafloorCavern_Room9.json + data/interiors/190.json,
  per version through version.alt_rooms; map replace event 0 = work 0x4031, Emerald's Route 111 event, unused by S/R;
  set on entry only by the zone init PG_R9_Init, reloading the matrix only when it differs). The legend stays on its tile.
- **One-chance legendaries:** not caught (the Pokédex's caught mark) = back after the next Hall of Fame:
  scenes/postgame_legends.inc (0114 HF_SetGameClearFlags); Cave of Origin B4F's re-encounter: 0206 L_B4_Again.
- **Unchosen fossil (S/R):** back at its Route 111 spot (scenes/Route111.inc R111_PostgameFossil; FLAG_CHOSE_ROOT_FOSSIL /
  _CLAW_FOSSIL, pokeemerald's names, now set in S/R too).
- **Unchosen starters:** Birch, Lv 5, both in one talk (his four NEW lines approved by the user 2026-11-09) (scenes/BirchLab_Postgame.inc PG_LabStarters, VAR_BIRCH_OTHER_STARTERS;
  party full: Black 2's BoxAdd into the PC). Text 0625 rows: 0-37 Gen 3, 38-43 the follower aide in every version
  (placeholders, src/text/overrides_followers.json with our C on), Sapphire/Ruby 44-51 these lines; Emerald 44-54 its Johto
  starters (EMJ_T), 55-62 these lines (PGS_T).
- **Swarm bug fixed:** Black 2's swarm table names zone 0xffff under HOENNB2 (src/ov036/enc_pokeset.c SWARM_DATA).
