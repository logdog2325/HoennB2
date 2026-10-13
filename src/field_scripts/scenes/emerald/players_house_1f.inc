// Emerald's Littleroot houses, 1F (emerald_ch0_3, 2026-10-12; notes/EMERALD_STORY.md Ch0). Included at the end of
// scenes/players_house_1f.inc in an Emerald build only (zones 390 Brendan's house, 392 May's), after the shared bodies, with
// HOUSE_BRENDAN and T_BASE set by the zone file. Sources: pokeemerald data/maps/LittlerootTown_BrendansHouse_1F and
// MaysHouse_1F scripts.inc (the two houses play the same lists: May's differ only by 6 tiles), data/scripts/players_house.inc.
//
// What Emerald does here that Sapphire does not:
//  - The rival's introduction. When the player has stood in the rival's room (VAR_LITTLEROOT_RIVAL_STATE 2: set by the 2F
//    zone init) and comes back down, three coord triggers by the stairs (MeetRival0/1/2 = Script_7/8/9) let the rival walk in
//    through the front door, speak and go up the stairs. (Examining the Poké Ball upstairs starts the same meeting: 2F.)
//  - The rival's sibling, a boy who wanders the room and asks "Do you already have your own Pokémon?" (Script_10).
//  - The rival's mom has Emerald's four-way talk (Script_29 below); the shared Sapphire body of Script_29 is not built here.
// Objects (data/story/emerald/e_ch0.json): the rival at the door (uid 6, hidden by the house's FLAG_HIDE_..._BRENDAN/_MAY, set
// at the new game), the sibling (uid 7). Text: the file's Emerald overlay src/text/script/emerald/0619_* / 0621_* (Ch13's lines are
// B3's, Ch0's are made by work/agents/emerald_ch0_3/tools/gen_text_ch0.py): lines 41 (the rival's "Who are you?") and 42 (the
// sibling) are appended. Zone tiles = pokeemerald tiles + (1, 0).
#include "hoenn_story.inc"

#define EM_RIVAL1F 6
#define EM_SIBLING 7
#define EM_T_WHOAREYOU 41                        // appended to the house's Emerald text overlay (src/text/script/emerald/0619 / 0621)
#define EM_T_SIBLING 42
#if HOUSE_BRENDAN
#define EM_RIVAL_HIDE FLAG_HIDE_LITTLEROOT_TOWN_BRENDANS_HOUSE_BRENDAN
#define EM_BEDROOM_HIDE FLAG_HIDE_LITTLEROOT_TOWN_BRENDANS_HOUSE_RIVAL_BEDROOM
#define EM_BALL_HIDE FLAG_HIDE_LITTLEROOT_TOWN_BRENDANS_HOUSE_2F_POKE_BALL
#define EM_MUS_ENCOUNTER MUS_ENCOUNTER_BRENDAN
#else
#define EM_RIVAL_HIDE FLAG_HIDE_LITTLEROOT_TOWN_MAYS_HOUSE_MAY
#define EM_BEDROOM_HIDE FLAG_HIDE_LITTLEROOT_TOWN_MAYS_HOUSE_RIVAL_BEDROOM
#define EM_BALL_HIDE FLAG_HIDE_LITTLEROOT_TOWN_MAYS_HOUSE_2F_POKE_BALL
#define EM_MUS_ENCOUNTER MUS_ENCOUNTER_MAY
#endif

Script_7:                                        // ..._1F_EventScript_MeetRival0 (trigger left of the stairs)
    h_lock
    h_setvar 0x8008, 0
    VMJump L_Em_MeetRival
Script_8:                                        // ..._MeetRival1 (below the stairs)
    h_lock
    h_setvar 0x8008, 1
    VMJump L_Em_MeetRival
Script_9:                                        // ..._MeetRival2 (right of the stairs)
    h_lock
    h_setvar 0x8008, 2
L_Em_MeetRival:                                  // ..._1F_EventScript_MeetRival (VAR_0x8008 = which trigger)
    h_playse SE_EXIT
    h_delay 10
    h_addobject EM_RIVAL1F, EM_RIVAL_HIDE
    h_delay 30
    h_applymovement EM_RIVAL1F, Mv_Exclaim       // playse SE_PIN + the "!" balloon + Delay48
    h_waitmovement
    h_goto_if_eq 0x8008, 1, L_Em_NoFaceDown
    h_applymovement 255, Mv_Em_PlayerFaceDown    // PlayerFaceBrendan/May (not for the trigger straight below the stairs)
    h_waitmovement
L_Em_NoFaceDown:
    h_playbgm EM_MUS_ENCOUNTER
    h_goto_if_eq 0x8008, 1, L_Em_Approach1
    h_goto_if_eq 0x8008, 2, L_Em_Approach2
    h_applymovement EM_RIVAL1F, Mv_Em_RivalApproach0
    VMJump L_Em_Approached
L_Em_Approach1:
    h_applymovement EM_RIVAL1F, Mv_Em_RivalApproach1
    VMJump L_Em_Approached
L_Em_Approach2:
    h_applymovement EM_RIVAL1F, Mv_Em_RivalApproach2
L_Em_Approached:
    h_waitmovement
    h_buffer_player
    h_msgbox_actor EM_T_WHOAREYOU, EM_RIVAL1F    // "Hey! You... Who are you? ..." / "Huh? Who... Who are you? ..."
    h_closemessage
    h_goto_if_eq 0x8008, 1, L_Em_GoUp1
    h_goto_if_eq 0x8008, 2, L_Em_GoUp2
    h_applymovement 255, Mv_Em_PlayerWatchExit0
    h_applymovement EM_RIVAL1F, Mv_Em_RivalUpstairs0
    VMJump L_Em_WentUp
L_Em_GoUp1:
    h_applymovement 255, Mv_Em_PlayerWatchExit1
    h_applymovement EM_RIVAL1F, Mv_Em_RivalUpstairs1
    VMJump L_Em_WentUp
L_Em_GoUp2:
    h_applymovement 255, Mv_Em_PlayerWatchExit2
    h_applymovement EM_RIVAL1F, Mv_Em_RivalUpstairs2
L_Em_WentUp:
    h_waitmovement
    h_playse SE_EXIT
    h_removeobject EM_RIVAL1F, EM_RIVAL_HIDE
    h_setflag EM_BALL_HIDE
    h_clearflag EM_BEDROOM_HIDE                  // the rival is in the bedroom now
    h_delay 30
    h_setvar VAR_LITTLEROOT_RIVAL_STATE, 3
    h_setvar VAR_LITTLEROOT_STATE, 1
    h_fadedefaultbgm                             // savebgm MUS_DUMMY + fadedefaultbgm
    h_release

Script_10:                                       // RivalsHouse_1F_EventScript_RivalSibling
    h_lock
    SEPlay SEQ_SE_MESSAGE
    h_faceplayer
    h_msgbox EM_T_SIBLING                        // Hi, neighbor! Do you already have your own Pokémon?
    h_release

// RivalsHouse_1F_EventScript_RivalMom (pokeemerald's order of checks; Sapphire's Script_29 is not built in Emerald). T(17) is the
// "My husband..." line the shared file already holds for the same state; the lines are Emerald's (text overrides).
Script_29:
    ActorsPauseAll
    SEPlay SEQ_SE_MESSAGE
    ActorSetEyeToEye
    WordSetPlayerName 0
    h_goto_if_set FLAG_DEFEATED_RIVAL_ROUTE103, L_Em_RivalMomGoHome
    h_goto_if_set FLAG_SYS_POKEMON_GET, L_Em_RivalMomOut
    h_goto_if_eq VAR_LITTLEROOT_RIVAL_STATE, 3, L_Em_RivalMomBusy
    ParentActorMsg MSGFILE_SCRIPT, T(12), 0, 0   // Like child, like father. ...
    VMJump L_Em_RivalMomDone
L_Em_RivalMomGoHome:
    ParentActorMsg MSGFILE_SCRIPT, T(16), 0, 0   // I think it's wonderful for people to travel with Pokémon. ...
    VMJump L_Em_RivalMomDone
L_Em_RivalMomOut:
    ParentActorMsg MSGFILE_SCRIPT, T(15), 0, 0   // Oh, <rival> went out to Route 103 just a little while ago. ...
    VMJump L_Em_RivalMomDone
L_Em_RivalMomBusy:
    ParentActorMsg MSGFILE_SCRIPT, T(17), 0, 0   // That <rival>! I guess our child is too busy with Pokémon to notice ...
L_Em_RivalMomDone:
    LastKeyWait
    ActorMsgClose
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

    .balign 4, 0
Mv_Em_PlayerFaceDown:
    walk_in_place_fastest_down
    step_end
Mv_Em_RivalApproach0:                            // ..._BrendanApproachPlayer0 (the same for May): door, left, up to the trigger's tile
    walk_in_place_fastest_left
    walk_left
    walk_in_place_fastest_up
    walk_up 4
    step_end
Mv_Em_RivalApproach1:
    walk_up 3
    step_end
Mv_Em_RivalApproach2:
    walk_in_place_fastest_right
    walk_right
    walk_in_place_fastest_up
    walk_up 4
    step_end
Mv_Em_PlayerWatchExit0:
    delay_16
    delay_8
    walk_in_place_fastest_right
    step_end
Mv_Em_PlayerWatchExit1:
    delay_16
    delay_8
    walk_in_place_fastest_right
    delay_16 2
    walk_in_place_fastest_up
    step_end
Mv_Em_PlayerWatchExit2:
    delay_16
    delay_8
    walk_in_place_fastest_left
    step_end
Mv_Em_RivalUpstairs0:
    walk_in_place_fastest_right
    walk_right
    walk_in_place_fastest_up
    walk_up 2
    step_end
Mv_Em_RivalUpstairs1:
    walk_in_place_fastest_right
    walk_right
    walk_in_place_fastest_up
    walk_up 2
    walk_in_place_fastest_left
    walk_left
    walk_in_place_fastest_up
    walk_up
    step_end
Mv_Em_RivalUpstairs2:
    walk_in_place_fastest_left
    walk_left
    walk_in_place_fastest_up
    walk_up 2
    step_end
    .balign 4, 0
