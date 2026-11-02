"""Black 2's code built from the decomp's C (fuddlesworth/pokebw2 in b2decomp.SRC) instead of the dump's binaries:
notes/POKEBW2_UPGRADE.md section 8 "Building from source" (feasibility, 2026-10-25). Modelled on PearlB2's decomp.py.

    python3 decomp_build.py build       ninja the code binaries and the file system (incremental), then the layout check
    python3 decomp_build.py check       the layout check alone: every module of the game its original size and every
                                        symbol of the decomp's symbols.txt at its original address (ITCM may grow:
                                        our C after the game's)
    python3 decomp_build.py changed     the functions whose bytes differ from the dump's (what our C changes touch)
    python3 decomp_build.py vanilla     every HoennB2 change off (HOENNB2 0 in include/hoennb2.h): the code must be the
                                        dump's again (--rom: also the decomp's own `ninja b2_us`, the ROM's SHA-1);
                                        then HOENNB2 1 again and rebuilt
    python3 decomp_build.py symbol NAME the linked address of a function or data symbol
    python3 decomp_build.py verify      the tree = decomp_changes/UPSTREAM + decomp_changes/hoennb2_decomp.patch (releases)
    python3 decomp_build.py patch       save the tree's changes as decomp_changes/hoennb2_decomp.patch (`diff`: show them)
    python3 decomp_build.py setup DIR   a decomp tree of its own (HOENN_DECOMP=DIR): worktree + patch + tools, configured

build_rom.py takes its code binaries from here (HOENN_CODE=source, the default since Phase 1; HOENN_CODE=base = the
dump's binaries in b2decomp.BASE, the fallback): it calls build() first, then dsd_compat() on its copy.
HOENN_DECOMP_C=0 builds with every HoennB2 C change off (the dump's code), for the byte-identical checks.

Why the layout check: our binary patches (patches/*.py) edit the code at fixed addresses and assert the bytes they
replace. Black 2's overlays are chained in memory, so a C change that makes a function a byte longer or shorter moves
everything after it, and those patches would stop applying. Until they look addresses up by name (symbol()), a change
keeps its function's size and new code goes to src/hoennb2/*_itcm.c, linked after Black 2's ITCM code.

Toolchain (git-ignored in SRC/tools, copied from PearlB2's external/pokebw2_pearlb2/tools on 2026-10-25, no download):
dsd v0.12.1-dsi.9, wibo pokebw2-sjis-1, sjiswrap v1.2.2-pokebw2.1 (SHA-256s as configure.py pins), mwccarm (dsi/1.1p1
for the game, dsi/1.1 mwldarm, 1.2/base, 2.0/sp1p2, 2.0/sp2, dsi/1.2 for libraries). Not needed: objdiff-cli (only
the decomp's progress report). Configure once: `PATH=/opt/homebrew/opt/llvm/bin:$PATH python3 configure.py
--no-download b2_us` in SRC (ninja reruns it by itself when configure.py or src/hoennb2 change).
"""
import bisect, fcntl, os, re, shutil, struct, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import b2decomp  # noqa: E402

DECOMP = b2decomp.SRC
VERSION = 'b2_us'
BUILD = os.path.join(DECOMP, 'build', VERSION)
CODE = os.path.join(BUILD, 'build')                      # arm9.bin, arm9_ovNNN.bin, itcm.bin, *.yaml, rom_config.yaml
ORIGINAL = os.path.join(DECOMP, 'extract', VERSION)      # the dump's modules (decompressed), as dsd extracted them
CONFIG = os.path.join(DECOMP, 'config', VERSION, 'arm9')
XMAP = os.path.join(BUILD, 'arm9.o.xMAP')
SWITCH = os.path.join(DECOMP, 'include', 'hoennb2.h')    # #define HOENNB2 1
ARM9 = 0x02004000
LLVM = '/opt/homebrew/opt/llvm/bin'
NINJA = shutil.which('ninja') or os.path.expanduser('~/Library/Python/3.13/bin/ninja')
TARGET = f'{VERSION}_hoennb2'                            # the code binaries and the files tree, no ROM
JOBS = os.environ.get('HOENN_DECOMP_JOBS', '5')
# Our changes to the decomp (GPL-3.0: private, never in public/export.sh's snapshot): the upstream commit they apply to
# and the patch itself, kept in this repo (decomp_changes/README.md)
CHANGES = os.path.join(b2decomp.ROOT, 'decomp_changes')
PATCH = os.path.join(CHANGES, 'hoennb2_decomp.patch')
UPSTREAM_FILE = os.path.join(CHANGES, 'UPSTREAM')
NEW_PATHS = ['include/hoennb2.h', 'include/hoennb2', 'include/follower.h', 'include/follower_port.h', 'src/hoennb2',
             'tools/hoennb2']                            # our new files (rules: only there)
GENERATED = ['compile_flags.txt']                        # tracked, but rewritten by configure.py
TOOLS = ['dsd', 'dsd.rev', 'wibo', 'sjiswrap.exe', 'mwccarm']    # git-ignored toolchain in SRC/tools
OPTION_A = (['data', 'tools/scripts'] +                  # section 7's old data layer, read by our readers
            [f'include/constants/{h}.h' for h in 'abilities flags items moves sound species trainer_classes types '
             'zones'.split()] +
            [f'include/asm/{i}.inc' for i in 'baby_species encounters evolution growth_rates levelup_moves move_data '
             'personal trainer zone_header'.split()])


# ---- modules -----------------------------------------------------------------------------------------------------------
def modules(code=CODE):
    """[(name, built .bin, original .bin, symbols.txt, base address)] of every code module."""
    out = []
    fixed = [('arm9', 'arm9.bin', 'arm9/arm9.bin', ''), ('itcm', 'itcm.bin', 'arm9/itcm.bin', 'itcm'),
             ('dtcm', 'dtcm.bin', 'arm9/dtcm.bin', 'dtcm'),
             ('autoload_2', 'autoload_2.bin', 'arm9/unk_autoload_2.bin', 'autoload_2'),
             ('autoload_3', 'autoload_3.bin', 'arm9/unk_autoload_3.bin', 'autoload_3'),
             ('ltd_autoload_0', 'ltd_autoload_0.bin', 'dsi/ltd_autoload_0.bin', 'ltd_autoload_0')]
    for name, built, orig, sym in fixed:
        yml = os.path.join(code, built.replace('.bin', '.yaml'))
        base = int(re.search(r'^base_address: (\d+)$', open(yml).read(), re.M).group(1))
        out.append((name, os.path.join(code, built), os.path.join(ORIGINAL, orig),
                    os.path.join(CONFIG, sym, 'symbols.txt'), base))
    ovl = open(os.path.join(code, 'arm9_overlays.yaml')).read()
    for m in re.finditer(r'- id: (\d+)\n\s+base_address: (\d+)', ovl):
        n, base = int(m.group(1)), int(m.group(2))
        out.append((f'ov{n:03d}', os.path.join(code, f'arm9_ov{n:03d}.bin'),
                    os.path.join(ORIGINAL, 'arm9_overlays', f'ov{n:03d}.bin'),
                    os.path.join(CONFIG, 'overlays', f'ov{n:03d}', 'symbols.txt'), base))
    return out


def _symbols_list(path):
    """[(name, address, size or None, kind)] of a decomp symbols.txt."""
    out = []
    for line in open(path):
        m = re.match(r'(\S+) kind:(\w+)(?:\((\w+)(?:,size=(0x[0-9a-f]+))?[^)]*\))? addr:(0x[0-9a-f]+)', line)
        if m:
            out.append((m.group(1), int(m.group(5), 16), int(m.group(4), 16) if m.group(4) else None, m.group(2)))
    return out


def _xmap(path=XMAP):
    """{name: {address, ...}} of the link (arm9.o.xMAP: every module; overlays share addresses)."""
    out = {}
    for line in open(path, errors='replace'):
        m = re.match(r'  ([0-9A-F]{8}) [0-9A-F]{8} \.\w+\s+(.+?)\t\(', line) or \
            re.match(r'#>([0-9A-F]{8})\s+(\S+) \(linker command file\)', line)
        if m:
            out.setdefault(m.group(2), set()).add(int(m.group(1), 16))
            if '::' in m.group(2):      # a C++ function's static, also by its own name (as symbols.txt has it)
                out.setdefault(m.group(2).rsplit('::', 1)[1], set()).add(int(m.group(1), 16))
    return out


def symbol(name, code=None):
    """The linked address of a function or data symbol (Thumb functions without the bit), of the link whose binaries
    build_rom copied into `code` (the link map is copied with them; none = the dump's binaries, HOENN_CODE=base), or
    with code None of the decomp's last build; None if the link has no such symbol (e.g. a decomp without our C)."""
    path = os.path.join(code, 'arm9.o.xMAP') if code else XMAP
    if not os.path.exists(path):
        return None
    addrs = _xmap(path).get(name)
    if not addrs:
        return None
    assert len(addrs) == 1, f'{name}: {len(addrs)} addresses in the link'
    return next(iter(addrs))


# ---- dsd compatibility -------------------------------------------------------------------------------------------------
def _dsd_windows():
    sym = {n: a for n, a, _, _ in _symbols_list(os.path.join(CONFIG, 'symbols.txt'))}
    return [(sym['OverlayTableDigests'], sym['SDK_OVERLAY_DIGEST_END']),
            (sym['LtdModuleParams'] + 0xC, sym['LtdModuleParams'] + 0x10)]


def copy_map(code):
    """Keep the link map with build_rom's copy of the code binaries, for symbol(name, code)."""
    if os.path.exists(XMAP):
        subprocess.run(['cp', '-c', XMAP, os.path.join(code, 'arm9.o.xMAP')], check=True)


def _write(path, data):
    if os.path.islink(path): os.unlink(path)
    mode = 'wb' if isinstance(data, (bytes, bytearray)) else 'w'
    with open(path + '.tmp', mode) as f: f.write(data)
    os.replace(path + '.tmp', path)


def dsd_compat(code):
    """Make the decomp's code binaries what build_rom's dsd (BASE's v0.12.1-dsi.1, b2decomp.dsd()) expects.

    The decomp (dsd v0.12.1-dsi.5 and later) links the overlay digests (OverlayTableDigests .. SDK_OVERLAY_DIGEST_END)
    and one word of LtdModuleParams as zeros and lets its own `dsd rom build` fill them (arm9.yaml overlay_signatures,
    arm9_overlays.yaml table_signed). Our dsd keeps what arm9.bin holds, so this puts the dump's bytes back there and
    the old yaml values; the decomp's yaml also drops the DS Protect overlays' `bss_variable`, which BASE's has (put
    back from BASE). Then the code binaries are byte for byte BASE's (checked 2026-10-25), and our ROMs the same.
    (Patched overlays keep Black 2's digests, as they always did: the game checks them only when it isn't booted from
    the cartridge.)"""
    yml = os.path.join(code, 'arm9.yaml')
    text = open(yml).read()
    m = re.search(r'^overlay_signatures: (\d+)$', text, re.M)
    if not m or m.group(1) == '0':
        return 'dsd compat: nothing to restore'
    path = os.path.join(code, 'arm9.bin')
    arm9 = bytearray(open(path, 'rb').read())
    orig = open(os.path.join(ORIGINAL, 'arm9', 'arm9.bin'), 'rb').read()
    restored = 0
    for start, end in _dsd_windows():
        a, b = start - ARM9, end - ARM9
        assert not any(arm9[a:b]) or arm9[a:b] == orig[a:b], \
            f'dsd compat: {start:#x}-{end:#x} is neither zeros (to be filled by dsd) nor the original'
        restored += sum(1 for x, y in zip(arm9[a:b], orig[a:b]) if x != y)
        arm9[a:b] = orig[a:b]
    _write(path, arm9)
    _write(yml, re.sub(r'^overlay_signatures: \d+$', 'overlay_signatures: 0', text, flags=re.M))
    oyml = os.path.join(code, 'arm9_overlays.yaml')
    otext = re.sub(r'^table_signed: true$', 'table_signed: false', open(oyml).read(), flags=re.M)
    base = open(os.path.join(b2decomp.BASE, 'build', VERSION, 'build', 'arm9_overlays.yaml')).read()
    for bss in re.findall(r'^( +bss_variable: \d+\n)', base, re.M):       # after the line before it in BASE's yaml
        before = base[:base.index(bss)].rsplit('\n', 2)[-2] + '\n'
        if bss not in otext:
            assert otext.count(before) == 1, f'dsd compat: no single "{before.strip()}" for {bss.strip()}'
            otext = otext.replace(before, before + bss)
    _write(oyml, otext)
    return f'dsd compat: {restored} bytes of overlay digests and LTD params from the dump, signatures off'


# ---- our overlays in the ROM's overlay table ----------------------------------------------------------------------------
RESIDENT = 344      # tools/hoennb2/link_overlays.py


def _elf_symbols(path):
    d = open(path, 'rb').read()
    assert d[:4] == b'\x7fELF' and d[4] == 1 and d[5] == 1, f'{path}: not a 32-bit little-endian ELF'
    shoff, = struct.unpack_from('<I', d, 0x20)
    shentsize, shnum = struct.unpack_from('<HH', d, 0x2E)
    secs = [struct.unpack_from('<10I', d, shoff + i * shentsize) for i in range(shnum)]
    syms = {}
    for name, typ, flags, addr, off, size, link, info, align, entsize in secs:
        if typ != 2:                                # SHT_SYMTAB
            continue
        stroff = secs[link][4]
        for k in range(size // 16):
            nm, value = struct.unpack_from('<II', d, off + 16 * k)
            if nm:
                e = d.index(b'\0', stroff + nm)
                syms[d[stroff + nm:e].decode()] = value
    return syms


def install_overlays(code, c_off=False):
    """Our resident section (overlay 344, linked after overlay 290 but not in dsd's config) into the ROM's overlay table:
    its entry in code/arm9_overlays.yaml (unsigned, uncompressed, file id = id); its bytes are the build's
    arm9_ov344.bin, already in the code dir. Right after build_rom copies the code binaries, before any patch. With our
    C off (HOENN_DECOMP_C=0: the dump's code) or an older decomp: none, and the ROM's layout stays the release's."""
    if c_off or not os.path.exists(SWITCH) or not re.search(r'^#define HOENNB2 1$', open(SWITCH).read(), re.M):
        return 'resident section: our C is off, none'
    syms = _elf_symbols(os.path.join(BUILD, 'arm9.o'))
    n = RESIDENT
    if f'OV{n}_TEXT_START' not in syms:
        return 'resident section: this decomp has none'
    start, bss, end = syms[f'OV{n}_TEXT_START'], syms[f'OV{n}_BSS_START'], syms[f'OV{n}_BSS_END']
    path = os.path.join(code, f'arm9_ov{n:03d}.bin')
    assert os.path.getsize(path) == bss - start, f'{path}: {os.path.getsize(path)} B, the link says {bss - start}'
    yml = os.path.join(code, 'arm9_overlays.yaml')
    text = open(yml).read()
    assert f'id: {n}\n' not in text, f'{yml}: overlay {n} is there already'
    last = max(int(m) for m in re.findall(r'^  - id: (\d+)$', text, re.M))
    assert last == n - 1, f'{yml}: the last overlay is {last}, not {n - 1}'
    entry = (f'  - id: {n}\n    base_address: {start}\n    code_size: {bss - start}\n    bss_size: {end - bss}\n'
             f'    ctor_start: {syms[f"OV{n}_CTOR_START"]}\n    ctor_end: {syms[f"OV{n}_CTOR_END"]}\n    file_id: {n}\n'
             f'    compressed: false\n    signed: false\n    file_name: {path}\n')
    _write(yml, text.rstrip('\n') + '\n' + entry)
    pool_end = syms['HOENNB2_RESIDENT_POOL_END'] - syms['HOENNB2_RESIDENT_POOL']
    return f'resident section: overlay {n}, {end - start} B at {start:#x} (pool {pool_end} B), ITCM unchanged by it'


# ---- build ---------------------------------------------------------------------------------------------------------------
class _Lock:
    """One ninja at a time in the decomp tree."""
    def __enter__(self):
        os.makedirs(os.path.join(DECOMP, 'build'), exist_ok=True)
        self.f = open(os.path.join(DECOMP, 'build', '.hoennb2_ninja.lock'), 'w')
        fcntl.flock(self.f, fcntl.LOCK_EX)
        return self

    def __exit__(self, *exc):
        fcntl.flock(self.f, fcntl.LOCK_UN); self.f.close()


def _ninja(*targets):
    """Run the decomp's ninja; its generator rule reruns configure.py, which wants Homebrew's clang first on PATH."""
    env = dict(os.environ, PATH=f'{LLVM}:{os.environ.get("PATH", "")}')
    t = time.time()
    r = subprocess.run([NINJA, '-j', JOBS, '-C', DECOMP, *targets], capture_output=True, text=True, env=env)
    lines = [l for l in r.stdout.splitlines() if l.strip()]
    if r.returncode:
        raise SystemExit(f'decomp: ninja {" ".join(targets)} failed:\n' + '\n'.join(lines[-40:]) + r.stderr[-2000:])
    work = [l for l in lines if l.startswith('[')]
    return f'{len(work)} steps in {time.time() - t:.0f} s' if work else f'up to date ({time.time() - t:.0f} s)'


def _set_switch(on):
    """include/hoennb2.h's HOENNB2 to 1 or 0; returns the old text (None: no hoennb2.h, an upstream tree)."""
    if not os.path.exists(SWITCH):
        return None
    text = open(SWITCH).read()
    assert re.search(r'^#define HOENNB2 [01]$', text, re.M), f'{SWITCH}: no "#define HOENNB2 0/1"'
    open(SWITCH, 'w').write(re.sub(r'^#define HOENNB2 [01]$', f'#define HOENNB2 {int(on)}', text, flags=re.M))
    return text


def build(after=None, c_off=False):
    """Bring the decomp's code binaries and files tree up to date, check the layout, then run after() (build_rom's
    copies) while still holding the lock. c_off (HOENN_DECOMP_C=0): with every HoennB2 C change switched off
    (HOENNB2 0), i.e. the dump's code, for the byte-identical checks against the releases; the tree is switched back
    and rebuilt before the lock is released. Returns a summary line."""
    if not os.path.exists(os.path.join(DECOMP, 'build.ninja')):
        raise SystemExit(f'decomp: {DECOMP} is not configured (notes/POKEBW2_UPGRADE.md section 8.2: configure.py '
                         '--no-download b2_us), or build with HOENN_CODE=base (the dump\'s binaries)')
    with _Lock():
        old = _set_switch(False) if c_off else None
        try:
            done = _ninja(TARGET)
            problems, summary = check()
            if problems:
                raise SystemExit('decomp: the C changes move the game\'s code (our binary patches need it in place):\n  '
                                 + '\n  '.join(problems[:30]))
            if c_off:
                diff = changed()
                assert not diff, f'decomp: with HOENNB2 0 the code still differs from the dump: {diff[:10]}'
            if after: after()
        finally:
            if old is not None:
                open(SWITCH, 'w').write(old)
        if old is not None:
            _ninja(TARGET)                  # the shared tree's build back to its own state
    return f'decomp {_head()}{" (HoennB2 C OFF: the dump\'s code)" if c_off else ""}: ninja {done}; {summary}; {patch_state()}'


# ---- our changes as a patch (decomp_changes/) ---------------------------------------------------------------------------
def _git(*args, env=None, check=True):
    r = subprocess.run(['git', '-C', DECOMP, *args], capture_output=True, text=True, env=env)
    if check and r.returncode:
        raise SystemExit(f'decomp: git {" ".join(args)}: {r.stderr.strip()}')
    return r.stdout


def current_patch():
    """The decomp tree's changes against decomp_changes/UPSTREAM as one patch, committed on its hoennb2 branch or not:
    tracked files (but configure's generated ones) and our new files (NEW_PATHS), through a scratch index in build/ (the
    tree's own index is not touched)."""
    os.makedirs(os.path.join(DECOMP, 'build'), exist_ok=True)
    env = dict(os.environ, GIT_INDEX_FILE=os.path.join(DECOMP, 'build', '.hoennb2_index'))
    _git('read-tree', upstream(), env=env)
    new = [p for p in NEW_PATHS if os.path.exists(os.path.join(DECOMP, p))]
    if new:
        _git('add', '-N', *new, env=env)
    return _git('diff', '--', '.', *(f':(exclude){g}' for g in GENERATED), env=env)


def upstream():
    return open(UPSTREAM_FILE).read().strip()


def verify(c_on=True):
    """[problems]: the decomp tree must be the pinned upstream commit plus exactly this repo's patch (with HOENNB2 1)."""
    out = []
    r = subprocess.run(['git', '-C', DECOMP, 'merge-base', '--is-ancestor', upstream(), 'HEAD'], capture_output=True)
    if r.returncode:
        out.append(f'decomp HEAD is not on decomp_changes/UPSTREAM ({upstream()[:10]})')
    cur = current_patch()
    want = open(PATCH).read() if os.path.exists(PATCH) else ''
    if cur != want:
        out.append('the decomp tree\'s changes differ from decomp_changes/hoennb2_decomp.patch '
                   '(python3 b2tools/decomp_build.py diff shows how; `patch` saves the tree\'s)')
    if c_on and os.path.exists(SWITCH) and not re.search(r'^#define HOENNB2 1$', open(SWITCH).read(), re.M):
        out.append('include/hoennb2.h has HOENNB2 0')
    return out


def patch_state():
    try:
        problems = verify()
    except (SystemExit, OSError) as ex:
        return f'decomp changes: unknown ({ex})'
    return 'decomp changes = decomp_changes/hoennb2_decomp.patch' if not problems else \
        'WARNING decomp changes: ' + '; '.join(problems)


def write_patch():
    text = current_patch()
    os.makedirs(CHANGES, exist_ok=True)
    open(PATCH, 'w').write(text)
    return f'{PATCH}: {text.count(chr(10))} lines, {len(re.findall(r"^diff --git", text, re.M))} files'


def setup(dest):
    """A decomp tree of its own at `dest` (for HOENN_DECOMP=dest: a helper's C work, or a release whose patch differs
    from the shared tree's): a git worktree of SRC at decomp_changes/UPSTREAM with this repo's patch applied, the
    toolchain, orig/, extract/ and section 7's data layer as APFS clones of SRC's, configured. Then the first ninja
    (about 6 min, 0.9 GB): `python3 b2tools/decomp_build.py build` with HOENN_DECOMP=dest."""
    dest = os.path.abspath(dest)
    assert not os.path.exists(dest), f'{dest} exists'
    _git('worktree', 'add', '--detach', dest, upstream())
    if os.path.exists(PATCH) and os.path.getsize(PATCH):
        r = subprocess.run(['git', '-C', dest, 'apply', PATCH], capture_output=True, text=True)
        if r.returncode:
            raise SystemExit(f'git apply {PATCH}: {r.stderr}')
    clone = lambda rel: subprocess.run(['cp', '-c', '-R', os.path.join(DECOMP, rel),
                                        os.path.dirname(os.path.join(dest, rel)) + '/'], check=True)
    for t in TOOLS:
        clone(os.path.join('tools', t))
    for rel in ['orig', 'extract', *OPTION_A]:
        if os.path.exists(os.path.join(DECOMP, rel)) and not os.path.exists(os.path.join(dest, rel)):
            os.makedirs(os.path.dirname(os.path.join(dest, rel)), exist_ok=True)
            clone(rel)
    env = dict(os.environ, PATH=f'{LLVM}:{os.environ.get("PATH", "")}')
    subprocess.run([sys.executable, 'configure.py', '--no-download', VERSION], cwd=dest, check=True, env=env)
    return f'{dest}: decomp {upstream()[:10]} + {os.path.relpath(PATCH, b2decomp.ROOT)}, configured; next: ' \
           f'HOENN_DECOMP={dest} python3 b2tools/decomp_build.py build'


def _head():
    s = subprocess.run(['git', '-C', DECOMP, 'rev-parse', '--short', 'HEAD'], capture_output=True, text=True)
    d = subprocess.run(['git', '-C', DECOMP, 'status', '--porcelain', '--untracked-files=no'], capture_output=True,
                       text=True)
    return f'{s.stdout.strip()}{" + local changes" if d.stdout.strip() else ""}'


def check():
    """(problems, summary): each module against the dump's. Every module keeps its size (ITCM may grow: our code after
    the game's) and every symbol of the decomp's symbols.txt that the link has stays at its address."""
    problems, moved, checked = [], 0, 0
    linked = _xmap()
    itcm_extra = 0
    for name, built, orig, symtxt, base in modules():
        b, o = os.path.getsize(built), os.path.getsize(orig)
        if name == 'itcm':
            itcm_extra = b - o
            if b < o:
                problems.append(f'itcm: {b} bytes, smaller than the original {o}')
        elif b != o:
            problems.append(f'{name}: {b} bytes (the original {o})')
        if not os.path.exists(symtxt):
            continue
        for sym, addr, _, kind in _symbols_list(symtxt):
            addrs = linked.get(sym)
            if not addrs:
                continue
            checked += 1
            if addr not in addrs:
                moved += 1
                if moved <= 20:
                    problems.append(f'{name}: {sym} at {", ".join(hex(a) for a in sorted(addrs))} (was {addr:#x})')
    if moved > 20:
        problems.append(f'... {moved} symbols moved in all')
    return problems, f'layout kept ({checked} symbols checked; ITCM +{itcm_extra} B of our code)'


def changed():
    """[(module, function, differing bytes)]: the functions whose bytes differ from the dump's."""
    out = []
    skip = _dsd_windows()
    for name, built, orig, symtxt, base in modules():
        b, o = open(built, 'rb').read(), open(orig, 'rb').read()
        diff = [i for i in range(len(b)) if (i >= len(o) or b[i] != o[i])
                and not (name == 'arm9' and any(s <= base + i < e for s, e in skip))]
        if not diff:
            continue
        funcs = sorted((a, n, s) for n, a, s, k in _symbols_list(symtxt)) if os.path.exists(symtxt) else []
        starts = [a for a, _, _ in funcs]
        hits = {}
        for i in diff:
            j = bisect.bisect_right(starts, base + i) - 1
            if j < 0:
                owner = f'{base + i:#x}'
            elif i >= len(o) or (funcs[j][2] and base + i >= funcs[j][0] + funcs[j][2]):
                owner = f'(after {funcs[j][1]}: padding or our code)'
            else:
                owner = funcs[j][1]
            hits[owner] = hits.get(owner, 0) + 1
        out += [(name, f, n) for f, n in hits.items()]
    return out


def vanilla(rom=False):
    """Build with HOENNB2 0: every code module must then be the dump's (changed() empty, ITCM its size), which proves
    each change of ours is inside #if HOENNB2; rom=True also builds and checks the whole ROM (`ninja b2_us`, the
    dump's SHA-1; its 512 MB ROM is then a clone of orig/ again). Then HOENNB2 1 again and rebuilt."""
    text = open(SWITCH).read()
    assert re.search(r'^#define HOENNB2 1$', text, re.M), f'{SWITCH}: no "#define HOENNB2 1"'
    with _Lock():
        try:
            open(SWITCH, 'w').write(text.replace('#define HOENNB2 1', '#define HOENNB2 0'))
            done = _ninja(VERSION if rom else TARGET)
            diff = changed()
            itcm = next(m for m in modules() if m[0] == 'itcm')
            extra = os.path.getsize(itcm[1]) - os.path.getsize(itcm[2])
        finally:
            open(SWITCH, 'w').write(text)
        _ninja(TARGET)
    if diff or extra:
        raise SystemExit(f'decomp vanilla: with HOENNB2 0 the code still differs from the dump: ITCM +{extra} B, '
                         + ', '.join(f'{m} {f} ({n} B)' for m, f, n in diff[:20]))
    return (f'HOENNB2 0: every code module is the dump\'s' + (' and the ROM\'s SHA-1 the original\'s' if rom else '')
            + f' (ninja {done}); HOENNB2 1 again, rebuilt')


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else ''
    if cmd == 'build':
        print(build())
    elif cmd == 'check':
        problems, summary = check()
        print('\n'.join(problems) if problems else summary)
        sys.exit(1 if problems else 0)
    elif cmd == 'changed':
        for module, func, n in changed():
            print(f'{module:15} {func:50} {n} bytes')
    elif cmd == 'vanilla':
        print(vanilla(rom='--rom' in sys.argv))
    elif cmd == 'verify':
        problems = verify()
        print('\n'.join(problems) if problems else f'decomp = {upstream()[:10]} + decomp_changes/hoennb2_decomp.patch')
        sys.exit(1 if problems else 0)
    elif cmd == 'patch':
        print(write_patch())
    elif cmd == 'diff':
        import difflib
        want = open(PATCH).read().splitlines(True) if os.path.exists(PATCH) else []
        sys.stdout.writelines(difflib.unified_diff(want, current_patch().splitlines(True), 'decomp_changes', 'tree'))
    elif cmd == 'setup' and len(sys.argv) > 2:
        print(setup(sys.argv[2]))
    elif cmd == 'symbol' and len(sys.argv) > 2:
        a = symbol(sys.argv[2])
        print(f'{a:#x}' if a is not None else 'not in the link')
    else:
        sys.exit(__doc__)
