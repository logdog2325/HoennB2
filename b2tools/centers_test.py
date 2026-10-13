"""Emulator checks of the centers agent: b2tools/walk.py's moves plus the ones the Center tests need.

    ../.venv/bin/python centers_test.py ROM STATE OUT.png MOVES...
MOVES as walk.py (D3 hold, A, B, W60, S, SAVE:path, P, Gx,z, Cx,z) and:
  tD / tU / tL / tR   tap the direction (4 frames: one menu step, or a turn)
  @<town>             test builds (CENTERS_TEST_BLACKOUT=1 b2tools/centers_rooms.py, HOENN_TEST_WARP): standing in
                      front of Oldale Center's map (Sapphire 11,1 -> zone 11,10, facing up), open the town menu,
                      pick <town> and walk in through its Center door (A works again after a door, not after a
                      script warp); ends standing on the 1F exit mat, position calibrated
"""
import sys, os, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, 'patches'))
from PIL import Image
from emu import Emu

def towns():
    import centers
    out = []
    for z, (town, tz) in sorted(centers.center_towns().items(), key=lambda kv: kv[1][0]):
        t = centers.door_tile(town, tz, z)
        if t: out.append((town, t))
    return out

def main(rom, state, out, moves):
    e = Emu(rom); e.load_state(state); e.run(2)
    DIR = {'U': 'UP', 'D': 'DOWN', 'L': 'LEFT', 'R': 'RIGHT'}
    shots = []
    for m in moves:
        if m[0] in DIR and m[1:].isdigit(): e.hold(DIR[m[0]], 16 * int(m[1:])); e.run(4)
        elif m[0] == 't' and m[1:] in DIR: e.hold(DIR[m[1:]], 4); e.run(12)
        elif m in ('A', 'B'): e.press(m, 6, 30)
        elif m[0] == 'W': e.run(int(m[1:]))
        elif m == 'S': shots.append(e.d.screenshot().crop((0, 0, 256, 192)))
        elif m.startswith('SAVE:'): e.save_state(m[5:])
        elif m == 'P': print('pos', e.player_tile())
        elif m[0] == 'C':
            tx, tz = map(int, m[1:].split(','))
            print('calibrated' if e.calibrate(tx, tz) else 'calibration failed', hex(e.pos_addr))
        elif m[0] == 'G':
            tx, tz = map(int, m[1:].split(','))
            print('goto', (tx, tz), 'ok' if e.goto(tx, tz) else f'blocked at {e.player_tile()}')
        elif m[0] == '@':
            names = [t for t, _ in towns()]
            i = names.index(m[1:]); door = dict(towns())[m[1:]]
            e.press('A', 6, 40)
            for _ in range(i): e.hold('DOWN', 4); e.run(12)
            e.press('A', 6, 300)
            e.calibrate(*door)
            e.hold('UP', 16); e.run(300)              # through the door
            e.hold('UP', 16); e.run(30)               # one step in: the live position copy
            ok = e.calibrate(7, 15)
            print(f'@{m[1:]}: in' if ok else f'@{m[1:]}: not in the Center?')
    if shots:
        cols = min(4, len(shots)); rows = (len(shots) + cols - 1) // cols
        sheet = Image.new('RGB', (256 * cols, 192 * rows))
        for i, im in enumerate(shots): sheet.paste(im, (256 * (i % cols), 192 * (i // cols)))
        sheet.save(out)
    print('shots', len(shots), '->', out if shots else '-')

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4:])
