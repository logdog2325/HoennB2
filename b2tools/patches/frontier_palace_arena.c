/* The Battle Palace and the Battle Arena (frontier_palace_arena, 2026-10-12; notes/FRONTIER_PALACE_ARENA.md): Pokémon
 * Emerald NDS only. Built by b2tools/patches/frontier_palace_arena.py and linked into the Frontier code area (main RAM,
 * b2tools/patches/frontier_area.py), which also writes frontier_pa_data.h (the k* tables and PA_* constants, read from
 * pokeemerald and data/emerald/frontier.json at build time).
 *
 * Field side: script command 291 (Black 2's BoxAddEx, unused) = FrontierPA (src/field_scripts/scenes/frontier_pa_lib.inc):
 *   the opponent (Emerald's GetRandomScaledFrontierTrainerId, never twice in a challenge, or the Brain at Emerald's
 *   streaks), its name and greeting, the Brain's status, the battle (Black 2's Battle Subway battle set up as the
 *   Factory/Dome's: SetupTrialHouseBattle, then the player's three as they are and the opponent's party built here by
 *   Emerald's FillFrontierTrainerParty / CreateFrontierBrainPokemon), its result.
 * Battle side (hooks in ov167, the battle overlay; each does Black 2's own thing outside a Palace/Arena battle):
 *   Palace: the player's FIGHT and the opponents' AI choose by Nature (ChooseMoveAndTargetInBattlePalace: the Attack /
 *     Defense / Support weights above and at or below half HP, the move then picked by Black 2's trainer AI among that
 *     group's moves, as Emerald's AI among selectedMoves; no group move: a random usable move, and half the time
 *     "appears incapable of using its power!"; the doubles target by Nature); the flavor text once a Pokémon is at half
 *     HP or less ("A glint appears in X's eyes!" ...).
 *   Arena: no switching (the player: "can't be switched out!", the AI never switches, the next Pokémon comes in by
 *     party order), Mind (sMindRatings per move used), Skill (the move's result: super effective +2, not very
 *     effective -1, no effect / missed / already statused -2, a defending Ability blocking -3, otherwise +1), Body (HP
 *     left of the HP at the matchup's start); after the third turn of a matchup with both standing, the referee's
 *     judgment and the loser (or both) faints.
 * Battle texts are std messages with ids 0x4000 | line (the Palace battle room's text) and 0x6000 | line (the Arena
 * battle room's): PA_StdString loads them instead of Black 2's battle message file. */
typedef unsigned char u8;
typedef signed char s8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef signed int s32;
typedef unsigned long long u64;

#define FN(type, addr) ((type)((addr) | 1))
/* ---- arm9 */
#define GFL_HeapAllocate           FN(void *(*)(u32, u32, u32, u32, u32), 0x0203a1fc)
#define GFL_HeapFree               FN(void (*)(void *), 0x0203a24c)
#define GFL_HeapGetFreeSize        FN(u32 (*)(u32), 0x0203a2a8)
#define GFL_RandomLC               FN(u32 (*)(u32), 0x02005748)
#define GFL_ArcSysReadRange        FN(void (*)(void *, u32, u32, u32, u32), 0x0204a940)
#define GFL_MsgSysLoadData         FN(void *(*)(u32, u32, u32, u32), 0x0204875c)
#define GFL_MsgDataLoadStrbuf      FN(void (*)(void *, u32, void *), 0x02048838)
#define GFL_MsgDataFree            FN(void (*)(void *), 0x020487d4)
#define GFL_StrBufCreate           FN(void *(*)(u32, u32), 0x02048530)
#define GFL_StrBufFree             FN(void (*)(void *), 0x02048564)
#define GFL_StrBufStoreString      FN(void (*)(void *, u16 *, u32), 0x020486b8)
#define WordSet_LoadStrbuf         FN(void (*)(void *, u32, void *, u32, u32, u32), 0x0202437c)
#define WordSet_ExpandStr          FN(void (*)(void *, void *, void *), 0x02024920)
#define GSYS_GetGameData           FN(void *(*)(void *), 0x02016ad8)
#define GSYS_GetField              FN(void *(*)(void *), 0x02016af0)
#define GameEvent_Create           FN(void *(*)(void *, void *, void *, u32), 0x02016cb4)
#define GameEvent_ChainNext        FN(void (*)(void *, void *), 0x02016d68)
#define GameEvent_GetData          FN(void *(*)(void *), 0x02016edc)
#define GameData_GetParty          FN(void *(*)(void *), 0x0201735c)
#define GameData_GetSaveControl    FN(void *(*)(void *), 0x02017934)
#define SaveControl_GetBlockPtr    FN(void *(*)(void *, u32), 0x02007448)
#define PokeParty_Create           FN(void *(*)(u32), 0x0201fd00)
#define PokeParty_InitCore         FN(void (*)(void *, u32), 0x0201fd34)
#define PokeParty_AddPkm           FN(u32 (*)(void *, void *), 0x0201fd6c)
#define PokeParty_GetPkm           FN(void *(*)(void *, u32), 0x0201ff08)
#define PokeParty_GetPkmCount      FN(u32 (*)(void *), 0x0201fdf8)
#define PokeParty_Copy             FN(void (*)(void *, void *), 0x020200ac)
#define PokeParty_GetParam         FN(u32 (*)(void *, u32, void *), 0x0201ccf8)
#define PokeParty_SetParam         FN(void (*)(void *, u32, u32), 0x0201cd1c)
#define PokeParty_SetMove          FN(void (*)(void *, u32, u32), 0x0201d224)
#define PokeParty_SetNature        FN(void (*)(void *, u32), 0x0201d5e0)
#define PokeParty_RecalcStats      FN(void (*)(void *), 0x0201d5f4)
#define PokeParty_CreatePkm        FN(void (*)(void *, u32, u32, u32, u32, u32, u32, u32), 0x0201c464)
#define PokeParty_GetPkmRawSize    FN(u32 (*)(void), 0x0201c2c8)
#define BtlSetup_Free              FN(void (*)(void *), 0x02017c84)
#define VSPlayerBlk_Alloc          FN(void (*)(u32), 0x0200bb24)
#define FreeVSPlayerBlk            FN(void (*)(void), 0x0200bb48)
/* ---- ov012 (the field script overlay) */
#define FieldScriptEnv_GetGameData   FN(void *(*)(void *), 0x02155174)
#define FieldScriptEnv_GetGameSystem FN(void *(*)(void *), 0x0215516c)
#define FieldScriptEnv_GetScriptWork FN(void *(*)(void *), 0x02155184)
#define ScriptWork_CallEvent       FN(void (*)(void *, void *), 0x02153880)
#define ScriptWork_GetWordSet      FN(void *(*)(void *), 0x02153ec4)
#define ScriptReadAny              FN(u32 (*)(void *, void *), 0x02154910)
#define ScriptReadVar              FN(u16 *(*)(void *, void *), 0x021548e8)
#define SubwayPkm_FromSet          FN(void (*)(void *, u32, u32, u32, u32, u32, u32, u32, u32), 0x02162490)
#define SetupTrialHouseBattle      FN(void *(*)(void *, void *, u32, void *, void *, u32), 0x02161fc4)
#define BattleCall_Create          FN(void *(*)(void *, void *, void *), 0x0216881c)
/* ---- ov167 (the battle) */
#define GetBattleMonStat           FN(u32 (*)(void *, u32), 0x021bb1b4)
#define GetBattleMonStatus         FN(u32 (*)(void *), 0x021bbaa8)
#define GetMonID                   FN(u32 (*)(void *), 0x021bac40)
#define IsFainted                  FN(u32 (*)(void *), 0x021bb368)
#define MoveGetID                  FN(u32 (*)(void *, u32), 0x021bacc0)
#define GetMovePP                  FN(u32 (*)(void *, u32), 0x021bad84)
#define GetBattleMonMoveCount      FN(u32 (*)(void *), 0x021bac48)
#define GetSrcData                 FN(void *(*)(void *), 0x021bb044)
#define GetClientMon               FN(void *(*)(void *, u32, u32), 0x0219d1e8)    /* (pokeCon, client, slot) */
#define MonIDToBattlePos           FN(u32 (*)(void *, void *, u32), 0x0219c5f8)
#define BattlePosToClientID        FN(u32 (*)(void *, u32), 0x0219c650)
#define GetClientSide              FN(u32 (*)(void *, u32), 0x0219c430)
#define BtlSetup_GetBattleStyle    FN(u32 (*)(void *), 0x0219bd80)
#define DecideMoveTargetAuto       FN(u32 (*)(void *, void *, void *, u32, void *), 0x021bda20)
#define BattleAction_SetFightParam FN(void (*)(u32 *, u32, u32), 0x021bdaf8)
#define CheckCondition             FN(u32 (*)(void *, u32), 0x021bbac4)
#define Btlv_StringParam_Setup     FN(void (*)(void *, u32, u32), 0x021d0aec)
#define StoreSelectableMoveFlag    FN(u32 (*)(void *, void *, u8 *), 0x021b4a24)
#define CheckForSelectableMove     FN(u32 (*)(void *, void *, u32 *), 0x021b472c)
#define ActionSelectFight          FN(u32 (*)(void *, u32 *), 0x021b3c00)
#define Client_SetProc             FN(void (*)(void *, u32), 0x021b2168)
#define PROC_ACTION_DECIDED        0x021b4429                                     /* func_ov167_021b4428 (Thumb) */
#define AISwitchChecks             FN(u32 (*)(void *, void *, u32, u8 *), 0x021b4df8)
#define PickBestMonToSwitchInto    FN(u32 (*)(void *, u8 *, u32), 0x021b5c4c)
#define ChangeProcUI5              FN(u32 (*)(void *, u32 *), 0x021b5fa4)
#define ChangeProcUI6              FN(u32 (*)(void *, u32 *), 0x021b5fb0)
#define ChangeProcAI               FN(u32 (*)(void *, u32 *), 0x021b5fbc)
#define AiFlagsOf                  FN(u32 (*)(void *, u32), 0x0219d8d4)
#define AiVmParam                  FN(void *(*)(void *), 0x0219e158)
#define TrAI_CreateVM              FN(void *(*)(void *, void *, void *, u32, u32), 0x0217f600)
#define TrAI_Think                 FN(u32 (*)(void *), 0x0217f6b0)
#define TrAI_Setup                 FN(void (*)(void *, u8 *, u32), 0x0217f7bc)
#define TrAI_GetChosenMove         FN(u32 (*)(void *), 0x0217f834)
#define TrAI_GetChosenTarget       FN(u32 (*)(void *), 0x0217f840)
#define TurnStart_ResetFlags       FN(void (*)(void *), 0x0219f6fc)
#define CheckObedience             FN(u32 (*)(void *, void *), 0x021a0a44)
#define MoveFailMessage            FN(void (*)(void *, void *, u32, u32), 0x021a3fc4)
#define ServerFight                FN(void (*)(void *, void *, u32 *, u32), 0x021a1940)
#define MovePrecheck               FN(u32 (*)(void *, void *, u32, u32), 0x021a3ac0)
#define TurnEnd                    FN(u32 (*)(void *), 0x021a7f1c)
#define ServerControl_FaintPokemon FN(void (*)(void *, void *), 0x021a5dc4)
#define ServerControl_CheckMatchup FN(u32 (*)(void *), 0x0219fd04)
#define SCQUE_PutMsg               ((void (*)(void *, u32, u32, ...))0x021b15d1)    /* (queue, 0x5a std, id, args..., 0xffff0000) */
#define StdString_Make             FN(void (*)(void *, u32, void *), 0x021d4f64)
#define StdString_Args             FN(void (*)(void *, void *, void *), 0x021d507c)
#define BTL_STR                    ((u8 *)0x021dd87c)                                /* +8 wordset, +12 temp strbuf */

#define ARC_SETS 211
#define ARC_SCRIPT_TEXT 3
#define HEAP_TAIL 0x8004                       /* the game-event heap, from its end (as the Subway's own) */
#define P_SPECIES 0x05
#define P_ITEM 0x06
#define P_HAPPY 0x09
#define P_EV_HP 0x0d
#define P_IS_EGG 0x4c
#define P_NATURE 0x70
#define P_LEVEL 0x9e
#define P_HP 0xa0
#define P_MAXHP 0xa1
#define MOVE_FRUSTRATION 218
#define MOVE_PROTECT 182
#define MOVE_DETECT 197
#define ST_SLEEP 2
#define SETUP_PARTY0 0x24
#define SETUP_PARTY1 0x28
#define SETUP_RESULT 0xa8
#define TRAINER_PKM 0x30
#define PKM_SIZE 60

/* frontier_core's record keys (notes/FRONTIER.md 2.2): u16[96] after Black 2's 60 bytes of save block 0x38 */
#define FR_PLAY_BLOCK 0x38
#ifdef FR_REC_OFF                              /* HOENN_SAVE_COMPAT=1 (save_compat.py, notes/SAVE_PKHEX.md): 64 */
#define FR_AREA_OFF FR_REC_OFF
#else
#define FR_AREA_OFF 60
#endif
#define K_STATUS 0
#define K_FACILITY 1
#define K_BATTLE_MODE 2
#define K_LVL 3
#define K_PARTY 4
#define K_BATTLE_NUM 5
#define K_SYMBOLS 6
#define K_STREAK(f, m, l) (16 + 8 * (f) + 4 * (m) + 2 * (l))
#define K_PA_OPP 9                             /* ours (notes/FRONTIER.md 6): bits 0-9 the opponent (PA_BRAIN = the Brain),
                                                  bit 14 Spenser's first speech heard, bit 15 Greta's; bits 12 / 13
                                                  Anabel's (the Battle Tower, below: her first / her Gold intro) */
#define K_PA_MET 11                            /* 11-14: the trainers met in this challenge, 6 x 9 bits */
#define K_TENT_OPP 44                          /* battle_tents (notes/FRONTIER.md 6): bits 0-4 the tent's opponent (0-29),
                                                  5-9 / 10-14 the trainers of the challenge's 1st / 2nd battle */
#define FAC_TENT 0x10                          /* FrontierPA's facility | FAC_TENT: the Verdanturf (Palace rules) or the
                                                  Fallarbor (Arena rules) Battle Tent (battle_tents 2026-10-18) */
#define FAC_PALACE 2
#define FAC_ARENA 3
#define PA_BRAIN 1023

#include "frontier_pa_data.h"

/* compiler helpers -> Black 2's own ARM division routines (quotient r0, remainder r1) */
u32 __aeabi_uidiv(u32 a, u32 b) { return (u32)((u64 (*)(u32, u32))0x0208d868)(a, b); }
u64 __aeabi_uidivmod(u32 a, u32 b) { return ((u64 (*)(u32, u32))0x0208d868)(a, b); }
s32 __aeabi_idiv(s32 a, s32 b) { return (s32)((u64 (*)(s32, s32))0x0208d65c)(a, b); }
u64 __aeabi_idivmod(s32 a, s32 b) { return ((u64 (*)(s32, s32))0x0208d65c)(a, b); }

/* ================================================================================================ state */
enum { RULE_NONE, RULE_PALACE, RULE_ARENA };
#define R_SE 1
#define R_NVE 2
#define R_NOEFF 4
#define R_PROTECT 8
#define R_ALREADY 16
#define R_POPUP 32
#define R_HIT 64
typedef struct {
    u8 rule, doubles;
    /* Palace, per monId */
    u8 low[24], pending[24], unable[24], active[24];
    void *ai_client;                           /* the AI client between its move flags and its target */
    u8 pflags[4];                              /* the player's Pokémon's allowed moves while the AI thinks for it */
    u8 aiflags[4];                             /* the AI Pokémon's allowed moves (its target hook checks the AI kept them) */
    u8 ai_check;                               /* that Pokémon's monId + 1 (0: none; an Encore skips the flags) */
    /* Arena */
    u8 pa, oa;                                 /* the matchup's monIds (0xff before the first) */
    u8 turns, in_move, attacker, prevented, res, cant_switch;
    s8 mind[2], skill[2];
    u16 hp0[2];
} State;
static State g_st;
#define ST (&g_st)

/* ================================================================================================ helpers */
static u32 rnd(u32 n) { return n ? GFL_RandomLC(n) : 0; }
static void zero(void *p, u32 n) { u8 *b = p; while (n--) *b++ = 0; }
static u16 *rec(void *gd) { return (u16 *)((u8 *)SaveControl_GetBlockPtr(GameData_GetSaveControl(gd), FR_PLAY_BLOCK) + FR_AREA_OFF); }
static u32 move_info(u32 move) { return move < PA_N_MOVES ? kMoveInfo[move] : MI_ATTACK | MI_MIND1 | MI_SELECT; }
static u32 mon_nature(void *mon) { return PokeParty_GetParam(GetSrcData(mon), P_NATURE, 0) % 25; }
static u32 side_of(u32 monId) { return monId >= 12; }          /* Black 2's GetSideFromMonID: 0-11 the player's side */
static void *flow_pokecon(void *flow) { return *(void **)((u8 *)flow + 8); }
static void *flow_queue(void *flow) { return *(void **)((u8 *)flow + 12); }

/* =============================================================================================== the Palace */
/* the move group of Emerald's GetBattlePalaceMoveGroup, read from the build-time table */
static u32 group_of(u32 move) { return move_info(move) & MI_GROUP; }

/* palaceFlags' "at or below half HP and not asleep" bit: set once (the flavor text then), kept until switched out */
static u32 palace_low(void *mon) {
    u32 id = GetMonID(mon), hp = GetBattleMonStat(mon, 13), max = GetBattleMonStat(mon, 14);
    if (id < 24 && !ST->low[id] && hp && max / 2 >= hp && GetBattleMonStatus(mon) != ST_SLEEP) {
        ST->low[id] = 1;
        ST->pending[id] = 1;
    }
    return id < 24 ? ST->low[id] : 0;
}

/* ChooseMoveAndTargetInBattlePalace's move choice: flags[] (1 = selectable, Black 2's StoreSelectableMoveFlag) becomes
 * the moves the AI may pick from; returns the first of them (4 = none) */
static u32 palace_flags(void *mon, u8 *flags) {
    u32 nat = mon_nature(mon), pct = rnd(100), i, min, max, group, sel = 0, usable = 0, n = GetBattleMonMoveCount(mon);
    u32 id = GetMonID(mon), chosen = 4;
    if (id < 24) ST->unable[id] = 0;
    min = palace_low(mon) ? 2 : 0;
    max = min + 2;
    for (i = min; i < max; i++) if (kPalaceLikelihood[nat][i] > pct) break;
    group = i == max ? 2 : i - min;
    for (i = 0; i < 4 && i < n; i++) {
        if (flags[i]) usable |= 1u << i;
        if (group_of(MoveGetID(mon, i)) == group && GetMovePP(mon, i)) sel |= 1u << i;
    }
    if (sel) {                                        /* the AI chooses among the group's moves (Emerald: selectedMoves) */
        u32 m = (sel & usable) ? sel & usable : sel;  /* (all of them unusable: one is tried and fails, as Emerald's) */
        for (i = 0; i < 4; i++) flags[i] = (m >> i) & 1;
    } else if (!usable) {
        if (id < 24) ST->unable[id] = 1;              /* every move unusable: "incapable" */
        for (i = 0; i < 4; i++) flags[i] = i == 0;
    } else {                                          /* no move of the group: Emerald's fallback */
        u32 na = 0, nd = 0, multi = 0, rg = 3;
        for (i = 0; i < 4; i++) if (usable >> i & 1) {
            u32 g = group_of(MoveGetID(mon, i));
            if (g == 0) na++; else if (g == 1) nd++;
        }
        if (na >= 2) multi++;
        if (nd >= 2) multi++;
        /* (Emerald's support count tests the defense nibble against 2 << 8: never true, kept as in Emerald) */
        if (multi == 1) rg = na >= 2 ? 0 : 1;
        while (chosen == 4) {
            i = rnd(4);
            if ((usable >> i & 1) && (rg == 3 || group_of(MoveGetID(mon, i)) == rg)) chosen = i;
        }
        for (i = 0; i < 4; i++) flags[i] = i == chosen;
        if (rnd(100) >= 50 && id < 24) ST->unable[id] = 1;
    }
    for (i = 0; i < 4; i++) if (flags[i]) return i;
    return 4;
}

/* GetBattlePalaceTarget (doubles): a one-target move goes to the foe with more / less HP by Nature, or at random */
static u32 palace_target(void *main, void *pokecon, void *mon, u32 move, u32 target) {
    u32 info = move_info(move), my = MonIDToBattlePos(main, pokecon, GetMonID(mon)), side = my & 1, p1, p2, h1, h2;
    void *m1, *m2;
    if (!ST->doubles) return target;
    if (info & MI_USER) return my;
    if (!(info & MI_SELECT)) return target;
    p1 = side ^ 1; p2 = p1 + 2;
    m1 = GetClientMon(pokecon, BattlePosToClientID(main, p1), p1 >> 1);
    m2 = GetClientMon(pokecon, BattlePosToClientID(main, p2), p2 >> 1);
    h1 = m1 && !IsFainted(m1) ? GetBattleMonStat(m1, 13) : 0;
    h2 = m2 && !IsFainted(m2) ? GetBattleMonStat(m2, 13) : 0;
    if (!h1) return p2;
    if (!h2) return p1;
    if (h1 == h2) return rnd(2) ? p2 : p1;
    switch (kPalaceTarget[mon_nature(mon)]) {
    case 0: return h1 > h2 ? p1 : p2;                 /* PALACE_TARGET_STRONGER */
    case 1: return h1 < h2 ? p1 : p2;                 /* PALACE_TARGET_WEAKER */
    default: return rnd(2) ? p2 : p1;
    }
}

/* ---- the opponents' AI (AISelectAction): its StoreSelectableMoveFlag call */
u32 PA_AIStoreFlags(void *client, void *mon, u8 *flags) {
    u32 first = StoreSelectableMoveFlag(client, mon, flags);
    if (ST->rule != RULE_PALACE || first == 4) return first;
    ST->ai_client = client;
    first = palace_flags(mon, flags);
    for (first = 0; first < 4; first++) ST->aiflags[first] = flags[first];
    ST->ai_check = (u8)(GetMonID(mon) + 1);
    for (first = 0; first < 4 && !flags[first]; first++) continue;
    return first;
}
/* ... and its BattleAction_SetFightParam call: the doubles target by Nature */
void PA_AISetFight(u32 *action, u32 move, u32 target) {
    void *c = ST->ai_client;
    if (ST->rule == RULE_PALACE && c && move != 165) {
        void *mon = *(void **)((u8 *)c + 8);
        u32 i;
        for (i = 0; i < 4 && MoveGetID(mon, i) != move; i++) continue;
        if (ST->ai_check != GetMonID(mon) + 1) i = 4;   /* (not the Palace's choice: an Encore) */
        ST->ai_check = 0;
        if (i < 4 && !ST->aiflags[i]) {              /* (the AI's scripts raised a move outside the group: the group's) */
            for (i = 0; i < 4 && !ST->aiflags[i]; i++) continue;
            if (i < 4) { move = MoveGetID(mon, i); target = 6; }
        }
        if (target > 5) target = DecideMoveTargetAuto(*(void **)c, *(void **)((u8 *)c + 4), mon, move, (u8 *)c + 252);
        target = palace_target(*(void **)c, *(void **)((u8 *)c + 4), mon, move, target);
    }
    BattleAction_SetFightParam(action, move, target);
}

/* ---- the player's FIGHT (ActionSelectRoot's command 1): the Pokémon chooses by itself */
#define CL_MAIN(c)    (*(void **)((u8 *)(c) + 0))
#define CL_POKECON(c) (*(void **)((u8 *)(c) + 4))
#define CL_MON(c)     (*(void **)((u8 *)(c) + 8))
#define CL_ACTION(c)  (*(u32 **)((u8 *)(c) + 12))
#define CL_AI(c)      (*(void **)((u8 *)(c) + 248))
#define CL_HEAP(c)    (*(u16 *)((u8 *)(c) + 0x1a2))
static u32 palace_finish(void *client, u32 idx, u32 target) {
    void *mon = CL_MON(client);
    u32 move = MoveGetID(mon, idx);
    if (target > 5) target = DecideMoveTargetAuto(CL_MAIN(client), CL_POKECON(client), mon, move, (u8 *)client + 56);
    target = palace_target(CL_MAIN(client), CL_POKECON(client), mon, move, target);
    BattleAction_SetFightParam(CL_ACTION(client), move, target);
    Client_SetProc(client, PROC_ACTION_DECIDED);
    return 0;
}
u32 PA_SelectFight(void *client, u32 *seq) {
    void *mon = CL_MON(client);
    u32 i, first;
    if (ST->rule != RULE_PALACE) return ActionSelectFight(client, seq);
    if (*seq == 0) {
        if (CheckForSelectableMove(client, mon, CL_ACTION(client))) {      /* nothing selectable: Struggle, as Black 2 */
            Client_SetProc(client, PROC_ACTION_DECIDED);
            return 0;
        }
        StoreSelectableMoveFlag(client, mon, ST->pflags);
        first = palace_flags(mon, ST->pflags);
        if (!CL_AI(client) && GFL_HeapGetFreeSize(CL_HEAP(client)) > 0x2000) {    /* Black 2's trainer AI, as the foe's */
            void *main = CL_MAIN(client);
            CL_AI(client) = TrAI_CreateVM(main, AiVmParam(main), CL_POKECON(client), AiFlagsOf(main, 1), CL_HEAP(client));
        }
        if (!CL_AI(client)) {                          /* (no room for it: a random move of the allowed ones) */
            u32 n = 0, k;
            for (i = 0; i < 4; i++) n += ST->pflags[i];
            k = rnd(n ? n : 1);
            for (i = 0; i < 4; i++) if (ST->pflags[i] && !k--) return palace_finish(client, i, 6);
            return palace_finish(client, first < 4 ? first : 0, 6);
        }
        TrAI_Setup(CL_AI(client), ST->pflags, MonIDToBattlePos(CL_MAIN(client), CL_POKECON(client), GetMonID(mon)));
        *seq = 1;
        return 0;
    }
    if (TrAI_Think(CL_AI(client))) return 0;           /* still thinking */
    i = TrAI_GetChosenMove(CL_AI(client));
    if (i >= 4 || !ST->pflags[i]) for (i = 0; i < 4 && !ST->pflags[i]; i++) continue;
    return palace_finish(client, i < 4 ? i : 0, TrAI_GetChosenTarget(CL_AI(client)));
}

/* ---- server: turn start (the flavor text; the Arena's matchup) */
static void put_msg1(void *flow, u32 id, u32 a) { SCQUE_PutMsg(flow_queue(flow), 0x5a, id, a, 0xffff0000); }
static void put_msg2(void *flow, u32 id, u32 a, u32 b) { SCQUE_PutMsg(flow_queue(flow), 0x5a, id, a, b, 0xffff0000); }
static void put_msg4(void *flow, u32 id, u32 a, u32 b, u32 c, u32 d) { SCQUE_PutMsg(flow_queue(flow), 0x5a, id, a, b, c, d, 0xffff0000); }
/* a line with the player's / the foe's wording (3 lines: player's, wild, foe's, as Black 2's set messages) */
static u32 by_side(u32 line, u32 monId) { return line + (side_of(monId) ? 2 : 0); }
static void *active(void *flow, u32 client, u32 slot) {
    void *m = GetClientMon(flow_pokecon(flow), client, slot);
    return m && !IsFainted(m) ? m : 0;
}
static void arena_matchup(void *flow);
void PA_TurnStart(void *flow) {
    TurnStart_ResetFlags(flow);
    if (ST->rule == RULE_PALACE) {
        u8 now[24];
        u32 pos, i;
        zero(now, sizeof now);
        for (pos = 0; pos < (ST->doubles ? 4u : 2u); pos++) {    /* battler order: player left, foe left, ... */
            void *m = active(flow, pos & 1, pos >> 1);
            u32 id;
            if (!m) continue;
            id = GetMonID(m);
            if (id >= 24) continue;
            now[id] = 1;
            if (ST->pending[id]) {
                ST->pending[id] = 0;
                if (ST->active[id])                   /* (just switched in: Emerald sets the flag silently) */
                    put_msg1(flow, PA_MSG_PALACE | by_side(kFlavorLine[kPalaceFlavor[mon_nature(m)]], id), id);
            }
        }
        for (i = 0; i < 24; i++) {
            if (!now[i]) ST->low[i] = ST->pending[i] = 0;
            ST->active[i] = now[i];
        }
    } else if (ST->rule == RULE_ARENA) {
        arena_matchup(flow);
    }
}

/* ---- server: the obedience check before a move; Palace: "appears incapable of using its power" */
u32 PA_Obedience(void *flow, void *mon) {
    u32 id = GetMonID(mon);
    if (ST->rule == RULE_PALACE && id < 24 && ST->unable[id]) { ST->unable[id] = 0; return 4; }
    if (ST->rule == RULE_PALACE && id < 24) ST->unable[id] = 0;
    return CheckObedience(flow, mon);
}
void PA_FailMessage(void *flow, void *mon, u32 move, u32 cause) {
    if (ST->rule == RULE_PALACE && cause == 0x16) {
        u32 id = GetMonID(mon);
        put_msg1(flow, PA_MSG_PALACE | by_side(PA_L_INCAPABLE, id), id);
        return;
    }
    MoveFailMessage(flow, mon, move, cause);
}

/* ================================================================================================ the Arena */
/* the matchup: the two Pokémon out; a new pair starts Emerald's count (BattleArena_InitPoints, "Commence battling!") */
static void arena_matchup(void *flow) {
    void *p = active(flow, 0, 0), *o = active(flow, 1, 0);
    u32 pi, oi;
    if (!p || !o) return;
    pi = GetMonID(p); oi = GetMonID(o);
    if (pi == ST->pa && oi == ST->oa) return;
    ST->pa = pi; ST->oa = oi;
    ST->turns = 0;
    ST->mind[0] = ST->mind[1] = ST->skill[0] = ST->skill[1] = 0;
    ST->hp0[0] = GetBattleMonStat(p, 13);
    ST->hp0[1] = GetBattleMonStat(o, 13);
    put_msg2(flow, PA_MSG_ARENA | PA_L_COMMENCE, pi, oi);
}

static s32 skill_of(u32 res, u32 move) {               /* BattleArena_AddSkillPoints / DeductSkillPoints */
    if (res & R_ALREADY) return -2;
    if ((res & R_POPUP) && !(res & R_HIT)) return -3;  /* the target's Ability blocked the move */
    if (res & R_PROTECT) return 0;
    if (res & R_NOEFF) return -2;
    if ((res & R_SE) && (res & R_NVE)) return 1;
    if (res & R_SE) return 2;
    if (res & R_NVE) return -1;
    if (move == MOVE_PROTECT || move == MOVE_DETECT) return 0;
    return 1;
}
void PA_Fight(void *flow, void *mon, u32 *action, u32 key) {
    u32 move, id, side, mi;
    if (ST->rule != RULE_ARENA) { ServerFight(flow, mon, action, key); return; }
    move = (*action >> 7) & 0xffff;
    id = GetMonID(mon); side = side_of(id);
    mi = move_info(move);
    ST->mind[side] += (mi & MI_MIND1) ? 1 : (mi & MI_MINDN) ? -1 : 0;     /* sMindRatings */
    ST->in_move = 1; ST->attacker = id; ST->prevented = 0; ST->res = 0;
    ServerFight(flow, mon, action, key);
    ST->in_move = 0;
    if (!ST->prevented) ST->skill[side] += skill_of(ST->res, move);
}
u32 PA_MovePrecheck(void *flow, void *mon, u32 move, u32 flag) {
    u32 r = MovePrecheck(flow, mon, move, flag);
    if (ST->rule == RULE_ARENA && ST->in_move && r) ST->prevented = 1;   /* asleep, frozen, flinched...: no Skill */
    return r;
}
/* the message and command spies (called from the asm detours below with the put functions' first arguments) */
void PA_MsgSpyC(void *queue, u32 cmd, u32 id, u32 a0) {
    if (ST->rule != RULE_ARENA || !ST->in_move) return;
    (void)queue; (void)a0;
    if (cmd == 0x5a) {
        if (id == 0x4e) ST->res |= R_SE;
        else if (id == 0x4f) ST->res |= R_NVE;
        else if (id == 0x47) ST->res |= R_NOEFF;            /* But it failed! */
    } else if (cmd == 0x5b) {
        switch (id) {
        case 210: case 213: case 216: ST->res |= R_NOEFF; break;   /* doesn't affect / avoided / unaffected */
        case 523: ST->res |= R_PROTECT; break;                      /* protected itself */
        case 249: case 267: case 282: case 297: case 315: case 354: ST->res |= R_ALREADY; break;   /* already ... */
        }
    }
}
void PA_CmdSpyC(void *queue, u32 cmd, u32 a, u32 b) {
    if (ST->rule != RULE_ARENA || !ST->in_move) return;
    (void)queue;
    if (cmd == 0x33) { ST->res |= R_HIT; if (b == 2) ST->res |= R_SE; else if (b == 3) ST->res |= R_NVE; }   /* damage */
    else if (cmd == 0x57 && a != ST->attacker) ST->res |= R_POPUP;          /* another Pokémon's Ability window */
}
/* detours: at func+4 of func_ov167_021b15d0 / 021b1434 (after their two pushes), `bl` here; the two displaced
 * instructions run here, with sp as the function's own (+4 for the return address still on the stack) */
__attribute__((naked)) void PA_MsgSpy(void) {
    __asm__ volatile("push {r0, r1, r2, r3, lr}\n"
                     "bl PA_MsgSpyC\n"
                     "pop {r0, r1, r2, r3}\n"
                     "add r2, sp, #32\n"            /* add r2, sp, #28 */
                     "movs r1, #3\n"
                     "pop {pc}\n");
}
__attribute__((naked)) void PA_CmdSpy(void) {
    __asm__ volatile("push {r0, r1, r2, r3, lr}\n"
                     "bl PA_CmdSpyC\n"
                     "pop {r0, r1, r2, r3}\n"
                     "adds r7, r0, #0\n"            /* adds r7, r0, #0 */
                     "ldr r1, [sp, #32]\n"          /* ldr r1, [sp, #28] */
                     "pop {pc}\n");
}

/* the judgment (BattleScript_ArenaDoJudgment, BattleArena_ShowJudgmentWindow) */
static void faint(void *flow, void *mon) {
    u8 *suppress = (u8 *)flow + 0x789, old = *suppress;    /* (no "fainted!": the referee's line says it) */
    *suppress = (u8)GetMonID(mon);
    ServerControl_FaintPokemon(flow, mon);
    *suppress = old;
}
static void judge(void *flow, void *p, void *o) {
    u32 pi = GetMonID(p), oi = GetMonID(o), c, ps = 0, os = 0;
    s32 a[3], b[3];
    a[0] = ST->mind[0]; b[0] = ST->mind[1];
    a[1] = ST->skill[0]; b[1] = ST->skill[1];
    a[2] = ST->hp0[0] ? GetBattleMonStat(p, 13) * 100 / ST->hp0[0] : 0;
    b[2] = ST->hp0[1] ? GetBattleMonStat(o, 13) * 100 / ST->hp0[1] : 0;
    put_msg2(flow, PA_MSG_ARENA | PA_L_THATS_IT, pi, oi);
    for (c = 0; c < 3; c++) {
        put_msg2(flow, PA_MSG_ARENA | (PA_L_MIND + c), pi, oi);
        if (a[c] > b[c]) { ps += 2; put_msg2(flow, PA_MSG_ARENA | PA_L_CAT_WIN, pi, oi); }
        else if (a[c] < b[c]) { os += 2; put_msg2(flow, PA_MSG_ARENA | PA_L_CAT_WIN, oi, pi); }
        else { ps++; os++; put_msg2(flow, PA_MSG_ARENA | PA_L_CAT_TIE, pi, oi); }
    }
    if (ps > os) {
        put_msg4(flow, PA_MSG_ARENA | PA_L_PLAYER_WON, ps, os, 0, pi);
        put_msg2(flow, PA_MSG_ARENA | PA_L_DEFEATED, pi, oi);
        faint(flow, o);
    } else if (ps < os) {
        put_msg4(flow, PA_MSG_ARENA | PA_L_OPP_WON, ps, os, 1, oi);
        put_msg2(flow, PA_MSG_ARENA | PA_L_LOST, pi, oi);
        faint(flow, p);
    } else {
        put_msg2(flow, PA_MSG_ARENA | PA_L_DRAW, pi, oi);
        put_msg2(flow, PA_MSG_ARENA | PA_L_TIED, pi, oi);
        faint(flow, p);
        faint(flow, o);
    }
    ST->turns = 0;
}
/* the turn's end (after every end-of-turn effect): the third full turn of a matchup with both standing -> judgment */
u32 PA_TurnEnd(void *flow) {
    u32 r = TurnEnd(flow);
    void *p, *o;
    if (ST->rule != RULE_ARENA || r || *((u8 *)flow + 0x77e) || ServerControl_CheckMatchup(flow)) return r;
    p = active(flow, 0, 0); o = active(flow, 1, 0);
    if (!p || !o || GetMonID(p) != ST->pa || GetMonID(o) != ST->oa) return r;     /* (a switch: next turn's matchup) */
    if (++ST->turns >= 3) judge(flow, p, o);
    return r;
}

/* ---- no switching: the AI never switches; replacements come in party order (the player's too) */
u32 PA_AISwitchChecks(void *client, void *mon, u32 idx, u8 *out) {
    if (ST->rule == RULE_ARENA) return 0;
    return AISwitchChecks(client, mon, idx, out);
}
u32 PA_AIPickBest(void *client, u8 *list, u32 n) {
    if (ST->rule == RULE_ARENA) return 0;               /* (the list stays in party order) */
    return PickBestMonToSwitchInto(client, list, n);
}
/* the "will you switch your Pokémon?" prompt (Shift style, client command 7): the Arena answers no */
#define ShiftProcUI                FN(u32 (*)(void *, u32 *), 0x021b5f30)
u32 PA_ShiftProc(void *client, u32 *seq) {
    u8 *c = client;
    if (ST->rule != RULE_ARENA) return ShiftProcUI(client, seq);
    c[436] = 0;
    *(u8 **)(c + 224) = c + 436;
    *(u32 *)(c + 228) = 1;
    return 1;
}
u32 PA_ChangeProc5(void *client, u32 *seq) { return ST->rule == RULE_ARENA ? ChangeProcAI(client, seq) : ChangeProcUI5(client, seq); }
u32 PA_ChangeProc6(void *client, u32 *seq) { return ST->rule == RULE_ARENA ? ChangeProcAI(client, seq) : ChangeProcUI6(client, seq); }
/* the player's POKéMON command: "{mon} can't be switched out!" (the root menu's Sky Drop path, with our line) */
u32 PA_RootCheckCondition(void *mon, u32 cond) {
    if (ST->rule == RULE_ARENA) { ST->cant_switch = 1; return 1; }
    return CheckCondition(mon, cond);
}
void PA_RootStringSetup(void *param, u32 type, u32 id) {
    if (ST->cant_switch) { ST->cant_switch = 0; id = PA_MSG_ARENA | PA_L_CANT_SWITCH; }
    Btlv_StringParam_Setup(param, type, id);
}

/* ---- the battle's std strings: ours from the rooms' texts */
void PA_StdString(void *out, u32 id, void *args) {
    u32 file;
    void *msg;
    if ((id & 0xc000) != 0x4000) { StdString_Make(out, id, args); return; }
    file = (id & 0x2000) ? PA_TEXT_ARENA : PA_TEXT_PALACE;
    msg = GFL_MsgSysLoadData(0, ARC_SCRIPT_TEXT, file, HEAP_TAIL);
    GFL_MsgDataLoadStrbuf(msg, id & 0x1fff, *(void **)(BTL_STR + 12));
    GFL_MsgDataFree(msg);
    StdString_Args(*(void **)(BTL_STR + 12), args, *(void **)(BTL_STR + 8));
    WordSet_ExpandStr(*(void **)(BTL_STR + 8), out, *(void **)(BTL_STR + 12));
}

/* ================================================================================================ the field */
static u32 lvl_mode(const u16 *k) { return k[K_LVL] & 1; }
static u32 streak_key(const u16 *k, u32 fac) { return K_STREAK(fac, fac == FAC_PALACE ? k[K_BATTLE_MODE] & 1 : 0, lvl_mode(k)); }
static u32 met_get(const u16 *k, u32 i) { u32 b = 9 * i; u32 w = k[K_PA_MET + b / 16] | (u32)k[K_PA_MET + b / 16 + 1] << 16; return (w >> (b % 16)) & 511; }
static void met_set(u16 *k, u32 i, u32 v) {
    u32 b = 9 * i, j = K_PA_MET + b / 16, s = b % 16;
    u32 w = k[j] | (u32)k[j + 1] << 16;
    w = (w & ~(511u << s)) | (v & 511) << s;
    k[j] = (u16)w;
    if (j + 1 < K_PA_MET + 4) k[j + 1] = (u16)(w >> 16);
}
static u32 brain_status(const u16 *k, u32 fac) {        /* GetFrontierBrainStatus */
    const u8 *a = kBrainStreak[fac == FAC_ARENA];
    s32 ws = k[streak_key(k, fac)] + a[3];
    u32 sym = (k[K_SYMBOLS] >> (2 * fac)) & 3, n = (sym & 1) + ((sym >> 1) & 1);
    if (fac == FAC_PALACE && (k[K_BATTLE_MODE] & 1)) return 0;   /* the Brains take singles challenges only */
    if (n < 2) return ws == a[n] ? n + 1 : 0;
    if (ws == a[0]) return 3;
    if (ws == a[1]) return 4;
    if (ws > a[1] && (ws - a[1]) % a[2] == 0) return 4;
    return 0;
}
static u32 trainer_id(u32 c, u32 battle) {              /* GetRandomScaledFrontierTrainerId */
    const u16 *r;
    if (c > 7) c = 7;
    r = (battle == 6 && c <= 7) ? kTrainerRangesHard[c] : kTrainerRanges[c];
    if (c == 7) r = kTrainerRanges[7];
    return r[0] + rnd(r[1] - r[0] + 1);
}
typedef struct { u16 cls, sprite, off, count; } TrRec;
typedef struct { u16 species, moves[4]; u8 ev, nature; u16 item, form; } SetRec;
static void tr_rec(u32 t, TrRec *o) { GFL_ArcSysReadRange(o, ARC_SETS, PA_TRAINERS_FILE, t * 8, 8); }
static u32 tr_set(const TrRec *t, u32 k) { u16 v; GFL_ArcSysReadRange(&v, ARC_SETS, PA_TRAINERS_FILE, (t->off + k) * 2, 2); return v; }
static void set_rec(u32 id, SetRec *s) { GFL_ArcSysReadRange(s, ARC_SETS, PA_SET_BASE + id, 0, 16); }
static u32 fixed_iv(u32 t) {                            /* GetFrontierTrainerFixedIvs */
    return t <= 99 ? 3 : t <= 119 ? 6 : t <= 139 ? 9 : t <= 159 ? 12 : t <= 179 ? 15 : t <= 199 ? 18 : t <= 219 ? 21 : 31;
}
static void make_mon(void *party, u32 species, u32 level, u32 iv, u32 nature, const u16 *moves, u32 item, const u8 *evs) {
    void *pkm = GFL_HeapAllocate(HEAP_TAIL, PokeParty_GetPkmRawSize(), 1, 0, 0);
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
/* FillTrainerParty: three sets of the trainer's list, no species or held item twice, high-tier sets only at Open Level */
static void fill_party(void *party, u32 t, u32 level, u16 *ids) {
    TrRec tr; SetRec s; u16 sp[3], it[3]; u32 i = 0, j, tries = 0, c, e; u8 evs[6];
    tr_rec(t, &tr);
    while (i < 3 && tries++ < 3000) {
        u32 id = tr_set(&tr, rnd(tr.count));
        if (level == 50 && id > PA_HIGH_TIER) continue;
        set_rec(id, &s);
        for (j = 0; j < i && sp[j] != s.species; j++) continue;
        if (j != i) continue;
        for (j = 0; j < i && !(it[j] && it[j] == s.item); j++) continue;
        if (j != i) continue;
        for (j = 0; j < i && ids[j] != id; j++) continue;
        if (j != i) continue;
        ids[i] = (u16)id; sp[i] = s.species; it[i] = s.item;
        for (c = 0, j = 0; j < 6; j++) c += (s.ev >> j) & 1;
        e = c ? (510 / c) & 0xFF : 0;                  /* (u8, as Emerald's CreateMonWithEVSpread stores it) */
        for (j = 0; j < 6; j++) evs[j] = (u8)(((s.ev >> j) & 1) ? e : 0);
        make_mon(party, s.species, level, fixed_iv(t), s.nature, s.moves, s.item, evs);
        i++;
    }
}
static void brain_party(void *party, u32 fac, u32 gold, u32 level) {   /* CreateFrontierBrainPokemon */
    u32 i;
    for (i = 0; i < 3; i++) {
        const BrainMon *b = &kBrainMons[fac == FAC_ARENA][gold ? 1 : 0][i];
        make_mon(party, b->species, level, b->iv, b->nature, b->moves, b->item, b->evs);
    }
}
/* ---- the Battle Tents (pokeemerald src/battle_tower.c SetTentPtrsGetLevel, SetNextBattleTentOpponent,
 * FillTentTrainerParty_): the tent's own 30 trainers and their sets (arc 211 TENT_FILE, frontier_factory_dome.py
 * tent_file), never a trainer twice in a challenge, at the level of the three's highest (at least TENT_MIN_LEVEL, 30),
 * IVs 0, friendship 255 (0 with Frustration), no set, species or held item twice */
typedef struct { u16 tr, sets, n_sets, n_tr; } TentHead;
typedef struct { u16 cls, sprite, list, n; } TentTr;
static void tent_head(u32 tent, TentHead *h) { GFL_ArcSysReadRange(h, ARC_SETS, TENT_FILE, 8 + 8 * tent, 8); }
static void tent_tr(const TentHead *h, u32 t, TentTr *o) { GFL_ArcSysReadRange(o, ARC_SETS, TENT_FILE, h->tr + 8 * t, 8); }
static u32 tent_list(const TentTr *t, u32 k) { u16 v; GFL_ArcSysReadRange(&v, ARC_SETS, TENT_FILE, t->list + 2 * k, 2); return v; }
static void tent_set(const TentHead *h, u32 id, SetRec *s) { GFL_ArcSysReadRange(s, ARC_SETS, TENT_FILE, h->sets + 16 * id, 16); }
static u32 tent_of(u32 fac) { return fac == FAC_ARENA ? 1 : 0; }
static u32 tent_text(u32 fac) { return fac == FAC_ARENA ? TENT_TEXT_FALLARBOR : TENT_TEXT_VERDANTURF; }
static u32 tent_met(const u16 *k, u32 i) { return (k[K_TENT_OPP] >> (5 + 5 * i)) & 31; }
static void tent_fill(void *party, u32 fac, u32 t, u32 level) {
    TentHead h; TentTr tr; SetRec s; u16 sp[3], it[3], ids[3]; u32 i = 0, j, tries = 0, c, e; u8 evs[6];
    tent_head(tent_of(fac), &h);
    tent_tr(&h, t, &tr);
    while (i < 3 && tries++ < 3000) {
        u32 id = tent_list(&tr, rnd(tr.n));
        tent_set(&h, id, &s);
        for (j = 0; j < i && sp[j] != s.species; j++) continue;
        if (j != i) continue;
        for (j = 0; j < i && !(it[j] && it[j] == s.item); j++) continue;
        if (j != i) continue;
        for (j = 0; j < i && ids[j] != id; j++) continue;
        if (j != i) continue;
        ids[i] = (u16)id; sp[i] = s.species; it[i] = s.item;
        for (c = 0, j = 0; j < 6; j++) c += (s.ev >> j) & 1;
        e = c ? (510 / c) & 0xFF : 0;
        for (j = 0; j < 6; j++) evs[j] = (u8)(((s.ev >> j) & 1) ? e : 0);
        make_mon(party, s.species, level, 0, s.nature, s.moves, s.item, evs);
        i++;
    }
}
static u32 three_highest(void *gd) {
    u16 *k = rec(gd);
    void *party = GameData_GetParty(gd);
    u32 i, lv = 0;
    for (i = 0; i < 3; i++) {
        u32 slot = ((k[K_PARTY] >> (4 * i)) & 15) - 1;
        if (slot < PokeParty_GetPkmCount(party)) { u32 l = PokeParty_GetParam(PokeParty_GetPkm(party, slot), P_LEVEL, 0); if (l > lv) lv = l; }
    }
    return lv;
}
static u32 tent_level(void *gd) { u32 l = three_highest(gd); return l < TENT_LEVEL ? TENT_LEVEL : l; }

static u32 enemy_level(void *gd) {                      /* GetFrontierEnemyMonLevel: 50, or the three's highest (>= 60) */
    u16 *k = rec(gd);
    void *party = GameData_GetParty(gd);
    u32 i, lv = 0;
    if (!lvl_mode(k)) return 50;
    for (i = 0; i < 3; i++) {
        u32 slot = ((k[K_PARTY] >> (4 * i)) & 15) - 1;
        if (slot < PokeParty_GetPkmCount(party)) { u32 l = PokeParty_GetParam(PokeParty_GetPkm(party, slot), P_LEVEL, 0); if (l > lv) lv = l; }
    }
    return lv < 60 ? 60 : lv;
}
static void load_line(u32 file, u32 line, void *sb) {
    void *msg = GFL_MsgSysLoadData(0, ARC_SCRIPT_TEXT, file, HEAP_TAIL);
    GFL_MsgDataLoadStrbuf(msg, line, sb);
    GFL_MsgDataFree(msg);
}
static void word_line(void *env, u32 slot, u32 file, u32 line) {
    void *sb = GFL_StrBufCreate(128, HEAP_TAIL);
    load_line(file, line, sb);
    WordSet_LoadStrbuf(ScriptWork_GetWordSet(FieldScriptEnv_GetScriptWork(env)), slot, sb, 0, 1, 2);
    GFL_StrBufFree(sb);
}
static u32 opp_name_line(u32 fac, u32 t, u32 *file) {    /* both battle rooms' texts hold the names */
    *file = fac == FAC_ARENA ? PA_TEXT_ARENA : PA_TEXT_PALACE;
    if (t == PA_BRAIN) return fac == FAC_ARENA ? PA_L_NAME_GRETA : PA_L_NAME_SPENSER;
    return PA_NAME_BASE + t;
}

/* ---- the battle: our event around Black 2's battle event */
typedef struct { void *gsys, *setup; u16 *out; u8 rule, doubles; } BattleWork;
static void reset_battle_state(u32 rule, u32 doubles) {
    zero(ST, sizeof(*ST));
    ST->rule = (u8)rule; ST->doubles = (u8)doubles;
    ST->pa = ST->oa = 0xff;
}
u32 PA_BattleEvent(void *event, u32 *state, void *data) {
    BattleWork *w = data;
    switch (*state) {
    case 0:
        reset_battle_state(w->rule, w->doubles);
        GameEvent_ChainNext(event, BattleCall_Create(w->gsys, GSYS_GetField(w->gsys), w->setup));
        *state = 1;
        return 0;
    default:
        ST->rule = RULE_NONE;
        *w->out = *(u32 *)((u8 *)w->setup + SETUP_RESULT) == 1;
        FreeVSPlayerBlk();
        BtlSetup_Free(w->setup);
        return 1;
    }
}
static u32 start_battle(void *env, u16 *var, u32 fac, u32 tent) {
    void *gd = FieldScriptEnv_GetGameData(env), *gsys = FieldScriptEnv_GetGameSystem(env);
    u16 *k = rec(gd);
    void *party = GameData_GetParty(gd), *pl, *op, *setup, *event;
    u8 *tr;
    u16 ids[3] = {0, 1, 2};
    u32 i, t = tent ? k[K_TENT_OPP] & 31 : k[K_PA_OPP] & 1023, level = tent ? tent_level(gd) : enemy_level(gd), cls;
    u32 doubles = !tent && fac == FAC_PALACE && (k[K_BATTLE_MODE] & 1);
    BattleWork *w;
    pl = PokeParty_Create(HEAP_TAIL);
    PokeParty_InitCore(pl, 6);
    for (i = 0; i < 3; i++) {                           /* the challenge's three, in the order they were entered */
        u32 slot = ((k[K_PARTY] >> (4 * i)) & 15) - 1;
        if (slot < PokeParty_GetPkmCount(party)) PokeParty_AddPkm(pl, PokeParty_GetPkm(party, slot));
    }
    op = PokeParty_Create(HEAP_TAIL);
    PokeParty_InitCore(op, 6);
    if (tent) { TentHead h; TentTr r; tent_fill(op, fac, t, level); tent_head(tent_of(fac), &h); tent_tr(&h, t, &r); cls = r.cls; }
    else if (t == PA_BRAIN) { brain_party(op, fac, brain_status(k, fac) == 2 || brain_status(k, fac) == 4, level); cls = fac == FAC_ARENA ? PA_GRETA_CLASS : PA_SPENSER_CLASS; }
    else { TrRec r; fill_party(op, t, level, ids); tr_rec(t, &r); cls = r.cls; }
    /* the Subway trainer record (func_ov012_021628c0's layout): +0 id + 1, +4 class, +8 name, +24/+26 lines (none), +48
       the Pokémon (any valid sets: the party built above replaces them) */
    tr = GFL_HeapAllocate(HEAP_TAIL, 0x30 + 4 * PKM_SIZE, 1, 0, 0);
    *(u32 *)tr = 1;
    *(u16 *)(tr + 4) = (u16)cls;
    { void *sb = GFL_StrBufCreate(32, HEAP_TAIL); u32 file, line = tent ? (file = tent_text(fac), TENT_NAME_BASE + t) : opp_name_line(fac, t, &file);
      load_line(file, line, sb); GFL_StrBufStoreString(sb, (u16 *)(tr + 8), 8); GFL_StrBufFree(sb); }
    *(u16 *)(tr + 24) = 0xFFFF;
    *(u16 *)(tr + 26) = 0xFFFF;
    for (i = 0; i < 3; i++)
        SubwayPkm_FromSet(tr + TRAINER_PKM + i * PKM_SIZE, ARC_SETS, PA_SET_BASE + ids[i], 0, 0x77 + i, 0, i, 0, HEAP_TAIL);
    VSPlayerBlk_Alloc(4);
    setup = SetupTrialHouseBattle(gsys, pl, doubles, tr, 0, 3);
    PokeParty_Copy(pl, *(void **)((u8 *)setup + SETUP_PARTY0));    /* the three as they are (no Lv. 50 scaling) */
    PokeParty_Copy(op, *(void **)((u8 *)setup + SETUP_PARTY1));
    GFL_HeapFree(tr);
    GFL_HeapFree(pl);
    GFL_HeapFree(op);
    event = GameEvent_Create(gsys, 0, (void *)PA_BattleEvent, sizeof(BattleWork));
    w = GameEvent_GetData(event);
    w->gsys = gsys; w->setup = setup; w->out = var;
    w->rule = fac == FAC_ARENA ? RULE_ARENA : RULE_PALACE;
    w->doubles = (u8)doubles;
    *var = 0;
    ScriptWork_CallEvent(FieldScriptEnv_GetScriptWork(env), event);
    return 1;
}

/* ---- the Battle Tower's Salon Maiden Anabel (Emerald v1.1, 2026-10-18; src/field_scripts/0030_room_BattleTower_
 * BattleRoom.s, #ifdef HOENN_EMERALD). The tower is Sapphire's on Black 2's Battle Subway (battle_tower.py): its streak
 * is the Subway's (the script passes it: command 358), its three are the Subway work's members, its Lv. 50 / Open Level
 * rooms are play modes 0 / 5. pokeemerald frontier_util.c GetFrontierBrainStatus, GetFrontierBrainSymbol,
 * CreateFrontierBrainPokemon (sFrontierBrainStreakAppearances[TOWER], sFrontierBrainsMons[TOWER]: kTowerStreak,
 * kTowerBrainMons) and GetFrontierEnemyMonLevel; the battle is the Brains' battle above (start_battle) without a rule. */
#define BSubway_GetWork  FN(u8 *(*)(void *), 0x0201794c)
#define BSW_MEMBER_COUNT 8                     /* BSubwayScrWork (include/field/bsubway_scr.h): memberCount, playMode, */
#define BSW_PLAY_MODE 9                        /* memberSlots[4] (party slots) */
#define BSW_MEMBER_SLOTS 30
#define TOWER_MODE_OPEN 5                      /* the Lv. 100 room's play mode = Emerald's Open Level (frontier_core) */
#define TOWER_HEARD 0x1000                     /* K_PA_OPP bit 12 / 13: sBattledBrainBitFlags[TOWER][0 / 1] */
static u32 tower_status(const u16 *k, u32 wins) {        /* GetFrontierBrainStatus (singles: the tower's only mode) */
    const u8 *a = kTowerStreak;
    s32 ws = (s32)wins + a[3];
    u32 sym = k[K_SYMBOLS] & 3, n = (sym & 1) + ((sym >> 1) & 1);   /* FR_SYMBOLS bits 0 / 1: facility 0 */
    if (n < 2) return ws == a[n] ? n + 1 : 0;           /* FRONTIER_BRAIN_SILVER / _GOLD */
    if (ws == a[0]) return 3;                           /* FRONTIER_BRAIN_STREAK */
    if (ws == a[1]) return 4;                           /* FRONTIER_BRAIN_STREAK_LONG */
    if (ws > a[1] && (ws - a[1]) % a[2] == 0) return 4;
    return 0;
}
static u32 tower_battle(void *env, u16 *var, u32 status) {
    void *gd = FieldScriptEnv_GetGameData(env), *gsys = FieldScriptEnv_GetGameSystem(env);
    u8 *bsw = BSubway_GetWork(gd), *tr;
    void *party = GameData_GetParty(gd), *pl, *op, *setup, *event;
    u32 i, n = bsw[BSW_MEMBER_COUNT] < 3 ? bsw[BSW_MEMBER_COUNT] : 3, lv = 0, level;
    u32 gold = status == 2 || status == 4;              /* GetFrontierBrainSymbol: her Gold Symbol party */
    BattleWork *w;
    pl = PokeParty_Create(HEAP_TAIL);
    PokeParty_InitCore(pl, 6);
    for (i = 0; i < n; i++) {                           /* the three entered, in their order (as BSubway_BuildSetup) */
        u32 slot = bsw[BSW_MEMBER_SLOTS + i];
        if (slot < PokeParty_GetPkmCount(party)) {
            void *pkm = PokeParty_GetPkm(party, slot);
            u32 l = PokeParty_GetParam(pkm, P_LEVEL, 0);
            PokeParty_AddPkm(pl, pkm);
            if (l > lv) lv = l;
        }
    }
    /* GetFrontierEnemyMonLevel: 50, or at Open Level the three's highest (at least 60), as the tower's trainers
       (frontier_core.c FR_TowerLevel) */
    level = bsw[BSW_PLAY_MODE] != TOWER_MODE_OPEN ? 50 : lv < 60 ? 60 : lv;
    op = PokeParty_Create(HEAP_TAIL);
    PokeParty_InitCore(op, 6);
    for (i = 0; i < 3; i++) {                           /* CreateFrontierBrainPokemon */
        const BrainMon *b = &kTowerBrainMons[gold][i];
        make_mon(op, b->species, level, b->iv, b->nature, b->moves, b->item, b->evs);
    }
    /* the Subway trainer record as start_battle's: Salon Maiden (class 9: her battle picture) Anabel */
    tr = GFL_HeapAllocate(HEAP_TAIL, 0x30 + 4 * PKM_SIZE, 1, 0, 0);
    *(u32 *)tr = 1;
    *(u16 *)(tr + 4) = PA_ANABEL_CLASS;
    { void *sb = GFL_StrBufCreate(32, HEAP_TAIL);
      load_line(PA_TOWER_TEXT, BTB_L_ANABEL_NAME, sb); GFL_StrBufStoreString(sb, (u16 *)(tr + 8), 8); GFL_StrBufFree(sb); }
    *(u16 *)(tr + 24) = 0xFFFF;
    *(u16 *)(tr + 26) = 0xFFFF;
    for (i = 0; i < 3; i++)
        SubwayPkm_FromSet(tr + TRAINER_PKM + i * PKM_SIZE, ARC_SETS, PA_SET_BASE + i, 0, 0x77 + i, 0, i, 0, HEAP_TAIL);
    VSPlayerBlk_Alloc(4);
    setup = SetupTrialHouseBattle(gsys, pl, 0, tr, 0, 3);
    PokeParty_Copy(pl, *(void **)((u8 *)setup + SETUP_PARTY0));    /* the three as they are */
    PokeParty_Copy(op, *(void **)((u8 *)setup + SETUP_PARTY1));
    GFL_HeapFree(tr);
    GFL_HeapFree(pl);
    GFL_HeapFree(op);
    event = GameEvent_Create(gsys, 0, (void *)PA_BattleEvent, sizeof(BattleWork));
    w = GameEvent_GetData(event);
    w->gsys = gsys; w->setup = setup; w->out = var;
    w->rule = RULE_NONE;
    w->doubles = 0;
    *var = 0;
    ScriptWork_CallEvent(FieldScriptEnv_GetScriptWork(env), event);
    return 1;
}

/* ---- script command 291: FrontierPA var, sub, a, b (+ five unused) */
enum { PA_NEXT_OPPONENT = 11, PA_BRAIN_STATUS = 12, PA_GREETING = 13, PA_NAME = 14, PA_BATTLE = 15, PA_HEARD = 16,
       PA_INIT = 10, PA_RANDOM = 1, PA_TOWER_STATUS = 20, PA_TOWER_BATTLE = 21, PA_TOWER_HEARD = 22 };
u32 PA_Cmd(void *vm, void *env) {
    u16 *var = ScriptReadVar(vm, env);
    u32 args[8], i, fac;
    void *gd;
    u16 *k;
    for (i = 0; i < 8; i++) args[i] = ScriptReadAny(vm, env);
    gd = FieldScriptEnv_GetGameData(env);
    k = rec(gd);
    switch (args[0]) {                                  /* the Battle Tower's Anabel (no facility argument) */
    case PA_TOWER_STATUS: *var = (u16)tower_status(k, args[1]); return 0;       /* a = the Subway streak */
    case PA_TOWER_BATTLE: return tower_battle(env, var, args[1]);               /* a = her status */
    case PA_TOWER_HEARD: {                              /* a = 0 / 1 (no symbol / Silver held), b = 1 marks it heard */
        u32 bit = args[1] ? TOWER_HEARD << 1 : TOWER_HEARD;
        *var = (k[K_PA_OPP] & bit) != 0;
        if (args[2]) k[K_PA_OPP] |= bit;
        return 0;
    }
    }
    fac = (args[1] & 15) == FAC_ARENA ? FAC_ARENA : FAC_PALACE;
    if (args[1] & FAC_TENT) {                           /* a Battle Tent (battle_tents): its own trainers, no Brain */
        switch (args[0]) {
        case PA_INIT: k[K_TENT_OPP] = 0; return 0;
        case PA_NEXT_OPPONENT: {                        /* SetNextBattleTentOpponent; var = the walking sprite */
            u32 bn = k[K_BATTLE_NUM], t, j;
            TentHead h; TentTr r;
            tent_head(tent_of(fac), &h);
            do {
                t = rnd(h.n_tr);
                for (j = 0; j < bn && j < 2 && tent_met(k, j) != t; j++) continue;
            } while (j < bn && j < 2);
            if (bn < 2) k[K_TENT_OPP] = (u16)((k[K_TENT_OPP] & ~(31u << (5 + 5 * bn))) | t << (5 + 5 * bn));
            k[K_TENT_OPP] = (u16)((k[K_TENT_OPP] & ~31u) | t);
            tent_tr(&h, t, &r);
            *var = r.sprite;
            return 0;
        }
        case PA_BRAIN_STATUS: *var = 0; return 0;
        case PA_GREETING: *var = (u16)(TENT_SPEECH_BASE + (k[K_TENT_OPP] & 31)); return 0;
        case PA_NAME: word_line(env, args[2], tent_text(fac), TENT_NAME_BASE + (k[K_TENT_OPP] & 31)); return 0;
        case PA_BATTLE: return start_battle(env, var, fac, 1);
        case PA_HEARD: *var = 1; return 0;
        }
    }
    switch (args[0]) {
    case PA_RANDOM: *var = (u16)rnd(args[1]); return 0;
    case PA_INIT:                                       /* a new challenge: nobody met yet */
        for (i = 0; i < 4; i++) k[K_PA_MET + i] = 0;
        return 0;
    case PA_NEXT_OPPONENT: {                            /* SetNextFacilityOpponent; var = the opponent's walking sprite */
        u32 bn = k[K_BATTLE_NUM], c = k[streak_key(k, fac)] / 7, t, j, tries = 0;
        TrRec r;
        if (brain_status(k, fac)) {
            k[K_PA_OPP] = (k[K_PA_OPP] & 0xF000) | PA_BRAIN;
            *var = fac == FAC_ARENA ? PA_GRETA_SPRITE : PA_SPENSER_SPRITE;
            return 0;
        }
        do {
            t = trainer_id(c, bn);
            for (j = 0; j < bn && j < 6 && met_get(k, j) != t; j++) continue;
        } while ((j < bn && j < 6) && tries++ < 500);
        if (bn < 6) met_set(k, bn, t);
        k[K_PA_OPP] = (k[K_PA_OPP] & 0xF000) | t;
        tr_rec(t, &r);
        *var = r.sprite;
        return 0;
    }
    case PA_BRAIN_STATUS: *var = (u16)brain_status(k, fac); return 0;
    case PA_GREETING: {                                 /* var = the greeting's line in the battle room's text, 0xFFFF the Brain */
        u32 t = k[K_PA_OPP] & 1023;
        *var = t == PA_BRAIN ? 0xFFFF : (u16)(PA_SPEECH_BASE + t);
        return 0;
    }
    case PA_NAME: { u32 file, line = opp_name_line(fac, k[K_PA_OPP] & 1023, &file); word_line(env, args[2], file, line); return 0; }
    case PA_BATTLE: return start_battle(env, var, fac, 0);
    case PA_HEARD: {                                    /* the Brain's first speech: var = heard; b = 1 marks it heard */
        u32 bit = fac == FAC_ARENA ? 0x8000 : 0x4000;
        *var = (k[K_PA_OPP] & bit) != 0;
        if (args[2]) k[K_PA_OPP] |= bit;
        return 0;
    }
    }
    return 0;
}
