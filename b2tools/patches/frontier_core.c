/* The Battle Frontier's shared systems (frontier_core, 2026-10-12): Pokémon Emerald NDS builds only. Compiled and
 * placed in ITCM by b2tools/patches/frontier_core.py (after emerald_mech), which also has the findings.
 * notes/FRONTIER.md is the interface for the facility scripts (src/include/hoenn_frontier.inc has the macros).
 *
 *   command 230 (Black 2's TrainerCardCmd_00E6, unused by every script): FrGet key, var    (args any, var)
 *   command 232 (Black 2's TrainerCardCmd_00E8, unused):                 FrOp op, var      (args any, var)
 *
 * Save data:
 *   Battle Points: Black 2's own, the u16 at the start of its Battle Subway score block (save block 0x39; arm9
 *     func_0200e318 adds and caps at 9,999, func_0200e330 takes, func_0200e354 reads).
 *   The Frontier's records: 96 u16 after the 60 bytes Black 2 uses of its Battle Subway play block (save block 0x38,
 *     a 256-byte slot: frontier_core.py makes the block 252 bytes long, so no other block moves). Black 2's own code
 *     never reads past byte 60 of that block (its clear, func_0200e0f4, still clears only 60: the Battle Tower's
 *     challenges do not touch the records); a new game clears all 252 (FR_PlayInit, the block's initializer).
 *   BP shop lists: Emerald's Exchange Service Corner lists on Black 2's BP shop screen (FR_ShopMsgData).
 *   BP window: Black 2's money window with the shop's "N BP" line (FR_BPWin).
 */
typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef int s32;

#define FN(type, addr) ((type)((addr) | 1))
#define ARMFN(type, addr) ((type)(addr))
#define ScriptReadVar              FN(u16 *(*)(void *, void *), 0x021548e8)
#define ScriptReadAny              FN(u32 (*)(void *, void *), 0x02154910)
#define FieldScriptEnv_GetGameData FN(void *(*)(void *), 0x02155174)
#define FieldScriptEnv_GetGameSystem FN(void *(*)(void *), 0x0215516c)
#define FieldScriptEnv_GetScriptWork FN(void *(*)(void *), 0x02155184)
#define GameData_GetSaveControl    FN(void *(*)(void *), 0x02017934)
#define GameData_GetParty          FN(void *(*)(void *), 0x0201735c)
#define SaveControl_GetBlockPtr    FN(void *(*)(void *, u32), 0x02007448)
#define GetBSubwayScore            FN(void *(*)(void *), 0x0201795c)      /* func_0201795c(gameData): block 0x39 */
#define BP_Add                     FN(void (*)(void *, u16), 0x0200e318)  /* adds, caps at 9,999 */
#define BP_Take                    FN(void (*)(void *, u16), 0x0200e330)  /* takes, floors at 0 */
#define BP_Get                     FN(u16 (*)(void *), 0x0200e354)
#define getTrainerCardInfoBlkAddress FN(void *(*)(void *), 0x02009408)
#define RecordAdd                  FN(void (*)(void *, u32, u32), 0x0200955c)
#define PokeParty_GetParam         FN(u32 (*)(void *, u32, void *), 0x0201ccf8)
#define PokeParty_GetPkmCount      FN(u32 (*)(void *), 0x0201fdf8)
#define PokeParty_GetPkm           FN(void *(*)(void *, u32), 0x0201ff08)
#define sys_reset                  ARMFN(void (*)(u32), 0x0207c29c)
#define FieldScriptEnv_GetHeapID   FN(u32 (*)(void *), 0x0215515c)
#define GameData_GetPokedex        FN(void *(*)(void *), 0x0200d190)
#define PokeDex_IsCaught           FN(u32 (*)(void *, u32), 0x0200d660)
#define g_PMLSpeciesNamesResident  (*(void **)0x0209a434)                 /* the species names' message data */
#define GFL_StrBufAppend           FN(void (*)(void *, u16), 0x02048734)
#define GFL_StrBufConcat           FN(void (*)(void *, void *), 0x02048700)
#define GFL_WordSetCopyStrbuf      FN(void (*)(void *, u32, void *, void *), 0x020242f4)
/* the shop screen (ov036) */
#define ShopUI_LoadMsgData         FN(u32 (*)(void *, u32), 0x021aca14)
#define BP_SHOP_ITEMS              ((u32 *)0x021d5160)                    /* 2 list pointers (ids 254, 253) */
#define BP_SHOP_ITEM_COUNTS        ((u8 *)0x021d0918)
#define B2_BP_LIST0                0x021d0e08u                            /* Black 2's own list 0 (42 items) */
#define B2_BP_COUNT0               42
#define SHOP_BP_ITEMS              254                                    /* ShopUI_Init: BP shop, list 0 */
/* the money window (ov036 s0040_MoneyWinDisp, re-done with the BP) */
#define GSYS_GetField              FN(void *(*)(void *), 0x02016af0)
#define Field_GetMsgBGSys          FN(void *(*)(void *), 0x02180490)
#define Field_GetHeapID            FN(u32 (*)(void *), 0x021804c0)
#define Field_GetMoneyWin          FN(void *(*)(void *), 0x02180588)
#define Field_SetMoneyWin          FN(void (*)(void *, void *), 0x0218058c)
#define FieldMsgBG_CreateMoneyWin  FN(void *(*)(void *, void *, u32, u32, u32, u32), 0x02187bfc)
#define MoneyWin_Delete            FN(void (*)(void *), 0x02187c1c)
#define MoneyWin_Print             FN(void (*)(void *, u32, u32, void *), 0x02187c4c)
#define ScriptWork_GetWordSet      FN(void *(*)(void *), 0x02153ec4)
#define ScriptWork_GetAltStrBuf    FN(void *(*)(void *), 0x02153ecc)
#define GFL_MsgSysLoadData         FN(void *(*)(u32, u32, u32, u32), 0x0204875c)
#define GFL_MsgDataFree            FN(void (*)(void *), 0x020487d4)
#define GFL_MsgDataLoadStrbuf      FN(void (*)(void *, u32, void *), 0x02048838)
#define GFL_StrBufCreate           FN(void *(*)(u32, u32), 0x02048530)
#define GFL_StrBufFree             FN(void (*)(void *), 0x02048564)
#define WordSetNumber              FN(void (*)(void *, u32, u32, u32, u32, u32), 0x0202451c)
#define GFL_WordSetFormatStrbuf    FN(void (*)(void *, void *, void *), 0x02024920)

#define PKM_PARAM_SPECIES 0x05
#define PKM_PARAM_ITEM    0x06
#define PKM_PARAM_LEVEL   0x9e
#define PKM_PARAM_IS_EGG  0x4c

#define PLAY_BLOCK        0x38      /* Black 2's Battle Subway play block */
#define PLAY_B2_SIZE      60        /* what Black 2 uses of it */
#define PLAY_SIZE         252       /* the Emerald build's size: 252 + 4 (footer) = its 256-byte slot */
#define N_KEYS            ((PLAY_SIZE - PLAY_B2_SIZE) / 2)   /* 96 */
#define RECORD_ADD_BP     0x21      /* Black 2's trainer card record of BP earned (its own award commands add it) */
#define BP_MAX            9999
#define STREAK_MAX        9999      /* pokeemerald MAX_STREAK */

/* keys (notes/FRONTIER.md 2.2) */
#define K_STATUS 0
#define K_FACILITY 1
#define K_BATTLE_MODE 2
#define K_LVL_MODE 3
#define K_PARTY 4
#define K_BATTLE_NUM 5
#define K_SYMBOLS 6
#define K_LAST_BP 7
#define K_STREAKS 16                /* 16 + 8f + 4m + 2l current, + 1 best */

/* frontier_core_data.h (written by frontier_core.py from pokeemerald): N_AWARD_ROWS, kAwards[row][7][4],
 * kStreakDiv[7], kBanned[] (national numbers, 0-terminated), N_SHOPS, kShopIds[], kShopCount[], kShopItems[][..]
 * (8-byte entries as Black 2's BP lists: u16 item, u16 0, u32 price), kTutorCost/Tutor/Move[2][10] */
#include "frontier_core_data.h"

static u32 udiv(u32 a, u32 b) {                      /* no division helper in the blob: small numbers only */
    u32 q = 0;
    if (!b) return 0;
    while (a >= b) { a -= b; q++; }
    return q;
}

static u16 *records(void *gd) {
    return (u16 *)((u8 *)SaveControl_GetBlockPtr(GameData_GetSaveControl(gd), PLAY_BLOCK) + PLAY_B2_SIZE);
}

static u32 streak_key(u16 *rec, u32 arg) {           /* arg = f | m << 3 -> the current streak's key */
    u32 f = arg & 7, m = (arg >> 3) & 1, l = rec[K_LVL_MODE] & 1;
    if (f > 6) f = 6;
    return K_STREAKS + 8 * f + 4 * m + 2 * l;
}

/* pokeemerald frontier_util.c CheckPartyIneligibility / AppendIfValid, counting from each start slot */
static u32 eligible(void *gd, u32 lvl50) {
    void *party = GameData_GetParty(gd);
    u32 n = PokeParty_GetPkmCount(party), best = 0, start, k, i;
    for (start = 0; start < n; start++) {
        u16 sp[6], it[6];
        u32 count = 0;
        for (k = 0; k < n; k++) {
            u32 slot = start + k;
            void *pkm;
            if (slot >= n) slot -= n;
            pkm = PokeParty_GetPkm(party, slot);
            u32 species = PokeParty_GetParam(pkm, PKM_PARAM_SPECIES, 0);
            u32 item = PokeParty_GetParam(pkm, PKM_PARAM_ITEM, 0);
            const u16 *b;
            if (species == 0 || PokeParty_GetParam(pkm, PKM_PARAM_IS_EGG, 0)) continue;
            for (b = kBanned; *b && *b != species; b++) ;
            if (*b) continue;
            if (lvl50 && PokeParty_GetParam(pkm, PKM_PARAM_LEVEL, 0) > 50) continue;
            for (i = 0; i < count && sp[i] != species; i++) ;
            if (i != count) continue;
            if (item) {
                for (i = 0; i < count && it[i] != item; i++) ;
                if (i != count) continue;
            }
            sp[count] = (u16)species;
            it[count] = (u16)item;
            count++;
        }
        if (count > best) best = count;
        if (best >= 3) break;
    }
    return best;
}

static void add_bp(void *gd, u32 amount) {
    if (!amount) return;
    BP_Add(GetBSubwayScore(gd), (u16)amount);
    RecordAdd(getTrainerCardInfoBlkAddress(GameData_GetSaveControl(gd)), RECORD_ADD_BP, amount);
}

/* pokeemerald GiveBattlePoints: sBattlePointAwards[challengeNum][facility][battleMode] (+10 for a Frontier Brain) */
static u32 award(u16 *rec, u32 streak, u32 brain) {
    u32 f = rec[K_FACILITY], m = rec[K_BATTLE_MODE] & 3, row, pts;
    if (f > 6) return 0;
    row = udiv(streak, kStreakDiv[f]);
    if (row) row--;                                     /* pokeemerald: if (challengeNum != 0) challengeNum--; */
    if (row >= N_AWARD_ROWS) row = N_AWARD_ROWS - 1;
    pts = kAwards[row][f][m];
    if (brain) pts += 10;
    return pts;
}

/* pokeemerald CheckPartyIneligibility's {STR_VAR_1} of the "not enough eligible Pokémon" lines
 * ("Eggs{STR_VAR_1} ineligible."): the banned species the player has caught (Pokédex), in the banned list's order,
 * joined as AppendCaughtBannedMonSpeciesName does (", " / " and ", a new line after the 2nd name, a scroll after the
 * 4th, 6th ...), then " are" or (after an odd count) a scroll + "are". Into word buffer `word`; returns the count. */
static void put(void *sb, const char *t) { while (*t) GFL_StrBufAppend(sb, (u16)(u8)*t++); }
static void scroll(void *sb) {                         /* Black 2's {be00} + new line (Gen 3's \l) */
    GFL_StrBufAppend(sb, 0xF000); GFL_StrBufAppend(sb, 0xBE00); GFL_StrBufAppend(sb, 0x0000);
    GFL_StrBufAppend(sb, 0xFFFE);
}
static u32 banned_names(void *env, void *gd, u32 word) {
    void *dex = GameData_GetPokedex(gd);
    u32 heap = FieldScriptEnv_GetHeapID(env);
    void *out = GFL_StrBufCreate(400, heap), *name = GFL_StrBufCreate(32, heap);
    const u16 *b;
    u32 total = 0, count = 0;
    for (b = kBannedNames; *b; b++) if (PokeDex_IsCaught(dex, *b)) total++;
    for (b = kBannedNames; *b; b++) {
        if (!PokeDex_IsCaught(dex, *b)) continue;
        count++;
        put(out, count == total ? " and " : ", ");
        if (count == 2) GFL_StrBufAppend(out, 0xFFFE);
        else if (count >= 4 && !(count & 1)) scroll(out);
        GFL_MsgDataLoadStrbuf(g_PMLSpeciesNamesResident, *b, name);
        GFL_StrBufConcat(out, name);
    }
    if (count & 1) scroll(out);
    else put(out, " ");
    put(out, "are");
    GFL_WordSetCopyStrbuf(ScriptWork_GetWordSet(FieldScriptEnv_GetScriptWork(env)), word, out, 0);
    GFL_StrBufFree(name);
    GFL_StrBufFree(out);
    return count;
}

/* pokeemerald GetFrontierEnemyMonLevel for the Battle Tower: Open Level (Black 2's play mode 5, the tower's Lv. 100
 * room) = the highest level among the player's Pokémon in the battle (the three entered: Emerald's party is cut to
 * them, ReducePlayerPartyToSelectedMons), at least 60 (FRONTIER_MIN_LEVEL_OPEN); every other mode battle_tower.py's
 * 50 + 10 x mode (Lv. 50: 50). setup = the battle setup (+36: the player's battle party, filled by RestrictPlayerParty
 * before the opponents are loaded). */
#define TOWER_MODE_OPEN 5
#define FRONTIER_MIN_LEVEL_OPEN 60
#define BTLSETUP_PARTY0 36
u32 FR_TowerLevel(void *setup, u32 mode) {
    void *party;
    u32 n, i, lv, best = 0;
    if ((mode & 0xff) != TOWER_MODE_OPEN) return 50 + 10 * (mode & 0xff);
    party = *(void **)((u8 *)setup + BTLSETUP_PARTY0);
    n = PokeParty_GetPkmCount(party);
    for (i = 0; i < n; i++) {
        void *pkm = PokeParty_GetPkm(party, i);
        if (PokeParty_GetParam(pkm, PKM_PARAM_IS_EGG, 0)) continue;
        lv = PokeParty_GetParam(pkm, PKM_PARAM_LEVEL, 0);
        if (lv > best) best = lv;
    }
    return best < FRONTIER_MIN_LEVEL_OPEN ? FRONTIER_MIN_LEVEL_OPEN : best;
}
/* called from BtlSetup_SetTrialHouseParty (ov012 0x02161fac) in place of battle_tower.py's level helper, with its
 * contract: r5 = the setup, r7 = the play mode; returns r0 = heap 4, r2 = the level; r1, r3 are set again after */
__attribute__((naked)) void FR_TowerLevelShim(void) {
    __asm__ volatile("push {r4, lr}\n"
                     "adds r0, r5, #0\n"
                     "adds r1, r7, #0\n"
                     "bl FR_TowerLevel\n"
                     "adds r2, r0, #0\n"
                     "movs r0, #4\n"
                     "pop {r4, pc}\n");
}

u32 FR_CmdGet(void *vm, void *env) {
    u32 key = ScriptReadAny(vm, env) & 0xffff;
    u16 *var = ScriptReadVar(vm, env);
    void *gd = FieldScriptEnv_GetGameData(env);
    u16 *rec = records(gd);
    u32 arg = key & 0xff, side = (arg >> 4) & 1, sel = arg & 15, v = 0;
    switch (key >> 8) {
    case 0x0: if (arg < N_KEYS) v = rec[arg]; break;
    case 0x1: v = BP_Get(GetBSubwayScore(gd)); break;
    case 0x2: v = rec[streak_key(rec, arg)]; break;
    case 0x3: v = rec[streak_key(rec, arg) + 1]; break;
    case 0x4: v = (rec[K_SYMBOLS] >> (2 * (arg & 7))) & 3; v = v & 2 ? 2 : v; break;
    case 0x5: v = sel < 10 ? kTutorCost[side][sel] : 0; break;
    case 0x6: v = sel < 10 ? kTutorId[side][sel] : 0; break;
    case 0x7: v = sel < 10 ? kTutorMove[side][sel] : 0; break;
    case 0x8: v = eligible(gd, (arg & 1) == 0); break;
    case 0x9: v = arg < 3 ? (rec[K_PARTY] >> (4 * arg)) & 15 : 0; v = v ? v - 1 : 255; break;
    case 0xA: v = banned_names(env, gd, arg & 15); break;
    }
    *var = (u16)v;
    return 0;
}

u32 FR_BPWin(void *env);

u32 FR_CmdOp(void *vm, void *env) {
    u32 op = ScriptReadAny(vm, env) & 0xffff;
    u16 *var = ScriptReadVar(vm, env);
    void *gd = FieldScriptEnv_GetGameData(env);
    u16 *rec = records(gd);
    u32 arg = op & 0xff, k, v, bp;
    switch (op >> 8) {
    case 0x1:                                           /* set a key */
        if (arg < N_KEYS) rec[arg] = *var;
        break;
    case 0x2:                                           /* BP += var; var = the BP now */
        add_bp(gd, *var);
        *var = BP_Get(GetBSubwayScore(gd));
        break;
    case 0x3:                                           /* take var BP if there are enough: var = 1, else 0 */
        bp = BP_Get(GetBSubwayScore(gd));
        if (bp >= *var) { BP_Take(GetBSubwayScore(gd), *var); *var = 1; } else *var = 0;
        break;
    case 0x4:                                           /* a win: the current streak + 1, the best = max */
        k = streak_key(rec, arg);
        if (rec[k] < STREAK_MAX) rec[k]++;
        if (rec[k + 1] < rec[k]) rec[k + 1] = rec[k];
        *var = rec[k];
        break;
    case 0x5:                                           /* the current streak ends */
        rec[streak_key(rec, arg)] = 0;
        break;
    case 0x6:                                           /* GiveBattlePoints from the records (arg = brain) */
    case 0xC:                                           /* the same with var = the streak */
        v = (op >> 8) == 0x6 ? rec[streak_key(rec, rec[K_FACILITY] | (rec[K_BATTLE_MODE] & 1) << 3)] : *var;
        v = award(rec, v, arg & 1);
        add_bp(gd, v);
        rec[K_LAST_BP] = (u16)v;
        *var = (u16)v;
        break;
    case 0x7:                                           /* a symbol: arg = f << 1 | gold */
        k = 2 * ((arg >> 1) & 7);
        rec[K_SYMBOLS] |= (u16)((arg & 1 ? 2 : 1) << k);
        break;
    case 0x8:                                           /* the picks (var+1 .. var+3, 255 = none) -> FR_PARTY */
        v = 0;
        for (k = 0; k < 3; k++)
            if (var[1 + k] < 6) v |= (u32)(var[1 + k] + 1) << (4 * k);
        rec[K_PARTY] = (u16)v;
        break;
    case 0x9:                                           /* soft reset (as Black 2's Battle Subway: sys_reset) */
        sys_reset(0);
        break;
    case 0xA:                                           /* the BP window (top right, as the money window) */
        FR_BPWin(env);
        break;
    case 0xB:                                           /* key += var; var = the new value */
        if (arg < N_KEYS) { rec[arg] = (u16)(rec[arg] + *var); *var = rec[arg]; }
        break;
    }
    return 0;
}

/* Black 2's money window (s0040_MoneyWinDisp 31, 1) showing the BP: the shop screen's own "N BP" line (script
 * text 613, FR_BPWIN_LINE: "{0205:0} BP"). Closed by MoneyWinClose (command 65), as the money window. */
u32 FR_BPWin(void *env) {
    void *gsys = FieldScriptEnv_GetGameSystem(env);
    void *gd = FieldScriptEnv_GetGameData(env);
    void *field = GSYS_GetField(gsys);
    void *bg = Field_GetMsgBGSys(field);
    void *old = Field_GetMoneyWin(field);
    void *sw = FieldScriptEnv_GetScriptWork(env);
    void *wordset = ScriptWork_GetWordSet(sw);
    void *tmpl = ScriptWork_GetAltStrBuf(sw);
    u32 heap = Field_GetHeapID(field);
    void *msg = GFL_MsgSysLoadData(0, 3, FR_BPWIN_FILE, heap);
    void *out = GFL_StrBufCreate(128, heap);
    void *win;
    u32 bp = BP_Get(GetBSubwayScore(gd));
    if (old) MoneyWin_Delete(old);
    win = FieldMsgBG_CreateMoneyWin(bg, msg, 31 - 9, 1, 9, 2);
    Field_SetMoneyWin(field, win);
    WordSetNumber(wordset, 0, bp, 4, 1, 1);
    GFL_MsgDataLoadStrbuf(msg, FR_BPWIN_LINE, tmpl);
    GFL_WordSetFormatStrbuf(wordset, out, tmpl);
    MoneyWin_Print(win, 0, 0, out);
    GFL_StrBufFree(out);
    GFL_MsgDataFree(msg);
    return 0;
}

/* ShopUI_Init's call of ShopUI_LoadMsgData (ov036 0x021abf68; it returns the shop id the switch then reads): the
 * Emerald shop ids get Emerald's list in Black 2's BP list 0 and go on as shop 254 (the BP shop: BP shown, BP paid);
 * every other shop finds Black 2's own list 0 back first. */
u32 FR_ShopMsgData(void *ui, u32 id) {
    u32 r = ShopUI_LoadMsgData(ui, id), i;
    BP_SHOP_ITEMS[0] = B2_BP_LIST0;
    BP_SHOP_ITEM_COUNTS[0] = B2_BP_COUNT0;
    for (i = 0; i < N_SHOPS; i++)
        if ((r & 0xffff) == kShopIds[i]) {
            BP_SHOP_ITEMS[0] = (u32)kShopItems[i];
            BP_SHOP_ITEM_COUNTS[0] = kShopCount[i];
            return SHOP_BP_ITEMS;
        }
    return r;
}

/* the play block's initializer (new game): all 252 bytes (Black 2's func_0200e0f4 clears 60) */
void FR_PlayInit(void *block) {
    u32 *p = block, i;
    for (i = 0; i < PLAY_SIZE / 4; i++) p[i] = 0;
}
