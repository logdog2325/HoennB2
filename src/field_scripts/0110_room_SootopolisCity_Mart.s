// SootopolisCity_Mart (zone 55): shops agent, b2tools/shops_rooms.py (people and signs with one Sapphire message,
// shop clerks with Sapphire's lists: data/hoenn_shops.json). Messages: src/text/script/0064_room_SootopolisCity_Mart.txt
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_trainers.h"  // ch10
#include "hoenn_key_items.h"  // ch10
#include "hoenn_story.inc"  // ch10

    ScriptEntry Script_1
    ScriptEntry M_FatMan  // 2: object 2 (SootopolisCity_Mart_EventScript_FatMan)  // story:
    ScriptEntry M_Gentleman  // 3: object 3 (SootopolisCity_Mart_EventScript_Gentleman)  // story:
    ScriptEntriesEnd

Script_1:                                      // clerk mart_employee (1,3), Sapphire SootopolisCity_Mart_EventScript_Clerk
    ActorsPauseAll
    SEPlay SEQ_SE_MESSAGE
    ActorSetEyeToEye
    VMStackPush 0x8000
    VMStackPush 0x8001
    WorkSet 0x8000, 24                  // SootopolisCity_Mart_Pokemart
    WorkSet 0x8001, 1
    RTCallGlobal 10110
    VMStackPop 0x8001
    VMStackPop 0x8000
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt
    .balign 4, 0

// ---- story (chapter Ch10, ch10 agent 2026-10-07; Sapphire data/maps/SootopolisCity_Mart/scripts.inc; generators keep everything from
// this line on; entries above marked "// story:"). Messages: 0064_room_SootopolisCity_Mart.txt
#include "scenes/ch10_lib.inc"
#define T_TooScaryOutside 1
#define T_PPUpIsGreat 2
#define T_DidSomethingAwaken 3
#define T_FullRestoreItemOfDreams 4
M_FatMan:                               // SootopolisCity_Mart_EventScript_FatMan
    c10_talk
    h_goto_if_set FLAG_LEGENDARY_BATTLE_COMPLETED, L_M_FatManCalm
    h_goto_if_unset FLAG_LEGEND_ESCAPED_SEAFLOOR_CAVERN, L_M_FatManCalm
    h_msgbox T_TooScaryOutside
    h_release
L_M_FatManCalm:
    h_msgbox T_PPUpIsGreat
    h_release
M_Gentleman:                            // SootopolisCity_Mart_EventScript_Gentleman
    c10_talk
    h_goto_if_set FLAG_LEGENDARY_BATTLE_COMPLETED, L_M_GentlemanCalm
    h_goto_if_unset FLAG_LEGEND_ESCAPED_SEAFLOOR_CAVERN, L_M_GentlemanCalm
    h_msgbox T_DidSomethingAwaken
    h_release
L_M_GentlemanCalm:
    h_msgbox T_FullRestoreItemOfDreams
    h_release
    .balign 4, 0
