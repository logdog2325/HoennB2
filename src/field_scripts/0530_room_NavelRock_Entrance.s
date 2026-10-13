// NavelRock_Entrance (zone 265): cave_builder (converter/gen_caves.py): ladders and cracked floors as step triggers
// (Sapphire's step-on warps), simple people/signs. Story scripts: add them after a line "// ---- story" (this
// generator keeps everything from that line on and the entries you add: b2tools/story_merge.py) and number them
// after these entries.
#include "asm/field_script.inc"
#include "hoenn.h"

    ScriptEntry Script_1
    ScriptEntriesEnd

Script_1:                                      // ladder down (10,5) -> NavelRock_B1F warp 0 (4,3)
    ActorsPauseAll
    SEPlay SEQ_SE_KAIDAN
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    MapChangeCore 224, 4, 0, 3, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt
    .balign 4, 0
