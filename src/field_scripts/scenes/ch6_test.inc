// Chapter Ch6 / Ch12 test start (test builds only: HOENN_TEST_CH6=<stage>, HOENN_TEST_CH12=<stage>; notes/STORY_PORTING.md
// "Test switches"). Included in the bodies of scenes/PetalburgCity_Gym_ch6.inc (Ch6_PG_Init, the Gym's zone init) and
// of chapter Ch12's Pacifidlog scene (its zone init). Never assembled into normal builds.
// Start from work/emu/base_littleroot.dst with HOENN_TEST_WARP=439,103,298 (Petalburg, in front of the Gym) and walk
// into the Gym (a real warp: people answer afterwards).
// Stages: HOENN_TEST_CH6=1 = the end of Chapter 5 (four Badges, VAR_PETALBURG_GYM_STATE 6: Dad waits; the first entry
// leaves him at the entrance, Ch1's init having run first); =2 = also Norman beaten (Balance Badge, TM42, HM03): the
// Surf side areas (Wally's father still has HM03); =3 = also HM03 and the Basement Key (Wattson, New Mauville) and the Scanner (Stern's trade) in the Bag, all
// eight Badges. HOENN_TEST_CH12 = stage 2 + all eight Badges and HM02/HM05/HM06, a Relicanth and a Wailord.
// Party: a Lv 100 Swampert when the party is empty (battles ask no "Will you switch?").
#if defined(HOENN_TEST_CH6) || defined(HOENN_TEST_CH12)
#ifndef CH6_TEST_INC
#define CH6_TEST_INC
#include "hoenn_trainers.h"
#include "hoenn_key_items.h"
Test_Ch6Start:
    PokePartyRecoverAll                 // every entry: a full heal (PP too) for battle tests
    h_goto_if_set FLAG_RECEIVED_HM04, L_C6T_Done      // once
    // Chapters 1-5 (the parts later chapters read)
    FlagSet 2401                        // FLAG_SYS_POKEMON_GET
    FlagSet 2403                        // FLAG_SYS_B_DASH (Running Shoes)
    FlagSet 2402                        // Black 2's Pokédex flag
    h_setflag FLAG_SYS_POKEDEX_GET
    h_setflag FLAG_ADVENTURE_STARTED
    h_setflag FLAG_DEFEATED_RIVAL_ROUTE103
    h_setvar VAR_STARTER_MON, 2
#ifdef HOENN_TEST_CH12
    PokePartyAdd HLIB_TMP, SPECIES_RELICANTH, 0, 50   // the Sealed Chamber: Relicanth first, Wailord last
#endif
    h_getpartysize HLIB_TMP
#ifndef HOENN_TEST_CH12
    h_goto_if_ne HLIB_TMP, 0, L_C6T_Party
#endif
    PokePartyAdd HLIB_TMP, SPECIES_SWAMPERT, 0, 100
L_C6T_Party:
    TrainerCardAddBadge 0               // (h_givebadge's TrainerCardSaveGymVictoryParty may not run in a zone init)
    FlagSet 2414
    TrainerCardAddBadge 1
    FlagSet 2415
    TrainerCardAddBadge 2
    FlagSet 2416
    TrainerCardAddBadge 3
    FlagSet 2417
    h_setflag FLAG_DEFEATED_RUSTBORO_GYM
    h_setflag FLAG_DEFEATED_DEWFORD_GYM
    h_setflag FLAG_DEFEATED_MAUVILLE_GYM
    h_setflag FLAG_DEFEATED_LAVARIDGE_GYM
    h_settrainerflag TRAINER_ROXANNE
    h_settrainerflag TRAINER_BRAWLY
    h_settrainerflag TRAINER_WATTSON
    h_settrainerflag TRAINER_FLANNERY
    h_set_gym_trainers 1
    h_set_gym_trainers 2
    h_set_gym_trainers 3
    h_set_gym_trainers 4
    h_setvar VAR_PETALBURG_GYM_STATE, 6
    h_clearflag FLAG_HIDE_PETALBURG_GYM_GUIDE
    h_setflag FLAG_PETALBURG_MART_EXPANDED_ITEMS
    h_setflag FLAG_RECEIVED_POKENAV
    h_setflag FLAG_RETURNED_DEVON_GOODS
    h_setflag FLAG_DELIVERED_DEVON_GOODS
    h_setflag FLAG_RECEIVED_HM04
    ItemAdd ITEM_HM01, 1, HLIB_TMP
    ItemAdd ITEM_HM04, 1, HLIB_TMP
    ItemAdd ITEM_TM70, 1, HLIB_TMP      // Flash
    ItemAdd ITEM_TM94, 1, HLIB_TMP      // Rock Smash
    ItemAdd ITEM_BICYCLE, 1, HLIB_TMP   // the Mach Bike
    MoneyAdd 10000
#if (HOENN_TEST_CH6 + 0) >= 2 || defined(HOENN_TEST_CH12)
    // Chapter 6: Norman beaten, Surf
    TrainerCardAddBadge 4
    FlagSet 2418
    h_setflag FLAG_DEFEATED_PETALBURG_GYM
    h_setvar VAR_PETALBURG_GYM_STATE, 7
    h_settrainerflag TRAINER_NORMAN
    h_set_gym_trainers 5
    h_setflag FLAG_RECEIVED_TM42
    h_setflag FLAG_HIDE_WATTSON_MAUVILLE_GYM
    h_clearflag FLAG_HIDE_WATTSON_MAUVILLE
    h_clearflag FLAG_HIDE_SLUDGE_BOMB_MAN_DEWFORD_HALL
#endif
#if (HOENN_TEST_CH6 + 0) >= 3 || defined(HOENN_TEST_CH12)
    h_setflag FLAG_RECEIVED_HM_SURF            // Wally's father's HM03 (stage 2 leaves it to him)
    ItemAdd ITEM_HM03, 1, HLIB_TMP
    h_setflag FLAG_RECEIVED_BASEMENT_KEY
    ItemAdd ITEM_BASEMENT_KEY, 1, HLIB_TMP
    ItemAdd ITEM_SCANNER, 1, HLIB_TMP
    h_clearflag FLAG_HIDE_STERN_SLATEPORT_HARBOR       // Capt. Stern at the Slateport Harbor (chapter Ch8's time)
    ItemAdd ITEM_STORAGE_KEY, 1, HLIB_TMP               // the Abandoned Ship's keys (Storage Room, rooms 1/2/4/6)
    ItemAdd ITEM_ROOM_1_KEY, 1, HLIB_TMP
    ItemAdd ITEM_ROOM_2_KEY, 1, HLIB_TMP
    ItemAdd ITEM_ROOM_4_KEY, 1, HLIB_TMP
    ItemAdd ITEM_ROOM_6_KEY, 1, HLIB_TMP
    TrainerCardAddBadge 5
    FlagSet 2419
    TrainerCardAddBadge 6
    FlagSet 2420
    TrainerCardAddBadge 7
    FlagSet 2421
    ItemAdd ITEM_HM02, 1, HLIB_TMP
    ItemAdd ITEM_HM05, 1, HLIB_TMP
    ItemAdd ITEM_HM06, 1, HLIB_TMP
#endif
#if (HOENN_TEST_CH6 + 0) >= 4
    h_setvar VAR_NEW_MAUVILLE_STATE, 2          // New Mauville's generator is off: Wattson gives TM24
#endif
#if (HOENN_TEST_CH6 + 0) >= 5
    h_setvar VAR_NEW_MAUVILLE_STATE, 1          // the Basement Key's door is open: the generator switch works
#endif
#ifdef HOENN_TEST_CH12
    // Chapters 7-10 (badges 6-8, Fly, Dive, Waterfall) for the southern seas and the Regi puzzle
    TrainerCardAddBadge 5
    FlagSet 2419
    TrainerCardAddBadge 6
    FlagSet 2420
    TrainerCardAddBadge 7
    FlagSet 2421
    ItemAdd ITEM_HM02, 1, HLIB_TMP
    ItemAdd ITEM_HM05, 1, HLIB_TMP
    ItemAdd ITEM_HM06, 1, HLIB_TMP
    PokePartyAdd HLIB_TMP, SPECIES_BELLOSSOM, 0, 30     // Pacifidlog's trade (before the Wailord: it stays last)
    PokePartyAdd HLIB_TMP, SPECIES_WAILORD, 0, 50
#if (HOENN_TEST_CH12 + 0) >= 3
    h_setflag FLAG_REGI_DOORS_OPENED                    // the Sealed Chamber has been solved (Route 105's Island Cave opens)
#endif
#if (HOENN_TEST_CH12 + 0) >= 2
    WorkSetConst HLIB_TMP, 0                            // the lead's friendship up for the Fan Club's TM (Return)
    PokePartyAdjustHappiness HLIB_TMP, 30, 1
    PokePartyAdjustHappiness HLIB_TMP, 30, 1
    PokePartyAdjustHappiness HLIB_TMP, 30, 1
    PokePartyAdjustHappiness HLIB_TMP, 30, 1
#endif
#endif
#ifdef HOENN_EMERALD
#include "scenes/emerald_test_chain.inc"
#ifdef HOENN_TEST_CH12
    em_test_chain 120                       // Emerald-only state before Ch12 (scenes/emerald_test_chain.inc)
#else
    em_test_chain 60                        // Emerald-only state before Ch6 (scenes/emerald_test_chain.inc)
#endif
#endif
L_C6T_Done:
    VMReturn
#endif
#endif
