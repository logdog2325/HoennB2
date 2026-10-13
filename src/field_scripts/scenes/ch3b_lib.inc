// Chapter 3 part 3b helpers (ch3b agent, 2026-10-07): macros and script works only (no code). Include after
// "hoenn_story.inc" (scene bodies and room files of Route 110, Mauville, Route 117, Verdanturf). Builds on ch3a's
// scenes/ch3_lib.inc (c3_talk, c3_say_turn_back, c3_mart_sub, c3_lead_mon; works 0x8032-0x8036).
#ifndef CH3B_LIB_INC
#define CH3B_LIB_INC
#include "scenes/ch3_lib.inc"

// script works of 3b's scripts (0x8030/0x8031 = hoenn_story.inc, 0x8032-0x8036 = ch3_lib.inc)
#define C3B_A 0x8037
#define C3B_B 0x8038
#define C3B_X 0x8039
#define C3B_Z 0x803A
#define C3B_SEL 0x803B

// a person that says one line (MSGBOX_DEFAULT after lock + faceplayer) and stays facing the player
    .macro c3b_say n
    c3_talk
    h_msgbox \n
    h_release
    .endm

// one line in a signpost window, the script stays open for more (lockall + msgbox MSGBOX_DEFAULT of a bg event)
    .macro c3b_sign_line n
    MsgPlaceSign \n, 2
    .endm
#endif
