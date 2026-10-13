// FarawayIsland_Interior's map scripts (Emerald: ON_TRANSITION, ON_FRAME_TABLE VAR_TEMP_1 0 -> FindMew; ON_RESUME /
// ON_RETURN_TO_FIELD are done by ev_legend_battle): zone init = script 1, Black 2's temporary work 0x4001 = 0 -> script 2.
    MapScript 2, 1
    MapScriptConditions FI_Conditions
    MapScriptsEnd
FI_Conditions:
    MapScriptCondition 0x4001, 0, 2
    MapScriptConditionsEnd
