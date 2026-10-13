import sys; sys.path.insert(0, sys.path[0])
from pt import *
import battle, party as P
g = G('s15_oldale.dst', name='s16')
battle.install(g, run_wild=True, wanted={280, 276}, catch=True)
print('to gym door', g.go(103, 299), g.zone(), g.tile())
for m in P.party(g): print(m['species'], m['level'], m['hp'], m['maxhp'])
print('gym', g.enter(452), g.zone(), g.tile()); g.adv()
for a in g.actors(): print(' actor', a['uid'], a['x'], a['z'], a['scr'])
g.S()
g.save('s16_gym.dst')
g.sheet(os.path.join(PT, 'scratch.png'))
