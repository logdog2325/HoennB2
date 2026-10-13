// Emerald's Battle Pyramid (frontier_pyramid, 2026-10-12; notes/FRONTIER_PYRAMID.md): shared defines and macros of the
// three zones' scripts (src/field_scripts/emerald/0694/0695 lobby, 0776/0777 floor, 0840/0841 top). Emerald builds only.
// The Pyramid's own command (b2tools/patches/frontier_pyramid.c PY_Cmd, through frontier_pyramid_stub.c) is
// EmPyr var, op, a: var is the answer (and the input of some ops), a a number or a work.
#ifndef FRONTIER_PYRAMID_LIB_INC
#define FRONTIER_PYRAMID_LIB_INC
#include "scenes/frontier_pyramid_lines.inc"

#define PY_LOBBY_ZONE 347
#define PY_FLOOR_ZONE 388
#define PY_TOP_ZONE 420
#define PY_LOBBY_OX 0                   // the lobby room's origin (Emerald tile + origin = zone tile; rooms.py ORIGIN)
#define PY_LOBBY_OZ (-2)
#define PY_TOP_OX (-1)                  // the top room's origin
#define PY_TOP_OZ (-5)
#define PY_ISLAND_ZONE 17
#define PY_ISLAND_DOOR 5                // zone 17's warp 5 (Black 2's 2, then world.json door 3 = OutsideEast warp 3)
#define PY_PLAYER 255
#define PY_TR 532                       // the floor's Frontier trainers (frontier_pyramid.py TR)
#define PY_TR_BRAIN 533                 // Brandon

// scratch works (the Pike's 0x8038-0x803B: never at the same time)
#define PY_T0 0x8038
#define PY_T1 0x8039
#define PY_T2 0x803A
#define PY_T3 0x803B
// map-local works (0x4000-0x401F: cleared on every map change, saved with the game); frontier_pyramid.c reads 0x4010-0x4013
#define PY_W_SLOT 0x4010                // the object the script is about (0-15)
#define PY_W_STEPS 0x4011               // a trainer who spotted the player: steps to walk, its facing
#define PY_W_DIR 0x4012
#define PY_W_WILD_LV 0x4013             // the wild Pokemon's level (PY_WILD)
#define PY_W_STATE 0x4014               // 0 after a map change: the zone's condition script runs once (Emerald's ON_RESUME)
#define PY_W_ACTOR 0x4015               // the object's actor uid (slot + 1)
#define PY_W_ARRIVED 0x4016             // the player has been put on the floor's entrance
#define PY_HIDE_FLAG 0x40               // map-local flags 0x40-0x4F hide the floor's objects 0-15 (frontier_pyramid.c)

// EmPyr ops (frontier_pyramid.c PY_*; frontier_pyramid.py checks the order)
#define PY_INIT 0
#define PY_SEED 1
#define PY_SETUP 2
#define PY_START_X 3
#define PY_START_Z 4
#define PY_SLOT_KIND 5
#define PY_TRAINER_PREP 6
#define PY_TRAINER_WON 7
#define PY_HINT 8
#define PY_ITEM 9
#define PY_ITEM_TAKEN 10
#define PY_WILD 11
#define PY_WILD_LV 12
#define PY_LIGHT 13
#define PY_LIGHT_ADD 14
#define PY_BRAIN 15
#define PY_BRAIN_PARTY 16
#define PY_HEARD 17
#define PY_SET_HEARD 18
#define PY_STREAK_ACTIVE 19
#define PY_SET_STREAK_ACTIVE 20
#define PY_SYNC 21
#define PY_END 22
#define PY_HELD_TO_BAG 23
#define PY_ELIGIBLE 24
#define PY_PICKS_HOLD 25
#define PY_REST_POS 26
#define PY_ARRIVAL 27
#define PY_BAG_COUNT 28
#define PY_GET 29
#define PY_SET 30
#define PY_UNLOAD 31
#define PY_FLOOR_NO 32
#define PY_HINT_GIVER 33
#define PY_RESULTS 34
#define PY_TEST 35
#define PY_ALL_FAINTED 36
#define PY_HEAP_FREE 37
#define PYF_STREAK 0                    // PY_GET / PY_SET fields
#define PYF_RECORD 1
#define PYF_FLOOR 2
// PY_SLOT_KIND
#define PYK_TRAINER 0
#define PYK_ITEM 1
#define PYK_BEATEN 2
#define PYK_NONE 3
// PY_BRAIN (Emerald's FRONTIER_BRAIN_*)
#define PY_BRAIN_NOT_READY 0
#define PY_BRAIN_SILVER 1
#define PY_BRAIN_GOLD 2
#define PY_BRAIN_STREAK 3
#define PY_BRAIN_STREAK_LONG 4
#define PY_ST_IN_CHALLENGE 99           // FR_STATUS while walking the Pyramid (frontier_pike's convention)

    .macro EmPyr var, op, a=0           // command 530 (frontier_pyramid.c PY_Cmd)
    FieldCommand 530
    .2byte \var
    .2byte \op
    .2byte \a
    .endm

#endif
