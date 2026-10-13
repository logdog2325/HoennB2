// DesertRuins (zone 116): cave_builder (converter/gen_caves.py): ladders and cracked floors as step triggers
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
    ScriptEntry Story_DR_Regirock   // 2: object 1 (Regirock)  // story:
    ScriptEntry Story_DR_Braille   // 3: braille (8,20)  // story:
    ScriptEntry Story_DR_BrailleSide   // 4: braille (7,20) (9,20)  // story:
    ScriptEntry Story_DR_StrengthSpot   // 5: step trigger (9..11,23): Strength  // story:
    ScriptEntry Story_DR_Init   // 6: zone init (0233)  // story:
    ScriptEntriesEnd

Script_None:
    VMHalt
    .balign 4, 0

// ---- story (chapter Ch12, ch6 agent: Sapphire data/maps/DesertRuins/scripts.inc; generators keep everything from this
// line on). Regirock (data/story/ch12.json, uid 1, FLAG_HIDE_REGIROCK), the braille signs, the Strength spot.
// Sapphire covers the door (8,20) until Strength is used at (9..11,23) (the braille: right, right, down, down, then use
// Strength): here the door's warp (index 1) is off the map until then, and the step trigger uses Strength for you
// (scenes/ch12_lib.inc: the badge, then a Pokémon that knows it or HM04). Text: 0135_room_DesertRuins.txt.
#include "scenes/ch12_lib.inc"
#define T_BRAILLE 0
#define T_BIGHOLE 1
#define T_USEDSTRENGTH 2
#define DR_DOOR_WARP 1

Story_DR_Regirock:                          // DesertRuins_EventScript_15CB85 (Regirock Lv 40)
    h_regi_battle SPECIES_REGIROCK, FLAG_HIDE_REGIROCK, 1
Story_DR_Braille:                           // DesertRuins_EventScript_15CB56
    h_lock
    SEPlay SEQ_SE_MESSAGE
    h_goto_if_set FLAG_SYS_BRAILLE_STRENGTH, L_DR_BigHole
    h_msgbox_info T_BRAILLE
    h_closemessage
    h_release
L_DR_BigHole:
    h_msgbox_info T_BIGHOLE                 // There is a big hole in the wall.
    h_closemessage
    h_release
Story_DR_BrailleSide:                       // DesertRuins_EventScript_15CB77
    h_lock
    SEPlay SEQ_SE_MESSAGE
    h_msgbox_info T_BRAILLE
    h_closemessage
    h_release
Story_DR_StrengthSpot:                      // ShouldDoBrailleStrengthEffect + DoBrailleStrengthEffect
    h_goto_if_set FLAG_SYS_BRAILLE_STRENGTH, L_DR_NoUse
    h_field_move_user ITEM_HM04, 3, 70, L_DR_NoUse    // Strength: the Heat Badge; move 70; HM04
    h_lock
    h_move_user_name
    h_msgbox_info T_USEDSTRENGTH            // <Pokémon> used Strength!
    h_closemessage
    h_playse CH12_BANG                      // SE_BANG
    ObjInitWarpGPos DR_DOOR_WARP, 8, 0, 20  // the door opens
    h_setflag FLAG_SYS_BRAILLE_STRENGTH
    h_release
L_DR_NoUse:
    VMHalt
Story_DR_Init:                              // OnResume (FLAG_SYS_CTRL_OBJ_DELETE: gone with the battle's object), OnLoad, OnTransition
    h_setflag FLAG_LANDMARK_DESERT_RUINS
#if defined(HOENN_TEST_CH6) || defined(HOENN_TEST_CH12)
    VMCall Test_Ch6Start                    // test builds only (scenes/ch6_test.inc)
#endif
    h_goto_if_set FLAG_SYS_BRAILLE_STRENGTH, L_DR_InitDone
    ObjInitWarpGPos DR_DOOR_WARP, 0, 0, 0   // the door is covered
L_DR_InitDone:
    VMHalt
    .balign 4, 0
#include "scenes/ch6_test.inc"
