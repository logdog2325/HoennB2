"""Install interior zones from data/interiors/<zone>.json (notes/INTERIORS.md).

A json with "room": NAME installs the room built in work/interiors/NAME/ (b2tools/rebuild_interiors.sh:
models_interior.py recipes, or models_truck.py) into the zone:
  - the room's chunk (terrain .nsbmd + collision .per + placements) is appended to a/0/0/8 (after the overworld's
    chunks, so this patch runs after hoenn_world) and becomes the chunk of the zone's 1x1 matrix (the zone's own
    matrix is rewritten in place; a matrix shared with any other zone, ours or not, gets a new matrix instead);
  - the room's map textures are merged losslessly (nsbtx.merge) into the texture set(s) of the zone's area, its
    furniture models that the area's interior building pack lacks are copied in (from the Black 2 pack that has them,
    or from a file for new models; a resized Black 2 model, room.json models "base", takes the base's info record and
    textures) with their textures merged into the pack's texture set (a/1/7/5);
  - the zone's camera box (a/1/0/9 entry cam_bound, rewritten in place when the zone is its only user; a zone whose
    box is shared with another zone, has another size or is missing (0xFFFF) gets one of the a/1/0/9 entries no zone
    header names (165 in Black 2, all 28 bytes): same-size rewrites keep the archive's size, so the ROM layout and the
    savestates stay valid) and fly point.
A big room (room.json "chunks", models_interior.py) appends one chunk per matrix cell and gets a w x h matrix (its own
matrix rewritten in place when no other zone uses it, else a new one); zone tiles then run over the whole matrix.
Entities: "npcs" replace the zone's NPC list; "signs", "warps", "triggers" replace those lists when given (a room without
"triggers" gets none: Black 2's own would run the room's scripts of their numbers). With a room,
optional "bgm" (one SEQ number for all seasons) and "battle_bg" (zone header flags bits 5-9) override the parent town's;
positions are Sapphire tiles ("at": [x, y]) moved by the room's origin; warps name a Sapphire tile of a warp spot of
the room (exit mat or stairs) and their destination ("to": [zone, warp]). Without a room, x/z are zone tiles (old
format). If src/field_scripts has a file for the zone's init-script number, it becomes the zone's map scripts (they
live in the entity file); a zone with a room and no such file gets an empty table instead of Black 2's."""
import os, json, glob, sys, struct
import narcio, zoneheaders
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import version  # noqa: E402  (Ruby: data/interiors/ruby/<zone>.json; data/versions.json rooms of one version)
from zones import parse_entities, build_entities

ROOT = os.path.join(os.path.dirname(__file__), '..', '..')
ROOMS = os.environ.get('HOENN_INTERIORS_DIR') or os.path.join(ROOT, 'work', 'interiors')

def _own_files():
    p = os.path.join(ROOT, 'data', 'hoenn_interiors.json')
    # (version.load_json: an Emerald build adds data/emerald/hoenn_interiors.json's claimed rooms; frontier_factory_dome)
    rooms = version.load_json(p)['rooms'].values() if os.path.exists(p) else []
    return {r['zone']: (r['own_scripts'], r['own_init'], r['own_text']) for r in rooms if 'own_scripts' in r}
OWN = _own_files()
def _hoenn_zones():
    z = {m['zone'] for m in json.load(open(os.path.join(ROOT, 'data', 'hoenn_zones.json')))['maps'].values()}
    return z | {int(os.path.basename(f)[:-5]) for f in version.overlay(os.path.join(ROOT, 'data', 'interiors'), '*.json')}
HOENN_ZONES = _hoenn_zones()                            # zones a warp may lead to (outdoor maps and installed rooms)
B2_INIT = {z: n for z, n in ((r['zone'], r['init_scripts']) for r in (version.load_json(os.path.join(ROOT, 'data', 'hoenn_interiors.json'))['rooms'].values() if os.path.exists(os.path.join(ROOT, 'data', 'hoenn_interiors.json')) else []) if 'zone' in r)}   # source files keep these names

NPC_DEFAULTS = dict(uid=0, model=0, move=0, evtype=0, flag=0, script=0, dir=1, p0=0, p1=0, p2=0, areaw=0, areah=0,
                    rail=0, x=0, z=0, y=0)
NO_MAP_SCRIPTS = bytes(4)            # MapScriptsEnd (.2byte 0) + padding, as Black 2's empty tables (0785.s)
def anim_pairs(info):
    """(texture, palette) pairs a copied model's texture-pattern animations (BTP0 in its info record) swap in by name.
    The model's materials name only the first frame's texture; every other frame's texture must be in the pack's set
    too, or NNS's lookup returns NULL and the pattern code reads through it: a data abort on hardware and melonDS (the
    game freezes as the room loads; DeSmuME reads ITCM's mirror at 0 and goes on). museum_freeze 2026-10-12: Black 2's
    machine02 in the Slateport Museum without machin0.2 / machin0.3 (b2tools/anim_tex_check.py)."""
    from anim_tex_check import btp_names
    out = []
    for _, texs, pals in btp_names(info):
        for i, t in enumerate(texs):
            out.append((t, pals[i] if len(pals) == len(texs) else (pals[0] if pals else None)))
    return out

STATIC_INFO = bytes.fromhex('0000 0000 ffff 0000 0000 0000 ffff 0000 0000 0000 ffff ffff ffff ffff ffff ffff ffff ffff')

def _area_record(files, area):
    raw = open(os.path.join(files, 'a', '0', '1', '3'), 'rb').read()
    pack, texset = struct.unpack_from('<HH', raw, area * 10)
    ext = raw[area * 10 + 6]                               # u16 pack, u16 texset, u8 srt, u8 pat, u8 isExterior
    seasons = 4 if 2 <= area <= 281 else 1                 # AreaData_HasSeasons: area + season
    return pack, [texset + s for s in range(seasons)], ext

def _pack_sections(data):
    from b2files import gf_container
    magic, secs = gf_container(data)
    assert magic == 'AB', magic
    n = len(secs) // 2
    return secs[:n], secs[n:]

def _pos(cfg, room, item):
    """Zone tile (x, z) of an entity: Sapphire "at" + room origin, else the old x/z."""
    if 'at' in item:
        assert room, f'zone {cfg["zone"]}: "at" needs a room'
        return item['at'][0] + room['origin'][0], item['at'][1] + room['origin'][1]
    return item['x'], item['z']

def chunk_container(d, c):
    """A room/cave chunk for a/0/0/8: 'WB' (model, terrain, buildings), or 'GC' (model, terrain layer 0, terrain
    layer 1, buildings) when the room has a second collision layer ("collision1": walk-under bridges, caves_east;
    ov036 FieldChunkAccessor_GC_GetTerrain returns both layers, FieldG3DMapper_GetTerrain takes the one nearest the
    actor's height, ties to layer 0)."""
    from b2files import gf_container_build
    keys = ('terrain', 'collision', 'collision1', 'placements') if c.get('collision1') else ('terrain', 'collision', 'placements')
    data = gf_container_build('GC' if c.get('collision1') else 'WB', [open(os.path.join(d, c[k]), 'rb').read() for k in keys])
    # Map type 16 (interiors, caves) loads each chunk file into a buffer of 0x1b008 = 110,600 bytes (ov036 MAP_CONFIGS
    # 0x021ca01c entry 16, FieldG3DMapperConfig.chunkBufferSize); a bigger chunk hangs the field on a black screen
    # (tested, caves_east: a 123 KB cave model)
    if len(data) > 0x1b008:
        print(f'WARNING interiors: {d} {c.get("terrain")}: chunk {len(data)} bytes > 110600 (the field hangs): split the room '
              'over more chunks ("origin"/"matrix") or simplify it')
    return data

def apply(files):
    import nsbtx, b2files
    from b2files import gf_container_build
    from scripts import assemble, source_for
    src_files = os.path.join(ROOT, 'external', 'pokebw2', 'build', 'b2_us', 'files')
    headers, hentries = zoneheaders.load(files)
    ents = narcio.load(files, 126)
    cfgs = [json.load(open(f)) for f in version.overlay(os.path.join(ROOT, 'data', 'interiors'), '*.json')]
    other = [c for c in cfgs if c.get('room') and not version.room_in_version(c['room'])]   # the other version's rooms
    if other:                                                                              # (data/versions.json)
        cfgs = [c for c in cfgs if c not in other]
        print(f'interiors: {version.NAME} leaves out', ', '.join(c['room'] for c in other))
    for c in cfgs:                       # a room built from this version's other layout (data/versions.json room_variants)
        v = version.room_variant(c.get('room'))
        if v != c.get('room') and os.path.exists(os.path.join(ROOMS, v, 'room.json')):
            print(f'interiors: {version.NAME} installs {v} for {c["room"]}'); c['room'] = v
    # caves (data/cave_layouts, built by b2tools/models_cave.py; notes/CAVES.md) that this build's interiors folder
    # doesn't have yet (an agent's copy of work/interiors made before the cave existed) are left out, so every room
    # agent's build keeps working while the cave agents add caves; rebuild_interiors.sh with no names builds them all
    unbuilt_caves = [c for c in cfgs if c.get('cave') and c.get('room') and not os.path.exists(os.path.join(ROOMS, c['room'], 'room.json'))]
    if unbuilt_caves:
        cfgs = [c for c in cfgs if c not in unbuilt_caves]
        print('interiors: caves left out (not built in', ROOMS + '):', ', '.join(c['room'] for c in unbuilt_caves))
    if os.environ.get('HOENN_SKIP_UNBUILT_ROOMS'):      # lead builds while agents add rooms: leave out rooms not built
        unbuilt = [c for c in cfgs if c.get('room') and not os.path.exists(os.path.join(ROOMS, c['room'], 'room.json'))]
        cfgs = [c for c in cfgs if c not in unbuilt]
        if unbuilt: print('interiors: left out (not built in', ROOMS + '):', ', '.join(c['room'] for c in unbuilt))
    ours = {c['zone'] for c in cfgs}
    rooms = [c for c in cfgs if c.get('room')]
    done = []
    if rooms:
        chunks, mats = narcio.load(files, 8), narcio.load(files, 9)
        texsets, btex, packs, cams = (narcio.load(files, a) for a in (14, 175, 226, 109))
        map_adds, pack_adds = {}, {}                       # texset -> [(src, tex, pal)], pack -> {res: (info, bmd, adds)}
        replaces = []                                      # a/0/1/0 entries for zones' other layouts (alt_rooms)
        src_maps, src_btex = {}, {}
        def map_set(i):
            if i not in src_maps: src_maps[i] = b2files.map_textures(src_files, i)
            return src_maps[i]
        def btex_set(p):
            if p not in src_btex: src_btex[p] = b2files.building_textures(src_files, p, exterior=False)
            return src_btex[p]
        mat_users = {}                                     # matrix -> number of zone headers naming it
        for h_ in headers: mat_users[h_['matrix']] = mat_users.get(h_['matrix'], 0) + 1
        users = {}                                         # camera box -> number of zone headers naming it
        for h_ in headers: users[h_['cam_bound']] = users.get(h_['cam_bound'], 0) + 1
        free_cams = [k for k in range(len(cams)) if not users.get(k) and len(cams[k]) == 28]
        for cfg in rooms:
            zone = cfg['zone']; hd = headers[zone]
            d = os.path.join(ROOMS, cfg['room'])
            meta = json.load(open(os.path.join(d, 'room.json')))
            cfg['_room'] = meta
            missing = [f for f in (meta['terrain'], meta['collision'], meta['placements']) if not os.path.exists(os.path.join(d, f))]
            assert not missing, f'{d}: missing {missing} (run b2tools/rebuild_interiors.sh)'
            big = meta.get('chunks')                      # a big room: one chunk per matrix cell (None = empty)
            if big:
                missing = [c[k] for c in big if c for k in ('terrain', 'collision', 'placements') if not os.path.exists(os.path.join(d, c[k]))]
                assert not missing, f'{d}: missing {missing} (run b2tools/rebuild_interiors.sh)'
                ids = []
                for c in big:
                    if c is None: ids.append(0xFFFFFFFF); continue
                    ids.append(len(chunks))
                    chunks.append(chunk_container(d, c))
                chunk_id = ids[0]
                mw, mh = meta['matrix']
                new = struct.pack('<HHHH', 0, 0, mw, mh) + struct.pack(f'<{mw * mh}I', *ids)
            else:
                chunk_id = len(chunks)
                chunks.append(chunk_container(d, meta))
                new = struct.pack('<HHHHI', 0, 0, 1, 1, chunk_id)
            # the zone's matrix: its own 1x1 matrix is rewritten, a shared one (also with another of our rooms: Black 2's
            # Nacrene zones 22-24 share matrix 31) is replaced by a new matrix, so no room overwrites another's
            m = hd['matrix']
            fmt, _, w, h = struct.unpack_from('<HHHH', mats[m], 0)
            if fmt == 0 and mat_users.get(m) == 1 and ((w, h) == (1, 1) or big):
                mats[m] = new
            else:
                mat_users[m] = mat_users.get(m, 1) - 1
                hd['matrix'] = m = len(mats); mats.append(new); mat_users[m] = 1
            # textures of the room's terrain -> the area's texture set(s); furniture -> the area's interior pack
            if 'area' in cfg: hd['area'] = cfg['area']     # rooms sharing a style share an interior area (gen_interiors)
            own = OWN.get(zone)                             # a room's own script/text files after Black 2's
            if own:                                         # (allocate_interiors own_*; the scripts/text patches write
                hd['scripts'], hd['init_scripts'], hd['text'] = own   # them there): never Black 2's (a cold boot hung)
            if 'parent' in cfg:      # a generated room: Littleroot's house (390) as Black 2 made it (no place banner,
                tmpl = headers[390]  # no season card), named after and playing the music of the town it belongs to
                for k in ('map_type', 'npc_cache', 'flags', 'weather_word', 'place_display', 'icon_word'): hd[k] = tmpl[k]
                town = headers[cfg['parent']]
                hd['parent'], hd['place'] = cfg['parent'], town['place']
                hd['bgm0'], hd['bgm1'], hd['bgm2'], hd['bgm3'] = town['bgm0'], town['bgm1'], town['bgm2'], town['bgm3']
                hd['encounters'], hd['enc_slot'] = 0x1FFF, 6
            if 'bgm' in cfg:                               # e.g. Black 2's Gym / League music instead of the town's
                hd['bgm0'] = hd['bgm1'] = hd['bgm2'] = hd['bgm3'] = cfg['bgm']
            for k, v in cfg.get('header', {}).items():     # explicit header fields win (e.g. the Centers' town names)
                assert k in hd, f'zone {zone}: unknown header field {k}'
                hd[k] = v
            if 'battle_bg' in cfg:                         # header flags bits 5-9 (e.g. an Elite Four room's own)
                hd['flags'] = (hd['flags'] & ~(31 << 5)) | ((cfg['battle_bg'] & 31) << 5)
            pack, sets, ext = _area_record(files, hd['area'])
            assert ext == 0, f'zone {zone}: area {hd["area"]} is an exterior area'
            for ts in sets:
                for tex, src in meta['map_textures'].items():
                    map_adds.setdefault(ts, []).append((map_set(src), tex, tex + '_pl'))
            # other layouts of this zone ("alt_rooms", caves_misc: Shoal Cave's high tide): their chunks, a matrix of their
            # own and an a/0/1/0 map replacement of kind 1 (the whole matrix: MapReplace_Patch, ov012 map_matrix.c) that
            # loads it instead of the zone's while EVENT_MAP_REPLACE_TABLE's event uid alt['event'] is set (condition =
            # uid + 3, map_replace.c; uid 9 = work 0x403A == 0x1028: no Black 2 script sets uids 7-9 and no replacement
            # uses conditions 10-12). Scripts switch it with MapReplaceSetEvent (converter/gen_caves.py tide_script).
            alt_metas = []
            for alt in cfg.get('alt_rooms', []):
                ad = os.path.join(ROOMS, alt['room'])
                if not os.path.exists(os.path.join(ad, 'room.json')):     # not built in this interiors folder yet: the
                    done.append(f"zone {zone}: other layout {alt['room']} not built ({ROOMS}): left out")   # room only
                    continue
                am = json.load(open(os.path.join(ad, 'room.json')))
                ids2 = []
                for c in (am.get('chunks') or [am]):
                    if c is None: ids2.append(0xFFFFFFFF); continue
                    ids2.append(len(chunks)); chunks.append(chunk_container(ad, c))
                aw, ah = am.get('matrix', [1, 1])
                m2 = len(mats); mats.append(struct.pack('<HHHH', 0, 0, aw, ah) + struct.pack(f'<{aw * ah}I', *ids2)); mat_users[m2] = 0
                replaces.append(struct.pack('<HBB6H', m, 1, alt['event'] + 3, m, m2, 0, 0, 0, 0xFFFF))
                for ts in sets:
                    for tex, src in am['map_textures'].items():
                        map_adds.setdefault(ts, []).append((map_set(src), tex, tex + '_pl'))
                alt_metas.append(am)
                done.append(f"zone {zone}: {alt['room']} = chunks {ids2} (matrix {m2}, loaded instead of {m} while map replace event {alt['event']} is set)")
            have = {struct.unpack_from('<H', info, 0)[0] for info in _pack_sections(packs[pack])[0]}
            for mdl in meta.get('models', []) + meta.get('extra_models', []) + [x for am in alt_metas for x in am.get('models', [])]:
                if mdl['res'] in have or mdl['res'] in pack_adds.get(pack, {}): continue
                if 'file' in mdl and 'base' in mdl:         # a resized Black 2 model (models_interior.py DERIVED_MODELS):
                    infos, _ = _pack_sections(packs[mdl['pack']])        # the base model's info record under the new
                    k = [struct.unpack_from('<H', i, 0)[0] for i in infos].index(mdl['base'])   # res id, the base
                    info = struct.pack('<H', mdl['res']) + infos[k][2:]                        # pack's textures
                    bmd = open(os.path.join(d, mdl['file']), 'rb').read()
                    adds = [(btex_set(mdl['pack']), t, p) for t, p in sorted(nsbtx.material_pairs(bmd), key=str) if t]
                    adds += [(btex_set(mdl['pack']), t, p) for t, p in anim_pairs(info)]      # its animation's frames
                elif 'file' in mdl:                         # a new model (e.g. the truck's rear door)
                    bmd = open(os.path.join(d, mdl['file']), 'rb').read()
                    info = struct.pack('<HH', mdl['res'], mdl.get('type', 0)) + STATIC_INFO[4:]   # type 11: BMSetVisible 8
                    adds = [(map_set(src), tex, tex + '_pl') for tex, src in mdl['textures'].items()]
                else:                                       # a Black 2 model from another interior pack
                    infos, bmds = _pack_sections(packs[mdl['pack']])
                    k = [struct.unpack_from('<H', i, 0)[0] for i in infos].index(mdl['res'])
                    info, bmd = infos[k], bmds[k]
                    adds = [(btex_set(mdl['pack']), t, p) for t, p in sorted(nsbtx.material_pairs(bmd), key=str) if t]
                    adds += [(btex_set(mdl['pack']), t, p) for t, p in anim_pairs(info)]      # its animation's frames
                pack_adds.setdefault(pack, {})[mdl['res']] = (info, bmd, adds)
            # camera box: Black 2's format (u32 count 1; u32 1, 0; s32 xmin, xmax, zmin, zmax), rewritten in place
            cam = hd['cam_bound']
            if cam != 0xFFFF and cam < len(cams) and len(cams[cam]) == 28 and users.get(cam) == 1:
                cams[cam] = struct.pack('<7i', 1, 1, 0, *meta['camera'])          # the zone's own box
            elif free_cams:                                 # a/1/0/9 has no reserve: take an entry no zone names
                own = free_cams.pop()
                users[cam] = users.get(cam, 1) - 1; users[own] = 1
                hd['cam_bound'] = own
                cams[own] = struct.pack('<7i', 1, 1, 0, *meta['camera'])
                done.append(f'zone {zone}: camera box {cam} shared or unusual -> own box {own}')
            else:
                done.append(f'zone {zone}: camera box {cam} shared or unusual, left as it is (no free a/1/0/9 entry)')
            hd['fly_x'], hd['fly_y'], hd['fly_z'] = meta['fly'][0], 0, meta['fly'][1]
            done.append(f"zone {zone}: room {cfg['room']} = chunk {chunk_id} (matrix {m})")
        for ts, adds in map_adds.items():
            texsets[ts] = nsbtx.merge(texsets[ts], adds)
        for p, models in pack_adds.items():
            infos, bmds = _pack_sections(packs[p])
            for res, (info, bmd, adds) in models.items():
                infos.append(info); bmds.append(bmd)
                btex[p] = nsbtx.merge(btex[p], adds)
            packs[p] = gf_container_build('AB', infos + bmds)
            done.append(f'pack {p} + models {sorted(models)}')
        narcio.save(files, 8, chunks); narcio.save(files, 9, mats)
        if replaces:                                       # a/0/1/0: a 64 KB RESERVE in build_rom.py, 16 bytes each
            mr = narcio.load(files, 10)
            taken = {struct.unpack_from('<H', mr[0], i)[0] for i in range(0, len(mr[0]), 16)}
            for e in replaces: assert struct.unpack_from('<H', e, 0)[0] not in taken, f'matrix {struct.unpack_from("<H", e, 0)[0]} already has Black 2 replacements'
            mr[0] = mr[0] + b''.join(replaces); narcio.save(files, 10, mr)
        for arc, data in ((14, texsets), (175, btex), (226, packs), (109, cams)): narcio.save(files, arc, data)
    for cfg in cfgs:
        zone = cfg['zone']; hd = headers[zone]; room = cfg.get('_room')
        e, _ = parse_entities(ents[hd['entities']])
        tmpl = dict(e['npcs'][0]) if e['npcs'] else dict(NPC_DEFAULTS)
        if 'npcs' in cfg:
            e['npcs'] = []
            for n in cfg['npcs']:
                x, z = _pos(cfg, room, n)
                npc = dict(tmpl, **{k: v for k, v in NPC_DEFAULTS.items() if k not in ('uid', 'model', 'script', 'x', 'z')})
                npc.update({k: v for k, v in n.items() if k in NPC_DEFAULTS})
                if 'range' in n: npc['areaw'], npc['areah'] = n['range']
                npc['x'], npc['z'] = x, z
                e['npcs'].append(npc)
        if 'signs' in cfg:
            e['signs'] = []
            for s in cfg['signs']:
                x, z = _pos(cfg, room, s)
                e['signs'].append(dict(script=s['script'], cond=s.get('cond', 0), dir=s.get('dir', 4), rail=0, x=x, z=z, y=s.get('y', 0)))
        if 'warps' in cfg:
            out = []
            for wcfg in cfg['warps']:
                if 'at' in wcfg and room:
                    spot = next((s for s in room['warp_spots'] if list(wcfg['at']) in s['tiles']), None)
                    if spot is None and wcfg.get('tile_only'):     # a warp tile the builder found no spot for
                        tx, tz = _pos(cfg, room, wcfg)            # (ladders, odd behaviours): plain stairs-like warp
                        spot = dict(x=tx, z=tz, w=1, h=1, type=wcfg.get('type', 2), dir=wcfg.get('dir', 2))
                    assert spot, f'zone {zone}: no warp spot at Sapphire {wcfg["at"]} in {cfg["room"]}'
                    x, z, w, h, typ, dr = spot['x'], spot['z'], spot['w'], spot['h'], spot['type'], spot['dir']
                    if wcfg.get('tile_only'):     # just this Sapphire tile of the spot (one warp per Sapphire warp
                        x, z = _pos(cfg, room, wcfg); w = h = 1    # event: you arrive exactly where Sapphire puts you)
                else:
                    x, z, w, h, typ, dr = wcfg['x'], wcfg['z'], wcfg.get('w', 1), wcfg.get('h', 1), wcfg['type'], wcfg['dir']
                dz, dw = wcfg['to']
                if dz not in HOENN_ZONES and dz != 0xFFFF:      # a room not built (Cable Club rooms behind the Centers'
                    dz, dw = zone, 0                            # 2F counters...): back to this room's own warp 0
                wy = wcfg.get('y', spot.get('y', 0) if ('at' in wcfg and room) else 0)   # a warp fires within 2 units
                out.append(dict(dest_zone=dz, dest_warp=dw, dir=wcfg.get('dir', dr),      # of its y (caves' levels:
                                type=wcfg.get('type', typ), rail=0, x=x * 16 + 8, y=int(wy) & 0xFFFF,   # models_cave
                                z=z * 16 + 8, w=w, h=h, unk=0))                                        # warp_spots "y")
            e['warps'] = out
        if 'triggers' in cfg or room:
            # a rebuilt room drops Black 2's own step triggers when its json gives none (script_check 2026-10-08): they
            # ran this room's script of the same number when stepped on (Weather Institute 2F (4,10): script 6, which
            # does not exist; Fallarbor Center 2F, Contest Hall, Old Lady's Rest Stop: an attendant's or the zone init's
            # script), as Black 2's map-script table did (below). Story triggers are added later by the story patch.
            e['triggers'] = []
            for t in cfg.get('triggers', []):
                x, z = _pos(cfg, room, t)
                e['triggers'].append(dict(script=t['script'], value=t.get('value', 0), work=t.get('var', 0), type=t.get('type', 0),
                                          rail=0, x=x, z=z, w=t.get('w', 1), h=t.get('h', 1), y=t.get('y', 0), unk=0))
        # map scripts: ours if src/field_scripts has the zone's init file; a rebuilt room otherwise gets none (Black 2's
        # table would start Black 2's scenes by script number, e.g. zone 390's "0x407d == 0 -> script 4")
        init_src = source_for(B2_INIT.get(zone, hd['init_scripts']) if zone in OWN else hd['init_scripts'])
        init = assemble(init_src) if init_src else (NO_MAP_SCRIPTS if room else None)
        ents[hd['entities']] = build_entities(e, ents[hd['entities']], init)
        done.append(f"zone {zone}: {len(e['npcs'])} NPCs, {len(e['signs'])} signs, {len(e['warps'])} warps, {len(e['triggers'])} triggers")
    # zone copies (gen_caves "variants", postgame_maps 2026-10-07: Emerald's Altering Cave has nine wild tables, Black 2 one
    # per zone header): the zone's finished header (same matrix, area, scripts, text, entities, camera box, music, place)
    # with another encounter file; Route 103's dynamic warp (dest 0x100: GameData's next zone, set by its zone init)
    # leads into one of them. No a/0/1/2 entry moves (the copies overwrite free zones' headers).
    for cfg in cfgs:
        for v in cfg.get('variants', []):
            headers[v['zone']] = dict(headers[cfg['zone']], encounters=v['encounters'])
            done.append(f"zone {v['zone']}: copy of zone {cfg['zone']} with encounter file {v['encounters']} ({v.get('table')})")
    test = os.environ.get('HOENN_TEST_INTERIOR_DOOR')
    if test:      # test only: Littleroot's warp 1 (May's house door) leads to zone <test> (and back from its fly tile)
        tz = int(test); lr, _ = parse_entities(ents[headers[389]['entities']]); dst, _ = parse_entities(ents[headers[tz]['entities']])
        lr['warps'][1]['dest_zone'], lr['warps'][1]['dest_warp'] = tz, len(dst['warps'])
        dst['warps'].append(dict(dest_zone=389, dest_warp=1, dir=1, type=1, rail=0, x=headers[tz]['fly_x'] * 16 + 8, y=0,
                                 z=headers[tz]['fly_z'] * 16 + 8, w=1, h=1, unk=0))
        for z, e in ((389, lr), (tz, dst)): ents[headers[z]['entities']] = build_entities(e, ents[headers[z]['entities']])
        done.append(f'TEST: Littleroot warp 1 -> zone {tz} warp {len(dst["warps"]) - 1}')
    zoneheaders.save(files, headers, hentries)
    narcio.save(files, 126, ents)
    return '; '.join(done)
