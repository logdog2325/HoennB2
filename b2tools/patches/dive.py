"""Dive in Hoenn (dive agent, 2026-10-06; notes/DIVE.md). List after `interiors`, `story` and `standalone` (it reads the
zones they install) and after `hm_free` (its global scripts 10011/10012 do the dive and the surfacing).

Black 2 has a Dive of its own: on Undella Bay (zone 240) the A button over one of four 3x3-tile squares runs global
script 10011 ("Would you like to use Dive?" -> CallDiving 0 -> EventDiveIn: the player sinks, special state 3, and
EventMapChangeDiveIn takes them to the square's Abyssal Ruins zone, arriving at that zone's spawn; the dive spot is
remembered as the "next zone"). Surfacing is a script: FieldSetNextZone + CallDiving 1 (Abyssal Ruins 0482.s Script_3).
Where you may dive is GetAbyssalRuinsDiveZoneID (ov036 0x021C3D50) -> DecideAbyssalRuinsDiveZoneByUndellaBayPos
(0x021C3D10): 4 entries of (zone, x, z, dest zone) at 0x021D2540, each square x..x+2, z..z+2 [code][bytes].

Sapphire's Dive works by coordinates: dive at (x, y) of Route 124 and you are at (x, y) of Underwater1 (the "dive"
connection), surface anywhere above surfacing water to the same (x, y) of the route (the "emerge" connection); maps
without a connection set a fixed spot by script (setdivewarp, e.g. Sootopolis -> Underwater_SootopolisCity (9, 6))
(pokeruby overworld.c SetDiveWarp, field_control_avatar.c TrySetDiveWarp). Its dive patches are irregular (Route 126's
deep water around Sootopolis is one 1,213-tile ring), so 3x3 squares and one arrival per zone can't follow it. This
patch replaces the two functions with one that keeps Black 2's interface (zone in, BOOL + zone out) and reads a table
built from Sapphire's maps, so Dive works exactly where Sapphire's does and lands where Sapphire's lands:

  GetAbyssalRuinsDiveZoneID(field, *zone) (ov036 0x021C3D10, its three callers re-pointed: the A button in
  FieldEventProvider_Grid_CheckForEvent, the party menu's CalcPlayerActionPossibilities, EventDiveIn_Callback)
    - zone table entry of the player's zone (u16 per zone: record offset / 16 << 4 | record count), 0 = no dive;
    - records (16 bytes: u16 x0, z0; u8 w, h; u16 dest zone; s16 ax, az; u16 tile map offset; u16 flags) of rectangles
      in the zone's tile coordinates (the actor's grid position, as Black 2's table) and its tile map (1 byte per
      tile, 0 = no);
    - hit: *zone = dest, and works VAR_HOENN_DIVE_X/_Z/_ZONE (hoenn.h, consecutive) = the tile on the other side
      (x + ax, z + az, or (ax, az) when flags bit 0: Sapphire's fixed setdivewarp spots) and the zone;
    - the table is a file of a/1/2/6 (zone entities: the file of zone 241, never used by Hoenn) read on demand
      through the field's own handle on that archive (EventData->entityArc, GFL_ArcToolReadRange): no RAM, no size
      limit. 1 read for a zone without dives, 3-4 with.
  EventMapChangeDiveIn_Create (ov035 0x0217DE10): LoadZoneSpawnInfoCheckRail -> a hook (in ov033 0x02179E98, the dead
    CheckAbyssalRuinsStepEvent) that loads the spawn as before and puts the player on the works' tile; after the map
    change EventDiveIn_Callback walked the diver one tile up (actor command 8, the Abyssal Ruins' swim forward [test:
    every arrival was one tile north]): command 0 (face up) instead (ov033 0x02179FB6).
  Underwater surfacing: the same lookup on the underwater zones' surfacing tiles (Sapphire: not MB_NO_SURFACING 0x19
    / MB_SEAWEED_NO_SURFACING 0x2A); hm_free's 10011/10012 see the player diving (PlayerGetExState 3) and surface:
    FieldSetNextZone VAR_HOENN_DIVE_ZONE, 0, VAR_HOENN_DIVE_X, 0, VAR_HOENN_DIVE_Z + CallDiving 1. Sapphire surfaces
    with B, Black 2's field only checks events on A: here it is A (or Dive from the party menu).
  Code space: the two old functions (140 B, ov036 0x021C3D10-0x021C3D9C), UpdateAbyssalRuinsSteps (ov036 0x02182424,
    68 B; its only call, CheckPerStepEvents 0x02182218, now returns 0: it counted steps in zones 245-248 only, the
    Abyssal Ruins, which Hoenn never uses: allocate_zones DENY) and the CheckAbyssalRuinsStepEvent it called (ov033,
    108 B).
  The underwater look: ov012's script plugin of the Abyssal Ruins (SCRIPT_PLUGIN_TABLE entry 5, zones 241-245) gives
    AbyssalRuinsCmd_StartUnderwaterEffect (command 1000) to the zones in its list. Its list is moved onto the 12 slots
    of the Black Tower's (478-487, 492, 493: DENY zones, never used by Hoenn; the Black Tower entry gets count 0) and
    holds the underwater zones.

Test switch: HOENN_TEST_DIVE=1 makes Littleroot's town sign give the 8 badges, HM06 and a Pokémon that knows Dive and
Surf (the scripts patch's HOENN_TEST_WARP still warps from the sign afterwards: see dive_build.sh)."""
import os, sys, json, struct, importlib.util

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'b2tools')); sys.path.insert(0, os.path.join(ROOT, 'converter'))
_spec = importlib.util.spec_from_file_location('exp_share_', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'exp_share.py'))
_es = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_es)
_patch, _load, _save, _bl = _es._patch, _es._load, _es._save, _es._bl

OV012, OV033, OV035, OV036 = 0x021503C0, 0x02176B00, 0x0217C940, 0x0217F600   # extract/b2_us/arm9_overlays/overlays.yaml
# Black 2 functions (decomp symbols)
Field_GetPlayerStateZoneID, Field_GetPlayer, FieldPlayer_GetActor = 0x021804D8, 0x021804F0, 0x0219A6A0
GFL_ArcToolReadRange, LoadZoneSpawnInfoCheckRail, GameData_GetEventData = 0x0204AC58, 0x020190C8, 0x02017240
GAMEDATA_EVENTDATA, GAMEDATA_EVENTWORK = 86 * 4, 107 * 4    # GameData_GetEventData / _GetEventWork offsets (arm9)
# code space (see the docstring)
LOOKUP = (0x021C3D10, 0x021C3D9C)                           # ov036: DecideAbyssal... + GetAbyssalRuinsDiveZoneID
HELPER = (0x02182424, 0x02182468)                           # ov036: UpdateAbyssalRuinsSteps
HOOK = (0x02179E98, 0x02179F04)                             # ov033: CheckAbyssalRuinsStepEvent
READ = (0x021D2540, 0x021D2560)                             # ov036: UNDELLA_BAY_DIVE_WARPS (the old table)
STEPS_CALL = 0x02182218                                     # ov036 CheckPerStepEvents: bl UpdateAbyssalRuinsSteps
LOOKUP_CALLS = {'arm9_ov036.bin': (OV036, 0x021816D2), 'arm9_ov012.bin': (OV012, 0x02159344),
                'arm9_ov033.bin': (OV033, 0x02179F94)}
OLD_LOOKUP = 0x021C3D50
SPAWN_CALL = 0x0217DE10                                     # ov035 EventMapChangeDiveIn_Create: bl LoadZoneSpawn...
DIVE_ARRIVAL_ACMD = 0x02179FB6                              # ov033 EventDiveIn_Callback: movs r1, #8 (FldAct_SetAcmd)
# ov012 SCRIPT_PLUGIN_TABLE (5 words per entry): Abyssal Ruins entry 5, Black Tower entry 9, and their zone lists
PLUGIN_ABYSS_ENTRY, ABYSS_ZONES, BLACK_TOWER_ZONES = 0x0216C210, 0x0216C138, 0x0216C16C
ABYSS_LIST = (241, 242, 243, 244, 245)
BLACK_TOWER_LIST = (478, 479, 480, 481, 482, 483, 484, 485, 486, 487, 492, 493)
ZONES = 616                                                 # zone table entries (Black 2 has 615 zones)
ENTITIES_ARC = 126                                          # a/1/2/6
# the table's file: the entity file of zone 241 (Abyssal Ruins, allocate_zones DENY: never a Hoenn zone). Replacing a
# file keeps a/1/2/6's file count and section offsets, which the field's open handle (EventData->entityArc) caches
# from the ROM it was opened on: an appended file made a savestate's handle fail its fileCount assert (tested)
TABLE_ZONE = 241

DIVE = {0x11, 0x12, 0x14}                                   # pokeruby MetatileBehavior_IsDiveable
NO_SURFACE = {0x19, 0x2A}                                   # pokeruby MetatileBehavior_IsNotSurfacable
# Sapphire's dive links (pokeruby data/maps/*/map.json "dive"/"emerge" connections and setdivewarp map scripts; checked
# against them by links()): (map with the tiles, which tiles, destination map, fixed destination tile or None = the
# same coordinates). "surface@x,y" = only that tile, listed before the map's general surfacing (first record wins).
LINKS = [
    ('Route124', 'dive', 'Underwater1', None), ('Route126', 'dive', 'Underwater2', None),
    ('Route127', 'dive', 'Underwater3', None), ('Route128', 'dive', 'Underwater4', None),
    ('SootopolisCity', 'dive', 'Underwater_SootopolisCity', (9, 6)),
    ('Route134', 'dive', 'Underwater_Route134', (8, 6)),
    ('SealedChamber_OuterRoom', 'dive', 'Underwater_SealedChamber', (12, 44)),
    ('SeafloorCavern_Entrance', 'dive', 'Underwater_SeafloorCavern', (6, 5)),
    ('AbandonedShip_Rooms_B1F', 'dive', 'AbandonedShip_Underwater2', (17, 4)),
    ('AbandonedShip_HiddenFloorCorridors', 'dive', 'AbandonedShip_Underwater1', (5, 4)),
    ('Underwater1', 'surface', 'Route124', None), ('Underwater2', 'surface', 'Route126', None),
    ('Underwater3', 'surface', 'Route127', None), ('Underwater4', 'surface', 'Route128', None),
    ('Underwater_SootopolisCity', 'surface', 'SootopolisCity', (29, 53)),
    ('Underwater_Route134', 'surface', 'Route134', (60, 31)),
    ('Underwater_SealedChamber', 'surface@12,44', 'SealedChamber_OuterRoom', (10, 19)),
    ('Underwater_SealedChamber', 'surface', 'Route134', (60, 31)),
    ('Underwater_SeafloorCavern', 'surface', 'SeafloorCavern_Entrance', (10, 17)),
    ('AbandonedShip_Underwater1', 'surface', 'AbandonedShip_HiddenFloorCorridors', (0, 10)),
    ('AbandonedShip_Underwater2', 'surface', 'AbandonedShip_Rooms_B1F', (13, 7)),
]

# (emerald_caves 2026-10-12) Emerald's own dive links, after Sapphire's, in an Emerald build only: the Marine Cave
# (pokeemerald MarineCave_Entrance / Underwater_MarineCave OnResume setdivewarp) and the surfacing of Emerald's three new
# underwater maps (emerge connections to Routes 105, 125, 129). Their dive spots on those routes (and Route 127's) are
# sea that Emerald's abnormal weather turns into dive tiles for a day (data/scripts/abnormal_weather.inc): not here
# (Phase 4, notes/EMERALD.md).
LINKS_EMERALD = [
    ('MarineCave_Entrance', 'dive', 'Underwater_MarineCave', (9, 6)),
    ('Underwater_MarineCave', 'surface', 'MarineCave_Entrance', (10, 17)),
    ('Underwater_Route105', 'surface', 'Route105', None), ('Underwater_Route125', 'surface', 'Route125', None),
    ('Underwater_Route129', 'surface', 'Route129', None),
]
# (emerald_ch12_13 2026-10-12) The Marine Cave spots of Emerald's abnormal weather (pokeemerald data/scripts/
# abnormal_weather.inc AbnormalWeather_EventScript_PlaceTilesRoute105North ... 129East, spots 9-16 of
# include/constants/weather.h): 12 tiles each that the weather turns into rough (diveable) water; the route's "dive"
# connection takes you to the same tile of its underwater map, where Emerald's doors lead into the Marine Cave. Their
# records carry the spot in flags bits 8-15 and the lookup accepts them only while VAR_ABNORMAL_WEATHER_LOCATION is
# that spot (make_code, Emerald). The look of the rough water: data/emerald/hoenn_world.json alt_layouts RouteNNN_AWk.
AW_SPOTS = {9: ('Route105', 10, 28), 10: ('Route105', 20, 53), 11: ('Route125', 8, 16), 12: ('Route125', 53, 18),
            13: ('Route127', 57, 9), 14: ('Route127', 61, 30), 15: ('Route129', 16, 14), 16: ('Route129', 42, 19)}
AW_SHAPE = [(0, 0), (1, 0), (-1, 1), (0, 1), (1, 1), (2, 1), (-1, 2), (0, 2), (1, 2), (2, 2), (0, 3), (1, 3)]   # from the top-left tile
AW_DEST = {'Route105': 'Underwater_Route105', 'Route125': 'Underwater_Route125', 'Route127': 'Underwater3',
           'Route129': 'Underwater_Route129'}
LINKS_EMERALD += [(m, f'aw{k}', AW_DEST[m], None) for k, (m, _, _) in sorted(AW_SPOTS.items())]

def _version():
    import version
    return version

def _work_ids():
    import re
    h = open(os.path.join(ROOT, 'src', 'include', 'hoenn.h')).read()
    ids = [int(re.search(rf'#define\s+{n}\s+(0x[0-9A-Fa-f]+)', h).group(1), 16)
           for n in ('VAR_HOENN_DIVE_X', 'VAR_HOENN_DIVE_Z', 'VAR_HOENN_DIVE_ZONE')]
    assert ids[1] == ids[0] + 1 and ids[2] == ids[0] + 2, 'the dive works must be consecutive (hoenn.h)'
    return ids

def _aw_work():
    """(Emerald) VAR_ABNORMAL_WEATHER_LOCATION (hoenn.h): the Marine Cave spots' records read it."""
    import re
    return int(re.search(r'#define\s+VAR_ABNORMAL_WEATHER_LOCATION\s+(0x[0-9A-Fa-f]+)',
                         open(os.path.join(ROOT, 'src', 'include', 'hoenn.h')).read()).group(1), 16)

# ------------------------------------------------------------------------------------------------ Sapphire data
_grids = {}
def sapphire(name):
    """(walk, beh) grids [y][x] of a pokeruby map."""
    if name not in _grids:
        from gba import Repo, MetatileRenderer
        # (an Emerald build: Emerald's maps, as its world reads them: converter/gba.py Repo(..., emerald=True))
        repo = Repo(os.path.join(ROOT, 'external', 'pokeruby'), emerald=_version().is_emerald())
        mj = repo.map_json(name)
        g, l = repo.layout_grid(mj['layout'])
        mr = MetatileRenderer(repo, l['primary_tileset'], l['secondary_tileset'])
        H, W = g.shape
        _grids[name] = ([[(int(g[y, x]) >> 10) & 3 == 0 for x in range(W)] for y in range(H)],
                        [[mr.behavior(int(g[y, x]) & 0x3FF) for x in range(W)] for y in range(H)], mj)
    return _grids[name]

def links():
    """LINKS, checked against Sapphire's connections and setdivewarp scripts."""
    import re
    if _version().is_emerald():      # (Emerald's own links, checked against pokeemerald's connections and scripts)
        em = os.path.join(ROOT, 'external', 'pokeemerald', 'data', 'maps')
        for src, kind, dst, fixed in LINKS_EMERALD:
            _, _, mj = sapphire(src)
            if fixed is None:
                conn = {c['direction']: c['map'] for c in mj.get('connections') or []}
                assert conn.get('dive' if kind.startswith('aw') else 'emerge') == mj_id(dst), (src, kind, dst, conn)
            else:
                scr = open(os.path.join(em, mj.get('_emerald', src), 'scripts.inc')).read()
                assert re.search(rf'setdivewarp\s+MAP_\w+, {fixed[0]}, {fixed[1]}\b', scr), (src, dst, fixed)
        return LINKS + LINKS_EMERALD
    for src, kind, dst, fixed in LINKS:
        _, _, mj = sapphire(src)
        conn = {c['direction']: c['map'] for c in mj.get('connections') or []}
        want = 'dive' if kind == 'dive' else 'emerge'
        if fixed is None:
            assert conn.get(want) == mj_id(dst), (src, kind, dst, conn)
        else:
            scr = open(os.path.join(ROOT, 'external', 'pokeruby', 'data', 'maps', src, 'scripts.inc')).read()
            assert f'setdivewarp {mj_id(dst)}, 255, {fixed[0]}, {fixed[1]}' in scr, (src, dst, fixed)
    return LINKS

def mj_id(name):
    return sapphire(name)[2]['id']

def tiles(src, kind):
    walk, beh, _ = sapphire(src)
    H, W = len(walk), len(walk[0])
    if kind.startswith('surface@'):
        x, y = map(int, kind[8:].split(',')); return [(x, y)]
    if kind.startswith('aw'):                    # (Emerald) the rough water of abnormal-weather spot k (AW_SPOTS)
        _, x0, y0 = AW_SPOTS[int(kind[2:])]; return [(x0 + dx, y0 + dy) for dx, dy in AW_SHAPE]
    if kind == 'dive':
        return [(x, y) for y in range(H) for x in range(W) if beh[y][x] in DIVE]
    return [(x, y) for y in range(H) for x in range(W) if walk[y][x] and beh[y][x] not in NO_SURFACE]

# ------------------------------------------------------------------------------------------------ Black 2 frames
def frames():
    """Sapphire map -> (origin (zone tile of Sapphire (0, 0)), zone_of(x, z)) for every map a link names that this
    build has: the main matrix (world.json cells, data/hoenn_world.json's layout rules as b2tools/world.py compose()),
    a standalone group (its origins and cells), a room or cave (its room.json origin, its zone)."""
    wd = os.environ.get('HOENN_WORLD_DIR') or os.path.join(ROOT, 'work', 'world')
    world = json.load(open(os.path.join(wd, 'world.json')))
    lj = _version().load_json        # (Emerald: its overlays, data/emerald/; Sapphire and Ruby read the shared files)
    cfg = lj(os.path.join(ROOT, 'data', 'hoenn_world.json'))
    lay = json.load(open(os.path.join(ROOT, 'data', 'hoenn_world_layout.json')))['main']['maps']
    zones = lj(os.path.join(ROOT, 'data', 'hoenn_zones.json'))['maps']
    rooms = {n: r for n, r in lj(os.path.join(ROOT, 'data', 'hoenn_interiors.json'))['rooms'].items() if 'zone' in r}
    rd = os.environ.get('HOENN_INTERIORS_DIR') or os.path.join(ROOT, 'work', 'interiors')
    M = cfg['margin_cells'] * 32
    main_cells = {(c['cx'], c['cz']): c['zone'] for c in world['cells']}
    sys.path.insert(0, os.path.join(ROOT, 'b2tools'))
    import world as W
    out = {}
    names = {n for l in links() for n in (l[0], l[2])}
    for name in names:
        if name in rooms:
            p = os.path.join(rd, name, 'room.json')
            if os.path.exists(p):
                z = rooms[name]['zone']
                out[name] = (tuple(json.load(open(p))['origin']), lambda x, y, z=z: z)
            continue
        g = next((g for g in world.get('standalone', []) if name in g.get('origins', {})), None)
        if g:
            cells = {(c['cx'], c['cz']): c['zone'] for c in g['cells']}
            out[name] = (tuple(g['origins'][name]), lambda x, y, cells=cells: cells.get((x // 32, y // 32)))
        elif name in lay and name in zones:
            sx, sz = cfg.get('shift', {}).get(name, [0, 0]); pad = cfg.get('pad_north', {}).get(name, 0)
            L = lay[name]
            # the zone the game sees there: world.json zone_rects first (sub-cell zones: Route 124's tiles in Mossdeep's
            # cells are Route 124's zone 157), then the cell's (b2tools/world.py zone_of; story_fixups 2026-10-07)
            out[name] = ((L['tile_x'] + M + sx, L['tile_z'] + M + sz + pad),
                         lambda x, y: W.zone_of(main_cells, x, y, world.get('zone_rects', [])))
    return out

# ------------------------------------------------------------------------------------------------ the table
def table():
    """(file bytes, report lines, records): the dive table file (format in the docstring)."""
    fr = frames()
    groups, report = {}, []
    for src, kind, dst, fixed in links():
        if src not in fr or dst not in fr:
            report.append(f'{src} -> {dst}: {"not built: " + ", ".join(n for n in (src, dst) if n not in fr)}'); continue
        (sox, soz), szone = fr[src]
        (dox, doz), dzone = fr[dst]
        n = 0
        for x, y in tiles(src, kind):
            gx, gz = sox + x, soz + y
            zs = szone(gx, gz)
            if fixed is None: tx, tz, flags = dox + x, doz + y, 0
            else: tx, tz, flags = dox + fixed[0], doz + fixed[1], 1
            if kind.startswith('aw'): flags |= int(kind[2:]) << 8      # (Emerald: only while the weather is there)
            zd = dzone(tx, tz)
            if zs is None or zd is None: continue
            key = (zs, zd, flags, (tx - gx, tz - gz) if not flags & 1 else (tx, tz), src, dst)
            if (gx, gz) in {t for k, ts in groups.items() if k[0] == zs for t in ts}: continue   # first link wins
            groups.setdefault(key, []).append((gx, gz)); n += 1
        report.append(f'{src} {kind} -> {dst}{" " + str(fixed) if fixed else " (same tile)"}: {n} tiles')
    recs = []
    for (zs, zd, flags, (ax, az), src, dst), ts in groups.items():
        xs = [t[0] for t in ts]; zs_ = [t[1] for t in ts]
        x0, z0, x1, z1 = min(xs), min(zs_), max(xs), max(zs_)
        w, h = x1 - x0 + 1, z1 - z0 + 1
        assert w < 256 and h < 256, (src, w, h)
        st = set(ts)
        bm = bytes(1 if (x0 + i, z0 + j) in st else 0 for j in range(h) for i in range(w))   # (every record has one)
        recs.append(dict(zone=zs, x0=x0, z0=z0, w=w, h=h, dest=zd, ax=ax, az=az, flags=flags, map=bm, tiles=len(ts),
                         what=f'{src} -> {dst}'))
    # order: by zone, the links' order inside a zone (a "surface@" spot before its map's general surfacing)
    recs.sort(key=lambda r: r['zone'])
    head = bytearray(2 * ZONES)
    body, maps = bytearray(), bytearray()
    start = (2 * ZONES + 15) // 16 * 16
    by_zone = {}
    for r in recs: by_zone.setdefault(r['zone'], []).append(r)
    n_rec = len(recs)
    map_base = start + 16 * n_rec
    for z, rs in sorted(by_zone.items()):
        assert len(rs) <= 15, f'zone {z}: {len(rs)} dive records (max 15)'
        off = start + len(body)
        assert off % 16 == 0 and off // 16 < 4096
        struct.pack_into('<H', head, 2 * z, (off // 16) << 4 | len(rs))
        for r in rs:
            mo = map_base + len(maps); maps += r['map']
            assert mo + len(r['map']) <= 0x10000, 'dive table over 64 KB'
            body += struct.pack('<HHBBHhhHH', r['x0'], r['z0'], r['w'], r['h'], r['dest'], r['ax'], r['az'], mo, r['flags'])
    data = bytes(head) + bytes(start - len(head)) + bytes(body) + bytes(maps)
    return data, report, recs

# ------------------------------------------------------------------------------------------------ code
class T(_es.Thumb):
    def ldrsh_rr(self, rd, rn, rm): self.h(0x5E00 | rm << 6 | rn << 3 | rd)
    def ldr_rr(self, rd, rn, rm): self.h(0x5800 | rm << 6 | rn << 3 | rd)
    def strh_off(self, rd, rn, off): assert off % 2 == 0 and off < 64; self.h(0x8000 | off >> 1 << 6 | rn << 3 | rd)
    def str_off(self, rd, rn, off): assert off % 4 == 0 and off < 128; self.h(0x6000 | off >> 2 << 6 | rn << 3 | rd)
    def subsr(self, rd, rn, rm): self.h(0x1A00 | rm << 6 | rn << 3 | rd)
    def add_sp(self, rd, off): assert off % 4 == 0 and off < 1024; self.h(0xA800 | rd << 8 | off >> 2)
    def sp_sub(self, n): assert n % 4 == 0 and n < 512; self.h(0xB080 | n >> 2)
    def sp_add(self, n): assert n % 4 == 0 and n < 512; self.h(0xB000 | n >> 2)
    def bhs(self, name): self.bcc('hs', name)
    def b_abs(self, name): self.b(name)

FRAME = 260          # [0] 5th argument, [4] arc, [8] gameData, [12] count, [16] byte buffer, [20..259] 15 records

def make_code(file_id, work0, aw_work=None):
    """(lookup @ LOOKUP, hit tail @ HELPER, read helper @ READ, spawn hook @ HOOK) bytes. aw_work (Emerald):
    VAR_ABNORMAL_WEATHER_LOCATION, which records with flags bits 8-15 set must equal (else no dive)."""
    # u32 DiveLookup(Field *field, u16 *zone): r4 = grid x, r7 = grid z, r6 = zone out, r5 = record
    t = T(LOOKUP[0])
    t.at('RD', READ[0]); t.at('HIT', HELPER[0])
    t.push([4, 5, 6, 7]); t.sp_sub(FRAME)
    t.mov(6, 1); t.mov(4, 0)
    t.bl(Field_GetPlayerStateZoneID)
    t.mov(5, 0)                                                      # (*zone is only read after TRUE: callers)
    t.ldr_off(0, 4, 4); t.ldr_off(0, 0, 28); t.str_sp(0, 8)          # field->gsys->gameData
    t.bl(GameData_GetEventData)
    t.ldr_off(0, 0, 4); t.str_sp(0, 4)                               # eventData->entityArc
    t.mov(0, 4); t.bl(Field_GetPlayer); t.bl(FieldPlayer_GetActor)
    t.ldrh_off(4, 0, 60); t.adds(0, 0, 4); t.ldrh_off(7, 0, 60)      # grid x (actor +60), z (+64): never negative
    t.lsls(2, 5, 1); t.movs(3, 2); t.add_sp(0, 12); t.bl_label('RD') # zone table entry
    t.mov(5, 0); t.beq('fail')
    t.lsls(3, 5, 28); t.lsrs(3, 3, 24)                               # size = count * 16
    t.lsrs(0, 3, 4); t.str_sp(0, 12)                                 # count
    t.lsrs(2, 5, 4); t.lsls(2, 2, 4)                                 # offset
    t.add_sp(0, 20); t.bl_label('RD')
    t.add_sp(5, 20)
    t.label('loop')
    t.ldrh_off(0, 5, 0); t.subsr(0, 4, 0)                            # u = x - x0
    t.ldrb_off(1, 5, 4); t.cmpr(0, 1); t.bhs('next')                 # u >= w (or x < x0)
    t.ldrh_off(2, 5, 2); t.subsr(2, 7, 2)                            # v = z - z0
    t.ldrb_off(3, 5, 5); t.cmpr(2, 3); t.bhs('next')
    t.ldrh_off(3, 5, 12)                                             # every record has a tile map
    t.muls(2, 1); t.addsr(2, 2, 0); t.addsr(2, 2, 3)                 # map + v * w + u
    t.movs(3, 1); t.add_sp(0, 16); t.bl_label('RD')
    t.lsls(0, 0, 24); t.bne('hit')                                   # the tile's byte
    t.label('next')
    t.addi(5, 16)
    t.ldr_sp(0, 12); t.subi(0, 1); t.str_sp(0, 12); t.bne('loop')
    t.label('fail')
    t.movs(0, 0)
    t.sp_add(FRAME); t.pop([4, 5, 6, 7])
    t.label('hit')
    t.bl_label('HIT')                                                # (does not return here)
    lookup = t.assemble()
    assert len(lookup) <= LOOKUP[1] - LOOKUP[0], f'lookup {len(lookup)} B > {LOOKUP[1] - LOOKUP[0]}'
    # HIT (lookup's frame and registers): *zone = dest, the works = the other side's tile and zone, return TRUE
    h = T(HELPER[0])
    if aw_work is None:              # (Sapphire, Ruby: unchanged)
        h.ldrh_off(0, 5, 6); h.strh_off(0, 6, 0)
        h.ldrh_off(2, 5, 8); h.ldrh_off(3, 5, 10)
        h.ldrh_off(1, 5, 14); h.cmp(1, 0); h.bne('abs')
        h.addsr(2, 2, 4); h.addsr(3, 3, 7)                           # relative: x + ax, z + az
        h.label('abs')
        h.ldr_sp(1, 8); h.movs(5, GAMEDATA_EVENTWORK // 4); h.lsls(5, 5, 2); h.ldr_rr(1, 1, 5)
        h.ldr_lit(5, 'work'); h.addsr(1, 1, 5)
        h.strh_off(2, 1, 0); h.strh_off(3, 1, 2); h.strh_off(0, 1, 4)    # VAR_HOENN_DIVE_X, _Z, _ZONE
        h.movs(0, 1)
        h.sp_add(FRAME); h.pop([4, 5, 6, 7])
        h.word('work', (work0 - 0x4000) * 2)
    else:                            # (Emerald, emerald_ch12_13) flags bits 8-15 = an abnormal-weather spot: the record
        diff = (aw_work - work0) * 2     # counts only while VAR_ABNORMAL_WEATHER_LOCATION is that spot (bit 0 = fixed)
        assert 0 < diff < 256, diff
        h.ldrh_off(0, 5, 6); h.strh_off(0, 6, 0)                     # *zone = dest (callers read it after TRUE only)
        h.ldrh_off(2, 5, 8); h.ldrh_off(3, 5, 10)
        h.ldrh_off(6, 5, 14); h.lsls(5, 6, 31); h.bne('abs')         # r6 = flags
        h.addsr(2, 2, 4); h.addsr(3, 3, 7)                           # relative: x + ax, z + az
        h.label('abs')
        h.ldr_sp(1, 8); h.movs(5, GAMEDATA_EVENTWORK // 4); h.lsls(5, 5, 2); h.ldr_rr(1, 1, 5)
        h.ldr_lit(5, 'work'); h.addsr(1, 1, 5)                       # r1 = &VAR_HOENN_DIVE_X
        h.lsrs(6, 6, 8); h.beq('ok')
        h.mov(5, 1); h.addi(5, diff); h.ldrh_off(5, 5, 0)           # VAR_ABNORMAL_WEATHER_LOCATION
        h.cmpr(5, 6); h.bne('no')
        h.label('ok')
        h.strh_off(2, 1, 0); h.strh_off(3, 1, 2); h.strh_off(0, 1, 4)    # VAR_HOENN_DIVE_X, _Z, _ZONE
        h.movs(0, 1); h.b('end')
        h.label('no')
        h.movs(0, 0)
        h.label('end')
        h.sp_add(FRAME); h.pop([4, 5, 6, 7])
        h.word('work', (work0 - 0x4000) * 2)
    hit = h.assemble()
    assert len(hit) <= HELPER[1] - HELPER[0], len(hit)
    # RD(dest r0, offset r2, size r3) -> r0 = the u16 at dest: GFL_ArcToolReadRange(arc = the lookup's [sp+4], the
    # table's file, offset, size, dest)
    r = T(READ[0])
    r.push([]); r.sp_sub(4); r.str_sp(0, 0)
    r.ldr_sp(0, 12)
    r.ldr_lit(1, 'file')
    r.bl(GFL_ArcToolReadRange)
    r.ldr_sp(0, 0); r.ldrh_off(0, 0, 0)
    r.sp_add(4); r.pop([])
    r.word('file', file_id)
    read = r.assemble()
    assert len(read) <= READ[1] - READ[0], len(read)
    # spawn hook (r0 = &wk->spawn, r1 = zone): LoadZoneSpawnInfoCheckRail, then x/z = the works' tile centre
    k = T(HOOK[0])
    k.push([4]); k.mov(4, 0)
    k.bl(LoadZoneSpawnInfoCheckRail)
    k.mov(0, 4); k.subi(0, 12); k.ldr_off(0, 0, 0)                   # wk->gameData (spawn is wk + 16)
    k.movs(1, GAMEDATA_EVENTWORK // 4); k.lsls(1, 1, 2); k.ldr_rr(0, 0, 1)
    k.ldr_lit(1, 'work'); k.addsr(0, 0, 1)
    k.ldrh_off(1, 0, 0); k.ldrh_off(2, 0, 2)
    k.lsls(1, 1, 16); k.lsls(2, 2, 16)
    k.movs(3, 1); k.lsls(3, 3, 15); k.orrs(1, 3); k.orrs(2, 3)       # tile * 16 + 8 units, fx32
    k.str_off(1, 4, 16); k.str_off(2, 4, 24)                         # spawn.pos.x, .z (y: the zone's spawn)
    k.pop([4])
    k.word('work', (work0 - 0x4000) * 2)
    hook = k.assemble()
    assert len(hook) <= HOOK[1] - HOOK[0], len(hook)
    return lookup, hit, read, hook

# ------------------------------------------------------------------------------------------------ apply
_state = {}

def underwater_zones():
    rooms = json.load(open(os.path.join(ROOT, 'data', 'hoenn_interiors.json')))['rooms']
    return sorted(r['zone'] for r in rooms.values() if r['map_type'] == 'MAP_TYPE_UNDERWATER')

def apply(files):
    import narcio
    data, report, recs = table()
    import zoneheaders
    headers, _ = zoneheaders.load(files)
    fid = headers[TABLE_ZONE]['entities']
    assert sum(1 for h in headers if h['entities'] == fid) == 1, f'entity file {fid} is shared'
    ents = narcio.load(files, ENTITIES_ARC)
    _state['file'] = fid
    ents[fid] = data
    narcio.save(files, ENTITIES_ARC, ents)
    zs = sorted({r['zone'] for r in recs})
    done = f'dive table = a/1/2/6 file {_state["file"]} ({len(data)} B, {len(recs)} records in {len(zs)} zones)'
    if os.environ.get('HOENN_TEST_DIVE'):
        done += '; ' + _test_setup(files)
    return done + '; ' + '; '.join(report)

def apply_code(code_dir):
    assert 'file' in _state, 'dive: apply() runs first (build_rom.py calls apply, then apply_code)'
    vanilla = os.path.join(ROOT, 'external', 'pokebw2', 'build', 'b2_us', 'build')
    def orig(name, base, a, b): return open(os.path.join(vanilla, name), 'rb').read()[a - base:b - base]
    lookup, helper, read, hook = make_code(_state['file'], _work_ids()[0], _aw_work() if _version().is_emerald() else None)
    # ov036: the lookup over the two old functions, the helper over UpdateAbyssalRuinsSteps (its call returns 0 now)
    path, d = _load(code_dir, 'arm9_ov036.bin')
    _patch(d, OV036, LOOKUP[0], orig('arm9_ov036.bin', OV036, *LOOKUP), lookup + bytes(LOOKUP[1] - LOOKUP[0] - len(lookup)), 'dive lookup')
    _patch(d, OV036, HELPER[0], orig('arm9_ov036.bin', OV036, *HELPER), helper + bytes(HELPER[1] - HELPER[0] - len(helper)), 'dive hit tail')
    _patch(d, OV036, READ[0], orig('arm9_ov036.bin', OV036, *READ), read + bytes(READ[1] - READ[0] - len(read)), 'dive read helper')
    _patch(d, OV036, STEPS_CALL, _bl(STEPS_CALL, HELPER[0]), bytes.fromhex('0020c046'), 'CheckPerStepEvents: no Abyssal Ruins steps')
    for name, (base, at) in LOOKUP_CALLS.items():
        if name != 'arm9_ov036.bin': continue
        _patch(d, base, at, _bl(at, OLD_LOOKUP), _bl(at, LOOKUP[0]), f'{name} dive check call')
    _save(path, d)
    # ov012 (party menu's CalcPlayerActionPossibilities) and ov033 (EventDiveIn_Callback): the lookup's new address;
    # ov012: the Abyssal Ruins script plugin's zones -> the underwater zones (on the Black Tower's list)
    path, d = _load(code_dir, 'arm9_ov012.bin')
    base, at = LOOKUP_CALLS['arm9_ov012.bin']
    _patch(d, base, at, _bl(at, OLD_LOOKUP), _bl(at, LOOKUP[0]), 'party menu dive check call')
    uz = underwater_zones()
    assert len(uz) <= len(BLACK_TOWER_LIST), uz
    _patch(d, OV012, BLACK_TOWER_ZONES, struct.pack(f'<{len(BLACK_TOWER_LIST)}H', *BLACK_TOWER_LIST),
           struct.pack(f'<{len(BLACK_TOWER_LIST)}H', *(uz + [0xFFFF] * (len(BLACK_TOWER_LIST) - len(uz)))), 'underwater zones')
    abyss = struct.pack('<IIIii', 0x021E5868, ABYSS_ZONES, len(ABYSS_LIST), 54, -1)
    _patch(d, OV012, PLUGIN_ABYSS_ENTRY, abyss, struct.pack('<IIIii', 0x021E5868, BLACK_TOWER_ZONES, len(uz), 54, -1),
           'Abyssal Ruins plugin -> the underwater zones')
    bt = PLUGIN_ABYSS_ENTRY + 4 * 20                                  # entry 9 = entry 5 + 4 entries of 20 bytes
    _patch(d, OV012, bt + 4, struct.pack('<II', BLACK_TOWER_ZONES, len(BLACK_TOWER_LIST)),
           struct.pack('<II', BLACK_TOWER_ZONES, 0), 'Black Tower plugin: no zones')
    _save(path, d)
    path, d = _load(code_dir, 'arm9_ov033.bin')
    base, at = LOOKUP_CALLS['arm9_ov033.bin']
    _patch(d, base, at, _bl(at, OLD_LOOKUP), _bl(at, LOOKUP[0]), 'EventDiveIn dive check call')
    _patch(d, OV033, HOOK[0], orig('arm9_ov033.bin', OV033, *HOOK), hook + bytes(HOOK[1] - HOOK[0] - len(hook)), 'dive spawn hook')
    # EventDiveIn_Callback state 3: Black 2 walks the arrived diver one tile up (actor command 8, walk_slow_up: the
    # Abyssal Ruins' descent swims on); Sapphire puts you on the tile below the dive spot: command 0 (face up)
    _patch(d, OV033, DIVE_ARRIVAL_ACMD, bytes.fromhex('0821'), bytes.fromhex('0021'), 'dive arrival: no step')
    _save(path, d)
    # ov035: EventMapChangeDiveIn_Create's spawn
    path, d = _load(code_dir, 'arm9_ov035.bin')
    _patch(d, OV035, SPAWN_CALL, _bl(SPAWN_CALL, LoadZoneSpawnInfoCheckRail), _bl(SPAWN_CALL, HOOK[0]), 'dive arrival')
    _save(path, d)
    return (f'dive lookup {len(lookup)}/{LOOKUP[1] - LOOKUP[0]} B at {LOOKUP[0]:#x}, hit tail {len(helper)} B at '
            f'{HELPER[0]:#x}, read helper {len(read)} B at {READ[0]:#x}, spawn hook {len(hook)} B at {HOOK[0]:#x}; '
            f'plugin 5 zones {uz}')

# ------------------------------------------------------------------------------------------------ test setup
def _test_setup(files):
    """HOENN_TEST_DIVE=1: a Littleroot map-load script gives a Lv 50 Mudkip knowing Surf and Dive, HM06/HM03 and all
    8 badges once (party empty). Littleroot's script file (778) gets one more script and its init table a MapScript."""
    return 'TEST: see dive_build.sh (scripts patch HOENN_TEST_PARTY + test_cave_kit)'
