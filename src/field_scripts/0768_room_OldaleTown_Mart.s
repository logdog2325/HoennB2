// OldaleTown_Mart (zone 384): shops agent, b2tools/shops_rooms.py (people and signs with one Sapphire message,
// shop clerks with Sapphire's lists: data/hoenn_shops.json). Messages: src/text/script/0596_room_OldaleTown_Mart.txt
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_trainers.h"
#include "hoenn_story.inc"

    ScriptEntry Script_1
    ScriptEntry Script_2
    ScriptEntry Script_3    // woman (OldaleTown_Mart_EventScript_Woman), chapter Ch1
    ScriptEntriesEnd

Script_1:                                      // clerk mart_employee (1,3), Sapphire OldaleTown_Mart_EventScript_Clerk
    ActorsPauseAll
    SEPlay SEQ_SE_MESSAGE
    ActorSetEyeToEye
    VMStackPush 0x8000
    VMStackPush 0x8001
    WorkSet 0x8000, 1                  // OldaleTown_Mart_Pokemart_Basic
#ifdef FLAG_ADVENTURE_STARTED                   // Sapphire: the bigger list once FLAG_ADVENTURE_STARTED is set
    VMStackPushFlag FLAG_ADVENTURE_STARTED
    VMStackPushConst 1
    VMStackCmp CMP_NE                   // (Ch1: CMP_STACK jumps when the compare is false: NE = flag set)
    VMJumpIf CMP_STACK, L_Shop1_Expanded
    VMJump L_Shop1_Open
L_Shop1_Expanded:
    WorkSet 0x8000, 0                 // OldaleTown_Mart_Pokemart_Expanded
L_Shop1_Open:
#endif
    WorkSet 0x8001, 1
    RTCallGlobal 10110
    VMStackPop 0x8001
    VMStackPop 0x8000
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_2:                                      // boy_1 (9,4), Sapphire OldaleTown_Mart_EventScript_Boy
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
    .balign 4, 0

// ---- story (chapter Ch1)
Script_3:                                      // woman_7 (5,5), Sapphire OldaleTown_Mart_EventScript_Woman (lock, faceplayer)
    h_lock
    SEPlay SEQ_SE_MESSAGE
    h_faceplayer
    h_goto_if_set FLAG_ADVENTURE_STARTED, L_OM_InStock
    h_msgbox 1                                  // The clerk says they're all sold out. I can't buy any Poké Balls.
    h_release
L_OM_InStock:
    h_msgbox 2                                  // I'm going to buy a bunch of Poké Balls and catch a bunch of Pokémon!
    h_release
    .balign 4, 0
