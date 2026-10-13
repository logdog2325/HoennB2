// MirageTower_2F (zone 361, Emerald): converter/gen_caves_emerald.py from emerald/MirageTower_2F (emerald_caves): ladders and
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
    ScriptEntry Script_6
    ScriptEntry Script_7
    ScriptEntry Script_8
    ScriptEntry Script_9
    ScriptEntry Script_10
    ScriptEntry Script_11
    ScriptEntry Script_12
    ScriptEntry Script_13
    ScriptEntriesEnd

Script_1:                                      // ladder up (18,12) -> MirageTower_3F warp 0 (18,12)
    ActorsPauseAll
    SEPlay SEQ_SE_KAIDAN
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    MapChangeCore 362, 18, 0, 12, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_2:                                      // ladder down (15,2) -> MirageTower_1F warp 1 (15,2)
    ActorsPauseAll
    SEPlay SEQ_SE_KAIDAN
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    MapChangeCore 360, 15, 0, 2, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_3:                                      // cracked floor (2,4) -> fall to MirageTower_1F (2,4)
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
    MapChangeCore 360, 2, 0, 4, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_4:                                      // cracked floor (3,4) -> fall to MirageTower_1F (3,4)
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
    MapChangeCore 360, 3, 0, 4, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_5:                                      // cracked floor (2,5) -> fall to MirageTower_1F (2,5)
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
    MapChangeCore 360, 2, 0, 5, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_6:                                      // cracked floor (3,5) -> fall to MirageTower_1F (3,5)
    PlayerGetExState 0x8010
    VMStackPush 0x8010
    VMStackPushConst 1
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_Fall_6
    VMHalt
L_Fall_6:
    ActorsPauseAll
    SEPlay SEQ_SE_DANSA
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    MapChangeCore 360, 3, 0, 5, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_7:                                      // cracked floor (2,6) -> fall to MirageTower_1F (2,6)
    PlayerGetExState 0x8010
    VMStackPush 0x8010
    VMStackPushConst 1
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_Fall_7
    VMHalt
L_Fall_7:
    ActorsPauseAll
    SEPlay SEQ_SE_DANSA
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    MapChangeCore 360, 2, 0, 6, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_8:                                      // cracked floor (3,6) -> fall to MirageTower_1F (3,6)
    PlayerGetExState 0x8010
    VMStackPush 0x8010
    VMStackPushConst 1
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_Fall_8
    VMHalt
L_Fall_8:
    ActorsPauseAll
    SEPlay SEQ_SE_DANSA
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    MapChangeCore 360, 3, 0, 6, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_9:                                      // cracked floor (2,7) -> fall to MirageTower_1F (2,7)
    PlayerGetExState 0x8010
    VMStackPush 0x8010
    VMStackPushConst 1
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_Fall_9
    VMHalt
L_Fall_9:
    ActorsPauseAll
    SEPlay SEQ_SE_DANSA
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    MapChangeCore 360, 2, 0, 7, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_10:                                      // cracked floor (3,7) -> fall to MirageTower_1F (3,7)
    PlayerGetExState 0x8010
    VMStackPush 0x8010
    VMStackPushConst 1
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_Fall_10
    VMHalt
L_Fall_10:
    ActorsPauseAll
    SEPlay SEQ_SE_DANSA
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    MapChangeCore 360, 3, 0, 7, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_11:                                      // cracked floor (2,8) -> fall to MirageTower_1F (2,8)
    PlayerGetExState 0x8010
    VMStackPush 0x8010
    VMStackPushConst 1
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_Fall_11
    VMHalt
L_Fall_11:
    ActorsPauseAll
    SEPlay SEQ_SE_DANSA
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    MapChangeCore 360, 2, 0, 8, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_12:                                      // cracked floor (2,9) -> fall to MirageTower_1F (2,9)
    PlayerGetExState 0x8010
    VMStackPush 0x8010
    VMStackPushConst 1
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_Fall_12
    VMHalt
L_Fall_12:
    ActorsPauseAll
    SEPlay SEQ_SE_DANSA
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    MapChangeCore 360, 2, 0, 9, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_13:                                      // cracked floor (2,10) -> fall to MirageTower_1F (2,10)
    PlayerGetExState 0x8010
    VMStackPush 0x8010
    VMStackPushConst 1
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_Fall_13
    VMHalt
L_Fall_13:
    ActorsPauseAll
    SEPlay SEQ_SE_DANSA
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    MapChangeCore 360, 2, 0, 10, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt
    .balign 4, 0
