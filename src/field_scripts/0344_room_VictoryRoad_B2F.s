// VictoryRoad_B2F (zone 172): cave_builder (converter/gen_caves.py): ladders and cracked floors as step triggers
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

Script_1:                                      // ladder up (30,25) -> VictoryRoad_B1F warp 0 (30,25)
    ActorsPauseAll
    SEPlay SEQ_SE_KAIDAN
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    MapChangeCore 171, 38, 0, 25, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_2:                                      // ladder up (43,2) -> VictoryRoad_B1F warp 3 (42,2)
    ActorsPauseAll
    SEPlay SEQ_SE_KAIDAN
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    MapChangeCore 171, 50, 1, 2, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_3:                                      // ladder up (19,12) -> VictoryRoad_B1F warp 1 (17,16)
    ActorsPauseAll
    SEPlay SEQ_SE_KAIDAN
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    MapChangeCore 171, 25, 0, 16, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_4:                                      // ladder up (5,26) -> VictoryRoad_B1F warp 6 (5,26)
    ActorsPauseAll
    SEPlay SEQ_SE_KAIDAN
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    MapChangeCore 171, 13, 0, 26, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt
    .balign 4, 0
