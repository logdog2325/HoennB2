import sys; sys.path.insert(0, sys.path[0])
from pt import *
import battle, party as P
g = G('s19_woods.dst', name='s20')
battle.install(g, run_wild=True, wanted={280, 285}, catch=True)
print(P.bag_list(g, 'items'))
print(g.go(49, 35), g.tile()); g.adv()
for a in g.actors(): print(' actor', a['uid'], a['x'], a['z'], a['scr'])
print(P.bag_list(g, 'items'))
g.save('s20_aqua.dst')
