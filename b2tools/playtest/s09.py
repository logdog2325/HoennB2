import sys; sys.path.insert(0, sys.path[0])
from pt import *
import battle
g = G('s08b.dst', name='s09')
battle.install(g)
g.adv()
print('now', g.zone(), g.tile())
g.press('X', 4, 40); g.S(True)
g.save('s09_menu.dst')
g.sheet(os.path.join(PT, 'scratch.png'), cols=5)
