"""poke.py STATE X Z: stand next to (X,Z) (each side in turn), face it, press A, screenshot."""
import sys; sys.path.insert(0, sys.path[0])
from pt import *
g = G(sys.argv[1])
x, z = int(sys.argv[2]), int(sys.argv[3])
grid = g.nav_grid()
for dx, dz in ((0, 1), (0, -1), (-1, 0), (1, 0)):
    c = (x + dx, z + dz)
    print(c, grid.rec(*c), 'walk', any(R.land(r) for r in grid.rec(*c)))
print('target rec', grid.rec(x, z))
for dx, dz in ((0, 1), (0, -1), (-1, 0), (1, 0)):
    c = (x + dx, z + dz)
    if not any(R.land(r) for r in grid.rec(*c)): continue
    r = g.go(*c); print('go', c, r, g.tile())
    if r is not True: continue
    g.face((-dx, -dz)); g.press('A', 4, 30); g.run(30); g.S()
    print('event', hex(g.event()), g.texts())
    g.adv()
g.sheet(os.path.join(PT, 'scratch.png'))
