"""People in the built rooms as the game's camera shows them (indoor_check agent, 2026-10-08; notes/INTERIORS.md
"Indoor check"). rooms_check.py runs it as kinds m-q (part of its default); alone:

    python3 rooms_view.py [--dir ROOMS] [--rom ROM] [--kinds mnopq] [--summary] [ROOM ...]
    python3 rooms_view.py --render OUT.png ROOM [X,Z]      the room from the game camera with its people (+ the player
                                                           at Sapphire tile X,Z), a 256x192 frame like the emulator's
    python3 rooms_view.py --b2 [ZONE ...]                  the same checks on Black 2's own rooms (the baseline)

How Black 2 draws a person (measured in DeSmuME and read in the decomp):
  - a camera-facing quad (billboard.c BLACT_TYPE_FACE_CAMERA: the inverse view rotation, so the quad is perpendicular
    to the view direction and every pixel of it has the view depth of its anchor), 28 x 28 units for a 32 x 32 frame
    (BlActSceneSetup scale 7.0 x actor scale 2.0 x the BLACT_ORIGIN_CENTER_BOTTOM quad 2 x 2), anchored at the bottom
    centre 0.59 units below the person's feet (RAM: the actors' pos y -0.5947 at y 0);
  - drawn after the map with the depth test. fieldmap.c FieldRenderPhase2_Fieldmap adds FX_Mul(m[2][2], 0x136) to
    the projection's m[3][2] for objects (0x1ee for zones whose header has projection type 1, the caves). Measured on
    emulator shots against this renderer (DEPTH_K below): in camera 0 rooms people are drawn over geometry up to
    ~4.3% of their view distance nearer the camera (~10 units); the Pokémon Center 1F camera (3) gives them nothing;
  - the field camera of the zone header's camera index (zone_header.inc: weather_word >> 9). Rooms use two (RAM,
    NNS_G3dGlb camPos/camTarget/projMtx at 0x02143a0c): camera 0 = eye 185.73 up and 142.05 south of the target
    (52.6 degrees down, the target 4 above the player) and camera 3 (Black 2's Pokémon Center 1F zones) = 120.44 up
    and 194.58 south (31.75 degrees down, the target 24.02 up and 16.90 north of the player); both fov y 39.9 degrees
    (cot 2.7539), 4:3, near 1, far 1024. The target is the player (+ the offset) inside the zone's camera box.
  - checked: this module's render() of Oldale Center 1F, Oldale Center 2F, Oldale Mart and Black 2's own zone 382
    (unchanged in our ROM) against DeSmuME shots from the same camera: the same pixels hidden and drawn
    (screenshots/indoor_check/00_model_validation.png).
So a person's quad leans back from their feet by the camera's angle: at height h above the feet it stands
h x tan(pitch) north of them, h x 1.307 (camera 0, less ~16 units for the depth margin) or h x 0.619 (camera 3).
Anything nearer the camera than that plane is drawn over the person even when it stands BEHIND them: a counter top
20 units high whose front edge is 8 units north of the feet (camera 3: the quad passes 12.4 north at that height)
shows across their head (the Oldale Pokémon Center case); in camera 0 rooms a block over ~19 units high reaching the
tile edge north of a person does the same (Black 2 stands its walls 12 units back, models_interior FRONT_H).

Kinds (one line per finding, "ROOM: (kind) detail"):
  m  people drawn wrong: every zone json / data/story NPC (32-px sheets; 64-px ones are objects such as the cable car)
     from the camera centred on them, from the camera box's two x ends, and with the player standing on the reachable
     tiles up to 6 rows north / 3 rows south of them (the camera follows the player: an NPC low on the screen, with
     the player north of them, was cut by an 18-high block behind them that the centred camera showed clean: Rustboro
     Gym's Josh, map_gfx 2026-10-11), and the player (north and south views) on every reachable tile. Each hidden sprite pixel is classed by the surface drawn over it: "cut by" = it stands more
     than 4 units north of the feet (behind the body, yet drawn across it: heads in counters, a block or shelf top
     through the hat), "stands inside" = within 6 units of the body in its own tile, "cut off by the side wall" = a
     wall / block side beside them (the sprite pokes out through it), "head hidden behind the wall in front" = a wall
     south of them covering the head (camera centred on them only: from the box's ends that is perspective). Not
     counted: in front (the nurse behind her counter), floor-level pieces, furniture beside them at their depth.
     NPCs report any of it (6+ px); the player only what Black 2's own rooms never show (`--b2` baseline: 0.3% of its
     walkable tiles): the room's walls/blocks/counter tops and standing inside furniture; tall furniture behind the
     player covering the top of the head is Black 2's own look (4% of its tiles) and counts only as a slice (a band
     through the sprite with sprite drawn above it)
  n  a person whose feet are not on the drawn floor: the drawn surface under their tile's centre (floor, raised floor,
     ramp, block top) more than 3 units above (sunk) or below (floating) the height Black 2 gives them (the collision
     height of the tile)
  o  a door / elevator model whose doorway (box centre; elevator01: its origin) is more than 4 units off the warp tile
     (or 2-tile pair) next to it (doors with no warp within 1.5 tiles are decoration)
  p  holes: pixels where nothing is drawn (the black void) enclosed by the room's geometry, from the camera at the
     box's corners; not the clear texels of cut-out textures, rooms "open": true, recipe "holes", or tiles Sapphire
     draws dark
  q  a reachable floor tile whose north / west / east side has no floor and no wall (open to the void), outside
     recipe "open" / "holes"
"""
import os, sys, json, math, struct, argparse
from collections import defaultdict, Counter
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, 'patches'))
import version  # noqa: E402

W, H = 256, 192
COT = 2.75390625                       # projMtx[1][1] (fov y 39.9 degrees); [0][0] = 2.065673828125 = COT / (4/3)
FX, FY = W / 2 * 2.065673828125, H / 2 * COT
CAMERAS = {0: dict(eye=(0.0, 185.7273, 142.0496), off=(0.0, 4.0, 0.0)),
           3: dict(eye=(0.0, 120.4419, 194.5770), off=(0.0, 24.0249, -16.9006))}
# The depth a person's quad is tested with, as a fraction of its anchor's view distance (measured in DeSmuME,
# indoor_check 2026-10-08, tools in work/agents/indoor_check/tools: rowvis.py / depthgap.py on emulator shots against
# this renderer): camera 0 rooms draw people over geometry up to ~4.3% of their distance nearer the camera (Oldale
# Center 2F, the player under the counter pillar at 238 units: sprite rows with geometry 9.7 units nearer drawn, 10.8
# hidden; the Mart counter (2.8 units) and Black 2's own zone 382 sink woman (4.9 units) drawn); the Pokémon Center
# 1F camera (3) gives none (Oldale 1F: the counter top 0.32 units nearer already hides the player's and the
# gentleman's head rows). fieldmap.c adds FX_Mul(m[2][2], 0x136) to the projection's m[3][2] for objects, which with
# near 1 / far 1024 would be 3.7% (k 0.9635) in every zone: the game does something else for camera 3 that this does
# not model; the factors are the measured ones. Camera 0 0.957 -> 0.959 (map_gfx 2026-10-11): in Rustboro Gym, Josh
# (Sapphire (7,12), an 18-high rock block at his tile's north edge) seen with the player at (5,9) has his hat brim cut by
# the block's top edge in DeSmuME (2 rows, ~40 px); this renderer hides nothing there below 0.958 and those 40 px at
# 0.959 (the Oldale 2F rows above bound it at <= 0.9592).
DEPTH_K = {0: 0.959, 3: 1.0}
QUAD = 28.0                             # units per 32-px frame
ANCHOR_Y = {0: -1.583, 3: -0.5947}      # the quad's bottom below the feet (RAM: actor pos y at feet y 0), per camera
FRONT, LOW = 4.0, 3.0                   # body depth in front of the feet; floor-level pieces (rugs, cushions, shadows)
MIN_PX = 6                              # pixels of a sprite that make a finding (3-5 px slivers at an arm
                                        # or hat brim beside furniture are not visible as a glitch)
BAD = ('inside', 'cut', 'wall', 'wallhead')   # the occlusion classes that are glitches (see View.look)
ALPHA_MIN = 8                           # texels at or below this alpha draw nothing (colour 0 / A3I5 alpha 0); translucent
                                        # ones blend over what is behind, so they count as drawn


# ------------------------------------------------------------------------------------------------ sprites
class Sprites:
    """Frames of the people's object codes (a/0/4/7 table, a/0/4/8 sheets) from a ROM, or Black 2's own files."""
    def __init__(self, rom=None):
        import importlib.util                              # b2tools/sprites.py (patches/sprites.py has the same name)
        spec = importlib.util.spec_from_file_location('b2tools_sprites', os.path.join(HERE, 'sprites.py'))
        sp = importlib.util.module_from_spec(spec); spec.loader.exec_module(sp)
        self.sp = sp
        if rom:
            import interior_sweep_check as isc
            self.table_raw, self.sheets = isc.nds_narc(rom, 47)[0], isc.nds_narc(rom, 48)
        else:
            from models_interior import FILES
            import b2files
            self.table_raw = b2files.narc_entries(b2files.arc_path(FILES, 47))[0]
            self.sheets = b2files.narc_entries(b2files.arc_path(FILES, 48))
        n = struct.unpack_from('<I', self.table_raw, 0)[0]
        keys = ('uid entityType sceneNodeType shadow footprint reflections billboardSize spriteAtlasSize '
                'spriteControllerType gender collWidth collHeight offX offY offZ res1 res2 anim0 anim1 anim2').split()
        self.table = [dict(zip(keys, struct.unpack_from('<HBBBBBBBBBBBbbbHHHHH', self.table_raw, 4 + 28 * i))) for i in range(n)]
        self.cache = {}

    def frame(self, code, d):
        """(alpha mask HxW bool, RGB HxWx3) of the standing frame of object code `code` facing d (0 up 1 down 2 left 3
        right), or None for a 3D object / unknown code. Frame order by controller type (the sheets, by eye): 1 (the
        player) and 3: up, down, left, right x 3; 2 and 15: up x2, down x2, left x3, right = left mirrored."""
        k = (code, d)
        if k in self.cache: return self.cache[k]
        rec = self.table[self.sp.obj_record(code)]
        out = None
        try:
            if rec['entityType'] == 1:
                frames, _, pal = self.sp.btx_decode(self.sheets[rec['res1']])
                ct, n = rec['spriteControllerType'], len(frames)
                flip = False
                if ct in (1, 3) and n >= 12: i = 3 * d
                elif n >= 7 and ct in (2, 15): i, flip = (0, 2, 4, 4)[d], d == 3
                elif n >= 4: i = min(d, n - 1)
                else: i = 0
                _, w, h, pix = frames[i]
                a = np.array(pix, np.uint8).reshape(h, w)
                rgb = np.array([self.sp.bgr555_to_rgb(c) for c in pal], np.uint8)[a]
                if flip: a, rgb = a[:, ::-1], rgb[:, ::-1]
                out = (a > 0, rgb)
        except Exception:
            out = None
        self.cache[k] = out
        return out


# ------------------------------------------------------------------------------------------------ camera
def zone_camera(cfg):
    """(camera index, projection type) the zone header gets (patches/interiors.py: a room with "parent" takes zone
    390's weather word, "header" fields win; otherwise Black 2's own header of that zone)."""
    import zoneheaders, b2files
    from models_interior import FILES
    if not hasattr(zone_camera, 'H'):
        zone_camera.H = zoneheaders.parse(b2files.narc_entries(b2files.arc_path(FILES, 12))[0])
    hd = zone_camera.H
    w = hd[cfg['zone']]['weather_word']
    if 'parent' in cfg: w = hd[390]['weather_word']
    w = cfg.get('header', {}).get('weather_word', w)
    return w >> 9, (w >> 6) & 7

def view_matrix(eye, target):
    f = np.array(target, float) - np.array(eye, float); f /= np.linalg.norm(f)
    r = np.cross(f, [0, 1.0, 0]); r /= np.linalg.norm(r)
    u = np.cross(r, f)
    return np.stack([r, u, -f])

def camera_at(cam, box, px, py, pz):
    """(eye, target) with the player at world (px, py, pz): the target is the player inside the camera box, plus the
    camera's offset."""
    c = CAMERAS.get(cam, CAMERAS[0])
    x0, x1, z0, z1 = box
    tx, tz = min(max(px, x0), x1), min(max(pz, z0), z1)
    t = np.array([tx + c['off'][0], py + c['off'][1], tz + c['off'][2]])
    return t + np.array(c['eye']), t


# ------------------------------------------------------------------------------------------------ one room
def built_parts(b):
    """[(owner label, texture path, P (n,3,3) zone units, UV (n,3,2))] of a rooms_check.Built or a B2Room: the room's
    terrain (one owner per texture) and every furniture piece, with UVs (alpha-tested texels draw nothing)."""
    import preview_interior as pv
    out = []
    if isinstance(b, B2Room):
        terr = pv.parse(b.parts_path)
        furn = [(b.label(f), pv.placed(pv.furniture_parts(bl['res_id'], b.pack), (bl['x'], bl['y'], bl['z']), bl['rot']))
                for f, bl in zip(b.furn, b.placements)]
    else:
        tf = os.path.join(b.d, 'terrain_all.dae')
        terr = pv.parse(tf if os.path.exists(tf) else os.path.join(b.d, 'terrain.dae'))
        names = {m['res']: m['name'] for m in b.meta['models']}; packs = {m['res']: m['pack'] for m in b.meta['models']}
        by_name = {v: k for k, v in names.items()}
        furn = []
        for f, fm in zip(b.furn, b.meta['furniture']):
            res = fm['m'] if isinstance(fm['m'], int) else by_name[fm['m']]
            furn.append((b.label(f), pv.placed(pv.furniture_parts(res, packs[res]), fm['pos'], fm['rot'])))
    off = np.array([256.0, 0, 256.0])
    for tp, P, UV, C in terr:
        out.append((f'room {os.path.basename(tp or "none")[:-4]}', tp, P + off, UV))
    for label, parts in furn:
        for tp, P, UV, C in parts: out.append((label, tp, P + off, UV))
    return out


class View:
    """The room's triangles in zone units with their owners and texture coordinates."""
    def __init__(self, built, cfg, sprites):
        import preview_interior as pv
        self.b, self.cfg, self.spr = built, cfg or {}, sprites
        tris, own, uvs, tex = [], [], [], []
        self.names, self.texs = [], []
        for label, tp, P, UV in built_parts(built):
            if label not in self.names: self.names.append(label)
            if tp not in self.texs: self.texs.append(tp)
            tris.append(np.asarray(P, float).reshape(-1, 3, 3)); uvs.append(np.asarray(UV, float).reshape(-1, 3, 2))
            own += [self.names.index(label)] * len(P); tex += [self.texs.index(tp)] * len(P)
        T = np.concatenate(tris) if tris else np.zeros((0, 3, 3))
        UV = np.concatenate(uvs) if uvs else np.zeros((0, 3, 2))
        n = np.cross(T[:, 1] - T[:, 0], T[:, 2] - T[:, 0])
        keep = np.linalg.norm(n, axis=1) > 1e-6
        self.T, self.UV, self.own, self.tex = T[keep], UV[keep], np.array(own, int)[keep], np.array(tex, int)[keep]
        self.alpha = [None if pv.tex(tp) is None else pv.tex(tp)[..., 3] for tp in self.texs]
        self.lo, self.hi = self.T.min(axis=1), self.T.max(axis=1)          # triangle boxes (zone units)
        self.is_room = np.array([n.startswith('room ') for n in self.names] + [False])   # owner -> room terrain
        self.cam, self.proj = zone_camera(self.cfg) if self.cfg.get('zone') is not None else (0, 0)
        self.bias = DEPTH_K.get(self.cam, DEPTH_K[0])
        self.box = built.meta['camera']

    # --- people
    def people(self, story_objs=()):
        """[(label, zone tile, code, dir)] of the zone json's NPCs and the room's data/story NPCs (64-px sheets are
        objects placed on purpose: the cable car hanging from its cable, the S.S. Tidal; people are 32 px)."""
        b = self.b; out = []
        for i, n in enumerate(self.cfg.get('npcs', [])):
            if 'at' in n:
                who = (n.get('_what') or n.get('what') or f'uid {n.get("uid")}')[:48]
                out.append((f'NPC {i} uid {n.get("uid")} ({who})', b.zt(n['at']), n.get('model', 0), n.get('dir', 1)))
        for src, o in story_objs:
            if o.get('kind') == 'npc' and 'at' in o:
                who = (o.get('what') or '')[:48]
                code = o.get(f'model_{version.VERSION}', o.get('model', 0))         # (the story patch's choice)
                out.append((f'{src} NPC uid {o.get("uid")} ({who})', b.zt(o['at']), code, o.get('dir', 1)))
        if self.spr:
            out = [p for p in out if (self.spr.frame(p[2], p[3]) is None or self.spr.frame(p[2], p[3])[0].shape[0] <= 32)]
        return out

    def feet_y(self, tile):
        c = self.b.cells.get(tile)
        if c is None: return 0.0
        # (a solid flat tile too: Black 2 snaps an actor to its tile's height, CheckRecalcActorY; a table top under a
        # Poke Ball, models_interior "solid_y", as Black 2's own starter balls on solid tiles at 8: zone 391)
        try: return float(self.b.plane_y(c, tile[0] * 16 + 8, tile[1] * 16 + 8))
        except Exception: return 0.0

    # --- one sprite from one camera
    def look(self, tile, code, d, eye, target, y=None):
        """Hidden opaque pixels of the sprite of `code` facing d at zone tile `tile`: {class: {owner: n}}, total
        opaque pixels, and the sprite rows hit ({class: set(rows)}). Classes: 'cut' (geometry behind the person drawn
        over them), 'inside' (geometry in their own tile within their body), 'front' (in front: natural)."""
        fr = self.spr.frame(code, d) if self.spr else None
        if fr is None: return None
        mask, _ = fr
        fh, fw = mask.shape
        R = view_matrix(eye, target); eye = np.asarray(eye, float)
        fy = self.feet_y(tile) if y is None else y
        px, pz = tile[0] * 16 + 8, tile[1] * 16 + 8
        c = R @ (np.array([px, fy + ANCHOR_Y.get(self.cam, ANCHOR_Y[0]), pz]) - eye)
        zq = -c[2]
        if zq < 2: return None
        qw, qh = QUAD * fw / 32, QUAD * fh / 32
        sx0, sx1 = W / 2 + FX * (c[0] - qw / 2) / zq, W / 2 + FX * (c[0] + qw / 2) / zq
        sy0, sy1 = H / 2 - FY * (c[1] + qh) / zq, H / 2 - FY * c[1] / zq
        X0, X1 = int(math.floor(sx0)), int(math.ceil(sx1)); Y0_, Y1 = int(math.floor(sy0)), int(math.ceil(sy1))
        gx, gy = np.meshgrid(np.arange(X0, X1) + 0.5, np.arange(Y0_, Y1) + 0.5)
        u = ((gx - sx0) / (sx1 - sx0) * fw).astype(int); v = ((gy - sy0) / (sy1 - sy0) * fh).astype(int)
        inside = (u >= 0) & (u < fw) & (v >= 0) & (v < fh) & (gx >= 0) & (gx < W) & (gy >= 0) & (gy < H)   # on screen
        opaque = np.zeros(gx.shape, bool)
        opaque[inside] = mask[v[inside], u[inside]]
        if not opaque.any(): return None
        # the room's triangles over the sprite's rectangle, nearest first (z-buffer)
        # only triangles near the person can cover the sprite: 40 units to each side, 64 north (the quad leans back
        # 37 units at most), 64 south (tall pieces in front), above the floor-level pieces (they can only be 'low')
        near = ((self.hi[:, 0] >= px - 40) & (self.lo[:, 0] <= px + 40) & (self.hi[:, 2] >= pz - 64) &
                (self.lo[:, 2] <= pz + 64) & (self.hi[:, 1] >= fy + LOW))
        idx = np.nonzero(near)[0]
        V = (self.T[idx] - eye) @ R.T                               # (N,3,3) view space
        z = -V[..., 2]
        ok = (z > 1).all(axis=1) & (z.min(axis=1) < zq)
        if not ok.any():
            return dict(hidden={}, opaque=int(opaque.sum()), rows={}, rect=(X0, Y0_, X1, Y1), slice=0)
        idx = idx[ok]
        Vk, zk, ownk, Tk, UVk, texk = V[ok], z[ok], self.own[idx], self.T[idx], self.UV[idx], self.tex[idx]
        sx = W / 2 + FX * Vk[..., 0] / zk; sy = H / 2 - FY * Vk[..., 1] / zk
        over = (sx.max(1) >= X0) & (sx.min(1) <= X1) & (sy.max(1) >= Y0_) & (sy.min(1) <= Y1)
        zb = np.full(gx.shape, np.inf); ob = np.full(gx.shape, -1, int); tb = np.full(gx.shape, -1, int)
        for t in np.nonzero(over)[0]:
            (ax, bx, cx), (ay, by, cy) = sx[t], sy[t]
            den = (by - cy) * (ax - cx) + (cx - bx) * (ay - cy)
            if abs(den) < 1e-9: continue
            w0 = ((by - cy) * (gx - cx) + (cx - bx) * (gy - cy)) / den
            w1 = ((cy - ay) * (gx - cx) + (ax - cx) * (gy - cy)) / den
            w2 = 1 - w0 - w1
            m = (w0 >= -1e-4) & (w1 >= -1e-4) & (w2 >= -1e-4)
            if not m.any(): continue
            iz = 1 / zk[t]
            q = w0 * iz[0] + w1 * iz[1] + w2 * iz[2]
            dep = 1 / q
            m &= dep < zb
            A = self.alpha[texk[t]]
            if A is not None and m.any():                      # alpha test: clear texels draw nothing (leaves,
                uu = (w0 * UVk[t, 0, 0] * iz[0] + w1 * UVk[t, 1, 0] * iz[1] + w2 * UVk[t, 2, 0] * iz[2]) / q   # glass
                vv_ = (w0 * UVk[t, 0, 1] * iz[0] + w1 * UVk[t, 1, 1] * iz[1] + w2 * UVk[t, 2, 1] * iz[2]) / q  # rims)
                th, tw = A.shape
                m &= A[np.floor((1 - vv_) * th).astype(int) % th, np.floor(uu * tw).astype(int) % tw] > ALPHA_MIN
            zb[m] = dep[m]; ob[m] = ownk[t]; tb[m] = idx[t]
        hid = opaque & (zb < zq * self.bias)
        out = defaultdict(Counter); rows = defaultdict(set)
        if hid.any():
            # world point of the drawn surface at each hidden pixel
            hy, hx = np.nonzero(hid)
            dz = zb[hy, hx]
            vx = (gx[hy, hx] - W / 2) * dz / FX; vy = -(gy[hy, hx] - H / 2) * dz / FY
            Q = np.stack([vx, vy, -dz], 1) @ R + eye
            # classify every hidden pixel by where the surface drawn over it stands (vectorised)
            own_px, tri_px, vrow = ob[hy, hx], tb[hy, hx], v[hy, hx]
            Tp = self.T[tri_px]
            nrm = np.cross(Tp[:, 1] - Tp[:, 0], Tp[:, 2] - Tp[:, 0])
            nrm = nrm / np.maximum(np.linalg.norm(nrm, axis=1), 1e-9)[:, None]
            room = self.is_room[own_px]
            wallish = room & (np.abs(nrm[:, 1]) < 0.3)                  # a wall face of the room
            qx, qy, qz = Q[:, 0], Q[:, 1], Q[:, 2]
            cls = np.select(
                [qy < fy + LOW,                                         # floor-level pieces
                 qz < pz - FRONT,                                       # behind the body, drawn over it
                 (qz >= pz + FRONT) & wallish & (vrow < 14),            # a wall in front hides the head
                 qz >= pz + FRONT,                                      # in front: natural
                 np.abs(qx - px) < 6,                                   # in their own tile, at the body (Black 2 lets
                                                                        # furniture reach 2 units into a tile)
                 room & (np.abs(nrm[:, 0]) > 0.7)],                     # a side wall / block side running past them:
                                                                        # the sprite pokes out through it, cut off
                ['low', 'cut', 'wallhead', 'front', 'inside', 'wall'], 'side')   # side: furniture beside them
            for c_, o_, r_ in zip(cls, own_px, vrow):
                out[c_][int(o_)] += 1; rows[c_].add(int(r_))
            badm = np.isin(cls, BAD)
            bad = np.zeros(gx.shape, bool); bad[hy[badm], hx[badm]] = True
            # a slice: a bad pixel with a drawn pixel of the sprite above it in its column (a band through the head,
            # the hat tip floating over a counter top); a cover hides the sprite from its top down (reads as "behind")
            vis = opaque & ~hid
            above = np.maximum.accumulate(vis, axis=0)
            above = np.vstack([np.zeros((1, gx.shape[1]), bool), above[:-1]])
            slice_px = int((bad & above).sum())
        else:
            slice_px = 0
        return dict(hidden=out, opaque=int(opaque.sum()), rows=rows, rect=(X0, Y0_, X1, Y1), slice=slice_px)

    def cameras(self, tile, player=False):
        """Camera (eye, target) pairs a person on `tile` is seen from: centred on them, and for NPCs the box's x ends
        and the player on the reachable tiles of the rows 6 north .. 3 south of them (the row's middle and both ends:
        the camera follows the player inside its box; the first camera is the centred one)."""
        px, pz = tile[0] * 16 + 8, tile[1] * 16 + 8
        y = self.feet_y(tile)
        xs = [px] if player else [px, self.box[0], self.box[1]]
        out = [camera_at(self.cam, self.box, x, y, pz) for x in xs]
        if player: return out
        if not hasattr(self, '_rows'):
            rows = defaultdict(list)
            for t in reachable(self.b): rows[t[1]].append(t[0])
            self._rows = rows
        seen = {(round(t[0], 2), round(t[2], 2)) for _, t in out}
        for dz in range(-6, 4):
            xs_ = self._rows.get(tile[1] + dz)
            if not dz or not xs_: continue
            for tx in {min(xs_), max(xs_), min(xs_, key=lambda q: abs(q - tile[0]))}:
                e, t = camera_at(self.cam, self.box, tx * 16 + 8, self.feet_y((tx, tile[1] + dz)), (tile[1] + dz) * 16 + 8)
                k = (round(t[0], 2), round(t[2], 2))
                if k not in seen: seen.add(k); out.append((e, t))
        return out

    def worst(self, tile, code, dirs, player=False):
        best = None
        for d in dirs:
            for ci, (eye, tgt) in enumerate(self.cameras(tile, player)):
                r = self.look(tile, code, d, eye, tgt)
                if r is None: continue
                if ci:                         # from the box's ends a wall in front hiding a head is perspective (a
                    r['hidden'].pop('wallhead', None)   # pillar between a far camera and them): only centred on them
                n = self.score(r, player)
                if best is None or n > best[0]: best = (n, r, d)
        return best

    def score(self, r, player=False):
        """Glitch pixels of a look: every BAD pixel for an NPC (they stand where Sapphire put them, always in view). For
        the player, what Black 2's own rooms never show (rooms_view.py --b2 baseline: 0.3% of its walkable tiles):
        the room's walls/blocks/counter tops drawn over them and standing inside furniture; furniture behind them that
        covers the top of the head is Black 2's own look (its plants, fridges and shelves do it on 4% of its tiles), so
        it counts only as a slice (a band through the sprite with the sprite drawn above it)."""
        if not player: return sum(sum(c.values()) for k, c in r['hidden'].items() if k in BAD)
        n = sum(v for k, c in r['hidden'].items() if k in BAD for o, v in c.items() if self.is_room[o] or k == 'inside')
        return n + (r['slice'] if r['slice'] >= MIN_PX else 0)

    def describe(self, r):
        parts = []
        for cls in BAD:
            c = r['hidden'].get(cls)
            if not c or sum(c.values()) < MIN_PX: continue
            rows = sorted(r['rows'][cls])
            where = 'head' if rows[-1] < 14 else ('feet' if rows[0] > 26 else 'body')
            who = ', '.join(f'{self.names[o]} ({n} px)' for o, n in c.most_common(3))
            verb = {'inside': 'stands inside', 'cut': 'cut by', 'wall': 'cut off by the side wall',
                    'wallhead': 'head hidden behind the wall in front'}[cls]
            parts.append(f'{verb} {who} across sprite rows {rows[0]}-{rows[-1]} ({where})')
        return '; '.join(parts)


# ------------------------------------------------------------------------------------------------ checks
PLAYER_CODE = 231                      # the boy's walking sheet (Brendan's art in our ROM); the girl's is the same size

def check_room(view, story_objs, kinds, say):
    b = view.b
    if 'm' in kinds:
        stairs = b.stair_tiles()
        for who, t, code, d in view.people(story_objs):
            w = view.worst(t, code, [d])
            if w and w[0] >= MIN_PX:
                say('m', f'{who} at Sapphire {b.sap(t)}: {view.describe(w[1])} (camera {view.cam})')
        # the player on every reachable walkable tile, facing north and south
        seen = reachable(b)
        bad = []
        for t in sorted(seen):
            if t in stairs: continue
            w = view.worst(t, PLAYER_CODE, [0, 1], player=True)
            if w and w[0] >= MIN_PX: bad.append((t, w))
        for t, w in bad:
            say('m', f'the player at Sapphire {b.sap(t)} facing {"north" if w[2] == 0 else "south"}: {view.describe(w[1])} (camera {view.cam})')
    if 'o' in kinds: check_doors(view, say)
    if 'p' in kinds: check_view_holes(view, say)
    if 'q' in kinds: check_walls(view, say)
    if 'n' in kinds:
        for who, t, code, d in view.people(story_objs):
            if view.spr and view.spr.frame(code, d) is None: continue     # 3D objects (ships, the cable car): their own
            gy = view.feet_y(t)                                          # model, placed on purpose
            ys = surface_heights(b, t)
            if not ys: continue
            near = min(ys, key=lambda y: abs(y - (gy - 2)))       # Black 2 floors are drawn 2 below the collision
            if abs(near - (gy - 2)) > 3:
                say('n', f'{who} at Sapphire {b.sap(t)}: feet at {gy:.0f} (collision), drawn surface at {near:.0f} '
                         f'({"sunk" if near > gy - 2 else "floating"} {abs(near - (gy - 2)):.0f} units)')

DOOR_MODELS = ('door', 'elevator')            # door models: cabin_door(_r), door_h5_in, door_pwood01, elevator01

def warp_tiles(view):
    """Zone tiles of the room's warps: the builder's warp spots and the zone json's warps."""
    b = view.b
    out = {tuple(t) for s in b.meta.get('warp_spots', []) for t in ([(q[0] + b.ox, q[1] + b.oz) for q in s['tiles']])}
    for w in view.cfg.get('warps', []):
        if 'at' in w: out.add(b.zt(w['at']))
    return out

def check_doors(view, say):
    """(o) a door or elevator model whose doorway is not centred on a warp tile next to it: the door you walk into is
    drawn beside the warp (doors with no warp within 1.5 tiles are decoration: Sapphire's inner doors, back doors)."""
    b = view.b
    if not hasattr(b, 'meta') or 'furniture' not in b.meta: return
    tiles = warp_tiles(view)
    for f in b.furn:
        if not any(k in f['name'] for k in DOOR_MODELS): continue
        P = f['pts'] + np.array([256.0, 0, 256.0]) if len(f['pts']) else None
        if P is None: continue
        z0, z1 = P[:, 2].min(), P[:, 2].max()
        # the doorway: the box centre (cabin_door_r's origin is 9 units off it); elevator01's is its origin (6 units
        # off its box: Black 2 chunks 836/1011 and our Devon / Dept. Store rooms)
        cx = f['pos'][0] + 256 if f['name'].startswith('elevator') else (P[:, 0].min() + P[:, 0].max()) / 2
        near = [t for t in tiles if abs(t[0] * 16 + 8 - cx) <= 24 and z0 - 24 <= t[1] * 16 + 8 <= z1 + 24]
        if not near: continue
        t = min(near, key=lambda q: abs(q[0] * 16 + 8 - cx))
        dx = cx - (t[0] * 16 + 8)
        # a 2-tile warp (mats, double doors) centres the door on the pair
        pair = [q for q in near if q[1] == t[1] and abs(q[0] - t[0]) == 1]
        if pair: dx = min([dx] + [cx - ((t[0] + q[0]) * 8 + 8) for q in pair], key=abs)
        if abs(dx) > 4:
            say('o', f'{b.label(f)}: its doorway centre is {dx:+.0f} units off the warp tile Sapphire {b.sap(t)}')

def coverage(view, eye, target, geometry=False):
    """Depth buffer of the room's geometry (alpha-tested) from (eye, target): inf where nothing is drawn. geometry:
    also a mask of the pixels any triangle covers, clear texels or not (cut-out textures: arrows, grates, rails)."""
    R = view_matrix(eye, target); eye = np.asarray(eye, float)
    V = (view.T - eye) @ R.T; z = -V[..., 2]
    ok = (z > 1).all(axis=1)
    zb = np.full((H, W), np.inf); geo = np.zeros((H, W), bool)
    sx = W / 2 + FX * V[..., 0] / np.maximum(z, 1e-3); sy = H / 2 - FY * V[..., 1] / np.maximum(z, 1e-3)
    for t in np.nonzero(ok)[0]:
        x0, x1 = int(max(0, math.floor(sx[t].min()))), int(min(W - 1, math.ceil(sx[t].max())))
        y0, y1 = int(max(0, math.floor(sy[t].min()))), int(min(H - 1, math.ceil(sy[t].max())))
        if x1 < x0 or y1 < y0: continue
        xs, ys = np.meshgrid(np.arange(x0, x1 + 1) + 0.5, np.arange(y0, y1 + 1) + 0.5)
        (ax, bx, cx), (ay, by, cy) = sx[t], sy[t]
        den = (by - cy) * (ax - cx) + (cx - bx) * (ay - cy)
        if abs(den) < 1e-9: continue
        w0 = ((by - cy) * (xs - cx) + (cx - bx) * (ys - cy)) / den
        w1 = ((cy - ay) * (xs - cx) + (ax - cx) * (ys - cy)) / den
        w2 = 1 - w0 - w1
        m = (w0 >= -1e-4) & (w1 >= -1e-4) & (w2 >= -1e-4)
        if not m.any(): continue
        geo[y0:y1 + 1, x0:x1 + 1] |= m
        iz = 1 / z[t]; q = w0 * iz[0] + w1 * iz[1] + w2 * iz[2]; dep = 1 / q
        sub = zb[y0:y1 + 1, x0:x1 + 1]
        m &= dep < sub
        A = view.alpha[view.tex[t]]
        if A is not None and m.any():
            UV = view.UV[t]
            uu = (w0 * UV[0, 0] * iz[0] + w1 * UV[1, 0] * iz[1] + w2 * UV[2, 0] * iz[2]) / q
            vv = (w0 * UV[0, 1] * iz[0] + w1 * UV[1, 1] * iz[1] + w2 * UV[2, 1] * iz[2]) / q
            th, tw = A.shape
            m &= A[np.floor((1 - vv) * th).astype(int) % th, np.floor(uu * tw).astype(int) % tw] > ALPHA_MIN
        sub[m] = dep[m]
    return (zb, geo) if geometry else zb

def check_view_holes(view, say):
    """(p) cracks and holes: screen pixels where nothing is drawn (the black clear colour shows) enclosed by the room's
    drawn geometry, from the camera at the corners of the camera box."""
    b = view.b
    try:
        import models_interior as mi
        rec = mi.load_recipe(b.name)
    except Exception:
        rec = {}
    if rec.get('open') is True: return                 # floating in the dark on purpose (Dewford Gym, New Mauville)
    holes_rec = set()                                  # floor openings on purpose: Mt. Pyre's, Sky Pillar's well
    for q in rec.get('holes') or []:
        for x in range(int(math.floor(q[0])) - 1, int(math.ceil(q[2])) + 1):
            for z in range(int(math.floor(q[1])) - 1, int(math.ceil(q[3])) + 1): holes_rec.add(b.zt((x, z)))
    try: lum = mi.metatile_lum(b.meta['map'])
    except Exception: lum = []
    x0, x1, z0, z1 = view.box
    seen = set()
    for x in sorted({x0, x1}):
        for z in sorted({z0, z1}):
            eye, tgt = camera_at(view.cam, view.box, x, 0, z)
            zb, geo = coverage(view, eye, tgt, geometry=True)
            empty = ~np.isfinite(zb)
            # flood the empty pixels from the screen border: what it can't reach is enclosed
            from collections import deque
            out = np.zeros_like(empty); dq = deque()
            for yy in range(H):
                for xx in (0, W - 1):
                    if empty[yy, xx] and not out[yy, xx]: out[yy, xx] = True; dq.append((yy, xx))
            for xx in range(W):
                for yy in (0, H - 1):
                    if empty[yy, xx] and not out[yy, xx]: out[yy, xx] = True; dq.append((yy, xx))
            while dq:
                yy, xx = dq.popleft()
                for a, c in ((yy + 1, xx), (yy - 1, xx), (yy, xx + 1), (yy, xx - 1)):
                    if 0 <= a < H and 0 <= c < W and empty[a, c] and not out[a, c]: out[a, c] = True; dq.append((a, c))
            holes = empty & ~out & ~geo        # (clear texels of cut-out textures over the void are Black 2's own look)
            if not holes.any(): continue
            # components; each reported once (by the floor tile its ray meets)
            lab = np.zeros(holes.shape, int); k = 0
            R = view_matrix(eye, tgt)
            for yy, xx in zip(*np.nonzero(holes)):
                if lab[yy, xx]: continue
                k += 1; st = [(yy, xx)]; lab[yy, xx] = k; comp = []
                while st:
                    a, c = st.pop(); comp.append((a, c))
                    for a2, c2 in ((a + 1, c), (a - 1, c), (a, c + 1), (a, c - 1)):
                        if 0 <= a2 < H and 0 <= c2 < W and holes[a2, c2] and not lab[a2, c2]: lab[a2, c2] = k; st.append((a2, c2))
                if len(comp) < 2: continue
                cy_, cx_ = np.mean(comp, axis=0)
                d = R.T @ np.array([(cx_ + 0.5 - W / 2) / FX, -(cy_ + 0.5 - H / 2) / FY, -1.0])
                tt = (Y0F - eye[1]) / d[1] if d[1] < 0 else None
                tile = (int((eye[0] + tt * d[0]) // 16), int((eye[2] + tt * d[2]) // 16)) if tt else None
                key = tile
                if tile in holes_rec: continue
                st = b.sap(tile) if tile else None
                if st and 0 <= st[1] < len(lum) and 0 <= st[0] < len(lum[0]) and lum[st[1]][st[0]] < 100:
                    continue                                   # Sapphire draws it dark there too (the cable car pits)
                if key in seen: continue
                seen.add(key)
                say('p', f'{len(comp)} px of nothing drawn (black void) inside the room at screen ({cx_:.0f},{cy_:.0f}), '
                         f'about Sapphire {b.sap(tile) if tile else "?"} (camera at {x},{z})')

Y0F = -2.0

def check_walls(view, say):
    """(q) a reachable floor tile whose north, west or east side has no floor and no wall (a vertical face within 16
    units beyond the edge, at least 8 high): the room's edge open to the black void where Black 2 stands a wall."""
    b = view.b
    try:
        import models_interior as mi
        rec = mi.load_recipe(b.name)
    except Exception:
        rec = {}
    if rec.get('open') is True: return
    opened = set()
    for q in (rec.get('open') or []) if isinstance(rec.get('open'), list) else []:
        for x in range(q[0], q[2] + 1):
            for z in range(q[1], q[3] + 1): opened.add(b.zt((x, z)))
    for q in rec.get('holes') or []:                    # floor openings on purpose (stair_d01 shafts, Sky Pillar's well)
        for x in range(int(math.floor(q[0])), int(math.ceil(q[2]))):
            for z in range(int(math.floor(q[1])), int(math.ceil(q[3]))): opened.add(b.zt((x, z)))
    T = view.T
    n = np.cross(T[:, 1] - T[:, 0], T[:, 2] - T[:, 0]); n /= np.linalg.norm(n, axis=1)[:, None]
    vert = T[np.abs(n[:, 1]) < 0.3]
    vx0, vx1 = vert[..., 0].min(1), vert[..., 0].max(1); vz0, vz1 = vert[..., 2].min(1), vert[..., 2].max(1)
    vy0, vy1 = vert[..., 1].min(1), vert[..., 1].max(1)
    stairs = b.stair_tiles() if hasattr(b, 'stair_tiles') else set()
    warps = warp_tiles(view)
    bad = []
    for t in sorted(reachable(b)):
        fy = view.feet_y(t) - 2
        for dx, dz, side in ((0, -1, 'north'), (-1, 0, 'west'), (1, 0, 'east')):
            u = (t[0] + dx, t[1] + dz)
            if u in b.walk or u in stairs or u in warps or u in opened or t in warps: continue
            if surface_heights(b, u): continue                     # floor / block top / furniture row beyond
            ex, ez = t[0] * 16 + 8 + dx * 8, t[1] * 16 + 8 + dz * 8   # edge midpoint
            if dz:
                m = (vx0 <= ex + 4) & (vx1 >= ex - 4) & (vz1 >= ez - 16) & (vz0 <= ez)
            else:
                m = (vz0 <= ez + 4) & (vz1 >= ez - 4) & ((vx1 >= ex) & (vx0 <= ex + 16) if dx > 0 else (vx0 <= ex) & (vx1 >= ex - 16))
            m &= (vy1 >= fy + 8) & (vy0 <= fy + 4)
            if not m.any(): bad.append((t, side))
    for t, side in bad:
        say('q', f'no wall on the {side} side of walkable Sapphire {b.sap(t)} (open to the black void)')

def surface_heights(b, t):
    """Heights of upward faces of the room's terrain and furniture over the tile's centre (a Poke Ball on a table top:
    models_interior "solid_y")."""
    x, z = t[0] * 16 + 8 - 256, t[1] * 16 + 8 - 256
    out = []
    for tex, P in list(b.terrain) + [tp for f in getattr(b, 'furn', []) for tp in f['tris']]:
        P = np.asarray(P, float)
        for tri in P:
            if not (tri[:, 0].min() <= x <= tri[:, 0].max() and tri[:, 2].min() <= z <= tri[:, 2].max()): continue
            n = np.cross(tri[1] - tri[0], tri[2] - tri[0])
            if np.linalg.norm(n) < 1e-9 or n[1] / np.linalg.norm(n) < 0.5: continue
            (ax, bx, cx), (az, bz, cz) = tri[:, 0], tri[:, 2]
            den = (bz - cz) * (ax - cx) + (cx - bx) * (az - cz)
            if abs(den) < 1e-9: continue
            w0 = ((bz - cz) * (x - cx) + (cx - bx) * (z - cz)) / den
            w1 = ((cz - az) * (x - cx) + (ax - cx) * (z - cz)) / den
            if w0 >= -1e-6 and w1 >= -1e-6 and w0 + w1 <= 1 + 1e-6:
                out.append(float(w0 * tri[0, 1] + w1 * tri[1, 1] + (1 - w0 - w1) * tri[2, 1]))
    return out

def reachable(b):
    seen, todo = set(), []
    V = {1: (0, 1), 2: (0, -1), 3: (1, 0), 4: (-1, 0)}
    for s in b.meta['warp_spots']:
        for st in s['tiles']:
            t = (st[0] + b.ox, st[1] + b.oz)
            v = V.get(s.get('dir'))
            out = [(t[0] - v[0], t[1] - v[1])] if v and t not in b.walk else []
            todo += [q for q in [t] + out + [(t[0] + a, t[1] + c) for a, c in ((0, 1), (0, -1), (1, 0), (-1, 0))] if q in b.walk]
    while todo:
        p = todo.pop()
        if p in seen: continue
        seen.add(p)
        todo += [q for q in ((p[0] + 1, p[1]), (p[0] - 1, p[1]), (p[0], p[1] + 1), (p[0], p[1] - 1)) if q in b.walk and q not in seen]
    return seen


def run(rooms_dir, names, cfgs, kinds, rom=None, built=None):
    """[(kind, line)] for kinds m, n (built: rooms_check's Built cache, a function name -> Built or None)."""
    import rooms_check_more as rcm
    out = []
    spr = Sprites(rom)
    objs = rcm.story_objects()
    for n in names:
        b = built(n) if built else None
        if b is None: continue
        try:
            v = View(b, cfgs.get(n), spr)
            check_room(v, objs.get(n, []), kinds, lambda k, msg: out.append((k, f'{n}: ({k}) {msg}')))
        except Exception as ex:
            out.append(('!', f'{n}: (!) check m/n failed: {type(ex).__name__}: {ex}'))
    return out


# ------------------------------------------------------------------------------------------------ render
def render(rooms_dir, name, cfg, sprites, player=None, story_objs=(), eye=None, target=None, hide_people=False, pdir=0):
    """The room from the game camera (camera centred on `player`, a zone tile, or the first NPC) with every person
    drawn as Black 2 draws them: a PIL image 256x192."""
    import preview_interior as pv
    import rooms_check as rc
    from PIL import Image
    b = rc.Built(rooms_dir, name, cfg)
    v = View(b, cfg, sprites)
    d = os.path.join(rooms_dir, name)
    tf = os.path.join(d, 'terrain_all.dae') if os.path.exists(os.path.join(d, 'terrain_all.dae')) else os.path.join(d, 'terrain.dae')
    parts = pv.parse(tf)
    names = {m['res']: m['name'] for m in b.meta['models']}; packs = {m['res']: m['pack'] for m in b.meta['models']}
    by_name = {nm: k for k, nm in names.items()}
    for f in b.meta['furniture']:
        res = f['m'] if isinstance(f['m'], int) else by_name[f['m']]
        parts += pv.placed(pv.furniture_parts(res, packs[res]), f['pos'], f['rot'])
    people = [] if hide_people else v.people(story_objs)
    if player is not None: people = people + [('player', player, PLAYER_CODE, pdir)]
    if eye is None:
        t = player if player is not None else (people[0][1] if people else (b.ox + 7, b.oz + 4))
        eye, target = camera_at(v.cam, v.box, t[0] * 16 + 8, v.feet_y(t), t[1] * 16 + 8)
    return draw(parts, people, v, eye, target, sprites)


def draw(parts, people, v, eye, target, sprites, zbuf=False):
    """Rasterise model-unit parts [(texture path, P, UV, C)] and the people [(label, zone tile, code, dir)] (billboards
    as Black 2 draws them) from (eye, target): PIL 256x192 (zbuf: also the depth buffer, inf where nothing is drawn)."""
    import preview_interior as pv
    from PIL import Image
    parts = [(tp, P + np.array([256.0, 0, 256.0]), UV, C) for tp, P, UV, C in parts]
    R = view_matrix(eye, target); eye = np.asarray(eye, float)
    img = np.zeros((H, W, 3), np.float32); zb = np.full((H, W), np.inf)
    for tp, P, UV, C in parts:
        T = pv.tex(tp)
        cam = (P - eye) @ R.T
        z = -cam[..., 2]
        ok = (z > 1).all(axis=1)
        sx = W / 2 + FX * cam[..., 0] / np.maximum(z, 1e-3); sy = H / 2 - FY * cam[..., 1] / np.maximum(z, 1e-3)
        for t in np.nonzero(ok)[0]:
            x0, x1 = int(max(0, math.floor(sx[t].min()))), int(min(W - 1, math.ceil(sx[t].max())))
            y0, y1 = int(max(0, math.floor(sy[t].min()))), int(min(H - 1, math.ceil(sy[t].max())))
            if x1 < x0 or y1 < y0: continue
            xs, ys = np.meshgrid(np.arange(x0, x1 + 1) + 0.5, np.arange(y0, y1 + 1) + 0.5)
            (ax, bx, cx), (ay, by, cy) = sx[t], sy[t]
            den = (by - cy) * (ax - cx) + (cx - bx) * (ay - cy)
            if abs(den) < 1e-9: continue
            w0 = ((by - cy) * (xs - cx) + (cx - bx) * (ys - cy)) / den
            w1 = ((cy - ay) * (xs - cx) + (ax - cx) * (ys - cy)) / den
            w2 = 1 - w0 - w1
            m = (w0 >= -1e-4) & (w1 >= -1e-4) & (w2 >= -1e-4)
            if not m.any(): continue
            iz = 1 / z[t]; q = w0 * iz[0] + w1 * iz[1] + w2 * iz[2]; dep = 1 / q
            sub = zb[y0:y1 + 1, x0:x1 + 1]
            m &= dep < sub
            if not m.any(): continue
            uu = (w0 * UV[t, 0, 0] * iz[0] + w1 * UV[t, 1, 0] * iz[1] + w2 * UV[t, 2, 0] * iz[2]) / q
            vv = (w0 * UV[t, 0, 1] * iz[0] + w1 * UV[t, 1, 1] * iz[1] + w2 * UV[t, 2, 1] * iz[2]) / q
            col = (w0[..., None] * C[t, 0] + w1[..., None] * C[t, 1] + w2[..., None] * C[t, 2])
            if T is not None:
                th, tw = T.shape[:2]
                s = T[np.floor((1 - vv) * th).astype(int) % th, np.floor(uu * tw).astype(int) % tw]
                m &= s[..., 3] > 100
                rgb = s[..., :3] * col
            else:
                rgb = 255 * col
            reg = img[y0:y1 + 1, x0:x1 + 1]
            reg[m] = rgb[m]; sub[m] = dep[m]
    if True:
        # billboards, back to front, with the depth test (and the 0.076-unit object bias)
        bl = []
        for who, t, code, d in people:
            fr = sprites.frame(code, d)
            if fr is None: continue
            fy = v.feet_y(t)
            c = R @ (np.array([t[0] * 16 + 8, fy + ANCHOR_Y.get(v.cam, ANCHOR_Y[0]), t[1] * 16 + 8]) - eye)
            bl.append((-c[2], c, fr))
        for zq, c, (mask, rgb) in sorted(bl, key=lambda q: -q[0]):
            fh, fw = mask.shape; qw, qh = QUAD * fw / 32, QUAD * fh / 32
            sx0, sx1 = W / 2 + FX * (c[0] - qw / 2) / zq, W / 2 + FX * (c[0] + qw / 2) / zq
            sy0, sy1 = H / 2 - FY * (c[1] + qh) / zq, H / 2 - FY * c[1] / zq
            X0, X1 = max(0, int(math.floor(sx0))), min(W, int(math.ceil(sx1)))
            Y0_, Y1 = max(0, int(math.floor(sy0))), min(H, int(math.ceil(sy1)))
            if X1 <= X0 or Y1 <= Y0_: continue
            gx, gy = np.meshgrid(np.arange(X0, X1) + 0.5, np.arange(Y0_, Y1) + 0.5)
            u = ((gx - sx0) / (sx1 - sx0) * fw).astype(int).clip(0, fw - 1)
            vv = ((gy - sy0) / (sy1 - sy0) * fh).astype(int).clip(0, fh - 1)
            m = mask[vv, u] & (zq * v.bias < zb[Y0_:Y1, X0:X1])
            reg = img[Y0_:Y1, X0:X1]; reg[m] = rgb[vv, u][m]
            zb[Y0_:Y1, X0:X1][m] = zq * v.bias
    im = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))
    return (im, zb) if zbuf else im


def main():
    import rooms_check as rc, rooms_check_more as rcm
    ap = argparse.ArgumentParser()
    ap.add_argument('--dir', default=os.environ.get('HOENN_INTERIORS_DIR') or os.path.join(ROOT, 'work', 'interiors'))
    ap.add_argument('--rom'); ap.add_argument('--kinds', default='mnopq'); ap.add_argument('--summary', action='store_true')
    ap.add_argument('--render'); ap.add_argument('--b2', action='store_true'); ap.add_argument('rooms', nargs='*')
    a = ap.parse_args()
    os.environ['HOENN_INTERIORS_DIR'] = os.path.abspath(a.dir)
    if a.b2:                         # Black 2's own rooms (zone numbers; none = every 1x1 interior zone): the baseline
        import preview_interior as pv, zoneheaders, b2files
        from models_interior import FILES
        cache = os.path.join(a.dir, '_b2rooms'); pv.OUT = os.environ.get('ROOMS_CHECK_MODELS') or a.dir
        H = zoneheaders.parse(b2files.narc_entries(b2files.arc_path(FILES, 12))[0])
        mats = b2files.narc_entries(b2files.arc_path(FILES, 9))
        zs = [int(z) for z in a.rooms] or [z for z, h in enumerate(H) if h['map_type'] == 16 and
                                            struct.unpack_from('<HHHH', mats[h['matrix']], 0)[0::2] == (0, 1)
                                            and struct.unpack_from('<HHHH', mats[h['matrix']], 0)[3] == 1]
        spr, out = Sprites(a.rom), []
        for z in zs:
            try: out += b2_check(z, cache, spr, a.kinds.replace('p', '').replace('q', '').replace('o', ''))
            except Exception as ex: out.append(('!', f'B2 zone {z}: (!) {type(ex).__name__}: {ex}'))
        for _, ln in out: print(ln)
        return
    cfgs = rc.zone_cfgs()
    if a.render:
        name = a.rooms[0]; cfg = cfgs.get(name)
        b0 = rc.Built(a.dir, name, cfg)
        player = None
        if len(a.rooms) > 1:
            sx, sz = map(int, a.rooms[1].split(',')); player = b0.zt((sx, sz))
        im = render(a.dir, name, cfg, Sprites(a.rom), player, rcm.story_objects().get(name, []))
        im.save(a.render); print(a.render); return
    names = a.rooms or sorted(d for d in os.listdir(a.dir) if os.path.exists(os.path.join(a.dir, d, 'room.json'))
                              and os.path.exists(os.path.join(ROOT, 'data', 'interior_layouts', d + '.json')))
    cache = {}
    def built(n):
        if n not in cache:
            try: cache[n] = rc.Built(a.dir, n, cfgs.get(n))
            except Exception: cache[n] = None
        return cache[n]
    out = run(a.dir, names, cfgs, a.kinds, a.rom, built)
    if a.summary:
        c = Counter(k for k, _ in out); rooms = defaultdict(set)
        for k, ln in out: rooms[k].add(ln.split(':')[0])
        for k in sorted(c): print(f'{k}: {c[k]} findings in {len(rooms[k])} rooms')
    else:
        for _, ln in out: print(ln)



# ------------------------------------------------------------------------------------------------ Black 2's own rooms
class B2Room:
    """A Black 2 interior zone with one chunk (its terrain, buildings, collision, NPCs, camera box), shaped like
    rooms_check.Built for View: the baseline of what Black 2 itself shows (python3 rooms_view.py --b2 ZONE ...)."""
    def __init__(self, zone, cache_dir):
        import subprocess, zoneheaders, b2files, zones
        import preview_interior as pv
        from models_interior import FILES
        hd = zoneheaders.parse(b2files.narc_entries(b2files.arc_path(FILES, 12))[0])[zone]
        self.zone, self.hd = zone, hd
        mat = b2files.narc_entries(b2files.arc_path(FILES, 9))[hd['matrix']]
        fmt, _, mw, mh = struct.unpack_from('<HHHH', mat, 0)
        assert fmt == 0 and (mw, mh) == (1, 1), f'zone {zone}: matrix {mw}x{mh} format {fmt}'
        chunk = struct.unpack_from('<I', mat, 8)[0]
        ar = b2files.area(FILES, hd['area'])
        d = os.path.join(cache_dir, f'b2chunk_{chunk}')
        if not os.path.isdir(os.path.join(d, 'dae')):
            os.makedirs(d, exist_ok=True)
            open(os.path.join(d, 't.nsbmd'), 'wb').write(b2files.chunk(FILES, chunk)[1][0])
            open(os.path.join(d, 'tex.nsbtx'), 'wb').write(b2files.map_textures(FILES, ar['texset']))
            subprocess.run([pv.APICULA, 'convert', os.path.join(d, 't.nsbmd'), os.path.join(d, 'tex.nsbtx'), '-o',
                            os.path.join(d, 'dae'), '-f', 'dae'], capture_output=True)
        dae = next(f for f in os.listdir(os.path.join(d, 'dae')) if f.endswith('.dae'))
        self.terrain = [(os.path.basename(tp or 'none')[:-4], P) for tp, P, UV, C in pv.parse(os.path.join(d, 'dae', dae))]
        self.parts_path = os.path.join(d, 'dae', dae)
        pack = {r['res_id']: r['name'] for r in b2files.building_pack(FILES, ar['pack'], exterior=False)}
        self.furn = []
        self.placements = b2files.chunk_buildings(FILES, chunk)
        for k, bl in enumerate(self.placements):
            parts = pv.placed(pv.furniture_parts(bl['res_id'], ar['pack']), (bl['x'], bl['y'], bl['z']), bl['rot'])
            self.furn.append(dict(k=k, name=pack.get(bl['res_id'], str(bl['res_id'])), rot=bl['rot'],
                                  pos=(bl['x'], bl['y'], bl['z']), tris=[(os.path.basename(tp or '-')[:-4], P) for tp, P, UV, C in parts]))
        self.pack = ar['pack']
        per = b2files.chunk(FILES, chunk)[1][1]
        self.cells = {(i % 32, i // 32): struct.unpack_from('<HHHH', per, 4 + 8 * i) for i in range(1024)}
        self.walk = {t for t, c in self.cells.items() if not c[3] & 1}
        cam = b2files.narc_entries(b2files.arc_path(FILES, 109))[hd['cam_bound']] if hd['cam_bound'] != 0xFFFF else None
        box = list(struct.unpack_from('<4i', cam, 12)) if cam else [0, 512, 0, 512]
        self.ents = zones.entities(hd['entities'])
        spots = [dict(kind='warp', tiles=[[w['tile_x'] + i, w['tile_z'] + j] for i in range(max(1, w['w'])) for j in range(max(1, w['h']))],
                      dir=w['dir']) for w in self.ents['warps']]
        self.meta = dict(camera=box, warp_spots=spots, origin=[0, 0])
        self.ox = self.oz = 0
    def label(self, f): return f"{f['name']}#{f['k']}"
    def zt(self, s): return tuple(s)
    def sap(self, t): return tuple(t)
    def stair_tiles(self): return set()
    def plane_y(self, c, x, z):
        import models_interior as mi
        h = mi.heights()
        nx, ny, nz = h.NORMALS[c[0] >> 2]; d = h.OFFS[c[1]]
        return -(nx * ((x % 512) - 256) - nz * ((z % 512) - 256) + d) / ny

def b2_check(zone, cache_dir, sprites, kinds='m'):
    b = B2Room(zone, cache_dir)
    w = b.hd['weather_word']
    cfg = dict(zone=zone, npcs=[dict(uid=n['uid'], model=n['model'], dir=n['dir'], at=[n['x'], n['z']],
                                     _what=f'B2 model {n["model"]}') for n in b.ents['npcs'] if n['y'] == 0])
    v = View(b, cfg, sprites)
    v.cam, v.proj = w >> 9, (w >> 6) & 7
    v.bias = DEPTH_K.get(v.cam, DEPTH_K[0])
    out = []
    check_room(v, [], kinds, lambda k, msg: out.append((k, f'B2 zone {zone}: ({k}) {msg}')))
    return out

def b2_render(zone, cache_dir, sprites, player=None, pdir=0):
    """Black 2's own room `zone` from its camera with its NPCs (+ the player at zone tile `player`): PIL 256x192."""
    import preview_interior as pv
    from PIL import Image
    b = B2Room(zone, cache_dir)
    w = b.hd['weather_word']
    cfg = dict(zone=zone, npcs=[dict(uid=n['uid'], model=n['model'], dir=n['dir'], at=[n['x'], n['z']]) for n in b.ents['npcs'] if n['y'] == 0])
    v = View(b, cfg, sprites); v.cam, v.proj = w >> 9, (w >> 6) & 7; v.bias = DEPTH_K.get(v.cam, DEPTH_K[0])
    parts = pv.parse(b.parts_path)
    for bl in b.placements:
        parts += pv.placed(pv.furniture_parts(bl['res_id'], b.pack), (bl['x'], bl['y'], bl['z']), bl['rot'])
    people = v.people() + ([('player', player, PLAYER_CODE, pdir)] if player else [])
    t = player or people[0][1]
    eye, target = camera_at(v.cam, v.box, t[0] * 16 + 8, v.feet_y(t), t[1] * 16 + 8)
    return draw(parts, people, v, eye, target, sprites)


if __name__ == '__main__':
    main()
