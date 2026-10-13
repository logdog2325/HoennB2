// BattleFrontier_BattleArenaCorridor (zone 431; Emerald only): the hall to the battle room (pokeemerald
// data/maps/BattleFrontier_BattleArenaCorridor/scripts.inc; frontier_palace_arena, 2026-10-12). Reached only by script
// 1 from the lobby: the attendant leads the player round the hall to the battle room's door, "Please step in!".
// Room origin (1,-1).
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_story.inc"
#include "hoenn_emerald.inc"
#include "hoenn_frontier.inc"
#include "scenes/frontier_pa_lib.inc"

    ScriptEntry AC_Enter                // 1: WalkToBattleRoom
    ScriptEntry AC_None                 // 2: the attendant
    ScriptEntriesEnd

AC_None:
    VMHalt

AC_Enter:
    ActorsPauseAll
    fd_player_visible
    FadeInBlack
    FadeWait
    h_delay 16
    h_applymovement 1, AC_MvAttendantToDoor
    h_applymovement PA_PLAYER, AC_MvPlayerToDoor
    h_waitmovement
    h_applymovement 1, AC_MvAttendantFacePlayer
    h_waitmovement
    fd_say PA_ARENACORRIDOR_STEP_IN, 1
    h_applymovement 1, AC_MvAttendantOutOfWay
    h_waitmovement
    h_applymovement PA_PLAYER, AC_MvPlayerIn
    h_waitmovement
    fd_to_room PA_A_ROOM, 1, 5, 3, 1    // warp MAP_BATTLE_FRONTIER_BATTLE_ARENA_BATTLE_ROOM (at the stand-in's spot (0,6))

    .balign 4, 0
AC_MvPlayerToDoor:                      // Movement_PlayerWalkToDoor
    walk_up
    walk_left 8
    walk_up 8
    walk_right 3
    step_end
AC_MvPlayerIn:                          // Movement_PlayerEnterDoor
    walk_right
    set_invisible
    step_end
AC_MvAttendantToDoor:                   // Movement_AttendantWalkToDoor
    walk_left 8
    walk_up 8
    walk_right 4
    step_end
AC_MvAttendantFacePlayer:
    walk_in_place_fastest_left
    step_end
AC_MvAttendantOutOfWay:
    walk_up
    walk_in_place_fastest_down
    step_end
