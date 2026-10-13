/* Emerald's Battle Pyramid (frontier_pyramid, 2026-10-12): the small fixed-address parts of the Pyramid's code. The
 * engine itself (frontier_pyramid.c) is a position-independent file loaded into the game-event heap (heap 4) while
 * the player is in the Pyramid; ITCM has no room for it (256 B were left after rods) and these parts call it.
 *
 * Built twice by b2tools/patches/frontier_pyramid.py, into code nothing in Hoenn runs:
 *   -DPART_OV012 (ov012 0x02164838-0x021649ec: the handlers of script commands 530 and 531, Cmd_0212 / Cmd_0213,
 *                which no Black 2 or Hoenn script uses, with their callbacks; ov012, the field system, stays loaded
 *                during battles): the hooks that run while the field overlay is not loaded (the battle's trainer lines)
 *                or may (the arm9 battle setup calls): each calls the previous target of its call site
 *                (frontier_pike's ITCM hooks, NEXT_*) and then the engine when it is loaded;
 *   -DPART_OV036 (ov036 0x021c898c-0x021c8c34, Join Avenue's map-building code: zone 490, never Hoenn's): the loader
 *                and the field's hooks (the RD chunk call, the per-step check, the wild battle setup, the Start menu's
 *                Save, script command 530).
 * The engine's address (PY_ENG) is the only ITCM: 4 bytes (ITCM is reloaded at every reset, so it starts at 0).
 * Engine header (frontier_pyramid.py): 'PYRM', code size, allocation size, entry count, entry offsets (Thumb). */
typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef int s32;

#define FN(type, addr) ((type)((addr) | 1))
#include "frontier_pyramid_stub.h"            /* generated: PY_ENG_ADDR, NEXT_*, PY_* */

#define PY_ENG (*(u8 **)PY_ENG_ADDR)
typedef struct { u32 magic, size, total, n, ent[12]; } Hdr;
#define ENTRY(eng, k) ((void *)((eng) + ((Hdr *)(eng))->ent[k] + 1))
enum { E_CMD, E_RD, E_STEP, E_ENC, E_SAVEMENU, E_PARTY, E_TRAINER, E_MSGEX, E_MSGLD };

#ifdef PART_OV012
void PY_I_LoadParty(void *setup, void *gd, u32 heap) {
    u8 *e = PY_ENG;
    FN(void (*)(void *, void *, u32), NEXT_PARTY)(setup, gd, heap);
    if (e) ((void (*)(u8 *, void *, void *))ENTRY(e, E_PARTY))(e, setup, gd);
}
void PY_I_LoadTrainer(void *setup, void *gd, u32 client, void **pparty, u32 id, u32 heap) {
    u8 *e = PY_ENG;
    FN(void (*)(void *, void *, u32, void **, u32, u32), NEXT_TRAINER)(setup, gd, client, pparty, id, heap);
    if (e && (id == PY_TR || id == PY_TR_BRAIN))
        ((void (*)(u8 *, void *, void *, u32, void **, u32, u32))ENTRY(e, E_TRAINER))(e, setup, gd, client, pparty, id, heap);
}
u32 PY_I_MsgExists(u32 id, u32 type, u32 heap) {
    u8 *e = PY_ENG;
    if (e && (id == PY_TR || id == PY_TR_BRAIN)) {
        s32 r = ((s32 (*)(u8 *, u32, u32))ENTRY(e, E_MSGEX))(e, id, type);
        if (r >= 0) return (u32)r;
    }
    return FN(u32 (*)(u32, u32, u32), NEXT_MSGEX)(id, type, heap);
}
void PY_I_MsgLoad(u32 id, u32 type, void *strbuf, u32 heap) {
    u8 *e = PY_ENG;
    if (e && (id == PY_TR || id == PY_TR_BRAIN) && ((u32 (*)(u8 *, u32, u32, void *, u32))ENTRY(e, E_MSGLD))(e, id, type, strbuf, heap))
        return;
    FN(void (*)(u32, u32, void *, u32), NEXT_MSGLD)(id, type, strbuf, heap);
}
#endif

#ifdef PART_OV036
#define GFL_HeapAllocate           FN(void *(*)(u32, u32, u32, const char *, u32), 0x0203a1fc)
#define GFL_HeapFree               FN(void (*)(void *), 0x0203a24c)
#define GFL_HeapGetFreeSize        FN(u32 (*)(u32), 0x0203a2a8)
#define GFL_ArcSysReadRange        FN(void (*)(void *, u32, u32, u32, u32), 0x0204a940)
#define cp15_flushDC               ((void (*)(const void *, u32))0x0207b0ac)      /* ARM */
#define cp15_invalidateIC          ((void (*)(const void *, u32))0x0207b0e8)      /* ARM */
#define memset_(p, v, n)           (((void (*)(void *, u32, u32))0x020787a8)((p), (v), (n)))
#define ScriptReadAny              FN(u32 (*)(void *, void *), 0x02154910)
#define ScriptReadVar              FN(u16 *(*)(void *, void *), 0x021548e8)
#define FieldChunk_GetDatID        FN(void (*)(void *, u32 *), 0x021635b0)
#define EventSave_Create           FN(void *(*)(void *, void *, u32, void *, u32, u32), 0x0215c4f8)
#define Field_GetPlayerStateZoneID FN(u32 (*)(void *), 0x021804d8)
#define HEAP 4                     /* HEAPID_GAMEEVENT: kept while the field closes for a battle or a menu */

static u8 *load(void) {
    Hdr h; u8 *e = PY_ENG;
    if (e) return e;
    GFL_ArcSysReadRange(&h, 8, PY_ENGINE_FILE, 0, sizeof h);
    if (h.magic != 0x4d525950 || GFL_HeapGetFreeSize(HEAP) < h.total + 0x1000) return 0;
    e = GFL_HeapAllocate(HEAP | 0x8000, h.total, 0, "pyrm", 0);
    GFL_ArcSysReadRange(e, 8, PY_ENGINE_FILE, 0, h.size);
    memset_(e + ((h.size + 3) & ~3), 0, h.total - ((h.size + 3) & ~3));
    cp15_flushDC(e, h.size);
    cp15_invalidateIC(e, h.size);
    PY_ENG = e;
    return e;
}

/* ov036 0x0218ac40 (the RD chunk loader's call of this function's old body, Join Avenue's builder): the Pyramid floor's
 * chunk gets its squares; any other RD chunk (none in Hoenn) keeps its count */
u32 PY_O_RDHook(void *work, u8 *terrain, void *props, void *chunk, u32 count, u32 index, u32 heap) {
    u32 id = 0; u8 *e;
    FieldChunk_GetDatID(chunk, &id);
    if (id != PY_FLOOR_CHUNK || !(e = load())) return count;
    return ((u32 (*)(u8 *, u8 *, void *, void *, u32))ENTRY(e, E_RD))(e, terrain, props, chunk, count);
}
/* the field's per-step checks (ov036 0x021815e6 / 0x02181afe, after frontier_pike's): the Pyramid floor's exit,
 * trainers' eyes and wild Pokemon */
void *PY_O_Step(u8 *ctx, void *a1, void *field) {
    u8 *e;
    if (*(u16 *)(ctx + 16) == PY_ZONE_FLOOR && (e = load())) {
        u32 r = ((u32 (*)(u8 *, u8 *, void *))ENTRY(e, E_STEP))(e, ctx, field);
        if (r != 1) return (void *)r;
    }
    return FN(void *(*)(void *, void *, void *), NEXT_STEP)(ctx, a1, field);
}
/* ov036 0x021a196e (EventWildBattleCall_CreateStatic's FieldEncount_SetupNormal, after frontier_pike's) */
void PY_O_EncSetup(void *field, void *encman, void *setup, u32 heap, void *param) {
    u8 *e = PY_ENG;
    FN(void (*)(void *, void *, void *, u32, void *), NEXT_ENC)(field, encman, setup, heap, param);
    if (e) ((void (*)(u8 *, void *))ENTRY(e, E_ENC))(e, setup);
}
/* ov012 0x0215c0fc (the Start menu's Save: EventSave_Create): on a Pyramid floor or its top, the Rest / Retire script */
void *PY_O_SaveMenu(void *gsys, void *field, u32 heap, void *msgbg, u32 a4, u32 a5) {
    u32 zone = Field_GetPlayerStateZoneID(field); u8 *e;
    if ((zone == PY_ZONE_FLOOR || zone == PY_ZONE_TOP) && (e = load())) {
        void *ev = (void *)((u32 (*)(u8 *, void *, u32, u32))ENTRY(e, E_SAVEMENU))(e, gsys, zone, heap);
        if (ev) return ev;
    }
    return EventSave_Create(gsys, field, heap, msgbg, a4, a5);
}
/* script command 530 (Black 2's Cmd_0212, unused): EmPyr var, op, a; op PY_UNLOAD frees the engine */
u32 PY_O_Cmd(void *vm, void *env) {
    u8 *e = load(); u32 r;
    if (!e) {
        *ScriptReadVar(vm, env) = 0xFFFF; ScriptReadAny(vm, env); ScriptReadAny(vm, env);
        return 0;
    }
    r = ((u32 (*)(u8 *, void *, void *))ENTRY(e, E_CMD))(e, vm, env);
    if (r & 0x100) { PY_ENG = 0; GFL_HeapFree(e); }
    return r & 1;
}
#endif
