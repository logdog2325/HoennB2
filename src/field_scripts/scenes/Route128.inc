// Route 128's story (Sapphire data/maps/Route128/scripts.inc; chapter Ch10, ch10 agent 2026-10-07).
// converter/gen_map_content.py includes this file twice in the generated zone file of zone 230: the entries below are
// scripts 1-2, the generated signs follow. Text: src/text/scenes/Route128.txt (T_* below).
// People: data/story/ch10.json (outdoor uid = 100 + Sapphire local id): Steven 103 (FLAG_HIDE_STEVEN_ROUTE128), Archie 104
// (FLAG_HIDE_EVIL_LEADER_ROUTE128), Maxie 105 (FLAG_HIDE_OTHER_LEADER_ROUTE128). The five trainers (Isaiah, Katelyn, Alexa,
// Ruben, Wayne) and the three hidden Heart Scales are Black 2 eye-contact trainers / hidden-item signs placed by the
// converters. Sapphire's ON_TRANSITION (Common_EventScript_SetLegendaryWeather while FLAG_SYS_WEATHER_CTRL, the Evil Team
// gfx ids) needs nothing here: the weather is the `weather` patch's (common/legendary_weather.inc), the Aqua/Magma/Archie/
// Maxie models are placed directly. The ON_FRAME_TABLE entry (VAR_ROUTE128_STATE 1 = the scene after Seafloor Cavern) is
// the scene condition of scenes/Route128_init.inc.
// Black 2 gap: Steven arrives and leaves on his Skarmory (FLDEFF_NPCFLY_OUT); Black 2 has no such effect: he appears
// after a pause and walks in place, and disappears after the same pause (c10_fly_out).
// RUBY (ruby_scenes, 2026-10-08; pokeruby's .ifndef SAPPHIRE blocks of this map): the scene is the same with the other team: object 104 is the
// evil team's leader (Sapphire Archie, Ruby Maxie: the art of sprite code 353 is swapped by src/sprites/overworld/ruby/), 105 the other one, and Steven's
// "terrible" line is Ruby's (T_StevenTerrible, src/text/scenes/Route128.txt line 6 through the Ruby text layer). The one flow difference is Ruby's
// `special sub_807E25C; waitstate` after delay 20 (field_weather_effects.c task50_0807B6D4): the screen is lightened to white within six frames, then
// fades back over about 160 frames, while Groudon's sun scorches the road. Black 2: FadeOutWhiteQ + a slow FadeInWhite (below, #ifdef HOENN_RUBY).
#ifdef SCENE_ENTRIES
    ScriptEntry R128_Init               // 1: Route128_MapScript1_152126 (zone init: the test start only)
    ScriptEntry R128_Scene              // 2: Route128_EventScript_15213F (VAR_ROUTE128_STATE 1, a scene condition)
#else
#include "scenes/ch10_lib.inc"

#define T_ArchieWhatHappened 0
#define T_ArchieIOnlyWanted 1
#define T_MaxieDoYouUnderstand 2
#define T_MaxiePlayerLeaveThingsToUs 3
#define T_MaxieDefiesBelief 4
#define T_StevenWhatIsHappening 5
#define T_StevenTerrible 6
#define T_StevenGoingToSootopolis 7

#define R128_STEVEN 103                 // object 3
#define R128_ARCHIE 104                 // object 4 (the evil team's leader: Ruby Maxie)
#define R128_MAXIE 105                  // object 5 (the other leader: Ruby Archie)

R128_Init:                              // Route128_MapScript1_152126
#ifdef HOENN_TEST_CH10
    VMCall Test_Ch10Start               // test builds only (scenes/ch10_test.inc)
#endif
#if __has_include("common/legendary_weather.inc")
    h_call_if_set FLAG_SYS_WEATHER_CTRL, Common_SetLegendaryWeather     // (the `weather` patch does it for every zone)
#endif
    VMHalt

R128_Scene:                             // Route128_EventScript_15213F: Archie, Maxie and Steven after Kyogre woke (Ruby: Maxie, Archie and Steven after Groudon woke)
    c10_lock
    h_delay 20
#ifdef HOENN_RUBY
    FadeOutWhiteQ                       // special sub_807E25C / waitstate (Ruby only): the glare of the drought
    FadeWait
    FadeInWhite
    FadeWait
#endif
    h_applymovement R128_ARCHIE, Mv_R128_ArchieLooksAround
    h_waitmovement
    h_msgbox_actor T_ArchieWhatHappened, R128_ARCHIE       // Archie: What happened... What is this wretched scene... Did I...make a horrible mistake?
    h_applymovement R128_ARCHIE, Mv_R128_ArchieStepsBack
    h_waitmovement
    h_msgbox_actor T_ArchieIOnlyWanted, R128_ARCHIE        // I... I only wanted...
    h_closemessage
    h_applymovement R128_MAXIE, Mv_R128_MaxieComesLeft
    h_waitmovement
    h_applymovement R128_ARCHIE, Common_Movement_WalkInPlaceFastestUp
    h_waitmovement
    h_msgbox_actor T_MaxieDoYouUnderstand, R128_MAXIE      // Maxie: Do you understand now, Archie? ...
    h_closemessage
    h_applymovement R128_MAXIE, Mv_R128_MaxieComesRight
    h_waitmovement
    h_applymovement 255, Common_Movement_WalkInPlaceFastestUp
    h_waitmovement
    h_msgbox_actor T_MaxiePlayerLeaveThingsToUs, R128_MAXIE    // Maxie: <player>... We, Team Magma, had been pursuing Team Aqua ...
    h_closemessage
    h_applymovement R128_ARCHIE, Mv_R128_ArchieWalksLeft
    h_applymovement 255, Common_Movement_WalkInPlaceFastestLeft
    h_applymovement R128_MAXIE, Mv_R128_MaxieWalksLeft
    h_waitmovement
    h_msgbox_actor T_MaxieDefiesBelief, R128_MAXIE         // Maxie: This defies belief... A super-ancient Pokémon...
    h_closemessage
    h_delay 40
    h_applymovement R128_MAXIE, Mv_R128_MaxieLeaves
    h_applymovement R128_ARCHIE, Mv_R128_ArchieLeaves
    h_waitmovement
    h_removeobject R128_MAXIE, FLAG_HIDE_OTHER_LEADER_ROUTE128
    h_removeobject R128_ARCHIE, FLAG_HIDE_EVIL_LEADER_ROUTE128
    h_delay 100
    h_addobject R128_STEVEN, FLAG_HIDE_STEVEN_ROUTE128     // Steven flies in (Skarmory): appears here
    h_applymovement R128_STEVEN, Mv_R128_StevenSteps
    h_waitmovement
    h_applymovement 255, Common_Movement_WalkInPlaceFastestRight
    h_waitmovement
    h_msgbox_actor T_StevenWhatIsHappening, R128_STEVEN    // Steven: <player>! What is happening?
    h_closemessage
    h_applymovement R128_STEVEN, Mv_R128_StevenUp
    h_applymovement 255, Common_Movement_WalkInPlaceFastestUp
    h_waitmovement
    h_msgbox_actor T_StevenTerrible, R128_STEVEN           // This is terrible... If this doesn't stop, all Hoenn... No, the whole world will drown. ...
    h_applymovement R128_STEVEN, Common_Movement_WalkInPlaceFastestDown
    h_waitmovement
    h_msgbox_actor T_StevenGoingToSootopolis, R128_STEVEN  // <player>... I don't know what you intend to do, but don't do anything reckless. Okay. I'm going to Sootopolis.
    h_closemessage
    h_applymovement R128_STEVEN, Common_Movement_WalkInPlaceFastestDown
    h_waitmovement
    h_delay 50
    c10_fly_out R128_STEVEN, FLAG_HIDE_STEVEN_ROUTE128     // Steven flies off (the Skarmory effect: none in Black 2)
    h_setvar VAR_ROUTE128_STATE, 2
    h_release

    .balign 4, 0
Mv_R128_ArchieLooksAround:              // Route128_Movement_152271
    walk_fast_down
    walk_in_place_fastest_left
    delay_16
    walk_in_place_fastest_right
    delay_16
    delay_16
    walk_in_place_fastest_down
    step_end
    .balign 4, 0
Mv_R128_ArchieStepsBack:                // Route128_Movement_152279
    lock_facing_direction
    walk_slow_up
    delay_16
    unlock_facing_direction
    step_end
    .balign 4, 0
Mv_R128_ArchieWalksLeft:                // Route128_Movement_15227E
    walk_fast_left 3
    walk_in_place_fastest_right
    step_end
    .balign 4, 0
Mv_R128_ArchieLeaves:                   // Route128_Movement_152283
    delay_16 2
    walk_fast_up
    walk_fast_left
    walk_fast_up 8
    step_end
    .balign 4, 0
Mv_R128_MaxieWalksLeft:                 // Route128_Movement_152290
    walk_left 2
    step_end
    .balign 4, 0
Mv_R128_MaxieComesLeft:                 // Route128_Movement_152293
    walk_left
    walk_in_place_fastest_down
    step_end
    .balign 4, 0
Mv_R128_MaxieLeaves:                    // Route128_Movement_152296
    walk_fast_left 3
    walk_fast_up 7
    step_end
    .balign 4, 0
Mv_R128_MaxieComesRight:                // Route128_Movement_1522A1
    walk_right
    walk_in_place_fastest_down
    step_end
    .balign 4, 0
Mv_R128_StevenSteps:                    // Route128_Movement_15226F
    walk_fast_left
    step_end
    .balign 4, 0
Mv_R128_StevenUp:                       // Route128_Movement_15226D
    walk_up
    step_end

#if __has_include("common/legendary_weather.inc")
#include "common/legendary_weather.inc"
#endif
#include "common/movement.inc"
#ifdef HOENN_TEST_CH10
#include "scenes/ch10_test.inc"
#endif
#endif
