"""Black 2's game-clear sequence for Hoenn (halloffame agent, 2026-10-07; notes/STORY_HANDOFFS.md "From halloffame").

The Hall of Fame room (zone 57, src/field_scripts/0114_room_EverGrandeCity_HallOfFame.s) ends with Black 2's own
`CallGameClear` (script command 342 -> ov012 EventGameClear, decomp src/ov012/event_game_clear.c). Its state list
(SetGameClearStatusSequence): field close, the Hall of Fame record screen (ov265), [first clear: the Unova Link key
screen (ov332) when the key is new], global script 9601 (src/field_scripts/1242_global_9600.s: heal, respawn, the place
Continue loads), the save (ov295), field open + EventMapChangeEnding to zone 0x8b at sEndingPositionA + script 1 of that
zone, field close, the credits (ov266), field open + EventMapChangeEnding to zone 0x1ab at sEndingPositionB + script 0x20
of that zone, BGM fade, field close, SEQ_BGM_THEEND, THE END (ov267), done.

apply_code (ov012, same-size byte edits; nothing moves inside the overlay):
  - the two hard-coded ending zones: 0x8b (Black 2's Pokémon League plaza; here Shoal Cave's ice room) and 0x1ab (Aspertia
    City), whose scripts 1 and 0x20 are Black 2's Unova ending scenes -> the Hall of Fame room (zone 57) both times, at
    the machine (zone tile (8, 5)), scripts 1 and 3 there (both end at once: the screen stays black, as Sapphire has no
    field scene between the record and the credits nor after them).
    EventGameClear_Callback state 15 `mov r2, #0x8b` (0x0215a342), literal 0x1ab (0x0215a47c), sEndingPositionA/B
    (.rodata 0x0216cb44 / 0x0216cb38: VecFx32, tile * 16 units), state 17 `mov r1, #0x1` (0x0215a38e), state 18
    `mov r1, #0x20` (0x0215a3ba).
  - the first clear's Challenge Mode key screen (state 11, the Unova Link proc) is left out: SetGameClearStatusSequence
    `mov r2, #0xb` (0x0215a560) -> 13 (a 60-frame wait). The record screen goes straight to the save (user, 2026-10-07).
apply (a/2/1/5, the credits' pictures; ov266 reads them, decoded from its code):
  - the command list is file 1 (16-byte records: u32 message (0xffff none), u16 frames, u8 command, u8 param, ...);
    command 8 shows picture `param` (0-11) for `frames` with fades, on the top or bottom screen (byte 10: 3 / 4), files
    0x15 + 12 * picture + 3 * gender (girl) + 0 NCLR / 1 NCGR (8bpp, 768 tiles) / 2 NSCR (256x256, 256 colours): the
    "photos" are 224x160 at (16, 16) (screen rows 2-21, columns 2-29 = tiles 1-560), colour 0 transparent. Command 9 (one,
    before the last photo) shows files 10/11/12 (a 256x192 picture, identity screen) with a sprite over it (files 6-9: ClAct,
    NCLR / NCGR / NCER / NANR).
  - Black 2's photos are greyscale Unova scenes with the player (and Unova characters) in colour; command 9's is N with
    Zekrom. They are replaced by data/credits/*.png (indexed PNGs made by work/agents/halloffame/tools/credits_pics.py from
    emulator shots of our own Hoenn maps: Black 2's art), same sizes, so the archive keeps its size; the sprite over
    command 9's picture is made transparent (its tiles zeroed). The staff text (message file 369) is Black 2's, unchanged.
"""
import os, json, struct, sys
import narcio
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))

OV012_BASE = 0x021503c0
HOF_ZONE = 57                                   # EverGrandeCity_HallOfFame (data/interiors/57.json)
HOF_TILE = (8, 5)                               # zone tile in front of the machine (Sapphire (7, 5))
SCRIPT_BEFORE, SCRIPT_AFTER = 1, 3              # 0114_room_EverGrandeCity_HallOfFame.s: Script_None, HF_AfterCredits

def _thumb_mov(rd, imm):
    assert 0 <= imm < 256
    return bytes([imm, 0x20 | rd])

EDITS = [  # (address, Black 2's bytes, ours)
    (0x0215a342, _thumb_mov(2, 0x8b), _thumb_mov(2, HOF_ZONE)),
    (0x0215a47c, struct.pack('<I', 0x1ab), struct.pack('<I', HOF_ZONE)),
    (0x0216cb44, struct.pack('<iii', 31 * 16 << 12, 47 * 16 << 12, 16 << 12),
     struct.pack('<iii', HOF_TILE[0] * 16 << 12, 0, HOF_TILE[1] * 16 << 12)),
    (0x0216cb38, struct.pack('<iii', 43 * 16 << 12, 16 << 12, 757 * 16 << 12),
     struct.pack('<iii', HOF_TILE[0] * 16 << 12, 0, HOF_TILE[1] * 16 << 12)),
    (0x0215a38e, _thumb_mov(1, 0x01), _thumb_mov(1, SCRIPT_BEFORE)),
    (0x0215a3ba, _thumb_mov(1, 0x20), _thumb_mov(1, SCRIPT_AFTER)),
    # first clear: no Black 2 "Challenge Mode key obtained" screen (user, 2026-10-07): SetGameClearStatusSequence's
    # states[6] = 11 (the Unova Link proc, ov332) becomes 13 (a 60-frame wait, as states[7])
    (0x0215a560, _thumb_mov(2, 0x0b), _thumb_mov(2, 0x0d)),
]

def apply_code(code):
    path = os.path.join(code, 'arm9_ov012.bin')
    d = bytearray(open(path, 'rb').read())
    for addr, old, new in EDITS:
        o = addr - OV012_BASE
        assert d[o:o + len(old)] in (old, new), f'ov012 {addr:#x}: {d[o:o + len(old)].hex()} is not Black 2\'s'
        d[o:o + len(new)] = new
    if os.path.islink(path): os.unlink(path)
    open(path, 'wb').write(d)
    return f'EventGameClear: ending zones 0x8b/0x1ab -> {HOF_ZONE} at {HOF_TILE}, scripts {SCRIPT_BEFORE}/{SCRIPT_AFTER}; no key screen'

# ---- the credits' pictures (a/2/1/5) -------------------------------------------------------------------------------
ARC = 215
PIC_FIRST, PICS = 0x15, 12
CMD9 = 10                                       # files 10/11/12
SPRITE_NCGR = 7                                 # the sprite over command 9's picture (ClAct files 6-9)
DATA = os.path.join(ROOT, 'data', 'credits')

def _png_indexed(path):
    from PIL import Image
    im = Image.open(path)
    assert im.mode == 'P' and im.size == (256, 192), f'{path}: indexed 256x192 PNG expected ({im.mode} {im.size})'
    pal = im.getpalette()[:768]
    pal += [0] * (768 - len(pal))
    return bytes(im.getdata()), [tuple(pal[i * 3:i * 3 + 3]) for i in range(256)]

def _bgr555(rgb):
    return sum(((c * 31 + 127) // 255) << (5 * i) for i, c in enumerate(rgb))

def _encode(template_nclr, template_ncgr, template_nscr, pix, pal, photo):
    """The three files for a 256x192 palette-index picture, built on Black 2's own files (same headers and sizes).
    photo: tiles of screen rows 2-21, columns 2-29 only (1..560, tile 0 blank, the rest 0); else the whole screen
    (identity map, tiles 0..767)."""
    nclr = bytearray(template_nclr)
    size, off = struct.unpack_from('<II', nclr, 0x20)
    assert size == 0x200
    struct.pack_into('<256H', nclr, 0x18 + off, *[_bgr555(c) for c in pal])
    ncgr = bytearray(template_ncgr)
    th, tw, depth, mapping, tiled, dsize, doff = struct.unpack_from('<HHIIIII', ncgr, 0x18)
    assert depth == 4 and dsize == 768 * 64, (depth, dsize)
    base = 0x18 + doff
    nscr = bytearray(template_nscr)
    w, h, mode, _, ssize = struct.unpack_from('<HHHHI', nscr, 0x18)
    assert (w, h, mode, ssize) == (256, 256, 1, 2048)
    ents = [0] * 1024
    tiles = []
    for ty in range(24):
        for tx in range(32):
            if photo and not (2 <= ty <= 21 and 2 <= tx <= 29):
                continue
            tiles.append((ty, tx, bytes(pix[(ty * 8 + y) * 256 + tx * 8 + x] for y in range(8) for x in range(8))))
    data = bytearray(768 * 64)
    for k, (ty, tx, t) in enumerate(tiles):
        n = k + 1 if photo else k
        data[n * 64:n * 64 + 64] = t
        ents[ty * 32 + tx] = n
    ncgr[base:base + len(data)] = data
    struct.pack_into('<1024H', nscr, 0x24, *ents)
    return bytes(nclr), bytes(ncgr), bytes(nscr)

def apply(files):
    spec = os.path.join(DATA, 'credits.json')
    if not os.path.exists(spec):
        return 'credits: no data/credits/credits.json (Black 2\'s pictures kept)'
    cfg = json.load(open(spec))
    e = narcio.load(files, ARC)
    sizes = [len(x) for x in e]
    done = []
    for p in range(PICS):
        for g, gname in enumerate(('m', 'f')):
            name = cfg['photos'][p][gname]
            pix, pal = _png_indexed(os.path.join(DATA, name))
            b = PIC_FIRST + 12 * p + 3 * g
            e[b], e[b + 1], e[b + 2] = _encode(e[b], e[b + 1], e[b + 2], pix, pal, True)
        done.append(cfg['photos'][p].get('place', str(p)))
    pix, pal = _png_indexed(os.path.join(DATA, cfg['final']['file']))
    e[CMD9], e[CMD9 + 1], e[CMD9 + 2] = _encode(e[CMD9], e[CMD9 + 1], e[CMD9 + 2], pix, pal, False)
    spr = bytearray(e[SPRITE_NCGR])
    assert spr[:4] == b'RGCN' and spr[0x10:0x14] == b'RAHC'
    dsize, doff = struct.unpack_from('<II', spr, 0x28)
    spr[0x18 + doff:0x18 + doff + dsize] = bytes(dsize)
    e[SPRITE_NCGR] = bytes(spr)
    assert [len(x) for x in e] == sizes, 'a credits file changed size'
    narcio.save(files, ARC, e)
    return f'credits: {PICS} Hoenn photos x 2 ({", ".join(done)}), final picture {cfg["final"].get("place", "")}, its sprite cleared'
