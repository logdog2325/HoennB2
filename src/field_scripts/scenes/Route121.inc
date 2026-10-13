// Route 121's story (Sapphire data/maps/Route121/scripts.inc; chapter Ch8 part 8b, ch8b agent 2026-10-07).
// converter/gen_map_content.py includes this file twice in the generated zone file 0950_auto_Route121.s: the entries
// below are scripts 1-2, the generated signs/people follow. Text: src/text/scenes/Route121.txt (T_* below).
// People and triggers: data/story/ch8b.json (outdoor uid = 100 + Sapphire local id): the three Aqua grunts (objects
// 12-14, FLAG_HIDE_GRUNTS_ROUTE121) and the four trigger tiles (25,5)-(25,8) of VAR_ROUTE121_STATE 0. The trainers
// (Walter, Tammy, Kate & Joy, Vanessa, Jessica) are Black 2 eye-contact trainers placed by the trainers patch; the
// woman at (29,14) and the two signs are generated. Sapphire's OnTransition (SetupEvilTeamGfxIds: the Aqua sprites are
// placed directly) needs nothing here.
#ifdef SCENE_ENTRIES
    ScriptEntry R121_Init               // 1: zone init (test start only, scenes/ch8b_test.inc)
    ScriptEntry R121_GruntsLeave        // 2: triggers (25,5)-(25,8) VAR_ROUTE121_STATE 0, Route121_EventScript_151B25
#else
#define T_GruntsLeave 0

#define R121_GRUNT1 112                 // Sapphire objects 12-14 (VAR_1: Aqua grunts, FLAG_HIDE_GRUNTS_ROUTE121)
#define R121_GRUNT2 113
#define R121_GRUNT3 114

R121_Init:
    RTCallGlobal 8297                       // the berry trees' new-day reset (converter/gen_hidden_items.py; missing_objects)
#ifdef HOENN_TEST_CH8B
    VMCall Test_Ch8bStart
#endif
    VMHalt

R121_GruntsLeave:                       // Route121_EventScript_151B25: the grunts head for Mt. Pyre
    h_lock
    h_msgbox_actor T_GruntsLeave, R121_GRUNT1       // Okay! We're to move out to Mt. Pyre!
    h_closemessage
    h_applymovement R121_GRUNT1, Mv_R121_GruntsWalk
    h_applymovement R121_GRUNT2, Mv_R121_GruntsWalk
    h_applymovement R121_GRUNT3, Mv_R121_GruntsWalk
    h_waitmovement
    h_removeobject R121_GRUNT1, FLAG_HIDE_GRUNTS_ROUTE121
    h_removeobject R121_GRUNT2, FLAG_HIDE_GRUNTS_ROUTE121
    h_removeobject R121_GRUNT3, FLAG_HIDE_GRUNTS_ROUTE121
    h_setvar VAR_ROUTE121_STATE, 1
    h_release

    .balign 4, 0
Mv_R121_GruntsWalk:                     // Route121_Movement_151B57/60/69: eight steps down
    walk_down 8
    step_end

#ifdef HOENN_TEST_CH8B
#include "scenes/ch8b_test.inc"
#endif
#endif
