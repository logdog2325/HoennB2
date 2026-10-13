// The Battle Frontier's shared script interface (frontier_core, 2026-10-12; notes/FRONTIER.md has the reference).
// Pokémon Emerald NDS builds only: commands 230/232 are b2tools/patches/frontier_core.c's and global 2289 is
// emerald_mech's (src/field_scripts/emerald/1236_global_2280.s); a Sapphire or Ruby build has neither.
// Include after "asm/field_script.inc", "hoenn.h", "hoenn_story.inc" and "hoenn_emerald.inc". Emits no code by itself.
//
// Scratch works: FR_T0-FR_T3 (0x8048-0x804B) and FR_PICK (0x804C-0x804F) are this file's; the macros overwrite
// them. HLIB_TMP is left alone.

#ifndef HOENN_FRONTIER_INC
#define HOENN_FRONTIER_INC

#define FR_T0 0x8048
#define FR_T1 0x8049
#define FR_T2 0x804A
#define FR_T3 0x804B
#define FR_PICK 0x804C                  // EmPickParty's var: + 1 .. + 3 = the picked party slots

// ---- Emerald's constants (pokeemerald include/constants/battle_frontier.h) -------------------------------------
#define FRONTIER_FACILITY_TOWER 0
#define FRONTIER_FACILITY_DOME 1
#define FRONTIER_FACILITY_PALACE 2
#define FRONTIER_FACILITY_ARENA 3
#define FRONTIER_FACILITY_FACTORY 4
#define FRONTIER_FACILITY_PIKE 5
#define FRONTIER_FACILITY_PYRAMID 6
#define FRONTIER_MODE_SINGLES 0
#define FRONTIER_MODE_DOUBLES 1
#define FRONTIER_MODE_MULTIS 2
#define FRONTIER_MODE_LINK_MULTIS 3
#define FR_LVL_50 0
#define FR_LVL_OPEN 1
#define FR_ST_NONE 0                    // CHALLENGE_STATUS_*: nothing going on
#define FR_ST_SAVING 1                  // entered (saved in the lobby): seen on Continue = quit without saving
#define FR_ST_PAUSED 2                  // saved and quit mid-challenge: resume in the lobby
#define FR_ST_WON 3                     // back in the lobby after winning the challenge
#define FR_ST_LOST 4                    // back in the lobby after losing

// ---- keys of the record area (FrGet / FrOp 0x100 | key): notes/FRONTIER.md 2.2 ------------------------------------
#define FR_STATUS 0
#define FR_FACILITY 1
#define FR_BATTLE_MODE 2
#define FR_LVL_MODE 3
#define FR_PARTY 4                      // the picks: (slot1+1) | (slot2+1) << 4 | (slot3+1) << 8
#define FR_BATTLE_NUM 5
#define FR_SYMBOLS 6                    // bit 2f silver, 2f+1 gold
#define FR_LAST_BP 7
#define FR_BRAIN_BEATEN 8               // 1: the challenge just won ended with the facility's Brain (the lobby's +10 BP)
#define FR_TUTOR_MET 10                 // bit 0 / 1: the left / right BP tutor has been met (Emerald's FLAG_MET_FRONTIER_*_MOVE_TUTOR)
#define FR_STREAKS 16                   // 16 + 8f + 4m + 2l current, + 1 best (m: 0 singles, 1 doubles; l: level mode)
#define FR_EXTRA 72                     // 72-95: claimed per facility (notes/FRONTIER.md 6)

// computed keys of FrGet
#define FR_GET_BP 0x100                 // the player's Battle Points
#define FR_GET_STREAK 0x200             // | f | m << 3: the current streak at FR_LVL_MODE
#define FR_GET_BEST 0x300               // | f | m << 3: the best streak at FR_LVL_MODE
#define FR_GET_SYMBOL 0x400             // | f: 0 none, 1 silver, 2 gold
#define FR_GET_TUTOR_COST 0x500         // | side << 4 | k: the BP tutor's k-th move (0-9) price
#define FR_GET_TUTOR_ID 0x600           //   its EM_TUTOR_* (emerald_mech's compatibility bit)
#define FR_GET_TUTOR_MOVE 0x700         //   its move id
#define FR_GET_ELIGIBLE 0x800           // | lvl: Pokémon eligible under the Frontier's rules (pokeemerald CheckPartyIneligibility)
#define FR_GET_PICK 0x900               // | i: the i-th pick (party slot 0-5; 255 none)
#define FR_GET_BANNED_NAMES 0xA00       // | w: Emerald's {STR_VAR_1} of the "not enough eligible" lines into word buffer w
                                        //   (the banned species the player has caught, then "are"); the count
// ops of FrOp (op | arg, var)
#define FR_OP_SET 0x100                 // | key: key = var
#define FR_OP_ADD_BP 0x200              // BP += var (cap 9,999; the trainer card's BP record too); var = the BP now
#define FR_OP_TAKE_BP 0x300             // var = 1 and var's BP taken if the player has them, else var = 0
#define FR_OP_STREAK_WIN 0x400          // | f | m << 3: current streak + 1 (at FR_LVL_MODE), best = max; var = the streak
#define FR_OP_STREAK_RESET 0x500        // | f | m << 3: current streak = 0
#define FR_OP_GIVE_POINTS 0x600         // | brain: Emerald's GiveBattlePoints for FR_FACILITY/BATTLE_MODE/LVL_MODE; var = BP
#define FR_OP_SYMBOL 0x700              // | f << 1 | gold
#define FR_OP_SAVE_PICKS 0x800          // var = FR_PICK: its + 1 .. + 3 -> FR_PARTY
#define FR_OP_SOFT_RESET 0x900
#define FR_OP_BP_WINDOW 0xA00           // Black 2's money window, top right, showing the BP (close: MoneyWinClose)
#define FR_OP_ADD 0xB00                 // | key: key += var; var = the new value
#define FR_OP_GIVE_POINTS_FOR 0xC00     // | brain: as GIVE_POINTS with var = the streak (a facility with its own count)

// Emerald's Frontier fanfares and songs (Black 2 sequence ids of the Emerald build: data/emerald/hoenn_music.json,
// frontier_core_music; notes/FRONTIER.md 5). MEPlay the fanfares, BGM via the zone (zone_songs) or BGMPlay.
#define FR_ME_OBTAIN_BP 2401            // mus_obtain_b_points (Unova music answer: Black 2's SEQ_ME_BPGET)
#define FR_ME_OBTAIN_SYMBOL 2323        // mus_obtain_symbol (Unova answer: SEQ_ME_BADGE)
#define FR_BGM_FRONTIER 2398            // mus_b_frontier (the island)
#define FR_BGM_TOWER 2405               // Emerald's mus_b_tower
#define FR_BGM_DOME 2324
#define FR_BGM_DOME_LOBBY 2328
#define FR_BGM_FACTORY 2326
#define FR_BGM_PIKE 2325
#define FR_BGM_PALACE 2404
#define FR_BGM_ARENA 2400
#define FR_BGM_PYRAMID 2402
#define FR_BGM_PYRAMID_TOP 2403
#define FR_BGM_VS_BRAIN 2327            // mus_vs_frontier_brain

// the Exchange Service Corner's BP shops (CallFriendlyShopBuy id): Emerald's lists on Black 2's BP shop screen
#define FR_SHOP_VITAMINS 240
#define FR_SHOP_HOLD_ITEMS 241

// ---- the two commands -----------------------------------------------------------------------------------------
    .macro FrGet key, var
    FieldCommand 230
    .2byte \key
    .2byte \var
    .endm
    .macro FrOp op, var
    FieldCommand 232
    .2byte \op
    .2byte \var
    .endm

// ---- small macros ---------------------------------------------------------------------------------------------
    .macro fr_get key, var              // var = key (a record key 0-95 or an FR_GET_* key)
    FrGet \key, \var
    .endm
    .macro fr_set key, value            // key = value (a number or a work)
    WorkSet FR_T0, \value
    FrOp FR_OP_SET | (\key), FR_T0
    .endm
    .macro fr_bp var                    // var = the player's BP
    FrGet FR_GET_BP, \var
    .endm
    .macro fr_add_bp value              // BP += value (a number or a work)
    WorkSet FR_T0, \value
    FrOp FR_OP_ADD_BP, FR_T0
    .endm
    .macro fr_take_bp cost, result      // result = 1 and the BP taken, or 0 and nothing taken
    WorkSet \result, \cost
    FrOp FR_OP_TAKE_BP, \result
    .endm
    .macro fr_streak_win fac, mode      // the current streak + 1 (the best follows); FR_T0 = the streak
    FrOp FR_OP_STREAK_WIN | (\fac) | ((\mode) << 3), FR_T0
    .endm
    .macro fr_streak_reset fac, mode
    FrOp FR_OP_STREAK_RESET | (\fac) | ((\mode) << 3), FR_T0
    .endm
    .macro fr_streak fac, mode, var     // the current streak at FR_LVL_MODE
    FrGet FR_GET_STREAK | (\fac) | ((\mode) << 3), \var
    .endm
    .macro fr_best fac, mode, var
    FrGet FR_GET_BEST | (\fac) | ((\mode) << 3), \var
    .endm
    .macro fr_symbol_get fac, var       // 0 none, 1 silver, 2 gold
    FrGet FR_GET_SYMBOL | (\fac), \var
    .endm
    .macro fr_symbol_give fac, gold     // gold: 0 the Silver Symbol, 1 the Gold Symbol
    FrOp FR_OP_SYMBOL | ((\fac) << 1) | (\gold), FR_T0
    .endm
    .macro fr_check_party lvl, result   // result = eligible Pokémon at level mode lvl (a number or a work)
    WorkSet FR_T0, \lvl
    WorkCmpConst FR_T0, FR_LVL_50
    VMJumpIf CMP_NE, .Lfrcp_open\@
    FrGet FR_GET_ELIGIBLE | FR_LVL_50, \result
    VMJump .Lfrcp_end\@
.Lfrcp_open\@:
    FrGet FR_GET_ELIGIBLE | FR_LVL_OPEN, \result
.Lfrcp_end\@:
    .endm
    .macro fr_give_points brain=0       // Emerald's GiveBattlePoints; FR_T0 = the BP given, also word 1 (a number)
    FrOp FR_OP_GIVE_POINTS | (\brain), FR_T0
    WordSetNumber 1, FR_T0, 2
    .endm
    .macro fr_give_points_for streak, brain=0   // the same, with the facility's own streak count (a number or a work)
    WorkSet FR_T0, \streak
    FrOp FR_OP_GIVE_POINTS_FOR | (\brain), FR_T0
    WordSetNumber 1, FR_T0, 2
    .endm
    .macro fr_bp_window                 // show / refresh the BP window (top right); close with MoneyWinClose
    FrOp FR_OP_BP_WINDOW, FR_T0
    .endm
    .macro fr_soft_reset
    FrOp FR_OP_SOFT_RESET, FR_T0
    .endm

// Black 2's save dialog (global 2003, Common_EventScript_SaveGame): result = 0 saved. Works 0x8000-0x8005 kept.
    .macro fr_save_game result
    VMStackPush 0x8000
    VMStackPush 0x8001
    VMStackPush 0x8002
    VMStackPush 0x8003
    VMStackPush 0x8004
    VMStackPush 0x8005
    RTCallGlobal 2003
    WorkSet \result, 0x8000
    VMStackPop 0x8005
    VMStackPop 0x8004
    VMStackPop 0x8003
    VMStackPop 0x8002
    VMStackPop 0x8001
    VMStackPop 0x8000
    .endm
// a save without the dialog ("SAVING..." is the caller's message), as the Battle Tower's record save
    .macro fr_save_quiet
    SaveDataWrite FR_T3
    SEPlay SEQ_SE_SAVE
    SEWait
    .endm

// The party menu (emerald_mech's EmPickParty: Black 2's battle-entry screen, numbered picks, CONFIRM / CANCEL) with
// the Frontier's rule: exactly `need` Pokémon, Lv. 50 = level 50 or less (FR_LVL_MODE), no species or held item
// twice, the banned list. The picks go to FR_PARTY (and FR_PICK + 1 .. + 3); B / CANCEL -> `cancel`.
    .macro fr_pick_party need, cancel
    FrGet FR_LVL_MODE, FR_T0
    WorkSetConst FR_PICK, 0x20 | 0x10 | (\need)
    WorkCmpConst FR_T0, FR_LVL_50
    VMJumpIf CMP_EQ, .Lfrpp_go\@
    WorkSetConst FR_PICK, 0x20 | (\need)
.Lfrpp_go\@:
    EmPickParty FR_PICK
    WorkCmpConst FR_PICK, \need
    VMJumpIf CMP_NE, \cancel
    FrOp FR_OP_SAVE_PICKS, FR_PICK
    .endm

// ---- the lobby ------------------------------------------------------------------------------------------------
// A receptionist script, Emerald's flow (pokeemerald BattleFrontier_Battle<Facility>Lobby_EventScript_Attendant /
// _TryEnterChallenge / _SaveBeforeChallenge): welcome; "take the challenge?" CHALLENGE / INFO / EXIT; the level
// mode LV. 50 / OPEN LEVEL / EXIT; the eligibility check (Emerald's "not enough eligible Pokémon" lines); the pick of
// `pick` Pokémon (0: none, e.g. the Factory's rentals) or the facility's own pick (`onpick`); "the challenge must be
// saved" YES/NO; Black 2's save dialog; "step this way"; then it jumps to `enter` (the facility walks the player in
// and warps). Cancelled anywhere: the goodbye line, release.
// tb = the first line of the zone's lobby text block (the lines below, from tools: b2tools/frontier_text.py lobby).
// Hooks (labels, optional; VMCall'ed, return with VMReturn): onpick (instead of the library's pick: FR_T0 = the level
// mode; set FR_T1 = 1 picked, 0 cancelled), onunpick (after a pick, when the player says NO to the save or the save
// fails), onsave (just before the save). track = 1: FR_STATUS = FR_ST_SAVING before the save (0: the facility keeps
// its own status, e.g. the Battle Tower's).
#define FRT_WELCOME 0
#define FRT_TAKE 1
#define FRT_EXPLAIN 2
#define FRT_WHICH_LEVEL 3
#define FRT_NOT_ENOUGH_50 4
#define FRT_NOT_ENOUGH_OPEN 5
#define FRT_CHOOSE 6
#define FRT_SAVE_BEFORE 7
#define FRT_STEP 8
#define FRT_GOODBYE 9
#define FRT_DIDNT_SAVE 10
#define FRT_WON 11
#define FRT_WON_BRAIN 12
#define FRT_AWARD 13
#define FRT_RECORD_WON 14
#define FRT_LOST 15
#define FRT_RESUME 16
#define FRT_MENU_CHALLENGE 17
#define FRT_MENU_INFO 18
#define FRT_MENU_EXIT 19
#define FRT_MENU_LV50 20
#define FRT_MENU_OPEN 21
#define FRT_OBTAINED_BP 22
#define FRT_COUNT 23

    .macro fr_lobby_attendant fac, mode, tb, enter, pick=3, onpick, onunpick, onsave, track=1
    h_lock
    SEPlay SEQ_SE_MESSAGE
    h_faceplayer
    fr_set FR_FACILITY, \fac
    fr_set FR_BATTLE_MODE, \mode
    h_msgbox (\tb) + FRT_WELCOME
.Lfrla_ask\@:
    ParentActorMsg MSGFILE_SCRIPT, (\tb) + FRT_TAKE, 0, 0
    ListMenu_AnchorTopRight 31, 6, 0, 1, FR_T0
    ListMenuAdd (\tb) + FRT_MENU_CHALLENGE, 65535, 0
    ListMenuAdd (\tb) + FRT_MENU_INFO, 65535, 1
    ListMenuAdd (\tb) + FRT_MENU_EXIT, 65535, 2
    ListMenuShow
    WorkCmpConst FR_T0, 0
    VMJumpIf CMP_EQ, .Lfrla_level\@
    WorkCmpConst FR_T0, 1
    VMJumpIf CMP_NE, .Lfrla_cancel\@
    h_msgbox (\tb) + FRT_EXPLAIN
    VMJump .Lfrla_ask\@
.Lfrla_level\@:
    ParentActorMsg MSGFILE_SCRIPT, (\tb) + FRT_WHICH_LEVEL, 0, 0
    ListMenu_AnchorTopRight 31, 6, 0, 1, FR_T0
    ListMenuAdd (\tb) + FRT_MENU_LV50, 65535, FR_LVL_50
    ListMenuAdd (\tb) + FRT_MENU_OPEN, 65535, FR_LVL_OPEN
    ListMenuAdd (\tb) + FRT_MENU_EXIT, 65535, 2
    ListMenuShow
    WorkCmpConst FR_T0, FR_LVL_OPEN
    VMJumpIf CMP_GT, .Lfrla_cancel\@
    .if \pick
    WorkSet FR_T2, FR_T0
    fr_check_party FR_T2, FR_T1
    WorkSet FR_T0, FR_T2
    WorkCmpConst FR_T1, \pick
    VMJumpIf CMP_LT, .Lfrla_ineligible\@
    .endif
    fr_set FR_LVL_MODE, FR_T0
    .ifnb \onpick
    FrGet FR_LVL_MODE, FR_T0
    VMCall \onpick
    WorkCmpConst FR_T1, 0
    VMJumpIf CMP_EQ, .Lfrla_cancel\@
    .else
    .if \pick
    h_msgbox (\tb) + FRT_CHOOSE
    h_closemessage
    fr_pick_party \pick, .Lfrla_cancel\@
    .endif
    .endif
    h_yesno (\tb) + FRT_SAVE_BEFORE, FR_T1
    h_goto_if_no FR_T1, .Lfrla_unpick\@
    .ifnb \onsave
    VMCall \onsave
    .endif
    .if \track
    fr_set FR_STATUS, FR_ST_SAVING
    fr_set FR_BRAIN_BEATEN, 0
    .endif
    h_closemessage
    fr_save_game FR_T1
    WorkCmpConst FR_T1, 0
    VMJumpIf CMP_EQ, .Lfrla_saved\@
    .if \track
    fr_set FR_STATUS, FR_ST_NONE
    .endif
.Lfrla_unpick\@:
    .ifnb \onunpick
    VMCall \onunpick
    .endif
    VMJump .Lfrla_cancel\@
.Lfrla_ineligible\@:
    FrGet FR_GET_BANNED_NAMES | 1, FR_T3    // word 1: "Eggs{0100:1} ineligible." as Emerald (", Mew and Mewtwo are")
    WorkCmpConst FR_T0, FR_LVL_50
    VMJumpIf CMP_NE, .Lfrla_inopen\@
    h_msgbox (\tb) + FRT_NOT_ENOUGH_50
    h_closemessage
    h_release
.Lfrla_inopen\@:
    h_msgbox (\tb) + FRT_NOT_ENOUGH_OPEN
    h_closemessage
    h_release
.Lfrla_cancel\@:
    h_msgbox (\tb) + FRT_GOODBYE
    h_closemessage
    h_release
.Lfrla_saved\@:
    h_msgbox (\tb) + FRT_STEP
    h_closemessage
    VMJump \enter
    .endm

// The lobby's state on arrival (the zone's map-script condition, as Emerald's OnFrame table: run it once per visit,
// e.g. while a map-local work is 0): FR_STATUS of this facility -> quit without saving (the line, the current
// streak ends), won (congratulations or the Brain line, "we award you these Battle Points", Emerald's BP, the
// record saved), lost (the line, the streak ends, saved), paused (the "waiting for you" line, FR_STATUS back to
// FR_ST_SAVING, saved, then jumps to `resume`: the facility walks the player in again). Every other case: release.
// who = the receptionist's uid (it says the lines). Hooks: onquit / onwon / onlost (VMCall'ed first: the facility's
// own clean-up, e.g. its engine's state). me = the fanfare of "obtained N Battle Points" (Emerald's
// mus_obtain_b_points, FR_ME_OBTAIN_BP).
    .macro fr_lobby_returned fac, mode, tb, who, resume, onquit, onwon, onlost, me=FR_ME_OBTAIN_BP
    h_lock
    FrGet FR_FACILITY, FR_T0
    WorkCmpConst FR_T0, \fac
    VMJumpIf CMP_NE, .Lfrlr_end\@
    FrGet FR_STATUS, FR_T1
    WorkCmpConst FR_T1, FR_ST_SAVING
    VMJumpIf CMP_EQ, .Lfrlr_quit\@
    WorkCmpConst FR_T1, FR_ST_WON
    VMJumpIf CMP_EQ, .Lfrlr_won\@
    WorkCmpConst FR_T1, FR_ST_LOST
    VMJumpIf CMP_EQ, .Lfrlr_lost\@
    WorkCmpConst FR_T1, FR_ST_PAUSED
    VMJumpIf CMP_EQ, .Lfrlr_resume\@
.Lfrlr_end\@:
    h_release
.Lfrlr_quit\@:
    .ifnb \onquit
    VMCall \onquit
    .endif
    h_msgbox_actor (\tb) + FRT_DIDNT_SAVE, \who
    fr_streak_reset \fac, \mode
    fr_set FR_STATUS, FR_ST_NONE
    h_closemessage
    h_release
.Lfrlr_won\@:
    .ifnb \onwon
    VMCall \onwon
    .endif
    FrGet FR_BRAIN_BEATEN, FR_T2
    WorkCmpConst FR_T2, 0
    VMJumpIf CMP_NE, .Lfrlr_brain\@
    h_msgbox_actor (\tb) + FRT_WON, \who
    VMJump .Lfrlr_award\@
.Lfrlr_brain\@:
    h_msgbox_actor (\tb) + FRT_WON_BRAIN, \who
.Lfrlr_award\@:
    h_msgbox_actor (\tb) + FRT_AWARD, \who
    FrGet FR_BRAIN_BEATEN, FR_T2
    WorkCmpConst FR_T2, 0
    VMJumpIf CMP_NE, .Lfrlr_award10\@
    fr_give_points 0
    VMJump .Lfrlr_awarded\@
.Lfrlr_award10\@:
    fr_give_points 1
.Lfrlr_awarded\@:
    h_buffer_player
    MEPlay \me
    h_msgbox_actor (\tb) + FRT_OBTAINED_BP, \who
    MEWait
    fr_set FR_STATUS, FR_ST_NONE
    fr_set FR_BRAIN_BEATEN, 0
    ActorMsg MSGFILE_SCRIPT, (\tb) + FRT_RECORD_WON, \who, 0, 0
    fr_save_quiet
    VMJump .Lfrlr_bye\@
.Lfrlr_lost\@:
    .ifnb \onlost
    VMCall \onlost
    .endif
    ActorMsg MSGFILE_SCRIPT, (\tb) + FRT_LOST, \who, 0, 0
    fr_streak_reset \fac, \mode
    fr_set FR_STATUS, FR_ST_NONE
    fr_save_quiet
.Lfrlr_bye\@:
    h_msgbox_actor (\tb) + FRT_GOODBYE, \who
    h_closemessage
    h_release
.Lfrlr_resume\@:
    ActorMsg MSGFILE_SCRIPT, (\tb) + FRT_RESUME, \who, 0, 0
    fr_set FR_STATUS, FR_ST_SAVING
    fr_save_quiet
    h_closemessage
    VMJump \resume
    .endm

// Mid-challenge "save and quit" (Emerald's pause): FR_STATUS = FR_ST_PAUSED; Continue starts in the lobby (Black 2's
// next zone + EVENT_FLAG_CONTINUE_SCRIPT 2405, as the Battle Tower's rest) at zone tile (x, z) facing dir; the save
// ("SAVING..." line `saving` of the zone's text, said by actor `who`), then the soft reset.
    .macro fr_rest_and_quit lobby_zone, x, z, dir, saving, who
    fr_set FR_STATUS, FR_ST_PAUSED
    FieldSetNextZone \lobby_zone, \dir, \x, 0, \z
    FlagSet 2405
    ActorMsg MSGFILE_SCRIPT, \saving, \who, 0, 0
    h_delay 60
    SaveDataWrite FR_T3
    SEPlay SEQ_SE_SAVE
    SEWait
    h_closemessage
    FadeOutBlack
    FadeWait
    fr_soft_reset
    VMHalt
    .endm

// ---- the Exchange Service Corner and the BP tutors -------------------------------------------------------------
// A BP prize clerk: Emerald's welcome (line `welcome`), Black 2's BP shop screen with Emerald's list (FR_SHOP_*),
// Emerald's goodbye (line `bye`).
    .macro fr_bp_shop shop, welcome, bye
    h_lock
    SEPlay SEQ_SE_MESSAGE
    h_faceplayer
    h_msgbox \welcome
    h_closemessage
    CallFriendlyShopBuy \shop, FR_T0
    h_msgbox \bye
    h_closemessage
    h_release
    .endm

// One of Emerald's two BP move tutors (pokeemerald BattleFrontier_Lounge7_EventScript_LeftMoveTutor /
// _RightMoveTutor): side 0 left (Softboiled ... Swords Dance), 1 right (Defense Curl ... Fire Punch); the first talk
// is remembered in FR_TUTOR_MET (bit side); tt = the first line of the zone's tutor text block:
//   tt+0 intro (first talk), +1 welcome back, +2 "which move should I teach?", +3 .. +12 the menu (move and price),
//   +13 the menu's EXIT, +14 "The move X, is it? That will be N Battle Points, okay?" (word 1 the move, word 2 the
//   price: Emerald's STR_VAR_1/2), +15 not enough BP, +16 "pick the Pokémon", +17 "I'll take your Battle Points",
//   +18 "you don't want to".
// The menu shows the BP window; the move is taught by emerald_mech's tutor global (2289: who can learn it is
// pokeemerald's sTutorLearnsets; "not compatible" / "already knows" / forgetting a move as Emerald); the BP are taken
// only when it was taught.
    .macro fr_bp_tutor side, tt
    h_lock
    SEPlay SEQ_SE_MESSAGE
    h_faceplayer
    FrGet FR_TUTOR_MET, FR_T0
    WorkAnd FR_T0, 1 << (\side)
    WorkCmpConst FR_T0, 0
    VMJumpIf CMP_NE, .Lfrbt_back\@
    h_msgbox (\tt) + 0
    FrGet FR_TUTOR_MET, FR_T0
    WorkOr FR_T0, 1 << (\side)
    FrOp FR_OP_SET | FR_TUTOR_MET, FR_T0
    VMJump .Lfrbt_menu\@
.Lfrbt_back\@:
    h_msgbox (\tt) + 1
.Lfrbt_menu\@:
    fr_bp_window
    ParentActorMsg MSGFILE_SCRIPT, (\tt) + 2, 0, 0
    ListMenu_AnchorTopRight 31, 4, 0, 1, FR_T0
    ListMenuAdd (\tt) + 3, 65535, 0
    ListMenuAdd (\tt) + 4, 65535, 1
    ListMenuAdd (\tt) + 5, 65535, 2
    ListMenuAdd (\tt) + 6, 65535, 3
    ListMenuAdd (\tt) + 7, 65535, 4
    ListMenuAdd (\tt) + 8, 65535, 5
    ListMenuAdd (\tt) + 9, 65535, 6
    ListMenuAdd (\tt) + 10, 65535, 7
    ListMenuAdd (\tt) + 11, 65535, 8
    ListMenuAdd (\tt) + 12, 65535, 9
    ListMenuAdd (\tt) + 13, 65535, 10
    ListMenuShow
    WorkCmpConst FR_T0, 9
    VMJumpIf CMP_GT, .Lfrbt_exit\@
    WorkSet FR_T1, FR_T0
    WorkAdd FR_T1, FR_GET_TUTOR_COST | ((\side) << 4)
    FrGet FR_T1, FR_T2                  // the price
    WorkSet FR_T1, FR_T0
    WorkAdd FR_T1, FR_GET_TUTOR_MOVE | ((\side) << 4)
    FrGet FR_T1, FR_T3                  // the move
    WordSetMoveName 1, FR_T3
    WordSetNumber 2, FR_T2, 2
    h_yesno (\tt) + 14, FR_T1
    h_goto_if_no FR_T1, .Lfrbt_menu\@
    fr_bp FR_T1
    VMStackPush FR_T1
    VMStackPush FR_T2
    VMStackCmp CMP_GE
    VMJumpIf CMP_STACK, .Lfrbt_poor\@
    h_msgbox (\tt) + 16
    MoneyWinClose
    h_closemessage
    WorkSet FR_T1, FR_T0
    WorkAdd FR_T1, FR_GET_TUTOR_ID | ((\side) << 4)
    FrGet FR_T1, 0x8000                 // the global's input: 0x8000 tutor, 0x8001 move -> 0x8010 1 taught
    WorkSet 0x8001, FR_T3
    RTCallGlobal EM_GLOBAL_MOVE_TUTOR
    WorkCmpConst 0x8010, 1
    VMJumpIf CMP_NE, .Lfrbt_no\@
    h_msgbox (\tt) + 17
    fr_take_bp FR_T2, FR_T1
    h_closemessage
    h_release
.Lfrbt_poor\@:
    h_msgbox (\tt) + 15
    VMJump .Lfrbt_menu\@
.Lfrbt_exit\@:
    MoneyWinClose
.Lfrbt_no\@:
    h_msgbox (\tt) + 18
    h_closemessage
    h_release
    .endm

#endif
