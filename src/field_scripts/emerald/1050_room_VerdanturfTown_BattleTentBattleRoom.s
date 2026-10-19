// VerdanturfTown_BattleTentBattleRoom (zone 525; Emerald only): the Verdanturf tent's battles (pokeemerald
// data/maps/VerdanturfTown_BattleTentBattleRoom/scripts.inc; battle_tents, 2026-10-18, notes/BATTLE_TENTS.md). Reached
// only by script 1 from the corridor. Each battle is the Battle Palace's (the Pokémon choose their own moves by Nature:
// frontier_palace_arena.c) against one of the tent's 30 trainers (tower_setopponent = SetNextBattleTentOpponent: never
// one twice in a challenge), its three Pokémon at the level of the player's highest of the three (at least 30); three
// wins in a row win the tent. Emerald keeps the camera still with a stand-in player object; here the player walks in
// from the stand-in's spot (2,8) (the camera follows). Room origin (1,0).
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_story.inc"
#include "hoenn_emerald.inc"
#include "hoenn_frontier.inc"
#include "scenes/battle_tents_lib.inc"

#define VB_OPP 2                        // the opponent (Emerald LOCALID_VERDANTURF_TENT_BATTLE_OPPONENT)
#define VB_ATT 3                        // the attendant

    ScriptEntry VB_Enter                // 1: OnFrame EnterRoom
    ScriptEntry VB_None                 // 2: the opponent, the attendant
    ScriptEntriesEnd

VB_None:
    VMHalt

VB_Enter:
    ActorsPauseAll
    fd_player_visible
    FadeInBlack
    FadeWait
    h_applymovement TT_PLAYER, VB_MvPlayerIn
    h_waitmovement
    fr_get FR_BATTLE_NUM, FD_T1
    h_goto_if_ne FD_T1, 0, L_VB_Ask     // (a resumed challenge: "ready for the Nth opponent?")
L_VB_Next:                              // NextOpponentEnter: tower_setopponent, the walk in, battletent_getopponentintro
    FrontierPA PA_NEXT_OPPONENT, TT_PA_VERDANTURF, 0, FD_T1
    WorkSet PA_OPP_GFX, FD_T1
    h_addobject VB_OPP, PA_FLAG_OPP
    h_applymovement VB_OPP, VB_MvOpponentIn
    h_waitmovement
    FrontierPA PA_GREETING, TT_PA_VERDANTURF, 0, FD_T1
    fd_say FD_T1, VB_OPP
    h_heal                              // DoPalaceBattle
    FrontierPA PA_BATTLE, TT_PA_VERDANTURF, 0, FD_T1
    h_heal
    h_goto_if_eq FD_T1, 1, L_VB_Won
L_VB_Lost:                              // WarpToLobbyLost
    fd_status FR_ST_LOST
    tt_to_lobby TT_V_LOBBY              // warp MAP_VERDANTURF_TOWN_BATTLE_TENT_LOBBY, 6, 6
L_VB_Won:                               // DefeatedOpponent: the battle number
    WorkSetConst FD_T1, 1
    FrOp FR_OP_ADD | FR_BATTLE_NUM, FD_T1
    h_goto_if_ge FD_T1, 3, L_VB_Three   // (TENT_STAGES_PER_CHALLENGE)
    h_applymovement VB_OPP, VB_MvOpponentOut
    h_waitmovement
    h_removeobject VB_OPP, PA_FLAG_OPP
    h_applymovement VB_ATT, VB_MvFaceDown
    h_applymovement TT_PLAYER, VB_MvFaceUp
    h_waitmovement
    ActorMsg MSGFILE_SCRIPT, BT_V_BATTLEROOM_RESTORE, VB_ATT, 0, 0
    LastKeyWait
    MEPlay MUS_HEAL
    MEWait
    MsgWinCloseAll
    h_heal
L_VB_Ask:                               // AskContinueChallenge: "prepared for the 2nd / 3rd opponent?"
    fr_get FR_BATTLE_NUM, FD_T1
    WorkAdd FD_T1, BT_V_BATTLEROOM_READY_2 - 1
    ActorMsg MSGFILE_SCRIPT, FD_T1, VB_ATT, 0, 0
    fd_menu3 FD_T2, BT_V_BATTLEROOM_MENU_GO_ON, BT_V_BATTLEROOM_MENU_REST, BT_V_BATTLEROOM_MENU_RETIRE
    MsgWinCloseAll
    h_goto_if_eq FD_T2, 0, L_VB_GoOn
    h_goto_if_eq FD_T2, 1, L_VB_Rest
    h_goto_if_eq FD_T2, 2, L_VB_Retire
    VMJump L_VB_Ask
L_VB_GoOn:                              // ContinueChallenge
    h_applymovement VB_ATT, VB_MvFaceRight
    h_applymovement TT_PLAYER, VB_MvFaceRight
    h_waitmovement
    VMJump L_VB_Next
L_VB_Rest:                              // AskPauseChallenge -> PauseChallenge (save, then the soft reset)
    h_yesno_actor BT_V_BATTLEROOM_SAVE_QUIT, VB_ATT, FD_T1
    h_goto_if_no FD_T1, L_VB_Ask
    FlagSet PA_FLAG_OPP
    fr_rest_and_quit TT_V_LOBBY, TT_LX(6), TT_LZ(6), 0, BT_V_BATTLEROOM_SAVING, VB_ATT
L_VB_Retire:                            // AskRetireChallenge
    h_yesno_actor BT_V_BATTLEROOM_RETIRE, VB_ATT, FD_T1
    h_goto_if_no FD_T1, L_VB_Ask
    VMJump L_VB_Lost
L_VB_Three:                             // WarpToLobbyWon
    fd_status FR_ST_WON
    tt_to_lobby TT_V_LOBBY

    .balign 4, 0
VB_MvPlayerIn:                          // Movement_PlayerEnter (from the stand-in's spot)
    walk_up 3
    face_right
    step_end
VB_MvFaceUp:
    face_up
    step_end
VB_MvFaceDown:
    face_down
    step_end
VB_MvFaceRight:
    face_right
    step_end
VB_MvOpponentIn:                        // Movement_OpponentEnter
    walk_down 4
    face_left
    step_end
VB_MvOpponentOut:                       // Movement_OpponentExit
    walk_up 4
    step_end
