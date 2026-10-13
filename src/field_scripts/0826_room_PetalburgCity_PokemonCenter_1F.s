// PetalburgCity_PokemonCenter_1F (zone 413): Pokémon Center, centers agent (b2tools/centers_rooms.py writes this file; edit the
// generator). Room: data/interior_layouts/PetalburgCity_PokemonCenter_1F.json, people/signs/warps: data/interiors/413.json.
// Messages: src/text/script/0642_room_PetalburgCity_PokemonCenter_1F.txt (Sapphire's words, Gen 5 capitalisation).
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
    ScriptEntry Script_7
    ScriptEntry Script_8
    ScriptEntriesEnd

Script_1:                                    // nurse (7,2), Sapphire PetalburgCity_PokemonCenter_1F_EventScript_Nurse: heals (Black 2's sequence)
#include "centers/nurse.inc"

Script_2:                                    // Mystery Event Club man: his greeting (the profile is Easy Chat, which Black 2 lacks)
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    ActorSetEyeToEye
#ifdef FLAG_SYS_CHAT_USED
    FlagGet FLAG_SYS_CHAT_USED, 0x8000
    WorkCmpConst 0x8000, 1
    VMJumpIf CMP_EQ, L_2_Set
#endif
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

Script_3:                                    // fat_man: PCStorageSystem
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

Script_4:                                    // youngster: OranBerryRegainedHP
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    ActorSetEyeToEye
    ParentActorMsg MSGFILE_SCRIPT, 8, 0, 0
    LastKeyWait
    ActorMsgClose
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_5:                                    // types talk + the starter's type (Sapphire IsStarterInParty)
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    ActorSetEyeToEye
    ParentActorMsg MSGFILE_SCRIPT, 9, 0, 0
    LastKeyWait
    WorkCmpConst VAR_STARTER_MON, 0
    VMJumpIf CMP_NE, L_5_Not0
    PokePartyGetCountBySpecies SPECIES_TREECKO, 0x8000
    WorkCmpConst 0x8000, 0
    VMJumpIf CMP_EQ, L_5_End
    ParentActorMsg MSGFILE_SCRIPT, 10, 0, 0
    LastKeyWait
    VMJump L_5_End
L_5_Not0:
    WorkCmpConst VAR_STARTER_MON, 1
    VMJumpIf CMP_NE, L_5_Not1
    PokePartyGetCountBySpecies SPECIES_TORCHIC, 0x8000
    WorkCmpConst 0x8000, 0
    VMJumpIf CMP_EQ, L_5_End
    ParentActorMsg MSGFILE_SCRIPT, 11, 0, 0
    LastKeyWait
    VMJump L_5_End
L_5_Not1:
    WorkCmpConst VAR_STARTER_MON, 2
    VMJumpIf CMP_NE, L_5_Not2
    PokePartyGetCountBySpecies SPECIES_MUDKIP, 0x8000
    WorkCmpConst 0x8000, 0
    VMJumpIf CMP_EQ, L_5_End
    ParentActorMsg MSGFILE_SCRIPT, 12, 0, 0
    LastKeyWait
    VMJump L_5_End
L_5_Not2:
L_5_End:
    ActorMsgClose
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_6:                                    // magazine shelf (Sapphire MB_POKEMON_CENTER_BOOKSHELF)
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    SystemMsg 13, 2
    LastKeyWait
    MsgWinCloseAll
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_7:                                    // Hoenn map (Sapphire MB_REGION_MAP opens the map screen)
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    SystemMsg 14, 2
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

Script_8:                                    // map script (zone init): Mr. Briney's whereabouts
    VMCall Sub_UpdateBrineyLocation                // Sapphire: call Common_EventScript_UpdateBrineyLocation
    VMHalt

    .balign 4, 0
#include "common/briney.inc"
