// Petalburg City's map scripts (Sapphire PetalburgCity_MapScripts): zone init = story script 1, OnFrame table =
// MapScriptConditions (scenes/PetalburgCity.inc).
    MapScript 2, 1
    MapScriptConditions PB_Conditions
    MapScriptsEnd
PB_Conditions:
    MapScriptCondition VAR_PETALBURG_STATE, 2, 2
#ifdef HOENN_EMERALD
    MapScriptCondition VAR_PETALBURG_STATE, 4, 10   // Wally's father leads the player to his house (scenes/emerald/PetalburgCity.inc)
#endif
    MapScriptConditionsEnd
