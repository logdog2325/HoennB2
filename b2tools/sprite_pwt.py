"""The PWT overworld sheets Hoenn uses (Gym Leaders, Steven, Wallace): their missing frames drawn.

Black 2 draws the Hoenn Gym Leaders, Steven and Wallace only for the PWT, where they stand still facing the camera or
sideways, so their sheets hold placeholder "X" images for the back view and for walking toward / away from the camera
(notes/RESEARCH_STORY_SPRITES.md 5.1): frames 0, 1, 3 of the 7-frame sheets (controller type 2: up, up step, down,
down step, left + 2 steps; the game mirrors the step for the other foot and left for right) and 0-2, 4, 5 of the
12-frame sheets (type 3: up, down, left, right x stand + 2 steps). Used as Hoenn NPCs they showed the X when seen from
above or walking away (user report, Story Ch2: Steven).

    python3 sprite_pwt.py [code ...]     default: every sheet below; writes src/sprites/overworld/<code>-<name>/
    python3 sprite_pwt.py review         screenshots/sprites/pwt_frames_review.png (Black 2 sheet / filled sheet)
    python3 sprite_pwt.py 276            Juan, Emerald only: src/sprites/overworld/emerald/276-juan/ ('overlay')

How the frames are made (from the sheet's own front and side frames, Black 2's conventions read off its NPC sheets
such as 104 Cedric Juniper and 251 Mom):
- back view: the front stand frame with the face turned into the back of the head (each face pixel takes the hair
  colour above it, so the bangs' strands run on down; the lowest hair row one tone darker) and the front of the
  clothes into their back (per-character colour maps: ties, shirts, buttons, zips become the jacket); then a few
  hand-placed pixels per character (PATCH) for what only shows from behind (Roxanne's bows, Wattson's bald crown...);
- walking toward / away from the camera: Black 2's step = the body one pixel higher, the leading leg two pixels
  longer (its thigh row repeated) and the other leg raised behind it (a two-row stub); step 1 leads with the screen
  left leg, step 2 (12-frame sheets) with the right one.
The front and side frames are not touched. Same frame count, size and palette as Black 2's sheet (in place).
"""
import os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sprites  # noqa: E402
import sprite_upgrade as U  # noqa: E402
import sprite_upgrade_players as PL  # noqa: E402

# frame roles per controller type
LAYOUT = {2: dict(back=0, back_steps=(1,), front=2, front_steps=(3,)),
          3: dict(back=0, back_steps=(1, 2), front=3, front_steps=(4, 5))}

# Per sheet:
#   face: (x0, y0, x1, y1) box of the front frame whose non-hair pixels become hair (inclusive)
#   hair: hair colours, dark -> light; skin: colours replaced inside the face box (outline pixels there that sit
#         between hair pixels go too)
#   body: (x0, y0, x1, y1, {colour: colour}) recolours for the back of the clothes
#   hip: first row of the legs; legs: (x0, x1) their columns (pixels outside stay with the body)
#   patch_back: [(x, y, rows)] hand-placed pixels on the back view ('.' keep, '_' clear, hex = colour)
SHEETS = {
    287: dict(name='steven', tones=(3, 2, 1), face=(8, 9, 23, 18), hair=[1, 2, 3, 4], skin=[0xA, 0xB, 0xC, 0xD, 0xE],
              body=(8, 19, 23, 28, {0x8: 0x7, 0x9: 0x7, 0xE: 0x6, 0xA: 0x6}), hip=26, legs=(11, 20)),
    272: dict(name='norman', tones=(8, 7, 7), face=(8, 9, 23, 18), hair=[7, 8, 4], skin=[0x9, 0xA, 0xB, 0xC, 0xD, 0x3],
              body=(8, 19, 23, 26, {0x2: 0x6, 0x3: 0x6, 0x8: 0x6}), hip=27, legs=(10, 21)),
    268: dict(name='roxanne', tones=(3, 2, 1), outline=0xD, face=(8, 10, 23, 19), hair=[1, 2, 3, 4], skin=[0xA, 0xB, 0xC, 0xF, 0x8, 0x9],
              body=(7, 20, 24, 28, {0x7: 0x5, 0xE: 0x6, 0xF: 0x6}), hip=28, legs=(12, 19)),
    269: dict(name='brawly', tones=(7, 6, 5), face=(8, 9, 23, 18), hair=[5, 6, 7, 8], skin=[0x9, 0xA, 0xB, 0xC],
              body=(8, 19, 23, 27, {0x4: 0x2, 0x3: 0x2}), hip=27, legs=(10, 21)),
    270: dict(name='wattson', tones=(0xD, 0xC, 0xB), outline=0xE, face=(8, 8, 23, 18), hair=[7, 8, 0xF], skin=[0xB, 0xC, 0xD, 0xA],
              body=(10, 19, 21, 25, {0x6: 0x3, 0x7: 0x3, 0x8: 0x3, 0x4: 0x3}), hip=27, legs=(8, 23),
              # bald crown, the white hair that the side view shows over the back of his head, the neck
              patch_back=[(7, 8, ['...1CD8FFFF8DC1...',
                                  '..1CDD8FFFF8DDC1..',
                                  '..1CD8FFFFFF8DC1..',
                                  '.ECD8FFFFFFFF8DCE.',
                                  'AC8FFFFFFFFFFFF8CA',
                                  'EC8FFF8FFFF8FFF8CE',
                                  'EB8FF8FFFFFF8FF8BE',
                                  '.E78F8FFFFFF8F87E.',
                                  '..6788F8FF8F8876..',
                                  '.6778888888888776.',
                                  '.6677777777777766.',
                                  '..E3366BBBB6633E..'])]),
    273: dict(name='winona', tones=(6, 5, 1), face=(9, 12, 22, 18), hair=[1, 5, 6, 7], skin=[0xA, 0xB, 0xC, 0xD],
              body=(8, 19, 23, 28, {0x8: 0x6, 0x9: 0x5}), hip=25, legs=(11, 20),
              # her cap covers the back of her head; her two long lavender locks hang down her back (side view)
              patch_back=[(12, 14, ['6']), (19, 14, ['6']),
                          (10, 18, ['F4F......F4F',
                                    '243......342',
                                    '243......342',
                                    'F43......34F',
                                    '.F43....34F.',
                                    '.F43....34F.',
                                    '.F4F....F4F.',
                                    '..F......F..'])]),
    271: dict(name='flannery', tones=(3, 2, 1), face=(9, 10, 22, 18), hair=[1, 2, 3, 4], skin=[0xA, 0xB, 0xC, 0xD, 0x6],
              body=(8, 19, 23, 25, {0x8: 0x7, 0xB: 0x7, 0xA: 0x7, 0x4: 0x7}), hip=27, legs=(11, 20)),
    274: dict(name='tate', tones=(8, 7, 6), hi=9, keep=0, face=(9, 9, 22, 18), hair=[6, 7, 8, 9], skin=[0xA, 0xB, 0xC, 0xD, 0xE],
              body=(8, 20, 23, 27, {0x4: 0x1, 0x5: 0x2}), hip=27, legs=(11, 20)),
    275: dict(name='liza', tones=(8, 7, 6), hi=9, keep=0, face=(9, 9, 22, 18), hair=[6, 7, 8, 9], skin=[0xA, 0xB, 0xC, 0xD, 0xE],
              body=(8, 20, 23, 27, {0x4: 0x1, 0x5: 0x2}), hip=27, legs=(11, 20)),
    288: dict(stretch=1, name='wallace', tones=(7, 6, 5), face=(8, 8, 24, 19), hair=[5, 4, 6, 7, 8], skin=[0x9, 0xA, 0xB, 0x2, 0x3],
              body=(7, 20, 24, 28, {0x9: 0xC, 0xA: 0xC}), hip=29, legs=(10, 21),
              # the back of his hat's brim, his hair under it (shadowed below the brim), his collar
              patch_back=[(7, 8, ['1CCCDDDDEDDDDDEDD1',
                                  '1EDDDDEEDDDDDDEE11',
                                  '.11EEEEEEEEEEEE11.',
                                  '.F56666666666665F.',
                                  'F5677777777777765F',
                                  'F5678888888888765F',
                                  'F5677777887777765F',
                                  '556777777777777655',
                                  '566677777777776665',
                                  '56_566666666665_65',
                                  '56_1D55555555D1_65',
                                  '_5_FECCCCCCCCEF_5_'])]),
    # Juan (Emerald NDS only, user decision 2026-10-12, emerald_integrate): his dark hair (1, 2) shows from behind and in the
    # side frames under the white streak, which stays on top; the coat's white front and purple cravat become blue
    276: dict(name='juan', overlay='emerald', tones=(2, 1, 1), face=(9, 10, 22, 16), hair=[1, 2, 0xA, 3, 0xE],
              skin=[0xD, 0xC, 0xB, 0x8], body=(10, 17, 21, 26, {0xE: 0x9, 0x6: 0x8, 0x5: 0x8, 0x2: 0x8, 0x3: 0x9}),
              hip=27, legs=(11, 20)),
}


def placeholder(frame, x_mask):
    return frame.shape == x_mask.shape and ((frame != 0) == x_mask).all()


def x_mask():
    return PL.U_donor(287)[0][0] != 0


def darker(c, ramp):
    return ramp[max(0, ramp.index(c) - 1)] if c in ramp else c


def back_view(front, spec):
    out = front.copy()
    x0, y0, x1, y1 = spec['face']
    hair, skin = spec['hair'], set(spec['skin'])
    OL = spec.get('outline', 15)
    mid, dark, low = spec['tones']
    keep = spec.get('keep', 2)                             # rows of the box that keep the bangs' own strands
    box = np.zeros(out.shape, bool); box[y0:y1 + 1, x0:x1 + 1] = True
    face = box & np.isin(out, list(skin))
    # outline pixels inside the face (eyes, brows, mouth) that sit between face / hair pixels
    for _ in range(2):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                if out[y, x] == OL and not face[y, x]:
                    ud = (face[y - 1, x] or out[y - 1, x] in hair) and (face[y + 1, x] or out[y + 1, x] in hair)
                    lr = (face[y, x - 1] or out[y, x - 1] in hair) and (face[y, x + 1] or out[y, x + 1] in hair)
                    if (ud and face[y - 1:y + 2, x].any()) or (lr and face[y, x - 1:x + 2].any()):
                        face[y, x] = True
    region = face | (box & np.isin(out, hair))             # the back of the head: one hair mass
    for x in range(x0, x1 + 1):
        ys = np.nonzero(region[:, x])[0]
        if not len(ys):
            continue
        last = mid
        for y in range(ys.min(), ys.max() + 1):
            if not region[y, x]:
                continue
            if y < y0 + keep:                              # top rows: continue the strands above
                if face[y, x]:
                    out[y, x] = last if last in hair else mid
                if out[y, x] == hair[0]:                   # strand tips (darkest tone) would read as dots
                    out[y, x] = mid
                last = out[y, x]
            else:
                out[y, x] = mid
                if y == y0 + keep and spec.get('hi') and abs(x - (x0 + x1) / 2) <= (x1 - x0) / 4:
                    out[y, x] = spec['hi']                 # a light patch under the crown
        bottom = [y for y in ys if region[y, x]]
        if spec.get('shade', True) and len(bottom) > 3:
            out[bottom[-1], x] = low
            if len(bottom) > 5:
                out[bottom[-2], x] = dark
    bx0, by0, bx1, by1, cmap = spec['body']
    for y in range(by0, by1 + 1):
        for x in range(bx0, bx1 + 1):
            out[y, x] = cmap.get(int(out[y, x]), out[y, x])
    for px, py, rows in spec.get('patch_back', []):
        paint(out, px, py, rows)
    return out


def paint(a, px, py, rows):
    assert len({len(r) for r in rows}) == 1, f'patch at ({px}, {py}): rows of different lengths'
    for j, row in enumerate(rows):
        for i, ch in enumerate(row):
            if ch == '.':
                continue
            a[py + j, px + i] = 0 if ch == '_' else int(ch, 16)


def step(stand, spec, lead):
    """Black 2's walking step toward / away from the camera, from a stand frame (lead 'L' or 'R': the long leg)."""
    hip, (lx0, lx1) = spec['hip'], spec['legs']
    H, W = stand.shape
    out = np.zeros_like(stand)
    legs = np.zeros(stand.shape, bool); legs[hip:, lx0:lx1 + 1] = True
    upper = np.where(legs, 0, stand)
    out[:-1] = upper[1:]                                   # the body one pixel higher
    cx = (lx0 + lx1 + 1) // 2
    strip = stand[hip:, lx0:lx1 + 1]
    rows = [r for r in range(strip.shape[0]) if strip[r].any()]
    strip = strip[:rows[-1] + 1]
    left, right = strip.copy(), strip.copy()
    left[:, cx - lx0:] = 0; right[:, :cx - lx0] = 0
    long_, short = (left, right) if lead == 'L' else (right, left)
    n = spec.get('stretch', 2)
    longer = np.concatenate([long_[:1]] * n + [long_], 0)              # thigh row repeated: two pixels longer
    y = hip - 1
    for r in range(longer.shape[0]):
        if y + r >= H:
            break
        row = longer[r]
        m = row != 0
        out[y + r, lx0:lx1 + 1][m] = row[m]
    stub = short[:1].copy()                                # the raised leg: its top row, closed below by outline
    m = stub[0] != 0
    tgt = out[y, lx0:lx1 + 1]
    tgt[m & (tgt == 0)] = stub[0][m & (tgt == 0)]
    below = out[y + 1, lx0:lx1 + 1]
    below[m & (below == 0)] = spec.get('outline', 15)
    return out


def sheet(code):
    spec = SHEETS[code]
    frames, pal, meta = PL.U_donor(code)
    frames = [f.copy() for f in frames]
    lay = LAYOUT[meta['controller']]
    X = x_mask()
    missing = [i for i, f in enumerate(frames) if placeholder(f, X)]
    front = frames[lay['front']]
    back = back_view(front, spec)
    new = {lay['back']: back}
    for i, lead in zip(lay['front_steps'], 'LR'):
        new[i] = step(front, spec, lead)
    for i, lead in zip(lay['back_steps'], 'LR'):
        new[i] = step(back, spec, lead)
    assert sorted(new) == missing, (code, sorted(new), missing)
    for i, f in new.items():
        frames[i] = f
    return frames, pal, meta, missing


def write(code):
    spec = SHEETS[code]
    frames, pal, meta, missing = sheet(code)
    note = f'{spec["name"].title()} (Black 2 PWT sheet; frames {missing} drawn: back view, walking)'
    source = (f'Black 2 a/0/4/8 sheet {meta["sheet"]} (code {code}); the missing frames from its own front and side '
              'frames')
    if spec.get('overlay'):         # one version's art only (src/sprites/overworld/<version>/: Emerald's Juan, whom Sapphire
        folder = write_overlay(code, spec, frames, pal, meta, note, source)   # and Ruby show only standing in the PWT)
    else:
        folder = PL.write_sheet(code, spec['name'], frames, pal, note, source)
    path = os.path.join(folder, 'sprite.json')
    sprites.write_json(path, dict(sprites.read_json(path), made_by='b2tools/sprite_pwt.py', drawn_frames=missing))
    return folder


def write_overlay(code, spec, frames, pal, meta, note, source):
    """PL.write_sheet into the version overlay src/sprites/overworld/<overlay>/<code>-<name>/ (patches/sprites.py
    installs it in that version's builds only; the shared folder, Black 2's own sheet here, is left alone)."""
    kind_dir = os.path.join(U.SRC, 'overworld', spec['overlay'])
    folder = os.path.join(kind_dir, f'{code:03d}-{spec["name"]}')
    U._replace_folder(kind_dir, code, folder)
    os.makedirs(folder, exist_ok=True)
    sprites.write_pal(os.path.join(folder, 'palette.pal'), pal)
    w, h = meta['size']
    for i, f in enumerate(frames):
        sprites.write_png(os.path.join(folder, f'frame_{i:02d}.png'), f.tobytes(), w, h, pal)
    sprites.write_json(os.path.join(folder, 'sprite.json'), dict(meta, name=spec['name'], note=note, source=source,
                                                                   version=spec['overlay']))
    return folder


def review(path=None, codes=None):
    from PIL import Image, ImageDraw
    codes = codes or list(SHEETS)
    rows = []
    for code in codes:
        before, pal, meta = PL.U_donor(code)
        after, _, _, missing = sheet(code)
        sc = 3
        def strip(fr, mark=()):
            W = len(fr) * (32 * sc + 4)
            im = Image.new('RGBA', (W, 32 * sc + 4), (0, 0, 0, 0))
            for k, f in enumerate(fr):
                im.alpha_composite(U.rgba(f, pal).resize((32 * sc, 32 * sc), Image.NEAREST), (k * (32 * sc + 4), 2))
                if k in mark:
                    ImageDraw.Draw(im).rectangle([k * (32 * sc + 4), 0, k * (32 * sc + 4) + 32 * sc + 3, 32 * sc + 3],
                                                 outline=(255, 220, 90, 255))
            return im
        rows.append((f'{SHEETS[code]["name"].title()} ({code}, {len(before)} frames): Black 2', strip(before)))
        rows.append(('filled (new frames framed)', strip(after, missing)))
    W = max(im.width for _, im in rows) + 20
    Hh = sum(im.height + 18 for _, im in rows) + 10
    out = Image.new('RGBA', (W, Hh), (88, 112, 128, 255)); d = ImageDraw.Draw(out); y = 6
    for label, im in rows:
        d.text((10, y), label, fill=(255, 255, 255, 255)); y += 14
        out.alpha_composite(im, (10, y)); y += im.height + 4
    path = path or os.path.join(U.SHOTS, 'pwt_frames_review.png')
    out.save(path)
    return path


if __name__ == '__main__':
    args = sys.argv[1:]
    if args[:1] == ['review']:
        print('review ->', review(*args[1:2]))
    else:
        for c in ([int(a) for a in args] or list(SHEETS)):
            print(c, '->', os.path.relpath(write(c), U.ROOT))
