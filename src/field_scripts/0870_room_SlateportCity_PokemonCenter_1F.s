// SlateportCity_PokemonCenter_1F (zone 435): Pokémon Center, centers agent (b2tools/centers_rooms.py writes this file; edit the
// generator). Room: data/interior_layouts/SlateportCity_PokemonCenter_1F.json, people/signs/warps: data/interiors/435.json.
// Messages: src/text/script/0172_room_SlateportCity_PokemonCenter_1F.txt (Sapphire's words, Gen 5 capitalisation).
// Actors = Sapphire local ids. The PC is the pc01 model on a 0xd6 tile (Black 2 runs its PC script itself).
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_story.inc"

    ScriptEntry Script_1
    ScriptEntry Script_2
    ScriptEntry Script_3
    ScriptEntry Script_4
    ScriptEntry Script_5
    ScriptEntry Script_6
    ScriptEntriesEnd

Script_1:                                    // nurse (7,2), Sapphire SlateportCity_PokemonCenter_1F_EventScript_Nurse: heals (Black 2's sequence)
#include "centers/nurse.inc"

Script_2:                                    // sailor: RaiseDifferentTypesOfPokemon
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

Script_3:                                    // woman_7: TradedMonWithFriend
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    ActorSetEyeToEye
    ParentActorMsg MSGFILE_SCRIPT, 6, 0, 0
    LastKeyWait
    ActorMsgClose
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_4:                                    // magazine shelf (Sapphire MB_POKEMON_CENTER_BOOKSHELF)
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    SystemMsg 7, 2
    LastKeyWait
    MsgWinCloseAll
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_5:                                    // Hoenn map (Sapphire MB_REGION_MAP opens the map screen)
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    SystemMsg 8, 2
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

Script_6:                                    // map script (zone init): Mr. Briney's whereabouts
    VMCall Sub_UpdateBrineyLocation                // Sapphire: call Common_EventScript_UpdateBrineyLocation
    VMHalt

    .balign 4, 0
#include "common/briney.inc"
