// SootopolisCity_PokemonCenter_1F (zone 443): Pokémon Center, centers agent (b2tools/centers_rooms.py writes this file; edit the
// generator). Room: data/interior_layouts/SootopolisCity_PokemonCenter_1F.json, people/signs/warps: data/interiors/443.json.
// Messages: src/text/script/0652_room_SootopolisCity_PokemonCenter_1F.txt (Sapphire's words, Gen 5 capitalisation).
// Actors = Sapphire local ids. The PC is the pc01 model on a 0xd6 tile (Black 2 runs its PC script itself).
#include "asm/field_script.inc"
#include "hoenn.h"

    ScriptEntry Script_1
    ScriptEntry Script_2
    ScriptEntry Script_3
    ScriptEntry Script_4
    ScriptEntry Script_5
    ScriptEntriesEnd

Script_1:                                    // nurse (7,2), Sapphire EverGrandeCity_PokemonCenter_1F_EventScript_Nurse: heals (Black 2's sequence)
#include "centers/nurse.inc"

Script_2:                                    // the weather crisis talk (Groudon/Kyogre awake)
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    ActorSetEyeToEye
#if defined(FLAG_LEGENDARY_BATTLE_COMPLETED) && defined(FLAG_LEGEND_ESCAPED_SEAFLOOR_CAVERN)
    FlagGet FLAG_LEGEND_ESCAPED_SEAFLOOR_CAVERN, 0x8000   // set while the legend is loose ...
    FlagGet FLAG_LEGENDARY_BATTLE_COMPLETED, 0x8001
    WorkCmpConst 0x8001, 1
    VMJumpIf CMP_NE, L_SootoTest2
    WorkSetConst 0x8000, 0                     // ... until it is calmed
L_SootoTest2:
#else
    WorkSetConst 0x8000, 0
#endif
    WorkCmpConst 0x8000, 1
    VMJumpIf CMP_EQ, L_2_Set
    ParentActorMsg MSGFILE_SCRIPT, 6, 0, 0
    VMJump L_2_End
L_2_Set:
    ParentActorMsg MSGFILE_SCRIPT, 5, 0, 0
L_2_End:
    LastKeyWait
    ActorMsgClose
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_3:                                    // the weather crisis talk (Groudon/Kyogre awake)
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    ActorSetEyeToEye
#if defined(FLAG_LEGENDARY_BATTLE_COMPLETED) && defined(FLAG_LEGEND_ESCAPED_SEAFLOOR_CAVERN)
    FlagGet FLAG_LEGEND_ESCAPED_SEAFLOOR_CAVERN, 0x8000   // set while the legend is loose ...
    FlagGet FLAG_LEGENDARY_BATTLE_COMPLETED, 0x8001
    WorkCmpConst 0x8001, 1
    VMJumpIf CMP_NE, L_SootoTest3
    WorkSetConst 0x8000, 0                     // ... until it is calmed
L_SootoTest3:
#else
    WorkSetConst 0x8000, 0
#endif
    WorkCmpConst 0x8000, 1
    VMJumpIf CMP_EQ, L_3_Set
    ParentActorMsg MSGFILE_SCRIPT, 8, 0, 0
    VMJump L_3_End
L_3_Set:
    ParentActorMsg MSGFILE_SCRIPT, 7, 0, 0
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
    SystemMsg 9, 2
    LastKeyWait
    MsgWinCloseAll
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_5:                                    // Hoenn map (Sapphire MB_REGION_MAP opens the map screen)
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
