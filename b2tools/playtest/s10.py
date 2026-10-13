import sys; sys.path.insert(0, sys.path[0])
from pt import *
import battle
g = G('s09_opts.dst', name='s10')
battle.install(g, run_wild=False)
print('exit lab', g.warp(0), g.zone(), g.tile()); g.adv()
r = g.go(178, 283); print('to May', r, g.zone(), g.tile())
g.S()
g.save('s10_may103.dst')
g.sheet(os.path.join(PT, 'scratch.png'), cols=5)
