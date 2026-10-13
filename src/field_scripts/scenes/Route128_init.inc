// Route 128's map scripts (zone 230; Sapphire Route128_MapScripts: ON_TRANSITION, ON_FRAME_TABLE): zone init = story script 1
// (scenes/Route128.inc R128_Init), scene condition VAR_ROUTE128_STATE 1 = script 2 (the Archie / Maxie / Steven scene
// after Kyogre woke). Chapter Ch10, ch10 agent, 2026-10-07.
    MapScript 2, 1
    MapScriptConditions R128_Conditions
    MapScriptsEnd
R128_Conditions:
    MapScriptCondition VAR_ROUTE128_STATE, 1, 2
    MapScriptConditionsEnd
