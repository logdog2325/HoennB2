"""Sapphire's trainers (converter/gen_trainers.py; notes/STORY_PORTING.md "Trainers").

apply(files):
  - src/trainers/NNNN_*.s (the decomp's trainer.inc macros, assembled with clang as the decomp's build does:
    `.trainer` section -> a/0/9/1 entry NNNN, `.party` -> a/0/9/2 entry NNNN)
  - a/0/8/9 file 0 + a/0/9/0 file 0 (trainer message table) from data/hoenn_trainer_msgs.json, which lists the
    (trainer, type) of each line of src/text/system/0381_trainer_msg_load.txt (packed by the text patch)
  - sizes: a/0/8/9, a/0/9/0 and a/0/9/1 keep Black 2's exact size (padded inside the NARC like build_rom.py's RESERVE
    padding), so the ROM's file table does not move. a/0/9/2 (parties) grows by ~7.9 KB because every Sapphire
    movesets is written out: the lead adds RESERVE[92] (and RESERVE[89] for later message growth) to build_rom.py and
    rebuilds the savestates; until then HOENN_TRAINERS_FIT=1 (test builds) gives default-move parties Black 2's own
    level-up moves until a/0/9/2 fits (HOENN_TRAINERS_FIT_KEEP=TRAINER_A,B keeps those exact)
  - the trainer NPCs of data/hoenn_trainer_npcs.json (converter/gen_trainer_npcs.py), appended to their zones
  - test switch HOENN_TEST_TRAINER=TRAINER_X[,x,z][+TRAINER_Y...] (env): eye-contact NPCs of those trainers in
    Littleroot (zone 389), from (176,358) facing down, 2 tiles apart
apply_code(code):
  - arm9 TRAINER_CLASS_RESOURCES (0x02092394: u8 front sprite, u8 sex, u16 eye-contact BGM per class) for the classes
    data/hoenn_trainer_classes.json "edits" lists; the special classes' battle music group (arm9 SPECIAL_TRAINER_CLASSES),
    encounter effect and group music (ov036 SPECIAL_TRAINER_ENCEFF / SPECIAL_TRAINER_BGM): "special", "special_bgm". arm9 grows by a few bytes at most when dsd recompresses it; the
    ROM layout keeps its slack (checked: start offsets of every file unchanged).
  - arm9 TrainerUtil_LoadTrainer: class 145 (Wally, on Hugh's class) takes its name from text 382, not from the
    save's rival name (RIVAL_NAME_CLASS)
  - ov167 func_ov167_021d0288 (prints a trainer's in-battle line): formats it with the player's name in word 0, so
    Sapphire's {PLAYER} shows in battle as in the field (battle_trainer_msg below)
Run after `hoenn_world` and `interiors`, with `text` (names, class names and messages: src/text/system/0381-0383, 0485).
apply_code also changes overlay 36 (encounter effects), whose compressed size changes: savestates made on a ROM
without this patch read a stale file table (end of file 36), so test from states made on a ROM with it.
"""
import os, sys, glob, json, struct, subprocess, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import narcio, version  # noqa: E402   (Ruby: src/trainers/ruby/, data/ruby/<name>.json merged over data/<name>.json)

ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
DECOMP = os.path.join(ROOT, 'external', 'pokebw2')
SRC_FILES = os.path.join(DECOMP, 'build', 'b2_us', 'files')
LLVM = '/opt/homebrew/opt/llvm/bin'
ARM9_BASE = 0x02004000
CLASS_RESOURCES = 0x02092394
ARCS = (89, 90, 91, 92)

def assemble_trainer(src):
    """(trdata bytes, party bytes) of one trainer source."""
    with tempfile.TemporaryDirectory() as t:
        o = os.path.join(t, 'x.o')
        subprocess.run([f'{LLVM}/clang', '--target=armv5te-none-eabi', '-x', 'assembler-with-cpp', '-c',
                        '-I', f'{DECOMP}/include', '-I', f'{DECOMP}/lib/nitro/include', '-D', 'BLACK2',
                        '-o', o, os.path.abspath(src)], check=True, cwd=DECOMP)
        undef = subprocess.run([f'{LLVM}/llvm-nm', '--undefined-only', o], capture_output=True, text=True,
                               check=True).stdout.split()
        undef = [w for w in undef if w != 'U']
        if undef: raise SystemExit(f'{src}: undefined names {undef}')
        out = []
        for sec in ('.trainer', '.party'):
            b = os.path.join(t, sec[1:] + '.bin')
            subprocess.run([f'{LLVM}/llvm-objcopy', '-O', 'binary', '-j', sec, o, b], check=True)
            out.append(open(b, 'rb').read())
        return out

def reserved():
    """build_rom.py's RESERVE: archives it pads to a fixed size itself."""
    import importlib.util
    spec = importlib.util.spec_from_file_location('build_rom', os.path.join(os.path.dirname(HERE), 'build_rom.py'))
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod.RESERVE

def keep_size(files, arc):
    """Pad archive arc to Black 2's own size (grow the NARC's GMIF, as build_rom.pad_archives does), unless
    build_rom.py has a RESERVE for it (then build_rom pads it)."""
    from b2files import arc_path
    if arc in reserved(): return 'RESERVE'
    orig = os.path.getsize(arc_path(SRC_FILES, arc))
    path = arc_path(files, arc)
    data = bytearray(open(path, 'rb').read())
    if len(data) > orig:
        raise SystemExit(f'trainers: a/{arc:03d} is {len(data)} bytes, more than Black 2\'s {orig}: the lead must add '
                         f'RESERVE[{arc}] to build_rom.py and rebuild the savestates (make_states.py)')
    if len(data) == orig: return 0
    off = struct.unpack_from('<H', data, 0xC)[0]
    for _ in range(2): off += struct.unpack_from('<I', data, off + 4)[0]    # BTAF, BTNF
    assert data[off:off + 4] == b'GMIF'
    extra = orig - len(data)
    struct.pack_into('<I', data, off + 4, struct.unpack_from('<I', data, off + 4)[0] + extra)
    struct.pack_into('<I', data, 8, orig)
    data += bytes(extra)
    if os.path.islink(path): os.unlink(path)
    open(path + '.tmp', 'wb').write(data); os.replace(path + '.tmp', path)
    return extra

def fit_parties(tr, party):
    """Test builds only (HOENN_TRAINERS_FIT=1, until build_rom.py has RESERVE[92]): make a/0/9/2 fit Black 2's size by
    giving trainers whose Sapphire party used default moves Black 2's own level-up moves instead (party kind bit 0
    cleared, the 8 move bytes of each Pokémon dropped), highest id first; HOENN_TRAINERS_FIT_KEEP=TRAINER_A,B keeps
    those exact."""
    from narc import write_narc
    from b2files import arc_path
    limit = os.path.getsize(arc_path(SRC_FILES, 92))
    data = version.load_json(os.path.join(ROOT, 'data', 'hoenn_trainer_data.json'))['trainers']
    keep = set(filter(None, os.environ.get('HOENN_TRAINERS_FIT_KEEP', '').split(',')))
    cands = sorted((d['b2_id'], t) for t, d in data.items() if d.get('sapphire_default_moves') and t not in keep)
    n = 0
    while len(write_narc(party)) > limit and cands:
        bid, t = cands.pop()
        kind, count = tr[bid][0], tr[bid][3]
        if not kind & 1: continue
        size = 8 + (2 if kind & 2 else 0) + 8
        p = party[bid]
        party[bid] = b''.join(p[i * size:i * size + size - 8] for i in range(count))
        tr[bid] = bytes([kind & ~1]) + tr[bid][1:]
        n += 1
    return f'; TEST FIT: {n} default-move parties use Black 2\'s level-up moves'

def apply(files):
    srcs = version.overlay(os.path.join(ROOT, 'src', 'trainers'), '*.s')
    if not srcs: return 'no trainers (run converter/gen_trainers.py)'
    tr, party = narcio.load(files, 91), narcio.load(files, 92)
    for s in srcs:
        n = int(os.path.basename(s)[:4])
        tr[n], party[n] = assemble_trainer(s)
        assert len(tr[n]) == 20, (s, len(tr[n]))
    fit = fit_parties(tr, party) if os.environ.get('HOENN_TRAINERS_FIT') and 92 not in reserved() else ''
    narcio.save(files, 91, tr); narcio.save(files, 92, party)
    recs = version.load_json(os.path.join(ROOT, 'data', 'hoenn_trainer_msgs.json'))['records']
    table = b''.join(struct.pack('<HH', t, ty) for t, ty in recs)
    first = {}
    for i, (t, _) in enumerate(recs): first.setdefault(t, 4 * i)
    n_tr = len(narcio.load(SRC_FILES, 90)[0]) // 2
    offs = b''.join(struct.pack('<H', first.get(t, len(table))) for t in range(n_tr))   # no messages: end of table
    m89, m90 = narcio.load(files, 89), narcio.load(files, 90)
    m89[0], m90[0] = table, offs
    narcio.save(files, 89, m89); narcio.save(files, 90, m90)
    pads = {a: keep_size(files, a) for a in ARCS}
    done = f'{len(srcs)} trainers, {len(recs)} message records; padding kept Black 2 sizes {pads}{fit}'
    done += '; ' + place_npcs(files)
    test = os.environ.get('HOENN_TEST_TRAINER')
    if test: done += '; ' + test_trainer(files, test)
    return done

def place_npcs(files):
    """The trainer NPCs of data/hoenn_trainer_npcs.json (converter/gen_trainer_npcs.py), appended to their zones' NPC
    lists (outdoor: zone tiles; rooms: Sapphire tile + the built room's origin, as interiors.py places people)."""
    import zoneheaders
    from zones import parse_entities, build_entities
    path = os.path.join(ROOT, 'data', 'hoenn_trainer_npcs.json')
    if not os.path.exists(path): return 'no trainer NPCs (run converter/gen_trainer_npcs.py)'
    cfg = version.load_json(path)
    rooms_dir = os.environ.get('HOENN_INTERIORS_DIR') or os.path.join(ROOT, 'work', 'interiors')
    headers, _ = zoneheaders.load(files)
    ents = narcio.load(files, 126)
    by_zone = {}
    for n in cfg['outdoor']: by_zone.setdefault(n['zone'], []).append((n['x'], n['z'], n))
    skipped = []
    for n in cfg['rooms']:
        if not version.room_in_version(n['room']): continue    # the other version's room (data/versions.json)
        rj = os.path.join(rooms_dir, n['room'], 'room.json')
        if not os.path.exists(rj): skipped.append(n['room']); continue
        ox, oz = json.load(open(rj))['origin']
        by_zone.setdefault(n['zone'], []).append((n['at'][0] + ox, n['at'][1] + oz, n))
    keys = ('uid', 'model', 'move', 'evtype', 'flag', 'script', 'dir', 'p0', 'p1', 'p2')
    for zone, items in sorted(by_zone.items()):
        e, _ = parse_entities(ents[headers[zone]['entities']])
        uids = {x['uid'] for x in e['npcs']}
        tmpl = dict(e['npcs'][0]) if e['npcs'] else dict(rail=0, y=0)
        for x, z, n in items:
            npc = dict(tmpl, **{k: n[k] for k in keys}, areaw=n.get('areaw', 0), areah=n.get('areah', 0), rail=0, x=x, z=z,
                       y=0)                                     # (walkers: Sapphire's range, converter/gen_trainer_npcs.py)
            while npc['uid'] in uids: npc['uid'] += 1
            uids.add(npc['uid'])
            e['npcs'].append(npc)
        ents[headers[zone]['entities']] = build_entities(e, ents[headers[zone]['entities']])
    narcio.save(files, 126, ents)
    n = sum(len(v) for v in by_zone.values())
    return f'{n} trainer NPCs in {len(by_zone)} zones' + (f' (rooms not built here: {sorted(set(skipped))})' if skipped else '')

def test_trainer(files, spec):
    """Test only: eye-contact NPCs of Hoenn trainers in Littleroot. spec = TRAINER_A[,x,z][+TRAINER_B[,x,z]...]; without
    a position the first stands at (176,358) facing down and each next one 2 tiles further east."""
    import zoneheaders
    from zones import parse_entities, build_entities
    data = version.load_json(os.path.join(ROOT, 'data', 'hoenn_trainer_data.json'))['trainers']
    sprites = version.load_json(os.path.join(ROOT, 'data', 'sprite_map.json'))
    headers, _ = zoneheaders.load(files)
    ents = narcio.load(files, 126)
    e, _ = parse_entities(ents[headers[389]['entities']])
    tmpl = dict(e['npcs'][0])
    done = []
    for k, part in enumerate(spec.split('+')):
        name, *pos = part.split(',')
        x, z = (int(pos[0]), int(pos[1])) if pos else (176 + 2 * k, 358)
        d = data[name]
        o = d['objects'][0] if d['objects'] else {'gfx': 'OBJ_EVENT_GFX_YOUNGSTER', 'sight': 3}
        model = (sprites.get(o['gfx']) or {}).get('code') or 2
        e['npcs'].append(dict(tmpl, uid=200 + k, model=model, move=15, evtype=1, flag=0, script=3000 + d['b2_id'],
                              dir=1, p0=max(1, o['sight']), p1=0, p2=0, areaw=0, areah=0, rail=0, x=x, z=z, y=tmpl['y']))
        done.append(f'{name} (id {d["b2_id"]}, model {model}) at ({x},{z})')
    ents[headers[389]['entities']] = build_entities(e, ents[headers[389]['entities']])
    narcio.save(files, 126, ents)
    return 'TEST trainers in Littleroot: ' + ', '.join(done)

SPECIAL_CLASSES = 0x020922bc           # arm9: 29 x {u8 class, u8 BGM group, u8 pedestal}
RIVAL_NAME_CLASS = 0x02030856          # arm9 TrainerUtil_LoadTrainer: cmp r1, #0x91 (the rival's class: name from the save)
OV036_BASE, SPECIAL_BGM, SPECIAL_ENCEFF = 0x0217f600, 0x021d28e4, 0x021d2900   # ov036: u16 SEQ per group, u8 per entry

def _write(path, data):
    if os.path.islink(path): os.unlink(path)
    open(path, 'wb').write(data)

def apply_code(code):
    cfg = version.load_json(os.path.join(ROOT, 'data', 'hoenn_trainer_classes.json'))
    edits = cfg['edits']
    path = os.path.join(code, 'arm9.bin')
    data = bytearray(open(path, 'rb').read())
    n = 0
    for c, e in edits.items():
        o = CLASS_RESOURCES - ARM9_BASE + 4 * int(c)
        if 'sprite' in e: data[o] = e['sprite']; n += 1
        if 'sex' in e: data[o + 1] = e['sex']; n += 1
        if 'eye_bgm' in e: struct.pack_into('<H', data, o + 2, e['eye_bgm']); n += 1
    special = cfg.get('special', {})
    for c, e in special.items():                 # battle music group of the class's special entry
        o = SPECIAL_CLASSES - ARM9_BASE + 3 * e['entry']
        assert data[o] == int(c), (c, e, data[o])
        if 'bgm_group' in e: data[o + 1] = e['bgm_group']
    # Wally's class 145 (Hugh's, kept for its sprite slot and music group): Black 2 names a trainer of class 0x91 after
    # the rival-name field of the save (TrainerUtil_LoadTrainer: `cmp r1, #0x91` -> getPtrToRivalName), which this port
    # never fills, so Wally showed as "PKMN Trainer ???????" (ch3b). The compare now tests 0xFF (Black 2's 237 classes
    # end at 236): every class 145 trainer takes its name from text 382 ("Wally"), as Sapphire's PKMN TRAINER WALLY.
    # The other readers of the rival name (the script word set, ov036/ov057/ov135/ov259) are left as they are.
    o = RIVAL_NAME_CLASS - ARM9_BASE
    assert data[o:o + 2] in (bytes.fromhex('9129'), bytes.fromhex('ff29')), data[o:o + 2].hex()
    data[o] = 0xFF
    _write(path, data)
    path = os.path.join(code, 'arm9_ov036.bin')          # encounter effects and the groups' battle music
    ov = bytearray(open(path, 'rb').read())
    for c, e in special.items():
        ov[SPECIAL_ENCEFF - OV036_BASE + e['entry']] = e['enceff']
    for g, seq in cfg.get('special_bgm', {}).items():
        struct.pack_into('<H', ov, SPECIAL_BGM - OV036_BASE + 2 * int(g), seq)
    _write(path, ov)
    path = os.path.join(code, 'arm9_ov167.bin')          # battle trainer lines get the player's name
    ov = bytearray(open(path, 'rb').read())
    o, blob = BTL_TRAINER_MSG - OV167_BASE, battle_trainer_msg()
    vanilla = open(os.path.join(DECOMP, 'build', 'b2_us', 'build', 'arm9_ov167.bin'), 'rb').read()
    assert ov[o:o + len(blob)] in (vanilla[o:o + len(blob)], blob), 'ov167 0x021d0288 is not Black 2\'s'
    ov[o:o + len(blob)] = blob
    _write(path, ov)
    return (f'trainer classes: {n} values in TRAINER_CLASS_RESOURCES ({len(edits)} classes); {len(special)} special '
            f'classes: encounter effect / music group; class 145 named from text 382 (Wally); group music {cfg.get("special_bgm")}; battle trainer lines '
            f'formatted with the player\'s name (ov167 {BTL_TRAINER_MSG:#x}, {len(blob)} B)')

# ---- battle trainer lines: the player's name -------------------------------------------------------------------------
# Black 2 prints a trainer's in-battle line (defeat line, mid-battle lines) with func_ov167_021d0288 (btlv_core.c):
# TrainerMsg_Load straight into core->strbuf, never through the battle word set, so Sapphire's {PLAYER} ({0100:0})
# printed nothing ("I lost to …?"). The rewrite (same 68 bytes; its three callers ignore the result) loads the line into
# the battle string module's work buffer, puts the player's name in word 0 the way the battle's own "{trainer}" words
# do (func_ov167_021d4e4c with the player's client 0 = copyVarForText(wordSet, 0, its PlayerInfo)), formats it into
# core->strbuf and prints it (func_ov167_021d01d8 = print core->strbuf, wait 0x50). A missing line leaves the buffer
# empty (TrainerMsg_Load clears it), and nothing is printed, as before (TrainerMsg_CheckExists's other case, Battle
# Institute ids >= 0x500, is only line 1 or 8, which TrainerMsg_Load reads from files 0x32/0x33 as before).
OV167_BASE = 0x021998c0
BTL_TRAINER_MSG, BTL_TRAINER_MSG_END = 0x021d0288, 0x021d02cc
TrainerMsg_Load, GFL_WordSetFormatStrbuf = 0x020305d8, 0x02024920
BtlStr_SetTrainerName, Btlv_PrintStrbuf = 0x021d4e4c, 0x021d01d8   # func_ov167_021d4e4c(wordSet, idx, client)
BTL_STR = 0x021dd87c                   # ov167 bss: +0 main module, +8 word set, +0xc work StrBuf (func_ov167_021d4f64)
CORE_STRBUF, CORE_HEAPID = 0xac, 0x1c8 # BtlvCore offsets, as the vanilla function reads them
PLAYER_CLIENT = 0                      # the player's client (func_ov167_021d4e4c: not an NPC trainer -> copyVarForText of
                                       # its PlayerInfo, as "{player} got $ for winning!"; client 4's PlayerInfo is not set
                                       # in a field battle: tested, it printed "????")

def battle_trainer_msg():
    """BOOL func_ov167_021d0288(BtlvCore *core, u32 trainerId, u32 msgId) -> bytes (exactly 68)."""
    import importlib.util
    spec = importlib.util.spec_from_file_location('exp_share_', os.path.join(HERE, 'exp_share.py'))
    es = importlib.util.module_from_spec(spec); spec.loader.exec_module(es)
    t = es.Thumb(BTL_TRAINER_MSG)
    t.push([4, 5, 7])                                     # 4 registers + lr keeps sp 8-aligned
    t.mov(5, 0)                                           # r5 = core
    t.movs(3, CORE_HEAPID >> 2); t.lsls(3, 3, 2)
    t.h(0x5A00 | 3 << 6 | 5 << 3 | 3)                     # ldrh r3, [r5, r3]: core->heapId
    t.ldr_lit(7, 'btlstr')                                # r7 = battle string module
    t.mov(0, 1); t.mov(1, 2)                              # trainerId, msgId
    t.ldr_off(2, 7, 0xc)
    t.bl(TrainerMsg_Load)                                 # (trainerId, msgId, work, heapId)
    t.ldr_off(0, 7, 0xc); t.ldrh_off(0, 0, 2)             # work->length (0: no such line, cleared)
    t.cmp(0, 0); t.beq('end')
    t.ldr_off(0, 7, 8); t.movs(1, 0); t.movs(2, PLAYER_CLIENT)
    t.bl(BtlStr_SetTrainerName)                           # word 0 = the player's name
    t.ldr_off(0, 7, 8); t.ldr_off(2, 7, 0xc)
    t.mov(1, 5); t.addi(1, CORE_STRBUF); t.ldr_off(1, 1, 0)
    t.bl(GFL_WordSetFormatStrbuf)                         # (wordSet, core->strbuf, work)
    t.mov(0, 5); t.bl(Btlv_PrintStrbuf)                   # r0 != 0 on return (callers ignore it)
    t.label('end'); t.pop([4, 5, 7])
    t.word('btlstr', BTL_STR)
    blob = t.assemble()
    assert len(blob) <= BTL_TRAINER_MSG_END - BTL_TRAINER_MSG, len(blob)
    return blob + bytes(BTL_TRAINER_MSG_END - BTL_TRAINER_MSG - len(blob))
