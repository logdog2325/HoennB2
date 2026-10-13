"""do.py IN_STATE|- OUT_STATE|- OUT.png cmd ...   (IN '-' = cold boot)
cmds: A B X Y ST SE (press), A5 (A x5, wait 40 each), U D L R (tap), hU16 (hold), W60, S (top shot), SS (both),
Tx,y (touch), P (info), Q (shot every n)"""
import sys; sys.path.insert(0, sys.path[0])
from pt import *
ins, outs, png = sys.argv[1:4]
g = G(None if ins == '-' else ins)
K = {'A': 'A', 'B': 'B', 'X': 'X', 'Y': 'Y', 'ST': 'START', 'SE': 'SELECT', 'U': 'UP', 'D': 'DOWN', 'L': 'LEFT', 'R': 'RIGHT'}
def info(): print('frame', g.e.frames, 'zone', g.zone(), 'tile', g.tile(), 'field', hex(g.field()), 'event', hex(g.event()), flush=True)
for c in sys.argv[4:]:
    if c in K: g.press(K[c], 6, 30)
    elif c[0] == 'A' and c[1:].isdigit():
        for _ in range(int(c[1:])): g.press('A', 6, 40)
    elif c[0] == 'B' and c[1:].isdigit():
        for _ in range(int(c[1:])): g.press('B', 6, 40)
    elif c[0] == 'h': g.hold(K[c[1]], int(c[2:])); g.run(4)
    elif c[0] == 'W': g.run(int(c[1:]))
    elif c == 'S': g.S()
    elif c == 'SS': g.S(True)
    elif c[0] == 'T': g.touch(*map(int, c[1:].split(',')), 6, 40)
    elif c == 'P': info()
    else: print('?', c)
if outs != '-': g.save(outs)
g.sheet(png, cols=4)
info()
