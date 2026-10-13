// Chapter 5 test start (test builds only, HOENN_TEST_CH5=<stage>): Test_Ch5Start sets the start-of-chapter state once
// (flag 539 guards it). Called from the Route 112 cable car station's and Lavaridge's zone inits (this file is included
// by 1110_room_Route112_CableCarStation.s and scenes/LavaridgeTown.inc) and, in the ch5 agent's private build, from
// Littleroot's town sign before its HOENN_TEST_WARP warp (work/agents/ch5/build_tree.sh patches that copy of 0778).
// Never assembled into normal builds. Start from work/emu/base_littleroot.dst; HOENN_TEST_WARP=zone,x,z picks the place:
//   374,236,108 Route 112 in front of the cable car station (walk in: a real warp)   62,196,129 Lavaridge Town
//   145,9,23 the Gym 1F's door (walk down: out of the door starts the rival scene, stage 3)   6,134,80 Fallarbor, Cozmo's house
// Stages: 1 = the end of Chapter 4 (badges 1-3, Meteor Falls done: the cable car is free); 2 = also Mt. Chimney done
// (Archie beaten, the Meteorite in the Bag: Lavaridge, the Gym and Cozmo); 3 = also Flannery beaten (VAR_LAVARIDGE_RIVAL_STATE 1:
// the rival's Go-Goggles scene is next). Party: one Lv 100 Swampert if the party is empty.
// (After a test warp NPCs/triggers work again only once the player has gone through a real door.)
#ifdef HOENN_TEST_CH5
#ifndef CH5_TEST_INC
#define CH5_TEST_INC
#include "hoenn_key_items.h"
#include "hoenn_version.inc"             // TRAINER_MT_CHIMNEY_GRUNT_1..3 (the role names)
#define CH5_TEST_DONE 539                   // (test only) Ch5's last reserved flag: the start state was written
Test_Ch5Start:
    PokePartyRecoverAll                     // every entry: a full heal for battle tests
    h_goto_if_set CH5_TEST_DONE, L_C5T_Done
    h_setflag CH5_TEST_DONE
    FlagSet 2401                            // FLAG_SYS_POKEMON_GET
    FlagSet 2403                            // FLAG_SYS_B_DASH (Running Shoes)
    h_setflag FLAG_SYS_POKEDEX_GET
    FlagSet 2402                            // Black 2's Pokédex flag
    h_setflag FLAG_ADVENTURE_STARTED
    h_setflag FLAG_DEFEATED_RIVAL_ROUTE103
    h_setvar VAR_STARTER_MON, 2
    h_getpartysize HLIB_TMP
    h_goto_if_ne HLIB_TMP, 0, L_C5T_Party
#ifdef HOENN_TEST_CH5_WEAK                  // a party that loses (whiteout tests): one Lv 2 Magikarp
    PokePartyAdd HLIB_TMP, SPECIES_MAGIKARP, 0, 2
#else
    PokePartyAdd HLIB_TMP, SPECIES_SWAMPERT, 0, 100
#endif
L_C5T_Party:
    // badges 1-3 (h_givebadge: TrainerCardSaveGymVictoryParty may not run in a zone init)
    TrainerCardAddBadge 0
    FlagSet 2414
    TrainerCardAddBadge 1
    FlagSet 2415
    TrainerCardAddBadge 2
    FlagSet 2416
    h_setflag FLAG_DEFEATED_RUSTBORO_GYM
    h_setflag FLAG_DEFEATED_DEWFORD_GYM
    h_setflag FLAG_DEFEATED_MAUVILLE_GYM
    h_settrainerflag TRAINER_ROXANNE
    h_settrainerflag TRAINER_BRAWLY
    h_settrainerflag TRAINER_WATTSON
    h_set_gym_trainers 1
    h_set_gym_trainers 2
    h_set_gym_trainers 3
    h_setvar VAR_PETALBURG_GYM_STATE, 5     // tutorial 2 + three badges (Flannery makes it 6: Norman's Gym opens)
    h_setflag FLAG_RECEIVED_POKENAV
    h_setflag FLAG_DELIVERED_STEVEN_LETTER
    h_setflag FLAG_RETURNED_DEVON_GOODS
    h_setflag FLAG_DELIVERED_DEVON_GOODS
    h_setflag FLAG_VISITED_SLATEPORT_CITY
    h_setflag FLAG_VISITED_FALLARBOR_TOWN
    // Chapter 4's end: the Meteor Falls scene freed the cable car; Cozmo is still away
    h_setflag FLAG_HIDE_GRUNTS_BLOCKING_CABLE_CAR
    h_setflag FLAG_MET_PROF_COSMO
    h_setvar VAR_METEOR_FALLS_STATE, 1
    h_setvar VAR_CABLE_CAR_STATION_STATE, 0
    MoneyAdd 5000
#if (HOENN_TEST_CH5 + 0) >= 2
    // Mt. Chimney done (scenes/MtChimney.inc MC_Archie, MC_Machine)
    h_setflag FLAG_EVIL_LEADER_PLEASE_STOP
    h_setflag FLAG_HIDE_EVIL_TEAM_MT_CHIMNEY
    h_setflag FLAG_HIDE_OTHER_TEAM_MT_CHIMNEY
    h_setflag FLAG_DEFEATED_EVIL_TEAM_MT_CHIMNEY
    h_clearflag FLAG_HIDE_PROF_COSMO_FALLARBOR
    h_setflag FLAG_HIDE_PROF_COSMO_METEOR_FALLS
    h_settrainerflag TRAINER_MT_CHIMNEY_GRUNT_3    // (Sapphire: Archie 3, Ruby: Maxie 3, Emerald: Maxie; hoenn_version.inc)
    h_settrainerflag TRAINER_MT_CHIMNEY_GRUNT_1
    h_settrainerflag TRAINER_MT_CHIMNEY_GRUNT_2
#ifdef HOENN_EMERALD
    h_settrainerflag TRAINER_GRUNT_MT_CHIMNEY_1    // Emerald's second grunt
    h_clearflag FLAG_HIDE_MT_CHIMNEY_LAVA_COOKIE_LADY   // the Lava Cookie lady is back after Maxie
#endif
    ItemAdd ITEM_METEORITE, 1, HLIB_TMP
    h_setflag FLAG_RECEIVED_METEORITE
#endif
#if (HOENN_TEST_CH5 + 0) >= 3
    // Flannery beaten (the rival's Go-Goggles scene runs when you step out of the Gym): scenes/LavaridgeTown.inc
    TrainerCardAddBadge 3
    FlagSet 2417
    h_setflag FLAG_DEFEATED_LAVARIDGE_GYM
    h_settrainerflag TRAINER_FLANNERY
    h_set_gym_trainers 4
    h_setflag FLAG_RECEIVED_TM_OVERHEAT
    h_addvar VAR_PETALBURG_GYM_STATE, 1
    h_setflag FLAG_HIDE_WALLY_WANDAS_HOUSE
    h_setvar VAR_LAVARIDGE_RIVAL_STATE, 1
#endif
#ifdef HOENN_EMERALD
    h_setflag FLAG_HIDE_MAGMA_HIDEOUT_4F_GROUDON      // a new-game flag (Sub_NewGameFlags): the awake Groudon of the Magma Hideout waits hidden (savestates made before it lack it)
#include "scenes/emerald_test_chain.inc"
    em_test_chain 50                                  // Emerald-only state of the chapters before (scenes/emerald_test_chain.inc)
#endif
L_C5T_Done:
    VMReturn
#endif
#endif
