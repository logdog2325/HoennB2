// Route121_SafariZoneEntrance's map scripts (Sapphire ON_FRAME_TABLE: VAR_SAFARI_ZONE_STATE 1 = back from the Safari Game,
// script 5 Story_SZE_Exit of 1138_room_Route121_SafariZoneEntrance.s; chapter Ch8 part 8b). b2tools/patches/interiors.py
// installs this table.
#include "asm/field_script.inc"
#include "hoenn.h"

    MapScriptConditions Conditions
    MapScriptsEnd

Conditions:
    MapScriptCondition VAR_SAFARI_ZONE_STATE, 1, 5
    MapScriptConditionsEnd
    .balign 4, 0
