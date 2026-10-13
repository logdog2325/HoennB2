import sys; sys.path.insert(0, sys.path[0])
from pt import *
import flags as F
g = G(sys.argv[1])
print([(n, F.flag(g, n)) for n in range(2819, 2840)])
