"""The regional Pokédex is Hoenn's (dex_fix, 2026-10-08; v15.3 hotfix). Data only: two archive files are rewritten at their
original sizes, so the ROM layout (and every savestate) is unchanged, and saves need no repair (the save stores seen and
caught flags by national number, never a regional number).

The bug (v15.2): opening the Pokédex showed "An error has occurred". Black 2's regional list was still the Unova one, and
Sapphire's player has only seen Hoenn Pokémon, none of them in it. How Black 2 builds the regional list (ov302, read in
fairy_ui's disassembly):
- func_ov302_021acee0 (the Pokédex proc's init) -> func_ov302_021ad624(pokedex): mode = save +4 bits 10-11
  (func_0200d1f8; 1 = national, else regional). Regional: func_ov302_021ae210 builds the list = a/0/9/7 file 4 (every
  species, the regional ones last in regional order), keeping species whose number in personal a/0/1/6 file 709
  (PML_PersonalLoadRegionalDexTable: one u16 per species, 999 = not in the dex) isn't 999. count = index of the last
  seen or caught entry + 1.
- func_ov302_021ad0e8 (starts the ov299 list): in regional mode, if func_ov302_021ad72c says Victini (0x1ee, the
  Unova dex's #000) is neither seen nor caught, the list starts at entry 1 and count - 1 goes into the ov299 param
  (+0xa). With nothing regional seen, that is 0 - 1 = 0xffff: ov299 func_ov299_021a0324 then allocates a strbuf for
  65535 entries from heap 0x6b until GFL_HeapAllocate fails and sys_exit shows the error screen. (Black 2 never gets
  there: its starter is in the Unova dex.)

The fix: Hoenn's 202 species numbered 1-202 in Sapphire's order (pokeruby include/constants/species.h HOENN_DEX_* ->
NATIONAL_DEX_*); Victini stays the hidden #000 (the engine still skips entry 0 until Victini is seen, which Hoenn never
shows), every other species 999. The start menu's seen count, the summary screen's number and Birch's dex all follow
the same table. Old v15.2 saves open the dex with no repair step: their starter is Hoenn's.
"""
import os, re, struct, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import narcio  # noqa: E402
from b2files import arc_path  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
SPECIES_H = os.path.join(ROOT, 'external', 'pokeruby', 'include', 'constants', 'species.h')
ARC_PERSONAL, FILE_REGIONAL = 16, 709      # a/0/1/6 file 709: u16 regional number per species (999 = not in it)
ARC_SORT, FILE_REGIONAL_ORDER = 97, 4      # a/0/9/7 file 4: species 1-649, the regional ones last in regional order
NONE = 999
VICTINI = 494


def hoenn_order():
    """National numbers of Hoenn #1..#202 (Sapphire's order)."""
    t = open(SPECIES_H).read()
    nat = {k: int(v) for k, v in re.findall(r'#define NATIONAL_DEX_(\w+) (\d+)', t)}
    hoenn = {int(v): nat[k] for k, v in re.findall(r'#define HOENN_DEX_(\w+) (\d+)', t) if 1 <= int(v) <= 202}
    order = [hoenn[n] for n in range(1, 203)]
    assert len(set(order)) == 202 and order[0] == 252 and order[-1] == 386, order[:3]
    return order


def apply(files):
    order = hoenn_order()
    size = {a: os.path.getsize(arc_path(files, a)) for a in (ARC_PERSONAL, ARC_SORT)}

    personal = narcio.load(files, ARC_PERSONAL)
    old = personal[FILE_REGIONAL]
    table = [NONE] * (len(old) // 2)
    table[VICTINI] = 0
    for n, species in enumerate(order, 1):
        table[species] = n
    personal[FILE_REGIONAL] = struct.pack(f'<{len(table)}H', *table)
    assert len(personal[FILE_REGIONAL]) == len(old)
    narcio.save(files, ARC_PERSONAL, personal)

    sort = narcio.load(files, ARC_SORT)
    old = sort[FILE_REGIONAL_ORDER]
    n_species = len(old) // 2
    regional = [VICTINI] + order
    rest = [s for s in range(1, n_species + 1) if s not in set(regional)]
    sort[FILE_REGIONAL_ORDER] = struct.pack(f'<{n_species}H', *(rest + regional))
    assert len(sort[FILE_REGIONAL_ORDER]) == len(old)
    narcio.save(files, ARC_SORT, sort)

    for a, n in size.items():
        assert os.path.getsize(arc_path(files, a)) == n, f'a/{a:03d} changed size: the ROM layout must stay the same'
    return f'regional Pokédex = Hoenn #1-#202 ({len(order)} species; Victini kept as the hidden #000), sizes unchanged'
