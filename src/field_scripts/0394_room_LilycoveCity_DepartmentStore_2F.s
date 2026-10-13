// LilycoveCity_DepartmentStore_2F (zone 197): shops agent, b2tools/shops_rooms.py (people and signs with one Sapphire message,
// shop clerks with Sapphire's lists: data/hoenn_shops.json). Messages: src/text/script/0255_room_LilycoveCity_DepartmentStore_2F.txt
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
    ScriptEntry DS2_Init                // 6: zone init (0395): VAR_DEPT_STORE_FLOOR = 1, for the elevator  // story:
    ScriptEntriesEnd

Script_1:                                      // cook (8,2), Sapphire LilycoveCity_DepartmentStore_2F_EventScript_Cook
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

Script_2:                                      // woman_2 (0,5), Sapphire LilycoveCity_DepartmentStore_2F_EventScript_PokefanF
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

Script_3:                                      // sailor (13,5), Sapphire LilycoveCity_DepartmentStore_2F_EventScript_Sailor
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

Script_4:                                      // clerk woman_4 (10,6), Sapphire LilycoveCity_DepartmentStore_2F_EventScript_ClerkRight
    ActorsPauseAll
    SEPlay SEQ_SE_MESSAGE
    ActorSetEyeToEye
    VMStackPush 0x8000
    VMStackPush 0x8001
    WorkSet 0x8000, 10                  // LilycoveCity_DepartmentStore_2F_Pokemart2
    WorkSet 0x8001, 1
    RTCallGlobal 10110
    VMStackPop 0x8001
    VMStackPop 0x8000
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_5:                                      // clerk woman_4 (7,6), Sapphire LilycoveCity_DepartmentStore_2F_EventScript_ClerkLeft
    ActorsPauseAll
    SEPlay SEQ_SE_MESSAGE
    ActorSetEyeToEye
    VMStackPush 0x8000
    VMStackPush 0x8001
    WorkSet 0x8000, 6                  // LilycoveCity_DepartmentStore_2F_Pokemart1
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

DS2_Init:
    h_setvar VAR_DEPT_STORE_FLOOR, 1
    VMHalt
    .balign 4, 0
