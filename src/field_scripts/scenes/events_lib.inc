// The in-game event islands' shared pieces (events agent, 2026-10-07; notes/EVENTS.md): Emerald's Faraway Island,
// Birth Island and Navel Rock (pokeemerald data/maps/*, built as warp-only maps and caves) and the tickets to them.
// Macros and defines only (no labels). Needs hoenn_story.inc and scenes/ch13_lib.inc (the ferry: ch13_board_island,
// h_sail_ferry of hoenn_story.inc and ch2_land), which this file includes.
#ifndef EVENTS_LIB_INC
#define EVENTS_LIB_INC
#include "scenes/ch13_lib.inc"

// the way home: every island's sailor sails to Lilycove's harbor (Emerald: warp MAP_LILYCOVE_CITY_HARBOR, 8, 11), landing
// script 6 of 0406_room_LilycoveCity_Harbor.s (Ch13_LH_ArriveFromIsland: the fade in). Room origin (1, -2). Every crossing
// is h_sail_ferry (the boats agent: Black 2's ferry cutscene, demo 26).
#define EV_LILYCOVE_ZONE 203
#define EV_LILYCOVE_X (8 + 1)
#define EV_LILYCOVE_Z (11 - 2)
#define EV_LILYCOVE_ARRIVE 6
#define EV_TEMP 0x4001                  // Emerald's VAR_TEMP_1: Black 2's temporary work 0x4001 (0 after every map change)

// zones of the islands (data/hoenn_zones.json; warp-only maps: matrix tile = Emerald tile + the group's origin in
// world.json "standalone" (deterministic: b2tools/world.py group_layout))
#define EV_FARAWAY_ZONE 158             // FarawayIsland_Entrance, origin (15, 26)
#define EV_FARAWAY_OX 15
#define EV_FARAWAY_OZ 26
#define EV_BIRTH_ZONE 195               // BirthIsland_Exterior, origin (16, 18)
#define EV_BIRTH_OX 16
#define EV_BIRTH_OZ 18
#define EV_NAVEL_ZONE 232               // NavelRock_Exterior, origin (21, 22)
#define EV_NAVEL_OX 21
#define EV_NAVEL_OZ 22
#define EV_NAVEL_TOP_ZONE 233           // NavelRock_Top, origin (3, 2)
#define EV_NAVEL_TOP_OX 3
#define EV_NAVEL_TOP_OZ 2
#define EV_ARRIVE_SCRIPT 1              // every island's landing is script 1 of its scene (the ferry reserves it)

// the scaled levels (data/level_scaling.json curve, as ch13's Latios 50 -> 55 and Rayquaza 70 -> 78): Emerald's
// Mew 30, Deoxys 30, Lugia 70, Ho-Oh 70
#define EV_MEW_LEVEL 32
#define EV_DEOXYS_LEVEL 32
#define EV_LUGIA_LEVEL 78
#define EV_HO_OH_LEVEL 78

// Emerald's legendary encounter (seteventmon + special BattleSetup_StartLegendaryBattle + GetBattleOutcome) on Black 2's
// own (its Latios/Latias, 0304.s): CallWildBattle flag 1, WildBattleIsVictory (0 = lost: whiteout, the Pokemon stays for
// the next visit), the actor gone, CallWildBattleEnd, then WildBattleGetResult (ov012 GetWildBattleResultByCombined,
// table 0x0216dd1c: battle result 5 caught -> 0, 1 won -> 2, ran/other -> 1). Caught: caught flag + hide flag. Defeated:
// defeated flag + hide flag + Emerald's "The X flew away!" (Common_EventScript_LegendaryFlewAway; line `flew`, buffer 1 =
// the species). Ran: the line only; the island's zone init shows it again next time (Emerald's TryShow... scripts).
    .macro ev_legend_battle species, level, uid, hide, caught, defeated, flew
    CallWildBattle \species, \level, 1
    WildBattleIsVictory HLIB_TMP
    WorkCmpConst HLIB_TMP, 1
    VMJumpIf CMP_EQ, .Lelb_won\@
    CallWildLose
    VMHalt
.Lelb_won\@:
    ActorDelete \uid
    CallWildBattleEnd
    WildBattleGetResult HLIB_TMP
    WorkCmpConst HLIB_TMP, 0
    VMJumpIf CMP_NE, .Lelb_notcaught\@
    FlagSet \caught
    FlagSet \hide
    VMJump .Lelb_done\@
.Lelb_notcaught\@:
    WorkCmpConst HLIB_TMP, 2
    VMJumpIf CMP_NE, .Lelb_ran\@
    FlagSet \defeated
    FlagSet \hide
.Lelb_ran\@:
    WordSetPokeSpecies 1, \species
    SystemMsg \flew, 2
    LastKeyWait
    MsgWinCloseAll
.Lelb_done\@:
    .endm

// the island sailor's goodbye (Emerald FarawayIsland_Entrance / BirthIsland_Harbor / NavelRock_Harbor _EventScript_Sailor):
// "Do you want to return to Lilycove?" YES -> "Aye, right, then! Sail home we will!", the sailor turns to the ferry and is
// gone (Common_EventScript_FerryDepartIsland), the crossing to Lilycove; NO -> "Aye, right, as you like, then."
    .macro ev_island_sailor uid, ask, home, stay
    h_lock
    SEPlay SEQ_SE_MESSAGE
    h_faceplayer
    h_yesno \ask, HLIB_TMP
    h_goto_if_no HLIB_TMP, .Leis_stay\@
    h_msgbox \home
    ch13_board_island \uid
    h_sail_ferry EV_LILYCOVE_ZONE, EV_LILYCOVE_X, EV_LILYCOVE_Z, 0, EV_LILYCOVE_ARRIVE
    h_release
.Leis_stay\@:
    h_msgbox \stay
    h_release
    .endm
// Lilycove Harbor's event-ticket lines and works (scenes/LilycoveCity_Harbor_Events.inc; used by ch13's attendant too)
#define EV_LH_T 19
// EV_LH_T +0 "Is it you who brought that odd ticket? ... Get on board, youngster!"   +1 "The ferry to Slateport is... Can
//      we sail to this place on the map? ... Please wait."   +2 "What's up, youngster? ... I'm afraid I can't help you..."
//      +3 "Briney: Hold on a second! ..."   +4 "<player>, I'm terribly sorry. ... Let's find this island on this Old Sea Map!"
//      +5 "Is it you who brought those odd tickets? ... Where shall we sail first?"   +6/+7/+8 Navel Rock / Birth Island /
//      Faraway Island   +9 "Aye, right, as you like, then."   +10 Southern Island (Emerald only: src/text/emerald/
//      overrides_postgame_fix.json appends it)
#define EV_LH_BRINEY 5
#define EV_LH_MYSTIC 0x8034                 // Emerald VAR_TEMP_9: Mystic Ticket 0 none, 1 held, 2 held and not shown yet
#define EV_LH_AURORA 0x8035                 // VAR_TEMP_D: Aurora Ticket
#define EV_LH_MAP 0x8036                    // VAR_TEMP_C: Old Sea Map
#define EV_LH_EON 0x8037                    // VAR_TEMP_E: Eon Ticket (Emerald only; Sapphire/Ruby keep their one-time trip)
#define EV_LH_FIRST 0x8038                  // VAR_TEMP_B: the tickets shown for the first time (Eon 1, Aurora 2, Mystic 8; Emerald)
#endif
