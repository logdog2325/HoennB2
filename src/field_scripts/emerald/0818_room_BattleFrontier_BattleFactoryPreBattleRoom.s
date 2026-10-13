// BattleFrontier_BattleFactoryPreBattleRoom (zone 409; Emerald only): the rental room (pokeemerald
// data/maps/BattleFrontier_BattleFactoryPreBattleRoom/scripts.inc; frontier_factory_dome, 2026-10-12). Reached only by
// script: 1 from the lobby (a new challenge), 3 back from a won battle, 4 a resumed challenge. The rentals, the
// opponent and the swap are frontier_factory_dome.c's (FrontierCmd); the screens are Black 2's battle-entry party
// screen. Room origin (1,-3): Emerald (x, y) = zone (x + 1, y - 3). Every arrival walks in from the mat (8,13) with the
// attendant (Emerald puts the player at (8,8) on the way back from a battle: here the same walk as the first time).
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_story.inc"
#include "hoenn_emerald.inc"
#include "hoenn_frontier.inc"
#include "scenes/frontier_fd_lib.inc"

    ScriptEntry PB_First                // 1: EnterRoom (VAR_0x8006 0): rentals, the first opponent, the rental screen
    ScriptEntry PB_None                 // 2: the attendant (no talk script in Emerald)
    ScriptEntry PB_Return               // 3: ReturnToRoomFromBattle
    ScriptEntry PB_Resume               // 4: ResumeChallenge (VAR_0x8006 2)
    ScriptEntriesEnd

PB_None:
    VMHalt

    .macro pb_walk_in
    ActorsPauseAll
    fd_player_visible
    FadeInBlack
    FadeWait
    h_applymovement 1, PB_MvAttendantIn
    h_applymovement FD_PLAYER, PB_MvPlayerIn
    h_waitmovement
    .endm

PB_First:
    pb_walk_in
    FrontierCmd FC_F_GEN_RENTALS        // factory_generaterentalmons
    VMCall Sub_PB_Opponent              // factory_generateopponentmons + the two comments
    fd_say FD_FACTORYPREBATTLEROOM_HOLD_CHOOSE, 1
    FrontierCmd FC_F_RENT, 0, 0, FD_T1  // factory_rentmons (three of the six; the screen cannot be left without them)
L_PB_ToRoom:                            // EnterBattleRoom
    fd_say FD_FACTORYPREBATTLEROOM_THIS_WAY, 1
    fr_get FR_LVL_MODE, FD_T1
    h_goto_if_eq FD_T1, FR_LVL_OPEN, L_PB_ToOpen
    bt_door_open 7, 1                   // the Lv. 50 room's door (Emerald (6,5))
    h_applymovement FD_PLAYER, PB_MvTo50
    h_waitmovement
    fd_to_room FD_F_ROOM, 6, 11, 0, 1, 1    // warp MAP_BATTLE_FRONTIER_BATTLE_FACTORY_BATTLE_ROOM, 6, 11
L_PB_ToOpen:
    bt_door_open 11, 1                  // the Open Level room's door (Emerald (10,5))
    h_applymovement FD_PLAYER, PB_MvToOpen
    h_waitmovement
    fd_to_room FD_F_ROOM, 6, 11, 0, 1, 1

PB_Return:
    pb_walk_in
    FrontierCmd FC_F_KEEP_OPPONENT      // factory_setopponentmons: the defeated three can be swapped in
    ActorMsg MSGFILE_SCRIPT, FD_FACTORYPREBATTLEROOM_RESTORE, 1, 0, 0
    LastKeyWait
    MEPlay MUS_HEAL
    MEWait
    MsgWinCloseAll
    h_heal
    FrontierCmd FC_BRAIN_STATUS, FRONTIER_FACILITY_FACTORY, 0, FD_T1
    h_goto_if_eq FD_T1, 0, L_PB_Ask
    SEPlay SEQ_SE_MESSAGE               // (Emerald: SE_POKENAV_CALL) the Factory Head calls
    fd_say FD_FACTORYPREBATTLEROOM_WAIT_MOMENTS, 1
    h_applymovement 1, PB_MvAttendantCall
    h_waitmovement
    fd_say FD_FACTORYPREBATTLEROOM_UNDERSTOOD, 1
    h_applymovement 1, PB_MvAttendantBack
    h_waitmovement
    fd_say FD_FACTORYPREBATTLEROOM_HEAD_COME, 1
    VMJump L_PB_Ask

PB_Resume:
    pb_walk_in
L_PB_Ask:                               // AskReadyForOpponent: "ready for the Nth opponent?" GO ON / REST / RETIRE
    FrontierCmd FC_BRAIN_STATUS, FRONTIER_FACILITY_FACTORY, 0, FD_T1
    h_goto_if_eq FD_T1, 0, L_PB_AskRegular
    ActorMsg MSGFILE_SCRIPT, FD_FACTORYPREBATTLEROOM_PREPARED_HEAD, 1, 0, 0
    VMJump L_PB_Menu
L_PB_AskRegular:
    fr_get FR_BATTLE_NUM, FD_T1
    WorkAdd FD_T1, FD_FACTORYPREBATTLEROOM_READY_2 - 1
    ActorMsg MSGFILE_SCRIPT, FD_T1, 1, 0, 0
L_PB_Menu:
    fd_menu3 FD_T2, FD_FACTORYPREBATTLEROOM_MENU_GO_ON, FD_FACTORYPREBATTLEROOM_MENU_REST, FD_FACTORYPREBATTLEROOM_MENU_RETIRE
    MsgWinCloseAll
    h_goto_if_eq FD_T2, 0, L_PB_GoOn
    h_goto_if_eq FD_T2, 1, L_PB_Rest
    h_goto_if_eq FD_T2, 2, L_PB_Retire
    VMJump L_PB_Ask
L_PB_GoOn:                              // AskSwapMon
    VMCall Sub_PB_Opponent
    h_yesno_actor FD_FACTORYPREBATTLEROOM_LIKE_SWAP, 1, FD_T1
    MsgWinCloseAll
    h_goto_if_no FD_T1, L_PB_ToRoom
    FrontierCmd FC_F_SWAP, 0, 0, FD_T1  // factory_swapmons (the player's three, then the defeated opponent's three)
    h_goto_if_ne FD_T1, 1, L_PB_ToRoom
    FrontierCmd FC_F_SET_SWAPPED
    fd_say FD_FACTORYPREBATTLEROOM_SWAP_DONE, 1
    VMJump L_PB_ToRoom
L_PB_Rest:                              // AskPauseChallenge: save and quit
    h_yesno_actor FD_FACTORYPREBATTLEROOM_SAVE_QUIT, 1, FD_T1
    MsgWinCloseAll
    h_goto_if_no FD_T1, L_PB_Ask
    fd_rest_and_quit FD_F_LOBBY, 5, 6, 15, 6, FD_FACTORYPREBATTLEROOM_SAVING, 1
L_PB_Retire:                            // AskRetireChallenge -> the battle room's WarpToLobbyLost
    h_yesno_actor FD_FACTORYPREBATTLEROOM_RETIRE, 1, FD_T1
    MsgWinCloseAll
    h_goto_if_no FD_T1, L_PB_Ask
    fd_status FR_ST_LOST
    fd_to_lobby_m FD_F_LOBBY, 5, 6, 15, 6

Sub_PB_Opponent:                        // factory_generateopponentmons, CommentOnOpponentType / Style
    FrontierCmd FC_F_GEN_OPPONENT, 0, 0, FD_T1
    h_goto_if_eq FD_T1, 1, L_PB_OppHead
    fd_say FD_FACTORYPREBATTLEROOM_INVESTIGATED, 1
    FrontierCmd FC_F_OPP_TYPE, 0, 0, FD_T1
    WorkAdd FD_T1, FD_FACTORYPREBATTLEROOM_TYPE_0
    fd_say FD_T1, 1
    FrontierCmd FC_F_OPP_STYLE, 0, 0, FD_T1
    WorkAdd FD_T1, FD_FACTORYPREBATTLEROOM_STYLE_0
    fd_say FD_T1, 1
    VMReturn
L_PB_OppHead:                           // (the Factory Head: nothing to tell)
    fd_say FD_FACTORYPREBATTLEROOM_CANT_TELL_HEAD, 1
    VMReturn

    .balign 4, 0
PB_MvAttendantIn:                       // Movement_AttendantEnterRoom
    walk_up 5
    face_down
    step_end
PB_MvPlayerIn:                          // Movement_PlayerEnterRoom
    walk_up 5
    step_end
PB_MvTo50:                              // (8,8) -> the door (6,5) and in
    walk_left 2
    walk_up 4
    step_end
PB_MvToOpen:                            // (8,8) -> the door (10,5) and in
    walk_right 2
    walk_up 4
    step_end
PB_MvAttendantCall:                     // Movement_AttendantMoveToReceiveCall
    walk_right
    face_up
    step_end
PB_MvAttendantBack:                     // Movement_AttendantReturnToPlayer
    walk_left
    face_down
    step_end
