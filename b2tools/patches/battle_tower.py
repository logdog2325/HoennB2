"""Sapphire's Battle Tower on Black 2's Battle Subway engine (battle_tower agent, 2026-10-08; notes/BATTLE_TOWER.md).

The tower's rooms (zones 21 lobby, 343 elevator, 336 corridor, 15 battle room; data/interiors) run Sapphire's scripts
(src/field_scripts/0042/0043 lobby, 0686 elevator, 0672 corridor, 0030 battle room) with Black 2's Battle Subway script
plugin (plugin 1: ov050 BSubwayCmd_Tool + ov033 bsubway_scr.c) for the party choice, the seven trainers, the battles
and the streak bookkeeping. Sapphire's Lv. 50 room = Black 2 play mode 0 (Single Train), its Lv. 100 room = play mode 5
(Super Single Train). Battle Subway trainer id t: arc 212 file t + 1, system text 15 line t (name), 376 lines 3t (the
greeting before the battle), 3t + 1 / 3t + 2 (Black 2's in-battle win / lose lines). Sapphire's trainer k (0-99) is id
k with its Lv. 50 sets and id 100 + k with its Lv. 100 sets.

apply_code (all same-size edits; addresses from the decomp's b2_us symbols, checked in the disassembly):
  ov012
  - sBSubwayZones (0x0216c156, 11 u16 = zones 66-76; plugin 1 loads only there, script_plugin.c): entries 9 and 10, Black
    2's Battle Subway platforms 75/76 (no Hoenn map uses them: allocate_zones.py DENY), become the tower's lobby (21) and
    battle room (15), the two rooms whose scripts use plugin 1. 66-74 stay (Hoenn rooms that never call plugin 1).
  - BtlSetup_SetTrialHouseParty 0x02161fac-0x02161fbb (the 8 instructions before `bl LoadTrialHouseParty` at 0x02161fbc):
    the opponents' level, Black 2's constant 50 (`movs r2, #50` at 0x02161fba), becomes 50 + 10 x play mode: mode 0 = 50,
    mode 5 = 100 (Sapphire's Lv. 100 trainers are level 100). `add r0, sp, #32; ldrh r0, [r0, #4]` (the heap id, the
    constant 4 at all three call sites: SetupTrialHouseBattle 0x02162010 / 0x02162030 / 0x0216204c) becomes a `bl` to a
    helper in ov033 that sets r0 = 4 and r2 = the level; `movs r2, #50` becomes a nop.
  - SetupTrialHouseBattle 0x02162006 `movs r3, #50` (RestrictPlayerParty's level: every chosen Pokémon set to exactly 50)
    -> 0 (RestrictPlayerParty skips the level when it is 0): the player's Pokémon battle at their own levels, as in
    Sapphire (the Lv. 50 room only takes Pokémon of Level 50 or less, below).
  - func_ov012_02162828 (the trainer's IVs by trainer id, its only caller func_ov012_02162864 0x02162884): Sapphire's
    FillBattleTowerTrainerParty fixed IVs by trainer k = id mod 100: k < 20: 6, < 30: 9, < 40: 12, < 50: 15, < 60: 18,
    < 70: 21, else 31.
  - genSubwayBtlInstitutePoke 0x0216274a `bl PokeParty_SetNature` (the set's nature) -> `bl PokeParty_RecalcStats`:
    the nature stays PML_CreatePkm's random one (GFL_RandomLC(25), arm9 0x0201c77e), as Sapphire (CreateMon with a random
    personality: the sets' .nature is never read); the stats are recalculated as SetNature did.
  - func_ov012_02165f70 (script command 300, the party list) 0x02165fd4 `movs r0, #20; str r0, [sp, #4]` (the
    regulation of play modes 0/4/5) -> `bl` a helper in ov033 (below): mode 0 takes REG_LV50 (arc 106 file 38, written
    here: Black 2's regulation 20 with level mode 2 = "Level 50 or less", func_0201f09c), the others 20 (level mode 3:
    no level check = Sapphire's Lv. 100 room). ov033 is loaded whenever the field is (ov036 FieldRoutine_Open).
  ov033
  - func_ov033_0217c11c (0x148 bytes: the trainer of each of the seven battles, called by func_ov033_0217b9dc with the
    sets won in this streak, the battle 0-6 and the play mode; r4-r7 preserved): Sapphire's ChooseNextBattleTowerTrainer:
    challenge c = sets won + 1; c <= 7: battles 1-6 one of trainers (c-1)*10 + 0..19 ((rand & 0xFF) * 5 >> 6), battle 7
    one of (c-1)*10 + 20..29 ((rand & 0xFF) * 5 >> 7); c >= 8: one of 70..99 ((rand & 0xFF) * 30 >> 8); + 100 in play mode
    5. Black 2's caller keeps the seven different. The regulation helper follows it in the freed bytes.
  - func_ov033_0217bca0 (command 308, the opponent's field sprite: tail call `ldr r3, =func_ov012_02162b38; bx r3` with
    the trainer's class): its literal (0x0217bcb0) -> a lookup in the freed bytes with the tower's own {class, sprite}
    pairs (data/battle_tower.json "sprite": Sapphire's OBJ_EVENT_GFX via data/sprite_map.json) for the classes whose
    sprite differs from Black 2's table data_ov012_0216d9b4 or is missing from it (Black 2 then shows object 10); other
    classes fall through to Black 2's lookup. Black 2's table is left alone (the PWT reads it, ov135 0x021ef6fc).
apply
  - arc 211 (Battle Subway sets, 16 bytes: u16 species, 4 x u16 moves, u8 EV flags, u8 nature, u16 item, u16 form)
    files 0-299 = Sapphire's level_50_mons.h, 300-599 = level_100_mons.h; arc 212 (u16 class, u16 count, u16 sets[])
    files 1-200 = the 100 trainers twice, each listing exactly the sets Sapphire's FillBattleTowerTrainerParty may draw
    for it (data/battle_tower.json, converter/gen_battle_tower.py); both archives keep their size (arc 212 padded).
  - arc 106 file 38 (REG_LV50, appended).
  The names and lines (system texts 15 and 376) are src/text/overrides_battle_tower.json, read by the text patch."""
import os, sys, json, struct
import narcio
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, HERE)

OV012_BASE, OV033_BASE = 0x021503c0, 0x02176b00
BUILD = os.path.join(ROOT, 'external', 'pokebw2', 'build', 'b2_us', 'build')
BSUBWAY_ZONES = 0x0216c156
TOWER_PLUGIN_ZONES = {9: 21, 10: 15}            # sBSubwayZones index -> zone (75 -> lobby, 76 -> battle room)
TRAINER_CHOICE, TRAINER_CHOICE_SIZE = 0x0217c11c, 0x148
RAND = 0x0217c328                               # randFFFFFFFFdivFFFF (bsubway_scr.c)
IV_FUNC, IV_FUNC_SIZE = 0x02162828, 0x3c
SET_NATURE_CALL, SET_NATURE, RECALC_STATS = 0x0216274a, 0x0201d5e0, 0x0201d5f4
REG_CALL = 0x02165fd4
CLASS_SPRITE, CLASS_SPRITE_TABLE = 0x02162b38, 0x0216d9b4   # func_ov012_02162b38: class -> field sprite
SPRITE_LIT = 0x0217bcb0                         # func_ov033_0217bca0's literal (`ldr r3, =0x02162b39; bx r3`)
MODE_LV100 = 5                                  # play mode of the Lv. 100 room (Super Single Train)
LV100_IDS = 100                                 # trainer id of Sapphire trainer k in the Lv. 100 room: 100 + k
REG_LV50, REG_BASE = 38, 20                     # arc 106 files
LV100_SETS = 300                                # arc 211 file of the first Lv. 100 set

def _thumb():
    import importlib.util
    spec = importlib.util.spec_from_file_location('exp_share_bt', os.path.join(HERE, 'exp_share.py'))
    es = importlib.util.module_from_spec(spec); spec.loader.exec_module(es)
    return es.Thumb

def ov033_code():
    """The new func_ov033_0217c11c and, after it, the regulation helper; returns (bytes, helper address)."""
    T = _thumb()
    t = T(TRAINER_CHOICE)            # in: r0 bsw, r1 sets won (u16), r2 battle 0-6, r3 play mode; out: r0 trainer id
    t.push([4, 5, 6])
    t.mov(4, 1); t.mov(5, 2); t.mov(6, 3)
    t.bl(RAND)                       # r0 = rand (bsw is ignored)
    t.lsls(0, 0, 24); t.lsrs(0, 0, 24)              # & 0xFF
    t.cmp(4, 7); t.bcc('hs', 'late')                # challenge 8+ (7 sets won)
    t.cmp(5, 6); t.beq('last')
    t.movs(1, 5); t.muls(0, 1); t.lsrs(0, 0, 6)     # battles 1-6: 0..19
    t.b('tier')
    t.label('last')
    t.movs(1, 5); t.muls(0, 1); t.lsrs(0, 0, 7); t.addi(0, 20)   # battle 7: 20..29
    t.label('tier')
    t.movs(1, 10); t.muls(1, 4); t.addsr(0, 0, 1)   # + (c - 1) * 10
    t.b('mode')
    t.label('late')
    t.movs(1, 30); t.muls(0, 1); t.lsrs(0, 0, 8); t.addi(0, 70)  # 70..99
    t.label('mode')
    t.cmp(6, MODE_LV100); t.bne('done')
    t.addi(0, LV100_IDS)
    t.label('done')
    t.lsls(0, 0, 16); t.lsrs(0, 0, 16)
    t.pop([4, 5, 6])
    while t.pc & 3: t.nop()
    helper = t.pc                    # called from func_ov012_02165f70 (r5 = bsw; [sp+4] = its regulation slot)
    t.ldrb_off(0, 5, 9)              # play mode
    t.cmp(0, 0); t.bne('other')
    t.movs(0, REG_LV50); t.b('store')
    t.label('other'); t.movs(0, REG_BASE)
    t.label('store'); t.str_sp(0, 4); t.h(0x4770)   # bx lr
    level_helper = t.pc              # called from BtlSetup_SetTrialHouseParty (r7 = play mode): r0 = heap 4, r2 = level
    t.movs(0, 4); t.movs(2, 10); t.muls(2, 7); t.addi(2, 50); t.h(0x4770)
    sprite = t.pc                    # tail-called by func_ov033_0217bca0 (command 308), r0 = the trainer's class
    pairs = sprite_pairs()
    t.ldr_lit(2, 'tab'); t.movs(3, len(pairs))
    t.label('sl')
    t.ldrh_off(1, 2, 0); t.cmpr(0, 1); t.beq('sf')
    t.addi(2, 4); t.subi(3, 1); t.bne('sl')
    t.ldr_lit(3, 'b2'); t.h(0x4718)  # bx r3: Black 2's func_ov012_02162b38 for any other class
    t.label('sf')
    t.ldrh_off(0, 2, 2); t.h(0x4770)
    t.word('b2', CLASS_SPRITE | 1)
    t.word('tab', t.pc + 4)
    for c, s in pairs: t.h(c); t.h(s)
    blob = t.assemble()
    assert len(blob) <= TRAINER_CHOICE_SIZE, len(blob)
    return blob + bytes.fromhex('c046') * ((TRAINER_CHOICE_SIZE - len(blob)) // 2), helper, level_helper, sprite

def sprite_pairs():
    """(class, sprite) of the tower's trainer classes whose field sprite is not Black 2's own for that class (Black 2's
    table data_ov012_0216d9b4: 53 x {u16 class, u16 object code}, missing classes get 10). Black 2's table stays as it
    is: the PWT (ov135 0x021ef6fc) reads it too."""
    v12 = open(os.path.join(BUILD, 'arm9_ov012.bin'), 'rb').read()
    o = CLASS_SPRITE_TABLE - OV012_BASE
    b2 = dict(struct.unpack_from('<HH', v12, o + 4 * i) for i in range(53))
    bt = json.load(open(os.path.join(ROOT, 'data', 'battle_tower.json')))
    ours = {}
    for t in bt['trainers']:
        assert ours.setdefault(t['b2_class'], t['sprite']) == t['sprite'], t['name']     # one sprite per class
    return sorted((c, s) for c, s in ours.items() if b2.get(c) != s)

def opponent_level(level_helper):
    """The 16 bytes 0x02161fac-0x02161fbb: Black 2's instructions with the heap load replaced by `bl level_helper` and
    `movs r2, #50` by a nop (r2 is not touched in between)."""
    T = _thumb()
    t = T(0x02161fac)                # r5 setup, r6 party data, r4 slot * 4, r7 play mode; [sp+32] count
    t.bl(level_helper)               # r0 = 4 (heap), r2 = 50 + 10 * mode
    t.addsr(1, 5, 4)                 # adds r1, r5, r4
    t.ldr_sp(3, 32)                  # ldr r3, [sp, #32]   (count)
    t.str_sp(0, 0)                   # str r0, [sp]        (heap)
    t.ldr_off(1, 1, 36)              # ldr r1, [r1, #36]   (setup->party[slot])
    t.mov(0, 6)                      # adds r0, r6, #0
    t.nop()                          # (was movs r2, #50)
    blob = t.assemble()
    assert len(blob) == 16, len(blob)
    return blob

def iv_func():
    T = _thumb()
    t = T(IV_FUNC)                   # in r0 trainer id, out r0 IV (all six)
    t.cmp(0, LV100_IDS); t.bcc('lo', 'k'); t.subi(0, LV100_IDS)
    t.label('k')
    for i, (lim, iv) in enumerate(((20, 6), (30, 9), (40, 12), (50, 15), (60, 18), (70, 21))):
        t.cmp(0, lim); t.bcc('hs', f'n{i}'); t.movs(0, iv); t.h(0x4770)
        t.label(f'n{i}')
    t.movs(0, 31); t.h(0x4770)
    blob = t.assemble()
    assert len(blob) <= IV_FUNC_SIZE, len(blob)
    return blob + bytes.fromhex('c046') * ((IV_FUNC_SIZE - len(blob)) // 2)

def _bl(at, target):
    T = _thumb(); t = T(at); t.bl(target); return t.assemble()

def apply_code(code):
    v12 = open(os.path.join(BUILD, 'arm9_ov012.bin'), 'rb').read()
    v33 = open(os.path.join(BUILD, 'arm9_ov033.bin'), 'rb').read()
    def orig(v, base, addr, n): return v[addr - base:addr - base + n]
    choice, helper, level_helper, sprite = ov033_code()
    edits12 = [(BSUBWAY_ZONES + 2 * i, struct.pack('<H', 66 + i), struct.pack('<H', z)) for i, z in TOWER_PLUGIN_ZONES.items()]
    edits12 += [(0x02161fac, orig(v12, OV012_BASE, 0x02161fac, 16), opponent_level(level_helper)),
                (0x02162006, bytes.fromhex('3223'), bytes.fromhex('0023')),
                (IV_FUNC, orig(v12, OV012_BASE, IV_FUNC, IV_FUNC_SIZE), iv_func()),
                (SET_NATURE_CALL, _bl(SET_NATURE_CALL, SET_NATURE), _bl(SET_NATURE_CALL, RECALC_STATS)),
                (REG_CALL, bytes.fromhex('14200190'), _bl(REG_CALL, helper))]
    edits33 = [(TRAINER_CHOICE, orig(v33, OV033_BASE, TRAINER_CHOICE, TRAINER_CHOICE_SIZE), choice),
               (SPRITE_LIT, struct.pack('<I', CLASS_SPRITE | 1), struct.pack('<I', sprite | 1))]
    for name, base, edits in (('arm9_ov012.bin', OV012_BASE, edits12), ('arm9_ov033.bin', OV033_BASE, edits33)):
        path = os.path.join(code, name)
        d = bytearray(open(path, 'rb').read())
        for addr, old, new in edits:
            o = addr - base
            assert len(old) == len(new), (hex(addr), len(old), len(new))
            assert d[o:o + len(old)] in (old, new), f'{name} {addr:#x}: {d[o:o + len(old)].hex()} is not Black 2\'s'
            d[o:o + len(new)] = new
        if os.path.islink(path): os.unlink(path)
        open(path, 'wb').write(d)
    return (f'plugin 1 zones 75/76 -> {TOWER_PLUGIN_ZONES[9]}/{TOWER_PLUGIN_ZONES[10]}; opponents level 50 + 10 x mode; '
            f'player keeps levels; Sapphire IVs, random natures, trainer choice; Lv. 50 regulation {REG_LV50} '
            f'(helper {helper:#x}); field sprites of {len(sprite_pairs())} classes (lookup {sprite:#x})')

def set_record(m):
    flags = sum(1 << ['HP', 'ATTACK', 'DEFENSE', 'SPEED', 'SP_ATTACK', 'SP_DEFENSE'].index(e) for e in m['ev'])
    moves = (m['move_ids'] + [0, 0, 0, 0])[:4]
    nature = NATURES.index(m['nature'])
    return struct.pack('<H4HBBHH', m['species_id'] & 0x7ff, *moves, flags, nature, m['item_id'], 0)

NATURES = ['NATURE_HARDY', 'NATURE_LONELY', 'NATURE_BRAVE', 'NATURE_ADAMANT', 'NATURE_NAUGHTY', 'NATURE_BOLD',
           'NATURE_DOCILE', 'NATURE_RELAXED', 'NATURE_IMPISH', 'NATURE_LAX', 'NATURE_TIMID', 'NATURE_HASTY',
           'NATURE_SERIOUS', 'NATURE_JOLLY', 'NATURE_NAIVE', 'NATURE_MODEST', 'NATURE_MILD', 'NATURE_QUIET',
           'NATURE_BASHFUL', 'NATURE_RASH', 'NATURE_CALM', 'NATURE_GENTLE', 'NATURE_SASSY', 'NATURE_CAREFUL',
           'NATURE_QUIRKY']

def _pad_save(files, arc, entries, size):
    """Write a NARC no bigger than `size` (the original), padded with zeros to it: no later ROM file moves."""
    narcio.save(files, arc, entries)
    from b2files import arc_path
    p = arc_path(files, arc)
    data = open(p, 'rb').read()
    assert len(data) <= size, f'a/{arc:03d} grew: {len(data)} > {size}'
    open(p, 'wb').write(data + bytes(size - len(data)))

def apply(files):
    from b2files import arc_path
    bt = json.load(open(os.path.join(ROOT, 'data', 'battle_tower.json')))
    size211, size212 = os.path.getsize(arc_path(files, 211)), os.path.getsize(arc_path(files, 212))
    sets = narcio.load(files, 211)
    for i, m in enumerate(bt['sets_50']): sets[i] = set_record(m)
    for i, m in enumerate(bt['sets_100']): sets[LV100_SETS + i] = set_record(m)
    _pad_save(files, 211, sets, size211)
    trs = narcio.load(files, 212)
    for t in bt['trainers']:
        for tid, key, base in ((t['index'], 'sets_50', 0), (LV100_IDS + t['index'], 'sets_100', LV100_SETS)):
            ids = [base + k for k in t[key]]
            trs[tid + 1] = struct.pack(f'<HH{len(ids)}H', t['b2_class'], len(ids), *ids)
    _pad_save(files, 212, trs, size212)
    regs = narcio.load(files, 106)
    assert len(regs) == REG_LV50, len(regs)
    reg = bytearray(regs[REG_BASE])
    assert reg[4:6] == bytes([50, 3]), reg[:8].hex()
    reg[5] = 2                                      # level mode 2: Level 50 or less, nothing scaled (func_0201f09c)
    regs.append(bytes(reg))
    narcio.save(files, 106, regs)
    return (f'arc 211: {len(bt["sets_50"])} + {len(bt["sets_100"])} sets; arc 212: {2 * len(bt["trainers"])} trainers '
            f'(files 1-{2 * len(bt["trainers"])}); arc 106 file {REG_LV50} (Lv. 50 or less)')
