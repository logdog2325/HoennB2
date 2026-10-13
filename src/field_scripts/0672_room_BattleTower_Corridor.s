// BattleTower_Corridor (zone 336): Sapphire's walk to the Battle Room (data/maps/BattleTower_Corridor/scripts.inc;
// battle_tower agent, 2026-10-08, notes/BATTLE_TOWER.md). Reached only from the Elevator (h_warp_scene to script 1),
// leaves by h_warp_scene to the Battle Room's script 1. Sapphire opens the Level 50 room's door (12,0) or the Level 100
// room's (15,0) on load (VAR_0x8006 = the level, setmetatile ..._CorridorOpenDoor) and walks the attendant and the
// player into it (ON_FRAME VAR_TEMP_0 0). No text.
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_story.inc"
#include "scenes/battle_tower_lib.inc"

    ScriptEntry BTC_Walk                // 1: BattleTower_Corridor_EventScript_16088B (arrival from the elevator)
    ScriptEntriesEnd

// ---- story (battle_tower)
BTC_Walk:                               // the player arrives at Sapphire (8,1), the floor in front of the elevator here (the
                                        // room's doors stand north of row 1: Sapphire's door step to (8,2)); the attendant
                                        // waits beside him at (9,1) (data/interiors/336.json; Sapphire (9,2), walk_sweep)
    ActorsPauseAll
    h_goto_if_eq VAR_BT_LEVEL_TYPE, 1, L_BTC_Door100
    bt_door_open 12 + BT_CORRIDOR_OX, 0 + BT_CORRIDOR_OZ     // ON_LOAD: setmetatile 12, 0 / 12, 1 ..._CorridorOpenDoor
    VMJump L_BTC_In
L_BTC_Door100:
    bt_door_open 15 + BT_CORRIDOR_OX, 0 + BT_CORRIDOR_OZ     // VAR_0x8006 1: setmetatile 15, 0 / 15, 1
L_BTC_In:
    FadeInBlack
    FadeWait
    h_goto_if_eq VAR_BT_LEVEL_TYPE, 1, L_BTC_Lv100
    h_applymovement BT_ATTENDANT, BTC_Attendant50       // BattleTower_Corridor_Movement_1608D5
    h_applymovement BT_PLAYER, BTC_Player50             // _1608D4
    h_waitmovement
    VMJump L_BTC_Go
L_BTC_Lv100:
    h_applymovement BT_ATTENDANT, BTC_Attendant100      // _1608D2
    h_applymovement BT_PLAYER, BTC_Player100            // _1608D1
    h_waitmovement
L_BTC_Go:                               // warp MAP_BATTLE_TOWER_BATTLE_ROOM, 255, 4, 8 (h_warp_scene, the door's handle
    FadeOutBlack                        // let go on the black screen)
    RTReserveScript 1
    FadeWait
    BMReleaseHandle BT_DOOR
    MapChangeCore BT_ROOM_ZONE, 4 + BT_ROOM_OX, 0, 8 + BT_ROOM_OZ, 0
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

    .balign 4, 0
BTC_Attendant50:                        // _1608D5
    walk_right 3
    walk_up
    set_invisible
    step_end
BTC_Player50:                           // _1608D4 (+ _1608D5)
    walk_right 4
    walk_up
    set_invisible
    step_end
BTC_Attendant100:                       // _1608D2 (+ _1608D4 + _1608D5)
    walk_right 6
    walk_up
    set_invisible
    step_end
BTC_Player100:                          // _1608D1 (+ ...)
    walk_right 7
    walk_up
    set_invisible
    step_end
