// BattleFrontier_PokemonCenter_1F (zone 460; header scripts 920 -> own file 2102), Pokemon Emerald NDS only.
// frontier_center (2026-10-20, work/agents/frontier_center/tools/center_rooms.py writes this file). pokeemerald data/maps/BattleFrontier_PokemonCenter_1F/scripts.inc. Room: data/interior_layouts/BattleFrontier_PokemonCenter_1F.json,
// people/signs/warps: data/interiors/emerald/460.json (uid = script = Emerald local id). Messages:
// src/text/script/emerald/0658_room_BattleFrontier_PokemonCenter_1F.txt.
#include "asm/field_script.inc"
#include "hoenn.h"

    ScriptEntry Script_1
    ScriptEntry Script_2
    ScriptEntry Script_3
    ScriptEntry Script_4
    ScriptEntry Script_5
    ScriptEntry Script_6
    ScriptEntry Script_7
    ScriptEntriesEnd

Script_1:                                    // nurse (7,2): heals (centers/nurse.inc, Black 2's sequence)
#include "centers/nurse.inc"

Script_2:                                    // school_kid_m: NeverSeenPokemon
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

Script_3:                                    // man_3: NextStopBattleArena
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

Script_4:                                    // picnicker: GoingThroughEveryChallenge
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

Script_5:                                    // Skitty: its cry and "Mya myaaah!" (pokeemerald playmoncry SPECIES_SKITTY)
    ActorsPauseAll
    ActorSetEyeToEye
    PokeVoicePlay 300, 0                    // SPECIES_SKITTY
    ParentActorMsg MSGFILE_SCRIPT, 8, 0, 0
    LastKeyWait
    ActorMsgClose
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_6:                                    // magazine shelf (MB_POKEMON_CENTER_BOOKSHELF)
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    SystemMsg 9, 2
    LastKeyWait
    MsgWinCloseAll
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_7:                                    // Hoenn map (MB_REGION_MAP: the line, then the map screen)
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    SystemMsg 10, 2
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
