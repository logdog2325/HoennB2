import sys; sys.path.insert(0, sys.path[0])
from pt import *
g = G('s07_picked.dst')
def cmd():
    b = g.bot().convert('RGB'); p = b.getpixel((40, 168)); return p[0] > 180 and p[2] < 100
for i in range(80):
    g.run(20)
    if cmd(): print('cmd menu at', i); break
    if g.field() != 0 or i < 30: g.press('A', 4, 10)
g.save('t_cmd.dst')
g.S(True)
b = g.bot().convert('RGB')
pts = [(128, 95), (40, 168), (128, 178), (215, 168), (64, 57), (192, 57), (128, 170), (128, 20)]
print('cmd', [b.getpixel(p) for p in pts])
g.touch(128, 95, 4, 40); g.S(True)
b = g.bot().convert('RGB'); print('moves', [b.getpixel(p) for p in pts + [(64, 104), (192, 104)]])
g.touch(64, 57, 4, 40); g.S(True)
for i in range(10): g.run(40); g.S(True)
g.sheet(os.path.join(PT, 'scratch.png'), cols=7)
