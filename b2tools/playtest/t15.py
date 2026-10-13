import sys, time; sys.path.insert(0, sys.path[0])
from pt import *
g = G('s20_aqua.dst')
t = time.time(); g.run(600); print('plain', 600 / (time.time() - t))
hits = []
for a in (0x0207c774, 0x0207c7dc, 0x0207c7e8, 0x0207c7f4):
    g.m = g.e.d.memory
    g.e.d.memory.register_exec(a, lambda addr, n: hits.append(addr))
t = time.time(); g.run(600); print('hooked', 600 / (time.time() - t), hits)
g.walk_dir((1, 0), 3)
t = time.time(); g.run(600); print('hooked2', 600 / (time.time() - t), hits)
