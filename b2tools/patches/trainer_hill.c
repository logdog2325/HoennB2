/* Emerald's Trainer Hill (battle_tents, 2026-10-18; notes/BATTLE_TENTS.md): Pokémon Emerald NDS builds only. Built by
 * b2tools/patches/trainer_hill.py into the Frontier code area (main RAM, frontier_area.py: resident from boot to power
 * off, in battles too), with trainer_hill_data.h (generated from data/emerald/trainer_hill.json: the four base-game
 * modes' 4 x 2 trainers and their Pokémon, the prize lists, the floors' text numbers).
 *
 * pokeemerald src/trainer_hill.c ported:
 *   script command 562 (Black 2's Cmd_0232, unused by every script; args any, var) = `ThHill op, var`: the challenge's
 *     state (TrainerHillStartChallenge, GetOwnerState, GiveChallengePrize, CheckFinalTime, the time and the time board),
 *     a floor's zone init (which of the floor's eight trainer NPCs are shown: this mode's, not yet beaten), the battle's
 *     two trainer slots;
 *   the field's per-step check (ov036 0x021815e6 / 0x02181afe, chained after frontier_pike's and frontier_pyramid's):
 *     a floor's trainers who see the player (Black 2's TrainerEye_LineOfSight / _PathObstacle on the NPC's facing and
 *     sight): one walks up and battles; two at once battle together (a double battle), as Emerald's
 *     CheckForTrainersWantingBattle, when the player has two Pokémon able to battle;
 *   BtlSetup_LoadTrainer's calls (arm9, chained after frontier_pike's / frontier_pyramid's): trainer ids TH_TR_A / TH_TR_B
 *     (534 / 535, Black 2 ids no Hoenn trainer takes, as the Pike's 529-531 and the Pyramid's 532/533) get the Hill
 *     trainer's class, name and three Pokémon (CreateNPCTrainerHillParty: the floor data's sets at the level of the
 *     player's highest Pokémon), no experience (BATTLE_TYPE_TRAINER_HILL), no items;
 *   the battle's trainer lines (chained): a beaten Hill trainer says its speechLose.
 * The time: Black 2's play time (GameData's live copy, counted in battles and menus as Emerald's VBlank counter, and kept
 * across a save and a reset): whole seconds, so the hundredths always show 00.
 * State: frontier_core's record keys (notes/FRONTIER.md 6): 60 the flags, 61-62 the timer, 63/68/69 the four best times. */
typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef signed short s16;
typedef int s32;

#define FN(type, addr) ((type)((addr) | 1))
#define ScriptReadVar              FN(u16 *(*)(void *, void *), 0x021548e8)
#define ScriptReadAny              FN(u32 (*)(void *, void *), 0x02154910)
#define FieldScriptEnv_GetGameData FN(void *(*)(void *), 0x02155174)
#define FieldScriptEnv_GetScriptWork FN(void *(*)(void *), 0x02155184)
#define ScriptWork_GetWordSet      FN(void *(*)(void *), 0x02153ec4)
#define WordSet_LoadStrbuf         FN(void (*)(void *, u32, void *, u32, u32, u32), 0x0202437c)
#define GameData_GetParty          FN(void *(*)(void *), 0x0201735c)
#define GameData_GetSaveControl    FN(void *(*)(void *), 0x02017934)
#define GameData_GetEventWork      FN(void *(*)(void *), 0x02017394)
#define EventWork_GetWkPtr         FN(u16 *(*)(void *, u32), 0x02019294)
#define EventWork_FlagSet          FN(void (*)(void *, u32), 0x020191d8)
#define EventWork_FlagReset        FN(void (*)(void *, u32), 0x02019200)
#define SaveControl_GetBlockPtr    FN(void *(*)(void *, u32), 0x02007448)
#define GameData_GetPlayerState    FN(void *(*)(void *), 0x020171f4)
#define PlayerState_GetZoneID      FN(u32 (*)(void *), 0x02017544)
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
#define GFL_HeapAllocate           FN(void *(*)(u32, u32, u32, u32, u32), 0x0203a1fc)
#define GFL_HeapFree               FN(void (*)(void *), 0x0203a24c)
#define GFL_StrBufCreate           FN(void *(*)(u32, u32), 0x02048530)
#define GFL_StrBufFree             FN(void (*)(void *), 0x02048564)
#define GFL_StrBufLoadString       FN(void (*)(void *, const u16 *), 0x02048614)
#define GFL_MsgSysLoadData         FN(void *(*)(u32, u32, u32, u32), 0x0204875c)
#define GFL_MsgDataFree            FN(void (*)(void *), 0x020487d4)
#define GFL_MsgDataLoadStrbuf      FN(void (*)(void *, u32, void *), 0x02048838)
#define BtlSetup_SetFlag           FN(void (*)(void *, u32), 0x02017d18)
#define EventScriptCall_Create     FN(void *(*)(void *, u32, void *, u32), 0x0215366c)
#define Field_GetActorSystem       FN(void *(*)(void *), 0x021804b8)
#define Field_GetPlayer            FN(void *(*)(void *), 0x021804f0)
#define Field_GetEncountSystem     FN(void *(*)(void *), 0x02180524)
#define FieldPlayer_GetActor       FN(void *(*)(void *), 0x0219a6a0)
#define FindFieldActor             FN(void *(*)(void *, u32), 0x02167a14)
#define GetActorFaceDir            FN(u32 (*)(void *), 0x02167078)
#define GetActorUserParam          FN(u32 (*)(void *, u32), 0x021670bc)
#define FldAct_GetGPos             FN(void (*)(void *, s16 *), 0x02167294)
#define TrainerEye_LineOfSight     FN(s32 (*)(u32, s32, s16 *, s16 *), 0x021a5fe0)
#define TrainerEye_PathObstacle    FN(u32 (*)(void *, u32, s32, void *), 0x021a6448)
#define g_SaveControl              (*(void **)0x02140f60)

#define P_SPECIES 0x05
#define P_ITEM    0x06
#define P_HAPPY   0x09
#define P_ABILITY 0x0a
#define P_EV_HP   0x0d
#define P_IV_HP   0x46
#define P_IS_EGG  0x4c
#define P_LEVEL   0x9e
#define P_HP      0xa0
#define P_MAXHP   0xa1

#include "trainer_hill_data.h"        /* generated by trainer_hill.py: kHill, kPrize, TH_* numbers, NEXT_* targets */

/* compiler helpers -> Black 2's own ARM division routines (quotient r0, remainder r1) */
typedef unsigned long long u64;      /* (only the helpers' return type) */
u32 __aeabi_uidiv(u32 a, u32 b) { return (u32)((u64 (*)(u32, u32))0x0208d868)(a, b); }
u64 __aeabi_uidivmod(u32 a, u32 b) { return ((u64 (*)(u32, u32))0x0208d868)(a, b); }

/* frontier_core's record keys (u16[] after Black 2's 60 bytes of save block 0x38; notes/FRONTIER.md 2.2) */
#ifndef FR_REC_OFF                     /* HOENN_SAVE_COMPAT=1 (save_compat.py, notes/SAVE_PKHEX.md): 64 */
#define FR_REC_OFF 60
#endif
#define K_FLAGS 60                     /* bits 0-1 the mode, 2 a challenge on (VAR_TRAINER_HILL_IS_ACTIVE), 3 the owner spoken
                                          to (spokeToOwner: the timer stopped), 4 the prize received, 5 the final time
                                          checked, 6 lost (hasLost), 7 saved before the first challenge (savedGame), 8-15
                                          the floors' trainers beaten (trainerFlags: bit 8 + 2 * (floor - 1) + i) */
#define K_TIMER 61                     /* 61-62: the play time (seconds) at the start, or (spoken to the owner) the time */
#define K_BEST0 63                     /* 63, 68, 69: the four modes' best times, 12 bits each (seconds + 1; 0 = none) */
#define K_BEST1 68
#define K_BEST2 69
#define F_ACTIVE 4
#define F_SPOKE 8
#define F_PRIZE 16
#define F_CHECKED 32
#define F_LOST 64
#define F_SAVED 128
#define MAX_SECONDS 3599               /* HILL_MAX_TIME 59:59.99 */

static u16 *rec(void *gd) {
    return (u16 *)((u8 *)SaveControl_GetBlockPtr(gd ? GameData_GetSaveControl(gd) : g_SaveControl, 0x38) + FR_REC_OFF);
}
static u32 mode_of(const u16 *k) { return k[K_FLAGS] & 3; }
static u32 beaten(const u16 *k, u32 floor, u32 i) { return (k[K_FLAGS] >> (8 + 2 * (floor - 1) + i)) & 1; }
#define GD_PLAY_TIME 0x2f0                 /* GameData: the live PlayTime (the save block's copy, SaveControl_GetPlayTime,
                                              is only written when the game saves: GameData_SaveBackup; tested 2026-10-18) */
static u32 play_seconds(void *gd) {
    u8 *pt = *(u8 **)((u8 *)gd + GD_PLAY_TIME);
    return (u32)*(u16 *)pt * 3600 + pt[2] * 60 + pt[3];
}
static u32 timer_get(void *gd) {                     /* the challenge's time in seconds (capped at 59:59) */
    u16 *k = rec(gd);
    u32 v = k[K_TIMER] | (u32)k[K_TIMER + 1] << 16, t;
    if (k[K_FLAGS] & F_SPOKE) t = v;
    else { u32 now = play_seconds(gd); t = now >= v ? now - v : 0; }
    return t > MAX_SECONDS ? MAX_SECONDS : t;
}
static void timer_set(u16 *k, u32 v) { k[K_TIMER] = (u16)v; k[K_TIMER + 1] = (u16)(v >> 16); }
static u16 *best_word(u16 *k, u32 bit) { return &k[bit < 16 ? K_BEST0 : bit < 32 ? K_BEST1 : K_BEST2]; }
static u32 best_get(u16 *k, u32 m) {                 /* seconds + 1, 0 none (bits 12m .. 12m + 11 of keys 63, 68, 69) */
    u32 i, v = 0;
    for (i = 0; i < 12; i++) { u32 b = 12 * m + i; v |= (u32)((*best_word(k, b) >> (b & 15)) & 1) << i; }
    return v;
}
static void best_set(u16 *k, u32 m, u32 s1) {
    u32 i;
    for (i = 0; i < 12; i++) {
        u32 b = 12 * m + i;
        u16 *w = best_word(k, b);
        *w = (u16)((*w & ~(1u << (b & 15))) | ((s1 >> i) & 1) << (b & 15));
    }
}
static u16 *work(void *gd, u32 id) { return EventWork_GetWkPtr(GameData_GetEventWork(gd), id); }

/* the battle's two trainer slots: which floor trainer each one is (uid 1-8; 0 none) and the floor (set at its zone init) */
static u8 g_floor, g_slot[2];

/* "12 min. 5.00 sec." pieces: Emerald's ConvertIntToDecimalStringN(.., STR_CONV_MODE_RIGHT_ALIGN, 2) pads with spaces */
static void word_str(void *env, u32 slot, const u16 *s) {
    void *sb = GFL_StrBufCreate(32, 0x8004);
    GFL_StrBufLoadString(sb, s);
    WordSet_LoadStrbuf(ScriptWork_GetWordSet(FieldScriptEnv_GetScriptWork(env)), slot, sb, 0, 1, 2);
    GFL_StrBufFree(sb);
}
static void two(u16 *o, u32 v, u32 zero) { o[0] = v >= 10 ? '0' + v / 10 : (zero ? '0' : ' '); o[1] = '0' + v % 10; o[2] = 0xFFFF; }
static void time_words(void *env, u32 slot, u32 secs) {   /* words slot, slot+1, slot+2: minutes, seconds, hundredths */
    u16 s[4];
    two(s, secs / 60, 0); word_str(env, slot, s);
    two(s, secs % 60, 0); word_str(env, slot + 1, s);
    two(s, secs >= MAX_SECONDS ? 99 : 0, 1); word_str(env, slot + 2, s);   /* (HILL_MAX_TIME shows 59:59.99) */
}

/* ---- the challenge ------------------------------------------------------------------------------------------- */
static u32 able_count(void *gd) {
    void *party = GameData_GetParty(gd);
    u32 i, n = 0;
    for (i = 0; i < PokeParty_GetPkmCount(party); i++) {
        void *p = PokeParty_GetPkm(party, i);
        if (!PokeParty_GetParam(p, P_IS_EGG, 0) && PokeParty_GetParam(p, P_HP, 0)) n++;
    }
    return n;
}
static void floor_init(void *gd, u32 floor) {        /* the eight trainer NPCs (uid u = 1 + 2 * mode + i): map-local
                                                        flag 0x20 + u hides another mode's (LoadTrainerHillObjectEvent-
                                                        Templates: this mode's two stand there, beaten or not) */
    u16 *k = rec(gd);
    void *ew = GameData_GetEventWork(gd);
    u32 u, m = mode_of(k), on = k[K_FLAGS] & F_ACTIVE;
    g_floor = (u8)floor;
    for (u = 1; u <= 8; u++) {
        if (!on || (u - 1) >> 1 != m) EventWork_FlagSet(ew, TH_HIDE_FLAG + u);
        else EventWork_FlagReset(ew, TH_HIDE_FLAG + u);
    }
}
static u32 prize_item(void *gd) {                    /* GetPrizeItemId: the mode's list (TH data), by the minutes */
    u32 mins = timer_get(gd) / 60, id;
    id = mins < 12 ? 0 : mins < 13 ? 1 : mins < 14 ? 2 : mins < 16 ? 3 : mins < 18 ? 4 : 5;
    return kPrize[mode_of(rec(gd))][id];
}
static const HillTr *trainer_of(void *gd, u32 uid) {
    u32 m = (uid - 1) >> 1, i = (uid - 1) & 1;
    (void)gd;
    if (!uid || uid > 8 || !g_floor) return 0;
    return &kHill[m][g_floor - 1][i];
}
static u32 line_of(u32 uid, u32 kind) { return TH_LINE_BASE + 5 * (uid - 1) + kind; }   /* in the floor's text */
static void sync_floor(void *gd) {                   /* g_floor from the player's zone (it is .bss: a Continue on a
                                                        floor, before any zone init or step, finds it 0) */
    u32 zone = PlayerState_GetZoneID(GameData_GetPlayerState(gd));
    if (zone >= TH_ZONE_1F && zone <= TH_ZONE_1F + 3) g_floor = (u8)(zone - TH_ZONE_1F + 1);
}

/* ---- script command 562: ThHill op, var (op = code << 8 | argument) -------------------------------------------- */
enum { TH_START = 1, TH_FLOOR_INIT, TH_FLAGS, TH_FLAG_SET, TH_FLAG_CLEAR, TH_BATTLE, TH_LINE, TH_WON, TH_BEATEN,
       TH_LOST, TH_OWNER, TH_PRIZE, TH_FINAL_TIME, TH_TIME_WORDS, TH_BOARD_WORDS, TH_LEAVE };
u32 TH_Cmd(void *vm, void *env) {
    u32 op = ScriptReadAny(vm, env) & 0xFFFF;
    u16 *var = ScriptReadVar(vm, env);
    void *gd = FieldScriptEnv_GetGameData(env);
    u16 *k = rec(gd);
    u32 a = op & 0xFF, i;
    sync_floor(gd);
    switch (op >> 8) {
    case TH_START:                                   /* TrainerHillSetMode (var = the mode 0-3) + StartChallenge */
        k[K_FLAGS] = (u16)((k[K_FLAGS] & F_SAVED) | (*var & 3) | F_ACTIVE);
        timer_set(k, play_seconds(gd));
        return 0;
    case TH_FLOOR_INIT: floor_init(gd, a); *var = (u16)mode_of(k); return 0;
    case TH_FLAGS: *var = k[K_FLAGS]; return 0;
    case TH_FLAG_SET: k[K_FLAGS] |= (u16)(1 << a); return 0;
    case TH_FLAG_CLEAR: k[K_FLAGS] &= (u16)~(1 << a); return 0;
    case TH_BATTLE: g_slot[0] = (u8)*work(gd, TH_W_A); g_slot[1] = (u8)*work(gd, TH_W_B); return 0;   /* uid A, B (0 none) */
    case TH_LINE: *var = (u16)line_of(*var, a); return 0;                                  /* var = uid; a = 1 before, 3 lose, 4 after */
    case TH_WON:                                     /* SetHillTrainerFlag (the one or two just beaten: works A, B) */
        for (i = 0; i < 2; i++) {
            u32 u = *work(gd, i ? TH_W_B : TH_W_A);
            if (u && g_floor) k[K_FLAGS] |= (u16)(1 << (8 + 2 * (g_floor - 1) + ((u - 1) & 1)));
        }
        return 0;
    case TH_BEATEN: { u32 u = a ? a : *var;          /* the floor trainer uid (the argument, else var) beaten */
        *var = g_floor && u ? (u16)beaten(k, g_floor, (u - 1) & 1) : 1; return 0; }
    case TH_LOST: k[K_FLAGS] |= F_LOST | 0xFF00; return 0;   /* TrainerHillSetPlayerLost + SetAllTrainerFlags */
    case TH_OWNER: {                                 /* trainerhill_settrainerflags + GetOwnerState: the timer stops at
                                                        the first talk */
        u32 r = 0;
        k[K_FLAGS] |= 0xFF00;
        if (k[K_FLAGS] & F_SPOKE) r++;
        if ((k[K_FLAGS] & F_PRIZE) && (k[K_FLAGS] & F_CHECKED)) r++;
        if (!(k[K_FLAGS] & F_SPOKE)) { timer_set(k, timer_get(gd)); k[K_FLAGS] |= F_SPOKE; }
        *var = (u16)r;
        return 0;
    }
    case TH_PRIZE: *var = (k[K_FLAGS] & F_PRIZE) ? 0 : (u16)prize_item(gd); return 0;    /* (the script gives it) */
    case TH_FINAL_TIME: {                            /* CheckFinalTime: 0 a new record, 1 not, 2 checked already */
        u32 m = mode_of(k), t = timer_get(gd), b = best_get(k, m);
        if (k[K_FLAGS] & F_CHECKED) *var = 2;
        else if (!b || b - 1 > t) { best_set(k, m, t + 1); *var = 0; }
        else *var = 1;
        k[K_FLAGS] |= F_CHECKED;
        return 0;
    }
    case TH_TIME_WORDS: time_words(env, a, timer_get(gd)); return 0;                       /* BufferChallengeTime */
    case TH_BOARD_WORDS:                             /* PrintOnTrainerHillRecordsWindow: words a + 3 m .. a + 3 m + 2 */
        for (i = 0; i < 4; i++) { u32 b = best_get(k, i); time_words(env, a + 3 * i, b ? b - 1 : MAX_SECONDS); }
        return 0;
    case TH_LEAVE: k[K_FLAGS] &= (u16)~(F_ACTIVE | F_LOST); return 0;                      /* Route 111: IS_ACTIVE 0 */
    }
    return 0;
}

/* ---- the field's per-step check: a floor's trainers who see the player ------------------------------------------ */
void *TH_Step(u8 *ctx, void *a1, void *field) {
    void *gd = *(void **)(ctx + 8), *gsys = *(void **)(ctx + 4), *asys, *enc, *player, *act[2] = {0, 0};
    u16 *k = rec(gd), zone = *(u16 *)(ctx + 16);
    s16 pp[3];
    s32 dist[2];
    u32 dir[2], uid[2], n = 0, i, m, floor;
    if ((ctx[60] & 0x10) && (k[K_FLAGS] & F_ACTIVE) && (zone < TH_ZONE_FIRST || zone > TH_ZONE_LAST))
        k[K_FLAGS] &= (u16)~(F_ACTIVE | F_LOST);     /* out of the building (Route111_OnTransition: IS_ACTIVE 0) */
    if (zone < TH_ZONE_1F || zone > TH_ZONE_1F + 3 || !(ctx[60] & 0x10) || !(k[K_FLAGS] & F_ACTIVE))
        return FN(void *(*)(void *, void *, void *), NEXT_STEP)(ctx, a1, field);
    floor = zone - TH_ZONE_1F + 1;
    g_floor = (u8)floor;
    m = mode_of(k);
    asys = Field_GetActorSystem(field); enc = Field_GetEncountSystem(field);
    player = FieldPlayer_GetActor(Field_GetPlayer(field));
    FldAct_GetGPos(player, pp);
    for (i = 0; i < 2 && n < 2; i++) {                /* CheckForTrainersWantingBattle: in object order */
        void *a; s16 ap[3]; s32 d; u32 dr, u = 1 + 2 * m + i;
        if (beaten(k, floor, i)) continue;
        a = FindFieldActor(asys, u);
        if (!a) continue;
        dr = GetActorFaceDir(a);
        FldAct_GetGPos(a, ap);
        d = TrainerEye_LineOfSight(dr, (s32)GetActorUserParam(a, 0), ap, pp);
        if (d == -1 || TrainerEye_PathObstacle(a, dr, d, enc)) continue;
        act[n] = a; dist[n] = d; dir[n] = dr; uid[n] = u; n++;
    }
    if (!n) return FN(void *(*)(void *, void *, void *), NEXT_STEP)(ctx, a1, field);
    if (n == 2 && able_count(gd) < 2) n = 1;          /* (one Pokémon able to battle: the first trainer only) */
    *work(gd, TH_W_A) = (u16)uid[0]; *work(gd, TH_W_SA) = (u16)(dist[0] > 0 ? dist[0] - 1 : 0); *work(gd, TH_W_DA) = (u16)dir[0];
    *work(gd, TH_W_B) = (u16)(n == 2 ? uid[1] : 0);
    *work(gd, TH_W_SB) = (u16)(n == 2 && dist[1] > 0 ? dist[1] - 1 : 0); *work(gd, TH_W_DB) = (u16)(n == 2 ? dir[1] : 0);
    return EventScriptCall_Create(gsys, TH_SCR_SPOTTED, act[0], *(u16 *)ctx);
}

/* ---- the battle: the two trainer slots -------------------------------------------------------------------------- */
static u32 highest_level(void *gd) {                 /* GetHighestLevelInPlayerParty */
    void *party = GameData_GetParty(gd);
    u32 i, best = 0;
    for (i = 0; i < PokeParty_GetPkmCount(party); i++) {
        void *p = PokeParty_GetPkm(party, i);
        if (PokeParty_GetParam(p, P_SPECIES, 0) && !PokeParty_GetParam(p, P_IS_EGG, 0) && PokeParty_GetParam(p, P_LEVEL, 0) > best)
            best = PokeParty_GetParam(p, P_LEVEL, 0);
    }
    return best ? best : 1;
}
static u32 hill_slot(u32 id) {                       /* the slot's floor trainer uid, 0 = not ours */
    u16 *k = rec(0);
    if ((id != TH_TR_A && id != TH_TR_B) || !(k[K_FLAGS] & F_ACTIVE) || !g_floor) return 0;
    return g_slot[id == TH_TR_B];
}
void TH_LoadTrainer(void *setup, void *gd, u32 client, void **pparty, u32 id, u32 heap) {
    u32 *tbs, uid, i, j, level;
    const HillTr *t;
    FN(void (*)(void *, void *, u32, void **, u32, u32), NEXT_TRAINER)(setup, gd, client, pparty, id, heap);
    if (!(uid = hill_slot(id)) || !(t = trainer_of(gd, uid))) return;
    tbs = *(u32 **)((u8 *)setup + 72 + 4 * client);
    PokeParty_InitCore(*pparty, 6);
    BtlSetup_SetFlag(setup, 0x200);                  /* no experience (Emerald: BATTLE_TYPE_TRAINER_HILL) */
    ((u16 *)(tbs + 3))[0] = ((u16 *)(tbs + 3))[1] = ((u16 *)(tbs + 3))[2] = ((u16 *)(tbs + 3))[3] = 0;
    tbs[1] = t->cls;
    { void *msg = GFL_MsgSysLoadData(0, 3, kFloorText[g_floor - 1], heap);
      GFL_MsgDataLoadStrbuf(msg, line_of(uid, 0), (void *)tbs[5]);
      GFL_MsgDataFree(msg); }
    level = highest_level(gd);                       /* SetTrainerHillMonLevel */
    for (i = 0; i < 3; i++) {                        /* CreateNPCTrainerHillParty: CreateBattleTowerMon */
        const HillMon *h = &t->mons[i];
        void *pkm = GFL_HeapAllocate(heap, PokeParty_GetPkmRawSize(), 1, 0, 0);
        u32 ivs = 0;
        for (j = 0; j < 6; j++) ivs |= (u32)(h->ivs[j] & 31) << (5 * j);
        PokeParty_CreatePkm(pkm, h->species, level, 0, 0xFFFFFFFF, ivs, h->personality ? h->personality : 0x80, 0);
        PokeParty_SetParam(pkm, P_ITEM, h->item);
        for (j = 0; j < 4; j++) PokeParty_SetMove(pkm, h->moves[j], j);
        PokeParty_SetParam(pkm, P_HAPPY, h->friendship);
        for (j = 0; j < 6; j++) PokeParty_SetParam(pkm, P_EV_HP + j, h->evs[j]);
        if (h->ability) PokeParty_SetParam(pkm, P_ABILITY, h->ability);
        PokeParty_SetNature(pkm, h->nature);
        PokeParty_RecalcStats(pkm);
        PokeParty_SetParam(pkm, P_HP, PokeParty_GetParam(pkm, P_MAXHP, 0));
        PokeParty_AddPkm(*pparty, pkm);
        GFL_HeapFree(pkm);
    }
}
/* the battle's trainer lines (ov167): a Hill trainer beaten says its speechLose; the slots' own lines never show */
u32 TH_MsgExists(u32 id, u32 type, u32 heap) {
    if (hill_slot(id)) return type == 1;
    return FN(u32 (*)(u32, u32, u32), NEXT_MSGEX)(id, type, heap);
}
void TH_MsgLoad(u32 id, u32 type, void *strbuf, u32 heap) {
    u32 uid = hill_slot(id);
    void *msg;
    if (!uid || type != 1) { FN(void (*)(u32, u32, void *, u32), NEXT_MSGLD)(id, type, strbuf, heap); return; }
    msg = GFL_MsgSysLoadData(0, 3, kFloorText[g_floor - 1], heap);
    GFL_MsgDataLoadStrbuf(msg, line_of(uid, 3), strbuf);
    GFL_MsgDataFree(msg);
}
