// BattleFrontier_BattlePyramidLobby map scripts (frontier_pyramid, Emerald only): Emerald's ON_FRAME table = the
// condition PY_W_STATE (map-local work 0x4014, 0 after every map change) 0 -> script 7 (the challenge's outcome, run once
// per visit).
#include "asm/field_script.inc"

    MapScriptConditions Conditions_PY
    MapScriptsEnd

Conditions_PY:
    MapScriptCondition 0x4014, 0, 7
    MapScriptConditionsEnd
    .byte 0x00
    .byte 0x00
