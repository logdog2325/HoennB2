import sys; sys.path.insert(0, sys.path[0])
from pt import *
g = G('tour/g1_back_z326.dst', name='t27')
print(g.go(217, 287), g.tile()); g.S(True)
for i in range(3):
    n = g.walk_dir((-1, 0), 1); me = g.me()
    print('step left', n, g.tile(), 'y', me['wy'], 'ex', g.exstate(), 'zone', g.zone()); g.S(True)
n = g.walk_dir((0, -1), 1); print('up', n, g.tile(), g.zone()); g.S(True)
g.sheet(os.path.join(PT, 'scratch.png'), cols=5)
