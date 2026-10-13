import sys; sys.path.insert(0, sys.path[0])
from pt import *
import battle, party as P
g = G('t_wild1.dst', name='s13')
print('pace', g.pace_grass())
for i in range(40):
    g.run(20)
    k, im = battle.classify(g)
    if k == 'cmd': break
g.save('t_wild1.dst')
g.S(True)
g.touch(40, 168, 4, 60); g.S(True)
g.sheet(os.path.join(PT, 'scratch.png'), cols=5)
