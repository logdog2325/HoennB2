"""Pull the non-layout data for a set of Sapphire maps out of pokeruby: NPCs, signs, warps, wild encounters, text.

Usage: python3 sapphire_data.py ../external/pokeruby LittlerootTown Route101 OldaleTown
Writes ../data/sapphire/<Map>.json (Ruby, Emerald: data/sapphire/<version>/). Everything is copied from the decomp,
nothing is made up. Emerald (HOENN_VERSION=emerald python3 sapphire_data.py ../external/pokeemerald Map ...): the
Sapphire map names are read from the folder Emerald plays them with (version.decomp_map) and the map's one table:
- an NPC/sign whose script is a single `msgbox` gets its text resolved;
- anything with a longer script is marked "complex": true and keeps its script name and every text it can show,
  so it can be ported by hand later.
"""
import sys, os, re, json, glob
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'b2tools'))
import version  # noqa: E402  (HOENN_VERSION=ruby: the *_Ruby wild tables, written to data/sapphire/ruby/; emerald: notes/EMERALD.md)

root = sys.argv[1]
maps = sys.argv[2:]

# label -> text, from every .inc under data/ (map text, common scripts, shared text)
TEXT = {}
for path in sorted(glob.glob(f'{root}/data/**/*.inc', recursive=True) + glob.glob(f'{root}/data/**/*.s', recursive=True)):
    label = None
    for line in open(path, encoding='utf-8', errors='replace'):
        m = re.match(r'^(\w+):{1,2}', line)
        if m:
            label = m.group(1); continue
        m = re.match(r'\s*\.string\s+"(.*)"', line)
        if m and label:
            TEXT[label] = TEXT.get(label, '') + m.group(1)
            if m.group(1).endswith('$'): label = None        # a string ends at its terminator
        elif line.strip() and not line.strip().startswith('@'):
            label = None if not m else label

# script label -> list of lines, from every .inc
SCRIPTS = {}
for path in sorted(glob.glob(f'{root}/data/**/*.inc', recursive=True) + glob.glob(f'{root}/data/**/*.s', recursive=True)):
    cur = None
    for line in open(path, encoding='utf-8', errors='replace'):
        m = re.match(r'^(\w+):{1,2}', line)
        if m:
            cur = m.group(1); SCRIPTS[cur] = []; continue
        if cur is not None and line.strip():
            SCRIPTS[cur].append(line.strip())

def script_info(name):
    body = SCRIPTS.get(name)
    if body is None:
        return {'script': name, 'missing': True}
    texts = [t for t in re.findall(r'\b\w+\b', ' '.join(body)) if t in TEXT]
    cmds = [l.split()[0] for l in body if not l.startswith('@')]
    simple = cmds[:2] == ['msgbox', 'end'] or cmds == ['msgbox', 'end']
    info = {'script': name, 'texts': {t: TEXT[t] for t in dict.fromkeys(texts)}}
    if not simple:
        info['complex'] = True
    return info

wild = json.load(open(f'{root}/src/data/wild_encounters.json'))['wild_encounter_groups'][0]
rates = {f['type']: f.get('encounter_rates') for f in wild['fields']}

def upper_map(name):  # LittlerootTown -> MAP_LITTLEROOT_TOWN, Route101 -> MAP_ROUTE101
    return 'MAP_' + re.sub(r'(?<=[a-z])(?=[A-Z])', '_', name).upper()

out_dir = version.overlay_dir(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'sapphire'))
os.makedirs(out_dir, exist_ok=True)
for name in maps:
    emerald = os.path.basename(os.path.abspath(root)) == 'pokeemerald'
    folder = version.decomp_map(name, 'emerald') if emerald else name
    if emerald and name.endswith('_Emerald') and not os.path.isdir(f'{root}/data/maps/{folder}'):
        folder = name[:-len('_Emerald')]       # an Emerald-only map whose folder is a Sapphire map's name (name_clash)
    mj = json.load(open(f'{root}/data/maps/{folder}/map.json'))
    out = {'map': name, 'id': mj.get('id'), 'layout': mj['layout'], 'music': mj.get('music'),
           'region_map_section': mj.get('region_map_section'), 'weather': mj.get('weather'),
           'connections': mj.get('connections'), 'npcs': [], 'signs': [], 'warps': [], 'coord_events': [],
           'wild': {}}
    for i, o in enumerate(mj.get('object_events', []), 1):
        out['npcs'].append({'local_id': i, 'x': o['x'], 'y': o['y'], 'gfx': o['graphics_id'],
                            'movement': o['movement_type'], 'range': [o['movement_range_x'], o['movement_range_y']],
                            'trainer_type': o['trainer_type'], 'hide_flag': o['flag'], **script_info(o['script'])})
    for b in mj.get('bg_events', []):
        if b.get('type') == 'sign':
            out['signs'].append({'x': b['x'], 'y': b['y'], 'facing': b['player_facing_dir'], **script_info(b['script'])})
        else:
            out['signs'].append({'x': b['x'], 'y': b['y'], 'type': b.get('type'), 'raw': b})
    for i, w in enumerate(mj.get('warp_events', [])):
        out['warps'].append({'id': i, 'x': w['x'], 'y': w['y'], 'dest_map': w['dest_map'], 'dest_warp_id': w['dest_warp_id']})
    for c in mj.get('coord_events', []):
        out['coord_events'].append({**c, **(script_info(c['script']) if c.get('script') else {})})
    for e in wild['encounters']:
        if emerald:                                    # (pokeemerald: no version labels; the map's first table)
            if e['map'] != mj['id'] or out['wild']: continue
        else:
            other = 'Sapphire' if version.is_ruby() else 'Ruby'
            if not (e['map'] == upper_map(name) and e.get('base_label', '').endswith('_' + version.SUFFIX) or
                    (e['map'] == upper_map(name) and not e.get('base_label', '').endswith('_' + other) and name not in out['wild'])):
                continue
        for kind, v in e.items():
            if isinstance(v, dict) and 'mons' in v:
                out['wild'][kind] = {'encounter_rate': v['encounter_rate'], 'slot_rates': rates.get(kind),
                                     'mons': [{'species': m['species'], 'min': m['min_level'], 'max': m['max_level']}
                                              for m in v['mons']]}
    path = f'{out_dir}/{name}.json'
    json.dump(out, open(path, 'w'), indent=1, ensure_ascii=False)
    print(f"{name}: {len(out['npcs'])} NPCs ({sum(1 for n in out['npcs'] if n.get('complex'))} complex), "
          f"{len(out['signs'])} signs, {len(out['warps'])} warps, {len(out['coord_events'])} triggers, wild={list(out['wild'])}")
