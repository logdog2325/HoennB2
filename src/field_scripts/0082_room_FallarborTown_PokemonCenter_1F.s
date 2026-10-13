// FallarborTown_PokemonCenter_1F (zone 41): Pokémon Center, centers agent (b2tools/centers_rooms.py writes this file; edit the
// generator). Room: data/interior_layouts/FallarborTown_PokemonCenter_1F.json, people/signs/warps: data/interiors/41.json.
// Messages: src/text/script/0050_room_FallarborTown_PokemonCenter_1F.txt (Sapphire's words, Gen 5 capitalisation).
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

Script_1:                                    // nurse (7,2), Sapphire FallarborTown_PokemonCenter_1F_EventScript_Nurse: heals (Black 2's sequence)
#include "centers/nurse.inc"

Script_2:                                    // girl_3: FossilManiacEdgeOfTown
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

Script_3:                                    // old_man_1: PlantHardyTrees
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

Script_4:                                    // Lanette at the PC: greeting, walks out, her house on Route 114 opens
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    ActorSetEyeToEye
    ParentActorMsg MSGFILE_SCRIPT, 7, 0, 0
    LastKeyWait
    ActorMsgClose
    PlayerGetDir 0x8000                          // 0 up (talking from her south), 2 left (from her east)
    WorkCmpConst 0x8000, 2
    VMJumpIf CMP_EQ, L_4_West
    ActorCmdExec 4, Movement_LanetteExitNorth
    VMJump L_4_Walk
L_4_West:
    ActorCmdExec 4, Movement_LanetteExitWest
L_4_Walk:
    ActorCmdWait
    ActorDelete 4
#ifdef FLAG_HIDE_LANETTE_FALLARBOR
    FlagSet FLAG_HIDE_LANETTE_FALLARBOR
#endif
#ifdef FLAG_HIDE_LANETTE
    FlagReset FLAG_HIDE_LANETTE
#endif
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

Script_7:                                    // map script (zone init): Mr. Briney's whereabouts
    VMCall Sub_UpdateBrineyLocation                // Sapphire: call Common_EventScript_UpdateBrineyLocation
    VMHalt

    .balign 4, 0

Movement_LanetteExitNorth:                       // Sapphire: right, down x2, left x4, down x4
    Move 15, 1
    Move 13, 2
    Move 14, 4
    Move 13, 4
    MoveEnd

Movement_LanetteExitWest:                        // Sapphire: down x2, left x3, down x4
    Move 13, 2
    Move 14, 3
    Move 13, 4
    MoveEnd
    .balign 4, 0
#include "common/briney.inc"
