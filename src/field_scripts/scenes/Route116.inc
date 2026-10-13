// Route 116's story (Sapphire data/maps/Route116/scripts.inc; chapter Ch2, notes/STORY_PORTING.md). Included twice by
// the generated zone file of Route 116 (zone 423): the entries below become scripts 1-5, the generated signs follow.
// Text: src/text/scenes/Route116.txt. Story objects (uid 100 + Sapphire local id; the tunneler's second spot 171):
// data/story/ch2.json. Map scripts: scenes/Route116_init.inc. Trainers: the trainers patch (eye contact).
// The lost-glasses man (object 22, (74,13)): scenes/Route116_GlassesMan.inc (script 6; his tile was in Verdanturf's
// zone 120 while a zone covered whole 32x32 cells, and Verdanturf's file included it; every map has its own zone up to
// its edges since zone_edges 2026-10-08). Text lines 8-12: Route116_GlassesMan.txt's.
#ifdef SCENE_ENTRIES
    ScriptEntry R116_Init           // 1: Route116_MapScript1_150A37 (zone init)
    ScriptEntry R116_Tunneler       // 2: Route116_EventScript_150A49
    ScriptEntry R116_DevonEmployee  // 3: Route116_EventScript_150A7B (Repeat Ball, after the goods reach Slateport)
    ScriptEntry R116_Briney         // 4: Route116_EventScript_150B5D
    ScriptEntry R116_BrineyTrigger  // 5: Route116_EventScript_150B6E (47,9), VAR_ROUTE116_STATE 1
#include "scenes/Route116_GlassesMan.inc"   // 6: the lost-glasses man (object 22, (74,13))
#else
#define R116_BRINEY 111             // Sapphire object 11 (FLAG_HIDE_BRINEY_ROUTE116)
#define R116_EMPLOYEE 119           // object 19 (FLAG_HIDE_DEVON_EMPLOYEE_ROUTE116)
#define FLAG_R116_TUNNELER_MOVED 0x58   // map-local flags (reset on every zone change): the tunneler (object 21)
#define FLAG_R116_TUNNELER_AWAY 0x59    // stands at (38,9) (uid 121) or, once the goods are recovered, (41,10) (uid 171)
#define R116G_TEXT 8                    // Route116_GlassesMan.txt's 5 lines (src/text/scenes/Route116.txt 8-12)

// OnTransition: call_if_set FLAG_RECOVERED_DEVON_GOODS -> setobjectxyperm 21, 41, 10. Black 2 has one NPC per spot,
// each hidden by a local flag set here (and both by Sapphire's FLAG_HIDE_TUNNER_DIGGER_ROUTE116).
R116_Init:
    RTCallGlobal 8297                       // the berry trees' new-day reset (converter/gen_hidden_items.py; missing_objects)
    h_goto_if_unset FLAG_RECOVERED_DEVON_GOODS, L_R116_TunnelerAtDoor
    h_setflag FLAG_R116_TUNNELER_MOVED
    h_goto_if_set FLAG_HIDE_TUNNER_DIGGER_ROUTE116, L_R116_TunnelerAway
    VMHalt
L_R116_TunnelerAtDoor:
    h_setflag FLAG_R116_TUNNELER_AWAY
    h_goto_if_unset FLAG_HIDE_TUNNER_DIGGER_ROUTE116, L_R116_InitDone
    h_setflag FLAG_R116_TUNNELER_MOVED
L_R116_TunnelerAway:
    h_setflag FLAG_R116_TUNNELER_AWAY
L_R116_InitDone:
    VMHalt

R116_Tunneler:
    h_lock
    SEPlay SEQ_SE_MESSAGE
    h_faceplayer
    h_goto_if_set FLAG_RECOVERED_DEVON_GOODS, L_R116_TunnelerBack
    h_goto_if_set FLAG_DEVON_GOODS_STOLEN, L_R116_TunnelerGoon
    h_msgbox 1                      // Nnn... Roar! I want to dig that tunnel!
    h_release
L_R116_TunnelerBack:
    h_msgbox 3                      // That goofy goon hightailed it out of the tunnel!
    h_release
L_R116_TunnelerGoon:
    h_msgbox 2                      // Nnn... Roar! What's going on?...
    h_release

R116_DevonEmployee:
    h_lock
    SEPlay SEQ_SE_MESSAGE
    h_faceplayer
    h_goto_if_set FLAG_MET_DEVON_EMPLOYEE, L_R116_EmployeeAgain
    h_msgbox 4                      // Oh! It's you! You're that person who not only helped me in Petalburg Woods...
    VMJump L_R116_GiveRepeatBall
L_R116_EmployeeAgain:
    h_msgbox 7                      // As a token of our appreciation for your delivering our package...
L_R116_GiveRepeatBall:              // Route116_EventScript_150A94
    h_setflag FLAG_MET_DEVON_EMPLOYEE
    h_closemessage                  // (Black 2: the item script opens its own window)
    h_giveitem ITEM_REPEAT_BALL
    h_goto_if_eq HLIB_RESULT, 0, L_R116_BagFull
    h_msgbox 5                      // Our new Poké Ball will be available at the Pokémon Mart in Rustboro...
    h_closemessage
    h_getplayerfacing HLIB_TMP      // VAR_FACING 4 (the player faces east) -> down first; else left
    h_goto_if_eq HLIB_TMP, 3, L_R116_EmployeeLeaveDown
    h_applymovement R116_EMPLOYEE, Mv_R116_EmployeeLeave
    h_waitmovement
    VMJump L_R116_EmployeeGone
L_R116_EmployeeLeaveDown:
    h_applymovement R116_EMPLOYEE, Mv_R116_EmployeeLeaveDown
    h_waitmovement
L_R116_EmployeeGone:
    h_removeobject R116_EMPLOYEE, FLAG_HIDE_DEVON_EMPLOYEE_ROUTE116
    h_clearflag FLAG_HIDE_EMPLOYEE_DEVON_CORP_3F
    h_setflag FLAG_RECEIVED_REPEAT_BALL
    h_release
L_R116_BagFull:
    h_msgbox 6                      // Your Bag is jam-packed. I can't give you this Repeat Ball.
    h_release

R116_Briney:
    h_lock
    SEPlay SEQ_SE_MESSAGE
    h_faceplayer
    h_msgbox 0                      // Ohhh, what am I to do? ...The scoundrel made off with my darling Peeko!
    h_setvar VAR_ROUTE116_STATE, 2
    h_release

R116_BrineyTrigger:
    h_lock
    h_applymovement R116_BRINEY, Common_Movement_WalkInPlaceFastestRight
    h_applymovement 255, Common_Movement_WalkInPlaceFastestLeft
    h_waitmovement
    h_msgbox_actor 0, R116_BRINEY
    h_setvar VAR_ROUTE116_STATE, 2
    h_release

    .balign 4, 0
Mv_R116_EmployeeLeave:              // Route116_Movement_150B1C
    walk_left 8
    step_end
Mv_R116_EmployeeLeaveDown:          // Route116_Movement_150B25
    walk_down
    walk_left 9
    step_end
#include "scenes/Route116_GlassesMan.inc"
#include "common/movement.inc"
#endif
