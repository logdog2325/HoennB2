// BattleFrontier_BattlePalaceLobby (zone 466; Emerald only): Emerald's Battle Palace lobby (pokeemerald
// data/maps/BattleFrontier_BattlePalaceLobby/scripts.inc; frontier_palace_arena, 2026-10-12,
// notes/FRONTIER_PALACE_ARENA.md). The two attendants are frontier_core's lobby flow (hoenn_frontier.inc
// fr_lobby_attendant): Single Battle Halls (object 1, door (5,4)) and Double Battle Halls (object 6, door (19,4)); the
// lobby text blocks are lines 0-22 (singles) and PA_PALACELOBBY_LOBBYD_* (doubles; b2tools/frontier_pa_text.py).
// Room origin (1,-2): Emerald (x, y) = zone (x + 1, y - 2).
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_story.inc"
#include "hoenn_emerald.inc"
#include "hoenn_frontier.inc"
#include "scenes/frontier_pa_lib.inc"

    ScriptEntry PL_Attendant            // 1: the singles attendant (Emerald object 1, EXPERT_M)
    ScriptEntry PL_BlackBelt            // 2
    ScriptEntry PL_Maniac               // 3
    ScriptEntry PL_Man                  // 4
    ScriptEntry PL_Beauty               // 5
    ScriptEntry PL_AttendantD           // 6: the doubles attendant (Emerald object 6)
    ScriptEntry PL_Results              // 7: the singles results (Emerald sign (2,7))
    ScriptEntry PL_ResultsD             // 8: the doubles results (Emerald sign (16,7))
    ScriptEntry PL_Rules                // 9: the rules board (10,4)
    ScriptEntry PL_Returned             // 10: map-script condition PA_STATE 0 (Emerald's OnFrame table)
    ScriptEntriesEnd

PL_Attendant:
    fr_lobby_attendant FRONTIER_FACILITY_PALACE, FRONTIER_MODE_SINGLES, 0, L_PL_Enter, 3, , , Sub_PL_Save
Sub_PL_Save:                            // palace_init: a new challenge (before the save)
    fr_set FR_BATTLE_NUM, 0
    FrontierPA PA_INIT
    VMReturn
L_PL_Enter:                             // EnterChallenge: WalkToDoor, then the corridor
    h_applymovement 1, PL_MvToDoor
    h_applymovement PA_PLAYER, PL_MvToDoor
    h_waitmovement
    bt_door_open 6, 1                   // (Emerald's door (5,4))
    h_applymovement 1, PL_MvAttendantIn
    h_applymovement PA_PLAYER, PL_MvPlayerIn
    h_waitmovement
    fd_to_room PA_P_CORR, 9, 11, 0, 1, 1    // warp MAP_BATTLE_FRONTIER_BATTLE_PALACE_CORRIDOR, 8, 13

PL_AttendantD:
    fr_lobby_attendant FRONTIER_FACILITY_PALACE, FRONTIER_MODE_DOUBLES, PA_PALACELOBBY_LOBBYD_WELCOME, L_PL_EnterD, 3, , , Sub_PL_Save
L_PL_EnterD:
    h_applymovement 6, PL_MvToDoor
    h_applymovement PA_PLAYER, PL_MvToDoor
    h_waitmovement
    bt_door_open 20, 1                  // (Emerald's door (19,4))
    h_applymovement 6, PL_MvAttendantIn
    h_applymovement PA_PLAYER, PL_MvPlayerIn
    h_waitmovement
    fd_to_room PA_P_CORR, 9, 11, 0, 1, 1

PL_Returned:                            // (the attendant of the challenge's mode says the lines)
    WorkSetConst PA_STATE, 1
    FrGet FR_BATTLE_MODE, FD_T0
    h_goto_if_eq FD_T0, FRONTIER_MODE_DOUBLES, L_PL_ReturnedD
    fr_lobby_returned FRONTIER_FACILITY_PALACE, FRONTIER_MODE_SINGLES, 0, 1, L_PL_Resume
L_PL_ReturnedD:
    fr_lobby_returned FRONTIER_FACILITY_PALACE, FRONTIER_MODE_DOUBLES, PA_PALACELOBBY_LOBBYD_WELCOME, 6, L_PL_ResumeD
L_PL_Resume:                            // ResumeChallenge: the walk in again (the battle room asks "ready?")
    h_closemessage
    VMJump L_PL_Enter
L_PL_ResumeD:
    h_closemessage
    VMJump L_PL_EnterD

PL_BlackBelt:
    h_msgbox_npc PA_PALACELOBBY_BLACK_BELT
PL_Man:
    h_msgbox_npc PA_PALACELOBBY_MAN
PL_Beauty:
    h_msgbox_npc PA_PALACELOBBY_BEAUTY
PL_Maniac:
    h_msgbox_npc PA_PALACELOBBY_MANIAC

PL_Results:                             // frontier_results FRONTIER_FACILITY_PALACE, singles (as one message)
    pa_results PA_PAL_STREAK_50, PA_PALACELOBBY_RESULTS
PL_ResultsD:
    pa_results PA_PAL_STREAK_50 + 4, PA_PALACELOBBY_RESULTS_D

PL_Rules:                               // RulesBoard: the headings until EXIT
    h_lock
    h_msgbox_info PA_PALACELOBBY_RULES
L_PL_RulesAsk:
    SystemMsg PA_PALACELOBBY_RULES_WHICH, 2
    ListMenu_AnchorTopRight 31, 0, 0, 1, FD_T0
    ListMenuAdd PA_PALACELOBBY_MENU_BASICS, 65535, 0
    ListMenuAdd PA_PALACELOBBY_MENU_NATURE, 65535, 1
    ListMenuAdd PA_PALACELOBBY_MENU_MOVES, 65535, 2
    ListMenuAdd PA_PALACELOBBY_MENU_UNDERPOWERED, 65535, 3
    ListMenuAdd PA_PALACELOBBY_MENU_DANGER, 65535, 4
    ListMenuAdd PA_PALACELOBBY_MENU_EXIT, 65535, 5
    ListMenuShow
    WorkCmpConst FD_T0, 4
    VMJumpIf CMP_GT, L_PL_RulesEnd
    WorkAdd FD_T0, PA_PALACELOBBY_RULES_BASICS
    SystemMsg FD_T0, 2
    LastKeyWait
    VMJump L_PL_RulesAsk
L_PL_RulesEnd:
    h_release

    .balign 4, 0
PL_MvToDoor:                            // Movement_WalkToDoor
    walk_up
    step_end
PL_MvAttendantIn:                       // Movement_AttendantEnterDoor
    walk_up
    set_invisible
    step_end
PL_MvPlayerIn:                          // Movement_PlayerEnterDoor
    walk_up 2
    set_invisible
    step_end
