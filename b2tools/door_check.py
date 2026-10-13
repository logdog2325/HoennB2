"""Door fit check (door_fix, 2026-10-11): does each building's animated door sit in its wall, under the eave, the way
Black 2's own houses hold theirs? (User: "on too many houses the door is positioned kind of in the roof".)

    python3 door_check.py models [--json OUT]        every pack-0 / warp-only-map model of ours with a door record
    python3 door_check.py world [WORLD] [--json OUT] every placed door of a built world (a building's door record, and
                                                     doors placed by themselves), our models within 6 tiles as occluders
    python3 door_check.py b2 [--json OUT]            Black 2's own buildings (all 70 exterior packs): the reference
    python3 door_check.py render RES OUT.png         camera-angle picture of one model + its door (ours)

Models: HOENN_BUILDINGS_DIR / HOENN_STANDALONE_BUILDINGS (an agent's own builds), else work/buildings. WORLD defaults
to $HOENN_WORLD_DIR or work/world.

The game draws the door model (pack res `door`) at the building's position + (dx, dy, dz), not turned with the building
(field_buildmodel.c FieldPropSystem_InstantiateProps; our records keep dy 0). Black 2's door models: door_n_01-03
(259-261) and door_t1_01 (164) are a plate 18 wide, y 6..32, its face 2 units in front of the door origin; door_t1_02
(165, 236) y 4..33; door_pc (93, the Center's curved sliding door) y 2.9..29.8, an arc 26.4 wide bulging 13.8 forward;
r34_door1 (101) y 3..30. Seen from the field camera's eye (185.7 up and 142 south of the player standing on the tile in
front of the door; notes/NPC_LIMIT.md), per door, sampled every unit over its front face:

  clear   the underside of whatever is over the door (lintel, eave, skirt roof, awning, roof slope): upward rays from
          above the door's step, from 2 units behind its face to 6 in front. Finding when < door top + 2: a roof or an
          eave comes down through the door ("in the roof"). Black 2's house doors: median top + 7, 25th pct top + 4
  wall    over the door's top, what the camera sees: points of the door's plane 1-6 units above its top, the first
          surface the eye's ray meets there; per column across the door one must lie within 8 units of the door's plane
          (the wall the door is set in, its frame in front of it, or a canopy over it). Else the door's top stands
          against a roof (or a wall) far behind it on screen. Finding when < 90 % of the columns (Black 2: 86 % of its
          buildings with a door pass; the rest are vestibules and towers)
  hidden  share of the door face the eye cannot see for a south-facing building surface within 40 units of the door
          along the view (eaves, awnings, porch roofs; not a sign or a building a few tiles south). Finding when > 15 %
          (Black 2's house doors: median 12 %, 75th pct 15 %: their awnings and porch roofs)
  inset   the first surface behind the door's face at mid height: < 1 unit depth-fights in melonDS (finding); a wall
          in front of the face (the door sunk in) is reported negative

Exit status 1 when a finding is left (models / world)."""
import os, sys, json, math, struct, argparse
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, 'patches'))
import exterior_check as ec

EYE_UP, EYE_BACK = 185.7, 142.0   # the field camera's eye over/south of the player (RAM, Slateport: notes/NPC_LIMIT.md)
PLAYER_Z = 18.0            # the player in front of the door: the approach tile's centre, ~18 units south of the door face
CAM = np.array([0.0, math.sin(math.radians(45)), math.cos(math.radians(45))])   # (about the direction to the eye)
CLEAR_MIN, WALL_MIN, HIDDEN_MAX, INSET_MIN = 2.0, 0.9, 0.15, 1.0
DOOR_TOPS = {259: 32, 260: 32, 261: 32, 164: 32, 165: 33, 236: 33, 93: 29.8, 101: 30.1}   # (buildings.DOOR_TOP)
# by design (world mode): (frame, door tile) -> why
ACCEPTED = {('main', (79, 208)): "Rustboro House 2's door looks out over the Trainer's School's walk-behind roof row: "
                                 "the school's back edge hides the door's foot from the camera (Sapphire draws the "
                                 "player behind that roof on the same tile)"}
OCCLUDER_REACH = 40.0      # occluders this far along the view from the door face (eaves, awnings, porches: Black 2's
                           # stand 2-12 units out; a sign or a lamp a tile or two south is no part of the door's fit)
LINTEL_REACH = 8.0         # ray length from the door plane to the wall above it (a wall 2-4 units behind the face: 3-5)
SKIP_TEX = ('h_kage',)     # the translucent ground shadow is no wall or roof

def tris_of(parts, skip_tex=SKIP_TEX):
    """(N,3,3) triangles of parts [(name, img, P, ...)] without the shadow."""
    keep = [p[2] for p in parts if not (p[1] and os.path.basename(p[1]).split('.')[0] in skip_tex)
            and not any(s in (p[0] or '') for s in skip_tex)]
    return np.concatenate(keep) if keep else np.zeros((0, 3, 3))

def ray_hits(O, D, T, eps=1e-7):
    """Moller-Trumbore: for rays O (R,3) + t*D (R,3) against triangles T (N,3,3): t (R,N), inf where no hit (t > 0)."""
    if not len(T) or not len(O): return np.full((len(O), len(T)), np.inf)
    v0, e1, e2 = T[:, 0], T[:, 1] - T[:, 0], T[:, 2] - T[:, 0]
    out = np.full((len(O), len(T)), np.inf)
    for i in range(0, len(O), 256):
        o, d = O[i:i + 256, None, :], D[i:i + 256, None, :]
        p = np.cross(d, e2[None]); det = (e1[None] * p).sum(-1)
        ok = np.abs(det) > eps
        inv = np.where(ok, 1 / np.where(ok, det, 1), 0)
        s = o - v0[None]
        u = (s * p).sum(-1) * inv
        q = np.cross(s, e1[None])
        v = (d * q).sum(-1) * inv
        t = (e2[None] * q).sum(-1) * inv
        hit = ok & (u >= -1e-6) & (v >= -1e-6) & (u + v <= 1 + 1e-6) & (t > 1e-4)
        out[i:i + 256] = np.where(hit, t, np.inf)
    return out

def normals(T):
    N = np.cross(T[:, 1] - T[:, 0], T[:, 2] - T[:, 0]); L = np.linalg.norm(N, axis=1)
    return N / np.maximum(L, 1e-9)[:, None]

def door_face(D):
    """The door's front face: triangles facing south (n_z > 0.5) -> (x0, x1, y0, y1, z of the face per x sample)."""
    N = normals(D)
    F = D[N[:, 2] > 0.5]
    if not len(F): F = D
    Q = F.reshape(-1, 3)
    return Q[:, 0].min(), Q[:, 0].max(), Q[:, 1].min(), Q[:, 1].max(), F

def measure(B, D):
    """Door fit of door triangles D in front of building triangles B (same frame: model space, +z south)."""
    x0, x1, y0, y1, F = door_face(D)
    top = float(D.reshape(-1, 3)[:, 1].max())
    NB = normals(B)
    xs = np.arange(math.ceil(x0 + 1), math.floor(x1 - 1) + 1, 1.0)
    ys = np.arange(math.ceil(y0 + 1), math.floor(y1) + 1, 1.0)
    # the face's z at each x (curved Center doors: a ray down through the face)
    zf = {}
    for x in xs:
        t = ray_hits(np.array([[x, (y0 + y1) / 2, 999.0]]), np.array([[0, 0, -1.0]]), F)[0]
        zf[x] = 999.0 - t.min() if np.isfinite(t.min()) else float(F.reshape(-1, 3)[:, 2].max())
    # clear: the underside of whatever is over the door (lintel, eave, skirt roof, awning, roof slope): upward rays from
    # just above the door's step, across the door, from 2 units behind its face (between door and wall) to 6 in front
    O = np.array([[x, y0 + 2, zf[x] + dz] for x in xs for dz in np.arange(-2, 6.01, 1.0)])
    t = ray_hits(O, np.tile([0, 1.0, 0], (len(O), 1)), B)
    tmin = t.min(1)
    under = O[:, 1] + tmin
    clear = float(under.min()) if np.isfinite(under).any() else 999.0
    clear_at = O[int(np.argmin(under))] if np.isfinite(under).any() else None
    # wall (what the camera sees over the door's top): for points of the door's plane 1 to 6 units above the door, the
    # surface the camera sees there (first front face coming from the camera). In each column across the door, one of
    # them must lie within LINTEL_REACH of the door's plane along the view: the wall the door is set in (behind a door
    # standing out of it, or in front of a door set back in a frame), or a canopy/beam right over the door, as Black 2
    # has all three. Else the door's top stands against a roof (or wall) far behind it on screen: "the door is in the
    # roof".
    # wall = share of the columns that have it
    eye = np.array([(x0 + x1) / 2, EYE_UP, float(np.median(list(zf.values()))) + PLAYER_Z + EYE_BACK])
    Oy = np.arange(math.floor(top) + 1, math.floor(top) + 7, 1.0)
    P = np.array([[x, y, zf[x] + 0.05] for x in xs for y in Oy])
    Dv = P - eye; L = np.linalg.norm(Dv, axis=1); Dv /= L[:, None]
    tw = ray_hits(np.tile(eye, (len(P), 1)), Dv, B)
    tw[(NB @ -Dv.T).T <= 1e-3] = np.inf                  # back faces: culled by the game
    fw = tw.argmin(1); twm = tw[np.arange(len(P)), fw]
    ok = np.isfinite(twm) & (np.abs(twm - L) <= LINTEL_REACH)
    col = ok.reshape(len(xs), len(Oy)).any(1)
    wall = float(col.mean()) if len(col) else 0.0
    wall_bad_y = [float(x) for x in xs[~col]][:1] or None
    # inset: the first surface behind the face at mid height (closer than 1: depth-fights in melonDS); sunk: a south-
    # facing surface just in front of the face (the door is inside the wall)
    mid = (y0 + y1) / 2
    Om = np.array([[x, mid, zf[x] - 0.05] for x in xs])
    tm = ray_hits(Om, np.tile([0, 0, -1.0], (len(Om), 1)), B).min(1)
    inset = float(np.median(tm[np.isfinite(tm)])) if np.isfinite(tm).any() else None
    ts = ray_hits(Om, np.tile([0, 0, 1.0], (len(Om), 1)), B)
    fs = ts.argmin(1); tsm = ts[np.arange(len(Om)), fs]
    sunk = np.isfinite(tsm) & (tsm < 3) & (NB[fs, 2] < -0.5)       # (seen from inside: a wall's back)
    if sunk.mean() > 0.5: inset = -float(np.median(tsm[sunk]))
    # hidden from the camera: a building face turned to the camera between the door face and the camera
    Oc = np.array([[x, y, zf[x] + 0.05] for x in xs for y in ys])
    Dc = eye - Oc; Lc = np.linalg.norm(Dc, axis=1); Dc /= Lc[:, None]
    tc = ray_hits(Oc, Dc, B)
    tc[(NB @ Dc.T).T <= 1e-3] = np.inf                   # back faces (culled), and nothing beyond the eye or
    tc[tc > np.minimum(Lc, OCCLUDER_REACH)[:, None]] = np.inf   # further out than the door's own eaves and porch
    hid = np.isfinite(tc.min(1)) if tc.size else np.zeros(len(Oc), bool)
    hidden = float(hid.mean()) if len(hid) else 0.0
    hid_y = float(Oc[hid][:, 1].min()) if hid.any() else None
    return dict(top=round(top, 1), clear=round(clear, 1), clear_at=None if clear_at is None else [round(float(v), 1) for v in clear_at],
                wall=round(wall, 2), wall_bad_from_y=wall_bad_y, hidden=round(hidden, 3), hidden_from_y=hid_y, inset=None if inset is None else round(inset, 1),
                x=(round(float(x0), 1), round(float(x1), 1)), face_z=round(float(np.median(list(zf.values()))), 1))

def problems(m):
    out = []
    if m["clear"] < m["top"] + CLEAR_MIN:
        out.append(f"door top {m['top']} reaches the eave/roof/wall top over it at y {m['clear']} (at {m['clear_at']})")
    if m["wall"] < WALL_MIN: out.append(f"door top {m['top']} stands against the roof on screen (wall over the door: {m['wall'] * 100:.0f}%, first column without one x {m['wall_bad_from_y']})")
    if m['hidden'] > HIDDEN_MAX: out.append(f"{m['hidden'] * 100:.0f}% of the door hidden from the camera (from y {m['hidden_from_y']})")
    if m['inset'] is not None and m['inset'] < INSET_MIN: out.append(f"door face {m['inset']} from the wall behind (sunk in / depth-fights)")
    return out

# ------------------------------------------------------------------------------------------------------- our models
def door_tris(door_res, dx, dz, parts_of=ec.model_parts):
    D = tris_of(parts_of(door_res))
    return D + np.array([dx, 0, dz]) if len(D) else D

def our_models():
    """[(res, record)] with a door: pack 0 (enabled groups) and the standalone pack."""
    reg = dict(ec.registry())
    p = os.path.join(ROOT, 'data', 'buildings', 'standalone.json')
    alt = os.environ.get('HOENN_BUILDINGS_DIR')
    for m in json.load(open(p))['models']:
        path = m['model'][:-5] + 'dae'
        if alt: path = path.replace('work/buildings', alt)
        reg.setdefault(m['res'], dict(retail=False, dae=os.path.join(ROOT, path), door=m['door'], dx=m['dx'], dz=m['dz'],
                                      what=m.get('what', m['model']), group='standalone'))
    return [(res, r) for res, r in sorted(reg.items()) if not r['retail'] and r['door'] not in (None, 0xFFFF)]

def model_report():
    rows = []
    for res, r in our_models():
        if not os.path.exists(r['dae']): rows.append(dict(res=res, what=r['what'], error=f"no {r['dae']}")); continue
        B = tris_of(ec.load_dae(r['dae']))
        D = door_tris(r['door'], r['dx'], r['dz'])
        m = measure(B, D)
        rows.append(dict(res=res, what=r['what'], group=r.get('group'), door=r['door'], dx=r['dx'], dz=r['dz'],
                         model=os.path.relpath(r['dae'], ROOT), **m, problems=problems(m)))
    return rows

# ------------------------------------------------------------------------------------------------------- the world
def world_report(wd):
    """Every placed door in a built world: a building's door record, and door models placed by themselves (second
    doors: Route 110's gate, the cable car stations). Occluders: every model of ours placed within 6 tiles (awnings,
    annexes, lamps, a second building). The game puts a door at the building's position + (dx, dy, dz), not rotated with it,
    and turns the door model with the building (field_buildmodel.c FieldPropSystem_InstantiateProps)."""
    import outdoor_check as oc
    door_res = set(DOOR_TOPS)
    rows = []
    for fr in oc.frames(wd):
        if fr.name.startswith('alt_'): continue          # (alt layouts reuse the main world's buildings)
        pl = [(c, p) for c in fr.cells for p in fr.placements(c)]
        for c, (res, X, Y, Z, rot) in pl:
            r = oc.registry(fr).get(res)
            if res in door_res:                           # a door placed by itself
                door, off, what = res, np.zeros(3), f'door {res} prop'
            elif r and r['door'] not in (None, 0xFFFF) and not r['retail']:
                door, off, what = r['door'], np.array([r['dx'], 0.0, r['dz']]), r['what']
            else: continue
            cs, sn = math.cos(math.radians(rot)), math.sin(math.radians(rot))
            R = np.array([[cs, 0, sn], [0, 1, 0], [-sn, 0, cs]])
            B = []
            for c2, (res2, X2, Y2, Z2, rot2) in pl:
                if abs(X2 - X) > 96 or abs(Z2 - Z) > 96 or res2 in door_res and (res2, X2, Z2) == (res, X, Z): continue
                r2 = oc.registry(fr).get(res2)
                if r2 is None or r2['retail']: continue      # Black 2's own props (signs, the fountain, rocks): not walls,
                                                             # eaves or porches (a sign on the approach tile is no misfit)
                for n, img, P, UV, A, src in oc.placed_parts(fr, res2, X2, Y2, Z2, rot2, with_door=False):
                    if img and os.path.basename(img).split('.')[0] in SKIP_TEX: continue
                    B.append((P - np.array([X, Y, Z])) @ R)        # world -> this model's frame (R orthonormal)
            B = np.concatenate(B) if B else np.zeros((0, 3, 3))
            D = tris_of(oc.model_parts(fr, door)) + R.T @ off
            m = measure(B, D)
            tile = (int((X + off[0]) // 16), int((Z + off[2]) // 16))
            pr = problems(m); acc = ACCEPTED.get((fr.name, tile)) if pr else None
            rows.append(dict(frame=fr.name, res=res, door=door, what=what, tile=tile, rot=round(rot), **m,
                             problems=[] if acc else pr, accepted=pr if acc else None, why=acc))
    return rows

# ------------------------------------------------------------------------------------------------ Black 2's own
B2_CACHE = os.path.join(ROOT, 'work', 'agents', 'door_fix', 'b2models')
def _b2_dae(pack, res, bmd):
    import b2files, subprocess
    d = os.path.join(B2_CACHE, f'p{pack}_{res}')
    dd = os.path.join(d, 'dae')
    if os.path.isdir(dd):
        f = [x for x in os.listdir(dd) if x.endswith('.dae')]
        if f: return os.path.join(dd, f[0])
    os.makedirs(d, exist_ok=True)
    open(os.path.join(d, 'm.nsbmd'), 'wb').write(bmd)
    open(os.path.join(d, 't.nsbtx'), 'wb').write(b2files.building_textures(ec.FILES, pack))
    subprocess.run([ec.APICULA, 'convert', os.path.join(d, 'm.nsbmd'), os.path.join(d, 't.nsbtx'), '-o', dd, '-f', 'dae'],
                   capture_output=True)
    f = [x for x in os.listdir(dd) if x.endswith('.dae')] if os.path.isdir(dd) else []
    return os.path.join(dd, f[0]) if f else None

def b2_report():
    import b2files
    packs = b2files.narc_entries(b2files.arc_path(ec.FILES, 225))
    rows = []
    for pk in range(len(packs)):
        magic, secs = b2files.gf_container(packs[pk])
        if magic != 'AB': continue
        n = len(secs) // 2
        recs = {}
        for i in range(n):
            res, typ, door, dx, dy, dz = struct.unpack_from('<HHHhhh', secs[i], 0)
            recs[res] = (typ, door, dx, dy, dz, secs[n + i])
        for res, (typ, door, dx, dy, dz, bmd) in sorted(recs.items()):
            if door == 0xFFFF or door not in recs: continue
            p = _b2_dae(pk, res, bmd); q = _b2_dae(pk, door, recs[door][5])
            if not p or not q: continue
            B = tris_of(ec.load_dae(p)); D = tris_of(ec.load_dae(q)) + np.array([dx, dy, dz])
            if not len(B) or not len(D): continue
            m = measure(B, D)
            rows.append(dict(pack=pk, res=res, name=b2files.nitro_names(bmd)[:1], door=door,
                             door_name=b2files.nitro_names(recs[door][5])[:1], dx=dx, dy=dy, dz=dz, **m, problems=problems(m)))
    return rows

# ------------------------------------------------------------------------------------------------------- render
def render_model(res, out, scale=4.0, parts=None):
    """Camera-angle picture of model res + its door (ours, or parts given)."""
    reg = dict(our_models())
    r = reg[res]
    P = parts or [(n, img, P, UV, A, 'b') for n, img, P, UV, A in ec.load_dae(r['dae'])]
    P += [(n, img, P_ + np.array([r['dx'], 0, r['dz']]), UV, A, 'd') for n, img, P_, UV, A in ec.model_parts(r['door'])]
    Q = np.concatenate([p[2].reshape(-1, 3) for p in P])
    box = (Q[:, 0].min() - 8, Q[:, 2].min() - 8, Q[:, 0].max() + 8, Q[:, 2].max() + 24)
    ec.render(P, box, scale, bg=(150, 190, 120)).save(out)
    return out

def summary(rows, key='what'):
    bad = [r for r in rows if r.get('problems') or r.get('error')]
    for r in rows:
        tag = 'FIX ' if (r.get('problems') or r.get('error')) else ('acc ' if r.get('accepted') else 'ok  ')
        name = r.get(key) if key in r else r.get('name')
        where = f"{r['frame']} {r['tile']} " if 'frame' in r else (f"pack {r['pack']} " if 'pack' in r else '')
        if 'error' in r: print(f"{tag}{where}res {r['res']} {name}: {r['error']}"); continue
        print(f"{tag}{where}res {r['res']} {str(name)[:44]:44s} door {r['door']:3d} top {r['top']:5.1f} clear {r['clear']:5.1f} "
              f"wall {r['wall'] * 100:3.0f}% hidden {r['hidden'] * 100:3.0f}% inset {r['inset']}"
              + (('  <- ' + '; '.join(r['problems'])) if r['problems'] else '')
              + (f"  (accepted: {'; '.join(r['accepted'])}: {r['why']})" if r.get('accepted') else ''))
    print(f'{len(rows)} doors, {len(bad)} with findings')
    return bad

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('what', choices=['models', 'world', 'b2', 'render'])
    ap.add_argument('args', nargs='*')
    ap.add_argument('--json')
    a = ap.parse_args()
    if a.what == 'render':
        print(render_model(int(a.args[0]), a.args[1])); return
    if a.what == 'models': rows = model_report(); bad = summary(rows)
    elif a.what == 'world': rows = world_report(ec.world_dir(a.args[0] if a.args else None) if a.args else
                                                (os.environ.get('HOENN_WORLD_DIR') or os.path.join(ROOT, 'work', 'world')))
    else: rows = b2_report()
    if a.what != 'models': bad = summary(rows, 'what' if a.what == 'world' else 'name')
    if a.json: json.dump(rows, open(a.json, 'w'), indent=1, default=str)
    if a.what != 'b2' and bad: sys.exit(1)

if __name__ == '__main__':
    main()
