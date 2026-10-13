// Battle Tower test start (test builds only: HOENN_TEST_CHBT=<n>; battle_tower agent, 2026-10-08, notes/BATTLE_TOWER.md).
// Run once by the tower lobby's zone init (0042 BTL_Init) on top of HOENN_TEST_CH13's post-game state: three Lv 50
// Pokémon with all IVs 31 (Latios, Metagross, Salamence: none on Sapphire's banlist, three species, no items), so a Lv. 50
// challenge can be entered and won. HOENN_TEST_CHBT=2 also makes the first win of a challenge count as six (the Battle
// Room's L_BTB_Won runs Black 2's round + 1 five more times): the next battle is the seventh, for the prize and records.
// Uses flag 3042 (the first of Battle_tower's reserved flags) as its "done" mark. Never assembled into normal builds.
#ifdef HOENN_TEST_CHBT
#ifndef BATTLE_TOWER_TEST_INC
#define BATTLE_TOWER_TEST_INC
Test_BT_Party:
    h_goto_if_set 3042, L_BTT_Done
    h_setflag 3042
    PokePartyAdd HLIB_TMP, SPECIES_LATIOS, 0, 50
    PokePartyAdd HLIB_TMP, SPECIES_METAGROSS, 0, 50
    PokePartyAdd HLIB_TMP, SPECIES_SALAMENCE, 0, 50
    PokePartyGetCount BT_T1, 0
    WorkSetConst BT_T2, 0
L_BTT_Slot:
    WorkSetConst BT_T3, 0x46
L_BTT_IV:
    PokePartySetIV BT_T2, BT_T3, 31
    WorkAdd BT_T3, 1
    h_goto_if_lt BT_T3, 0x4c, L_BTT_IV
    WorkAdd BT_T2, 1
    VMStackPush BT_T2
    VMStackPush BT_T1
    VMStackCmp CMP_LT
    VMJumpIf CMP_STACK, L_BTT_Done
    VMJump L_BTT_Slot
L_BTT_Done:
    VMReturn
#endif
#endif
