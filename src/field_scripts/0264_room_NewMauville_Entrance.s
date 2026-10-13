// NewMauville_Entrance (zone 132): cave_builder (converter/gen_caves.py): ladders and cracked floors as step triggers
// (Sapphire's step-on warps), simple people/signs. Story scripts: add them after a line "// ---- story" (this
// generator keeps everything from that line on and the entries you add: b2tools/story_merge.py) and number them
// after these entries.
// (Sapphire's step-on warps), simple people/signs. Story scripts: add them after a line "// ---- story" (then this
// generator leaves the file alone) and number them after these entries.
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_trainers.h"  // ch6 (before hoenn_story.inc: its macros name trainers)
#include "hoenn_story.inc"  // ch6

    ScriptEntry Script_None
    ScriptEntry Story_NE_Door   // 2: step trigger (4,2) VAR_NEW_MAUVILLE_STATE 0  // story:
    ScriptEntry Story_NE_Init   // 3: zone init (0265)  // story:
    ScriptEntriesEnd

Script_None:
    VMHalt
    .balign 4, 0

// ---- story (chapter Ch6, ch6 agent: Sapphire data/maps/NewMauville_Entrance/scripts.inc; generators keep everything
// from this line on). The door to the inside (Sapphire (4,0)-(5,1): closed-door metatiles until the Basement Key):
// its warp (index 1, tile (4,1)) leaves the map while VAR_NEW_MAUVILLE_STATE is 0; the step trigger in front of it
// (data/story/ch6.json) does Sapphire's script and puts the warp back. Text: src/text/script/
// 0151_room_NewMauville_Entrance.txt lines 0-2. The door model itself does not change (Sapphire swaps its metatiles).
#define NE_DOOR_WARP 1
Story_NE_Init:                              // NewMauville_Entrance OnTransition + OnLoad
#if defined(HOENN_TEST_CH6) || defined(HOENN_TEST_CH12)
    VMCall Test_Ch6Start                    // test builds only (scenes/ch6_test.inc)
#endif
    FlagSet FLAG_LANDMARK_NEW_MAUVILLE
    h_goto_if_ne VAR_NEW_MAUVILLE_STATE, 0, L_NE_InitDone
    ObjInitWarpGPos NE_DOOR_WARP, 0, 0, 0   // the door is closed
L_NE_InitDone:
    VMHalt

Story_NE_Door:                              // NewMauville_Entrance_EventScript_15E4DC
    h_lock
    h_applymovement 255, Common_Movement_WalkInPlaceFastestUp
    h_waitmovement
    h_msgbox_info 0                         // The door is closed.
    h_checkitem ITEM_BASEMENT_KEY, 1, HLIB_TMP
    h_goto_if_eq HLIB_TMP, 0, L_NE_Done
    SystemMsg 1, 2                          // Use the Basement Key?
    YesNoWin HLIB_TMP
    h_goto_if_no HLIB_TMP, L_NE_Done
    h_buffer_player
    h_msgbox_info 2                         // <player> used the Basement Key. The door opened!
    h_closemessage
    ObjInitWarpGPos NE_DOOR_WARP, 4, 0, 1   // the door is open
    h_playse SEQ_SE_KAIDAN                  // SE_BANG [guess]
    h_setvar VAR_NEW_MAUVILLE_STATE, 1
L_NE_Done:
    h_closemessage
    h_release
    .balign 4, 0
#include "common/movement.inc"
#include "scenes/ch6_test.inc"
