// Emerald's Slateport City: Scott outside the Museum and the three extra people of the queue (emerald_ch0_3, 2026-10-12;
// notes/EMERALD_STORY.md Ch3). Bodies included at the end of the bodies of scenes/SlateportCity.inc in an Emerald build only; their
// entries 29-32 (last, under #ifdef HOENN_EMERALD in the entry part) exist in the Emerald build once converter/gen_map_content.py has
// been run in Emerald mode (S0-1), which also moves the zone's generated people after them. Source: pokeemerald
// data/maps/SlateportCity/scripts.inc (ScottScene, AquaGrunt9-11).
//
//  29 Em_SC_ScottScene: OnFrame while VAR_SLATEPORT_OUTSIDE_MUSEUM_STATE is 1 (the Museum 2F scene sets it, 0022_room_...). Coming out
//     of the Museum the player meets Scott, who walks over from the west: "I just saw Team Aqua run away... you drove them away?",
//     "Maybe, just maybe, this Trainer...", "Let's register each other" (a plain message with the register jingle, decision 3A),
//     "Be seeing you!" and walks west. VAR_SCOTT_STATE +1. Emerald then lets Scott wait at the Battle Tent door for a second scene
//     (VAR_SLATEPORT_OUTSIDE_MUSEUM_STATE 2): the tent is closed (decision 2), so the state goes to 3 at once and Scott is gone.
//  30-32 the queue's other Team Aqua grunts: 30 (26, 27) reads the sign for you, 31 (28, 27) grumbles (a sign-style line),
//     32 (25, 27) dreams of a hot spring. Sapphire's queue has the first eight; the Aqua flag is the same (FLAG_HIDE_EVIL_TEAM_SLATEPORT).
// Objects: data/story/emerald/e_ch3.json (Scott uid 191, grunts uid 140-142). Zone tiles = pokeemerald tiles + (248, 320).
// Text (src/text/scenes/emerald/SlateportCity.txt, appended after Sapphire's 56 lines): 56 YouDroveTeamAquaAway, 57 MaybeThisTrainer,
// 58 LetsRegisterEachOther, 59 RegisteredScott, 60 KeepEyeOnTrainers, 61 WhatDoYouWant, 62 IllReadSignForYou, 63 SaysSomething...,
// 64 ShouldveBroughtMyGameBoy, 65 HotSpringsAfterOperation.
#include "scenes/emerald/b1_common.inc"

#define EM_SC_SCOTT 191
#define EM_SC_GRUNT9 140
#define EM_SC_GRUNT10 141
#define EM_SC_GRUNT11 142
#define EM_SC_T_YouDrove 56
#define EM_SC_T_MaybeThisTrainer 57
#define EM_SC_T_LetsRegister 58
#define EM_SC_T_RegisteredScott 59
#define EM_SC_T_KeepEyeOn 60
#define EM_SC_T_WhatDoYouWant 61
#define EM_SC_T_IllRead 62
#define EM_SC_T_SaysSomething 63
#define EM_SC_T_GameBoy 64
#define EM_SC_T_HotSprings 65

Em_SC_ScottScene:                                // SlateportCity_EventScript_ScottScene (+ OnTransition's SetReadyForScottScene)
    h_lock
    h_setflag FLAG_HIDE_MAP_NAME_POPUP
    PlayerGetGPos 0x8020, 0x8021                 // the player comes out of one of the Museum's two doors: x 30 or 31
    h_addobject EM_SC_SCOTT, FLAG_HIDE_SLATEPORT_CITY_SCOTT
    h_goto_if_eq 0x8020, SLATEPORT_X(30), L_Em_SC_ScottLeft
    ActorSetGPos EM_SC_SCOTT, SLATEPORT_X(23), 0, SLATEPORT_Z(27), 3
    VMJump L_Em_SC_ScottGo
L_Em_SC_ScottLeft:
    ActorSetGPos EM_SC_SCOTT, SLATEPORT_X(22), 0, SLATEPORT_Z(27), 3
L_Em_SC_ScottGo:
    h_applymovement 255, Mv_Em_SC_PlayerFaceScott
    h_applymovement EM_SC_SCOTT, Mv_Em_SC_ScottApproach
    h_waitmovement
    h_buffer_player
    h_msgbox_actor EM_SC_T_YouDrove, EM_SC_SCOTT         // Scott: Huh? I'm sure I met you somewhere before. ...
    h_closemessage
    h_applymovement EM_SC_SCOTT, Common_Movement_WalkInPlaceFastestLeft
    h_waitmovement
    h_delay 60
    h_msgbox_actor EM_SC_T_MaybeThisTrainer, EM_SC_SCOTT  // Scott: Hmm... Maybe, just maybe, this Trainer...
    h_applymovement EM_SC_SCOTT, Common_Movement_WalkInPlaceFastestRight
    h_waitmovement
    h_msgbox_actor EM_SC_T_LetsRegister, EM_SC_SCOTT      // Scott: All right! I think you're going to become a good friend. ...
    h_closemessage
    h_delay 30
    h_playfanfare MUS_REGISTER_MATCH_CALL
    h_msgbox_actor EM_SC_T_RegisteredScott, EM_SC_SCOTT   // Registered this Scott person in the PokéNav.
    h_waitfanfare
    h_closemessage
    h_delay 30
    h_msgbox_actor EM_SC_T_KeepEyeOn, EM_SC_SCOTT         // Scott: What I'd like to do is tag along with you, ... Be seeing you, <player>!
    h_closemessage
    h_applymovement EM_SC_SCOTT, Mv_Em_SC_ScottExit
    h_waitmovement
    h_removeobject EM_SC_SCOTT, FLAG_HIDE_SLATEPORT_CITY_SCOTT
    h_clearflag FLAG_HIDE_MAP_NAME_POPUP
    h_setvar VAR_SLATEPORT_OUTSIDE_MUSEUM_STATE, 3   // (pokeemerald: 2, then the Battle Tent scene sets 3: the tent is closed)
    h_addvar VAR_SCOTT_STATE, 1
    h_release

Em_SC_Grunt9:                                    // SlateportCity_EventScript_AquaGrunt9: reads the sign for you
    c3_talk
    h_applymovement EM_SC_GRUNT9, Mv_Em_SC_Notice        // playse SE_PIN + "!" + Delay48
    h_waitmovement
    ParentActorMsg MSGFILE_SCRIPT, EM_SC_T_WhatDoYouWant, 0, 0
    LastKeyWait
    ActorMsgClose
    h_turnobject EM_SC_GRUNT9, 0                         // Common_Movement_FaceOriginalDirection (FACE_UP)
    h_applymovement EM_SC_GRUNT9, Mv_Em_SC_Delay
    h_waitmovement
    h_faceplayer                                         // Common_Movement_FacePlayer
    ParentActorMsg MSGFILE_SCRIPT, EM_SC_T_IllRead, 0, 0
    LastKeyWait
    ActorMsgClose
    h_turnobject EM_SC_GRUNT9, 0
    h_applymovement EM_SC_GRUNT9, Mv_Em_SC_Delay
    h_waitmovement
    ParentActorMsg MSGFILE_SCRIPT, EM_SC_T_SaysSomething, 0, 0
    LastKeyWait
    ActorMsgClose
    h_faceplayer
    h_applymovement EM_SC_GRUNT9, Mv_Em_SC_Delay
    h_waitmovement
    h_turnobject EM_SC_GRUNT9, 0
    h_release

Em_SC_Grunt10:                                   // SlateportCity_EventScript_AquaGrunt10 (MSGBOX_SIGN: he does not turn)
    h_msgbox_sign EM_SC_T_GameBoy

Em_SC_Grunt11:                                   // SlateportCity_EventScript_AquaGrunt11
    c3_say_turn_back EM_SC_T_HotSprings, EM_SC_GRUNT11, 0   // FACE_UP

    .balign 4, 0
Mv_Em_SC_PlayerFaceScott:                        // SlateportCity_Movement_PlayerFaceScott
    delay_16
    delay_8
    walk_in_place_fastest_left
    step_end
Mv_Em_SC_ScottApproach:
    walk_right 7
    step_end
Mv_Em_SC_ScottExit:
    walk_left 8
    step_end
Mv_Em_SC_Notice:
    emote_exclamation_mark
    delay_16 3
    step_end
Mv_Em_SC_Delay:                                  // SlateportCity_Movement_DelayAquaGrunt
    delay_16 2
    step_end
    .balign 4, 0
#include "common/movement.inc"
