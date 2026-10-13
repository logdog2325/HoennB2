// RustboroCity_Mart (zone 589): shops agent, b2tools/shops_rooms.py (people and signs with one Sapphire message,
// shop clerks with Sapphire's lists: data/hoenn_shops.json). Messages: src/text/script/0345_room_RustboroCity_Mart.txt
#include "asm/field_script.inc"
#include "hoenn.h"

    ScriptEntry Script_1
    ScriptEntry Script_2
    ScriptEntry Script_3
    ScriptEntry Script_4
    ScriptEntriesEnd

Script_1:                                      // clerk mart_employee (1,3), Sapphire RustboroCity_Mart_EventScript_Clerk
    ActorsPauseAll
    SEPlay SEQ_SE_MESSAGE
    ActorSetEyeToEye
    VMStackPush 0x8000
    VMStackPush 0x8001
    WorkSet 0x8000, 9                  // RustboroCity_Mart_Pokemart_Basic
#ifdef FLAG_MET_DEVON_EMPLOYEE                   // Sapphire: the bigger list once FLAG_MET_DEVON_EMPLOYEE is set
    VMStackPushFlag FLAG_MET_DEVON_EMPLOYEE
    VMStackPushConst 1
    VMStackCmp CMP_NE                   // (Ch1: CMP_STACK jumps when the compare is false: NE = flag set)
    VMJumpIf CMP_STACK, L_Shop1_Expanded
    VMJump L_Shop1_Open
L_Shop1_Expanded:
    WorkSet 0x8000, 13                 // RustboroCity_Mart_Pokemart_Expanded
L_Shop1_Open:
#endif
    WorkSet 0x8001, 1
    RTCallGlobal 10110
    VMStackPop 0x8001
    VMStackPop 0x8000
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_2:                                      // boy_1 (2,5), Sapphire RustboroCity_Mart_EventScript_Boy
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

Script_3:                                      // woman_2 (8,4), Sapphire RustboroCity_Mart_EventScript_PokefanF
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

Script_4:                                      // bug_catcher (8,2), Sapphire RustboroCity_Mart_EventScript_BugCatcher
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
