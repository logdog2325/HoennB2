"""Give every Sapphire building interior a Black 2 zone (notes/INTERIORS.md, plan: notes/INTERIORS_PLAN.md).

    python3 allocate_interiors.py          -> data/hoenn_interiors.json (zones fixed once given)

Rooms: every MAP_TYPE_INDOOR map reachable from a built outdoor map (data/hoenn_zones.json) through warps, following
warps between indoor maps (stairs). Caves and other underground maps are left for O5. Then the maps only Dive reaches
(Sapphire's dive/emerge connections and setdivewarp targets: underwater maps, Seafloor Cavern, the Sealed Chamber, the
Abandoned Ship's hidden floor; status cave, dive agent 2026-10-06).
Zones:
- Littleroot's rooms keep the zones the interiors agent installed (390-396).
- Pokémon Center 1F rooms get Black 2's own Pokémon Center zones (map type 16, Pokémon Center music, area 283): the
  game may treat those ids specially (respawn), and their area's pack already holds the Center furniture.
- Every other room gets a free zone: not one of ours, not on the engine's special lists (allocate_zones.py DENY/AVOID),
  not on matrix 0, preferring zones with their own matrix (interiors.py rewrites a 1x1 matrix in place).
Each entry: zone, the zone's script/text/entities numbers, Sapphire tilesets (the furniture family), the warps of the
room in Sapphire's order (an interior's warp list keeps that order, so a door can name Sapphire's dest_warp_id).
"""
import os, sys, json, re, collections, glob

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..')
sys.path.insert(0, os.path.join(ROOT, 'b2tools'))
import zoneheaders

RUBY = os.path.join(ROOT, 'external', 'pokeruby', 'data')
FIXED = {'LittlerootTown_BrendansHouse_1F': 390, 'LittlerootTown_BrendansHouse_2F': 391,
         'LittlerootTown_MaysHouse_1F': 392, 'LittlerootTown_MaysHouse_2F': 393,
         'LittlerootTown_ProfessorBirchsLab': 396}
SEQ_BGM_POKECEN = 0x424
# zones whose id Black 2's code treats specially, found by testing rooms in them: never given to a room
NEVER = {63}           # Nimbasa Gym: entering zone 63 spawns Elesa's runway audience (crowd sprites), whatever the room
MOVED = {'EverGrandeCity_PhoebesRoom': 123}     # was 63 (gyms_league, 2026-10-06)

def variant_zones():
    """Zones that cave recipes give copies of their zone (data/cave_layouts/<Map>.json "variants": Altering Cave's
    eight other wild tables, postgame_maps 2026-10-07): never a room's."""
    out = set()
    for f in glob.glob(os.path.join(ROOT, 'data', 'cave_layouts', '*.json')):
        r = json.load(open(f))
        if isinstance(r, dict): out |= {v['zone'] for v in r.get('variants', [])}
    for f in glob.glob(os.path.join(ROOT, 'data', 'interiors', '**', '*.json'), recursive=True):   # (trick_house: a room's
        r = json.load(open(f))                                         # other state in a zone of its own, Puzzle 3's 451)
        if isinstance(r, dict): out |= {v['zone'] for v in r.get('variants', [])}
    return out

def deny_avoid():
    src = open(os.path.join(HERE, 'allocate_zones.py')).read()
    ns = {}
    for name in ('DENY', 'AVOID'):
        m = re.search(rf'^{name} = .*?(?=^\S)', src, re.S | re.M)
        exec(m.group(0), ns)
    return ns['DENY'] | ns['AVOID']

def rooms():
    folders = {}
    for d in os.listdir(os.path.join(RUBY, 'maps')):
        p = os.path.join(RUBY, 'maps', d, 'map.json')
        if os.path.exists(p): folders[json.load(open(p))['id']] = d
    outdoor = set(json.load(open(os.path.join(ROOT, 'data', 'hoenn_zones.json')))['maps'])
    layouts = {l['id']: l for l in json.load(open(os.path.join(RUBY, 'layouts', 'layouts.json')))['layouts'] if 'id' in l}
    def mj(name): return json.load(open(os.path.join(RUBY, 'maps', name, 'map.json')))
    out, queue = {}, [(w['dest_map'], m) for m in sorted(outdoor) if os.path.exists(os.path.join(RUBY, 'maps', m))
                      for w in mj(m)['warp_events']]
    def dive_links(name):
        """Maps reached from `name` by Dive (dive agent, 2026-10-06): its "dive"/"emerge" connections and the targets
        of setdivewarp in its map scripts (pokeruby overworld.c SetDiveWarp: a connection, else the map's
        ON_DIVE_WARP/ON_RESUME script's fixed dive warp)."""
        p = os.path.join(RUBY, 'maps', name, 'scripts.inc')
        src = open(p).read() if os.path.exists(p) else ''
        return [c['map'] for c in (mj(name).get('connections') or []) if c['direction'] in ('dive', 'emerge')] + \
            re.findall(r'setdivewarp\s+(MAP_\w+)', src)
    def walk(queue, dive):
        while queue:
            dest, frm = queue.pop(0)
            name = folders.get(dest)
            if not name or name in outdoor or name in out: continue
            j = mj(name)
            # caves too (status cave, O5); underwater maps (MAP_TYPE_UNDERWATER) only behind Dive (second pass)
            if j['map_type'] not in ('MAP_TYPE_INDOOR', 'MAP_TYPE_UNDERGROUND') + (('MAP_TYPE_UNDERWATER',) if dive else ()): continue
            lay = layouts[j['layout']]
            out[name] = dict(map_id=dest, map_type=j['map_type'], entered_from=frm, tilesets=[lay['primary_tileset'], lay['secondary_tileset']],
                             size=[lay['width'], lay['height']],
                             warps=[dict(x=w['x'], y=w['y'], dest=folders.get(w['dest_map'], w['dest_map']),
                                         dest_warp=int(w['dest_warp_id']) if str(w['dest_warp_id']).isdigit() else w['dest_warp_id'])
                                    for w in j['warp_events']])
            queue += [(w['dest_map'], name) for w in j['warp_events']] + ([(d, name) for d in dive_links(name)] if dive else [])
    walk(queue, False)
    # second pass: the maps only Dive reaches (underwater maps, Seafloor Cavern, the Sealed Chamber, the Abandoned
    # Ship's hidden floor), after the warp-reachable rooms so their entries stay exactly as before
    walk([(d, m) for m in sorted(outdoor | set(out)) if os.path.exists(os.path.join(RUBY, 'maps', m))
          for d in dive_links(m)], True)
    out.update(event_rooms(outdoor, out))
    # fourth pass (battle_tower 2026-10-08): rooms only a script's `warp` reaches (Sapphire's Battle Tower: the lobby's
    # attendant walks you into the Elevator, the Elevator's script warps to the Corridor), after every older entry
    for frm in SCRIPT_WARP_MAPS:
        src = open(os.path.join(RUBY, 'maps', frm, 'scripts.inc')).read()
        walk([(d, frm) for d in re.findall(r'^\s*warp\s+(MAP_\w+)', src, re.M)], False)
    return out

# maps whose scripts.inc `warp` commands lead to rooms no warp event reaches (the fourth pass of rooms()), in order
SCRIPT_WARP_MAPS = ('BattleTower_Lobby', 'BattleTower_Elevator',
                    'Route110_TrickHouseEntrance')   # (trick_house 2026-10-19) its scroll warps to Puzzle2-8

def event_rooms(outdoor, have):
    """Third pass (events agent, 2026-10-07): the caves and rooms of the event maps of other decomps
    (data/hoenn_event_maps.json: Emerald's Navel Rock), reached through warps from their outdoor maps (data/hoenn_zones.json,
    warp-only groups), same record as walk()'s; Emerald calls its island exteriors MAP_TYPE_INDOOR: outdoor maps are skipped
    by name. After the two pokeruby passes, so every older entry stays as it was."""
    from gba import Repo, event_maps, map_folders
    repo = Repo(os.path.join(ROOT, 'external', 'pokeruby'))
    ev = event_maps()
    folders = map_folders(repo.root)
    out = {}
    queue = [(w['dest_map'], m) for m in sorted(outdoor) if m in ev for w in repo.map_json(m)['warp_events']]
    # (postgame_maps 2026-10-07) and the event maps behind warps that data/hoenn_map_additions.json adds to pokeruby's own
    # outdoor maps (Route 103 -> Emerald's Altering Cave); repo.map_json gives those warps, after every older entry
    queue += [(w['dest_map'], m) for m in sorted(outdoor) if m not in ev and os.path.exists(os.path.join(RUBY, 'maps', m))
              for w in repo.map_json(m)['warp_events'] if folders.get(w['dest_map']) in ev]
    while queue:
        dest, frm = queue.pop(0)
        name = folders.get(dest)
        if not name or name not in ev or name in outdoor or name in out or name in have: continue
        j = repo.map_json(name)
        if j['map_type'] not in ('MAP_TYPE_INDOOR', 'MAP_TYPE_UNDERGROUND'): continue
        lay = repo.layouts[j['layout']]
        out[name] = dict(map_id=dest, map_type=j['map_type'], entered_from=frm, tilesets=[lay['primary_tileset'], lay['secondary_tileset']],
                         size=[lay['width'], lay['height']],
                         warps=[dict(x=w['x'], y=w['y'], dest=folders.get(w['dest_map'], w['dest_map']),
                                     dest_warp=int(w['dest_warp_id']) if str(w['dest_warp_id']).isdigit() else w['dest_warp_id'])
                                for w in j['warp_events']], decomp=ev[name])
        queue += [(w['dest_map'], name) for w in j['warp_events']]
    return out

SCRIPT_FILES, TEXT_FILES = 1289, 676        # Black 2's a/0/5/6 and a/0/0/3 file counts

def own_files(out, old, migrate=False):
    """Rooms get their own script, map-script and text file NUMBERS after Black 2's (own_scripts, own_init, own_text;
    no gaps: the text packer needs 0..n). The source files keep the Black 2 zone's numbers in their names (agents name
    them from "scripts"/"text"); the build (patches/scripts.py, text.py) writes them at the own numbers and leaves
    Black 2's files in place, and patches/interiors.py points the zone header at them. Overwriting Black 2's files
    hung the cold boot (found 2026-10-06: code reads some of them directly, e.g. script text 0051). Littleroot's
    hand-made rooms keep Nuvema's files (they boot fine). Numbers are fixed once given."""
    have = {n: v for n, v in old.items() if 'own_scripts' in v}
    used_s = {v[k] for v in have.values() for k in ('own_scripts', 'own_init')}
    used_t = {v['own_text'] for v in have.values()}
    next_s, next_t = max(used_s, default=SCRIPT_FILES - 1) + 1, max(used_t, default=TEXT_FILES - 1) + 1
    for name in sorted(out):
        r = out[name]
        if r['status'] in ('hand', 'link'):
            if name in have:            # a link room someone built by hand (the Hall of Fame) keeps its numbers
                for k in ('own_scripts', 'own_init', 'own_text'): r[k] = have[name][k]
            continue
        if name in have:
            for k in ('own_scripts', 'own_init', 'own_text'): r[k] = have[name][k]
            continue
        r.update(own_scripts=next_s, own_init=next_s + 1, own_text=next_t)
        next_s += 2; next_t += 1

def main():
    files = os.path.join(ROOT, 'external', 'pokebw2', 'build', 'b2_us', 'files')
    headers, _ = zoneheaders.load(files)
    reg_path = os.path.join(ROOT, 'data', 'hoenn_interiors.json')
    old = json.load(open(reg_path))['rooms'] if os.path.exists(reg_path) else {}
    outdoor_zones = {m['zone'] for m in json.load(open(os.path.join(ROOT, 'data', 'hoenn_zones.json')))['maps'].values()}
    taken = outdoor_zones | set(range(389, 397)) | deny_avoid() | {v['zone'] for v in old.values()} | NEVER | set(MOVED.values())
    taken |= variant_zones()
    mat_users = collections.Counter(h['matrix'] for h in headers)
    pc_pool = [i for i, h in enumerate(headers) if h['bgm0'] == SEQ_BGM_POKECEN and h['map_type'] == 16
               and h['area'] == 283 and i not in taken]
    pool = sorted((i for i, h in enumerate(headers) if i not in taken and i not in pc_pool and h['matrix'] != 0
                   and h['map_type'] != 0), key=lambda i: (mat_users[headers[i]['matrix']] != 1, i))
    found = rooms()
    out = {}
    for name in sorted(found):
        r = found[name]
        if name in MOVED: zone = MOVED[name]
        elif name in old: zone = old[name]['zone']
        elif name in FIXED: zone = FIXED[name]
        elif name.endswith('_PokemonCenter_1F') and pc_pool: zone = pc_pool.pop(0)
        else: zone = pool.pop(0)
        hd = headers[zone]
        # status: hand = installed by hand (Littleroot); b2 = (until 2026-10-06) Black 2's own Center room as it is;
        # big = taller/wider than one chunk (needs multi-chunk rooms); link = Pokémon Center 2F and its link rooms;
        # cave = an underground map (caves and dungeons, O5: built by the cave agents, gen_interiors leaves them)
        # (Black 2's Centers have no stairs); auto = converter/gen_interiors.py writes it
        w_, h_ = r['size']
        # center = Pokémon Center 1F/2F rebuilt with Sapphire's Gen 3 layout (nurse and PC, no Mart counter: Hoenn has
        # its own Marts; user, 2026-10-06), by hand in Black 2's own Center zones (1F) — gen_interiors leaves them alone
        # (trick_house 2026-10-19) a room registered by hand ("hand": Trick House Puzzle2-8, b2tools/trick_house.py) stays
        # hand, so gen_interiors.py never writes a placeholder room for it
        status = ('hand' if name in FIXED or old.get(name, {}).get('status') == 'hand' else
                  'center' if name.endswith(('_PokemonCenter_1F', '_PokemonCenter_2F')) else
                  'cave' if r['map_type'] in ('MAP_TYPE_UNDERGROUND', 'MAP_TYPE_UNDERWATER') else   # (underwater: dive agent)
                  'big' if w_ > 30 or h_ > 29 else
                  'link' if r['tilesets'][1] == 'gTileset_CableClub' else 'auto')
        out[name] = dict(zone=zone, status=status, scripts=hd['scripts'], init_scripts=hd['init_scripts'], text=hd['text'],
                         entities=hd['entities'], area=hd['area'], own_matrix=mat_users[hd['matrix']] == 1, **r)
    own_files(out, old)
    json.dump({'_doc': __doc__.strip().split('\n\n')[0], 'rooms': out}, open(reg_path, 'w'), indent=1)
    fam = collections.Counter(tuple(v['tilesets'])[1] for v in out.values())
    print(f'{len(out)} rooms, {sum(1 for v in out.values() if v["own_matrix"])} with their own matrix; '
          f'Pokémon Centers in Black 2 Center zones: {sum(1 for n in out if n.endswith("_PokemonCenter_1F"))}')
    print(dict(fam.most_common()))
    print(dict(collections.Counter(v['status'] for v in out.values())))

def emerald_rooms():
    """HOENN_VERSION=emerald (emerald_world 2026-10-12, notes/EMERALD.md "Emerald's world"): the rooms and caves Emerald's
    outdoor maps lead to that data/hoenn_interiors.json lacks (Emerald-only: Battle Tents, Trainer Hill, Mirage Tower,
    Terra Cave, the Battle Frontier's buildings, the Mystery Events House, ...), found as rooms() finds Sapphire's but
    through Emerald's maps (converter/gba.py world_repo: HoennB2 names, Sapphire's ids for the rooms Sapphire has) ->
    data/emerald/hoenn_interiors.json "rooms" (deep-merged over data/hoenn_interiors.json by the Emerald world's readers),
    status "todo" and no zone: b2tools/world.py makes no door for them (the building or cave mouth stands closed) until a
    rooms agent builds the room and gives it a zone (notes/EMERALD.md work list). Sapphire's file is never written here,
    and the rooms Sapphire has keep their entries (their Emerald changes: data/versions.json "ground")."""
    from gba import world_repo, world_map_folders
    repo = world_repo()
    names = world_map_folders()
    have = json.load(open(os.path.join(ROOT, 'data', 'hoenn_interiors.json')))['rooms']
    outdoor = set(version.load_json(os.path.join(ROOT, 'data', 'hoenn_zones.json'))['maps'])
    out, queue = {}, [(w['dest_map'], m) for m in sorted(outdoor) for w in (repo.map_json(m).get('warp_events') or [])]
    def walk(queue, dive=False):
        while queue:
            dest, frm = queue.pop(0)
            name = names.get(dest)
            if not name or name in outdoor or name in out or name in have: continue
            try: j = repo.map_json(name)
            except FileNotFoundError: continue
            if dive is False and j['map_type'] == 'MAP_TYPE_UNDERWATER': continue
            lay = repo.layouts[j['layout']]
            out[name] = dict(status='todo', map_id=dest, map_type=j['map_type'], entered_from=frm,
                             tilesets=[lay['primary_tileset'], lay['secondary_tileset']], size=[lay['width'], lay['height']],
                             warps=[dict(x=w['x'], y=w['y'], dest=names.get(w['dest_map'], w['dest_map']),
                                         dest_warp=int(w['dest_warp_id']) if str(w['dest_warp_id']).isdigit() else w['dest_warp_id'])
                                    for w in j.get('warp_events') or []], emerald=j.get('_emerald', name))
            queue += [(w['dest_map'], name) for w in j.get('warp_events') or []] + \
                ([(d, name) for d in emerald_dive_links(repo, name)] if dive else [])
    walk(queue)
    # (emerald_caves 2026-10-12) second pass, after every older entry: the Emerald-only maps behind Sapphire's own rooms
    # and caves (their Emerald maps' warps: Meteor Falls -> Steven's Cave, the Fossil Maniac's tunnel -> the Desert
    # Underpass, Underwater3 -> Underwater_MarineCave) and the maps only Emerald's Dive reaches (dive/emerge connections and
    # setdivewarp map scripts: Underwater_Route105/125/129, Underwater_MarineCave -> MarineCave_Entrance), as rooms() does
    # for Sapphire's
    second = []
    for m in sorted(set(have) | outdoor | set(out)):
        try: j = repo.map_json(m)
        except FileNotFoundError: continue
        second += [(w['dest_map'], m) for w in j.get('warp_events') or []] + [(d, m) for d in emerald_dive_links(repo, m)]
    walk(second, dive=True)
    p = os.path.join(ROOT, 'data', 'emerald', 'hoenn_interiors.json')
    # (frontier_pike 2026-10-12) a room an agent has claimed (built, given a zone: "zone" in its entry) keeps its entry as
    # the agent wrote it, also a room only a script's warp reaches (the Battle Pike's corridor and rooms), which the walk
    # above never finds; every unclaimed room is written as before
    old = json.load(open(p))['rooms'] if os.path.exists(p) else {}
    for name, e in old.items():
        if 'zone' in e: out[name] = e
    json.dump({'_doc': ' '.join(emerald_rooms.__doc__.split()), 'rooms': out}, open(p, 'w'), indent=1)
    print(f'{len(out)} Emerald-only rooms (status todo) -> {p}')
    print(dict(collections.Counter(v['map_type'] for v in out.values())))

def emerald_dive_links(repo, name):
    """Maps reached from Emerald map `name` by Dive: its dive/emerge connections and its scripts' setdivewarp targets
    (as rooms().dive_links for pokeruby), by the ids the Emerald view gives them (emerald_caves 2026-10-12)."""
    try: j = repo.map_json(name)
    except FileNotFoundError: return []
    p = os.path.join(repo.root, 'data', 'maps', j.get('_emerald', name), 'scripts.inc')
    src = open(p).read() if os.path.exists(p) else ''
    return [c['map'] for c in (j.get('connections') or []) if c['direction'] in ('dive', 'emerge')] + \
        [repo.hoenn_id(m) for m in re.findall(r'setdivewarp\s+(MAP_\w+)', src)]

def emerald_claim(names, skip=0):
    """HOENN_VERSION=emerald python3 allocate_interiors.py --claim [--skip N] MAP ... (emerald_caves 2026-10-12): give
    Emerald-only rooms/caves of data/emerald/hoenn_interiors.json (status todo) a zone and their own script/text file
    numbers, as main() gives Sapphire's: status 'cave' for underground/underwater maps, else 'auto'. The zone comes from
    main()'s pool (not one of Sapphire's or Emerald's outdoor zones or rooms, not DENY/AVOID/NEVER, not matrix 0, own matrix
    first), never a zone another Emerald room has claimed; --skip N leaves the pool's first N zones for other agents.
    Own numbers continue after the highest of Sapphire's and Emerald's (patches/text.py / scripts.py fill any gap).
    Re-reads the file just before writing it and changes only the named entries (other agents claim in parallel)."""
    import version
    files = os.path.join(ROOT, 'external', 'pokebw2', 'build', 'b2_us', 'files')
    headers, _ = zoneheaders.load(files)
    p = os.path.join(ROOT, 'data', 'emerald', 'hoenn_interiors.json')
    sap = json.load(open(os.path.join(ROOT, 'data', 'hoenn_interiors.json')))['rooms']
    doc = json.load(open(p))
    em = doc['rooms']
    outdoor = {m['zone'] for m in version.load_json(os.path.join(ROOT, 'data', 'hoenn_zones.json'))['maps'].values()}
    taken = outdoor | set(range(389, 397)) | deny_avoid() | {v['zone'] for v in sap.values()} | NEVER | set(MOVED.values())
    taken |= variant_zones() | {v['zone'] for v in em.values() if 'zone' in v}
    for f in glob.glob(os.path.join(ROOT, 'data', 'interiors', '*.json')) + glob.glob(os.path.join(ROOT, 'data', 'interiors', '*', '*.json')):
        try: c = json.load(open(f))
        except ValueError: continue
        if isinstance(c, dict):
            if isinstance(c.get('zone'), int): taken.add(c['zone'])
            taken |= {v['zone'] for v in c.get('variants', [])}
    mat_users = collections.Counter(h['matrix'] for h in headers)
    pc_pool = {i for i, h in enumerate(headers) if h['bgm0'] == SEQ_BGM_POKECEN and h['map_type'] == 16 and h['area'] == 283}
    pool = sorted((i for i, h in enumerate(headers) if i not in taken and i not in pc_pool and h['matrix'] != 0
                   and h['map_type'] != 0), key=lambda i: (mat_users[headers[i]['matrix']] != 1, i))[skip:]
    rooms_ = list(sap.values()) + list(em.values())
    next_s = max(v[k] for v in rooms_ for k in ('own_scripts', 'own_init') if k in v) + 1
    next_t = max(v['own_text'] for v in rooms_ if 'own_text' in v) + 1
    claimed = {}
    for name in names:
        e = em.get(name)
        assert e, f'{name}: not an Emerald-only room of {p} (run allocate_interiors.py in Emerald mode first)'
        if 'zone' in e: claimed[name] = e; continue
        zone = pool.pop(0); hd = headers[zone]
        claimed[name] = dict(e, zone=zone, status='cave' if e['map_type'] in ('MAP_TYPE_UNDERGROUND', 'MAP_TYPE_UNDERWATER') else 'auto',
                             scripts=hd['scripts'], init_scripts=hd['init_scripts'], text=hd['text'], entities=hd['entities'],
                             area=hd['area'], own_matrix=mat_users[hd['matrix']] == 1, own_scripts=next_s, own_init=next_s + 1,
                             own_text=next_t, claimed_by='emerald_caves')
        next_s += 2; next_t += 1
    doc = json.load(open(p))            # (re-read: another agent may have claimed meanwhile)
    clash = {e['zone'] for n, e in doc['rooms'].items() if 'zone' in e and n not in claimed}
    assert not clash & {e['zone'] for e in claimed.values()}, 'a zone was claimed meanwhile: run again'
    doc['rooms'].update(claimed)
    json.dump(doc, open(p, 'w'), indent=1)
    for n, e in claimed.items():
        print(f"{n}: zone {e['zone']} ({e['status']}), scripts/init/text {e['scripts']}/{e['init_scripts']}/{e['text']}, "
              f"own {e['own_scripts']}/{e['own_init']}/{e['own_text']}")

if __name__ == '__main__':
    import version
    if version.is_emerald():                       # (never writes data/hoenn_interiors.json)
        if sys.argv[1:2] == ['--claim']:
            a = sys.argv[2:]; skip = 0
            if a[:1] == ['--skip']: skip, a = int(a[1]), a[2:]
            emerald_claim(a, skip)
        else: emerald_rooms()
    else: main()
