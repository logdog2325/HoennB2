// Inside of the moving truck (replaces script file 0788 of zone 394, a spare Nuvema interior).
// Messages are lines of src/text/script/0623_truck.txt (zone 394's text file). Room and signs: data/interiors/394.json
// (interiors patch): Script_1 = the box signs. Scripts 20-31 are the lead's (20 = leaving the truck, a trigger on
// Sapphire (3,1)-(3,3) = zone (11,9)-(11,11) while VAR_LITTLEROOT_INTRO_STATE == 0).
// A new game starts here (b2tools/patches/opening.py): the engine runs Script_29 before the map fades in and
// Script_30 after it (src/ov035/event_mapchange.c:205-247). Scripts 1-28 must exist so 29/30 resolve.
#include "asm/field_script.inc"

    ScriptEntry Script_1
    ScriptEntry Script_2
    ScriptEntry Script_3
    ScriptEntry Script_4
    ScriptEntry Script_5
    ScriptEntry Script_6
    ScriptEntry Script_7
    ScriptEntry Script_8
    ScriptEntry Script_9
    ScriptEntry Script_10
    ScriptEntry Script_11
    ScriptEntry Script_12
    ScriptEntry Script_13
    ScriptEntry Script_14
    ScriptEntry Script_15
    ScriptEntry Script_16
    ScriptEntry Script_17
    ScriptEntry Script_18
    ScriptEntry Script_19
    ScriptEntry Script_20
    ScriptEntry Script_21
    ScriptEntry Script_22
    ScriptEntry Script_23
    ScriptEntry Script_24
    ScriptEntry Script_25
    ScriptEntry Script_26
    ScriptEntry Script_27
    ScriptEntry Script_28
    ScriptEntry Script_29
    ScriptEntry Script_30
    ScriptEntry Script_31
    ScriptEntriesEnd

Script_1:                       // box sign (Sapphire's InsideOfTruck_EventScript_15FC8B)
    ActorsPauseAll
    SEPlay SEQ_SE_MESSAGE
    SystemMsg 0, 2
    LastKeyWait
    MsgWinCloseAll
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_2:
Script_3:
Script_4:
Script_5:
Script_6:
Script_7:
Script_8:
Script_9:
Script_10:
Script_11:
Script_12:
Script_13:
Script_14:
Script_15:
Script_16:
Script_17:
Script_18:
Script_19:
    VMHalt                      // free

Script_21:
Script_22:
Script_23:
Script_24:
Script_25:
Script_26:
Script_27:
Script_28:
    VMHalt

#define T_BASE 1
#include "scenes/truck.inc"
