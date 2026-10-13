// AbandonedShip_Corridors_B1F (zone 73): ship_hideouts (b2tools/ship_hideouts_rooms.py): simple people, signs and Sapphire's
// furniture messages. Story scripts: add them after a line "// ---- story" (this generator keeps everything
// from that line on, and the entries you add: b2tools/story_merge.py) and number them after these entries.
// Messages: src/text/script/0083_room_AbandonedShip_Corridors_B1F.txt
// furniture messages. Story scripts: add them after a line "// ---- story" (then this generator leaves the file
// alone) and number them after these entries.
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_trainers.h"  // ch6 (before hoenn_story.inc: its macros name trainers)
#include "hoenn_story.inc"  // ch6

    ScriptEntry Script_1
    ScriptEntry Story_CB_StorageDoor   // 2: sign (11,4) the Storage Room door  // story:
    ScriptEntry Story_CB_Init   // 3: zone init (0147): the Storage Room locked  // story:
    ScriptEntriesEnd

Script_1:
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    ActorSetEyeToEye
    ParentActorMsg MSGFILE_SCRIPT, 0, 0, 0
    LastKeyWait
    ActorMsgClose
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt
    .balign 4, 0

// ---- story (chapter Ch6, ch6 agent: Sapphire data/maps/AbandonedShip_Corridors_B1F/scripts.inc; generators keep
// everything from this line on). Duncan: an eye-contact trainer (data/story/ch6.json); the dive spot is the dive
// patch's. The Storage Room door (Sapphire (11,4): a locked-door metatile until the Storage Key is used): its warp
// (index 5, zone tile (12,4)) leaves the map while FLAG_USED_STORAGE_KEY is clear; the door's sign (data/story/ch6.json)
// does Sapphire's script and puts the warp back. Lines 1-3 of the text file.
#define CB_DOOR_WARP 5
Story_CB_Init:                              // AbandonedShip_Corridors_B1F_OnLoad
#if defined(HOENN_TEST_CH6) || defined(HOENN_TEST_CH12)
    VMCall Test_Ch6Start                    // test builds only (scenes/ch6_test.inc)
#endif
    h_goto_if_set FLAG_USED_STORAGE_KEY, L_CB_InitDone
    ObjInitWarpGPos CB_DOOR_WARP, 0, 0, 0   // LockStorageRoom
L_CB_InitDone:
    VMHalt

Story_CB_StorageDoor:                       // AbandonedShip_Corridors_B1F_EventScript_StorageRoomDoor
    h_lock
    SEPlay SEQ_SE_MESSAGE
    h_goto_if_set FLAG_USED_STORAGE_KEY, L_CB_DoorOpen
    h_checkitem ITEM_STORAGE_KEY, 1, HLIB_TMP
    h_goto_if_eq HLIB_TMP, 0, L_CB_DoorLocked
    h_buffer_player
    h_msgbox_info 1                         // <player> inserted and turned the Storage Key. ...
    h_closemessage
    h_playse SEQ_SE_DECIDE1                 // SE_PIN [guess]
    h_removeitem ITEM_STORAGE_KEY, 1, HLIB_TMP
    h_setflag FLAG_USED_STORAGE_KEY
    ObjInitWarpGPos CB_DOOR_WARP, 12, 0, 4  // UnlockStorageRoom: the door's warp is back
    h_release
L_CB_DoorLocked:
    h_msgbox_info 2                         // The door is locked. ...
    h_closemessage
    h_release
L_CB_DoorOpen:
    h_msgbox_info 3                         // The door is open.
    h_closemessage
    h_release
    .balign 4, 0
#include "scenes/ch6_test.inc"
