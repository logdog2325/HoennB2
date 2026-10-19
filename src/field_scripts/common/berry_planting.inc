// Berry planting (HOENN_BERRY_PLANTING; notes/BERRY_PLANTING.md): Gen 3's berry tree script (pokeruby
// data/scripts/berry_tree.inc S_BerryTree, pokeemerald BerryTreeScript) for every tree actor of
// data/story/berries/berry_trees.json (global 8299 = file 1241 Script_300; the actor's uid 400 + tree id tells the code
// which tree). Included by 1241_hidden_items.s (converter/gen_hidden_items.py) when the switch is on.
// The specials are script command 612 (b2tools/patches/berries.c Berry_Cmd): BerryCmd op, arg.
// Names and macros: common/berry_planting_defs.inc (included at the top of the file).

Script_300:                                     // global 8299: talking to a berry tree (S_BerryTree)
    ActorsPauseAll
    BerryCmd BT_OP_GET, 0                       // special ObjectEventInteractionGetBerryTreeData
    VMCall L_BT_Refresh                         // (grown since the actor was made: its picture first)
    WordSetPlayerName 0
    WordSetItemNameEx 1, BT_ITEM, 1, 0          // "Oran Berry"
    bt_goto_if_eq BT_STAGE, 0, L_BT_Soil
    bt_goto_if_eq BT_STAGE, 1, L_BT_Stage1
    bt_goto_if_eq BT_STAGE, 2, L_BT_Stage2
    bt_goto_if_eq BT_STAGE, 3, L_BT_Stage3
    bt_goto_if_eq BT_STAGE, 4, L_BT_Stage4
    VMJump L_BT_Berries

L_BT_Soil:                                      // BerryTree_EventScript_1A153D
    BerryCmd BT_OP_HAS_BERRIES, 0               // specialvar VAR_RESULT, PlayerHasBerries
    bt_goto_if_ne BT_RESULT, 0, L_BT_WantPlant
    SystemMsg BT_T_SOIL, 2
    LastKeyWait
    VMJump L_BT_End
L_BT_WantPlant:
    SystemMsg BT_T_WANTPLANT, 2                 // It's soft, loamy soil. Want to plant a Berry?
    YesNoWin BT_TMP                             // 0 = YES
    bt_goto_if_ne BT_TMP, 0, L_BT_End
    InfoMsgClose                                // fadescreen, Berry_FadeAndGoToBerryBagMenu (Black 2's Bag as the
    BerryCmd BT_OP_BAG_POCKET, 0                //  gourmet's, file 1270: on the Berries pocket)
    WorkSetConst BT_CHOICE, 0
    FadeOutBlackQ
    FadeWait
    FieldClose
    CallBag 1, BT_TMP, BT_CHOICE
    FieldOpen
    FadeInBlackQ
    FadeWait
    bt_goto_if_eq BT_CHOICE, 0, L_BT_End        // compare VAR_ITEM_ID, 0 (closed the Bag)
    BerryCmd BT_OP_PLANT, BT_CHOICE               // special ObjectEventInteractionPlantBerryTree
    bt_goto_if_eq BT_RESULT, 0, L_BT_CantPlant
    ItemSub BT_CHOICE, 1, BT_TMP                // removeitem VAR_ITEM_ID, 1
    VMCall L_BT_Refresh                         // the dirt pile
    WordSetPlayerName 0
    WordSetItemNameEx 1, BT_ITEM, 1, 0
    SystemMsg BT_T_PLANTED, 2                   // {PLAYER} planted one {1} in the soft, loamy soil.
    LastKeyWait
    VMJump L_BT_End
L_BT_CantPlant:                                 // (Black 2's Bag lists every item: one Gen 3 cannot plant)
    WordSetItemNameEx 1, BT_CHOICE, 1, 0
    SystemMsg BT_T_CANTPLANT, 2
    LastKeyWait
    VMJump L_BT_End

L_BT_Stage1:
    SystemMsg BT_T_STAGE1, 2                    // One {1} was planted here.
    VMJump L_BT_WantWater
L_BT_Stage2:
    SystemMsg BT_T_STAGE2, 2                    // {1} has sprouted.
    VMJump L_BT_WantWater
L_BT_Stage3:
    SystemMsg BT_T_STAGE3, 2                    // This {1} plant is growing taller.
    VMJump L_BT_WantWater
L_BT_Stage4:                                    // These {1} flowers are blooming <adverb>: by the times watered
    bt_goto_if_eq BT_WATER, 0, L_BT_Cutely
    bt_goto_if_eq BT_WATER, 4, L_BT_Beautifully
    SystemMsg BT_T_PRETTILY, 2
    VMJump L_BT_WantWater
L_BT_Cutely:
    SystemMsg BT_T_CUTELY, 2
    VMJump L_BT_WantWater
L_BT_Beautifully:
    SystemMsg BT_T_BEAUTIFULLY, 2
L_BT_WantWater:                                 // BerryTree_EventScript_1A165F
    LastKeyWait
    ItemCheckAmount ITEM_SPRAYDUCK, 1, BT_TMP    // checkitem ITEM_WAILMER_PAIL (Sprayduck renamed: gen_key_items.py)
    bt_goto_if_eq BT_TMP, 0, L_BT_End
    SystemMsg BT_T_WANTWATER, 2                 // Want to water the {1} with the Wailmer Pail?
    YesNoWin BT_TMP
    bt_goto_if_ne BT_TMP, 0, L_BT_End
    SystemMsg BT_T_WATERED, 2                   // {PLAYER} watered the {1}.
    BerryCmd BT_OP_WATER, 0                     // special ObjectEventInteractionWaterBerryTree
    LastKeyWait
    SystemMsg BT_T_DELIGHTED, 2                 // The plant seems to be delighted.
    LastKeyWait
    VMJump L_BT_End

L_BT_Berries:                                   // BerryTree_EventScript_1A15F9
    WordSetItemNameEx 1, BT_ITEM, 2, 0          // "Oran Berries"
    WordSetNumber 2, BT_YIELD, 1
    SystemMsg BT_T_PICK, 2                      // There are {2} {1}! Do you want to pick the {1}?
    YesNoWin BT_TMP
    bt_goto_if_eq BT_TMP, 0, L_BT_Pick
    SystemMsg BT_T_LEFT, 2                      // {PLAYER} left the {1} unpicked.
    LastKeyWait
    VMJump L_BT_End
L_BT_Pick:                                      // special ObjectEventInteractionPickBerryTree
    ItemCheckSpace BT_ITEM, BT_YIELD, BT_TMP
    bt_goto_if_ne BT_TMP, 0, L_BT_Room
    SystemMsg BT_T_FULL, 2                      // The Bag's Berries Pocket is full.
    LastKeyWait
    VMJump L_BT_End
L_BT_Room:
    ItemAdd BT_ITEM, BT_YIELD, BT_TMP
    BerryCmd BT_OP_PICK, 0                      // special ObjectEventInteractionRemoveBerryTree: soft soil
    VMCall L_BT_Refresh
    MEPlay SEQ_ME_KINOMI                        // playfanfare MUS_OBTAIN_BERRY
    SystemMsg BT_T_PICKED, 2                    // {PLAYER} picked the {2} {1}.
    MEWait
    LastKeyWait
    SystemMsg BT_T_PUTAWAY, 2                   // ... put away the {1} in the Bag's Berries Pocket. The soil returned ...
    LastKeyWait
L_BT_End:
    InfoMsgClose
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

L_BT_Refresh:                                   // the actor shows the tree's picture now (Black 2 picks a sprite when
    bt_goto_if_eq BT_REFRESH, 0, L_BT_Fresh     //  an actor is made: b2tools/patches/berries.c Berry_ResolveCode)
    ActorDelete BT_UID
    ActorAdd BT_UID
    WorkSetConst BT_REFRESH, 0
L_BT_Fresh:
    VMReturn
