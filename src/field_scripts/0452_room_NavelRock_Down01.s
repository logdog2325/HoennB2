// NavelRock_Down01 (zone 226): cave_builder (converter/gen_caves.py): ladders and cracked floors as step triggers
// (Sapphire's step-on warps), simple people/signs. Story scripts: add them after a line "// ---- story" (this
// generator keeps everything from that line on and the entries you add: b2tools/story_merge.py) and number them
// after these entries.
#include "asm/field_script.inc"
#include "hoenn.h"

    ScriptEntry Script_1
    ScriptEntry Script_2
    ScriptEntriesEnd

Script_1:                                      // ladder up (3,3) -> NavelRock_Fork warp 2 (22,6)
    ActorsPauseAll
    SEPlay SEQ_SE_KAIDAN
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    MapChangeCore 266, 22, 0, 6, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_2:                                      // ladder down (5,5) -> NavelRock_Down02 warp 0 (5,5)
    ActorsPauseAll
    SEPlay SEQ_SE_KAIDAN
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    MapChangeCore 227, 5, 0, 5, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt
    .balign 4, 0
