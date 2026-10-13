/* The Frontier code area's boot loader (frontier_palace_arena, 2026-10-12; notes/FRONTIER.md "Code space"): Pokémon
 * Emerald NDS only. b2tools/patches/frontier_area.py places it in ITCM and points main's call of GameInit (arm9
 * 0x0200515c) here: before the game starts (and again after every soft reset, which restarts main), the area's image
 * (arc 211 file FRAM_FILE: a 16-byte header 'FRAM', size, base, 0, then the code and data of every Frontier patch that
 * uses the area) is read to main RAM at its base (FRAM_BASE, above the heaps: the main arena's end moves down to it),
 * the caches are flushed, then GameInit runs as before. */
typedef unsigned int u32;

#define FN(type, addr) ((type)((addr) | 1))
#define GFL_ArcSysReadRange  FN(void (*)(void *, u32, u32, u32, u32), 0x0204a940)
#define GameInit             FN(void (*)(void), 0x02005264)
#define cp15_flushDC         ((void (*)(const void *, u32))0x0207b0ac)      /* ARM */
#define cp15_invalidateIC    ((void (*)(const void *, u32))0x0207b0e8)      /* ARM */
#ifndef FRAM_FILE
#define FRAM_FILE 1891
#define FRAM_BASE 0x023d0000
#define FRAM_SIZE 0x10000
#endif

void FRAM_Boot(void) {
    u32 h[4];
    GFL_ArcSysReadRange(h, 211, FRAM_FILE, 0, sizeof(h));
    if (h[0] == 0x4d415246 && h[2] == FRAM_BASE && h[1] <= FRAM_SIZE) {     /* 'FRAM' */
        GFL_ArcSysReadRange((void *)FRAM_BASE, 211, FRAM_FILE, sizeof(h), h[1]);
        cp15_flushDC((void *)FRAM_BASE, h[1]);
        cp15_invalidateIC((void *)FRAM_BASE, h[1]);
    }
    GameInit();
}
