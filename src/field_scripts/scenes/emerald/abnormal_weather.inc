// Pokémon Emerald NDS: the abnormal weather of the post-game (emerald_ch12_13, 2026-10-12). Emerald builds only; include
// after "hoenn_story.inc". Emits no code by itself (macros and defines).
//
// pokeemerald: the Weather Institute 2F scientist, after the game, reports a drought or heavy rain on one of 16 route spots
// (Route119_WeatherInstitute_2F_EventScript_TryStartAbnormalWeather, special CreateAbnormalWeatherEvent; a new one on each
// visit to his floor, never Kyogre's / Groudon's once caught or beaten). VAR_ABNORMAL_WEATHER_LOCATION 1-8: a Terra Cave
// mouth opens in a rock wall of Route 114, 115, 116 or 118 (drought); 9-16: rough water on Route 105, 125, 127 or 129
// leads down to the Marine Cave (downpour). It ends after 1000 steps (AbnormalWeatherHasExpired) or, once Kyogre /
// Groudon is caught or beaten, when the player is back on the route (VAR_SHOULD_END_ABNORMAL_WEATHER, the route's
// map_script_2 AbnormalWeather_EventScript_EndEventAndCleanup_1: "The intense sunshine appears to have subsided..." /
// "The massive downpour appears to have stopped...", the screen fades, the mouth / rough water goes).
//
// Here:
//  - the look: b2tools/patches/emerald_postgame.py (the weather: Sapphire NDS's rainstorm / Ruby NDS's drought, the
//    looks the user chose for Emerald's abnormal weather; the mouth / rough water: the route's cells swapped by the map
//    replacement of the spot) and patches/dive.py (the rough water's dive records) read VAR_ABNORMAL_WEATHER_LOCATION
//    only; the scripts end the weather by setting it to 0.
//  - the 1000 steps: VAR_ABNORMAL_WEATHER_STEP_COUNTER keeps Black 2's step record (record 0) of the moment the scientist
//    spoke, and the routes' and caves' zone inits compare (aw_steps_left): a map load after the 1000th step ends it
//    (Emerald counts each step; on the route itself Emerald ends it with its message at that step, here at the next
//    map load, silently). Over while in Terra / Marine Cave: the end is pending, as Emerald's.
//  - a Terra Cave door: each of the 8 route doors into TerraCave_Entrance is parked off the map by patches/hoenn_world.py
//    ("doors_parked", data/emerald/hoenn_interiors.json); the zone init (global AW_GLOBAL_ZONE_INIT) moves the open one
//    onto the mouth's tile (ObjInitWarpGPos). The cave's exit is a dynamic warp: back where the player stepped in.
//  - the routes' map scripts (scenes/<Route>_init.inc, Emerald block): MapScript 2 AW_GLOBAL_ZONE_INIT and the frame
//    condition VAR_SHOULD_END_ABNORMAL_WEATHER 1 -> AW_GLOBAL_CLEANUP. The two globals are scripts 2293 / 2294 of
//    src/field_scripts/emerald/1236_global_2280.s (its text: script/0615, src/text/emerald/overrides_emerald_postgame.json).
#ifndef EM_ABNORMAL_WEATHER_INC
#define EM_ABNORMAL_WEATHER_INC

#define AW_GLOBAL_ZONE_INIT 2293       // a route's zone init: the 1000 steps, the Terra Cave door
#define AW_GLOBAL_CLEANUP 2294         // a route's frame script: the end after Kyogre / Groudon
#define AW_GLOBAL_CAVE_INIT 2295       // Terra / Marine Cave's zone inits: 1000 steps over in there = the end pending
#define AW_T_RAIN_ENDED 61             // script/0615 lines (src/text/emerald/overrides_emerald_postgame.json)
#define AW_T_SUN_ENDED 62
#if defined(HOENN_TEST_AW_STEPS)
#define AW_STEPS HOENN_TEST_AW_STEPS   // TEST ONLY: a shorter weather
#else
#define AW_STEPS 1000                  // pokeemerald AbnormalWeatherHasExpired: ++steps > 999
#endif
#define AW_TMP 0x8038                  // scratch works (scripts' own: 0x8030 HLIB_TMP .. 0x8037 are taken by the libraries)
#define AW_TMP2 0x8039
#define AW_TMP3 0x803A
#define AW_MAP_RELOAD_EVENT 7          // map replace event 7 (Route 131's / Route 103's, set after the game): set to its
                                       // own state with reload = the matrix patched again (Route131.inc's way)
#define AW_TERRA_SPOTS 8               // 1-8 Terra Cave (drought), 9-16 Marine Cave (rain): MARINE_CAVE_LOCATIONS_START 9

// ---- the 8 Terra Cave spots: the route zone, the door (warp index in the zone, its tile and the height of the tile the
// player stands on in front of it, in 16-unit steps), the tile in front (the cave's dynamic exit leaves the player
// there, facing down). Written by work/agents/emerald_ch12_13/tools/mk_aw_inc.py from the Emerald world (world.json
// doors, Black 2's warp count of each zone's entity file, the cells' collision); keep the lines between the markers.
// (Assembler symbols, not #defines: the macros below build their names from the spot number, AW_ZONE_\k.)
// >>> aw spots
    .set AW_ZONE_1, 383   // Route114 North (7,4)
    .set AW_DOOR_1, 7
    .set AW_DX_1, 95
    .set AW_DY_1, 0
    .set AW_DZ_1, 64
    .set AW_ZONE_2, 383   // Route114 South (6,46)
    .set AW_DOOR_2, 6
    .set AW_DX_2, 94
    .set AW_DY_2, 4
    .set AW_DZ_2, 106
    .set AW_ZONE_3, 387   // Route115 West (21,6)
    .set AW_DOOR_3, 2
    .set AW_DX_3, 69
    .set AW_DY_3, 2
    .set AW_DZ_3, 106
    .set AW_ZONE_4, 387   // Route115 East (36,10)
    .set AW_DOOR_4, 3
    .set AW_DX_4, 84
    .set AW_DY_4, 3
    .set AW_DZ_4, 110
    .set AW_ZONE_5, 423   // Route116 North (59,13)
    .set AW_DOOR_5, 4
    .set AW_DX_5, 147
    .set AW_DY_5, 1
    .set AW_DZ_5, 193
    .set AW_ZONE_6, 423   // Route116 South (79,6)
    .set AW_DOOR_6, 5
    .set AW_DX_6, 167
    .set AW_DY_6, 2
    .set AW_DZ_6, 186
    .set AW_ZONE_7, 446   // Route118 East (42,6)
    .set AW_DOOR_7, 2
    .set AW_DX_7, 330
    .set AW_DY_7, 0
    .set AW_DZ_7, 206
    .set AW_ZONE_8, 446   // Route118 West (9,6)
    .set AW_DOOR_8, 3
    .set AW_DX_8, 297
    .set AW_DY_8, 0
    .set AW_DZ_8, 206
// the route zone of every spot (1-8 above; 9-16: Route 105, 125, 127, 129 twice each)
    .set AW_ZONE_9, 331
    .set AW_ZONE_10, 331
    .set AW_ZONE_11, 194
    .set AW_ZONE_12, 194
    .set AW_ZONE_13, 205
    .set AW_ZONE_14, 205
    .set AW_ZONE_15, 238
    .set AW_ZONE_16, 238
// the Marine Cave's way back: Underwater_MarineCave's exit is a dynamic warp (GameData's next zone); the zone init sets
// it to the tile in front of (below) the spot's door into it on its underwater route (pokeemerald Underwater_Route105/
// 125/127/129 warps 0 / 1; Underwater_Route127 = this port's Underwater3, its Emerald variant's origin (0,15))
    .set AW_UZONE_9, 379
    .set AW_UX_9, 13
    .set AW_UZ_9, 5
    .set AW_UZONE_10, 379
    .set AW_UX_10, 17
    .set AW_UZ_10, 67
    .set AW_UZONE_11, 382
    .set AW_UX_11, 22
    .set AW_UZ_11, 11
    .set AW_UZONE_12, 382
    .set AW_UX_12, 45
    .set AW_UZ_12, 31
    .set AW_UZONE_13, 218
    .set AW_UX_13, 57
    .set AW_UZ_13, 21
    .set AW_UZONE_14, 218
    .set AW_UX_14, 67
    .set AW_UZ_14, 54
    .set AW_UZONE_15, 386
    .set AW_UX_15, 26
    .set AW_UZ_15, 4
    .set AW_UZONE_16, 386
    .set AW_UX_16, 32
    .set AW_UZ_16, 22
// the 8 routes in spot order (114, 115, 116, 118, 105, 125, 127, 129) as zones: WordSetPlaceName takes a zone and
// buffers its place name (pokebw2 s0059_WordSetPlaceName: ZoneData_GetPlaceNameID)
    .set AW_PLACE_1, 383
    .set AW_PLACE_2, 387
    .set AW_PLACE_3, 423
    .set AW_PLACE_4, 446
    .set AW_PLACE_5, 331
    .set AW_PLACE_6, 194
    .set AW_PLACE_7, 205
    .set AW_PLACE_8, 238
// <<< aw spots

// ---- the 1000 steps (pokeemerald AbnormalWeatherHasExpired): jumps to `left` while fewer than AW_STEPS steps were
// taken since the scientist spoke (Black 2's step record, low 16 bits: RecordGet keeps them; the u16 difference wraps)
    .macro aw_steps_left left                          // (uses AW_TMP3 only: AW_TMP holds the zone)
    RecordGet 0, AW_TMP3
    WorkSub AW_TMP3, VAR_ABNORMAL_WEATHER_STEP_COUNTER
    WorkCmpConst AW_TMP3, AW_STEPS
    VMJumpIf CMP_LT, \left
    .endm

// ---- pokeemerald CreateAbnormalWeatherEvent: a new spot (no Terra spot once Groudon is caught or beaten, no Marine one
// once Kyogre is), the step mark
    .macro aw_create
    RecordGet 0, VAR_ABNORMAL_WEATHER_STEP_COUNTER     // VarSet(VAR_ABNORMAL_WEATHER_STEP_COUNTER, 0)
    h_goto_if_set FLAG_DEFEATED_KYOGRE, .Lawc_terra\@
    h_goto_if_set FLAG_DEFEATED_GROUDON, .Lawc_marine\@
    Random AW_TMP, 2                                   // (Random() & 1) == 0: Terra
    h_goto_if_eq AW_TMP, 0, .Lawc_terra\@
.Lawc_marine\@:
    Random AW_TMP, 8                                   // (Random() % MARINE_CAVE_LOCATIONS) + MARINE_CAVE_LOCATIONS_START
    WorkAdd AW_TMP, 9
    VMJump .Lawc_set\@
.Lawc_terra\@:
    Random AW_TMP, 8                                   // (Random() % TERRA_CAVE_LOCATIONS) + TERRA_CAVE_LOCATIONS_START
    WorkAdd AW_TMP, 1
.Lawc_set\@:
    WorkSet VAR_ABNORMAL_WEATHER_LOCATION, AW_TMP
    .endm

// ---- pokeemerald GetAbnormalWeatherMapNameAndType: word \word = the spot's route (place name), jumps to `kyogre` for a
// Marine spot (heavy rain), falls through for a Terra spot (drought)
    .macro aw_place word, kyogre
    WorkSet AW_TMP, VAR_ABNORMAL_WEATHER_LOCATION
    WorkSub AW_TMP, 1
    WorkDiv AW_TMP, 2                                  // route 0-7
    aw_place_if \word, 0, AW_PLACE_1
    aw_place_if \word, 1, AW_PLACE_2
    aw_place_if \word, 2, AW_PLACE_3
    aw_place_if \word, 3, AW_PLACE_4
    aw_place_if \word, 4, AW_PLACE_5
    aw_place_if \word, 5, AW_PLACE_6
    aw_place_if \word, 6, AW_PLACE_7
    aw_place_if \word, 7, AW_PLACE_8
    h_goto_if_gt VAR_ABNORMAL_WEATHER_LOCATION, AW_TERRA_SPOTS, \kyogre
    .endm
    .macro aw_place_if word, r, place
    h_goto_if_ne AW_TMP, \r, .Lawp\@
    WordSetPlaceName \word, \place
.Lawp\@:
    .endm

// ---- a route's zone init (AW_GLOBAL_ZONE_INIT; level 2: zone init commands only)
    .macro aw_door k                                   // spot k's door, when it is the spot and this its route
    h_goto_if_ne VAR_ABNORMAL_WEATHER_LOCATION, \k, .Lawd\@
    h_goto_if_ne AW_TMP, AW_ZONE_\k, .Lawd\@
    ObjInitWarpGPos AW_DOOR_\k, AW_DX_\k, AW_DY_\k, AW_DZ_\k
.Lawd\@:
    .endm
    .macro aw_reload_if k                              // the matrix again when spot k (just ended) is on this route
    h_goto_if_ne AW_TMP2, \k, .Lawr\@
    h_goto_if_ne AW_TMP, AW_ZONE_\k, .Lawr\@
    MapReplaceIsEventSet AW_MAP_RELOAD_EVENT, AW_TMP3
    MapReplaceSetEvent AW_MAP_RELOAD_EVENT, AW_TMP3, 1
.Lawr\@:
    .endm
    .macro aw_zone_init
    h_goto_if_eq VAR_ABNORMAL_WEATHER_LOCATION, 0, .Lawz_done\@
    RTGetZoneID AW_TMP
    h_goto_if_eq VAR_SHOULD_END_ABNORMAL_WEATHER, 1, .Lawz_on\@     // (the end pending: the cleanup's frame script)
    aw_steps_left .Lawz_on\@
    WorkSet AW_TMP2, VAR_ABNORMAL_WEATHER_LOCATION   // over: VarSet(VAR_ABNORMAL_WEATHER_LOCATION, ABNORMAL_WEATHER_NONE)
    WorkSetConst VAR_ABNORMAL_WEATHER_LOCATION, 0
    .irp k, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16
    aw_reload_if \k
    .endr
    VMJump .Lawz_done\@
.Lawz_on\@:
    .irp k, 1, 2, 3, 4, 5, 6, 7, 8
    aw_door \k
    .endr
.Lawz_done\@:
    .endm

// ---- Terra / Marine Cave's zone init (AW_GLOBAL_CAVE_INIT): the 1000 steps over while in there = the end is pending
// (pokeemerald AbnormalWeatherHasExpired: in the Marine / Terra Cave maps VAR_SHOULD_END_ABNORMAL_WEATHER = 1)
// Also the caves' way out: Terra Cave Entrance's exit and Underwater_MarineCave's are dynamic warps (GameData's next
// zone, which Black 2 sets from no warp of ours: it led into Unova's zone 0); pokeemerald returns you to where you came
// in: the tile in front of the spot's Terra Cave door (facing down), or of its underwater door (Black 2 dir 2 = down).
    .macro aw_next_terra k
    h_goto_if_ne VAR_ABNORMAL_WEATHER_LOCATION, \k, .Lawnt\@
    FieldSetNextZone AW_ZONE_\k, 2, AW_DX_\k, AW_DY_\k, (AW_DZ_\k+1)
.Lawnt\@:
    .endm
    .macro aw_next_marine k
    h_goto_if_ne VAR_ABNORMAL_WEATHER_LOCATION, \k, .Lawnm\@
    FieldSetNextZone AW_UZONE_\k, 2, AW_UX_\k, 0, AW_UZ_\k
.Lawnm\@:
    .endm
    .macro aw_cave_init
    .irp k, 1, 2, 3, 4, 5, 6, 7, 8
    aw_next_terra \k
    .endr
    .irp k, 9, 10, 11, 12, 13, 14, 15, 16
    aw_next_marine \k
    .endr
    h_goto_if_eq VAR_ABNORMAL_WEATHER_LOCATION, 0, .Lawci\@
    h_goto_if_eq VAR_SHOULD_END_ABNORMAL_WEATHER, 1, .Lawci\@
    aw_steps_left .Lawci\@
    WorkSetConst VAR_SHOULD_END_ABNORMAL_WEATHER, 1
.Lawci\@:
    .endm

// ---- a route's frame script while VAR_SHOULD_END_ABNORMAL_WEATHER is 1 (AW_GLOBAL_CLEANUP; pokeemerald
// AbnormalWeather_EventScript_EndEventAndCleanup_1/_2): the message, the screen fades, the weather and the cave's door /
// rough water are gone. A Terra spot: a map change to the tile in front of its door (Emerald's fade + DrawWholeMapView:
// the closed rock, the zone's own weather); a Marine spot: the player is swimming somewhere on the route, the weather
// changes behind the fade (the rough water is drawn until the next map load; it cannot be dived into any more).
    .macro aw_arrive k
    h_goto_if_ne AW_TMP, \k, .Lawa\@
    h_warp_arrive AW_ZONE_\k, AW_DX_\k, (AW_DZ_\k+1), 1, AW_DY_\k
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt
.Lawa\@:
    .endm
    .macro aw_cleanup
    ActorsPauseAll
    h_goto_if_gt VAR_ABNORMAL_WEATHER_LOCATION, AW_TERRA_SPOTS, .Lawcl_rain\@
    SystemMsg AW_T_SUN_ENDED, 2                        // gText_AbnormalWeatherEnded_Sun
    VMJump .Lawcl_msg\@
.Lawcl_rain\@:
    SystemMsg AW_T_RAIN_ENDED, 2                       // gText_AbnormalWeatherEnded_Rain
.Lawcl_msg\@:
    LastKeyWait
    InfoMsgClose
    WorkSet AW_TMP, VAR_ABNORMAL_WEATHER_LOCATION
    WorkSetConst VAR_ABNORMAL_WEATHER_LOCATION, 0      // ABNORMAL_WEATHER_NONE
    WorkSetConst VAR_SHOULD_END_ABNORMAL_WEATHER, 0
    .irp k, 1, 2, 3, 4, 5, 6, 7, 8
    aw_arrive \k
    .endr
    FadeOutBlack                                       // (a Marine spot) fadescreenswapbuffers, setweather SUNNY, doweather
    FadeWait
    FieldSetWeather 0xFFFF, 1                          // the zone's own weather again (emerald_postgame.c: no spot now)
    FadeInBlack
    FadeWait
    ActorsUnpauseAll
    .endm
#endif
