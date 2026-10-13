// LavaridgeTown_HerbShop (zone 149): shops agent, b2tools/shops_rooms.py (people and signs with one Sapphire message,
// shop clerks with Sapphire's lists: data/hoenn_shops.json). Messages: src/text/script/0168_room_LavaridgeTown_HerbShop.txt
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_story.inc"

    ScriptEntry Script_1
    ScriptEntry Script_2
    ScriptEntry LH_OldMan       // 3: old man (LavaridgeTown_HerbShop_EventScript_OldMan, Charcoal), ch5
    ScriptEntriesEnd

Script_1:                                      // clerk woman_3 (3,2), Sapphire LavaridgeTown_HerbShop_EventScript_Clerk
    ActorsPauseAll
    SEPlay SEQ_SE_MESSAGE
    ActorSetEyeToEye
    ParentActorMsg MSGFILE_SCRIPT, 0, 0, 0
    LastKeyWait
    ActorMsgClose
    VMStackPush 0x8000
    VMStackPush 0x8001
    WorkSet 0x8000, 11                  // LavaridgeTown_HerbShop_Pokemart
    WorkSet 0x8001, 1
    RTCallGlobal 10110
    VMStackPop 0x8001
    VMStackPop 0x8000
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_2:                                      // old_man_1 (9,3), Sapphire LavaridgeTown_HerbShop_EventScript_ExpertM
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
    .balign 4, 0

// ---- story
// Chapter Ch5 (ch5 agent, 2026-10-07): the old man (Sapphire object 2, data/story/ch5.json uid 2) gives Charcoal.
// Text: lines 2-4 of src/text/script/0168_room_LavaridgeTown_HerbShop.txt.
LH_OldMan:                                       // LavaridgeTown_HerbShop_EventScript_OldMan
    h_lock
    SEPlay SEQ_SE_MESSAGE
    h_faceplayer
    h_goto_if_set FLAG_RECEIVED_CHARCOAL, L_LH_Explain
    h_msgbox 2                                   // You've come to look at herbal medicine in Lavaridge? ... Take this!
    h_closemessage
    h_giveitem ITEM_CHARCOAL
    h_goto_if_eq HLIB_RESULT, 0, L_LH_BagFull
    h_setflag FLAG_RECEIVED_CHARCOAL
    h_release
L_LH_BagFull:                                    // Common_EventScript_ShowBagIsFull
    h_msgbox 4                                   // Too bad! The Bag is full...
    h_release
L_LH_Explain:                                    // LavaridgeTown_HerbShop_EventScript_ExplainCharcoal
    h_msgbox 3                                   // That Charcoal I gave you, it's used for making herbal medicine. ...
    h_release
    .balign 4, 0
