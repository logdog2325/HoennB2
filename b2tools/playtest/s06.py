import sys; sys.path.insert(0, sys.path[0])
from pt import *
g = G('s05_route101.dst', name='s06')
print(g.go(175, 346, adjacent=True), g.tile())
here = g.tile(); g.face((175 - here[0], 346 - here[1])); g.press('A', 4, 30)
for i in range(30):
    for t in g.texts(): print('  >', t[:120])
    g.S(True); g.run(40)
    if g.field() == 0: print('field closed at', i); break
    if g.choice_menu(): print('choice'); break
    g.press('A', 4, 20)
g.save('s06_bag.dst')
g.sheet(os.path.join(PT, 'scratch.png'), cols=6)
