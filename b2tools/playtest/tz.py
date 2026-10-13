"""tz.py STATE [label]: tour the zone the state stands in."""
import sys; sys.path.insert(0, sys.path[0])
from pt import *
import battle, tour
g = G(sys.argv[1], name='tz')
battle.install(g, run_wild=True)
T = tour.Tour(g, label=sys.argv[2] if len(sys.argv) > 2 else 'test')
print(T.zone())
