// FortreeCity_Mart (zone 143): shops agent, b2tools/shops_rooms.py (people and signs with one Sapphire message,
// shop clerks with Sapphire's lists: data/hoenn_shops.json). Messages: src/text/script/0162_room_FortreeCity_Mart.txt
#include "asm/field_script.inc"
#include "hoenn.h"

    ScriptEntry Script_1
    ScriptEntry Script_2
    ScriptEntry Script_3
    ScriptEntry Script_4
    ScriptEntriesEnd

Script_1:                                      // clerk mart_employee (1,3), Sapphire FortreeCity_Mart_EventScript_Clerk
    ActorsPauseAll
    SEPlay SEQ_SE_MESSAGE
    ActorSetEyeToEye
    VMStackPush 0x8000
    VMStackPush 0x8001
    WorkSet 0x8000, 4                  // FortreeCity_Mart_Items
    WorkSet 0x8001, 1
    RTCallGlobal 10110
    VMStackPop 0x8001
    VMStackPop 0x8000
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_2:                                      // woman_3 (9,3), Sapphire FortreeCity_Mart_EventScript_Woman
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    ActorSetEyeToEye
    ParentActorMsg MSGFILE_SCRIPT, 0, 0, 0
    LastKeyWait
    ActorMsgClose
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_3:                                      // girl_3 (8,5), Sapphire FortreeCity_Mart_EventScript_Girl
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    ActorSetEyeToEye
    ParentActorMsg MSGFILE_SCRIPT, 1, 0, 0
    LastKeyWait
    ActorMsgClose
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_4:                                      // boy_2 (5,6), Sapphire FortreeCity_Mart_EventScript_Boy
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    ActorSetEyeToEye
    ParentActorMsg MSGFILE_SCRIPT, 2, 0, 0
    LastKeyWait
    ActorMsgClose
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt
    .balign 4, 0
