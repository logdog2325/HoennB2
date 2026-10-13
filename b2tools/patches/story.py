"""Story objects of the chapter agents (notes/STORY_PORTING.md "Story objects"): NPCs, signs and step triggers that
Sapphire's scenes need, appended to their zones' entity lists AFTER everything else (hoenn_world, interiors,
trainers), so no NPC index that a script or ObjInitNPCGPos already uses moves. Nothing here edits world/room jsons
that other agents own.

data/story/<chapter>.json:
  {"objects": [
     {"kind": "npc", "map": "Route103", "at": [10, 2], "uid": 102, "model": 162, "script": 1,
      "flag": "FLAG_HIDE_RIVAL_ROUTE103", "dir": 0, "move": 0},
     {"kind": "trigger", "map": "Route103", "at": [9, 3], "w": 3, "h": 1, "script": 2,
      "var": "VAR_ROUTE103_STATE", "value": 0},
     {"kind": "sign", "map": "LittlerootTown_ProfessorBirchsLab", "at": [4, 2], "script": 9, "dir": 0}, ...]}
- "map": a Sapphire map. Outdoor maps: "at" = Sapphire tile, placed at the map's world offset (b2tools/world.py) in
  the zone owning that cell. Rooms (data/hoenn_interiors.json): "at" + the built room's origin (room.json, as
  b2tools/patches/interiors.py places people). Or give "zone" and zone tiles "x", "z" directly.
  Warp-only maps (data/hoenn_standalone.json groups) use their group's own matrix; give a trigger there its "y"
  (outdoor triggers on the main matrix get the ground height of their tile from the cell's collision).
- Names of src/include/hoenn.h (FLAG_*, VAR_*) may be used for "flag" and "var".
- NPC keys as zone entities (b2tools/zones.py): uid, model, move, evtype, flag, script, dir, p0-p2, areaw, areah.
- "optional": true = skip the object while its map is not built (data/story/hidden_items.json, gen_hidden_items.py).
- Versions (notes/RUBY.md "WP0 layout"): "model_ruby": N replaces "model" in a Ruby build (Kyogre 4511 -> Groudon 4512), and any
  other key the same way ("script_emerald", "at_emerald", "flag_emerald", "skip_emerald": true: version_keys);
  objects in a room only the other version installs (data/versions.json "rooms") are skipped; data/story/ruby/<name>.json
  replaces data/story/<name>.json in a Ruby build (b2tools/version.py).
Run after `trainers` (see b2tools/story_build.sh).
"""
import os, re, sys, glob, json

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
import narcio, version  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))

def hoenn_names():
    src = open(os.path.join(ROOT, 'src', 'include', 'hoenn.h')).read()
    return {k: int(v, 0) for k, v in re.findall(r'#define\s+((?:FLAG|VAR)_\w+)\s+(0x[0-9a-fA-F]+|\d+)', src)}

def _num(v, names):
    if isinstance(v, str):
        if v in names: return names[v]
        return int(v, 0)
    return v

def ground_y(world_dir, wx, wz, prefix=''):
    """Ground height (world units) of an outdoor tile: its cell's collision plane at the tile's centre, where the
    player stands (ov036 FieldChunkAccessor_GetTerrainCore: y = -(nx*x - nz*z + d) / ny, x/z from the chunk centre,
    as b2tools/world.py collision_y), slopes included. A trigger fires while the player's position->y >> 12 is in
    [y - 2, y + 2) (ov012 CheckTriggerPositionMatchXYZ). The old flat-plane reading (-d / ny) was wrong on slopes:
    Route 119's stairs read 240 instead of 56, so the rival's trigger never fired (story_finish). prefix: a warp-only
    map's cells ('s_<group>_')."""
    import struct
    sys.path.insert(0, os.path.join(ROOT, 'b2tools'))
    from terrain.heights import NORMALS, OFFS
    path = os.path.join(world_dir, 'cells', f'{prefix}{wx // 32:02d}_{wz // 32:02d}', 'collision.per')
    if not os.path.exists(path): return 0
    d = open(path, 'rb').read()
    a, b, _, _ = struct.unpack_from('<HHHH', d, 4 + 8 * ((wz % 32) * 32 + wx % 32))
    nx, ny, nz = NORMALS[a >> 2]
    x, z = (wx % 32) * 16 + 8 - 256, (wz % 32) * 16 + 8 - 256
    return round(-(nx * x - nz * z + OFFS[b]) / ny)

SURF_CLASSES = {0x3d, 0x3e, 0x3f, 0x40, 0x42, 0x43, 0x94, 0x95, 0x96, 0x97}   # (outdoor_check.py's surf collision classes)

def sign_y(world_dir, wx, wz, prefix='', dir_=4):
    """y of an outdoor sign / hidden item (BG event): the game reads one when the tile in front of the player is its
    tile and the player's y is in [y - 2, y + 2) (ov012 CheckBGPositionMatchGrid). On a walkable tile, or when a tile
    you can read it from is at its own height, that is the tile's ground height (as before). On a solid tile whose
    readers all stand at another height (Lilycove's and Route 108's hidden items on beach rocks 8 above the sand:
    script_check 2026-10-08, never found), the height of the tiles it is read from (the most common one; dir 0 = from
    the south only, as caves_check)."""
    import struct
    from collections import Counter
    own = ground_y(world_dir, wx, wz, prefix)
    def rec(x, z):
        path = os.path.join(world_dir, 'cells', f'{prefix}{x // 32:02d}_{z // 32:02d}', 'collision.per')
        if not os.path.exists(path): return None
        return struct.unpack_from('<HHHH', open(path, 'rb').read(), 4 + 8 * ((z % 32) * 32 + x % 32))
    r = rec(wx, wz)
    if r is None or not r[3] & 1: return own
    sides = [(0, 1)] if dir_ == 0 else [(0, 1), (0, -1), (1, 0), (-1, 0)]
    hs = [ground_y(world_dir, wx + dx, wz + dz, prefix) for dx, dz in sides
          if (q := rec(wx + dx, wz + dz)) is not None and not q[3] & 1 and q[2] not in SURF_CLASSES]
    if not hs or any(-2 <= own - h < 2 for h in hs): return own
    return Counter(hs).most_common(1)[0][0]
def alt_land(world_dir, m, wx, wz):
    """True when an outdoor tile of map m is surf water in the main world and land in one of the map's other layouts
    (world.json alt_cells, b2tools/world.py build_alts): Mirage Island's Liechi Berry spot (Route 130 (52,9), daily berry
    spot tree_82) stands on the island; at the sea's height a surfer could read it on days the island is away. Such an
    object takes the other layout's height: a surfer is 8+ units off it then (signs and triggers match within 2)."""
    import struct
    def cls(d):
        path = os.path.join(world_dir, 'cells', d, 'collision.per')
        if not os.path.exists(path): return None
        return struct.unpack_from('<HHHH', open(path, 'rb').read(), 4 + 8 * ((wz % 32) * 32 + wx % 32))[2]
    alt = cls(f'alt_{m}_{wx // 32:02d}_{wz // 32:02d}')
    return alt is not None and alt not in SURF_CLASSES and cls(f'{wx // 32:02d}_{wz // 32:02d}') in SURF_CLASSES

def cave_y(rooms_dir, m, zx, zz, o):
    """Height (units) a trigger or sign in a cave (b2tools/models_cave.py: floors at several heights) needs: a trigger
    the height of its own tile, a sign (BG event, CheckBGPositionMatchGrid: within -2..+2 of the reader's y) that of the
    tile it is read from (its own tile when walkable, else the one south of it / the highest walkable neighbour).
    None for a room that is not a cave (one floor at 0). Events fire within 2 units of their y, so a story trigger or
    hidden item on a raised cave floor never fired at y 0 (Shoal Cave's shells; sweep_caves)."""
    import struct
    meta = json.load(open(os.path.join(rooms_dir, m, 'room.json')))
    if not meta.get('cave'): return None
    sys.path.insert(0, os.path.join(ROOT, 'b2tools'))
    from terrain.heights import NORMALS, OFFS
    mw = meta.get('matrix', [1, 1])[0]
    chunks = meta.get('chunks') or [dict(collision=meta['collision'])]
    def cell(x, z):
        k = (z // 32) * mw + x // 32
        if not (0 <= x and 0 <= z and k < len(chunks)) or not chunks[k]: return None
        d = open(os.path.join(rooms_dir, m, chunks[k]['collision']), 'rb').read()
        a, b, cls, fl = struct.unpack_from('<HHHH', d, 4 + 8 * ((z % 32) * 32 + x % 32))
        nx, ny, nz = NORMALS[a >> 2]
        y = -(nx * ((x % 32) * 16 + 8 - 256) - nz * ((z % 32) * 16 + 8 - 256) + OFFS[b]) / ny
        return y, not fl & 1
    c = cell(zx, zz)
    if o.get('kind') == 'trigger' or (c and c[1]): return round(c[0]) if c else None
    if o.get('dir', 4) == 0:
        s = cell(zx, zz + 1)
        return round(s[0]) if s and s[1] else None
    ys = [r[0] for r in (cell(zx + a, zz + b) for a, b in ((0, 1), (0, -1), (1, 0), (-1, 0))) if r and r[1]]
    return round(max(ys)) if ys else None

HIDDEN_PLACED = {}     # hidden-item slot -> (zone, x, z, on the main matrix), filled by apply for apply_code

def _objects3d_installed(files):
    """Object codes whose a/0/4/7 record holds a 3D model (entityType 2 with a model file): the codes data/story objects
    marked "requires_object3d" may use. A build without patches/objects3d.py leaves 0x2000-0x2002 empty (sceneNodeType 0,
    res 0) and 112 a people record, so those objects are left out instead of showing Black 2's boulder or nothing."""
    import struct
    sys.path.insert(0, os.path.join(ROOT, 'b2tools'))
    import sprites
    t = narcio.load(files, sprites.ARC_OW_TABLE)[0]
    out = set()
    for code in list(range(377)) + list(range(0x2000, 0x200B)):
        et, snt = t[4 + 28 * sprites.obj_record(code) + 2], t[4 + 28 * sprites.obj_record(code) + 3]
        res1 = struct.unpack_from('<H', t, 4 + 28 * sprites.obj_record(code) + 0x10)[0]
        if et == 2 and snt and res1: out.add(code)
    return out

def W_zone_of(owner, wx, wz, rects):
    """world.py zone_of: a zone_rects rectangle (main matrix only), else the cell's zone, as the game and the converters
    (gen_map_content, gen_trainer_npcs) see it: Route 104's north end is Route 104's zone 329, not Rustboro's 113."""
    for x0, z0, x1, z1, z in rects:
        if x0 <= wx <= x1 and z0 <= wz <= z1: return z
    return owner[(wx // 32, wz // 32)]

def version_keys(o):
    """Per-version keys (emerald_ch45_magma 2026-10-12): "<key>_<version>" replaces "<key>" in a build of that version, e.g.
    "script_emerald": 3379, "at_emerald": [9, 16], "flag_emerald": ..., "p0_emerald": 6 (Ruby's "model_ruby" is the same rule);
    "skip_emerald": true leaves the object out of an Emerald build. Sapphire builds read none of them (no "_sapphire" keys)."""
    sfx = '_' + version.VERSION
    over = {k[:-len(sfx)]: v for k, v in o.items() if k.endswith(sfx) and len(k) > len(sfx)}
    return dict(o, **over) if over else o

def apply(files):
    paths = version.overlay(os.path.join(ROOT, 'data', 'story'), '*.json')
    paths += [p for p in os.environ.get('HOENN_EXTRA_STORY', '').split(':') if p]   # test builds: more object files
    objs = [(os.path.basename(p), version_keys(o)) for p in paths for o in json.load(open(p)).get('objects', [])]
    if not objs: return 'no story objects (data/story/*.json)'
    import zoneheaders
    from zones import parse_entities, build_entities
    names = hoenn_names()
    rooms = json.load(open(os.path.join(ROOT, 'data', 'hoenn_interiors.json')))['rooms']
    rooms_dir = os.environ.get('HOENN_INTERIORS_DIR') or os.path.join(ROOT, 'work', 'interiors')
    world_dir = os.environ.get('HOENN_WORLD_DIR') or os.path.join(ROOT, 'work', 'world')
    maps = None
    rects = []                       # world.json "zone_rects": sub-cell zones (world.py zone_rects, the banner code patch)
    def place(o):
        """(zone, x, z) zone tiles of an object."""
        nonlocal maps, rects
        if 'zone' in o: o.setdefault('_main', o.get('main', True)); return o['zone'], o['x'], o['z']
        m = o['map']
        if m in rooms:
            # (emerald_rooms 2026-10-12) Emerald installs a room variant built from pokeemerald's map for some rooms
            # (data/versions.json room_variants.emerald, b2tools/emerald_rooms.py): its origin and floors are the ones
            # the object stands in. Sapphire and Ruby read the room itself, as before.
            mr = version.room_variant(m) if version.is_emerald() and os.path.exists(
                os.path.join(rooms_dir, version.room_variant(m), 'room.json')) else m
            if not os.path.exists(os.path.join(rooms_dir, mr, 'room.json')):
                if o.get('optional'): return None             # a room not built yet (hidden items)
            ox, oz = json.load(open(os.path.join(rooms_dir, mr, 'room.json')))['origin']
            o['_main'] = False
            if o.get('kind', 'npc') in ('trigger', 'sign') and 'y' not in o:     # a cave's raised floors (sweep_caves)
                y = cave_y(rooms_dir, mr, o['at'][0] + ox, o['at'][1] + oz, o)
                if y: o['y'] = y
            return rooms[m]['zone'], o['at'][0] + ox, o['at'][1] + oz
        if maps is None:
            import world as W
            cfg, lay = W.load()
            _, _, main = W.compose(cfg, lay)
            wj = json.load(open(os.path.join(world_dir, 'world.json')))
            cells = {(c['cx'], c['cz']): c['zone'] for c in wj['cells']}
            rects = wj.get('zone_rects', [])
            maps = {n: (main, cells, '') for n in main}
            if any(ob.get('map') not in main and ob.get('map') not in rooms and 'zone' not in ob for _, ob in objs):
                for g, _, fm, fo in W.standalone_frames(cfg):     # warp-only maps: their own matrix and cells
                    for n in fm: maps.setdefault(n, (fm, fo, f's_{g}_'))
        if m not in maps and o.get('optional'): return None     # a map not built yet
        fmaps, fowner, prefix = maps[m]
        wx, wz = fmaps[m]['ox'] + o['at'][0], fmaps[m]['oz'] + o['at'][1]
        if 'y' not in o and prefix == '' and alt_land(world_dir, m, wx, wz):   # (postgame_maps) open sea here, land in
            o['y'] = ground_y(world_dir, wx, wz, f'alt_{m}_')       # the map's other layout: that layout's height
        if 'y' not in o and o.get('kind') == 'sign':                 # a hidden item / sign on a solid tile (a beach
            o['y'] = sign_y(world_dir, wx, wz, prefix, o.get('dir', 4))   # rock): the height you read it from
        o.setdefault('y', ground_y(world_dir, wx, wz, prefix))       # triggers fire within 2 units of their y
        o['_main'] = prefix == ''
        return W_zone_of(fowner, wx, wz, rects if prefix == '' else ()), wx, wz
    headers, _ = zoneheaders.load(files)
    ents = narcio.load(files, 126)
    edits, done = {}, []
    skipped = []
    have3d = _objects3d_installed(files)
    for src, o in objs:
        if o.get('skip'): continue                             # "skip_<version>": true (version_keys)
        if o.get('map') in rooms and not version.room_in_version(o['map']):   # the other version's room
            skipped.append(o['map']); continue
        if o.get('requires_object3d') and o['model'] not in have3d:   # (missing_objects) a 3D object whose record
            skipped.append(f'{o["map"]} 3D object {o["model"]}'); continue   # patches/objects3d.py did not fill
        at = place(o)
        if at is None: skipped.append(o['map']); continue
        zone, x, z = at
        if zone not in edits: edits[zone] = parse_entities(ents[headers[zone]['entities']])[0]
        e = edits[zone]
        kind = o.get('kind', 'npc')
        if kind == 'npc':
            tmpl = dict(e['npcs'][0]) if e['npcs'] else dict(rail=0, y=0)
            npc = dict(tmpl, uid=o['uid'], model=o.get(f'model_{version.VERSION}', o['model']), move=o.get('move', 0), evtype=o.get('evtype', 0),
                       flag=_num(o.get('flag', 0), names), script=o['script'], dir=o.get('dir', 1), p0=o.get('p0', 0),
                       p1=o.get('p1', 0), p2=o.get('p2', 0), areaw=o.get('areaw', 0), areah=o.get('areah', 0),
                       rail=0, x=x, z=z, y=0)
            assert npc['uid'] not in {n['uid'] for n in e['npcs']}, f'{src}: uid {npc["uid"]} already in zone {zone}'
            e['npcs'].append(npc)
        elif kind == 'trigger':
            e['triggers'].append(dict(script=o['script'], value=_num(o.get('value', 0), names),
                                      work=_num(o.get('var', 0), names), type=o.get('type', 0), rail=0, x=x, z=z,
                                      w=o.get('w', 1), h=o.get('h', 1), y=o.get('y', 0), unk=0))
        elif kind == 'sign':
            e['signs'].append(dict(script=o['script'], cond=o.get('cond', 0), dir=o.get('dir', 4), rail=0, x=x, z=z,
                                   y=o.get('y', 0)))
        else:
            raise SystemExit(f'{src}: unknown kind {kind}')
        if 'hidden_slot' in o: HIDDEN_PLACED[o['hidden_slot']] = (zone, x, z, o['_main'])
        done.append(f'{kind} {o.get("map", zone)}->{zone} ({x},{z})')
    for zone, e in edits.items():
        ents[headers[zone]['entities']] = build_entities(e, ents[headers[zone]['entities']])
    narcio.save(files, 126, ents)
    return (f'{len(done)} story objects' + (f' ({len(skipped)} optional ones skipped, maps not built: '
            f'{sorted(set(skipped))})' if skipped else '') + ': ' + ', '.join(done[:12]) + (' ...' if len(done) > 12 else ''))

# ---- Black 2's hidden-item table (ov012 HIDDEN_ITEMS 0x0216ce44, 213 x {u16 flag - 2820, u8 on the main matrix,
# u8 respawns daily, u16 zone, u16 x, u16 z}): the Itemfinder (Dowsing Machine, ov086) and the daily respawn
# (TryClearRepeatableHiddenItemFlags, ov012 0x0215f27c: 20 % of the "respawns" entries each new day) read it.
# Sapphire's hidden items (converter/gen_hidden_items.py) get their placed zone and tile and never respawn; the slots
# no Hoenn item uses (Unova places) are moved far off (x, z 0x7fff) and never respawn either.
OV012_BASE, HIDDEN_ITEMS, HIDDEN_SLOTS = 0x021503c0, 0x0216ce44, 213
OV279_BASE = 0x021e8be0                # ov279 .text start (config/b2_us/arm9/overlays/ov279/delinks.txt)

def apply_code(code):
    import struct
    # These overlay edits change ov012's compressed size: savestates made before them break as soon as the game reloads
    # ov012 (a door warp: tested 2026-10-07 with work/emu/base_littleroot.dst). Off until the lead's next savestate
    # remake (the same step as converter/gen_key_items.py --install): HOENN_STORY_CODE=1 turns them on; then the
    # default becomes on.
    if os.environ.get('HOENN_STORY_CODE', '1') != '1':
        return 'skipped until the savestate remake (HOENN_STORY_CODE=1: hidden-item table, no Xtransceiver in the new-game Bag)'
    path = os.path.join(code, 'arm9_ov012.bin')
    d = bytearray(open(path, 'rb').read())
    o = HIDDEN_ITEMS - OV012_BASE
    for n in range(1, HIDDEN_SLOTS + 1):
        e = o + 10 * (n - 1)
        flag = struct.unpack_from('<H', d, e)[0]
        assert flag == n - 1, (n, flag)
        if n in HIDDEN_PLACED:
            zone, x, z, main = HIDDEN_PLACED[n]
            struct.pack_into('<HBBHHH', d, e, n - 1, 1 if main else 0, 0, zone, x, z)
        else:
            struct.pack_into('<HBBHHH', d, e, n - 1, d[e + 2], 0, struct.unpack_from('<H', d, e + 4)[0], 0x7fff, 0x7fff)
    if os.path.islink(path): os.unlink(path)
    open(path, 'wb').write(d)
    # the new-game Bag: no Xtransceiver (it is the PokéNav, Mr. Stone gives it: user decision 2026-10-06); the Pal Pad
    # stays. ov279 InitItemBag_ (src/ov279/new_game.c): the gender's BagSave_AddItem call at 0x021e8c12 -> two nops.
    path = os.path.join(code, 'arm9_ov279.bin')
    d = bytearray(open(path, 'rb').read())
    o = 0x021e8c12 - OV279_BASE
    assert d[o:o + 4] in (bytes.fromhex('1ff629fb'), bytes.fromhex('c046c046')), d[o:o + 4].hex()
    d[o:o + 4] = bytes.fromhex('c046c046')
    if os.path.islink(path): os.unlink(path)
    open(path, 'wb').write(d)
    ribbons = ribbon_commands(code)
    return f'{ribbons}; new-game Bag without the Xtransceiver (PokéNav); hidden-item table: {len(HIDDEN_PLACED)} Hoenn slots placed, {HIDDEN_SLOTS - len(HIDDEN_PLACED)} others off-map; none respawn'

# ---- ribbons (user decision 2026-10-07: Sapphire's ribbons are really given; h_give_ribbon / h_check_ribbon) -------
# Black 2's scripts can read or set a Pokémon's fields only through two whitelists in ov012: PokePartyGetParam
# (s0110 0x02156fdc: u8 list of 20 fields at 0x0216ca06) and PokePartySetIV (s0111 0x02156f74: {field, max} x 6 at
# 0x0216ca1a, the IVs 0x46-0x4b, max 31). Fields 0x4d-0x6c are the Hoenn ribbons (swan's PkmField, the PK4 Hoenn
# ribbon set): 20 contest ribbons, then 0x61 Champion, 0x62 Winning, 0x63 Victory, 0x64 Artist, 0x65 Effort, ...
#  - s0111: the table loop is replaced by two range checks: IVs 0x46-0x4b up to 31 (as before) and ribbons 0x4d-0x6c up
#    to 1 (same 0x4a bytes, no table read).
#  - s0110's list: five fields no script reads (0x0c region, 0x6d fateful encounter, 0x77 origin game, 0x9a OT gender,
#    0xa6 Sp. Def; checked in Black 2's and our scripts) become the five ribbons Sapphire's scripts check or give:
#    Champion, Winning, Victory, Artist, Effort.
SETIV, SETIV_END = 0x02156f92, 0x02156fdc
CheckGetPartyPokemon, PokeParty_SetParam, PokeParty_RecalcStats = 0x02156174, 0x0201cd1c, 0x0201d5f4
GETPARAM_LIST = 0x0216ca06
GETPARAM_SWAP = {0x0c: 0x61, 0x6d: 0x62, 0x77: 0x63, 0x9a: 0x64, 0xa6: 0x65,
                 0xa5: 0x00}   # (postgame_maps) Sp. Atk, read by no script -> the personality (Route 130's Mirage Island:
                               # s0110 stores the u32 into a u16 work = personality & 0xFFFF, Sapphire's IsMirageIslandPresent)

def ribbon_commands(code):
    import importlib.util
    spec = importlib.util.spec_from_file_location('exp_share_', os.path.join(HERE, 'exp_share.py'))
    es = importlib.util.module_from_spec(spec); spec.loader.exec_module(es)
    t = es.Thumb(SETIV)                        # in: r7 index, r4 field, r0 value, r5 env (s0111's own registers)
    t.mov(6, 0)
    t.mov(0, 4); t.subi(0, 0x4d); t.cmp(0, 0x1f); t.bcc('hi', 'iv')
    t.cmp(6, 1); t.bcc('hi', 'ret'); t.b('set')
    t.label('iv'); t.mov(0, 4); t.subi(0, 0x46); t.cmp(0, 5); t.bcc('hi', 'ret')
    t.cmp(6, 31); t.bcc('hi', 'ret')
    t.label('set'); t.mov(0, 5); t.mov(1, 7); t.h(0xAA00)                  # add r2, sp, #0
    t.bl(CheckGetPartyPokemon); t.cmp(0, 1); t.bne('ret')
    t.ldr_sp(0, 0); t.mov(1, 4); t.mov(2, 6); t.bl(PokeParty_SetParam)
    t.ldr_sp(0, 0); t.bl(PokeParty_RecalcStats)
    t.label('ret'); t.movs(0, 0); t.pop([3, 4, 5, 6, 7])
    blob = t.assemble()
    assert len(blob) <= SETIV_END - SETIV, len(blob)
    path = os.path.join(code, 'arm9_ov012.bin')
    d = bytearray(open(path, 'rb').read())
    o = SETIV - OV012_BASE
    vanilla = open(os.path.join(ROOT, 'external', 'pokebw2', 'build', 'b2_us', 'build', 'arm9_ov012.bin'), 'rb').read()
    new = blob + bytes.fromhex('c046') * ((SETIV_END - SETIV - len(blob)) // 2)
    assert d[o:o + len(new)] in (vanilla[o:o + len(new)], new), 's0111 is not Black 2\'s'
    d[o:o + len(new)] = new
    lo = GETPARAM_LIST - OV012_BASE
    for i in range(20):
        if d[lo + i] in GETPARAM_SWAP: d[lo + i] = GETPARAM_SWAP[d[lo + i]]
    assert sorted(set(GETPARAM_SWAP.values())) == sorted(set(d[lo:lo + 20]) & set(GETPARAM_SWAP.values()))
    if os.path.islink(path): os.unlink(path)
    open(path, 'wb').write(d)
    return f'ribbons: PokePartySetIV takes fields 0x4d-0x6c (0/1), PokePartyGetParam reads 0x61-0x65 ({len(blob)} B)'
