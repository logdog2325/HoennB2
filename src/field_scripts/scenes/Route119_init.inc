// Route 119's map scripts (zone 463; Sapphire Route119_MapScripts: ON_TRANSITION = the Institute workers, ON_RESUME =
// the Kecleon removal): zone init = story script 1, field load / return = script 6 (C7_KECLEON_HIDDEN 0 again), scene
// condition C7_KECLEON_HIDDEN 0 = script 5 (hides the invisible Kecleon; scenes/ch7_lib.inc). ch7, 2026-10-07.
    MapScript 2, 1
    MapScript 3, 6
    MapScript 4, 6
    MapScriptConditions R119_Conditions
    MapScriptsEnd
R119_Conditions:
    MapScriptCondition 0x4010, 0, 5     // C7_KECLEON_HIDDEN
    MapScriptConditionsEnd
