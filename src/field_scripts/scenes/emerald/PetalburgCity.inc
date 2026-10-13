// Emerald's Petalburg City (emerald_ch0_3, 2026-10-12; notes/EMERALD_STORY.md Ch1 and Ch6). The bodies of the two Emerald-only
// story scripts, included at the end of the bodies of scenes/PetalburgCity.inc in an Emerald build only; their ScriptEntry lines
// (numbers 9 and 10, after Sapphire's 1-8) are the last two of the entry list under #ifdef HOENN_EMERALD, so they exist in the
// Emerald build once converter/gen_map_content.py has been run in Emerald mode (S0-1: it counts scene entries per version and
// numbers the zone's generated people after them). Sources: pokeemerald data/maps/PetalburgCity/scripts.inc.
//
//  9  Em_PB_Scott (Ch1): Scott0-3. Walking into the town from Route 102 over x = 4 (a 1x4 trigger, y 10-13, while
//     VAR_SCOTT_PETALBURG_ENCOUNTER is 0) Scott comes from the east on your row, asks "are you a Pokémon Trainer?", decides you
//     are a rookie, tells you he is looking for talented Trainers and leaves west. VAR_SCOTT_STATE 1.
//  10 Em_PB_WalkToWallysHouse (Ch6): OnFrame while VAR_PETALBURG_STATE is 4 (the Gym's scene sets it: Wally's father took the
//     player out of the Gym). The two walk to Wally's house (no door animation) and the room's arrival script gives Surf.
// Objects (data/story/emerald/e_ch1.json uid 190 Scott, e_ch6.json uid 120 Wally's father). Zone tiles = pokeemerald tiles +
// (88, 290). Text: src/text/scenes/emerald/PetalburgCity.txt lines 8-10 (Scott), Sapphire's 0-7 reworded where Emerald's differ.
#define EM_PB_X 88
#define EM_PB_Z 290
#define EM_PB_SCOTT 190
#define EM_PB_WDAD 120
#define EM_PB_T_AreYouATrainer 8
#define EM_PB_T_WellMaybeNot 9
#define EM_PB_T_LookingForTalent 10

Em_PB_Scott:                                     // PetalburgCity_EventScript_Scott0-3 + Scott
    h_lock
    PlayerGetGPos 0x8020, 0x8021                 // which of the four triggers: pokeemerald y 10-13
    h_copyvar 0x8008, 0x8021
    h_subvar 0x8008, 300                         // EM_PB_Z + 10: 0-3 = the row (setvar VAR_0x8008)
    h_addobject EM_PB_SCOTT, FLAG_HIDE_PETALBURG_CITY_SCOTT
    h_goto_if_eq 0x8008, 1, L_Em_PB_ScottRow1
    h_goto_if_eq 0x8008, 2, L_Em_PB_ScottRow2
    h_goto_if_eq 0x8008, 3, L_Em_PB_ScottRow3
    h_setvar 0x8008, 0                           // (each branch sets its row as a constant: the walk checkers then follow one row at a time)
    ActorSetGPos EM_PB_SCOTT, EM_PB_X + 13, 1, EM_PB_Z + 10, 2
    VMJump L_Em_PB_ScottCome
L_Em_PB_ScottRow1:
    h_setvar 0x8008, 1
    ActorSetGPos EM_PB_SCOTT, EM_PB_X + 13, 1, EM_PB_Z + 11, 2
    VMJump L_Em_PB_ScottCome
L_Em_PB_ScottRow2:
    h_setvar 0x8008, 2
    ActorSetGPos EM_PB_SCOTT, EM_PB_X + 13, 1, EM_PB_Z + 12, 2
    VMJump L_Em_PB_ScottCome
L_Em_PB_ScottRow3:
    h_setvar 0x8008, 3
    ActorSetGPos EM_PB_SCOTT, EM_PB_X + 13, 1, EM_PB_Z + 13, 2
L_Em_PB_ScottCome:                               // PetalburgCity_EventScript_Scott
    h_applymovement EM_PB_SCOTT, Mv_Em_PB_ScottStartWalkLeft
    h_waitmovement
    h_applymovement EM_PB_SCOTT, Mv_Em_PB_ScottNotice   // playse SE_PIN + "!" + Delay48
    h_waitmovement
    h_goto_if_ne 0x8008, 1, L_Em_PB_ScottApproachFull    // ScottApproachPlayer (left x4): on the player's row 11 while the gym boy
    h_goto_if_ne VAR_PETALBURG_STATE, 0, L_Em_PB_ScottApproachFull   // still stands at the west entrance (5,11) (state 0) Scott
    h_applymovement EM_PB_SCOTT, Mv_Em_PB_ScottApproachShort         // stops one tile short, as pokeemerald's blocked step does
    h_waitmovement
    VMJump L_Em_PB_ScottApproached
L_Em_PB_ScottApproachFull:
    h_applymovement EM_PB_SCOTT, Mv_Em_PB_ScottStartWalkLeft
    h_waitmovement
L_Em_PB_ScottApproached:
    h_applymovement 255, Common_Movement_WalkInPlaceFastestRight
    h_waitmovement
    h_setvar VAR_SCOTT_STATE, 1
    h_msgbox_actor EM_PB_T_AreYouATrainer, EM_PB_SCOTT      // Excuse me! Let me guess, from the way you're dressed, ...
    h_closemessage
    h_applymovement EM_PB_SCOTT, Common_Movement_WalkInPlaceFastestRight
    h_waitmovement
    h_delay 30
    h_msgbox_actor EM_PB_T_WellMaybeNot, EM_PB_SCOTT        // ... Well, maybe not. Your clothes aren't all that dirty. ...
    h_closemessage
    h_applymovement EM_PB_SCOTT, Common_Movement_WalkInPlaceFastestLeft
    h_waitmovement
    h_delay 30
    h_msgbox_actor EM_PB_T_LookingForTalent, EM_PB_SCOTT    // I'm roaming the land in search of talented Trainers. ...
    h_closemessage
    h_goto_if_eq 0x8008, 1, L_Em_PB_ScottExit1
    h_goto_if_eq 0x8008, 2, L_Em_PB_ScottExit2
    h_goto_if_eq 0x8008, 3, L_Em_PB_ScottExit3
    h_applymovement 255, Mv_Em_PB_PlayerWatchScottExit0
    h_applymovement EM_PB_SCOTT, Mv_Em_PB_ScottExit0
    VMJump L_Em_PB_ScottLeft
L_Em_PB_ScottExit1:
    h_applymovement 255, Mv_Em_PB_PlayerWatchScottExit1
    h_applymovement EM_PB_SCOTT, Mv_Em_PB_ScottExit1
    VMJump L_Em_PB_ScottLeft
L_Em_PB_ScottExit2:
    h_applymovement 255, Mv_Em_PB_PlayerWatchScottExit1   // (the same list as row 1)
    h_applymovement EM_PB_SCOTT, Mv_Em_PB_ScottExit1
    VMJump L_Em_PB_ScottLeft
L_Em_PB_ScottExit3:
    h_applymovement 255, Mv_Em_PB_PlayerWatchScottExit3
    h_applymovement EM_PB_SCOTT, Mv_Em_PB_ScottExit3
L_Em_PB_ScottLeft:
    h_waitmovement
    h_setvar VAR_SCOTT_PETALBURG_ENCOUNTER, 1
    h_removeobject EM_PB_SCOTT, FLAG_HIDE_PETALBURG_CITY_SCOTT
    h_release

Em_PB_WalkToWallysHouse:                         // PetalburgCity_EventScript_WalkToWallyHouse (OnFrame, VAR_PETALBURG_STATE 4)
    h_lock
    FadeInBlack                                  // (the Gym's scripted warp leaves the screen black)
    FadeWait
    h_setflag FLAG_HIDE_MAP_NAME_POPUP
    h_applymovement EM_PB_WDAD, Mv_Em_PB_WDadToHouse
    h_applymovement 255, Mv_Em_PB_PlayerToHouse
    h_waitmovement
    h_applymovement EM_PB_WDAD, Mv_Em_PB_WDadInside
    h_applymovement 255, Mv_Em_PB_PlayerInside
    h_waitmovement
    h_setflag FLAG_HIDE_PETALBURG_CITY_WALLYS_DAD
    h_clearflag FLAG_HIDE_MAP_NAME_POPUP
    h_fadedefaultbgm
    h_clearflag FLAG_DONT_TRANSITION_MUSIC
    // warp MAP_PETALBURG_CITY_WALLYS_HOUSE, 2, 4 (room tile + (1, 1)); the room's arrival script (entry 5 of 1000) plays the rest
    h_warp_scene 500, 3, 5, 3, 5
    h_release

    .balign 4, 0
Mv_Em_PB_ScottStartWalkLeft:
    walk_left 4
    step_end
Mv_Em_PB_ScottApproachShort:
    walk_left 3
    step_end
Mv_Em_PB_ScottNotice:
    emote_exclamation_mark
    delay_16 3
    step_end
Mv_Em_PB_ScottExit0:                             // PetalburgCity_Movement_ScottExit0..3 (Scott leaves west along the street)
    walk_down 2
    walk_left 11
    step_end
Mv_Em_PB_PlayerWatchScottExit0:
    delay_16
    walk_in_place_fastest_down
    delay_16 2
    delay_8
    walk_in_place_fastest_left
    step_end
Mv_Em_PB_ScottExit1:
    walk_down
    walk_left 11
    step_end
Mv_Em_PB_PlayerWatchScottExit1:
    delay_16
    walk_in_place_fastest_down
    delay_16
    delay_8
    walk_in_place_fastest_left
    step_end
Mv_Em_PB_ScottExit3:
    walk_up
    walk_left 11
    step_end
Mv_Em_PB_PlayerWatchScottExit3:
    delay_16
    walk_in_place_fastest_up
    delay_16
    delay_8
    walk_in_place_fastest_left
    step_end
Mv_Em_PB_WDadToHouse:                            // PetalburgCity_Movement_WalkToWallyHouseWallysDad
    delay_8
    walk_down 2
    walk_left 8
    walk_up 6
    step_end
Mv_Em_PB_PlayerToHouse:                          // ..._WalkToWallyHousePlayer
    delay_8
    walk_down 3
    walk_left 8
    walk_up 5
    step_end
Mv_Em_PB_WDadInside:                             // ..._WalkInsideHouseWallysDad
    walk_up
    set_invisible
    step_end
Mv_Em_PB_PlayerInside:
    walk_up 2
    step_end
    .balign 4, 0
