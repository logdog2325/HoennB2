// Lilycove Harbor: Emerald's event tickets (pokeemerald data/maps/LilycoveCity_Harbor/scripts.inc: GetAuroraTicketState,
// GetOldSeaMapState, GetMysticTicketState, GetFirstTimeShowingTicket, the first-time scenes with the ferry sailor and
// Mr. Briney, the islands in the destination menu; src/script_menu.c CreateLilycoveSSTidalMultichoice). Events agent,
// 2026-10-07 (notes/EVENTS.md). Included at the end of scenes/LilycoveCity_Harbor_Ch13.inc (ch13's attendant), which
// jumps here once the game is cleared (after Sapphire's own Eon Ticket scene, which stays first) and adds the islands to
// its destination menu (Sub_EV_LH_TicketStates). Text: lines 19-28 of src/text/script/0261_room_LilycoveCity_Harbor.txt
// (Emerald's words; EV_LH_T + n below); "The ferry to Slateport is... Oh? That Pass..." is Sapphire's own line LH13_T + 13.
// People: the attendant (uid 1), the ferry sailor (uid 4, FLAG_HIDE_FERRY_SAILOR_LILYCOVE: Sapphire's, placed by ch8a) and
// Mr. Briney (uid 5, FLAG_HIDE_LILYCOVE_HARBOR_EVENT_TICKET_TAKER, data/story/events.json; Emerald object 5), all at (8,10).
// Emerald sails to the islands only from Lilycove (its Slateport attendant offers Lilycove and the Battle Frontier): the
// same here. The islands' sailors bring you back to this harbor (landing script 6, Ch13_LH_ArriveFromIsland).
// (its defines EV_LH_*: scenes/events_lib.inc, needed before ch13's menu uses them)

// the three Get...State scripts: held = the ticket in the Bag and its FLAG_ENABLE_SHIP_ flag (the givers set both)
Sub_EV_LH_TicketStates:
    h_setvar EV_LH_MYSTIC, 0
    h_goto_if_unset FLAG_ENABLE_SHIP_NAVEL_ROCK, L_EV_LH_S1
    h_checkitem ITEM_MYSTIC_TICKET, 1, HLIB_RESULT
    h_goto_if_eq HLIB_RESULT, 0, L_EV_LH_S1
    h_setvar EV_LH_MYSTIC, 1
    h_goto_if_set FLAG_SHOWN_MYSTIC_TICKET, L_EV_LH_S1
    h_setvar EV_LH_MYSTIC, 2
L_EV_LH_S1:
    h_setvar EV_LH_AURORA, 0
    h_goto_if_unset FLAG_ENABLE_SHIP_BIRTH_ISLAND, L_EV_LH_S2
    h_checkitem ITEM_AURORA_TICKET, 1, HLIB_RESULT
    h_goto_if_eq HLIB_RESULT, 0, L_EV_LH_S2
    h_setvar EV_LH_AURORA, 1
    h_goto_if_set FLAG_SHOWN_AURORA_TICKET, L_EV_LH_S2
    h_setvar EV_LH_AURORA, 2
L_EV_LH_S2:
    h_setvar EV_LH_MAP, 0
    h_goto_if_unset FLAG_ENABLE_SHIP_FARAWAY_ISLAND, L_EV_LH_S3
    h_checkitem ITEM_OLD_SEA_MAP, 1, HLIB_RESULT
    h_goto_if_eq HLIB_RESULT, 0, L_EV_LH_S3
    h_setvar EV_LH_MAP, 1
    h_goto_if_set FLAG_SHOWN_OLD_SEA_MAP, L_EV_LH_S3
    h_setvar EV_LH_MAP, 2
L_EV_LH_S3:
    VMReturn

// LilycoveCity_Harbor_EventScript_FerryAttendant after the game is cleared (the Eon Ticket's first time is Sapphire's, above)
L_EV_LH_EventTickets:
    VMCall Sub_EV_LH_TicketStates
    h_goto_if_eq EV_LH_MAP, 2, L_EV_LH_OldSeaMapFirstTime
    h_goto_if_ne EV_LH_AURORA, 2, L_EV_LH_NoAurora
    h_goto_if_eq EV_LH_MYSTIC, 2, L_EV_LH_MultipleFirstTime
    VMJump L_EV_LH_AuroraFirstTime
L_EV_LH_NoAurora:
    h_goto_if_eq EV_LH_MYSTIC, 2, L_EV_LH_MysticFirstTime
    VMJump L_LH13_NoFirstTimeEventTickets   // Sapphire's "May I see your Ticket?" and the destination menu

// LilycoveCity_Harbor_EventScript_GetEventTicketSailor: the attendant turns to the ship and is gone, the sailor comes out
    .macro ev_lh_get_sailor
    h_closemessage
    h_move LH13_ATTENDANT, 40               // Common_Movement_WalkInPlaceFasterUp
    VMSleep 15                              // delay 30
    ActorDelete LH13_ATTENDANT              // hideobjectat
    VMSleep 30                              // delay 60
    h_addobject LH13_SAILOR, FLAG_HIDE_FERRY_SAILOR_LILYCOVE
    VMSleep 15
    h_move LH13_SAILOR, 1                   // Common_Movement_FacePlayer (the player stands south or west of the dock tile)
    .endm

// LilycoveCity_Harbor_EventScript_BoardFerryWithSailor: the sailor boards first, then the player (ch13_board_dock's steps)
    .macro ev_lh_board_with_sailor
    h_closemessage
    h_move LH13_SAILOR, 40
    VMSleep 15
    h_removeobject LH13_SAILOR, FLAG_HIDE_FERRY_SAILOR_LILYCOVE
    ev_lh_player_boards
    .endm

// the player steps onto the dock tile and is gone (ch13_board_dock's steps: facing north = walk up, east = walk right)
    .macro ev_lh_player_boards
    h_getplayerfacing HLIB_TMP
    h_goto_if_eq HLIB_TMP, 0, .Levbs_up\@
    h_goto_if_eq HLIB_TMP, 3, .Levbs_right\@
    VMJump .Levbs_done\@
.Levbs_up\@:
    h_move 255, 12                          // walk_up
    VMJump .Levbs_done\@
.Levbs_right\@:
    h_move 255, 15                          // walk_right
    h_move 255, 40                          // walk_in_place_fastest_up
.Levbs_done\@:
    VMSleep 15
    ch2_hide_player
    .endm

L_EV_LH_AuroraFirstTime:                    // LilycoveCity_Harbor_EventScript_AuroraTicketFirstTime
    h_setflag FLAG_SHOWN_AURORA_TICKET
    h_msgbox LH13_T + 13                    // The ferry to Slateport is... Oh? That Pass...
    ev_lh_get_sailor
    h_msgbox_actor EV_LH_T + 0, LH13_SAILOR // Is it you who brought that odd ticket? ... Get on board, youngster!
L_EV_LH_GoToBirthIslandFirstTime:
    ev_lh_board_with_sailor
    h_sail_ferry EV_BIRTH_ZONE, 15 + EV_BIRTH_OX, 23 + EV_BIRTH_OZ, 1, EV_ARRIVE_SCRIPT   // warp MAP_BIRTH_ISLAND_HARBOR, 8, 4
    h_release

L_EV_LH_MysticFirstTime:                    // LilycoveCity_Harbor_EventScript_MysticTicketFirstTime
    h_setflag FLAG_SHOWN_MYSTIC_TICKET
    h_msgbox LH13_T + 13
    ev_lh_get_sailor
    h_msgbox_actor EV_LH_T + 0, LH13_SAILOR
L_EV_LH_GoToNavelRockFirstTime:
    ev_lh_board_with_sailor
    h_sail_ferry EV_NAVEL_ZONE, 10 + EV_NAVEL_OX, 17 + EV_NAVEL_OZ, 1, EV_ARRIVE_SCRIPT   // warp MAP_NAVEL_ROCK_HARBOR, 8, 4
    h_release

L_EV_LH_MultipleFirstTime:                  // LilycoveCity_Harbor_EventScript_MultipleEventTicketsFirstTime
    h_msgbox LH13_T + 13
    ev_lh_get_sailor
    ActorMsg MSGFILE_SCRIPT, EV_LH_T + 5, LH13_SAILOR, 0, 0   // Is it you who brought those odd tickets? ... Where shall we sail first?
    ListMenu_AnchorTopRight 31, 6, 0, 1, HLIB_TMP   // ScriptMenu_CreateLilycoveSSTidalMultichoice, 0x8004 = 1: the islands
    ListMenuAdd EV_LH_T + 6, 65535, 3       // not shown yet (both here), each marked shown when listed
    ListMenuAdd EV_LH_T + 7, 65535, 4
    ListMenuAdd LH13_T + 10, 65535, 6
    ListMenuShow
    h_setflag FLAG_SHOWN_MYSTIC_TICKET
    h_setflag FLAG_SHOWN_AURORA_TICKET
    h_goto_if_eq HLIB_TMP, 3, L_EV_LH_GoToNavelRockFirstTime
    h_goto_if_eq HLIB_TMP, 4, L_EV_LH_GoToBirthIslandFirstTime
    h_msgbox_actor EV_LH_T + 9, LH13_SAILOR // ExitFirstTimeTicketSailSelect: Aye, right, as you like, then.
    h_closemessage
    h_move LH13_SAILOR, 40
    VMSleep 15
    h_removeobject LH13_SAILOR, FLAG_HIDE_FERRY_SAILOR_LILYCOVE
    VMSleep 15
    ActorAdd LH13_ATTENDANT                 // showobjectat
    h_move LH13_ATTENDANT, 1                // Common_Movement_WalkInPlaceFasterDown
    VMSleep 15
    h_msgbox LH13_T + 7                     // Please sail with us another time!
    h_release

// LilycoveCity_Harbor_EventScript_OldSeaMapFirstTime: the sailor can't help, Mr. Briney (who owes you so much) sails you there
L_EV_LH_OldSeaMapFirstTime:
    h_setflag FLAG_SHOWN_OLD_SEA_MAP
    h_msgbox EV_LH_T + 1                    // The ferry to Slateport is... Can we sail to this place on the map? ... Please wait.
    ev_lh_get_sailor
    h_msgbox_actor EV_LH_T + 2, LH13_SAILOR // What's up, youngster? ... I'm afraid I can't help you...
    h_closemessage
    h_move LH13_SAILOR, 40                  // Common_Movement_WalkInPlaceFasterUp
    h_applymovement LH13_SAILOR, Mv_EV_LH_Exclaim   // playse SE_PIN, ExclamationMark, Delay48
    h_waitmovement
    h_getplayerfacing EV_LH_MAP             // (VAR_FACING; EV_LH_MAP is free again)
    h_goto_if_eq EV_LH_MAP, 3, L_EV_LH_OSM_East
    h_applymovement LH13_SAILOR, Mv_EV_LH_SailorOutOfWayNorth
    h_waitmovement
    h_addobject EV_LH_BRINEY, FLAG_HIDE_LILYCOVE_HARBOR_EVENT_TICKET_TAKER
    h_move EV_LH_BRINEY, 42                 // Common_Movement_WalkInPlaceFasterLeft: Briney faces the sailor
    h_msgbox_actor EV_LH_T + 3, EV_LH_BRINEY   // Briney: Hold on a second! ...
    h_closemessage                          // (Black 2: a speaker turned while its balloon is open never lets the
    h_move EV_LH_BRINEY, 41                 //  balloon close again: tested) ... and the player (WalkInPlaceFasterDown)
    h_buffer_player
    h_msgbox_actor EV_LH_T + 4, EV_LH_BRINEY   // <player>, I'm terribly sorry. ... Let's find this island on this Old Sea Map!
    VMJump L_EV_LH_OSM_Board
L_EV_LH_OSM_East:
    h_applymovement LH13_SAILOR, Mv_EV_LH_SailorOutOfWayEast
    h_waitmovement
    h_addobject EV_LH_BRINEY, FLAG_HIDE_LILYCOVE_HARBOR_EVENT_TICKET_TAKER
    h_move EV_LH_BRINEY, 41                 // Common_Movement_WalkInPlaceFasterDown: Briney faces the sailor
    h_msgbox_actor EV_LH_T + 3, EV_LH_BRINEY
    h_closemessage
    h_move EV_LH_BRINEY, 42                 // WalkInPlaceFasterLeft: the player
    h_buffer_player
    h_msgbox_actor EV_LH_T + 4, EV_LH_BRINEY
L_EV_LH_OSM_Board:                          // BoardFerryWithBrineyAndSailorNorth / East: Briney, the sailor, then the
    h_closemessage                          // player, one after the other (Emerald moves the three at once; Black 2's
    h_applymovement EV_LH_BRINEY, Mv_EV_LH_Board   // scripted steps stop at another actor: tested, the player stood
    h_waitmovement                                 // still behind Briney), each gone on the dock
    h_removeobject EV_LH_BRINEY, FLAG_HIDE_LILYCOVE_HARBOR_EVENT_TICKET_TAKER
    h_applymovement LH13_SAILOR, Mv_EV_LH_Board
    h_waitmovement
    h_removeobject LH13_SAILOR, FLAG_HIDE_FERRY_SAILOR_LILYCOVE
    ev_lh_player_boards
    h_sail_ferry EV_FARAWAY_ZONE, 13 + EV_FARAWAY_OX, 38 + EV_FARAWAY_OZ, 1, EV_ARRIVE_SCRIPT   // warp MAP_FARAWAY_ISLAND_ENTRANCE, 13, 38
    h_release

// the destination menu's islands (LilycoveCity_Harbor_EventScript_GoToNavelRock / GoToBirthIsland / GoToFarawayIsland):
// "Please board the ferry and wait for departure.", the attendant steps aside, the crossing
L_EV_LH_GoToNavelRock:
    h_msgbox LH13_T + 6
    ch13_board_dock LH13_ATTENDANT
    h_sail_ferry EV_NAVEL_ZONE, 10 + EV_NAVEL_OX, 17 + EV_NAVEL_OZ, 1, EV_ARRIVE_SCRIPT
    h_release
L_EV_LH_GoToBirthIsland:
    h_msgbox LH13_T + 6
    ch13_board_dock LH13_ATTENDANT
    h_sail_ferry EV_BIRTH_ZONE, 15 + EV_BIRTH_OX, 23 + EV_BIRTH_OZ, 1, EV_ARRIVE_SCRIPT
    h_release
L_EV_LH_GoToFarawayIsland:
    h_msgbox LH13_T + 6
    ch13_board_dock LH13_ATTENDANT
    h_sail_ferry EV_FARAWAY_ZONE, 13 + EV_FARAWAY_OX, 38 + EV_FARAWAY_OZ, 1, EV_ARRIVE_SCRIPT
    h_release

// the harbor's zone init (script 7 of 0406_room_LilycoveCity_Harbor.s, 0407_..._init.s): Mr. Briney is only here for the Old
// Sea Map scene (Emerald's new game sets FLAG_HIDE_LILYCOVE_HARBOR_EVENT_TICKET_TAKER; Sapphire's list has no such flag)
Ev_LH_Init:
    h_setflag FLAG_HIDE_LILYCOVE_HARBOR_EVENT_TICKET_TAKER
    VMHalt

    .balign 4, 0
Mv_EV_LH_Exclaim:
    emote_exclamation_mark
    delay_16 3
    step_end
    .balign 4, 0
Mv_EV_LH_SailorOutOfWayNorth:               // LilycoveCity_Harbor_Movement_SailorOutOfWayNorth
    walk_in_place_fastest_right
    lock_facing_direction
    walk_left
    unlock_facing_direction
    step_end
    .balign 4, 0
Mv_EV_LH_SailorOutOfWayEast:                // ..._SailorOutOfWayEast
    lock_facing_direction
    walk_down
    unlock_facing_direction
    step_end
    .balign 4, 0
Mv_EV_LH_Board:                             // ..._BrineyBoardFerry (set_invisible: the actor is removed after it)
    walk_in_place_fastest_up
    delay_8
    step_end
    .balign 4, 0
