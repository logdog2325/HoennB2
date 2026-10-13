// NavelRock_Up4 (zone 270): cave_builder (converter/gen_caves.py): ladders and cracked floors as step triggers
// (Sapphire's step-on warps), simple people/signs. Story scripts: add them after a line "// ---- story" (this
// generator keeps everything from that line on and the entries you add: b2tools/story_merge.py) and number them
// after these entries.
#include "asm/field_script.inc"
#include "hoenn.h"

    ScriptEntry Script_1
    ScriptEntry EV_NU4_LadderToTop      // 2: ladder up (5,5) -> NavelRock_Top warp 0 (step trigger, data/story/events.json)  // story:
    ScriptEntriesEnd

Script_1:                                      // ladder down (3,3) -> NavelRock_Up3 warp 1 (3,3)
    ActorsPauseAll
    SEPlay SEQ_SE_KAIDAN
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    MapChangeCore 269, 3, 0, 3, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt
    .balign 4, 0

// ---- story (events agent, 2026-10-07; generators keep everything from this line on; entries above marked "// story:").
// The ladder up to the summit: converter/gen_caves.py makes step triggers only between caves, and NavelRock_Top is a
// warp-only outdoor map (world.py): the same ladder script by hand. You arrive below the summit's ladder (Emerald (13,21);
// its ladder tile (13,20) is Black 2's solid door tile back down), facing south.
#include "hoenn_story.inc"
#include "scenes/events_lib.inc"
EV_NU4_LadderToTop:                             // warp MAP_NAVEL_ROCK_TOP, 0 (13,20)
    ActorsPauseAll
    SEPlay SEQ_SE_KAIDAN
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    MapChangeCore EV_NAVEL_TOP_ZONE, 13 + EV_NAVEL_TOP_OX, 0, 21 + EV_NAVEL_TOP_OZ, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt
    .balign 4, 0
