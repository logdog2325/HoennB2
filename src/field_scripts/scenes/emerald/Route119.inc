// Emerald's Route 119: Scott after the rival's Fly scene (emerald_ch0_3, 2026-10-12; notes/EMERALD_STORY.md Ch7). Subroutine included at
// the end of the bodies of scenes/Route119.inc in an Emerald build only and called (VMCall) from L_R119_Gone, after the rival rode
// away (the scene's `delay 60`, then Scott): no new entry. Source: pokeemerald data/maps/Route119/scripts.inc
// (RivalExitScottArrive ... ScottExit1/2). Scott comes down from the north to the tile above the player (the rival's trigger
// C7_POS 1 = (25, 31), 2 = (26, 31)): "Hahahah! Way to go! I just passed by a Trainer riding a Bike... Are you off to Fortree Gym
// next?" (VAR_SCOTT_STATE +1), then walks back up. Object: data/story/emerald/e_ch7.json uid 193 (hidden by FLAG_HIDE_ROUTE_119_SCOTT, set
// at the new game). His Fortree call (pokenav, message) is left out with the Match Call (decision 3A). Zone tiles = pokeemerald
// tiles + (328, 60). Text: src/text/scenes/emerald/Route119.txt line 11 (ScottWayToGoBeSeeingYou).
#define EM_R119_SCOTT 193
#define EM_R119_T_Scott 11

Sub_Em_R119_Scott:                               // C7_POS: 1 or 2
    h_delay 60
    h_addobject EM_R119_SCOTT, FLAG_HIDE_ROUTE_119_SCOTT
    h_goto_if_eq C7_POS, 2, L_Em_R119_ScottPos2
    ActorSetGPos EM_R119_SCOTT, 328 + 27, 6, 60 + 25, 1       // SetScottPos1: (27, 25)
    VMJump L_Em_R119_ScottComes
L_Em_R119_ScottPos2:
    ActorSetGPos EM_R119_SCOTT, 328 + 28, 6, 60 + 25, 1       // SetScottPos2: (28, 25)
L_Em_R119_ScottComes:
    h_applymovement EM_R119_SCOTT, Mv_Em_R119_ScottEnter
    h_waitmovement
    h_addvar VAR_SCOTT_STATE, 1
    h_buffer_player
    h_msgbox_actor EM_R119_T_Scott, EM_R119_SCOTT    // Scott: Hahahah! Way to go, <player>! ... Well, I'll be seeing you!
    h_closemessage
    h_goto_if_eq C7_POS, 2, L_Em_R119_ScottExit2
    h_applymovement EM_R119_SCOTT, Mv_Em_R119_ScottExit1
    VMJump L_Em_R119_ScottLeft
L_Em_R119_ScottExit2:
    h_applymovement EM_R119_SCOTT, Mv_Em_R119_ScottExit2
L_Em_R119_ScottLeft:
    h_waitmovement
    h_removeobject EM_R119_SCOTT, FLAG_HIDE_ROUTE_119_SCOTT
    VMReturn

    .balign 4, 0
Mv_Em_R119_ScottEnter:                           // Route119_Movement_ScottEnter
    walk_down 4
    walk_left 2
    walk_down
    step_end
Mv_Em_R119_ScottExit1:
    walk_up
    walk_right 2
    walk_up 5
    step_end
Mv_Em_R119_ScottExit2:
    walk_up
    walk_right
    walk_up 5
    step_end
    .balign 4, 0
