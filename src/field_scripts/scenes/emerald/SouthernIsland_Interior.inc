// EMERALD's Southern Island slab scene (pokeemerald data/maps/SouthernIsland_Interior/scripts.inc; emerald_ch11_gameclear 2026-10-12,
// Emerald's run-away / knock-out rule postgame_fix 2026-10-19). Included by scenes/SouthernIsland_Interior.inc after `SII_Slab:` in an
// Emerald build, in place of Sapphire's fixed Latios. The island's Pokémon is the one that is NOT the roamer (VAR_ROAMER_POKEMON, the
// colour told to Mom: scenes/emerald/players_house_1f_ch13.inc):
//   var 0 (Red) = Latias roams, Latios waits here (also what a save has that has not seen Mom's scene: pokeemerald's
//                 SetUpLatios is the var-0 branch); var 1 (Blue) = Latios roams, Latias waits here.
// The two are two story objects: Latios = ch13.json object 102 (4510, FLAG_HIDE_LATIOS_OR_LATIAS_STATIONARY), Latias = object 103 of
// data/story/emerald/e_ch11.json (4509, FLAG_HIDE_SOUTHERN_ISLAND_UNCHOSEN_EON_DUO_MON); both start hidden (new-game flags).
// SouthernIsland_Interior_EventScript_Lati: the slab shows the sign's line instead of the Lati once this visit has had its battle
// (FLAG_TEMP_2, map-local), when it was knocked out (FLAG_DEFEATED_LATIAS_OR_LATIOS, cleared by every Hall of Fame: 0114
// HF_EmeraldFlags) or caught (FLAG_CAUGHT_LATIAS_OR_LATIOS), or without the Eon Ticket's ship (FLAG_SYS_HAS_EON_TICKET, our
// FLAG_ENABLE_SHIP_SOUTHERN_ISLAND). Ran away: it is here again on the next visit. Knocked out or ran: "The X flew away!" (RanFromLati /
// LatiDefeated -> Common_EventScript_LegendaryFlewAway: line 1 of src/text/scenes/emerald/SouthernIsland_Interior.txt).
// Saves of Emerald NDS v1.1 and earlier met the Lati under the old one-time rule without recording the outcome: FLAG_ENCOUNTERED set
// before the Eon Ticket was ever marked shown (the new harbor always marks it before the first crossing). Once, on the first read of the
// slab, such a save counts the Lati as caught when the Pokédex has it caught; otherwise it is here again (it ran or was knocked out).
// Not ported (as in Sapphire's port): the camera pan, the Soul Dew it holds (CallWildBattle sets no item).
#include "scenes/events_lib.inc"           // ev_legend_battle (Emerald's legendary encounter: caught / defeated flags, "flew away")
#define SII_TEMP_2 0x5C                    // FLAG_TEMP_2 (map-local: flags 0-0x63 reset on every zone change)
#define SII_T_FLEW 1                       // "The {STR_VAR_1} flew away!"
    .macro sii_lati_appears species, uid, hide
    h_playmoncry \species
    h_delay 30
    h_waitmoncry
    h_addobject \uid, \hide
    h_delay 30
    h_applymovement \uid, Mv_SII_LatiosFliesDown
    h_waitmovement
    h_delay 50
    h_setflag \hide
    ev_legend_battle \species, SII_LATIOS_LEVEL, \uid, \hide, FLAG_CAUGHT_LATIAS_OR_LATIOS, FLAG_DEFEATED_LATIAS_OR_LATIOS, SII_T_FLEW
    h_release
    .endm
    h_lock
    h_goto_if_unset FLAG_ENCOUNTERED_LATIAS_OR_LATIOS, L_SII_E_Rule     // (old saves, once: see above)
    h_goto_if_set FLAG_SHOWN_EON_TICKET, L_SII_E_Rule
    h_setflag FLAG_SHOWN_EON_TICKET
    h_goto_if_ne VAR_ROAMER_POKEMON, 0, L_SII_E_OldLatias
    PokeDexIsRegist 1, SPECIES_LATIOS, HLIB_TMP
    VMJump L_SII_E_OldDex
L_SII_E_OldLatias:
    PokeDexIsRegist 1, SPECIES_LATIAS, HLIB_TMP
L_SII_E_OldDex:
    h_goto_if_eq HLIB_TMP, 0, L_SII_E_Rule
    h_setflag FLAG_CAUGHT_LATIAS_OR_LATIOS
L_SII_E_Rule:                              // SouthernIsland_Interior_EventScript_Lati
    h_goto_if_set SII_TEMP_2, L_SII_Slab
    h_goto_if_set FLAG_DEFEATED_LATIAS_OR_LATIOS, L_SII_Slab
    h_goto_if_set FLAG_CAUGHT_LATIAS_OR_LATIOS, L_SII_Slab
    h_goto_if_unset FLAG_SYS_HAS_EON_TICKET, L_SII_Slab
    h_setflag FLAG_ENCOUNTERED_LATIAS_OR_LATIOS
    h_setflag SII_TEMP_2
    h_delay 50
    h_waitse
    h_goto_if_ne VAR_ROAMER_POKEMON, 0, L_SII_E_Latias
    sii_lati_appears SPECIES_LATIOS, SII_LATIOS, FLAG_HIDE_LATIOS_OR_LATIAS_STATIONARY              // Red: Latias roams
L_SII_E_Latias:
    sii_lati_appears SPECIES_LATIAS, SII_LATIAS, FLAG_HIDE_SOUTHERN_ISLAND_UNCHOSEN_EON_DUO_MON     // Blue: Latios roams
