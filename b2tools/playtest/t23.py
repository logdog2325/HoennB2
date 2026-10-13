import sys; sys.path.insert(0, sys.path[0])
from pt import *
g = G('kit_pg.dst', rom_path=os.path.join(PT, 'pt_pgtest.nds'), name='t23')
g.press('X', 4, 40); g.wait_stable(); g.touch(64, 140, 4, 60); g.run(60); g.S(True)
g.touch(222, 60, 4, 40); g.run(30); g.S(True)
for i in range(8):
    g.run(120); g.S(True)
    for t in g.texts(): print(t)
g.sheet(os.path.join(PT, 'scratch.png'), cols=5)
