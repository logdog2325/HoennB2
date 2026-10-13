"""Sapphire's large objects that Black 2 has no sprite for, as Black 2 3D field objects (missing_objects, 2026-10-08).

    python3 models_objects.py [name ...]        build src/objects3d/<code>-<name>/ and the billboard folders in
                                                 src/sprites/overworld (default: all; 'berry-trees' = the 7 tree sheets
                                                 and data/berry_tree_sprites.json)

Black 2's field actors come in two kinds (a/0/4/7 FieldActorConfig.entityType, data/sprite_map.json): billboards (1,
the people: one 32x32 or 64x64 texture per frame) and 3D models (2: the Strength boulders 0x2003/0x2005, the bronze
statue 0x200A, ...; their BMD0 in a/0/4/8 holds MDL0 + TEX0). A 3D actor is placed, hidden by its spawn flag and moved
by movement lists like any NPC (the boulders are pushed that way), in whole tiles; the model never turns with the
actor's direction (ov036's one 3D draw processor, 0x021cf9a0: func_ov036_021974b4 only sets the object's position), so
a model is made in the direction Sapphire's object faces (rotate_bmd). Object codes 0x2000-0x2002 have empty records
(entityType 2, sceneNodeType 0, res 0; used by no zone, no script and none of our data); a fourth model takes code 112,
an empty people record (entityType 0, res 0: no Black 2 zone NPC, ActorNew or WKOBJCODE work uses it; not a Strength
rock code, which 109 = 0x6d is). This builder makes the models and b2tools/patches/objects3d.py fills the records (as
patches/boulder_1x1.py did for 0x2004).

Objects (Sapphire object_events, pokeruby data/maps/*/map.json; art = Sapphire's own pixels or Black 2's own model):
  0x2001 briney-boat       OBJ_EVENT_GFX_MR_BRINEYS_BOAT facing up (Route 104 (12,54), Route 109 (21,26)): Black 2's
                           white motorboat c03_ship_04 (exterior pack 21 res 208; the boat of the Briney cutscene,
                           demo 4) scaled to Sapphire's boat (BOAT_SCALE), its textures copied from texture set 21
  112    briney-boat-south the same boat facing down (Dewford (12,8))
  0x2002 ss-tidal          OBJ_EVENT_GFX_SS_TIDAL, facing right in all four places (Slateport and Lilycove Harbors (8,9),
                           Battle Tower (19,26), Southern Island (13,25)): Black 2's ferry c13_ship_01 (exterior pack 54
                           res 318, Virbank's; the S.S. Tidal's trips play Black 2's ferry demo) scaled to Sapphire's
                           ship and turned bow east
  Record offsets (object.json): offY lifts the hull to the water (the models' waterline is 15 units below their
  origin), offZ puts the model where Sapphire draws the sprite (bottom on the tile's south edge: half the sprite's
  height north of the tile centre).
  194    seafloor-submarine the stolen submarine in Underwater_SeafloorCavern, which Sapphire draws in the map (metatiles
                           0x2e0-0x2eb at (5-8,3-5), rock after the legend escaped): the 64x32 top layer of those
                           metatiles on a quad leaning back 45 degrees to the camera, its floor shadow under it;
                           collision 4x1 over the hull tiles, hidden by FLAG_HIDE_UNDERWATER_SUBMARINE_INTERACTION
  0x2000 submarine-shadow  OBJ_EVENT_GFX_SUBMARINE_SHADOW (Slateport Harbor (7,9), Aqua Hideout B2F (19,20), Magma
                           Hideout B2F (12,20)): Sapphire draws the stolen Explorer 1 only as this shadow under the
                           water (88x32 px, pokeruby graphics/object_events/pics/misc/submarine_shadow.png, palette 26:
                           colours 6 and 7 in a checkerboard). Here: a flat quad lying on the water, 88 x 32 units
                           (Sapphire's pixel = one Black 2 unit, 16 per tile), placed as Sapphire places the sprite
                           (centred on the object's tile in x, its bottom edge on the tile's south edge: rows y-1 and y).
                           The checkerboard's holes are filled with the same colours (a 4-colour texture, 1 KB) and
                           the quad is drawn at polygon alpha 16/31, the 3D equivalent of Gen 3's dithered shadow.

Model files: the DAE goes through b2tools/java ToNsbmd (CTRMap's writer, --vcol: unlit vertex colours, as the shadow
must keep Sapphire's colours under every room light), which writes the MDL0; the TEX0 is written here (formats from
GBATEK "DS 3D Texture Formats"; layout as Black 2's TEX0 blocks, nsbtx.py) and the two blocks make one BMD0 as Black 2's actor models are (bigrock: MDL0 at 0x18, TEX0 after).
src/objects3d/<code>-<name>/: model.nsbmd (installed byte for byte), object.json (the a/0/4/7 record: which Black 2
record it copies and what it changes), texture.png (the texture as drawn), source.png (Sapphire's picture).
"""
import json, os, struct, subprocess, sys, tempfile
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
import nsbtx  # noqa: E402
from dae import Model  # noqa: E402

OUT = os.path.join(ROOT, 'src', 'objects3d')
PR = os.path.join(ROOT, 'external', 'pokeruby', 'graphics', 'object_events')
CP = ':'.join(os.path.join(ROOT, p) for p in ('tools/CTRMap.jar', 'tools/ctrmap-plugins/CTRMapV-1.4.1.jar'))
SHOTS = os.path.join(ROOT, 'screenshots', 'missing_objects')

def c8to5(c): return (int(c) * 31 + 127) // 255
def bgr555(rgb): return c8to5(rgb[0]) | (c8to5(rgb[1]) << 5) | (c8to5(rgb[2]) << 10)

def sapphire_pic(rel, pal):
    """A Sapphire object picture as RGBA with its in-game palette (graphics/object_events/palettes/<pal>.pal)."""
    im = Image.open(os.path.join(PR, 'pics', rel))
    idx = np.array(im)
    lines = open(os.path.join(PR, 'palettes', f'{pal}.pal')).read().split('\n')[3:19]
    cols = [tuple(int(v) for v in l.split()) for l in lines]
    rgba = np.zeros(idx.shape + (4,), np.uint8)
    for i, c in enumerate(cols):
        if i: rgba[idx == i] = c + (255,)
    return idx, rgba, cols

# ---------------------------------------------------------------------------------------------------- TEX0 / BMD0

def tex0_block(textures):
    """textures: [(name, rgba HxWx4 uint8, fmt)] with fmt 1 (A3I5: alpha 0-7 from the image's alpha), 2 (4 colours)
    or 3 (16 colours; 2 and 3 with index 0 clear). Each texture gets its own palette '<name>_pl' (its distinct colours). Returns the TEX0
    block bytes (header layout as Black 2's actor models)."""
    texdata, pdata, texs, pals, pflag = bytearray(), bytearray(), [], [], 0
    for name, rgba, fmt in textures:
        h, w = rgba.shape[:2]
        assert w in (8, 16, 32, 64, 128, 256, 512, 1024) and h in (8, 16, 32, 64, 128, 256, 512, 1024), (name, w, h)
        a = rgba[..., 3]
        colours = sorted({bgr555(px[:3]) for px in rgba.reshape(-1, 4) if px[3]})
        if fmt == 1:
            assert len(colours) <= 32, f'{name}: {len(colours)} colours (A3I5 holds 32)'
            pal = colours
            look = {c: i for i, c in enumerate(pal)}
            raw = bytearray(w * h)
            for y in range(h):
                for x in range(w):
                    if a[y, x]:
                        raw[y * w + x] = look[bgr555(rgba[y, x, :3])] | (round(int(a[y, x]) * 7 / 255) << 5)
            col0 = 0
        elif fmt == 2:
            assert len(colours) <= 3, f'{name}: {len(colours)} colours (4-colour textures hold 3 + clear)'
            pal = [0] + colours
            look = {c: i + 1 for i, c in enumerate(colours)}
            raw = bytearray(w * h // 4)
            for y in range(h):
                for x in range(w):
                    v = look[bgr555(rgba[y, x, :3])] if a[y, x] >= 128 else 0
                    raw[(y * w + x) // 4] |= v << (2 * (x & 3))
            col0 = 1
        elif fmt == 3:
            assert len(colours) <= 15, f'{name}: {len(colours)} colours (16-colour textures hold 15 + clear)'
            pal = [0] + colours
            look = {c: i + 1 for i, c in enumerate(colours)}
            raw = bytearray(w * h // 2)
            for y in range(h):
                for x in range(w):
                    v = look[bgr555(rgba[y, x, :3])] if a[y, x] >= 128 else 0
                    raw[(y * w + x) // 2] |= v << (4 * (x & 1))
            col0 = 1
        else:
            raise ValueError(fmt)
        while len(texdata) % 8: texdata.append(0)
        off = len(texdata); texdata += raw
        lw, lh = (w // 8).bit_length() - 1, (h // 8).bit_length() - 1
        params = (off >> 3) | (lw << 20) | (lh << 23) | (fmt << 26) | (col0 << 29)
        texs.append((name, struct.pack('<II', params, 0x80000000 | (h << 11) | w)))
        while len(pdata) % 16: pdata.append(0)     # 16-colour palettes need a 16-byte boundary (4-colour: 8)
        pals.append((name + '_pl', struct.pack('<HH', len(pdata) >> 3, 1 if fmt == 2 else 0)))
        pflag |= 0x8000 if fmt == 2 else 0          # (nsbtx.merge: a set with a 4-colour palette sets this bit)
        pal = pal + [0] * ({1: 32, 2: 4, 3: 16}[fmt] - len(pal))    # whole palettes (the next one stays aligned)
        pdata += b''.join(struct.pack('<H', c) for c in pal)
    while len(pdata) % 8: pdata.append(0)
    tdict, pdict = nsbtx.dict_build(texs, 8), nsbtx.dict_build(pals, 4)
    o_tdict = 0x3C; o_pdict = o_tdict + len(tdict); o_tex = o_pdict + len(pdict)
    o_c = o_tex + len(texdata); o_p = o_c
    size = o_p + len(pdata)
    hdr = bytearray(0x3C)
    hdr[0:4] = b'TEX0'
    struct.pack_into('<I', hdr, 4, size)
    struct.pack_into('<HH', hdr, 0xC, len(texdata) >> 3, o_tdict); struct.pack_into('<I', hdr, 0x14, o_tex)
    struct.pack_into('<HH', hdr, 0x1C, 0, o_tdict); struct.pack_into('<II', hdr, 0x24, o_c, o_c)
    struct.pack_into('<HH', hdr, 0x30, len(pdata) >> 3, pflag); struct.pack_into('<H', hdr, 0x34, o_pdict)
    struct.pack_into('<I', hdr, 0x38, o_p)
    return bytes(hdr) + tdict + pdict + bytes(texdata) + bytes(pdata)

def blocks(bmd):
    nb = struct.unpack_from('<H', bmd, 0xE)[0]
    offs = [struct.unpack_from('<I', bmd, 0x10 + 4 * k)[0] for k in range(nb)] + [len(bmd)]
    return {bmd[offs[k]:offs[k] + 4]: bmd[offs[k]:offs[k + 1]] for k in range(nb)}

def bmd0(mdl0, tex0):
    """One BMD0 file with an MDL0 and a TEX0 block (Black 2's actor model layout)."""
    while len(mdl0) % 4: mdl0 += b'\0'
    head = 0x10 + 8
    return struct.pack('<4sHHIHHII', b'BMD0', 0xFEFF, 2, head + len(mdl0) + len(tex0), 0x10, 2, head,
                       head + len(mdl0)) + mdl0 + tex0

def to_mdl0(model, textures, vcol=True, wrap=None):
    """MDL0 block of a dae.Model through ToNsbmd (textures: {name: rgba array or PIL image} written beside the DAE
    for its sizes)."""
    with tempfile.TemporaryDirectory() as t:
        for name, rgba in textures.items():
            (rgba if isinstance(rgba, Image.Image) else Image.fromarray(rgba, 'RGBA')).save(os.path.join(t, name + '.png'))
        model.write(os.path.join(t, 'm.dae'), wrap=wrap)
        open(os.path.join(t, 'pal.txt'), 'w').write(''.join(f'{n} {n}_pl\n' for n in textures))
        jd = os.path.join(ROOT, 'work', 'java')            # rebuild_slice.sh compiles b2tools/java there
        if not os.path.exists(os.path.join(jd, 'ToNsbmd.class')):
            jd = os.path.join(t, 'java')
            subprocess.run(['javac', '-cp', CP, '-d', jd, os.path.join(HERE, 'java', 'ToNsbmd.java')], check=True)
        args = ['java', '-Djava.awt.headless=true', '-cp', jd + ':' + CP, 'ToNsbmd'] + (['--vcol'] if vcol else []) + \
               [os.path.join(t, 'm.dae'), os.path.join(t, 'm.nsbmd'), os.path.join(t, 'pal.txt')]
        subprocess.run(args, check=True, capture_output=True)
        return blocks(open(os.path.join(t, 'm.nsbmd'), 'rb').read())[b'MDL0']

def set_material_alpha(mdl0, alpha, only=None):
    """Every material of an MDL0 block drawn with polygon alpha `alpha` (0-31; PolygonAttr bits 16-20, which the
    material's mask 0x3f1ff8ff applies): the polygon goes into the DS's translucent list."""
    b = bytearray(mdl0)
    for _, ent in nsbtx._dict(b, 8):
        model = struct.unpack_from('<I', ent, 0)[0]
        mats = model + struct.unpack_from('<I', b, model + 8)[0]
        for mname, e in nsbtx._dict(b, mats + 4):
            if only and mname not in only: continue
            o = mats + struct.unpack_from('<I', e, 0)[0]
            poly = struct.unpack_from('<I', b, o + 12)[0]
            struct.pack_into('<I', b, o + 12, (poly & ~(31 << 16)) | (alpha << 16))
    return bytes(b)

FILES = os.path.join(ROOT, 'external', 'pokebw2', 'extract', 'b2_us', 'files')

def material_textures(bmd):
    """{material name: texture name} of a BMD0's first model (MDL0 texture -> material dictionary)."""
    m0 = blocks_at(bmd)[b'MDL0']
    mo = m0 + struct.unpack_from('<I', nsbtx._dict(bmd, m0 + 8)[0][1], 0)[0]
    mats = mo + struct.unpack_from('<I', bmd, mo + 8)[0]
    names = [n for n, _ in nsbtx._dict(bmd, mats + 4)]
    tex_d = struct.unpack_from('<H', bmd, mats)[0]
    out = {}
    for tname, e in nsbtx._dict(bmd, mats + tex_d):
        off, n = struct.unpack_from('<HB', e, 0)
        for i in range(n): out[names[bmd[mats + off + i]]] = tname
    return out

def btx0(tex0):
    return struct.pack('<4sHHIHHI', b'BTX0', 0xFEFF, 1, 0x14 + len(tex0), 0x10, 1, 0x14) + tex0

def drop_shapes(bmd, materials):
    """Remove the geometry drawn with the named materials from a BMD0's single model: each such shape's display list
    is cut out (size 0) and its SBC draw command becomes NOPs, and every offset behind it moves down (later shapes' list offsets, the model
    size and envelope offset, the MDL0 block, the file and its later blocks). The materials stay (unused). Returns the
    new bytes. Used to leave a Black 2 model's wake ring off a docked boat: its list and texture are bytes the field
    heap holds for as long as the boat is in the zone (patches/area2_buildings.py: the menu save needs that heap)."""
    b = bytearray(bmd)
    m0 = blocks_at(b)[b'MDL0']
    ents = nsbtx._dict(b, m0 + 8)
    assert len(ents) == 1, 'one model only'
    mo = m0 + struct.unpack_from('<I', ents[0][1], 0)[0]
    sbc, mat, shp = struct.unpack_from('<III', b, mo + 4)
    names = [n for n, _ in nsbtx._dict(b, mo + mat + 4)]
    code, pairs, i = b[mo + sbc:mo + mat], [], 0
    while i < len(code):          # SBC: MAT (0x04 m) then SHP (0x05 s); other commands skipped by their lengths
        op = code[i]
        if op == 0x04: cur = code[i + 1]; i += 2
        elif op == 0x05: pairs.append((cur, code[i + 1])); i += 2
        elif op == 0x01: break
        else: i += {0x00: 1, 0x02: 3, 0x03: 2, 0x06: 4, 0x26: 5, 0x46: 5, 0x66: 6, 0x07: 2, 0x08: 2, 0x0b: 1, 0x2b: 1, 0x0c: 3,
                    0x0d: 3, 0x24: 2, 0x44: 2, 0x47: 2, 0x48: 2}[op]
    drop = {s_ for m_, s_ in pairs if names[m_] in materials}
    i = 0                         # the SBC's draw command of each dropped shape (05 s) -> two NOPs (patches/boat_demos.py):
    while i < len(code):          # the game would still send a 0-byte display list otherwise (tested: the hull broke up)
        op = code[i]
        if op == 0x05 and code[i + 1] in drop: b[mo + sbc + i:mo + sbc + i + 2] = b'\0\0'
        if op == 0x01: break
        i += {0x00: 1, 0x02: 3, 0x03: 2, 0x04: 2, 0x05: 2, 0x06: 4, 0x26: 5, 0x46: 5, 0x66: 6, 0x07: 2, 0x08: 2, 0x0b: 1,
              0x2b: 1, 0x0c: 3, 0x0d: 3, 0x24: 2, 0x44: 2, 0x47: 2, 0x48: 2}[op]
    shapes = [(sn, shp + struct.unpack_from('<I', se, 0)[0]) for sn, se in nsbtx._dict(b, mo + shp)]
    cuts = []
    for k, (sn, so) in enumerate(shapes):
        dlo, dls = struct.unpack_from('<II', b, mo + so + 8)
        if k in drop and dls: cuts.append((mo + so + dlo, dls, k))
    for start, size, k in sorted(cuts, reverse=True):
        del b[start:start + size]
        for kk, (sn, so) in enumerate(shapes):
            rec = mo + so
            dlo, dls = struct.unpack_from('<II', b, rec + 8)
            if kk == k: struct.pack_into('<II', b, rec + 8, dlo, 0)
            elif rec + dlo > start: struct.pack_into('<I', b, rec + 8, dlo - size)
        msize, evp = struct.unpack_from('<I', b, mo)[0], struct.unpack_from('<I', b, mo + 16)[0]
        struct.pack_into('<I', b, mo, msize - size)
        if evp >= msize: struct.pack_into('<I', b, mo + 16, evp - size)
        struct.pack_into('<I', b, m0 + 4, struct.unpack_from('<I', b, m0 + 4)[0] - size)
        struct.pack_into('<I', b, 8, struct.unpack_from('<I', b, 8)[0] - size)
        nb = struct.unpack_from('<H', b, 0xE)[0]
        for kb in range(nb):
            o = struct.unpack_from('<I', b, 0x10 + 4 * kb)[0]
            if o > start: struct.pack_into('<I', b, 0x10 + 4 * kb, o - size)
    return bytes(b)

def black2_model(pack, res, scale, exterior=True, turns=0, drop=()):
    """A Black 2 building model as a 3D-object BMD0: its MDL0 byte for byte with the position scale times `scale`
    (patches/boulder_1x1.py's scaled_bmd: posScale, invPosScale and the box scales of every model), and a TEX0 with the
    textures and palettes its materials use, copied byte for byte from the pack's texture set (nsbtx.merge)."""
    import b2files
    sys.path.insert(0, os.path.join(HERE, 'patches'))
    from boulder_1x1 import scaled_bmd
    r = next(x for x in b2files.building_pack(FILES, pack, exterior=exterior) if x['res_id'] == res)
    bmd = rotate_bmd(scaled_bmd(r['bmd'], scale) if scale != 1 else r['bmd'], turns)
    tex = b2files.building_textures(FILES, pack, exterior=exterior)
    pairs = sorted(nsbtx.material_pairs(bmd))
    base = btx0(tex0_block([]))
    if drop:                      # the dropped materials' textures: an 8x8 clear stand-in (the binding needs the name)
        mats = {m: t for m, t in material_textures(bmd).items()}
        gone = {mats[m] for m in drop}
        # (16 colours: its 32-byte palette keeps the next palette on a 16-byte boundary, which 16-colour palettes
        # need; a 4-colour stand-in put the hull's palette at 8 and the boat came out in wrong colours, tested)
        base = btx0(tex0_block([(t, np.zeros((8, 8, 4), np.uint8), 3) for t in sorted(gone)]))
        bmd = drop_shapes(bmd, set(drop))
        pairs = [(t, p) for t, p in pairs if t not in gone]
    merged = nsbtx.merge(base, [(tex, t, p) for t, p in pairs])
    return bmd0(blocks(bmd)[b'MDL0'], blocks(merged)[b'TEX0']), r['name']

_PARAMS = {0x10: 1, 0x11: 0, 0x12: 1, 0x13: 1, 0x14: 1, 0x15: 0, 0x16: 16, 0x17: 12, 0x18: 16, 0x19: 12, 0x1a: 9, 0x1b: 3,
           0x1c: 3, 0x20: 1, 0x21: 1, 0x22: 1, 0x23: 2, 0x24: 1, 0x25: 1, 0x26: 1, 0x27: 1, 0x28: 1, 0x29: 1, 0x2a: 1,
           0x2b: 1, 0x30: 1, 0x31: 1, 0x32: 1, 0x33: 1, 0x34: 32, 0x40: 1, 0x41: 0, 0x50: 1, 0x60: 1, 0x70: 3, 0x71: 2,
           0x72: 1}                     # GX geometry commands: parameter words (GBATEK "DS 3D Geometry Commands")

def _s(v, bits):
    v &= (1 << bits) - 1
    return v - (1 << bits) if v >> (bits - 1) else v

def _neg(v, bits):
    return min(-v, (1 << (bits - 1)) - 1)

def rotate_bmd(bmd, turns):
    """Every model of a BMD0 turned `turns` quarter turns clockwise seen from above (north -> east; x east, z south):
    each shape's display list is rewritten in place (VTX_16 / VTX_XY / VTX_XZ / VTX_YZ / NORMAL; a command that sets
    two coordinates and keeps the third becomes the one that does the same in the turned frame) and the model's
    bounding box (model info, used for culling) is turned with it. Lossless: same size, same everything else. Models
    whose nodes carry a transform or whose lists hold VTX_10 are refused (VTX_DIFF is turned like NORMAL)."""
    turns %= 4
    if not turns: return bmd
    b = bytearray(bmd)
    m0 = blocks_at(b)[b'MDL0']
    def rot(x, z, n):
        for _ in range(n): x, z = _neg(z, 16), x
        return x, z
    for _, ent in nsbtx._dict(b, m0 + 8):
        mo = m0 + struct.unpack_from('<I', ent, 0)[0]
        shp = mo + struct.unpack_from('<I', b, mo + 12)[0]
        info = mo + 0x14
        for _, ne in nsbtx._dict(b, info + 0x2C):
            no = info + 0x2C + struct.unpack_from('<I', ne, 0)[0]
            assert struct.unpack_from('<H', b, no)[0] & 7 == 7, 'node with a transform'
        bx, by, bz, bw, bh, bd = struct.unpack_from('<6h', b, info + 24)
        for _ in range(turns): bx, bz, bw, bd = -(bz + bd), bx, bd, bw
        struct.pack_into('<6h', b, info + 24, bx, by, bz, bw, bh, bd)
        for _, se in nsbtx._dict(b, shp):
            so = shp + struct.unpack_from('<I', se, 0)[0]
            dlo, dls = struct.unpack_from('<II', b, so + 8)
            i, end = so + dlo, so + dlo + dls
            while i < end:
                ops = list(b[i:i + 4]); at = i; i += 4
                for k, op in enumerate(ops):
                    if op == 0: continue
                    n = _PARAMS[op]
                    assert op != 0x24, f'vertex command {op:#x} not handled'
                    if op == 0x23:            # VTX_16: x | y << 16, z
                        x, y = struct.unpack_from('<hh', b, i); z = struct.unpack_from('<h', b, i + 4)[0]
                        x, z = rot(x, z, turns)
                        struct.pack_into('<hh', b, i, x, y); struct.pack_into('<h', b, i + 4, z)
                    elif op in (0x25, 0x26, 0x27):
                        a, c = struct.unpack_from('<hh', b, i)
                        for _ in range(turns):          # one quarter turn: x' = -z, z' = x
                            if op == 0x25: op, a, c = 0x27, c, a           # XY (z kept)  -> YZ (y, z' = x)
                            elif op == 0x26: op, a, c = 0x26, _neg(c, 16), a   # XZ -> XZ (-z, x)
                            else: op, a, c = 0x25, _neg(c, 16), a          # YZ (x kept) -> XY (x' = -z, y)
                        b[at + k] = op
                        struct.pack_into('<hh', b, i, a, c)
                    elif op in (0x21, 0x28):  # NORMAL / VTX_DIFF: 10-bit x, y, z
                        w = struct.unpack_from('<I', b, i)[0]
                        x, y, z = _s(w, 10), _s(w >> 10, 10), _s(w >> 20, 10)
                        for _ in range(turns): x, z = _neg(z, 10), x
                        struct.pack_into('<I', b, i, (w & ~0x3FFFFFFF) | (x & 1023) | ((y & 1023) << 10) | ((z & 1023) << 20))
                    i += 4 * n
    return bytes(b)

def blocks_at(bmd):
    nb = struct.unpack_from('<H', bmd, 0xE)[0]
    offs = [struct.unpack_from('<I', bmd, 0x10 + 4 * k)[0] for k in range(nb)]
    return {bytes(bmd[o:o + 4]): o for o in offs}

# ---------------------------------------------------------------------------------------------------- objects

def submarine_shadow():
    idx, rgba, cols = sapphire_pic('misc/submarine_shadow.png', 26)
    h, w = idx.shape                                   # 32 x 88
    # Gen 3's checkerboard -> solid: every clear pixel with set pixels left and right (or above and below) takes
    # their colour (the ring colour 6 where it touches a 6, else the inside colour 7)
    fill = idx.copy()
    for y in range(h):
        for x in range(w):
            if idx[y, x]: continue
            n = [idx[y, x - 1] if x else 0, idx[y, x + 1] if x + 1 < w else 0, idx[y - 1, x] if y else 0,
                 idx[y + 1, x] if y + 1 < h else 0]
            if (n[0] and n[1]) or (n[2] and n[3]):
                fill[y, x] = 6 if 6 in n else 7
    tex = np.zeros((32, 128, 4), np.uint8)
    for i in (6, 7):
        tex[:h, :w][fill == i] = cols[i] + (255,)
    name = 'subshadow'
    m = Model('subshadow')
    # Sapphire: sprite centre x = tile centre, bottom = tile's south edge -> x -44..44, z -24..8 from the tile centre
    x0, x1, z0, z1, y = -44, 44, -24, 8, 0.5
    u1 = w / 128
    m.quad(name, [(x0, y, z0, 0, 1), (x0, y, z1, 0, 0), (x1, y, z1, u1, 0), (x1, y, z0, u1, 1)])
    mdl = set_material_alpha(to_mdl0(m, {name: tex}), SHADOW_ALPHA)
    return dict(bmd=bmd0(mdl, tex0_block([(name, tex, 2)])), texture=tex, source=rgba)

SHADOW_ALPHA = 16       # of 31: about half, as Gen 3's checkerboard
SUBCAVE_LEAN = 25       # degrees back from upright: the seafloor submarine faces the camera but keeps clear of the rock
                        # face behind it (row 3; data/cave_layouts/Underwater_SeafloorCavern.json opens row 4 as seabed)

def _metatile_layer(mr, m, layer):
    """One layer of a Gen 3 metatile as RGBA (colour 0 clear), from converter/gba.py's MetatileRenderer data."""
    src = mr.p['mt'] if m < 512 else mr.s['mt']
    i = m if m < 512 else m - 512
    out = np.zeros((16, 16, 4), np.uint8)
    for q in range(4):
        e = int(src[i][layer * 4 + q])
        t, hf, vf, pal = e & 0x3FF, (e >> 10) & 1, (e >> 11) & 1, (e >> 12) & 0xF
        px = mr.tile(t)
        if hf: px = px[:, ::-1]
        if vf: px = px[::-1, :]
        rgb = mr.pals[pal][px]; mask = px != 0
        oy, ox = (q // 2) * 8, (q % 2) * 8
        reg = out[oy:oy + 8, ox:ox + 8]; reg[mask, :3] = rgb[mask]; reg[mask, 3] = 255
    return out

def seafloor_submarine():
    """The stolen submarine in Underwater_SeafloorCavern. Sapphire draws it in the map: the top layer of metatiles
    0x2e4-0x2e7 (row 3) over 0x2e0-0x2e3 (row 4) at x 5-8 is the submarine alone (64x32, colour 0 clear), the bottom layer
    of rows 4-5 holds its dark rounded shadow on the sea floor; setmetatile turns rows 3-4 into rock wall / floor once the
    legend escaped. Here: the 64x32 picture on a quad standing on the row 4 / 5 edge and leaning back SUBCAVE_LEAN
    degrees toward the room camera (about 45 degrees down, b2tools/preview_interior.py), its top still inside row 4, in
    open water in front of row 3's rock (the cave recipe makes the hull tiles seabed, as Sapphire's FloorShadow after the
    legend escaped), and the shadow (Sapphire's shadow rectangle in its outline colour) flat on the seabed at 12/31.
    Origin: the centre of tile (5,4); the record's collision is 4 x 1 tiles (collWidth runs east), the hull tiles (5..8,4)
    that Sapphire's four invisible objects block; the NPC runs the hull signs' script (talking finds it first)."""
    sys.path.insert(0, os.path.join(ROOT, 'converter'))
    from gba import Repo, MetatileRenderer
    import math
    r = Repo(os.path.join(ROOT, 'external', 'pokeruby'))
    mj = r.map_json('Underwater_SeafloorCavern'); g, lay = r.layout_grid(mj['layout'])
    mr = MetatileRenderer(r, lay['primary_tileset'], lay['secondary_tileset'])
    assert [int(g[3, x]) & 0x3FF for x in range(5, 9)] == [0x2e4, 0x2e5, 0x2e6, 0x2e7]
    assert [int(g[4, x]) & 0x3FF for x in range(5, 9)] == [0x2e0, 0x2e1, 0x2e2, 0x2e3]
    sub = np.zeros((32, 64, 4), np.uint8)
    for k in range(4):
        sub[0:16, 16 * k:16 * k + 16] = _metatile_layer(mr, 0x2e4 + k, 1)
        sub[16:32, 16 * k:16 * k + 16] = _metatile_layer(mr, 0x2e0 + k, 1)
    base = np.zeros((32, 64, 4), np.uint8)            # bottom layer of rows 4-5: the shadow rectangle's outline colour
    for k in range(4):
        base[0:16, 16 * k:16 * k + 16] = _metatile_layer(mr, 0x2e0 + k, 0)
        base[16:32, 16 * k:16 * k + 16] = _metatile_layer(mr, 0x2e8 + k, 0)
    rgb = base[..., :3].reshape(-1, 3)
    dark = min({tuple(int(v) for v in c) for c in rgb}, key=sum)          # (57, 16, 164): the outline
    ys, xs = np.nonzero(np.all(base[..., :3] == dark, axis=-1))
    shadow = np.zeros((32, 64, 4), np.uint8)                              # the outline's box, corners rounded by 2
    y0, y1, xa, xb = ys.min(), ys.max(), xs.min(), xs.max()
    for y in range(y0, y1 + 1):
        cut = max(0, 2 - min(y - y0, y1 - y))
        shadow[y, xa + cut:xb + 1 - cut] = dark + (255,)
    m = Model('subcave')
    x0, x1 = 5 * 16 - (5 * 16 + 8), 9 * 16 - (5 * 16 + 8)               # x 5..8 from tile (5,4)'s centre: -8..56
    zb = 5 * 16 - (4 * 16 + 8)                                            # the row 4 / 5 edge: +8
    lean = math.radians(SUBCAVE_LEAN)
    top_y, top_z = 32 * math.cos(lean), zb - 32 * math.sin(lean)          # the top stays inside row 4: in the water,
    m.quad('subcave', [(x0, 0, zb, 0, 0), (x1, 0, zb, 1, 0), (x1, top_y, top_z, 1, 1), (x0, top_y, top_z, 0, 1)])
    sz0, sz1 = zb - 12, zb + 2                                            # in front of the rock face of row 3; its
    m.quad('subcave_kage', [(x0, 2.5, sz0, 0, 1), (x0, 2.5, sz1, 0, 0), (x1, 2.5, sz1, 1, 0), (x1, 2.5, sz0, 1, 1)])
    # shadow flat on the seabed under the hull (the floor's sand decal lies at 2 units)
    mdl = set_material_alpha(to_mdl0(m, {'subcave': sub, 'subcave_kage': shadow}), 12, only=('subcave_kage',))
    return dict(bmd=bmd0(mdl, tex0_block([('subcave', sub, 3), ('subcave_kage', shadow, 2)])), texture=sub,
                source=sub)

def briney_boat(turns=0):
    bmd, name = black2_model(21, 208, BOAT_SCALE, turns=turns, drop=('h',))   # 'h' = the wake ring (C3Ship_wa)
    return dict(bmd=bmd, texture=None, source=sapphire_pic('misc/mr_brineys_boat.png', '02')[1], b2=name)

def ss_tidal():
    bmd, name = black2_model(54, 318, TIDAL_SCALE, turns=1)
    return dict(bmd=bmd, texture=None, source=sapphire_pic('misc/ss_tidal.png', 21)[1], b2=name)

def truck():
    """Sapphire's moving truck in Littleroot (OBJ_EVENT_GFX_TRUCK, objects 5/6 at (2,10)/(11,10), hidden by
    FLAG_HIDE_MOVING_TRUCK_BRENDAN/_MAY): the same model as before (b2tools/models_truck_ext.py: Black 2 textures only,
    lit by normals as a building), now a 3D object instead of exterior building res 460. A building is part of its
    chunk and BMSetVisible hides it only until the chunk reloads, so the trucks came back whenever the player walked
    into Littleroot again (user report 2026-10-08); an object's spawn flag holds across zone changes and Continue.
    Its textures are copied byte for byte from the Black 2 sets models_truck_ext.SOURCES names (nsbtx.merge)."""
    import models_truck_ext as T, b2files
    from exterior_layers import separate
    m = T.build(); separate(m)
    used = sorted(m.tris)
    images = T.texture_images(used)
    mdl = to_mdl0(m, images, vcol=False, wrap={t: ('CLAMP', 'CLAMP') for t in used})
    adds = []
    for t in used:
        src = b2files.building_textures(FILES, T.SETS[T.SOURCES[t]])
        pals = dict(nsbtx._parse(src)['pals'])
        adds.append((src, t, t + '_pl' if t + '_pl' in pals else next(iter(pals))))
    merged = nsbtx.merge(btx0(tex0_block([])), adds)
    return dict(bmd=bmd0(mdl, blocks(merged)[b'TEX0']), texture=None, source=sapphire_pic('misc/truck.png', '00')[1])

BOAT_SCALE = 0.18       # Black 2's motorboat hull is 213 x 79 units (13 x 5 tiles); Sapphire's boat about 28 x 20 px
TIDAL_SCALE = 0.42      # Black 2's ferry hull 213 x 79 units; Sapphire's S.S. Tidal about 90 x 30 px

OBJECTS = {
    'submarine-shadow': dict(code=0x2000, build=submarine_shadow, record_from=0x2009,
                             what='OBJ_EVENT_GFX_SUBMARINE_SHADOW: the stolen submarine under the water (Slateport '
                                  'Harbor, Aqua Hideout B2F, Magma Hideout B2F)',
                             record={'collWidth': 1, 'collHeight': 1, 'offX': 0, 'offY': 0, 'offZ': 0}),
    'briney-boat': dict(code=0x2001, build=briney_boat, record_from=0x2009,
                        what="OBJ_EVENT_GFX_MR_BRINEYS_BOAT: Mr. Briney's boat docked (Route 104, Dewford, Route 109): "
                             "Black 2's white motorboat c03_ship_04 (exterior pack 21 res 208, the boat of demo 4)",
                        # collision 1 x 2 (collHeight runs north from the boat's tile): the hull's two tiles, so a
                        # surfer cannot sit in its bow (Route 104's cove, Route 109; final_check 2026-10-08)
                        record={'collWidth': 1, 'collHeight': 2, 'offX': 0, 'offY': round(15 * BOAT_SCALE), 'offZ': -8}),
    'briney-boat-south': dict(code=112, build=lambda: briney_boat(2), record_from=0x2009,
                              what="OBJ_EVENT_GFX_MR_BRINEYS_BOAT facing down (Dewford): the same motorboat turned "
                                   "half round (rotate_bmd); a 3D actor never turns with its direction",
                              record={'collWidth': 1, 'collHeight': 2, 'offX': 0, 'offY': round(15 * BOAT_SCALE),
                                      'offZ': -12}),     # bow 4 units off Dewford's jetty; hull rows 7-8 (1 x 2)
    'seafloor-submarine': dict(code=194, build=seafloor_submarine, record_from=0x2009,
                               what='the stolen submarine in Underwater_SeafloorCavern (Sapphire: map metatiles 0x2e0-0x2eb, '
                                    'rock after the legend escaped): its own pixels on a camera-facing quad + its floor shadow',
                               record={'collWidth': 4, 'collHeight': 1, 'offX': 0, 'offY': 0, 'offZ': 0}),
    'truck': dict(code=118, build=truck, record_from=0x2009,
                  what="OBJ_EVENT_GFX_TRUCK: the moving trucks of Brendan's and May's families in Littleroot (models_truck_ext.py's "
                       "model, formerly exterior building res 460)",
                  record={'collWidth': 1, 'collHeight': 1, 'offX': 1, 'offY': 0, 'offZ': 0}),   # (169.56 tiles: 1 unit east)
    'ss-tidal': dict(code=0x2002, build=ss_tidal, record_from=0x2009,
                     what="OBJ_EVENT_GFX_SS_TIDAL: the S.S. Tidal docked (Slateport and Lilycove Harbors, Battle Tower, "
                          "Southern Island): Black 2's ferry c13_ship_01 (exterior pack 54 res 318, Virbank's ferry)",
                     record={'collWidth': 1, 'collHeight': 1, 'offX': 0, 'offY': round(15 * TIDAL_SCALE), 'offZ': -12}),
}

# ---------------------------------------------------------------------------------------------------- billboards
# Small objects Black 2 draws as one-frame billboards (controller 4; Black 2's Poke Ball 110 stands 9 px tall on rows
# 22-30 of its 32x32 frame, the ground point at the frame's bottom centre). Sapphire's own picture goes in 1:1 (a
# Sapphire pixel is a Black 2 unit, as for the 3D objects; Sapphire's items are already a little bigger than Black 2's)
# with its own 15 colours, its bottom row on row 30 (64x64: row 62) and centred, into an unused Black 2 one-frame sheet
# of the same size (src/sprites/overworld/<code>-<name>/, installed in place by patches/sprites.py; the sheet keeps
# its size). Donors: codes no Hoenn data, no Black 2 zone and no Black 2 script of a kept place uses (checked
# 2026-10-08: data/story, data/interiors, hoenn_content/trainer_npcs/world json, a/1/2/6 zone NPCs, ActorNew and the
# WKOBJCODE works 0x4020-0x402F in Black 2's scripts): 292 (a blue Poke Ball, used nowhere), 143 (a grey ball, set
# only by Black 2 script 0034 through work 0x4020: a Unova scene), 356 (Regigigas, 64x64, Black 2 zone 253 only);
# 208 (the gift box, already Birch's bag) gets Sapphire's own bag instead of the earlier hand-drawn satchel
# (sprite_art.py "bag", now superseded: the user wants Sapphire's pixels, never redraws).

BILLBOARDS = {
    'birchs-bag': dict(code=208, pic='misc/birchs_bag.png', pal='01', size=32, donor='gift box 208',
                       what="OBJ_EVENT_GFX_BIRCHS_BAG: Prof. Birch's bag on Route 101"),
    'fossil': dict(code=292, pic='misc/fossil.png', pal='00', size=32, donor='blue Poke Ball 292 (unused)',
                   what='OBJ_EVENT_GFX_FOSSIL: the Root and Claw Fossils in the Route 111 desert'),
    'pichu-doll': dict(code=143, pic='dolls/pichu_doll.png', pal='01', size=32, donor='grey ball 143 (unused in Hoenn)',
                       what="OBJ_EVENT_GFX_PICHU_DOLL: the Pichu Doll in May's room"),
    'cable-car': dict(code=356, pic='misc/cable_car.png', pal='20', size=64, donor='Regigigas 356 (64x64, unused in Hoenn)',
                      what='OBJ_EVENT_GFX_CABLE_CAR: the cable car waiting at both stations'),
}

def billboard(name):
    o = BILLBOARDS[name]
    idx, rgba, cols = sapphire_pic(o['pic'], o['pal'])
    h, w = idx.shape
    ys, xs = np.nonzero(idx)
    used = sorted(set(idx[idx > 0].tolist()))
    assert len(used) <= 15
    size = o['size']
    frame = np.zeros((size, size), np.uint8)
    look = {c: i + 1 for i, c in enumerate(used)}
    x0 = (size - w) // 2
    y0 = (size - 2) - (ys.max() + 1)            # the picture's lowest pixel on row size-2
    for y, x in zip(ys, xs):
        frame[y0 + y, x0 + x] = look[int(idx[y, x])]
    pal = [cols[0]] + [cols[c] for c in used] + [(0, 0, 0)] * (15 - len(used))
    d = os.path.join(ROOT, 'src', 'sprites', 'overworld', f'{o["code"]:03d}-{name}')
    os.makedirs(d, exist_ok=True)
    im = Image.fromarray(frame, 'P')
    im.putpalette([v for c in pal for v in c] + [0] * (768 - 48))
    im.save(os.path.join(d, 'frame_00.png'), transparency=0)
    open(os.path.join(d, 'palette.pal'), 'w').write('JASC-PAL\n0100\n16\n' + ''.join(f'{r} {g} {b}\n' for r, g, b in pal))
    sheet = {32: 't4x4x1', 64: 't8x8x1'}[size]
    import sprites
    res1, _ = sprites.ow_sheet_of(FILES, o['code'], sprites.ow_table(FILES))
    meta = dict(kind='overworld', code=o['code'], sheet=res1, frames=1, size=[size, size], controller=4,
                textures=[sheet + '.0'], palette=sheet, name=name, donor=o['donor'], note=o['what'],
                sapphire=f'pokeruby graphics/object_events/pics/{o["pic"]}, palette {o["pal"]}',
                made_by='b2tools/models_objects.py (Sapphire\'s pixels 1:1)')
    json.dump(meta, open(os.path.join(d, 'sprite.json'), 'w'), indent=1)
    return d

# ---------------------------------------------------------------------------------------------------- berry trees
# User decision 2026-10-08: each daily berry spot (converter/gen_hidden_items.py) shows Sapphire's own fully grown tree
# for its berry, hidden once picked until the next day. Sapphire's tree for berry b: gBerryTreePicTablePointers[b]
# (several berries share a picture: Bluk = Razz's, Nanab = Mago's, Pinap = Iapapa's, Qualot = Wepear's), its berry
# stage = pic frames 7/8 = frames 4/5 of berry_trees/<tree>.png (6 frames of 16x32; anim 8370D68 sways between them),
# drawn in OBJ palette slot gBerryTreePaletteSlotTablePointers[b][4]: slot k (2-5 here) holds the field's palette k - 2
# (gObjectPaletteTags0: slot k <- OBJ_EVENT_PAL_TAG_*, tags 0x1103.. = palettes 00..). Frame 4 with its own palette,
# through sprite_upgrade.py's resize (axis_map + rescale) at TREE_SCALE, the Gen 3 frame centred and bottom-aligned.
# Sheets: unused Black 2 12-frame people sheets (controller 3; no Hoenn data, Black 2 zone NPC, ActorNew, WKOBJCODE work,
# PWT record or trainer class uses them: checked 2026-10-08). One sheet has one palette, so a sheet holds up to four
# trees of the same Sapphire palette, one per facing (frames 0-2 up, 3-5 down, 6-8 left, 9-11 right): a static NPC shows
# its facing's standing frame and Black 2 turns NPCs only by script (ActorSetEyeToEye), which the berry script doesn't.
# data/berry_tree_sprites.json: berry item -> [code, facing] for gen_hidden_items.py.

TREE_CODES = [90, 102, 106, 111, 113, 114, 180, 204]
TREE_SCALE = 1      # Sapphire's trees already reach 30 of the Gen 3 frame's 32 rows (Liechi rows 0-29), and Black 2's
                    # frame is 32 rows too: the largest uniform sprite_upgrade scale that keeps every tree whole is 1

def berry_trees(spot_items):
    import re as _re
    sys.path.insert(0, HERE)
    import sprite_upgrade as su
    pr = os.path.join(ROOT, 'external', 'pokeruby')
    tab = open(os.path.join(pr, 'src', 'data', 'object_events', 'berry_tree_graphics_tables.h')).read()
    pics = _re.findall(r'gObjectEventPicTable_(\w+)BerryTree,', tab.split('gBerryTreePicTablePointers[]')[1].split('};')[0])
    slots_of = _re.findall(r'gBerryTreePaletteSlotTable_(\w+),', tab.split('gBerryTreePaletteSlotTablePointers[]')[1].split('};')[0])
    slot_tab = {m.group(1): [int(x) for x in m.group(2).split(',')]
                for m in _re.finditer(r'gBerryTreePaletteSlotTable_(\w+)\[\] = \{([^}]*)\}', tab)}
    consts = open(os.path.join(pr, 'include', 'constants', 'items.h')).read()
    ids = {m.group(1): int(m.group(2)) for m in _re.finditer(r'#define (ITEM_\w+_BERRY) (\d+)', consts)}
    trees = {}                                   # tree picture -> (palette, [berry items])
    for it in sorted(spot_items):
        b = ids[it] - ids['ITEM_CHERI_BERRY']
        pic, pal = pics[b], f'{slot_tab[slots_of[b]][4] - 2:02d}'           # slot k >= 2 holds palette k - 2
        trees.setdefault(pic, (pal, []))[1].append(it)
    sheets, assign = [], {}
    for pal in sorted({pl for pl, _ in trees.values()}):
        group = sorted(p for p, (pl, _) in trees.items() if pl == pal)
        for i in range(0, len(group), 4): sheets.append((pal, group[i:i + 4]))
    assert len(sheets) <= len(TREE_CODES), f'{len(sheets)} tree sheets, {len(TREE_CODES)} codes'
    import sprites
    folders = []
    for (pal, group), code in zip(sheets, TREE_CODES):
        lines = open(os.path.join(PR, 'palettes', f'{pal}.pal')).read().split('\n')[3:19]
        cols = [tuple(int(v) for v in l.split()) for l in lines]
        pictures = []
        for pic in group:
            idx = np.array(Image.open(os.path.join(PR, 'pics', 'berry_trees', pic.lower() + '.png')))[:, 64:80]
            H = round(32 * TREE_SCALE); W = round(16 * TREE_SCALE)       # the whole Gen 3 frame, one scale for all
            big = su.rescale(idx, su.axis_map(16, W), su.axis_map(32, H)) if TREE_SCALE != 1 else idx
            frame = np.zeros((32, 32), np.uint8)
            x0 = (32 - W) // 2
            frame[32 - H:32, x0:x0 + W] = big          # the Gen 3 frame's bottom = the tile's south edge, as Sapphire
            pictures.append(frame)
            for it in trees[pic][1]: assign[it] = [code, len(pictures) - 1]
        while len(pictures) < 4: pictures.append(pictures[-1])
        d = os.path.join(ROOT, 'src', 'sprites', 'overworld', f'{code:03d}-berry-trees-{len(folders) + 1}')
        os.makedirs(d, exist_ok=True)
        flat = [v for c in cols for v in c] + [0] * (768 - 48)
        for f in range(12):
            im = Image.fromarray(pictures[f // 3], 'P'); im.putpalette(flat); im.save(os.path.join(d, f'frame_{f:02d}.png'), transparency=0)
        open(os.path.join(d, 'palette.pal'), 'w').write('JASC-PAL\n0100\n16\n' + ''.join(f'{r} {g} {b}\n' for r, g, b in cols))
        res1, rec = sprites.ow_sheet_of(FILES, code, sprites.ow_table(FILES))
        meta = dict(kind='overworld', code=code, sheet=res1, frames=12, size=[32, 32], controller=3,
                    textures=[f't4x4x12.{i}' for i in range(12)], palette='t4x4x12', name=f'berry-trees-{len(folders) + 1}',
                    donor=f'unused Black 2 sheet {code}', note='Sapphire berry trees (berry stage), one per facing: '
                    + ', '.join(f'{["up", "down", "left", "right"][i]} {g}' for i, g in enumerate(group)),
                    sapphire=f'pokeruby graphics/object_events/pics/berry_trees/*.png frame 4, palette {pal}',
                    made_by='b2tools/models_objects.py berry_trees (sprite_upgrade resize)')
        json.dump(meta, open(os.path.join(d, 'sprite.json'), 'w'), indent=1)
        folders.append(d)
    json.dump({'_doc': 'Generated by b2tools/models_objects.py berry_trees: berry item -> [object code, facing (0 up, '
                       '1 down, 2 left, 3 right)] of its Sapphire tree picture; converter/gen_hidden_items.py places them.',
               'trees': dict(sorted(assign.items()))}, open(os.path.join(ROOT, 'data', 'berry_tree_sprites.json'), 'w'), indent=1)
    return folders

def build(name):
    o = OBJECTS[name]
    r = o['build']()
    d = os.path.join(OUT, f'{o["code"]:04x}-{name}')
    os.makedirs(d, exist_ok=True)
    open(os.path.join(d, 'model.nsbmd'), 'wb').write(r['bmd'])
    if r.get('texture') is not None: Image.fromarray(r['texture'], 'RGBA').save(os.path.join(d, 'texture.png'))
    if r.get('source') is not None: Image.fromarray(r['source'], 'RGBA').save(os.path.join(d, 'source.png'))
    meta = dict(code=o['code'], name=name, what=o['what'], record_from=o['record_from'], record=o['record'],
                made_by='b2tools/models_objects.py')
    json.dump(meta, open(os.path.join(d, 'object.json'), 'w'), indent=1)
    return d, len(r['bmd'])

if __name__ == '__main__':
    names = sys.argv[1:] or list(OBJECTS) + list(BILLBOARDS) + ['berry-trees']
    if 'berry-trees' in names:
        spots = json.load(open(os.path.join(ROOT, 'data', 'hoenn_berry_spots.json')))['spots'].values()
        print(*berry_trees({v['item'] for v in spots}), sep='\n')
        names = [n for n in names if n != 'berry-trees']
    for n in names:
        print(*build(n)) if n in OBJECTS else print(billboard(n))
