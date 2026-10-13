"""Install the edited character sprites in src/sprites/ (formats: b2tools/sprites.py).

    src/sprites/overworld/<code>[-name]/          sprite.json, palette.pal, frame_NN.png  -> a/0/4/8, the sheet of
                                                   object code <code> (looked up in a/0/4/7), rewritten in place
    src/sprites/trainer/front/<sprite>[-name]/    sprite.json, palette.pal, parts.png, static.png -> a/0/7/1
    src/sprites/trainer/back/<sprite>[-name]/     same -> a/0/7/2 (files 8s, 8s+1 LZ11-compressed again, 8s+7)
    src/sprites/texture/<name>/                   sprite.json, texture.png -> an 8 bpp texture (and its palette) in a
                                                   model's TEX0, rewritten in place (e.g. the intro's gender choice,
                                                   a/1/6/8 file 22: int_swan_m/f.1/.2); the archive keeps its size
    src/sprites/objframes/<name>/                 sprite.json only: the player icons in a/0/3/0 (Continue panel, GTS,
                                                   Spin Trade) get the frames and palette of the overworld art folder
                                                   of "from_code" (sprites.py "Player icons"); in place
    src/sprites/cardpic/<name>/                   sprite.json only: trainer card pictures (a/0/4/0 avatars) get the
                                                   still picture of a trainer folder (sprites.py "Trainer card
                                                   pictures"); in place
    src/sprites/mcss/<name>/                      any other MCSS sprite: sprite.json names the archive and files
                                                   (e.g. the intro professor, a/1/6/8 files 25 + 28); "keep_size"
                                                   keeps the archive's size (it is not padded by build_rom.py);
                                                   "node_moves" [{"seq", "x", "y"}] moves the multi-cell nodes that
                                                   play those cell animations (files "nmcr"; mcss.move_nodes)

Code (apply_code): the trainer card (ov186) shows the player's own card with Black 2's built-in Nate / Rosa picture
(a/0/3/9 NCGR 36 + NSCR 50 / 51, 110 shared 8 bpp tiles, too few for new art) and only another player's card with
the Union Room avatar picture (a/0/4/0 NCGR 16 + v / NCLR v). In func_ov186_021a7ec0 the test of the card's
"another player's card" bit (card data +4, bit 7) before the picture load, `bne` at 0x021a7ee0, becomes `b`: every
card shows the avatar picture, which src/sprites/cardpic/ makes Brendan (boys) or May (girls). The bit's other uses
(no editing of another player's card) are unchanged.

A folder whose sprite.json is {"copy_of": <code or sprite>} installs the art of that other folder of the same kind
(the layouts must match; checked), so e.g. the rival Brendan NPC codes reuse the player Brendan art.
A trainer folder with "mcss_from": <sprite> holds art drawn on that other sprite's parts: its 8 files (pictures,
cells, animations, MCSS data, palette) are copied into the slot first, then the art is installed. "static_intro": true
makes the battle intro show the still figure instead of the parts' gesture (b2tools/mcss.py static_intro);
"node_edits" [{"mc", "node", "seq", "x", "y"}] re-point / move single multi-cell nodes (mcss.set_nodes) and
"still_multicells" [m ...] stops animation 1 from sliding those multi-cells (mcss.still_translations), both in place
(Wally's back sprite: b2tools/sprite_upgrade_backs.py).
Overworld sheets keep their size; the trainer archives change size and build_rom.py pads them (RESERVE 71/72).
"""
import glob, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import mcss, narcio, sprites, version  # noqa: E402

SRC = os.environ.get('HOENN_SPRITES_SRC') or os.path.join(os.path.dirname(os.path.dirname(HERE)), 'src', 'sprites')  # override: tests
# The Gen 5 (community) set, b2tools/sprite_community.py: same layout as src/sprites. The in-game switch (Birch's 4th
# question, patch sprite_switch) puts it in the ROM next to this install and picks one at run time; HOENN_SPRITES_GEN5=1
# installs its folders over src/sprites' as the only set (test builds; sprite_switch then does nothing).
GEN5 = os.path.join(os.path.dirname(os.path.dirname(HERE)), 'src', 'sprites_gen5')
# Its battle backs (b2tools/sprite_community.py: Gen 4-style waist-up figures on Nate's cells, placed with their bottom
# edge on the screen's edge) are raised by placement only: every node node_edits places moves up GEN5_BACK_LIFT pixels,
# so the figure stands on the battle message box (its first row is the top screen's row 147, 45 above the edge) and the
# whole throw shows above it. The art (parts.png) is untouched; every Gen 5 back (Brendan's, May's later) gets it.
GEN5_BACK_LIFT = 45

def _gen5_back(folder, side):
    return side == 'back' and os.path.commonpath([os.path.abspath(folder), GEN5]) == GEN5

def placed_nodes(meta, folder, side):
    """node_edits as installed: a Gen 5 back's placed nodes raised GEN5_BACK_LIFT pixels"""
    edits = meta['node_edits']
    if _gen5_back(folder, side):
        edits = [dict(e, y=int(e['y']) - GEN5_BACK_LIFT) if 'y' in e else e for e in edits]
    return edits

def _shared(kind_dir):
    """{number: folder} of the shared (Sapphire) folders: src/sprites, with src/sprites_gen5 over it when
    HOENN_SPRITES_GEN5=1."""
    out = _scan(os.path.join(SRC, kind_dir))
    if os.environ.get('HOENN_SPRITES_GEN5'):
        out.update(_scan(os.path.join(GEN5, kind_dir)))
    return out

def folders(kind_dir):
    """{number: folder} for the folders named <number>[-name] under src/sprites/<kind_dir>; in a Ruby or Emerald build
    the folders of src/sprites/<kind_dir>/<version>/ replace (or add) theirs (notes/RUBY.md "WP0 layout"), and with
    HOENN_SPRITES_GEN5=1 those of src/sprites_gen5/<kind_dir>/<version>/ over all of them (Emerald's NEW-set outfits,
    notes/EMERALD.md)."""
    out = _shared(kind_dir)
    if version.has_overlay():
        out.update(_scan(os.path.join(SRC, kind_dir, version.OVERLAY)))
        if os.environ.get('HOENN_SPRITES_GEN5'):
            out.update(_scan(os.path.join(GEN5, kind_dir, version.OVERLAY)))
    return out

def _scan(path):
    out = {}
    for d in sorted(glob.glob(os.path.join(path, '*'))):
        name = os.path.basename(d)
        if not os.path.isdir(d) or not name.split('-')[0].isdigit():
            continue
        n = int(name.split('-')[0])
        assert n not in out, f'two folders for {path} {n}: {out[n]} and {d}'
        out[n] = d
    return out

def source(found, n, kind_dir):
    """The folder holding the art for number n (follows copy_of). A copy_of in a ruby/ (emerald/) folder names a shared
    (Sapphire) folder, so two numbers can trade art (ruby/293 copy_of 302, ruby/302 copy_of 293)."""
    meta = sprites.read_json(os.path.join(found[n], 'sprite.json'))
    if 'copy_of' in meta:
        src = int(meta['copy_of'])
        if os.path.basename(os.path.dirname(found[n])) == version.OVERLAY:
            found = _shared(kind_dir)
        assert src in found and 'copy_of' not in sprites.read_json(os.path.join(found[src], 'sprite.json')), \
            f'{found[n] if n in found else n}: copy_of {src} is not an art folder in {kind_dir}'
        return found[src]
    return found[n]

CARD_PICTURE_EDIT = ('arm9_ov186.bin', 0x021a7ee0 - 0x021a75a0, '1fd1', '1fe0')   # bne -> b (same target 0x021a7f22)

def apply_code(code):
    name, at, old, new = CARD_PICTURE_EDIT
    if not os.path.isdir(os.path.join(SRC, 'cardpic')):
        return 'no trainer card pictures: ov186 unchanged'
    path = os.path.join(code, name)
    data = bytearray(open(path, 'rb').read())
    o, n = bytes.fromhex(old), bytes.fromhex(new)
    assert data[at:at + 2] in (o, n), f'{name} {at:#x}: unexpected {data[at:at + 2].hex()}'
    data[at:at + 2] = n
    if os.path.islink(path): os.unlink(path)
    open(path, 'wb').write(data)
    return f'{name}: the trainer card shows the avatar picture (Brendan / May)'

def apply(files):
    done = []
    ow = folders('overworld')
    if ow:
        table = sprites.ow_table(files)
        sheets = narcio.load(files, sprites.ARC_OW_SHEETS)
        for code in sorted(ow):
            folder = source(ow, code, 'overworld')
            meta = sprites.read_json(os.path.join(folder, 'sprite.json'))
            if folder == ow[code]:
                assert meta['code'] == code, f'{folder}: sprite.json says code {meta["code"]}'
            sheet, _ = sprites.ow_sheet_of(files, code, table)
            new = sprites.ow_import(folder, sheets[sheet])
            assert len(new) == len(sheets[sheet])
            sheets[sheet] = new
            done.append(f'ow {code}' + ('' if folder == ow[code] else f'<-{meta["code"]}'))
        narcio.save(files, sprites.ARC_OW_SHEETS, sheets)
    for side, arc in sprites.ARC_TR.items():
        tr = folders(os.path.join('trainer', side))
        if not tr:
            continue
        ents = narcio.load(files, arc)
        orig = list(ents)
        for s in sorted(tr):
            folder = source(tr, s, f'trainer/{side}')
            meta = sprites.read_json(os.path.join(folder, 'sprite.json'))
            assert meta['side'] == side, f'{folder}: a {meta["side"]} sprite in trainer/{side}'
            if 'mcss_from' in meta:                  # art drawn on another sprite's parts: take its whole set
                src = int(meta['mcss_from'])
                ents[8 * s:8 * s + 8] = orig[8 * src:8 * src + 8]
            new = sprites.tr_import(folder, ents, sprite=s)
            for k, data in new.items():
                ents[k] = data
            if meta.get('static_intro'):             # the intro gesture shows the still figure (mcss.static_intro)
                ents[8 * s + 5] = mcss.static_intro(ents[8 * s + 5])
            if meta.get('node_edits'):               # multi-cell nodes re-pointed / moved (mcss.set_nodes, same size)
                ents[8 * s + 4] = mcss.set_nodes(ents[8 * s + 4], placed_nodes(meta, folder, side))
            if meta.get('still_multicells'):         # animation 1 no longer slides these multi-cells (same size)
                ents[8 * s + 5] = mcss.still_translations(ents[8 * s + 5], 1, meta['still_multicells'])
            done.append(f'{side} {s}')
        narcio.save(files, arc, ents)
    for folder in sorted(glob.glob(os.path.join(SRC, 'mcss', '*'))):
        if not os.path.isfile(os.path.join(folder, 'sprite.json')):
            continue
        meta = sprites.read_json(os.path.join(folder, 'sprite.json'))
        path = sprites.arc_path(files, meta['archive'])
        before = os.path.getsize(path)
        ents = narcio.load(files, meta['archive'])
        for k, data in sprites.mcss_import(folder, ents).items():
            ents[k] = data
        if meta.get('node_moves'):                   # cell animations placed elsewhere (mcss.move_nodes, same size)
            f = meta['files']['nmcr']
            ents[f] = mcss.move_nodes(ents[f], meta['node_moves'])
        narcio.save(files, meta['archive'], ents)
        if meta.get('keep_size'):
            assert os.path.getsize(path) == before, f'{folder}: archive {meta["archive"]} changed size'
        done.append(f'mcss {os.path.basename(folder)} (a/{meta["archive"]:03d})')
    for folder in sorted(glob.glob(os.path.join(SRC, 'objframes', '*'))):
        if not os.path.isfile(os.path.join(folder, 'sprite.json')):
            continue
        meta = sprites.read_json(os.path.join(folder, 'sprite.json'))
        art = source(ow, int(meta['from_code']), 'overworld')
        path = sprites.arc_path(files, meta['archive'])
        before = os.path.getsize(path)
        ents = narcio.load(files, meta['archive'])
        for k, data in sprites.objframes_import(folder, ents, art).items():
            assert len(data) == len(ents[k])
            ents[k] = data
        narcio.save(files, meta['archive'], ents)
        assert os.path.getsize(path) == before, f'{folder}: archive {meta["archive"]} changed size'
        done.append(f'objframes {os.path.basename(folder)} (a/{meta["archive"]:03d})')
    fronts = folders(os.path.join('trainer', 'front'))
    for folder in sorted(glob.glob(os.path.join(SRC, 'cardpic', '*'))):
        if not os.path.isfile(os.path.join(folder, 'sprite.json')):
            continue
        meta = sprites.read_json(os.path.join(folder, 'sprite.json'))
        art = source(fronts, int(meta['from_front']), 'trainer/front')
        path = sprites.arc_path(files, meta['archive'])
        before = os.path.getsize(path)
        ents = narcio.load(files, meta['archive'])
        for k, data in sprites.cardpic_import(folder, ents, art).items():
            assert len(data) == len(ents[k])
            ents[k] = data
        narcio.save(files, meta['archive'], ents)
        assert os.path.getsize(path) == before, f'{folder}: archive {meta["archive"]} changed size'
        done.append(f'cardpic {os.path.basename(folder)} (a/{meta["archive"]:03d})')
    by_file = {}
    for folder in sorted(glob.glob(os.path.join(SRC, 'texture', '*'))):
        if os.path.isfile(os.path.join(folder, 'sprite.json')):
            meta = sprites.read_json(os.path.join(folder, 'sprite.json'))
            by_file.setdefault((meta['archive'], meta['file']), []).append(folder)
    for (arc, fi), fols in sorted(by_file.items()):
        path = sprites.arc_path(files, arc)
        before = os.path.getsize(path)
        ents = narcio.load(files, arc)
        data = ents[fi]
        for folder in fols:
            data = sprites.tex_import(folder, data)
        assert len(data) == len(ents[fi])
        ents[fi] = data
        narcio.save(files, arc, ents)
        assert os.path.getsize(path) == before, f'texture: archive {arc} changed size'
        done.append(f'texture a/{arc:03d}/{fi}: ' + ', '.join(os.path.basename(f) for f in fols))
    return 'sprites: ' + (', '.join(done) if done else 'none in src/sprites')
