// BattleFrontier_BattleArenaLobby (zone 429; Emerald only): Emerald's Battle Arena lobby (pokeemerald
// data/maps/BattleFrontier_BattleArenaLobby/scripts.inc; frontier_palace_arena, 2026-10-12,
// notes/FRONTIER_PALACE_ARENA.md). The attendant is frontier_core's lobby flow (hoenn_frontier.inc fr_lobby_attendant);
// he leads the player to the Lv. 50 door (2,2) or the Open Level door (11,2). Room origin (1,-1).
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_story.inc"
#include "hoenn_emerald.inc"
#include "hoenn_frontier.inc"
#include "scenes/frontier_pa_lib.inc"

    ScriptEntry AL_Attendant            // 1: the attendant (Emerald object 1, BLACK_BELT)
    ScriptEntry AL_Woman                // 2
    ScriptEntry AL_Man                  // 3
    ScriptEntry AL_Camper               // 4
    ScriptEntry AL_Youngster            // 5
    ScriptEntry AL_Results              // 6: the results (Emerald sign (5,9))
    ScriptEntry AL_Rules                // 7: the rules board (1,7)
    ScriptEntry AL_Returned             // 8: map-script condition PA_STATE 0 (Emerald's OnFrame table)
    ScriptEntriesEnd

AL_Attendant:
    fr_lobby_attendant FRONTIER_FACILITY_ARENA, FRONTIER_MODE_SINGLES, 0, L_AL_Enter, 3, , , Sub_AL_Save
Sub_AL_Save:                            // arena_init: a new challenge (before the save)
    fr_set FR_BATTLE_NUM, 0
    FrontierPA PA_INIT
    VMReturn
L_AL_Enter:                             // EnterChallenge: the door of the level mode, then the corridor
    fr_get FR_LVL_MODE, FD_T1
    h_goto_if_eq FD_T1, FR_LVL_OPEN, L_AL_Open
    h_applymovement 1, AL_MvAttendantToLeft
    h_applymovement PA_PLAYER, AL_MvPlayerToLeft
    h_waitmovement
    bt_door_open 3, 1                   // (Emerald's door (2,2))
    VMJump L_AL_In
L_AL_Open:
    h_applymovement 1, AL_MvAttendantToRight
    h_applymovement PA_PLAYER, AL_MvPlayerToRight
    h_waitmovement
    bt_door_open 12, 1                  // (Emerald's door (11,2))
L_AL_In:
    h_applymovement 1, AL_MvAttendantIn
    h_applymovement PA_PLAYER, AL_MvPlayerIn
    h_waitmovement
    fd_to_room PA_A_CORR, 10, 12, 0, 1, 1   // warp MAP_BATTLE_FRONTIER_BATTLE_ARENA_CORRIDOR, 9, 13

AL_Returned:
    WorkSetConst PA_STATE, 1
    fr_lobby_returned FRONTIER_FACILITY_ARENA, FRONTIER_MODE_SINGLES, 0, 1, L_AL_Resume
L_AL_Resume:                            // ResumeChallenge: the walk in again (the battle room asks "ready?")
    h_closemessage
    VMJump L_AL_Enter

AL_Woman:
    h_msgbox_npc PA_ARENALOBBY_WOMAN
AL_Man:
    h_msgbox_npc PA_ARENALOBBY_MAN
AL_Camper:
    h_msgbox_npc PA_ARENALOBBY_CAMPER
AL_Youngster:
    h_msgbox_npc PA_ARENALOBBY_YOUNGSTER

AL_Results:                             // frontier_results FRONTIER_FACILITY_ARENA (as one message)
    pa_results PA_ARE_STREAK_50, PA_ARENALOBBY_RESULTS

AL_Rules:                               // RulesBoard: the headings until EXIT
    h_lock
    h_msgbox_info PA_ARENALOBBY_RULES
L_AL_RulesAsk:
    SystemMsg PA_ARENALOBBY_RULES_WHICH, 2
    ListMenu_AnchorTopRight 31, 0, 0, 1, FD_T0
    ListMenuAdd PA_ARENALOBBY_MENU_BATTLE, 65535, 0
    ListMenuAdd PA_ARENALOBBY_MENU_MIND, 65535, 1
    ListMenuAdd PA_ARENALOBBY_MENU_SKILL, 65535, 2
    ListMenuAdd PA_ARENALOBBY_MENU_BODY, 65535, 3
    ListMenuAdd PA_ARENALOBBY_MENU_EXIT, 65535, 4
    ListMenuShow
    WorkCmpConst FD_T0, 3
    VMJumpIf CMP_GT, L_AL_RulesEnd
    WorkAdd FD_T0, PA_ARENALOBBY_RULES_BATTLE
    SystemMsg FD_T0, 2
    LastKeyWait
    VMJump L_AL_RulesAsk
L_AL_RulesEnd:
    h_release

    .balign 4, 0
AL_MvAttendantToLeft:                   // Movement_AttendantWalkToLeftDoor
    walk_up 3
    walk_left 5
    walk_up
    step_end
AL_MvPlayerToLeft:                      // Movement_PlayerWalkToLeftDoor
    walk_up 4
    walk_left 5
    walk_in_place_fastest_up
    step_end
AL_MvAttendantToRight:                  // Movement_AttendantWalkToRightDoor
    walk_up 3
    walk_right 4
    walk_up
    step_end
AL_MvPlayerToRight:                     // Movement_PlayerWalkToRightDoor
    walk_up 4
    walk_right 4
    walk_in_place_fastest_up
    step_end
AL_MvAttendantIn:                       // Movement_AttendantEnterDoor
    walk_up
    set_invisible
    step_end
AL_MvPlayerIn:                          // Movement_PlayerEnterDoor
    walk_up 2
    set_invisible
    step_end
