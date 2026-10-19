"""The Pokémon Musical at Hoenn's Contest Hall counters (musical agent, 2026-10-18; notes/RESUME.md "Emerald gaps" ->
Contests, the user's idea): Contests can't run on Black 2, so the receptionists send you to Black 2's own Musical.
The scripts are src/field_scripts/common/musical.inc (the reception, Black 2's global 10450 flow without Nimbasa's
walk), the four Sapphire/Ruby lobbies + Emerald's Lilycove lobby, and 0156_musical_backstage.s (zone 78). This patch
is the code side: two places where Black 2's musical event assumes Nimbasa's Musical Theater (map type 9).

What the musical event does (ov012 func_ov012_02150cf8 = MusicalCmd_0163 kind 0, its state machine func_ov012_02150e6c):
  create: GFL_HeapCreateChild(HEAPID_USER, HEAPID_MUSICAL_EVENT 0x2c | tail, 0x42000), the show's program (a/1/1/2-5:
          its timeline, Props' sounds; shows 0-3 ~25 KB; a downloaded 5th show is read from the save, hence 264 KB)
          loaded into that heap (func_ov210_021eee0c), the three other performers picked
  13/14:  map change to zone 78 (the backstage, map type 9), its script 3 (the owner's welcome)
  3-8:    dress-up (heap 0x2d, 256 KB), backstage script 4, the stage (heap 0x2e, 672 KB, field closed), the photo
  19/20:  backstage script 5 (the audience's comments)
  2:      program freed (func_ov012_021511b4), then func_ov012_02151a90: map change to zone 77 = Nimbasa's Musical
          Theater lobby, at a fixed spot (data_ov012_0216ade4) -> in Hoenn zone 77 is Ever Grande's Pokemon League
  9/10:   global script 10454 there (fade in), then GFL_HeapDelete(0x2c)

Problems in Hoenn and the fixes:
  1. The heap. Map type 9 (zones 77/78) has a 0xAA000 field heap, type 16 (every Hoenn room) 0x136800
     (ov036 MAP_CONFIGS[t].heapSize, taken from HEAPID_USER while the field runs). In a Hoenn lobby USER keeps 110,696 B
     free (script_check heapsweep 2026-10-08), so the 264 KB heap can't be made there, and the return map change
     to a type-16 room can't make its field heap while the 264 KB still exist (1,382,504 B - 270,336 < 1,271,808).
     Fix: the heap is 0x10000 (64 KB: the program of shows 0-3 with room to spare; the reception offers only those
     four) -> ov012 0x02150d00 `movs r2, #66` -> `movs r2, #16` (size = r2 << 12); and it is deleted before the
     return map change (point 2), not after it (ov012 0x0215112e `bl GFL_HeapDelete` -> two nops).
  2. The return. func_ov012_02151a90 is rewritten in place (100 bytes, 60 used):
         GFL_HeapDelete(HEAPID_MUSICAL_EVENT)                       (everything in it was freed by 021511b4)
         next = GameData_GetNextZone(work->gameData)                (set by the reception: FieldSetNextZoneHere)
         ChainNext(event, EventMapChange_CreateGridDefault(gsys, GSYS_GetField(gsys), next->zoneId, &next->pos,
                                                           next->warpDir))
     so the show ends where the player stood at the counter, facing it (FieldSetNextZoneHere stores
     PlayerState_CalcDirection, a direction, which CreateGridDefault converts like the original's constant 1).
     GameData's next zone is Black 2's "dynamic warp": the Lilycove Dept. Store elevator sets it on arrival, dive
     sets it before surfacing, the Frontier's rest-and-quit with flag 2405: none reads a stale value from here.
  Both the online path and the connection-error path also end in func_ov012_02151a90 (states 24/26): unchanged
  otherwise (Hoenn never offers the online Musical).
Zones 77/78 keep Black 2's headers (map type 9); zone 78 (scripts 156, text 88, area 305) is Black 2's backstage.

Symbols (decomp config/b2_us): GFL_HeapDelete 0x0203a1d0, GSYS_GetField 0x02016af0, GameData_GetNextZone 0x02017290,
GameEvent_ChainNext 0x02016d68, ov035 EventMapChange_CreateGridDefault 0x0217e1d8 (gsys, field, zone, pos, dir);
ZoneSpawnInfo (include/field/zone.h): zoneId +4, warpDir +8, pos +16. All versions (code only)."""
import os, struct

OV012 = 0x021503C0
HEAPID_MUSICAL_EVENT = 0x2C

HEAP_SIZE_AT = 0x02150D00                     # func_ov012_02150cf8: movs r2, #66 (lsls r2, r2, #12 -> 0x42000)
HEAP_SIZE_OLD, HEAP_SIZE_NEW = bytes.fromhex('4222'), bytes.fromhex('1022')   # -> movs r2, #16 (0x10000)

LATE_DELETE_AT = 0x0215112E                   # state 10: bl GFL_HeapDelete (after `movs r0, #44`)
LATE_DELETE_OLD, NOPS = bytes.fromhex('e9f64ff8'), bytes.fromhex('c046c046')

RETURN_AT, RETURN_END = 0x02151A90, 0x02151AF4  # func_ov012_02151a90 (+ its 2-word literal pool)
RETURN_OLD = bytes.fromhex(
    'f8b588b00c1c01902068c5f629f805aa124b061c03cb151c03c21868104b106002aa03cb171c03c2186810606069012806d10120'
    '00902068311c4d223b1c05e0012000902068311c4d222b1c2cf07cfb011c0198c5f640f908b0f8bde4ad1602fcad1602')

GFL_HEAP_DELETE, GSYS_GET_FIELD, GET_NEXT_ZONE = 0x0203A1D0, 0x02016AF0, 0x02017290
CHAIN_NEXT, CREATE_GRID_DEFAULT = 0x02016D68, 0x0217E1D8


def _bl(src, dst):
    off = dst - (src + 4)
    assert -(1 << 22) <= off < (1 << 22) and not off & 1, hex(off)
    return struct.pack('<HH', 0xF000 | (off >> 12) & 0x7FF, 0xF800 | (off >> 1) & 0x7FF)


def return_code():
    """func_ov012_02151a90(GameEvent *event, MusicalEventWork *work): see the module doc, point 2."""
    out = bytearray()
    def h(*w):
        for x in w: out.extend(struct.pack('<H', x))
    def bl(dst):
        out.extend(_bl(RETURN_AT + len(out), dst))
    h(0xB5F0, 0xB081)                 # push {r4-r7, lr}; sub sp, #4
    h(0x1C05, 0x1C0C)                 # adds r5, r0, #0 (event); adds r4, r1, #0 (work)
    h(0x2000 | HEAPID_MUSICAL_EVENT)  # movs r0, #0x2c
    bl(GFL_HEAP_DELETE)               # the musical's heap goes before the Hoenn room's field heap is made
    h(0x6820); bl(GSYS_GET_FIELD)     # ldr r0, [r4] (gsys)
    h(0x1C06)                         # adds r6, r0, #0 (field)
    h(0x6860); bl(GET_NEXT_ZONE)      # ldr r0, [r4, #4] (gameData)
    h(0x1C07)                         # adds r7, r0, #0 (ZoneSpawnInfo *next)
    h(0x8938, 0x9000)                 # ldrh r0, [r7, #8] (warpDir: a direction here); str r0, [sp]
    h(0x6820, 0x1C31)                 # ldr r0, [r4] (gsys); adds r1, r6, #0 (field)
    h(0x88BA)                         # ldrh r2, [r7, #4] (zoneId)
    h(0x1C3B, 0x3310)                 # adds r3, r7, #0; adds r3, #16 (&next->pos)
    bl(CREATE_GRID_DEFAULT)
    h(0x1C01, 0x1C28)                 # adds r1, r0, #0; adds r0, r5, #0
    bl(CHAIN_NEXT)                    # GameEvent_ChainNext(event, map change)
    h(0xB001, 0xBDF0)                 # add sp, #4; pop {r4-r7, pc}
    size = RETURN_END - RETURN_AT
    assert len(out) <= size, len(out)
    while len(out) < size: h(0x46C0)  # mov r8, r8 (never reached)
    return bytes(out)


def _put(d, addr, old, new, what):
    o = addr - OV012
    cur = bytes(d[o:o + len(new)])
    if cur == new:
        return
    assert cur == old, f'musical: unexpected bytes at {addr:#x} ({what}): {cur.hex()}'
    d[o:o + len(new)] = new


def apply_code(code):
    p = os.path.join(code, 'arm9_ov012.bin')
    d = bytearray(open(p, 'rb').read())
    assert len(RETURN_OLD) == RETURN_END - RETURN_AT
    _put(d, HEAP_SIZE_AT, HEAP_SIZE_OLD, HEAP_SIZE_NEW, 'musical heap size')
    _put(d, LATE_DELETE_AT, LATE_DELETE_OLD, NOPS, 'late heap delete')
    _put(d, RETURN_AT, RETURN_OLD, return_code(), 'return map change')
    if os.path.islink(p): os.unlink(p)
    open(p + '.tmp', 'wb').write(d); os.replace(p + '.tmp', p)
    return ('musical: heap 0x2c 0x42000 -> 0x10000, deleted before the return; the show returns to GameData\'s next '
            'zone (the reception\'s FieldSetNextZoneHere) instead of zone 77')


if __name__ == '__main__':          # check against the decomp's build (no ROM): python3 musical.py
    import sys
    src = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'external', 'pokebw2', 'build', 'b2_us',
                       'build', 'arm9_ov012.bin')
    d = open(src, 'rb').read()
    for addr, old in ((HEAP_SIZE_AT, HEAP_SIZE_OLD), (LATE_DELETE_AT, LATE_DELETE_OLD), (RETURN_AT, RETURN_OLD)):
        assert d[addr - OV012:addr - OV012 + len(old)] == old, hex(addr)
    print('musical: decomp bytes as expected;', return_code().hex())
    sys.exit(0)
