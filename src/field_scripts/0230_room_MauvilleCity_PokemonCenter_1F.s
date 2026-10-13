// MauvilleCity_PokemonCenter_1F (zone 115): Pokémon Center, centers agent (b2tools/centers_rooms.py writes this file; edit the
// generator). Room: data/interior_layouts/MauvilleCity_PokemonCenter_1F.json, people/signs/warps: data/interiors/115.json.
// Messages: src/text/script/0134_room_MauvilleCity_PokemonCenter_1F.txt (Sapphire's words, Gen 5 capitalisation).
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

Script_1:                                    // nurse (7,2), Sapphire MauvilleCity_PokemonCenter_1F_EventScript_Nurse: heals (Black 2's sequence)
#include "centers/nurse.inc"

Script_2:                                    // Mauville's old man (Bard/Hipster/Trader/Storyteller/Giddy): first line only
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    ActorSetEyeToEye
#ifdef VAR_MAUVILLE_OLD_MAN
    WorkCmpConst VAR_MAUVILLE_OLD_MAN, 0         // not chosen yet (the map script normally has): choose now
    VMJumpIf CMP_NE, L_2_Chosen
    Random 0x8000, 5                             // 0-4, as Black 2's own scripts use it (0048.s Script_1)
    WorkSet VAR_MAUVILLE_OLD_MAN, 0x8000
    WorkAdd VAR_MAUVILLE_OLD_MAN, 1
L_2_Chosen:
    WorkCmpConst VAR_MAUVILLE_OLD_MAN, 2
    VMJumpIf CMP_EQ, L_2_Hipster
    WorkCmpConst VAR_MAUVILLE_OLD_MAN, 3
    VMJumpIf CMP_EQ, L_2_Trader
    WorkCmpConst VAR_MAUVILLE_OLD_MAN, 4
    VMJumpIf CMP_EQ, L_2_Storyteller
    WorkCmpConst VAR_MAUVILLE_OLD_MAN, 5
    VMJumpIf CMP_EQ, L_2_Giddy
#endif
    ParentActorMsg MSGFILE_SCRIPT, 5, 0, 0
    VMJump L_2_End
L_2_Hipster:
    ParentActorMsg MSGFILE_SCRIPT, 6, 0, 0
    VMJump L_2_End
L_2_Trader:
    ParentActorMsg MSGFILE_SCRIPT, 7, 0, 0
    VMJump L_2_End
L_2_Storyteller:
    ParentActorMsg MSGFILE_SCRIPT, 8, 0, 0
    VMJump L_2_End
L_2_Giddy:
    ParentActorMsg MSGFILE_SCRIPT, 9, 0, 0
    VMJump L_2_End
L_2_End:
    LastKeyWait
    ActorMsgClose
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_3:                                    // woman_1: ManOverThereSaysWeirdThings
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    ActorSetEyeToEye
    ParentActorMsg MSGFILE_SCRIPT, 10, 0, 0
    LastKeyWait
    ActorMsgClose
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_4:                                    // woman_7: MyDataUpdatedFromRecordCorner
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    ActorSetEyeToEye
    ParentActorMsg MSGFILE_SCRIPT, 11, 0, 0
    LastKeyWait
    ActorMsgClose
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_5:                                    // youngster: RecordCornerSoundsFun
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    ActorSetEyeToEye
    ParentActorMsg MSGFILE_SCRIPT, 12, 0, 0
    LastKeyWait
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

Script_8:                                    // map script (zone init): Mr. Briney's whereabouts, the old man's sprite
    VMCall Sub_UpdateBrineyLocation                // Sapphire: call Common_EventScript_UpdateBrineyLocation
#ifdef VAR_MAUVILLE_OLD_MAN
    WorkCmpConst VAR_MAUVILLE_OLD_MAN, 0
    VMJumpIf CMP_NE, L_ManChosen
    Random 0x8000, 5
    WorkSet VAR_MAUVILLE_OLD_MAN, 0x8000
    WorkAdd VAR_MAUVILLE_OLD_MAN, 1                // 1 Bard .. 5 Giddy
L_ManChosen:
    WorkCmpConst VAR_MAUVILLE_OLD_MAN, 2
    VMJumpIf CMP_EQ, L_GfxHipster
    WorkCmpConst VAR_MAUVILLE_OLD_MAN, 3
    VMJumpIf CMP_EQ, L_GfxTrader
    WorkCmpConst VAR_MAUVILLE_OLD_MAN, 4
    VMJumpIf CMP_EQ, L_GfxStoryteller
    WorkCmpConst VAR_MAUVILLE_OLD_MAN, 5
    VMJumpIf CMP_EQ, L_GfxGiddy
#endif
    WorkSetConst 0x4020, 328           // the Bard's stand-in
    VMHalt
L_GfxHipster:
    WorkSetConst 0x4020, 329
    VMHalt
L_GfxTrader:
    WorkSetConst 0x4020, 334
    VMHalt
L_GfxStoryteller:
    WorkSetConst 0x4020, 335
    VMHalt
L_GfxGiddy:
    WorkSetConst 0x4020, 336
    VMHalt

    .balign 4, 0
#include "common/briney.inc"
