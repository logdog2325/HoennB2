// PetalburgCity_Mart (zone 471): shops agent, b2tools/shops_rooms.py (people and signs with one Sapphire message,
// shop clerks with Sapphire's lists: data/hoenn_shops.json). Messages: src/text/script/0197_room_PetalburgCity_Mart.txt
#include "asm/field_script.inc"
#include "hoenn.h"

    ScriptEntry Script_1
    ScriptEntry Script_2
    ScriptEntry Script_3
    ScriptEntry Script_4
    ScriptEntriesEnd

Script_1:                                      // clerk mart_employee (1,3), Sapphire PetalburgCity_Mart_EventScript_Clerk
    ActorsPauseAll
    SEPlay SEQ_SE_MESSAGE
    ActorSetEyeToEye
    VMStackPush 0x8000
    VMStackPush 0x8001
    WorkSet 0x8000, 2                  // PetalburgCity_Mart_Pokemart_Basic
#ifdef FLAG_PETALBURG_MART_EXPANDED_ITEMS                   // Sapphire: the bigger list once FLAG_PETALBURG_MART_EXPANDED_ITEMS is set
    VMStackPushFlag FLAG_PETALBURG_MART_EXPANDED_ITEMS
    VMStackPushConst 1
    VMStackCmp CMP_NE                   // (Ch1: CMP_STACK jumps when the compare is false: NE = flag set)
    VMJumpIf CMP_STACK, L_Shop1_Expanded
    VMJump L_Shop1_Open
L_Shop1_Expanded:
    WorkSet 0x8000, 12                 // PetalburgCity_Mart_Pokemart_Expanded
L_Shop1_Open:
#endif
    WorkSet 0x8001, 1
    RTCallGlobal 10110
    VMStackPop 0x8001
    VMStackPop 0x8000
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_2:                                      // man_1 (9,4), Sapphire PetalburgCity_Mart_EventScript_Man
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

Script_3:                                      // boy_1 (6,3), Sapphire PetalburgCity_Mart_EventScript_Boy
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

Script_4:                                      // woman_3 (5,5), Sapphire PetalburgCity_Mart_EventScript_Woman
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
