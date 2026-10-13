"""houses agent: room recipes for every gTileset_GenericBuilding room, written from Sapphire's metatiles.

    python3 gen_interior_recipes_houses.py [MAP ...]          (default: all 74 rooms of the family)
    python3 gen_interior_recipes_houses.py --check [MAP ...]  print what would be written, write nothing

Reads data/interior_tiles_houses.json (Sapphire metatile -> Black 2 room part) and Sapphire's map (layout, collision,
behaviours, events) and writes, per room:
  data/interior_layouts/<Map>.json   recipe for b2tools/models_interior.py ("_gen": this script; no "_auto", so
                                     converter/gen_interiors.py leaves it alone). Regenerated on every run: hand
                                     fixes go into the table's "rooms" section, never into the recipe.
  data/interiors/<zone>.json         the room's zone: interior area HOUSES_AREA, no "auto" (owned by this script);
                                     warps/parent kept as converter/gen_interiors.py wrote them; people and Sapphire's
                                     signs regenerated the same way + signs for Sapphire's furniture messages
                                     (bookshelves, picture-book shelves, vases: behaviour-driven in Sapphire)
  src/field_scripts/<scripts>_room_<Map>.s, src/text/script/<text>_room_<Map>.txt

Recipe rules (Sapphire tile units, as models_interior.py):
  - floor = every tile that is not void, not Sapphire's top wall row ("walltop"), not a partition; a walltop tile with
    floor north of it is an inner low wall (Rustboro's flats) and becomes floor with white counters on it
  - style = the most common floor metatile kind; furniture by anchor metatile (top-left of its solid footprint),
    against the back wall when the anchor is right under a walltop tile
  - walkable chairs/cushions -> floor cushions, pushed off a neighbouring round table; on a rug they are lifted
  - rugs / door mats = Black 2 rug textures over each group's bounding box, 2 units above the floor (y 0: Black 2
    keeps layered surfaces >= 2 apart), cushions 2 above the rug
  - stairs: Sapphire's warp tiles 20b (up) / 219 (down) -> stair_u01 / stair_d01 (+ floor opening), as Littleroot
  - windows/pictures/posts on the walltop row -> window models or wall decals

Hand fixes ("rooms": {Map: {...}} in the table): style, add (furniture items), drop (indices or model names to leave
out), floor_add / floor_drop (tile rects), block (tiles), mats_add, decals_add, holes_add, origin, solid_y, area, note,
warps_to ({Sapphire warp index: [zone, warp]} for exits converter/gen_interiors.py could not resolve) + warps_note,
warps_dir ({Sapphire warp index: Black 2 direction}: the side a warp is walked into from, e.g. 1 = from the north,
to keep an arrival-only warp on a plain floor tile from firing when walked onto from the south).
"""
import os, sys, json, glob, collections

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(ROOT, 'b2tools'))
import move_codes as MOVE_CODES                       # noqa: E402  (v165_fixes)
from gba import Repo, MetatileRenderer

TABLE = os.path.join(ROOT, 'data', 'interior_tiles_houses.json')
LAYOUTS = os.path.join(ROOT, 'data', 'interior_layouts')
ZONES = os.path.join(ROOT, 'data', 'interiors')
HOUSES_AREA = 313       # unused Black 2 interior area (pack 31 = the generic interior pack, own texture set 313)
FAMILY = 'gTileset_GenericBuilding'
MB_EXIT, MB_DOOR = 0x65, 0x60

def dumps(obj):
    """json with one list item / object per line, short number lists and flat dicts kept on one line."""
    import re
    s = json.dumps(obj, indent=1, ensure_ascii=False)
    s = re.sub(r'\[\s+([-0-9.,\s]+?)\s+\]', lambda m: '[' + re.sub(r'\s+', ' ', m.group(1)) + ']', s)
    s = re.sub(r'\{\n\s+([^{}\[\]]*?)\n\s*\}', lambda m: '{' + re.sub(r'\n\s+', ' ', m.group(1)) + '}', s)
    return s + '\n'

def components(tiles):
    """4-connected groups of a set of (x, z) tiles."""
    tiles = set(tiles); out = []
    while tiles:
        st = [tiles.pop()]; grp = set(st)
        while st:
            x, z = st.pop()
            for n in ((x + 1, z), (x - 1, z), (x, z + 1), (x, z - 1)):
                if n in tiles: tiles.remove(n); grp.add(n); st.append(n)
        out.append(grp)
    return out

def bbox(grp):
    xs = [t[0] for t in grp]; zs = [t[1] for t in grp]
    return [min(xs), min(zs), max(xs), max(zs)]

def rects(tiles):
    """Inclusive tile rects covering a tile set: row runs, merged downwards while identical."""
    rows = collections.defaultdict(list)
    for x, z in sorted(tiles, key=lambda t: (t[1], t[0])): rows[z].append(x)
    runs = []
    for z in sorted(rows):
        xs = rows[z]; s = p = xs[0]
        for x in xs[1:] + [None]:
            if x is not None and x == p + 1: p = x; continue
            runs.append([s, z, p, z])
            if x is not None: s = p = x
    out = []
    for r in runs:
        m = next((o for o in out if o[0] == r[0] and o[2] == r[2] and o[3] == r[1] - 1), None)
        if m: m[3] = r[3]
        else: out.append(list(r))
    return out

class Gen:
    def __init__(self):
        self.t = json.load(open(TABLE))
        self.repo = Repo(os.path.join(ROOT, 'external', 'pokeruby'))
        self.rooms = json.load(open(os.path.join(ROOT, 'data', 'hoenn_interiors.json')))['rooms']
        t = self.t
        self.void = set(int(v, 16) for v in t['void'])
        self.walltop = set(int(v, 16) for v in t['walltop'])
        self.partition = set(int(v, 16) for v in t['partition']['tiles'])
        self.divider = set(int(v, 16) for v in t.get('divider', {}).get('tiles', []))
        self.kind = {int(v, 16): k for k, l in t['floor_kind'].items() if not k.startswith('_') for v in l}
        self.objects = {int(k, 16): v for k, v in t['objects'].items() if not k.startswith('_')}
        self.seats = set(int(v, 16) for v in t['seats']['tiles'])
        self.stairs = {int(k, 16): v for k, v in t['stairs'].items()}
        self.wall_things = {int(k, 16): v for k, v in t['wall_things'].items() if not k.startswith('_')}

    def family(self):
        return sorted(k for k, v in self.rooms.items() if v['tilesets'][1] == FAMILY and v['status'] == 'auto')

    # ------------------------------------------------------------------------------------------------ recipe
    def recipe(self, name):
        t = self.t; fix = t['rooms'].get(name, {})
        mj = self.repo.map_json(name); g, l = self.repo.layout_grid(mj['layout'])
        H, W = g.shape
        mt = lambda x, z: int(g[z, x]) & 0x3FF if 0 <= x < W and 0 <= z < H else None
        # ---- floor
        floor, counters, divider = set(), set(), []
        for z in range(H):
            for x in range(W):
                m = mt(x, z)
                if m in self.divider and z > 0 and mt(x, z - 1) not in self.void:   # a white divider in the room:
                    floor.add((x, z)); divider.append([x, z]); continue           # floor + a raised block (below)
                if m in self.void or m in self.partition or m in self.divider: continue
                if m in self.walltop:
                    n = mt(x, z - 1)
                    if n is not None and n not in self.walltop and n not in self.void and n not in self.partition and n not in self.divider:
                        counters.add((x, z)); floor.add((x, z))        # inner low wall -> counters on the floor
                    continue
                floor.add((x, z))
        for r in fix.get('floor_add', []): floor |= {(x, z) for x in range(r[0], r[2] + 1) for z in range(r[1], r[3] + 1)}
        for r in fix.get('floor_drop', []): floor -= {(x, z) for x in range(r[0], r[2] + 1) for z in range(r[1], r[3] + 1)}
        # ---- style
        kinds = collections.Counter(self.kind[mt(x, z)] for x, z in floor if mt(x, z) in self.kind)
        style = fix.get('style') or (kinds.most_common(1)[0][0] if kinds else 'houses_wood')
        against_wall = lambda x, z: mt(x, z - 1) is None or (mt(x, z - 1) in self.walltop and (x, z - 1) not in counters)
        furniture, decals, mats, holes, block = [], [], [], [], []
        consumed, table_tiles = set(), {}
        # ---- objects
        for z in range(H):
            for x in range(W):
                m = mt(x, z)
                if (x, z) in consumed or m not in self.objects: continue
                o = self.objects[m]
                if 'run' in o:
                    run = {int(v, 16) for v in o['run']}; w = 1
                    while mt(x + w, z) in run and (x + w, z) not in consumed: w += 1
                else: w = o.get('w', 1)
                h = o.get('h', 1)
                fp = [(xx, zz) for xx in range(x, x + w) for zz in range(z, z + h)]
                consumed |= set(fp)
                wall = o.get('wall') or ('N' if against_wall(x, z) else None)
                base = {k: o[k] for k in ('rot', 'y', 'dx', 'dz', 'gap') if k in o}
                if wall: base['wall'] = wall
                what = o.get('_what', '')
                if 'm' in o:
                    if o['m'] == 'table01':
                        # 2.8 tiles wide over a 2-tile footprint: keep it off the side walls (the table now uses
                        # table01_2x2, Black 2's table01 at Sapphire's 2x2 size, which needs none of this)
                        if x == 0 or (x - 1, z) not in floor: base['dx'] = base.get('dx', 0) + 7
                        elif x + w == W or (x + w, z) not in floor: base['dx'] = base.get('dx', 0) - 7
                        table_tiles.update({t_: base.get('dx', 0) for t_ in fp})
                    furniture.append(dict(m=o['m'], tiles=[x, z, x + w - 1, z + h - 1], **base, _what=f'{what} ({x},{z})'))
                    if o.get('block_head'): block.append([x, z])
                elif 'fit' in o:           # as many copies of a model `fit` units wide as fit in the run, evenly spaced
                    n = max(1, int(w * 16 // o['fit']))
                    for i in range(n):
                        furniture.append(dict(m=o['fill'], at=[x + (i + 0.5) * w / n, z + h / 2], **base, _what=f'{what} ({x},{z}) {i + 1}/{n}'))
                else:
                    lg = o.get('long')          # per row: a long model per `len` tiles, the fill model on the rest
                    for zz in range(z, z + h):
                        xx = x
                        while xx < x + w:
                            if lg and xx + lg['len'] <= x + w:
                                furniture.append(dict(m=lg['m'], at=[xx + lg['len'] / 2, zz + 0.5], rot=lg.get('rot', 0),
                                                      _what=f'{what} ({xx}-{xx + lg["len"] - 1},{zz})'))
                                xx += lg['len']; continue
                            furniture.append(dict(m=o['fill'], tile=[xx, zz], **{k: v for k, v in base.items() if k != 'wall'},
                                                  _what=f'{what} ({xx},{zz})'))
                            xx += 1
        # two round tables side by side (Sapphire's long tables): move them apart so they only touch
        tabs = sorted((f for f in furniture if f['m'] == 'table01'), key=lambda f: (f['tiles'][1], f['tiles'][0]))
        for a, b in zip(tabs, tabs[1:]):
            if a['tiles'][1] == b['tiles'][1] and b['tiles'][0] == a['tiles'][2] + 1:
                a['dx'] = a.get('dx', 0) - 6.5; b['dx'] = b.get('dx', 0) + 6.5
                for f in (a, b):
                    x0, z0, x1, z1 = f['tiles']
                    table_tiles.update({(xx, zz): f['dx'] for xx in range(x0, x1 + 1) for zz in range(z0, z1 + 1)})
        # inner low walls -> white counters along the run
        for grp in components(counters):
            x0, z0, x1, z1 = bbox(grp)
            for zz in range(z0, z1 + 1):
                xs = sorted(x for x, z in grp if z == zz); w = len(xs)
                n = max(1, int(w * 16 // 30))
                for i in range(n):
                    furniture.append(dict(m='shelf03', at=[xs[0] + (i + 0.5) * w / n, zz + 1.0], _what=f'inner low wall ({xs[0]}-{xs[-1]},{zz}) as counters {i + 1}/{n}'))
        # ---- rugs and mats (y 0 = 2 units above the floor)
        rug_tiles = set()
        for kind, spec in t['rugs'].items():
            if kind.startswith('_'): continue
            ids = {int(v, 16) for v in spec['tiles']}
            for grp in components((x, z) for z in range(H) for x in range(W) if mt(x, z) in ids):
                r = bbox(grp)
                if (r[2] - r[0] + 1) * (r[3] - r[1] + 1) < 4: continue     # stray rug-coloured tile
                rug_tiles |= {(xx, zz) for xx in range(r[0], r[2] + 1) for zz in range(r[1], r[3] + 1)}
                mats.append(dict(tex=spec['tex'], src=spec['src'], rect=r, border=spec['border'], border_units=spec['border_units'], y=0, _what=f'{kind} rug'))
        for kind, spec in t['mats'].items():
            if kind.startswith('_'): continue
            ids = {int(v, 16) for v in spec['tiles']}
            for grp in components((x, z) for z in range(H) for x in range(W) if mt(x, z) in ids):
                mats.append(dict(tex=spec['tex'], src=spec['src'], rect=bbox(grp), border=spec['border'], border_units=spec['border_units'], y=0,
                                 _what=f'{kind} mat' if kind != 'genkan' else 'concrete entrance strip'))
        # ---- seats
        st = t['seats']
        for z in range(H):
            for x in range(W):
                if mt(x, z) not in self.seats or (x, z) in consumed: continue
                f = dict(m=st['m'], tile=[x, z], _what=f'seat ({x},{z})')
                if (x + 1, z) in table_tiles: f['dx'] = -st['seat_dx'] + min(0, table_tiles[(x + 1, z)])
                elif (x - 1, z) in table_tiles: f['dx'] = st['seat_dx'] + max(0, table_tiles[(x - 1, z)])
                if (x, z) in rug_tiles: f['y'] = 1
                furniture.append(f)
        # ---- stairs (Sapphire warp tiles)
        for w in mj.get('warp_events', []):
            x, z = w['x'], w['y']
            kind = self.stairs.get(mt(x, z))
            # Black 2's stair placement (models_interior.py STAIR_MODELS: the flight starts on the warp tile, sloped
            # collision, stair_d01's floor opening made by the builder; rooms_cleanup agent)
            if kind == 'up':
                furniture.append(dict(m='stair_u01', stair=[x, z], dir='N', _what=f'stairs up (warp tile {x},{z}, entered from the south)'))
            elif kind == 'down':
                furniture.append(dict(m='stair_d01', stair=[x, z], dir='N', _what=f'stairs down (warp tile {x},{z}, entered from the south)'))
        # ---- things on the back wall
        for z in range(H):
            for x in range(W):
                m = mt(x, z)
                if m not in self.wall_things or (x, z) in counters: continue
                o = self.wall_things[m]
                zf = next((zz for zz in range(z + 1, H) if (x, zz) in floor), None)
                if zf is None: continue
                cx = x + 0.5 + o.get('dx', 0)
                if 'm' in o:
                    furniture.append(dict(m=o['m'], at=[cx, zf + 0.5], wall='N', gap=o.get('gap', 1), y=o.get('y', 0), _what=f"{o.get('_what', '')} ({x},{z})"))
                else:
                    d = dict(o['decal']); d['at'] = [round(cx, 3)]; d['z'] = zf; d['_what'] = f"{o.get('_what', '')} ({x},{z})"
                    decals.append(d)
        # ---- hand fixes
        drop = fix.get('drop', [])
        furniture = [f for i, f in enumerate(furniture) if i not in drop and f['m'] not in drop]
        furniture += fix.get('add', [])
        mats += fix.get('mats_add', []); decals += fix.get('decals_add', []); holes += fix.get('holes_add', [])
        block += fix.get('block', [])
        r = dict(_doc=f'{name}: generated by converter/gen_interior_recipes_houses.py from Sapphire\'s metatiles '
                      f'(data/interior_tiles_houses.json); do not edit, add fixes to the table\'s "rooms" section.'
                      + (' ' + fix['note'] if 'note' in fix else ''),
                 _gen='gen_interior_recipes_houses', map=name, style=style, floor=rects(floor))
        if 'origin' in fix: r['origin'] = fix['origin']
        if 'solid_y' in fix: r['solid_y'] = fix['solid_y']        # (table tops under Poke Balls: models_interior)
        if block: r['block'] = block
        if divider:                    # the dividers: wall-high blocks, sides in the room's wall texture, a light top
            sty = json.load(open(os.path.join(LAYOUTS, '_styles_houses.json')))[style]['wall']
            r['blocks'] = [dict(t['divider']['block'], tiles=divider, side=dict(sty, v=[0, 1]),
                                _what='Sapphire\'s white divider (data/interior_tiles_houses.json "divider")')]
        if holes: r['holes'] = holes
        if mats: r['mats'] = mats
        if decals: r['decals'] = decals
        r['furniture'] = furniture
        return r

    # ------------------------------------------------------------------------------------------------ zone + scripts
    def warps(self, name):
        """One warp per Sapphire warp event, in Sapphire's order, resolved as converter/gen_interiors.py does (outdoor
        doors from world.json: the zone's Black 2 warp slots first, then its 'doors'; rooms by their zone)."""
        if not hasattr(self, '_door'):
            sys.path.insert(0, os.path.join(ROOT, 'b2tools', 'patches'))
            import narcio, zoneheaders
            from zones import parse_entities
            files = os.path.join(ROOT, 'external', 'pokebw2', 'build', 'b2_us', 'files')
            world = json.load(open(os.path.join(os.environ.get('HOENN_WORLD_DIR') or os.path.join(ROOT, 'work', 'world'), 'world.json')))
            headers, _ = zoneheaders.load(files); ents = narcio.load(files, 126)
            self._door = {}
            for zid, z in world['zones'].items():
                base = len(parse_entities(ents[headers[int(zid)]['entities']])[0]['warps'])
                for k, d in enumerate(z.get('doors', [])): self._door[(d['map'], d['id'])] = (int(zid), base + k)
            self._zones = json.load(open(os.path.join(ROOT, 'data', 'hoenn_zones.json')))['maps']
        r = self.rooms[name]; out = []
        for i, w in enumerate(r['warps']):
            dest, dw = w['dest'], w['dest_warp']
            if dest in self._zones: to = self._door.get((dest, dw))
            elif dest in self.rooms and self.rooms[dest]['status'] == 'auto': to = (self.rooms[dest]['zone'], dw)
            elif dest in self.rooms and self.rooms[dest]['status'] == 'b2': to = (self.rooms[dest]['zone'], 0)
            else: to = None
            what = f'Sapphire warp {i} -> {dest} {dw}'
            fix = self.t['rooms'].get(name, {}).get('warps_to', {})
            if str(i) in fix: to = fix[str(i)]; what += f" (set by hand: {self.t['rooms'][name].get('warps_note', '')})"
            elif to is None: to = (r['zone'], 0); what += ' (UNRESOLVED: no door in world.json yet, points at its own warp 0)'
            wc = dict(at=[w['x'], w['y']], tile_only=True, to=list(to), what=what)
            d = self.t['rooms'].get(name, {}).get('warps_dir', {}).get(str(i))
            if d is not None: wc['dir'] = d; wc['what'] += f' (dir {d}: arrival only, Sapphire has no warp behaviour here)'
            out.append(wc)
        return out

    def zone(self, name):
        """The zone json, script and text of a room: people and signs as converter/gen_interiors.py makes them, plus
        Sapphire's behaviour-driven furniture messages as signs."""
        from gen3text import convert
        from gen_map_content import ruby_scripts, simple_message
        import gen_interiors as gi
        if not hasattr(self, '_text'):
            self._text, self._scripts = ruby_scripts()
            self._sprites = json.load(open(os.path.join(ROOT, 'data', 'sprite_map.json')))
            self._balls = json.load(open(os.path.join(ROOT, 'data', 'hoenn_items.json')))['balls']
        text, scripts, sprites, balls = self._text, self._scripts, self._sprites, self._balls
        r = self.rooms[name]; zone = r['zone']
        jpath = os.path.join(ZONES, f'{zone}.json')
        cfg = json.load(open(jpath))
        j = self.repo.map_json(name)
        cfg['warps'] = self.warps(name)
        msgs, blocks, npcs, signs, skipped = [], [], [], [], []
        for lid, o in enumerate(j.get('object_events', []), 1):          # same order and rules as gen_interiors.py
            if o['graphics_id'] == 'OBJ_EVENT_GFX_ITEM_BALL':
                b = balls.get(o['script'])
                if b: npcs.append(dict(uid=lid, model=110, script=b['script'], flag=b['flag'], dir=1, at=[o['x'], o['y']]))
                else: skipped.append(f"item ball {o['script']} (no Black 2 item)")
                continue
            if o.get('trainer_type', 'TRAINER_TYPE_NONE') not in ('TRAINER_TYPE_NONE', '0', 0):
                skipped.append(f"trainer {o['graphics_id'][14:]} {o['script']}"); continue
            if str(o.get('flag', '0')) not in ('0', ''):
                skipped.append(f"story person {o['graphics_id'][14:]} at ({o['x']},{o['y']}) {o['script']} (hide flag {o['flag']})"); continue
            code = (sprites.get(o['graphics_id']) or {}).get('code')
            label = simple_message(o['script'], text, scripts) if code else None
            if not label or convert(text[label])[1]:
                skipped.append(f"person {o['graphics_id'][14:]} at ({o['x']},{o['y']}) {o['script']} ({'no Black 2 sprite' if not code else 'story/complex script'})"); continue
            msgs.append(convert(text[label])[0]); blocks.append(gi.npc_block(len(blocks) + 1, len(msgs) - 1))
            face = {'MOVEMENT_TYPE_FACE_UP': 0, 'MOVEMENT_TYPE_FACE_DOWN': 1, 'MOVEMENT_TYPE_FACE_LEFT': 2,
                    'MOVEMENT_TYPE_FACE_RIGHT': 3}.get(o['movement_type'], 1)
            n = dict(uid=lid, model=code, script=len(blocks), dir=face, at=[o['x'], o['y']])
            n.update(MOVE_CODES.room_npc(o))     # Sapphire's movement type as Black 2's code (b2tools/move_codes.py)
            npcs.append(n)
        bg_tiles = set()
        for b in j.get('bg_events', []):
            bg_tiles.add((b['x'], b['y']))
            if b.get('type') != 'sign' or not b.get('script'):
                skipped.append(f"bg {b.get('type')} at ({b['x']},{b['y']})"); continue
            label = simple_message(b['script'], text, scripts)
            if not label or convert(text[label])[1]:
                skipped.append(f"sign at ({b['x']},{b['y']}) {b['script']} (story/complex script)"); continue
            msgs.append(convert(text[label])[0]); blocks.append(gi.sign_block(len(blocks) + 1, len(msgs) - 1))
            facing = b.get('player_facing_dir', 'BG_EVENT_PLAYER_FACING_ANY')
            signs.append(dict(script=len(blocks), at=[b['x'], b['y']], dir=0 if facing.endswith('NORTH') else 4))
        # furniture messages (Sapphire: by metatile behaviour), one sign per tile, one message per kind
        g, l = self.repo.layout_grid(j['layout'])
        mr = MetatileRenderer(self.repo, l['primary_tileset'], l['secondary_tileset'])
        kinds = {int(k, 16): v for k, v in self.t['signs'].items() if not k.startswith('_')}
        by_label = {}
        for z in range(g.shape[0]):
            for x in range(g.shape[1]):
                b = mr.behavior(int(g[z, x]) & 0x3FF)
                if b not in kinds or (x, z) in bg_tiles: continue
                lab = kinds[b]
                if lab not in by_label:
                    msgs.append(convert(text[lab])[0]); blocks.append(gi.sign_block(len(blocks) + 1, len(msgs) - 1))
                    by_label[lab] = len(blocks)
                signs.append(dict(script=by_label[lab], at=[x, z], dir=4, what=lab[5:]))
        entries = '\n'.join(f'    ScriptEntry Script_{i}' for i in range(1, len(blocks) + 1))
        src = (f'// {name} (zone {zone}): generated by converter/gen_interior_recipes_houses.py (Sapphire\'s simple people, signs\n'
               f'// and furniture messages). Messages: src/text/script/{r["text"]:04d}_room_{name}.txt\n#include "asm/field_script.inc"\n\n'
               + (entries + '\n' if blocks else '    ScriptEntry Script_None\n') + '    ScriptEntriesEnd\n\n'
               + '\n'.join(blocks) + ('' if blocks else 'Script_None:\n    VMHalt\n') + '    .balign 4, 0\n')
        txt = '\n'.join(msgs or ['…']) + '\n'
        cfg.pop('auto', None)
        fix = self.t['rooms'].get(name, {})
        cfg['area'] = fix.get('area', HOUSES_AREA)
        cfg['npcs'], cfg['signs'] = npcs, signs
        cfg = dict(_doc=f'{name}: zone written by converter/gen_interior_recipes_houses.py (warps and parent from '
                        f'converter/gen_interiors.py); story people left for the story phase: {"; ".join(skipped) or "none"}', **{k: v for k, v in cfg.items() if k != '_doc'})
        return cfg, src, txt, skipped

    def write(self, name, check=False):
        r = self.rooms[name]
        rec = self.recipe(name)
        cfg, src, txt, skipped = self.zone(name)
        paths = (os.path.join(LAYOUTS, f'{name}.json'), os.path.join(ZONES, f'{r["zone"]}.json'),
                 os.path.join(ROOT, 'src', 'field_scripts', f'{r["scripts"]:04d}_room_{name}.s'),
                 os.path.join(ROOT, 'src', 'text', 'script', f'{r["text"]:04d}_room_{name}.txt'))
        if not check:
            open(paths[0], 'w').write(dumps(rec))
            open(paths[1], 'w').write(dumps(cfg))
            from story_merge import write_room_script, write_room_text   # a story agent's part (after "// ---- story")
            write_room_text(paths[3], txt.rstrip('\n').split('\n'), paths[2])   # stays
            write_room_script(paths[2], src)
        return rec, cfg, skipped

def main(args):
    check = '--check' in args
    names = [a for a in args if not a.startswith('--')]
    gen = Gen()
    names = names or gen.family()
    for n in names:
        rec, cfg, skipped = gen.write(n, check)
        ms = collections.Counter(f['m'] for f in rec['furniture'])
        print(f"{n}: {rec['style']}, floor {len(rec['floor'])} rects, {sum(ms.values())} furniture {dict(ms)}, "
              f"{len(rec.get('mats', []))} rugs/mats, {len(rec.get('decals', []))} decals, {len(cfg['npcs'])} people, "
              f"{len(cfg['signs'])} signs" + (f"; left out: {len(skipped)}" if skipped else ''))

if __name__ == '__main__':
    main(sys.argv[1:])
