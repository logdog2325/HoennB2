// Chapter Ch13's part of the game-clear flags (Sapphire data/scripts/hall_of_fame.inc EverGrandeCity_HallOfFame_
// EventScript_SetGameClearFlags: the calls ReadyReceiveSSTicketEvent, ReadyLatiTVEvent, ShowStevensBeldum, ShowHM08 and
// their four labels; ch13 agent, 2026-10-07). Chapter Ch11's Hall of Fame (the room with the Champion's credits) runs
//     VMCall Sub_Ch13_GameClear
// where Sapphire runs those four calls, and includes this file at the END of its script file (code with labels comes
// after the scripts), both guarded because the lead commits chapters one at a time:
//     #if __has_include("scenes/ch13_gameclear.inc")
//         VMCall Sub_Ch13_GameClear
//     #endif
//     ...
//     #if __has_include("scenes/ch13_gameclear.inc")
//     #include "scenes/ch13_gameclear.inc"
//     #endif
// Everything here is flags, works and a map replacement, which every script level allows (notes/STORY_COMMON.md "Map-script
// permissions"), so it can run from the Hall of Fame script or from a zone init.
// What it does, in Sapphire's order:
//  - unless FLAG_RECEIVED_SS_TICKET: VAR_LITTLEROOT_HOUSES_STATE(_2) = 3 and Norman appears in the house
//    (clearflag FLAG_HIDE_NORMAN_LITTLEROOT): the player's house plays the S.S. Ticket scene (scenes/players_house_1f_ch13.inc);
//  - unless FLAG_LATIOS_OR_LATIAS_ROAMING: FLAG_SYS_TV_LATI (the Lati news; see notes/STORY_HANDOFFS.md "From ch13");
//  - unless FLAG_RECEIVED_BELDUM: Steven's Poké Ball with Beldum appears (FLAG_HIDE_BELDUM_BALL_STEVENS_HOUSE cleared);
//  - unless FLAG_RECEIVED_HM08: the Dive ball in Steven's house appears (FLAG_ITEM_MOSSDEEP_STEVENS_HOUSE_HM08 cleared);
//  - not Sapphire's script but its OnTransition of Route 131 (FLAG_SYS_GAME_CLEAR -> layout 320): Black 2 swaps a map chunk
//    set by map replace event 7 (scenes/Route131.inc does the same on a warp into Route 131), so the Sky Pillar islet is
//    already there when the player sails to Route 131 after the credits.
// The Eon Ticket (Southern Island, Latios) is an event item in Sapphire (a Mystery Event gives ITEM_EON_TICKET and sets
// FLAG_SYS_HAS_EON_TICKET; no script gives it). By default (CH13_EON_TICKET_GIFT 0) nothing here gives it, like Sapphire; with
// `#define CH13_EON_TICKET_GIFT 1` before this file the Hall of Fame puts Black 2's Liberty Pass (the Eon Ticket) in the Bag.
// FLAG_LATIOS_OR_LATIAS_ROAMING has no id (S_optional: Black 2 has no roamer command; notes/STORY_HANDOFFS.md): the Lati
// news is therefore shown once (FLAG_SYS_TV_LATI is cleared by the TV).
#ifndef CH13_GAMECLEAR_INC
#define CH13_GAMECLEAR_INC
#include "hoenn_key_items.h"
#define CH13_MAP_REPLACE_SKY_PILLAR 7
#ifndef CH13_EON_TICKET_GIFT
#define CH13_EON_TICKET_GIFT 0   // 1 = the Hall of Fame also puts the Eon Ticket in the Bag (see below); 0 = Sapphire: an event item
#endif

Sub_Ch13_GameClear:
    VMStackPushFlag FLAG_RECEIVED_SS_TICKET        // call_if_unset FLAG_RECEIVED_SS_TICKET, ReadyReceiveSSTicketEvent
    VMStackPushConst 1
    VMStackCmp CMP_NE                              // (jumps when the comparison is false: the flag is set)
    VMJumpIf CMP_STACK, L_Ch13GC_Ticket
    WorkSetConst VAR_LITTLEROOT_HOUSES_STATE, 3
    WorkSetConst VAR_LITTLEROOT_HOUSES_STATE_2, 3
    FlagReset FLAG_HIDE_NORMAN_LITTLEROOT
L_Ch13GC_Ticket:
#ifndef HOENN_EMERALD
    FlagSet FLAG_SYS_TV_LATI                       // ReadyLatiTVEvent (FLAG_LATIOS_OR_LATIAS_ROAMING is never set)
#endif
    // Emerald (emerald_ch11_gameclear): no TV news waiting. Its Lati broadcast is part of Mom's S.S. Ticket scene in the
    // house (scenes/emerald/players_house_1f_ch13.inc: the colour question starts the roamer), so FLAG_SYS_TV_LATI stays clear
    VMStackPushFlag FLAG_RECEIVED_BELDUM           // call_if_unset FLAG_RECEIVED_BELDUM, ShowStevensBeldum
    VMStackPushConst 1
    VMStackCmp CMP_NE
    VMJumpIf CMP_STACK, L_Ch13GC_Beldum
    FlagReset FLAG_HIDE_BELDUM_BALL_STEVENS_HOUSE
L_Ch13GC_Beldum:
    VMStackPushFlag FLAG_RECEIVED_HM08             // call_if_unset FLAG_RECEIVED_HM08, ShowHM08
    VMStackPushConst 1
    VMStackCmp CMP_NE
    VMJumpIf CMP_STACK, L_Ch13GC_HM08
    FlagReset FLAG_ITEM_MOSSDEEP_STEVENS_HOUSE_HM08
L_Ch13GC_HM08:
#if CH13_EON_TICKET_GIFT
    VMStackPushFlag FLAG_SYS_HAS_EON_TICKET        // the Eon Ticket (Sapphire: given by a Mystery Event, never by a script)
    VMStackPushConst 1
    VMStackCmp CMP_NE
    VMJumpIf CMP_STACK, L_Ch13GC_Eon
    ItemAdd ITEM_EON_TICKET, 1, 0x8030             // (ITEM_EON_TICKET = Black 2's Liberty Pass, src/include/hoenn_key_items.h)
    FlagSet FLAG_SYS_HAS_EON_TICKET
L_Ch13GC_Eon:
#endif
    MapReplaceSetEvent CH13_MAP_REPLACE_SKY_PILLAR, 1, 0   // Route131_MapScript1_152444 (setmaplayoutindex 320)
    VMReturn
#endif
