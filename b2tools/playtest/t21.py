import sys; sys.path.insert(0, sys.path[0])
from pt import *
import battle as BT
g = G('t_double.dst', name='t21')
g.battle_hook = None
def probe(tag):
    b = g.bot().convert('RGB')
    pts = [(64, 50), (192, 50), (64, 98), (192, 98), (128, 74), (10, 50), (246, 50), (128, 20), (40, 168), (128, 178), (215, 168), (214, 168)]
    print(tag, BT.classify(g)[0], [b.getpixel(p) for p in pts])
probe('cmd1')
g.tap(128, 95); probe('moves')
g.tap(192, 57); probe('target(surf)')
g.tap(64, 50); probe('after target')
g.wait_stable(); probe('cmd2')
