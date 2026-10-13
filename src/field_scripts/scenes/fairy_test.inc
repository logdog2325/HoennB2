// fairy_core's battle kit (test builds only: HOENN_TEST_CHFA=1; 2026-10-08). Littleroot's town sign (stand at (183,366)
// facing north) runs Test_FA_Start: the stage in work FA_STAGE (0x41AE, a free work of hoenn.h's pool, poked in RAM by
// work/agents/fairy_core/tools/battle_test.py) gives the player one Lv 50 Pokemon with four set moves and starts a
// wild battle against a Lv 50 Pokemon (both with their first ability; the player's holds the item in work FA_ITEM
// 0x41AD, 0 = none). Moves 560+ only exist with the fairy patch: stages 1-4 and 6 use them, so a ROM
// without it runs stages 5 and 11-16 only. Never assembled into normal builds.
//  1  Gardevoir  Moonblast, Dazzling Gleam, Draining Kiss, Psychic       vs Altaria   (Fairy into Dragon: x2)
//  2  Altaria    Dragon Pulse, Dragon Breath, Sky Attack, Moonblast      vs Marill    (Dragon into Fairy: no effect)
//  3  Gardevoir  Moonblast, Psychic, Shadow Ball, Thunderbolt            vs Skarmory  (Steel resists Fairy)
//  4  Gardevoir  Psychic, Shadow Ball, Thunderbolt, Moonblast            vs Mawile    (Steel/Fairy; Gen 6 Steel change)
//  5  Tyranitar  Shadow Ball, Crunch, Stone Edge, Earthquake             vs Wobbuffet (the split: same attacker)
//  6  Azumarill  Aqua Tail, Play Rough, Charm, Waterfall                 vs Salamence (Play Rough into Dragon; Azumarill)
// 11-14, 16: the same Pokemon with Black 2 moves only, for the ROM without the fairy patch (the baseline):
//  11/13/14  Gardevoir  Psychic, Shadow Ball, Thunderbolt, Energy Ball   vs Altaria / Skarmory / Mawile
//  12        Altaria    Dragon Pulse, Dragon Breath, Sky Attack, Pluck   vs Marill
//  16        Azumarill  Aqua Tail, Waterfall, Ice Punch, Superpower      vs Salamence
// 20: no battle: warp to Lilycove Dept. Store 3F (zone 199) below the right clerk (Sapphire (10,2) + the room's origin 1),
//     whose list has the Pixie Plate and Fairy Gem when Fairy is on
#ifdef HOENN_TEST_CHFA
#ifndef FAIRY_TEST_INC
#define FAIRY_TEST_INC
#define FA_STAGE 0x41AE
#define FA_ITEM 0x41AD
#define FA_SPECIES 0x8004
#define FA_FOE 0x8005
Test_FA_Start:
    FlagSet 2401                            // FLAG_SYS_POKEMON_GET
    h_goto_if_eq FA_STAGE, 2, L_FA_2
    h_goto_if_eq FA_STAGE, 3, L_FA_3
    h_goto_if_eq FA_STAGE, 4, L_FA_4
    h_goto_if_eq FA_STAGE, 5, L_FA_5
    h_goto_if_eq FA_STAGE, 6, L_FA_6
    h_goto_if_eq FA_STAGE, 11, L_FA_11
    h_goto_if_eq FA_STAGE, 12, L_FA_12
    h_goto_if_eq FA_STAGE, 13, L_FA_13
    h_goto_if_eq FA_STAGE, 14, L_FA_14
    h_goto_if_eq FA_STAGE, 16, L_FA_16
    h_goto_if_eq FA_STAGE, 20, L_FA_20
    PokePartyAddEx HLIB_TMP, SPECIES_GARDEVOIR, 0, 50, 0, 2, 2, FA_ITEM, 4
    PokePartyLearnMove 0, 0, 565            // Moonblast
    PokePartyLearnMove 0, 1, 563            // Dazzling Gleam
    PokePartyLearnMove 0, 2, 562            // Draining Kiss
    PokePartyLearnMove 0, 3, 94             // Psychic
    WorkSetConst FA_FOE, SPECIES_ALTARIA
    VMJump L_FA_Battle
L_FA_2:
    PokePartyAddEx HLIB_TMP, SPECIES_ALTARIA, 0, 50, 0, 2, 2, FA_ITEM, 4
    PokePartyLearnMove 0, 0, 406            // Dragon Pulse
    PokePartyLearnMove 0, 1, 225            // Dragon Breath
    PokePartyLearnMove 0, 2, 143            // Sky Attack
    PokePartyLearnMove 0, 3, 565            // Moonblast
    WorkSetConst FA_FOE, SPECIES_MARILL
    VMJump L_FA_Battle
L_FA_3:
    PokePartyAddEx HLIB_TMP, SPECIES_GARDEVOIR, 0, 50, 0, 2, 2, FA_ITEM, 4
    PokePartyLearnMove 0, 0, 565            // Moonblast
    PokePartyLearnMove 0, 1, 94             // Psychic
    PokePartyLearnMove 0, 2, 247            // Shadow Ball
    PokePartyLearnMove 0, 3, 85             // Thunderbolt
    WorkSetConst FA_FOE, SPECIES_SKARMORY
    VMJump L_FA_Battle
L_FA_4:
    PokePartyAddEx HLIB_TMP, SPECIES_GARDEVOIR, 0, 50, 0, 2, 2, FA_ITEM, 4
    PokePartyLearnMove 0, 0, 94             // Psychic
    PokePartyLearnMove 0, 1, 247            // Shadow Ball
    PokePartyLearnMove 0, 2, 85             // Thunderbolt
    PokePartyLearnMove 0, 3, 565            // Moonblast
    WorkSetConst FA_FOE, SPECIES_MAWILE
    VMJump L_FA_Battle
L_FA_5:
    PokePartyAddEx HLIB_TMP, SPECIES_TYRANITAR, 0, 50, 0, 2, 2, FA_ITEM, 4
    PokePartyLearnMove 0, 0, 247            // Shadow Ball
    PokePartyLearnMove 0, 1, 242            // Crunch
    PokePartyLearnMove 0, 2, 444            // Stone Edge
    PokePartyLearnMove 0, 3, 89             // Earthquake
    WorkSetConst FA_FOE, SPECIES_WOBBUFFET
    VMJump L_FA_Battle
L_FA_6:
    PokePartyAddEx HLIB_TMP, SPECIES_AZUMARILL, 0, 50, 0, 2, 2, FA_ITEM, 4
    PokePartyLearnMove 0, 0, 401            // Aqua Tail
    PokePartyLearnMove 0, 1, 564            // Play Rough
    PokePartyLearnMove 0, 2, 204            // Charm
    PokePartyLearnMove 0, 3, 127            // Waterfall
    WorkSetConst FA_FOE, SPECIES_SALAMENCE
    VMJump L_FA_Battle
L_FA_11:
    WorkSetConst FA_FOE, SPECIES_ALTARIA
    VMJump L_FA_GardevoirB2
L_FA_13:
    WorkSetConst FA_FOE, SPECIES_SKARMORY
    VMJump L_FA_GardevoirB2
L_FA_14:
    WorkSetConst FA_FOE, SPECIES_MAWILE
L_FA_GardevoirB2:
    PokePartyAddEx HLIB_TMP, SPECIES_GARDEVOIR, 0, 50, 0, 2, 2, FA_ITEM, 4
    PokePartyLearnMove 0, 0, 94             // Psychic
    PokePartyLearnMove 0, 1, 247            // Shadow Ball
    PokePartyLearnMove 0, 2, 85             // Thunderbolt
    PokePartyLearnMove 0, 3, 412            // Energy Ball
    VMJump L_FA_Battle
L_FA_12:
    PokePartyAddEx HLIB_TMP, SPECIES_ALTARIA, 0, 50, 0, 2, 2, FA_ITEM, 4
    PokePartyLearnMove 0, 0, 406            // Dragon Pulse
    PokePartyLearnMove 0, 1, 225            // Dragon Breath
    PokePartyLearnMove 0, 2, 143            // Sky Attack
    PokePartyLearnMove 0, 3, 365            // Pluck
    WorkSetConst FA_FOE, SPECIES_MARILL
    VMJump L_FA_Battle
L_FA_16:
    PokePartyAddEx HLIB_TMP, SPECIES_AZUMARILL, 0, 50, 0, 2, 2, FA_ITEM, 4
    PokePartyLearnMove 0, 0, 401            // Aqua Tail
    PokePartyLearnMove 0, 1, 127            // Waterfall
    PokePartyLearnMove 0, 2, 8              // Ice Punch
    PokePartyLearnMove 0, 3, 276            // Superpower
    WorkSetConst FA_FOE, SPECIES_SALAMENCE
    VMJump L_FA_Battle
L_FA_20:
    h_warp_arrive 199, 11, 5, 0
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt
L_FA_Battle:
    CallWildBattle FA_FOE, 50, 0
    CallWildBattleEnd
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt
#endif
#endif
