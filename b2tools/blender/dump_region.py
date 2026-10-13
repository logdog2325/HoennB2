"""Dump polygons (material, vertex tile coords, height, UVs) with any vertex in a tile region of a chunk model.
blender --background --python dump_region.py -- chunk.glb x0 z0 x1 z1 [material-substring]"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import b2lib
a = b2lib.args()
b2lib.reset()
obj = b2lib.import_glb(a[0])
x0, z0, x1, z1 = map(float, a[1:5]); filt = a[5] if len(a) > 5 else ''
uv = obj.data.uv_layers.active.data
for p in obj.data.polygons:
    pts = [obj.data.vertices[i].co for i in p.vertices]
    if not any(x0 <= (v.x + 256) / 16 <= x1 and z0 <= (-v.y + 256) / 16 <= z1 for v in pts): continue
    name = b2lib.material_name(obj, p)
    if filt and filt not in name: continue
    vs = []
    for li in p.loop_indices:
        v = obj.data.vertices[obj.data.loops[li].vertex_index].co
        u = uv[li].uv
        vs.append(f'({(v.x+256)/16:.2f},{(-v.y+256)/16:.2f},h{v.z:.0f} uv{u.x:.2f},{u.y:.2f})')
    print(f'{name:12s} ' + ' '.join(vs))
