"""Decode the textures of a BTX0 (.nsbtx) or the TEX0 block inside a BMD0, all seven DS texture formats.
Read-only; used to browse the game's texture sets. Format layout from the NDS TEX0 block (GBATEK "DS 3D Texture
Formats"): params word = offset>>3 (bits 0-15), width 8<<n (20-22), height 8<<n (23-25), format (26-28),
colour 0 transparent (29). Palettes pair with textures by name: <texture>_pl, else the first palette.

    python3 nsbtx.py FILE.nsbtx OUT_DIR        writes OUT_DIR/<texture>.png and OUT_DIR/sheet.png
    python3 nsbtx.py merge BASE OUT [PAIRS.txt] SRC:texture[:palette] ...   lossless merge (see merge())
"""
import struct, sys, os

def _dict(d, off):
    cnt = d[off + 1]
    tree = off + 4 + 8 + 4 * cnt
    unit, _ = struct.unpack_from('<HH', d, tree)
    data_at = tree + 4
    names_at = data_at + unit * cnt
    return [(d[names_at + 16 * j:names_at + 16 * j + 16].rstrip(b'\0').decode('ascii', 'replace'),
             d[data_at + unit * j:data_at + unit * (j + 1)]) for j in range(cnt)]

def tex0(data):
    nb = struct.unpack_from('<H', data, 0xE)[0]
    for k in range(nb):
        bo = struct.unpack_from('<I', data, 0x10 + 4 * k)[0]
        if data[bo:bo + 4] == b'TEX0':
            return data[bo:]
    raise ValueError('no TEX0 block')

def _rgb(c, a=255):
    e = lambda v: (v << 3) | (v >> 2)      # 5-bit to 8-bit by bit replication (as apicula)
    return (e(c & 31), e((c >> 5) & 31), e((c >> 10) & 31), a)

def decode(data):
    """[(name, PIL RGBA image, format)] for every texture."""
    from PIL import Image
    t = tex0(data)
    texdict = struct.unpack_from('<H', t, 0xE)[0]
    texdata = struct.unpack_from('<I', t, 0x14)[0]
    cmp_data = struct.unpack_from('<I', t, 0x24)[0]
    cmp_idx = struct.unpack_from('<I', t, 0x28)[0]
    pltdict = struct.unpack_from('<I', t, 0x34)[0]
    pltdata = struct.unpack_from('<I', t, 0x38)[0]
    pals = {n: pltdata + (struct.unpack_from('<H', e, 0)[0] << 3) for n, e in _dict(t, pltdict)}
    first = next(iter(pals.values())) if pals else None
    out = []
    for name, ent in _dict(t, texdict):
        p = struct.unpack_from('<I', ent, 0)[0]
        fmt = (p >> 26) & 7; w = 8 << ((p >> 20) & 7); h = 8 << ((p >> 23) & 7); col0 = (p >> 29) & 1
        rel = (p & 0xFFFF) << 3
        po = pals.get(name + '_pl', first)
        pal = lambda i: struct.unpack_from('<H', t, po + 2 * i)[0]
        img = Image.new('RGBA', (w, h)); px = img.load()
        if fmt == 7:
            for i in range(w * h):
                c = struct.unpack_from('<H', t, texdata + rel + 2 * i)[0]
                px[i % w, i // w] = _rgb(c, 255 if c & 0x8000 else 0)
        elif fmt == 5:
            blocks = t[cmp_data + rel:]
            idx_at = cmp_idx + rel // 2
            for b in range(w * h // 16):
                bx, by = (b % (w // 4)) * 4, (b // (w // 4)) * 4
                bits = struct.unpack_from('<I', blocks, 4 * b)[0]
                ex = struct.unpack_from('<H', t, idx_at + 2 * b)[0]
                base = po + ((ex & 0x3FFF) << 2); mode = ex >> 14
                c = [struct.unpack_from('<H', t, base + 2 * i)[0] for i in range(4)]
                cols = [_rgb(c[0]), _rgb(c[1])]
                if mode == 0: cols += [_rgb(c[2]), (0, 0, 0, 0)]
                elif mode == 1: cols += [tuple((a + b2) // 2 for a, b2 in zip(cols[0], cols[1])), (0, 0, 0, 0)]
                elif mode == 2: cols += [_rgb(c[2]), _rgb(c[3])]
                else: cols += [tuple((5 * a + 3 * b2) // 8 for a, b2 in zip(cols[0], cols[1])),
                               tuple((3 * a + 5 * b2) // 8 for a, b2 in zip(cols[0], cols[1]))]
                for i in range(16):
                    px[bx + i % 4, by + i // 4] = cols[(bits >> (2 * i)) & 3]
        else:
            raw = t[texdata + rel:]
            for i in range(w * h):
                x, y = i % w, i // w
                if fmt == 1:    # A3I5
                    v = raw[i]; a = (v >> 5) * 255 // 7; c = _rgb(pal(v & 31))
                    px[x, y] = c[:3] + (a,)
                elif fmt == 6:  # A5I3
                    v = raw[i]; a = (v >> 3) * 255 // 31; c = _rgb(pal(v & 7))
                    px[x, y] = c[:3] + (a,)
                else:
                    bpp = {2: 2, 3: 4, 4: 8}[fmt]
                    v = (raw[i * bpp // 8] >> ((i * bpp) % 8)) & ((1 << bpp) - 1)
                    px[x, y] = (0, 0, 0, 0) if (v == 0 and col0) else _rgb(pal(v))
        out.append((name, img, fmt))
    return out

def sheet(textures, cell=64, cols=8):
    """Contact sheet: each texture scaled into a cell with its name."""
    from PIL import Image, ImageDraw
    rows = (len(textures) + cols - 1) // cols
    s = Image.new('RGBA', (cell * cols, (cell + 10) * rows), (255, 0, 255, 255))
    d = ImageDraw.Draw(s)
    for i, (name, img, _) in enumerate(textures):
        x, y = cell * (i % cols), (cell + 10) * (i // cols)
        k = cell / max(img.size)
        im = img.resize((max(1, int(img.width * k)), max(1, int(img.height * k))), Image.NEAREST)
        s.alpha_composite(im, (x, y))
        d.rectangle((x, y + cell, x + cell, y + cell + 10), fill=(0, 0, 0, 255))
        d.text((x + 1, y + cell), name[:11], fill=(255, 255, 255, 255))
    return s

def material_pairs(bmd):
    """(texture, palette) pairs used by the materials of every model in a BMD0 (MDL0 block): each material's
    texture comes from the texture->material dictionary, its palette from the palette->material dictionary."""
    nb = struct.unpack_from('<H', bmd, 0xE)[0]
    mdl = next(bo for bo in (struct.unpack_from('<I', bmd, 0x10 + 4 * k)[0] for k in range(nb)) if bmd[bo:bo + 4] == b'MDL0')
    pairs = set()
    for _, ent in _dict(bmd, mdl + 8):
        model = mdl + struct.unpack_from('<I', ent, 0)[0]
        mats = model + struct.unpack_from('<I', bmd, model + 8)[0]
        tex_d, pal_d = struct.unpack_from('<HH', bmd, mats)
        def by_material(d_off):
            out = {}
            for name, e in _dict(bmd, mats + d_off):
                off, n = struct.unpack_from('<HB', e, 0)
                for i in range(n): out[bmd[mats + off + i]] = name
            return out
        texs, pals = by_material(tex_d), by_material(pal_d)
        for mi, t in texs.items():
            pairs.add((t, pals.get(mi)))
    return pairs


# ---------------------------------------------------------------------------------------------------------------
# Lossless texture-set merge: keeps every byte of the base set's textures and palettes, appends new ones copied
# byte for byte from other sets, and rebuilds the two name dictionaries. (CTRMap's writer re-encodes textures:
# A3I5 shadows become A5I3 and some pixels change, notes/OPENING.md.) Dictionary trees are Patricia tries built
# exactly like the game's own (checked byte for byte against 118 game dictionaries).

def _bit(name, k):
    return (name[k >> 3] >> (k & 7)) & 1

def dict_tree(names):
    """Patricia tree nodes [refBit, left, right, entry] for up to 255 names; node 0 is the head (refBit 127, its
    key all zeros); nodes numbered in pre-order from the root, as in the game's files."""
    keys = [n.encode('ascii').ljust(16, b'\0')[:16] if isinstance(n, str) else n.ljust(16, b'\0')[:16] for n in names]
    nodes = [[127, 0, 0, 0]]
    for i, k in enumerate(keys):
        p, x = 0, nodes[0][1]
        while nodes[x][0] < nodes[p][0]:
            p = x; x = nodes[x][2] if _bit(k, nodes[x][0]) else nodes[x][1]
        other = bytes(16) if x == 0 else keys[nodes[x][3]]
        b = 127
        while b >= 0 and _bit(k, b) == _bit(other, b): b -= 1
        assert b >= 0, f'duplicate name {k}'
        p, x = 0, nodes[0][1]
        while nodes[x][0] < nodes[p][0] and nodes[x][0] > b:
            p = x; x = nodes[x][2] if _bit(k, nodes[x][0]) else nodes[x][1]
        t = len(nodes)
        nodes.append([b, x, t, i] if _bit(k, b) else [b, t, x, i])
        if p == 0: nodes[0][1] = t
        elif _bit(k, nodes[p][0]): nodes[p][2] = t
        else: nodes[p][1] = t
    order = [0]
    def visit(n):
        order.append(n)
        for c in (nodes[n][1], nodes[n][2]):
            if nodes[c][0] < nodes[n][0]: visit(c)
    if len(nodes) > 1: visit(nodes[0][1])
    new = {old: i for i, old in enumerate(order)}
    return [[nodes[o][0], new[nodes[o][1]], new[nodes[o][2]], nodes[o][3]] for o in order]

def dict_build(entries, unit):
    """entries: [(name, data bytes of length unit)] -> dictionary bytes."""
    n = len(entries)
    tree = b''.join(bytes(node) for node in dict_tree([e[0] for e in entries]))
    head_entries = 8 + len(tree)
    body = struct.pack('<HH', unit, 4 + unit * n) + b''.join(d for _, d in entries) + \
           b''.join(nm.encode('ascii').ljust(16, b'\0') for nm, _ in entries)
    size = head_entries + len(body)
    return struct.pack('<BBHHH', 0, n, size, 8, head_entries) + tree + body

def _parse(btx):
    t = tex0(btx)
    texdict, texdata = struct.unpack_from('<H', t, 0xE)[0], struct.unpack_from('<I', t, 0x14)[0]
    texsize = struct.unpack_from('<H', t, 0xC)[0] << 3
    c_size = struct.unpack_from('<H', t, 0x1C)[0] << 3
    c_data, c_idx = struct.unpack_from('<II', t, 0x24)
    psize = struct.unpack_from('<H', t, 0x30)[0] << 3
    pflag = struct.unpack_from('<H', t, 0x32)[0]
    pdict, pdata = struct.unpack_from('<H', t, 0x34)[0], struct.unpack_from('<I', t, 0x38)[0]
    texs = [(n, struct.unpack_from('<II', e, 0)) for n, e in _dict(t, texdict)]
    pals = [(n, struct.unpack_from('<HH', e, 0)) for n, e in _dict(t, pdict)]
    return dict(t=t, texdata=t[texdata:texdata + texsize], c_data=t[c_data:c_data + c_size],
                c_idx=t[c_idx:c_idx + c_size // 2], pdata=t[pdata:pdata + psize], texs=texs, pals=pals, pflag=pflag)

def _tex_bytes(src, params):
    """Raw data of one texture of a parsed set: (texel bytes, 4x4 index bytes or b'')."""
    fmt = (params >> 26) & 7; w = 8 << ((params >> 20) & 7); h = 8 << ((params >> 23) & 7)
    off = (params & 0xFFFF) << 3
    if fmt == 5:
        n = w * h // 4      # 2 bits per texel
        return src['c_data'][off:off + n], src['c_idx'][off // 2:off // 2 + n // 2]
    bpp = {1: 8, 2: 2, 3: 4, 4: 8, 6: 8, 7: 16}[fmt]
    return src['texdata'][off:off + w * h * bpp // 8], b''

def _pal_size(src, name):
    offs = sorted(o << 3 for _, (o, _f) in src['pals'])
    o = dict(src['pals'])[name][0] << 3
    nxt = [x for x in offs if x > o]
    return (nxt[0] if nxt else len(src['pdata'])) - o

def image_source(name, img):
    """A parsed one-texture source for merge() from a PIL image (power-of-two sides, 8-1024): a 16-colour palette
    texture (format 3) named `name` with palette `name`_pl. Used for Gen 3 art drawn on a room surface (models_interior
    gen3_tile_image: Mauville Gym's switches, 2026-10-18)."""
    from PIL import Image
    im = img.convert('RGB').quantize(colors=16)
    w, h = im.size
    assert w in (8, 16, 32, 64, 128, 256, 512, 1024) and h in (8, 16, 32, 64, 128, 256, 512, 1024), (name, im.size)
    px = list(im.getdata())
    raw = bytes((px[i] & 15) | ((px[i + 1] & 15) << 4) for i in range(0, w * h, 2))
    pal = (im.getpalette() or [])[:48]; pal += [0] * (48 - len(pal))
    pdata = b''.join(struct.pack('<H', (pal[i] >> 3) | ((pal[i + 1] >> 3) << 5) | ((pal[i + 2] >> 3) << 10)) for i in range(0, 48, 3))
    params = (((w // 8).bit_length() - 1) << 20) | (((h // 8).bit_length() - 1) << 23) | (3 << 26)
    return dict(texdata=raw, c_data=b'', c_idx=b'', pdata=pdata, pflag=0,
                texs=[(name, (params, 0x80000000 | w | (h << 11)))], pals=[(name + '_pl', (0, 0))])

def merge(base, additions, drop=()):
    """base: BTX0 bytes. additions: [(src BTX0 bytes, texture name, palette name or None)], optionally
    (..., new texture name, new palette name): the copy goes in under those names (a texture and its palette are
    found by name only, so another set's same-named texture can stand beside the base's own: data/hoenn_ash.json).
    drop: base textures left out first (their texels too; every palette stays), e.g. to put another texture in under
    the same name (seasons2: the warp-only maps' clear falling leaves). Returns BTX0 bytes."""
    B = _parse(base)
    texdata, c_data, c_idx, pdata = bytearray(B['texdata']), bytearray(B['c_data']), bytearray(B['c_idx']), bytearray(B['pdata'])
    texs = [(n, struct.pack('<II', *v)) for n, v in B['texs']]
    if drop:                                     # (the kept textures' texels again, in their order, packed)
        texdata, c_data, c_idx, texs, moved = bytearray(), bytearray(), bytearray(), [], {}
        for n, (params, extra) in B['texs']:
            if n in drop: continue
            key = (params & 0xFFFF, (params >> 26) & 7 == 5)
            if key not in moved:
                raw, idx = _tex_bytes(B, params)
                if key[1]:
                    moved[key] = len(c_data); c_data += raw; c_idx += idx
                else:
                    while len(texdata) % 8: texdata.append(0)
                    moved[key] = len(texdata); texdata += raw
            texs.append((n, struct.pack('<II', (params & ~0xFFFF) | (moved[key] >> 3), extra)))
    pals = [(n, struct.pack('<HH', *v)) for n, v in B['pals']]
    have_t, have_p = {n for n, _ in texs}, {n for n, _ in pals}
    pflag = B['pflag']
    cache = {}
    for src_bytes, tname, pname, *renamed in additions:
        S = src_bytes if isinstance(src_bytes, dict) else cache.setdefault(id(src_bytes), _parse(src_bytes))   # (image_source)
        recolor = renamed[2] if len(renamed) > 2 else None       # optional palette transform (BGR555 bytes -> bytes)
        renamed = renamed[:2]
        name, pnew = (renamed + [None, None])[:2] if renamed else (tname, pname)
        assert len(name) <= 16 and (pnew is None or len(pnew) <= 16), f'{name}/{pnew}: names hold 16 characters'
        if name in have_t: continue
        params, extra = dict(S['texs'])[tname]
        assert (params >> 26) & 7 != 5, f'{tname}: 4x4-compressed textures are not supported (none in map/building sets)'
        raw, idx = _tex_bytes(S, params)
        if (params >> 26) & 7 == 5:
            off = len(c_data); c_data += raw; c_idx += idx
        else:
            while len(texdata) % 8: texdata.append(0)
            off = len(texdata); texdata += raw
        texs.append((name, struct.pack('<II', (params & ~0xFFFF) | (off >> 3), extra))); have_t.add(name)
        if pname and (pnew or pname) not in have_p:
            o, flag = dict(S['pals'])[pname]
            data = S['pdata'][o << 3:(o << 3) + _pal_size(S, pname)]
            if recolor: data = recolor(data)
            while len(pdata) % 8: pdata.append(0)
            pals.append((pnew or pname, struct.pack('<HH', len(pdata) >> 3, flag))); have_p.add(pnew or pname)
            pdata += data
            if flag & 1: pflag |= 0x8000
    tdict, pdict = dict_build(texs, 8), dict_build(pals, 4)
    o_tdict = 0x3C; o_pdict = o_tdict + len(tdict); o_tex = o_pdict + len(pdict)
    o_c = o_tex + len(texdata); o_ci = o_c + len(c_data); o_p = o_ci + len(c_idx)
    size = o_p + len(pdata)
    t0 = B['t']
    hdr = bytearray(t0[:0x3C])
    struct.pack_into('<I', hdr, 4, size)
    struct.pack_into('<HH', hdr, 0xC, len(texdata) >> 3, o_tdict); struct.pack_into('<I', hdr, 0x14, o_tex)
    struct.pack_into('<HH', hdr, 0x1C, len(c_data) >> 3, o_tdict); struct.pack_into('<II', hdr, 0x24, o_c, o_ci)
    struct.pack_into('<HH', hdr, 0x30, len(pdata) >> 3, pflag); struct.pack_into('<H', hdr, 0x34, o_pdict)
    struct.pack_into('<I', hdr, 0x38, o_p)
    block = bytes(hdr) + tdict + pdict + bytes(texdata) + bytes(c_data) + bytes(c_idx) + bytes(pdata)
    head = bytearray(base[:0x14])
    struct.pack_into('<I', head, 8, 0x14 + len(block))
    return bytes(head) + block

def merge_cli(args):
    """merge BASE.nsbtx OUT.nsbtx [PAIRS.txt] SRC.nsbtx:texture[:palette] ...  (palette: PAIRS, else texture_pl
    if the source has it, else none)"""
    base, out, rest = args[0], args[1], args[2:]
    pairs = {}
    if rest and rest[0].endswith('.txt'):
        for line in open(rest.pop(0)):
            p = line.replace('"', '').split()
            if len(p) == 2: pairs[p[0]] = p[1]
    adds, srcs = [], {}
    for a in rest:
        path, tex, *pal = a.split(':')
        data = srcs.setdefault(path, open(path, 'rb').read())
        names = {n for n, _ in _parse(data)['pals']}
        pname = pal[0] if pal else pairs.get(tex, tex + '_pl' if tex + '_pl' in names else None)
        adds.append((data, tex, pname))
    open(out, 'wb').write(merge(open(base, 'rb').read(), adds))

if __name__ == '__main__' and sys.argv[1] == 'merge':
    merge_cli(sys.argv[2:])
elif __name__ == '__main__':
    data = open(sys.argv[1], 'rb').read()
    out = sys.argv[2]; os.makedirs(out, exist_ok=True)
    texs = decode(data)
    for name, img, _ in texs: img.save(os.path.join(out, name + '.png'))
    sheet(texs).save(os.path.join(out, 'sheet.png'))
    print(len(texs), 'textures ->', out)
