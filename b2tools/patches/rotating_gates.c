/* Gen 3's rotating gates (th_p6, 2026-10-19; notes/TRICK_HOUSE.md "P6"): Trick House Puzzle 6 and Fortree Gym (fortree_gates
 * 2026-10-20: sPuzzles, one gate table per zone, as Gen 3's GetCurrentMapRotatingGatePuzzleType). A port of
 * pokeruby/pokeemerald src/rotating_gate.c: walking into a
 * gate's arm turns the gate 90 degrees if nothing on the map is in the arm's way (you walk through), else you bump.
 * Compiled and placed in ITCM by b2tools/patches/rotating_gates.py, which writes rotating_gates_gen.h (the decomp's
 * tables and this version's gates) and has the findings (hooks and why).
 *
 * Geometry (as Gen 3): a gate's pivot is the north-west corner of its tile (x, y); its arms lie on tile edges, a short
 * arm 1 tile long, a long one 2. Walking from one tile into the next across an edge that holds an arm is what turns
 * the gate (the 4x4 tables RotationInfo*: the destination tile around the pivot -> the arm hit and the turn).
 *
 * State: the gate's quarter turns since the room was entered, (orientation - start) & 3, in the room's map-local work
 * 0x4000 + gate (the gate's number in its zone's table; Gen 3 keeps them in VAR_TEMP_*): Black 2 clears map-local works at every zone init, so entering the
 * room resets every gate as RotatingGate_InitPuzzle does, and battles and menus keep them.
 *
 * Drawing: every arm is a 3D actor (zone NPC, uid GATE_UID0 + 4 * gate + shape arm, object code GATE_CODE_SHORT or
 * _LONG: a rail pointing north from the model's origin) standing on a tile next to the pivot. Black 2's 3D actors never
 * turn (ov036's one 3D draw processor only sets the position), so Gate_Update3D runs after it and sets the arm's turn,
 * moves the model's origin onto the pivot, animates a quarter turn and takes the arm out of Black 2's actor collision
 * (actor flag 0x80, func_ov012_02167580's "no collision": the gate's own check decides). */
typedef unsigned char u8;
typedef signed char s8;
typedef unsigned short u16;
typedef short s16;
typedef unsigned int u32;
typedef int s32;

#include "rotating_gates_gen.h"   /* sPuzzles, sGates, sRotInfo, sArmPos, sArmLayout, GATE_* constants */

/* Black 2 functions (decomp symbols, config/b2_us/arm9/...; Thumb: address | 1) */
#define FN(type, addr) ((type)((addr) | 1))
#define PlayerMoveCollCheck        FN(u32 (*)(void *, void *, u32, u32 *), 0x0219c88c)   /* ov036 */
#define Draw3DActor                FN(void (*)(void *), 0x021974b4)                      /* ov036 3D draw processor */
#define GetActorMModelSystem       FN(void *(*)(void *), 0x021670fc)                     /* ov012 */
#define GetMMSysField              FN(void *(*)(void *), 0x02166fac)
#define GetMMSysG3DMapper          FN(void *(*)(void *), 0x02166fa4)
#define Field_GetGameSystem        FN(void *(*)(void *), 0x021804bc)                     /* ov036 */
#define Field_GetPlayerStateZoneID FN(u16 (*)(void *), 0x021804d8)
#define GSYS_GetGameData           FN(void *(*)(void *), 0x02016ad8)                     /* arm9 */
#define GameData_GetEventWork      FN(void *(*)(void *), 0x02017394)
#define EventWork_GetWkPtr         FN(u16 *(*)(void *, u32), 0x02019294)
#define GetTileTypeAtPos           FN(u32 (*)(void *, s32 *), 0x021a29d0)                /* ov036 */
#define MapTile_BlocksCollision    FN(u32 (*)(u32), 0x021a2a18)
#define FldAct_GetBlActWorkPtr     FN(u16 *(*)(void *), 0x02167170)                      /* ov012 */
#define FldAct_GetG3DObjSystem     FN(void *(*)(void *), 0x02194708)                     /* ov036 */
#define G3DObj_GetTransform        FN(s32 *(*)(void *, u32), 0x021c0134)                 /* FieldG3DObjSystem_GetObjTransform */
#define MAT3_RotationEulerZYX      FN(void (*)(u32, u32, u32, void *), 0x020507d4)       /* arm9 */
#define GFL_SndSEPlay              FN(void (*)(u32), 0x02006254)

/* FieldActor (pokebw2 include/field/field_actor_internal.h) */
#define ACT_FLAGS(a)   (*(u32 *)((u8 *)(a) + 0x00))
#define ACT_UID(a)     (*(u16 *)((u8 *)(a) + 0x08))
#define ACT_CODE(a)    (*(u16 *)((u8 *)(a) + 0x0C))
#define ACT_PARAM2(a)  (*(u16 *)((u8 *)(a) + 0x24))   /* zone NPC param 2: unused by a 3D actor; here the turn animation */
#define ACT_GX(a)      (*(s16 *)((u8 *)(a) + 0x3C))   /* gPos */
#define ACT_GY(a)      (*(s16 *)((u8 *)(a) + 0x3E))
#define ACT_GZ(a)      (*(s16 *)((u8 *)(a) + 0x40))
#define ACT_WY(a)      (*(s32 *)((u8 *)(a) + 0x48))   /* wPos.y */
/* MMSys */
#define MM_CAPACITY(m) (*(u16 *)((u8 *)(m) + 0x04))
#define MM_ACTORS(m)   (*(u8 **)((u8 *)(m) + 0x1C))
#define ACTOR_SIZE     0x100
#define ACT_NO_COLL    0x80

#define ROT_ACW 1          /* ROTATE_ANTICLOCKWISE */
#define ROT_CW  2          /* ROTATE_CLOCKWISE */
#define TURN_FRAMES 8      /* the quarter turn's animation (frames; a power of 2) */
#define TURN_SHIFT 11      /* 0x4000 / TURN_FRAMES = 1 << TURN_SHIFT */

typedef const u8 GateDef[4];       /* sGates row: x, y, shape, orientation */

/* The gates of the player's zone (GetCurrentMapRotatingGatePuzzleType + RotatingGate_InitPuzzle's table), 0 elsewhere */
static GateDef *ZoneGates(void *field, u32 *count)
{
    u32 zone = Field_GetPlayerStateZoneID(field), i;
    for (i = 0; i < GATE_PUZZLES; i++) {
        if (sPuzzles[i][0] == zone) {
            *count = sPuzzles[i][2];
            return sGates + sPuzzles[i][1];
        }
    }
    *count = 0;
    return 0;
}

static u16 *GateWork(void *field, u32 gate)
{
    return EventWork_GetWkPtr(GameData_GetEventWork(GSYS_GetGameData(Field_GetGameSystem(field))), 0x4000 + gate);
}

static u32 GateOrientation(void *field, GateDef *gates, u32 gate)
{
    return (gates[gate][3] + *GateWork(field, gate)) & 3;
}

/* RotatingGate_HasArm */
static u32 HasArm(void *field, GateDef *gates, u32 gate, u32 armInfo)
{
    u32 arm = armInfo >> 1, isLong = armInfo & 1;
    u32 armOrientation = (arm - GateOrientation(field, gates, gate) + 4) & 3;
    return sArmLayout[gates[gate][2]][armOrientation * 2 + isLong];
}

/* RotatingGate_CanRotate: no map collision where the arms sweep (Gen 3 checks the map only) */
static u32 CanRotate(void *field, void *mmsys, s32 y, GateDef *gates, u32 gate, u32 rot)
{
    u32 orientation = GateOrientation(field, gates, gate), shape = gates[gate][2], i, j;
    const s8 (*armPos)[2] = sArmPos[rot == ROT_CW];
    s32 pos[3];
    for (i = 0; i < 4; i++) {
        for (j = 0; j < 2; j++) {
            u32 armIndex = 2 * ((orientation + i) & 3) + j;
            if (!sArmLayout[shape][2 * i + j])
                continue;
            pos[0] = ((gates[gate][0] + armPos[armIndex][0]) << 16) + 0x8000;
            pos[1] = y;
            pos[2] = ((gates[gate][1] + armPos[armIndex][1]) << 16) + 0x8000;
            if (MapTile_BlocksCollision(GetTileTypeAtPos(GetMMSysG3DMapper(mmsys), pos)))
                return 0;
        }
    }
    return 1;
}

/* RotatingGate_RotateInDirection + the arms' animation (RotatingGate_TriggerRotationAnimation) and SE_ROTATING_GATE */
static void Rotate(void *field, void *mmsys, u32 gate, u32 rot)
{
    u16 *w = GateWork(field, gate);
    u8 *a = MM_ACTORS(mmsys);
    u32 i, uid0 = GATE_UID0 + 4 * gate;
    *w = (*w + (rot == ROT_CW ? 1 : 3)) & 3;
    for (i = 0; i < MM_CAPACITY(mmsys); i++, a += ACTOR_SIZE) {
        u32 code = ACT_CODE(a);
        if ((ACT_FLAGS(a) & 1) && (code == GATE_CODE_SHORT || code == GATE_CODE_LONG)
            && ACT_UID(a) >= uid0 && ACT_UID(a) < uid0 + 4)
            ACT_PARAM2(a) = (u16)(rot << 8 | TURN_FRAMES);
    }
    GFL_SndSEPlay(GATE_SE);
}

/* CheckForRotatingGatePuzzleCollision, after Black 2's own check found nothing in the way (Gen 3: COLLISION_NONE) */
u32 Gate_MoveCollCheck(void *grid, void *actor, u32 dir, u32 *tile)
{
    u32 result = PlayerMoveCollCheck(grid, actor, dir, tile), i, count;
    void *mmsys, *field;
    GateDef *gates;
    s32 x, z;
    if (result || dir > 3)
        return result;
    mmsys = GetActorMModelSystem(actor);
    field = GetMMSysField(mmsys);
    gates = ZoneGates(field, &count);
    x = ACT_GX(actor) + (dir == 3) - (dir == 2);
    z = ACT_GZ(actor) + (dir == 1) - (dir == 0);
    for (i = 0; i < count; i++) {
        s32 gx = gates[i][0], gy = gates[i][1];
        if (gx - 2 <= x && x <= gx + 1 && gy - 2 <= z && z <= gy + 1) {
            u32 info = sRotInfo[dir][(z - gy + 2) * 4 + (x - gx + 2)];
            if (info != 0xFF && HasArm(field, gates, i, info & 0xF)) {
                if (!CanRotate(field, mmsys, ACT_WY(actor), gates, i, info >> 4))
                    return 4;                    /* an actor's collision bit: Black 2 bumps (no ledge check) */
                Rotate(field, mmsys, i, info >> 4);
                return 0;
            }
        }
    }
    return 0;
}

/* ov036's 3D draw processor, then the arms' turn */
void Gate_Update3D(void *a)
{
    u32 code = ACT_CODE(a), uid, gate, arm, dir, anim, frames, count;
    void *field;
    GateDef *gates;
    s32 *t, angle;
    Draw3DActor(a);
    if (code != GATE_CODE_SHORT && code != GATE_CODE_LONG)
        return;
    ACT_FLAGS(a) |= ACT_NO_COLL;
    field = GetMMSysField(GetActorMModelSystem(a));
    uid = ACT_UID(a) - GATE_UID0;
    gate = uid >> 2;
    arm = uid & 3;
    gates = ZoneGates(field, &count);
    if (uid >= 4 * count)                                     /* (no gates here: count 0) */
        return;
    dir = (arm + GateOrientation(field, gates, gate)) & 3;   /* the arm's direction now: 0 N, 1 E, 2 S, 3 W */
    angle = -(s32)(dir << 14);                                /* quarter turns clockwise seen from above */
    anim = ACT_PARAM2(a);
    frames = anim & 0xFF;
    if (frames) {                                             /* still turning from the previous direction */
        if ((anim >> 8) == ROT_CW)
            angle += (s32)(frames << TURN_SHIFT);
        else
            angle -= (s32)(frames << TURN_SHIFT);
        ACT_PARAM2(a) = frames > 1 ? (u16)(anim - 1) : 0;
    }
    t = G3DObj_GetTransform(FldAct_GetG3DObjSystem(a), *FldAct_GetBlActWorkPtr(a));
    t[0] += ((gates[gate][0] - ACT_GX(a)) << 16) - 0x8000;   /* the model's origin on the pivot (the tile's NW corner) */
    t[2] += ((gates[gate][1] - ACT_GZ(a)) << 16) - 0x8000;
    MAT3_RotationEulerZYX(0, (u32)angle & 0xFFFF, 0, t + 6);  /* GFL_G3D_OBJSTATUS: trans, scale, rotate (+0x18) */
}
