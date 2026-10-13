// Route 120's map scripts (zone 474; Sapphire Route120_MapScripts: ON_TRANSITION = Gabby & Ty's place, ON_RESUME = the
// Kecleon removal, ON_LOAD = the metatiles): zone init = story script 1, field load / return = script 11
// (C7_KECLEON_HIDDEN 0 again), scene condition C7_KECLEON_HIDDEN 0 = script 10 (hides the invisible Kecleons;
// scenes/ch7_lib.inc). ch7, 2026-10-07.
    MapScript 2, 1
    MapScript 3, 11
    MapScript 4, 11
    MapScriptConditions R120_Conditions
    MapScriptsEnd
R120_Conditions:
    MapScriptCondition 0x4010, 0, 10    // C7_KECLEON_HIDDEN
    MapScriptConditionsEnd
