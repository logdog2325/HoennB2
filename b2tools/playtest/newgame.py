"""newgame.py ROM OUTSTATE: cold boot (no battery save), New Game as a boy named BRENDAN, the truck, the house scenes
(clock, TV), out into Littleroot. Saves OUTSTATE (relative to states/)."""
import sys; sys.path.insert(0, sys.path[0])
import os
sys.path.insert(0, os.path.expanduser('~/Documents/GitHub/HoennB2/b2tools'))
from emu import fresh_battery
rom_path = os.path.abspath(sys.argv[1])
fresh_battery(rom_path)
from pt import *
g = G(None, rom_path=rom_path, name='newgame')
g.run(1300)
for _ in range(9): g.press('A', 4, 100)          # title -> menu -> New Game -> Birch's first lines
for _ in range(14): g.press('A', 4, 80)          # Birch's speech up to "Are you a boy?"
g.run(60)
for _ in range(4): g.press('A', 4, 100)          # boy, YES, "What's your name?"
g.run(60)
for _ in range(8): g.touch(148, 172, 4, 20)      # DELETE the default name
for xy in ((46, 51), (144, 75), (94, 51), (78, 75), (78, 51), (29, 51), (78, 75)):   # B R E N D A N
    g.touch(*xy, 4, 30)
g.touch(200, 172, 4, 100)                         # OK
for _ in range(16): g.press('A', 4, 80)          # "So it's BRENDAN?" YES ... into the truck
for _ in range(60):
    g.run(30)
    if g.idle() and g.zone() == 394: break
    g.press('A', 4, 10)
print('truck', g.zone(), g.tile(), flush=True)
g.walk_dir((1, 0), 1); g.adv()
print('house', g.zone(), g.tile(), flush=True)
g.warp(1); g.adv()                               # upstairs
g.go(6, 3); g.face((0, -1)); g.press('A', 4, 30); g.adv()   # the wall clock; Mom comes up
g.warp(0); g.adv()                               # downstairs: the TV report
g.warp(0); g.adv()                               # out into Littleroot
print('outside', g.zone(), g.tile(), flush=True)
g.S(True); g.sheet(os.path.join(PT, 'scratch_newgame.png'))
g.save(sys.argv[2])
