// A host-side run of the contest's rules (src/hoennb2/contest/contest_logic.c, contest_effect.c, contest_ai.c): AI against AI
#include <stdio.h>
#include <stdlib.h>
#include "contest_port.h"

struct ContestResources *gContestResources;
struct ContestPokemon gContestMons[CONTESTANT_COUNT];
s16 gContestMonRound1Points[CONTESTANT_COUNT], gContestMonTotalPoints[CONTESTANT_COUNT], gContestMonAppealPointTotals[CONTESTANT_COUNT], gContestMonRound2Points[CONTESTANT_COUNT];
u8 gContestFinalStandings[CONTESTANT_COUNT], gContestPlayerMonIndex, gContestantTurnOrder[CONTESTANT_COUNT];
u16 gSpecialVar_ContestCategory, gSpecialVar_ContestRank;
const struct ContestMove *gContestMoves;
const struct ContestEffect *gContestEffects;
const u8 *gComboStarterLookupTable, *gContestAIScripts, *gAIScriptPtr;

u32 GFL_RandomLC(u32 max) { return (u32)rand() % max; }

static void *load(const char *path, long *size) {
    FILE *f = fopen(path, "rb");
    void *d;
    if (!f) { perror(path); exit(2); }
    fseek(f, 0, SEEK_END); *size = ftell(f); fseek(f, 0, SEEK_SET);
    d = malloc(*size); fread(d, 1, *size, f); fclose(f);
    return d;
}

int main(int argc, char **argv) {
    long n, oppSize;
    static struct ContestResources res;
    const ContestOpponentRec *opp;
    long appeals = 0, wins[4] = {0}, heartsTotal = 0, combos = 0, nervous = 0, repeats = 0;
    int runs = atoi(argv[5]);
    char path[1024];

    gContestMoves = load(argv[1], &n);
    gComboStarterLookupTable = (const u8 *)(gContestMoves + CONTEST_MOVES_COUNT);
    gContestEffects = load(argv[2], &n);
    opp = load(argv[3], &oppSize);
    gContestAIScripts = load(argv[4], &n);
    gContestResources = &res;
    (void)path;
    srand(12345);
    int count = oppSize / sizeof(ContestOpponentRec);
    if (sizeof(ContestOpponentRec) != 28) { printf("FAIL rec size %zu\n", sizeof(ContestOpponentRec)); return 1; }
    for (int run = 0; run < runs; run++) {
        int cat = rand() % 5, rank = rand() % 4, c = 0, pool[128];
        for (int i = 0; i < count; i++) if (opp[i].whichRank == rank && (opp[i].pools & (1 << cat))) pool[c++] = i;
        if (c < 4) { printf("FAIL pool %d rank %d cat %d: %d\n", run, rank, cat, c); return 1; }
        gSpecialVar_ContestCategory = cat; gSpecialVar_ContestRank = rank;
        gContestPlayerMonIndex = 3;
        for (int i = 0; i < 4; i++) {
            int pick = rand() % c; const ContestOpponentRec *r = &opp[pool[pick]];
            struct ContestPokemon *m = &gContestMons[i];
            memset(m, 0, sizeof(*m));
            m->species = r->species; m->aiFlags = r->aiFlags; memcpy(m->moves, r->moves, 8);
            m->cool = r->stats[0]; m->beauty = r->stats[1]; m->cute = r->stats[2]; m->smart = r->stats[3]; m->tough = r->stats[4]; m->sheen = r->stats[5];
            pool[pick] = pool[--c];
        }
        CalculateRound1Points(cat);
        memset(&res, 0, sizeof(res));
        for (int i = 0; i < 4; i++) { eContestantStatus[i].effectStringId = eContestantStatus[i].effectStringId2 = CONTEST_STRING_NONE; }
        SortContestants(FALSE);
        for (int i = 0; i < 4; i++) { eContestantStatus[i].nextTurnOrder = CONTESTANT_NONE; eContest.prevTurnOrder[i] = gContestantTurnOrder[i]; }
        ApplyNextTurnOrder();
        for (eContest.appealNumber = 0; eContest.appealNumber < CONTEST_NUM_APPEALS; eContest.appealNumber++) {
            eContest.playerMoveChoice = rand() % 4;
            for (int i = 0; i < 4; i++) if (i != 3) {} 
            // the "player" plays a random move, as GetChosenMove's other arm does for the AI
            GetAllChosenMoves();
            if (eContestantStatus[3].currMove == 0 && !Contest_IsMonsTurnDisabled(3)) eContestantStatus[3].currMove = gContestMons[3].moves[0];
            for (eContest.turnNumber = 0; eContest.turnNumber < 4; eContest.turnNumber++) {
                int i;
                for (i = 0; eContest.turnNumber != eContestAppealResults.turnOrder[i]; i++) { if (i > 3) { printf("FAIL order\n"); return 1; } }
                eContest.currentContestant = i;
                CalculateAppealMoveImpact(i);
                struct ContestantStatus *s = &eContestantStatus[i];
                if (s->nervous) nervous++;
                if (s->repeatedMove) { s->appeal -= s->repeatJam; repeats++; }
                if (s->usedComboMove && s->completedCombo) { s->appeal += s->comboAppealBonus; combos++; }
                if (!s->repeatedMove || eContestExcitement.moveExcitement <= 0) {
                    int ex = s->overrideCategoryExcitementMod ? 1 : eContestExcitement.moveExcitement;
                    if (!(eContestExcitement.frozen && i != eContestExcitement.freezer)) {
                        eContest.applauseLevel += ex;
                        if (eContest.applauseLevel < 0) eContest.applauseLevel = 0;
                        if (ex > 0) s->appeal += eContestExcitement.excitementAppealBonus;
                        if (eContest.applauseLevel > 4) eContest.applauseLevel = 0;
                    }
                }
                if (s->appeal > 2000 || s->appeal < -2000) { printf("FAIL appeal %d\n", s->appeal); return 1; }
                heartsTotal += s->appeal; appeals++;
                for (int j = 0; j < 4; j++) { eContestantStatus[j].effectStringId = eContestantStatus[j].effectStringId2 = CONTEST_STRING_NONE; }
            }
            RankContestants();
            SetAttentionLevels();
            SetContestantStatusesForNextRound();
            int seen = 0;
            for (int i = 0; i < 4; i++) seen |= 1 << gContestantTurnOrder[i];
            if (seen != 15) { printf("FAIL turn order not a permutation run %d\n", run); return 1; }
        }
        for (int i = 0; i < 4; i++) gContestMonAppealPointTotals[i] = eContestantStatus[i].pointTotal;
        CalculateFinalScores();
        int places = 0;
        for (int i = 0; i < 4; i++) { places |= 1 << gContestFinalStandings[i]; if (gContestFinalStandings[i] == 0) wins[i]++; }
        if (places != 15) { printf("FAIL places run %d\n", run); return 1; }
    }
    printf("OK %d contests, %ld appeals, mean appeal %.1f, %ld combos, %ld repeats, %ld nervous, wins %ld %ld %ld %ld\n", runs, appeals,
           (double)heartsTotal / appeals, combos, repeats, nervous, wins[0], wins[1], wins[2], wins[3]);
    return 0;
}
