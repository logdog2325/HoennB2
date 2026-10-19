// Global trainer scripts 3000-6999 (a/0/5/6 entry 1239): Black 2's data/field_scripts/1239.s, unchanged except for one
// call in Script_816 (talking to an eye-contact trainer NPC, script 3000 + id or 5000 + id) and its subroutine at the end.
// Pokémon Emerald NDS only (src/field_scripts/emerald/: Sapphire and Ruby keep Black 2's file): Emerald's rematches
// (emerald_rematch, 2026-10-18; notes/EMERALD_REMATCH.md). A beaten trainer of Emerald's rematch table
// (data/emerald/hoenn_rematch.json) with 5 badges or more, once a day: Emerald's rematch line (message type 100, or 104
// for the second NPC of a pair), YES / NO, the battle with today's tier (b2tools/patches/emerald_rematch.c loads the
// tier's record and party for the trainer's own id), then Emerald's after-rematch line (101 / 105); a double tier with
// one Pokémon able to battle: Emerald's "need two" line (102 / 106). Fought today: the after-rematch line. No rematch
// now (fewer than 5 badges, or not in the table): Black 2's after line, as before. No eye-contact rematches (talk only).
#include "asm/field_script.inc"
#include "hoenn_rematch.inc"

    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_1
    ScriptEntry Script_816
    ScriptEntry Script_817
    ScriptEntriesEnd

Script_1:
    WorkSetConst 0x8020, 0
    WorkSetConst 0x8021, 0
    WorkSetConst 0x8022, 0
    WorkSetConst 0x8023, 0
    WorkSetConst 0x8024, 0

Script_816:
    ActorsPauseAll
    SEPlay SEQ_SE_MESSAGE
    ActorSetEyeToEye
    VMCall L_0F57
    ActorGetTrainerID 0x8020
    TrainerFlagGet 0x8020, 0x8010
    VMStackPush 0x8010
    VMStackPushConst 1
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_0D5F
    VMCall L_EmRematch                  // Hoenn (Emerald): a rematch? 0x8024 != 0: it is done, end the script
    WorkCmpConst 0x8024, 0
    VMJumpIf CMP_NE, L_0E54
    TrainerGetFieldAction 0x8020, 0x8010
    VMStackPush 0x8010
    VMStackPushConst 1
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_0D34
    VMCall L_0EE9
    VMJump L_0D59

L_0D34:
    VMStackPush 0x8010
    VMStackPushConst 2
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_0D53
    VMCall L_0F49
    VMJump L_0D59

L_0D53:
    VMCall L_0ED3

L_0D59:
    VMJump L_0E54

L_0D5F:
    WorkSetConst 0x8025, 0
    WorkSetConst 0x8026, 0
    TrainerGetBattleType_008A 0x8020, 0x8025
    PokePartyGetCount 0x8026, 2
    VMStackPush 0x8025
    VMStackPushConst 1
    VMStackCmp CMP_EQ
    VMStackPush 0x8026
    VMStackPushConst 2
    VMStackCmp CMP_LT
    VMStackCmp CMP_AND
    VMJumpIf CMP_STACK, L_0DA6
    VMCall L_0E9F
    VMJump L_0E48

L_0DA6:
    VMStackPush 0x8025
    VMStackPushConst 2
    VMStackCmp CMP_EQ
    VMStackPush 0x8026
    VMStackPushConst 3
    VMStackCmp CMP_LT
    VMStackCmp CMP_AND
    VMJumpIf CMP_STACK, L_0DD5
    VMCall L_0EB9
    VMJump L_0E48

L_0DD5:
    VMStackPush 0x8025
    VMStackPushConst 3
    VMStackCmp CMP_EQ
    VMStackPush 0x8026
    VMStackPushConst 3
    VMStackCmp CMP_LT
    VMStackCmp CMP_AND
    VMJumpIf CMP_STACK, L_0E04
    VMCall L_0EB9
    VMJump L_0E48

L_0E04:
    VMCall L_0E5A
    TrainerGetFieldAction 0x8020, 0x8010
    VMStackPush 0x8010
    VMStackPushConst 1
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_0E2F
    VMCall L_0EE9
    VMJump L_0E48

L_0E2F:
    VMStackPush 0x8010
    VMStackPushConst 2
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_0E48
    VMCall L_0F21

L_0E48:
    WorkSetConst 0x8026, 0
    WorkSetConst 0x8025, 0

L_0E54:
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

L_0E5A:
    TrainerBGMPlayPush 0x8020
    TrainerGetMessageTypes 0x8021, 0x8022, 0x8023
    TrainerSayMessage 0x8020, 0x8021, 0x8011
    ActorMsgClose
    CallTrainerBattle 0x8020, 0, 0
    TrainerBattleIsVictory 0x8010
    VMStackPush 0x8010
    VMStackPushConst 1
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_0E97
    CallTrainerBattleEnd
    VMJump L_0E99

L_0E97:
    CallTrainerLose

L_0E99:
    TrainerFlagSet 0x8020
    VMReturn

L_0E9F:
    ActorGetTrainerID 0x8010
    TrainerGetMessageTypes 0x8021, 0x8022, 0x8023
    TrainerSayMessage 0x8020, 0x8023, 0x8011
    LastKeyWait
    ActorMsgClose
    VMReturn

L_0EB9:
    ActorGetTrainerID 0x8020
    TrainerGetMessageTypes 0x8021, 0x8022, 0x8023
    TrainerSayMessage 0x8020, 0x8023, 0x8011
    LastKeyWait
    ActorMsgClose
    VMReturn

L_0ED3:
    TrainerGetMessageTypes 0x8021, 0x8022, 0x8023
    TrainerSayMessage 0x8020, 0x8022, 0x8011
    LastKeyWait
    ActorMsgClose
    VMReturn

L_0EE9:
    TrainerSayMessage 0x8020, 13, 0x8011
    ActorMsgClose
    FadeEx 3, 0, 16, 2
    FadeExWait
    PokePartyRecoverAll
    MEPlay SEQ_ME_ASA
    MEWait
    FadeEx 3, 16, 0, 2
    FadeExWait
    TrainerSayMessage 0x8020, 14, 0x8011
    LastKeyWait
    ActorMsgClose
    VMReturn

L_0F21:
    TrainerSayMessage 0x8020, 15, 0x8011
    ActorMsgClose
    TrainerGetPrizeItem 0x8020, 0x8000
    WorkSetConst 0x8001, 1
    RTCallGlobal 2805
    TrainerSayMessage 0x8020, 16, 0x8011
    LastKeyWait
    ActorMsgClose
    VMReturn

L_0F49:
    TrainerSayMessage 0x8020, 16, 0x8011
    LastKeyWait
    ActorMsgClose
    VMReturn

L_0F57:
    ActorGetMoveCode 0x8010, 0x8011
    WorkCmpConst 0x8010, 51
    VMJumpIf CMP_EQ, L_0F70
    VMJump L_0F7C

L_0F70:
    VMCall L_0FFA
    VMJump L_0FF8

L_0F7C:
    WorkCmpConst 0x8010, 52
    VMJumpIf CMP_EQ, L_0F8F
    VMJump L_0F9B

L_0F8F:
    VMCall L_0FFA
    VMJump L_0FF8

L_0F9B:
    WorkCmpConst 0x8010, 53
    VMJumpIf CMP_EQ, L_0FAE
    VMJump L_0FBA

L_0FAE:
    VMCall L_0FFA
    VMJump L_0FF8

L_0FBA:
    WorkCmpConst 0x8010, 54
    VMJumpIf CMP_EQ, L_0FCD
    VMJump L_0FD9

L_0FCD:
    VMCall L_0FFA
    VMJump L_0FF8

L_0FD9:
    WorkCmpConst 0x8010, 85
    VMJumpIf CMP_EQ, L_0FEC
    VMJump L_0FF8

L_0FEC:
    VMCall L_0FFA
    VMJump L_0FF8

L_0FF8:
    VMReturn

L_0FFA:
    ActorCmdExec 0x8011, Movement_1088
    ActorCmdWait
    PlayerGetDir 0x8010
    WorkCmpConst 0x8010, 0
    VMJumpIf CMP_EQ, L_101B
    VMJump L_1027

L_101B:
    ActorSetMoveCode 0x8011, 15
    VMJump L_1084

L_1027:
    WorkCmpConst 0x8010, 1
    VMJumpIf CMP_EQ, L_103A
    VMJump L_1046

L_103A:
    ActorSetMoveCode 0x8011, 14
    VMJump L_1084

L_1046:
    WorkCmpConst 0x8010, 2
    VMJumpIf CMP_EQ, L_1059
    VMJump L_1065

L_1059:
    ActorSetMoveCode 0x8011, 17
    VMJump L_1084

L_1065:
    WorkCmpConst 0x8010, 3
    VMJumpIf CMP_EQ, L_1078
    VMJump L_1084

L_1078:
    ActorSetMoveCode 0x8011, 16
    VMJump L_1084

L_1084:
    VMReturn
    .balign 4, 0

Movement_1088:
    Move 101, 1
    MoveEnd

Script_817:
    ActorsPauseAll
    TrainerGetBattleType 0x8010
    VMStackPush 0x8010
    VMStackPushConst 0
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_10B5
    VMCall L_1156
    VMJump L_110C

L_10B5:
    VMStackPush 0x8010
    VMStackPushConst 1
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_10D4
    VMCall L_11BD
    VMJump L_110C

L_10D4:
    VMStackPush 0x8010
    VMStackPushConst 2
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_10F3
    VMCall L_124E
    VMJump L_110C

L_10F3:
    VMStackPush 0x8010
    VMStackPushConst 3
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_110C
    VMCall L_12E5

L_110C:
    TrainerEyeGetTrainerID 0, 0x8020
    TrainerGetFieldAction 0x8020, 0x8010
    VMStackPush 0x8010
    VMStackPushConst 1
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_1137
    VMCall L_0EE9
    VMJump L_1150

L_1137:
    VMStackPush 0x8010
    VMStackPushConst 2
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_1150
    VMCall L_0F21

L_1150:
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

L_1156:
    WorkSetConst 0x8027, 0
    WorkSetConst 0x8028, 0
    TrainerEyeGetTrainerID 0, 0x8027
    TrainerBGMPlayPush 0x8027
    TrainerEyeEventInit 0
    TrainerEyeEventStart
    TrainerGetActorID 0, 0x8028
    TrainerSayMessage 0x8027, 0, 0x8028
    ActorMsgClose
    CallTrainerBattle 0x8027, 0, 0
    TrainerBattleIsVictory 0x8010
    VMStackPush 0x8010
    VMStackPushConst 1
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_11A9
    CallTrainerBattleEnd
    VMJump L_11AB

L_11A9:
    CallTrainerLose

L_11AB:
    TrainerFlagSet 0x8027
    VMReturn
    WorkSetConst 0x8028, 0
    WorkSetConst 0x8027, 0

L_11BD:
    WorkSetConst 0x8029, 0
    WorkSetConst 0x802a, 0
    WorkSetConst 0x802b, 0
    TrainerEyeGetTrainerID 0, 0x8029
    TrainerEyeGetTrainerID 1, 0x802a
    TrainerBGMPlayPush 0x8029
    TrainerEyeEventInit 0
    TrainerEyeEventInit 1
    TrainerEyeEventStart
    TrainerGetActorID 0, 0x802b
    TrainerSayMessage 0x8029, 3, 0x802b
    ActorMsgClose
    TrainerGetActorID 1, 0x802b
    TrainerSayMessage 0x802a, 7, 0x802b
    ActorMsgClose
    CallTrainerBattle 0x8029, 0x802a, 0
    TrainerBattleIsVictory 0x8010
    VMStackPush 0x8010
    VMStackPushConst 1
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_1230
    CallTrainerBattleEnd
    VMJump L_1232

L_1230:
    CallTrainerLose

L_1232:
    TrainerFlagSet 0x8029
    TrainerFlagSet 0x802a
    VMReturn
    WorkSetConst 0x802b, 0
    WorkSetConst 0x802a, 0
    WorkSetConst 0x8029, 0

L_124E:
    WorkSetConst 0x802c, 0
    WorkSetConst 0x802d, 0
    WorkSetConst 0x802e, 0
    TrainerEyeGetTrainerID 0, 0x802c
    TrainerEyeGetTrainerID 1, 0x802d
    TrainerBGMPlayPush 0x802c
    TrainerEyeEventInit 0
    TrainerEyeEventStart
    TrainerGetActorID 0, 0x802e
    TrainerSayMessage 0x802c, 0, 0x802e
    ActorMsgClose
    TrainerBGMPlay 0x802d
    TrainerEyeEventInit 1
    TrainerEyeEventStart
    TrainerGetActorID 1, 0x802e
    TrainerSayMessage 0x802d, 0, 0x802e
    ActorMsgClose
    CallTrainerBattle 0x802c, 0x802d, 0
    TrainerBattleIsVictory 0x8010
    VMStackPush 0x8010
    VMStackPushConst 1
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_12C7
    CallTrainerBattleEnd
    VMJump L_12C9

L_12C7:
    CallTrainerLose

L_12C9:
    TrainerFlagSet 0x802c
    TrainerFlagSet 0x802d
    VMReturn
    WorkSetConst 0x802e, 0
    WorkSetConst 0x802d, 0
    WorkSetConst 0x802c, 0

L_12E5:
    WorkSetConst 0x802f, 0
    WorkSetConst 0x8030, 0
    WorkSetConst 0x8031, 0
    WorkSetConst 0x8032, 0
    ActorPairGetTrID 0x802f
    TrainerEyeGetTrainerID 0, 0x8030
    TrainerEyeGetTrainerID 1, 0x8031
    TrainerBGMPlayPush 0x8030
    TrainerEyeEventInit 0
    TrainerEyeEventStart
    TrainerGetActorID 0, 0x8032
    TrainerSayMessage 0x8030, 0, 0x8032
    ActorMsgClose
    TrainerBGMPlay 0x8031
    TrainerEyeEventInit 1
    TrainerEyeEventStart
    TrainerGetActorID 1, 0x8032
    TrainerSayMessage 0x8031, 0, 0x8032
    ActorMsgClose
    CallTrainerMultiBattle 0x802f, 0x8030, 0x8031, 0
    TrainerBattleIsVictory 0x8010
    VMStackPush 0x8010
    VMStackPushConst 1
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_1385
    PokePartyGetCount 0x8008, 2
    VMStackPush 0x8008
    VMStackPushConst 0
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_137D
    PokePartyRecoverAll

L_137D:
    CallTrainerBattleEnd
    VMJump L_1387

L_1385:
    CallTrainerLose

L_1387:
    TrainerFlagSet 0x8030
    TrainerFlagSet 0x8031
    VMReturn
    .byte 0x28
    .byte 0x00
    .byte 0x32
    .byte 0x80
    .byte 0x00
    .byte 0x00
    .byte 0x28
    .byte 0x00
    .byte 0x31
    .byte 0x80
    .byte 0x00
    .byte 0x00
    .byte 0x28
    .byte 0x00
    .byte 0x30
    .byte 0x80
    .byte 0x00
    .byte 0x00
    .byte 0x28
    .byte 0x00
    .byte 0x2f
    .byte 0x80
    .byte 0x00
    .byte 0x00
    .balign 4, 0

// ---- Hoenn (Emerald): Emerald's rematches (see the top). In: 0x8020 the trainer, 0x8011 the NPC talked to. Out: 0x8024
// RM_NONE (the caller goes on to the trainer's after line) or the rematch state (the caller ends the script).
L_EmRematch:
    EmRematch 0x8024, RM_QUERY, 0x8020
    WorkCmpConst 0x8024, RM_NONE
    VMJumpIf CMP_EQ, L_EmRmReturn
    WordSetPlayerName 0
    TrainerGetMessageTypes 0x8021, 0x8022, 0x8023
    EmRematch 0x8025, RM_MSGBASE, 0x8021        // 0x8025: the NPC's rematch intro type (100 or 104)
    WorkCmpConst 0x8024, RM_POST
    VMJumpIf CMP_EQ, L_EmRmPost
    WorkCmpConst 0x8024, RM_DOUBLE
    VMJumpIf CMP_NE, L_EmRmAsk
    PokePartyGetCount 0x8026, 2
    WorkCmpConst 0x8026, 2
    VMJumpIf CMP_GE, L_EmRmAsk
    WorkAdd 0x8025, 2                           // "you need two Pokémon" (102 / 106)
    VMJump L_EmRmSay

L_EmRmAsk:
    TrainerSayMessage 0x8020, 0x8025, 0x8011    // Emerald's rematch intro, then YES / NO
    YesNoWin 0x8026
    ActorMsgClose
    WorkCmpConst 0x8026, 0
    VMJumpIf CMP_NE, L_EmRmReturn               // NO: nothing more
    EmRematch 0x8026, RM_ARM, 0x8020
    CallTrainerBattle 0x8020, 0, 0
    EmRematch 0x8026, RM_DISARM, 0
    TrainerBattleIsVictory 0x8010
    WorkCmpConst 0x8010, 1
    VMJumpIf CMP_EQ, L_EmRmWon
    CallTrainerLose                             // (as L_0E5A: the whiteout)
    VMReturn

L_EmRmWon:
    CallTrainerBattleEnd
    EmRematch 0x8026, RM_WON, 0x8020
    WordSetPlayerName 0

L_EmRmPost:
    WorkAdd 0x8025, 1                           // the after-rematch line (101 / 105)

L_EmRmSay:
    TrainerSayMessage 0x8020, 0x8025, 0x8011
    LastKeyWait
    ActorMsgClose

L_EmRmReturn:
    VMReturn
    .balign 4, 0
