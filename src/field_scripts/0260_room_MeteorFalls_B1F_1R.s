// MeteorFalls_B1F_1R (zone 130): cave_builder (converter/gen_caves.py): ladders and cracked floors as step triggers
// (Sapphire's step-on warps), simple people/signs. Story scripts: add them after a line "// ---- story" (this
// generator keeps everything from that line on and the entries you add: b2tools/story_merge.py) and number them
// after these entries.
#include "asm/field_script.inc"
#include "hoenn.h"

    ScriptEntry Script_1
    ScriptEntry Script_2
    ScriptEntry Script_3
    ScriptEntry Script_4
    ScriptEntriesEnd

Script_1:                                      // ladder up (5,6) -> MeteorFalls_1F_2R warp 1 (4,14)
    ActorsPauseAll
    SEPlay SEQ_SE_KAIDAN
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    MapChangeCore 129, 4, 0, 14, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_2:                                      // ladder up (7,11) -> MeteorFalls_1F_2R warp 2 (7,20)
    ActorsPauseAll
    SEPlay SEQ_SE_KAIDAN
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    MapChangeCore 129, 7, 0, 20, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_3:                                      // ladder up (18,15) -> MeteorFalls_1F_2R warp 3 (21,23)
    ActorsPauseAll
    SEPlay SEQ_SE_KAIDAN
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    MapChangeCore 129, 21, 0, 23, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_4:                                      // ladder up (3,23) -> MeteorFalls_1F_1R warp 3 (5,4)
    ActorsPauseAll
    SEPlay SEQ_SE_KAIDAN
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    MapChangeCore 128, 5, 6, 15, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt
    .balign 4, 0
