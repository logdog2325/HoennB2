"""Load a savestate on a ROM, walk a route, save ONE contact-sheet image.  walk.py ROM STATE OUT.png MOVES...
MOVES: D3 = hold DOWN for 3 tiles, L2, R1, U4, A (press A), W60 (wait 60 frames), S (snapshot top screen),
SAVE:path, P (print the player's tile from RAM), G779,745 (walk to global tile, straight), T784,690 (walk there by the shortest route), C779,745 (find the position in RAM while standing on that tile). Snapshots are kept in memory and written as a single sheet (no per-frame files)."""
import sys
from PIL import Image
from emu import Emu
rom, state, out, moves = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4:]
e = Emu(rom); e.load_state(state); e.run(2)
DIR = {'U': 'UP', 'D': 'DOWN', 'L': 'LEFT', 'R': 'RIGHT'}
shots = []
for m in moves:
    if m[0] in DIR and m[1:].isdigit():
        e.hold(DIR[m[0]], 16 * int(m[1:])); e.run(4)
    elif m == 'A': e.press('A', 6, 30)
    elif m == 'B': e.press('B', 6, 30)
    elif m[0] == 'W': e.run(int(m[1:]))
    elif m == 'S': shots.append(e.d.screenshot().crop((0, 0, 256, 192)))
    elif m.startswith('SAVE:'): e.save_state(m[5:])
    elif m == 'P': print('pos', e.player_tile())
    elif m[0] == 'C':
        tx, tz = map(int, m[1:].split(','))
        print('calibrated' if e.calibrate(tx, tz) else 'calibration failed', hex(e.pos_addr))
    elif m[0] == 'T':
        tx, tz = map(int, m[1:].split(','))
        print('travel', (tx, tz), 'ok' if e.travel(tx, tz) else f'stopped at {e.player_tile()}')
    elif m[0] == 'G':
        tx, tz = map(int, m[1:].split(','))
        print('goto', (tx, tz), 'ok' if e.goto(tx, tz) else f'blocked at {e.player_tile()}')
if shots:
    cols = min(4, len(shots)); rows = (len(shots) + cols - 1) // cols
    sheet = Image.new('RGB', (256 * cols, 192 * rows))
    for i, im in enumerate(shots): sheet.paste(im, (256 * (i % cols), 192 * (i // cols)))
    sheet.save(out)
print('shots', len(shots), '->', out if shots else '-')
