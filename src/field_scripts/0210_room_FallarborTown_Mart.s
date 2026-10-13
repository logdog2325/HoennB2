// FallarborTown_Mart (zone 105): shops agent, b2tools/shops_rooms.py (people and signs with one Sapphire message,
// shop clerks with Sapphire's lists: data/hoenn_shops.json). Messages: src/text/script/0124_room_FallarborTown_Mart.txt
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_trainers.h"  // ch4
#include "hoenn_story.inc"  // ch4
#include "scenes/ch4_lib.inc"  // ch4

    ScriptEntry Script_1
    ScriptEntry Script_2
    ScriptEntry Script_3
    ScriptEntry FM_Skitty               // 4: object 4 (FallarborTown_Mart_EventScript_Skitty)  // story:
    ScriptEntriesEnd

Script_1:                                      // clerk mart_employee (1,3), Sapphire FallarborTown_Mart_EventScript_Clerk
    ActorsPauseAll
    SEPlay SEQ_SE_MESSAGE
    ActorSetEyeToEye
    VMStackPush 0x8000
    VMStackPush 0x8001
    WorkSet 0x8000, 3                  // FallarborTown_Mart_Items
    WorkSet 0x8001, 1
    RTCallGlobal 10110
    VMStackPop 0x8001
    VMStackPop 0x8000
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_2:                                      // woman_3 (5,3), Sapphire FallarborTown_Mart_EventScript_Woman
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

Script_3:                                      // man_3 (9,6), Sapphire FallarborTown_Mart_EventScript_PokefanM
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

// ---- story (chapter Ch4, ch4 agent 2026-10-07: Sapphire data/maps/FallarborTown_Mart/scripts.inc; generators keep everything
// from this line on; entries above marked "// story:"). The Skitty (a cry: not a generated person): data/story/ch4.json
// uid 4. Text line 2 (0-1 are the generated people's).
#define T_Skitty 2              // FallarborTown_Mart_Text_Skitty
FM_Skitty:
    c4_mon_cry SPECIES_SKITTY, T_Skitty
    .balign 4, 0
