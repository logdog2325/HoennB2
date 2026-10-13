import sys; sys.path.insert(0, sys.path[0])
from pt import *
import battle as BT
g = G('t_double.dst', name='t22')
b = BT.Battle(g); b.mod = b.module(); print('style', b.style())
g.adv()
print('after', g.zone(), g.tile(), g.idle())
