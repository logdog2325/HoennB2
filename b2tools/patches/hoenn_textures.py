"""Hoenn's map texture set: Black 2's area 2 summer set (a/0/1/4 entry 3, the one our terrain was built from) plus
every texture the terrain modules (b2tools/terrain/*.py) take from other Black 2 sets, merged byte for byte by
b2tools/nsbtx.py (no re-encoding). Prints the size against the ~200 KB budget for map + building textures
(notes/RESEARCH_WORLD.md). The same for area 2's spring, autumn and winter sets (seasonal_sets): the season is summer
unless the player chose Black 2's seasons (Birch's fifth question, patches/hoenn_season.py, notes/SEASONS.md)."""
import os, sys
import narcio
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..'))
import nsbtx, terrain

HOENN_SET = 3
HOENN_AREA = 2                    # the overworld's area (world.json "area"): records 2-5 = spring, summer, autumn, winter
SEASON_KEEP = {'c8k_grass01ax'}   # the ash grass (terrain/ground.py) keeps the same art in every season
SEASONS = ((0, 'spring'), (2, 'autumn'), (3, 'winter'))

def ash_grey(data):
    """The winter art's snow as volcanic ash (user 2026-10-17: "turning the snow grey ... so it looks like ash"): every
    bluish-white / pale-blue palette colour (snow and its blue shadows; b >= r + 8, or a near-white) becomes a warm grey
    of 52% of its luminance (78% and 60% still read too light in daylight, user tests); greens (grass, leaves) and browns (bark, rock) keep their colours."""
    import struct
    out = bytearray(data)
    for i in range(0, len(out) - 1, 2):
        c = struct.unpack_from('<H', out, i)[0]
        r, g, b = (c & 31) * 255 // 31, ((c >> 5) & 31) * 255 // 31, ((c >> 10) & 31) * 255 // 31
        white = min(r, g, b) >= 200 and max(r, g, b) - min(r, g, b) <= 40
        if not (white or b >= r + 8 and b >= g - 8):
            continue
        v = (0.30 * r + 0.59 * g + 0.11 * b) * 0.52
        rr, gg, bb = (max(0, min(255, int(round(x)))) for x in (v + 4, v, v - 6))
        struct.pack_into('<H', out, i, (rr >> 3) | ((gg >> 3) << 5) | ((bb >> 3) << 10) | (c & 0x8000))
    return bytes(out)

def apply(files):
    sets = narcio.load(files, 14)
    adds = []
    bsets = []
    mods = []                                    # (src, name, palette, Black 2 set) of the terrain modules' textures
    for f in terrain.modules():
        for name, ts in getattr(f, 'TEXTURES', {}).items():
            if not isinstance(ts, int):          # 'ext<N>': exterior building texture set a/1/7/4 N (terrain/ship.py)
                bsets = bsets or narcio.load(files, 174)
            src = sets[ts] if isinstance(ts, int) else bsets[int(ts[3:])]
            pal = getattr(f, 'PALETTES', {}).get(name, name + '_pl')
            adds.append((src, name, pal if pal in {n for n, _ in nsbtx._parse(src)['pals']} else None))
            mods.append(adds[-1] + (ts,))
    # Sapphire's ash drawn with Black 2's snowy winter art: renamed copies (data/hoenn_ash.json, world.py ash_tiles)
    ap = os.path.join(HERE, '..', '..', 'data', 'hoenn_ash.json')
    if os.path.exists(ap):
        import json
        ash = json.load(open(ap))
        grey = ash_grey if ash.get('grey') else None
        for new, (ts, name) in ash.get('textures', {}).items():
            src = sets[ts]
            pal = name + '_pl' if name + '_pl' in {n for n, _ in nsbtx._parse(src)['pals']} else None
            adds.append((src, name, pal, new, new + '_pl' if pal else None, grey))
    if not adds: return 'no terrain module textures'
    before = len(sets[HOENN_SET])
    sets[HOENN_SET] = nsbtx.merge(sets[HOENN_SET], adds)
    pack = len(narcio.load(files, 174)[0])
    seasons = seasonal_sets(files, sets, mods, adds[len(mods):], pack)
    decals = seasonal_decals(files, sets, pack)
    narcio.save(files, 14, sets)
    return (f'{len(adds)} textures added to set {HOENN_SET}: {before} -> {len(sets[HOENN_SET])} B; with building '
            f'textures {len(sets[HOENN_SET]) + pack} B of ~200 KB; ' + seasons + '; ' + decals + '; ' + autumn_leaves(files))

def season_source(raw, load, ts, name, pal, season):
    """The Black 2 map set to take texture `name` (palette `pal`) from for `season` when it comes from set `ts` in
    summer: the same Black 2 area's set for that season (area records 2..0x119 come in groups of four, spring to
    winter: AreaData_HasSeasons) when it has the texture with the same size (and the palette), else ts. raw = a/0/1/3,
    load(i) = set i's bytes."""
    import struct
    tex = lambda a: struct.unpack_from('<H', raw, a * 10 + 2)[0]
    rs = [r for r in range(2, 0x11a) if tex(r) == ts]
    if not rs: return ts
    alt = tex(rs[0] - (rs[0] - 2) % 4 + season)
    A, S = nsbtx._parse(load(alt)), nsbtx._parse(load(ts))
    at, st = dict(A['texs']).get(name), dict(S['texs']).get(name)
    dims = lambda params: (params >> 20) & 0x3F                       # width and height bits
    if at and st and dims(at[0]) == dims(st[0]) and (pal is None or pal in {n for n, _ in A['pals']}):
        return alt
    return ts

def seasonal_sets(files, sets, mods, ash_adds, pack):
    """Hoenn's textures in area 2's spring, autumn and winter sets too (seasons_study 2026-10-18, user-tested; always
    built since Birch's seasons question). The game loads the area's record for the season (AreaData_Create: area id
    + season; area 2 = sets 2, 3, 4, 5), and a chunk binds its textures by name from that set (a missing one draws flat
    white), so each of the three gets every texture of the summer set: the names Black 2's set already has keep
    Black 2's art for that season (its autumn leaves, its pale winter grass...); a texture a terrain module copies
    from another Black 2 area's set comes from that area's set for the same season when it has it with the same size
    (season_source; only Route 7's tall grass differs: Humilau's palms, Route 4's sand, the sea and cliff textures are
    the same in all four), else the summer one; the ash copies (data/hoenn_ash.json) and SEASON_KEEP stay the same all
    year. The building textures (pack 0) are one set for all four seasons already (records 2-5 all name pack 0)."""
    import struct
    raw = open(os.path.join(files, 'a', '0', '1', '3'), 'rb').read()
    tex = lambda a: struct.unpack_from('<H', raw, a * 10 + 2)[0]
    assert tex(HOENN_AREA + 1) == HOENN_SET, f'area {HOENN_AREA} summer is set {tex(HOENN_AREA + 1)}, not {HOENN_SET}'
    summer = nsbtx._parse(sets[HOENN_SET])
    want = {n for n, _ in summer['texs']}
    out = []
    for season, label in SEASONS:
        adds, own = [], 0
        for src, name, pal, ts in mods:
            if isinstance(ts, int) and name not in SEASON_KEEP:
                alt = season_source(raw, lambda i: sets[i], ts, name, pal, season)
                if alt != ts:
                    A, S = nsbtx._parse(sets[alt]), nsbtx._parse(src)
                    own += ts != HOENN_SET and nsbtx._tex_bytes(A, dict(A['texs'])[name][0]) != \
                        nsbtx._tex_bytes(S, dict(S['texs'])[name][0])
                    src = sets[alt]
            adds.append((src, name, pal))
        ts_out = tex(HOENN_AREA + season)
        before = len(sets[ts_out])
        sets[ts_out] = nsbtx.merge(sets[ts_out], adds + list(ash_adds))
        missing = want - {n for n, _ in nsbtx._parse(sets[ts_out])['texs']}
        assert not missing, f'{label} set {ts_out} lacks {sorted(missing)}'
        out.append(f'{label} set {ts_out}: {before} -> {len(sets[ts_out])} B ({len(sets[ts_out]) + pack} B with '
                   f'buildings; {own} copied textures with their own {label} art)')
    return 'seasons: ' + ', '.join(out)

def clear_source(name, w=8, h=8):
    """A parsed one-texture source for nsbtx.merge: `name`, w x h, 16 colours with colour 0 transparent, every texel
    colour 0 (the DS never draws a clear texel: no colour, no depth), palette `name`_pl all black."""
    import struct
    params = (((w // 8).bit_length() - 1) << 20) | (((h // 8).bit_length() - 1) << 23) | (3 << 26) | (1 << 29)
    return dict(texdata=bytes(w * h // 2), c_data=b'', c_idx=b'', pdata=bytes(32), pflag=0,
                texs=[(name, (params, 0x80000000 | w | (h << 11)))], pals=[(name + '_pl', (0, 0))])

def seasonal_decals(files, sets, pack):
    """terrain/seasons.py SEASONAL (seasons2, 2026-10-20): Black 2's seasonal decal art under Hoenn names in area 2's
    four sets: the season's own (renamed copy, byte for byte, of Black 2's set `ts` texture `src`) in the set of the
    season it shows in, a clear 8x8 stand-in in the other three (the chunks draw these decals all year: they bind by
    name, and a missing name draws flat white). kisetu_yuki (snow) is Black 2's own and already in all four."""
    import struct
    sys.path.insert(0, os.path.join(HERE, '..'))
    from terrain import seasons as S
    raw = open(os.path.join(files, 'a', '0', '1', '3'), 'rb').read()
    tex = lambda a: struct.unpack_from('<H', raw, a * 10 + 2)[0]
    out = []
    for season, label in ((0, 'spring'), (1, 'summer'), (2, 'autumn'), (3, 'winter')):
        ts_out = tex(HOENN_AREA + season)
        adds = []
        for name, (shown, ts, src) in sorted(S.SEASONAL.items()):
            if season == shown:
                b2 = sets[ts]
                pal = src + '_pl' if src + '_pl' in {n for n, _ in nsbtx._parse(b2)['pals']} else None
                adds.append((b2, src, pal, name, name + '_pl' if pal else None))
            else:
                adds.append((clear_source(name), name, name + '_pl'))
        before = len(sets[ts_out])
        sets[ts_out] = nsbtx.merge(sets[ts_out], adds)
        out.append(f'{label} set {ts_out} +{len(sets[ts_out]) - before} B ({len(sets[ts_out]) + pack} B with buildings)')
    return 'seasonal decals ' + ', '.join(sorted(S.SEASONAL)) + ': ' + ', '.join(out)

AUTUMN_SRT = 47                   # Route 20's texture animation (a/0/6/8 file 47): area 2's own (file 0) + its leaves

def autumn_leaves(files):
    """Route 20's falling leaves (terrain/seasons.py ribbons, material _ha01) move by Route 20's texture animation, SRT
    file 47 (its areas 214-217 name it in all four seasons): it has every track of area 2's own SRT file 0 (ponds,
    rivers, shores, sea foam...), byte for byte, except the sea (sea_mizu1, sea_mizu1_1: Route 20's sea scrolls twice as
    fast), plus _ha01 and Route 20's lavender. So file 47's two sea tracks become file 0's (same sizes, in place: no
    archive changes size) and area 2's autumn record (4) names file 47; spring, summer and winter keep file 0, where
    the clear stand-in draws nothing anyway (and with seasons off nothing changes: summer). The warp-only maps keep
    their own (no falling leaves there: terrain/seasons.py AREA2_ONLY)."""
    import struct
    from b2files import arc_path
    p = arc_path(files, 68)
    d = bytearray(open(p, 'rb').read())
    hdr = struct.unpack_from('<H', d, 0xC)[0]
    n = struct.unpack_from('<H', d, hdr + 8)[0]
    spans = [struct.unpack_from('<II', d, hdr + 12 + 8 * i) for i in range(n)]
    gmif = hdr + struct.unpack_from('<I', d, hdr + 4)[0]
    gmif += struct.unpack_from('<I', d, gmif + 4)[0]
    assert d[gmif:gmif + 4] == b'GMIF'
    base = gmif + 8
    def tracks(i):                              # material -> [(info, absolute data offset)] of entry i's one animation
        e0 = base + spans[i][0]
        srt = e0 + struct.unpack_from('<I', d, e0 + 0x10)[0]
        assert d[srt:srt + 4] == b'SRT0'
        (_, ent), = nsbtx._dict(d, srt + 8)
        a = srt + struct.unpack_from('<I', ent, 0)[0]
        return {m: [struct.unpack_from('<II', me, 8 * k) for k in range(5)] for m, me in nsbtx._dict(d, a + 8)}, a
    t0, a0 = tracks(0); t47, a47 = tracks(AUTUMN_SRT)
    assert '_ha01' in t47 and set(t0) <= set(t47), 'SRT 47 is not Route 20\'s'
    fixed = 0
    for mat in ('sea_mizu1', 'sea_mizu1_1'):
        for k in range(5):
            (i0, o0), (i47, o47) = t0[mat][k], t47[mat][k]
            assert i0 == i47, (mat, k, hex(i0), hex(i47))
            if i0 & 0x20000000: continue                       # (a constant: the same value in both)
            size = 240 * (2 if i0 >> 28 & 1 else 4) >> (i0 >> 30 & 3)
            src, dst = a0 + o0, a47 + o47
            if d[dst:dst + size] != d[src:src + size]:
                d[dst:dst + size] = d[src:src + size]; fixed += 1
    if os.path.islink(p): os.unlink(p)
    open(p, 'wb').write(d)
    rp = os.path.join(files, 'a', '0', '1', '3')
    raw = bytearray(open(rp, 'rb').read())
    rec = (HOENN_AREA + 2) * 10
    assert raw[rec + 4] in (0, AUTUMN_SRT), f'area {HOENN_AREA} autumn srt {raw[rec + 4]}'
    raw[rec + 4] = AUTUMN_SRT
    if os.path.islink(rp): os.unlink(rp)
    open(rp, 'wb').write(raw)
    return f'autumn: area {HOENN_AREA} record {HOENN_AREA + 2} srt {AUTUMN_SRT} (Route 20\'s falling leaves; {fixed} sea tracks set to file 0\'s)'
