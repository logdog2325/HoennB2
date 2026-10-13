"""Sapphire's unique NPCs as Gen 5 overworld / battle sprites (DECISIONS 2026-10-06: "character sprites from
Sapphire's own art", touched up "to the point where they look like actual Gen 5 sprites from Black 2 and White 2").
Not the other sprite agents' characters (Brendan/May/Birch: sprite_players.py; Aqua/Magma, Wally, Elite Four:
sprite_upgrade.py). Characters, slots and stand-ins: data/sprite_map.json (review screenshots/sprites/
unique_upgrade_review.png):
    Mom 251 (+357), Gabby 331, Ty 340, contest reporter 341, Contest Judge 343, Teala 79, hot-springs old woman 332,
    rooftop sale woman 339, Mauville old man: Bard 328, Hipster 329, Trader 334, Storyteller 335, Giddy 336;
    battle: Gabby & Ty (Interviewer) front sprite 22.
Overworld sheets are drawn by hand from each character's Sapphire sprite (same design and colours) at Black 2's
proportions (figure rows 3-30, ~18 px wide; walk steps one pixel higher with Black 2's leg/arm poses), with Black 2's
conventions: Black 2's overworld skin ramp, two-pixel eyes, black outlines on clothes and the material's own dark tone
around skin and hair ("outlines:" in the drawn file, material_outlines, as sprite_upgrade.py's colour_outlines).
The battle picture is Sapphire's pic touched up with sprite_upgrade.py's battle steps (Gen 5 proportions, outlines,
Black 2's battle skin ramp) and stored as pixels in its drawn file.

    python3 sprite_unique.py [name ...]        build src/sprites/drawn/<name>.txt -> src/sprites/overworld/<code>-<name>/
                                                (or src/sprites/trainer/front/<n>-<name>/), default: all
    python3 sprite_unique.py review            screenshots/sprites/unique_upgrade_review.png (Sapphire / stand-in / new)
    python3 sprite_unique.py draft CODE SYM    print a donor sheet as text with a symbol map (start of a drawing)

Drawn source format (src/sprites/drawn/<name>.txt), one file per sheet:
    name: <folder name>          code: <object code> | trainer: <front sprite>      sapphire: <pokeruby pic> <pal>
    standin: <old Black 2 code>  note: <one line>     [variants: <name> <code> <palette name> ...]
    [include: <other drawn file>: its palettes, parts and frames, unless this file redefines them]
    [outlines: <members>><outline>[<<last row>] ...: Black 2's outline colours, applied when the sheet is built:
     black outline pixels around only skin (or only hair) take that material's dark tone (material_outlines)]
    palette [<name>]             then 16 lines "<symbol> r g b": the first is index 0 (clear), the last index 15
    frame <label>                then the rows of that frame (32 x 32 overworld, 80 x 80 battle); '.' = clear
Frame labels by sheet layout (spriteControllerType in a/0/4/7):
    12 frames (type 3): up up1 up2 down down1 down2 left left1 left2 [right right1 right2 = mirrors of left if absent]
     7 frames (type 2): up up1 down down1 left left1 left2           (the engine mirrors left for right)
    13 frames (357, Mom with the phone): the 7 above, then phone0 phone1 look0 look1 look2 look3
A frame line "frame X = mirror Y" / "= shift Y dy" / "= same Y" reuses another frame, and
"frame X = stack R:part[:dx] ..." builds it from "part <name>" blocks (any number of rows): each part's rows are
laid from row R (shifted dx columns), later parts drawn over earlier ones ('.' leaves what is below, '_' clears);
a frame's name in place of a part lays that whole frame.
"""
import os, re, sys, json
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
import sprites  # noqa: E402
from b2files import arc_path, narc_entries  # noqa: E402

SRC = os.path.join(ROOT, 'src', 'sprites')
DRAWN = os.path.join(SRC, 'drawn')
SHOTS = os.path.join(ROOT, 'screenshots', 'sprites')
FILES = sprites.SRC_FILES
PR = os.path.join(ROOT, 'external', 'pokeruby', 'graphics')

LAYOUTS = {12: ['up', 'up1', 'up2', 'down', 'down1', 'down2', 'left', 'left1', 'left2', 'right', 'right1', 'right2'],
           7: ['up', 'up1', 'down', 'down1', 'left', 'left1', 'left2'],
           13: ['up', 'up1', 'down', 'down1', 'left', 'left1', 'left2', 'phone0', 'phone1', 'look0', 'look1', 'look2',
                'look3']}

# ---------------------------------------------------------------------------------------------------- source files

def parse(path):
    """-> dict(meta..., palettes {name: [(sym, rgb)] * 16}, frames {label: list of row strings or ('ref', ...)})."""
    meta = {'palettes': {}, 'frames': {}, 'order': [], 'parts': {}}
    cur = None; pal = None; target = None
    for raw in open(path):
        line = raw.rstrip('\n')
        if line.startswith('#') or (not line.strip() and cur is None):
            continue
        m = re.match(r'part\s+(\S+)\s*$', line)
        if m:
            pal = None; cur = m.group(1); target = meta['parts']; target[cur] = []; continue
        m = re.match(r'(name|code|trainer|sapphire|standin|note|variants|size|include|outlines):\s*(.*)$', line)
        if m and cur is None and pal is None:
            meta[m.group(1)] = m.group(2).strip(); continue
        m = re.match(r'palette\s*(\S*)\s*$', line)
        if m:
            cur = None; pal = m.group(1) or 'main'; meta['palettes'][pal] = []; continue
        m = re.match(r'frame\s+(\S+)\s*(=\s*(.*))?$', line)
        if m:
            pal = None; cur = m.group(1); meta['order'].append(cur); target = meta['frames']
            meta['frames'][cur] = ('ref', m.group(3).split()) if m.group(2) else []
            if m.group(2): cur = None
            continue
        if pal is not None:
            if not line.strip():
                continue
            sym, r, g, b = line.split()[:4]
            meta['palettes'][pal].append((sym, (int(r), int(g), int(b)))); continue
        if cur is not None:
            if not line.strip() and not target[cur]:
                continue
            target[cur].append(line)
    if meta.get('include'):                     # another drawn file's palettes, parts and frames, unless redefined
        base = parse(os.path.join(os.path.dirname(path), meta['include'] + '.txt'))
        for key in ('palettes', 'parts', 'frames'):
            meta[key] = {**base[key], **meta[key]}
        meta['order'] = base['order'] + [o for o in meta['order'] if o not in base['order']]
    for name, p in meta['palettes'].items():
        assert len(p) == 16, f'{path}: palette {name} has {len(p)} colours'
        assert len({s for s, _ in p}) == 16, f'{path}: palette {name} repeats a symbol'
    return meta

def frames_of(meta, w, h, path=''):
    """{label: uint8 index array} with references resolved."""
    syms = {s: i for i, (s, _) in enumerate(meta['palettes']['main'])}
    out = {}
    def get(label):
        if label in out:
            return out[label]
        assert label in meta['frames'], f'{path}: no frame {label}'
        v = meta['frames'][label]
        if isinstance(v, tuple) and v[1][0] == 'stack':
            a = np.zeros((h, w), np.uint8)
            for item in v[1][1:]:
                bits = item.split(':')
                r0, pname = int(bits[0]), bits[1]
                dx = int(bits[2]) if len(bits) > 2 else 0
                if pname not in meta['parts'] and pname in meta['frames']:     # another frame as a layer
                    src = get(pname)
                    ys, xs = np.nonzero(src)
                    for y, x in zip(ys, xs):
                        if 0 <= y + r0 < h and 0 <= x + dx < w:
                            a[y + r0, x + dx] = src[y, x]
                    continue
                assert pname in meta['parts'], f'{path}: frame {label}: no part {pname}'
                for j, row in enumerate(meta['parts'][pname]):
                    y = r0 + j
                    for x, ch in enumerate(row):
                        if ch in '. ':
                            continue
                        if ch == '_':                  # erase to clear
                            a[y, x + dx] = 0
                            continue
                        assert ch in syms, f'{path}: part {pname} row {j}: symbol {ch!r} not in the palette'
                        assert 0 <= y < h and 0 <= x + dx < w, f'{path}: frame {label}: part {pname} outside the frame'
                        a[y, x + dx] = syms[ch]
        elif isinstance(v, tuple):
            op, args = v[1][0], v[1][1:]
            src = get(args[0])
            if op == 'mirror':
                a = src[:, ::-1].copy()
            elif op == 'same':
                a = src.copy()
            elif op == 'shift':
                dy = int(args[1]); a = np.zeros_like(src)
                if dy < 0: a[:dy] = src[-dy:]
                else: a[dy:] = src[:h - dy]
            else:
                raise SystemExit(f'{path}: frame {label}: unknown op {op}')
        else:
            rows = [r for r in v]
            while rows and not rows[-1].strip(): rows.pop()
            assert len(rows) == h, f'{path}: frame {label} has {len(rows)} rows, need {h}'
            a = np.zeros((h, w), np.uint8)
            for y, r in enumerate(rows):
                assert len(r.rstrip()) <= w, f'{path}: frame {label} row {y} longer than {w}: {r!r}'
                for x, ch in enumerate(r.ljust(w)[:w]):
                    if ch == ' ': ch = '.'
                    assert ch in syms, f'{path}: frame {label} row {y} col {x}: symbol {ch!r} not in the palette'
                    a[y, x] = syms[ch]
        out[label] = a
        return a
    for label in meta['frames']:
        get(label)
    return out

def material_outlines(a, groups, black):
    """Black 2's outline colours (the same convention as b2tools/sprite_upgrade.py colour_outlines): black around
    clothes, but the material's own dark tone around skin and hair. groups = [(member indices, outline index, last
    row or None)]: an outline pixel whose coloured 4-neighbours all belong to one group, sitting on the figure's edge
    or on a line of such pixels reaching it, takes the group's outline colour (lines inside a face, eyes and mouths,
    stay black)."""
    H, W = a.shape
    cand = np.full((H, W), -1, np.int16)
    for y, x in zip(*np.nonzero(a == black)):
        nb = [a[j, i] for j, i in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1))
              if 0 <= j < H and 0 <= i < W and a[j, i] not in (0, black)]
        if not nb:
            continue
        for members, oi, last in groups:
            if (last is None or y < last) and all(v in members for v in nb):
                cand[y, x] = oi
                break
    op = np.pad(a != 0, 1)
    edge = (a != 0) & (~op[:-2, 1:-1] | ~op[2:, 1:-1] | ~op[1:-1, :-2] | ~op[1:-1, 2:])
    keep = np.zeros((H, W), bool)
    stack = list(zip(*np.nonzero(edge & (cand >= 0))))
    while stack:
        y, x = stack.pop()
        if keep[y, x]:
            continue
        keep[y, x] = True
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                j, i = y + dy, x + dx
                if 0 <= j < H and 0 <= i < W and not keep[j, i] and cand[j, i] == cand[y, x]:
                    stack.append((j, i))
    out = a.copy()
    out[keep] = cand[keep]
    return out

def outline_groups(meta):
    """'outlines: Ssa>a hHLl>h<24' -> [(member indices, outline index, last row or None)]."""
    syms = {s: i for i, (s, _) in enumerate(meta['palettes']['main'])}
    groups = []
    for item in (meta.get('outlines') or '').split():
        m = re.match(r'([^>]+)>(.)(?:<(\d+))?$', item)
        assert m, f'outlines: bad item {item!r}'
        groups.append(({syms[c] for c in m.group(1)}, syms[m.group(2)], int(m.group(3)) if m.group(3) else None))
    return groups

def finished(meta, frames):
    """Frames with the Black 2 outline convention applied (when the file lists 'outlines')."""
    groups = outline_groups(meta)
    if not groups:
        return frames
    black = len(meta['palettes']['main']) - 1
    assert meta['palettes']['main'][black][1] == (0, 0, 0), 'the last palette entry must be the black outline'
    return {k: material_outlines(v, groups, black) for k, v in frames.items()}

def to_text(a, syms):
    return '\n'.join(''.join(syms[v] for v in row) for row in a)

# ---------------------------------------------------------------------------------------------------- Black 2 sheets

_cache = {}
def ow_data():
    if 'ow' not in _cache:
        _cache['ow'] = (sprites.ow_table(FILES), narc_entries(arc_path(FILES, sprites.ARC_OW_SHEETS)))
    return _cache['ow']

def donor(code):
    """(frames as index arrays, 16 RGB colours, export metadata) of an overworld code in the original ROM."""
    table, sheets = ow_data()
    sheet, rec = sprites.ow_sheet_of(FILES, code, table)
    frames, pname, pal = sprites.btx_decode(sheets[sheet])
    arrs = [np.frombuffer(bytes(px), np.uint8).reshape(h, w).copy() for _, w, h, px in frames]
    meta = dict(kind='overworld', code=code, sheet=sheet, frames=len(frames), size=[frames[0][1], frames[0][2]],
                controller=rec['spriteControllerType'], textures=[f[0] for f in frames], palette=pname)
    return arrs, [sprites.bgr555_to_rgb(c) for c in pal], meta

def tr_donor(s, side='front'):
    key = ('tr', side)
    if key not in _cache:
        _cache[key] = narc_entries(arc_path(FILES, sprites.ARC_TR[side]))
    ents = _cache[key]
    _, pal = sprites.nclr_colors(ents[8 * s + sprites.TR_PALETTE])
    _, _, parts = sprites.tr_decode_image(ents[8 * s + sprites.TR_PARTS], 'parts')
    _, _, static = sprites.tr_decode_image(ents[8 * s + sprites.TR_STATIC], 'static')
    cells = sprites.ncer_cells(ents[8 * s + 2])
    return (np.frombuffer(parts, np.uint8).reshape(128, 256).copy(),
            np.frombuffer(static, np.uint8).reshape(80, 80).copy(),
            [sprites.bgr555_to_rgb(c) for c in pal], cells)

# ---------------------------------------------------------------------------------------------------- Sapphire art

def g3_pal(n):
    v = open(os.path.join(PR, 'object_events', 'palettes', f'{n:02d}.pal')).read().split()[3:]
    v = [int(x) for x in v[:48]]
    return [tuple(v[3 * i:3 * i + 3]) for i in range(16)]

def g3_frames(pic, pal):
    """Sapphire's 16x32 overworld frames (9: down, up, left, down walk x2, up walk x2, left walk x2) and colours."""
    from PIL import Image
    a = np.array(Image.open(os.path.join(PR, 'object_events', 'pics', 'people', f'{pic}.png')))
    return [a[:, 16 * i:16 * i + 16] for i in range(a.shape[1] // 16)], g3_pal(int(pal))

def g3_trainer(pic):
    from PIL import Image
    im = Image.open(os.path.join(PR, 'trainers', f'{pic}.png'))
    p = im.getpalette()[:48]
    return np.array(im), [tuple(p[3 * i:3 * i + 3]) for i in range(16)]

# ---------------------------------------------------------------------------------------------------- build

def clear_number(kind_dir, n, keep=None):
    """Move an older folder for the same number (another name) to ~/.Trash, so the patch never sees two."""
    import shutil, time
    if not os.path.isdir(kind_dir):
        return
    for d in os.listdir(kind_dir):
        if d.split('-')[0].isdigit() and int(d.split('-')[0]) == n and d != keep:
            dst = os.path.join(os.path.expanduser('~/.Trash'), f'{d}-{time.strftime("%H%M%S")}')
            shutil.move(os.path.join(kind_dir, d), dst)
            print('  moved old', d, 'to', dst)

def build_ow(meta, path):
    code = int(meta['code'])
    _, _, dmeta = donor(code)
    n = dmeta['frames']; w, h = dmeta['size']
    labels = LAYOUTS[n]
    fr = finished(meta, frames_of(meta, w, h, path))
    for i, lab in enumerate(labels):            # right frames default to mirrored left frames
        if lab not in fr and lab.startswith('right'):
            fr[lab] = fr['left' + lab[5:]][:, ::-1].copy()
        assert lab in fr, f'{path}: frame {lab} missing (sheet of code {code} has {n} frames: {labels})'
    order = [fr[l] for l in labels]
    out = []
    variants = [(meta['name'], code, 'main')]
    if meta.get('variants'):
        v = meta['variants'].split()
        variants += [(v[i], int(v[i + 1]), v[i + 2]) for i in range(0, len(v), 3)]
    for name, vcode, pname in variants:
        _, _, vmeta = donor(vcode)
        assert vmeta['frames'] == n and vmeta['size'] == dmeta['size'], f'{name}: code {vcode} has another layout'
        rgbs = [rgb for _, rgb in meta['palettes'][pname]]
        kind_dir = os.path.join(SRC, 'overworld')
        folder = os.path.join(kind_dir, f'{vcode:03d}-{name}')
        clear_number(kind_dir, vcode, keep=os.path.basename(folder))
        os.makedirs(folder, exist_ok=True)
        sprites.write_pal(os.path.join(folder, 'palette.pal'), rgbs)
        for i, f in enumerate(order):
            sprites.write_png(os.path.join(folder, f'frame_{i:02d}.png'), f.tobytes(), w, h, rgbs)
        sprites.write_json(os.path.join(folder, 'sprite.json'), dict(
            vmeta, name=name, note=meta.get('note', ''), sapphire=meta.get('sapphire', ''),
            drawn=os.path.relpath(path, ROOT), made_by='b2tools/sprite_unique.py'))
        out.append((folder, order, rgbs))
    return out

def build_trainer(meta, path):
    """An 80x80 battle picture into a front sprite whose MCSS shows one still 80x80 cell (the NO_DATA classes'
    sprites 20/22/23/39/55/76/81: one cell, OBJs over texture (0,0)-(80,80), one frame): static.png = parts."""
    s = int(meta['trainer'])
    parts, static, rgbs0, cells = tr_donor(s)
    assert len(cells) == 1 and sprites.render_cell is not None
    box = (min(o[4] for o in cells[0]), min(o[5] for o in cells[0]),
           max(o[4] + o[2] for o in cells[0]), max(o[5] + o[3] for o in cells[0]))
    assert box == (0, 0, 80, 80), f'front sprite {s}: its cell covers {box}, not one 80x80 picture'
    fr = finished(meta, frames_of(meta, 80, 80, path))
    pic = fr['front']
    new_parts = np.zeros((128, 256), np.uint8); new_parts[:80, :80] = pic
    rgbs = [rgb for _, rgb in meta['palettes']['main']]
    kind_dir = os.path.join(SRC, 'trainer', 'front')
    folder = os.path.join(kind_dir, f'{s:03d}-{meta["name"]}')
    clear_number(kind_dir, s, keep=os.path.basename(folder))
    os.makedirs(folder, exist_ok=True)
    sprites.write_pal(os.path.join(folder, 'palette.pal'), rgbs)
    sprites.write_png(os.path.join(folder, 'parts.png'), new_parts.tobytes(), 256, 128, rgbs)
    sprites.write_png(os.path.join(folder, 'static.png'), pic.tobytes(), 80, 80, rgbs)
    sprites.write_json(os.path.join(folder, 'sprite.json'), dict(
        kind='trainer', side='front', sprite=s, archive=sprites.ARC_TR['front'], files=sprites.tr_files(s),
        name=meta['name'], note=meta.get('note', ''), sapphire=meta.get('sapphire', ''),
        drawn=os.path.relpath(path, ROOT), made_by='b2tools/sprite_unique.py'))
    return [(folder, [pic], rgbs)]

def build(name):
    path = os.path.join(DRAWN, f'{name}.txt')
    meta = parse(path)
    return build_trainer(meta, path) if 'trainer' in meta else build_ow(meta, path)

# ---------------------------------------------------------------------------------------------------- review

def render(frames, pal, scale=3, gap=2):
    from PIL import Image
    h, w = frames[0].shape
    lut = np.zeros((16, 4), np.uint8)
    for i in range(1, 16): lut[i] = (*pal[i], 255)
    strip = np.zeros((h, len(frames) * (w + gap) - gap, 4), np.uint8)
    for k, f in enumerate(frames):
        strip[:, k * (w + gap):k * (w + gap) + w] = lut[f]
    img = Image.fromarray(strip, 'RGBA')
    return img.resize((img.width * scale, img.height * scale), Image.NEAREST)

def review_rows(name, scale=3):
    """[(label, image)]: Sapphire's frames, the old stand-in (Black 2), the new sheet."""
    path = os.path.join(DRAWN, f'{name}.txt')
    meta = parse(path)
    rows = []
    if 'trainer' in meta:
        g3, gp = g3_trainer(meta['sapphire'].split()[0])
        rows.append((f'Sapphire: trainers/{meta["sapphire"].split()[0]}.png (64x64)', render([g3], gp, scale - 1)))
        if meta.get('standin'):
            from PIL import Image
            parts, static, rgbs, cells = tr_donor(int(meta['standin']))
            lut = np.zeros((16, 4), np.uint8)
            for i in range(1, 16): lut[i] = (*rgbs[i], 255)
            fig, _ = sprites.render_cell(Image.fromarray(lut[parts], 'RGBA'), cells[sprites.whole_figure_cell(cells)])
            fig = fig.resize((fig.width * (scale - 1), fig.height * (scale - 1)), Image.NEAREST)
            rows.append((f'before: front sprite {meta["standin"]} (Black 2 stand-in in converter/gen_trainers.py)', fig))
        fr = finished(meta, frames_of(meta, 80, 80, path))
        rows.append((f'new: front sprite {meta["trainer"]} ({meta.get("note", "")})',
                     render([fr['front']], [rgb for _, rgb in meta['palettes']['main']], scale - 1)))
        return rows
    pic, pal = meta['sapphire'].split()[:2]
    g3, gp = g3_frames(pic, pal)
    order = [1, 5, 6, 0, 3, 4, 2, 7, 8]       # up, up walk x2, down, down walk x2, left, left walk x2
    g3o = [np.pad(g3[i], ((0, 0), (8, 8))) for i in order]
    rows.append((f'Sapphire: {pic} (palette {pal})', render(g3o, gp, scale)))
    for sc in (meta.get('standin') or '').split():
        fr, rgbs, dm = donor(int(sc))
        rows.append((f'before: Black 2 code {sc} (stand-in)', render(fr, rgbs, scale)))
    code = int(meta['code'])
    _, _, dmeta = donor(code)
    labels = LAYOUTS[dmeta['frames']]
    fr = finished(meta, frames_of(meta, 32, 32, path))
    for lab in labels:
        if lab not in fr and lab.startswith('right'):
            fr[lab] = fr['left' + lab[5:]][:, ::-1].copy()
    pnames = ['main'] + ([meta['variants'].split()[i + 2] for i in range(0, len(meta['variants'].split()), 3)]
                         if meta.get('variants') else [])
    codes = [code] + ([int(meta['variants'].split()[i + 1]) for i in range(0, len(meta['variants'].split()), 3)]
                      if meta.get('variants') else [])
    for pname, c in zip(pnames, codes):
        rows.append((f'new: code {c} {meta["name"] if pname == "main" else pname} ({dmeta["frames"]} frames)',
                     render([fr[l] for l in labels], [rgb for _, rgb in meta['palettes'][pname]], scale)))
    return rows

def save_sheet(rows, out, title):
    from PIL import Image, ImageDraw
    os.makedirs(os.path.dirname(out), exist_ok=True)
    W = max(r.width for _, r in rows) + 16
    H = sum(r.height + 18 for _, r in rows) + 30
    img = Image.new('RGB', (W, H), (88, 112, 128)); d = ImageDraw.Draw(img); y = 6
    d.text((8, y), title, fill=(255, 255, 255)); y += 20
    for label, r in rows:
        d.text((8, y), label, fill=(230, 236, 255)); y += 14
        img.paste(r, (8, y), r); y += r.height + 4
    img.save(out)
    return out

ORDER = ['mom', 'mom-phone', 'gabby', 'ty', 'contest-reporter', 'contest-judge', 'teala', 'hot-springs-old-woman',
         'rooftop-sale-woman', 'mauville-old-man-1', 'mauville-old-man-2', 'interviewers-battle']

def names():
    have = {os.path.splitext(f)[0] for f in os.listdir(DRAWN) if f.endswith('.txt')} if os.path.isdir(DRAWN) else set()
    return [n for n in ORDER if n in have] + sorted(have - set(ORDER))

def review(out=None):
    rows = []
    for n in names():
        rows.append(('', None))
        rows += review_rows(n)
    rows = [r for r in rows if r[1] is not None]
    return save_sheet(rows, out or os.path.join(SHOTS, 'unique_upgrade_review.png'),
                      "Sapphire's unique NPCs, redrawn for Black 2 (b2tools/sprite_unique.py): "
                      'Sapphire / old Black 2 stand-in / new')

def draft(code, symmap):
    """Print a donor sheet as text with `symmap` ("0.f k 1a ..." pairs: donor index -> symbol)."""
    fr, rgbs, meta = donor(code)
    m = {int(p[0], 16): p[1] for p in symmap.split()}
    labels = LAYOUTS[meta['frames']]
    for lab, f in zip(labels, fr):
        print('frame', lab)
        print('\n'.join(''.join(m.get(v, '%x' % v) for v in row) for row in f))

def main(argv):
    if argv and argv[0] == 'review':
        print(review(argv[1] if len(argv) > 1 else None)); return
    if argv and argv[0] == 'draft':
        draft(int(argv[1]), ' '.join(argv[2:])); return
    for n in argv or names():
        for folder, frames, rgbs in build(n):
            print(n, '->', os.path.relpath(folder, ROOT), len(frames), 'frames')

if __name__ == '__main__':
    main(sys.argv[1:])
