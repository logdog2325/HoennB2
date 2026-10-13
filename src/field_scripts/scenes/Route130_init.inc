// Route 130's map scripts (Sapphire Route130_MapScripts): zone init = story script 1 (Mirage Island, scenes/Route130.inc);
// the island's layout swapped in the field = story script 2 while VAR_MIRAGE_REDRAW is 1 or 2 (postgame_maps 2026-10-07).
    MapScript 2, 1
    MapScriptConditions R130_Conditions
    MapScriptsEnd
R130_Conditions:
    MapScriptCondition VAR_MIRAGE_REDRAW, 1, 2
    MapScriptCondition VAR_MIRAGE_REDRAW, 2, 2
    MapScriptConditionsEnd
