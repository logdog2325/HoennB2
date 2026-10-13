// VictoryRoad_B1F (zone 171): cave_builder (converter/gen_caves.py): ladders and cracked floors as step triggers
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
    ScriptEntry Script_6
    ScriptEntry Script_7
    ScriptEntriesEnd

Script_1:                                      // ladder down (30,25) -> VictoryRoad_B2F warp 0 (30,25)
    ActorsPauseAll
    SEPlay SEQ_SE_KAIDAN
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    MapChangeCore 172, 38, 0, 25, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_2:                                      // ladder down (17,16) -> VictoryRoad_B2F warp 2 (19,12)
    ActorsPauseAll
    SEPlay SEQ_SE_KAIDAN
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    MapChangeCore 172, 27, 0, 12, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_3:                                      // ladder up (42,25) -> VictoryRoad_1F warp 3 (42,38)
    ActorsPauseAll
    SEPlay SEQ_SE_KAIDAN
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    MapChangeCore 170, 50, 1, 46, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_4:                                      // ladder down (42,2) -> VictoryRoad_B2F warp 1 (43,2)
    ActorsPauseAll
    SEPlay SEQ_SE_KAIDAN
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    MapChangeCore 172, 51, 0, 2, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_5:                                      // ladder up (8,3) -> VictoryRoad_1F warp 4 (9,14)
    ActorsPauseAll
    SEPlay SEQ_SE_KAIDAN
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    MapChangeCore 170, 17, 1, 22, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_6:                                      // ladder up (20,21) -> VictoryRoad_1F warp 2 (21,32)
    ActorsPauseAll
    SEPlay SEQ_SE_KAIDAN
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    MapChangeCore 170, 29, 0, 40, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_7:                                      // ladder down (5,26) -> VictoryRoad_B2F warp 3 (5,26)
    ActorsPauseAll
    SEPlay SEQ_SE_KAIDAN
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    MapChangeCore 172, 13, 0, 26, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt
    .balign 4, 0
