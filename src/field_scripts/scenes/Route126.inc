// Route126's story (Sapphire data/maps/Route126/scripts.inc; chapter Ch9, ch9 agent 2026-10-07).
// converter/gen_map_content.py includes this file twice in the generated zone file of zone 198: the entry below is
// script 1, the generated signs/people follow. Sapphire's Route126_MapScript1_152004 (ON_TRANSITION) only runs
// Common_EventScript_SetLegendaryWeather while FLAG_SYS_WEATHER_CTRL is set (chapter Ch10's Kyogre/Groudon weather: it
// writes common/legendary_weather.inc, which this guarded call picks up). Everything else on the route is generated:
// the trainers (Black 2 eye-contact trainers, data/hoenn_trainer_npcs.json), the sign and the item balls.
#ifdef SCENE_ENTRIES
    ScriptEntry R126_Init                 // 1: Route126_MapScript1_152004 (zone init)
#else
R126_Init:
#if __has_include("common/legendary_weather.inc")
    h_call_if_set FLAG_SYS_WEATHER_CTRL, Common_SetLegendaryWeather     // chapter Ch10's (Kyogre's rain)
#endif
    VMHalt
#if __has_include("common/legendary_weather.inc")
#include "common/legendary_weather.inc"
#endif
#endif
