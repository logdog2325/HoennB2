/* Emerald's Battle Pike (frontier_pike, 2026-10-12): Pokémon Emerald NDS builds only. Compiled twice by
 * b2tools/patches/frontier_pike.py, which also has the findings and the data layout (emerald_itcm, 2026-10-12):
 *   without PK_PART_LINES: everything but the battle's trainer-line hooks, linked into the Frontier code area (main RAM,
 *       b2tools/patches/frontier_area.py: resident from boot);
 *   with PK_PART_LINES: only PK_TrainerMsgExists / PK_TrainerMsgLoad (they run inside the battle), placed in ITCM after
 *       the other ITCM patches. The helpers the other part needs are left out by the compiler (unused statics).
 * notes/FRONTIER_PIKE.md describes the facility; the scripts are src/field_scripts/emerald/0798-0809_*.s.
 *
 *   command 290 (Black 2's BoxAdd, unused by every script): EmPike var, op, a, b     (args var, any, any, any)
 *       the Pike's specials (pokeemerald src/battle_pike.c and the parts of frontier_util.c the Pike uses), op = PK_*
 *       below; var gets the answer.
 * and these hooks:
 *   PK_LoadPlayerParty: BtlSetup_LoadPlayerParty's calls in BtlSetup_SetWildNormal and BtlSetup_LoadTrainerBase: during a
 *       Pike challenge the battle's copy of the party keeps its first three (the challenge's three, put first by
 *       PK_PARTY_ORDER), as Emerald's party holds only them; emerald_mech's EM_PartyCopyBack copies them back.
 *   PK_LoadTrainer: BtlSetup_LoadTrainer's calls in BtlSetup_SetTrainer1v1Single and BtlSetup_SetTrainer1v2: the
 *       Pike's battle slots (trainer ids PK_TR_A/B, PK_TR_LUCY) get the Frontier trainer the room chose (class, name,
 *       no items) and Emerald's party for it (FillTrainerParty: sets drawn from the trainer's list, no species or held
 *       item twice, Lv. 50 sets only at Lv. 50, fixed IVs by trainer, EVs/nature/moves of the set) or Lucy's; no
 *       experience (BtlSetup flag 0x200), as Emerald's Frontier battles.
 *   PK_EncSetupNormal: FieldEncount_SetupNormal's call in EventWildBattleCall_CreateStatic: the wild Pokémon of the wild
 *       room (pending in a map-local work) gets its four Pike moves (TryGenerateBattlePikeWildMon).
 *   PK_CheckEncounter: CheckCallRandomEncounter's two calls (the field's per-step checks): in the wild room during a
 *       challenge, Emerald's step check (encounter rate 10, StandardWildEncounter) starts the room's wild-battle
 *       script instead of a random battle.
 *   PK_TrainerMsgExists / PK_TrainerMsgLoad: the battle's trainer lines (ov167): a beaten Pike trainer says Emerald's
 *       speechLose, Lucy "Urk…" / "Darn!"; the slots' own Black 2 lines (mid-battle ones too) never show.
 */
#ifdef PK_PART_LINES                    /* (the field-time helpers are unused here: the compiler leaves them out) */
#pragma clang diagnostic ignored "-Wunused-function"
#pragma clang diagnostic ignored "-Wunused-const-variable"
#endif
typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef int s32;

#define FN(type, addr) ((type)((addr) | 1))
#define ScriptReadVar              FN(u16 *(*)(void *, void *), 0x021548e8)
#define ScriptReadAny              FN(u32 (*)(void *, void *), 0x02154910)
#define FieldScriptEnv_GetGameData FN(void *(*)(void *), 0x02155174)
#define FieldScriptEnv_GetHeapID   FN(u32 (*)(void *), 0x0215515c)
#define GameData_GetParty          FN(void *(*)(void *), 0x0201735c)
#define GameData_GetSaveControl    FN(void *(*)(void *), 0x02017934)
#define GameData_GetEventWork      FN(void *(*)(void *), 0x02017394)
#define EventWork_GetWkPtr         FN(u16 *(*)(void *, u32), 0x02019294)
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
#define PokeParty_SwapPkms         FN(void (*)(void *, u32, u32, u32), 0x0201ff58)
#define PokeParty_RemovePkm        FN(u32 (*)(void *, u32), 0x0201fda8)
#define GFL_HeapAllocate           FN(void *(*)(u32, u32, u32, u32, u32), 0x0203a1fc)
#define GFL_HeapFree               FN(void (*)(void *), 0x0203a24c)
#define GFL_ArcSysReadRange        FN(void (*)(void *, u32, u32, u32, u32), 0x0204a940)
#define GFL_StrBufLoadString       FN(void (*)(void *, const u16 *), 0x02048614)
#define GFL_RandomLC               FN(u32 (*)(u32), 0x02005748)
#define BtlSetup_LoadPlayerParty   FN(void (*)(void *, void *, u32), 0x02017f14)
#define BtlSetup_LoadTrainer       FN(void (*)(void *, void *, u32, void **, u32, u32), 0x02017e54)
#define BtlSetup_SetFlag           FN(void (*)(void *, u32), 0x02017d18)
#define FieldEncount_SetupNormal   FN(void (*)(void *, void *, void *, u32, void *), 0x021a1bcc)
#define CheckCallRandomEncounter   FN(void *(*)(void *, void *, void *), 0x02182af8)
#define EventScriptCall_Create     FN(void *(*)(void *, u32, u32, u32), 0x0215366c)
#define TrainerMsg_CheckExists     FN(u32 (*)(u32, u32, u32), 0x02030548)
#define TrainerMsg_Load            FN(void (*)(u32, u32, void *, u32), 0x020305d8)
#define GFL_MsgSysLoadData         FN(void *(*)(u32, u32, u32, u32), 0x0204875c)
#define GFL_MsgDataFree            FN(void (*)(void *), 0x020487d4)
#define GFL_MsgDataLoadStrbuf      FN(void (*)(void *, u32, void *), 0x02048838)
#define g_SaveControl              (*(void **)0x02140f60)   /* arm9 g_SaveControlWork: the SaveControl (as GameData +0) */

#define P_SPECIES 0x05
#define P_ITEM    0x06
#define P_HAPPY   0x09
#define P_ABILITY 0x0a
#define P_EV_HP   0x0d
#define P_MOVE1   0x36
#define P_PP1     0x3a
#define P_MAXPP1  0x42
#define P_IS_EGG  0x4c
#define P_STATUS  0x9d
#define P_LEVEL   0x9e
#define P_HP      0xa0
#define P_MAX_HP  0xa1
#define P_TYPE1   0xae
#define P_TYPE2   0xaf

/* Black 2's party status is one value, not Gen 3's bit word (pokebw2 include/constants/battle.h CONDITION_*: the battle
   reads it as an index, src/ov167/btl_pokeparam.c): 1 paralysis, 2 sleep (its turns are drawn in battle), 3 freeze,
   4 burn, 5 poison. Black 2 keeps no bad poison outside battle, so Emerald's toxic is poison here */
#define ST_PARALYSIS 1
#define ST_SLEEP     2
#define ST_FREEZE    3
#define ST_BURN      4
#define ST_TOXIC     5

#define T_POISON 3
#define T_GROUND 4
#define T_STEEL  8
#define T_FIRE   9
#define T_ELECTRIC 12
#define T_ICE    14
#define A_STENCH 1
#define A_LIMBER 7
#define A_STATIC 9
#define A_INSOMNIA 15
#define A_IMMUNITY 17
#define A_INTIMIDATE 22
#define A_ILLUMINATE 35
#define A_MAGMA_ARMOR 40
#define A_WATER_VEIL 41
#define A_KEEN_EYE 51
#define A_VITAL_SPIRIT 72
#define I_CLEANSE_TAG 224
#define MOVE_FRUSTRATION 218

/* the Frontier's records (notes/FRONTIER.md 2.2, frontier_core): u16[96] after Black 2's 60 bytes of save block 0x38 */
#define PLAY_BLOCK 0x38
#define PLAY_B2_SIZE 60
#define K_STATUS 0
#define K_FACILITY 1
#define K_BATTLE_MODE 2
#define K_LVL_MODE 3
#define K_PARTY 4
#define K_BATTLE_NUM 5
#define K_SYMBOLS 6
#define K_LAST_BP 7
#define K_STREAK(l) (16 + 8 * 5 + 2 * (l))      /* fr_streak(PIKE, singles, l); + 1 = fr_best */
#define K_PK_STATE 72                            /* hint index 0-2, hint type 3-6, healing rooms off 7, door 8-9,
                                                    room type 10-13, heard Lucy's speech 14, paused 15 */
#define K_PK_ROOM 73                             /* status kind 0-2, status Pokémon 3, streak active Lv50 4 / Open 5 */
#define K_PK_ITEMS 74                            /* 74-76: the three's held items at entry */
#define K_PK_TOTAL 77                            /* 77/78: challenges completed, Lv. 50 / Open */
#define K_PK_SEEN 91                             /* 91-92: the trainers met in this challenge (a 32-bit filter) */
#define K_PK_TR 93                               /* 93/94: the room's Frontier trainers (the battle's lines need them) */
#define FACILITY_PIKE 5
#define ST_IN_CHALLENGE 99                       /* Emerald's frontier_set FRONTIER_DATA_CHALLENGE_STATUS, 99 */

/* map-local works of the Pike's rooms (0x4000-0x401F are cleared on every map change, saved with the game) */
#define W_TR_A    0x4001
#define W_TR_B    0x4002
#define W_NPC     0x4003
#define W_WILD    0x4004    /* the pending wild Pokémon's slot in its table + 1 (0 = none) */
#define W_WILD_LV 0x4005
#define W_GFX0    0x4020    /* the room's two people (NPC codes 162/163 read their sprite from these) */
#define W_GFX1    0x4021

#define PK_TR_A    529
#define PK_TR_B    530
#define PK_TR_LUCY 531

#define NUM_PIKE_ROOMS 14
enum { R_SINGLE, R_HEAL_FULL, R_NPC, R_STATUS, R_HEAL_PART, R_WILD, R_HARD, R_DOUBLE, R_BRAIN, N_ROOM_TYPES };
enum { H_NOSTALGIA, H_WHISPERING, H_POKEMON, H_PEOPLE, H_BRAIN };
enum { S_FREEZE, S_BURN, S_TOXIC, S_PARALYSIS, S_SLEEP };
static const u8 kRoomHint[N_ROOM_TYPES] = { H_PEOPLE, H_PEOPLE, H_WHISPERING, H_NOSTALGIA, H_NOSTALGIA, H_POKEMON, H_POKEMON,
                                             H_WHISPERING, H_BRAIN };
static const u8 kHealBeforeQueen[6][3] = { {2, 1, 0}, {2, 0, 1}, {1, 2, 0}, {1, 0, 2}, {0, 2, 1}, {0, 1, 2} };
static const u8 kBrainStreak[4] = { 28, 140, 56, 1 };          /* sFrontierBrainStreakAppearances[FRONTIER_FACILITY_PIKE] */
static const u8 kLandRates[12] = { 20, 20, 10, 10, 10, 10, 5, 5, 4, 4, 1, 1 };   /* gWildMonLandRates (Gen 3) */
static const u16 kRangeLo[8] = { 0, 80, 100, 120, 140, 160, 180, 200 }, kRangeHi[8] = { 99, 119, 139, 159, 179, 199, 219, 299 };
static const u16 kHardLo[8] = { 100, 120, 140, 160, 180, 200, 220, 200 }, kHardHi[8] = { 119, 139, 159, 179, 199, 219, 239, 299 };

/* frontier_pike_data.h (frontier_pike.py): PK_ARC, PK_DAT (the data file: a/0/0/8 member), PK_OFF_* (its sections),
 * PK_HIGH_TIER, PK_N_TRAINERS, kWildSpecies[2][4][3] (and the table of the wild room, see blob) */
#include "frontier_pike_data.h"

typedef struct { u16 cls, obj, list_off, list_n, name[8]; } TrainerRec;              /* 24 bytes */
typedef struct { u16 species, moves[4], item; u8 nature, ev; u16 pad; } SetRec;        /* 16 bytes */
typedef struct { u16 species, item; u8 iv, nature, evs[6]; u16 moves[4], pad[2]; } BrainRec;  /* 24 bytes */
typedef struct { u16 species; u8 delta, pad; u16 moves[4]; } WildRec;                  /* 12 bytes */
typedef struct { u16 obj; u8 speech[3], pad; } NpcRec;                                 /* 6 bytes */

static void rd(void *dst, u32 off, u32 size) { GFL_ArcSysReadRange(dst, PK_ARC, PK_DAT, off, size); }
static u32 rnd(u32 n) { return GFL_RandomLC(n); }
static u32 udiv(u32 a, u32 b) { return ((u32 (*)(u32, u32))0x0208d868)(a, b); }   /* arm9 __aeabi_uidivmod (ARM) */
static u32 umod(u32 a, u32 b) { return a - udiv(a, b) * b; }
static u16 *rec(void *gd) {
    return (u16 *)((u8 *)SaveControl_GetBlockPtr(GameData_GetSaveControl(gd), PLAY_BLOCK) + PLAY_B2_SIZE);
}
#ifdef PK_PART_LINES                    /* (the battle has no GameData at hand: the global SaveControl) */
static u16 *rec_g(void) { return (u16 *)((u8 *)SaveControl_GetBlockPtr(g_SaveControl, PLAY_BLOCK) + PLAY_B2_SIZE); }
#endif
static u16 *wk(void *gd, u32 id) { return EventWork_GetWkPtr(GameData_GetEventWork(gd), id); }
static u32 bits(u32 v, u32 at, u32 n) { return (v >> at) & ((1u << n) - 1); }
static void setbits(u16 *p, u32 at, u32 n, u32 v) { u32 m = ((1u << n) - 1) << at; *p = (u16)((*p & ~m) | ((v << at) & m)); }
static u32 lvl(u16 *r) { return r[K_LVL_MODE] & 1; }
static u16 *streak(u16 *r) { return &r[K_STREAK(lvl(r))]; }
static u32 in_challenge(void *gd) { u16 *r = rec(gd); return r[K_FACILITY] == FACILITY_PIKE && r[K_STATUS] == ST_IN_CHALLENGE; }
static u32 pget(void *pkm, u32 p) { return PokeParty_GetParam(pkm, p, 0); }

/* the challenge's three (the first three party slots during a challenge) */
static u32 n3(void *party) { u32 n = PokeParty_GetPkmCount(party); return n < 3 ? n : 3; }
static u32 alive(void *pkm) { return pget(pkm, P_SPECIES) && !pget(pkm, P_IS_EGG) && pget(pkm, P_HP); }

static u32 can_be_healed(void *pkm) {
    u32 j;
    if (pget(pkm, P_HP) < pget(pkm, P_MAX_HP) || pget(pkm, P_STATUS)) return 1;
    for (j = 0; j < 4; j++)
        if (pget(pkm, P_MOVE1 + j) && pget(pkm, P_PP1 + j) < pget(pkm, P_MAXPP1 + j)) return 1;
    return 0;
}
static void heal_mon(void *pkm) {                                 /* battle_pike.c HealMon */
    u32 j;
    PokeParty_SetParam(pkm, P_HP, pget(pkm, P_MAX_HP));
    for (j = 0; j < 4; j++) PokeParty_SetParam(pkm, P_PP1 + j, pget(pkm, P_MAXPP1 + j));
    PokeParty_SetParam(pkm, P_STATUS, 0);
}
static void shuffle3(u8 *idx) {                                   /* 10 random swaps, as Emerald */
    u32 k, i, j; u8 t;
    for (i = 0; i < 3; i++) idx[i] = (u8)i;
    for (k = 0; k < 10; k++) { i = rnd(3); j = rnd(3); t = idx[i]; idx[i] = idx[j]; idx[j] = t; }
}
static void try_heal(void *party, u32 count) {                    /* TryHealMons */
    u8 idx[3]; u32 i;
    if (!count) return;
    shuffle3(idx);
    for (i = 0; i < 3 && i < n3(party); i++) {
        void *pkm = PokeParty_GetPkm(party, idx[i]);
        if (idx[i] >= n3(party)) continue;
        if (can_be_healed(pkm)) { heal_mon(pkm); if (--count == 0) break; }
    }
}
static u32 count_for_room(u16 *r, u32 nine) {                      /* 1 / 2 / 3 Pokémon by room number */
    u32 b = r[K_BATTLE_NUM];
    return b <= 4 ? 1 : b <= nine ? 2 : 3;
}
static u32 at_least_one_healthy(void *gd) {                        /* AtLeastOneHealthyMon */
    void *party = GameData_GetParty(gd); u16 *r = rec(gd);
    u32 i, n = 0, count = count_for_room(r, 9);
    for (i = 0; i < n3(party); i++) {
        void *pkm = PokeParty_GetPkm(party, i);
        if (!pget(pkm, P_STATUS) && pget(pkm, P_HP)) n++;
        if (n == count) break;
    }
    return n != 0;
}
static u32 at_least_two_alive(void *gd) {                          /* AtLeastTwoAliveMons */
    void *party = GameData_GetParty(gd); u32 i, dead = 0;
    for (i = 0; i < 3; i++) if (i >= n3(party) || !pget(PokeParty_GetPkm(party, i), P_HP)) dead++;
    return dead < 2;
}
static u32 type_prevents(void *pkm, u32 st) {                      /* DoesTypePreventStatus */
    u32 t1 = pget(pkm, P_TYPE1), t2 = pget(pkm, P_TYPE2);
#define HAS(t) (t1 == (t) || t2 == (t))
    switch (st) {
    case ST_TOXIC: return HAS(T_STEEL) || HAS(T_POISON);
    case ST_FREEZE: return HAS(T_ICE);
    case ST_PARALYSIS: return HAS(T_GROUND) || HAS(T_ELECTRIC);
    case ST_BURN: return HAS(T_FIRE);
    }
    return 0;
#undef HAS
}
static u32 ability_prevents(void *pkm, u32 st) {                   /* DoesAbilityPreventStatus */
    u32 a = pget(pkm, P_ABILITY);
    switch (st) {
    case ST_FREEZE: return a == A_MAGMA_ARMOR;
    case ST_BURN: return a == A_WATER_VEIL;
    case ST_PARALYSIS: return a == A_LIMBER;
    case ST_SLEEP: return a == A_INSOMNIA || a == A_VITAL_SPIRIT;
    case ST_TOXIC: return a == A_IMMUNITY;
    }
    return 0;
}
static u32 kind_of(u32 st) {
    switch (st) { case ST_FREEZE: return S_FREEZE; case ST_BURN: return S_BURN; case ST_PARALYSIS: return S_PARALYSIS;
                  case ST_SLEEP: return S_SLEEP; default: return S_TOXIC; }
}
static u32 inflict_status(void *gd) {                              /* TryInflictRandomStatus */
    void *party = GameData_GetParty(gd); u16 *r = rec(gd);
    u8 idx[3]; u32 count = count_for_room(r, 9), status = 0, st = 0, chosen, i, j, mon;
    shuffle3(idx);
    do {
        u32 x = rnd(100);
        chosen = 0;
        st = x < 35 ? ST_TOXIC : x < 60 ? ST_FREEZE : x < 80 ? ST_PARALYSIS : x < 90 ? ST_SLEEP : ST_BURN;
        if (status != st) {
            status = st;
            for (i = 0, j = 0; i < 3; i++) {
                void *pkm;
                if (idx[i] >= n3(party)) continue;
                pkm = PokeParty_GetPkm(party, idx[i]);
                if (!pget(pkm, P_STATUS) && pget(pkm, P_HP)) {
                    j++;
                    if (!type_prevents(pkm, st)) { chosen = 1; break; }
                }
                if (j == count) break;
            }
            if (j == 0) return 0;
        }
    } while (!chosen);
    mon = st == ST_FREEZE ? 1 : st == ST_BURN ? rnd(2) != 0 : 0;   /* 1 = Dusclops, 0 = Kirlia */
    setbits(&r[K_PK_ROOM], 0, 3, kind_of(st));
    setbits(&r[K_PK_ROOM], 3, 1, mon);
    for (i = 0, j = 0; i < 3; i++) {
        void *pkm;
        if (idx[i] >= n3(party)) continue;
        pkm = PokeParty_GetPkm(party, idx[i]);
        if (!pget(pkm, P_STATUS) && pget(pkm, P_HP)) {
            j++;
            if (!ability_prevents(pkm, st) && !type_prevents(pkm, st)) PokeParty_SetParam(pkm, P_STATUS, st);
        }
        if (j == count) break;
    }
    return 1;
}

static u32 symbols(u16 *r) { u32 s = (r[K_SYMBOLS] >> (2 * FACILITY_PIKE)) & 3; return (s & 1) + ((s >> 1) & 1); }

static u32 queen_fight_type(u16 *r, u32 next) {                    /* GetPikeQueenFightType */
    u32 w = *streak(r) + next, n = symbols(r);
    if (n < 2) return w == (u32)(kBrainStreak[n] - kBrainStreak[3]) ? n + 1 : 0;
    if (w == (u32)(kBrainStreak[0] - kBrainStreak[3])) return 3;
    if (w == (u32)(kBrainStreak[1] - kBrainStreak[3]) ||
        (w > kBrainStreak[1] && umod(w - kBrainStreak[1] + kBrainStreak[3], kBrainStreak[2]) == 0)) return 4;
    return 0;
}

static void set_hint_room(void *gd, u16 *var) {                    /* SetHintedRoom */
    u16 *r = rec(gd); u8 cand[8]; u32 i, id, count, type;
    *var = 0;
    if (queen_fight_type(r, 1)) {
        *var = 1;
        setbits(&r[K_PK_STATE], 0, 3, rnd(6));
        setbits(&r[K_PK_STATE], 3, 4, R_BRAIN);
        return;
    }
    setbits(&r[K_PK_STATE], 0, 3, rnd(3));
    count = bits(r[K_PK_STATE], 7, 1) ? N_ROOM_TYPES - 3 : N_ROOM_TYPES - 1;
    for (i = 0; i < 8; i++) cand[i] = 0;                                   /* AllocZeroed */
    for (i = 0, id = 0; i < count; i++) {                                  /* (Emerald's own loop: with the healing */
        if (bits(r[K_PK_STATE], 7, 1)) { if (i != R_HEAL_FULL && i != R_HEAL_PART) cand[id++] = (u8)i; }   /* rooms off */
        else cand[i] = (u8)i;                                              /* it never offers 6 and 7, and the two */
    }                                                                      /* unfilled slots stay 0 = single battle) */
    type = cand[rnd(count)];
    if (type == R_STATUS && !at_least_one_healthy(gd)) type = R_NPC;
    if (type == R_DOUBLE && !at_least_two_alive(gd)) type = R_NPC;
    setbits(&r[K_PK_STATE], 3, 4, type);
}

static u32 next_room_type(void *gd, u32 door) {                    /* GetNextRoomType */
    u16 *r = rec(gd); u8 off[8], cand[8]; u32 i, n = 8, id = 0, hint, type, htype = bits(r[K_PK_STATE], 3, 4);
    if (htype == R_BRAIN) return R_BRAIN;
    if (door == bits(r[K_PK_STATE], 0, 3)) {
        if (htype == R_STATUS) inflict_status(gd);
        return htype;
    }
    for (i = 0; i < 8; i++) off[i] = 0;
    hint = kRoomHint[htype];
    for (i = 0; i < 8; i++) if (kRoomHint[i] == hint) { off[i] = 1; n--; }
    if (!off[R_DOUBLE] && !at_least_two_alive(gd)) { off[R_DOUBLE] = 1; n--; }
    if (!off[R_STATUS] && !at_least_one_healthy(gd)) { off[R_STATUS] = 1; n--; }
    if (bits(r[K_PK_STATE], 7, 1)) {
        if (!off[R_HEAL_FULL]) { off[R_HEAL_FULL] = 1; n--; }
        if (!off[R_HEAL_PART]) { off[R_HEAL_PART] = 1; n--; }
    }
    for (i = 0; i < 8; i++) if (!off[i]) cand[id++] = (u8)i;
    type = cand[rnd(n)];
    if (type == R_STATUS) inflict_status(gd);
    return type;
}

/* trainers met this challenge: a 32-bit filter in two record keys (a trainer is never met twice in a challenge, as
 * Emerald's trainerIds[]; a false match only means another trainer is drawn) */
static u32 seen_bits(u32 t) { return (1u << ((t * 37) & 31)) | (1u << ((t * 13 + 7) & 31)); }
static u32 seen(u16 *r, u32 t) { u32 f = r[K_PK_SEEN] | (u32)r[K_PK_SEEN + 1] << 16, b = seen_bits(t); return (f & b) == b; }
static void mark_seen(u16 *r, u32 t) { u32 f = (r[K_PK_SEEN] | (u32)r[K_PK_SEEN + 1] << 16) | seen_bits(t);
                                       r[K_PK_SEEN] = (u16)f; r[K_PK_SEEN + 1] = (u16)(f >> 16); }

static u32 random_trainer(u16 *r, u32 hard) {                      /* GetRandomScaledFrontierTrainerId + no repeats */
    u32 c = udiv(*streak(r), NUM_PIKE_ROOMS), t, tries = 0;
    do {
        if (c > 7) t = kRangeLo[7] + rnd(kRangeHi[7] - kRangeLo[7] + 1);
        else if (hard) t = kHardLo[c] + rnd(kHardHi[c] - kHardLo[c] + 1);
        else t = kRangeLo[c] + rnd(kRangeHi[c] - kRangeLo[c] + 1);
    } while (seen(r, t) && ++tries < 200);
    mark_seen(r, t);
    return t;
}

static u32 trainer_obj(u32 t) { TrainerRec tr; rd(&tr, PK_OFF_TRAINERS + 24 * t, sizeof tr); return tr.obj; }

static void setup_room(void *gd, u16 *var) {                       /* SetupRoomObjectEvents (+ BufferNPC's choice) */
    u16 *r = rec(gd); u32 type = bits(r[K_PK_STATE], 10, 4);
    *wk(gd, W_GFX0) = PK_OBJ_ATTENDANT; *wk(gd, W_GFX1) = PK_OBJ_DUSCLOPS;
    switch (type) {
    case R_SINGLE: *wk(gd, W_TR_A) = (u16)random_trainer(r, 0); *wk(gd, W_GFX0) = (u16)trainer_obj(*wk(gd, W_TR_A)); break;
    case R_HEAL_FULL: break;
    case R_NPC: { NpcRec np; u32 id = rnd(PK_N_NPCS); rd(&np, PK_OFF_NPCS + 6 * id, 6);
                  *wk(gd, W_NPC) = (u16)id; *wk(gd, W_GFX0) = np.obj; break; }
    case R_STATUS: *wk(gd, W_GFX0) = PK_OBJ_GENTLEMAN;
                   *wk(gd, W_GFX1) = bits(r[K_PK_ROOM], 3, 1) ? PK_OBJ_DUSCLOPS : PK_OBJ_KIRLIA; break;
    case R_HEAL_PART: *wk(gd, W_GFX0) = PK_OBJ_GENTLEMAN; break;
    case R_WILD: break;
    case R_HARD: *wk(gd, W_TR_A) = (u16)random_trainer(r, 1); *wk(gd, W_GFX0) = (u16)trainer_obj(*wk(gd, W_TR_A));
                 *wk(gd, W_GFX1) = PK_OBJ_ATTENDANT; break;
    case R_DOUBLE: *wk(gd, W_TR_A) = (u16)random_trainer(r, 0); *wk(gd, W_TR_B) = (u16)random_trainer(r, 0);
                   *wk(gd, W_GFX0) = (u16)trainer_obj(*wk(gd, W_TR_A)); *wk(gd, W_GFX1) = (u16)trainer_obj(*wk(gd, W_TR_B)); break;
    case R_BRAIN: *wk(gd, W_GFX0) = PK_OBJ_LUCY; *wk(gd, W_GFX1) = PK_OBJ_ATTENDANT; break;
    }
    *var = (u16)type;
}

/* ---------------------------------------------------------------------------------------------------- battles */
static u32 highest_level(void *gd) {
    void *party = GameData_GetParty(gd); u32 i, best = 0;
    for (i = 0; i < n3(party); i++) {
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
static void fill_party(void *gd, void *party, void *other, u32 t_list, u32 t_iv, u32 n, u32 heap) {   /* FillTrainerParty */
    TrainerRec tr; SetRec s; u16 picked[3], sp[6], it[6]; u32 level = enemy_level(gd), iv = fixed_iv(t_iv), i = 0, j, k = 0, tries = 0;
    u8 evs[6];
    rd(&tr, PK_OFF_TRAINERS + 24 * t_list, sizeof tr);
    if (other) for (j = 0; j < PokeParty_GetPkmCount(other) && k < 6; j++) {    /* the first trainer's (a double) */
        void *pkm = PokeParty_GetPkm(other, j);
        sp[k] = (u16)pget(pkm, P_SPECIES); it[k] = (u16)pget(pkm, P_ITEM); k++;
    }
    while (i < n && tries++ < 2000) {
        u16 id; u32 c, e;
        rd(&id, PK_OFF_LISTS + 2 * (tr.list_off + rnd(tr.list_n)), 2);
        if (level == 50 && id > PK_HIGH_TIER) continue;
        rd(&s, PK_OFF_SETS + 16 * id, sizeof s);
        for (j = 0; j < k && sp[j] != s.species; j++) continue;
        if (j != k) continue;
        for (j = 0; j < k && !(it[j] && it[j] == s.item); j++) continue;
        if (j != k) continue;
        for (j = 0; j < i && picked[j] != id; j++) continue;
        if (j != i) continue;
        picked[i] = id;
        for (c = 0, j = 0; j < 6; j++) c += (s.ev >> j) & 1;
        e = c ? udiv(510, c) & 0xFF : 0;                             /* (u8 as Emerald's CreateMonWithEVSpread stores it) */
        for (j = 0; j < 6; j++) evs[j] = (u8)(((s.ev >> j) & 1) ? e : 0);
        make_mon(party, heap, s.species, level, iv, s.nature, s.moves, s.item, evs);
        sp[k] = s.species; it[k] = s.item; k++;
        i++;
    }
}
static u32 brain_party(u16 *r) {                                   /* GetFronterBrainSymbol: 0 silver, 1 gold party */
    u32 n = symbols(r), w = *streak(r) + kBrainStreak[3];
    if (n < 2) return n;
    if (w == kBrainStreak[0]) return 0;
    return 1;
}
static void fill_lucy(void *gd, void *party, u32 heap) {           /* CreateFrontierBrainPokemon */
    BrainRec b; u32 sym = brain_party(rec(gd)), i, level = enemy_level(gd);
    for (i = 0; i < 3; i++) {
        rd(&b, PK_OFF_LUCY + 24 * (3 * sym + i), sizeof b);
        make_mon(party, heap, b.species, level, b.iv, b.nature, b.moves, b.item, b.evs);
    }
}

#ifndef PK_PART_LINES                   /* the Frontier code area's part: the field-time hooks and the command */
void PK_LoadPlayerParty(void *setup, void *gd, u32 heap) {
    BtlSetup_LoadPlayerParty(setup, gd, heap);
    if (in_challenge(gd)) {
        void *party = *(void **)((u8 *)setup + 36);
        while (PokeParty_GetPkmCount(party) > 3) PokeParty_RemovePkm(party, PokeParty_GetPkmCount(party) - 1);
    }
}

void PK_LoadTrainer(void *setup, void *gd, u32 client, void **pparty, u32 trainerId, u32 heap) {
    u32 *tbs; TrainerRec tr; u32 t;
    BtlSetup_LoadTrainer(setup, gd, client, pparty, trainerId, heap);
    if ((trainerId != PK_TR_A && trainerId != PK_TR_B && trainerId != PK_TR_LUCY) || !in_challenge(gd)) return;
    tbs = *(u32 **)((u8 *)setup + 72 + 4 * client);
    PokeParty_InitCore(*pparty, 6);
    BtlSetup_SetFlag(setup, 0x200);                                 /* no experience (Emerald: BATTLE_TYPE_FRONTIER) */
    ((u16 *)(tbs + 3))[0] = ((u16 *)(tbs + 3))[1] = ((u16 *)(tbs + 3))[2] = ((u16 *)(tbs + 3))[3] = 0;   /* no items */
    if (trainerId == PK_TR_LUCY) {                                  /* the slot's class (LUCY_CLASS: Pike Queen), her */
        static const u16 kLucy[] = { 'L', 'u', 'c', 'y', 0xFFFF };   /* name (the slot's own is Black 2's) */
        GFL_StrBufLoadString((void *)tbs[5], kLucy);
        fill_lucy(gd, *pparty, heap);
        return;
    }
    t = *wk(gd, trainerId == PK_TR_A ? W_TR_A : W_TR_B);
    rd(&tr, PK_OFF_TRAINERS + 24 * t, sizeof tr);
    tbs[1] = tr.cls;
    GFL_StrBufLoadString((void *)tbs[5], tr.name);
    if (trainerId == PK_TR_A)                                       /* FillFrontierTrainerParty(3), or (1) each in */
        fill_party(gd, *pparty, 0, t, t, bits(rec(gd)[K_PK_STATE], 10, 4) == R_DOUBLE ? 1 : 3, heap);   /* a double */
    else                                                            /* (Emerald's FillTrainerParty draws the second */
        fill_party(gd, *pparty, *(void **)((u8 *)setup + 36 + 4), *wk(gd, W_TR_A), t, 1, heap);  /* trainer's from the first's list) */
}
#endif

#ifdef PK_PART_LINES                    /* the ITCM part */
/* the battle's trainer lines (ov167): a Pike trainer beaten says Emerald's speechLose (Lucy: "Urk…" / "Darn!") */
static u32 pike_trainer(u32 id) { u16 *r = rec_g(); return (id == PK_TR_A || id == PK_TR_B || id == PK_TR_LUCY) &&
                                  r[K_FACILITY] == FACILITY_PIKE && r[K_STATUS] == ST_IN_CHALLENGE; }
u32 PK_TrainerMsgExists(u32 id, u32 type, u32 heap) {
    if (pike_trainer(id)) return type == 1;
    return TrainerMsg_CheckExists(id, type, heap);
}
void PK_TrainerMsgLoad(u32 id, u32 type, void *strbuf, u32 heap) {
    u16 *r = rec_g(); void *msg; u32 line;
    if (!pike_trainer(id) || type != 1) { TrainerMsg_Load(id, type, strbuf, heap); return; }
    line = id == PK_TR_LUCY ? PK_LINE_LUCY_LOSE + brain_party(r) : PK_LINE_LOSE + r[K_PK_TR + (id == PK_TR_B)];
    msg = GFL_MsgSysLoadData(0, 3, PK_TEXT_ROOM, heap);
    GFL_MsgDataLoadStrbuf(msg, line, strbuf);
    GFL_MsgDataFree(msg);
}
#endif

#ifndef PK_PART_LINES                   /* the Frontier code area's part */
void PK_EncSetupNormal(void *field, void *encman, void *setup, u32 heap, void *param) {
    void *gd; u32 slot;
    FieldEncount_SetupNormal(field, encman, setup, heap, param);
    gd = *(void **)((u8 *)setup + 112);
    slot = *wk(gd, W_WILD);
    if (slot && in_challenge(gd)) {                                /* TryGenerateBattlePikeWildMon: the four moves */
        WildRec w; void *pkm = PokeParty_GetPkm(*(void **)((u8 *)setup + 40), 0); u32 j;
        rd(&w, PK_OFF_WILD + 12 * (slot - 1), sizeof w);
        for (j = 0; j < 4; j++) PokeParty_SetMove(pkm, w.moves[j], j);
        *wk(gd, W_WILD) = 0;
    }
}

/* the field's per-step check (ov036 FieldEventProvider_InitCheckData: ctx +0 heap id, +4 game system, +8 game data,
 * +16 the zone, +60 bit 4: the player has just finished a step) */
void *PK_CheckEncounter(void *ctx, void *a1, void *field) {
    void *gd = *(void **)((u8 *)ctx + 8);
    if (*(u16 *)((u8 *)ctx + 16) == PK_ZONE_WILD && in_challenge(gd)) {
        void *party = GameData_GetParty(gd), *lead = PokeParty_GetPkm(party, 0);
        u32 rate = 10 * 16;                                         /* WildEncounterCheck: encounterRate * 16 */
        if (!(((u8 *)ctx)[60] & 0x10)) return 0;                    /* (only after a step, as Black 2's own check) */
        if (pget(lead, P_ITEM) == I_CLEANSE_TAG) rate = udiv(rate * 2, 3);
        if (!pget(lead, P_IS_EGG)) {
            if (pget(lead, P_ABILITY) == A_STENCH) rate /= 2;
            else if (pget(lead, P_ABILITY) == A_ILLUMINATE) rate *= 2;
        }
        if (rnd(2880) >= rate) return 0;
        return EventScriptCall_Create(*(void **)((u8 *)ctx + 4), PK_WILD_SCRIPT, 0, *(u16 *)ctx);   /* (as the triggers' call) */
    }
    return CheckCallRandomEncounter(ctx, a1, field);
}

static u32 wild_setup(void *gd, u16 *var) {                        /* the species (0 = none) and W_WILD / W_WILD_LV */
    u16 *r = rec(gd); void *party = GameData_GetParty(gd), *lead = PokeParty_GetPkm(party, 0);
    u32 s = *streak(r), h = s <= 20 * 14 ? 0 : s <= 40 * 14 ? 1 : s <= 60 * 14 ? 2 : 3, x, slot = 0, acc = 0, m, level;
    WildRec w;
    /* TryGenerateWildMon (land): a Static lead picks an Electric slot half the time (only Electrode, the 2nd table);
       Magnet Pull would pick a Steel one, and no Pike table has one */
    if (!pget(lead, P_IS_EGG) && pget(lead, P_ABILITY) == A_STATIC && rnd(2) == 0 && h == 1) m = 2;
    else {
        x = rnd(100);                                               /* ChooseWildMonIndex_Land */
        while (slot < 11 && x >= (acc += kLandRates[slot])) slot++;
        m = (slot == 0 || slot == 6 || slot == 10) ? 0 : (slot == 1 || slot == 7 || slot == 11) ? 1 : 2;   /* gBattlePike_N */
    }
    rd(&w, PK_OFF_WILD + 12 * (12 * lvl(r) + 3 * h + m), sizeof w);
    if (lvl(r)) {
        level = highest_level(gd);
        level = level < 60 ? 60 : level - w.delta < 60 ? 60 : level - w.delta;
    } else level = 50 - w.delta;
    if (!pget(lead, P_IS_EGG) && (pget(lead, P_ABILITY) == A_KEEN_EYE || pget(lead, P_ABILITY) == A_INTIMIDATE)) {
        u32 pl = pget(lead, P_LEVEL);                              /* CanEncounterWildMon */
        if (pl > 5 && level <= pl - 5 && rnd(2) == 0) { *var = 0; return 0; }
    }
    *wk(gd, W_WILD) = (u16)(12 * lvl(r) + 3 * h + m + 1);
    *wk(gd, W_WILD_LV) = (u16)level;
    *var = w.species;
    return 1;
}

/* the three's order: FR_PARTY's picks moved to slots 0-2 (swaps), and back */
static void party_order(void *gd, u32 apply, u32 heap) {
    void *party = GameData_GetParty(gd); u16 *r = rec(gd); u32 p[3], i, j, n = PokeParty_GetPkmCount(party), pos[6];
    for (i = 0; i < 3; i++) p[i] = (r[K_PARTY] >> (4 * i)) & 15;
    if (!p[0]) return;
    for (i = 0; i < n; i++) pos[i] = i;                             /* pos[k] = where original slot k is now */
    if (apply) {
        for (i = 0; i < 3 && p[i]; i++) {
            u32 from = pos[p[i] - 1];
            if (from >= n || from == i) continue;
            for (j = 0; j < n; j++) if (pos[j] == i) pos[j] = from;
            pos[p[i] - 1] = i;
            PokeParty_SwapPkms(party, i, from, heap);
        }
    } else {                                                        /* undo: replay the swaps backwards */
        u32 sw[3][2], k = 0;
        for (i = 0; i < 3 && p[i]; i++) {
            u32 from = pos[p[i] - 1];
            if (from >= n || from == i) continue;
            for (j = 0; j < n; j++) if (pos[j] == i) pos[j] = from;
            pos[p[i] - 1] = i;
            sw[k][0] = i; sw[k][1] = from; k++;
        }
        while (k--) PokeParty_SwapPkms(party, sw[k][0], sw[k][1], heap);
    }
}

enum { PK_INIT, PK_GET, PK_SET, PK_NEXT_ROOM, PK_ROOM_TYPE, PK_SETUP_ROOM, PK_INTRO, PK_STATUS_KIND, PK_STATUS_MON,
       PK_HEAL_ONE_TWO, PK_NPC_SPEECH, PK_SET_HINT, PK_HINT_ROOM, PK_HINT_KIND, PK_QUEEN_TYPE, PK_HEAL_BEFORE_QUEEN,
       PK_FULL_HEALTH, PK_SAVE_ITEMS, PK_RESTORE_ITEMS, PK_IS_FINAL, PK_WILD, PK_PARTY_ORDER, PK_ALL_FAINTED };
/* (BP, eligibility, symbols and the lobby's heal are frontier_core's: fr_lobby_returned, fr_lobby_attendant,
   fr_symbol_give) */
enum { F_STREAK, F_RECORD, F_TOTAL, F_STREAK_ACTIVE, F_ROOM, F_STATUS, F_LVL, F_HEARD_BRAIN, F_PAUSED, F_HEAL_OFF,
       F_SYMBOLS, F_HINT_INDEX, F_DOOR, F_LAST_BP };

static u32 field_get(u16 *r, u32 f) {
    switch (f) {
    case F_STREAK: return *streak(r);
    case F_RECORD: return streak(r)[1];
    case F_TOTAL: return r[K_PK_TOTAL + lvl(r)];
    case F_STREAK_ACTIVE: return bits(r[K_PK_ROOM], 4 + lvl(r), 1);
    case F_ROOM: return r[K_BATTLE_NUM];
    case F_STATUS: return r[K_STATUS];
    case F_LVL: return lvl(r);
    case F_HEARD_BRAIN: return bits(r[K_PK_STATE], 14, 1);
    case F_PAUSED: return bits(r[K_PK_STATE], 15, 1);
    case F_HEAL_OFF: return bits(r[K_PK_STATE], 7, 1);
    case F_SYMBOLS: return symbols(r);
    case F_HINT_INDEX: return bits(r[K_PK_STATE], 0, 3);
    case F_DOOR: return bits(r[K_PK_STATE], 8, 2);
    case F_LAST_BP: return r[K_LAST_BP];
    }
    return 0;
}
static void field_set(u16 *r, u32 f, u32 v) {
    switch (f) {
    case F_STREAK: if (v <= 9999) *streak(r) = (u16)v; break;
    case F_RECORD: if (v <= 9999 && streak(r)[1] < v) streak(r)[1] = (u16)v; break;     /* (only ever raised) */
    case F_TOTAL: if (v <= 9999) r[K_PK_TOTAL + lvl(r)] = (u16)v; break;
    case F_STREAK_ACTIVE: setbits(&r[K_PK_ROOM], 4 + lvl(r), 1, v != 0); break;
    case F_ROOM: r[K_BATTLE_NUM] = (u16)v; break;
    case F_STATUS: r[K_STATUS] = (u16)v; break;
    case F_LVL: r[K_LVL_MODE] = (u16)(v & 1); break;
    case F_HEARD_BRAIN: setbits(&r[K_PK_STATE], 14, 1, v != 0); break;
    case F_PAUSED: setbits(&r[K_PK_STATE], 15, 1, v != 0); break;
    case F_HEAL_OFF: setbits(&r[K_PK_STATE], 7, 1, v != 0); break;
    }
}

u32 PK_Cmd(void *vm, void *env) {
    u16 *var = ScriptReadVar(vm, env);
    u32 op = ScriptReadAny(vm, env) & 0xffff, a = ScriptReadAny(vm, env) & 0xffff, b = ScriptReadAny(vm, env) & 0xffff;
    void *gd = FieldScriptEnv_GetGameData(env), *party = GameData_GetParty(gd);
    u16 *r = rec(gd);
    u32 i, n;
    switch (op) {
    case PK_INIT:                                                   /* InitPikeChallenge (a = level mode) */
        r[K_FACILITY] = FACILITY_PIKE; r[K_BATTLE_MODE] = 0; r[K_LVL_MODE] = (u16)(a & 1);
        r[K_STATUS] = 0; r[K_BATTLE_NUM] = 0; setbits(&r[K_PK_STATE], 15, 1, 0);
        r[K_PK_SEEN] = r[K_PK_SEEN + 1] = 0;
        if (!bits(r[K_PK_ROOM], 4 + lvl(r), 1)) *streak(r) = 0;
        break;
    case PK_GET: *var = (u16)field_get(r, a); break;
    case PK_SET: field_set(r, a, b); break;
    case PK_NEXT_ROOM:                                              /* SetRoomType, door a (0 left, 1 centre, 2 right) */
        setbits(&r[K_PK_STATE], 8, 2, a);
        setbits(&r[K_PK_STATE], 10, 4, next_room_type(gd, a));
        *var = (u16)bits(r[K_PK_STATE], 10, 4);
        break;
    case PK_ROOM_TYPE: *var = (u16)bits(r[K_PK_STATE], 10, 4); break;
    case PK_SETUP_ROOM: *wk(gd, W_TR_A) = *wk(gd, W_TR_B) = 0xFFFF; setup_room(gd, var);
        r[K_PK_TR] = *wk(gd, W_TR_A); r[K_PK_TR + 1] = *wk(gd, W_TR_B); break;
    case PK_INTRO: *var = *wk(gd, a ? W_TR_B : W_TR_A); break;     /* (the line = the trainer's index) */
    case PK_STATUS_KIND: *var = (u16)bits(r[K_PK_ROOM], 0, 3); break;
    case PK_STATUS_MON: *var = (u16)bits(r[K_PK_ROOM], 3, 1); break;
    case PK_HEAL_ONE_TWO: n = rnd(2) + 1; try_heal(party, n); *var = (u16)n; break;
    case PK_NPC_SPEECH: {                                           /* BufferNPCMessage: the speech's index */
        NpcRec np; rd(&np, PK_OFF_NPCS + 6 * *wk(gd, W_NPC), 6);
        *var = np.speech[r[K_BATTLE_NUM] <= 4 ? 0 : r[K_BATTLE_NUM] <= 10 ? 1 : 2];
        break; }
    case PK_SET_HINT: set_hint_room(gd, var); break;
    case PK_HINT_ROOM: *var = (u16)bits(r[K_PK_STATE], 0, 3); break;
    case PK_HINT_KIND: *var = kRoomHint[bits(r[K_PK_STATE], 3, 4)]; break;
    case PK_QUEEN_TYPE: *var = (u16)queen_fight_type(r, 0); break;
    case PK_HEAL_BEFORE_QUEEN:
        n = kHealBeforeQueen[umod(bits(r[K_PK_STATE], 0, 3), 6)][umod(bits(r[K_PK_STATE], 8, 2), 3)];
        try_heal(party, n); *var = (u16)n; break;
    case PK_FULL_HEALTH:                                            /* IsPartyFullHealed */
        *var = 1;
        for (i = 0; i < n3(party); i++) if (can_be_healed(PokeParty_GetPkm(party, i))) { *var = 0; break; }
        break;
    case PK_SAVE_ITEMS:                                             /* SaveMonHeldItems (the three are first) */
        for (i = 0; i < 3; i++) r[K_PK_ITEMS + i] = (u16)(i < n3(party) ? pget(PokeParty_GetPkm(party, i), P_ITEM) : 0);
        break;
    case PK_RESTORE_ITEMS:
        for (i = 0; i < n3(party); i++) PokeParty_SetParam(PokeParty_GetPkm(party, i), P_ITEM, r[K_PK_ITEMS + i]);
        break;
    case PK_IS_FINAL: *var = r[K_BATTLE_NUM] > NUM_PIKE_ROOMS; break;
    case PK_WILD: wild_setup(gd, var); break;
    case PK_PARTY_ORDER: party_order(gd, a, FieldScriptEnv_GetHeapID(env)); break;
    case PK_ALL_FAINTED:                                            /* the three can no longer battle (lost or drew) */
        *var = 1;
        for (i = 0; i < n3(party); i++) if (alive(PokeParty_GetPkm(party, i))) { *var = 0; break; }
        break;
    }
    (void)b;
    return 0;
}
#endif
