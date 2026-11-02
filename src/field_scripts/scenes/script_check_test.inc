// Test start for the script_check agent (test builds only: HOENN_TEST_CHSC=1 with HOENN_TEST_WARP=563,6,7; 2026-10-08).
// Littleroot's town sign (stand at (183,366) facing north) runs Test_SC_Setup, then the sign's test warp; tests overwrite the
// warp's constants and the stage constant SC_STAGE_SENTINEL below (0x5C01) in an APFS clone of the ROM
// (work/agents/script_check/tools/mo.py, the missing objects' method), so one build reaches every place and stage.
// The party is made HERE, by a normal script (as a playthrough gets its Pokémon), not by a zone init:
//  0x5C01  Lv 100 Tyranitar (lead) + Lv 100 Swampert              (the Room 9 crash with the ch10 test party's species)
//  0x5C02  Lv 100 Swampert (lead) + Lv 100 Tyranitar
//  0x5C03  Lv 100 Swampert + Lv 100 Manectric                      (no Sand Stream)
//  0x5C04  Lv 100 Tyranitar alone
//  0x5C05  chapter Ch5's start (HOENN_TEST_CH5: Mt. Chimney's scene next) + Lv 100 Swampert
//  0x5C06  chapter Ch13's start with the tickets (HOENN_TEST_CH13 / _EVENTS: the ferry, the event islands, Sky Pillar)
//  0x5C07  a Lv 2 Wurmple (to lose a battle: the blackout to the respawn point the new game set, the player's house)
//  0x5C08  the same, with Oldale's Pokémon Center as the respawn point (FieldSetTeleportZone 2 = RESPAWN_ZONE_INFO 1)
// Stages 1-4 add nothing else: HOENN_TEST_CH10=1 (Room 9's zone init: Test_Ch10Start) writes the chapter's flags and adds
// no Pokémon when the party is not empty. Never assembled into normal builds.
#ifdef HOENN_TEST_CHSC
#ifndef SCRIPT_CHECK_TEST_INC
#define SCRIPT_CHECK_TEST_INC
#define SC_STAGE 0x8004
Test_SC_Setup:
    h_setvar SC_STAGE, 0x5C01               // SC_STAGE_SENTINEL
    FlagSet 2401                            // FLAG_SYS_POKEMON_GET
    FlagSet 2403                            // FLAG_SYS_B_DASH
#ifdef HOENN_TEST_CHFOLLOW
    // the followers' test (notes/FOLLOWERS.md "Test"): every badge, the bike and the machines of Surf, Waterfall and Dive
    TrainerCardAddBadge 0
    TrainerCardAddBadge 1
    TrainerCardAddBadge 2
    TrainerCardAddBadge 3
    TrainerCardAddBadge 4
    TrainerCardAddBadge 5
    TrainerCardAddBadge 6
    TrainerCardAddBadge 7
    ItemAdd ITEM_MACH_BIKE, 1, HLIB_TMP
    ItemAdd ITEM_HM03, 1, HLIB_TMP
    ItemAdd ITEM_HM05, 1, HLIB_TMP
    ItemAdd ITEM_HM06, 1, HLIB_TMP
    ItemAdd ITEM_SUPER_ROD, 1, HLIB_TMP
    ItemAdd ITEM_OLD_ROD, 1, HLIB_TMP
    h_goto_if_eq SC_STAGE, 0x5C09, L_SC_FollowEgg
    h_goto_if_eq SC_STAGE, 0x5C0A, L_SC_FollowHuge
    h_goto_if_eq SC_STAGE, 0x5C0B, L_SC_FollowNoSprite
    VMJump L_SC_FollowEnd
L_SC_FollowEgg:                             // an Egg first: nobody follows
    h_getpartysize HLIB_TMP
    h_goto_if_ne HLIB_TMP, 0, L_SC_Done
    PokePartyAddEgg HLIB_TMP, SPECIES_MUDKIP, 0
    PokePartyAdd HLIB_TMP, SPECIES_SWAMPERT, 0, 100
    VMReturn
L_SC_FollowHuge:                            // Wailord (64 x 64): on the overworld only
    h_getpartysize HLIB_TMP
    h_goto_if_ne HLIB_TMP, 0, L_SC_Done
    PokePartyAdd HLIB_TMP, SPECIES_WAILORD, 0, 100
    PokePartyAdd HLIB_TMP, SPECIES_SWAMPERT, 0, 100
    VMReturn
L_SC_FollowNoSprite:                        // first a species with no walking sprite: the next one follows
    h_getpartysize HLIB_TMP
    h_goto_if_ne HLIB_TMP, 0, L_SC_Done
    PokePartyAdd HLIB_TMP, SPECIES_SNIVY, 0, 100
    PokePartyAdd HLIB_TMP, SPECIES_SWAMPERT, 0, 100
    VMReturn
L_SC_FollowEnd:
#endif
    h_goto_if_eq SC_STAGE, 0x5C05, L_SC_Ch5
    h_goto_if_eq SC_STAGE, 0x5C06, L_SC_Ch13
    h_goto_if_eq SC_STAGE, 0x5C07, L_SC_Weak
    h_goto_if_eq SC_STAGE, 0x5C08, L_SC_WeakCenter
    h_getpartysize HLIB_TMP
    h_goto_if_ne HLIB_TMP, 0, L_SC_Done
    h_goto_if_eq SC_STAGE, 0x5C02, L_SC_Party2
    h_goto_if_eq SC_STAGE, 0x5C03, L_SC_Party3
    PokePartyAdd HLIB_TMP, SPECIES_TYRANITAR, 0, 100
    h_goto_if_eq SC_STAGE, 0x5C04, L_SC_Done
    PokePartyAdd HLIB_TMP, SPECIES_SWAMPERT, 0, 100
    VMReturn
L_SC_Party2:
    PokePartyAdd HLIB_TMP, SPECIES_SWAMPERT, 0, 100
    PokePartyAdd HLIB_TMP, SPECIES_TYRANITAR, 0, 100
    VMReturn
L_SC_Party3:
    PokePartyAdd HLIB_TMP, SPECIES_SWAMPERT, 0, 100
    PokePartyAdd HLIB_TMP, SPECIES_MANECTRIC, 0, 100
    VMReturn
L_SC_WeakCenter:
    FieldSetTeleportZone 2
L_SC_Weak:
    PokePartyAdd HLIB_TMP, SPECIES_WURMPLE, 0, 2
    VMReturn
L_SC_Ch5:
#ifdef HOENN_TEST_CH5
    VMCall Test_Ch5Start
#endif
    VMReturn
L_SC_Ch13:
#ifdef HOENN_TEST_CH13
    VMCall Test_Ch13Start
    VMCall Test_Ch13Tickets
#endif
L_SC_Done:
    VMReturn
#ifdef HOENN_TEST_CH5
#include "scenes/ch5_test.inc"
#endif
#endif
#endif
