import sys; sys.path.insert(0, sys.path[0])
from pt import *
import battle, party as P
g = G('t_wild1.dst', name='t14')
b = battle.Battle(g, wanted={265}, catch=True)
orig_touch = g.touch
n = [0]
def touch(x, y, f=6, a=20):
    orig_touch(x, y, f, a); n[0] += 1
    if n[0] < 30: g.S(True); print('touch', x, y, battle.classify(g)[0])
g.touch = touch
import threading
b.mod = None
# run limited loop manually
b.mod = b.module(); b.wild = True; b.doubles = False; b.turns = 0
for i in range(60):
    if not g.in_battle(): break
    k, im = battle.classify(g)
    if k == 'cmd': b.command()
    else: g.run(20); g.press('B', 4, 6)
    if n[0] >= 12: break
g.sheet(os.path.join(PT, 'scratch.png'), cols=6)
