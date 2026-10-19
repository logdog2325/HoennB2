// SlateportCity_BattleTentBattleRoom (zone 527; Emerald only): the Slateport tent's battles (pokeemerald
// data/maps/SlateportCity_BattleTentBattleRoom/scripts.inc; battle_tents, 2026-10-18, notes/BATTLE_TENTS.md). Reached
// only by script 1 from the corridor. The battle is Black 2's Battle Subway battle with the three rentals against the
// tent trainer's three (frontier_factory_dome.c's Slateport tent mode: everything at level 30, the trainers without AI
// scripts as Emerald's tent). Emerald keeps the camera still with a stand-in player object; here the player walks in
// from the stand-in's spot (4,8). Room origin (1,0).
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_story.inc"
#include "hoenn_emerald.inc"
#include "hoenn_frontier.inc"
#include "scenes/battle_tents_lib.inc"

#define SB_OPP 2                        // the opponent (Emerald LOCALID_SLATEPORT_TENT_BATTLE_OPPONENT)

    ScriptEntry SB_Enter                // 1: OnFrame EnterRoom
    ScriptEntry SB_None                 // 2: the scientist, the opponent
    ScriptEntriesEnd

SB_None:
    VMHalt

SB_Enter:
    ActorsPauseAll
    fd_player_visible
    FrontierCmd FC_B_PREP, TT_FC_SLATEPORT, 0, FD_T1    // the tent trainer; factory_setopponentgfx
    WorkSet FD_OPP_GFX, FD_T1
    FadeInBlack
    FadeWait
    h_applymovement TT_PLAYER, SB_MvPlayerIn
    h_waitmovement
    h_addobject SB_OPP, FD_FLAG_OPP
    h_applymovement SB_OPP, SB_MvOpponentIn
    h_waitmovement
    FrontierCmd FC_B_SPEECH, 0, 0, FD_T1                // battletent_getopponentintro
    fd_say FD_T1, SB_OPP
    h_heal
    FrontierCmd FC_B_BATTLE                             // DoSpecialTrainerBattle (SPECIAL_BATTLE_FACTORY)
    FrontierCmd FC_B_RESULT, 0, 0, FD_T1
    h_goto_if_eq FD_T1, 1, L_SB_Won
L_SB_Lost:                              // WarpToLobbyLost
    fd_status FR_ST_LOST
    fd_to_lobby TT_S_LOBBY, TT_LX(6), TT_LZ(6)
L_SB_Won:                               // DefeatedOpponent: the battle number
    WorkSetConst FD_T1, 1
    FrOp FR_OP_ADD | FR_BATTLE_NUM, FD_T1
    h_goto_if_ge FD_T1, 3, L_SB_Three
    h_applymovement SB_OPP, SB_MvOpponentOut
    h_waitmovement
    h_removeobject SB_OPP, FD_FLAG_OPP
    fd_to_room TT_S_CORR, TT_CX(2), TT_CZ(7), 0, 3      // warp MAP_SLATEPORT_CITY_BATTLE_TENT_CORRIDOR (VAR_0x8006 1)
L_SB_Three:                             // WarpToLobbyWon
    fd_status FR_ST_WON
    fd_to_lobby TT_S_LOBBY, TT_LX(6), TT_LZ(6)

    .balign 4, 0
SB_MvPlayerIn:                          // Movement_PlayerEnter (from the stand-in's spot)
    walk_up 3
    walk_in_place_fast_right
    step_end
SB_MvOpponentIn:                        // Movement_OpponentEnter
    walk_down 4
    walk_in_place_fast_left
    step_end
SB_MvOpponentOut:
    walk_up 4
    step_end
