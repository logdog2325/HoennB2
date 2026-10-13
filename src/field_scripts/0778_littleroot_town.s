// Littleroot Town's scripts (replaces Nuvema Town's script file 0778, zone 389).
// Built with the Black 2 decomp's macros (external/pokebw2/include/asm/field_script.inc).
// Messages are lines of src/text/script/0618_littleroot_town.txt (the zone's text file, 618).
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_trainers.h"
#include "hoenn_key_items.h"
#include "hoenn_story.inc"                      // (chapter Ch1's scenes/LittlerootTown_ch1.inc and the test switches)

    ScriptEntry Script_1    // sign: Littleroot Town
    ScriptEntry Script_2    // sign: player's house (Sapphire: Brendan's house)
    ScriptEntry Script_3    // sign: Prof. Birch's house
    ScriptEntry Script_4    // sign: Prof. Birch's Pokémon Lab
    ScriptEntry Script_5    // NPC: twin (Sapphire LittlerootTown_EventScript_Twin, before the story starts)
    ScriptEntry Script_6    // NPC: fat man (LittlerootTown_EventScript_FatMan)
    ScriptEntry Script_7    // NPC: boy (LittlerootTown_EventScript_Boy)
    ScriptEntry Script_8    // unused
    ScriptEntry Script_9    // map-load script (0779 runs script 9); Nuvema's rival setup is not wanted here
    ScriptEntry Script_10   // Ch1: GiveRunningShoesTrigger0 (scenes/LittlerootTown_ch1.inc)
    ScriptEntry Script_11   // Ch1: GiveRunningShoesTrigger1 (scenes/LittlerootTown_ch1.inc)
    ScriptEntry Script_12   // Ch1: GiveRunningShoesTrigger2 (scenes/LittlerootTown_ch1.inc)
    ScriptEntry Script_13   // Ch1: GiveRunningShoesTrigger3 (scenes/LittlerootTown_ch1.inc)
    ScriptEntry Script_14   // Ch1: GiveRunningShoesTrigger4 (scenes/LittlerootTown_ch1.inc)
    ScriptEntry Script_15   // Ch1: GiveRunningShoesTrigger5 (scenes/LittlerootTown_ch1.inc)
    ScriptEntry Script_16   // Ch1: Mom in front of the door (LittlerootTown_EventScript_Mom)
    ScriptEntry Script_17
    ScriptEntry Script_18
    ScriptEntry Script_19
    ScriptEntry Script_20
    ScriptEntry Script_21
    ScriptEntry Script_22
    ScriptEntry Script_23
    ScriptEntry Script_24
    ScriptEntry Script_25
    ScriptEntry Script_26   // post-game: Emerald's BeginDexUpgradeScene (scenes/LittlerootTown_Postgame.inc)
    ScriptEntry Script_27
    ScriptEntry Script_28
    ScriptEntry Script_29   // new game, before the fade-in: nothing
    ScriptEntry Script_30   // new game (b2tools/patches/opening.py), after the fade-in: respawn, warp to the truck spot
    ScriptEntry Script_31   // reserved by 30: Mom greets the player (Sapphire LittlerootTown_EventScript_GoInsideWithMom)
    ScriptEntriesEnd

Script_1:
    ActorsPauseAll
#ifdef HOENN_TEST_CHPOSTGAME
    VMJump Test_PG_Sign                           // test only: the post-game start state + warp (scenes/postgame_test.inc)
#endif
#ifdef HOENN_TEST_CHCREDITS
    VMJump Test_CreditsShots                      // test only: the halloffame agent's credits pictures (scenes/halloffame_test.inc)
#endif
#ifdef HOENN_TEST_CHBOATS
    VMJump Test_Boats                             // test only: the boats agent's demo survey (common/boat_test.inc)
#endif
#ifdef HOENN_TEST_CH13_W1
    VMJump Test_Ch13Warp1                         // test only: chapter Ch13's start state + warp (scenes/ch13_test.inc)
#endif
#ifdef HOENN_TEST_CHZE_W1
    h_warp_arrive HOENN_TEST_CHZE_W1               // test only (zone_edges): warp to "zone,x,z,dir" (no start state)
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt
#endif
#ifdef HOENN_TEST_COMMON
    FlagReset FLAG_DAILY_BERRY_SPOTS                // TEST ONLY: the town sign plays midnight for the berry spots
#endif
#ifdef HOENN_TEST_CH1
    VMJump Test_Ch1_Sign                        // test only: chapter Ch1's start state (scenes/LittlerootTown_ch1.inc)
#endif
#ifdef HOENN_TEST_SPRITES
    // Test builds only (HOENN_TEST_SPRITES=trainer,code, b2tools/patches/scripts.py; default 345,353): the town sign
    // shows the redrawn character sprites (b2tools/sprite_upgrade.py): object code TEST_SPRITES_CODE walks a loop
    // beside the player, then a battle with Black 2 trainer TEST_SPRITES_TRAINER (345 = class TEAM_PLASMA_GHETSIS,
    // whose front sprite 151 is now Archie; 39 = ELITE_FOUR_MARSHAL, front sprite 78 = Drake).
    ActorNew 180, 366, 1, 240, TEST_SPRITES_CODE, 0
    ActorCmdExec 240, Movement_TestSpriteLoop
    ActorCmdWait
    PokePartyGetCount 0x8000, 0                 // a battle with an empty party hangs: lend a Lv 50 Mudkip
    VMStackPush 0x8000
    VMStackPushConst 0
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_TestSpriteParty
    PokePartyAdd 0x8001, SPECIES_MUDKIP, 0, 50
L_TestSpriteParty:
    CallTrainerBattle TEST_SPRITES_TRAINER, 0, 0
    TrainerBattleIsVictory 0x8010
    VMStackPush 0x8010
    VMStackPushConst 1
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_TestSpriteLost      // (jumps when the comparison is false)
    CallTrainerBattleEnd
    ActorDelete 240
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt
L_TestSpriteLost:
    CallTrainerLose
    VMHalt
#endif
#ifdef HOENN_TEST_TWO
    // Test builds only (HOENN_TEST_TWO=1, b2tools/patches/scripts.py): the town sign starts the Tate & Liza battle
    // (h_trainerbattle_two, src/include/hoenn_story.inc), lending Lv 100 Tyranitars until two can battle
L_TestTwoParty:
    h_goto_if_cannot_double L_TestTwoAdd
    h_trainerbattle_two TRAINER_TATE, TRAINER_LIZA
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt
L_TestTwoAdd:
    PokePartyAdd 0x8001, SPECIES_TYRANITAR, 0, 100
    VMJump L_TestTwoParty
#endif
#ifdef HOENN_TEST_CHMO
    VMCall Test_MO_Setup                          // test only: the missing objects' start state (scenes/missing_objects_test.inc)
#endif
#ifdef HOENN_TEST_CHSC
    VMCall Test_SC_Setup                          // test only: script_check's start states (scenes/script_check_test.inc)
#endif
#ifdef HOENN_TEST_CHFA
    VMJump Test_FA_Start                          // test only: fairy_core's battle kit (scenes/fairy_test.inc)
#endif
#ifdef HOENN_TEST_CHTM
    VMCall Test_TM_Setup                          // test only: town_map's start state (scenes/town_map_test.inc)
#endif
#ifdef HOENN_TEST_WARP
    // Test builds only (HOENN_TEST_WARP=zone,x,z, b2tools/patches/scripts.py): the town sign warps there, as Black 2's
    // scripted warps do (story_finish): fade out, reserve the global arrival script 10017 (hm_free.py Script_18: fade in,
    // FinishAllEvents, ActorsUnpauseAll), map change. A scripted map change needs a FadeInBlack after it (here the arrival
    // script's; or in the same script): without one, NPC balloons never show or crash and nobody answers (tested).
    h_warp_arrive TEST_WARP_ZONE, TEST_WARP_X, TEST_WARP_Z, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt
#endif
    SEPlay SEQ_SE_MESSAGE
    MsgPlaceSign 0, 1
    MsgPlaceSignClose
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_2:
    ActorsPauseAll
#ifdef HOENN_TEST_CH13_W2
    VMJump Test_Ch13Warp2                         // test only: chapter Ch13's start state + warp (scenes/ch13_test.inc)
#endif
#ifdef HOENN_TEST_CHZE_W2
    h_warp_arrive HOENN_TEST_CHZE_W2               // test only (zone_edges): warp to "zone,x,z,dir" (no start state)
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt
#endif
#ifdef HOENN_TEST_MOVES
    // Test builds only (HOENN_TEST_MOVES=1, b2tools/patches/scripts.py): the player's house sign plays every movement
    // group of notes/STORY_PORTING.md on the player, one list at a time with 30-frame pauses, so a harness that logs
    // the player's tile each frame can time them (work/agents/story_infra/tests/moves_probe.py).
    VMCall Sub_TestMoves
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt
#endif
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    MsgPlaceSign 1, 2
    MsgPlaceSignClose
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_3:
    ActorsPauseAll
#ifdef HOENN_TEST_CHPOSTGAME
    VMJump Test_PG_Sign2                          // test only: the post-game start state with the National Dex + roamers (scenes/postgame_test.inc)
#endif
#ifdef HOENN_TEST_CH13_W3
    VMJump Test_Ch13Warp3                         // test only: chapter Ch13's start state + warp (scenes/ch13_test.inc)
#endif
#ifdef HOENN_TEST_CHZE_W3
    h_warp_arrive HOENN_TEST_CHZE_W3               // test only (zone_edges): warp to "zone,x,z,dir" (no start state)
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt
#endif
#ifdef HOENN_TEST_TWO
    // Test builds only (HOENN_TEST_TWO=1): Birch's house sign battles May (TRAINER_MAY_4, Route 103) to show her
    // defeat line with the player's name in battle (b2tools/patches/trainers.py battle_trainer_msg)
    PokePartyGetCount 0x8000, 2
    WorkCmpConst 0x8000, 0
    VMJumpIf CMP_NE, L_TestMayBattle
    PokePartyAdd 0x8001, SPECIES_MUDKIP, 0, 50
L_TestMayBattle:
    h_trainerbattle TRAINER_MAY_4
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt
#endif
    SEPlay SEQ_SE_MESSAGE
    MsgPlaceSign 2, 2
    MsgPlaceSignClose
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_4:
    ActorsPauseAll
#ifdef HOENN_TEST_CHPOSTGAME
    VMJump Test_PG_HoF                            // test only: the post-game start state + the Hall of Fame scene (scenes/postgame_test.inc)
#endif
#ifdef HOENN_TEST_CH13_W4
    VMJump Test_Ch13Warp4                         // test only: chapter Ch13's start state + warp (scenes/ch13_test.inc)
#endif
#ifdef HOENN_TEST_CHZE_W4
    h_warp_arrive HOENN_TEST_CHZE_W4               // test only (zone_edges): warp to "zone,x,z,dir" (no start state)
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt
#endif
#ifdef HOENN_TEST_COMMON
#include "common/test_common.inc"
#endif
    SEPlay SEQ_SE_MESSAGE
    MsgPlaceSign 3, 2
    MsgPlaceSignClose
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_5:                                       // Sapphire LittlerootTown_EventScript_Twin
    ActorsPauseAll
    SEPlay SEQ_SE_MESSAGE
    ActorSetEyeToEye
#ifdef HOENN_TEST_CHTWIN                         // test builds only: the first talk is the usual one, from the second on the adventure counts as started
    h_goto_if_set FLAG_DEFEATED_ELITE_4_SYDNEY, L_Test_TwinStarted
    h_setflag FLAG_DEFEATED_ELITE_4_SYDNEY
    VMJump L_Test_TwinHookDone
L_Test_TwinStarted:
    h_setflag FLAG_ADVENTURE_STARTED
L_Test_TwinHookDone:
#endif
#ifdef HOENN_EMERALD
    h_goto_if_set FLAG_ADVENTURE_STARTED, L_Em_TwinGoodLuck   // Emerald: once the adventure has started (starter chosen)
#endif
    VMStackPush VAR_ROUTE101_STATE
    VMStackPushConst 3
    VMStackCmp CMP_GE
    VMJumpIf CMP_STACK, L_TwinNotRescued       // (jumps when the comparison is false)
    ParentActorMsg MSGFILE_SCRIPT, 10, 0, 0        // "Boy, am I glad you went and rescued the Professor."
    VMJump L_TwinDone
L_TwinNotRescued:
    VMStackPush VAR_LITTLEROOT_STATE
    VMStackPushConst 0
    VMStackCmp CMP_NE
    VMJumpIf CMP_STACK, L_TwinGrass
    ParentActorMsg MSGFILE_SCRIPT, 9, 0, 0         // "I can hear someone shouting down the road here..."
    WorkSetConst VAR_LITTLEROOT_STATE, 2
    VMJump L_TwinDone
L_TwinGrass:
    ParentActorMsg MSGFILE_SCRIPT, 4, 0, 0         // "If you go in the tall grass..."
L_TwinDone:
    LastKeyWait
    ActorMsgClose
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

#ifdef HOENN_EMERALD
L_Em_TwinGoodLuck:
    ParentActorMsg MSGFILE_SCRIPT, 17, 0, 0        // "Are you going to catch Pokémon? Good luck!"
    VMJump L_TwinDone
#endif

Script_6:
    ActorsPauseAll
    SEPlay SEQ_SE_MESSAGE
    ActorSetEyeToEye
    ParentActorMsg MSGFILE_SCRIPT, 5, 0, 0
    LastKeyWait
    ActorMsgClose
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_7:
    ActorsPauseAll
    SEPlay SEQ_SE_MESSAGE
    ActorSetEyeToEye
    ParentActorMsg MSGFILE_SCRIPT, 6, 0, 0
    LastKeyWait
    ActorMsgClose
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_8:
    VMHalt

Script_9:
#ifdef HOENN_TEST_TRUCK
    // Test builds only (HOENN_TEST_TRUCK=1, b2tools/patches/scripts.py): hide the moving truck at Brendan's house
    // (building res 460, info type 11 -> BMSetVisible type 8). Script 9 runs at zone init (MapScript 2), before the
    // field and its building models exist (a direct BMSetVisible here hangs the game after a warp, tested), so it
    // reserves itself (RTReserveScript, as 0274.s does) and hides the truck on that second run, once the field is up.
    VMStackPush 0x401F                      // map-local work, wiped at every zone init
    VMStackPushConst 0
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_TestTruckHide     // (jumps when the comparison is false: the reserved run)
    WorkSetConst 0x401F, 1
    RTReserveScript 9
    VMJump L_TestTruckDone
L_TestTruckHide:
    BMSetVisible 8, 170, 362, 0
    VMHalt
L_TestTruckDone:
#endif
#ifdef HOENN_TEST_PARTY
    // Test builds only (HOENN_TEST_PARTY=1, b2tools/patches/scripts.py): the test savestates have an empty party,
    // and a wild battle with no Pokémon hangs. Give a Lv 50 Mudkip on entering Littleroot if the party is empty.
    PokePartyGetCount 0x8000, 0
    VMStackPush 0x8000
    VMStackPushConst 0
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_TestPartyDone     // (jumps when the comparison is false)
    PokePartyAdd 0x8001, SPECIES_MUDKIP, 0, 50
L_TestPartyDone:
#endif
    // Sapphire LittlerootTown_EventScript_SetTwinPos: until Birch is rescued the twin (uid 1) stands at the north
    // exit, guarding it (Sapphire (7,2), facing down) before the player has met the rival, beside it (10,1) after.
    // She stands still (data/hoenn_world.json move 0; Sapphire's wandering after the rescue is not done yet).
    VMStackPush VAR_ROUTE101_STATE
    VMStackPushConst 3
    VMStackCmp CMP_LT
    VMJumpIf CMP_STACK, L_TwinPosDone
    VMStackPush VAR_LITTLEROOT_STATE
    VMStackPushConst 0
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_TwinBeside
    ObjInitNPCGPos 0, 1, 175, 0, 354               // (takes the NPC's index in the zone's list: the twin is first)
    VMJump L_TwinPosDone
L_TwinBeside:
    ObjInitNPCGPos 0, 0, 178, 0, 353               // beside the exit, facing up (Sapphire FACE_UP)
L_TwinPosDone:
    // Sapphire LittlerootTown_EventScript_MoveRivalFromOldale (chapter Ch1): coming home after Route 103 without
    // passing the rival in Oldale moves the rival on to the Lab
    VMStackPush VAR_OLDALE_STATE
    VMStackPushConst 1
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_OldaleRivalDone          // (jumps when the comparison is false)
    WorkSetConst VAR_OLDALE_STATE, 2
    FlagSet FLAG_HIDE_RIVAL_OLDALE_TOWN
L_OldaleRivalDone:
    VMCall Ch1_LittlerootInit                      // chapter Ch1: Mom in front of the door, rival left (scenes/LittlerootTown_ch1.inc)
#if __has_include("scenes/LittlerootTown_ch13.inc")
    VMCall Ch13_LittlerootInit                     // chapter Ch13: the house states after the S.S. Ticket scene (scenes/LittlerootTown_ch13.inc)
#endif
#if __has_include("scenes/LittlerootTown_Postgame.inc")
    VMCall PG_LittlerootInit                       // post-game: the National Dex scene's state and people (scenes/LittlerootTown_Postgame.inc)
#endif
    VMHalt

Script_17:
Script_18:
Script_19:
Script_24:
#if !__has_include("scenes/LittlerootTown_ch13.inc")
Script_25:                                      // chapter Ch13: BeginDexUpgradeScene is in scenes/LittlerootTown_ch13.inc
#endif
#if !__has_include("scenes/LittlerootTown_Postgame.inc")
Script_26:                                      // post-game: BeginDexUpgradeScene (Emerald) is in scenes/LittlerootTown_Postgame.inc
#endif
Script_27:
Script_28:
Script_29:
    VMHalt

// North exit (Sapphire coord events at (10,1)/(11,1) = (178,353)/(179,353), data/hoenn_world.json triggers).

Script_23:                                      // (unused since 2026-10-08) the moving trucks are 3D objects now
    VMHalt                                      // (code 118, data/story/missing_objects.json) hidden by their spawn flags

Script_20:                                      // Sapphire LittlerootTown_EventScript_NeedPokemonTriggerLeft
    ActorsPauseAll
    ActorCmdExec 1, Movement_TwinApproachPlayerLeft
    ActorCmdWait
    VMCall Sub_DangerousWithoutPokemon
    ActorCmdExec 1, Movement_TwinReturnLeft
    ActorCmdWait
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_21:                                      // Sapphire LittlerootTown_EventScript_NeedPokemonTriggerRight
    ActorsPauseAll
    ActorCmdExec 1, Movement_TwinApproachPlayerRight
    ActorCmdWait
    VMCall Sub_DangerousWithoutPokemon
    ActorCmdExec 1, Movement_TwinReturnRight
    ActorCmdWait
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Sub_DangerousWithoutPokemon:
    ActorMsg MSGFILE_SCRIPT, 4, 1, 0, 0          // "If you go in the tall grass..."
    LastKeyWait
    MsgWinCloseAll
    ActorCmdExec 255, Movement_PushPlayerBackFromRoute
    ActorCmdExec 1, Movement_TwinPushPlayerFromRoute
    ActorCmdWait
    ActorMsg MSGFILE_SCRIPT, 8, 1, 0, 0          // "It's not safe to go out there..."
    LastKeyWait
    MsgWinCloseAll
    VMReturn

Script_22:                                      // Sapphire LittlerootTown_EventScript_GoSaveBirchTrigger
    ActorsPauseAll
    ActorCmdExec 1, Movement_FaceRight
    ActorCmdWait
    ActorCmdExec 255, Movement_FaceLeft
    ActorCmdWait
    ActorMsg MSGFILE_SCRIPT, 9, 1, 0, 0          // "I can hear someone shouting down the road here..."
    LastKeyWait
    MsgWinCloseAll
    ActorCmdExec 1, Movement_FaceDown
    ActorCmdWait
    WorkSetConst VAR_LITTLEROOT_STATE, 2
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

// A new game starts in Littleroot (until the moving truck's interior is installed): Black 2 shows the zone with the
// player hidden (actor flag 4), runs script 29 before and 30 after the fade-in; like Black 2's own opening, 30 warps
// so the player is placed visibly, and the reserved 31 plays the scene on the (black) arrival screen.
Script_30:
    FieldSetTeleportZone 1                         // blackout/respawn: the player's house (RESPAWN_ZONE_INFO entry 0)
    FadeOutBlackQ
    FadeWait
    RTReserveScript 31
    TrainerCardGetSex 0x8010
    VMStackPush 0x8010
    VMStackPushConst 0
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_ArriveGirl
    MapChangeCore 389, 171, 0, 362, 1              // boy: Sapphire's truck exit (3,10), facing down
    VMHalt
L_ArriveGirl:
    MapChangeCore 389, 180, 0, 362, 1              // girl: (12,10)
    VMHalt

Script_31:
    // Sapphire LittlerootTown_EventScript_GoInsideWithMom: the player hops off the truck, Mom comes out of the
    // house, greets the player, and both go in (warp to the house's 1F, reserving its moving-in scene, script 20).
    // Boy: Brendan's house door Sapphire (5,8) = (173,360); girl: May's house door (14,8) = (182,360).
    ActorsPauseAll
    TrainerCardGetSex 0x8010
    WorkSetConst 0x8004, 173
    VMStackPush 0x8010
    VMStackPushConst 0
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_DoorGirl
    VMJump L_DoorSet
L_DoorGirl:
    WorkSetConst 0x8004, 182
L_DoorSet:
    WorkSetConst 0x8005, 360
    FadeInBlack
    FadeWait
    VMSleep 8                                      // Sapphire delay 15 (Gen 3 frames; the field runs at 30 fps)
    SEPlay SEQ_SE_DANSA
    ActorCmdExec 255, Movement_PlayerStepOffTruck
    ActorCmdWait
    BMCreateHandleByGPos 0x8020, 1, 0x8004, 0x8005  // the house's door model (Black 2 door 164)
    BMHndAudioVisualAnmPlay 0x8020, 0               // open
    BMHndAnmWait 0x8020
    ActorNew 0x8004, 0x8005, 1, 251, 251, 0         // Mom (sprite 251) in the doorway, facing down
    ActorCmdExec 251, Movement_MomExitHouse
    ActorCmdWait
    BMHndAudioVisualAnmPlay 0x8020, 1               // close
    BMHndAnmWait 0x8020
    VMSleep 5                                       // Sapphire delay 10
    ActorCmdExec 251, Movement_MomApproachPlayerAtTruck
    ActorCmdWait
    WordSetPlayerName 0
    ActorMsg MSGFILE_SCRIPT, 7, 251, 0, 0           // "Mom: <player>, we're here, honey! ... Let's go inside."
    LastKeyWait
    MsgWinCloseAll
    ActorCmdExec 251, Movement_MomApproachDoor
    ActorCmdExec 255, Movement_PlayerApproachDoor
    ActorCmdWait
    BMHndAudioVisualAnmPlay 0x8020, 0
    BMHndAnmWait 0x8020
    ActorCmdExec 251, Movement_MomEnterHouse
    ActorCmdExec 255, Movement_PlayerEnterHouse
    ActorCmdWait
    ActorDelete 251
    FlagSet FLAG_HIDE_MOM_LITTLEROOT
    WorkSetConst VAR_LITTLEROOT_INTRO_STATE, 3
    BMHndAudioVisualAnmPlay 0x8020, 1
    BMHndAnmWait 0x8020
    BMReleaseHandle 0x8020
    FlagReset FLAG_HIDE_MAP_NAME_POPUP
    FlagReset FLAG_HIDE_FAT_MAN_LITTLEROOT
    FadeOutBlack
    RTReserveScript 20                              // the house's moving-in scene (scenes/players_house_1f.inc)
    FadeWait
    VMStackPush 0x8010
    VMStackPushConst 0
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_IntoMaysHouse
    FlagSet FLAG_HIDE_MOVING_TRUCK_BRENDAN          // the truck leaves (its object's spawn flag)
    MapChangeCore 390, 9, 0, 8, 0                   // Brendan's house 1F, Sapphire (8,8) (interior offset +1,+0)
    VMJump L_IntoHouseDone
L_IntoMaysHouse:
    FlagSet FLAG_HIDE_MOVING_TRUCK_MAY
    MapChangeCore 392, 3, 0, 8, 0                   // May's house 1F, Sapphire (2,8)
L_IntoHouseDone:
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

    .balign 4, 0                                   // movement lists are read as words (Black 2 aligns them too)
Movement_PlayerStepOffTruck:                       // jump_right, delay_16 x3 (48 Gen 3 frames = 24 field frames)
    Move 55, 1
    Move 63, 3
    MoveEnd

Movement_MomExitHouse:
    Move 13, 1
    MoveEnd

Movement_MomApproachPlayerAtTruck:                 // walk_down, face left
    Move 13, 1
    Move 2, 1
    MoveEnd

Movement_MomApproachDoor:                          // delay_16, delay_8, walk_up
    Move 63, 1
    Move 62, 1
    Move 12, 1
    MoveEnd

Movement_MomEnterHouse:                            // walk_up, set_invisible
    Move 12, 1
    Move 69, 1
    MoveEnd

Movement_PlayerApproachDoor:                       // delay_16, delay_8, walk_right, face up
    Move 63, 1
    Move 62, 1
    Move 15, 1
    Move 0, 1
    MoveEnd

Movement_PlayerEnterHouse:                         // walk_up x2, set_invisible (Sapphire hides the player)
    Move 12, 2
    Move 69, 1
    MoveEnd

Movement_TwinApproachPlayerLeft:                // face_right, delay_8, jump_in_place_right, delay_8, walk right x4, up x2, left, face_down
                                                // (Sapphire walks fast; Black 2's fast-walk codes are not settled yet)
    Move 3, 1
    Move 62, 1
    Move 51, 1
    Move 62, 1
    Move 15, 4
    Move 12, 2
    Move 14, 1
    Move 1, 1
    MoveEnd

Movement_TwinReturnLeft:
    Move 15, 1
    Move 13, 2
    Move 14, 4
    Move 12, 1
    Move 1, 1
    MoveEnd

Movement_TwinApproachPlayerRight:
    Move 3, 1
    Move 62, 1
    Move 51, 1
    Move 62, 1
    Move 15, 3
    Move 12, 2
    Move 15, 1
    Move 1, 1
    MoveEnd

Movement_TwinReturnRight:
    Move 14, 1
    Move 13, 1
    Move 14, 3
    Move 1, 1
    MoveEnd

Movement_TwinPushPlayerFromRoute:
    Move 13, 1
    MoveEnd

Movement_PushPlayerBackFromRoute:               // lock_facing_direction, walk_down, unlock_facing_direction
    Move 71, 1
    Move 13, 1
    Move 72, 1
    MoveEnd

Movement_FaceRight:
    Move 3, 1
    MoveEnd

Movement_FaceLeft:
    Move 2, 1
    MoveEnd

Movement_FaceDown:
    Move 1, 1
    MoveEnd

#ifdef HOENN_TEST_SPRITES
Movement_TestSpriteLoop:                        // test only: down, right x2, up, left x2 (every walking direction)
    Move 13, 1
    Move 15, 2
    Move 12, 1
    Move 14, 2
    Move 1, 1
    MoveEnd
#endif

#ifdef HOENN_TEST_MOVES
// Test only: the movement probe of Script_2 (see there). The player starts on (175,361) facing the sign.
Sub_TestMoves:
    ActorCmdExec 255, Mv_TestStart
    ActorCmdWait
    VMSleep 30
    ActorCmdExec 255, Mv_TestWalks
    ActorCmdWait
    VMSleep 30
    ActorCmdExec 255, Mv_TestJumps
    ActorCmdWait
    VMSleep 30
    ActorCmdExec 255, Mv_TestInPlace
    ActorCmdWait
    VMSleep 30
    ActorCmdExec 255, Mv_TestDelay
    ActorCmdWait
    VMSleep 30
    ActorCmdExec 255, Mv_TestEmote75
    ActorCmdWait
    VMSleep 30
    ActorCmdExec 255, Mv_TestEmote159
    ActorCmdWait
    VMSleep 30
    ActorCmdExec 255, Mv_TestEmote160
    ActorCmdWait
    VMSleep 30
    ActorCmdExec 255, Mv_TestEmote161
    ActorCmdWait
    VMSleep 30
    ActorCmdExec 255, Mv_TestEmote103
    ActorCmdWait
    VMReturn

    .balign 4, 0
Mv_TestStart:                   // face down (the row in front of the houses, 361, is open from 175 to 182)
    Move 1, 1
    MoveEnd
Mv_TestWalks:                   // fast x2, normal, fastest, slow (right)
    Move 19, 2
    Move 15, 1
    Move 23, 1
    Move 11, 1
    MoveEnd
Mv_TestJumps:                   // 58 (jump 2 left?), 54 (jump 1 left), 95 (jump 3 right?)
    Move 58, 1
    Move 54, 1
    Move 95, 1
    MoveEnd
Mv_TestInPlace:                 // left, 4 x walk-in-place (TURN8 left), left, 4 x TURN2 left, left
    Move 14, 1
    Move 34, 4
    Move 14, 1
    Move 42, 4
    Move 14, 1
    MoveEnd
Mv_TestDelay:                   // right, 10 x code 63, right
    Move 15, 1
    Move 63, 10
    Move 15, 1
    MoveEnd
Mv_TestEmote75:
    Move 75, 1
    MoveEnd
Mv_TestEmote159:
    Move 159, 1
    MoveEnd
Mv_TestEmote160:
    Move 160, 1
    MoveEnd
Mv_TestEmote161:
    Move 161, 1
    MoveEnd
Mv_TestEmote103:
    Move 103, 1
    MoveEnd
#endif
#include "scenes/LittlerootTown_ch1.inc"         // chapter Ch1: scripts 10-16 (Running Shoes), its zone-init part
#if __has_include("scenes/LittlerootTown_ch13.inc")
#include "scenes/LittlerootTown_ch13.inc"        // chapter Ch13: house states after the S.S. Ticket, Script_25 (dex upgrade state)
#endif
#if __has_include("scenes/LittlerootTown_Postgame.inc")
#include "scenes/LittlerootTown_Postgame.inc"    // post-game: the National Dex scene (Script_26, PG_LittlerootInit)
#endif
#include "common/movement.inc"
#ifdef HOENN_TEST_CHCREDITS
#include "scenes/halloffame_test.inc"
#endif
#ifdef HOENN_TEST_COMMON
#include "common/briney.inc"
#endif
#ifdef HOENN_TEST_CHBOATS
#include "common/boat_test.inc"
#endif
#ifdef HOENN_TEST_CHMO
#include "scenes/missing_objects_test.inc"
#endif
#ifdef HOENN_TEST_CHSC
#include "scenes/script_check_test.inc"
#endif
#ifdef HOENN_TEST_CHFA
#include "scenes/fairy_test.inc"
#endif
#ifdef HOENN_TEST_CHTM
#if __has_include("scenes/town_map_test.inc")
#include "scenes/town_map_test.inc"
#endif
#endif
