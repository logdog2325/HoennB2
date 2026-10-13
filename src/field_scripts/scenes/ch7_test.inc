// Chapter Ch7 test start (test builds only: HOENN_TEST_CH7=1, 2, 3 (Gym guide/statue test warps, six Lv 100s) or 4 (+ Devon Scope); notes/STORY_PORTING.md "Test switches"). Included in the
// body of the scene files of Routes 118-120 and Fortree and called from their zone inits (once: the first zone entered
// gives the end state of Chapters 1-6). Never assembled into normal builds.
// From work/emu/base_littleroot.dst with HOENN_TEST_WARP=406,283,206 (Mauville, below the Bike Shop door): walk into
// the Bike Shop and out again (a real warp: people answer afterwards), then east into Route 118 (zone 446): its zone
// init gives the end state of Chapters 1-6 once (five Badges, Surf, a Lv 100 Swampert when the party is empty).
#ifdef HOENN_TEST_CH7
#ifndef CH7_TEST_INC
#define CH7_TEST_INC
#include "hoenn_key_items.h"                // (ITEM_DEVON_SCOPE)
Test_Ch7Start:
    PokePartyRecoverAll                 // every entry: a full heal (PP too) for battle tests
    h_goto_if_set FLAG_RECEIVED_HM_SURF, L_C7T_Done   // once
    FlagSet 2401                        // FLAG_SYS_POKEMON_GET
    FlagSet 2403                        // FLAG_SYS_B_DASH (Running Shoes)
    FlagSet 2402                        // Black 2's Pokédex flag
    h_setflag FLAG_SYS_POKEDEX_GET
    h_setflag FLAG_ADVENTURE_STARTED
    h_setflag FLAG_DEFEATED_RIVAL_ROUTE103
    h_setvar VAR_STARTER_MON, 2         // Mudkip: the rival battles TRAINER_MAY_3 / TRAINER_BRENDAN_3 on Route 119
    h_getpartysize HLIB_TMP
    h_goto_if_ne HLIB_TMP, 0, L_C7T_Party
    PokePartyAdd HLIB_TMP, SPECIES_SWAMPERT, 0, 100
#if HOENN_TEST_CH7 >= 3                 // battle tests (story_finish): six Lv 100s and Full Restores
    PokePartyAdd HLIB_TMP, SPECIES_TYRANITAR, 0, 100
    PokePartyAdd HLIB_TMP, SPECIES_METAGROSS, 0, 100
    PokePartyAdd HLIB_TMP, SPECIES_SALAMENCE, 0, 100
    PokePartyAdd HLIB_TMP, SPECIES_GARCHOMP, 0, 100
    PokePartyAdd HLIB_TMP, SPECIES_ELECTIVIRE, 0, 100
    ItemAdd ITEM_FULL_RESTORE, 30, HLIB_TMP
#endif
#if HOENN_TEST_CH7 >= 4                 // HOENN_TEST_CH7=4: the Devon Scope too (Fortree's Kecleon test)
    ItemAdd ITEM_DEVON_SCOPE, 1, HLIB_TMP
    h_setflag FLAG_RECEIVED_DEVON_SCOPE
#endif
L_C7T_Party:
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
    h_setflag FLAG_DEFEATED_RUSTBORO_GYM
    h_setflag FLAG_DEFEATED_DEWFORD_GYM
    h_setflag FLAG_DEFEATED_MAUVILLE_GYM
    h_setflag FLAG_DEFEATED_LAVARIDGE_GYM
    h_setflag FLAG_DEFEATED_PETALBURG_GYM
    h_settrainerflag TRAINER_ROXANNE
    h_settrainerflag TRAINER_BRAWLY
    h_settrainerflag TRAINER_WATTSON
    h_settrainerflag TRAINER_FLANNERY
    h_settrainerflag TRAINER_NORMAN
    h_set_gym_trainers 1
    h_set_gym_trainers 2
    h_set_gym_trainers 3
    h_set_gym_trainers 4
    h_set_gym_trainers 5
#if HOENN_TEST_CH7 >= 2                 // HOENN_TEST_CH7=2: start past Route 118 (Good Rod and Steven done; warp into Route 119)
    h_setvar VAR_ROUTE118_STATE, 1
    h_setflag FLAG_HIDE_STEVEN_ROUTE118
    h_setflag FLAG_RECEIVED_GOOD_ROD
#endif
    h_setflag FLAG_RECEIVED_POKENAV
    h_setflag FLAG_RETURNED_DEVON_GOODS
    h_setflag FLAG_DELIVERED_DEVON_GOODS
    h_setflag FLAG_RECEIVED_HM04
    h_setflag FLAG_RECEIVED_HM_SURF
    ItemAdd ITEM_HM01, 1, HLIB_TMP
    ItemAdd ITEM_HM03, 1, HLIB_TMP
    ItemAdd ITEM_HM04, 1, HLIB_TMP
    ItemAdd ITEM_BICYCLE, 1, HLIB_TMP   // the Mach Bike
    MoneyAdd 10000
#ifdef HOENN_EMERALD
#include "scenes/emerald_test_chain.inc"
    em_test_chain 70                                  // Emerald-only state of the chapters before (scenes/emerald_test_chain.inc)
#endif
L_C7T_Done:
    VMReturn
#endif
#endif
