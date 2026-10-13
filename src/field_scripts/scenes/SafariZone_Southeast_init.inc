// The Safari Zone south-east area's map scripts (Sapphire SafariZone_Southeast_MapScripts): ON_TRANSITION = zone init
// (story script 1), ON_FRAME_TABLE = scene condition VAR_SAFARI_ZONE_STATE 2 -> script 2 (the arrival).
    MapScript 2, 1
    MapScriptConditions Conditions
    MapScriptsEnd

Conditions:
    MapScriptCondition VAR_SAFARI_ZONE_STATE, 2, 2
    MapScriptConditionsEnd
    .balign 4, 0
