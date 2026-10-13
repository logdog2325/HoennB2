// Rusturf Tunnel: chapter Ch3's beat (Sapphire RusturfTunnel_EventScript_15C7D1 .. 15C9A5 and
// RusturfTunnel_EventScript_SetRusturfTunnelOpen: Rock Smash opens the tunnel, Wanda and her boyfriend, HM04). The
// Ch2 owner (0268_room_RusturfTunnel.s) includes this file twice: its ScriptEntry lines (#ifdef SCENE_ENTRIES) become
// scripts 9.. after Ch2's 1-8, the bodies follow (#else). Text: lines 9-11 of src/text/script/0153_room_RusturfTunnel.txt
// (after Ch2's 0-8). Written by ch3b, 2026-10-07.
//
// Sapphire starts the reunion the moment a rock is smashed: its Rock Smash field effect calls TryUpdateRusturfTunnelState
// (VAR_RUSTURF_TUNNEL_STATE 4/5 by the rock's hide flag) and the map's OnFrame table runs the scene, with VAR_TEMP_1 =
// where the player stood (step triggers (23,4) = 1, (25,4) = 2, (25,5) = 3). Black 2's rocks run its global Rock Smash
// script (10016, b2tools/patches/hm_free.py: ActorDelete only, no hook for a zone), so here the scene starts when the
// player steps into the gap: a step trigger on each rock's tile (VAR_RUSTURF_TUNNEL_STATE 3, after Ch2's grunt fled;
// data/story/ch3b.json). The player first steps back to the tile they smashed from, then Sapphire's scene plays:
//   rock 2 (24,4), smashed from the west (23,4)  -> Sapphire's VAR_TEMP_1 1;
//   rock 1 (24,5), smashed from the east (25,5)  -> VAR_TEMP_1 3 (VAR_TEMP_1 2, (25,4), is Wanda's own tile).
// The smashed rock's Sapphire hide flag is set too (FLAG_HIDE_RUSTURF_TUNNEL_ROCK_1/2: the rocks stay gone once the
// cave's rock entities carry those flags; today Black 2's rocks come back when the map reloads).
#ifdef SCENE_ENTRIES
    ScriptEntry RT3_ReunionWest     // 9: trigger (24,4): rock 2 smashed from the west (VAR_TEMP_1 1)
    ScriptEntry RT3_ReunionEast     // 10: trigger (24,5): rock 1 smashed from the east (VAR_TEMP_1 3)
#else
#define T_Shattered 9
#define T_StrengthHM 10
#define T_SeeYouAnytime 11

RT3_ReunionWest:
    h_lock
    h_applymovement 255, Mv_RT3_StepBackWest            // back to (23,4), still facing the gap
    h_waitmovement
    h_applymovement RT_BOYFRIEND, Common_Movement_WalkInPlaceFastestUp   // RusturfTunnel_EventScript_15C8CA
    h_waitmovement
    h_applymovement 255, Common_Movement_WalkInPlaceFastestDown
    h_waitmovement
    VMCall Sub_RT3_Notice
    h_msgbox_actor T_Shattered, RT_BOYFRIEND            // Wow! You shattered that boulder blocking the way. ...
    VMCall Sub_RT3_GiveStrength
    h_applymovement 255, Mv_RT3_PlayerMakeWayWest       // RusturfTunnel_EventScript_15C880
    h_applymovement RT_BOYFRIEND, Mv_RT3_BoyfriendToWandaWest
    h_waitmovement
    h_msgbox_actor T_SeeYouAnytime, RT_BOYFRIEND        // Wanda! Now I can see you anytime! ...
    h_closemessage
    h_applymovement RT_GIRLFRIEND, Mv_RT3_WandaLeave    // RusturfTunnel_EventScript_15C8F7
    h_applymovement RT_BOYFRIEND, Mv_RT3_BoyfriendLeaveWest
    h_waitmovement
    h_setflag FLAG_HIDE_RUSTURF_TUNNEL_ROCK_2
    VMJump L_RT3_TunnelOpen

RT3_ReunionEast:
    h_lock
    h_applymovement 255, Mv_RT3_StepBackEast            // back to (25,5), still facing the gap
    h_waitmovement
    VMCall Sub_RT3_Notice                               // (RusturfTunnel_EventScript_15C8EA: nothing to turn)
    h_msgbox_actor T_Shattered, RT_BOYFRIEND
    h_closemessage                                      // RusturfTunnel_EventScript_15C8EB
    h_applymovement RT_BOYFRIEND, Mv_RT3_StepRight
    h_waitmovement
    VMCall Sub_RT3_GiveStrength
    h_applymovement 255, Mv_RT3_PlayerMakeWayEast       // RusturfTunnel_EventScript_15C8AE
    h_applymovement RT_BOYFRIEND, Mv_RT3_BoyfriendToWandaEast
    h_waitmovement
    h_applymovement RT_GIRLFRIEND, Common_Movement_WalkInPlaceFastestDown
    h_waitmovement
    h_msgbox_actor T_SeeYouAnytime, RT_BOYFRIEND
    h_closemessage
    h_applymovement RT_GIRLFRIEND, Mv_RT3_WandaLeave    // RusturfTunnel_EventScript_15C91B
    h_applymovement RT_BOYFRIEND, Mv_RT3_BoyfriendLeaveEast
    h_waitmovement
    h_setflag FLAG_HIDE_RUSTURF_TUNNEL_ROCK_1
L_RT3_TunnelOpen:                   // RusturfTunnel_EventScript_SetRusturfTunnelOpen
    h_removeobject RT_BOYFRIEND, FLAG_HIDE_BOYFRIEND_RUSTURF_TUNNEL
    h_removeobject RT_GIRLFRIEND, FLAG_HIDE_GIRLFRIEND_RUSTURF_TUNNEL
    h_clearflag FLAG_HIDE_BOYFRIEND_WANDAS_HOUSE
    h_clearflag FLAG_HIDE_GIRLFRIEND_WANDAS_HOUSE
    h_setvar VAR_RUSTURF_TUNNEL_STATE, 6
    h_setflag FLAG_RUSTURF_TUNNEL_OPENED
    h_release

Sub_RT3_Notice:                     // RusturfTunnel_EventScript_15C92D: SE_PIN, "!", delay_48
    h_applymovement RT_BOYFRIEND, Mv_RT3_Notice
    h_waitmovement
    VMReturn

Sub_RT3_GiveStrength:               // giveitem ITEM_HM04_STRENGTH (Sapphire does not look at its result here)
    h_closemessage
    h_giveitem ITEM_HM04
    h_setflag FLAG_RECEIVED_HM04
    h_msgbox_actor T_StrengthHM, RT_BOYFRIEND           // That HM contains Strength. ...
    h_closemessage
    VMReturn

    .balign 4, 0
Mv_RT3_StepBackWest:
    lock_facing_direction
    walk_left
    unlock_facing_direction
    step_end
Mv_RT3_StepBackEast:
    lock_facing_direction
    walk_right
    unlock_facing_direction
    step_end
Mv_RT3_Notice:
    emote_exclamation_mark
    delay_16 3
    step_end
Mv_RT3_StepRight:                   // RusturfTunnel_Movement_15C98D
    walk_right
    step_end
Mv_RT3_PlayerMakeWayWest:           // RusturfTunnel_Movement_15C96A
    walk_left
    walk_in_place_fastest_right
    step_end
Mv_RT3_PlayerMakeWayEast:           // RusturfTunnel_Movement_15C96D
    walk_right
    walk_in_place_fastest_left
    step_end
Mv_RT3_BoyfriendToWandaWest:        // RusturfTunnel_Movement_15C98F
    walk_in_place_fast_up 2
    walk_fast_up
    walk_fast_right
    step_end
Mv_RT3_BoyfriendToWandaEast:        // RusturfTunnel_Movement_15C994
    walk_in_place_fast_right 2
    walk_fast_right
    walk_in_place_fastest_up
    step_end
Mv_RT3_WandaLeave:                  // RusturfTunnel_Movement_15C945 / 15C951
    walk_right 4
    walk_down 7
    step_end
Mv_RT3_BoyfriendLeaveWest:          // RusturfTunnel_Movement_15C973
    walk_right 5
    walk_down 7
    step_end
Mv_RT3_BoyfriendLeaveEast:          // RusturfTunnel_Movement_15C980
    walk_up
    walk_right 4
    walk_down 7
    step_end
#include "common/movement.inc"
#endif
