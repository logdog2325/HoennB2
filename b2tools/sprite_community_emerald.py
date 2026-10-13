"""Pokémon Emerald NDS, NEW sprite set: Brendan's Emerald outfit by hyo-oppa (src/sprites/community/incoming/emerald/
brendan_emerald_hyo-oppa.png; credit: hyo-oppa, src/sprites/community/incoming/CREDITS.md "Emerald"). The author's page
says "DO NOT EDIT!": the sheet is only cut, placed and palette-indexed, exactly as b2tools/sprite_community.py does
with hyo-oppa's Sapphire sheet, with one difference: no colour is ever merged (sprite_community's NEAR merges of
near-identical colours and its EXTRA_MERGES are off: NEAR = 0). A sheet or picture that needs more than Black 2's 15
colours (+ clear) or does not fit Black 2's frame stays CLASSIC and is reported.

    python3 sprite_community_emerald.py analyze          colours and fit of every planned Black 2 sheet / picture
    python3 sprite_community_emerald.py build            write the installable ones into the Emerald NEW overlay
    python3 sprite_community_emerald.py review           screenshots/sprites/emerald_new_review.png

Output (the NEW set's layout, src/sprites_gen5 = src/sprites' layout, with the Ruby-style emerald/ overlay folder):
    src/sprites_gen5/overworld/emerald/231-238-brendan-*     hyo-oppa's frames
    src/sprites_gen5/overworld/emerald/239-brendan-fishing   CLASSIC Emerald fishing (the sheet has no fishing frames;
                                                             a copy of src/sprites/overworld/emerald/239, so the
                                                             Sapphire-outfit NEW fishing in src/sprites_gen5/overworld/
                                                             239 never shows in Emerald)
    src/sprites_gen5/trainer/front/emerald/000-brendan       the sheet's battle front, on front 108's parts
    src/sprites_gen5/trainer/back/emerald/000-brendan        the sheet's back throw (frames 1, 3, 4 of 5) on Nate's
                                                             cells, as the Sapphire NEW back (GEN5_BACK_LIFT applies)
    src/sprites_gen5/overworld/emerald/240-248-may-*          copies of the shared NEW May (DiegoWT's ORAS May): NEW May
                                                             in Emerald stays hers (copy_shared_new says why copies)

Frames on the sheet (370x254, figures on a clear background, alpha only 0 or 255 in the sprite areas): rows facing
down, up, left, right; per row walk (step, stand, step), run (step, stand, step), bike (3 frames: stand in the middle),
then down row: surf down, left, up, right; up row: four action frames (stand, hands in front, ball raised, ball raised
high); left row: the battle front; below the credit box: five back-throw frames on a 79-pixel grid (the same grid as
the Sapphire sheet's: left edges 27, 8, 0, 0, 0 from their grid columns; bottom edge row 248).
Black 2 frames the sheet has no picture for take its nearest frames, as on the Sapphire sheet: bike stills = the
bike's middle frames; action5 (turn) = the left and up standing frames; balance = the walking frames.
"""
import os, shutil, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
import sprites, mcss  # noqa: E402
import sprite_community as C  # noqa: E402

OVERLAY = 'emerald'
GEN5 = C.GEN5
SHOTS = C.SHOTS
NAME = 'brendan_e'
C.SHEETS[NAME] = dict(file='emerald/brendan_emerald_hyo-oppa.png', author='hyo-oppa', bg='alpha')
NEAR = 0                    # no colour merges (the author: "DO NOT EDIT!")
SOURCE = 'community: src/sprites/community/incoming/emerald/brendan_emerald_hyo-oppa.png by hyo-oppa (cut, placed, ' \
         'palette-indexed; no colour merged)'

def _row(xs, y0, y1):
    return [(x0, y0, x1, y1) for x0, x1 in xs]

# (x0, y0, x1, y1) of each figure (its exact bounding box), listed stand first as Black 2 orders a walking row
BE = {
    'walk': {'down': [(36, 2, 53, 28), (11, 1, 28, 29), (61, 1, 78, 29)],
             'up': [(36, 37, 53, 61), (11, 36, 28, 62), (61, 36, 78, 62)],
             'left': [(36, 70, 54, 93), (13, 69, 31, 93), (60, 69, 78, 92)],
             'right': [(35, 103, 53, 126), (11, 102, 29, 125), (58, 102, 76, 126)]},
    'run': {'down': [(122, 3, 139, 26), (97, 2, 117, 27), (144, 2, 164, 27)],
            'up': [(123, 37, 140, 60), (98, 35, 115, 61), (147, 35, 164, 61)],
            'left': [(121, 70, 139, 92), (97, 69, 115, 92), (146, 69, 164, 92)],
            'right': [(121, 103, 139, 125), (96, 102, 114, 125), (145, 102, 163, 125)]},
    'bike': {'down': [(211, 3, 228, 30), (185, 3, 202, 30), (237, 3, 254, 30)],
             'up': [(211, 36, 228, 62), (185, 36, 202, 62), (237, 36, 254, 62)],
             'left': [(209, 69, 229, 94), (183, 69, 203, 94), (235, 69, 256, 94)],
             'right': [(210, 101, 230, 126), (183, 101, 204, 126), (236, 101, 256, 126)]},
    'surf': {'down': [(269, 4, 286, 27)], 'left': [(292, 5, 310, 27)], 'up': [(316, 5, 333, 28)],
             'right': [(339, 5, 357, 27)]},
    'action': [(267, 35, 284, 59), (292, 36, 308, 59), (316, 32, 336, 59), (341, 32, 362, 60)],
    'front': (277, 68, 314, 136),
    'back': dict(grid_x0=-20, pitch=79, bottom=248, frames=[(7, 188, 55, 248), (67, 191, 126, 248),
                                                           (138, 189, 203, 248), (217, 190, 284, 248),
                                                           (296, 194, 363, 248)]),
}
DIRS = C.DIRS
NAMES = C.BRENDAN_NAMES

def plan():
    """{code: (name, [(RGBA frame, lost pixels, note)])} for codes 231-238 (Black 2's layouts, as brendan_plan)."""
    n = NAME
    walk = {d: C.place_group(n, BE['walk'][d]) for d in DIRS}
    run = {d: C.place_group(n, BE['run'][d]) for d in DIRS}
    bike = {d: C.place_group(n, BE['bike'][d]) for d in DIRS}
    def frames(g, note):
        return [(cv, lost, note) for cv, lost, _ in g]
    out = {}
    out[231] = ('walk-run', sum((frames(walk[d], f'walk {d}') for d in DIRS), []) +
                sum((frames(run[d], f'run {d}') for d in DIRS), []))
    out[232] = ('bike', sum((frames(bike[d], f'bike {d}') for d in DIRS), []) +
                [(bike[d][0][0], bike[d][0][1], f'bike still {d}: the middle frame') for d in DIRS])
    out[233] = ('surf', [(*C.place_group(n, BE['surf'][d], feet=28)[0][:2], f'surf {d}') for d in DIRS])
    def reg(rects, d, note, size=32):
        """frames registered by the head to the walking stand frame of direction d (sprite_community.brendan_plan)"""
        cv0, _, pos0 = walk[d][0]
        ref = C.crop(n, BE['walk'][d][0])
        off = (size - 32) // 2
        g = C.place_group(n, rects, size=size, ref=ref, ref_pos=(pos0[0] + off, pos0[1] + off))
        return [(cv, lost, note) for cv, lost, _ in g]
    act = BE['action']
    out[234] = ('item', reg([act[0], act[2]], 'down', 'item: stand, ball raised'))
    out[235] = ('action2', reg([act[0], act[1]], 'down', 'action2: stand, hands in front'))
    out[236] = ('action5', [(walk['left'][0][0], walk['left'][0][1], 'action5: left standing (no turning frames)')] * 2 +
                [(walk['up'][0][0], walk['up'][0][1], 'action5: up standing (no turning frames)')] * 3)
    out[237] = ('throw', reg([act[0], act[2], act[3], act[3]], 'down', 'throw: stand, ball raised, raised high x2'))
    bal = []
    for d in DIRS:
        bal += [(walk[d][i][0], walk[d][i][1], f'balance {d}: walking frame (none on the sheet)') for i in (0, 1, 0, 2)]
    out[238] = ('balance', bal)
    return out

def _colours(frames):
    """(exact 8-bit colours, distinct 5-bit (DS) colours)."""
    c = C.colours_of(frames)
    return len(c), len({tuple(v >> 3 for v in k) for k in c})

def front_rgba():
    return C.front_still(NAME, BE['front'])

def back_figures():
    """The three back poses (frames 0, 2, 3 of 5, as the Sapphire NEW back) on Nate's canvas (sprite_community)."""
    import sprite_upgrade_player_backs as PB
    e, tex, dpal, sp = PB.donor(0)
    saved = C.B.get('back')
    C.B['back'] = BE['back']
    real_crop = C.crop
    C.crop = lambda name, r: real_crop(NAME, r)
    try:
        return C.brendan_back_figures(sp, tex)
    finally:
        C.B['back'] = saved
        C.crop = real_crop

def analyze():
    lines, ok = [], {}
    def row(key, what, frames, lost=0):
        exact, ds = _colours(frames)
        good = exact <= 15 and not lost
        ok[key] = good
        lines.append(f"{'OK  ' if good else 'OVER'} {what}: {exact} colours" + (f' ({ds} distinct on the DS)' if ds != exact else '')
                     + (f', {lost} pixels outside the frame' if lost else ''))
    for code, (name, fr) in plan().items():
        row(code, f'Brendan {code} {name}', [f for f, _, _ in fr], sum(l for _, l, _ in fr))
    lines.append('     Brendan 239 fishing: no fishing frames on the sheet -> CLASSIC Emerald fishing')
    row('front', 'Brendan battle front (sheet, 37x68)', [front_rgba()])
    row('back', 'Brendan battle back (frames 1, 3, 4 of 5)', back_figures())
    return lines, ok

# ---------------------------------------------------------------------------------------------------- writing

def _index(frames):
    return C.index_frames(frames, near=NEAR)

def write_overworld(code, name, frames, note):
    don, meta = C._donor_frames(code)
    assert len(frames) == len(don) and frames[0].shape[:2] == don[0].shape[:2], (code, len(frames), len(don))
    idx, pal, merges, n = _index(frames)
    assert not merges
    kind_dir = os.path.join(GEN5, 'overworld', OVERLAY)
    folder = os.path.join(kind_dir, f'{code:03d}-{name}')
    C._replace_folder(kind_dir, code, folder)
    os.makedirs(folder, exist_ok=True)
    sprites.write_pal(os.path.join(folder, 'palette.pal'), pal)
    w, h = meta['size']
    for i, a in enumerate(idx):
        sprites.write_png(os.path.join(folder, f'frame_{i:02d}.png'), a.tobytes(), w, h, pal)
    sprites.write_json(os.path.join(folder, 'sprite.json'), dict(
        kind='overworld', code=code, sheet=meta['sheet'], frames=len(idx), size=meta['size'],
        controller=meta['controller'], textures=meta['textures'], palette=meta['palette'], name=name, note=note,
        source=SOURCE, colours=n, merged_colours=[], made_by='b2tools/sprite_community_emerald.py'))
    return folder

def copy_classic(kind, code, why):
    """A copy of the CLASSIC Emerald folder src/sprites/<kind>/emerald/<code>-* into the NEW overlay (the build lays
    src/sprites_gen5/<kind>/emerald/ over everything else, so the shared NEW folder of that number never shows)."""
    src_dir = os.path.join(ROOT, 'src', 'sprites', *kind.split('/'), OVERLAY)
    src = next(os.path.join(src_dir, d) for d in sorted(os.listdir(src_dir)) if d.split('-')[0] == f'{code:03d}')
    kind_dir = os.path.join(GEN5, *kind.split('/'), OVERLAY)
    folder = os.path.join(kind_dir, os.path.basename(src))
    C._replace_folder(kind_dir, code, folder)
    if os.path.isdir(folder):
        shutil.move(folder, os.path.join(os.path.expanduser('~/.Trash'), os.path.basename(folder) + '-old-' +
                                         __import__('time').strftime('%Y%m%d-%H%M%S')))
    shutil.copytree(src, folder)
    meta = sprites.read_json(os.path.join(folder, 'sprite.json'))
    meta['note'] = meta.get('note', '') + f' -- NEW set: CLASSIC art ({why})'
    sprites.write_json(os.path.join(folder, 'sprite.json'), meta)
    return folder

def copy_shared_new(code):
    """NEW May in Emerald = DiegoWT's ORAS May (src/sprites_gen5/overworld/240-248, shared): a copy of that folder in
    the NEW overlay. patches/sprites.py lays src/sprites/<version>/ over src/sprites_gen5/ (the order Ruby's team swaps
    need), so without these copies Emerald's CLASSIC May (src/sprites/overworld/emerald/240-248) would show in the NEW
    set; a {"copy_of"} folder cannot do it (the rival NPC codes 4-6, 137-161 copy 240-248, and copy_of does not chain)."""
    src_dir = os.path.join(GEN5, 'overworld')
    src = next(os.path.join(src_dir, d) for d in sorted(os.listdir(src_dir)) if d.split('-')[0] == f'{code:03d}')
    kind_dir = os.path.join(GEN5, 'overworld', OVERLAY)
    folder = os.path.join(kind_dir, os.path.basename(src))
    C._replace_folder(kind_dir, code, folder)
    if os.path.isdir(folder):
        shutil.move(folder, os.path.join(os.path.expanduser('~/.Trash'), os.path.basename(folder) + '-old-' +
                                         __import__('time').strftime('%Y%m%d-%H%M%S')))
    shutil.copytree(src, folder)
    meta = sprites.read_json(os.path.join(folder, 'sprite.json'))
    meta['note'] = meta.get('note', '') + ' -- Emerald NEW set: a copy of the shared NEW folder (DiegoWT\'s ORAS May)'
    sprites.write_json(os.path.join(folder, 'sprite.json'), meta)
    return folder

def write_front():
    """The sheet's front on Black 2 front 108's parts (sprite_community.write_front's way, NEAR = 0)."""
    import sprite_upgrade as U
    rgba = front_rgba()
    (still,), pal, merges, n = _index([rgba])
    layout = 108
    dparts, dstill, dpal, sp = U.tr_donor(layout)
    off = mcss.still_offset(sp, dparts, dstill)
    W, H = mcss.CANVAS
    ys, xs = np.nonzero(still)
    whole, partsm = mcss.coverage(sp, dparts)
    def lost(dx, dy):
        X_, Y_ = xs + off[0] + dx, ys + off[1] + dy
        ok = (X_ >= 0) & (X_ < W) & (Y_ >= 0) & (Y_ < H)
        return (int((~ok).sum() + (~whole[Y_[ok], X_[ok]]).sum()), int((~ok).sum() + (~partsm[Y_[ok], X_[ok]]).sum()))
    shifts = sorted(((dx, dy) for dx in range(-12, 13) for dy in range(-4, 3)), key=lambda d: abs(d[0]) + abs(d[1]))
    dx, dy = min(shifts, key=lambda d: lost(*d))
    fig = np.zeros((H, W), np.uint8)
    fig[ys + off[1] + dy, xs + off[0] + dx] = still[ys, xs]
    outline = int(np.argmin([sum(c) if i else 999 for i, c in enumerate(pal)]))
    parts, rep = mcss.distribute(sp, dparts, fig, outline)
    if rep['lost_in_whole'] or rep['lost_in_parts']:
        raise SystemExit(f'front: layout {layout} cannot show every pixel ({rep})')
    kind_dir = os.path.join(GEN5, 'trainer', 'front', OVERLAY)
    folder = os.path.join(kind_dir, '000-brendan')
    C._replace_folder(kind_dir, 0, folder)
    os.makedirs(folder, exist_ok=True)
    sprites.write_pal(os.path.join(folder, 'palette.pal'), pal)
    sprites.write_png(os.path.join(folder, 'parts.png'), parts.tobytes(), 256, 128, pal)
    sprites.write_png(os.path.join(folder, 'static.png'), still.tobytes(), 80, 80, pal)
    sprites.write_json(os.path.join(folder, 'sprite.json'), dict(
        kind='trainer', side='front', sprite=0, archive=sprites.ARC_TR['front'], files=sprites.tr_files(0),
        name='brendan', note='Brendan (rival battles, Hall of Fame), Emerald outfit', source=SOURCE,
        layout=f'parts and animations of Black 2 front sprite {layout}', colours=n, merged_colours=[], mcss_from=layout,
        made_by='b2tools/sprite_community_emerald.py'))
    return folder, dict(rep, shift=(dx, dy), colours=n)

def write_back():
    """sprite_community.write_brendan_back with the Emerald sheet's frames, into the emerald/ overlay (NEAR = 0)."""
    import sprite_upgrade_player_backs as P
    slot = 0
    e, tex, dpal, sp = P.donor(slot)
    figs = back_figures()
    idx, pal, merges, n = _index(figs)
    assert not merges
    O = mcss.ORIGIN
    new = np.zeros_like(tex)
    edits, lost = [], 0
    for (k, cells, nodes), fig in zip(C.BACK_POSES, idx):
        qs = {ci: P.quad(sp, ci) for ci in cells}
        corners = P.place(fig, [(qs[ci][2] - qs[ci][0], qs[ci][3] - qs[ci][1]) for ci in cells])
        own = np.zeros(fig.shape, bool)
        node_xy = {}
        for ci, (cx, cy) in zip(cells, corners):
            qx0, qy0, _, _ = qs[ci]
            nx, ny = cx - O[0] - qx0, cy - O[1] - qy0
            node_xy[ci] = (nx, ny)
            X_, Y_, Uu, V = mcss.cell_pixels(sp.cells[ci], (0, 1, 1, nx, ny))
            X_ = X_ + O[0]; Y_ = Y_ + O[1]
            ok = (X_ >= 0) & (X_ < fig.shape[1]) & (Y_ >= 0) & (Y_ < fig.shape[0])
            mine = np.zeros(len(X_), bool)
            mine[ok] = ~own[Y_[ok], X_[ok]]
            val = np.zeros(len(X_), np.uint8)
            val[mine] = fig[Y_[mine], X_[mine]]
            new[V, Uu] = val
            own[Y_[mine], X_[mine]] = True
        lost += int(((fig != 0) & ~own).sum())
        for mc, node, ci in nodes:
            if ci is None:
                edits.append(dict(mc=mc, node=node, seq=C.BACK_BLANK_SEQ))
            else:
                edits.append(dict(mc=mc, node=node, seq=P.seq_of(sp, ci), x=int(node_xy[ci][0]), y=int(node_xy[ci][1])))
    for ci in C.BACK_CLEAR:
        for (x, y, w, h, u, v, hf, vf) in sp.cells[ci]:
            new[v:v + h, u:u + w] = 0
    if lost:
        raise SystemExit(f'back: {lost} pixels outside every cell')
    kind_dir = os.path.join(GEN5, 'trainer', 'back', OVERLAY)
    folder = os.path.join(kind_dir, f'{slot:03d}-brendan')
    C._replace_folder(kind_dir, slot, folder)
    os.makedirs(folder, exist_ok=True)
    _, _, still = sprites.tr_decode_image(e[8 * slot], 'static')
    sprites.write_pal(os.path.join(folder, 'palette.pal'), pal)
    sprites.write_png(os.path.join(folder, 'parts.png'), new.tobytes(), 256, 128, pal)
    sprites.write_png(os.path.join(folder, 'static.png'), bytes(still), 80, 80, pal)
    sprites.write_json(os.path.join(folder, 'sprite.json'), dict(
        kind='trainer', side='back', sprite=slot, archive=sprites.ARC_TR['back'], files=sprites.tr_files(slot),
        name='brendan', note='Brendan (player back), Emerald outfit', source=SOURCE + ' (back frames 1, 3, 4 of 5)',
        layout='cells, quads and throw timing of Black 2 back sprite 0; whole-figure poses', colours=n,
        merged_colours=[], node_edits=edits, still_multicells=[2, 3, 4], made_by='b2tools/sprite_community_emerald.py'))
    e2 = list(e)
    e2[8 * slot + 4] = mcss.set_nodes(e[8 * slot + 4], edits)
    e2[8 * slot + 5] = mcss.still_translations(e[8 * slot + 5], 1, [2, 3, 4])
    return folder, (mcss.Sprite(e2, 8 * slot), new, pal)

# Overworld result (analyze, 2026-10-11): as drawn, the sheet uses near-identical colours side by side (four blacks
# (0,0,0) (3,3,3) (3,3,5) (4,4,6); reds (189,57,57) and (193,57,57); skins (254,214,189) (248,208,184) ...: 36 colours
# in its sprite areas, 21 on the DS). Exactly as drawn, only action2 (235) fits Black 2's 15 colours; with the DS's own
# 5-bit colours (two 8-bit colours the DS shows as one) 232-238 fit, and walk-run (231) still has 17 and would need two
# real merges ((97,97,103) 62 px -> (99,99,107); (56,64,64) 2 px -> (64,64,64)). The overworld sheets go together (one
# player, nine animations), so with any of them over the limit all nine stay CLASSIC. The user decides (report):
#   ALLOW_DS_ROUNDING   colours the DS cannot tell apart share one palette entry (no pixel changes on screen)
#   ALLOW_MERGES        {code: {from rgb: to rgb}} real merges the author or the user approved
ALLOW_DS_ROUNDING = True     # user 2026-10-13: merge the colours (Emerald NEW Brendan walks in hyo-oppa's art)
ALLOW_MERGES = {231: {(97, 97, 103): (99, 99, 107), (56, 64, 64): (64, 64, 64)}}   # walk-run: the two closest real merges

def _apply(frames, code):
    out = []
    for f in frames:
        f = f.copy()
        if ALLOW_DS_ROUNDING:
            c = C.colours_of(frames)
            best = {}
            for k, v in c.items():
                ds = tuple(x >> 3 for x in k)
                if ds not in best or v > c[best[ds]]: best[ds] = k
            ys, xs = np.nonzero(f[..., 3])
            for y, x in zip(ys, xs):
                f[y, x, :3] = best[tuple(int(v) >> 3 for v in f[y, x, :3])]
        for a, b in ALLOW_MERGES.get(code, {}).items():
            sel = np.all(f[..., :3] == a, -1) & (f[..., 3] > 0)
            f[sel, :3] = b
        out.append(f)
    return out

def build():
    lines, ok = analyze()
    done = []
    p = plan()
    ow_new = all(ok[c] for c in p) or ALLOW_DS_ROUNDING or ALLOW_MERGES
    for code, (name, fr) in p.items():
        if ow_new:
            frames = _apply([f for f, _, _ in fr], code)
            assert _colours(frames)[0] <= 15, (code, _colours(frames))
            done.append(write_overworld(code, f'brendan-{name}', frames,
                                        f'Brendan (player, Emerald outfit), {name}: ' +
                                        '; '.join(dict.fromkeys(t for _, _, t in fr))))
        else:
            done.append(copy_classic('overworld', code, 'the hyo-oppa overworld sheets need more than Black 2\'s 15 '
                                     'colours as drawn (sprite_community_emerald.py analyze)'))
    done.append(copy_classic('overworld', 239, 'no fishing frames on the hyo-oppa sheet'))
    for code in range(240, 249):
        done.append(copy_shared_new(code))
    if ok['front']:
        done.append(write_front()[0])
    else:
        done.append(copy_classic('trainer/front', 0, 'the hyo-oppa front is over Black 2\'s limits'))
    if ok['back']:
        done.append(write_back()[0])
    else:
        done.append('back over the limits: CLASSIC needed (a CLASSIC back copied here would be lifted by GEN5_BACK_LIFT)')
    return lines, [os.path.relpath(d, ROOT) if os.path.isabs(d) else d for d in done]

# ---------------------------------------------------------------------------------------------------- review

def review(path=None):
    """screenshots/sprites/emerald_new_review.png: the hyo-oppa frames as cut and placed on Black 2's layouts (not
    installed where over the limits: their colour counts), what the NEW set installs, the battle front's intro and the
    back's throw, the Sapphire-outfit NEW Brendan for comparison."""
    import sprite_upgrade as U
    import sprite_emerald as SE
    from PIL import Image
    lines, ok = analyze()
    sections = []
    for code, (name, fr) in plan().items():
        frames = [f for f, _, _ in fr]
        exact, ds = _colours(frames)
        inst = os.path.join(GEN5, 'overworld', OVERLAY, f'{code:03d}-brendan-{name}')
        ifr = SE._folder_frames(inst)
        _, ipal = SE._pal_png(os.path.join(inst, 'frame_00.png'))
        sfold = os.path.join(GEN5, 'overworld', f'{code:03d}-brendan-{name}')
        sfr = SE._folder_frames(sfold)
        _, spal = SE._pal_png(os.path.join(sfold, 'frame_00.png'))
        sections.append((f'Brendan {name} ({code}): hyo-oppa {exact} colours ({ds} on the DS) -> '
                         f'{"NEW" if ok[code] else "over 15: CLASSIC installed"}', [
            ('hyo-oppa, cut + placed', SE._strip([Image.fromarray(f) for f in frames], 3)),
            ('installed (NEW, Emerald)', SE._strip([U.rgba(f, ipal) for f in ifr], 3)),
            ('NEW Sapphire (hyo-oppa)', SE._strip([U.rgba(f, spal) for f in sfr], 3))]))
    fold = os.path.join(GEN5, 'trainer', 'front', OVERLAY, '000-brendan')
    parts, pal = SE._pal_png(os.path.join(fold, 'parts.png'))
    still, _ = SE._pal_png(os.path.join(fold, 'static.png'))
    _, _, _, sp = U.tr_donor(108)
    T = sp.length(0)
    fr = U.anim_frames(sp, parts, pal, [0, T // 4, T // 2, 3 * T // 4])
    sfold = os.path.join(GEN5, 'trainer', 'front', '000-brendan')
    sst, spal = SE._pal_png(os.path.join(sfold, 'static.png'))
    sections.append(('Brendan battle front 0 (on front 108\'s parts): still, intro gesture', [
        ('hyo-oppa sheet', SE._strip([Image.fromarray(front_rgba())], 2)),
        ('installed (still, intro)', SE._strip([U.rgba(still, pal)] + fr[:4], 2)),
        ('NEW Sapphire (still)', SE._strip([U.rgba(sst, spal)], 2))]))
    ticks = [(0, 0), (1, 10), (1, 25), (1, 36), (1, 45), (1, 99)]
    def bframe(spr, t_, p_, an, t):
        im = U.rgba(mcss.render(spr, t_, an, t), p_)
        return im.crop((24, 0, im.width - 24, mcss.ORIGIN[1]))
    sp2, new, bpal = _back_sprite()
    sb = os.path.join(GEN5, 'trainer', 'back', '000-brendan')
    old, op = SE._pal_png(os.path.join(sb, 'parts.png'))
    meta = sprites.read_json(os.path.join(sb, 'sprite.json'))
    import sprite_upgrade_player_backs as P
    e, tex, dpal, sp = P.donor(0)
    e2 = list(e)
    e2[4] = mcss.set_nodes(e[4], meta['node_edits'])
    e2[5] = mcss.still_translations(e[5], 1, [2, 3, 4])
    sections.append(('Brendan battle back 0 (Nate\'s cells; the build lifts NEW backs by GEN5_BACK_LIFT): animation 0, '
                     'the throw at ticks ' + ', '.join(str(t) for _, t in ticks[1:]), [
        ('hyo-oppa sheet, frames 1-5', SE._strip([Image.fromarray(C.crop(NAME, r)) for r in BE['back']['frames']], 1)),
        ('installed (NEW, Emerald)', SE._strip([bframe(sp2, new, bpal, an, t) for an, t in ticks], 1)),
        ('NEW Sapphire (hyo-oppa)', SE._strip([bframe(mcss.Sprite(e2, 0), old, op, an, t) for an, t in ticks], 1))]))
    return SE._sheet(sections, 'Pokemon Emerald NDS, NEW set: Brendan\'s Emerald outfit by hyo-oppa (cut, placed, '
                     'indexed; no colour merged) - b2tools/sprite_community_emerald.py',
                     path or os.path.join(SHOTS, 'emerald_new_review.png'))

def _back_sprite():
    """(sprite with the installed node edits, parts, palette) of the installed NEW Emerald back."""
    import sprite_emerald as SE
    import sprite_upgrade_player_backs as P
    fold = os.path.join(GEN5, 'trainer', 'back', OVERLAY, '000-brendan')
    new, pal = SE._pal_png(os.path.join(fold, 'parts.png'))
    meta = sprites.read_json(os.path.join(fold, 'sprite.json'))
    e, tex, dpal, sp = P.donor(0)
    e2 = list(e)
    e2[4] = mcss.set_nodes(e[4], meta['node_edits'])
    e2[5] = mcss.still_translations(e[5], 1, [2, 3, 4])
    return mcss.Sprite(e2, 0), new, pal

if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else ''
    if cmd == 'analyze':
        print('\n'.join(analyze()[0]))
    elif cmd == 'build':
        lines, done = build()
        print('\n'.join(lines)); print('\n'.join(done))
    elif cmd == 'review':
        print(review())
    else:
        print(__doc__)
