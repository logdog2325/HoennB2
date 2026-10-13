import sys; sys.path.insert(0, sys.path[0])
from pt import *
import party as P
g = G(sys.argv[1])
d = g.gdata(); p = g.u32(d + 0x194); print('party ptr', hex(p), struct.unpack('<II', g.rd(p, 8)))
for m in P.party(g): print(m)
