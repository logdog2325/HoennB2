// Route 119's story (Sapphire data/maps/Route119/scripts.inc; chapter Ch7, ch7 agent 2026-10-07): the whole map is
// zone 463 (every map has its own zone up to its edges: b2tools/world.py zone_rects; until 2026-10-08 the north part,
// x 24-39 y 0-35, was in Fortree's zone 16 and these scripts were in scenes/FortreeCity.inc: zone_edges moved them here).
// converter/gen_map_content.py includes this file twice in the generated zone file 0926_auto_Route119.s: the entries
// below are scripts 1-9, the generated signs/people follow. Text: src/text/scenes/Route119.txt (T_* below).
// People and triggers: data/story/ch7.json (outdoor uid = 100 + Sapphire local id). Map scripts: scenes/Route119_init.inc.
// Trainers (Brent, Donald, Taylor, Doug, Greg, Kent, Takashi, Yasu, Hideo; the grass walkers and the mountain/tree
// disguises): eye contact (data/story/ch7.json, global script 3000 + id), the others are placed by the trainers patch.
// Not ported: Route119_MapScript1_151172 (ON_RESUME: removes the Kecleon after its battle: h_static_battle does),
// `special SetRoute119Weather` (Black 2's weather is per zone: no per-tile weather).
#ifdef SCENE_ENTRIES
    ScriptEntry R119_Init               // 1: Route119_MapScript1_15119B (zone init)
    ScriptEntry R119_Lookout1           // 2: object 23, Route119_EventScript_1515C5
    ScriptEntry R119_Lookout2           // 3: object 24, Route119_EventScript_1515DC
    ScriptEntry R119_Kecleon2           // 4: object 36, Route119_EventScript_Kecleon2
    ScriptEntry R119_HideKecleons       // 5: scene condition C7_KECLEON_HIDDEN 0 (MOVEMENT_TYPE_INVISIBLE)
    ScriptEntry R119_FieldLoad          // 6: field load / return: the Kecleons are hidden again
    ScriptEntry R119_RivalLeft          // 7: trigger (25,31) VAR_ROUTE119_STATE 0, Route119_EventScript_1511C5
    ScriptEntry R119_RivalRight         // 8: trigger (26,31), Route119_EventScript_1511D0
    ScriptEntry R119_Kecleon1           // 9: object 35, Route119_EventScript_Kecleon1
#else
#include "scenes/ch7_lib.inc"
#include "scenes/ch7_test.inc"

#define T_Lookout1 0
#define T_Lookout2 1
#define T_SomethingUnseeable 2
#define T_UnseeableUseDevonScope 3
#define T_UseDevonScopeMonAttacked 4
#define T_MayWhereWereYou 5
#define T_MayNothingToWorry 6
#define T_MayUseFly 7
#define T_BrendanSoThisIsWhere 8
#define T_BrendanGoodEnough 9
#define T_BrendanUseFly 10

#define R119_LOOKOUT1 123               // object 23 at (13,33): Team Aqua lookout (FLAG_HIDE_EVIL_TEAM_WEATHER_INSTITUTE)
#define R119_LOOKOUT2 124               // object 24 at (13,34)
#define R119_KECLEON2 136               // object 36 at (20,13) (FLAG_HIDE_KECLEON_ROUTE119_2)
#define R119_KECLEON1 135               // object 35 at (31,6) (FLAG_HIDE_KECLEON_ROUTE119_1)
// The rival (Sapphire objects 16 = walking, 25 = on the Mach Bike). Sapphire moves both with setobjectxyperm to (25,32)
// or (26,32), below the trigger the player stepped on; Black 2 cannot move an entity's place outside the zone init
// (ObjInitNPCGPos is a level-2 command), so each place has its own entity, shown by the same hide flag:
#define R119_RIVAL_L 116                // walking rival at (25,32) (FLAG_HIDE_RIVAL_ROUTE119)
#define R119_RIVAL_R 216                // walking rival at (26,32)
#define R119_BIKE 125                   // rival on the bike at (17,33), where the scene starts (FLAG_HIDE_RIVAL_ROUTE119_ON_BIKE)
#define R119_BIKE_L 225                 // rival on the bike at (25,32), for the exit
#define R119_BIKE_R 226                 // ... at (26,32)

// the rival says a line (Sapphire's msgbox) in a balloon from the walking rival (C7_TMP2 = R119_RIVAL_L / _R, set when
// she gets off the bike)
    .macro r119_say n
    h_msgbox_actor \n, C7_TMP2
    .endm

R119_Init:                              // Route119_MapScript1_15119B: the rival's sprites, the Weather Institute's workers
    RTCallGlobal 8297                       // the berry trees' new-day reset (converter/gen_hidden_items.py; missing_objects)
#ifdef HOENN_TEST_CH7
    VMCall Test_Ch7Start
#endif
    h_setup_rival_gfx                   // Common_EventScript_SetupRivalGfxId (walking rival: model 162, work 0x4020)
    c7_setup_rival_bike_gfx             // Common_EventScript_SetupRivalOnBikeGfxId (model 165, work 0x4023)
    h_goto_if_ne VAR_WEATHER_INSTITUTE_STATE, 1, L_R119_InitDone
    h_setflag FLAG_HIDE_WEATHER_INSTITUTE_WORKERS_2F
    h_clearflag FLAG_HIDE_WEATHER_INSTITUTE_WORKERS_1F
    h_setvar VAR_WEATHER_INSTITUTE_STATE, 2
L_R119_InitDone:
    h_keep_banner                       // the Kecleon scene below leaves the place-name banner shown
    VMHalt

R119_HideKecleons:                      // MOVEMENT_TYPE_INVISIBLE of Route 119's two Kecleons
    h_keep_banner_end                   // (later scripts close the banner again, as in Black 2)
    h_setvar C7_KECLEON_HIDDEN, 1
    c7_hide_kecleon R119_KECLEON1, FLAG_HIDE_KECLEON_ROUTE119_1
    c7_hide_kecleon R119_KECLEON2, FLAG_HIDE_KECLEON_ROUTE119_2
    h_waitmovement
    VMHalt

R119_FieldLoad:
    h_setvar C7_KECLEON_HIDDEN, 0
    VMHalt

R119_Lookout1:                          // Route119_EventScript_1515C5
    c7_talk
    h_msgbox T_Lookout1                 // We're standing lookout here. Hey, you! Stay away from the Weather Institute. ...
    h_closemessage
    h_turnobject R119_LOOKOUT1, 3       // Common_Movement_FaceOriginalDirection (FACE_RIGHT)
    h_release

R119_Lookout2:                          // Route119_EventScript_1515DC
    c7_talk
    h_msgbox T_Lookout2                 // Lookout duty is surprisingly boring. Hey, you! ...
    h_closemessage
    h_turnobject R119_LOOKOUT2, 3
    h_release

R119_Kecleon1:                          // Route119_EventScript_Kecleon1 -> EventScript_Kecleon
    c7_kecleon R119_KECLEON1, FLAG_HIDE_KECLEON_ROUTE119_1, T_SomethingUnseeable, T_UnseeableUseDevonScope, T_UseDevonScopeMonAttacked

R119_Kecleon2:                          // Route119_EventScript_Kecleon2 -> EventScript_Kecleon
    c7_kecleon R119_KECLEON2, FLAG_HIDE_KECLEON_ROUTE119_2, T_SomethingUnseeable, T_UnseeableUseDevonScope, T_UseDevonScopeMonAttacked

// ---- the rival and HM02 Fly (Route119_EventScript_1511DB) -------------------------------------------------------
R119_RivalLeft:
    h_setvar C7_POS, 1                  // VAR_TEMP_1 1: the player is on (25,31)
    VMJump L_R119_Rival
R119_RivalRight:
    h_setvar C7_POS, 2                  // VAR_TEMP_1 2: (26,31)
L_R119_Rival:
    h_lock
    h_addobject R119_BIKE, FLAG_HIDE_RIVAL_ROUTE119_ON_BIKE
    h_goto_if_girl L_R119_MusicBrendan
    h_playbgm MUS_ENCOUNTER_MAY
    VMJump L_R119_Music
L_R119_MusicBrendan:
    h_playbgm MUS_ENCOUNTER_BRENDAN
L_R119_Music:
    h_delay 65
    h_goto_if_eq C7_POS, 2, L_R119_RideInRight
    h_applymovement R119_BIKE, Mv_R119_RideInLeft
    VMJump L_R119_RodeIn
L_R119_RideInRight:
    h_applymovement R119_BIKE, Mv_R119_RideInRight
L_R119_RodeIn:
    h_waitmovement
    h_applymovement 255, Common_Movement_WalkInPlaceFastestDown
    h_waitmovement
    h_delay 30
    // setobjectxyperm 16/25 to the player's column, removeobject 25, addobject 16
    h_removeobject R119_BIKE, FLAG_HIDE_RIVAL_ROUTE119_ON_BIKE
    h_goto_if_eq C7_POS, 2, L_R119_WalkerRight
    h_addobject R119_RIVAL_L, FLAG_HIDE_RIVAL_ROUTE119
    h_setvar C7_TMP2, R119_RIVAL_L      // (who speaks: r119_say)
    VMJump L_R119_Walker
L_R119_WalkerRight:
    h_addobject R119_RIVAL_R, FLAG_HIDE_RIVAL_ROUTE119
    h_setvar C7_TMP2, R119_RIVAL_R
L_R119_Walker:
    h_delay 30
    h_buffer_player
    h_goto_if_girl L_R119_Brendan
    r119_say T_MayWhereWereYou
    h_closemessage
    h_goto_if_eq VAR_STARTER_MON, 1, L_R119_May9
    h_goto_if_eq VAR_STARTER_MON, 2, L_R119_May3
    h_trainerbattle TRAINER_MAY_6           // (in battle: "Achah! <player>, you're strong! ...")
    VMJump L_R119_MayWon
L_R119_May9:
    h_trainerbattle TRAINER_MAY_9
    VMJump L_R119_MayWon
L_R119_May3:
    h_trainerbattle TRAINER_MAY_3
L_R119_MayWon:                          // Route119_EventScript_1512BD
    r119_say T_MayNothingToWorry
    h_closemessage
    VMCall Sub_R119_GiveFly
    h_buffer_player
    r119_say T_MayUseFly
    VMJump L_R119_RivalLeaves
L_R119_Brendan:                         // Route119_EventScript_1512D8
    r119_say T_BrendanSoThisIsWhere
    h_closemessage
    h_goto_if_eq VAR_STARTER_MON, 1, L_R119_Brendan9
    h_goto_if_eq VAR_STARTER_MON, 2, L_R119_Brendan3
    h_trainerbattle TRAINER_BRENDAN_6       // (in battle: "Hmm... You've gotten pretty darn decent.")
    VMJump L_R119_BrendanWon
L_R119_Brendan9:
    h_trainerbattle TRAINER_BRENDAN_9
    VMJump L_R119_BrendanWon
L_R119_Brendan3:
    h_trainerbattle TRAINER_BRENDAN_3
L_R119_BrendanWon:                      // Route119_EventScript_151337
    r119_say T_BrendanGoodEnough
    h_closemessage
    VMCall Sub_R119_GiveFly
    r119_say T_BrendanUseFly
L_R119_RivalLeaves:                     // Route119_EventScript_151362
    h_closemessage
    // setobjectxyperm 25 to the player's column, removeobject 16, addobject 25 (the rival gets on the bike)
    h_goto_if_eq C7_POS, 2, L_R119_MountRight
    h_removeobject R119_RIVAL_L, FLAG_HIDE_RIVAL_ROUTE119
    h_addobject R119_BIKE_L, FLAG_HIDE_RIVAL_ROUTE119_ON_BIKE
    h_delay 30
    h_applymovement R119_BIKE_L, Mv_R119_RideAwayLeft
    h_waitmovement
    h_removeobject R119_BIKE_L, FLAG_HIDE_RIVAL_ROUTE119_ON_BIKE
    VMJump L_R119_Gone
L_R119_MountRight:
    h_removeobject R119_RIVAL_R, FLAG_HIDE_RIVAL_ROUTE119
    h_addobject R119_BIKE_R, FLAG_HIDE_RIVAL_ROUTE119_ON_BIKE
    h_delay 30
    h_applymovement R119_BIKE_R, Mv_R119_RideAwayRight
    h_waitmovement
    h_removeobject R119_BIKE_R, FLAG_HIDE_RIVAL_ROUTE119_ON_BIKE
L_R119_Gone:
    h_setvar VAR_ROUTE119_STATE, 1
    h_fadedefaultbgm                    // savebgm 0, fadedefaultbgm
#ifdef HOENN_EMERALD                    // Emerald (emerald_ch0_3): Scott comes by after the rival left (scenes/emerald/Route119.inc)
    VMCall Sub_Em_R119_Scott
#endif
    h_release

Sub_R119_GiveFly:                       // Route119_EventScript_151352 (Sapphire does not look at giveitem's result)
    h_giveitem ITEM_HM02
    h_setflag FLAG_RECEIVED_HM02
    VMReturn

    .balign 4, 0
Mv_R119_RideInLeft:                     // Route119_Movement_1513F0
    walk_fast_right 8
    walk_fast_up
    step_end
Mv_R119_RideInRight:                    // Route119_Movement_1513FA
    walk_fast_right 9
    walk_fast_up
    step_end
Mv_R119_RideAwayLeft:                   // Route119_Movement_151405
    walk_fast_right
    walk_fast_up 3
    walk_fast_right
    walk_fast_up 4
    step_end
Mv_R119_RideAwayRight:                  // Route119_Movement_15140F
    walk_fast_left
    walk_fast_up 3
    walk_fast_right 2
    walk_fast_up 4
    step_end
#ifdef HOENN_EMERALD
#include "scenes/emerald/Route119.inc"
#endif
#include "common/movement.inc"
#endif
