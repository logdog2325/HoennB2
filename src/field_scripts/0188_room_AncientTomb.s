// AncientTomb (zone 94): cave_builder (converter/gen_caves.py): ladders and cracked floors as step triggers
// (Sapphire's step-on warps), simple people/signs. Story scripts: add them after a line "// ---- story" (this
// generator keeps everything from that line on and the entries you add: b2tools/story_merge.py) and number them
// after these entries.
// (Sapphire's step-on warps), simple people/signs. Story scripts: add them after a line "// ---- story" (then this
// generator leaves the file alone) and number them after these entries.
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_key_items.h"  // ch6
#include "hoenn_trainers.h"  // ch6 (before hoenn_story.inc: its macros name trainers)
#include "hoenn_story.inc"  // ch6

    ScriptEntry Script_None
    ScriptEntry Story_AT_Registeel   // 2: object 1 (Registeel)  // story:
    ScriptEntry Story_AT_Braille   // 3: braille (8,20)  // story:
    ScriptEntry Story_AT_BrailleSide   // 4: braille (7,20) (9,20)  // story:
    ScriptEntry Story_AT_FlySpot   // 5: step trigger (8,25): Fly  // story:
    ScriptEntry Story_AT_Init   // 6: zone init (0189)  // story:
    ScriptEntriesEnd

Script_None:
    VMHalt
    .balign 4, 0

// ---- story (chapter Ch12, ch6 agent: Sapphire data/maps/AncientTomb/scripts.inc; generators keep everything from this line
// on). Registeel (data/story/ch12.json, uid 1, FLAG_HIDE_REGISTEEL), the braille signs, the Fly spot. Text:
// 0104_room_AncientTomb.txt. Sapphire covers the door (8,20) until Fly is used at (8,25) (the braille: aim to the sky in
// the middle): the door's warp (index 1) is off the map until then, and the step trigger uses Fly for you (scenes/
// ch12_lib.inc: the Feather Badge, then a Pokémon that knows Fly or HM02; Sapphire's flying animation is left out).
#include "scenes/ch12_lib.inc"
#define T_BRAILLE 0
#define T_BIGHOLE 1
#define T_USEDFLY 2
#define AT_DOOR_WARP 1

Story_AT_Registeel:                         // AncientTomb_EventScript_15F050 (Registeel Lv 40)
    h_regi_battle SPECIES_REGISTEEL, FLAG_HIDE_REGISTEEL, 1
Story_AT_Braille:                           // AncientTomb_EventScript_15F021
    h_lock
    SEPlay SEQ_SE_MESSAGE
    h_goto_if_set FLAG_SYS_BRAILLE_FLY, L_AT_BigHole
    h_msgbox_info T_BRAILLE
    h_closemessage
    h_release
L_AT_BigHole:
    h_msgbox_info T_BIGHOLE                 // There is a big hole in the wall.
    h_closemessage
    h_release
Story_AT_BrailleSide:                       // AncientTomb_EventScript_15F042
    h_lock
    SEPlay SEQ_SE_MESSAGE
    h_msgbox_info T_BRAILLE
    h_closemessage
    h_release
Story_AT_FlySpot:                           // ShouldDoBrailleFlyEffect + DoBrailleFlyEffect
    h_goto_if_set FLAG_SYS_BRAILLE_FLY, L_AT_NoUse
    h_field_move_user ITEM_HM02, 5, 19, L_AT_NoUse    // Fly: the Feather Badge; move 19; HM02
    h_lock
    h_move_user_name
    h_msgbox_info T_USEDFLY                 // <Pokémon> used Fly!
    h_closemessage
    h_playse CH12_BANG                      // SE_BANG
    ObjInitWarpGPos AT_DOOR_WARP, 8, 0, 20  // the door opens
    h_setflag FLAG_SYS_BRAILLE_FLY
    h_release
L_AT_NoUse:
    VMHalt
Story_AT_Init:                              // OnResume, OnLoad, OnTransition
    h_setflag FLAG_LANDMARK_ANCIENT_TOMB
#if defined(HOENN_TEST_CH6) || defined(HOENN_TEST_CH12)
    VMCall Test_Ch6Start                    // test builds only (scenes/ch6_test.inc)
#endif
    h_goto_if_set FLAG_SYS_BRAILLE_FLY, L_AT_InitDone
    ObjInitWarpGPos AT_DOOR_WARP, 0, 0, 0   // the door is covered
L_AT_InitDone:
    VMHalt
    .balign 4, 0
#include "scenes/ch6_test.inc"
