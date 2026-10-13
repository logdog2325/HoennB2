// BattleFrontier_BattleFactoryLobby (zone 408; Emerald only): Emerald's Battle Factory lobby (pokeemerald
// data/maps/BattleFrontier_BattleFactoryLobby/scripts.inc; frontier_factory_dome, 2026-10-12, notes/FRONTIER_FACTORY_DOME.md).
// The receptionist is frontier_core's lobby flow (hoenn_frontier.inc fr_lobby_attendant: no pick, the rentals come in the
// next room); the lobby text blocks are lines 0-22 (singles) and FD_FACTORYLOBBY_LOBBYD_* (doubles; b2tools/frontier_fd_text.py).
// Room origin (1,-2): Emerald (x, y) = zone (x + 1, y - 2). Two attendants as Emerald: Battle Swap Single (object 1,
// door (4,4)) and Battle Swap Double (object 6, door (14,4)); both lead to the same rental room.
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_story.inc"
#include "hoenn_emerald.inc"
#include "hoenn_frontier.inc"
#include "scenes/frontier_fd_lib.inc"

    ScriptEntry FL_Attendant            // 1: the singles attendant (Emerald object 1, SCIENTIST_1)
    ScriptEntry FL_Woman                // 2
    ScriptEntry FL_Camper               // 3
    ScriptEntry FL_Picnicker            // 4
    ScriptEntry FL_FatMan               // 5
    ScriptEntry FL_Results              // 6: the results terminals (Emerald signs (2,7), (11,7))
    ScriptEntry FL_Rules                // 7: the rules board (9,4)
    ScriptEntry FL_Returned             // 8: map-script condition FD_STATE 0 (Emerald's OnFrame table)
    ScriptEntry FL_AttendantD           // 9: the doubles attendant (Emerald object 6, SCIENTIST_1)
    ScriptEntry FL_ResultsD             // 10: the doubles results terminal (Emerald sign (11,7))
    ScriptEntriesEnd

FL_Attendant:
    fr_lobby_attendant FRONTIER_FACILITY_FACTORY, FRONTIER_MODE_SINGLES, 0, L_FL_Enter, 0, , , Sub_FL_Save
Sub_FL_Save:                            // factory_init (Emerald: before the save)
    FrontierCmd FC_F_INIT
    VMReturn
L_FL_Enter:                             // EnterChallenge: the attendant and the player walk through the door (4,4)
    bt_door_open 5, 1
    h_applymovement 1, FL_MvAttendantIn
    h_applymovement FD_PLAYER, FL_MvPlayerIn
    h_waitmovement
    fd_to_room FD_F_PRE, 9, 10, 0, 1, 1  // warp MAP_BATTLE_FRONTIER_BATTLE_FACTORY_PRE_BATTLE_ROOM, 8, 13

FL_AttendantD:                          // Emerald's DoublesAttendant: the same flow, Double Battles
    fr_lobby_attendant FRONTIER_FACILITY_FACTORY, FRONTIER_MODE_DOUBLES, FD_FACTORYLOBBY_LOBBYD_WELCOME, L_FL_EnterD, 0, , , Sub_FL_Save
L_FL_EnterD:                            // the doubles attendant's door (14,4)
    bt_door_open 15, 1
    h_applymovement 6, FL_MvAttendantIn
    h_applymovement FD_PLAYER, FL_MvPlayerIn
    h_waitmovement
    fd_to_room FD_F_PRE, 9, 10, 0, 1, 1

FL_Returned:                            // (the receptionist of the challenge's mode says the lines)
    WorkSetConst FD_STATE, 1
    FrGet FR_BATTLE_MODE, FD_T0
    h_goto_if_eq FD_T0, FRONTIER_MODE_DOUBLES, L_FL_ReturnedD
    fr_lobby_returned FRONTIER_FACILITY_FACTORY, FRONTIER_MODE_SINGLES, 0, 1, L_FL_Resume
L_FL_ReturnedD:
    fr_lobby_returned FRONTIER_FACILITY_FACTORY, FRONTIER_MODE_DOUBLES, FD_FACTORYLOBBY_LOBBYD_WELCOME, 6, L_FL_ResumeD
L_FL_ResumeD:
    bt_door_open 15, 1
    h_applymovement 6, FL_MvAttendantIn
    h_applymovement FD_PLAYER, FL_MvPlayerIn
    h_waitmovement
    fd_to_room FD_F_PRE, 9, 10, 0, 4, 1
L_FL_Resume:                            // ResumeChallenge: the walk in again, then the pre-battle room asks "ready?"
    bt_door_open 5, 1
    h_applymovement 1, FL_MvAttendantIn
    h_applymovement FD_PLAYER, FL_MvPlayerIn
    h_waitmovement
    fd_to_room FD_F_PRE, 9, 10, 0, 4, 1

FL_Woman:
    h_msgbox_npc FD_FACTORYLOBBY_MAN_KNOWLEDGE
FL_Camper:
    h_msgbox_npc FD_FACTORYLOBBY_CAMPER
FL_Picnicker:
    h_msgbox_npc FD_FACTORYLOBBY_PICNICKER
FL_FatMan:
#ifdef HOENN_TEST_CHFD
    // TEST ONLY (HOENN_TEST_CHFD=1, frontier_factory_dome): the fat man warps to the Battle Dome lobby
    h_lock
    h_warp_arrive FD_D_LOBBY, 12, 12, 0
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt
#endif
    h_msgbox_npc FD_FACTORYLOBBY_FAT_MAN

FL_Results:                             // frontier_results FRONTIER_FACILITY_FACTORY (Emerald's window, as one message)
    h_lock
    h_buffer_player
    FrGet FD_FAC_STREAK_50, FD_T0
    WordSetNumber 1, FD_T0, 4
    FrGet FD_FAC_STREAK_50 + 1, FD_T0
    WordSetNumber 2, FD_T0, 4
    FrGet FD_FAC_STREAK_50 + 2, FD_T0
    WordSetNumber 3, FD_T0, 4
    FrGet FD_FAC_STREAK_50 + 3, FD_T0
    WordSetNumber 4, FD_T0, 4
    h_msgbox_info FD_FACTORYLOBBY_RESULTS
    h_release

FL_ResultsD:                            // frontier_results FRONTIER_FACILITY_FACTORY, doubles
    h_lock
    h_buffer_player
    FrGet FD_FAC_STREAK_50 + 4, FD_T0
    WordSetNumber 1, FD_T0, 4
    FrGet FD_FAC_STREAK_50 + 5, FD_T0
    WordSetNumber 2, FD_T0, 4
    FrGet FD_FAC_STREAK_50 + 6, FD_T0
    WordSetNumber 3, FD_T0, 4
    FrGet FD_FAC_STREAK_50 + 7, FD_T0
    WordSetNumber 4, FD_T0, 4
    h_msgbox_info FD_FACTORYLOBBY_RESULTS_D
    h_release

FL_Rules:                               // RulesBoard: the headings until EXIT
    h_lock
    h_msgbox_info FD_FACTORYLOBBY_RULES
L_FL_RulesAsk:
    SystemMsg FD_FACTORYLOBBY_RULES_WHICH, 2
    ListMenu_AnchorTopRight 31, 0, 0, 1, FD_T0
    ListMenuAdd FD_FACTORYLOBBY_MENU_BASIC, 65535, 0
    ListMenuAdd FD_FACTORYLOBBY_MENU_PARTNER, 65535, 1
    ListMenuAdd FD_FACTORYLOBBY_MENU_NUMBER, 65535, 2
    ListMenuAdd FD_FACTORYLOBBY_MENU_NOTES, 65535, 3
    ListMenuAdd FD_FACTORYLOBBY_MENU_OPEN, 65535, 4
    ListMenuAdd FD_FACTORYLOBBY_MENU_EXIT, 65535, 5
    ListMenuShow
    WorkCmpConst FD_T0, 4
    VMJumpIf CMP_GT, L_FL_RulesEnd
    WorkAdd FD_T0, FD_FACTORYLOBBY_RULES_BASIC
    SystemMsg FD_T0, 2
    LastKeyWait
    VMJump L_FL_RulesAsk
L_FL_RulesEnd:
    h_release

    .balign 4, 0
FL_MvAttendantIn:                       // Movement_AttendantEnterDoor
    walk_up 3
    set_invisible
    step_end
FL_MvPlayerIn:                          // Movement_PlayerEnterDoor
    walk_up 4
    step_end
