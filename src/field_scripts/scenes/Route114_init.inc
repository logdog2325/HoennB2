// Route114's map scripts (missing_objects 2026-10-08): the zone init is global script 8298, the berry trees' new-day
// reset (converter/gen_hidden_items.py): Sapphire has no map script here that Black 2 needs.
    MapScript 2, 8298
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
