// LilycoveCity_PokemonCenter_1F (zone 109): Pokémon Center, centers agent (b2tools/centers_rooms.py writes this file; edit the
// generator). Room: data/interior_layouts/LilycoveCity_PokemonCenter_1F.json, people/signs/warps: data/interiors/109.json.
// Messages: src/text/script/0128_room_LilycoveCity_PokemonCenter_1F.txt (Sapphire's words, Gen 5 capitalisation).
// Actors = Sapphire local ids. The PC is the pc01 model on a 0xd6 tile (Black 2 runs its PC script itself).
#include "asm/field_script.inc"
#include "hoenn.h"

    ScriptEntry Script_1
    ScriptEntry Script_2
    ScriptEntry Script_3
    ScriptEntry Script_4
    ScriptEntry Script_5
    ScriptEntriesEnd

Script_1:                                    // nurse (7,2), Sapphire LilycoveCity_PokemonCenter_1F_EventScript_Nurse: heals (Black 2's sequence)
#include "centers/nurse.inc"

Script_2:                                    // boy_1: HowManyKindsOfPokemon
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    ActorSetEyeToEye
    ParentActorMsg MSGFILE_SCRIPT, 5, 0, 0
    LastKeyWait
    ActorMsgClose
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_3:                                    // Team Aqua talk (seventh badge)
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    ActorSetEyeToEye
    TrainerCardHasBadge 0x8000, 6                // Sapphire FLAG_BADGE07_GET (Mind Badge)
    WorkCmpConst 0x8000, 1
    VMJumpIf CMP_EQ, L_3_Set
    ParentActorMsg MSGFILE_SCRIPT, 7, 0, 0
    VMJump L_3_End
L_3_Set:
    ParentActorMsg MSGFILE_SCRIPT, 6, 0, 0
L_3_End:
    LastKeyWait
    ActorMsgClose
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_4:                                    // magazine shelf (Sapphire MB_POKEMON_CENTER_BOOKSHELF)
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    SystemMsg 8, 2
    LastKeyWait
    MsgWinCloseAll
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_5:                                    // Hoenn map (Sapphire MB_REGION_MAP opens the map screen)
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    SystemMsg 9, 2
    LastKeyWait
    MsgWinCloseAll
    FadeOutBlackQ
    FadeWait
    CallPlaceSelect 0x8000, 0x8001
    FadeInBlackQ
    FadeWait
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

    .balign 4, 0
