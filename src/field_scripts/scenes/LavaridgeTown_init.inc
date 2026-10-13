// Lavaridge Town's map scripts (Sapphire LavaridgeTown_MapScripts): ON_TRANSITION -> zone init = story script 1
// (scenes/LavaridgeTown.inc LV_Init); ON_FRAME_TABLE VAR_LAVARIDGE_RIVAL_STATE 1 -> script 2 (the Go-Goggles). ch5.
    MapScript 2, 1
    MapScriptConditions LV_Conditions
    MapScriptsEnd
LV_Conditions:
    MapScriptCondition VAR_LAVARIDGE_RIVAL_STATE, 1, 2
    MapScriptConditionsEnd
