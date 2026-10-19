// LilycoveCity_ContestLobby (zone 161): Sapphire's simple people and signs (as converter/gen_interiors.py makes them),
// plus people that turn back after their message (Common_Movement_FaceOriginalDirection), by the specials agent
// (b2tools/specials.py people). Messages: src/text/script/0219_room_LilycoveCity_ContestLobby.txt
#include "asm/field_script.inc"
#include "hoenn.h"  // ch8a
#include "hoenn_trainers.h"  // ch8a
#include "hoenn_story.inc"  // ch8a
#include "scenes/ch8a_lib.inc"  // ch8a

    ScriptEntry Script_1
    ScriptEntry Script_2
    ScriptEntry Script_3
    ScriptEntry Script_4
    ScriptEntry Script_5
    ScriptEntry LB_Receptionist         // 6: object 1 (the Contest receptionist)  // story:
    ScriptEntry LB_LinkReceptionist     // 7: object 2  // story:
    ScriptEntry LB_Girl                 // 8: object 6  // story:
    ScriptEntry LB_Blender2Girl         // 9: object 10  // story:
    ScriptEntry LB_NinjaBoy             // 10: object 14  // story:
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

Script_3:
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    ActorSetEyeToEye
    ParentActorMsg MSGFILE_SCRIPT, 2, 0, 0
    LastKeyWait
    ActorMsgClose
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_4:
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    ActorSetEyeToEye
    ParentActorMsg MSGFILE_SCRIPT, 3, 0, 0
    LastKeyWait
    ActorMsgClose
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_5:
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    ActorSetEyeToEye
    ParentActorMsg MSGFILE_SCRIPT, 4, 0, 0
    LastKeyWait
    ActorMsgClose
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt
    .balign 4, 0

// ---- story (chapter Ch8 part 8a, ch8a agent: Sapphire's story scripts of this room; generators must keep
// everything from this line on; entries above marked "// story:")
// Sapphire data/maps/LilycoveCity_ContestLobby/scripts.inc. Pokémon Contests are decided later (notes/DECISIONS.md:
// "contests decided later (counters keep Sapphire's reception lines, register nobody)"): the receptionist says
// Sapphire's own reception line (Master Rank) and "We hope you will participate another time."; the link-contest
// receptionist says her no-Contest-Pass line (no pass is ever given). Not placed (Contests / Berry Blender are optional
// systems, as in ch3a's Slateport lobby): the Contest reporter (object 8, FLAG_HIDE_LILYCOVE_CONTEST_HALL_REPORTER stays set),
// the two artists (objects 4 and 11: the painting scene; FLAG_HIDE_ARTIST_LILCOVE_CONTEST / ATTENDENT_1 stay set), the Blender
// partner (object 3), the two Berry Blender machines and the four contest-winner pictures (signs). The script of VAR
// LILYCOVE_CONTEST_LOBBY_STATE (artist scenes) waits for Contests. People: data/story/ch8a.json. Lines 5-11.
#define T_RecAccepting 5
#define T_RecAnotherTime 6
#define T_LinkNeedPass 7
#define T_GetPassVerdanturf 8
#define T_WholeVariety 9
#define T_WhatKindOfPokeblock 10
#define T_PokeblocksWithFamily 11
#define T_NoPokeblockCase 12            // Emerald only (appended lines)
#define T_ClearedThatUp 13
// Pokémon Contests can't run on Black 2: the receptionist offers Black 2's Pokémon Musical instead (musical agent
// 2026-10-18; common/musical.inc, b2tools/patches/musical.py). Text lines 12-25 (Emerald: 14-27, after its
// Pokéblock Case lines). T_RecAccepting, T_RecAnotherTime and Emerald's T_ClearedThatUp stay in the files, unused
// (after the Pokéblock Case the Musical's own "Hello, there!" follows). The link receptionist is unchanged.
#include "common/musical.inc"
#ifdef HOENN_EMERALD
#define T_Musical 14
#else
#define T_Musical 12
#endif
LB_Receptionist:                            // ..._EventScript_ContestReceptionist: the Musical's reception
    c3_talk
#ifdef HOENN_EMERALD
// EMERALD (emerald_ch45_magma 2026-10-12; pokeemerald data/scripts/contest_hall.inc SpeakToContestReceptionist): the Pokéblock Case is
// given HERE, at the first visit (Sapphire's Slateport lobby girl gives it there; Emerald has no contest hall in Slateport:
// 1190_room_SlateportCity_ContestLobby.s). The welcome line is Emerald's (text line 5), then the same "another time" stand-in.
// Text lines 12-13 are appended to src/text/script/emerald/0219_room_LilycoveCity_ContestLobby.txt.
    h_goto_if_set FLAG_RECEIVED_POKEBLOCK_CASE, L_LB_Welcome
    h_msgbox T_NoPokeblockCase          // Hello! This is the reception counter for Pokémon Contests. Oh? It appears that you don't have a Pokéblock Case yet. ...
    h_closemessage
    h_giveitem ITEM_POKEBLOCK_CASE, 1
    h_setflag FLAG_RECEIVED_POKEBLOCK_CASE
L_LB_Welcome:
#endif
    musical_reception T_Musical

LB_LinkReceptionist:                        // ..._EventScript_LinkContestReceptionist (no Contest Pass)
    c3_talk
    h_msgbox T_LinkNeedPass
    h_release

LB_Girl:                                    // ..._EventScript_Girl (FLAG_RECEIVED_CONTEST_PASS has no id yet: Contests / S_optional
#ifdef FLAG_RECEIVED_CONTEST_PASS           // give the pass; until then nobody has it)
    h_goto_if_unset FLAG_RECEIVED_CONTEST_PASS, L_LB_GetPass
    h_msgbox_npc T_WholeVariety
#endif
L_LB_GetPass:
    h_msgbox_npc T_GetPassVerdanturf

LB_Blender2Girl:
    h_msgbox_npc T_WhatKindOfPokeblock
LB_NinjaBoy:
    h_msgbox_npc T_PokeblocksWithFamily
    .balign 4, 0
