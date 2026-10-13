// Mossdeep City, EMERALD ONLY (emerald_ch9_mirage 2026-10-12; pokeemerald data/maps/MossdeepCity/scripts.inc; chapter Ch9, builder B5).
// Included by scenes/MossdeepCity.inc under #ifdef HOENN_EMERALD, in the body part (its four entries are scripts 4-7 there). Text:
// src/text/scenes/emerald/MossdeepCity.txt (lines 6-10, converter/gen_emerald_ch9_text.py). People and triggers:
// data/story/emerald/e_ch9_mirage.json (uid = 200 + pokeemerald's local object number in this zone: the trainers patch holds 100 +).
// What happens: once Tate & Liza are beaten (the Gym's win sets VAR_MOSSDEEP_CITY_STATE 1) Maxie and four Magma grunts stand in the
// east of town; the first step on one of six tiles near them (pokeemerald's coord events, tiles of its own map) makes them walk off
// toward the Space Center (state 2, they are hidden by FLAG_HIDE_MOSSDEEP_CITY_TEAM_MAGMA). The Space Center is in the rooms
// (src/field_scripts/emerald/0670 / 0676). Scott stands at the south-east shore from the start and says his line (+1 VAR_SCOTT_STATE);
// the Sailor and the Pokefan F answer by whether Magma is gone (FLAG_RECEIVED_HM08 = pokeemerald's FLAG_RECEIVED_HM_DIVE: Steven's Dive).
// Black 2 gaps: none (the movement lists are pokeemerald's, its faster = Sapphire's fastest). The Pokefan F, the Sailor and the grunts
// are placed on pokeemerald's tiles in Emerald's world (data/story/emerald/e_ch9_mirage.json).
#define MD_EM_SAILOR 201
#define MD_EM_POKEFAN_F 203
#define MD_EM_GRUNT_1 210
#define MD_EM_GRUNT_2 211
#define MD_EM_GRUNT_3 212
#define MD_EM_GRUNT_4 213
#define MD_EM_MAXIE 214
#define MD_EM_SCOTT 216
#define MD_T_SpaceCenterLetter 6        // MossdeepCity_Text_SpaceCenterReceivedLetter
#define MD_T_LaunchingRockets 7         // MossdeepCity_Text_SpaceCenterLaunchingRockets
#define MD_T_TargetedByMagma 8          // MossdeepCity_Text_MossdeepTargetedByMagma
#define MD_T_FeelRelief 9               // MossdeepCity_Text_FeelReliefOnLand
#define MD_T_Scott 10                   // MossdeepCity_Text_ScottSomethingWrongWithTown

MD_EmMagmaEnter:                        // MossdeepCity_EventScript_TeamMagmaEnterSpaceCenter (lockall)
    h_lock
    h_applymovement MD_EM_MAXIE, Mv_MD_MaxieGestureToSpaceCenter
    h_waitmovement
    h_applymovement MD_EM_GRUNT_1, Mv_MD_GruntFaceSpaceCenter
    h_applymovement MD_EM_GRUNT_2, Mv_MD_GruntFaceSpaceCenter
    h_applymovement MD_EM_GRUNT_3, Mv_MD_GruntFaceSpaceCenter
    h_applymovement MD_EM_GRUNT_4, Mv_MD_GruntFaceSpaceCenter
    h_waitmovement
    h_applymovement MD_EM_MAXIE, Mv_MD_MaxieEnterSpaceCenter
    h_applymovement MD_EM_GRUNT_1, Mv_MD_Grunt1EnterSpaceCenter
    h_applymovement MD_EM_GRUNT_2, Mv_MD_Grunt2EnterSpaceCenter
    h_applymovement MD_EM_GRUNT_3, Mv_MD_Grunt3EnterSpaceCenter
    h_applymovement MD_EM_GRUNT_4, Mv_MD_Grunt4EnterSpaceCenter
    h_waitmovement
    h_removeobject MD_EM_MAXIE, FLAG_HIDE_MOSSDEEP_CITY_TEAM_MAGMA
    h_removeobject MD_EM_GRUNT_1, FLAG_HIDE_MOSSDEEP_CITY_TEAM_MAGMA
    h_removeobject MD_EM_GRUNT_2, FLAG_HIDE_MOSSDEEP_CITY_TEAM_MAGMA
    h_removeobject MD_EM_GRUNT_3, FLAG_HIDE_MOSSDEEP_CITY_TEAM_MAGMA
    h_removeobject MD_EM_GRUNT_4, FLAG_HIDE_MOSSDEEP_CITY_TEAM_MAGMA
    h_delay 30
    h_setvar VAR_MOSSDEEP_CITY_STATE, 2
    h_setflag FLAG_HIDE_MOSSDEEP_CITY_TEAM_MAGMA
    h_release

MD_EmScott:                             // MossdeepCity_EventScript_Scott (lock, faceplayer)
    c9_talk
    h_msgbox MD_T_Scott                 // Scott: <player>, feeling good? I'm doing great! ... there's something wrong about this town. ...
    h_closemessage
    h_getplayerfacing C9_A              // VAR_FACING: the player faces north (0) or east (3)
    h_call_if_eq C9_A, 0, L_MD_ScottExitNorth
    h_call_if_eq C9_A, 3, L_MD_ScottExitEast
    h_addvar VAR_SCOTT_STATE, 1
    h_removeobject MD_EM_SCOTT, FLAG_HIDE_MOSSDEEP_CITY_SCOTT
    h_release
L_MD_ScottExitNorth:                    // MossdeepCity_EventScript_ScottExitNorth
    h_applymovement 255, Mv_MD_PlayerWatchScottExit
    h_applymovement MD_EM_SCOTT, Mv_MD_ScottExitNorth
    h_waitmovement
    VMReturn
L_MD_ScottExitEast:                     // MossdeepCity_EventScript_ScottExitEast
    h_applymovement 255, Mv_MD_PlayerWatchScottExit
    h_applymovement MD_EM_SCOTT, Mv_MD_ScottExitEast
    h_waitmovement
    VMReturn

MD_EmSailor:                            // MossdeepCity_EventScript_Sailor (lock, faceplayer)
    c9_talk
    h_goto_if_set FLAG_RECEIVED_HM08, L_MD_SailorMagmaGone
    h_msgbox MD_T_TargetedByMagma       // I heard from a Sailor buddy that Team Aqua set up shop in Lilycove. ... Mossdeep's been targeted by that Team Magma! ...
    h_release
L_MD_SailorMagmaGone:                   // MossdeepCity_EventScript_SailorMagmaGone
    h_msgbox MD_T_FeelRelief            // I'm a Sailor, so the sea's obviously more important to me. ...
    h_release

MD_EmPokefanF:                          // MossdeepCity_EventScript_PokefanF (lock, faceplayer)
    c9_talk
    h_goto_if_set FLAG_RECEIVED_HM08, L_MD_PokefanFMagmaGone
    h_msgbox MD_T_SpaceCenterLetter     // The island's Space Center has been launching huge rockets. ... an uproar over a letter they received recently.
    h_release
L_MD_PokefanFMagmaGone:                 // MossdeepCity_EventScript_PokefanFMagmaGone
    h_msgbox MD_T_LaunchingRockets      // The island's Space Center has been launching huge rockets.
    h_release

    .balign 4, 0
Mv_MD_MaxieGestureToSpaceCenter:        // MossdeepCity_Movement_MaxieGestureToSpaceCenter
    delay_16
    face_right
    delay_16 4
    face_left
    delay_16 2
    step_end
    .balign 4, 0
Mv_MD_GruntFaceSpaceCenter:             // MossdeepCity_Movement_GruntFaceSpaceCenter
    face_right
    delay_16 3
    step_end
    .balign 4, 0
Mv_MD_MaxieEnterSpaceCenter:            // MossdeepCity_Movement_MaxieEnterSpaceCenter
    walk_down
    walk_right 2
    walk_down 3
    walk_right 7
    step_end
    .balign 4, 0
Mv_MD_Grunt1EnterSpaceCenter:           // MossdeepCity_Movement_Grunt1EnterSpaceCenter
    delay_16
    delay_8
    walk_down 3
    walk_right 3
    walk_down 3
    walk_right 7
    step_end
    .balign 4, 0
Mv_MD_Grunt2EnterSpaceCenter:           // MossdeepCity_Movement_Grunt2EnterSpaceCenter
    delay_16
    delay_8
    walk_down 2
    walk_right 3
    walk_down 3
    walk_right 7
    step_end
    .balign 4, 0
Mv_MD_Grunt3EnterSpaceCenter:           // MossdeepCity_Movement_Grunt3EnterSpaceCenter
    delay_16
    delay_8
    walk_down
    walk_right 3
    walk_down 3
    walk_right 7
    step_end
    .balign 4, 0
Mv_MD_Grunt4EnterSpaceCenter:           // MossdeepCity_Movement_Grunt4EnterSpaceCenter
    delay_16
    delay_8
    walk_right 3
    walk_down 3
    walk_right 7
    step_end
    .balign 4, 0
Mv_MD_PlayerWatchScottExit:             // MossdeepCity_Movement_PlayerWatchScottExit
    delay_16 2
    walk_in_place_fastest_left
    step_end
    .balign 4, 0
Mv_MD_ScottExitNorth:                   // MossdeepCity_Movement_ScottExitNorth
    walk_left 9
    step_end
    .balign 4, 0
Mv_MD_ScottExitEast:                    // MossdeepCity_Movement_ScottExitEast
    walk_down
    walk_left 9
    step_end
    .balign 4, 0
