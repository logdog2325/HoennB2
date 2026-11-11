"""The DexNav's data (notes/DEXNAV.md): its code is C in the decomp (src/hoennb2/resident/dexnav.c, always loaded, and
src/hoennb2/dexnav/, overlay 349 in the C-Gear's slot). This puts the version's art and text in the ROM and fills
gHoennB2DexNav (decomp include/hoennb2/dexnav.h HoennB2DexNavConfig) in the resident pool. build_rom.py adds it itself, last,
when our C is on.

apply(files): the screen's text to a/0/0/2 (after `text` and `pokenav`); the three views (b2tools/dexnav_art.py, Omega Ruby
  / Alpha Sapphire's look) and every wild table's snapshot of its Gen 3 map (b2tools/dexnav_snapshots.py), uncompressed,
  at the end of a/0/0/8 (the map chunks' archive has room inside its fixed size: no RESERVE change; files of an earlier
  run, recognised by their magic, are replaced); then b2tools/dexnav_check.py's budgets. The build stops on a zone whose
  table has species but no snapshot, a group with too few places on its own tiles, or a budget missed.
apply_code(code): the config: the text file, the views' and snapshots' first files, the works and the PokéNav's flag
  (src/include/hoenn.h), Route 101's zone, the tutorial's species, scripts and moves, the cave zones (a cave's land group
  shows dust clouds), the save's species order and the encounter file -> snapshot pairs; then overlay 349 in the ROM's
  overlay table, checked to end before the field gimmicks' overlays.

The save's order (a search-level byte per species in the Dream Radar block's unused bytes, include/save/cygnus_save_control.h):
the Hoenn Pokédex #1-#202, then EXTRAS. Saved bytes follow this order, so it never changes: a new wild species outside the
Hoenn dex is APPENDED to EXTRAS (the build stops on one that is missing). 230 at most.
"""
import glob, json, os, re, struct, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)
import b2decomp, narcio, resident, version  # noqa: E402

OVERLAY = 349
TEXT_ARC = 2
CHUNK_ARC = 8                   # a/0/0/8 (ARCID_MAP_TERRAIN): the views and snapshots, after the map chunks
SAVE_MAX = 230                  # DreamRadarSave.padding09: a layout byte, then the levels
# Wild species outside the Hoenn dex, in the order the save keeps them (APPEND ONLY): Emerald's Safari Zone and every
# version's Altering Cave
EXTRAS = [132, 163, 165, 167, 179, 190, 191, 194, 195, 204, 207, 209, 213, 216, 228, 234, 235, 241]
TUTORIAL_MAP = 'Route101'
TUTORIAL_SPECIES = 'SPECIES_POOCHYENA'
TUTORIAL_MOVES = ['MOVE_THUNDER_FANG', 'MOVE_ICE_FANG', 'MOVE_FIRE_FANG']   # Poochyena's egg moves (a/1/2/4), ORAS's tutorial
TUTORIAL_SCRIPT, TUTORIAL_END_SCRIPT = 4, 5     # src/field_scripts/0634_route_101.s (scenes/Route101_DexNav.inc)
SLOT_END = 'OV089_TEXT_START'   # the field gimmicks' overlays start where the C-Gear's slot ends
STATE = {}


def _pack_text(lines):
    sys.path.insert(0, os.path.join(b2decomp.SRC, 'tools', 'scripts'))
    import text_data
    return text_data.pack_file(''.join(l + '\n' for l in lines))


def apply(files):
    import dexnav_art, dexnav_check, dexnav_snapshots, zoneheaders
    if not b2decomp.c_on():
        return 'dexnav: our C is off'
    text = _pack_text(dexnav_art.text_lines())
    entries = narcio.load(files, TEXT_ARC)
    STATE['text'] = len(entries)
    entries.append(text)
    narcio.save(files, TEXT_ARC, entries)
    # the views and the snapshots
    views = {n: dexnav_art.pack_view(n) for n in dexnav_art.VIEWS}
    counts = dexnav_snapshots.counts_built(files)
    snaps = dexnav_snapshots.build(1 + views['area']['tiles'], views['area']['lines'], counts)
    report, problems = dexnav_check.check(views, snaps, counts)
    if problems:
        raise SystemExit('dexnav: ' + '; '.join(problems))
    snap_chars = max(r['tiles'] for _, _, r in snaps)
    have = {f for f, _, _ in snaps if f is not None}
    headers, _ = zoneheaders.load(files)
    missing = sorted({(z, h['encounters']) for z, h in enumerate(headers) if h['encounters'] in counts and
                      any(counts[h['encounters']]) and h['encounters'] not in have})
    if missing:
        raise SystemExit(f'dexnav: zones whose wild table has no snapshot (zone, file): {missing}')
    chunks = narcio.load(files, CHUNK_ARC)
    while chunks and chunks[-1][:4] in (b'DNV1', b'DNS1'):      # (an earlier run's)
        chunks.pop()
    STATE['view'] = len(chunks)
    for n in dexnav_art.VIEWS:
        v = views[n]
        chunks.append(dexnav_art.view_file(v, 1 + v['tiles'] + (snap_chars if n == 'area' else 0)))
    STATE['snap'] = len(chunks)
    STATE['pairs'] = []
    for i, (f, data, _) in enumerate(snaps):
        chunks.append(data)
        if f is not None:
            STATE['pairs'].append((f, i))
    narcio.save(files, CHUNK_ARC, chunks)
    size = sum(len(c) for c in chunks[STATE['view']:])
    return (f'dexnav: a/0/0/2 file {STATE["text"]} (text {len(text)} B); a/0/0/8 files {STATE["view"]}-{len(chunks) - 1} '
            f'(3 views, {len(snaps)} snapshots, {size} B); ' + '; '.join(report))


def _defines(path, pattern):
    return {k: int(v, 0) for k, v in re.findall(pattern, open(path).read())}


def _hoenn_h():
    return _defines(os.path.join(ROOT, 'src', 'include', 'hoenn.h'), r'#define (\w+)\s+(0x[0-9A-Fa-f]+|\d+)')


def _generated(name):
    return _defines(os.path.join(b2decomp.SRC, 'build', 'include', 'generated', 'constants', name + '.h'),
                    r'#define (\w+)\s+(\d+)')


def save_order():
    """National numbers in the save's order (the Hoenn dex, then EXTRAS); the build stops on a wild species it lacks."""
    import hoenn_dex
    order = hoenn_dex.hoenn_order() + EXTRAS
    assert len(set(order)) == len(order) and len(order) <= SAVE_MAX, len(order)
    species = _generated('species')
    wild = set()
    for p in version.overlay(os.path.join(ROOT, 'src', 'encounters'), '*.s'):
        group = None
        for line in open(p):
            line = line.strip()
            m = re.match(r'(\w+)Encounters$', line)
            if m:
                group = m.group(1)
                continue
            m = re.match(r'Encounter (SPECIES_\w+),', line)
            if m and group in ('Grass', 'Surf'):
                wild.add(species[m.group(1)])
    missing = sorted(wild - set(order))
    assert not missing, f'dexnav: wild species {missing} are not in the save\'s order: append them to EXTRAS'
    return order


def cave_zones():
    rooms = version.load_json(os.path.join(ROOT, 'data', 'hoenn_interiors.json'))['rooms']
    return sorted({r['zone'] for r in rooms.values() if r.get('status') == 'cave' and 'zone' in r})


def _sym(name, code):
    import decomp_build
    return decomp_build.symbol(name, code)


def apply_code(code):
    if not b2decomp.c_on():
        return 'dexnav: our C is off (Black 2\'s NoGear screen)'
    slot = _sym('gHoennB2DexNav', code)
    start = _sym(f'OV{OVERLAY}_TEXT_START', code)
    if slot is None or start is None:
        raise SystemExit('dexnav: the decomp has no DexNav (src/hoennb2/resident/dexnav.c, overlay 349)')
    assert 'view' in STATE, 'dexnav: apply_code without apply'
    h = _hoenn_h()
    moves = _generated('moves')
    species = _generated('species')
    zone = version.load_json(os.path.join(ROOT, 'data', 'hoenn_zones.json'))['maps'][TUTORIAL_MAP]['zone']
    caves = cave_zones()
    order = save_order()

    pairs = STATE['pairs']

    def build(base):
        head = struct.pack('<10H3H2H3H', STATE['view'], STATE['text'], h['VAR_DEXNAV_STATE'], h['VAR_DEXNAV_CHAIN'],
                           h['VAR_DEXNAV_CHAIN_SPECIES'], h['FLAG_SYS_POKENAV_GET'], zone, species[TUTORIAL_SPECIES],
                           TUTORIAL_SCRIPT, TUTORIAL_END_SCRIPT, *[moves[m] for m in TUTORIAL_MOVES], len(caves),
                           len(order), STATE['snap'], len(pairs), 0)
        flat = [v for p in pairs for v in p]
        return head + struct.pack(f'<{len(caves) + len(order) + len(flat)}H', *caves, *order, *flat), {}

    base, end, _ = resident.install(code, build)
    assert resident.read(code, slot, 4) == bytes(4), f'gHoennB2DexNav at {slot:#x}: not NULL'
    resident.write(code, slot, struct.pack('<I', base))

    # Overlay 349 in the ROM's overlay table (as patches/pokenav.py puts 345), in id order
    n = OVERLAY
    path = os.path.join(code, f'arm9_ov{n:03d}.bin')
    bss, bss_end = _sym(f'OV{n}_BSS_START', code), _sym(f'OV{n}_BSS_END', code)
    limit = _sym(SLOT_END, code)
    assert limit is None or bss_end <= limit, \
        f'dexnav: overlay {n} ends at {bss_end:#x}, past the C-Gear slot ({SLOT_END} {limit:#x})'
    assert os.path.getsize(path) == bss - start, f'{path}: {os.path.getsize(path)} B, the link says {bss - start}'
    yml = os.path.join(code, 'arm9_overlays.yaml')
    text = open(yml).read()
    if f'id: {n}\n' not in text:
        ctor, ctor_end = _sym(f'OV{n}_CTOR_START', code), _sym(f'OV{n}_CTOR_END', code)
        entry = (f'  - id: {n}\n    base_address: {start}\n    code_size: {bss - start}\n    bss_size: {bss_end - bss}\n'
                 f'    ctor_start: {ctor}\n    ctor_end: {ctor_end}\n    file_id: {n}\n'
                 f'    compressed: false\n    signed: false\n    file_name: {path}\n')
        rows = re.split(r'(?m)^(?=  - id: )', text)
        head, rows = rows[0], rows[1:] + [entry]
        rows.sort(key=lambda r: int(re.match(r'  - id: (\d+)', r).group(1)))
        ids = [int(re.match(r'  - id: (\d+)', r).group(1)) for r in rows]
        assert ids == list(range(ids[0], ids[0] + len(ids))), f'dexnav: overlay ids not contiguous: {ids[-6:]}'
        open(yml, 'w').write(head + ''.join(r.rstrip('\n') + '\n' for r in rows))
    return (f'dexnav: config {end - base} B at {base:#x} ({len(caves)} cave zones, {len(order)} species in the save\'s '
            f'order, {len(pairs)} snapshots); overlay {n}, {bss_end - start} B at {start:#x} (the C-Gear slot ends {limit or 0:#x})')


if __name__ == '__main__':
    print(version.NAME, len(save_order()), 'species in the save order;', len(cave_zones()), 'cave zones')
