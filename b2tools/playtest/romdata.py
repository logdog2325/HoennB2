"""What the game's ROM holds (read only, from the release clone): zone headers, entities, map collision, moves.
Used by the playthrough driver to route walks (the same data the game walks on)."""
import os, sys, struct, functools
ROOT = os.path.expanduser('~/Documents/GitHub/HoennB2')
sys.path.insert(0, os.path.join(ROOT, 'b2tools'))
import importlib.util
_spec = importlib.util.spec_from_file_location('npc_check_tool', os.path.join(ROOT, 'b2tools', 'npc_check.py'))
NC = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(NC)
import zoneheaders
from zones import parse_entities
from terrain import heights as H

SURF = {0x3d, 0x3e, 0x3f, 0x42, 0x43, 0x40, 0x94, 0x95, 0x96, 0x97}
WALL_SIDES = {0x51: 'e', 0x52: 'w', 0x53: 'n', 0x54: 's', 0x55: 'ne', 0x56: 'nw', 0x57: 'se', 0x58: 'sw'}
LEDGE = {0x72: (1, 0), 0x73: (-1, 0), 0x74: (0, -1), 0x75: (0, 1)}
DIRS = {(1, 0): 'e', (-1, 0): 'w', (0, -1): 'n', (0, 1): 's'}
OPP = {'e': 'w', 'w': 'e', 'n': 's', 's': 'n'}
NOLAND = 0x4000
GRASS = {0x04, 0x05, 0x06, 0x07}    # (tall grass classes; only used to prefer paths)


def gf_container(d):
    magic = d[:2]; n = struct.unpack_from('<H', d, 2)[0]
    offs = struct.unpack_from('<%dI' % (n + 1), d, 4)
    return magic, [d[offs[i]:offs[i + 1]] for i in range(n)]


class Grid:
    """Collision of one matrix: rec(x, z) -> list of (a, b, class, flags) layer records (empty outside)."""
    def __init__(self, rom, matrix):
        d = rom.matrices[matrix]
        fmt, _, w, h = struct.unpack_from('<HHHH', d, 0)
        self.w, self.h = w, h
        self.chunk = struct.unpack_from('<%dI' % (w * h), d, 8)
        self.zones = struct.unpack_from('<%dI' % (w * h), d, 8 + 4 * w * h) if fmt == 1 else None
        self.rom = rom
        self._layers = {}

    def layers(self, cx, cz):
        key = (cx, cz)
        if key not in self._layers:
            out = []
            if 0 <= cx < self.w and 0 <= cz < self.h:
                c = self.chunk[cz * self.w + cx]
                if c != 0xFFFFFFFF:
                    magic, secs = gf_container(self.rom.chunks[c])
                    if magic == b'WB': out = [secs[1]]
                    elif magic == b'GC': out = [secs[1], secs[2]]
            self._layers[key] = out
        return self._layers[key]

    def rec(self, x, z):
        if x < 0 or z < 0: return []
        out = []
        for L in self.layers(x // 32, z // 32):
            r = struct.unpack_from('<HHI', L, 4 + 8 * ((z % 32) * 32 + x % 32))
            out.append((r[0], r[1], r[2] & 0xFFFF, r[2] >> 16))
        return out

    def zone_at(self, x, z):
        if not self.zones or x < 0 or z < 0: return None
        cx, cz = x // 32, z // 32
        if not (0 <= cx < self.w and 0 <= cz < self.h): return None
        v = self.zones[cz * self.w + cx]
        return None if v == 0xFFFFFFFF else v

    @staticmethod
    def y(r, x, z):
        a, i = r[0], r[1]
        if a & 3: return None
        nx, ny, nz = H.NORMALS[a >> 2]
        lx, lz = x % 32, z % 32
        return -(nx * (lx * 16 - 248) - nz * (lz * 16 - 248) + H.OFFS[i]) / ny


def land(r): return not (r[3] & 1) and r[2] not in SURF
def surf(r): return r[2] == 0x40 or (not (r[3] & 1) and r[2] in SURF)


class Rom:
    def __init__(self, path):
        f = NC.Files(path)
        self.f = f
        self.hdr = zoneheaders.parse(f.narc(12)[0])
        self.matrices = f.narc(9)
        self.chunks = f.narc(8)
        self.ents = f.narc(126)
        self.moves_raw = f.narc(21)
        self.personal = f.narc(16)
        self._grids = {}
        self._ent = {}

    def entities(self, zone):
        e = self.hdr[zone]['entities']
        if e not in self._ent: self._ent[e] = parse_entities(self.ents[e])[0]
        return self._ent[e]

    def grid(self, zone):
        m = self.hdr[zone]['matrix']
        if m not in self._grids: self._grids[m] = Grid(self, m)
        return self._grids[m]

    @functools.lru_cache(maxsize=None)
    def move(self, mid):
        """(type, category, power, accuracy, pp, priority) of a move (a/0/2/1)."""
        d = self.moves_raw[mid]
        return dict(type=d[0], cat=d[2], power=d[3], acc=d[4], pp=d[5], prio=struct.unpack('b', d[6:7])[0],
                    hits=(d[7] & 0xF, d[7] >> 4), effect=struct.unpack_from('<H', d, 0x0C)[0] if len(d) > 0x0D else 0)

    @functools.lru_cache(maxsize=None)
    def types(self, species):
        d = self.personal[species]
        return d[6], d[7]


# Gen 5 type chart: EFF[attacker][defender] (0 Normal 1 Fighting 2 Flying 3 Poison 4 Ground 5 Rock 6 Bug 7 Ghost
# 8 Steel 9 Fire 10 Water 11 Grass 12 Electric 13 Psychic 14 Ice 15 Dragon 16 Dark)
_T = ['Normal', 'Fighting', 'Flying', 'Poison', 'Ground', 'Rock', 'Bug', 'Ghost', 'Steel', 'Fire', 'Water', 'Grass',
      'Electric', 'Psychic', 'Ice', 'Dragon', 'Dark']
_SE = {'Fighting': 'Normal Rock Steel Ice Dark', 'Flying': 'Fighting Bug Grass', 'Poison': 'Grass',
       'Ground': 'Poison Rock Steel Fire Electric', 'Rock': 'Flying Bug Fire Ice', 'Bug': 'Grass Psychic Dark',
       'Ghost': 'Ghost Psychic', 'Steel': 'Rock Ice', 'Fire': 'Bug Steel Grass Ice', 'Water': 'Ground Rock Fire',
       'Grass': 'Ground Rock Water', 'Electric': 'Flying Water', 'Psychic': 'Fighting Poison', 'Ice': 'Flying Ground Grass Dragon',
       'Dragon': 'Dragon', 'Dark': 'Ghost Psychic'}
_NVE = {'Normal': 'Rock Steel', 'Fighting': 'Flying Poison Bug Psychic', 'Flying': 'Rock Steel Electric',
        'Poison': 'Poison Ground Rock Ghost', 'Ground': 'Bug Grass', 'Rock': 'Fighting Ground Steel',
        'Bug': 'Fighting Flying Poison Ghost Steel Fire', 'Ghost': 'Steel Dark', 'Steel': 'Steel Fire Water Electric',
        'Fire': 'Rock Fire Water Dragon', 'Water': 'Water Grass Dragon', 'Grass': 'Flying Poison Bug Steel Fire Grass Dragon',
        'Electric': 'Grass Electric Dragon', 'Psychic': 'Steel Psychic', 'Ice': 'Steel Fire Water Ice',
        'Dragon': 'Steel', 'Dark': 'Fighting Steel Dark'}
_NO = {'Normal': 'Ghost', 'Fighting': 'Ghost', 'Poison': 'Steel', 'Ground': 'Flying', 'Ghost': 'Normal',
       'Electric': 'Ground', 'Psychic': 'Dark', 'Dragon': ''}
EFF = [[1.0] * 17 for _ in range(17)]
for a, ds in _SE.items():
    for d in ds.split(): EFF[_T.index(a)][_T.index(d)] = 2.0
for a, ds in _NVE.items():
    for d in ds.split(): EFF[_T.index(a)][_T.index(d)] = 0.5
for a, ds in _NO.items():
    for d in ds.split(): EFF[_T.index(a)][_T.index(d)] = 0.0
TYPE_NAMES = _T

def effectiveness(atk, t1, t2):
    e = EFF[atk][t1] if atk < 17 and t1 < 17 else 1.0
    if t2 != t1 and atk < 17 and t2 < 17: e *= EFF[atk][t2]
    return e
