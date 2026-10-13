"""Play the new game (Hoenn opening, boy) on a ROM and write the base savestates (work/emu/*.dst) with one check image.
Savestates only work on ROMs with the same file layout, so run this again whenever build_rom.py's RESERVE changes.
Run it alone (it emulates several minutes; heavy when other jobs run): ../.venv/bin/python make_states.py ../work/rom/hoenn.nds

States (what each one is, where the player stands):
  base_truck.dst        inside the truck after the ride, (10,10) in zone 394
  base_house.dst        Brendan's house 1F after moving in, (9,7) in zone 390
  base_littleroot.dst   Littleroot after the TV report, in front of the player's house (173,361); next: May's house
  base_after_rival.dst  Littleroot after meeting May, at the north exit (179,353), the twin has asked for help
The moves are the ones verified scene by scene on 2026-10-06 (notes/OPENING.md); messages are paged with A and
timed waits, so a change in a scene's length needs the counts below adjusted (check make_states_check.png).
2026-10-07 (story_infra): every message now waits for A before its window closes (LastKeyWait), so the upstairs,
TV, May's-mom, May and twin scenes take one more A each; counts re-verified on a cold boot. Where a scene ends with
the player facing someone (TV: Mom, May's house 1F: her mom, north exit: the twin) the count is exact: one more A
would start talking to them.
"""
import sys
from PIL import Image
from emu import Emu, fresh_battery

rom = sys.argv[1]
OUT = '../work/emu/'
fresh_battery(rom)                              # a cold boot with no save: New Game
e = Emu(rom)
checks = []
D = {'U': 'UP', 'D': 'DOWN', 'L': 'LEFT', 'R': 'RIGHT'}

def run(moves):
    """walk.py's move language: D3 hold down 3 tiles, A/B press, W60 wait, S snapshot, C x,z calibrate, G x,z go."""
    for m in moves.split():
        if m[0] in D and m[1:].isdigit(): e.hold(D[m[0]], 16 * int(m[1:])); e.run(4)
        elif m == 'A': e.press('A', 6, 30)
        elif m == 'B': e.press('B', 6, 30)
        elif m[0] == 'W': e.run(int(m[1:]))
        elif m == 'S': checks.append(e.d.screenshot().crop((0, 0, 256, 192)))
        elif m[0] == 'C': assert e.calibrate(*map(int, m[1:].split(','))), f'calibration failed at {m}'
        elif m[0] == 'G': assert e.goto(*map(int, m[1:].split(','))), f'blocked going to {m}'

def times(n, moves): return ' '.join([moves] * n)

e.run(1200)
for _ in range(40): e.press('A', 6, 50)          # title, Birch's intro
for _ in range(90): e.press('A', 6, 40)          # boy, name AAAAAAA, Birch's 4 questions (YES/YES/HOENN/CLASSIC), into the truck
                                                # (2026-10-11, 4 questions: 76 do not reach the truck, 80 do: 90 for margin)
run('W900 S')
e.save_state(OUT + 'base_truck.dst')
run('C10,10 R1 W300 ' + times(26, 'A W50') + ' W100 S')                        # step out, arrival, moving in
e.save_state(OUT + 'base_house.dst')
run('C9,7 U4 U1 W120 L2 U1 A W40 A W40 W200 ' + times(11, 'A W40') + ' W150')  # upstairs, the clock, Mom
run('C6,3 A W40 A W40 A W40 W200 G8,3 U1 W150 ' + times(19, 'A W45') + ' W100 S')  # downstairs: TV report
run('R4 D3 D1 W200 S')                                                          # out to Littleroot
e.save_state(OUT + 'base_littleroot.dst')
run('C173,361 G182,361 U1 W200 ' + times(9, 'A W45') + ' ' + times(3, 'A W60'))  # May's house: her mom
run('U5 U1 W200 R5 R1 W20 ' + times(4, 'A W60'))                                # upstairs, talk to May
run(times(20, 'A W50') + ' W180 S')                                              # May's speech; she leaves
run('L5 U1 W200 D5 D1 W200 C182,361 G179,355 U1 U1 W40 A W50 A W50 A W50 A W50 W60 S')   # out, the twin's request
e.save_state(OUT + 'base_after_rival.dst')
sheet = Image.new('RGB', (256 * len(checks), 192))
for i, im in enumerate(checks): sheet.paste(im, (256 * i, 0))
sheet.save(OUT + 'make_states_check.png')
print('states written; check', OUT + 'make_states_check.png')
