/* Real TMs for the nine Gen 3 TM moves Black 2 has no TM for (new_tms, 2026-10-18): TM96-TM104 at Black 2's unused item
 * ids 120-128. Compiled and placed in ITCM by b2tools/patches/new_tms.py, which has the findings (the code sites, the
 * data it patches) and passes the table below as -D defines (one source of truth: NEW_TMS in new_tms.py).
 *
 * Black 2's four TM functions (arm9 pml_item.c) are replaced whole (new_tms.py puts a long jump at each one's start);
 * they behave exactly as Black 2's for every other item. The new TMs:
 *   - teach NEW_TM_MOVES[item - NEW_TM_FIRST];
 *   - use personal-data TM bit NEW_TM_BIT + (item - NEW_TM_FIRST) (bits 101-109: Black 2 uses 0-100 of the 128);
 *   - are numbered 96 + (item - NEW_TM_FIRST) in the Bag (its "No." line and its sort by number). */
typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef int s32;

#if !defined(NEW_TM_FIRST) || !defined(NEW_TM_COUNT) || !defined(NEW_TM_BIT) || !defined(NEW_TM_MOVES)
#error "NEW_TM_FIRST, NEW_TM_COUNT, NEW_TM_BIT and NEW_TM_MOVES come from new_tms.py"
#endif

#define ITEM_TM01 328
#define ITEM_TM92 419
#define ITEM_HM01 420
#define ITEM_HM06 425
#define ITEM_TM93 618
#define ITEM_TM95 620
#define TM_INDEX_TM93 98        /* TM_MOVE_LIST: TM01-TM92, HM01-HM06, TM93-TM95 */
#define FIRST_NEW_NUMBER 96     /* TM96 */

#define FN(type, addr) ((type)((addr) | 1))
#define WordSetNumber FN(void (*)(void *, u32, s32, u32, u32, u32), 0x0202451c)
#define TM_MOVE_LIST ((const u16 *)0x02090c84)

static const u16 kNewMoves[NEW_TM_COUNT] = { NEW_TM_MOVES };

static int is_new(u32 item) { return item - NEW_TM_FIRST < NEW_TM_COUNT; }

/* PML_ItemIsTMHM (arm9 0x02026a94) */
u32 NewTm_IsTMHM(u32 item) {
    item &= 0xffff;
    return (item >= ITEM_TM01 && item <= ITEM_HM06) || (item >= ITEM_TM93 && item <= ITEM_TM95) || is_new(item);
}

/* PML_ItemIsTM (arm9 0x02026abc) */
u32 NewTm_IsTM(u32 item) {
    item &= 0xffff;
    return (item >= ITEM_TM01 && item <= ITEM_TM92) || (item >= ITEM_TM93 && item <= ITEM_TM95) || is_new(item);
}

/* PML_ItemGetTMWazaID (arm9 0x02026ae4) */
u32 NewTm_GetMove(u32 item) {
    item &= 0xffff;
    if (is_new(item)) return kNewMoves[item - NEW_TM_FIRST];
    if (item >= ITEM_TM93 && item <= ITEM_TM95) return TM_MOVE_LIST[item - ITEM_TM93 + TM_INDEX_TM93];
    if (item >= ITEM_TM01 && item <= ITEM_HM06) return TM_MOVE_LIST[item - ITEM_TM01];
    return 0;
}

/* PML_ItemGetTMBitMask (arm9 0x02026b40): the personal-data bit (Black 2: TM01-92 = 0-91, TM93-95 = 92-94,
 * HM01-06 = 95-100), 0xff for anything else */
u32 NewTm_GetBit(u32 item) {
    item &= 0xffff;
    if (is_new(item)) return NEW_TM_BIT + (item - NEW_TM_FIRST);
    if (item >= ITEM_TM93 && item <= ITEM_TM95) return item - ITEM_TM93 + 92;
    if (item >= ITEM_HM01 && item <= ITEM_HM06) return item - ITEM_HM01 + 95;
    if (item >= ITEM_TM01 && item <= ITEM_TM92) return item - ITEM_TM01;
    return 0xff;
}

/* The Bag's "No. N" line (ov142 ItemMenuDisp_DrawItemInfo, which adds 1): the TM's number - 1 */
u32 NewTm_BagNumber(u32 item) {
    item &= 0xffff;
    if (is_new(item)) return FIRST_NEW_NUMBER - 1 + (item - NEW_TM_FIRST);
    return NewTm_GetBit(item);
}

/* The Bag's sort by number (ov142 ItemMenu_SortByNumber): TM01-TM95, then TM96 on, then the HMs */
u32 NewTm_SortKey(u32 item) {
    item &= 0xffff;
    if (item >= ITEM_HM01 && item <= ITEM_HM06) return 200 + (item - ITEM_HM01);
    return NewTm_BagNumber(item);
}

/* The same line's WordSetNumber call (2 digits, zero-padded): 3 digits from TM100 on, or the first digit shows "?" */
void NewTm_WordSetNumber(void *wordSet, u32 index, s32 number, u32 digits, u32 pad, u32 ascii) {
    if (number >= 100 && digits < 3) digits = 3;
    WordSetNumber(wordSet, index, number, digits, pad, ascii);
}
