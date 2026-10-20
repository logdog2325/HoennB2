// postgame_fix test start (test builds only: HOENN_TEST_CHPGFIX=1 with HOENN_TEST_CHPOSTGAME; postgame_fix 2026-10-19). Included by
// scenes/postgame_test.inc in Test_PG_Start (once): the three rods and TM94 Rock Smash for the Safari Zone tests. The ticket
// combinations, the defeated / caught / shown flags and the Hall of Fame tests set their flags from the test driver (RAM: the
// GameData's event work, work/agents/postgame_fix/tests/lib_pgf.py). Never assembled into normal builds.
    ItemAdd ITEM_OLD_ROD, 1, HLIB_TMP
    ItemAdd ITEM_GOOD_ROD, 1, HLIB_TMP
    ItemAdd ITEM_SUPER_ROD, 1, HLIB_TMP
    ItemAdd ITEM_TM94, 1, HLIB_TMP
