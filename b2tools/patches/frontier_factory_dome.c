/* Pokémon Emerald NDS: the Battle Factory and the Battle Dome (frontier_factory_dome, 2026-10-12;
 * notes/FRONTIER_FACTORY_DOME.md). HOENN_VERSION=emerald builds only; compiled and placed in ITCM by
 * b2tools/patches/frontier_factory_dome.py, which also writes frontier_fd_data.h (the tables below named k*).
 *
 * Built position-independent (-fropi) into arc 211 file FR_BLOB_FILE; frontier_fd_stub.c (ITCM) loads it per call.
 * One script command (505, Black 2's unused Cmd_01F9: args any, any, any, var):  FrontierCmd sub, a, b, var
 * and one hook: ov012 0x02166082, the Battle Subway battle's call of func_ov033_0217c094 (the setup: the player's
 * members + the round's trainer) -> FR_BuildSetup: in a Factory or Dome battle the player's side is the rental party or
 * the two Pokémon picked for the match, and the opponent's party is Emerald's (its sets at the facility's level with
 * their natures); every other Subway battle (the Battle Tower) goes to Black 2's function as before.
 *
 * Black 2's own pieces this drives (decomp names; addresses in b2_us):
 *   - the rental engine of the PWT's Rental tournament (ov055 wbt_party.c): a set file of the Battle Subway set archive ->
 *     func_ov012_02162490 (BSubwayPokemon: species, item, moves, IVs, EVs 510 / n per flagged stat, personality, ability,
 *     nickname) -> func_ov012_021621d4 (a party at a level, genSubwayBtlInstitutePoke). The sets are Emerald's 882
 *     Battle Frontier sets (arc 211 files 1000-1881, converter/gen_frontier_emerald.py).
 *   - the Battle Subway's battle (ov033 work func_ov033_0217b478, battle event func_ov012_02166070, result in the setup).
 *   - the battle-entry party screen (ov012 func_ov012_02161c88, the Battle Institute's team selection; emerald_mech's
 *     EmPickParty) on any party: the six rentals (rent three), the player's three (swap one away), the last opponent's
 *     three (take one), the three registered for the Dome (pick two).
 *   - the PWT's bracket screen (ov320, proc data 0x0219ee40, as ov022 func_ov022_0216e73c opens it: EventFieldSubprocessTransition_Create) with a WbtSetup this
 *     code fills: one half of Emerald's 16-trainer tree at a time (8 trainers, its 1st and 2nd round results).
 * Emerald's rules (pokeemerald src/battle_factory.c, battle_dome.c, battle_tower.c, frontier_util.c) are ported below.
 * The state lives in frontier_core's record area (notes/FRONTIER.md 2.2: Battle Subway play block +60, u16 keys) and,
 * during a challenge, in spare words of the Battle Subway work (BSubwayScrWork unk32[14..28]). */
typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef signed int s32;

#define FN(type, addr) ((type)((addr) | 1))
/* arm9 */
#define GFL_HeapAllocate           FN(void *(*)(u32, u32, u32, const char *, u32), 0x0203a1fc)
#define GFL_HeapFree               FN(void (*)(void *), 0x0203a24c)
#define GFL_RandomLC               FN(u32 (*)(u32), 0x02005748)
#define GFL_ArcSysCreateFileHandle FN(void *(*)(u32, u32), 0x0204aa30)
#define GFL_ArcToolReadRange       FN(void (*)(void *, u32, u32, u32, void *), 0x0204ac58)
#define GFL_ArcToolFree            FN(void (*)(void *), 0x0204ab0c)
#define GFL_MsgSysLoadData         FN(void *(*)(u32, u32, u32, u32), 0x0204875c)
#define GFL_MsgDataLoadStrbuf      FN(void (*)(void *, u32, void *), 0x02048838)
#define GFL_MsgDataFree            FN(void (*)(void *), 0x020487d4)
#define GFL_StrBufCreate           FN(void *(*)(u32, u32), 0x02048530)
#define GFL_StrBufFree             FN(void (*)(void *), 0x02048564)
#define GFL_StrBufStoreString      FN(void (*)(void *, u16 *, u32), 0x020486b8)
#define GFL_StrBufLoadString       FN(void (*)(void *, const u16 *), 0x02048614)
#define WordSet_LoadStrbuf         FN(void (*)(void *, u32, void *, u32, u32, u32), 0x0202437c)
#define GFL_SndPlayerSetVolume     FN(void (*)(s32, s32), 0x0200632c)
#define GSYS_GetGameData           FN(void *(*)(void *), 0x02016ad8)
#define GSYS_GetField              FN(void *(*)(void *), 0x02016af0)
#define GameEvent_Create           FN(void *(*)(void *, void *, void *, u32), 0x02016cb4)
#define GameEvent_ChainNext        FN(void (*)(void *, void *), 0x02016d68)
#define GameEvent_GetData          FN(void *(*)(void *), 0x02016edc)
#define EventFieldSubprocessTransition_Create FN(void *(*)(void *, void *, u32, const void *, void *), 0x020195c0)   /* fade out, the proc, field back */
#define GameData_GetParty          FN(void *(*)(void *), 0x0201735c)
#define GameData_GetSaveControl    FN(void *(*)(void *), 0x02017934)
#define GetGameDataPlayerInfo      FN(u16 *(*)(void *), 0x0201736c)
#define SaveControl_GetBlockPtr    FN(void *(*)(void *, u32), 0x02007448)
#define BSubway_GetWork            FN(u8 *(*)(void *), 0x0201794c)
#define PokeParty_Create           FN(void *(*)(u32), 0x0201fd00)
#define PokeParty_InitCore         FN(void (*)(void *, u32), 0x0201fd34)
#define PokeParty_AddPkm           FN(u32 (*)(void *, void *), 0x0201fd6c)
#define PokeParty_GetPkm           FN(void *(*)(void *, u32), 0x0201ff08)
#define PokeParty_GetPkmCount      FN(u32 (*)(void *), 0x0201fdf8)
#define PokeParty_Copy             FN(void (*)(void *, void *), 0x020200ac)
#define PokeParty_GetParam         FN(u32 (*)(void *, u32, void *), 0x0201ccf8)
#define PokeParty_SetParam         FN(void (*)(void *, u32, u32), 0x0201cd1c)
#define PokeParty_SetNature        FN(void (*)(void *, u32), 0x0201d5e0)
#define PokeParty_RecalcStats      FN(void (*)(void *), 0x0201d5f4)
#define PML_PersonalGetParamSingle FN(u32 (*)(u32, u32, u32), 0x0201ef1c)
#define GetIndexOfObjID            FN(u32 (*)(u32), 0x0200fe34)
#define BtlSetup_Free              FN(void (*)(void *), 0x02017c84)
#define FreeVSPlayerBlk            FN(void (*)(void), 0x0200bb48)
/* ov012 (the field script overlay) */
#define ScriptReadVar              FN(u16 *(*)(void *, void *), 0x021548e8)
#define ScriptReadAny              FN(u32 (*)(void *, void *), 0x02154910)
#define FieldScriptEnv_GetGameData FN(void *(*)(void *), 0x02155174)
#define FieldScriptEnv_GetGameSystem FN(void *(*)(void *), 0x0215516c)
#define FieldScriptEnv_GetScriptWork FN(void *(*)(void *), 0x02155184)
#define ScriptWork_CallEvent       FN(void (*)(void *, void *), 0x02153880)
#define ScriptWork_GetWordSet      FN(void *(*)(void *), 0x02153ec4)
#define TeamSelect_Create          FN(void *(*)(void *, u32, u32, u32, void *, u8 *, u32 *, u32 *, void *), 0x02161c88)
#define SubwayPkm_FromSet          FN(void (*)(void *, u32, u32, u32, u32, u32, u32, u32, u32), 0x02162490)
#define SubwayParty_Make           FN(void (*)(void *, const void *, u32, u32, u32), 0x021621d4)
#define SetupTrialHouseBattle      FN(void *(*)(void *, void *, u32, void *, void *, u32), 0x02161fc4)
#define SubwayBattle_Event         FN(void *(*)(void *, void *, void *), 0x02166070)
/* ov033 (bsubway_scr.c, loaded with the field) */
#define BSubwayWork_Create         FN(u8 *(*)(void *, u32, u32), 0x0217b478)
#define BSubwayWork_Free           FN(void (*)(void *, void *), 0x0217b664)
#define BSubway_BuildSetup         FN(void *(*)(void *, void *), 0x0217c094)
/* ov036 (the field) */
#define kOv036ControllerTable      ((const u32 *)0x021cf1c8)
#define PWT_BRACKET_OVERLAY        320
#define PWT_BRACKET_PROC           ((const void *)0x0219ee40)

#define ARC_SETS    211         /* the Battle Subway set archive */
#define ARC_SCRIPT_TEXT 3       /* a/0/0/3 */
#define ARC_MMODEL_TBL 47
#define HEAP_EVENT  4           /* HEAPID_GAMEEVENT */
#define HEAP_TAIL   0x8004      /* HEAPID_TAIL(HEAPID_GAMEEVENT), as the Subway's own temporary party */
#define SET_SIZE    16
#define FACT_SIZE   16
#define BSW_TRAINERS 136        /* BSubwayScrWork: trainers[2] (BSubwayTrainer, 288 B: 0x30 header + 4 x 60 B pokemon) */
#define BSW_UNK2C8  712
#define BSW_SETUP   0x7d0
#define BSW_SCRATCH 0x32        /* unk32[]: Black 2's 14 trainer ids, then spare words; ours from [14] */
#define BSW_MODE    9
#define BSW_UNKC    12
#define TRAINER_PKM 0x30
#define PKM_SIZE    60          /* BSubwayPokemon */
#define SETUP_PARTY1 40         /* BtlSetup party[1] */
#define SETUP_RESULT 0xa8       /* BtlSetup unkA8: 1 = the player won (Black 2's command 332) */
#define P_SPECIES 0x05
#define P_ITEM    0x06
#define P_EV_HP   0x0d
#define P_ABILITY 0x0a
#define P_LEVEL   0x9e
#define P_MAXHP   0xa1
#define P_IS_EGG  0x4c

/* frontier_core's record keys (notes/FRONTIER.md 2.2) */
#define FR_PLAY_BLOCK 0x38
#define FR_AREA_OFF   60
#define K_STATUS 0
#define K_FACILITY 1
#define K_LVL 3
#define K_PARTY 4
#define K_BATTLE_NUM 5
#define K_SYMBOLS 6
#define K_BATTLE_MODE 2         /* FRONTIER_MODE_*: 0 singles, 1 doubles */
#define K_STREAK(f, m, l) (16 + 8 * (f) + 4 * (m) + 2 * (l))
#define K_F_MONS 79             /* our claims (notes/FRONTIER.md 6) */
#define K_F_RENTS 85            /* 85 singles, 86 doubles: low byte Lv. 50, high byte Open Level (Emerald reads its
                                   factoryRentsCount as a u8: the same count modulo 256) */
#define K_F_SEED 87
#define K_D_SEED 88
#define K_D_INFO 90
#define FAC_DOME 1
#define FAC_FACTORY 4

/* our words of the Subway work during a challenge */
#define S_MAGIC 14
#define S_OPP 15                /* 15-17: the opponent's set ids (Factory 3; Dome: the two it sends) */
#define S_TRAINER 18            /* Frontier trainer index; T_BRAIN = the facility's Brain */
#define S_IV 19
#define S_COUNT 20
#define S_PICK 21               /* 21-22: Dome: the party slots the player picked for the match */
#define S_FLAGS 24              /* bit 0: rented or swapped since the last win (Emerald's sPerformedRentalSwap) */
#define S_LEVEL 25
#define S_GOLD 26               /* Brain battle: 1 silver party, 2 gold */
#define MAGIC_FACTORY 0xF0D0
#define MAGIC_DOME    0xD03E
#define T_BRAIN 0xFFFE
#define T_PLAYER 0xFFFF
#define NONE 0xFFFF
#define S_BLOB 27              /* 27/28: the loaded engine's address during B_BATTLE (frontier_fd_stub.c's hook reads it) */
#define KEEP 0x100              /* FR_Cmd's answer: an event of ours runs on (the stub frees the engine when it ends) */
#define GFL_HeapGetFreeSize FN(u32 (*)(u32), 0x0203a2a8)

#include "frontier_fd_data.h"

/* the compiler's division calls -> Black 2's own ARM routines (arm9 __aeabi_uidivmod = _u32_div_f, _s32_div_f): quotient
 * in r0, remainder in r1 */
typedef unsigned long long u64;
u32 __aeabi_uidiv(u32 a, u32 b) { return (u32)((u64 (*)(u32, u32))0x0208d868)(a, b); }
u64 __aeabi_uidivmod(u32 a, u32 b) { return ((u64 (*)(u32, u32))0x0208d868)(a, b); }
s32 __aeabi_idiv(s32 a, s32 b) { return (s32)((u64 (*)(s32, s32))0x0208d65c)(a, b); }
u64 __aeabi_idivmod(s32 a, s32 b) { return ((u64 (*)(s32, s32))0x0208d65c)(a, b); }

/* ------------------------------------------------------------------------------------------------ small helpers */
static void *gd_of(void *env) { return FieldScriptEnv_GetGameData(env); }
static u16 *rec(void *gd) { return (u16 *)((u8 *)SaveControl_GetBlockPtr(GameData_GetSaveControl(gd), FR_PLAY_BLOCK) + FR_AREA_OFF); }
static u16 *scratch(u8 *bsw) { return (u16 *)(bsw + BSW_SCRATCH); }
static u32 rnd16(void) { return GFL_RandomLC(0xffffffff) / 0xffff; }      /* Black 2's randFFFFFFFFdivFFFF */
static u32 rnd(u32 n) { return n ? rnd16() % n : 0; }
static u32 lcg(u32 *s) { *s = *s * 1103515245u + 24691u; return *s >> 16; }  /* Emerald's Random() (ISO C LCG) */
static void *alloc(u32 size) { return GFL_HeapAllocate(HEAP_TAIL, size, 1, "fr", 0); }
static void zero(void *p, u32 n) { u8 *b = p; while (n--) *b++ = 0; }

typedef struct { void *h; } Rd;
static void rd_open(Rd *r) { r->h = GFL_ArcSysCreateFileHandle(ARC_SETS, HEAP_TAIL); }
static void rd_close(Rd *r) { GFL_ArcToolFree(r->h); }
/* per-set facts (gen_frontier_emerald / frontier_factory_dome.py FACTS): u16 species, u16 item, u8 type1, u8 type2 (Gen 3),
 * u8 flags (1 Levitate, 2 Wonder Guard), u8 base stat total / 10, u8 move types[4] (Gen 3, 255 = no power),
 * u16 styles (4 bits a move: FACTORY_STYLE_*), u8 nature, u8 EV flags */
typedef struct { u16 species, item; u8 t1, t2, flags, sum10; u8 mt[4]; u16 styles; u8 nature, evs; } Fact;
static void fact(Rd *r, u32 id, Fact *f) { GFL_ArcToolReadRange(r->h, FR_FACTS_FILE, id * FACT_SIZE, FACT_SIZE, f); }
/* the trainer table: 300 x {u16 class, u16 sprite, u16 list offset (u16 units), u16 count}, then the set lists */
typedef struct { u16 cls, sprite, off, count; } TrRec;
static void trainer(Rd *r, u32 t, TrRec *o) { GFL_ArcToolReadRange(r->h, FR_TRAINERS_FILE, t * 8, 8, o); }
static u16 trainer_set(Rd *r, const TrRec *t, u32 k) { u16 v; GFL_ArcToolReadRange(r->h, FR_TRAINERS_FILE, (t->off + k) * 2, 2, &v); return v; }

/* ------------------------------------------------------------------------------------------------ Emerald's tables */
static u32 fixed_iv(u32 c, u32 last) { if (c >= 8) c = 7; return kFactoryIV[c][last ? 1 : 0]; }   /* BUGFIX clamp */
static u32 streak_key(const u16 *k, u32 fac) { return K_STREAK(fac, k[K_BATTLE_MODE] & 1, k[K_LVL] & 1); }
static u32 rents(const u16 *k) { u16 v = k[K_F_RENTS + (k[K_BATTLE_MODE] & 1)]; return (k[K_LVL] & 1) ? v >> 8 : v & 0xff; }
static void rents_set(u16 *k, u32 n) {
    u16 *p = &k[K_F_RENTS + (k[K_BATTLE_MODE] & 1)];
    n &= 0xff;
    *p = (k[K_LVL] & 1) ? (u16)((*p & 0xff) | n << 8) : (u16)((*p & 0xff00) | n);
}
static u32 trainer_id(u32 c, u32 battle, u32 (*rng)(void *), void *st) {
    const u16 *r;                                    /* GetRandomScaledFrontierTrainerId */
    if (c > 7) c = 7;
    r = battle == 6 ? kTrainerRangesHard[c] : kTrainerRanges[c];
    return r[0] + rng(st) % (r[1] - r[0] + 1);
}
static u32 rng_lcg(void *st) { return lcg((u32 *)st); }
static u32 factory_mon(u32 lvl, u32 c, u32 better) {           /* GetFactoryMonId */
    u32 i = (lvl ? 8 : 0) + (c < 7 ? c + (better ? 1 : 0) : 7);
    return kFactoryRanges[i][0] + rnd(kFactoryRanges[i][1] - kFactoryRanges[i][0] + 1);
}
static u32 brain_status(void *gd, u32 fac) {                   /* GetFrontierBrainStatus */
    u16 *k = rec(gd);
    const u8 *a = fac == FAC_DOME ? kBrainDome : kBrainFactory;
    s32 ws = k[streak_key(k, fac)] + a[3];
    if (k[K_BATTLE_MODE] & 1) return 0;                         /* the Brains only take singles challenges */
    u32 sym = (k[K_SYMBOLS] >> (2 * fac)) & 3, n = (sym & 1) + ((sym >> 1) & 1);
    if (n < 2) return ws == a[n] ? n + 1 : 0;
    if (ws == a[0]) return 3;
    if (ws == a[1]) return 4;
    if (ws > a[1] && (ws - a[1]) % a[2] == 0) return 4;
    return 0;
}
static u32 personality(u32 seed, u32 id) { u32 p = (seed * 0x9E3779B1u) ^ (id * 0x85EBCA77u) ^ 0x5F3759DFu; return p ? p : 1; }

/* a party from (set id | IV << 10) values at a level, with each set's nature (Emerald's CreateMonWithEVSpreadNatureOTID:
 * the set's nature; Black 2's loader as HoennB2's Battle Tower leaves it gives a random one) */
static void make_party(void *party, const u16 *ids, u32 n, u32 level, u32 iv_all, u32 seed, const u8 *natures, const u16 *evs) {
    u8 pkms[6 * PKM_SIZE];         /* up to six (the rental screen) */
    u32 i, j;
    zero(pkms, sizeof(pkms));
    for (i = 0; i < n; i++) {
        u32 id = ids[i] & 0x3ff, iv = iv_all < 32 ? iv_all : (ids[i] >> 10) & 31;
        SubwayPkm_FromSet(pkms + i * PKM_SIZE, ARC_SETS, FR_SET_BASE + id, 0, personality(seed, id), iv, i, 0, HEAP_TAIL);
    }
    SubwayParty_Make(party, pkms, level, n, HEAP_TAIL);
    for (i = 0; i < n; i++) {
        void *p = PokeParty_GetPkm(party, i);
        if (evs) for (j = 0; j < 6; j++) PokeParty_SetParam(p, P_EV_HP + j, evs[i * 6 + j]);
        PokeParty_SetNature(p, natures[i]);
        PokeParty_RecalcStats(p);
        PokeParty_SetParam(p, 0xa0, PokeParty_GetParam(p, P_MAXHP, 0));   /* full HP */
    }
}

/* ================================================================================================ the Battle Factory */
static u32 factory_challenge(void *gd) { u16 *k = rec(gd); return k[streak_key(k, FAC_FACTORY)] / 7; }
static u32 rental_rank(u32 rents) { return rents < 15 ? 0 : rents < 22 ? 1 : rents < 29 ? 2 : rents < 36 ? 3 : rents < 43 ? 4 : 5; }

/* GenerateInitialRentalMons: six candidates -> keys 79-84 (id | IV << 10) */
static void factory_rentals(void *gd) {
    u16 *k = rec(gd);
    u32 lvl = k[K_LVL] & 1, c = factory_challenge(gd), rank = rental_rank(rents(k));
    u16 sp[6], held[6], ids[6], cur = 0;
    u32 i = 0, j, id;
    Fact f;
    Rd r; rd_open(&r);
    while (i != 6) {
        id = factory_mon(lvl, c, i < rank);
        fact(&r, id, &f);
        if (f.species == kSpeciesUnown) continue;
        for (j = 0; j < i; j++) {
            if (ids[j] == id) break;
            if (sp[j] == f.species) { if (cur == 0) cur = f.species; else break; }
        }
        if (j != i) continue;
        for (j = 0; j < i; j++)
            if (held[j] && held[j] == f.item) { if (f.species == cur) cur = 0; break; }
        if (j != i) continue;
        ids[i] = id; sp[i] = f.species; held[i] = f.item;
        k[K_F_MONS + i] = id | (fixed_iv(c + (i < rank ? 1 : 0), 0) << 10);
        i++;
    }
    rd_close(&r);
    if (k[K_BATTLE_NUM] == 0) k[K_F_SEED] = rnd16() | 1;
}

/* GenerateOpponentMons (+ FillFactoryBrainParty for Noland): the trainer and three sets -> the Subway work */
static void factory_opponent(void *gd, u8 *bsw) {
    u16 *k = rec(gd), *s = scratch(bsw);
    u32 lvl = k[K_LVL] & 1, c = factory_challenge(gd), battle = k[K_BATTLE_NUM], brain = brain_status(gd, FAC_FACTORY);
    u16 sp[3], held[3];
    u32 i = 0, j, id, t = 0, st, prev[7], n;
    Fact f, g;
    Rd r; rd_open(&r);
    /* the trainer: seven different ones in a challenge, from the challenge's seed (Emerald keeps trainerIds[]) */
    st = k[K_F_SEED] * 0x10001u + c;
    for (n = 0; n <= battle; n++) {
        do {
            t = trainer_id(c, n, rng_lcg, &st);
            for (j = 0; j < n; j++) if (prev[j] == t) break;
        } while (j != n);
        prev[n] = t;
    }
    s[S_TRAINER] = brain ? T_BRAIN : t;
    s[S_IV] = brain ? fixed_iv(c + 2, 0) : fixed_iv(c, battle == 6);
    while (i != 3) {
        id = factory_mon(lvl, c, 0);
        fact(&r, id, &f);
        if (f.species == kSpeciesUnown) continue;
        if (lvl == 0 && id > kHighTier) continue;
        for (j = 0; j < 6; j++) {
            if (k[K_F_MONS + j] == NONE) continue;
            if (brain) { if ((k[K_F_MONS + j] & 0x3ff) == id) break; continue; }
            fact(&r, k[K_F_MONS + j] & 0x3ff, &g);
            if (g.species == f.species) break;
        }
        if (j != 6) continue;
        for (j = 0; j < i; j++) if (sp[j] == f.species) break;
        if (j != i) continue;
        for (j = 0; j < i; j++) if (held[j] && held[j] == f.item) break;
        if (j != i) continue;
        sp[i] = f.species; held[i] = f.item; s[S_OPP + i] = id; i++;
    }
    s[S_COUNT] = 3;
    s[S_LEVEL] = lvl ? 100 : 50;
    rd_close(&r);
}

/* GetOpponentMostCommonMonType: 0-17 (Gen 3 types), 18 = none */
static u32 factory_type(u8 *bsw) {
    u16 *s = scratch(bsw);
    u8 cnt[18], most[2];
    u32 i;
    Fact f; Rd r; rd_open(&r);
    zero(cnt, sizeof(cnt));
    for (i = 0; i < 3; i++) {
        fact(&r, s[S_OPP + i], &f);
        cnt[f.t1]++;
        if (f.t1 != f.t2) cnt[f.t2]++;
    }
    rd_close(&r);
    most[0] = most[1] = 0;
    for (i = 1; i < 18; i++) {
        if (cnt[most[0]] < cnt[i]) most[0] = i;
        else if (cnt[most[0]] == cnt[i]) most[1] = i;
    }
    if (cnt[most[0]] == 0) return 18;
    if (cnt[most[0]] > cnt[most[1]] || most[0] == most[1]) return most[0];
    return 18;
}

/* GetOpponentBattleStyle: 0 none, 1-7, 8 = flexible */
static u32 factory_style(u8 *bsw) {
    u16 *s = scratch(bsw);
    u8 pts[8];
    u32 i, j, res = 0, count = 0;
    Fact f; Rd r; rd_open(&r);
    zero(pts, sizeof(pts));
    for (i = 0; i < 3; i++) {
        fact(&r, s[S_OPP + i], &f);
        for (j = 0; j < 4; j++) pts[(f.styles >> (4 * j)) & 15]++;
    }
    rd_close(&r);
    for (i = 1; i < 8; i++) if (pts[i] >= kStyleRequired[i - 1]) { res = i; count++; }
    return count > 2 ? 8 : res;
}

/* ================================================================================================ the Battle Dome */
typedef struct {
    u16 trainer[16];            /* tournament id -> trainer index, T_PLAYER, T_BRAIN */
    u16 mons[16][3];            /* set ids (the player's: unused) */
    u8 elim[16];                /* 0 = still in; round + 1 when eliminated */
    s32 pts1, pts2;             /* DecideRoundWinners' running sums (Emerald does not clear them per match) */
} Dome;

static u32 dome_level(void *gd, u32 lvl) {                      /* SetFacilityPtrsGetLevel for the Dome */
    u16 *k = rec(gd);
    u32 i, lv, max = 0;
    void *party = GameData_GetParty(gd);
    if (!lvl) return 50;
    for (i = 0; i < 3; i++) {
        u32 slot = ((k[K_PARTY] >> (4 * i)) & 15) - 1;
        if (slot < 6 && slot < PokeParty_GetPkmCount(party)) { lv = PokeParty_GetParam(PokeParty_GetPkm(party, slot), P_LEVEL, 0); if (lv > max) max = lv; }
    }
    return max < 60 ? 60 : max;
}
static u32 dome_ivs(u32 t) { u32 i; for (i = 0; i < 8; i++) if (t <= kDomeIvLimit[i][0]) return kDomeIvLimit[i][1]; return 31; }
/* CalcDomeMonStats (pokeemerald battle_dome.c), with its quirks: the EVs come out as 0 (its second loop tests a
 * shifted-out bit mask), the five other stats are cut to a byte, Shedinja's HP is 1 */
static u32 stat_calc(u32 species, u32 base, u32 iv, u32 lv, u32 nature, u32 stat) {
    u32 v;
    if (stat == 0) return species == 292 ? 1 : ((2 * base + iv) * lv) / 100 + lv + 10;
    v = ((2 * base + iv) * lv) / 100 + 5;
    if (nature < 25 && nature / 5 != nature % 5) {          /* ModifyStatByNature: +10% / -10% (Atk Def Spe SpA SpD) */
        if (nature / 5 == stat - 1) v = v * 110 / 100;
        else if (nature % 5 == stat - 1) v = v * 90 / 100;
    }
    return v & 0xff;
}
static u32 gen3_type_of_b2(u32 t) { return t < 9 ? t : t <= 16 ? t + 1 : 0; }   /* Black 2 (+ Fairy 17) -> Gen 3 */
static s32 eff_points(u32 mtype, u32 dt1, u32 dt2, u32 dflags, u32 mode) {     /* GetTypeEffectivenessPoints */
    s32 p = 20;
    u32 i;
    if (mtype == 255) return 0;
    if ((dflags & 1) && mtype == 4) { if (mode == 1) p = 8; }        /* Levitate vs Ground (Emerald's missing return) */
    else for (i = 0; i < sizeof(kTypeChart) / 3; i++) {
        if (kTypeChart[i][0] != mtype) continue;
        if (kTypeChart[i][1] == dt1 && (!(dflags & 2) || kTypeChart[i][2] == 40)) p = p * kTypeChart[i][2] / 10;
        if (kTypeChart[i][1] == dt2 && dt1 != dt2 && (!(dflags & 2) || kTypeChart[i][2] == 40)) p = p * kTypeChart[i][2] / 10;
    }
    switch (mode) {
    case 0: return p == 20 ? 2 : p == 40 ? 4 : p == 80 ? 8 : 0;                         /* GOOD */
    case 1: return p == 0 ? 8 : p == 5 ? 4 : p == 10 ? 2 : p == 40 ? -2 : p == 80 ? -4 : 0;   /* BAD */
    default: return p == 0 ? -16 : p == 5 ? -8 : p == 20 ? 4 : p == 40 ? 12 : p == 80 ? 20 : 0;   /* AI vs AI */
    }
}
static const u8 kTreeIds[16] = {0, 8, 12, 4, 7, 15, 11, 3, 2, 10, 14, 6, 5, 13, 9, 1};         /* sTourneyTreeTrainerIds */
static const u8 kOppIds[16] = {0, 8, 4, 12, 7, 15, 3, 11, 2, 10, 6, 14, 5, 13, 1, 9};          /* sTourneyTreeTrainerOpponentIds */
static const u8 kIdToOpp[16][4] = {{8,0,4,8},{9,12,8,0},{10,8,12,0},{11,4,0,8},{12,0,4,8},{13,12,8,0},{14,8,12,0},{15,4,0,8},
                                   {0,0,4,8},{1,12,8,0},{2,8,12,0},{3,4,0,8},{4,0,4,8},{5,12,8,0},{6,8,12,0},{7,4,0,8}};
static u32 opp_of(Dome *d, u32 round, u32 i) {                  /* TournamentIdOfOpponent (by tournament id) */
    u32 j, max;
    if (round == 0) return d->elim[kIdToOpp[i][0]] ? 0xff : kIdToOpp[i][0];
    max = kIdToOpp[i][round] + (round == 3 ? 8 : 4);
    for (j = kIdToOpp[i][round]; j < max; j++) if (kOppIds[j] != i && !d->elim[kOppIds[j]]) return kOppIds[j];
    return 0xff;
}
static u32 player_id(Dome *d) { u32 i; for (i = 0; i < 16; i++) if (d->trainer[i] == T_PLAYER) return i; return 0; }
static void dome_round(Dome *d, Rd *r, u32 round, u32 *st) {     /* DecideRoundWinners */
    u32 i, a, b, m1, m2, mv, lose;
    Fact f1, f2;
    for (i = 0; i < 16; i++) {
        if (d->elim[i] || d->trainer[i] == T_PLAYER) continue;
        a = i; b = opp_of(d, round, a);
        if (b == 0xff) continue;
        if (d->trainer[a] == T_BRAIN) { d->elim[b] = round + 1; continue; }
        if (d->trainer[b] == T_BRAIN) { d->elim[a] = round + 1; continue; }
        for (m1 = 0; m1 < 3; m1++) {
            fact(r, d->mons[a][m1], &f1);
            for (mv = 0; mv < 4; mv++)
                for (m2 = 0; m2 < 3; m2++) { fact(r, d->mons[b][m2], &f2); d->pts1 += eff_points(f1.mt[mv], f2.t1, f2.t2, f2.flags, 2); }
            d->pts1 += f1.sum10;
        }
        d->pts1 += lcg(st) & 0x1f; d->pts1 += a;
        for (m1 = 0; m1 < 3; m1++) {
            fact(r, d->mons[b][m1], &f1);
            for (mv = 0; mv < 4; mv++)
                for (m2 = 0; m2 < 3; m2++) { fact(r, d->mons[a][m2], &f2); d->pts2 += eff_points(f1.mt[mv], f2.t1, f2.t2, f2.flags, 2); }
            d->pts2 += f1.sum10;
        }
        d->pts2 += lcg(st) & 0x1f; d->pts2 += b;
        lose = d->pts1 > d->pts2 ? b : d->pts1 < d->pts2 ? a : a > b ? b : a;
        d->elim[lose] = round + 1;
    }
}

/* InitDomeTrainers, rebuilt from the seed (keys 88/89) and the player's place (key 90 bits 0-3; Tucker: bit 4); with
 * build = 1 the player's place is decided here (the ranking with the player's own stats) and stored */
static void dome_build(void *gd, Dome *d, Rd *r, u32 build) {
    u16 *k = rec(gd);
    u32 st = k[K_D_SEED] | (u32)k[K_D_SEED + 1] << 16, i, j, m, t, id, lvl = k[K_D_INFO] >> 15 & 1, level = dome_level(gd, lvl);
    u32 streak = k[K_D_INFO] >> 11 & 7;            /* min(tournaments won, 7) at the draw (D_INIT) */
    u16 sp[3] = {0, 0, 0}, score[16], tmp;
    TrRec tr;
    Fact f;
    zero(d, sizeof(*d));
    d->trainer[0] = T_PLAYER;
    for (i = 1; i < 16; i++) {
        do {
            t = trainer_id(i > 5 ? streak : streak + 1, 0, rng_lcg, &st);
            for (j = 1; j < i; j++) if (d->trainer[j] == t) break;
        } while (j != i);
        d->trainer[i] = t;
        trainer(r, t, &tr);
        for (j = 0; j < 3; j++) {
            do {
                do { id = trainer_set(r, &tr, lcg(&st) % tr.count); } while (lvl == 0 && id > kHighTier);
                fact(r, id, &f);
                for (m = 0; m < j; m++) {
                    Fact g; fact(r, d->mons[i][m], &g);
                    if (d->mons[i][m] == id || sp[0] == f.species || sp[1] == f.species || g.item == f.item) break;
                }
            } while (m != j);
            d->mons[i][j] = id; sp[j] = f.species;
        }
    }
    /* ranking scores: the sum of the six stats of the three Pokémon + types * level / 20 */
    for (i = 1; i < 16; i++) {
        u32 types = 0, n = 0, iv = dome_ivs(d->trainer[i]);
        score[i] = 0;
        for (j = 0; j < 3; j++) {
            u32 b;
            fact(r, d->mons[i][j], &f);
            for (b = 0; b < 6; b++) score[i] += stat_calc(f.species, PML_PersonalGetParamSingle(f.species, 0, b), iv, level, f.nature, b);
            types |= 1u << f.t1 | 1u << f.t2;
        }
        for (; types; types >>= 1) n += types & 1;
        score[i] += n * level / 20;
    }
    if (build) {
        void *party = GameData_GetParty(gd);
        u32 types = 0, n = 0;
        score[0] = 0;
        for (i = 0; i < 3; i++) {
            u32 slot = ((k[K_PARTY] >> (4 * i)) & 15) - 1;
            void *p;
            if (slot >= PokeParty_GetPkmCount(party)) continue;
            p = PokeParty_GetPkm(party, slot);
            for (j = 0; j < 6; j++) score[0] += PokeParty_GetParam(p, P_MAXHP + j, 0);
            types |= 1u << gen3_type_of_b2(PML_PersonalGetParamSingle(PokeParty_GetParam(p, P_SPECIES, 0), 0, 6));
            types |= 1u << gen3_type_of_b2(PML_PersonalGetParamSingle(PokeParty_GetParam(p, P_SPECIES, 0), 0, 7));
        }
        for (; types; types >>= 1) n += types & 1;
        score[0] += n * level / 20;
    } else score[0] = 0;
    /* seed by score (Emerald's exchange sort: ties go to the player, then to the lower trainer id) */
    for (i = 0; i < 15; i++)
        for (j = i + 1; j < 16; j++) {
            u32 sw;
            if (!build && (d->trainer[i] == T_PLAYER || d->trainer[j] == T_PLAYER)) sw = 0;
            else sw = score[i] < score[j] || (score[i] == score[j] && (d->trainer[j] == T_PLAYER ||
                      (d->trainer[i] != T_PLAYER && d->trainer[i] > d->trainer[j])));
            if (sw) {
                tmp = d->trainer[i]; d->trainer[i] = d->trainer[j]; d->trainer[j] = tmp;
                tmp = score[i]; score[i] = score[j]; score[j] = tmp;
                for (m = 0; m < 3; m++) { tmp = d->mons[i][m]; d->mons[i][m] = d->mons[j][m]; d->mons[j][m] = tmp; }
            }
        }
    if (!build) {                   /* the NPCs are in order: move the player (now at 0) to its stored place */
        u32 p = k[K_D_INFO] & 15;
        for (i = 0; i < p; i++) {
            d->trainer[i] = d->trainer[i + 1];
            for (m = 0; m < 3; m++) d->mons[i][m] = d->mons[i + 1][m];
        }
        d->trainer[p] = T_PLAYER;
    } else k[K_D_INFO] = (k[K_D_INFO] & ~15) | player_id(d);
    if (build) {                    /* bit 4 Tucker is in it, bit 8 with his Gold party */
        u32 bs = brain_status(gd, FAC_DOME);
        k[K_D_INFO] = (k[K_D_INFO] & ~(16 | 256)) | (bs ? 16 : 0) | (bs && !(bs & 1) ? 256 : 0);
    }
    if (k[K_D_INFO] & 16) {         /* Tucker: in the other half, as the top seed of that half */
        u32 pl = player_id(d), left = 0, b, gold = k[K_D_INFO] >> 8 & 1;
        for (i = 0; i < 8; i++) if (kTreeIds[i] == pl) left = 1;
        b = left ? 1 : 0;
        d->trainer[b] = T_BRAIN;
        for (m = 0; m < 3; m++) d->mons[b][m] = kTuckerSet + (gold ? 3 : 0) + m;
    }
    /* the rounds played so far (key 5) and the player's own result (key 90 bits 5-7: lost in round n + 1) */
    {
        u32 rounds = k[K_BATTLE_NUM], lost = (k[K_D_INFO] >> 5) & 7, pl = player_id(d), sst = st ^ 0x5eed;
        for (i = 0; i < 4; i++) {
            if (lost && i == lost - 1) {        /* ResolveDomeRoundWinners (lost): the player out, the rest decided */
                d->elim[pl] = i + 1;
                for (j = i; j < 4; j++) dome_round(d, r, j, &sst);
                break;
            }
            if (i >= rounds) break;
            d->elim[opp_of(d, i, pl)] = i + 1;   /* (won) the player's opponent out, the other matches decided */
            if (i < 3) dome_round(d, r, i, &sst);
        }
    }
}

/* GetDomeTrainerSelectedMons: the two of the opponent's three it sends out, by Emerald's type points against the
 * player's three registered Pokémon */
static u32 dome_pick_two(void *gd, Rd *r, const u16 *mons) {
    u16 *k = rec(gd);
    void *party = GameData_GetParty(gd);
    s32 pts[3], pos[3];
    u32 i, j, pm, mv, mode = rnd16() & 1 ? 0 : 1, bits = 0, tries;
    for (tries = 0; tries < 2 && !bits; tries++, mode ^= 1) {
        for (i = 0; i < 3; i++) {
            Fact f; fact(r, mons[i], &f);
            pts[i] = 0; pos[i] = i;
            for (mv = 0; mv < 4; mv++)
                for (pm = 0; pm < 3; pm++) {
                    u32 slot = ((k[K_PARTY] >> (4 * pm)) & 15) - 1, sp, ab, flags = 0;
                    void *p;
                    if (slot >= PokeParty_GetPkmCount(party)) continue;
                    p = PokeParty_GetPkm(party, slot);
                    sp = PokeParty_GetParam(p, P_SPECIES, 0);
                    ab = PML_PersonalGetParamSingle(sp, 0, 26);
                    if (ab == 26) flags |= 1;                      /* Levitate */
                    if (ab == 25) flags |= 2;                      /* Wonder Guard */
                    pts[i] += eff_points(f.mt[mv], gen3_type_of_b2(PML_PersonalGetParamSingle(sp, 0, 6)),
                                         gen3_type_of_b2(PML_PersonalGetParamSingle(sp, 0, 7)), flags, mode);
                }
        }
        if (pts[0] == pts[1] && pts[0] == pts[2]) {
            if (tries == 1) while (((bits & 1) + (bits >> 1 & 1) + (bits >> 2 & 1)) < 2) { u32 x = rnd16() & 3; if (x != 3) bits |= 1u << x; }
            continue;
        }
        for (i = 0; i < 2; i++)
            for (j = i + 1; j < 3; j++) {
                s32 t;
                if (pts[i] < pts[j] || (pts[i] == pts[j] && (rnd16() & 1))) { t = pts[i]; pts[i] = pts[j]; pts[j] = t; t = pos[i]; pos[i] = pos[j]; pos[j] = t; }
            }
        bits = 1u << pos[0] | 1u << pos[1];
    }
    if (!bits) bits = 3;
    return bits;
}

/* the round's opponent -> the Subway work (S_TRAINER, S_OPP: the two it sends, S_IV, S_LEVEL) */
static u32 dome_opponent(void *gd, u8 *bsw) {
    u16 *k = rec(gd), *s = scratch(bsw);
    Dome *d = alloc(sizeof(Dome));
    u32 o, bits, i, n = 0;
    Rd r; rd_open(&r);
    dome_build(gd, d, &r, 0);
    o = opp_of(d, k[K_BATTLE_NUM], player_id(d));
    if (o == 0xff) o = 0;
    s[S_TRAINER] = d->trainer[o];
    bits = dome_pick_two(gd, &r, d->mons[o]);
    for (i = 0; i < 3; i++) if (bits >> i & 1) s[S_OPP + n++] = d->mons[o][i];
    s[S_COUNT] = 2;
    /* Emerald's CreateDomeOpponentMon passes the tournament id (0-15) to GetDomeTrainerMonIvs, so every Dome trainer's
     * Pokémon have IVs of 3 (its BUGFIX would use dome_ivs(trainer)); kept as Emerald plays. 32: Tucker's own IVs */
    s[S_IV] = d->trainer[o] == T_BRAIN ? 32 : kDomeOpponentIv;
    s[S_LEVEL] = dome_level(gd, k[K_LVL] & 1);
    s[S_GOLD] = d->trainer[o] == T_BRAIN ? (d->mons[o][0] >= kTuckerSet + 3 ? 2 : 1) : 0;
    rd_close(&r);
    o = s[S_TRAINER];
    GFL_HeapFree(d);
    return o;
}

/* ================================================================================================ names, words */
static void load_line(u32 line, void *strbuf) {
    void *msg = GFL_MsgSysLoadData(0, ARC_SCRIPT_TEXT, FR_TEXT_FILE, HEAP_TAIL);
    GFL_MsgDataLoadStrbuf(msg, line, strbuf);
    GFL_MsgDataFree(msg);
}
static void word_name(void *env, u32 slot, u32 t) {
    void *sb = GFL_StrBufCreate(32, HEAP_TAIL);
    void *gd = gd_of(env);
    if (t == T_PLAYER) GFL_StrBufLoadString(sb, GetGameDataPlayerInfo(gd));
    else load_line(t == T_BRAIN ? (rec(gd)[K_FACILITY] == FAC_DOME ? kNameTucker : kNameNoland) : FR_NAME_BASE + t, sb);
    WordSet_LoadStrbuf(ScriptWork_GetWordSet(FieldScriptEnv_GetScriptWork(env)), slot, sb, 0, 1, 2);
    GFL_StrBufFree(sb);
}

/* ================================================================================================ the battle */
static u8 *work_of(void *env) {
    void *gd = gd_of(env);
    u8 *bsw = BSubway_GetWork(gd);
    if (!bsw) {
        bsw = BSubwayWork_Create(FieldScriptEnv_GetGameSystem(env), 0, 0);   /* Single Train: one trainer, singles */
        { u16 *s = scratch(bsw); u32 i; for (i = S_MAGIC; i < 29; i++) s[i] = 0; }
    }
    return bsw;
}
/* the round's trainer in the Subway work's trainer slot 0: class, name, the sets (BSubwayTrainer, func_ov012_021628c0's
 * layout: +0 id + 1, +4 class, +8 name (8 u16), +24/+26 Black 2's in-battle lines (none), +48 the Pokémon) */
static u32 battle_prep(void *env, u32 facility) {
    void *gd = gd_of(env);
    u8 *bsw = work_of(env), *tr = bsw + BSW_TRAINERS;
    u16 *s = scratch(bsw);
    u32 t = s[S_TRAINER], i, cls, sprite;
    void *sb = GFL_StrBufCreate(32, HEAP_TAIL);
    TrRec rr;
    Rd r; rd_open(&r);
    s[S_MAGIC] = facility == FAC_DOME ? MAGIC_DOME : MAGIC_FACTORY;
    if (t == T_BRAIN) { cls = facility == FAC_DOME ? kTuckerClass : kNolandClass; sprite = facility == FAC_DOME ? kTuckerSprite : kNolandSprite; }
    else { trainer(&r, t, &rr); cls = rr.cls; sprite = rr.sprite; }
    rd_close(&r);
    zero(tr, 0x30);
    *(u32 *)tr = 1;
    *(u16 *)(tr + 4) = cls;
    load_line(t == T_BRAIN ? (facility == FAC_DOME ? kNameTucker : kNameNoland) : FR_NAME_BASE + t, sb);
    GFL_StrBufStoreString(sb, (u16 *)(tr + 8), 8);
    GFL_StrBufFree(sb);
    *(u16 *)(tr + 24) = NONE;
    for (i = 0; i < s[S_COUNT]; i++)
        SubwayPkm_FromSet(tr + TRAINER_PKM + i * PKM_SIZE, ARC_SETS, FR_SET_BASE + s[S_OPP + i], 0, personality(0x77, s[S_OPP + i]),
                          s[S_IV] < 32 ? s[S_IV] : kTuckerIv[s[S_OPP + i] - kTuckerSet], i, 0, HEAP_TAIL);
    (void)gd;
    return sprite;
}

/* the hook: ov012 func_ov012_02166070's call of func_ov033_0217c094 */
void *FR_BuildSetup(u8 *bsw, void *gsys) {
    u16 *s = scratch(bsw);
    void *gd, *pl, *op, *setup;
    u32 n, i, lv;
    u8 nat[4];
    u16 ids[4], evs[24];
    Fact f;
    Rd r;
    if (s[S_MAGIC] != MAGIC_FACTORY && s[S_MAGIC] != MAGIC_DOME) return BSubway_BuildSetup(bsw, gsys);   /* (the stub checks first) */
    gd = GSYS_GetGameData(gsys);
    n = s[S_COUNT];
    pl = PokeParty_Create(HEAP_TAIL);
    op = PokeParty_Create(HEAP_TAIL);
    rd_open(&r);
    if (s[S_MAGIC] == MAGIC_FACTORY) {             /* the player's three rentals (keys 79-81) */
        u16 *k = rec(gd);
        for (i = 0; i < 3; i++) { ids[i] = k[K_F_MONS + i]; fact(&r, ids[i] & 0x3ff, &f); nat[i] = f.nature; }
        make_party(pl, ids, 3, (k[K_LVL] & 1) ? 100 : 50, 32, k[K_F_SEED], nat, 0);
    } else {                                       /* the two picked for the match, as they are */
        void *party = GameData_GetParty(gd);
        PokeParty_InitCore(pl, 6);
        for (i = 0; i < n; i++) PokeParty_AddPkm(pl, PokeParty_GetPkm(party, s[S_PICK + i]));
    }
    for (i = 0; i < n; i++) {
        ids[i] = s[S_OPP + i];
        fact(&r, ids[i], &f); nat[i] = f.nature;
        if (s[S_IV] >= 32) { u32 j, b = ids[i] - kTuckerSet; for (j = 0; j < 6; j++) evs[i * 6 + j] = kTuckerEvs[b][j]; ids[i] |= kTuckerIv[b] << 10; }
    }
    rd_close(&r);
    lv = s[S_LEVEL];
#ifdef HOENN_TEST_FD_WEAK
    lv = 5;                                        /* TEST ONLY (HOENN_TEST_FD_WEAK=1): quick wins for the flow tests */
#endif
    make_party(op, ids, n, lv, s[S_IV], 0x77, nat, s[S_IV] >= 32 ? evs : 0);
    /* the battle mode: Black 2's Subway modes (BtlSetup_SetTrainerTrialHouse: 0 single, 1 double) */
    setup = SetupTrialHouseBattle(gsys, pl, rec(gd)[K_BATTLE_MODE] & 1 ? 1 : 0, bsw + BSW_TRAINERS,
                                  bsw + BSW_UNK2C8 + 288 * ((*(u16 *)(bsw + BSW_UNKC) >> 5) & 7), n);
    PokeParty_Copy(op, *(void **)((u8 *)setup + SETUP_PARTY1));
    GFL_HeapFree(pl);
    GFL_HeapFree(op);
    return setup;
}

/* ================================================================================================ party screens */
typedef struct {
    u8 *blob; void *cb;         /* frontier_fd_stub.c's EventHead */
    void *gsys;
    u16 *out;
    u32 index, result;
    u8 picked[8];
    void *party;
    u8 kind, state, need, first;
} PickWork;
#define PICK_RENT 0
#define PICK_SWAP 1
#define PICK_DOME 2

static void *open_screen(PickWork *w, u32 need) {
    void *inner;
    u8 *reg;
    u32 i;
    for (i = 0; i < 8; i++) w->picked[i] = 0;
    w->index = w->result = 0;
    inner = TeamSelect_Create(w->gsys, 0, PICK_MODE, PICK_REGULATION, w->party, w->picked, &w->index, &w->result, 0);
    reg = (u8 *)GameEvent_GetData(inner) + REG_OFFSET;
    reg[2] = need; reg[3] = need;          /* exactly `need` */
    reg[4] = 0; reg[5] = 0;                /* no level rule */
    reg[8] = 0; reg[9] = 0;                /* no species or item clause (the rentals are Emerald's own choice) */
    return inner;
}
static u32 first_pick(PickWork *w) { u32 i; for (i = 0; i < 6; i++) if (w->picked[i] >= 1 && w->picked[i] <= 6) return w->picked[i] - 1; return 0xff; }
static u32 cancelled(PickWork *w) { return w->result == 0 && (w->index == 7 || w->index == 8); }

u32 FR_PickCallback(void *event, u32 *state, void *data) {
    PickWork *w = data;
    void *gd = GSYS_GetGameData(w->gsys);
    u16 *k = rec(gd);
    u32 i, n;
    switch (*state) {
    case 0:
        w->party = PokeParty_Create(HEAP_TAIL);
        if (w->kind == PICK_RENT) {
            u8 nat[6]; Fact f; Rd r; rd_open(&r);
            for (i = 0; i < 6; i++) { fact(&r, k[K_F_MONS + i] & 0x3ff, &f); nat[i] = f.nature; }
            rd_close(&r);
            make_party(w->party, k + K_F_MONS, 6, (k[K_LVL] & 1) ? 100 : 50, 32, k[K_F_SEED], nat, 0);
            w->need = 3;
        } else if (w->kind == PICK_SWAP) {
            u8 nat[3]; Fact f; Rd r; rd_open(&r);
            for (i = 0; i < 3; i++) { fact(&r, k[K_F_MONS + i] & 0x3ff, &f); nat[i] = f.nature; }
            rd_close(&r);
            make_party(w->party, k + K_F_MONS, 3, (k[K_LVL] & 1) ? 100 : 50, 32, k[K_F_SEED], nat, 0);
            w->need = 1;
        } else {
            void *party = GameData_GetParty(gd);
            PokeParty_InitCore(w->party, 6);
            for (i = 0; i < 3; i++) {
                u32 slot = ((k[K_PARTY] >> (4 * i)) & 15) - 1;
                if (slot < PokeParty_GetPkmCount(party)) PokeParty_AddPkm(w->party, PokeParty_GetPkm(party, slot));
            }
            w->need = 2;
        }
        GameEvent_ChainNext(event, open_screen(w, w->need));
        *state = 1;
        return 0;
    case 1:
        if (w->kind == PICK_RENT) {                    /* Emerald's rental screen cannot be left without three */
            for (n = 0, i = 0; i < 6; i++) if (w->picked[i] >= 1 && w->picked[i] <= 6) n++;
            if (n != 3) { GameEvent_ChainNext(event, open_screen(w, 3)); return 0; }
            { u16 c[6]; for (i = 0; i < 6; i++) c[i] = k[K_F_MONS + i];
              for (i = 0; i < 3; i++) k[K_F_MONS + i] = c[w->picked[i] - 1];
              for (i = 3; i < 6; i++) k[K_F_MONS + i] = NONE; }
            *w->out = 1;
            break;
        }
        if (w->kind == PICK_DOME) {
            u32 slots[3];
            if (cancelled(w)) { *w->out = 0; break; }
            for (n = 0, i = 0; i < 3; i++) slots[i] = ((k[K_PARTY] >> (4 * i)) & 15) - 1;
            for (i = 0; i < 6 && n < 2; i++) if (w->picked[i] >= 1 && w->picked[i] <= 3) w->out[1 + n++] = slots[w->picked[i] - 1];
            *w->out = n == 2;
            break;
        }
        /* the swap: the player's Pokémon to give away, then the last opponent's to take */
        if (cancelled(w) || (w->first = first_pick(w)) > 2) { *w->out = 0; break; }
        { u8 nat[3]; Fact f; Rd r; rd_open(&r);
          for (i = 0; i < 3; i++) { fact(&r, k[K_F_MONS + 3 + i] & 0x3ff, &f); nat[i] = f.nature; }
          rd_close(&r);
          make_party(w->party, k + K_F_MONS + 3, 3, (k[K_LVL] & 1) ? 100 : 50, 32, k[K_F_SEED], nat, 0); }
        GameEvent_ChainNext(event, open_screen(w, 1));
        *state = 2;
        return 0;
    case 2:
        n = first_pick(w);
        if (cancelled(w) || n > 2) { *w->out = 0; break; }
        k[K_F_MONS + w->first] = k[K_F_MONS + 3 + n];
        *w->out = 1;
        break;
    }
    GFL_HeapFree(w->party);
    return 1;
}
static u32 start_pick(void *env, u16 *out, u32 kind, u8 *blob, void *evfn) {
    void *gsys = FieldScriptEnv_GetGameSystem(env);
    void *event = GameEvent_Create(gsys, 0, evfn, sizeof(PickWork));
    PickWork *w = GameEvent_GetData(event);
    zero(w, sizeof(*w));
    w->blob = blob; w->cb = (void *)FR_PickCallback;
    w->gsys = gsys; w->out = out; w->kind = kind;
    ScriptWork_CallEvent(FieldScriptEnv_GetScriptWork(env), event);
    return KEEP | 1;
}

/* ================================================================================================ the bracket */
typedef struct { void *name; u16 res; u8 ctl, unk7, rank, type, isPlayer, pad; } WbtEntrant;
typedef struct { u32 firstWon; u8 score, pad[3]; } WbtMatch;
typedef struct { void *gsys; u32 round; WbtEntrant e[8]; WbtMatch r1[4]; WbtMatch r2[2]; void *tname, *style; u32 unkA0; } WbtSetup;
typedef struct { u8 *blob; void *cb; void *gsys; WbtSetup *setup; } TreeWork;

static void sprite_res(void *h, u32 code, WbtEntrant *e) {      /* func_ov055_021e6a2c */
    u8 rec_[28];
    GFL_ArcToolReadRange(h, 0, GetIndexOfObjID(code) * 28 + 4, 28, rec_);
    e->ctl = (u8)(**(const u16 **)(kOv036ControllerTable[rec_[9] * 2] + 4) & 0x3fff);
    e->res = rec_[16] | rec_[17] << 8;
}
u32 FR_TreeCallback(void *event, u32 *state, void *data) {
    TreeWork *w = data;
    u32 i;
    if (*state == 0) {
        GFL_SndPlayerSetVolume(2, 63);
        GameEvent_ChainNext(event, EventFieldSubprocessTransition_Create(w->gsys, GSYS_GetField(w->gsys), PWT_BRACKET_OVERLAY, PWT_BRACKET_PROC, w->setup));
        *state = 1;
        return 0;
    }
    for (i = 0; i < 8; i++) GFL_StrBufFree(w->setup->e[i].name);
    GFL_StrBufFree(w->setup->tname);
    GFL_StrBufFree(w->setup->style);
    GFL_HeapFree(w->setup);
    GFL_SndPlayerSetVolume(2, 127);
    return 1;
}
static u32 show_tree(void *env, u32 half, u8 *blob, void *evfn) {
    void *gsys = FieldScriptEnv_GetGameSystem(env), *gd = gd_of(env);
    u16 *k = rec(gd);
    void *event = GameEvent_Create(gsys, 0, evfn, sizeof(TreeWork));
    TreeWork *w = GameEvent_GetData(event);
    WbtSetup *st = GFL_HeapAllocate(HEAP_EVENT, sizeof(WbtSetup), 1, "fr", 1);
    Dome *d = alloc(sizeof(Dome));
    u32 i, pl, rounds, female = ((u8 *)GetGameDataPlayerInfo(gd))[0x1d], mine = 1;
    void *mm;
    TrRec tr;
    Rd r; rd_open(&r);
    dome_build(gd, d, &r, 0);
    pl = player_id(d);
    for (i = 0; i < 8; i++) if (kTreeIds[i] == pl) mine = 0;          /* the tree half (0 left, 1 right) with the player */
    if (half > 1) half = half == 2 ? mine : 1 - mine;
    mm = GFL_ArcSysCreateFileHandle(ARC_MMODEL_TBL, HEAP_TAIL);
    st->gsys = gsys;
    for (i = 0; i < 8; i++) {
        u32 id = kTreeIds[half * 8 + i], t = d->trainer[id], code;
        WbtEntrant *e = &st->e[i];
        e->name = GFL_StrBufCreate(16, HEAP_EVENT);
        if (t == T_PLAYER) { GFL_StrBufLoadString(e->name, GetGameDataPlayerInfo(gd)); code = female ? kPlayerSpriteF : kPlayerSpriteM; e->isPlayer = 1; }
        else if (t == T_BRAIN) { load_line(kNameTucker, e->name); code = kTuckerSprite; }
        else { load_line(FR_NAME_BASE + t, e->name); trainer(&r, t, &tr); code = tr.sprite; }
        sprite_res(mm, code, e);
        e->rank = 1;
    }
    GFL_ArcToolFree(mm);
    /* results: a first-round match (tree slots 2m, 2m+1) is decided when either was knocked out in round 1, and so on */
    rounds = 0;
    for (i = 0; i < 4; i++) {
        u32 a = kTreeIds[half * 8 + 2 * i], b = kTreeIds[half * 8 + 2 * i + 1];
        st->r1[i].firstWon = d->elim[b] == 1;
        st->r1[i].score = 8;
        if (d->elim[a] == 1 || d->elim[b] == 1) rounds = 1;
    }
    for (i = 0; i < 2; i++) {
        u32 j, top = 0, bottom = 0;
        for (j = 0; j < 4; j++) {
            u32 id = kTreeIds[half * 8 + 4 * i + j];
            if (d->elim[id] == 0 || d->elim[id] > 2) { if (j < 2) top = id + 1; else bottom = id + 1; }
            if (d->elim[id] == 2) rounds = 2;
        }
        st->r2[i].firstWon = bottom == 0 || (top && d->elim[bottom - 1] == 2);
        st->r2[i].score = 8;
    }
    st->round = rounds;
    st->tname = GFL_StrBufCreate(40, HEAP_EVENT);
    st->style = GFL_StrBufCreate(40, HEAP_EVENT);
    load_line(kLineTournamentName, st->tname);
    load_line(half != mine ? kLineOtherBlock : kLineYourBlock, st->style);   /* (by the player's half, not left / right) */
    rd_close(&r);
    GFL_HeapFree(d);
    (void)k;
    w->blob = blob; w->cb = (void *)FR_TreeCallback;
    w->gsys = gsys; w->setup = st;
    ScriptWork_CallEvent(FieldScriptEnv_GetScriptWork(env), event);
    return KEEP | 1;
}

/* ================================================================================================ the command */
u32 FR_Cmd(void *vm, void *env, u8 *blob, void *evfn) {
    u32 sub = ScriptReadAny(vm, env) & 0xffff;
    u32 a = ScriptReadAny(vm, env) & 0xffff;
    u32 b = ScriptReadAny(vm, env) & 0xffff;
    u16 *var = ScriptReadVar(vm, env);
    void *gd = gd_of(env);
    u16 *k = rec(gd);
    u8 *bsw;
    switch (sub) {
    case 0: *var = a ? rnd(a) : rnd16(); return 0;                            /* FR_RANDOM n */
    case 1: *var = GFL_HeapGetFreeSize(a) >> 4; return 0;                     /* FR_HEAP_FREE heap: var = free / 16 */
    /* ---- Factory */
    case 10: factory_rentals(gd); scratch(work_of(env))[S_FLAGS] |= 1; return 0; /* F_GEN_RENTALS (+ "rented": counts) */
    case 11: return start_pick(env, var, PICK_RENT, blob, evfn);                           /* F_RENT: the screen, three of six */
    case 12: bsw = work_of(env); factory_opponent(gd, bsw);                    /* F_GEN_OPPONENT: var = 1 Noland */
             *var = scratch(bsw)[S_TRAINER] == T_BRAIN; return 0;
    case 13: *var = factory_type(work_of(env)); return 0;                      /* F_OPP_TYPE: 0-17, 18 none */
    case 14: *var = factory_style(work_of(env)); return 0;                     /* F_OPP_STYLE: 0-8 */
    case 15: return start_pick(env, var, PICK_SWAP, blob, evfn);             /* F_SWAP: var = 1 swapped */
    case 16: { u16 *s = scratch(work_of(env)); u32 i;                          /* F_KEEP_OPPONENT: keys 82-84 */
               for (i = 0; i < 3; i++) k[K_F_MONS + 3 + i] = s[S_OPP + i] | (s[S_IV] < 32 ? s[S_IV] << 10 : 31 << 10);
               return 0; }
    case 17: *var = brain_status(gd, a); return 0;                             /* FR_BRAIN_STATUS facility */
    case 18: { u16 *s = scratch(work_of(env));                                  /* F_WON: the rents count (key 85/86) */
               if (s[S_FLAGS] & 1) { rents_set(k, rents(k) + 1); s[S_FLAGS] &= ~1; }
               return 0; }
    case 19: scratch(work_of(env))[S_FLAGS] |= 1; return 0;                    /* F_SET_SWAPPED */
    case 20: { u32 i, sk = streak_key(k, FAC_FACTORY);                         /* F_INIT: a new challenge */
               k[K_BATTLE_NUM] = 0;
               for (i = 0; i < 6; i++) k[K_F_MONS + i] = NONE;
               if (k[sk] == 0) rents_set(k, 0);                                 /* Emerald: a broken streak resets it */
               (void)i; return 0; }
    /* ---- Dome */
    case 30: { Dome *d = alloc(sizeof(Dome)); Rd r; u32 sk = streak_key(k, FAC_DOME), c0;   /* D_INIT: a new tournament */
               c0 = k[sk] > 7 ? 7 : k[sk];
               k[K_D_SEED] = rnd16(); k[K_D_SEED + 1] = rnd16(); k[K_BATTLE_NUM] = 0;
               /* bit 9 tried before, bit 10: before this one; the tournament's own facts for every rebuild (the record
                  changes after it: the streak, the level and battle mode of the next challenge): bits 11-13 the trainer
                  range (min(tournaments won, 7)), 14 doubles, 15 Open Level */
               k[K_D_INFO] = ((k[K_D_INFO] & 0x200) ? 0x600 : 0x200) | c0 << 11 | (k[K_BATTLE_MODE] & 1) << 14 | (k[K_LVL] & 1) << 15;
               rd_open(&r); dome_build(gd, d, &r, 1); rd_close(&r); GFL_HeapFree(d); return 0; }
    case 31: *var = dome_opponent(gd, work_of(env)); return 0;                 /* D_OPPONENT: var = trainer (T_BRAIN) */
    case 32: return start_pick(env, var, PICK_DOME, blob, evfn);                           /* D_PICK2: var = 1, var+1/var+2 slots */
    case 33: return show_tree(env, a, blob, evfn);                                         /* D_TREE half (0 left, 1 right, 2 yours, 3 the other) */
    case 34: if (a) { if (k[K_BATTLE_NUM] < 4) k[K_BATTLE_NUM]++; }            /* D_RESULT won: next round; lost: */
             else k[K_D_INFO] = (k[K_D_INFO] & ~(7 << 5)) | ((k[K_BATTLE_NUM] + 1) << 5);   /* the round lost */
             return 0;
    case 35: { u16 *s = scratch(work_of(env)); u32 i;                          /* D_SET_PICKS a, b (party slots) */
               s[S_PICK] = a; s[S_PICK + 1] = b; (void)i; return 0; }
    case 36: { Dome *d; Rd r; u32 w = 0, i;                                       /* D_WINNER slot: the champion's name */
               if (!k[K_D_SEED] && !k[K_D_SEED + 1]) { *var = NONE; return 0; }
               d = alloc(sizeof(Dome)); rd_open(&r); dome_build(gd, d, &r, 0); rd_close(&r);
               for (i = 0; i < 16; i++) if (!d->elim[i]) w = d->trainer[i];
               GFL_HeapFree(d); word_name(env, a, w); *var = w == T_PLAYER; return 0; }
    case 37: { Dome *d = alloc(sizeof(Dome)); Rd r; u32 o;                     /* D_OPP_NAME slot: next opponent's name */
               rd_open(&r); dome_build(gd, d, &r, 0); rd_close(&r);
               o = opp_of(d, k[K_BATTLE_NUM], player_id(d));
               *var = o == 0xff ? NONE : d->trainer[o];
               if (o != 0xff) word_name(env, a, d->trainer[o]);
               GFL_HeapFree(d); return 0; }
    case 38: { Dome *d = alloc(sizeof(Dome)); Rd r; u32 o; Fact f;              /* D_OPP_SPECIES i: var = its species */
               rd_open(&r); dome_build(gd, d, &r, 0);
               o = opp_of(d, k[K_BATTLE_NUM], player_id(d));
               *var = 0;
               if (o != 0xff && a < 3) { fact(&r, d->mons[o][a], &f); *var = f.species; }
               rd_close(&r); GFL_HeapFree(d); return 0; }
    case 39: { u32 sk = streak_key(k, FAC_DOME);                                /* D_HISTORY: the announcer's kind */
               if (!(k[K_D_INFO] & 0x400)) *var = 0;                              /* first attempt */
               else if (k[sk + 1] == 0) *var = 1;                                 /* never won */
               else if (k[sk] == 0) *var = 2;                                     /* a broken streak */
               else *var = 3;                                                     /* the champion */
               return 0; }
    case 41: *var = (k[K_D_INFO] >> 14 & 1) * 2 + (k[K_D_INFO] >> 15 & 1); return 0;   /* D_PREV_KIND: doubles * 2 + Open */
    case 40: { void *sb = GFL_StrBufCreate(64, HEAP_TAIL);                       /* FR_WORD_LINE slot, line (FR_TEXT_FILE) */
               load_line(b, sb);
               WordSet_LoadStrbuf(ScriptWork_GetWordSet(FieldScriptEnv_GetScriptWork(env)), a, sb, 0, 1, 2);
               GFL_StrBufFree(sb); return 0; }
    /* ---- the battle (both) */
    case 50: *var = battle_prep(env, a); return 0;                             /* B_PREP facility: var = sprite */
    case 51: { u8 *w = work_of(env); void *gsys = FieldScriptEnv_GetGameSystem(env), *ev;   /* B_BATTLE */
               u16 *sc = scratch(w);
               sc[S_BLOB] = (u32)blob & 0xffff; sc[S_BLOB + 1] = (u32)blob >> 16;   /* for the setup hook (called now) */
               ev = SubwayBattle_Event(w, gsys, GSYS_GetField(gsys));
               sc[S_BLOB] = sc[S_BLOB + 1] = 0;
               ScriptWork_CallEvent(FieldScriptEnv_GetScriptWork(env), ev);
               return 1; }
    case 52: { u8 *w = work_of(env); void *setup = *(void **)(w + BSW_SETUP);  /* B_RESULT: var = 1 won; frees the setup */
               *var = setup && *(u32 *)((u8 *)setup + SETUP_RESULT) == 1;
               if (setup) { FreeVSPlayerBlk(); BtlSetup_Free(setup); *(void **)(w + BSW_SETUP) = 0; }
               return 0; }
    case 53: bsw = BSubway_GetWork(gd); BSubwayWork_Free(FieldScriptEnv_GetGameSystem(env), bsw); return 0;  /* B_END */
    case 54: { u32 t = scratch(work_of(env))[S_TRAINER];                       /* B_SPEECH: var = the greeting's line */
               *var = t == T_BRAIN ? NONE : FR_SPEECH_BASE + t; return 0; }
    case 55: word_name(env, a, scratch(work_of(env))[S_TRAINER]); return 0;    /* B_NAME slot */
    case 56: *var = scratch(work_of(env))[S_GOLD]; return 0;                   /* B_BRAIN_GOLD: 1 silver, 2 gold party */
    }
    return 0;
}
