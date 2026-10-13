// BattleFrontier_BattleDomeBattleRoom (zone 417; Emerald only): the match (pokeemerald
// data/maps/BattleFrontier_BattleDomeBattleRoom/scripts.inc; frontier_factory_dome, 2026-10-12). Reached only by script
// 1 from the waiting room. The announcer's lines are Emerald's (by the player's Dome history and the round); the match
// is Black 2's Battle Subway battle with the player's two picks against the two the opponent sends
// (frontier_factory_dome.c). Not here: the crowd's walking and cheering, the confetti, a draw's referee decision (Black
// 2's battle has no draw). Room origin (1,-1). The player walks in (Emerald uses a stand-in object, camera still).
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_story.inc"
#include "hoenn_emerald.inc"
#include "hoenn_frontier.inc"
#include "scenes/frontier_fd_lib.inc"

#define DB_ANN 1                        // the announcer (REPORTER_M)
#define DB_OPP 2                        // the opponent (code 162)

    ScriptEntry DB_Enter                // 1: OnFrame EnterRoom
    ScriptEntry DB_None                 // 2: the people
    ScriptEntriesEnd

DB_None:
    VMHalt

DB_Enter:
    ActorsPauseAll
    fd_player_visible
    FrontierCmd FC_B_PREP, FRONTIER_FACILITY_DOME, 0, FD_T1   // dome_setopponentgfx
    WorkSet FD_OPP_GFX, FD_T1
    h_addobject DB_OPP, FD_FLAG_OPP
    FadeInBlack
    FadeWait
    // AnnouncePlayer: Emerald's four kinds (first try, never won, a broken streak, the champion) x the round, or the
    // lines before Tucker
    h_buffer_player
    FrontierCmd FC_B_SPEECH, 0, 0, FD_T3                  // 0xFFFF: the opponent is Tucker
    fr_get FR_BATTLE_NUM, FD_T2
    h_goto_if_ne FD_T3, 0xFFFF, L_DB_Announce
    FrontierCmd FC_B_BRAIN_GOLD, 0, 0, FD_T1
    h_goto_if_eq FD_T1, 2, L_DB_PreTuckerGold
    fd_say FD_DOMEBATTLEROOM_TUCKER_GLOW, DB_ANN
    VMJump L_DB_Entered
L_DB_PreTuckerGold:
    fd_say FD_DOMEBATTLEROOM_TUCKER_STRETCHED, DB_ANN
    VMJump L_DB_Entered
L_DB_Announce:
    FrontierCmd FC_D_HISTORY, 0, 0, FD_T1
    WorkMul FD_T1, 4
    WorkAdd FD_T1, FD_T2
    WorkAdd FD_T1, FD_DOMEBATTLEROOM_ANNOUNCE_0
    fd_say FD_T1, DB_ANN
L_DB_Entered:
    fd_say FD_DOMEBATTLEROOM_ENTERED, DB_ANN
    h_applymovement FD_PLAYER, DB_MvPlayerIn
    h_waitmovement
    h_goto_if_eq FD_T3, 0xFFFF, L_DB_Tucker
    // BattleOpponent: "<round> match! <player> versus <trainer>!", both step forward, the trainer's greeting
    WorkSet FD_T1, FD_T2
    WorkAdd FD_T1, FD_ROUND_NAMES
    FrontierCmd FC_WORD_LINE, 1, FD_T1
    FrontierCmd FC_B_NAME, 2
    fd_say FD_DOMEBATTLEROOM_VERSUS, DB_ANN
    h_applymovement FD_PLAYER, DB_MvStepRight
    h_applymovement DB_OPP, DB_MvStepLeft
    h_waitmovement
    fd_say FD_T3, DB_OPP
    VMCall Sub_DB_Battle
    h_goto_if_ne FD_T1, 1, L_DB_Lost
    h_buffer_player
    fd_say FD_DOMEBATTLEROOM_PLAYER_WINS, DB_ANN
L_DB_Won:                               // DefeatedOpponent: dome_resolvewinners DOME_PLAYER_WON_MATCH, the next round
    FrontierCmd FC_D_RESULT, 1
    fr_get FR_BATTLE_NUM, FD_T1
    h_goto_if_ge FD_T1, 4, L_DB_Champion
    h_applymovement DB_OPP, DB_MvOpponentOut
    h_waitmovement
    h_removeobject DB_OPP, FD_FLAG_OPP
    fd_to_room FD_D_PRE, 6, 7, 0, 3     // warp MAP_BATTLE_FRONTIER_BATTLE_DOME_PRE_BATTLE_ROOM (VAR_0x8006 1)
L_DB_Champion:                          // WonTourney: the Level 50 / Open Level champion, the streak (tournaments won)
    h_buffer_player
    fr_get FR_LVL_MODE, FD_T1
    h_goto_if_eq FD_T1, FR_LVL_OPEN, L_DB_ChampOpen
    fd_say FD_DOMEBATTLEROOM_CHAMP_50, DB_ANN
    VMJump L_DB_ChampDone
L_DB_ChampOpen:
    fd_say FD_DOMEBATTLEROOM_CHAMP_OPEN, DB_ANN
L_DB_ChampDone:
    fd_streak_win FRONTIER_FACILITY_DOME     // (Emerald: the lobby's IncrementWinStreak)
    fd_status FR_ST_WON
    fd_to_lobby_m FD_D_LOBBY, 6, 9, 18, 9
L_DB_Lost:                              // LostToOpponent: "<trainer> is the winner!", the tournament decided, the lobby
    FrontierCmd FC_B_NAME, 2
    fd_say FD_DOMEBATTLEROOM_TRAINER_WINS, DB_ANN
L_DB_LostEnd:
    FrontierCmd FC_D_RESULT, 0
    fd_status FR_ST_LOST
    fd_to_lobby_m FD_D_LOBBY, 6, 9, 18, 9

L_DB_Tucker:                            // AnnounceTucker, his intro, the final
    FrontierCmd FC_B_BRAIN_GOLD, 0, 0, FD_T1
    h_goto_if_eq FD_T1, 2, L_DB_TuckerGold
    fd_say FD_DOMEBATTLEROOM_TUCKER_MAKE_WAY, DB_ANN
    fd_say FD_DOMEBATTLEROOM_TUCKER_SILVER_INTRO, DB_OPP
    fd_say FD_DOMEBATTLEROOM_TUCKER_STRATEGY, DB_OPP
    VMJump L_DB_TuckerBattle
L_DB_TuckerGold:
    fd_say FD_DOMEBATTLEROOM_TUCKER_LEGEND, DB_ANN
    fd_say FD_DOMEBATTLEROOM_TUCKER_GOLD_INTRO, DB_OPP
    fd_say FD_DOMEBATTLEROOM_TUCKER_UNLEASH, DB_OPP
L_DB_TuckerBattle:
    h_buffer_player
    fd_say FD_DOMEBATTLEROOM_VERSUS_TUCKER, DB_ANN
    VMCall Sub_DB_Battle
    h_goto_if_eq FD_T1, 1, L_DB_TuckerWon
    fd_say FD_DOMEBATTLEROOM_WINNER_TUCKER, DB_ANN
    VMJump L_DB_LostEnd
L_DB_TuckerWon:
    h_buffer_player
    fd_say FD_DOMEBATTLEROOM_VICTOR_PLAYER, DB_ANN
    fr_symbol_get FRONTIER_FACILITY_DOME, FD_T2
    FrontierCmd FC_B_BRAIN_GOLD, 0, 0, FD_T1
    h_goto_if_eq FD_T1, 2, L_DB_TuckerGoldWon
    h_goto_if_ne FD_T2, 0, L_DB_TuckerDone
    fd_say FD_DOMEBATTLEROOM_TUCKER_PASS, DB_OPP
    MEPlay FR_ME_OBTAIN_SYMBOL          // mus_obtain_symbol (notes/FRONTIER.md 5)
    h_msgbox_info FD_DOMEBATTLEROOM_GOT_SILVER
    MEWait
    MsgWinCloseAll
    fr_symbol_give FRONTIER_FACILITY_DOME, 0
    fd_say FD_DOMEBATTLEROOM_TUCKER_NEXT, DB_OPP
    VMJump L_DB_TuckerDone
L_DB_TuckerGoldWon:
    h_goto_if_eq FD_T2, 2, L_DB_TuckerDone
    fd_say FD_DOMEBATTLEROOM_TUCKER_PASS, DB_OPP
    MEPlay FR_ME_OBTAIN_SYMBOL
    h_msgbox_info FD_DOMEBATTLEROOM_GOT_GOLD
    MEWait
    MsgWinCloseAll
    fr_symbol_give FRONTIER_FACILITY_DOME, 1
    fd_say FD_DOMEBATTLEROOM_TUCKER_NEVER_LOST, DB_OPP
L_DB_TuckerDone:
    fr_set FR_BRAIN_BEATEN, 1
    VMJump L_DB_Won

Sub_DB_Battle:                          // DoDomeBattle: FD_T1 = 1 won
    h_heal
    FrontierCmd FC_B_BATTLE
    FrontierCmd FC_B_RESULT, 0, 0, FD_T1
    h_heal
    VMReturn

    .balign 4, 0
DB_MvPlayerIn:                          // Movement_PlayerEnter (up 3, right 1) + PlayerStepForward (right 1) for Tucker
    walk_up 3
    walk_right
    face_right
    step_end
DB_MvStepRight:                         // Movement_PlayerStepForward
    walk_right
    step_end
DB_MvStepLeft:                          // Movement_OpponentStepForward
    walk_left
    face_left
    step_end
DB_MvOpponentOut:
    walk_right 2
    step_end
