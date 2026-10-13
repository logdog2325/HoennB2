import sys, time; sys.path.insert(0, sys.path[0])
import romdata as R
t = time.time(); rom = R.Rom('pt_sapphire.nds'); print('load', time.time() - t)
print(rom.move(7), rom.types(4), rom.types(258))
h = rom.hdr[389]; print({k: h[k] for k in ('map_type', 'matrix', 'scripts', 'entities', 'area')})
e = rom.entities(389)
for w in e['warps']: print('warp', w)
g = rom.grid(389)
print('matrix', g.w, g.h)
for z in range(350, 372):
    row = ''
    for x in range(165, 192):
        rs = g.rec(x, z)
        if not rs: row += ' '; continue
        r = rs[0]
        row += 'v' if r[2] in R.LEDGE else ('#' if r[3] & 1 else ('~' if R.surf(r) else '.'))
    print(z, row)
h = rom.hdr[390]; print({k: h[k] for k in ('map_type', 'matrix', 'scripts', 'entities', 'area')})
g = rom.grid(390); print('house matrix', g.w, g.h)
for z in range(0, 12):
    print(z, ''.join(('#' if (g.rec(x, z) and g.rec(x, z)[0][3] & 1) else ('.' if g.rec(x, z) else ' ')) for x in range(0, 14)))
for w in rom.entities(390)['warps']: print('warp', w)
