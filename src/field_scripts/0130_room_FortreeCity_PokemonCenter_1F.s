// FortreeCity_PokemonCenter_1F (zone 65): Pokémon Center, centers agent (b2tools/centers_rooms.py writes this file; edit the
// generator). Room: data/interior_layouts/FortreeCity_PokemonCenter_1F.json, people/signs/warps: data/interiors/65.json.
// Messages: src/text/script/0075_room_FortreeCity_PokemonCenter_1F.txt (Sapphire's words, Gen 5 capitalisation).
// Actors = Sapphire local ids. The PC is the pc01 model on a 0xd6 tile (Black 2 runs its PC script itself).
#include "asm/field_script.inc"
#include "hoenn.h"

    ScriptEntry Script_1
    ScriptEntry Script_2
    ScriptEntry Script_3
    ScriptEntry Script_4
    ScriptEntry Script_5
    ScriptEntry Script_6
    ScriptEntriesEnd

Script_1:                                    // nurse (7,2), Sapphire FortreeCity_PokemonCenter_1F_EventScript_Nurse: heals (Black 2's sequence)
#include "centers/nurse.inc"

Script_2:                                    // gentleman: GoToSafariZone
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

Script_3:                                    // man_4: RecordCornerIsNeat
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

Script_4:                                    // boy_3: DoYouKnowAboutPokenav
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    ActorSetEyeToEye
    ParentActorMsg MSGFILE_SCRIPT, 7, 0, 0
    LastKeyWait
    ActorMsgClose
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_5:                                    // magazine shelf (Sapphire MB_POKEMON_CENTER_BOOKSHELF)
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    SystemMsg 8, 2
    LastKeyWait
    MsgWinCloseAll
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_6:                                    // Hoenn map (Sapphire MB_REGION_MAP opens the map screen)
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
