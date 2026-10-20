// BattleFrontier_PokemonCenter_2F (zone 499; header scripts 998 -> own file 2098), Pokemon Emerald NDS only.
// frontier_center (2026-10-20, work/agents/frontier_center/tools/center_rooms.py writes this file): a copy of 0770_room_OldaleTown_PokemonCenter_2F.s (the centers agent's 2F attendants).
// People/warps: data/interiors/emerald/499.json. Messages: src/text/script/emerald/0299_room_BattleFrontier_PokemonCenter_2F.txt.
#include "asm/field_script.inc"
#include "hoenn.h"

    ScriptEntry Script_1
    ScriptEntry Script_2
    ScriptEntry Script_3
    ScriptEntriesEnd

Script_1:                                    // Colosseum attendant: Sapphire's apology until FLAG_SYS_POKEDEX_GET, then Black 2's Union Room counter (global 2101)
#ifdef FLAG_SYS_POKEDEX_GET
    FlagGet FLAG_SYS_POKEDEX_GET, 0x8000
    WorkCmpConst 0x8000, 1
    VMJumpIf CMP_EQ, L_1_Open
#endif
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
L_1_Open:
    FlagSet 106
    RTCallGlobal 2101                          // it pauses, talks, ends the events (FinishAllEvents) itself
    VMHalt

Script_2:                                    // Trade Center attendant: Sapphire's apology until FLAG_SYS_POKEDEX_GET, then Black 2's Wi-Fi Club counter (global 10100)
#ifdef FLAG_SYS_POKEDEX_GET
    FlagGet FLAG_SYS_POKEDEX_GET, 0x8000
    WorkCmpConst 0x8000, 1
    VMJumpIf CMP_EQ, L_2_Open
#endif
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
L_2_Open:
    FlagSet 106
    RTCallGlobal 10100                          // it pauses, talks, ends the events (FinishAllEvents) itself
    VMHalt

Script_3:                                    // Record Corner attendant (Cable Club): Sapphire's apology
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
