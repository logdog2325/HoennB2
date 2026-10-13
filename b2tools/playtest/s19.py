import sys; sys.path.insert(0, sys.path[0])
from pt import *
import battle, party as P
g = G('s18_r104.dst', name='s19')
battle.install(g, run_wild=False, wanted={280, 276, 285}, catch=True)
print('woods', g.warp(7), g.zone(), g.tile()); g.adv()
print(g.go(49, 37), g.tile())
g.hunt([285], max_battles=12)
for m in P.party(g): print(m['species'], m['level'], m['hp'], m['maxhp'], m['moves'])
g.save('s19_woods.dst')
