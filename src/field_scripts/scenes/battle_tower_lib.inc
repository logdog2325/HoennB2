// Sapphire's Battle Tower (battle_tower agent, 2026-10-08; notes/BATTLE_TOWER.md): shared defines and macros of the
// four rooms' scripts (0042 lobby, 0686 elevator, 0672 corridor, 0030 battle room). Rooms: zone tile = Sapphire tile +
// the room's origin (work/interiors/<room>/room.json "origin").
#ifndef BATTLE_TOWER_LIB_INC
#define BATTLE_TOWER_LIB_INC

#define BT_LOBBY_ZONE 21
#define BT_LOBBY_OX 1
#define BT_LOBBY_OZ 1
#define BT_ELEVATOR_ZONE 343
#define BT_ELEVATOR_OX 1
#define BT_ELEVATOR_OZ 1
#define BT_CORRIDOR_ZONE 336
#define BT_CORRIDOR_OX 1
#define BT_CORRIDOR_OZ 1
#define BT_ROOM_ZONE 15
#define BT_ROOM_OX 1
#define BT_ROOM_OZ 1

// actors (uids of data/interiors/<zone>.json)
#define BT_RECEPTIONIST 1               // lobby (Sapphire object 1, TEALA at (6,5))
#define BT_AWARD_MAN 6                  // lobby (MAN_2 at (7,6), FLAG_HIDE_AWARD_MAN_BATTLE_TOWER)
#define BT_ATTENDANT 1                  // elevator / corridor (TEALA)
#define BT_OPPONENT 1                   // battle room (VAR_OBJ_GFX_ID_0 sprite, FLAG_HIDE_BATTLE_TOWER_OPPONENT)
#define BT_ROOM_ATTENDANT 2             // battle room (TEALA at (1,7))
#define BT_PLAYER 255

// Black 2's Battle Subway play modes (ov033 bsubway_scr.c): 0 Single Train = Sapphire's Lv. 50 room, 5 Super Single
// Train = the Lv. 100 room (b2tools/patches/battle_tower.py: opponents at level 50 + 10 x mode)
#define BT_MODE_LV50 0
#define BT_MODE_LV100 5

// Sapphire's challenge status (gSaveBlock2.battleTower.var_4AE[level]): VAR_BT_STATUS_LV50 / _LV100
#define BT_ST_NONE 0                    // nothing going on (the lobby resets the streak)
#define BT_ST_ENTERED 1                 // saved on entering: seen again only after quitting without a save
#define BT_ST_RESTED 2                  // saved mid-challenge ("save and quit")
#define BT_ST_WON_SAVED 3               // won seven, record saved: the streak goes on
#define BT_ST_WON 4                     // back from seven wins
#define BT_ST_LOST 5                    // back from a loss
#define BT_ST_PRIZE 6                   // the prize did not fit in the Bag

// scratch works of the tower scripts (script works 0x8030/0x8031 are the porting library's)
#define BT_T1 0x8032
#define BT_T2 0x8033
#define BT_T3 0x8034
#define BT_T4 0x8035
#define BT_STATE 0x4000                 // map-local (Sapphire's VAR_TEMP_0)
#define BT_DOOR 0x8036                  // building-model handle of a door being animated
#define BT_OPPONENT_GFX 0x4020          // the opponent's sprite (its NPC has code 162 = work 0x4020, ov012 0x02167fc8)

// Black 2's door_h5_in (building model res 131): animation 0 opens, 1 closes; the door stays open while the handle is
// kept, BMReleaseHandle shows it closed again (the rooms helper's finding, notes/BATTLE_TOWER.md)
    .macro bt_door_open x, z
    BMCreateHandleByGPos BT_DOOR, 1, \x, \z
    BMHndAudioVisualAnmPlay BT_DOOR, 0
    BMHndAnmWait BT_DOOR
    .endm
    .macro bt_door_close
    BMHndAudioVisualAnmPlay BT_DOOR, 1
    BMHndAnmWait BT_DOOR
    BMReleaseHandle BT_DOOR
    .endm

#endif
