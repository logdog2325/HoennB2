// Emerald's Petalburg Gym, Norman's end (emerald_ch0_3, 2026-10-12; notes/EMERALD_STORY.md Ch6). Included at the end of the
// bodies of scenes/PetalburgCity_Gym_ch6.inc in an Emerald build only. Source: pokeemerald data/maps/PetalburgCity_Gym/
// scripts.inc (NormanBattle, GiveFacade, WallysDadArrives..., the movement lists) and PetalburgCity/scripts.inc.
//
// What Emerald changes: Sapphire's Norman only hands over the badge and TM42 (Facade) and mentions that Wally's parents came
// calling (Surf comes from Wally's father when you visit him). In Emerald, once Facade is explained and Dad has said he is
// happy and a little sad, Wally's father walks in through the Leaders' room door, asks Norman to lend him the player and takes
// the player out to his house in Petalburg (this file: the gym half; scenes/emerald/PetalburgCity.inc: the walk through the
// town; the room 1000 file: the HM). The player leaves the Gym with VAR_PETALBURG_STATE 4.
// Improvement over pokeemerald: when the Bag was full for Facade and Dad hands it over later (the post-battle talk), Wally's
// father still comes (in pokeemerald he never does and Surf cannot be had).
// Wally's father in the Gym: data/story/emerald/e_ch6.json uid 30 (hidden by FLAG_HIDE_PETALBURG_GYM_WALLYS_DAD, set at the new
// game). Room tiles = pokeemerald tiles + (1, 0). Text: the room's Emerald overlay src/text/script/emerald/0187_*: lines 16-51
// as Ch6's, EM_PGT_* appended.
#define EM_WALLYSDAD 30
#define EM_PGT_PleaseComeWithMe 53
#define EM_PGT_LetMeBorrow 54

L_Em_GiveFacadeBattle:                           // PetalburgCity_Gym_EventScript_NormanBattle after the badge: GiveFacade
    h_giveitem ITEM_TM42
    h_goto_if_eq HLIB_RESULT, 0, L_Ch6_BagFull   // Common_EventScript_BagIsFull: the scene ends, Facade is given at the next talk
    h_setflag FLAG_RECEIVED_TM42
    h_buffer_player
    h_msgbox_actor PGT_ExplainFacade, 1          // Dad: TM42 contains Facade. ...
    h_delay 30
    VMJump L_Em_HappySad

L_Em_GiveFacadeLate:                             // PetalburgCity_Gym_EventScript_GiveFacade2 (the Bag was full before)
    h_giveitem ITEM_TM42
    h_goto_if_eq HLIB_RESULT, 0, L_Ch6_BagFull
    h_setflag FLAG_RECEIVED_TM42
    h_buffer_player
    h_msgbox_actor PGT_ExplainFacade, 1
    h_goto_if_ge VAR_PETALBURG_STATE, 4, L_Em_NoDadScene   // (Wally's father came already)
    h_delay 30
L_Em_HappySad:
    h_msgbox_actor PGT_HappySad, 1               // Dad: As the Gym Leader, I can't express how upset I am... Wait, hold on
    h_closemessage
    h_delay 40
    h_playse SE_EXIT                             // playse SE_DOOR
    h_delay 10
    h_addobject EM_WALLYSDAD, FLAG_HIDE_PETALBURG_GYM_WALLYS_DAD
    h_getplayerfacing 0x8008                     // VAR_FACING: 0 up (north), 2 left (west), 3 right (east)
    h_applymovement EM_WALLYSDAD, Mv_Em_WDadEnters
    h_waitmovement
    h_applymovement EM_WALLYSDAD, Mv_Em_WDadNotice   // playse SE_PIN + "!" + Delay48
    h_waitmovement
    h_delay 10
    h_goto_if_eq 0x8008, 2, L_Em_WDadArrivesWest
    h_goto_if_eq 0x8008, 3, L_Em_WDadArrivesEast
    h_setvar 0x8008, 0                           // (each branch sets the facing as a constant: the walk checkers then follow one facing at a time)
    h_applymovement EM_WALLYSDAD, Mv_Em_WDadApproachNorth     // facing north: Dad is in front of the player, Dad's friend comes from the left
    h_waitmovement
    h_applymovement 255, Common_Movement_WalkInPlaceFastestLeft
    h_applymovement 1, Common_Movement_WalkInPlaceFastestLeft
    h_waitmovement
    VMJump L_Em_WDadTalk
L_Em_WDadArrivesEast:
    h_setvar 0x8008, 3
    h_applymovement EM_WALLYSDAD, Mv_Em_WDadApproachEast
    h_waitmovement
    h_applymovement 255, Common_Movement_WalkInPlaceFastestDown
    h_applymovement 1, Common_Movement_WalkInPlaceFastestDown
    h_waitmovement
    VMJump L_Em_WDadTalk
L_Em_WDadArrivesWest:
    h_setvar 0x8008, 2
    h_applymovement EM_WALLYSDAD, Mv_Em_WDadApproachWest
    h_waitmovement
    h_applymovement 255, Common_Movement_WalkInPlaceFastestDown
    h_applymovement 1, Common_Movement_WalkInPlaceFastestDown
    h_waitmovement
L_Em_WDadTalk:
    h_buffer_player
    h_msgbox_actor EM_PGT_PleaseComeWithMe, EM_WALLYSDAD   // Ah, there you are, <player>! Please come with me. ...
    h_closemessage
    h_delay 20
    h_goto_if_eq 0x8008, 2, L_Em_WDadFaceWest
    h_goto_if_eq 0x8008, 3, L_Em_WDadFaceEast
    h_applymovement EM_WALLYSDAD, Common_Movement_WalkInPlaceFastestUp       // ...FaceNormanNorth
    VMJump L_Em_WDadAskNorman
L_Em_WDadFaceEast:
    h_applymovement EM_WALLYSDAD, Common_Movement_WalkInPlaceFastestRight
    VMJump L_Em_WDadAskNorman
L_Em_WDadFaceWest:
    h_applymovement EM_WALLYSDAD, Common_Movement_WalkInPlaceFastestLeft
L_Em_WDadAskNorman:
    h_waitmovement
    h_msgbox_actor EM_PGT_LetMeBorrow, EM_WALLYSDAD  // Norman, you don't mind, do you? Let me borrow your <player> for a minute or two.
    h_closemessage
    h_setflag FLAG_DONT_TRANSITION_MUSIC
    h_playbgm MUS_FOLLOW_ME
    h_goto_if_eq 0x8008, 2, L_Em_WDadLeaveWest
    h_goto_if_eq 0x8008, 3, L_Em_WDadLeaveEast
    h_applymovement EM_WALLYSDAD, Mv_Em_WDadExitNorth
    h_applymovement 1, Common_Movement_WalkInPlaceFastestDown
    h_applymovement 255, Mv_Em_PlayerExitNorth
    VMJump L_Em_WDadLeft
L_Em_WDadLeaveEast:
    h_applymovement EM_WALLYSDAD, Mv_Em_WDadExitNorth
    h_applymovement 255, Mv_Em_PlayerExitEast
    VMJump L_Em_WDadLeft
L_Em_WDadLeaveWest:
    h_applymovement EM_WALLYSDAD, Mv_Em_WDadExitWest
    h_applymovement 255, Mv_Em_PlayerExitWest
L_Em_WDadLeft:
    h_waitmovement
    h_removeobject EM_WALLYSDAD, FLAG_HIDE_PETALBURG_GYM_WALLYS_DAD
    h_setvar VAR_PETALBURG_STATE, 4
    h_clearflag FLAG_HIDE_PETALBURG_CITY_WALLYS_DAD
    // warp MAP_PETALBURG_CITY, 15, 8: in front of the Gym door (Petalburg zone 439, Sapphire tile + (88, 290)); the walk to the
    // house is Petalburg's OnFrame scene (VAR_PETALBURG_STATE 4, scenes/emerald/PetalburgCity.inc)
    h_warpsilent 439, 103, 299, 1
    h_release
L_Em_NoDadScene:
    h_release

    .balign 4, 0
Mv_Em_WDadEnters:                                // PetalburgCity_Gym_Movement_WallysDadEnterGym
    walk_up
    delay_8
    walk_in_place_fastest_right
    delay_8
    walk_in_place_fastest_left
    delay_16
    walk_in_place_fastest_up
    step_end
Mv_Em_WDadNotice:                                // playse SE_PIN, ExclamationMark, Delay48
    emote_exclamation_mark
    delay_16 3
    step_end
Mv_Em_WDadApproachNorth:                         // ..._WallysDadApproachPlayerNorth
    walk_right 2
    walk_up 3
    walk_in_place_fastest_right
    step_end
Mv_Em_WDadApproachEast:
    walk_right 2
    walk_up 3
    step_end
Mv_Em_WDadApproachWest:
    walk_right 2
    walk_up 2
    walk_right 2
    walk_up
    step_end
Mv_Em_WDadExitNorth:                             // ..._WallysDadExitNorth (the same for East)
    walk_down 2
    walk_left 2
    walk_down 2
    walk_in_place_fastest_up
    delay_8
    walk_in_place_down
    set_invisible
    step_end
Mv_Em_WDadExitWest:
    walk_down 2
    walk_left 4
    walk_down 2
    walk_in_place_fastest_up
    delay_8
    walk_in_place_down
    set_invisible
    step_end
Mv_Em_PlayerExitNorth:                           // ..._PlayerExitWithWallysDadNorth
    delay_16
    walk_down 2
    walk_left 2
    walk_down 2
    step_end
Mv_Em_PlayerExitEast:
    delay_16
    walk_down 2
    walk_left
    walk_down 3
    step_end
Mv_Em_PlayerExitWest:
    delay_16
    walk_down 3
    walk_left 3
    walk_down 2
    step_end
    .balign 4, 0
