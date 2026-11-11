"""Post-game wild tables (postgame_dex, 2026-11-09; notes/POSTGAME.md "Post-game dex completion"). After the Champion
(FLAG_SYS_GAME_CLEAR = Black 2's game-clear flag 2400) a zone whose encounter file has a post-game twin reads the twin:
the decomp's src/hoennb2/resident/postgame_enc.c, called by EncData_Load (ov012 field_encount_st.c) in place of
GetZoneEncID. The twins themselves are ordinary a/1/2/7 files (src/encounters[/version]/NNNN_pg_*.s, written by
converter/gen_postgame_encounters.py from data/hoenn_postgame_encounters.json; the encounters patch installs them).
This patch fills gHoennB2PostgameEnc in the resident pool:
  u16 pairCount, u16 cellCount; {u16 file, u16 twin} x pairCount; {u16 species, u8 cell, u8 bits} x cellCount
- pairs: the version's maps' installed file -> their twin (keyed by file, so every zone of a map, e.g. Route 111's desert
  zones, follows; one file may serve several zones);
- cells: the Pokédex area page after the flag (HoennB2_PostgameHabitat, called by hoenn_pokedex's ITCM HabitatRead): for
  every (species, habitat index) whose post-game value differs from the habitat file's, the post-game value (Black 2's
  encounter-group bits of every zone of that cell, with the twins), the way hoenn_pokedex.habitat() computes them.
build_rom.py adds this patch itself (after hoenn_pokedex) when our C is on; with it off there is no post-game swap.
Checks (the build stops): every twin id is used by no zone header of this build (a Hoenn zone pointing at it would get
the twin before the Champion) and has its file's original size; each map's file is the one data/hoenn_encounters.json
names.
    python3 postgame_encounters.py      the version's pairs (HOENN_VERSION=...), without a build
"""
import json, os, struct, sys
import importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'converter'))
import b2decomp, resident, version  # noqa: E402
import gen_postgame_encounters as GPE  # noqa: E402

DATA = {}                                   # apply() -> apply_code(): pairs, cells


def pairs():
    """[(installed file, twin)] of this version, one per file."""
    files, maps = GPE.load()
    reg = GPE.registry()
    out = {}
    for m in maps:
        f, t = reg[m], files[m]
        assert out.get(f, t) == t, f'{m}: file {f} has two twins ({out[f]}, {t})'
        out[f] = t
    return sorted(out.items())


def _pokedex():
    spec = importlib.util.spec_from_file_location('hoenn_pokedex_pg', os.path.join(HERE, 'hoenn_pokedex.py'))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


def file_bits(data, dex):
    """{species: habitat bits} of an a/1/2/7 file's first table (hoenn_pokedex.zone_bits' rule)."""
    n = len(data) // dex.ENC_TABLE
    assert n in (1, 4) and len(data) == n * dex.ENC_TABLE, len(data)
    bits = {}
    for k in range(56):
        sp = struct.unpack_from('<H', data, 8 + 4 * k)[0] & 0x7FF
        g = dex.GROUPS[k]
        if g == 6: g = 5                 # (rods_fix) the Old / Good Rod's slots count as fishing, by the fishing rate
        if sp and data[g]: bits[sp] = bits.get(sp, 0) | 1 << g
    return bits


def cells(files, twin_of):
    """[(species, habitat index, post-game bits)] where the area page's value changes after the flag."""
    import narcio, zoneheaders
    dex = _pokedex()
    tm = dex._tm()
    if b'TMAP' not in narcio.load(files, tm.ARC_GFX)[tm.NEW_FILE]:
        return []                        # (no town_map patch in this build: no Hoenn area page to fill)
    f21 = tm.read_file21(files)
    recs, ztab = f21['records'], f21['zone_table']
    rzones = [r[0] for r in recs]
    slot_of = [rzones.index(z) for z in rzones]
    hidden = {dex._species()[s] for s in dex.HIDDEN}
    hoenn_files = set(json.load(open(os.path.join(ROOT, 'data', 'hoenn_encounters.json'))).values())
    headers, _ = zoneheaders.load(files)
    enc = narcio.load(files, dex.ARC_ENC)
    before, after = {}, {}
    for z, h in enumerate(headers):
        f = h['encounters']
        if f not in hoenn_files or z >= len(ztab) or ztab[z] == 0xFF: continue
        k = slot_of[ztab[z]]
        for out, fid in ((before, f), (after, twin_of.get(f, f))):
            for sp, b in file_bits(enc[fid], dex).items():
                if sp not in hidden: out[(sp, k)] = out.get((sp, k), 0) | b
    return sorted((sp, k, after.get((sp, k), 0)) for sp, k in set(before) | set(after)
                  if before.get((sp, k), 0) != after.get((sp, k), 0))


def apply(files):
    import narcio, zoneheaders
    DATA.clear()
    if not b2decomp.c_on():
        return 'postgame_encounters: our C is off (no post-game tables)'
    ps = pairs()
    headers, _ = zoneheaders.load(files)
    used = {h['encounters'] for h in headers}
    sizes = [len(x) for x in narcio.load(os.path.join(b2decomp.BASE, 'build', 'b2_us', 'files'), 127)]
    enc = narcio.load(files, 127)
    for f, t in ps:
        assert t not in used, f'postgame_encounters: a zone header uses twin file {t} (it would play before the Champion)'
        assert len(enc[t]) == sizes[t], f'postgame_encounters: twin {t} is {len(enc[t])} B, not {sizes[t]}'
        assert f in used, f'postgame_encounters: no zone uses file {f}'
    cs = cells(files, dict(ps))
    DATA.update(pairs=ps, cells=cs)
    return f'postgame_encounters: {len(ps)} twins {ps}; {len(cs)} area-page cells'


def apply_code(code):
    if not DATA:
        return 'postgame_encounters: nothing to install'
    import decomp_build
    slot = decomp_build.symbol('gHoennB2PostgameEnc', code)
    if slot is None:
        raise SystemExit('postgame_encounters: the decomp has no gHoennB2PostgameEnc (src/hoennb2/resident/postgame_enc.c)')
    ps, cs = DATA['pairs'], DATA['cells']

    def build(base):
        blob = struct.pack('<HH', len(ps), len(cs)) + b''.join(struct.pack('<HH', f, t) for f, t in ps)
        blob += b''.join(struct.pack('<HBB', sp, k, b) for sp, k, b in cs)
        return blob, {}
    base, end, _ = resident.install(code, build)
    assert resident.read(code, slot, 4) == bytes(4), f'gHoennB2PostgameEnc at {slot:#x}: not NULL'
    resident.write(code, slot, struct.pack('<I', base))
    return f'postgame_encounters: {len(ps)} pairs + {len(cs)} cells, {end - base} B at {base:#x}'


if __name__ == '__main__':
    print(version.NAME, pairs())
