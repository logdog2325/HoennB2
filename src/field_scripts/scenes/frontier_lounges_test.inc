// frontier_lounges test kit (test builds only: HOENN_TEST_CHFRLOUNGES=1 with HOENN_TEST_CHPOSTGAME=1; included by
// scenes/postgame_test.inc in its once-only start state, the sign's event script, never a zone init): 200 Battle Points and
// all seven Silver Symbols (record key FR_SYMBOLS = bit 2f per facility), so the Gambler takes bets, Scott gives the Lansat
// Berry and the tutors teach. Raw FrOp (command 232) as hoenn_frontier.inc's fr_add_bp / fr_set, which Littleroot's
// script does not include. 0x8048 = hoenn_frontier.inc's FR_T0.
    WorkSetConst 0x8048, 200
    FieldCommand 232                    // FrOp FR_OP_ADD_BP, FR_T0
    .2byte 0x200
    .2byte 0x8048
    WorkSetConst 0x8048, 0x1555
    FieldCommand 232                    // FrOp FR_OP_SET | FR_SYMBOLS, FR_T0
    .2byte 0x106
    .2byte 0x8048
