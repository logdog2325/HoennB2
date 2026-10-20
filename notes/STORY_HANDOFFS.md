# Story hand-offs between chapters (lead's list; give each chapter agent its section)

## For Ch3b (Route 110, Mauville, Route 117, Verdanturf, Rusturf reunion)
- From ch2: Rusturf Tunnel (room 134) includes `scenes/RusturfTunnel_Ch3.inc` (SCENE_ENTRIES + body; Ch3 entries are scripts 9+, after ch2's 1-8) and `scenes/RusturfTunnel_Ch3_init.inc` (lines inside 0269's map-script table; with RT_CH3_TABLES defined, the condition tables after MapScriptsEnd). Both are empty stubs: fill them for the Wanda/HM04 beat; append text to `src/text/script/0153_room_RusturfTunnel.txt` after line 8. Wanda's boyfriend = uid 1, Wanda = uid 10 (data/story/ch2.json).
- From ch2: Route 116's lost-glasses man stands in Verdanturf's zone 120: `#include "scenes/Route116_GlassesMan.inc"` in both parts of `scenes/VerdanturfTown.inc` (1 ScriptEntry; `#define R116G_TEXT n` before the body include, n = where the 5 lines of `src/text/scenes/Route116_GlassesMan.txt` go in VerdanturfTown.txt). Tell ch2 (or the lead) its script number so uid 172 gets placed.

## For Ch4 (Routes 111-115, Fiery Path, Fallarbor, Meteor Falls)
- From ch2: Devon Corp 2F's fossil scientist is script 5 = `scenes/RustboroCity_DevonCorp_2F_Fossil.inc` (stub with his first Sapphire line; append text after line 6 of 0367).

## For Ch6 (Norman, Surf, Routes 105-108, Abandoned Ship, New Mauville)
- From ch1: Petalburg Gym: fill `scenes/PetalburgCity_Gym_ch6.inc` (labels Ch6_NormanBattle / Ch6_NormanPostBattle, entries 4+ of 0904_room_PetalburgCity_Gym.s, text after line 15 of 0187).
- From ch2: Dewford Hall's Sludge Bomb man is written (`scenes/DewfordTown_Hall_SludgeBomb.inc`, script 11, hidden by FLAG_HIDE_SLUDGE_BOMB_MAN_DEWFORD_HALL): just keep it.

## Shared
- gen_map_content.py: scene_files() counts ScriptEntry lines of `#include "scenes/..."` inside a scene's SCENE_ENTRIES part (ch2's fix; nested includes keep numbering right).
- Message windows: not a bug (story_infra, 2026-10-07: frame-by-frame logs show the window always closes before the next command; ch1's contact sheets were misread). Keep position 0 (h_msgbox / h_msgbox_actor).
- Key items: src/include/hoenn_key_items.h (ITEM_DEVON_GOODS, ITEM_POKENAV via h_give_pokenav, ITEM_MACH_BIKE; no Acro Bike). Daily berry spots and hidden items are placed by the story patch.
- Test switches: HOENN_TEST_CH<n> (start state in your own scene file), passed straight to the assembler.

## From ch3a (2026-10-07)
- Ch3 flags 430-432 taken (reporters' "story recorded" flags); 3b takes from 433 up.
- Reserved includes in Slateport files (fill them, objects already placed and hidden by their flags): `scenes/SlateportCity_Ch8.inc` (Stern's TV interview, Gabby & Ty), `scenes/SlateportCity_Harbor_Ch8.inc` (submarine escape, harbor Stern, Ch6's Scanner trade), `scenes/SlateportCity_Harbor_Ch13.inc` (ferry attendant), `scenes/SlateportCity_SternsShipyard_1F_Ch9.inc` (Briney).
- Money: Sapphire's "¥" must become "$" (gen3text fix pending; ch3a converted its own lines).

## From story_infra (2026-10-07)
- For ch3a's successor: the Slateport Effort Ribbon woman (`scenes/SlateportCity.inc`, Story_EffortRibbonWoman) now really
  checks and gives the ribbon (`h_check_ribbon` / `h_give_ribbon`, `FLAG_SYS_RIBBON_GET`); it needs the story patch's
  overlay edits (`HOENN_STORY_CODE=1` until the lead's savestate remake). Ribbon macros: notes/STORY_COMMON.md "Ribbons".
- Money: converter/gen3text.py now turns Sapphire's "¥" into "$" (Black 2's Pokédollar) for every generator; files
  generated before keep "¥" until their generator reruns (e.g. 0262_room_Route109_SeashoreHouse.txt).
- Room files: everything after `// ---- story` (plus your entries, includes and notes above it) survives generator
  reruns: notes/STORY_COMMON.md "Room scripts shared with a generator".
- Oldale Mart (ch1): the shops generator now writes ch1's CMP_NE fix of the expanded list itself.

## From ch3b (2026-10-07)
- For Ch6: Mauville's outdoor Wattson (New Mauville, TM24 Thunderbolt) is Mauville script 5: write
  `scenes/MauvilleCity_Ch6.inc` (label `Ch6_Wattson`, text after line 14 of `src/text/scenes/MauvilleCity.txt`); it is
  picked up by `__has_include`. Object uid 108 (data/story/ch3b.json, FLAG_HIDE_WATTSON_MAUVILLE). Its model 270 (the
  PWT Wattson) has no back/walk frames. Mauville's zone init already does Sapphire's OnTransition part for him, and the
  Gym's Wattson already branches on VAR_NEW_MAUVILLE_STATE 2.
- For Ch1 (Route103.inc is yours): Route 110's first Aqua grunt stands in Route 103's zone, so `scenes/Route103.inc`
  includes `scenes/Route110_Grunt1.inc` twice (script 3 in the entries, and the body with `#define R110G1_TEXT 6` = line 6
  of `src/text/scenes/Route103.txt`). Keep both lines.
- ch2's hooks are filled: `scenes/RusturfTunnel_Ch3.inc` (scripts 9-10, step triggers (24,4)/(24,5) on
  VAR_RUSTURF_TUNNEL_STATE 3, text lines 9-11 of 0153) and the lost-glasses man = Verdanturf script 4 (`R116G_TEXT 4`).
- Route 117's Day-Care Man is Route 117 script 1 (`scenes/Route117.inc`, zone 437 since the banner rectangles). He and
  the Day Care Pokémon give `"zone": 437` and world tiles in data/story/ch3b.json, because b2tools/patches/story.py
  still places `"map"` objects by matrix cell only (it ignores world.json "zone_rects"): for the lead, objects of
  other chapters on rectangle tiles (ch1's Route 104 people 116/123/124, the Route 104/112/117 berry and hidden-item
  signs) still land in the cell's zone, where the game no longer loads them.
- For the lead / gyms_league: the Mauville Gym's beams need two more map-replacement layouts (`MG_EVENT_ALT`,
  `MG_EVENT_OFF` in 0478_room_MauvilleCity_Gym.s; the scripts use them as soon as they are defined). Until then
  Wattson's platform cannot be reached (the test build opened two tiles in a test-only interiors copy).
- Map-script permissions (all chapters): notes/STORY_COMMON.md "Notes" (some commands hang the game in a zone init).

## From npc_limit (2026-10-07)
- Zones now show up to 30 different NPC sprites (b2tools/npc_check.py reports; 0 zones over). Sprite-budget ordering of objects is no longer needed.
- ch3a's harbor (24,12) and shipyard (23,38) sign entries and ch2's Rustboro Gym sign (23,19) entry in data/story/*.json are now duplicates of generated signboards: drop them (harmless until then).
- New story signs: name the sign in its ScriptEntry comment to get a Black 2 signboard (STORY_PORTING.md).

## From ch2 (final, 2026-10-07)
- Rustboro's generated scripts start at 25; Mr. Briney keeps Route 104 scripts 4 and 5 (no more there).
- Hiker Mike (Rusturf) is placed by ch2.json; if gen_trainer_npcs places him later, the build stops on duplicate uid 9: drop him from work/agents/ch2/tools/mkjson.py.
- Dewford Hall: black untextured block at the partition wall (room builder).
- Black 2's PWT overworld sprites (Gym Leaders, Steven) have placeholder X frames for back/walk: being drawn.

## From ch5 (2026-10-07)
- Cable car (both stations are ch5's room files, `// ---- story` sections): Black 2 has no ride, so the attendant's yes
  fades to black, plays Black 2's elevator hum (`SEQ_SE_FLD_23`, 3 s), warps with `RTReserveScript 3` + `MapChangeCore` to the
  other station and the reserved script 3 (the arrival: fade in, walk down 3, attendant follows) runs on the black screen.
  Sapphire's lines word for word; `VAR_CABLE_CAR_STATION_STATE` 1 (up) / 2 (down) as Sapphire. Rooms: 1110 (Route 112, zone
  555) and 0680 (Mt. Chimney, zone 340).
- For Ch4: Mt. Chimney's Archie scene (`scenes/MtChimney.inc` MC_Archie) writes `FLAG_DEFEATED_EVIL_TEAM_MT_CHIMNEY`, clears
  `FLAG_HIDE_PROF_COSMO_FALLARBOR` and sets `FLAG_HIDE_PROF_COSMO_METEOR_FALLS`, as Sapphire. Route 112's zone init (yours)
  sets `VAR_JAGGED_PASS_ASH_WEATHER` 0 and Mt. Chimney's sets it 1; Hoenn has no weather yet, so Jagged Pass's ash weather and
  its weather coordinate events are not ported (nothing reads the var). Route 112's two Aqua grunts and the Cable Car station
  door: yours; the station room scripts do not check `FLAG_HIDE_GRUNTS_BLOCKING_CABLE_CAR`.
- For Ch4 (Fallarbor House1, `0194`): Prof. Cozmo's Meteorite hand-over (TM27 Return) is `scenes/FallarborTown_House1_Ch5.inc`
  (labels `Ch5_CozmoMeteorite`, `Ch5_CozmoGaveMeteorite`, `#define CH5_COZMO_TEXT 6` = first of its 6 lines in 0108, copied in
  order from `src/text/scenes/FallarborTown_House1_Ch5.txt`). Keep your `#if __has_include` of it. Tested here with ch4's
  Cozmo script (`c4_talk`, flag checks) in a private build.
- For Ch6 (Petalburg): Flannery's defeat adds 1 to `VAR_PETALBURG_GYM_STATE` and, at 6, runs the two lines of
  `Common_EventScript_ReadyPetalburgGymForBattle` inline (`FLAG_HIDE_PETALBURG_GYM_GUIDE` cleared,
  `FLAG_PETALBURG_MART_EXPANDED_ITEMS` set): do not write them again. It also sets `FLAG_HIDE_WALLY_WANDAS_HOUSE` (Ch3's Wanda's
  house) and `VAR_LAVARIDGE_RIVAL_STATE` 1.
- Lavaridge's rival bike (Sapphire object 7) is the walking rival (no bike sprites yet); Lavaridge Gym trainers (Sapphire:
  buried in the sand) stand facing down with sight 1: Black 2 has no buried trainers.
- **Lavaridge Gym warps (APPLIED by story_fixups with ONE global arrival script, `RTReserveScript 10017` = hm_free Script_18 / file 1243; my work/agents/ch5/gym_warp_fix copies are superseded: do NOT copy them over the tree; rebuild before testing)**: the generated hole/vent
  scripts (`gyms_league_rooms.py write_scripts`: `ActorsPauseAll; MapChangeCore ...; FinishAllEvents; ActorsUnpauseAll; VMHalt`)
  leave every NPC and trainer of the arrival room dead (A on Flannery or the guide starts nothing, trainers do not see you;
  tested: before any hole the guide talks, after one fall nobody does). The same as the sign's test warp ("talking is dead
  until a real warp"). Black 2's own pattern fixes it (tested: Zane's battle starts, Flannery's talk, battle, badge and TM50
  work): `ActorsPauseAll; FadeOutBlack; RTReserveScript <n>; FadeWait; MapChangeCore ...; FinishAllEvents; ActorsUnpauseAll;
  VMHalt`, plus in the destination room one arrival script n: `ActorsPauseAll; FadeInBlack; FadeWait; FinishAllEvents;
  ActorsUnpauseAll; VMHalt` (1F -> B1F: n = B1F's new Script_7; B1F -> 1F: n = 1F's script after the story entries = 24).
  Tested files: `work/agents/ch5/gym_warp_fix/0290_room_LavaridgeTown_Gym_1F.s` and `0296_room_LavaridgeTown_Gym_B1F.s`.
  Every generated room with step-trigger warps (`STEP_ON` behaviours: Lavaridge holes and vents, ladders) has the same problem.
  Lavaridge's puzzle itself works (all 20 holes and 6 vents; solution path in `work/agents/ch5/tests/gym_path.py`); trainers stand
  on the hole tiles (10,19) (4,17) (4,12) (0,2) (6,2) like Sapphire's buried ones, so those holes cannot be used.
  **Flannery's platform is a dead end** (the same in Sapphire's own map data, checked with its walkability and warp behaviours
  in pokeruby: only the six B1F steam vents fire): from her band (right half, rows 8-14) the two holes (6,14) and (10,14) lead into
  closed B1F corridors (the first loops back to her band by its vent), so 89 tiles are reachable and the door is not (BFS in
  `gym_path.py`). The player leaves by Escape Rope / flying out of the building is not possible indoors: question for the user
  (proposal: after the Heat Badge, make the hole at (6,14) drop the player at the Gym door, one trigger script in Gym 1F).
- Outdoor `ActorSetGPos` takes the grid height as y: Lavaridge's ground is 32 units = `LV_GY 2` (Littleroot 1, Route 110 0); y 0
  puts the actor under the ground (invisible, no collision). `ObjInitNPCGPos` takes 0.
- Test switch `HOENN_TEST_CH5=1|2|3` (scenes/ch5_test.inc): stage 3 = Flannery beaten (the rival scene); in a private build the
  town sign calls it before the warp (work/agents/ch5/build_tree.sh). `MapScriptConditions` scenes (the rival's Go-Goggles) start
  when you step out of a building door (tested), not after a test warp.

## From ch8a (Lilycove City and its buildings, 2026-10-07)
- Test switch `HOENN_TEST_CH8A=1` (Chapters 1-7's end: six Badges, Surf/Fly, Lv 100 Swampert) or `=3` (also eight Badges, game
  cleared, the Fan Club in state 1, the Motel staff, the submarine escaped): `scenes/ch8a_test.inc`, run from Lilycove's zone
  init. Start from the lead's `work/emu/base_littleroot.dst` with `HOENN_TEST_WARP=96,555,139` (below the Department Store
  door; walk through a building door once before talking). Never put it in normal builds (all under `#ifdef`).
- Ids claimed from Ch8's reserve (works): `VAR_LOTTERY_ID` 0x40CE, `VAR_FANCLUB_UNKNOWN_1` 0x40D2, `VAR_FANCLUB_UNKNOWN_2` 0x40D3.
- For Ch11 (Hall of Fame, Sapphire data/scripts/hall_of_fame.inc): `#include "common/fan_club.inc"` at the END of your file and
  `VMCall Sub_FanClub_GameClear` where Sapphire says `special UpdateTrainerFanClubGameClear` (shows the four hidden fans, makes
  Lass/Little Girl/Man the player's, sets VAR_LILYCOVE_FAN_CLUB_STATE 1 so the Fan Club plays its scene). Also clear
  `FLAG_HIDE_LILYCOVE_MOTEL_PEOPLE` there (the Game Freak staff in the Cove Lily Motel 2F: placed and scripted, hidden until then).
  Drake's room (`special sub_810FF60`, VAR_0x8004 = 0) and the Battle Tower rooms (VAR_0x8004 = 3): `WorkSetConst 0x8004, n` +
  `VMCall Sub_FanClub_CountWin` (same include). `common/fan_club.inc` has the whole fan state (header lists every sub).
- For Ch13 (Lilycove Harbor, room 0406): write `scenes/LilycoveCity_Harbor_Ch13.inc` with the label `Ch13_LH_FerryAttendant`
  (Sapphire LilycoveCity_Harbor_EventScript_FerryAttendant: S.S. Ticket / Eon Ticket); it is included automatically (Script entry 2,
  object 1, hidden by FLAG_HIDE_FERRY_ATTENDANT_LILYCOVE which is NOT set at new game). Text file `0261_room_LilycoveCity_Harbor.txt`:
  lines 1-3 are mine (the attendant's "ferry unavailable", the sailor's two lines): append yours after line 3. Objects 2 (the S.S.
  Tidal, no sprite) and 4 (the ferry sailor of the Eon Ticket scene, hidden by FLAG_HIDE_FERRY_SAILOR_LILYCOVE, no script) are not
  placed / placed without a script: yours. The harbor sailor is written (before / after the game is cleared).
- For the Contests block (optional, decided later): the Lilycove Museum 2F's frames (signs, five painting flags
  `FLAG_*_PAINTING_MADE`), the Curator's glass-ornament scene, the four museum visitors (hidden by `FLAG_HIDE_LILYCOVE_MUSEUM_*`)
  and the Contest Lobby's artist scene (`VAR_LILYCOVE_CONTEST_LOBBY_STATE`, objects 4/8/11 not placed) are ported up to what needs a
  Contest; the lobby receptionist says Sapphire's reception line and registers nobody. The Hoenn Pokédex check of the Game Designer
  (Motel 2F, 200 national numbers) and Black 2's diploma are in `0360_room_LilycoveCity_CoveLilyMotel_2F.s`.
- Rival in Littleroot after the Lilycove battle: `scenes/players_house_2f_ch8.inc`, included (guarded) at the start of
  `scenes/players_house_2f.inc` Script_21 (Ch0's file), two lines appended to 0620 / 0622 (T(4), T(5)).
- Lilycove's Wailmer (3 NPCs with Black 2's Wailmer overworld sprite, hidden by FLAG_EVIL_TEAM_ESCAPED_IN_SUBMARINE) and the Aqua grunts
  (hidden by FLAG_HIDE_GRUNTS_LILYCOVE, set by ch8b's AquaHideout_B2F) are Lilycove's; the hideout door's warp (zone 96 warp slot 27)
  is moved off the map by the zone init once the Mind Badge is owned (Sapphire's RemoveEvilTeamBaseEntrance).
- The Dept Store floors set `VAR_DEPT_STORE_FLOOR` in their zone inits (init files 0393/0395/0399/0401/0403): the elevator reads it.
  The elevator's exit tiles are Black 2's dynamic warp (warp id 256): the attendant sets the target with `FieldSetNextZone`.


## From ch9 (Mossdeep, Routes 124-127, Shoal Cave, the Treasure Hunter; 2026-10-07)
- Test switch `HOENN_TEST_CH9=<stage>` (`scenes/ch9_test.inc`, run from the zone inits of Mossdeep City, Route 124 and Route 125):
  1 = Chapters 1-8's end (six Badges, Surf/Fly/Cut/Strength, a Lv 100 Swampert, Fortree's Wingull in Mossdeep), 2 = also a Lv 100
  Tyranitar (Tate and Liza need two) and the trade items (Red/Blue Shards, 4 Shoal Salt + 4 Shells), 3 = also the Mind Badge and HM06.
  `HOENN_TEST_CH9T=1` marks the Gym's six trainers beaten. Start from `work/emu/base_littleroot.dst` with `HOENN_TEST_WARP=107,707,171`
  (below Steven's door); walk through a door once before talking to outdoor people. Never in normal builds (all under `#ifdef`).
- For Ch10 (Sootopolis; Steven leaves): Steven's house is `0678_room_MossdeepCity_StevensHouse.s` (+ init `0679`): he gives HM06 Dive
  (Sapphire's HM08; Black 2's Dive is HM06) on the first entry (VAR_STEVENS_HOUSE_STATE 0 -> 1) and stands at (6,5) after that. His object
  (uid 1, NPC index 0) is hidden by FLAG_HIDE_STEVEN_STEVENS_HOUSE (yours: set it where Sapphire does). Kyogre's weather: Mossdeep City and Routes
  124-127 call `Common_SetLegendaryWeather` (guarded `__has_include("common/legendary_weather.inc")`, as Lilycove) while FLAG_SYS_WEATHER_CTRL is set.
- For Ch11 (Hall of Fame, `EverGrandeCity_HallOfFame_EventScript_SetGameClearFlags`): `clearflag FLAG_ITEM_MOSSDEEP_STEVENS_HOUSE_HM08` (the Dive ball
  in Steven's house, id 813, set at new game by new_game_flags.inc: it is the hide flag of the ball object, uid 3), `clearflag FLAG_HIDE_BELDUM_BALL_
  STEVENS_HOUSE` (Beldum's ball, uid 2), `clearflag FLAG_HIDE_STEVENS_LETTER` and `setvar VAR_STEVENS_HOUSE_STATE, 1` as Sapphire.
- For Ch13: Steven's Beldum ball (`Ch13_SH_BeldumBall`, script 10) and the letter (`Ch13_SH_Letter`, script 11: a sign on the table tile (6,4); it does
  nothing while FLAG_HIDE_STEVENS_LETTER is set) are written in 0678's story part as Sapphire has them (fallback). To replace them write
  `scenes/MossdeepCity_StevensHouse_Ch13.inc` defining the same two labels: it is picked up by `__has_include` instead of the fallback.
- Briney in Stern's Shipyard: `scenes/SlateportCity_SternsShipyard_1F_Ch9.inc` (Sapphire's one MSGBOX_NPC line; the Mind Badge in the Gym clears
  FLAG_HIDE_BRINEY_SLATEPORT_SHIPYARD and FLAG_HIDE_WORKERS_SLATEPORT_HARBOR, as Sapphire's TateAndLizaDefeated).
- Wingull mail: Mossdeep House 2's Wingull (uid 3, hidden by FLAG_HIDE_WINGULL_MOSSDEEP_HOUSE until Fortree's boy sends it: ch7) sets
  FLAG_WINGULL_DELIVERED_MAIL and clears FLAG_HIDE_WINGULL_FORTREE_HOUSE; ch7's boy gives the Mental Herb.
- Shoal Cave: the tide is the generator's; the salt and shells are Poké Ball objects + signs on Sapphire's tiles (hidden by FLAG_HIDE_TOOK_SHOAL_*), and
  the old man brings them back once a day with a midnight-reset flag `FLAG_DAILY_SHOAL_ITEMS_RESET` (id 2791, clear = a new day).
- Ids claimed: `FLAG_ITEM_MOSSDEEP_STEVENS_HOUSE_HM08` 813, `VAR_MOSSDEEP_SPACE_CENTER_START_DAY` 0x40D9, `FLAG_DAILY_SHOAL_ITEMS_RESET` 2791.
- Mossdeep outdoor people use uid 200 + Sapphire id (the trainers patch holds uid 107 in zone 107).

## From ch4 (Routes 111-115, Fiery Path, Fallarbor, Meteor Falls, Devon Corp 2F's fossil scientist; 2026-10-07)
- Tested end to end (screenshots/ch4/, tests in work/agents/ch4/tests): the Winstrate gauntlet + Macho Brace, the sandstorm wall
  without Go-Goggles, the fossil choice (Root/Claw), the Secret Power man, the Old Lady's Rest Stop, Gabby & Ty (double battle +
  interview with Black 2's word picker), the Glass Workshop (Soot Sack, ash steps, flute menu), the Move Tutor (Black 2's Move
  Reminder screens), the Meteor Falls Aqua/Magma scene + Prof. Cozmo, the Route 114 berry man, Devon Corp 2F's fossil revival
  (Root Fossil -> Lileep, nickname screen). Test switch `HOENN_TEST_CH4=1|2|3`: header of `scenes/ch4_test.inc` (stage 2 =
  start `HOENN_TEST_WARP=554,4,7` + `HOENN_TEST_NO_WILD=1`, walk out of the Winstrate house).
- Shared helpers: `scenes/ch4_lib.inc` (macros `c4_talk`, `c4_opendoor`/`c4_closedoor` (Black 2's door model animation at a
  world tile), `c4_mon_cry`, `c4_yesno_info`, `c4_easy_chat`). **Black 2's item script opens its own window: put `h_closemessage`
  before every `h_giveitem` / `RTCallGlobal 2805` that follows an `h_msgbox`** (ch4 found it the hard way: the game hangs on the
  message otherwise; ch2 had the same note in Dewford House 2).
- For Ch7 (Routes 118/120): Gabby & Ty are `scenes/gabby_ty.inc` (written by ch4; include it ONCE in the BODY of your route's
  scene file after `#define GT_TEXT n` = the first of their 14 lines in that zone's text file; header lists the 14 Sapphire
  labels in order; zone init: `VMCall Sub_GabbyTyUpdate`; people: `c4_gabby_ty TRAINER_GABBY_AND_TY_n, GT_GABBY|GT_TY, first`).
  Route 111's three pairs and the update sub (which shows the right pair on Route 111/118/120 from VAR_GABBY_AND_TY_BATTLE_NUM)
  are done; `VAR_GABBY_AND_TY_BATTLE_NUM` and `FLAG_GABBY_AND_TY_QUOTE` are used as Sapphire. Guard the include with
  `#if __has_include("scenes/gabby_ty.inc")` (the lead commits chapters one at a time). Black 2 gaps: the trivia/last-quote
  questions need gBattleResults (Black 2 scripts cannot read it): the plain question is always asked.
- For Ch5 (done): `FallarborTown_House1` includes your `scenes/FallarborTown_House1_Ch5.inc` guarded; Cozmo's script jumps to
  `Ch5_CozmoMeteorite` / `Ch5_CozmoGaveMeteorite`. Route 112's cable car station (rooms 1110/1111) is yours, untouched by ch4;
  Route 112's zone init sets `VAR_JAGGED_PASS_ASH_WEATHER` 0. The two Aqua grunts on Route 112 (uids 101/106, data/story/ch4.json)
  are hidden by `FLAG_HIDE_GRUNTS_BLOCKING_CABLE_CAR`, which the Meteor Falls scene sets (so the cable car is free after it).
- For Ch12 (Desert Ruins): Route 111's sealed Desert Ruins wall is an object (uid 140, data/story/ch4.json: a rock at Sapphire
  (29,87)) hidden by `FLAG_REGI_DOORS_OPENED`; the Desert Ruins room (zone 116) is not built (Route 111's warp 2 leads to it).
- For Ch2 (done): `scenes/RustboroCity_DevonCorp_2F_Fossil.inc` is the whole fossil scientist now (script 5, text lines 6-14 of
  0367); Sub_DV2_SetFossilReady (your zone init / the other scientists) makes the fossil ready.
- Black 2 gaps / stand-ins: the desert's weather and music switches (Sapphire's `setweather` / `fadenewbgm` coordinate events of
  Route 111, 30 events) are not done (Black 2 has one weather per zone and no script weather command; proposal: a separate zone
  for the desert rectangle with its own weather via world.py zone_rects); Route 113's ash is only Black 2's snowy trees (ash steps
  for the Soot Sack are 14 step-trigger columns worth 5 each, not Sapphire's per-step engine count); Lanette's Lotad Doll
  (decoration) and the Glass Workshop's Pretty Chair/Desk are not given (no decorations); the Secret Power man gives Black 2's
  TM43 (Flame Charge: no Gen 5 TM Secret Power) but says Sapphire's Secret Power lines; contests (Fallarbor Lobby/Hall people
  say Sapphire's lines, the receptionist registers nobody); secret bases (8 spots on Route 111) are plain scenery; the buried
  trainers Lao/Lung stand in the ash as normal trainers; Route 111's door animations need the buildings (see below).
- For the lead (map): the Winstrate house and the Old Lady's Rest Stop show NO building on Route 111 in work/world (10:15):
  the door scenes (`c4_opendoor` at world (261,173)) still run, Black 2's door model is just not there to open. Also the Route
  111 south rocks (Sapphire (18,101),(19,100): Rock Smash) sit on the only way north, as in Sapphire.

## From ch13 (post-game: S.S. Ticket, ferries, Battle Tower island, Southern Island, Sky Pillar, Steven's Beldum; 2026-10-07)
- **For Ch11 (Hall of Fame)**: one call replaces Sapphire's four calls (`ReadyReceiveSSTicketEvent`, `ReadyLatiTVEvent`, `ShowStevensBeldum`,
  `ShowHM08`) and the Route 131 islet: `VMCall Sub_Ch13_GameClear` in your game-clear script, with `#include "scenes/ch13_gameclear.inc"` at the END
  of the same file, both inside `#if __has_include("scenes/ch13_gameclear.inc")`. It sets houses state 3 + Norman, FLAG_SYS_TV_LATI, un-hides
  Beldum's ball / the Dive ball, `MapReplaceSetEvent 7`. You keep the rest (FLAG_SYS_GAME_CLEAR, the S.S. Tidal / Briney / letter flags, Steven's
  house state 1, fan club ...). After the credits the player must wake up in their own room (house 2F): the S.S. Ticket scene runs when they walk
  down. `#define CH13_EON_TICKET_GIFT 1` before the include also puts the Eon Ticket in the Bag (default 0, see below).
- S.S. Ticket scene (Dad / Norman, uid 5, Sapphire's movements for a boy and a girl): `scenes/players_house_1f_ch13.inc` = Script_30 of both
  house files (map-script condition VAR_LITTLEROOT_HOUSES_STATE 3 in 0781/0785; it waits in the rival's house: Sapphire plays it in either house),
  Mom's "Dad should stay longer" (state 4) is in her script 26, Littleroot's zone init sets the states to 5 (`scenes/LittlerootTown_ch13.inc`, also
  the BeginDexUpgradeScene state hook = Script_25 + a condition in 0779). Text: lines T(24)-T(27) of 0619 / 0621.
- Ferries (`scenes/ch13_lib.inc`: the crossing is Ch2's Briney boat, `scenes/ch2_boat.inc`): attendants `scenes/SlateportCity_Harbor_Ch13.inc` (text lines
  22-34 of 0352), `scenes/LilycoveCity_Harbor_Ch13.inc` (lines 4-18 of 0261; also the Eon Ticket branch), `scenes/BattleTower_Outside.inc`,
  `scenes/SouthernIsland_Exterior.inc`. Landing scripts: Slateport harbor 11 (from Lilycove, with Sapphire's "We have made land in Slateport City"
  announcement and the respawn set to Slateport's Center) / 12 (from the tower); Lilycove harbor 4 (from Slateport, announcement + respawn) / 5 (tower)
  / 6 (island); Battle Tower island script 3; Southern Island script 3. The S.S. Tidal's rooms (SSTidalCorridor / LowerDeck / Rooms) are NOT BUILT:
  no cabins, no 8 trainers (all converted, TRAINER_PHILLIP ... TRAINER_ANETTE: their NPCs would be placed by gen_trainer_npcs once the rooms exist),
  no TM49 man (Black 2's TM49 is not Snatch), no bed, no Capt. Briney / Peeko, no porthole texts. If the rooms get built: the room scripts are Sapphire's
  SSTidalCorridor / SSTidalRooms / SSTidalLowerDeck scripts (listed in notes/STORY_CHAPTERS.md Ch13), the harbors' attendants then warp there instead of
  `ch13_sail_announce` and the sailor's "We've arrived!" / `setrespawn` lines belong to the corridor sailor (the landings above already do the respawn).
- Battle Tower island: only the ferry attendant + Sapphire's three people and sign (generated). The tower door leads to the (generated) Lobby, nothing
  scripted: the PWT task owns that. `BT_Init` sets FLAG_LANDMARK_BATTLE_TOWER, VAR_BRAVO_TRAINER_BATTLE_TOWER_ON 0, FLAG_HIDE_REPORTER_BATTLE_TOWER.
- Southern Island: `scenes/SouthernIsland_Interior.inc` (the slab = a sign at (13,11) read facing north; Latios flies down from (13,2), Lv 55 = Sapphire 50
  on the level curve, `ch13_legend_battle`: CallWildBattle flag 1) and the quote after. Not done: the camera pan (SpawnCameraDummy), the Soul Dew it holds
  (CallWildBattle sets no item). The Eon Ticket is a Mystery Event item in Sapphire (nothing gives it): kept that way (default); the one-line switch is in
  ch13_gameclear.inc. The roaming Latias (Sapphire's TV news after the Hall of Fame -> InitRoamer) is not done: S_optional, Black 2 TVs are plain and no
  script command starts a roamer (FLAG_SYS_TV_LATI is set and nothing reads it).
- Sky Pillar: `scenes/SkyPillar_Top.inc` (Rayquaza uid 101, Lv 78 = Sapphire 70, the hide flag is set before the battle as Sapphire), the Entrance
  room's landmark flag (`0338`/`0339_init`); 1F-5F / Outside have nothing scripted in Sapphire (the cracked floors are the cave builder's).
- Steven's house: `scenes/MossdeepCity_StevensHouse_Ch13.inc` (ch9's fallback moved here: same text lines 8-15, tested: ball, nickname screen, letter).
- Level scaling: static legendaries use the curve (Kyogre 45 -> 49 precedent): Rayquaza 70 -> 78, Latios 50 -> 55. DECIDED (user, 2026-10-19,
  notes/DECISIONS.md): every static battle follows the curve in all versions: ch12's Regis 40 -> 44 (ch12_lib.inc CH12_REGI_LEVEL), the Kecleons
  30 -> 32 (ch7_lib.inc C7_KECLEON_LEVEL), New Mauville's Voltorbs 25 -> 26 (NI_VOLTORB_LEVEL), the hideouts' Electrodes 30 -> 32
  (AH1B_/MH1B_ELECTRODE_LEVEL). postgame_fix.
- Test switches: `HOENN_TEST_CH13=1` plus `HOENN_TEST_CH13_W1..W4="zone,x,0,z,dir"` (the warp targets of Littleroot's four signs; each runs the
  chapter's start state once: `scenes/ch13_test.inc` header). Used here: W1 `448,276,0,333,0` (below Slateport's harbor door; walk in), W2 `391,8,0,4,0`
  (player's room: walk up to the stairs = the S.S. Ticket scene; the only warp without the tickets), W3 `107,707,0,171,0` (Steven's door), W4
  `168,11,0,3,0` (Sky Pillar 5F: walk up 2 to the ladder). Test navigation inside rooms: the default player-position address of the harness can be off by a
  row; prefer screenshots.
- Files for the lead to commit together: scenes/{ch13_lib,ch13_gameclear,ch13_test,players_house_1f_ch13,LittlerootTown_ch13,SlateportCity_Harbor_Ch13,
  LilycoveCity_Harbor_Ch13,MossdeepCity_StevensHouse_Ch13,BattleTower_Outside(_init),SouthernIsland_Exterior(_init),SouthernIsland_Interior,SkyPillar_Top}.inc,
  0339_room_SkyPillar_Entrance_init.s, data/story/ch13.json, src/text/scenes/{BattleTower_Outside,SouthernIsland_Exterior,SouthernIsland_Interior}.txt,
  the generated auto files, the text appends (0619, 0621, 0261, 0352) and the edits of 0778/0779/0780/0781/0784/0785/0338/0406/1192 + scenes/players_house_1f.inc.
  The world needs the lead's rebuild (world.py): the generated people of BattleTower_Outside / SouthernIsland_Exterior got new script numbers (the story
  scenes come first) and Southern Island's slab sign (script 1) is a new generated sign (my build patched a clone of work/world).

## From ch6 (Ch6 + Ch12; 2026-10-07)
- For Ch8 (Slateport Harbor): the Scanner trade is `scenes/SlateportCity_Harbor_Ch6.inc` (label `Ch6_HB_SternScanner`); your Capt. Stern script must
  start (after lock + faceplayer) with `h_goto_if_badge 7, Ch6_HB_SternScanner` and keep that file included (1192 does it with a stand-in until
  `scenes/SlateportCity_Harbor_Ch8.inc` exists). Tested (Mind Badge + Scanner: Deepseatooth, "handed the Scanner", thanks line).
- For Ch11: Wally's father after Victory Road is in `1000_room_PetalburgCity_WallysHouse.s` (FLAG_DEFEATED_WALLY_VICTORY_ROAD branch kept).
- For Ch13: nothing new (Route 131's Sky Pillar scene is yours); the Regi doors flag `FLAG_REGI_DOORS_OPENED` is set by the Sealed Chamber.
- Black 2 scripts: close the message window (`h_closemessage`) BEFORE `h_giveitem` (the obtain-item script opens its own window and the
  game crashes with an open one: ARM9 undefined instruction; fixed in Wally's father, Wattson, Mom's Amulet Coin, the Fan Club, Stern).
- Test aids (test builds only, nothing in normal builds): `HOENN_TEST_CH6=<stage>` / `HOENN_TEST_CH12=<stage>` (scenes/ch6_test.inc: 1 = four Badges, Dad waits;
  2 = Norman beaten; 3 = + HM03, Basement Key, Scanner, ship keys, all Badges, Stern shown; 4 = + generator off; 5 = + door open; CH12: 2 = + friendship,
  3 = + Regi doors open, 9 = Swampert's Protect stands for Dig); the start runs in the zone init of the Gym, Wally's house, Pacifidlog, Route 105, New Mauville,
  the ship's Deck / Corridors B1F / hidden corridors and the Regi rooms. Teleport signs in the Petalburg Gym hall (work/agents/ch6/test_story.json via
  `HOENN_EXTRA_STORY`, scripts 37-46 of the Gym scene) reach Mauville (Wattson), the player's house (Mom), Slateport Harbor (Stern), New Mauville, the
  Captain's office, the Sealed Chamber, the three Regi caves and Pacifidlog with a real warp (text only works after one: the Littleroot test-warp sign
  leaves the field "dead" for talking and messages until you pass a door).
- Map replacement events: Ch6 uses none. Proposal for the lead: New Mauville's two barrier layouts (blue lowered / green lowered) as map-replace events 5 and 6
  (NM_EVENT_BLUE_DOWN / NM_EVENT_GREEN_DOWN in 0266_room_NewMauville_Inside.s; the scripts use them as soon as they are defined and the stand-in below then
  steps aside).
- Black 2 gaps and stand-ins (all listed in the report): New Mauville's 7 barriers are walked through by script (a step in front of a lowered barrier, facing it,
  carries you across: data/story/ch6.json triggers, 0266 scripts 10-13); braille is shown as its text; the Regi chambers' Dig / Strength / Fly spots use the
  move for you when you step on the tile; the Island Cave's two-minute wait cannot be interrupted; Mirage Island is not in the map (the watcher in
  Pacifidlog's house 5 never sees it); Pacifidlog's log-bridge step callback is not done; Route 105's Island Cave door is sealed by a script (its warp, index 3
  of zone 331) plus Black 2's rock model.

## From ch8b (2026-10-07: Routes 121-123, Safari Zone, Mt. Pyre, the Slateport foreign beats, the Aqua Hideout)
- For Ch10 (done by ch10 already): Mt. Pyre's summit hooks are filled in `scenes/MtPyre_Summit_Ch10.inc` (guarded include of
  `scenes/MtPyre_Summit.inc`; labels `Ch10_Pyre_OldWomanReturn`, `Ch10_Pyre_Trigger0-2` = scripts 6-8, the state-2 triggers at
  (22-24,7) are placed by data/story/ch8b.json; Archie uid 102 / old woman uid 103 / old man uid 101; ch10's file uses my labels
  `MPS_OLDWOMAN`, `MPS_ARCHIE`, `Mv_MPS_PlayerUp`, `Mv_MPS_ArchieFaceDown`, `Mv_MPS_ArchieLeft/Right`: keep them). Their text
  is lines 8-12 of `src/text/scenes/MtPyre_Summit.txt`.
- For Ch9 (Dive) / Ch11: the Slateport Harbor workers are hidden from the Mt. Pyre scene on by `FLAG_HIDE_WORKERS_SLATEPORT_HARBOR`
  (the zone init `Ch8_HB_Init` sets it while `VAR_SLATEPORT_HARBOR_STATE` is 1); Ch9 clears it (Sapphire). Capt. Stern's harbor
  script (`Ch8_HB_CaptStern`, scenes/SlateportCity_Harbor_Ch8.inc) starts with Ch6's Scanner branch (`h_goto_if_badge 7,
  Ch6_HB_SternScanner`, a stand-in label when Ch6's file is absent) and has Sapphire's four states.
- For ch8a (Lilycove): the hideout is open from the Slateport harbor scene (it sets `FLAG_HIDE_GRUNT_1/2_BLOCKING_HIDEOUT`, the two
  guards INSIDE AquaHideout_1F) until your Mind Badge wall-up; Matt's scene (AquaHideout_B2F) sets `FLAG_EVIL_TEAM_ESCAPED_IN_SUBMARINE`
  and `FLAG_HIDE_GRUNTS_LILYCOVE` as Sapphire. Nothing else of yours is touched.
- Black 2 facts found (tested in the emulator, 2026-10-07; useful to everyone):
  - **`h_warpsilent` / `FadeOutBlack` + `MapChangeCore` leaves the screen BLACK for good** unless the arriving zone runs a reserved
    script that fades in (the black screen is not a hang: the game runs). A scripted warp that should fade in by itself:
    `MapChangeWarp zone, x, z, dir` (zone tiles as `MapChangeCore`, no y): tested Slateport -> Harbor, Safari entrance <-> Safari Zone.
  - A message window left open (`h_msgbox` / `h_msgbox_actor` without `h_closemessage`) before a movement list or a SystemMsg crashes the
    game (ARM9 undefined instruction): put `h_closemessage` between a line and any movement / info message / `h_giveitem`
    (ch4 found the item case; the Slateport interview crashed on the movement case).
  - Zone-init permissions (ov012 EVCMD_PERM_TABLE) also forbid `BGMPlay` (Sapphire's `savebgm` of the harbor: the Aqua theme starts with
    the Archie scene instead). `ObjInitNPCGPos` works in standalone zones too (Safari Southeast).
  - Doors of rooms (warp tiles) fire when the player presses the door's direction while standing on the tile (e.g. DOWN on Mt. Pyre
    1F (4,6)), not on arrival; test walks by `emu.step` need `calib2` after a zone change (rooms: the default address is often a
    camera copy).
- Safari Zone (Black 2 has no Safari Game): a normal area. The entrance runs Sapphire's flow ($500, Pokéblock Case = Poffin Case, a
  free Box slot with a full party, 30 Safari Balls as items: Black 2's Safari Ball is a real 1.5x ball), the camper inside takes the
  remaining Balls back when you leave (`c8b_take_safari_balls`); no step or ball limit, no bait / rock / run-away mechanics, no
  Pokéblock Feeder. Proposal (only with a battle-engine patch, not done): the Safari battle screen with Safari Balls, rocks and
  bait, and an end-of-game check.
- Other Black 2 stand-ins: Route 121's weather, Route 123's rain/sun cycle (10 weather tiles) and Mt. Pyre's fog (fixed zone weather;
  no script command, see ch10's note on `FieldSetWeather`); the Berry Master's wife asks for a phrase with Black 2's word picker
  (`c8b_phrase`), which has no Gen 3 phrase list, so the picked word's id decides: 1 in 8 gives one of the five rare Berries (once
  each), otherwise a Cheri..Nomel Berry; the submarine shadow of the Harbor and of Hideout B2F has no Black 2 sprite (the grunts jump
  away, Matt looks off to the side); the Safari Pokéblock Feeders are not placed; Trainer rematches are not done (Black 2 has none).
- Gaps in the map (report to the owners): Mt. Pyre 1F-6F are drawn with Celestial Tower's pale blue slabs, not grey gravestones;
  some floor tiles block although the room's collision.per says walkable (1F (20,8)); the Safari Southeast area has only 1 of
  Sapphire's 3 plain people generated (the two with {POKEBLOCK} lines and the Southwest woman are placed by ch8b.json).
- Test helpers (not part of the build): `work/agents/ch8b/` (tests/lib.py has a working Black 2 battle driver, copied from ch5's,
  and `calib2` / `blind` walkers); build with `work/agents/ch8b/build.sh` (HOENN_TEST_CH8B=1|2, HOENN_TEST_WARP=zone,x,z).

## From ch11 (Ever Grande, Victory Road, the Pokémon League, the Hall of Fame; 2026-10-07)
- Ported: Ever Grande City (the visited-flag trigger; the zone init), Victory Road 1F (Wally's entrance fight with the three step triggers and his
  vanish, Wally inside after the Hall of Fame, the trainers of 1F/B1F/B2F as Black 2's global trainer scripts), the Pokémon League lobby (the nurse,
  the clerk with Sapphire's list = shop id 20, the two door guards), Sidney / Phoebe / Glacia / Drake, the Champion's room (Steven, the rival, Prof.
  Birch with the Pokédex rating) and the Hall of Fame scene with the game-clear flags. Wally's house (Surf after Victory Road) was ch6's.
- Test switch `HOENN_TEST_CH11=1|2|3` (`scenes/ch11_test.inc`, run from the zone inits of Ever Grande City, Victory Road 1F, the League lobby and
  the E4 / Champion rooms): 1 = seven Badges, six Lv 100 Groudon (4th move Fire Blast, tapped by the tests), 99 Full Restores / Max Revives, Cut/Surf/Strength; 2 = also the Rain Badge
  (the League opens); 3 = also the four Elite Four members marked beaten. Start from `work/emu/base_littleroot.dst` with
  `HOENN_TEST_WARP=412,826,268` (Ever Grande City, below Victory Road's door) or `=34,7,11` (the Champion's room: the scene starts on its own).
  Build: `work/agents/ch11/build.sh` (own world clone, tests in `work/agents/ch11/tests`).
- **The doors of the Elite Four rooms**: the rooms' door models stay as built (no open/close animation). The room's two warps are the doors: each
  room's zone init (`NNNN_room_EverGrandeCity_*Room_init.s` -> script 3) moves the exit warp off the map (`ObjInitWarpGPos`) until the member is
  beaten and the entrance warp once VAR_ELITE_4_STATE says you walked in (state 1/2/3/4 for Sidney/Phoebe/Glacia/Drake: the OnFrame table runs the
  walk-in scene) or the member is beaten. Beating the member moves the exit warp back (zone tile (7,1)). The League lobby's guards block the corridor
  warps until FLAG_ENTERED_ELITE_FOUR.
- **Whiteout**: Sapphire's whiteout runs ResetEliteFour; Black 2 has no hook. `FLAG_E4_BATTLE_PENDING` (new id 1024) is set before each Elite Four /
  Champion battle and cleared when won; the League lobby's zone init resets the four defeat flags and VAR_ELITE_4_STATE when it is still set.
  Black 2 respawns in Ever Grande's Pokémon Center (the last Center zone), not in the League lobby (Sapphire's HEAL_LOCATION_..._POKEMON_LEAGUE).
- **Hall of Fame / credits**: the Hall of Fame room is a "link" room that is not built. After Steven's "Come with me" the player and Steven walk out
  through the door (both vanish), Black 2's Hall of Fame theme (SEQ_BGM_E_DENDOUIRI) starts and Steven's two Hall of Fame lines are shown over the empty
  Champion's room (a fade to black hides text windows too: an earlier version said them on black and nothing showed), then the screen fades and
  `CH_SetGameClearFlags` runs (Sapphire's list: Lilycove motel staff, ResetEliteFour, Briney / S.S. Tidal / letter flags, Steven's house state 1, Wally inside,
  `Sub_FanClub_GameClear` (ch8a), `Sub_Ch13_GameClear` (ch13: S.S. Ticket scene, Lati TV, Beldum's ball, the Dive ball, Route 131's islet), FLAG_SYS_GAME_CLEAR),
  the Champion ribbon for every Pokémon (`h_give_ribbon`, FLAG_SYS_RIBBON_GET), the heal, the respawn point (`FieldSetTeleportZone 1`, the player's house)
  and the walk home: `h_warp_scene` to Brendan's / May's room (zones 391 / 393, room tile (5,3), script 22 = fade in; tested: the player wakes up in their room).
  Black 2's own `CallGameClear` (record screen ov265 + credits ov266) is **not** run (engine code: after the credits it does two hard-coded map changes to
  zones 0x8b = Shoal Cave's ice room here and 0x1ab = Aspertia, whose Black 2 scripts are the Unova ending): a separate agent does the Hall of Fame room and
  that engine sequence and plugs into `CH_Credits` (a `VMSleep 60` hook between `CH_GameClear` and the warp home, 0068 Champion's room file). Not recorded:
  Black 2's Hall of Fame data (the PC's Hall of Fame list is dropped, notes/STORY_SPECIALS.md).
- **Test artifact found**: after `HOENN_TEST_WARP` (the town sign's MapChangeCore) the first `ActorMsg` of an NPC other than the player hangs (nothing shows),
  also inside a frame scene; coming through a real warp (door / stairs) first cures it (ch9's "talking is dead until a real warp"). The Champion's scene is
  tested from Corridor 4's stairs through the real door (`HOENN_TEST_WARP=43,6,30`, 28 steps up). Not a script bug.
- **Rival name**: this port never stores the rival's name in the save (`{RIVAL}` shows "???????", notes in b2tools/patches/trainers.py): Birch's
  "What did I tell you, {RIVAL}?" is two lines (May for a boy player, Brendan for a girl: `h_msgbox_gendered`). Any other chapter that needs {RIVAL}
  has the same gap.
- Not done: the Elite Four rooms' door animation / spotlights (the room builder has none), `playbgm MUS_ENCOUNTER_ELITE_FOUR` (the League music keeps
  playing), the Hall of Fame machine animation, Sapphire's Elite Four guards check only FLAG_BADGE06_GET (pokeruby): this checks all eight Badges as
  the text says, rematches (Trainer's Eyes) of Wally and the Victory Road trainers.
- Pokédex rating (Birch in the Champion's room): the Hoenn counts of the 202 Hoenn species through Black 2's per-species flags
  (`scenes/ch11_dexcount.inc`, generated by `work/agents/ch11/tools/gen_dex.py`: `Sub_C11_CountDex`, C11_DEXKIND 0 seen / 1 caught -> C11_DEXCOUNT) and
  Sapphire's 20 rating lines; ch0/ch1's Birch in his lab (`ProfBirch_EventScript_AskRatePokedex`, the rating on request) can call the same sub.
  The Pokémon Centers' / bedroom PC's "Prof. Birch's PC" (Black 2's "Professor's PC", after the Pokédex flag 2402) uses the same sub and lines in
  system windows: global 10382 = `src/field_scripts/1260_global_pokedex_rating.s` + text 434 (room_pc 2026-10-09; Black 2's Juniper rating counted Unova species).
- For the lead: the world needs the lead's rebuild (rebuild_slice) so Ever Grande City's generated signs get script numbers 3-6 (my scene entries
  are scripts 1-2); the shops patch has shop id 20 (data/hoenn_shops.json, tested size: a/2/8/2 stays 1300 bytes).

## From fixups2 (2026-10-07: Flannery's exit, TM/HM text, New Mauville's barrier layouts, warp audit)
- **Flannery's platform is NOT a dead end** (ch5's report was wrong, tested in game with the Lavaridge test kit, `screenshots/fixups2/01_*`): ch5's BFS
  (`work/agents/ch5/tests/gym_path.py`) treats the ledge cells of B1F as walls. Sapphire's way off the platform: hole (6,14) or (10,14) -> B1F's
  corridor x 6-7 / 9-10 -> walk down to row 18 -> jump the ledge on row 19 (`MB_JUMP_SOUTH`, built as Black 2 ledge cells) -> the open area rows 20-23 ->
  steam vents (3,21) / (6,20) -> 1F's bottom band (the Gym door). Nothing to build; no door drop needed. Engine quirk: a ledge jump that lands ON a vent tile
  (the (6,20) vent, column x 6) does not fire the vent (Black 2's step triggers do not run on a jump landing): step off and back on (or use column x 7 and
  step left onto it). The people of the arrival room answer after a hole/vent warp (the Gym guide talked in the test): the 10017 arrival script works.
- **Scripted warps (audit)**: every generated step-trigger warp now uses `FadeOutBlack; RTReserveScript 10017; FadeWait; MapChangeCore ...` (story_fixups;
  global script 10017 = fade in + unpause, `b2tools/patches/hm_free.py` Script_18). Tested here, one per kind, from the Littleroot test kit: Lavaridge hole
  and vent (people alive), a cave ladder (Granite Cave 1F -> B1F), a cracked-floor fall (Sky Pillar 2F -> 1F): fade out, fade in, walking afterwards.
  Without the reserved script a scripted map change (`h_warpsilent`'s pattern: pause, fade out, change, unpause) leaves the arrival screen BLACK for good
  and the people dead (tested: a vent built without it). Not scripted, so not affected: Mt. Pyre's holes, the Aqua/Magma warp panels (Black 2 entity
  warps, type 5), doors, stairs. `MapChangeWarp zone, x, z, dir` (Black 2's own warp command, as ch8b's Safari Zone entrance uses) fades by itself.
  Still without it (their owners' files): ch10's Sootopolis Gym ice fall (`gy_ice`, 0046) and the Seafloor Cavern Room 9 -> Route 128 `h_warpsilent`
  (0380) (ch10 was told); ch8a's Museum 1F -> 2F `h_warpsilent` relies on the 2F's OnFrame scene fading in (tested by ch8a). Test-only: the Littleroot
  test-warp signs, `ch13_test.inc`, Ch6's `test_tele`.
- **TM/HM text**: Sapphire's HM05 Flash is Black 2's TM70 (Dewford Gym: "the move Flash from TM70", Granite Cave hiker: "Teach the move Flash from TM70");
  Rock Smash is TM94 (the Mauville house man says "take this TM"); Wattson's TM34 line describes Sludge Wave (may poison; was Shock Wave's "never
  misses"); Route 104's TM09 man describes Venoshock (Bullet Seed's "seeds"); Black 2's TMs are reusable, so the three "a TM can be used only once"
  lines (Route 104 man, Rustboro Gym, the Cutter's "unlike a TM, an HM doesn't break") say so. Left as Sapphire has it: the Secret Power man's lines
  (Route 111, TM43 is Flame Charge: ch4's stand-in, the user may want those lines changed). HM01-04 lines (Cut, Fly, Surf, Strength) and HM06 Dive are
  right (Black 2's HM numbers).
- **New Mauville's barriers** are three layouts now (map replace events 5 / 6, `NM_EVENT_BLUE_DOWN` / `NM_EVENT_GREEN_DOWN` defined in
  `0266_room_NewMauville_Inside.s`, works 0x4036 / 0x4037 reserved in `data/story_ids.json` engine): see notes/CAVES.md. Ch6's walk-through stand-in (scripts
  10-13, its 14 triggers in data/story/ch6.json) is gone (the entries stay as `VMHalt`); the switch triggers read the event works (0x4036 / 0x4037 == 0:
  that colour is not lowered) instead of VAR_TEMP_1/2. New id: `FLAG_NEW_MAUVILLE_REDRAW` 564 (Ch6's reserve). **For the lead**: build the two new rooms
  (`zsh b2tools/rebuild_interiors.sh NewMauville_Inside NewMauville_Inside_BlueDown NewMauville_Inside_GreenDown`) before the next full build; until then
  the interiors patch leaves them out and the barriers stay up.

## From ch10 (Seafloor Cavern, Route 128, Sootopolis City + Gym, Cave of Origin, Kyogre, Mt. Pyre's summit; 2026-10-07)
- **Ported (tested one by one from the Littleroot test kit, proofs in screenshots/ch10/):** Seafloor Cavern Room 1 / 3 / 4 grunts (TRAINER_GRUNT_5 / 6, SHELLY_2,
  GRUNT_7 = scripts 3000 + trainer id) and Room 9 (Archie, the Orb, Kyogre wakes, Maxie and the Magma pair, Archie_2 battle, FLAG_SYS_WEATHER_CTRL, the arrival fade to Route 128); Route 128's Archie / Maxie /
  Steven scene (VAR_ROUTE128_STATE 1); Sootopolis City (crisis people, 11 closed doors, Wallace + Steven lead the player to the Cave of Origin, Steven's flight after Kyogre,
  Kiri's daily Berry, the Expert); the Cave of Origin 1F-B3F shakes and B4F (Kyogre Lv 49, CallWildBattle, caught or not: FLAG_LEGENDARY_BATTLE_COMPLETED, the weather ends, the residents come back,
  Wallace's Gym opens); Sootopolis Gym (1F ice floor with the 66 tile scripts, falls to B1F, 8 B1F trainers, Wallace, Rain Badge, TM03 text names **Psyshock**, with a new second sentence, Black 2's TM03);
  the Mart, Houses 1 / 2 / 3 / 4 / 6 / 8 (TM31 Brick Break, the size-record men); Mt. Pyre summit's foreign beat (`scenes/MtPyre_Summit_Ch10.inc`: Archie returns the Red Orb, the old woman takes the
  Blue Orb back, FLAG_RETURNED_RED_OR_BLUE_ORB). Sapphire has **no Rayquaza / Embedded Tower scene** (Emerald only), so there is nothing to port there.
- **Weather (what the lead must do):** add the new `weather` patch (b2tools/patches/weather.py) to the patch lists of `b2tools/story_build.sh` / `rebuild_slice.sh`, after `story` (my copy: work/agents/ch10/story_build.sh).
  It replaces arm9's GetEntralinkWeatherIfApplicable (0x02032fb8, Hoenn never reaches it) so that GetWeatherAll answers the thunderstorm (id 6) for the zones of Routes 124-128, Lilycove, Mossdeep,
  Sootopolis, Ever Grande while FLAG_SYS_WEATHER_CTRL is set (read from world.json by map name; HOENN_KYOGRE_WEATHER=<id> changes it). Tested: Sootopolis rains in the crisis and is sunny after Kyogre.
  It is **main arm9 code**: savestates made before it need a cold boot / new states. `Common_SetLegendaryWeather` (common/legendary_weather.inc) is a documented no-op (the findings are in its comment: FieldSetWeather
  exists but is forbidden in a zone init and every zone change resets the weather, so a script cannot hold it). The patch is independent of the fixed-weather agent's zone-header weather
  (`fixed_weather.py`): the hook answers before the zone header's weather, so the crisis wins in the crisis zones. I added the guarded include to `scenes/MossdeepCity.inc` (ch9's file; ch11's report).
- **Ids claimed** (data/story_ids.json, src/include/hoenn.h regenerated): VAR_SHROOMISH_SIZE_RECORD 0x40EE, VAR_BARBOACH_SIZE_RECORD 0x40EF, FLAG_SHROOMISH_RECORD_IS_PLAYERS 906, FLAG_BARBOACH_RECORD_IS_PLAYERS 907. No other
  chapter's ids touched. Objects: data/story/ch10.json (150), written by my `work/agents/ch10/tools/ch10_build.py` from `work/agents/ch10/rooms/*.spec` (kept as the source; ask me or edit the room files directly).
- **Test switches** (build env, passed to the assembler): `HOENN_TEST_CH10=1` (end of chapter 9 state: 7 badges, HMs, TM94 / TM70, Lv 100 Tyranitar + Swampert, Bicycle, Blue Orb), `=2` (the Seafloor Cavern done: crisis
  flags), `=3` (Kyogre calmed); extra `HOENN_TEST_CH10_SKIP` (trainer battles skipped), `_OPEN` (Sootopolis doors not locked), `_ICE` (Gym ice already crossed); `scenes/ch10_test.inc`.
- **Closed doors in the crisis:** Black 2 has no "locked door" check, so the zone init of Sootopolis moves the 11 door warps off the map (`ObjInitWarpGPos idx, 0, 0, 0`: warps 1 Center, 2 Mart, 3 Gym, 5-12 the eight houses of the zone's warp list) and signs
  on the door tiles say "The door is closed." (tested). The Gym door's warp stays off until FLAG_LEGENDARY_BATTLE_COMPLETED. If a generator reorders the Sootopolis zone's warps, the indices in `SC_Init` (scenes/SootopolisCity.inc) must follow.
- **Black 2 gaps and what I did:** Skarmory fly-in / fly-out (Steven on Route 128 and in Sootopolis): the person walks in / out and fades (white flash for the sparkle); the Cave of Origin's glow and the Orb effects: a white
  flash; Kyogre has no field model: Pokémon sprite code 4511 as an NPC model (a/2/0/8 table); the Gym ice floor has no crack / stairs visuals (the tile scripts count steps: 8 / 28 / 69 open the ramps, fall to B1F
  at the end); the Mon-size records use `h_random` (Sapphire: the size comes from the Pokémon's personality value); Wailmer Doll: Black 2 has no decorations, so the woman says "Take good care of it!" and sets
  FLAG_RECEIVED_WAILMER_DOLL (nothing given); the Cave of Origin 1F-B3F are dark caves (Sapphire's Flash caves), left as the cave builder made them; the standalone Sootopolis map is reachable only by Dive / the Cave of Origin.
- **For the lead:** (1) add `weather` to the patch lists; (2) the Gym ice fall (`gy_ice`, 0046) and Room 9 -> Route 128 (0380) already use FadeOutBlack + `RTReserveScript 10017` + FadeWait (your audit's request);
  (3) run `converter/gen_map_content.py` and rebuild the world (b2tools/world.py) once more before the next full build: Sootopolis City's and Route 128's generated signs / people take their script numbers from
  scenes/SootopolisCity.inc and Route128.inc (my test world clone got them from `work/agents/ch10/tools/patch_world.py`, same rule as ch3b's); the room files carry `// ---- story`, so the cave / gym generators keep them;
  (4) states made before the weather patch need a cold boot / new states.
- **Hooks / flags other files read (all done, nothing left to add):** FLAG_LEGENDARY_BATTLE_COMPLETED, FLAG_LEGEND_ESCAPED_SEAFLOOR_CAVERN (set in Room 9) and VAR_SOOTOPOLIS_STATE are set by me and already read by
  the Sootopolis Pokémon Center (0886), Mt. Pyre (ch8b) and the Cave of Origin rooms; FLAG_SYS_WEATHER_CTRL is set in Room 9 and cleared in the Cave of Origin B4F (Lilycove, Mossdeep, Routes 124-127 and Ever Grande call
  `Common_SetLegendaryWeather`, now a no-op that exists); Mt. Pyre's VAR_MT_PYRE_STATE 2 -> 3 (ch8b's triggers 6-8 are mine, filled); Steven's house (ch9) is closed by FLAG_HIDE_STEVEN_STEVENS_HOUSE + VAR_STEVENS_HOUSE_STATE 1 in Room 9.

## From ch7 (Routes 118-120, Weather Institute, Fortree, Winona; 2026-10-07)
- Files: `scenes/Route118|119|120|FortreeCity(.inc,_init.inc)` + `ch7_lib.inc` (macros: `c7_kecleon`, `c7_hide_kecleon`, `c7_npc_fly_out`) + `ch7_test.inc`; rooms: Gym 0238, Fortree houses/Decoration Shop, Route 119 house, Weather Institute 1F/2F (+`1127`/`1129` init), Scorched Slab (`0270/0271`); objects `data/story/ch7.json` (made by `work/agents/ch7/gen_objects.py`). Route 119's north part (rival, Kecleon 1, Yasu, Hideo) is Route 119's zone 463 since zone_edges (2026-10-08; scripts 7-9 of `scenes/Route119.inc`); it was Fortree's zone 16 (cell zones). Test: `HOENN_TEST_CH7=1|2|3` (`ch7_test.inc`; 3 = the Gym statue warps to Route 120's bridge).
- Hooks: Ancient Tomb door = rock uid 160 hidden by FLAG_REGI_DOORS_OPENED (ch12); Fortree House 4's boy sends the Wingull (Mossdeep House 2 is ch9's, flags as Sapphire); new flag 618 FLAG_HIDE_WEATHER_INSTITUTE_BOY; Fortree's trade = Black 2 trade 25 (`trades.py`, names on lines 50/51 of system text 37, Skitty Lv 15 fixed).
- Trigger heights (story.py): `ground_y` reads flat planes only (Route 119's stairs: 240, real 56) and the player's RAM height is collision height + 4, so Route 119's rival trigger never fired. ch7.json gives every trigger two entries (collision height and +4, from `work/agents/ch7/tools/tile_y.py`); other chapters' triggers on slopes may have the same bug.
- Test-warp artifact: after a script warp (`MapChangeCore`: the Littleroot-sign test warp, or a test script warp) any NPC balloon (`ActorMsg`/`ParentActorMsg`) crashes the game (2D balloon animation, NULL function `func_0204d46c`) and talking is dead until a real door warp. So the rival (added by `ActorAdd`) speaks through info windows (works) and was not retested with balloons after a door warp. UNTESTED in the emulator: Winona/badge/TM40 (reached her after 3 trainer fights; the battle driver failed), Route 120 Steven/Kecleon/Devon Scope/fly-away, the Scope on Fortree's Kecleon, the Fortree trade/Hidden Power/Wingull houses.
- Gaps: no per-tile weather (Routes 119/120 rain/sun), no `setmetatile` (the bridge's Kecleon tiles, the Tomb rock wall = blocker rock), the Gym's rotating gates are not built, Fortree's wobbling-plank step callback, tree/mountain-disguise trainers (Yasu, Hideo, Takashi, Keigo, Tsunao) and the grass-copying trainers just stand/look around, the Decoration Shop clerks sell nothing, the Berry friend on Route 120 gives a random one of Sapphire's five (no trainer ID), Route 120's camouflaged second Kecleon (object 36) is left out. Invisible Kecleons = `set_invisible` by a scene condition (talk works through a balloon from the empty tile). Steven's fly-away uses Black 2's unused `PlayAlderFlyEffect` (tested only if run 2 below says so).
- Zone watch (from sweep_outdoor; DONE by zone_edges 2026-10-08, see the end of this file): Route 119's north part (x 24-39, y 0-35: rival triggers and rivals, uids 116/125/216/225/226, Kecleon 1, Yasu, Hideo) is in Fortree's zone 16 and its scripts are in `scenes/FortreeCity.inc`. If world.py's new per-map zone rectangles map those tiles to zone 463, move those scripts/objects into `scenes/Route119.inc` (the rival scene tested only with zone 16).
- Map: Weather Institute 2F has a tall black untextured block at the partition wall (room builder); Fortree's row-74 boardwalk is in navgrid but not reachable from row 73 (test walks).


## From halloffame (the Hall of Fame room, Black 2's game-clear sequence, Hoenn credits; 2026-10-07)
- **Flow (tested end to end from a cold boot, screenshots/halloffame/)**: ch11's Champion scene walks Steven and the player out and
  `h_warp_scene 57, 8, 16, 0, 2` -> the Hall of Fame room (zone 57, `0114_room_EverGrandeCity_HallOfFame.s`, script 2): Sapphire's walk with
  Steven (up 6, his line, up 5, the record line), `BMPlayHOFMachineSeq` (Black 2's c09_dendo machine: a Poké Ball per party Pokémon, its light),
  the game-clear flags (ch11's `CH_SetGameClearFlags` / `ResetEliteFour` / `GameClear` ribbons moved here as `HF_*`, with ch8a's fan club and
  ch13's `Sub_Ch13_GameClear` calls), `setrespawn 1`, then Black 2's `CallGameClear 0` (1 on a later clear: Black 2's choice, START skips the
  credits): record screen (ov265), global 9601, the save (no Challenge Mode key screen: user), credits (ov266), THE END (ov267), the
  game restarts at the title; Continue = the player's room (Brendan 391 / May 393, (5,3), facing down); downstairs ch13's S.S. Ticket scene plays.
- **9601** (`src/field_scripts/1242_global_9600.s`: Black 2's 1242.s, Script_1/3 byte-identical): FLAG_SYS_GAME_CLEAR (2400), heal, respawn 1,
  `FieldSetNextZone` 391/393 + flag 2405 (EVENT_FLAG_CONTINUE_SCRIPT: Continue loads that place). Black 2's ~40 Unova post-game flags/works and
  map replacements (L_06DD) are gone. Warp-direction encoding of FieldSetNextZone: 1 up, 2 down, 3 left, 4 right (ConvDirToWarpDir).
- **`b2tools/patches/game_clear.py`** (added to story_build.sh and rebuild_slice.sh): ov012 EventGameClear's two hard-coded ending zones
  (0x8b, 0x1ab, positions, scripts 1 / 0x20) -> zone 57 at (8,5), scripts 1 / 3 (both halt: the screen stays black; Sapphire has no field
  scene there); same-size byte edits, ov012's compressed size 94580 (94584 without: same 512-byte slot). And the credits pictures: a/2/1/5
  photos 0-11 (x2 genders) + the colour picture (command 9) replaced by `data/credits/*.png` (same file sizes; the sprite over the colour
  picture made transparent). Staff text, THE END and the copyright cards are Black 2's.
- **Credits pictures**: greyscale photos with the player in colour like Black 2's, from emulator shots of our maps: Route 101 (Birch's bag and the
  Zigzagoon), Oldale, Petalburg, Rustboro, Dewford, Slateport, Mauville, Lavaridge, Fortree, Lilycove, Mossdeep, colour Sootopolis, Littleroot.
  Remake: `HOENN_TEST_CHCREDITS=1` build (Littleroot's town sign runs `scenes/halloffame_test.inc`: every place, Brendan / May / nobody, waits
  for A), `work/agents/halloffame/tools/credits_shots.py ROM STATE`, `tools/credits_pics.py SHOTS data/credits`.
- **Room**: `data/interior_layouts/EverGrandeCity_HallOfFame.json` + `_styles_halloffame.json` (Black 2's Hall of Fame look: area 319, gold walls
  and pillars, marble runway, c09_dendo on a dais), `data/interiors/57.json` (Steven uid 1). It needs `rebuild_interiors.sh EverGrandeCity_HallOfFame`
  (rebuild_slice does all). Own files 1859/1860/961 in data/hoenn_interiors.json: **converter/allocate_interiors.py own_files() skips 'link' rooms,
  so a rerun would drop them** (the room's status is 'link': CableClub tileset) -> keep own numbers of link rooms that have them.
- Map problem (not mine): Ever Grande City's Pokémon League building (res 409) is not in work/world (cells 25_06/25_07 have no placement).

## From boats (boat cutscenes, cable car; 2026-10-07)
- Every crossing now plays a Black 2 3D boat cutscene, from ONE place: `h_sail_briney` (Mr. Briney: Black 2's white motorboat,
  demo 4) and `h_sail_ferry` (S.S. Tidal, Battle Tower island, Southern Island, the event islands: Black 2's ferry on the open sea,
  demo 26, its own ship music) in `src/include/hoenn_story.inc`, research + macros in `src/field_scripts/common/boat.inc`. Same
  arguments as `ch2_sail` (zone, x, z, dir, arrival script); arrival scripts unchanged (`ch2_land`). `ch2_sail` = `h_sail_briney`
  (Briney only); `ch13_sail_announce` = announcement + `h_sail_ferry`; ch13's and the events agent's ferry calls use `h_sail_ferry`.
- **For the lead: add the patch `boat_demos` to the patch lists** (b2tools/story_build.sh, rebuild_slice.sh, ...; anywhere after
  `title`): it hides Castelia's pier, lamps, flags and people from demo 4 (a/1/5/8 members 256/261/265, draw commands NOPed, every
  file the same size: no layout change). Without it Briney's boat leaves from a Castelia pier (the user: no Unova may show).
- Cable car: `h_ride_cable_car` (the same fade + elevator hum as before, now shared; Black 2 has no cable car/gondola ride).
- Testing a trip: from a cold-boot state of your ROM (work/agents/world_fixes/tools/mkstate.py). From work/emu/base_*.dst a demo
  stays black: the current tree's arm9 is 152 bytes bigger than v13.1's, so every file moved 512 bytes (the states are stale).
- Test-only: `HOENN_TEST_CHBOATS=1|2` (Littleroot's town sign plays Black 2's demos in a row: common/boat_test.inc).


## From events (in-game event tickets and islands; 2026-10-07; notes/EVENTS.md)
- Givers (after the Hall of Fame, first talk; guarded includes inside their scripts): Mom (Eon Ticket, scenes/players_house_1f.inc
  Script_26 before Ch13's check), Capt. Stern (Old Sea Map, SlateportCity_Harbor_Ch8.inc Ch8_HB_CaptStern after h_faceplayer), Prof.
  Cozmo (Aurora Ticket, 0194 FH1_ProfCozmo), Lanette (Mystic Ticket, 1118 LH_Lanette). Whoever regenerates or rewrites those scripts:
  keep the `#if __has_include("scenes/..._Events.inc")` lines where they are.
- ch13: `CH13_EON_TICKET_GIFT` can stay 0: Mom gives the Eon Ticket (same item and FLAG_SYS_HAS_EON_TICKET; with 1 the Hall of Fame
  gives it first and Mom says nothing). LilycoveCity_Harbor_Ch13.inc includes scenes/LilycoveCity_Harbor_Events.inc (guarded) and its
  menu offers the islands per held ticket; Sapphire's Eon branch stays first.
- The lead: rerun world.py so the five island groups exist, then set data/hoenn_standalone.json "build" to "all" (fits RESERVE[8]
  today: 1.40 MB left with them); rebuild the Navel Rock caves (rebuild_interiors.sh NavelRock_* then gen_caves.py NavelRock_*);
  gen_map_content.py for the island scenes. Without the islands built, the tickets are still given and the ferry would sail to a
  missing zone. Future legendaries: notes/EVENTS.md "Adding another legendary island"; raise RESERVE[8] first.

## From story_finish (2026-10-07: trigger heights, test-warp artifact, ch7's untested beats, Flame Charge text)
- **Trigger heights**: `b2tools/patches/story.py ground_y` now reads the collision plane at the tile's centre (slopes
  included, as world.py collision_y). Only Route 119's rival triggers (353,91)/(354,91) changed (240 -> 56); every other
  chapter trigger/sign on outdoor and warp-only maps is on flat ground (checked all data/story/*.json; Route 113's ash
  columns keep ch4's explicit y 32, every walkable tile of them is at 32). ch7's "+4" entries are gone (data/story/ch7.json,
  work/agents/ch7/gen_objects.py): the player's height is the ground; the +4 was emu.calibrate's lowest RAM match, not the
  player. Tested: the single y-56 trigger starts the rival's scene.
- **Scripted warps**: a `MapChangeCore` needs a FadeInBlack after it (the reserved arrival script 10017 or the same script),
  else NPC balloons hang/crash and nobody answers. New macro `h_warp_arrive zone, x, z, dir[, y]` (src/include/hoenn_story.inc:
  fade out, RTReserveScript 10017, map change; follow with FinishAllEvents, ActorsUnpauseAll, VMHalt). The Littleroot
  test warp, ch7's Gym guide/statue test warps use it; ch13_test.inc's four warps got FadeInBlack + FadeWait (ch6's
  test_tele already had them). `h_warpsilent` (no fade-in) stays only where the arrival zone fades in itself.
- ch7 tested (screenshots/story_finish/02-05): Winona (intro balloon, battle, Feather Badge, TM40 Aerial Ace), Route 120
  (Steven, the Kecleon battle, Devon Scope), the Scope on Fortree's Kecleon (it flees, the way opens), Route 119's rival
  (now in balloons again: `r119_say` = ActorMsg from the walking rival), battle, HM02. `HOENN_TEST_CH7=3` gives six Lv 100s
  + 30 Full Restores, `=4` also the Devon Scope.
- Open: Steven's fly-away (`PlayAlderFlyEffect`, ov036 s019D = field effect 30) shows nothing on Route 120 (he stands 50
  frames and vanishes), also with ch8a's work-variable form (now in `c7_npc_fly_out`, + `h_delay 200`). ov036
  EventFieldEffect_Create silently skips an effect when heap 0x15's largest free block is below FIELD_EFFECT_HEAP_SIZES[n]
  (effect 30: 0xa478 = 42 KB): Lilycove (ch8a, works) has room, Route 120 apparently not. Map (sweep_outdoor): Route 120's bridge (x 416-433, rows 75-76, height 32) is not reachable on foot from
  Fortree's side (the stairs at x 427-433 row 73 end at 64 above the river; the bridge's east end (434,75) is at 96).

## From zone_edges (zone rectangles for every map; 2026-10-08)
- **Every map has its own zone up to Sapphire's edges** (b2tools/world.py zone_rects; notes/WORLD.md "Zone rectangles for
  every map"): an outdoor map's people, signs, triggers, items and trainers all sit in the map's own zone, so their
  scripts belong in the map's own scene file. No more "his tile lies in X's zone" includes: moved (scripts renumbered,
  the jsons regenerated with their chapters' helpers):
  - ch7: Route 119's rival scene (triggers 7/8, rivals 116/216/125/225/226), Kecleon 1 (script 9), Yasu and Hideo:
    `scenes/FortreeCity.inc` -> `scenes/Route119.inc` (+ its 6 text lines); Route 119's zone init now sets the rival's
    sprites (Sapphire's Route119 OnTransition); uid 125 is a plain Route 119 object at (17,33) now (no 'zone').
    FortreeCity.inc keeps scripts 1-5 and lines 0-4.
  - ch2: the lost-glasses man (uid 172) = script 6 of `scenes/Route116.inc` (`Route116_GlassesMan.inc` included there,
    text lines 8-12); VerdanturfTown.inc keeps scripts 1-3.
  - ch3b: Route 110's first grunt (uid 122) = script 11 of `scenes/Route110.inc` (`Route110_Grunt1.inc`, line 12);
    Route103.inc keeps scripts 1-2 and lines 0-5.
- **New macro `h_zone_hold`** (src/include/hoenn_story.inc): Black 2 swaps zone the moment the player stands in another
  zone, also while a script walks them, and the swap deletes every actor of the scene. A scene that walks the player over
  a map edge (Wally's tutorial, Petalburg -> Route 102) calls `h_zone_hold` first: the zone lookup then gives every tile
  its cell's zone until the next map change (map-local flag 0x60; `h_zone_release` ends it in place). Scenes that keep
  the player inside one map need nothing.
- Found while testing (not changed, for their owners): (1) Wally's catching demo shows a wrong wild Pokémon with a
  garbage name (Vileplume in 4 runs from one savestate, Ralts with a garbage name in another run): Vileplume is
  species 45 = Growl, the Ralts' first move, so its data blocks are read in the wrong order - most likely
  capture_demo.py's PokeParty_SetParam(PID, 0xff) after CreateTempPkm (Gen 5 orders a Pokémon's four blocks by its PID;
  the random PID's order is then read with PID 0xff's; BtlSetup_SetCaptureDemo copies the parties, so no use-after-free).
  Making the Pokémon with that PID (or not changing it) would avoid it. (2) Routes 119/120 and Fortree show no place-name banner when walked into: their
  invisible-Kecleon scene condition (ch7_lib `c7_hide_kecleon`) runs on every zone entry and closes it (also before).


## From fixes_v151 (v15.1 fixes; 2026-10-08; proofs screenshots/fixes_v151/)
- **Wally's catching demo** (zone_edges' (1) above): fixed in `b2tools/patches/capture_demo.py`. Cause confirmed in the code:
  PML_PkmSetParamCore finds each field's block with PML_PkmGetParamBlockCore(pkm, pkm->pid, block), so setting
  PKM_PARAM_PID after PokeParty_CreateTempPkm only stores the new PID and the old blocks are then read in PID 0xff's order.
  The wild Pokémon is now made by PokeParty_CreatePkm with the PID given (0xff: male, not shiny); slot 0 = Growl. Tested:
  "A wild Ralts appeared!", Ralts ♂ Lv 5, Growl, "Gotcha! Ralts was caught!", the tutorial to its end.
- **New macros `h_keep_banner` / `h_keep_banner_end`** (src/include/hoenn_story.inc, map-local flag 0x61): Black 2 closes
  the place-name banner whenever the field starts ANY script event (ov036 FieldEventProvider_Grid -> func_ov036_021b5168),
  so a scene condition that runs on every zone entry killed it (no script command avoids that: the script itself is the
  event). b2tools/patches/zone_effects.py keep_banner: that hide call skips while flag 0x61 is set. Set it in the zone init,
  clear it first thing in the entry scene; every later script closes the banner as in Black 2. Used by Routes 119/120 and
  Fortree (their Kecleon hide scripts); any other "every entry" scene condition can do the same. Tested: banners
  Route 119 (from 118), Fortree City (from 119), Route 120 (from Fortree); Fortree's Kecleon still invisible, the Devon
  Scope reveals it and it flees.
- **Steven's Route 120 exit** (story_finish's open item above): `c7_npc_fly_out` is ch8a's pattern again; with the save
  fix's bigger field heap the cut-in plays on Route 120 (tested). Note: the cut-in is Black 2's fixed Alder animation
  (Alder's red-haired sprite on Braviary, at the screen centre; Steven and the player are hidden meanwhile), as for ch8a's
  rival in Lilycove.
- converter/allocate_zones.py keeps every place line of the old data/hoenn_zones.json that its rebuild does not make
  (MAPSEC_ALTERING_CAVE line 109 was dropped by rebuild_slice's rerun); a clean rerun now gives the committed file byte
  for byte. The event islands (Faraway, Birth Island, Navel Rock) were already kept through their 'decomp' maps.

## From missing_objects (Sapphire's objects without a Black 2 sprite; 2026-10-08)
- **3D field objects** (b2tools/models_objects.py -> src/objects3d/<code>-<name>/, installed by `b2tools/patches/objects3d.py`, now in
  story_build.sh, rebuild_slice.sh, agent_build_rooms.sh, agent_build_caves.sh after `boulder_1x1`): a/0/4/7 records 0x2000-0x2002 (empty
  in Black 2) and 112 (an empty people record) get BMD0 models appended to a/0/4/8 (+29 KB of its 2 MB reserve). A 3D actor is placed,
  hidden by its spawn flag and moved by movement lists like any NPC, but **never turns with its direction** (ov036's 3D draw processor
  only sets the position), so each facing is its own model (`rotate_bmd`: lossless quarter turns of a BMD's display lists).
  0x2000 submarine shadow (Sapphire's 88x32 shadow, flat on the water, 50 % alpha), 0x2001 / 112 Mr. Briney's boat bow north / south
  (Black 2's motorboat c03_ship_04 at Sapphire's size, wake ring left off), 0x2002 S.S. Tidal bow east (Black 2's Virbank ferry).
  Placed by `data/story/missing_objects.json` ("requires_object3d": story.py leaves them out of a build without the patch).
- Scenes now move the submarine: Ch8's harbor escape (`Mv_HB8_SubmarineExit`, uid 8), Aqua Hideout B2F (uid 4, 4 tiles west) and Ruby's
  Magma Hideout B2F (uid 3, 4 tiles east) instead of a delay; the flags are Sapphire's.
- **Billboards from Sapphire's pixels 1:1** (src/sprites/overworld): 208 Birch's bag (replaces sprite_art.py's hand-drawn satchel, recipe
  now superseded), 292 fossil (ch4.json Root/Claw Fossils), 143 Pichu Doll (May's room), 356 cable car (64x64, both stations).
- **Field heap**: a 3D object's BMD0 stays in the field heap while it is in the zone. Mr. Briney's boat (7.4 KB) costs 7,808 B in Route 104 /
  Dewford / Route 109: the menu save's lowest field-heap free beside it is 9,476 B (17.3 KB without it; save -> Continue tested,
  screenshots/missing_objects/08). Anything that grows pack 0 eats into that: keep pack-0 growth under ~6 KB. Rooms and standalone
  maps have 370+ KB free (the S.S. Tidal's 11.3 KB is no concern there).
- Test switch `HOENN_TEST_CHMO=1` with `HOENN_TEST_WARP=563,6,7` (scenes/missing_objects_test.inc, hooked in Littleroot's town sign):
  stage sentinel `WorkSetConst 0x8004, 0x5A01` (2 = post-game objects), tools in work/agents/missing_objects/tools (mo.py, cont.py).
- **Seafloor Cavern's submarine** (Underwater_SeafloorCavern, Sapphire's map metatiles): 3D object 194 (people record), the metatiles' top
  layer on a camera-facing quad with its floor shadow; collision 4x1 over the hull tiles (5..8,4); talking runs the hull signs' script 3;
  hidden by FLAG_HIDE_UNDERWATER_SUBMARINE_INTERACTION (its zone init sets it once the legend escaped). Tested with a real dive.
- **Berry trees** (user decision 2026-10-08): every daily berry spot shows Sapphire's grown tree of its berry, an NPC on the spot's tile
  (data/story/berry_spots.json, uid 400 + k, script = the spot's 8212 + k) on 7 unused Black 2 12-frame sheets (90, 102, 106, 111, 113,
  114, 180: four trees of one Sapphire palette per sheet, one per facing; b2tools/models_objects.py berry_trees ->
  data/berry_tree_sprites.json). Hidden by FLAG_BERRY_TREE_PICKED_<k> (80 new flags, chapter "Berry_trees" in data/story_ids.json): the
  pick sets it and deletes the tree; L_BerryNewDay (file 1241) clears them all on a new day, and every tree zone's init runs it first:
  global 8297 (RTCallGlobal at the top of the 11 maps' own zone inits) or 8298 (MapScript 2 of Route 102/114/115/117/123, new
  scenes/<Map>_init.inc). Black 2's midnight reset (ov012 `midnight` -> EventWork_ResetDailyFlags, FLAG_DAILY_BERRY_SPOTS) runs in the
  field and on Continue after the zone init, so a tree comes back at the next zone entry of the new day (tested: Route 123 through the
  Berry Master's door, Route 104 through the flower shop). Mirage Island's Liechi tree (spot 73) is hidden on days the island is away
  (scenes/Route130.inc). Cost: no field heap (billboard sheets go to texture VRAM, 6,176 B per sheet in use), at most 2 more
  materials per zone (npc_check: Route 111 23/32 is the fullest tree zone).
- gen_hidden_items.py regenerates 1241_hidden_items.s and berry_spots.json with the trees: rerun it after changing berry spots.
- **Mr. Briney's boat collision 1 x 2** (final_check 2026-10-08): collHeight 2 for codes 0x2001 and 112 (collHeight runs north from
  the boat's tile: the hull's two tiles), so a surfer can no longer sit in the bow (Route 104's cove (12,53) [test], Dewford (12,7),
  Route 109 (21,25)). Scenes that put the player on the boat's tiles: script_check was told (scripted walks ignore it in Black 2).

## From script_check (script regression and crash pass before v15.2; 2026-10-08; proofs screenshots/script_check/)
- **New report step**: b2tools/script_check.py (rebuild_slice.sh, after the ROM; notes/TESTING.md "Script checks"). Both
  versions: 0 open (after the second pass below; the first left 5 unreadable signs).
- **Fixed (crash / soft-lock)**: blackout at home (0780 Script_2, notes/TESTING.md); Black 2's own step triggers left in
  7 rooms (Weather Institute 2F (4,10) ran script 6, which does not exist; Fallarbor Center 2F, Contest Hall, Old Lady's
  Rest Stop (her zone init), Winstrate house, Weather Institute 1F, Game Corner ran an attendant's or a zone-init
  script on a step): b2tools/patches/interiors.py now gives a built room no triggers unless its json lists some (story
  triggers come later from the story patch); Lilycove Dept Store 1F's lottery prizes (4 + the prize kept from earlier)
  and Lilycove House 2's TM44 gave the item with the balloon still open (ch4's crash pattern): h_closemessage added.
- **Fixed (placement)**: three hidden items on beach rocks 8 above the sand were never found (Lilycove PP Up (61,7) and
  Poké Ball (64,31), Route 108 Rare Candy (38,14)): b2tools/patches/story.py sign_y gives a sign / hidden item on a
  solid tile the height of the tiles it is read from. Mr. Briney's boat was not drawn after landing at Dewford or on
  Route 109 until the next map load (the scripts only cleared its flag): h_addobject of the boat (uids 104 / 101) before
  the landing (scenes/DewfordTown.inc Sub_DT_BoatArrives, scenes/Route109.inc).
- **Season banner**: Black 2's place-name banner has two parts, the name and the season ("SUMMER"); it showed with every
  banner (walking in, dive, warp panels, Escape Rope, Dig). b2tools/patches/hoenn_season.py now stops ov036's banner
  loops after the name part (details in its docstring); tested walking Oldale -> Route 103 (05_*; 04_* before).
- **Room 9 crash (Test_Ch10Start's Tyranitar + Swampert)**: test-only. The same party (same species, order, levels) made by
  a normal script (HOENN_TEST_CHSC stage 1) battles Archie in Room 9 with Sand Stream and no crash (09_*). The test party is
  made by PokePartyAdd inside Room 9's zone init; no real gift is (every real PokePartyAdd is in a talk/event script).
  Tests that need that battle: give the party before the warp (the kit) instead of in a zone init.
- **Message windows**: Black 2's own scripts never move an actor or call a window-opening global after LastKeyWait
  without closing, but our 12 places that move the speaker after a waited line play fine (the Rustboro boy, 01_*; Wally's
  tutorial, Room 9, Route 128 were tested by their chapters), so script_check reports only the giveitem/info-window case.
- **Scenes run on the v15.2 tree** (each once): Route 104 Briney ride -> Dewford (with final_check's 1x2 boat
  collision: the walk onto the bow is not blocked), Slateport harbor submarine theft, Aqua Hideout B2F (Matt, the
  submarine leaves), the Route 112 cable car, Mt. Chimney (Archie battle, Maxie), Lilycove harbor (Old Sea Map scene ->
  Faraway Island, the ferry menu with all tickets, Navel Rock and Birth Island arrivals), Rayquaza on Sky Pillar (the
  battle starts), a dive at the Seafloor Cavern entrance (submarine nook).
- **Second pass (2026-10-08, the five open items; proofs 22-26)**:
  - Sky Pillar 2F's crack (0,8) dropped you onto 1F (1,8), a solid tile (Sapphire's (0,8) on 1F is a wall too):
    converter/gen_caves.py now lands a fall on a blocked tile on its nearest walkable neighbour (reported), so 0330
    Script_11 lands on 1F (2,8) (22_*: walking on afterwards).
  - Route 109 -> Dewford: Mv_DT_ExitBoatFromRoute109 (walk_down 2, walk_left, Sapphire's) walked over the pier's edge
    (12,10)/(11,10), solid; now walk_down, walk_left: the player ends on the pier (11,9) facing Mr. Briney (24_*).
  - Signs: world.py's sign_y gives an outdoor sign the height of the tiles it is read from when its own tile is not
    within reach (Route 104 (75,306) 0 -> 16, Route 115 (73,138) 16 -> 32; 25_*, 26_*); shops_rooms.py puts a sign below
    Sapphire's map on its last row, read from any side (Lilycove Dept Store 1F's floor names: Sapphire (0,8) of an 8-row
    map, now (0,7), read from the tile above; 26_*); the truck's box sign (0,3) is gone (no floor tile touches it, and
    Sapphire's truck has no sign); Weather Institute 1F (1,3) is the bed's top-left tile, unreachable in Sapphire too
    (its other three tiles read it): ACCEPT.
  - A girl's blackout before her first Center: record 0 is Brendan's house 1F, so 0780 Script_2 now sends a girl on to
    May's house 1F (6,8) (zone 392) with 0784 Script_2 reserved, the same heal and fade-in (23_*: healed Wurmple, walking,
    menu). In that test the kit's save was a boy's (VAR_LITTLEROOT_HOUSES_STATE_2 = 1), so May's mom's neighbour greeting
    (script 23) ran too; a real girl never has that var at 1 (truck.inc sets it only for a boy).

