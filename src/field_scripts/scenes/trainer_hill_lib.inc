// Emerald's Trainer Hill (battle_tents, 2026-10-18; notes/BATTLE_TENTS.md): the rooms' shared pieces. The engine is
// b2tools/patches/trainer_hill.c (script command 562 `ThHill op, var`, the floors' per-step trainer eyes, the battle's
// two trainer slots 534/535); trainer_hill_lines.h (b2tools/trainer_hill_text.py) holds its numbers and the rooms' lines.
// Zones (data/emerald/hoenn_interiors.json): Entrance 543, 1F-4F 544-547 (the four modes' floors are each floor's alt
// rooms: map replace events 3 Variety, 4 Unique, 5 Expert), Roof 548, Elevator 549. Room tile = Emerald tile + origin.
#ifndef TRAINER_HILL_LIB_INC
#define TRAINER_HILL_LIB_INC
#include "trainer_hill_lines.h"

    .macro ThHill op, var                       // command 562 (Black 2's Cmd_0232: args any, var)
    FieldCommand 562
    .2byte \op
    .2byte \var
    .endm

#define TH_ENT_OX 1                             // TrainerHill_Entrance origin (1,1)
#define TH_ENT_OZ 1
#define TH_FL_OX 1                              // the floors (all four modes) (1,1)
#define TH_FL_OZ 1
#define TH_ROOF_OX 1                            // TrainerHill_Roof (1,-3)
#define TH_ROOF_OZ (-3)
#define TH_ELEV_OX 1                            // the elevator car (BattleTower_Elevator_Emerald) (1,1)
#define TH_ELEV_OZ 1
#define TH_EX(x) ((x) + TH_ENT_OX)
#define TH_EZ(z) ((z) + TH_ENT_OZ)

#define TH_F_ACTIVE 4                           // record key 60 bits (trainer_hill.c K_FLAGS)
#define TH_F_LOST 64
#define TH_F_SAVED 128
#define TH_BIT_PRIZE 4                          // (TH_OP_FLAG_SET / _CLEAR take the bit number)
#define TH_BIT_SAVED 7
#define TH_ACTIVE 0x4001                        // map-local work (Entrance): VAR_TRAINER_HILL_IS_ACTIVE for its triggers
#define TH_STATE 0x4000                         // map-local work (Entrance): the "back from the challenge" check ran
#define TH_PLAYER 255
#define TH_TEALA 1                              // the Entrance attendant (Emerald LOCALID_TRAINER_HILL_ATTENDANT)
#define TH_T0 FR_T0
#define TH_T1 FR_T1
#define TH_T2 FR_T2
#define TH_T3 FR_T3

    // the challenge's flags (record key 60) & mask -> var
    .macro th_flags_test mask, var
    ThHill TH_OP_FLAGS, \var
    WorkAnd \var, \mask
    .endm

    // a floor's zone init: which mode's layout (alt room) and trainers; floor 1-4
    .macro th_floor_init floor
    ThHill TH_OP_FLOOR_INIT | \floor, TH_T0     // TH_T0 = the mode (0 Normal .. 3 Expert); the other modes' trainers hidden
    th_alt 3, 1
    th_alt 4, 2
    th_alt 5, 3
    VMHalt
    .endm
    .macro th_alt ev, mode                      // map replace event ev on for this mode only (reload when it changes)
    WorkSetConst TH_T1, 0
    h_goto_if_ne TH_T0, \mode, .Ltha\@
    WorkSetConst TH_T1, 1
.Ltha\@:
    MapReplaceIsEventSet \ev, TH_T2
    h_goto_if_eq_var TH_T1, TH_T2, .Lthb\@
    MapReplaceSetEvent \ev, TH_T1, 1
.Lthb\@:
    .endm
#endif
