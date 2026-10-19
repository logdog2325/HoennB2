"""Hoenn's warp-only outdoor maps (b2tools/world.py build_standalone, data/hoenn_standalone.json), after hoenn_world
(chunks, matrices, zones, doors), area2_buildings (pack 0) and the room patches (interiors, centers, shops):

1. Their own exterior building pack. Black 2 loads one area per field (AreaData_Create in Field_Create; a warp
   reloads it, notes/RESEARCH_WORLD.md section 2) and the whole pack goes into the field heap (pack 0 is at its
   limit, notes/TOWNS_TOWNS2.md), so these maps don't use pack 0: their area (hoenn_world copied area 3 into it) gets
   a new pack appended to a/2/2/5 with only the models their chunks place (pack 0's, e.g. signs and the Center, plus
   data/buildings/standalone.json's own models, b2tools/models_standalone.py), each with its door model and the default
   res 0x15 (FieldPropSystem_BuildResIDLUT falls back to it), and a texture set appended to a/1/7/4 at the same index
   (pack i <-> textures i, FieldPropSystem_LoadArea): pack 0's set plus the new models' textures, merged byte for byte.
2. Room exits that lead to these maps. A room's warps keep Sapphire's order (converter/gen_interiors.py and the room
   agents' tools); hoenn_world gave these maps' doors Sapphire's order too, so warp i of a room whose Sapphire warp i
   leads to (map, k) is pointed at that map's door k (zone's Black 2 warp count + k), as the room tools do for the
   connected world from world.json. Rooms whose warp count differs from Sapphire's are only reported. A generated
   room whose door is on one of these maps had Littleroot (389) as its town (gen_interiors.py read world.json before
   these maps had doors): it gets its map's zone as parent, place name and music.
3. Their area's own map texture set (map_textures): Hoenn's set 3 plus the stand-in ground textures the groups' look
   options name (world.json group 'textures'), at a/0/1/4 entry <area>, the area record pointed at it.
4. Seasons (seasonal_areas, Birch's seasons question 2026-10-18, notes/SEASONS.md): their areas (407, 408: fixed,
   summer) are not seasonal, so their zones move to two seasonal area groups of Black 2's that no zone uses
   (records b..b+3 = spring..winter, AreaData_HasSeasons: 2 <= id < 0x11a), each record a copy of its area's with the
   season's lights and texture set: Hoenn's set for that season (hoenn_textures' sets 2-5) plus the same stand-in
   textures (each from its Black 2 area's set for that season when it has the same texture, as hoenn_textures does).
   The four sets are shared by both groups (written to the first group's entries b..b+3). Summer is the same bytes
   as before, so with the summer lock (Birch's answer NO, older saves) nothing changes.
Apply it last (after centers); patches/hoenn_world.py has already put the groups' chunks, matrices and zones in."""
import os, sys, json, struct, glob
import narcio, zoneheaders
sys.path.insert(0, os.path.dirname(__file__))
from b2files import gf_container, gf_container_build
from zones import parse_entities, build_entities

ROOT = os.path.join(os.path.dirname(__file__), '..', '..')
W = os.environ.get('HOENN_WORLD_DIR') or os.path.join(ROOT, 'work', 'world')
SRC = os.path.join(ROOT, 'external', 'pokebw2', 'build', 'b2_us', 'files')
DEFAULT_RES = 0x15                   # exterior fallback model (rock_01), FieldPropSystem_BuildResIDLUT

def _placed(world):
    res = set()
    for g in world.get('standalone', []):
        for c in g['cells']:
            p = open(os.path.join(W, 'cells', c['dir'], 'placements.bin'), 'rb').read()
            for i in range(struct.unpack_from('<I', p, 0)[0]):
                res.add((p[4 + 16 * i + 14] << 8) | p[4 + 16 * i + 15])
    return res

def build_pack(files, world):
    sys.path.insert(0, os.path.join(ROOT, 'b2tools'))
    import nsbtx
    from area2_buildings import info_record, pairs_for
    reg_path = os.path.join(ROOT, 'data', 'buildings', 'standalone.json')
    reg = json.load(open(reg_path)) if os.path.exists(reg_path) else {'models': [], 'textures': []}
    packs, tex = narcio.load(files, 225), narcio.load(files, 174)
    magic, secs = gf_container(packs[0]); n = len(secs) // 2
    pack0 = {struct.unpack_from('<H', s, 0)[0]: (s, b) for s, b in zip(secs[:n], secs[n:])}
    mdir = os.environ.get('HOENN_STANDALONE_BUILDINGS') or os.path.join(ROOT, 'work', 'buildings', 'standalone')
    path = lambda m: os.path.join(mdir, os.path.basename(m['model']))         # (models_standalone.py's output)
    own = {m['res']: (info_record(m['res'], m['door'], m['dx'], m['dz'], m.get('type', 0)), open(path(m), 'rb').read())
           for m in reg['models'] if os.path.exists(path(m))}
    # their textures: textures.txt next to the models ('<set> <texture>', set extNN = a/1/7/4 entry NN, mapNNN =
    # a/0/1/4 entry NNN), read from the user's dump; work/tex/<set>.nsbtx when a town agent made one
    tl = os.path.join(mdir, 'textures.txt')
    reg_tex = [l.split() for l in open(tl)] if os.path.exists(tl) else reg.get('textures', [])
    want = _placed(world) | {DEFAULT_RES}
    models, missing = {}, []
    todo = sorted(want)
    while todo:
        r = todo.pop()
        if r in models or r == 0xFFFF: continue
        src = own.get(r) or pack0.get(r)
        if not src: missing.append(r); continue
        models[r] = src
        door = struct.unpack_from('<H', src[0], 4)[0]
        if door != 0xFFFF and door not in models: todo.append(door)
    assert len(models) <= 128, f'standalone pack: {len(models)} models'
    infos = [models[r][0] for r in sorted(models)]; bmds = [models[r][1] for r in sorted(models)]
    index = len(packs)
    packs.append(gf_container_build('AB', infos + bmds))
    adds, srcs = [], {}
    import b2files
    def tex_set(setname):
        p = os.path.join(ROOT, 'work', 'tex', setname + '.nsbtx')
        if os.path.exists(p): return open(p, 'rb').read()
        if setname.startswith('ext'): return b2files.building_textures(SRC, int(setname[3:]))
        return b2files.map_textures(SRC, int(setname[3:]))
    have0 = {tn for tn, _ in nsbtx._parse(tex[0])['texs']}
    for setname, name, *pal in reg_tex:
        if name in have0: continue                       # (already in pack 0's set, the base of this pack's)
        src = srcs.setdefault(setname, tex_set(setname))
        have = {pn for pn, _ in nsbtx._parse(src)['pals']}
        pn = pal[0] if pal else pairs_for(setname).get(name, name + '_pl')
        adds.append((src, name, pn if pn in have else None))
    while len(tex) < index: tex.append(tex[0])          # (pack i <-> texture set i)
    tex.append(nsbtx.merge(tex[0], adds) if adds else tex[0])
    narcio.save(files, 225, packs); narcio.save(files, 174, tex)
    size = sum(map(len, infos + bmds))
    return index, f'pack {index}: {len(models)} models {sorted(models)}, {size} B (pack 0: {len(packs[0])} B); textures {len(tex[index])} B' + \
        (f'; MISSING models {missing}' if missing else '')

def map_textures(files, world, raw):
    """The groups' own ground textures (world.json group 'textures': name -> Black 2 map set, from
    data/hoenn_standalone.json 'retex'/'ground'/'lava'): the area's map texture set becomes Hoenn's (set 3, with the
    terrain modules' textures from hoenn_textures) plus those, byte for byte (nsbtx.merge), written to a/0/1/4 entry
    <area> (texSet = area id for every Black 2 area, and the standalone area is used by no Black 2 zone) and the area
    record's texSet pointed at it."""
    import nsbtx, b2files
    extra = {}
    for g in world['standalone']: extra.update(g.get('textures', {}))
    if not extra: return 'map textures: set 3'
    sets = narcio.load(files, 14)
    srcs, adds = {}, []
    for name, ts in sorted(extra.items()):
        src = srcs.setdefault(ts, b2files.map_textures(SRC, int(ts)))
        pals = {n for n, _ in nsbtx._parse(src)['pals']}
        adds.append((src, name, name + '_pl' if name + '_pl' in pals else None))
    out = []
    for area in sorted({g['area'] for g in world['standalone']}):
        assert area < len(sets), f'a/0/1/4 has no entry {area}'
        sets[area] = nsbtx.merge(sets[3], adds)
        struct.pack_into('<H', raw, area * 10 + 2, area)
        out.append(f'set {area} = set 3 + {len(adds)} textures, {len(sets[area])} B')
    narcio.save(files, 14, sets)
    return 'map textures: ' + ', '.join(out)

HOENN_AREA = 2                       # the overworld's seasonal area (records 2-5: lights 140-143, sets 2-5)

def seasonal_areas(files, world, raw):
    """Point 4 of the module doc. raw = a/0/1/3 (edited in place). The groups: the first free ones (no zone header
    names any of their four ids, no used area's record names their texture sets), 6 and 10 in all three versions."""
    import nsbtx
    from hoenn_textures import season_source
    areas = sorted({g['area'] for g in world['standalone']})
    headers, hentries = zoneheaders.load(files)
    n = len(raw) // 10
    rec = lambda a: struct.unpack_from('<HH', raw, a * 10)           # (building pack, texture set)
    seasonal = lambda a: 2 <= a < 0x11a
    used = set()
    for h in headers:
        if h['area'] in areas: continue
        used |= set(range(h['area'], h['area'] + 4)) if seasonal(h['area']) else {h['area']}
    used_sets = {rec(a)[1] for a in used if a < n}
    free = [b for b in range(2, 0x11a, 4) if not (set(range(b, b + 4)) & (used | used_sets | set(areas)))]
    assert len(free) >= len(areas), f'only {len(free)} free seasonal area groups: {free}'
    groups = dict(zip(areas, free))
    # the four texture sets: Hoenn's for the season (hoenn_textures) + the stand-in textures for the season
    extra = {}
    for g in world['standalone']: extra.update(g.get('textures', {}))
    sets = narcio.load(files, 14)
    vraw = open(os.path.join(SRC, 'a', '0', '1', '3'), 'rb').read()
    vsets = narcio.load(SRC, 14)
    vload = lambda i: vsets[i]
    first = groups[areas[0]]
    tex_of, sizes = [], []
    for season in range(4):
        base = struct.unpack_from('<H', raw, (HOENN_AREA + season) * 10 + 2)[0]
        if not extra:                                                  # (map_textures: no stand-ins, set 3 itself)
            tex_of.append(base); continue
        adds = []
        for name, ts in sorted(extra.items()):
            pal = name + '_pl' if name + '_pl' in {p for p, _ in nsbtx._parse(vload(int(ts)))['pals']} else None
            alt = int(ts) if season == 1 else season_source(vraw, vload, int(ts), name, pal, season)
            adds.append((vload(alt), name, pal))                       # (summer: map_textures' own source)
        sets[first + season] = nsbtx.merge(sets[base], adds)
        tex_of.append(first + season); sizes.append(len(sets[first + season]))
    if extra:
        assert sets[first + 1] == sets[areas[0]], 'the summer set differs from map_textures\' (it must stay the same)'
        narcio.save(files, 14, sets)
    for a, b in groups.items():
        for season in range(4):
            r = bytearray(raw[a * 10:a * 10 + 10])                     # pack, srt anim, flags: the area's own
            struct.pack_into('<H', r, 2, tex_of[season])
            r[7] = raw[(HOENN_AREA + season) * 10 + 7]                  # the season's lights (140-143)
            raw[(b + season) * 10:(b + season) * 10 + 10] = r
    moved = {}
    for z, h in enumerate(headers):
        if h['area'] in groups:
            moved.setdefault(h['area'], []).append(z); h['area'] = groups[h['area']]
    zoneheaders.save(files, headers, hentries)
    sizes = ', '.join(map(str, sizes)) or "area 2's"
    return 'seasons: ' + ', '.join(f'area {a} -> {b}-{b + 3} ({len(moved.get(a, []))} zones)' for a, b in groups.items()) + \
        f'; texture sets {tex_of} ({sizes} B)'

def fix_room_exits(files, world):
    import version                  # (data/versions.json door aliases: version.door_alias)
    """Point rooms' exits at the warp-only maps' doors (see module doc)."""
    headers, hentries = zoneheaders.load(files)
    src_headers, _ = zoneheaders.load(SRC)
    towns = []
    src_ents = narcio.load(SRC, 126)
    sa_maps = {m for g in world.get('standalone', []) for m in g.get('origins', {})}
    door_at = {}
    for zid, z in world['zones'].items():
        if z.get('group') is None: continue
        base = len(parse_entities(src_ents[src_headers[int(zid)]['entities']])[0]['warps'])
        for k, d in enumerate(z.get('doors', [])): door_at[(d['map'], d['id'])] = (int(zid), base + k)
    rooms = json.load(open(os.path.join(ROOT, 'data', 'hoenn_interiors.json')))['rooms']
    ents = narcio.load(files, 126)
    done, odd = [], []
    for name, r in sorted(rooms.items()):
        targets = [(i, (w['dest'], w['dest_warp'])) for i, w in enumerate(r['warps']) if w['dest'] in sa_maps]
        if not targets: continue
        hd = headers[r['zone']]
        e, _ = parse_entities(ents[hd['entities']])
        if len(e['warps']) != len(r['warps']):
            odd.append(f"{name} ({len(e['warps'])} warps, Sapphire {len(r['warps'])})"); continue
        changed = []
        for i, key in targets:
            key = version.door_alias(*key)     # (Emerald: the Battle Tower door is BattleFrontier_OutsideEast's warp 0)
            if key not in door_at: odd.append(f'{name} warp {i}: no door {key}'); continue
            zone, idx = door_at[key]
            if (e['warps'][i]['dest_zone'], e['warps'][i]['dest_warp']) != (zone, idx):
                e['warps'][i]['dest_zone'], e['warps'][i]['dest_warp'] = zone, idx; changed.append(i)
        if changed:
            ents[hd['entities']] = build_entities(e, ents[hd['entities']])
            done.append(f"{name} (zone {r['zone']}) warps {changed}")
        # a generated room whose door is on a warp-only map got Littleroot (389) as its town (gen_interiors.py finds
        # a room's town from world.json's doors, written before these maps had any): its place name and music
        # are its warp-only map's, as patches/interiors.py does for a room's town
        cp = os.path.join(ROOT, 'data', 'interiors', f"{r['zone']}.json")
        cfg = json.load(open(cp)) if os.path.exists(cp) else {}
        home = next((door_at[k][0] for _, k in targets if k in door_at), None)
        if home is not None and cfg.get('parent') == 389 and not name.startswith('LittlerootTown') and \
                hd['parent'] != home:
            town = headers[home]
            hd['parent'], hd['place'] = home, town['place']
            if 'bgm' not in cfg: hd['bgm0'], hd['bgm1'], hd['bgm2'], hd['bgm3'] = town['bgm0'], town['bgm1'], town['bgm2'], town['bgm3']
            towns.append(f"{name}: zone {home}")
    zoneheaders.save(files, headers, hentries)
    narcio.save(files, 126, ents)
    return 'room exits: ' + ('; '.join(done) or 'none changed') + (f'; NOT CHANGED: {odd}' if odd else '') + \
        (f"; rooms' town: {', '.join(towns)}" if towns else '')

def apply(files):
    world = json.load(open(os.path.join(W, 'world.json')))
    if not world.get('standalone'): return 'no warp-only maps in world.json'
    index, msg = build_pack(files, world)
    a13 = os.path.join(files, 'a', '0', '1', '3')
    raw = bytearray(open(a13, 'rb').read())
    tex_msg = map_textures(files, world, raw)
    for area in {g['area'] for g in world['standalone']}:
        struct.pack_into('<H', raw, area * 10, index)        # u16 building pack, u16 texture set, ...
    for g in world['standalone']:   # a group's own terrain SRT animation (u8 at +4, a/0/6/8 entry; AreaData_GetSRTAnmID,
        if g.get('srt_anim') is not None:      # ov036 fieldmap.c:1509): Mt. Chimney's area 407 takes Reversal
            raw[g['area'] * 10 + 4] = g['srt_anim']    # Mountain's (29: its lava scrolls; buildings_audit 2026-10-08)
    tex_msg += '; ' + seasonal_areas(files, world, raw)
    if os.path.islink(a13): os.unlink(a13)
    open(a13, 'wb').write(raw)
    msg += '; ' + tex_msg + '; ' + fix_room_exits(files, world)
    print('patch standalone:', msg, file=sys.stderr)      # (agent_build.sh greps stdout)
    return msg
