"""HoennB2's resident section (the decomp's include/hoennb2/resident.h, overlay 344, read once at boot): the place for
the build's data that the C reads through a pointer, instead of ITCM (Emerald's is nearly full). The same design as
PearlB2's b2tools/resident.py; notes/POKEBW2_UPGRADE.md section 9.

    install(code, build_fn)   build_fn(base) -> (blob, symbols): the blob goes into the section's pool
                              (HOENNB2_RESIDENT_POOL .. _END, in code/arm9_ov344.bin), at base; returns (base, end, symbols)
    write(code, addr, data)   bytes at a linked address, in whichever code binary holds it (ITCM, ARM9, the resident
                              section); read(code, addr, size) the same way
The pool's next free address is kept in code/resident_pool.json (a quick non-clean build appends).
"""
import json, os

RESIDENT = 344
ITCM_BASE, ITCM_END, ARM9 = 0x01FF8000, 0x02000000, 0x02004000


def _symbol(name, code):
    import decomp_build
    return decomp_build.symbol(name, code)


def _pool(code):
    lo, hi = _symbol('HOENNB2_RESIDENT_POOL', code), _symbol('HOENNB2_RESIDENT_POOL_END', code)
    base = _symbol(f'OV{RESIDENT}_TEXT_START', code)
    path = os.path.join(code, f'arm9_ov{RESIDENT:03d}.bin')
    if lo is None or not os.path.exists(path):
        return None
    return lo, hi, base, path


def available(code):
    """The code binaries have the section (HOENN_CODE=source with our C on)."""
    return _pool(code) is not None


def _binary(code, addr, size):
    """(path, offset) of the code binary that holds addr .. addr+size."""
    if ITCM_BASE <= addr and addr + size <= ITCM_END:
        return os.path.join(code, 'itcm.bin'), addr - ITCM_BASE
    start = _symbol(f'OV{RESIDENT}_TEXT_START', code)
    bss = _symbol(f'OV{RESIDENT}_BSS_START', code)
    if start is not None and start <= addr and addr + size <= bss:
        return os.path.join(code, f'arm9_ov{RESIDENT:03d}.bin'), addr - start
    path = os.path.join(code, 'arm9.bin')
    assert ARM9 <= addr and addr + size <= ARM9 + os.path.getsize(path), \
        f'{addr:#x}: in no code binary this knows (ITCM, ARM9, overlay {RESIDENT})'
    return path, addr - ARM9


def read(code, addr, size):
    path, at = _binary(code, addr, size)
    return open(path, 'rb').read()[at:at + size]


def write(code, addr, data):
    path, at = _binary(code, addr, len(data))
    d = bytearray(open(path, 'rb').read())
    assert at + len(data) <= len(d), f'{path}: {at + len(data)} past its {len(d)} B'
    d[at:at + len(data)] = data
    if os.path.islink(path):
        os.unlink(path)
    open(path + '.tmp', 'wb').write(d)
    os.replace(path + '.tmp', path)


def install(code, build_fn):
    pool = _pool(code)
    assert pool is not None, 'resident.install: these code binaries have no resident section (HOENN_CODE=source, C on)'
    lo, hi, base, path = pool
    state = os.path.join(code, 'resident_pool.json')
    at = json.load(open(state))['next'] if os.path.exists(state) else lo
    blob, sym = build_fn(at)
    end = (at + len(blob) + 3) & ~3
    assert end <= hi, f'the resident pool is full: {end - lo} B of {hi - lo} (tools/hoennb2/link_overlays.py POOL_SIZE)'
    write(code, at, blob)
    json.dump({'next': end}, open(state, 'w'))
    return at, end, sym
