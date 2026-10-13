// Route 110's story (Sapphire data/maps/Route110/scripts.inc; chapter Ch3 part 3b, ch3b agent 2026-10-07).
// converter/gen_map_content.py includes this file twice in the generated zone file 0736_auto_Route110.s: the entries
// below are scripts 1-11, the generated signs/people follow. Text: src/text/scenes/Route110.txt (lines T_* below).
// People, signs and triggers: data/story/ch3b.json (outdoor uid = 100 + Sapphire local id). Map scripts:
// scenes/Route110_init.inc (zone init = script 1). Trainers: the trainers patch (eye contact). Not here:
// - the Trick House (optional block 3T) and the sign "Seaside Cycling Road" etc. (generated: simple signs);
// - Sapphire's Cycling Road challenge (VAR_CYCLING_CHALLENGE_STATE 1-3: ScrSpecial_BeginCyclingRoadChallenge,
//   FinishCyclingRoadChallenge, GetRecordedCyclingRoadResults count frames and bike collisions in C). Black 2 scripts
//   have no frame timer and no collision counter (field_commands.json: RTCGetTime gives hours and minutes only), so
//   the challenge never starts: VAR_CYCLING_CHALLENGE_STATE stays 0, the finish line triggers (28,92)/(29,92) are not
//   placed, the man at the south end always explains the rating (his state-0 line) and the record sign says that no
//   one has taken the challenge (its no-record line). Sapphire's savebgm MUS_CYCLING: Black 2 plays its own bicycle
//   music whenever the player rides.
#ifdef SCENE_ENTRIES
    ScriptEntry R110_Init               // 1: Route110_MapScript1_14F914 (zone init)
    ScriptEntry R110_Grunt2             // 2: object 23, Route110_EventScript_14F95C
    ScriptEntry R110_Grunt3             // 3: object 24, Route110_EventScript_14F972
    ScriptEntry R110_Grunt4             // 4: object 25, Route110_EventScript_14F988
    ScriptEntry R110_CyclingMan         // 5: object 21, Route110_EventScript_14FA53
    ScriptEntry R110_RivalLeft          // 6: trigger (33,56) VAR_ROUTE110_STATE 0, Route110_EventScript_14FD13
    ScriptEntry R110_RivalMiddle        // 7: trigger (34,56), Route110_EventScript_14FD1E
    ScriptEntry R110_RivalRight         // 8: trigger (35,56), Route110_EventScript_14FD29
    ScriptEntry R110_AquaSign           // 9: sign (15,25), Route110_EventScript_14F9EF ("Team Aqua Rulez!")
    ScriptEntry R110_RecordSign         // 10: sign (32,93), Route110_EventScript_14FA2E
#include "scenes/Route110_Grunt1.inc"   // 11: object 22 (7,83), Route110_EventScript_14F946 (until 2026-10-08 in Route 103's
                                        // zone 326 and its file: a zone covered whole cells; zone_edges)
#else
#include "scenes/ch3b_lib.inc"

#define T_Grunt2 0
#define T_Grunt3 1
#define T_Grunt4 2
#define T_CyclingRated 3
#define T_MayHi 4
#define T_MayReward 5
#define T_MayItemfinder 6
#define T_BrendanHey 7
#define T_BrendanReward 8
#define T_BrendanItemfinder 9
#define T_AquaSign 10
#define T_NoRecord 11
#define R110G1_TEXT 12                  // the first grunt's line (scenes/Route110_Grunt1.inc, Route110_Grunt1.txt)

#define R110_GRUNT2 123                 // Sapphire objects 23-25 (FLAG_HIDE_EVIL_TEAM_ROUTE110)
#define R110_GRUNT3 124
#define R110_GRUNT4 125
#define R110_RIVAL 128                  // object 28, RIVAL_GFX (FLAG_HIDE_RIVAL_ROUTE110)
#define R110_RIVAL_BIKE 129             // object 29, RIVAL_GFX: no Brendan/May bike sprite yet (FLAG_HIDE_RIVAL_ON_BIKE_ROUTE110)
#define R110_POS C3B_A                  // Sapphire VAR_0x8008: 1/2/3 = the player stepped on (33,56)/(34,56)/(35,56)
#define R110_X(x) (248+(x))             // Sapphire tile -> world tile (b2tools/world.py offset of Route110)
#define R110_Z(z) (220+(z))

R110_Init:                              // OnTransition: SetupEvilTeamGfxIds (Aqua models are placed directly),
    RTCallGlobal 8297                       // the berry trees' new-day reset (converter/gen_hidden_items.py; missing_objects)
    h_setup_rival_gfx                   // SetupRivalGfxId, SetupRivalOnBikeGfxId (the same stand-in)
#ifdef HOENN_TEST_CH3B
    VMCall Test_Ch3bStart
#endif
    VMHalt

// the Aqua grunts on the low road at (8-10,83) (until Capt. Stern's museum scene sets FLAG_HIDE_EVIL_TEAM_ROUTE110); they
// turn back up afterwards (Common_Movement_FaceOriginalDirection: MOVEMENT_TYPE_FACE_UP)
R110_Grunt2:
    c3_say_turn_back T_Grunt2, R110_GRUNT2, 0
R110_Grunt3:
    c3_say_turn_back T_Grunt3, R110_GRUNT3, 0
R110_Grunt4:
    c3_say_turn_back T_Grunt4, R110_GRUNT4, 0

R110_CyclingMan:                        // Route110_EventScript_14FA53 (GetPlayerAvatarBike 1 = Acro Bike: no Acro Bike
    h_lock                              // here, one bike; VAR_CYCLING_CHALLENGE_STATE is always 0, see above)
    SEPlay SEQ_SE_MESSAGE
    h_faceplayer
    h_msgbox T_CyclingRated             // This is Cycling Road. If you were to ride from Mauville to Slateport...
    h_release

// the rival on the way to Mauville (Route110_EventScript_14FD34)
R110_RivalLeft:
    h_setvar R110_POS, 1
    VMJump L_R110_Rival
R110_RivalMiddle:
    h_setvar R110_POS, 2
    VMJump L_R110_Rival
R110_RivalRight:
    h_setvar R110_POS, 3
L_R110_Rival:
    h_lock
    h_goto_if_girl L_R110_MusicBrendan
    h_playbgm MUS_ENCOUNTER_MAY
    VMJump L_R110_Notice
L_R110_MusicBrendan:
    h_playbgm MUS_ENCOUNTER_BRENDAN
L_R110_Notice:
    h_applymovement R110_RIVAL, Mv_R110_RivalNotice     // walk_in_place_fastest_down, "!", delay_48
    h_waitmovement
    h_delay 30
    h_goto_if_eq R110_POS, 2, L_R110_ApproachMiddle
    h_goto_if_eq R110_POS, 3, L_R110_ApproachRight
    h_applymovement R110_RIVAL, Mv_R110_ApproachLeft
    VMJump L_R110_Approached
L_R110_ApproachMiddle:
    h_applymovement R110_RIVAL, Mv_R110_ApproachMiddle
    VMJump L_R110_Approached
L_R110_ApproachRight:
    h_applymovement R110_RIVAL, Mv_R110_ApproachRight
L_R110_Approached:
    h_waitmovement
    h_buffer_player
    h_goto_if_girl L_R110_Brendan
    h_msgbox_actor T_MayHi, R110_RIVAL                  // May: Hi, <player>, long time no see! ...
    h_closemessage
    h_goto_if_eq VAR_STARTER_MON, 1, L_R110_May8
    h_goto_if_eq VAR_STARTER_MON, 2, L_R110_May2
    h_trainerbattle TRAINER_MAY_5                       // (in battle: "Yikes! You're better than I expected!")
    VMJump L_R110_MayWon
L_R110_May8:
    h_trainerbattle TRAINER_MAY_8
    VMJump L_R110_MayWon
L_R110_May2:
    h_trainerbattle TRAINER_MAY_2
L_R110_MayWon:                          // Route110_EventScript_14FE10
    h_buffer_player
    h_msgbox_actor T_MayReward, R110_RIVAL              // <player>, you've been busy training, too...
    h_closemessage
    h_giveitem ITEM_ITEMFINDER                          // (Sapphire does not look at giveitem's result here)
    h_buffer_player
    h_msgbox_actor T_MayItemfinder, R110_RIVAL          // That's an Itemfinder. ...
    VMJump L_R110_RivalLeaves
L_R110_Brendan:
    h_msgbox_actor T_BrendanHey, R110_RIVAL             // Brendan: Hey, <player>. So this is where you were. ...
    h_closemessage
    h_goto_if_eq VAR_STARTER_MON, 1, L_R110_Brendan8
    h_goto_if_eq VAR_STARTER_MON, 2, L_R110_Brendan2
    h_trainerbattle TRAINER_BRENDAN_5                   // (in battle: "Hmm... You're pretty good.")
    VMJump L_R110_BrendanWon
L_R110_Brendan8:
    h_trainerbattle TRAINER_BRENDAN_8
    VMJump L_R110_BrendanWon
L_R110_Brendan2:
    h_trainerbattle TRAINER_BRENDAN_2
L_R110_BrendanWon:                      // Route110_EventScript_14FE8A
    h_buffer_player
    h_msgbox_actor T_BrendanReward, R110_RIVAL          // <player>, you've trained without me noticing...
    h_closemessage
    h_giveitem ITEM_ITEMFINDER
    h_buffer_player
    h_msgbox_actor T_BrendanItemfinder, R110_RIVAL      // That's an Itemfinder. ...
L_R110_RivalLeaves:                     // Route110_EventScript_14FEB2
    h_closemessage
    // setobjectxyperm 29 to the walking rival's spot (33/34/35, 55), removeobject 28, addobject 29: Black 2 adds the
    // hidden bike rival at its entity tile (34,54) and moves it with ActorSetGPos (ground height 0 there)
    ActorGetGPos R110_RIVAL, C3B_X, C3B_Z
    h_removeobject R110_RIVAL, FLAG_HIDE_RIVAL_ROUTE110
    h_addobject R110_RIVAL_BIKE, FLAG_HIDE_RIVAL_ON_BIKE_ROUTE110
    ActorSetGPos R110_RIVAL_BIKE, C3B_X, 0, C3B_Z, 0
    h_delay 45
    h_goto_if_eq R110_POS, 2, L_R110_RideMiddle
    h_applymovement R110_RIVAL_BIKE, Mv_R110_RideAway
    VMJump L_R110_Ridden
L_R110_RideMiddle:
    h_applymovement R110_RIVAL_BIKE, Mv_R110_RideAwayMiddle
L_R110_Ridden:
    h_waitmovement
    h_removeobject R110_RIVAL_BIKE, FLAG_HIDE_RIVAL_ON_BIKE_ROUTE110
    h_setvar VAR_ROUTE110_STATE, 1
    h_fadedefaultbgm                    // savebgm 0, fadedefaultbgm
    h_release

R110_AquaSign:                          // Route110_EventScript_14F9EF (the generator skips it: {EVIL_TEAM} in its text)
    h_msgbox_sign T_AquaSign

R110_RecordSign:                        // Route110_EventScript_14FA2E: GetRecordedCyclingRoadResults is always FALSE
    h_lock                              // (no challenge, see above) -> Route110_EventScript_14FA49
    SEPlay SEQ_SE_MESSAGE
    h_msgbox_info T_NoRecord            // The Best Record To Date... No one seems to have taken the challenge...
    h_release

    .balign 4, 0
Mv_R110_RivalNotice:                    // Common_Movement_WalkInPlaceFastestDown, _ExclamationMark, _Delay48
    walk_in_place_fastest_down
    emote_exclamation_mark
    delay_16 3
    step_end
Mv_R110_ApproachLeft:                   // Route110_Movement_14FF6E
    walk_down
    walk_left
    walk_in_place_fastest_down
    step_end
Mv_R110_ApproachMiddle:                 // Route110_Movement_14FF72
    walk_down
    step_end
Mv_R110_ApproachRight:                  // Route110_Movement_14FF74
    walk_down
    walk_right
    walk_in_place_fastest_down
    step_end
Mv_R110_RideAway:                       // Route110_Movement_14FF78 / 14FF89
    walk_fast_up 7
    step_end
Mv_R110_RideAwayMiddle:                 // Route110_Movement_14FF80 (Sapphire's list ends with one walk_fast_down)
    walk_fast_up 7
    walk_fast_down
    step_end

#include "scenes/Route110_Grunt1.inc"
#include "scenes/ch3b_test.inc"
#endif
