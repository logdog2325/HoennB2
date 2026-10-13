"""Hoenn has no seasons: Black 2's season is always summer.

Season_GetRealTime (arm9 0x02034f6c) returns (month - 1) & 3 (0 spring, 1 summer, 2 autumn, 3 winter; read with
b2tools/armdis.py). Every seasonal thing (area textures and lights, winter snow, encounters, season banner) follows
the season it returns once it is synced into the save, so returning 1 keeps Hoenn in summer all year: the textures
our maps were built with (area 2 summer = texture set 3, notes/GEN5_TERRAIN.md) and Black 2's summer lighting.

The season the game itself keeps (GameData + 0x1c8, read by GameData_GetSeason at 0x020173ac) also returns 1 now
(exterior sweep, 2026-10-06). Why: EventMapChange_LoadSeasons (ov035, src/ov035/event_mapchange.c:386) compares that
kept season with Season_GetRealTime() on every warp into an exterior area, and when they differ the warp plays the
season card ("Summer") and only then stores the new season (event_mapchange.c:493-503). A save made while the kept
season was not summer (an older build, or a DS clock in another month) therefore showed "Summer" when the player left
a building (reproduced in DeSmuME by setting the byte to 0 at work/emu/base_littleroot.dst), and until then loaded
the area's spring/autumn/winter texture set, which lacks Hoenn's textures. With both functions answering summer the
two always agree: no card on warps, and every reader (textures, lights, encounters, music) sees summer. Black 2's own
card on "Continue" (EventFieldContinue, event_mapchange.c:334, transition type 3 = the season banner) still shows the
season once per load, as in Black 2.

The place-name banner (script_check, 2026-10-08): Black 2's banner is two parts, the place name and the season
("SUMMER", bottom right of the top screen), and it showed with every banner in Hoenn: walking into a map (fixes_v151's
proofs), out of a dive or a warp panel, Escape Rope, Dig (reproduced: a dive at the Seafloor Cavern entrance,
screenshots/script_check/). ov036's place-name module (decomp symbols; not decompiled) keeps two banner parts at
PlaceName +88 (the name) and +92 (the season: func_ov036_021b5500 hands it GameData_GetSeason, which
func_ov036_021b5660 stored at +33), made by func_ov036_021b6824 (types 0 and 1) and driven by loops over both parts:
func_ov036_021b55ac (slide in, state 1), _55cc (slide out, state 2), _5550 (reset, state 3), _5570 (update),
_5588 (all done?). The three state loops now stop after the name (cmp r4, #2 -> #1): the season part never leaves its
idle state (+28 = 0), so it is never drawn, its update never runs (func_ov036_021b68e8 checks +28) and _5588 counts it
as done (func_ov036_021b6940: +28 == 0)."""
import os

AT = 0x02034f76 - 0x02004000          # arm9.bin offset of "ldr r0, [sp, #4]" (the month)
OLD = bytes.fromhex('0198' '411e' '0320' '0840')    # ldr r0,[sp,#4]; subs r1,r0,#1; movs r0,#3; ands r0,r1
NEW = bytes.fromhex('0120' 'c046' 'c046' 'c046')    # movs r0,#1; nop; nop; nop
AT_GET = 0x020173ac - 0x02004000      # GameData_GetSeason
OLD_GET = bytes.fromhex('7221' '8900' '405c' '7047')   # movs r1,#114; lsls r1,r1,#2; ldrb r0,[r0,r1]; bx lr
NEW_GET = bytes.fromhex('0120' '7047' 'c046' 'c046')   # movs r0,#1; bx lr; nop; nop

OV036 = 0x0217F600                    # arm9_ov036.bin load address (extract/b2_us/arm9_overlays/overlays.yaml)
BANNER_LOOPS = (0x021b5562, 0x021b55c6, 0x021b55e6)   # "cmp r4, #2" of func_ov036_021b5550 / _55ac / _55cc

def banner_without_season(code):
    path = os.path.join(code, 'arm9_ov036.bin')
    data = bytearray(open(path, 'rb').read())
    for a in BANNER_LOOPS:
        at = a - OV036
        assert data[at:at + 2] in (b'\x02\x2c', b'\x01\x2c'), f'ov036 {a:#x}: unexpected {data[at:at + 2].hex()}'
        data[at:at + 2] = b'\x01\x2c'                              # cmp r4, #1
    if os.path.islink(path): os.unlink(path)
    open(path, 'wb').write(data)

def apply_code(code):
    banner_without_season(code)
    path = os.path.join(code, 'arm9.bin')
    data = bytearray(open(path, 'rb').read())
    for at, old, new in ((AT, OLD, NEW), (AT_GET, OLD_GET, NEW_GET)):
        assert data[at:at + 8] in (old, new), f'unexpected bytes {data[at:at + 8].hex()} at {at:#x}'
        data[at:at + 8] = new
    if os.path.islink(path): os.unlink(path)
    open(path, 'wb').write(data)
    return 'season always summer (real time and the kept season); place-name banner without the season part'
