// Test start for the missing objects (test builds only: HOENN_TEST_CHMO=1 with HOENN_TEST_WARP=563,6,7; missing_objects
// 2026-10-08). Littleroot's town sign (stand at (183,366) facing north) writes a start state once, then the sign's test
// warp runs; tests overwrite the warp's constants (b2tools/room_look.py) and the stage constant MO_STAGE_SENTINEL below
// (0x5A01) in an APFS clone of the ROM, so one build reaches every place and both stages:
//  stage 1 (0x5A01): before the submarine theft: the harbor scene armed (VAR_SLATEPORT_HARBOR_STATE 1, Capt. Stern,
//    Archie, the grunt and the submarine shown), the hideout B2F admin, grunts and submarine shown;
//  stage 6 (0x5A06): Birch rescued (Route 101 <-> Littleroot, the trucks' zone-change test);
//  stage 3 (0x5A03): berry trees 3 and 66 picked today (the next-day test: their zones' inits bring them back);
//  stage 4 (0x5A04) / 5 (0x5A05): Southern Island's stationary Lati@s shown / the Eon Ticket slab scene armed (final_check);
//  stage 2 (0x5A02): the game cleared: the S.S. Tidal docked in both harbors, Mr. Briney's boat at all three docks
//    (Sapphire shows one at a time; here all three for the test), May's Pichu doll.
// Both: a Lv 100 Swampert when the party is empty (the hideout battle). Never assembled into normal builds.
#ifdef HOENN_TEST_CHMO
#ifndef MISSING_OBJECTS_TEST_INC
#define MISSING_OBJECTS_TEST_INC
#define MO_STAGE 0x8004
Test_MO_Setup:
    h_setvar MO_STAGE, 0x5A01               // MO_STAGE_SENTINEL (tests write 0x5A02 for stage 2)
    PokePartyRecoverAll
    h_getpartysize HLIB_TMP
    h_goto_if_ne HLIB_TMP, 0, L_MO_Party
    PokePartyAdd HLIB_TMP, SPECIES_SWAMPERT, 0, 100
L_MO_Party:
    FlagSet 2401                            // FLAG_SYS_POKEMON_GET
    FlagSet 2403                            // FLAG_SYS_B_DASH
    TrainerCardAddBadge 4                   // Balance (Surf) and Mind (Dive) Badges + HM03 / HM06: the Seafloor dive test
    FlagSet 2418
    TrainerCardAddBadge 6
    FlagSet 2420
    ItemAdd 422, 1, HLIB_TMP
    ItemAdd 425, 1, HLIB_TMP
    h_goto_if_eq MO_STAGE, 0x5A02, L_MO_Stage2
    h_goto_if_eq MO_STAGE, 0x5A03, L_MO_Stage3
    h_goto_if_eq MO_STAGE, 0x5A06, L_MO_Stage6
    h_goto_if_eq MO_STAGE, 0x5A04, L_MO_Stage4
    h_goto_if_eq MO_STAGE, 0x5A05, L_MO_Stage5
    h_setvar VAR_SLATEPORT_HARBOR_STATE, 1
    h_clearflag FLAG_HIDE_SUBMARINE_SHADOW_SLATEPORT_HARBOR
    h_clearflag FLAG_HIDE_GRUNT_1_SLATEPORT_HARBOR
    h_clearflag FLAG_HIDE_GRUNT_2_SLATEPORT_HARBOR
    h_clearflag FLAG_HIDE_STERN_SLATEPORT_HARBOR
    h_setflag FLAG_HIDE_SS_TIDAL_SLATEPORT_HARBOR
    h_clearflag FLAG_HIDE_SUBMARINE_SHADOW_HIDEOUT
    h_clearflag FLAG_HIDE_GRUNTS_HIDEOUTS
    h_clearflag FLAG_EVIL_TEAM_ESCAPED_IN_SUBMARINE
    h_setflag FLAG_HIDE_MR_BRINEY_BOAT_ROUTE104     // (the field-heap comparison: Route 104 without the boat)
    h_clearflag FLAG_LEGEND_ESCAPED_SEAFLOOR_CAVERN // the submarine in Underwater_SeafloorCavern
    h_clearflag FLAG_HIDE_UNDERWATER_SUBMARINE_INTERACTION
    VMReturn
L_MO_Stage6:                                // after Birch's rescue (as postgame_test.inc): walk Route 101 <-> Littleroot freely
    h_setvar VAR_ROUTE101_STATE, 3
    h_setvar VAR_BIRCH_LAB_STATE, 5
    h_setvar VAR_LITTLEROOT_STATE, 4                // Littleroot's north-exit triggers (0x4054 = 0 / 1) off
    h_setflag FLAG_RESCUED_BIRCH
    h_setflag FLAG_HIDE_BIRCH_BATTLE_POOCHYENA
    h_setflag FLAG_HIDE_BIRCH_STARTERS_BAG
    VMReturn
L_MO_Stage3:                                // berry trees 3 (Route 104 (3,23)) and 66 (Route 123 (18,5)) picked today
    h_setflag FLAG_BERRY_TREE_PICKED_03
    h_setflag FLAG_BERRY_TREE_PICKED_66
    h_setflag FLAG_DAILY_BERRY_SPOTS
    WorkOr VAR_BERRY_PICKED_0, 4
    WorkOr VAR_BERRY_PICKED_4, 512
    VMReturn
L_MO_Stage4:                                // (final_check) Southern Island's stationary Lati@s shown where it waits
    h_clearflag FLAG_HIDE_LATIOS_OR_LATIAS_STATIONARY
    VMReturn
L_MO_Stage5:                                // (final_check) the Eon Ticket scene armed: read the slab (13,11) from (13,12)
    h_setflag FLAG_SYS_HAS_EON_TICKET
    h_clearflag FLAG_ENCOUNTERED_LATIAS_OR_LATIOS
    h_setflag FLAG_HIDE_LATIOS_OR_LATIAS_STATIONARY
    VMReturn
L_MO_Stage2:
    FlagSet FLAG_SYS_GAME_CLEAR
    h_setflag FLAG_HIDE_SUBMARINE_SHADOW_SLATEPORT_HARBOR
    h_setflag FLAG_HIDE_SUBMARINE_SHADOW_HIDEOUT
    h_clearflag FLAG_HIDE_SS_TIDAL_SLATEPORT_HARBOR
    h_clearflag FLAG_HIDE_SS_TIDAL_LILYCOVE_HARBOR
    h_clearflag FLAG_HIDE_MR_BRINEY_BOAT_ROUTE104
    h_clearflag FLAG_HIDE_MR_BRINEY_BOAT_DEWFORD
    h_clearflag FLAG_HIDE_MR_BRINEY_BOAT_ROUTE109
    h_clearflag FLAG_HIDE_MAY_PICHU_DOLL
    h_setflag FLAG_LEGEND_ESCAPED_SEAFLOOR_CAVERN   // the seafloor submarine gone (its zone init hides it)
    VMReturn
#endif
#endif
