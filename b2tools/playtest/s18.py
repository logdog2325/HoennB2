import sys; sys.path.insert(0, sys.path[0])
from pt import *
import battle, party as P
g = G('s17_dad.dst', name='s18')
battle.install(g, run_wild=False, wanted={280, 276, 285}, catch=True)
g.exit_room(); print('out', g.zone(), g.tile())
g.heal(); print('healed', g.zone(), g.tile())
for m in P.party(g): print(m['species'], m['level'], m['hp'], m['maxhp'], m['moves'])
print('to woods', g.go(58, 279), g.zone(), g.tile())
g.save('s18_r104.dst')
for m in P.party(g): print(m['species'], m['level'], m['hp'], m['maxhp'], m['moves'])
