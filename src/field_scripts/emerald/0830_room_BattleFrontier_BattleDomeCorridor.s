// BattleFrontier_BattleDomeCorridor (zone 415; Emerald only): the walk to the Level 50 or Open Level waiting room
// (pokeemerald data/maps/BattleFrontier_BattleDomeCorridor/scripts.inc; frontier_factory_dome, 2026-10-12). Reached
// only by script 1. Room origin (-11,-2): Emerald (x, y) = zone (x - 11, y - 2); doors (13,3) Lv. 50 and (37,3) Open.
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_story.inc"
#include "hoenn_emerald.inc"
#include "hoenn_frontier.inc"
#include "scenes/frontier_fd_lib.inc"

    ScriptEntry DC_Walk                 // 1: OnFrame EnterCorridor
    ScriptEntry DC_None                 // 2: the attendant
    ScriptEntriesEnd

DC_None:
    VMHalt

DC_Walk:
    ActorsPauseAll
    fd_player_visible
    FadeInBlack
    FadeWait
    fr_get FR_LVL_MODE, FD_T1
    h_goto_if_eq FD_T1, FR_LVL_OPEN, L_DC_Open
    h_applymovement 1, DC_MvAttendant50
    h_applymovement FD_PLAYER, DC_MvPlayer50
    h_waitmovement
    bt_door_open 2, 1                   // opendoor 13, 3
    h_applymovement 1, DC_MvAttendantIn
    h_applymovement FD_PLAYER, DC_MvPlayerIn
    h_waitmovement
    fd_to_room FD_D_PRE, 6, 7, 0, 1, 1  // warp MAP_BATTLE_FRONTIER_BATTLE_DOME_PRE_BATTLE_ROOM, 5, 7
L_DC_Open:
    h_applymovement 1, DC_MvAttendantOpen
    h_applymovement FD_PLAYER, DC_MvPlayerOpen
    h_waitmovement
    bt_door_open 26, 1                  // opendoor 37, 3
    h_applymovement 1, DC_MvAttendantIn
    h_applymovement FD_PLAYER, DC_MvPlayerIn
    h_waitmovement
    fd_to_room FD_D_PRE, 6, 7, 0, 1, 1

    .balign 4, 0
DC_MvAttendant50:                       // Movement_AttendantWalkToDoorLv50
    walk_left 10
    walk_up
    step_end
DC_MvPlayer50:                          // Movement_PlayerWalkToDoorLv50
    walk_up
    walk_left 10
    walk_in_place_fastest_up
    step_end
DC_MvAttendantOpen:                     // Movement_AttendantWalkToDoorLvOpen
    walk_right 14
    walk_up
    step_end
DC_MvPlayerOpen:                        // Movement_PlayerWalkToDoorLvOpen
    walk_up
    walk_right 14
    walk_in_place_fastest_up
    step_end
DC_MvAttendantIn:                       // Movement_AttendantEnterDoor
    walk_up
    set_invisible
    step_end
DC_MvPlayerIn:                          // Movement_PlayerEnterDoor
    walk_up 2
    step_end
