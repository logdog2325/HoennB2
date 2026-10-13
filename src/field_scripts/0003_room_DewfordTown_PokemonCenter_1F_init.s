// Map scripts of DewfordTown_PokemonCenter_1F (zone 1; installed by b2tools/patches/interiors.py): zone init = script 6
// (before the people appear: Mr. Briney's whereabouts / the old man's sprite).
#include "asm/field_script.inc"

    MapScript 2, 6
    MapScriptConditions DC_Conditions
    MapScriptsEnd
DC_Conditions:
    MapScriptCondition 0x4003, 1, 7                // stranded in Dewford by the blackout bug: back to Rustboro
    MapScriptConditionsEnd
    .balign 4, 0
