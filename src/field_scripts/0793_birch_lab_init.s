// Prof. Birch's Lab map scripts (init file 0793; installed by b2tools/patches/interiors.py).
// Sapphire LittlerootTown_ProfessorBirchsLab_MapScripts: OnTransition -> MapScript 2 = script 10 (the rival's
// sprite); OnFrame VAR_BIRCH_LAB_STATE 4 -> MapScriptConditions = script 12 (the Pokédex). State 2 (the starter) is
// not here: Route 101 reserves script 11 with its warp.
#include "asm/field_script.inc"
#include "hoenn.h"

    MapScript 2, 10
    MapScriptConditions Conditions
    MapScriptsEnd

Conditions:
    MapScriptCondition VAR_BIRCH_LAB_STATE, 4, 12
#ifdef HOENN_EMERALD
    MapScriptCondition VAR_DEX_UPGRADE_JOHTO_STARTER_STATE, 4, 15   // Emerald: Birch offers the Johto starters (scenes/emerald/BirchLab_JohtoStarters.inc; switched off until the Lab has its table)
#endif
    MapScriptConditionsEnd
    .balign 4, 0
