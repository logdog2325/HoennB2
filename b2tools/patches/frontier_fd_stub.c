/* The Battle Factory / Battle Dome loader (frontier_factory_dome, 2026-10-12): the small part that lives in ITCM.
 * The engine itself (frontier_factory_dome.c, ~11 KB) does not fit the ITCM the other patches leave, so it is built
 * position-independent (clang -fropi) and kept as a file of the Battle Subway set archive (arc 211, FR_BLOB_FILE);
 * these three entry points load it into the game-event heap when they need it, run it, and free it again:
 *   FRS_Cmd        script command 505 (FrontierCmd): load, run the engine's FR_Cmd; free, unless the engine started an
 *                  event of its own (a party screen, the bracket): then FRS_Event frees it when that event ends.
 *   FRS_Event      the callback of the engine's events: calls the engine's callback (event data: {blob, callback, ...}).
 *   FRS_BuildSetup ov012 0x02166082's call (the Subway battle's setup): in a Factory / Dome battle the engine (loaded by
 *                  the FrontierCmd that starts the battle; its address in the Subway work's words 27/28) builds it;
 *                  every other Subway battle calls Black 2's func_ov033_0217c094 as before.
 * Blob header (16 bytes, b2tools/patches/frontier_factory_dome.py): 'FRFD', size, FR_Cmd offset, FR_BuildSetup offset.
 * After the read: cp15_flushDC + cp15_invalidateIC over the blob (code written as data, then run). */
typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;

#define FN(type, addr) ((type)((addr) | 1))
#define GFL_HeapAllocate           FN(void *(*)(u32, u32, u32, const char *, u32), 0x0203a1fc)
#define GFL_HeapFree               FN(void (*)(void *), 0x0203a24c)
#define GFL_HeapGetFreeSize        FN(u32 (*)(u32), 0x0203a2a8)
#define GFL_ArcSysCreateFileHandle FN(void *(*)(u32, u32), 0x0204aa30)
#define GFL_ArcToolReadRange       FN(void (*)(void *, u32, u32, u32, void *), 0x0204ac58)
#define GFL_ArcToolFree            FN(void (*)(void *), 0x0204ab0c)
#define cp15_flushDC               ((void (*)(const void *, u32))0x0207b0ac)      /* ARM */
#define cp15_invalidateIC          ((void (*)(const void *, u32))0x0207b0e8)      /* ARM */
#define ScriptReadAny              FN(u32 (*)(void *, void *), 0x02154910)
#define ScriptReadVar              FN(u16 *(*)(void *, void *), 0x021548e8)
#define BSubway_BuildSetup         FN(void *(*)(void *, void *), 0x0217c094)
#define ARC_SETS 211
#define HEAP 4                     /* HEAPID_GAMEEVENT: kept while the field closes for a party screen or a battle */
#define KEEP 0x100                 /* FR_Cmd's answer: an event of the engine runs on; free the blob when it ends */
#ifndef FR_BLOB_FILE
#define FR_BLOB_FILE 1890
#endif

typedef struct { u32 magic, size, cmd, setup; } Header;
typedef struct { u8 *blob; u32 (*cb)(void *, u32 *, void *); } EventHead;
u32 FRS_Event(void *event, u32 *state, void *data);

static u8 *load(void) {
    Header h;
    u8 *blob;
    void *a = GFL_ArcSysCreateFileHandle(ARC_SETS, HEAP | 0x8000);
    GFL_ArcToolReadRange(a, FR_BLOB_FILE, 0, sizeof(h), &h);
    if (h.magic != 0x44465246 || GFL_HeapGetFreeSize(HEAP) < h.size + 0x1000) { GFL_ArcToolFree(a); return 0; }
    blob = GFL_HeapAllocate(HEAP | 0x8000, h.size, 0, "frfd", 0);
    GFL_ArcToolReadRange(a, FR_BLOB_FILE, 0, h.size, blob);
    GFL_ArcToolFree(a);
    cp15_flushDC(blob, h.size);
    cp15_invalidateIC(blob, h.size);
    return blob;
}

u32 FRS_Cmd(void *vm, void *env) {
    u8 *blob = load();
    u32 r;
    if (!blob) {                    /* no room: the command does nothing, var = 0xFFFF (the scripts treat it as "no") */
        ScriptReadAny(vm, env); ScriptReadAny(vm, env); ScriptReadAny(vm, env);
        *ScriptReadVar(vm, env) = 0xFFFF;
        return 0;
    }
    r = ((u32 (*)(void *, void *, u8 *, void *))(blob + ((Header *)blob)->cmd + 1))(vm, env, blob, (void *)FRS_Event);
    if (!(r & KEEP)) GFL_HeapFree(blob);
    return r & 1;
}

u32 FRS_Event(void *event, u32 *state, void *data) {
    EventHead *h = data;
    u8 *blob = h->blob;
    u32 r = h->cb(event, state, data);
    if (r) GFL_HeapFree(blob);
    return r;
}

void *FRS_BuildSetup(u8 *bsw, void *gsys) {
    u16 *s = (u16 *)(bsw + 0x32);
    u8 *blob = (u8 *)((u32)s[27] | (u32)s[28] << 16);
    if ((s[14] == 0xF0D0 || s[14] == 0xD03E) && blob)
        return ((void *(*)(u8 *, void *))(blob + ((Header *)blob)->setup + 1))(bsw, gsys);
    return BSubway_BuildSetup(bsw, gsys);
}
