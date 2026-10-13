import sys; sys.path.insert(0, sys.path[0])
from pt import *
g = G(sys.argv[1])
im = g.screen(); b = im.crop((0, 192, 256, 384)).convert('RGB')
for p in [(200, 172), (20, 40), (148, 172), (29, 51), (128, 5), (5, 5)]: print(p, b.getpixel(p))
print('naming?', is_naming(im), 'chain', [hex(x) for x in g.event_chain()])
