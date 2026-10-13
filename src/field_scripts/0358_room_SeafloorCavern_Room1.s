// SeafloorCavern_Room1 (zone 179): cave_builder (converter/gen_caves.py): ladders and cracked floors as step triggers
// (Sapphire's step-on warps), simple people/signs. Story scripts: add them after a line "// ---- story" (this
// generator keeps everything from that line on and the entries you add: b2tools/story_merge.py) and number them
// after these entries.
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_trainers.h"  // ch10
#include "hoenn_key_items.h"  // ch10
#include "hoenn_story.inc"  // ch10

    ScriptEntry Script_None
    ScriptEntry R1_Init  // 2: zone init: the test start only (Sapphire's ON_TRANSITION: SetupEvilTeamGfxIds)  // story:
    ScriptEntriesEnd

Script_None:
    VMHalt
    .balign 4, 0

// ---- story (chapter Ch10, ch10 agent 2026-10-07; Sapphire data/maps/SeafloorCavern_Room1/scripts.inc; generators keep everything from
// this line on; entries above marked "// story:"). Messages: -
// Two Aqua grunts (data/story/ch10.json: Black 2 eye-contact trainers, global script 3000 + trainer id, hidden by FLAG_HIDE_EVIL_TEAM_GRUNTS_SEAFLOOR_CAVERN). The zone init is the test start only.
#include "scenes/ch10_lib.inc"
R1_Init:
#ifdef HOENN_TEST_CH10
    VMCall Test_Ch10Start               // test builds only (scenes/ch10_test.inc)
#endif
    VMHalt
#ifdef HOENN_TEST_CH10
#include "scenes/ch10_test.inc"
#endif
    .balign 4, 0
