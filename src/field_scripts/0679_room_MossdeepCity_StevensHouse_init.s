// Map scripts of MossdeepCity_StevensHouse (zone 339; installed by b2tools/patches/interiors.py), chapter Ch9: Sapphire
// ON_TRANSITION (Steven stands at (6,5) once he has given Dive) = zone init = script 8 of 0678_room_MossdeepCity_
// StevensHouse.s; ON_FRAME_TABLE VAR_STEVENS_HOUSE_STATE 0 = script 7 (Steven gives Dive on the first entry). ON_LOAD
// (the letter's table tile) is not built.
#include "asm/field_script.inc"
#include "hoenn.h"

    MapScript 2, 8
    MapScriptConditions Conditions
    MapScriptsEnd

Conditions:
#ifdef HOENN_EMERALD
    MapScriptCondition VAR_STEVENS_HOUSE_STATE, 1, 7    // EMERALD: the Dive is due at 1 (the Space Center's end sets it; 2 = given), 0 = not yet
#else
    MapScriptCondition VAR_STEVENS_HOUSE_STATE, 0, 7
#endif
    MapScriptConditionsEnd
    .balign 4, 0
