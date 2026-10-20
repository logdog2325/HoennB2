// BattleFrontier_Mart (zone 528; header scripts 1056 -> own file 2100), Pokemon Emerald NDS only.
// frontier_center (2026-10-20, work/agents/frontier_center/tools/center_rooms.py writes this file). pokeemerald data/maps/BattleFrontier_Mart/scripts.inc. Room: data/interior_layouts/BattleFrontier_Mart.json,
// people/signs/warps: data/interiors/emerald/528.json (uid = script = Emerald local id). Messages:
// src/text/script/emerald/0537_room_BattleFrontier_Mart.txt.
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_story.inc"

    ScriptEntry Script_1
    ScriptEntry Script_2
    ScriptEntry Script_3
    ScriptEntry Script_4
    ScriptEntriesEnd

Script_1:                                    // clerk (1,3): pokeemerald's Frontier list (shop id 26), Black 2's shop counter (global 10110)
    ActorsPauseAll
    SEPlay SEQ_SE_MESSAGE
    ActorSetEyeToEye
    VMStackPush 0x8000
    VMStackPush 0x8001
    WorkSet 0x8000, 26                 // BattleFrontier_Mart_Pokemart
    WorkSet 0x8001, 1
    RTCallGlobal 10110
    VMStackPop 0x8001
    VMStackPop 0x8000
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_2:                                    // old woman (5,4): turns down (Common_Movement_FaceDown), not to the player: ProteinMakeNiceGift
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    ActorCmdExec 2, Movement_FaceDown
    ActorCmdWait
    ParentActorMsg MSGFILE_SCRIPT, 0, 0, 0
    LastKeyWait
    ActorMsgClose
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_3:                                    // old man (5,5): ChaperonGrandson
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

Script_4:                                    // boy (8,4): FacilitiesDontAllowItems
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

Movement_FaceDown:
    face_down
    MoveEnd
    .balign 4, 0
