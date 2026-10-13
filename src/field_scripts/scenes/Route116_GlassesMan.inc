// Route 116's lost-glasses man (Sapphire Route116_EventScript_150B8F; chapter Ch2's Route 116). He stands at Route 116
// (74,13), Route 116's zone 423: scenes/Route116.inc includes this file in both of its parts (one ScriptEntry in the
// SCENE_ENTRIES list, script 6; the body after #else, with `#define R116G_TEXT <n>` = the line of
// src/text/scenes/Route116.txt where these 5 lines of src/text/scenes/Route116_GlassesMan.txt start). data/story/ch2.json
// places him (uid 172, Sapphire object 22, FLAG_HIDE_LOST_GLASSES_MAN). (Until 2026-10-08 his tile was in Verdanturf
// Town's zone 120, a zone covering whole 32x32 cells, and scenes/VerdanturfTown.inc included this file: zone_edges.)
#ifdef SCENE_ENTRIES
    ScriptEntry R116G_GlassesMan    // Route116_EventScript_150B8F (chapter Ch2)
#else
#define R116G_T(n) (R116G_TEXT + (n))
#define R116G_MAN 172
#ifndef FLAG_HIDDEN_ITEM_BLACK_GLASSES
#define FLAG_HIDDEN_ITEM_BLACK_GLASSES 2868 // Black 2 hidden-item flag 2819 + n of converter/gen_hidden_items.py (n 49)
#endif

R116G_GlassesMan:
    h_lock
    SEPlay SEQ_SE_MESSAGE
    h_faceplayer
    h_checkitem ITEM_BLACK_GLASSES, 1, HLIB_TMP
    h_goto_if_eq HLIB_TMP, 1, L_R116G_HasGlasses
    h_goto_if_set FLAG_HIDDEN_ITEM_BLACK_GLASSES, L_R116G_NotAroundHere   // special FoundBlackGlasses
    h_msgbox R116G_T(0)             // I dropped my glasses... Can you help me find them?
    h_release
L_R116G_NotAroundHere:              // Route116_EventScript_150BBB
    h_msgbox R116G_T(3)             // Hmm... I can't find my glasses anywhere... Maybe they're not around here...
    h_closemessage
    VMJump L_R116G_Leave
L_R116G_HasGlasses:                 // Route116_EventScript_150BCA
    h_msgbox R116G_T(0)
    h_msgbox R116G_T(1)             // Those glasses! May I see them for a second?
    h_goto_if_set FLAG_HIDDEN_ITEM_BLACK_GLASSES, L_R116G_NotMine
    h_msgbox R116G_T(4)             // Hmm... These are Blackglasses. They're not what I'm looking for...
    h_release
L_R116G_NotMine:                    // Route116_EventScript_150BF4
    h_msgbox R116G_T(2)             // ...Maybe my glasses aren't around here...
    h_closemessage
L_R116G_Leave:                      // Route116_EventScript_150C03
    h_delay 20
    h_getplayerfacing HLIB_TMP      // VAR_FACING 4 (the player faces east): up first; else left
    h_goto_if_eq HLIB_TMP, 3, L_R116G_LeaveUp
    h_applymovement R116G_MAN, Mv_R116G_Leave
    h_waitmovement
    VMJump L_R116G_Gone
L_R116G_LeaveUp:
    h_applymovement R116G_MAN, Mv_R116G_LeaveUp
    h_waitmovement
L_R116G_Gone:
    h_removeobject R116G_MAN, FLAG_HIDE_LOST_GLASSES_MAN
    h_release

    .balign 4, 0
Mv_R116G_Leave:                     // Route116_Movement_150C4D
    walk_left 9
    step_end
Mv_R116G_LeaveUp:                   // Route116_Movement_150C57
    walk_up
    walk_left 9
    step_end
#endif
