"""zinfo.py ZONE [x0 z0 x1 z1]: a zone's entities and its collision as ASCII (from the release ROM)."""
import sys; sys.path.insert(0, sys.path[0])
import romdata as R
from pt import ROM
rom = R.Rom(ROM)
z = int(sys.argv[1])
h = rom.hdr[z]; e = rom.entities(z)
print({k: h[k] for k in ('map_type', 'matrix', 'scripts', 'text', 'entities', 'area', 'parent')})
for i, w in enumerate(e['warps']): print(f"warp {i}: ({w['tile_x']},{w['tile_z']}) {w['w']}x{w['h']} -> zone {w['dest_zone']} warp {w['dest_warp']} type {w['type']} dir {w['dir']}")
for n in e['npcs']: print(f"npc uid {n['uid']} ({n['x']},{n['z']}) model {n['model']} script {n['script']} flag {n['flag']} move {n['move']} evtype {n['evtype']} dir {n['dir']} p {n['p0']},{n['p1']},{n['p2']}")
for s in e['signs']: print(f"sign ({(s['x'])},{s['z']}) script {s['script']} dir {s['dir']}")
for t in e['triggers']: print(f"trigger ({t['x']},{t['z']}) {t['w']}x{t['h']} script {t['script']} work {t['work']:#x}=={t['value']}")
g = rom.grid(z)
ws = {(w['tile_x'] + i, w['tile_z'] + j) for w in e['warps'] for i in range(w['w']) for j in range(w['h'])}
ns = {(n['x'], n['z']) for n in e['npcs']}
if len(sys.argv) > 5: x0, z0, x1, z1 = map(int, sys.argv[2:6])
else:
    xs = [w['tile_x'] for w in e['warps']] + [n['x'] for n in e['npcs']] or [0]
    zs = [w['tile_z'] for w in e['warps']] + [n['z'] for n in e['npcs']] or [0]
    if g.w * g.h <= 4: x0, z0, x1, z1 = 0, 0, g.w * 32 - 1, g.h * 32 - 1
    else: x0, z0, x1, z1 = min(xs) - 8, min(zs) - 8, max(xs) + 8, max(zs) + 8
rows = []
for zz in range(z0, z1 + 1):
    row = ''
    for x in range(x0, x1 + 1):
        rs = g.rec(x, zz)
        if (x, zz) in ws: row += 'W'; continue
        if (x, zz) in ns: row += 'N'; continue
        if not rs: row += ' '; continue
        r = rs[0]
        c = 'v' if r[2] in R.LEDGE else ('#' if r[3] & 1 else ('~' if R.surf(r) else ('g' if r[2] in R.GRASS else '.')))
        if len(rs) > 1: c = c.upper() if c != '.' else ','
        row += c
    if row.strip('# '): rows.append(f'{zz:4d} {row}')
print(f'x from {x0}')
print('\n'.join(rows))
