"""Give every Hoenn outdoor map a Black 2 zone and every Hoenn place a line of the place-name text (system 0109).

    python3 allocate_zones.py        -> ../data/hoenn_zones.json (review it; ids never change once used)

Zones: a zone id only matters to the engine through hard-coded checks (arm9 0x02018a54-0x02018ee4, read with
b2tools/armdis.py; notes/OVERWORLD_PLAN.md), so those ids are never used: Union Room 422, 150/151, 75/76, Royal Unova
52, PWT 191-193, Musical 78, Nimbasa Stadium 81-87, Abyssal Ruins 241-248, Entralink 279-316, Black City/White Forest
0/294/295/424, Black Tower/White Treehollow 478-487/492/493, Join Avenue 489-491, Hidden Grotto 518, Victory Road
573, Memory Link 597-607. 427/428 stay Aspertia while the test harness starts there. Everything else in a zone
header (matrix, area, scripts, music, place) is rewritten by our patches, so towns take Unova's town zones and routes
Unova's route zones (their fog/light/sound table entries then fit best), then any other free zone.
Place names: pokeruby's region map section names in Gen 5 capitalisation, on lines 4.. of the place-name file
(0-3 are Black 2's special names); Littleroot 4, Oldale 5, Route 101 14 are already in use.
"""
import json, os, re, glob

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..')
RUBY = os.path.join(ROOT, 'external', 'pokeruby')

DENY = ({0, 52, 75, 76, 78, 150, 151, 191, 192, 193, 422, 424, 427, 428, 518, 573} | set(range(81, 88))
        | set(range(241, 249)) | set(range(279, 317)) | set(range(478, 494)) | set(range(597, 608)))
FIXED = {'LittlerootTown': 389, 'Route101': 317, 'OldaleTown': 397}
FIXED_PLACE = {'MAPSEC_LITTLEROOT_TOWN': 4, 'MAPSEC_OLDALE_TOWN': 5, 'MAPSEC_ROUTE_101': 14}
# Unova's overworld zones (header matrix 0), by kind, in Unova order
UNOVA_TOWNS = [6, 16, 62, 96, 107, 113, 120, 406, 412, 439, 448, 458, 465]
UNOVA_ROUTES = [319, 321, 326, 329, 331, 337, 345, 348, 365, 368, 370, 374, 378, 383, 387, 423, 437, 446, 463, 474,
                475, 551]
UNOVA_OTHER_OUTDOOR = [154, 157, 194, 198, 205, 230, 238, 240, 444, 456, 461]
# not used: zones with special map types (Castelia rails 28, League 136, moving bridges 249-263, Liberty Garden 235)
AVOID = {28, 136, 147, 235, 249, 250, 253, 254, 255, 263} | set(range(610, 614)) | {550, 586, 608, 609}   # 610-613, 550, 586,
#   608, 609: fixed-weather zone copies (patches/fixed_weather.py; 550-609: Route 119/123's sunny ends, v166_fixes)
SKIP_MAPS = {'Route104_Prototype'}     # pokeruby test map, not in the game

def gen5_name(s):
    s = s.replace('{NAME_END}', '').replace('{EVIL_TEAM}', 'AQUA ')       # Sapphire: Team Aqua
    words = []
    for i, w in enumerate(s.split()):
        words.append(w if re.fullmatch(r'\d+', w) else w.lower() if i and w in ('OF', 'THE') else w[0] + w[1:].lower())
    return ' '.join(words)

def main():
    maps = {m['name']: m for m in json.load(open(os.path.join(ROOT, 'data', 'hoenn_maps.json')))}
    lay = json.load(open(os.path.join(ROOT, 'data', 'hoenn_world_layout.json')))
    outdoor = [n for n in list(lay['main']['maps']) + list(lay['standalone']) if n not in SKIP_MAPS]
    secs = json.load(open(os.path.join(RUBY, 'src', 'data', 'region_map', 'region_map_sections.json')))['map_sections']
    sec_name = {s['id']: s['name'] for s in secs}
    used_secs = []
    for f in sorted(glob.glob(os.path.join(RUBY, 'data', 'maps', '*', 'map.json'))):
        s = json.load(open(f)).get('region_map_section')
        if s and s != 'MAPSEC_DYNAMIC' and s not in used_secs: used_secs.append(s)
    order = [s['id'] for s in secs if s['id'] in used_secs]          # region map order
    place, line = {}, 4
    taken = set(FIXED_PLACE.values())
    for s in order:
        if s in FIXED_PLACE:
            place[s] = dict(line=FIXED_PLACE[s], name=gen5_name(sec_name[s])); continue
        while line in taken: line += 1
        place[s] = dict(line=line, name=gen5_name(sec_name[s])); taken.add(line)
    import sys
    sys.path.insert(0, os.path.join(ROOT, 'b2tools'))
    import zoneheaders
    headers, _ = zoneheaders.load(os.path.join(ROOT, 'external', 'pokebw2', 'build', 'b2_us', 'files'))
    # then any other zone with an outdoor map type (0), then interiors, lowest id first
    spare = [i for i, h in enumerate(headers) if h['map_type'] == 0 and i not in AVOID] + \
            [i for i, h in enumerate(headers) if h['map_type'] == 16 and i not in AVOID]
    pool_town = [z for z in UNOVA_TOWNS if z not in DENY]
    pool_route = [z for z in UNOVA_ROUTES + UNOVA_OTHER_OUTDOOR + spare if z not in DENY]
    zones = dict(FIXED)
    used = set(FIXED.values())
    def take(pool):
        while pool:
            z = pool.pop(0)
            if z not in used: used.add(z); return z
        raise SystemExit('zone pool exhausted')
    towns = [n for n in outdoor if maps[n]['type'] in ('MAP_TYPE_TOWN', 'MAP_TYPE_CITY') and n not in zones]
    rest = [n for n in outdoor if n not in zones and n not in towns]
    rest.sort(key=lambda n: (not n.startswith('Route'), int(re.sub(r'\D', '', n) or 0) if n.startswith('Route') else 0, n))
    for n in towns: zones[n] = take(pool_town if pool_town else pool_route)
    for n in rest: zones[n] = take(pool_route)
    out = dict(_doc=__doc__.strip().split('\n\n')[0] + ' See converter/allocate_zones.py.',
               places=place,
               maps={n: dict(zone=zones[n], type=maps[n]['type'], mapsec=json.load(open(os.path.join(
                   RUBY, 'data', 'maps', n, 'map.json')))['region_map_section']) for n in outdoor})
    for n, m in out['maps'].items(): m['place'] = place[m['mapsec']]['line']
    # the event maps (add_event_maps, from other decomps) keep their zones and place lines: main() never gives them out
    # (it reads pokeruby only, and its pools take the same zones in the same order every run)
    old_path = os.path.join(ROOT, 'data', 'hoenn_zones.json')
    if os.path.exists(old_path):
        old = json.load(open(old_path))
        for n, m in old['maps'].items():
            if m.get('decomp') and n not in out['maps']:
                out['maps'][n] = m
                out['places'].setdefault(m['mapsec'], old['places'][m['mapsec']])
        # place lines are never given out again either (fixes_v151, 2026-10-08): a place another tool or agent added for
        # a room or cave of another decomp (MAPSEC_ALTERING_CAVE, line 109: postgame_maps; gen_caves.py reads its line
        # for the cave's header) is no outdoor map's mapsec, so the rebuild above dropped it and the cave lost its name
        for sec, p in old['places'].items():
            if sec not in out['places']: out['places'][sec] = p
    lines = [p['line'] for p in out['places'].values()]
    assert len(lines) == len(set(lines)), f'place-name lines given twice: {sorted(l for l in set(lines) if lines.count(l) > 1)}'
    json.dump(out, open(os.path.join(ROOT, 'data', 'hoenn_zones.json'), 'w'), indent=1, ensure_ascii=False)
    print(f'{len(out["maps"])} outdoor maps -> zones {sorted(zones.values())}')
    print(f'{len(place)} place names on lines {min(p["line"] for p in place.values())}..{max(p["line"] for p in place.values())}')

def add_event_maps():
    """`python3 allocate_zones.py --events` (events agent, 2026-10-07): give the outdoor event maps (data/hoenn_event_maps.json
    maps that data/hoenn_standalone.json builds as warp-only groups: Emerald's Faraway Island, Birth Island, Navel Rock)
    a zone and their place a name line, appended to data/hoenn_zones.json without touching any existing entry (main()
    would renumber: never rerun it). Zones from main()'s route pool order (Unova's outdoor zones, then the other map
    type 0 zones), skipping every zone a Hoenn map already has and the Black 2 zones our builds read as templates
    (data/hoenn_standalone.json bgm_zone, cave looks' header zones); place lines after the last used one."""
    import sys
    sys.path.insert(0, os.path.join(ROOT, 'b2tools')); sys.path.insert(0, HERE)
    import zoneheaders
    from gba import event_maps, map_json_path
    path = os.path.join(ROOT, 'data', 'hoenn_zones.json')
    out = json.load(open(path))
    sa = json.load(open(os.path.join(ROOT, 'data', 'hoenn_standalone.json')))
    outdoor = [n for g in sa['groups'].values() for n in g['maps'] if n in event_maps()]
    new = [n for n in outdoor if n not in out['maps']]
    if not new: print('no new event maps'); return
    headers, _ = zoneheaders.load(os.path.join(ROOT, 'external', 'pokebw2', 'build', 'b2_us', 'files'))
    rooms = json.load(open(os.path.join(ROOT, 'data', 'hoenn_interiors.json')))['rooms']
    templates = {g['bgm_zone'] for g in sa['groups'].values() if g.get('bgm_zone') is not None}
    looks = json.load(open(os.path.join(ROOT, 'data', 'cave_layouts', '_looks.json')))
    templates |= {v[k] for v in looks.values() if isinstance(v, dict) for k in ('header_zone', 'header_zone_dark') if k in v}
    used = {m['zone'] for m in out['maps'].values()} | {r['zone'] for r in rooms.values()} | DENY | AVOID | templates
    from allocate_interiors import variant_zones           # (cave recipes' zone copies: Altering Cave's tables)
    used |= variant_zones()
    spare = [i for i, h in enumerate(headers) if h['map_type'] == 0] + [i for i, h in enumerate(headers) if h['map_type'] == 16]
    pool = [z for z in UNOVA_ROUTES + UNOVA_OTHER_OUTDOOR + spare if z not in used]
    line = max(p['line'] for p in out['places'].values()) + 1
    for n in new:
        mj = json.load(open(map_json_path(RUBY, n)))
        sec = mj['region_map_section']
        if sec not in out['places']:
            out['places'][sec] = dict(line=line, name=gen5_name(sec.replace('MAPSEC_', '').replace('_', ' '))); line += 1
        z = pool.pop(0); used.add(z)
        out['maps'][n] = dict(zone=z, type='MAP_TYPE_ROUTE', mapsec=sec, place=out['places'][sec]['line'], decomp=mj['_decomp'] if '_decomp' in mj else 'pokeemerald')
        print(f'{n}: zone {z}, place line {out["places"][sec]["line"]} ({out["places"][sec]["name"]})')
    json.dump(out, open(path, 'w'), indent=1, ensure_ascii=False)

def emerald_maps():
    """HOENN_VERSION=emerald (emerald_world 2026-10-12, notes/EMERALD.md "Emerald's world"): the Emerald-only outdoor maps
    (the groups' maps of data/emerald/hoenn_standalone.json that data/hoenn_zones.json lacks) -> data/emerald/hoenn_zones.json,
    deep-merged over data/hoenn_zones.json by the Emerald world's readers (version.load_json). Every other map keeps
    Sapphire's zone (rooms' exits, scripts and savestates name them), and data/hoenn_zones.json is never written here.
    An Emerald-only map shares the zone of the map it connects to in its group (pokeemerald connections, the first one
    that has a zone): the Safari Zone's expansion areas are their west neighbours' zones, the Battle Frontier's east half
    is the island's zone 17. A zone of its own needs its scripts, wild table, music and place in the ROM (phases 1/3,
    notes/EMERALD.md work list), so none is given out yet."""
    import sys
    sys.path.insert(0, HERE)
    from gba import world_repo
    sys.path.append(os.path.join(ROOT, 'b2tools'))
    import version
    base = json.load(open(os.path.join(ROOT, 'data', 'hoenn_zones.json')))
    sa = version.load_json(os.path.join(ROOT, 'data', 'hoenn_standalone.json'))
    repo = world_repo()
    from gba import world_map_folders
    names = world_map_folders()
    out = {}
    for g in sa['groups'].values():
        for n in g['maps']:
            if n in base['maps']: continue
            mj = repo.map_json(n)
            near = [names.get(c['map']) for c in mj.get('connections') or []]
            share = next((m for m in near if m in base['maps'] and m in g['maps']), None)
            assert share, f'{n}: no connected map with a zone in its group'
            z = base['maps'][share]
            out[n] = dict(zone=z['zone'], type=mj['map_type'], mapsec=mj['region_map_section'], place=z['place'], shares=share)
            print(f"{n}: zone {z['zone']} (shared with {share}), place line {z['place']}")
    d = {'_doc': ' '.join(emerald_maps.__doc__.split()), 'maps': out}
    p = os.path.join(ROOT, 'data', 'emerald', 'hoenn_zones.json')
    json.dump(d, open(p, 'w'), indent=1, ensure_ascii=False)
    print(f'{len(out)} Emerald-only outdoor maps -> {p}')

if __name__ == '__main__':
    import sys
    sys.path.append(os.path.join(ROOT, 'b2tools'))
    import version
    if version.is_emerald(): emerald_maps()       # (never writes data/hoenn_zones.json)
    elif sys.argv[1:] == ['--events']: add_event_maps()
    else: main()
