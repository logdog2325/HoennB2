// Global scripts 2000-2006 (a/0/5/6 entry 1230): Black 2's data/field_scripts/1230.s, unchanged except for one call at
// the start of Script_2 (2001, the blackout: the player wakes up in front of the Center's nurse, who heals the party).
// Sapphire's EventScript_WhiteOut runs EventScript_ResetMrBriney, so his boat is where you can reach it after fainting;
// Black 2 has no such hook and the reset was never run (heal in Rustboro, sail to Dewford, faint in Granite Cave:
// you woke up in Rustboro with his boat in Dewford, stranded). Sub_BlackoutBriney below puts Mr. Briney and his boat on
// the side of the sea of the Center you wake up in (Sapphire uses VAR_BRINEY_LOCATION from your last Center visit,
// which is the same place before Norman; Rusturf Tunnel's land route can only make it differ, never strand you).
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_story.inc"

    ScriptEntry Script_1
    ScriptEntry Script_2
    ScriptEntry Script_3
    ScriptEntry Script_4
    ScriptEntry Script_5
    ScriptEntry Script_6
    ScriptEntry Script_7
    ScriptEntriesEnd

Script_1:
    ActorsPauseAll
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_2:
    ActorsPauseAll
    VMCall Sub_BlackoutBriney                    // Hoenn: Mr. Briney's boat (see the top)
    WorkSetConst 0x8020, 0
    WorkSetConst 0x8021, 0
    WorkSetConst 0x8022, 0
    FadeInBlackQ_
    FadeWait
    PlayerSetSpecialSequence 64
    ActorCmdExec 255, Movement_0120
    ActorCmdWait
    PlayerSetSpecialSequence 8
    ActorCmdExec 255, Movement_0128
    ActorCmdWait
    PlayerGetGPos 0x8020, 0x8021
    WorkSub 0x8021, 2
    ActorFindByGPos 0x8011, 0x8022, 0x8020, 0, 0x8021
    PokePartyRecoverAll
    VMStackPush 0x8022
    VMStackPushConst 1
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_009B
    // "First, let's restore your Pokémon\nto full health."
    ActorMsg MSGFILE_SCRIPT, 19, 0x8011, 0, 0
    VMCall L_0144
    ActorMsgClose

L_009B:
    PlayerSetSpecialSequence 64
    ActorCmdExec 255, Movement_0130
    ActorCmdWait
    PlayerSetSpecialSequence 8
    VMStackPush 0x8022
    VMStackPushConst 1
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_0105
    ActorCmdExec 0x8011, Movement_0138
    ActorCmdWait
    TrainerCardHasBadge 0x8010, 0
    VMStackPush 0x8010
    VMStackPushConst 0
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_00F5
    // "Please visit a Pokémon Center when your\nPokémon's HP goes down.[f000]븁\u0000\nIf you're planning to travel any\ndistance, you should stock up on Potions[f000]븀\u0000\nat a Poké Mart.[f000]븁\u0000\nGood luck, Trainer!"
    ActorMsg MSGFILE_SCRIPT, 20, 0x8011, 0, 0
    VMJump L_0101

L_00F5:
    // "There! All happy and healthy![f000]븁\u0000\nGood luck and take care!"
    ActorMsg MSGFILE_SCRIPT, 21, 0x8011, 0, 0

L_0101:
    LastKeyWait
    ActorMsgClose

L_0105:
    WorkSetConst 0x8022, 0
    WorkSetConst 0x8021, 0
    WorkSetConst 0x8020, 0
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt
    .balign 4, 0

Movement_0120:
    Move 102, 1
    MoveEnd

Movement_0128:
    Move 0, 1
    MoveEnd

Movement_0130:
    Move 104, 1
    MoveEnd

Movement_0138:
    Move 100, 1
    Move 62, 1
    MoveEnd

L_0144:
    WorkSetConst 0x8023, 0
    ActorCmdExec 0x8011, Movement_0170
    ActorCmdWait
    PokePartyGetCount 0x8023, 1
    PokecenPlayHealingSequence 0x8023
    ActorCmdExec 0x8011, Movement_0178
    ActorCmdWait
    VMReturn
    .byte 0x28
    .byte 0x00
    .byte 0x23
    .byte 0x80
    .balign 4, 0

Movement_0170:
    Move 0, 1
    MoveEnd

Movement_0178:
    Move 1, 1
    MoveEnd

Script_3:
    WorkSetConst 0x8024, 0
    SaveDataCheckRequired 0x8024
    WorkCmpConst 0x8024, 1
    VMJumpIf CMP_EQ, L_019D
    VMJump L_01A9

L_019D:
    VMCall Script_4
    VMJump L_01C8

L_01A9:
    WorkCmpConst 0x8024, 0
    VMJumpIf CMP_EQ, L_01BC
    VMJump L_01C8

L_01BC:
    WorkSetConst 0x8000, 0
    VMJump L_01C8

L_01C8:
    RTEndGlobal
    WorkSetConst 0x8024, 0
    VMHalt

Script_4:
    VMCall L_01DC
    RTEndGlobal
    VMHalt

L_01DC:
    WorkSetConst 0x8025, 0
    WorkSetConst 0x8026, 0
    WorkSetConst 0x8027, 0
    WorkSetConst 0x8028, 0
    WorkSetConst 0x8029, 0
    WorkSetConst 0x8001, 0
    WorkSetConst 0x8026, 0
    WorkSetConst 0x8027, 0
    WorkSetConst 0x8004, 0
    WorkSetConst 0x8029, 0
    SaveDataGetStatus 0x8026, 0x8027, 0x8028
    FieldSubscreenChange 0
    // "Would you like to save the game?"
    SystemMsg 2, 2
    YesNoWin 0x8029
    VMStackPush 0x8029
    VMStackPushConst 0
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_0247
    WorkSetConst 0x8025, 1

L_0247:
    InfoMsgClose
    VMStackPush 0x8025
    VMStackPushConst 1
    VMStackCmp CMP_EQ
    VMStackPush 0x8026
    VMStackPushConst 1
    VMStackCmp CMP_EQ
    VMStackPush 0x8027
    VMStackPushConst 1
    VMStackCmp CMP_EQ
    VMStackCmp CMP_AND
    VMStackCmp CMP_AND
    VMJumpIf CMP_STACK, L_028A
    // "There is already a saved game file.\nIt is impossible to save.[f000]븁\u0000\nPlease refer to the Instruction\nBooklet for details.[f000]븁\u0000\nPress Up + SELECT + B Button on\nthe title screen if you want to erase[f000]븀\u0000\nthe current saved game file.[f000]븁\u0000"
    SystemMsg 9, 2
    InfoMsgClose
    WorkSetConst 0x8025, 0

L_028A:
    VMStackPush 0x8025
    VMStackPushConst 1
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_0329
    WorkCmpConst 0x8028, 0
    VMJumpIf CMP_EQ, L_02B0
    VMJump L_02BC

L_02B0:
    // "Saving...\nDon't turn off the power."
    SystemMsgAsync 4, 2
    VMJump L_02DB

L_02BC:
    WorkCmpConst 0x8028, 1
    VMJumpIf CMP_EQ, L_02CF
    VMJump L_02DB

L_02CF:
    // "Saving a lot of data...\nDon't turn off the power."
    SystemMsgAsync 10, 2
    VMJump L_02DB

L_02DB:
    VMSleep 1
    MsgSetLoadingSpinner 0
    SaveDataWrite 0x8029
    SEStop
    InfoMsgClose
    VMStackPush 0x8029
    VMStackPushConst 1
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_031B
    SEPlay SEQ_SE_SAVE
    WordSetPlayerName 0
    // "[f000]Ā\u0001\u0000 saved the game."
    SystemMsg 5, 2
    MsgWaitAdvance
    InfoMsgClose
    WorkSetConst 0x8000, 0
    VMJump L_0329

L_031B:
    // "Save error.[f000]븁\u0000"
    SystemMsg 7, 2
    InfoMsgClose
    WorkSetConst 0x8000, 1

L_0329:
    VMStackPush 0x8025
    VMStackPushConst 1
    VMStackCmp CMP_NE
    VMJumpIf CMP_STACK, L_0342
    WorkSetConst 0x8000, 1

L_0342:
    FieldSubscreenReturn
    VMReturn
    WorkSetConst 0x8029, 0
    WorkSetConst 0x8028, 0
    WorkSetConst 0x8027, 0
    WorkSetConst 0x8026, 0
    WorkSetConst 0x8025, 0

Script_5:
    VMCall L_036E
    RTEndGlobal
    VMHalt

L_036E:
    GameCommGetStatus 0x8010
    VMStackPush 0x8010
    VMStackPushConst 0
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_038D
    WorkSetConst 0x8000, 0
    VMReturn

L_038D:
    VMStackPush 0x8010
    VMStackPushConst 2
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_03D9
    // "It looks like you are connecting\nwith somebody. Is it OK to disconnect?"
    SystemMsg 15, 2
    YesNoWin 0x8010
    VMStackPush 0x8010
    VMStackPushConst 1
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_03C7
    WorkSetConst 0x8000, 1
    InfoMsgClose
    VMReturn

L_03C7:
    // "Ending communication.\nPlease wait."
    SystemMsg 16, 2
    GameCommDisconnect 0x8000
    InfoMsgClose
    VMJump L_03DD

L_03D9:
    GameCommDisconnect 0x8000

L_03DD:
    VMReturn

Script_6:
    // "Wireless communications are turned OFF.\nTurn wireless communications ON[f000]븀\u0000\nin the System Settings.[f000]븀\u0000\nError code: 50699[f000]븁\u0000"
    SystemMsg 22, 2
    InfoMsgClose
    RTEndGlobal

Script_7:
    ActorsPauseAll
    WorkSetConst 0x802a, 0
    WorkSetConst 0x802a, 24
    WorkAdd 0x802a, 0x8000
    WordSetPlayerName 0
    WordSetItemName 1, 0x8001
    SystemMsg 0x802a, 2
    LastKeyWait
    InfoMsgClose
    WorkSetConst 0x802a, 0
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt
    .balign 4, 0

Sub_BlackoutBriney:
    h_goto_if_unset FLAG_MR_BRINEY_SAILING_INTRO, L_BB_Done     // his boat service has not started (story as is)
    h_goto_if_set FLAG_DEFEATED_PETALBURG_GYM, L_BB_Done         // after Norman he is gone and you can Surf
    RTGetZoneID 0x8024
    h_goto_if_eq 0x8024, 398, L_BB_House        // Oldale, Petalburg, Rustboro's Centers: his house on Route 104
    h_goto_if_eq 0x8024, 413, L_BB_House
    h_goto_if_eq 0x8024, 425, L_BB_House
    h_goto_if_eq 0x8024, 1, L_BB_Dewford        // Dewford's Center
    h_goto_if_eq 0x8024, 435, L_BB_Route109     // Slateport, Mauville, Verdanturf, Fallarbor, Lavaridge: Route 109
    h_goto_if_eq 0x8024, 115, L_BB_Route109
    h_goto_if_eq 0x8024, 454, L_BB_Route109
    h_goto_if_eq 0x8024, 41, L_BB_Route109
    h_goto_if_eq 0x8024, 99, L_BB_Route109
L_BB_Done:
    VMReturn
L_BB_House:
    VMCall L_MoveMrBrineyToHouse
    VMReturn
L_BB_Dewford:
    VMCall L_MoveMrBrineyToDewford
    VMReturn
L_BB_Route109:
    VMCall L_MoveMrBrineyToRoute109
    VMReturn
    .balign 4, 0
#include "common/briney.inc"
