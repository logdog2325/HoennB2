// Route 104's map scripts (Sapphire Route104_MapScripts): zone init = story script 1 (Route104_OnTransition); OnFrame
// VAR_BOARD_BRINEY_BOAT_ROUTE104_STATE 1 = story script 4, chapter Ch2's boat ride (scenes/Route104.inc).
    MapScript 2, 1
    MapScriptConditions R104_Conditions
    MapScriptsEnd
R104_Conditions:
    MapScriptCondition VAR_BOARD_BRINEY_BOAT_ROUTE104_STATE, 1, 4
    MapScriptConditionsEnd
