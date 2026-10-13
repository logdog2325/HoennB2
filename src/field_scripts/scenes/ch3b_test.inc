// Chapter 3 part 3b test start (test builds only, HOENN_TEST_CH3B=<stage>): included in the bodies of
// scenes/Route110.inc and scenes/MauvilleCity.inc (their zone inits call it). Never assembled into normal builds.
#ifdef HOENN_TEST_CH3B
// TEST ONLY (HOENN_TEST_CH3B=<stage>, notes/STORY_PORTING.md "Test switches"): the end of Chapter 3a on the first zone
// init of Route 110 or Mauville (start from a Littleroot savestate with HOENN_TEST_WARP=368,264,309: in front of the
// Cycling Road's south gate, or 406,249,210: Mauville's west edge; walk through a door once before talking to people). Party: one Lv 100 Swampert (battles ask no "Will
// you switch?"). Stages: 1 = after Slateport's museum (badges 1-2); 2 = also Wattson beaten (Dynamo Badge, HM06 = TM94,
// the Mach Bike, a second Pokémon and money: the Rusturf reunion, the Day Care, the side beats); 3 = as 1 but
// before the museum scene (the Aqua grunts still on Route 110).
#include "hoenn_key_items.h"
Test_Ch3bStart:
    PokePartyRecoverAll                 // every entry of Route 110 / Mauville: a full heal (PP too) for battle tests
    h_goto_if_set FLAG_RETURNED_DEVON_GOODS, L_C3BT_Done
    // Chapter 1's end (scenes/ch2_test.inc)
    FlagSet 2401                        // FLAG_SYS_POKEMON_GET
    FlagSet 2403                        // FLAG_SYS_B_DASH (Running Shoes)
    h_setflag FLAG_SYS_POKEDEX_GET
    FlagSet 2402                        // Black 2's Pokédex flag
    h_setflag FLAG_ADVENTURE_STARTED
    h_setflag FLAG_DEFEATED_RIVAL_ROUTE103
    h_setvar VAR_STARTER_MON, 2
    h_getpartysize HLIB_TMP
    h_goto_if_ne HLIB_TMP, 0, L_C3BT_Party
    PokePartyAdd HLIB_TMP, SPECIES_SWAMPERT, 0, 100
L_C3BT_Party:
    TrainerCardAddBadge 0               // (h_givebadge: TrainerCardSaveGymVictoryParty may not run in a zone init)
    FlagSet 2414
    h_setflag FLAG_DEFEATED_RUSTBORO_GYM
    h_settrainerflag TRAINER_ROXANNE
    h_set_gym_trainers 1
    // Chapter 2's end
    h_setflag FLAG_RECOVERED_DEVON_GOODS
    h_setflag FLAG_RETURNED_DEVON_GOODS
    h_setvar VAR_RUSTURF_TUNNEL_STATE, 3
    h_setflag FLAG_HIDE_BRINEY_RUSTURF_TUNNEL
    h_setflag FLAG_HIDE_GRUNT_RUSTURF_TUNNEL
    h_setflag FLAG_HIDE_PEEKO_RUSTURF_TUNNEL
    h_clearflag FLAG_HIDE_BOYFRIEND_RUSTURF_TUNNEL
    h_clearflag FLAG_HIDE_GIRLFRIEND_RUSTURF_TUNNEL
    h_setflag FLAG_RECEIVED_POKENAV
    h_setflag FLAG_DELIVERED_STEVEN_LETTER
    TrainerCardAddBadge 1               // (h_givebadge: TrainerCardSaveGymVictoryParty may not run in a zone init)
    FlagSet 2415
    h_setflag FLAG_DEFEATED_DEWFORD_GYM
    h_settrainerflag TRAINER_BRAWLY
    h_set_gym_trainers 2
    h_setvar VAR_PETALBURG_GYM_STATE, 3
    // Chapter 3a's end (Slateport: the museum)
    h_setflag FLAG_VISITED_SLATEPORT_CITY
    h_setflag FLAG_DOCK_REJECTED_DEVON_GOODS
#if (HOENN_TEST_CH3B + 0) != 3
    h_setflag FLAG_HIDE_EVIL_TEAM_ROUTE110
    h_setflag FLAG_DELIVERED_DEVON_GOODS
    h_clearflag FLAG_HIDE_DEVON_EMPLOYEE_ROUTE116
    h_setflag FLAG_HIDE_EMPLOYEE_DEVON_CORP_3F
#endif
    // walking tests: Route 110's and Route 117's eye-contact trainers count as beaten
    h_settrainerflag TRAINER_EDWARD
    h_settrainerflag TRAINER_JACLYN
    h_settrainerflag TRAINER_EDWIN_1
    h_settrainerflag TRAINER_DALE
    h_settrainerflag TRAINER_JACOB
    h_settrainerflag TRAINER_ANTHONY
    h_settrainerflag TRAINER_BENJAMIN_1
    h_settrainerflag TRAINER_JASMINE
    h_settrainerflag TRAINER_ABIGAIL_1
    h_settrainerflag TRAINER_ISABEL_1
    h_settrainerflag TRAINER_TIMMY
    h_settrainerflag TRAINER_ISAAC_1
    h_settrainerflag TRAINER_LYDIA_1
    h_settrainerflag TRAINER_DYLAN_1
    h_settrainerflag TRAINER_MARIA_1
    h_settrainerflag TRAINER_DEREK
    h_settrainerflag TRAINER_ANNA_AND_MEG_1
    h_settrainerflag TRAINER_MIKE_2           // Rusturf Tunnel's hiker
    MoneyAdd 3000
#if (HOENN_TEST_CH3B + 0) == 2
    // Wattson beaten: the Dynamo Badge, TM34, Rydel's bike, HM06 (Rock Smash = Black 2's TM94), a second Pokémon
    TrainerCardAddBadge 2               // (h_givebadge: TrainerCardSaveGymVictoryParty may not run in a zone init)
    FlagSet 2416
    h_setflag FLAG_DEFEATED_MAUVILLE_GYM
    h_settrainerflag TRAINER_WATTSON
    h_set_gym_trainers 3
    h_setflag FLAG_RECEIVED_TM_SHOCK_WAVE
    h_setvar VAR_PETALBURG_GYM_STATE, 4
    h_setflag FLAG_RECEIVED_BIKE
    ItemAdd ITEM_MACH_BIKE, 1, HLIB_TMP
    h_setflag FLAG_DEFEATED_WALLY_MAUVILLE      // Wally beaten in Mauville: he and his uncle are in Wanda's house
    h_settrainerflag TRAINER_WALLY_2
    h_setflag FLAG_HIDE_WALLY_MAUVILLE
    h_setflag FLAG_HIDE_WALLY_FATHER_MAUVILLE
    h_clearflag FLAG_HIDE_WALLY_WANDAS_HOUSE
    h_clearflag FLAG_HIDE_WALLY_FATHER_WANDAS_HOUSE
    h_setvar VAR_ROUTE110_STATE, 1
    h_setflag FLAG_RECEIVED_HM06
    ItemAdd ITEM_TM94, 1, HLIB_TMP
    PokePartyAdd HLIB_TMP, SPECIES_MARILL, 0, 20
    MoneyAdd 20000
#endif
#ifdef HOENN_EMERALD
#include "scenes/emerald_test_chain.inc"
    em_test_chain 31                                  // Emerald-only state of the chapters before (scenes/emerald_test_chain.inc)
#endif
L_C3BT_Done:
    VMReturn
#endif
