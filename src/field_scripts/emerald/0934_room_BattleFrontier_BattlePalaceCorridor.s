// BattleFrontier_BattlePalaceCorridor (zone 467; Emerald only): the garden corridor (pokeemerald
// data/maps/BattleFrontier_BattlePalaceCorridor/scripts.inc; frontier_palace_arena, 2026-10-12). Reached only by script
// 1 from the lobby: the attendant walks the player in, says one of Emerald's comments (palace_getcomment: a random one
// of three below a 50-win streak, then the streak ones), and leads the way to the Lv. 50 hall (door (6,3)) or the
// Open Level hall (door (10,3)). Room origin (1,-2).
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_story.inc"
#include "hoenn_emerald.inc"
#include "hoenn_frontier.inc"
#include "scenes/frontier_pa_lib.inc"

    ScriptEntry PC_Enter                // 1: WalkThroughCorridor
    ScriptEntry PC_None                 // 2: the attendant and the Pokémon (no talk script in Emerald)
    ScriptEntriesEnd

PC_None:
    VMHalt

PC_Enter:
    ActorsPauseAll
    fd_player_visible
    FadeInBlack
    FadeWait
    h_delay 16
    h_applymovement 1, PC_MvEnter
    h_applymovement PA_PLAYER, PC_MvEnter
    h_waitmovement
    VMCall Sub_PC_Comment
    MsgWinCloseAll
    fr_get FR_LVL_MODE, FD_T1
    h_goto_if_eq FD_T1, FR_LVL_OPEN, L_PC_Open
    h_applymovement 1, PC_MvAttendantTo50
    h_applymovement PA_PLAYER, PC_MvPlayerTo50
    h_waitmovement
    bt_door_open 7, 1                   // (Emerald's door (6,3))
    h_applymovement 1, PC_MvAttendantIn
    h_applymovement PA_PLAYER, PC_MvPlayerIn
    h_waitmovement
    VMJump L_PC_Warp
L_PC_Open:
    h_applymovement 1, PC_MvAttendantToOpen
    h_applymovement PA_PLAYER, PC_MvPlayerToOpen
    h_waitmovement
    bt_door_open 11, 1                  // (Emerald's door (10,3))
    h_applymovement 1, PC_MvAttendantIn
    h_applymovement PA_PLAYER, PC_MvPlayerIn
    h_waitmovement
L_PC_Warp:                              // warp MAP_BATTLE_FRONTIER_BATTLE_PALACE_BATTLE_ROOM (the player walks in from
    fd_to_room PA_P_ROOM, 2, 9, 0, 1, 1     // Emerald's stand-in spot (1,9): the camera follows the player here)

Sub_PC_Comment:                         // palace_getcomment: the streak of this mode and level
    FrGet FR_BATTLE_MODE, FD_T0
    FrGet FR_LVL_MODE, FD_T1
    WorkMul FD_T0, 4
    WorkMul FD_T1, 2
    WorkAdd FD_T0, FD_T1
    WorkAdd FD_T0, PA_PAL_STREAK_50
    FrGet FD_T0, FD_T2
    h_goto_if_ge FD_T2, 99, L_PC_Long
    h_goto_if_ge FD_T2, 50, L_PC_Streak
    FrontierPA PA_RANDOM, 3, 0, FD_T1
    WorkAdd FD_T1, PA_PALACECORRIDOR_PEOPLE
    ActorMsg MSGFILE_SCRIPT, FD_T1, 1, 0, 0
    LastKeyWait
    VMReturn
L_PC_Streak:
    h_msgbox_actor PA_PALACECORRIDOR_UNDERSTAND, 1
    VMReturn
L_PC_Long:
    h_msgbox_actor PA_PALACECORRIDOR_HEARTFELT, 1
    VMReturn

    .balign 4, 0
PC_MvEnter:                             // Movement_EnterCorridor
    walk_up 4
    step_end
PC_MvAttendantTo50:
    walk_up 2
    walk_left 2
    walk_up 2
    step_end
PC_MvPlayerTo50:
    walk_up 3
    walk_left 2
    walk_up
    step_end
PC_MvAttendantToOpen:
    walk_up
    walk_right 2
    walk_up 3
    step_end
PC_MvPlayerToOpen:
    walk_up 2
    walk_right 2
    walk_up 2
    step_end
PC_MvPlayerIn:                          // Movement_PlayerEnterBattleRoom
    walk_up
PC_MvAttendantIn:                       // Movement_AttendantEnterBattleRoom
    walk_up
    set_invisible
    step_end
