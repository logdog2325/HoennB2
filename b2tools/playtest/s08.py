import sys; sys.path.insert(0, sys.path[0])
from pt import *
g = G('t_cmd.dst', name='s08')
def simple_battle(g):
    # crude: FIGHT + move 1 at the command menu, B otherwise
    for i in range(400):
        if g.field() != 0: return
        b = g.bot().convert('RGB'); p = b.getpixel((40, 168))
        if p[0] > 180 and p[2] < 100:
            g.touch(128, 95, 4, 30); g.touch(64, 57, 4, 30)
        else:
            g.run(20)
            if i % 3 == 0: g.press('B', 4, 10)
        for t in g.texts(): print('  b>', t[:100])
g.battle_hook = simple_battle
g.adv(maxn=800)
print('now', g.zone(), g.tile())
g.S(True)
g.save('s08_lab.dst')
g.sheet(os.path.join(PT, 'scratch.png'), cols=5)
