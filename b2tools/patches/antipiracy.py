"""Black 2's anti-piracy reactions made harmless (battle_crash, 2026-10-13; Discord: crashes in battles, the May
battle in particular, on DS flashcarts and 3DS, never in DeSmuME / melonDS).

Black 2 runs a DS Protect check (overlay 337, pokebw2 include/dsprot/dsprot.h) at three places. Each place puts two
callbacks in a table (data_ov337_02182444, the slot of the "OK" one picked from the VBlank counter) and the check
calls the OK one when it finds nothing and the "tampered" one when it detects a copy (a flashcart, a loader without
an anti-piracy fix) or when the check's own code was changed:
  boot    GameSystem_Init (arm9)      OK func_020166a0 / func_020166d0; tampered func_02016678 (a permanent VBlank
                                      task, and one more per badge after every boot) / func_020166c0
  warps   EventMapChange (ov035)      OK EventMapChange_DSProtNop; tampered EventMapChange_DSProtTamper1/2: each
                                      allocates 4 KB of the game-event heap and never frees it (8 KB per door)
  battles EventBattleCall (ov012)     OK func_ov012_02169170 / func_ov012_02169198; tampered func_ov012_02169154 /
                                      func_ov012_02169180: after the battle a permanent VBlank task
In a few doors the event heap is full and the next allocation fails (the game stops: GFL's allocation-failure exit);
battles need the most event memory, so that is usually where it happens. Loaders hide this for the original game
with an "AP fix" chosen by game code AND header CRC (nds-bootstrap: loadApFix(romTid, headerCRC)); a hack's header
CRC differs (Sapphire/Ruby v16.9 82B2, Emerald v1.0.2 1746, Black 2 7680), so no fix is applied. Emulators pass
the check (tested in DeSmuME: every check calls its OK callback).

Fix: each tampered callback starts with a branch to the OK callback of its pair, so a detection does exactly what a
pass does (same arguments, same return value as the OK path, same random-number use). Overlay 337 is not touched: the
game checksums the DS Protect functions before calling them. All three versions."""
import os, struct

ARM9_BASE, OV012_BASE, OV035_BASE = 0x02004000, 0x021503c0, 0x0217c940

# (code file, base, tampered callback, its first halfword in Black 2, OK callback it now branches to)
EDITS = [
    ('arm9.bin', ARM9_BASE, 0x02016678, 0xb510, 0x020166a0, 'boot check 1'),
    ('arm9.bin', ARM9_BASE, 0x020166c0, 0x6802, 0x020166d0, 'boot check 2'),
    ('arm9_ov035.bin', OV035_BASE, 0x0217eccc, 0xb518, 0x0217ed1c, 'warp check 1 (4 KB leak)'),
    ('arm9_ov035.bin', OV035_BASE, 0x0217ecf4, 0xb518, 0x0217ed1c, 'warp check 2 (4 KB leak)'),
    ('arm9_ov012.bin', OV012_BASE, 0x02169154, 0xb510, 0x02169170, 'battle check 1'),
    ('arm9_ov012.bin', OV012_BASE, 0x02169180, 0xb510, 0x02169198, 'battle check 2'),
]


def thumb_b(src, dst):
    """Thumb unconditional branch (B, +-2 KB) at src to dst."""
    off = (dst - (src + 4)) >> 1
    assert -1024 <= off < 1024 and not (dst - src) & 1
    return struct.pack('<H', 0xe000 | (off & 0x7ff))


def apply_code(code):
    files = {}
    for name, base, at, old, ok, what in EDITS:
        if name not in files:
            p = os.path.join(code, name)
            files[name] = (p, bytearray(open(p, 'rb').read()))
        d = files[name][1]
        o = at - base
        cur = struct.unpack_from('<H', d, o)[0]
        new = thumb_b(at, ok)
        if bytes(d[o:o + 2]) == new: continue                      # already applied (a second run)
        assert cur == old, f'antipiracy: {what} at {at:#x} is {cur:#06x}, expected {old:#06x}'
        d[o:o + 2] = new
    for p, d in files.values():
        if os.path.islink(p): os.unlink(p)
        open(p + '.tmp', 'wb').write(d); os.replace(p + '.tmp', p)
    return f'antipiracy: {len(EDITS)} tampered callbacks -> their OK callbacks (boot, warps, battles)'
