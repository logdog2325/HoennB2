// DesertRuins (zone 116), Emerald build only (emerald_ch12_13, 2026-10-12): the Sapphire room's scripts
// (src/field_scripts/0232_room_DesertRuins.s, chapter Ch12 by the ch6 agent: cave_builder's head + its story) with
// Emerald's puzzle. The room, its braille signs, Regirock and the door are Sapphire's (data/story/ch12.json; Emerald's
// map differs by one block that does not change where you walk). Story script numbers are the shared file's.
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_key_items.h"  // ch6
#include "hoenn_trainers.h"  // ch6 (before hoenn_story.inc: its macros name trainers)
#include "hoenn_story.inc"  // ch6

    ScriptEntry Script_None
    ScriptEntry Story_DR_Regirock   // 2: object 1 (Regirock)  // story:
    ScriptEntry Story_DR_Braille   // 3: braille (8,20)  // story:
    ScriptEntry Story_DR_BrailleSide   // 4: braille (7,20) (9,20)  // story:
    ScriptEntry Story_DR_RockSmashSpot   // 5: step trigger (5..7,23): Rock Smash (Emerald; Sapphire: Strength at (9..11,23))  // story:
    ScriptEntry Story_DR_Init   // 6: zone init (0233)  // story:
    ScriptEntriesEnd

Script_None:
    VMHalt
    .balign 4, 0

// ---- story (chapter Ch12; Emerald: pokeemerald data/maps/DesertRuins/scripts.inc + src/braille_puzzles.c). Regirock
// (data/story/ch12.json, uid 1, FLAG_HIDE_REGIROCK), the braille signs, the Rock Smash spot.
// Emerald covers the door (8,20) until Rock Smash is used at (5..7,23) (ShouldDoBrailleRegirockEffect; the braille: left,
// left, down, down, then use Rock Smash: from the braille's front (8,21)); FLAG_SYS_REGIROCK_PUZZLE_COMPLETED is this port's
// FLAG_SYS_BRAILLE_STRENGTH id (Emerald's flag in its place). Here the door's warp (index 1) is off the map until then,
// and the step trigger (ch12.json's Strength trigger moved there in Emerald: at_emerald) uses Rock Smash for you
// (scenes/ch12_lib.inc: the Dynamo Badge, then a Pokémon that knows it or TM94, hm_free's rule for Rock Smash).
// Text: src/text/script/emerald/0135_room_DesertRuins.txt (Emerald's braille, "used Rock Smash!").
#include "scenes/ch12_lib.inc"
#define FLAG_SYS_REGIROCK_PUZZLE_COMPLETED FLAG_SYS_BRAILLE_STRENGTH
#define T_BRAILLE 0
#define T_BIGHOLE 1
#define T_USEDROCKSMASH 2
#define DR_DOOR_WARP 1

Story_DR_Regirock:                          // DesertRuins_EventScript_Regirock (Regirock Lv 40)
    h_regi_battle SPECIES_REGIROCK, FLAG_HIDE_REGIROCK, 1
Story_DR_Braille:                           // DesertRuins_EventScript_CaveEntranceMiddle
    h_lock
    SEPlay SEQ_SE_MESSAGE
    h_goto_if_set FLAG_SYS_REGIROCK_PUZZLE_COMPLETED, L_DR_BigHole
    h_msgbox_info T_BRAILLE                 // braillemsgbox DesertRuins_Braille_UseRockSmash
    h_closemessage
    h_release
L_DR_BigHole:
    h_msgbox_info T_BIGHOLE                 // gText_BigHoleInTheWall
    h_closemessage
    h_release
Story_DR_BrailleSide:                       // DesertRuins_EventScript_CaveEntranceSide
    h_lock
    SEPlay SEQ_SE_MESSAGE
    h_msgbox_info T_BRAILLE
    h_closemessage
    h_release
Story_DR_RockSmashSpot:                     // ShouldDoBrailleRegirockEffect + DoBrailleRegirockEffect (fldeff_rocksmash.c)
    h_goto_if_set FLAG_SYS_REGIROCK_PUZZLE_COMPLETED, L_DR_NoUse
    h_field_move_user ITEM_TM94, 2, MOVE_ROCK_SMASH, L_DR_NoUse    // the Dynamo Badge; TM94 (hm_free.py)
    h_lock
    h_move_user_name
    h_msgbox_info T_USEDROCKSMASH           // <Pokémon> used Rock Smash!
    h_closemessage
    h_playse CH12_BANG                      // PlaySE(SE_BANG)
    ObjInitWarpGPos DR_DOOR_WARP, 8, 0, 20  // the door opens (the setmetatile lines)
    h_setflag FLAG_SYS_REGIROCK_PUZZLE_COMPLETED
    h_release
L_DR_NoUse:
    VMHalt
Story_DR_Init:                              // OnResume (FLAG_SYS_CTRL_OBJ_DELETE: gone with the battle's object), OnLoad, OnTransition
    h_setflag FLAG_LANDMARK_DESERT_RUINS
#if defined(HOENN_TEST_CH6) || defined(HOENN_TEST_CH12)
    VMCall Test_Ch6Start                    // test builds only (scenes/ch6_test.inc)
#endif
    h_goto_if_set FLAG_SYS_REGIROCK_PUZZLE_COMPLETED, L_DR_InitDone
    ObjInitWarpGPos DR_DOOR_WARP, 0, 0, 0   // the door is covered (DesertRuins_EventScript_HideRegiEntrance)
L_DR_InitDone:
    VMHalt
    .balign 4, 0
#include "scenes/ch6_test.inc"
