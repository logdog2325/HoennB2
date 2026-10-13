// BattleFrontier_BattlePikeRoomNormal map scripts (frontier_pike, Emerald only): the zone init = Emerald's
// ON_TRANSITION (pike_setroomobjects, the people's places by room type) and ON_WARP (_InitRoomObjects: who is hidden)
// -> script 7; ON_FRAME = the condition PK_W_STATE (map-local work 0x4000) 0 -> script 6 (the room's event).
#include "asm/field_script.inc"

    MapScript 2, 7
    MapScriptConditions Conditions_PK
    MapScriptsEnd

Conditions_PK:
    MapScriptCondition 0x4000, 0, 6
    MapScriptConditionsEnd
    .byte 0x00
    .byte 0x00
