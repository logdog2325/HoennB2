// PetalburgCity_Gym (zone 452, big room by the gyms_league agent): story scripts, chapter Ch1 (Sapphire
// data/maps/PetalburgCity_Gym/scripts.inc up to PetalburgCity_Gym_EventScript_NormanPostBattle): meeting Dad, Wally's
// arrival, the walk out for Wally's tutorial, the return, Dad's lines before the Balance Badge. The Norman battle,
// Facade, the gym rooms' doors, the seven trainers, the guide and the statues are chapter Ch6's beats: its scripts
// come from scenes/PetalburgCity_Gym_ch6.inc (entries from 4 on, labels Ch6_NormanBattle / Ch6_NormanPostBattle).
// Messages: src/text/script/0187_room_PetalburgCity_Gym.txt (lines 0-15 Ch1's). Map scripts: 0905.
// Room tiles = Sapphire tiles + (1, 0) (room.json origin). People (data/story/ch1.json, uid = Sapphire local id,
// the room's first NPCs): Dad (uid 1, index 0), Wally (uid 10, index 1).
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_trainers.h"
#include "hoenn_story.inc"

    ScriptEntry Script_1    // Dad (PetalburgCity_Gym_EventScript_Norman)
    ScriptEntry Script_2    // zone init (PetalburgCity_Gym_OnTransition)
    ScriptEntry Script_3    // OnFrame VAR_PETALBURG_GYM_STATE 1: PetalburgCity_Gym_EventScript_ReturnFromWallyTutorial
#define SCENE_ENTRIES
#include "scenes/PetalburgCity_Gym_ch6.inc"
#undef SCENE_ENTRIES
    ScriptEntriesEnd

#define PG_NORMAN 1
#define PG_WALLY 10
#define PG_NORMAN_INDEX 0
#define PG_WALLY_INDEX 1
#ifndef SE_DOOR
#define SE_DOOR SE_EXIT             /* [guess] Black 2 has no separate door sound (its door models play their own) */
#endif

Script_2:                                        // PetalburgCity_Gym_OnTransition
    h_goto_if_ne VAR_PETALBURG_GYM_STATE, 1, L_PG_InitWallyDone
    ObjInitNPCGPos PG_WALLY_INDEX, 0, 6, 0, 108     // Wally back from the tutorial: (5,108)
L_PG_InitWallyDone:
    h_goto_if_ge VAR_PETALBURG_GYM_STATE, 6, L_PG_InitNormanClear
    ObjInitNPCGPos PG_NORMAN_INDEX, 1, 5, 0, 107    // Dad at the entrance (4,107) until you have four Badges
L_PG_InitNormanClear:
    h_goto_if_unset FLAG_SYS_GAME_CLEAR, L_PG_InitDone
    ObjInitNPCGPos PG_NORMAN_INDEX, 1, 5, 0, 107
L_PG_InitDone:
    VMCall Ch6_PG_Init                           // chapter Ch6's part (scenes/PetalburgCity_Gym_ch6.inc: the doors' warps)
    VMHalt

Script_3:                                       // PetalburgCity_Gym_EventScript_ReturnFromWallyTutorial
    h_lock
    FadeInBlack                                  // (Petalburg's scripted warp leaves the screen black)
    FadeWait
    h_msgbox_actor 0, PG_NORMAN                  // Dad: So, did it work out?
    h_buffer_player
    h_msgbox_actor 1, PG_WALLY                   // Wally: Thank you, yes, it did. ... Bye, <player>!
    h_closemessage
    h_applymovement 255, Common_Movement_WalkInPlaceFastestDown
    h_applymovement PG_WALLY, Mv_PG_WallyExitGym
    h_waitmovement
    h_playse SE_EXIT
    h_removeobject PG_WALLY, FLAG_HIDE_WALLY_PETALBURG_GYM
    h_setflag FLAG_HIDE_WALLY_PETALBURG
    h_delay 30
    h_applymovement 255, Common_Movement_WalkInPlaceFastestUp
    h_waitmovement
    h_buffer_player
    h_msgbox_actor 2, PG_NORMAN                  // Dad: Now... <player>, if you want to become a strong Trainer ...
    h_setvar VAR_PETALBURG_GYM_STATE, 2
    h_release

Script_1:                                        // PetalburgCity_Gym_EventScript_Norman
    h_lock
    SEPlay SEQ_SE_MESSAGE
    h_faceplayer
    h_buffer_player
    h_goto_if_eq VAR_PETALBURG_GYM_STATE, 2, L_PG_NoBadges
    h_goto_if_eq VAR_PETALBURG_GYM_STATE, 3, L_PG_OneBadge
    h_goto_if_eq VAR_PETALBURG_GYM_STATE, 4, L_PG_TwoBadges
    h_goto_if_eq VAR_PETALBURG_GYM_STATE, 5, L_PG_ThreeBadges
    h_goto_if_eq VAR_PETALBURG_GYM_STATE, 6, Ch6_NormanBattle
    h_goto_if_eq VAR_PETALBURG_GYM_STATE, 7, Ch6_NormanPostBattle
    h_msgbox 3                                   // Dad: Hm? Well, if it isn't <player>! ...
    h_closemessage
    h_getplayerfacing 0x8008                     // Sapphire VAR_FACING: S 1 / N 2 / W 3 / E 4 = Black 2 1 / 0 / 2 / 3;
    // L_PG_Tutorial below keeps Black 2's value in 0x8008: 1 = from the north (player faces south), 0 = from the
    // south, 2 = from the east (faces west), 3 = from the west (faces east)
L_PG_Tutorial:                                   // PetalburgCity_Gym_EventScript_BeginWallyTutorial
    h_addobject PG_WALLY, FLAG_HIDE_WALLY_PETALBURG_GYM
    h_playse SE_DOOR
    h_goto_if_eq 0x8008, 0, L_PG_ArriveNorth
    h_goto_if_eq 0x8008, 1, L_PG_ArriveSouth
    h_applymovement PG_NORMAN, Common_Movement_WalkInPlaceFastestDown   // WallyArriveWestEast
    h_applymovement 255, Common_Movement_WalkInPlaceFastestDown
    h_applymovement PG_WALLY, Mv_PG_WallyArrive
    VMJump L_PG_Arrived
L_PG_ArriveSouth:                                // WallyArriveSouth
    h_applymovement PG_NORMAN, Common_Movement_WalkInPlaceFastestDown
    h_applymovement PG_WALLY, Mv_PG_WallyArrive
    VMJump L_PG_Arrived
L_PG_ArriveNorth:                                // WallyArriveNorth
    h_applymovement PG_WALLY, Mv_PG_WallyArriveNorth
    h_waitmovement
    h_applymovement PG_NORMAN, Common_Movement_WalkInPlaceFastestRight
    h_applymovement 255, Common_Movement_WalkInPlaceFastestRight
L_PG_Arrived:
    h_waitmovement
    h_msgbox_actor 4, PG_WALLY                   // Um... I... I'd like to get a Pokémon, please...
    h_msgbox_actor 5, PG_NORMAN                  // Dad: Hm? You're... Uh... Oh, right. You're Wally, right?
    h_msgbox_actor 6, PG_WALLY                   // Wally: I'm going to go stay with my relatives ...
    h_msgbox_actor 7, PG_NORMAN                  // Dad: Hm. I see.
    h_goto_if_eq 0x8008, 1, L_PG_AddressPlayerSouth
    h_goto_if_eq 0x8008, 0, L_PG_AddressPlayerNorth
    h_goto_if_eq 0x8008, 2, L_PG_AddressPlayerWest
    h_applymovement PG_NORMAN, Common_Movement_WalkInPlaceFastestLeft   // NormanAddressPlayerEast
    h_applymovement 255, Common_Movement_WalkInPlaceFastestRight
    VMJump L_PG_AddressedPlayer
L_PG_AddressPlayerSouth:
    h_applymovement PG_NORMAN, Common_Movement_WalkInPlaceFastestUp
    VMJump L_PG_AddressedPlayer
L_PG_AddressPlayerNorth:
    h_applymovement PG_NORMAN, Common_Movement_WalkInPlaceFastestDown
    h_applymovement 255, Common_Movement_WalkInPlaceFastestUp
    VMJump L_PG_AddressedPlayer
L_PG_AddressPlayerWest:
    h_applymovement PG_NORMAN, Common_Movement_WalkInPlaceFastestRight
    h_applymovement 255, Common_Movement_WalkInPlaceFastestLeft
L_PG_AddressedPlayer:
    h_waitmovement
    h_buffer_player
    h_msgbox_actor 8, PG_NORMAN                  // Dad: <player>, you heard that, right? Go with Wally ...
    h_goto_if_eq 0x8008, 0, L_PG_AddressWallyNorth
    h_applymovement PG_NORMAN, Common_Movement_WalkInPlaceFastestDown   // NormanAddressWallySouth/West/East
    VMJump L_PG_AddressedWally
L_PG_AddressWallyNorth:
    h_applymovement PG_NORMAN, Common_Movement_WalkInPlaceFastestRight
L_PG_AddressedWally:
    h_waitmovement
    h_msgbox_actor 9, PG_NORMAN                  // Wally, here, I'll loan you my Pokémon. Wally received a Zigzagoon!
    h_msgbox_actor 10, PG_WALLY                  // Wally: Oh, wow! A Pokémon! Dad: ... Wally received a Poké Ball!
    h_msgbox_actor 11, PG_WALLY                  // Wally: Oh, wow! Thank you!
    h_goto_if_ne 0x8008, 0, L_PG_FacedDoor       // NormanFaceDoorNorth (the other three do nothing)
    h_applymovement PG_NORMAN, Common_Movement_WalkInPlaceFastestDown
    h_waitmovement
L_PG_FacedDoor:                                  // WallyFacePlayer / WallyFaceDown (Common_Movement_FacePlayer:
    h_goto_if_eq 0x8008, 0, L_PG_WallyFaceDown   // Wally (4,108), the player north (4,106) / west (3,107) / east)
    h_goto_if_eq 0x8008, 1, L_PG_WallyFaceUp
    h_goto_if_eq 0x8008, 2, L_PG_WallyFaceRight
    h_turnobject PG_WALLY, 2
    VMJump L_PG_WallyFaced
L_PG_WallyFaceUp:
    h_turnobject PG_WALLY, 0
    VMJump L_PG_WallyFaced
L_PG_WallyFaceRight:
    h_turnobject PG_WALLY, 3
    VMJump L_PG_WallyFaced
L_PG_WallyFaceDown:
    h_applymovement PG_WALLY, Common_Movement_WalkInPlaceFastestDown
    h_waitmovement
L_PG_WallyFaced:
    h_buffer_player
    h_msgbox_actor 12, PG_WALLY                  // <player>... Would you really come with me?
    h_closemessage
    h_setflag FLAG_DONT_TRANSITION_MUSIC
    h_playbgm MUS_FOLLOW_ME
    h_goto_if_eq 0x8008, 1, L_PG_ExitSouth
    h_goto_if_eq 0x8008, 0, L_PG_ExitNorth
    h_goto_if_eq 0x8008, 2, L_PG_ExitWest
    h_applymovement PG_WALLY, Mv_PG_WallyExitEast                       // ExitGymWithWallyEast
    h_applymovement 255, Mv_PG_PlayerExitEast
    VMJump L_PG_Exited
L_PG_ExitSouth:
    h_applymovement PG_NORMAN, Common_Movement_WalkInPlaceFastestDown
    h_applymovement PG_WALLY, Mv_PG_WallyExitSouthWest
    h_applymovement 255, Mv_PG_PlayerExitSouth
    VMJump L_PG_Exited
L_PG_ExitNorth:
    h_applymovement PG_WALLY, Mv_PG_WallyExitNorth
    h_applymovement 255, Mv_PG_PlayerExitNorth
    VMJump L_PG_Exited
L_PG_ExitWest:
    h_applymovement PG_WALLY, Mv_PG_WallyExitSouthWest
    h_applymovement 255, Mv_PG_PlayerExitWest
L_PG_Exited:
    h_waitmovement
    h_removeobject PG_WALLY, FLAG_HIDE_WALLY_PETALBURG_GYM
    h_setflag FLAG_HIDE_WALLY_MOM_PETALBURG_1
    h_setvar VAR_PETALBURG_GYM_STATE, 1
    h_setvar VAR_PETALBURG_STATE, 2
    h_clearflag FLAG_HIDE_WALLY_PETALBURG
    h_clearflag FLAG_HIDE_WALLY_PETALBURG_GYM
    h_setflag FLAG_HIDE_RIVAL_BIRCH_LAB
    h_setvar VAR_BIRCH_STATE, 0                  // special InitBirchState
    h_warpsilent 439, 103, 299, 1                // warp MAP_PETALBURG_CITY (15,8) is the Gym's door: Sapphire's door
    h_release                                    //   exit (Task_ExitDoor) steps the player out to (15,9) before the
                                                 //   tutorial; Black 2's scripted warp has no exit step, so land on
                                                 //   (15,9) (from (15,8) the walk ran one row north, through the
                                                 //   Pokémon Center). Petalburg's OnFrame starts the tutorial (script 2).

L_PG_NoBadges:                                   // PetalburgCity_Gym_EventScript_NormanNoBadges
    h_msgbox 13                                  // Dad: Hm? Aren't you going to the Pokémon Gym in Rustboro City? ...
    h_release
L_PG_OneBadge:
    h_msgbox 14                                  // Dad: I see... So, you've beaten the Gym Leader in Rustboro City. ...
    h_release
L_PG_TwoBadges:
L_PG_ThreeBadges:
    h_msgbox 15                                  // Dad: Hm... <player>, you have gotten stronger. ...
    h_release

#include "scenes/PetalburgCity_Gym_ch6.inc"

    .balign 4, 0
Mv_PG_WallyExitGym:                              // PetalburgCity_Gym_Movement_WallyExitGym
    walk_down 3
    delay_16
    step_end
Mv_PG_WallyArriveNorth:
    delay_16
    walk_up
    delay_16
    delay_8
    walk_up
    walk_right
    walk_up 2
    walk_in_place_fastest_left
    step_end
Mv_PG_WallyArrive:
    delay_16
    walk_up
    delay_16
    delay_8
    walk_up 2
    step_end
Mv_PG_WallyExitNorth:
    walk_down 4
    walk_in_place_fastest_up
    delay_16
    walk_in_place_down
    step_end
Mv_PG_WallyExitEast:
    walk_down 2
    walk_right
    walk_down
    walk_in_place_fastest_up
    delay_16
    walk_in_place_down
    step_end
Mv_PG_WallyExitSouthWest:
    walk_down 3
    walk_in_place_fastest_up
    delay_16
    walk_in_place_down
    step_end
Mv_PG_PlayerExitNorth:
    delay_16 3
    walk_down 3
    delay_8
    step_end
Mv_PG_PlayerExitSouth:
    delay_16 2
    walk_right
    walk_down 5
    delay_8
    step_end
Mv_PG_PlayerExitWest:
    delay_16 2
    walk_down 4
    delay_8
    step_end
Mv_PG_PlayerExitEast:
    walk_in_place_fastest_down
    delay_16 2
    walk_down 3
    walk_right
    walk_down
    delay_8
    step_end
#include "common/movement.inc"
