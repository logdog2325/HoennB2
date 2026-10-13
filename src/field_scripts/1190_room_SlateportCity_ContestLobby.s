// SlateportCity_ContestLobby (zone 595): Sapphire's simple people and signs (as converter/gen_interiors.py makes them),
// plus people that turn back after their message (Common_Movement_FaceOriginalDirection), by the specials agent
// (b2tools/specials.py people). Messages: src/text/script/0351_room_SlateportCity_ContestLobby.txt
#include "asm/field_script.inc"
#include "hoenn.h"  // ch3a
#include "hoenn_trainers.h"  // ch3a
#include "hoenn_story.inc"  // ch3a
#include "scenes/ch3_lib.inc"  // ch3a

    ScriptEntry Script_1
    ScriptEntry Script_2
    ScriptEntry Story_CL_Receptionist   // 3: object 1 (Teala)  // story:
    ScriptEntry Story_CL_Girl           // 4: object 4  // story:
    ScriptEntry Story_CL_Boy            // 5: object 6  // story:
    ScriptEntry Story_CL_LittleGirl     // 6: object 7 (Pokéblock Case)  // story:
    ScriptEntriesEnd

Script_1:
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    ActorSetEyeToEye
    ParentActorMsg MSGFILE_SCRIPT, 0, 0, 0
    LastKeyWait
    ActorMsgClose
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_2:
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    ActorSetEyeToEye
    ParentActorMsg MSGFILE_SCRIPT, 1, 0, 0
    LastKeyWait
    ActorMsgClose
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt
    .balign 4, 0

// ---- story (chapter Ch3 part 3a, ch3a agent: Sapphire's story scripts of this room; generators must keep
// everything from this line on; entries above marked "// story:")
// Sapphire data/maps/SlateportCity_ContestLobby/scripts.inc: the people. Pokémon Contests are an optional system
// (notes/STORY_CHAPTERS.md S_optional): the receptionist says two of Sapphire's own reception lines ("accepting
// registrations for Hyper Rank", Lilycove's "We hope you will participate another time.") and registers nobody.
// Not placed (S_optional: Contests, Berry Blender): the contest reporter (object 5, FLAG_HIDE_CONTEST_REPORTER_SLATEPORT
// stays set), the Blend Master (object 2, data/scripts/pokeblocks.inc), the two Berry Blender spots, the contest
// winner's painting and the other painting (bg events). People: data/story/ch3a.json. Lines 2-7 of the text file.
#define T_RecAccepting 2
#define T_RecAnotherTime 3
#define T_Berries 4
#define T_Blending 5
#define T_HaveCase 6
#define T_PutPokeblocks 7

Story_CL_Receptionist:                      // SlateportCity_ContestLobby_EventScript_ContestReceptionist (stand-in)
    c3_talk
    h_msgbox T_RecAccepting
    h_msgbox T_RecAnotherTime
    h_release
Story_CL_Girl:
    h_msgbox_npc T_Berries
Story_CL_Boy:
    h_msgbox_npc T_Blending

Story_CL_LittleGirl:                        // SlateportCity_ContestLobby_EventScript_LittleGirl
#ifdef HOENN_EMERALD
    // EMERALD: no case from her (Emerald has no contest hall in Slateport; the Pokéblock Case is given at the Lilycove lobby,
    // 0322_room_LilycoveCity_ContestLobby.s; emerald_ch45_magma 2026-10-12)
    VMJump L_CL_HavePokeblockCase
#endif
    h_goto_if_set FLAG_RECEIVED_POKEBLOCK_CASE, L_CL_HavePokeblockCase
    c3_talk                                 // lockall + Common_Movement_FacePlayer
    h_msgbox T_HaveCase
    h_closemessage
    h_giveitem ITEM_POKEBLOCK_CASE, 1       // (Sapphire does not look at giveitem's result here)
    h_setflag FLAG_RECEIVED_POKEBLOCK_CASE
    h_release
L_CL_HavePokeblockCase:
    h_msgbox_npc T_PutPokeblocks
    .balign 4, 0
