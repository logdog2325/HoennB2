// Route125's story (Sapphire data/maps/Route125/scripts.inc; chapter Ch9, ch9 agent 2026-10-07).
// converter/gen_map_content.py includes this file twice in the generated zone file of zone 194: the entry below is
// script 1, the generated signs/people follow. Sapphire's Route125_MapScript1_151F24 (ON_TRANSITION) only runs
// Common_EventScript_SetLegendaryWeather while FLAG_SYS_WEATHER_CTRL is set (chapter Ch10's Kyogre/Groudon weather: it
// writes common/legendary_weather.inc, which this guarded call picks up). Everything else on the route is generated:
// the trainers (Black 2 eye-contact trainers, data/hoenn_trainer_npcs.json), the sign and the item balls.
#ifdef SCENE_ENTRIES
    ScriptEntry R125_Init                 // 1: Route125_MapScript1_151F24 (zone init)
#else
R125_Init:
#ifdef HOENN_TEST_CH9
    VMCall Test_Ch9Start                // test builds only (scenes/ch9_test.inc)
#endif
#if __has_include("common/legendary_weather.inc")
    h_call_if_set FLAG_SYS_WEATHER_CTRL, Common_SetLegendaryWeather     // chapter Ch10's (Kyogre's rain)
#endif
    VMHalt
#if __has_include("common/legendary_weather.inc")
#include "common/legendary_weather.inc"
#endif
#ifdef HOENN_TEST_CH9
#include "scenes/ch9_test.inc"
#endif
#endif
