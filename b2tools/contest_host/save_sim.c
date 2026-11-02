// The save's other half: b2tools/patches/berries.c's tree functions, as compiled for the game, on a block made as an old
// save has it: an existing save's trees stay as they were, and the Contests' bytes at +552 on survive a growth update.
#include <stdio.h>
#include <string.h>
#include "types.h"
#include "berries_extract.h"

static u8 block[996];

static u32 sum(int from, int to) { u32 s = 0; for (int i = from; i < to; i++) s = s * 31 + block[i]; return s; }

int main(void) {
    BerrySave *s = (BerrySave *)block;
    // a v18.x save: the set-up cleared 128 trees (+12 to +780), Pokéstar's bytes after it
    memset(block, 0, sizeof(block));
    s->magic = BERRY_MAGIC;
    for (int i = 780; i < 996; i++) block[i] = (u8)(0xA0 + i);
    // trees at each stage (ids 0-89), growing or waiting
    for (int i = 1; i < N_TREES; i++) {
        BerryTree *t = &s->trees[i];
        t->berry = (u8)(1 + i % 43);
        t->stage = (u8)(1 + i % 5) | (i % 7 == 0 ? STOP : 0);
        t->minutes = (u16)(i % 60 + 1);
        t->yield = (u8)(i % 5);
        t->flags = (u8)(i % 3);
    }
#ifdef OLD_BOUND
    // the same trees and updates with the old 128-tree loops, no Contest data: the first 552 bytes must come out the same
    for (int m = 1; m < 2000000; m = m * 3 + 1) {
        time_update_trees(s, m);
    }
    printf("%08x\n", sum(0, 552));
    return 0;
#endif
    // the Contests' data arrives at +552 (Pokeblock_GetSave: its magic, then blocks)
    block[552] = 'P'; block[553] = 'L'; block[554] = 'B'; block[555] = '3';
    for (int i = 556; i < 552 + 292; i++) block[i] = (u8)i;
    u32 contest = sum(552, 996);
    // growth updates, little and big
    for (int m = 1; m < 2000000; m = m * 3 + 1) {
        time_update_trees(s, m);
    }
    // the first 552 bytes moved only inside the trees' own records: header kept
    if (s->magic != BERRY_MAGIC) { printf("FAIL the trees' magic changed\n"); return 1; }
    if (sum(552, 996) != contest) { printf("FAIL the Contests' bytes changed in a growth update\n"); return 1; }
    // the trees beyond 90 no longer exist; the same growth on the first 552 bytes as with the old 128-tree loop:
    if (sizeof(BerrySave) != 12 + N_TREES * 6) { printf("FAIL BerrySave %zu\n", sizeof(BerrySave)); return 1; }
    // a save with the magic: save() leaves trees alone. An old save without trees' magic: the first set-up writes only
    // up to +552 (checked on the source by contest_check.py: it loops to N_TREES)
    printf("OK %08x a growth update leaves +552..+996 alone; BerrySave ends at +552\n", sum(0, 552));
    return 0;
}
