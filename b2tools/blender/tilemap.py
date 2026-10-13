"""Print, for each 16x16 tile of a chunk model, the material of the highest polygon over it, plus heights.
blender --background --python tilemap.py -- chunk.glb"""
import sys, os, collections
sys.path.insert(0, os.path.dirname(__file__))
import b2lib
b2lib.reset()
obj = b2lib.import_glb(b2lib.args()[0])
me = obj.data
xs = [v.co.x for v in me.vertices]; ys = [v.co.y for v in me.vertices]; zs = [v.co.z for v in me.vertices]
print('bounds x %.1f..%.1f  y %.1f..%.1f  z %.1f..%.1f' % (min(xs), max(xs), min(ys), max(ys), min(zs), max(zs)))
top = {}
mats = collections.Counter()
for p in me.polygons:
    c = p.center
    tx, tz = b2lib.tile_of(c.x, c.y)
    name = b2lib.material_name(obj, p)
    mats[name] += 1
    if not (0 <= tx < 32 and 0 <= tz < 32): continue
    if (tx, tz) not in top or c.z > top[(tx, tz)][0]:
        top[(tx, tz)] = (c.z, name)
syms = {}
chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
print('top material per tile:')
for tz in range(32):
    row = ''
    for tx in range(32):
        if (tx, tz) not in top: row += ' '; continue
        n = top[(tx, tz)][1]
        if n not in syms: syms[n] = chars[len(syms)]
        row += syms[n]
    print(row)
print(' '.join(f'{s}={n}' for n, s in syms.items()))
print('ground heights (min z of grass-ish polys):', sorted(collections.Counter(round(p.center.z) for p in me.polygons if 'grass' in b2lib.material_name(obj, p) or 'michi' in b2lib.material_name(obj, p)).items())[:12])
