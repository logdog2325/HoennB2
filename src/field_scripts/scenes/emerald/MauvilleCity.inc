// Emerald's Mauville City: Scott after the Wally battle (emerald_ch0_3, 2026-10-12; notes/EMERALD_STORY.md Ch3). Subroutine included at
// the end of the bodies of scenes/MauvilleCity.inc in an Emerald build only and called (VMCall) from L_MC_DefeatedWally, right
// after Wally and his uncle have gone: no new entry, no new numbering. Source: pokeemerald data/maps/MauvilleCity/scripts.inc
// (MauvilleCity_EventScript_DefeatedWally ... ScottExitNorth/East). Scott walks up from the south to the player's side (where
// the player stood for the battle: facing east = 3, else north), says "I was watching that match! ... I'll be cheering for you!"
// (VAR_SCOTT_STATE +1) and walks west. Object: data/story/emerald/e_ch3.json uid 192 (hidden by FLAG_HIDE_MAUVILLE_CITY_SCOTT, set
// at the new game), standing at (12, 14); the east case starts him at (12, 13). Zone tiles = pokeemerald tiles + (248, 200).
// Text: src/text/scenes/emerald/MauvilleCity.txt line 20 (ScottYouDidntHoldBack).
#define EM_MC_SCOTT 192
#define EM_MC_T_Scott 20

Sub_Em_MC_Scott:                                 // C3B_A: 3 = the player stood west of Wally (east case), else north
    h_goto_if_eq C3B_A, 3, L_Em_MC_ScottEast
    h_addobject EM_MC_SCOTT, FLAG_HIDE_MAUVILLE_CITY_SCOTT
    h_applymovement EM_MC_SCOTT, Mv_Em_MC_ScottApproachNorth
    h_waitmovement
    VMJump L_Em_MC_ScottTalk
L_Em_MC_ScottEast:                               // MauvilleCity_EventScript_ScottApproachPlayerEast: setobjectxyperm (12, 13)
    h_addobject EM_MC_SCOTT, FLAG_HIDE_MAUVILLE_CITY_SCOTT
    ActorSetGPos EM_MC_SCOTT, MC_X(12), 0, MC_Z(13), 0
    h_applymovement EM_MC_SCOTT, Mv_Em_MC_ScottApproachEast
    h_waitmovement
L_Em_MC_ScottTalk:
    h_applymovement 255, Common_Movement_WalkInPlaceFastestDown
    h_waitmovement
    h_buffer_player
    h_msgbox_actor EM_MC_T_Scott, EM_MC_SCOTT    // Scott: Hehe... I was watching that match! ... I'll be cheering for you!
    h_closemessage
    h_addvar VAR_SCOTT_STATE, 1
    h_goto_if_eq C3B_A, 3, L_Em_MC_ExitEast
    h_applymovement 255, Mv_Em_MC_PlayerWatchExitNorth
    h_applymovement EM_MC_SCOTT, Mv_Em_MC_ScottExitNorth
    VMJump L_Em_MC_ScottGone
L_Em_MC_ExitEast:
    h_applymovement 255, Mv_Em_MC_PlayerWatchExitEast
    h_applymovement EM_MC_SCOTT, Mv_Em_MC_ScottExitEast
L_Em_MC_ScottGone:
    h_waitmovement
    h_removeobject EM_MC_SCOTT, FLAG_HIDE_MAUVILLE_CITY_SCOTT
    VMReturn

    .balign 4, 0
Mv_Em_MC_ScottApproachNorth:                     // MauvilleCity_Movement_ScottApproachPlayerNorth
    walk_up 6
    walk_left 4
    walk_in_place_fastest_up
    step_end
Mv_Em_MC_ScottApproachEast:
    walk_up 5
    walk_left 5
    walk_up
    step_end
Mv_Em_MC_ScottExitNorth:
    walk_left 9
    step_end
Mv_Em_MC_ScottExitEast:
    walk_down
    walk_left 9
    step_end
Mv_Em_MC_PlayerWatchExitNorth:                   // ..._PlayerWatchScottExitNorth
    delay_16
    walk_in_place_fastest_left
    step_end
Mv_Em_MC_PlayerWatchExitEast:
    delay_16 2
    walk_in_place_fastest_left
    step_end
    .balign 4, 0
