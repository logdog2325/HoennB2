"""Zone files of the Hoenn caves built with b2tools/models_cave.py (notes/CAVES.md).

    python3 gen_caves.py [MAP ...]      (default: every data/cave_layouts/<Map>.json; after b2tools/world.py, which
                                         writes the outdoor doors into world.json: HOENN_WORLD_DIR or work/world)
    python3 gen_caves.py --allocate     gives every status-cave map with a Sapphire wild table its encounter file in
                                         data/hoenn_encounters.json now (done 2026-10-06 for all 45, so agents working
                                         in parallel never allocate: the registry is only rewritten when it changes)

Per cave (zone Z, scripts S, text T from data/hoenn_interiors.json):
  data/interiors/Z.json                 room, area, header (the look's Black 2 cave header, _looks.json "header_zone":
                                        Wellspring Cave 324, or 325 for Sapphire's dark maps; Reversal Mountain 539 for
                                        the lava look), warps in Sapphire's order (a door names Sapphire's
                                        dest_warp_id), item balls, Strength boulders, breakable rocks, simple people and
                                        signs, step triggers (ladders, cracked floors), "dark" (Sapphire's requires_flash,
                                        read by b2tools/patches/zone_effects.py), "cave": true
  src/field_scripts/SSSS_room_<Map>.s   the step-trigger scripts (+ simple people/signs), story scripts go after them
  src/text/script/TTTT_room_<Map>.txt   only when the cave has messages
  src/encounters/NNNN_cave_<Map>.s      Sapphire's wild table through converter/gen_encounters.py's rules (flat rate rule,
                                        data/level_scaling.json levels, the file's original size), file id kept in
                                        data/hoenn_encounters.json (a free Unova file)
A zone json without "cave_auto": true was edited by hand (or by a story agent): only its "warps", "triggers" and
"header" are refreshed, "npcs"/"signs" are kept. Story objects (hide flags, trainers, other scripts) are listed, not
placed.
"""
import os, sys, json, re, collections

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..')
sys.path.insert(0, os.path.join(ROOT, 'b2tools')); sys.path.insert(0, os.path.join(ROOT, 'b2tools', 'patches'))
import move_codes as MOVE_CODES                       # noqa: E402  (v165_fixes)
import narcio, zoneheaders                                       # noqa: E402
import version                                                   # noqa: E402  (HOENN_VERSION: ruby_encounters)
from zones import parse_entities                                 # noqa: E402
import models_cave as MC                                         # noqa: E402

FILES = os.path.join(ROOT, 'external', 'pokebw2', 'build', 'b2_us', 'files')
RUBY = os.path.join(ROOT, 'external', 'pokeruby')
TEMPLATE, TEMPLATE_DARK = 324, 325            # Black 2's Wellspring Cave 1F (lit) and B1F (dark): map type 16, cave
HEADER_KEYS = ('map_type', 'npc_cache', 'weather_word', 'flags', 'icon_word', 'place_display', 'bgm0', 'bgm1', 'bgm2', 'bgm3')
MODEL_BOULDER = 8196          # 0x2004: Hoenn's one-tile Strength boulder (b2tools/patches/boulder_1x1.py fills its empty
                              # object record; Black 2's own 0x2003/0x2005 boulders cover 2x2 tiles, notes/CAVES.md)
SCRIPT_STRENGTH, SCRIPT_ROCK = 10000, 10016   # global scripts: Strength boulder (1243.s), breakable rock (hm_free)
STORY_MARK = '// ---- story'                   # a story agent's scripts follow this line: the file is not rewritten

def folders():
    out = {}
    for d in os.listdir(os.path.join(RUBY, 'data', 'maps')):
        p = os.path.join(RUBY, 'data', 'maps', d, 'map.json')
        if os.path.exists(p): out[json.load(open(p))['id']] = d
    return out

def hole_warp(name):
    """Sapphire's fall destination (setholewarp MAP_X in the map's scripts), or None."""
    p = os.path.join(RUBY, 'data', 'maps', name, 'scripts.inc')
    m = re.search(r'setholewarp\s+(MAP_\w+)', open(p).read()) if os.path.exists(p) else None
    return m.group(1) if m else None

def map_scripts(name):
    """Sapphire's map scripts of a map: [(MAP_SCRIPT_ON_*, label)] from its scripts.inc (story agents' work)."""
    p = os.path.join(RUBY, 'data', 'maps', name, 'scripts.inc')
    if not os.path.exists(p): return []
    src = open(p).read()
    m = re.search(rf'{name}_MapScripts::.*?\n((?:\s*map_script .*\n)*)', src)
    return re.findall(r'map_script (MAP_SCRIPT_\w+), (\w+)', m.group(1)) if m else []

def door_index(world):
    """(outdoor map, Sapphire warp id) -> (zone, Black 2 warp index), as converter/gen_interiors.py."""
    headers, _ = zoneheaders.load(FILES)
    ents = narcio.load(FILES, 126)
    door = {}
    for zid, z in world['zones'].items():
        base = len(parse_entities(ents[headers[int(zid)]['entities']])[0]['warps'])
        for k, d in enumerate(z.get('doors', [])):    # a door in another zone's cell: its copy there (world.py) wins
            if d.get('foreign') or (d['map'], d['id']) not in door: door[(d['map'], d['id'])] = (int(zid), base + k)
        for d in z.get('slot_doors', []): door[(d['map'], d['id'])] = (int(zid), d['slot'])
    return door

def level_y(c, x, z):
    """{"y": height} for a trigger/sign on a raised level (events fire within 2 units of their y); {} at 0."""
    y = MC.MISC.approach_y(c, (x, z), c.fy.get((x, z), 0))    # on a shoal: the shoal's height (caves_misc)
    return {'y': int(y) & 0xFFFF} if y else {}

# Global script 10017 (b2tools/patches/hm_free.py Script_18): FadeInBlack on arrival. A scripted map change leaves the
# arrival zone's people dead unless it fades out, reserves an arrival script and fades in (ch5, tested; story_fixups).
ARRIVAL_SCRIPT = 10017

def _has_story_mark(path):
    """A story agent marked the file ("// ---- story ..." at the start of a line or inside a comment line: ch9's and ch10's
    init files carry the words after the mark; an exact-line test let a rerun overwrite both, story_fixups 2026-10-07)."""
    return any('---- story' in l for l in open(path, encoding='utf-8'))

def step_script(k, what, lines):
    return f'Script_{k}:                                      // {what}\n' + ''.join(f'    {l}\n' for l in lines)

def event_tables(name):
    """The wild tables of an event map of another decomp (data/hoenn_event_maps.json) from that decomp's
    src/data/wild_encounters.json, in its order: Emerald's Altering Cave has nine (gAlteringCave1-9, the first its own;
    VAR_ALTERING_CAVE_WILD_SET picks one); [] for every other map (postgame_maps 2026-10-07)."""
    from gba import event_maps, map_json_path
    if name not in event_maps() or os.path.exists(os.path.join(RUBY, 'data', 'maps', name, 'map.json')): return []
    mid = json.load(open(map_json_path(RUBY, name)))['id']
    p = os.path.join(os.path.dirname(os.path.abspath(RUBY)), event_maps()[name], 'src', 'data', 'wild_encounters.json')
    if not os.path.exists(p): return []
    return [e for g in json.load(open(p))['wild_encounter_groups'] if g.get('label') == 'gWildMonHeaders'
            for e in g['encounters'] if e.get('map') == mid]

def sapphire_table(name, version_=None):
    """The map's wild table of the build's version (HOENN_VERSION; `version_` 'sapphire'/'ruby'/'emerald' picks one;
    Emerald: pokeemerald's table of the map Emerald plays it with, gen_encounters.wild_tables)."""
    import gen_encounters as GE
    ev = event_tables(name)
    if ev: return ev[0]                                         # (an event map: its decomp's own first table)
    if (version_ or version.VERSION) == 'emerald':
        tables = GE.wild_tables('emerald')
    else:
        wild = json.load(open(os.path.join(RUBY, 'src', 'data', 'wild_encounters.json')))
        tables = {e['map']: e for e in wild['wild_encounter_groups'][0]['encounters'] if version.wild_label_ok(e['base_label'], version_)}
    p = os.path.join(RUBY, 'data', 'maps', name, 'map.json')     # the map's own id: upper_map() makes Underwater1 /
    return tables.get(json.load(open(p))['id'] if os.path.exists(p) else GE.upper_map(name))   # Room1 *_1 (dive agent)

def _table_key(t):
    return json.dumps({k: t[k] for k in sorted(t) if k.endswith('_mons')}, sort_keys=True)

def allocate(name, reg):
    """A free Unova encounter file (no Hoenn zone's, not Aspertia's test-harness ones, not in the registry). A map whose
    Sapphire table is identical to an allocated map's shares that map's file (dive agent: Seafloor Cavern's rooms,
    the Abandoned Ship's hidden floor; a/1/2/7 has a fixed number of files, savestates)."""
    if name in reg: return reg[name]
    own = sapphire_table(name)
    if own:
        key = _table_key(own)
        for other, fid in sorted(reg.items()):
            t = sapphire_table(other) if os.path.exists(os.path.join(RUBY, 'data', 'maps', other, 'map.json')) else None
            if t and _table_key(t) == key:
                reg[name] = fid
                return fid
    sizes = [len(x) for x in narcio.load(FILES, 127)]
    headers, _ = zoneheaders.load(FILES)
    zones = json.load(open(os.path.join(ROOT, 'data', 'hoenn_zones.json')))['maps']
    rooms = json.load(open(os.path.join(ROOT, 'data', 'hoenn_interiors.json')))['rooms']
    hoenn = {m['zone'] for m in zones.values()} | {r['zone'] for r in rooms.values()}
    keep = {headers[z]['encounters'] for z in (427, 428)}
    free = sorted({h['encounters'] for i, h in enumerate(headers) if i not in hoenn and h['encounters'] < len(sizes)}
                  - keep - {headers[z]['encounters'] for z in hoenn} - set(reg.values()))
    assert free, 'no free Unova encounter file left (a/1/2/7 keeps its file count: savestates)'
    reg[name] = free[0]
    return free[0]

def encounters(name, zone, reg, report, own=None, fid=None, tag=''):
    """Sapphire's land/water/fishing tables for the cave (gen_encounters.py's rules) -> src/encounters, file id.
    own/fid/tag (postgame_maps): another table of the map (an event map's: event_tables), a fixed file id (recipe
    "encounter_files", kept in the registry as name + tag) and the source file's tag (Altering Cave's _2 ... _9)."""
    import gen_encounters as GE
    own = own or sapphire_table(name)
    if not own: return None
    sizes = [len(x) for x in narcio.load(FILES, 127)]
    if fid is None: fid = allocate(name + tag, reg)
    else: reg[name + tag] = fid
    name_ = name + tag
    out = os.path.join(ROOT, 'src', 'encounters')
    shared = [f for f in os.listdir(out) if f.startswith(f'{fid:04d}_') and not f.endswith(f'_cave_{name_}.s')]
    if shared:                                 # a shared file (allocate): its first map's source makes it
        for f in os.listdir(out):
            if f.endswith(f'_cave_{name_}.s'):
                os.rename(os.path.join(out, f), os.path.join(os.path.expanduser('~/.Trash'), f'{f}.{os.getpid()}'))
        report.append(f'{name_}: Sapphire\'s wild table = {shared[0]}\'s (encounter file {fid} shared)')
        return fid
    sec, lines = cave_lines(own, sizes[fid])
    if 'rock_smash_mons' in own: report.append(f'{name}: Sapphire Rock Smash table dropped (Black 2\'s Rock Smash starts no battles)')
    out = os.path.join(ROOT, 'src', 'encounters')
    for f in os.listdir(out):                  # an older file id's table: to the Trash (never deleted)
        if f.endswith(f'_cave_{name_}.s') and not f.startswith(f'{fid:04d}'):
            os.rename(os.path.join(out, f), os.path.join(os.path.expanduser('~/.Trash'), f'{f}.{os.getpid()}'))
    open(os.path.join(out, f'{fid:04d}_cave_{name_}.s'), 'w').write(cave_text(name_, zone, fid, own, sec, lines))
    return fid

def cave_lines(own, size):
    """(sections, table lines) of a cave's wild table `own` for an encounter file of `size` bytes (gen_encounters.py's rules)."""
    import gen_encounters as GE
    scale = {int(k): v for k, v in json.load(open(os.path.join(ROOT, 'data', 'level_scaling.json')))['curve']['table'].items()}
    lv = lambda l: scale.get(l, l)
    sec = {k: own[key] for k, key in (('land', 'land_mons'), ('water', 'water_mons'), ('fishing', 'fishing_mons')) if key in own}
    rates = dict(grass=GE.LAND_RULES[sec['land']['encounter_rate']] if 'land' in sec else 0,
                 surf=GE.WATER_RULES[sec['water']['encounter_rate']] if 'water' in sec else 0,
                 fishing=GE.FISHING_BITE if 'fishing' in sec else 0)
    slots = lambda mons: [f"    Encounter {m['species']}, {lv(m['min_level'])}, {lv(m['max_level'])}" for m in mons]
    lines = [f"    EncounterRates grass={rates['grass']}, dark_grass=0, shaking_grass=0, surf={rates['surf']}, "
             f"rippling_surf=0, fishing={rates['fishing']}, rippling_fishing=0", '    GrassEncounters']
    if 'land' in sec: lines += slots(sec['land']['mons'])
    lines += ['    DarkGrassEncounters', '    ShakingGrassEncounters', '    SurfEncounters']
    if 'water' in sec: lines += slots(sec['water']['mons'])
    lines.append('    RipplingSurfEncounters')
    lines += GE.fishing_lines(sec['fishing']['mons'] if 'fishing' in sec else None, slots)   # the three rods (rods_fix)
    lines.append('    EncountersEnd')
    return sec, lines * (size // 232)

def cave_text(name_, zone, fid, own, sec, lines):
    return (f'#include "asm/encounters.inc"\n\n// {name_} (zone {zone}, encounter file {fid}). Generated by converter/gen_caves.py '
            f'with converter/gen_encounters.py\'s rules from {own["base_label"]}.\n// Sapphire rates: '
            + ', '.join(f"{k} {v['encounter_rate']}" for k, v in sec.items()) + ', levels scaled by data/level_scaling.json.\n\n'
            + '\n'.join(lines) + '\n')

def ruby_encounters():
    """HOENN_VERSION=ruby (or emerald): only the caves' wild tables differ (notes/RUBY.md 1.3): every cave of the registry
    (data/hoenn_encounters.json, read only: same file ids) whose Ruby (Emerald) table gives other lines than its Sapphire
    table gets src/encounters/<version>/NNNN_cave_<Map>.s. Zones, scripts and text stay Sapphire's (shared). A file that two caves
    share in Sapphire (allocate) is refused if their Ruby tables differ. Also the rooms (any status) whose files come
    from encounters(): Mt. Pyre 1F-6F (b2tools/facilities_pyre.py, wild_tables 2026-10-08)."""
    reg = json.load(open(os.path.join(ROOT, 'data', 'hoenn_encounters.json')))
    rooms = json.load(open(os.path.join(ROOT, 'data', 'hoenn_interiors.json')))['rooms']
    sizes = [len(x) for x in narcio.load(FILES, 127)]
    src = os.path.join(ROOT, 'src', 'encounters')
    out = version.overlay_dir(src); os.makedirs(out, exist_ok=True)
    ep = os.path.join(ROOT, 'data', 'emerald', 'hoenn_encounters.json')   # (emerald_caves: Emerald-only caves' own files,
    own = {n for n in (json.load(open(ep)) if version.is_emerald() and os.path.exists(ep) else {}) if not n.startswith('_')}  # written
    for f in os.listdir(out):                                                # by gen_caves_emerald.py, stay)
        if '_cave_' in f and not any(f.endswith(f'_cave_{n}.s') for n in own):
            os.rename(os.path.join(out, f), os.path.join(os.path.expanduser('~/.Trash'), f'{f}.{os.getpid()}'))
    written, by_fid = [], {}
    for name, fid in sorted(reg.items()):
        if name not in rooms or event_tables(name): continue      # (rooms of every status: Mt. Pyre's are 'auto')
        sap, own = sapphire_table(name, 'sapphire'), sapphire_table(name)
        if not sap or not own: continue
        _, sl = cave_lines(sap, sizes[fid]); sec, rl = cave_lines(own, sizes[fid])
        if fid in by_fid and by_fid[fid] != rl:
            raise SystemExit(f'{name}: encounter file {fid} is shared in Sapphire but its {version.NAME} table differs from another map\'s')
        by_fid[fid] = rl
        if rl == sl: continue
        mine = [f for f in os.listdir(src) if f.startswith(f'{fid:04d}_')]
        if mine and not mine[0].endswith(f'_cave_{name}.s'): continue      # (the file's first map writes it)
        open(os.path.join(out, f'{fid:04d}_cave_{name}.s'), 'w').write(cave_text(name, rooms[name]['zone'], fid, own, sec, rl))
        written.append(f'{name}:{fid}')
    print(len(written), f'{version.NAME} cave tables:', ' '.join(written))

def dest_origin(dest, dc):
    """Zone tile of Sapphire tile (0, 0) in a step trigger's destination: the cave's origin, or for a room built by
    b2tools/models_interior.py (no cave recipe: Sky Pillar's floors, caves_misc) its recipe's "origin", else the built
    room.json's."""
    if os.path.exists(os.path.join(MC.LAYOUTS, dest + '.json')): return dc.ox, dc.oz
    p = os.path.join(ROOT, 'data', 'interior_layouts', dest + '.json')
    o = json.load(open(p)).get('origin') if os.path.exists(p) else None
    if not o:
        p = os.path.join(MC.OUT, dest, 'room.json')
        o = json.load(open(p)).get('origin') if os.path.exists(p) else None
    return tuple(o) if o else (dc.ox, dc.oz)

def tide_script(k, t):
    """Zone-init script of a cave with two layouts chosen by the clock (recipe "tide", caves_misc; notes/CAVES.md
    "Shoal Cave: tides"): Sapphire's UpdateShoalTideFlag (time_events.c: high tide 00-02, 09-14, 21-23 h, decided when
    you come in from outdoors and kept while you are inside) on Black 2's map replacement: MapReplaceSetEvent uid, set,
    1 (ov012 scrcmd_game_state.c s00DA: sets the event's work, reloads and re-patches the zone's matrix; zone init runs
    after FieldMapControl_LoadZone and before the field opens, event_mapchange.c) swaps the zone's matrix for the
    high-tide one (a/0/1/0 entry kind 1: b2tools/patches/interiors.py alt_rooms).
      event         the map replace event uid of the tide (9: work 0x403A == 0x1028)
      flag          also set/cleared with it (Sapphire's FLAG_SYS_SHOAL_TIDE, for story scripts)
      inside_event  a map replace event no replacement uses (8: work 0x4039 == 0x120, saved): "came from inside";
                    every other room of the cave sets it, the entrance reads and clears it (Black 2's zone init can't
                    tell where the player came from: PlayerGetGPos needs the field's player actor)
      update        true in the entrance: decide the tide unless the player came from inside
      flooded       warp indices whose Sapphire warp tile is water at high tide (no warp there): moved to tile (0, 0)
                    while the tide event is set (ObjInitWarpGPos = SetZoneWarpLocation, eventdata_system.c), else a
                    type-4 warp still fires when a surfer bumps into its arch (FieldPlayerGrid_CheckWarpAtHitWall)"""
    ev, flag, ins = t['event'], t.get('flag'), t.get('inside_event')
    lines, tail = [], ''
    if t.get('update'):
        if ins is not None:
            lines += [f'MapReplaceIsEventSet {ins}, 0x8002', f'MapReplaceSetEvent {ins}, 0, 0',
                      'WorkCmpConst 0x8002, 1', 'VMJumpIf CMP_EQ, L_TideKept']
        lines += ['RTCGetTime 0x8000, 0x8001']
        for h, lab in ((3, 'L_TideHigh'), (9, 'L_TideLow'), (15, 'L_TideHigh'), (21, 'L_TideLow')):
            lines += [f'WorkCmpConst 0x8000, {h}', f'VMJumpIf CMP_LT, {lab}']
        hi = ([f'FlagSet {flag}'] if flag else []) + [f'MapReplaceSetEvent {ev}, 1, 1', 'VMJump L_TideKept']
        lo = ([f'FlagReset {flag}'] if flag else []) + [f'MapReplaceSetEvent {ev}, 0, 1']
        tail += 'L_TideHigh:\n' + ''.join(f'    {l}\n' for l in hi) + 'L_TideLow:\n' + ''.join(f'    {l}\n' for l in lo)
        tail += 'L_TideKept:\n'
    elif ins is not None:
        lines += [f'MapReplaceSetEvent {ins}, 1, 0']
    body = []
    if t.get('flooded'):
        body += [f'MapReplaceIsEventSet {ev}, 0x8002', 'WorkCmpConst 0x8002, 0', 'VMJumpIf CMP_EQ, L_TideDone']
        body += [f'ObjInitWarpGPos {w}, 0, 0, 0' for w in t['flooded']]
        body += ['L_TideDone:']
    body += ['VMHalt']
    what = 'zone init: the tide (Sapphire UpdateShoalTideFlag)' if t.get('update') else 'zone init: inside the cave (tide kept)'
    out = step_script(k, what, lines)
    out += tail + ''.join((f'{l}\n' if l.endswith(':') else f'    {l}\n') for l in body)
    return out

def story_flag(name):
    """Number of a FLAG_ name in src/include/hoenn.h (converter/gen_story_ids.py), or 0."""
    if not hasattr(story_flag, 'ids'):
        src = open(os.path.join(ROOT, 'src', 'include', 'hoenn.h')).read()
        story_flag.ids = {k: int(v, 0) for k, v in re.findall(r'#define\s+(FLAG_\w+)\s+(0x[0-9a-fA-F]+|\d+)', src)}
    return story_flag.ids.get(name, 0)

def main(names):
    if version.is_emerald():   # (emerald_caves 2026-10-12) no names: the shared caves' Emerald tables (as before); --emerald
        if not names: return ruby_encounters()   # or names: Emerald's own caves and the Emerald variants with their own zone
        from gen_caves_emerald import emerald_main   # json (converter/gen_caves_emerald.py; after Emerald's world.py: its doors)
        return emerald_main([] if names == ['--emerald'] else names)
    if version.has_overlay():  # Ruby changes only wild tables here; zones, scripts, text are Sapphire's (shared)
        return ruby_encounters()
    reg_path = os.path.join(ROOT, 'data', 'hoenn_encounters.json')
    if names[:1] == ['--allocate']:
        reg = json.load(open(reg_path)); before = dict(reg)
        rooms = json.load(open(os.path.join(ROOT, 'data', 'hoenn_interiors.json')))['rooms']
        for n in sorted(k for k, v in rooms.items() if v['status'] == 'cave'):
            if sapphire_table(n): print(n, allocate(n, reg))
        if reg != before: json.dump(reg, open(reg_path, 'w'), indent=1, sort_keys=True)
        return
    names = names or sorted(f[:-5] for f in os.listdir(MC.LAYOUTS) if f.endswith('.json') and not f.startswith('_')
                            # (emerald_caves 2026-10-12) Emerald's caves ("map": "emerald/<Map>") are gen_caves_emerald's
                            and not str((MC.load_json(os.path.join(MC.LAYOUTS, f), {}) or {}).get('map', '')).startswith('emerald/'))
    # recipes that are another layout of a zone's cave ("alt_of": Shoal Cave's high tide, caves_misc) have no zone of
    # their own: models_cave.py builds them, b2tools/patches/interiors.py installs them through the zone's "alt_rooms"
    alts = [n for n in names if (MC.load_json(os.path.join(MC.LAYOUTS, n + '.json'), {}) or {}).get('alt_of')]
    names = [n for n in names if n not in alts]
    rooms = json.load(open(os.path.join(ROOT, 'data', 'hoenn_interiors.json')))['rooms']
    zones = json.load(open(os.path.join(ROOT, 'data', 'hoenn_zones.json')))
    world = json.load(open(os.path.join(os.environ.get('HOENN_WORLD_DIR') or os.path.join(ROOT, 'work', 'world'), 'world.json')))
    door = door_index(world)
    fold = folders()
    headers, _ = zoneheaders.load(FILES)
    balls = json.load(open(os.path.join(ROOT, 'data', 'hoenn_items.json')))['balls']
    sprites = json.load(open(os.path.join(ROOT, 'data', 'sprite_map.json')))
    reg = json.load(open(reg_path)); reg_before = dict(reg)
    from gen_map_content import ruby_scripts, simple_message
    from gen3text import convert
    from gen_interiors import npc_block, sign_block
    text, scripts = ruby_scripts()
    report, story = [], collections.defaultdict(list)
    caves = {}
    def cave(n):
        if n not in caves: caves[n] = MC.Cave(n)
        return caves[n]
    for name in names:
        r = rooms[name]; zone = r['zone']
        c = cave(name); sm = c.sm
        dark = bool(sm['json'].get('requires_flash'))
        # ---- warps, in Sapphire's order
        warps, unresolved = [], []
        for spot, w in zip(c.spots, r['warps']):
            dest, dw = w['dest'], w['dest_warp']
            to = door.get((dest, dw))
            if to is None and dest in rooms:
                st = rooms[dest]['status']
                to = (rooms[dest]['zone'], 0 if st == 'b2' else dw) if st in ('auto', 'big', 'b2', 'hand', 'cave', 'center') else None
            what = f'Sapphire warp {spot["index"]} ({w["x"]},{w["y"]}) -> {dest} {dw}'
            if to is None: unresolved.append(what); to = (zone, 0); what += ' (not built: points at this cave\'s warp 0)'
            warps.append(dict(at=[w['x'], w['y']], to=list(to), what=what))
        # ---- links (recipe "links", b2tools/models_cave.py): Sapphire's map connections between two caves, one wide warp
        # each way after Sapphire's warps; the other map's matching link (side opposite, "to" this map) is its target
        opp = {'n': 's', 's': 'n'}
        for spot in (s_ for s_ in c.spots if s_['kind'] == 'link'):
            ln = c.r['links'][spot['link']]
            dc = cave(ln['to'])
            nth = next(k_ for k_, l2 in enumerate(dc.r.get('links', [])) if l2['to'] == name and l2['side'] == opp[ln['side']])
            dw_ = len(rooms[ln['to']]['warps']) + nth
            warps.append(dict(x=spot['x'], z=spot['z'], w=spot['w'], h=1, type=4, dir=spot['dir'],
                              to=[rooms[ln['to']]['zone'], dw_], **MC.spot_y(c, spot),
                              what=f'Sapphire connection {ln["side"]} (x {ln["x"][0]}-{ln["x"][1]}) -> {ln["to"]} warp {dw_}'))
        # ---- step triggers: ladders (Sapphire's step-on warps) and cracked floors / holes (fall to the hole warp)
        blocks, trig, k = [], [], 0
        for spot, w in zip(c.spots, r['warps']):
            if not spot.get('step'): continue
            dest = w['dest']
            if dest not in rooms or rooms[dest]['status'] != 'cave':
                report.append(f'{name}: ladder {w["x"]},{w["y"]} -> {dest}: not a cave, no trigger'); continue
            dc = cave(dest); dwp = rooms[dest]['warps'][w['dest_warp']]
            dox, doz = dest_origin(dest, dc)
            tx, tz = dox + dwp['x'], doz + dwp['y']
            # MapChangeCore zone, x, y, z, dir: x/y/z are shifted left 16 (s00C4_MapChangeCore, ov036 0x021a80dc), so
            # y counts 16-unit levels like x/z count tiles (the arrival tile's level; 0 without levels)
            ty = round(dc.fy.get((dwp['x'], dwp['y']), 0) / 16)
            k += 1
            blocks.append(step_script(k, f'ladder {spot["kind"][7:]} ({w["x"]},{w["y"]}) -> {dest} warp {w["dest_warp"]} ({dwp["x"]},{dwp["y"]})',
                                      ['ActorsPauseAll', 'SEPlay SEQ_SE_KAIDAN', 'FadeOutBlack', f'RTReserveScript {ARRIVAL_SCRIPT}',
                                       'FadeWait', f'MapChangeCore {rooms[dest]["zone"]}, {tx}, {ty}, {tz}, 1',
                                       'FinishAllEvents', 'ActorsUnpauseAll', 'VMHalt']))
            tide = c.r.get('tide') or {}                  # a ladder under water at high tide (caves_misc): only while
            flooded = spot['index'] in tide.get('flooded', ())   # the tide event's work is 0 (work 0x4031 + uid)
            trig.append(dict(script=k, var=0x4031 + tide['event'] if flooded else 0, value=0, at=[w['x'], w['y']], **level_y(c, w['x'], w['y'])))
        falls = [(x, z) for (x, z), s in c.special.items() if s in ('cracked', 'hole')]
        if falls:
            hw = hole_warp(sm['name']); dest = fold.get(hw)
            if not dest or dest not in rooms:
                report.append(f'{name}: {len(falls)} cracked floor tiles, hole warp {hw} not a Hoenn cave: no triggers')
            else:
                dc = cave(dest); dz = rooms[dest]['zone']
                for (x, z) in sorted(falls, key=lambda t: (t[1], t[0])):
                    k += 1
                    dox, doz = dest_origin(dest, dc)
                    lx, lz = x, z
                    if not dc.sm['walk'][z][x]:     # Sapphire drops you onto a wall there too (you step off it); land on
                        near = [(x + a, z + b) for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, 1), (1, -1), (-1, -1))
                                if 0 <= z + b < len(dc.sm['walk']) and 0 <= x + a < len(dc.sm['walk'][0]) and dc.sm['walk'][z + b][x + a]]
                        if near: lx, lz = near[0]   # its nearest walkable tile instead (script_check 2026-10-08: Sky Pillar
                        report.append(f'{name}: fall from {x},{z} lands on a blocked tile of {dest}'   # 2F (0,8))
                                      + (f': moved to {lx},{lz}' if near else ''))
                    tx, tz = dox + lx, doz + lz
                    lab = f'L_Fall_{k}'
                    # Sapphire: walking on cracked floor (not at Mach Bike speed) drops you to the same spot below
                    # (field_tasks.c PerStepCallback_806A07C + cave_hole.inc); Black 2 has one bike: riding it crosses
                    # (PlayerGetExState 1 = on the bike, as 0192.s dismounts with it)
                    blocks.append(step_script(k, f'cracked floor ({x},{z}) -> fall to {dest} ({lx},{lz})',
                        ['PlayerGetExState 0x8010', 'VMStackPush 0x8010', 'VMStackPushConst 1', 'VMStackCmp CMP_EQ',
                         f'VMJumpIf CMP_STACK, {lab}', 'VMHalt', '']).rstrip() + f'\n{lab}:\n' + ''.join(f'    {l}\n' for l in
                        ['ActorsPauseAll', 'SEPlay SEQ_SE_DANSA', 'FadeOutBlack', f'RTReserveScript {ARRIVAL_SCRIPT}', 'FadeWait',
                         f'MapChangeCore {dz}, {tx}, {round(dc.fy.get((lx, lz), 0) / 16)}, {tz}, 1',
                         'FinishAllEvents', 'ActorsUnpauseAll', 'VMHalt']))
                    trig.append(dict(script=k, var=0, value=0, at=[x, z], **level_y(c, x, z)))
        # ---- objects
        npcs, signs, msgs = [], [], []
        for lid, o in enumerate(sm['objects'], 1):
            g = o['graphics_id']; at = [o['x'], o['y']]
            if g == 'OBJ_EVENT_GFX_ITEM_BALL':
                b = balls.get(o['script'])
                if b: npcs.append(dict(uid=lid, model=110, script=b['script'], flag=b['flag'], dir=1, at=at, what=f'item ball {b["item"]}'))
                else: story[name].append(f'item ball {o["script"]} without a Black 2 item')
                continue
            if g == 'OBJ_EVENT_GFX_PUSHABLE_BOULDER':
                npcs.append(dict(uid=lid, model=MODEL_BOULDER, script=SCRIPT_STRENGTH, flag=0, dir=1, at=at, what='Strength boulder')); continue
            if g == 'OBJ_EVENT_GFX_BREAKABLE_ROCK':
                code = sprites.get(g, {}).get('code') or 206
                fl = str(o.get('flag', '0'))
                hide = 0
                if not fl.startswith('FLAG_TEMP') and fl != '0':
                    # Sapphire's hide flag (Rusturf Tunnel's two rocks, Victory Road's): the rock stays away once it is
                    # set. Black 2's 10016 only deletes the actor (until the map reloads), so the story script that
                    # follows the smash sets the flag (Rusturf: scenes/RusturfTunnel_Ch3.inc; story_fixups 2026-10-07)
                    hide = story_flag(fl)
                    story[name].append(f'breakable rock {lid} ({o["x"]},{o["y"]}) has {fl} ' + (f'({hide}): a story script '
                                       'must set it when the rock is smashed (10016 only deletes the actor)' if hide else
                                       '(no id in src/include/hoenn.h: placed without it)'))
                npcs.append(dict(uid=lid, model=code, script=SCRIPT_ROCK, flag=hide, dir=1, at=at, what='breakable rock'
                                 + (f' ({fl})' if hide else ''))); continue
            if o.get('trainer_type', 'TRAINER_TYPE_NONE') not in ('TRAINER_TYPE_NONE', '0', 0):
                story[name].append(f'trainer {g} ({o["x"]},{o["y"]}) {o["script"]}'); continue
            if str(o.get('flag', '0')) not in ('0', ''):
                story[name].append(f'story object {g} ({o["x"]},{o["y"]}) {o["script"]} hide flag {o["flag"]}'); continue
            code = (sprites.get(g) or {}).get('code')
            label = simple_message(o['script'], text, scripts) if code else None
            if not label or convert(text[label])[1]:
                story[name].append(f'person {g} ({o["x"]},{o["y"]}) {o["script"]}: not one message / no sprite'); continue
            msgs.append(convert(text[label])[0]); k += 1
            blocks.append(npc_block(k, len(msgs) - 1))
            face = {'MOVEMENT_TYPE_FACE_UP': 0, 'MOVEMENT_TYPE_FACE_DOWN': 1, 'MOVEMENT_TYPE_FACE_LEFT': 2,
                    'MOVEMENT_TYPE_FACE_RIGHT': 3}.get(o['movement_type'], 1)
            n = dict(uid=lid, model=code, script=k, dir=face, at=at)
            n.update(MOVE_CODES.room_npc(o))     # Sapphire's movement type as Black 2's code (b2tools/move_codes.py)
            npcs.append(n)
        for b in sm['bgs']:
            if b.get('type') == 'hidden_item':
                story[name].append(f'hidden item {b["item"]} at ({b["x"]},{b["y"]}) {b["flag"]} (Black 2 hidden items: not placed)'); continue
            if b.get('type') != 'sign' or not b.get('script'): continue
            label = simple_message(b['script'], text, scripts)
            if not label or convert(text[label])[1]: story[name].append(f'sign ({b["x"]},{b["y"]}) {b["script"]}'); continue
            msgs.append(convert(text[label])[0]); k += 1
            blocks.append(sign_block(k, len(msgs) - 1))
            signs.append(dict(script=k, at=[b['x'], b['y']], dir=0 if b.get('player_facing_dir', '').endswith('NORTH') else 4,
                              **level_y(c, b['x'], b['y'])))
        for e in sm['coords']:
            story[name].append(f'coord event ({e["x"]},{e["y"]}) {e.get("script")} var {e.get("var")}={e.get("var_value")}')
        for kind_, label in map_scripts(sm['name']):     # (the cave falls are done above: CaveHole_* and the
            if label.startswith('CaveHole_') or (falls and kind_ == 'MAP_SCRIPT_ON_RESUME'): continue   # hole warp)
            story[name].append(f'map script {kind_} {label}')
        # ---- header: Black 2's own cave header (the look's; map type 16 = interior: every chunk of the matrix loaded)
        # a map the room builder builds (no cave recipe; caves_misc: Sky Pillar, New Mauville) names its zone's area and
        # Black 2 header zone in its interior recipe ("cave_zone"); a cave recipe may name a header zone too
        ir = {} if os.path.exists(os.path.join(MC.LAYOUTS, name + '.json')) else \
            (MC.load_json(os.path.join(ROOT, 'data', 'interior_layouts', name + '.json'), {}) or {})
        cz = ir.get('cave_zone', {})
        t = headers[cz.get('header_zone') or c.r.get('header_zone') or (c.look.get('header_zone_dark', TEMPLATE_DARK) if dark else c.look.get('header_zone', TEMPLATE))]
        hd = {k_: t[k_] for k_ in HEADER_KEYS}
        hd['map_type'] = 16
        sec = sm['json'].get('region_map_section')
        if sec in zones['places']: hd['place'] = zones['places'][sec]['line']
        files_ = c.r.get('encounter_files')          # fixed files and zone copies with the map's other tables
        tables_ = event_tables(name)                   # (postgame_maps: Emerald's Altering Cave, recipe "variants")
        fid = encounters(name, zone, reg, report, fid=files_[0] if files_ else None)
        hd.update(encounters=fid if fid is not None else 0x1FFF, enc_slot=2 if fid is not None else 6)
        variants = []
        for v in c.r.get('variants', []):
            t_ = v['table']
            vf = encounters(name, v['zone'], reg, report, own=tables_[t_ - 1], fid=files_[t_ - 1], tag=f'_{t_}')
            variants.append(dict(zone=v['zone'], encounters=vf, table=tables_[t_ - 1]['base_label']))
        # ---- write
        jpath = os.path.join(ROOT, 'data', 'interiors', f'{zone}.json')
        old = json.load(open(jpath)) if os.path.exists(jpath) else None
        cfg = dict(zone=zone, room=name, cave=True, cave_auto=True, area=cz.get('area', c.look['area']), dark=dark, header=hd,
                   warps=warps, triggers=trig, npcs=npcs, signs=signs,
                   what=f'{name}: cave (converter/gen_caves.py, b2tools/models_cave.py); story objects: see notes/CAVES.md')
        if old and not old.get('cave_auto'):
            for k_ in ('npcs', 'signs'): cfg[k_] = old.get(k_, cfg[k_])
            cfg['cave_auto'] = False
            report.append(f'{name}: zone {zone} json edited by hand: kept its npcs/signs')
        files = {k_: r[k_] for k_ in ('scripts', 'init_scripts', 'text')} if r.get('own_files') else {}
        cfg.update(files)
        if variants: cfg['variants'] = variants         # (b2tools/patches/interiors.py copies the zone's header)
        if c.r.get('alt_rooms') or ir.get('alt_rooms'):                 # other layouts of this zone (caves_misc; an interior
            cfg['alt_rooms'] = c.r.get('alt_rooms') or ir['alt_rooms']  # recipe too: New Mauville's barriers, story_fixups)
        json.dump(cfg, open(jpath, 'w'), indent=1, ensure_ascii=False)
        if c.r.get('tide'):                              # the zone-init tide script and the zone's map-script file
            k += 1; blocks.append(tide_script(k, c.r['tide']))
            ip = os.path.join(ROOT, 'src', 'field_scripts', f'{r["init_scripts"]:04d}_room_{name}_init.s')
            if not os.path.exists(ip) or not _has_story_mark(ip):
                what_ = 'decides the tide by the clock' if c.r['tide'].get('update') else 'marks "inside the cave" and keeps the tide'
                open(ip, 'w').write(f'// Map scripts of {name} (zone {zone}): converter/gen_caves.py (caves_misc). Zone init (MapScript 2) =\n'
                                    f'// script {k}: {what_}. Story map scripts: add a line "{STORY_MARK}" (then this file\n'
                                    '// is left alone) and add them to the table.\n#include "asm/field_script.inc"\n#include "hoenn.h"\n\n'
                                    f'    MapScript 2, {k}\n    MapScriptsEnd\n    .balign 4, 0\n')
            else: report.append(f'{name}: {ip} has story map scripts: not rewritten (it must still run script {k} at zone init)')
        if c.r.get('underwater') and c.r.get('uw_effect', True):   # (dive agent) Black 2's underwater look
            k += 1
            blocks.append(step_script(k, 'field load / return: the underwater effect (Abyssal Ruins script plugin, '
                                         'b2tools/patches/dive.py lists this zone)', ['AbyssalRuinsCmd_StartUnderwaterEffect', 'VMHalt']))
            ip = os.path.join(ROOT, 'src', 'field_scripts', f'{r["init_scripts"]:04d}_room_{name}_init.s')
            if not os.path.exists(ip) or not _has_story_mark(ip):
                open(ip, 'w').write(f'// Map scripts of {name} (zone {zone}): converter/gen_caves.py (dive agent). Field load (MapScript 3)\n'
                                    f'// and return (MapScript 4) = script {k}: the underwater effect, as Black 2\'s Abyssal Ruins\n'
                                    f'// (0483.s). Story map scripts: add a line "{STORY_MARK}" (then this file is left alone).\n'
                                    '#include "asm/field_script.inc"\n#include "hoenn.h"\n\n'
                                    f'    MapScript 3, {k}\n    MapScript 4, {k}\n    MapScriptsEnd\n    .balign 4, 0\n')
            else: report.append(f'{name}: {ip} has story map scripts: not rewritten (it must still run script {k} on field load)')
        elif c.r.get('underwater'):                      # "uw_effect": false: an earlier run's effect file to the Trash
            ip = os.path.join(ROOT, 'src', 'field_scripts', f'{r["init_scripts"]:04d}_room_{name}_init.s')
            if os.path.exists(ip) and 'gen_caves.py (dive agent)' in open(ip).read() \
                    and not _has_story_mark(ip):
                os.rename(ip, os.path.join(os.path.expanduser('~/.Trash'), os.path.basename(ip) + f'.{os.getpid()}'))
        sp =os.path.join(ROOT, 'src', 'field_scripts', f'{r["scripts"]:04d}_room_{name}.s')
        entries = ''.join(f'    ScriptEntry Script_{i}\n' for i in range(1, k + 1)) or '    ScriptEntry Script_None\n'
        src = (f'// {name} (zone {zone}): cave_builder (converter/gen_caves.py): ladders and cracked floors as step triggers\n'
               f'// (Sapphire\'s step-on warps), simple people/signs. Story scripts: add them after a line "{STORY_MARK}" (this\n'
               f'// generator keeps everything from that line on and the entries you add: b2tools/story_merge.py) and number them\n'
               f'// after these entries.\n'
               + (f'// Messages: src/text/script/{r["text"]:04d}_room_{name}.txt\n' if msgs else '')
               + '#include "asm/field_script.inc"\n#include "hoenn.h"\n\n' + entries + '    ScriptEntriesEnd\n\n'
               + ('\n'.join(blocks) if blocks else 'Script_None:\n    VMHalt\n') + '    .balign 4, 0\n')
        from story_merge import write_room_script, write_room_text  # a story agent's part (after STORY_MARK) stays
        if msgs:
            w = write_room_text(os.path.join(ROOT, 'src', 'text', 'script', f'{r["text"]:04d}_room_{name}.txt'), msgs, sp)
            if w: report.append(w)
        if write_room_script(sp, src) != 'written': report.append(f'{name}: {sp} has story scripts (after "{STORY_MARK}"): merged')
        report.append(f'{name}: zone {zone}, {len(warps)} warps ({len(unresolved)} unresolved), {len(trig)} triggers, '
                      f'{len(npcs)} objects, encounters {fid}, dark {dark}')
        for u in unresolved: report.append(f'  unresolved: {u}')
    if reg != reg_before: json.dump(reg, open(reg_path, 'w'), indent=1, sort_keys=True)
    for n in alts: report.append(f'{n}: another layout of {MC.load_json(os.path.join(MC.LAYOUTS, n + ".json"))["alt_of"]} (no zone of its own)')
    print('\n'.join(report))
    for n, items in story.items():
        print(f'{n}: left for the story agents:'); print('\n'.join('  ' + s for s in items))

if __name__ == '__main__':
    main(sys.argv[1:])
