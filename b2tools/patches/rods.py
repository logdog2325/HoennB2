"""The Old Rod and the Good Rod (rods_fix, 2026-10-12; Discord bug report: the Old Rod has no Use or Register option).
All three rods can be used from the Bag and registered to Y, and each rod fishes its own table: the Old Rod Sapphire's
Old Rod Pokémon, the Good Rod the Good Rod's, the Super Rod the Super Rod's, in Sapphire's slot order and odds (Ruby's /
Emerald's tables in those versions: converter/gen_encounters.py and gen_caves.py write them).

What Black 2 has [code: decomp symbols + dsd disassembly; bytes: the decomp's build]:
  - Only the Super Rod (447) is a fishing rod. Items 445/446 are Gen 4 leftovers: a/0/2/4 +8 = 0x021f (bits 5 and 6
    clear: "Give" offered, no "Register"), +0xA field use 0 (no "Use"); Super Rod +8 = 0x027f, +0xA = 18
    (notes/RESEARCH_EXPSHARE_HM.md: the Bag's menu shows Use when +0xA != 0, Give/Toss when bit 5 is clear, Register when
    bit 6 is set; tested: the Old Rod showed USE, GIVE, REGISTER with only bit 6 set). The Good Rod's +0x10 is 1 (Old Rod
    0, Super Rod 2): for an item with +0xC = 0, PML_ItemGetParam returns +0x10 for every param above 0x11, and the Bag's
    Use (func_ov142_0219a4d0) sends an item whose param 0x1d is 1 down the "use on a Pokémon" path instead of the Use
    table (tested: "It won't have any effect." for the Good Rod, fishing for the other two).
  - Bag Use: ov142 key-item table (0x021a0980, {u16 first item, u16 count, handler}) entry 4 {447, 1, func_ov142_0219a404}:
    if action 5 (fishing: FieldActionBlockCheck_Surf = water in front and no partner) is not blocked, leave the Bag with
    result 16, which the field turns into common event 4 (FIELD_COMMON_EVENTS: EventFieldFishing_Create); else message
    0x3a ("can't use") / 0x77 (partner). The item is not passed on: the fishing event never knows the rod.
  - Register: arm9 data_020929f8, 13 x u16 {item (bits 0-9), Y shortcut id (bits 10-15)}, read by func_02034aa4 (the Bag's
    Register and its registered mark); 447 -> shortcut 4. The Y menu lists shortcut ids by name (system text 365, line =
    id) and runs them through ov012 ShortcutMenu_SetKeyItemID (4 -> event 4, fishing) and
    ShortcutMenu_GetActionFromKeyItem (4 -> check action 5).
  - Fishing: EventFieldFishing_Create -> BtlSetup_CreateFishing(enc, phenomenon) (ov036 0x021a19fc): type 5 (6 on a
    rippling spot), no fish if that rate byte is 0, bite roll (rate 50 + abilities), then FieldEncount_GenWilds (enc,
    manager, zone, out) = PrepareActiveSlots (type 5: the 5 fishing slots at enc+0xc0, odds kind 2 = ENCOUNTRATE_RND5T2
    40/40/15/4/1, Sapphire's Super Rod odds) + GenWildsCore (slot roll, level, Repel).
  - Rippling water: UpdatePhenomenon (ov036 0x021a206c) spawns spots only in zones whose shaking-grass, rippling-surf or
    rippling-fishing rate is set; every Hoenn table has them 0, so no spot ever appears and the 5 rippling-fishing slots
    (enc+0xd4) are never read. They hold the Old Rod's 2 + the Good Rod's 3 slots (gen_encounters.fishing_lines).
What this patch does:
  1. a/0/2/4 items 445, 446: +8 |= 0x60 (no Give, Register: 0x027f, the Super Rod's), +0xA = 18 (Use; the Super Rod's);
     the Good Rod's +0x10 1 -> 0 (the Old Rod's value: not a "use on a Pokémon" item).
  2. ov142 key-item table entry 4 -> {445, 3, Rod_BagUse}: remembers the rod, then Black 2's Super Rod handler.
  3. arm9 data_020929f8 entries 10/11 (628 DNA Splicers -> 7, 629 -> 8; not in Hoenn) -> Old Rod -> 7, Good Rod -> 8;
     their Y-menu names (system 365 lines 7/8) come from src/text/overrides_rods.json.
  4. ov012 0x0215ac4a, 0x0215ae8c (bl ShortcutMenu_GetActionFromKeyItem) -> Rod_GetAction and 0x0215ac54, 0x0215ae80
     (bl ShortcutMenu_SetKeyItemID) -> Rod_SetKeyItemID: shortcuts 7/8 remember the rod and act as 4.
  5. ov036 0x021a1a82 in BtlSetup_CreateFishing: bl FieldEncount_GenWilds -> Rod_GenWilds (rods.c: Old/Good Rod = the
     rod's own slots with Sapphire's odds; the Super Rod = Black 2's call).
  The rod variable is a u16 in ITCM just before the code (0 at boot, not saved). Rippling fishing (never in Hoenn) and
  every other battle are unchanged.
Code space: ITCM after the other patches' code (the arena literal arm9 0x0207B400, as roamers.py). Main-RAM code: savestates
made before need a cold boot (a state of your own ROM: work/agents/world_fixes/tools/mkstate.py)."""
import os, re, struct, subprocess, sys, tempfile, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
DECOMP = os.path.join(ROOT, 'external', 'pokebw2')
sys.path.insert(0, os.path.dirname(HERE))
import narcio  # noqa: E402
LLVM = '/opt/homebrew/opt/llvm/bin'
ITCM_BASE, ARENA_ITCM_LIT, ARM9 = 0x01FF8000, 0x0207B400, 0x02004000
OV012, OV036, OV142 = 0x021503C0, 0x0217F600, 0x021998C0      # overlays.yaml base addresses

ITEM_OLD_ROD, ITEM_GOOD_ROD, ITEM_SUPER_ROD = 445, 446, 447
FIELD_USE_ROD = 18                       # a/0/2/4 +0xA of the Super Rod
KEY_FLAGS = 0x60                         # a/0/2/4 +8 bit 5 (no Give/Toss) and bit 6 (Register), as the Super Rod
KEY_ITEM_USE_ENTRY = 0x021A0980 + 4 * 8  # ov142: entry 4 of the Bag's key-item Use table
SUPER_ROD_HANDLER = 0x0219A404           # func_ov142_0219a404
SHORTCUT_TABLE = 0x020929F8              # arm9 data_020929f8 (13 x u16)
SHORTCUTS = {10: (628, 7, ITEM_OLD_ROD), 11: (629, 8, ITEM_GOOD_ROD)}   # entry: (Black 2's item, id, rod)
SET_KEY_ITEM_ID, GET_ACTION = 0x0215B010, 0x0215B1EC
OV012_CALLS = [(0x0215AC4A, GET_ACTION, 'Rod_GetAction'), (0x0215AC54, SET_KEY_ITEM_ID, 'Rod_SetKeyItemID'),
               (0x0215AE80, SET_KEY_ITEM_ID, 'Rod_SetKeyItemID'), (0x0215AE8C, GET_ACTION, 'Rod_GetAction')]
GEN_WILDS_CALL, GEN_WILDS = 0x021A1A82, 0x021A0C38                   # BtlSetup_CreateFishing -> FieldEncount_GenWilds


def _roamers():
    spec = importlib.util.spec_from_file_location('roamers_link', os.path.join(HERE, 'roamers.py'))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


def _bl(src, dst):
    off = dst - (src + 4)
    assert -(1 << 22) <= off < (1 << 22) and not off & 1, hex(off)
    return struct.pack('<HH', 0xF000 | (off >> 12) & 0x7FF, 0xF800 | (off >> 1) & 0x7FF)


def _put(d, base, addr, old, new, what):
    """Write new at addr (old = the expected bytes; already new is fine: a rerun)."""
    o = addr - base
    cur = bytes(d[o:o + len(new)])
    assert cur in (old, new), f'{what} at {addr:#x}: {cur.hex()} (expected {old.hex()})'
    d[o:o + len(new)] = new


def _load(code, name):
    p = os.path.join(code, name); return p, bytearray(open(p, 'rb').read())


def _save(p, d):
    if os.path.islink(p): os.unlink(p)
    open(p + '.tmp', 'wb').write(d); os.replace(p + '.tmp', p)


def apply(files):
    """Items 445/446: Use and Register, no Give, as the Super Rod (Black 2's other bytes kept)."""
    entries = narcio.load(files, 24)
    vanilla = narcio.load(os.path.join(DECOMP, 'build', 'b2_us', 'files'), 24)
    for item in (ITEM_OLD_ROD, ITEM_GOOD_ROD):
        d = bytearray(entries[item])
        assert bytes(d) == vanilla[item] or d[10] == FIELD_USE_ROD, f'item {item}: unexpected data {bytes(d).hex()}'
        struct.pack_into('<H', d, 8, struct.unpack_from('<H', d, 8)[0] | KEY_FLAGS)
        d[10] = FIELD_USE_ROD
        assert d[0x10] in (0, 1), f'item {item}: +0x10 = {d[0x10]}'
        d[0x10] = 0                      # (Good Rod: 1 = "use on a Pokémon" for the Bag's Use, see above)
        entries[item] = bytes(d)
    narcio.save(files, 24, entries)
    return f'items {ITEM_OLD_ROD}, {ITEM_GOOD_ROD}: Use + Register, no Give (field use {FIELD_USE_ROD})'


def build(base, workdir):
    """rods.c linked at base + 4 (the rod variable is the u16 at base)."""
    obj = os.path.join(workdir, 'rods.o')
    subprocess.run([f'{LLVM}/clang', '--target=thumbv5te-none-eabi', '-mthumb', '-march=armv5te', '-Os', '-ffreestanding',
                    '-fno-builtin', '-fno-jump-tables', '-fno-pic', '-fno-unwind-tables', '-fno-asynchronous-unwind-tables',
                    '-fno-exceptions', '-fno-common', '-mno-unaligned-access', '-Wall', '-Werror', f'-DROD_VAR={base:#x}',
                    '-c', os.path.join(HERE, 'rods.c'), '-o', obj], check=True)
    und = subprocess.run([f'{LLVM}/llvm-nm', '--undefined-only', obj], capture_output=True, text=True, check=True).stdout.split()
    assert not und, f'rods.c needs {und}: call Black 2 functions by address only'
    return _roamers().link(obj, base + 4)


def apply_code(code):
    yml = os.path.join(code, 'itcm.yaml')
    text = open(yml).read()
    size = int(re.search(r'^code_size: (\d+)$', text, re.M).group(1))
    assert re.search(r'^base_address: (\d+)$', text, re.M).group(1) == str(ITCM_BASE)
    base = ITCM_BASE + size
    p9, arm9 = _load(code, 'arm9.bin')
    lit = ARENA_ITCM_LIT - ARM9
    assert struct.unpack_from('<I', arm9, lit)[0] == base, 'the ITCM arena literal is not at the end of ITCM (run rods after hoenn_world)'
    with tempfile.TemporaryDirectory(dir=code) as tmp:
        blob, sym = build(base, tmp)
    end = (base + 4 + len(blob) + 31) & ~31
    assert end <= 0x02000000, f'ITCM full: {end:#x}'
    struct.pack_into('<I', arm9, lit, end)
    pi, itcm = _load(code, 'itcm.bin')
    assert len(itcm) == size
    _save(pi, bytes(itcm) + bytes(4) + blob + bytes(end - base - 4 - len(blob)))
    open(yml, 'w').write(re.sub(r'^code_size: \d+$', f'code_size: {end - ITCM_BASE}', text, flags=re.M))
    # 3. Y shortcut ids of the Old and Good Rods
    for i, (old_item, sc, rod) in SHORTCUTS.items():
        a = SHORTCUT_TABLE + 2 * i
        _put(arm9, ARM9, a, struct.pack('<H', old_item | sc << 10), struct.pack('<H', rod | sc << 10), 'shortcut table')
    _save(p9, arm9)
    # 2. the Bag's Use
    p142, ov142 = _load(code, 'arm9_ov142.bin')
    _put(ov142, OV142, KEY_ITEM_USE_ENTRY, struct.pack('<HHI', ITEM_SUPER_ROD, 1, SUPER_ROD_HANDLER | 1),
         struct.pack('<HHI', ITEM_OLD_ROD, 3, sym['Rod_BagUse'] | 1), 'key-item Use table (Super Rod entry)')
    _save(p142, ov142)
    # 4. the Y menu
    p012, ov012 = _load(code, 'arm9_ov012.bin')
    for at, old, new in OV012_CALLS:
        _put(ov012, OV012, at, _bl(at, old), _bl(at, sym[new] & ~1), f'bl {old:#x}')
    _save(p012, ov012)
    # 5. the fishing encounter
    p036, ov036 = _load(code, 'arm9_ov036.bin')
    _put(ov036, OV036, GEN_WILDS_CALL, _bl(GEN_WILDS_CALL, GEN_WILDS), _bl(GEN_WILDS_CALL, sym['Rod_GenWilds'] & ~1),
         'BtlSetup_CreateFishing: bl FieldEncount_GenWilds')
    _save(p036, ov036)
    return (f'rods: {len(blob)} B of ITCM at {base + 4:#x} (rod variable {base:#x}, arena from {end:#x}); Bag Use '
            f'{ITEM_OLD_ROD}-{ITEM_SUPER_ROD}, Y shortcuts 7/8, fishing table by rod')


if __name__ == '__main__':                       # python3 rods.py: compile and link at a dummy base
    with tempfile.TemporaryDirectory() as tmp:
        blob, sym = build(0x01FFDE00, tmp)
        print(len(blob), {k: hex(v) for k, v in sym.items() if k.startswith('Rod_')})
