"""Shops agent test walker: b2tools/walk.py's moves plus 'S2' (snapshot BOTH screens, for the shop list on the
touch screen) and 'DN'/'UP' (one menu step with a short press). One emulator, silent (b2tools/emu.py), closed at the end.

    ../.venv/bin/python shops_walk.py ROM STATE OUT.png MOVES...
"""
import sys
from PIL import Image
from emu import Emu

rom, state, out, moves = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4:]
e = Emu(rom); e.load_state(state); e.run(2)


def calibrate(tx, tz):
    """Like Emu.calibrate, but skips 0x02143c64: in rooms that copy is the CAMERA target, clamped to the zone's
    camera box (a/1/0/9), so it stops changing near the room's edges although the player walks on (tested in
    Lilycove 1F: the player reaches the east wall while that copy stays at x 15). The player's own copy is higher."""
    import numpy as np
    ram = np.frombuffer(bytes(e.d.memory.unsigned[0x02000000:0x02400000]), dtype='<i4')
    want_x, want_z = (tx * 16 + 8) << 12, (tz * 16 + 8) << 12
    hits = [0x02000000 + 4 * int(i) for i in np.where((ram[:-2] == want_x) & (ram[2:] == want_z))[0]]
    hits = [h for h in hits if h != 0x02143c64] or hits
    if not hits: return False
    e.pos_addr = hits[0]
    return True
DIR = {'U': 'UP', 'D': 'DOWN', 'L': 'LEFT', 'R': 'RIGHT'}
shots = []
for m in moves:
    if m in ('DN', 'UP'): e.press('DOWN' if m == 'DN' else 'UP', 4, 12)
    elif m[0] in DIR and m[1:].isdigit():
        e.hold(DIR[m[0]], 16 * int(m[1:])); e.run(4)
    elif m == 'A': e.press('A', 6, 30)
    elif m == 'B': e.press('B', 6, 30)
    elif m[0] == 'W': e.run(int(m[1:]))
    elif m == 'S': shots.append(e.d.screenshot().crop((0, 0, 256, 192)))
    elif m == 'S2': shots.append(e.d.screenshot().crop((0, 0, 256, 384)))
    elif m.startswith('SAVE:'): e.save_state(m[5:])
    elif m == 'P': print('pos', e.player_tile())
    elif m[0] == 'K':                      # calibrate near (x, z): try the 5x5 tiles around it, nearest first
        tx, tz = map(int, m[1:].split(','))
        cands = sorted(((dx, dz) for dx in range(-2, 3) for dz in range(-2, 3)), key=lambda d: abs(d[0]) + abs(d[1]))
        hit = next(((tx + dx, tz + dz) for dx, dz in cands if calibrate(tx + dx, tz + dz)), None)
        print('calibrated at', hit, hex(e.pos_addr))
    elif m[0] == 'C':
        tx, tz = map(int, m[1:].split(','))
        print('calibrated' if calibrate(tx, tz) else 'calibration failed', hex(e.pos_addr))
    elif m[0] == 'T':
        tx, tz = map(int, m[1:].split(','))
        print('travel', (tx, tz), 'ok' if e.travel(tx, tz) else f'stopped at {e.player_tile()}')
    elif m[0] == 'G':
        tx, tz = map(int, m[1:].split(','))
        print('goto', (tx, tz), 'ok' if e.goto(tx, tz) else f'blocked at {e.player_tile()}')
if shots:
    H = max(s.height for s in shots)
    cols = min(4, len(shots)); rows = (len(shots) + cols - 1) // cols
    sheet = Image.new('RGB', (256 * cols, H * rows))
    for i, im in enumerate(shots): sheet.paste(im, (256 * (i % cols), H * (i // cols)))
    sheet.save(out)
print('shots', len(shots), '->', out if shots else '-')
e.close()
