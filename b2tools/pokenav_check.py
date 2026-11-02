"""Offline checks of the PokéNav's data, for each version (notes/POKENAV.md):

    python3 b2tools/pokenav_check.py FILES_DIR      FILES_DIR/a/0/0/2 is a system text archive to work on a copy of
    python3 b2tools/pokenav_check.py --built BUILD  a finished build's own two files (BUILD/files, BUILD/code)

The two files through patches/pokenav.py's apply: the file unpacks to what the C reads (every offset, map, piece and palette in
bounds), each contact's lines exist, registered and rematch ids are in range, Emerald's rows are all there, every line fits its
place on screen by length, and the archive's reserve holds them."""
import json, os, shutil, struct, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, 'patches'))
import b2decomp, narcio, title_art, version, pokenav_art  # noqa: E402
import pokenav  # noqa: E402

RESERVE = 512 << 10
PIECE_SIZE, CONTACT_SIZE = 8, 12
MAP_BYTES = pokenav_art.W * pokenav_art.H * 2


def check(files):
    """The two files as patches/pokenav.py would make them for this version, on a copy of files' archive."""
    with tempfile.TemporaryDirectory(dir=os.path.dirname(os.path.abspath(files))) as t:
        os.makedirs(os.path.join(t, 'a', '0', '0'))
        shutil.copyfile(os.path.join(files, 'a', '0', '0', '2'), os.path.join(t, 'a', '0', '0', '2'))
        before = os.path.getsize(os.path.join(t, 'a', '0', '0', '2'))
        report = pokenav.apply(t)
        entries = narcio.load(t, 2)
        grew = os.path.getsize(os.path.join(t, 'a', '0', '0', '2')) - before
    problems = check_files(entries[pokenav.STATE['first']:pokenav.STATE['text']], entries[pokenav.STATE['text']])
    return problems, f'{report}; the archive +{grew} B'


def check_built(build):
    """A finished build's own files (BUILD/files, BUILD/code): the numbers in the overlay's gHoennB2Pokenav, what they hold,
    the file's padding."""
    import decomp_build
    code = os.path.join(build, 'code')
    config = decomp_build.symbol('gHoennB2Pokenav', code)
    import resident
    first, text = struct.unpack('<HH', resident.read(code, config, 4))
    files = os.path.join(build, 'files')
    entries = narcio.load(files, 2)
    problems = check_files(entries[first:text], entries[text])
    path = os.path.join(files, 'a', '0', '0', '2')
    d = open(path, 'rb').read()
    off = struct.unpack_from('<H', d, 0xC)[0]
    n = struct.unpack_from('<I', d, off + 8)[0]
    used = max(struct.unpack_from('<II', d, off + 12 + 8 * i)[1] for i in range(n))
    o2 = off + struct.unpack_from('<I', d, off + 4)[0]
    o3 = o2 + struct.unpack_from('<I', d, o2 + 4)[0]
    free = struct.unpack_from('<I', d, o3 + 4)[0] - 8 - used
    return problems, (f'files {first}-{text} ({sum(map(len, entries[first:text + 1]))} B) of {len(entries)}; a/0/0/2 '
                      f'{len(d)} B, {free} B free in its reserve')


def check_files(art, text):
    problems = []
    n_views = len(pokenav_art.VIEWS)
    if len(art) != n_views + 1: problems.append(f'{len(art)} art files')
    sys.path.insert(0, os.path.join(b2decomp.SRC, 'tools', 'scripts'))
    import text_data
    lines = text_data.unpack_file(text).split('\n')[:-1]
    for i, name in enumerate(pokenav_art.VIEWS):
        d = title_art.lz10_decompress(art[i])
        magic, view, tiles, tiles_ofs, pal, m0, m1, m2, table, n = struct.unpack_from('<IHHII3III', d, 0)
        if magic != pokenav_art.MAGIC or view != i: problems.append(f'{name}: magic {magic:#x} view {view}')
        if not 0 < tiles or tiles + pokenav_art.WINDOW_TILES[name] > pokenav_art.CHAR_LIMIT: problems.append(f'{name}: {tiles} tiles')
        if tiles_ofs + tiles * 32 > len(d) or pal + 0x200 > len(d) or pal & 1 or table & 3: problems.append(f'{name}: offsets')
        for m in (m0, m1, m2):
            if m and m + MAP_BYTES > len(d): problems.append(f'{name}: map')
            if m and any((e & 0x3FF) >= tiles for e in struct.unpack_from(f'<{MAP_BYTES // 2}H', d, m)):
                problems.append(f'{name}: map tile')
        need = 5 + {'menu': 5, 'ribbon_grid': 24}.get(name, 0)
        if n != need: problems.append(f'{name}: {n} pieces, the C expects {need}')
        for k in range(n):
            ofs, w, h, _ = struct.unpack_from('<IBBH', d, table + k * PIECE_SIZE)
            if w and ofs + 2 * w * h > len(d): problems.append(f'{name} piece {k}')
            if w and any((e & 0x3FF) >= tiles for e in struct.unpack_from(f'<{w * h}H', d, ofs)):
                problems.append(f'{name} piece {k}: tile')
    d = title_art.lz10_decompress(art[n_views])
    magic, ver, count, contacts, ribbons = struct.unpack_from('<IHHII', d, 0)
    if magic != pokenav_art.MAGIC: problems.append(f'data magic {magic:#x}')
    if ver != {None: 0, 'ruby': 1, 'emerald': 2}[version.OVERLAY]: problems.append(f'version {ver}')
    if contacts & 3 or contacts != 40: problems.append(f'contacts at {contacts}')
    rows = set()
    for i in range(count):
        flag, trainer, base, rm, gym, row, sex, hascheck = struct.unpack_from('<HHHHBBBB', d, contacts + i * CONTACT_SIZE)
        if base + 7 > len(lines): problems.append(f'contact {i}: text {base}')
        if trainer != 0xFFFF and trainer >= 814: problems.append(f'contact {i}: trainer {trainer}')
        if flag == 0xFFFF and trainer == 0xFFFF: problems.append(f'contact {i}: always registered')
        if sex not in (0, 1, 2): problems.append(f'contact {i}: sex')
        if row != 0xFF:
            rows.add(row)
            if rm == 0xFFFF or rm >= 814: problems.append(f'contact {i}: rematch id')
        name, cls, place, *rest = lines[base:base + 7]
        if not name: problems.append(f'contact {i}: no name')
        for s in [name, cls] + rest:
            if len(s) > 30: problems.append(f'contact {i}: too long for its place: {s!r}')
    if version.OVERLAY == 'emerald':
        n = len(json.load(open(os.path.join(pokenav_art.ROOT, 'data', 'emerald', 'hoenn_rematch.json')))['rows'])
        if rows != set(range(n)): problems.append(f'rematch rows: {sorted(set(range(n)) - rows)} missing')
    elif rows: problems.append('Sapphire and Ruby have no rematches')
    if count != (85 if version.OVERLAY == 'emerald' else 56): problems.append(f'{count} contacts')
    for i in range(80):
        p, ln = struct.unpack_from('<BB', d, ribbons + 2 * i)
        if p >= 12 or not 9 <= ln <= 13: problems.append(f'ribbon {i}: {p}, {ln}')
    for i, s in enumerate(lines[:7]):
        if len(s) > 36: problems.append(f'line {i} too long: {s!r}')
    return problems


if __name__ == '__main__':
    problems, summary = check_built(sys.argv[2]) if sys.argv[1] == '--built' else check(sys.argv[1])
    print(f'{version.VERSION}: {summary}')
    print('\n'.join(problems) if problems else 'OK')
    sys.exit(1 if problems else 0)
