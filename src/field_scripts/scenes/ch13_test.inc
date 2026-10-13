// Chapter Ch13 test start (test builds only: HOENN_TEST_CH13=<stage>; notes/STORY_PORTING.md "Test switches"). Included at the
// end of scenes/LittlerootTown_ch13.inc. Littleroot's four signs warp (and run the start state, once) when HOENN_TEST_CH13_W1..4
// is set to the MapChangeCore arguments "zone,x,0,z,dir": the town sign (stand at (183,366) facing north, from
// work/emu/base_littleroot.dst; notes/TESTING.md) = W1, the player's house sign (175,360) = W2, Birch's house sign (180,360) = W3,
// the Lab sign (174,370) = W4 (stand below, face north, press A). Never assembled into normal builds.
// It is the state after Chapter 11's credits: eight Badges, the game cleared (FLAG_SYS_GAME_CLEAR), a Lv 100 Swampert,
// Surf/Dive/Fly HMs and the Bicycle, the Hall of Fame's flags (scenes/ch13_gameclear.inc: houses state 3 and Dad at home,
// Beldum's ball, the Dive ball, the Sky Pillar islet), Ch11's own flags of the Hall of Fame (the S.S. Tidal at the harbors, Steven's
// letter and VAR_STEVENS_HOUSE_STATE 1, Steven gone) and Ch9's Mind Badge effect on the Slateport harbor (the attendant is there).
// The house sign (W2) keeps the state as it is after the Hall of Fame (the house scene hands over the S.S. Ticket); the
// others (W1, W3, W4) also give the S.S. Ticket and the Eon Ticket (Liberty Pass + FLAG_SYS_HAS_EON_TICKET) and skip the
// house scene. HOENN_TEST_CH13's value is not used (1).
#ifdef HOENN_TEST_CH13
#ifndef CH13_TEST_INC
#define CH13_TEST_INC
#ifdef HOENN_TEST_CH13_W1
Test_Ch13Warp1:
    VMCall Test_Ch13Start
    VMCall Test_Ch13Tickets
    MapChangeCore HOENN_TEST_CH13_W1
    FadeInBlack                         // (story_finish: a scripted warp needs a fade-in, else no balloon/talk works)
    FadeWait
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt
#endif
#ifdef HOENN_TEST_CH13_W2
Test_Ch13Warp2:
    VMCall Test_Ch13Start
    MapChangeCore HOENN_TEST_CH13_W2
    FadeInBlack                         // (story_finish: a scripted warp needs a fade-in, else no balloon/talk works)
    FadeWait
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt
#endif
#ifdef HOENN_TEST_CH13_W3
Test_Ch13Warp3:
    VMCall Test_Ch13Start
    VMCall Test_Ch13Tickets
    MapChangeCore HOENN_TEST_CH13_W3
    FadeInBlack                         // (story_finish: a scripted warp needs a fade-in, else no balloon/talk works)
    FadeWait
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt
#endif
#ifdef HOENN_TEST_CH13_W4
Test_Ch13Warp4:
    VMCall Test_Ch13Start
    VMCall Test_Ch13Tickets
    MapChangeCore HOENN_TEST_CH13_W4
    FadeInBlack                         // (story_finish: a scripted warp needs a fade-in, else no balloon/talk works)
    FadeWait
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt
#endif
Test_Ch13Start:
    PokePartyRecoverAll                 // every entry: a full heal for battle tests
    h_goto_if_set 1513, L_C13T_Done     // once (1513 = Ch13's first reserved flag, used here as the "test start done" mark)
    h_setflag 1513
    FlagSet 2401                        // FLAG_SYS_POKEMON_GET
    FlagSet 2403                        // FLAG_SYS_B_DASH
    FlagSet 2402                        // Black 2's Pokédex flag
    h_setflag FLAG_SYS_POKEDEX_GET
    h_setflag FLAG_ADVENTURE_STARTED
    h_setflag FLAG_DEFEATED_RIVAL_ROUTE103
    h_setvar VAR_STARTER_MON, 2
    h_getpartysize HLIB_TMP
    h_goto_if_ne HLIB_TMP, 0, L_C13T_Party
    PokePartyAdd HLIB_TMP, SPECIES_SWAMPERT, 0, 100
L_C13T_Party:
    TrainerCardAddBadge 0
    FlagSet 2414
    TrainerCardAddBadge 1
    FlagSet 2415
    TrainerCardAddBadge 2
    FlagSet 2416
    TrainerCardAddBadge 3
    FlagSet 2417
    TrainerCardAddBadge 4
    FlagSet 2418
    TrainerCardAddBadge 5
    FlagSet 2419
    TrainerCardAddBadge 6
    FlagSet 2420
    TrainerCardAddBadge 7
    FlagSet 2421
    h_setflag FLAG_RECEIVED_POKENAV
    h_setflag FLAG_RECEIVED_HM_SURF
    h_setflag FLAG_RECEIVED_HM08
    ItemAdd ITEM_HM01, 1, HLIB_TMP
    ItemAdd ITEM_HM02, 1, HLIB_TMP
    ItemAdd ITEM_HM03, 1, HLIB_TMP
    ItemAdd ITEM_HM04, 1, HLIB_TMP
    ItemAdd ITEM_HM05, 1, HLIB_TMP
    ItemAdd ITEM_HM06, 1, HLIB_TMP
    ItemAdd ITEM_BICYCLE, 1, HLIB_TMP   // the Mach Bike
    MoneyAdd 10000
    h_setflag FLAG_SYS_GAME_CLEAR       // Sapphire's EverGrandeCity_HallOfFame_EventScript_SetGameClearFlags, Ch11's lines:
    h_clearflag FLAG_HIDE_SS_TIDAL_SLATEPORT_HARBOR
    h_clearflag FLAG_HIDE_SS_TIDAL_LILYCOVE_HARBOR
    h_clearflag FLAG_HIDE_BRINEY_AND_PEEKO_SS_TIDAL
    h_clearflag FLAG_HIDE_STEVENS_LETTER
    h_setvar VAR_STEVENS_HOUSE_STATE, 1
    h_setflag FLAG_HIDE_STEVEN_STEVENS_HOUSE
    h_clearflag FLAG_HIDE_WORKERS_SLATEPORT_HARBOR   // Ch9's Mind Badge effect (TateAndLizaDefeated)
    VMCall Sub_Ch13_GameClear           // Ch13's lines (scenes/ch13_gameclear.inc)
#ifdef HOENN_TEST_CH13_EVENTS
#include "scenes/events_test.inc"               // (events agent) Emerald's tickets and Master Balls (every warp)
#endif
#ifdef HOENN_EMERALD
#include "scenes/emerald_test_chain.inc"
    em_test_chain 130                                 // Emerald-only state of the chapters before (scenes/emerald_test_chain.inc)
#endif
L_C13T_Done:
    VMReturn

Test_Ch13Tickets:                       // warps 1, 3 and 4 (not the house sign): the state after the house scene, with both tickets
    ItemAdd ITEM_SS_TICKET, 1, HLIB_TMP
    h_setflag FLAG_RECEIVED_SS_TICKET
    h_setflag FLAG_HIDE_NORMAN_LITTLEROOT
    h_setvar VAR_LITTLEROOT_HOUSES_STATE, 5
    h_setvar VAR_LITTLEROOT_HOUSES_STATE_2, 5
    ItemAdd ITEM_EON_TICKET, 1, HLIB_TMP
    h_setflag FLAG_SYS_HAS_EON_TICKET
    VMReturn
#endif
#endif
