"""The PokéNav's data (notes/POKENAV.md): its code is C in the decomp (src/hoennb2/pokenav/, overlay 345, and
src/hoennb2/resident/pokenav_event.c). This puts the version's art and text in the ROM and tells the code where.

apply(files): appends to a/0/0/2 (the system text archive; its RESERVE has the room, build_rom.pad_archives checks) a file per view of
  the art, the contact data (b2tools/pokenav_art.py, LZ-compressed) and the text. Their numbers are whatever the archive's count is
  now, so other patches may append too. Keep this patch after `text`, which rebuilds the archive from sources and whose
  fixed_slots requires Black 2's 495 files.
apply_code(code): writes the numbers in gHoennB2Pokenav (the resident section), and adds the overlay to the ROM's overlay table unless
  decomp_build already has. With HOENN_CODE=base, or a decomp without the app, it does nothing and the item stays Black 2's
  Xtransceiver: the files in a/0/0/2 are then unused.
"""
import os, re, struct, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import b2decomp, narcio, pokenav_art  # noqa: E402

OVERLAY = 345
TEXT_ARC = 2
STATE = {}


def _pack_text(lines):
    sys.path.insert(0, os.path.join(b2decomp.SRC, 'tools', 'scripts'))
    import text_data
    return text_data.pack_file(''.join(l + '\n' for l in lines))


def apply(files):
    import title_art
    views, data, lines, rep = pokenav_art.file_bytes()
    art = [title_art.lz10_compress(f) for f in views + [data]]
    text = _pack_text(lines)
    entries = narcio.load(files, TEXT_ARC)
    STATE['first'], STATE['text'] = len(entries), len(entries) + len(art)
    entries += art + [text]
    narcio.save(files, TEXT_ARC, entries)
    return (f'pokenav: a/0/0/2 files {STATE["first"]}-{STATE["text"]}: art and data {sum(map(len, art))} B, text {len(text)} B '
            f'({rep["lines"]} lines); {rep["contacts"]} contacts; views (tiles, window tiles, palette lines, file B) {rep["views"]}')


def _sym(name, code):
    import decomp_build
    return decomp_build.symbol(name, code)


def apply_code(code):
    n = OVERLAY
    config = _sym('gHoennB2Pokenav', code)
    start = _sym(f'OV{n}_TEXT_START', code)
    if config is None or start is None:
        return 'pokenav: this decomp has no overlay 345 (HOENN_CODE=base?): the item stays the Xtransceiver'
    assert 'first' in STATE, 'pokenav: apply_code without apply'
    path = os.path.join(code, f'arm9_ov{n:03d}.bin')
    if not os.path.exists(path):
        raise SystemExit(f'pokenav: {path} is not there (the decomp build makes it)')
    import resident
    assert resident.read(code, config, 4) == b'\xff\xff\xff\xff', 'pokenav: gHoennB2Pokenav is not the C\'s'
    resident.write(code, config, struct.pack('<HH', STATE['first'], STATE['text']))
    yml = os.path.join(code, 'arm9_overlays.yaml')
    text = open(yml).read()
    if f'id: {n}\n' in text:
        return f'pokenav: overlay {n}, its table entry is there; files {STATE["first"]}-{STATE["text"]}'
    bss, end = _sym(f'OV{n}_BSS_START', code), _sym(f'OV{n}_BSS_END', code)
    ctor, ctor_end = _sym(f'OV{n}_CTOR_START', code), _sym(f'OV{n}_CTOR_END', code)
    assert os.path.getsize(path) == bss - start, f'{path}: {os.path.getsize(path)} B, the link says {bss - start}'
    entry = (f'  - id: {n}\n    base_address: {start}\n    code_size: {bss - start}\n    bss_size: {end - bss}\n'
             f'    ctor_start: {ctor}\n    ctor_end: {ctor_end}\n    file_id: {n}\n'
             f'    compressed: false\n    signed: false\n    file_name: {path}\n')
    # In id order: the table is indexed by id, so the ids must be contiguous
    rows = re.split(r'(?m)^(?=  - id: )', text)
    head, rows = rows[0], rows[1:]
    rows.append(entry)
    rows.sort(key=lambda r: int(re.match(r'  - id: (\d+)', r).group(1)))
    ids = [int(re.match(r'  - id: (\d+)', r).group(1)) for r in rows]
    assert ids == list(range(ids[0], ids[0] + len(ids))), f'pokenav: overlay ids not contiguous: {ids[-5:]}'
    rows = [r.rstrip('\n') + '\n' for r in rows]
    open(yml, 'w').write(head + ''.join(rows))
    return f'pokenav: overlay {n}, {end - start} B at {start:#x}; files {STATE["first"]}-{STATE["text"]}'
