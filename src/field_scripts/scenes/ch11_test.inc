// Chapter Ch11 test start (test builds only: HOENN_TEST_CH11=<stage>; notes/STORY_PORTING.md "Test switches").
// Included by the files that call Test_Ch11Start from their zone init (Ever Grande City, Victory Road 1F, the Pokémon League
// lobby). Never assembled into normal builds. From work/emu/base_littleroot.dst with HOENN_TEST_WARP=412,<x>,<z> (Ever Grande
// City: the tile in front of the League door or Victory Road's door): the first zone init gives the end state of Chapters 1-10
// once: the first seven Badges (Mind Badge = Tate and Liza; the Rain Badge comes with stage 2 / the Wallace battle), Surf, Cut,
// Strength, Rock Smash (Black 2's HM01-04 + TM94), six Lv 100 Groudon, Full Restores, Max Revives and Money.
// Stages: 1 = seven Badges (the Pokémon League guards turn you away: the Rain Badge is missing), 2 = also the eighth Badge
// (a start for the Elite Four), 3 = also marks the four Elite Four members beaten (a start for Steven).
#ifdef HOENN_TEST_CH11
#ifndef CH11_TEST_INC
#define CH11_TEST_INC
#include "hoenn_trainers.h"
#include "hoenn_key_items.h"
Test_Ch11Start:
    PokePartyRecoverAll                 // every entry: a full heal (PP too) for battle tests
    h_goto_if_set FLAG_RECEIVED_HM_SURF, L_C11T_Done    // once
    FlagSet 2401                        // FLAG_SYS_POKEMON_GET
    FlagSet 2403                        // FLAG_SYS_B_DASH (Running Shoes)
    FlagSet 2402                        // Black 2's Pokédex flag
    h_setflag FLAG_SYS_POKEDEX_GET
    h_setflag FLAG_ADVENTURE_STARTED
    h_setflag FLAG_DEFEATED_RIVAL_ROUTE103
    h_setvar VAR_STARTER_MON, 2
    h_getpartysize HLIB_TMP
    h_goto_if_ne HLIB_TMP, 0, L_C11T_Party
#ifdef HOENN_TEST_CH11W
    PokePartyAdd HLIB_TMP, SPECIES_MAGIKARP, 0, 5     // test builds only (HOENN_TEST_CH11W=1): one Lv 5 Magikarp, to lose the Champion battle (the forced-loss test)
    VMJump L_C11T_Party
#endif
    PokePartyAdd HLIB_TMP, SPECIES_GROUDON, 0, 100    // six Lv 100 Groudon: Earth Power, Fissure, Solar Beam and Fire Blast (the 4th, which
    PokePartyAdd HLIB_TMP, SPECIES_GROUDON, 0, 100    // the tests tap) knock out everything of the Elite Four and Steven
    PokePartyAdd HLIB_TMP, SPECIES_GROUDON, 0, 100
    PokePartyAdd HLIB_TMP, SPECIES_GROUDON, 0, 100
    PokePartyAdd HLIB_TMP, SPECIES_GROUDON, 0, 100
    PokePartyAdd HLIB_TMP, SPECIES_GROUDON, 0, 100
L_C11T_Party:
    TrainerCardAddBadge 0               // (h_givebadge's TrainerCardSaveGymVictoryParty may not run in a zone init)
    FlagSet 2414
    TrainerCardAddBadge 1
    FlagSet 2415
    TrainerCardAddBadge 2
    FlagSet 2416
    TrainerCardAddBadge 3
    FlagSet 2417
    TrainerCardAddBadge 4
    FlagSet 2418
    TrainerCardAddBadge 5
    FlagSet 2419
    TrainerCardAddBadge 6
    FlagSet 2420
    h_setflag FLAG_DEFEATED_RUSTBORO_GYM
    h_setflag FLAG_DEFEATED_DEWFORD_GYM
    h_setflag FLAG_DEFEATED_MAUVILLE_GYM
    h_setflag FLAG_DEFEATED_LAVARIDGE_GYM
    h_setflag FLAG_DEFEATED_PETALBURG_GYM
    h_setflag FLAG_DEFEATED_FORTREE_GYM
    h_setflag FLAG_DEFEATED_MOSSDEEP_GYM
    h_setflag FLAG_RECEIVED_POKENAV
    h_setflag FLAG_RETURNED_DEVON_GOODS
    h_setflag FLAG_DELIVERED_DEVON_GOODS
    h_setflag FLAG_DELIVERED_STEVEN_LETTER
    h_setflag FLAG_RECEIVED_HM04
    h_setflag FLAG_RECEIVED_HM02
    h_setflag FLAG_RECEIVED_HM_SURF
    ItemAdd ITEM_HM01, 1, HLIB_TMP
    ItemAdd ITEM_HM02, 1, HLIB_TMP
    ItemAdd ITEM_HM03, 1, HLIB_TMP
    ItemAdd ITEM_HM04, 1, HLIB_TMP
    ItemAdd ITEM_BICYCLE, 1, HLIB_TMP   // the Mach Bike
    ItemAdd ITEM_FULL_RESTORE, 99, HLIB_TMP
    ItemAdd ITEM_MAX_REVIVE, 99, HLIB_TMP
    MoneyAdd 10000
#if (HOENN_TEST_CH11 + 0) >= 2
    TrainerCardAddBadge 7               // stage 2: the Rain Badge (all eight)
    FlagSet 2421
    h_setflag FLAG_DEFEATED_SOOTOPOLIS_GYM
#endif
#if (HOENN_TEST_CH11 + 0) >= 3
    h_settrainerflag TRAINER_SIDNEY
    h_settrainerflag TRAINER_PHOEBE
    h_settrainerflag TRAINER_GLACIA
    h_settrainerflag TRAINER_DRAKE
    h_setflag FLAG_ENTERED_ELITE_FOUR
    h_setflag FLAG_DEFEATED_ELITE_4_SYDNEY
    h_setflag FLAG_DEFEATED_ELITE_4_PHOEBE
    h_setflag FLAG_DEFEATED_ELITE_4_GLACIA
    h_setflag FLAG_DEFEATED_ELITE_4_DRAKE
#endif
#ifdef HOENN_EMERALD
#include "scenes/emerald_test_chain.inc"
    em_test_chain 110                                 // Emerald-only state of the chapters before (scenes/emerald_test_chain.inc)
#endif
L_C11T_Done:
    VMReturn
#endif
#endif
