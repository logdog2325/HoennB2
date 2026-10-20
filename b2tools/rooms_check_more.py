"""More checks for the built rooms (sweep_rooms agent, 2026-10-07): the kinds rooms_check.py lacked. rooms_check.py
runs them with its own (kinds h-l, part of its default); alone:

    python3 rooms_check_more.py [--dir ROOMS] [--rom ROM] [--world WORLD_DIR] [--kinds hijkl] [--summary] [ROOM ...]

Kinds (what the player sees in the game):
  h  black in the room: a thin wall (<= 2 tiles) between two floors that Sapphire draws as a wall or partition (its
     metatile is light) but the room leaves black (the builder's black wall cap or the void: a black slab between the
     floors from the camera; the recipe key "inner_walls" draws them as light-topped blocks), and terrain faces turned
     away from the camera (culled: nothing is drawn there). Black void in Sapphire (gaps between the Abandoned Ship's
     cabins) and rooms floating in the dark on purpose ("open": true) are not counted.
  i  textures: every terrain material has its image, every chunk fits the field's 110,600-byte buffer; with --rom, for each room zone: every room texture is in the zone
     area's map texture set(s) WITH THE BYTES OF ITS SOURCE SET (nsbtx.merge keeps a same-named texture already in the
     set, so the room would show that one instead), every furniture model is in the area's interior pack under its res
     id with the same model name, and each of its textures/palettes is in the pack's texture set with its source bytes
     (missing: drawn white/untextured; different: another model's look)
  j  exits: b2tools/check_exits.py (a room exit that leads to the wrong outdoor door, or a wrong dynamic warp); room-to-
     room differences are listed as "(j) info"
  k  story people: data/story/*.json NPCs in rooms (trainers, scene people) on solid tiles, inside furniture or on the
     same tile as another person shown at the same time; triggers on tiles nobody can step on (they never fire)
  l  floor: a walkable tile reachable from the warps with nothing drawn under it at its collision height (water, raised
     levels and ramps included)
"""
import os, sys, re, json, glob, math, struct, argparse
from collections import defaultdict, Counter
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, 'patches'))
import version  # noqa: E402  (HOENN_VERSION=ruby: the ruby/ overlays of data/interiors, data/story; notes/RUBY.md)
T, Y0, YW = 16, -2, 48
ROOMS_JSON = json.load(open(os.path.join(ROOT, 'data', 'hoenn_interiors.json')))['rooms']


def _faces(path):
    """[(texture name, tri 3x3, mean colour)] of a built terrain DAE."""
    import preview_interior as pv
    out = []
    for tp, P, UV, C in pv.parse(path):
        tex = os.path.basename(tp or 'none')[:-4]
        for t, c in zip(P, C): out.append((tex, np.asarray(t, float), float(np.asarray(c).mean())))
    return out


class Room:
    """What the checks need of one built room (terrain faces, collision, warps)."""
    def __init__(self, rooms_dir, name, built=None):
        self.name, self.d = name, os.path.join(rooms_dir, name)
        self.meta = json.load(open(os.path.join(self.d, 'room.json')))
        self.ox, self.oz = self.meta['origin']
        tf = os.path.join(self.d, 'terrain_all.dae')
        self.faces = _faces(tf if os.path.exists(tf) else os.path.join(self.d, 'terrain.dae'))
        self.built = built                                  # rooms_check.Built (collision, furniture, plane_y)
        self.out = []
        try:
            import models_interior as mi
            self.recipe = mi.load_recipe(name)
        except Exception:
            self.recipe = {}

    def say(self, kind, msg): self.out.append((kind, f'{self.name}: ({kind}) {msg}'))
    def sap(self, t): return (t[0] - self.ox, t[1] - self.oz)

    # horizontal faces (any height) as (x0, x1, z0, z1, y, tex, black, tri) in zone units
    def flats(self):
        if not hasattr(self, '_flats'):
            fl = []
            for tex, t, c in self.faces:
                n = np.cross(t[1] - t[0], t[2] - t[0]); l = np.linalg.norm(n)
                if l < 1e-6 or abs(n[1]) / l < 0.5: continue        # floors, ramps, water, block tops, caps
                xs, zs = t[:, 0] + 256, t[:, 2] + 256
                fl.append((xs.min(), xs.max(), zs.min(), zs.max(), float(t[:, 1].mean()), tex, c < 0.05, t))
            self._flats = fl
        return self._flats

    def surface_at(self, x, z, ymin=-99, ymax=YW - 4, black=False, skip=()):
        """Heights of the non-black (black=False) horizontal faces covering zone point (x, z) (units), textures in skip
        left out."""
        out = []
        for x0, x1, z0, z1, y, tex, blk, t in self.flats():
            if blk != black or not (x0 - 1e-6 <= x <= x1 + 1e-6 and z0 - 1e-6 <= z <= z1 + 1e-6): continue
            if tex in skip and y < Y0 + 6: continue           # a rug (not a high cap like the Centers' pillar tops)
            (ax, bx, cx), (az, bz, cz) = t[:, 0] + 256, t[:, 2] + 256
            den = (bz - cz) * (ax - cx) + (cx - bx) * (az - cz)
            if abs(den) < 1e-9: continue
            w0 = ((bz - cz) * (x - cx) + (cx - bx) * (z - cz)) / den
            w1 = ((cz - az) * (x - cx) + (ax - cx) * (z - cz)) / den
            if w0 >= -1e-6 and w1 >= -1e-6 and w0 + w1 <= 1 + 1e-6:
                y = w0 * t[0, 1] + w1 * t[1, 1] + (1 - w0 - w1) * t[2, 1]
                if ymin <= y <= ymax: out.append(y)
        return out

    def floor_tiles(self):
        """Zone tiles with a non-black floor-ish face over their centre."""
        if not hasattr(self, '_ft'):
            xs = [f[0] for f in self.flats()] + [f[1] for f in self.flats()]
            zs = [f[2] for f in self.flats()] + [f[3] for f in self.flats()]
            ft = set()
            mats = {m['tex'] for m in self.recipe.get('mats', []) if isinstance(m, dict) and 'tex' in m}
            for X in range(int(min(xs)) // T, int(max(xs)) // T + 1):
                for Z in range(int(min(zs)) // T, int(max(zs)) // T + 1):
                    # covered at its centre and 2 units in from each edge (not the builder's 12-unit back strip or
                    # 3-unit side strips of a wall's floor); block tops count
                    # (the recipe's rugs and mats don't make a floor: a door mat in a wall row)
                    if all(self.surface_at(X * T + a, Z * T + b, ymax=YW + 4, skip=mats) for a, b in ((8, 8), (8, 2), (8, 14), (2, 8), (14, 8))):
                        ft.add((X, Z))
            self._ft = ft
        return self._ft

    # -------------------------------------------------------------------------------------------- (h) black
    def check_black(self):
        import models_interior as mi
        r = self.recipe
        if r.get('open') is True: return                  # floating in the dark on purpose
        # 1. thin walls between two floors that Sapphire draws as walls (light metatiles) but the room leaves without
        #    floor or block top: the builder's black cap / the void shows there (models_interior.inner_wall_tiles,
        #    the rule the recipe key "inner_walls" fixes them with). Black void in Sapphire (the Abandoned Ship's gaps
        #    between cabins) is not counted.
        ft = {self.sap(t) for t in self.floor_tiles()}
        # (sweep_rooms 2026-10-11) a stairs tile is drawn by its stair model (not in the terrain faces read here): not
        # black. The ship corridor 1F's stairs (6,2) read as a partition once the broken-wall blob (8,2) beyond Sapphire's
        # black column became a light-topped block (a 'floor' end for the run)
        stairs = {tuple(f['stair']) for f in r.get('furniture', []) if isinstance(f, dict) and 'stair' in f}
        for comp in _components(mi.inner_wall_tiles(self.meta['map'], ft, 2, 100) - stairs):
            s = sorted(comp)
            ns = any(((x, z - 1) in ft or (x, z - 2) in ft) and ((x, z + 1) in ft or (x, z + 2) in ft) for x, z in comp)
            if not ns and max(z for _, z in comp) - min(z for _, z in comp) < 1:
                continue                      # a one-row jog of a wall between two recesses (doors, stairs)
            self.say('h', f'black between floors where Sapphire draws a wall/partition: Sapphire {s[:6]}{" ..." if len(s) > 6 else ""} ({len(s)} tiles)')
        # 3. faces turned away from the camera (DS back-face culling: not drawn)
        bad = Counter()
        for tex, t, c in self.faces:
            n = np.cross(t[1] - t[0], t[2] - t[0]); l = np.linalg.norm(n)
            if l < 1e-6: continue
            n = n / l
            if n[1] < -0.5 and c > 0.05: bad[(tex, 'down')] += 1      # (north-facing faces are never seen anyway)
        for (tex, d), k in sorted(bad.items()):
            self.say('h', f'{k} {tex} faces turn {d} (away from the camera: culled, not drawn)')

    # -------------------------------------------------------------------------------------------- (i) textures
    def check_textures_static(self):
        for tex in self.meta.get('map_textures', {}):
            if not os.path.exists(os.path.join(self.d, tex + '.png')):
                self.say('i', f'terrain texture {tex} has no image in the built room')
        for m in self.meta.get('models', []):
            if 'file' in m and not os.path.exists(os.path.join(self.d, m['file'])):
                self.say('i', f'model {m["name"]} ({m["res"]}): {m["file"]} missing')
        # chunk size: map type 16 loads each chunk into a 110,600-byte buffer (patches/interiors.py chunk_container): a
        # bigger one hangs the field on a black screen
        for c in (self.meta.get('chunks') or [self.meta]):
            if not c: continue
            fs = [os.path.join(self.d, c[k]) for k in ('terrain', 'collision', 'collision1', 'placements') if c.get(k)]
            if all(os.path.exists(f) for f in fs):
                n = 4 + 4 * (len(fs) + 1) + sum(os.path.getsize(f) for f in fs)
                if n > 0x1b008: self.say('i', f'chunk {c["terrain"]}: {n} bytes > 110600 (the field hangs on a black screen)')

    # -------------------------------------------------------------------------------------------- (k) story people
    def check_story(self, objs, cfg):
        b = self.built
        if b is None: return
        stairs = b.stair_tiles()
        people = []                                      # (zone tile, flag, label)
        for i, n in enumerate((cfg or {}).get('npcs', [])):
            if 'at' in n: people.append((b.zt(n['at']), n.get('flag', 0), f'room NPC {i} uid {n.get("uid")}', None))
        sm = b.sm
        for src, o in objs:
            if o.get('kind') == 'npc':
                if 'at' not in o: continue
                t = b.zt(o['at']); who = f'{src} NPC uid {o.get("uid")} ({(o.get("what") or "")[:50]})'
                people.append((t, o.get('flag', 0), who, o))
                if t in stairs: continue
                sx, sz = o['at']
                sap_walk = 0 <= sz < sm['h'] and 0 <= sx < sm['w'] and sm['walk'][sz][sx]
                if t not in b.walk:
                    c = b.cells.get(t)
                    if c is None: self.say('k', f'{who} at Sapphire {tuple(o["at"])} stands outside the room')
                    elif sap_walk: self.say('k', f'{who} at Sapphire {tuple(o["at"])} stands on a solid tile (class {c[2]:#x}) that Sapphire lets you walk on')
                    else: self.say('k', f'{who} at Sapphire {tuple(o["at"])} stands on a solid tile (as in Sapphire)')
                c = b.cells.get(t)
                feet = b.plane_y(c, t[0] * 16 + 8, t[1] * 16 + 8) if c else 0      # (Black 2 snaps actors to their tile's
                for f in b.furn:                                                   #  height: a table top, "solid_y")
                    frac, centre = b.covers(f, t)
                    top = max((float(P[:, :, 1].max()) for _, P in f['tris'] if len(P)), default=0)   # (placed: world y)
                    if centre and feet > 1 and feet >= top - 4: continue        # (standing on it)
                    if centre: self.say('k', f'{who} at Sapphire {tuple(o["at"])} stands inside {b.label(f)} ({frac:.0%} of the tile)')
            elif o.get('kind') == 'trigger' and 'at' in o:
                w, h = o.get('w', 1), o.get('h', 1)
                tiles = [b.zt((o['at'][0] + i, o['at'][1] + j)) for i in range(w) for j in range(h)]
                if not any(t in b.walk or t in stairs for t in tiles):
                    self.say('k', f'{src} trigger at Sapphire {tuple(o["at"])} {w}x{h} (script {o.get("script")}): no tile of it can be stepped on')
        # two people on one tile shown together (no flag on either: both always there)
        seen = defaultdict(list)
        for t, flag, who, o in people: seen[t].append((flag, who))
        for t, lst in seen.items():
            if len(lst) > 1 and sum(1 for f, _ in lst if not f) > 1:
                self.say('k', f'{len(lst)} people on Sapphire {self.sap(t)} without hide flags: {"; ".join(w for _, w in lst)[:160]}')

    # -------------------------------------------------------------------------------------------- (l) floor
    def check_floor(self, cfg=None):
        b = self.built
        if b is None: return
        # a pit you fall through: a recipe "holes" tile with a step trigger on it (Mt. Pyre's holes, b2tools/
        # facilities_pyre.py): nothing is drawn there on purpose, its trigger falls to the floor below as you step on
        pits = {(x, z) for x0, z0, x1, z1 in self.recipe.get('holes', [])
                for x in range(math.floor(x0), math.ceil(x1)) for z in range(math.floor(z0), math.ceil(z1))}
        falls = pits & {tuple(t['at']) for t in (cfg or {}).get('triggers', []) if 'at' in t}
        seen, todo = set(), []
        V = {1: (0, 1), 2: (0, -1), 3: (1, 0), 4: (-1, 0)}           # Black 2 warp dir -> the way you walk in
        for s in self.meta['warp_spots']:
            for st in s['tiles']:
                t = (st[0] + self.ox, st[1] + self.oz)
                v = V.get(s.get('dir'))
                out = [(t[0] - v[0], t[1] - v[1])] if v and t not in b.walk else []   # stepping out of a solid warp tile
                todo += [q for q in [t] + out + ([(t[0] + a, t[1] + c) for a, c in ((0, 1), (0, -1), (1, 0), (-1, 0))]
                                                  if t in b.walk else []) if q in b.walk]
        while todo:
            p = todo.pop()
            if p in seen: continue
            seen.add(p)
            todo += [q for q in ((p[0] + 1, p[1]), (p[0] - 1, p[1]), (p[0], p[1] + 1), (p[0], p[1] - 1)) if q in b.walk and q not in seen]
        bad = []
        for p in sorted(seen):
            c = b.cells[p]
            try: h = b.plane_y(c, p[0] * T + 8, p[1] * T + 8)
            except Exception: h = 0
            if not self.surface_at(p[0] * T + 8, p[1] * T + 8, ymin=h - 12, ymax=h + 3) and self.sap(p) not in falls:
                bad.append(p)
        for comp in _components(set(bad)):
            s = sorted(self.sap(t) for t in comp)
            self.say('l', f'walkable tiles with nothing drawn at their height: Sapphire {s[:6]}{" ..." if len(s) > 6 else ""} ({len(s)} tiles)')


def _components(tiles):
    tiles, out = set(tiles), []
    while tiles:
        st = [tiles.pop()]; comp = set(st)
        while st:
            p = st.pop()
            for q in ((p[0] + 1, p[1]), (p[0] - 1, p[1]), (p[0], p[1] + 1), (p[0], p[1] - 1)):
                if q in tiles: tiles.discard(q); comp.add(q); st.append(q)
        out.append(comp)
    return sorted(out, key=lambda c: min(c))


# ------------------------------------------------------------------------------------------------ (i) with a ROM
def _btx_items(btx):
    """{texture name: bytes}, {palette name: bytes} of a BTX0 (as nsbtx.merge copies them)."""
    import nsbtx
    S = nsbtx._parse(btx)
    tex = {}
    for n, (params, extra) in S['texs']:
        raw, idx = nsbtx._tex_bytes(S, params)
        tex[n] = (params & ~0xFFFF, raw, idx)
    pal = {n: S['pdata'][o << 3:(o << 3) + nsbtx._pal_size(S, n)] for n, (o, f) in S['pals']}
    return tex, pal

def check_rom_textures(rom, rooms_dir, names):
    import interior_sweep_check as isc, zoneheaders, b2files, nsbtx
    from patches.interiors import _pack_sections
    out = []
    hdrs = zoneheaders.parse(isc.nds_narc(rom, 12)[0])
    area_raw = isc.nds_file(rom, 'a/0/1/3')
    texsets, btex, packs = isc.nds_narc(rom, 14), isc.nds_narc(rom, 175), isc.nds_narc(rom, 226)
    files = os.path.join(ROOT, 'external', 'pokebw2', 'build', 'b2_us', 'files')
    cache = {}
    def items(kind, i, data):
        k = (kind, i)
        if k not in cache: cache[k] = _btx_items(data)
        return cache[k]
    src_map = lambda s: items('srcmap', s, b2files.map_textures(files, s))
    src_btex = lambda p: items('srcbtex', p, b2files.building_textures(files, p, exterior=False))
    import models_interior as mi
    by_name, by_res = mi.interior_models()
    for f in version.overlay(os.path.join(ROOT, 'data', 'interiors'), '*.json'):
        cfg = json.load(open(f))
        name = cfg.get('room')
        if not name or (names and name not in names): continue
        rd = os.path.join(rooms_dir, name)
        if not os.path.exists(os.path.join(rd, 'room.json')): continue
        metas = [json.load(open(os.path.join(rd, 'room.json')))]
        for alt in cfg.get('alt_rooms', []):
            p = os.path.join(rooms_dir, alt['room'], 'room.json')
            if os.path.exists(p): metas.append(json.load(open(p)))
        hd = hdrs[cfg['zone']]
        pack, texset, _, _, ext = struct.unpack_from('<HHBBB', area_raw, hd['area'] * 10)
        seasons = 4 if 2 <= hd['area'] <= 281 else 1
        say = lambda msg: out.append(('i', f'{name}: (i) {msg}'))
        rt0, _ = items('rommap', texset, texsets[texset])
        miss = [t for t in metas[0]['map_textures'] if t not in rt0]
        if len(miss) >= max(3, len(metas[0]['map_textures']) / 2):
            say(f'probably not installed in this ROM ({len(miss)} of its {len(metas[0]["map_textures"])} textures are not in the area '
                f'{hd["area"]} set): built after the ROM, or left out (HOENN_SKIP_UNBUILT_ROOMS)?'); continue
        for meta in metas:
            for tex, src in meta['map_textures'].items():
                # (["gen3", map, x, y]: a texture drawn from a Gen 3 metatile, Mauville Gym's switches: no Black 2 set to
                #  compare it with, only its presence is checked; it crashed the Emerald release report, league_door)
                st, sp = src_map(src) if isinstance(src, int) else (None, {})
                for s in range(seasons):
                    rt, rp = items('rommap', texset + s, texsets[texset + s])
                    if tex not in rt: say(f'texture {tex} (set {src}) is not in the area {hd["area"]} map texture set {texset + s}: drawn untextured'); continue
                    if st is not None and rt[tex] != st.get(tex): say(f'texture {tex}: the area {hd["area"]} set {texset + s} has another texture under this name (the room shows that one, not set {src}\'s)')
                    pl = tex + '_pl'
                    if pl in sp and rp.get(pl) != sp[pl]: say(f'palette {pl}: the area set {texset + s} has other colours under this name')
            infos, bmds = _pack_sections(packs[pack])
            have = {}
            for info, bmd in zip(infos, bmds):
                have.setdefault(struct.unpack_from('<H', info, 0)[0], bmd)
            bt, bp = items('rombtex', pack, btex[pack])
            for m in meta.get('models', []) + meta.get('extra_models', []):
                bmd = have.get(m['res'])
                if bmd is None: say(f'model {m["name"]} (res {m["res"]}) is not in the area\'s interior pack {pack}: not drawn'); continue
                nm = b2files.nitro_names(bmd)
                want = m['name'] if m['name'] not in mi.DERIVED_MODELS else mi.DERIVED_MODELS[m['name']][0]
                if nm and nm[0] != want and 'file' not in m:
                    say(f'res {m["res"]} in pack {pack} is model {nm[0]}, the room wants {m["name"]} (the wrong model is drawn)')
                if 'file' in m and 'base' not in m:      # a new model (its textures from map sets)
                    srcs = {t: src_map(s) for t, s in m.get('textures', {}).items()}
                else:
                    srcs = None
                    st, sp = src_btex(m['pack'])
                for t, p in sorted(nsbtx.material_pairs(bmd), key=str):
                    if not t: continue
                    if srcs is not None: st, sp = srcs.get(t, ({}, {}))
                    if t not in bt: say(f'model {m["name"]}: texture {t} is not in pack {pack}\'s texture set: drawn untextured'); continue
                    if t in st and bt[t] != st[t]: say(f'model {m["name"]}: texture {t} in pack {pack}\'s set is another texture of that name')
                    if p and p not in bp: say(f'model {m["name"]}: palette {p} is not in pack {pack}\'s texture set')
                    elif p and p in sp and bp[p] != sp[p]: say(f'model {m["name"]}: palette {p} in pack {pack}\'s set has other colours')
    return out


# ------------------------------------------------------------------------------------------------ (j) exits
def check_exit_list(world_dir, names):
    import check_exits
    bad, info, n = check_exits.check(world_dir)
    out = []
    for name, zone, i, to, want, owner in bad:
        if names and name not in names: continue
        out.append(('j', f'{name}: (j) exit warp {i} (zone {zone}) leads to {to}, Sapphire\'s door is {want} ({owner})'))
    for name, zone, i, to, want, owner in info:
        if names and name not in names: continue
        out.append(('j-info', f'{name}: (j) info: warp {i} (zone {zone}) to {to}, Sapphire\'s room warp {want} ({owner})'))
    return out


# ------------------------------------------------------------------------------------------------ run
def story_objects():
    """{room name: [(file, object)]} of data/story/*.json objects in rooms."""
    out = defaultdict(list)
    em = version.variants() if version.is_emerald() else {}
    for f in version.overlay(os.path.join(ROOT, 'data', 'story'), '*.json'):
        try: d = json.load(open(f))
        except Exception: continue
        for o in d.get('objects', []):
            if em:                      # (emerald_rooms) Emerald: the object as Emerald places it, in the room's variant
                o = version.version_object(o)
                if o is None: continue
                if o.get('map') in em: out[em[o['map']]].append((os.path.basename(f)[:-5], o)); continue
            if o.get('map') in ROOMS_JSON: out[o['map']].append((os.path.basename(f)[:-5], o))
    return out

def run(rooms_dir, names, cfgs, kinds, rom=None, built=None, world=None):
    """[(kind, line)] for kinds in h, i, j, k, l (built: rooms_check's Built cache, a function name -> Built or None)."""
    out = []
    objs = story_objects() if 'k' in kinds else {}
    for n in names:
        try:
            r = Room(rooms_dir, n, built(n) if built else None)
        except Exception as ex:
            out.append(('!', f'{n}: (!) cannot read the built room: {type(ex).__name__}: {ex}')); continue
        for k, fn in (('h', r.check_black), ('i', r.check_textures_static), ('l', lambda: r.check_floor(cfgs.get(n))),
                      ('k', lambda: r.check_story(objs.get(n, []), cfgs.get(n)))):
            if k in kinds:
                try: fn()
                except Exception as ex: r.say('!', f'check {k} failed: {type(ex).__name__}: {ex}')
        out += r.out
    if 'i' in kinds and rom:
        out += check_rom_textures(rom, rooms_dir, set(names))
    if 'j' in kinds:
        wd = world or os.environ.get('HOENN_WORLD_DIR') or os.path.join(ROOT, 'work', 'world')
        out += check_exit_list(wd, set(names))
    return out

def main():
    import rooms_check as rc
    ap = argparse.ArgumentParser()
    ap.add_argument('--dir', default=os.environ.get('HOENN_INTERIORS_DIR') or os.path.join(ROOT, 'work', 'interiors'))
    ap.add_argument('--rom'); ap.add_argument('--world'); ap.add_argument('--kinds', default='hijkl')
    ap.add_argument('--summary', action='store_true'); ap.add_argument('rooms', nargs='*')
    a = ap.parse_args()
    os.environ['HOENN_INTERIORS_DIR'] = os.path.abspath(a.dir)
    cfgs = rc.zone_cfgs()
    names = a.rooms or sorted(d for d in os.listdir(a.dir) if os.path.exists(os.path.join(a.dir, d, 'room.json'))
                              and os.path.exists(os.path.join(ROOT, 'data', 'interior_layouts', d + '.json')))
    cache = {}
    def built(n):
        if n not in cache:
            try: cache[n] = rc.Built(a.dir, n, cfgs.get(n))
            except Exception: cache[n] = None
        return cache[n]
    out = run(a.dir, names, cfgs, a.kinds, a.rom, built, a.world)
    if a.summary:
        c = Counter(k for k, _ in out); rooms = defaultdict(set)
        for k, ln in out: rooms[k].add(ln.split(':')[0])
        for k in sorted(c): print(f'{k}: {c[k]} findings in {len(rooms[k])} rooms')
    else:
        for _, ln in out: print(ln)

if __name__ == '__main__':
    main()
