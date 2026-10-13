import sys, time; sys.path.insert(0, sys.path[0])
from pt import *
import planner
class FakeG:
    def __init__(s, z, t): s.z, s.t = z, t
    def zone(s): return s.z
    def tile(s): return s.t
for surf in (False, True):
    t = time.time(); r = planner.regions(416, surf); print('regions', surf, len(r), len(set(r.values())), time.time() - t)
fg = FakeG(396, (7, 6))
for tz, tt in ((326, (217, 293)), (406, (256, 206)), (96, (555, 137)), (16, (373, 67))):
    for surf in (False, True):
        t = time.time(); print(tz, surf, planner.plan(fg, tz, tt, surf=surf), round(time.time() - t, 2))
