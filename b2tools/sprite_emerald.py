"""Pokémon Emerald NDS, CLASSIC sprite set: Brendan's and May's Emerald outfits and Steven's battle back, from Emerald's
own sprites (the user's dump, read through pokeemerald's files: b2tools/emerald_src.py verifies every picture and
palette byte for byte against roms/emerald_original.gba), resized, outlined and placed exactly as Sapphire's were:
the same code with the same settings (b2tools/sprite_upgrade_players.py for the overworld sheets and the battle fronts,
b2tools/sprite_upgrade_player_backs.py for the battle backs; their own steps are b2tools/sprite_upgrade.py's). Only
the source pictures change. Nothing is redrawn. (notes/EMERALD_PLAN.md phase 5, DECISIONS 2026-10-11: "Brendan/May
Emerald outfits from Emerald's own sprites for CLASSIC".)

    python3 sprite_emerald.py check            the Sapphire run of the same code reproduces the committed Sapphire art
                                               (src/sprites/overworld/231-248, trainer/front|back/000-001) pixel for pixel
    python3 sprite_emerald.py build [part ...] brendan, may, steven (default: all) -> the emerald/ overlay folders
    python3 sprite_emerald.py review           screenshots/sprites/emerald_classic_review.png

Output (the Ruby overlay layout, notes/RUBY.md "WP0 layout"; an Emerald build reads <kind>/emerald/ over the shared
folders, emerald_wp0's machinery):
    src/sprites/overworld/emerald/231-239-brendan-*, 240-248-may-*      every player sheet (walk-run, bike, surf, item,
                                                                        action2, action5, throw, balance, fishing)
    src/sprites/trainer/front/emerald/000-brendan, 001-may              battle fronts (rival battles, Hall of Fame),
                                                                        on front 108's parts as Sapphire's
    src/sprites/trainer/back/emerald/000-brendan, 001-may               battle backs (Nate's / Rosa's cells)
    src/sprites/trainer/back/emerald/<STEVEN_SLOT>-steven               Steven's back for the Space Center tag battle
The rival NPC sheets (codes 1-6, 136-161: {"copy_of": 231..248} in the shared folders), the Continue icon
(src/sprites/objframes) and the trainer card picture (src/sprites/cardpic) follow these folders by themselves.

Settings that are per picture (all Sapphire's own, checked to fit Emerald's pictures: the Emerald pictures have the
same pose, head and neck rows as Sapphire's, screenshots/sprites/emerald_necks.png):
- overworld: sprite_upgrade_players.PLAYER_SETS (Sapphire frame -> Black 2 frame; Emerald's pic tables have the same
  frame order: walk 0-8 + run 9-17, Mach Bike 9, surf 12, field move 5, fishing 12, checked), Sapphire's colour
  setting for Brendan's clothes on the overworld palette (indices 5, 6, 8 = his battle picture's three navy tones),
  taken from Emerald's battle picture (the same three tones), May's hair group;
- battle fronts: neck rows 24 / 23, layout 108, the intro gesture;
- battle backs: neck rows 42 / 45, head drop 0 / 4, the same cells and nodes;
- Steven: the player-back method on STEVEN_SLOT's cells (see STEVEN).
"""
import copy, os, shutil, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, 'converter'))
import sprites, mcss  # noqa: E402
import emerald_src as E  # noqa: E402
import sprite_upgrade as U  # noqa: E402
import sprite_upgrade_players as P  # noqa: E402
import sprite_upgrade_player_backs as PB  # noqa: E402

OVERLAY = 'emerald'
SRC = os.path.join(ROOT, 'src', 'sprites')
SHOTS = os.path.join(ROOT, 'screenshots', 'sprites')

# ---------------------------------------------------------------------------------------------------- Emerald's pictures
# The Sapphire tools read pokeruby's files through U.gen3_trainer (battle pictures) and P.g3 (overworld frames). For an
# Emerald run they get Emerald's pictures instead: pic names 'em:<side>:<name>' and the overworld cache P._g3.
EM_PALS = {'brendan': 'brendan', 'may': 'may', 'steven': E.STEVEN_PAL}
_gen3_trainer = U.gen3_trainer

def gen3_trainer(pic):
    if pic.startswith('em:'):
        _, side, name = pic.split(':')
        return E.trainer_pic(side, name, EM_PALS[name])
    return _gen3_trainer(pic)

def use_emerald():
    """Point the Sapphire tools at Emerald's pictures (overworld frames, battle fronts and backs)."""
    U.gen3_trainer = gen3_trainer
    P._g3.clear()
    e = E.emerald()
    for who in ('BRENDAN', 'MAY'):
        for s in ('NORMAL', 'MACH_BIKE', 'SURFING', 'FIELD_MOVE', 'FISHING'):
            fr, pal, _ = e.frames(f'OBJ_EVENT_GFX_{who}_{s}')
            P._g3[(who, s)] = (fr, pal)

def use_sapphire():
    U.gen3_trainer = _gen3_trainer
    P._g3.clear()

def emerald_players():
    """sprite_upgrade_players.PLAYERS with Emerald's pictures: Sapphire's settings; Brendan's three clothes colours on
    the overworld palette taken from Emerald's battle picture (Sapphire took them from Sapphire's: the same three
    navy tones there, at front indices 6, 7, 8)."""
    out = copy.deepcopy(P.PLAYERS)
    _, fpal = E.trainer_pic('front', 'brendan', 'brendan')
    sap = P.PLAYERS['brendan']['colours']
    out['brendan']['colours'] = {5: fpal[6], 6: fpal[7], 8: fpal[8]}
    for k, i in ((5, 6), (6, 7), (8, 8)):          # the same tones (5-bit) as Sapphire's setting
        assert all(abs(a - b) <= 4 for a, b in zip(sap[k], fpal[i])), (k, sap[k], fpal[i])
    for who in out:
        out[who]['battle']['pic'] = f'em:front:{who}'
    return out

def emerald_backs():
    out = copy.deepcopy(PB.CHARS)
    for who, c in out.items():
        c['pic'] = f'em:back:{who}'
        c['note'] = f'{who.capitalize()} (player back), from Emerald'
    return out

# ---------------------------------------------------------------------------------------------------- Steven's back
# Steven's back for the Space Center tag battle (Emerald's Steven partner; pokeemerald back_pics/steven.png, palette =
# his front picture's, gTrainerPalette_Steven). Black 2 shows a partner's back by its trainer class
# (TRAINER_CLASS_BACK_SPRITES, arm9 0x02092314: 32 {class, back sprite} pairs); Steven's own class (177, PWT) has no
# entry, so the tag battle needs one (phase 4's choice: e.g. replace an entry's class by 177). The art goes into back
# sprite 5, which only class 37 reaches (NO_DATA_M_37, HoennB2's Tuber M: a Tuber never stands beside the player): its
# cells, multi-cells and throw are a copy of Nate's (sprite 0: same cell sizes, the same node places; checked by
# steven_layout_check), so Brendan's settings apply unchanged: frames 3 (standing) = cells 1 + 0, 1 (wind-up) = cell 4,
# 2 (throw) = cell 5, cells 2 and 3 clear, animation 1 stops sliding multi-cells 2-4. Per-picture settings: his neck
# (first row of the shoulders in frame 3: row 40; Brendan's 42), a head drop of 2 rows, and as for Brendan no hair group
# (black outlines).
STEVEN_SLOT = 5
STEVEN_NECK = 40
STEVEN_HEAD_DROP = 2       # his head 2 rows lower than Hugh's so the throw (frame 2) fits cell 5 (as May's 4 for cell 6)

def steven_spec(slot=STEVEN_SLOT):
    """A sprite_upgrade_player_backs CHARS entry for Steven on back sprite `slot` (Brendan's on Nate's cells)."""
    b = PB.CHARS['brendan']
    return dict(slot=slot, pic='em:back:steven', note='Steven (Space Center tag battle partner, back), from Emerald',
                neck=STEVEN_NECK, head_drop=STEVEN_HEAD_DROP, hair=[], poses=copy.deepcopy(b['poses']), clear=list(b['clear']),
                blank_seq=b['blank_seq'])

def steven_layout_check(slot=STEVEN_SLOT):
    """Back sprite `slot` has Nate's (sprite 0's) cells, multi-cell nodes and animations: Brendan's poses fit it."""
    _, _, _, a = PB.donor(0)
    _, _, _, b = PB.donor(slot)
    same_cells = [PB.quad(a, i) for i in range(6)] == [PB.quad(b, i) for i in range(6)]
    same_nodes = [[(n['seq'], n['x'], n['y']) for n in mc] for mc in a.nmcr] == \
        [[(n['seq'], n['x'], n['y']) for n in mc] for mc in b.nmcr]
    same_anim = [[(t, r['idx']) for t, r in sq['frames']] for sq in a.nmar] == \
        [[(t, r['idx']) for t, r in sq['frames']] for sq in b.nmar]
    return same_cells, same_nodes, same_anim

# ---------------------------------------------------------------------------------------------------- writing

def _replace_folder(kind_dir, n, keep):
    """Another folder for the same number in this overlay folder (an older name) moves to ~/.Trash."""
    if not os.path.isdir(kind_dir):
        return
    for d in os.listdir(kind_dir):
        p = os.path.join(kind_dir, d)
        if d.split('-')[0].isdigit() and int(d.split('-')[0]) == n and p != keep:
            shutil.move(p, os.path.join(os.path.expanduser('~/.Trash'), f'{d}-{time.strftime("%Y%m%d-%H%M%S")}'))

def write_overworld(code, name, frames, pal, note, source, made_by='b2tools/sprite_emerald.py', root=SRC):
    arrs, _, meta = P.U_donor(code)
    assert len(frames) == meta['frames'] and frames[0].shape == arrs[0].shape, (code, len(frames), meta['frames'])
    kind_dir = os.path.join(root, 'overworld', OVERLAY)
    folder = os.path.join(kind_dir, f'{code:03d}-{name}')
    _replace_folder(kind_dir, code, folder)
    os.makedirs(folder, exist_ok=True)
    sprites.write_pal(os.path.join(folder, 'palette.pal'), pal)
    w, h = meta['size']
    for i, f in enumerate(frames):
        sprites.write_png(os.path.join(folder, f'frame_{i:02d}.png'), np.ascontiguousarray(f).tobytes(), w, h, pal)
    sprites.write_json(os.path.join(folder, 'sprite.json'), dict(meta, name=name, note=note, source=source,
                                                                   made_by=made_by))
    return folder

def write_front(name, spec, note, made_by='b2tools/sprite_emerald.py', root=SRC):
    still, parts, pal, rep, sp, off = U.battle_sprite(spec)
    slot, layout = spec['slot'], spec['layout']
    kind_dir = os.path.join(root, 'trainer', 'front', OVERLAY)
    folder = os.path.join(kind_dir, f'{slot:03d}-{name}')
    _replace_folder(kind_dir, slot, folder)
    os.makedirs(folder, exist_ok=True)
    sprites.write_pal(os.path.join(folder, 'palette.pal'), pal)
    sprites.write_png(os.path.join(folder, 'parts.png'), parts.tobytes(), 256, 128, pal)
    sprites.write_png(os.path.join(folder, 'static.png'), still.tobytes(), 80, 80, pal)
    meta = dict(kind='trainer', side='front', sprite=slot, archive=sprites.ARC_TR['front'], files=sprites.tr_files(slot),
                name=name, note=note, source=f'pokeemerald graphics/trainers/front_pics/{name}.png (Emerald dump: '
                f'emerald_src.py verify)', layout=f'parts and animations of Black 2 front sprite {layout}',
                made_by=made_by)
    if layout != slot:
        meta['mcss_from'] = layout
    if spec.get('intro') == 'still':
        meta['static_intro'] = True
    sprites.write_json(os.path.join(folder, 'sprite.json'), meta)
    return folder, rep

def write_back(name, c, made_by='b2tools/sprite_emerald.py', root=SRC):
    """sprite_upgrade_player_backs.write for a CHARS-like entry c, into the emerald/ overlay."""
    PB.CHARS[name] = c
    new, pal, edits, (e, tex, dpal, sp, sp2), figs = PB.build(name)
    s = c['slot']
    kind_dir = os.path.join(root, 'trainer', 'back', OVERLAY)
    folder = os.path.join(kind_dir, f'{s:03d}-{name}')
    _replace_folder(kind_dir, s, folder)
    os.makedirs(folder, exist_ok=True)
    _, _, still = sprites.tr_decode_image(e[8 * s], 'static')            # Black 2 leaves the back still empty
    sprites.write_pal(os.path.join(folder, 'palette.pal'), pal)
    sprites.write_png(os.path.join(folder, 'parts.png'), new.tobytes(), 256, 128, pal)
    sprites.write_png(os.path.join(folder, 'static.png'), bytes(still), 80, 80, pal)
    sprites.write_json(os.path.join(folder, 'sprite.json'), dict(
        kind='trainer', side='back', sprite=s, archive=sprites.ARC_TR['back'], files=sprites.tr_files(s),
        name=name, note=c['note'], source=f"pokeemerald graphics/trainers/back_pics/{c['pic'].split(':')[-1]}.png "
        f"(frames {', '.join(str(k) for k, _, _ in c['poses'])}; Emerald dump: emerald_src.py verify)",
        layout=f'cells, quads and throw timing of Black 2 back sprite {s}; whole-figure poses',
        node_edits=edits, still_multicells=[2, 3, 4], made_by=made_by))
    data = sprites.tr_encode_image(e[8 * s + 1], 'parts', new.tobytes())
    return folder, f'parts {len(data)} bytes compressed (donor {len(e[8 * s + 1])})'

# ---------------------------------------------------------------------------------------------------- parts

def player(who):
    use_emerald()
    spec = emerald_players()[who]
    done = []
    for n, (name, plan) in P.PLAYER_SETS.items():
        frames, pal, size = P.player_sheet(spec, n)
        sets = sorted({s.lower() for s, _, _ in plan})
        files = {'normal': 'walking, running', 'mach_bike': 'mach_bike', 'surfing': 'surfing',
                 'field_move': 'field_move', 'fishing': 'fishing'}
        done.append(write_overworld(spec['base'] + n, f'{who}-{name}', frames, pal,
                                    f'{spec["note"]} (player, Emerald outfit), {name}',
                                    f'pokeemerald graphics/object_events/pics/people/{who}/' +
                                    ', '.join(files[s] for s in sets) + ' (Emerald dump: emerald_src.py verify)'))
    folder, rep = write_front(who, spec['battle'], f'{spec["note"]} (rival battles, Hall of Fame), Emerald outfit')
    done.append(folder)
    folder, rep2 = write_back(who, emerald_backs()[who])
    done.append(folder)
    return [os.path.relpath(d, ROOT) for d in done] + [str(rep), rep2]

def steven():
    use_emerald()
    assert all(steven_layout_check()), steven_layout_check()
    spec = steven_spec()
    folder, rep = write_back('steven', spec)
    return [os.path.relpath(folder, ROOT), rep]

# ---------------------------------------------------------------------------------------------------- check

def _folder_frames(folder):
    from PIL import Image
    fs = sorted(f for f in os.listdir(folder) if f.startswith('frame_'))
    return [np.array(Image.open(os.path.join(folder, f))) for f in fs]

def _png(path):
    from PIL import Image
    return np.array(Image.open(path))

def check():
    """The same code with Sapphire's pictures gives the committed Sapphire art (pixels and palettes): proof that the
    Emerald run uses Sapphire's method unchanged."""
    use_sapphire()
    out, bad = [], 0
    for who, spec in P.PLAYERS.items():
        for n, (name, plan) in P.PLAYER_SETS.items():
            code = spec['base'] + n
            frames, pal, size = P.player_sheet(spec, n)
            folder = os.path.join(SRC, 'overworld', f'{code:03d}-{who}-{name}')
            old = _folder_frames(folder)
            same = len(old) == len(frames) and all((a == b).all() for a, b in zip(old, frames))
            opal = sprites.read_pal(os.path.join(folder, 'palette.pal')) if hasattr(sprites, 'read_pal') else None
            bad += not same
            out.append(f'{"same" if same else "DIFFERS"} overworld {code} {who}-{name}')
        still, parts, pal, rep, sp, off = U.battle_sprite(spec['battle'])
        f = os.path.join(SRC, 'trainer', 'front', f'{spec["battle"]["slot"]:03d}-{who}')
        same = (_png(os.path.join(f, 'parts.png')) == parts).all() and (_png(os.path.join(f, 'static.png')) == still).all()
        bad += not same
        out.append(f'{"same" if same else "DIFFERS"} front {spec["battle"]["slot"]} {who}')
        new, pal, edits, _, _ = PB.build(who)
        f = os.path.join(SRC, 'trainer', 'back', f'{PB.CHARS[who]["slot"]:03d}-{who}')
        meta = sprites.read_json(os.path.join(f, 'sprite.json'))
        same = (_png(os.path.join(f, 'parts.png')) == new).all() and meta['node_edits'] == edits
        bad += not same
        out.append(f'{"same" if same else "DIFFERS"} back {PB.CHARS[who]["slot"]} {who}')
    return out, bad

# ---------------------------------------------------------------------------------------------------- review

def _pal_png(path):
    from PIL import Image
    im = Image.open(path)
    p = im.getpalette()[:48]
    return np.array(im), [tuple(p[3 * i:3 * i + 3]) for i in range(16)]

def _strip(ims, sc, gap=4):
    from PIL import Image
    ims = [i.resize((i.width * sc, i.height * sc), Image.NEAREST) for i in ims]
    W = sum(i.width + gap for i in ims); H = max(i.height for i in ims)
    o = Image.new('RGBA', (W, H), (0, 0, 0, 0)); x = 0
    for i in ims:
        o.alpha_composite(i, (x, H - i.height)); x += i.width + gap
    return o

def _crop(im):
    a = np.array(im)[..., 3]
    ys, xs = np.nonzero(a)
    return im.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)) if len(ys) else im

def _sheet(sections, title, path):
    from PIL import Image, ImageDraw
    rows = []
    for t, cells in sections:
        rows.append(('T', t))
        rows += cells
    W = max(im.width for k, im in rows if k != 'T') + 200
    H = sum((16 if k == 'T' else im.height + 6) for k, im in rows) + 30
    out = Image.new('RGBA', (W, H), (88, 112, 128, 255)); d = ImageDraw.Draw(out)
    d.text((6, 6), title, fill=(255, 255, 255, 255))
    y = 26
    for k, im in rows:
        if k == 'T':
            d.text((6, y), im, fill=(255, 240, 160, 255)); y += 16
        else:
            d.text((6, y + 2), k, fill=(230, 236, 255, 255))
            out.alpha_composite(im, (194, y)); y += im.height + 6
    os.makedirs(os.path.dirname(path), exist_ok=True)
    out.convert('RGB').save(path)
    return path

def review(path=None):
    """screenshots/sprites/emerald_classic_review.png: per sheet Emerald's own frames / the new Emerald CLASSIC frames
    / HoennB2's Sapphire CLASSIC frames (the same code on Sapphire's pictures); battle fronts and backs as their
    animations play (intro gesture, the throw); Steven's back with Black 2's own sprite 5 (Hugh) at the same ticks."""
    from PIL import Image
    use_emerald()
    rgba = U.rgba
    sections = []
    players = emerald_players()
    for who, spec in players.items():
        for n, (setname, plan) in P.PLAYER_SETS.items():
            code = spec['base'] + n
            folder = os.path.join(SRC, 'overworld', OVERLAY, f'{code:03d}-{who}-{setname}')
            new, npal = [], sprites.read_pal(os.path.join(folder, 'palette.pal')) if hasattr(sprites, 'read_pal') else None
            fr_new = _folder_frames(folder)
            _, npal = _pal_png(os.path.join(folder, 'frame_00.png'))
            sfold = os.path.join(SRC, 'overworld', f'{code:03d}-{who}-{setname}')
            _, spal = _pal_png(os.path.join(sfold, 'frame_00.png'))
            fr_sap = _folder_frames(sfold)
            size = fr_new[0].shape[0]
            sc = 3 if size == 32 else 2
            srcs = []
            for s_, k, fl in plan:
                fr, gp = P.g3(spec['who'], s_)
                img = rgba(fr[k], gp)
                srcs.append(img.transpose(Image.FLIP_LEFT_RIGHT) if 'm' in fl else img)
            sections.append((f'{who.capitalize()} {setname} ({code})', [
                ('Emerald (dump)', _strip(srcs, sc)), ('new: Emerald CLASSIC', _strip([rgba(f, npal) for f in fr_new], sc)),
                ('Sapphire CLASSIC (now)', _strip([rgba(f, spal) for f in fr_sap], sc))]))
        b = spec['battle']
        a, gp = U.gen3_trainer(b['pic'])
        still, parts, npal, rep, sp, off = U.battle_sprite(b)
        T = sp.length(0)
        fr = U.anim_frames(sp, parts, npal, [0, T // 4, T // 2, 3 * T // 4])
        sf = os.path.join(SRC, 'trainer', 'front', f'{b["slot"]:03d}-{who}')
        sstill, spal = _pal_png(os.path.join(sf, 'static.png'))
        sections.append((f'{who.capitalize()} battle front {b["slot"]} (on front {b["layout"]}\'s parts): still, then the '
                         'intro gesture', [('Emerald (dump)', _strip([rgba(a, gp)], 2)),
                                          ('new (still, intro)', _strip([fr[-1]] + fr[:4], 2)),
                                          ('Sapphire CLASSIC (still)', _strip([_crop(rgba(sstill, spal))], 2))]))
    ticks = [(0, 0), (1, 10), (1, 25), (1, 36), (1, 45), (1, 99)]
    def bframe(spr, t_, p_, an, t):
        im = U.rgba(mcss.render(spr, t_, an, t), p_)
        return im.crop((24, 0, im.width - 24, mcss.ORIGIN[1]))
    backs = dict(emerald_backs(), steven=steven_spec())
    for name, c in backs.items():
        PB.CHARS[name] = c
        new, pal, edits, (e, tex, dpal, sp, sp2), figs = PB.build(name)
        a, gp = U.gen3_trainer(c['pic'])
        cells = [('Emerald (dump), frames 0-3', _strip([U.rgba(a[64 * k:64 * k + 64], gp) for k in range(4)], 2)),
                 ('new: standing, throw', _strip([bframe(sp2, new, pal, an, t) for an, t in ticks], 1))]
        if name != 'steven':
            sf = os.path.join(SRC, 'trainer', 'back', f'{c["slot"]:03d}-{name}')
            old, op = _pal_png(os.path.join(sf, 'parts.png'))
            ometa = sprites.read_json(os.path.join(sf, 'sprite.json'))
            e2 = list(e)
            e2[8 * c['slot'] + 4] = mcss.set_nodes(e[8 * c['slot'] + 4], ometa['node_edits'])
            e2[8 * c['slot'] + 5] = mcss.still_translations(e[8 * c['slot'] + 5], 1, [2, 3, 4])
            cells.append(('Sapphire CLASSIC (now)', _strip([bframe(mcss.Sprite(e2, 8 * c['slot']), old, op, an, t)
                                                            for an, t in ticks], 1)))
        cells.append((f'Black 2 back {c["slot"]} (donor)', _strip([bframe(sp, tex, dpal, an, t) for an, t in ticks], 1)))
        sections.append((f'{name.capitalize()} battle back {c["slot"]}: animation 0, then the throw at ticks ' +
                         ', '.join(str(t) for _, t in ticks[1:]), cells))
    return _sheet(sections, 'Pokemon Emerald NDS, CLASSIC set: Emerald\'s own sprites through Sapphire\'s method '
                  '(b2tools/sprite_emerald.py)', path or os.path.join(SHOTS, 'emerald_classic_review.png'))

PARTS = {'brendan': lambda: player('brendan'), 'may': lambda: player('may'), 'steven': steven}

if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else ''
    if cmd == 'check':
        lines, bad = check()
        print('\n'.join(lines))
        print('Sapphire run reproduces the committed art' if not bad else f'{bad} differ')
    elif cmd == 'build':
        for name in (sys.argv[2:] or list(PARTS)):
            print(name, '->', PARTS[name]())
    elif cmd == 'review':
        print(review())
    else:
        print(__doc__)
