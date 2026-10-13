// EMERALD's Southern Island slab scene (pokeemerald data/maps/SouthernIsland_Interior/scripts.inc; emerald_ch11_gameclear 2026-10-12).
// Included by scenes/SouthernIsland_Interior.inc after `SII_Slab:` in an Emerald build, in place of Sapphire's fixed Latios. The island's
// Pokémon is the one that is NOT the roamer (VAR_ROAMER_POKEMON, the colour told to Mom: scenes/emerald/players_house_1f_ch13.inc):
//   var 0 (Red) = Latias roams, Latios waits here (also what a save has that has not seen Mom's scene: pokeemerald's
//                 SetUpLatios is the var-0 branch); var 1 (Blue) = Latios roams, Latias waits here.
// The two are two story objects: Latios = ch13.json object 102 (4510, FLAG_HIDE_LATIOS_OR_LATIAS_STATIONARY), Latias = object 103 of
// data/story/emerald/e_ch11.json (4509, FLAG_HIDE_SOUTHERN_ISLAND_UNCHOSEN_EON_DUO_MON); both start hidden (new-game flags).
// The rest is the shared scene (the slab read facing north, the Eon Ticket, the cry, the flight down, the battle at the curve's Lv 55).
// Not ported (as in Sapphire's port): the camera pan, the Soul Dew it holds; Emerald lets a Lati you ran from come back next visit and
// one you beat after the next Hall of Fame (FLAG_DEFEATED_LATIAS_OR_LATIOS): this port keeps the one-time FLAG_ENCOUNTERED rule of the scene.
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
    ch13_legend_battle \species, SII_LATIOS_LEVEL, \uid
    h_release
    .endm
    h_lock
    h_goto_if_set FLAG_ENCOUNTERED_LATIAS_OR_LATIOS, L_SII_Slab
    h_goto_if_unset FLAG_SYS_HAS_EON_TICKET, L_SII_Slab
    h_setflag FLAG_ENCOUNTERED_LATIAS_OR_LATIOS
    h_delay 50
    h_waitse
    h_goto_if_ne VAR_ROAMER_POKEMON, 0, L_SII_E_Latias
    sii_lati_appears SPECIES_LATIOS, SII_LATIOS, FLAG_HIDE_LATIOS_OR_LATIAS_STATIONARY              // Red: Latias roams
L_SII_E_Latias:
    sii_lati_appears SPECIES_LATIAS, SII_LATIAS, FLAG_HIDE_SOUTHERN_ISLAND_UNCHOSEN_EON_DUO_MON     // Blue: Latios roams
