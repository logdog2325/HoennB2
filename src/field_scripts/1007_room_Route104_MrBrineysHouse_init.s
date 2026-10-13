// Route104_MrBrineysHouse's map scripts (Sapphire Route104_MrBrineysHouse_MapScripts; chapter Ch2): zone init =
// script 4 of 1006_room_Route104_MrBrineysHouse.s; condition: map-local work 0x4000 (BH_CHASE) 1, set by the zone init
// after the Rusturf rescue = script 7 (Mr. Briney and Peeko start walking around the table). b2tools/patches/interiors.py
// installs this table.
#include "asm/field_script.inc"
#include "hoenn.h"

    MapScript 2, 4
    MapScriptConditions BH_Conditions
    MapScriptsEnd
BH_Conditions:
#if (HOENN_TEST_CH2 + 0) >= 2
    MapScriptCondition VAR_RUSTBORO_STATE, 0, 6 // test builds only (scenes/ch2_test.inc, stages 2 and 3)
#endif
    MapScriptCondition 0x4000, 1, 7             // BH_CHASE
    MapScriptConditionsEnd
    .balign 4, 0
