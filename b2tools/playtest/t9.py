import sys; sys.path.insert(0, sys.path[0])
from pt import *
import syms
def evinfo(g):
    ev = g.event(); out = []
    while g.ok(ev) and len(out) < 6:
        cb = g.u32(ev + 4); out.append((hex(ev), hex(cb), syms.name(cb)))
        ev = g.u32(ev)
    return out
g = G(sys.argv[1]); print(sys.argv[1], evinfo(g))
