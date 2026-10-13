// Events test start (test builds only: HOENN_TEST_CH13_EVENTS=1 with HOENN_TEST_CH13 and its Littleroot sign warps,
// scenes/ch13_test.inc; events agent, 2026-10-07). Inside ch13's Test_Ch13Start (every warp, once): the S.S. Ticket and
// Emerald's three tickets as their givers leave them (the item + FLAG_ENABLE_SHIP_*), 20 Master Balls for the battles.
// HOENN_TEST_CH13_EVENTS=2: the Master Balls only (to test the givers); 3: as 1, and Birth Island's triangle ignores
// the step limit (the test harness's walking is not step-exact). Never assembled into normal builds.
#include "hoenn_key_items.h"
    ItemAdd ITEM_MASTER_BALL, 20, HLIB_TMP
#if HOENN_TEST_CH13_EVENTS == 2
    h_clearflag FLAG_HIDE_STERN_SLATEPORT_HARBOR    // the givers where a real playthrough leaves them (Ch8, Mt. Chimney,
    h_clearflag FLAG_HIDE_PROF_COSMO_FALLARBOR      // Fallarbor's Pokemon Center): Ch13's test start does not set these
    h_clearflag FLAG_HIDE_LANETTE
#endif
#if HOENN_TEST_CH13_EVENTS == 1 || HOENN_TEST_CH13_EVENTS == 3
    ItemAdd ITEM_SS_TICKET, 1, HLIB_TMP
    h_setflag FLAG_RECEIVED_SS_TICKET
    h_setflag FLAG_ENCOUNTERED_LATIAS_OR_LATIOS     // (Sapphire's own Eon Ticket scene would come first at the harbor)
    ItemAdd ITEM_OLD_SEA_MAP, 1, HLIB_TMP
    h_setflag FLAG_ENABLE_SHIP_FARAWAY_ISLAND
    ItemAdd ITEM_AURORA_TICKET, 1, HLIB_TMP
    h_setflag FLAG_ENABLE_SHIP_BIRTH_ISLAND
    ItemAdd ITEM_MYSTIC_TICKET, 1, HLIB_TMP
    h_setflag FLAG_ENABLE_SHIP_NAVEL_ROCK
#endif
