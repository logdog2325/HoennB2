import sys; sys.path.insert(0, sys.path[0])
from pt import *
g = G(None, rom_path=os.path.join(PT, 'pt_pg.nds'), name='t24')
g.run(1300); g.S(True)
for i in range(6):
    g.press('A', 4, 120); g.S(True)
for i in range(4):
    g.run(150); g.S(True)
print(g.zone(), g.tile(), g.idle())
g.sheet(os.path.join(PT, 'scratch.png'), cols=6)
