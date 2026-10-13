// SealedChamber_OuterRoom (zone 215): cave_builder (converter/gen_caves.py): ladders and cracked floors as step triggers
// (Sapphire's step-on warps), simple people/signs. Story scripts: add them after a line "// ---- story" (this
// generator keeps everything from that line on and the entries you add: b2tools/story_merge.py) and number them
// after these entries.
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_trainers.h"  // ch6 (before hoenn_story.inc: its macros name trainers)
#include "hoenn_story.inc"  // ch6

    ScriptEntry Script_None
    ScriptEntry Story_SO_ABC   // 2: braille (5,6) (6,6) (4,6)  // story:
    ScriptEntry Story_SO_DEF   // 3: braille (11,6) (10,6) (12,6)  // story:
    ScriptEntry Story_SO_GHI   // 4: braille (5,9) (4,9) (6,9)  // story:
    ScriptEntry Story_SO_JKL   // 5: braille (11,9) (10,9) (12,9)  // story:
    ScriptEntry Story_SO_MNO   // 6: braille (5,12) (4,12) (6,12)  // story:
    ScriptEntry Story_SO_PQRS   // 7: braille (11,12) (10,12) (12,12)  // story:
    ScriptEntry Story_SO_TUV   // 8: braille (5,15) (4,15) (6,15)  // story:
    ScriptEntry Story_SO_WXYZ   // 9: braille (11,15) (10,15) (12,15)  // story:
    ScriptEntry Story_SO_Period   // 10: braille (16,6)  // story:
    ScriptEntry Story_SO_Comma   // 11: braille (16,9)  // story:
    ScriptEntry Story_SO_DigHere   // 12: braille (10,2)  // story:
    ScriptEntry Story_SO_DigHereSide   // 13: braille (9,2) (11,2)  // story:
    ScriptEntry Story_SO_DigSpot   // 14: step trigger (9..11,3): Dig  // story:
    ScriptEntry Story_SO_Init   // 15: zone init (0431)  // story:
    ScriptEntriesEnd

Script_None:
    VMHalt
    .balign 4, 0

// ---- story (chapter Ch12, ch6 agent: Sapphire data/maps/SealedChamber_OuterRoom/scripts.inc; generators keep everything
// from this line on). Braille: Black 2 has no braille font, so every braille message is shown as the plain text it spells
// (Sapphire's own strings, data/text/braille.inc, in sentence case); the signs are data/story/ch12.json (Sapphire's tiles).
// The Dig puzzle: Sapphire covers the door (10,2) with a wall (OnLoad setmetatile) until Dig is used at (9..11,3). Here
// the door's warp (index 0, tile (10,2)) is off the map until then (the chamber's doors work from the start, notes/CAVES.md),
// and the step trigger on (9..11,3) uses Dig for you when a Pokémon in the party knows it (scenes/ch12_lib.inc).
// Text: src/text/script/0274_room_SealedChamber_OuterRoom.txt.
#include "scenes/ch12_lib.inc"
#define T_ABC 0
#define T_DEF 1
#define T_GHI 2
#define T_JKL 3
#define T_MNO 4
#define T_PQRS 5
#define T_TUV 6
#define T_WXYZ 7
#define T_PERIOD 8
#define T_COMMA 9
#define T_DIGHERE 10
#define T_BIGHOLE 11
#define T_USEDDIG 12
#define SO_DOOR_WARP 0

    .macro so_braille n
    h_lock
    SEPlay SEQ_SE_MESSAGE
    h_msgbox_info \n
    h_closemessage
    h_release
    .endm
Story_SO_ABC:
    so_braille T_ABC
Story_SO_DEF:
    so_braille T_DEF
Story_SO_GHI:
    so_braille T_GHI
Story_SO_JKL:
    so_braille T_JKL
Story_SO_MNO:
    so_braille T_MNO
Story_SO_PQRS:
    so_braille T_PQRS
Story_SO_TUV:
    so_braille T_TUV
Story_SO_WXYZ:
    so_braille T_WXYZ
Story_SO_Period:
    so_braille T_PERIOD
Story_SO_Comma:
    so_braille T_COMMA
Story_SO_DigHere:                           // SealedChamber_OuterRoom_EventScript_15F1B8
    h_lock
    SEPlay SEQ_SE_MESSAGE
    h_goto_if_set FLAG_SYS_BRAILLE_DIG, L_SO_BigHole
    h_msgbox_info T_DIGHERE
    h_closemessage
    h_release
L_SO_BigHole:
    h_msgbox_info T_BIGHOLE                 // There is a big hole in the wall.
    h_closemessage
    h_release
Story_SO_DigHereSide:                       // SealedChamber_OuterRoom_EventScript_15F1D9
    so_braille T_DIGHERE

Story_SO_DigSpot:                           // ShouldDoBrailleDigEffect + DoBrailleDigEffect
    h_goto_if_set FLAG_SYS_BRAILLE_DIG, L_SO_NoDig
    h_dig_user CH12_DIG, L_SO_NoDig
    h_lock
    h_move_user_name
    h_msgbox_info T_USEDDIG                 // <Pokémon> used Dig!
    h_closemessage
    h_playse CH12_BANG                      // SE_BANG
    ObjInitWarpGPos SO_DOOR_WARP, 10, 0, 2  // the door opens
    h_setflag FLAG_SYS_BRAILLE_DIG
    h_release
L_SO_NoDig:
    VMHalt

Story_SO_Init:                              // OnResume (the dive warps: the dive patch's), OnTransition, OnLoad
    h_setflag FLAG_LANDMARK_SEALED_CHAMBER
#if defined(HOENN_TEST_CH6) || defined(HOENN_TEST_CH12)
    VMCall Test_Ch6Start                    // test builds only (scenes/ch6_test.inc)
#endif
    h_goto_if_set FLAG_SYS_BRAILLE_DIG, L_SO_InitDone
    ObjInitWarpGPos SO_DOOR_WARP, 0, 0, 0   // the door is covered
L_SO_InitDone:
    VMHalt
    .balign 4, 0
#include "scenes/ch6_test.inc"
