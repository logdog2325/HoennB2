import sys; sys.path.insert(0, sys.path[0])
from pt import *
import party as P
g = G(sys.argv[1])
for k in P.POCKETS: print(k, P.bag_list(g, k))
