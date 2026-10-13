import sys; sys.path.insert(0, sys.path[0])
from pt import *
g = G('tour/g1_back_z368.dst', name='t29')
g.can_surf = True; g.can_clear = True
print('at', g.zone(), g.tile(), 'ex', g.exstate())
r = g.warp(1); print('warp1', r, g.zone(), g.tile(), 'ex', g.exstate())
g.S(True); g.sheet(os.path.join(PT, 'scratch.png'))
