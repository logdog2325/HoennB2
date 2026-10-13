"""Graphical-glitch checks for the built Hoenn overworld (exterior sweep, 2026-10-06). Reads a built world
(world.py output: cells/<cx>_<cz>/terrain.dae + placements.bin) and the building models the cells place (our DAEs
next to the registry's .nsbmd files, Black 2's own pack-0 models converted once with tools/apicula).

    python3 exterior_check.py layers  [WORLD]        surfaces closer than 2 units (flicker in melonDS)
    python3 exterior_check.py holes   [WORLD]        spots the game camera sees through (nothing drawn: black)
    python3 exterior_check.py render  MAP [OUT.png] [WORLD]   camera-angle render of one map, terrain + buildings
    python3 exterior_check.py buildings [WORLD]      building models vs the ground and their door tiles

WORLD defaults to $HOENN_WORLD_DIR or work/agents/exterior/world.

Layers: every triangle is rasterised on a 2-unit grid in the plane its normal points most along (XZ for ground and
roofs, XY for south/north walls, ZY for east/west walls); where two triangles that face the same way (normals within
~11 degrees) cover the same sample less than 2 units apart along that normal, the pair is reported. Black 2 keeps its
own layered surfaces at least 2 units apart; closer ones depth-fight per pixel in melonDS (notes/TESTING.md,
commit df33c9e: paths at 0.5 above the grass flickered, at 2 they don't). Two copies of the same surface (same
texture, same texture coordinates) are listed separately: they fight too, but both draw the same texels.
"""
import os, sys, re, json, math, struct, subprocess
import numpy as np
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
NS = '{http://www.collada.org/2005/11/COLLADASchema}'
FILES = os.path.join(ROOT, 'external', 'pokebw2', 'build', 'b2_us', 'files')
APICULA = os.path.join(ROOT, 'tools', 'apicula', 'bin', 'apicula')
CACHE = os.path.join(ROOT, 'work', 'agents', 'exterior', 'models')
MIN_GAP = 2.0

def world_dir(arg=None):
    return arg or os.environ.get('HOENN_WORLD_DIR') or os.path.join(ROOT, 'work', 'agents', 'exterior', 'world')

# ---------------------------------------------------------------------------------------------------------- DAE
def load_dae(path):
    """[(material, image path or None, P (N,3,3), UV (N,3,2), alpha (N,))] of a COLLADA file (ours or apicula's)."""
    root = ET.parse(path).getroot()
    d = os.path.dirname(path)
    imgs = {i.get('id'): i.find(NS + 'init_from').text for i in root.iter(NS + 'image')}
    eff = {}
    for e in root.iter(NS + 'effect'):
        surf = e.find('.//' + NS + 'surface/' + NS + 'init_from')
        img = imgs.get(surf.text, surf.text) if surf is not None else None
        if img is None:
            t = e.find('.//' + NS + 'diffuse/' + NS + 'texture')
            if t is not None:
                sid = t.get('texture'); s2 = e.find(f'.//{NS}newparam[@sid="{sid}"]')
                src = s2.find('.//' + NS + 'source').text if s2 is not None and s2.find('.//' + NS + 'source') is not None else None
                s3 = e.find(f'.//{NS}newparam[@sid="{src}"]') if src else None
                ii = s3.find('.//' + NS + 'init_from').text if s3 is not None else None
                img = imgs.get(ii, ii)
        eff[e.get('id')] = img
    mats = {}
    for m in root.iter(NS + 'material'):
        mats[m.get('id')] = (m.get('name') or m.get('id'), eff.get(m.find(NS + 'instance_effect').get('url')[1:]))
    # instance_material symbol -> material id (apicula binds symbols)
    sym = {}
    for im in root.iter(NS + 'instance_material'):
        sym[im.get('symbol')] = im.get('target')[1:]
    out = []
    for g in root.iter(NS + 'geometry'):
        mesh = g.find(NS + 'mesh')
        src = {}
        for s in mesh.findall(NS + 'source'):
            fa = s.find(NS + 'float_array')
            stride = int(s.find('.//' + NS + 'accessor').get('stride', '1'))
            src[s.get('id')] = np.array([float(v) for v in fa.text.split()]).reshape(-1, stride)
        vin = {}
        vtx = mesh.find(NS + 'vertices')
        for i in vtx.findall(NS + 'input'): vin[i.get('semantic')] = src[i.get('source')[1:]]
        for prim in list(mesh.findall(NS + 'triangles')) + list(mesh.findall(NS + 'polylist')):
            inputs = prim.findall(NS + 'input')
            nin = max(int(i.get('offset')) for i in inputs) + 1
            sem = {}
            for i in inputs:
                s = i.get('semantic'); o = int(i.get('offset'))
                if s == 'VERTEX':
                    for k, v in vin.items(): sem[k] = (v, o)
                elif s not in sem: sem[s] = (src[i.get('source')[1:]], o)
            p = np.array([int(v) for v in prim.find(NS + 'p').text.split()]).reshape(-1, nin)
            vc = [int(v) for v in prim.find(NS + 'vcount').text.split()] if prim.tag == NS + 'polylist' else [3] * (len(p) // 3)
            tris, k = [], 0
            for n in vc:
                for j in range(1, n - 1): tris.append([k, k + j, k + j + 1])
                k += n
            if not tris: continue
            tris = np.array(tris)
            P = sem['POSITION'][0][p[tris, sem['POSITION'][1]]]
            UV = sem['TEXCOORD'][0][p[tris, sem['TEXCOORD'][1]]][..., :2] if 'TEXCOORD' in sem else np.zeros(P.shape[:2] + (2,))
            A = (sem['COLOR'][0][p[tris, sem['COLOR'][1]]][..., 3].mean(1) if 'COLOR' in sem and sem['COLOR'][0].shape[1] > 3
                 else np.ones(len(P)))
            mid = sym.get(prim.get('material'), prim.get('material'))
            name, img = mats.get(mid, (mid, None))
            out.append((name, os.path.join(d, img) if img else None, P, UV, A))
    return out

# ------------------------------------------------------------------------------------------------ building models
def _pack0_records():
    """Retail pack 0: res -> (info dict, bmd bytes)."""
    import b2files
    packs = b2files.narc_entries(b2files.arc_path(FILES, 225))
    _, secs = b2files.gf_container(packs[0]); n = len(secs) // 2
    out = {}
    for i in range(n):
        res, typ, door, dx, dy, dz = struct.unpack_from('<HHHhhh', secs[i], 0)
        out[res] = (dict(door=door, dx=dx, dy=dy, dz=dz), secs[n + i])
    return out

def _retail_dae(res, bmd):
    """Black 2's own pack-0 model res as DAE (apicula, cached)."""
    import b2files
    d = os.path.join(CACHE, f'p0_{res}')
    dae = [os.path.join(d, 'dae', f) for f in (os.listdir(os.path.join(d, 'dae')) if os.path.isdir(os.path.join(d, 'dae')) else [])
           if f.endswith('.dae')]
    if dae: return dae[0]
    os.makedirs(d, exist_ok=True)
    open(os.path.join(d, 'm.nsbmd'), 'wb').write(bmd)
    open(os.path.join(d, 't.nsbtx'), 'wb').write(b2files.building_textures(FILES, 0))
    subprocess.run([APICULA, 'convert', os.path.join(d, 'm.nsbmd'), os.path.join(d, 't.nsbtx'), '-o',
                    os.path.join(d, 'dae'), '-f', 'dae'], capture_output=True)
    dae = [os.path.join(d, 'dae', f) for f in os.listdir(os.path.join(d, 'dae')) if f.endswith('.dae')]
    return dae[0] if dae else None

_MODELS = {}
def registry():
    """res -> dict(dae, door, dx, dz, what) for every pack-0 model the enabled groups give (ours replace retail)."""
    if _MODELS: return _MODELS
    sys.path.insert(0, os.path.join(HERE, 'patches'))
    from area2_buildings import groups
    retail = _pack0_records()
    for res, (info, bmd) in retail.items():
        _MODELS[res] = dict(retail=True, bmd=bmd, door=info['door'], dx=info['dx'], dz=info['dz'], what=f'retail {res}')
    for g in groups():
        for m in json.load(open(os.path.join(ROOT, 'data', 'buildings', f'{g}.json')))['models']:
            path = m['model'][:-5] + 'dae'                 # (HOENN_BUILDINGS_DIR: models built elsewhere)
            if os.environ.get('HOENN_BUILDINGS_DIR'): path = path.replace('work/buildings', os.environ['HOENN_BUILDINGS_DIR'])
            _MODELS[m['res']] = dict(retail=False, dae=os.path.join(ROOT, path), door=m['door'],
                                     dx=m['dx'], dz=m['dz'], what=m.get('what', m['model']), group=g)
    return _MODELS

_PARTS = {}
def model_parts(res):
    if res in _PARTS: return _PARTS[res]
    r = registry().get(res)
    if r is None: _PARTS[res] = []; return []
    path = r['dae'] if not r['retail'] else _retail_dae(res, r['bmd'])
    _PARTS[res] = load_dae(path) if path and os.path.exists(path) else []
    return _PARTS[res]

def placements(wd, cx, cz):
    """[(res, X, Y, Z, rot_degrees)] in world units of one cell's placements.bin."""
    b = open(os.path.join(wd, 'cells', f'{cx:02d}_{cz:02d}', 'placements.bin'), 'rb').read()
    n = struct.unpack_from('<I', b, 0)[0]
    out = []
    for i in range(n):
        x, y, z, rot = struct.unpack_from('<iiiH', b, 4 + 16 * i)
        res = (b[4 + 16 * i + 14] << 8) | b[4 + 16 * i + 15]
        out.append((res, cx * 512 + 256 + x / 4096, y / 4096, cz * 512 + 256 - z / 4096, rot * 360 / 0x10000))
    return out

def placed_parts(res, X, Y, Z, rot, with_door=True):
    """Model parts of a placement in world units (the door model too, at origin + (dx, dz))."""
    c, s = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    R = np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])
    out = [(n, img, P @ R.T + np.array([X, Y, Z]), UV, A, f'res{res}') for n, img, P, UV, A in model_parts(res)]
    r = registry().get(res)
    if with_door and r and r['door'] not in (None, 0xFFFF):
        off = R @ np.array([r['dx'], 0, r['dz']])
        out += [(n, img, P @ R.T + np.array([X, Y, Z]) + off, UV, A, f'door{r["door"]}@res{res}')
                for n, img, P, UV, A in model_parts(r['door'])]
    return out

# ------------------------------------------------------------------------------------------------------- the world
def world_cells(wd):
    return [(c['cx'], c['cz']) for c in json.load(open(os.path.join(wd, 'world.json')))['cells']]

def cell_terrain(wd, cx, cz):
    out = []
    for n, img, P, UV, A in load_dae(os.path.join(wd, 'cells', f'{cx:02d}_{cz:02d}', 'terrain.dae')):
        out.append((n, img, P + np.array([cx * 512 + 256, 0, cz * 512 + 256]), UV, A, f'cell{cx}_{cz}'))
    return out

def all_parts(wd, cells=None):
    """Terrain of every cell + every placed building (world units)."""
    cells = cells or world_cells(wd)
    parts = []
    for cx, cz in cells:
        parts += cell_terrain(wd, cx, cz)
        for res, X, Y, Z, rot in placements(wd, cx, cz):
            parts += placed_parts(res, X, Y, Z, rot)
    return parts

def flatten(parts):
    """Arrays over all triangles: P (N,3,3), UV (N,3,2), material index, source index, names."""
    mats, srcs, Ps, UVs, Mi, Si, As = [], [], [], [], [], [], []
    for n, img, P, UV, A, src in parts:
        if n not in mats: mats.append(n)
        if src not in srcs: srcs.append(src)
        Ps.append(P); UVs.append(UV); As.append(A)
        Mi.append(np.full(len(P), mats.index(n))); Si.append(np.full(len(P), srcs.index(src)))
    return (np.concatenate(Ps), np.concatenate(UVs), np.concatenate(Mi), np.concatenate(Si), np.concatenate(As),
            mats, srcs)

# ----------------------------------------------------------------------------------------------------- layers check
AXES = {1: (0, 2), 2: (0, 1), 0: (2, 1)}         # value axis -> the two projection axes

def _raster(P2, step, off, eps=1e-6):
    """Sample points (strictly inside) of 2D triangles P2 (N,3,2): yields (tri, ia, ib, w0, w1, w2)."""
    for t in range(len(P2)):
        (ax, ay), (bx, by), (cx, cy) = P2[t]
        lo_a, hi_a = min(ax, bx, cx), max(ax, bx, cx); lo_b, hi_b = min(ay, by, cy), max(ay, by, cy)
        i0, i1 = math.ceil((lo_a - off[0]) / step), math.floor((hi_a - off[0]) / step)
        j0, j1 = math.ceil((lo_b - off[1]) / step), math.floor((hi_b - off[1]) / step)
        if i1 < i0 or j1 < j0: continue
        ii, jj = np.meshgrid(np.arange(i0, i1 + 1), np.arange(j0, j1 + 1))
        xs, ys = ii * step + off[0], jj * step + off[1]
        den = (by - cy) * (ax - cx) + (cx - bx) * (ay - cy)
        if abs(den) < 1e-9: continue
        w0 = ((by - cy) * (xs - cx) + (cx - bx) * (ys - cy)) / den
        w1 = ((cy - ay) * (xs - cx) + (ax - cx) * (ys - cy)) / den
        w2 = 1 - w0 - w1
        m = (w0 > eps) & (w1 > eps) & (w2 > eps)
        if m.any(): yield t, ii[m], jj[m], w0[m], w1[m], w2[m]

_REACH = {}
def reachable(wd):
    """World tiles within 10 tiles of a walkable tile (chunk.json collision marks): where the game camera can look."""
    if wd in _REACH: return _REACH[wd]
    walk = set()
    for cx, cz in world_cells(wd):
        grid = json.load(open(os.path.join(wd, 'cells', f'{cx:02d}_{cz:02d}', 'chunk.json')))['collision']
        for tz, row in enumerate(grid):
            for tx, ch in enumerate(row):
                if ch != '#': walk.add((cx * 32 + tx, cz * 32 + tz))
    near = {((x + dx) // 8, (z + dz) // 8) for x, z in walk for dx in (-10, 0, 10) for dz in (-10, 0, 10)}
    _REACH[wd] = lambda tx, tz: (tx // 8, tz // 8) in near
    return _REACH[wd]

def layer_pairs(parts, found, step=2.0, span=None, limit=None):
    """Add the close same-facing pairs among `parts` (world units) to `found`; span = (x0, z0, x1, z1) keeps only
    samples inside it (a cell's own area)."""
    if not parts: return found
    P, UV, Mi, Si, A, mats, srcs = flatten(parts)
    N = np.cross(P[:, 1] - P[:, 0], P[:, 2] - P[:, 0])
    L = np.linalg.norm(N, axis=1); ok = L > 1e-6
    N[ok] /= L[ok][:, None]
    dom = np.argmax(np.abs(N), axis=1)
    for ax in (0, 1, 2):
        sel = np.nonzero(ok & (dom == ax))[0]
        if not len(sel): continue
        a, b = AXES[ax]
        off = {1: (0.7, 1.3), 2: (0.7, 1.1), 0: (1.3, 1.1)}[ax]
        P2 = P[sel][:, :, [a, b]]
        rows = []
        for t, ii, jj, w0, w1, w2 in _raster(P2, step, off):
            T = sel[t]
            xs = ii * step + off[0]; ys = jj * step + off[1]
            if span:
                x0, z0, x1, z1 = span
                if ax == 1: keep = (xs >= x0) & (xs < x1) & (ys >= z0) & (ys < z1)
                elif ax == 2: keep = (xs >= x0) & (xs < x1)
                else: keep = (xs >= z0) & (xs < z1)
            else: keep = np.ones(len(xs), bool)
            if not keep.any(): continue
            val = w0 * P[T, 0, ax] + w1 * P[T, 1, ax] + w2 * P[T, 2, ax]
            u = w0 * UV[T, 0, 0] + w1 * UV[T, 1, 0] + w2 * UV[T, 2, 0]
            v = w0 * UV[T, 0, 1] + w1 * UV[T, 1, 1] + w2 * UV[T, 2, 1]
            k = keep
            rows.append(np.stack([ii[k].astype(float), jj[k].astype(float), val[k], np.full(k.sum(), T, float), u[k], v[k]], 1))
        if not rows: continue
        R = np.concatenate(rows)
        key = R[:, 0] * 1e6 + R[:, 1]
        order = np.lexsort((R[:, 2], key))
        R, key = R[order], key[order]
        same = key[1:] == key[:-1]
        ta, tb = R[:-1, 3].astype(int), R[1:, 3].astype(int)
        gap = (R[1:, 2] - R[:-1, 2]) * np.minimum(np.abs(N[ta, ax]), np.abs(N[tb, ax]))
        facing = (N[ta] * N[tb]).sum(1) > 0.98
        hit = same & facing & (gap < (limit or MIN_GAP) - 0.01) & (ta != tb)
        for i in np.nonzero(hit)[0]:
            A_, B_ = ta[i], tb[i]
            dup = (Mi[A_] == Mi[B_] and gap[i] < 0.05 and abs((R[i, 4] - R[i + 1, 4] + 0.5) % 1 - 0.5) < 0.02
                   and abs((R[i, 5] - R[i + 1, 5] + 0.5) % 1 - 0.5) < 0.02)
            ma, mb = sorted([mats[Mi[A_]], mats[Mi[B_]]])
            sa, sb = srcs[Si[A_]], srcs[Si[B_]]
            kind = ('copy' if dup else 'layer') + (':bld' if (sa.startswith(('res', 'door')) or sb.startswith(('res', 'door'))) else '')
            f = found.setdefault((ma, mb, kind), [0, 99.0, [], set()])
            f[0] += 1; f[1] = min(f[1], gap[i])
            pos = [0, 0, 0]; pos[a] = R[i, 0] * step + off[0]; pos[b] = R[i, 1] * step + off[1]; pos[ax] = R[i, 2]
            if len(f[2]) < 400: f[2].append(tuple(round(p, 1) for p in pos))
            f[3].update({sa, sb})
    return found

def layers(wd, cells=None, step=2.0, verbose=True):
    """Pairs of same-facing surfaces closer than MIN_GAP: {(mat_a, mat_b, kind): [count, gap, [(x, y, z), ...], srcs]}."""
    cells = cells or world_cells(wd)
    found = {}
    bpl = {c: placements(wd, *c) for c in world_cells(wd)}
    for ci, (cx, cz) in enumerate(cells):
        x0, z0 = cx * 512, cz * 512
        parts = cell_terrain(wd, cx, cz)
        for c2, pl in bpl.items():        # buildings of this and the neighbouring cells reach in
            if abs(c2[0] - cx) > 1 or abs(c2[1] - cz) > 1: continue
            for res, X, Y, Z, rot in pl:
                if x0 - 200 < X < x0 + 712 and z0 - 200 < Z < z0 + 712: parts += placed_parts(res, X, Y, Z, rot)
        layer_pairs(parts, found, step, (x0, z0, x0 + 512, z0 + 512))
        if verbose and ci % 25 == 0: print(f'  layers: {ci + 1}/{len(cells)} cells', file=sys.stderr)
    # keep only what the camera can see (near walkable tiles): the outer ring of forest and sea is never in view
    near = reachable(wd)
    for key in list(found):
        f = found[key]
        f[2] = [p for p in f[2] if near(int(p[0]) // 16, int(p[2]) // 16)]
        if not f[2]: del found[key]
    return found

def report_layers(found):
    out = []
    for (ma, mb, kind), (n, gap, pos, srcs) in sorted(found.items(), key=lambda kv: -kv[1][0]):
        tiles = sorted({(int(p[0]) // 16, int(p[2]) // 16) for p in pos})
        out.append(f'{n:7d} samples  {kind:10s} {ma} / {mb}  min gap {gap:.2f}  tiles {len(tiles)}: {tiles[:8]}'
                   + (f'  [{", ".join(sorted(srcs)[:4])}]' if 'bld' in kind else ''))
    return '\n'.join(out)

# ------------------------------------------------------------------------------------------------------ holes check
CAM_PITCH = 40.0              # degrees above the horizon, looking north (notes/GEN5_TERRAIN.md)

def _view(P, pitch=CAM_PITCH):
    """Orthographic camera-angle projection: (screen x, screen y down, depth) of world points."""
    p = math.radians(pitch)
    x = P[..., 0]
    sy = -P[..., 1] * math.cos(p) + P[..., 2] * math.sin(p)       # down the screen
    dep = -P[..., 1] * math.sin(p) - P[..., 2] * math.cos(p)      # larger = further (north / lower)
    return x, sy, dep

def holes(wd, step=2.0, cells=None):
    """Top-down: sample points of every cell (2-unit grid) that no opaque upward-facing surface covers. The game
    clears to black, so such a spot shows black (or black through a translucent layer such as the sea's upper
    sheet, sea_mizu1_1, or a pond's ike01). Returns [(cell, count, [(tile, top translucent material or None)])]."""
    res = []
    for cx, cz in (cells or world_cells(wd)):
        parts = cell_terrain(wd, cx, cz)
        X0, Z0 = cx * 512, cz * 512
        n = int(512 / step)
        opaque = np.zeros((n, n), bool); tl = np.full((n, n), -1)
        P, UV, Mi, Si, A, mats, srcs = flatten(parts)
        N = np.cross(P[:, 1] - P[:, 0], P[:, 2] - P[:, 0])
        up = np.nonzero(N[:, 1] > 1e-6)[0]
        P2 = P[up][:, :, [0, 2]]
        for t, ii, jj, w0, w1, w2 in _raster(P2, step, (X0 % step + step / 2, Z0 % step + step / 2), eps=-1e-4):
            T = up[t]
            ii = ii - int(X0 / step); jj = jj - int(Z0 / step)
            k = (ii >= 0) & (ii < n) & (jj >= 0) & (jj < n)
            if A[T] >= 0.99: opaque[jj[k], ii[k]] = True
            else: tl[jj[k], ii[k]] = Mi[T]
        bad = np.argwhere(~opaque)
        if len(bad):
            tiles = {}
            for j, i in bad:
                tiles.setdefault(((X0 + i * step) // 16, (Z0 + j * step) // 16), mats[tl[j, i]] if tl[j, i] >= 0 else None)
            res.append(((cx, cz), len(bad), sorted(tiles.items())))
    return res

# ----------------------------------------------------------------------------------------------------- render a map
_TEX = {}
def _tex(path):
    if path not in _TEX:
        from PIL import Image
        _TEX[path] = np.asarray(Image.open(path).convert('RGBA')).astype(np.float32) if path and os.path.exists(path) else None
    return _TEX[path]

def render(parts, box, scale=1.0, pitch=CAM_PITCH, bg=(255, 0, 255), want_depth=False):
    """Orthographic camera-angle render of world box (x0, z0, x1, z1) at `scale` pixels per unit (textured, alpha
    test, back faces culled). Magenta = nothing drawn."""
    from PIL import Image
    x0, z0, x1, z1 = box
    p = math.radians(pitch)
    Y0, Y1 = z0 * math.sin(p) - 120 * math.cos(p), z1 * math.sin(p) + 40 * math.cos(p)
    W, H = int((x1 - x0) * scale), int((Y1 - Y0) * scale)
    img = np.zeros((H, W, 3), np.float32); img[:] = bg
    zb = np.full((H, W), np.inf)
    # opaque first, then translucent (the game draws translucent polygons after the opaque ones)
    parts = [q for q in parts if (q[4] >= 0.99).all()] + [q for q in parts if not (q[4] >= 0.99).all()]
    for n, tp, P, UV, A, src in parts:
        T = _tex(tp)
        xs, ys, dep = _view(P, pitch)
        N = np.cross(P[:, 1] - P[:, 0], P[:, 2] - P[:, 0])
        towards = N[:, 1] * math.sin(p) + N[:, 2] * math.cos(p) > 1e-6
        light = np.clip(0.55 + 0.45 * (N[:, 1] / np.maximum(np.linalg.norm(N, axis=1), 1e-9)), 0.55, 1.0)
        for t in np.nonzero(towards)[0]:
            sx, sy = (xs[t] - x0) * scale, (ys[t] - Y0) * scale
            i0, i1 = max(0, math.floor(sx.min())), min(W - 1, math.ceil(sx.max()))
            j0, j1 = max(0, math.floor(sy.min())), min(H - 1, math.ceil(sy.max()))
            if i1 < i0 or j1 < j0: continue
            ii, jj = np.meshgrid(np.arange(i0, i1 + 1) + 0.5, np.arange(j0, j1 + 1) + 0.5)
            (ax, bx, cx), (ay, by, cy) = sx, sy
            den = (by - cy) * (ax - cx) + (cx - bx) * (ay - cy)
            if abs(den) < 1e-9: continue
            w0 = ((by - cy) * (ii - cx) + (cx - bx) * (jj - cy)) / den
            w1 = ((cy - ay) * (ii - cx) + (ax - cx) * (jj - cy)) / den
            w2 = 1 - w0 - w1
            m = (w0 >= -1e-4) & (w1 >= -1e-4) & (w2 >= -1e-4)
            if not m.any(): continue
            d = w0 * dep[t, 0] + w1 * dep[t, 1] + w2 * dep[t, 2]
            sub = zb[j0:j1 + 1, i0:i1 + 1]
            m &= d < sub
            if not m.any(): continue
            u = w0 * UV[t, 0, 0] + w1 * UV[t, 1, 0] + w2 * UV[t, 2, 0]
            v = w0 * UV[t, 0, 1] + w1 * UV[t, 1, 1] + w2 * UV[t, 2, 1]
            if T is not None:
                th, tw = T.shape[:2]
                s = T[np.floor((1 - v) * th).astype(int) % th, np.floor(u * tw).astype(int) % tw]
                m &= s[..., 3] > 100
                rgb = s[..., :3] * light[t]
                if A[t] < 0.99:            # translucent material: blend over what is there
                    reg = img[j0:j1 + 1, i0:i1 + 1]
                    rgb = A[t] * rgb + (1 - A[t]) * reg
            else:
                rgb = np.zeros(m.shape + (3,)); rgb[:] = (128, 128, 128)
            reg = img[j0:j1 + 1, i0:i1 + 1]
            reg[m] = rgb[m]
            if A[t] >= 0.99: sub[m] = d[m]
    im = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))
    if want_depth: return im, zb, Y0
    return im

def map_box(name):
    """World-unit box of a map (world.py's composition: layout + margin + pad/shift)."""
    cfg = json.load(open(os.path.join(ROOT, 'data', 'hoenn_world.json')))
    lay = json.load(open(os.path.join(ROOT, 'data', 'hoenn_world_layout.json')))['main']['maps']
    plan = json.load(open(os.path.join(ROOT, 'data', 'plans', f'{name}.json')))
    M = cfg['margin_cells'] * 32
    pad = cfg.get('pad_north', {}).get(name, 0); sx, sz = cfg.get('shift', {}).get(name, [0, 0])
    ox, oz = lay[name]['tile_x'] + M + sx, lay[name]['tile_z'] + M + sz + pad
    W, H = plan['size']
    return ox, oz - pad, ox + W, oz + H       # tiles

def render_map(name, out, wd, margin=2, scale=1.0):
    tx0, tz0, tx1, tz1 = map_box(name)
    tx0 -= margin; tz0 -= margin; tx1 += margin; tz1 += margin
    cells = {(cx, cz) for cx in range(tx0 // 32, (tx1 - 1) // 32 + 1) for cz in range(tz0 // 32, (tz1 + 3) // 32 + 1)}
    cells &= set(world_cells(wd))
    parts = all_parts(wd, sorted(cells))
    img = render(parts, (tx0 * 16, tz0 * 16, tx1 * 16, tz1 * 16), scale)
    img.save(out)
    return out

# -------------------------------------------------------------------------------------------------- buildings check
def buildings(wd):
    """Every placement: the ground height under its model's footprint (terrain triangles) vs the placement y, and for
    models with a door record, where the door model's centre lands vs the nearest door warp tile."""
    import world as W_
    world = json.load(open(os.path.join(wd, 'world.json')))
    doors = []
    for z in world['zones'].values():
        for d in z.get('doors', []): doors.append(((d['x'] - 8) // 16, (d['z'] - 8) // 16, d['map']))
        for w in z['warps'].values(): doors.append(((w[0] - 8) // 16, (w[2] - 8) // 16, 'slot'))
    out = []
    for cx, cz in world_cells(wd):
        for res, X, Y, Z, rot in placements(wd, cx, cz):
            r = registry().get(res)
            if not r or r['door'] in (None, 0xFFFF): continue
            dparts = model_parts(r['door'])
            if not dparts: continue
            P = np.concatenate([p[2] for p in dparts]).reshape(-1, 3)
            dcx = (P[:, 0].min() + P[:, 0].max()) / 2
            door_x = X + r['dx'] + dcx; door_z = Z + r['dz']
            tile = (math.floor(door_x / 16), math.floor(door_z / 16))
            near = min(doors, key=lambda d: abs(d[0] * 16 + 8 - door_x) + abs(d[1] * 16 + 8 - door_z)) if doors else None
            off = (door_x - (near[0] * 16 + 8)) if near else None
            out.append(dict(res=res, what=r['what'], at=(round(X / 16, 2), round(Z / 16, 2)), y=Y, door=r['door'],
                            door_centre_x=round(door_x, 1), door_tile=near, dx_off=round(off, 1) if off is not None else None))
    return out

def probe(wd, tx, tz, r=0):
    """Triangles (terrain + buildings) over world tile (tx, tz) (+- r tiles): material, source, y range, normal."""
    cx, cz = tx // 32, tz // 32
    parts = cell_terrain(wd, cx, cz)
    for c2 in world_cells(wd):
        if abs(c2[0] - cx) <= 1 and abs(c2[1] - cz) <= 1:
            for res, X, Y, Z, rot in placements(wd, *c2): parts += placed_parts(res, X, Y, Z, rot)
    x0, x1, z0, z1 = (tx - r) * 16, (tx + r + 1) * 16, (tz - r) * 16, (tz + r + 1) * 16
    out = []
    for n, img, P, UV, A, src in parts:
        for t in range(len(P)):
            xs, zs = P[t, :, 0], P[t, :, 2]
            if xs.max() <= x0 or xs.min() >= x1 or zs.max() <= z0 or zs.min() >= z1: continue
            N = np.cross(P[t, 1] - P[t, 0], P[t, 2] - P[t, 0]); N = N / max(np.linalg.norm(N), 1e-9)
            out.append((n, src, round(float(P[t, :, 1].min()), 2), round(float(P[t, :, 1].max()), 2), tuple(np.round(N, 2)),
                        [tuple(np.round(v, 1)) for v in P[t]]))
    return out

def view_holes(wd, scale=0.5, cells=None):
    """Camera-angle holes: per cell, an orthographic view along the game camera's direction (with the 3x4 cells
    around it); pixels over the cell's ground where no opaque front face is hit show the clear colour (black) in the
    game, alone or through translucent water. Returns [(cell, pixels, [world tiles at y 0 under them])]."""
    allc = set(world_cells(wd))
    out = []
    p = math.radians(CAM_PITCH)
    # only where the camera can be: within 10 tiles of a walkable tile (the collision grids' walkable marks)
    near_walk = set()
    for cx, cz in allc:
        grid = json.load(open(os.path.join(wd, 'cells', f'{cx:02d}_{cz:02d}', 'chunk.json')))['collision']
        for tz, row in enumerate(grid):
            for tx, ch in enumerate(row):
                if ch != '#': near_walk.add((cx * 32 + tx, cz * 32 + tz))
    near10 = {((x + dx) // 10 * 10, (z + dz) // 10 * 10) for x, z in near_walk for dx in (-10, 0, 10) for dz in (-10, 0, 10)}
    for cx, cz in (cells or sorted(allc)):
        near = sorted(c for c in allc if abs(c[0] - cx) <= 1 and -2 <= c[1] - cz <= 1)
        if len(near) < 9: continue                 # the world's outer ring: nothing beyond it by design
        parts = all_parts(wd, near)
        x0, z0 = cx * 512, cz * 512
        im, zb, Y0 = render(parts, (x0, z0, x0 + 512, z0 + 512), scale, want_depth=True)
        H, W = zb.shape
        jj, ii = np.nonzero(~np.isfinite(zb))
        sy = jj / scale + Y0                       # screen y in world units; ground point at y 0: z = sy / sin
        zg = sy / math.sin(p); xg = ii / scale + x0
        k = (zg >= z0 + 16) & (zg < z0 + 496) & (xg >= x0 + 16) & (xg < x0 + 496)
        k &= np.array([(int(a) // 16 // 10 * 10, int(b) // 16 // 10 * 10) in near10 for a, b in zip(xg, zg)], bool) if len(xg) else k
        if k.any():
            tiles = sorted({(int(a) // 16, int(b) // 16) for a, b in zip(xg[k], zg[k])})
            out.append(((cx, cz), int(k.sum()), tiles))
    return out

def render_tiles(wd, tx0, tz0, tx1, tz1, out, scale=2.0, pitch=CAM_PITCH, hide=()):
    """Camera-angle render of world tiles tx0..tx1, tz0..tz1 (exclusive ends) with everything in the cells around."""
    cells = {(cx, cz) for cx in range((tx0 - 4) // 32, (tx1 + 4) // 32 + 1) for cz in range((tz0 - 4) // 32, (tz1 + 8) // 32 + 1)}
    cells &= set(world_cells(wd))
    parts = [p for p in all_parts(wd, sorted(cells)) if p[0] not in hide]
    render(parts, (tx0 * 16, tz0 * 16, tx1 * 16, tz1 * 16), scale, pitch).save(out)
    return out

if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'layers':
        f = layers(world_dir(sys.argv[2] if len(sys.argv) > 2 else None))
        print(report_layers(f))
    elif cmd == 'holes':
        for c, n, tiles in holes(world_dir(sys.argv[2] if len(sys.argv) > 2 else None)):
            print(f'cell {c}: {n} uncovered samples, {len(tiles)} tiles: {tiles[:10]}{" ..." if len(tiles) > 10 else ""}')
    elif cmd == 'render':
        print(render_map(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else f'{sys.argv[2]}.png',
                         world_dir(sys.argv[4] if len(sys.argv) > 4 else None)))
    elif cmd == 'view':      # view TX0 TZ0 TX1 TZ1 OUT.png [SCALE] [PITCH]
        a = sys.argv[2:]
        print(render_tiles(world_dir(), *map(int, a[:4]), a[4], float(a[5]) if len(a) > 5 else 2.0,
                           float(a[6]) if len(a) > 6 else CAM_PITCH))
    elif cmd == 'viewholes':
        for c, n, tiles in view_holes(world_dir()):
            print(f'cell {c}: {n} pixels, {len(tiles)} tiles (at y 0): {tiles[:12]}{" ..." if len(tiles) > 12 else ""}')
    elif cmd == 'probe':
        for row in probe(world_dir(), int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]) if len(sys.argv) > 4 else 0):
            print(*row)
    elif cmd == 'buildings':
        for b in buildings(world_dir(sys.argv[2] if len(sys.argv) > 2 else None)):
            print(b)
