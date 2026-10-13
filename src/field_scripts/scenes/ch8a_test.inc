// Chapter Ch8 part 8a test start (test builds only: HOENN_TEST_CH8A=<stage>; notes/STORY_PORTING.md "Test switches").
// Included in the body of scenes/LilycoveCity.inc and called from Lilycove's zone init. Never assembled into normal builds.
// From a cold-boot state of the same ROM (work/agents/ch8a/states/base_littleroot.dst) with HOENN_TEST_WARP=96,555,139
// (Lilycove, below the Department Store door where the rival waits): the first arrival gives the end state of
// Chapters 1-7 once (six Badges, Surf/Fly, a Lv 100 Swampert when the party is empty, money, the Pokédex).
// Stages: 1 = that; 3 = also eight Badges, the game cleared (Fan Club state 1, the Motel's staff appear) and 100000 $.
// Walk into a building and out again before talking to people (the test warp is not a real warp).
#ifdef HOENN_TEST_CH8A
#ifndef CH8A_TEST_INC
#define CH8A_TEST_INC
#if HOENN_TEST_CH8A >= 3
#include "common/fan_club.inc"
#endif
Test_Ch8aStart:
    PokePartyRecoverAll                 // every entry: a full heal (PP too) for battle tests
    h_goto_if_set FLAG_RECEIVED_DEVON_SCOPE, L_C8T_Done   // once
    FlagSet 2401                        // FLAG_SYS_POKEMON_GET
    FlagSet 2403                        // FLAG_SYS_B_DASH (Running Shoes)
    FlagSet 2402                        // Black 2's Pokédex flag
    h_setflag FLAG_SYS_POKEDEX_GET
    h_setflag FLAG_ADVENTURE_STARTED
    h_setflag FLAG_DEFEATED_RIVAL_ROUTE103
    h_setvar VAR_STARTER_MON, 2         // Mudkip: the rival battles TRAINER_MAY_LILYCOVE_MUDKIP / TRAINER_BRENDAN_LILYCOVE_MUDKIP
    h_getpartysize HLIB_TMP
    h_goto_if_ne HLIB_TMP, 0, L_C8T_Party
    PokePartyAdd HLIB_TMP, SPECIES_SWAMPERT, 0, 100
L_C8T_Party:
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
    h_setflag FLAG_RECEIVED_POKENAV
    h_setflag FLAG_RETURNED_DEVON_GOODS
    h_setflag FLAG_DELIVERED_DEVON_GOODS
    h_setflag FLAG_RECEIVED_HM04
    h_setflag FLAG_RECEIVED_HM_SURF
    h_setflag FLAG_RECEIVED_HM02
    h_setflag FLAG_RECEIVED_DEVON_SCOPE
    ItemAdd ITEM_HM01, 1, HLIB_TMP
    ItemAdd ITEM_HM02, 1, HLIB_TMP
    ItemAdd ITEM_HM03, 1, HLIB_TMP
    ItemAdd ITEM_HM04, 1, HLIB_TMP
    ItemAdd ITEM_BICYCLE, 1, HLIB_TMP   // the Mach Bike
    MoneyAdd 10000
#if HOENN_TEST_CH8A >= 3
    TrainerCardAddBadge 6               // the Mind and Rain Badges, the game cleared
    FlagSet 2420
    TrainerCardAddBadge 7
    FlagSet 2421
    h_setflag FLAG_SYS_GAME_CLEAR
    h_clearflag FLAG_HIDE_LILYCOVE_MOTEL_PEOPLE
    h_setflag FLAG_EVIL_TEAM_ESCAPED_IN_SUBMARINE
    h_setflag FLAG_HIDE_GRUNTS_LILYCOVE
    MoneyAdd 50000
    MoneyAdd 50000
    VMCall Sub_FanClub_GameClear        // UpdateTrainerFanClubGameClear (Ch11's Hall of Fame calls it)
#endif
#ifdef HOENN_EMERALD
#include "scenes/emerald_test_chain.inc"
    em_test_chain 80                                  // Emerald-only state of the chapters before (scenes/emerald_test_chain.inc)
#endif
L_C8T_Done:
    VMReturn
#endif
#endif
