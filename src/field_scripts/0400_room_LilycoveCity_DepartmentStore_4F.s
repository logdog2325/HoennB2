// LilycoveCity_DepartmentStore_4F (zone 200): shops agent, b2tools/shops_rooms.py (people and signs with one Sapphire message,
// shop clerks with Sapphire's lists: data/hoenn_shops.json). Messages: src/text/script/0258_room_LilycoveCity_DepartmentStore_4F.txt
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_trainers.h"  // ch8a
#include "hoenn_story.inc"  // ch8a
#include "scenes/ch8a_lib.inc"  // ch8a

    ScriptEntry Script_1
    ScriptEntry Script_2
    ScriptEntry Script_3
    ScriptEntry Script_4
    ScriptEntry Script_5
    ScriptEntry DS4_Init                // 6: zone init (0401): VAR_DEPT_STORE_FLOOR = 3, for the elevator  // story:
    ScriptEntriesEnd

Script_1:                                      // gentleman (0,2), Sapphire LilycoveCity_DepartmentStore_4F_EventScript_Gentleman
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

Script_2:                                      // woman_3 (6,2), Sapphire LilycoveCity_DepartmentStore_4F_EventScript_Woman
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

Script_3:                                      // youngster (13,4), Sapphire LilycoveCity_DepartmentStore_4F_EventScript_Youngster
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

Script_4:                                      // clerk woman_4 (7,6), Sapphire LilycoveCity_DepartmentStore_4F_EventScript_ClerkLeft
    ActorsPauseAll
    SEPlay SEQ_SE_MESSAGE
    ActorSetEyeToEye
    VMStackPush 0x8000
    VMStackPush 0x8001
    WorkSet 0x8000, 16                  // LilycoveCity_DepartmentStore_4F_Pokemart_AttackTMs
    WorkSet 0x8001, 2
    RTCallGlobal 10110
    VMStackPop 0x8001
    VMStackPop 0x8000
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_5:                                      // clerk woman_4 (9,6), Sapphire LilycoveCity_DepartmentStore_4F_EventScript_ClerkRight
    ActorsPauseAll
    SEPlay SEQ_SE_MESSAGE
    ActorSetEyeToEye
    VMStackPush 0x8000
    VMStackPush 0x8001
    WorkSet 0x8000, 17                  // LilycoveCity_DepartmentStore_4F_Pokemart_DefenseTMs
    WorkSet 0x8001, 2
    RTCallGlobal 10110
    VMStackPop 0x8001
    VMStackPop 0x8000
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt
    .balign 4, 0

// ---- story (chapter Ch8 part 8a, ch8a agent: Sapphire's story scripts of this room; generators must keep
// everything from this line on; entries above marked "// story:")
// The shops agent's people and clerks are above. Zone init: the elevator's current floor (Sapphire's
// SetDepartmentStoreFloorVar reads the dynamic warp; every floor sets its own number as it loads).

DS4_Init:
    h_setvar VAR_DEPT_STORE_FLOOR, 3
    VMHalt
    .balign 4, 0
