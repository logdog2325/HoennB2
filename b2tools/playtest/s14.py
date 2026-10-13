import sys; sys.path.insert(0, sys.path[0])
from pt import *
import battle, party as P
g = G('t_wild1.dst', name='s14')
battle.install(g, wanted={265}, catch=True)
g.adv()
for m in P.party(g): print(m['species'], m['level'], m['hp'], m['maxhp'], m['moves'])
print(P.bag_list(g, 'items'))
g.S(True)
g.sheet(os.path.join(PT, 'scratch.png'), cols=5)
g.save('s14.dst')
