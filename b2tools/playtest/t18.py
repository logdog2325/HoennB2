import sys; sys.path.insert(0, sys.path[0])
from pt import *
import mkparty, party as P
g = G(sys.argv[1])
g.wait_idle()
for m in mkparty.install(g): print(m and (m['species'], m['level'], m['hp'], m['maxhp'], m['moves'], m['nick']))
g.run(30); print('idle', g.idle())
g.save(sys.argv[2])
