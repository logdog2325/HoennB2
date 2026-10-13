// Navel Rock's summit and Ho-Oh (Emerald data/maps/NavelRock_Top/scripts.inc; events agent, 2026-10-07; notes/EVENTS.md).
// Included twice by the generated zone file (zone 233, a warp-only map floating in the dark like Sky Pillar's top):
// entries 1-2. Text: src/text/scenes/NavelRock_Top.txt. Story objects (data/story/events.json): Ho-Oh (uid 101, Black 2's
// own Ho-Oh overworld sprite 4379, hidden by FLAG_HIDE_HO_OH, in the sky at (12,4)) and the step trigger (12,10) on
// Black 2's temporary work 0x4001 (Emerald's VAR_TEMP_1) = 0. Not ported: the camera pan up and down (SpawnCameraObject;
// the camera stays on the player and Ho-Oh flies into view), LoopWingFlapSE, the shade weather; the hidden Sacred Ash
// at (12,9) (FLAG_HIDDEN_ITEM_NAVEL_ROCK_TOP_SACRED_ASH: Black 2's hidden items are global script entries; not placed).
#ifdef SCENE_ENTRIES
    ScriptEntry NT_Init                 // 1: NavelRock_Top_OnTransition (zone init)
    ScriptEntry NT_HoOh                 // 2: NavelRock_Top_EventScript_HoOh (step trigger (12,10), VAR_TEMP_1 0)
#else
#include "scenes/events_lib.inc"
#define NT_HO_OH 101

NT_Init:                                // NavelRock_Top_OnTransition
    h_setvar EV_TEMP, 1
    h_goto_if_unset FLAG_CAUGHT_HO_OH, L_NT_TryShow
    h_setflag FLAG_HIDE_HO_OH           // NavelRock_Top_EventScript_HideHoOh
    VMHalt
L_NT_TryShow:                           // NavelRock_Top_EventScript_TryShowHoOh
    h_goto_if_set FLAG_DEFEATED_HO_OH, L_NT_InitDone
    h_setvar EV_TEMP, 0
    h_clearflag FLAG_HIDE_HO_OH
L_NT_InitDone:
    VMHalt

NT_HoOh:                                // NavelRock_Top_EventScript_HoOh
    h_lock
    h_setvar EV_TEMP, 1
    h_applymovement NT_HO_OH, Mv_NT_HoOhAppear
    h_waitmovement
    h_delay 50
    h_waitse
    h_playmoncry SPECIES_HO_OH
    h_delay 30
    h_waitmoncry
    h_delay 60
    h_applymovement NT_HO_OH, Mv_NT_HoOhApproach
    h_waitmovement
    ev_legend_battle SPECIES_HO_OH, EV_HO_OH_LEVEL, NT_HO_OH, FLAG_HIDE_HO_OH, FLAG_CAUGHT_HO_OH, FLAG_DEFEATED_HO_OH, 0
    h_release

    .balign 4, 0
Mv_NT_HoOhAppear:                       // NavelRock_Top_Movement_HoOhAppear
    delay_16 2
    walk_in_place_down 4
    step_end
    .balign 4, 0
Mv_NT_HoOhApproach:                     // NavelRock_Top_Movement_HoOhApproach
    walk_down 5
    walk_in_place_down
    delay_16 2
    step_end
    .balign 4, 0
#endif
