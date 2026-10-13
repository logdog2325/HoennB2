// Porting library for Sapphire's story scripts (notes/STORY_PORTING.md). Macros named after Sapphire's commands
// (h_ + the Gen 3 name), each one a short sequence of Black 2 field-script commands (external/pokebw2/include/asm/
// field_script.inc) that Black 2's own scripts use the same way; movement actions under Sapphire's own names.
// Include after "asm/field_script.inc" and "hoenn.h". Emits no code by itself.
//
// Black 2 facts the macros rely on (tested 2026-10-06 unless marked):
// - Directions: 0 up, 1 down, 2 left, 3 right (Sapphire: 1 down, 2 up, 3 left, 4 right).
// - YesNoWin: 0 = YES, 1 = NO (Sapphire's VAR_RESULT: YES = 1).
// - WorkCmpConst + VMJumpIf CMP_xx jumps when the comparison is TRUE; VMStackCmp + VMJumpIf CMP_STACK jumps when it
//   is FALSE (ov012 scrcmd_vm.c:291-303).
// - ActorMsg / ParentActorMsg return when the text is printed: a line that does not end with a page break ({be01})
//   needs LastKeyWait before the window closes (Black 2 writes ActorMsg + MsgWinCloseAll only for lines ending {be01}).
// - The field runs at 30 fps: VMSleep n waits n field frames = 2n Gen 3 frames (movement probe, below).
// - ActorDelete does not set the NPC's spawn flag (Gen 3's removeobject does): h_removeobject sets it.
// - Script works 0x8000-0x8006 are shared with RTCallGlobal callees; the macros save the ones they use.
// - HLIB_TMP (0x8030) is the library's scratch work: don't keep values in it across a macro. HLIB_RESULT (0x8031)
//   holds h_giveitem's result.

#define HLIB_TMP 0x8030
#define HLIB_RESULT 0x8031      // result of h_giveitem (Sapphire's VAR_RESULT after giveitem)

// ---- script frame --------------------------------------------------------------------------------------------
    .macro h_lock                          // lock / lockall
    ActorsPauseAll
    .endm

    .macro h_release                       // release + end / releaseall + end (closes windows, unpauses, halts)
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt
    .endm

    .macro h_faceplayer                    // the talked-to NPC and the player face each other
    ActorSetEyeToEye
    .endm

// ---- messages: n = line of the zone's text file (src/text/script/NNNN_*.txt, 0-based) --------------------------
    .macro h_msgbox_npc n                  // a whole MSGBOX_NPC script: lock, faceplayer, message, wait, release
    ActorsPauseAll
    SEPlay SEQ_SE_MESSAGE
    ActorSetEyeToEye
    ParentActorMsg MSGFILE_SCRIPT, \n, 0, 0
    LastKeyWait
    ActorMsgClose
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt
    .endm

    .macro h_msgbox_sign n                 // a whole MSGBOX_SIGN script (signpost window)
    ActorsPauseAll
    SEPlay SEQ_SE_MESSAGE
    MsgPlaceSign \n, 2
    MsgPlaceSignClose
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt
    .endm

    .macro h_msgbox n                      // MSGBOX_DEFAULT said by the NPC the player talked to; window stays open
    ParentActorMsg MSGFILE_SCRIPT, \n, 0, 0
    LastKeyWait
    .endm

    .macro h_msgbox_actor n, actor         // MSGBOX_DEFAULT said by an actor (its uid; 255 = the player)
    ActorMsg MSGFILE_SCRIPT, \n, \actor, 0, 0
    LastKeyWait
    .endm

    .macro h_msgbox_info n                 // a line nobody says (TV, "<player> received ...", signs read as objects)
    SystemMsg \n, 2
    LastKeyWait
    .endm

    .macro h_msgbox_autoclose n            // MSGBOX_AUTOCLOSE (NPC talked to)
    ParentActorMsg MSGFILE_SCRIPT, \n, 0, 0
    LastKeyWait
    MsgWinCloseAll
    .endm

    .macro h_closemessage
    MsgWinCloseAll
    .endm

    .macro h_yesno n, var                  // MSGBOX_YESNO (talked-to NPC): var = 0 YES, 1 NO
    ParentActorMsg MSGFILE_SCRIPT, \n, 0, 0
    YesNoWin \var
    .endm

    .macro h_yesno_actor n, actor, var     // MSGBOX_YESNO said by an actor
    ActorMsg MSGFILE_SCRIPT, \n, \actor, 0, 0
    YesNoWin \var
    .endm

    .macro h_msgbox_gendered nboy, ngirl, actor   // one line for a boy, another for a girl (Black 2's own way to
    ActorMsgGendered MSGFILE_SCRIPT, \nboy, \ngirl, \actor, 0, 0   // write {RIVAL}: the May line / the Brendan line)
    LastKeyWait
    .endm

    .macro h_goto_if_yes var, label
    WorkCmpConst \var, 0
    VMJumpIf CMP_EQ, \label
    .endm

    .macro h_goto_if_no var, label
    WorkCmpConst \var, 1
    VMJumpIf CMP_EQ, \label
    .endm

// word buffers: Sapphire {PLAYER} = {0100:0}, {STR_VAR_n} = {0100:n}, {RIVAL} = {0100:4} (converter/gen3text.py expand)
    .macro h_buffer_player
    WordSetPlayerName 0
    .endm
    .macro h_bufferspeciesname n, species  // bufferspeciesname STR_VAR_n
    WordSetPokeSpecies \n, \species
    .endm
    .macro h_bufferitemname n, item
    WordSetItemName \n, \item
    .endm
    .macro h_buffer_rival                  // {RIVAL}: the save's rival name (the new game must store May/Brendan)
    WordSetLoadRivalName 4
    .endm

// ---- flags, vars, conditions ---------------------------------------------------------------------------------
    .macro h_setflag flag
    FlagSet \flag
    .endm
    .macro h_clearflag flag
    FlagReset \flag
    .endm
    .macro h_setvar var, value
    WorkSetConst \var, \value
    .endm
    .macro h_addvar var, value
    WorkAdd \var, \value
    .endm
    .macro h_subvar var, value
    WorkSub \var, \value
    .endm
    .macro h_copyvar dst, src
    WorkSet \dst, \src
    .endm

    .macro h_goto_if_set flag, label       // VMStackCmp result FALSE -> CMP_STACK jumps: test "flag != 1"
    VMStackPushFlag \flag
    VMStackPushConst 1
    VMStackCmp CMP_NE
    VMJumpIf CMP_STACK, \label
    .endm
    .macro h_goto_if_unset flag, label
    VMStackPushFlag \flag
    VMStackPushConst 1
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, \label
    .endm
    .macro h_call_if_set flag, label
    h_goto_if_unset \flag, .Lhskip\@
    VMCall \label
.Lhskip\@:
    .endm
    .macro h_call_if_unset flag, label
    h_goto_if_set \flag, .Lhskip\@
    VMCall \label
.Lhskip\@:
    .endm

    // var (work) against a number: compare + goto_if_xx in one (jumps when TRUE)
    .macro h_goto_if_eq var, value, label
    WorkCmpConst \var, \value
    VMJumpIf CMP_EQ, \label
    .endm
    .macro h_goto_if_ne var, value, label
    WorkCmpConst \var, \value
    VMJumpIf CMP_NE, \label
    .endm
    .macro h_goto_if_lt var, value, label
    WorkCmpConst \var, \value
    VMJumpIf CMP_LT, \label
    .endm
    .macro h_goto_if_le var, value, label
    WorkCmpConst \var, \value
    VMJumpIf CMP_LE, \label
    .endm
    .macro h_goto_if_gt var, value, label
    WorkCmpConst \var, \value
    VMJumpIf CMP_GT, \label
    .endm
    .macro h_goto_if_ge var, value, label
    WorkCmpConst \var, \value
    VMJumpIf CMP_GE, \label
    .endm
    .macro h_call_if_eq var, value, label
    h_goto_if_ne \var, \value, .Lhskip\@
    VMCall \label
.Lhskip\@:
    .endm
    .macro h_call_if_ne var, value, label
    h_goto_if_eq \var, \value, .Lhskip\@
    VMCall \label
.Lhskip\@:
    .endm
    .macro h_goto_if_eq_var var, var2, label   // var against var
    WorkCmpWork \var, \var2
    VMJumpIf CMP_EQ, \label
    .endm

    .macro h_checkplayergender var         // 0 boy, 1 girl (same values as Sapphire)
    TrainerCardGetSex \var
    .endm
    .macro h_goto_if_girl label
    TrainerCardGetSex HLIB_TMP
    WorkCmpConst HLIB_TMP, 1
    VMJumpIf CMP_EQ, \label
    .endm
    .macro h_goto_if_boy label
    TrainerCardGetSex HLIB_TMP
    WorkCmpConst HLIB_TMP, 0
    VMJumpIf CMP_EQ, \label
    .endm
    .macro h_getplayerfacing var           // Black 2 directions (0 up, 1 down, 2 left, 3 right), no VAR_FACING
    PlayerGetDir \var
    .endm
    .macro h_random var, n
    Random \var, \n
    .endm

// ---- objects ---------------------------------------------------------------------------------------------------
    .macro h_applymovement actor, list     // actor uid; 255 = the player
    ActorCmdExec \actor, \list
    .endm
    .macro h_waitmovement                  // waits for every actor's list
    ActorCmdWait
    .endm
    .macro h_move actor, code, count=1     // one action without a separate list (inline, word-aligned)
    ActorCmdExec \actor, .Lhmv\@
    ActorCmdWait
    VMJump .Lhend\@
    .balign 4, 0
.Lhmv\@:
    Move \code, \count
    MoveEnd
.Lhend\@:
    .endm
    .macro h_turnobject actor, dir         // dir: 0 up, 1 down, 2 left, 3 right
    h_move \actor, \dir, 1
    .endm
    .macro h_addobject uid, flag           // addobject: spawn flag cleared, actor added
    FlagReset \flag
    ActorAdd \uid
    .endm
    .macro h_removeobject uid, flag        // removeobject: actor removed, spawn flag set
    ActorDelete \uid
    FlagSet \flag
    .endm
    .macro h_setobjectxyperm index, x, z, dir  // zone-init only; index = position in the zone's NPC list, not uid
    ObjInitNPCGPos \index, \dir, \x, 0, \z
    .endm

// ---- ribbons (user decision 2026-10-07: really given) --------------------------------------------------------------
// Black 2's fields of the Hoenn ribbons (PKM_PARAM 0x4d-0x6c). Giving any of them and reading the five Sapphire's
// scripts use needs the story patch's ov012 change (b2tools/patches/story.py ribbon_commands; on with
// HOENN_STORY_CODE=1 until the lead's savestate remake, then always): without it the macros do nothing / read 0.
#define RIBBON_CHAMPION 0x61                   /* Hall of Fame (Sapphire CHAMPION_RIBBON) */
#define RIBBON_WINNING 0x62                    /* Battle Tower */
#define RIBBON_VICTORY 0x63                    /* Battle Tower */
#define RIBBON_ARTIST 0x64                     /* Lilycove Contest Hall (contests: S_optional) */
#define RIBBON_EFFORT 0x65                     /* Slateport */
#define RIBBON_CONTEST(category, rank) (0x4d + 4 * (category) + (rank))   /* cool, beauty, cute, smart, tough; 0-3 */
    .macro h_get_lead_mon var                  // GetLeadMonIndex: the first party slot that is not an Egg
    WorkSetConst \var, 0
.Lhlm\@:
    PokePartyIsEgg HLIB_TMP, \var
    WorkCmpConst HLIB_TMP, 0
    VMJumpIf CMP_EQ, .Lhlm2\@
    WorkAdd \var, 1
    VMJump .Lhlm\@
.Lhlm2\@:
    .endm
    .macro h_give_ribbon slot, ribbon          // SetMonData(..., MON_DATA_*_RIBBON, TRUE): slot = number or work
    PokePartySetIV \slot, \ribbon, 1           // (Black 2's PokePartySetIV, widened to the ribbon fields)
    .endm
    .macro h_check_ribbon var, slot, ribbon    // var = 1 if that Pokémon has it (RIBBON_CHAMPION ... RIBBON_EFFORT)
    PokePartyGetParam \var, \slot, \ribbon
    .endm

// ---- items, Pokémon, money -------------------------------------------------------------------------------------
    .macro h_giveitem item, count=1        // giveitem: Black 2's Std_ObtainItem (global 2805, file 1238 Script_6:
    ItemCheckSpace \item, \count, HLIB_RESULT   // pocket jingle, "obtained" + pocket text). HLIB_RESULT = 1 given,
    WorkCmpConst HLIB_RESULT, 0            // 0 Bag full: then nothing is shown, as Sapphire's giveitem (the caller
    VMJumpIf CMP_EQ, .Lhgi\@               // says Sapphire's "Too bad! The Bag is full...": h_bag_is_full)
    VMStackPush 0x8000                     // (checked before the call: 2805 overwrites 0x8010 itself, tested 2026-10-06)
    VMStackPush 0x8001
    WorkSetConst 0x8000, \item
    WorkSetConst 0x8001, \count
    RTCallGlobal 2805
    VMStackPop 0x8001
    VMStackPop 0x8000
.Lhgi\@:
    .endm
    .macro h_give_pokenav                  // Mr. Stone's PokéNav = Black 2's Xtransceiver (user decision 2026-10-06),
    TrainerCardGetSex HLIB_TMP             // the boy's or the girl's one, renamed "PokéNav" (gen_key_items.py); then
    WorkCmpConst HLIB_TMP, 0               // h_setflag FLAG_RECEIVED_POKENAV as Sapphire. Needs hoenn_key_items.h.
    VMJumpIf CMP_NE, .Lhpn\@
    h_giveitem ITEM_POKENAV, 1
    VMJump .Lhpn2\@
.Lhpn\@:
    h_giveitem ITEM_POKENAV_FEMALE, 1
.Lhpn2\@:
    .endm
    .macro h_bag_is_full n                 // Common_EventScript_ShowBagIsFull without its release (Text_TooBadBagIsFull
    ParentActorMsg MSGFILE_SCRIPT, \n, 0, 0     // "Too bad!\nThe Bag is full..." in your text file): the NPC says it
    LastKeyWait
    MsgWinCloseAll
    .endm
    .macro h_handover_item item, n         // Common_EventScript_PlayerHandedOverTheItem: n = Sapphire's "{PLAYER} handed
    WordSetPlayerName 0                    // over the\n{STR_VAR_1}." ({0100:0} ... {0100:1}); TM jingle, line, item
    WordSetItemName 1, \item               // taken out of the Bag
    MEPlay SEQ_ME_WAZA                     // MUS_OBTAIN_TMHM
    SystemMsg \n, 2
    MEWait
    LastKeyWait
    InfoMsgClose
    ItemSub \item, 1, HLIB_TMP
    .endm
    .macro h_checkitemspace item, count, var   // var = 1 when it fits
    ItemCheckSpace \item, \count, \var
    .endm
    .macro h_checkitem item, count, var        // var = 1 when the bag has it
    ItemCheckAmount \item, \count, \var
    .endm
    .macro h_removeitem item, count, var
    ItemSub \item, \count, \var
    .endm
    .macro h_givemon species, level, var       // givemon (Poké Ball, no item); var = result
    PokePartyAdd \var, \species, 0, \level
    .endm
    .macro h_getpartysize var
    PokePartyGetCount \var, 0
    .endm
    .macro h_heal                              // special HealPlayerParty
    PokePartyRecoverAll
    .endm
    .macro h_heal_party_fade                   // Common_EventScript_OutOfCenterPartyHeal: fade to black, heal jingle,
    FadeEx 3, 0, 16, 2                         // heal, fade back (Black 2's own out-of-center heal, 0522.s:47-53)
    FadeExWait
    PokePartyRecoverAll
    MEPlay SEQ_ME_ASA                          // MUS_HEAL
    MEWait
    FadeEx 3, 16, 0, 2
    FadeExWait
    .endm
    .macro h_name_received_mon slot            // Common_EventScript_NameReceivedPartyMon (special ChangePokemonNickname
    MsgWinCloseAll                             // with VAR_0x8004 = slot): Black 2's nickname screen for party slot
    FadeOutBlackQ                              // `slot` (a number or a work: givemon's slot is party size - 1)
    FadeWait
    CallPokeNameInput HLIB_TMP, \slot, 0
    FadeInBlackQ
    FadeWait
    .endm
    .macro h_static_battle species, level, flag, uid   // static_pokemon.inc (Kecleon, Electrode): setwildbattle +
    FlagSet \flag                               // set the object's hide flag + dowildbattle; the object is gone after
    CallWildBattle \species, \level, 0          // the battle whatever happened (FLAG_SYS_CTRL_OBJ_DELETE). Lost:
    WildBattleIsVictory HLIB_TMP                // whiteout. HLIB_RESULT = Black 2's result (0 caught, 1/2 fainted or
    WorkCmpConst HLIB_TMP, 1                    // fled: 0364.s Volcarona)
    VMJumpIf CMP_EQ, .Lhsb\@
    CallWildLose
    VMHalt
.Lhsb\@:
    ActorDelete \uid
    CallWildBattleEnd
    WildBattleGetResult HLIB_RESULT
    .endm

    .macro h_obtain_pokedex n              // "<player> received the Pokédex!" as Black 2 gives it (0854.s:438-456):
    MEPlay SEQ_ME_KEYITEM                  // key-item jingle, field effect 63 (boy) / 64 (girl) = the Pokédex
    TrainerCardGetSex HLIB_TMP             // shown over the player (tested), the line in an info window
    WorkCmpConst HLIB_TMP, 0
    VMJumpIf CMP_EQ, .Lhboy\@
    PlayFieldEffect 64
    VMJump .Lhpose\@
.Lhboy\@:
    PlayFieldEffect 63
.Lhpose\@:
    WordSetPlayerName 0
    SystemMsg \n, 1
    MEWait
    MsgWaitAdvance
    InfoMsgClose
    .endm

// The rival's overworld sprite (Sapphire Common_EventScript_SetupRivalGfxId): an NPC with object code 162 shows the
// code stored in work 0x4020 (GetWKOBJCODENPCOBJCODE: code + 0x3F7E); run this in the zone-init map script.
// Boy -> rival May (object code 4), girl -> rival Brendan (1) (src/sprites/overworld/001-, 004-).
#define RIVAL_GFX 162
    .macro h_setup_rival_gfx
    TrainerCardGetSex HLIB_TMP
    WorkSetConst 0x4020, 4
    WorkCmpConst HLIB_TMP, 0
    VMJumpIf CMP_EQ, .Lhrg\@
    WorkSetConst 0x4020, 1
.Lhrg\@:
    .endm
    .macro h_setup_rival_bike_gfx              // SetupRivalOnBikeGfxId: no Brendan/May bike sprites yet (sprites
    h_setup_rival_gfx                          // agents), so the walking rival for now (notes/STORY_COMMON.md)
    .endm

// ---- trainers (ids: src/include/hoenn_trainers.h, Sapphire's TRAINER_* names) ------------------------------------
    // trainerbattle_no_intro / a scripted battle: the defeat line is the trainer's in-battle line (type 1). Lost:
    // Black 2 whites out (the script ends). Won: the trainer's flag is set (as Sapphire's SetTrainerFlag).
    .macro h_trainerbattle id
    CallTrainerBattle \id, 0, 0
    TrainerBattleIsVictory HLIB_TMP
    WorkCmpConst HLIB_TMP, 1
    VMJumpIf CMP_EQ, .Lhwon\@
    CallTrainerLose
    VMHalt
.Lhwon\@:
    CallTrainerBattleEnd
    TrainerFlagSet \id
    .endm
    .macro h_trainerbattle_continue id, var    // battle that goes on after a loss (Black 2's first rival battle:
    CallTrainerBattle \id, 0, 1                // flags 1); var = 1 won, 0 lost; trainer flag set either way
    CallTrainerBattleEnd
    TrainerBattleIsVictory \var
    TrainerFlagSet \id
    .endm
    .macro h_trainerbattle_two id1, id2       // Sapphire's trainerbattle_double against two people (Tate & Liza:
    CallTrainerBattle \id1, \id2, 0            // TRAINER_TATE, TRAINER_LIZA): Black 2's battle against two trainers
    TrainerBattleIsVictory HLIB_TMP            // (global 1239 L_124E; both single-style -> BtlSetup_SetTrainer1v2).
    WorkCmpConst HLIB_TMP, 1                   // Music and encounter effect: id1's class. Each says its defeat line.
    VMJumpIf CMP_EQ, .Lhwon2\@
    CallTrainerLose
    VMHalt
.Lhwon2\@:
    CallTrainerBattleEnd
    TrainerFlagSet \id1
    TrainerFlagSet \id2
    .endm
    .macro h_goto_if_cannot_double label      // fewer than two Pokémon able to battle (Sapphire's trainerbattle_double
    PokePartyGetCount HLIB_TMP, 2              // check, GetMonsStateToDoubles): show the "need two" line (type 6)
    WorkCmpConst HLIB_TMP, 2
    VMJumpIf CMP_LT, \label
    .endm
    .macro h_trainer_intro id, actor           // the trainer's eye-contact music + its intro line (type 0)
    TrainerBGMPlayPush \id
    TrainerSayMessage \id, 0, \actor
    ActorMsgClose
    .endm
    .macro h_goto_if_defeated id, label
    TrainerFlagGet \id, HLIB_TMP
    WorkCmpConst HLIB_TMP, 1
    VMJumpIf CMP_EQ, \label
    .endm
    .macro h_goto_if_not_defeated id, label
    TrainerFlagGet \id, HLIB_TMP
    WorkCmpConst HLIB_TMP, 0
    VMJumpIf CMP_EQ, \label
    .endm
    .macro h_settrainerflag id
    TrainerFlagSet \id
    .endm

// ---- gyms and badges ---------------------------------------------------------------------------------------------
// Badges are Black 2's trainer-card badges (no flags): Sapphire FLAG_BADGEnn_GET = badge nn - 1. hm_free reads them.
    .macro h_givebadge n                       // setflag FLAG_BADGE0n_GET, as Black 2's gyms give one (0126.s:246-249):
    TrainerCardSaveGymVictoryParty (\n - 1)    // the winning party for the trainer card, the badge, and Black 2's
    TrainerCardAddBadge (\n - 1)               // per-badge system flag 2414+ (set by every Black 2 gym)
    FlagSet (2413 + \n)
    .endm
    .macro h_goto_if_badge n, label            // goto_if_set FLAG_BADGE0n_GET
    TrainerCardHasBadge HLIB_TMP, (\n - 1)
    WorkCmpConst HLIB_TMP, 1
    VMJumpIf CMP_EQ, \label
    .endm
    .macro h_goto_if_no_badge n, label         // goto_if_unset FLAG_BADGE0n_GET
    TrainerCardHasBadge HLIB_TMP, (\n - 1)
    WorkCmpConst HLIB_TMP, 0
    VMJumpIf CMP_EQ, \label
    .endm
    .macro h_badge_fanfare                     // Common_EventScript_PlayGymBadgeFanfare (MUS_OBTAIN_BADGE). Black 2
    MEPlay SEQ_ME_BADGE                        // also shows its badge art over the player (field effects 2-10 /
    MEWait                                     // 55-62): Unova's badges, so left out
    .endm
    .macro h_set_gym_trainers gym              // Common_EventScript_SetGymTrainers (VAR_0x8008 = gym): the gym's
// >>> emerald_rooms gym_trainers (b2tools/emerald_rooms.py / emerald_gyms.py write this block on every run: edit the generator)
#ifdef HOENN_EMERALD
    .if 0
    .elseif \gym == 1
    TrainerFlagSet 320                     // TRAINER_MARC (Emerald only)
    .elseif \gym == 2
    TrainerFlagSet 321                     // TRAINER_BRENDEN (Emerald only)
    TrainerFlagSet 326                     // TRAINER_LILITH (Emerald only)
    TrainerFlagSet 327                     // TRAINER_CRISTIAN (Emerald only)
    .elseif \gym == 3
    TrainerFlagSet 605                     // TRAINER_ANGELO (Emerald only)
    .elseif \gym == 4
    TrainerFlagSet 188                     // TRAINER_JEFF (Emerald only)
    TrainerFlagSet 189                     // TRAINER_JACE (Emerald only)
    TrainerFlagSet 260                     // TRAINER_ELI (Emerald only)
    .elseif \gym == 6
    TrainerFlagSet 215                     // TRAINER_HUMBERTO (Emerald only)
    TrainerFlagSet 606                     // TRAINER_DARIUS (Emerald only)
    .elseif \gym == 7
    TrainerFlagSet 328                     // TRAINER_SYLVIA (Emerald only)
    TrainerFlagSet 347                     // TRAINER_NATE (Emerald only)
    TrainerFlagSet 348                     // TRAINER_KATHLEEN (Emerald only)
    TrainerFlagSet 349                     // TRAINER_CLIFFORD (Emerald only)
    TrainerFlagSet 350                     // TRAINER_NICHOLAS (Emerald only)
    TrainerFlagSet 370                     // TRAINER_MACEY (Emerald only)
    .elseif \gym == 8
    TrainerFlagSet 159                     // TRAINER_DAPHNE (Emerald only)
    TrainerFlagSet 261                     // TRAINER_ANNIKA (Emerald only)
    .endif
#endif
// <<< emerald_rooms gym_trainers
    .if \gym == 1                              // trainers count as beaten once its leader is (set_gym_trainers.inc)
    TrainerFlagSet TRAINER_JOSH
    TrainerFlagSet TRAINER_TOMMY
    .elseif \gym == 2
    TrainerFlagSet TRAINER_HIDEKI
    TrainerFlagSet TRAINER_TESSA
    TrainerFlagSet TRAINER_LAURA
    .elseif \gym == 3
    TrainerFlagSet TRAINER_KIRK
    TrainerFlagSet TRAINER_SHAWN
    TrainerFlagSet TRAINER_BEN
    TrainerFlagSet TRAINER_VIVIAN
    .elseif \gym == 4
    TrainerFlagSet TRAINER_COLE
    TrainerFlagSet TRAINER_AXLE
    TrainerFlagSet TRAINER_ANDY
    TrainerFlagSet TRAINER_ZANE
    TrainerFlagSet TRAINER_SADIE
    .elseif \gym == 5
    TrainerFlagSet TRAINER_RANDALL
    TrainerFlagSet TRAINER_PARKER
    TrainerFlagSet TRAINER_GEORGE
    TrainerFlagSet TRAINER_BERKE
    TrainerFlagSet TRAINER_MARY
    TrainerFlagSet TRAINER_LORI
    TrainerFlagSet TRAINER_JODY
    .elseif \gym == 6
    TrainerFlagSet TRAINER_JARED
    TrainerFlagSet TRAINER_TERRELL
    TrainerFlagSet TRAINER_KYLEE
    TrainerFlagSet TRAINER_WILL
    .elseif \gym == 7
    TrainerFlagSet TRAINER_PRESTON
    TrainerFlagSet TRAINER_VIRGIL
    TrainerFlagSet TRAINER_FRITZ
    TrainerFlagSet TRAINER_HANNAH
    TrainerFlagSet TRAINER_SAMANTHA
    TrainerFlagSet TRAINER_MAURA
    .elseif \gym == 8
    TrainerFlagSet TRAINER_ANDREA
    TrainerFlagSet TRAINER_CRISSY
    TrainerFlagSet TRAINER_BRIANNA_2
    TrainerFlagSet TRAINER_CONNIE
    TrainerFlagSet TRAINER_BRIDGET
    TrainerFlagSet TRAINER_OLIVIA
    TrainerFlagSet TRAINER_TIFFANY
    TrainerFlagSet TRAINER_MARISSA
    .else
    .error "h_set_gym_trainers: gym 1-8"
    .endif
    .endm

// ---- sound -----------------------------------------------------------------------------------------------------
    .macro h_playse se
    SEPlay \se
    .endm
    .macro h_waitse
    SEWait
    .endm
    .macro h_playfanfare me
    MEPlay \me
    .endm
    .macro h_waitfanfare
    MEWait
    .endm
    .macro h_playbgm bgm
    BGMPlay \bgm
    .endm
    .macro h_fadedefaultbgm                    // back to the zone's music (also ends a playbgm scene)
    BGMChangeMap
    .endm
    .macro h_playmoncry species
    PVPlay \species, 0
    .endm
    .macro h_waitmoncry
    PVWait
    .endm
// Sapphire sound names -> Black 2 (notes/STORY_SPECIALS.md table 3; [guess] = picked by name/situation, audition)
#define SE_EXIT SEQ_SE_KAIDAN                    /* door/stairs exit (B2 uses it 100x) */
#define SE_LEDGE SEQ_SE_DANSA                    /* [guess] */
#define SE_PC_LOGIN SEQ_SE_PC_LOGIN
#define SE_PC_ON SEQ_SE_PC_ON                    /* [guess] */
#define SE_PC_OFF SEQ_SE_PC_LOGOFF               /* [guess] */
#define SE_SELECT SEQ_SE_DECIDE1
#define SE_SHOP SEQ_SE_SYS_22
#define MUS_OBTAIN_ITEM SEQ_ME_ITEM              /* MEPlay: item received (giveitem picks it by pocket) */
#define MUS_OBTAIN_TMHM SEQ_ME_WAZA
#define MUS_OBTAIN_BADGE SEQ_ME_BADGE
#define MUS_HEAL SEQ_ME_ASA
#define MUS_LEVEL_UP SEQ_ME_LVUP
#define MUS_EVIL_TEAM SEQ_BGM_E_PLASMA           /* Team Aqua appears */
#define MUS_FOLLOW_ME SEQ_BGM_E_TSURETEKE2       /* "follow me" (Wye leading the player) */
#include "hoenn_music.inc"
#define MUS_ENCOUNTER_MAY MUS_HOENN_ENCOUNTER_MAY          /* Sapphire's; Unova music: Black 2's rival Hugh (E_HUE) */
#define MUS_ENCOUNTER_BRENDAN MUS_HOENN_ENCOUNTER_BRENDAN  /* Sapphire's; Unova music: E_HUE */
#define MUS_ENCOUNTER_CHAMPION SEQ_BGM_E_CHAMPION
#define MUS_SAILING MUS_HOENN_SAILING            /* Mr. Briney's boat: Sapphire's; Unova music: Black 2's surfing theme */
    .macro h_play_briney_boat_music            // Common_EventScript_PlayBrineysBoatMusic (Sapphire also sets
    BGMPlay MUS_SAILING                        // FLAG_DONT_TRANSITION_MUSIC so warps keep it: the boat scene's
    .endm                                      // chapter (Ch2) plays it again after each warp if needed)
    .macro h_stop_briney_boat_music            // Common_EventScript_StopBrineysBoatMusic
    BGMChangeMap
    .endm

// ---- boat and ship trips: Black 2's 3D boat cutscenes (src/field_scripts/common/boat.inc has the research) -------
// After the boarding (the player hidden): the music, the screen fades out, Black 2's boat demo plays, then the map
// changes and the destination's arrival script `script` runs on the black screen (begin it with FadeInBlack +
// FadeWait: ch2_land). zone, x, z, dir = MapChangeCore's (dir 0 up 1 down 2 left 3 right).
#include "common/boat.inc"
    .macro h_sail_briney zone, x, z, dir, script   // Mr. Briney's boat (Route 104, Dewford, Route 109): a small
    h_play_briney_boat_music                       // motorboat speeds off on the open sea (needs the boat_demos
                                                   // patch), Sapphire's boat music (stand-in)
    boat_trip BOAT_DEMO_BRINEY, 0, \zone, \x, \z, \dir, \script
    .endm
    .macro h_sail_ferry zone, x, z, dir, script    // the S.S. Tidal and every other ferry (Battle Tower island,
    boat_trip BOAT_DEMO_FERRY, 1, \zone, \x, \z, \dir, \script   // Southern Island, the event islands): Black 2's
    .endm                                          // ferry on the open sea with its own ship music
    .macro h_ride_cable_car zone, x, z, dir, script    // the cable car between its two stations (Black 2 has none:
    cable_car_ride \zone, \x, \z, \dir, \script       // a black screen with the elevator hum, common/boat.inc)
    .endm

// ---- warps, screen, time ---------------------------------------------------------------------------------------
    .macro h_warpsilent zone, x, z, dir        // fade + map change (dir 0 up 1 down 2 left 3 right)
    FadeOutBlack
    FadeWait
    MapChangeCore \zone, \x, 0, \z, \dir
    .endm
    .macro h_warp_scene zone, x, z, dir, script    // ... and run that zone's script on arrival (it starts on a black
    FadeOutBlack                                   // screen: begin it with FadeInBlack + FadeWait)
    RTReserveScript \script
    FadeWait
    MapChangeCore \zone, \x, 0, \z, \dir
    .endm
    .macro h_warp_arrive zone, x, z, dir, y=0  // a scripted warp after which the arrival zone works (people talk, trainers
    FadeOutBlack                               // see you): Black 2's pattern, the global arrival script 10017 fades in
    RTReserveScript 10017                      // (hm_free.py Script_18). Follow it with FinishAllEvents, ActorsUnpauseAll,
    FadeWait                                   // VMHalt. (y: MapChangeCore's height in 16-unit steps; the player lands on
    MapChangeCore \zone, \x, \y, \z, \dir      // the ground below anyway: story_finish)
    .endm
    .macro h_setrespawn n                     // n = 1-based RESPAWN_ZONE_INFO entry (1 = the player's house)
    FieldSetTeleportZone \n
    .endm
// Zone hold (zone_edges, 2026-10-08): every map has its own zone up to its edges (b2tools/world.py zone_rects), and
// Black 2 swaps zone as soon as the player's position is in another zone, also while a script moves the player: the swap
// deletes every actor of the scene and loads the other zone's (ov036 Field_SwapZoneByMatrix). A scene that walks the
// player over a map edge inside one 32x32 cell (Wally's tutorial: Petalburg -> Route 102) sets h_zone_hold first: while
// map-local flag 0x60 is set the zone lookup gives every position its cell's zone (b2tools/patches/hoenn_world.py
// ZONE_HOLD_FLAG). Every zone change clears flags 0-0x63, so a warp ends it; h_zone_release ends it in place (the swap
// then comes with the player's next step).
#define FLAG_ZONE_HOLD 0x60
    .macro h_zone_hold
    FlagSet FLAG_ZONE_HOLD
    .endm
    .macro h_zone_release
    FlagReset FLAG_ZONE_HOLD
    .endm
// Place-name banner through a zone-entry scene (fixes_v151, 2026-10-08): Black 2 closes the banner whenever the field
// starts any script event (ov036 FieldEventProvider_Grid), so a scene condition that runs on every zone entry (ch7's
// invisible Kecleons) closed it before it showed, also after Fly. While map-local flag 0x61 is set the field leaves the
// banner alone (b2tools/patches/zone_effects.py keep_banner). h_keep_banner in the zone init (MapScript 2: it runs on
// every entry, walking or warping, and every zone change clears flags 0-0x63), h_keep_banner_end first thing in the entry
// scene: every other script then closes the banner as in Black 2.
#define FLAG_KEEP_BANNER 0x61
    .macro h_keep_banner
    FlagSet FLAG_KEEP_BANNER
    .endm
    .macro h_keep_banner_end
    FlagReset FLAG_KEEP_BANNER
    .endm
    .macro h_fadescreen_black                  // fadescreen FADE_TO_BLACK
    FadeOutBlack
    FadeWait
    .endm
    .macro h_fadescreen_from_black
    FadeInBlack
    FadeWait
    .endm
    .macro h_delay frames                      // delay N (Gen 3 frames at 60 fps)
    VMSleep ((\frames) + 1) / 2
    .endm

// ---- darkness: Sapphire's setflashradius / animateflash (Dewford Gym; b2tools/patches/zone_effects.py) -----------
// Command 0x1c9 (Black 2's unused NDemoStart, rewritten): the dark circle's scale in 1/256 (Black 2's dark cave = 768,
// its Flash = 2720; 0 = no darkness), at once (frames 0) or grown over `frames` field frames (30 a second); both may
// be works. A room needs no a/1/4/9 entry: the first nonzero call creates the darkness. Needs the field: MapScript 3/4
// (field load) or a normal script, never a zone init (MapScript 2). FLASH_PX: Sapphire's radius in pixels -> scale.
#define FLASH_PX(px) ((px) * 32)
    .macro h_flash_scale scale, frames=0
    FieldCommand 0x1c9
    .2byte \scale
    .2byte \frames
    .endm
    .macro h_wait_work work, unit=1            // wait `work` x `unit` field frames (counts `work` down to 0; one
.Lhww\@:                                       // VMSleep per unit: a unit of 1 costs about 3 frames a round)
    WorkCmpConst \work, 0
    VMJumpIf CMP_EQ, .Lhwwe\@
    VMSleep \unit
    WorkSub \work, 1
    VMJump .Lhww\@
.Lhwwe\@:
    .endm

// ---- movement actions (inside a list: `.balign 4, 0` before the list label, step_end at the end) --------------
// Codes from ov036's action table (0x021cca50 + 38 entries) and the movement probe (work/agents/story_infra/tests,
// 2026-10-06: tiles and frames measured in the emulator). Order inside each group: up, down, left, right.
    .macro step_end
    MoveEnd
    .endm
    .macro hmv code, n=1
    Move \code, \n
    .endm
    .macro face_up n=1
    Move 0, \n
    .endm
    .macro face_down n=1
    Move 1, \n
    .endm
    .macro face_left n=1
    Move 2, \n
    .endm
    .macro face_right n=1
    Move 3, \n
    .endm
    .macro walk_slow_up n=1                    // 16 field frames a tile (Gen 3 32)
    Move 8, \n
    .endm
    .macro walk_slow_down n=1
    Move 9, \n
    .endm
    .macro walk_slow_left n=1
    Move 10, \n
    .endm
    .macro walk_slow_right n=1
    Move 11, \n
    .endm
    .macro walk_up n=1                         // 8 field frames a tile (Gen 3 16)
    Move 12, \n
    .endm
    .macro walk_down n=1
    Move 13, \n
    .endm
    .macro walk_left n=1
    Move 14, \n
    .endm
    .macro walk_right n=1
    Move 15, \n
    .endm
    .macro walk_fast_up n=1                    // 4 field frames a tile (Gen 3 8)
    Move 16, \n
    .endm
    .macro walk_fast_down n=1
    Move 17, \n
    .endm
    .macro walk_fast_left n=1
    Move 18, \n
    .endm
    .macro walk_fast_right n=1
    Move 19, \n
    .endm
    .macro walk_fastest_up n=1                 // 2 field frames a tile (Gen 3 4)
    Move 20, \n
    .endm
    .macro walk_fastest_down n=1
    Move 21, \n
    .endm
    .macro walk_fastest_left n=1
    Move 22, \n
    .endm
    .macro walk_fastest_right n=1
    Move 23, \n
    .endm
    .macro walk_in_place_slow_up n=1           // step animation without moving, 16 field frames
    Move 28, \n
    .endm
    .macro walk_in_place_slow_down n=1
    Move 29, \n
    .endm
    .macro walk_in_place_slow_left n=1
    Move 30, \n
    .endm
    .macro walk_in_place_slow_right n=1
    Move 31, \n
    .endm
    .macro walk_in_place_up n=1                // 8 field frames
    Move 32, \n
    .endm
    .macro walk_in_place_down n=1
    Move 33, \n
    .endm
    .macro walk_in_place_left n=1
    Move 34, \n
    .endm
    .macro walk_in_place_right n=1
    Move 35, \n
    .endm
    .macro walk_in_place_fast_up n=1           // 4 field frames
    Move 36, \n
    .endm
    .macro walk_in_place_fast_down n=1
    Move 37, \n
    .endm
    .macro walk_in_place_fast_left n=1
    Move 38, \n
    .endm
    .macro walk_in_place_fast_right n=1
    Move 39, \n
    .endm
    .macro walk_in_place_fastest_up n=1        // 2 field frames (Sapphire's "turn on the spot")
    Move 40, \n
    .endm
    .macro walk_in_place_fastest_down n=1
    Move 41, \n
    .endm
    .macro walk_in_place_fastest_left n=1
    Move 42, \n
    .endm
    .macro walk_in_place_fastest_right n=1
    Move 43, \n
    .endm
    .macro jump_in_place_up n=1                // hop without moving (8 field frames; 44-47 = 16 frames)
    Move 48, \n
    .endm
    .macro jump_in_place_down n=1
    Move 49, \n
    .endm
    .macro jump_in_place_left n=1
    Move 50, \n
    .endm
    .macro jump_in_place_right n=1
    Move 51, \n
    .endm
    .macro jump_up n=1                         // jump one tile
    Move 52, \n
    .endm
    .macro jump_down n=1
    Move 53, \n
    .endm
    .macro jump_left n=1
    Move 54, \n
    .endm
    .macro jump_right n=1
    Move 55, \n
    .endm
    .macro jump_2_up n=1                       // jump two tiles (ledges); 92-95 jump three tiles
    Move 56, \n
    .endm
    .macro jump_2_down n=1
    Move 57, \n
    .endm
    .macro jump_2_left n=1
    Move 58, \n
    .endm
    .macro jump_2_right n=1
    Move 59, \n
    .endm
    // delays: Black 2 waits 1, 2, 4, 8, 15, 16, 32 field frames (codes 60-66); Gen 3 delay_N = N/2 field frames
    .macro delay_1 n=1
    Move 60, \n
    .endm
    .macro delay_2 n=1
    Move 60, \n
    .endm
    .macro delay_4 n=1
    Move 61, \n
    .endm
    .macro delay_8 n=1
    Move 62, \n
    .endm
    .macro delay_16 n=1
    Move 63, \n
    .endm
    .macro set_invisible
    Move 69, 1
    .endm
    .macro set_visible
    Move 70, 1
    .endm
    .macro lock_facing_direction
    Move 71, 1
    .endm
    .macro unlock_facing_direction
    Move 72, 1
    .endm
    .macro emote_exclamation_mark              // "!" balloon (with its sound)
    Move 75, 1
    .endm
    .macro emote_question_mark                 // "?" balloon
    Move 159, 1
    .endm
    .macro emote_heart                         // Black 2 has no heart balloon: the music-note one (160); 161 = "..."
    Move 160, 1
    .endm
