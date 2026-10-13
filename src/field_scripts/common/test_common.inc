// TEST ONLY (HOENN_TEST_COMMON=1, b2tools/patches/scripts.py): the body of Littleroot's Lab sign (0778 Script_4) runs
// every common piece of notes/STORY_COMMON.md once. Lines of Littleroot's text stand in for the chapters' own:
// 0 = the town sign (all passed), 8 = "It's not safe..." (a check failed), 1 = "{0100:0}'s House" (word 0 test).
// The player stands below the Lab sign (174,370) facing north. Expected, in order: "!" over the player; "obtained a
// Potion"; (no message for the 999 Potions: no room); TM jingle + "<player>'s House" (the hand-over line); fade, heal
// jingle; badge jingle; nickname screen for party slot 0; a Kecleon battle against the actor beside the player, which
// is gone afterwards; the town sign text = every check passed.
    PokePartyGetCount 0x8000, 0                     // a battle with an empty party hangs: lend a Lv 50 Mudkip
    WorkCmpConst 0x8000, 0
    VMJumpIf CMP_NE, L_TCParty
    PokePartyAdd 0x8001, SPECIES_MUDKIP, 0, 50
L_TCParty:
    h_applymovement 255, Common_Movement_ExclamationMark
    h_waitmovement
    h_giveitem ITEM_DEVON_GOODS, 1                  // key items: Sapphire's names (hoenn_key_items.h, item text)
    h_giveitem ITEM_DEVON_SCOPE, 1
    h_give_pokenav                                  // Black 2's Xtransceiver (boy/girl), named PokéNav
    h_giveitem ITEM_MACH_BIKE, 1                    // Black 2's Bicycle, named Mach Bike
    h_giveitem ITEM_POTION, 1
    h_goto_if_ne HLIB_RESULT, 1, L_TCFail
    h_giveitem ITEM_POTION, 999                     // does not fit: nothing shown, HLIB_RESULT 0
    h_goto_if_ne HLIB_RESULT, 0, L_TCFail
    h_handover_item ITEM_POTION, 1
    h_checkitem ITEM_POTION, 1, HLIB_TMP
    h_goto_if_ne HLIB_TMP, 0, L_TCFail
    h_heal_party_fade
    h_goto_if_badge 1, L_TCFail
    h_givebadge 1
    h_badge_fanfare
    h_goto_if_no_badge 1, L_TCFail
    h_goto_if_badge 2, L_TCFail
    h_goto_if_defeated TRAINER_JOSH, L_TCFail
    h_set_gym_trainers 1
    h_goto_if_not_defeated TRAINER_JOSH, L_TCFail
    h_goto_if_not_defeated TRAINER_TOMMY, L_TCFail
    FlagSet FLAG_RECEIVED_POKENAV                   // Briney: met, at Dewford (his Route 104 boat gone)
    FlagSet FLAG_HIDE_MR_BRINEY_BOAT_ROUTE104
    FlagReset FLAG_HIDE_MR_BRINEY_DEWFORD_TOWN
    WorkSetConst VAR_BRINEY_LOCATION, 0
    VMCall Sub_UpdateBrineyLocation
    h_goto_if_ne VAR_BRINEY_LOCATION, 2, L_TCFail
    VMCall Sub_ResetMrBriney
    h_goto_if_unset FLAG_HIDE_MR_BRINEY_ROUTE109, L_TCFail
    h_goto_if_set FLAG_HIDE_MR_BRINEY_BOAT_DEWFORD, L_TCFail
    VMCall Sub_BackupMrBrineyLocation
    h_goto_if_ne 0x8008, 2, L_TCFail
    h_goto_if_ne VAR_BRINEY_LOCATION, 0, L_TCFail
    VMCall Sub_HideMrBriney
    h_goto_if_unset FLAG_HIDE_MR_BRINEY_DEWFORD_TOWN, L_TCFail
    FlagReset FLAG_RECEIVED_POKENAV                 // (undo the story flags this test set)
    h_get_lead_mon 0x8004                           // ribbons (h_give_ribbon / h_check_ribbon; HOENN_STORY_CODE=1)
    h_check_ribbon HLIB_TMP, 0x8004, RIBBON_EFFORT
    h_goto_if_ne HLIB_TMP, 0, L_TCFail
    h_give_ribbon 0x8004, RIBBON_EFFORT
    h_check_ribbon HLIB_TMP, 0x8004, RIBBON_EFFORT
    h_goto_if_ne HLIB_TMP, 1, L_TCFail
    h_name_received_mon 0
    ActorNew 175, 370, 2, 240, 353, 0               // a stand-in Kecleon beside the player
    h_static_battle SPECIES_KECLEON, 30, FLAG_HIDE_KECLEON_ROUTE120_1, 240
    h_goto_if_unset FLAG_HIDE_KECLEON_ROUTE120_1, L_TCFail
    SEPlay SEQ_SE_MESSAGE
    MsgPlaceSign 0, 1
    MsgPlaceSignClose
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt
L_TCFail:
    SEPlay SEQ_SE_MESSAGE
    MsgPlaceSign 8, 1
    MsgPlaceSignClose
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt
