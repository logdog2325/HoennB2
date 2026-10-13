"""Character sprites: export to PNG + palette and import back, byte-exact. No Nintendo tools.

    python3 sprites.py ow-export CODE OUTDIR          overworld object code -> OUTDIR/frame_NN.png, palette.pal, sprite.json
    python3 sprites.py ow-import DIR OUT.btx0          edited folder -> the sheet's BTX0 bytes
    python3 sprites.py tr-export front|back ID OUTDIR  trainer sprite -> OUTDIR/parts.png, static.png, palette.pal, sprite.json
    python3 sprites.py tr-import DIR OUTDIR            edited folder -> OUTDIR/<file index>.bin (the changed archive files)
    python3 sprites.py mcss-export ARC PARTS PAL OUTDIR  any other MCSS sprite (e.g. 168 25 28: the intro professor)
    python3 sprites.py mcss-import DIR OUTDIR          same as tr-import, for an mcss-export folder
    python3 sprites.py tex-export ARC FILE TEXTURE OUTDIR  an 8 bpp model/BTX texture (e.g. 168 22 int_swan_m.2) -> OUTDIR
    python3 sprites.py preview DIR OUT.png [DONOR_DIR]  sheet of a folder (before/after if a donor folder is given)
    python3 sprites.py check                           round trip of every sheet and trainer sprite through PNG files

Overworld (field) sprites [checked on all 968 sheets, see `check`]
  a/0/4/7 (ARCID_MMODEL_TBL): u32 count (1008), then count x 0x1C FieldActorConfig records (field_actor.h);
      u16 res1 at +0x10 = the sheet's file in a/0/4/8. Object code -> record as GetIndexOfObjID (arm9 0x0200fe34).
  a/0/4/8 (ARCID_MMODEL_GRA): 968 BTX0 sheets (+7 BMD0 objects). One TEX0 block: one 4bpp 16-colour texture per
      frame, 32x32 ('t4x4xN.k') or 64x64 ('t8x8xN.k'), stored one after another, colour 0 transparent, one palette.
  Import writes the pixels and the palette in place, so the file keeps its size and layout.
  Folder: sprite.json (what it is), palette.pal (JASC-PAL, 16 colours), frame_00.png ... (indexed PNG, index 0 clear).

Battle (trainer) sprites [checked on all 188 front + 31 back sprites]
  a/0/7/1 (front) and a/0/7/2 (back), sprite s = files 8s .. 8s+7 (GetTrSprite*DatID, arm9 0x02033cf0):
    +0 NCGR, LZ11: 80x80 still figure, 4bpp tiles in OBJ order 64x64 @(0,0), 16x64 @(64,0), 32x16 @(0,64),
       32x16 @(32,64), 16x16 @(64,64) (empty in back sprites)
    +1 NCGR, LZ11: 256x128 4bpp linear bitmap = the MCSS texture: the parts the animation moves, plus one whole figure
    +2 NCER cells (OBJ tile t = texture pixel (t%32*8, t//32*8); affine double-size OBJs, so the picture's top-left
       on screen is the OBJ position + size/2), +3 NANR (LZ11), +4 NMCR, +5 NMAR, +6 MCSS data: never changed here
    +7 NCLR: 16 colours
  Import rewrites the pixels of +0/+1 (headers kept) and the colours of +7, and LZ11-compresses again with a
  compressor that reproduces the game's own compressed bytes (all 657 LZ11 files in a/0/7/1-2 come out identical).
  Folder: sprite.json, palette.pal, parts.png (256x128), static.png (80x80).
  Other MCSS sprites (same NCGR/NCLR formats, e.g. the intro's professor in a/1/6/8: parts 25, palette 28) use the
  same folder with sprite.json "files" naming the archive files; "keep_size": true pads a recompressed picture to
  its old length (and refuses a longer one), for archives that build_rom.py does not pad.

Textures in models (8 bpp, format 4) [checked on the intro's four gender-choice pictures, see `check`]
  A BMD0/BTX0 TEX0 block: the texture's 8-bit texels and its 256-colour palette '<texture>_pl' are rewritten in
  place (same size, same layout); colour 0 is transparent when the texture says so (the intro's pictures do).
  Folder: sprite.json (kind 'texture', archive, file, texture, palette), texture.png (indexed, <= 256 colours,
  index 0 clear; its own palette is the one written).

Player icons (a/0/3/0) [checked: every frame equals an overworld frame of 231 / 240, see `check`]
  The start menu's Continue panel (NCGR 5 / 7), the GTS (14 / 17) and Spin Trade / Battle Video (20 / 23) show
  frames of the player's walk-run sheet: uncompressed NCGR, 4 bpp, 32 x 32 OBJ frames one after another (16 tiles
  of 8 x 8 each, row-major), palette = NCLR 4 / 6 colours 0-15 (= the sheet's palette). Folder:
  src/sprites/objframes/<name>/sprite.json {"archive", "palette", "from_code", "ncgr": {file: [sheet frame, ...]}}:
  no pictures of its own; the frames are copied from the overworld art folder of from_code.

Trainer card pictures (a/0/4/0) [checked: all 16 re-encoded byte-identical, see `check`]
  The card shows Union Room avatar v (PlayerInfo, a new game sets random 0-7 + 8 x gender): NCGR 16 + v (80 x 80,
  8 bpp, 8 x 8 tiles row-major, uncompressed) with NCLR v (256 colours). Folder src/sprites/cardpic/<name>/:
  sprite.json {"archive", "ncgr": [...], "nclr": [...], "from_front": <front sprite>} copies that battle sprite's
  still picture (static.png, 16 colours) into each listed avatar: pixels use colours 64-79 (ov186 loads the NCLR's
  first 16 colours there, `func_ov186_021a7d40`), the NCLR gets the colours at 1-15 and 65-79 (as Black 2's), colour
  0 left as the avatar's own background.

Colours: BGR555 -> 8 bit as (c << 3) | (c >> 2); back by rounding, which inverts it exactly.
PNG input: an indexed PNG whose palette matches palette.pal is read by index; anything else is matched by colour
(alpha < 128 = transparent = index 0); colours not in palette.pal are an error (no silent dithering).
palette.pal is the palette that gets written; the PNGs' own palettes are only used for matching.
"""
import io, json, os, struct, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
SRC_FILES = os.path.join(ROOT, 'external', 'pokebw2', 'extract', 'b2_us', 'files')
sys.path.insert(0, HERE)
from b2files import arc_path, narc_entries  # noqa: E402

ARC_OW_TABLE, ARC_OW_SHEETS = 47, 48
ARC_TR = {'front': 71, 'back': 72}
TR_STATIC, TR_PARTS, TR_PALETTE = 0, 1, 7          # file offsets inside a trainer sprite's 8 files
STATIC_OBJS = [(0, 0, 64, 64), (64, 0, 16, 64), (0, 64, 32, 16), (32, 64, 32, 16), (64, 64, 16, 16)]

# ---------------------------------------------------------------------------------------------------- colours, files

def c5to8(c): return (c << 3) | (c >> 2)
def c8to5(c): return (c * 31 + 127) // 255

def bgr555_to_rgb(v): return (c5to8(v & 31), c5to8((v >> 5) & 31), c5to8((v >> 10) & 31))
def rgb_to_bgr555(rgb): r, g, b = rgb[:3]; return c8to5(r) | c8to5(g) << 5 | c8to5(b) << 10

def write_pal(path, rgbs):
    with open(path, 'w', newline='\r\n') as f:
        f.write('JASC-PAL\n0100\n%d\n' % len(rgbs))
        for r, g, b in rgbs: f.write(f'{r} {g} {b}\n')

def read_pal(path):
    lines = open(path).read().split()
    assert lines[0] == 'JASC-PAL', f'{path}: not a JASC-PAL file'
    n = int(lines[2]); vals = list(map(int, lines[3:3 + 3 * n]))
    rgbs = [tuple(vals[3 * i:3 * i + 3]) for i in range(n)]
    assert n == 16, f'{path}: {n} colours, need 16'
    return rgbs

def write_png(path, pixels, w, h, rgbs):
    """pixels: bytes/list of palette indices, row-major. Indexed PNG, index 0 transparent."""
    from PIL import Image
    img = Image.frombytes('P', (w, h), bytes(pixels))
    img.putpalette([v for rgb in rgbs for v in rgb])
    img.save(path, transparency=0, optimize=False)

def read_png(path, rgbs, w, h):
    """Palette indices (bytes, row-major) of an edited PNG, against the 16 colours `rgbs`."""
    from PIL import Image
    img = Image.open(path)
    assert img.size == (w, h), f'{path}: {img.size}, expected {w}x{h}'
    want = [tuple(c8to5(v) for v in rgb) for rgb in rgbs]
    if img.mode == 'P':
        pal = img.getpalette()[:48]
        have = [tuple(c8to5(v) for v in pal[3 * i:3 * i + 3]) for i in range(len(pal) // 3)]
        data = img.tobytes()
        if have[:16] == want[:len(have[:16])] and max(data, default=0) < 16:
            return data
    img = img.convert('RGBA')
    lookup = {}
    for i in range(15, 0, -1):            # first index wins when a palette repeats a colour
        lookup[want[i]] = i
    out = bytearray(); bad = {}
    for k, (r, g, b, a) in enumerate(img.getdata()):
        if a < 128: out.append(0); continue
        key = (c8to5(r), c8to5(g), c8to5(b))
        i = lookup.get(key)
        if i is None:
            bad.setdefault((r, g, b), (k % w, k // w)); out.append(0)
        else:
            out.append(i)
    if bad:
        raise SystemExit(f'{path}: {len(bad)} colours not in palette.pal, e.g. ' +
                         ', '.join(f'{c} at {p}' for c, p in list(bad.items())[:5]))
    return bytes(out)

def unpack4(data, n):
    out = bytearray(n)
    for i in range(n):
        b = data[i >> 1]; out[i] = (b >> 4) if i & 1 else (b & 15)
    return out

def pack4(pix):
    return bytes((pix[i] & 15) | (pix[i + 1] & 15) << 4 for i in range(0, len(pix), 2))

def read_json(path): return json.load(open(path))
def write_json(path, obj):
    with open(path, 'w') as f: json.dump(obj, f, indent=1); f.write('\n')

# ---------------------------------------------------------------------------------------------------- LZ11

def lz11_decompress(d):
    assert d[0] == 0x11, 'not LZ11'
    size = d[1] | d[2] << 8 | d[3] << 16; pos = 4; out = bytearray()
    while len(out) < size:
        flags = d[pos]; pos += 1
        for bit in range(8):
            if len(out) >= size: break
            if flags & (0x80 >> bit):
                t = d[pos] >> 4
                if t == 0:
                    n = ((d[pos] & 15) << 4 | d[pos + 1] >> 4) + 0x11; disp = ((d[pos + 1] & 15) << 8 | d[pos + 2]) + 1; pos += 3
                elif t == 1:
                    n = ((d[pos] & 15) << 12 | d[pos + 1] << 4 | d[pos + 2] >> 4) + 0x111
                    disp = ((d[pos + 2] & 15) << 8 | d[pos + 3]) + 1; pos += 4
                else:
                    n = t + 1; disp = ((d[pos] & 15) << 8 | d[pos + 1]) + 1; pos += 2
                for _ in range(n): out.append(out[-disp])
            else:
                out.append(d[pos]); pos += 1
    return bytes(out)

def lz11_compress(data):
    """Greedy LZ11 as the game's files were made: longest match in the 4 KB window, distance >= 2, the FARTHEST
    match wins a tie, no padding at the end. Reproduces every LZ11 file in a/0/7/1 and a/0/7/2 byte for byte."""
    n = len(data); out = bytearray([0x11, n & 0xff, n >> 8 & 0xff, n >> 16 & 0xff])
    heads = {}; added = 0; pos = 0
    while pos < n:
        flag_at = len(out); out.append(0); flags = 0
        for bit in range(8):
            if pos >= n: break
            while added < pos:
                if added + 3 <= n: heads.setdefault(data[added:added + 3], []).append(added)
                added += 1
            best_len = best_disp = 0
            ml = min(0x10110, n - pos)
            if ml >= 3:
                for c in heads.get(data[pos:pos + 3], ()):
                    d = pos - c
                    if d > 0x1000 or d < 2: continue
                    l = 3
                    while l < ml and data[c + l] == data[pos + l]: l += 1
                    if l > best_len:
                        best_len, best_disp = l, d
                        if l == ml: break
            if best_len >= 3:
                flags |= 0x80 >> bit; d = best_disp - 1
                if best_len <= 0x10:
                    out += bytes([(best_len - 1) << 4 | d >> 8, d & 0xff])
                elif best_len <= 0x110:
                    l = best_len - 0x11; out += bytes([l >> 4, (l & 15) << 4 | d >> 8, d & 0xff])
                else:
                    l = best_len - 0x111; out += bytes([0x10 | l >> 12, l >> 4 & 0xff, (l & 15) << 4 | d >> 8, d & 0xff])
                pos += best_len
            else:
                out.append(data[pos]); pos += 1
        out[flag_at] = flags
    return bytes(out)

# ---------------------------------------------------------------------------------------------------- overworld

def obj_record(code):
    """GetIndexOfObjID: object code -> record in a/0/4/7."""
    if code <= 376: return code
    if 0x1000 <= code <= 0x126B: return code - 0xE87
    if 0x2000 <= code <= 0x200A: return code - 0x1C1B
    return 10

def ow_table(files):
    t = narc_entries(arc_path(files, ARC_OW_TABLE))[0]
    n = struct.unpack_from('<I', t, 0)[0]
    keys = ('uid entityType sceneNodeType shadow footprint reflections billboardSize spriteAtlasSize '
            'spriteControllerType gender collWidth collHeight offX offY offZ res1 res2 anim0 anim1 anim2').split()
    return [dict(zip(keys, struct.unpack_from('<HBBBBBBBBBBBbbbHHHHH', t, 4 + 28 * i))) for i in range(n)]

def ow_sheet_of(files, code, table=None):
    rec = (table or ow_table(files))[obj_record(code)]
    return rec['res1'], rec

def _dict(t, off):
    """Nitro resource dictionary at t[off]: [(name, entry bytes)]."""
    cnt = t[off + 1]
    entries = off + 4 + 8 + 4 * cnt
    unit = struct.unpack_from('<H', t, entries)[0]
    data_at = entries + 4; names_at = data_at + unit * cnt
    return [(t[names_at + 16 * j:names_at + 16 * j + 16].rstrip(b'\0').decode('ascii'), t[data_at + unit * j:data_at + unit * (j + 1)])
            for j in range(cnt)]

def btx_layout(btx):
    """(frames [(name, w, h, absolute offset)], palette name, palette absolute offset) of a sheet."""
    assert btx[:4] == b'BTX0', 'not a BTX0 sheet'
    tex0 = struct.unpack_from('<I', btx, 0x10)[0]
    t = btx[tex0:]
    assert t[:4] == b'TEX0'
    texdict = struct.unpack_from('<H', t, 0xE)[0]
    texdata = struct.unpack_from('<I', t, 0x14)[0]
    paldict, paldata = struct.unpack_from('<II', t, 0x34)
    frames = []
    for name, ent in _dict(t, texdict):
        p = struct.unpack_from('<I', ent, 0)[0]
        fmt, w, h, clear = p >> 26 & 7, 8 << (p >> 20 & 7), 8 << (p >> 23 & 7), p >> 29 & 1
        assert fmt == 3 and clear, f'{name}: format {fmt}, colour 0 clear {clear} (only 4bpp sheets are handled)'
        frames.append((name, w, h, tex0 + texdata + ((p & 0xffff) << 3)))
    pals = _dict(t, paldict)
    assert len(pals) == 1, f'{len(pals)} palettes'
    pname, pent = pals[0]
    return frames, pname, tex0 + paldata + (struct.unpack_from('<H', pent, 0)[0] << 3)

def btx_decode(btx):
    frames, pname, poff = btx_layout(btx)
    pal = list(struct.unpack_from('<16H', btx, poff))
    return [(name, w, h, unpack4(btx[off:off + w * h // 2], w * h)) for name, w, h, off in frames], pname, pal

def btx_encode(btx, pixels, pal):
    """The sheet with new frame pixels (list of index bytes, one per frame) and 16 BGR555 colours, in place."""
    frames, _, poff = btx_layout(btx)
    assert len(pixels) == len(frames), f'{len(pixels)} frames given, sheet has {len(frames)}'
    out = bytearray(btx)
    for (name, w, h, off), pix in zip(frames, pixels):
        assert len(pix) == w * h
        out[off:off + w * h // 2] = pack4(pix)
    struct.pack_into('<16H', out, poff, *pal)
    return bytes(out)

def ow_export(files, code, outdir, sheets=None, table=None):
    os.makedirs(outdir, exist_ok=True)
    sheet, rec = ow_sheet_of(files, code, table)
    btx = (sheets or narc_entries(arc_path(files, ARC_OW_SHEETS)))[sheet]
    frames, pname, pal = btx_decode(btx)
    rgbs = [bgr555_to_rgb(c) for c in pal]
    write_pal(os.path.join(outdir, 'palette.pal'), rgbs)
    for i, (name, w, h, pix) in enumerate(frames):
        write_png(os.path.join(outdir, f'frame_{i:02d}.png'), pix, w, h, rgbs)
    meta = dict(kind='overworld', code=code, sheet=sheet, frames=len(frames), size=[frames[0][1], frames[0][2]],
                controller=rec['spriteControllerType'], textures=[f[0] for f in frames], palette=pname)
    write_json(os.path.join(outdir, 'sprite.json'), meta)
    return meta

def ow_load_folder(folder):
    """(meta, frames [index bytes], 16 BGR555 colours) of an edited overworld folder."""
    meta = read_json(os.path.join(folder, 'sprite.json'))
    rgbs = read_pal(os.path.join(folder, 'palette.pal'))
    w, h = meta['size']
    frames = [read_png(os.path.join(folder, f'frame_{i:02d}.png'), rgbs, w, h) for i in range(meta['frames'])]
    return meta, frames, [rgb_to_bgr555(c) for c in rgbs]

def ow_import(folder, btx):
    """New bytes for sheet `btx` from an edited folder (same layout as the sheet)."""
    meta, frames, pal = ow_load_folder(folder)
    lay, _, _ = btx_layout(btx)
    assert [f[0] for f in lay] == meta['textures'], f'{folder}: texture names differ from the sheet'
    return btx_encode(btx, frames, pal)

# ---------------------------------------------------------------------------------------------------- trainer (MCSS)

def ncgr_pixels(ncgr):
    """(header bytes, data offset, pixel count) of an uncompressed NCGR with one 4bpp image."""
    assert ncgr[:4] == b'RGCN' and ncgr[0x10:0x14] == b'RAHC'
    th, tw, depth, _, tiled, size, off = struct.unpack_from('<HHIIIII', ncgr, 0x18)
    assert depth == 3, f'depth {depth}'
    return 0x18 + off, size, (tw * 8, th * 8, tiled)

def static_order(w=80):
    """Pixel index (row-major in the 80x80 picture) of each 4bpp texel of the tiled +0 file."""
    order = []
    for ox, oy, ow, oh in STATIC_OBJS:
        for t in range(ow * oh // 64):
            tx, ty = ox + t % (ow // 8) * 8, oy + t // (ow // 8) * 8
            order += [(ty + j // 8) * w + tx + j % 8 for j in range(64)]
    return order

def tr_decode_image(lzfile, kind):
    u = lz11_decompress(lzfile)
    off, size, (w, h, tiled) = ncgr_pixels(u)
    texels = unpack4(u[off:off + size], size * 2)
    if kind == 'parts':
        assert (w, h, tiled) == (256, 128, 1), (w, h, tiled)
        return w, h, bytes(texels)
    assert (w, h, tiled) == (80, 80, 0), (w, h, tiled)
    pix = bytearray(80 * 80)
    for k, p in enumerate(static_order()): pix[p] = texels[k]
    return w, h, bytes(pix)

def tr_encode_image(lzfile, kind, pix):
    u = bytearray(lz11_decompress(lzfile))
    off, size, _ = ncgr_pixels(u)
    if kind == 'static':
        pix = bytes(pix[p] for p in static_order())
    assert len(pix) == size * 2
    u[off:off + size] = pack4(pix)
    return lz11_compress(bytes(u))

def nclr_colors(nclr):
    assert nclr[:4] == b'RLCN' and nclr[0x10:0x14] == b'TTLP'
    size, off = struct.unpack_from('<II', nclr, 0x20)
    at = 0x18 + off
    assert size == 32, f'palette of {size} bytes'
    return at, list(struct.unpack_from('<16H', nclr, at))

def tr_files(sprite):
    """File indices of trainer sprite `sprite` in a/0/7/1 or a/0/7/2."""
    return {'static': 8 * sprite + TR_STATIC, 'parts': 8 * sprite + TR_PARTS, 'palette': 8 * sprite + TR_PALETTE}

IMAGE_SIZE = {'parts': (256, 128), 'static': (80, 80)}

def mcss_export(files, archive, file_ids, outdir, meta_extra, entries=None):
    """Export an MCSS sprite's pictures (file_ids: {'parts': n, 'palette': n[, 'static': n]}) and palette."""
    os.makedirs(outdir, exist_ok=True)
    ents = entries or narc_entries(arc_path(files, archive))
    _, pal = nclr_colors(ents[file_ids['palette']])
    rgbs = [bgr555_to_rgb(c) for c in pal]
    write_pal(os.path.join(outdir, 'palette.pal'), rgbs)
    for kind in ('parts', 'static'):
        if kind in file_ids:
            w, h, pix = tr_decode_image(ents[file_ids[kind]], kind)
            write_png(os.path.join(outdir, f'{kind}.png'), pix, w, h, rgbs)
    meta = dict(meta_extra, archive=archive, files=file_ids)
    write_json(os.path.join(outdir, 'sprite.json'), meta)
    return meta

def tr_export(files, side, sprite, outdir, entries=None):
    return mcss_export(files, ARC_TR[side], tr_files(sprite), outdir,
                       dict(kind='trainer', side=side, sprite=sprite), entries)

def mcss_import(folder, entries, file_ids=None):
    """{file index: new bytes} for an edited MCSS folder; `entries` = the archive's current files; `file_ids`
    overrides sprite.json's files (to install the art as another sprite). With "keep_size": true in sprite.json, a
    recompressed picture is padded with zeros to its old length (LZ11 stops at its stated size) and must not be
    longer, so archives outside build_rom.py's RESERVE keep their size."""
    meta = read_json(os.path.join(folder, 'sprite.json'))
    ids = file_ids or meta['files']
    rgbs = read_pal(os.path.join(folder, 'palette.pal'))
    out = {}
    for kind in ('static', 'parts'):
        if kind not in ids:
            continue
        old = entries[ids[kind]]
        _, _, pix = tr_decode_image(old, kind)
        w, h = IMAGE_SIZE[kind]
        new_pix = read_png(os.path.join(folder, f'{kind}.png'), rgbs, w, h)
        if new_pix == pix:
            out[ids[kind]] = old
            continue
        data = tr_encode_image(old, kind, new_pix)
        if meta.get('keep_size'):
            if len(data) > len(old):
                raise SystemExit(f'{folder}: {kind} compresses to {len(data)} bytes, over the original {len(old)}')
            data += bytes(len(old) - len(data))
        out[ids[kind]] = data
    nclr = bytearray(entries[ids['palette']])
    at, _ = nclr_colors(nclr)
    struct.pack_into('<16H', nclr, at, *[rgb_to_bgr555(c) for c in rgbs])
    out[ids['palette']] = bytes(nclr)
    return out

def tr_import(folder, entries, sprite=None):
    """mcss_import for a trainer folder; `sprite` installs the art as another sprite number."""
    return mcss_import(folder, entries, None if sprite is None else tr_files(sprite))

# ---------------------------------------------------------------------------------------------------- 8 bpp textures

def tex0_entries(data):
    """{texture: (format, w, h, absolute offset, colour 0 clear)}, {palette: absolute offset} of the TEX0 block of
    a BMD0 / BTX0 (dictionary layout as _dict)."""
    tex0 = data.find(b'TEX0')
    assert tex0 >= 0, 'no TEX0 block'
    t = data[tex0:]
    texdict = struct.unpack_from('<H', t, 0xE)[0]
    texdata = struct.unpack_from('<I', t, 0x14)[0]
    pltdict, pltdata = struct.unpack_from('<II', t, 0x34)
    texs = {}
    for name, ent in _dict(t, texdict):
        p = struct.unpack_from('<I', ent, 0)[0]
        texs[name] = (p >> 26 & 7, 8 << (p >> 20 & 7), 8 << (p >> 23 & 7), tex0 + texdata + ((p & 0xFFFF) << 3), p >> 29 & 1)
    pals = {name: tex0 + pltdata + (struct.unpack_from('<H', ent, 0)[0] << 3) for name, ent in _dict(t, pltdict)}
    return texs, pals

def tex8_decode(data, name, palette=None):
    """(texel bytes row-major, w, h, 256 BGR555 colours) of an 8 bpp texture and its palette."""
    texs, pals = tex0_entries(data)
    fmt, w, h, off, clear = texs[name]
    assert fmt == 4, f'{name}: format {fmt}, not 8 bpp'
    return data[off:off + w * h], w, h, list(struct.unpack_from('<256H', data, pals[palette or name + '_pl']))

def tex8_encode(data, name, texels, colours, palette=None):
    """`data` with the 8 bpp texture `name` and its palette rewritten in place."""
    texs, pals = tex0_entries(data)
    fmt, w, h, off, clear = texs[name]
    assert fmt == 4 and len(texels) == w * h and len(colours) <= 256
    out = bytearray(data)
    out[off:off + w * h] = bytes(texels)
    struct.pack_into('<256H', out, pals[palette or name + '_pl'], *(list(colours) + [0] * (256 - len(colours))))
    return bytes(out)

def tex_export(files, archive, file, name, outdir, entries=None):
    from PIL import Image
    os.makedirs(outdir, exist_ok=True)
    data = (entries or narc_entries(arc_path(files, archive)))[file]
    texels, w, h, cols = tex8_decode(data, name)
    im = Image.frombytes('P', (w, h), bytes(texels))
    im.putpalette([v for c in cols for v in bgr555_to_rgb(c)])
    im.save(os.path.join(outdir, 'texture.png'), transparency=0)
    meta = dict(kind='texture', archive=archive, file=file, texture=name, palette=name + '_pl')
    write_json(os.path.join(outdir, 'sprite.json'), meta)
    return meta

def tex_import(folder, data):
    """New bytes for the archive file `data` from a texture folder (the PNG's indices and palette)."""
    from PIL import Image
    meta = read_json(os.path.join(folder, 'sprite.json'))
    im = Image.open(os.path.join(folder, 'texture.png'))
    assert im.mode == 'P', f'{folder}: texture.png must be an indexed PNG'
    pal = im.getpalette()
    n = len(pal) // 3
    cols = [rgb_to_bgr555(pal[3 * i:3 * i + 3]) for i in range(min(n, 256))]
    return tex8_encode(data, meta['texture'], im.tobytes(), cols, meta.get('palette'))

# ---------------------------------------------------------------------------------------------------- player icons

def objframes_decode(ncgr):
    """32 x 32 4 bpp OBJ frames (row-major index bytes, 1024 each) of an uncompressed tiled NCGR (a/0/3/0)."""
    off, size, (w, h, tiled) = ncgr_pixels(ncgr)
    tex = unpack4(ncgr[off:off + size], size * 2)
    frames = []
    for k in range(size // 512):
        fr = bytearray(1024)
        for t in range(16):
            for j in range(64):
                fr[(t // 4 * 8 + j // 8) * 32 + t % 4 * 8 + j % 8] = tex[k * 1024 + t * 64 + j]
        frames.append(bytes(fr))
    return frames

def objframes_encode(ncgr, frames):
    """`ncgr` with its frames replaced (same count, same size)."""
    off, size, _ = ncgr_pixels(ncgr)
    assert len(frames) * 512 == size, f'{len(frames)} frames for {size} bytes'
    tex = bytearray(size * 2)
    for k, fr in enumerate(frames):
        for t in range(16):
            for j in range(64):
                tex[k * 1024 + t * 64 + j] = fr[(t // 4 * 8 + j // 8) * 32 + t % 4 * 8 + j % 8]
    out = bytearray(ncgr)
    out[off:off + size] = pack4(tex)
    return bytes(out)

def objframes_import(folder, entries, art_folder):
    """{file: new bytes} for an objframes folder, with the frames and palette of the overworld folder `art_folder`."""
    meta = read_json(os.path.join(folder, 'sprite.json'))
    ometa, frames, pal = ow_load_folder(art_folder)
    out = {}
    for f, order in meta['ncgr'].items():
        out[int(f)] = objframes_encode(entries[int(f)], [frames[k] for k in order])
    nclr = bytearray(entries[meta['palette']])
    at, _ = nclr_colors_any(nclr)
    struct.pack_into('<16H', nclr, at, *pal)
    out[meta['palette']] = bytes(nclr)
    return out

def nclr_colors_any(nclr):
    """(absolute offset, colours) of an NCLR of any size."""
    assert nclr[:4] == b'RLCN' and nclr[0x10:0x14] == b'TTLP'
    size, off = struct.unpack_from('<II', nclr, 0x20)
    return 0x18 + off, list(struct.unpack_from(f'<{size // 2}H', nclr, 0x18 + off))

# ---------------------------------------------------------------------------------------------------- trainer card pictures

def card_decode(ncgr):
    """80 x 80 index bytes (row-major) of a trainer card avatar NCGR (8 bpp, tiled)."""
    th, tw, depth, _, tiled, size, off = struct.unpack_from('<HHIIIII', ncgr, 0x18)
    assert depth == 4 and tiled == 0 and size == 6400, (depth, tiled, size)
    raw = ncgr[0x18 + off:0x18 + off + size]
    out = bytearray(6400)
    for t in range(100):
        for j in range(64):
            out[(t // 10 * 8 + j // 8) * 80 + t % 10 * 8 + j % 8] = raw[t * 64 + j]
    return bytes(out)

def card_encode(ncgr, pix):
    th, tw, depth, _, tiled, size, off = struct.unpack_from('<HHIIIII', ncgr, 0x18)
    raw = bytearray(6400)
    for t in range(100):
        for j in range(64):
            raw[t * 64 + j] = pix[(t // 10 * 8 + j // 8) * 80 + t % 10 * 8 + j % 8]
    out = bytearray(ncgr)
    out[0x18 + off:0x18 + off + size] = raw
    return bytes(out)

def cardpic_import(folder, entries, art_folder):
    """{file: new bytes}: the still picture of the trainer folder `art_folder` into every avatar of `folder`."""
    meta = read_json(os.path.join(folder, 'sprite.json'))
    rgbs = read_pal(os.path.join(art_folder, 'palette.pal'))
    pix = read_png(os.path.join(art_folder, 'static.png'), rgbs, 80, 80)
    pix = bytes(0 if v == 0 else 64 + v for v in pix)     # the card loads NCLR colours 0-15 into BG colours 64-79
    out = {}
    for f in meta['ncgr']:
        out[f] = card_encode(entries[f], pix)
    for f in meta['nclr']:
        nclr = bytearray(entries[f])
        at, cols = nclr_colors_any(nclr)
        for base in (0, 64):                              # Black 2's avatar palettes hold the 16 colours at both
            struct.pack_into('<15H', nclr, at + 2 * (base + 1), *[rgb_to_bgr555(c) for c in rgbs[1:16]])
        out[f] = bytes(nclr)
    return out

# ---------------------------------------------------------------------------------------------------- cells (previews)

OBJ_SIZES = {(0, 0): (8, 8), (0, 1): (16, 16), (0, 2): (32, 32), (0, 3): (64, 64), (1, 0): (16, 8), (1, 1): (32, 8),
             (1, 2): (32, 16), (1, 3): (64, 32), (2, 0): (8, 16), (2, 1): (8, 32), (2, 2): (16, 32), (2, 3): (32, 64)}

def ncer_cells(ncer):
    """Cells of an NCER: [[(x, y, w, h, texture x, texture y, hflip, vflip)]] with x, y = the picture's top-left."""
    assert ncer[:4] == b'RECN' and ncer[0x10:0x14] == b'KBEC'
    n, attr, celloff = struct.unpack_from('<HHI', ncer, 0x18)
    base = 0x18 + celloff; csz = 16 if attr & 1 else 8; oambase = base + n * csz
    cells = []
    for i in range(n):
        no, _, oo = struct.unpack_from('<HHI', ncer, base + csz * i)
        objs = []
        for j in range(no):
            a0, a1, a2 = struct.unpack_from('<HHH', ncer, oambase + oo + 6 * j)
            y = a0 & 0xff; y -= 256 if y >= 128 else 0
            x = a1 & 0x1ff; x -= 512 if x >= 256 else 0
            w, h = OBJ_SIZES[(a0 >> 14, a1 >> 14)]
            if a0 >> 8 & 3 == 3: x += w // 2; y += h // 2     # affine double-size box
            t = a2 & 0x3ff
            objs.append((x, y, w, h, t % 32 * 8, t // 32 * 8, a1 >> 12 & 1, a1 >> 13 & 1))
        cells.append(objs)
    return cells

def whole_figure_cell(cells):
    """The cell that holds the whole figure (largest area)."""
    return max(range(len(cells)), key=lambda i: sum(o[2] * o[3] for o in cells[i]))

def render_cell(parts_img, cell):
    """Draw one cell from the 256x128 parts picture (PIL RGBA). Returns (image, (min x, min y))."""
    from PIL import Image, ImageOps
    x0 = min(o[0] for o in cell); y0 = min(o[1] for o in cell)
    x1 = max(o[0] + o[2] for o in cell); y1 = max(o[1] + o[3] for o in cell)
    img = Image.new('RGBA', (x1 - x0, y1 - y0), (0, 0, 0, 0))
    for x, y, w, h, tx, ty, hf, vf in reversed(cell):
        piece = parts_img.crop((tx, ty, tx + w, ty + h))
        if hf: piece = ImageOps.mirror(piece)
        if vf: piece = ImageOps.flip(piece)
        img.alpha_composite(piece, (x - x0, y - y0))
    return img, (x0, y0)

# ---------------------------------------------------------------------------------------------------- previews

def _rgba(folder, name):
    from PIL import Image
    return Image.open(os.path.join(folder, name)).convert('RGBA')

def preview_strip(folder, scale=3):
    """One row of the folder's frames (overworld) or still / parts (trainer, mcss), as a PIL image."""
    from PIL import Image
    meta = read_json(os.path.join(folder, 'sprite.json'))
    if 'copy_of' in meta:
        parent = os.path.dirname(folder)
        folder = next(os.path.join(parent, d) for d in sorted(os.listdir(parent))
                      if d.split('-')[0].isdigit() and int(d.split('-')[0]) == int(meta['copy_of']))
        meta = read_json(os.path.join(folder, 'sprite.json'))
    if meta['kind'] == 'overworld':
        ims = [_rgba(folder, f'frame_{i:02d}.png') for i in range(meta['frames'])]
    else:
        ims = [_rgba(folder, f'{k}.png') for k in ('static', 'parts') if os.path.exists(os.path.join(folder, f'{k}.png'))]
    W = sum(i.width for i in ims) + 4 * (len(ims) - 1); H = max(i.height for i in ims)
    out = Image.new('RGBA', (W, H), (0, 0, 0, 0)); x = 0
    for i in ims: out.alpha_composite(i, (x, H - i.height)); x += i.width + 4
    return out.resize((out.width * scale, out.height * scale), Image.NEAREST)

def preview(rows, out_path, scale=3, labels=None):
    """Stack strips (PIL images or folders) on a checker-free mid-tone background with optional labels."""
    from PIL import Image, ImageDraw
    strips = [r if hasattr(r, 'size') else preview_strip(r, scale) for r in rows]
    pad = 14 if labels else 0
    W = max(s.width for s in strips) + 8; H = sum(s.height + pad + 6 for s in strips) + 2
    img = Image.new('RGBA', (W, H), (96, 128, 144, 255)); d = ImageDraw.Draw(img); y = 2
    for k, s in enumerate(strips):
        if labels: d.text((4, y), labels[k], fill=(255, 255, 255, 255)); y += pad
        img.alpha_composite(s, (4, y)); y += s.height + 6
    img.convert('RGB').save(out_path)

# ---------------------------------------------------------------------------------------------------- self-check

def check(files=SRC_FILES, verbose=True):
    """Every overworld sheet and every trainer sprite: export to PNG files, import, compare bytes."""
    import tempfile, time
    t0 = time.time()
    sheets = narc_entries(arc_path(files, ARC_OW_SHEETS)); table = ow_table(files)
    by_sheet = {}
    for code in list(range(377)) + list(range(0x1000, 0x126C)) + list(range(0x2000, 0x200B)):
        r = table[obj_record(code)]
        if r['entityType'] == 1 and sheets[r['res1']][:4] == b'BTX0': by_sheet.setdefault(r['res1'], code)
    ok = bad = 0
    with tempfile.TemporaryDirectory() as tmp:
        for sheet, code in sorted(by_sheet.items()):
            d = os.path.join(tmp, f'ow{code}')
            ow_export(files, code, d, sheets, table)
            new = ow_import(d, sheets[sheet])
            if new == sheets[sheet]: ok += 1
            else: bad += 1; print('overworld code', code, 'sheet', sheet, 'DIFFERS')
        n_btx = sum(1 for s in sheets if s[:4] == b'BTX0')
        print(f'overworld: {ok}/{len(by_sheet)} sheets byte-identical after PNG export/import '
              f'({n_btx} BTX0 sheets in a/0/4/8, {n_btx - len(by_sheet)} not used by any object code) {time.time() - t0:.0f}s')
        for side, arc in ARC_TR.items():
            ents = narc_entries(arc_path(files, arc)); good = 0; n = len(ents) // 8; lz_ok = lz_n = 0
            for s in range(n):
                d = os.path.join(tmp, f'{side}{s}')
                tr_export(files, side, s, d, ents)
                out = tr_import(d, ents)
                if all(out[k] == ents[k] for k in out): good += 1
                else: print(side, s, 'DIFFERS')
                for k in (TR_STATIC, TR_PARTS):    # forced recompression, not the unchanged shortcut
                    old = ents[8 * s + k]; kind = 'static' if k == TR_STATIC else 'parts'
                    lz_n += 1; lz_ok += tr_encode_image(old, kind, tr_decode_image(old, kind)[2]) == old
            print(f'trainer {side}: {good}/{n} sprites byte-identical after PNG export/import; '
                  f'{lz_ok}/{lz_n} picture files re-encoded + LZ11-recompressed byte-identical {time.time() - t0:.0f}s')
        ents = narc_entries(arc_path(files, 168)); d = os.path.join(tmp, 'intro')   # intro professor (ov294)
        mcss_export(files, 168, {'parts': 25, 'palette': 28}, d, dict(kind='mcss'), ents)
        same = all(v == ents[k] for k, v in mcss_import(d, ents).items())
        lz = tr_encode_image(ents[25], 'parts', tr_decode_image(ents[25], 'parts')[2]) == ents[25]
        print(f'intro professor (a/1/6/8 25+28): {"byte-identical" if same else "DIFFERS"}, LZ11 recompression '
              f'{"byte-identical" if lz else "DIFFERS"}')
        bad += (not same) + (not lz)
        d22 = ents[22]; tsame = True                       # intro gender choice: 8 bpp model textures
        for name in ('int_swan_m.1', 'int_swan_m.2', 'int_swan_f.1', 'int_swan_f.2'):
            dt = os.path.join(tmp, name)
            tex_export(files, 168, 22, name, dt, ents)
            tsame &= tex_import(dt, d22) == d22
        print(f'intro gender-choice textures (a/1/6/8 22): {"byte-identical" if tsame else "DIFFERS"}')
        bad += not tsame
        e30 = narc_entries(arc_path(files, 30)); osame = True     # player icons = the overworld frames, in place
        sh = narc_entries(arc_path(files, ARC_OW_SHEETS))
        for code, pal, ncgrs in ((231, 4, (5, 14, 20)), (240, 6, (7, 17, 23))):
            sheet_frames = [bytes(f[3]) for f in btx_decode(sh[ow_sheet_of(files, code, table)[0]])[0]]
            for f in ncgrs:
                fr = objframes_decode(e30[f])
                order = [sheet_frames.index(x) for x in fr]
                osame &= objframes_encode(e30[f], [sheet_frames[k] for k in order]) == e30[f]
        print(f'player icons (a/0/3/0): {"every frame is an overworld frame, re-encoded byte-identical" if osame else "DIFFERS"}')
        bad += not osame
        e40 = narc_entries(arc_path(files, 40))                 # trainer card avatars
        csame = all(card_encode(e40[f], card_decode(e40[f])) == e40[f] for f in range(16, 32))
        print(f'trainer card pictures (a/0/4/0 16-31): {"byte-identical" if csame else "DIFFERS"}')
        bad += not csame
    return bad == 0

# ---------------------------------------------------------------------------------------------------- CLI

def main(argv):
    if not argv or argv[0] in ('-h', '--help'):
        print(__doc__); return
    cmd, args = argv[0], argv[1:]
    files = os.environ.get('B2_FILES', SRC_FILES)
    if cmd == 'ow-export':
        print(ow_export(files, int(args[0], 0), args[1]))
    elif cmd == 'ow-import':
        meta = read_json(os.path.join(args[0], 'sprite.json'))
        sheet, _ = ow_sheet_of(files, meta['code'])
        btx = narc_entries(arc_path(files, ARC_OW_SHEETS))[sheet]
        new = ow_import(args[0], btx)
        open(args[1], 'wb').write(new)
        print(args[1], len(new), 'bytes,', 'identical to the game' if new == btx else 'changed')
    elif cmd == 'tr-export':
        print(tr_export(files, args[0], int(args[1]), args[2]))
    elif cmd == 'mcss-export':
        arc, parts, pal = (int(a, 0) for a in args[:3])
        print(mcss_export(files, arc, {'parts': parts, 'palette': pal}, args[3], dict(kind='mcss')))
    elif cmd in ('tr-import', 'mcss-import'):
        meta = read_json(os.path.join(args[0], 'sprite.json'))
        ents = narc_entries(arc_path(files, meta['archive']))
        os.makedirs(args[1], exist_ok=True)
        for k, data in mcss_import(args[0], ents).items():
            open(os.path.join(args[1], f'{k}.bin'), 'wb').write(data)
            print(f'{k}.bin', len(data), 'bytes,', 'identical' if data == ents[k] else 'changed')
    elif cmd == 'tex-export':
        print(tex_export(files, int(args[0]), int(args[1]), args[2], args[3]))
    elif cmd == 'preview':
        rows = [args[2], args[0]] if len(args) > 2 else [args[0]]
        preview(rows, args[1], labels=['before', 'after'] if len(args) > 2 else None)
    elif cmd == 'check':
        sys.exit(0 if check(files) else 1)
    else:
        sys.exit(f'unknown command {cmd}\n' + __doc__)

if __name__ == '__main__':
    main(sys.argv[1:])
