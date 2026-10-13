// Post-game test start (test builds only: HOENN_TEST_CHPOSTGAME=1, with HOENN_TEST_CH13=1 for chapter Ch13's start state;
// postgame_scripts 2026-10-07). Two Littleroot signs run a start state once and warp to HOENN_TEST_CHPOSTGAME_W =
// MapChangeCore's "zone,x,0,z,dir" (default 563,6,0,7,0: a sentinel the tests overwrite in an APFS clone of the ROM, as
// b2tools/room_look.py does, so one build reaches every test spot):
//  - the town sign (stand at (183,366) facing north; notes/TESTING.md): Ch13's state after the credits and the S.S.
//    Ticket scene (Test_Ch13Start + Test_Ch13Tickets: eight Badges, the game cleared and its flags, the Lati news waiting
//    on the TV, a Lv 100 Swampert, HMs, Bicycle) + 20 Master Balls, Norman beaten (Petalburg Gym state 7, TM42);
//  - Birch's house sign (180,360, facing north): the same, plus the National Dex (PokeDexGiveNational,
//    VAR_DEX_UPGRADE_JOHTO_STARTER_STATE 3) and all seven roamers roaming (Latias as after the TV news), started again
//    after each warp at location HOENN_TEST_CHPOSTGAME_LOC (0-19, a row of Sapphire's sRoamerLocations: 0 Route 110)
//    when set, else random;
//  - the Lab sign (174,370, facing north): the town sign's state, then the Hall of Fame scene (0114 script 2) and its
//    CallGameClear (the knocked-out roamers' return: roamers.c PG_OnGameClear).
// Never assembled into normal builds.
#ifdef HOENN_TEST_CHPOSTGAME
#ifndef POSTGAME_TEST_INC
#define POSTGAME_TEST_INC
#ifndef HOENN_TEST_CH13
#error "HOENN_TEST_CHPOSTGAME needs HOENN_TEST_CH13=1 (chapter Ch13's start state)"
#endif
#ifndef HOENN_TEST_CHPOSTGAME_LOC
#define HOENN_TEST_CHPOSTGAME_LOC PG_RANDOM_LOC
#endif
#ifndef HOENN_TEST_CHPOSTGAME_W
#define HOENN_TEST_CHPOSTGAME_W 563, 6, 0, 7, 0
#endif
Test_PG_Sign:
    VMCall Test_PG_Start
    MapChangeCore HOENN_TEST_CHPOSTGAME_W
    VMJump L_PGT_FadeIn
Test_PG_Sign2:
    VMCall Test_PG_Start
    h_goto_if_set 2433, L_PGT_Warp2     // once (2433: the second reserved flag, test only)
    h_setflag 2433
    PokeDexGiveNational
    h_setvar VAR_DEX_UPGRADE_JOHTO_STARTER_STATE, 3
    h_setflag FLAG_ROAMING_BEASTS_BIRDS_STARTED
    h_setflag FLAG_LATIOS_OR_LATIAS_ROAMING
    h_clearflag FLAG_SYS_TV_LATI
L_PGT_Warp2:
    MapChangeCore HOENN_TEST_CHPOSTGAME_W
    // (after the map load, which moves every roamer to another set: roamers.c PG_OnSpawn)
    pg_roamer_start 0, HOENN_TEST_CHPOSTGAME_LOC
    pg_roamer_start 1, HOENN_TEST_CHPOSTGAME_LOC
    pg_roamer_start 2, HOENN_TEST_CHPOSTGAME_LOC
    pg_roamer_start 3, HOENN_TEST_CHPOSTGAME_LOC
    pg_roamer_start 4, HOENN_TEST_CHPOSTGAME_LOC
    pg_roamer_start 5, HOENN_TEST_CHPOSTGAME_LOC
    pg_roamer_start 6, HOENN_TEST_CHPOSTGAME_LOC
L_PGT_FadeIn:
    FadeInBlack                         // (story_finish: a scripted warp needs a fade-in, else no balloon/talk works)
    FadeWait
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Test_PG_HoF:                            // the Lab sign (174,370; stand below, face north): into the Hall of Fame scene, as the
    VMCall Test_PG_Start                // Champion's room sends you there (0068: h_warp_scene 57, 8, 16, 0, 2)
    h_warp_scene 57, 8, 16, 0, 2
    h_release

Test_PG_Start:
    VMCall Test_Ch13Start
    h_goto_if_set 2432, L_PGT_Done      // once (2432: Postgame's first reserved flag, the "test start done" mark)
    h_setflag 2432
    VMCall Test_Ch13Tickets
    ItemAdd ITEM_MASTER_BALL, 20, HLIB_TMP
    h_setvar VAR_PETALBURG_GYM_STATE, 7     // Norman beaten, TM42 given (Ch6): his post-battle talk
    h_setflag FLAG_DEFEATED_PETALBURG_GYM
    h_setflag FLAG_RECEIVED_TM42
    h_setvar VAR_ROUTE110_STATE, 1          // the Route 110 rival battle done (Ch3: its triggers)
    h_setvar VAR_ROUTE101_STATE, 3          // Birch rescued (the base state is before it): Route 101's triggers and people
    h_setvar VAR_BIRCH_LAB_STATE, 5
    h_setflag FLAG_RESCUED_BIRCH
    h_setflag FLAG_HIDE_BIRCH_BATTLE_POOCHYENA
    h_setflag FLAG_HIDE_BIRCH_STARTERS_BAG
L_PGT_Done:
    VMReturn
#endif
#endif
