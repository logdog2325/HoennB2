"""Black 2's fonts (a/0/2/3, Nitro NFTR files) for measuring text widths (hoenn_pokedex, 2026-10-08).

Format read from the decomp (src/system/gf_font.c) and checked on the files: FINF after the header (line feed, the
default widths, offsets of CGLP / CWDH / CMAP data); each glyph cell in CGLP is (left, width, advance) + 2bpp pixels;
the character maps are direct (0), table (1) or sorted pairs (2), chained by `next` (the last map, method 2 with
0..0xFFFF, ends the walk). A character's advance is its cell's third byte (GFL_FontGlyphCopy `info->advance`).
Check: font 0 measures Black 2's longest Pokédex entry lines (system 0442) at exactly 222 px, the entry window's
28 tiles minus its x = 2."""
import os, struct, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
VANILLA = os.path.join(HERE, '..', 'external', 'pokebw2', 'build', 'b2_us', 'files')


class Font:
    def __init__(self, data):
        assert data[:4] == b'RTFN', data[:4]
        self.d = d = data
        finf = struct.unpack_from('<H', d, 0xC)[0] + 8
        self.linefeed = d[finf + 1]
        self.alter = struct.unpack_from('<H', d, finf + 2)[0]
        self.pglp, _, pcmap = struct.unpack_from('<III', d, finf + 8)
        self.cellsize = struct.unpack_from('<H', d, self.pglp + 2)[0]
        self.cmap = {}
        p = pcmap
        while p and p + 12 <= len(d):
            first, last, method, _, nxt = struct.unpack_from('<HHHHI', d, p)
            data = p + 12
            if method == 0:
                base = struct.unpack_from('<H', d, data)[0]
                for c in range(first, last + 1): self.cmap.setdefault(c, base + c - first)
            elif method == 1:
                for i, c in enumerate(range(first, last + 1)):
                    g = struct.unpack_from('<H', d, data + 2 * i)[0]
                    if g != 0xFFFF: self.cmap.setdefault(c, g)
            else:
                for i in range(struct.unpack_from('<H', d, data)[0]):
                    c, g = struct.unpack_from('<HH', d, data + 2 + 4 * i)
                    self.cmap.setdefault(c, g)
            if method == 2 and first == 0 and last == 0xFFFF: break
            p = nxt

    def has(self, ch):
        return ord(ch) in self.cmap

    def advance(self, ch):
        g = self.cmap.get(ord(ch), self.alter)
        return self.d[self.pglp + 8 + g * self.cellsize + 2]

    def width(self, s):
        return sum(self.advance(c) for c in s)


def load(n=0, files=VANILLA):
    import narcio
    return Font(narcio.load(files, 23)[n])
