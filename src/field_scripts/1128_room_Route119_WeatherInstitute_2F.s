// Route119_WeatherInstitute_2F (zone 564): Sapphire's simple people and signs (as converter/gen_interiors.py makes them),
// plus people that turn back after their message (Common_Movement_FaceOriginalDirection), by the specials agent
// (b2tools/specials.py people). Messages: src/text/script/0365_room_Route119_WeatherInstitute_2F.txt
#include "asm/field_script.inc"
#include "hoenn.h"  // ch7
#include "hoenn_trainers.h"  // ch7
#include "hoenn_story.inc"  // ch7

    ScriptEntry Script_None
    ScriptEntry WI2_Shelly  // 2: Route119_WeatherInstitute_2F_EventScript_163D2A (+ 163D45, 163D7A)  // story:
    ScriptEntry WI2_Scientist  // 3: Route119_WeatherInstitute_2F_EventScript_163DCC  // story:
    ScriptEntry WI2_Init  // 4: Route119_WeatherInstitute_2F_MapScript1_163CC8 (zone init)  // story:
    ScriptEntriesEnd

Script_None:
    VMHalt
    .balign 4, 0

// ---- story (chapter Ch7, ch7 agent 2026-10-07; Sapphire data/maps/Route119_WeatherInstitute_2F/scripts.inc; generators must
// keep everything from this line on). Scripts 2-4, text lines 1-6 (line 0 is the generator's). Shelly (uid 3), the
// scientist (uid 5), the two tied-up workers (uids 4 and 6, no script, hidden by FLAG_HIDE_WEATHER_INSTITUTE_WORKERS_2F)
// and the two grunts (uids 1 and 2: eye-contact trainers, hidden by FLAG_HIDE_EVIL_TEAM_WEATHER_INSTITUTE) are in
// data/story/ch7.json; the map script (zone init) is 1129_room_Route119_WeatherInstitute_2F_init.s. Room tiles =
// Sapphire tiles + (1,1). Shelly is Sapphire's TRAINER_WEATHER_INSTITUTE_GRUNT_5 = TRAINER_SHELLY_1, sight 0: she
// battles when talked to.
#include "scenes/ch7_lib.inc"
#include "scenes/ch7_test.inc"        // (test builds only: HOENN_TEST_CH7)
#define T_OutOfOptions 1
#define T_Thanks 2
#define T_ReceivedCastform 3
#define T_CastformExplain 4
#define T_NoRoom 5
#define T_ResearchedRain 6
#define WI2_GRUNT1 1
#define WI2_GRUNT2 2
#define WI2_SHELLY 3
#define WI2_SCIENTIST 5
#define WI2_SCIENTIST_INDEX 5               // his place in the zone's NPC list (ObjInitNPCGPos: the objects of data/story/ch7.json in order)

WI2_Init:                           // Route119_WeatherInstitute_2F_MapScript1_163CC8: where the scientist stands
#ifdef HOENN_TEST_CH7
    VMCall Test_Ch7Start
#endif
#ifdef HOENN_EMERALD                // (emerald_ch12_13) Emerald: after the game he stands at (2,2) facing up
    h_goto_if_set FLAG_SYS_GAME_CLEAR, L_WI2_GameClear   // (SetScientistPosGameClear, after the state's own place)
#endif
    h_goto_if_eq VAR_WEATHER_INSTITUTE_STATE, 0, L_WI2_Hostage
    h_goto_if_eq VAR_WEATHER_INSTITUTE_STATE, 1, L_WI2_Freed
    VMHalt
L_WI2_Hostage:                      // setobjectxyperm 5, 1, 6 (+ face right)
    ObjInitNPCGPos WI2_SCIENTIST_INDEX, 3, 1 + 1, 0, 6 + 1
    VMHalt
L_WI2_Freed:                        // setobjectxyperm 5, 4, 6
    ObjInitNPCGPos WI2_SCIENTIST_INDEX, 3, 4 + 1, 0, 6 + 1
    VMHalt
#ifdef HOENN_EMERALD
L_WI2_GameClear:                    // Route119_WeatherInstitute_2F_EventScript_SetScientistPosGameClear: setobjectxyperm 2, 2
    ObjInitNPCGPos WI2_SCIENTIST_INDEX, 0, 2 + 1, 0, 2 + 1
    VMHalt
#endif

WI2_Shelly:                         // trainerbattle_single TRAINER_WEATHER_INSTITUTE_GRUNT_5, ..., 163D45
    c7_talk
    TrainerSayMessage TRAINER_SHELLY_1, 0, WI2_SHELLY   // Ahahahaha! You're going to meddle in Team Aqua's affairs? ...
    ActorMsgClose
    h_trainerbattle TRAINER_SHELLY_1    // (in battle: "Ahahahaha! You're disgustingly strong!")
    h_msgbox_actor T_OutOfOptions, WI2_SHELLY   // Route119_WeatherInstitute_2F_EventScript_163D45: Ahahahaha! We got meddled with ...
    h_closemessage
    h_setvar VAR_WEATHER_INSTITUTE_STATE, 1
    h_clearflag FLAG_HIDE_WEATHER_INSTITUTE_WORKERS_2F
    h_fadedefaultbgm
    h_fadescreen_black
    h_setflag FLAG_HIDE_EVIL_TEAM_WEATHER_INSTITUTE
    ActorDelete WI2_GRUNT1
    ActorDelete WI2_GRUNT2
    ActorDelete WI2_SHELLY
    h_fadescreen_from_black
    h_applymovement WI2_SCIENTIST, Mv_WI2_ScientistWalk
    h_waitmovement
    VMJump L_WI2_Castform

WI2_Scientist:                      // Route119_WeatherInstitute_2F_EventScript_163DCC
    c7_talk
    h_goto_if_set FLAG_RECEIVED_CASTFORM, L_WI2_AlreadyGave
L_WI2_Castform:                     // Route119_WeatherInstitute_2F_EventScript_163D7A
    h_buffer_player
    h_msgbox_actor T_Thanks, WI2_SCIENTIST      // Thanks! Thanks to you, we're safe! ... take this Pokémon.
    h_getpartysize HLIB_TMP
    h_goto_if_eq HLIB_TMP, 6, L_WI2_PartyFull
    h_closemessage
    h_playfanfare MUS_OBTAIN_ITEM
    h_msgbox_info T_ReceivedCastform            // <player> received Castform!
    h_waitfanfare
    PokePartyAddEx HLIB_TMP, SPECIES_CASTFORM, 0, 25, 2, 2, 2, ITEM_MYSTIC_WATER, 4   // givemon SPECIES_CASTFORM, 25, ITEM_MYSTIC_WATER
    h_closemessage
    h_setflag FLAG_RECEIVED_CASTFORM
    h_msgbox_actor T_CastformExplain, WI2_SCIENTIST   // That Pokémon changes shape according to the weather conditions. ...
    h_release
L_WI2_PartyFull:                    // Route119_WeatherInstitute_2F_EventScript_163DB4
    h_msgbox_actor T_NoRoom, WI2_SCIENTIST      // Hm? You don't seem to have any room for this Pokémon.
    h_release
L_WI2_AlreadyGave:                  // Route119_WeatherInstitute_2F_EventScript_163DBE
#ifdef HOENN_EMERALD                // (emerald_ch12_13) Emerald's ScientistMentionWeather: after the game, the abnormal weather
    h_goto_if_set FLAG_SYS_GAME_CLEAR, L_WI2_TryStartAbnormalWeather
#endif
    h_msgbox T_ResearchedRain       // I've been researching rain for many years, ...
    h_release
#ifdef HOENN_EMERALD
// Route119_WeatherInstitute_2F_EventScript_TryStartAbnormalWeather (scenes/emerald/abnormal_weather.inc): Kyogre and Groudon
// both caught or beaten -> "no longer being reported"; else a new spot once per visit to this floor (FLAG_TEMP_2: a
// map-local flag, cleared by every map change) and the report on it (GetAbnormalWeatherMapNameAndType: the route's name)
#include "scenes/emerald/abnormal_weather.inc"
#define WI2_FLAG_TEMP_2 0x22                // FLAG_TEMP_2 (Black 2's map-local flags 0-0x63)
#define T_GroudonWeather 7                  // the Emerald text overlay's rows (src/text/script/emerald/0365_...)
#define T_KyogreWeather 8
#define T_NoAbnormalWeather 9
L_WI2_TryStartAbnormalWeather:
    h_goto_if_unset FLAG_DEFEATED_KYOGRE, L_WI2_AwStart
    h_goto_if_unset FLAG_DEFEATED_GROUDON, L_WI2_AwStart
    h_msgbox T_NoAbnormalWeather    // Abnormal weather conditions are no longer being reported. ...
    h_release
L_WI2_AwStart:
    h_goto_if_set WI2_FLAG_TEMP_2, L_WI2_AwReport
    aw_create                       // special CreateAbnormalWeatherEvent
    h_setflag WI2_FLAG_TEMP_2
L_WI2_AwReport:
    aw_place 1, L_WI2_AwKyogre
    h_msgbox T_GroudonWeather       // I track weather patterns over the Hoenn region. Presently, a drought has been recorded in ...
    h_release
L_WI2_AwKyogre:
    h_msgbox T_KyogreWeather        // ... heavy rainfall has been recorded over ...
    h_release
#endif

    .balign 4, 0
Mv_WI2_ScientistWalk:               // Route119_WeatherInstitute_2F_Movement_163DC8
    walk_right 3
    step_end
