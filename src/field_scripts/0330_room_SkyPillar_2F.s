// SkyPillar_2F (zone 165): cave_builder (converter/gen_caves.py): ladders and cracked floors as step triggers
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
#ifdef HOENN_EMERALD
    ScriptEntry SPF_Init  // 39: zone init (Emerald: the cracked floor after Rayquaza, emerald_ch10)  // story:
#endif
    ScriptEntriesEnd

Script_1:                                      // cracked floor (10,5) -> fall to SkyPillar_1F (10,5)
    PlayerGetExState 0x8010
    VMStackPush 0x8010
    VMStackPushConst 1
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_Fall_1
    VMHalt
L_Fall_1:
    ActorsPauseAll
    SEPlay SEQ_SE_DANSA
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    MapChangeCore 164, 11, 0, 5, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_2:                                      // cracked floor (11,5) -> fall to SkyPillar_1F (11,5)
    PlayerGetExState 0x8010
    VMStackPush 0x8010
    VMStackPushConst 1
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_Fall_2
    VMHalt
L_Fall_2:
    ActorsPauseAll
    SEPlay SEQ_SE_DANSA
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    MapChangeCore 164, 12, 0, 5, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_3:                                      // cracked floor (12,5) -> fall to SkyPillar_1F (12,5)
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
    MapChangeCore 164, 13, 0, 5, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_4:                                      // cracked floor (13,5) -> fall to SkyPillar_1F (13,5)
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
    MapChangeCore 164, 14, 0, 5, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_5:                                      // cracked floor (10,6) -> fall to SkyPillar_1F (10,6)
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
    MapChangeCore 164, 11, 0, 6, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_6:                                      // cracked floor (11,6) -> fall to SkyPillar_1F (11,6)
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
    MapChangeCore 164, 12, 0, 6, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_7:                                      // cracked floor (12,6) -> fall to SkyPillar_1F (12,6)
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
    MapChangeCore 164, 13, 0, 6, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_8:                                      // cracked floor (13,6) -> fall to SkyPillar_1F (13,6)
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
    MapChangeCore 164, 14, 0, 6, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_9:                                      // cracked floor (2,7) -> fall to SkyPillar_1F (2,7)
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
    MapChangeCore 164, 3, 0, 7, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_10:                                      // cracked floor (3,7) -> fall to SkyPillar_1F (3,7)
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
    MapChangeCore 164, 4, 0, 7, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_11:                                      // cracked floor (0,8) -> fall to SkyPillar_1F (1,8)
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
    MapChangeCore 164, 2, 0, 8, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_12:                                      // cracked floor (1,8) -> fall to SkyPillar_1F (1,8)
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
    MapChangeCore 164, 2, 0, 8, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_13:                                      // cracked floor (2,8) -> fall to SkyPillar_1F (2,8)
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
    MapChangeCore 164, 3, 0, 8, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_14:                                      // cracked floor (3,8) -> fall to SkyPillar_1F (3,8)
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
    MapChangeCore 164, 4, 0, 8, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_15:                                      // cracked floor (0,9) -> fall to SkyPillar_1F (0,9)
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
    MapChangeCore 164, 1, 0, 9, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_16:                                      // cracked floor (1,9) -> fall to SkyPillar_1F (1,9)
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
    MapChangeCore 164, 2, 0, 9, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_17:                                      // cracked floor (2,9) -> fall to SkyPillar_1F (2,9)
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
    MapChangeCore 164, 3, 0, 9, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_18:                                      // cracked floor (3,9) -> fall to SkyPillar_1F (3,9)
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
    MapChangeCore 164, 4, 0, 9, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_19:                                      // cracked floor (0,10) -> fall to SkyPillar_1F (0,10)
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
    MapChangeCore 164, 1, 0, 10, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_20:                                      // cracked floor (1,10) -> fall to SkyPillar_1F (1,10)
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
    MapChangeCore 164, 2, 0, 10, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_21:                                      // cracked floor (10,10) -> fall to SkyPillar_1F (10,10)
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
    MapChangeCore 164, 11, 0, 10, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_22:                                      // cracked floor (11,10) -> fall to SkyPillar_1F (11,10)
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
    MapChangeCore 164, 12, 0, 10, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_23:                                      // cracked floor (0,11) -> fall to SkyPillar_1F (0,11)
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
    MapChangeCore 164, 1, 0, 11, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_24:                                      // cracked floor (4,11) -> fall to SkyPillar_1F (4,11)
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
    MapChangeCore 164, 5, 0, 11, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_25:                                      // cracked floor (5,11) -> fall to SkyPillar_1F (5,11)
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
    MapChangeCore 164, 6, 0, 11, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_26:                                      // cracked floor (10,11) -> fall to SkyPillar_1F (10,11)
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
    MapChangeCore 164, 11, 0, 11, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_27:                                      // cracked floor (11,11) -> fall to SkyPillar_1F (11,11)
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
    MapChangeCore 164, 12, 0, 11, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_28:                                      // cracked floor (12,11) -> fall to SkyPillar_1F (12,11)
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
    MapChangeCore 164, 13, 0, 11, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_29:                                      // cracked floor (13,11) -> fall to SkyPillar_1F (13,11)
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
    MapChangeCore 164, 14, 0, 11, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_30:                                      // cracked floor (4,12) -> fall to SkyPillar_1F (4,12)
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
    MapChangeCore 164, 5, 0, 12, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_31:                                      // cracked floor (5,12) -> fall to SkyPillar_1F (5,12)
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
    MapChangeCore 164, 6, 0, 12, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_32:                                      // cracked floor (10,12) -> fall to SkyPillar_1F (10,12)
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
    MapChangeCore 164, 11, 0, 12, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_33:                                      // cracked floor (11,12) -> fall to SkyPillar_1F (11,12)
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
    MapChangeCore 164, 12, 0, 12, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_34:                                      // cracked floor (12,12) -> fall to SkyPillar_1F (12,12)
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
    MapChangeCore 164, 13, 0, 12, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_35:                                      // cracked floor (13,12) -> fall to SkyPillar_1F (13,12)
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
    MapChangeCore 164, 14, 0, 12, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_36:                                      // cracked floor (3,13) -> fall to SkyPillar_1F (3,13)
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
    MapChangeCore 164, 4, 0, 13, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_37:                                      // cracked floor (4,13) -> fall to SkyPillar_1F (4,13)
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
    MapChangeCore 164, 5, 0, 13, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_38:                                      // cracked floor (5,13) -> fall to SkyPillar_1F (5,13)
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
    MapChangeCore 164, 6, 0, 13, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt
    .balign 4, 0

// ---- story (Pokémon Emerald NDS, emerald_ch10 2026-10-12; generators keep everything from this line on and the entry above
// marked "// story:"). Emerald only: pokeemerald SkyPillar_2F_OnTransition shows the clean floor while VAR_SKY_PILLAR_STATE < 2
// (until Rayquaza has been to Sootopolis). In an Emerald build the clean floor is this room's variant (SkyPillar_2F_Emerald)
// and Sapphire's cracked room its other layout (data/interiors/emerald/165.json alt_rooms: map replace event 3, shared with
// Mauville Gym, whose zone init sets it too: b2tools/emerald_caves_rooms.py). Map script: src/field_scripts/emerald/
// 0331_room_SkyPillar_2F_init.s (zone init = script 39).
// The falls of the cracked floor (the zone json's triggers) fire only while temporary work 0x4001 is 1.
#ifdef HOENN_EMERALD
#include "hoenn_story.inc"
SPF_Init:
    MapReplaceIsEventSet 3, 0x8000
    h_goto_if_ge VAR_SKY_PILLAR_STATE, 2, L_SPF_Cracked
    h_goto_if_eq 0x8000, 0, L_SPF_Done
    MapReplaceSetEvent 3, 0, 1          // the clean floor (the zone's matrix is loaded already: reload it)
    VMHalt
L_SPF_Cracked:
    WorkSetConst 0x4001, 1              // the falls
    h_goto_if_eq 0x8000, 1, L_SPF_Done
    MapReplaceSetEvent 3, 1, 1          // Sapphire's cracked floor
L_SPF_Done:
    VMHalt
    .balign 4, 0
#endif
