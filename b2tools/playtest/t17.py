import sys; sys.path.insert(0, sys.path[0])
from pt import *
import pt
g = G('s20_aqua.dst')
print('go', g.go(62, 48), g.tile())
for fr in (1, 2):
    g.hold('LEFT', fr); g.run(12); m = g.me(); print('tap', fr, {k: m[k] for k in ('x', 'z', 'face')})
g.hold('UP', 3); g.run(20)
grid = g.nav_grid(); p = g.tile(); y = g.height()
print('at', p, y, 'obst', g.obstacles(), 'blocked', g.blocked)
for d in pt.DIRK: print(d, pt.step_options(grid, p, y, d, 'land'))
print(g.route((49, 36)))
