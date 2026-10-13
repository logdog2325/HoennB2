// Littleroot Town: chapter Ch1's beats (Sapphire data/maps/LittlerootTown/scripts.inc), included at the end of
// 0778_littleroot_town.s (Ch0's zone file; scripts 10-16 are Ch1's, notes/STORY_CHAPTERS.md "foreign beats").
//   10-15  LittlerootTown_EventScript_GiveRunningShoesTrigger0..5: Mom stops you after the Pokédex (VAR_LITTLEROOT_STATE
//          3) and gives the Running Shoes (story triggers: data/story/ch1.json)
//   16     LittlerootTown_EventScript_Mom: talking to her in front of the door does the same
//   Ch1_LittlerootInit  (VMCall from the zone init, 0778 Script_9): LittlerootTown_OnTransition's Ch1 parts
//          (SetMomStandingInFrontOfDoorPos, SetRivalLeftForRoute103)
//   Test_Ch1_Sign  (test builds only, HOENN_TEST_CH1=1: the town sign): the state after the Pokédex, see below.
// Text: lines 11-15 of src/text/script/0618_littleroot_town.txt (LR1(n) below). Zone tiles = Sapphire + (168, 352).
// Mom = Sapphire object 4 (uid 104, sprite 251, FLAG_HIDE_MOM_LITTLEROOT), a story NPC at her boy's spot (5,9); she is
// the zone's 4th NPC (index 3: twin, fat man, boy come first, data/hoenn_world.json), which ObjInitNPCGPos needs.
#define LR1(n) (11 + (n))
#define LR_MOM 104
#define LR_MOM_INDEX 3

Script_10:                                       // GiveRunningShoesTrigger0 (Sapphire (10,2)): Mom from (10,9)
    h_lock
    h_setvar 0x8008, 0
    ActorSetGPos LR_MOM, 178, 1, 361, 0          // setobjectxy 4, 10, 9 (grid y 1 = Littleroot's ground, 16 units)
    VMJump L_LR1_ShoesTrigger
Script_11:                                       // GiveRunningShoesTrigger1 ((11,2)): Mom from (11,9)
    h_lock
    h_setvar 0x8008, 1
    ActorSetGPos LR_MOM, 179, 1, 361, 0
    VMJump L_LR1_ShoesTrigger
Script_12:                                       // GiveRunningShoesTrigger2 ((10,9))
    h_lock
    h_setvar 0x8008, 2
    VMJump L_LR1_ShoesTrigger

Script_13:                                       // GiveRunningShoesTrigger3 ((11,9))
    h_lock
    h_setvar 0x8008, 3
    VMJump L_LR1_ShoesTrigger
Script_14:                                       // GiveRunningShoesTrigger4 ((8,9))
    h_lock
    h_setvar 0x8008, 4
    VMJump L_LR1_ShoesTrigger
Script_15:                                       // GiveRunningShoesTrigger5 ((9,9))
    h_lock
    h_setvar 0x8008, 5
L_LR1_ShoesTrigger:                              // LittlerootTown_EventScript_GiveRunningShoesTrigger
    h_goto_if_girl L_LR1_NoticeGirl
    h_applymovement LR_MOM, Common_Movement_WalkInPlaceFastestRight   // MomNoticePlayerMale
    VMJump L_LR1_Noticed
L_LR1_NoticeGirl:
    h_applymovement LR_MOM, Common_Movement_WalkInPlaceFastestLeft    // MomNoticePlayerFemale
L_LR1_Noticed:
    h_waitmovement
    VMCall Sub_LR1_HomeDoor
    h_buffer_player
    h_msgbox_actor LR1(0), LR_MOM                // Mom: Wait, <player>!
    h_closemessage
    h_goto_if_girl L_LR1_ApproachGirl            // MomApproachPlayerMale / Female
    h_goto_if_eq 0x8008, 2, L_LR1_ApproachM2
    h_goto_if_eq 0x8008, 3, L_LR1_ApproachM3
    h_goto_if_eq 0x8008, 4, L_LR1_ApproachM4
    h_goto_if_eq 0x8008, 5, L_LR1_ApproachM5
    VMJump L_LR1_Approach01
L_LR1_ApproachGirl:
    h_goto_if_eq 0x8008, 2, L_LR1_ApproachF2
    h_goto_if_eq 0x8008, 3, L_LR1_ApproachF3
    h_goto_if_eq 0x8008, 4, L_LR1_ApproachF4
    h_goto_if_eq 0x8008, 5, L_LR1_ApproachF5
L_LR1_Approach01:                                // MomApproachPlayer0 / 1: she comes up 6 tiles
    h_applymovement 255, Common_Movement_WalkInPlaceFastestDown
    h_waitmovement
    h_applymovement LR_MOM, Mv_LR1_Up6
    VMJump L_LR1_Approached
L_LR1_ApproachM2:
    h_applymovement 255, Common_Movement_WalkInPlaceFastestLeft
    h_waitmovement
    h_applymovement LR_MOM, Mv_LR1_Right4
    VMJump L_LR1_Approached
L_LR1_ApproachM3:
    h_applymovement 255, Common_Movement_WalkInPlaceFastestLeft
    h_waitmovement
    h_applymovement LR_MOM, Mv_LR1_Right5
    VMJump L_LR1_Approached
L_LR1_ApproachM4:
    h_applymovement 255, Common_Movement_WalkInPlaceFastestLeft
    h_waitmovement
    h_applymovement LR_MOM, Mv_LR1_Right2
    VMJump L_LR1_Approached
L_LR1_ApproachM5:
    h_applymovement 255, Common_Movement_WalkInPlaceFastestLeft
    h_waitmovement
    h_applymovement LR_MOM, Mv_LR1_Right3
    VMJump L_LR1_Approached
L_LR1_ApproachF2:
    h_applymovement 255, Common_Movement_WalkInPlaceFastestRight
    h_waitmovement
    h_applymovement LR_MOM, Mv_LR1_Left3
    VMJump L_LR1_Approached
L_LR1_ApproachF3:
    h_applymovement 255, Common_Movement_WalkInPlaceFastestRight
    h_waitmovement
    h_applymovement LR_MOM, Mv_LR1_Left2
    VMJump L_LR1_Approached
L_LR1_ApproachF4:
    h_applymovement 255, Common_Movement_WalkInPlaceFastestRight
    h_waitmovement
    h_applymovement LR_MOM, Mv_LR1_Left5
    VMJump L_LR1_Approached
L_LR1_ApproachF5:
    h_applymovement 255, Common_Movement_WalkInPlaceFastestRight
    h_waitmovement
    h_applymovement LR_MOM, Mv_LR1_Left4
L_LR1_Approached:
    h_waitmovement
    VMCall Sub_LR1_GiveRunningShoes
    h_goto_if_girl L_LR1_ReturnGirl              // MomReturnHomeMale / Female
    h_goto_if_eq 0x8008, 2, L_LR1_ReturnM2
    h_goto_if_eq 0x8008, 3, L_LR1_ReturnM3
    h_goto_if_eq 0x8008, 4, L_LR1_ReturnM4
    h_goto_if_eq 0x8008, 5, L_LR1_ReturnM5
    VMJump L_LR1_Return01
L_LR1_ReturnGirl:
    h_goto_if_eq 0x8008, 2, L_LR1_ReturnF2
    h_goto_if_eq 0x8008, 3, L_LR1_ReturnF3
    h_goto_if_eq 0x8008, 4, L_LR1_ReturnF4
    h_goto_if_eq 0x8008, 5, L_LR1_ReturnF5
L_LR1_Return01:                                  // MomReturnHome0 / 1: down 5, no door
    h_applymovement LR_MOM, Mv_LR1_Down5
    h_waitmovement
    VMJump L_LR1_SetReceived
L_LR1_ReturnM2:
    h_applymovement LR_MOM, Mv_LR1_Left4Up
    VMJump L_LR1_IntoHouse
L_LR1_ReturnM3:
    h_applymovement LR_MOM, Mv_LR1_Left5Up
    VMJump L_LR1_IntoHouse
L_LR1_ReturnM4:
    h_applymovement LR_MOM, Mv_LR1_Left2Up
    VMJump L_LR1_IntoHouse
L_LR1_ReturnM5:
    h_applymovement LR_MOM, Mv_LR1_Left3Up
    VMJump L_LR1_IntoHouse
L_LR1_ReturnF2:
    h_applymovement LR_MOM, Mv_LR1_Right3Up
    VMJump L_LR1_IntoHouse
L_LR1_ReturnF3:
    h_applymovement LR_MOM, Mv_LR1_Right2Up
    VMJump L_LR1_IntoHouse
L_LR1_ReturnF4:
    h_applymovement LR_MOM, Mv_LR1_Right5Up
    VMJump L_LR1_IntoHouse
L_LR1_ReturnF5:
    h_applymovement LR_MOM, Mv_LR1_Right4Up
L_LR1_IntoHouse:
    h_waitmovement
    VMCall Sub_LR1_MomThroughDoor
L_LR1_SetReceived:                               // LittlerootTown_EventScript_SetReceivedRunningShoes
    h_removeobject LR_MOM, FLAG_HIDE_MOM_LITTLEROOT
    GiveRunningShoes                             // setflag FLAG_SYS_B_DASH (Black 2's command sets flag 2403)
    h_setvar VAR_LITTLEROOT_STATE, 4
    h_release

Script_16:                                       // LittlerootTown_EventScript_Mom (in front of the door)
    h_lock
    h_faceplayer
    VMCall Sub_LR1_HomeDoor
    VMCall Sub_LR1_GiveRunningShoes
    h_applymovement LR_MOM, Common_Movement_WalkInPlaceFastestUp
    h_waitmovement
    VMCall Sub_LR1_MomThroughDoor
    VMJump L_LR1_SetReceived


Sub_LR1_HomeDoor:                                // SetHomeDoorCoordsMale / Female: (5,8) / (14,8)
    h_setvar 0x8009, 173
    h_goto_if_boy L_LR1_DoorSet
    h_setvar 0x8009, 182
L_LR1_DoorSet:
    h_setvar 0x800A, 360
    VMReturn

Sub_LR1_MomThroughDoor:                          // opendoor, walk up, hideobjectat, closedoor
    BMCreateHandleByGPos 0x8020, 1, 0x8009, 0x800A   // the house's door model (as the arrival scene, Script_31)
    BMHndAudioVisualAnmPlay 0x8020, 0
    BMHndAnmWait 0x8020
    h_applymovement LR_MOM, Mv_LR1_ExitThroughDoor
    h_waitmovement
    BMHndAudioVisualAnmPlay 0x8020, 1
    BMHndAnmWait 0x8020
    BMReleaseHandle 0x8020
    VMReturn

Sub_LR1_GiveRunningShoes:                        // LittlerootTown_EventScript_GiveRunningShoes
    h_buffer_player
    h_msgbox_actor LR1(1), LR_MOM                // Mom: <player>! <player>! Did you introduce yourself ...
    h_closemessage
    h_playfanfare MUS_OBTAIN_ITEM
    SystemMsg LR1(2), 1                          // <player> switched shoes with the Running Shoes.
    MEWait
    MsgWaitAdvance
    InfoMsgClose
    h_setflag FLAG_RECEIVED_RUNNING_SHOES
    h_msgbox_actor LR1(3), LR_MOM                // Mom: <player>, those shoes came with instructions. ...
    h_msgbox_actor LR1(4), LR_MOM                // ... To think that you have your very own Pokémon now...
    h_closemessage
    h_delay 30
    VMReturn

Ch1_LittlerootInit:                              // LittlerootTown_OnTransition, Ch1's parts
    h_goto_if_ne VAR_LITTLEROOT_STATE, 3, L_LR1_InitMomDone
    h_clearflag FLAG_HIDE_MOM_LITTLEROOT         // SetMomStandingInFrontOfDoorPos: (5,9) / (14,9), facing down
    h_goto_if_boy L_LR1_InitMomDone
    ObjInitNPCGPos LR_MOM_INDEX, 1, 182, 0, 361
L_LR1_InitMomDone:
    h_goto_if_ne VAR_LITTLEROOT_RIVAL_STATE, 3, L_LR1_InitRivalDone
    h_setflag FLAG_RIVAL_LEFT_FOR_ROUTE103       // SetRivalLeftForRoute103
L_LR1_InitRivalDone:
    VMReturn

#ifdef HOENN_TEST_CH1
// TEST ONLY (HOENN_TEST_CH1=1, b2tools/patches/scripts.py): Littleroot's town sign (stand at (183,366) facing north)
// gives the state the chapter starts from: Ch0 done, the Route 103 battle won, the Pokédex and 10 Poké Balls received
// (as 0792 Script_12 leaves it), a Lv 50 Mudkip as the starter if the party is empty; then it reloads Littleroot in
// front of the player's house so the zone init places Mom (the Running Shoes triggers are armed).
// HOENN_TEST_CH1=2: only Ch0's end (starter, Birch rescued), for Oldale before the Pokédex; 3: the catching demo
// alone; 4: after Wally's tutorial, at Petalburg Woods' south door; 5: after the woods, at Rustboro's Gym; 6: also
// three badges and the flower shop owner met, at the flower shop's door; 7: 5 and a Slakoth for Rustboro's trade.
Test_Ch1_Sign:
#if HOENN_TEST_CH1 == 3                          // HOENN_TEST_CH1=3: Wally's catching demo alone (capture_demo patch)
    PokePartyGetCount 0x8000, 0
    h_goto_if_ne 0x8000, 0, L_TC1_Demo
    PokePartyAdd 0x8001, SPECIES_MUDKIP, 0, 50
L_TC1_Demo:
    CallCaptureDemo
    CallWildBattleEnd
    h_release
#endif
    PokePartyGetCount 0x8000, 0
    h_goto_if_ne 0x8000, 0, L_TC1_Party
    PokePartyAdd 0x8001, SPECIES_MUDKIP, 0, 50
    h_setvar VAR_STARTER_MON, 2
L_TC1_Party:
    FlagSet 2401                                 // has a Pokémon (Black 2)
    h_setflag FLAG_RESCUED_BIRCH
    h_setflag FLAG_HIDE_BIRCH_BATTLE_POOCHYENA
    h_setflag FLAG_HIDE_BIRCH_STARTERS_BAG
    h_setvar VAR_ROUTE101_STATE, 3
    h_setvar VAR_BIRCH_LAB_STATE, 3
#if HOENN_TEST_CH1 == 2                          // HOENN_TEST_CH1=2: before the Route 103 battle (Oldale's blocked path
    h_setvar VAR_LITTLEROOT_STATE, 2             //   and the Mart's small list), no Pokédex
    MapChangeWarp 389, 177, 362, 0
    h_release
#endif
    FlagSet 2402                                 // has the Pokédex (Black 2)
    h_setflag FLAG_SYS_POKEDEX_GET
    h_setvar VAR_ROUTE103_STATE, 1
    h_setflag FLAG_DEFEATED_RIVAL_ROUTE103
    h_setflag FLAG_HIDE_RIVAL_ROUTE103
    h_setflag FLAG_HIDE_RIVAL_OLDALE_TOWN
    h_clearflag FLAG_HIDE_RIVAL_BIRCH_LAB
    h_setvar VAR_OLDALE_STATE, 2
    h_setvar VAR_BIRCH_LAB_STATE, 5
    h_setflag FLAG_ADVENTURE_STARTED
    h_setvar VAR_ROUTE102_ACCESSIBLE, 1
    h_setvar VAR_LITTLEROOT_RIVAL_STATE, 4
    h_setvar VAR_LITTLEROOT_STATE, 3
    ItemAdd ITEM_POKE_BALL, 10, 0x8000
#if HOENN_TEST_CH1 >= 4                          // 4: after Wally's tutorial (Running Shoes, Potion, Dad's advice),
    h_setflag FLAG_HIDE_MOM_LITTLEROOT           //    on Route 104 below Petalburg Woods' south door (Sapphire (10,39))
    GiveRunningShoes                             // 5: also after Petalburg Woods, in front of Rustboro's Gym (27,20)
    h_setflag FLAG_RECEIVED_RUNNING_SHOES
    h_setvar VAR_LITTLEROOT_STATE, 4
    h_setflag FLAG_RECEIVED_POTION_OLDALE
    h_setflag FLAG_VISITED_OLDALE_TOWN
    h_setflag FLAG_VISITED_PETALBURG_CITY
    h_setflag FLAG_HIDE_WALLY_MOM_PETALBURG_1
    h_setflag FLAG_HIDE_WALLY_PETALBURG
    h_setflag FLAG_HIDE_WALLY_PETALBURG_GYM
    h_setflag FLAG_HIDE_RIVAL_BIRCH_LAB
    h_setvar VAR_BIRCH_STATE, 0
    h_setvar VAR_PETALBURG_STATE, 3
    h_setvar VAR_PETALBURG_GYM_STATE, 2
#if HOENN_TEST_CH1 >= 5
    h_setvar VAR_PETALBURG_WOODS_STATE, 1
    h_setflag FLAG_HIDE_DEVON_PETALBURG_WOODS
    h_setflag FLAG_HIDE_EVIL_TEAM_PETALBURG_WOODS
    ItemAdd ITEM_GREAT_BALL, 1, 0x8000
#if HOENN_TEST_CH1 == 7                          // 7: also a Lv 9 Slakoth (Rustboro's trade), in front of the Gym
    PokePartyAdd 0x8001, SPECIES_SLAKOTH, 0, 9
    MapChangeWarp 113, 75, 200, 0
#elif HOENN_TEST_CH1 >= 6                        // 6: also three badges and the flower shop owner met (Route 104's
    h_givebadge 1                                //    worker outside with the White Herb, the owner's shop), by the
    h_givebadge 2                                //    flower shop's door (Sapphire (5,19))
    h_givebadge 3
    h_setflag FLAG_MET_PRETTY_PETAL_SHOP_OWNER
    MapChangeWarp 329, 53, 259, 0
#else
    MapChangeWarp 113, 75, 200, 0
#endif
#else
    MapChangeWarp 329, 58, 279, 0
#endif
    h_release
#endif
    MapChangeWarp 389, 177, 362, 0               // in front of the houses, facing up (zone init runs again)
    h_release
#endif

    .balign 4, 0
Mv_LR1_Up6:
    walk_up 6
    step_end
Mv_LR1_Down5:
    walk_down 5
    step_end
Mv_LR1_Right2:
    walk_right 2
    step_end
Mv_LR1_Right3:
    walk_right 3
    step_end
Mv_LR1_Right4:
    walk_right 4
    step_end
Mv_LR1_Right5:
    walk_right 5
    step_end
Mv_LR1_Left2:
    walk_left 2
    step_end
Mv_LR1_Left3:
    walk_left 3
    step_end
Mv_LR1_Left4:
    walk_left 4
    step_end
Mv_LR1_Left5:
    walk_left 5
    step_end
Mv_LR1_Left2Up:                                  // MomReturnHomeMale4
    walk_left 2
    walk_in_place_fastest_up
    step_end
Mv_LR1_Left3Up:                                  // MomReturnHomeMale5
    walk_left 3
    walk_in_place_fastest_up
    step_end
Mv_LR1_Left4Up:                                  // MomReturnHomeMale2
    walk_left 4
    walk_in_place_fastest_up
    step_end
Mv_LR1_Left5Up:                                  // MomReturnHomeMale3
    walk_left 5
    walk_in_place_fastest_up
    step_end
Mv_LR1_Right2Up:                                 // MomReturnHomeFemale3
    walk_right 2
    walk_in_place_fastest_up
    step_end
Mv_LR1_Right3Up:                                 // MomReturnHomeFemale2
    walk_right 3
    walk_in_place_fastest_up
    step_end
Mv_LR1_Right4Up:                                 // MomReturnHomeFemale5
    walk_right 4
    walk_in_place_fastest_up
    step_end
Mv_LR1_Right5Up:                                 // MomReturnHomeFemale4
    walk_right 5
    walk_in_place_fastest_up
    step_end
Mv_LR1_ExitThroughDoor:                          // walk_up, then hideobjectat (set_invisible)
    walk_up
    set_invisible
    step_end
