"""Forced loss (user's idea): every party Pokémon level 1 with 1 HP and 1 in every stat, a wild battle on Route 101,
lose -> blackout. Before it: the return point (RESPAWN_ZONE_INFO index) and Mr. Briney's flags are set in RAM.
    FF_ROM=ROM python lose.py VER FROM_STATE CASE      CASE: rustboro | briney | rescue | sailed"""
import sys, os, re, struct; sys.path.insert(0, sys.path[0])
from pt import *
import battle, party as P, flags as F
ver, frm, case = sys.argv[1:4]
H = open(os.path.join(ROOT, 'src', 'include', 'hoenn.h')).read()
def fid(n): return int(re.search(r'#define\s+' + n + r'\s+(\d+|0x[0-9a-fA-F]+)', H).group(1), 0)
BRINEY = ['FLAG_HIDE_MR_BRINEY_DEWFORD_TOWN', 'FLAG_HIDE_MR_BRINEY_BOAT_DEWFORD', 'FLAG_HIDE_MR_BRINEY_ROUTE104_HOUSE',
          'FLAG_HIDE_MR_BRINEY_BOAT_ROUTE104', 'FLAG_HIDE_MR_BRINEY_ROUTE109', 'FLAG_HIDE_MR_BRINEY_BOAT_ROUTE109']
g = G(os.path.join(STATES, ver, frm), name='lose-' + case)
def ret_addr(): return g.u32(g.gdata() + 0x15C) + 0x70           # SetCurrentTeleportOrDeathZone's u16
def weaken():
    d = g.gdata(); p = g.u32(d + 0x194); cnt = g.u32(p + 4)
    g.e.d.memory.write_long(p + 4, 1); cnt = 1                    # one Pokémon: its faint ends the battle
    for i in range(cnt):
        a = p + 8 + 220 * i; pkm = bytearray(g.rd(a, 220))
        pid = struct.unpack_from('<I', pkm, 0)[0]
        w = P._xor(list(struct.unpack('<42H', pkm[136:220])), pid)
        w[2] = (w[2] & 0xff00) | 1                                   # level 1
        for k in range(3, 10): w[k] = 1                              # HP 1, max HP and every stat 1
        pkm[136:220] = struct.pack('<42H', *P._xor(w, pid))
        for k in range(0, 220, 4): g.e.d.memory.write_long(a + k, struct.unpack_from('<I', pkm, k)[0])
def briney(): return {n.replace('FLAG_HIDE_MR_BRINEY_', ''): F.flag(g, fid(n)) for n in BRINEY}
# the case's setup
idx = {'rustboro': 16, 'rustboro_old': 16, 'briney': 16, 'rescue': 15, 'sailed': 15,
       'rustboro_key0': 16, 'rustboro_old_key0': 16, 'rustboro_old_key0_sailed': 16, 'rustboro_key0_sailed': 16}[case]
if '_key0' in case:    # the save's Key System check (arm9 0x02010564) on its other answer (0), as in the
    g.e.d.memory.write_short(0x02010564, 0x2000)          # user's save: movs r0, #0
    g.e.d.memory.write_short(0x02010566, 0x4770)          # bx lr
if case.startswith('rustboro_old'):
    g.e.d.memory.write_short(0x0201732A, 0xD80B)
print('branch at 0x0201732A:', hex(g.u16(0x0201732A)), 'check at 0x02010564:', hex(g.u16(0x02010564)), flush=True)
HITS = []
def hook(name):
    def cb(a, n):
        if len(HITS) < 40: HITS.append((name, g.e.d.memory.register_arm9.r0 & 0xffff, hex(g.e.d.memory.register_arm9.lr)))
        return True
    return cb
for addr, name in ((0x02017310, 'GetReturnLocationIdx'), (0x0201733E, 'swap->15'), (0x02017342, 'swap->16'),
                   (0x02017344, 'return'), (0x02010564, 'key check')):
    g.e.d.memory.register_exec(addr, hook(name))
g.e.d.memory.write_short(ret_addr(), idx)
if case == 'briney':          # his boat waits in Dewford (sailing started), you heal in Rustboro, then faint
    F.set_flag(g, fid('FLAG_MR_BRINEY_SAILING_INTRO'), 1)
    for n, v in zip(BRINEY, (0, 0, 1, 1, 1, 1)): F.set_flag(g, fid(n), v)
if case == 'sailed':          # sailed normally: the rescue must leave you in Dewford
    F.set_flag(g, fid('FLAG_MR_BRINEY_SAILING_INTRO'), 1)
    for n, v in zip(BRINEY, (0, 0, 1, 1, 1, 1)): F.set_flag(g, fid(n), v)
if case.endswith('_key0_sailed'):   # sailing started (no rescue), his boat at his house: shows where you wake up
    F.set_flag(g, fid('FLAG_MR_BRINEY_SAILING_INTRO'), 1)
if case == 'rescue':
    F.set_flag(g, fid('FLAG_MR_BRINEY_SAILING_INTRO'), 0)
weaken()
print('setup: return', g.u16(ret_addr()), 'party', [(m['species'], m['level'], m['hp']) for m in P.party(g)],
      'sailing intro', F.flag(g, fid('FLAG_MR_BRINEY_SAILING_INTRO')), 'briney', briney(), flush=True)
battle.install(g, run_wild=False)
z0 = g.zone()
for i in range(10):
    try:
        if g.pace_grass(80): g.adv(maxn=900)
    except Stop as ex:
        print('bot gave up:', ex, flush=True)
        for k in range(160):
            if k % 10 == 0: g.S(True)
            if g.field() != 0 and g.event() == 0: break
            g.press('A', 4, 26)
        g.wait_idle()
    if g.zone() != z0: break
for k in range(60):                    # the nurse's lines, then any condition script (the rescue's warp)
    g.press('A', 4, 26)
    if k % 15 == 0: g.S(True)
g.wait_idle(); g.run(240); g.wait_idle()
g.S(True)
print('after: zone', g.zone(), 'tile', g.tile(), 'return', g.u16(ret_addr()),
      'party', [(m['species'], m['level'], m['hp']) for m in P.party(g)], 'briney', briney(), flush=True)
g.sheet(os.path.join(PT, 'shots', f'{ver}_lose_{case}.png'), cols=4)
print('hits:', HITS, flush=True)
