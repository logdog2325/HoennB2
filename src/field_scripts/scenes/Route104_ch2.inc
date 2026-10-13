// Route 104: chapter Ch2's beats (Sapphire data/maps/Route104/scripts.inc Route104_EventScript_14EFD5: Mr. Briney's boat
// from his cottage to Dewford, its movements; his objects 7/8 and their flags), included in both parts of chapter
// Ch1's scenes/Route104.inc (Route 104's owner). Script 4 (Ch2_R104BrineyBoat) is Route 104's OnFrame scene
// (VAR_BOARD_BRINEY_BOAT_ROUTE104_STATE 1); Mr. Briney's cottage reserves it with its warp here (the script starts
// on a black screen). Ch2's own entries: 5. Mr. Briney on Route 104 (Sapphire object 8, uid 108, FLAG_HIDE_MR_BRINEY_ROUTE104,
// data/story/ch2.json); his boat (object 7) has no Black 2 object (scenes/ch2_boat.inc). No text here.
#ifdef SCENE_ENTRIES
    ScriptEntry Ch2_R104None        // 5: Mr. Briney on Route 104 (Sapphire script 0x0)
#else
#include "scenes/ch2_boat.inc"
#define R104_BRINEY 108
#define R104_X 48                   // zone tile = Sapphire tile + (48, 240) (world.py offset of Route104)
#define R104_Z 240

Ch2_R104BrineyBoat:                 // Route104_EventScript_14EEA1 (lockall) + 14EFD5
    h_lock
    FadeInBlack                     // (the cottage's warp left the screen black)
    FadeWait
    h_applymovement R104_BRINEY, Mv_R104_BrineyBoard
    h_waitmovement
    h_removeobject R104_BRINEY, FLAG_HIDE_MR_BRINEY_ROUTE104
    h_applymovement 255, Mv_R104_PlayerBoard
    h_waitmovement
    ch2_hide_player
    h_setflag FLAG_HIDE_MR_BRINEY_BOAT_ROUTE104
    h_setvar VAR_BOARD_BRINEY_BOAT_ROUTE104_STATE, 0
    // to Dewford: the player lands on the boat's tile (12,8) (Dewford's arrival script 5, scenes/DewfordTown.inc)
    ch2_sail 465, 12 + 108, 8 + 420, 1, 5
    h_release

Ch2_R104None:
    VMHalt

    .balign 4, 0
Mv_R104_BrineyBoard:                // Route104_Movement_14F16C
    walk_down 2
    step_end
Mv_R104_PlayerBoard:                // Route104_Movement_14F162
    walk_left
    walk_down 2
    step_end
#endif
