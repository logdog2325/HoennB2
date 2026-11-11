// The DexNav (notes/DEXNAV.md): row 0x60-0x7F of the extension command 0x15F (decomp include/hoennb2/dexnav.h,
// src/hoennb2/resident/dexnav.c HoennB2_Ext_DexNav) and what Birch's Lab and Route 101's tutorial share. Only built with
// our C (HOENN_DEXNAV, b2tools/patches/scripts.py).
#ifndef HOENN_DEXNAV_DEFS
#define HOENN_DEXNAV_DEFS

// Every DexNav line is in Route 101's script text file (a/0/0/3 file 516; src/text/overrides_dexnav.json): the Lab shows
// them with ActorMsg DN_TEXT / dn_info, which read any file of the archive
#define DN_TEXT 516
#define DN_RIVAL 248                    // the rival's actor (uid 0xf8, made by DN_OP_RIVAL_SPAWN)
#define DN_W_A 0x8004
#define DN_W_DIR 0x8005
#define DN_W_N 0x8006
#define DN_W_GAVE 0x8007                // Birch's talk (0792 Script_7): 1 when the DexNav was just given (scenes/BirchLab_DexNav.inc)

// VAR_DEXNAV_STATE (decomp include/hoennb2/dexnav.h DEXNAV_STATE_*)
#define DN_STATE_NONE 0
#define DN_STATE_TUTORIAL 1             // given: Route 101's grass starts the tutorial (dexnav.c, the first step in it)
#define DN_STATE_TUTORIAL_SEARCH 2
#define DN_STATE_DONE 3
#define DN_STATE_TUTORIAL_KO 4          // the tutorial battle's result, for Route 101's script 5
#define DN_STATE_TUTORIAL_CAUGHT 5
#define DN_STATE_TUTORIAL_RAN 6

// The ops
#define DN_OP_TUTORIAL_SEARCH 0         // var = 1 when the tutorial's Poochyena is out (shaking grass 2-5 steps away)
#define DN_OP_RIVAL_SPAWN 1             // var = the rival's steps to the player (1-3), 0xffff: no room for it
#define DN_OP_RIVAL_DELETE 2
#define DN_OP_SPOT_DIR 3                // var = the way to the hidden Pokémon (0 up, 1 down, 2 left, 3 right), 0xffff
#define DN_OP_RIVAL_PRESENT 4           // var = 1 when the rival stands in the zone
#define DN_OP_RIVAL_INFO 5              // a = 0: the way it walks to the player; 1: its steps; 2: the way back (0xffff: none)
#define DN_OP_INFO_MSG 6                // the info window (InfoMsg's) with line b of text file a (close: InfoMsgClose_0039)
#define DN_OP_SCREEN_REFRESH 7          // the touch screen made again behind its wipe: the DexNav shows at once

// Route 101's text (file 516; NEW lines, approved by the user 2026-11-09: src/text/overrides_dexnav.json)
#define DN_T_BIRCH_GIVE 7
#define DN_T_RECEIVED 8
#define DN_T_BIRCH_EXPLAIN_MAY 9        // a boy's rival is May
#define DN_T_BIRCH_EXPLAIN_BRENDAN 10
#define DN_T_INTRO_MAY 11
#define DN_T_INTRO_BRENDAN 12
#define DN_T_NO_BALLS_MAY 13
#define DN_T_NO_BALLS_BRENDAN 14
#define DN_T_EXPLAIN_MAY 15
#define DN_T_EXPLAIN_BRENDAN 16
#define DN_T_GO_MAY 17
#define DN_T_GO_BRENDAN 18
#define DN_T_GO_NO_RIVAL 19
#define DN_T_CAUGHT_MAY 20
#define DN_T_CAUGHT_BRENDAN 21
#define DN_T_KO_MAY 22
#define DN_T_KO_BRENDAN 23
#define DN_T_RAN_MAY 24
#define DN_T_RAN_BRENDAN 25

    .macro DexNavCmd op, a, b, var
    FieldCommand 351
    .byte 0x60 + \op
    .2byte \a
    .2byte \b
    .2byte \var
    .endm

// The info window with a DexNav line, waiting for A (as h_msgbox_info, from Route 101's file)
    .macro dn_info line
    DexNavCmd DN_OP_INFO_MSG, DN_TEXT, \line, DN_W_A
    LastKeyWait
    InfoMsgClose_0039
    .endm

// A DexNav line said by an actor (ActorMsg reads any file of the archive)
    .macro dn_msg_actor line, actor
    ActorMsg DN_TEXT, \line, \actor, 0, 0
    LastKeyWait
    .endm
#endif
