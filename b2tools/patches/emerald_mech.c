/* Pokémon Emerald NDS mechanics (emerald_mech, 2026-10-12): two field-script commands for HOENN_VERSION=emerald
 * builds only. Compiled and placed in ITCM by b2tools/patches/emerald_mech.py, which also has the findings (what
 * Black 2 has for tag battles and move tutors, and why these two commands are needed).
 *
 *   command 533 (Black 2's func_ov012_021658c8, unused by every script): EmPartySwap a, b
 *       swaps party slots a and b (Black 2's PokeParty_SwapPkms, as its own Zekrom/Reshiram command does); nothing
 *       when a == b or either slot is past the party's end. Used by the tag battle's party choice (global 2290).
 *   command 281 (Black 2's PokePartyIsFromWhiteForest, unused): EmTutorCheck var, slot, tutor
 *       var = 0 the Pokémon in party slot `slot` can learn Emerald tutor move `tutor` (pokeemerald TUTOR_MOVE_*, 0-29),
 *       1 it cannot (Emerald's sTutorLearnsets; an Egg cannot either), 2 it already knows the move (Emerald's
 *       CanMonLearnTMTutor: CANNOT_LEARN_MOVE / ALREADY_KNOWS_MOVE). Used by the move tutor script (global 2289).
 *   command 686 (Black 2's func_ov012_0216a82c, unused): EmPickParty var
 *       Emerald's ChooseHalfPartyForBattle in one party menu: Black 2's own battle-entry party screen (ov165, the
 *       mode the Battle Subway and the Battle Institute use: numbered picks, a pick tapped again is unmarked, then
 *       confirm), run through Black 2's own event for it (func_ov012_02161c88, the Battle Institute's), with its
 *       regulation changed to Emerald's multi rule (1 to 3 Pokémon, any level, no species or item clause). Writes
 *       var = how many were picked and the next three works = the picked party slots (0-5) in pick order, 255 for
 *       none; var | 0x80 when the screen was left with CANCEL or B (var = 0: nothing was marked). Called with
 *       var = 0x40 | n, the n slots in the next works are marked when the screen opens. Used by the tag battle
 *       (global 2290).
 * and two hooks for the tag battle (Emerald: each side of a multi battle has at most 3 Pokémon, MULTI_PARTY_SIZE;
 * Black 2's partner battles give the player the whole party: tested, a 4th Pokémon could be sent out):
 *   EM_SetTrainer2v2: ov036 BtlSetup_SetTrainerLocal's call of BtlSetup_SetTrainer2v2 (the battle with a partner,
 *       CallTrainerMultiBattle): the original, then the battle's copy of the player's party (BtlSetup +36) keeps only
 *       its first n, the ones the tag battle script moved to the front: n = bits 12-15 of the partner id the script
 *       passed (1-3; 0 = 3), which are taken off before the original loads the partner (trainer ids are < 0x1000;
 *       EventTrainerBattleCall_Create and BtlSetup_SetTrainerLocal use the partner id for nothing else).
 *   EM_PartyCopyBack: ov166's copy of the battle's party back into the player's party after a local battle
 *       (PokeParty_Copy): when the battle's party is shorter than the player's (only after EM_SetTrainer2v2), its
 *       Pokémon (HP, experience, PP ...) go back into the first slots and the others stay; otherwise PokeParty_Copy.
 */
typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;

/* Black 2 functions (decomp symbols, config/b2_us/arm9/...; Thumb: address | 1) */
#define FN(type, addr) ((type)((addr) | 1))
#define GameData_GetParty          FN(void *(*)(void *), 0x0201735c)
#define PokeParty_GetParam         FN(u32 (*)(void *, u32, void *), 0x0201ccf8)
#define PokeParty_GetPkmCount      FN(u32 (*)(void *), 0x0201fdf8)
#define PokeParty_GetPkm           FN(void *(*)(void *, u32), 0x0201ff08)
#define PokeParty_SwapPkms         FN(void (*)(void *, u32, u32, u32), 0x0201ff58)
#define PokeParty_RemovePkm        FN(u32 (*)(void *, u32), 0x0201fda8)
#define PokeParty_Copy             FN(void (*)(void *, void *), 0x020200ac)
#define BtlSetup_SetTrainer2v2     FN(void (*)(void *, void *, void *, u32, u32, u32, u32), 0x020183b0)
#define ScriptReadVar              FN(u16 *(*)(void *, void *), 0x021548e8)
#define ScriptReadAny              FN(u32 (*)(void *, void *), 0x02154910)
#define FieldScriptEnv_GetHeapID   FN(u32 (*)(void *), 0x0215515c)
#define FieldScriptEnv_GetGameData FN(void *(*)(void *), 0x02155174)
#define FieldScriptEnv_GetGameSystem FN(void *(*)(void *), 0x0215516c)
#define FieldScriptEnv_GetScriptWork FN(void *(*)(void *), 0x02155184)
#define ScriptWork_CallEvent       FN(void (*)(void *, void *), 0x02153880)
#define GSYS_GetGameData           FN(void *(*)(void *), 0x02016ad8)
#define GameEvent_Create           FN(void *(*)(void *, void *, void *, u32), 0x02016cb4)
#define GameEvent_ChainNext        FN(void (*)(void *, void *), 0x02016d68)
#define GameEvent_GetData          FN(void *(*)(void *), 0x02016edc)
/* the Battle Institute's team selection event (ov012): gsys, style (unk48), party screen mode, regulation file (arc 106),
 * party shown, out picked[6] (party slots from 1, in pick order), out the screen's index (7/8 = cancelled), out its
 * result, a party to fill with the picks (NULL: none) */
#define TeamSelect_Create          FN(void *(*)(void *, u32, u32, u32, void *, u8 *, u32 *, u32 *, void *), 0x02161c88)

#define PKM_PARAM_SPECIES 0x05
#define PKM_PARAM_MOVE1   0x36
#define PKM_PARAM_IS_EGG  0x4c
#define MULTI_PARTY_SIZE  3         /* pokeemerald include/constants/global.h */
#define BTLSETUP_PARTY0   36        /* BtlSetup +36: the player's party (BtlSetup_LoadPlayerParty) */
#define PARTNER_KEEP_SHIFT 12       /* CallTrainerMultiBattle's partner id: bits 12-15 = how many of the player's */
#define PARTNER_ID_MASK   0xFFF     /* Pokémon battle (global 2290 sets them; 0 = 3), the rest = the trainer id */
#define PKM_WORDS         (220 / 4) /* one party Pokémon (PokeParty_AddPkm copies 220 bytes) */
#ifndef PICK_MODE
#define PICK_MODE         22        /* ov165 party screen mode: 22 = the Battle Subway's entry, 23 = the Battle Institute's */
#endif
#ifndef PICK_STYLE
#define PICK_STYLE        0         /* Ov165Param unk48: 0 single, 1 double, 2 multi (the Subway's own values) */
#endif
#define PICK_REGULATION   22        /* arc 106 file 22: the Subway's multi rule (4 04 02 02 ...), changed below */
#define REG_OFFSET        216       /* the regulation inside the team selection event's data (func_0201f744 target) */
#define REG_SPECIES_BANS  0x0A      /* include/battle/regulation.h unkA[0x52]: a bit per species (0-655) */
#define REG_ITEM_BANS     0x5C      /* unk5C[0x4c]: a bit per item (file 22: only bit 225, the Soul Dew) */
#define REG_ITEM_BANS_END 0xA8
#define PICKED_OFFSET     (48 + 0x59) /* Ov165Param picked[6] (party slots from 1) inside that event's data */
#define PICK_KEEP         0x40      /* var on entry: mark these picks when the screen opens */
#define PICK_FRONTIER     0x20      /* var on entry: the Battle Frontier's rule instead (frontier_core, 2026-10-12,
                                       notes/FRONTIER.md 2.4): exactly var & 7 Pokémon, no species or held item twice,
                                       arc 106 file 22's banned list (Black 2's Battle Subway list = Emerald's
                                       gFrontierBannedSpecies + Gen 4/5 legends); PICK_LV50: level 50 or less */
#define PICK_LV50         0x10
#define PICK_CANCELLED    0x80      /* var on exit: the screen was left with CANCEL / B */
#define PICK_CANCEL_A     7         /* the screen's index when it was left without picking (Battle Institute: */
#define PICK_CANCEL_B     8         /* func_ov012_02162ccc treats 7 and 8 with result 0 as cancelled) */

/* emerald_mech_data.h (written by emerald_mech.py): N_SPECIES, N_TUTOR, kTutorMove[N_TUTOR] (move ids),
 * kTutorBit[N_TUTOR] (the bit of kTutorCompat, 0xFF = a tutor this table leaves out), kTutorCompat[N_SPECIES] (u32: one
 * bit per tutor, all 30: the 10 town tutors and the Frontier's 20 BP tutors, frontier_core 2026-10-12) */
#include "emerald_mech_data.h"

static void *party_of(void *env) { return GameData_GetParty(FieldScriptEnv_GetGameData(env)); }

u32 EM_CmdPartySwap(void *vm, void *env) {
    void *party = party_of(env);
    u32 a = ScriptReadAny(vm, env) & 0xffff;
    u32 b = ScriptReadAny(vm, env) & 0xffff;
    u32 n = PokeParty_GetPkmCount(party);
    if (a != b && a < n && b < n) PokeParty_SwapPkms(party, a, b, FieldScriptEnv_GetHeapID(env));
    return 0;
}

u32 EM_CmdTutorCheck(void *vm, void *env) {
    void *party = party_of(env);
    u16 *var = ScriptReadVar(vm, env);
    u32 slot = ScriptReadAny(vm, env) & 0xffff;
    u32 tutor = ScriptReadAny(vm, env) & 0xffff;
    void *pkm;
    u32 species, move, i;
    *var = 1;
    if (slot >= PokeParty_GetPkmCount(party) || tutor >= N_TUTOR || kTutorBit[tutor] == 0xFF) return 0;
    pkm = PokeParty_GetPkm(party, slot);
    if (PokeParty_GetParam(pkm, PKM_PARAM_IS_EGG, 0)) return 0;
    species = PokeParty_GetParam(pkm, PKM_PARAM_SPECIES, 0);
    if (species >= N_SPECIES || !((kTutorCompat[species] >> kTutorBit[tutor]) & 1)) return 0;
    move = kTutorMove[tutor];
    for (i = 0; i < 4; i++)
        if (PokeParty_GetParam(pkm, PKM_PARAM_MOVE1 + i, 0) == move) { *var = 2; return 0; }
    *var = 0;
    return 0;
}

void EM_SetTrainer2v2(void *setup, void *gd, void *status, u32 partner, u32 foe1, u32 foe2, u32 heap) {
    void *party;
    u32 keep = (partner >> PARTNER_KEEP_SHIFT) & 0xF;      /* how many of the player's Pokémon battle (1-3) */
    if (keep == 0 || keep > MULTI_PARTY_SIZE) keep = MULTI_PARTY_SIZE;
    BtlSetup_SetTrainer2v2(setup, gd, status, partner & PARTNER_ID_MASK, foe1, foe2, heap);
    party = *(void **)((u8 *)setup + BTLSETUP_PARTY0);
    while (PokeParty_GetPkmCount(party) > keep) PokeParty_RemovePkm(party, PokeParty_GetPkmCount(party) - 1);
}

void EM_PartyCopyBack(void *battle, void *player) {
    u32 n = PokeParty_GetPkmCount(battle), i, k;
    if (n >= PokeParty_GetPkmCount(player)) { PokeParty_Copy(battle, player); return; }
    for (i = 0; i < n; i++) {
        const u32 *s = (const u32 *)PokeParty_GetPkm(battle, i);
        u32 *d = (u32 *)PokeParty_GetPkm(player, i);
        for (k = 0; k < PKM_WORDS; k++) d[k] = s[k];
    }
}

typedef struct { void *gsys; u16 *out; u32 index; u32 result; u8 picked[8]; } PickWork;

u32 EM_PickCallback(void *event, u32 *state, void *data) {
    PickWork *w = data;
    u32 i, n = 0, cancelled;
    if (*state == 0) {
        void *gd = GSYS_GetGameData(w->gsys);
        void *inner = TeamSelect_Create(w->gsys, PICK_STYLE, PICK_MODE, PICK_REGULATION, GameData_GetParty(gd), w->picked,
                                        &w->index, &w->result, 0);
        u8 *reg = (u8 *)GameEvent_GetData(inner) + REG_OFFSET;
        u8 *picked = (u8 *)GameEvent_GetData(inner) + PICKED_OFFSET;
        for (i = REG_ITEM_BANS; i < REG_ITEM_BANS_END; i++) reg[i] = 0;   /* no banned items (file 22 bans the
                                                                               Soul Dew; Emerald bans none) */
        if (w->out[0] & PICK_FRONTIER) {                    /* the Battle Frontier (fr_pick_party) */
            reg[2] = reg[3] = (u8)(w->out[0] & 7);
            reg[4] = (w->out[0] & PICK_LV50) ? 50 : 0;      /* Lv. 50: level mode 2, "50 or less" (arc 106 file 38, */
            reg[5] = (w->out[0] & PICK_LV50) ? 2 : 0;       /* the Battle Tower's Lv. 50); Open Level: no level rule */
            reg[8] = 0;                                     /* no species / held item twice, as every Subway rule */
            reg[9] = 0;                                     /* of arc 106; file 22's banned species stay */
        } else {                                            /* the tag battle: Emerald's ChooseHalfPartyForBattle lets */
            reg[2] = 1;      /* any Pokémon but an Egg or a fainted one join: at least 1 (GetMinBattleEntries) */
            reg[3] = 3;      /* at most MULTI_PARTY_SIZE */
            reg[4] = 0;      /* no level rule (GetBattleEntryLevelCap: MAX_LEVEL), as arc 106's files 5-9 */
            reg[5] = 0;
            reg[8] = 1;      /* duplicates allowed: arc 106's free-battle files 0-9 have 1 here, every Subway rule 0 */
            reg[9] = 1;
            for (i = REG_SPECIES_BANS; i < REG_ITEM_BANS; i++) reg[i] = 0;   /* no banned species (file 22 bans the */
        }                                                                    /* Subway's 25 legends) */
        if (w->out[0] & PICK_KEEP)
            for (i = 0; i < (w->out[0] & 3u); i++) picked[i] = (u8)(w->out[1 + i] + 1);
        GameEvent_ChainNext(event, inner);
        *state = 1;
        return 0;
    }
    cancelled = w->result == 0 && (w->index == PICK_CANCEL_A || w->index == PICK_CANCEL_B);
    w->out[1] = w->out[2] = w->out[3] = 255;
    for (i = 0; i < 6 && n < MULTI_PARTY_SIZE; i++)
        if (w->picked[i] >= 1 && w->picked[i] <= 6) w->out[1 + n++] = w->picked[i] - 1;
    w->out[0] = (u16)(n | (cancelled && n ? PICK_CANCELLED : 0));
    return 1;
}

u32 EM_CmdPickParty(void *vm, void *env) {
    u16 *out = ScriptReadVar(vm, env);
    void *gsys = FieldScriptEnv_GetGameSystem(env);
    void *event = GameEvent_Create(gsys, 0, EM_PickCallback, sizeof(PickWork));
    PickWork *w = GameEvent_GetData(event);
    u32 i;
    w->gsys = gsys;
    w->out = out;
    w->index = 0;
    w->result = 0;
    for (i = 0; i < 8; i++) w->picked[i] = 0;
    ScriptWork_CallEvent(FieldScriptEnv_GetScriptWork(env), event);
    return 1;
}

/* ---- Emerald's crisis weather (emerald_ch10, 2026-10-12; notes/EMERALD.md "Phase 4 mechanics") --------------------
 * pokeemerald: once Archie wakes Kyogre (FLAG_SYS_WEATHER_CTRL) the crisis maps call Common_EventScript_SetAbnormalWeather
 * (WEATHER_ABNORMAL: Task_DoAbnormalWeather swaps WEATHER_DOWNPOUR and WEATHER_DROUGHT every 600 frames, the phase kept
 * across maps in sCurrentAbnormalWeather); Routes 129-131 and Sky Pillar's outside only from VAR_SOOTOPOLIS_CITY_STATE 4;
 * Sootopolis has the downpour alone at state 1 and while VAR_SKY_PILLAR_STATE is 1 (Rayquaza on its way). The user's
 * choice (DECISIONS 2026-10-12): the two looks are Sapphire NDS's Kyogre rainstorm and Ruby NDS's Groudon drought.
 *   EM_ZoneWeather replaces GetEntralinkWeatherIfApplicable (arm9 0x02032fb8, the hook patches/weather.py fills for
 *       Sapphire / Ruby; in an Emerald build its first bytes jump here): GetWeatherAll asks it for a zone's weather on
 *       every zone change (ResetWeather), for FieldSetWeather 0xFFFF and for the lens flare. It gives the day-by-day
 *       cycles of Route 119 / 123 (weather.py's, same rule) and the crisis weather of kCrisis' zones, else 0xFFFF.
 *   EM_WeatherTick: ov036 FieldG3D_Update's call of FieldWeather_Update (every field frame) goes through it: every
 *       EMW_PERIOD calls, in a zone whose rule is the alternating one, the weather swaps (SetNowWeather + the weather
 *       system's own change, func_ov036_02199208, as Field_SwapWeather does on a zone change: it waits while a change
 *       is under way). gEmPhase keeps the phase for the next zone (pokeemerald's sCurrentAbnormalWeather). */
#define GameData_GetEventWork  FN(void *(*)(void *), 0x02017394)
#define EventWork_FlagGet      FN(u32 (*)(void *, u32), 0x020191ac)
#define EventWork_GetWkPtr     FN(u16 *(*)(void *, u32), 0x02019294)
#define GetNowWeather          FN(u32 (*)(void *), 0x020173bc)
#define SetNowWeather          FN(void (*)(void *, u32), 0x020173c8)
#define RTC_GetCachedDate      FN(void (*)(void *), 0x0204424c)
#define RTC_ConvertDateToDay   FN(u32 (*)(void *), 0x0207d0b4)
#define FieldWeather_Update    FN(void (*)(void *, u32), 0x02199120)
#define FieldWeather_Change    FN(u32 (*)(void *, u32), 0x02199208)
#define FIELD_GAMEDATA         8          /* Field: gameData (include/field/field_internal.h) */
#define FIELD_PLAYER_ZONE      232        /* Field_GetPlayerStateZoneID (ov036 0x021804d8): playerZoneState.zoneId */
#define EMW_NONE 0                        /* rules: no crisis weather here now */
#define EMW_DOWNPOUR 1
#define EMW_ABNORMAL 2

/* the phase (the weather shown in an alternating zone now) and the frame count: words in the code's own ITCM */
__asm__(".text\n\t.align 2\n\t.global gEmPhase\ngEmPhase:\n\t.word 0\n\t.global gEmTick\ngEmTick:\n\t.word 0\n");
extern volatile u32 gEmPhase, gEmTick;

static u32 em_crisis_rule(void *gd, u32 zone) {
    const u16 *t;
    u32 kind = 0;
    void *ew;
    for (t = kEmCrisis; t[0]; t += 2)
        if (t[0] == zone) { kind = t[1]; break; }
    if (!kind || !gd) return EMW_NONE;
    ew = GameData_GetEventWork(gd);
    if (!EventWork_FlagGet(ew, EMW_FLAG)) return EMW_NONE;
    if (kind == 2 && *EventWork_GetWkPtr(ew, EMW_STATE) < 4) return EMW_NONE;     /* Routes 129-131, Sky Pillar */
    if (kind == 3 && (*EventWork_GetWkPtr(ew, EMW_STATE) == 1 || *EventWork_GetWkPtr(ew, EMW_SKY) == 1))
        return EMW_DOWNPOUR;                                                        /* Sootopolis */
    return EMW_ABNORMAL;
}

static u32 em_phase(void) { return gEmPhase == EMW_DROUGHT_ID ? EMW_DROUGHT_ID : EMW_RAIN_ID; }

u32 EM_ZoneWeather(void *gsys, void *gd, u32 zone) {
    const u8 *c;
    u8 date[16];
    u32 rule;
    zone &= 0xffff;
    for (c = kEmCycles; c[0] | c[1]; c += 6)                  /* u16 zone, u8 weather[4] (the day's step, & 3) */
        if ((u32)(c[0] | c[1] << 8) == zone) {
            RTC_GetCachedDate(date);
            return c[2 + (RTC_ConvertDateToDay(date) & 3)];
        }
    rule = em_crisis_rule(gd, zone);
    if (rule == EMW_DOWNPOUR) return EMW_RAIN_ID;
    if (rule == EMW_ABNORMAL) return em_phase();
    return 0xffff;
}

void EM_WeatherTick(void *ws, u32 heap, void *field) {
    void *gd;
    u32 next;
    FieldWeather_Update(ws, heap);
    if (++gEmTick < EMW_PERIOD) return;
    gEmTick = 0;
    gd = *(void **)((u8 *)field + FIELD_GAMEDATA);
    if (em_crisis_rule(gd, *(u16 *)((u8 *)field + FIELD_PLAYER_ZONE)) != EMW_ABNORMAL) return;
    next = GetNowWeather(gd) == EMW_RAIN_ID ? EMW_DROUGHT_ID : EMW_RAIN_ID;
    gEmPhase = next;
    SetNowWeather(gd, next);
    FieldWeather_Change(ws, next);
}

/* the call site's registers: r0 the weather system, r1 the heap, r5 the Field (FieldG3D_Update keeps it there) */
__attribute__((naked)) void EM_WeatherTickShim(void) {
    __asm__ volatile("push {lr}\n\tadds r2, r5, #0\n\tbl EM_WeatherTick\n\tpop {pc}\n");
}
