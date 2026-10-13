import sys; sys.path.insert(0, sys.path[0])
from pt import *
import battle as BT, flags as F
g = G('t_party.dst', name='t20')
F.repel(g)
print('warp', g.warp(2), g.zone(), g.tile()); g.adv()
print(g.go(75, 256), g.tile())
hook = g.battle_hook; g.battle_hook = None
g.face((0, -1)); g.press('A', 4, 30)
for i in range(80):
    g.texts(); g.run(20)
    if g.in_battle():
        k, im = BT.classify(g)
        if k == 'cmd': break
    else: g.press('A', 4, 10)
g.save('t_double.dst')
g.S(True)
g.tap(128, 95); g.S(True)
g.tap(64, 57); g.S(True)          # Earthquake (no target)
g.wait_stable(); g.S(True)
g.tap(128, 95); g.S(True)
g.tap(64, 57); g.S(True)          # Meteor Mash: target screen?
g.sheet(os.path.join(PT, 'scratch.png'), cols=6)
