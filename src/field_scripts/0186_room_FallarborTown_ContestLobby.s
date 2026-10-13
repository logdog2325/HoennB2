// FallarborTown_ContestLobby (zone 93): Sapphire's simple people and signs (as converter/gen_interiors.py makes them),
// plus people that turn back after their message (Common_Movement_FaceOriginalDirection), by the specials agent
// (b2tools/specials.py people). Messages: src/text/script/0103_room_FallarborTown_ContestLobby.txt
#include "asm/field_script.inc"
#include "hoenn.h"  // ch4
#include "hoenn_trainers.h"  // ch4
#include "hoenn_story.inc"  // ch4
#include "scenes/ch4_lib.inc"  // ch4

    ScriptEntry Script_1
    ScriptEntry FCL_Receptionist        // 2: object 1 (FallarborTown_ContestLobby_EventScript_ContestReceptionist, stand-in)  // story:
    ScriptEntry FCL_Lass                // 3: object 3 (FallarborTown_ContestLobby_EventScript_Lass)  // story:
    ScriptEntry FCL_SketchArtist        // 4: object 6 (FallarborTown_ContestLobby_EventScript_SketchArtist)  // story:
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
    .balign 4, 0

// ---- story (chapter Ch4, ch4 agent 2026-10-07: Sapphire data/maps/FallarborTown_ContestLobby/scripts.inc; generators keep
// everything from this line on; entries above marked "// story:"). People: data/story/ch4.json (uid = Sapphire local
// id). Text lines 1-5 (line 0 is the generated boy's). Pokémon Contests are decided later (decision 2026-10-07): the
// receptionist says Sapphire's own reception lines for Fallarbor's Super Rank (contest_hall.inc's
// FallarborTown_ContestLobby_Text_1A5DFC with STR_VAR_1 = "Super", Lilycove's "We hope you will participate another
// time.") and registers nobody, as ch3a's Slateport and ch3b's Verdanturf counters. Not placed (S_optional: Contests,
// Berry Blender), as theirs: the contest reporter (object 5, FLAG_HIDE_CONTEST_REPORTER_FALLARBOR stays set), the Blend
// Master (object 4), the Berry Blender (10,3)/(12,5), its record board (13,1) and the contest winner's painting (11,1).
#define T_RecAccepting 1        // "Hello, there!{be01}\nWe’re accepting registrations for\nSuper Rank Pokémon Contests."
#define T_RecAnotherTime 2      // LilycoveCity_ContestLobby_Text_ParticipateAnotherTime
#define T_Pokeblock 3           // FallarborTown_ContestLobby_Text_AreYouMakingPokeblock
#define T_ICreateSketches 4     // FallarborTown_ContestLobby_Text_ICreateSketches
#define T_SketchIsUp 5          // FallarborTown_ContestLobby_Text_YourSketchIsUp

FCL_Receptionist:                           // (stand-in)
    c4_talk
    h_msgbox T_RecAccepting
    h_msgbox T_RecAnotherTime
    h_release
FCL_Lass:
    h_msgbox_npc T_Pokeblock
FCL_SketchArtist:
    h_goto_if_set FLAG_CONTEST_SKETCH_CREATED, L_FCL_SketchUp
    h_msgbox_npc T_ICreateSketches
L_FCL_SketchUp:
    h_msgbox_npc T_SketchIsUp
    .balign 4, 0
