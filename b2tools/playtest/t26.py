import sys, time; sys.path.insert(0, sys.path[0])
from pt import *
import planner
class FakeG:
    def __init__(s, z, t): s.z, s.t = z, t
    def zone(s): return s.z
    def tile(s): return s.t
fg = FakeG(389, (175, 369))
for tz, tt in ((319, (40, 60)), (216, (20, 20)), (177, (10, 17))):
    t = time.time(); print(tz, planner.plan(fg, tz, tt, surf=True), round(time.time() - t, 2))
