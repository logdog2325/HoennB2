import sys; sys.path.insert(0, sys.path[0])
from pt import *
g = G('tour/g2_back_z118.dst', name='t28')
g.can_surf = True; g.can_clear = True
print('at', g.zone(), g.tile(), [ (a['uid'], a['x'], a['z']) for a in g.actors()])
print('route', g.route((35, 3)))
r = g.go(35, 3); print('go', r, g.zone(), g.tile(), hex(g.event()))
g.S(True)
g.adv(); print('after adv', g.zone(), g.tile())
g.sheet(os.path.join(PT, 'scratch.png'))
