"""Secret Bases: gimmick 30 in the base zones (a/1/0/2 file 0: u32 zone, u32 gimmick pairs), which loads overlay 348 while
a base's field runs, after zone_effects, which clears the table's entries of Hoenn's zones; overlay 348 into the ROM's overlay
table, after pokenav's and contests' (the ids must be contiguous) (notes/SECRET_BASES.md)."""
import os, re, struct, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import narcio                                               # noqa: E402
import secret_base_data as SB                               # noqa: E402

GIMMICK = 30


def apply(files):
    g = narcio.load(files, 102)
    data = bytearray(g[0])
    size = len(data)
    for z in SB.ZONES:
        data += struct.pack('<II', z, GIMMICK)
    g[0] = bytes(data)
    narcio.save(files, 102, g)
    return f'Secret Bases: gimmick {GIMMICK} in {len(SB.ZONES)} zones (a/1/0/2 {size} -> {len(data)} B)'


OVERLAY = 348


def apply_code(code):
    """Overlay 348 into the ROM's overlay table (as patches/contests.py): the ids must be contiguous, so after theirs."""
    import decomp_build
    n = OVERLAY
    yml = os.path.join(code, 'arm9_overlays.yaml')
    text = open(yml).read()
    rows = re.split(r'(?m)^(?=  - id: )', text)
    head, rows = rows[0], rows[1:]
    if any(int(re.match(r'  - id: (\d+)', r).group(1)) == n for r in rows):
        return f'Secret Bases: overlay {n} is in the table'
    sym = lambda s: decomp_build.symbol(s, code)
    start = sym(f'OV{n}_TEXT_START')
    if start is None:
        return 'Secret Bases: this decomp has no overlay 348 (HOENN_CODE=base?)'
    path = os.path.join(code, f'arm9_ov{n:03d}.bin')
    bss, end = sym(f'OV{n}_BSS_START'), sym(f'OV{n}_BSS_END')
    ctor, ctor_end = sym(f'OV{n}_CTOR_START'), sym(f'OV{n}_CTOR_END')
    assert os.path.getsize(path) == bss - start, f'{path}: {os.path.getsize(path)} B, the link says {bss - start}'
    rows.append(f'  - id: {n}\n    base_address: {start}\n    code_size: {bss - start}\n    bss_size: {end - bss}\n'
                f'    ctor_start: {ctor}\n    ctor_end: {ctor_end}\n    file_id: {n}\n'
                f'    compressed: false\n    signed: false\n    file_name: {path}\n')
    rows.sort(key=lambda r: int(re.match(r'  - id: (\d+)', r).group(1)))
    ids = [int(re.match(r'  - id: (\d+)', r).group(1)) for r in rows]
    assert ids == list(range(ids[0], ids[0] + len(ids))), f'Secret Bases: overlay ids not contiguous: {ids[-6:]}'
    if os.path.islink(yml):
        os.unlink(yml)
    open(yml, 'w').write(head + ''.join(r.rstrip('\n') + '\n' for r in rows))
    return f'Secret Bases: overlay {n}, {end - start} B at {start:#x}'
