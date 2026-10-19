"""Sapphire's fixed weather (data/hoenn_weather.json; user decision 2026-10-07, weather agent).

How Black 2 does weather [code]: one weather per zone, the zone header's 0x1C bits 0-5 (GetZoneEnvFlagsWeather, arm9
0x0201899c), asked for by GetWeatherAll (arm9 0x02032e94: GetDefaultWeatherValue, the Entralink / Route 7 / birthday
weathers, then the calendar a/0/9/6 only while the save's season is the real one and only for its 24 zones, else the
header). Every zone change sets it again: Field_SwapZoneByMatrix (walking into another zone's cell or zone rectangle,
ov036 fieldmap.c) -> Field_SwapWeather -> ResetWeather -> the weather system changes over; a warp loads the new zone's.
So a weather that covers only part of a map needs a zone of its own there:

- 'parts': a zone that copies the map zone's header (same scripts, init scripts, text, entities, encounters, camera
  box, place name, fly point: the same file numbers, so its people, signs, triggers and doors are the map's own and
  nothing about them changes) with its own weather and, with 'bgm_zone', that Black 2 zone's four BGM fields.
  patches/hoenn_world.py calls outdoor_headers() when it writes the world's zone headers and puts lookup_rects() into
  its ITCM zone lookup (the banner code patch: GetZoneIDAtMatrixXZWorld -> ZoneLookup), so the game swaps to the part's
  zone on the first step onto one of its tiles: weather, music (Field_SwapZoneBGM), and the people of the same file
  respawned (DeleteAllActors + Field_HotswapSpawnActors). The banner does not show again: the place name is the
  same (ov036 IsLocNameIdxChanged).
- 'maps': a whole outdoor map's zone gets the weather (outdoor_headers()).
- 'rooms': a room's or cave's zone gets the weather (apply(), after the interiors patch writes their headers).
- fog: every Hoenn chunk and Hoenn-made model takes the material fog flag Black 2's own have (fog_everything below):
  every Black 2 weather draws its haze with the 3D fog, which skipped our models.
apply() also points every door that arrives inside a part (rooms' and caves' exits: Desert Ruins, Glass Workshop,
Mt. Chimney -> Jagged Pass, Mt. Pyre's summit -> outside) at the part's zone, same warp index (same entity file), so the
player arrives in the part's weather instead of swapping after the first step.

Zones of the parts: Black 2 zones no Hoenn map or room uses and no zone-keyed table names (gimmick, Flash, fog, ISS,
calendar, script plugins, respawn table, the arm9 zone checks): 610-613 (Underground Ruins / Regi chambers in Unova);
550, 586, 608, 609 (Route 119's and Route 123's sunny ends, v166_fixes: checked against the same tables)."""
import os, json, struct

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
DATA = os.path.join(ROOT, 'data', 'hoenn_weather.json')
WEATHER_MASK = 0x3F                     # zone header weather_word bits 0-5 (zone_header.inc)

def data():
    if not os.path.exists(DATA): return {'parts': {}, 'maps': {}, 'rooms': {}}
    import version          # (Emerald, emerald_world 2026-10-12: data/emerald/hoenn_weather.json deep-merged over it)
    return version.load_json(DATA)

def _map_zone(world, name):
    zs = [int(z) for z, v in world['zones'].items() if name in v.get('maps', [])]
    assert len(zs) == 1, f'{name}: zones {zs} in world.json'
    return zs[0]

def _main_origin(name):
    """World tile of Sapphire's (0, 0) of a main-matrix map: b2tools/world.py compose()."""
    cfg = json.load(open(os.path.join(ROOT, 'data', 'hoenn_world.json')))
    L = json.load(open(os.path.join(ROOT, 'data', 'hoenn_world_layout.json')))['main']['maps'][name]
    M = cfg['margin_cells'] * 32
    sx, sz = cfg.get('shift', {}).get(name, [0, 0])
    return L['tile_x'] + M + sx, L['tile_z'] + M + sz + cfg.get('pad_north', {}).get(name, 0)

def group_matrices(world):
    """Matrix id of each warp-only group: appended after the Hoenn matrix in world.json's order (hoenn_world.apply)."""
    return {g['group']: world['matrix'] + 1 + i for i, g in enumerate(world.get('standalone', []))}

def parts(world):
    """[(name, part, src zone, matrix, [[x0, z0, x1, z1] in that matrix's tiles])] for the parts of built maps."""
    gm = group_matrices(world)
    group_of = {m: g for g in world.get('standalone', []) for m in g.get('origins', {})}
    zone_owner = {(c['cx'], c['cz']): c['zone'] for c in world['cells']}
    taken = {m['zone'] for m in json.load(open(os.path.join(ROOT, 'data', 'hoenn_zones.json')))['maps'].values()}
    taken |= {r['zone'] for r in json.load(open(os.path.join(ROOT, 'data', 'hoenn_interiors.json')))['rooms'].values()}
    clash = sorted(p['zone'] for p in data()['parts'].values() if p['zone'] in taken)
    assert not clash, f'fixed weather: zones {clash} (data/hoenn_weather.json parts) are given to maps or rooms too'
    out = []
    for name, p in data()['parts'].items():
        m = p['map']
        if not any(m in v.get('maps', []) for v in world['zones'].values()): continue    # (map not built)
        src = _map_zone(world, m)
        assert str(p['zone']) not in world['zones'], f"{name}: zone {p['zone']} is a world zone"
        if m in group_of:
            g = group_of[m]; ox, oz = g['origins'][m]; matrix = gm[g['group']]
            owner = {(c['cx'], c['cz']): c['zone'] for c in g['cells']}
        else:
            (ox, oz), matrix, owner = _main_origin(m), world['matrix'], zone_owner
        rects = []
        own_rects = [zr for zr in world.get('zone_rects', []) if zr[4] == src] if matrix == world['matrix'] else []
        for x0, y0, x1, y1 in p['rects']:
            # only tiles whose zone is the map's: its cells, and its own zone rectangles in other zones' cells (world.py
            # zone_rects: every map's tiles are its zone since 2026-10-08, zone_edges). Cells of other zones and other
            # maps' zone rectangles keep theirs: the part shares the map zone's people, so it must not cover another zone's
            r = [ox + x0, oz + y0, ox + x1, oz + y1]
            for cz in range(r[1] // 32, r[3] // 32 + 1):
                for cx in range(r[0] // 32, r[2] // 32 + 1):
                    c = [max(r[0], cx * 32), max(r[1], cz * 32), min(r[2], cx * 32 + 31), min(r[3], cz * 32 + 31)]
                    if owner.get((cx, cz)) == src: pieces = [c]
                    else:                    # (the map's own rectangle in this cell: the part's tiles inside it)
                        pieces = [[max(c[0], zr[0]), max(c[1], zr[1]), min(c[2], zr[2]), min(c[3], zr[3])] for zr in own_rects]
                        pieces = [q for q in pieces if q[0] <= q[2] and q[1] <= q[3]]
                    for q in pieces:
                        if matrix == world['matrix']:
                            for zr in world.get('zone_rects', []):
                                assert zr[4] == src or zr[2] < q[0] or zr[0] > q[2] or zr[3] < q[1] or zr[1] > q[3], \
                                    f'{name}: {q} overlaps zone rectangle {zr}'
                        rects.append(q)
        out.append((name, p, src, matrix, _merge(rects)))
    return out

def _merge(rects):
    """Join rectangles that the cell grid split (same columns and touching rows, or same rows and touching columns)."""
    rects = [list(r) for r in rects]
    again = True
    while again:
        again = False
        for i, a in enumerate(rects):
            for j, b in enumerate(rects):
                if i != j and ((a[0], a[2]) == (b[0], b[2]) and a[3] + 1 == b[1] or
                               (a[1], a[3]) == (b[1], b[3]) and a[2] + 1 == b[0]):
                    a[2], a[3] = b[2], b[3]; del rects[j]; again = True; break
            if again: break
    return rects

# ---- fog: every Black 2 weather draws part of its look with the 3D fog (its overlays 75-78 all call ov036
# func_ov036_0219990c: FieldFog_SetDepthShift/SetOffset/SetEnabled; mist 9 = offset 0x7fdf -> 0x7f78, depth shift 9,
# white-grey 0x6318: a haze over the far part of the screen). The DS fogs only polygons whose material polygon
# attribute has bit 15 (GX_POLYGON_ATTR fog enable): Black 2's map chunks and building models have it (0x001f8081;
# its exceptions are effect materials such as the warp pads), ours did not (CTRMap's NSBMD writer: 0x001f0081), so
# the weathers showed only their particles [bytes][test]. User decision 2026-10-07: the flag on every Hoenn terrain
# chunk and every Hoenn-made building/furniture model (rooms included), so every weather's haze shows (ch10's storm,
# the mist, the sandstorm). The fog is off in every Hoenn zone without such a weather (zone_effects removed our zones
# from the zone fog table a/0/8/0 #29), so a clear zone looks the same [test].
POLY_FOG = 0x8000

def _dict(d, o):
    """NNSG3dResDict entries (data bytes) at o."""
    n = d[o + 1]; e = o + struct.unpack_from('<H', d, o + 6)[0]
    unit = struct.unpack_from('<H', d, e)[0]
    return [d[e + 4 + unit * i: e + 4 + unit * (i + 1)] for i in range(n)]

# Materials left without the fog flag (underwater_polish 2026-10-08): "d0ana_002", the inside cave arch's dark tunnel,
# and "d29_gake2d", the cave builder's black void in mist caves (b2tools/models_cave_mist.py; no other Hoenn chunk uses
# it). A mist weather also swaps the field light (a/0/6/1 file 1: fog 0x6318, clear colour = the sky's light blue by
# day), so the fogged black turned grey and the uncovered background light blue; unfogged it stays black.
NO_FOG = {'d0ana_002', 'd29_gake2d'}

def _dict_names(d, o):
    """NNSG3dResDict names (16 bytes each, after the data entries) at o."""
    n = d[o + 1]; e = o + struct.unpack_from('<H', d, o + 6)[0]
    unit = struct.unpack_from('<H', d, e)[0]
    at = e + 4 + unit * n
    return [bytes(d[at + 16 * i:at + 16 * i + 16]).rstrip(b'\0').decode('ascii', 'replace') for i in range(n)]

def nsbmd_fog(data):
    """The NSBMD with the fog flag in every material's polygon attribute (NNSG3dResMatData +12), except NO_FOG's."""
    d = bytearray(data)
    assert d[:4] == b'BMD0'
    mdl = struct.unpack_from('<I', d, 16)[0]
    assert d[mdl:mdl + 4] == b'MDL0'
    for ent in _dict(d, mdl + 8):
        m = mdl + struct.unpack_from('<I', ent, 0)[0]
        mo = m + struct.unpack_from('<I', d, m + 8)[0]          # NNSG3dResMdl ofsMat
        for me, name in zip(_dict(d, mo + 4), _dict_names(d, mo + 4)):
            if name in NO_FOG: continue
            at = mo + struct.unpack_from('<I', me, 0)[0] + 12
            struct.pack_into('<I', d, at, struct.unpack_from('<I', d, at)[0] | POLY_FOG)
    return bytes(d)

def _fog_container(buf, keep=frozenset()):
    """Set the fog flag in place in every BMD0 section of a GF container (chunk 'WB'/'GC', building pack 'AB'),
    skipping models whose bytes are in `keep` (Black 2's own: left as Black 2 made them). -> models changed."""
    import hashlib
    n = struct.unpack_from('<H', buf, 2)[0]
    offs = struct.unpack_from(f'<{n + 1}I', buf, 4)
    done = 0
    for i in range(n):
        a, b = offs[i], offs[i + 1]
        if bytes(buf[a:a + 4]) != b'BMD0' or (keep and hashlib.sha1(bytes(buf[a:b])).digest() in keep): continue
        new = nsbmd_fog(bytes(buf[a:b]))
        # (and every polygon's first vertex absolute: CTRMap's writer may start one relative to (0, 0, 0), which the DS
        # takes from the last vertex drawn: a sheared triangle; b2tools/nsbmd_fix.py, buildings_audit 2026-10-08)
        from nsbmd_fix import fix_first_vertex
        new = fix_first_vertex(new)[0]
        if new != bytes(buf[a:b]): buf[a:b] = new; done += 1
    return done

def fog_everything(files, headers, first_chunk):
    """The fog flag on every chunk from first_chunk on (Hoenn's: world cells, warp-only maps, other layouts, rooms,
    caves) and on every model of the building packs our zones' areas use that is not Black 2's own."""
    import hashlib, glob, narcio, b2files
    chunks = narcio.load(files, 8)
    n_chunks = 0
    for c in range(first_chunk, len(chunks)):
        buf = bytearray(chunks[c])
        if bytes(buf[:2]) in (b'WB', b'GC', b'NG', b'RD') and _fog_container(buf): chunks[c] = bytes(buf); n_chunks += 1
    narcio.save(files, 8, chunks)
    zs = {m['zone'] for m in json.load(open(os.path.join(ROOT, 'data', 'hoenn_zones.json')))['maps'].values()}
    zs |= {r['zone'] for r in json.load(open(os.path.join(ROOT, 'data', 'hoenn_interiors.json')))['rooms'].values()}
    zs |= set(range(389, 397)) | {p['zone'] for p in data()['parts'].values()}
    raw = open(os.path.join(files, 'a', '0', '1', '3'), 'rb').read()
    packs = set()
    for z in zs:
        a = headers[z]['area']
        for area in (range(a, a + 4) if 2 <= a <= 281 else [a]):         # (2-281: the game adds the season)
            pack, _, _, _, ext = struct.unpack_from('<HHBBB', raw, area * 10)
            packs.add((ext, pack))
    out = []
    for ext in (1, 0):
        arc = 225 if ext else 226                                         # exterior / interior building packs
        vanilla = set()
        for e in b2files.narc_entries(b2files.arc_path(os.path.join(ROOT, 'external', 'pokebw2', 'build', 'b2_us', 'files'), arc)):
            if e[:2] == b'AB':
                magic, secs = b2files.gf_container(e)
                vanilla |= {hashlib.sha1(s).digest() for s in secs if s[:4] == b'BMD0'}
        entries = narcio.load(files, arc)
        for p in sorted(pk for x, pk in packs if x == ext and pk < len(entries)):
            buf = bytearray(entries[p])
            if bytes(buf[:2]) != b'AB': continue
            k = _fog_container(buf, vanilla)
            if k: entries[p] = bytes(buf); out.append(f"{'ext' if ext else 'int'} pack {p}: {k} models")
        narcio.save(files, arc, entries)
    return f'fog flag: {n_chunks} chunks from {first_chunk}, ' + ', '.join(out)

def lookup_rects(world):
    """{matrix: [[x0, z0, x1, z1, zone], ...]} for patches/hoenn_world.py's ZoneLookup (first match wins: these go
    before world.json's zone_rects on the Hoenn matrix)."""
    out = {}
    for name, p, src, matrix, rects in parts(world):
        out.setdefault(matrix, []).extend(r + [p['zone']] for r in rects)
    return out

def outdoor_headers(headers, bgm_src, world):
    """The parts' zone headers (copies of their map zone's, own weather/music) and the whole maps' weather. headers:
    the zone headers as patches/hoenn_world.py has just written them; bgm_src: Black 2's headers (for bgm_zone)."""
    done = []
    for name, p, src, matrix, rects in parts(world):
        hd = dict(headers[src])
        hd['weather_word'] = (hd['weather_word'] & ~WEATHER_MASK) | p['weather']
        if p.get('bgm_zone') is not None:
            b = bgm_src[p['bgm_zone']]
            hd['bgm0'], hd['bgm1'], hd['bgm2'], hd['bgm3'] = b['bgm0'], b['bgm1'], b['bgm2'], b['bgm3']
        headers[p['zone']] = hd
        done.append(f"{name}: zone {p['zone']} = zone {src} + weather {p['weather']}"
                    + (f", music of zone {p['bgm_zone']}" if p.get('bgm_zone') is not None else '')
                    + f", {len(rects)} rectangles on matrix {matrix}")
    for m, v in data()['maps'].items():
        if not any(m in z.get('maps', []) for z in world['zones'].values()): continue
        zid = _map_zone(world, m)
        headers[zid]['weather_word'] = (headers[zid]['weather_word'] & ~WEATHER_MASK) | v['weather']
        done.append(f"{m}: zone {zid} weather {v['weather']}")
    return 'fixed weather: ' + '; '.join(done)

# The falling "ash" (light snow, weather 1: ov036 WEATHER_OVERLAYS entry 1 = ov075's 0x021ea364 {a/0/5/5 23 NCGR, 24 NCLR,
# 22 NCER, 21 NANR}) recoloured grey (user 2026-10-17: "make the falling flakes especially greyer"). Hoenn uses weather 1
# only for the ash (data/hoenn_weather.json: Route 113, Jagged Pass, Mt. Chimney), so Black 2's own palette is changed.
ASH_FLAKES_ARC, ASH_FLAKES_PAL = 55, 24
ASH_FLAKES = {1: (120, 116, 112), 2: (100, 96, 92)}       # Black 2: (224, 232, 240), (216, 224, 232)

def ash_flakes(files):
    import struct, narcio
    e = narcio.load(files, ASH_FLAKES_ARC)
    d = bytearray(e[ASH_FLAKES_PAL])
    assert d[:4] == b'RLCN', 'a/0/5/5 24 is not the snow palette'
    for i, (r, g, b) in ASH_FLAKES.items():
        struct.pack_into('<H', d, 0x28 + 2 * i, (r >> 3) | ((g >> 3) << 5) | ((b >> 3) << 10))
    e[ASH_FLAKES_PAL] = bytes(d)
    narcio.save(files, ASH_FLAKES_ARC, e)

def apply(files):
    """Rooms' weather (after the interiors patch), the fog flag on every Hoenn chunk and model (after every patch
    that writes them: listed after them) and the doors that arrive inside a part."""
    ash_flakes(files)
    import sys
    sys.path.insert(0, os.path.join(ROOT, 'b2tools'))
    import narcio, zoneheaders
    from zones import parse_entities, build_entities
    W = os.environ.get('HOENN_WORLD_DIR') or os.path.join(ROOT, 'work', 'world')
    world = json.load(open(os.path.join(W, 'world.json')))
    headers, hentries = zoneheaders.load(files)
    rooms = json.load(open(os.path.join(ROOT, 'data', 'hoenn_interiors.json')))['rooms']
    done = []
    for name, v in data()['rooms'].items():
        if name not in rooms: continue
        z = rooms[name]['zone']
        headers[z]['weather_word'] = (headers[z]['weather_word'] & ~WEATHER_MASK) | v['weather']
        done.append(f"{name} (zone {z}) weather {v['weather']}")
    zoneheaders.save(files, headers, hentries)
    done.append(fog_everything(files, headers, min(c['chunk'] for c in world['cells'])))
    # doors arriving inside a part: (dest zone = the map's zone, dest warp = a warp of its file standing in a part)
    ents = narcio.load(files, 126)
    inside = {}
    for name, p, src, matrix, rects in parts(world):
        assert headers[p['zone']]['entities'] == headers[src]['entities'], f'{name}: zone {p["zone"]} header not written'
        for i, wp in enumerate(parse_entities(ents[headers[src]['entities']])[0]['warps']):
            tx, tz = (wp['x'] - 8) // 16, (wp['z'] - 8) // 16
            if any(x0 <= tx <= x1 and z0 <= tz <= z1 for x0, z0, x1, z1 in rects): inside[(src, i)] = (p['zone'], name)
    ours = {m['zone'] for m in json.load(open(os.path.join(ROOT, 'data', 'hoenn_zones.json')))['maps'].values()}
    ours |= {r['zone'] for r in rooms.values()}
    for z in sorted(ours):
        idx = headers[z]['entities']
        e, _ = parse_entities(ents[idx])
        hit = [i for i, wp in enumerate(e['warps']) if (wp['dest_zone'], wp['dest_warp']) in inside]
        if not hit: continue
        for i in hit:
            wp = e['warps'][i]; new, part = inside[(wp['dest_zone'], wp['dest_warp'])]
            done.append(f"zone {z} warp {i} -> zone {new} ({part}) warp {wp['dest_warp']}")
            wp['dest_zone'] = new
        ents[idx] = build_entities(e, ents[idx])
    narcio.save(files, 126, ents)
    return '; '.join(done) or 'nothing'
