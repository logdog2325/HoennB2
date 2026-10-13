import sys; sys.path.insert(0, sys.path[0])
from pt import *
g = G('s07_picked.dst')
for i in range(12): g.run(100); g.press('A', 4, 10)
g.run(200)
m = g.battle_module(); print('module', hex(m) if m else None)
g.save('t_battle1.dst')
def bm(a):
    sp, mhp, hp = struct.unpack('<HHH', g.rd(a + 0x0c, 6))
    lvl = g.u8(a + 0x16)
    t1, t2 = g.u8(a + 0xf8), g.u8(a + 0xf9)
    moves = []
    for i in range(4):
        mid, pp, mpp = struct.unpack('<HBB', g.rd(a + 0x104 + 14 * i, 4))
        moves.append((mid, pp, mpp))
    return dict(species=sp, maxhp=mhp, hp=hp, level=lvl, types=(t1, t2), moves=moves, monId=g.u8(a + 0x17))
for pc in (0, 1):
    pcon = m + 0xc8 + 0xe8 * pc
    print('pokecon', pc, hex(pcon), 'main', hex(g.u32(pcon)))
    for cl in range(4):
        base = pcon + 4 + 0x1c * cl
        ptrs = struct.unpack('<6I', g.rd(base, 24)); cnt = g.u8(base + 24)
        print(' client', cl, 'count', cnt, [hex(p) for p in ptrs[:cnt]])
        for p in ptrs[:cnt]:
            if g.ok(p): print('   ', bm(p))
print('playerClientId', g.u8(m + 0x46c), 'clientCount', g.u8(m + 0x46b))
