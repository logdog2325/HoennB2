// LilycoveCity_DepartmentStore_5F (zone 201): shops agent, b2tools/shops_rooms.py (people and signs with one Sapphire message,
// shop clerks with Sapphire's lists: data/hoenn_shops.json). Messages: src/text/script/0259_room_LilycoveCity_DepartmentStore_5F.txt
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_trainers.h"  // ch8a
#include "hoenn_story.inc"  // ch8a
#include "scenes/ch8a_lib.inc"  // ch8a

    ScriptEntry Script_1
    ScriptEntry Script_2
    ScriptEntry Script_3
    ScriptEntry DS5_Clerk               // 4: objects 3-6: the four decoration clerks (Sapphire sells Poké Dolls, Mats, stones, vitamins, shards)  // story:
    ScriptEntry DS5_Init                // 5: zone init (0403): VAR_DEPT_STORE_FLOOR = 4, for the elevator  // story:
    ScriptEntriesEnd

Script_1:                                      // little_girl_2 (1,6), Sapphire LilycoveCity_DepartmentStore_5F_EventScript_LittleGirl
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

Script_2:                                      // woman_2 (7,7), Sapphire LilycoveCity_DepartmentStore_5F_EventScript_PokefanF
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

Script_3:                                      // woman_3 (9,5), Sapphire LilycoveCity_DepartmentStore_5F_EventScript_WomanNormal
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

// ---- story (chapter Ch8 part 8a, ch8a agent: Sapphire's story scripts of this room; generators must keep
// everything from this line on; entries above marked "// story:")
// Sapphire LilycoveCity_DepartmentStore_5F_EventScript_ClerkFarLeft/MidLeft/MidRight/FarRight: message
// Text_HowMayIServeYou, pokemartdecoration2 LIST, msgbox Text_PleaseComeAgain. User decision (2026-10-06): Black 2 has no
// Secret Base decorations, so the four clerks say Sapphire's two lines and sell nothing (the stones, vitamins and
// shards on their lists are not sold either). Proposal: a shop list of those items (data/hoenn_shops.json).
#define T_HowMayIServeYou 3
#define T_PleaseComeAgain 4
DS5_Clerk:
    c3_talk
    h_msgbox T_HowMayIServeYou
    h_msgbox T_PleaseComeAgain
    h_release

DS5_Init:
    h_setvar VAR_DEPT_STORE_FLOOR, 4
    VMHalt
    .balign 4, 0
