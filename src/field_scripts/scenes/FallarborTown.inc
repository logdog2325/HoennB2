// Fallarbor Town's story (Sapphire data/maps/FallarborTown/scripts.inc; chapter Ch4, ch4 agent 2026-10-07). Scripts
// 1-3 of the zone's generated script file (zone 6); the generated signs/people follow. Text:
// src/text/scenes/FallarborTown.txt. People: data/story/ch4.json (uid = 100 + Sapphire local id). Map scripts:
// scenes/FallarborTown_init.inc. Contests are decided later (decision 2026-10-07): the contest-room vars are still set.
#ifdef SCENE_ENTRIES
    ScriptEntry FT_Init                     // 1: FallarborTown_OnTransition (zone init)
    ScriptEntry FT_ExpertM                  // 2: object 2
    ScriptEntry FT_Azurill                  // 3: object 4
#else
#include "scenes/ch4_lib.inc"
#define T_ShadyFellow 0         // FallarborTown_Text_ShadyFellowAtLab
#define T_Meteors 1             // FallarborTown_Text_RegionKnownForMeteors
#define T_Azurill 2             // FallarborTown_Text_Azurill

FT_Init:                                    // FallarborTown_OnTransition
    h_setflag FLAG_VISITED_FALLARBOR_TOWN
    h_setvar VAR_LINK_CONTEST_ROOM_STATE, 0
    h_setflag FLAG_HIDE_CONTEST_REPORTER_FALLARBOR
    h_clearflag FLAG_CONTEST_SKETCH_CREATED
    VMHalt
FT_ExpertM:                                 // FallarborTown_EventScript_ExpertM
    c4_talk
    h_goto_if_set FLAG_DEFEATED_EVIL_TEAM_MT_CHIMNEY, L_FT_Meteors
    h_msgbox T_ShadyFellow
    h_release
L_FT_Meteors:
    h_msgbox T_Meteors
    h_release
FT_Azurill:                                 // FallarborTown_EventScript_Azurill
    c4_mon_cry SPECIES_AZURILL, T_Azurill
    .balign 4, 0
#endif
