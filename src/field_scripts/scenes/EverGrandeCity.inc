// Ever Grande City's story (Sapphire data/maps/EverGrandeCity/scripts.inc; chapter Ch11, ch11 agent 2026-10-07).
// converter/gen_map_content.py includes this file twice in the generated zone file 0824_auto_EverGrandeCity.s: the entries
// below become scripts 1-2, the generated signs follow. Map scripts: scenes/EverGrandeCity_init.inc. The three signs
// (Victory Road, the city, the Pokémon League) and the Center's sign are the generator's.
// People: none. Step trigger: Sapphire's eleven coord events (16-26, 58) on VAR_TEMP_1 0 are one trigger of
// data/story/ch11.json (11 tiles wide, work 0x4001 = VAR_TEMP_1).
#ifdef SCENE_ENTRIES
    ScriptEntry EG_Visited          // 1: step trigger (16-26, 58): EverGrandeCity_EventScript_SetVisitedEverGrande
    ScriptEntry EG_Init             // 2: EverGrandeCity_OnTransition (zone init)
#else
EG_Visited:                         // EverGrandeCity_EventScript_SetVisitedEverGrande
    h_lock
    h_setflag FLAG_VISITED_EVER_GRANDE_CITY   // the Fly point
    h_setvar 0x4001, 1              // VAR_TEMP_1 1: once a visit
    h_release

EG_Init:
#ifdef HOENN_TEST_CH11
    VMCall Test_Ch11Start           // test builds only (scenes/ch11_test.inc)
#endif
#if __has_include("common/legendary_weather.inc")
    h_call_if_set FLAG_SYS_WEATHER_CTRL, Common_SetLegendaryWeather     // chapter Ch10's (Kyogre's rain)
#endif
    VMHalt
#if __has_include("common/legendary_weather.inc")
#include "common/legendary_weather.inc"
#endif
    .balign 4, 0
#include "scenes/ch11_test.inc"
#endif
