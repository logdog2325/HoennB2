// Chapter Ch6's beat in the player's house 1F (Sapphire data/scripts/players_house.inc
// LittlerootTown_BrendansHouse_1F_EventScript_1B6C3D): Mom gives the Amulet Coin once you have Dad's Balance Badge.
// Included by scenes/players_house_1f.inc (Ch0/Ch1) inside Mom's script 26, right after `WordSetPlayerName 0` and
// before the rescued-Birch branch (Sapphire's order: the badge check comes first). Plain Black 2 commands (the house
// files do not include hoenn_story.inc). The including file defines:
//   CH6_MOM_T      the first of the three lines below in the house's text file (T(...) index, both houses alike):
//                  +0 "Mom: Oh? Did Dad give you that Badge? ..." (PlayersHouse_1F_Text_GotDadsBadgeHeresSomethingFromMom)
//                  +1 "Don't push yourself too hard, dear. ..." (PlayersHouse_1F_Text_DontPushYourselfTooHard)
//                  +2 "Too bad!\nThe Bag is full..." (Text_TooBadBagIsFull)
//   CH6_MOM_REST   the label of Mom's "you should rest a bit" + heal branch (Sapphire 1B6C72)
// Falls through (to the rest of Mom's script) when the player has no Balance Badge.
#ifdef HOENN_TEST_CH6
    TrainerCardAddBadge 4                        // TEST ONLY: the Balance Badge (the test warp lands in this house)
#endif
    TrainerCardHasBadge 0x8030, 4                // goto_if_unset FLAG_BADGE05_GET
    WorkCmpConst 0x8030, 0
    VMJumpIf CMP_EQ, L_Ch6_MomNoBadge5
    VMStackPushFlag FLAG_RECEIVED_AMULET_COIN    // goto_if_set FLAG_RECEIVED_AMULET_COIN, 1B6C72
    VMStackPushConst 1
    VMStackCmp CMP_NE
    VMJumpIf CMP_STACK, CH6_MOM_REST
    ParentActorMsg MSGFILE_SCRIPT, T(CH6_MOM_T), 0, 0     // Mom: Oh? Did Dad give you that Badge? ...
    LastKeyWait
    MsgWinCloseAll                               // (Black 2: the item script opens its own window)
    ItemCheckSpace ITEM_AMULET_COIN, 1, 0x8031   // giveitem ITEM_AMULET_COIN (hoenn_story.inc h_giveitem)
    WorkCmpConst 0x8031, 0
    VMJumpIf CMP_EQ, L_Ch6_MomBagFull
    VMStackPush 0x8000
    VMStackPush 0x8001
    WorkSetConst 0x8000, ITEM_AMULET_COIN
    WorkSetConst 0x8001, 1
    RTCallGlobal 2805
    VMStackPop 0x8001
    VMStackPop 0x8000
    ParentActorMsg MSGFILE_SCRIPT, T(CH6_MOM_T + 1), 0, 0 // Don't push yourself too hard, dear. ...
    LastKeyWait
    FlagSet FLAG_RECEIVED_AMULET_COIN
    ActorMsgClose
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt
L_Ch6_MomBagFull:                                // Common_EventScript_ShowBagIsFull
    ParentActorMsg MSGFILE_SCRIPT, T(CH6_MOM_T + 2), 0, 0 // Too bad! The Bag is full...
    LastKeyWait
    MsgWinCloseAll
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt
L_Ch6_MomNoBadge5:
