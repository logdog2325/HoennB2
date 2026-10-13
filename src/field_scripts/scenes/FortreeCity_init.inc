// Fortree City's map scripts (zone 16; Sapphire FortreeCity_MapScripts): zone init =
// story script 1, field load / return = script 3 (C7_KECLEON_HIDDEN 0 again), scene condition C7_KECLEON_HIDDEN 0 =
// script 2 (hides the invisible Kecleons; scenes/ch7_lib.inc). ch7, 2026-10-07.
    MapScript 2, 1
    MapScript 3, 3
    MapScript 4, 3
    MapScriptConditions FC_Conditions
    MapScriptsEnd
FC_Conditions:
    MapScriptCondition 0x4010, 0, 2     // C7_KECLEON_HIDDEN
    MapScriptConditionsEnd
