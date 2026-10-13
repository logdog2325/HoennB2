// Chapter Ch8's beats in the Slateport Harbor (Sapphire data/maps/SlateportCity_Harbor/scripts.inc OnTransition's
// ReadyEvilTeamEscapeScene, the four EvilTeamEscapeTriggers and EventScript_CaptStern; ch8b agent 2026-10-07).
// Included by 1192_room_SlateportCity_Harbor.s (scripts 6-10; the zone init, Story_HB_Init, calls Ch8_HB_Init while
// VAR_SLATEPORT_HARBOR_STATE is 1). People and triggers: data/story/ch3a.json (Stern uid 4, the grunt 6 and Archie 7,
// the workers 1-3 hidden by FLAG_HIDE_WORKERS_SLATEPORT_HARBOR). The submarine (object 8, Sapphire's shadow in the
// water: 3D object 0x2000, b2tools/models_objects.py, placed by data/story/missing_objects.json) sails off to the east
// while the two Aqua members jump into it, Capt. Stern comes up to the player as in Sapphire (missing_objects 2026-10-08). Text: lines 17-21 of src/text/script/0352_room_SlateportCity_Harbor.txt (Ch6's Scanner
// trade is scenes/SlateportCity_Harbor_Ch6.inc, lines 4-16).
#define T_ArchieYouAgain 17
#define T_SternWhySteal 18
#define T_SternEvilLeftNeedDive 19
#define T_SternNeedDive 20
#define T_SternSameThugs 21

#define HB8_STERN 4
#define HB8_GRUNT 6
#define HB8_ARCHIE 7
#define HB8_SUB 8                       // the submarine shadow (Sapphire object 8; 3D object 0x2000, data/story/missing_objects.json)
#define HB8_POS 0x803A                  // Sapphire VAR_0x8008: which trigger tile (0-3)
#define HB8_STERN_IDX 3                 // Stern's place in the zone's NPC list for ObjInitNPCGPos (ch3a.json order: 1, 2, 3, 4, 6, 7)

#if !__has_include("scenes/SlateportCity_Harbor_Ch6.inc")
Ch6_HB_SternScanner:                    // stand-in while Chapter 6's Scanner trade file is not in the tree
    h_release
#endif

Ch8_HB_Init:                            // SlateportCity_Harbor_EventScript_ReadyEvilTeamEscapeScene (called by the zone init)
    // savebgm MUS_EVIL_TEAM: BGMPlay is forbidden in a zone init (ov012 permission table), so the theme starts with the
    // Archie scene below instead
    ObjInitNPCGPos HB8_STERN_IDX, 2, 13, 0, 11  // setobjectxyperm 4, 12, 13 (zone tile (13,11)), facing left (movement type 9)
    h_setflag FLAG_HIDE_WORKERS_SLATEPORT_HARBOR
    VMReturn

Ch8_HB_CaptStern:                       // SlateportCity_Harbor_EventScript_CaptStern
    h_lock
    SEPlay SEQ_SE_MESSAGE
    h_faceplayer
#if __has_include("scenes/SlateportCity_Harbor_Events.inc")
#include "scenes/SlateportCity_Harbor_Events.inc"   // (events agent) after the game: the Old Sea Map (text lines 35-36)
#endif
    h_goto_if_badge 7, Ch6_HB_SternScanner
    h_goto_if_set FLAG_EVIL_TEAM_ESCAPED_STERN_SPOKE, L_HB8_NeedDive
    h_goto_if_set FLAG_EVIL_TEAM_ESCAPED_IN_SUBMARINE, L_HB8_LeftNeedDive
    h_goto_if_eq VAR_SLATEPORT_HARBOR_STATE, 2, L_HB8_WhySteal
    h_msgbox T_SternSameThugs           // Capt. Stern: Those thugs... They're the same lot who tried to rob the Devon Goods at the Museum.
    h_closemessage
    h_release
L_HB8_WhySteal:
    h_msgbox T_SternWhySteal            // Capt. Stern: Why... Why would Team Aqua steal my Submarine Explorer 1? ...
    h_release
L_HB8_LeftNeedDive:
    h_setflag FLAG_EVIL_TEAM_ESCAPED_STERN_SPOKE
    h_buffer_player
    h_msgbox T_SternEvilLeftNeedDive    // Capt. Stern: Oh, <player>... Okay... So Team Aqua left before you could stop them... You would need a Pokemon that knows how to Dive ...
    h_release
L_HB8_NeedDive:
    h_msgbox T_SternNeedDive            // Capt. Stern: Trying to catch a submarine... It's impossible. ...
    h_release

Ch8_HB_EscapeTrigger0:
    h_setvar HB8_POS, 0
    VMJump L_HB8_Scene
Ch8_HB_EscapeTrigger1:
    h_setvar HB8_POS, 1
    VMJump L_HB8_Scene
Ch8_HB_EscapeTrigger2:
    h_setvar HB8_POS, 2
    VMJump L_HB8_Scene
Ch8_HB_EscapeTrigger3:                  // the player first steps up one tile
    h_setvar HB8_POS, 3
    h_lock
    h_applymovement 255, Mv_HB8_PlayerWalkUp
    h_waitmovement
    VMJump L_HB8_SceneLocked
L_HB8_Scene:
    h_lock
L_HB8_SceneLocked:                      // SlateportCity_Harbor_EventScript_EvilTeamEscapeScene
    h_playbgm MUS_EVIL_TEAM
    h_applymovement HB8_ARCHIE, Mv_HB8_FaceDown
    h_waitmovement
    h_applymovement 255, Mv_HB8_PlayerFaceUp
    h_waitmovement
    h_msgbox_actor T_ArchieYouAgain, HB8_ARCHIE     // Archie: Fwahahaha... I commiserate with you! ... Or, will you follow us back to our Hideout in Lilycove City? Fwahahahaha...
    h_closemessage
    h_applymovement HB8_GRUNT, Mv_HB8_BoardSub
    h_applymovement HB8_ARCHIE, Mv_HB8_BoardSub
    h_applymovement HB8_SUB, Mv_HB8_SubmarineExit
    h_waitmovement
    h_removeobject HB8_GRUNT, FLAG_HIDE_GRUNT_1_SLATEPORT_HARBOR
    h_removeobject HB8_ARCHIE, FLAG_HIDE_GRUNT_2_SLATEPORT_HARBOR
    h_removeobject HB8_SUB, FLAG_HIDE_SUBMARINE_SHADOW_SLATEPORT_HARBOR
    h_setvar VAR_SLATEPORT_HARBOR_STATE, 2
    h_call_if_eq HB8_POS, 0, L_HB8_Approach0
    h_call_if_eq HB8_POS, 1, L_HB8_Approach1
    h_call_if_eq HB8_POS, 2, L_HB8_Approach
    h_call_if_eq HB8_POS, 3, L_HB8_Approach
    h_msgbox_actor T_SternWhySteal, HB8_STERN       // Capt. Stern: Why... Why would Team Aqua steal my Submarine Explorer 1? ...
    h_closemessage
    h_setflag FLAG_HIDE_GRUNT_1_BLOCKING_HIDEOUT    // the Lilycove Hideout's door guards leave
    h_setflag FLAG_HIDE_GRUNT_2_BLOCKING_HIDEOUT
    h_release

L_HB8_Approach0:                        // SlateportCity_Harbor_EventScript_SternApproachPlayer0
    h_applymovement HB8_STERN, Mv_HB8_Approach0
    h_waitmovement
    h_applymovement 255, Mv_HB8_PlayerFaceDown
    h_waitmovement
    VMReturn
L_HB8_Approach1:                        // SternApproachPlayer1
    h_applymovement HB8_STERN, Mv_HB8_Approach1
    h_waitmovement
    h_applymovement 255, Mv_HB8_PlayerFaceRight
    h_waitmovement
    VMReturn
L_HB8_Approach:                         // SternApproachPlayer (triggers 2 and 3)
    h_applymovement HB8_STERN, Mv_HB8_Approach
    h_waitmovement
    h_applymovement 255, Mv_HB8_PlayerFaceRight
    h_waitmovement
    VMReturn

    .balign 4, 0
Mv_HB8_PlayerWalkUp:
    walk_up
    step_end
    .balign 4, 0
Mv_HB8_FaceDown:
    walk_in_place_fastest_down
    step_end
    .balign 4, 0
Mv_HB8_PlayerFaceUp:
    walk_in_place_fastest_up
    step_end
    .balign 4, 0
Mv_HB8_PlayerFaceDown:
    walk_in_place_fastest_down
    step_end
    .balign 4, 0
Mv_HB8_PlayerFaceRight:
    walk_in_place_fastest_right
    step_end
    .balign 4, 0
Mv_HB8_BoardSub:                        // SlateportCity_Harbor_Movement_EvilTeamBoardSub
    delay_16 2
    jump_up
    set_invisible
    step_end
    .balign 4, 0
Mv_HB8_SubmarineExit:                   // SlateportCity_Harbor_Movement_SubmarineExit (the shadow leaves to the east)
    delay_16 4
    walk_right 3
    walk_fast_right 6
    step_end
    .balign 4, 0
Mv_HB8_Approach0:                       // SlateportCity_Harbor_Movement_SternApproachPlayer0
    walk_left 4
    walk_up
    step_end
    .balign 4, 0
Mv_HB8_Approach1:                       // SternApproachPlayer1
    walk_left 2
    walk_up
    walk_left
    step_end
    .balign 4, 0
Mv_HB8_Approach:                        // SternApproachPlayer
    walk_left 3
    step_end
    .balign 4, 0
