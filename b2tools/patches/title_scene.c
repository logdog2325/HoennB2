/* The title's bottom screen: Sapphire's own title scene (Ruby: Ruby's), as pokeruby's src/title_screen.c draws it
 * (title_anim, 2026-10-11; the findings are in b2tools/patches/title.py SCENE_DOC). Compiled and placed by title.py over
 * Black 2's TitleG3D_* functions in ov162 (src/ov162/title.c): the 3D Kyurem scene is never loaded.
 *
 * Three 2D layers on the main engine, all 4bpp, sharing BG3's characters (a/0/2/6 file 9, char base 0x4000):
 *   BG3 (priority 0): Black 2's "Developed by GAME FREAK inc." line (file 10, made by TitleBG_Init)
 *   BG2 (priority 1): the sea (Ruby: the lava), Sapphire's water_map (file TITLE_FILE_MON + 1)    = Sapphire's BG1, blend target 1
 *   BG1 (priority 2): the dark Kyogre over its gradient, Sapphire's kyogre_map (file TITLE_FILE_MON) = Sapphire's BG0, target 2
 * and the same blend as Sapphire's phase 3 (BLDCNT 0x2142: BG1 over BG0 + backdrop, EVA 15, EVB 31 = 16).
 * Everything that moves is done by an HBlank task (GFL_HBlankTCBAdd, as Black 2's Pokedex ov299 does), so it is
 * locked to the display like Sapphire's VBlank/HBlank-DMA effects and keeps its speed if the main loop lags:
 *   - each line: the sea's x offset = Sapphire's wave (ScanlineEffect_InitWave(0, 160, 4, 4, 0, BG1HOFS): sine,
 *     4 px, 64 lines long, one line further up every frame)
 *   - each frame (the first VBlank line): the frame counter and the colour of Kyogre's markings, palette 14 colour 15
 *     (UpdateLegendaryMarkingColor: every 4th frame, red 0..31 and back over 256 frames; Ruby: blue)
 *   - each VBlank line: the sea's y offset = Sapphire's gBattle_BG1_Y (one pixel up every second frame), line 0's x
 *     offset, the blend registers
 * Frame n of the counter shows what Sapphire shows after its phase-3 frame n.
 *
 * TitleG3D (the title's work, src/ov162/title.c) keeps its size: +0 the HBlank task (was the G3D manager), +4 the
 * frame counter, +8 the VBlank flag, +12 the curve (stays NULL: only read in the attract swap, which title.py turns off).
 *
 * Build-time defines from title.py: TITLE_HBLANK (address of TitleScene_HBlank), TITLE_SETUP (address of Black 2's
 * sBGSetupMain3), TITLE_FILE_MON (a/0/2/6 file of BG1's map; BG2's is the next one), TITLE_MARK_SHIFT (0 red, 10 blue), TITLE_WAVE0
 * (the wave's phase at frame 0).
 *
 * TITLE_EMERALD (emerald_art, 2026-10-12; b2tools/title_art.py "Emerald"): the bottom screen is Emerald's own scene,
 * pokeemerald's src/title_screen.c phase 3: BG1 = the dark Rayquaza, BG2 = the clouds, the same wave and targets as
 * Sapphire's, but the clouds rise one pixel every 4 frames (gBattle_BG1_Y = tBg1Y / 2), the blend is BLDALPHA_BLEND(6, 15),
 * and the markings' colour follows Emerald's cosine (UpdateLegendaryMarkingColor): 64 BGR555 values computed by title.py
 * from pokeemerald's gSineTable, given as TITLE_MARK_DATA and stored as the data-only function TitleScene_Marks, which
 * title.py places at TITLE_MARKS (TitleG3D_Draw's room, after TitleScene_Draw) and checks after compiling. The top screen
 * is the Sapphire/Ruby one (the logo of data/title/emerald, Black 2's strip and PRESS START).
 */
typedef unsigned int u32;
typedef unsigned short u16;
typedef unsigned char u8;

typedef struct {
    u32 x, y, screenSize, screenOffset;
    u8 resolution, colorMode, screenBase, charBase;
    u32 charSize;
    u8 extPaletteSlot, priority, areaOverflow, pad;
    u32 mosaic;
} BGSetup;      /* include/gfl/bg_sys.h, 32 bytes */

typedef struct {
    void *tcb;          /* the HBlank task */
    u32 frame;          /* frames since the title started */
    u32 inVBlank;       /* the last line seen was a VBlank line */
    void *curve;        /* NULL */
    u32 unused16;
} TitleScene;

#define FN(type, addr) ((type)((addr) | 1))
/* Black 2 functions (decomp symbols, config/b2_us/arm9/symbols.txt; all Thumb) */
#define GFL_HBlankTCBAdd          FN(void *(*)(void *, void *, u32), 0x02005680)
#define GFL_TCBRemove             FN(u32 (*)(void *), 0x0203a6a8)
#define GFL_BGSysCreateBG         FN(void (*)(u32, const BGSetup *, u32), 0x0204476c)
#define GFL_BGSysSet3DBGPriority  FN(void (*)(u32), 0x02044bb8)
#define GFL_BGSysSetBGEnabled     FN(void (*)(u32, u32), 0x02044c98)
#define GFL_BGSysLoadScr          FN(void (*)(u32), 0x02044f90)
#define GFL_G3DSysReqSwapBuffers  FN(void (*)(void), 0x02049aa0)
#define LoadScrFromArc            FN(void (*)(u32, u32, u32, u32, u32, u32, u32), 0x0204af18)
                                  /* loadBGScrToVramByNarcNoReserveNegAlign(arc, file, bg, offset, size, compressed, heap) */

#define REG16(a) (*(volatile u16 *)(a))
#define REG_VCOUNT    0x04000006
#define REG_BG2HOFS   0x04000018
#define REG_BG2VOFS   0x0400001a
#define REG_BLDCNT    0x04000050
#define REG_BLDALPHA  0x04000052
#define REG_IME       0x04000208
#define MARK_COLOUR   (0x05000000 + (14 * 16 + 15) * 2)   /* main BG palette 14, colour 15 */
#define ARCID_TITLE 26

#if TITLE_EMERALD
#define SCENE_VOFS(n)  (((n) + 1) >> 2)     /* Emerald: tBg1Y = (n + 1) >> 1, gBattle_BG1_Y = tBg1Y / 2 */
#define SCENE_BLDALPHA 0x0f06               /* EVA 6, EVB 15 */
#define STR_(...) #__VA_ARGS__
#define STR(...) STR_(__VA_ARGS__)
/* data only (64 halfwords): Emerald's marking colour for frames 0, 4, ... 252; placed at TITLE_MARKS by title.py */
__attribute__((naked)) void TitleScene_Marks(void) {
    __asm__(".short " STR(TITLE_MARK_DATA));
}
#else
#define SCENE_VOFS(n)  (((n) + 1) >> 1)     /* Sapphire: gBattle_BG1_Y + 1 every second frame */
#define SCENE_BLDALPHA 0x100f               /* EVA 15, EVB 16 */
#endif

/* Sapphire's wave: gSineTable[4 * j] * 4 / 256 (C division), j = 0..63; checked against pokeruby's table by title.py */
static inline int wave(u32 j) {
    u32 q = j & 31, k = q <= 16 ? q : 32 - q;
    int v = (k >= 3) + (k >= 6) + (k >= 9) + (k >= 16);
    return j & 32 ? -v : v;
}

/* placed at TITLE_HBLANK; runs in the HBlank interrupt (GFLAppIRQHBlank -> GFL_HBlankTCBUpdate) after every line.
 * An interrupt can come late (seen in DeSmuME: now and then one line late), so the frame changes on the first VBlank
 * line seen, whichever it is, and the VBlank writes are repeated on every VBlank line. */
void TitleScene_HBlank(void *tcb, TitleScene *s) {
#if TITLE_EMERALD
    u32 v = REG16(REG_VCOUNT), line, n = s->frame;
#else
    u32 v = REG16(REG_VCOUNT), line, n = s->frame, m, c;
#endif
    if (v >= 192) {                     /* VBlank: set up the next frame */
        if (!s->inVBlank) {
            s->inVBlank = 1;
            n = ++s->frame;
#if TITLE_EMERALD                       /* UpdateLegendaryMarkingColor((u8)n) at the last multiple of 4 */
            REG16(MARK_COLOUR) = ((const u16 *)TITLE_MARKS)[(n >> 2) & 63];
#else
            m = (n >> 2) & 63;          /* UpdateLegendaryMarkingColor((u8)n) at the last multiple of 4 */
            c = m & 32 ? 31 - (m & 31) : m & 31;
            REG16(MARK_COLOUR) = c << TITLE_MARK_SHIFT;
#endif
        }
        line = 0;
        REG16(REG_BG2VOFS) = SCENE_VOFS(n);
        REG16(REG_BLDCNT) = 0x2244;     /* target 1 BG2, alpha blend, target 2 BG1 + backdrop */
        REG16(REG_BLDALPHA) = SCENE_BLDALPHA;
    } else {
        s->inVBlank = 0;
        line = v + 1;                   /* the next line (192 for line 191: not drawn) */
    }
    REG16(REG_BG2HOFS) = wave(line + n + TITLE_WAVE0);
}

/* replaces TitleG3D_Init (ov162 0x0219d554) */
void TitleScene_Init(TitleScene *s, u32 heapId) {
    BGSetup b;
    const u32 *src = (const u32 *)TITLE_SETUP;      /* Black 2's sBGSetupMain3: BG3's text setup, chars at 0x4000 */
    u32 *dst = (u32 *)&b, i;
    u16 ime;
    for (i = 0; i < sizeof b / 4; i++)
        dst[i] = src[i];
    for (i = 1; i <= 2; i++) {          /* BG1 = the legendary (file TITLE_FILE_MON), BG2 = the sea (the next file) */
        b.screenBase = i + 1;           /* BG1 at 0x1000, BG2 at 0x1800 (BG3's screen is at 0x0800) */
        b.priority = 3 - i;
        GFL_BGSysCreateBG(i, &b, 0);
        LoadScrFromArc(ARCID_TITLE, TITLE_FILE_MON - 1 + i, i, 0, 0, 1, heapId);
        GFL_BGSysLoadScr(i);
        GFL_BGSysSetBGEnabled(i, 1);
    }
    GFL_BGSysSet3DBGPriority(3);        /* nothing is drawn in 3D; behind everything */
    ime = REG16(REG_IME); REG16(REG_IME) = 0;
    s->tcb = GFL_HBlankTCBAdd((void *)(TITLE_HBLANK | 1), s, 0);
    REG16(REG_IME) = ime;
}

/* replaces TitleG3D_Draw (ov162 0x0219d70c) */
void TitleScene_Draw(TitleScene *s) {
    GFL_G3DSysReqSwapBuffers();         /* an empty 3D frame */
}

/* replaces TitleG3D_Free (ov162 0x0219d7b0) */
void TitleScene_Free(TitleScene *s) {
    u16 ime = REG16(REG_IME);
    REG16(REG_IME) = 0;
    GFL_TCBRemove(s->tcb);
    REG16(REG_IME) = ime;
    REG16(REG_BLDCNT) = 0;
    REG16(REG_BG2HOFS) = 0;
    REG16(REG_BG2VOFS) = 0;
}
