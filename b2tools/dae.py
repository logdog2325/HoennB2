"""Minimal COLLADA (.dae) writer for static, textured models that CTRMap's DAE importer reads (same layout as the
apicula exports that round-tripped into the game). Coordinates are Black 2 model units, Y up.

    m = Model('littleroot')
    m.tri('grass01ax', [(x, y, z, u, v), ...3 vertices])     # or m.quad(...) with 4 vertices
    m.write('out.dae', wrap={'grass01ax': ('WRAP', 'WRAP')})

Texture and image ids are the game texture names (dots allowed, at most 16 characters): the game binds textures by
these names, so they must match the area's texture set exactly.
"""
from collections import OrderedDict
from xml.sax.saxutils import escape

class Model:
    def __init__(self, name):
        self.name = name
        self.tris = OrderedDict()   # material -> list of triangles [(x,y,z,u,v,(r,g,b)), ...]

    def tri(self, mat, verts, color=(1.0, 1.0, 1.0)):
        assert len(mat) <= 16, mat
        self.tris.setdefault(mat, []).append([tuple(v[:5]) + (tuple(v[5]) if len(v) > 5 else color,) for v in verts])

    def quad(self, mat, verts, color=(1.0, 1.0, 1.0)):
        """verts in order around the quad (counter-clockwise seen from the side that should face the camera)."""
        a, b, c, d = verts
        self.tri(mat, [a, b, c], color); self.tri(mat, [a, c, d], color)

    def extend(self, other, dx=0.0, dy=0.0, dz=0.0):
        for mat, tris in other.tris.items():
            for t in tris:
                self.tris.setdefault(mat, []).append([(x + dx, y + dy, z + dz, u, v, c) for x, y, z, u, v, c in t])

    def write(self, path, wrap=None, double_sided=()):
        wrap = wrap or {}
        out = ['<?xml version="1.0" encoding="utf-8"?>',
               '<COLLADA xmlns="http://www.collada.org/2005/11/COLLADASchema" version="1.4.1">',
               '  <asset><unit name="meter" meter="1"/><up_axis>Y_UP</up_axis></asset>',
               '  <library_images>']
        mats = list(self.tris)
        for m in mats:
            out.append(f'    <image id="{escape(m)}"><init_from>{escape(m)}.png</init_from></image>')
        out.append('  </library_images>\n  <library_materials>')
        for i, m in enumerate(mats):
            out.append(f'    <material id="material{i}" name="{escape(m)}"><instance_effect url="#effect{i}"/></material>')
        out.append('  </library_materials>\n  <library_effects>')
        for i, m in enumerate(mats):
            ws, wt = wrap.get(m, ('WRAP', 'WRAP'))
            out.append(f'''    <effect id="effect{i}" name="{escape(m)}">
      <profile_COMMON>
        <newparam sid="Image-surface"><surface type="2D"><init_from>{escape(m)}</init_from><format>A8R8G8B8</format></surface></newparam>
        <newparam sid="Image-sampler"><sampler2D><source>Image-surface</source><wrap_s>{ws}</wrap_s><wrap_t>{wt}</wrap_t><minfilter>NEAREST</minfilter><magfilter>NEAREST</magfilter><mipfilter>NEAREST</mipfilter></sampler2D></newparam>
        <technique sid="common"><phong>
          <emission><color>0 0 0 1</color></emission>
          <ambient><color>0.8064516 0.8064516 0.8064516 1</color></ambient>
          <diffuse><texture texture="Image-sampler" texcoord="tc"/></diffuse>
          <specular><color>0 0 0 1</color></specular>
          <transparent><texture texture="Image-sampler" texcoord="tc"/></transparent>
        </phong></technique>
        {'<extra><technique profile="GOOGLEEARTH"><double_sided>1</double_sided></technique></extra>' if m in double_sided else ''}
      </profile_COMMON>
    </effect>''')
        out.append('  </library_effects>\n  <library_geometries>')
        pos, uvs, cols, nrm, prims = [], [], [], [], []
        fixed = getattr(self, 'normals', {})     # material -> one normal for all its triangles (Black 2's trees: up)
        for i, m in enumerate(mats):
            idx = []
            for t in self.tris[m]:
                # face normal from the winding (the game lights by normals; without them colours wash out)
                (ax, ay, az), (bx, by, bz), (cx, cy, cz) = [v[:3] for v in t]
                ux_, uy_, uz_ = bx - ax, by - ay, bz - az
                vx_, vy_, vz_ = cx - ax, cy - ay, cz - az
                n_ = (uy_ * vz_ - uz_ * vy_, uz_ * vx_ - ux_ * vz_, ux_ * vy_ - uy_ * vx_)
                ln = (n_[0] ** 2 + n_[1] ** 2 + n_[2] ** 2) ** 0.5 or 1.0
                n_ = fixed.get(m) or tuple(c_ / ln for c_ in n_)
                for x, y, z, u, v, c in t:
                    pos.append((x, y, z)); uvs.append((u, v)); cols.append(c); nrm.append(n_)
                    n = len(pos) - 1
                    idx.append(f'{n} {n} {n} {n}')
            prims.append((i, len(self.tris[m]), ' '.join(idx)))
        f = lambda xs: ' '.join(f'{v:.4f}'.rstrip('0').rstrip('.') if v != int(v) else str(int(v)) for t in xs for v in t)
        out.append(f'''    <geometry id="geometry" name="{escape(self.name)}">
      <mesh>
        <source id="positions"><float_array id="positions-array" count="{3*len(pos)}">{f(pos)}</float_array>
          <technique_common><accessor source="#positions-array" count="{len(pos)}" stride="3"><param name="X" type="float"/><param name="Y" type="float"/><param name="Z" type="float"/></accessor></technique_common></source>
        <source id="texcoords"><float_array id="texcoords-array" count="{2*len(uvs)}">{f(uvs)}</float_array>
          <technique_common><accessor source="#texcoords-array" count="{len(uvs)}" stride="2"><param name="S" type="float"/><param name="T" type="float"/></accessor></technique_common></source>
        <source id="colors"><float_array id="colors-array" count="{3*len(cols)}">{f(cols)}</float_array>
          <technique_common><accessor source="#colors-array" count="{len(cols)}" stride="3"><param name="R" type="float"/><param name="G" type="float"/><param name="B" type="float"/></accessor></technique_common></source>
        <source id="normals"><float_array id="normals-array" count="{3*len(nrm)}">{f(nrm)}</float_array>
          <technique_common><accessor source="#normals-array" count="{len(nrm)}" stride="3"><param name="X" type="float"/><param name="Y" type="float"/><param name="Z" type="float"/></accessor></technique_common></source>
        <vertices id="vertices"><input semantic="POSITION" source="#positions"/></vertices>''')
        for i, n, idx in prims:
            out.append(f'''        <triangles material="material{i}" count="{n}">
          <input semantic="VERTEX" source="#vertices" offset="0"/>
          <input semantic="TEXCOORD" source="#texcoords" offset="1" set="0"/>
          <input semantic="COLOR" source="#colors" offset="2" set="0"/>
          <input semantic="NORMAL" source="#normals" offset="3"/>
          <p>{idx}</p>
        </triangles>''')
        out.append('      </mesh>\n    </geometry>\n  </library_geometries>')
        binds = ''.join(f'<instance_material symbol="material{i}" target="#material{i}"><bind_vertex_input semantic="tc" input_semantic="TEXCOORD" input_set="0"/></instance_material>' for i in range(len(mats)))
        out.append(f'''  <library_visual_scenes>
    <visual_scene id="scene">
      <node id="{escape(self.name)}" name="{escape(self.name)}" type="NODE">
        <instance_geometry url="#geometry"><bind_material><technique_common>{binds}</technique_common></bind_material></instance_geometry>
      </node>
    </visual_scene>
  </library_visual_scenes>
  <scene><instance_visual_scene url="#scene"/></scene>
</COLLADA>''')
        open(path, 'w').write('\n'.join(out))
        return sum(len(t) for t in self.tris.values())
