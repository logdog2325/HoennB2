// SlateportCity_BattleTentCorridor (zone 524; Emerald only): the Slateport tent's rental room (pokeemerald
// data/maps/SlateportCity_BattleTentCorridor/scripts.inc, "Slateport Tent's version of the Battle Factory Pre-Battle
// Room"; battle_tents, 2026-10-18, notes/BATTLE_TENTS.md). Reached only by script: 1 from the lobby (a new challenge),
// 3 back from a won battle, 4 a resumed challenge. The rentals, the opponent and the swap are frontier_factory_dome.c's
// Slateport tent mode (FrontierCmd TC_T_*: the tent's 70 sets, every Pokémon at level 30); the screens are Black 2's
// battle-entry party screen. Every arrival walks in from (2,7) with the attendant (Emerald puts the player at (2,3) with
// the attendant above on the way back from a battle). Room origin (1,0).
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_story.inc"
#include "hoenn_emerald.inc"
#include "hoenn_frontier.inc"
#include "scenes/battle_tents_lib.inc"

    ScriptEntry SC_First                // 1: EnterCorridor (VAR_0x8006 0): the rentals, the first opponent, the rental screen
    ScriptEntry SC_None                 // 2: the attendant (no talk script in Emerald)
    ScriptEntry SC_Return               // 3: ReturnToRoomFromBattle (VAR_0x8006 1)
    ScriptEntry SC_Resume               // 4: ResumeChallenge (VAR_0x8006 2)
    ScriptEntriesEnd

SC_None:
    VMHalt

    .macro sc_walk_in
    ActorsPauseAll
    fd_player_visible
    FadeInBlack
    FadeWait
    h_applymovement 1, SC_MvAttendantIn
    h_applymovement TT_PLAYER, SC_MvPlayerIn
    h_waitmovement
    .endm

SC_First:
    sc_walk_in
    FrontierCmd TC_T_GEN_RENTALS        // slateporttent_generaterentalmons
    FrontierCmd TC_T_GEN_OPPONENT       // slateporttent_generateopponentmons
    fd_say BT_S_CORRIDOR_HOLD_CHOOSE, 1
    FrontierCmd TC_T_RENT, 0, 0, FD_T1  // slateporttent_rentmons (three of the six; the screen cannot be left without them)
L_SC_ToRoom:                            // EnterBattleRoom
    fd_say BT_S_CORRIDOR_THIS_WAY, 1
    h_applymovement 1, SC_MvFaceUp
    h_waitmovement
    bt_door_open TT_CX(2), TT_CZ(1)     // opendoor 2, 1
    h_applymovement 1, SC_MvAttendantOut
    h_applymovement TT_PLAYER, SC_MvPlayerOut
    h_waitmovement
    fd_to_room TT_S_ROOM, TT_RX(4), TT_RZ(8), 0, 1, 1      // warp ..._BATTLE_ROOM (the stand-in's (4,8))

SC_Return:                              // ReturnToRoomFromBattle
    sc_walk_in
    FrontierCmd TC_T_KEEP_OPPONENT      // factory_setopponentmons: the defeated three can be swapped in
    ActorMsg MSGFILE_SCRIPT, BT_S_CORRIDOR_RESTORE, 1, 0, 0
    LastKeyWait
    MEPlay MUS_HEAL
    MEWait
    MsgWinCloseAll
    h_heal
    VMJump L_SC_Ask

SC_Resume:                              // ResumeChallenge
    sc_walk_in
L_SC_Ask:                               // AskReadyForOpponent: "the 2nd / 3rd match is next" GO ON / REST / RETIRE
    fr_get FR_BATTLE_NUM, FD_T1
    WorkAdd FD_T1, BT_S_CORRIDOR_READY_2 - 1
    ActorMsg MSGFILE_SCRIPT, FD_T1, 1, 0, 0
    fd_menu3 FD_T2, BT_S_CORRIDOR_MENU_GO_ON, BT_S_CORRIDOR_MENU_REST, BT_S_CORRIDOR_MENU_RETIRE
    MsgWinCloseAll
    h_goto_if_eq FD_T2, 0, L_SC_GoOn
    h_goto_if_eq FD_T2, 1, L_SC_Rest
    h_goto_if_eq FD_T2, 2, L_SC_Retire
    VMJump L_SC_Ask
L_SC_GoOn:                              // AskSwapMon: the next opponent first, then "swap a Pokémon?"
    FrontierCmd TC_T_GEN_OPPONENT
    h_yesno_actor BT_S_CORRIDOR_LIKE_SWAP, 1, FD_T1
    MsgWinCloseAll
    h_goto_if_no FD_T1, L_SC_ToRoom
    FrontierCmd TC_T_SWAP, 0, 0, FD_T1  // slateporttent_swapmons (the player's three, then the defeated opponent's three)
    h_goto_if_ne FD_T1, 1, L_SC_ToRoom
    fd_say BT_S_CORRIDOR_SWAP_DONE, 1
    VMJump L_SC_ToRoom
L_SC_Rest:                              // AskPauseChallenge -> PauseChallenge: save and quit
    h_yesno_actor BT_S_CORRIDOR_SAVE_QUIT, 1, FD_T1
    MsgWinCloseAll
    h_goto_if_no FD_T1, L_SC_Ask
    fr_rest_and_quit TT_S_LOBBY, TT_LX(6), TT_LZ(6), 0, BT_S_CORRIDOR_SAVING, 1
L_SC_Retire:                            // AskRetireChallenge -> the battle room's WarpToLobbyLost
    h_yesno_actor BT_S_CORRIDOR_RETIRE, 1, FD_T1
    MsgWinCloseAll
    h_goto_if_no FD_T1, L_SC_Ask
    fd_status FR_ST_LOST
    fd_to_lobby TT_S_LOBBY, TT_LX(6), TT_LZ(6)

    .balign 4, 0
SC_MvAttendantIn:                       // Movement_AttendantEnter
    walk_up 4
    walk_in_place_fast_down
    step_end
SC_MvPlayerIn:                          // Movement_PlayerEnter
    walk_up 4
    step_end
SC_MvFaceUp:                            // Common_Movement_WalkInPlaceFasterUp
    walk_in_place_fast_up
    step_end
SC_MvAttendantOut:                      // Movement_AttendantExit
    walk_up
    set_invisible
    step_end
SC_MvPlayerOut:                         // Movement_PlayerExit
    walk_up 2
    set_invisible
    step_end
