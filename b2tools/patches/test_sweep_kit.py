"""TEST ONLY (sweep_caves, 2026-10-07): test_cave_kit's field-move kit WITHOUT replacing Littleroot's other scripts.
Never in a release build.

test_cave_kit replaces Littleroot's whole script file (778) by the kit, so Littleroot's own scenes stop: a new game's
opening and walking back into Littleroot from a door go black, and savestates for a kit ROM can't be made by playing
the opening. This patch appends the kit (test_cave_kit.KIT, assembled the same way) to the end of Littleroot's real
file and points only ScriptEntry 1 (the town sign, read facing north at (183,366)) at the kit's Script_1: party (a
Mudkip if empty), 8 badges, HM01-HM06, TM70, TM94, then MapChangeCore to HOENN_TEST_WARP (+ HOENN_TEST_WARP_Y).
Everything else in Littleroot works, so a state made on a kit-free build of the same layout (b2tools make_states /
work/agents/world_fixes/tools/mkstate.py) is used like this: walk into a house and out again (Littleroot's scripts
reload from this ROM), then read the town sign.

    HOENN_TEST_WARP=zone,x,z [HOENN_TEST_WARP_Y=level] ... build_rom.py ... scripts ... hm_free ... test_sweep_kit
List it after `scripts` and `hm_free` (not together with test_cave_kit).
"""
import os, struct, importlib.util

_d = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location('test_cave_kit_', os.path.join(_d, 'test_cave_kit.py'))
_kit = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_kit)

def apply(files):
    import narcio
    zone, x, z = os.environ.get('HOENN_TEST_WARP', '389,183,365').split(',')
    blob = _kit._hm._assemble(_kit.KIT, dict(TEST_WARP_ZONE=zone, TEST_WARP_X=x, TEST_WARP_Z=z,
                                             TEST_WARP_Y=os.environ.get('HOENN_TEST_WARP_Y', '0'),
                                             TEST_WARP2_ZONE=zone, TEST_WARP2_X=x, TEST_WARP2_Z=z, TEST_WARP2_Y='0'))
    entries = narcio.load(files, 56)
    data = bytearray(entries[778])
    while len(data) % 4: data.append(0)
    base = len(data)
    kit1 = 4 + struct.unpack_from('<i', blob, 0)[0]          # the kit's Script_1 (entry 1: offset relative to after it)
    data += blob
    struct.pack_into('<i', data, 0, base + kit1 - 4)          # Littleroot's entry 1 -> the kit's Script_1
    entries[778] = bytes(data)
    narcio.save(files, 56, entries)
    return f'TEST ONLY: Littleroot town sign (entry 1) = field-move kit + warp to {zone},{x},{z} (rest of 778 kept)'
