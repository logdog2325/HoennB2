// Chapter Ch8's beat in Slateport City (Sapphire data/maps/SlateportCity/scripts.inc SlateportCity_EventScript_CaptStern
// .. SlateportCity_EventScript_Ty; ch8b agent 2026-10-07). Included by scenes/SlateportCity.inc (its scripts 26-28:
// Capt. Stern, Ty, Gabby; the people are placed by data/story/ch3a.json, hidden by FLAG_HIDE_STERN_SLATEPORT and
// FLAG_HIDE_GABBY_AND_TY_SLATEPORT, which Mt. Pyre's summit scene clears). Capt. Stern (uid 111) runs the TV interview
// that the crowd watches (their positions are set by ch3a's zone init when VAR_SLATEPORT_STATE is 1), a megaphone voice
// announces the Aqua takeover of the submarine, and he takes the player to the Harbor (Ch8's
// scenes/SlateportCity_Harbor_Ch8.inc). Text: lines 48-55 of src/text/scenes/SlateportCity.txt. Ty and Gabby keep ch3a's
// stand-in lines (T_BigSmile, T_Invaluable) as Sapphire's.
#define T_SternMoveAhead 48
#define T_GabbyWonderful 49
#define T_SternWhew 50
#define T_OhPlayerDiscovery 51
#define T_EvilTeamAssume 52
#define T_SternWhatWasThat 53
#define T_FromHarbor 54
#define T_PleaseComeWithMe 55

#define SC8_TY 109                      // Sapphire objects 9-11 and the crowd, uid = 100 + local id
#define SC8_GABBY 110
#define SC8_STERN 111
#define SC8_FATMAN 101
#define SC8_MAN1 102
#define SC8_RICHBOY 103
#define SC8_COOK 106
#define SC8_OLDWOMAN 107
#define SC8_HARBOR_ZONE 596             // SlateportCity_Harbor (room origin (1,-2): Sapphire tile (11,14) = zone tile (12,12))

Ch8_CaptStern:                          // SlateportCity_EventScript_CaptStern
    h_lock
    h_buffer_player
    h_msgbox_actor T_SternMoveAhead, SC8_STERN      // Capt. Stern: Yes, indeed. We intend to move ahead with our exploration.
    h_msgbox_actor T_GabbyWonderful, SC8_GABBY      // Gabby: That's wonderful, Capt. Stern! Thank you for taking the time ...
    h_closemessage
    h_applymovement SC8_GABBY, Mv_SC8_FaceRight
    h_waitmovement
    h_delay 10
    h_applymovement SC8_TY, Mv_SC8_FaceDown
    h_waitmovement
    h_delay 25
    h_applymovement SC8_STERN, Mv_SC8_SternWatchGabbyAndTyExit
    h_applymovement 255, Mv_SC8_PlayerFaceStern
    h_applymovement SC8_GABBY, Mv_SC8_GabbyExit
    h_applymovement SC8_TY, Mv_SC8_TyExit
    h_waitmovement
    h_removeobject SC8_GABBY, FLAG_HIDE_GABBY_AND_TY_SLATEPORT
    h_removeobject SC8_TY, FLAG_HIDE_GABBY_AND_TY_SLATEPORT
    h_msgbox_actor T_SternWhew, SC8_STERN           // Capt. Stern: Whew... That was my first time to be filmed for TV. That was nerve wracking.
    h_closemessage
    h_applymovement SC8_STERN, Mv_SC8_FaceUp
    h_waitmovement
    h_buffer_player
    h_msgbox_actor T_OhPlayerDiscovery, SC8_STERN   // Capt. Stern: Oh! <player>! You're looking great! We made a huge discovery ...
    h_closemessage
    h_playbgm MUS_EVIL_TEAM
    h_msgbox_info T_EvilTeamAssume                  // Fufufu... Capt. Stern, I presume. We of Team Aqua will assume control of your submarine! ...
    h_closemessage
    h_applymovement SC8_COOK, Mv_SC8_FaceLeft
    h_applymovement SC8_FATMAN, Mv_SC8_FaceLeft
    h_applymovement SC8_OLDWOMAN, Mv_SC8_OldWomanConcern
    h_applymovement SC8_RICHBOY, Mv_SC8_QuestionMark
    h_applymovement SC8_MAN1, Mv_SC8_ManConcern
    h_waitmovement
    h_applymovement SC8_STERN, Mv_SC8_FaceDown
    h_waitmovement
    h_msgbox_actor T_SternWhatWasThat, SC8_STERN    // Capt. Stern: What was that all about? It sounded like someone using a megaphone...
    h_closemessage
    SEPlay SEQ_SE_MESSAGE                          // playse SE_PIN
    h_applymovement SC8_STERN, Mv_SC8_Exclaim
    h_waitmovement
    h_applymovement SC8_STERN, Mv_SC8_Delay48
    h_waitmovement
    h_msgbox_actor T_FromHarbor, SC8_STERN          // It's from the Harbor! The submarine! They're trying to take it!
    h_closemessage
    h_faceplayer                                    // Common_Movement_FacePlayer (Stern is the talked-to person)
    h_buffer_player
    h_msgbox_actor T_PleaseComeWithMe, SC8_STERN    // <player>! Please, come with me!
    h_closemessage
    h_applymovement SC8_STERN, Mv_SC8_SternEnterHarbor
    h_applymovement 255, Mv_SC8_PlayerEnterHarbor
    h_waitmovement
    h_removeobject SC8_STERN, FLAG_HIDE_STERN_SLATEPORT
    h_clearflag FLAG_HIDE_STERN_SLATEPORT_HARBOR
    h_clearflag FLAG_HIDE_SUBMARINE_SHADOW_SLATEPORT_HARBOR
    h_clearflag FLAG_HIDE_GRUNT_1_SLATEPORT_HARBOR
    h_clearflag FLAG_HIDE_GRUNT_2_SLATEPORT_HARBOR
    h_setvar VAR_SLATEPORT_STATE, 2
    MapChangeWarp SC8_HARBOR_ZONE, 12, 12, 0        // warp MAP_SLATEPORT_CITY_HARBOR, 255, 11, 14 (Black 2's own warp: it fades in by itself)
    h_release

Ch8_Ty:                                 // SlateportCity_EventScript_Ty
    h_msgbox_sign T_BigSmile
Ch8_Gabby:                              // SlateportCity_EventScript_Gabby
    h_msgbox_sign T_Invaluable

    .balign 4, 0
Mv_SC8_FaceUp:
    face_up
    step_end
    .balign 4, 0
Mv_SC8_FaceDown:
    walk_in_place_fastest_down
    step_end
    .balign 4, 0
Mv_SC8_FaceLeft:
    walk_in_place_fastest_left
    step_end
    .balign 4, 0
Mv_SC8_FaceRight:
    walk_in_place_fastest_right
    step_end
    .balign 4, 0
Mv_SC8_QuestionMark:
    emote_question_mark
    step_end
    .balign 4, 0
Mv_SC8_Exclaim:
    emote_exclamation_mark
    step_end
    .balign 4, 0
Mv_SC8_Delay48:                         // Common_Movement_Delay48
    delay_16 3
    step_end
    .balign 4, 0
Mv_SC8_OldWomanConcern:                 // SlateportCity_Movement_OldWomanConcern
    delay_16 2
    emote_question_mark
    walk_in_place_fastest_right
    delay_16 2
    walk_in_place_fastest_left
    step_end
    .balign 4, 0
Mv_SC8_ManConcern:                      // SlateportCity_Movement_ManConcern
    emote_question_mark
    walk_in_place_fastest_up
    delay_16
    walk_in_place_fastest_down
    delay_16 2
    walk_in_place_fastest_left
    step_end
    .balign 4, 0
Mv_SC8_GabbyExit:                       // SlateportCity_Movement_GabbyExit
    delay_16
    walk_left 2
    walk_down
    walk_left 8
    step_end
    .balign 4, 0
Mv_SC8_TyExit:                          // SlateportCity_Movement_TyExit
    walk_down
    walk_left 3
    walk_down
    walk_left 8
    step_end
    .balign 4, 0
Mv_SC8_SternEnterHarbor:                // SlateportCity_Movement_SternEnterHarbor
    walk_right
    walk_up 2
    set_invisible
    step_end
    .balign 4, 0
Mv_SC8_SternWatchGabbyAndTyExit:        // SlateportCity_Movement_SternWatchGabbyAndTyExit
    delay_16 5
    walk_down
    walk_left
    step_end
    .balign 4, 0
Mv_SC8_PlayerEnterHarbor:               // SlateportCity_Movement_PlayerEnterHarbor
    walk_in_place_fastest_right
    delay_16 2
    walk_right
    walk_up
    step_end
    .balign 4, 0
Mv_SC8_PlayerFaceStern:                 // SlateportCity_Movement_PlayerFaceStern
    delay_16 7
    walk_in_place_fastest_down
    step_end
    .balign 4, 0
