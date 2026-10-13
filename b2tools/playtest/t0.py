import sys; sys.path.insert(0, sys.path[0])
from pt import *
g = G()
for i in range(12):
    g.run(150); g.S(both=True)
    print(i, hex(g.gsys()), hex(g.gdata()), g.zone(), hex(g.field()), hex(g.event()))
g.sheet(os.path.join(PT, 'scratch_t0.png'), cols=6)
