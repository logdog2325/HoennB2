"""Pokémon Emerald NDS: the seven Frontier Brains' battle fronts and overworld sheets, from Emerald's own pictures
(frontier_core_sprites, 2026-10-12; notes/FRONTIER.md section 5). Emerald builds only: everything goes into the emerald/
overlay folders, which Sapphire's and Ruby's builds never read.

    python3 sprite_emerald_frontier.py verify       every picture and palette found byte for byte in the user's dump
    python3 sprite_emerald_frontier.py check        the slots below are still free (nothing else in HoennB2 uses them)
    python3 sprite_emerald_frontier.py build [who]  -> src/sprites/trainer/front/emerald/<slot>-<who>/,
                                                       src/sprites/overworld/emerald/<code>-<who>/
    python3 sprite_emerald_frontier.py review       work/agents/frontier_core/sprites/brains_review.png and the
                                                    256x384 copy screenshots/frontier_core/brains_review.png

Source pictures: pokeemerald's files read through b2tools/emerald_src.py, which checks each picture and palette byte for
byte against roms/emerald_original.gba (the user's own dump), as b2tools/sprite_emerald.py does for Brendan and May:
- battle: graphics/trainers/front_pics/<facility>_<name>.png with the palette the game loads (gTrainerPalette_* = that
  PNG's own palette, src/data/graphics/trainers.h);
- overworld: OBJ_EVENT_GFX_<NAME> (graphics/object_events/pics/people/frontier_brains/<name>.png, palette of its tag).
Resized, never redrawn, with Sapphire's method unchanged (b2tools/sprite_upgrade.py):
- battle: battle_picture + battle_sprite (Gen 5 proportions head x1.15 / body x1.35 / x1.2 wide, outlines, Black 2's
  battle skin ramp on indices 1-4), cut onto a Black 2 front sprite's parts ("layout", installed with "mcss_from"); a
  picture no Black 2 gesture shows cleanly stands still in the intro ("static_intro"). Per picture: neck row (first row
  below the chin), hair group (hair outlines in the hair's dark tone, as Sapphire's characters), layout and intro;
- overworld: ow_frames as Scott's (b2tools/sprite_emerald_story.py): Emerald's own palette, the neck row only.

Slots (proof of freedom: `check` here; the full survey with Black 2 itself and the built ROMs:
work/agents/frontier_core/sprites/free_fronts.py, free_overworld.py, check_built.py):
- fronts: the native sprites of seven of Black 2's spare classes (converter/gen_trainers.py SPARE_CLASSES, none used by
  any Sapphire/Ruby/Emerald trainer): class c shows sprite c for c = 7, 8, 9, 30, 31, 33, 34, so a Brain's class needs
  only a name (and sex/music) edit, no sprite edit. No class of any build, no PWT entrant and no art folder reaches them.
- overworld: Black 2 12-frame people sheets no HoennB2 build places (no zone NPC, story object, script ActorNew, PWT
  record, class sprite or art folder) and that Black 2 itself sets only in Unova zones/scripts HoennB2 replaced.
"""
import os, sys, json
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, 'converter'))
import sprites, mcss  # noqa: E402
import emerald_src as E  # noqa: E402
import sprite_upgrade as U  # noqa: E402
from b2files import arc_path, narc_entries  # noqa: E402

OVERLAY = 'emerald'
SRC = os.path.join(ROOT, 'src', 'sprites')
FILES = sprites.SRC_FILES
REVIEW = os.path.join(ROOT, 'work', 'agents', 'frontier_core', 'sprites', 'brains_review.png')
SHOT = os.path.join(ROOT, 'screenshots', 'frontier_core', 'brains_review.png')

# who -> front: pokeemerald picture, Black 2 front slot (= spare class), layout (Black 2 front whose parts/animations it
# uses), intro, neck, hair [(indices, outline index)]; overworld: graphics id, Black 2 object code, neck (16x32 frame).
# Layouts: the cleanest Black 2 gesture for the picture (work/agents/frontier_core/sprites/layout_rank.py: stray pixels and
# holes over the whole intro, then checked by eye); Tucker's and Spenser's poses (arms and cape spread wide, the long
# staff) fit no Black 2 gesture, so they stand still in the intro as Sapphire's Drake and Glacia do.
BRAINS = {
    'anabel': dict(note='Anabel (Salon Maiden, Battle Tower)',
                   front=dict(pic='salon_maiden_anabel', slot=9, layout=108, intro='gesture', neck=21,
                              hair=[({5, 6, 7, 8}, 8)]),
                   overworld=dict(gfx='OBJ_EVENT_GFX_ANABEL', code=56, neck=23)),
    'tucker': dict(note='Tucker (Dome Ace, Battle Dome)',
                   front=dict(pic='dome_ace_tucker', slot=7, layout=62, intro='still', neck=21,
                              hair=[({5, 6, 7, 8}, 8)]),
                   overworld=dict(gfx='OBJ_EVENT_GFX_TUCKER', code=99, neck=22)),
    'spenser': dict(note='Spenser (Palace Maven, Battle Palace)',
                    front=dict(pic='palace_maven_spenser', slot=8, layout=62, intro='still', neck=16),
                    overworld=dict(gfx='OBJ_EVENT_GFX_SPENSER', code=107, neck=23)),
    'greta': dict(note='Greta (Arena Tycoon, Battle Arena)',
                  front=dict(pic='arena_tycoon_greta', slot=34, layout=26, intro='gesture', neck=23,
                             hair=[({7, 8}, 8)]),
                  overworld=dict(gfx='OBJ_EVENT_GFX_GRETA', code=207, neck=23)),
    'noland': dict(note='Noland (Factory Head, Battle Factory)',
                   front=dict(pic='factory_head_noland', slot=33, layout=51, intro='gesture', neck=16),
                   overworld=dict(gfx='OBJ_EVENT_GFX_NOLAND', code=298, neck=22)),
    'lucy': dict(note='Lucy (Pike Queen, Battle Pike)',
                 front=dict(pic='pike_queen_lucy', slot=31, layout=73, intro='gesture', neck=16),
                 overworld=dict(gfx='OBJ_EVENT_GFX_LUCY', code=299, neck=22)),
    'brandon': dict(note='Brandon (Pyramid King, Battle Pyramid)',
                    front=dict(pic='pyramid_king_brandon', slot=30, layout=108, intro='gesture', neck=19,
                               hair=[({10, 12}, 12)]),
                    overworld=dict(gfx='OBJ_EVENT_GFX_BRANDON', code=300, neck=22)),
}

# ---------------------------------------------------------------------------------------------------- Emerald's pictures

def pal_of(pic):
    return f'png:graphics/trainers/front_pics/{pic}.png'

_gen3_trainer, _gen3_overworld = U.gen3_trainer, U.gen3_overworld

def gen3_trainer(pic):
    if pic.startswith('em:'):
        return E.trainer_pic('front', pic[3:], pal_of(pic[3:]))
    return _gen3_trainer(pic)

def gen3_overworld(gfx):
    frames, pal, _ = E.emerald().frames(gfx)
    return frames, pal

class emerald_pictures:
    """sprite_upgrade's readers pointed at Emerald's pictures for the duration (as sprite_emerald.use_emerald)."""
    def __enter__(self):
        U.gen3_trainer, U.gen3_overworld = gen3_trainer, gen3_overworld
    def __exit__(self, *a):
        U.gen3_trainer, U.gen3_overworld = _gen3_trainer, _gen3_overworld

def front_spec(who):
    return dict(BRAINS[who]['front'], pic='em:' + BRAINS[who]['front']['pic'])

def in_dump(who):
    """[(file, [GBA addresses])] of the Brain's pictures and palettes in roms/emerald_original.gba."""
    b = BRAINS[who]
    res = E.verify_trainer('front', b['front']['pic'], pal_of(b['front']['pic'])) + E.emerald().verify(b['overworld']['gfx'])
    return res

def _where(res):
    return ', '.join(f'{p} at {", ".join(hex(a) for a in adr)}' for p, adr in res)

# ---------------------------------------------------------------------------------------------------- writing

def _folder(kind_dir, n, name):
    """The overlay folder for number n; another folder already holding n (someone else's) stops the build."""
    folder = os.path.join(kind_dir, f'{n:03d}-{name}')
    if os.path.isdir(kind_dir):
        for d in os.listdir(kind_dir):
            p = os.path.join(kind_dir, d)
            if d.split('-')[0].isdigit() and int(d.split('-')[0]) == n and p != folder:
                raise SystemExit(f'{os.path.relpath(p, ROOT)} already holds {n}: pick another slot (python3 '
                                 f'sprite_emerald_frontier.py check)')
    os.makedirs(folder, exist_ok=True)
    return folder

def write_front(who, where):
    spec = front_spec(who)
    with emerald_pictures():
        still, parts, pal, rep, sp, off = U.battle_sprite(spec)
    slot, layout = spec['slot'], spec['layout']
    folder = _folder(os.path.join(SRC, 'trainer', 'front', OVERLAY), slot, who)
    sprites.write_pal(os.path.join(folder, 'palette.pal'), pal)
    sprites.write_png(os.path.join(folder, 'parts.png'), parts.tobytes(), 256, 128, pal)
    sprites.write_png(os.path.join(folder, 'static.png'), still.tobytes(), 80, 80, pal)
    meta = dict(kind='trainer', side='front', sprite=slot, archive=sprites.ARC_TR['front'], files=sprites.tr_files(slot),
                name=who, note=f'{BRAINS[who]["note"]}: Black 2 spare class {slot}\'s own sprite (Emerald builds only)',
                source=f'pokeemerald graphics/trainers/front_pics/{BRAINS[who]["front"]["pic"]}.png and its palette '
                       f'({_where(where[:2])} in roms/emerald_original.gba)',
                layout=f'parts and animations of Black 2 front sprite {layout}',
                made_by='b2tools/sprite_emerald_frontier.py (sprite_upgrade.battle_sprite, as Sapphire\'s characters)',
                mcss_from=layout)
    if spec.get('intro') == 'still':
        meta['static_intro'] = True
    sprites.write_json(os.path.join(folder, 'sprite.json'), meta)
    return folder, rep

def ow_frames(who):
    spec = BRAINS[who]['overworld']
    with emerald_pictures():
        return U.ow_frames(dict(gfx=spec['gfx'], neck=spec['neck']))

def write_overworld(who, where):
    spec = BRAINS[who]['overworld']
    frames, pal = ow_frames(who)
    code = spec['code']
    table = sprites.ow_table(FILES)
    sheet, rec = sprites.ow_sheet_of(FILES, code, table)
    lay, pname, _ = sprites.btx_layout(narc_entries(arc_path(FILES, sprites.ARC_OW_SHEETS))[sheet])
    assert rec['spriteControllerType'] == 3 and len(lay) == 12 and lay[0][1] == 32, (code, rec)
    assert [c for c in range(len(table)) if table[c]['res1'] == sheet] == [code], f'sheet {sheet} is shared'
    folder = _folder(os.path.join(SRC, 'overworld', OVERLAY), code, who)
    sprites.write_pal(os.path.join(folder, 'palette.pal'), pal)
    for i, f in enumerate(frames):
        sprites.write_png(os.path.join(folder, f'frame_{i:02d}.png'), f.tobytes(), 32, 32, pal)
    sprites.write_json(os.path.join(folder, 'sprite.json'), dict(
        kind='overworld', code=code, sheet=sheet, frames=12, size=[32, 32], controller=3,
        textures=[l[0] for l in lay], palette=pname, name=who,
        note=f'{BRAINS[who]["note"]}, walking (Emerald builds only)',
        source=f'pokeemerald {spec["gfx"]} ({_where(where[2:])} in roms/emerald_original.gba)',
        made_by='b2tools/sprite_emerald_frontier.py (sprite_upgrade.ow_frames, as Scott\'s and Sapphire\'s characters)'))
    return folder

def build(who):
    where = in_dump(who)
    assert all(a for _, a in where), f'{who}: not found in the dump: {where}'
    folder, rep = write_front(who, where)
    ow = write_overworld(who, where)
    return [os.path.relpath(folder, ROOT), os.path.relpath(ow, ROOT), str(rep)]

# ---------------------------------------------------------------------------------------------------- slot check

def check():
    """Every Brain slot is used by nothing else in HoennB2 (any version, either sprite set): art folders, the classes of
    every build's trainers and class edits, the PWT entrants, data JSON object codes, field-script ActorNew codes."""
    import glob, re, struct
    sys.path.insert(0, os.path.join(ROOT, 'b2tools'))
    import version
    fronts = {b['front']['slot']: w for w, b in BRAINS.items()}
    codes = {b['overworld']['code']: w for w, b in BRAINS.items()}
    bad = []
    def mine(path, n, kind):
        name = os.path.basename(path)
        return name == f'{n:03d}-{(fronts if kind == "front" else codes)[n]}' and os.path.basename(os.path.dirname(path)) == OVERLAY
    for kind, nums, pat in (('front', fronts, 'trainer/front'), ('overworld', codes, 'overworld')):
        for d in glob.glob(os.path.join(ROOT, 'src', 'sprites*', *pat.split('/'), '**', '*'), recursive=True):
            n = os.path.basename(d).split('-')[0]
            if os.path.isdir(d) and n.isdigit() and int(n) in nums and not mine(d, int(n), kind):
                bad.append(f'{kind} {n}: art folder {os.path.relpath(d, ROOT)}')
            if os.path.isfile(os.path.join(d, 'sprite.json')):
                m = sprites.read_json(os.path.join(d, 'sprite.json'))
                for k in ('copy_of', 'from_code'):
                    if kind == 'overworld' and int(m.get(k, -1)) in nums: bad.append(f'overworld {m[k]}: {k} in {d}')
    arm9 = open(os.path.join(ROOT, 'external', 'pokebw2', 'build', 'b2_us', 'build', 'arm9.bin'), 'rb').read()
    base = {c: arm9[0x02092394 - 0x02004000 + 4 * c] for c in range(237)}
    pwt = narc_entries(arc_path(FILES, 247))[0]
    for ver in ('sapphire', 'ruby', 'emerald'):
        os.environ['HOENN_VERSION'] = ver
        import importlib; importlib.reload(version)
        cls = version.load_json(os.path.join(ROOT, 'data', 'hoenn_trainer_classes.json'))
        spr = dict(base)
        spr.update({int(c): e['sprite'] for c, e in cls['edits'].items() if 'sprite' in e})
        for t, v in version.load_json(os.path.join(ROOT, 'data', 'hoenn_trainer_data.json'))['trainers'].items():
            if spr[v['b2_class']] in fronts: bad.append(f'front {spr[v["b2_class"]]}: {ver} trainer {t} (class {v["b2_class"]})')
        for c, e in cls['edits'].items():
            if e.get('sprite') in fronts: bad.append(f'front {e["sprite"]}: {ver} class edit {c}')
        if ver == 'emerald': spr_em = spr
        for i in range(len(pwt) // 16):
            if spr[pwt[16 * i + 4]] in fronts: bad.append(f'front {spr[pwt[16 * i + 4]]}: {ver} PWT record {i}')
            if struct.unpack_from('<H', pwt, 16 * i + 2)[0] in codes: bad.append(f'overworld: PWT record {i}')
    os.environ.pop('HOENN_VERSION', None)
    def walk(o, f):
        # a dict with a Black 2 trainer class: its "sprite" is that class's front sprite (data/emerald/frontier.json),
        # unless it also names a graphics id ("gfx": frontier_pike.json's overworld code); elsewhere an object code
        if isinstance(o, dict):
            if f.endswith('sprite_map.json') and 'frontier brain' in json.dumps(o, ensure_ascii=False).lower() \
                    and ('code' in o or 'sprite' in o):
                return                                      # the Brains' own registry rows (data/emerald/sprite_map.json)
            front_rec = 'b2_class' in o and 'gfx' not in o
            if isinstance(o.get('b2_class'), int) and spr_em[o['b2_class']] in fronts:
                bad.append(f'front {spr_em[o["b2_class"]]}: {f} class {o["b2_class"]} ({o.get("name", "")})')
            for k, v in o.items():
                if k == 'sprite' and front_rec:
                    if v in fronts: bad.append(f'front {v}: {f} "sprite" ({o.get("name", "")})')
                elif k in ('model', 'model_emerald', 'code', 'sprite') and isinstance(v, int) and v in codes:
                    bad.append(f'overworld {v}: {f} "{k}"')
                walk(v, f)
        elif isinstance(o, list):
            for v in o: walk(v, f)
    for f in glob.glob(os.path.join(ROOT, 'data', '**', '*.json'), recursive=True):
        if os.path.basename(f) in ('hoenn_trainer_classes.json',): continue
        try: walk(json.load(open(f)), os.path.relpath(f, ROOT))
        except ValueError: pass
    for p in glob.glob(os.path.join(ROOT, 'src', 'field_scripts', '**', '*.s'), recursive=True) + \
            glob.glob(os.path.join(ROOT, 'src', 'field_scripts', '**', '*.inc'), recursive=True):
        for m in re.finditer(r'ActorNew\s+[^,]+,[^,]+,[^,]+,[^,]+,\s*(\d+)', open(p, errors='replace').read()):
            if int(m.group(1)) in codes: bad.append(f'overworld {m.group(1)}: ActorNew in {os.path.relpath(p, ROOT)}')
    return bad

# ---------------------------------------------------------------------------------------------------- review

def _rgba(a, pal):
    return U.rgba(np.asarray(a, np.uint8), pal)

def _crop(im):
    a = np.array(im)[..., 3]
    ys, xs = np.nonzero(a)
    return im.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)) if len(ys) else im

def _installed_front(who):
    """(still RGBA, [intro frames RGBA]) of the installed folder on its layout's cells, as the game plays it."""
    b = BRAINS[who]['front']
    folder = os.path.join(SRC, 'trainer', 'front', OVERLAY, f'{b["slot"]:03d}-{who}')
    pal = sprites.read_pal(os.path.join(folder, 'palette.pal'))
    parts = np.frombuffer(sprites.read_png(os.path.join(folder, 'parts.png'), pal, 256, 128), np.uint8).reshape(128, 256)
    still = np.frombuffer(sprites.read_png(os.path.join(folder, 'static.png'), pal, 80, 80), np.uint8).reshape(80, 80)
    e = list(narc_entries(arc_path(FILES, sprites.ARC_TR['front'])))
    s, L = b['slot'], b['layout']
    e[8 * s:8 * s + 8] = e[8 * L:8 * L + 8]
    if b.get('intro') == 'still':
        e[8 * s + 5] = mcss.static_intro(e[8 * s + 5])
    sp = mcss.Sprite(e, 8 * s)
    T = sp.length(0)
    fr = U.anim_frames(sp, parts, pal, [T // 4, T // 2, 3 * T // 4])
    return _crop(_rgba(still, pal)), fr[:3]

def _installed_ow(who):
    code = BRAINS[who]['overworld']['code']
    folder = os.path.join(SRC, 'overworld', OVERLAY, f'{code:03d}-{who}')
    pal = sprites.read_pal(os.path.join(folder, 'palette.pal'))
    return [_rgba(np.frombuffer(sprites.read_png(os.path.join(folder, f'frame_{k:02d}.png'), pal, 32, 32), np.uint8)
                  .reshape(32, 32), pal) for k in range(12)]

def review(path=REVIEW, shot=SHOT):
    from PIL import Image, ImageDraw
    BG = (112, 136, 152, 255)
    rows = []
    for who, b in BRAINS.items():
        a, gp = E.trainer_pic('front', b['front']['pic'], pal_of(b['front']['pic']))
        em_front = _crop(_rgba(a, gp))
        fr, op, _ = E.emerald().frames(b['overworld']['gfx'])
        em_ow = [_rgba(fr[k], op) for k in (0, 1, 2)]            # down, up, left (Emerald's frames 0-2)
        still, intro = _installed_front(who)
        ow = _installed_ow(who)
        rows.append((who, b, em_front, still, intro, em_ow, ow))
    # full sheet: per Brain, Emerald front | new still | intro gesture | Emerald overworld | new overworld (12 frames)
    S = 2
    def strip(ims, sc, gap=4):
        ims = [i.resize((i.width * sc, i.height * sc), Image.NEAREST) for i in ims]
        W = sum(i.width + gap for i in ims) - gap; H = max(i.height for i in ims)
        o = Image.new('RGBA', (W, H), (0, 0, 0, 0)); x = 0
        for i in ims:
            o.alpha_composite(i, (x, H - i.height)); x += i.width + gap
        return o
    blocks = []
    for who, b, em_front, still, intro, em_ow, ow in rows:
        f, o = b['front'], b['overworld']
        cells = [('Emerald (dump)', strip([em_front], S)), ('Black 2: still', strip([still], S)),
                 ('intro' + (' (still)' if f['intro'] == 'still' else f' gesture of {f["layout"]}'), strip(intro, S)),
                 ('Emerald walk', strip(em_ow, 3)), ('Black 2 walk (12 frames)', strip(ow, 2, 2))]
        title = (f'{b["note"]}: front sprite {f["slot"]} (class {f["slot"]}, on {f["layout"]}\'s parts, neck {f["neck"]}), '
                 f'overworld code {o["code"]} (neck {o["neck"]})')
        blocks.append((title, cells))
    W = max(sum(max(c.width, 6 * len(l)) + 16 for l, c in cells) for _, cells in blocks) + 20
    H = sum(16 + 14 + max(c.height for _, c in cells) + 12 for _, cells in blocks) + 30
    out = Image.new('RGBA', (W, H), BG); d = ImageDraw.Draw(out)
    d.text((10, 8), 'Frontier Brains, Pokemon Emerald NDS: Emerald\'s own pictures resized with Sapphire\'s method '
                    '(b2tools/sprite_emerald_frontier.py)', fill=(255, 255, 255, 255))
    y = 30
    for title, cells in blocks:
        d.text((10, y), title, fill=(255, 240, 160, 255)); y += 16
        x = 10; h = max(c.height for _, c in cells)
        for label, c in cells:
            d.text((x, y), label, fill=(230, 236, 255, 255))
            out.alpha_composite(c, (x, y + 14 + h - c.height)); x += max(c.width, 6 * len(label)) + 16
        y += 14 + h + 12
    os.makedirs(os.path.dirname(path), exist_ok=True)
    out.convert('RGB').save(path)
    # 256x384 copy, 1:1 pixels: every Brain's front (Emerald | Black 2 still), then walking (Emerald's down and left
    # frames | Black 2's down and left frames), packed in rows left to right
    small = Image.new('RGBA', (256, 384), BG); d = ImageDraw.Draw(small)
    def pack(groups, y, gap_in, gap_out):
        x, row_h = 0, 0
        for ims in groups:
            w = sum(i.width for i in ims) + gap_in * (len(ims) - 1)
            h = max(i.height for i in ims)
            if x and x + w > 256: x, y, row_h = 0, y + row_h + 2, 0
            for i in ims:
                small.alpha_composite(i, (x, y + h - i.height)); x += i.width + gap_in
            x += gap_out - gap_in; row_h = max(row_h, h)
        return y + row_h
    d.text((2, 0), 'Frontier Brains: Emerald | Black 2', fill=(255, 255, 255, 255))
    y = pack([[r[2], r[3]] for r in rows], 13, 1, 3)
    y = pack([[_crop(r[5][0]), _crop(r[5][2]), _crop(r[6][3]), _crop(r[6][6])] for r in rows], y + 6, 1, 6)
    assert y <= 384, y
    os.makedirs(os.path.dirname(shot), exist_ok=True)
    small.convert('RGB').save(shot)
    return path, shot

def main(argv):
    cmd = argv[0] if argv else ''
    if cmd == 'verify':
        bad = 0
        for who in BRAINS:
            for p, adr in in_dump(who):
                bad += not adr
                print(f'{"ok " if adr else "MISSING"} {who}: {p} at {", ".join(hex(a) for a in adr) or "-"}')
        print('all found in the dump' if not bad else f'{bad} not found'); sys.exit(1 if bad else 0)
    elif cmd == 'check':
        bad = check()
        print('\n'.join(bad) or 'every Brain slot is free: ' + ', '.join(
            f'{w} front {b["front"]["slot"]} / overworld {b["overworld"]["code"]}' for w, b in BRAINS.items()))
        sys.exit(1 if bad else 0)
    elif cmd == 'build':
        for who in (argv[1:] or list(BRAINS)):
            print(who, '->', build(who))
    elif cmd == 'review':
        print(*[os.path.relpath(p, ROOT) for p in review()])
    else:
        print(__doc__)

if __name__ == '__main__':
    main(sys.argv[1:])
