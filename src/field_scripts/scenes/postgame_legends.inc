// The one-chance legendaries come back after the Hall of Fame (postgame_dex, 2026-11-09; user decision 2026-11-09,
// notes/DECISIONS.md; notes/POSTGAME.md "Post-game dex completion"): a legendary that was knocked out, ran or won the battle
// is there again after the next Hall of Fame; caught = gone for good. The roamers' rule (roamers.c PG_OnGameClear) and the
// event legendaries' (0114 HF_SetGameClearFlags: Mew, Deoxys, Lugia, Ho-Oh, Celebi; Emerald's Lati) now cover these too:
//   all versions  Regirock, Regice, Registeel (scenes/ch12_lib.inc h_regi_battle sets the hide flag before the battle)
//   S/R           Kyogre / Groudon in Cave of Origin B4F (0206: its hide flag + VAR_CAVE_OF_ORIGIN_B4F_STATE 0 = the
//                 trigger wakes it again, without the story: 0206 L_B4_Again), Rayquaza (Sky Pillar Top, FLAG_HIDE_RAYQUAZA),
//                 the Southern Island Lati (FLAG_ENCOUNTERED_LATIAS_OR_LATIOS: the slab calls it again), the other version's
//                 legend in Seafloor Cavern Room 9 (FLAG_DEFEATED_OTHER_LEGEND; scenes/SeafloorCavern_Room9_Postgame.inc)
//   Emerald       Rayquaza (FLAG_DEFEATED_RAYQUAZA: caught or knocked out), Kyogre and Groudon (FLAG_DEFEATED_KYOGRE /
//                 _GROUDON: the Weather Institute reports their weather again and its cave holds it)
// "Caught" is the Pokédex's caught mark of the species: these scripts never recorded the outcome before (a v19.1 / v2.1
// save's caught legendary must not come back), and no other source of these species exists in the version (the
// roaming Lati is the other one; the Room 9 legend keeps its own FLAG_CAUGHT_OTHER_LEGEND). Included by
// 0114_room_EverGrandeCity_HallOfFame.s; HF_ResetLostLegends is called by HF_SetGameClearFlags before the game is saved.
#ifndef HOENN_EMERALD
#include "hoenn_version.inc"                // SPECIES_GROUDON_OR_KYOGRE, SPECIES_LATIAS_OR_LATIOS (Emerald: not needed)
#endif
#define HFL_TMP 0x8051                     // = 0114's HF_TMP (a script work of the Hall of Fame's own range)

// flag set (met) and the species not caught: clear the flag
    .macro hfl_reset species, flag
    h_goto_if_unset \flag, .Lhfl\@
    PokeDexIsRegist 1, \species, HFL_TMP
    h_goto_if_ne HFL_TMP, 0, .Lhfl\@
    h_clearflag \flag
.Lhfl\@:
    .endm

HF_ResetLostLegends:
    hfl_reset SPECIES_REGIROCK, FLAG_HIDE_REGIROCK
    hfl_reset SPECIES_REGICE, FLAG_HIDE_REGICE
    hfl_reset SPECIES_REGISTEEL, FLAG_HIDE_REGISTEEL
#ifdef HOENN_EMERALD
    hfl_reset SPECIES_RAYQUAZA, FLAG_DEFEATED_RAYQUAZA
    hfl_reset SPECIES_KYOGRE, FLAG_DEFEATED_KYOGRE
    hfl_reset SPECIES_GROUDON, FLAG_DEFEATED_GROUDON
#else
    hfl_reset SPECIES_RAYQUAZA, FLAG_HIDE_RAYQUAZA
    hfl_reset SPECIES_LATIAS_OR_LATIOS, FLAG_ENCOUNTERED_LATIAS_OR_LATIOS
    h_goto_if_unset FLAG_LEGENDARY_BATTLE_COMPLETED, L_HFL_B4Done      // Cave of Origin B4F: only after the story's battle
    h_goto_if_unset FLAG_HIDE_LEGEND_MON_CAVE_OF_ORIGIN, L_HFL_B4Done
    PokeDexIsRegist 1, SPECIES_GROUDON_OR_KYOGRE, HFL_TMP
    h_goto_if_ne HFL_TMP, 0, L_HFL_B4Done
    h_clearflag FLAG_HIDE_LEGEND_MON_CAVE_OF_ORIGIN
    h_setvar VAR_CAVE_OF_ORIGIN_B4F_STATE, 0                          // its trigger (9,13) wakes it again (0206 L_B4_Again)
L_HFL_B4Done:
    h_clearflag FLAG_DEFEATED_OTHER_LEGEND                             // Seafloor Cavern Room 9 (caught: FLAG_CAUGHT_OTHER_LEGEND)
#endif
    VMReturn
