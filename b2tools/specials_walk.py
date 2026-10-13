"""walk.py with one more command, for the specials agent's room tests (entering rooms through their doors).

    ../.venv/bin/python specials_walk.py ROM STATE OUT.png MOVES...

All of walk.py's moves (D3 L2 U1 R1, A, B, W60, S, P, G x,z, T x,z, C x,z, SAVE:path) plus:
  NODARK              replace the savestate's stale Flash-darkness table in RAM by the zone_effects one (see nodark)
  SS                  snapshot of both screens (top | bottom)
  KU / KD / KL / KR   find the player's position in RAM by walking one tile that way: every position-like vector
                      (fx32 x, y, z at tile centres) is read before and after the step, and the one that moved by
                      exactly that tile becomes the position (C x,z alone can pick a stale copy after a zone change).
"""
import sys
import numpy as np
from PIL import Image
from emu import Emu

def candidates(e):
    ram = np.frombuffer(bytes(e.d.memory.unsigned[0x02000000:0x02400000]), dtype='<i4')
    xs, zs = ram[:-2], ram[2:]
    ok = ((xs & 0xFFF) == 0) & ((zs & 0xFFF) == 0)
    xv, zv = (xs >> 12) - 8, (zs >> 12) - 8
    ok &= (xv % 16 == 0) & (zv % 16 == 0) & (xv >= 0) & (zv >= 0) & (xv < 1024 * 16) & (zv < 1024 * 16)
    return {0x02000000 + 4 * int(i): (int(xv[i]) // 16, int(zv[i]) // 16) for i in np.where(ok)[0]}

def nodark(e):
    """Test-only stand-in for a cold boot (until the base savestates are remade with the zone_effects patch): Black 2
    reads the Flash-darkness table a/1/4/9 once at boot, so a savestate keeps the unpatched table in RAM (found at
    0x02246ad4 in base_littleroot.dst). Overwrite that copy with the table b2tools/patches/zone_effects.py writes."""
    import os, b2files
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'patches'))
    import zone_effects
    files = os.path.join(os.path.dirname(__file__), '..', 'external', 'pokebw2', 'build', 'b2_us', 'files')
    t = b2files.narc_entries(b2files.arc_path(files, 149))[0]
    new = zone_effects._pairs(t, '<HH', zone_effects.our_zones()[0], [], 'dark')
    ram = bytes(e.d.memory.unsigned[0x02000000:0x02400000]); i = ram.find(t)
    if i < 0: return None
    for k, b in enumerate(new): e.d.memory.unsigned[0x02000000 + i + k] = b
    return hex(0x02000000 + i)

def move_calibrate(e, d):
    dx, dz = Emu.DELTA[d]
    for _ in range(3):                         # a short tap = one step (or only a turn: tap again)
        before = candidates(e)
        e.hold(d, 6); e.run(30)
        after = candidates(e)
        moved = [a for a, t in before.items() if a in after and after[a] == (t[0] + dx, t[1] + dz)]
        if moved:
            e.pos_addr = moved[0]
            return after[moved[0]]
    return None

if __name__ == '__main__':
    rom, state, out, moves = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4:]
    e = Emu(rom); e.load_state(state); e.run(2)
    DIR = {'U': 'UP', 'D': 'DOWN', 'L': 'LEFT', 'R': 'RIGHT'}
    shots = []
    for m in moves:
        if m[0] in DIR and m[1:].isdigit():
            e.hold(DIR[m[0]], 16 * int(m[1:])); e.run(4)
        elif m == 'NODARK': print('darkness table replaced in RAM at', nodark(e))
        elif m[0] == 'K' and m[1:] in DIR:
            print('move-calibrated at', move_calibrate(e, DIR[m[1:]]))
        elif m == 'A': e.press('A', 6, 30)
        elif m == 'B': e.press('B', 6, 30)
        elif m[0] == 'W': e.run(int(m[1:]))
        elif m == 'S': shots.append(e.d.screenshot().crop((0, 0, 256, 192)))
        elif m == 'SS':                          # both screens, side by side
            full = e.d.screenshot(); im = Image.new('RGB', (512, 192))
            im.paste(full.crop((0, 0, 256, 192)), (0, 0)); im.paste(full.crop((0, 192, 256, 384)), (256, 0))
            shots.append(im)
        elif m.startswith('SAVE:'): e.save_state(m[5:])
        elif m == 'P': print('pos', e.player_tile())
        elif m[0] in 'CTG':
            tx, tz = map(int, m[1:].split(','))
            if m[0] == 'C': print('calibrated' if e.calibrate(tx, tz) else 'calibration failed', hex(e.pos_addr))
            elif m[0] == 'T': print('travel', (tx, tz), 'ok' if e.travel(tx, tz) else f'stopped at {e.player_tile()}')
            else: print('goto', (tx, tz), 'ok' if e.goto(tx, tz) else f'blocked at {e.player_tile()}')
    if shots:
        cw = max(im.width for im in shots)
        cols = min(4, len(shots)) if cw == 256 else 2
        rows = (len(shots) + cols - 1) // cols
        sheet = Image.new('RGB', (cw * cols, 192 * rows))
        for i, im in enumerate(shots): sheet.paste(im, (cw * (i % cols), 192 * (i // cols)))
        sheet.save(out)
    print('shots', len(shots), '->', out if shots else '-')
