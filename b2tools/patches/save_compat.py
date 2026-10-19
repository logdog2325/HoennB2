"""PKHeX-compatible Emerald saves (save_compat, 2026-10-18; notes/SAVE_PKHEX.md). OFF by default: only a build with
HOENN_SAVE_COMPAT=1 changes anything, and only an Emerald one (build_rom.py then appends this patch to the list, last,
as it does hoenn_music for HOENN_MUSIC). Without the switch every patch builds exactly as before.

Why: the Emerald builds enlarge two of Black 2's save blocks (frontier_core.py point 3: block 0x38 60 -> 252 bytes,
the Frontier's records; frontier_pyramid.py point 7: block 0x3e 16 -> 16 + PySave). The game checksums the new sizes,
PKHeX checks Black 2's (SAV5B2W2's block list: CRC-16 of 0x3C bytes at 0x21A00 against 0x21A3E and the table at
0x25F70, of 0x10 at 0x23600 against 0x23612 and 0x25F7C), so those two checks fail on every Emerald save.

With the switch:
  frontier_core.py / frontier_pyramid.py keep Black 2's sizes (60, 16), and every Frontier C file (frontier_core,
  _pike, _factory_dome, _palace_arena, _pyramid) is compiled with cflags(): the records start at block 0x38 + 64
  (after the 4-byte footer; FR_REC_OFF), keys 0-94 (FR_N_KEYS; key 95, never claimed, holds the area's CRC), the
  Pyramid's PySave at block 0x3e + 20 (PY_SAVE_OFF).
apply(files):  save_compat.c linked into the Frontier code area (frontier_area.add; resident from before GameInit).
apply_code(code):
  arm9 0x0203b95e (func_0203b92c, the block write: `bl getSizeOfSaveBlockData`, the length - 4) -> SC_WriteLen
  arm9 0x0203b854 (func_0203b81c, the compare with the card before a save: the length)        -> SC_CmpLen
  arm9 0x0200713a (SaveControl_Create) and 0x0200732c (func_02007324): `bl func_0203ae4c` (the main save's load)
                                                                                                  -> SC_Load
  (save_compat.c has what each does; the size functions arm9 0x0200e0f0 / 0x0200f128 are asserted at 60 / 16.)
Run `python3 save_compat.py` for a compile-only check (no ROM)."""
import os, re, sys, struct, subprocess, tempfile, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)
import version  # noqa: E402

ENV = 'HOENN_SAVE_COMPAT'
ARM9 = 0x02004000
REC_OFF, N_KEYS, PY_SAVE_OFF = 64, 95, 20          # block 0x38: 60 + footer; keys 0-94 + the CRC; block 0x3e: 16 + footer
SIZE_FNS = {0x0200E0F0: 60, 0x0200F128: 16}         # block 0x38's and 0x3e's getSize: movs r0, #n; bx lr
LOAD, GET_SIZE = 0x0203AE4C, 0x0203C3B0
CALLS = [(0x0203B95E, GET_SIZE, 'SC_WriteLen'),     # func_0203b92c
         (0x0203B854, GET_SIZE, 'SC_CmpLen'),       # func_0203b81c
         (0x0200713A, LOAD, 'SC_Load'),             # SaveControl_Create
         (0x0200732C, LOAD, 'SC_Load')]             # func_02007324
STATE = {}

def enabled():
    """the switch: ON in every Emerald build since 2026-10-18 (the user approved it after the melonDS + PKHeX test);
    HOENN_SAVE_COMPAT=0 builds the old layout (Emerald <= v1.0.4's enlarged blocks)"""
    return os.environ.get(ENV, '1') != '0' and version.is_emerald()

def cflags():
    """clang flags for the Frontier C files: [] without the switch (their code stays byte-identical)"""
    if not enabled():
        return []
    return ['-DHOENN_SAVE_COMPAT', f'-DFR_REC_OFF={REC_OFF}', f'-DFR_N_KEYS={N_KEYS}', f'-DPY_SAVE_OFF={PY_SAVE_OFF}']

def _mod(name, file):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, file))
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod

def py_state():
    """sizeof(PySave): frontier_pyramid.py's SAVE_STATE"""
    m = re.search(r'^SAVE_STATE = (\d+)', open(os.path.join(HERE, 'frontier_pyramid.py')).read(), re.M)
    n = int(m.group(1))
    assert 16 + 4 + n + 2 <= 256, n
    return n

def build(base, workdir):
    import frontier_area
    obj = frontier_area.compile(os.path.join(HERE, 'save_compat.c'), workdir, [f'-DPY_STATE={py_state()}'])
    return frontier_area.link(obj, base)

def apply(files):
    if not enabled():
        return f'{version.NAME}: nothing ({ENV}=1 Emerald builds only)'
    import frontier_area
    syms, base, size = frontier_area.add(files, 'save_compat', build)
    STATE.update(syms=syms, base=base, size=size)
    return f'save_compat: {size} B in the Frontier code area at {base:#x} (arc 211 file {frontier_area.STATE["file"]})'

def _load(code, name):
    p = os.path.join(code, name); return p, bytearray(open(p, 'rb').read())

def _save(p, d):
    if os.path.islink(p): os.unlink(p)
    open(p + '.tmp', 'wb').write(d); os.replace(p + '.tmp', p)

def apply_code(code):
    if not enabled():
        return f'{version.NAME}: nothing ({ENV}=1 Emerald builds only)'
    assert 'syms' in STATE, 'save_compat: apply() must run first (same patch)'
    import frontier_area
    loader = frontier_area.install(code)
    sym = STATE['syms']
    bl = _mod('roamers_sc', 'roamers.py')._bl
    p9, arm9 = _load(code, 'arm9.bin')
    for at, n in SIZE_FNS.items():
        assert struct.unpack_from('<HH', arm9, at - ARM9) == (0x2000 | n, 0x4770), \
            f'arm9 {at:#x}: block size is not Black 2\'s {n} (frontier_core / frontier_pyramid without {ENV}?)'
    for at, old, new in CALLS:
        assert bytes(arm9[at - ARM9:at - ARM9 + 4]) == bl(at, old), f'arm9 {at:#x}: not Black 2\'s call (another patch?)'
        arm9[at - ARM9:at - ARM9 + 4] = bl(at, sym[new] & ~1)
    _save(p9, arm9)
    return (f'save_compat: blocks 0x38 / 0x3e at Black 2\'s 60 / 16 B, extensions after their footers (records '
            f'+{REC_OFF}, keys 0-{N_KEYS - 1} + CRC; PySave +{PY_SAVE_OFF}, {py_state()} B + CRC); hooks '
            + ', '.join(f'{at:#x} -> {new}' for at, _, new in CALLS) + f'; old saves migrate on load; {loader}')

if __name__ == '__main__':          # python3 save_compat.py: compile + link at the area's base (no ROM)
    with tempfile.TemporaryDirectory() as tmp:
        import frontier_area
        b, sym = build(frontier_area.FRAM_BASE, tmp)
        print(len(b), 'B', {k: hex(v) for k, v in sym.items() if k.startswith('SC_')})
