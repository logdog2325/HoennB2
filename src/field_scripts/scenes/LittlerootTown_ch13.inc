// Chapter Ch13's two foreign beats in Littleroot Town (Sapphire data/maps/LittlerootTown/scripts.inc; ch13 agent,
// 2026-10-07). Included at the end of 0778_littleroot_town.s (guarded); the file defines
//  - Ch13_LittlerootInit: called by the zone init (script 9) -> LittlerootTown_OnTransition's
//        compare VAR_LITTLEROOT_HOUSES_STATE, 4 / call_if_eq SetExitedHouseAfterLatiSSTicketEvent (and the same for _2):
//        once the player leaves the house after the S.S. Ticket scene, both house states become 5;
//  - Script_25: map-script condition VAR_LITTLEROOT_INTRO_STATE 7 (0779_littleroot_town_init.s) =
//        LittlerootTown_EventScript_BeginDexUpgradeScene: lockall, VAR_LITTLEROOT_INTRO_STATE = 8, releaseall. (Sapphire's
//        scene never became more than this: nothing reads state 8, "Mom"'s lines test >= 7.)
// The test start of the chapter (HOENN_TEST_CH13) is scenes/ch13_test.inc, run from the town sign before its test warp.

Ch13_LittlerootInit:
    WorkCmpConst VAR_LITTLEROOT_HOUSES_STATE, 4
    VMJumpIf CMP_NE, L_C13L_State1
    WorkSetConst VAR_LITTLEROOT_HOUSES_STATE, 5
    WorkSetConst VAR_LITTLEROOT_HOUSES_STATE_2, 5
L_C13L_State1:
    WorkCmpConst VAR_LITTLEROOT_HOUSES_STATE_2, 4
    VMJumpIf CMP_NE, L_C13L_State2
    WorkSetConst VAR_LITTLEROOT_HOUSES_STATE, 5
    WorkSetConst VAR_LITTLEROOT_HOUSES_STATE_2, 5
L_C13L_State2:
    VMReturn

Script_25:                                      // LittlerootTown_EventScript_BeginDexUpgradeScene
    ActorsPauseAll
    WorkSetConst VAR_LITTLEROOT_INTRO_STATE, 8
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt
    .balign 4, 0
#ifdef HOENN_TEST_CH13
#include "scenes/ch13_gameclear.inc"             // (the Hall of Fame includes it itself in a normal build)
#include "scenes/ch13_test.inc"
#endif
