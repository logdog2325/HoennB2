import sys; sys.path.insert(0, sys.path[0])
from pt import *
g = G('s08_lab.dst')
gs = g.gsys()
print('naming: gsys words', [hex(g.u32(gs + 4 * i)) for i in range(16)], 'byte35', g.u8(gs + 0x35))
g.press('START', 4, 30); g.S(True); g.press('A', 4, 60); g.S(True)
for i in range(20):
    g.run(30)
    if i == 5: print('after: gsys words', [hex(g.u32(gs + 4 * i)) for i in range(16)], 'byte35', g.u8(gs + 0x35))
g.S(True)
print(g.zone(), g.tile(), hex(g.event()), hex(g.field()))
g.save('s08b.dst')
g.sheet(os.path.join(PT, 'scratch.png'), cols=5)
