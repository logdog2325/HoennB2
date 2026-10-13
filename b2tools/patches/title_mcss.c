/* The title's bottom screen: Kyogre (Sapphire) or Groudon (Ruby) playing its Black 2 battle animation (title_anim,
 * 2026-10-08). Compiled and placed by b2tools/patches/title.py (which has the findings) over Black 2's TitleG3D_*
 * functions in ov162 (src/ov162/title.c): the 3D Kyurem scene, its camera curve and its light are never loaded.
 *
 * The sprite is drawn by MCSS, Black 2's multi-cell sprite system in the main module (src/system/mcss.c,
 * include/system/mcss.h), set up the way Black 2's own 2D screens do it (ov265 func_ov265_0219a06c, the Pokedex
 * ov298 func_ov298_021a8df8/021a8e80): one sprite, character data at texture VRAM offset 0, "2D" mode
 * (func_0201aacc), scale 16, the sprite's files from SetupPokemonLoaderFSTool. Its animation (multi-cell animation
 * 0, play mode loop) runs on its own: MCSSSys_Update steps it once per frame, as on the summary screen.
 *
 * TitleG3D (the title's work, src/ov162/title.c) keeps its layout: +0 the MCSS system (was the G3D manager),
 * +8 the sprite (was the light), +12 the curve (stays NULL: only read in the attract swap, which title.py turns off),
 * +16 the camera.
 *
 * Build-time defines from title.py: TITLE_EYE_Z, TITLE_SPECIES, TITLE_X, TITLE_Y (fx32 position of the sprite's origin, in pixels
 * from the screen centre, y up: the camera below maps one unit to one pixel).
 */
typedef unsigned int u32;
typedef unsigned short u16;
typedef int fx32;
typedef struct { fx32 x, y, z; } VecFx32;
typedef struct { u32 arcId, character, palette, cells, cellAnime, multiCells, multiCellAnime, bin, unk20; } MCSSLoadInfo;
typedef struct {
    void *system;       /* MCSSSystem * */
    u16 scene;
    void *sprite;       /* MCSS * */
    void *curve;
    void *camera;       /* G3DCamera * */
} TitleG3D;

#define FX32(n) ((fx32)((n) * 4096))
#define FN(type, addr) ((type)((addr) | 1))
/* Black 2 functions (decomp symbols, config/b2_us/arm9/symbols.txt; all Thumb) */
#define MCSSSys_Create            FN(void *(*)(u32, u32), 0x020199e8)
#define MCSSSys_Free              FN(void (*)(void *), 0x02019a88)
#define MCSSSys_Update            FN(void (*)(void *), 0x02019ae8)
#define MCSSSys_Draw              FN(void (*)(void *), 0x02019c0c)
#define MCSSSys_Add               FN(void *(*)(void *, fx32, fx32, fx32, const MCSSLoadInfo *), 0x0201a8a8)
#define MCSSSys_Set2D             FN(void (*)(void *), 0x0201aacc)       /* func_0201aacc */
#define MCSSSys_SetCharOffset     FN(void (*)(void *, u32), 0x0201aefc)  /* func_0201aefc */
#define MCSS_SetScale             FN(void (*)(void *, const VecFx32 *), 0x0201ab88)
#define MCSS_PauseAnimation       FN(void (*)(void *), 0x0201ace0)
#define SetupPokemonLoaderFSTool  FN(void (*)(u32, u32, u32, u32, u32, MCSSLoadInfo *, u32), 0x0201c044)
#define GFL_BGSysSet3DBGPriority  FN(void (*)(u32), 0x02044bb8)
#define GFL_G3DSysReset           FN(void (*)(void), 0x02049a98)
#define GFL_G3DSysReqSwapBuffers  FN(void (*)(void), 0x02049aa0)
#define GFL_G3DSysMtxViewFlush    FN(void (*)(void), 0x02049af0)
#define GFL_G3DCameraCreate       FN(void *(*)(u32, fx32, fx32, fx32, fx32, fx32, fx32, fx32, const VecFx32 *, \
                                               const VecFx32 *, const VecFx32 *, u32), 0x0204a5c8)
#define GFL_G3DCameraFree         FN(void (*)(void *), 0x0204a630)
#define GFL_G3DCameraFlush        FN(void (*)(void *), 0x0204a638)

#define G3DCAM_PROJECTION_ORTHO 2
#define SEX_UNKNOWN 2           /* Kyogre and Groudon are genderless */

/* replaces TitleG3D_Init (ov162 0x0219d554) */
void TitleMcss_Init(TitleG3D *g3d, u32 heapId) {
    VecFx32 position, up, target, scale;
    MCSSLoadInfo info;

    /* An orthographic camera one unit per pixel, looking down -z at the screen centre */
    position.x = 0; position.y = 0; position.z = TITLE_EYE_Z;
    up.x = 0; up.y = FX32(1); up.z = 0;
    target.x = 0; target.y = 0; target.z = 0;
    g3d->camera = GFL_G3DCameraCreate(G3DCAM_PROJECTION_ORTHO, FX32(96), -FX32(96), -FX32(128), FX32(128), FX32(1),
                                      FX32(1024), 0, &position, &up, &target, heapId);
    g3d->system = MCSSSys_Create(1, heapId);
    MCSSSys_SetCharOffset(g3d->system, 0);
    MCSSSys_Set2D(g3d->system);
    /* species, form 0, genderless, not shiny, not an egg, front */
    SetupPokemonLoaderFSTool(TITLE_SPECIES, 0, SEX_UNKNOWN, 0, 0, &info, 0);
    g3d->sprite = MCSSSys_Add(g3d->system, TITLE_X, TITLE_Y, 0, &info);
    scale.x = FX32(16); scale.y = FX32(16); scale.z = FX32(1);
    MCSS_SetScale(g3d->sprite, &scale);
#ifdef TITLE_TEST_PAUSE
    MCSS_PauseAnimation(g3d->sprite);   /* test only (HOENN_TITLE_TEST_PAUSE=1): the first frame, the still's pose */
#endif
    /* the 3D layer (BG0) in front of BG3 (the backdrop and the credit line): equal priority, BG0 wins */
    GFL_BGSysSet3DBGPriority(0);
}

/* replaces TitleG3D_Draw (ov162 0x0219d70c) */
void TitleMcss_Draw(TitleG3D *g3d) {
    GFL_G3DCameraFlush(g3d->camera);
    GFL_G3DSysReset();
    GFL_G3DSysMtxViewFlush();
    MCSSSys_Update(g3d->system);
    MCSSSys_Draw(g3d->system);
    GFL_G3DSysReqSwapBuffers();
}

/* replaces TitleG3D_Free (ov162 0x0219d7b0); MCSSSys_Free removes the sprite too */
void TitleMcss_Free(TitleG3D *g3d) {
    MCSSSys_Free(g3d->system);
    GFL_G3DCameraFree(g3d->camera);
}
