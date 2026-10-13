// Emerald's Battle Pike (frontier_pike, 2026-10-12; notes/FRONTIER_PIKE.md): shared defines and macros of the six
// rooms' scripts (src/field_scripts/emerald/0798-0809_room_BattleFrontier_BattlePike*.s). Emerald builds only.
// Rooms: zone tile = Emerald tile + the room's origin (work/interiors/<room>/room.json "origin": (1, -1), the final
// room (1, -2)). The Pike's own command (b2tools/patches/frontier_pike.c) is EmPike var, op, a, b.
#ifndef FRONTIER_PIKE_LIB_INC
#define FRONTIER_PIKE_LIB_INC
#include "scenes/frontier_pike_lines.inc"

#define PK_LOBBY_ZONE 399
#define PK_CORRIDOR_ZONE 400
#define PK_THREE_ZONE 401
#define PK_ROOM_ZONE 402
#define PK_WILD_ZONE 403
#define PK_FINAL_ZONE 404
#define PK_OX 1                         // the rooms' origin (every room but the final one)
#define PK_OZ (-1)
#define PK_FINAL_OX 1
#define PK_FINAL_OZ (-2)
#define PK_ISLAND_ZONE 17               // the Battle Frontier island (Battle Tower / Frontier west + east)
#define PK_ISLAND_DOOR 16               // its warp 16 (Black 2 slots 0-1, then world.json door 14 = OutsideWest warp 0)

#define PK_PLAYER 255
#define PK_TR_A 529                     // the Pike's battle slots (frontier_pike.py): the room's trainers and Lucy
#define PK_TR_B 530
#define PK_TR_LUCY 531

// scratch works (0x8030/0x8031 are the porting library's, 0x8032-0x8036 the Battle Tower's, 0x8048-0x804F frontier_core's)
#define PK_T0 0x8038
#define PK_T1 0x8039
#define PK_T2 0x803A
#define PK_T3 0x803B
// map-local works of each room (0x4000-0x401F: cleared on every map change; frontier_pike.c reads 0x4001-0x4005)
#define PK_W_STATE 0x4000               // 0 on arrival: the map-script condition runs the room's scene once (Emerald's
                                        // ON_FRAME VAR_TEMP_0 / VAR_TEMP_CHALLENGE_STATUS)
#define PK_W_TR_A 0x4001
#define PK_W_TR_B 0x4002
#define PK_W_NPC 0x4003
#define PK_W_WILD 0x4004
#define PK_W_WILD_LV 0x4005
#define PK_W_EXIT 0x4006                // Emerald's VAR_TEMP_1: the exit trigger is live while 0
#define PK_W_ENTERED 0x4007             // VAR_TEMP_2: 0 until the player has walked in
#define PK_W_NO_TURN 0x4008             // VAR_TEMP_3: 1 once walked in (the "no turning back" triggers fire)
#define PK_W_HINT 0x4009                // VAR_TEMP_5 of the three-path room: 0 set the hint, 1 Lucy's warning, 255 done
// map-local flags hiding the room's two people (cleared on every map change)
#define PK_F_HIDE1 0x50
#define PK_F_HIDE2 0x51

// EmPike ops (frontier_pike.c PK_*) and fields (F_*)
#define PK_INIT 0
#define PK_GET 1
#define PK_SET 2
#define PK_NEXT_ROOM 3
#define PK_ROOM_TYPE 4
#define PK_SETUP_ROOM 5
#define PK_INTRO 6
#define PK_STATUS_KIND 7
#define PK_STATUS_MON 8
#define PK_HEAL_ONE_TWO 9
#define PK_NPC_SPEECH 10
#define PK_SET_HINT 11
#define PK_HINT_ROOM 12
#define PK_HINT_KIND 13
#define PK_QUEEN_TYPE 14
#define PK_HEAL_BEFORE_QUEEN 15
#define PK_FULL_HEALTH 16
#define PK_SAVE_ITEMS 17
#define PK_RESTORE_ITEMS 18
#define PK_IS_FINAL 19
#define PK_WILD 20
#define PK_PARTY_ORDER 21
#define PK_ALL_FAINTED 22
#define PKF_STREAK 0
#define PKF_RECORD 1
#define PKF_TOTAL 2
#define PKF_STREAK_ACTIVE 3
#define PKF_ROOM 4
#define PKF_STATUS 5
#define PKF_LVL 6
#define PKF_HEARD_BRAIN 7
#define PKF_PAUSED 8
#define PKF_HEAL_OFF 9
#define PKF_SYMBOLS 10
#define PKF_HINT_INDEX 11
#define PKF_DOOR 12
// pokeemerald include/constants/battle_pike.h
#define PIKE_ROOM_SINGLE_BATTLE 0
#define PIKE_ROOM_HEAL_FULL 1
#define PIKE_ROOM_NPC 2
#define PIKE_ROOM_STATUS 3
#define PIKE_ROOM_HEAL_PART 4
#define PIKE_ROOM_WILD_MONS 5
#define PIKE_ROOM_HARD_BATTLE 6
#define PIKE_ROOM_DOUBLE_BATTLE 7
#define PIKE_ROOM_BRAIN 8
#define PIKE_ROOM_LEFT 0
#define PIKE_ROOM_CENTER 1
#define PIKE_ROOM_RIGHT 2
#define PIKE_HINT_NOSTALGIA 0
#define PIKE_HINT_WHISPERING 1
#define PIKE_HINT_POKEMON 2
#define PIKE_HINT_PEOPLE 3
#define PIKE_HINT_BRAIN 4
#define PIKE_STATUSMON_KIRLIA 0
#define PIKE_STATUSMON_DUSCLOPS 1
#define PIKE_STATUS_FREEZE 0
#define PIKE_STATUS_BURN 1
#define PIKE_STATUS_TOXIC 2
#define PIKE_STATUS_PARALYSIS 3
#define PIKE_STATUS_SLEEP 4
#define FRONTIER_BRAIN_NOT_READY 0
#define FRONTIER_BRAIN_SILVER 1
#define FRONTIER_BRAIN_GOLD 2
#define FRONTIER_BRAIN_STREAK 3
#define FRONTIER_BRAIN_STREAK_LONG 4
#define PK_ST_IN_CHALLENGE 99           // Emerald's frontier_set FRONTIER_DATA_CHALLENGE_STATUS, 99
#define SE_PIKE_CURTAIN SEQ_SE_KAIDAN   // Emerald's SE_PIKE_CURTAIN_CLOSE / _OPEN: Black 2 has no curtain sound (stand-in)
#define MUS_OBTAIN_SYMBOL FR_ME_OBTAIN_SYMBOL   // Emerald's mus_obtain_symbol (frontier_core's songs, FRONTIER.md 5)

    .macro EmPike var, op, a=0, b=0     // command 290 (frontier_pike.c PK_Cmd)
    FieldCommand 290
    .2byte \var
    .2byte \op
    .2byte \a
    .2byte \b
    .endm
    .macro pk_get field, var
    EmPike \var, PK_GET, \field
    .endm
    .macro pk_set field, value          // value: a number or a work
    EmPike PK_T3, PK_SET, \field, \value
    .endm
    .macro pk_streak_win                // pike_get WIN_STREAK, addvar 1, pike_set (the record follows: frontier_core)
    fr_streak_win FRONTIER_FACILITY_PIKE, FRONTIER_MODE_SINGLES
    .endm
    .macro pk_room_plus_one             // frontier_get BATTLE_NUM, addvar 1, frontier_set
    fr_get FR_BATTLE_NUM, PK_T3
    WorkAdd PK_T3, 1
    fr_set FR_BATTLE_NUM, PK_T3
    .endm
    // Emerald's "close the curtain" + warpsilent to the next room: the curtain is a fade (Black 2 has no such screen
    // effect); the arrival room's map-script condition (PK_W_STATE 0) runs its scene, as Emerald's ON_FRAME table
    .macro pk_curtain_warp zone, x, z
    SEPlay SE_PIKE_CURTAIN
    h_warp_arrive \zone, \x, \z, 0
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt
    .endm
    .macro pk_say n, who                // msgbox said by an actor
    ActorMsg MSGFILE_SCRIPT, \n, \who, 0, 0
    LastKeyWait
    .endm
    .macro pk_print n, who              // message + waitmessage (no key wait at its end)
    ActorMsg MSGFILE_SCRIPT, \n, \who, 0, 0
    .endm
#endif
