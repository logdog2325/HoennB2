import sys; sys.path.insert(0, sys.path[0])
from pt import *
import battle, party as P
g = G('s11_after_may.dst', name='s12')
battle.install(g, run_wild=False)
r = g.warp(to_zone=396) if g.zone() == 389 else None
print('go home', g.go(175, 369), g.zone(), g.tile())
print('lab', g.warp(3), g.zone(), g.tile())
g.adv()
for a in g.actors(): print(' actor', a['uid'], a['x'], a['z'], a['scr'])
g.S()
g.save('s12_lab2.dst')
g.sheet(os.path.join(PT, 'scratch.png'), cols=5)
