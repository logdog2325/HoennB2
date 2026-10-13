// Route 109's story (Sapphire data/maps/Route109/scripts.inc; chapter Ch2, notes/STORY_PORTING.md). Included twice by
// the generated zone file of Route 109 (zone 365): the entries below become scripts 1-5, the generated signs/people
// follow. Text: src/text/scenes/Route109.txt. Story objects (uid 100 + Sapphire local id): Mr. Briney (102), the tuber
// boy (114) and girl (115), Zigzagoon (120) in data/story/ch2.json; Mr. Briney's boat (object 1) has no Black 2 object
// (scenes/ch2_boat.inc). Trainers: the trainers patch (eye contact).
#ifdef SCENE_ENTRIES
    ScriptEntry R109_ArriveFromDewford  // 1: the landing of DewfordTown_EventScript_SailToSlateport (reserved by it)
    ScriptEntry R109_Briney             // 2: Route109_EventScript_14F680
    ScriptEntry R109_TuberBoy           // 3: Route109_EventScript_14F70E
    ScriptEntry R109_TuberGirl          // 4: Route109_EventScript_14F725 (Soft Sand)
    ScriptEntry R109_Zigzagoon          // 5: Route109_EventScript_14F788
#else
#include "hoenn_key_items.h"
#include "scenes/ch2_boat.inc"
#define R109_BRINEY 102
#define R109_BOAT 101                   // Mr. Briney's boat (3D object, data/story/missing_objects.json)
#define R109_TUBERBOY 114
#define R109_TUBERGIRL 115
#define R109_X 248                      // zone tile = Sapphire tile + (248, 380) (world.py offset of Route109)
#define R109_Z 380

// DewfordTown_EventScript_SailToSlateport after the crossing (scenes/DewfordTown.inc reserves this)
R109_ArriveFromDewford:
    h_goto_if_unset FLAG_HIDE_MR_BRINEY_BOAT_ROUTE109, L_R109_BoatThere   // addobject 1 (the boat): it is at the dock
    h_addobject R109_BOAT, FLAG_HIDE_MR_BRINEY_BOAT_ROUTE109              // when the player lands on it (script_check)
L_R109_BoatThere:
    ch2_land
    h_applymovement 255, Mv_R109_ExitBoatSlateport
    h_waitmovement
    h_addobject R109_BRINEY, FLAG_HIDE_MR_BRINEY_ROUTE109   // setobjectxyperm 2, 21, 26 + addobject 2
    ActorSetGPos R109_BRINEY, 21 + R109_X, 0, 26 + R109_Z, 0
    h_applymovement R109_BRINEY, Mv_R109_BrineyExitBoat
    h_waitmovement
    h_setflag FLAG_HIDE_MR_BRINEY_BOAT_DEWFORD
    h_goto_if_set FLAG_DELIVERED_DEVON_GOODS, L_R109_LandedSlateport
    h_msgbox_actor 9, R109_BRINEY       // Mr. Briney: Ahoy! We've made land in Slateport! ...deliver the Devon Goods?
    h_release
L_R109_LandedSlateport:
    h_msgbox_actor 10, R109_BRINEY      // Mr. Briney: Ahoy! We've made land in Slateport! ...
    h_release

R109_Briney:
    h_lock
    SEPlay SEQ_SE_MESSAGE
    h_faceplayer
    h_goto_if_set FLAG_DELIVERED_DEVON_GOODS, L_R109_WhereAreWeBound
    h_yesno 0, HLIB_TMP                 // Mr. Briney: Aren't you delivering the Devon Goods? ...back to Dewford?
    h_goto_if_no HLIB_TMP, L_R109_DeliverGoods
    VMJump L_R109_DewfordItIs
L_R109_WhereAreWeBound:
    ParentActorMsg MSGFILE_SCRIPT, 3, 0, 0  // Mr. Briney: Ahoy! For you, I'll go out to sea anytime! ...where are we bound?
    ListMenu_AnchorTopRight 31, 8, 0, 1, HLIB_TMP   // multichoicedefault 21, 8, 14 (DEWFORD / CANCEL), 1, 0
    ListMenuAdd 11, 65535, 0
    ListMenuAdd 12, 65535, 1
    ListMenuShow
    h_goto_if_eq HLIB_TMP, 0, L_R109_DewfordItIs
    h_msgbox 4                          // Mr. Briney: You just tell me whenever you need to set sail again!
    h_release
L_R109_DeliverGoods:
    h_msgbox 2                          // Mr. Briney: Then you go on and deliver the Devon Goods. I'll be waiting.
    h_release
L_R109_DewfordItIs:
    h_msgbox 1                          // Mr. Briney: Dewford it is, then! Anchors aweigh!...
    h_closemessage
// Route109_EventScript_14F4D3 (EventScript_BackupMrBrineyLocation: see 1006_room_Route104_MrBrineysHouse.s)
    h_applymovement R109_BRINEY, Mv_R109_BrineyBoard
    h_waitmovement
    h_removeobject R109_BRINEY, FLAG_HIDE_MR_BRINEY_ROUTE109
    h_getplayerfacing HLIB_TMP          // VAR_FACING 1 (south) / 3 (west) / 4 (east)
    h_goto_if_eq HLIB_TMP, 2, L_R109_BoardFromRight
    h_goto_if_eq HLIB_TMP, 3, L_R109_BoardFromLeft
    h_applymovement 255, Mv_R109_PlayerBoardFromAbove
    VMJump L_R109_Board
L_R109_BoardFromRight:
    h_applymovement 255, Mv_R109_PlayerBoardFromRight
    VMJump L_R109_Board
L_R109_BoardFromLeft:
    h_applymovement 255, Mv_R109_PlayerBoardFromLeft
L_R109_Board:                       // Route109_EventScript_14F548
    h_waitmovement
    ch2_hide_player
    // to Dewford: the player lands on the boat's tile (12,8) (Dewford's arrival script 6, scenes/DewfordTown.inc)
    ch2_sail 465, 12 + 108, 8 + 420, 1, 6
    h_release

R109_TuberBoy:
    h_lock
    SEPlay SEQ_SE_MESSAGE
    h_faceplayer
    h_msgbox 5                          // Our sand castle's taking a long time to make.
    h_closemessage
    h_turnobject R109_TUBERBOY, 3       // Common_Movement_FaceOriginalDirection (MOVEMENT_TYPE_FACE_RIGHT)
    h_release

R109_TuberGirl:                     // (GetPlayerBigGuyGirlString: her lines do not use it)
    h_lock
    SEPlay SEQ_SE_MESSAGE
    h_faceplayer
    h_goto_if_set FLAG_RECEIVED_SOFT_SAND, L_R109_TuberGirlAgain
    h_msgbox 6                          // You can have this!
    h_closemessage                  // (Black 2: the item script opens its own window)
    h_giveitem ITEM_SOFT_SAND
    h_goto_if_eq HLIB_RESULT, 0, L_R109_BagFull
    h_closemessage
    h_turnobject R109_TUBERGIRL, 2      // (MOVEMENT_TYPE_FACE_LEFT)
    h_setflag FLAG_RECEIVED_SOFT_SAND
    h_release
L_R109_TuberGirlAgain:
    h_msgbox 7                          // We're going to get all the sand from the beach and make a big castle!...
    h_turnobject R109_TUBERGIRL, 2
    h_release
L_R109_BagFull:                     // Common_EventScript_ShowBagIsFull
    h_msgbox 13                         // Too bad! The Bag is full...
    h_release

R109_Zigzagoon:
    h_lock
    SEPlay SEQ_SE_MESSAGE
    h_faceplayer
    h_waitse
    h_playmoncry SPECIES_ZIGZAGOON
    h_msgbox 8                          // Zigzagoon: Guguu?
    h_waitmoncry
    h_release

    .balign 4, 0
Mv_R109_ExitBoatSlateport:          // DewfordTown_Movement_ExitBoatSlateport
    walk_up 3
    walk_in_place_fastest_down
    step_end
Mv_R109_BrineyExitBoat:             // DewfordTown_Movement_BrineyExitBoat
    walk_up 2
    step_end
Mv_R109_BrineyBoard:                // Route109_Movement_14F67B
    walk_down
    step_end
Mv_R109_PlayerBoardFromAbove:       // Route109_Movement_14F66D
    walk_down 2
    step_end
Mv_R109_PlayerBoardFromRight:       // Route109_Movement_14F678 (the player faces west)
    walk_left
    walk_down
    step_end
Mv_R109_PlayerBoardFromLeft:        // Route109_Movement_14F675 (the player faces east)
    walk_right
    walk_down
    step_end
#endif
