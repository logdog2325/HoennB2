// BattleFrontier_BattleArenaBattleRoom (zone 433; Emerald only): the dojo (pokeemerald
// data/maps/BattleFrontier_BattleArenaBattleRoom/scripts.inc; frontier_palace_arena, 2026-10-12). Reached only by
// script 1 from the corridor. The battle is Black 2's Battle Subway battle with the Arena's rules
// (b2tools/patches/frontier_palace_arena.c: 1-vs-1 matchups, three turns, the referee's judgment, no switching).
// Room origin (1,-1). Emerald keeps the camera still with a stand-in player object; here the player walks in from the
// stand-in's spot (0,6) (the camera follows). The announcer (object 9) and the four black belts jump as in Emerald
// (Emerald's drum / snore sounds are left out: Black 2 has no such field sounds).
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_story.inc"
#include "hoenn_emerald.inc"
#include "hoenn_frontier.inc"
#include "scenes/frontier_pa_lib.inc"

#define AB_OPP 7                        // the opponent (Emerald LOCALID_ARENA_BATTLE_OPPONENT)
#define AB_ATT 5                        // the attendant
#define AB_ANN 9                        // the announcer

    ScriptEntry AB_Enter                // 1: OnFrame EnterRoom
    ScriptEntry AB_None                 // 2: everybody else
    ScriptEntriesEnd

AB_None:
    VMHalt

    .macro ab_announce line             // the announcer jumps and calls out a line
    h_applymovement AB_ANN, AB_MvJumpDown
    h_waitmovement
    ActorMsg MSGFILE_SCRIPT, \line, AB_ANN, 0, 0
    LastKeyWait
    MsgWinCloseAll
    .endm

AB_Enter:
    ActorsPauseAll
    fd_player_visible
    FadeInBlack
    FadeWait
    h_applymovement PA_PLAYER, AB_MvPlayerIn
    h_waitmovement
    fr_get FR_BATTLE_NUM, FD_T1
    h_goto_if_eq FD_T1, 0, L_AB_Announce
    h_applymovement AB_ATT, AB_MvWalkInPlaceDown       // (a resumed challenge)
    h_applymovement PA_PLAYER, AB_MvFaceUp
    h_waitmovement
    VMJump L_AB_Ask

L_AB_Announce:                          // AnnounceTrainers
    FrontierPA PA_NEXT_OPPONENT, FRONTIER_FACILITY_ARENA, 0, FD_T1
    WorkSet PA_OPP_GFX, FD_T1
    h_addobject AB_OPP, PA_FLAG_OPP
    h_applymovement AB_OPP, AB_MvOpponentIn
    h_waitmovement
    h_buffer_player
    ab_announce PA_ARENABATTLEROOM_PLAYER_STEP
    h_applymovement PA_PLAYER, AB_MvStepRight
    h_waitmovement
    FrontierPA PA_NAME, FRONTIER_FACILITY_ARENA, 1
    ab_announce PA_ARENABATTLEROOM_OPPONENT_STEP
    h_applymovement AB_OPP, AB_MvStepLeft
    h_waitmovement
    ab_announce PA_ARENABATTLEROOM_BEGIN
    h_applymovement PA_PLAYER, AB_MvStepRight
    h_applymovement AB_OPP, AB_MvStepLeft
    h_waitmovement
    FrontierPA PA_GREETING, FRONTIER_FACILITY_ARENA, 0, FD_T1
    fd_say FD_T1, AB_OPP
    VMCall Sub_AB_Battle
    h_goto_if_eq FD_T1, 1, L_AB_Won
L_AB_OpponentWins:                      // DeclareOpponentWinner
    VMCall Sub_AB_Cheer
    FrontierPA PA_NAME, FRONTIER_FACILITY_ARENA, 1
    h_msgbox_actor PA_ARENABATTLEROOM_WINNER_OPPONENT, AB_ANN
    h_closemessage
L_AB_Lost:                              // WarpToLobbyLost
    fd_status FR_ST_LOST
    pa_to_lobby PA_A_LOBBY, 8, 7        // warp MAP_BATTLE_FRONTIER_BATTLE_ARENA_LOBBY, 7, 8

L_AB_Won:                               // DefeatedOpponent: DeclarePlayerWinner, the battle number
    VMCall Sub_AB_PlayerWins
    WorkSetConst FD_T1, 1
    FrOp FR_OP_ADD | FR_BATTLE_NUM, FD_T1
    h_goto_if_ge FD_T1, 7, L_AB_Seven
    h_applymovement PA_PLAYER, AB_MvPlayerBack
    h_applymovement AB_OPP, AB_MvOpponentOut
    h_waitmovement
    h_removeobject AB_OPP, PA_FLAG_OPP
    h_applymovement AB_ATT, AB_MvWalkInPlaceDown
    h_applymovement PA_PLAYER, AB_MvFaceUp
    h_waitmovement
    ActorMsg MSGFILE_SCRIPT, PA_ARENABATTLEROOM_RESTORE, AB_ATT, 0, 0
    LastKeyWait
    MEPlay MUS_HEAL
    MEWait
    MsgWinCloseAll
    h_heal
L_AB_Ask:                               // AskReadyForOpponent
    FrontierPA PA_BRAIN_STATUS, FRONTIER_FACILITY_ARENA, 0, FD_T3
    h_goto_if_ne FD_T3, 0, L_AB_TycoonNext
    fr_get FR_BATTLE_NUM, FD_T1
    WorkAdd FD_T1, PA_ARENABATTLEROOM_READY_2 - 1
    ActorMsg MSGFILE_SCRIPT, FD_T1, AB_ATT, 0, 0
L_AB_Menu:
    fd_menu3 FD_T2, PA_ARENABATTLEROOM_MENU_GO_ON, PA_ARENABATTLEROOM_MENU_REST, PA_ARENABATTLEROOM_MENU_RETIRE
    MsgWinCloseAll
    h_goto_if_eq FD_T2, 0, L_AB_GoOn
    h_goto_if_eq FD_T2, 1, L_AB_Rest
    h_goto_if_eq FD_T2, 2, L_AB_Retire
    VMJump L_AB_Ask
L_AB_GoOn:                              // ContinueChallenge
    h_applymovement PA_PLAYER, AB_MvFaceRight
    h_applymovement AB_ATT, AB_MvFaceRight
    h_waitmovement
    h_goto_if_ne FD_T3, 0, L_AB_Greta
    VMJump L_AB_Announce
L_AB_Rest:                              // AskPauseChallenge -> PauseChallenge
    h_yesno_actor PA_ARENABATTLEROOM_SAVE_QUIT, AB_ATT, FD_T1
    h_goto_if_no FD_T1, L_AB_Ask
    FlagSet PA_FLAG_OPP
    fr_rest_and_quit PA_A_LOBBY, 8, 7, 0, PA_ARENABATTLEROOM_SAVING, AB_ATT
L_AB_Retire:                            // AskRetireChallenge
    h_yesno_actor PA_ARENABATTLEROOM_RETIRE, AB_ATT, FD_T1
    h_goto_if_no FD_T1, L_AB_Ask
    VMJump L_AB_Lost
L_AB_Seven:                             // ReturnToLobbyWon
    h_delay 60
    fd_status FR_ST_WON
    pa_to_lobby PA_A_LOBBY, 8, 7

L_AB_TycoonNext:                        // TycoonUpNext: "the Arena Tycoon", then ready?
    h_msgbox_actor PA_ARENABATTLEROOM_TYCOON_NEXT, AB_ATT
    ActorMsg MSGFILE_SCRIPT, PA_ARENABATTLEROOM_TYCOON_READY, AB_ATT, 0, 0
    VMJump L_AB_Menu

L_AB_Greta:                             // BattleGreta
    FrontierPA PA_NEXT_OPPONENT, FRONTIER_FACILITY_ARENA, 0, FD_T1     // (the Brain: Greta's walking sprite)
    WorkSet PA_OPP_GFX, FD_T1
    h_buffer_player
    ab_announce PA_ARENABATTLEROOM_PLAYER_STEP
    h_applymovement PA_PLAYER, AB_MvStepRightLong
    h_waitmovement
    ab_announce PA_ARENABATTLEROOM_MAKE_WAY
    h_addobject AB_OPP, PA_FLAG_OPP
    h_applymovement AB_OPP, AB_MvGretaIn
    h_waitmovement
    h_applymovement AB_OPP, AB_MvStepLeft
    h_waitmovement
    h_goto_if_eq FD_T3, 2, L_AB_IntroGold
    h_goto_if_eq FD_T3, 3, L_AB_Silver
    h_goto_if_eq FD_T3, 4, L_AB_Gold
    FrontierPA PA_HEARD, FRONTIER_FACILITY_ARENA, 1, FD_T1
    h_goto_if_ne FD_T1, 0, L_AB_Silver
    h_buffer_player
    fd_say PA_ARENABATTLEROOM_GRETA_INTRO, AB_OPP
    h_applymovement AB_OPP, AB_MvGretaLookAround
    h_waitmovement
    fd_say PA_ARENABATTLEROOM_GRETA_RIGHT, AB_OPP
    h_applymovement AB_OPP, AB_MvGretaBack
    h_waitmovement
    fd_say PA_ARENABATTLEROOM_GRETA_WEAK, AB_OPP
L_AB_Silver:
    fd_say PA_ARENABATTLEROOM_GRETA_IGNITE, AB_OPP
    VMCall Sub_AB_BrainBattle
    fr_symbol_get FRONTIER_FACILITY_ARENA, FD_T2
    h_goto_if_ne FD_T2, 0, L_AB_BrainDone
    h_applymovement AB_OPP, AB_MvStepLeftLong
    h_waitmovement
    fd_say PA_ARENABATTLEROOM_GRETA_POST_SILVER, AB_OPP
    MEPlay FR_ME_OBTAIN_SYMBOL
    h_buffer_player
    h_msgbox_info PA_ARENABATTLEROOM_GOT_SILVER
    MEWait
    MsgWinCloseAll
    fr_symbol_give FRONTIER_FACILITY_ARENA, 0
    fd_say PA_ARENABATTLEROOM_GRETA_NEXT, AB_OPP
    VMJump L_AB_BrainDone
L_AB_IntroGold:
    FrontierPA PA_HEARD, FRONTIER_FACILITY_ARENA, 1, FD_T1
    h_goto_if_ne FD_T1, 0, L_AB_Gold
    fd_say PA_ARENABATTLEROOM_GRETA_GOLD_INTRO, AB_OPP
    h_applymovement AB_OPP, AB_MvGretaLookAround
    h_waitmovement
    fd_say PA_ARENABATTLEROOM_GRETA_READY, AB_OPP
    h_applymovement AB_OPP, AB_MvGretaBack
    h_waitmovement
    fd_say PA_ARENABATTLEROOM_GRETA_HALFHEARTED, AB_OPP
L_AB_Gold:
    fd_say PA_ARENABATTLEROOM_GRETA_START, AB_OPP
    VMCall Sub_AB_BrainBattle
    fr_symbol_get FRONTIER_FACILITY_ARENA, FD_T2
    h_goto_if_eq FD_T2, 2, L_AB_BrainDone
    h_applymovement AB_OPP, AB_MvStepLeftLong
    h_waitmovement
    fd_say PA_ARENABATTLEROOM_GRETA_POST_GOLD, AB_OPP
    MEPlay FR_ME_OBTAIN_SYMBOL
    h_buffer_player
    h_msgbox_info PA_ARENABATTLEROOM_GOT_GOLD
    MEWait
    MsgWinCloseAll
    fr_symbol_give FRONTIER_FACILITY_ARENA, 1
    fd_say PA_ARENABATTLEROOM_GRETA_LAST, AB_OPP
L_AB_BrainDone:                         // (the streak was counted by DeclarePlayerWinner)
    fr_set FR_BRAIN_BEATEN, 1
    WorkSetConst FD_T1, 1
    FrOp FR_OP_ADD | FR_BATTLE_NUM, FD_T1
    VMJump L_AB_Seven

Sub_AB_Battle:                          // DoArenaBattle: healed, the battle; FD_T1 = 1 won
    h_heal
    FrontierPA PA_BATTLE, FRONTIER_FACILITY_ARENA, 0, FD_T1
    h_heal
    VMReturn
Sub_AB_BrainBattle:                     // StartArenaBattle (lost: DeclareOpponentWinner)
    ab_announce PA_ARENABATTLEROOM_BEGIN
    VMCall Sub_AB_Battle
    h_goto_if_ne FD_T1, 1, L_AB_OpponentWins
    VMCall Sub_AB_PlayerWins
    VMReturn
Sub_AB_Cheer:                           // the announcer and the four black belts jump
    h_applymovement AB_ANN, AB_MvJumpDown
    h_applymovement 1, AB_MvJumpDown
    h_applymovement 2, AB_MvJumpDown
    h_applymovement 3, AB_MvJumpUp
    h_applymovement 4, AB_MvJumpUp
    h_waitmovement
    VMReturn
Sub_AB_PlayerWins:                      // DeclarePlayerWinner (+ IncrementWinStreak)
    VMCall Sub_AB_Cheer
    h_buffer_player
    h_msgbox_actor PA_ARENABATTLEROOM_WINNER_PLAYER, AB_ANN
    h_closemessage
    fr_streak_win FRONTIER_FACILITY_ARENA, FRONTIER_MODE_SINGLES
    VMReturn

    .balign 4, 0
AB_MvPlayerIn:                          // Movement_PlayerEnter (from the stand-in's spot)
    walk_right 4
    step_end
AB_MvStepRightLong:                     // Movement_PlayerStepForwardLong
    walk_right
AB_MvStepRight:                         // Movement_PlayerStepForward
    walk_right
    step_end
AB_MvPlayerBack:                        // Movement_PlayerWalkBackToLine
    walk_left 2
    walk_in_place_fastest_right
    step_end
AB_MvFaceUp:                            // Movement_WalkInPlaceLeft (Emerald: in place, up)
    walk_in_place_fastest_up
    step_end
AB_MvFaceRight:                         // Movement_WalkInPlaceRight
    walk_in_place_fastest_right
    step_end
AB_MvWalkInPlaceDown:
    walk_in_place_fastest_down
    step_end
AB_MvOpponentIn:                        // Movement_OpponentEnter
    walk_left 4
    step_end
AB_MvStepLeftLong:                      // Movement_OpponentStepForwardLong
    walk_left
AB_MvStepLeft:                          // Movement_OpponentStepForward
    walk_left
    step_end
AB_MvGretaIn:                           // Movement_GretaEnter
    walk_fast_left 5
    step_end
AB_MvOpponentOut:                       // Movement_OpponentExit
    walk_right 7
    step_end
AB_MvJumpDown:
    jump_in_place_down
    step_end
AB_MvJumpUp:
    jump_in_place_up
    step_end
AB_MvGretaLookAround:                   // Movement_GretaLookAroundPlayer
    walk_down
    walk_in_place_fastest_left
    delay_16 4
    walk_up 2
    walk_in_place_fastest_left
    step_end
AB_MvGretaBack:                         // Movement_GretaWalkBackToCenter
    walk_down
    walk_in_place_fastest_left
    step_end
