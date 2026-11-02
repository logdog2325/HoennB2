"""The Berry Blender's and the Pokéblock Case's data for archive 271 (b2tools/contest_data.py MEMBERS): Gen 3's pictures from
pokeemerald's graphics (the same as pokeruby's), Gen 3's Berry flavors (the same in both)."""
import os, re, struct

import contest_data as cd


def blender():
    g = os.path.join(cd.EMERALD, 'graphics/berry_blender')
    center = cd._png(os.path.join(g, 'center.png'))    # 8bpp tiles, as the GBA's: an affine BG, the disc turns
    outer = cd._png(os.path.join(g, 'outer.png'))
    w, h = center.size
    px = center.tobytes()
    tiles8 = b''.join(px[(ty + y) * w + tx:(ty + y) * w + tx + 8] for ty in range(0, h, 8) for tx in range(0, w, 8) for y in range(8))
    assert len(tiles8) <= 0x2000
    chars = tiles8.ljust(0x2000, b'\0') + cd._tiles4(outer).ljust(0x2000, b'\0')
    cmap = open(os.path.join(g, 'center_map.bin'), 'rb').read()
    # Gen 3's affine map as it is (one byte a tile, 32x32); the outer one uses Gen 3's palette 8
    center_map = cmap[:0x400].ljust(0x800, b'\0')
    outer_map = open(os.path.join(g, 'outer_map.bin'), 'rb').read()
    pal = (cd._pal555(center, 16) + [0] * 256)[:256]
    pal[8 * 16:9 * 16] = cd._pal555(outer, 16)
    # OBJ: the marker (a score symbol's star), the four player arrows' first frames, the three score symbols
    arrow = cd._png(os.path.join(g, 'arrow.png'))
    score = cd._png(os.path.join(g, 'score_symbols.png'))
    raw = bytearray()
    cells = []
    def add(data):
        t = len(raw) // 32
        raw.extend(data)
        return t
    s = cd._tiles4(score)
    a = cd._tiles4(arrow)
    t = add(s[:32 * 4])
    cells.append([(-8, -8, 16, 16, t, 1)])                     # BSEQ_MARKER
    t = add(a)
    for i in range(4):                                         # BSEQ_PLAYER_0..3: the arrow's frames, 32x32 each
        cells.append([(-16, -16, 32, 32, t + 16 * i, 0)])
    t = add(s)
    for i in range(3):                                         # BSEQ_SCORE_0..2
        cells.append([(-8, -8, 16, 16, t + 4 * i, 1)])
    obj_pal = cd._pal555(arrow, 16) + cd._jasc(os.path.join(g, 'misc.pal'))[:16]
    return dict(BLEND_CHARS=chars, BLEND_PAL=struct.pack('<256H', *pal), BLEND_MAP=center_map + outer_map,
                BLEND_OBJ_CHARS=cd.ncgr(bytes(raw)), BLEND_OBJ_PLTT=cd.nclr(obj_pal),
                BLEND_OBJ_CELLS=cd.ncer(cells), BLEND_OBJ_ANIMS=cd.nanr(len(cells)))


def case():
    g = os.path.join(cd.EMERALD, 'graphics/pokeblock')
    menu = cd._png(os.path.join(g, 'menu.png'))
    pal = (cd._jasc(os.path.join(g, 'menu.pal')) + [0] * 256)[:256]
    device = cd._png(os.path.join(g, 'device.png'))
    return dict(BLOCK_CHARS=cd._tiles4(menu), BLOCK_PAL=struct.pack('<256H', *pal),
                BLOCK_MAP=open(os.path.join(g, 'menu.bin'), 'rb').read(),
                BLOCK_OBJ_CHARS=cd.ncgr(cd._tiles4(device)), BLOCK_OBJ_PLTT=cd.nclr(cd._pal555(device, 16)),
                BLOCK_OBJ_CELLS=cd.ncer([[(-32, -32, 64, 64, 0, 0)]]), BLOCK_OBJ_ANIMS=cd.nanr(1))


def berry_table(decomp=None):
    """gBerries' flavors in Gen 3's order: 43 x (spicy, dry, sweet, bitter, sour, smoothness)."""
    src = open(os.path.join(decomp or cd.EMERALD, 'src/berry.c')).read()
    rows = re.findall(r'\.spicy = (\d+),\s*\.dry = (\d+),\s*\.sweet = (\d+),\s*\.bitter = (\d+),\s*\.sour = (\d+),\s*\.smoothness = (\d+)', src)
    assert len(rows) >= 43, len(rows)
    return b''.join(bytes(int(x) for x in r) for r in rows[:43])


def members():
    d = {}
    d.update(blender())
    d.update(case())
    d['BERRY_TABLE'] = berry_table()
    return d
