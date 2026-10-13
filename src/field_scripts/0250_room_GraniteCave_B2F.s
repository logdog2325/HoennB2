// GraniteCave_B2F (zone 125): cave_builder (converter/gen_caves.py): ladders and cracked floors as step triggers
// (Sapphire's step-on warps), simple people/signs. Story scripts: add them after a line "// ---- story" (this
// generator keeps everything from that line on and the entries you add: b2tools/story_merge.py) and number them
// after these entries.
#include "asm/field_script.inc"
#include "hoenn.h"

    ScriptEntry Script_1
    ScriptEntry Script_2
    ScriptEntry Script_3
    ScriptEntry Script_4
    ScriptEntry Script_5
    ScriptEntriesEnd

Script_1:                                      // ladder up (29,13) -> GraniteCave_B1F warp 2 (29,13)
    ActorsPauseAll
    SEPlay SEQ_SE_KAIDAN
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    MapChangeCore 124, 29, 0, 13, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_2:                                      // ladder up (28,21) -> GraniteCave_B1F warp 3 (28,21)
    ActorsPauseAll
    SEPlay SEQ_SE_KAIDAN
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    MapChangeCore 124, 28, 0, 21, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_3:                                      // ladder up (8,5) -> GraniteCave_B1F warp 4 (8,5)
    ActorsPauseAll
    SEPlay SEQ_SE_KAIDAN
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    MapChangeCore 124, 8, 0, 5, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_4:                                      // ladder up (12,3) -> GraniteCave_B1F warp 5 (12,3)
    ActorsPauseAll
    SEPlay SEQ_SE_KAIDAN
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    MapChangeCore 124, 12, 0, 3, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_5:                                      // ladder up (29,2) -> GraniteCave_B1F warp 6 (29,2)
    ActorsPauseAll
    SEPlay SEQ_SE_KAIDAN
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    MapChangeCore 124, 29, 0, 2, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt
    .balign 4, 0
