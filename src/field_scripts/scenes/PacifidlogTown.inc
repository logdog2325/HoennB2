// Pacifidlog Town's story (Sapphire data/maps/PacifidlogTown/scripts.inc; chapter Ch12, ch6 agent 2026-10-07). converter/
// gen_map_content.py includes this file twice in the generated zone file 0916_auto_PacifidlogTown.s: the entry below
// becomes script 1, the generated people and signs follow. Map scripts: scenes/PacifidlogTown_init.inc.
// Not ported: OnResume's setstepcallback 3 (Pacifidlog's floating log bridges bob under your steps; Black 2 has no such
// step callback). The town's people and its signs are the generator's (Sapphire's one-message scripts).
#ifdef SCENE_ENTRIES
    ScriptEntry PT_Init                     // 1: PacifidlogTown_OnTransition (zone init)
#else
PT_Init:
#if defined(HOENN_TEST_CH6) || defined(HOENN_TEST_CH12)
    VMCall Test_Ch6Start                    // test builds only (scenes/ch6_test.inc: chapter Ch12 starts here)
#endif
    h_setflag FLAG_VISITED_PACIFIDLOG_TOWN  // the fly point
    VMHalt
    .balign 4, 0
#include "scenes/ch6_test.inc"
#endif
