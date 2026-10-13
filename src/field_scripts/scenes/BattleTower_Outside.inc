// Battle Tower Outside's story (Sapphire data/maps/BattleTower_Outside/scripts.inc; chapter Ch13, ch13 agent 2026-10-07).
// Included twice by the generated zone file of the island (zone 17, a standalone map on its own matrix; the generated
// sign and the three people follow): the entries below become scripts 1-3. Text: src/text/scenes/BattleTower_Outside.txt
// (lines 0-10). Story objects: the ferry attendant (uid 105, data/story/ch13.json; the S.S. Tidal, object 4, has no Black 2
// sprite). Map scripts: scenes/BattleTower_Outside_init.inc. The Battle Tower itself (the door at (14,8) leads to the
// Lobby room, zone 21) is not scripted yet: the PWT moves into it later (notes/RESEARCH_PWT.md).
#ifdef SCENE_ENTRIES
    ScriptEntry BT_Init                 // 1: BattleTower_Outside_MapScript1_16015C (zone init)
    ScriptEntry BT_FerryAttendant       // 2: BattleTower_Outside_EventScript_160168
    ScriptEntry BT_Arrive               // 3: the landing of the ferry (reserved by the harbors and Southern Island)
#else
#include "scenes/ch13_lib.inc"
#define BT_ATTENDANT 105
#define BT_SLATEPORT_ZONE 596           // SlateportCity_Harbor (room origin (1, -2): zone tile = Sapphire tile + (1, -2))
#define BT_LILYCOVE_ZONE 203            // LilycoveCity_Harbor
// text lines: 0 "Hello, are you here for the ferry? May I see your Ticket?"  1 "<player> doesn't have the Ticket..."
// 2 "<player> flashed the Ticket. ... And where would you like to go?"  3 "Slateport City it is, then!"
// 4 "Lilycove City it is, then!"  5 "Please sail with us another time!"  6 "Please board the ferry and wait for departure."
// 7 "Then, where would you like to go?"  8/9/10 Slateport / Lilycove / Cancel

BT_Init:                                // BattleTower_Outside_MapScript1_16015C
    h_setflag FLAG_LANDMARK_BATTLE_TOWER
    h_setvar VAR_BRAVO_TRAINER_BATTLE_TOWER_ON, 0
    h_setflag FLAG_HIDE_REPORTER_BATTLE_TOWER
    VMHalt

BT_FerryAttendant:                      // BattleTower_Outside_EventScript_160168
    h_lock
    SEPlay SEQ_SE_MESSAGE
    h_faceplayer
    h_buffer_player
    h_msgbox 0                          // Hello, are you here for the ferry? May I see your Ticket?
    h_checkitem ITEM_SS_TICKET, 1, HLIB_TMP
    h_goto_if_eq HLIB_TMP, 0, L_BT_NoTicket
    ParentActorMsg MSGFILE_SCRIPT, 2, 0, 0      // <player> flashed the Ticket. Perfect! ... And where would you like to go?
L_BT_Choose:
    ListMenu_AnchorTopRight 31, 6, 0, 1, HLIB_TMP      // multichoicedefault 21, 6, 53 (SLATEPORT / LILYCOVE / CANCEL), 2, 0
    ListMenuAdd 8, 65535, 0
    ListMenuAdd 9, 65535, 1
    ListMenuAdd 10, 65535, 2
    ListMenuShow
    h_goto_if_eq HLIB_TMP, 0, L_BT_Slateport
    h_goto_if_eq HLIB_TMP, 1, L_BT_Lilycove
    h_msgbox 5                          // Please sail with us another time!
    h_release
L_BT_NoTicket:
    h_msgbox 1                          // <player> doesn't have the Ticket... I'm terribly sorry. You must have a Ticket to board the ferry.
    h_release
L_BT_Slateport:
    h_yesno 3, HLIB_TMP                 // Slateport City it is, then!
    h_goto_if_no HLIB_TMP, L_BT_ChangeMind
    h_msgbox 6                          // Please board the ferry and wait for departure.
    ch13_board_island BT_ATTENDANT
    h_sail_ferry BT_SLATEPORT_ZONE, 8 + 1, 11 - 2, 0, 12   // warp MAP_SLATEPORT_CITY_HARBOR, 255, 8, 11 (script 12 of the room file)
    h_release
L_BT_Lilycove:
    h_yesno 4, HLIB_TMP                 // Lilycove City it is, then!
    h_goto_if_no HLIB_TMP, L_BT_ChangeMind
    h_msgbox 6
    ch13_board_island BT_ATTENDANT
    h_sail_ferry BT_LILYCOVE_ZONE, 8 + 1, 11 - 2, 0, 5     // warp MAP_LILYCOVE_CITY_HARBOR, 255, 8, 11 (script 5)
    h_release
L_BT_ChangeMind:
    ParentActorMsg MSGFILE_SCRIPT, 7, 0, 0      // Then, where would you like to go?
    VMJump L_BT_Choose

BT_Arrive:                              // the player stands on the dock at (19,23), facing the attendant at (19,24)
    ch2_land
    h_release
#endif
