"""Room exits that lead to the wrong door (story_fixups 2026-10-07, from ch3b's check; a report step of rebuild_slice.sh).

A room's warp in data/interiors/<zone>.json says {"to": [zone, warp index]}. An outdoor zone keeps Black 2's own warps
first and then gets world.json's "doors" appended (b2tools/patches/hoenn_world.py), so Sapphire's door k of a zone is
warp (Black 2's warp count + k); a door's copy in the zone of the cell it stands in ("foreign": Slateport's harbour warp
outside its map) wins, and hand-made towns' door slots ("slot_doors") keep their slot, as the room generators
(converter/gen_interiors.py, gen_caves.py, gen_interior_recipes_houses.py, b2tools/shops_rooms.py, centers_rooms.py,
gyms_league_rooms.py, ship_hideouts_rooms.py) resolve them. Each room warp is matched to its Sapphire warp event by tile
("at"; else by index) and checked:
  - to an outdoor map: that map's door (above). Exits made before the world changed point at the next door (seen in
    game: the Cycling Road gates, the Friendship Rater's house) or at the room itself (outdoor map not built then);
  - MAP_DYNAMIC (Lilycove's Dept. Store elevator): warp id 256 = Black 2's dynamic warp (ov035 event_mapchange.c
    EventMapChangeWarp_CreateFromEntity: dest id 0x100 -> GameData's next zone, which arriving on such a warp sets to
    where you came from, ov012 SetupZoneWarpArrival; scripts set it with FieldSetNextZone);
  - to another room: that room's zone and Sapphire's warp id (rooms list their warps in Sapphire's order), only
    reported (some rooms list extra warps, e.g. Mt. Pyre's holes).
    python3 b2tools/check_exits.py [WORLD_DIR] [--fix] [--quiet]
--fix rewrites the "to" of the outdoor/dynamic exits that differ, in the room jsons (for rooms no generator rewrites;
a generator rerun against the same world gives the same). Exit status 1 when an outdoor/dynamic exit differs."""
import sys, os, json, collections
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
sys.path.insert(0, os.path.join(ROOT, 'b2tools')); sys.path.insert(0, os.path.join(ROOT, 'b2tools', 'patches'))
import version  # noqa: E402  (HOENN_VERSION=ruby: data/interiors/ruby/ zone files, Ruby's door aliases; notes/RUBY.md)
DYNAMIC = 256

def door_map(world):
    """(outdoor Sapphire map, Sapphire warp id) -> (zone, Black 2 warp index), as hoenn_world.py installs the doors."""
    import narcio, zoneheaders
    from zones import parse_entities
    files = os.path.join(ROOT, 'external', 'pokebw2', 'build', 'b2_us', 'files')
    headers, _ = zoneheaders.load(files)
    ents = narcio.load(files, 126)
    door = {}
    for zid, z in world['zones'].items():
        base = len(parse_entities(ents[headers[int(zid)]['entities']])[0]['warps'])
        for k, d in enumerate(z.get('doors', [])):
            if d.get('foreign') or (d['map'], d['id']) not in door: door[(d['map'], d['id'])] = (int(zid), base + k)
        for d in z.get('slot_doors', []): door[(d['map'], d['id'])] = (int(zid), d['slot'])
    return door

def owner(cfg):
    """Which generator writes this room json (its _doc / what), for the report."""
    s = cfg.get('_doc', '') + ' ' + cfg.get('what', '')
    for g in ('gen_interior_recipes_houses', 'shops_rooms', 'specials', 'centers_rooms', 'gyms_league_rooms',
              'facilities_pyre', 'ship_hideouts_rooms', 'dive_rooms', 'gen_caves', 'gen_interiors'):
        if g in s: return g
    return 'by hand'

def check(world_dir, fix=False):
    world = json.load(open(os.path.join(world_dir, 'world.json')))
    door = door_map(world)
    outdoor = set(json.load(open(os.path.join(ROOT, 'data', 'hoenn_zones.json')))['maps'])
    rooms = json.load(open(os.path.join(ROOT, 'data', 'hoenn_interiors.json')))['rooms']
    bad, info, n = [], [], collections.Counter()
    for name, r in sorted(rooms.items()):
        p = version.overlay_file(os.path.join(ROOT, 'data', 'interiors', f"{r['zone']}.json"))
        mp = os.path.join(ROOT, 'external', 'pokeruby', 'data', 'maps', name, 'map.json')
        if not os.path.exists(p) or not os.path.exists(mp): continue
        cfg = json.load(open(p))
        if cfg.get('room', name) != name: continue
        sap = json.load(open(mp))['warp_events']
        changed = False
        for i, w in enumerate(cfg.get('warps', [])):
            at = [s for s in sap if 'at' in w and [s['x'], s['y']] == list(w['at'])]
            s = at[0] if len(at) == 1 else (sap[i] if 'at' not in w and i < len(sap) else None)
            if s is None or list(w.get('to', [])) == [65535, 65535]: continue      # extra warps / arrival-only spots
            dest, dw = s['dest_map'], s['dest_warp_id']
            dname = dest[4:] if dest.startswith('MAP_') else dest
            dname = next((m for m in list(outdoor) + list(rooms) if m.upper().replace('_', '') == dname.replace('_', '')), dname)
            if dest == 'MAP_DYNAMIC': want, kind = [r['zone'], DYNAMIC], 'dynamic'
            elif dname in outdoor and str(dw).isdigit() and version.door_alias(dname, int(dw)) in door:
                want, kind = list(door[version.door_alias(dname, int(dw))]), 'outdoor'     # (Ruby: Lilycove 14 is door 6)
            elif dname in rooms and str(dw).isdigit() and rooms[dname]['status'] != 'b2': want, kind = [rooms[dname]['zone'], int(dw)], 'room'
            else: n['not checked'] += 1; continue
            n[kind] += 1
            if list(w['to']) == want: continue
            row = (name, r['zone'], i, list(w['to']), want, owner(cfg))
            if kind == 'room': info.append(row); continue
            bad.append(row)
            if fix: w['to'] = want; changed = True
        if changed: json.dump(cfg, open(p, 'w'), indent=1, ensure_ascii=False)
    return bad, info, n

if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    wd = args[0] if args else (os.environ.get('HOENN_WORLD_DIR') or os.path.join(ROOT, 'work', 'world'))
    bad, info, n = check(wd, fix='--fix' in sys.argv)
    print(f'check_exits: {dict(n)}; {len(bad)} outdoor/dynamic exits differ' + (' (fixed)' if bad and '--fix' in sys.argv else '')
          + f', {len(info)} room-to-room exits differ (report only)')
    if '--quiet' not in sys.argv:
        for b in bad: print('  exit', *b[:3], 'to', b[3], 'expected', b[4], '|', b[5])
        for b in info: print('  room', *b[:3], 'to', b[3], 'Sapphire', b[4], '|', b[5])
    sys.exit(1 if bad and '--fix' not in sys.argv else 0)
