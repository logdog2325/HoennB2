// MirageTower_3F (zone 362, Emerald): converter/gen_caves_emerald.py from emerald/MirageTower_3F (emerald_caves): ladders and
// cracked floors as step triggers, simple people/signs. Story scripts: add them after a line "// ---- story" (this
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

Script_1:                                      // ladder down (18,12) -> MirageTower_2F warp 0 (18,12)
    ActorsPauseAll
    SEPlay SEQ_SE_KAIDAN
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    MapChangeCore 361, 18, 0, 12, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_2:                                      // ladder up (2,4) -> MirageTower_4F warp 0 (1,4)
    ActorsPauseAll
    SEPlay SEQ_SE_KAIDAN
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    MapChangeCore 363, 1, 0, 4, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_3:                                      // cracked floor (17,6) -> fall to MirageTower_2F (17,6)
    PlayerGetExState 0x8010
    VMStackPush 0x8010
    VMStackPushConst 1
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_Fall_3
    VMHalt
L_Fall_3:
    ActorsPauseAll
    SEPlay SEQ_SE_DANSA
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    MapChangeCore 361, 17, 0, 6, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_4:                                      // cracked floor (16,7) -> fall to MirageTower_2F (16,7)
    PlayerGetExState 0x8010
    VMStackPush 0x8010
    VMStackPushConst 1
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_Fall_4
    VMHalt
L_Fall_4:
    ActorsPauseAll
    SEPlay SEQ_SE_DANSA
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    MapChangeCore 361, 16, 0, 7, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_5:                                      // cracked floor (18,7) -> fall to MirageTower_2F (18,7)
    PlayerGetExState 0x8010
    VMStackPush 0x8010
    VMStackPushConst 1
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_Fall_5
    VMHalt
L_Fall_5:
    ActorsPauseAll
    SEPlay SEQ_SE_DANSA
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    MapChangeCore 361, 18, 0, 7, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt
    .balign 4, 0
