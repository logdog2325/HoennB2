// Chapter Ch9 test start (test builds only: HOENN_TEST_CH9=<stage>; notes/STORY_PORTING.md "Test switches"). Included in the body
// of scenes/MossdeepCity.inc and called from Mossdeep City's zone init. Never assembled into normal builds.
// From work/emu/base_littleroot.dst with HOENN_TEST_WARP=107,707,171 (Mossdeep City, below Steven's door at (19,10)): walk into
// the house (a real warp: people answer afterwards; Steven gives Dive on the first entry), out again, and on to the Gym.
// The first entry gives the end state of Chapters 1-8 once: six Badges (Feather = Winona), Surf, Fly, Cut, Strength (Black 2's
// HM01-04), a Lv 100 Swampert (one Pokémon only: Tate and Liza ask for two) and Money.
// Stages: 1 = that; 2 = also a Lv 100 Tyranitar (a second Pokémon able to battle) and the trade items of the side people
// (2 Red Shards, 1 Blue Shard for the Treasure Hunter; 4 Shoal Salt and 4 Shoal Shells for the Shell Bell); 3 = also the
// Mind Badge and HM06 Dive (a start on Route 124: the test is also called by Route 124's zone init).
#ifdef HOENN_TEST_CH9
#ifndef CH9_TEST_INC
#define CH9_TEST_INC
#include "hoenn_trainers.h"
#include "hoenn_key_items.h"
Test_Ch9Start:
    PokePartyRecoverAll                 // every entry: a full heal (PP too) for battle tests
#if (HOENN_TEST_CH9 + 0) >= 2
    h_getpartysize HLIB_TMP             // stage 2 on a state that ran stage 1 before: the second Pokémon
    h_goto_if_ne HLIB_TMP, 1, L_C9T_Stage2Done
    PokePartyAdd HLIB_TMP, SPECIES_TYRANITAR, 0, 100
L_C9T_Stage2Done:
#endif
    h_goto_if_set FLAG_RECEIVED_HM_SURF, L_C9T_Done   // once
    FlagSet 2401                        // FLAG_SYS_POKEMON_GET
    FlagSet 2403                        // FLAG_SYS_B_DASH (Running Shoes)
    FlagSet 2402                        // Black 2's Pokédex flag
    h_setflag FLAG_SYS_POKEDEX_GET
    h_setflag FLAG_ADVENTURE_STARTED
    h_setflag FLAG_DEFEATED_RIVAL_ROUTE103
    h_setvar VAR_STARTER_MON, 2
    h_getpartysize HLIB_TMP
    h_goto_if_ne HLIB_TMP, 0, L_C9T_Party
    PokePartyAdd HLIB_TMP, SPECIES_SWAMPERT, 0, 100
L_C9T_Party:
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
    h_setflag FLAG_DEFEATED_RUSTBORO_GYM
    h_setflag FLAG_DEFEATED_DEWFORD_GYM
    h_setflag FLAG_DEFEATED_MAUVILLE_GYM
    h_setflag FLAG_DEFEATED_LAVARIDGE_GYM
    h_setflag FLAG_DEFEATED_PETALBURG_GYM
    h_setflag FLAG_DEFEATED_FORTREE_GYM
    h_settrainerflag TRAINER_ROXANNE
    h_settrainerflag TRAINER_BRAWLY
    h_settrainerflag TRAINER_WATTSON
    h_settrainerflag TRAINER_FLANNERY
    h_settrainerflag TRAINER_NORMAN
    h_settrainerflag TRAINER_WINONA
    h_set_gym_trainers 1
    h_set_gym_trainers 2
    h_set_gym_trainers 3
    h_set_gym_trainers 4
    h_set_gym_trainers 5
    h_set_gym_trainers 6
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
    MoneyAdd 10000
    // Fortree's boy sent his Wingull to Mossdeep (chapter Ch7): the Wingull sits in Mossdeep's House 2
    h_setflag FLAG_WINGULL_SENT_ON_ERRAND
    h_clearflag FLAG_HIDE_WINGULL_MOSSDEEP_HOUSE
    h_setflag FLAG_HIDE_WINGULL_FORTREE_HOUSE
#if (HOENN_TEST_CH9 + 0) >= 2
    PokePartyAdd HLIB_TMP, SPECIES_TYRANITAR, 0, 100
    ItemAdd ITEM_RED_SHARD, 2, HLIB_TMP
    ItemAdd ITEM_BLUE_SHARD, 1, HLIB_TMP
    ItemAdd ITEM_SHOAL_SALT, 4, HLIB_TMP
    ItemAdd ITEM_SHOAL_SHELL, 4, HLIB_TMP
#endif
#if (HOENN_TEST_CH9 + 0) >= 3
    TrainerCardAddBadge 6               // stage 3: the Mind Badge and HM06 Dive too (Dive tests on Routes 124-128)
    FlagSet 2420
    h_setflag FLAG_DEFEATED_MOSSDEEP_GYM
    h_setflag FLAG_RECEIVED_HM08
    ItemAdd ITEM_HM06, 1, HLIB_TMP
#endif
#ifdef HOENN_TEST_CH9T
    h_set_gym_trainers 7                // test builds only (HOENN_TEST_CH9T=1): the Mossdeep Gym's trainers count as beaten
#endif
#ifdef HOENN_EMERALD
#include "scenes/emerald_test_chain.inc"
    em_test_chain 90                                  // Emerald-only state of the chapters before (scenes/emerald_test_chain.inc)
#endif
L_C9T_Done:
    VMReturn
#endif
#endif
