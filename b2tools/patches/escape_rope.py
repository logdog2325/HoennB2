"""Escape Rope and Dig in Hoenn: remember the exit when you walk from Hoenn's outdoors into a cave or building
(Discord 2026-10-14: "if you use Escape Rope in the cave ... you don't exit the cave, you get up to a weird city").

Black 2 remembers the Escape Rope / Dig exit only for a warp from a zone on matrix 0 (its Unova overworld) into one on
another matrix (ov035 src/ov035/event_mapchange.c:1231, EventMapChangeWarp_CreateFromEntity:
GetIsZoneMatrix0(remember) && !GetIsZoneMatrix0(dest) -> GameData_SetEscapeRopeZone). Hoenn's overworld is matrix 416
and its standalone outdoor maps (Petalburg Woods, Mt. Pyre, Sootopolis, the islands...) are 417.. (world.json "matrix",
"standalone"; patches/fixed_weather.py standalone_matrices), so the exit was never stored: the rope used whatever an
older event left there (a blackout's town spawn, or Black 2's new-game value), a far-away town.

Fix: GetIsZoneMatrix0 (arm9 0x02018cfc; also read by the Dowsing MC) answers "a Hoenn outdoor matrix" instead:
    ldrh r0, [r0, #4]          ; the zone header's matrix (kept)
    subs r0, #255 ; subs r0, #(M - 255)   ; r0 = matrix - M  (M = 416)
    cmp r0, #(N + 1)           ; N standalone matrices: inside when matrix - M <= N (unsigned)
    sbcs r0, r0                ; C clear (inside) -> -1, C set (outside) -> 0
    negs r0, r0                ; -> 1 / 0
    pop {r3, pc}
in the 12 bytes of Black 2's own compare-and-return (0x02018d04-0x02018d0f), so nothing moves. Unova's matrix 0 (no
Hoenn zone uses it) now answers 0. All versions (Sapphire, Ruby and Emerald share matrix 416 and 17 standalone groups;
read from the version's world at build time)."""
import os, sys, json, struct
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import version  # noqa: E402

ARM9 = 0x02004000
AT = 0x02018d04
OLD = bytes.fromhex('002801d1012008bd002008bd')     # cmp r0,#0; bne; movs r0,#1; pop {r3,pc}; movs r0,#0; pop {r3,pc}


def _world():
    for d in (os.environ.get('HOENN_WORLD_DIR'), version.world_dir()):
        if d and os.path.exists(os.path.join(d, 'world.json')):
            return json.load(open(os.path.join(d, 'world.json')))
    raise SystemExit('escape_rope: no world.json (HOENN_WORLD_DIR / version.world_dir())')


def apply_code(code):
    w = _world()
    m, n = w['matrix'], len(w.get('standalone', []))
    assert 255 < m <= 510 and n + 1 <= 255, (m, n)
    new = struct.pack('<6H', 0x3800 | 255, 0x3800 | (m - 255), 0x2800 | (n + 1), 0x4180, 0x4240, 0xBD08)
    p = os.path.join(code, 'arm9.bin')
    d = bytearray(open(p, 'rb').read())
    o = AT - ARM9
    if bytes(d[o:o + 12]) != new:
        assert bytes(d[o:o + 12]) == OLD, f'escape_rope: unexpected bytes at {AT:#x}: {bytes(d[o:o + 12]).hex()}'
        d[o:o + 12] = new
        if os.path.islink(p): os.unlink(p)
        open(p + '.tmp', 'wb').write(d); os.replace(p + '.tmp', p)
    return f'escape_rope: GetIsZoneMatrix0 = Hoenn outdoor matrices {m}..{m + n} (Escape Rope / Dig exits)'
