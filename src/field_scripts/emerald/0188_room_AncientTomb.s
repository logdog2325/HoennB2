// AncientTomb (zone 94), Emerald build only (emerald_ch12_13, 2026-10-12): the Sapphire room's scripts
// (src/field_scripts/0188_room_AncientTomb.s, chapter Ch12 by the ch6 agent: cave_builder's head + its story) with
// Emerald's puzzle. The room, its braille signs, Registeel, the door and the step trigger at (8,25) are Sapphire's
// (data/story/ch12.json; Emerald's map differs by one block that does not change where you walk). Story script
// numbers are the shared file's.
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_key_items.h"  // ch6
#include "hoenn_trainers.h"  // ch6 (before hoenn_story.inc: its macros name trainers)
#include "hoenn_story.inc"  // ch6

    ScriptEntry Script_None
    ScriptEntry Story_AT_Registeel   // 2: object 1 (Registeel)  // story:
    ScriptEntry Story_AT_Braille   // 3: braille (8,20)  // story:
    ScriptEntry Story_AT_BrailleSide   // 4: braille (7,20) (9,20)  // story:
    ScriptEntry Story_AT_FlashSpot   // 5: step trigger (8,25): Flash (Emerald; Sapphire: Fly at the same tile)  // story:
    ScriptEntry Story_AT_Init   // 6: zone init (0189)  // story:
    ScriptEntriesEnd

Script_None:
    VMHalt
    .balign 4, 0

// ---- story (chapter Ch12; Emerald: pokeemerald data/maps/AncientTomb/scripts.inc + src/braille_puzzles.c). Registeel
// (data/story/ch12.json, uid 1, FLAG_HIDE_REGISTEEL), the braille signs, the Flash spot.
// Emerald covers the door (8,20) until Flash is used at (8,25) (ShouldDoBrailleRegisteelEffect from fldeff_flash.c; the
// braille: "Those who inherit our will, shine in the middle."); FLAG_SYS_REGISTEEL_PUZZLE_COMPLETED is this port's
// FLAG_SYS_BRAILLE_FLY id (Emerald's flag in its place). Here the door's warp (index 1) is off the map until then, and
// the step trigger uses Flash for you (scenes/ch12_lib.inc: the Knuckle Badge, then a Pokémon that knows it or TM70,
// hm_free's rule for Flash). Text: src/text/script/emerald/0104_room_AncientTomb.txt (Emerald's braille, "used Flash!").
#include "scenes/ch12_lib.inc"
#define FLAG_SYS_REGISTEEL_PUZZLE_COMPLETED FLAG_SYS_BRAILLE_FLY
#define T_BRAILLE 0
#define T_BIGHOLE 1
#define T_USEDFLASH 2
#define AT_DOOR_WARP 1

Story_AT_Registeel:                         // AncientTomb_EventScript_Registeel (Registeel Lv 40)
    h_regi_battle SPECIES_REGISTEEL, FLAG_HIDE_REGISTEEL, 1
Story_AT_Braille:                           // AncientTomb_EventScript_CaveEntranceMiddle
    h_lock
    SEPlay SEQ_SE_MESSAGE
    h_goto_if_set FLAG_SYS_REGISTEEL_PUZZLE_COMPLETED, L_AT_BigHole
    h_msgbox_info T_BRAILLE                 // braillemsgbox AncientTomb_Braille_ShineInTheMiddle
    h_closemessage
    h_release
L_AT_BigHole:
    h_msgbox_info T_BIGHOLE                 // gText_BigHoleInTheWall
    h_closemessage
    h_release
Story_AT_BrailleSide:                       // AncientTomb_EventScript_CaveEntranceSide
    h_lock
    SEPlay SEQ_SE_MESSAGE
    h_msgbox_info T_BRAILLE
    h_closemessage
    h_release
Story_AT_FlashSpot:                         // ShouldDoBrailleRegisteelEffect + DoBrailleRegisteelEffect
    h_goto_if_set FLAG_SYS_REGISTEEL_PUZZLE_COMPLETED, L_AT_NoUse
    h_field_move_user ITEM_TM70, 1, MOVE_FLASH, L_AT_NoUse    // the Knuckle Badge; TM70 (hm_free.py)
    h_lock
    h_move_user_name
    h_msgbox_info T_USEDFLASH               // <Pokémon> used Flash!
    h_closemessage
    h_playse CH12_BANG                      // PlaySE(SE_BANG)
    ObjInitWarpGPos AT_DOOR_WARP, 8, 0, 20  // the door opens (the setmetatile lines)
    h_setflag FLAG_SYS_REGISTEEL_PUZZLE_COMPLETED
    h_release
L_AT_NoUse:
    VMHalt
Story_AT_Init:                              // OnResume, OnLoad, OnTransition
    h_setflag FLAG_LANDMARK_ANCIENT_TOMB
#if defined(HOENN_TEST_CH6) || defined(HOENN_TEST_CH12)
    VMCall Test_Ch6Start                    // test builds only (scenes/ch6_test.inc)
#endif
    h_goto_if_set FLAG_SYS_REGISTEEL_PUZZLE_COMPLETED, L_AT_InitDone
    ObjInitWarpGPos AT_DOOR_WARP, 0, 0, 0   // the door is covered (AncientTomb_EventScript_HideRegiEntrance)
L_AT_InitDone:
    VMHalt
    .balign 4, 0
#include "scenes/ch6_test.inc"
