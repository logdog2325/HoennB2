// SeafloorCavern_Room9 (zone 190): cave_builder (converter/gen_caves.py): ladders and cracked floors as step triggers
// (Sapphire's step-on warps), simple people/signs. Story scripts: add them after a line "// ---- story" (this
// generator keeps everything from that line on and the entries you add: b2tools/story_merge.py) and number them
// after these entries.
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_trainers.h"  // ch10
#include "hoenn_key_items.h"  // ch10
#include "hoenn_story.inc"  // ch10
#include "hoenn_version.inc"  // ruby_scenes: version-neutral names (SPECIES_/ITEM_/TRAINER_ aliases)

    ScriptEntry Script_None
    ScriptEntry R9_Scene  // 2: trigger (17,42) VAR_SEAFLOOR_CAVERN_STATE 0 (SeafloorCavern_Room9_EventScript_15DAFA)  // story:
    ScriptEntry R9_Init  // 3: zone init: the test start only (Sapphire's ON_TRANSITION sets up gfx ids and a map layout)  // story:
    ScriptEntriesEnd

Script_None:
    VMHalt
    .balign 4, 0

// ---- story (chapter Ch10, ch10 agent 2026-10-07; Sapphire data/maps/SeafloorCavern_Room9/scripts.inc; generators keep everything from
// this line on; entries above marked "// story:"). Messages: 0248_room_SeafloorCavern_Room9.txt
// People (data/story/ch10.json, uid = Sapphire local id; Kyogre = Black 2's overworld Pokémon sprite code 4511, "model_ruby" 4512 = Groudon): the awakened legendary 1 and the sleeping one 7 (both at (17,38): the object swap is the awakening), the evil team's leader 2 (Sapphire: Archie), the other leader 3 (Maxie), two good-team grunts 4 and 5 (Magma; all hidden by their FLAG_HIDE_*_SEAFLOOR_CAVERN until the scene), the trigger at (17,42) (VAR_SEAFLOOR_CAVERN_STATE 0).
// RUBY (ruby_scenes, 2026-10-08; pokeruby's .ifdef SAPPHIRE blocks of this map): the flow is the same event for event. What differs is only data: the text lines (same line numbers: src/text/script/ruby/0248_*.txt), the models (art swap of sprite codes 353 <-> 303 for the leaders, 293/294 <-> 302/192 for the grunts: src/sprites/overworld/ruby/; "model_ruby" 4512 for the legendary), the trainer (TRAINER_SEAFLOOR_CAVERN_GRUNT_5 = Black 2 id of TRAINER_ARCHIE_2, holding Maxie in a Ruby build), the room's layout (setmaplayoutindex 327: data/cave_layouts/SeafloorCavern_Room9_Ruby.json, WP3) and the glow colour (Sapphire's glow is red, Ruby's blue: VAR_RESULT 0 / 1 of sub_80818A4; Black 2 has no coloured screen flash, both are the one white flash below).
// Black 2 gaps: Sapphire's screen glow task (sub_80818A4/FC), the sparkle field effect and the white-out of sub_8081924 are one white flash (FadeOutWhiteQ/FadeInWhiteQ); the weather lines (setweather NONE) need nothing (no weather in the cave, the crisis weather is the `weather` patch's); sounds are guesses (SEQ_SE_FLD_*).
#include "scenes/ch10_lib.inc"
#define T_HoldItRightThere 0
#define T_FufufuSoItWasYou 1
#define T_Behold 2
#define T_ItSurprisesMe 3
#define T_ICommendYou 4
#define T_RedOrbShining 5
#define T_WhatDidntDoAnything 6
#define T_MessageFromMembers 7
#define T_YesWhatIsIt 8
#define T_SomethingWrong 9
#define T_MaxieWhatHaveYouWrought 10
#define T_ArcheWhatAreYouSaying 11
#define T_MaxieNoTimeToArgue 12
#define T_MaxieComeOnGetOut 13
#define R9_LEGEND 1                    // Sapphire: Kyogre (4511), Ruby: Groudon (4512, "model_ruby")
#define R9_EVIL_LEADER 2               // Sapphire: Archie, Ruby: Maxie (the art of sprite code 353; TRAINER_SEAFLOOR_CAVERN_GRUNT_5)
#define R9_GOOD_LEADER 3               // Sapphire: Maxie, Ruby: Archie (code 303)
#define R9_GOOD_GRUNT_M 4              // Sapphire: Magma grunt M, Ruby: Aqua (code 302)
#define R9_GOOD_GRUNT_F 5              // (code 192)
#define R9_LEGEND_ASLEEP 7
#define R9_ROUTE128_ZONE 230            // Sapphire (38,22) + Route 128's offset (688,280)
#define R9_ROUTE128_X 726
#define R9_ROUTE128_Z 302

R9_Scene:                               // SeafloorCavern_Room9_EventScript_15DAFA
    c10_lock
    h_applymovement 255, Common_Movement_WalkInPlaceFastestUp
    h_waitmovement
    h_applymovement 255, Mv_R9_PlayerPause
    h_waitmovement
#ifdef HOENN_EMERALD
    h_playbgm MUS_EVIL_TEAM             // Emerald: playbgm MUS_ENCOUNTER_AQUA, FALSE (emerald_ch10)
#endif
    h_msgbox_info T_HoldItRightThere    // Archie: Hold it right there.
    h_closemessage
    h_addobject R9_EVIL_LEADER, FLAG_HIDE_EVIL_LEADER_SEAFLOOR_CAVERN
    h_applymovement 255, Common_Movement_WalkInPlaceFastestLeft
    h_waitmovement
    h_applymovement R9_EVIL_LEADER, Mv_R9_ArchieComes
    h_waitmovement
    h_msgbox_actor T_FufufuSoItWasYou, R9_EVIL_LEADER    // Archie: Fufufu... So it was you, after all.
    h_applymovement R9_EVIL_LEADER, Common_Movement_WalkInPlaceFastestUp
    h_waitmovement
    h_msgbox_actor T_Behold, R9_EVIL_LEADER  // Archie: Behold! See how beautiful it is, the sleeping form of the ancient Pokémon Kyogre! ...
    h_applymovement R9_EVIL_LEADER, Common_Movement_WalkInPlaceFastestRight     // Common_Movement_FacePlayer (the player is on his right)
    h_waitmovement
    h_msgbox_actor T_ItSurprisesMe, R9_EVIL_LEADER   // Archie: It surprises me, how you've managed to chase me here. ... you must disappear now!
    h_closemessage
    c10_trainerbattle TRAINER_SEAFLOOR_CAVERN_GRUNT_5    // trainerbattle_no_intro (Sapphire: Archie, TRAINER_ARCHIE_2; Ruby: Maxie; in battle: I... I lost again?)
    h_msgbox_actor T_ICommendYou, R9_EVIL_LEADER     // Archie: Fufufu... I commend you. ... With this Red Orb, I can make Kyogre...
    h_closemessage
    BGMFadeOut 30                       // special sub_8081924: the music fades (setweather NONE / doweather: no weather here)
    h_delay 40
    h_msgbox_info T_RedOrbShining       // The Red Orb suddenly began shining by itself!
    h_closemessage
    SEPlay C10_SE_DETECT                // SE_M_DETECT + the sparkle at (16,42)
    h_delay 40
    BGMPlay SEQ_BGM_E_LEGEND_BORN_B     // MUS_AWAKEN_LEGEND [guess]
    SEPlay C10_SE_ORB                   // SE_ORB
    FadeOutWhiteQ                       // the glow (sub_80818A4): one white flash
    FadeWait
    h_applymovement R9_EVIL_LEADER, Common_Movement_WalkInPlaceFastestUp
    h_applymovement 255, Common_Movement_WalkInPlaceFastestUp
    h_waitmovement
    h_removeobject R9_LEGEND_ASLEEP, FLAG_HIDE_SLEEPING_MON_SEAFLOOR_CAVERN
    h_addobject R9_LEGEND, FLAG_HIDE_AWAKENED_MON_SEAFLOOR_CAVERN
    h_delay 60
    FadeInWhiteQ
    FadeWait
    h_applymovement R9_LEGEND, Mv_R9_KyogreRises
    h_waitmovement
    c10_shake 4                         // setvar 8004 1, 8005 1; special ShakeCamera
    h_applymovement R9_LEGEND, Mv_R9_KyogreLeaves
    h_waitmovement
    h_removeobject R9_LEGEND, FLAG_HIDE_AWAKENED_MON_SEAFLOOR_CAVERN
    h_delay 4
    c10_shake 8                         // setvar 8004 2, 8005 2
    h_delay 30
    h_msgbox_actor T_WhatDidntDoAnything, R9_EVIL_LEADER     // Archie: What?! I didn't do anything. Why did the Red Orb... Where did Kyogre go?
    SEPlay SE_PC_LOGIN
    h_applymovement 255, Common_Movement_WalkInPlaceFastestLeft
    h_waitmovement
    h_msgbox_actor T_MessageFromMembers, R9_EVIL_LEADER      // Archie: Hm? It's a message from our members outside...
    h_closemessage
    h_applymovement R9_EVIL_LEADER, Mv_R9_ArchieStepsLeft
    h_waitmovement
    h_msgbox_actor T_YesWhatIsIt, R9_EVIL_LEADER             // Archie: Yes, what is it? Hm... It's raining heavily? ... Hold your position and monitor the situation!
    h_closemessage
    SEPlay SE_PC_OFF
    h_delay 20
    h_applymovement R9_EVIL_LEADER, Common_Movement_WalkInPlaceFastestDown
    h_waitmovement
    h_msgbox_actor T_SomethingWrong, R9_EVIL_LEADER          // Archie: There's something wrong... The Red Orb is supposed to awaken and control Kyogre... Why?!
    h_closemessage
    h_addobject R9_GOOD_LEADER, FLAG_HIDE_OTHER_LEADER_SEAFLOOR_CAVERN
    h_addobject R9_GOOD_GRUNT_M, FLAG_HIDE_OTHER_TEAM_GRUNTS_SEAFLOOR_CAVERN
    h_addobject R9_GOOD_GRUNT_F, FLAG_HIDE_OTHER_TEAM_GRUNTS_SEAFLOOR_CAVERN
    h_applymovement R9_GOOD_GRUNT_F, Mv_R9_GruntsWalk
    h_applymovement R9_GOOD_GRUNT_M, Mv_R9_GruntsWalk
    h_applymovement R9_GOOD_LEADER, Mv_R9_MaxieWalks
    h_waitmovement
    h_applymovement R9_EVIL_LEADER, Common_Movement_WalkInPlaceFastestLeft
    h_waitmovement
    h_msgbox_actor T_MaxieWhatHaveYouWrought, R9_GOOD_LEADER  // Maxie: What have you wrought? Archie... You've finally awoken Kyogre, haven't you? ...
    h_applymovement R9_EVIL_LEADER, Common_Movement_ExclamationMark
    h_waitmovement
    h_applymovement R9_EVIL_LEADER, Common_Movement_Delay48
    h_waitmovement
    h_msgbox_actor T_ArcheWhatAreYouSaying, R9_EVIL_LEADER   // Archie: What are you saying? The Red Orb should let me control Kyogre... That can't be possible...
    h_msgbox_actor T_MaxieNoTimeToArgue, R9_GOOD_LEADER       // Maxie: We don't have the time to argue about it here! Get outside and see for yourself! ...
    h_closemessage
    h_applymovement R9_GOOD_LEADER, Mv_R9_MaxieStepsRight
    h_applymovement R9_EVIL_LEADER, Mv_R9_ArchieMakesRoom
    h_waitmovement
    h_msgbox_actor T_MaxieComeOnGetOut, R9_GOOD_LEADER        // Maxie: <player>, come on, you have to get out of here, too!
#ifdef HOENN_EMERALD
    // Emerald (emerald_ch10, 2026-10-12; pokeemerald SeafloorCavern_Room9_EventScript_ArchieAwakenKyogre's end): the same scene with
    // Emerald's lines (src/text/script/emerald/0248_*.txt); Kyogre flies to Sootopolis, where Groudon meets it (VAR_SOOTOPOLIS_CITY_STATE
    // 1 = this port's VAR_SOOTOPOLIS_STATE: scenes/emerald/SootopolisCity.inc). Steven's house: this port's state 1 (Emerald's 2,
    // notes/EMERALD_STORY.md 2.4.2)
    h_setvar VAR_ROUTE128_STATE, 1
    h_setvar VAR_SOOTOPOLIS_STATE, 1
    h_clearflag FLAG_HIDE_STEVEN_SOOTOPOLIS                 // FLAG_HIDE_SOOTOPOLIS_CITY_STEVEN
    h_clearflag FLAG_HIDE_SOOTOPOLIS_CITY_ARCHIE
    h_clearflag FLAG_HIDE_SOOTOPOLIS_CITY_MAXIE
    h_clearflag FLAG_HIDE_SOOTOPOLIS_CITY_RESIDENTS
    h_clearflag FLAG_HIDE_SOOTOPOLIS_CITY_GROUDON
    h_clearflag FLAG_HIDE_SOOTOPOLIS_CITY_KYOGRE
    h_setflag FLAG_HIDE_SOOTOPOLIS_CITY_MAN_1
    h_setflag FLAG_LEGENDARIES_IN_SOOTOPOLIS
    h_clearflag FLAG_HIDE_EVIL_LEADER_ROUTE128              // FLAG_HIDE_ROUTE_128_ARCHIE
    h_clearflag FLAG_HIDE_OTHER_LEADER_ROUTE128             // FLAG_HIDE_ROUTE_128_MAXIE
    h_setflag FLAG_SYS_WEATHER_CTRL     // the abnormal weather (patches/emerald_mech.c EM_ZoneWeather)
    h_setflag FLAG_LEGEND_ESCAPED_SEAFLOOR_CAVERN           // FLAG_KYOGRE_ESCAPED_SEAFLOOR_CAVERN
    h_setflag FLAG_HIDE_STEVEN_STEVENS_HOUSE
    h_setvar VAR_STEVENS_HOUSE_STATE, 2                 // pokeemerald VAR_STEVENS_HOUSE_STATE 2 (Steven left his house)
    h_setvar VAR_SEAFLOOR_CAVERN_STATE, 1
#else
    h_setvar VAR_ROUTE128_STATE, 1
    h_clearflag FLAG_HIDE_CAVE_OF_ORIGIN_ENTRANCE_WOMAN_1
    h_clearflag FLAG_HIDE_CAVE_OF_ORIGIN_ENTRANCE_WOMAN_2
    h_clearflag FLAG_HIDE_WALLACE_SOOTOPOLIS
    h_clearflag FLAG_HIDE_STEVEN_SOOTOPOLIS
    h_setvar VAR_SOOTOPOLIS_STATE, 1
    h_clearflag FLAG_HIDE_EVIL_LEADER_ROUTE128
    h_clearflag FLAG_HIDE_OTHER_LEADER_ROUTE128
    h_setflag FLAG_SYS_WEATHER_CTRL     // Kyogre's rain (the `weather` patch)
    h_setflag FLAG_HIDE_SOOTOPOLIS_RESIDENTS
    h_setflag FLAG_LEGEND_ESCAPED_SEAFLOOR_CAVERN
    h_setflag FLAG_HIDE_STEVEN_STEVENS_HOUSE
    h_setvar VAR_STEVENS_HOUSE_STATE, 1
    h_setvar VAR_SEAFLOOR_CAVERN_STATE, 1
#endif
    h_setflag FLAG_HIDE_EVIL_LEADER_SEAFLOOR_CAVERN
    h_setflag FLAG_HIDE_OTHER_LEADER_SEAFLOOR_CAVERN
    h_setflag FLAG_HIDE_OTHER_TEAM_GRUNTS_SEAFLOOR_CAVERN
    h_setflag FLAG_HIDE_AWAKENED_MON_SEAFLOOR_CAVERN
    h_setflag FLAG_HIDE_EVIL_TEAM_GRUNTS_SEAFLOOR_CAVERN
    h_closemessage
    h_warp_scene R9_ROUTE128_ZONE, R9_ROUTE128_X, R9_ROUTE128_Z, 0, 10017      // warp MAP_ROUTE128, 255, 38, 22 (hm_free Script_18 fades the arrival in)
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

    .balign 4, 0
Mv_R9_PlayerPause:                      // SeafloorCavern_Room9_Movement_15DD68
    delay_16 2
    step_end
    .balign 4, 0
Mv_R9_ArchieComes:                      // _15DD36
    walk_right 7
    step_end
    .balign 4, 0
Mv_R9_ArchieStepsLeft:                  // _15DD41
    walk_left
    delay_16
    step_end
    .balign 4, 0
Mv_R9_ArchieMakesRoom:                  // _15DD46
    face_up
    lock_facing_direction
    walk_down
    unlock_facing_direction
    walk_in_place_fastest_right
    step_end
    .balign 4, 0
Mv_R9_KyogreRises:                      // _15DD4C
    delay_16 2
    walk_slow_down
    delay_16 3
    walk_slow_down
    delay_16 3
    step_end
    .balign 4, 0
Mv_R9_KyogreLeaves:                     // _15DD57 (slide_up x2: Black 2 has no slide, a quick walk)
    walk_fast_up 2
    step_end
    .balign 4, 0
Mv_R9_MaxieWalks:                       // _15DD5A
    walk_fast_right 5
    step_end
    .balign 4, 0
Mv_R9_MaxieStepsRight:                  // _15DD60
    walk_right 2
    step_end
    .balign 4, 0
Mv_R9_GruntsWalk:                       // _15DD63
    walk_fast_right 4
    step_end

R9_Init:                                // SeafloorCavern_Room9_MapScript1_15DAEC (the gfx ids and the layout need nothing here)
#ifdef HOENN_TEST_CH10
    VMCall Test_Ch10Start               // test builds only (scenes/ch10_test.inc)
#endif
    VMHalt

#include "common/movement.inc"
#ifdef HOENN_TEST_CH10
#include "scenes/ch10_test.inc"
#endif
    .balign 4, 0
