// BattleFrontier_BattlePyramidFloor map scripts (frontier_pyramid, Emerald only): the zone init = Emerald's
// ON_TRANSITION (the floor's objects, the Battle Bag) -> script 21; the field loads (MapScript 4 after a warp: the
// darkness and the entrance, 3 back from a battle or a menu: the darkness) -> 22 / 23; ON_RESUME = the condition
// PY_W_STATE (map-local work 0x4014, 0 after a map change) 0 -> script 24.
#include "asm/field_script.inc"

    MapScript 2, 21
    MapScript 4, 22
    MapScript 3, 23
    MapScriptConditions Conditions_PY
    MapScriptsEnd

Conditions_PY:
    MapScriptCondition 0x4014, 0, 24
    MapScriptConditionsEnd
    .byte 0x00
    .byte 0x00
