"""Where HoennB2 reads the Black 2 decomp (fuddlesworth/pokebw2). How it is set up and updated:
notes/POKEBW2_UPGRADE.md section 7.

SRC   The decomp's source tree, read for its headers (include/, lib/nitro/include, build/include/generated), symbols
      (config/b2_us/**/symbols.txt) and C (src/). It also holds untracked copies of the old layout our readers use
      ("option A": data/, tools/scripts/, 9 include/constants headers, 9 include/asm/*.inc). Default
      external/pokebw2_new; HOENN_DECOMP=<dir> (absolute, or relative to the repo) reads another tree, e.g.
      HOENN_DECOMP=external/pokebw2 = the old copy, to compare builds.
BASE  The ROM builder's base, never moved or modified: the matching build (build/b2_us), extract/, orig/, and the dsd
      that built it (tools/dsd v0.12.1-dsi.1) with the config it reads (config/, for `dsd dis`; the new config needs a
      newer dsd). external/pokebw2. Readers of these files may also name external/pokebw2/build|extract directly.
CODE  Where build_rom.py takes Black 2's code binaries from (HOENN_CODE): 'source' (the default since Phase 1,
      2026-10-25) = SRC built from the decomp's C with our C changes (b2tools/decomp_build.py; HOENN_DECOMP_C=0 switches
      our C off), 'base' = BASE's matching build, the dump's code (the one-switch fallback). notes/POKEBW2_UPGRADE.md
      section 8. The NitroFS files always come from BASE (the decomp's are byte-identical).
"""
import hashlib, os

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
BASE = os.path.join(ROOT, 'external', 'pokebw2')
SRC = os.path.normpath(os.path.join(ROOT, os.environ.get('HOENN_DECOMP') or os.path.join('external', 'pokebw2_new')))
DSD_SHA1 = 'dca3ae410630edd06fc90d8a186ea548cd6c8bbe'    # tools/dsd v0.12.1-dsi.1 (BASE's)
CODE = (os.environ.get('HOENN_CODE') or 'source').strip().lower()
assert CODE in ('base', 'source'), f'HOENN_CODE={CODE!r}: base or source'


def c_on():
    """Our C changes are in this build: the decomp's code (HOENN_CODE=source) with them on (not HOENN_DECOMP_C=0). Off,
    everything that depends on them stays out too (the resident section, the followers' question, text and script), so
    the ROM is what it was without them. A decomp tree without them (upstream's) counts as off."""
    return (CODE == 'source' and os.environ.get('HOENN_DECOMP_C') != '0'
            and os.path.exists(os.path.join(SRC, 'include', 'hoennb2.h')))


def code_dir():
    """The build dir build_rom.py copies the code binaries (arm9.bin, arm9_ovNNN.bin, itcm.bin, *.yaml,
    rom_config.yaml) from: BASE's matching build, or with HOENN_CODE=source the decomp's own build of SRC."""
    return os.path.join(SRC if CODE == 'source' else BASE, 'build', 'b2_us', 'build')


def dsd():
    """BASE's dsd, after checking it is the one that built the base (a different dsd may lay out the ROM differently)."""
    path = os.path.join(BASE, 'tools', 'dsd')
    h = hashlib.sha1(open(path, 'rb').read()).hexdigest()
    if h != DSD_SHA1:
        raise SystemExit(f'{path}: sha1 {h}, not the pinned dsd v0.12.1-dsi.1 ({DSD_SHA1}); see notes/POKEBW2_UPGRADE.md')
    return path


if __name__ == '__main__':
    print('SRC ', SRC)
    print('BASE', BASE)
    print('dsd ', dsd())
