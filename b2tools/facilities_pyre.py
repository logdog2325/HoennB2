"""The facilities agent's Mt. Pyre generator: writes the six Mt. Pyre room recipes (data/interior_layouts/MtPyre_*.json)
from Sapphire's metatiles, the holes' warps and step triggers in their zone jsons (data/interiors/<zone>.json) and the
holes' fall scripts in the floors' script files (src/field_scripts/NNNN_room_MtPyre_*.s, between the "// ---- holes"
lines and the PyreFall_* entries; the rest of those files is kept).

    python3 facilities_pyre.py            (then: HOENN_AGENT=facilities zsh b2tools/agent_build_rooms.sh MtPyre_1F ...)
    python3 facilities_pyre.py --recipes  only the six recipes (the zone jsons, scripts and wild tables stay as they are)
    (Emerald's 2F/3F/6F recipes: b2tools/emerald_caves_rooms.py runs recipe() on Emerald's maps: rerun it after this.)

Sapphire's Mt. Pyre (gTileset_Facility) read metatile by metatile (ids checked in the six maps):
  outer walls  0x2ef/0x2f7 (wall), 0x2e4/0x2ec (pillar), 0x2ea/0x2eb, 0x30f/0x317, 0x31f/0x327 (ends and corners),
               0x2b3-0x2bd (doorway up), 0x2c3-0x2cd (doorway down), 0x201 (outside): no floor -> the builder's walls.
               A wall tile with floor somewhere north of it in its column is an INTERNAL wall (the step between two
               levels: 5F rows 4-5, 6F rows 6-7): floor + a low balustrade block (Black 2 rooms are flat: a 50-unit wall
               there would hide the level behind it from the camera).
  gravestones  0x2ee, 0x326, 0x2ed, 0x3d7 (solid): an upright grey stone (block style fac_grave: smooth grey in82_ishi,
               10 x 5 units, 18 high) on a low base (fac_grave_base, 14 x 8 x 3), as Sapphire's grey stones (the user's
               choice over the Celestial Tower's pale blue tomb slabs; sweep_rooms 2026-10-07).
  holes        0x3f2 (MB_MT_PYRE_HOLE: step on it from any side and you fall to the floor below; pokeruby/pokeemerald
               field_control_avatar.c TryStartWarpEventScript -> EventScript_FallDownHoleMtPyre): no floor (a black
               pit), the tile walkable as in Sapphire, and a step trigger on it (it fires whichever way you step on)
               whose script falls to the hole warp's landing tile (SE, fade, MapChangeCore: the cave builder's
               cracked-floor fall, converter/gen_caves.py). The hole's own warp stays in Sapphire's order as a type-1
               0xFFFF marker that never fires. (Until 2026-10-19 the tile was solid with four walk-in warps on it, one
               per direction, but only the first of them, entered walking north, ever fired [test: 2F, 4F, 5F, 6F]:
               5F's two holes can only be walked into eastwards, so a player who fell from 6F into 5F's lower
               part had no way out (Discord softlock; Escape Rope and Fly do not work in Mt. Pyre: Gen 3's
               MAP_TYPE_INDOOR). Black 2 keeps one walk-in warp per tile.)
  landings     the lower floor's warp tiles that holes lead to (Sapphire behaviour 0x08: arrival points only): a
               type-1 warp whose destination is 0xFFFF/0xFFFF, which Black 2 never fires (IsWarpZoneOrWarpID0xFFFF in
               GetWarpIDByPlayerPos); the falls' MapChangeCore lands you on its tile.
  stairs       0x2de, 0xcf (walkable steps through an internal wall): floor with the tower's step texture d17_slope_a.
  doorways     Sapphire's warp tiles with behaviour 0x60 in the back wall: a white frame in42_win01 with a dark inside
               h_kage painted on the wall (the warp itself is the builder's stairs spot: solid, entered walking north).
  wild Pokémon Sapphire's MtPyre_1F-6F tables (land, rate 10: Shuppet, 4F-6F also Duskull; Ruby: Duskull, 4F-6F also
               Shuppet) (wild_tables 2026-10-08; before, the floors had no table in either version): the recipes get
               "encounters": true (models_interior.py: the walkable 0x08 floor tiles, Sapphire's MB_CAVE with the
               encounter attribute, get Black 2's encounter flag 0x84) and each zone json "header": {encounters, enc_slot
               2} (patches/interiors.py applies it after the parent's no-encounter default). The files come from
               converter/gen_caves.py encounters() with Sapphire's table (gen_encounters.py's rules; allocate() gives
               1F a free Unova file that 2F/3F share, 4F one that 5F/6F share: identical tables, in Ruby too); Ruby's
               tables: `HOENN_VERSION=ruby python3 converter/gen_caves.py` (src/encounters/ruby/).
"""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, '..', 'converter'))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
LAYOUTS = os.path.join(ROOT, 'data', 'interior_layouts')
ZONES = os.path.join(ROOT, 'data', 'interiors')
SCRIPTS = os.path.join(ROOT, 'src', 'field_scripts')

WALL = {0x2ef, 0x2f7, 0x2e4, 0x2ec, 0x2ea, 0x2eb, 0x30f, 0x317, 0x31f, 0x327, 0x201} | set(range(0x2b3, 0x2be)) | set(range(0x2c3, 0x2ce))
GRAVE = {0x2ee, 0x326, 0x2ed, 0x3d7}
HOLE, LANDING_BEH, DOOR_BEH = 0x3f2, 0x08, 0x60
STEPS = {0x2de, 0xcf}
ROOMS = {'MtPyre_1F': 341, 'MtPyre_2F': 342, 'MtPyre_3F': 346, 'MtPyre_4F': 350, 'MtPyre_5F': 351, 'MtPyre_6F': 376}

def runs(tiles):
    """Tile set -> row rects [x0, z, x1, z] (inclusive)."""
    out = []
    for z in sorted({t[1] for t in tiles}):
        xs = sorted(x for x, zz in tiles if zz == z)
        s = p = xs[0]
        for x in xs[1:] + [None]:
            if x is not None and x == p + 1: p = x; continue
            out.append([s, z, p, z])
            if x is not None: s = p = x
    return out

def recipe(name):
    from gba import Repo, MetatileRenderer
    repo = Repo(os.path.join(ROOT, 'external', 'pokeruby'))
    mj = repo.map_json(name)
    g, l = repo.layout_grid(mj['layout'])
    mr = MetatileRenderer(repo, l['primary_tileset'], l['secondary_tileset'])
    H, W = g.shape
    mt = lambda x, z: int(g[z, x]) & 0x3FF
    floor, internal, graves, holes, steps = set(), set(), [], [], []
    for z in range(H):
        for x in range(W):
            m = mt(x, z)
            if m in WALL:
                if m != 0x201 and any(mt(x, zz) not in WALL for zz in range(z)):
                    internal.add((x, z)); floor.add((x, z))
                continue
            floor.add((x, z))
            if m in GRAVE: graves.append([x, z])
            if m == HOLE: holes.append([x, z])
            if m in STEPS: steps.append([x, z])
    doors = [(w['x'], w['y']) for w in mj['warp_events'] if mr.behavior(int(g[w['y'], w['x']]) & 0x3FF) == DOOR_BEH]
    decals = []
    for x, z in doors:
        decals.append(dict(tex='in42_win01', src=323, at=[x + 0.5], z=z + 1, y=-2, w=22, h=34, gap=1, _what=f'doorway frame ({x},{z})'))
        decals.append(dict(tex='h_kage', src=323, at=[x + 0.5], z=z + 1, y=-2, w=14, h=28, gap=3, _what='doorway'))
    r = dict(map=name, style='fac_pyre', floor=runs(floor))
    r['floor_tex'] = [dict(rect=[0, 0, W - 1, H - 1], tex='in42_fl01', src=323, size=64, size_v=32, _what='cobblestones, 1 texel per unit')]
    if steps: r['floor_tex'] += [dict(rect=[x, z, x, z], tex='d17_slope_a', src=323, size=16, _what='steps') for x, z in steps]
    if holes:                    # a black pit you can step onto (its step trigger falls: main())
        r['holes'] = [[x, z, x + 1, z + 1] for x, z in holes]
    r['decals'] = decals
    # one upright grey stone per gravestone on a low base (user choice, notes/DECISIONS.md: grey upright stones like
    # Sapphire's, not the Celestial Tower's pale blue slabs; sweep_rooms 2026-10-07): the base 14 x 8 units, the stone
    # 10 x 5 units and 18 high standing on its back half, so neighbours stay separate stones
    blocks = []
    for x, z in graves:
        blocks.append(dict(use='fac_grave_base', units=[x + 0.0625, z + 0.375, x + 0.9375, z + 0.875], _what=f'gravestone base ({x},{z})'))
        blocks.append(dict(use='fac_grave', units=[x + 0.1875, z + 0.375, x + 0.8125, z + 0.6875], _what=f'gravestone ({x},{z})'))
    if internal: blocks.append(dict(use='fac_rail', tiles=sorted([list(t) for t in internal]), _what='step between two levels (Sapphire wall rows)'))
    r['blocks'] = blocks
    # Sapphire's red door mats on the exits (south-arrow warps, behaviour 0x65): Black 2's door mat in70_mat1 (rooms_cleanup)
    exits = sorted((w['x'], w['y']) for w in mj['warp_events'] if mr.behavior(int(g[w['y'], w['x']]) & 0x3FF) == 0x65)
    rows = {}
    for x, z in exits: rows.setdefault(z, []).append(x)
    mats = [dict(tex='in70_mat1', src=351, rect=[min(xs), z, max(xs), z], border=0.25, border_units=3, y=0, _what='exit mat')
            for z, xs in sorted(rows.items())]
    if mats: r['mats'] = mats
    if name == 'MtPyre_1F':      # the entrance corridor south of the hall (17-18, 13-18): no side walls (a 50-unit wall
        r['open'] = [[16, 13, 16, 18], [19, 13, 19, 18]]     # south of the hall would hide it from the camera)
    r['encounters'] = True       # Sapphire's wild encounters on its MB_CAVE floor (0x84 cells; wild_tables 2026-10-08)
    return r, holes

def origin(r):
    """Zone tile of Sapphire (0, 0) in the built room: models_interior.py's default (x 1, the first floor row on chunk
    row 2); the recipes give no "origin"."""
    return r.get('origin', [1, 2 - min(q[1] for q in r['floor'])])

ARRIVAL_SCRIPT = 10017           # the reserved arrival script that fades in after a scripted map change (gen_caves.py)
FALL_MARK = '// ---- holes'      # the fall scripts' part of a floor's script file (write_falls)

def fall_lines(dest_zone, x, z):
    """A hole's fall: the cave builder's cracked-floor fall (converter/gen_caves.py, tested in Granite Cave): SE, fade
    out, the arrival script reserved (fade in), MapChangeCore onto the landing tile (x/y/z in tiles and 16-unit levels,
    facing down). Sapphire: EventScript_FallDownHoleMtPyre (lockall, the player vanishes, SE_FALL, DoFallWarp)."""
    return ['ActorsPauseAll', 'SEPlay SEQ_SE_DANSA', 'FadeOutBlack', f'RTReserveScript {ARRIVAL_SCRIPT}', 'FadeWait',
            f'MapChangeCore {dest_zone}, {x}, 0, {z}, 1', 'FinishAllEvents', 'ActorsUnpauseAll', 'VMHalt']

def write_falls(path, falls):
    """Write a floor's fall scripts into its script file: the "ScriptEntry PyreFall_<k>" entries at the end of the
    ScriptEntry table and their bodies between "// ---- holes" and "// ---- holes end" before the final .balign;
    everything else in the file (the generated people, a story part) is kept, an older holes part replaced.
    falls: [(label, comment, lines)]. Returns {label: script number}."""
    out, skip = [], False
    for l in open(path).read().split('\n'):
        s = l.strip()
        if s.startswith(FALL_MARK + ' end'): skip = False; continue
        if s.startswith(FALL_MARK): skip = True; continue
        if skip or s.startswith('ScriptEntry PyreFall_'): continue
        out.append(l)
    entries = [i for i, l in enumerate(out) if l.strip().startswith('ScriptEntry ')]
    n = len(entries)
    out[entries[-1] + 1:entries[-1] + 1] = [f'    ScriptEntry {lab}' for lab, _, _ in falls]
    body = [f'{FALL_MARK}: the holes\' falls, run by their step triggers (data/interiors/<zone>.json). Written by',
            '// b2tools/facilities_pyre.py with the PyreFall_* entries: edit that script, not this part.']
    for lab, what, lines in falls:
        body += [f'{lab + ":":<47}// {what}'] + [f'    {x}' for x in lines] + ['']
    body[-1] = f'{FALL_MARK} end'
    end = max(i for i, l in enumerate(out) if l.strip().startswith('.balign'))
    out[end:end] = body
    open(path, 'w').write('\n'.join(out))
    return {lab: n + k + 1 for k, (lab, _, _) in enumerate(falls)}

def main(args=()):
    from gba import Repo, MetatileRenderer
    import version
    if version.has_overlay():  # every file written here is shared by all versions (Ruby's/Emerald's tables: gen_caves.py)
        raise SystemExit(f'facilities_pyre.py writes the shared (Sapphire) files: run it without HOENN_VERSION={version.VERSION}')
    import gen_caves
    repo = Repo(os.path.join(ROOT, 'external', 'pokeruby'))
    reg_path = os.path.join(ROOT, 'data', 'hoenn_encounters.json')
    reg = json.load(open(reg_path)); reg_before = dict(reg); report = []
    recipes = {name: recipe(name) for name in ROOMS}
    by_id = {repo.map_json(name)['id']: name for name in ROOMS}
    for name, zone in ROOMS.items():
        r, holes = recipes[name]
        doc = (f'Mt. Pyre {name[-2:]} (Sapphire {repo.map_json(name)["id"]}; zone {zone}, area 323 = Black 2\'s Celestial '
               'Tower: its cobblestone floor in42_fl01, arched walls in42_wl01, grey gravestones). Generated by '
               'b2tools/facilities_pyre.py from Sapphire\'s metatiles (see its docstring); edit that script, not this file.')
        out = dict(_doc=doc, **r)
        json.dump(out, open(os.path.join(LAYOUTS, name + '.json'), 'w'), indent=1, ensure_ascii=False)
        if '--recipes' in args:            # only the recipes (zone jsons left as they are)
            print(name, 'recipe'); continue
        # zone json: a hole = a step trigger (its fall script) + its warp as a marker that never fires; landings never fire
        zp = os.path.join(ZONES, f'{zone}.json')
        zj = json.load(open(zp))
        zj.pop('auto', None); zj['area'] = 323
        mj = repo.map_json(name)
        g, l = repo.layout_grid(mj['layout'])
        mr = MetatileRenderer(repo, l['primary_tileset'], l['secondary_tileset'])
        warps = [w for w in zj['warps'] if not w.get('_extra')]     # (the holes' old extra walk-in warps dropped)
        falls, trig = [], []
        for i, (w, sw) in enumerate(zip(warps, mj['warp_events'])):
            beh = mr.behavior(int(g[sw['y'], sw['x']]) & 0x3FF)
            for k in ('type', 'dir'): w.pop(k, None)
            if beh == 0x0F:                       # hole: you fall to the landing tile of Sapphire's destination warp
                dest = by_id[sw['dest_map']]; dw = int(sw['dest_warp_id'])
                lw = repo.map_json(dest)['warp_events'][dw]
                ox, oz = origin(recipes[dest][0])
                lab = f'PyreFall_{len(falls) + 1}'
                what = f'hole ({sw["x"]},{sw["y"]}) -> fall to {dest} warp {dw} ({lw["x"]},{lw["y"]})'
                falls.append((lab, what, fall_lines(ROOMS[dest], lw['x'] + ox, lw['y'] + oz)))
                trig.append(dict(script=lab, var=0, value=0, at=[sw['x'], sw['y']], what=what))
                w['type'], w['dir'] = 1, 1
                w['to'] = [65535, 65535]
                w['what'] = f'Sapphire warp {i} -> {dest} {dw}: a hole (marker, never fires; its step trigger falls)'
            elif beh == LANDING_BEH:              # arrival point of a hole above: never fires
                w['type'], w['dir'] = 1, 1
                w['to'] = [65535, 65535]
                w['what'] = f'Sapphire warp {i}: landing spot of the hole above (arrival only)'
        zj['warps'] = warps
        if falls:
            sp = [p for p in os.listdir(SCRIPTS) if p.endswith(f'_room_{name}.s')]
            assert len(sp) == 1, f'{name}: script file {sp}'
            num = write_falls(os.path.join(SCRIPTS, sp[0]), falls)
            for t in trig: t['script'] = num[t['script']]
            zj['triggers'] = trig
        else:
            zj.pop('triggers', None)
        # wild Pokémon: Sapphire's table -> src/encounters/NNNN_cave_<Map>.s (or the file of an identical table), the
        # file id in the zone header (enc_slot 2 as the caves and the Abandoned Ship's rooms)
        fid = gen_caves.encounters(name, zone, reg, report, own=gen_caves.sapphire_table(name, 'sapphire'))
        if fid is not None: zj['header'] = dict(zj.get('header', {}), encounters=fid, enc_slot=2)
        docz = (f'Mt. Pyre {name[-2:]} (zone {zone}; scripts/text: the generated *_room_{name} files). Area 323 = Black 2\'s '
                'Celestial Tower (interior pack 41). Warps in Sapphire\'s order (holes and landings: markers that never '
                'fire); a hole falls by its step trigger (b2tools/facilities_pyre.py). Item balls as generated.')
        zj = dict([('_doc', docz)] + [(k, v) for k, v in zj.items() if k != '_doc'])
        json.dump(zj, open(zp, 'w'), indent=1, ensure_ascii=False)
        print(name, zone, len(r['floor']), 'floor rects,', sum(b['use'] == 'fac_grave' for b in r['blocks']), 'graves,', len(holes), 'holes,',
              len(zj['warps']), 'warps, encounter file', fid)
    for line in report: print(' ', line)
    if reg != reg_before: json.dump(reg, open(reg_path, 'w'), indent=1, sort_keys=True)

if __name__ == '__main__':
    main(sys.argv[1:])
