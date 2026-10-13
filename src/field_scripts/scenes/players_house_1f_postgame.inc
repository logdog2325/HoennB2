// Sapphire's Lati news on the player's TV (postgame_scripts, 2026-10-07): pokeruby data/scripts/tv.inc Event_TV ->
// EventScript_1A6F0B (special CheckForBigMovieOrEmergencyNewsOnTV = 1: in the player's own house 1F with
// FLAG_SYS_TV_LATI, set by the Hall of Fame: scenes/ch13_gameclear.inc): the news bulletin (Sapphire: a red Flying
// Pokémon = Latias), special InitRoamer (pg_roamer_start PG_LATIAS: b2tools/patches/roamers.py), clearflag
// FLAG_SYS_TV_LATI, setflag FLAG_LATIOS_OR_LATIAS_ROAMING. Sub_PG_TVNews is called by the TV (Script_6 of 0780 / 0784,
// guarded): work 0x8030 = 1 when it showed the news (the TV's own line is then skipped), 0 otherwise. Included at the
// end of 0780_brendans_house_1f.s / 0784_mays_house_1f.s after their HOUSE_BRENDAN define; raw commands (the house
// files do not include hoenn_story.inc). Text: line 35 of src/text/script/0619_brendans_house_1f.txt /
// 0621_mays_house_1f.txt (Sapphire's UnknownString_8172D30).
// Black 2's TVs are models without a screen: Sapphire's flashing TV (the news waiting) is not shown.
#include "scenes/postgame_lib.inc"
#define PGH_T_LATI_NEWS 35
#define PGH_TMP 0x8030

Sub_PG_TVNews:
    WorkSetConst PGH_TMP, 0
    VMStackPushFlag FLAG_SYS_TV_LATI                // goto_if_unset FLAG_SYS_TV_LATI: Black 2's TV line
    VMStackPushConst 1
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_PGH_Done
    TrainerCardGetSex PGH_TMP                       // only in the player's own house (the rival's: the TV line)
#if HOUSE_BRENDAN
    WorkCmpConst PGH_TMP, 1
#else
    WorkCmpConst PGH_TMP, 0
#endif
    VMJumpIf CMP_EQ, L_PGH_NotShown
    WorkSetConst PGH_TMP, 0
    VMStackPushFlag FLAG_LATIOS_OR_LATIAS_ROAMING   // (Sapphire's Hall of Fame sets the news only before that)
    VMStackPushConst 1
    VMStackCmp CMP_NE
    VMJumpIf CMP_STACK, L_PGH_Seen
    SEPlay SEQ_SE_MESSAGE
    SystemMsg PGH_T_LATI_NEWS, 2                    // We bring you a special news bulletin. ... a red Flying Pokémon ...
    LastKeyWait
    MsgWinCloseAll
    pg_roamer_start PG_LATIAS                       // special InitRoamer
    FlagSet FLAG_LATIOS_OR_LATIAS_ROAMING
    WorkSetConst PGH_TMP, 1
L_PGH_Seen:
    FlagReset FLAG_SYS_TV_LATI
L_PGH_Done:
    VMReturn
L_PGH_NotShown:
    WorkSetConst PGH_TMP, 0
    VMReturn
