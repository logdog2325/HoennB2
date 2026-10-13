// Slateport Harbor's ferry attendant (Sapphire data/maps/SlateportCity_Harbor/scripts.inc, SlateportCity_Harbor_EventScript_
// FerryAttendant ... ChooseNewDestination, BoardFerry, CancelDestinationSelect, BoardFerryEast/North; chapter Ch13, ch13 agent
// 2026-10-07). Included by 1192_room_SlateportCity_Harbor.s (guarded) in place of its fallback; replaces the attendant's
// label Ch13_HB_FerryAttendant (script 3, object 1, data/story/ch3a.json). Text: lines 22-34 of 0352 (HB13_T + n, below);
// T_FerryUnavailable is the room file's own line 1. Scripts 11/12 (room file entries) are the landings.
// The ship is scenes/ch13_lib.inc's crossing (Black 2 has no ship to ride and the S.S. Tidal's rooms are not built).
// Slateport -> Lilycove: VAR_PORTHOLE_STATE 1 and the ship's departure announcement; the landing in Lilycove is script
// 4 of the Lilycove harbor file. Slateport -> Battle Tower: scene script 3 of scenes/BattleTower_Outside.inc.
#include "scenes/ch13_lib.inc"
#define HB13_T 22
// HB13_T +0 "Hello, are you here for the ferry? May I see your Ticket?"  +1 "<player> doesn't have the Ticket..."
//        +2 "<player> flashed the Ticket. ... where would you like to go?"  +3 "Lilycove City it is, then!"
//        +4 "Battle Tower it is, then!"  +5 "Then, where would you like to go?"  +6 "Please board the ferry and wait for departure."
//        +7 "Please sail with us another time!"  +8/+9/+10 Lilycove / Battle Tower / Cancel
//        +11 "This ferry is built to plow through fast-running currents. ..."  +12 "We have made land in Slateport City. ..."
#define HB13_ATTENDANT 1
#define HB13_BT_ZONE 17                 // BattleTower_Outside (standalone group; matrix tile = Sapphire tile + (17, 18))
#define HB13_LH_ZONE 203                // LilycoveCity_Harbor (room origin (1, -2): zone tile = Sapphire tile + (1, -2))

Ch13_HB_FerryAttendant:                 // SlateportCity_Harbor_EventScript_FerryAttendant
    h_lock
    SEPlay SEQ_SE_MESSAGE
    h_faceplayer
    h_buffer_player
    h_goto_if_set FLAG_SYS_GAME_CLEAR, L_HB13_AskForTicket
    h_msgbox T_FerryUnavailable         // I beg your pardon? You're looking for a ship? ... the ferry service isn't available at present...
    h_release
L_HB13_AskForTicket:
    h_msgbox HB13_T + 0                 // Hello, are you here for the ferry? May I see your Ticket?
    h_checkitem ITEM_SS_TICKET, 1, HLIB_TMP
    h_goto_if_eq HLIB_TMP, 0, L_HB13_NoTicket
    ParentActorMsg MSGFILE_SCRIPT, HB13_T + 2, 0, 0     // <player> flashed the Ticket. Perfect! ... And where would you like to go?
L_HB13_ChooseDestination:
    ListMenu_AnchorTopRight 31, 6, 0, 1, HLIB_TMP      // multichoicedefault 18, 6, 52 (LILYCOVE / BATTLE TOWER / CANCEL), 2, 0
    ListMenuAdd HB13_T + 8, 65535, 0
    ListMenuAdd HB13_T + 9, 65535, 1
    ListMenuAdd HB13_T + 10, 65535, 2
    ListMenuShow
    h_goto_if_eq HLIB_TMP, 0, L_HB13_Lilycove
    h_goto_if_eq HLIB_TMP, 1, L_HB13_BattleTower
    h_msgbox HB13_T + 7                 // Please sail with us another time!
    h_release
L_HB13_NoTicket:
    h_msgbox HB13_T + 1                 // <player> doesn't have the Ticket... I'm terribly sorry. You must have a Ticket to board the ferry.
    h_release
L_HB13_Lilycove:
    h_yesno HB13_T + 3, HLIB_TMP        // Lilycove City it is, then!
    h_goto_if_no HLIB_TMP, L_HB13_ChooseNewDestination
    h_setvar VAR_PORTHOLE_STATE, 1
    h_msgbox HB13_T + 6                 // Please board the ferry and wait for departure.
    ch13_board_dock HB13_ATTENDANT
    // warp MAP_SS_TIDAL_CORRIDOR, 255, 1, 10: the cabins are not built; the crossing lands in Lilycove's harbor (script 4)
    ch13_sail_announce HB13_LH_ZONE, 8 + 1, 11 - 2, 0, 4, HB13_T + 11
    h_release
L_HB13_BattleTower:
    h_yesno HB13_T + 4, HLIB_TMP        // Battle Tower it is, then!
    h_goto_if_no HLIB_TMP, L_HB13_ChooseNewDestination
    h_msgbox HB13_T + 6
    ch13_board_dock HB13_ATTENDANT
    h_sail_ferry HB13_BT_ZONE, 19 + 17, 23 + 18, 1, 3      // warp MAP_BATTLE_TOWER_OUTSIDE, 255, 19, 23 (script 3 of its scene)
    h_release
L_HB13_ChooseNewDestination:
    ParentActorMsg MSGFILE_SCRIPT, HB13_T + 5, 0, 0     // Then, where would you like to go?
    VMJump L_HB13_ChooseDestination

// the landing from Lilycove (SSTidalCorridor_EventScript_15FE17: "We've arrived!", setrespawn HEAL_LOCATION_SLATEPORT_CITY,
// warp MAP_SLATEPORT_CITY_HARBOR, 255, 8, 11; the announcement is SSTidalRooms_EventScript_15FD50's)
Ch13_HB_ArriveFromLilycove:             // script 11 of the room file
    ch2_land
    FieldSetTeleportZone CH13_RESPAWN_SLATEPORT
    h_setvar VAR_PORTHOLE_STATE, 8
    ch13_announce HB13_T + 12           // We have made land in Slateport City. Thank you for sailing with us.
    h_release

// the landing from the Battle Tower (BattleTower_Outside_EventScript_160232: warp MAP_SLATEPORT_CITY_HARBOR, 255, 8, 11)
Ch13_HB_ArriveFromTower:                // script 12
    ch2_land
    h_release
