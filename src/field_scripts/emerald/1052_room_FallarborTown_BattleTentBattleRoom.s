// FallarborTown_BattleTentBattleRoom (zone 526; Emerald only): the Fallarbor tent's Set KO Tourney battles (pokeemerald
// data/maps/FallarborTown_BattleTentBattleRoom/scripts.inc; battle_tents, 2026-10-18, notes/BATTLE_TENTS.md). Reached
// only by script 1 from the corridor. Each battle is the Battle Arena's (one Pokémon each at a time in party order, no
// switching, the referee's judgment after three turns: frontier_palace_arena.c) against one of the tent's 30 trainers
// (never one twice in a challenge), its three at the level of the player's highest of the three (at least 30); three wins
// in a row win the tent. The referee's drum / snore / bang sounds are left out (as the Frontier Arena's). Emerald keeps
// the camera still with a stand-in player object; here the player walks in from the stand-in's spot (4,8). Origin (1,0).
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_story.inc"
#include "hoenn_emerald.inc"
#include "hoenn_frontier.inc"
#include "scenes/battle_tents_lib.inc"

#define FB_ATT 2                        // the referee (Emerald LOCALID_FALLARBOR_TENT_BATTLE_ATTENDANT, BLACK_BELT)
#define FB_OPP 3                        // the opponent

    ScriptEntry FB_Enter                // 1: OnFrame EnterRoom
    ScriptEntry FB_None                 // 2: the referee, the opponent
    ScriptEntriesEnd

FB_None:
    VMHalt

FB_Enter:
    ActorsPauseAll
    fd_player_visible
    FadeInBlack
    FadeWait
    h_applymovement TT_PLAYER, FB_MvPlayerIn
    h_waitmovement
    fr_get FR_BATTLE_NUM, FD_T1
    h_goto_if_ne FD_T1, 0, L_FB_Ask     // (a resumed challenge)
L_FB_Next:                              // NextOpponentEnter
    FrontierPA PA_NEXT_OPPONENT, TT_PA_FALLARBOR, 0, FD_T1
    WorkSet PA_OPP_GFX, FD_T1
    h_addobject FB_OPP, PA_FLAG_OPP
    h_applymovement FB_OPP, FB_MvOpponentIn
    h_waitmovement
    h_applymovement FB_ATT, FB_MvJump
    h_waitmovement
    fd_say BT_F_BATTLEROOM_BEGIN, FB_ATT                        // "Set KO Tourney! Begin!"
    FrontierPA PA_GREETING, TT_PA_FALLARBOR, 0, FD_T1
    fd_say FD_T1, FB_OPP
    h_heal                              // DoArenaBattle
    FrontierPA PA_BATTLE, TT_PA_FALLARBOR, 0, FD_T1
    h_heal
    h_goto_if_eq FD_T1, 1, L_FB_Won
    h_applymovement FB_ATT, FB_MvJump
    h_waitmovement
    FrontierPA PA_NAME, TT_PA_FALLARBOR, 1                      // fallarbortent_getopponentname
    fd_say BT_F_BATTLEROOM_WINNER_OPPONENT, FB_ATT
L_FB_Lost:                              // WarpToLobbyLost
    fd_status FR_ST_LOST
    tt_to_lobby TT_F_LOBBY              // warp MAP_FALLARBOR_TOWN_BATTLE_TENT_LOBBY, 6, 6
L_FB_Won:                               // DefeatedOpponent
    h_applymovement FB_ATT, FB_MvJump
    h_waitmovement
    h_buffer_player
    fd_say BT_F_BATTLEROOM_WINNER_PLAYER, FB_ATT
    WorkSetConst FD_T1, 1                                       // IncrementBattleNum
    FrOp FR_OP_ADD | FR_BATTLE_NUM, FD_T1
    h_goto_if_ge FD_T1, 3, L_FB_Three
    h_applymovement FB_OPP, FB_MvOpponentOut
    h_waitmovement
    h_removeobject FB_OPP, PA_FLAG_OPP
    h_applymovement FB_ATT, FB_MvApproach
    h_waitmovement
    h_applymovement TT_PLAYER, FB_MvFaceLeft
    h_waitmovement
    ActorMsg MSGFILE_SCRIPT, BT_F_BATTLEROOM_RESTORE, FB_ATT, 0, 0
    LastKeyWait
    MEPlay MUS_HEAL
    MEWait
    MsgWinCloseAll
    h_heal
    VMJump L_FB_AskNear
L_FB_Ask:                               // (resumed: the referee comes to the player first)
    h_applymovement FB_ATT, FB_MvApproach
    h_waitmovement
    h_applymovement TT_PLAYER, FB_MvFaceLeft
    h_waitmovement
L_FB_AskNear:                           // AskContinueChallenge: "your second / third opponent!"
    fr_get FR_BATTLE_NUM, FD_T1
    WorkAdd FD_T1, BT_F_BATTLEROOM_READY_2 - 1
    ActorMsg MSGFILE_SCRIPT, FD_T1, FB_ATT, 0, 0
    fd_menu3 FD_T2, BT_F_BATTLEROOM_MENU_GO_ON, BT_F_BATTLEROOM_MENU_REST, BT_F_BATTLEROOM_MENU_RETIRE
    MsgWinCloseAll
    h_goto_if_eq FD_T2, 0, L_FB_GoOn
    h_goto_if_eq FD_T2, 1, L_FB_Rest
    h_goto_if_eq FD_T2, 2, L_FB_Retire
    VMJump L_FB_AskNear
L_FB_GoOn:                              // ContinueChallenge: the referee back to his place, the player faces the battle
    h_applymovement FB_ATT, FB_MvReturn
    h_waitmovement
    h_applymovement TT_PLAYER, FB_MvFaceRight
    h_waitmovement
    VMJump L_FB_Next
L_FB_Rest:                              // AskPauseChallenge -> PauseChallenge
    h_yesno_actor BT_F_BATTLEROOM_SAVE_QUIT, FB_ATT, FD_T1
    h_goto_if_no FD_T1, L_FB_AskNear
    FlagSet PA_FLAG_OPP
    fr_rest_and_quit TT_F_LOBBY, TT_LX(6), TT_LZ(6), 0, BT_F_BATTLEROOM_SAVING, FB_ATT
L_FB_Retire:                            // AskRetireChallenge
    h_yesno_actor BT_F_BATTLEROOM_RETIRE, FB_ATT, FD_T1
    h_goto_if_no FD_T1, L_FB_AskNear
    VMJump L_FB_Lost
L_FB_Three:                             // WarpToLobbyWon
    h_delay 60
    fd_status FR_ST_WON
    tt_to_lobby TT_F_LOBBY

    .balign 4, 0
FB_MvPlayerIn:                          // Movement_PlayerEnter (from the stand-in's spot)
    walk_up 3
    walk_in_place_fast_right
    step_end
FB_MvFaceRight:                         // Movement_PlayerFaceBattle
    walk_in_place_fast_right
    step_end
FB_MvFaceLeft:                          // Movement_PlayerFaceAttendant
    walk_in_place_fast_left
    step_end
FB_MvOpponentIn:                        // Movement_OpponentEnter
    walk_down 4
    walk_in_place_fast_left
    step_end
FB_MvOpponentOut:                       // Movement_OpponentExit
    walk_up 4
    step_end
FB_MvJump:                              // Movement_AttendantJump
    jump_in_place_down
    step_end
FB_MvApproach:                          // Movement_AttendantApproachPlayer
    walk_down 3
    walk_in_place_fast_right
    step_end
FB_MvReturn:                            // Movement_AttendantReturnToPos
    walk_up 3
    walk_in_place_fast_down
    step_end
