// Petalburg Gym: chapter Ch6's beats (Sapphire data/maps/PetalburgCity_Gym/scripts.inc from
// PetalburgCity_Gym_EventScript_NormanPostBattle to the end, and OnLoad: the Norman battle and the Balance Badge,
// Facade, the rooms' doors, the seven trainers, the guide, the statues). Included twice by chapter Ch1's room file
// 0904_room_PetalburgCity_Gym.s: the entries between `#ifdef SCENE_ENTRIES` and `#else` are scripts 4.. of the room,
// the bodies after `#else`. Dad's script (Ch1's Script_1: lock, faceplayer, player name buffered) jumps to
// Ch6_NormanBattle (VAR_PETALBURG_GYM_STATE 6) / Ch6_NormanPostBattle (7); the zone init (Ch1's Script_2) calls
// Ch6_PG_Init. Text: src/text/script/0187_room_PetalburgCity_Gym.txt lines 16-51 (Ch1's are 0-15).
// Objects (data/story/ch6.json, uid = Sapphire local id): Mary 2, Randall 3, Parker 4, Lori 5, George 6, Jody 7,
// Berke 8, the guide 9; the statue signs; a sign on each of the 12 room doors; a step trigger on each room's back exit.
// Room tiles = Sapphire tiles + (1, 0).
//
// Black 2 differences (chapter Ch6, 2026-10-07):
// - The doors: Sapphire's door tiles are signs ("Speed Room," the sign says. Do you want to go through?) that
//   warpdoor to the next room once the room's trainer is beaten; walking into a door does nothing. The room
//   (gyms_league) has a walk-in warp on each door (every door open): the zone init moves those 12 warps off the map
//   (ObjInitWarpGPos, as the Shoal Cave tides) and the signs do Sapphire's script (fade + MapChangeCore inside the
//   zone). Sapphire's sliding-door animation (PetalburgGymSlideOpenDoors) is left out: the door models stay shut.
// - The back exits (Sapphire: the RoomEntrance tiles become south arrow warps when the doors open): the room's
//   warps there only mark arrivals, so a step trigger on each pair of tiles sends you back to the room you came from
//   when you step onto it walking south and its door is open (Sapphire: press south while standing on it).
// - Enigma Berry (e-Reader, IsEnigmaBerryValid): left out, as Black 2 has no e-Reader (always "not valid").
#ifdef SCENE_ENTRIES
    ScriptEntry Ch6_PG_Mary         // 4: Mary (object 2, Accuracy Room)
    ScriptEntry Ch6_PG_Randall      // 5: Randall (object 3, Speed Room)
    ScriptEntry Ch6_PG_Parker       // 6: Parker (object 4)
    ScriptEntry Ch6_PG_Lori         // 7: Lori (object 5)
    ScriptEntry Ch6_PG_George       // 8: George (object 6)
    ScriptEntry Ch6_PG_Jody         // 9: Jody (object 7)
    ScriptEntry Ch6_PG_Berke        // 10: Berke (object 8)
    ScriptEntry Ch6_PG_GymGuide     // 11: Gym guide (object 9)
    ScriptEntry Ch6_PG_Statue       // 12: statues (1,110) / (7,110)
    ScriptEntry Ch6_PG_DoorSpeed    // 13: door (1,105) SpeedRoomDoor
    ScriptEntry Ch6_PG_DoorAccuracy // 14: door (7,105) AccuracyRoomDoor
    ScriptEntry Ch6_PG_DoorZeroRed  // 15: door (1,79) ZeroReductionRoomDoor
    ScriptEntry Ch6_PG_DoorDefenseL // 16: door (7,79) LeftDefenseRoomDoor
    ScriptEntry Ch6_PG_DoorDefenseR // 17: door (1,92) RightDefenseRoomDoor
    ScriptEntry Ch6_PG_DoorRecovery // 18: door (7,92) RecoveryRoomDoor
    ScriptEntry Ch6_PG_DoorStrengthL // 19: door (7,40) LeftStrengthRoomDoor
    ScriptEntry Ch6_PG_DoorStrengthR // 20: door (1,53) RightStrengthRoomDoor
    ScriptEntry Ch6_PG_DoorOHKOL    // 21: door (7,53) LeftOHKORoomDoor
    ScriptEntry Ch6_PG_DoorOHKOR    // 22: door (1,66) RightOHKORoomDoor
    ScriptEntry Ch6_PG_DoorLeadersL // 23: door (7,14) LeftGymLeadersRoomDoor
    ScriptEntry Ch6_PG_DoorLeadersR // 24: door (1,27) RightGymLeadersRoomDoor
    ScriptEntry Ch6_PG_BackSpeed    // 25: back exit (6-7,85) -> in front of door (1,105)
    ScriptEntry Ch6_PG_BackAccuracy // 26: back exit (1-2,98) -> (7,105)
    ScriptEntry Ch6_PG_BackZeroRed  // 27: back exit (6-7,46) -> (1,79)
    ScriptEntry Ch6_PG_BackDefenseL // 28: back exit (1-2,59) -> (7,79)
    ScriptEntry Ch6_PG_BackDefenseR // 29: back exit (6-7,59) -> (1,92)
    ScriptEntry Ch6_PG_BackRecovery // 30: back exit (1-2,72) -> (7,92)
    ScriptEntry Ch6_PG_BackStrengthL // 31: back exit (1-2,20) -> (7,40)
    ScriptEntry Ch6_PG_BackStrengthR // 32: back exit (6-7,20) -> (1,53)
    ScriptEntry Ch6_PG_BackOHKOL    // 33: back exit (1-2,33) -> (7,53)
    ScriptEntry Ch6_PG_BackOHKOR    // 34: back exit (6-7,33) -> (1,66)
    ScriptEntry Ch6_PG_BackLeadersL // 35: back exit (1-2,7) -> (7,14)
    ScriptEntry Ch6_PG_BackLeadersR // 36: back exit (6-7,7) -> (1,27)
#ifdef HOENN_TEST_CH6
    ScriptEntry Test_TeleWattson    // 37: TEST ONLY (HOENN_TEST_CH6): the teleport signs of work/agents/ch6/test_story.json
    ScriptEntry Test_TeleMom        // 38
    ScriptEntry Test_TeleStern      // 39
    ScriptEntry Test_TeleNMEntrance // 40
    ScriptEntry Test_TeleShipDeck   // 41
    ScriptEntry Test_TeleSealed     // 42
    ScriptEntry Test_TeleDesert     // 43
    ScriptEntry Test_TeleIsland     // 44
    ScriptEntry Test_TeleTomb       // 45
    ScriptEntry Test_TelePacifidlog // 46
#endif
#else
#include "hoenn_key_items.h"

#define PGT_NormanIntro 16
#define PGT_ReceivedBadge 17
#define PGT_ExplainBadge 18
#define PGT_ExplainFacade 19
#define PGT_HappySad 20
#define PGT_WallysParents 21
#define PGT_KeepTraining 22
#define PGT_NoAmount 23
#define PGT_GuideAdvice 24
#define PGT_GuideVictory 25
#define PGT_RandallPost 26
#define PGT_RandallBadge 27
#define PGT_ParkerPost 28
#define PGT_ParkerBadge 29
#define PGT_GeorgePost 30
#define PGT_GeorgeBadge 31
#define PGT_BerkePost 32
#define PGT_BerkeBadge 33
#define PGT_MaryPost 34
#define PGT_MaryBadge 35
#define PGT_LoriPost 36
#define PGT_LoriBadge 37
#define PGT_JodyPost 38
#define PGT_JodyBadge 39
#define PGT_Locked 40
#define PGT_Speed 41
#define PGT_Accuracy 42
#define PGT_ZeroRed 43
#define PGT_Defense 44
#define PGT_Recovery 45
#define PGT_Strength 46
#define PGT_OHKO 47
#define PGT_Leaders 48
#define PGT_Statue 49
#define PGT_StatueCert 50
#define PGT_BagFull 51
#define PG_ZONE 452
#define PGX(x) ((x) + 1)                            /* Sapphire x -> room tile */

// ---- zone init (called by Ch1's Script_2): the 12 door warps leave the map (the signs open the doors) ----------
Ch6_PG_Init:
#ifdef HOENN_TEST_CH6
    VMCall Test_Ch6Start                            // test builds only (scenes/ch6_test.inc)
#endif
    ObjInitWarpGPos 2, 0, 0, 0                      // (1,105) -> warp 3
    ObjInitWarpGPos 5, 0, 0, 0                      // (7,105)
    ObjInitWarpGPos 8, 0, 0, 0                      // (1,79)
    ObjInitWarpGPos 9, 0, 0, 0                      // (7,79)
    ObjInitWarpGPos 14, 0, 0, 0                     // (1,92)
    ObjInitWarpGPos 15, 0, 0, 0                     // (7,92)
    ObjInitWarpGPos 20, 0, 0, 0                     // (7,40)
    ObjInitWarpGPos 21, 0, 0, 0                     // (1,53)
    ObjInitWarpGPos 22, 0, 0, 0                     // (7,53)
    ObjInitWarpGPos 23, 0, 0, 0                     // (1,66)
    ObjInitWarpGPos 32, 0, 0, 0                     // (7,14)
    ObjInitWarpGPos 33, 0, 0, 0                     // (1,27)
    VMReturn

// ---- Norman ----------------------------------------------------------------------------------------------------
Ch6_NormanBattle:                                   // PetalburgCity_Gym_EventScript_NormanBattle
    h_msgbox PGT_NormanIntro                        // Dad: Hm... So, you did get four Gym Badges. ...
    h_closemessage
    h_trainerbattle TRAINER_NORMAN                  // (in battle: "... I lost to <player>? But, rules are rules!")
    h_buffer_player
    SystemMsg PGT_ReceivedBadge, 2                  // <player> received the Balance Badge from Dad!
    h_badge_fanfare
    LastKeyWait
    MsgWinCloseAll
    h_msgbox_actor PGT_ExplainBadge, 1              // Dad: With that Badge, the Defense of all your Pokémon ...
    h_closemessage
    h_setflag FLAG_DEFEATED_PETALBURG_GYM
    h_setvar VAR_PETALBURG_GYM_STATE, 7
    h_givebadge 5                                   // setflag FLAG_BADGE05_GET
    VMCall Sub_HideMrBriney                         // EventScript_HideMrBriney
    h_setflag FLAG_HIDE_WATTSON_MAUVILLE_GYM
    h_clearflag FLAG_HIDE_WATTSON_MAUVILLE
    h_set_gym_trainers 5                            // Common_EventScript_SetGymTrainers (VAR_0x8008 5)
    h_clearflag FLAG_HIDE_SLUDGE_BOMB_MAN_DEWFORD_HALL
    // PetalburgCity_Gym_EventScript_UnlockAllDoors: the doors read the trainers' flags, all set now
#ifdef HOENN_EMERALD
    VMJump L_Em_GiveFacadeBattle                    // Emerald: Facade, then Wally's father takes the player home (scenes/emerald/PetalburgCity_Gym_ch6.inc)
#else
    VMJump L_Ch6_GiveFacade
#endif

Ch6_NormanPostBattle:                               // PetalburgCity_Gym_EventScript_NormanPostBattle
    // (ShouldGiveEnigmaBerry: no e-Reader in Black 2; the post-game gives it after the Hall of Fame instead)
#if __has_include("scenes/PetalburgCity_Gym_Postgame.inc")
#include "scenes/PetalburgCity_Gym_Postgame.inc"
#endif
    h_goto_if_unset FLAG_RECEIVED_TM42, L_Ch6_GiveFacade
    em_gym_rematch TRAINER_NORMAN, 1                // Emerald: after the Hall of Fame, a rematch (hoenn_rematch.inc; Dad is uid 1)
    h_goto_if_set FLAG_SYS_GAME_CLEAR, L_Ch6_NoAmountOfTraining
    h_msgbox PGT_KeepTraining                       // Dad: <player>, you should go visit your mother ...
    h_release
L_Ch6_NoAmountOfTraining:
    h_msgbox PGT_NoAmount                           // Dad: <player>, how are things going? ...
    h_release

L_Ch6_GiveFacade:                                   // PetalburgCity_Gym_EventScript_GiveFacade2
#ifdef HOENN_EMERALD
    VMJump L_Em_GiveFacadeLate
#endif
    h_giveitem ITEM_TM42
    h_goto_if_eq HLIB_RESULT, 0, L_Ch6_BagFull
    h_setflag FLAG_RECEIVED_TM42
    h_buffer_player
    h_msgbox_actor PGT_ExplainFacade, 1             // Dad: TM42 contains Facade. ...
    h_msgbox_actor PGT_HappySad, 1                  // Dad: As the Gym Leader, I can't express how upset I am...
    h_closemessage
    h_getplayerfacing 0x8008                        // Dad turns away (the way the player faces), then back
    h_goto_if_eq 0x8008, 0, L_Ch6_DadTurnUp
    h_goto_if_eq 0x8008, 1, L_Ch6_DadTurnDown
    h_goto_if_eq 0x8008, 2, L_Ch6_DadTurnLeft
    h_applymovement 1, Common_Movement_WalkInPlaceFastestRight
    h_waitmovement
    h_delay 70
    h_applymovement 1, Common_Movement_WalkInPlaceFastestLeft
    VMJump L_Ch6_DadTurned
L_Ch6_DadTurnUp:
    h_applymovement 1, Common_Movement_WalkInPlaceFastestUp
    h_waitmovement
    h_delay 70
    h_applymovement 1, Common_Movement_WalkInPlaceFastestDown
    VMJump L_Ch6_DadTurned
L_Ch6_DadTurnDown:
    h_applymovement 1, Common_Movement_WalkInPlaceFastestDown
    h_waitmovement
    h_delay 70
    h_applymovement 1, Common_Movement_WalkInPlaceFastestUp
    VMJump L_Ch6_DadTurned
L_Ch6_DadTurnLeft:
    h_applymovement 1, Common_Movement_WalkInPlaceFastestLeft
    h_waitmovement
    h_delay 70
    h_applymovement 1, Common_Movement_WalkInPlaceFastestRight
L_Ch6_DadTurned:
    h_waitmovement
    h_buffer_player
    h_msgbox_actor PGT_WallysParents, 1             // Dad: Oh, yes... Wally's parents came calling earlier. ...
    h_release
L_Ch6_BagFull:                                      // Common_EventScript_ShowBagIsFull
    h_bag_is_full PGT_BagFull
    h_release

// ---- the gym trainers (sight 0: they battle when talked to; trainerbattle_single + the room's doors) ----------
    .macro pg_trainer trainer, uid, post, badge
    h_lock
    SEPlay SEQ_SE_MESSAGE
    h_faceplayer
    h_goto_if_defeated \trainer, .Lpgt_after\@
    h_trainer_intro \trainer, \uid                  // the trainer's music and intro line
    h_trainerbattle \trainer                        // (in battle: the defeat line)
    h_release                                       // SlideOpen...Doors: the next doors now open (their signs)
.Lpgt_after\@:
    h_goto_if_set FLAG_DEFEATED_PETALBURG_GYM, .Lpgt_badge\@
    h_buffer_player
    h_msgbox_autoclose \post
    h_release
.Lpgt_badge\@:
    h_msgbox \badge
    h_release
    .endm

Ch6_PG_Mary:
    pg_trainer TRAINER_MARY, 2, PGT_MaryPost, PGT_MaryBadge
Ch6_PG_Randall:
    pg_trainer TRAINER_RANDALL, 3, PGT_RandallPost, PGT_RandallBadge
Ch6_PG_Parker:
    pg_trainer TRAINER_PARKER, 4, PGT_ParkerPost, PGT_ParkerBadge
Ch6_PG_Lori:
    pg_trainer TRAINER_LORI, 5, PGT_LoriPost, PGT_LoriBadge
Ch6_PG_George:
    pg_trainer TRAINER_GEORGE, 6, PGT_GeorgePost, PGT_GeorgeBadge
Ch6_PG_Jody:
    pg_trainer TRAINER_JODY, 7, PGT_JodyPost, PGT_JodyBadge
Ch6_PG_Berke:
    pg_trainer TRAINER_BERKE, 8, PGT_BerkePost, PGT_BerkeBadge

Ch6_PG_GymGuide:                                    // PetalburgCity_Gym_EventScript_GymGuide
    h_lock
    SEPlay SEQ_SE_MESSAGE
    h_faceplayer
    h_buffer_player
    h_goto_if_set FLAG_DEFEATED_PETALBURG_GYM, L_Ch6_GuideVictory
    h_msgbox PGT_GuideAdvice                        // Hey, how's it going, Champion-bound <player>? ...
    h_release
L_Ch6_GuideVictory:
    h_msgbox PGT_GuideVictory                       // <player>! Whoa! You've overcome even your own father! ...
    h_release

Ch6_PG_Statue:                                      // Left/RightGymStatue (lockall; MSGBOX_DEFAULT)
    h_lock
    SEPlay SEQ_SE_MESSAGE
    h_goto_if_badge 5, L_Ch6_StatueCertified
    h_msgbox_info PGT_Statue                        // Petalburg City Pokémon Gym
    h_closemessage
    h_release
L_Ch6_StatueCertified:
    h_buffer_player
    h_msgbox_info PGT_StatueCert                    // ... Norman's Certified Trainers: <player>
    h_closemessage
    h_release

// ---- the doors: lock check, "... the sign says. Do you want to go through?", warpdoor to (x, z) of the zone ----
    .macro pg_door_go text, x, z
    SystemMsg \text, 2
    YesNoWin 0x8008
    h_goto_if_no 0x8008, L_Ch6_DoorNo
    MsgWinCloseAll
    h_delay 30
    SEPlay SE_EXIT
    FadeOutBlack
    FadeWait
    MapChangeCore PG_ZONE, PGX(\x), 0, (\z) - 1, 0  // warpdoor MAP_PETALBURG_CITY_GYM, 255, x, z: one tile north of Sapphire's
    // arrival (as Black 2's doors), so walking back south onto the entrance tiles fires the back exit (Discord 2026-10-14:
    // arriving ON the trigger tile, pressing south hit the wall and the doors seemed one-way)
    FadeInBlack
    FadeWait
    h_release
    .endm
    .macro pg_door_state text, x, z                 // locked until VAR_PETALBURG_GYM_STATE 6 (four Badges)
    h_lock
    SEPlay SEQ_SE_MESSAGE
    h_goto_if_lt VAR_PETALBURG_GYM_STATE, 6, L_Ch6_DoorLocked
    pg_door_go \text, \x, \z
    .endm
    .macro pg_door_trainer trainer, text, x, z      // locked until the room's trainer is beaten
    h_lock
    SEPlay SEQ_SE_MESSAGE
    h_goto_if_not_defeated \trainer, L_Ch6_DoorLocked
    pg_door_go \text, \x, \z
    .endm

Ch6_PG_DoorSpeed:
    pg_door_state PGT_Speed, 7, 85
Ch6_PG_DoorAccuracy:
    pg_door_state PGT_Accuracy, 1, 98
Ch6_PG_DoorZeroRed:
    pg_door_trainer TRAINER_RANDALL, PGT_ZeroRed, 7, 46
Ch6_PG_DoorDefenseL:
    pg_door_trainer TRAINER_RANDALL, PGT_Defense, 1, 59
Ch6_PG_DoorDefenseR:
    pg_door_trainer TRAINER_MARY, PGT_Defense, 7, 59
Ch6_PG_DoorRecovery:
    pg_door_trainer TRAINER_MARY, PGT_Recovery, 1, 72
Ch6_PG_DoorStrengthL:
    pg_door_trainer TRAINER_PARKER, PGT_Strength, 1, 20
Ch6_PG_DoorStrengthR:
    pg_door_trainer TRAINER_LORI, PGT_Strength, 7, 20
Ch6_PG_DoorOHKOL:
    pg_door_trainer TRAINER_LORI, PGT_OHKO, 1, 33
Ch6_PG_DoorOHKOR:
    pg_door_trainer TRAINER_GEORGE, PGT_OHKO, 7, 33
Ch6_PG_DoorLeadersL:
    pg_door_trainer TRAINER_JODY, PGT_Leaders, 1, 7
Ch6_PG_DoorLeadersR:
    pg_door_trainer TRAINER_BERKE, PGT_Leaders, 7, 7

L_Ch6_DoorLocked:                                   // PetalburgCity_Gym_EventScript_DoorLocked
    h_msgbox_info PGT_Locked                        // This door appears to be locked right now...
    h_closemessage
    h_release
L_Ch6_DoorNo:                                       // DontEnterRoom
    h_closemessage
    h_release

// ---- the back exits: walking south onto a room's entrance tiles returns through its (open) door ----------------
    .macro pg_back_go x, z
    h_getplayerfacing 0x8008
    h_goto_if_ne 0x8008, 1, L_Ch6_BackNone
    h_lock
    SEPlay SE_EXIT
    FadeOutBlack
    FadeWait
    MapChangeCore PG_ZONE, PGX(\x), 0, (\z) + 1, 1  // out of the door (x, z), one step south, facing south
    FadeInBlack
    FadeWait
    h_release
    .endm
    .macro pg_back_state x, z
    h_goto_if_lt VAR_PETALBURG_GYM_STATE, 6, L_Ch6_BackNone
    pg_back_go \x, \z
    .endm
    .macro pg_back_trainer trainer, x, z
    h_goto_if_not_defeated \trainer, L_Ch6_BackNone
    pg_back_go \x, \z
    .endm

Ch6_PG_BackSpeed:
    pg_back_state 1, 105
Ch6_PG_BackAccuracy:
    pg_back_state 7, 105
Ch6_PG_BackZeroRed:
    pg_back_trainer TRAINER_RANDALL, 1, 79
Ch6_PG_BackDefenseL:
    pg_back_trainer TRAINER_RANDALL, 7, 79
Ch6_PG_BackDefenseR:
    pg_back_trainer TRAINER_MARY, 1, 92
Ch6_PG_BackRecovery:
    pg_back_trainer TRAINER_MARY, 7, 92
Ch6_PG_BackStrengthL:
    pg_back_trainer TRAINER_PARKER, 7, 40
Ch6_PG_BackStrengthR:
    pg_back_trainer TRAINER_LORI, 1, 53
Ch6_PG_BackOHKOL:
    pg_back_trainer TRAINER_LORI, 7, 53
Ch6_PG_BackOHKOR:
    pg_back_trainer TRAINER_GEORGE, 1, 66
Ch6_PG_BackLeadersL:
    pg_back_trainer TRAINER_JODY, 7, 14
Ch6_PG_BackLeadersR:
    pg_back_trainer TRAINER_BERKE, 1, 27
L_Ch6_BackNone:
    VMHalt

#ifdef HOENN_TEST_CH6
// TEST ONLY: signs in the Gym's entrance hall (data in work/agents/ch6/test_story.json, HOENN_EXTRA_STORY) warp to the
// places where chapter Ch6's other beats stand, so one test ROM reaches all of them with the test start's flags set.
    .macro test_tele zone, x, z, dir
    ActorsPauseAll
    FadeOutBlack
    FadeWait
    MapChangeCore \zone, \x, 0, \z, \dir        // (as Black 2's own warps: fade out, change, fade in, then the events go on)
    FadeInBlack
    FadeWait
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt
    .endm
Test_TeleWattson:
    test_tele 239, 5, 19, 1                     // the Mauville Gym's hall: leave by its door (talking works only after a real warp)
Test_TeleMom:
    test_tele 390, 3, 6, 2
Test_TeleStern:
    test_tele 596, 7, 13, 0
Test_TeleNMEntrance:
#if (HOENN_TEST_CH6 + 0) >= 5
    test_tele 133, 45, 19, 1                    // stage 5: inside, below the generator's switch (Sapphire (33,7))
#else
    test_tele 132, 4, 5, 0
#endif
Test_TeleShipDeck:
#if (HOENN_TEST_CH6 + 0) >= 7
    test_tele 173, 4, 9, 0                      // stage 7: the hidden floor's corridor, in front of room 1's door
#elif (HOENN_TEST_CH6 + 0) >= 6
    test_tele 73, 12, 5, 0                      // stage 6: Corridors B1F, in front of the Storage Room's door
#else
    test_tele 71, 4, 6, 0                       // the Captain's office, in front of Stern's aide (the deck has three levels: y)
#endif
Test_TeleSealed:
    test_tele 215, 8, 6, 0                      // in the corridor below the Dig spot (the dive arrival (10,19) is in the pool)
Test_TeleDesert:
    test_tele 116, 8, 28, 0
Test_TeleIsland:
    test_tele 127, 8, 28, 0
Test_TeleTomb:
    test_tele 94, 8, 28, 0
Test_TelePacifidlog:
    test_tele 458, 536, 336, 1
#endif
#include "scenes/ch6_test.inc"
#include "common/briney.inc"
#ifdef HOENN_EMERALD
#include "scenes/emerald/PetalburgCity_Gym_ch6.inc"     // Emerald (emerald_ch0_3): Wally's father takes the player to his house
#endif
#endif
