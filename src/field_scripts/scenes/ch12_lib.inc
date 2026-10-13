// Chapter Ch12's shared macros (ch6 agent, 2026-10-07): the Regi puzzle. Included by the rooms of the Sealed Chamber, Desert
// Ruins, Island Cave and Ancient Tomb (include guard: once per script file).
#ifndef CH12_LIB_INC
#define CH12_LIB_INC
#define CH12_TMP 0x8030                      /* = HLIB_TMP */
#define CH12_SLOT 0x8036                     /* party slot of the Pokémon that uses the move (6 = the machine in the Bag) */
#if defined(HOENN_TEST_CH12) && ((HOENN_TEST_CH12 + 0) >= 9)
#define CH12_DIG 182                          /* TEST ONLY: the test Swampert knows Protect, not Dig */
#else
#define CH12_DIG 91                           /* Dig */
#endif
#define CH12_BANG SEQ_SE_FLD_154             /* [guess] Sapphire SE_BANG / SE_DOOR: Black 2's dull rumble of its cave scenes */

// Sapphire opens a braille chamber when a field move is USED at one tile (party menu: Dig, Strength, Fly: pokeruby
// braille_puzzles.c). Black 2's party menu cannot be hooked per tile, so the tile is a step trigger that uses the move for
// you: hm_free's rule for field moves (a Pokémon that knows the move, or its machine in the Bag, after the badge; Dig has
// no badge and no HM: only a Pokémon that knows it). Jumps to `fail` when the player cannot use the move.
    .macro h_field_move_user machine, badge, move, fail
    TrainerCardHasBadge CH12_TMP, \badge
    WorkCmpConst CH12_TMP, 0
    VMJumpIf CMP_EQ, \fail
    PokePartyHasMoveAny CH12_SLOT, \move
    WorkCmpConst CH12_SLOT, 6
    VMJumpIf CMP_NE, .Lfmu\@
    ItemCheckAmount \machine, 1, CH12_TMP
    WorkCmpConst CH12_TMP, 0
    VMJumpIf CMP_EQ, \fail
.Lfmu\@:
    .endm
    .macro h_dig_user move, fail             // Dig: no badge, no machine
    PokePartyHasMoveAny CH12_SLOT, \move
    WorkCmpConst CH12_SLOT, 6
    VMJumpIf CMP_EQ, \fail
    .endm
    .macro h_move_user_name                  // word 0 = the Pokémon's nickname, or the player's name when only the machine is used
    WorkCmpConst CH12_SLOT, 6
    VMJumpIf CMP_EQ, .Lmun\@
    WordSetPartyPokeName 0, CH12_SLOT
    VMJump .Lmun2\@
.Lmun\@:
    WordSetPlayerName 0
.Lmun2\@:
    .endm

// a Regi (Sapphire: setwildbattle REGI 40, hide flag + FLAG_SYS_CTRL_OBJ_DELETE, ScrSpecial_StartRegiBattle): Black 2's
// legendary encounter (the cry, then a battle with the "legendary" flag as its own Latios/Latias/Volcarona scripts, 0304.s,
// 0364.s). The Regi's hide flag is set before the battle, as Sapphire, and the actor is gone afterwards.
    .macro h_regi_battle species, flag, uid
    h_lock
    SEPlay SEQ_SE_MESSAGE
    h_faceplayer
    h_waitse
    h_playmoncry \species
    h_delay 40
    h_waitmoncry
    FlagSet \flag
    CallWildBattle \species, 40, 1
    WildBattleIsVictory CH12_TMP
    WorkCmpConst CH12_TMP, 1
    VMJumpIf CMP_EQ, .Lrb\@
    CallWildLose
    VMHalt
.Lrb\@:
    ActorDelete \uid
    CallWildBattleEnd
    h_release
    .endm
#endif
