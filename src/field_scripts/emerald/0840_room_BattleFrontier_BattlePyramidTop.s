// BattleFrontier_BattlePyramidTop (zone 420, Emerald only): the top of the Battle Pyramid (pokeemerald
// data/maps/BattleFrontier_BattlePyramidTop; frontier_pyramid 2026-10-12, notes/FRONTIER_PYRAMID.md). The attendant
// takes the player up to the summit (the challenge won), or, when the streak calls the Pyramid King (Emerald's
// GetFrontierBrainStatus: 21 floors for the Silver Symbol, 70 for the Gold, then every 35), steps aside: Brandon comes
// down when the player steps on (17,9). The Start menu's Save runs script 5 (REST / RETIRE, as on the floors).
// Messages: src/text/script/emerald/0649_room_BattleFrontier_BattlePyramidTop.txt (converter/gen_frontier_pyramid.py).
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_story.inc"
#include "hoenn_emerald.inc"
#include "hoenn_frontier.inc"
#include "scenes/frontier_pyramid_lib.inc"

#define PYT_ATTENDANT 1                 // LOCALID_PYRAMID_TOP_ATTENDANT (17,11)
#define PYT_BRANDON 2                   // LOCALID_BRANDON (17,7)
#define PYT_F_BRANDON 0x41              // map-local flag: Brandon hidden (rooms.py)
#define PYT_W_BRAIN 0x4010              // Emerald's VAR_TEMP_C: the Brain's status
#define PYT_W_TRIGGER 0x4011            // VAR_TEMP_2: the summit trigger (17,9) is live while 0
#define PYT_W_ASIDE 0x4012              // VAR_TEMP_D: the attendant has stepped aside for Brandon

    ScriptEntry PYT_Attendant           // 1: _Attendant
    ScriptEntry PYT_Brandon             // 2: Brandon (not talked to in Emerald)
    ScriptEntry PYT_BattleBrandon       // 3: the trigger (17,9): _BattleBrandon
    ScriptEntry PYT_Ready               // 4: condition PY_W_STATE 0 (ON_RESUME)
    ScriptEntry PYT_Menu                // 5: the Start menu's Save
    ScriptEntry PYT_Init                // 6: zone init (ON_TRANSITION, ON_WARP's _SetUpObjects)
    ScriptEntry PYT_Load                // 7: field load: no darkness (pyramid_updatelight 200)
    ScriptEntriesEnd

PYT_Attendant:
    h_lock
    h_faceplayer
    h_goto_if_ne PYT_W_ASIDE, 0, L_PYT_StepForward
    h_goto_if_ne PYT_W_BRAIN, PY_BRAIN_NOT_READY, L_PYT_BrandonHere
    h_msgbox PYL_TOP_SUMMIT                     // "You've reached the summit... Up you go!"
    h_closemessage
    h_applymovement PYT_ATTENDANT, PYT_MvAttendantAside
    h_waitmovement
    h_applymovement PY_PLAYER, PYT_MvPlayerClimb
    h_waitmovement
    h_applymovement PYT_ATTENDANT, PYT_MvAttendantBlock
    h_waitmovement
    WordSetPlayerName 0
    h_msgbox_actor PYL_TOP_CONQUERED, PYT_ATTENDANT
    MEPlay FR_ME_OBTAIN_BP
    MEWait
    h_closemessage
L_PYT_Won:                                      // _WarpToLobbyWon
    fr_set FR_STATUS, FR_ST_WON
    h_warp_arrive PY_LOBBY_ZONE, 7 + PY_LOBBY_OX, 13 + PY_LOBBY_OZ, 0
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt
L_PYT_StepForward:
    h_msgbox PYL_TOP_STEP_FORWARD
    h_closemessage
    h_release
L_PYT_BrandonHere:                              // _BrandonHereMoveAside
    h_msgbox PYL_TOP_CHIEF_HERE
    h_closemessage
    h_applymovement PYT_ATTENDANT, PYT_MvAttendantAside
    h_waitmovement
    WorkSetConst PYT_W_ASIDE, 1
    h_release

PYT_Brandon:
    VMHalt

// _BattleBrandon (the switch on the Brain's status; the camera's pan up is Emerald's, not done here)
PYT_BattleBrandon:
    ActorsPauseAll
    WorkSetConst PYT_W_TRIGGER, 1
    h_goto_if_eq PYT_W_BRAIN, PY_BRAIN_GOLD, L_PYT_IntroGold
    h_goto_if_eq PYT_W_BRAIN, PY_BRAIN_STREAK, L_PYT_HeardSilver
    h_goto_if_eq PYT_W_BRAIN, PY_BRAIN_STREAK_LONG, L_PYT_HeardGold
    EmPyr PY_T0, PY_HEARD
    h_goto_if_ne PY_T0, 0, L_PYT_HeardSilver
    h_msgbox_actor PYL_TOP_EXPLORATIONS, PYT_BRANDON
    h_closemessage
    EmPyr PY_T0, PY_SET_HEARD
    h_applymovement PYT_BRANDON, PYT_MvBrandonApproach
    h_waitmovement
    h_msgbox_actor PYL_TOP_IM_BRANDON, PYT_BRANDON
    VMJump L_PYT_BattleSilver
L_PYT_HeardSilver:
    h_applymovement PYT_BRANDON, PYT_MvBrandonApproach
    h_waitmovement
L_PYT_BattleSilver:
    h_msgbox_actor PYL_TOP_BRING_COURAGE, PYT_BRANDON
    VMCall Sub_PYT_DoBattle
    h_goto_if_ne PY_T0, 1, L_PYT_Lost
    fr_symbol_get FRONTIER_FACILITY_PYRAMID, PY_T1    // _DefeatedBrandonSilver
    h_goto_if_ne PY_T1, 0, L_PYT_BrainWon
    h_msgbox_actor PYL_TOP_PASS_PLEASE, PYT_BRANDON
    h_closemessage
    WordSetPlayerName 0
    MEPlay FR_ME_OBTAIN_SYMBOL
    SystemMsg PYL_TOP_RECEIVED_SYMBOL, 2
    MEWait
    LastKeyWait
    fr_symbol_give FRONTIER_FACILITY_PYRAMID, 0
    h_msgbox_actor PYL_TOP_NEXT_MEETING, PYT_BRANDON
    h_closemessage
    VMJump L_PYT_BrainWon
L_PYT_IntroGold:
    EmPyr PY_T0, PY_HEARD
    h_goto_if_ne PY_T0, 0, L_PYT_HeardGold
    h_msgbox_actor PYL_TOP_RETURNED, PYT_BRANDON
    h_closemessage
    EmPyr PY_T0, PY_SET_HEARD
    h_applymovement PYT_BRANDON, PYT_MvBrandonApproach
    h_waitmovement
    h_msgbox_actor PYL_TOP_OFF_METER, PYT_BRANDON
    VMJump L_PYT_BattleGold
L_PYT_HeardGold:
    h_applymovement PYT_BRANDON, PYT_MvBrandonApproach
    h_waitmovement
L_PYT_BattleGold:
    h_msgbox_actor PYL_TOP_EVERYTHING, PYT_BRANDON
    VMCall Sub_PYT_DoBattle
    h_goto_if_ne PY_T0, 1, L_PYT_Lost
    fr_symbol_get FRONTIER_FACILITY_PYRAMID, PY_T1    // _DefeatedBrandonGold
    h_goto_if_eq PY_T1, 2, L_PYT_BrainWon
    h_msgbox_actor PYL_TOP_REMARKABLE, PYT_BRANDON
    h_closemessage
    WordSetPlayerName 0
    MEPlay FR_ME_OBTAIN_SYMBOL
    SystemMsg PYL_TOP_GOLDEN, 2
    MEWait
    LastKeyWait
    fr_symbol_give FRONTIER_FACILITY_PYRAMID, 1
    h_msgbox_actor PYL_TOP_FAREWELL, PYT_BRANDON
    h_closemessage
L_PYT_BrainWon:
    fr_set FR_BRAIN_BEATEN, 1
    VMJump L_PYT_Won
Sub_PYT_DoBattle:                               // SPECIAL_BATTLE_PYRAMID against the Brain (frontier_pyramid.c fills
    h_closemessage                              // Brandon's three)
    CallTrainerBattle PY_TR_BRAIN, 0, 1
    CallTrainerBattleEnd
    TrainerBattleIsVictory PY_T0
    EmPyr PY_T1, PY_SYNC
    VMReturn
L_PYT_Lost:                                     // BattleFrontier_BattlePyramid_EventScript_WarpToLobbyLost
    fr_set FR_STATUS, FR_ST_LOST
    h_warp_arrive PY_LOBBY_ZONE, 7 + PY_LOBBY_OX, 13 + PY_LOBBY_OZ, 0
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

// ---- map scripts
PYT_Init:                                       // the Battle Bag; Brandon only when the Brain is ready
    EmPyr PY_T0, PY_SETUP, 1
    EmPyr PYT_W_BRAIN, PY_BRAIN
    FlagReset PYT_F_BRANDON
    h_goto_if_ne PYT_W_BRAIN, PY_BRAIN_NOT_READY, L_PYT_InitEnd
    FlagSet PYT_F_BRANDON
L_PYT_InitEnd:
    VMHalt
PYT_Load:                                       // pyramid_updatelight 200: no darkness on the top
    h_flash_scale 0
    VMHalt
PYT_Ready:                                      // ON_RESUME: quit without saving -> the lobby; else ReadyChallenge
    fr_get FR_STATUS, PY_T0
    h_goto_if_eq PY_T0, FR_ST_SAVING, L_PYT_Quit
    h_turnobject PY_PLAYER, 0                   // (ON_WARP: the player faces north)
    EmPyr PY_T1, PY_SYNC
    fr_set FR_STATUS, FR_ST_SAVING
    fr_save_quiet
    fr_set FR_STATUS, PY_ST_IN_CHALLENGE
    WorkSetConst PY_W_STATE, 1
    VMHalt
L_PYT_Quit:
    WorkSetConst PY_W_STATE, 1
    ActorsPauseAll
    h_warp_arrive PY_LOBBY_ZONE, 7 + PY_LOBBY_OX, 13 + PY_LOBBY_OZ, 0
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

// ---- the Start menu's Save: REST / RETIRE (as the floors')
PYT_Menu:
    ActorsPauseAll
    ListMenu_AnchorTopRight 31, 6, 0, 1, PY_T0
    ListMenuAdd PYL_TOP_M_REST, 65535, 0
    ListMenuAdd PYL_TOP_M_RETIRE, 65535, 1
    ListMenuAdd PYL_TOP_M_CANCEL, 65535, 2
    ListMenuShow
    h_goto_if_eq PY_T0, 0, L_PYT_Rest
    h_goto_if_eq PY_T0, 1, L_PYT_Retire
    h_release
L_PYT_Rest:
    SystemMsg PYL_TOP_CONFIRM_REST, 2
    YesNoWin PY_T0
    h_goto_if_ne PY_T0, 0, L_PYT_MenuEnd
    PlayerGetGPos PY_T1, PY_T2
    EmPyr PY_T1, PY_REST_POS, PY_T2
    EmPyr PY_T3, PY_SYNC
    fr_rest_and_quit PY_LOBBY_ZONE, 7 + PY_LOBBY_OX, 13 + PY_LOBBY_OZ, 0, PYL_TOP_SAVING, PY_PLAYER
L_PYT_Retire:
    SystemMsg PYL_TOP_CONFIRM_RETIRE, 2
    YesNoWin PY_T0
    h_goto_if_ne PY_T0, 0, L_PYT_MenuEnd
    h_closemessage
    VMJump L_PYT_Lost
L_PYT_MenuEnd:
    h_closemessage
    h_release

    .balign 4, 0
PYT_MvAttendantAside:                   // _AttendantMoveAside
    walk_right
    walk_in_place_fastest_left
    step_end
    .balign 4, 0
PYT_MvAttendantBlock:                   // _AttendantBlockPath
    walk_left
    walk_in_place_fastest_up
    step_end
    .balign 4, 0
PYT_MvPlayerClimb:                      // _PlayerClimbToTop
    walk_up 5
    walk_in_place_fastest_down
    step_end
    .balign 4, 0
PYT_MvBrandonApproach:                  // _BrandonApproachPlayer
    walk_fast_down
    step_end
