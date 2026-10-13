// Route 129's map scripts: Sapphire has none; Emerald's (emerald_ch12_13, 2026-10-12): the abnormal weather (zone init +
// the frame script of its end, scenes/emerald/abnormal_weather.inc). Sapphire / Ruby: an empty table, as before.
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
