/* Berry planting (HOENN_BERRY_PLANTING; notes/BERRY_PLANTING.md): Gen 3's berry trees, pokeemerald src/berry.c (the same
 * rules as pokeruby's), on Black 2. Compiled and placed in ITCM by b2tools/patches/berries.py, which has the hooks:
 *   - script command 612 (BerryCmd op, arg): the tree script's specials (file 1241 Script_300, global 8299);
 *   - ov012 GetWKOBJCODENPCOBJCODE -> Berry_ResolveCode: a tree actor's object code VCODE_BASE + tree id becomes the
 *     picture of its berry and stage when the actor is created (zone spawn, ActorAdd);
 *   - arm9 GetIndexOfObjID -> Berry_ObjIndex: Black 2's ranges, plus the picture codes PIC_CODE_BASE + i -> the records
 *     appended to a/0/4/7 (REC_BASE + i).
 *
 * Save: Black 2's save block 0x47 (Pokéstar Studios, 996 bytes; no Hoenn place reaches the studios):
 *   +0   u32 magic BERRY_MAGIC (absent: the block still holds Black 2's Pokéstar data -> Gen 3's new-game trees)
 *   +4   u32 the DS clock (minutes since 2000-01-01 00:00) of the last growth update (Gen 3 lastBerryTreeUpdate)
 *   +8   u8  the version that set the trees up (HOENN_VERSION_ID), 3 bytes 0
 *   +12  BerryTree[128] (Gen 3's struct, 6 bytes: berry, stage | stopGrowth << 7, minutes until the next stage, yield,
 *        regrowth count | watered bits << 4), tree id = Gen 3's (1-89 used): the actor's tile tells which
 *   780 bytes used; the block keeps Black 2's size, so its CRC, the save's CRC table and PKHeX's checks stay valid.
 */
typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef int s32;

#define FN(type, addr) ((type)((addr) | 1))
#define SaveControl_GetInstance    FN(void *(*)(void), 0x020072fc)
#define SaveControl_GetBlockPtr    FN(u8 *(*)(void *, u32), 0x02007448)
#define BagSave_GetItemCountByID   FN(u32 (*)(void *, u32, u32), 0x02008538)
#define BagCursor_SetPocket        FN(void (*)(void *, u32), 0x020088a4)   /* func_020088a4: u16 +24 of the Bag cursor = the
                                                                            pocket the Bag opens on (the Bag stores its last
                                                                            pocket there: ov142 func_ov142_02199a5c; tested) */
#define GameData_GetBagCursor      FN(void *(*)(void *), 0x0201734c)       /* func_0201734c */
#define GameData_GetBag            FN(void *(*)(void *), 0x02017354)
#define EventWork_GetWkPtr         FN(u16 *(*)(void *, u32), 0x02019294)
#define GFL_RandomLCAlt            FN(u32 (*)(u32), 0x02005784)            /* random in [0, n) */
#define RTC_GetCachedDateTime      FN(void (*)(void *, void *), 0x02044210)
#define RTC_ConvertDateToDay       FN(s32 (*)(const void *), 0x0207d0b4)   /* NitroSDK RTC_ConvertDateToDay: days since 2000 */
/* ov012 (the field's script overlay) */
#define ScriptWork_GetParentActor  FN(void *(*)(void *), 0x02153ee0)       /* the actor whose talk started the script */
#define ScriptWork_GetWkAddr       FN(u16 *(*)(void *, void *, u32), 0x02153f30)
#define ScriptReadAny              FN(u32 (*)(void *, void *), 0x02154910)
#define FieldScriptEnv_GetGameData FN(void *(*)(void *), 0x02155174)
#define FieldScriptEnv_GetScriptWork FN(void *(*)(void *), 0x02155184)
#define FieldScriptEnv_FindActor   FN(void *(*)(void *, u32), 0x02164db4)
#define GetActorUID                FN(u32 (*)(void *), 0x02167008)
#define GetGPosX                   FN(s32 (*)(void *), 0x021672a8)       /* the actor's tile (s16) */
#define GetGPosZ                   FN(s32 (*)(void *), 0x021672d8)
#define FldAct_GetObjCode          FN(u32 (*)(void *), 0x02167018)

#include "berries_data.h"     /* berries.py: kBerry, kPic, kInit, kTreeX/Z, VCODE_BASE, PIC_CODE_BASE, N_PICS, REC_BASE */

#define BERRY_MAGIC 0x33595242u   /* "BRY3" */
#define SAVE_BLOCK 0x47
#define N_TREES 128               /* BERRY_TREES_COUNT */
#define HEAPID_GAMEEVENT 4
#define POCKET_BERRIES 3          /* BagSave_GetPocketPtr: 0 items, 1 medicine, 2 TMs, 3 berries, 4 key items */

enum { STAGE_NO_BERRY, STAGE_PLANTED, STAGE_SPROUTED, STAGE_TALLER, STAGE_FLOWERING, STAGE_BERRIES };
/* BerryCmd ops (src/field_scripts/1241_hidden_items.s, the HOENN_BERRY_PLANTING part) */
enum { OP_GET, OP_PLANT, OP_WATER, OP_PICK, OP_HAS_BERRIES, OP_BAG_POCKET, OP_UPDATE };
/* results, in the script's local works */
#define W_STAGE   0x8004          /* the stage 0-5 (Gen 3 VAR_0x8004) */
#define W_WATER   0x8005          /* times watered 0-4 (VAR_0x8005) */
#define W_YIELD   0x8006          /* berries on the tree (VAR_0x8006) */
#define W_ITEM    0x8007          /* the tree's berry as a Black 2 item (0: none) */
#define W_REFRESH 0x8008          /* 1: the actor shows another picture than the tree's: ActorDelete + ActorAdd it */
#define W_UID     0x8009          /* the tree actor's uid (for ActorDelete / ActorAdd) */
#define W_TREE    0x800d          /* the tree id + 1 (0: no tree), kept from OP_GET for the later ops */
#define W_RESULT  0x800b          /* OP_PLANT: 1 planted (0: not a Gen 3 berry); OP_HAS_BERRIES: 1 when the Bag has one */

typedef struct {
    u8 berry;                     /* Gen 3 berry 1-43, 0 none */
    u8 stage;                     /* bits 0-6 stage, bit 7 stopGrowth (not seen yet: a new game's tree waits) */
    u16 minutes;                  /* minutesUntilNextStage */
    u8 yield;                     /* berryYield */
    u8 flags;                     /* bits 0-3 regrowthCount, bit 4 + n: watered at stage n + 1 */
} BerryTree;

typedef struct {
    u32 magic;
    u32 last;
    u8 version, pad[3];
    BerryTree trees[N_TREES];
} BerrySave;

#define STOP 0x80
#define STAGE(t) ((t)->stage & 0x7f)

/* ---- Gen 3 rules (pokeemerald src/berry.c) ---------------------------------------------------------------------- */

static u32 stage_minutes(u32 berry) { return kBerry[berry - 1][0] * 60u; }     /* GetStageDurationByBerryType */

static u32 times_watered(const BerryTree *t) {                                   /* BerryTreeGetNumStagesWatered */
    u32 n = 0, w = t->flags >> 4;
    while (w) { n += w & 1; w >>= 1; }
    return n;
}

static u32 calc_yield(const BerryTree *t) {                                      /* CalcBerryYield(Internal) */
    u32 max = kBerry[t->berry - 1][1], min = kBerry[t->berry - 1][2], water = times_watered(t), lo, hi, r, extra;
    if (water == 0) return min;
    lo = (max - min) * (water - 1);
    hi = (max - min) * water;
    r = lo + GFL_RandomLCAlt(hi - lo + 1);
    extra = (r & 3) >= 2 ? (r >> 2) + 1 : r >> 2;     /* NUM_WATER_STAGES 4: rounds upwards */
    return extra + min;
}

static void clear(BerryTree *t) { t->berry = 0; t->stage = 0; t->minutes = 0; t->yield = 0; t->flags = 0; }

static u32 grow(BerryTree *t) {                                                   /* BerryTreeGrow */
    if (t->stage & STOP) return 0;
    switch (STAGE(t)) {
    case STAGE_NO_BERRY: return 0;
    case STAGE_FLOWERING: t->yield = (u8)calc_yield(t); /* fallthrough */
    case STAGE_PLANTED: case STAGE_SPROUTED: case STAGE_TALLER: t->stage++; break;
    case STAGE_BERRIES:
        t->yield = 0;
        t->stage = STAGE_SPROUTED;
        t->flags = (u8)((t->flags & 0x0f) + 1);        /* the watered bits cleared, regrowthCount + 1 */
        if ((t->flags & 0x0f) == 10) clear(t);         /* the tenth regrowth: the tree is gone, soft soil again */
        break;
    }
    return 1;
}

static void time_update_trees(BerrySave *s, s32 minutes) {                       /* BerryTreeTimeUpdate */
    u32 i;
    for (i = 0; i < N_TREES; i++) {
        BerryTree *t = &s->trees[i];
        s32 time;
        if (!t->berry || !STAGE(t) || (t->stage & STOP)) continue;
        if (minutes >= (s32)(stage_minutes(t->berry) * 71)) { clear(t); continue; }
        time = minutes;
        while (time != 0) {
            if ((s32)t->minutes > time) { t->minutes = (u16)(t->minutes - time); break; }
            time -= t->minutes;
            t->minutes = (u16)stage_minutes(t->berry);
            if (!grow(t)) break;
            if (STAGE(t) == STAGE_BERRIES) t->minutes = (u16)(t->minutes * 4);
        }
    }
}

static void plant(BerryTree *t, u32 berry, u32 stage, u32 allow) {               /* PlantBerryTree */
    clear(t);
    t->berry = (u8)berry;
    t->minutes = (u16)stage_minutes(berry);
    t->stage = (u8)stage;
    if (stage == STAGE_BERRIES) {
        t->yield = (u8)calc_yield(t);
        t->minutes = (u16)(t->minutes * 4);
    }
    if (!allow) t->stage |= STOP;                      /* a new game's tree waits until the player has seen it */
}

/* ---- the save and the clock --------------------------------------------------------------------------------------- */

/* The DS clock in minutes since 2000-01-01 00:00 (Black 2's cached RTC read), or -1 before the first read. */
static s32 now_minutes(void) {
    struct { u32 year, month, day, week; } date;
    struct { u32 hour, minute, second; } time;
    RTC_GetCachedDateTime(&date, &time);
    if (date.month - 1 > 11 || date.day - 1 > 30 || date.year > 99 || time.hour > 23 || time.minute > 59) return -1;
    return RTC_ConvertDateToDay(&date) * 1440 + (s32)(time.hour * 60 + time.minute);
}

/* The trees, set up as Gen 3's new game sets them (EventScript_ResetAllBerries: every planted tree fully grown, waiting
 * until seen) when the block does not hold them yet: a new game, or a save made before berry planting existed. */
static BerrySave *save(void) {
    BerrySave *s = (BerrySave *)SaveControl_GetBlockPtr(SaveControl_GetInstance(), SAVE_BLOCK);
    u32 i;
    if (s->magic != BERRY_MAGIC) {
        s32 now = now_minutes();
        for (i = 0; i < N_TREES; i++) {
            if (kInit[i]) plant(&s->trees[i], kInit[i], STAGE_BERRIES, 0);
            else clear(&s->trees[i]);
        }
        s->last = now < 0 ? 0 : (u32)now;
        s->version = HOENN_VERSION_ID;
        s->pad[0] = s->pad[1] = s->pad[2] = 0;
        s->magic = BERRY_MAGIC;
    }
    return s;
}

/* Gen 3 UpdatePerMinute: the trees grow by the minutes the clock moved forward since the last update. A clock set back
 * changes nothing and keeps the last update's time, so the trees wait until the clock passes it again (Gen 3's rule:
 * moving the clock back and forth gives no growth beyond the forward moves). */
static BerrySave *update(void) {
    BerrySave *s = save();
    s32 now = now_minutes(), diff;
    if (now < 0) return s;
    diff = now - (s32)s->last;
    if (diff > 0) {
        time_update_trees(s, diff);
        s->last = (u32)now;
    }
    return s;
}

static u32 item_of(u32 berry) { return berry == 0 ? 0 : berry <= 35 ? 148 + berry : 165 + berry; }   /* Cheri 149.. Belue 183, Liechi 201.. Enigma 208 */
static u32 berry_of(u32 item) {
    if (item >= 149 && item <= 183) return item - 148;
    if (item >= 201 && item <= 208) return item - 165;
    return 0;
}

/* The object code of a tree's picture (0: blank, the soft soil Gen 3 leaves invisible). */
static u32 tree_code(const BerryTree *t) {
    u32 st = STAGE(t);
    if (!t->berry || st == STAGE_NO_BERRY || st > STAGE_BERRIES) return PIC_CODE_BASE;
    return PIC_CODE_BASE + kPic[t->berry - 1][st - 1];
}

/* ---- hooks -------------------------------------------------------------------------------------------------------- */

/* ov012 GetWKOBJCODENPCOBJCODE (every actor made from zone data, and ActorNew): Black 2's work codes 162-177 as before;
 * a tree's code VCODE_BASE + id -> its picture now (the trees grow first; the tree is seen, as Gen 3 SetBerryTreesSeen). */
u32 Berry_ResolveCode(void *ew, u32 code) {
    if (code >= 162 && code <= 177) {
        if (!ew) return 10;
        return *EventWork_GetWkPtr(ew, (code + 0x3f7e) & 0xffff);
    }
    if (code >= VCODE_BASE && code < VCODE_BASE + N_TREES) {
        BerryTree *t = &update()->trees[code - VCODE_BASE];
        t->stage &= ~STOP;
        return tree_code(t);
    }
    return code;
}

/* arm9 GetIndexOfObjID: object code -> its a/0/4/7 record (Black 2's three ranges, then the berry pictures). */
u32 Berry_ObjIndex(u32 code) {
    if (code < 377) return code;
    if (code >= 0x1000 && code < 0x126c) return (code - 0xe87) & 0xffff;
    if (code >= 0x2000 && code < 0x200b) return (code - 0x1c1b) & 0xffff;
    if (code >= PIC_CODE_BASE && code < PIC_CODE_BASE + N_PICS) return REC_BASE + code - PIC_CODE_BASE;
    return 10;
}

static void put(void *env, u32 w, u32 v) {
    u16 *p = ScriptWork_GetWkAddr(FieldScriptEnv_GetScriptWork(env), FieldScriptEnv_GetGameData(env), w);
    if (p) *p = (u16)v;
}

static u32 get(void *env, u32 w) {
    u16 *p = ScriptWork_GetWkAddr(FieldScriptEnv_GetScriptWork(env), FieldScriptEnv_GetGameData(env), w);
    return p ? *p : 0;
}

/* The tree: OP_GET takes the actor the player talked to, finds the tree standing on its tile (kTreeX/Z: the trees' world
 * tiles; Black 2's actor save keeps uids in 8 bits, so after Continue a uid would not tell) and keeps the tree in W_TREE
 * and the actor's uid in W_UID; the other ops read W_TREE (the Bag's FieldClose / FieldOpen lies between them). */
static s32 tree_of(void *env, u32 op) {
    u32 i, t = 0;
    if (op == OP_GET) {
        void *actor = ScriptWork_GetParentActor(FieldScriptEnv_GetScriptWork(env));
        put(env, W_UID, actor ? GetActorUID(actor) : 0);
        if (actor) {
            u32 x = (u32)GetGPosX(actor) & 0xffff, z = (u32)GetGPosZ(actor) & 0xffff;
            for (i = 1; i < N_TREES && !t; i++)
                if (kTreeX[i] == x && kTreeZ[i] == z) t = i + 1;
        }
        put(env, W_TREE, t);
    } else t = get(env, W_TREE);
    return t ? (s32)t - 1 : -1;
}

/* Gen 3 ObjectEventInteractionGetBerryTreeData, plus the actor's picture check (W_REFRESH). */
static void report(void *env, BerrySave *s, s32 id) {
    BerryTree *t;
    void *actor;
    if (id < 0) {
        put(env, W_STAGE, 0); put(env, W_ITEM, 0); put(env, W_REFRESH, 0);
        return;
    }
    t = &s->trees[id];
    put(env, W_STAGE, t->berry ? STAGE(t) : 0);
    put(env, W_WATER, times_watered(t));
    put(env, W_YIELD, t->yield);
    put(env, W_ITEM, item_of(t->berry));
    actor = FieldScriptEnv_FindActor(env, get(env, W_UID));
    put(env, W_REFRESH, actor && FldAct_GetObjCode(actor) != tree_code(t));
}

/* script command 612: BerryCmd op, arg */
u32 Berry_Cmd(void *vm, void *env) {
    u32 op = ScriptReadAny(vm, env) & 0xffff;
    u32 arg = ScriptReadAny(vm, env) & 0xffff;
    void *gd = FieldScriptEnv_GetGameData(env);
    BerrySave *s = update();
    s32 id = tree_of(env, op);
    BerryTree *t = id >= 0 ? &s->trees[id] : 0;
    u32 i, b;
    switch (op) {
    case OP_GET:                                        /* the tree as it is now; talking to it counts as seeing it */
        if (t) t->stage &= ~STOP;
        report(env, s, id);
        break;
    case OP_PLANT:                                      /* arg = the item picked in the Bag */
        b = berry_of(arg);
        put(env, W_RESULT, t && b && !t->berry);
        if (t && b && !t->berry) plant(t, b, STAGE_PLANTED, 1);   /* ObjectEventInteractionPlantBerryTree */
        report(env, s, id);
        break;
    case OP_WATER:                                      /* ObjectEventInteractionWaterBerryTree */
        if (t && t->berry && STAGE(t) >= STAGE_PLANTED && STAGE(t) <= STAGE_FLOWERING)
            t->flags |= (u8)(0x10 << (STAGE(t) - 1));
        report(env, s, id);
        break;
    case OP_PICK:                                       /* ObjectEventInteractionRemoveBerryTree (the script added the berries) */
        if (t) clear(t);
        report(env, s, id);
        break;
    case OP_HAS_BERRIES:                                /* PlayerHasBerries: a berry Gen 3 can plant */
        for (i = 1, b = 0; i <= 43 && !b; i++)
            b = BagSave_GetItemCountByID(GameData_GetBag(gd), item_of(i), HEAPID_GAMEEVENT) != 0;
        put(env, W_RESULT, b);
        break;
    case OP_BAG_POCKET:                                 /* the Bag opens on the Berries pocket (Gen 3's berry Bag) */
        BagCursor_SetPocket(GameData_GetBagCursor(gd), POCKET_BERRIES);
        break;
    default:                                            /* OP_UPDATE: the growth only (the tree zones' inits) */
        break;
    }
    return 0;
}
