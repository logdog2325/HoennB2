// AbandonedShip_Deck (zone 74): ship_hideouts (b2tools/ship_hideouts_rooms.py): simple people, signs and Sapphire's
// furniture messages. Story scripts: add them after a line "// ---- story" (this generator keeps everything
// from that line on, and the entries you add: b2tools/story_merge.py) and number them after these entries.
// furniture messages. Story scripts: add them after a line "// ---- story" (then this generator leaves the file
// alone) and number them after these entries.
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_trainers.h"  // ch6 (before hoenn_story.inc: its macros name trainers)
#include "hoenn_story.inc"  // ch6

    ScriptEntry Script_None
    ScriptEntry Story_DK_Init   // 2: zone init (0149)  // story:
    ScriptEntriesEnd

Script_None:
    VMHalt
    .balign 4, 0

// ---- story (chapter Ch6, ch6 agent: Sapphire data/maps/AbandonedShip_Deck/scripts.inc; generators keep everything
// from this line on).
Story_DK_Init:                              // AbandonedShip_Deck_OnTransition
#if defined(HOENN_TEST_CH6) || defined(HOENN_TEST_CH12)
    VMCall Test_Ch6Start                    // test builds only (scenes/ch6_test.inc)
#endif
    FlagSet FLAG_LANDMARK_ABANDONED_SHIP
    VMHalt
    .balign 4, 0
#include "scenes/ch6_test.inc"
