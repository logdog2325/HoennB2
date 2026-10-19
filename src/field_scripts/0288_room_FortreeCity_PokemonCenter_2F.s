// FortreeCity_PokemonCenter_2F (zone 144): Pokémon Center, centers agent (b2tools/centers_rooms.py writes this file; edit the
// generator). Room: data/interior_layouts/FortreeCity_PokemonCenter_2F.json, people/signs/warps: data/interiors/144.json.
// Messages: src/text/script/0163_room_FortreeCity_PokemonCenter_2F.txt (Sapphire's words, Gen 5 capitalisation).
// Actors = Sapphire local ids. The PC is the pc01 model on a 0xd6 tile (Black 2 runs its PC script itself).
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
