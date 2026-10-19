/* The Fairy type (Gen 6 rules) and the physical/special split toggle: code in ITCM, compiled and linked by
 * b2tools/patches/fairy.py (which has the findings, every hook site and notes/FAIRY.md's design).
 *
 * Toggles: the options u16 at the start of the trainer-data save block (getTrainerDataBlkAddress, SaveControl block 27),
 * whose bits 0-10 the option accessors 0x0200898c-0x02008b0c use and whose bits 11-15 nothing reads:
 *   bit 11 (CFG_FAIRY)   1 = Fairy type on (Gen 6 chart, retypes, Fairy moves)       0 = Black 2's Gen 5 types
 *   bit 12 (CFG_CLASSIC) 1 = Gen 3 rule: a damaging move's category comes from its type  0 = Black 2's per-move split
 *   bit 15 (CFG_SEASONS) 1 = Black 2's seasons by the DS clock's month                    0 = summer all year
 * Birch's questions in the intro set them once (Intro_SetConfigBit); a new game starts with all of them 0 (bits 13
 * and 14 are hoenn_music's and sprite_switch's).
 *
 * Types: 0-16 Black 2's, 17 = Fairy, 18 = "no type" (Black 2 used 17; every such check in ov167 moves to 18).
 * The data (a/0/1/6 species, a/0/2/1 moves) holds the Gen 6 types; with the toggle off the two readers below give
 * the old ones back, so nothing outside them ever sees type 17. */
typedef unsigned char u8;
typedef signed char s8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef int s32;

#define FN(type, addr) ((type)((addr) | 1))
/* arm9 */
#define SaveControl_GetBlockPtr    FN(u8 *(*)(void *, u32), 0x02007448)
#define PML_PersonalGetDatID       FN(u32 (*)(u32, u32), 0x02020480)
#define PML_MoveGetParamCore       FN(u32 (*)(const u8 *, u32), 0x0202130c)
#define PML_MoveGetCategory        FN(u32 (*)(u32), 0x02021740)
#define GFL_ArcToolGetDataOfs      FN(u32 (*)(void *, u32), 0x0204ad14)
#define GFL_ArcToolReadRaw         FN(void (*)(void *, u32, void *), 0x0204ad64)
#define GFL_ArcToolSeek            FN(void (*)(void *, u32), 0x0204ad74)
#define g_SaveControlWork          (*(void **)0x02140f60)
#define g_PMLPersonalNowLoadForme  ((u16 *)0x0214111c)      /* [0] form, [1] species of g_PersonalDataCache */
#define g_PersonalDataCache        ((u8 *)0x021411a0)
#define g_PMLPersonalArcBW2        (*(void **)0x021413e8)
/* ov167 (battle; loaded whenever these hooks run) */
#define BattleEventVar_Pop         FN(void (*)(u32), 0x021bcd54)
#define CommonTypeBoostingItem     FN(void (*)(void *, void *, u32, u32), 0x021c5164)
#define CommonGemDecide            FN(void (*)(void *, void *, u32, void *, u32), 0x021c59fc)
#define CommonGemPower             FN(void (*)(void *, void *, u32, void *, u32), 0x021c5aac)
#define BtlNet_SendSync            FN(u32 (*)(u8 *), 0x021b9bb8)   /* func_ov167_021b9bb8: send the 32-byte sync to all */
#define BtlNet_RecvSync            FN(u32 (*)(u8 *), 0x021b9c0c)   /* func_ov167_021b9c0c: TRUE once it has arrived */
#define BtlProc_InitSub            FN(void (*)(u32, u32, u32, u32), 0x021ce10c)   /* the battle proc's first ... */
#define BtlProc_ExitSub            FN(void (*)(u32, u32, u32, u32), 0x021ce138)   /* ... and last call */
#define VANILLA_CHART              ((const u8 *)0x021d7500)  /* data_ov167_021d7500, u8[17][17] in halves: 0 2 4 8 */

#define CFG_FAIRY   (1u << 11)
#define CFG_CLASSIC (1u << 12)
#define CFG_SEASONS (1u << 15)
#define TYPE_NORMAL 0
#define TYPE_FAIRY  17
#define TYPE_NONE   18
#define EFF_NEUTRAL 3       /* GetTypeEffectiveness's codes: 0 immune, 2 half, 3 neutral, 4 double */

#include "fairy_data.h"      /* written by fairy.py: kChart6, kClassic, retypes, fallbacks, donors, items */
#define STR2(x) #x
#define STR(x) STR2(x)
#ifdef FAIRY_SELFTEST
static void SelfTest_Hook(void);
#endif

/* ---- toggles ------------------------------------------------------------------------------------------------- */
/* Link battles (link, 2026-10-18; notes/LINK.md): both machines must use the same Fairy and split rules, or they
 * compute different damage and the battle desyncs (each machine runs the battle's calculations: the client keeps its
 * own server copy, BtlMainModule unk0C). Before the parties, Black 2 sends one BtlMainSyncData (32 bytes: the random
 * state, ...) from the battle's server machine to every machine (ov167 func_ov167_0219ada0, every link battle style,
 * local wireless and Wi-Fi alike). Its byte 0x1f has 4 spare bits (unk1F_4: the main module is zeroed and nothing
 * writes or reads them). The server writes 8 | Fairy (bit 0) | classic split (bit 1) there (Link_SyncSend); every
 * machine, the server included, takes the bits it receives as the battle's rules (Link_SyncRecv), and config()
 * answers them instead of the save's bits 11-12 until the battle proc ends (Link_BattleInit / Link_BattleExit clear
 * them). A server without this code sends 0, read as Black 2's rules (no Fairy, per-move split): right for an
 * unmodified Black 2; an older HoennB2 release computes with its own options instead, but link.py's GGID keeps those
 * out of local wireless. gLinkRules: 0 none, else 0x100 | the two bits; it lives in ITCM (.text, as emerald_mech's
 * gEmPhase): 0 at boot. */
__asm__(".text\n\t.align 2\n\t.global gLinkRules\ngLinkRules:\n\t.word 0\n");
extern volatile u32 gLinkRules;
#define LINK_SYNC_RULES 0x1f        /* BtlMainSyncData byte: bits 4-7 = unk1F_4 */

static u32 config_saved(void) {
    void *sc = g_SaveControlWork;
    if (!sc) return 0;
    return *(const u16 *)SaveControl_GetBlockPtr(sc, 27);
}

static u32 config(void) {
    u32 v = config_saved(), r = gLinkRules;
    if (r) v = (v & ~(CFG_FAIRY | CFG_CLASSIC)) | (r & 1 ? CFG_FAIRY : 0) | (r & 2 ? CFG_CLASSIC : 0);
    return v;
}

/* ov167 func_ov167_0219ada0: its `bl func_ov167_021b9bb8` (the server sends, r0 = &mainModule->syncData) */
u32 Link_SyncSend(u8 *sync) {
    u32 v = config_saved();
    sync[LINK_SYNC_RULES] = (u8)((sync[LINK_SYNC_RULES] & 0x0f)
                                 | ((8 | (v & CFG_FAIRY ? 1 : 0) | (v & CFG_CLASSIC ? 2 : 0)) << 4));
    return BtlNet_SendSync(sync);
}

/* ... and its `bl func_ov167_021b9c0c` (every machine receives it into the same struct) */
u32 Link_SyncRecv(u8 *sync) {
    u32 ok = BtlNet_RecvSync(sync), n;
    if (ok) {
        n = sync[LINK_SYNC_RULES] >> 4;
        gLinkRules = 0x100 | ((n & 8) ? (n & 3) : 0);
    }
    return ok;
}

/* ov167 func_ov167_021998c0 (battle proc init) `bl func_ov167_021ce10c` and func_ov167_02199cd4 (battle proc end)
 * `bl func_ov167_021ce138`: every battle starts and ends with the save's rules (arguments passed through) */
void Link_BattleInit(u32 a, u32 b, u32 c, u32 d) { gLinkRules = 0; BtlProc_InitSub(a, b, c, d); }
void Link_BattleExit(u32 a, u32 b, u32 c, u32 d) { gLinkRules = 0; BtlProc_ExitSub(a, b, c, d); }

/* Exported for fairy_ui (Thumb, 0/1 in r0, C calling convention: clobbers only r0-r3, r12, lr) */
u32 Fairy_IsOn(void) { return (config() & CFG_FAIRY) != 0; }
u32 Split_IsClassic(void) { return (config() & CFG_CLASSIC) != 0; }

/* ---- seasons (Birch's fifth question; patches/hoenn_season.py, notes/SEASONS.md) -------------------------------
 * hoenn_season locks Black 2's two season readers to summer; fairy.py points them here instead, so the lock holds
 * only while bit 15 is 0 (every save made before the question, a "No", no save loaded yet).
 * Season_FromMonth: Season_GetRealTime (arm9 0x02034f6c) calls it with the RTC month (1-12) in r0 where it computed
 *   (month - 1) & 3 (0 spring, 1 summer, 2 autumn, 3 winter); r1-r3 are dead there.
 * Season_Kept: GameData_GetSeason (arm9 0x020173ac) jumps here; the kept season is GameData +0x1c8. */
u32 Season_FromMonth(u32 month) { return (config() & CFG_SEASONS) ? ((month - 1) & 3) : 1; }
u32 Season_Kept(const u8 *gameData) { return (config() & CFG_SEASONS) ? gameData[0x1c8] : 1; }

/* ---- type chart (replaces ov167 GetTypeEffectiveness 0x021bd160 and GetTypeWeaknesses 0x021bd2b0) ---------------- */
static u32 vanilla_eff(u32 a, u32 d) {
    switch (VANILLA_CHART[a * 17 + d]) {
    case 0: return 0;
    case 2: return 2;
    case 4: return 3;
    case 8: return 4;
    }
    return 0;
}

u32 Fairy_TypeEff(u32 attackType, u32 defenseType) {
    u32 a = attackType & 0xff, d = defenseType & 0xff;
#ifdef FAIRY_SELFTEST
    SelfTest_Hook();
#endif
    if (Fairy_IsOn()) {
        if (a >= 18 || d >= 18) return EFF_NEUTRAL;
        return kChart6[a * 18 + d];
    }
    if (a >= 17 || d >= 17) return EFF_NEUTRAL;      /* Black 2: 17 = no type -> neutral */
    return vanilla_eff(a, d);
}

/* The types a move of attackType is resisted by or does nothing to (Conversion 2), as Black 2's loop over the chart */
u32 Fairy_TypeWeaknesses(u32 attackType, u8 *out) {
    u32 n = Fairy_IsOn() ? 18 : 17, i, count = 0;
    for (i = 0; i < n; i++) {
        u32 e = Fairy_TypeEff(attackType, i);
        if (e == 0 || e == 2) out[count++] = (u8)i;
    }
    return count;
}

/* ---- move data (hook in PML_MoveGetParam 0x02021280, the only reader of a/0/2/1's type and category) ------------- */
static u32 old_move_type(u32 move) {
    if (move >= FIRST_NEW_MOVE && move < FIRST_NEW_MOVE + N_NEW_MOVES) return kNewMoveFallback[move - FIRST_NEW_MOVE];
    return TYPE_NORMAL;      /* Sweet Kiss, Charm, Moonlight: Normal in Black 2 */
}

static u32 move_type(const u8 *rec, u32 move) {
    u32 t = rec[0];
    if (t == TYPE_FAIRY && !Fairy_IsOn()) t = old_move_type(move);
    return t;
}

u32 Fairy_MoveParam(const u8 *rec, u32 param, u32 move) {
    u32 v = PML_MoveGetParamCore(rec, param);
    if (param == 0) return move_type(rec, move);
    if (param == 2 && v != 0 && Split_IsClassic()) {
        u32 t = move_type(rec, move);
        v = kClassic[t < 19 ? t : TYPE_NONE];
    }
    return v;
}

/* PML_MoveGetParam: `mov r0, r5; mov r1, r6; bl PML_MoveGetParamCore` -> bl here; r4 holds the move id */
__attribute__((naked)) void Fairy_MoveParamShim(void) {
    __asm__ volatile("adds r2, r4, #0\n\tldr r3, 1f\n\tbx r3\n\t.align 2\n1:\t.word Fairy_MoveParam\n");
}

/* ---- species data (replaces PML_PersonalFetchBW2 0x02020234 and PML_PersonalLoadBW2 0x0201eee0) ---------------- */
void Fairy_PersonalFetch(u32 species, u32 form, u8 *dest) {
    u32 id = PML_PersonalGetDatID(species, form), i;
    void *arc = g_PMLPersonalArcBW2;
    GFL_ArcToolSeek(arc, GFL_ArcToolGetDataOfs(arc, id));
    GFL_ArcToolReadRaw(arc, 0x4c, dest);
    if (Fairy_IsOn()) return;
    for (i = 0; i < N_RETYPES; i++) {
        if (kRetypeId[i] == id) {      /* the Gen 6 record back to Black 2's types (record +6 type 1, +7 type 2) */
            dest[6] = kRetypeOld[i][0];
            dest[7] = kRetypeOld[i][1];
            break;
        }
    }
}

/* Black 2's one-record cache, keyed by (form, species); bit 15 of the form key is the Fairy toggle the record was read
 * with, so a record read before Birch's answer is never handed out after it */
u8 *Fairy_PersonalLoad(u32 species, u32 form) {
    u16 *key = g_PMLPersonalNowLoadForme;
    u32 kform = (form & 0x7fff) | (Fairy_IsOn() ? 0x8000 : 0);
    if (key[1] != (u16)species || key[0] != (u16)kform) {
        key[0] = (u16)kform;
        key[1] = (u16)species;
        Fairy_PersonalFetch(species, form, g_PersonalDataCache);
    }
    return g_PersonalDataCache;
}

/* ---- intro: Birch's questions (ov294 sCommands[INTRO_CMD_SET_MSG_LANGUAGE = 31], unused by the US scripts) ------
 * args[0] = config bit, args[1] = value. IntroCmd +4 = IntroParam, IntroParam +4 = the new game's Config (ov162 copies
 * it into the save in NewGame_Exit); the save's own copy gets the bit at once too, so every reader agrees from here */
u32 Intro_SetConfigBit(void *cmd, void *work, s32 *args) {
    u16 *cfg = *(u16 **)(*(u8 **)((u8 *)cmd + 4) + 4);
    u32 mask = 1u << (args[0] & 15);
    void *sc = g_SaveControlWork;
    (void)work;
    if (args[1]) *cfg |= mask; else *cfg &= ~mask;
    if (sc) {
        u16 *save = (u16 *)SaveControl_GetBlockPtr(sc, 27);
        if (args[1]) *save |= mask; else *save &= ~mask;
    }
    return 1;
}

/* ---- battle: the classic split on the move's final type (after Hidden Power, Weather Ball, Normalize ...) --------
 * BtlFlowMoveParam: +0 u16 move, +6 u8 type, +8 u32 category (ov167 ServerEvent_GetMoveParam fills it) */
static u32 param_category(u32 move, const u8 *param) {
    u32 c = PML_MoveGetCategory(move);
    if (c != 0 && Split_IsClassic()) {
        u32 t = param[6];
        c = kClassic[t < 19 ? t : TYPE_NONE];
    }
    return c;
}
u32 Split_CatR4(u32 move, const u8 *param) { return param_category(move, param); }
__attribute__((naked)) void Split_CatShimR4(void) {    /* ServerEvent_CalcDamage: param in r4 */
    __asm__ volatile("adds r1, r4, #0\n\tldr r2, 1f\n\tbx r2\n\t.align 2\n1:\t.word Split_CatR4\n");
}
__attribute__((naked)) void Split_CatShimR5(void) {    /* ServerEvent_GetAttackPower: param in r5 */
    __asm__ volatile("adds r1, r5, #0\n\tldr r2, 1f\n\tbx r2\n\t.align 2\n1:\t.word Split_CatR4\n");
}
__attribute__((naked)) void Split_CatShimR6(void) {    /* ServerEvent_GetTargetDefenses: param in r6 */
    __asm__ volatile("adds r1, r6, #0\n\tldr r2, 1f\n\tbx r2\n\t.align 2\n1:\t.word Split_CatR4\n");
}

/* end of ServerEvent_GetMoveParam (param in r4): the category from the final type, then the original Pop */
void Split_MoveParamEnd(u32 popId, u8 *param) {
    u32 *cat = (u32 *)(param + 8);
    if (*cat != 0 && Split_IsClassic()) {
        u32 t = param[6];
        *cat = kClassic[t < 19 ? t : TYPE_NONE];
    }
    BattleEventVar_Pop(popId);
}
__attribute__((naked)) void Split_MoveParamEndShim(void) {
    __asm__ volatile("adds r1, r4, #0\n\tldr r2, 1f\n\tbx r2\n\t.align 2\n1:\t.word Split_MoveParamEnd\n");
}

/* ---- battle animation of the new moves (ov167 func_ov167_021cfc60's call of func_ov167_021d3094, r3 = move) ------
 * a/0/6/5 holds animations for ids < 561 only (ov168 func_ov168_021e0ee8); a new move plays a donor's */
__attribute__((naked)) void Fairy_AnimShim(void) {
    __asm__ volatile(
        "push {r0, r1}\n\t"
        "ldr r0, 2f\n\t"
        "cmp r3, r0\n\t"
        "blo 1f\n\t"
        "subs r1, r3, r0\n\t"
        "cmp r1, #" STR(N_NEW_MOVES) "\n\t"
        "bhs 1f\n\t"
        "lsls r1, r1, #1\n\t"
        "ldr r0, 3f\n\t"
        "ldrh r3, [r0, r1]\n"
        "1:\tldr r0, 4f\n\t"
        "mov r12, r0\n\t"
        "pop {r0, r1}\n\t"
        "bx r12\n\t"
        ".align 2\n"
        "2:\t.word " STR(FIRST_NEW_MOVE) "\n"
        "3:\t.word kAnimDonor\n"
        "4:\t.word 0x021d3095\n");
}

/* Metronome's move count (ov167 func_ov167_021bd658 `mov r0, #0x23; lsl r0, r0, #4` = 0x230 -> bl here) */
u32 Fairy_MoveCount(void) { return FIRST_NEW_MOVE + N_NEW_MOVES; }

/* ---- held items ---------------------------------------------------------------------------------------------------
 * Pixie Plate: as the other plates (EventAdd*Plate -> {0x38, handler}, handler = CommonTypeBoostingItem(.., type)).
 * Fairy Gem: as the other gems ({0x81 decide, 0x38 power, 0x88 0x021c5ae9 the shared "used" handler}).
 * Both never fire with the toggle off: no move is Fairy-type then. */
typedef struct { u32 event; void *handler; } Handler;

void Fairy_PlateHandler(void *flow, void *a1, u32 a2) { CommonTypeBoostingItem(flow, a1, a2, TYPE_FAIRY); }
static const Handler kPlateHandlers[1] = { { 0x38, (void *)Fairy_PlateHandler } };
const Handler *EventAddPixiePlate(u32 *count) { *count = 1; return kPlateHandlers; }

void Fairy_GemDecide(void *flow, void *a1, u32 a2, void *a3) { CommonGemDecide(flow, a1, a2, a3, TYPE_FAIRY); }
void Fairy_GemPower(void *flow, void *a1, u32 a2, void *a3) { CommonGemPower(flow, a1, a2, a3, TYPE_FAIRY); }
static const Handler kGemHandlers[3] = {
    { 0x81, (void *)Fairy_GemDecide }, { 0x38, (void *)Fairy_GemPower }, { 0x88, (void *)0x021c5ae9 } };
const Handler *EventAddFairyGem(u32 *count) { *count = 3; return kGemHandlers; }

/* ItemEvent_AddItemCore's {item, EventAdd} table, moved here from ov167 0x021d8f28 (172 entries, the last one free)
 * with the two new items: fairy.py writes kItemEvents (its entries are Black 2's, then ours) */
#include "fairy_items.h"

/* ---- the shop that sells them: with the toggle on, Lilycove Dept. Store 3F's right clerk (shop id SHOP_ID) reads
 * the list file SHOP_FILE (its own list + the two items, fairy.py) instead of SHOP_ID + 6. ov036
 * ShopUI_LoadPokeMartItems reads the list with GFL_ArcSysReadHeapNew(0x11a, r4, heap) and then the item count byte
 * [r4] of a/2/8/3 file 0, so the shim changes r1 and the caller's r4 */
u32 Fairy_ShopFile(u32 file) { return (file == SHOP_ID + 6 && Fairy_IsOn()) ? SHOP_FILE : file; }
__attribute__((naked)) void Fairy_ShopShim(void) {
    __asm__ volatile(
        "push {r0, r1, r2, lr}\n\t"
        "adds r0, r1, #0\n\t"
        "bl Fairy_ShopFile\n\t"
        "adds r4, r0, #0\n\t"
        "pop {r0, r1, r2}\n\t"
        "adds r1, r4, #0\n\t"
        "pop {r3}\n\t"
        "mov lr, r3\n\t"
        "ldr r3, 1f\n\t"
        "bx r3\n\t"
        ".align 2\n"
        "1:\t.word 0x0204a935\n");     /* GFL_ArcSysReadHeapNew */
}

#ifdef FAIRY_SELFTEST
#include "fairy_selftest.h"
#endif
