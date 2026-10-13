// Chapter Ch2 test start (test builds only: HOENN_TEST_CH2=<stage>, notes/STORY_PORTING.md "Test switches"). Included
// in the body of the scene that starts each stage (an OnFrame scene while VAR_RUSTBORO_STATE is 0, i.e. once per new
// game); never assembled into normal builds. Start from a Littleroot savestate with HOENN_TEST_WARP=<zone,x,z>:
//   1  Rustboro after Roxanne (Ch1's end):        HOENN_TEST_WARP=113,75,201 (Rustboro, below the Gym)
//   2  ...and Devon Corp done (PokéNav, Letter): HOENN_TEST_WARP=329,65,291 (Route 104, Mr. Briney's door; the state
//      is set on entering his cottage, re-enter to see him)
//   3  ...and the Letter delivered, Knuckle Badge: HOENN_TEST_WARP=113,75,201 (Rustboro: Mr. Stone's Exp. Share) or
//      HOENN_TEST_WARP=329,65,291 (Mr. Briney's cottage: the boat to Dewford, then to Slateport / Route 109)
// Walking tests: Route 104 and Route 116's eye-contact trainers count as beaten. Party: one Lv 50 Swampert (one Pokémon: battles ask no
// "Will you switch?", so a test can press A through them).
#ifdef HOENN_TEST_CH2
#include "hoenn_key_items.h"
Sub_Ch2TestStart:
    h_goto_if_ne VAR_RUSTBORO_STATE, 0, L_Ch2TestDone
    // Ch1's end: the Pokédex, Running Shoes, Mudkip chosen, Roxanne beaten
    FlagSet 2401                    // FLAG_SYS_POKEMON_GET
    FlagSet 2403                    // FLAG_SYS_B_DASH (Running Shoes)
    h_setflag FLAG_SYS_POKEDEX_GET
    FlagSet 2402                    // Black 2's Pokédex flag (h_obtain_pokedex callers set it)
    h_setflag FLAG_ADVENTURE_STARTED
    h_setflag FLAG_DEFEATED_RIVAL_ROUTE103
    h_setflag FLAG_RECEIVED_RUNNING_SHOES
    h_setvar VAR_STARTER_MON, 2
    h_getpartysize HLIB_TMP
    h_goto_if_ne HLIB_TMP, 0, L_Ch2TestParty
    PokePartyAdd HLIB_TMP, SPECIES_SWAMPERT, 0, 50
L_Ch2TestParty:
    h_givebadge 1
    h_setflag FLAG_DEFEATED_RUSTBORO_GYM
    h_settrainerflag TRAINER_ROXANNE
    h_set_gym_trainers 1
    h_setflag FLAG_RECEIVED_TM_ROCK_TOMB
    h_settrainerflag TRAINER_CINDY_1
    h_settrainerflag TRAINER_WINSTON_1
    h_settrainerflag TRAINER_BILLY
    h_settrainerflag TRAINER_IVAN
    h_settrainerflag TRAINER_HALEY_1
    h_settrainerflag TRAINER_JOEY
    h_settrainerflag TRAINER_JOSE
    h_settrainerflag TRAINER_JERRY_1
    h_settrainerflag TRAINER_KAREN_1
    h_settrainerflag TRAINER_JANICE
    h_settrainerflag TRAINER_CLARK
    h_setvar VAR_RUSTBORO_STATE, 1
    h_setvar VAR_PETALBURG_GYM_STATE, 2      // Norman (1) + Roxanne (+1)
#if (HOENN_TEST_CH2 + 0) >= 2
    // the Devon Goods recovered and returned, Mr. Stone's PokéNav and Letter (Rustboro/Rusturf/Devon 3F's flags)
    h_setflag FLAG_UNKNOWN_9F
    h_setflag FLAG_RECOVERED_DEVON_GOODS
    h_setflag FLAG_RETURNED_DEVON_GOODS
    h_setflag FLAG_HIDE_DEVON_RUSTBORO
    h_setvar VAR_RUSTBORO_STATE, 5
    h_setvar VAR_RUSTURF_TUNNEL_STATE, 3
    h_setvar VAR_ROUTE116_STATE, 2
    h_setvar VAR_BRINEY_HOUSE_STATE, 1
    h_setvar VAR_DEVON_CORP_3F_STATE, 1
    h_setflag FLAG_HIDE_BRINEY_ROUTE116
    h_setflag FLAG_HIDE_BRINEY_RUSTURF_TUNNEL
    h_setflag FLAG_HIDE_GRUNT_RUSTURF_TUNNEL
    h_setflag FLAG_HIDE_PEEKO_RUSTURF_TUNNEL
    h_setflag FLAG_HIDE_TUNNER_DIGGER_ROUTE116
    h_clearflag FLAG_HIDE_BOYFRIEND_RUSTURF_TUNNEL
    h_clearflag FLAG_HIDE_GIRLFRIEND_RUSTURF_TUNNEL
    h_clearflag FLAG_HIDE_MR_BRINEY_ROUTE104_HOUSE
    h_clearflag FLAG_HIDE_PEEKO_BRINEY_HOUSE
    h_clearflag FLAG_HIDE_RIVAL_RUSTBORO
    h_setvar VAR_BRINEY_LOCATION, 1
    h_setflag FLAG_SYS_POKENAV_GET
    h_setflag FLAG_RECEIVED_POKENAV
    ItemAdd ITEM_DEVON_GOODS, 1, HLIB_TMP
    ItemAdd ITEM_LETTER, 1, HLIB_TMP
#ifdef HOENN_EMERALD                 // Emerald (emerald_ch0_3): Mr. Stone's scene also sets these (the school's Scott leaves; the rival waits in Rustboro)
    h_setflag FLAG_HIDE_RUSTBORO_CITY_POKEMON_SCHOOL_SCOTT
    h_setvar VAR_RUSTBORO_STATE, 7
    h_setvar VAR_ROUTE104_STATE, 1
#if defined(HOENN_TEST_CHDEVON) && (HOENN_TEST_CHDEVON + 0) == 2   // test only: =2 = Mr. Stone's scene is done but Scott is still in the school
    h_clearflag FLAG_HIDE_RUSTBORO_CITY_POKEMON_SCHOOL_SCOTT
#elif defined(HOENN_TEST_CHDEVON)    // test only (emerald_ch0_3): the state before Rustboro's employee takes the player to Mr. Stone
    h_clearflag FLAG_RETURNED_DEVON_GOODS      // (Rustboro triggers (30..31, 9..12): zone tiles (78..79, 189..192))
    h_clearflag FLAG_HIDE_DEVON_RUSTBORO
    h_clearflag FLAG_SYS_POKENAV_GET
    h_clearflag FLAG_RECEIVED_POKENAV
    h_clearflag FLAG_HIDE_RUSTBORO_CITY_POKEMON_SCHOOL_SCOTT
    h_setflag FLAG_HIDE_RIVAL_RUSTBORO
    h_setvar VAR_RUSTBORO_STATE, 4
    h_setvar VAR_DEVON_CORP_3F_STATE, 0
    h_setvar VAR_ROUTE104_STATE, 0
    ItemSub ITEM_LETTER, 1, HLIB_TMP
#endif
#endif
#endif
#if (HOENN_TEST_CH2 + 0) >= 3
    // Dewford: Brawly beaten, the Letter delivered to Steven
    ItemSub ITEM_LETTER, 1, HLIB_TMP
    h_setflag FLAG_DELIVERED_STEVEN_LETTER
    h_setflag FLAG_HIDE_STEVEN_GRANITE_CAVE
    h_setflag FLAG_MR_BRINEY_SAILING_INTRO
    h_givebadge 2
    h_setflag FLAG_DEFEATED_DEWFORD_GYM
    h_settrainerflag TRAINER_BRAWLY
    h_set_gym_trainers 2
    h_setflag FLAG_RECEIVED_TM_BULK_UP
    h_setvar VAR_PETALBURG_GYM_STATE, 3
#endif
#ifdef HOENN_EMERALD
#include "scenes/emerald_test_chain.inc"
    em_test_chain 20                                  // Emerald-only state of the chapters before (scenes/emerald_test_chain.inc)
#endif
L_Ch2TestDone:
    VMReturn
#endif
