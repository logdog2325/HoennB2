"""Hoenn town map (town_map agent, 2026-10-08; notes/TOWN_MAP.md): Black 2's town map app (FIELD_APP 8, overlay 144)
shows Sapphire's region map instead of Unova, for the Town Map key item, Fly (party menu and the Town Map) and the
Pokémon Centers' wall maps (CallPlaceSelect, view mode below).

Black 2's town map [code: ov144 disassembly (dsd), notes/TOWN_MAP.md]:
  - art: a/0/8/4 (ARC 84). Bottom screen BG3 = the painted map (8bpp extended-affine, NCGR 7 + NSCR 16, palette 0 of the
    extended palette NCLR 0), BG2 = the route/town/landmark overlay (NCGR 5 + NSCR 17); sprites (NCGR 8, NCER 12, NANR 19,
    NCLR 2) draw the cursor, the player and the location icons. The map is shown at 1:1 (256x168 visible) and zoomed 2x by
    scaling the affine BGs.
  - locations: a/0/8/5 file 0, 85 records x 54 bytes (27 u16): zone, snap radius, icon x/y, snap x/y, capsule (hit area)
    end points x/y x 2, capsule radius, type (0 town, 1 route, 2 landmark, 3/4/5 special icons), can fly, 2 zero words,
    fly/visited flag, show flag (0xffff = always), 7 lines of system text 377 (description, facilities), 3 unused words.
    Names are the zone header's place name (system text 109).

This patch:
  - art: Sapphire's region map (pokeruby graphics/pokenav/region_map.png + region_map_map.bin, its own palette) at 1:1:
    its 32x20-tile picture is exactly the DS screen's width; placed 2 tiles down (Y0) in BG3, the sea tile around it;
    BG2 left empty (Sapphire's picture has its own routes and towns). Same NCGR/NSCR/NCLR file sizes.
  - locations: a new file a/0/8/4 #21 (the NARC is padded back to its original size: same ROM layout) = the records
    (Sapphire's region map sections: towns, routes (one record per straight run of their layout cells), landmarks), then
    a zone -> record table (every zone header of the build: Sapphire's map section of the zone's pokeruby/pokeemerald map,
    else the zone's place name), then the refine table (Sapphire's GetPositionOfCursorWithinMapSection for routes).
  - code (ov144, inside its own size): the records come from the new file; the player's location is found through the
    zone table (Black 2: zone parent == record zone); the player's cell inside a multi-cell route as Sapphire computes it;
    the entry count; a scripted call (CallPlaceSelect) in a zone where Fly is off (the Centers' wall maps) opens the map
    in view mode (Black 2's mode 1) instead of "Fly to where?".
"""
import json, os, re, struct, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'b2tools'))

ARC_GFX, NEW_FILE = 84, 21
Y0 = 2                                    # Sapphire's picture row 0 -> BG3 tile row Y0
RUBY = os.path.join(ROOT, 'external', 'pokeruby')
EMERALD = os.path.join(ROOT, 'external', 'pokeemerald')
FIRERED = os.path.join(ROOT, 'external', 'pokefirered')
REC = 54
OV144 = 0x0219CE80

# ---------------------------------------------------------------------------------------------------- the art

def sapphire_map():
    """(tiles: [64-byte 8bpp tiles], picture: 20 rows x 32 tile indices, palette: 256 RGB) of Sapphire's region map
    (region_map.png: 16x15 tiles of 8bpp; region_map_map.bin: the 64x64 affine map, 1 byte per tile)."""
    from PIL import Image
    g = os.path.join(RUBY, 'graphics', 'pokenav')
    im = Image.open(os.path.join(g, 'region_map.png'))
    w = im.width // 8
    px = im.tobytes()
    tiles = [bytes(px[(t // w * 8 + y) * im.width + t % w * 8 + x] for y in range(8) for x in range(8))
             for t in range(w * (im.height // 8))]
    m = open(os.path.join(g, 'region_map_map.bin'), 'rb').read()
    pic = [[m[r * 64 + c] for c in range(32)] for r in range(20)]
    assert all(m[r * 64 + c] == 0 for r in range(64) for c in range(64) if r >= 20 or c >= 32), 'map outside 32x20'
    pal = im.getpalette()
    return tiles, pic, [tuple(pal[3 * i:3 * i + 3]) for i in range(256)]

def bg3_screen():
    """(tiles, 32x32 screen of tile indices) of the new BG3: Sapphire's picture at rows Y0..Y0+19, sea elsewhere."""
    tiles, pic, pal = sapphire_map()
    sea = 0
    assert not any(t not in (113, 114) for t in tiles[sea]), 'tile 0 is not the sea'
    used, out = {}, []
    scr = [[sea] * 32 for _ in range(32)]
    for r in range(20):
        scr[Y0 + r] = list(pic[r])
    for row in scr:
        for t in row:
            if t not in used: used[t] = len(out); out.append(tiles[t])
    return out, [[used[t] for t in row] for row in scr], pal

# Black 2's landmark marker on BG2 (a/0/8/4 NCGR 5 + NSCR 17, e.g. at (4..9, 27..34)): 6x6 green square (palette 0
# indices 199 edge, 200 corners, 201 inside) over a 6x2 shadow (205); Sapphire's colours use indices 113-140 only.
LANDMARK_STAMP = [[200, 199, 199, 199, 199, 200]] + [[199, 201, 201, 201, 201, 199]] * 4 + \
                 [[200, 199, 199, 199, 199, 200], [205] * 6, [205] * 6]

def bg2_screen(entries, locs):
    """(tiles, 32x32 entries) of BG2: blank, with Black 2's landmark square (LANDMARK_STAMP, Black 2's own pixels read
    from its BG2) centred on every always-shown landmark's icon point (Black 2 draws its landmarks the same way;
    the ones with a show flag are sprites instead, type 4)."""
    import title_art as ta
    w, h, _, ents = ta.nscr_entries(entries[17]); _, tl = ta.ncgr_tiles(entries[5])
    old = ta.render_screen(tl + [bytes(64)] * 1024, ents, 256, 256, 8)
    assert [old[y * 256 + 4:y * 256 + 10] for y in range(27, 35)] == [bytes(r) for r in LANDMARK_STAMP], \
        'Black 2 landmark square not where expected'
    pix = bytearray(256 * 256)
    for l in locs:
        if l['type'] != TYPE_LANDMARK_BG: continue
        x0, y0 = l['icon'][0] - 3, l['icon'][1] - 3
        for dy, row in enumerate(LANDMARK_STAMP):
            for dx, v in enumerate(row):
                if 0 <= x0 + dx < 256 and 0 <= y0 + dy < 256: pix[(y0 + dy) * 256 + x0 + dx] = v
    ts = ta.TileSet()
    scr = ta.screen_from_image(ts, pix, 256, 256)
    return ts.tiles, scr

# Town icons: Sapphire's fly-target icons (graphics/pokenav/fly_target_icons.png, region_map.c
# CreateCityTownFlyTargetIcons: pink = visited, grey = not yet, in the town's shape: dot 1x1, capsule 2x1 / 1x2) as 6 new
# cells (25-30 of NCER 12, one OBJ each, on new 128-byte units of NCGR 8) and 6 new one-frame anims (19-24 of NANR 19),
# appended: Black 2's own cells/anims stay as they are (the Pokédex's area page, ov298, draws with them too). Colours:
# OBJ palette 4 of NCLR 2, whose indices 2-5 and 9-12 no Black 2 cell uses (Sapphire's icon colours 4, 7-12, 15).
# (Sapphire frame tiles, OBJ (w, h), offset from the icon point = the section's centre, what)
ICONS = [([0], (16, 16), (-8, -8), 'dot visited'), ([5], (16, 16), (-8, -8), 'dot not visited'),
         ([1, 2], (16, 8), (-8, -4), 'capsule 2x1 visited'), ([6, 7], (16, 8), (-8, -4), 'capsule 2x1 not visited'),
         ([3, 4], (8, 16), (-4, -8), 'capsule 1x2 visited'), ([8, 9], (8, 16), (-4, -8), 'capsule 1x2 not visited')]
ICON_ANIM0 = 19                                                  # first new anim (Black 2's NANR 19 has 0-18)
ICON_ANIMS = {(1, 1): (19, 20), (2, 1): (21, 22), (1, 2): (23, 24)}   # section (w, h) -> (visited, not visited) anim
ICON_PAL = 4
ICON_INDEX = {4: 2, 7: 3, 8: 4, 9: 5, 10: 9, 11: 10, 12: 11, 15: 12}  # Sapphire icon colour -> palette 4 slot

def _sections_of(d):
    """[(magic, start, size)] of a Nitro file's sections."""
    hsize, nsec = struct.unpack_from('<HH', d, 0xC)
    out, off = [], hsize
    for _ in range(nsec):
        m, sz = struct.unpack_from('<4sI', d, off); out.append((m, off, sz)); off += sz
    return out

def _nitro(d, sections):
    """Rebuild a Nitro file from its header and new section blobs (each with its own 8-byte header)."""
    body = b''.join(sections)
    return d[:8] + struct.pack('<IHH', 0x10 + len(body), 0x10, len(sections)) + body

def sprite_entries(entries):
    """New a/0/8/4 entries 2 (OBJ palettes), 8 (OBJ tiles), 12 (cells), 19 (anims) with Sapphire's town icons."""
    import title_art as ta
    from PIL import Image
    im = Image.open(os.path.join(RUBY, 'graphics', 'pokenav', 'fly_target_icons.png'))
    px = im.tobytes(); W = im.width; pal = im.getpalette()
    def stile(k):                                   # Sapphire's 8x8 tile k (1D: tile k at ((k % 2) * 8, (k // 2) * 8))
        x0, y0 = k % 2 * 8, k // 2 * 8
        return [[px[(y0 + y) * W + x0 + x] for x in range(8)] for y in range(8)]
    # tiles: one new 128-byte unit (4 tiles) per icon after Black 2's (1D 128K mapping: cells count 128-byte units)
    ncgr = bytearray(entries[8])
    th, tw, depth, mapping, tiled, size, off = struct.unpack_from('<HHIIIII', ncgr, 0x18)
    assert depth == 3 and size % 128 == 0 and (th, tw) == (0xFFFF, 0xFFFF)
    unit0 = size // 128
    raw = bytearray()
    for frame, (w, h), _, what in ICONS:
        fw, fh = {1: (8, 8), 2: (16, 8) if frame[0] in (1, 6) else (8, 16)}[len(frame)]
        canvas = [[0] * w for _ in range(h)]
        dx, dy = (w - fw) // 2, (h - fh) // 2
        for k, ft in enumerate(frame):
            tx, ty = (k, 0) if fw == 16 else (0, k)
            for y, row in enumerate(stile(ft)):
                for x, v in enumerate(row):
                    if v:
                        assert v in ICON_INDEX, (what, v)
                        canvas[dy + ty * 8 + y][dx + tx * 8 + x] = ICON_INDEX[v]
        unit = bytearray(128)
        k = 0
        for ty in range(h // 8):
            for tx in range(w // 8):
                t = [canvas[ty * 8 + y][tx * 8 + x] for y in range(8) for x in range(8)]
                unit[32 * k:32 * k + 32] = bytes(t[i] | t[i + 1] << 4 for i in range(0, 64, 2)); k += 1
        raw += unit
    secs = _sections_of(bytes(ncgr))                 # RAHC: 8-byte header, u16 h, u16 w, u32 depth, mapping, tiled,
    m, ro, rsz = secs[0]                             # u32 data size (+0x18), u32 data offset (0x18, from +8)
    assert m == b'RAHC' and ro == 0x10 and off == 0x18 and rsz == 0x20 + size, (m, ro, rsz, size)
    rahc_new = bytearray(ncgr[ro:ro + rsz]) + raw
    struct.pack_into('<I', rahc_new, 4, rsz + len(raw)); struct.pack_into('<I', rahc_new, 0x18, size + len(raw))
    ncgr_new = _nitro(bytes(ncgr), [bytes(rahc_new)] + [bytes(ncgr[o:o + sz]) for _, o, sz in secs[1:]])
    # cells: KBEC = header (u16 cells, u16 attr, u32 table offset 0x18, ...), 16-byte cell entries, then 6-byte OAMs
    ncer = entries[12]
    secs = _sections_of(ncer)
    m, ko, ksz = secs[0]; assert m == b'KBEC'
    kb = ncer[ko:ko + ksz]
    n, attr, co = struct.unpack_from('<HHI', kb, 8)
    assert attr & 1 and co == 0x18
    table = bytearray(kb[8 + co:8 + co + 16 * n]); oams = bytearray(kb[8 + co + 16 * n:])
    oam_len = max(struct.unpack_from('<I', table, 16 * i + 4)[0] + 6 * struct.unpack_from('<H', table, 16 * i)[0] for i in range(n))
    oams = oams[:oam_len]
    for k, (frame, (w, h), (ox, oy), what) in enumerate(ICONS):
        shape = 0 if w == h else (1 if w > h else 2); size_ = 1 if (w, h) == (16, 16) else 0
        a0 = shape << 14 | (oy & 0xFF)
        a1 = size_ << 14 | (ox & 0x1FF)
        a2 = ICON_PAL << 12 | (unit0 + k)
        table += struct.pack('<HHIhhhh', 1, struct.unpack_from('<H', table, 16 * 4 + 2)[0], len(oams), ox + w - 1, oy + h - 1, ox, oy)
        oams += struct.pack('<HHH', a0, a1, a2)
    while len(oams) % 4: oams += b'\0'
    head = bytearray(kb[8:8 + co]); struct.pack_into('<H', head, 0, n + len(ICONS))
    kb_new = struct.pack('<4sI', b'KBEC', 8 + len(head) + len(table) + len(oams)) + bytes(head) + bytes(table) + bytes(oams)
    ncer_new = _nitro(ncer, [kb_new] + [ncer[o:o + sz] for _, o, sz in secs[1:]])
    # anims: KNBA = header (u16 anims, u16 frames, u32 0x18, u32 frames at, u32 positions at), 16-byte anims,
    # 8-byte frames (u32 position offset, u16 duration, 0xbeef), positions (u16 cell, 0xcccc)
    nanr = entries[19]
    secs = _sections_of(nanr)
    m, ao, asz = secs[0]; assert m == b'KNBA'
    ab = nanr[ao:ao + asz]
    nA, nF, aoff, foff, poff = struct.unpack_from('<HHIII', ab, 8)
    assert nA + 6 <= 32 and ICON_ANIM0 == nA, nA
    anims = bytearray(ab[8 + aoff:8 + foff]); frames = bytearray(ab[8 + foff:8 + poff]); pos = bytearray(ab[8 + poff:])
    proto = ab[8 + aoff + 16:8 + aoff + 32]           # anim 1: one frame, cell 4 (u32 1, u16 0, u16 1, u32 2, u32 frame)
    for k in range(len(ICONS)):
        a = bytearray(proto); struct.pack_into('<I', a, 12, len(frames)); anims += a
        frames += struct.pack('<IHH', len(pos), 4, 0xBEEF)
        pos += struct.pack('<HH', n + k, 0xCCCC)
    head = bytearray(ab[8:8 + aoff])
    struct.pack_into('<HHIII', head, 0, nA + len(ICONS), nF + len(ICONS), aoff, aoff + len(anims), aoff + len(anims) + len(frames))
    ab_new = struct.pack('<4sI', b'KNBA', 8 + len(head) + len(anims) + len(frames) + len(pos)) + bytes(head + anims + frames + pos)
    nanr_new = _nitro(nanr, [ab_new] + [nanr[o:o + sz] for _, o, sz in secs[1:]])
    cols = ta.nclr_colours(entries[2])
    for src, dst in ICON_INDEX.items():
        cols[ICON_PAL * 16 + dst] = tuple(pal[3 * src:3 * src + 3])
    return {2: ta.nclr_build(entries[2], cols), 8: ncgr_new, 12: ncer_new, 19: nanr_new}

def art_entries(entries, locs):
    """New a/0/8/4 entries 0 (palettes), 5/17 (BG2: the landmark squares), 7/16 (BG3: Sapphire's map)."""
    import title_art as ta
    out = list(entries)
    tiles, scr, pal = bg3_screen()
    bpp, old = ta.ncgr_tiles(entries[7])
    assert bpp == 8 and len(tiles) <= len(old), (bpp, len(tiles), len(old))
    out[7] = ta.ncgr_build(tiles, 8)                # (whole rows of 32 tiles; the NARC is padded back in apply)
    w, h, mode, ents = ta.nscr_entries(entries[16])
    assert (w, h) == (256, 256)
    hdr = entries[16][:0x24]
    out[16] = hdr + struct.pack('<1024H', *[t for row in scr for t in row])
    t2, s2 = bg2_screen(entries, locs)
    assert len(t2) <= 256, len(t2)
    out[5] = ta.ncgr_build(t2, 8)
    out[17] = entries[17][:0x24] + struct.pack('<1024H', *s2)
    cols = ta.nclr_colours(entries[0])              # 16 extended palettes x 256; the map's entries use palette 0
    used = {p for t in tiles for p in t}
    for i in used: cols[i] = pal[i]
    out[0] = ta.nclr_build(entries[0], cols)
    for k, v in sprite_entries(entries).items(): out[k] = v
    return out

# ---------------------------------------------------------------------------------------------------- the locations

def _sections():
    d = json.load(open(os.path.join(RUBY, 'src', 'data', 'region_map', 'region_map_sections.json')))['map_sections']
    out = {s['id']: s for s in d}
    for s in json.load(open(os.path.join(EMERALD, 'src', 'data', 'region_map', 'region_map_sections.json')))['map_sections']:
        if s['id'] not in out and 'x' in s: out[s['id']] = s   # Emerald's Altering Cave
    return out

def _layout():
    """Sapphire's 28x15 cursor grid (region_map_layout.h): [[mapsec]] by row."""
    t = open(os.path.join(RUBY, 'src', 'data', 'region_map', 'region_map_layout.h')).read()
    ids = re.findall(r'MAPSEC_\w+', t)
    assert len(ids) == 28 * 15
    return [ids[r * 28:(r + 1) * 28] for r in range(15)]

def cell_px(cx, cy):
    """Screen pixel of the centre of Sapphire's cursor cell (cx, cy) (MAPCURSOR_X_MIN 1, Y_MIN 2; picture row + Y0)."""
    return (cx + 1) * 8 + 4, (cy + 2 + Y0) * 8 + 4

def _flags():
    t = open(os.path.join(ROOT, 'src', 'include', 'hoenn.h')).read()
    return {m.group(1): int(m.group(2), 0) for m in re.finditer(r'#define\s+((?:FLAG|VAR)_\w+)\s+(0x[0-9A-Fa-f]+|\d+)', t)}

TOWNS = ['LITTLEROOT_TOWN', 'OLDALE_TOWN', 'DEWFORD_TOWN', 'LAVARIDGE_TOWN', 'FALLARBOR_TOWN', 'VERDANTURF_TOWN',
         'PACIFIDLOG_TOWN', 'PETALBURG_CITY', 'SLATEPORT_CITY', 'MAUVILLE_CITY', 'RUSTBORO_CITY', 'FORTREE_CITY',
         'LILYCOVE_CITY', 'MOSSDEEP_CITY', 'SOOTOPOLIS_CITY', 'EVER_GRANDE_CITY']
# Landmarks: Sapphire's region map sections that are not towns/routes (cave and building positions: the player marker
# inside them; Black 2 shows its landmarks as icons). (section, show flag, icon offset from the cell centre in pixels,
# own hover cells from Sapphire's cursor grid?). Show flags: Sapphire's own rule for the two it hides (region_map.c
# sub_80FB758: Battle Tower with FLAG_LANDMARK_BATTLE_TOWER, also its Fly; Southern Island with
# FLAG_LANDMARK_SOUTHERN_ISLAND); the post-game maps of this build after the game (Sky Pillar's islet and Altering Cave's
# mouth appear with FLAG_SYS_GAME_CLEAR, notes/EVENTS.md). Not on the map, as in Emerald (sMapSecIdsOffMap): Faraway
# Island, Birth Island, Navel Rock. Mirage Island is part of Route 130 (no map of its own).
LANDMARKS = [
    ('GRANITE_CAVE', None, (-2, 2)), ('MT_CHIMNEY', None, (4, -6)), ('SAFARI_ZONE', None, (0, 0)),
    ('BATTLE_TOWER', 'FLAG_LANDMARK_BATTLE_TOWER', (0, 0)), ('PETALBURG_WOODS', None, (2, 0)),
    ('RUSTURF_TUNNEL', None, (0, -2)), ('ABANDONED_SHIP', None, (0, 2)), ('NEW_MAUVILLE', None, (2, 0)),
    ('METEOR_FALLS', None, (0, 0)), ('MT_PYRE', None, (-2, 0)), ('EVIL_TEAM_HIDEOUT', None, (4, -9)),
    ('SHOAL_CAVE', None, (0, -2)), ('SEAFLOOR_CAVERN', None, (2, 2)), ('VICTORY_ROAD', None, (-3, 2)),
    ('CAVE_OF_ORIGIN', None, (7, 5)), ('SOUTHERN_ISLAND', 'FLAG_LANDMARK_SOUTHERN_ISLAND', (0, 0)),
    ('FIERY_PATH', None, (-3, 6)), ('JAGGED_PASS', None, (9, -5)), ('SEALED_CHAMBER', None, (0, 2)),
    ('SCORCHED_SLAB', None, (2, 0)), ('ISLAND_CAVE', None, (2, 0)), ('DESERT_RUINS', None, (2, 0)),
    ('ANCIENT_TOMB', None, (-2, 0)), ('SKY_PILLAR', 'FLAG_SYS_GAME_CLEAR', (2, 0)),
    ('ALTERING_CAVE', 'FLAG_SYS_GAME_CLEAR', (2, 2))]
GRID_LANDMARKS = {'MT_CHIMNEY', 'SAFARI_ZONE', 'BATTLE_TOWER', 'SOUTHERN_ISLAND'}   # in Sapphire's cursor grid
UNDERWATER = {'UNDERWATER_124': 'ROUTE_124', 'UNDERWATER_125': 'ROUTE_126', 'UNDERWATER_126': 'ROUTE_127',
              'UNDERWATER_127': 'ROUTE_128', 'UNDERWATER_SOOTOPOLIS': 'SOOTOPOLIS_CITY', 'UNDERWATER_128': 'ROUTE_128',
              'UNDERWATER_SEALED_CHAMBER': 'ROUTE_134'}   # region_map.c sUnderwaterMaps
LINE_POKEMON_CENTER = 5            # system text 377 line 5 "Pokémon Center" (Black 2's facility line)
TYPE_TOWN, TYPE_ROUTE, TYPE_LANDMARK_BG, TYPE_LANDMARK, TYPE_TOWN_ICON = 0, 1, 2, 4, 5
# 5: always an icon (Black 2: anims 0x10/0x11 by the visited flag, 0x12 selected); here its anims come from record
# field 26 (visited | not visited << 5, the patched case 5 of func_ov144_0219e18c): Sapphire's icons.
# 2: a landmark drawn on BG2 (red square sprite when selected); 4: green square sprite, red when selected, hidden by its
# show flag. Black 2's sprite system has 32 affine matrices: icons on more than ~25 sprites at once draw as solid boxes
# (tested), so only the landmarks with a show flag are sprites.

def _map_json(name):
    for dec in (RUBY, EMERALD, FIRERED):
        p = os.path.join(dec, 'data', 'maps', name, 'map.json')
        if os.path.exists(p): return json.load(open(p))
    return None

def zone_sections():
    """{zone: MAPSEC_*} for every zone of the build's Hoenn maps (outdoor, rooms, caves) from their pokeruby /
    pokeemerald map.json."""
    out = {}
    maps = json.load(open(os.path.join(ROOT, 'data', 'hoenn_zones.json')))['maps']
    rooms = json.load(open(os.path.join(ROOT, 'data', 'hoenn_interiors.json')))['rooms']
    for name, r in list(maps.items()) + list(rooms.items()):
        j = _map_json(name)
        if j: out.setdefault(r['zone'], j['region_map_section'])
    return out

def _runs(cells):
    """Split a set of grid cells into straight runs (longest first): [(c0, c1)]."""
    left, runs = set(cells), []
    while left:
        best = None
        for (x, y) in left:
            for dx, dy in ((1, 0), (0, 1)):
                n = 0
                while (x + dx * (n + 1), y + dy * (n + 1)) in left: n += 1
                if (x - dx, y - dy) in left: continue
                if best is None or n > best[0]: best = (n, (x, y), (x + dx * n, y + dy * n))
        n, a, b = best
        runs.append((a, b))
        for k in range(n + 1):
            left.discard((a[0] + (b[0] - a[0]) * k // max(n, 1), a[1] + (b[1] - a[1]) * k // max(n, 1)))
    return runs

def locations():
    """The map's locations in record order: dicts (key, mapsec, type, zone, icon, snap, cap (x0, y0, x1, y1, r), snap_r,
    fly flag, can_fly, show flag, lines, sec (x, y, w, h)). Landmarks first (small hit areas inside towns' and routes'
    cells win), then towns, then routes (Black 2 picks the first record whose capsule holds the cursor)."""
    secs, grid, flags = _sections(), _layout(), _flags()
    zones = json.load(open(os.path.join(ROOT, 'data', 'hoenn_zones.json')))['maps']
    by_sec = {}
    for name, z in zones.items():
        by_sec.setdefault(z['mapsec'], []).append(z['zone'])
    rooms = json.load(open(os.path.join(ROOT, 'data', 'hoenn_interiors.json')))['rooms']
    zs = zone_sections()
    def main_zone(sec):
        if sec in by_sec: return min(by_sec[sec], key=lambda z: (z not in (zones.get(n, {}).get('zone') for n in zones), z))
        cand = sorted(z for z, s in zs.items() if s == sec)
        return cand[0] if cand else None
    def first_zone(sec, prefer=()):
        for n in prefer:
            if n in zones: return zones[n]['zone']
            if n in rooms: return rooms[n]['zone']
        return main_zone(sec)
    grid_cells = {}
    for y, row in enumerate(grid):
        for x, s in enumerate(row):
            grid_cells.setdefault(s, []).append((x, y))
    out = []
    def centre(s):
        return ((s['x'] + 1) * 8 + s['width'] * 4, (s['y'] + 2 + Y0) * 8 + s['height'] * 4)
    # landmarks
    prefer = {'MAPSEC_GRANITE_CAVE': ['GraniteCave_1F'], 'MAPSEC_METEOR_FALLS': ['MeteorFalls_1F_1R'],
              'MAPSEC_MT_PYRE': ['MtPyre_Exterior'], 'MAPSEC_EVIL_TEAM_HIDEOUT': ['AquaHideout_1F', 'MagmaHideout_1F'],
              'MAPSEC_SHOAL_CAVE': ['ShoalCave_LowTideEntranceRoom'], 'MAPSEC_SEAFLOOR_CAVERN': ['SeafloorCavern_Entrance'],
              'MAPSEC_VICTORY_ROAD': ['VictoryRoad_1F'], 'MAPSEC_CAVE_OF_ORIGIN': ['CaveOfOrigin_Entrance'],
              'MAPSEC_SOUTHERN_ISLAND': ['SouthernIsland_Exterior'], 'MAPSEC_SEALED_CHAMBER': ['SealedChamber_OuterRoom'],
              'MAPSEC_SKY_PILLAR': ['SkyPillar_Outside'], 'MAPSEC_SAFARI_ZONE': ['SafariZone_Southwest'],
              'MAPSEC_BATTLE_TOWER': ['BattleTower_Outside'], 'MAPSEC_ABANDONED_SHIP': ['AbandonedShip_Deck'],
              'MAPSEC_NEW_MAUVILLE': ['NewMauville_Entrance'], 'MAPSEC_MT_CHIMNEY': ['MtChimney'],
              'MAPSEC_ALTERING_CAVE': ['AlteringCave']}
    for key, show, (dx, dy) in LANDMARKS:
        sec = 'MAPSEC_' + key; s = secs[sec]
        zone = first_zone(sec, prefer.get(sec, ()))
        if zone is None: continue                          # (a map this build does not have)
        cx, cy = cell_px(s['x'], s['y'])
        icon = (cx + dx, cy + dy)
        if key in GRID_LANDMARKS:                          # Sapphire's cursor names these over their grid cells
            cells = grid_cells['MAPSEC_' + key]
            xs = [c[0] for c in cells]; ys = [c[1] for c in cells]
            a = cell_px(min(xs), min(ys)); b = cell_px(max(xs), max(ys))
            mid = ((a[0] + b[0]) // 2, (a[1] + b[1]) // 2)
            r = 4 + 4 * min(max(xs) - min(xs), max(ys) - min(ys)) + 1
            cap = (mid[0], mid[1], mid[0], mid[1], r) if len(cells) > 1 else (cx, cy, cx, cy, 5)
            snap = mid if len(cells) > 1 else (cx, cy)
        else:
            cap = (icon[0], icon[1], icon[0], icon[1], 3); snap = icon
        fly = key == 'BATTLE_TOWER'
        out.append(dict(key=key, mapsec=sec, type=TYPE_LANDMARK if show else TYPE_LANDMARK_BG, zone=zone, icon=icon, snap=snap, cap=cap,
                        snap_r=4, fly_flag=flags[show] if fly else 0xFFFF, can_fly=int(fly),
                        show=flags[show] if show else 0xFFFF, lines=[], sec=(s['x'], s['y'], s['width'], s['height'])))
    # towns: flyable after FLAG_VISITED_<town> (region_map.c sub_80FB758, Sapphire's own flags, set by the towns'
    # OnTransition scripts in this port)
    centers = {r.split('_PokemonCenter')[0] for r in rooms if r.endswith('_PokemonCenter_1F')}
    for key in TOWNS:
        sec = 'MAPSEC_' + key; s = secs[sec]
        town = next(n for n, z in zones.items() if z['mapsec'] == sec)
        cells = grid_cells[sec]
        xs = [c[0] for c in cells]; ys = [c[1] for c in cells]
        a = cell_px(min(xs), min(ys)); b = cell_px(max(xs), max(ys))
        c = centre(s)
        lines = [0xFFFF, LINE_POKEMON_CENTER] if town in centers else []
        vis, unvis = ICON_ANIMS[(s['width'], s['height'])]
        out.append(dict(key=key, mapsec=sec, type=TYPE_TOWN_ICON, anims=vis | unvis << 5,
                        zone=zones[town]['zone'], icon=c, snap=c,
                        cap=(a[0], a[1], b[0], b[1], 5), snap_r=6, fly_flag=flags['FLAG_VISITED_' + key], can_fly=1,
                        show=0xFFFF, lines=lines, sec=(s['x'], s['y'], s['width'], s['height'])))
    # routes: one record per straight run of their cursor-grid cells (the first one is the route's main record)
    routes = sorted((s for s in grid_cells if s.startswith('MAPSEC_ROUTE_')), key=lambda s: len(grid_cells[s]))
    for sec in routes:
        s = secs[sec]; zone = main_zone(sec); c = centre(s)
        for k, (a, b) in enumerate(_runs(grid_cells[sec])):
            pa, pb = cell_px(*a), cell_px(*b)
            out.append(dict(key=sec[7:] + (f'#{k}' if k else ''), mapsec=sec, type=TYPE_ROUTE, zone=zone, icon=c,
                            snap=((pa[0] + pb[0]) // 2, (pa[1] + pb[1]) // 2), cap=(pa[0], pa[1], pb[0], pb[1], 5),
                            snap_r=0, fly_flag=0xFFFF, can_fly=0, show=0xFFFF, lines=[], main=k == 0,
                            sec=(s['x'], s['y'], s['width'], s['height'])))
    assert not any(l['zone'] in (0, 424, 490) for l in out), 'zones 0/424/490 have Black 2 special cases in ov144'
    return out

def dex_highlights(locs):
    """The Pokédex area page's highlight of each location (record fields 24-26: anim, x, y; ov298/ov303 draw a sprite
    with that anim of a/1/5/7 NANR 46 at (x, y); hoenn_pokedex.py builds the cells): Sapphire's area screen
    (pokedex_area_screen.c) glows a town's or route's map cells (BuildAreaGlowTilemap: the solid glow tile 0x10 on every
    cell of the section) and puts its area marker on a dungeon (CreateAreaMarkerSprites: centred on the section).
    Here: ('fill', w, h) = the glow tile over the record's own cells (a town's cells, one straight run of a route) with
    (x, y) its top-left pixel; ('marker',) = the marker (16x16) for a landmark, (x, y) = the section's centre - 8.
    -> ([(anim, x, y)] per location, [shape per anim]): anim 0 the marker, then the fills in sorted order."""
    shapes, out = [('marker',)], []
    fills = sorted({('fill', (max(l['cap'][0], l['cap'][2]) - min(l['cap'][0], l['cap'][2])) // 8 + 1,
                     (max(l['cap'][1], l['cap'][3]) - min(l['cap'][1], l['cap'][3])) // 8 + 1)
                    for l in locs if l['type'] in (TYPE_ROUTE, TYPE_TOWN_ICON) and l['mapsec']})
    shapes += fills
    for l in locs:
        if not l['mapsec']:                                # the filler record: never shown, kept off screen
            out.append((0, 0, 200)); continue
        if l['type'] in (TYPE_ROUTE, TYPE_TOWN_ICON):
            x0, y0, x1, y1, _ = l['cap']
            w = (max(x0, x1) - min(x0, x1)) // 8 + 1; h = (max(y0, y1) - min(y0, y1)) // 8 + 1
            out.append((shapes.index(('fill', w, h)), min(x0, x1) - 4, min(y0, y1) - 4))
        else:
            sx, sy, sw, sh = l['sec']
            out.append((0, (sx + 1) * 8 + sw * 4 - 8, (sy + 2 + Y0) * 8 + sh * 4 - 8))
    return out, shapes

def record(l, hl=None):
    r = [0] * 27
    r[0] = l['zone']; r[1] = l['snap_r']
    r[2], r[3] = l['icon']; r[4], r[5] = l['snap']
    x0, y0, x1, y1, rad = l['cap']
    r[6], r[7], r[8], r[9], r[10] = x0, y0, x1, y1, rad
    r[11] = l['type']; r[12] = l['can_fly']; r[13] = r[14] = 0
    r[15] = l['fly_flag']; r[16] = l['show']
    lines = l['lines'] + [0xFFFF] * 7
    r[17:24] = lines[:7] if l['lines'] else [0xFFFF] * 7
    # 24-26: the Pokédex area page's highlight (ov298/ov303: anim, x, y; Black 2: 0 towns, 1 landmarks, 2-21 route
    # shapes at the shape's corner, towns/landmarks at the point - 8). Hoenn: dex_highlights (hoenn_pokedex's cells)
    if hl is None:
        r[24] = 0 if l['type'] in (TYPE_TOWN, TYPE_TOWN_ICON) else 1
        r[25], r[26] = l['icon'][0] - 8, l['icon'][1] - 8
    else:
        r[24], r[25], r[26] = hl
    return struct.pack('<27H', *[v & 0xFFFF for v in r])

def dummy_record(locs):
    """Record 84: Black 2's code and data are made for 85 records (the Pokédex's loops, its habitat files' 85 bytes per
    season); the last one is a harmless filler: Littleroot's zone (record lookups by zone find the real one first),
    a route (no icon) whose hit capsule (radius 0 at (0,0)) the cursor (y >= 8) never reaches."""
    return dict(key='(filler)', mapsec='', type=TYPE_ROUTE, zone=next(l['zone'] for l in locs if l['key'] == 'LITTLEROOT_TOWN'),
                icon=(8, 8), snap=(8, 8), cap=(0, 0, 0, 0, 0), snap_r=0, fly_flag=0xFFFF, can_fly=0, show=0xFFFF,
                lines=[], sec=(0, 0, 1, 1))

# ---------------------------------------------------------------------------------------------------- tables

PWT_ZONES = (191, 192, 193)

def zone_table(headers, locs):
    """One byte per zone header: the record of the zone's location (0xff: none). A zone's location is the region map
    section of its Sapphire map (pokeruby / pokeemerald map.json; underwater -> the route above, region_map.c
    sUnderwaterMaps; MAPSEC_DYNAMIC (the S.S. Tidal, link rooms) none), else the location named like the zone's place
    (rooms other agents add: Black 2 headers copied with the place of their map)."""
    main = {}
    for i, l in enumerate(locs):
        if l['type'] != TYPE_ROUTE or l.get('main'): main.setdefault(l['mapsec'], i)
    by_place = {}
    for i, l in enumerate(locs):
        p = headers[l['zone']]['place']
        if l['type'] != TYPE_ROUTE or l.get('main'): by_place.setdefault(p, i)
    zs = zone_sections()
    for z in PWT_ZONES:                   # Black 2's PWT (plaza, lobby, stadium) = Hoenn's Battle Tower (notes/RESEARCH_PWT.md)
        if z < len(headers): zs[z] = 'MAPSEC_BATTLE_TOWER'
    t = bytearray([0xFF] * len(headers))
    for z, h in enumerate(headers):
        sec = zs.get(z)
        if sec:
            sec = 'MAPSEC_' + UNDERWATER.get(sec[7:], sec[7:])
            if sec in main: t[z] = main[sec]
        elif h['place'] in by_place:
            t[z] = by_place[h['place']]
    return bytes(t)

def origins():
    """{map: (ox, oz, w, h)}: world tile of Sapphire's (0, 0) of every map on the Hoenn matrix (b2tools/world.py
    compose: layout tile + margin + shift + pad_north) and the map's size."""
    cfg = json.load(open(os.path.join(ROOT, 'data', 'hoenn_world.json')))
    lay = json.load(open(os.path.join(ROOT, 'data', 'hoenn_world_layout.json')))['main']['maps']
    zones = json.load(open(os.path.join(ROOT, 'data', 'hoenn_zones.json')))['maps']
    sa = os.path.join(ROOT, 'data', 'hoenn_standalone.json')
    standalone = {n for g in (json.load(open(sa))['groups'].values() if os.path.exists(sa) else []) for n in g['maps']}
    M = cfg['margin_cells'] * 32
    out = {}
    for name in lay:                      # (world.py load: the layout's maps with a zone, minus the warp-only ones)
        if name not in zones or name in standalone: continue
        L = lay[name]; pad = cfg.get('pad_north', {}).get(name, 0); sx, sz = cfg.get('shift', {}).get(name, [0, 0])
        plan = json.load(open(os.path.join(ROOT, 'data', 'plans', f'{name}.json')))
        W, H = plan['size']
        out[name] = (L['tile_x'] + M + sx, L['tile_z'] + M + sz + pad, W, H)
    return out

REF_SIZE = 20
def refine_table(locs, ztab):
    """Sapphire's player cell inside a multi-cell route section (region_map.c RegionMap_InitializeStateBasedOnPlayerLocation:
    x / (map width / section width), clamped; Route 114: x = 0 below row 0; Routes 121 and 126 their own thresholds),
    as thresholds in map tiles: u16 zone, u16 ox, u16 oz, u8 flags (1: Route 114), u8 section x, u8 x[4], u8 y[5],
    u8 section y, 2 pad (20 bytes)."""
    zones = json.load(open(os.path.join(ROOT, 'data', 'hoenn_zones.json')))['maps']
    org = origins()
    out = []
    for name, z in zones.items():
        sec = z['mapsec']
        if not sec.startswith('MAPSEC_ROUTE_') or name not in org: continue
        rec = ztab[z['zone']]
        if rec == 0xFF: continue
        sx, sy, sw, sh = locs[rec]['sec']
        if sw == 1 and sh == 1: continue
        ox, oz, W, H = org[name]
        xt = [k * max(W // sw, 1) for k in range(1, sw)]
        yt = [k * max(H // sh, 1) for k in range(1, sh)]
        flags = 0
        if sec == 'MAPSEC_ROUTE_114': flags = 1
        if sec == 'MAPSEC_ROUTE_126': xt, yt = [33, 52], [38, 57]      # x > 32, > 0x33; y > 0x25, > 0x38
        if sec == 'MAPSEC_ROUTE_121': xt = [15, 29, 55]                  # x > 14, > 0x1c, > 0x36
        assert len(xt) <= 4 and len(yt) <= 5 and max(xt + yt + [0]) < 255, (name, xt, yt)
        out.append(struct.pack('<HHHBB4B5BBxx', z['zone'], ox, oz, flags, sx, *(xt + [255] * (4 - len(xt))),
                               *(yt + [255] * (5 - len(yt))), sy))
    return out

NREC = 85                              # Black 2's record count (the Pokédex's loops and habitat format)

def data_file(headers):
    """a/0/8/4 #21 (little-endian; hoenn_pokedex reads it too): records at 0, NREC x 54 B (27 u16, notes/TOWN_MAP.md) |
    zone table at ZT (u8 record per zone header, 0xff none) | refine table at REF (u16 count, u16 0, 20-B entries) |
    icon anims at ANIM (u16 per record: visited | not visited << 5, 0 = Black 2's) | 16-B trailer 'TMAP', u16 NREC,
    ZT, zone count, REF, ANIM, 0.  -> (bytes, layout, locations, zone table)"""
    locs = locations()
    assert len(locs) < NREC, len(locs)
    locs = locs + [dummy_record(locs)] * (NREC - len(locs))
    hls, _ = dex_highlights(locs)
    recs = b''.join(record(l, hl) for l, hl in zip(locs, hls))
    ztab = zone_table(headers, locs)
    zt_off = (len(recs) + 3) & ~3
    ref_off = (zt_off + len(ztab) + 3) & ~3
    refs = refine_table(locs, ztab)
    d = recs + bytes(zt_off - len(recs)) + ztab + bytes(ref_off - zt_off - len(ztab))
    d += struct.pack('<HH', len(refs), 0) + b''.join(refs)
    anim_off = (len(d) + 3) & ~3
    d += bytes(anim_off - len(d)) + struct.pack(f'<{len(locs)}H', *[l.get('anims', 0) for l in locs])
    d += bytes((-len(d)) % 4) + struct.pack('<4s6H', b'TMAP', len(locs), zt_off, len(ztab), ref_off, anim_off, 0)
    return d, dict(n=len(locs), zt_off=zt_off, nzones=len(ztab), ref_off=ref_off, nref=len(refs), anim_off=anim_off), locs, ztab

def read_file21(files):
    """The built a/0/8/4 #21 of a files tree: dict(n, records=[27-tuples], zone_table=bytes, refine=[...], anims=[...])."""
    import narcio
    d = narcio.load(files, ARC_GFX)[NEW_FILE]
    i = d.rfind(b'TMAP'); n, zt, nz, ref, anim, _ = struct.unpack_from('<6H', d, i + 4)
    nref = struct.unpack_from('<H', d, ref)[0]
    return dict(n=n, records=[struct.unpack_from('<27H', d, REC * k) for k in range(n)], zone_table=d[zt:zt + nz],
                refine=[struct.unpack_from('<HHHBB4B5BB', d, ref + 4 + REF_SIZE * k) for k in range(nref)],
                anims=list(struct.unpack_from(f'<{n}H', d, anim)))

def _pad_narc(data, target):
    """Grow a NARC (its GMIF and header sizes) to `target` bytes with zeros, as build_rom.py pad_archives does."""
    data = bytearray(data)
    assert len(data) <= target, (len(data), target)
    hdr = struct.unpack_from('<H', data, 0xC)[0]; off = hdr
    for _ in range(2): off += struct.unpack_from('<I', data, off + 4)[0]
    assert data[off:off + 4] == b'GMIF'
    extra = target - len(data)
    struct.pack_into('<I', data, off + 4, struct.unpack_from('<I', data, off + 4)[0] + extra)
    struct.pack_into('<I', data, 8, target)
    return bytes(data) + bytes(extra)

# Fly lands where Sapphire's Fly does: the town's heal location (src/data/heal_locations.json HEAL_LOCATION_<TOWN>, the
# tile in front of the Pokémon Center; region_map.c sub_80FC5B4 -> sub_8053538(heal location); the Battle Tower its
# island's). Black 2 lands on the zone header's fly point (ov033 EventFly: LoadZoneSpawnInfoCheckRail), which
# hoenn_world.py sets to a walkable tile near the map's middle (world.py 'fly'); Teleport and the Escape Rope's fallback
# use the same point (ov035 event_mapchange.c), and Sapphire's Teleport lands at the heal location too. Littleroot keeps
# world.py's point between the two houses (the Escape Rope's fallback); Fly lands at the player's own house and Teleport home
# in the bedroom (the hooks below).
HEAL_LANDING = True
def fly_points(world_dir=None):
    """{zone: (x, z)}: the heal tile of each town (and the Battle Tower island) in its matrix's tiles, when that tile is
    walkable and in the town's zone (work/world cells); towns whose heal tile fails keep world.py's point (listed)."""
    world_dir = world_dir or os.environ.get('HOENN_WORLD_DIR') or os.path.join(ROOT, 'work', 'world')
    w = json.load(open(os.path.join(world_dir, 'world.json')))
    zones = json.load(open(os.path.join(ROOT, 'data', 'hoenn_zones.json')))['maps']
    heal = {h['id']: h for h in json.load(open(os.path.join(RUBY, 'src', 'data', 'heal_locations.json')))['heal_locations']}
    org = {n: o[:2] for n, o in origins().items()}
    group_of = {}
    for g in w['standalone']:
        for n, o in g['origins'].items(): org[n] = tuple(o); group_of[n] = g
    def snake(n): return '_'.join(re.sub(r'(?<!^)(?=[A-Z])', '_', part).upper() for part in n.split('_'))
    targets = {'MAPSEC_' + t for t in TOWNS} | {'MAPSEC_BATTLE_TOWER'}      # Sapphire's Fly targets
    out, kept = {}, []
    grids = {}
    for name, z in zones.items():
        hid = 'HEAL_LOCATION_' + snake(name)
        if z['mapsec'] not in targets or hid not in heal or name == 'LittlerootTown' or name not in org: continue
        h = heal[hid]
        x, zz = org[name][0] + h['x'], org[name][1] + h['y']
        g = group_of.get(name)
        key = g['group'] if g else None
        if key not in grids:
            cells = g['cells'] if g else w['cells']
            grid, owner = {}, {}
            for c in cells:
                d = c.get('dir') or next((os.path.basename(p) for p in [os.path.join(world_dir, 'cells', f"{c['cx']:02d}_{c['cz']:02d}")] if os.path.isdir(p)), None)
                if d is None: continue
                f = os.path.join(world_dir, 'cells', d, 'chunk.json')
                if not os.path.exists(f): continue
                for zz_, row in enumerate(json.load(open(f))['collision']):
                    for xx, ch in enumerate(row): grid[(c['cx'] * 32 + xx, c['cz'] * 32 + zz_)] = ch
                for xx in range(32):
                    for zz_ in range(32): owner[(c['cx'] * 32 + xx, c['cz'] * 32 + zz_)] = c['zone']
            grids[key] = (grid, owner)
        grid, owner = grids[key]
        zone_here = owner.get((x, zz))
        if not g:
            for x0, z0, x1, z1, rz in w.get('zone_rects', []):
                if x0 <= x <= x1 and z0 <= zz <= z1: zone_here = rz; break
        ch = grid.get((x, zz))
        if ch is None or ch in '#v' or zone_here != z['zone']:
            kept.append(f"{name} ({ch!r}, zone {zone_here})"); continue
        out[z['zone']] = (x, zz)
    return out, kept

# Fly to Littleroot lands in front of the player's own house (littleroot2, 2026-10-19): pokeruby region_map.c (Fly to
# MAPSEC_LITTLEROOT_TOWN: sub_8053538(playerGender == MALE ? HEAL_LOCATION_LITTLEROOT_TOWN_BRENDANS_HOUSE :
# ..._MAYS_HOUSE)), pokeemerald the same (SetWarpDestinationToHealLocation): (5,9) below Brendan's door for a boy,
# (14,9) below May's for a girl. Black 2's Fly takes the zone header's one fly point, so EventFly's creation
# (ov033 func_ov033_02178908) calls a hook instead of LoadZoneSpawnInfoCheckRail: it loads the spawn as before, then in
# Littleroot puts the player on the tile of their sex (the event's take-off effect, set just before the call from the
# player's sex: 11 boy, 31 girl). The header point between the houses stays for the Escape Rope's fallback (Teleport
# home: the bedroom, apply_home_teleport below). The hook sits in the
# zero tail of dive.py's spawn-hook block (ov033's dead CheckAbyssalRuinsStepEvent; dive runs first in the patch list).
# Code only: saves are unchanged.
LITTLEROOT_FLY = True
OV033 = 0x02176B00
FLY_SPAWN_CALL = 0x02178956             # func_ov033_02178908: bl LoadZoneSpawnInfoCheckRail (r0 = &work->spawn, r1 = zone)
LoadZoneSpawnInfoCheckRail = 0x020190C8
FLY_HOOK_SPACE = (0x02179E98, 0x02179F04)   # dive.py HOOK (its spawn hook, then zeros)
FLY_EFFECT_OUT = 0x1C                   # FlyEventWork.effectOut (work + 0x28) from &work->spawn (work + 0xC)

def littleroot_landings(world_dir=None):
    """(zone, {'boy': (x, z), 'girl': (x, z)}): Gen 3's Fly landings in Littleroot (the version's decomp's heal locations
    HEAL_LOCATION_LITTLEROOT_TOWN_BRENDANS_HOUSE / _MAYS_HOUSE) in world tiles, each checked walkable and in the zone."""
    import version
    world_dir = world_dir or os.environ.get('HOENN_WORLD_DIR') or version.world_dir()
    w = json.load(open(os.path.join(world_dir, 'world.json')))
    zone = json.load(open(os.path.join(ROOT, 'data', 'hoenn_zones.json')))['maps']['LittlerootTown']['zone']
    heal = {h['id']: h for h in json.load(open(os.path.join(version.DECOMP, 'src', 'data', 'heal_locations.json')))['heal_locations']}
    ox, oz = origins()['LittlerootTown'][:2]
    out = {}
    for sex, hid in (('boy', 'HEAL_LOCATION_LITTLEROOT_TOWN_BRENDANS_HOUSE'), ('girl', 'HEAL_LOCATION_LITTLEROOT_TOWN_MAYS_HOUSE')):
        h = heal[hid]
        assert h['map'] == 'MAP_LITTLEROOT_TOWN', h
        x, z = ox + h['x'], oz + h['y']
        cell = next(c for c in w['cells'] if c['cx'] == x // 32 and c['cz'] == z // 32)
        d = cell.get('dir') or f"{cell['cx']:02d}_{cell['cz']:02d}"
        ch = json.load(open(os.path.join(world_dir, 'cells', d, 'chunk.json')))['collision'][z % 32][x % 32]
        assert cell['zone'] == zone and ch not in '#v', (sex, x, z, ch, cell['zone'])   # (a zone_rect would win: none in Littleroot)
        out[sex] = (x, z)
    return zone, out

def littleroot_fly_hook(at, zone, pts):
    """hook(spawn, zone): LoadZoneSpawnInfoCheckRail(spawn, zone); in `zone`, spawn.pos.x/z = the boy's or the girl's
    tile centre (fx32: tile * 16 + 8 units)."""
    fx = lambda t: t << 16 | 0x8000
    assert pts['boy'][1] == pts['girl'][1], pts
    t = T(at)
    t.push([3, 4, 5]); t.mov(4, 0); t.mov(5, 1)
    t.bl(LoadZoneSpawnInfoCheckRail)
    t.ldr_lit(0, 'zone'); t.cmpr(5, 0); t.bne('done')
    t.ldr_lit(1, 'xb'); t.ldr_off(0, 4, FLY_EFFECT_OUT); t.cmp(0, 11); t.beq('set')   # 11: a boy's take-off
    t.ldr_lit(1, 'xg')
    t.label('set'); t.str_off(1, 4, 16)                          # spawn.pos.x (pos at +16: dive.py's hook)
    t.ldr_lit(1, 'z'); t.str_off(1, 4, 24)                       # spawn.pos.z (y: the header's)
    t.label('done'); t.pop([3, 4, 5])
    t.word('zone', zone); t.word('xb', fx(pts['boy'][0])); t.word('xg', fx(pts['girl'][0])); t.word('z', fx(pts['boy'][1]))
    return t.assemble()

def apply_littleroot_fly(code):
    zone, pts = littleroot_landings()
    path = os.path.join(code, 'arm9_ov033.bin')
    ov = bytearray(open(path, 'rb').read())
    n = len(littleroot_fly_hook(FLY_HOOK_SPACE[0], zone, pts))
    at = (FLY_HOOK_SPACE[1] - n) & ~3
    assert not any(ov[at - OV033:FLY_HOOK_SPACE[1] - OV033]), 'Littleroot Fly hook: dive.py\'s spawn hook block has no room (dive patch first?)'
    hook = littleroot_fly_hook(at, zone, pts)
    ov[at - OV033:at - OV033 + len(hook)] = hook
    def bl(src, dst):
        off = dst - (src + 4)
        return struct.pack('<HH', 0xF000 | (off >> 12) & 0x7FF, 0xF800 | (off >> 1) & 0x7FF)
    c = FLY_SPAWN_CALL - OV033
    assert bytes(ov[c:c + 4]) == bl(FLY_SPAWN_CALL, LoadZoneSpawnInfoCheckRail), f'EventFly spawn call: {bytes(ov[c:c + 4]).hex()}'
    ov[c:c + 4] = bl(FLY_SPAWN_CALL, at)
    if os.path.islink(path): os.unlink(path)
    open(path + '.tmp', 'wb').write(ov); os.replace(path + '.tmp', path)
    return f"; Fly to Littleroot lands by the player's sex: boy {pts['boy']}, girl {pts['girl']} (ov033 hook {len(hook)} B at {at:#x})"

# Teleport home (littleroot2 follow-up, 2026-10-19): Gen 3's Teleport goes to the last heal location (pokeruby
# field_effect.c Overworld_SetWarpDestToLastHealLoc, pokeemerald TeleportWarpOutFieldEffect_End
# SetWarpDestinationToLastHealLocation). Before the first Pokémon Center, and again after the Hall of Fame, that is the
# player's own bedroom (InsideOfTruck / the Hall of Fame: setrespawn HEAL_LOCATION_LITTLEROOT_TOWN_BRENDANS_HOUSE_2F or
# _MAYS_HOUSE_2F, (4,2) of the 2F map). Black 2's Teleport (ov035 EventMapChangeTeleport_Create) lands on the zone header
# point of the return location's main zone: for RESPAWN_ZONE_INFO record 0 (home) that is Littleroot, between the
# houses. Its LoadZoneSpawnInfoCheckRail call goes to a hook in ITCM (the arena-literal protocol of hm_free.py /
# fairy.py): the spawn as before, then, when the return location is 1 (1-based: RESPAWN_ZONE_INFO record 0, h_setrespawn 1;
# the caller keeps it in r6, the GameSystem in r5),
# the bedroom of the player's sex at Gen 3's tile (the room's zone tiles = map tiles + its origin), on the floor (y 0,
# as the rooms' scripted warps). A Center's return location keeps Black 2's landing (town_map's heal tiles).
# The blackout at home lands in the same bedroom by script (0780_brendans_house_1f.s Script_2). Code only.
HOME_TELEPORT = True
TELEPORT_SPAWN_CALL = 0x0217DD88        # ov035 EventMapChangeTeleport_Create: bl LoadZoneSpawnInfoCheckRail
OV035 = 0x0217C940
GetGameDataPlayerInfo, getTrainerGender = 0x0201736C, 0x02008BF0
ITCM_BASE, ARENA_ITCM_LIT, ARM9 = 0x01FF8000, 0x0207B400, 0x02004000

def home_bedrooms(rooms_dir=None):
    """{'boy': (zone, x, z), 'girl': (zone, x, z)}: Gen 3's home heal locations (the version's decomp:
    HEAL_LOCATION_LITTLEROOT_TOWN_BRENDANS_HOUSE_2F / _MAYS_HOUSE_2F) in our rooms' zone tiles, checked walkable."""
    import version
    rooms_dir = rooms_dir or os.environ.get('HOENN_INTERIORS_DIR') or os.path.join(ROOT, 'work', 'interiors')
    rooms = json.load(open(os.path.join(ROOT, 'data', 'hoenn_interiors.json')))['rooms']
    heal = {h['id']: h for h in json.load(open(os.path.join(version.DECOMP, 'src', 'data', 'heal_locations.json')))['heal_locations']}
    out = {}
    for sex, house in (('boy', 'BRENDANS'), ('girl', 'MAYS')):
        h = heal[f'HEAL_LOCATION_LITTLEROOT_TOWN_{house}_HOUSE_2F']
        name = {'BRENDANS': 'LittlerootTown_BrendansHouse_2F', 'MAYS': 'LittlerootTown_MaysHouse_2F'}[house]
        assert h['map'] == 'MAP_' + 'LITTLEROOT_TOWN_' + house + '_HOUSE_2F', h
        d = os.path.join(rooms_dir, version.room_variant(name))
        if not os.path.exists(os.path.join(d, 'room.json')): d = os.path.join(rooms_dir, name)
        meta = json.load(open(os.path.join(d, 'room.json')))
        ox, oz = meta['origin']
        x, z = h['x'] + ox, h['y'] + oz
        per = open(os.path.join(d, meta['collision']), 'rb').read()
        assert not struct.unpack_from('<HHHH', per, 4 + 8 * (z * 32 + x))[3] & 1, (name, x, z, 'solid')
        out[sex] = (rooms[name]['zone'], x, z)
    return out

def home_teleport_hook(base, homes):
    fx = lambda t: t << 16 | 0x8000
    assert homes['boy'][1:] == homes['girl'][1:], homes
    t = T(base)
    t.push([4, 5, 6]); t.mov(4, 0)
    t.bl(LoadZoneSpawnInfoCheckRail)                             # (r0 = spawn, r1 = the main zone): Black 2's landing
    t.cmp(6, 1); t.bne('done')                                   # the caller's GetReturnLocationIdx: 1 = home (record 0)
    t.mov(0, 5); t.bl(GSYS_GetGameData); t.bl(GetGameDataPlayerInfo); t.bl(getTrainerGender)
    t.ldr_lit(1, 'zb'); t.cmp(0, 0); t.beq('load')
    t.ldr_lit(1, 'zg')
    t.label('load'); t.mov(0, 4); t.bl(LoadZoneSpawnInfoCheckRail)   # the bedroom zone (changeType, zone, direction)
    t.ldr_lit(0, 'x'); t.str_off(0, 4, 16)                       # spawn.pos.x
    t.movs(0, 0); t.str_off(0, 4, 20)                            # spawn.pos.y: the floor
    t.ldr_lit(0, 'z'); t.str_off(0, 4, 24)                       # spawn.pos.z
    t.label('done'); t.pop([4, 5, 6])
    t.word('zb', homes['boy'][0]); t.word('zg', homes['girl'][0]); t.word('x', fx(homes['boy'][1])); t.word('z', fx(homes['boy'][2]))
    return t.assemble()

def apply_home_teleport(code):
    homes = home_bedrooms()
    yml = os.path.join(code, 'itcm.yaml')
    text = open(yml).read()
    size = int(re.search(r'^code_size: (\d+)$', text, re.M).group(1))
    assert re.search(r'^base_address: (\d+)$', text, re.M).group(1) == str(ITCM_BASE)
    base = ITCM_BASE + size
    p9 = os.path.join(code, 'arm9.bin'); arm9 = bytearray(open(p9, 'rb').read())
    lit = ARENA_ITCM_LIT - ARM9
    assert struct.unpack_from('<I', arm9, lit)[0] == base, 'Teleport home: the ITCM arena literal is not the end of ITCM'
    blob = home_teleport_hook(base, homes)
    end = (base + len(blob) + 31) & ~31
    struct.pack_into('<I', arm9, lit, end)
    pi = os.path.join(code, 'itcm.bin'); itcm = open(pi, 'rb').read()
    assert len(itcm) == size
    po = os.path.join(code, 'arm9_ov035.bin'); ov = bytearray(open(po, 'rb').read())
    def bl(src, dst):
        off = dst - (src + 4)
        assert -(1 << 22) <= off < (1 << 22)
        return struct.pack('<HH', 0xF000 | (off >> 12) & 0x7FF, 0xF800 | (off >> 1) & 0x7FF)
    c = TELEPORT_SPAWN_CALL - OV035
    assert bytes(ov[c:c + 4]) == bl(TELEPORT_SPAWN_CALL, LoadZoneSpawnInfoCheckRail), f'Teleport spawn call: {bytes(ov[c:c + 4]).hex()}'
    ov[c:c + 4] = bl(TELEPORT_SPAWN_CALL, base)
    for path, data in ((p9, arm9), (pi, bytes(itcm) + blob + bytes(end - base - len(blob))), (po, ov)):
        if os.path.islink(path): os.unlink(path)
        open(path + '.tmp', 'wb').write(data); os.replace(path + '.tmp', path)
    open(yml, 'w').write(re.sub(r'^code_size: \d+$', f'code_size: {end - ITCM_BASE}', text, flags=re.M))
    return (f"; Teleport home lands in the bedroom: boy zone {homes['boy']}, girl {homes['girl']} "
            f"(ITCM hook {len(blob)} B at {base:#x}, arena from {end:#x})")

LAYOUT = {}
def apply(files):
    import narcio, zoneheaders
    from b2files import arc_path
    path = arc_path(files, ARC_GFX)
    size = os.path.getsize(path)
    entries = narcio.load(files, ARC_GFX)
    assert len(entries) == 21, f'a/0/8/4 has {len(entries)} files (town_map applied twice?)'
    headers, _ = zoneheaders.load(files)
    blob, lay, locs, ztab = data_file(headers)
    new = art_entries(entries, locs)
    LAYOUT.update(lay)
    new.append(blob)
    narcio.save(files, ARC_GFX, new)
    fly_note = ''
    if HEAL_LANDING:
        pts, kept = fly_points()
        hd, ents = zoneheaders.load(files)
        for z, (x, zz) in pts.items(): hd[z]['fly_x'], hd[z]['fly_z'] = x, zz
        zoneheaders.save(files, hd, ents)
        fly_note = f'; Fly lands at Sapphire\'s heal tiles in {len(pts)} zones' + (f' (kept world.py\'s point: {kept})' if kept else '')
    d = open(path, 'rb').read()
    open(path + '.tmp', 'wb').write(_pad_narc(d, size)); os.replace(path + '.tmp', path)
    json.dump(dict(layout=lay, locations=locs, zone_table={z: locs[r]['key'] for z, r in enumerate(ztab) if r != 0xFF}),
              open(os.path.join(os.path.dirname(files), 'town_map.json'), 'w'), indent=1, default=list)
    return (f"Sapphire's region map in BG3 ({len(bg3_screen()[0])} tiles); {lay['n']} locations, "
            f"{sum(1 for r in ztab if r != 0xFF)} zones placed, {lay['nref']} refined routes; file {NEW_FILE} {len(blob)} B"
            + fly_note)

# ---------------------------------------------------------------------------------------------------- the code (ov144)

GSYS_GetGameData, GameData_GetPlayerState = 0x02016AD8, 0x020171F4
GetZoneFlagsEnableFlyFrom, GFL_ArcSysReadHeapNewLZ = 0x020189CC, 0x0204B4E4
INIT_LOAD_CALL = 0x0219CF18          # init: movs r0, #0x44; bl func_ov144_0219f718 (r5 = gameData, r6 = the param)
FIND_ENTRY = (0x0219E118, 0x0219E154)   # func_ov144_0219e118(module, zone): the player's location entry
COUNT_AT, BOUND_AT = 0x0219DDA4, 0x0219DE3C   # func_ov144_0219dd78: movs r0, #0x54 (entries); cmp r4, #0x55 (records)
JA_BRANCH = 0x0219ECF8               # func_ov144_0219eb6c: bne .L_0219ecfc (Join Avenue lines, zone 490 only)
FREE = (0x0219ECFC, 0x0219EE7C)      # ... the Join Avenue block it jumps to: unreachable once the branch is gone
SIZE_FILLER = 48
LOADER = 0x0219F71C                    # func_ov144_0219f718 + 4: movs r0, #0x55; movs r1, #0; movs r2, #0 (a/0/8/5 #0);
                                       # the Pokédex (ov298, ov303, ov308) gets the Hoenn records without this switch:
POKEDEX_RECORDS = False                # hoenn_pokedex.py sends its calls to its own loader (ov144 keeps its tuned size)
JA_DEAD = [(0x0219EBD4, bytes.fromhex('11d0'), 0x0219EBFA),   # func_ov144_0219eb6c: the name from JoinAvenue_GetParam
           (0x0219F13E, bytes.fromhex('1fd0'), 0x0219F180)]   # func_ov144_0219f0ec: the same for the banner

class T:
    def __init__(self, base):
        sys.path.insert(0, HERE)
        import importlib.util
        spec = importlib.util.spec_from_file_location('exp_share_', os.path.join(HERE, 'exp_share.py'))
        es = importlib.util.module_from_spec(spec); spec.loader.exec_module(es)
        self.t = es.Thumb(base)
    def __getattr__(self, k): return getattr(self.t, k)
    def asrs(self, rd, rm, imm): self.t.h(0x1000 | imm << 6 | rm << 3 | rd)
    def subsr(self, rd, rn, rm): self.t.h(0x1A00 | rm << 6 | rn << 3 | rd)
    def strh_off(self, rd, rn, off): assert off % 2 == 0 and off < 64; self.t.h(0x8000 | off >> 1 << 6 | rn << 3 | rd)
    def ldrb_rr(self, rd, rn, rm): self.t.h(0x5C00 | rm << 6 | rn << 3 | rd)
    def str_off(self, rd, rn, off): assert off % 4 == 0 and off < 128; self.t.h(0x6000 | off >> 2 << 6 | rn << 3 | rd)

def find_entry_code(lay):
    """func_ov144_0219e118 replacement: entry whose record index (+8) is the zone table's record for `zone`."""
    t = T(FIND_ENTRY[0])
    t.push([4])
    t.ldr_off(2, 0, 8); t.ldr_off(3, 0, 12)                   # entries, count
    t.cmp(3, 0); t.beq('none')
    t.ldr_off(4, 2, 4)                                        # the records (entry 0's)
    t.ldr_lit(0, 'nz'); t.cmpr(1, 0); t.bcc('hs', 'none')
    t.ldr_lit(0, 'zt'); t.addsr(4, 4, 0)
    t.ldrb_rr(1, 4, 1)                                        # record of the zone (0xff: none)
    t.label('loop')
    t.ldr_off(0, 2, 8); t.cmpr(0, 1); t.beq('found')
    t.addi(2, 0x44); t.subi(3, 1); t.bne('loop')
    t.label('none'); t.movs(0, 0); t.pop([4])
    t.label('found'); t.mov(0, 2); t.pop([4])
    t.word('nz', lay['nzones']); t.word('zt', lay['zt_off'])
    code = t.assemble()
    assert len(code) <= FIND_ENTRY[1] - FIND_ENTRY[0], len(code)
    return code

def load_code(lay):
    """HoennLoad(heap) at FREE[0], called by init instead of func_ov144_0219f718 (r5 = gameData, r6 = TownMapParam):
    view mode for a scripted call (mode 0 from CallPlaceSelect) in a zone without Fly, the locations from a/0/8/4 #21,
    then the player's cell in a multi-cell route (Sapphire's rule, refine_table)."""
    t = T(FREE[0])
    t.push([3, 4, 7])
    t.mov(7, 0)                                               # heap
    t.ldr_off(0, 6, 0); t.cmp(0, 0); t.bne('load')            # param->mode
    t.ldrh_off(0, 6, 8); t.bl(GetZoneFlagsEnableFlyFrom)      # param->zoneId
    t.cmp(0, 0); t.bne('load')
    t.movs(0, 1); t.str_off(0, 6, 0)                          # param->mode = 1 (view)
    t.label('load')
    t.movs(0, ARC_GFX); t.movs(1, NEW_FILE); t.movs(2, 0); t.mov(3, 7)
    t.bl(GFL_ArcSysReadHeapNewLZ)
    t.mov(4, 0)
    t.mov(0, 5); t.bl(GameData_GetPlayerState)
    t.mov(1, 0); t.mov(0, 4); t.bl_label('refine')
    t.mov(0, 4); t.pop([3, 4, 7])
    # refine(data r0, PlayerState* r1)
    t.label('refine')
    t.push([3, 4, 5, 6, 7])
    t.mov(4, 0); t.mov(5, 1)
    t.ldrh_off(6, 5, 0)                                       # zone
    t.ldr_lit(0, 'ref'); t.addsr(7, 4, 0)
    t.ldrh_off(3, 7, 0); t.addi(7, 4)                         # count, first entry
    t.label('find')
    t.cmp(3, 0); t.beq('done')
    t.ldrh_off(0, 7, 0); t.cmpr(0, 6); t.beq('found')
    t.addi(7, REF_SIZE); t.subi(3, 1); t.b('find')
    t.label('found')
    t.ldr_off(0, 5, 4); t.asrs(0, 0, 16)                      # player tile x (position fx32, 16 units a tile)
    t.ldrh_off(1, 7, 2); t.subsr(0, 0, 1)                     # - ox
    t.movs(2, 0)
    t.label('xl')
    t.adds(1, 7, 0); t.addi(1, 8); t.ldrb_rr(1, 1, 2)         # x threshold k
    t.cmpr(0, 1); t.bcc('lt', 'xd'); t.adds(2, 2, 1); t.cmp(2, 4); t.bcc('lt', 'xl')
    t.label('xd')
    t.ldr_off(0, 5, 12); t.asrs(0, 0, 16)                     # player tile z
    t.ldrh_off(1, 7, 4); t.subsr(0, 0, 1)                     # - oz
    t.movs(3, 0)
    t.label('yl')
    t.adds(1, 7, 0); t.addi(1, 12); t.ldrb_rr(1, 1, 3)        # y threshold k
    t.cmpr(0, 1); t.bcc('lt', 'yd'); t.adds(3, 3, 1); t.cmp(3, 5); t.bcc('lt', 'yl')
    t.label('yd')
    t.ldrb_off(0, 7, 6); t.cmp(0, 0); t.beq('cell')           # Route 114: x = 0 below its first row
    t.cmp(3, 0); t.beq('cell'); t.movs(2, 0)
    t.label('cell')
    t.ldr_lit(0, 'zt'); t.addsr(0, 4, 0); t.ldrb_rr(0, 0, 6)  # the zone's record
    t.movs(1, REC); t.muls(0, 1); t.addsr(0, 4, 0)            # its address
    t.ldrb_off(1, 7, 7); t.addsr(2, 2, 1)                     # cell x = section x (refine entry +7) + cx
    t.lsls(2, 2, 3); t.addi(2, 12)                            # (x + 1) * 8 + 4
    t.ldrb_off(1, 7, 17); t.addsr(3, 3, 1)                    # cell y = section y (refine entry +17) + cy
    t.lsls(3, 3, 3); t.addi(3, (2 + Y0) * 8 + 4)              # (y + 2 + Y0) * 8 + 4
    t.strh_off(2, 0, 4); t.strh_off(3, 0, 6)                  # icon (= the player marker)
    t.strh_off(2, 0, 8); t.strh_off(3, 0, 10)                 # snap point (= the cursor's start)
    t.label('done')
    t.pop([3, 4, 5, 6, 7])
    type5_code(t)
    t.word('ref', lay['ref_off']); t.word('zt', lay['zt_off']); t.word('anim', lay['anim_off'])
    code = t.assemble()
    assert len(code) <= FREE[1] - FREE[0], len(code)
    return code, FREE[0], t.labels['type5']

TYPE5_CASE = (0x0219E2B8, 0x0219E2CC)   # func_ov144_0219e18c, switch on the record type, case 5 (up to .L_0219e2cc)
F730 = 0x0219F730                      # func_ov144_0219f730(records, index, field): a record's u16 field

def type5_code(t):
    """Type5Anims(entry r0) -> r1 = the entry's anim, also stored as its selected anim (+0x31): the file's icon-anim
    table (u16 per record at ANIM: visited | not visited << 5, 5 bits each; Sapphire's icon does not change when
    selected: the cursor ring shows it) when not 0, else Black 2's (0x11 visited / 0x10, 0x12 selected)."""
    t.label('type5')
    t.push([3, 4])
    t.mov(4, 0)
    t.ldr_off(0, 4, 4); t.ldr_off(1, 4, 8); t.lsls(1, 1, 1); t.addsr(0, 0, 1)   # records + index * 2
    t.ldr_lit(1, 'anim'); t.addsr(0, 0, 1); t.ldrh_off(0, 0, 0)               # the record's icon anims
    t.cmp(0, 0); t.bne('t5c')
    t.movs(1, 0x12); t.adds(2, 4, 0); t.addi(2, 0x31); t.strb_off(1, 2, 0)
    t.ldr_off(0, 4, 0x38); t.movs(1, 0x10); t.cmp(0, 0); t.beq('t5r'); t.movs(1, 0x11)
    t.label('t5r'); t.pop([3, 4])
    t.label('t5c')
    t.ldr_off(2, 4, 0x38); t.cmp(2, 0); t.beq('t5u')
    t.lsls(1, 0, 27); t.b('t5s')                                              # visited
    t.label('t5u')
    t.lsls(1, 0, 22)                                                          # not visited
    t.label('t5s')
    t.lsrs(1, 1, 27)
    t.adds(2, 4, 0); t.addi(2, 0x31); t.strb_off(1, 2, 0)                    # selected: the same icon
    t.pop([3, 4])

def type5_case(at):
    """Case 5 of the type switch: r1 = Type5Anims(entry), then Black 2's store of r1 at +0x30 (.L_0219e2cc)."""
    t = T(TYPE5_CASE[0])
    t.mov(0, 4); t.bl(at); t.at('back', TYPE5_CASE[1]); t.b('back')
    code = t.assemble()
    return code + bytes.fromhex('c046') * ((TYPE5_CASE[1] - TYPE5_CASE[0] - len(code)) // 2)

def _put(ov, addr, old, new, what):
    at = addr - OV144
    if old is not None:
        assert bytes(ov[at:at + len(old)]) == old, f'{what}: unexpected bytes {bytes(ov[at:at + len(old)]).hex()} at {addr:#x}'
    ov[at:at + len(new)] = new

def apply_code(code):
    if not LAYOUT:                       # (apply ran in another process: recompute from the files tree next to code)
        import narcio, zoneheaders
        files = os.path.join(os.path.dirname(code), 'files')
        LAYOUT.update(data_file(zoneheaders.load(files)[0])[1])
    lay = LAYOUT
    path = os.path.join(code, 'arm9_ov144.bin')
    ov = bytearray(open(path, 'rb').read())
    _put(ov, COUNT_AT, bytes.fromhex('5420'), struct.pack('<H', 0x2000 | lay['n']), 'entry count')   # 85: none skipped
    _put(ov, BOUND_AT, bytes.fromhex('552c'), struct.pack('<H', 0x2C00 | lay['n']), 'record loop bound')
    _put(ov, JA_BRANCH, bytes.fromhex('00d1'), bytes.fromhex('c046'), 'Join Avenue branch')
    # the other two Join Avenue paths (zone 490 only; no record has it): unconditional jumps over them and their code
    # zeroed, so ov144 compresses to no more than Black 2's size (ROM layout and old savestates: notes/TOWN_MAP.md)
    for at, old_, end in JA_DEAD:
        _put(ov, at, old_, struct.pack('<H', 0xE000 | ((end - (at + 4)) >> 1) & 0x7FF), 'Join Avenue jump')
        _put(ov, at + 2, None, bytes(end - at - 2), 'Join Avenue code')
    load, at, t5 = load_code(lay)
    # filler after the code: dsd's BLZ then gives ov144 exactly Black 2's compressed size (8,688 B), so the ROM's file
    # table stays Black 2's (old savestates keep working). Tuned with work/agents/town_map/tools/tune.py (48 bytes of
    # random.Random(144)); recheck it after any change of this file's code.
    import random
    rng = random.Random(144)
    filler = bytes(rng.randrange(256) for _ in range(FREE[1] - FREE[0] - len(load)))[:SIZE_FILLER]
    _put(ov, FREE[0], None, load + filler + bytes(FREE[1] - FREE[0] - len(load) - len(filler)), 'HoennLoad')
    import importlib.util
    off = at - (INIT_LOAD_CALL + 4)
    _put(ov, INIT_LOAD_CALL, None, struct.pack('<HH', 0xF000 | (off >> 12) & 0x7FF, 0xF800 | (off >> 1) & 0x7FF),
         'init: load call')
    _put(ov, TYPE5_CASE[0], bytes.fromhex('201c122131300170'), type5_case(t5), 'type 5 anims')
    if POKEDEX_RECORDS:                        # (phase 2, off: the Pokédex area page untested with Hoenn records)
        _put(ov, LOADER, bytes.fromhex('5520' '0021' '0022'), bytes([0x54, 0x20, NEW_FILE, 0x21, 0x00, 0x22]),
             'records loader')                 # func_ov144_0219f718: movs r0, #0x54; movs r1, #21; movs r2, #0
    fe = find_entry_code(lay)
    _put(ov, FIND_ENTRY[0], None, fe + bytes(FIND_ENTRY[1] - FIND_ENTRY[0] - len(fe)), 'find entry')
    if os.path.islink(path): os.unlink(path)
    open(path + '.tmp', 'wb').write(ov); os.replace(path + '.tmp', path)
    fly = apply_littleroot_fly(code) if LITTLEROOT_FLY else ''
    fly += apply_home_teleport(code) if HOME_TELEPORT else ''
    return f"ov144: {lay['n']} entries, locations from a/0/8/4 #{NEW_FILE}, zone table lookup, route refine, view mode for scripts" + fly
