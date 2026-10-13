// EverGrandeCity_PokemonLeague_2F (zone 344, Emerald only): emerald_rooms (b2tools/emerald_rooms.py writes this file: edit the
// generator), a copy of 0132_room_EverGrandeCity_PokemonCenter_2F.s's people scripts. Room: data/interior_layouts/EverGrandeCity_PokemonLeague_2F.json,
// people/warps: data/interiors/emerald/344.json. Messages: src/text/script/emerald/0556_room_EverGrandeCity_PokemonLeague_2F.txt.
#include "asm/field_script.inc"
#include "hoenn.h"

    ScriptEntry Script_1
    ScriptEntry Script_2
    ScriptEntry Script_3
    ScriptEntriesEnd

Script_1:                                    // Colosseum attendant (Cable Club): Sapphire's apology
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

Script_2:                                    // Trade Center attendant (Cable Club): Sapphire's apology
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
