// EverGrandeCity_PokemonCenter_1F (zone 8): Pokémon Center, centers agent (b2tools/centers_rooms.py writes this file; edit the
// generator). Room: data/interior_layouts/EverGrandeCity_PokemonCenter_1F.json, people/signs/warps: data/interiors/8.json.
// Messages: src/text/script/0014_room_EverGrandeCity_PokemonCenter_1F.txt (Sapphire's words, Gen 5 capitalisation).
// Actors = Sapphire local ids. The PC is the pc01 model on a 0xd6 tile (Black 2 runs its PC script itself).
// EMERALD OVERLAY (emerald_ch11_gameclear, 2026-10-12): this file replaces src/field_scripts/0016_room_EverGrandeCity_PokemonCenter_1F.s in an
// Emerald build (version.overlay). Scripts 1-5 are the shared Center's, unchanged (the shared file is written by
// b2tools/centers_rooms.py: if the Center generator changes, copy the change here); script 6 is SCOTT (pokeemerald
// EverGrandeCity_PokemonCenter_1F_EventScript_Scott: he cheers the player on once the 6th badge is owned and leaves by the
// door; FLAG_MET_SCOTT_IN_EVERGRANDE also gets set, and he is gone, by entering Sidney's room: 0158's zone init), script 7 is
// the zone init (..._OnTransition: TryShowScott). Scott's object: data/story/emerald/e_ch11.json (uid 4, hidden by
// FLAG_HIDE_EVER_GRANDE_POKEMON_CENTER_1F_SCOTT). His line is row 9 of src/text/script/emerald/0014_room_EverGrandeCity_PokemonCenter_1F.txt.
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_story.inc"

    ScriptEntry Script_1
    ScriptEntry Script_2
    ScriptEntry Script_3
    ScriptEntry Script_4
    ScriptEntry Script_5
    ScriptEntry EC_Scott                     // 6: EverGrandeCity_PokemonCenter_1F_EventScript_Scott
    ScriptEntry EC_Init                      // 7: zone init (..._OnTransition)
    ScriptEntriesEnd

Script_1:                                    // nurse (7,2), Sapphire EverGrandeCity_PokemonCenter_1F_EventScript_Nurse: heals (Black 2's sequence)
#include "centers/nurse.inc"

Script_2:                                    // woman_7: LeagueAfterVictoryRoad
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

Script_3:                                    // old_man_1: BelieveInYourPokemon
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

#define T_ScottHappyForYou 9
#define EC_SCOTT 4

EC_Scott:                                    // ..._EventScript_Scott (lock, faceplayer)
    h_lock
    SEPlay SEQ_SE_MESSAGE
    h_faceplayer
    h_buffer_player
    h_msgbox T_ScottHappyForYou              // Scott: <player>, you've clawed your way up to face the Pokémon League! ... Go for greatness!
    h_closemessage
    h_getplayerfacing HLIB_TMP               // VAR_FACING: the player talked to him facing north (from below), east or west
    h_goto_if_eq HLIB_TMP, 0, L_EC_ExitNorth
    h_goto_if_eq HLIB_TMP, 2, L_EC_Exit
    h_goto_if_eq HLIB_TMP, 3, L_EC_Exit
    VMJump L_EC_Gone                         // (facing south: no walk, as Emerald)
L_EC_ExitNorth:
    h_applymovement EC_SCOTT, Mv_EC_ScottExitNorth
    h_waitmovement
    VMJump L_EC_Gone
L_EC_Exit:
    h_applymovement EC_SCOTT, Mv_EC_ScottExit
    h_waitmovement
L_EC_Gone:
    WorkAdd VAR_SCOTT_STATE, 1               // addvar VAR_SCOTT_STATE, 1
    h_setflag FLAG_MET_SCOTT_IN_EVERGRANDE
    h_playse SE_EXIT
    h_waitse
    h_removeobject EC_SCOTT, FLAG_HIDE_EVER_GRANDE_POKEMON_CENTER_1F_SCOTT
    h_release

EC_Init:                                     // ..._OnTransition (setrespawn is the Center's own in this port)
#ifdef HOENN_TEST_CH11
    VMCall Test_Ch11Start                    // test builds only (scenes/ch11_test.inc): the chapter's start state before the check below
#endif
    h_goto_if_set FLAG_MET_SCOTT_IN_EVERGRANDE, L_EC_InitDone
    h_goto_if_no_badge 6, L_EC_InitDone      // TryShowScott: goto_if_unset FLAG_BADGE06_GET (the Feather Badge)
    h_clearflag FLAG_HIDE_EVER_GRANDE_POKEMON_CENTER_1F_SCOTT
L_EC_InitDone:
    VMHalt

    .balign 4, 0
Mv_EC_ScottExitNorth:                        // ..._Movement_ScottExitNorth
    walk_left
    walk_down 2
    walk_left
    walk_down 2
    step_end
Mv_EC_ScottExit:                             // ..._Movement_ScottExit
    walk_down 2
    walk_left 2
    walk_down 2
    step_end
#include "common/movement.inc"
#include "scenes/ch11_test.inc"                      // test builds only (HOENN_TEST_CH11)
    .balign 4, 0
