// Secret Bases (notes/SECRET_BASES.md): row 0x40-0x5F of the extension command 0x15F (decomp include/hoennb2/ext_cmd.h,
// src/hoennb2/resident/secret_base.c) and the macros any zone's script uses to reach the decorations.
#ifndef HOENN_SECRET_BASE_DEFS
#define HOENN_SECRET_BASE_DEFS
#define SB_W_A 0x8004
#define SB_W_B 0x8005
#define SB_W_C 0x8006
#define SB_W_D 0x8007
#define SB_W_ARG 0x8010
#define SB_W_LIST 0x8011
#define SB_W_RES 0x8012

#define SB_GLOBAL_SPOT 10735
#define SB_GLOBAL_PC 10736
#define SB_GLOBAL_ANSWER 10737
#define SB_GLOBAL_ROOM_DECOR 10738
#define SB_GLOBAL_SHOP 10739
#define SB_GLOBAL_GIVE 10740
#define SB_GLOBAL_FIRST 10741
#define SB_GLOBAL_JUMP 10742
#define SB_GLOBAL_SPIN 10743
#define SB_GLOBAL_LEAVE 10744
#define SB_GLOBAL_HAS_ROOM 10745

// The ops (decomp src/hoennb2/secret_base/sb_main.c)
#define SB_OP_UNLOAD 0
#define SB_OP_ENTER 1
#define SB_OP_SPOT 2
#define SB_OP_MAKE 3
#define SB_OP_MOVE_OUT 4
#define SB_OP_CATEGORIES 5
#define SB_OP_ITEMS 6
#define SB_OP_SLOT_CHECK 7
#define SB_OP_CANT_ROOM 8
#define SB_OP_TOSS 9
#define SB_OP_PLACE_BEGIN 10
#define SB_OP_CURSOR 11
#define SB_OP_CURSOR_END 12
#define SB_OP_CAN_PLACE 13
#define SB_OP_PLACE 14
#define SB_OP_PUTAWAY_BEGIN 15
#define SB_OP_PUTAWAY_AT 16
#define SB_OP_PUTAWAY 17
#define SB_OP_WORD 18
#define SB_OP_GIVE 19
#define SB_OP_HAS_ROOM 20
#define SB_OP_SHOP 21
#define SB_OP_PRICE 22
#define SB_OP_AT_FRONT 23
#define SB_OP_HIDE_FRONT 24
#define SB_OP_LEAVE 25
#define SB_OP_BP_CHECK 26
#define SB_OP_BP_PAY 27
#define SB_OP_BASE_PLACE_WORD 28
#define SB_OP_SHOP_IS_BP 29
#define SB_OP_BP_WORD 30
#define SB_OP_ROOM_MAX 31

// The decoration shops' lists (decomp include/hoennb2/secret_base_data.h sSBShops)
#define SB_SHOP_SR_SLATEPORT_DOLLS 0
#define SB_SHOP_SR_SLATEPORT_1 1
#define SB_SHOP_SR_SLATEPORT_2 2
#define SB_SHOP_SR_FORTREE_DESKS 3
#define SB_SHOP_SR_FORTREE_CHAIRS 4
#define SB_SHOP_SR_FLOWER 5
#define SB_SHOP_SR_5F_FAR_LEFT 6
#define SB_SHOP_SR_5F_MID_LEFT 7
#define SB_SHOP_SR_5F_MID_RIGHT 8
#define SB_SHOP_SR_5F_FAR_RIGHT 9
#define SB_SHOP_SR_ROOFTOP 10
#define SB_SHOP_EM_SLATEPORT_DOLLS 11
#define SB_SHOP_EM_SLATEPORT 12
#define SB_SHOP_EM_FORTREE_DESKS 13
#define SB_SHOP_EM_FORTREE_CHAIRS 14
#define SB_SHOP_EM_FLOWER 15
#define SB_SHOP_EM_5F_DOLLS 16
#define SB_SHOP_EM_5F_CUSHIONS 17
#define SB_SHOP_EM_5F_POSTERS 18
#define SB_SHOP_EM_5F_MATS 19
#define SB_SHOP_EM_ROOFTOP 20
#define SB_SHOP_EM_EXCHANGE_1 21
#define SB_SHOP_EM_EXCHANGE_2 22

    .macro SBCmd op, arg
    FieldCommand 351
    .byte 0x40 + \op
    .2byte \arg
    .endm

// Opens a shop's menu (the message window of "How may I serve you?" may stay open): the clerk's own script says the lines
    .macro sb_shop list
    VMStackPush 0x8010
    WorkSetConst 0x8010, \list
    RTCallGlobal SB_GLOBAL_SHOP
    VMStackPop 0x8010
    .endm

// givedecoration: "Obtained the ...!" with the jingle, or "no room" (Std_ObtainDecoration); var = 1 given, 0 no room
    .macro sb_givedecoration decor, var
    VMStackPush 0x8010
    VMStackPush 0x8012
    WorkSetConst 0x8010, \decor
    RTCallGlobal SB_GLOBAL_GIVE
    WorkSet \var, 0x8012
    VMStackPop 0x8012
    VMStackPop 0x8010
    .endm

// checkdecorspace: var = 1 when the decoration fits in its category's slots
    .macro sb_checkdecorspace decor, var
    VMStackPush 0x8010
    VMStackPush 0x8012
    WorkSetConst 0x8010, \decor
    RTCallGlobal SB_GLOBAL_HAS_ROOM
    WorkSet \var, 0x8012
    VMStackPop 0x8012
    VMStackPop 0x8010
    .endm

// ... of a decoration in a work
    .macro sb_givedecoration_var work, var
    VMStackPush 0x8010
    VMStackPush 0x8012
    WorkSet 0x8010, \work
    RTCallGlobal SB_GLOBAL_GIVE
    WorkSet \var, 0x8012
    VMStackPop 0x8012
    VMStackPop 0x8010
    .endm
#endif
