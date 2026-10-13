import sys; sys.path.insert(0, sys.path[0])
from pt import *
g = G('s03_mayroom.dst', name='s04')
g.adv()
for a in g.actors(): print(' actor', a['uid'], a['x'], a['z'], a['scr'], a['face'])
may = [a for a in g.actors() if a['uid'] == 1][0]
g.talk(may['x'], may['z']); g.S()
print('after May', g.zone(), g.tile())
for a in g.actors(): print(' actor', a['uid'], a['x'], a['z'], a['scr'])
g.save('s04_aftermay.dst')
g.sheet(os.path.join(PT, 'scratch.png'), cols=5)
