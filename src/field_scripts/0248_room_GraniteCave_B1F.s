// GraniteCave_B1F (zone 124): cave_builder (converter/gen_caves.py): ladders and cracked floors as step triggers
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
    ScriptEntry Script_8
    ScriptEntry Script_9
    ScriptEntry Script_10
    ScriptEntry Script_11
    ScriptEntry Script_12
    ScriptEntry Script_13
    ScriptEntry Script_14
    ScriptEntry Script_15
    ScriptEntry Script_16
    ScriptEntry Script_17
    ScriptEntry Script_18
    ScriptEntry Script_19
    ScriptEntry Script_20
    ScriptEntry Script_21
    ScriptEntry Script_22
    ScriptEntry Script_23
    ScriptEntry Script_24
    ScriptEntry Script_25
    ScriptEntry Script_26
    ScriptEntry Script_27
    ScriptEntry Script_28
    ScriptEntry Script_29
    ScriptEntry Script_30
    ScriptEntry Script_31
    ScriptEntry Script_32
    ScriptEntry Script_33
    ScriptEntry Script_34
    ScriptEntry Script_35
    ScriptEntry Script_36
    ScriptEntry Script_37
    ScriptEntry Script_38
    ScriptEntry Script_39
    ScriptEntry Script_40
    ScriptEntry Script_41
    ScriptEntry Script_42
    ScriptEntry Script_43
    ScriptEntry Script_44
    ScriptEntry Script_45
    ScriptEntry Script_46
    ScriptEntry Script_47
    ScriptEntry Script_48
    ScriptEntry Script_49
    ScriptEntry Script_50
    ScriptEntry Script_51
    ScriptEntry Script_52
    ScriptEntry Script_53
    ScriptEntry Script_54
    ScriptEntry Script_55
    ScriptEntry Script_56
    ScriptEntry Script_57
    ScriptEntry Script_58
    ScriptEntry Script_59
    ScriptEntry Script_60
    ScriptEntry Script_61
    ScriptEntry Script_62
    ScriptEntry Script_63
    ScriptEntry Script_64
    ScriptEntry Script_65
    ScriptEntry Script_66
    ScriptEntry Script_67
    ScriptEntry Script_68
    ScriptEntry Script_69
    ScriptEntriesEnd

Script_1:                                      // ladder up (25,13) -> GraniteCave_1F warp 1 (35,3)
    ActorsPauseAll
    SEPlay SEQ_SE_KAIDAN
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    MapChangeCore 118, 35, 0, 3, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_2:                                      // ladder up (4,21) -> GraniteCave_1F warp 2 (17,11)
    ActorsPauseAll
    SEPlay SEQ_SE_KAIDAN
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    MapChangeCore 118, 17, 0, 11, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_3:                                      // ladder down (29,13) -> GraniteCave_B2F warp 0 (29,13)
    ActorsPauseAll
    SEPlay SEQ_SE_KAIDAN
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    MapChangeCore 125, 29, 0, 13, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_4:                                      // ladder down (28,21) -> GraniteCave_B2F warp 1 (28,21)
    ActorsPauseAll
    SEPlay SEQ_SE_KAIDAN
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    MapChangeCore 125, 28, 0, 21, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_5:                                      // ladder down (8,5) -> GraniteCave_B2F warp 2 (8,5)
    ActorsPauseAll
    SEPlay SEQ_SE_KAIDAN
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    MapChangeCore 125, 8, 0, 5, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_6:                                      // ladder down (12,3) -> GraniteCave_B2F warp 3 (12,3)
    ActorsPauseAll
    SEPlay SEQ_SE_KAIDAN
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    MapChangeCore 125, 12, 0, 3, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_7:                                      // ladder down (29,2) -> GraniteCave_B2F warp 4 (29,2)
    ActorsPauseAll
    SEPlay SEQ_SE_KAIDAN
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    MapChangeCore 125, 29, 0, 2, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_8:                                      // cracked floor (2,1) -> fall to GraniteCave_B2F (2,1)
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
    MapChangeCore 125, 2, 0, 1, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_9:                                      // cracked floor (3,1) -> fall to GraniteCave_B2F (3,1)
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
    MapChangeCore 125, 3, 0, 1, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_10:                                      // cracked floor (4,1) -> fall to GraniteCave_B2F (4,1)
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
    MapChangeCore 125, 4, 0, 1, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_11:                                      // cracked floor (5,1) -> fall to GraniteCave_B2F (5,1)
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
    MapChangeCore 125, 5, 0, 1, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_12:                                      // cracked floor (6,1) -> fall to GraniteCave_B2F (6,1)
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
    MapChangeCore 125, 6, 0, 1, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_13:                                      // cracked floor (7,1) -> fall to GraniteCave_B2F (7,1)
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
    MapChangeCore 125, 7, 0, 1, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_14:                                      // cracked floor (15,1) -> fall to GraniteCave_B2F (15,1)
    PlayerGetExState 0x8010
    VMStackPush 0x8010
    VMStackPushConst 1
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_Fall_14
    VMHalt
L_Fall_14:
    ActorsPauseAll
    SEPlay SEQ_SE_DANSA
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    MapChangeCore 125, 15, 0, 1, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_15:                                      // cracked floor (16,1) -> fall to GraniteCave_B2F (16,1)
    PlayerGetExState 0x8010
    VMStackPush 0x8010
    VMStackPushConst 1
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_Fall_15
    VMHalt
L_Fall_15:
    ActorsPauseAll
    SEPlay SEQ_SE_DANSA
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    MapChangeCore 125, 16, 0, 1, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_16:                                      // cracked floor (17,1) -> fall to GraniteCave_B2F (17,1)
    PlayerGetExState 0x8010
    VMStackPush 0x8010
    VMStackPushConst 1
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_Fall_16
    VMHalt
L_Fall_16:
    ActorsPauseAll
    SEPlay SEQ_SE_DANSA
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    MapChangeCore 125, 17, 0, 1, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_17:                                      // cracked floor (18,1) -> fall to GraniteCave_B2F (18,1)
    PlayerGetExState 0x8010
    VMStackPush 0x8010
    VMStackPushConst 1
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_Fall_17
    VMHalt
L_Fall_17:
    ActorsPauseAll
    SEPlay SEQ_SE_DANSA
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    MapChangeCore 125, 18, 0, 1, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_18:                                      // cracked floor (19,1) -> fall to GraniteCave_B2F (19,1)
    PlayerGetExState 0x8010
    VMStackPush 0x8010
    VMStackPushConst 1
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_Fall_18
    VMHalt
L_Fall_18:
    ActorsPauseAll
    SEPlay SEQ_SE_DANSA
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    MapChangeCore 125, 19, 0, 1, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_19:                                      // cracked floor (20,1) -> fall to GraniteCave_B2F (20,1)
    PlayerGetExState 0x8010
    VMStackPush 0x8010
    VMStackPushConst 1
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_Fall_19
    VMHalt
L_Fall_19:
    ActorsPauseAll
    SEPlay SEQ_SE_DANSA
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    MapChangeCore 125, 20, 0, 1, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_20:                                      // cracked floor (21,1) -> fall to GraniteCave_B2F (21,1)
    PlayerGetExState 0x8010
    VMStackPush 0x8010
    VMStackPushConst 1
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_Fall_20
    VMHalt
L_Fall_20:
    ActorsPauseAll
    SEPlay SEQ_SE_DANSA
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    MapChangeCore 125, 21, 0, 1, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_21:                                      // cracked floor (22,1) -> fall to GraniteCave_B2F (22,1)
    PlayerGetExState 0x8010
    VMStackPush 0x8010
    VMStackPushConst 1
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_Fall_21
    VMHalt
L_Fall_21:
    ActorsPauseAll
    SEPlay SEQ_SE_DANSA
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    MapChangeCore 125, 22, 0, 1, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_22:                                      // cracked floor (2,2) -> fall to GraniteCave_B2F (2,2)
    PlayerGetExState 0x8010
    VMStackPush 0x8010
    VMStackPushConst 1
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_Fall_22
    VMHalt
L_Fall_22:
    ActorsPauseAll
    SEPlay SEQ_SE_DANSA
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    MapChangeCore 125, 2, 0, 2, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_23:                                      // cracked floor (3,2) -> fall to GraniteCave_B2F (3,2)
    PlayerGetExState 0x8010
    VMStackPush 0x8010
    VMStackPushConst 1
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_Fall_23
    VMHalt
L_Fall_23:
    ActorsPauseAll
    SEPlay SEQ_SE_DANSA
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    MapChangeCore 125, 3, 0, 2, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_24:                                      // cracked floor (4,2) -> fall to GraniteCave_B2F (4,2)
    PlayerGetExState 0x8010
    VMStackPush 0x8010
    VMStackPushConst 1
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_Fall_24
    VMHalt
L_Fall_24:
    ActorsPauseAll
    SEPlay SEQ_SE_DANSA
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    MapChangeCore 125, 4, 0, 2, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_25:                                      // cracked floor (5,2) -> fall to GraniteCave_B2F (5,2)
    PlayerGetExState 0x8010
    VMStackPush 0x8010
    VMStackPushConst 1
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_Fall_25
    VMHalt
L_Fall_25:
    ActorsPauseAll
    SEPlay SEQ_SE_DANSA
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    MapChangeCore 125, 5, 0, 2, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_26:                                      // cracked floor (6,2) -> fall to GraniteCave_B2F (6,2)
    PlayerGetExState 0x8010
    VMStackPush 0x8010
    VMStackPushConst 1
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_Fall_26
    VMHalt
L_Fall_26:
    ActorsPauseAll
    SEPlay SEQ_SE_DANSA
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    MapChangeCore 125, 6, 0, 2, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_27:                                      // cracked floor (7,2) -> fall to GraniteCave_B2F (7,2)
    PlayerGetExState 0x8010
    VMStackPush 0x8010
    VMStackPushConst 1
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_Fall_27
    VMHalt
L_Fall_27:
    ActorsPauseAll
    SEPlay SEQ_SE_DANSA
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    MapChangeCore 125, 7, 0, 2, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_28:                                      // cracked floor (15,2) -> fall to GraniteCave_B2F (15,2)
    PlayerGetExState 0x8010
    VMStackPush 0x8010
    VMStackPushConst 1
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_Fall_28
    VMHalt
L_Fall_28:
    ActorsPauseAll
    SEPlay SEQ_SE_DANSA
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    MapChangeCore 125, 15, 0, 2, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_29:                                      // cracked floor (16,2) -> fall to GraniteCave_B2F (16,2)
    PlayerGetExState 0x8010
    VMStackPush 0x8010
    VMStackPushConst 1
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_Fall_29
    VMHalt
L_Fall_29:
    ActorsPauseAll
    SEPlay SEQ_SE_DANSA
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    MapChangeCore 125, 16, 0, 2, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_30:                                      // cracked floor (17,2) -> fall to GraniteCave_B2F (17,2)
    PlayerGetExState 0x8010
    VMStackPush 0x8010
    VMStackPushConst 1
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_Fall_30
    VMHalt
L_Fall_30:
    ActorsPauseAll
    SEPlay SEQ_SE_DANSA
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    MapChangeCore 125, 17, 0, 2, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_31:                                      // cracked floor (18,2) -> fall to GraniteCave_B2F (18,2)
    PlayerGetExState 0x8010
    VMStackPush 0x8010
    VMStackPushConst 1
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_Fall_31
    VMHalt
L_Fall_31:
    ActorsPauseAll
    SEPlay SEQ_SE_DANSA
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    MapChangeCore 125, 18, 0, 2, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_32:                                      // cracked floor (19,2) -> fall to GraniteCave_B2F (19,2)
    PlayerGetExState 0x8010
    VMStackPush 0x8010
    VMStackPushConst 1
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_Fall_32
    VMHalt
L_Fall_32:
    ActorsPauseAll
    SEPlay SEQ_SE_DANSA
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    MapChangeCore 125, 19, 0, 2, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_33:                                      // cracked floor (20,2) -> fall to GraniteCave_B2F (20,2)
    PlayerGetExState 0x8010
    VMStackPush 0x8010
    VMStackPushConst 1
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_Fall_33
    VMHalt
L_Fall_33:
    ActorsPauseAll
    SEPlay SEQ_SE_DANSA
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    MapChangeCore 125, 20, 0, 2, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_34:                                      // cracked floor (21,2) -> fall to GraniteCave_B2F (21,2)
    PlayerGetExState 0x8010
    VMStackPush 0x8010
    VMStackPushConst 1
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_Fall_34
    VMHalt
L_Fall_34:
    ActorsPauseAll
    SEPlay SEQ_SE_DANSA
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    MapChangeCore 125, 21, 0, 2, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_35:                                      // cracked floor (22,2) -> fall to GraniteCave_B2F (22,2)
    PlayerGetExState 0x8010
    VMStackPush 0x8010
    VMStackPushConst 1
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_Fall_35
    VMHalt
L_Fall_35:
    ActorsPauseAll
    SEPlay SEQ_SE_DANSA
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    MapChangeCore 125, 22, 0, 2, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_36:                                      // cracked floor (15,3) -> fall to GraniteCave_B2F (15,3)
    PlayerGetExState 0x8010
    VMStackPush 0x8010
    VMStackPushConst 1
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_Fall_36
    VMHalt
L_Fall_36:
    ActorsPauseAll
    SEPlay SEQ_SE_DANSA
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    MapChangeCore 125, 15, 0, 3, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_37:                                      // cracked floor (16,3) -> fall to GraniteCave_B2F (16,3)
    PlayerGetExState 0x8010
    VMStackPush 0x8010
    VMStackPushConst 1
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_Fall_37
    VMHalt
L_Fall_37:
    ActorsPauseAll
    SEPlay SEQ_SE_DANSA
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    MapChangeCore 125, 16, 0, 3, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_38:                                      // cracked floor (17,3) -> fall to GraniteCave_B2F (17,3)
    PlayerGetExState 0x8010
    VMStackPush 0x8010
    VMStackPushConst 1
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_Fall_38
    VMHalt
L_Fall_38:
    ActorsPauseAll
    SEPlay SEQ_SE_DANSA
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    MapChangeCore 125, 17, 0, 3, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_39:                                      // cracked floor (18,3) -> fall to GraniteCave_B2F (18,3)
    PlayerGetExState 0x8010
    VMStackPush 0x8010
    VMStackPushConst 1
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_Fall_39
    VMHalt
L_Fall_39:
    ActorsPauseAll
    SEPlay SEQ_SE_DANSA
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    MapChangeCore 125, 18, 0, 3, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_40:                                      // cracked floor (19,3) -> fall to GraniteCave_B2F (19,3)
    PlayerGetExState 0x8010
    VMStackPush 0x8010
    VMStackPushConst 1
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_Fall_40
    VMHalt
L_Fall_40:
    ActorsPauseAll
    SEPlay SEQ_SE_DANSA
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    MapChangeCore 125, 19, 0, 3, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_41:                                      // cracked floor (20,3) -> fall to GraniteCave_B2F (20,3)
    PlayerGetExState 0x8010
    VMStackPush 0x8010
    VMStackPushConst 1
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_Fall_41
    VMHalt
L_Fall_41:
    ActorsPauseAll
    SEPlay SEQ_SE_DANSA
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    MapChangeCore 125, 20, 0, 3, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_42:                                      // cracked floor (21,3) -> fall to GraniteCave_B2F (21,3)
    PlayerGetExState 0x8010
    VMStackPush 0x8010
    VMStackPushConst 1
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_Fall_42
    VMHalt
L_Fall_42:
    ActorsPauseAll
    SEPlay SEQ_SE_DANSA
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    MapChangeCore 125, 21, 0, 3, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_43:                                      // cracked floor (22,3) -> fall to GraniteCave_B2F (22,3)
    PlayerGetExState 0x8010
    VMStackPush 0x8010
    VMStackPushConst 1
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_Fall_43
    VMHalt
L_Fall_43:
    ActorsPauseAll
    SEPlay SEQ_SE_DANSA
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    MapChangeCore 125, 22, 0, 3, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_44:                                      // cracked floor (18,4) -> fall to GraniteCave_B2F (18,4)
    PlayerGetExState 0x8010
    VMStackPush 0x8010
    VMStackPushConst 1
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_Fall_44
    VMHalt
L_Fall_44:
    ActorsPauseAll
    SEPlay SEQ_SE_DANSA
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    MapChangeCore 125, 18, 0, 4, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_45:                                      // cracked floor (19,4) -> fall to GraniteCave_B2F (19,4)
    PlayerGetExState 0x8010
    VMStackPush 0x8010
    VMStackPushConst 1
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_Fall_45
    VMHalt
L_Fall_45:
    ActorsPauseAll
    SEPlay SEQ_SE_DANSA
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    MapChangeCore 125, 19, 0, 4, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_46:                                      // cracked floor (20,4) -> fall to GraniteCave_B2F (20,4)
    PlayerGetExState 0x8010
    VMStackPush 0x8010
    VMStackPushConst 1
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_Fall_46
    VMHalt
L_Fall_46:
    ActorsPauseAll
    SEPlay SEQ_SE_DANSA
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    MapChangeCore 125, 20, 0, 4, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_47:                                      // cracked floor (22,4) -> fall to GraniteCave_B2F (22,4)
    PlayerGetExState 0x8010
    VMStackPush 0x8010
    VMStackPushConst 1
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_Fall_47
    VMHalt
L_Fall_47:
    ActorsPauseAll
    SEPlay SEQ_SE_DANSA
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    MapChangeCore 125, 22, 0, 4, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_48:                                      // cracked floor (23,4) -> fall to GraniteCave_B2F (23,4)
    PlayerGetExState 0x8010
    VMStackPush 0x8010
    VMStackPushConst 1
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_Fall_48
    VMHalt
L_Fall_48:
    ActorsPauseAll
    SEPlay SEQ_SE_DANSA
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    MapChangeCore 125, 23, 0, 4, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_49:                                      // cracked floor (24,4) -> fall to GraniteCave_B2F (24,4)
    PlayerGetExState 0x8010
    VMStackPush 0x8010
    VMStackPushConst 1
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_Fall_49
    VMHalt
L_Fall_49:
    ActorsPauseAll
    SEPlay SEQ_SE_DANSA
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    MapChangeCore 125, 24, 0, 4, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_50:                                      // cracked floor (3,5) -> fall to GraniteCave_B2F (3,5)
    PlayerGetExState 0x8010
    VMStackPush 0x8010
    VMStackPushConst 1
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_Fall_50
    VMHalt
L_Fall_50:
    ActorsPauseAll
    SEPlay SEQ_SE_DANSA
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    MapChangeCore 125, 3, 0, 5, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_51:                                      // cracked floor (4,5) -> fall to GraniteCave_B2F (4,5)
    PlayerGetExState 0x8010
    VMStackPush 0x8010
    VMStackPushConst 1
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_Fall_51
    VMHalt
L_Fall_51:
    ActorsPauseAll
    SEPlay SEQ_SE_DANSA
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    MapChangeCore 125, 4, 0, 5, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_52:                                      // cracked floor (5,5) -> fall to GraniteCave_B2F (5,5)
    PlayerGetExState 0x8010
    VMStackPush 0x8010
    VMStackPushConst 1
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_Fall_52
    VMHalt
L_Fall_52:
    ActorsPauseAll
    SEPlay SEQ_SE_DANSA
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    MapChangeCore 125, 5, 0, 5, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_53:                                      // cracked floor (18,5) -> fall to GraniteCave_B2F (18,5)
    PlayerGetExState 0x8010
    VMStackPush 0x8010
    VMStackPushConst 1
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_Fall_53
    VMHalt
L_Fall_53:
    ActorsPauseAll
    SEPlay SEQ_SE_DANSA
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    MapChangeCore 125, 18, 0, 5, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_54:                                      // cracked floor (19,5) -> fall to GraniteCave_B2F (19,5)
    PlayerGetExState 0x8010
    VMStackPush 0x8010
    VMStackPushConst 1
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_Fall_54
    VMHalt
L_Fall_54:
    ActorsPauseAll
    SEPlay SEQ_SE_DANSA
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    MapChangeCore 125, 19, 0, 5, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_55:                                      // cracked floor (20,5) -> fall to GraniteCave_B2F (20,5)
    PlayerGetExState 0x8010
    VMStackPush 0x8010
    VMStackPushConst 1
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_Fall_55
    VMHalt
L_Fall_55:
    ActorsPauseAll
    SEPlay SEQ_SE_DANSA
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    MapChangeCore 125, 20, 0, 5, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_56:                                      // cracked floor (21,5) -> fall to GraniteCave_B2F (21,5)
    PlayerGetExState 0x8010
    VMStackPush 0x8010
    VMStackPushConst 1
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_Fall_56
    VMHalt
L_Fall_56:
    ActorsPauseAll
    SEPlay SEQ_SE_DANSA
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    MapChangeCore 125, 21, 0, 5, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_57:                                      // cracked floor (22,5) -> fall to GraniteCave_B2F (22,5)
    PlayerGetExState 0x8010
    VMStackPush 0x8010
    VMStackPushConst 1
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_Fall_57
    VMHalt
L_Fall_57:
    ActorsPauseAll
    SEPlay SEQ_SE_DANSA
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    MapChangeCore 125, 22, 0, 5, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_58:                                      // cracked floor (23,5) -> fall to GraniteCave_B2F (23,5)
    PlayerGetExState 0x8010
    VMStackPush 0x8010
    VMStackPushConst 1
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_Fall_58
    VMHalt
L_Fall_58:
    ActorsPauseAll
    SEPlay SEQ_SE_DANSA
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    MapChangeCore 125, 23, 0, 5, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_59:                                      // cracked floor (24,5) -> fall to GraniteCave_B2F (24,5)
    PlayerGetExState 0x8010
    VMStackPush 0x8010
    VMStackPushConst 1
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_Fall_59
    VMHalt
L_Fall_59:
    ActorsPauseAll
    SEPlay SEQ_SE_DANSA
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    MapChangeCore 125, 24, 0, 5, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_60:                                      // cracked floor (3,6) -> fall to GraniteCave_B2F (3,6)
    PlayerGetExState 0x8010
    VMStackPush 0x8010
    VMStackPushConst 1
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_Fall_60
    VMHalt
L_Fall_60:
    ActorsPauseAll
    SEPlay SEQ_SE_DANSA
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    MapChangeCore 125, 3, 0, 6, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_61:                                      // cracked floor (4,6) -> fall to GraniteCave_B2F (4,6)
    PlayerGetExState 0x8010
    VMStackPush 0x8010
    VMStackPushConst 1
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_Fall_61
    VMHalt
L_Fall_61:
    ActorsPauseAll
    SEPlay SEQ_SE_DANSA
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    MapChangeCore 125, 4, 0, 6, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_62:                                      // cracked floor (5,6) -> fall to GraniteCave_B2F (5,6)
    PlayerGetExState 0x8010
    VMStackPush 0x8010
    VMStackPushConst 1
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_Fall_62
    VMHalt
L_Fall_62:
    ActorsPauseAll
    SEPlay SEQ_SE_DANSA
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    MapChangeCore 125, 5, 0, 6, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_63:                                      // cracked floor (18,6) -> fall to GraniteCave_B2F (18,6)
    PlayerGetExState 0x8010
    VMStackPush 0x8010
    VMStackPushConst 1
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_Fall_63
    VMHalt
L_Fall_63:
    ActorsPauseAll
    SEPlay SEQ_SE_DANSA
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    MapChangeCore 125, 18, 0, 6, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_64:                                      // cracked floor (19,6) -> fall to GraniteCave_B2F (19,6)
    PlayerGetExState 0x8010
    VMStackPush 0x8010
    VMStackPushConst 1
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_Fall_64
    VMHalt
L_Fall_64:
    ActorsPauseAll
    SEPlay SEQ_SE_DANSA
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    MapChangeCore 125, 19, 0, 6, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_65:                                      // cracked floor (20,6) -> fall to GraniteCave_B2F (20,6)
    PlayerGetExState 0x8010
    VMStackPush 0x8010
    VMStackPushConst 1
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_Fall_65
    VMHalt
L_Fall_65:
    ActorsPauseAll
    SEPlay SEQ_SE_DANSA
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    MapChangeCore 125, 20, 0, 6, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_66:                                      // cracked floor (21,6) -> fall to GraniteCave_B2F (21,6)
    PlayerGetExState 0x8010
    VMStackPush 0x8010
    VMStackPushConst 1
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_Fall_66
    VMHalt
L_Fall_66:
    ActorsPauseAll
    SEPlay SEQ_SE_DANSA
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    MapChangeCore 125, 21, 0, 6, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_67:                                      // cracked floor (22,6) -> fall to GraniteCave_B2F (22,6)
    PlayerGetExState 0x8010
    VMStackPush 0x8010
    VMStackPushConst 1
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_Fall_67
    VMHalt
L_Fall_67:
    ActorsPauseAll
    SEPlay SEQ_SE_DANSA
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    MapChangeCore 125, 22, 0, 6, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_68:                                      // cracked floor (23,6) -> fall to GraniteCave_B2F (23,6)
    PlayerGetExState 0x8010
    VMStackPush 0x8010
    VMStackPushConst 1
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_Fall_68
    VMHalt
L_Fall_68:
    ActorsPauseAll
    SEPlay SEQ_SE_DANSA
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    MapChangeCore 125, 23, 0, 6, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_69:                                      // cracked floor (24,6) -> fall to GraniteCave_B2F (24,6)
    PlayerGetExState 0x8010
    VMStackPush 0x8010
    VMStackPushConst 1
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_Fall_69
    VMHalt
L_Fall_69:
    ActorsPauseAll
    SEPlay SEQ_SE_DANSA
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    MapChangeCore 125, 24, 0, 6, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt
    .balign 4, 0
