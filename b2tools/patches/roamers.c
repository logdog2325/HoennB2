/* Hoenn's roaming legendaries (postgame_scripts, 2026-10-07): Sapphire's roamer (pokeruby src/roamer.c) for seven
 * roamers at once, on Black 2's own roaming-battle path. Compiled and placed in ITCM by b2tools/patches/roamers.py
 * (which has the findings: what Black 2 keeps of Black/White 1's roamers and where each hook goes).
 *
 * Save: the seven roamers live in the first 44 bytes of Black 2's encounter save block (block 55, 52 bytes): BW1's two
 * 20-byte roamer slots and their four clock/state bytes, which no Black 2 code writes and only the roaming code reads.
 * A new game zeroes the block (EncountSave_Init): every roamer inactive.
 *   +6k  roamer k (k 0-6): u16 hp (0 = inactive: not started, caught or knocked out), u8 location (0-19, Sapphire's
 *        sRoamerLocations row; bit 7 set = knocked out, roams again after the next Hall of Fame), u8 status, u16 seed
 *        (its PID, IVs and nature come from it: the same Pokemon every time)
 *   +42  the roamer of the battle in progress, + 1
 *   +43  the place (zone header place name) the player is on = Sapphire's sLocationHistory[0]
 * Work VAR_ROAMER_PLACE_HISTORY: low byte sLocationHistory[1], high byte sLocationHistory[2].
 * Places: Sapphire's map of a route = the place name of its zones (every zone of one Sapphire map has the map's place;
 * the desert's weather zones copy Route 111's header).
 */
typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;

#ifndef PG_VAR_HISTORY
#error "PG_VAR_HISTORY (the work id) comes from roamers.py"
#endif

/* Black 2 functions (decomp symbols, config/b2_us/arm9/...; Thumb: address | 1) */
#define FN(type, addr) ((type)((addr) | 1))
#define GFL_RandomLCAlt            FN(u32 (*)(u32), 0x02005784)           /* random in [0, n) */
#define SaveControl_GetEncountSave FN(u8 *(*)(void *), 0x0200dcf0)
#define GameData_GetEventWork      FN(void *(*)(void *), 0x02017394)
#define GameData_GetSaveControl    FN(void *(*)(void *), 0x02017934)
#define BtlSetup_GetParty          FN(void *(*)(void *, u32), 0x02017d10)
#define ZoneData_GetPlaceNameID    FN(u32 (*)(u32), 0x02018c80)
#define EventWork_GetWkPtr         FN(u16 *(*)(void *, u32), 0x02019294)
#define PokeParty_CreatePkm        FN(void (*)(void *, u32, u32, u32, u32, u32, u32, u32), 0x0201c464)
#define PokeParty_GetParam         FN(u32 (*)(void *, u32, void *), 0x0201ccf8)
#define PokeParty_GetPkm           FN(void *(*)(void *, u32), 0x0201ff08)
/* ov012 (the field's script/event overlay) */
#define ScriptReadVar              FN(u16 *(*)(void *, void *), 0x021548e8)
#define ScriptReadAny              FN(u32 (*)(void *, void *), 0x02154910)
#define FieldScriptEnv_GetGameData FN(void *(*)(void *), 0x02155174)
#define func_ov012_0215ee40        FN(void (*)(void *, u32), 0x0215ee40)   /* the zone-entry part of InitSpawn */
#define func_ov012_0215ee10        FN(void (*)(void *, void *), 0x0215ee10) /* the zone-change part of Field_SwapZoneByMatrix */
#define EventBattleCall_SyncGameDataOnReturn FN(void (*)(void *, void *), 0x021690e8)
/* ov036 (the field) */
#define FieldEncount_CheckLevelRepelled FN(u32 (*)(void *, u32), 0x021a1150)
#define FieldEncount_SetupRoaming  FN(void (*)(void *, void *, void *, u32, void *), 0x021a1cac)

#define PKM_PARAM_STATUS 0x9d
#define PKM_PARAM_HP     0xa0
#define PKM_PARAM_MAX_HP 0xa1
#define BTL_FLAG_ROAMING 8          /* BtlSetup battle-type flag 8 (word +0x9c): FieldEncount_SetupRoaming sets it (roaming AI: flees) */
#define RESULT_WON 1                /* battle results (ov012 GetWildBattleResultByCombined's table: 5 caught, 1 won) */
#define RESULT_CAUGHT 5
#define N_ROAMERS 7
#define N_LOCS 20

/* tables (roamers.py writes roamers_data.h: kSpecies, kLevel, kPlace[20], kAdj[20][5]; Emerald also kLatiAlt) */
#include "roamers_data.h"

/* EMERALD (emerald_ch11_gameclear, 2026-10-12; -DPG_LATI_BY_SEED, set by roamers.py in an Emerald build only): roamer 0 is Latias
 * or Latios by the colour the player tells Mom after the Hall of Fame (pokeemerald InitRoamer: 0 Red = Latias, 1 Blue = Latios).
 * The script passes the choice as bit 8 of the roamer number (pg_roamer_start 0x100 = Latios); it is kept in bit 0 of the
 * roamer's 16-bit seed (random anyway: PID, IVs and nature come from the other bits), so the save layout is unchanged, and every
 * place that makes the Pokemon asks SPECIES_OF. Sapphire and Ruby builds keep the plain table read (the same machine code). */
#ifdef PG_LATI_BY_SEED
static u32 species_of(u32 k, u32 seed) { return (k == 0 && (seed & 1)) ? kLatiAlt : kSpecies[k]; }
#define SPECIES_OF(k, seed) species_of(k, seed)
#else
#define SPECIES_OF(k, seed) kSpecies[k]
#endif

typedef struct { u16 hp; u8 loc; u8 status; u16 seed; } Roamer;
/* BW1's roamer record, as FieldEncount_GenRoamingPkm reads it (arm9 EncountSave_GetRoamingPkmParam: 1 zone, 10 nature
 * (+2, set as PKM field 0x70), 2 IVs, 3 PID, 4 species, 5 HP, 6 level, 7 status, 8 active) */
typedef struct { u16 zone; u8 nature; u8 pad; u32 ivs; u32 pid; u16 species; u16 hp; u8 level; u8 status; u8 active; u8 pad2; } Record;

static Roamer *roamer(u8 *save, u32 k) { return (Roamer *)(save + 6 * k); }

static u32 lcg(u32 *x) { *x = *x * 0x41C64E6Du + 0x6073u; return *x >> 16; }

/* the roamer's Pokemon from its seed: Gen 3's PID, then the IVs of two more calls (HP/Atk/Def, Spe/SpA/SpD), packed as
 * PML_CreatePkm reads them (bits 0 HP, 5 Atk, 10 Def, 15 SpA, 20 SpD, 25 Spe), and a nature */
static void derive(u32 seed, u32 *pid, u32 *ivs, u32 *nature) {
    u32 x = seed, lo, hi, a, b;
    lo = lcg(&x); hi = lcg(&x);
    *pid = hi << 16 | lo;
    a = lcg(&x); b = lcg(&x);
    *ivs = (a & 0x7fff) | ((b >> 5) & 31) << 15 | ((b >> 10) & 31) << 20 | (b & 31) << 25;
    *nature = (lcg(&x) * 25) >> 16;
}

static u8 *encount_save(void *gd) { return SaveControl_GetEncountSave(GameData_GetSaveControl(gd)); }

/* roamer k's max HP: its Pokemon made in a stack buffer (PokeParty_GetPkmRawSize: 220 bytes) and read back */
static u32 max_hp(u32 k, u32 seed) {
    u32 buf[224 / 4];
    u32 pid, ivs, nature;
    derive(seed, &pid, &ivs, &nature);
    PokeParty_CreatePkm(buf, SPECIES_OF(k, seed), kLevel[k], 0, 0, ivs, pid, 0);
    return PokeParty_GetParam(buf, PKM_PARAM_MAX_HP, 0);
}

/* Sapphire RoamerMoveToOtherLocationSet */
static void move_other_set(Roamer *r) {
    u32 v;
    if (!r->hp) return;
    do v = GFL_RandomLCAlt(N_LOCS); while (v == r->loc);
    r->loc = v;
}

/* Sapphire RoamerMove: 1 in 16 a jump, else a neighbouring route that is not where the player was two maps ago */
static void move(Roamer *r, u32 two_ago) {
    const u8 *row;
    u32 m;
    if (GFL_RandomLCAlt(16) == 0) { move_other_set(r); return; }
    if (!r->hp) return;
    row = kAdj[r->loc];
    for (;;) {
        m = row[GFL_RandomLCAlt(5)];
        if (m != 0xff && kPlace[m] != two_ago) break;
    }
    r->loc = m;
}

/* the player changed maps: Sapphire's UpdateLocationHistoryForRoamer + RoamerMove (a map connection) or
 * RoamerMoveToOtherLocationSet (a warp) for every roamer. A walk into another zone of the same map does nothing. */
static void map_change(void *gd, u32 zone, u32 warp) {
    u8 *save = encount_save(gd);
    u16 *hist = EventWork_GetWkPtr(GameData_GetEventWork(gd), PG_VAR_HISTORY);
    u32 place = ZoneData_GetPlaceNameID(zone & 0xffff) & 0xff;
    u32 k;
    if (!warp && place == save[43]) return;
    *hist = (u16)((*hist << 8) | save[43]);
    save[43] = (u8)place;
    for (k = 0; k < N_ROAMERS; k++) {
        if (warp) move_other_set(roamer(save, k));
        else move(roamer(save, k), *hist >> 8);
    }
}

/* replaces the call of func_ov012_0215ee10 in ov036 Field_SwapZoneByMatrix (the player walked into another zone: Black
 * 2's zone-change step, which also calls the emptied BW1 roamer hook func_ov012_021591f4): the shim passes the new
 * zone, which the caller keeps in r4 (ZoneLookup's answer); that call, then the move */
void PG_OnZoneSwap(void *gd, void *field, u32 zone) {
    func_ov012_0215ee10(gd, field);
#ifdef PG_DEBUG
    encount_save(gd)[42] = (u8)(0x80 | (ZoneData_GetPlaceNameID(zone & 0xffff) & 0x7f));
#endif
    map_change(gd, zone, 0);
}
__attribute__((naked)) void PG_OnZoneSwapShim(void) {
    __asm__ volatile("adds r2, r4, #0\n\tb PG_OnZoneSwap\n");
}

/* replaces the call of func_ov012_0215ee40 in ov035 FieldMapControl_InitSpawn, which every map load runs (warps of all
 * kinds through EventMapChangeCore, fly, blackout, Continue, the new game) with the new zone: that call, then the move */
void PG_OnSpawn(void *gd, u32 zone) {
    func_ov012_0215ee40(gd, zone);
    map_change(gd, zone, 1);
}

/* replaces the call of FieldEncount_RndCheckRoaming in EventWildBattleCall_CreateRandom (ov036): a wild encounter is
 * happening in zone `zone`; returns roamer + 1 to battle instead, or 0. Sapphire TryStartRoamerEncounter: the roamer's
 * map, then 1 in 4 (Black 2 BW1: 1 in 2). Roamers the Repel keeps away are not candidates (Black 2's rule). */
u32 PG_RndCheck(void *mgr, u32 zone) {
    u8 *save = *(u8 **)((u8 *)mgr + 4);         /* the encounter manager's EncountSave (as RndCheckRoaming reads it) */
    u32 place = ZoneData_GetPlaceNameID(zone & 0xffff);
    u8 cand[N_ROAMERS];
    u32 n = 0, k;
    for (k = 0; k < N_ROAMERS; k++) {
        Roamer *r = roamer(save, k);
        if (r->hp && kPlace[r->loc] == place && !FieldEncount_CheckLevelRepelled(mgr, kLevel[k])) cand[n++] = (u8)k;
    }
    if (!n) return 0;
#ifndef PG_TEST_ALWAYS
    if (GFL_RandomLCAlt(4) != 0) return 0;
#endif
    return cand[n > 1 ? GFL_RandomLCAlt(n) : 0] + 1;
}

/* replaces the call of FieldEncount_SetupRoaming in EventWildBattleCall_CreateRandom: the 5th argument is the roamer + 1
 * (PG_RndCheck's answer); builds BW1's record for it and runs Black 2's own setup (battle flag 8, roaming AI) */
void PG_SetupRoaming(void *encsys, void *mgr, void *setup, u32 heap, u32 k1) {
    u8 *save = *(u8 **)((u8 *)mgr + 4);
    Roamer *r = roamer(save, k1 - 1);
    Record rec;
    u32 pid, ivs, nature;
    derive(r->seed, &pid, &ivs, &nature);
    rec.zone = 0; rec.nature = (u8)nature; rec.pad = 0;
    rec.ivs = ivs; rec.pid = pid;
    rec.species = SPECIES_OF(k1 - 1, r->seed); rec.hp = r->hp; rec.level = kLevel[k1 - 1];
    rec.status = r->status; rec.active = 1; rec.pad2 = 0;
    save[42] = (u8)k1;
    FieldEncount_SetupRoaming(encsys, mgr, setup, heap, &rec);
#ifdef PG_TEST_NO_FLEE
    *(u32 *)((u8 *)setup + 0x9c) &= ~BTL_FLAG_ROAMING;     /* test builds: no roaming AI (BtlSetup_SetFlag's word) */
#endif
}

/* after every battle (ov012 EventBattleCall_Callback, in place of its EventBattleCall_SyncGameDataOnReturn call, while
 * the BtlSetup still exists: EventBattleCall_ReleaseBtlSetup frees it right after): after a roaming battle (+42 set by
 * PG_SetupRoaming), Sapphire's UpdateRoamerHPStatus (HP, status, another location set) and SetRoamerInactive when it was
 * knocked out or caught; knocked out also sets the location's bit 7 (it comes back after the next Hall of Fame, the
 * Gen 4+ rule: user decision). Black 2 copies the wild side's party back into the BtlSetup (ov167 btl_main.c, battle
 * type 0); the result is BtlSetup +0xA8 (what SyncGameDataOnReturn stores as the last battle result). Then the call. */
void PG_BattleReturn(void **work, void *gd) {
    u8 *setup = work[2];
    u8 *save = encount_save(gd);
    u32 k1 = save[42];
    if (k1 >= 1 && k1 <= N_ROAMERS) {
        u32 res = *(u32 *)(setup + 0xA8);
        Roamer *r = roamer(save, k1 - 1);
        void *pkm = PokeParty_GetPkm(BtlSetup_GetParty(setup, 1), 0);
        u32 hp = PokeParty_GetParam(pkm, PKM_PARAM_HP, 0);
#ifdef PG_DEBUG
        save[43] = (u8)(0xE0 | (res << 1));
#endif
        r->status = (u8)PokeParty_GetParam(pkm, PKM_PARAM_STATUS, 0);
        r->hp = (u16)hp;
        move_other_set(r);
        if (res == RESULT_CAUGHT) r->hp = 0;
        else if (res == RESULT_WON || hp == 0) { r->hp = 0; r->loc |= 0x80; }
    }
    save[42] = 0;
    EventBattleCall_SyncGameDataOnReturn(work, gd);
}

/* replaces the call of func_ov012_02159220 (empty in Black 2: BW1's roamer hook of the game clear) in ov012
 * EventGameClear_Create, which the Hall of Fame's CallGameClear runs before the game is saved: every roamer that was
 * knocked out (not caught) roams again, full HP, the same Pokemon, a random location (as InitRoamer) */
void PG_OnGameClear(void *gd) {
    u8 *save = encount_save(gd);
    u32 k;
    for (k = 0; k < N_ROAMERS; k++) {
        Roamer *r = roamer(save, k);
        if (r->hp || !(r->loc & 0x80)) continue;
        r->status = 0;
        r->loc = (u8)GFL_RandomLCAlt(N_LOCS);
        r->hp = (u16)max_hp(k, r->seed);
    }
}

/* script command 434 (BW1's roamer command, unused by Black 2's scripts): pg_roamer_start k, loc. Sapphire's InitRoamer
 * for roamer k: a new seed, full HP (max_hp), no status, location `loc` (0-19) or a random one (Sapphire:
 * sRoamerLocations[Random() % 20]). */
u32 PG_CmdStartRoamer(void *vm, void *env) {
    void *gd = FieldScriptEnv_GetGameData(env);
    u32 k = ScriptReadAny(vm, env) & 0xffff;
    u32 loc = ScriptReadAny(vm, env) & 0xffff;
    u32 seed;
    Roamer *r;
#ifdef PG_LATI_BY_SEED
    u32 lati = (k >> 8) & 1;                    /* pg_roamer_start 0x100: roamer 0 as Latios (Emerald's Blue) */
    k &= 0xff;
#endif
    if (k >= N_ROAMERS) return 0;
    r = roamer(encount_save(gd), k);
    seed = GFL_RandomLCAlt(0xffff) + 1;
#ifdef PG_LATI_BY_SEED
    if (k == 0) seed = ((seed | 2) & ~1u) | lati;   /* the Lati choice in bit 0 (never a zero seed) */
#endif
    r->seed = (u16)seed;
    r->status = 0;
    r->loc = (u8)(loc < N_LOCS ? loc : GFL_RandomLCAlt(N_LOCS));
    r->hp = (u16)max_hp(k, seed);
    return 0;
}

/* script command 435 (BW1's, unused): pg_roamer_get var, k -> 0 inactive, else the location + 1 */
u32 PG_CmdGetRoamer(void *vm, void *env) {
    void *gd = FieldScriptEnv_GetGameData(env);
    u16 *var = ScriptReadVar(vm, env);
    u32 k = ScriptReadAny(vm, env) & 0xffff;
    Roamer *r;
    *var = 0;
    if (k >= N_ROAMERS) return 0;
    r = roamer(encount_save(gd), k);
    if (r->hp) *var = (u16)(r->loc + 1);
    return 0;
}
