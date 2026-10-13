import sys; sys.path.insert(0, sys.path[0])
from pt import *
import battle, party as P
g = G('s16_gym.dst', name='s17')
battle.install(g, run_wild=True, wanted={280, 276}, catch=True)
g.talk(5, 107)
for a in g.actors(): print(' actor', a['uid'], a['x'], a['z'], a['scr'])
print(g.zone(), g.tile())
g.S()
g.save('s17_dad.dst')
g.sheet(os.path.join(PT, 'scratch.png'))
