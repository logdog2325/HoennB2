/* Emerald's Battle Pyramid (frontier_pyramid, 2026-10-12): Pokemon Emerald NDS builds only. The engine: built
 * position-independent (clang -fropi) by b2tools/patches/frontier_pyramid.py, kept as a file of a/0/0/8 and loaded
 * into the game-event heap (heap 4) by the loader in ov036 (frontier_pyramid_ov036.c) while the player is in the
 * Pyramid; notes/FRONTIER_PYRAMID.md describes the facility, the scripts are src/field_scripts/emerald/0694-0841_*.s.
 *
 * Every entry gets the engine's own address first (eng): the engine keeps its RAM after its code (State, at
 * eng + hdr->size), the challenge's lasting state in the save (PySave: save block 0x3e after Black 2's 16 bytes).
 * Ports of pokeemerald src/battle_pyramid.c (floor templates, the 4x4 squares, object placement, pick-up items, hints,
 * the light, the wild Pokemon), battle_pyramid_bag.c / item.c (the Battle Bag: 10 slots of up to 99 per level mode),
 * frontier_util.c (Brandon's status and parties) and battle_tower.c (the Frontier trainer ranges, FillTrainerParty).
 *
 * The Battle Bag: while the player is in the Pyramid, GameData's bag pointer (GameData + 0x190, what every
 * GameData_GetBag caller reads: the field Bag, the party menu's give/take, the battle's BtlSetup) points at a Black 2
 * BagSave in State built from the save's ten slots, so the player's own Bag (save block 0x19) is never touched and is
 * there again as soon as the pointer is put back (lobby, a soft reset, Continue). The ten slots are written back after
 * every battle, item, menu and step (PY_SyncBag).
 */
typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef signed short s16;
typedef int s32;

#define FN(type, addr) ((type)((addr) | 1))
#define ScriptReadVar              FN(u16 *(*)(void *, void *), 0x021548e8)
#define ScriptReadAny              FN(u32 (*)(void *, void *), 0x02154910)
#define FieldScriptEnv_GetGameData FN(void *(*)(void *), 0x02155174)
#define FieldScriptEnv_GetHeapID   FN(u32 (*)(void *), 0x0215515c)
#define GameData_GetParty          FN(void *(*)(void *), 0x0201735c)
#define GameData_GetSaveControl    FN(void *(*)(void *), 0x02017934)
#define GameData_GetEventWork      FN(void *(*)(void *), 0x02017394)
#define GameData_GetEventData      FN(void *(*)(void *), 0x02017240)
#define EventWork_GetWkPtr         FN(u16 *(*)(void *, u32), 0x02019294)
#define EventWork_FlagSet          FN(void (*)(void *, u32), 0x020191d8)
#define EventWork_FlagReset        FN(void (*)(void *, u32), 0x02019200)
#define SaveControl_GetBlockPtr    FN(void *(*)(void *, u32), 0x02007448)
#define PokeParty_GetPkmCount      FN(u32 (*)(void *), 0x0201fdf8)
#define PokeParty_GetPkm           FN(void *(*)(void *, u32), 0x0201ff08)
#define PokeParty_GetParam         FN(u32 (*)(void *, u32, void *), 0x0201ccf8)
#define PokeParty_SetParam         FN(void (*)(void *, u32, u32), 0x0201cd1c)
#define PokeParty_SetMove          FN(void (*)(void *, u32, u32), 0x0201d224)
#define PokeParty_SetNature        FN(void (*)(void *, u32), 0x0201d5e0)
#define PokeParty_RecalcStats      FN(void (*)(void *), 0x0201d5f4)
#define PokeParty_CreatePkm        FN(void (*)(void *, u32, u32, u32, u32, u32, u32, u32), 0x0201c464)
#define PokeParty_AddPkm           FN(u32 (*)(void *, void *), 0x0201fd6c)
#define PokeParty_InitCore         FN(void (*)(void *, u32), 0x0201fd34)
#define PokeParty_GetPkmRawSize    FN(u32 (*)(void), 0x0201c2c8)
#define PokeParty_RemovePkm        FN(u32 (*)(void *, u32), 0x0201fda8)
#define GFL_HeapAllocate           FN(void *(*)(u32, u32, u32, u32, u32), 0x0203a1fc)
#define GFL_HeapFree               FN(void (*)(void *), 0x0203a24c)
#define GFL_ArcSysReadRange        FN(void (*)(void *, u32, u32, u32, u32), 0x0204a940)
#define GFL_StrBufLoadString       FN(void (*)(void *, const u16 *), 0x02048614)
#define GFL_RandomLC               FN(u32 (*)(u32), 0x02005748)
#define GFL_MsgSysLoadData         FN(void *(*)(u32, u32, u32, u32), 0x0204875c)
#define GFL_MsgDataFree            FN(void (*)(void *), 0x020487d4)
#define GFL_MsgDataLoadStrbuf      FN(void (*)(void *, u32, void *), 0x02048838)
#define BtlSetup_SetFlag           FN(void (*)(void *, u32), 0x02017d18)
#define BagSave_AddItem            FN(u32 (*)(void *, u32, u32, u32), 0x02008268)
#define BagSave_CheckAvailItemSpace FN(u32 (*)(void *, u32, u32, u32), 0x02008238)
#define EventScriptCall_Create     FN(void *(*)(void *, u32, void *, u32), 0x0215366c)
#define Field_GetActorSystem       FN(void *(*)(void *), 0x021804b8)
#define Field_GetPlayer            FN(void *(*)(void *), 0x021804f0)
#define Field_GetEncountSystem     FN(void *(*)(void *), 0x02180524)
#define Field_GetGameSystem        FN(void *(*)(void *), 0x021804bc)
#define FieldPlayer_GetActor       FN(void *(*)(void *), 0x0219a6a0)
#define FindFieldActor             FN(void *(*)(void *, u32), 0x02167a14)
#define GetActorFaceDir            FN(u32 (*)(void *), 0x02167078)
#define GetActorUserParam          FN(u32 (*)(void *, u32), 0x021670bc)
#define FldAct_GetGPos             FN(void (*)(void *, s16 *), 0x02167294)
#define TrainerEye_LineOfSight     FN(s32 (*)(u32, s32, s16 *, s16 *), 0x021a5fe0)
#define TrainerEye_PathObstacle    FN(u32 (*)(void *, u32, s32, void *), 0x021a6448)
#define FieldPropSystem_InstantiateFromInfo FN(void (*)(void *, void *, void *, u32), 0x021832f8)
#define g_SaveControl              (*(void **)0x02140f60)
#define udiv(a, b)                 (((u32 (*)(u32, u32))0x0208d868)((a), (b)))   /* __aeabi_uidivmod (ARM) */
#define memset_(p, v, n)           (((void (*)(void *, u32, u32))0x020787a8)((p), (v), (n)))
#define memcpy_(d, s, n)           (((void (*)(const void *, void *, u32))0x02078920)((s), (d), (n)))

#define P_SPECIES 0x05
#define P_ITEM    0x06
#define P_HAPPY   0x09
#define P_ABILITY 0x0a
#define P_EV_HP   0x0d
#define P_IV_HP   0x46
#define P_IS_EGG  0x4c
#define P_LEVEL   0x9e
#define P_HP      0xa0
#define A_STENCH 1
#define A_ILLUMINATE 35
#define A_INTIMIDATE 22
#define A_KEEN_EYE 51
#define I_CLEANSE_TAG 224
#define MOVE_FRUSTRATION 218

/* frontier_core's records (u16[96] after Black 2's 60 bytes of save block 0x38; notes/FRONTIER.md 2.2) */
#define K_STATUS 0
#define K_FACILITY 1
#define K_LVL_MODE 3
#define K_PARTY 4
#define K_BATTLE_NUM 5
#define K_SYMBOLS 6
#define K_STREAK(l) (16 + 8 * 6 + 2 * (l))      /* fr_streak(PYRAMID, singles, l); + 1 = fr_best */
#define FACILITY_PYRAMID 6
#define ST_IN_CHALLENGE 99

#include "frontier_pyramid_data.h"   /* generated by frontier_pyramid.py from data/emerald/frontier_pyramid.json */

/* the Pyramid's lasting state: save block 0x3e after Black 2's 16 bytes (frontier_pyramid.py SAVE_*) */
typedef struct {
    u16 magic;               /* PY_MAGIC once a challenge has been set up */
    u16 rnd[4];              /* Emerald's pyramidRandoms (the floor) */
    u16 trainerIds[8];       /* Frontier trainer of object i (0xFFFF none) */
    u8 trainerFlags;         /* beaten (bit = object index) */
    u8 itemFlags;            /* taken (bit = object index - the floor's trainers) */
    u8 light;                /* pyramidLightRadius (pixels) */
    u8 flags;                /* PF_* */
    u16 bagItem[2][10];      /* the Battle Bag of each level mode */
    u8 bagQty[2][10];
    u16 resX, resZ;          /* where Rest left the player */
    u8 resDir, arrival;      /* arrival: 0 the floor's entrance, 1 resX/resZ */
} PySave;
#define PF_STREAK_50 1
#define PF_STREAK_OPEN 2
#define PF_HEARD_BRAIN 4
#define PF_SESSION_SAVED 8   /* (spare) */

#define BAG_CURSOR_FIELD 0x1A    /* the field part of Black 2's bag cursor (scroll[6], index[6], pocket): bag_pocket */
typedef struct { u8 x, y, kind, src; } Obj;        /* floor tile, 0 trainer / 1 item, index in the square's list */
typedef struct {
    u8 bag[BAG_SIZE];        /* the Battle Bag as a Black 2 BagSave */
    u32 origBag;             /* the player's own bag pointer while swapped, 0 = not swapped */
    u16 key[5];              /* the floor cache's randoms + floor */
    u8 ready, nObj, nTr, entrance, exit;
    u8 lo[16];               /* layout offset (square layout 0-15) of each of the 16 squares */
    Obj obj[16];
    u8 wildIdx, wildLvl, wildPending, pad;
    u8 walls[128];           /* the floor's collision, a bit a tile (y * 32 + x) */
    u8 cursor[BAG_CURSOR_FIELD];   /* the player's own Bag's field cursor while swapped (bag_swap / bag_unswap) */
} State;

typedef struct { u32 magic, size, total, n, ent[12]; } Hdr;
static State *st(u8 *eng) { return (State *)(eng + ((((Hdr *)eng)->size + 3) & ~3)); }
#ifndef FR_REC_OFF          /* HOENN_SAVE_COMPAT=1 (save_compat.py, notes/SAVE_PKHEX.md): 64 and 20, after the blocks' footers */
#define FR_REC_OFF 60
#endif
#ifndef PY_SAVE_OFF
#define PY_SAVE_OFF 16
#endif
static u16 *rec(void *gd) {
    return (u16 *)((u8 *)SaveControl_GetBlockPtr(gd ? GameData_GetSaveControl(gd) : g_SaveControl, 0x38) + FR_REC_OFF);
}
static PySave *sv(void *gd) {
    return (PySave *)((u8 *)SaveControl_GetBlockPtr(gd ? GameData_GetSaveControl(gd) : g_SaveControl, 0x3e) + PY_SAVE_OFF);
}
static u32 rnd(u32 n) { return GFL_RandomLC(n); }
static u32 umod(u32 a, u32 b) { return a - udiv(a, b) * b; }
static u32 lvl(u16 *r) { return r[K_LVL_MODE] & 1; }
static u16 *streak(u16 *r) { return &r[K_STREAK(lvl(r))]; }
static u32 in_challenge(u16 *r) { return r[K_FACILITY] == FACILITY_PYRAMID && r[K_STATUS] == ST_IN_CHALLENGE; }
static u16 *wk(void *gd, u32 id) { return EventWork_GetWkPtr(GameData_GetEventWork(gd), id); }
static u32 pget(void *pkm, u32 p) { return PokeParty_GetParam(pkm, p, 0); }
static void rd(void *dst, u32 file, u32 off, u32 size) { GFL_ArcSysReadRange(dst, 8, file, off, size); }

/* ------------------------------------------------------------------------------------------- the floor (Emerald) */
static u32 template_id(PySave *s, u16 *r) {                       /* GetPyramidFloorTemplateId */
    u32 x = umod(s->rnd[3], 100), i;
    for (i = kTplOffsets[r[K_BATTLE_NUM] > 6 ? 6 : r[K_BATTLE_NUM]]; i < 34; i++)
        if (x < kTplOptions[i][0]) return kTplOptions[i][1];
    return 0;
}
static void layout_offsets(PySave *s, u32 id, u8 *lo) {           /* GetPyramidFloorLayoutOffsets */
    s32 x = (s32)(s->rnd[0] | (u32)s->rnd[1] << 16); u32 i;
    for (i = 0; i < 16; i++) {
        lo[i] = kTpl[id].lo[x & 7];
        x >>= 3;
        if (i == 7) { x = (s32)(s->rnd[2] | (u32)s->rnd[3] << 16); x >>= 8; }
    }
}
static void entrance_exit(PySave *s, u8 *en, u8 *ex) {            /* GetPyramidEntranceAndExitSquareIds */
    *en = umod(s->rnd[3], 16); *ex = umod(s->rnd[0], 16);
    if (*en == *ex) { *en = umod(s->rnd[3] + 1, 16); *ex = umod(s->rnd[0] + 15, 16); }
}
/* TrySetPyramidObjectEventPositionAtCoords: 0 = placed */
static u32 try_at(State *t, u32 type, u32 x, u32 y, u32 sq, u32 id) {
    u32 lay = t->lo[sq], i, j;
    for (i = 0; i < kSqObjN[lay]; i++) {
        const u8 *o = kSqObj[lay][i];
        if (o[0] != x || o[1] != y) continue;
        if (type == 0 && o[2] != 0) continue;            /* trainers: not an item ball; items: only item balls */
        if (type == 1 && o[2] != 1) continue;
        for (j = 0; j < id; j++)
            if (t->obj[j].x == x + (sq & 3) * 8 && t->obj[j].y == y + (sq >> 2) * 8) break;
        if (j == id) {
            t->obj[id].x = (u8)(x + (sq & 3) * 8); t->obj[id].y = (u8)(y + (sq >> 2) * 8);
            t->obj[id].kind = (u8)type; t->obj[id].src = (u8)i;
            return 0;
        }
    }
    return 1;
}
static u32 try_in_square(State *t, PySave *s, u32 type, u32 sq, u32 id) {   /* ...PositionInSquare: 0 = placed */
    s32 x, y;
    if (s->rnd[0] & 1) {
        for (y = 7; y > -1; y--) for (x = 7; x > -1; x--) if (!try_at(t, type, x, y, sq, id)) return 0;
    } else {
        for (y = 0; y < 8; y++) for (x = 0; x < 8; x++) if (!try_at(t, type, x, y, sq, id)) return 0;
    }
    return 1;
}
static void place_uniformly(State *t, PySave *s, u32 tpl, u32 type) {        /* SetPyramidObjectPositionsUniformly */
    u32 n = type ? kTpl[tpl].numItems : kTpl[tpl].numTrainers, start = type ? kTpl[tpl].numTrainers : 0, i;
    u32 sq = umod(s->rnd[2], 16), bits = 0;
    for (i = 0; i < n; i++) {
        do {
            do {
                if (bits & 1) { if (!((1u << sq) & s->rnd[3])) bits |= 2; }
                else { if ((1u << sq) & s->rnd[3]) bits |= 2; }
                if (++sq >= 16) sq = 0;
                if (sq == umod(s->rnd[2], 16)) { if (bits & 1) bits |= 6; else bits |= 1; }
            } while (!(bits & 2));
        } while (!(bits & 4) && try_in_square(t, s, type, sq, start + i));
        bits &= 1;
    }
}
static u32 place_in_and_near(State *t, PySave *s, u32 tpl, u32 type, u32 sq) {   /* ...InAndNearSquare */
    u32 n = type ? kTpl[tpl].numItems : kTpl[tpl].numTrainers, start = type ? kTpl[tpl].numTrainers : 0;
    u32 i, b = 0, r7 = 0, placed = 0;
    for (i = 0; i < n; i++) {
        if (r7 == 0) { if (try_in_square(t, s, type, sq, start + i)) r7 = 1; else placed++; }
        if (r7 & 1) {
            if (try_in_square(t, s, type, kBordered[sq][b], start + i)) {
                do {
                    b++;
                    if (b >= 4 || kBordered[sq][b] == 0xFF) b = 0;
                    r7 += 2;
                } while (r7 >> 1 != 4 && try_in_square(t, s, type, kBordered[sq][b], start + i));
                placed++;
            } else {
                b++;
                if (b >= 4 || kBordered[sq][b] == 0xFF) b = 0;
                placed++;
            }
        }
        if (r7 >> 1 == 4) break;
        r7 &= 1;
    }
    return (n / 2) > placed;
}
static u32 place_near(State *t, PySave *s, u32 tpl, u32 type, u32 sq) {         /* ...NearSquare */
    u32 n = type ? kTpl[tpl].numItems : kTpl[tpl].numTrainers, start = type ? kTpl[tpl].numTrainers : 0;
    u32 i, b = 0, r8 = 0, placed = 0;
    for (i = 0; i < n; i++) {
        if (try_in_square(t, s, type, kBordered[sq][b], start + i)) {
            do {
                b++;
                if (b >= 4 || kBordered[sq][b] == 0xFF) b = 0;
                r8++;
            } while (r8 != 4 && try_in_square(t, s, type, kBordered[sq][b], start + i));
            placed++;
        } else {
            b++;
            if (b >= 4 || kBordered[sq][b] == 0xFF) b = 0;
            placed++;
        }
        if (r8 == 4) break;
    }
    return (n / 2) > placed;
}
/* the floor of the save's randoms: layout, entrance/exit, objects (LoadBattlePyramidObjectEventTemplates) */
static State *floor_(u8 *eng, void *gd) {
    State *t = st(eng); PySave *s = sv(gd); u16 *r = rec(gd); u32 tpl, k, sq, x, y;
    if (t->ready && t->key[0] == s->rnd[0] && t->key[1] == s->rnd[1] && t->key[2] == s->rnd[2] && t->key[3] == s->rnd[3]
        && t->key[4] == r[K_BATTLE_NUM]) return t;
    tpl = template_id(s, r);
    layout_offsets(s, tpl, t->lo);
    entrance_exit(s, &t->entrance, &t->exit);
    memset_(t->obj, 0, sizeof t->obj);                           /* (CpuFill32 0: an unplaced object stays at 0,0) */
    for (k = 0; k < 2; k++) {
        u32 how = k ? kTpl[tpl].itemPos : kTpl[tpl].trainerPos;
        switch (how) {
        case 0: place_uniformly(t, s, tpl, k); break;
        case 1: if (place_in_and_near(t, s, tpl, k, t->entrance)) place_uniformly(t, s, tpl, k); break;
        case 2: if (place_in_and_near(t, s, tpl, k, t->exit)) place_uniformly(t, s, tpl, k); break;
        case 3: if (place_near(t, s, tpl, k, t->entrance)) place_uniformly(t, s, tpl, k); break;
        case 4: if (place_near(t, s, tpl, k, t->exit)) place_uniformly(t, s, tpl, k); break;
        }
    }
    t->nTr = kTpl[tpl].numTrainers; t->nObj = (u8)(kTpl[tpl].numTrainers + kTpl[tpl].numItems);
    memset_(t->walls, 0, sizeof t->walls);
    for (sq = 0; sq < 16; sq++)
        for (y = 0; y < 8; y++)
            for (x = 0; x < 8; x++)
                if (kSqWalls[t->lo[sq]][y] & (1 << x)) {
                    u32 i = ((sq >> 2) * 8 + y) * 32 + (sq & 3) * 8 + x;
                    t->walls[i >> 3] |= (u8)(1 << (i & 7));
                }
    for (k = 0; k < 4; k++) t->key[k] = s->rnd[k];
    t->key[4] = r[K_BATTLE_NUM]; t->ready = 1;
    return t;
}
/* an object is placed when it has a position: Emerald's template is all zeros otherwise (no localId: no object) */
static u32 obj_placed(State *t, u32 i) {
    return i < t->nObj && (t->obj[i].x || t->obj[i].y);         /* (no square has an object at its (0,0)) */
}
static void exit_tile(State *t, u32 *x, u32 *y) {
    *x = (t->exit & 3) * 8 + (kSqExit[t->lo[t->exit]] & 15); *y = (t->exit >> 2) * 8 + (kSqExit[t->lo[t->exit]] >> 4);
}
static void entrance_tile(State *t, u32 *x, u32 *y) {
    *x = (t->entrance & 3) * 8 + (kSqExit[t->lo[t->entrance]] & 15); *y = (t->entrance >> 2) * 8 + (kSqExit[t->lo[t->entrance]] >> 4);
}

/* GetRandomScaledFrontierTrainerId / GetUniqueTrainerId */
static u32 scaled_trainer(u32 c, u32 battle) {
    const u16 *rg = c > 7 ? kTrRange[7] : battle == 6 ? kTrRangeHard[c] : kTrRange[c];
    return rg[0] + rnd(rg[1] - rg[0] + 1);
}
static void choose_trainers(u8 *eng, void *gd) {
    State *t = floor_(eng, gd); PySave *s = sv(gd); u16 *r = rec(gd);
    u32 c = udiv(*streak(r), 7), f = r[K_BATTLE_NUM], i, j, id, tries;
    for (i = 0; i < 8; i++) s->trainerIds[i] = 0xFFFF;
    for (i = 0; i < t->nTr && i < 8; i++) {
        if (!obj_placed(t, i)) continue;
        tries = 0;
        do {
            id = scaled_trainer(f == 7 ? c + 1 : c, f);
            for (j = 0; j < i && s->trainerIds[j] != id; j++) ;
        } while (j != i && ++tries < 100);
        s->trainerIds[i] = (u16)id;
    }
}

/* ------------------------------------------------------------------------------------------- the Battle Bag */
/* The field Bag opens on its cursor's pocket (GameData + 0x18C -> Black 2's bag cursor, arm9 0x02008860-0x020088ee:
 * s16 scroll[6] at 0x00, s16 index[6] at 0x0C, u16 pocket at 0x18 = Items 0, Medicine 1, TMs 2, Berries 3, Key Items 4,
 * Free Space 5 (BagSave_GetPocketPtr's order); returning from the party screen sets it to the pocket of the item used).
 * pokeemerald's Pyramid Bag is one list with its own position (battle_pyramid_bag.c gPyramidBagMenuState), apart from the
 * player's Bag: here the player's field cursor is kept aside while the Battle Bag is swapped in, the Battle Bag starts at
 * the top of its first pocket with items, and whenever its pocket is empty (Items: the Battle Bag's are Medicine and
 * Berries; or the last of a pocket used) the Bag opens on the first pocket with items: checked when the field Bag opens
 * (PY_BagOpen, from ov012's bag launcher; also back from the party screen) and on every field frame of a floor. */
#define bag_cursor(gd) (*(u8 **)((u8 *)(gd) + 0x18C))
static u32 bag_pocket_has(const u8 *bag, u32 p) {                  /* BagSave pocket p (cursor order) holds an item */
    static const u16 kUi[5][2] = { { 0, 310 }, { 0x7d8 / 4, 48 }, { 0x624 / 4, 109 }, { 0x898 / 4, 64 }, { 0x4d8 / 4, 83 } };
    const u16 *slot = (const u16 *)bag; u32 j;
    if (p >= 5) return 0;                                         /* (Free Space: the Battle Bag registers none) */
    for (j = 0; j < kUi[p][1]; j++)
        if (slot[2 * (kUi[p][0] + j)] && slot[2 * (kUi[p][0] + j) + 1]) return 1;
    return 0;
}
static void bag_pocket_c(u8 *eng, u8 *c, u32 force) {              /* the Battle Bag's pocket: never an empty one */
    State *t = st(eng); u32 p, q;
    if (!t->origBag || !c) return;
    p = *(u16 *)(c + 0x18);
    if (!force && bag_pocket_has(t->bag, p)) return;
    for (q = 0; q < 5 && !bag_pocket_has(t->bag, q); q++) ;
    if (q == 5) return;                                            /* (an empty Battle Bag: left as it is) */
    *(u16 *)(c + 0x18) = (u16)q;
    ((s16 *)c)[q] = 0; ((s16 *)c)[6 + q] = 0;                     /* the top of that pocket */
}
static void bag_pocket(u8 *eng, void *gd, u32 force) { bag_pocket_c(eng, bag_cursor(gd), force); }
/* the field Bag opens (frontier_pyramid_stub.c PY_I_BagNew / PY_I_BagPocket, ov012's bag launcher): its cursor */
void PY_BagOpen(u8 *eng, u8 *cursor) { bag_pocket_c(eng, cursor, 0); }
static void bag_build(u8 *eng, void *gd, u32 heap) {               /* the ten slots -> the BagSave in State */
    State *t = st(eng); PySave *s = sv(gd); u32 l = lvl(rec(gd)), i;
    memset_(t->bag, 0, BAG_SIZE);
    for (i = 0; i < 10; i++)
        if (s->bagItem[l][i] && s->bagQty[l][i]) BagSave_AddItem(t->bag, s->bagItem[l][i], s->bagQty[l][i], heap);
}
static void bag_sync(u8 *eng, void *gd) {                         /* the BagSave -> the ten slots (Emerald's order kept) */
    State *t = st(eng); PySave *s = sv(gd); u32 l = lvl(rec(gd)), i, j, p, n = 0;
    u16 item[10]; u8 qty[10];
    static const u16 kPocket[3][2] = { { 0, 310 }, { 0x7d8 / 4, 48 }, { 0x898 / 4, 64 } };   /* items, medicine, berries */
    const u16 *slot = (const u16 *)t->bag;
    if (!t->origBag) return;
    for (i = 0; i < 10; i++) { item[i] = 0; qty[i] = 0; }
    for (i = 0; i < 10; i++) {                                    /* the slots that are still there, in their places */
        u32 have = 0;
        if (!s->bagItem[l][i]) continue;
        for (p = 0; p < 3; p++)
            for (j = 0; j < kPocket[p][1]; j++)
                if (slot[2 * (kPocket[p][0] + j)] == s->bagItem[l][i]) have += slot[2 * (kPocket[p][0] + j) + 1];
        if (have) { item[i] = s->bagItem[l][i]; qty[i] = (u8)(have > 99 ? 99 : have); }
    }
    for (p = 0; p < 3; p++)                                        /* new ones in the first empty slots */
        for (j = 0; j < kPocket[p][1]; j++) {
            u32 it = slot[2 * (kPocket[p][0] + j)], q = slot[2 * (kPocket[p][0] + j) + 1];
            if (!it || !q) continue;
            for (i = 0; i < 10 && item[i] != it; i++) ;
            if (i < 10) continue;
            for (i = 0; i < 10 && item[i]; i++) ;
            if (i < 10) { item[i] = (u16)it; qty[i] = (u8)(q > 99 ? 99 : q); }
        }
    for (i = 0; i < 10; i++) { s->bagItem[l][i] = item[i]; s->bagQty[l][i] = qty[i]; n += qty[i]; }
    (void)n;
}
static void bag_swap(u8 *eng, void *gd, u32 heap) {
    State *t = st(eng);
    if (t->origBag) return;
    bag_build(eng, gd, heap);
    t->origBag = *(u32 *)((u8 *)gd + 0x190);
    *(u32 *)((u8 *)gd + 0x190) = (u32)t->bag;
    if (bag_cursor(gd)) {                                         /* the player's Bag position aside, the Battle Bag's own */
        memcpy_(t->cursor, bag_cursor(gd), BAG_CURSOR_FIELD);
        memset_(bag_cursor(gd), 0, BAG_CURSOR_FIELD);
    }
    bag_pocket(eng, gd, 1);
}
static void bag_unswap(u8 *eng, void *gd) {
    State *t = st(eng);
    if (!t->origBag) return;
    bag_sync(eng, gd);
    *(u32 *)((u8 *)gd + 0x190) = t->origBag;
    t->origBag = 0;
    if (bag_cursor(gd)) memcpy_(bag_cursor(gd), t->cursor, BAG_CURSOR_FIELD);   /* the player's Bag position back */
}
static u32 bag_add(PySave *s, u32 l, u32 item, u32 count) {        /* AddPyramidBagItem: 1 = put away */
    u16 it[10]; u8 q[10]; u32 i;
    for (i = 0; i < 10; i++) { it[i] = s->bagItem[l][i]; q[i] = s->bagQty[l][i]; }
    for (i = 0; i < 10 && count; i++)
        if (it[i] == item && q[i] < 99) {
            u32 n = q[i] + count;
            if (n > 99) { count = n - 99; q[i] = 99; } else { q[i] = (u8)n; count = 0; }
        }
    for (i = 0; i < 10 && count; i++)
        if (!it[i]) { it[i] = (u16)item; q[i] = (u8)(count > 99 ? 99 : count); count = count > 99 ? count - 99 : 0; }
    if (count) return 0;
    for (i = 0; i < 10; i++) { s->bagItem[l][i] = it[i]; s->bagQty[l][i] = q[i]; }
    return 1;
}

/* ------------------------------------------------------------------------------------------- the zone's people */
typedef struct {                       /* ZoneNPC (pokebw2 include/field/field_actor.h) */
    u16 uid, model, move, evType, flag, script, dir, p0, p1, p2, areaW, areaH;
    u32 isRail; u16 x, z; s32 y;
} ZoneNPC;
/* the floor zone's NPCs 0-15 = Emerald's objects (trainers first, then items); scripts 1-16 (the object's talk
 * script), map-local flags 0x40-0x4F hide the ones this floor has not got or that were taken */
static void setup_people(u8 *eng, void *gd) {
    State *t = floor_(eng, gd); PySave *s = sv(gd);
    void *ed = GameData_GetEventData(gd), *ew = GameData_GetEventWork(gd);
    ZoneNPC *n = *(ZoneNPC **)((u8 *)ed + 0x20);
    u32 cnt = *(u16 *)((u8 *)ed + 0x14), i;
    for (i = 0; i < cnt && i < 16; i++) {
        u32 show = obj_placed(t, i);
        n[i].flag = (u16)(PY_HIDE_FLAG + i);
        n[i].evType = 0; n[i].areaW = n[i].areaH = 0; n[i].p0 = n[i].p1 = n[i].p2 = 0;
        n[i].script = (u16)(1 + i);
        if (show) {
            const u8 *o = kSqObj[t->lo[(t->obj[i].y >> 3) * 4 + (t->obj[i].x >> 3)]][t->obj[i].src];
            n[i].x = t->obj[i].x; n[i].z = t->obj[i].y;
            if (t->obj[i].kind == 0) {
                u16 tr[4];
                if (s->trainerIds[i] >= 300) show = 0;
                else {
                    rd(tr, PK_DAT, PK_OFF_TRAINERS + 24 * s->trainerIds[i], 8);
                    n[i].model = tr[1]; n[i].move = o[3]; n[i].dir = o[4]; n[i].p0 = o[5];
                    if (s->trainerFlags & (1 << i)) n[i].move = 3, n[i].areaW = n[i].areaH = 1;  /* beaten: wanders (Emerald) */
                }
            } else {
                n[i].model = PY_ITEM_BALL; n[i].move = 0; n[i].dir = 1;
                if (s->itemFlags & (1 << (i - t->nTr))) show = 0;
            }
        }
        if (show) EventWork_FlagReset(ew, PY_HIDE_FLAG + i);
        else EventWork_FlagSet(ew, PY_HIDE_FLAG + i);
    }
}

/* ------------------------------------------------------------------------------------------- the RD chunk hook */
/* the floor's chunk (an RD container: Join Avenue's kind, whose loader calls this with its terrain and props): the 16
 * squares' collision into the terrain (24-byte cells, ov036 FieldChunkAccessor_RD_GetTerrain), their wall models and
 * the exit's stairs as props (FieldPropSystem_InstantiateFromInfo; 32 a chunk) */
typedef struct { s16 na[3], nb[3]; s32 da, db; u32 tile; } RDCell;
typedef struct { s32 x, y, z; u16 rot; u8 hi, lo; } PropInfo;
u32 PY_RDHook(u8 *eng, u8 *terrain, void *props, void *chunk, u32 count) {
    void *gd = 0; State *t; u32 sq, x, y, ex, ey; PropInfo p;
    RDCell *c = (RDCell *)(terrain + 4);
    (void)gd;
    t = floor_(eng, 0);
    for (y = 0; y < 32; y++)
        for (x = 0; x < 32; x++) {
            u32 i = y * 32 + x, wall = (t->walls[i >> 3] >> (i & 7)) & 1;
            c[i].tile = wall ? PY_TILE_WALL : PY_TILE_FLOOR;
        }
    for (sq = 0; sq < 16 && count < 31; sq++) {
        p.x = ((sq & 3) * 128 - 256 + 64) << 12;                  /* the square's centre, from the chunk's centre */
        p.y = 0;
        p.z = -(((sq >> 2) * 128 - 256 + 64) << 12);              /* (z is stored negated) */
        p.rot = 0;
        p.hi = (u8)((PY_RES_SQUARE + t->lo[sq]) >> 8); p.lo = (u8)(PY_RES_SQUARE + t->lo[sq]);
        FieldPropSystem_InstantiateFromInfo(props, chunk, &p, count++);
    }
    exit_tile(t, &ex, &ey);
    p.x = (ex * 16 + 8 - 256) << 12; p.y = 0; p.z = -((ey * 16 + 8 - 256) << 12); p.rot = 0;
    p.hi = (u8)(PY_RES_STAIRS >> 8); p.lo = (u8)PY_RES_STAIRS;
    FieldPropSystem_InstantiateFromInfo(props, chunk, &p, count++);
    return count;
}

/* ------------------------------------------------------------------------------------------- per step */
static u32 wild_encounter(u8 *eng, void *gd) {                    /* StandardWildEncounter's Pyramid branch */
    u16 *r = rec(gd); State *t = st(eng);
    void *lead = PokeParty_GetPkm(GameData_GetParty(gd), 0);
    u32 f = r[K_BATTLE_NUM] > 6 ? 6 : r[K_BATTLE_NUM], rate = kWildRate[f] * 16, slot = 0, acc = 0, x;
    static const u8 kLandRates[12] = { 20, 20, 10, 10, 10, 10, 5, 5, 4, 4, 1, 1 };
    if (pget(lead, P_ITEM) == I_CLEANSE_TAG) rate = udiv(rate * 2, 3);
    if (!pget(lead, P_IS_EGG)) {
        u32 a = pget(lead, P_ABILITY);
        if (a == A_STENCH) rate = udiv(rate * 3, 4);
        else if (a == A_ILLUMINATE) rate *= 2;
    }
    if (rate > 2880) rate = 2880;
    if (rnd(2880) >= rate) return 0;
    x = rnd(100);                                                  /* ChooseWildMonIndex_Land */
    while (slot < 11 && x >= (acc += kLandRates[slot])) slot++;
    /* TryGenerateWildMon's Keen Eye / Intimidate check runs on the slot's placeholder level (5) */
    if (!pget(lead, P_IS_EGG)) {
        u32 a = pget(lead, P_ABILITY), pl = pget(lead, P_LEVEL);
        if ((a == A_KEEN_EYE || a == A_INTIMIDATE) && pl > 5 && 5 <= pl - 5 && rnd(2) == 0) return 0;
    }
    t->wildIdx = kWildSlots[f][slot];
    t->wildPending = 1;
    return 1;
}
/* returns the event to start, 0 none, 1 = not ours (the caller runs the next check) */
u32 PY_Step(u8 *eng, u8 *ctx, void *field) {
    void *gd = *(void **)(ctx + 8), *gsys = *(void **)(ctx + 4), *player, *asys, *enc;
    u16 *r = rec(gd); PySave *s = sv(gd); State *t; s16 pp[3]; u32 i, ex, ey, heap = *(u16 *)ctx;
    if (*(u16 *)(ctx + 16) != PY_ZONE_FLOOR || !in_challenge(r)) return 1;
    bag_pocket(eng, gd, 0);                                        /* (every field frame: the Bag never opens on an empty pocket) */
    if (!(ctx[60] & 0x10)) return 0;                               /* (only after a step) */
    t = floor_(eng, gd);
    bag_sync(eng, gd);
    player = FieldPlayer_GetActor(Field_GetPlayer(field));
    FldAct_GetGPos(player, pp);
    exit_tile(t, &ex, &ey);
    if ((u32)pp[0] == ex && (u32)pp[2] == ey)                      /* the exit panel: BattlePyramid_WarpToNextFloor */
        return (u32)EventScriptCall_Create(gsys, PY_SCR_EXIT, 0, heap);
    asys = Field_GetActorSystem(field); enc = Field_GetEncountSystem(field);
    for (i = 0; i < t->nTr && i < 8; i++) {                        /* a trainer who sees the player walks up */
        void *a; s16 ap[3]; s32 d; u32 dir;
        if (!obj_placed(t, i) || (s->trainerFlags & (1 << i))) continue;
        a = FindFieldActor(asys, i + 1);
        if (!a) continue;
        dir = GetActorFaceDir(a);
        FldAct_GetGPos(a, ap);
        d = TrainerEye_LineOfSight(dir, (s32)GetActorUserParam(a, 0), ap, pp);
        if (d == -1 || TrainerEye_PathObstacle(a, dir, d, enc)) continue;
        *wk(gd, PY_W_SLOT) = (u16)i;
        *wk(gd, PY_W_STEPS) = (u16)(d > 0 ? d - 1 : 0);
        *wk(gd, PY_W_DIR) = (u16)dir;
        return (u32)EventScriptCall_Create(gsys, PY_SCR_SPOTTED, a, heap);
    }
    if (wild_encounter(eng, gd)) return (u32)EventScriptCall_Create(gsys, PY_SCR_WILD, 0, heap);
    return 0;
}

/* ------------------------------------------------------------------------------------------- battles */
static u32 highest_level(void *gd) {
    void *party = GameData_GetParty(gd); u32 i, n = PokeParty_GetPkmCount(party), best = 0;
    for (i = 0; i < 3 && i < n; i++) {
        void *pkm = PokeParty_GetPkm(party, i);
        if (pget(pkm, P_SPECIES) && !pget(pkm, P_IS_EGG) && pget(pkm, P_LEVEL) > best) best = pget(pkm, P_LEVEL);
    }
    return best;
}
static u32 enemy_level(void *gd) {                                 /* GetFrontierEnemyMonLevel */
    u32 l;
    if (!lvl(rec(gd))) return 50;
    l = highest_level(gd);
    return l < 60 ? 60 : l;
}
static u32 fixed_iv(u32 t) {                                       /* GetFrontierTrainerFixedIvs */
    return t <= 99 ? 3 : t <= 119 ? 6 : t <= 139 ? 9 : t <= 159 ? 12 : t <= 179 ? 15 : t <= 199 ? 18 : t <= 219 ? 21 : 31;
}
static void make_mon(void *party, u32 heap, u32 species, u32 level, u32 iv, u32 nature, const u16 *moves, u32 item,
                     const u8 *evs) {
    void *pkm = GFL_HeapAllocate(heap, PokeParty_GetPkmRawSize(), 1, 0, 0);
    u32 j, happy = 255, ivs = iv | iv << 5 | iv << 10 | iv << 15 | iv << 20 | iv << 25;
    PokeParty_CreatePkm(pkm, species, level, 0, 0xFFFFFFFF, ivs, GFL_RandomLC(0), 0);
    PokeParty_SetParam(pkm, P_ITEM, item);
    for (j = 0; j < 4; j++) {
        PokeParty_SetMove(pkm, moves[j], j);
        if (moves[j] == MOVE_FRUSTRATION) happy = 0;
    }
    PokeParty_SetParam(pkm, P_HAPPY, happy);
    for (j = 0; j < 6; j++) PokeParty_SetParam(pkm, P_EV_HP + j, evs[j]);
    PokeParty_SetNature(pkm, nature);
    PokeParty_RecalcStats(pkm);
    PokeParty_AddPkm(party, pkm);
    GFL_HeapFree(pkm);
}
typedef struct { u16 cls, obj, list_off, list_n, name[8]; } TrainerRec;              /* frontier_pike's data file */
typedef struct { u16 species, moves[4], item; u8 nature, ev; u16 pad; } SetRec;
typedef struct { u16 species, item; u8 iv, nature, evs[6]; u16 moves[4], pad[2]; } BrainRec;
static void fill_party(void *gd, void *party, u32 t, u32 heap) {   /* FillTrainerParty (three) */
    TrainerRec tr; SetRec s; u16 picked[3], sp[3], it[3]; u32 level = enemy_level(gd), iv = fixed_iv(t), i = 0, j, tries = 0;
    u8 evs[6];
    rd(&tr, PK_DAT, PK_OFF_TRAINERS + 24 * t, sizeof tr);
    while (i < 3 && tries++ < 2000) {
        u16 id; u32 c, e;
        rd(&id, PK_DAT, PK_OFF_LISTS + 2 * (tr.list_off + rnd(tr.list_n)), 2);
        if (level == 50 && id > PK_HIGH_TIER) continue;
        rd(&s, PK_DAT, PK_OFF_SETS + 16 * id, sizeof s);
        for (j = 0; j < i && sp[j] != s.species; j++) ;
        if (j != i) continue;
        for (j = 0; j < i && !(it[j] && it[j] == s.item); j++) ;
        if (j != i) continue;
        for (j = 0; j < i && picked[j] != id; j++) ;
        if (j != i) continue;
        picked[i] = id; sp[i] = s.species; it[i] = s.item;
        for (c = 0, j = 0; j < 6; j++) c += (s.ev >> j) & 1;
        e = c ? udiv(510, c) & 0xFF : 0;
        for (j = 0; j < 6; j++) evs[j] = (u8)(((s.ev >> j) & 1) ? e : 0);
        make_mon(party, heap, s.species, level, iv, s.nature, s.moves, s.item, evs);
        i++;
    }
}
static u32 symbols(u16 *r) { u32 b = (r[K_SYMBOLS] >> 12) & 3; return (b & 1) + ((b >> 1) & 1); }
static u32 brain_status(u16 *r) {                                  /* GetFrontierBrainStatus (singles) */
    u32 w = *streak(r) + kBrainStreak[3], n = symbols(r);
    if (n < 2) return w == kBrainStreak[n] ? n + 1 : 0;
    if (w == kBrainStreak[0]) return 3;
    if (w == kBrainStreak[1] || (w > kBrainStreak[1] && umod(w - kBrainStreak[1], kBrainStreak[2]) == 0)) return 4;
    return 0;
}
static u32 brain_party(u16 *r) {                                   /* GetFronterBrainSymbol: 0 silver, 1 gold */
    u32 n = symbols(r), w = *streak(r) + kBrainStreak[3];
    if (n < 2) return n;
    return w == kBrainStreak[0] ? 0 : 1;
}
void PY_LoadParty(u8 *eng, void *setup, void *gd) {               /* after Black 2's: only the challenge's three */
    void *party;
    if (!in_challenge(rec(gd))) return;
    party = *(void **)((u8 *)setup + 36);
    while (PokeParty_GetPkmCount(party) > 3) PokeParty_RemovePkm(party, PokeParty_GetPkmCount(party) - 1);
}
void PY_LoadTrainer(u8 *eng, void *setup, void *gd, u32 client, void **pparty, u32 id, u32 heap) {
    u16 *r = rec(gd); PySave *s = sv(gd); u32 *tbs; TrainerRec tr; u32 t, i;
    if (!in_challenge(r) || (id != PY_TR && id != PY_TR_BRAIN)) return;
    tbs = *(u32 **)((u8 *)setup + 72 + 4 * client);
    PokeParty_InitCore(*pparty, 6);
    BtlSetup_SetFlag(setup, 0x200);                                 /* no experience (Emerald: BATTLE_TYPE_FRONTIER) */
    ((u16 *)(tbs + 3))[0] = ((u16 *)(tbs + 3))[1] = ((u16 *)(tbs + 3))[2] = ((u16 *)(tbs + 3))[3] = 0;
    if (id == PY_TR_BRAIN) {                                        /* CreateFrontierBrainPokemon: Brandon */
        static const u16 kBrandon[] = { 'B', 'r', 'a', 'n', 'd', 'o', 'n', 0xFFFF };
        BrainRec b; u32 sym = brain_party(r), level = enemy_level(gd);
        GFL_StrBufLoadString((void *)tbs[5], kBrandon);
        for (i = 0; i < 3; i++) {
            rd(&b, PY_DAT, PY_OFF_BRANDON + 24 * (3 * sym + i), sizeof b);
            make_mon(*pparty, heap, b.species, level, b.iv, b.nature, b.moves, b.item, b.evs);
        }
        return;
    }
    t = s->trainerIds[*wk(gd, PY_W_SLOT) & 7];
    if (t >= 300) t = 0;
    rd(&tr, PK_DAT, PK_OFF_TRAINERS + 24 * t, sizeof tr);
    tbs[1] = tr.cls;
    GFL_StrBufLoadString((void *)tbs[5], tr.name);
    fill_party(gd, *pparty, t, heap);
}
/* the battle's trainer lines: a beaten Pyramid trainer says Emerald's speechLose, Brandon his; -1 = not ours */
s32 PY_MsgExists(u8 *eng, u32 id, u32 type) {
    if ((id != PY_TR && id != PY_TR_BRAIN) || !in_challenge(rec(0))) return -1;
    return type == 1;
}
u32 PY_MsgLoad(u8 *eng, u32 id, u32 type, void *strbuf, u32 heap) {
    u16 *r = rec(0); PySave *s = sv(0); void *msg; u32 line;
    if ((id != PY_TR && id != PY_TR_BRAIN) || !in_challenge(r) || type != 1) return 0;
    if (id == PY_TR_BRAIN) line = PYL_FLOOR_BRANDON_LOSE + brain_party(r);
    else {
        u32 t = s->trainerIds[(s->flags >> 4) & 7];                /* (the slot of this battle: PY_TRAINER_PREP's) */
        line = PYL_FLOOR_LOSE + (t < 300 ? t : 0);
    }
    msg = GFL_MsgSysLoadData(0, 3, PY_TEXT_FLOOR, heap);
    GFL_MsgDataLoadStrbuf(msg, line, strbuf);
    GFL_MsgDataFree(msg);
    return 1;
}
void PY_EncSetup(u8 *eng, void *setup) {                           /* GenerateBattlePyramidWildMon */
    State *t = st(eng); void *gd = *(void **)((u8 *)setup + 112); u16 *r; u32 j;
    if (!t->wildPending) return;
    t->wildPending = 0;
    r = rec(gd);
    if (in_challenge(r)) {
        u16 w[6]; void *pkm = PokeParty_GetPkm(*(void **)((u8 *)setup + 40), 0);
        rd(w, PY_DAT, PY_OFF_WILD + 12 * (160 * lvl(r) + 8 * umod(udiv(*streak(r), 7), 20) + t->wildIdx), 12);
        for (j = 0; j < 4; j++) PokeParty_SetMove(pkm, w[2 + j], j);
        if (*streak(r) >= 140) {                                    /* (UBFIX: the level mode's streak) */
            u32 iv = rnd(17) + 15;
            for (j = 0; j < 6; j++) PokeParty_SetParam(pkm, P_IV_HP + j, iv);
            PokeParty_RecalcStats(pkm);
        }
    }
}

/* ------------------------------------------------------------------------------------------- hints */
static u32 exit_hint_index(State *t, u32 ox, u32 oy, u32 *type, u32 dist, u32 dflt) {   /* GetPostBattleDirectionHintTextIndex */
    u32 ex, ey; s32 x, y; u32 idx = 0;
    exit_tile(t, &ex, &ey);
    x = (s32)ex - (s32)ox; y = (s32)ey - (s32)oy;
    if (x >= (s32)dist || x <= -(s32)dist || y >= (s32)dist || y <= -(s32)dist || dflt == 0) {
        if (x > 0 && y > 0) idx = x >= y ? 2 : 3;
        else if (x < 0 && y < 0) idx = x > y ? 0 : 1;
        else if (x == 0) idx = y > 0 ? 3 : 0;
        else if (y == 0) idx = x > 0 ? 2 : 1;
        else if (x < 0) idx = x + y > 0 ? 3 : 1;
        else idx = x + y >= 0 ? 2 : 0;
        *type = 0;
    } else *type = dflt;
    return idx;
}
static u32 hint_line(u8 *eng, void *gd, u32 slot) {                /* ShowPostBattleHintText: the line */
    State *t = floor_(eng, gd); PySave *s = sv(gd); u32 type = kHintTypes[slot & 7], idx = 0, i, group, ox, oy;
    u8 g;
    rd(&g, PY_DAT, PY_OFF_GROUPS + (s->trainerIds[slot & 7] < 300 ? s->trainerIds[slot & 7] : 0), 1);
    group = g > 5 ? 0 : g;
    ox = t->obj[slot & 15].x; oy = t->obj[slot & 15].y;          /* (Emerald: the trainer's initial coordinates) */
    for (;;) {
        if (type == 0) { idx = exit_hint_index(t, ox, oy, &type, 8, 0); break; }
        if (type == 1) {
            for (i = t->nTr; i < t->nObj; i++) if (obj_placed(t, i) && !(s->itemFlags & (1 << (i - t->nTr)))) idx++;
            break;
        }
        if (type == 2) {
            idx = t->nTr;
            for (i = 0; i < 8; i++) if (s->trainerFlags & (1 << i)) idx--;
            break;
        }
        {
            static const u8 kDist[9] = { 0, 0, 0, 8, 8, 16, 16, 24, 24 };
            u32 dflt = (type & 1) ? 2 : 1;                         /* 3/5/7: trainers, 4/6/8: items */
            idx = exit_hint_index(t, ox, oy, &type, kDist[type], dflt);
            if (type == 0) break;
        }
    }
    return PYL_FLOOR_HINTS + 21 * group + (type == 0 ? idx : type == 1 ? 4 + (idx > 8 ? 8 : idx) : 13 + (idx > 7 ? 7 : idx));
}

/* ------------------------------------------------------------------------------------------- the script command */
enum { PY_INIT, PY_SEED, PY_SETUP, PY_START_X, PY_START_Z, PY_SLOT_KIND, PY_TRAINER_PREP, PY_TRAINER_WON, PY_HINT,
       PY_ITEM, PY_ITEM_TAKEN, PY_WILD, PY_WILD_LV, PY_LIGHT, PY_LIGHT_ADD, PY_BRAIN, PY_BRAIN_PARTY, PY_HEARD,
       PY_SET_HEARD, PY_STREAK_ACTIVE, PY_SET_STREAK_ACTIVE, PY_SYNC, PY_END, PY_HELD_TO_BAG, PY_ELIGIBLE,
       PY_PICKS_HOLD, PY_REST_POS, PY_ARRIVAL, PY_BAG_COUNT, PY_GET, PY_SET, PY_UNLOAD, PY_FLOOR_NO, PY_HINT_GIVER,
       PY_RESULTS, PY_TEST, PY_ALL_FAINTED, PY_HEAP_FREE };
#define PYF_STREAK 0
#define PYF_RECORD 1
#define PYF_FLOOR 2

static u32 eligible(void *gd, u32 l) {                            /* CheckPartyIneligibility, the Pyramid's: no held item */
    void *party = GameData_GetParty(gd); u32 n = PokeParty_GetPkmCount(party), i, j, k = 0; u16 sp[6];
    for (i = 0; i < n; i++) {
        void *pkm = PokeParty_GetPkm(party, i); u32 s = pget(pkm, P_SPECIES);
        u16 ban;
        if (!s || pget(pkm, P_IS_EGG) || pget(pkm, P_ITEM)) continue;
        if (l == 0 && pget(pkm, P_LEVEL) > 50) continue;
        for (j = 0; j < PY_N_BANNED; j++) { rd(&ban, PY_DAT, PY_OFF_BANNED + 2 * j, 2); if (ban == s) break; }
        if (j < PY_N_BANNED) continue;
        for (j = 0; j < k && sp[j] != s; j++) ;
        if (j < k) continue;
        sp[k++] = (u16)s;
    }
    return k;
}

u32 PY_Cmd(u8 *eng, void *vm, void *env) {
    u16 *var = ScriptReadVar(vm, env);
    u32 op = ScriptReadAny(vm, env) & 0xffff, a = ScriptReadAny(vm, env) & 0xffff;
    void *gd = FieldScriptEnv_GetGameData(env), *party = GameData_GetParty(gd);
    u32 heap = FieldScriptEnv_GetHeapID(env), i, l;
    u16 *r = rec(gd); PySave *s = sv(gd); State *t;
    l = lvl(r);
    switch (op) {
    case PY_INIT:                                                   /* InitPyramidChallenge (a = level mode) */
        r[K_FACILITY] = FACILITY_PYRAMID; r[K_LVL_MODE] = (u16)(a & 1); l = a & 1;
        r[K_STATUS] = 0; r[K_BATTLE_NUM] = 0;
        s->magic = PY_MAGIC;
        if (!(s->flags & (l ? PF_STREAK_OPEN : PF_STREAK_50))) {
            *streak(r) = 0;
            for (i = 0; i < 10; i++) { s->bagItem[l][i] = 0; s->bagQty[l][i] = 0; }   /* InitPyramidBagItems */
            bag_add(s, l, PY_START_ITEM0, 1); bag_add(s, l, PY_START_ITEM1, 1);
        }
        break;
    case PY_SEED:                                                   /* SeedPyramidFloor + the floor's trainers */
        for (i = 0; i < 4; i++) s->rnd[i] = (u16)rnd(0x10000);
        s->trainerFlags = 0; s->itemFlags = 0; s->light = 32; s->arrival = 0;
        st(eng)->ready = 0;
        choose_trainers(eng, gd);
        break;
    case PY_SETUP:                                                  /* zone init of the floor (and the top: a = 1) */
        if (a == 0) setup_people(eng, gd);
        bag_swap(eng, gd, heap);
        *var = (u16)st(eng)->nObj;
        break;
    case PY_START_X: case PY_START_Z: {                             /* where the player stands on arrival */
        u32 x, y;
        t = floor_(eng, gd);
        entrance_tile(t, &x, &y);
        if (s->arrival) { x = s->resX; y = s->resZ; }
        *var = (u16)(op == PY_START_X ? x : y);
        break; }
    case PY_SLOT_KIND:                                              /* 0 trainer, 1 item, 2 beaten trainer, 3 none */
        t = floor_(eng, gd);
        *var = !obj_placed(t, a) ? 3 : t->obj[a].kind ? 1 : (s->trainerFlags & (1 << a)) ? 2 : 0;
        break;
    case PY_TRAINER_PREP:                                           /* slot a: the greeting line (the slot -> flags 4-6) */
        s->flags = (u8)((s->flags & ~0x70) | ((a & 7) << 4));
        *wk(gd, PY_W_SLOT) = (u16)a;
        *var = (u16)(PYL_FLOOR_INTRO + (s->trainerIds[a & 7] < 300 ? s->trainerIds[a & 7] : 0));
        break;
    case PY_TRAINER_WON:                                            /* MarkPyramidTrainerAsBattled */
        s->trainerFlags |= (u8)(1 << (a & 7));
        break;
    case PY_HINT: *var = (u16)hint_line(eng, gd, a); break;
    case PY_ITEM: {                                                 /* SetPickupItem for object a: var = item id */
        u32 idx, x = 0, v, round = umod(udiv(*streak(r), 7), 20), f = r[K_BATTLE_NUM] > 6 ? 6 : r[K_BATTLE_NUM];
        u16 it;
        t = floor_(eng, gd);
        idx = (a - t->nTr) & 7;                                     /* (gSpecialVar_LastTalked - numTrainers) - 1 */
        v = s->rnd[idx / 2];                                        /* SeedRng2(pyramidRandoms[idx / 2]); Random2() % 100, */
        for (i = 0; i <= idx; i++) { v = 1103515245u * v + 24691u; x = umod((v >> 16) & 0xFFFF, 100); }   /* idx + 1 times */
        for (i = kPickupOffsets[f]; i < 63; i++) if (x < kPickupSlots[i][0]) break;
        if (i >= 63) i = 62;
        rd(&it, PY_DAT, PY_OFF_PICKUP + 2 * (200 * l + 10 * round + kPickupSlots[i][1]), 2);
        *var = it;
        break; }
    case PY_ITEM_TAKEN: {                                           /* var in: the item; a: the object. var = 1 put away */
        u32 item = *var;
        t = floor_(eng, gd);
        if (bag_add(s, l, item, 1)) {
            if (st(eng)->origBag) BagSave_AddItem(st(eng)->bag, item, 1, heap);
            s->itemFlags |= (u8)(1 << ((a - t->nTr) & 7));
            *var = 1;
        } else *var = 0;
        break; }
    case PY_WILD: {                                                 /* the pending wild Pokemon: var = species, PY_W_WILD_LV */
        u16 w[6]; u32 lv;
        t = st(eng);
        rd(w, PY_DAT, PY_OFF_WILD + 12 * (160 * l + 8 * umod(udiv(*streak(r), 7), 20) + t->wildIdx), 12);
        if (l) {
            lv = enemy_level(gd);
            lv = lv - (w[1] & 0xFF);
            lv = lv - 5 + rnd(11);
        } else lv = (w[1] & 0xFF) - 5 + rnd(11);
        *wk(gd, PY_W_WILD_LV) = (u16)lv;
        t->wildPending = 1;
        *var = w[0];
        break; }
    case PY_LIGHT: *var = (u16)((s->light ? s->light : 32) * 32); break;     /* h_flash_scale's scale: FLASH_PX(px) */
    case PY_LIGHT_ADD: { u32 x = s->light + a; s->light = (u8)(x > 120 ? 120 : x); *var = (u16)(s->light * 32); break; }
    case PY_BRAIN: *var = (u16)brain_status(r); break;
    case PY_BRAIN_PARTY: *var = (u16)brain_party(r); break;
    case PY_HEARD: *var = (s->flags & PF_HEARD_BRAIN) != 0; break;
    case PY_SET_HEARD: s->flags |= PF_HEARD_BRAIN; break;
    case PY_STREAK_ACTIVE: *var = (s->flags & (l ? PF_STREAK_OPEN : PF_STREAK_50)) != 0; break;
    case PY_SET_STREAK_ACTIVE:
        if (a) s->flags |= (l ? PF_STREAK_OPEN : PF_STREAK_50); else s->flags &= ~(l ? PF_STREAK_OPEN : PF_STREAK_50);
        break;
    case PY_SYNC: bag_sync(eng, gd); break;
    case PY_END:                                                    /* back in the lobby: the player's own Bag */
        bag_unswap(eng, gd);
        if (a) for (i = 0; i < 10; i++) { s->bagItem[l][i] = 0; s->bagQty[l][i] = 0; }   /* (a lost challenge) */
        break;
    case PY_HELD_TO_BAG: {                                          /* TryStoreHeldItemsInPyramidBag: 1 = no room */
        u16 sb[10]; u8 sq[10]; u32 n = PokeParty_GetPkmCount(party);
        for (i = 0; i < 10; i++) { sb[i] = s->bagItem[l][i]; sq[i] = s->bagQty[l][i]; }
        for (i = 0; i < 3 && i < n; i++) {
            u32 it = pget(PokeParty_GetPkm(party, i), P_ITEM);
            if (it && !bag_add(s, l, it, 1)) {
                for (i = 0; i < 10; i++) { s->bagItem[l][i] = sb[i]; s->bagQty[l][i] = sq[i]; }
                *var = 1;
                return 0;
            }
        }
        for (i = 0; i < 3 && i < n; i++) PokeParty_SetParam(PokeParty_GetPkm(party, i), P_ITEM, 0);
        *var = 0;
        break; }
    case PY_ELIGIBLE: *var = (u16)eligible(gd, a & 1); break;
    case PY_PICKS_HOLD:                                             /* a pick holds an item (Emerald's lobby refuses it) */
        *var = 0;
        for (i = 0; i < 3; i++) {
            u32 p = (r[K_PARTY] >> (4 * i)) & 15;
            if (p && pget(PokeParty_GetPkm(party, p - 1), P_ITEM)) { *var = (u16)p; break; }
        }
        break;
    case PY_REST_POS:                                               /* var = x, a = z (works), then the dir */
        s->resX = *var; s->resZ = (u16)a; s->arrival = 1;
        break;
    case PY_ARRIVAL: s->arrival = (u8)a; break;
    case PY_BAG_COUNT:                                              /* how many items the Battle Bag holds */
        *var = 0;
        for (i = 0; i < 10; i++) *var += s->bagQty[l][i];
        break;
    case PY_GET:
        *var = a == PYF_STREAK ? *streak(r) : a == PYF_RECORD ? streak(r)[1] : r[K_BATTLE_NUM];
        break;
    case PY_SET:
        if (a == PYF_STREAK) { *streak(r) = *var; if (streak(r)[1] < *var) streak(r)[1] = *var; }
        else if (a == PYF_FLOOR) r[K_BATTLE_NUM] = *var;
        break;
    case PY_UNLOAD: bag_unswap(eng, gd); return 0x100;               /* (the loader frees the engine) */
    case PY_FLOOR_NO: *var = (u16)(r[K_BATTLE_NUM] + 1); break;
    case PY_HINT_GIVER: {                                           /* GetBattlePyramidHint: the lobby's fortune */
        u32 st_ = (s->flags & (a ? PF_STREAK_OPEN : PF_STREAK_50)) ? r[K_STREAK(a & 1)] : 0;
        *var = (u16)umod(udiv(st_, 7), 20);
        break; }
    case PY_RESULTS:                                                /* the results board: var = level a's streak, word use */
        *var = r[K_STREAK(a & 1)];
        break;
    case PY_ALL_FAINTED:                                            /* none of the three can battle (lost or drew) */
        *var = 1;
        for (i = 0; i < 3 && i < PokeParty_GetPkmCount(party); i++) {
            void *pkm = PokeParty_GetPkm(party, i);
            if (pget(pkm, P_SPECIES) && !pget(pkm, P_IS_EGG) && pget(pkm, P_HP)) { *var = 0; break; }
        }
        break;
    case PY_HEAP_FREE: *var = (u16)(((u32 (*)(u32))(0x0203a2a8 | 1))(a) >> 4); break;   /* (test: heap a's free / 16) */
    case PY_TEST:                       /* reserved (the test switch that set the streak and the floor was removed) */
        break;
    }
    return 0;
}

/* ------------------------------------------------------------------------------------------- the Start menu's Save */
/* in the Pyramid the Start menu's Save runs the floor's Rest / Retire script (Emerald's Start menu: REST, RETIRE) */
u32 PY_SaveMenu(u8 *eng, void *gsys, u32 zone, u32 heap) {
    void *gd = (void *)(((u32 (*)(void *))(0x02016ad8 | 1))(gsys));   /* GSYS_GetGameData */
    if ((zone != PY_ZONE_FLOOR && zone != PY_ZONE_TOP) || !in_challenge(rec(gd))) return 0;
    bag_sync(eng, gd);
    return (u32)EventScriptCall_Create(gsys, zone == PY_ZONE_FLOOR ? PY_SCR_MENU : PY_SCR_MENU_TOP, 0, heap);
}
