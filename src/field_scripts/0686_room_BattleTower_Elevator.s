// BattleTower_Elevator (zone 343): Sapphire's elevator ride (data/maps/BattleTower_Elevator/scripts.inc; battle_tower agent,
// 2026-10-08, notes/BATTLE_TOWER.md). Reached only by the lobby's walk to the Battle Room (h_warp_scene to script 1);
// leaves by h_warp_scene to the Corridor's script 1. Sapphire's map scripts (ON_WARP_INTO: face north; ON_FRAME
// VAR_TEMP_0 0: the ride) are this reserved arrival script. No text.
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_story.inc"
#include "scenes/battle_tower_lib.inc"

    ScriptEntry BTE_Ride                // 1: BattleTower_Elevator_EventScript_1607E4 (arrival from the lobby)
    ScriptEntriesEnd

// ---- story (battle_tower)
BTE_Ride:                               // the player arrives at Sapphire (1,6), below the attendant at (1,5)
    ActorsPauseAll
    h_turnobject BT_PLAYER, 0           // ON_WARP_INTO_MAP_TABLE: turnobject LOCALID_PLAYER, DIR_NORTH
    FadeInBlack
    FadeWait
    h_applymovement BT_ATTENDANT, BTE_AttendantIn
    h_applymovement BT_PLAYER, BTE_PlayerIn
    h_waitmovement
    SEPlay SEQ_SE_FLD_23                // special ShakeScreenInElevator: Black 2's elevator rumble and shake (as the
    EvCameraShake 4, 0, 4, 5, 1, 0, 1, 3    // Lilycove Dept. Store's elevator, 0362), then delay 64
    h_delay 64
    SEStop
    h_applymovement BT_ATTENDANT, BTE_AttendantOut
    h_applymovement BT_PLAYER, BTE_PlayerOut
    h_waitmovement
    h_warp_scene BT_CORRIDOR_ZONE, 8 + BT_CORRIDOR_OX, 1 + BT_CORRIDOR_OZ, 3, 1    // warp MAP_BATTLE_TOWER_CORRIDOR, 255, 8, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

    .balign 4, 0
BTE_AttendantIn:                        // BattleTower_Elevator_Movement_160835
    walk_up
    walk_right
    face_down
    step_end
BTE_PlayerIn:                           // _160839
    walk_up
    walk_up
    face_down
    step_end
BTE_AttendantOut:                       // _16083D
    walk_down
    walk_down
    set_invisible
    step_end
BTE_PlayerOut:                          // _160841
    walk_right
    walk_down
    walk_down
    step_end
