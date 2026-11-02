// Pokémon Contests at the Contest Hall counters (notes/CONTESTS.md): pokeruby's and pokeemerald's data/scripts/contest_hall.inc,
// data/scripts/pokeblocks.inc, on HoennB2's extension command (decomp src/hoennb2/resident/contest_cmd.c, sub-commands
// 0x20-0x28 of FieldCommand 351, include/hoennb2/ext_cmd.h). Replaces Black 2's Musical at these counters (the Musical stays with one person in Lilycove's lobby, all versions). Sapphire and Ruby: one
// rank at each of Verdanturf (Normal), Fallarbor (Super), Slateport (Hyper), Lilycove (Master), with the Contest Pass from
// Verdanturf. Emerald: every rank at Lilycove, no pass.
//
// The Hall's stage intro and award are on the contest screen (overlay 346), not Gen 3's walking scene in a room.
// Text: the lobby's own file holds the lines below from line t on (b2tools/gen_contest_text.py). Works 0x8029-0x802F.
#ifndef HOENN_CONTESTS_INC
#define HOENN_CONTESTS_INC

// HoennB2's range for Contests (registered by the lead at merge: data/story_ids.json): flags 2573-2584, works 0x419A-0x41A1
#ifndef FLAG_RECEIVED_CONTEST_PASS
#define FLAG_RECEIVED_CONTEST_PASS 2573
#endif
#ifndef VAR_CONTEST_PRIZE_PICKUP
#define VAR_CONTEST_PRIZE_PICKUP 0x419A
#endif

#define CON_W 0x8029
#define CON_OK 0x802A
#define CON_SLOT 0x802B
#define CON_CAT 0x802C
#define CON_RANK 0x802D
#define CON_PLACE 0x802E
#define CON_ITEM 0x802F

// b2tools/gen_contest_text.py LINES
#define CL_ENTER 0              // Would you like to enter a Contest? ...
#define CL_WHICH_TOPIC 1
#define CL_EXPLAIN 2
#define CL_TYPES 3
#define CL_RANKS 4
#define CL_ANOTHER 5
#define CL_WHICH_MON 6
#define CL_NO_PASS 7            // You need a Contest Pass (above Normal Rank's counter)
#define CL_PASS_ASK 8
#define CL_PASS_GOT 9
#define CL_PASS_HAD 10
#define CL_PASS_NO 11
#define CL_WHICH_CAT 12
#define CL_NOT_QUALIFIED 13
#define CL_CONFIRM 14
#define CL_HIGHER 15
#define CL_EGG 16
#define CL_NO_HP 17
#define CL_PROCEED 18
#define CL_PRIZE 19
#define CL_PRIZE_FULL 20
#define CL_CONFER 21
#define CL_RIBBON 22
#define CL_RIBBON_PUT 23
#define CL_AGAIN 24
#define CL_PICKUP 25
#define CL_M_ENTER 26
#define CL_M_INFO 27
#define CL_M_EXIT 28
#define CL_M_ABOUT 29
#define CL_M_TYPES 30
#define CL_M_RANKS 31
#define CL_M_BACK 32
#define CL_M_COOL 33            // 33-37 the categories, 38 Exit
#define CL_M_CAT_EXIT 38
#define CL_M_NORMAL 39          // 39-42 the ranks (Emerald's menu)
#define CL_WHICH_RANK 43
#define CL_BL_ASK 44
#define CL_BL_NO_CASE 45
#define CL_BL_NO_BERRY 46
#define CL_BL_FULL 47
#define CL_BL_PICK 48
#define CL_BL_CANT 49
#define CL_BL_NO 50

    .macro con_ext sub
    FieldCommand 351
    .byte \sub
    .endm
    .macro con_eligible slot, cat, rank, var
    con_ext 0x20
    .2byte \slot
    .2byte \cat
    .2byte \rank
    .2byte \var
    .endm
    .macro con_run slot, cat, rank, var
    con_ext 0x21
    .2byte \slot
    .2byte \cat
    .2byte \rank
    .2byte \var
    .endm
    .macro con_has_won slot, cat, rank, var
    con_ext 0x22
    .2byte \slot
    .2byte \cat
    .2byte \rank
    .2byte \var
    .endm
    .macro con_give_ribbon slot, cat, rank
    con_ext 0x23
    .2byte \slot
    .2byte \cat
    .2byte \rank
    .endm
    .macro con_blend item, people, var
    con_ext 0x24
    .2byte \item
    .2byte \people
    .2byte \var
    .endm
    .macro con_case_space var
    con_ext 0x26
    .2byte \var
    .endm
    .macro con_berry_ok item, var
    con_ext 0x27
    .2byte \item
    .2byte \var
    .endm
    .macro con_has_berries var
    con_ext 0x28
    .2byte \var
    .endm

// The whole receptionist, from c3_talk-style lock + face (done by the caller) to the release. rank: 0-3 (Sapphire, Ruby: the
// lobby's own) or 255 (Emerald: a menu). welcome: the "accepting registrations" line to say first.
    .macro contest_reception t, rank, welcome
    h_goto_if_eq VAR_CONTEST_PRIZE_PICKUP, 0, .Lcon_noprize\@
    h_msgbox (\t) + CL_PRIZE
    h_closemessage
    h_checkitemspace ITEM_LUXURY_BALL, 1, CON_W
    h_goto_if_eq CON_W, 0, .Lcon_prize_full\@
    h_giveitem ITEM_LUXURY_BALL, 1
    h_setvar VAR_CONTEST_PRIZE_PICKUP, 0
    h_release
.Lcon_prize_full\@:
    h_msgbox (\t) + CL_PRIZE_FULL
    h_release
.Lcon_noprize\@:
    h_msgbox \welcome
#ifndef HOENN_EMERALD
    h_goto_if_set FLAG_RECEIVED_CONTEST_PASS, .Lcon_menu\@
    h_checkitem ITEM_CONTEST_PASS, 1, CON_W
    h_goto_if_eq CON_W, 1, .Lcon_menu\@
    .if \rank != 0
    h_msgbox (\t) + CL_NO_PASS
    h_release
    .else
    h_yesno (\t) + CL_PASS_ASK, CON_W
    h_goto_if_no CON_W, .Lcon_pass_no\@
    h_msgbox (\t) + CL_PASS_GOT
    h_closemessage
    h_giveitem ITEM_CONTEST_PASS, 1
    h_setflag FLAG_RECEIVED_CONTEST_PASS
    h_msgbox (\t) + CL_EXPLAIN
    VMJump .Lcon_menu\@
.Lcon_pass_no\@:
    h_msgbox (\t) + CL_PASS_NO
    h_release
    .endif
#endif
.Lcon_menu\@:
    ParentActorMsg MSGFILE_SCRIPT, (\t) + CL_ENTER, 0, 0
    ListMenu_AnchorTopRight 31, 6, 0, 1, CON_W
    ListMenuAdd (\t) + CL_M_ENTER, 65535, 0
    ListMenuAdd (\t) + CL_M_INFO, 65535, 1
    ListMenuAdd (\t) + CL_M_EXIT, 65535, 2
    ListMenuShow
    h_goto_if_eq CON_W, 0, .Lcon_rank\@
    h_goto_if_eq CON_W, 1, .Lcon_info\@
.Lcon_bye\@:
    h_msgbox (\t) + CL_ANOTHER
    h_release
.Lcon_info\@:
    ParentActorMsg MSGFILE_SCRIPT, (\t) + CL_WHICH_TOPIC, 0, 0
    ListMenu_AnchorTopRight 31, 6, 0, 1, CON_W
    ListMenuAdd (\t) + CL_M_ABOUT, 65535, 0
    ListMenuAdd (\t) + CL_M_TYPES, 65535, 1
    ListMenuAdd (\t) + CL_M_RANKS, 65535, 2
    ListMenuAdd (\t) + CL_M_BACK, 65535, 3
    ListMenuShow
    h_goto_if_eq CON_W, 0, .Lcon_i0\@
    h_goto_if_eq CON_W, 1, .Lcon_i1\@
    h_goto_if_eq CON_W, 2, .Lcon_i2\@
    VMJump .Lcon_menu\@
.Lcon_i0\@:
    h_msgbox (\t) + CL_EXPLAIN
    VMJump .Lcon_info\@
.Lcon_i1\@:
    h_msgbox (\t) + CL_TYPES
    VMJump .Lcon_info\@
.Lcon_i2\@:
    h_msgbox (\t) + CL_RANKS
    VMJump .Lcon_info\@
.Lcon_rank\@:
    .if \rank == 255
    ParentActorMsg MSGFILE_SCRIPT, (\t) + CL_WHICH_RANK, 0, 0
    ListMenu_AnchorTopRight 31, 6, 0, 1, CON_RANK
    ListMenuAdd (\t) + CL_M_NORMAL, 65535, 0
    ListMenuAdd (\t) + CL_M_NORMAL + 1, 65535, 1
    ListMenuAdd (\t) + CL_M_NORMAL + 2, 65535, 2
    ListMenuAdd (\t) + CL_M_NORMAL + 3, 65535, 3
    ListMenuAdd (\t) + CL_M_CAT_EXIT, 65535, 4
    ListMenuShow
    h_goto_if_ge CON_RANK, 4, .Lcon_bye\@
    .else
    h_setvar CON_RANK, \rank
    .endif
    ParentActorMsg MSGFILE_SCRIPT, (\t) + CL_WHICH_CAT, 0, 0
    ListMenu_AnchorTopRight 31, 6, 0, 1, CON_CAT
    ListMenuAdd (\t) + CL_M_COOL, 65535, 0
    ListMenuAdd (\t) + CL_M_COOL + 1, 65535, 1
    ListMenuAdd (\t) + CL_M_COOL + 2, 65535, 2
    ListMenuAdd (\t) + CL_M_COOL + 3, 65535, 3
    ListMenuAdd (\t) + CL_M_COOL + 4, 65535, 4
    ListMenuAdd (\t) + CL_M_CAT_EXIT, 65535, 5
    ListMenuShow
    h_goto_if_ge CON_CAT, 5, .Lcon_bye\@
.Lcon_choose\@:
    h_msgbox (\t) + CL_WHICH_MON
    h_closemessage
    CallPokeSelect 0, CON_OK, CON_SLOT, 0
    h_goto_if_eq CON_OK, 0, .Lcon_menu\@
    con_eligible CON_SLOT, CON_CAT, CON_RANK, CON_W
    h_goto_if_eq CON_W, 1, .Lcon_equal\@
    h_goto_if_eq CON_W, 2, .Lcon_high\@
    h_goto_if_eq CON_W, 3, .Lcon_egg\@
    h_goto_if_eq CON_W, 4, .Lcon_nohp\@
    h_msgbox (\t) + CL_NOT_QUALIFIED
    VMJump .Lcon_choose\@
.Lcon_egg\@:
    h_msgbox (\t) + CL_EGG
    VMJump .Lcon_choose\@
.Lcon_nohp\@:
    h_msgbox (\t) + CL_NO_HP
    VMJump .Lcon_choose\@
.Lcon_equal\@:
    WordSetPartyPokeName 0, CON_SLOT
    h_yesno (\t) + CL_CONFIRM, CON_W
    h_goto_if_no CON_W, .Lcon_choose\@
    VMJump .Lcon_go\@
.Lcon_high\@:
    WordSetPartyPokeName 0, CON_SLOT
    h_yesno (\t) + CL_HIGHER, CON_W
    h_goto_if_no CON_W, .Lcon_choose\@
.Lcon_go\@:
    h_msgbox (\t) + CL_PROCEED
    h_closemessage
    FadeOutBlackQ
    FadeWait
    BGMPush 30
    con_run CON_SLOT, CON_CAT, CON_RANK, CON_PLACE
    BGMPop 0, 60
    FadeInBlackQ
    FadeWait
    h_goto_if_ne CON_PLACE, 0, .Lcon_lost\@
    // ContestHall's winner: a new ribbon if this Pokémon hasn't won this rank, else Master Rank's Luxury Ball
    con_has_won CON_SLOT, CON_CAT, CON_RANK, CON_W
    h_goto_if_ne CON_W, 0, .Lcon_had\@
    con_give_ribbon CON_SLOT, CON_CAT, CON_RANK
    h_setflag FLAG_SYS_RIBBON_GET
    h_msgbox (\t) + CL_CONFER
    h_closemessage
    h_playfanfare SEQ_ME_ACCE
    WordSetPlayerName 0
    WordSetPartyPokeName 1, CON_SLOT
    h_msgbox_info (\t) + CL_RIBBON
    h_waitfanfare
    h_msgbox_info (\t) + CL_RIBBON_PUT
    h_release
.Lcon_had\@:
    h_goto_if_ne CON_RANK, 3, .Lcon_lost\@
    h_checkitemspace ITEM_LUXURY_BALL, 1, CON_W
    h_goto_if_eq CON_W, 0, .Lcon_later\@
    h_giveitem ITEM_LUXURY_BALL, 1
    h_msgbox (\t) + CL_AGAIN
    h_release
.Lcon_later\@:
    h_msgbox (\t) + CL_PICKUP
    h_setvar VAR_CONTEST_PRIZE_PICKUP, 4
    h_release
.Lcon_lost\@:
    h_msgbox (\t) + CL_AGAIN
    h_release
    .endm

// A person at a Berry Blender: people = 2, 3 or 4 with the player (pokeblocks.inc). The Bag on Berries as berry_planting.inc.
    .macro contest_blender t, people
    h_yesno (\t) + CL_BL_ASK, CON_W
    h_goto_if_no CON_W, .Lbl_no\@
    h_goto_if_unset FLAG_RECEIVED_POKEBLOCK_CASE, .Lbl_nocase\@
    con_has_berries CON_W
    h_goto_if_eq CON_W, 0, .Lbl_noberry\@
    con_case_space CON_W
    h_goto_if_eq CON_W, 0, .Lbl_full\@
    h_msgbox (\t) + CL_BL_PICK
    h_closemessage
    WorkSetConst CON_ITEM, 0
    FadeOutBlackQ
    FadeWait
    FieldClose
    CallBag 1, CON_W, CON_ITEM
    FieldOpen
    FadeInBlackQ
    FadeWait
    h_goto_if_eq CON_ITEM, 0, .Lbl_no\@
    con_berry_ok CON_ITEM, CON_W
    h_goto_if_eq CON_W, 0, .Lbl_cant\@
    FadeOutBlackQ
    FadeWait
    con_blend CON_ITEM, \people, CON_W
    FadeInBlackQ
    FadeWait
    h_release
.Lbl_cant\@:
    h_msgbox (\t) + CL_BL_CANT
    h_release
.Lbl_nocase\@:
    h_msgbox (\t) + CL_BL_NO_CASE
    h_release
.Lbl_noberry\@:
    h_msgbox (\t) + CL_BL_NO_BERRY
    h_release
.Lbl_full\@:
    h_msgbox (\t) + CL_BL_FULL
    h_release
.Lbl_no\@:
    h_msgbox (\t) + CL_BL_NO
    h_release
    .endm

#endif
