// BattleFrontier_BattleDomeLobby (zone 411; Emerald only): Emerald's Battle Dome lobby (pokeemerald
// data/maps/BattleFrontier_BattleDomeLobby/scripts.inc; frontier_factory_dome, 2026-10-12, notes/FRONTIER_FACTORY_DOME.md).
// The receptionist is frontier_core's lobby flow (pick three, Emerald's rules); just before the save the tournament is
// drawn (dome_init: frontier_factory_dome.c D_INIT). Room origin (1,-2). Two attendants as Emerald: the Single
// Battle Tournament (object 1, door (5,4)) and the Double Battle Tournament (object 6, door (17,4)); both lead to the
// same corridor.
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_story.inc"
#include "hoenn_emerald.inc"
#include "hoenn_frontier.inc"
#include "scenes/frontier_fd_lib.inc"

    ScriptEntry DL_Attendant            // 1: the singles attendant (TEALA)
    ScriptEntry DL_Man                  // 2
    ScriptEntry DL_Lass                 // 3
    ScriptEntry DL_FatMan               // 4
    ScriptEntry DL_Maniac               // 5
    ScriptEntry DL_Results              // 6: the results terminals (4,10), (18,10)
    ScriptEntry DL_PrevTree             // 7: the last tournament's tree (7,10)
    ScriptEntry DL_Rules                // 8: the rules board (15,10)
    ScriptEntry DL_Returned             // 9: map-script condition FD_STATE 0
    ScriptEntry DL_Init                 // 10: zone init (test builds only)
    ScriptEntry DL_AttendantD           // 11: the doubles attendant (Emerald object 6, TEALA)
    ScriptEntry DL_ResultsD             // 12: the doubles results terminal (18,10)
    ScriptEntriesEnd

DL_Attendant:
    fr_lobby_attendant FRONTIER_FACILITY_DOME, FRONTIER_MODE_SINGLES, 0, L_DL_Enter, 3, , , Sub_DL_Save
Sub_DL_Save:                            // dome_init (the sixteen trainers, their seeding, Tucker), before the save
    FrontierCmd FC_D_INIT
    VMReturn
L_DL_Enter:                             // EnterChallenge -> WalkToDoor (the glass door (5,4))
    h_applymovement 1, DL_MvWalkToDoor
    h_applymovement FD_PLAYER, DL_MvWalkToDoor
    h_waitmovement
    bt_door_open 6, 1
    h_applymovement 1, DL_MvAttendantIn
    h_applymovement FD_PLAYER, DL_MvPlayerIn
    h_waitmovement
    h_heal
    fd_to_room FD_D_CORR, 12, 4, 0, 1, 1    // warp MAP_BATTLE_FRONTIER_BATTLE_DOME_CORRIDOR, 23, 6

DL_AttendantD:                          // Emerald's DoublesAttendant: the same flow, Double Battles
    fr_lobby_attendant FRONTIER_FACILITY_DOME, FRONTIER_MODE_DOUBLES, FD_DOMELOBBY_LOBBYD_WELCOME, L_DL_EnterD, 3, , , Sub_DL_Save
L_DL_EnterD:                            // the doubles door (17,4)
    h_applymovement 6, DL_MvWalkToDoor
    h_applymovement FD_PLAYER, DL_MvWalkToDoor
    h_waitmovement
    bt_door_open 18, 1
    h_applymovement 6, DL_MvAttendantIn
    h_applymovement FD_PLAYER, DL_MvPlayerIn
    h_waitmovement
    h_heal
    fd_to_room FD_D_CORR, 12, 4, 0, 1, 1

DL_Returned:                            // (the receptionist of the challenge's mode says the lines)
    WorkSetConst FD_STATE, 1
    FrGet FR_BATTLE_MODE, FD_T0
    h_goto_if_eq FD_T0, FRONTIER_MODE_DOUBLES, L_DL_ReturnedD
    fr_lobby_returned FRONTIER_FACILITY_DOME, FRONTIER_MODE_SINGLES, 0, 1, L_DL_Enter
L_DL_ReturnedD:
    fr_lobby_returned FRONTIER_FACILITY_DOME, FRONTIER_MODE_DOUBLES, FD_DOMELOBBY_LOBBYD_WELCOME, 6, L_DL_EnterD

DL_Man:                                 // "The winner, {STR_VAR_1}, was seriously tough" (the last champion)
    FrontierCmd FC_D_WINNER, 1, 0, FD_T1
    h_goto_if_eq FD_T1, 0xFFFF, DL_Lass
    h_msgbox_npc FD_DOMELOBBY_MAN
DL_Lass:
    h_msgbox_npc FD_DOMELOBBY_LASS
DL_FatMan:
    h_msgbox_npc FD_DOMELOBBY_FAT_MAN
DL_Maniac:
    h_msgbox_npc FD_DOMELOBBY_MANIAC

DL_Results:                             // frontier_results FRONTIER_FACILITY_DOME
    h_lock
    h_buffer_player
    FrGet FD_DOME_STREAK_50, FD_T0
    WordSetNumber 1, FD_T0, 4
    FrGet FD_DOME_STREAK_50 + 1, FD_T0
    WordSetNumber 2, FD_T0, 4
    FrGet FD_DOME_STREAK_50 + 2, FD_T0
    WordSetNumber 3, FD_T0, 4
    FrGet FD_DOME_STREAK_50 + 3, FD_T0
    WordSetNumber 4, FD_T0, 4
    h_msgbox_info FD_DOMELOBBY_RESULTS
    h_release

DL_PrevTree:                            // ShowPrevTourneyTree: both halves of the last tournament (Black 2's 8-trainer
    h_lock                              // bracket screen shows one half at a time)
    FrontierCmd FC_D_WINNER, 1, 0, FD_T1
    h_goto_if_eq FD_T1, 0xFFFF, L_DL_NoTree
    FrontierCmd FC_D_PREV_KIND, 0, 0, FD_T1   // that tournament's Single / Double and level
    h_goto_if_eq FD_T1, 1, L_DL_TreeOpen
    h_goto_if_eq FD_T1, 2, L_DL_TreeD
    h_goto_if_eq FD_T1, 3, L_DL_TreeDOpen
    h_msgbox_info FD_DOMELOBBY_PREV_TREE
    VMJump L_DL_Tree
L_DL_TreeOpen:
    h_msgbox_info FD_DOMELOBBY_PREV_TREE_OPEN
    VMJump L_DL_Tree
L_DL_TreeD:
    h_msgbox_info FD_DOMELOBBY_PREV_TREE_D
    VMJump L_DL_Tree
L_DL_TreeDOpen:
    h_msgbox_info FD_DOMELOBBY_PREV_TREE_D_OPEN
L_DL_Tree:
    MsgWinCloseAll
    FrontierCmd FC_D_TREE, 2
    FrontierCmd FC_D_TREE, 3
L_DL_NoTree:
    h_release

DL_ResultsD:                            // frontier_results FRONTIER_FACILITY_DOME, doubles
    h_lock
    h_buffer_player
    FrGet FD_DOME_STREAK_50 + 4, FD_T0
    WordSetNumber 1, FD_T0, 4
    FrGet FD_DOME_STREAK_50 + 5, FD_T0
    WordSetNumber 2, FD_T0, 4
    FrGet FD_DOME_STREAK_50 + 6, FD_T0
    WordSetNumber 3, FD_T0, 4
    FrGet FD_DOME_STREAK_50 + 7, FD_T0
    WordSetNumber 4, FD_T0, 4
    h_msgbox_info FD_DOMELOBBY_RESULTS_D
    h_release

DL_Rules:                               // RulesBoard: the headings until EXIT
    h_lock
    h_msgbox_info FD_DOMELOBBY_RULES
L_DL_RulesAsk:
    SystemMsg FD_DOMELOBBY_RULES_WHICH, 2
    ListMenu_AnchorTopRight 31, 0, 0, 1, FD_T0
    ListMenuAdd FD_DOMELOBBY_MENU_MATCHUP, 65535, 0
    ListMenuAdd FD_DOMELOBBY_MENU_TREE, 65535, 1
    ListMenuAdd FD_DOMELOBBY_MENU_DOUBLE_KO, 65535, 2
    ListMenuAdd FD_DOMELOBBY_MENU_EXIT, 65535, 3
    ListMenuShow
    WorkCmpConst FD_T0, 2
    VMJumpIf CMP_GT, L_DL_RulesEnd
    WorkAdd FD_T0, FD_DOMELOBBY_RULES_MATCHUP
    SystemMsg FD_T0, 2
    LastKeyWait
    VMJump L_DL_RulesAsk
L_DL_RulesEnd:
    h_release

DL_Init:
#ifdef HOENN_TEST_CHFD
    // TEST ONLY (HOENN_TEST_CHFD=1, frontier_factory_dome): three Level 50 Pokémon for the Dome when the party has fewer
    h_getpartysize FD_T0
    h_goto_if_ge FD_T0, 3, L_DL_TestDone
    h_givemon SPECIES_SWAMPERT, 50, FD_T1
    h_givemon SPECIES_MANECTRIC, 50, FD_T1
    h_givemon SPECIES_TYRANITAR, 50, FD_T1
L_DL_TestDone:
#endif
    VMHalt

    .balign 4, 0
DL_MvWalkToDoor:                        // Movement_WalkToDoor
    walk_up 5
    step_end
DL_MvAttendantIn:                       // Movement_AttendantEnterDoor
    walk_up 2
    set_invisible
    step_end
DL_MvPlayerIn:                          // Movement_PlayerEnterDoor
    walk_up 3
    step_end
