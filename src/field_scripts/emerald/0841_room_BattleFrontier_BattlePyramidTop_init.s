// BattleFrontier_BattlePyramidTop map scripts (frontier_pyramid, Emerald only): the zone init = Emerald's ON_TRANSITION /
// ON_WARP (the Battle Bag, Brandon shown only when the Brain is ready) -> script 6; every field load: no darkness ->
// script 7; ON_RESUME = the condition PY_W_STATE (map-local work 0x4014, 0 after a map change) 0 -> script 4.
#include "asm/field_script.inc"

    MapScript 2, 6
    MapScript 4, 7
    MapScript 3, 7
    MapScriptConditions Conditions_PY
    MapScriptsEnd

Conditions_PY:
    MapScriptCondition 0x4014, 0, 4
    MapScriptConditionsEnd
    .byte 0x00
    .byte 0x00
