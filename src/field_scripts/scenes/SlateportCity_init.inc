// Slateport City's map scripts (Sapphire SlateportCity_MapScripts: MAP_SCRIPT_ON_TRANSITION): zone init = story
// script 1 (scenes/SlateportCity.inc Story_Init). ch3a, 2026-10-07.
    MapScript 2, 1
#ifdef HOENN_EMERALD
    MapScriptConditions SC_EmConditions   // Emerald: Scott outside the Museum (scenes/emerald/SlateportCity.inc)
#endif
    MapScriptsEnd
#ifdef HOENN_EMERALD
SC_EmConditions:
    MapScriptCondition VAR_SLATEPORT_OUTSIDE_MUSEUM_STATE, 1, 29
    MapScriptConditionsEnd
#endif
