/* PKHeX-compatible Emerald saves (save_compat, 2026-10-18; notes/SAVE_PKHEX.md). Pokémon Emerald NDS builds with
 * HOENN_SAVE_COMPAT=1 only. Linked into the Frontier code area (frontier_area.py: main RAM, loaded before GameInit, so
 * before SaveControl_Create's load) by b2tools/patches/save_compat.py, which also has the hook sites.
 *
 * The Frontier's two save blocks keep Black 2's sizes (0x38: 60 bytes, 0x3e: 16), so the game's CRC of each covers
 * exactly what PKHeX checks. Their extra data lives after the block's 4-byte footer, in the rest of its 256-byte slot
 * (SaveData_BuildTable rounds size + 4 up to 0x100), with a CRC-16 of its own after it:
 *
 *   block 0x38 (slot 0x21A00): [Black 2's 60][footer 4][records: keys 0-94, 190 B][ext CRC 2]   = 256 B
 *   block 0x3e (slot 0x23600): [Black 2's 16][footer 4][PySave, PY_STATE B][ext CRC 2]           = 22 + PY_STATE B
 *
 * Black 2's save code never writes, compares or checks the bytes after a footer (backup_system.c: func_0203b92c
 * writes size + 4, func_0203b81c compares size, the loader checks CRC(size)); it only reads them (a load reads the
 * whole copy). So three hooks:
 *   SC_WriteLen  func_0203b92c's getSizeOfSaveBlockData call (the write length - 4): the slot's used length - 4, after
 *                sealing the extension (its CRC); main save, these two blocks only
 *   SC_CmpLen    func_0203b81c's getSizeOfSaveBlockData call (the length compared with the card before a save): the
 *                used length, so a change in the extension alone makes the block dirty
 *   SC_Load      SaveControl's two calls of func_0203ae4c (the main save's load): Black 2's load; if it says broken,
 *                Black 2's load again with the enlarged sizes of the builds before this one (0x38 252, 0x3e 16 +
 *                PY_STATE; each combination), and on success the migration: the extension moved 4 bytes up (the
 *                footer's place), the block marked to be written. Then each extension's CRC: a bad one is taken from
 *                whichever copy in the card has a good one, else cleared (and the block marked to be written).
 */
typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;

#define FN(type, addr) ((type)((addr) | 1))
#define SaveData_Load          FN(u32 (*)(u8 *, u32), 0x0203ae4c)            /* func_0203ae4c(sv, heapId) */
#define getSizeOfSaveBlockData FN(u32 (*)(u8 *, u32), 0x0203c3b0)
#define SaveData_GetBlockPtr   FN(u8 *(*)(u8 *, u32), 0x0203ad84)
#define SaveData_ReadCopy      FN(u32 (*)(u8 *, u32, u32, void *, u32), 0x0203bf48)   /* func_0203bf48(sv, id, 0 main / 1 backup, dest, size) */
#define g_SaveControlWork      (*(u8 **)0x02140f60)                          /* SaveControl; +16 the main SaveData */

/* struct SaveData (backup_system.c) */
#define SV_TABLE   44
#define SV_DATA    52
#define SV_CMPBUF  56              /* compareBuffer[256]: used only while a save compares blocks */
#define SV_STATUS  312             /* blockStatus: 2 bits a block */
/* struct SaveDataTable (savedata.c), SaveBlockInfo {id, size, offset} */
#define TBL_BLOCKS 20

#define LOAD_OK          1
#define LOAD_OK_PARTIAL  2
#define LOAD_BROKEN      3
#define STATUS_WRITE_MAIN 1

#ifndef PY_STATE
#error "PY_STATE (sizeof(PySave), frontier_pyramid.py SAVE_STATE) comes from save_compat.py"
#endif
#define N_BLK 2
/* block id, Black 2's size, the old enlarged size, extension length (the extension starts at size + 4) */
static const u16 kId[N_BLK]  = {0x38, 0x3e};
static const u16 kB2[N_BLK]  = {60, 16};
static const u16 kOld[N_BLK] = {252, 16 + PY_STATE};
static const u16 kExt[N_BLK] = {190, PY_STATE};               /* 0x38: keys 0-94 (key 95, never claimed, gives way to the CRC) */
#define USED(k) (kB2[k] + 4 + kExt[k] + 2)

static u16 crc16(const u8 *p, u32 n) {                        /* CRC-16/CCITT, init 0xFFFF (as Black 2's and PKHeX's) */
    u32 c = 0xFFFF, i;
    while (n--) {
        c ^= (u32)*p++ << 8;
        for (i = 0; i < 8; i++) c = c & 0x8000 ? (c << 1) ^ 0x1021 : c << 1;
    }
    return (u16)c;
}

static u16 *ext_crc(u8 *slot, u32 k) { return (u16 *)(slot + kB2[k] + 4 + kExt[k]); }
static void seal(u8 *slot, u32 k) { *ext_crc(slot, k) = crc16(slot + kB2[k] + 4, kExt[k]); }
static u32 ext_ok(u8 *slot, u32 k) { return *ext_crc(slot, k) == crc16(slot + kB2[k] + 4, kExt[k]); }

static u8 *main_sv(void) {
    u8 *sc = g_SaveControlWork;
    return sc ? *(u8 **)(sc + 16) : 0;
}

static void set_status(u8 *sv, u32 id, u32 st) {
    u32 *w = *(u32 **)(sv + SV_STATUS) + (id >> 4), sh = (id & 15) * 2;
    *w = (*w & ~(3u << sh)) | st << sh;
}

static void set_sizes(u8 *sv, u32 mask) {                     /* bit k: block k at its old enlarged size */
    u8 *blocks = *(u8 **)(*(u8 **)(sv + SV_TABLE) + TBL_BLOCKS);
    u32 k;
    for (k = 0; k < N_BLK; k++) *(u32 *)(blocks + 12 * kId[k] + 4) = mask >> k & 1 ? kOld[k] : kB2[k];
}

/* which of the two blocks (table, id) is, in the main save at Black 2's size; N_BLK = neither */
static u32 which(u8 *table, u32 id, u32 size) {
    u8 *sv = main_sv();
    u32 k;
    if (!sv || table != *(u8 **)(sv + SV_TABLE)) return N_BLK;
    for (k = 0; k < N_BLK && !(id == kId[k] && size == kB2[k]); k++) ;
    if (k < N_BLK) seal(SaveData_GetBlockPtr(sv, id), k);
    return k;
}

u32 SC_CmpLen(u8 *table, u32 id) {
    u32 n = getSizeOfSaveBlockData(table, id), k = which(table, id, n);
    return k < N_BLK ? USED(k) : n;
}

u32 SC_WriteLen(u8 *table, u32 id) {                          /* the caller writes this + 4 (the footer) */
    u32 n = getSizeOfSaveBlockData(table, id), k = which(table, id, n);
    return k < N_BLK ? USED(k) - 4 : n;
}

u32 SC_Load(u8 *sv, u32 heap) {
    static const u8 kTry[3] = {3, 1, 2};                      /* both enlarged (every Emerald release), 0x38 only, 0x3e only */
    u32 r = SaveData_Load(sv, heap), mask = 0, i, k, c;
    if (r == LOAD_BROKEN) {
        for (i = 0; i < 3; i++) {
            u32 r2;
            set_sizes(sv, kTry[i]);
            r2 = SaveData_Load(sv, heap);
            set_sizes(sv, 0);
            if (r2 == LOAD_OK || r2 == LOAD_OK_PARTIAL) { r = r2; mask = kTry[i]; break; }
        }   /* none: as Black 2's broken load (the RAM is the main copy, every block to be written) */
    }
    if (r != LOAD_OK && r != LOAD_OK_PARTIAL) return r;
    for (k = 0; k < N_BLK; k++) {
        u8 *slot = SaveData_GetBlockPtr(sv, kId[k]);
        if (mask >> k & 1) {                                   /* old form: [B2][ext][footer] -> [B2][footer][ext][crc] */
            u16 count = *(u16 *)(slot + kOld[k]);              /* the old footer's save count */
            for (i = kExt[k]; i--; ) slot[kB2[k] + 4 + i] = slot[kB2[k] + i];
            *(u16 *)(slot + kB2[k]) = count;
            *(u16 *)(slot + kB2[k] + 2) = 0;                   /* the CRC: the save computes it */
            seal(slot, k);
            set_status(sv, kId[k], STATUS_WRITE_MAIN);
        } else if (!ext_ok(slot, k)) {
            u8 *buf = sv + SV_CMPBUF;
            for (c = 0; c < 2; c++)
                if (SaveData_ReadCopy(sv, kId[k], c, buf, USED(k)) && ext_ok(buf, k)) break;
            for (i = 0; i < kExt[k]; i++) slot[kB2[k] + 4 + i] = c < 2 ? buf[kB2[k] + 4 + i] : 0;
            seal(slot, k);
            set_status(sv, kId[k], STATUS_WRITE_MAIN);
        }
    }
    return r;
}
