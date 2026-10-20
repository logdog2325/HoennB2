// Emerald's Littleroot houses, 2F (emerald_ch0_3, 2026-10-12; notes/EMERALD_STORY.md Ch0). Included at the end of
// scenes/players_house_2f.inc in an Emerald build only (zones 391 Brendan's room, 393 May's), with HOUSE_BRENDAN and T_BASE set
// by the zone file. Sources: pokeemerald data/maps/LittlerootTown_BrendansHouse_2F and MaysHouse_2F scripts.inc.
//
// Emerald's rival is not at a notebook when you walk in (Sapphire, Script_21 in the shared file). Her/his room starts empty
// with the rival's Poké Ball on the table: stepping into the room (as the other gender than the house's) sets
// VAR_LITTLEROOT_RIVAL_STATE to 2 (zone init, Sub_Em_2FInit) and examining the ball (Script_9) brings the rival up the stairs
// to meet you (four versions, by the way you face the ball). If you come back down first, the three triggers in the 1F room
// play the same meeting at the door (scenes/emerald/players_house_1f.inc). Afterwards the rival stands at the PC and says
// "Pokémon fully restored..." (Script_21; after the Lilycove battle the post-Lilycove lines of Ch8); a Route 101 rescue sends the
// rival out (0634_route_101.s) and the Lilycove battle brings the rival home (the FLAG_HIDE_..._RIVAL_BEDROOM flags, Ch8).
// Objects (data/story/emerald/e_ch0.json, uid 25 = the rival in the room, 26 = the ball; uid 15 is May's Pichu doll, missing_objects.json). The Sapphire notebook rival (uid 1,
// FLAG_HIDE_*_UPSTAIRS) is hidden for good in an Emerald build (Sub_Em_2FInit, and the new game's flags).
// Zone tiles = pokeemerald tiles + (1, 1). Text: the Emerald overlays src/text/script/emerald/0620_* / 0622_* (line 15 appended: the ball).
#include "hoenn_story.inc"

#define EM_RIVAL2F 25
#define EM_BALL2F 26
#define EM_RIVAL2F_INDEX 2                       // its place in the zone's NPC list (uid 1, 14, then the story objects in file order)
#define EM_T_BALL 15
#if HOUSE_BRENDAN
#define EM_BEDROOM_HIDE FLAG_HIDE_LITTLEROOT_TOWN_BRENDANS_HOUSE_RIVAL_BEDROOM
#define EM_BALL_HIDE FLAG_HIDE_LITTLEROOT_TOWN_BRENDANS_HOUSE_2F_POKE_BALL
#define EM_MUS_ENCOUNTER MUS_ENCOUNTER_BRENDAN
#ifdef HOENN_TEST_CHRIVALG                       // TEST ONLY (HOENN_TEST_CHRIVALG=1): a boy plays Brendan's rival scenes in his own house
#define EM_PLAYER_SEX 0                          // (the girl's path is otherwise only reachable with a new girl save)
#else
#define EM_PLAYER_SEX 1                          // the rival's house is the girl's visit: Brendan lives here
#endif
#define EM_PC_X 1                                // pokeemerald (0,2), where the rival stands after the meeting
#define EM_STAIRS_X 8                            // the tile in front of the stairs (the stairs tile (8, 2) is solid: pokeemerald (7,1) + (1,1))
#else
#define EM_BEDROOM_HIDE FLAG_HIDE_LITTLEROOT_TOWN_MAYS_HOUSE_RIVAL_BEDROOM
#define EM_BALL_HIDE FLAG_HIDE_LITTLEROOT_TOWN_MAYS_HOUSE_2F_POKE_BALL
#define EM_MUS_ENCOUNTER MUS_ENCOUNTER_MAY
#define EM_PLAYER_SEX 0
#define EM_PC_X 9                                // pokeemerald (8,2)
#define EM_STAIRS_X 2                            // the tile in front of the stairs (the stairs tile (2, 2) is solid: pokeemerald (1,1) + (1,1))
#endif

Sub_Em_2FInit:                                   // ..._2F_OnTransition (called by the zone init, Script_24)
    FlagSet RIVAL_HIDE_FLAG                      // Sapphire's notebook rival never shows in Emerald
#ifdef HOENN_TEST_CHRIVALG
    FlagReset EM_BALL_HIDE                       // TEST ONLY: the ball a boy's own room hides
#endif
    h_goto_if_ge VAR_LITTLEROOT_RIVAL_STATE, 2, L_Em_2FReadyDone
    TrainerCardGetSex HLIB_TMP                   // CheckSetReadyToMeet(Brendan/May): only the other gender's visit
    h_goto_if_ne HLIB_TMP, EM_PLAYER_SEX, L_Em_2FReadyDone
    h_setvar VAR_LITTLEROOT_RIVAL_STATE, 2
L_Em_2FReadyDone:
    // Home again after the Lilycove battle (littleroot2, 2026-10-19): pokeemerald's LilycoveCity_EventScript_DefeatedMay/
    // Brendan clear this bedroom flag and the Hall of Fame sets it for good; our shared Lilycove scene clears only Sapphire's
    // FLAG_HIDE_*_UPSTAIRS, so the room does it here, which also fixes saves already past Lilycove
    // (FLAG_MET_RIVAL_LILYCOVE = beaten there; FLAG_SYS_GAME_CLEAR = after the Hall of Fame). Only in the rival's house:
    // the player's own room keeps its (unused) rival hidden.
    h_goto_if_unset FLAG_MET_RIVAL_LILYCOVE, L_Em_2FHomeDone
    h_goto_if_set FLAG_SYS_GAME_CLEAR, L_Em_2FHomeDone
    TrainerCardGetSex HLIB_TMP
    h_goto_if_ne HLIB_TMP, EM_PLAYER_SEX, L_Em_2FHomeDone
    h_clearflag EM_BEDROOM_HIDE
L_Em_2FHomeDone:
    h_goto_if_lt VAR_LITTLEROOT_RIVAL_STATE, 3, L_Em_2FInitEnd
    ObjInitNPCGPos EM_RIVAL2F_INDEX, 0, EM_PC_X, 0, 3   // TryUpdate(Brendan/May)Pos: at the PC, facing up
L_Em_2FInitEnd:
    VMReturn

Script_9:                                        // ..._2F_EventScript_RivalsPokeBall
    h_lock
    h_goto_if_eq VAR_LITTLEROOT_RIVAL_STATE, 2, L_Em_Meet2F
    SEPlay SEQ_SE_MESSAGE
    h_msgbox_info EM_T_BALL                      // It's <rival>'s Poké Ball! Better leave it right where it is.
    h_closemessage
    h_release
L_Em_Meet2F:                                     // ..._2F_EventScript_MeetBrendan / MeetMay
    h_getplayerfacing 0x8008                     // VAR_FACING: 0 up (north), 1 down, 2 left (west), 3 right (east)
    h_delay 10
    h_addobject EM_RIVAL2F, EM_BEDROOM_HIDE
    ActorSetGPos EM_RIVAL2F, EM_STAIRS_X, 0, 3, 1       // (the rival's tile in the data is the one in front of the stairs: nobody stands on the solid stairs tile)
    h_applymovement EM_RIVAL2F, Mv_Em_RivalEnters
    h_waitmovement
    h_applymovement EM_RIVAL2F, Mv_Exclaim       // playse SE_PIN + "!" + Delay48
    h_waitmovement
    h_delay 10
    h_playbgm EM_MUS_ENCOUNTER
    h_buffer_player
    h_goto_if_eq 0x8008, 0, L_Em_MeetNorth
    h_goto_if_eq 0x8008, 1, L_Em_MeetSouth
    h_goto_if_eq 0x8008, 2, L_Em_MeetWest
    // facing east
    h_applymovement EM_RIVAL2F, Mv_Em_ApproachEast
    h_waitmovement
    h_applymovement 255, Mv_Em_PlayerTurnEast
    h_waitmovement
    h_msgbox_actor T(3), EM_RIVAL2F              // Hey! You... Who are you? ... / Huh? Who... Who are you? ...
    h_closemessage
#if HOUSE_BRENDAN
    h_applymovement EM_RIVAL2F, Mv_Em_ToPCEast
    h_waitmovement
#else
    h_applymovement 255, Mv_Em_PlayerWatchEast
    h_applymovement EM_RIVAL2F, Mv_Em_ToPCEast
    h_waitmovement
#endif
    VMJump L_Em_MetRival
L_Em_MeetNorth:
    h_applymovement EM_RIVAL2F, Mv_Em_ApproachNorth
    h_waitmovement
    h_applymovement 255, Mv_Em_PlayerTurnNorth
    h_waitmovement
    h_msgbox_actor T(3), EM_RIVAL2F
    h_closemessage
    h_applymovement 255, Mv_Em_PlayerWatchNorth
    h_applymovement EM_RIVAL2F, Mv_Em_ToPCNorth
    h_waitmovement
    VMJump L_Em_MetRival
L_Em_MeetSouth:
    h_applymovement EM_RIVAL2F, Mv_Em_ApproachSouth
    h_waitmovement
    h_applymovement 255, Mv_Em_PlayerTurnSouth
    h_waitmovement
    h_msgbox_actor T(3), EM_RIVAL2F
    h_closemessage
    h_applymovement 255, Mv_Em_PlayerWatchSouth
    h_applymovement EM_RIVAL2F, Mv_Em_ToPCSouth
    h_waitmovement
    VMJump L_Em_MetRival
L_Em_MeetWest:
    h_applymovement EM_RIVAL2F, Mv_Em_ApproachWest
    h_waitmovement
    h_applymovement 255, Mv_Em_PlayerTurnWest
    h_waitmovement
    h_msgbox_actor T(3), EM_RIVAL2F
    h_closemessage
#if HOUSE_BRENDAN
    h_applymovement 255, Mv_Em_PlayerWatchWest
    h_applymovement EM_RIVAL2F, Mv_Em_ToPCWest
    h_waitmovement
#else
    h_applymovement EM_RIVAL2F, Mv_Em_ToPCWest
    h_waitmovement
#endif
L_Em_MetRival:
    h_setvar VAR_LITTLEROOT_RIVAL_STATE, 3
    h_setflag EM_BALL_HIDE
    h_clearflag EM_BEDROOM_HIDE
    h_setvar VAR_LITTLEROOT_STATE, 1
    h_fadedefaultbgm                             // savebgm MUS_DUMMY + fadedefaultbgm
    h_release

Script_21:                                       // RivalsHouse_2F_EventScript_Rival (the shared file's Script_21 is Sapphire's)
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    ActorSetEyeToEye                             // Common_Movement_FacePlayer
    h_goto_if_set FLAG_MET_RIVAL_LILYCOVE, L_Em_RivalPostLilycove
    ActorMsg MSGFILE_SCRIPT, T(2), EM_RIVAL2F, 0, 0   // Pokémon fully restored! Items ready, and... (..._GettingReady)
    VMJump L_Em_RivalSaid
L_Em_RivalPostLilycove:                          // ..._RivalPostLilycove (Sapphire's is scenes/players_house_2f_ch8.inc)
    h_goto_if_set FLAG_MET_RIVAL_IN_HOUSE_AFTER_LILYCOVE, L_Em_RivalNext
    ActorMsg MSGFILE_SCRIPT, T(4), EM_RIVAL2F, 0, 0   // Hey, it's <player>. I was just checking out my Pokédex. ...
    VMJump L_Em_RivalFirstDone
L_Em_RivalNext:
    ActorMsg MSGFILE_SCRIPT, T(5), EM_RIVAL2F, 0, 0   // I'm having a hard time deciding where I should catch Pokémon next. ...
L_Em_RivalFirstDone:
    FlagSet FLAG_MET_RIVAL_IN_HOUSE_AFTER_LILYCOVE
L_Em_RivalSaid:
    LastKeyWait
    MsgWinCloseAll
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

    .balign 4, 0
#if HOUSE_BRENDAN
Mv_Em_RivalEnters:                               // ..._BrendanEnters (pokeemerald: down 2 from the stairs tile; here from the tile in front of it)
    walk_down
    walk_in_place_fastest_left
    step_end
Mv_Em_ApproachNorth:
    walk_left 2
    walk_down 2
    walk_left
    step_end
Mv_Em_ToPCNorth:
    walk_up 3
    walk_left 4
    walk_in_place_fastest_up
    step_end
Mv_Em_PlayerWatchNorth:
    delay_16
    walk_in_place_fastest_up
    delay_16 4
    walk_in_place_fastest_left
    step_end
Mv_Em_PlayerTurnNorth:
    walk_in_place_fastest_right
    step_end
Mv_Em_ApproachSouth:
    walk_left 3
    step_end
Mv_Em_ToPCSouth:
    walk_up
    walk_left 4
    walk_in_place_fastest_up
    step_end
Mv_Em_PlayerWatchSouth:
    delay_16
    walk_in_place_fastest_up
    delay_16 2
    walk_in_place_fastest_left
    step_end
Mv_Em_PlayerTurnSouth:
    walk_in_place_fastest_right
    step_end
Mv_Em_ApproachWest:
    walk_left 2
    walk_down
    walk_in_place_fastest_left
    step_end
Mv_Em_ToPCWest:
    walk_up 2
    walk_left 5
    walk_in_place_fastest_up
    step_end
Mv_Em_PlayerWatchWest:
    delay_8
    delay_16
    walk_in_place_fastest_up
    delay_16 2
    walk_in_place_fastest_left
    step_end
Mv_Em_PlayerTurnWest:
    walk_in_place_fastest_right
    step_end
Mv_Em_ApproachEast:
    walk_left 5
    walk_in_place_fastest_down
    step_end
Mv_Em_ToPCEast:
    walk_up
    walk_left 2
    walk_in_place_fastest_up
    step_end
Mv_Em_PlayerTurnEast:
    walk_in_place_fastest_up
    step_end
#else
Mv_Em_RivalEnters:                               // ..._MayEnters (down 2 from the stairs tile; here from the tile in front of it)
    walk_down
    walk_in_place_fastest_right
    step_end
Mv_Em_ApproachNorth:
    walk_right 2
    walk_down 2
    walk_right
    step_end
Mv_Em_ToPCNorth:
    walk_up 3
    walk_in_place_fastest_right
    walk_right 4
    walk_in_place_fastest_up
    step_end
Mv_Em_PlayerWatchNorth:
    delay_16
    walk_in_place_fastest_up
    delay_16 4
    walk_in_place_fastest_right
    step_end
Mv_Em_PlayerTurnNorth:
    walk_in_place_fastest_left
    step_end
Mv_Em_ApproachSouth:
    walk_right 3
    step_end
Mv_Em_ToPCSouth:
    walk_up
    walk_in_place_fastest_right
    walk_right 4
    walk_in_place_fastest_up
    step_end
Mv_Em_PlayerWatchSouth:
    delay_16
    walk_in_place_fastest_up
    delay_16 2
    walk_in_place_fastest_right
    step_end
Mv_Em_PlayerTurnSouth:
    walk_in_place_fastest_left
    step_end
Mv_Em_ApproachWest:
    walk_right 5
    walk_in_place_fastest_down
    step_end
Mv_Em_ToPCWest:
    walk_up
    walk_right 2
    walk_in_place_fastest_up
    step_end
Mv_Em_PlayerTurnWest:
    walk_in_place_fastest_up
    step_end
Mv_Em_ApproachEast:
    walk_right 2
    walk_down
    walk_in_place_fastest_right
    step_end
Mv_Em_ToPCEast:
    walk_up 2
    walk_right 5
    walk_in_place_fastest_up
    step_end
Mv_Em_PlayerWatchEast:
    delay_16
    walk_in_place_fastest_up
    delay_16 2
    walk_in_place_fastest_right
    step_end
Mv_Em_PlayerTurnEast:
    walk_in_place_fastest_left
    step_end
#endif
    .balign 4, 0
