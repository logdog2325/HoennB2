"""Write Black 2 wild encounter tables (src/encounters/NNNN_<Map>.s) for every built Hoenn zone from Sapphire's own
tables (pokeruby src/data/wild_encounters.json, the *_Sapphire entries).

    python3 gen_encounters.py          (after b2tools/world.py; writes src/encounters/ and data/hoenn_encounters.json)

- Slots are Sapphire's, in order: grass 12 (odds 20,20,10,10,10,10,5,5,4,4,1,1 in both games), surf 5 (60,30,5,4,1
  in both), fishing = Sapphire's Super Rod 5 slots (40,40,15,4,1 in both), and the Old Rod's 2 + Good Rod's 3 slots in
  Black 2's rippling-fishing group, which b2tools/patches/rods.py reads for those rods (fishing_lines; rods_fix
  2026-10-12). Rock Smash tables are dropped (Black 2's Rock Smash starts no battles). No shaking grass, rippling water
  or dark grass in Hoenn (their rates stay 0, so Black 2 never makes a rippling spot).
- Rates: Black 2's rate byte picks a rule in overlay 36 (notes/RESEARCH_ENCOUNTERS.md). Each Sapphire rate gets a
  flat rule after 2 safe steps, set by b2tools/patches/encounter_rules.py (RULES below): chance p = 23*rate/4096 in
  Sapphire, rounded to Black 2's whole percents. Fishing bite 50 % (Black 2's usual value).
- A section the zone's own map lacks is borrowed from the map with most such tiles in the zone (tiles of no map in a
  town's cell). Since every map has its own zone up to its edges (b2tools/world.py zone_rects, 2026-10-08) no town holds
  a route's grass or water any more; a map that once had a file and now has no table gets an empty one (same file).
- Levels: Sapphire's through the Exp. Share curve in data/level_scaling.json (decision 2026-10-06,
  notes/LEVEL_SCALING.md; levels up to 24 are unchanged).
- Versions (b2tools/version.py): HOENN_VERSION=ruby reads pokeruby's *_Ruby tables, HOENN_VERSION=emerald pokeemerald's
  tables (wild_tables: the map Emerald plays each Sapphire map with, version.decomp_map, data/versions.json "maps"); both
  keep Sapphire's file ids and write only the files whose lines differ from Sapphire's, into src/encounters/<version>/.
  Emerald-only outdoor maps (the Safari Zone's two new areas, postgame_fix 2026-10-19) get pokeemerald's own table in a
  file of their own (emerald_new_maps: data/emerald/hoenn_encounters.json, gen_caves_emerald.allocate's rules); their
  zone is a part zone of the neighbour's (data/emerald/hoenn_weather.json "parts" with "wild": patches/fixed_weather.py).
- File ids: the zone's own Unova encounter file if it had one, else another Unova file no Hoenn zone uses (fixed once
  given, kept in data/hoenn_encounters.json). Every file keeps its original size (a 4-season file gets the table 4
  times): the game keeps a/1/2/7 open with its file table in RAM, so savestates made with the original layout read
  garbage once files move (found 2026-10-06: no battles, then the error screen).
"""
import json, os, re, sys, collections

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..')
sys.path.insert(0, os.path.join(ROOT, 'b2tools'))
import version  # noqa: E402  (HOENN_VERSION=ruby|emerald: that version's tables; only the files that differ, into src/encounters/<version>/)

# Sapphire rate -> Black 2 rule id (values written by patches/encounter_rules.py)
LAND_RULES = {4: 12, 10: 11, 15: 4, 20: 8, 25: 9,
              7: 5}     # (Emerald's Altering Cave, rate 7 = 3.9 %: no 4 % rule exists; rule 5 = 5 %, the nearest, as water 9)
WATER_RULES = {1: 3, 4: 12, 9: 5}
FISHING_BITE = 50
GRASS_CLASSES = {'tall_grass', 'long_grass', 'ash_grass'}
WATER_CLASSES = {'water', 'deep_water', 'current_n', 'current_s', 'current_e', 'current_w'}

def fishing_lines(mons, slots):
    """Black 2's two fishing groups from a Gen 3 table's 10 fishing slots (old_rod 0-1, good_rod 2-4, super_rod 5-9 in
    pokeruby's and pokeemerald's wild_encounters.json), slots(mons) -> Encounter lines (rods_fix 2026-10-12):
    FishingEncounters = the Super Rod's 5 (Black 2's fishing odds 40/40/15/4/1 = Gen 3's Super Rod odds);
    RipplingFishingEncounters = the Old Rod's 2, then the Good Rod's 3 (b2tools/patches/rods.c picks them with Gen 3's
    70/30 and 60/20/20 when that rod is used; Hoenn's rippling-fishing rate stays 0, so Black 2 never reads them)."""
    lines = ['    FishingEncounters']
    if mons: lines += slots(mons[5:10])
    lines.append('    RipplingFishingEncounters')
    if mons: lines += slots(mons[0:5])
    return lines

def upper_map(name):
    return 'MAP_' + re.sub(r'(?<=[a-z])(?=[A-Z0-9])', '_', name).upper().replace('ROUTE_1', 'ROUTE1')

def species(s):
    return s.replace('SPECIES_', 'SPECIES_')

def _map_ids(root):
    """{map folder: MAP_ id} of a decomp's data/maps."""
    base = os.path.join(root, 'data', 'maps')
    return {d: json.load(open(os.path.join(base, d, 'map.json')))['id'] for d in sorted(os.listdir(base))
            if os.path.exists(os.path.join(base, d, 'map.json'))}

_WILD = {}

def wild_tables(version_=None):
    """{pokeruby MAP_ id of a Sapphire map: its wild table (a wild_encounters.json entry)} of the version (the build's,
    or version_): pokeruby's *_Sapphire / *_Ruby entries; Emerald: pokeemerald's gWildMonHeaders entry of the map Emerald
    plays it with (version.decomp_map: its renames; Sapphire maps Emerald dropped have none), its first one when a map
    has several (Altering Cave: event maps read their own, gen_caves.event_tables)."""
    v = version_ or version.VERSION
    if v != 'emerald':
        wild = json.load(open(os.path.join(ROOT, 'external', 'pokeruby', 'src', 'data', 'wild_encounters.json')))
        return {e['map']: e for e in wild['wild_encounter_groups'][0]['encounters'] if version.wild_label_ok(e['base_label'], v)}
    if v in _WILD: return _WILD[v]                     # (gen_caves asks once per cave: read the two decomps once)
    em = version.decomp('emerald')
    wild = json.load(open(os.path.join(em, 'src', 'data', 'wild_encounters.json')))
    group = next(g for g in wild['wild_encounter_groups'] if g.get('label') == 'gWildMonHeaders')
    by_id = {}
    for e in group['encounters']: by_id.setdefault(e['map'], e)
    eids = _map_ids(em)
    out = {}
    for name, rid in _map_ids(os.path.join(ROOT, 'external', 'pokeruby')).items():
        en = version.decomp_map(name, 'emerald')
        if en in eids and eids[en] in by_id: out[rid] = by_id[eids[en]]
    _WILD[v] = out
    return out

def main():
    import world as W, zoneheaders
    files = os.path.join(ROOT, 'external', 'pokebw2', 'build', 'b2_us', 'files')
    headers, _ = zoneheaders.load(files)
    import narcio
    n_files = len(narcio.load(files, 127))
    tables = wild_tables()
    # Ruby, Emerald (notes/RUBY.md "WP0 layout", notes/EMERALD.md): the same maps, file ids (data/hoenn_encounters.json,
    # read only) and rules; a file is written to src/encounters/<version>/ only when its table lines differ from
    # Sapphire's of the same run
    sap_tables = wild_tables('sapphire')
    scale = None
    sp = os.path.join(ROOT, 'data', 'level_scaling.json')
    if os.path.exists(sp):                       # converter/level_scaling.py: Sapphire level -> level with Exp. Share
        scale = {int(k): v for k, v in json.load(open(sp))['curve']['table'].items()}
    cfg, lay = W.load()
    world, _, maps = W.compose(cfg, lay)
    wj = json.load(open(os.path.join(os.environ.get('HOENN_WORLD_DIR') or os.path.join(ROOT, 'work', 'world'), 'world.json')))
    owner = {(c['cx'], c['cz']): c['zone'] for c in wj['cells']}
    count = collections.defaultdict(collections.Counter)     # zone -> (kind, map) -> tiles in the zone's cells
    frames = [(world, maps, owner)] + [(fw, fm, fo) for _, fw, fm, fo in W.standalone_frames(cfg)]   # + warp-only maps
    for fworld, _, fowner in frames:
        for (wx, wz), (name, cls, walk) in fworld.items():
            if fworld is not world and not walk: continue     # (a warp-only map's border: Sapphire's border blocks)
            z = W.zone_of(fowner, wx, wz, wj.get('zone_rects', []) if fowner is owner else ())   # (sub-cell zones)
            if cls in GRASS_CLASSES: count[z][('land', name)] += 1
            elif cls in WATER_CLASSES: count[z][('water', name)] += 1
    built = {n for f in frames for n in f[1]}
    all_maps = dict(cfg['maps'], **{n: mc for n, mc in cfg['standalone'].items() if n in built})
    reg_path = os.path.join(ROOT, 'data', 'hoenn_encounters.json')
    reg = json.load(open(reg_path)) if os.path.exists(reg_path) else {}
    reg = {k: v for k, v in reg.items() if v < n_files}          # (earlier versions appended files)
    sizes = [len(x) for x in narcio.load(files, 127)]
    hoenn_zones = {mc['zone'] for mc in all_maps.values()}
    keep = {headers[z]['encounters'] for z in (427, 428)}          # Aspertia: the test harness starts there
    free = sorted({h['encounters'] for i, h in enumerate(headers) if i not in hoenn_zones and h['encounters'] < n_files}
                  - keep - {headers[z]['encounters'] for z in hoenn_zones})
    out_dir = version.overlay_dir(os.path.join(ROOT, 'src', 'encounters'))
    os.makedirs(out_dir, exist_ok=True)
    for f in os.listdir(out_dir):
        if f.endswith('.s') and '_auto_' in f: os.remove(os.path.join(out_dir, f))
    used = {v for v in reg.values()}
    written = []
    def sections(name, zone, tables):
        own = tables.get(upper_map(name), {})
        sec = {}
        for kind, key in (('land', 'land_mons'), ('water', 'water_mons'), ('fishing', 'fishing_mons')):
            src = own if key in own else None
            if src is None and kind in ('land', 'water'):
                donors = [(n, c) for (k, n), c in count[zone].items() if k == kind and upper_map(n) in tables
                          and (('land_mons' if kind == 'land' else 'water_mons') in tables[upper_map(n)])]
                if donors:
                    src = tables[upper_map(max(donors, key=lambda d: d[1])[0])]
            if src is None and kind == 'fishing' and sec.get('water') is not None:
                src = sec['water'][1] if 'fishing_mons' in sec['water'][1] else None
            if src is not None and key in src:
                sec[kind] = (src[key], src)
        return sec
    for name, mc in all_maps.items():
        if name not in built: continue
        zone = mc['zone']
        sec = sections(name, zone, tables)
        # (a map with no table of its own or borrowed: no file; one that had a file keeps it, written empty, so its
        # zone header never points at the file's Unova table. Since every map has its own zone up to its edges,
        # world.py zone_rects 2026-10-08, the towns that borrowed a route's grass in their cells (Oldale, Rustboro,
        # Mauville, Fortree) have none)
        if not sec and name not in reg: continue
        if version.has_overlay() and name not in reg: continue  # (Ruby/Emerald never allocate: Sapphire's file ids)
        if name in reg: fid = reg[name]
        else:
            orig = headers[zone]['encounters']
            fid = orig if orig < n_files and orig not in used else next(f for f in free if f not in used)
            reg[name] = fid; used.add(fid)
        def table_lines(sec):
            return season_lines(sec, scale) * (sizes[fid] // 232)   # same table for every season, original file size
        lines = table_lines(sec)
        if version.has_overlay() and lines == table_lines(sections(name, zone, sap_tables)):
            continue                                     # same as Sapphire's file: shared
        open(os.path.join(out_dir, f'{fid:04d}_auto_{name}.s'), 'w').write(table_text(name, zone, fid, sec, lines, scale))
        written.append(f'{name}:{fid}')
    if not version.has_overlay(): json.dump(reg, open(reg_path, 'w'), indent=1, sort_keys=True)
    if version.is_emerald(): written += emerald_new_maps(all_maps, built, scale, out_dir)
    print(len(written), 'tables:', ' '.join(written))

def season_lines(sec, scale):
    """One season's table (a/1/2/7: 232 bytes) of the sections {kind: (mons table, wild_encounters.json entry)}."""
    def lv(level):
        return scale[level] if scale else level
    lines = []
    rates = dict(grass=0, surf=0, fishing=0)
    if 'land' in sec: rates['grass'] = LAND_RULES[sec['land'][0]['encounter_rate']]
    if 'water' in sec: rates['surf'] = WATER_RULES[sec['water'][0]['encounter_rate']]
    if 'fishing' in sec: rates['fishing'] = FISHING_BITE
    lines.append(f"    EncounterRates grass={rates['grass']}, dark_grass=0, shaking_grass=0, surf={rates['surf']}, "
                 f"rippling_surf=0, fishing={rates['fishing']}, rippling_fishing=0")
    def slots(mons):
        return [f"    Encounter {m['species']}, {lv(m['min_level'])}, {lv(m['max_level'])}" for m in mons]
    lines.append('    GrassEncounters')
    if 'land' in sec: lines += slots(sec['land'][0]['mons'])
    lines += ['    DarkGrassEncounters', '    ShakingGrassEncounters', '    SurfEncounters']
    if 'water' in sec: lines += slots(sec['water'][0]['mons'])
    lines.append('    RipplingSurfEncounters')
    lines += fishing_lines(sec['fishing'][0]['mons'] if 'fishing' in sec else None, slots)   # the three rods
    lines.append('    EncountersEnd')
    return lines

def table_text(name, zone, fid, sec, lines, scale):
    src_note = ', '.join(f"{k} from {v[1]['base_label']}" for k, v in sec.items()) or 'no table (no grass or water in its zone)'
    return (f'#include "asm/encounters.inc"\n\n// {name} (zone {zone}, encounter file {fid}). Generated by '
            f'converter/gen_encounters.py: {src_note}.\n'
            + ('// Sapphire rates: ' + ', '.join(f"{k} {v[0]['encounter_rate']}" for k, v in sec.items())
               + (', levels scaled by data/level_scaling.json' if scale else ', Sapphire levels') + '.\n' if sec else '') + '\n'
            + '\n'.join(lines) + '\n')

def emerald_new_maps(all_maps, built, scale, out_dir):
    """Emerald-only outdoor maps with a pokeemerald table (postgame_fix 2026-10-19: SafariZone_Northeast_Emerald and
    SafariZone_Southeast_Emerald, pokeemerald's SafariZone_Northeast / _Southeast): their own land, water and rod tables
    (Rock Smash: b2tools/patches/hm_free.py rock_smash_wild_asm) in a file of their own, one season (a new file, as the
    Emerald-only caves'), kept in data/emerald/hoenn_encounters.json (gen_caves_emerald.allocate). The map shares its
    neighbour's zone; the zone that plays this file is a part zone over the map (data/emerald/hoenn_weather.json "parts",
    "wild": the map's name; patches/fixed_weather.py)."""
    import gen_caves_emerald as GCE
    from gba import emerald_names
    em = version.decomp('emerald')
    wild = json.load(open(os.path.join(em, 'src', 'data', 'wild_encounters.json')))
    group = next(g for g in wild['wild_encounter_groups'] if g.get('label') == 'gWildMonHeaders')
    by_id = {}
    for e in group['encounters']: by_id.setdefault(e['map'], e)
    eids = _map_ids(em)
    sapphire = set(_map_ids(os.path.join(ROOT, 'external', 'pokeruby')))
    fwd = emerald_names()[0]
    reg_path = os.path.join(ROOT, 'data', 'emerald', 'hoenn_encounters.json')
    reg = {k: v for k, v in json.load(open(reg_path)).items() if not k.startswith('_')}
    before = dict(reg)
    shared_reg = json.load(open(os.path.join(ROOT, 'data', 'hoenn_encounters.json')))
    written = []
    for name, mc in sorted(all_maps.items()):
        if name not in built or name in sapphire: continue
        e = by_id.get(eids.get(fwd.get(name, name)))
        if not e: continue
        sec = {k: (e[key], e) for k, key in (('land', 'land_mons'), ('water', 'water_mons'), ('fishing', 'fishing_mons')) if key in e}
        if not sec: continue
        fid = GCE.allocate(name, e, reg, shared_reg, {})
        for f in os.listdir(out_dir):                    # (this map's file under another id: to the Trash, never deleted)
            if f.endswith(f'_auto_{name}.s') and not f.startswith(f'{fid:04d}_'):
                os.rename(os.path.join(out_dir, f), os.path.join(os.path.expanduser('~/.Trash'), f'{f}.{os.getpid()}'))
        open(os.path.join(out_dir, f'{fid:04d}_auto_{name}.s'), 'w').write(table_text(name, mc['zone'], fid, sec, season_lines(sec, scale), scale))
        written.append(f'{name}:{fid}')
    if reg != before: json.dump(dict(_doc=GCE.REG_DOC, **dict(sorted(reg.items()))), open(reg_path, 'w'), indent=1)
    return written

if __name__ == '__main__':
    main()
