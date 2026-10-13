// Chapter Ch10 test start (test builds only: HOENN_TEST_CH10=<stage>; notes/STORY_PORTING.md "Test switches"). Included in the
// body of scenes/Route128.inc and scenes/SootopolisCity.inc and called from their zone inits (and the test rooms' inits:
// Seafloor Cavern Room 1 / Room 9, the Cave of Origin's B4F, the Gym's 1F). Never assembled into normal builds.
// The first call (guard: FLAG_RECEIVED_HM08, Steven's Dive) gives the end of Chapters 1-9: seven Badges (the Mind Badge too),
// the HMs (Cut, Fly, Surf, Strength, Waterfall, Dive), Black 2's Bicycle, a Lv 100 Tyranitar (the lead) and a Lv 100 Swampert, the Blue Orb
// (Mt. Pyre) and money; the Wingull / Steven's-house flags do not matter here.
// Stage 1 = that. Stage 2 = also the flags Seafloor Cavern Room 9 ends with (Kyogre woke: the crisis, Route 128's scene armed,
// the residents of Sootopolis hidden, its doors closed, Wallace and Steven waiting at (30,6) / (29,6)). Stage 3 = also the flags
// of the Cave of Origin's end (Kyogre calmed: the weather over, the Gym open, Archie back on Mt. Pyre's summit).
#ifdef HOENN_TEST_CH10
#ifndef CH10_TEST_INC
#define CH10_TEST_INC
#include "hoenn_trainers.h"
#include "hoenn_key_items.h"
#include "hoenn_version.inc"             // ITEM_RED_OR_BLUE_ORB (ruby_scenes)
Test_Ch10Start:
    PokePartyRecoverAll                 // every entry: a full heal (PP too) for battle tests
    h_goto_if_set FLAG_RECEIVED_HM08, L_C10T_Stages
    FlagSet 2401                        // FLAG_SYS_POKEMON_GET
    FlagSet 2403                        // FLAG_SYS_B_DASH (Running Shoes)
    FlagSet 2402                        // Black 2's Pokédex flag
    h_setflag FLAG_SYS_POKEDEX_GET
    h_setflag FLAG_ADVENTURE_STARTED
    h_setflag FLAG_DEFEATED_RIVAL_ROUTE103
    h_setvar VAR_STARTER_MON, 2
    h_getpartysize HLIB_TMP
    h_goto_if_ne HLIB_TMP, 0, L_C10T_Party
#ifdef HOENN_TEST_CH10E_WEAK
    PokePartyAdd HLIB_TMP, SPECIES_MAGIKARP, 0, 2           // (Emerald, emerald_ch10: a forced loss, e.g. against Juan)
#else
    PokePartyAdd HLIB_TMP, SPECIES_TYRANITAR, 0, 100        // the lead: its first move is an attack (battle tests press A, A)
    PokePartyAdd HLIB_TMP, SPECIES_SWAMPERT, 0, 100
#endif
L_C10T_Party:
    TrainerCardAddBadge 0
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
    h_set_gym_trainers 7
    h_setflag FLAG_RECEIVED_POKENAV
    h_setflag FLAG_RETURNED_DEVON_GOODS
    h_setflag FLAG_DELIVERED_DEVON_GOODS
    h_setflag FLAG_DELIVERED_STEVEN_LETTER
    h_setflag FLAG_RECEIVED_HM04
    h_setflag FLAG_RECEIVED_HM02
    h_setflag FLAG_RECEIVED_HM_SURF
    h_setflag FLAG_RECEIVED_HM08
    ItemAdd ITEM_HM01, 1, HLIB_TMP
    ItemAdd ITEM_HM02, 1, HLIB_TMP
    ItemAdd ITEM_HM03, 1, HLIB_TMP
    ItemAdd ITEM_HM04, 1, HLIB_TMP
    ItemAdd ITEM_HM05, 1, HLIB_TMP
    ItemAdd ITEM_HM06, 1, HLIB_TMP
    ItemAdd ITEM_TM94, 1, HLIB_TMP      // Rock Smash (Black 2's TM94: hm_free's rock)
    ItemAdd ITEM_TM70, 1, HLIB_TMP      // Flash
    ItemAdd ITEM_BICYCLE, 1, HLIB_TMP   // the Mach Bike
    ItemAdd ITEM_RED_OR_BLUE_ORB, 1, HLIB_TMP   // the Blue Orb (Ruby: the Red Orb) from the old woman on Mt. Pyre's summit (chapter Ch8)
    h_setflag FLAG_RECEIVED_RED_OR_BLUE_ORB
    h_setflag FLAG_MT_PYRE_ORB_STOLEN
    h_setvar VAR_MT_PYRE_STATE, 1
    MoneyAdd 50000
L_C10T_Stages:
#if (HOENN_TEST_CH10 + 0) >= 2
    h_goto_if_set FLAG_LEGEND_ESCAPED_SEAFLOOR_CAVERN, L_C10T_Stage3     // (once)
    h_setvar VAR_ROUTE128_STATE, 1
    h_clearflag FLAG_HIDE_CAVE_OF_ORIGIN_ENTRANCE_WOMAN_1
    h_clearflag FLAG_HIDE_CAVE_OF_ORIGIN_ENTRANCE_WOMAN_2
    h_clearflag FLAG_HIDE_WALLACE_SOOTOPOLIS
    h_clearflag FLAG_HIDE_STEVEN_SOOTOPOLIS
    h_setvar VAR_SOOTOPOLIS_STATE, 1
    h_clearflag FLAG_HIDE_EVIL_LEADER_ROUTE128
    h_clearflag FLAG_HIDE_OTHER_LEADER_ROUTE128
    h_setflag FLAG_SYS_WEATHER_CTRL
    h_setflag FLAG_HIDE_SOOTOPOLIS_RESIDENTS
    h_setflag FLAG_LEGEND_ESCAPED_SEAFLOOR_CAVERN
    h_setflag FLAG_HIDE_STEVEN_STEVENS_HOUSE
    h_setvar VAR_STEVENS_HOUSE_STATE, 1
    h_setvar VAR_SEAFLOOR_CAVERN_STATE, 1
    h_setflag FLAG_HIDE_EVIL_LEADER_SEAFLOOR_CAVERN
    h_setflag FLAG_HIDE_OTHER_LEADER_SEAFLOOR_CAVERN
    h_setflag FLAG_HIDE_OTHER_TEAM_GRUNTS_SEAFLOOR_CAVERN
    h_setflag FLAG_HIDE_AWAKENED_MON_SEAFLOOR_CAVERN
    h_setflag FLAG_HIDE_SLEEPING_MON_SEAFLOOR_CAVERN
    h_setflag FLAG_HIDE_EVIL_TEAM_GRUNTS_SEAFLOOR_CAVERN
#endif
L_C10T_Stage3:
#if (HOENN_TEST_CH10 + 0) >= 3
    h_goto_if_set FLAG_LEGENDARY_BATTLE_COMPLETED, L_C10T_Done
    h_setflag FLAG_HIDE_WALLACE_SOOTOPOLIS
    h_setflag FLAG_HIDE_CAVE_OF_ORIGIN_ENTRANCE_WOMAN_1
    h_setflag FLAG_HIDE_CAVE_OF_ORIGIN_ENTRANCE_WOMAN_2
    h_clearflag FLAG_HIDE_WALLACE_SOOTOPOLIS_GYM
    h_setvar VAR_CAVE_OF_ORIGIN_B4F_STATE, 1
    h_setflag FLAG_LEGENDARY_BATTLE_COMPLETED
    h_clearflag FLAG_HIDE_SOOTOPOLIS_RESIDENTS
    h_clearflag FLAG_SYS_WEATHER_CTRL
    h_setvar VAR_MT_PYRE_STATE, 2
    h_clearflag FLAG_HIDE_LEADER_MT_PYRE_SUMMIT
    h_setflag FLAG_HIDE_LEGEND_MON_CAVE_OF_ORIGIN
    h_setflag FLAG_HIDE_GRUNTS_MT_PYRE_SUMMIT   // (the first Archie scene on Mt. Pyre's summit removed the grunts)
#endif
#ifdef HOENN_EMERALD
#include "scenes/emerald_test_chain.inc"
    em_test_chain 100                                 // Emerald-only state of the chapters before (scenes/emerald_test_chain.inc)
#if (HOENN_TEST_CH10E + 0) >= 2
// Emerald's Chapter 10 stages (emerald_ch10, 2026-10-12): HOENN_TEST_CH10=1 HOENN_TEST_CH10E=<stage>, each stage = the end of the
// scene before it (pokeemerald's flags, this port's names): 2 Seafloor Cavern's Room 9 (the legends fly to Sootopolis; Route
// 128's scene armed), 3 the legends' fight seen (state 2), 4 the Cave of Origin (Wallace went to the Sky Pillar, state 3), 5 Sky
// Pillar's outside (Wallace back in Sootopolis, state 4), 6 Rayquaza woke (state 5, VAR_SKY_PILLAR_STATE 1), 7 Rayquaza's scene in
// Sootopolis (the weather over, VAR_SKY_PILLAR_STATE 3, three Master Balls for the catch), 8 Archie and Maxie left (the Gym
// opens), 9 Waterfall from Wallace, 10 Juan beaten (state 6). Written once (flag 952, Ch10's last reserved flag: test only).
    h_goto_if_set 952, L_C10T_EmDone
    h_setflag 952
    h_setvar VAR_ROUTE128_STATE, 1
    h_setvar VAR_SOOTOPOLIS_STATE, 1
    h_clearflag FLAG_HIDE_STEVEN_SOOTOPOLIS
    h_clearflag FLAG_HIDE_SOOTOPOLIS_CITY_ARCHIE
    h_clearflag FLAG_HIDE_SOOTOPOLIS_CITY_MAXIE
    h_clearflag FLAG_HIDE_SOOTOPOLIS_CITY_RESIDENTS
    h_clearflag FLAG_HIDE_SOOTOPOLIS_CITY_GROUDON
    h_clearflag FLAG_HIDE_SOOTOPOLIS_CITY_KYOGRE
    h_setflag FLAG_HIDE_SOOTOPOLIS_CITY_MAN_1
    h_setflag FLAG_LEGENDARIES_IN_SOOTOPOLIS
    h_clearflag FLAG_HIDE_EVIL_LEADER_ROUTE128
    h_clearflag FLAG_HIDE_OTHER_LEADER_ROUTE128
    h_setflag FLAG_SYS_WEATHER_CTRL
    h_setflag FLAG_LEGEND_ESCAPED_SEAFLOOR_CAVERN
    h_setflag FLAG_HIDE_STEVEN_STEVENS_HOUSE
    h_setvar VAR_STEVENS_HOUSE_STATE, 2
    h_setvar VAR_SEAFLOOR_CAVERN_STATE, 1
    h_setflag FLAG_HIDE_EVIL_LEADER_SEAFLOOR_CAVERN
    h_setflag FLAG_HIDE_OTHER_LEADER_SEAFLOOR_CAVERN
    h_setflag FLAG_HIDE_OTHER_TEAM_GRUNTS_SEAFLOOR_CAVERN
    h_setflag FLAG_HIDE_AWAKENED_MON_SEAFLOOR_CAVERN
    h_setflag FLAG_HIDE_SLEEPING_MON_SEAFLOOR_CAVERN
    h_setflag FLAG_HIDE_EVIL_TEAM_GRUNTS_SEAFLOOR_CAVERN
#if (HOENN_TEST_CH10E + 0) >= 3
    h_setvar VAR_ROUTE128_STATE, 2
    h_setflag FLAG_HIDE_EVIL_LEADER_ROUTE128
    h_setflag FLAG_HIDE_OTHER_LEADER_ROUTE128
    h_setvar VAR_SOOTOPOLIS_STATE, 2
#endif
#if (HOENN_TEST_CH10E + 0) >= 4
    h_setflag FLAG_STEVEN_GUIDES_TO_CAVE_OF_ORIGIN
    h_setflag FLAG_WALLACE_GOES_TO_SKY_PILLAR
    h_setvar VAR_SOOTOPOLIS_STATE, 3
    h_setflag FLAG_HIDE_CAVE_OF_ORIGIN_B1F_WALLACE
    h_clearflag FLAG_HIDE_SKY_PILLAR_WALLACE
#endif
#if (HOENN_TEST_CH10E + 0) >= 5
    h_setvar VAR_SOOTOPOLIS_STATE, 4
    h_setflag FLAG_HIDE_SKY_PILLAR_WALLACE
    h_clearflag FLAG_HIDE_WALLACE_SOOTOPOLIS
#endif
#if (HOENN_TEST_CH10E + 0) >= 6
    h_setvar VAR_SOOTOPOLIS_STATE, 5
    h_setvar VAR_SKY_PILLAR_STATE, 1
    h_setvar VAR_SKY_PILLAR_RAYQUAZA_CRY_DONE, 1
    h_setflag FLAG_HIDE_SKY_PILLAR_TOP_RAYQUAZA
#endif
#if (HOENN_TEST_CH10E + 0) >= 7
    h_setflag FLAG_HIDE_SOOTOPOLIS_CITY_GROUDON
    h_setflag FLAG_HIDE_SOOTOPOLIS_CITY_KYOGRE
    h_clearflag FLAG_SYS_WEATHER_CTRL
    h_setvar VAR_SKY_PILLAR_STATE, 3
    h_clearflag FLAG_LEGENDARIES_IN_SOOTOPOLIS
    h_setflag FLAG_LEGENDARY_BATTLE_COMPLETED
    ItemAdd ITEM_MASTER_BALL, 3, HLIB_TMP
#endif
#if (HOENN_TEST_CH10E + 0) >= 8
    h_setflag FLAG_MET_MAXIE_SOOTOPOLIS
    h_setflag FLAG_MET_ARCHIE_SOOTOPOLIS
    h_setflag FLAG_HIDE_SOOTOPOLIS_CITY_MAXIE
    h_setflag FLAG_HIDE_SOOTOPOLIS_CITY_ARCHIE
    h_setflag FLAG_SOOTOPOLIS_ARCHIE_MAXIE_LEAVE
    h_clearflag FLAG_HIDE_MT_PYRE_SUMMIT_MAXIE
    h_clearflag FLAG_HIDE_LEADER_MT_PYRE_SUMMIT
    h_setvar VAR_MT_PYRE_STATE, 2
#endif
#if (HOENN_TEST_CH10E + 0) >= 9
    h_setflag FLAG_RECEIVED_HM_WATERFALL
    h_setvar VAR_SOOTOPOLIS_WALLACE_STATE, 1
#endif
#if (HOENN_TEST_CH10E + 0) >= 10
    h_setvar VAR_SOOTOPOLIS_STATE, 6
    TrainerCardAddBadge 7
    FlagSet 2421
    h_setflag FLAG_DEFEATED_SOOTOPOLIS_GYM
    h_settrainerflag TRAINER_WALLACE
    h_setflag FLAG_HIDE_SOOTOPOLIS_CITY_RESIDENTS
    h_setflag FLAG_HIDE_STEVEN_SOOTOPOLIS
    h_setflag FLAG_HIDE_WALLACE_SOOTOPOLIS
    h_clearflag FLAG_HIDE_SOOTOPOLIS_CITY_MAN_1
#endif
L_C10T_EmDone:
#endif
#endif
L_C10T_Done:
    VMReturn
#endif
#endif
