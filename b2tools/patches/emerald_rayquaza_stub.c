/* Emerald's Rayquaza cutscene, the part in the Frontier code area (emerald_art, 2026-10-12;
 * b2tools/patches/emerald_rayquaza_scene.py). Script command 494 (`EmRayquazaScene arg`, src/include/em_rayquaza_scene.inc)
 * -> RQ_Cmd: reads the scene's file (arc 211, RQ_FILE: emerald_rayquaza_scene.c with pokeemerald's rayquaza_scene.c and
 * engine, and Emerald's graphics from the user's dump) into Black 2's user heap, relocates it, and calls its Ray_Cmd,
 * which starts the scene as a proc; the script frees the file when the proc has ended (CreateScrCmdOverlayProcess's
 * resource). Without room in the heap the command does nothing (the screen stays black as long as the script waits).
 * File: a 32-byte header {'EMRQ', file size, memory size, Ray_Cmd offset, relocation table offset, relocation count,
 * image size, bss size}, the image (linked at 0), the table (offsets of the words to add the image's address to). */
typedef unsigned char u8;
typedef unsigned int u32;

#define FN(type, addr) ((type)((addr) | 1))
#define GFL_HeapAllocate                  FN(void *(*)(u32, u32, u32, const char *, u32), 0x0203a1fc)
#define GFL_HeapGetHighestAllocatableSize FN(u32 (*)(u32), 0x02039f90)
#define GFL_ArcSysCreateFileHandle        FN(void *(*)(u32, u32), 0x0204aa30)
#define GFL_ArcToolReadRange              FN(void (*)(void *, u32, u32, u32, void *), 0x0204ac58)
#define GFL_ArcToolFree                   FN(void (*)(void *), 0x0204ab0c)
#define cp15_flushDC                      ((void (*)(const void *, u32))0x0207b0ac)      /* ARM */
#define cp15_invalidateIC                 ((void (*)(const void *, u32))0x0207b0e8)      /* ARM */
#define ScriptReadAny                     FN(u32 (*)(void *, void *), 0x02154910)        /* ov012 */
#define HEAP (1 | 0x8000)          /* HEAPID_USER from its tail: the field is closed (FieldClose) when the scene runs */
#define MARGIN 0x10000             /* the scene's own buffers (sRayScene, decompressed tiles), allocated later */
#ifndef RQ_FILE
#error "RQ_FILE: the scene's file in arc 211"
#endif

typedef struct { u32 magic, fileSize, memSize, entry, relocOff, relocCount, imageSize, bssSize; } Head;
u32 RQ_lastFree;                   /* the heap's largest free block at the last call (for tests) */
u8 *RQ_lastBlob;                   /* where the file went (for tests) */

u32 RQ_Cmd(void *vm, void *env) {
    Head h;
    u8 *blob;
    u32 i, need, *rel;
    void *a = GFL_ArcSysCreateFileHandle(211, HEAP);
    GFL_ArcToolReadRange(a, RQ_FILE, 0, sizeof h, &h);
    need = h.fileSize > h.memSize ? h.fileSize : h.memSize;
    RQ_lastFree = GFL_HeapGetHighestAllocatableSize(1);
    if (h.magic != 0x51524D45 || RQ_lastFree < need + MARGIN) {
        GFL_ArcToolFree(a);
        ScriptReadAny(vm, env);
        return 0;
    }
    blob = GFL_HeapAllocate(HEAP, need, 0, "rq", 0);
    RQ_lastBlob = blob;
    GFL_ArcToolReadRange(a, RQ_FILE, 0, h.fileSize, blob);
    GFL_ArcToolFree(a);
    rel = (u32 *)(blob + h.relocOff);
    for (i = 0; i < h.relocCount; i++)
        *(u32 *)(blob + 32 + rel[i]) += (u32)blob + 32;
    for (i = 32 + h.imageSize; i < h.memSize; i += 4)
        *(u32 *)(blob + i) = 0;
    cp15_flushDC(blob, need);
    cp15_invalidateIC(blob, need);
    return ((u32 (*)(void *, void *, u8 *))(blob + 32 + h.entry))(vm, env, blob);
}
