// Sky Pillar's outside: map scripts (zone 98). Emerald only (emerald_ch10, 2026-10-12; scenes/SkyPillar_Outside.inc): zone init
// = script 1, the Wallace scene on arrival while VAR_SOOTOPOLIS_CITY_STATE (this port's VAR_SOOTOPOLIS_STATE) is 3 = script 2.
// Sapphire and Ruby: no map scripts (the same bytes as the generator's empty table: MapScriptsEnd + padding).
#ifdef HOENN_EMERALD
    MapScript 2, 1
    MapScriptConditions SPO_Conditions
    MapScriptsEnd
SPO_Conditions:
    MapScriptCondition VAR_SOOTOPOLIS_STATE, 3, 2
    MapScriptConditionsEnd
#else
    MapScriptsEnd
#endif
