import sys; sys.path.insert(0, sys.path[0])
from pt import *
import battle, party as P
g = G('s14.dst', name='s15')
battle.install(g, run_wild=True)
print(g.go(178, 316), g.zone(), g.tile())   # Oldale
g.heal()
for m in P.party(g): print(m['species'], m['level'], m['hp'], m['maxhp'])
g.save('s15_oldale.dst')
