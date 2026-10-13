import sys; sys.path.insert(0, sys.path[0])
from pt import *
g = G('s01_house.dst', name='s02')
print('warp', g.warp(1), g.zone(), g.tile())
g.adv()
print('go clock', g.go(6, 3), g.tile())
g.face((0, -1)); g.press('A', 4, 30)
for i in range(40):
    g.texts(); g.run(30)
    if i % 4 == 0: g.S(True)
    if g.idle(): break
    if g.choice_menu(): print('choice'); break
    g.press('A', 4, 20)
print('state', g.zone(), g.tile(), hex(g.event()), g.field())
g.save('s02_clock.dst')
g.sheet(os.path.join(PT, 'scratch.png'), cols=6)
