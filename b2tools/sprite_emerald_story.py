"""Pokémon Emerald NDS: overworld sprites of Emerald's story characters (emerald_s0, 2026-10-12; notes/EMERALD_STORY.md
S0-5, data/emerald/sprite_map.json). Black 2's own sheet where Black 2 draws the character (Juan 276, Steven 287,
Wallace 288: nothing to make); otherwise Emerald's own sprite from the user's dump, resized exactly as Sapphire's
characters were (b2tools/sprite_upgrade.py ow_frames: Gen 5 proportions, outlines, Black 2's overworld skin ramp, the
12-frame layout), as b2tools/sprite_emerald.py does for the players. Nothing is redrawn; the character's colours are
Emerald's own palette (no colour settings).

    python3 sprite_emerald_story.py build      -> src/sprites/overworld/emerald/<code>-<name>/ (an Emerald build only)
    python3 sprite_emerald_story.py build tabitha   (only one: Scott's is redrawn from the dump, Tabitha's copied)
    python3 sprite_emerald_story.py review     -> screenshots/emerald_s0/story_sprites_review.png

Characters (CHARS): Scott on code 289, a Black 2 sheet no Hoenn build uses (b2tools: free_codes scan in the S0 report:
no zone entity, PWT record, trainer-class sprite or ActorNew in Black 2 or HoennB2; Black 2 sets it only in script file
128, a Unova zone script HoennB2 replaces with Safari Zone's). Its picture: pokeemerald OBJ_EVENT_GFX_SCOTT
(graphics/object_events/pics/people/scott.png, palette npc_1), found byte for byte in roms/emerald_original.gba
(emerald_src.Emerald.verify).
Tabitha (COPIES, user decision 2026-10-12: he walks as in Ruby NDS, so both versions match): Ruby NDS's own Tabitha sheet
(src/sprites/overworld/ruby/088-tabitha, b2tools/sprite_upgrade.py: the Magma grunt (M) sheet changed to his battle design)
copied as it is onto code 290, the female twin of Scott's 289 (Black 2 sets 289/290 only in script file 128, the Unova zone
script HoennB2 replaces with Safari Zone Southwest's; no zone entity, PWT record, HoennB2 data or other script uses 290;
same 12-frame 32x32 layout as 88's). Emerald itself draws him with the Magma grunt sprite; 88 stays Matt in Emerald.
Not made here: Juan (Black 2's PWT sheet 276 with its X frames filled, b2tools/sprite_pwt.py 276 -> the Emerald overlay),
the two teams (shared codes 293/294/353 Aqua, 302/192/303 Magma: no Ruby-style swap in Emerald).
"""
import os, sys, time, shutil
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, 'converter'))
import sprites  # noqa: E402
import emerald_src as E  # noqa: E402
import sprite_upgrade as U  # noqa: E402
from b2files import arc_path, narc_entries  # noqa: E402

OUT = os.path.join(ROOT, 'src', 'sprites', 'overworld', 'emerald')
SHOTS = os.path.join(ROOT, 'screenshots', 'emerald_s0')
FILES = sprites.SRC_FILES

# name -> overworld spec for sprite_upgrade.ow_frames: Emerald graphics id, Black 2 code, neck row (the first row below
# the chin in Emerald's 16x32 frame, as Sapphire's characters' 22), no colour changes (Emerald's own palette)
CHARS = {
    'scott': dict(gfx='OBJ_EVENT_GFX_SCOTT', code=289, neck=22,
                  note='Scott (Emerald: Petalburg, Rustboro school, Slateport, Mauville, Route 119, Lilycove motel, '
                       'Mossdeep, Ever Grande Center, S.S. Tidal, Frontier gate)'),
}

# name -> another version's HoennB2 sheet installed as it is on a free Black 2 code in Emerald builds
COPIES = {
    'tabitha': dict(code=290, src=os.path.join('ruby', '088-tabitha'),
                    note='Tabitha (Team Magma admin; Emerald: Mt. Chimney, Magma Hideout, Mossdeep Space Center), Ruby NDS\'s '
                         'sheet so both versions match (user decision 2026-10-12)'),
}

def copy_sheet(name):
    """COPIES[name]: the frames and palette of the other version's folder written as an Emerald folder of the new code
    (the sheets' layouts must match: the same texture names and sizes)."""
    spec = COPIES[name]
    src = os.path.join(ROOT, 'src', 'sprites', 'overworld', spec['src'])
    smeta = sprites.read_json(os.path.join(src, 'sprite.json'))
    code = spec['code']
    table = sprites.ow_table(FILES)
    sheet, rec = sprites.ow_sheet_of(FILES, code, table)
    lay, pname, _ = sprites.btx_layout(narc_entries(arc_path(FILES, sprites.ARC_OW_SHEETS))[sheet])
    assert [l[0] for l in lay] == smeta['textures'] and pname == smeta['palette'] and \
        rec['spriteControllerType'] == smeta['controller'], (name, code, 'layout differs from', spec['src'])
    folder = os.path.join(OUT, f'{code:03d}-{name}')
    for d in (os.listdir(OUT) if os.path.isdir(OUT) else []):       # an older folder for the same code: to the Trash
        p = os.path.join(OUT, d)
        if d.split('-')[0].isdigit() and int(d.split('-')[0]) == code and p != folder:
            shutil.move(p, os.path.join(os.path.expanduser('~/.Trash'), f'{d}-{time.strftime("%Y%m%d-%H%M%S")}'))
    os.makedirs(folder, exist_ok=True)
    shutil.copyfile(os.path.join(src, 'palette.pal'), os.path.join(folder, 'palette.pal'))
    for i in range(smeta['frames']):
        shutil.copyfile(os.path.join(src, f'frame_{i:02d}.png'), os.path.join(folder, f'frame_{i:02d}.png'))
    sprites.write_json(os.path.join(folder, 'sprite.json'), dict(
        smeta, code=code, sheet=sheet, textures=[l[0] for l in lay], palette=pname, name=name, note=spec['note'],
        source=f'src/sprites/overworld/{spec["src"]} (Ruby NDS; {smeta.get("source", "")})',
        made_by='b2tools/sprite_emerald_story.py (copy of Ruby NDS\'s sheet)'))
    return folder

def emerald_overworld(gfx):
    """sprite_upgrade.gen3_overworld for Emerald's graphics ids: (9 frames 32x16, 16 RGB)."""
    frames, pal, _ = E.emerald().frames(gfx)
    return frames, pal

def frames_of(name):
    """12 Black 2 frames + palette of an Emerald character (sprite_upgrade.ow_frames on Emerald's picture)."""
    spec = CHARS[name]
    keep = U.gen3_overworld
    U.gen3_overworld = emerald_overworld
    try:
        return U.ow_frames(dict(gfx=spec['gfx'], neck=spec['neck']))
    finally:
        U.gen3_overworld = keep

def found_in_dump(gfx):
    """[(file, [addresses])] of the picture and palette in roms/emerald_original.gba; every list must be non-empty."""
    res = E.emerald().verify(gfx)
    assert all(a for _, a in res), f'{gfx}: not found in the dump: {res}'
    return res

def build(name):
    spec = CHARS[name]
    where = found_in_dump(spec['gfx'])
    frames, pal = frames_of(name)
    code = spec['code']
    table = sprites.ow_table(FILES)
    sheet, rec = sprites.ow_sheet_of(FILES, code, table)
    lay, pname, _ = sprites.btx_layout(narc_entries(arc_path(FILES, sprites.ARC_OW_SHEETS))[sheet])
    assert rec['spriteControllerType'] == 3 and len(lay) == 12 and lay[0][1] == 32, (code, rec['spriteControllerType'])
    folder = os.path.join(OUT, f'{code:03d}-{name}')
    for d in (os.listdir(OUT) if os.path.isdir(OUT) else []):       # an older folder for the same code: to the Trash
        p = os.path.join(OUT, d)
        if d.split('-')[0].isdigit() and int(d.split('-')[0]) == code and p != folder:
            shutil.move(p, os.path.join(os.path.expanduser('~/.Trash'), f'{d}-{time.strftime("%Y%m%d-%H%M%S")}'))
    os.makedirs(folder, exist_ok=True)
    sprites.write_pal(os.path.join(folder, 'palette.pal'), pal)
    for i, f in enumerate(frames):
        sprites.write_png(os.path.join(folder, f'frame_{i:02d}.png'), f.tobytes(), 32, 32, pal)
    sprites.write_json(os.path.join(folder, 'sprite.json'), dict(
        kind='overworld', code=code, sheet=sheet, frames=12, size=[32, 32], controller=3,
        textures=[l[0] for l in lay], palette=pname, name=name, note=spec['note'],
        source=f'pokeemerald {spec["gfx"]} (' + ', '.join(f'{p} at {", ".join(hex(a) for a in adr)}' for p, adr in where)
               + ' in roms/emerald_original.gba)',
        made_by='b2tools/sprite_emerald_story.py (sprite_upgrade.ow_frames, as Sapphire\'s characters)'))
    return folder

# ---------------------------------------------------------------------------------------------------- review

def _rgba(a, pal):
    return U.rgba(np.asarray(a, np.uint8), pal)

def _b2_sheet(code, frames=None):
    """[RGBA] of Black 2's own sheet for code (all its frames)."""
    table = sprites.ow_table(FILES)
    sheet, _ = sprites.ow_sheet_of(FILES, code, table)
    fr, _, pal = sprites.btx_decode(narc_entries(arc_path(FILES, sprites.ARC_OW_SHEETS))[sheet])
    rgbs = [sprites.bgr555_to_rgb(c) for c in pal]
    ks = range(len(fr)) if frames is None else frames
    return [_rgba(np.frombuffer(bytes(fr[k][3]), np.uint8).reshape(fr[k][2], fr[k][1]), rgbs) for k in ks]

def _folder(code, overlay=None):
    """[RGBA] of the frames of HoennB2's art folder for code (shared, or the overlay's)."""
    import glob, json
    base = os.path.join(ROOT, 'src', 'sprites', 'overworld', *( [overlay] if overlay else []))
    d = next(p for p in glob.glob(os.path.join(base, f'{code:03d}-*')) if os.path.isdir(p))
    meta = json.load(open(os.path.join(d, 'sprite.json')))
    if 'copy_of' in meta:
        return _folder(int(meta['copy_of']))
    pal = sprites.read_pal(os.path.join(d, 'palette.pal'))
    w, h = meta.get('size', [32, 32])
    return [_rgba(np.frombuffer(sprites.read_png(os.path.join(d, f'frame_{k:02d}.png'), pal, w, h), np.uint8).reshape(h, w), pal)
            for k in range(meta.get('frames', 12))]

def _gen3(gfx, ks=(0, 1, 2)):
    fr, pal, _ = E.emerald().frames(gfx)
    return [_rgba(fr[k], pal) for k in ks]

def review(path=None):
    from PIL import Image, ImageDraw
    S = 3
    rows = []
    def row(title, groups):
        rows.append((title, groups))
    sc = frames_of('scott')
    row('Scott: Emerald (dump) / Black 2 289 before (unused sheet) / Emerald NDS 289 (12 frames)',
        [('Emerald', _gen3('OBJ_EVENT_GFX_SCOTT')), ('B2 289 before', _b2_sheet(289, (3, 0, 6))),
         ('new 289', [_rgba(f, sc[1]) for f in sc[0]])])
    row('Juan: Emerald (dump) / Black 2 PWT 276 / Emerald NDS 276 (X frames filled by sprite_pwt.py, Emerald overlay)',
        [('Emerald', _gen3('OBJ_EVENT_GFX_JUAN')), ('B2 276 (all 12)', _b2_sheet(276)), ('new 276', _folder(276, 'emerald'))])
    row('Tabitha: Ruby NDS\'s sheet (ruby/088-tabitha) on code 290 in Emerald NDS (88 stays Matt); Emerald draws him with '
        'the Magma grunt (M) sprite',
        [('Emerald MAGMA_MEMBER_M', _gen3('OBJ_EVENT_GFX_MAGMA_MEMBER_M')), ('B2 290 before', _b2_sheet(290, (3, 0, 6))),
         ('new 290', _folder(290, 'emerald')[3:6] + _folder(290, 'emerald')[:1])])
    row('Teams unswapped in Emerald (shared art): Aqua 293 / 294 / Archie 353, Magma 302 / 192 / Maxie 303',
        [(f'{c}', [_folder(c)[3]]) for c in (293, 294, 353, 302, 192, 303)])
    row('Ruby for comparison (art swapped by RUBY_SWAPS): 293 / 294 / 353 / 302 / 192 / 303',
        [(f'{c}', [_folder(c, 'ruby')[3]]) for c in (293, 294, 353, 302, 192, 303)])
    row('Wallace 288 and Steven 287: Black 2 PWT sheets with sprite_pwt.py frames, shared (as in Sapphire)',
        [('288', _folder(288)), ('287', _folder(287))])
    y = 10; pad = 6
    W = 20 + max(sum(sum(im.width * S + pad for im in ims) + 24 for _, ims in groups) for _, groups in rows)
    heights = []
    for title, groups in rows:
        h = max(im.height for _, ims in groups for im in ims) * S
        heights.append(h)
    H = 10 + sum(h + 46 for h in heights)
    sheet = Image.new('RGBA', (W, H), (48, 48, 56, 255)); dr = ImageDraw.Draw(sheet)
    for (title, groups), h in zip(rows, heights):
        dr.text((10, y), title, fill=(235, 235, 235, 255)); y += 16
        x = 10
        for label, ims in groups:
            dr.text((x, y), label, fill=(170, 200, 255, 255))
            gx = x
            for im in ims:
                big = im.resize((im.width * S, im.height * S), Image.NEAREST)
                bg = Image.new('RGBA', big.size, (112, 136, 152, 255)); bg.alpha_composite(big)
                sheet.alpha_composite(bg, (gx, y + 12)); gx += big.width + pad
            x = gx + 24
        y += h + 30
    os.makedirs(SHOTS, exist_ok=True)
    out = path or os.path.join(SHOTS, 'story_sprites_review.png')
    sheet.save(out)
    return out

def main(argv):
    if argv[:1] == ['build']:
        for n in (argv[1:] or list(CHARS) + list(COPIES)):
            print(os.path.relpath(copy_sheet(n) if n in COPIES else build(n), ROOT))
    elif argv[:1] == ['review']:
        print(os.path.relpath(review(), ROOT))
    else:
        print(__doc__)

if __name__ == '__main__':
    main(sys.argv[1:])
