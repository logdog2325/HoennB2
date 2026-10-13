// Sootopolis City's map scripts (zone 319; Sapphire SootopolisCity_MapScripts: ON_LOAD, ON_TRANSITION, ON_RESUME): zone init =
// story script 1 (scenes/SootopolisCity.inc SC_Init: the people's places and the closed doors). The dive spot of
// ON_RESUME (setdivewarp) is the dive agent's table. Chapter Ch10, ch10 agent, 2026-10-07.
#ifdef HOENN_EMERALD
// Emerald (emerald_ch10, 2026-10-12; scenes/emerald/SootopolisCity.inc): zone init = script 1 (SE_Init), ON_FRAME_TABLE as
// scene conditions: VAR_SOOTOPOLIS_CITY_STATE 1 = script 19 (the legends' fight), VAR_SKY_PILLAR_STATE 1 = script 20 (Rayquaza)
    MapScript 2, 1
    MapScriptConditions SE_Conditions
    MapScriptsEnd
SE_Conditions:
    MapScriptCondition VAR_SOOTOPOLIS_STATE, 1, 19
    MapScriptCondition VAR_SKY_PILLAR_STATE, 1, 20
    MapScriptConditionsEnd
#else
    MapScript 2, 1
    MapScriptsEnd
#endif
