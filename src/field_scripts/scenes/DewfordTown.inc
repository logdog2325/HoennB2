// Dewford Town's story (Sapphire data/maps/DewfordTown/scripts.inc; chapter Ch2, notes/STORY_PORTING.md). Included
// twice by the generated zone file of Dewford (zone 465): the entries below become scripts 1-6, the generated signs and
// the woman follow. Text: src/text/scenes/DewfordTown.txt. Story objects (uid 100 + Sapphire local id): Mr. Briney
// (102), the Old Rod fisherman (103), the trendy-phrase boy (105) in data/story/ch2.json; Mr. Briney's boat (object
// 4) has no Black 2 object (scenes/ch2_boat.inc). Map scripts: scenes/DewfordTown_init.inc.
#ifdef SCENE_ENTRIES
    ScriptEntry DT_Init                 // 1: DewfordTown_OnTransition (zone init)
    ScriptEntry DT_Briney               // 2: DewfordTown_EventScript_Briney
    ScriptEntry DT_OldRodFisherman      // 3: DewfordTown_EventScript_OldRodFisherman
    ScriptEntry DT_TrendyPhraseBoy      // 4: DewfordTown_EventScript_TrendyPhraseBoy
    ScriptEntry DT_ArriveFromRoute104   // 5: the landing of Route104_EventScript_14EFD5 (reserved by Route 104's boat)
    ScriptEntry DT_ArriveFromRoute109   // 6: the landing of Route109_EventScript_14F548 (reserved by Route 109's boat)
#else
#include "hoenn_key_items.h"
#include "scenes/ch2_boat.inc"
#define DT_BRINEY 102
#define DT_BOAT 104                     // Mr. Briney's boat (3D object, data/story/missing_objects.json)
#define DT_X 108                        // zone tile = Sapphire tile + (108, 420) (world.py offset of DewfordTown)
#define DT_Z 420

DT_Init:
    h_setflag FLAG_VISITED_DEWFORD_TOWN
    VMHalt

DT_Briney:
    h_lock
    SEPlay SEQ_SE_MESSAGE
    h_faceplayer
    h_goto_if_unset FLAG_DELIVERED_STEVEN_LETTER, L_DT_ReturnToPetalburgPrompt
    ParentActorMsg MSGFILE_SCRIPT, 0, 0, 0  // Mr. Briney: Ahoy! For you, I'll go out to sea anytime! ...where are we bound?
    ListMenu_AnchorTopRight 31, 6, 0, 1, HLIB_TMP   // multichoicedefault 21, 6, 0 (PETALBURG / SLATEPORT / CANCEL), 2, 0
    ListMenuAdd 20, 65535, 0
    ListMenuAdd 21, 65535, 1
    ListMenuAdd 22, 65535, 2
    ListMenuShow
    h_goto_if_eq HLIB_TMP, 0, L_DT_ChoosePetalburg
    h_goto_if_eq HLIB_TMP, 1, L_DT_ChooseSlateport
    h_msgbox 3                          // Mr. Briney: Just tell me whenever you want to set sail again.
    h_release
L_DT_ChoosePetalburg:
    h_msgbox 1                          // Mr. Briney: Petalburg, is it? Anchors aweigh!...
    h_closemessage
    VMJump L_DT_SailToPetalburg
L_DT_ChooseSlateport:
    h_msgbox 2                          // Mr. Briney: Slateport, is it? Anchors aweigh!...
    h_closemessage
    VMJump L_DT_SailToSlateport
L_DT_ReturnToPetalburgPrompt:
    h_yesno 4, HLIB_TMP                 // Mr. Briney: Have you delivered your Letter? ...sail back to Petalburg?
    h_goto_if_yes HLIB_TMP, L_DT_SailBackToPetalburg
    h_msgbox 5                          // Mr. Briney: Then you go on and deliver the Letter. I'll be waiting.
    h_release
L_DT_SailBackToPetalburg:
    h_msgbox 6                          // Mr. Briney: Petalburg it is, then! ...
    h_closemessage

// DewfordTown_EventScript_SailToPetalburg (EventScript_BackupMrBrineyLocation: see 1006_room_Route104_MrBrineysHouse.s)
L_DT_SailToPetalburg:
    h_applymovement DT_BRINEY, Mv_DT_BrineyBoardBoat
    h_waitmovement
    h_removeobject DT_BRINEY, FLAG_HIDE_MR_BRINEY_DEWFORD_TOWN
    h_applymovement 255, Mv_DT_PlayerBoardBoat
    h_waitmovement
    ch2_hide_player
    h_clearflag FLAG_HIDE_MR_BRINEY_ROUTE104_HOUSE
    h_clearflag FLAG_HIDE_PEEKO_BRINEY_HOUSE
    h_clearflag FLAG_HIDE_MR_BRINEY_BOAT_ROUTE104
    h_setflag FLAG_HIDE_MR_BRINEY_BOAT_DEWFORD
    h_setvar VAR_BOARD_BRINEY_BOAT_ROUTE104_STATE, 2
    // warp MAP_ROUTE104_MR_BRINEYS_HOUSE, 255, 5, 4 (zone 503, room origin (1,1)); Sapphire lands at Route 104's
    // dock first (ExitBoatPetalburg) and warps in from there: here the crossing ends in the cottage (its script 5)
    ch2_sail 503, 5 + 1, 4 + 1, 1, 5
    h_release

L_DT_SailToSlateport:               // DewfordTown_EventScript_SailToSlateport
    h_applymovement DT_BRINEY, Mv_DT_BrineyBoardBoat
    h_waitmovement
    h_removeobject DT_BRINEY, FLAG_HIDE_MR_BRINEY_DEWFORD_TOWN
    h_applymovement 255, Mv_DT_PlayerBoardBoat
    h_waitmovement
    ch2_hide_player
    // to Route 109 (zone 365): the player lands on the boat's tile (21,26) (Route 109's arrival script 1)
    ch2_sail 365, 21 + 248, 26 + 380, 0, 1
    h_release

// Route104_EventScript_14EFD5 after the crossing (Ch2_R104BrineyBoat, scenes/Route104_ch2.inc, reserves this)
DT_ArriveFromRoute104:
    VMCall Sub_DT_BoatArrives
    ch2_land
    h_applymovement 255, Mv_DT_ExitBoatFromRoute104
    h_waitmovement
    VMCall Sub_DT_BrineyLands
    h_goto_if_set FLAG_DELIVERED_STEVEN_LETTER, L_DT_LandedAgain
    h_msgbox_actor 14, DT_BRINEY        // Mr. Briney: Ahoy! We've hit land in Dewford. ...that Letter to... Steven!
    h_release
L_DT_LandedAgain:
    h_msgbox_actor 15, DT_BRINEY        // Mr. Briney: Ahoy! We've hit land in Dewford! ...
    h_release

// Route109_EventScript_14F548 after the crossing (Route 109's boat, scenes/Route109.inc, reserves this)
DT_ArriveFromRoute109:
    VMCall Sub_DT_BoatArrives
    ch2_land
    h_applymovement 255, Mv_DT_ExitBoatFromRoute109
    h_waitmovement
    VMCall Sub_DT_BrineyLands
    h_setflag FLAG_HIDE_MR_BRINEY_BOAT_ROUTE109
    h_msgbox_actor 15, DT_BRINEY        // Mr. Briney: Ahoy! We've hit land in Dewford! ...
    h_release

Sub_DT_BoatArrives:                 // (script_check 2026-10-08) the boat is at the dock when the player lands on it
    h_goto_if_unset FLAG_HIDE_MR_BRINEY_BOAT_DEWFORD, L_DT_BoatThere    // (Sapphire's boat object sails in; the
    h_addobject DT_BOAT, FLAG_HIDE_MR_BRINEY_BOAT_DEWFORD               // flag alone showed it only after a reload)
L_DT_BoatThere:
    VMReturn

Sub_DT_BrineyLands:                 // setobjectxyperm 2, 12, 8 + addobject 2 + walk down, face left
    h_addobject DT_BRINEY, FLAG_HIDE_MR_BRINEY_DEWFORD_TOWN
    ActorSetGPos DT_BRINEY, 12 + DT_X, 0, 8 + DT_Z, 1
    h_applymovement DT_BRINEY, Mv_DT_BrineyExitBoat
    h_waitmovement
    VMReturn

DT_OldRodFisherman:
    h_lock
    SEPlay SEQ_SE_MESSAGE
    h_faceplayer
    h_goto_if_set FLAG_RECEIVED_OLD_ROD, L_DT_HowsFishing
    h_yesno 7, HLIB_TMP                 // This is a renowned fishing spot. Are you getting the itch to fish?
    h_goto_if_no HLIB_TMP, L_DT_NotGettingItchToFish
    h_msgbox 8                          // I hear you, and I like what you're saying! ...one of my fishing Rods.
    h_closemessage                  // (Black 2: the item script opens its own window)
    h_giveitem ITEM_OLD_ROD
    h_setflag FLAG_RECEIVED_OLD_ROD
    h_msgbox 9                          // And, as an added bonus, I'll even throw in a little fishing advice!...
    h_release
L_DT_NotGettingItchToFish:
    h_msgbox 10                         // Oh, is that so? That's too bad, then.
    h_release
L_DT_HowsFishing:
    ParentActorMsg MSGFILE_SCRIPT, 11, 0, 0  // Yo! How's your fishing?
    ListMenu_AnchorTopRight 31, 8, 0, 0, HLIB_TMP  // multichoice 20, 8, 50 (Excellent! / Not so hot), B ignored
    ListMenuAdd 23, 65535, 0
    ListMenuAdd 24, 65535, 1
    ListMenuShow
    h_goto_if_eq HLIB_TMP, 1, L_DT_FishingNotSoGood
    h_msgbox 12                         // Is that right! That's great! Haul in some big ones!
    h_release
L_DT_FishingNotSoGood:
    h_msgbox 13                         // Oh, hey, don't get down on yourself! ...fishing advice.
    h_release

// DewfordTown_EventScript_TrendyPhraseBoy. Sapphire's Dewford trend (an Easy Chat phrase, random at a new game, changed
// by the player through the Easy Chat screen) has no Black 2 equivalent (notes/STORY_COMMON.md: S_optional): the boy
// names one fixed phrase made of Sapphire's first words of the two groups (EC_GROUP_CONDITIONS "HOT", EC_GROUP_HOBBIES
// "IDOL": "Hot Idol", in the text file), and "No" goes on as if the Easy Chat screen were closed.
DT_TrendyPhraseBoy:
    h_lock
    SEPlay SEQ_SE_MESSAGE
    h_faceplayer
    h_yesno 16, HLIB_TMP                // ...have you heard about this new "Hot Idol"? ...the biggest happening thing?
    h_goto_if_no HLIB_TMP, L_DT_RejectTrendyPhrase
    h_msgbox 17                         // Yeah, absolutely right! "Hot Idol" is the definition of "in" right now.
    h_release
L_DT_RejectTrendyPhrase:
    h_msgbox 18                         // Hunh? It's not the hip and happening thing? ...what's "in"?
    h_msgbox 19                         // Well, if you hear of any happening new trends, come share them with me, okay?
    h_release

    .balign 4, 0
Mv_DT_PlayerBoardBoat:              // DewfordTown_Movement_PlayerBoardBoat
    walk_right
    walk_up
    step_end
Mv_DT_BrineyBoardBoat:              // DewfordTown_Movement_BrineyBoardBoat
    walk_up
    step_end
Mv_DT_ExitBoatFromRoute104:         // Route104_Movement_14F168
    walk_down
    walk_left
    walk_in_place_fastest_right
    step_end
Mv_DT_ExitBoatFromRoute109:         // Route109_Movement_14F670 (walk_down 2, walk_left: Sapphire's boat ends on (12,8)
    walk_down                       // too, so its walk crossed the pier's edge (12,10)/(11,10), solid there and here;
    walk_left                       // script_check 2026-10-08: one step down, as the Route 104 landing, so the player
    walk_in_place_fastest_right     // ends on the pier (11,9) facing Mr. Briney (12,9))
    step_end
Mv_DT_BrineyExitBoat:               // Route104_Movement_14F16F / Route109_Movement_14F67D
    walk_down
    walk_in_place_fastest_left
    step_end
#endif
