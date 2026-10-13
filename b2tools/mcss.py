"""MCSS sprite animations (trainer and Pokémon battle sprites): read the cell / multi-cell animation files, pose and
draw a sprite at any tick, and move a new picture onto an existing sprite's parts.

Files of a trainer sprite s in a/0/7/1 (front) or a/0/7/2 (back), see sprites.py: +2 NCER cells, +3 NANR cell
animations (LZ11), +4 NMCR multi-cells, +5 NMAR multi-cell animations, +6 MCSS quad table. Formats are Nintendo's G2D
ones (NitroSDK nnsys/g2d), read here only as far as these files use them [checked on all 188 front sprites: the last
tick of animation 0 draws the same picture as animation 1 for 154 of them, the rest differ by a few pixels]:

  NANR / NMAR, section 'KNBA' at 0x10, data at 0x18: u16 sequences, u16 frames, u32 sequence array, u32 frame array,
      u32 result array (offsets from 0x18). Sequence (16 bytes): u16 frames, u16 loop start, u16 result type (0 index,
      1 index + rotation/scale/translation, 2 index + translation), u16 animation type, u32 play mode (1 once,
      2 loop), u32 offset of its first frame in the frame array. Frame (8 bytes): u32 result offset, u16 ticks,
      u16 pad. Results: type 0 u16 index; type 1 u16 index, u16 rotation (65536 = full turn), fx32 scale x, y,
      s16 x, y; type 2 u16 index, u16 pad, s16 x, y. NANR indices are cells, NMAR indices are multi-cells.
  NMCR, section 'KBCM' at 0x10, data at 0x18: u16 multi-cells, u16 pad, u32 multi-cell array, u32 node array.
      Multi-cell (8 bytes): u16 nodes, u16 cell animations, u32 offset of its first node. Node (8 bytes): u16 NANR
      sequence, s16 x, s16 y, u16 attributes (cell animation index << 8 | visibility).
  +6 (MCSS quads): u32 count (= cells), 8 bytes 0, then per cell 48 bytes: s32 x * 256, s32 -y * 256,
      s32 w * 4096, s32 h * 4096, s32 u * 4096, s32 v * 4096, 24 bytes 0 = the cell's bounding box on screen (cell
      coordinates) and in the 256x128 texture; it equals the NCER cell's OBJ rectangles' bounding box.

Battle use (trainers): NMAR sequence 0 is the intro gesture (played once; multi-cell 0 = the parts), sequence 1 loops
the still figure (multi-cell 1 = one node showing the whole-figure cell). A node's cell is drawn rotated/scaled about
the cell's own (0, 0) and moved to node position + result translation; nodes listed first are drawn on top, and so are
a cell's first OBJs.
"""
import math, os, struct, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sprites  # noqa: E402


def _unlz(d):
    return sprites.lz11_decompress(d) if d[:1] == b'\x11' else d


def parse_anim(d):
    """NANR or NMAR -> [dict(etype, mode, loop, frames=[(ticks, result)])]."""
    d = _unlz(d)
    assert d[0x10:0x14] == b'KNBA', d[:4]
    base = 0x18
    nseq, _, pseq, pfr, pres = struct.unpack_from('<HHIII', d, base)
    seqs = []
    for i in range(nseq):
        n, loop, etype, atype, mode, pf = struct.unpack_from('<HHHHII', d, base + pseq + 16 * i)
        frames = []
        for j in range(n):
            pc, dur, _ = struct.unpack_from('<IHH', d, base + pfr + pf + 8 * j)
            at = base + pres + pc
            if etype == 0:
                r = dict(idx=struct.unpack_from('<H', d, at)[0], at=at)
            elif etype == 1:
                idx, rot, sx, sy, px, py = struct.unpack_from('<HHiihh', d, at)
                r = dict(idx=idx, rot=rot, sx=sx / 4096, sy=sy / 4096, px=px, py=py, at=at)
            else:
                idx, _, px, py = struct.unpack_from('<HHhh', d, at)
                r = dict(idx=idx, px=px, py=py, at=at)
            frames.append((dur, r))
        seqs.append(dict(etype=etype, atype=atype, mode=mode, loop=loop, frames=frames))
    return seqs


def parse_nmcr(d):
    d = _unlz(d)
    assert d[0x10:0x14] == b'KBCM'
    base = 0x18
    n, _, pdata, phier = struct.unpack_from('<HHII', d, base)
    mcs = []
    for i in range(n):
        nn, nca, ph = struct.unpack_from('<HHI', d, base + pdata + 8 * i)
        nodes = []
        for j in range(nn):
            seq, x, y, attr = struct.unpack_from('<HhhH', d, base + phier + ph + 8 * j)
            nodes.append(dict(seq=seq, x=x, y=y, attr=attr))
        mcs.append(nodes)
    return mcs


class Sprite:
    """Cells and animations of MCSS sprite files (entries = the archive's files, first = file index of +0)."""
    def __init__(self, entries, first):
        e = entries
        self.cells = sprites.ncer_cells(e[first + 2])
        self.nanr = parse_anim(e[first + 3])
        self.nmcr = parse_nmcr(e[first + 4])
        self.nmar = parse_anim(e[first + 5])

    def length(self, anim):
        return sum(f[0] for f in self.nmar[anim]['frames'])


def seq_at(seq, t):
    total = sum(f[0] for f in seq['frames'])
    if total == 0:
        return seq['frames'][0][1]
    t = t % total
    for dur, r in seq['frames']:
        if t < dur:
            return r
        t -= dur
    return seq['frames'][-1][1]


def pose(sp, anim, t):
    """[(cell, (rotation radians, sx, sy, tx, ty), node index)] at tick t, top first."""
    mres = seq_at(sp.nmar[anim], t)
    out = []
    for k, node in enumerate(sp.nmcr[mres['idx']]):
        r = seq_at(sp.nanr[node['seq']], t)
        rot = r.get('rot', 0) / 65536 * 2 * math.pi
        out.append((r['idx'], (rot, r.get('sx', 1), r.get('sy', 1), node['x'] + r.get('px', 0) + mres.get('px', 0),
                               node['y'] + r.get('py', 0) + mres.get('py', 0)), k))
    return out


def cell_pixels(cell, tr):
    """For a cell placed with transform tr: arrays (screen x, screen y, texture u, texture v) of its pixels."""
    rot, sx, sy, tx, ty = tr
    c, s = math.cos(rot), math.sin(rot)
    X, Y, U, V = [], [], [], []
    for (x, y, w, h, u, v, hf, vf) in cell:
        jj, ii = np.mgrid[0:h, 0:w]
        px = (x + ii + 0.5) * sx; py = (y + jj + 0.5) * sy
        X.append(np.floor(px * c - py * s + tx).astype(int).ravel())
        Y.append(np.floor(px * s + py * c + ty).astype(int).ravel())
        U.append((u + (w - 1 - ii if hf else ii)).ravel()); V.append((v + (h - 1 - jj if vf else jj)).ravel())
    if not X:
        return [np.zeros(0, int)] * 4
    return [np.concatenate(a) for a in (X, Y, U, V)]


ORIGIN = (96, 128)        # where screen (0, 0) lands on render canvases
CANVAS = (192, 176)       # w, h


def render(sp, tex, anim, t, owner=False):
    """Index picture (CANVAS, ORIGIN) of the sprite at tick t from texture `tex` (128x256 indices). With
    owner=True also an array of the node drawn at each pixel (-1 = none)."""
    W, H = CANVAS
    img = np.zeros((H, W), np.uint8); own = np.full((H, W), -1, int)
    for ci, tr, k in reversed(pose(sp, anim, t)):
        for obj in reversed(sp.cells[ci]):
            X, Y, U, V = cell_pixels([obj], tr)
            X = X + ORIGIN[0]; Y = Y + ORIGIN[1]
            val = tex[V, U]
            ok = (val != 0) & (X >= 0) & (X < W) & (Y >= 0) & (Y < H)
            img[Y[ok], X[ok]] = val[ok]; own[Y[ok], X[ok]] = k
    return (img, own) if owner else img


def still_offset(sp, tex, still):
    """(dx, dy): canvas pixel (x + dx, y + dy) of animation 1 shows still pixel (x, y), found by matching."""
    a = render(sp, tex, 1, 0)
    ys, xs = np.nonzero(a); sy, sx = np.nonzero(still)
    if not len(ys) or not len(sy):
        return None
    best = None
    for dy in range(ys.min() - sy.min() - 3, ys.min() - sy.min() + 4):
        for dx in range(xs.min() - sx.min() - 3, xs.min() - sx.min() + 4):
            ok = (sy + dy >= 0) & (sy + dy < a.shape[0]) & (sx + dx >= 0) & (sx + dx < a.shape[1])
            score = (a[sy[ok] + dy, sx[ok] + dx] == still[sy[ok], sx[ok]]).mean()
            if best is None or score > best[0]:
                best = (score, dx, dy)
    return best[1], best[2]


def _nearest_fill(values, have):
    """For every pixel: the value of the nearest pixel where `have` is true (brute force by growing rings)."""
    H, W = values.shape
    out = values.copy(); done = have.copy()
    for _ in range(64):
        if done.all():
            break
        grow = out.copy(); got = done.copy()
        for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            sh = np.roll(np.roll(done, dy, 0), dx, 1); sv = np.roll(np.roll(out, dy, 0), dx, 1)
            take = ~got & sh
            grow[take] = sv[take]; got |= take
        out, done = grow, got
    return out, done


def distribute(sp, donor_tex, figure, outline=15):
    """New 128x256 texture: `figure` (CANVAS-sized index picture, ORIGIN) cut onto the donor's parts.

    - whole-figure cells (animation 1): the figure itself;
    - parts (animation 0, final tick = the still pose): each figure pixel goes to the node the donor shows there
      (or, where the donor has nothing, to the nearest node whose rectangle covers it); where the donor part had
      pixels hidden under other parts, the part is filled with its own nearest colours (not the outline), so moving
      parts do not open holes; a node's other cells (gesture frames) get the same figure region;
    - cells no animation uses at the final tick: cleared.
    Returns (texture, report dict)."""
    T0 = sp.length(0)
    blank = blank_cells(sp, donor_tex)
    final = [n for n in pose(sp, 0, T0 - 1) if n[0] not in blank]
    tex = np.zeros_like(donor_tex)
    H, W = figure.shape
    fig_on = figure != 0
    donor_img, donor_own = render(sp, donor_tex, 0, T0 - 1, owner=True)
    # nodes covering each canvas pixel (by rectangle), top first
    cover = {}
    for ci, tr, k in final:
        X, Y, _, _ = cell_pixels(sp.cells[ci], tr)
        X = X + ORIGIN[0]; Y = Y + ORIGIN[1]
        ok = (X >= 0) & (X < W) & (Y >= 0) & (Y < H)
        m = np.zeros((H, W), bool); m[Y[ok], X[ok]] = True
        cover[k] = m
    # owner of every figure pixel
    own = np.where(fig_on, donor_own, -1)
    for k in cover:                                  # donor's owner must cover the pixel by rectangle
        own[(own == k) & ~cover[k]] = -1
    need = fig_on & (own < 0)
    if need.any():
        filled, got = _nearest_fill(np.where(donor_own >= 0, donor_own, 0), donor_own >= 0)
        cand = np.where(got, filled, -1)
        for y, x in zip(*np.nonzero(need)):
            k = cand[y, x]
            if k >= 0 and cover.get(k, np.zeros((H, W), bool))[y, x]:
                own[y, x] = k
            else:                                     # any node whose rectangle covers it, topmost
                for _, _, kk in final:
                    if cover[kk][y, x]:
                        own[y, x] = kk; break
    lost = int((fig_on & (own < 0)).sum())
    # per node: its colours spread over the whole canvas (for under-painting)
    under = {}
    for _, _, k in final:
        mine = (own == k) & (figure != outline)
        if not mine.any():
            mine = own == k
        if mine.any():
            under[k] = _nearest_fill(np.where(mine, figure, 0), mine)[0]
    node_tr = {k: tr for _, tr, k in final}
    node_cells = {}
    for t in range(T0):
        for ci, tr, k in pose(sp, 0, t):
            if ci not in blank and k in node_tr:
                node_cells.setdefault(k, set()).add(ci)
    done_cells = set(blank)
    for ci, tr, k in final:                          # the final cell of each node first
        _paint_cell(sp, ci, tr, k, donor_tex, tex, figure, own, under, done_cells)
    for k, cis in node_cells.items():                # then its gesture cells, placed where the node ends
        for ci in sorted(cis):
            _paint_cell(sp, ci, node_tr[k], k, donor_tex, tex, figure, own, under, done_cells)
    for ci, tr, k in pose(sp, 1, 0):                 # whole figure
        X, Y, U, V = cell_pixels(sp.cells[ci], tr)
        X = X + ORIGIN[0]; Y = Y + ORIGIN[1]
        ok = (X >= 0) & (X < W) & (Y >= 0) & (Y < H)
        tex[V, U] = 0
        tex[V[ok], U[ok]] = figure[Y[ok], X[ok]]
        whole_lost = int(fig_on.sum() - (figure[Y[ok], X[ok]] != 0).sum())
        done_cells.add(ci)
    return tex, dict(lost_in_parts=lost, lost_in_whole=whole_lost, nodes=len(final))


def _paint_cell(sp, ci, tr, k, donor_tex, tex, figure, own, under, done):
    if ci in done:
        return
    done.add(ci)
    H, W = figure.shape
    X, Y, U, V = cell_pixels(sp.cells[ci], tr)
    if not len(X):
        return
    X = X + ORIGIN[0]; Y = Y + ORIGIN[1]
    ok = (X >= 0) & (X < W) & (Y >= 0) & (Y < H)
    val = np.zeros(len(X), np.uint8)
    xs, ys = X[ok], Y[ok]
    mine = own[ys, xs] == k
    v = np.where(mine, figure[ys, xs], 0)
    donor_on = donor_tex[V[ok], U[ok]] != 0
    if k in under:                                   # hidden donor pixels: the part's own colours continue
        fill = (~mine) & donor_on & (figure[ys, xs] != 0)
        v = np.where(fill, under[k][ys, xs], v)
    val[ok] = v
    tex[V, U] = val


def static_intro(nmar):
    """NMAR bytes whose sequence 0 (the intro gesture) shows multi-cell 1 (the still figure) on every frame: the
    sprite then stands still from the start. Same size; only the multi-cell indices of sequence 0 change."""
    d = bytearray(nmar)
    assert d[:1] != b'\x11', 'NMAR is stored uncompressed'
    seqs = parse_anim(bytes(d))
    still = seqs[1]['frames'][0][1]['idx']
    for _, r in seqs[0]['frames']:
        struct.pack_into('<H', d, r['at'], still)
    return bytes(d)


def blank_cells(sp, tex):
    return {ci for ci, cell in enumerate(sp.cells)
            if not any(tex[v:v + h, u:u + w].any() for (x, y, w, h, u, v, hf, vf) in cell)}


def coverage(sp, donor_tex):
    """(whole, parts): canvas masks of the pixels the whole-figure cell (animation 1) and the parts at the intro's
    last tick (non-blank cells, by rectangle) can show."""
    W, H = CANVAS
    blank = blank_cells(sp, donor_tex)
    out = []
    for anim, t in ((1, 0), (0, sp.length(0) - 1)):
        m = np.zeros((H, W), bool)
        for ci, tr, k in pose(sp, anim, t):
            if ci in blank:
                continue
            X, Y, _, _ = cell_pixels(sp.cells[ci], tr)
            X = X + ORIGIN[0]; Y = Y + ORIGIN[1]
            ok = (X >= 0) & (X < W) & (Y >= 0) & (Y < H)
            m[Y[ok], X[ok]] = True
        out.append(m)
    return tuple(out)


def distribute_pose(sp, donor_tex, figure, ref=(1, 0), keep=(), variants=None, outline=15, overlays=()):
    """distribute() for MCSS sets with several animations and multi-cells (e.g. the intro professor): the parts are
    cut from `figure` as the donor shows them at animation/tick `ref`; cells in `keep` (props such as a thrown Poke
    Ball) keep the donor's pixels; a cell that `ref` does not show is painted like the reference part whose cell
    sequence also shows it (the same body part in another pose), else straight from the figure where it first
    appears; `variants` = {cell: another figure} paints a cell from a changed picture (closed eyes, open mouth);
    cells in `overlays` are left out (neither owning figure pixels nor painted), for the caller to paint.
    Returns (texture, report)."""
    variants = variants or {}
    H, W = figure.shape
    blank = blank_cells(sp, donor_tex)
    skip = blank | set(keep) | set(overlays)        # overlays (blink / mouth strips): painted by the caller
    final = [n for n in pose(sp, *ref) if n[0] not in skip]
    tex = np.zeros_like(donor_tex)
    for ci in keep:                                   # props stay as drawn
        for (x, y, w, h, u, v, hf, vf) in sp.cells[ci]:
            tex[v:v + h, u:u + w] = donor_tex[v:v + h, u:u + w]
    fig_on = figure != 0
    _, donor_own = render(sp, donor_tex, ref[0], ref[1], owner=True)
    cover = {}
    for ci, tr, k in final:
        X, Y, _, _ = cell_pixels(sp.cells[ci], tr)
        X = X + ORIGIN[0]; Y = Y + ORIGIN[1]
        ok = (X >= 0) & (X < W) & (Y >= 0) & (Y < H)
        m = np.zeros((H, W), bool); m[Y[ok], X[ok]] = True
        cover[k] = m
    own = np.where(fig_on, donor_own, -1)
    for k in list(np.unique(own)):
        if k >= 0 and k in cover:
            own[(own == k) & ~cover[k]] = -1
        elif k >= 0:
            own[own == k] = -1
    need = fig_on & (own < 0)
    if need.any():
        filled, got = _nearest_fill(np.where(own >= 0, own, 0), own >= 0)
        for y, x in zip(*np.nonzero(need)):
            k = filled[y, x] if got[y, x] else -1
            if k >= 0 and cover[k][y, x]:
                own[y, x] = k
            else:
                for _, _, kk in final:
                    if cover[kk][y, x]:
                        own[y, x] = kk; break
    lost = int((fig_on & (own < 0)).sum())
    under = {}
    for _, _, k in final:
        mine = (own == k) & (figure != outline)
        if not mine.any():
            mine = own == k
        if mine.any():
            under[k] = _nearest_fill(np.where(mine, figure, 0), mine)[0]
    mref = seq_at(sp.nmar[ref[0]], ref[1])['idx']
    ref_seq = {k: sp.nmcr[mref][k]['seq'] for _, _, k in final}
    node_tr = {k: tr for _, tr, k in final}
    seq_cells = {s: {r['idx'] for _, r in sq['frames']} for s, sq in enumerate(sp.nanr)}
    done = set(skip)
    for ci, tr, k in final:
        _paint_cell(sp, ci, tr, k, donor_tex, tex, variants.get(ci, figure), own, under, done)
    first_use = {}                                    # every cell any node's cell animation shows (they loop on
    for nodes in sp.nmcr:                             # their own timers, longer than some multi-cell animations)
        for node in nodes:
            for _, r in sp.nanr[node['seq']]['frames']:
                tr = (r.get('rot', 0) / 65536 * 2 * math.pi, r.get('sx', 1), r.get('sy', 1),
                      node['x'] + r.get('px', 0), node['y'] + r.get('py', 0))
                first_use.setdefault(r['idx'], (node['seq'], tr))
    raw = []
    for ci, (seq, tr) in sorted(first_use.items()):
        if ci in done:
            continue
        k = next((k for k, s in ref_seq.items() if seq_cells[s] & seq_cells[seq]), None)
        if k is not None:
            _paint_cell(sp, ci, node_tr[k], k, donor_tex, tex, variants.get(ci, figure), own, under, done)
        else:                                         # a part only another pose shows: the figure where it is
            fig = variants.get(ci, figure)
            X, Y, U, V = cell_pixels(sp.cells[ci], tr)
            X = X + ORIGIN[0]; Y = Y + ORIGIN[1]
            ok = (X >= 0) & (X < W) & (Y >= 0) & (Y < H)
            tex[V, U] = 0
            tex[V[ok], U[ok]] = fig[Y[ok], X[ok]]
            done.add(ci); raw.append(ci)
    return tex, dict(lost=lost, nodes=len(final), raw_cells=raw)


def node_offsets(nmcr):
    """{(multi-cell, node): byte offset of the node's 8-byte record} of an uncompressed NMCR."""
    assert nmcr[:1] != b'\x11', 'NMCR is stored uncompressed'
    base = 0x18
    n, _, pdata, phier = struct.unpack_from('<HHII', nmcr, base)
    out = {}
    for i in range(n):
        nn, nca, ph = struct.unpack_from('<HHI', nmcr, base + pdata + 8 * i)
        for j in range(nn):
            out[(i, j)] = base + phier + ph + 8 * j
    return out


def move_nodes(nmcr, moves):
    """NMCR bytes with nodes moved: moves = [{"seq": NANR sequence, "x": x, "y": y}]: every node (in every
    multi-cell) that plays that cell animation gets position (x, y). Same size (two s16 per node)."""
    d = bytearray(nmcr)
    for (i, j), at in node_offsets(nmcr).items():
        seq = struct.unpack_from('<H', d, at)[0]
        for m in moves:
            if m['seq'] == seq:
                struct.pack_into('<hh', d, at + 2, int(m['x']), int(m['y']))
    return bytes(d)


def set_nodes(nmcr, edits):
    """NMCR bytes with single nodes changed: edits = [{"mc": multi-cell, "node": node, and any of "seq" (the cell
    animation it plays), "x", "y"}]. Same size."""
    d = bytearray(nmcr)
    at = node_offsets(nmcr)
    for m in edits:
        o = at[(int(m['mc']), int(m['node']))]
        if 'seq' in m:
            struct.pack_into('<H', d, o, int(m['seq']))
        if 'x' in m:
            struct.pack_into('<h', d, o + 2, int(m['x']))
        if 'y' in m:
            struct.pack_into('<h', d, o + 4, int(m['y']))
    return bytes(d)


def still_translations(nmar, seq, mcs):
    """NMAR bytes whose sequence `seq` no longer moves the multi-cells `mcs` (their frames' translations set to 0;
    result types 1 and 2). Same size."""
    d = bytearray(nmar)
    assert d[:1] != b'\x11', 'NMAR is stored uncompressed'
    sq = parse_anim(bytes(d))[seq]
    at = {1: 12, 2: 4}[sq['etype']]                  # result types with a translation: offset of its s16 x, y
    for _, r in sq['frames']:
        if r['idx'] in mcs:
            struct.pack_into('<hh', d, r['at'] + at, 0, 0)
    return bytes(d)
