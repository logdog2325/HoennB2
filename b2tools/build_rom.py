"""Build a modified Black 2 ROM from the decomp's matching build plus our patches.

    python3 build_rom.py [--clean] [--no-pad] [patch ...]

1. Clones (APFS copy-on-write) external/pokebw2/build/b2_us/files -> work/rom/files  (only with --clean or first run)
2. Runs each named patch: patches/<name>.py defines apply(files_dir) (NitroFS files) and/or apply_code(code_dir)
   (decompressed arm9.bin / arm9_ovNNN.bin, a clone of the decomp's build dir; dsd recompresses them)
3. Writes work/rom/rom_config.yaml (the decomp's config with absolute paths and our files_dir)
4. Runs `dsd rom build` -> work/rom/hoenn.nds

The decomp checkout and its extracted files are never modified. With no patches, the output must match the
original dump's SHA1 (checked).
"""
import os, sys, subprocess, shutil, hashlib, importlib.util, re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
import version  # noqa: E402  (HOENN_VERSION=sapphire|ruby|emerald: every patch asks b2tools/version.py; notes/RUBY.md, EMERALD.md)
DECOMP = os.path.join(ROOT, 'external', 'pokebw2')
SRC_BUILD = os.path.join(DECOMP, 'build', 'b2_us', 'build')
SRC_FILES = os.path.join(DECOMP, 'build', 'b2_us', 'files')
OUT = version.build_dir(os.path.join(ROOT, 'work', 'rom'))   # HOENN_BUILD_DIR (parallel/test builds), else work/rom
                                                             # (Sapphire) or work/rom_ruby / work/rom_emerald (never the Sapphire ROM)
if version.EMERALD and not os.environ.get('HOENN_WORLD_DIR'):   # Emerald's own world (version.world_dir: pokeemerald's
    _w = version.world_dir()                                     # maps since emerald_world, notes/EMERALD.md), which the
    if not os.path.isdir(_w):                                    # patches read through HOENN_WORLD_DIR. Until the lead
        _w = os.path.join(ROOT, 'work', 'world')                 # has built work/world_emerald, Sapphire's world, said
        print(f'build_rom: WARNING no {version.world_dir()}: this Emerald ROM has Sapphire\'s maps ({_w}); '   # loudly
              f'build Emerald\'s world (HOENN_VERSION=emerald rebuild_slice.sh) to drop this fallback')
    os.environ['HOENN_WORLD_DIR'] = _w
ORIGINAL_SHA1 = 'e51e6dfb8678a3d19dcd2a10691b96a569ca0abb'

# Archives we edit get a fixed size (original + reserve), padded inside the NARC, so every build has the same ROM
# file table. The game keeps that table in RAM, so savestates only survive across builds with identical layout.
# Raising a reserve changes the layout: rebuild the base savestates (make_states.py) afterwards.
RESERVE = {
    2: 512 << 10,     # a/0/0/2 system text (place names)
    3: 1 << 20,       # a/0/0/3 script text (story chapters; v12)
    8: 40 << 20,      # a/0/0/8 map chunks (terrain ~8.1 MB + rooms + caves + standalone maps + event islands; v14: +8 MB for post-game maps; 2026-10-18: +4 MB, Emerald grew past 32 MB with the cracks fix, bridges and Battle Tents/Trainer Hill rooms; 2026-10-20: 40 MB for the Trick House, seasons and Frontier rooms)
    9: 256 << 10,     # a/0/0/9 matrices
    14: 4 << 20,      # a/0/1/4 map textures
    56: 1 << 20,      # a/0/5/6 scripts (story chapters; v12)
    126: 256 << 10,   # a/1/2/6 zone entities
    127: 64 << 10,    # a/1/2/7 wild encounters
    174: 2 << 20,     # a/1/7/4 building textures (exterior)
    175: 1 << 20,     # a/1/7/5 building textures (interior)
    225: 4 << 20,     # a/2/2/5 building packs (exterior)
    226: 2 << 20,     # a/2/2/6 building packs (interior)
    10: 64 << 10,     # a/0/1/0 map replacements
    12: 16 << 10,     # a/0/1/2 zone headers (room for nothing new; keeps edits safe)
    47: 64 << 10,     # a/0/4/7 overworld sprite table
    48: 2 << 20,      # a/0/4/8 overworld sprite sheets (Brendan, May, Birch, ...)
    71: 1 << 20,      # a/0/7/1 trainer sprites, front
    72: 1 << 20,      # a/0/7/2 trainer sprites, back
    92: 32 << 10,     # a/0/9/2 trainer parties (Sapphire's movesets written out; story_infra)
    89: 16 << 10,     # a/0/8/9 (story_infra)
}

def pad_archives(files):
    import struct
    from b2files import arc_path
    for arc, reserve in RESERVE.items():
        orig = os.path.getsize(arc_path(os.path.join(SRC_FILES), arc))
        target = (orig + reserve + 0x1FF) & ~0x1FF
        path = arc_path(files, arc)
        data = bytearray(open(path, 'rb').read())
        if len(data) > target:
            raise SystemExit(f'a/{arc:03d} is {len(data)} bytes, over its fixed size {target}: raise RESERVE[{arc}] '
                             f'and rebuild the base savestates')
        # grow the NARC's GMIF (last section) and header size, so the padding is part of a valid archive
        hdr_size = struct.unpack_from('<H', data, 0xC)[0]
        off = hdr_size
        for _ in range(2):  # BTAF, BTNF
            off += struct.unpack_from('<I', data, off + 4)[0]
        assert data[off:off+4] == b'GMIF'
        extra = target - len(data)
        struct.pack_into('<I', data, off + 4, struct.unpack_from('<I', data, off + 4)[0] + extra)
        struct.pack_into('<I', data, 8, target)
        data += bytes(extra)
        if os.path.islink(path): os.unlink(path)
        open(path + '.tmp', 'wb').write(data); os.replace(path + '.tmp', path)

def sha1(path):
    h = hashlib.sha1()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''): h.update(chunk)
    return h.hexdigest()

def write_config():
    """The decomp's ROM config with absolute paths: NitroFS from our files/ tree, code binaries (arm9, overlays,
    autoloads) from our code/ copy of the decomp's build dir, everything else (header, DSi parts) from the decomp."""
    src = open(os.path.join(SRC_BUILD, 'rom_config.yaml')).read()
    code = os.path.join(OUT, 'code')
    def absolutise(m):
        key, val = m.group(1), m.group(2).strip()
        if key == 'files_dir':
            return f'{key}: {os.path.join(OUT, "files")}'
        if val in ('null', 'false', 'true') or val == '' or re.fullmatch(r'-?(0x[0-9a-fA-F]+|\d+)', val):
            return m.group(0)
        path = os.path.normpath(os.path.join(SRC_BUILD, val))
        if os.path.dirname(path) == os.path.normpath(SRC_BUILD):   # a code file of the build dir -> our copy
            path = os.path.join(code, os.path.basename(path))
        return f'{key}: {path}'
    cfg = re.sub(r'^(\s*(?:- )?\w+): (\S.*)$', absolutise, src, flags=re.M)
    path = os.path.join(OUT, 'rom_config.yaml')
    open(path, 'w').write(cfg)
    return path

def main(args):
    clean = '--clean' in args
    pad = '--no-pad' not in args
    patches = [a for a in args if not a.startswith('--')]
    if os.environ.get('HOENN_MUSIC') and 'hoenn_music' not in patches:
        patches.append('hoenn_music')   # Hoenn's songs, last (after the zone headers): HOENN_MUSIC=hoenn, notes/MUSIC.md
    if os.environ.get('HOENN_SAVE_COMPAT', '1') != '0' and os.environ.get('HOENN_VERSION', '').strip().lower() == 'emerald' \
            and 'save_compat' not in patches:
        patches.append('save_compat')   # PKHeX-compatible Emerald saves (ON since 2026-10-18; =0 for the old layout): notes/SAVE_PKHEX.md
    if os.environ.get('HOENN_BERRY_PLANTING', '1') != '0' and 'berries' not in patches:
        patches.append('berries')       # Gen 3 berry planting (on by default since 2026-10-18; =0 = the daily trees): notes/BERRY_PLANTING.md
    files = os.path.join(OUT, 'files')
    if clean or not os.path.isdir(files):
        shutil.rmtree(files, ignore_errors=True)
        shutil.rmtree(os.path.join(OUT, 'code'), ignore_errors=True)
        os.makedirs(OUT, exist_ok=True)
        subprocess.run(['cp', '-c', '-R', '-L', SRC_FILES, files], check=True)
        # code binaries (arm9.bin, arm9_ovNNN.bin, ...): patches with apply_code(code_dir) edit this copy
        subprocess.run(['cp', '-c', '-R', '-L', SRC_BUILD, os.path.join(OUT, 'code')], check=True)
    for name in patches:
        spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, 'patches', f'{name}.py'))
        mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
        if hasattr(mod, 'apply'):
            print(f'patch {name}:', mod.apply(files) or 'ok')
        if hasattr(mod, 'apply_code'):
            print(f'patch {name} (code):', mod.apply_code(os.path.join(OUT, 'code')) or 'ok')
    if pad:
        sys.path.insert(0, HERE)
        pad_archives(files)
    cfg = write_config()
    rom = os.path.join(OUT, 'hoenn.nds')
    r = subprocess.run([os.path.join(DECOMP, 'tools', 'dsd'), 'rom', 'build', '--config', cfg, '--rom', rom],
                       capture_output=True, text=True)
    if r.returncode:
        sys.exit(r.stdout[-2000:] + r.stderr[-4000:])
    digest = sha1(rom)
    print(rom, digest)
    if not patches and clean and not pad:
        print('matches original' if digest == ORIGINAL_SHA1 else 'DOES NOT MATCH ORIGINAL')
    return rom

if __name__ == '__main__':
    main(sys.argv[1:])
