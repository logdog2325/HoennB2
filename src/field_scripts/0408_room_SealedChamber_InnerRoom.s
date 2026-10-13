// SealedChamber_InnerRoom (zone 204): cave_builder (converter/gen_caves.py): ladders and cracked floors as step triggers
// (Sapphire's step-on warps), simple people/signs. Story scripts: add them after a line "// ---- story" (this
// generator keeps everything from that line on and the entries you add: b2tools/story_merge.py) and number them
// after these entries.
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_trainers.h"  // ch6 (before hoenn_story.inc: its macros name trainers)
#include "hoenn_story.inc"  // ch6
#include "scenes/ch12_lib.inc"  // ch6

    ScriptEntry Script_None
    ScriptEntry Story_SI_Relicanth   // 2: braille (10,4) (9,4) (11,4): the Relicanth / Wailord check  // story:
    ScriptEntry Story_SI_Lived   // 3: braille (6,8)  // story:
    ScriptEntry Story_SI_Owe   // 4: braille (14,8)  // story:
    ScriptEntry Story_SI_Sealed   // 5: braille (4,13)  // story:
    ScriptEntry Story_SI_Feared   // 6: braille (16,13)  // story:
    ScriptEntry Story_SI_Courage   // 7: braille (6,18)  // story:
    ScriptEntry Story_SI_Door   // 8: braille (14,18)  // story:
    ScriptEntry Story_SI_Init   // 9: zone init (0409)  // story:
    ScriptEntriesEnd

Script_None:
    VMHalt
    .balign 4, 0

// ---- story (chapter Ch12, ch6 agent: Sapphire data/maps/SealedChamber_InnerRoom/scripts.inc; generators keep everything
// from this line on). Braille signs: data/story/ch12.json. Text: src/text/script/0263_room_SealedChamber_InnerRoom.txt.
// The seal: Sapphire opens the three Regi chambers (Route 105's Island Cave, Route 111's Desert Ruins, Route 120's Ancient
// Tomb) when you read the braille at the back wall with Relicanth first and Wailord last in the party (FLAG_REGI_DOORS_OPENED).
// Black 2: the Island Cave's door on Route 105 is blocked until the flag (scenes/Route105.inc). The three chambers'
// own doors open by their own puzzles. CheckRelicanthWailord = party slot 0 Relicanth and the last slot Wailord (an Egg
// counts as its species, as Sapphire's MON_DATA_SPECIES2 does not: eggs are "Bad Egg" species 0 there).
// The shaking (DoSealedChamberShakingEffect1/2): Black 2's own camera shakes (EvCameraShake, as its script 1269).
#define T_FIRST 0
#define T_LIVED 1
#define T_OWE 2
#define T_SEALED 3
#define T_FEARED 4
#define T_COURAGE 5
#define T_OPENDOOR 6
#define T_SOUND 7
#define SI_SPECIES 0x8036
#define SI_LAST 0x8037

    .macro si_braille n
    h_lock
    SEPlay SEQ_SE_MESSAGE
    h_msgbox_info \n
    h_closemessage
    h_release
    .endm
Story_SI_Relicanth:                         // SealedChamber_InnerRoom_EventScript_15F1E8
    h_lock
    SEPlay SEQ_SE_MESSAGE
    h_msgbox_info T_FIRST                   // First comes Relicanth. Last comes Wailord.
    h_closemessage
    h_goto_if_set FLAG_REGI_DOORS_OPENED, L_SI_Done
#ifdef HOENN_EMERALD                        // (emerald_ch12_13) Emerald flipped it (braille_puzzles.c CheckRelicanthWailord:
#define SI_FIRST_SPECIES SPECIES_WAILORD    // "First comes Wailord. Last comes Relicanth.", the Emerald text overlay's row 0)
#define SI_LAST_SPECIES SPECIES_RELICANTH
#else
#define SI_FIRST_SPECIES SPECIES_RELICANTH
#define SI_LAST_SPECIES SPECIES_WAILORD
#endif
    PokePartyGetSpecies SI_SPECIES, 0       // CheckRelicanthWailord
    h_goto_if_ne SI_SPECIES, SI_FIRST_SPECIES, L_SI_Done
    h_getpartysize SI_LAST
    h_subvar SI_LAST, 1
    PokePartyGetSpecies SI_SPECIES, SI_LAST
    h_goto_if_ne SI_SPECIES, SI_LAST_SPECIES, L_SI_Done
    BGMFadeOut 30                           // fadeoutbgm 0
    SEPlay SEQ_SE_FLD_126                   // SE_TRUCK_MOVE [guess]
    EvCameraShake 10, 0, 3, 20, 1, 0, 1, 5  // DoSealedChamberShakingEffect1 (the long shake)
    SEWait
    h_delay 40
    EvCameraShake 5, 0, 3, 8, 1, 0, 1, 5    // DoSealedChamberShakingEffect2
    VMSleep 10
    h_playse CH12_BANG                      // SE_DOOR [guess]
    h_delay 40
    EvCameraShake 5, 0, 3, 8, 1, 0, 1, 5
    VMSleep 10
    h_playse CH12_BANG
    h_delay 40
    EvCameraShake 5, 0, 3, 8, 1, 0, 1, 5
    VMSleep 10
    h_playse CH12_BANG
    h_delay 40
    h_msgbox_info T_SOUND                   // It sounded as if a door opened somewhere far away.
    h_closemessage
    h_fadedefaultbgm                        // fadeinbgm 0
    h_setflag FLAG_REGI_DOORS_OPENED
L_SI_Done:
    h_release
Story_SI_Lived:
    si_braille T_LIVED
Story_SI_Owe:
    si_braille T_OWE
Story_SI_Sealed:
    si_braille T_SEALED
Story_SI_Feared:
    si_braille T_FEARED
Story_SI_Courage:
    si_braille T_COURAGE
Story_SI_Door:
    si_braille T_OPENDOOR
Story_SI_Init:
#if defined(HOENN_TEST_CH6) || defined(HOENN_TEST_CH12)
    VMCall Test_Ch6Start                    // test builds only (scenes/ch6_test.inc)
#endif
    VMHalt
    .balign 4, 0
#include "scenes/ch6_test.inc"
