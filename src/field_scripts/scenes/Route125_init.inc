// Route125's map scripts (zone 194; Sapphire Route125_MapScripts: ON_TRANSITION): zone init = story script 1
// (scenes/Route125.inc R125_Init). Chapter Ch9, ch9 agent, 2026-10-07.
    MapScript 2, 1
#ifdef HOENN_EMERALD                // Emerald's abnormal weather (emerald_ch12_13): pokeemerald's OnTransition/OnLoad lines of
#include "scenes/emerald/abnormal_weather.inc"   // AbnormalWeather_* and map_script_2 VAR_SHOULD_END_ABNORMAL_WEATHER 1
    MapScript 2, AW_GLOBAL_ZONE_INIT
    MapScriptConditions AW_Conditions
#endif
    MapScriptsEnd
#ifdef HOENN_EMERALD
AW_Conditions:
    MapScriptCondition VAR_SHOULD_END_ABNORMAL_WEATHER, 1, AW_GLOBAL_CLEANUP
    MapScriptConditionsEnd
#endif
