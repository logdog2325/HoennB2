// IslandCave (zone 127): cave_builder (converter/gen_caves.py): ladders and cracked floors as step triggers
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
    ScriptEntry Story_IC_Regice   // 2: object 1 (Regice)  // story:
    ScriptEntry Story_IC_Braille   // 3: braille (8,20)  // story:
    ScriptEntry Story_IC_BrailleSide   // 4: braille (7,20) (9,20)  // story:
    ScriptEntry Story_IC_Init   // 5: zone init (0255)  // story:
    ScriptEntriesEnd

Script_None:
    VMHalt
    .balign 4, 0

// ---- story (chapter Ch12, ch6 agent: Sapphire data/maps/IslandCave/scripts.inc; generators keep everything from this line
// on). Regice (data/story/ch12.json, uid 1, FLAG_HIDE_REGICE), the braille signs. Text: 0146_room_IslandCave.txt.
// Sapphire covers the door (8,20) until you read the braille and then do nothing for two minutes (DoBrailleWait: 7200 frames;
// any button press erases the message and starts over). Here the door's warp (index 1) is off the map until then; the
// message stays up while the script waits two minutes (VMSleep 3600 at 30 fps); Black 2 has no way to read a button
// during a script, so the wait cannot be interrupted: it always succeeds.
#include "scenes/ch12_lib.inc"
#define T_BRAILLE 0
#define T_BIGHOLE 1
#define IC_DOOR_WARP 1

Story_IC_Regice:                            // IslandCave_EventScript_15EF9D (Regice Lv 40)
    h_regi_battle SPECIES_REGICE, FLAG_HIDE_REGICE, 1
Story_IC_Braille:                           // IslandCave_EventScript_15EF59
    h_lock
    SEPlay SEQ_SE_MESSAGE
    h_goto_if_set FLAG_SYS_BRAILLE_WAIT, L_IC_BigHole
    SystemMsg T_BRAILLE, 2                  // braillemessage (stays up during the wait)
    VMSleep 3600                            // special DoBrailleWait: two minutes
    MsgWinCloseAll
    VMSleep 15
    h_playse CH12_BANG                      // S_OpenRegiceChamber: SE_BANG
    ObjInitWarpGPos IC_DOOR_WARP, 8, 0, 20  // the door opens
    h_setflag FLAG_SYS_BRAILLE_WAIT
    h_release
L_IC_BigHole:
    h_msgbox_info T_BIGHOLE                 // There is a big hole in the wall.
    h_closemessage
    h_release
Story_IC_BrailleSide:                       // IslandCave_EventScript_15EF7C
    h_lock
    SEPlay SEQ_SE_MESSAGE
    h_goto_if_set FLAG_SYS_BRAILLE_WAIT, L_IC_SideDone
    SystemMsg T_BRAILLE, 2
    VMSleep 3600
    MsgWinCloseAll
    VMSleep 15
    h_playse CH12_BANG
    ObjInitWarpGPos IC_DOOR_WARP, 8, 0, 20
    h_setflag FLAG_SYS_BRAILLE_WAIT
    h_release
L_IC_SideDone:
    h_msgbox_info T_BRAILLE                 // (Sapphire: the braille again, no wait)
    h_closemessage
    h_release
Story_IC_Init:                              // OnResume, OnLoad, OnTransition
    h_setflag FLAG_LANDMARK_ISLAND_CAVE
#if defined(HOENN_TEST_CH6) || defined(HOENN_TEST_CH12)
    VMCall Test_Ch6Start                    // test builds only (scenes/ch6_test.inc)
#endif
    h_goto_if_set FLAG_SYS_BRAILLE_WAIT, L_IC_InitDone
    ObjInitWarpGPos IC_DOOR_WARP, 0, 0, 0   // the door is covered
L_IC_InitDone:
    VMHalt
    .balign 4, 0
#include "scenes/ch6_test.inc"
