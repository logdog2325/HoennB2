"""Assemble src/field_scripts/NNNN_*.s with the decomp's field-script macros (clang, as the decomp's build does) and put
each one into the script archive a/0/5/6 as entry NNNN."""
import os, sys, json, glob, subprocess, tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import narcio, version
ROOT = os.path.join(os.path.dirname(__file__), '..', '..')
SRC = os.path.join(ROOT, 'src', 'field_scripts')   # + src/field_scripts/ruby/ in a Ruby build (version.overlay)
DECOMP = os.path.abspath(os.path.join(ROOT, 'external', 'pokebw2'))
LLVM = '/opt/homebrew/opt/llvm/bin'

def assemble(src):
    """Assemble one field-script source with the decomp's macros; returns the binary."""
    with tempfile.TemporaryDirectory() as t:
        o, b = os.path.join(t, 'x.o'), os.path.join(t, 'x.bin')
        test = [a for v in ('HOENN_TEST_PARTY', 'HOENN_TEST_TRUCK', 'HOENN_TEST_SPRITES', 'HOENN_TEST_MOVES', 'HOENN_TEST_TWO', 'HOENN_TEST_GAME_CLEAR', 'HOENN_TEST_COMMON') if os.environ.get(v) for a in ('-D', v)]   # see 0778 Script_9 / Script_1 / Script_2; scenes/Route131.inc
        # chapter test switches (notes/STORY_PORTING.md "Test switches"): every HOENN_TEST_CH<n>=v in the environment
        # is passed on as -D HOENN_TEST_CH<n>=v, so a chapter's scene file can #ifdef its start-of-chapter setup
        test += [a for k, v in sorted(os.environ.items()) if k.startswith('HOENN_TEST_CH') for a in ('-D', f'{k}={v}')]
        if os.environ.get('HOENN_TEST_SPRITES'):  # "trainer,code" (or 1 = 345,353): Littleroot's town sign (0778 Script_1)
            v = os.environ['HOENN_TEST_SPRITES']; trainer, code = v.split(',') if ',' in v else ('345', '353')
            test += ['-D', f'TEST_SPRITES_TRAINER={trainer}', '-D', f'TEST_SPRITES_CODE={code}']
        if os.environ.get('HOENN_TEST_WARP'):     # "zone,x,z": Littleroot's town sign warps there (0778 Script_1)
            zone, x, z = os.environ['HOENN_TEST_WARP'].split(',')
            test += ['-D', 'HOENN_TEST_WARP', '-D', f'TEST_WARP_ZONE={zone}', '-D', f'TEST_WARP_X={x}', '-D', f'TEST_WARP_Z={z}']
        test += version.ASM_DEFINES      # -D HOENN_SAPPHIRE / HOENN_RUBY, HOENN_VERSION_ID (src/include/hoenn_version.inc)
        if os.environ.get('HOENN_BERRY_PLANTING', '1') != '0':   # berry planting (notes/BERRY_PLANTING.md; off by default:
            test += ['-D', 'HOENN_BERRY_PLANTING']          #  1241_hidden_items.s, scenes/Route130.inc)
        subprocess.run([f'{LLVM}/clang', '--target=armv5te-none-eabi', '-x', 'assembler-with-cpp', '-c', *test,
                        '-I', f'{DECOMP}/include', '-I', f'{DECOMP}/lib/nitro/include', '-I', f'{DECOMP}/build/include/generated',   # the newer decomp's generated constants headers (notes/POKEBW2_UPGRADE.md; absent = ignored)
                        '-I', os.path.join(ROOT, 'src', 'include'), '-I', os.path.join(ROOT, 'src', 'field_scripts'), '-D', 'BLACK2',   # field_scripts: "common/x.inc" (notes/STORY_COMMON.md)
                        '-o', o, os.path.abspath(src)], check=True, cwd=DECOMP)
        # an unknown name (e.g. a FLAG_ without #include "hoenn.h") would silently assemble as 0: refuse it
        undef = subprocess.run([f'{LLVM}/llvm-nm', '--undefined-only', o], capture_output=True, text=True, check=True).stdout.split()
        undef = [w for w in undef if w != 'U']
        if undef: raise SystemExit(f'{src}: undefined names {undef}')
        subprocess.run([f'{LLVM}/llvm-objcopy', '-O', 'binary', o, b], check=True)
        return open(b, 'rb').read()

def source_for(num):
    """Our source file for script-archive entry num, or None."""
    found = version.overlay(SRC, f'{num:04d}_*.s')      # a Ruby file in src/field_scripts/ruby/ replaces Sapphire's
    return found[0] if found else None

def room_numbers():
    """Black 2 script-file number of a Hoenn room -> the room's own number after Black 2's files
    (data/hoenn_interiors.json own_scripts/own_init, converter/allocate_interiors.py): room files are named after the
    zone's Black 2 numbers but must not overwrite Black 2's files (code reads some directly: a cold boot hung)."""
    p = os.path.join(ROOT, 'data', 'hoenn_interiors.json')
    # (version.load_json: an Emerald build adds data/emerald/hoenn_interiors.json's claimed rooms, the Battle Frontier's;
    # Sapphire and Ruby have no such file: the same numbers as before; frontier_factory_dome 2026-10-12)
    rooms = version.load_json(p)['rooms'].values() if os.path.exists(p) else []
    return {r[a]: r[b] for r in rooms if 'own_scripts' in r for a, b in (('scripts', 'own_scripts'), ('init_scripts', 'own_init'))}

def apply(files):
    entries = narcio.load(files, 56)
    done = []
    moved = room_numbers()
    for src in version.overlay(SRC, '*.s'):
        num = moved.get(int(os.path.basename(src)[:4]), int(os.path.basename(src)[:4]))
        while len(entries) <= num: entries.append(b'')    # new files after Black 2's (rooms' own script files)
        entries[num] = assemble(src)
        done.append(f'{num} ({len(entries[num])} B)')
    while moved and len(entries) <= max(moved.values()): entries.append(b'')   # every room's own number exists (as
    # the files before it: a room whose number lies past the last source, e.g. a cave's init file, had none; caves_east)
    narcio.save(files, 56, entries)
    return 'scripts ' + ', '.join(done)
