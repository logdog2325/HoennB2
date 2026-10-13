import sys; sys.path.insert(0, sys.path[0])
from pt import *
g = G('intro3.dst')
g.press('RIGHT', 6, 30); g.run(400)
last = None
for k in range(30):
    sb = [s for a, s in g.strbufs() if len(s) > 12]
    if sb != last: print('---', k, g.e.frames, g.zone(), hex(g.event()), sb[-2:] if sb else None); last = sb
    if k % 3 == 0: g.S()
    g.press('A', 6, 50)
    if not g.event(): print('event over at', k); break
g.sheet(os.path.join(PT, 'scratch.png'), cols=5)
