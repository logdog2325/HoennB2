// Southern Island Interior's story (Sapphire data/maps/SouthernIsland_Interior/scripts.inc; chapter Ch13, ch13 agent
// 2026-10-07): the slab at the end of the chamber and the Latios. Included twice by the generated zone file (zone 112,
// a standalone map): the entry below becomes script 1. Text: src/text/scenes/SouthernIsland_Interior.txt (line 0). Story
// objects (data/story/ch13.json): the slab as a sign at (13,11) read facing north (SouthernIsland_Interior_EventScript_
// 160B9B -> 160BA7), Latios (uid 102, Black 2's Latios overworld sprite = Sapphire's VAR_OBJ_GFX_ID_1 in Sapphire; Ruby: Latias)
// hidden by FLAG_HIDE_LATIOS_OR_LATIAS_STATIONARY. Sapphire's flying Latios/Latias object (object 1, the rival's picture,
// hidden by FLAG_HIDE_LATIOS_OR_LATIAS_FLYING) is never shown: not placed. Not done: the camera pan (SpawnCameraDummy: the
// camera rises three tiles while the Pokémon appears and follows it down; here the camera stays on the player, and the
// Latios flies into view from the north); the Soul Dew it holds (CallWildBattle cannot set a wild Pokémon's item).
// No map scripts (Sapphire's ON_RESUME removes Latios after the battle: ch13_legend_battle's ActorDelete does).
// RUBY (ruby_scenes, 2026-10-08; pokeruby's .ifdef SAPPHIRE blocks of this map and constants/version.inc): the island's Pokémon is Latias
// (SPECIES_LATIAS_OR_LATIOS = Sapphire Latios, Ruby Latias; the roamer is the other one), object model 4509 instead of 4510 (data/story/ch13.json
// "model_ruby"), the same slab, movement and battle. Black 2's Latias is level-scaled like Latios (both Sapphire Lv 50: data/level_scaling.json).
#ifdef SCENE_ENTRIES
    ScriptEntry SII_Slab                // 1: SouthernIsland_Interior_EventScript_160B9B / 160BA7
#else
#include "scenes/ch13_lib.inc"
#include "hoenn_version.inc"             // ruby_scenes: SPECIES_LATIAS_OR_LATIOS
#define SII_LATIOS 102
#define SII_LATIAS 103                 // Emerald only (data/story/emerald/e_ch11.json)
#define SII_LATIOS_LEVEL 55             // Sapphire 50 on the scaled curve (data/level_scaling.json)

SII_Slab:
#ifdef HOENN_EMERALD
#include "scenes/emerald/SouthernIsland_Interior.inc"   // Emerald: Latios or Latias by the colour told to Mom (VAR_ROAMER_POKEMON)
#else
    h_lock
    h_goto_if_set FLAG_ENCOUNTERED_LATIAS_OR_LATIOS, L_SII_Slab
    h_goto_if_unset FLAG_SYS_HAS_EON_TICKET, L_SII_Slab
    h_setflag FLAG_ENCOUNTERED_LATIAS_OR_LATIOS
    h_delay 50
    h_waitse
    h_playmoncry SPECIES_LATIAS_OR_LATIOS
    h_delay 30
    h_waitmoncry
    h_addobject SII_LATIOS, FLAG_HIDE_LATIOS_OR_LATIAS_STATIONARY
    h_delay 30
    h_applymovement SII_LATIOS, Mv_SII_LatiosFliesDown
    h_waitmovement
    h_delay 50
    h_setflag FLAG_HIDE_LATIOS_OR_LATIAS_STATIONARY
    ch13_legend_battle SPECIES_LATIAS_OR_LATIOS, SII_LATIOS_LEVEL, SII_LATIOS
    h_release
#endif
L_SII_Slab:                             // SouthernIsland_Interior_EventScript_160C08
    h_msgbox_info 0                     // "All dreams are but another reality. Never forget..."
    h_closemessage
    h_release

    .balign 4, 0
Mv_SII_LatiosFliesDown:                 // SouthernIsland_Interior_Movement_160C22
    walk_down 5
    delay_16 2
    walk_down 4
    step_end
    .balign 4, 0
#endif
