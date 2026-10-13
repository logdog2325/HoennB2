// Global scripts 2280-2299 (a/0/5/6 entry 1236; text file 615), Emerald builds only (src/field_scripts/emerald/):
// Black 2's data/field_scripts/1236.s (its tutors 2280-2288, unchanged: no Hoenn script calls them) with Emerald's
// mechanics appended as 2289-2292 (emerald_mech, 2026-10-12; src/include/hoenn_emerald.inc has the macros that call
// them, b2tools/patches/emerald_mech.py the findings). Their new lines are 615's lines 56-60
// (src/text/emerald/overrides_emerald_mech.json); 615's lines 10-16 are Black 2's own move-learning lines.
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_story.inc"
#include "hoenn_emerald.inc"


    ScriptEntry Script_1
    ScriptEntry Script_2
    ScriptEntry Script_3
    ScriptEntry Script_4
    ScriptEntry Script_5
    ScriptEntry Script_6
    ScriptEntry Script_7
    ScriptEntry Script_8
    ScriptEntry Script_9
    ScriptEntry EM_ScriptMoveTutor      // 2289 EM_GLOBAL_MOVE_TUTOR
    ScriptEntry EM_ScriptTagBattle      // 2290 EM_GLOBAL_TAG_BATTLE
    ScriptEntry EM_ScriptClosedDoor     // 2291 EM_GLOBAL_CLOSED_DOOR (a door or sign entity)
    ScriptEntry EM_ScriptClosedDoorMsg  // 2292 its message, for RTCallGlobal (em_closed_door)
    ScriptEntry AW_ScriptZoneInit       // 2293 AW_GLOBAL_ZONE_INIT: a route's zone init (the abnormal weather, emerald_ch12_13)
    ScriptEntry AW_ScriptCleanup        // 2294 AW_GLOBAL_CLEANUP: a route's frame script (its end after Kyogre / Groudon)
    ScriptEntry AW_ScriptCaveInit       // 2295 AW_GLOBAL_CAVE_INIT: Terra / Marine Cave's zone init (the 1000 steps)
    ScriptEntry SZ_ScriptWorker         // 2296: the Safari Zone's construction workers (emerald_ch12_13)
    ScriptEntry SZ_ScriptAttendant      // 2297: the Safari Zone expansion's attendant (emerald_ch12_13)
    ScriptEntriesEnd
    WorkSetConst 0x8020, 0
    WorkSetConst 0x8021, 0
    WorkSetConst 0x8022, 0
    WorkSetConst 0x8023, 0
    WorkSetConst 0x8024, 0

Script_1:
    VMCall L_004C
    RTEndGlobal

L_004C:
    // "Drayden: If you wish, I can teach your\nPokémon the strongest[f000]븀\u0000\nDragon-type move.[f000]븁\u0000\nWould you like your Pokémon to learn\nthat move?"
    ActorMsg MSGFILE_SCRIPT, 17, 0x8011, 0, 0
    YesNoWin 0x8010
    VMStackPush 0x8010
    VMStackPushConst 1
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_0081
    // "Understood.\nCome again if you change your mind."
    ActorMsg MSGFILE_SCRIPT, 18, 0x8011, 0, 0
    LastKeyWait
    ActorMsgClose
    VMReturn

L_0081:
    MoveTutorCheckParty 0, 0x8010
    VMStackPush 0x8010
    VMStackPushConst 1
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_00B2
    // "I see...[f000]븁\u0000\nBut there are no Pokémon with\nyou right now that can learn this move."
    ActorMsg MSGFILE_SCRIPT, 20, 0x8011, 0, 0
    LastKeyWait
    ActorMsgClose
    VMReturn
    VMJump L_00D7

L_00B2:
    VMStackPush 0x8010
    VMStackPushConst 2
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_00D7
    // "Hmm...[f000]븁\u0000\nThis Pokémon can learn this move, but\nyour bond of friendship is not yet[f000]븀\u0000\nstrong enough.[f000]븁\u0000\nThat means I cannot teach\nit this move."
    ActorMsg MSGFILE_SCRIPT, 19, 0x8011, 0, 0
    LastKeyWait
    ActorMsgClose
    VMReturn

L_00D7:
    // "Which Pokémon should\nlearn this move?[f000]븁\u0000"
    ActorMsg MSGFILE_SCRIPT, 21, 0x8011, 0, 0
    ActorMsgClose
    MoveTutorCallPokeSelect 0, 0x8010, 0x8020
    VMStackPush 0x8010
    VMStackPushConst 0
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_0112
    // "Understood.\nCome again if you change your mind."
    ActorMsg MSGFILE_SCRIPT, 18, 0x8011, 0, 0
    LastKeyWait
    ActorMsgClose
    VMReturn

L_0112:
    PokePartyIsEgg 0x8010, 0x8020
    VMStackPush 0x8010
    VMStackPushConst 1
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_013D
    // "That's an interesting request, but...\nNot even I can teach a move to an Egg."
    ActorMsg MSGFILE_SCRIPT, 23, 0x8011, 0, 0
    LastKeyWait
    ActorMsgClose
    VMReturn

L_013D:
    MoveTutorCheckPkm 0, 0x8020, 0x8010
    WorkCmpConst 0x8010, 2
    VMJumpIf CMP_EQ, L_0158
    VMJump L_0170

L_0158:
    // "Hmm...[f000]븁\u0000\nThis Pokémon can learn this move, but\nyour bond of friendship is not yet[f000]븀\u0000\nstrong enough.[f000]븁\u0000\nThat means I cannot teach\nit this move."
    ActorMsg MSGFILE_SCRIPT, 19, 0x8011, 0, 0
    LastKeyWait
    ActorMsgClose
    VMReturn
    VMJump L_01CB

L_0170:
    WorkCmpConst 0x8010, 1
    VMJumpIf CMP_EQ, L_0183
    VMJump L_019B

L_0183:
    // "I'm very sorry, but...[f000]븁\u0000\nThis Pokémon cannot learn this move."
    ActorMsg MSGFILE_SCRIPT, 22, 0x8011, 0, 0
    LastKeyWait
    ActorMsgClose
    VMReturn
    VMJump L_01CB

L_019B:
    WorkCmpConst 0x8010, 3
    VMJumpIf CMP_EQ, L_01AE
    VMJump L_01CB

L_01AE:
    WordSetMoveName 0, MOVE_DRACO_METEOR
    // "Hmm... It looks like this Pokémon\nalready knows [f000]ć\u0001\u0000."
    ActorMsg MSGFILE_SCRIPT, 24, 0x8011, 0, 0
    LastKeyWait
    ActorMsgClose
    VMReturn
    VMJump L_01CB

L_01CB:
    WorkSetConst 0x8021, 434
    WorkSetConst 0x8022, 0
    WorkSetConst 0x8023, 1
    VMCall L_098A
    VMStackPush 0x8010
    VMStackPushConst 1
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_0206
    // "Drayden: Draco Meteor's power is\nexceptional, but using it lowers[f000]븀\u0000\nthe user's Sp. Atk stat."
    ActorMsg MSGFILE_SCRIPT, 25, 0x8011, 0, 0
    LastKeyWait
    ActorMsgClose

L_0206:
    VMReturn

Script_2:
    ActorsPauseAll
    SEPlay SEQ_SE_MESSAGE
    ActorSetEyeToEye
    VMCall L_021C
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

L_021C:
    // "Your quest for power has brought\nyou here...[f000]븁\u0000\nVery well.[f000]븁\u0000\nLet me reward your passion with some\nabsolutely astounding moves.[f000]븁\u0000\nThey're the ultimate moves![f000]븁\u0000\nShall I teach them to\nyour Pokémon?"
    ParentActorMsg MSGFILE_SCRIPT, 26, 0, 0
    YesNoWin 0x8010
    VMStackPush 0x8010
    VMStackPushConst 1
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_024D
    // "Hmm... Well, that is fine, as well.\nVisit if you have a change of heart."
    ParentActorMsg MSGFILE_SCRIPT, 29, 0, 0
    LastKeyWait
    ActorMsgClose
    VMReturn

L_024D:
    MoveTutorCheckParty 1, 0x8010
    VMStackPush 0x8010
    VMStackPushConst 1
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_027C
    // "The Pokémon with you can't\nlearn these moves![f000]븁\u0000\nGo talk to my wife! Keh!!"
    ParentActorMsg MSGFILE_SCRIPT, 28, 0, 0
    LastKeyWait
    ActorMsgClose
    VMReturn
    VMJump L_029F

L_027C:
    VMStackPush 0x8010
    VMStackPushConst 2
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_029F
    // "The bond with your Pokémon\nis not strong enough! Keh!"
    ParentActorMsg MSGFILE_SCRIPT, 33, 0, 0
    LastKeyWait
    ActorMsgClose
    VMReturn

L_029F:
    // "Well, which Pokémon should I teach?[f000]븁\u0000"
    ParentActorMsg MSGFILE_SCRIPT, 30, 0, 0
    ActorMsgClose
    MoveTutorCallPokeSelect 1, 0x8010, 0x8020
    VMStackPush 0x8010
    VMStackPushConst 0
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_02D6
    // "Hmm... Well, that is fine, as well.\nVisit if you have a change of heart."
    ParentActorMsg MSGFILE_SCRIPT, 29, 0, 0
    LastKeyWait
    ActorMsgClose
    VMReturn

L_02D6:
    PokePartyIsEgg 0x8010, 0x8020
    VMStackPush 0x8010
    VMStackPushConst 1
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_02FF
    // "Teach a move to an Egg?\nImpossible, even for me! Keh!"
    ParentActorMsg MSGFILE_SCRIPT, 32, 0, 0
    LastKeyWait
    ActorMsgClose
    VMReturn

L_02FF:
    MoveTutorCheckPkm 1, 0x8020, 0x8010
    WorkCmpConst 0x8010, 2
    VMJumpIf CMP_EQ, L_031A
    VMJump L_0330

L_031A:
    // "The bond with your Pokémon\nis not strong enough! Keh!"
    ParentActorMsg MSGFILE_SCRIPT, 33, 0, 0
    LastKeyWait
    ActorMsgClose
    VMReturn
    VMJump L_0382

L_0330:
    WorkCmpConst 0x8010, 1
    VMJumpIf CMP_EQ, L_0343
    VMJump L_0359

L_0343:
    // "That Pokémon can't learn a move!\nGo talk to my wife! Keh!"
    ParentActorMsg MSGFILE_SCRIPT, 31, 0, 0
    LastKeyWait
    ActorMsgClose
    VMReturn
    VMJump L_0382

L_0359:
    WorkCmpConst 0x8010, 3
    VMJumpIf CMP_EQ, L_036C
    VMJump L_0382

L_036C:
    // "That Pokémon already knows\nthat move! Keh!"
    ParentActorMsg MSGFILE_SCRIPT, 34, 0, 0
    LastKeyWait
    ActorMsgClose
    VMReturn
    VMJump L_0382

L_0382:
    MoveTutorGetMoveID 1, 0x8020, 0x8021
    WordSetPartyPokeName 0, 0x8020
    WordSetMoveName 1, 0x8021
    // "I should teach [f000]ć\u0001\u0001 to\n[f000]ā\u0001\u0000, right? Keh!"
    ParentActorMsg MSGFILE_SCRIPT, 35, 0, 0
    YesNoWin 0x8010
    VMStackPush 0x8010
    VMStackPushConst 1
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_03C5
    // "Hmm... Well, that is fine, as well.\nVisit if you have a change of heart."
    ParentActorMsg MSGFILE_SCRIPT, 29, 0, 0
    LastKeyWait
    ActorMsgClose
    VMReturn

L_03C5:
    ActorMsgClose
    WorkSetConst 0x8022, 0
    WorkSetConst 0x8023, 0
    VMCall L_098A
    VMStackPush 0x8010
    VMStackPushConst 1
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_03EC

L_03EC:
    VMReturn

Script_3:
    ActorsPauseAll
    SEPlay SEQ_SE_MESSAGE
    ActorSetEyeToEye
    VMCall L_0402
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

L_0402:
    VMStackPushFlag 253
    VMStackPushConst 0
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_0429
    // "Heya![f000]븁\u0000\nThe professor gave you a Pokémon to\nstart your journey, right?[f000]븁\u0000\nIf that Pokémon is still with you, and if\nyou two have a strong bond, there's a[f000]븀\u0000\nspecial move it can learn...[f000]븁\u0000\nWant me to teach it a battle-combo move?"
    ParentActorMsg MSGFILE_SCRIPT, 37, 0, 0
    FlagSet 253
    VMJump L_0433

L_0429:
    // "A special move...\nShould I teach it a battle-combo move?"
    ParentActorMsg MSGFILE_SCRIPT, 38, 0, 0

L_0433:
    YesNoWin 0x8010
    VMStackPush 0x8010
    VMStackPushConst 1
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_045A
    // "Is that so...\nWell, come on back now, y'hear?"
    ParentActorMsg MSGFILE_SCRIPT, 40, 0, 0
    LastKeyWait
    ActorMsgClose
    VMReturn

L_045A:
    MoveTutorCheckParty 2, 0x8010
    VMStackPush 0x8010
    VMStackPushConst 1
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_0489
    // "I can't teach these Pokémon."
    ParentActorMsg MSGFILE_SCRIPT, 39, 0, 0
    LastKeyWait
    ActorMsgClose
    VMReturn
    VMJump L_04AC

L_0489:
    VMStackPush 0x8010
    VMStackPushConst 2
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_04AC
    // "This Pokémon... Well, it doesn't look\nlike it's too comfortable with you yet."
    ParentActorMsg MSGFILE_SCRIPT, 44, 0, 0
    LastKeyWait
    ActorMsgClose
    VMReturn

L_04AC:
    // "Which Pokémon should learn the move?[f000]븁\u0000"
    ParentActorMsg MSGFILE_SCRIPT, 41, 0, 0
    ActorMsgClose
    MoveTutorCallPokeSelect 2, 0x8010, 0x8020
    VMStackPush 0x8010
    VMStackPushConst 0
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_04E3
    // "Is that so...\nWell, come on back now, y'hear?"
    ParentActorMsg MSGFILE_SCRIPT, 40, 0, 0
    LastKeyWait
    ActorMsgClose
    VMReturn

L_04E3:
    PokePartyIsEgg 0x8010, 0x8020
    VMStackPush 0x8010
    VMStackPushConst 1
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_050C
    // "Teach a move to an Egg?\nWhat kinda crazy talk is that?!"
    ParentActorMsg MSGFILE_SCRIPT, 43, 0, 0
    LastKeyWait
    ActorMsgClose
    VMReturn

L_050C:
    MoveTutorCheckPkm 2, 0x8020, 0x8010
    WorkCmpConst 0x8010, 2
    VMJumpIf CMP_EQ, L_0527
    VMJump L_053D

L_0527:
    // "This Pokémon... Well, it doesn't look\nlike it's too comfortable with you yet."
    ParentActorMsg MSGFILE_SCRIPT, 44, 0, 0
    LastKeyWait
    ActorMsgClose
    VMReturn
    VMJump L_058F

L_053D:
    WorkCmpConst 0x8010, 1
    VMJumpIf CMP_EQ, L_0550
    VMJump L_0566

L_0550:
    // "Now, that Pokémon can't learn this\nspecial move![f000]븁\u0000\nI told ya, it's only for the Pokémon who\nstarted your journey with you."
    ParentActorMsg MSGFILE_SCRIPT, 42, 0, 0
    LastKeyWait
    ActorMsgClose
    VMReturn
    VMJump L_058F

L_0566:
    WorkCmpConst 0x8010, 3
    VMJumpIf CMP_EQ, L_0579
    VMJump L_058F

L_0579:
    // "I can't teach it twice. This Pokémon\nalready knows the special move!"
    ParentActorMsg MSGFILE_SCRIPT, 45, 0, 0
    LastKeyWait
    ActorMsgClose
    VMReturn
    VMJump L_058F

L_058F:
    MoveTutorGetMoveID 2, 0x8020, 0x8021
    WordSetPartyPokeName 0, 0x8020
    WordSetMoveName 1, 0x8021
    // "Want me to teach [f000]ć\u0001\u0001\nto [f000]ā\u0001\u0000?"
    ParentActorMsg MSGFILE_SCRIPT, 46, 0, 0
    YesNoWin 0x8010
    VMStackPush 0x8010
    VMStackPushConst 1
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_05D2
    // "Is that so...\nWell, come on back now, y'hear?"
    ParentActorMsg MSGFILE_SCRIPT, 40, 0, 0
    LastKeyWait
    ActorMsgClose
    VMReturn

L_05D2:
    ActorMsgClose
    WorkSetConst 0x8022, 0
    WorkSetConst 0x8023, 0
    VMCall L_098A
    VMStackPush 0x8010
    VMStackPushConst 1
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_05F9

L_05F9:
    VMReturn

Script_4:
    ActorsPauseAll
    SEPlay SEQ_SE_MESSAGE
    ActorSetEyeToEye
    WorkSetConst 0x8024, 72
    VMStackPushFlag 325
    VMStackPushConst 0
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_0638
    WordSetItemNameEx 0, 0x8024, 2, 0
    // "I'm the master Move Tutor![f000]븁\u0000\nAnd I'm also obsessed with\n[f000]ĉ\u0001\u0000![f000]븁\u0000\nGive me [f000]ĉ\u0001\u0000,\nand I'll thank you by teaching[f000]븀\u0000\nyour Pokémon a move![f000]븁\u0000"
    ParentActorMsg MSGFILE_SCRIPT, 48, 0, 0
    FlagSet 325
    VMJump L_0642

L_0638:
    // "I'm the master Move Tutor![f000]븁\u0000"
    ParentActorMsg MSGFILE_SCRIPT, 49, 0, 0

L_0642:
    VMCall L_0747
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_5:
    ActorsPauseAll
    SEPlay SEQ_SE_MESSAGE
    ActorSetEyeToEye
    WorkSetConst 0x8024, 73
    VMStackPushFlag 326
    VMStackPushConst 0
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_068B
    WordSetItemNameEx 0, 0x8024, 2, 0
    // "I'm the master Move Tutor![f000]븁\u0000\nAnd I'm also obsessed with\n[f000]ĉ\u0001\u0000![f000]븁\u0000\nGive me [f000]ĉ\u0001\u0000,\nand I'll thank you by teaching[f000]븀\u0000\nyour Pokémon a move![f000]븁\u0000"
    ParentActorMsg MSGFILE_SCRIPT, 48, 0, 0
    FlagSet 326
    VMJump L_0695

L_068B:
    // "I'm the master Move Tutor![f000]븁\u0000"
    ParentActorMsg MSGFILE_SCRIPT, 49, 0, 0

L_0695:
    VMCall L_0747
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_6:
    ActorsPauseAll
    SEPlay SEQ_SE_MESSAGE
    ActorSetEyeToEye
    WorkSetConst 0x8024, 74
    VMStackPushFlag 327
    VMStackPushConst 0
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_06DE
    WordSetItemNameEx 0, 0x8024, 2, 0
    // "I'm the master Move Tutor![f000]븁\u0000\nAnd I'm also obsessed with\n[f000]ĉ\u0001\u0000![f000]븁\u0000\nGive me [f000]ĉ\u0001\u0000,\nand I'll thank you by teaching[f000]븀\u0000\nyour Pokémon a move![f000]븁\u0000"
    ParentActorMsg MSGFILE_SCRIPT, 48, 0, 0
    FlagSet 327
    VMJump L_06E8

L_06DE:
    // "I'm the master Move Tutor![f000]븁\u0000"
    ParentActorMsg MSGFILE_SCRIPT, 49, 0, 0

L_06E8:
    VMCall L_0747
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_7:
    ActorsPauseAll
    SEPlay SEQ_SE_MESSAGE
    ActorSetEyeToEye
    WorkSetConst 0x8024, 75
    VMStackPushFlag 328
    VMStackPushConst 0
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_0731
    WordSetItemNameEx 0, 0x8024, 2, 0
    // "I'm the master Move Tutor![f000]븁\u0000\nAnd I'm also obsessed with\n[f000]ĉ\u0001\u0000![f000]븁\u0000\nGive me [f000]ĉ\u0001\u0000,\nand I'll thank you by teaching[f000]븀\u0000\nyour Pokémon a move![f000]븁\u0000"
    ParentActorMsg MSGFILE_SCRIPT, 48, 0, 0
    FlagSet 328
    VMJump L_073B

L_0731:
    // "I'm the master Move Tutor![f000]븁\u0000"
    ParentActorMsg MSGFILE_SCRIPT, 49, 0, 0

L_073B:
    VMCall L_0747
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

L_0747:
    // "Want me to teach your\nPokémon a move?"
    ParentActorMsg MSGFILE_SCRIPT, 50, 0, 0
    YesNoWin 0x8010
    VMStackPush 0x8010
    VMStackPushConst 1
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_0780
    WordSetItemNameEx 0, 0x8024, 2, 0
    // "If you collect some [f000]ĉ\u0001\u0000,\nyou come back now."
    ParentActorMsg MSGFILE_SCRIPT, 52, 0, 0
    LastKeyWait
    ActorMsgClose
    VMReturn

L_0780:
    // "Well, that's just fine![f000]븁\u0000\nPick the move you want\nme to teach![f000]븁\u0000"
    ParentActorMsg MSGFILE_SCRIPT, 51, 0, 0
    WorkSetConst 0x400c, 0
    WorkSetConst 0x400d, 0
    WorkSetConst 0x400e, 0
    WorkSetConst 0x400f, 0
    WorkCmpConst 0x8024, 72
    VMJumpIf CMP_EQ, L_07B5
    VMJump L_07DB

L_07B5:
    VMStackPush 0x8000
    VMStackPush 0x8001
    WorkSet 0x8000, 246
    WorkSet 0x8001, 0
    RTCallGlobal 10110
    VMStackPop 0x8001
    VMStackPop 0x8000
    VMJump L_0886

L_07DB:
    WorkCmpConst 0x8024, 73
    VMJumpIf CMP_EQ, L_07EE
    VMJump L_0814

L_07EE:
    VMStackPush 0x8000
    VMStackPush 0x8001
    WorkSet 0x8000, 245
    WorkSet 0x8001, 0
    RTCallGlobal 10110
    VMStackPop 0x8001
    VMStackPop 0x8000
    VMJump L_0886

L_0814:
    WorkCmpConst 0x8024, 74
    VMJumpIf CMP_EQ, L_0827
    VMJump L_084D

L_0827:
    VMStackPush 0x8000
    VMStackPush 0x8001
    WorkSet 0x8000, 244
    WorkSet 0x8001, 0
    RTCallGlobal 10110
    VMStackPop 0x8001
    VMStackPop 0x8000
    VMJump L_0886

L_084D:
    WorkCmpConst 0x8024, 75
    VMJumpIf CMP_EQ, L_0860
    VMJump L_0886

L_0860:
    VMStackPush 0x8000
    VMStackPush 0x8001
    WorkSet 0x8000, 243
    WorkSet 0x8001, 0
    RTCallGlobal 10110
    VMStackPop 0x8001
    VMStackPop 0x8000
    VMJump L_0886

L_0886:
    DebugPrint 0x400c
    DebugPrint 0x400d
    DebugPrint 0x400e
    DebugPrint 0x400f
    VMStackPush 0x400c
    VMStackPushConst 0
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_08C1
    WordSetItemNameEx 0, 0x8024, 2, 0
    // "If you collect some [f000]ĉ\u0001\u0000,\nyou come back now."
    ParentActorMsg MSGFILE_SCRIPT, 52, 0, 0
    LastKeyWait
    ActorMsgClose
    VMReturn

L_08C1:
    VMStackPush 0x400c
    VMStackPushConst 1
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_08E4
    // "This Pokémon can't learn\nthat move!"
    ParentActorMsg MSGFILE_SCRIPT, 54, 0, 0
    LastKeyWait
    ActorMsgClose
    VMReturn

L_08E4:
    PokePartyHasMove 0x8010, 0x400d, 0x400e
    VMStackPush 0x8010
    VMStackPushConst 1
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_090F
    // "This Pokémon already knows that move!"
    ParentActorMsg MSGFILE_SCRIPT, 55, 0, 0
    LastKeyWait
    ActorMsgClose
    VMReturn

L_090F:
    WorkGet 0x8021, 0x400d
    WorkGet 0x8020, 0x400e
    WorkSetConst 0x8022, 0
    WorkSetConst 0x8023, 1
    VMCall L_098A
    VMStackPush 0x8010
    VMStackPushConst 0
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_0956
    WordSetItemNameEx 0, 0x8024, 2, 0
    // "If you collect some [f000]ĉ\u0001\u0000,\nyou come back now."
    ParentActorMsg MSGFILE_SCRIPT, 52, 0, 0
    LastKeyWait
    ActorMsgClose

L_0956:
    VMReturn

Script_8:
    ActorsPauseAll
    FunfestMissionBroadcast 17, 0
    SEPlay SEQ_SE_MESSAGE
    // "The Pokémon I've taken a shine to are\nthe ones you get from the professor![f000]븁\u0000\nTo teach all of these Pokémon a\nspecial move, a battle-combo move...[f000]븀\u0000\nThat's my pledge!"
    MsgPlaceSign 47, 1
    MsgPlaceSignClose
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt
    WorkSetConst 0x8025, 0
    WorkSetConst 0x8026, 0
    WorkSetConst 0x8027, 0
    WorkSetConst 0x8028, 0

L_098A:
    WorkSetConst 0x8028, 0
    PokePartyGetMoveCount 0x8010, 0x8020
    VMStackPush 0x8010
    VMStackPushConst 4
    VMStackCmp CMP_NE
    VMJumpIf CMP_STACK, L_0A39
    WordSetPartyPokeName 0, 0x8020
    WordSetMoveName 1, 0x8021
    MEPlay SEQ_ME_LVUP
    // "[f000]Ă\u0001\u0000 learned\n[f000]ć\u0001\u0001!"
    SystemMsg 10, 0
    MEWait
    VMStackPush 0x8023
    VMStackPushConst 0
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_09DA
    LastKeyWait
    VMJump L_09DC

L_09DA:
    MsgWaitAdvance

L_09DC:
    VMStackPush 0x400c
    VMStackPushConst 2
    VMStackCmp CMP_EQ
    VMStackPush 0x400f
    VMStackPushConst 0
    VMStackCmp CMP_GT
    VMStackCmp CMP_AND
    VMJumpIf CMP_STACK, L_0A2D
    WorkSetConst 0x8029, 0
    ItemSub 0x8024, 0x400f, 0x8029
    WordSetPlayerName 0
    WordSetItemNameEx 1, 0x8024, 0x400f, 0
    WordSetNumber 2, 0x400f, 2
    // "[f000]Ā\u0001\u0000 handed over\n[f000]ȁ\u0001\u0002 [f000]ĉ\u0001\u0001 in exchange."
    SystemMsg 53, 0
    LastKeyWait
    WorkSetConst 0x8029, 0

L_0A2D:
    InfoMsgClose
    PokePartyLearnMove 0x8020, 0x8010, 0x8021
    VMReturn

L_0A39:
    WorkSetConst 0x8027, 1

L_0A3F:
    VMStackPush 0x8027
    VMStackPushConst 1
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_0AA8
    VMCall L_0B0B
    VMStackPush 0x8028
    VMStackPushConst 1
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_0A7D
    WorkSetConst 0x8010, 1
    WorkSetConst 0x8027, 0
    VMJump L_0AA2

L_0A7D:
    VMCall L_0AAA
    VMStackPush 0x8028
    VMStackPushConst 1
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_0AA2
    WorkSetConst 0x8010, 0
    WorkSetConst 0x8027, 0

L_0AA2:
    VMJump L_0A3F

L_0AA8:
    VMReturn

L_0AAA:
    WordSetMoveName 0, 0x8021
    // "Give up on learning the\nmove [f000]ć\u0001\u0000?"
    SystemMsg 12, 0
    YesNoWin 0x8010
    VMStackPush 0x8010
    VMStackPushConst 0
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_0B03
    WordSetPartyPokeName 0, 0x8020
    WordSetMoveName 1, 0x8021
    // "[f000]Ă\u0001\u0000 did not learn [f000]ć\u0001\u0001!"
    SystemMsg 13, 0
    VMStackPush 0x8022
    VMStackPushConst 0
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_0AF7
    LastKeyWait
    VMJump L_0AF9

L_0AF7:
    MsgWaitAdvance

L_0AF9:
    InfoMsgClose
    WorkSetConst 0x8028, 1
    VMReturn

L_0B03:
    WorkSetConst 0x8028, 0
    VMReturn

L_0B0B:
    WorkSetConst 0x8028, 0
    WordSetPartyPokeName 0, 0x8020
    WordSetMoveName 1, 0x8021
    // "[f000]Ă\u0001\u0000 is trying to\nlearn [f000]ć\u0001\u0001![f000]븁\u0000\nBut [f000]Ă\u0001\u0000 can't learn more than\nfour moves.[f000]븁\u0000\nDelete a move to make room\nfor [f000]ć\u0001\u0001?"
    SystemMsg 11, 0
    YesNoWin 0x8010
    VMStackPush 0x8010
    VMStackPushConst 1
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_0B3A
    VMReturn

L_0B3A:
    InfoMsgClose
    CallPokeMoveReplace 0x8010, 0x8025, 0x8020, 0x8021
    VMStackPush 0x8010
    VMStackPushConst 0
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_0B5B
    VMReturn

L_0B5B:
    PokePartyGetMove 0x8026, 0x8020, 0x8025
    WordSetMoveName 0, 0x8026
    // "Is it OK to forget the\nmove [f000]ć\u0001\u0000?"
    SystemMsg 14, 0
    YesNoWin 0x8010
    VMStackPush 0x8010
    VMStackPushConst 1
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_0B87
    VMReturn

L_0B87:
    PokePartyGetMove 0x8026, 0x8020, 0x8025
    WordSetPartyPokeName 0, 0x8020
    WordSetMoveName 1, 0x8026
    WordSetMoveName 2, 0x8021
    // "1, [f000]븂\u0001\u00142, and[f000]븂\u0001\u0014... [f000]븂\u0001\u0014... [f000]븂\u0001\u0014... Ta-da![f000]븅\u0001\u0003[f000]븅\u0001\u0006[f000]븁\u0000\n[f000]Ă\u0001\u0000 forgot how to\nuse [f000]ć\u0001\u0001.[f000]븁\u0000\nAnd...[f000]븁\u0000"
    SystemMsg 15, 0
    // "[f000]Ă\u0001\u0000 learned [f000]ć\u0001\u0002!"
    SystemMsg 16, 0
    MEPlay SEQ_ME_LVUP
    MEWait
    VMStackPush 0x8023
    VMStackPushConst 0
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_0BCB
    LastKeyWait
    VMJump L_0BCD

L_0BCB:
    MsgWaitAdvance

L_0BCD:
    VMStackPush 0x400c
    VMStackPushConst 2
    VMStackCmp CMP_EQ
    VMStackPush 0x400f
    VMStackPushConst 0
    VMStackCmp CMP_GT
    VMStackCmp CMP_AND
    VMJumpIf CMP_STACK, L_0C1E
    WorkSetConst 0x802a, 0
    ItemSub 0x8024, 0x400f, 0x802a
    WordSetPlayerName 0
    WordSetItemNameEx 1, 0x8024, 0x400f, 0
    WordSetNumber 2, 0x400f, 2
    // "[f000]Ā\u0001\u0000 handed over\n[f000]ȁ\u0001\u0002 [f000]ĉ\u0001\u0001 in exchange."
    SystemMsg 53, 0
    LastKeyWait
    WorkSetConst 0x802a, 0

L_0C1E:
    InfoMsgClose
    PokePartyLearnMove 0x8020, 0x8025, 0x8021
    WorkSetConst 0x8028, 1
    VMReturn
    WorkSetConst 0x8028, 0
    WorkSetConst 0x8027, 0
    WorkSetConst 0x8026, 0
    WorkSetConst 0x8025, 0

Script_9:
    WorkGet 0x8020, 0x8000
    WorkGet 0x8021, 0x8001
    WorkSetConst 0x8022, 1
    WorkSetConst 0x8023, 1
    VMCall L_098A
    RTEndGlobal
    VMHalt
    .balign 4, 0

// ==== Emerald's mechanics (emerald_mech) =========================================================================
// Text file 615 (this file's): Black 2's lines 10-16 (learning a move) and ours 56-60.
#define EM_T_LEARNED          10    // "X learned Y!"
#define EM_T_FOUR_MOVES       11    // "X is trying to learn Y! ... Delete a move to make room for Y?"
#define EM_T_GIVE_UP          12    // "Give up on learning the move Y?"
#define EM_T_DID_NOT_LEARN    13    // "X did not learn Y!"
#define EM_T_FORGET_OK        14    // "Is it OK to forget the move Z?"
#define EM_T_FORGOT           15    // "1, 2, and... Ta-da! X forgot how to use Z. And..."
#define EM_T_LEARNED_AFTER    16    // "X learned Y!"
#define EM_T_NOT_COMPATIBLE   56    // Emerald's gText_PkmnCantLearnMove
#define EM_T_ALREADY_KNOWS    57    // Emerald's gText_PkmnAlreadyKnows
#define EM_T_CANT_PARTICIPATE 58    // Emerald's gText_PkmnCantParticipate
#define EM_T_CONSTRUCTION     59    // Emerald's BattleFrontier_BattleTowerLobby_Text_DoubleBattleRoomConstruction words
#define EM_T_CANCEL_BATTLE    60    // Emerald's gText_CancelBattle (the multi battle's GetFacilityCancelString)

// ---- 2289: a move tutor's party menu and lesson (pokeemerald MoveTutor_EventScript_OpenPartyMenu, special
// ChooseMonForMoveTutor). In: 0x8000 tutor (pokeemerald TUTOR_MOVE_*), 0x8001 move. Out: 0x8010 = 1 taught, 0 not.
// Emerald: the party menu; a Pokémon that can't learn the move or already knows it gets its message and the menu
// closes (DisplayLearnMoveMessageAndClose: nothing taught); else the move is learned, or the four-move question.
// Scratch: 0x8020 slot, 0x8021 move, 0x8022-0x8027.
EM_ScriptMoveTutor:
    WorkGet 0x8021, 0x8001
    WorkSetConst 0x8022, 0
    WorkSetConst 0x8020, 0
    CallPokeSelect 0, 0x8022, 0x8020, 0
    WorkCmpConst 0x8022, 1
    VMJumpIf CMP_NE, EM_TutorNo
    EmTutorCheck 0x8023, 0x8020, 0x8000
    WordSetPartyPokeName 0, 0x8020
    WordSetMoveName 1, 0x8021
    WorkCmpConst 0x8023, 1
    VMJumpIf CMP_EQ, EM_TutorCantLearn
    WorkCmpConst 0x8023, 2
    VMJumpIf CMP_EQ, EM_TutorKnows
    VMCall EM_Learn
    RTEndGlobal
    VMHalt
EM_TutorCantLearn:
    SystemMsg EM_T_NOT_COMPATIBLE, 0
    LastKeyWait
    InfoMsgClose
    VMJump EM_TutorNo
EM_TutorKnows:
    SystemMsg EM_T_ALREADY_KNOWS, 0
    LastKeyWait
    InfoMsgClose
EM_TutorNo:
    WorkSetConst 0x8010, 0
    RTEndGlobal
    VMHalt

// Learn move 0x8021 in party slot 0x8020 -> 0x8010 = 1 learned, 0 not: Black 2's own sequence (Script_9's L_098A
// and its loop L_0A3F/L_0AAA/L_0B0B above, without the shard payment of its tutors, which reads map works).
EM_Learn:
    PokePartyGetMoveCount 0x8024, 0x8020
    WorkCmpConst 0x8024, 4
    VMJumpIf CMP_EQ, EM_LearnFull
    WordSetPartyPokeName 0, 0x8020
    WordSetMoveName 1, 0x8021
    MEPlay SEQ_ME_LVUP
    SystemMsg EM_T_LEARNED, 0
    MEWait
    LastKeyWait
    InfoMsgClose
    PokePartyLearnMove 0x8020, 0x8024, 0x8021
    WorkSetConst 0x8010, 1
    VMReturn
EM_LearnFull:
    WordSetPartyPokeName 0, 0x8020
    WordSetMoveName 1, 0x8021
    SystemMsg EM_T_FOUR_MOVES, 0
    YesNoWin 0x8025
    WorkCmpConst 0x8025, 0                       // 0 = YES
    VMJumpIf CMP_NE, EM_LearnGiveUp
    InfoMsgClose
    WorkSetConst 0x8025, 0
    WorkSetConst 0x8026, 0
    CallPokeMoveReplace 0x8025, 0x8026, 0x8020, 0x8021
    WorkCmpConst 0x8025, 0                       // 0 = no move chosen
    VMJumpIf CMP_EQ, EM_LearnGiveUp
    PokePartyGetMove 0x8027, 0x8020, 0x8026
    WordSetMoveName 0, 0x8027
    SystemMsg EM_T_FORGET_OK, 0
    YesNoWin 0x8025
    WorkCmpConst 0x8025, 0
    VMJumpIf CMP_NE, EM_LearnGiveUp
    PokePartyGetMove 0x8027, 0x8020, 0x8026
    WordSetPartyPokeName 0, 0x8020
    WordSetMoveName 1, 0x8027
    WordSetMoveName 2, 0x8021
    SystemMsg EM_T_FORGOT, 0
    SystemMsg EM_T_LEARNED_AFTER, 0
    MEPlay SEQ_ME_LVUP
    MEWait
    LastKeyWait
    InfoMsgClose
    PokePartyLearnMove 0x8020, 0x8026, 0x8021
    WorkSetConst 0x8010, 1
    VMReturn
EM_LearnGiveUp:
    WordSetMoveName 0, 0x8021
    SystemMsg EM_T_GIVE_UP, 0
    YesNoWin 0x8025
    WorkCmpConst 0x8025, 0
    VMJumpIf CMP_NE, EM_LearnFull
    WordSetPartyPokeName 0, 0x8020
    WordSetMoveName 1, 0x8021
    SystemMsg EM_T_DID_NOT_LEARN, 0
    LastKeyWait
    InfoMsgClose
    WorkSetConst 0x8010, 0
    VMReturn

// ---- 2290: the tag battle (pokeemerald ChooseHalfPartyForBattle + ReducePlayerPartyToSelectedMons +
// DoSpecialTrainerBattle SPECIAL_BATTLE_STEVEN + LoadPlayerParty). In: 0x8000 partner, 0x8001 foe 1, 0x8002 foe 2.
// Out: 0x8010 = 0 cancelled (the party menu left without a pick; the party unchanged), 1 won (CallTrainerBattleEnd done,
// both foes' flags set), 2 lost (the caller runs CallTrainerLose: em_tag_battle).
// Choice: one party menu, Black 2's battle-entry screen (EmPickParty, emerald_mech.c): pick 1 to 3 in order (FIRST,
// SECOND, THIRD; a pick can be taken out again: NO ENTRY), then CONFIRM; an Egg cannot be entered; a fainted Pokémon
// among the picks "can't participate" and the menu opens again (Emerald's menu does not let it be picked). CANCEL / B
// with nothing marked cancels; with picks marked Emerald asks "Cancel the battle?" (HandleChooseMonCancel): YES
// cancels, NO opens the menu again with the same picks marked. The picks are moved to party slots 0-2 in that
// order (0x8022-0x8024 = the swaps made: swap(0, P0), swap(1, P1), swap(2, P2) with the later picks followed through
// the earlier swaps) and moved back the same way after the battle. Scratch: 0x8021 count, 0x8022-0x8024 picks,
// 0x8025-0x8028.
EM_ScriptTagBattle:
    WorkSetConst 0x8021, 0                       // nothing marked when the menu opens
EM_TagPick:
    WorkSetConst 0x8026, 0
    EmPickParty 0x8021                           // 0x8021 = how many, 0x8022-0x8024 = slots in order (+0x80: left
    WorkCmpConst 0x8021, 0                       // with CANCEL / B; 0: left with nothing marked)
    VMJumpIf CMP_EQ, EM_TagCancel
    WorkCmpConst 0x8021, 0x80
    VMJumpIf CMP_GE, EM_TagAskCancel
    WorkGet 0x8025, 0x8022
    VMCall EM_TagCheckPick
    WorkCmpConst 0x8021, 2
    VMJumpIf CMP_LT, EM_TagChecked
    WorkGet 0x8025, 0x8023
    VMCall EM_TagCheckPick
    WorkCmpConst 0x8021, 3
    VMJumpIf CMP_LT, EM_TagChecked
    WorkGet 0x8025, 0x8024
    VMCall EM_TagCheckPick
EM_TagChecked:
    WorkCmpConst 0x8026, 1
    VMJumpIf CMP_EQ, EM_TagCantJoin
    // the choice to the front, in order (a pick of 255 = none: EmPartySwap ignores it)
    EmPartySwap 0, 0x8022
    WorkCmpConst 0x8023, 0
    VMJumpIf CMP_NE, EM_TagOrder1
    WorkGet 0x8023, 0x8022
EM_TagOrder1:
    WorkCmpConst 0x8024, 0
    VMJumpIf CMP_NE, EM_TagOrder2
    WorkGet 0x8024, 0x8022
EM_TagOrder2:
    EmPartySwap 1, 0x8023
    WorkCmpConst 0x8024, 1
    VMJumpIf CMP_NE, EM_TagOrder3
    WorkGet 0x8024, 0x8023
EM_TagOrder3:
    EmPartySwap 2, 0x8024
    WorkSet 0x8027, 0x8021                       // the partner id with how many of the player's Pokémon battle in
    WorkMul 0x8027, 4096                         // bits 12-15 (emerald_mech.c EM_SetTrainer2v2 keeps only those)
    WorkAdd 0x8027, 0x8000
    CallTrainerMultiBattle 0x8027, 0x8001, 0x8002, 0
    TrainerBattleIsVictory 0x8028
    EmPartySwap 2, 0x8024                        // the old order back (the same swaps, last first)
    EmPartySwap 1, 0x8023
    EmPartySwap 0, 0x8022
    WorkCmpConst 0x8028, 1
    VMJumpIf CMP_EQ, EM_TagWon
    WorkSetConst 0x8010, 2
    RTEndGlobal
    VMHalt
EM_TagWon:
    PokePartyGetCount 0x8027, 2                  // Black 2's multi battles: the partner won while none of the
    WorkCmpConst 0x8027, 0                       // player's Pokémon can battle -> heal (0014.s, 1239.s L_12E5)
    VMJumpIf CMP_NE, EM_TagEnd
    PokePartyRecoverAll
EM_TagEnd:
    CallTrainerBattleEnd
    TrainerFlagSet 0x8001
    TrainerFlagSet 0x8002
    WorkSetConst 0x8010, 1
    RTEndGlobal
    VMHalt
EM_TagCantJoin:                                  // pokeemerald gText_PkmnCantParticipate, then the menu again
    SystemMsg EM_T_CANT_PARTICIPATE, 0
    LastKeyWait
    InfoMsgClose
    WorkSetConst 0x8021, 0
    VMJump EM_TagPick
EM_TagAskCancel:                                 // "Cancel the battle?" YES: cancel; NO: the menu again, same picks
    SystemMsg EM_T_CANCEL_BATTLE, 0
    YesNoWin 0x8025
    InfoMsgClose
    WorkCmpConst 0x8025, 0
    VMJumpIf CMP_EQ, EM_TagCancel
    WorkSub 0x8021, 0x40                         // 0x80 | n -> 0x40 | n: EmPickParty marks them again
    VMJump EM_TagPick
EM_TagCheckPick:                                 // 0x8025 = a picked slot -> 0x8026 = 1 when it is an Egg or fainted
    PokePartyIsEgg 0x8027, 0x8025                // (0x8026 is cleared at EM_TagPick)
    WorkCmpConst 0x8027, 1
    VMJumpIf CMP_EQ, EM_TagBadPick
    PokePartyGetParam 0x8027, 0x8025, 0xa0       // HP (0xa0 is on s0110's list)
    WorkCmpConst 0x8027, 0
    VMJumpIf CMP_EQ, EM_TagBadPick
    VMReturn
EM_TagBadPick:
    WorkSetConst 0x8026, 1
    VMReturn
EM_TagCancel:
    WorkSetConst 0x8010, 0
    RTEndGlobal
    VMHalt

// ---- 2291: a closed door, as a door tile's sign (or an NPC's) script; 2292: its message, for RTCallGlobal ---------
EM_ScriptClosedDoor:
    ActorsPauseAll
    SEPlay SEQ_SE_MESSAGE
    RTCallGlobal EM_GLOBAL_CLOSED_DOOR_MSG
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt
EM_ScriptClosedDoorMsg:
    SystemMsg EM_T_CONSTRUCTION, 2
    LastKeyWait
    InfoMsgClose
    RTEndGlobal
    VMHalt

// ---- 2293-2295: Emerald's abnormal weather (emerald_ch12_13, 2026-10-12): the macros and the findings are in
// src/field_scripts/scenes/emerald/abnormal_weather.inc; their two lines are 615's 61-62
// (src/text/emerald/overrides_emerald_postgame.json)
#include "scenes/emerald/abnormal_weather.inc"
AW_ScriptZoneInit:
    aw_zone_init
    VMHalt
AW_ScriptCleanup:
    aw_cleanup
    VMHalt
AW_ScriptCaveInit:
    aw_cave_init
    VMHalt

// ---- 2296-2297: Emerald's Safari Zone expansion (emerald_ch12_13): the two construction workers at the way into the new
// areas (pokeemerald SafariZone_South objects 5 / 6, hidden by FLAG_HIDE_SAFARI_ZONE_SOUTH_CONSTRUCTION_WORKERS, which the
// Hall of Fame sets) and the attendant of the new south-east area (SafariZone_Southeast object 5, shown by the Hall of Fame:
// FLAG_HIDE_SAFARI_ZONE_SOUTH_EAST_EXPANSION); data/story/emerald/e_ch13.json. 615's lines 63-64.
SZ_ScriptWorker:                        // SafariZone_South_EventScript_ConstructionWorker1 / 2 (MSGBOX_NPC)
    h_msgbox_npc 63                     // This area is still under construction. It's off-limits, sorry!
SZ_ScriptAttendant:                     // SafariZone_Southeast_EventScript_ExpansionZoneAttendant (MSGBOX_NPC)
    h_msgbox_npc 64                     // The Safari Zone's expansion project is finished now. ...
