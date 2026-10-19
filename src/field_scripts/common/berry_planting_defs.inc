// Berry planting (HOENN_BERRY_PLANTING; notes/BERRY_PLANTING.md): the names and macros of common/berry_planting.inc,
// included at the top of 1241_hidden_items.s (the tree zones' init scripts there use BerryCmd too).
// The specials are script command 612 (b2tools/patches/berries.c Berry_Cmd): BerryCmd op, arg. Results in local works:
#define BT_STAGE   0x8004      /* stage 0 soil, 1 planted, 2 sprouted, 3 taller, 4 flowering, 5 berries (VAR_0x8004) */
#define BT_WATER   0x8005      /* times watered (VAR_0x8005) */
#define BT_YIELD   0x8006      /* berries on the tree (VAR_0x8006) */
#define BT_ITEM    0x8007      /* the tree's berry (Black 2 item) */
#define BT_REFRESH 0x8008      /* 1: the actor's picture is not the tree's any more */
#define BT_UID     0x8009      /* the tree actor's uid */
#define BT_TMP     0x800a
#define BT_RESULT  0x800b
#define BT_CHOICE  0x800c      /* the item picked in the Bag (BT_ITEM is the tree's berry again after each op) */
#define BT_OP_GET 0
#define BT_OP_PLANT 1
#define BT_OP_WATER 2
#define BT_OP_PICK 3
#define BT_OP_HAS_BERRIES 4
#define BT_OP_BAG_POCKET 5
#define BT_OP_UPDATE 6
// Lines of script text 208 (src/text/script/0208_*.txt): 28-33 the daily berry lines (Sapphire's), 34-45 these
// (src/text/berries/overrides_berry_planting.json, packed only with the switch).
#define BT_T_SOIL 28           /* It's soft, loamy soil. */
#define BT_T_PICK 29           /* There are {2} {1}! Do you want to pick the {1}? (plural) */
#define BT_T_PICKED 30
#define BT_T_PUTAWAY 31
#define BT_T_FULL 32
#define BT_T_LEFT 33
#define BT_T_WANTPLANT 34
#define BT_T_PLANTED 35
#define BT_T_STAGE1 36
#define BT_T_STAGE2 37
#define BT_T_STAGE3 38
#define BT_T_CUTELY 39
#define BT_T_PRETTILY 40
#define BT_T_BEAUTIFULLY 41
#define BT_T_WANTWATER 42
#define BT_T_WATERED 43
#define BT_T_DELIGHTED 44
#define BT_T_CANTPLANT 45

    .macro BerryCmd op, arg
    FieldCommand 612
    .2byte \op
    .2byte \arg
    .endm

    .macro bt_goto_if_eq var, value, label
    WorkCmpConst \var, \value
    VMJumpIf CMP_EQ, \label
    .endm
    .macro bt_goto_if_ne var, value, label
    WorkCmpConst \var, \value
    VMJumpIf CMP_NE, \label
    .endm
