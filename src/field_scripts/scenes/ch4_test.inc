// Chapter 4 test start (test builds only, HOENN_TEST_CH4=<stage>): included in the body of scenes/Route111.inc; its
// zone init calls it. Never assembled into normal builds.
#ifdef HOENN_TEST_CH4
// TEST ONLY (HOENN_TEST_CH4=<stage>, notes/STORY_PORTING.md "Test switches"): the end of Chapter 3 on the first zone
// init of Route 111. Start from work/emu/base_littleroot.dst with HOENN_TEST_WARP=554,4,7 (inside the Winstrate house;
// walk out of its door: Route 111's zone init runs the start) and HOENN_TEST_NO_WILD=1. Party: one Lv 100 Swampert + a
// Lv 100 Wailord (double battles). Stages: 1 = Chapter 3's end (badges 1-3, Mach Bike, HM06, a Heart Scale for the Move
// Tutor); 2 = also Chapter 5's end (Mt. Chimney beaten, badge 4, the Go-Goggles on the SECOND entry of Route 111: the first
// entry tests the sandstorm without them; Meteor Falls' scene still plays). Gabby & Ty (Route 111's first pair) stay
// unbeaten, every other eye-contact trainer of Routes 111-115 counts as beaten.
// Stage 3 (HOENN_TEST_WARP=576,3,4 = Devon Corp 2F by the stairs; go up to 3F and back for a real warp): talking to the
// fossil scientist without a fossil first gives a Root Fossil and a Pokémon (scenes/RustboroCity_DevonCorp_2F_Fossil.inc).
// Walk-test notes: work/agents/ch4/tests (ch4lib.py, t_*.py).
#include "hoenn_key_items.h"
Test_Ch4Start:
    PokePartyRecoverAll                 // every entry of Route 111: a full heal (PP too) for battle tests
#if (HOENN_TEST_CH4 + 0) == 2
    // the Go-Goggles come on the SECOND entry of Route 111 (the first one tests the sandstorm without them)
    h_goto_if_unset FLAG_RECEIVED_GO_GOGGLES, L_C4T_NoGoggles
    h_checkitem ITEM_GO_GOGGLES, 1, HLIB_TMP
    h_goto_if_eq HLIB_TMP, 1, L_C4T_NoGoggles
    ItemAdd ITEM_GO_GOGGLES, 1, HLIB_TMP
L_C4T_NoGoggles:
#endif
    h_goto_if_set FLAG_RECEIVED_HM06, L_C4T_Done
    FlagSet 2401                        // FLAG_SYS_POKEMON_GET
    FlagSet 2403                        // FLAG_SYS_B_DASH (Running Shoes)
    h_setflag FLAG_SYS_POKEDEX_GET
    FlagSet 2402                        // Black 2's Pokédex flag
    h_setflag FLAG_ADVENTURE_STARTED
    h_setflag FLAG_DEFEATED_RIVAL_ROUTE103
    h_getpartysize HLIB_TMP
    h_goto_if_ne HLIB_TMP, 0, L_C4T_Party
    PokePartyAdd HLIB_TMP, SPECIES_SWAMPERT, 0, 100
    PokePartyAdd HLIB_TMP, SPECIES_WAILORD, 0, 100
L_C4T_Party:
    TrainerCardAddBadge 0               // (h_givebadge: TrainerCardSaveGymVictoryParty may not run in a zone init)
    FlagSet 2414
    TrainerCardAddBadge 1
    FlagSet 2415
    TrainerCardAddBadge 2
    FlagSet 2416
    h_setflag FLAG_RECOVERED_DEVON_GOODS
    h_setflag FLAG_RETURNED_DEVON_GOODS
    h_setflag FLAG_RECEIVED_POKENAV
    h_setflag FLAG_DELIVERED_STEVEN_LETTER
    h_setflag FLAG_DELIVERED_DEVON_GOODS
    h_setflag FLAG_RECEIVED_HM06
    h_setvar VAR_PETALBURG_GYM_STATE, 3
    ItemAdd ITEM_MACH_BIKE, 1, HLIB_TMP
    ItemAdd ITEM_TM94, 1, HLIB_TMP      // HM06 Rock Smash (Black 2's TM94)
    MoneyAdd 30000
    // walking tests: Route 111-115's eye-contact trainers count as beaten
    h_settrainerflag TRAINER_DREW
    h_settrainerflag TRAINER_HEIDI
    h_settrainerflag TRAINER_CLIFF
    h_settrainerflag TRAINER_BECKY
    h_settrainerflag TRAINER_DUSTY_1
    h_settrainerflag TRAINER_TRAVIS
    h_settrainerflag TRAINER_IRENE
    h_settrainerflag TRAINER_DAISUKE
    h_settrainerflag TRAINER_WILTON_1
    h_settrainerflag TRAINER_BROOKE_1
    h_settrainerflag TRAINER_BRICE
    h_settrainerflag TRAINER_TRENT_1
    h_settrainerflag TRAINER_LARRY
    h_settrainerflag TRAINER_CAROL
    h_settrainerflag TRAINER_NEAL
    h_settrainerflag TRAINER_DILLON
    h_settrainerflag TRAINER_MADELINE_1
    h_settrainerflag TRAINER_LAO_1
    h_settrainerflag TRAINER_LUNG
    h_settrainerflag TRAINER_TORI_AND_TIA
    h_settrainerflag TRAINER_LENNY
    h_settrainerflag TRAINER_LUCAS_1
    h_settrainerflag TRAINER_SHANE
    h_settrainerflag TRAINER_NANCY
    h_settrainerflag TRAINER_STEVE_1
    h_settrainerflag TRAINER_BERNIE_1
    h_settrainerflag TRAINER_CLAUDE
    h_settrainerflag TRAINER_NOLAN
    h_settrainerflag TRAINER_TYRA_AND_IVY
    // (Gabby & Ty, Route 111's first pair, stay unbeaten: their double battle + interview is tested)
#if (HOENN_TEST_CH4 + 0) == 2
    // Chapter 5's end: Mt. Chimney (the teams gone, Cozmo home), the Heat Badge, the Go-Goggles
    h_setflag FLAG_DEFEATED_EVIL_TEAM_MT_CHIMNEY
    // (Meteor Falls' scene is left to play: VAR_METEOR_FALLS_STATE stays 0 for the test)
    TrainerCardAddBadge 3
    FlagSet 2417
    h_setflag FLAG_RECEIVED_GO_GOGGLES   // (the item itself on the next entry, above)
#endif
    ItemAdd ITEM_HEART_SCALE, 1, HLIB_TMP   // the Move Tutor
#ifdef HOENN_EMERALD
#include "scenes/emerald_test_chain.inc"
    em_test_chain 40                                  // Emerald-only state of the chapters before (scenes/emerald_test_chain.inc)
#endif
L_C4T_Done:
    VMReturn
#endif
