/* Pokémon Emerald NDS: Emerald's rematches (emerald_rematch, 2026-10-18; notes/EMERALD_REMATCH.md). Emerald builds only:
 * b2tools/patches/emerald_rematch.py compiles this file into the Frontier code area (b2tools/patches/frontier_area.py:
 * main RAM, loaded at boot, resident in battles too; .bss allowed) and points Black 2's calls at it.
 *
 * Black 2's trainer table is full (814 ids, notes/EMERALD_PLAN.md 1.3), so Emerald's 288 rematch tiers are not trainers:
 * each tier is a "rematch slot" (data/emerald/hoenn_rematch.json), its 20-byte record in a/0/8/9 file 1 (slot * 20) and its
 * party in a/0/9/2 entry RM_PARTY_BASE + slot. A rematch battles the first battle's own trainer id (name, picture, NPC
 * and flag stay its own); while it is armed (EmRematch RM_ARM, right before CallTrainerBattle) Black 2's two readers of
 * trainer data load the slot instead:
 *   EM_RmReadTrainerData: arm9 TrainerData_ReadTrainerData (0x020306e0; every reader of a/0/9/1 goes through it:
 *       TrainerUtil_LoadTrainer / LoadParty, TrainerData_GetParam: class, battle style, prize money in battle);
 *   EM_RmReadParty: arm9 TrainerData_ReadParty (0x02030724, TrainerUtil_LoadParty's party, 108-byte buffer);
 *   EM_RmMsgLoad: the battle's trainer-line call (trainers.py's rewrite of ov167 0x021d0288; the call frontier_pike and
 *       frontier_pyramid chain onto, NEXT_MSGLD = the hook it pointed at): type 1 (the defeat line) becomes Emerald's
 *       rematch defeat line, type RM_MSG_DEFEAT of the same trainer.
 * Disarmed right after the battle (RM_DISARM), and by every boot / soft reset (.bss).
 *
 *   command 299 (Black 2's BMAnmPlayInv, unused by every Black 2 and Hoenn script; args any, any, any read as var, any,
 *   any; EVCMD_PERM_TABLE 3, kept): EmRematch var, op, arg -> EM_RmCmd (src/include/hoenn_rematch.inc names the ops)
 *
 * When a rematch is offered (HoennB2's trigger for Emerald's Match Call, which Black 2 does not have):
 *   route trainers: 5 badges or more (Emerald's rule for any rematch: battle_setup.c HasAtLeastFiveBadges, match_call.c
 *       GetNumOwnedBadges); the tier follows the badges: 5 -> tier 2, 6 -> 3, 7 -> 4, 8 -> 5 (Emerald gives the next
 *       tier after each rematch; see the note);
 *   Gym Leaders: after the Hall of Fame (gym_leader_rematch.c: FLAG_SYS_GAME_CLEAR), tiers 2-5 in turn (2 bits a Leader
 *       in W_LEADERS), the fifth again after it; before Wattson's New Mauville job only the first rematch and none with
 *       Wattson (Emerald's FLAG_WATTSON_REMATCH_AVAILABLE, set after his Thunderbolt TM: F_WATTSON);
 *   post-game rows (gym 9 + n; 9 = Wally at Victory Road's exit, whose first battle is post-game too): after the Hall of
 *       Fame, tiers in turn as a Leader's (2 bits a row in W_POSTGAME), no Wattson rule;
 *   each trainer once a day: a bit per row in kDoneWork[], cleared when Black 2's midnight reset has cleared F_DAILY. */
typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;

#define FN(type, addr) ((type)((addr) | 1))
#define GFL_ArcSysRead             FN(void (*)(void *, u32, u32), 0x0204a928)
#define GFL_ArcSysReadRange        FN(void (*)(void *, u32, u32, u32, u32), 0x0204a940)
#define ScriptReadVar              FN(u16 *(*)(void *, void *), 0x021548e8)
#define ScriptReadAny              FN(u32 (*)(void *, void *), 0x02154910)
#define FieldScriptEnv_GetGameData FN(void *(*)(void *), 0x02155174)
#define GameData_GetEventWork      FN(void *(*)(void *), 0x02017394)
#define EventWork_FlagGet          FN(u32 (*)(void *, u32), 0x020191ac)
#define EventWork_FlagSet          FN(void (*)(void *, u32), 0x020191d8)
#define EventWork_GetWkPtr         FN(u16 *(*)(void *, u32), 0x02019294)
#define SaveControl_GetInstance    FN(void *(*)(void), 0x020072fc)
#define getTrainerGameInfoAddress  FN(void *(*)(void *), 0x0200c838)
#define isBadgeObtained            FN(u32 (*)(void *, u32), 0x0200c97c)

#define ARC_TRDATA 91
#define ARC_TRPOKE 92
#define ARC_TRMSG  89
#define TRDATA_SIZE 20
#define BATTLE_INST_FIRST 0x500    /* TrainerData_ReadTrainerData: ids from here are the Battle Institute's */

#define RM_QUERY   0
#define RM_ARM     1
#define RM_DISARM  2
#define RM_WON     3
#define RM_MSGBASE 4
#define RM_NONE    0
#define RM_SINGLE  1
#define RM_DOUBLE  2
#define RM_POST    3

/* emerald_rematch_data.h (written by emerald_rematch.py): N_ROWS, RM_PARTY_BASE, RM_TRDATA_FILE, F_DAILY, F_GAME_CLEAR,
 * F_WATTSON, GYM_WATTSON, W_LEADERS, W_POSTGAME, MSG_DEFEAT, MSG_INTRO, MSG_INTRO2, NEXT_MSGLD, kDoneWork[], kRows[] (RmRow) */
typedef struct { u16 trainer, partner; u8 gym, dbl; u16 slot[4]; } RmRow;   /* slot 0xFFFF: no such tier */
#include "emerald_rematch_data.h"

static u16 sArmA, sSlotA, sArmB, sSlotB;    /* the armed rematch: trainer ids and their slot + 1 (0: not armed) */

static u32 armed(u32 id) {
    if (sSlotA && id == sArmA) return sSlotA;
    if (sSlotB && id == sArmB) return sSlotB;
    return 0;
}

void EM_RmReadTrainerData(u32 id, void *buf) {
    u32 s = armed(id), d;
    if (s) { GFL_ArcSysReadRange(buf, ARC_TRMSG, RM_TRDATA_FILE, (s - 1) * TRDATA_SIZE, TRDATA_SIZE); return; }
    if (id < BATTLE_INST_FIRST) { GFL_ArcSysRead(buf, ARC_TRDATA, id); return; }
    d = id - BATTLE_INST_FIRST;                                 /* (Black 2's own rule, unchanged) */
    GFL_ArcSysRead(buf, ARC_TRDATA, d >= 620 && d < 640 ? 661 : 660);
}

void EM_RmReadParty(u32 id, void *buf) {
    u32 s = armed(id);
    GFL_ArcSysRead(buf, ARC_TRPOKE, s ? RM_PARTY_BASE + s - 1 : id);
}

void EM_RmMsgLoad(u32 id, u32 type, void *strbuf, u32 heap) {
    if (type == 1 && armed(id)) type = MSG_DEFEAT;
    FN(void (*)(u32, u32, void *, u32), NEXT_MSGLD)(id, type, strbuf, heap);
}

static int row_of(u32 id) {
    int i;
    for (i = 0; i < N_ROWS; i++) if (kRows[i].trainer == id) return i;
    return -1;
}

static u32 badges(void) {
    void *info = getTrainerGameInfoAddress(SaveControl_GetInstance());
    u32 i, n = 0;
    for (i = 0; i < 8; i++) n += isBadgeObtained(info, i) != 0;
    return n;
}

static u16 *done_word(void *ew, int r) { return EventWork_GetWkPtr(ew, kDoneWork[r >> 4]); }

/* the tiers row r's trainer has beaten (0-3): 2 bits a Gym in W_LEADERS (gym 1-8), a post-game row in W_POSTGAME (gym 9 + n) */
static u16 *progress_word(void *ew, u32 gym, u32 *shift) {
    *shift = 2 * (gym <= 8 ? gym - 1 : gym - 9);
    return EventWork_GetWkPtr(ew, gym <= 8 ? W_LEADERS : W_POSTGAME);
}
static u32 tiers_beaten(void *ew, u32 gym) { u32 sh; return *progress_word(ew, gym, &sh) >> sh & 3; }

/* The tier (0-3: Emerald's tiers 2-5) row r is fought at now, or -1; *state = RM_* */
static int tier_now(void *ew, int r, u32 *state) {
    const RmRow *w = &kRows[r];
    int i;
    u32 k;
    *state = RM_NONE;
    if (!EventWork_FlagGet(ew, F_DAILY)) {                      /* a new day: nobody has been fought today */
        for (k = 0; k < sizeof(kDoneWork) / sizeof(kDoneWork[0]); k++) *EventWork_GetWkPtr(ew, kDoneWork[k]) = 0;
        EventWork_FlagSet(ew, F_DAILY);
    }
    if (*done_word(ew, r) >> (r & 15) & 1) { *state = RM_POST; return -1; }
    if (w->gym == 0) {
        u32 b = badges();
        if (b < 5) return -1;
        i = b - 5 > 3 ? 3 : (int)(b - 5);
    } else {
        u32 p;
        if (!EventWork_FlagGet(ew, F_GAME_CLEAR)) return -1;
        p = tiers_beaten(ew, w->gym);
        if (w->gym <= 8 && !EventWork_FlagGet(ew, F_WATTSON)) {
            if (w->gym == GYM_WATTSON) return -1;
            if (p >= 1) { *state = RM_POST; return -1; }
        }
        i = (int)p;
    }
    while (i > 0 && w->slot[i] == 0xFFFF) i--;
    if (w->slot[i] == 0xFFFF) return -1;
    *state = (w->dbl >> i & 1) ? RM_DOUBLE : RM_SINGLE;
    return i;
}

u32 EM_RmCmd(void *vm, void *env) {
    u16 *var = ScriptReadVar(vm, env);
    u32 op = ScriptReadAny(vm, env) & 0xffff;
    u32 arg = ScriptReadAny(vm, env) & 0xffff;
    void *ew = GameData_GetEventWork(FieldScriptEnv_GetGameData(env));
    int r = op == RM_DISARM || op == RM_MSGBASE ? -1 : row_of(arg), i;
    u32 state;
    *var = 0;
    switch (op) {
    case RM_QUERY:
        if (r >= 0) { tier_now(ew, r, &state); *var = state; }
        break;
    case RM_ARM:
        sSlotA = sSlotB = 0;
        if (r < 0 || (i = tier_now(ew, r, &state)) < 0) break;
        sArmA = arg; sSlotA = kRows[r].slot[i] + 1;
        if (kRows[r].partner) { sArmB = kRows[r].partner; sSlotB = sSlotA + 1; }   /* Liza: the slot after Tate's */
        *var = 1;
        break;
    case RM_DISARM:
        sArmA = sSlotA = sArmB = sSlotB = 0;
        break;
    case RM_WON:
        if (r < 0) break;
        *done_word(ew, r) |= 1 << (r & 15);
        if (kRows[r].gym) {
            u32 sh, p = tiers_beaten(ew, kRows[r].gym);
            u16 *w = progress_word(ew, kRows[r].gym, &sh);
            if (p < 3) *w = (*w & ~(3 << sh)) | (p + 1) << sh;
        }
        *var = 1;
        break;
    case RM_MSGBASE:
        *var = arg == 7 ? MSG_INTRO2 : MSG_INTRO;
        break;
    }
    return 0;
}
