/* Pokémon Emerald NDS: Emerald's Rayquaza cutscene on Black 2's main engine (emerald_art, 2026-10-12;
 * b2tools/patches/emerald_rayquaza_scene.py; notes/EMERALD_STORY.md section 8).
 *
 * pokeemerald's own src/rayquaza_scene.c runs unchanged, with pokeemerald's own engine files (sprite.c, task.c, bg.c,
 * palette.c, dma3_manager.c, trig.c), compiled by arm-none-eabi-gcc for the DS's ARM9 into one file that the script
 * command loads (emerald_rayquaza_stub.c). This file is the GBA's side of them on the DS: main.c's callbacks, the GPU
 * register buffer, the scanline effect, malloc, the BIOS calls they use (CpuSet, CpuFastSet, LZ77UnCompWram,
 * BgAffineSet, ObjAffineSet), the DMA macros (done by the CPU: Black 2 owns the DMA channels, and DMA would read RAM
 * behind the ARM9's data cache), and the sounds (Black 2's SE and cries, table in the .py).
 *
 * The picture: the GBA's 240x160 screen at (8,16) of the top screen. Black 2's main engine is the GBA's 2D engine with
 * the same registers, palette and OAM layout; VRAM bank A is the BG VRAM (0x06000000, as the GBA's), bank B the OBJ
 * VRAM (0x06400000: OBJ_VRAM0 in the build's gba/defines.h). Every register value the scene writes goes through
 * SetGpuReg and is written at VBlank moved by (8,16): text BG offsets -8/-16, the affine BGs' reference point by
 * -(8,16) through their matrix, window 0 +8/+16. Sprites: the scene's OAM (gMain.oamBuffer, loaded by its own LoadOam
 * into a RAM copy) is written to OAM entries 18-127 moved by (8,16), the affine matrices staying in their slots;
 * entries 0-17 are a black frame around the GBA screen (OBJ palette 15 colour 1, kept black after every palette
 * transfer; tiles 992-1023, which no scene reaches). Window 1 is the GBA screen (the scene's "outside" settings
 * inside it, its window 0 as its own); outside it only sprites show, without effects, so the frame covers anything
 * the scene draws beyond the GBA's edges. The bottom screen stays black.
 *
 * Timing: the scene's main callback (CB2) runs once per frame from the proc's Main; the GBA's VBlank interrupt work
 * (the scene's VBlank callback, the register buffer, the DMA3 queue) runs in Black 2's HBlank interrupt at the first
 * VBlank line (as the title's scene, patches/title_scene.c), and the per-line work (the scanline effect's HBlank DMA,
 * the scene's HBlank callback) on every line, with REG_VCOUNT read as the GBA line (DS line - 16). */
#include "global.h"
#include "main.h"
#include "sprite.h"
#include "task.h"
#include "bg.h"
#include "palette.h"
#include "gpu_regs.h"
#include "scanline_effect.h"
#include "decompress.h"
#include "malloc.h"
#include "dma3.h"
#include "sound.h"
#include "random.h"
#include "menu.h"
#include "menu_helpers.h"
#include "util.h"
#include "constants/songs.h"
#include "constants/species.h"
#include "constants/rgb.h"

void DoRayquazaScene(u8 animId, bool8 endEarly, MainCallback exitCallback);

/* ---- Black 2 (by address; arm9 unless noted) ------------------------------------------------------------------- */
#define B2(type, addr) ((type)((addr) | 1))
#define GFL_HeapAllocate           B2(void *(*)(u32, u32, u32, const char *, u32), 0x0203a1fc)
#define GFL_HeapFree               B2(void (*)(void *), 0x0203a24c)
#define GFL_HBlankTCBAdd           B2(void *(*)(void *, void *, u32), 0x02005680)
#define GFL_TCBRemove              B2(u32 (*)(void *), 0x0203a6a8)
#define GFL_BGSysSetVRAMBanks      B2(void (*)(const u32 *), 0x02046c40)
#define GFL_FadeSet                B2(void (*)(u32, s32, s32, s32), 0x0204e060)
#define GFL_SndSEPlay              B2(void (*)(u32), 0x02006254)
#define GFL_SndBGMPlay             B2(void (*)(u32, u32), 0x02005df4)
#define GFL_SndBGMGetID            B2(u32 (*)(void), 0x02005c9c)
#define GFL_SndBGMIsPlaying        B2(u32 (*)(void), 0x02005fa8)
#define GFL_SndSeqGetPlayerIndex   B2(s32 (*)(u32), 0x020061b8)
#define GFL_SndPlayerStop          B2(void (*)(s32), 0x02006268)
#define PokeVoice_Play             B2(u32 (*)(u32, u32, u32, u32, u32, u32, u32, const void *), 0x020069f4)
#define ScriptReadAny              B2(u32 (*)(void *, void *), 0x02154910)                  /* ov012 */
#define CreateScrCmdOverlayProcess B2(void (*)(void *, void *, s32, const void *, void *, void *, void *), 0x021574f4)  /* ov012 */

#define R16(a) (*(vu16 *)(a))
#define R32(a) (*(vu32 *)(a))
#define DS_DISPCNT      0x04000000
#define DS_VCOUNT       0x04000006
#define DS_MASTER_A     0x0400006C
#define DS_MASTER_B     0x0400106C
#define DS_IME          0x04000208
#define DS_OAM          0x07000000
#define BRIGHT_BLACK    0x8010
#define FRAME_TILE      992             /* 32 tiles: the frame's 64x32 pieces read 32 tiles in 1D mapping */
#define FRAME_SPRITES   18
#define DX 8
#define DY 16

/* The build fills these in (emerald_rayquaza_scene.py): Black 2 sound ids for Emerald's songs/SEs */
#ifndef RAY_SE_DOWNPOUR
#error "build with emerald_rayquaza_scene.py"
#endif

/* ---- main.c ----------------------------------------------------------------------------------------------------- */
struct Main gMain;
u8 gRayOam[OAM_SIZE] ALIGNED(4);          /* OAM in the build's gba/defines.h: LoadOam fills this */
u8 ALIGNED(4) gDecompressionBuffer[0x4000];
u32 gRngValue;

void SetMainCallback2(MainCallback callback) { gMain.callback2 = callback; gMain.state = 0; }
void SetVBlankCallback(IntrCallback callback) { gMain.vblankCallback = callback; }
void SetHBlankCallback(IntrCallback callback) { gMain.hblankCallback = callback; }
void EnableInterrupts(u16 mask) { (void)mask; }   /* Black 2's HBlank TCB runs on every line anyway */
void DisableInterrupts(u16 mask) { (void)mask; }
u16 Random(void) { gRngValue = ISO_RANDOMIZE1(gRngValue); return gRngValue >> 16; }

/* ---- malloc.c (Black 2's user heap, from the tail; every block freed at the end) -------------------------------- */
#define MAX_BLOCKS 48
static void *sBlocks[MAX_BLOCKS];
void *Alloc(u32 size) {
    int i;
    for (i = 0; i < MAX_BLOCKS; i++)
        if (!sBlocks[i])
            return sBlocks[i] = GFL_HeapAllocate(1 | 0x8000, size, 0, "rayscene", 0);
    return NULL;
}
void *AllocZeroed(u32 size) {
    u32 *p = Alloc(size), i;
    if (p) for (i = 0; i < (size + 3) / 4; i++) p[i] = 0;
    return p;
}
void Free(void *pointer) {
    int i;
    for (i = 0; i < MAX_BLOCKS; i++)
        if (pointer && sBlocks[i] == pointer) { GFL_HeapFree(pointer); sBlocks[i] = NULL; }
}

/* ---- the BIOS calls ---------------------------------------------------------------------------------------------- */
void *memcpy(void *d, const void *s, unsigned int n) { u8 *a = d; const u8 *b = s; while (n--) *a++ = *b++; return d; }
void *memset(void *d, int c, unsigned int n) { u8 *a = d; while (n--) *a++ = c; return d; }

#undef CpuSet
#undef CpuFastSet
void CpuSet(const void *src, void *dest, u32 control) {
    u32 n = control & 0x1FFFFF, fixed = control & 0x01000000;
    if (control & CPU_SET_32BIT) {
        const vu32 *s = (const vu32 *)((u32)src & ~3); vu32 *d = (vu32 *)((u32)dest & ~3);
        while (n--) { *d++ = *s; if (!fixed) s++; }
    } else {
        const vu16 *s = (const vu16 *)((u32)src & ~1); vu16 *d = (vu16 *)((u32)dest & ~1);
        while (n--) { *d++ = *s; if (!fixed) s++; }
    }
}
void CpuFastSet(const void *src, void *dest, u32 control) {
    u32 n = ((control & 0x1FFFFF) + 7) & ~7, fixed = control & 0x01000000;
    const vu32 *s = (const vu32 *)((u32)src & ~3); vu32 *d = (vu32 *)((u32)dest & ~3);
    while (n--) { *d++ = *s; if (!fixed) s++; }
}
void LZ77UnCompWram(const u32 *src, void *dest) {
    const u8 *s = (const u8 *)src;
    u8 *d = dest;
    u32 size = s[1] | s[2] << 8 | s[3] << 16, n = 0;
    s += 4;
    while (n < size) {
        u32 flags = *s++, b;
        for (b = 0; b < 8 && n < size; b++, flags <<= 1) {
            if (flags & 0x80) {
                u32 x = s[0] << 8 | s[1], len = (x >> 12) + 3, disp = (x & 0xFFF) + 1;
                s += 2;
                while (len-- && n < size) { d[n] = d[n - disp]; n++; }
            } else {
                d[n++] = *s++;
            }
        }
    }
}
/* the BIOS's sine table (1.14 fixed point, theta >> 8); every call of this scene has theta 0 (cos 0x4000, sin 0) */
extern const s16 gRayBiosSine[256];
void BgAffineSet(struct BgAffineSrcData *src, struct BgAffineDstData *dest, s32 count) {
    for (; count > 0; count--, src++, dest++) {
        s32 t = src->alpha >> 8, sn = gRayBiosSine[t], cs = gRayBiosSine[(t + 64) & 255];
        s32 pa = (src->sx * cs) >> 14, pb = -(src->sx * sn) >> 14, pc = (src->sy * sn) >> 14, pd = (src->sy * cs) >> 14;
        dest->pa = pa; dest->pb = pb; dest->pc = pc; dest->pd = pd;
        dest->dx = src->texX - (pa * src->scrX + pb * src->scrY);
        dest->dy = src->texY - (pc * src->scrX + pd * src->scrY);
    }
}
void ObjAffineSet(struct ObjAffineSrcData *src, void *dest, s32 count, s32 offset) {
    s16 *d = dest;
    for (; count > 0; count--, src++) {
        s32 t = src->rotation >> 8, sn = gRayBiosSine[t], cs = gRayBiosSine[(t + 64) & 255];
        d[0] = (src->xScale * cs) >> 14;
        d[offset / 2] = -(src->xScale * sn) >> 14;
        d[offset] = (src->yScale * sn) >> 14;
        d[offset * 3 / 2] = (src->yScale * cs) >> 14;
        d += offset * 2;
    }
}
/* the DMA macros (the build's gba/macro.h): immediate transfers by the CPU; timed ones (HBlank/VBlank) are only the
 * scanline effect's, done below */
void GbaDmaSet(u32 num, const void *src, void *dest, u32 control) {
    u32 n = control & 0xFFFF, c = control >> 16, w = c & DMA_32BIT ? 4 : 2;
    s32 ds = (c >> 5 & 3) == 1 ? -1 : (c >> 5 & 3) == 2 ? 0 : 1, ss = (c >> 7 & 3) == 1 ? -1 : (c >> 7 & 3) == 2 ? 0 : 1;
    const u8 *s = src;
    u8 *d = dest;
    (void)num;
    if (!(c & DMA_ENABLE) || (c & 0x3000)) return;
    if (!n) n = 0x10000;
    while (n--) {
        if (w == 4) *(vu32 *)d = *(const vu32 *)s; else *(vu16 *)d = *(const vu16 *)s;
        d += ds * (s32)w; s += ss * (s32)w;
    }
}
void GbaDmaStop(u32 num) { (void)num; }

/* ---- gpu_regs.c: the scene's register writes, written at VBlank moved to (8,16) ------------------------------------ */
static u16 sReg[0x30];
static u8 sDirty[0x30];
void InitGpuRegManager(void) { int i; for (i = 0; i < 0x30; i++) { sReg[i] = 0; sDirty[i] = 0; } }
void SetGpuReg(u8 off, u16 value) { if (off < 0x60) { sReg[off >> 1] = value; sDirty[off >> 1] = 1; } }
void SetGpuReg_ForcedBlank(u8 off, u16 value) { SetGpuReg(off, value); }
static u16 GbaVcount(void) { u16 v = R16(DS_VCOUNT); return v >= DY ? v - DY : v + 263 - DY; }
u16 GetGpuReg(u8 off) {
    if (off == REG_OFFSET_VCOUNT) return GbaVcount();
    if (off == REG_OFFSET_DISPSTAT) return R16(0x04000004);
    return off < 0x60 ? sReg[off >> 1] : 0;
}
void SetGpuRegBits(u8 off, u16 mask) { SetGpuReg(off, GetGpuReg(off) | mask); }
void ClearGpuRegBits(u8 off, u16 mask) { SetGpuReg(off, GetGpuReg(off) & ~mask); }

/* a GBA register value -> the DS's (address = the same offset) */
static u32 Translate(u32 off, u32 v) {
    switch (off) {
    case REG_OFFSET_BG0HOFS: case REG_OFFSET_BG1HOFS: case REG_OFFSET_BG2HOFS: case REG_OFFSET_BG3HOFS:
        return (v - DX) & 0x1FF;
    case REG_OFFSET_BG0VOFS: case REG_OFFSET_BG1VOFS: case REG_OFFSET_BG2VOFS: case REG_OFFSET_BG3VOFS:
        return (v - DY) & 0x1FF;
    case REG_OFFSET_WIN0H: {
        u32 l = v >> 8, r = v & 0xFF;
        l = l > 240 ? 240 : l; r = r > 240 ? 240 : r;
        return (l + DX) << 8 | (r + DX);
    }
    case REG_OFFSET_WIN0V: {
        u32 t = v >> 8, b = v & 0xFF;
        t = t > 160 ? 160 : t; b = b > 160 ? 160 : b;
        return (t + DY) << 8 | (b + DY);
    }
    }
    return v;
}
void CopyBufferedValuesToGpuRegs(void) {
    u32 i, g, mode;
    for (i = 0; i < 0x30; i++) {
        u32 off = i * 2;
        if (!sDirty[i]) continue;
        sDirty[i] = 0;
        if (off == REG_OFFSET_DISPCNT || off == REG_OFFSET_DISPSTAT || off == REG_OFFSET_VCOUNT
            || off == REG_OFFSET_WIN1H || off == REG_OFFSET_WIN1V || off == REG_OFFSET_WININ || off == REG_OFFSET_WINOUT
            || (off >= REG_OFFSET_BG2PA && off < REG_OFFSET_WIN0H))
            continue;                                   /* written below */
        R16(0x04000000 + off) = Translate(off, sReg[i]);
    }
    g = sReg[0];
    /* GBA mode 1 (BG2 affine, BG0/1 text) is the DS's mode 2 (the DS's mode 1 has BG2 as text and BG3 affine) */
    R32(DS_DISPCNT) = ((g & 7) == 1 ? 2 : g & 7) | (g & 0x0040 ? 0x10 : 0) | (g & 0x0080) | (g & 0x0F00) | 0x1000 | (g & 0x2000)
                      | 0x4000 | (g & 0x8000) | 0x10000;
    R16(0x04000042) = (DX << 8) | (240 + DX);           /* WIN1H / WIN1V: the GBA screen */
    R16(0x04000046) = (DY << 8) | (160 + DY);
    R16(0x04000048) = (sReg[REG_OFFSET_WININ >> 1] & 0x3F)
                      | ((g & 0x6000 ? sReg[REG_OFFSET_WINOUT >> 1] : 0x3F) & 0x3F) << 8;
    R16(0x0400004A) = 0x0010;                           /* outside: sprites (the frame) only, no effects */
    mode = g & 7;
    for (i = 2; i <= 3; i++) {                          /* affine BGs: the reference point moved by -(8,16) */
        u32 b = REG_OFFSET_BG2PA + (i - 2) * 0x10;
        s32 pa = (s16)sReg[b >> 1], pb = (s16)sReg[(b >> 1) + 1], pc = (s16)sReg[(b >> 1) + 2], pd = (s16)sReg[(b >> 1) + 3];
        s32 x = (s32)((sReg[(b >> 1) + 4] | (u32)sReg[(b >> 1) + 5] << 16) << 4) >> 4;
        s32 y = (s32)((sReg[(b >> 1) + 6] | (u32)sReg[(b >> 1) + 7] << 16) << 4) >> 4;
        if (!(mode == 2 || (mode == 1 && i == 2))) continue;
        R16(0x04000000 + b) = pa; R16(0x04000002 + b) = pb; R16(0x04000004 + b) = pc; R16(0x04000006 + b) = pd;
        R32(0x04000008 + b) = (x - DX * pa - DY * pb) & 0x0FFFFFFF;
        R32(0x0400000C + b) = (y - DX * pc - DY * pd) & 0x0FFFFFFF;
    }
}

/* ---- scanline_effect.c: its HBlank DMA done per line by the HBlank TCB --------------------------------------------- */
EWRAM_DATA u16 ALIGNED(4) gScanlineEffectRegBuffers[2][0x3C0];
EWRAM_DATA struct ScanlineEffect gScanlineEffect;
static const void *sHbSrc;              /* this frame's buffer (the GBA line 1 entry), 0 = off */
static u32 sHbOff, sHbWide;
void ScanlineEffect_Stop(void) {
    gScanlineEffect.state = 0;
    sHbSrc = NULL;
    if (gScanlineEffect.waveTaskId != TASK_NONE) { DestroyTask(gScanlineEffect.waveTaskId); gScanlineEffect.waveTaskId = TASK_NONE; }
}
void ScanlineEffect_Clear(void) {
    CpuFill16(0, gScanlineEffectRegBuffers, sizeof(gScanlineEffectRegBuffers));
    gScanlineEffect.dmaSrcBuffers[0] = NULL; gScanlineEffect.dmaSrcBuffers[1] = NULL;
    gScanlineEffect.dmaDest = NULL; gScanlineEffect.dmaControl = 0; gScanlineEffect.srcBuffer = 0;
    gScanlineEffect.state = 0; gScanlineEffect.unused16 = 0; gScanlineEffect.unused17 = 0;
    gScanlineEffect.waveTaskId = TASK_NONE;
}
void ScanlineEffect_SetParams(struct ScanlineEffectParams params) {
    if (params.dmaControl == SCANLINE_EFFECT_DMACNT_16BIT) {
        gScanlineEffect.dmaSrcBuffers[0] = (u16 *)gScanlineEffectRegBuffers[0] + 1;
        gScanlineEffect.dmaSrcBuffers[1] = (u16 *)gScanlineEffectRegBuffers[1] + 1;
    } else {
        gScanlineEffect.dmaSrcBuffers[0] = (u32 *)gScanlineEffectRegBuffers[0] + 1;
        gScanlineEffect.dmaSrcBuffers[1] = (u32 *)gScanlineEffectRegBuffers[1] + 1;
    }
    gScanlineEffect.dmaControl = params.dmaControl;
    gScanlineEffect.dmaDest = params.dmaDest;
    gScanlineEffect.state = params.initState;
    gScanlineEffect.unused16 = params.unused9;
    gScanlineEffect.unused17 = params.unused9;
}
static void HbWrite(const void *p) {
    if (sHbWide) {
        u32 v = *(const u32 *)p;
        R32(0x04000000 + sHbOff) = Translate(sHbOff, v & 0xFFFF) | Translate(sHbOff + 2, v >> 16) << 16;
    } else {
        R16(0x04000000 + sHbOff) = Translate(sHbOff, *(const u16 *)p);
    }
}
void ScanlineEffect_InitHBlankDmaTransfer(void) {
    if (gScanlineEffect.state == 0) return;
    if (gScanlineEffect.state == 3) { gScanlineEffect.state = 0; sHbSrc = NULL; return; }
    sHbOff = (u32)gScanlineEffect.dmaDest - 0x04000000;
    sHbWide = gScanlineEffect.dmaControl != SCANLINE_EFFECT_DMACNT_16BIT;
    sHbSrc = gScanlineEffect.dmaSrcBuffers[gScanlineEffect.srcBuffer];
    HbWrite((const u8 *)sHbSrc - (sHbWide ? 4 : 2));    /* the first line's value (setFirstScanlineReg) */
    gScanlineEffect.srcBuffer ^= 1;
}

/* ---- menu.c / menu_helpers.c (as pokeemerald's) ------------------------------------------------------------------ */
static void *sTempTileDataBuffer[0x20];
static u16 sTempTileDataBufferIdx;
void ResetVramOamAndBgCntRegs(void) {
    SetGpuReg(REG_OFFSET_DISPCNT, 0);
    SetGpuReg(REG_OFFSET_BG3CNT, 0); SetGpuReg(REG_OFFSET_BG2CNT, 0);
    SetGpuReg(REG_OFFSET_BG1CNT, 0); SetGpuReg(REG_OFFSET_BG0CNT, 0);
    CpuFill16(0, (void *)BG_VRAM, BG_VRAM_SIZE);       /* the GBA's VRAM: its 64 KB of BGs and 32 KB of sprites */
    CpuFill16(0, (void *)OBJ_VRAM0, OBJ_VRAM0_SIZE);
    CpuFill32(0, (void *)OAM, OAM_SIZE);
    CpuFill16(0, (void *)PLTT, PLTT_SIZE);
}
void ResetAllBgsCoordinates(void) {
    ChangeBgX(0, 0, BG_COORD_SET); ChangeBgY(0, 0, BG_COORD_SET); ChangeBgX(1, 0, BG_COORD_SET); ChangeBgY(1, 0, BG_COORD_SET);
    ChangeBgX(2, 0, BG_COORD_SET); ChangeBgY(2, 0, BG_COORD_SET); ChangeBgX(3, 0, BG_COORD_SET); ChangeBgY(3, 0, BG_COORD_SET);
}
void SetVBlankHBlankCallbacksToNull(void) { SetVBlankCallback(NULL); SetHBlankCallback(NULL); }
void ResetTempTileDataBuffers(void) {
    int i;
    for (i = 0; i < (int)ARRAY_COUNT(sTempTileDataBuffer); i++) sTempTileDataBuffer[i] = NULL;
    sTempTileDataBufferIdx = 0;
}
bool8 FreeTempTileDataBuffersIfPossible(void) {
    int i;
    if (!IsDma3ManagerBusyWithBgCopy()) {
        if (sTempTileDataBufferIdx) {
            for (i = 0; i < sTempTileDataBufferIdx; i++) FREE_AND_SET_NULL(sTempTileDataBuffer[i]);
            sTempTileDataBufferIdx = 0;
        }
        return FALSE;
    }
    return TRUE;
}
void *DecompressAndCopyTileDataToVram(u8 bgId, const void *src, u32 size, u16 offset, u8 mode) {
    const u8 *s = src;
    u32 sizeOut = s[1] | s[2] << 8 | s[3] << 16;
    void *ptr;
    if (sTempTileDataBufferIdx >= ARRAY_COUNT(sTempTileDataBuffer)) return NULL;
    ptr = Alloc(sizeOut);
    if (!size) size = sizeOut;
    if (ptr) {
        LZ77UnCompWram(src, ptr);
        if (mode == 0) LoadBgTiles(bgId, ptr, size, offset);
        else if (mode == 1) LoadBgTilemap(bgId, ptr, size, offset);
        sTempTileDataBuffer[sTempTileDataBufferIdx++] = ptr;
    }
    return ptr;
}

static bool8 sScheduledBgCopiesToVram[4];
void ClearScheduledBgCopiesToVram(void) { int i; for (i = 0; i < 4; i++) sScheduledBgCopiesToVram[i] = FALSE; }
void ScheduleBgCopyTilemapToVram(u8 bgId) { sScheduledBgCopiesToVram[bgId] = TRUE; }
void DoScheduledBgTilemapCopiesToVram(void) {
    int i;
    for (i = 0; i < 4; i++)
        if (sScheduledBgCopiesToVram[i] == TRUE) { CopyBgTilemapBufferToVram(i); sScheduledBgCopiesToVram[i] = FALSE; }
}

/* ---- util.c (pokeemerald's BlendPalette, as written; the rest of util.c is not needed) ---- */
void BlendPalette(u16 palOffset, u16 numEntries, u8 coeff, u16 blendColor)
{
    u16 i;
    for (i = 0; i < numEntries; i++)
    {
        u16 index = i + palOffset;
        struct PlttData *data1 = (struct PlttData *)&gPlttBufferUnfaded[index];
        s8 r = data1->r;
        s8 g = data1->g;
        s8 b = data1->b;
        struct PlttData *data2 = (struct PlttData *)&blendColor;
        gPlttBufferFaded[index] = RGB(r + (((data2->r - r) * coeff) >> 4),
                                      g + (((data2->g - g) * coeff) >> 4),
                                      b + (((data2->b - b) * coeff) >> 4));
    }
}

/* ---- decompress.c ------------------------------------------------------------------------------------------------ */
void LZDecompressWram(const u32 *src, void *dest) { LZ77UnCompWram(src, dest); }
u16 LoadCompressedSpriteSheet(const struct CompressedSpriteSheet *src) {
    struct SpriteSheet dest;
    LZ77UnCompWram(src->data, gDecompressionBuffer);
    dest.data = gDecompressionBuffer; dest.size = src->size; dest.tag = src->tag;
    return LoadSpriteSheet(&dest);
}
void LoadCompressedSpritePalette(const struct CompressedSpritePalette *src) {
    struct SpritePalette dest;
    LZ77UnCompWram(src->data, gDecompressionBuffer);
    dest.data = (void *)gDecompressionBuffer; dest.tag = src->tag;
    LoadSpritePalette(&dest);
}

/* ---- sound.c: Black 2's sounds (emerald_rayquaza_scene.py's table); songs only with the Hoenn music answer -------- */
static u8 sHoennMusic;
static u32 sRainPlaying;
void PlaySE(u16 songNum) {
    s32 p;
    switch (songNum) {
    case SE_DOWNPOUR:      GFL_SndSEPlay(RAY_SE_DOWNPOUR); sRainPlaying = 1; break;
    case SE_DOWNPOUR_STOP:                              /* Emerald's stops the downpour's loop */
        if (sRainPlaying && (p = GFL_SndSeqGetPlayerIndex(RAY_SE_DOWNPOUR)) >= 0) GFL_SndPlayerStop(p);
        sRainPlaying = 0;
        break;
    case SE_THUNDER:       GFL_SndSEPlay(RAY_SE_THUNDER); break;
    case SE_INTRO_BLAST:   GFL_SndSEPlay(RAY_SE_INTRO_BLAST); break;
    case SE_M_WHIRLPOOL:   GFL_SndSEPlay(RAY_SE_M_WHIRLPOOL); break;
    case SE_MUGSHOT:       GFL_SndSEPlay(RAY_SE_MUGSHOT); break;
    case SE_SLIDING_DOOR:  GFL_SndSEPlay(RAY_SE_SLIDING_DOOR); break;
    }
}
void PlayCry_Normal(u16 species, s8 pan) { (void)pan; PokeVoice_Play(species, 0, 64, 0, 0, 0, 0, 0); }
void PlayNewMapMusic(u16 songNum) {
    if (sHoennMusic && songNum == MUS_RAYQUAZA_APPEARS) GFL_SndBGMPlay(RAY_MUS_RAYQUAZA_APPEARS, 0xFFFF);
}
void StopMapMusic(void) {
    s32 p;
    if (sHoennMusic && GFL_SndBGMIsPlaying() && (p = GFL_SndSeqGetPlayerIndex(GFL_SndBGMGetID())) >= 0)
        GFL_SndPlayerStop(p);
}

/* ---- the frame, the OAM and the VBlank ----------------------------------------------------------------------------- */
static vu32 sFrames;
static u32 sRun, sDone, sInVBlank;
static void *sTcb;

static void FixOam(void) {
    vu16 *o = (vu16 *)DS_OAM;
    const u16 *b = (const u16 *)gRayOam;
    u32 i, objOn = sReg[0] & DISPCNT_OBJ_ON;
    static const u8 frame[FRAME_SPRITES][3] = {         /* y, x / 8, shape|size: 0 = 64x32, 1 = 8x32 */
        {240, 0, 0}, {240, 8, 0}, {240, 16, 0}, {240, 24, 0}, {176, 0, 0}, {176, 8, 0}, {176, 16, 0}, {176, 24, 0},
        {16, 0, 1}, {48, 0, 1}, {80, 0, 1}, {112, 0, 1}, {144, 0, 1},
        {16, 31, 1}, {48, 31, 1}, {80, 31, 1}, {112, 31, 1}, {144, 31, 1}};
    for (i = 0; i < 128; i++) o[i * 4 + 3] = b[i * 4 + 3];            /* the affine matrices stay where they are */
    for (i = 0; i < FRAME_SPRITES; i++) {
        u32 wide = !frame[i][2];
        o[i * 4] = frame[i][0] | (wide ? 0x4000 : 0x8000);
        o[i * 4 + 1] = frame[i][1] * 8 | (wide ? 0xC000 : 0x4000);
        o[i * 4 + 2] = FRAME_TILE | 15 << 12;             /* priority 0, palette 15 */
    }
    for (i = 0; i < 128 - FRAME_SPRITES; i++) {
        u16 a0 = b[i * 4], a1 = b[i * 4 + 1];
        vu16 *d = o + (i + FRAME_SPRITES) * 4;
        if (!objOn || (a0 & 0x0300) == 0x0200) { d[0] = 0x0200; d[1] = 0; d[2] = 0; continue; }
        d[0] = (a0 & 0xFF00) | ((a0 + DY) & 0xFF);
        d[1] = (a1 & 0xFE00) | ((a1 + DX) & 0x1FF);
        d[2] = b[i * 4 + 2];
    }
}

static void Ray_VBlank(void) {
    u32 i;
    if (gMain.vblankCallback) gMain.vblankCallback();
    gMain.vblankCounter2++;
    CopyBufferedValuesToGpuRegs();
    ProcessDma3Requests();
    FixOam();
    for (i = 0; i < 32 * 8; i++)                        /* the frame's tiles (the scene's VRAM resets clear them) */
        ((vu32 *)OBJ_VRAM0)[FRAME_TILE * 8 + i] = 0x11111111;
    *(vu16 *)(PLTT + 0x200 + (15 * 16 + 1) * 2) = 0;   /* the frame's black, whatever the fades do */
    sFrames++;
}

void Ray_HBlank(void *tcb, void *work) {
    u32 v = R16(DS_VCOUNT);
    (void)tcb; (void)work;
    if (v >= 192) {
        if (!sInVBlank) { sInVBlank = 1; Ray_VBlank(); }
    } else {
        s32 g = (s32)v + 1 - DY;                      /* the GBA line drawn next */
        sInVBlank = 0;
        if (sHbSrc && g >= 1 && g <= 159) HbWrite((const u8 *)sHbSrc + (g - 1) * (sHbWide ? 4 : 2));
    }
    if (gMain.hblankCallback) gMain.hblankCallback();
}

/* ---- the proc (Black 2's GameProc: Init / Main / Exit) ------------------------------------------------------------ */
static u8 sAnim, sEndEarly;
static u16 sOldIE, sOldDispstat;
static void CB2_RayDone(void) { sDone = 1; }

static u32 Ray_Init(void *proc, u32 *state, void *param, void *work) {
    /* bgMain A, bgExtPaletteMain -, bgSub C, -, objMain B, -, objSub D, -, textures -, texture palettes -, 1D 32K x2 */
    static const u32 banks[12] = {0x01, 0, 0x04, 0, 0x02, 0, 0x08, 0, 0, 0, 0x10, 0x10};
    u16 ime;
    u32 i;
    (void)proc; (void)state; (void)param; (void)work;
    GFL_BGSysSetVRAMBanks(banks);
    R16(DS_MASTER_B) = BRIGHT_BLACK;
    R32(DS_DISPCNT) = 0x10000;
    for (i = 0; i < 0x200; i++) ((vu32 *)PLTT)[i] = 0;
    for (i = 0; i < 256; i++) ((vu32 *)DS_OAM)[i] = i & 1 ? 0 : 0x0200;
    InitGpuRegManager();
    ClearDma3Requests();
    gMain.callback1 = NULL; gMain.callback2 = NULL; gMain.vblankCallback = NULL; gMain.hblankCallback = NULL;
    gMain.oamLoadDisabled = 0;
    gRngValue = R16(DS_VCOUNT) * 0x10001 + 0x5A5A;
    sFrames = sRun = sDone = sInVBlank = sRainPlaying = 0;
    sHbSrc = NULL;
    gScanlineEffect.waveTaskId = TASK_NONE;
    DoRayquazaScene(sAnim, sEndEarly, CB2_RayDone);
    R16(DS_MASTER_A) = 0;                               /* palettes and backdrop are black: the scene fades in itself */
    ime = R16(DS_IME); R16(DS_IME) = 0;
    sTcb = GFL_HBlankTCBAdd((void *)Ray_HBlank, NULL, 0);
    sOldIE = R16(0x04000210); sOldDispstat = R16(0x04000004);
    R16(0x04000004) = sOldDispstat | 0x10;              /* the HBlank interrupt on (Black 2's IRQ table runs the TCBs) */
    R16(0x04000210) = sOldIE | 2;
    R16(DS_IME) = ime;
    return TRUE;
}

static u32 Ray_Main(void *proc, u32 *state, void *param, void *work) {
    u32 f = sFrames, n = f - sRun;
    (void)proc; (void)state; (void)param; (void)work;
    if (n > 2) n = 2;
    while (n-- && !sDone)
        if (gMain.callback2) gMain.callback2();
    sRun = f;
    return sDone;
}

static u32 Ray_Exit(void *proc, u32 *state, void *param, void *work) {
    u16 ime = R16(DS_IME);
    s32 p;
    u32 i;
    (void)proc; (void)state; (void)param; (void)work;
    R16(DS_IME) = 0;
    GFL_TCBRemove(sTcb);
    R16(0x04000210) = (R16(0x04000210) & ~2) | (sOldIE & 2);
    R16(0x04000004) = (R16(0x04000004) & ~0x10) | (sOldDispstat & 0x10);
    R16(DS_IME) = ime;
    if (sRainPlaying && (p = GFL_SndSeqGetPlayerIndex(RAY_SE_DOWNPOUR)) >= 0) GFL_SndPlayerStop(p);
    GFL_FadeSet(3, 16, 16, 0);                          /* both screens black, as Black 2's procs end */
    R32(DS_DISPCNT) = 0x10000;
    for (i = 0; i < 256; i++) ((vu32 *)DS_OAM)[i] = i & 1 ? 0 : 0x0200;
    for (i = 0; i < MAX_BLOCKS; i++) if (sBlocks[i]) { GFL_HeapFree(sBlocks[i]); sBlocks[i] = NULL; }
    return TRUE;
}

const void *const gRayProcFuncs[3] = {(const void *)Ray_Init, (const void *)Ray_Main, (const void *)Ray_Exit};

/* The script command (emerald_rayquaza_stub.c calls this after loading the file): `EmRayquazaScene arg`, arg bits 0-2
 * Emerald's animId (0 RAY_ANIM_DUO_FIGHT_PRE, 1 RAY_ANIM_DUO_FIGHT ...), bit 6 end after that one sequence (Emerald:
 * animId 0 ends early, 1 runs on to the end), bit 7 the Hoenn music answer. The proc's resource is the loaded file:
 * the script frees it when the proc has ended. */
u32 Ray_Cmd(void *vm, void *env, u8 *blob) {
    u32 arg = ScriptReadAny(vm, env);
    sAnim = arg & 7;
    sEndEarly = sAnim == 0 || (arg & 0x40);
    sHoennMusic = (arg & 0x80) != 0;
    CreateScrCmdOverlayProcess(vm, env, -1, gRayProcFuncs, blob, NULL, NULL);
    return 1;
}
