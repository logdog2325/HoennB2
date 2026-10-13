// BattleFrontier_BattleFactoryBattleRoom (zone 410; Emerald only): the battle (pokeemerald
// data/maps/BattleFrontier_BattleFactoryBattleRoom/scripts.inc; frontier_factory_dome, 2026-10-12). Reached only by
// script 1 from the pre-battle room. The battle is Black 2's Battle Subway battle with the rental party and the
// opponent's Emerald sets (frontier_factory_dome.c FR_BuildSetup). Room origin (1,0). Emerald keeps the camera still
// with a stand-in player object; here the player walks in (the camera follows). The opponent's in-battle win/lose
// words (Emerald's easy-chat speeches) are not shown: Black 2's Subway battle has no such text for these trainers.
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_story.inc"
#include "hoenn_emerald.inc"
#include "hoenn_frontier.inc"
#include "scenes/frontier_fd_lib.inc"

#define BR_OPP 1                        // the opponent (Emerald LOCALID_FACTORY_BATTLE_OPPONENT)

    ScriptEntry BR_Enter                // 1: OnFrame EnterRoom
    ScriptEntry BR_None                 // 2: the scientists and the opponent
    ScriptEntriesEnd

BR_None:
    VMHalt

BR_Enter:
    ActorsPauseAll
    fd_player_visible
    FrontierCmd FC_B_PREP, FRONTIER_FACILITY_FACTORY, 0, FD_T1   // the trainer and its sets; factory_setopponentgfx
    WorkSet FD_OPP_GFX, FD_T1
    FadeInBlack
    FadeWait
    h_applymovement FD_PLAYER, BR_MvPlayerIn
    h_waitmovement
    FrontierCmd FC_BRAIN_STATUS, FRONTIER_FACILITY_FACTORY, 0, FD_T3
    h_goto_if_eq FD_T3, 0, L_BR_Opponent
    h_msgbox_info FD_FACTORYBATTLEROOM_GET_MOVE_ON    // (Noland, from behind the door: no speaker yet)
    MsgWinCloseAll
L_BR_Opponent:
    h_addobject BR_OPP, FD_FLAG_OPP
    h_applymovement BR_OPP, BR_MvOpponentIn
    h_waitmovement
    h_goto_if_ne FD_T3, 0, L_BR_Noland
    FrontierCmd FC_B_SPEECH, 0, 0, FD_T1                      // palace_getopponentintro: the trainer's greeting
    fd_say FD_T1, BR_OPP
L_BR_Battle:
    h_heal
    FrontierCmd FC_B_BATTLE
    FrontierCmd FC_B_RESULT, 0, 0, FD_T1
    h_goto_if_eq FD_T1, 1, L_BR_Won
L_BR_Lost:                              // WarpToLobbyLost (in front of the attendant of the challenge's mode)
    fd_status FR_ST_LOST
    fd_to_lobby_m FD_F_LOBBY, 5, 6, 15, 6
L_BR_Won:                               // DefeatedOpponent: the rents count, the streak, the battle number
    FrontierCmd FC_F_WON
    fd_streak_win FRONTIER_FACILITY_FACTORY
    WorkSetConst FD_T1, 1
    FrOp FR_OP_ADD | FR_BATTLE_NUM, FD_T1
    h_goto_if_ge FD_T1, 7, L_BR_Seven
    h_applymovement BR_OPP, BR_MvOpponentOut
    h_waitmovement
    h_removeobject BR_OPP, FD_FLAG_OPP
    fd_to_room FD_F_PRE, 9, 10, 0, 3    // warp MAP_BATTLE_FRONTIER_BATTLE_FACTORY_PRE_BATTLE_ROOM (VAR_0x8006 1)
L_BR_Seven:                             // WarpToLobbyWon
    fd_status FR_ST_WON
    fd_to_lobby_m FD_F_LOBBY, 5, 6, 15, 6

L_BR_Noland:                            // BattleNoland: silver (the 21st battle) or gold (the 42nd)
    h_goto_if_eq FD_T3, 2, L_BR_NolandGold
    h_goto_if_eq FD_T3, 4, L_BR_NolandGold
    fd_say FD_FACTORYBATTLEROOM_NOLAND_HEAD, BR_OPP
    fd_say FD_FACTORYBATTLEROOM_NOLAND_SILVER, BR_OPP
    VMCall Sub_BR_NolandBattle
    fr_symbol_get FRONTIER_FACILITY_FACTORY, FD_T2
    h_goto_if_ne FD_T2, 0, L_BR_NolandDone
    fd_say FD_FACTORYBATTLEROOM_NOLAND_PASS, BR_OPP
    MEPlay FR_ME_OBTAIN_SYMBOL          // mus_obtain_symbol (notes/FRONTIER.md 5)
    h_buffer_player
    h_msgbox_info FD_FACTORYBATTLEROOM_GOT_SILVER
    MEWait
    MsgWinCloseAll
    fr_symbol_give FRONTIER_FACILITY_FACTORY, 0
    fd_say FD_FACTORYBATTLEROOM_NOLAND_NEXT, BR_OPP
    VMJump L_BR_NolandDone
L_BR_NolandGold:
    fd_say FD_FACTORYBATTLEROOM_NOLAND_HARDER, BR_OPP
    fd_say FD_FACTORYBATTLEROOM_NOLAND_GOLD, BR_OPP
    VMCall Sub_BR_NolandBattle
    fr_symbol_get FRONTIER_FACILITY_FACTORY, FD_T2
    h_goto_if_eq FD_T2, 2, L_BR_NolandDone
    fd_say FD_FACTORYBATTLEROOM_NOLAND_PASS2, BR_OPP
    MEPlay FR_ME_OBTAIN_SYMBOL
    h_buffer_player
    h_msgbox_info FD_FACTORYBATTLEROOM_GOT_GOLD
    MEWait
    MsgWinCloseAll
    fr_symbol_give FRONTIER_FACILITY_FACTORY, 1
    fd_say FD_FACTORYBATTLEROOM_NOLAND_LAST, BR_OPP
L_BR_NolandDone:                        // DefeatedNoland: the rents count, the streak, then the lobby (won)
    fr_set FR_BRAIN_BEATEN, 1
    FrontierCmd FC_F_WON
    fr_streak_win FRONTIER_FACILITY_FACTORY, FRONTIER_MODE_SINGLES     // (Noland: singles only)
    WorkSetConst FD_T1, 1
    FrOp FR_OP_ADD | FR_BATTLE_NUM, FD_T1
    VMJump L_BR_Seven

Sub_BR_NolandBattle:                    // DoNolandBattle (lost: back to the lobby)
    h_heal
    FrontierCmd FC_B_BATTLE
    FrontierCmd FC_B_RESULT, 0, 0, FD_T1
    h_goto_if_ne FD_T1, 1, L_BR_Lost
    VMReturn

    .balign 4, 0
BR_MvPlayerIn:                          // Movement_PlayerEnterRoom
    walk_up 5
    face_right
    step_end
BR_MvOpponentIn:                        // Movement_OpponentEnter (from the back door)
    walk_down 4
    face_left
    step_end
BR_MvOpponentOut:
    walk_up 4
    step_end
