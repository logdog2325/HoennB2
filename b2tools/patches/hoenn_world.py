"""Install the Hoenn overworld built by b2tools/world.py (work/world/): chunks appended to a/0/0/8 from
first_chunk on, the Hoenn matrix appended to a/0/0/9, the built zones' headers pointed at it (matrix, area, fly
point), and each zone's entities (signs, NPCs, warp positions) at Hoenn coordinates. Unova's matrix 0 and chunks
are left as they are. The warp-only maps (world.json "standalone", data/hoenn_standalone.json) follow: their chunks,
one matrix per group, their zones on that matrix and on the standalone area (a copy of area 3 here), and their doors
in Sapphire's order; doors between outdoor maps name their destination as Sapphire's map and warp id (to_map, to_id),
resolved here against every zone's door list."""
import os, json, struct, glob
import narcio, zoneheaders
import sys as _sys
_sys.path.insert(0, os.path.dirname(__file__))
from b2files import gf_container_build
from zones import parse_entities, build_entities
_sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import version  # noqa: E402  (Ruby: data/versions.json "doors" retargets doors, version_doors below)

ROOT = os.path.join(os.path.dirname(__file__), '..', '..')
W = os.environ.get('HOENN_WORLD_DIR') or os.path.join(ROOT, 'work', 'world')
NO_NPC_CACHE = 24    # zone header npc_cache: >= 24 = no a/0/5/7 list (ov035 event_mapchange.c: FldActSys_ClearCache)

def version_doors(world):
    """data/versions.json "doors" of this version: a door of world.json (Sapphire map + warp id, same index in both
    versions, so savestates and scripts' warp numbers fit both) leads to another room, e.g. Ruby's Lilycove hideout
    door to Magma Hideout 1F instead of Aqua Hideout 1F. Only when the room's zone file is installed in this version
    (data/interiors[/ruby]/<zone>.json); otherwise the door keeps Sapphire's destination."""
    rules = version.versions_json().get('doors', {}).get(version.VERSION, [])
    if not rules: return []
    rooms = json.load(open(os.path.join(ROOT, 'data', 'hoenn_interiors.json')))['rooms']
    installed = {int(os.path.basename(f)[:-5]) for f in version.overlay(os.path.join(ROOT, 'data', 'interiors'), '*.json')}
    done = []
    for r in rules:
        zone = rooms[r['dest']]['zone']
        doors = [d for z in world['zones'].values() for d in z.get('doors', []) if (d['map'], d['id']) == (r['map'], r['id'])]
        if zone not in installed or not doors:
            done.append(f"{r['map']} warp {r['id']}: kept ({r['dest']} zone {zone} not installed)" if doors else
                        f"{r['map']} warp {r['id']}: no such door")
            continue
        for d in doors: d['dest_zone'], d['dest_warp'] = zone, int(r['dest_warp'])
        done.append(f"{r['map']} warp {r['id']} -> {r['dest']} (zone {zone}, warp {r['dest_warp']})")
    return done

def _terrain(d):
    """A cell's terrain model with Black 2's own round-tree material values (b2tools/nsbmd_fix.py tree_materials)."""
    from nsbmd_fix import tree_materials
    return tree_materials(open(os.path.join(d, 'terrain.nsbmd'), 'rb').read())[0]

def _chunk(d):
    """A cell's chunk for a/0/0/8: 'WB' (model, terrain, buildings), or 'GC' (model, terrain layer 0, terrain layer 1,
    buildings) when world.py wrote a second collision layer (collision1.per: walk-under bridges, world.py bridge_layers;
    ov036 FIELD_CHUNK_VTABLES picks the accessor by the chunk's magic, outdoors as in caves: patches/interiors.py)."""
    p1 = os.path.join(d, 'collision1.per')
    layers = [open(os.path.join(d, 'collision.per'), 'rb').read()] + ([open(p1, 'rb').read()] if os.path.exists(p1) else [])
    return gf_container_build('GC' if len(layers) > 1 else 'WB',
                              [_terrain(d)] + layers + [open(os.path.join(d, 'placements.bin'), 'rb').read()])

def apply(files):
    world = json.load(open(os.path.join(W, 'world.json')))
    retargeted = version_doors(world)
    cells = sorted(world['cells'], key=lambda c: c['chunk'])
    chunks = narcio.load(files, 8)
    assert len(chunks) == cells[0]['chunk'], f'a/0/0/8 has {len(chunks)} entries, expected {cells[0]["chunk"]}'
    fw = _fixed_weather()      # (the material fog flag of every Hoenn chunk and model: patches/fixed_weather.py apply)
    for c in cells:
        d = os.path.join(W, 'cells', f'{c["cx"]:02d}_{c["cz"]:02d}')
        chunks.append(_chunk(d))
    # warp-only maps (world.py build_standalone): their unique chunks next, each group on its own matrix after the
    # Hoenn matrix, in world.json's order (identical cells share a chunk)
    standalone = world.get('standalone', [])
    done_dirs = {}
    for g in standalone:
        for c in sorted(g['cells'], key=lambda c: c['chunk']):
            if c['chunk'] in done_dirs: continue
            assert c['chunk'] == len(chunks), f"standalone chunk {c['chunk']} would be entry {len(chunks)}"
            d = os.path.join(W, 'cells', c['dir'])
            chunks.append(_chunk(d))
            done_dirs[c['chunk']] = c['dir']
    # other layouts of a map (world.py build_alts, data/hoenn_world.json "alt_layouts": Route 131 after the game):
    # their cells' chunks last, swapped for the cell's own chunk by a/0/1/0 map replacements (kind 0 = one chunk id
    # for another in the matrix, ov012 map_matrix.c MapReplace_Patch, applied when the matrix loads) while map replace
    # event uid 'event' is set (condition = uid + 3, map_replace.c EVENT_MAP_REPLACE_TABLE); same 16-byte layout as
    # Black 2's own event entries, e.g. (0, kind 0, cond 7, 338, 406, 0, 0, 0, 0xFFFF)
    replaces = []
    for a in sorted(world.get('alt_cells', []), key=lambda a: a['chunk']):
        assert a['chunk'] == len(chunks), f"alt chunk {a['chunk']} would be entry {len(chunks)}"
        d = os.path.join(W, 'cells', a['dir'])
        chunks.append(_chunk(d))
        # ("cond", Emerald's abnormal weather: emerald_postgame.c's own conditions 0x81-0x90 in place of an event's)
        replaces.append(struct.pack('<HBB6H', world['matrix'], 0, a['cond'] if 'cond' in a else a['event'] + 3,
                                    a['base_chunk'], a['chunk'], 0, 0, 0, 0xFFFF))
    # (a warp-only map's other layout, world.py group_alts: Emerald's Jagged Pass mouth; the same entries on its group's
    # own matrix, which comes after the Hoenn matrix in the groups' order below. Sapphire and Ruby have none)
    gmat = {g['group']: world['matrix'] + 1 + i for i, g in enumerate(standalone)}
    galts = sorted(((g['group'], a) for g in standalone for a in g.get('alt_cells', [])), key=lambda ga: ga[1]['chunk'])
    for gname, a in galts:
        assert a['chunk'] == len(chunks), f"{gname} alt chunk {a['chunk']} would be entry {len(chunks)}"
        d = os.path.join(W, 'cells', a['dir'])
        chunks.append(_chunk(d))
        replaces.append(struct.pack('<HBB6H', gmat[gname], 0, a['event'] + 3, a['base_chunk'], a['chunk'], 0, 0, 0, 0xFFFF))
    narcio.save(files, 8, chunks)
    if replaces:                              # (a/0/1/0 has a RESERVE in build_rom.py)
        mr = narcio.load(files, 10)
        for m in [world['matrix']] + [gmat[g] for g, _ in galts]:
            assert not any(struct.unpack_from('<H', mr[0], i)[0] == m for i in range(0, len(mr[0]), 16)), \
                f"a/0/1/0 already has entries for matrix {m}"
        if any(a.get('event') == 1 for a in world.get('alt_cells', [])) or any(a['event'] == 1 for _, a in galts):
            # event 1 (work 0x4032): Black 2 sets it from no script and no code, and its own four entries load other
            # matrices over 342/343/347/350, which HoennB2's rooms rewrite (Glass Workshop, Fossil Maniac's house, Day
            # Care, Weather Institute 2F): dropped, so the event only swaps our cells (emerald_integrate 2026-10-12)
            mr[0] = b''.join(mr[0][i:i + 16] for i in range(0, len(mr[0]), 16) if mr[0][i + 3] != 1 + 3)
        mr[0] = mr[0] + b''.join(replaces); narcio.save(files, 10, mr)

    w, h = world['width'], world['height']
    ids = [0xFFFFFFFF] * (w * h); zs = [0] * (w * h)
    for c in cells:
        ids[c['cz'] * w + c['cx']] = c['chunk']; zs[c['cz'] * w + c['cx']] = c['zone']
    mats = narcio.load(files, 9)
    assert len(mats) == world['matrix'], f'a/0/0/9 has {len(mats)} entries, expected {world["matrix"]}'
    mats.append(struct.pack('<HHHH', 1, 0, w, h) + struct.pack(f'<{w * h}I', *ids) + struct.pack(f'<{w * h}I', *zs))
    group_matrix = {}
    for g in standalone:                  # format 1 like the Hoenn matrix: a zone per cell (the Safari Zone's four)
        gw, gh = g['width'], g['height']
        gids = [0xFFFFFFFF] * (gw * gh); gzs = [0] * (gw * gh)
        for c in g['cells']:
            gids[c['cz'] * gw + c['cx']] = c['chunk']; gzs[c['cz'] * gw + c['cx']] = c['zone']
        group_matrix[g['group']] = len(mats)
        assert group_matrix[g['group']] == gmat[g['group']], (g['group'], group_matrix[g['group']], gmat[g['group']])
        mats.append(struct.pack('<HHHH', 1, 0, gw, gh) + struct.pack(f'<{gw * gh}I', *gids) + struct.pack(f'<{gw * gh}I', *gzs))
    narcio.save(files, 9, mats)
    if standalone:                        # their area: a copy of area 3 (Hoenn's summer record: texture set 3, pack 0,
        a13 = os.path.join(files, 'a', '0', '1', '3')    # lights); patches/standalone.py gives it its own pack
        raw = bytearray(open(a13, 'rb').read())
        for area in {g['area'] for g in standalone}:
            assert area >= 282, f'area {area} is seasonal (the game adds the season to areas 2-281)'
            raw[area * 10:area * 10 + 10] = raw[30:40]
        if os.path.islink(a13): os.unlink(a13)
        open(a13, 'wb').write(raw)

    headers, hentries = zoneheaders.load(files)
    bgm_src = [dict(h) for h in headers]  # (zone headers before any change: music of a Black 2 zone)
    kind_template = {'town': dict(headers[389]), 'route': dict(headers[317])}    # Nuvema / Route 1 as Black 2 made them
    enc_path = os.path.join(ROOT, 'data', 'hoenn_encounters.json')        # converter/gen_encounters.py
    enc_files = json.load(open(enc_path)) if os.path.exists(enc_path) else {}
    ents = narcio.load(files, 126)
    done = []
    # door indices of every zone (its Black 2 warps first, then world.json's doors), so a door to another outdoor map
    # (warp-only maps <-> the Hoenn matrix: to_map, to_id = Sapphire's map and warp id) finds its destination
    door_at = {}
    for zid, z in world['zones'].items():
        base = len(parse_entities(ents[headers[int(zid)]['entities']])[0]['warps'])
        for k, d in enumerate(z.get('doors', [])):    # (a door's copy in the zone of the cell it stands in wins:
            if d.get('foreign') or (d['map'], d['id']) not in door_at:   # world.py foreign_doors, as gen_caves.py)
                door_at[(d['map'], d['id'])] = (int(zid), base + k)
        for d in z.get('slot_doors', []): door_at[(d['map'], d['id'])] = (int(zid), d['slot'])
    unresolved = []
    for zid, z in world['zones'].items():
        zid = int(zid); hd = headers[zid]
        t = kind_template[z.get('kind', 'route')]
        if zid not in (389, 317, 397):
            outdoor = hd['map_type'] == 0
            for k in ('map_type', 'flags', 'cam_bound', 'icon_word'): hd[k] = t[k]
            hd['weather_word'] = t['weather_word']          # weather 0, projection 1, camera 0 (Sapphire weather: later)
            if not outdoor: hd['bgm0'], hd['bgm1'], hd['bgm2'], hd['bgm3'] = t['bgm0'], t['bgm1'], t['bgm2'], t['bgm3']
        # No preloaded people sprites (npc_cache 24 = none, as 562 of Black 2's 615 zones; notes/NPC_LIMIT.md). Nuvema's
        # and Route 1's list (a/0/5/7 file 0) preloaded 19 Unova sprites into the field's 32-entry billboard material
        # cache on every warp into the overworld (ov035 event_mapchange.c LoadMModelSystemInfoCache, ov036
        # FldActSys_LoadCachedBlact), leaving 12 slots for the zone's own people: the rest were invisible.
        hd['npc_cache'] = NO_NPC_CACHE
        tables = [enc_files[m] for m in z.get('maps', []) if m in enc_files]
        # enc_slot is a zone category in Black 2's own headers: 0 towns/cities, 1 routes, 2 caves, 3 forests, 6 none
        if tables: hd['encounters'], hd['enc_slot'] = tables[0], 0 if z.get('kind') == 'town' else 1
        elif zid not in (389, 317, 397): hd['encounters'], hd['enc_slot'] = 0x1FFF, 0
        hd['parent'] = zid
        hd['place'] = z.get('place', hd['place']); hd['place_display'] = z.get('place_display', t['place_display'])
        hd['matrix'], hd['area'] = world['matrix'], world['area']
        if 'group' in z:                  # a warp-only map: its own matrix and area
            g = next(g for g in standalone if g['group'] == z['group'])
            hd['matrix'], hd['area'] = group_matrix[z['group']], g['area']
            # transition effect (flags bits 0-4, read only by Get{In,Out}TransitionTypeBetweenZones, ov036): Black 2's
            # outdoor -> outdoor warps (effect 0 -> 0) play the gate-exit wipe that writes the season in the corner
            # ("Summer", tested on Petalburg Woods -> Route 104). Effect 1 (indoor) gives the building fades (black,
            # as Sapphire's warps); effect 3 (cave) would fade to white leaving, as Black 2's caves. Either way you
            # arrive on the warp and step off it against its direction (tested both)
            hd['flags'] = (hd['flags'] & ~31) | g.get('effect', 1)
            if g.get('bgm_zone') is not None:  # music: a Black 2 zone's (data/hoenn_standalone.json 'bgm_zone')
                b = bgm_src[g['bgm_zone']]
                hd['bgm0'], hd['bgm1'], hd['bgm2'], hd['bgm3'] = b['bgm0'], b['bgm1'], b['bgm2'], b['bgm3']
        hd['fly_x'], hd['fly_y'], hd['fly_z'] = z['fly'][0], 0, z['fly'][1]
        e, _ = parse_entities(ents[hd['entities']])
        template = dict(e['npcs'][0]) if e['npcs'] else dict(uid=0, model=0, move=0, evtype=0, flag=0, script=0, dir=1,
                                                              p0=0, p1=0, p2=0, areaw=0, areah=0, rail=0, x=0, z=0, y=0)
        e['signs'] = z['signs']
        e['npcs'] = [dict(template, **dict(dict(uid=i, evtype=0, rail=0, y=0, flag=0), **n)) for i, n in enumerate(z['npcs'])]
        for i, wp in enumerate(e['warps']):
            wp['x'], wp['y'], wp['z'] = z['warps'].get(str(i), z['park'])
            if str(i) not in z['warps']: wp['w'], wp['h'] = 1, 1
        for d in z.get('slot_doors', []): # a hand-made town's door slot now leads into its Hoenn room (world.py)
            e['warps'][d['slot']].update(dest_zone=d['dest_zone'], dest_warp=d['dest_warp'])
        for d in z.get('doors', []):      # doors to Hoenn interiors (world.py), after Black 2's own slots; their
            d['index'] = len(e['warps'])  # indices are what the rooms' exits point at (converter/gen_interiors.py)
            if 'to_map' in d:             # to another outdoor map (warp-only maps): its door of that Sapphire warp
                if (d['to_map'], d['to_id']) in door_at: d['dest_zone'], d['dest_warp'] = door_at[(d['to_map'], d['to_id'])]
                else: unresolved.append(f"{d['map']} warp {d['id']} -> {d['to_map']} {d['to_id']}")
            if d.get('parked'):              # (emerald_caves 2026-10-12, world.py "doors_parked": Emerald's Terra Cave
                d['x'], d['y'], d['z'] = z['park']   # mouths) leads into its room, parked off the map until a script
            if d.get('dest_zone') is None:   # moves it in (ObjInitWarpGPos); nowhere to go yet: parked, leading to itself
                d['dest_zone'], d['dest_warp'] = zid, d['index']
                d['x'], d['y'], d['z'] = z['park']
                unresolved.append(f"{d['map']} warp {d['id']} -> {d.get('to_map') or d.get('unresolved')} (parked)")
            e['warps'].append(dict(dest_zone=d['dest_zone'], dest_warp=d['dest_warp'], dir=d.get('dir', 2),
                                   type=d.get('type', 3), rail=0, x=d['x'], y=d['y'], z=d['z'], w=1, h=1, unk=0))
        e['triggers'] = z.get('triggers', [])
        # the zone's map scripts live in its entity file (ov012 eventdata_system.c LoadZoneEntities), not in the
        # script archive: use our source for the zone's init-script number when there is one (src/field_scripts)
        from scripts import assemble, source_for
        init_src = source_for(hd['init_scripts'])
        ents[hd['entities']] = build_entities(e, ents[hd['entities']], assemble(init_src) if init_src else None)
        done.append(f"zone {zid}: {len(e['signs'])} signs, {len(e['npcs'])} NPCs, warps {sorted(z['warps'])}")
    if unresolved: done.append('unresolved doors: ' + ', '.join(unresolved))
    if retargeted: done.append(f'{version.NAME} doors: ' + ', '.join(retargeted))
    # Sapphire's fixed weather (data/hoenn_weather.json, patches/fixed_weather.py): whole maps' weather and the zones
    # of map parts with a weather of their own (copies of their map zone's header; apply_code adds their rectangles)
    assert fw.group_matrices(world) == group_matrix, (fw.group_matrices(world), group_matrix)
    done.append(fw.outdoor_headers(headers, bgm_src, world))
    zoneheaders.save(files, headers, hentries)
    narcio.save(files, 126, ents)
    # weather calendar (a/0/9/6 file 1: u16 count, then {u16 zone, u16 offset} into file 0's 366 daily weathers):
    # Hoenn zones leave it, so Unova's seasonal rain/snow never reaches them (the matching is by zone id only)
    cal = narcio.load(files, 96)
    t1 = bytearray(cal[1]); n = struct.unpack_from('<H', t1, 0)[0]; dropped = []
    for i in range(n):
        if str(struct.unpack_from('<H', t1, 2 + 4 * i)[0]) in world['zones']:
            dropped.append(struct.unpack_from('<H', t1, 2 + 4 * i)[0]); struct.pack_into('<H', t1, 2 + 4 * i, 0xFFFF)
    cal[1] = bytes(t1); narcio.save(files, 96, cal)
    done.append(f'calendar weather removed for zones {dropped}')
    if replaces: done.append(f"alt cells {[(a['cx'], a['cz'], a['base_chunk'], a['chunk']) for a in world.get('alt_cells', [])]} "
                             + (f"{[(g, a['cx'], a['cz'], a['base_chunk'], a['chunk']) for g, a in galts]} " if galts else '')
                             + f"(a/0/1/0: {len(replaces)} entries)")
    return f"{len(cells)} chunks from {cells[0]['chunk']}, matrix {world['matrix']} ({w}x{h}); " + '; '.join(done)

# ---- sub-cell zones (world.json "zone_rects", world.py zone_rects): the banner code patch ---------------------------
# Black 2 asks one function for the zone at a world position on a matrix: GetZoneIDAtMatrixXZWorld (ov012 0x02154af0,
# map_matrix.c: cell = position / 0x1000 / 16 / 32, zone = matrix->zoneIds[cell]). Its callers: ov036 0x02180bd0
# Field_ShouldSwapZone and 0x02180c36 Field_SwapZoneByMatrix (fieldmap.c: the swap on walking into another zone loads
# that zone's entities, BGM, weather, camera box, encounters and shows its banner), ov036 0x021a20c6 UpdatePhenomenon
# (the zone of a rustling-grass spot) and ov086 0x021eab88 (decomp relocs, config/b2_us/arm9/**/relocs.txt); nothing
# else reads matrix->zoneIds (decomp src). The function is replaced by a call to ZoneLookup, which returns the zone of
# the first rectangle holding the position's tile when the matrix is the Hoenn matrix, else the cell's zone exactly
# as before (it calls the original GetChunkCoordOfWorld and GetZoneIDAtMatrixXZ).
#
# Where the code lives: ITCM. The ITCM autoload (code/itcm.yaml: base 0x01FF8000, 5024 bytes, no bss) fills only
# 0x01FF8000-0x01FF93A0 of the 32 KB ITCM; the rest is the SDK's ITCM arena (arena 3, its default start 0x01FF93A0 is
# the literal at arm9 0x0207B400 read by GetUserMemRegionDefaultStart). Black 2 never allocates from arena 3: every
# mem_init_alloc_area / mem_alloc_direct / malloc_device call passes arena 0 (main) or 4 (DTCM) (arm9 0x020053c0,
# 0x020054c0-0x020054e0, 0x02039b24-0x02039ba4, 0x0203a0b4-0x0203a120), no relocation in any module points past
# 0x01FF939C, and the only word in any code binary in 0x01FF93A0-0x01FFFFFF is that arena literal (0x01FFFFxx words in
# ov012/ov180/ov182 are masks/data, not addresses; the stacks are in DTCM). So the autoload grows by the code + table
# (dsd writes the autoload table from itcm.yaml) and the arena start moves past it. Being an autoload it is copied at
# boot: savestates made before this patch hold an ITCM without it (remake them, make_states.py).
ITCM_BASE, ARENA_ITCM_LIT = 0x01FF8000, 0x0207B400
OV012, LOOKUP = 0x021503C0, 0x02154AF0
GetZoneIDAtMatrixXZ, GetChunkCoordOfWorld = 0x02154AE0, 0x02154C78
LOOKUP_VANILLA = bytes.fromhex('70b5051c141c081c00f0bef8061c201c00f0baf8021c281c311cfff7e9ff70bd')   # (decomp build)
# Zone hold (zone_edges, 2026-10-08): while map-local flag ZONE_HOLD_FLAG is set, ZoneLookup gives every position its
# cell's zone (no rectangle), so a scene that walks the player across a map edge inside one cell keeps its zone: the
# swap (Field_CheckDoRealTimeLoad runs every frame, also during scripts: ov036 fieldmap.c FieldRoutine_Run) would
# delete every actor of the scene (DeleteAllActors) and load the other zone's. Wally's catching tutorial walks 6 tiles
# into Route 102, which Petalburg's cell holds (Sapphire keeps Petalburg's objects across its map change): scenes/
# PetalburgCity.inc sets the flag (h_zone_hold, src/include/hoenn_story.inc). Flags 0-0x63 are map-local: every zone
# change clears them (ov012 FieldScript_CallOnZoneInit -> FieldScript_ResetMapLocalEvents), so the scene's warp
# ends the hold; it cannot outlive the map. g_GameSystem: arm9 bss 0x021410f4 holds the GameSystem pointer
# (GameSystem_Init 0x020167ea: str r5, [r0]); GSYS_GetGameData, GameData_GetEventWork, EventWork_FlagGet (arm9 symbols).
ZONE_HOLD_FLAG = 0x60
G_GAME_SYSTEM, GSYS_GetGameData, GameData_GetEventWork, EventWork_FlagGet = 0x021410F4, 0x02016AD8, 0x02017394, 0x020191AC

def _fixed_weather():
    import importlib.util
    spec = importlib.util.spec_from_file_location('fixed_weather_', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixed_weather.py'))
    fw = importlib.util.module_from_spec(spec); spec.loader.exec_module(fw)
    return fw

def lookup_tables(world):
    """ZoneLookup's rectangles by matrix: the fixed-weather parts first (patches/fixed_weather.py; they only cover
    tiles of their own map's zone), then world.json's zone_rects on the Hoenn matrix. -> {matrix: [[x0, z0, x1, z1,
    zone], ...]} (zone_lookup_code's `groups`)."""
    groups = _fixed_weather().lookup_rects(world)
    groups.setdefault(world['matrix'], []).extend(world.get('zone_rects', []))
    return {m: r for m, r in groups.items() if r}

def zone_lookup_code(base, matrix, rects, groups=None):
    """Thumb ZoneLookup(MapMatrix *m, fx32 x, fx32 z) at `base` + its rectangle table: groups of (u16 matrix id, u16
    count, then x0, z0, x1, z1, zone per rectangle), a count of 0 ends it; tiles = position >> 16. `groups` ({matrix:
    rects}, lookup_tables) replaces `rects` on `matrix` (rects alone: world.json zone_rects, as before)."""
    import importlib.util
    spec = importlib.util.spec_from_file_location('exp_share_', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'exp_share.py'))
    es = importlib.util.module_from_spec(spec); spec.loader.exec_module(es)
    groups = groups if groups is not None else {matrix: rects}
    t = es.Thumb(base)
    asrs = lambda rd, rm, imm: t.h(0x1000 | imm << 6 | rm << 3 | rd)
    t.push([3, 4, 5, 6, 7])                   # 24 bytes + the hook's 8: the stack stays 8-aligned
    t.mov(4, 0); t.mov(5, 1); t.mov(6, 2)     # r4 matrix, r5 x, r6 z
    # zone hold (ZONE_HOLD_FLAG set by a scene): the cells' zones, no rectangle (see ZONE_HOLD_FLAG)
    t.ldr_lit(0, 'gsys'); t.ldr_off(0, 0, 0); t.cmp(0, 0); t.beq('rects')     # g_GameSystem (none yet: no hold)
    t.bl(GSYS_GetGameData); t.bl(GameData_GetEventWork)
    t.movs(1, ZONE_HOLD_FLAG); t.bl(EventWork_FlagGet)
    t.cmp(0, 0); t.bne('cell')
    t.label('rects')
    t.ldr_off(3, 4, 4)                        # matrix->matrixId (struct MapMatrix, field_map.h)
    t.ldr_lit(7, 'table')
    t.label('group')                          # find this matrix's group
    t.ldrh_off(0, 7, 2); t.cmp(0, 0); t.beq('cell')
    t.ldrh_off(1, 7, 0); t.addi(7, 4); t.cmpr(1, 3); t.beq('found')
    t.lsls(1, 0, 2); t.addsr(1, 1, 0); t.lsls(1, 1, 1); t.addsr(7, 7, 1)   # skip count * 10 bytes
    t.b('group')
    t.label('found')
    asrs(1, 5, 16); asrs(2, 6, 16)            # tile x, z
    t.label('loop')
    t.cmp(0, 0); t.beq('cell'); t.subi(0, 1)
    t.ldrh_off(3, 7, 0); t.cmpr(1, 3); t.bcc('lt', 'next')
    t.ldrh_off(3, 7, 4); t.cmpr(1, 3); t.bcc('gt', 'next')
    t.ldrh_off(3, 7, 2); t.cmpr(2, 3); t.bcc('lt', 'next')
    t.ldrh_off(3, 7, 6); t.cmpr(2, 3); t.bcc('gt', 'next')
    t.ldrh_off(0, 7, 8); t.pop([3, 4, 5, 6, 7])
    t.label('next'); t.addi(7, 10); t.b('loop')
    t.label('cell')                           # the original: GetZoneIDAtMatrixXZ(m, chunk(x), chunk(z))
    t.mov(0, 5); t.bl(GetChunkCoordOfWorld); t.mov(5, 0)
    t.mov(0, 6); t.bl(GetChunkCoordOfWorld); t.mov(2, 0)
    t.mov(1, 5); t.mov(0, 4); t.bl(GetZoneIDAtMatrixXZ)
    t.pop([3, 4, 5, 6, 7])
    t.word('gsys', G_GAME_SYSTEM)
    t.word('table', 0)                        # (filled below: the table follows the code)
    code = bytearray(t.assemble())
    table = b''.join(struct.pack('<HH', m, len(rs)) + b''.join(struct.pack('<5H', *r) for r in rs)
                     for m, rs in groups.items() if rs) + struct.pack('<HH', 0, 0)
    struct.pack_into('<I', code, t.labels['table'] - base, base + len(code))
    return bytes(code) + table

def apply_code(code):
    world = json.load(open(os.path.join(W, 'world.json')))
    groups = lookup_tables(world)
    if not groups: return 'no zone rectangles'
    import re
    yml = os.path.join(code, 'itcm.yaml')
    text = open(yml).read()
    size = int(re.search(r'^code_size: (\d+)$', text, re.M).group(1))
    assert re.search(r'^base_address: (\d+)$', text, re.M).group(1) == str(ITCM_BASE)
    assert re.search(r'^bss_size: 0$', text, re.M), 'ITCM autoload has a bss'
    base = ITCM_BASE + size
    def load(name):
        p = os.path.join(code, name); return p, bytearray(open(p, 'rb').read())
    def save(p, d):
        if os.path.islink(p): os.unlink(p)
        open(p + '.tmp', 'wb').write(d); os.replace(p + '.tmp', p)
    path, arm9 = load('arm9.bin')
    lit = ARENA_ITCM_LIT - 0x02004000
    assert struct.unpack_from('<I', arm9, lit)[0] == base, f'ITCM arena literal is {struct.unpack_from("<I", arm9, lit)[0]:#x}'
    blob = zone_lookup_code(base, world['matrix'], None, groups)
    end = (base + len(blob) + 31) & ~31
    assert end <= 0x02000000
    struct.pack_into('<I', arm9, lit, end); save(path, arm9)                 # the ITCM arena starts after it
    path, itcm = load('itcm.bin')
    assert len(itcm) == size
    save(path, itcm + blob + bytes(end - base - len(blob)))
    open(yml, 'w').write(re.sub(r'^code_size: \d+$', f'code_size: {end - ITCM_BASE}', text, flags=re.M))
    path, ov = load('arm9_ov012.bin')
    at = LOOKUP - OV012
    assert bytes(ov[at:at + 32]) == LOOKUP_VANILLA, f'GetZoneIDAtMatrixXZWorld: unexpected bytes {bytes(ov[at:at + 32]).hex()}'
    off = base - (LOOKUP + 2 + 4)
    hook = struct.pack('<HHHH', 0xB510, 0xF000 | (off >> 12) & 0x7FF, 0xF800 | (off >> 1) & 0x7FF, 0xBD10)  # push {r4,lr}; bl; pop {r4,pc}
    ov[at:at + 8] = hook        # (the rest of the old body stays, unreached: ov012 then compresses to about its old size, so
    save(path, ov)              # its 512-byte slot and every later ROM file keep their place and savestates stay usable)
    return 'zone lookup: ' + ', '.join(f'matrix {m}: {len(r)} rectangles' for m, r in groups.items()) + f', ZoneLookup at {base:#x} ({len(blob)} B), ITCM arena from {end:#x}'
