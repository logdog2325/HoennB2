// Route 118's map scripts (zone 446; Sapphire Route118_MapScripts: ON_TRANSITION = Gabby & Ty's place): zone init =
// story script 1 (scenes/Route118.inc R118_Init). ch7, 2026-10-07.
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
