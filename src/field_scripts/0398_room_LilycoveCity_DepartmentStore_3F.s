// LilycoveCity_DepartmentStore_3F (zone 199): shops agent, b2tools/shops_rooms.py (people and signs with one Sapphire message,
// shop clerks with Sapphire's lists: data/hoenn_shops.json). Messages: src/text/script/0257_room_LilycoveCity_DepartmentStore_3F.txt
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
    ScriptEntry DS3_Init                // 6: zone init (0399): VAR_DEPT_STORE_FLOOR = 2, for the elevator  // story:
    ScriptEntriesEnd

Script_1:                                      // running_triathlete_m (0,5), Sapphire LilycoveCity_DepartmentStore_3F_EventScript_TriathleteM
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

Script_2:                                      // man_3 (7,7), Sapphire LilycoveCity_DepartmentStore_3F_EventScript_PokefanM
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

Script_3:                                      // woman_7 (13,5), Sapphire LilycoveCity_DepartmentStore_3F_EventScript_Woman
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

Script_4:                                      // clerk woman_4 (8,2), Sapphire LilycoveCity_DepartmentStore_3F_EventScript_ClerkLeft
    ActorsPauseAll
    SEPlay SEQ_SE_MESSAGE
    ActorSetEyeToEye
    VMStackPush 0x8000
    VMStackPush 0x8001
    WorkSet 0x8000, 14                  // LilycoveCity_DepartmentStore_3F_Pokemart_Vitamins
    WorkSet 0x8001, 1
    RTCallGlobal 10110
    VMStackPop 0x8001
    VMStackPop 0x8000
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_5:                                      // clerk woman_4 (10,2), Sapphire LilycoveCity_DepartmentStore_3F_EventScript_ClerkRight
    ActorsPauseAll
    SEPlay SEQ_SE_MESSAGE
    ActorSetEyeToEye
    VMStackPush 0x8000
    VMStackPush 0x8001
    WorkSet 0x8000, 15                  // LilycoveCity_DepartmentStore_3F_Pokemart_StatBoosters
    WorkSet 0x8001, 1
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

DS3_Init:
    h_setvar VAR_DEPT_STORE_FLOOR, 2
    VMHalt
    .balign 4, 0
