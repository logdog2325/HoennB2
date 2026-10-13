// Route 101's scripts (replaces Route 1's script file 0634, zone 317). Map script table 0635 runs scripts 8 and 9
// on load; they do nothing here. Messages: src/text/script/0516_route_101.txt (the zone's text file, 516).
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_music.inc"

    ScriptEntry Script_1    // sign: Route 101 / Oldale Town
    ScriptEntry Script_2    // NPC: youngster (Sapphire Route101_EventScript_14EA64)
    ScriptEntry Script_3    // NPC: boy (Route101_EventScript_14EA6D)
    ScriptEntry Script_4    // unused
    ScriptEntry Script_5    // unused
    ScriptEntry Script_6    // unused
    ScriptEntry Script_7    // unused
    ScriptEntry Script_8    // map script (0635)
    ScriptEntry Script_9    // map script (0635)
    ScriptEntry Script_10   // trigger: Birch chased by a Poochyena (Sapphire Route101_EventScript_14E948)
    ScriptEntry Script_11   // trigger: "Where are you going?!", step back up (14E9B8)
    ScriptEntry Script_12   // trigger: same, step back right (14E9CE)
    ScriptEntry Script_13   // trigger: same, step back down (14E9E4)
    ScriptEntry Script_14   // Birch's Bag: choose a starter, Poochyena battle, to the lab (14EA7F)
    ScriptEntry Script_15   // Birch / Poochyena while chasing: nothing
    ScriptEntriesEnd

Script_1:
    ActorsPauseAll
    SEPlay SEQ_SE_MESSAGE
    MsgPlaceSign 0, 1
    MsgPlaceSignClose
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_2:
    ActorsPauseAll
    SEPlay SEQ_SE_MESSAGE
    ActorSetEyeToEye
    ParentActorMsg MSGFILE_SCRIPT, 1, 0, 0
    LastKeyWait
    ActorMsgClose
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_3:
    ActorsPauseAll
    SEPlay SEQ_SE_MESSAGE
    ActorSetEyeToEye
    ParentActorMsg MSGFILE_SCRIPT, 2, 0, 0
    LastKeyWait
    ActorMsgClose
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_4:
Script_5:
Script_6:
Script_7:
Script_8:
Script_9:
    VMHalt
    

// Actor ids (NPC uids in data/hoenn_world.json Route101): Birch 10, Poochyena 11 (Emerald: Zigzagoon), Bag 12; 255 = the player.
// VMJumpIf CMP_STACK jumps when the comparison is FALSE (notes/RESEARCH_STORY_SPRITES.md).
Script_10:
    ActorsPauseAll
    h_playbgm_hoenn MUS_HOENN_HELP                // Sapphire: playbgm MUS_HELP (Hoenn music only)
    ActorMsg MSGFILE_SCRIPT, 3, 10, 1, 0          // "H-help me!"
    LastKeyWait
    MsgWinCloseAll
    ActorCmdExec 255, Movement_Up4
    ActorCmdWait
    ActorMsg MSGFILE_SCRIPT, 4, 10, 1, 0          // "Hello! You over there! ... In my Bag!"
    LastKeyWait
    MsgWinCloseAll
    WorkSetConst VAR_ROUTE101_STATE, 2
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_11:
    ActorsPauseAll
    ActorMsg MSGFILE_SCRIPT, 5, 10, 1, 0          // "Wh-Where are you going?!"
    LastKeyWait
    MsgWinCloseAll
    ActorCmdExec 255, Movement_Up1
    ActorCmdWait
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_12:
    ActorsPauseAll
    ActorMsg MSGFILE_SCRIPT, 5, 10, 1, 0
    LastKeyWait
    MsgWinCloseAll
    ActorCmdExec 255, Movement_Right1
    ActorCmdWait
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_13:
    ActorsPauseAll
    ActorMsg MSGFILE_SCRIPT, 5, 10, 1, 0
    LastKeyWait
    MsgWinCloseAll
    ActorCmdExec 255, Movement_Down1
    ActorCmdWait
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_14:
    ActorsPauseAll
    FadeOutBlackQ
    FadeWait
    ActorDelete 11                                // the Poochyena (Sapphire: removeobject 4)
    WorkSetConst 0x8024, 0
    WorkSetConst 0x8025, 0
    FieldClose
    callPoke3Select 0x8024                        // Black 2's three-ball screen (ov316 shows Treecko/Torchic/Mudkip)
    FieldOpen
    FadeInBlackQ
    FadeWait
    VMStackPush 0x8024
    VMStackPushConst 0
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_NotTreecko
    WorkSetConst VAR_STARTER_MON, 0
    Cmd_0209 8, 3
    WorkSetConst 0x8025, SPECIES_TREECKO
    VMJump L_GotStarter
L_NotTreecko:
    VMStackPush 0x8024
    VMStackPushConst 1
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_Mudkip
    WorkSetConst VAR_STARTER_MON, 1
    Cmd_0209 8, 1
    WorkSetConst 0x8025, SPECIES_TORCHIC
    VMJump L_GotStarter
L_Mudkip:
    WorkSetConst VAR_STARTER_MON, 2
    Cmd_0209 8, 2
    WorkSetConst 0x8025, SPECIES_MUDKIP
L_GotStarter:
    PokePartyAdd 0x8010, 0x8025, 0, 5
    FlagSet 2401                                  // Black 2's "has a Pokémon" flag (set right after its own starter)
#ifdef HOENN_EMERALD                              // Emerald: Zigzagoon Lv 2 (pokeemerald battle_controllers.c, BATTLE_TYPE_FIRST_BATTLE;
    CallWildBattle SPECIES_ZIGZAGOON, 2, 0        // its chasing sprite: data/emerald/hoenn_world.json Route101 "#4")
#else
    CallWildBattle SPECIES_POOCHYENA, 2, 0
#endif
    WildBattleIsVictory 0x8010
    VMStackPush 0x8010
    VMStackPushConst 1
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_LostPoochyena
    CallWildBattleEnd
    ActorCmdExec 10, Movement_Right1
    ActorCmdWait
    WordSetPlayerName 0
    ActorMsg MSGFILE_SCRIPT, 6, 10, 1, 0          // "Prof. Birch: Whew... come by my Pokémon Lab later, okay?"
    LastKeyWait
    MsgWinCloseAll
    PokePartyRecoverAll
    FlagSet FLAG_HIDE_BIRCH_BATTLE_POOCHYENA
    FlagSet FLAG_HIDE_BIRCH_STARTERS_BAG
    WorkSetConst VAR_BIRCH_LAB_STATE, 2
    WorkSetConst VAR_ROUTE101_STATE, 3
#ifdef HOENN_EMERALD                              // Emerald (Route101_EventScript_HideMay/BrendanInBedroom): the rival is out of the room
    TrainerCardGetSex 0x8011
    WorkCmpConst 0x8011, 0
    VMJumpIf CMP_EQ, L_EmHideMayInBedroom
    FlagSet FLAG_HIDE_LITTLEROOT_TOWN_BRENDANS_HOUSE_RIVAL_BEDROOM
    VMJump L_EmHideBedroomDone
L_EmHideMayInBedroom:
    FlagSet FLAG_HIDE_LITTLEROOT_TOWN_MAYS_HOUSE_RIVAL_BEDROOM
L_EmHideBedroomDone:
#endif
    FadeOutBlack
    RTReserveScript 11                            // Birch's lab (zone 396) Script_11: "keep it" + nickname
    FadeWait
    MapChangeCore 396, 7, 0, 6, 0                  // Sapphire warp (6,5) facing Birch at (6,4) (lab room offset +1,+1)
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt
L_LostPoochyena:
    CallWildLose
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_15:
    VMHalt

    .balign 4, 0                                   // movement lists are read as words (Black 2 aligns them too)

Movement_Up4:
    Move 12, 4
    MoveEnd

Movement_Up1:
    Move 12, 1
    MoveEnd

Movement_Right1:
    Move 15, 1
    MoveEnd

Movement_Down1:
    Move 13, 1
    MoveEnd
    .balign 4, 0
