// Faraway Island's forest and Mew (Emerald data/maps/FarawayIsland_Interior/scripts.inc; events agent, 2026-10-07;
// notes/EVENTS.md). Included twice by the generated zone file (zone 159, a warp-only map): entries 1-3. Text:
// src/text/scenes/FarawayIsland_Interior.txt. Mew: data/story/events.json (uid 101, Black 2's own Mew overworld sprite 4248,
// hidden by FLAG_HIDE_MEW, wandering in the tall grass).
// Emerald's Mew chase, the closest Black 2 way: Emerald moves Mew one step away from the player for each step the player
// takes (MOVEMENT_TYPE_COPY_PLAYER_OPPOSITE_IN_GRASS) and hides it while it stands in the long grass; Black 2 has
// neither (no copy-the-player move code is decoded, an actor can't hide by the tile it stands on), so Mew wanders in the
// grass field on its own (Black 2's wander move, a 6x6 area) and is always visible. The first sight is Emerald's: Mew
// spots you ("!"), runs three steps into the grass and turns round (it does not vanish). Talk to it to battle it.
// Not ported: SetMewAboveGrass / the grass sprite over Mew, the float-up hop before the battle (Mew jumps in place),
// HideMewWhenGrassCut (Black 2's Cut cuts no grass).
#ifdef SCENE_ENTRIES
    ScriptEntry FI_Init                 // 1: FarawayIsland_Interior_OnTransition (zone init)
    ScriptEntry FI_FindMew              // 2: FarawayIsland_Interior_OnFrame: VAR_TEMP_1 0 (map-script condition)
    ScriptEntry FI_Mew                  // 3: FarawayIsland_Interior_EventScript_Mew
#else
#include "scenes/events_lib.inc"
#define FI_MEW 101

FI_Init:                                // FarawayIsland_Interior_OnTransition
    h_setvar EV_TEMP, 1
    h_goto_if_set FLAG_CAUGHT_MEW, L_FI_InitDone
    h_goto_if_set FLAG_DEFEATED_MEW, L_FI_InitDone   // FarawayIsland_Interior_EventScript_TryShowMew
    h_clearflag FLAG_HIDE_MEW
    h_setvar EV_TEMP, 0
L_FI_InitDone:
    VMHalt

FI_FindMew:                             // FarawayIsland_Interior_EventScript_FindMew
    h_lock
    h_applymovement FI_MEW, Mv_FI_MewNotices      // playse SE_PIN, Common_Movement_ExclamationMark, Delay48
    h_waitmovement
    h_applymovement FI_MEW, Mv_FI_MewMoveAndHide  // FarawayIsland_Interior_Movement_MewMoveAndHide (without set_invisible)
    h_waitmovement
    h_setvar EV_TEMP, 1
    h_release

FI_Mew:                                 // FarawayIsland_Interior_EventScript_Mew
    h_lock
    h_faceplayer
    h_msgbox_actor 0, FI_MEW            // Myuu...
    h_waitse
    h_playmoncry SPECIES_MEW
    h_applymovement FI_MEW, Mv_FI_MewHop
    h_waitmovement
    h_delay 40
    h_waitmoncry
    h_closemessage
    ev_legend_battle SPECIES_MEW, EV_MEW_LEVEL, FI_MEW, FLAG_HIDE_MEW, FLAG_CAUGHT_MEW, FLAG_DEFEATED_MEW, 1
    h_release

    .balign 4, 0
Mv_FI_MewNotices:
    emote_exclamation_mark
    delay_16 3
    step_end
    .balign 4, 0
Mv_FI_MewMoveAndHide:
    walk_up 3
    walk_in_place_fast_down
    step_end
    .balign 4, 0
Mv_FI_MewHop:
    jump_in_place_down
    step_end
    .balign 4, 0
#endif
