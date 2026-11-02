"""Gen 3's Pokémon Contests (notes/CONTESTS.md): the data the decomp's C reads, for the build's version.

apply(files):
- archive 271 (a/2/7/1: Pokéstar Studios', read only by Pokéstar's overlays; no Hoenn place reaches the studios) becomes the
  Contests' pictures, moves, opponents, AI scripts, text, the Blender's and the Case's data (b2tools/contest_data.py, in
  the order of the decomp's include/hoennb2/contest.h). build_rom keeps the archive at its size (RESERVE).
- item 449 (the Pokéblock Case, Black 2's Poffin Case) gets the Bicycle's Use in the Bag: its field function.
apply_code(code): overlays 346-347 (and any other of ours the link has and the table lacks) into the ROM's overlay table.
"""
import os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import contest_data, narcio, version  # noqa: E402

ARC = 271
ITEM_ARC = 24
ITEM_POKEBLOCK_CASE = 449
ITEM_BICYCLE = 450
ITEM_FIELD_FUNC = 0xA      # include/pml/item.h ItemData.fieldFunc
OVERLAYS = range(345, 349) # ours after the resident section (the decomp's tools/hoennb2/link_overlays.py APP_OVERLAYS)


def apply(files):
    members = contest_data.members(version.is_emerald())
    narcio.save(files, ARC, members)
    items = narcio.load(files, ITEM_ARC)
    rec = bytearray(items[ITEM_POKEBLOCK_CASE])
    rec[ITEM_FIELD_FUNC] = items[ITEM_BICYCLE][ITEM_FIELD_FUNC]
    items[ITEM_POKEBLOCK_CASE] = bytes(rec)
    narcio.save(files, ITEM_ARC, items)
    return f'contests: archive {ARC} = {len(members)} members, {sum(map(len, members))} B ({version.VERSION}); item 449 usable in the Bag'


def _sym(name, code):
    import decomp_build
    return decomp_build.symbol(name, code)


def apply_code(code):
    yml = os.path.join(code, 'arm9_overlays.yaml')
    text = open(yml).read()
    added = []
    rows = re.split(r'(?m)^(?=  - id: )', text)
    head, rows = rows[0], rows[1:]
    have = {int(re.match(r'  - id: (\d+)', r).group(1)) for r in rows}
    for n in OVERLAYS:
        start = _sym(f'OV{n}_TEXT_START', code)
        if start is None or n in have:
            continue
        path = os.path.join(code, f'arm9_ov{n:03d}.bin')
        bss, end = _sym(f'OV{n}_BSS_START', code), _sym(f'OV{n}_BSS_END', code)
        ctor, ctor_end = _sym(f'OV{n}_CTOR_START', code), _sym(f'OV{n}_CTOR_END', code)
        assert os.path.getsize(path) == bss - start, f'{path}: {os.path.getsize(path)} B, the link says {bss - start}'
        rows.append(f'  - id: {n}\n    base_address: {start}\n    code_size: {bss - start}\n    bss_size: {end - bss}\n'
                    f'    ctor_start: {ctor}\n    ctor_end: {ctor_end}\n    file_id: {n}\n'
                    f'    compressed: false\n    signed: false\n    file_name: {path}\n')
        added.append(f'{n} ({end - start} B at {start:#x})')
    if not added:
        return 'contests: overlays already in the table, or this decomp has none (HOENN_CODE=base?)'
    rows.sort(key=lambda r: int(re.match(r'  - id: (\d+)', r).group(1)))
    ids = [int(re.match(r'  - id: (\d+)', r).group(1)) for r in rows]
    assert ids == list(range(ids[0], ids[0] + len(ids))), f'contests: overlay ids not contiguous: {ids[-6:]}'
    if os.path.islink(yml):
        os.unlink(yml)
    open(yml, 'w').write(head + ''.join(r.rstrip('\n') + '\n' for r in rows))
    return 'contests: overlays ' + ', '.join(added)
