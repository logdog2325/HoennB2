// TEST ONLY (boats agent, 2026-10-07): Littleroot's town sign plays Black 2's 3D demos one after the other, with a
// 1 s look at the field between them (the separator in the test's frame sheets). Build with HOENN_TEST_CHBOATS=1
// (passed to every script by b2tools/patches/scripts.py as -D HOENN_TEST_CHBOATS=1). Never in normal builds.
// HOENN_TEST_CHBOATS=1: the boat demos (2 4 10 26 23 13), =2: the Ferris wheel (3) and the ids no Black 2 script
// plays (11 12 1; 0 is an empty table entry). Test from a cold-boot state of the ROM (common/boat.inc).
#ifdef HOENN_TEST_CHBOATS
    .macro tb_demo id
    FadeOutBlackQ
    FadeWait
    FieldClose
    Call3DDemo \id, 0
    FieldOpen
    FadeInBlackQ
    FadeWait
    VMSleep 30
    .endm
Test_Boats:
#if HOENN_TEST_CHBOATS == 1
    tb_demo 2
    tb_demo 4
    tb_demo 10
    tb_demo 26
    tb_demo 23
    tb_demo 13
#elif HOENN_TEST_CHBOATS == 2
    FadeOutBlackQ                       // the Ferris wheel (Nimbasa 1272.s: param = 9 + the partner)
    FadeWait
    FieldClose
    Call3DDemo 3, 9
    FieldOpen
    FadeInBlackQ
    FadeWait
    VMSleep 30
    tb_demo 11
    tb_demo 12
    tb_demo 1
#endif
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt
#endif
