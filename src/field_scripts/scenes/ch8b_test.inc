// Chapter 8 part 8b test start (test builds only, HOENN_TEST_CH8B=<stage>; notes/STORY_PORTING.md "Test switches").
// Included in the body of scenes/Route121.inc and called from Route 121's zone init, once. Never assembled into normal
// builds. From work/emu/base_littleroot.dst with HOENN_TEST_WARP=475,<x>,<z> (Route 121; tile = Sapphire (x,z) + (448,140)):
// the end state of Chapters 1-7 (six Badges, Surf, Fly, a Lv 100 party when empty), then walk the chapter.
// Stages: 1 = Route 121 as Sapphire leaves it after Fortree (the grunts still stand on the road); 2 = also the Mt. Pyre
// summit scene done (the Blue Orb in the Bag, Slateport's state 1 armed): for the Slateport and Hideout tests.
#ifdef HOENN_TEST_CH8B
#ifndef CH8B_TEST_INC
#define CH8B_TEST_INC
#include "hoenn_key_items.h"
#include "hoenn_version.inc"             // ITEM_RED_OR_BLUE_ORB (ruby_scenes)
#define CH8B_TEST_DONE 750                  // (test only) Ch8's last reserved flag: the start state was written
Test_Ch8bStart:
    PokePartyRecoverAll                     // every entry: a full heal for battle tests
    h_goto_if_set CH8B_TEST_DONE, L_C8T_Done
    h_setflag CH8B_TEST_DONE
    FlagSet 2401                            // FLAG_SYS_POKEMON_GET
    FlagSet 2403                            // FLAG_SYS_B_DASH
    FlagSet 2402                            // Black 2's Pokedex flag
    h_setflag FLAG_SYS_POKEDEX_GET
    h_setflag FLAG_ADVENTURE_STARTED
    h_setflag FLAG_DEFEATED_RIVAL_ROUTE103
    h_setvar VAR_STARTER_MON, 2
    h_getpartysize HLIB_TMP
    h_goto_if_ne HLIB_TMP, 0, L_C8T_Party
    PokePartyAdd HLIB_TMP, SPECIES_SWAMPERT, 0, 100
L_C8T_Party:
    TrainerCardAddBadge 0                   // h_givebadge's TrainerCardSaveGymVictoryParty may not run in a zone init
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
    h_set_gym_trainers 1
    h_set_gym_trainers 2
    h_set_gym_trainers 3
    h_set_gym_trainers 4
    h_set_gym_trainers 5
    h_set_gym_trainers 6
    h_setflag FLAG_RECEIVED_POKENAV
    h_setflag FLAG_RETURNED_DEVON_GOODS
    h_setflag FLAG_DELIVERED_DEVON_GOODS
    h_setflag FLAG_RECEIVED_HM04
    h_setflag FLAG_RECEIVED_HM_SURF
    h_setflag FLAG_RECEIVED_HM02
    h_setflag FLAG_RECEIVED_DEVON_SCOPE
    h_setflag FLAG_VISITED_SLATEPORT_CITY
    h_setflag FLAG_HIDE_EVIL_TEAM_SLATEPORT        // the museum robbery (Ch3) is over
    h_setflag FLAG_HIDE_EVIL_TEAM_OCEANIC_MUSEUM
    h_setflag FLAG_HIDE_GRUNT_1_OCEANIC_MUSEUM_2F
    h_setflag FLAG_HIDE_GRUNT_2_OCEANIC_MUSEUM_2F
    ItemAdd ITEM_HM01, 1, HLIB_TMP
    ItemAdd ITEM_HM02, 1, HLIB_TMP
    ItemAdd ITEM_HM03, 1, HLIB_TMP
    ItemAdd ITEM_HM04, 1, HLIB_TMP
    ItemAdd ITEM_BICYCLE, 1, HLIB_TMP
    ItemAdd ITEM_POKEBLOCK_CASE, 1, HLIB_TMP
    MoneyAdd 20000
#if (HOENN_TEST_CH8B + 0) >= 2
    // the summit scene (scenes/MtPyre_Summit.inc) is over
    h_setflag FLAG_MT_PYRE_ORB_STOLEN
    h_setflag FLAG_HIDE_LEADER_MT_PYRE_SUMMIT
    h_setflag FLAG_HIDE_GRUNTS_MT_PYRE_SUMMIT
    h_setflag FLAG_HIDE_GRUNTS_ROUTE121
    h_setvar VAR_ROUTE121_STATE, 1
    h_setvar VAR_SLATEPORT_STATE, 1
    h_setvar VAR_SLATEPORT_HARBOR_STATE, 1
    h_setvar VAR_MT_PYRE_STATE, 1
    h_clearflag FLAG_HIDE_STERN_SLATEPORT
    h_clearflag FLAG_HIDE_GABBY_AND_TY_SLATEPORT
    h_setflag FLAG_RECEIVED_RED_OR_BLUE_ORB
#ifdef HOENN_EMERALD
    ItemAdd ITEM_MAGMA_EMBLEM, 1, HLIB_TMP        // Emerald: the old woman gives the Magma Emblem, no Orb (scenes/MtPyre_Summit_Em.inc)
    h_setflag FLAG_HIDE_JAGGED_PASS_MAGMA_GUARD
    h_setflag FLAG_HIDE_MT_PYRE_SUMMIT_MAXIE      // (hidden since the start; Sootopolis brings him back)
#else
    ItemAdd ITEM_RED_OR_BLUE_ORB, 1, HLIB_TMP     // the Blue Orb (Ruby: the Red Orb)
#endif
#endif
#ifdef HOENN_EMERALD
    h_setflag FLAG_HIDE_MAGMA_HIDEOUT_4F_GROUDON      // a new-game flag (Sub_NewGameFlags): the awake Groudon of the Magma Hideout waits hidden (savestates made before it lack it)
#include "scenes/emerald_test_chain.inc"
    em_test_chain 81                                  // Emerald-only state of the chapters before (scenes/emerald_test_chain.inc)
#endif
L_C8T_Done:
    VMReturn
#endif
#endif
