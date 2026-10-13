"""Gen 6 Exp. Share (decision 2026-10-06; notes/RESEARCH_EXPSHARE_HM.md).

The Exp. Share (item 216) becomes a key item that is switched on and off from the Bag. While FLAG_EXP_SHARE_ON
(src/include/hoenn.h) is set, every live, non-egg party Pokémon that did not take part gets half of the defeated
Pokémon's base exp (before its own level scaling, trade/Lucky Egg/Pass Power bonuses); participants get their normal
share. Messages as in Gen 6: each participant keeps its own "X gained N Exp. Points!", then ONE line "The rest of your
team gained Exp. Points thanks to the Exp. Share!", then the benched Pokémon's level-ups and moves (no line each).
Mr. Stone's gift script should do `ItemAdd ITEM_EXP_SHARE, 1, <var>` and `FlagSet FLAG_EXP_SHARE_ON` (Gen 6 gives it
switched on).

Code (every site checked against the decomp's build bytes before writing; addresses are RAM addresses):
 1. ov167 AddExpAndEVs (0x021aee0c): the held-Exp.-Share block 0x021aee70-0x021aeef8 (136 bytes, dead once the item
    can't be held) becomes "if FLAG_EXP_SHARE_ON: every party slot that CanPokemonBattle gets base >> 1" (the flag is
    read with SaveControl_GetInstance -> getConstDataBlock = the EventWork save block 0x2d, the pointer
    GameData_GetEventWork returns -> EventWork_FlagGet), followed by ExpReport (below).
 2. ov167 0x021aef8a-0x021aef91, the participant loop: it stores its share instead of adding it (participants get
    exactly their normal amount) and marks the entry as a participant in the entry's unused last byte (+11, unk0B;
    AddEVs writes +5..+10 only).
 3. ov167 func_ov167_021a8e68 (exp messages + level-ups): takes a phase in r3 (prologue stores it in its now unused
    msg slot [sp+28]); 0x021a8e88-0x021a8ece is rewritten: an entry is handled only in its phase (participants in
    phase 0, benched in phase 1), and only phase 0 queues the "gained N Exp. Points" message.
 4. ov167 func_ov167_021a8dec 0x021a8e58: `bl func_ov167_021a8e68` -> `bl ExpReport`: phase 0; if any benched entry
    has exp, the std message TEAM_MSG (Black 2's own command 0x5a, as for 0x2a "gained N Exp. Points") then phase 1.
 5. arm9 ITEM_CATEGORIES[216] (0x0208f5a8): 0 (Items) -> 4 (Key Items): the save pocket.
 6. arm9 0x02005050-0x0200507f: ExpShareToggle (flips the flag bit through EventWork_GetFlagBytePtr, then shows a bag
    message through func_ov142_0219a2c4, the bag's own "message about the item" routine, and stays in the bag). The
    bytes are Nitro SDK middleware version strings that no code references (no relocation in any module's relocs.txt
    points into 0x02005000-0x02005123); hm_free.py uses 0x02005080-0x02005123.
 7. ov142 key-item "Use" table (0x021a0980, 11 x {u16 first item, u16 count, handler}): the two Xtransceiver entries
    (621 and 626, same handler) become one {621, 6} (622-625 have no Use option); the freed entry is {216, 1,
    ExpShareToggle}.
Data:
 8. a/0/2/4 entry 216 (item data): price 0, +8 flags |= 0x20 (no Give/Toss, like key items) and field pocket 4,
    +0xA field-use 25 (any non-zero shows "Use"; only the bag's menu builder reads it; 25 = Dowsing MCHN's).
 9. Text lives in src/text (installed by the `text` patch; this patch installs the same files itself, so patch order
    does not matter): system/0006_btl_main.txt (bag) + 2 lines, system/0017.txt and 0019.txt (battle std messages,
    one id in both) + the team line.

Test switch (test builds only): HOENN_TEST_EXPSHARE=1 replaces Littleroot's script file (a/0/5/6 entry 778) with a
setup script: on entering Littleroot with an empty party it gives Treecko Lv5 + Torchic Lv5 + Mudkip Lv1 (levels up from one
share) and the Exp. Share, switched on. List the patch after `scripts`.
"""
import os, re, struct, sys, subprocess, tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
DECOMP = os.path.join(ROOT, 'external', 'pokebw2')
LLVM = '/opt/homebrew/opt/llvm/bin'
ITEM = 216                                    # ITEM_EXP_SHARE (external/pokebw2/include/constants/items.h:205)

def flag_id():
    m = re.search(r'#define\s+FLAG_EXP_SHARE_ON\s+(\d+)', open(os.path.join(ROOT, 'src', 'include', 'hoenn.h')).read())
    assert m, 'FLAG_EXP_SHARE_ON missing from src/include/hoenn.h'
    return int(m.group(1))

# ---- Thumb (ARMv5TE) encoder: only the forms used here (hm_free.py uses it too) -------------------------------------
class Thumb:
    COND = {'eq': 0, 'ne': 1, 'cs': 2, 'hs': 2, 'cc': 3, 'lo': 3, 'mi': 4, 'pl': 5, 'hi': 8, 'ls': 9, 'ge': 10,
            'lt': 11, 'gt': 12, 'le': 13}
    def __init__(self, base):
        self.base, self.out, self.labels, self.fix = base, bytearray(), {}, []
    @property
    def pc(self): return self.base + len(self.out)
    def h(self, v): self.out += struct.pack('<H', v)
    def label(self, name): self.labels[name] = self.pc
    def at(self, name, addr): self.labels[name] = addr          # a label outside this block
    def bl(self, target):
        off = target - (self.pc + 4)
        assert -(1 << 22) <= off < (1 << 22) and not off & 1, hex(off)
        self.h(0xF000 | (off >> 12) & 0x7FF); self.h(0xF800 | (off >> 1) & 0x7FF)
    def bl_label(self, name): self.fix.append((len(self.out), 'bl', name, None)); self.h(0); self.h(0)
    def push(self, regs, lr=True): self.h(0xB400 | lr << 8 | sum(1 << r for r in regs))
    def pop(self, regs, pc=True): self.h(0xBC00 | pc << 8 | sum(1 << r for r in regs))
    def movs(self, rd, imm): assert 0 <= imm < 256; self.h(0x2000 | rd << 8 | imm)
    def mov(self, rd, rm): self.h(0x1C00 | rm << 3 | rd)                 # adds rd, rm, #0 (sets flags)
    def adds(self, rd, rn, imm3): self.h(0x1C00 | imm3 << 6 | rn << 3 | rd)
    def addsr(self, rd, rn, rm): self.h(0x1800 | rm << 6 | rn << 3 | rd)
    def addi(self, rd, imm): assert 0 <= imm < 256; self.h(0x3000 | rd << 8 | imm)
    def subi(self, rd, imm): assert 0 <= imm < 256; self.h(0x3800 | rd << 8 | imm)
    def cmp(self, rn, imm): assert 0 <= imm < 256; self.h(0x2800 | rn << 8 | imm)
    def cmpr(self, rn, rm): self.h(0x4280 | rm << 3 | rn)
    def lsls(self, rd, rm, imm): self.h(0x0000 | imm << 6 | rm << 3 | rd)
    def lsrs(self, rd, rm, imm): self.h(0x0800 | imm << 6 | rm << 3 | rd)
    def lsrsr(self, rd, rs): self.h(0x40C0 | rs << 3 | rd)              # rd >>= rs
    def ands(self, rd, rm): self.h(0x4000 | rm << 3 | rd)
    def eors(self, rd, rm): self.h(0x4040 | rm << 3 | rd)
    def orrs(self, rd, rm): self.h(0x4300 | rm << 3 | rd)
    def tst(self, rn, rm): self.h(0x4200 | rm << 3 | rn)
    def sbcs(self, rd, rm): self.h(0x4180 | rm << 3 | rd)
    def muls(self, rd, rm): self.h(0x4340 | rm << 3 | rd)               # rd = rm * rd
    def str_rr(self, rd, rn, rm): self.h(0x5000 | rm << 6 | rn << 3 | rd)
    def ldrb_rr(self, rd, rn, rm): self.h(0x5C00 | rm << 6 | rn << 3 | rd)
    def ldr_sp(self, rd, off): assert off % 4 == 0 and off < 1024; self.h(0x9800 | rd << 8 | off >> 2)
    def str_sp(self, rd, off): assert off % 4 == 0 and off < 1024; self.h(0x9000 | rd << 8 | off >> 2)
    def ldr_off(self, rd, rn, off): assert off % 4 == 0 and off < 128; self.h(0x6800 | off >> 2 << 6 | rn << 3 | rd)
    def ldrh_off(self, rd, rn, off): assert off % 2 == 0 and off < 64; self.h(0x8800 | off >> 1 << 6 | rn << 3 | rd)
    def ldrb_off(self, rd, rn, off): assert off < 32; self.h(0x7800 | off << 6 | rn << 3 | rd)
    def strb_off(self, rd, rn, off): assert off < 32; self.h(0x7000 | off << 6 | rn << 3 | rd)
    def nop(self): self.h(0x46C0)                                      # mov r8, r8
    def b(self, name): self.fix.append((len(self.out), 'b', name, None)); self.h(0)
    def bcc(self, cond, name): self.fix.append((len(self.out), 'bcc', name, self.COND[cond])); self.h(0)
    def beq(self, name): self.bcc('eq', name)
    def bne(self, name): self.bcc('ne', name)
    def blo(self, name): self.bcc('lo', name)
    def ldr_lit(self, rd, name): self.fix.append((len(self.out), 'lit', name, rd)); self.h(0)
    def word(self, name, value):
        while self.pc & 3: self.nop()
        self.label(name); self.out += struct.pack('<I', value)
    def pad_to(self, addr):
        assert self.pc <= addr, (hex(self.pc), hex(addr))
        while self.pc < addr: self.nop()
    def assemble(self):
        for at, kind, name, arg in self.fix:
            pc, tgt = self.base + at, self.labels[name]
            if kind == 'bl':
                off = tgt - (pc + 4); assert -(1 << 22) <= off < (1 << 22)
                struct.pack_into('<HH', self.out, at, 0xF000 | (off >> 12) & 0x7FF, 0xF800 | (off >> 1) & 0x7FF)
                continue
            if kind == 'lit':
                off = tgt - ((pc + 4) & ~3); assert 0 <= off < 1024 and off % 4 == 0, (name, off)
                v = 0x4800 | arg << 8 | off >> 2
            else:
                off = tgt - (pc + 4); assert not off & 1
                if kind == 'b': assert -2048 <= off < 2048; v = 0xE000 | (off >> 1) & 0x7FF
                else: assert -256 <= off < 256, (name, off); v = 0xD000 | arg << 8 | (off >> 1) & 0xFF
            struct.pack_into('<H', self.out, at, v)
        return bytes(self.out)

# ---- addresses (decomp symbols: config/b2_us/arm9/symbols.txt, overlays/ov142, ov167) -------------------------------
ARM9_BASE, OV142_BASE, OV167_BASE = 0x02004000, 0x021998C0, 0x021998C0   # extract/b2_us/arm9_overlays/overlays.yaml
SaveControl_GetInstance = 0x020072FC
getConstDataBlock = 0x02017A5C          # SaveControl_GetBlockPtr(save, 0x2d): the EventWork block
EventWork_FlagGet, EventWork_GetFlagBytePtr = 0x020191AC, 0x0201924C
ITEM_CATEGORIES = 0x0208F4D0
# ov167
GetBattleMonFromParty, CanPokemonBattle = 0x0219D4F4, 0x021BB37C
PartyMon, GetBattleMonStat, GetMonID = 0x0219D4E4, 0x021BB1B4, 0x021BAC40     # func_ov167_0219d4e4 = party slot i
QueueStdMsg = 0x021B15D0                # func_ov167_021b15d0(queue, 0x5a, msg, args..., 0xffff0000)
ExpMessages = 0x021A8E68                # func_ov167_021a8e68(flow, party, entries): messages + level-ups
ExpMessages_Call = 0x021A8E58           # its only call, in func_ov167_021a8dec
NEXT_ENTRY = 0x021A8F1A                 # func_ov167_021a8e68's "i++" (skip this entry)
TERMINATOR_LIT = 0x021A8F2C             # func_ov167_021a8e68's literal 0xffff0000
BLOCK = (0x021AEE70, 0x021AEEF8)        # AddExpAndEVs' held-item block
# ov142
BagItemMessage = 0x0219A2C4             # func_ov142_0219a2c4(work, msgId): message with word 0 = player name,
                                        # word 1 = the selected item, then back to the bag
KEY_ITEM_USE_TABLE = 0x021A0980         # 11 x 8 bytes, searched by func_ov142_0219a4a0
SDK_STRINGS = (0x02005050, 0x02005080)  # arm9 (see the docstring; hm_free.py has 0x02005080-0x02005123)

def ov167_block(flag, team_msg):
    """AddExpAndEVs 0x021aee70-0x021aeef8: the share, then ExpReport. At 0x021aee70 the live registers are r5 = entries
    (12 bytes each: u32 exp, u8 boosted, u8 evs[6], u8 unk0B); stack: [sp+4] party, [sp+36] party count (>= 1),
    [sp+40] base exp (after the trainer x1.5). r4, r6, r7 are free (the code at 0x021aeef8 sets them again)."""
    t = Thumb(BLOCK[0])
    t.at('vanilla_next', BLOCK[1]); t.at('ExpMessages', ExpMessages)
    t.bl(SaveControl_GetInstance)
    t.bl(getConstDataBlock)
    t.ldr_lit(1, 'flag')
    t.bl(EventWork_FlagGet)
    t.cmp(0, 0); t.beq('done')
    t.ldr_sp(7, 40); t.lsrs(7, 7, 1)             # share = base >> 1 (base >= 7: BaseExp >= 36, level >= 1)
    t.movs(4, 0)
    t.label('loop')
    t.ldr_sp(0, 4); t.mov(1, 4)
    t.bl(GetBattleMonFromParty)
    t.bl(CanPokemonBattle)                       # not fainted and not an egg
    t.cmp(0, 0); t.beq('next')
    t.movs(0, 12); t.muls(0, 4); t.str_rr(7, 5, 0)   # entries[i].exp = share (participants are overwritten later)
    t.label('next')
    t.adds(4, 4, 1); t.ldr_sp(0, 36); t.cmpr(4, 0); t.blo('loop')
    t.label('done')
    t.b('vanilla_next')
    # BOOL ExpReport(flow, party, entries): replaces func_ov167_021a8dec's call of func_ov167_021a8e68
    t.label('ExpReport')
    t.push([4, 5, 6, 7])
    t.mov(4, 0); t.mov(5, 1); t.mov(6, 2)
    t.movs(3, 0); t.bl_label('ExpMessages')      # phase 0: participants, with their own messages
    t.mov(7, 0)
    t.mov(2, 6); t.movs(3, 6)
    t.label('scan')                              # any benched entry (unk0B == 0) with exp?
    t.ldrb_off(0, 2, 11); t.cmp(0, 0); t.bne('scan_next')
    t.ldr_off(0, 2, 0); t.cmp(0, 0); t.bne('team')
    t.label('scan_next')
    t.addi(2, 12); t.subi(3, 1); t.bne('scan')
    t.mov(0, 7); t.pop([4, 5, 6, 7])
    t.label('team')
    t.ldr_off(0, 4, 12); t.movs(1, 0x5A); t.movs(2, team_msg); t.ldr_lit(3, 'term')
    t.bl(QueueStdMsg)                            # "The rest of your team gained Exp. Points thanks to the Exp. Share!"
    t.mov(0, 4); t.mov(1, 5); t.mov(2, 6); t.movs(3, 1)
    t.bl_label('ExpMessages')                    # phase 1: benched, no own message; exp, level-ups, moves
    t.orrs(0, 7); t.pop([4, 5, 6, 7])
    t.word('flag', flag)
    t.word('term', 0xFFFF0000)
    code = t.assemble()
    assert len(code) <= BLOCK[1] - BLOCK[0], len(code)
    return code + bytes.fromhex('c046') * ((BLOCK[1] - BLOCK[0] - len(code)) // 2), t.labels['ExpReport']

def exp_messages_region():
    """func_ov167_021a8e68 0x021a8e88-0x021a8ece. Live: r5 = flow, r6 = entry, [sp+20] party, [sp+36] i, [sp+28] phase
    (stored by the patched prologue). Same work as Black 2's code, plus the phase filter, and the message only in
    phase 0; the message id is computed here (0x2a, or 0x2b when boosted) instead of in [sp+28]."""
    t = Thumb(0x021A8E88)
    t.at('next', NEXT_ENTRY); t.at('after', 0x021A8ECE); t.at('term', TERMINATOR_LIT)
    t.ldr_sp(1, 36); t.ldr_sp(0, 20); t.bl(PartyMon); t.mov(4, 0)
    t.movs(1, 15); t.bl(GetBattleMonStat)
    t.cmp(0, 100); t.bcc('ge', 'next')           # Lv100: nothing (as before)
    t.ldrb_off(2, 6, 11); t.ldr_sp(3, 28)        # participant mark, phase
    t.cmp(2, 1); t.sbcs(2, 2)                    # participant -> 0, benched -> -1
    t.addsr(2, 2, 3); t.bne('next')              # handle participants in phase 0, benched in phase 1
    t.ldr_off(7, 6, 0)                           # exp
    t.mov(0, 4); t.bl(GetMonID); t.str_sp(0, 32)
    t.ldr_sp(3, 28); t.cmp(3, 0); t.bne('after') # phase 1: no "X gained N Exp. Points!"
    t.ldrb_off(2, 6, 4); t.addi(2, 0x2A)         # 0x2a, or 0x2b "a boosted"
    t.ldr_lit(0, 'term'); t.str_sp(7, 0); t.str_sp(0, 4)
    t.ldr_off(0, 5, 12); t.ldr_sp(3, 32); t.movs(1, 0x5A)
    t.bl(QueueStdMsg)
    t.pad_to(0x021A8ECE)
    return t.assemble()

def toggle_handler(flag, msg_on, msg_off):
    """ExpShareToggle(BagWork *work), called by the bag's Use dispatch (func_ov142_0219a4d0 via the key-item table):
    flips the flag's bit, then "The Exp. Share was turned on./off." and back to the item list."""
    t = Thumb(SDK_STRINGS[0])
    t.push([4])
    t.mov(4, 0)
    t.bl(SaveControl_GetInstance)
    t.bl(getConstDataBlock)
    t.ldr_lit(1, 'flag')
    t.bl(EventWork_GetFlagBytePtr)               # EventWork + 0x35e + flag / 8
    t.ldrb_off(3, 0, 0); t.movs(2, 1 << (flag & 7)); t.eors(3, 2); t.strb_off(3, 0, 0)
    t.movs(1, msg_on); t.tst(3, 2); t.bne('show'); t.movs(1, msg_off)
    t.label('show')
    t.mov(0, 4)
    t.bl(BagItemMessage)
    t.movs(0, 0)
    t.pop([4])
    t.word('flag', flag)
    return t.assemble()

# ---- text (src/text, the same files the `text` patch installs) ------------------------------------------------------
BAG_MSG_FILE, BATTLE_MSG_FILES = 6, (17, 19)   # bag: GFL_MsgSysLoadData(0, 2, 6) in ov142 0x0219c55e; battle std
                                               # messages: file 19, or 17 in one mode (ov167 0x021d4cb4 table)
BAG_MESSAGES = ['The {0109:1} was turned on.', 'The {0109:1} was turned off.']   # {0109:1} = item name (word 1)
TEAM_MESSAGE = 'The rest of your team gained Exp. Points\\nthanks to the Exp. Share!'

def _text_tools():
    sys.path.insert(0, os.path.join(DECOMP, 'tools', 'scripts'))
    import text_data
    return text_data

def src_text(kind, num):
    """(path, message lines) of src/text/<kind>/<num>_*.txt; message ids = indexes (the \\pad line is not one)."""
    import glob, json
    found = glob.glob(os.path.join(ROOT, 'src', 'text', kind, f'{num:04d}*.txt'))
    assert len(found) == 1, (kind, num, found)
    text = open(found[0], encoding='utf-8').read().split('\n')
    over = json.load(open(os.path.join(ROOT, 'src', 'text', 'overrides.json'))).get(f'{kind}/{os.path.basename(found[0])}', {})
    for i, v in over.items(): text[int(i)] = v                  # as patches/text.py does
    return found[0], [l for l in text if l and not l.startswith('\\pad{')], '\n'.join(text)

def install_text(files, kind, num):
    """Pack src/text/<kind>/<num>_*.txt into a/0/0/2 (system) or a/0/0/3 (script) entry num, as `text` does (so the
    patch order doesn't matter; identical bytes when `text` already ran)."""
    import narcio
    arc = {'system': 2, 'script': 3}[kind]
    _, _, text = src_text(kind, num)
    data = _text_tools().pack_file(text)
    entries = narcio.load(files, arc)
    if entries[num] != data:
        entries[num] = data
        narcio.save(files, arc, entries)

def message_id(kind, num, line):
    _, lines, _ = src_text(kind, num)
    assert line in lines, (kind, num, line)
    return lines.index(line)

def _ids():
    bag = [message_id('system', BAG_MSG_FILE, m) for m in BAG_MESSAGES]
    team = {message_id('system', f, TEAM_MESSAGE) for f in BATTLE_MSG_FILES}
    assert len(team) == 1, f'the team message must have one id in system files {BATTLE_MSG_FILES}: {team}'
    return bag, team.pop()

def _item_data(files):
    import narcio
    entries = narcio.load(files, 24)
    d = bytearray(entries[ITEM])
    vanilla = bytes.fromhex('2c01330000001e001f00000000010027')
    assert bytes(d[:16]) == vanilla or d[10] == 25, d[:16].hex()          # vanilla, or already patched
    struct.pack_into('<H', d, 0, 0)                                    # price 0 (key items can't be sold)
    flags = struct.unpack_from('<H', d, 8)[0]
    flags = (flags & ~(0xF << 7)) | 0x20 | (4 << 7)                    # no Give/Toss; field pocket 4 = Key Items
    struct.pack_into('<H', d, 8, flags)
    d[10] = 25                                                         # field use: shows "Use" in the bag
    entries[ITEM] = bytes(d)
    narcio.save(files, 24, entries)

TEST_SCRIPT = r'''
#include "asm/field_script.inc"
#include "constants/species.h"
#include "constants/items.h"
#include "hoenn.h"
    ScriptEntry Script_1
    ScriptEntry Script_2
    ScriptEntry Script_3
    ScriptEntry Script_4
    ScriptEntry Script_5
    ScriptEntry Script_6
    ScriptEntry Script_7
    ScriptEntry Script_8
    ScriptEntry Script_9
    ScriptEntriesEnd
Script_1:
Script_2:
Script_3:
Script_4:
Script_5:
Script_6:
Script_7:
Script_8:
    VMHalt
Script_9:
    // TEST ONLY (HOENN_TEST_EXPSHARE): Littleroot's map-load script gives a test party if the party is empty
    PokePartyGetCount 0x8000, 0
    VMStackPush 0x8000
    VMStackPushConst 0
    VMStackCmp CMP_EQ
    VMJumpIf CMP_STACK, L_Done
    PokePartyAdd 0x8001, SPECIES_TREECKO, 0, 5
    PokePartyAdd 0x8001, SPECIES_TORCHIC, 0, 5
    PokePartyAdd 0x8001, SPECIES_MUDKIP, 0, 1
    ItemAdd ITEM_EXP_SHARE, 1, 0x8001
    FlagSet FLAG_EXP_SHARE_ON
L_Done:
    VMHalt
    .balign 4, 0
'''

def _test_party(files):
    import narcio
    with tempfile.TemporaryDirectory() as t:
        src, o, b = os.path.join(t, 'x.s'), os.path.join(t, 'x.o'), os.path.join(t, 'x.bin')
        open(src, 'w').write(TEST_SCRIPT)
        subprocess.run([f'{LLVM}/clang', '--target=armv5te-none-eabi', '-x', 'assembler-with-cpp', '-c',
                        '-I', f'{DECOMP}/include', '-I', f'{DECOMP}/lib/nitro/include',
                        '-I', os.path.join(ROOT, 'src', 'include'), '-D', 'BLACK2', '-o', o, src], check=True, cwd=DECOMP)
        subprocess.run([f'{LLVM}/llvm-objcopy', '-O', 'binary', o, b], check=True)
        entries = narcio.load(files, 56)
        entries[778] = open(b, 'rb').read()
        narcio.save(files, 56, entries)

def apply(files):
    _item_data(files)
    for num in (BAG_MSG_FILE, *BATTLE_MSG_FILES):
        install_text(files, 'system', num)
    bag, team = _ids()
    done = f'item {ITEM} -> key item; text from src/text: bag messages {bag}, team message {team}'
    if os.environ.get('HOENN_TEST_EXPSHARE'):
        _test_party(files); done += ', TEST party script in Littleroot (778)'
    return done

# ---- code ------------------------------------------------------------------------------------------------------------
def _patch(data, base, addr, old, new, what):
    at = addr - base
    cur = bytes(data[at:at + len(new)])
    assert cur == new or (old is not None and cur == old), f'{what}: unexpected bytes {cur.hex()}'
    data[at:at + len(new)] = new

def _vanilla(name, base, addr, n):
    """The decomp's (= the dump's) bytes at addr in code file `name`."""
    return open(os.path.join(DECOMP, 'build', 'b2_us', 'build', name), 'rb').read()[addr - base:addr - base + n]

def _load(code, name):
    path = os.path.join(code, name)
    return path, bytearray(open(path, 'rb').read())

def _save(path, data):
    if os.path.islink(path): os.unlink(path)
    open(path + '.tmp', 'wb').write(data); os.replace(path + '.tmp', path)

def _bl(src, dst):
    off = dst - (src + 4)
    return struct.pack('<HH', 0xF000 | (off >> 12) & 0x7FF, 0xF800 | (off >> 1) & 0x7FF)

def apply_code(code):
    flag = flag_id()
    (msg_on, msg_off), team = _ids()

    # 1.-4. ov167
    path, d = _load(code, 'arm9_ov167.bin')
    ov = 'arm9_ov167.bin'
    block, exp_report = ov167_block(flag, team)
    old = _vanilla(ov, OV167_BASE, BLOCK[0], BLOCK[1] - BLOCK[0])
    assert old.count(bytes.fromhex('d828')) == 2, 'AddExpAndEVs held-item block not found (two "cmp r0, #0xd8")'
    _patch(d, OV167_BASE, BLOCK[0], old, block, 'AddExpAndEVs block + ExpReport')
    # participant loop: `ldr r1,[r5,r6]; ldr r0,[sp,#32]; adds r0,r1,r0; str r0,[r5,r6]`
    #             ->   `adds r1,r5,r6; ldr r0,[sp,#32]; strb r7,[r1,#11]; str r0,[r5,r6]`  (r7 = list length >= 1)
    _patch(d, OV167_BASE, 0x021AEF8A, bytes.fromhex('a959' '0898' '0818' 'a851'),
           bytes.fromhex('a919' '0898' 'cf72' 'a851'), 'participant loop')
    # func_ov167_021a8e68 prologue: `movs r0,#0` -> `str r3,[sp,#28]` (phase); `str r0,[sp,#36]` -> `str r7,[sp,#36]`
    _patch(d, OV167_BASE, 0x021A8E6E, bytes.fromhex('0020'), bytes.fromhex('0793'), 'exp messages: phase')
    _patch(d, OV167_BASE, 0x021A8E76, bytes.fromhex('0990'), bytes.fromhex('0997'), 'exp messages: i = 0')
    region = exp_messages_region()
    _patch(d, OV167_BASE, 0x021A8E88, _vanilla(ov, OV167_BASE, 0x021A8E88, len(region)), region, 'exp messages body')
    _patch(d, OV167_BASE, ExpMessages_Call, _bl(ExpMessages_Call, ExpMessages), _bl(ExpMessages_Call, exp_report),
           'call ExpReport')
    _save(path, d)

    # 5.-6. arm9: pocket of the Exp. Share, bag toggle handler in the SDK strings
    path, d = _load(code, 'arm9.bin')
    _patch(d, ARM9_BASE, ITEM_CATEGORIES + ITEM, b'\x00', b'\x04', 'ITEM_CATEGORIES[216]')
    handler = toggle_handler(flag, msg_on, msg_off)
    lo, hi = SDK_STRINGS
    assert len(handler) <= hi - lo, len(handler)
    old = _vanilla('arm9.bin', ARM9_BASE, lo, hi - lo)
    assert old.startswith(b'[SDK+NINTENDO:DWC'), old[:24]
    _patch(d, ARM9_BASE, lo, old, handler + bytes(hi - lo - len(handler)), 'SDK strings -> ExpShareToggle')
    _save(path, d)

    # 7. ov142 key-item Use table
    path, d = _load(code, 'arm9_ov142.bin')
    xtr = struct.pack('<HHI', 621, 1, 0x0219A481)
    _patch(d, OV142_BASE, KEY_ITEM_USE_TABLE + 8 * 8, xtr, struct.pack('<HHI', 621, 6, 0x0219A481), 'Xtransceiver 621')
    _patch(d, OV142_BASE, KEY_ITEM_USE_TABLE + 9 * 8, struct.pack('<HHI', 626, 1, 0x0219A481),
           struct.pack('<HHI', ITEM, 1, lo | 1), 'Xtransceiver 626 -> Exp. Share')
    _save(path, d)
    return (f'flag {flag}; AddExpAndEVs block with ExpReport at {exp_report:#x}; participant mark; exp messages by '
            f'phase (team message {team}); ITEM_CATEGORIES[216]=4; ExpShareToggle at {lo:#x} ({len(handler)} B, '
            f'messages {msg_on}/{msg_off}); ov142 Use table entry 9')
