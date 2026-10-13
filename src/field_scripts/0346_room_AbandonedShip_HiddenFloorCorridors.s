// AbandonedShip_HiddenFloorCorridors (zone 173): ship_hideouts (b2tools/ship_hideouts_rooms.py): simple people, signs and Sapphire's
// furniture messages. Story scripts: add them after a line "// ---- story" (this generator keeps everything
// from that line on, and the entries you add: b2tools/story_merge.py) and number them after these entries.
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_key_items.h"  // ch6
#include "hoenn_trainers.h"  // ch6 (before hoenn_story.inc: its macros name trainers)
#include "hoenn_story.inc"  // ch6

    ScriptEntry Script_None
    ScriptEntry Story_HC_Room1Door   // 2: sign (3,8)  // story:
    ScriptEntry Story_HC_Room2Door   // 3: sign (6,8)  // story:
    ScriptEntry Story_HC_Room4Door   // 4: sign (3,4)  // story:
    ScriptEntry Story_HC_Room6Door   // 5: sign (9,4)  // story:
    ScriptEntry Story_HC_Init   // 6: zone init (0347): the locked doors  // story:
    ScriptEntriesEnd

Script_None:
    VMHalt
    .balign 4, 0

// ---- story (chapter Ch6, ch6 agent: Sapphire data/maps/AbandonedShip_HiddenFloorCorridors/scripts.inc; generators
// keep everything from this line on). Rooms 1, 2, 4, 6 are locked until their Key (a hidden item in the rooms beyond)
// is used: their warps (indices 0, 1, 3, 5; zone tiles (4,8), (7,8), (4,3), (10,3)) leave the map while the key flag
// is clear (Sapphire: locked-door metatiles); the door signs (data/story/ch6.json) do Sapphire's scripts and put the
// warp back. Text: src/text/script/0231_room_AbandonedShip_HiddenFloorCorridors.txt lines 0-5.
Story_HC_Init:                              // AbandonedShip_HiddenFloorCorridors_OnLoad
#if defined(HOENN_TEST_CH6) || defined(HOENN_TEST_CH12)
    VMCall Test_Ch6Start                    // test builds only (scenes/ch6_test.inc)
#endif
    h_goto_if_set FLAG_USED_ROOM_1_KEY, L_HC_Init2
    ObjInitWarpGPos 0, 0, 0, 0
L_HC_Init2:
    h_goto_if_set FLAG_USED_ROOM_2_KEY, L_HC_Init4
    ObjInitWarpGPos 1, 0, 0, 0
L_HC_Init4:
    h_goto_if_set FLAG_USED_ROOM_4_KEY, L_HC_Init6
    ObjInitWarpGPos 3, 0, 0, 0
L_HC_Init6:
    h_goto_if_set FLAG_USED_ROOM_6_KEY, L_HC_InitDone
    ObjInitWarpGPos 5, 0, 0, 0
L_HC_InitDone:
    VMHalt

    .macro hc_door flag, key, locked, warp, x, z
    h_lock
    SEPlay SEQ_SE_MESSAGE
    h_goto_if_set \flag, L_HC_DoorOpen
    h_checkitem \key, 1, HLIB_TMP
    h_goto_if_eq HLIB_TMP, 0, .Lhc_locked\@
    h_buffer_player
    h_msgbox_info 0                         // <player> inserted and turned the Key. ...
    h_closemessage
    h_playse SEQ_SE_DECIDE1                 // SE_PIN [guess]
    h_removeitem \key, 1, HLIB_TMP
    h_setflag \flag
    ObjInitWarpGPos \warp, \x, 0, \z        // UnlockRoomN: the door's warp is back
    h_release
.Lhc_locked\@:
    h_msgbox_info \locked                   // The door is locked. "Rm. N" is painted on the door.
    h_closemessage
    h_release
    .endm
Story_HC_Room1Door:
    hc_door FLAG_USED_ROOM_1_KEY, ITEM_ROOM_1_KEY, 1, 0, 4, 8
Story_HC_Room2Door:
    hc_door FLAG_USED_ROOM_2_KEY, ITEM_ROOM_2_KEY, 2, 1, 7, 8
Story_HC_Room4Door:
    hc_door FLAG_USED_ROOM_4_KEY, ITEM_ROOM_4_KEY, 3, 3, 4, 3
Story_HC_Room6Door:
    hc_door FLAG_USED_ROOM_6_KEY, ITEM_ROOM_6_KEY, 4, 5, 10, 3
L_HC_DoorOpen:                              // AbandonedShip_HiddenFloorCorridors_EventScript_TheDoorIsOpen
    h_msgbox_info 5                         // The door is open.
    h_closemessage
    h_release
    .balign 4, 0
#include "scenes/ch6_test.inc"
