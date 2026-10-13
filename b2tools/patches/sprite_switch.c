/* The sprite style, Birch's 4th question (CLASSIC = src/sprites, NEW = src/sprites_gen5 over it): code in ITCM, compiled
 * and linked by b2tools/patches/sprite_switch.py (which has the hook sites and writes sprite_switch_data.h).
 *
 * The choice: the options u16 at the start of the trainer-data save block (SaveControl block 27), bit 14 (fairy.py's
 * intro script writes it with Intro_SetConfigBit; 0 for a new game answering CLASSIC and for every older save).
 * With NEW, a file number of the classic set is swapped for its Gen 5 copy (extra entries the build appended) at the
 * moment Black 2 picks the file, so only one set is ever loaded:
 *   - overworld sheets (ARCID_MMODEL_GRA 48): the field's two sheet loads (ov036 func_ov036_02193d54 and
 *     FldBlAct_ExecAsyncRead, both GFL_G3DSysReadArcToolResource(handle, res1)) and the one-frame billboard helper
 *     func_02016510 (arm9: name entry icon, PWT, Join Avenue ...: any archive, only 48 is remapped);
 *   - trainer pictures (ARCID_TRSPRITE_FRONT 71 / _BACK 72): the sprite number GetTrSpriteBaseDatID gives to the eight
 *     GetTrSprite*DatID functions, through which every trainer picture file id goes;
 *   - the player's icons (a/0/3/0: Continue panel, GTS, Spin Trade, Battle Video, Wi-Fi 2D room) and the trainer card
 *     pictures (a/0/4/0): those archives have no room, so their Gen 5 copies are entries of a/0/4/8 (kIcons: archive,
 *     file, copy); each hooked load reads the copy from a/0/4/8 instead (a handle opened and freed around the call).
 * With CLASSIC nothing changes but the table lookups' absence (the original call with the original number). */
typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;

#define FN(type, addr) ((type)((addr) | 1))
#define SaveControl_GetBlockPtr        FN(u8 *(*)(void *, u32), 0x02007448)
#define GFL_G3DSysReadArcToolResource  FN(void *(*)(void *, u32), 0x02049384)
#define GetTrSpriteBaseDatID           FN(u32 (*)(u32, u32), 0x02030740)
#define g_SaveControlWork              (*(void **)0x02140f60)
#define GFL_ArcSysCreateFileHandle     FN(void *(*)(u32, u32), 0x0204aa30)
#define GFL_ArcToolFree                FN(void (*)(void *), 0x0204ab0c)
#define ClactLoadChars                 FN(u32 (*)(void *, u32, u32, u32, u32), 0x0204b81c)          /* func_0204b81c */
#define ClactLoadPalEx                 FN(u32 (*)(void *, u32, u32, u32, u32, u32, u32), 0x0204bbb8) /* func_0204bbb8 */
#define GFL_G2DIOReadBGNCGR            FN(void *(*)(u32, u32, u32, void *, u32), 0x0204b264)
#define GFL_BGSysLoadNCLRDefault       FN(void (*)(u32, u32, u32, u32, u32, u32), 0x0204b0b8)
#define HEAPID_TAIL(h)                 (((h) & 0x7fffu) | 0x8000u)
#define CFG_GEN5_SPRITES               (1u << 14)
#define TRAINER_SPRITE_BACK            1u
#define NONE                           0xffffu

#include "sprite_switch_data.h"   /* ARC_OW, N_OW, kOw, N_FRONT, kFront, N_BACK, kBack: {classic, Gen 5} pairs;
                                     ARC_ICONS, N_ICONS, kIcons: {archive, file, copy in ARC_OW} */

u32 Sprite_IsGen5(void) {
#ifdef SPRITE_FORCE
    return SPRITE_FORCE;
#else
    void *sc = g_SaveControlWork;
    if (!sc) return 0;
    return (*(const u16 *)SaveControl_GetBlockPtr(sc, 27) & CFG_GEN5_SPRITES) ? 1 : 0;
#endif
}

static u32 lookup(const u16 *t, u32 n, u32 v) {
    u32 i;
    for (i = 0; i < n; i++)
        if (t[2 * i] == v) return t[2 * i + 1];
    return v;
}

u32 Sprite_OwFile(u32 file) {
    return Sprite_IsGen5() ? lookup(kOw, N_OW, file) : file;
}

/* the field's sheet loads: bl GFL_G3DSysReadArcToolResource(MMDL data handle, res1) -> here */
void *Sprite_OwRead(void *handle, u32 file) {
    return GFL_G3DSysReadArcToolResource(handle, Sprite_OwFile(file));
}

/* func_02016510 (actor, arc, file, ...): the file number it reads, for any archive */
u32 Sprite_ArcFile(u32 arc, u32 file) {
    return arc == ARC_OW ? Sprite_OwFile(file) : file;
}

/* func_02016510 at 0x0201651c: `adds r4, r2, #0; adds r6, r3, #0` (r0 = the archive, r2 = the file) -> bl here */
__attribute__((naked)) void Sprite_BillboardShim(void) {
    __asm__ volatile("push {r0, r1, r2, r3, lr}\n\tadds r1, r2, #0\n\tbl Sprite_ArcFile\n\tadds r4, r0, #0\n"
                     "\tpop {r0, r1, r2, r3}\n\tadds r6, r3, #0\n\tpop {pc}\n");
}

/* the GetTrSprite*DatID functions: bl GetTrSpriteBaseDatID(class, flags) -> here */
u32 Sprite_TrBase(u32 trainerClass, u32 flags) {
    u32 s = GetTrSpriteBaseDatID(trainerClass, flags);
    if (Sprite_IsGen5())
        s = (flags & TRAINER_SPRITE_BACK) ? lookup(kBack, N_BACK, s) : lookup(kFront, N_FRONT, s);
    return s;
}

/* the copy in ARC_OW of an icon / card file with NEW, else NONE */
static u32 icon_copy(u32 arc, u32 file) {
    u32 i;
    if (!N_ICONS || !Sprite_IsGen5()) return NONE;
    for (i = 0; i < N_ICONS; i++)
        if (kIcons[3 * i] == arc && kIcons[3 * i + 1] == file) return kIcons[3 * i + 2];
    return NONE;
}

/* func_0204b81c (handle on a/0/3/0, file, compressed, vram, heap) */
u32 Sprite_IconChars(void *arc, u32 file, u32 compressed, u32 vram, u32 heap) {
    u32 f = icon_copy(ARC_ICONS, file), r;
    void *h;
    if (f == NONE) return ClactLoadChars(arc, file, compressed, vram, heap);
    h = GFL_ArcSysCreateFileHandle(ARC_OW, HEAPID_TAIL(heap));
    r = ClactLoadChars(h, f, compressed, vram, heap);
    GFL_ArcToolFree(h);
    return r;
}

/* func_0204bbb8 (handle on a/0/3/0, file, vram, offset, start, count, heap) */
u32 Sprite_IconPalEx(void *arc, u32 file, u32 vram, u32 offset, u32 start, u32 count, u32 heap) {
    u32 f = icon_copy(ARC_ICONS, file), r;
    void *h;
    if (f == NONE) return ClactLoadPalEx(arc, file, vram, offset, start, count, heap);
    h = GFL_ArcSysCreateFileHandle(ARC_OW, HEAPID_TAIL(heap));
    r = ClactLoadPalEx(h, f, vram, offset, start, count, heap);
    GFL_ArcToolFree(h);
    return r;
}

/* func_0204bba0 (handle on a/0/3/0, file, vram, offset, heap) is Black 2's func_0204bbb8(.., 0, 0, heap) (arm9
 * 0x0204bba0: start 0, count 0 = every palette): the same here */
u32 Sprite_IconPal(void *arc, u32 file, u32 vram, u32 offset, u32 heap) {
    return Sprite_IconPalEx(arc, file, vram, offset, 0, 0, heap & 0xffffu);
}

/* the trainer card picture: GFL_G2DIOReadBGNCGR (archive, file, compressed, &character, heap) */
void *Sprite_CardChars(u32 arc, u32 file, u32 compressed, void *character, u32 heap) {
    u32 f = icon_copy(arc, file);
    if (f == NONE) return GFL_G2DIOReadBGNCGR(arc, file, compressed, character, heap);
    return GFL_G2DIOReadBGNCGR(ARC_OW, f, compressed, character, heap);
}

/* and its palette: GFL_BGSysLoadNCLRDefault (archive, file, type, offset, size, heap) */
void Sprite_CardPal(u32 arc, u32 file, u32 type, u32 offset, u32 size, u32 heap) {
    u32 f = icon_copy(arc, file);
    if (f == NONE) GFL_BGSysLoadNCLRDefault(arc, file, type, offset, size, heap);
    else GFL_BGSysLoadNCLRDefault(ARC_OW, f, type, offset, size, heap);
}
