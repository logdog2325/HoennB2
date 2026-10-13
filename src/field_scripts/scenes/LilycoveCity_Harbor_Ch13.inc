// Lilycove Harbor's ferry attendant (Sapphire data/maps/LilycoveCity_Harbor/scripts.inc, LilycoveCity_Harbor_EventScript_
// FerryAttendant ... FerryAttendantLocationAndBoarding; chapter Ch13, ch13 agent 2026-10-07). Included by
// 0406_room_LilycoveCity_Harbor.s (guarded) in place of its fallback; replaces the label Ch13_LH_FerryAttendant (script 2,
// object 1, hidden by FLAG_HIDE_FERRY_ATTENDANT_LILYCOVE which is not set at new game, data/story/ch8a.json). Text: lines
// 4-18 of 0261 (LH13_T + n, below); T_FerryUnavailable is the room file's own line 1. Scripts 4-6 (room file entries) are
// the landings from Slateport, the Battle Tower and Southern Island.
// The crossings are scenes/ch13_lib.inc's (Black 2 has no ship to ride and the S.S. Tidal's rooms are not built).
// Eon Ticket (Sapphire's Mystery Event item, ITEM_EON_TICKET = Black 2's Liberty Pass in the Bag + FLAG_SYS_HAS_EON_TICKET):
// the attendant takes the player to Southern Island once, after the game is cleared, as Sapphire: the ferry sailor of
// object 4 (uid 4, hidden by FLAG_HIDE_FERRY_SAILOR_LILYCOVE) takes the attendant's place, the party is healed and the
// landing is scene script 3 of scenes/SouthernIsland_Exterior.inc. How the ticket reaches the player: CH13_EON_TICKET_GIFT in
// scenes/ch13_gameclear.inc (off by default: in Sapphire it is a Mystery Event item no script gives).
#include "scenes/ch13_lib.inc"
#if __has_include("scenes/events_lib.inc")
#include "scenes/events_lib.inc"            // (events agent) Emerald's event tickets and islands
#endif
#define LH13_T 4
// LH13_T +0 "Hello, are you here for the ferry? May I see your Ticket?"  +1 "<player> doesn't have the Ticket..."
//        +2 "<player> flashed the Ticket. ... where would you like to go?"  +3 "Slateport City it is, then!"
//        +4 "Battle Tower it is, then!"  +5 "Then, where would you like to go?"  +6 "Please board the ferry and wait for departure."
//        +7 "Please sail with us another time!"  +8/+9/+10 Slateport / Battle Tower / Cancel
//        +11 "We hope you enjoy your voyage on our ferry."  +12 "We have made land in Lilycove City. ..."
//        +13 "The ferry to Slateport is... Oh? That Pass..."  +14 "Aye, mate, are you the one who brought that mighty odd Pass? ..."
#define LH13_ATTENDANT 1
#define LH13_SAILOR 4
#define LH13_SH_ZONE 17                  // BattleTower_Outside (matrix tile = Sapphire tile + (17, 18))
#define LH13_SI_ZONE 111                 // SouthernIsland_Exterior (matrix tile = Sapphire tile + (15, 18))
#define LH13_HB_ZONE 596                 // SlateportCity_Harbor (room origin (1, -2))

Ch13_LH_FerryAttendant:                 // LilycoveCity_Harbor_EventScript_FerryAttendant
    h_lock
    SEPlay SEQ_SE_MESSAGE
    h_faceplayer
    h_buffer_player
    h_checkitem ITEM_EON_TICKET, 1, HLIB_TMP
    h_goto_if_eq HLIB_TMP, 1, L_LH13_EonTicketPossible
L_LH13_FerryUnavailable:
#ifdef EVENTS_LIB_INC
    h_goto_if_set FLAG_SYS_GAME_CLEAR, L_EV_LH_EventTickets   // (events agent) Emerald's Old Sea Map / Aurora / Mystic Ticket
#else
    h_goto_if_set FLAG_SYS_GAME_CLEAR, L_LH13_NoFirstTimeEventTickets
#endif
    h_msgbox T_FerryUnavailable         // I beg your pardon? You're looking for a ship? ... the ferry service isn't available at present...
    h_release
L_LH13_NoFirstTimeEventTickets:
    h_msgbox LH13_T + 0                 // Hello, are you here for the ferry? May I see your Ticket?
    h_checkitem ITEM_SS_TICKET, 1, HLIB_TMP
    h_goto_if_eq HLIB_TMP, 0, L_LH13_NoTicket
    ParentActorMsg MSGFILE_SCRIPT, LH13_T + 2, 0, 0     // <player> flashed the Ticket. Perfect! ... And where would you like to go?
L_LH13_RegularLocationSelect:
    ListMenu_AnchorTopRight 31, 6, 0, 1, HLIB_TMP      // multichoicedefault 18, 6, 56 (SLATEPORT / BATTLE TOWER / CANCEL), 2, 0
    ListMenuAdd LH13_T + 8, 65535, 0
    ListMenuAdd LH13_T + 9, 65535, 1
#ifdef EVENTS_LIB_INC
    VMCall Sub_EV_LH_TicketStates       // (events agent) Emerald's ScriptMenu_CreateLilycoveSSTidalMultichoice, 0x8004 = 0:
    h_goto_if_eq EV_LH_MYSTIC, 0, .Lev_rm1   // the islands of the tickets you hold (Southern Island stays Sapphire's
    ListMenuAdd EV_LH_T + 6, 65535, 3   //   one-time trip above)
.Lev_rm1:
    h_goto_if_eq EV_LH_AURORA, 0, .Lev_rm2
    ListMenuAdd EV_LH_T + 7, 65535, 4
.Lev_rm2:
    h_goto_if_eq EV_LH_MAP, 0, .Lev_rm3
    ListMenuAdd EV_LH_T + 8, 65535, 5
.Lev_rm3:
#endif
    ListMenuAdd LH13_T + 10, 65535, 2
    ListMenuShow
    h_goto_if_eq HLIB_TMP, 0, L_LH13_GoToSlateport
    h_goto_if_eq HLIB_TMP, 1, L_LH13_GoToBattleTower
#ifdef EVENTS_LIB_INC
    h_goto_if_eq HLIB_TMP, 3, L_EV_LH_GoToNavelRock
    h_goto_if_eq HLIB_TMP, 4, L_EV_LH_GoToBirthIsland
    h_goto_if_eq HLIB_TMP, 5, L_EV_LH_GoToFarawayIsland
#endif
    h_msgbox LH13_T + 7                 // Please sail with us another time!
    h_release
L_LH13_NoTicket:
    h_msgbox LH13_T + 1                 // <player> doesn't have the Ticket... I'm terribly sorry. You must have a Ticket to board the ferry.
    h_release
L_LH13_GoToSlateport:
    h_yesno LH13_T + 3, HLIB_TMP        // Slateport City it is, then!
    h_goto_if_no HLIB_TMP, L_LH13_ChangeMind
    h_setvar VAR_PORTHOLE_STATE, 5
    h_msgbox LH13_T + 6                 // Please board the ferry and wait for departure.
    ch13_board_dock LH13_ATTENDANT
    // warp MAP_SS_TIDAL_CORRIDOR, 255, 1, 10: the cabins are not built; the crossing lands in Slateport's harbor (script 11)
    ch13_sail_announce LH13_HB_ZONE, 8 + 1, 11 - 2, 0, 11, LH13_T + 11
    h_release
L_LH13_GoToBattleTower:
    h_yesno LH13_T + 4, HLIB_TMP        // Battle Tower it is, then!
    h_goto_if_no HLIB_TMP, L_LH13_ChangeMind
    h_msgbox LH13_T + 6
    ch13_board_dock LH13_ATTENDANT
    h_sail_ferry LH13_SH_ZONE, 19 + 17, 23 + 18, 1, 3      // warp MAP_BATTLE_TOWER_OUTSIDE, 255, 19, 23 (script 3 of its scene)
    h_release
L_LH13_ChangeMind:
    ParentActorMsg MSGFILE_SCRIPT, LH13_T + 5, 0, 0     // Then, where would you like to go?
    VMJump L_LH13_RegularLocationSelect

L_LH13_EonTicketPossible:               // LilycoveCity_Harbor_EventScript_FerryAttendantLocationAndBoarding
    h_goto_if_unset FLAG_SYS_GAME_CLEAR, L_LH13_FerryUnavailable
    h_goto_if_set FLAG_ENCOUNTERED_LATIAS_OR_LATIOS, L_LH13_FerryUnavailable
    h_goto_if_unset FLAG_SYS_HAS_EON_TICKET, L_LH13_FerryUnavailable
    h_msgbox LH13_T + 13                // The ferry to Slateport is... Oh? That Pass...
    h_closemessage
    h_move LH13_ATTENDANT, 40           // walk_in_place_fastest_up
    VMSleep 15
    ActorDelete LH13_ATTENDANT          // hideobjectat
    VMSleep 30                          // delay 60
    h_addobject LH13_SAILOR, FLAG_HIDE_FERRY_SAILOR_LILYCOVE
    VMSleep 15
    h_move LH13_SAILOR, 1               // Common_Movement_FacePlayer (the player stands south of the dock tile)
    h_msgbox_actor LH13_T + 14, LH13_SAILOR   // Aye, mate, are you the one who brought that mighty odd Pass? ... All aboard!
    h_closemessage
    h_move LH13_SAILOR, 40
    VMSleep 15
    h_removeobject LH13_SAILOR, FLAG_HIDE_FERRY_SAILOR_LILYCOVE
    h_getplayerfacing HLIB_TMP
    h_goto_if_eq HLIB_TMP, 0, L_LH13_EonUp
    h_goto_if_eq HLIB_TMP, 3, L_LH13_EonRight
    VMJump L_LH13_EonBoarded
L_LH13_EonUp:
    h_move 255, 12
    VMJump L_LH13_EonBoarded
L_LH13_EonRight:
    h_move 255, 15
    h_move 255, 40
L_LH13_EonBoarded:
    VMSleep 15
    ch2_hide_player
    h_heal                              // special ScrSpecial_HealPlayerParty
    h_sail_ferry LH13_SI_ZONE, 13 + 15, 22 + 18, 1, 3      // warp MAP_SOUTHERN_ISLAND_EXTERIOR, 255, 13, 22 (script 3 of its scene)
    h_release

// the landing from Slateport (SSTidalCorridor_EventScript_15FDF8: "We've arrived!", setrespawn HEAL_LOCATION_LILYCOVE_CITY,
// warp MAP_LILYCOVE_CITY_HARBOR, 255, 8, 11; the announcement is SSTidalRooms_EventScript_15FCF9's)
Ch13_LH_ArriveFromSlateport:            // script 4 of the room file
    ch2_land
    FieldSetTeleportZone CH13_RESPAWN_LILYCOVE
    h_setvar VAR_PORTHOLE_STATE, 4
    ch13_announce LH13_T + 12           // We have made land in Lilycove City. Thank you for sailing with us.
    h_release

// the landing from the Battle Tower (BattleTower_Outside_EventScript_160232) and from Southern Island
// (SouthernIsland_Exterior_EventScript_160AE0): warp MAP_LILYCOVE_CITY_HARBOR, 255, 8, 11
Ch13_LH_ArriveFromTower:                // script 5
Ch13_LH_ArriveFromIsland:               // script 6
    ch2_land
    h_release

#ifdef EVENTS_LIB_INC
#include "scenes/LilycoveCity_Harbor_Events.inc"
#endif
