"""Look at any room (or zone) in the emulator with ONE build (sweep_rooms agent, 2026-10-07).

    ../.venv/bin/python room_look.py ROM STATE OUT.png ZONE,X,Z [MOVES...]

ROM: a build with HOENN_TEST_WARP=563,6,7 (Littleroot's town sign warps there; notes/TESTING.md "Test warp"; another
value: TEST_WARP=zone,x,z in the environment). The tool copies the ROM to an APFS clone next to OUT (room_look.nds,
reused), writes ZONE,X,Z over the sign script's MapChangeCore constants in the clone, loads STATE (a Littleroot state
of this ROM's file layout, e.g. a cold-boot state from work/agents/world_fixes/tools/mkstate.py), walks to the sign
(183,366), reads it and runs MOVES: U3/D1/L2/R1 steps, A, B, W60 (frames), S (snapshot), P (print the tile),
Cx,z (find the position in RAM on a known tile, e.g. the arrival tile, before P or steps that need it).
One contact sheet of the snapshots -> OUT. (People can't be talked to after this warp: notes/TESTING.md.)
"""
import sys, os, struct, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)


def main():
    rom, state, out, target, moves = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5:]
    tz, tx, tzz = map(int, (os.environ.get('TEST_WARP') or '563,6,7').split(','))
    zone, x, z = map(int, target.split(','))
    clone = os.path.join(os.path.dirname(os.path.abspath(out)), 'room_look.nds')
    if os.path.exists(clone):                                    # the previous clone to the Trash (never deleted)
        os.rename(clone, os.path.join(os.path.expanduser('~/.Trash'), f'room_look_{os.getpid()}.nds'))
    subprocess.run(['cp', '-c', rom, clone], check=True)
    data = open(clone, 'rb').read()
    pat = struct.pack('<5H', tz, tx, 0, tzz, 1)                  # MapChangeCore zone, x, 0, z, 1 (0778 Script_1)
    i = data.find(pat)
    assert i >= 0 and data.find(pat, i + 1) < 0, f'the test warp {tz},{tx},{tzz} is not in {rom} exactly once'
    with open(clone, 'r+b') as f:
        f.seek(i); f.write(struct.pack('<4H', zone, x, 0, z))
    from PIL import Image
    from emu import Emu
    e = Emu(clone); e.load_state(state); e.run(2)
    e.calibrate(173, 361) or e.calibrate(*e.player_tile())
    for px, pz in ((173, 362), (184, 362), (184, 366), (183, 366)):   # round the houses, waiting for wanderers
        for _ in range(12):
            if e.goto(px, pz): break
            e.run(60)
    e.step('UP'); e.press('A', 6, 30); e.run(300)
    D = {'U': 'UP', 'D': 'DOWN', 'L': 'LEFT', 'R': 'RIGHT'}
    shots = []
    for m in moves:
        if m[0] in D and m[1:].isdigit():
            for _ in range(int(m[1:])): e.step(D[m[0]])
        elif m in ('A', 'B'): e.press(m, 6, 30)
        elif m[0] == 'W': e.run(int(m[1:]))
        elif m == 'S': shots.append(e.d.screenshot().crop((0, 0, 256, 192)))
        elif m == 'P': print('pos', e.player_tile())
        elif m[0] == 'C': print('calibrated' if e.calibrate(*map(int, m[1:].split(','))) else 'calibration failed')
    if shots:
        cols = min(4, len(shots)); rows = (len(shots) + cols - 1) // cols
        sheet = Image.new('RGB', (256 * cols, 192 * rows))
        for k, im in enumerate(shots): sheet.paste(im, (256 * (k % cols), 192 * (k // cols)))
        sheet.save(out)
    print('shots', len(shots), '->', out)
    e.close()


if __name__ == '__main__':
    main()
