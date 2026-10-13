// DewfordTown_PokemonCenter_1F (zone 1): Pokémon Center, centers agent (b2tools/centers_rooms.py writes this file; edit the
// generator). Room: data/interior_layouts/DewfordTown_PokemonCenter_1F.json, people/signs/warps: data/interiors/1.json.
// Messages: src/text/script/0004_room_DewfordTown_PokemonCenter_1F.txt (Sapphire's words, Gen 5 capitalisation).
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
    ScriptEntriesEnd

Script_1:                                    // nurse (7,2), Sapphire DewfordTown_PokemonCenter_1F_EventScript_Nurse: heals (Black 2's sequence)
#include "centers/nurse.inc"

Script_2:                                    // woman_2: StoneCavern
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

Script_3:                                    // man_4: FaintedMonCanUseHM
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
    VMCall Sub_DC_Stranded                         // in Dewford although Mr. Briney never sailed: v16-v16.2's
    h_goto_if_ne HLIB_TMP, 1, L_DC_InitEnd         // blackout bug (Rustboro's Center returned you to Dewford's)
    WorkSetConst 0x4003, 1                         // -> script 7
L_DC_InitEnd:
    VMHalt

Script_7:                                    // condition 0x4003 == 1 (0003_..._init.s): back to Rustboro's Center,
    WorkSetConst 0x4003, 0                         // which becomes the respawn point again (RESPAWN_ZONE_INFO 16)
    VMCall Sub_DC_Stranded                         // (checked again: 0x4003 is a temporary work)
    h_goto_if_ne HLIB_TMP, 1, L_DC_NoRescue
    FieldSetTeleportZone 16
    h_warp_arrive 425, 7, 12, 0                    // (sweep_crash 2026-10-11: h_warpsilent never faded back in, so the
                                                   // top screen stayed black in Rustboro's Center after the door or the
                                                   // blackout; the arrival script 10017 fades in)
L_DC_NoRescue:
    VMHalt

Sub_DC_Stranded:                             // HLIB_TMP = 1 when nothing but the bug can have brought you here: you
    WorkSetConst HLIB_TMP, 0                       // reach Dewford only on Mr. Briney's boat (his first sail is after
    h_goto_if_set FLAG_MR_BRINEY_SAILING_INTRO, L_DC_StrandedEnd   // FLAG_MR_BRINEY_SAILING_INTRO, even before Mr. Stone's
    h_goto_if_set FLAG_DEFEATED_PETALBURG_GYM, L_DC_StrandedEnd    // PokéNav) until Surf (Norman's badge) and Fly
    WorkSetConst HLIB_TMP, 1
L_DC_StrandedEnd:
    VMReturn

    .balign 4, 0
#include "common/briney.inc"
