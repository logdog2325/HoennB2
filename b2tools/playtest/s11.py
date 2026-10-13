import sys; sys.path.insert(0, sys.path[0])
from pt import *
import battle, party as P
g = G('s10_may103.dst', name='s11')
battle.install(g)
g.talk(178, 282)
print('after', g.zone(), g.tile())
for m in P.party(g): print(m['species'], m['level'], m['hp'], m['maxhp'], m['moves'])
g.S()
g.save('s11_after_may.dst')
g.sheet(os.path.join(PT, 'scratch.png'), cols=5)
