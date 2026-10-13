"""People-sprite budget of every Hoenn zone in a built ROM (notes/NPC_LIMIT.md). Read-only.

    python3 npc_check.py ROM.nds|FILES_DIR [--all-zones] [--zone N ...] [--verbose] [--strict]

What limits the people Black 2 can draw at once on one field (all from code, measured in DeSmuME, NPC_LIMIT.md):
- **32 billboard materials** (ov036 Field_InitActorSystem: FldActSys_InitBlAct(…, 0x20) -> FldBlAct_InitMatCache):
  one entry per distinct sprite code (a/0/4/7 object code) on the field: the zone's preloaded list (zone header
  npc_cache < 24: a/0/5/7, kept for the whole field), the player's walking sprite, the player's current other form
  (bike, surf, fishing ...) and every code an NPC on the field uses. A code that finds the cache full is uploaded but
  never registered (FldBlAct_RegistCachedMat finds no free entry): that person stays invisible, yet solid and
  talkable. Codes are claimed in the zone's NPC order (SpawnAllZoneNPCs), so the last ones lose.
- **Texture VRAM, 3 x 128 KB** (FIELDMAP_VRAM_CONFIG: banks A-C): the area's map + building textures, then one whole
  sheet per material (BlActSys_LoadSingleUseTexMaterial). A failed upload leaves the person invisible too.
- **64 actors** (FldActSys_Create(…, 0x40)), the player included.
NPCs are counted when present: spawn flag 0 = always; a flag hides its NPC while set. The worst case (every flag
clear) is checked first; zones over a limit there are checked for every combination of their flags ("story states").
Sprite codes 162-177 read their real code from works 0x4020-0x402F (the rival: Brendan/May sheets, 12,320 B).
With --strict the exit status is 1 when a zone is over a limit (for build scripts).
"""
import os, sys, re, json, mmap, struct, itertools, collections

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..')

MAT_CACHE = 32                 # ov036 Field_InitActorSystem: FldActSys_InitBlAct(actorSystem, actorBlAct, 0x20)
PLAYER_ENTRIES = 2             # the player's walking sheet (FldActSys_LoadStaticBlact) + its current other form
ACTORS = 64                    # main FldActSys_Create(heap, 0x40, save): actor capacity, the player included
TEX_VRAM = 3 * 128 * 1024      # FIELDMAP_VRAM_CONFIG texture banks A+B+C (GFL_G3DSysCreate linked-list manager)
PLAYER_WALK = 12320            # sheets 231/240 (24 frames 32x32 4bpp + palette), loaded for the whole field
PLAYER_FORM = 24608            # the largest other form: fishing 239/248 (12 frames 64x64)
EFFECTS = 32768                # field effects, shadows etc.: 24.4 KB measured in Slateport (NPC_LIMIT.md) + margin
DYNAMIC = range(162, 178)      # codes read from works 0x4020-0x402F (GetWKOBJCODENPCOBJCODE)
DYNAMIC_SHEET = 12320          # the rival (162 -> Brendan 1 / May 4: player-sized sheets)

# ---------------------------------------------------------------------------------------------------- ROM access

class Files:
    """NitroFS files by path, from a built .nds (mmap) or a files/ directory."""
    def __init__(self, path):
        self.dir = path if os.path.isdir(path) else None
        if not self.dir:
            f = open(path, 'rb'); self.d = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
            self.fnt, = struct.unpack_from('<I', self.d, 0x40); self.fat, = struct.unpack_from('<I', self.d, 0x48)
    def _dir(self, did):
        d = self.d; off, first, _ = struct.unpack_from('<IHH', d, self.fnt + 8 * (did & 0xFFF))
        p = self.fnt + off; fid = first; out = {}
        while True:
            n = d[p]; p += 1
            if n == 0: return out
            name = bytes(d[p:p + (n & 0x7F)]).decode('latin1'); p += n & 0x7F
            if n & 0x80: out[name] = ('d', struct.unpack_from('<H', d, p)[0]); p += 2
            else: out[name] = ('f', fid); fid += 1
    def read(self, path):
        if self.dir: return open(os.path.join(self.dir, path), 'rb').read()
        did = 0xF000
        for part in path.split('/'):
            kind, v = self._dir(did)[part]
            if kind == 'd': did = v
            else:
                s, e = struct.unpack_from('<II', self.d, self.fat + 8 * v); return bytes(self.d[s:e])
    def arc(self, n): return f'a/{n // 100}/{n // 10 % 10}/{n % 10}'
    def narc(self, n):
        d = self.read(self.arc(n)); assert d[:4] == b'NARC'
        off = struct.unpack_from('<H', d, 0xC)[0]
        size, count = struct.unpack_from('<IH', d, off + 4)
        spans = [struct.unpack_from('<II', d, off + 12 + 8 * i) for i in range(count)]
        off += size; off += struct.unpack_from('<I', d, off + 4)[0]; base = off + 8
        return [d[base + s:base + e] for s, e in spans]

def tex_bytes(btx):
    """VRAM bytes of a BTX0/BMD0's TEX0: texture data + 4x4-compressed data and its index + palettes."""
    if btx[:4] not in (b'BTX0', b'BMD0'): return 0
    nb = struct.unpack_from('<H', btx, 0xE)[0]
    for k in range(nb):
        o = struct.unpack_from('<I', btx, 0x10 + 4 * k)[0]
        if btx[o:o + 4] == b'TEX0':
            t = btx[o:]
            tex, c4 = struct.unpack_from('<H', t, 0xC)[0] << 3, struct.unpack_from('<H', t, 0x1C)[0] << 3
            return tex + c4 + c4 // 2 + (struct.unpack_from('<H', t, 0x30)[0] << 3)
    return 0

HDR = struct.Struct('<BBHHHHH4HHHHHHHHH3I')
NPC = struct.Struct('<HHHHHHHHHHHHIHHi')

def npcs_of(entry):
    n_sign, n_npc = entry[4], entry[5]
    off = 8 + 0x14 * n_sign
    return [dict(zip(('uid', 'model', 'move', 'evtype', 'flag', 'script'), NPC.unpack_from(entry, off + 0x24 * i)[:6]))
            for i in range(n_npc)]

def obj_record(code):           # GetIndexOfObjID (arm9 0x0200fe34)
    if code <= 376: return code
    if 0x1000 <= code <= 0x126B: return code - 0xE87
    if 0x2000 <= code <= 0x200A: return code - 0x1C1B
    return 10

class Rom:
    def __init__(self, path):
        f = Files(path)
        hd = f.narc(12)[0]
        self.headers = [HDR.unpack_from(hd, 0x30 * i) for i in range(len(hd) // 0x30)]
        self.ents = f.narc(126)
        self.areas = f.read(f.arc(13))
        self.maptex, self.ext, self.int = f.narc(14), f.narc(174), f.narc(175)
        t = f.narc(47)[0]
        self.table = [struct.unpack_from('<HBBBBBBBBBBBbbbHH', t, 4 + 28 * i) for i in range(struct.unpack_from('<I', t, 0)[0])]
        self.sheets = f.narc(48)
        self.cache = f.narc(57)
        self._sheet = {}
    def zone(self, z):
        h = self.headers[z]
        return dict(map_type=h[0], npc_cache=h[1], area=h[2], scripts=h[4], entities=h[12])
    def area_tex(self, area):
        """Map + building texture bytes of an area (the largest season of a seasonal area 2..281)."""
        best = 0
        for a in ([area + s for s in range(4)] if 2 <= area < 0x11a else [area]):
            if a >= len(self.areas) // 10: a = 0          # AreaData_Create: id >= 0x199 -> area 0
            pack, texset, _, _, ext = struct.unpack_from('<HHBBB', self.areas, 10 * a)
            packs = self.ext if ext else self.int
            best = max(best, tex_bytes(self.maptex[texset]) + (tex_bytes(packs[pack]) if pack < len(packs) else 0))
        return best
    def sheet(self, code):
        """VRAM bytes of an object code's sheet (0 for 3D objects, which are not billboards)."""
        if code in DYNAMIC: return DYNAMIC_SHEET
        if code not in self._sheet:
            rec = self.table[obj_record(code)] if obj_record(code) < len(self.table) else None
            self._sheet[code] = tex_bytes(self.sheets[rec[15]]) if rec and rec[1] == 1 and rec[15] < len(self.sheets) else 0
        return self._sheet[code]
    def preloaded(self, idx):
        if idx >= 24 or idx >= len(self.cache): return []
        d = self.cache[idx]; n = struct.unpack_from('<H', d, 0)[0]
        return [struct.unpack_from('<H', d, 2 + 2 * k)[0] for k in range(n)]

# ---------------------------------------------------------------------------------------------------- names

def hoenn_zones():
    """{zone: name} of every Hoenn zone (outdoor maps, warp-only maps, rooms and caves)."""
    out = {}
    for name, m in json.load(open(os.path.join(ROOT, 'data', 'hoenn_zones.json')))['maps'].items(): out[m['zone']] = name
    for name, r in json.load(open(os.path.join(ROOT, 'data', 'hoenn_interiors.json')))['rooms'].items():
        if 'zone' in r: out.setdefault(r['zone'], name)
    return out

def flag_names():
    src = open(os.path.join(ROOT, 'src', 'include', 'hoenn.h')).read()
    out = {}
    for k, v in re.findall(r'#define\s+(FLAG_\w+)\s+(0x[0-9a-fA-F]+|\d+)', src): out.setdefault(int(v, 0), k)
    return out

def new_game_flags(names):
    p = os.path.join(ROOT, 'src', 'field_scripts', 'scenes', 'new_game_flags.inc')
    if not os.path.exists(p): return set()
    inv = {v: k for k, v in names.items()}
    return {inv[f] for f in re.findall(r'FlagSet\s+(FLAG_\w+)', open(p).read()) if f in inv}

def scripted_codes(scripts_id):
    """Literal sprite codes of ActorNew in the zone's script source (temporary actors of scenes)."""
    out = set()
    for p in __import__('glob').glob(os.path.join(ROOT, 'src', 'field_scripts', f'{scripts_id:04d}_*.s')):
        for m in re.finditer(r'^\s*ActorNew\s+[^,]+,[^,]+,[^,]+,[^,]+,\s*(\d+)', open(p).read(), re.M):
            out.add(int(m.group(1)))
    return out

# ---------------------------------------------------------------------------------------------------- the check

def budget(rom, z, present, extra=()):
    """Use of the three limits by the NPCs `present` (+ `extra` codes) on zone z's field."""
    h = rom.zone(z)
    pre = set(rom.preloaded(h['npc_cache']))
    codes = set(n['model'] for n in present) | set(extra)
    entries = len(pre | codes) + PLAYER_ENTRIES
    sheets = sum(rom.sheet(c) for c in pre | codes)
    area = rom.area_tex(h['area'])
    vram = area + sheets + PLAYER_WALK + PLAYER_FORM + EFFECTS
    over = []
    if entries > MAT_CACHE: over.append(f'materials {entries}/{MAT_CACHE}')
    if vram > TEX_VRAM: over.append(f'VRAM {vram}/{TEX_VRAM}')
    if len(present) + 1 > ACTORS: over.append(f'actors {len(present) + 1}/{ACTORS}')
    return dict(codes=len(codes), pre=len(pre - codes), entries=entries, sheets=sheets, area=area, vram=vram,
                npcs=len(present), over=over)

def invisible(rom, z, present):
    """NPCs whose code finds the material cache full, in spawn order (the zone's NPC list order)."""
    h = rom.zone(z)
    have = set(rom.preloaded(h['npc_cache'])); free = MAT_CACHE - PLAYER_ENTRIES - len(have); out = []
    for i, n in present:
        if n['model'] in have: continue
        if free > 0: have.add(n['model']); free -= 1
        else: out.append((i, n))
    return out

def check(rom, zones, hidden=frozenset()):
    """Every zone's use of the limits with every NPC present but those whose spawn flag is in `hidden` (set)."""
    rows, bad = [], []
    for z, name in sorted(zones.items(), key=lambda kv: kv[1]):
        if z >= len(rom.headers): continue
        h = rom.zone(z)
        npcs = [(i, n) for i, n in enumerate(npcs_of(rom.ents[h['entities']])) if n['flag'] not in hidden]
        extra = scripted_codes(h['scripts'])
        worst = budget(rom, z, [n for _, n in npcs], extra)
        flags = sorted({n['flag'] for _, n in npcs if n['flag']})
        row = dict(zone=z, name=name, flags=len(flags), worst=worst, states_over=[])
        if worst['over']:
            # every combination of the zone's spawn flags (set = hidden): which story states break a limit
            for k in range(len(flags) + 1) if len(flags) <= 14 else [0]:
                for hidden in itertools.combinations(flags, k):
                    present = [n for _, n in npcs if n['flag'] not in hidden]
                    b = budget(rom, z, present, extra)
                    if b['over']: row['states_over'].append((hidden, b['over']))
            row['invisible'] = invisible(rom, z, npcs)
            bad.append(row)
        rows.append(row)
    return rows, bad

def report(rows, bad, fnames, verbose=False):
    lines = [f'{"zone":>4} {"name":34} {"NPCs":>4} {"codes":>5} {"mat":>6} {"sheets B":>8} {"area B":>7} {"VRAM B":>7}  status']
    for r in rows:
        w = r['worst']
        if not verbose and not w['over'] and w['codes'] == 0: continue
        status = 'OVER: ' + ', '.join(w['over']) if w['over'] else 'ok'
        lines.append(f"{r['zone']:4d} {r['name'][:34]:34} {w['npcs']:4d} {w['codes']:5d} {w['entries']:3d}/{MAT_CACHE} "
                     f"{w['sheets']:8d} {w['area']:7d} {w['vram']:7d}  {status}")
    for r in bad:
        lines.append(f"\n{r['name']} (zone {r['zone']}): {len(r['states_over'])} flag combinations over a limit "
                     f"({r['flags']} spawn flags); with every NPC present these load invisibly:")
        for i, n in r['invisible']:
            lines.append(f"   NPC {i} uid {n['uid']} sprite {n['model']} flag {fnames.get(n['flag'], n['flag'])} script {n['script']}")
        for hidden, over in r['states_over'][:8]:
            lines.append(f"   hidden {[fnames.get(f, f) for f in hidden] or 'none'}: {', '.join(over)}")
    lines.append(f'\n{len(rows)} zones checked, {len(bad)} over a limit (worst case: every spawn flag clear). Limits: '
                 f'{MAT_CACHE} materials ({PLAYER_ENTRIES} for the player), {TEX_VRAM} B texture VRAM '
                 f'(area + sheets + player {PLAYER_WALK} + {PLAYER_FORM} + effects {EFFECTS}), {ACTORS} actors.')
    return '\n'.join(lines)

def sapphire_projection(rom, zones):
    """Every Hoenn map with all of Sapphire's objects present (its object_events; graphics -> Black 2 code by
    data/sprite_map.json, VAR graphics = the rival, 162): what the zones need once every chapter is ported."""
    sm = json.load(open(os.path.join(ROOT, 'data', 'sprite_map.json')))
    rows = []
    for z, name in sorted(zones.items(), key=lambda kv: kv[1]):
        p = os.path.join(ROOT, 'data', 'sapphire', f'{name}.json')
        if not os.path.exists(p) or z >= len(rom.headers): continue
        present, unmapped = [], 0
        for n in json.load(open(p))['npcs']:
            code = (sm.get(n['gfx']) or {}).get('code')
            if code is None and 'VAR' in n['gfx']: code = 162
            if code is None: unmapped += 1; continue
            present.append(dict(uid=n['local_id'], model=code, flag=0, script=0))
        b = budget(rom, z, present)
        rows.append(dict(zone=z, name=name + (f' (+{unmapped} unmapped)' if unmapped else ''), flags=0, worst=b, states_over=[]))
    return rows

def main(argv):
    import argparse
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('rom', help='built .nds or its files/ directory')
    ap.add_argument('--zone', type=int, nargs='*', help='only these zones')
    ap.add_argument('--all-zones', action='store_true', help="every zone, Black 2's own too")
    ap.add_argument('--set', default='', help='a story state: FLAG_A,FLAG_B,... set (their NPCs hidden); "new-game" = '
                    'the flags the new game sets (scenes/new_game_flags.inc)')
    ap.add_argument('--sapphire', action='store_true', help="projection: every Sapphire object present")
    ap.add_argument('--verbose', action='store_true', help='also zones without people')
    ap.add_argument('--strict', action='store_true', help='exit status 1 when a zone is over a limit')
    a = ap.parse_args(argv)
    rom = Rom(a.rom)
    zones = hoenn_zones()
    if a.all_zones: zones = {z: zones.get(z, f'zone {z}') for z in range(len(rom.headers))}
    if a.zone: zones = {z: zones.get(z, f'zone {z}') for z in a.zone}
    fn = flag_names()
    if a.sapphire:
        rows = sapphire_projection(rom, zones); bad = [r for r in rows if r['worst']['over']]
        for r in bad: r['invisible'] = []
        print('Projection: every Sapphire object of each map present (data/sapphire + data/sprite_map.json)')
    else:
        hidden = set()
        if a.set == 'new-game': hidden = new_game_flags(fn)
        elif a.set:
            inv = {v: k for k, v in fn.items()}
            hidden = {inv[f] if f in inv else int(f, 0) for f in a.set.split(',')}
        rows, bad = check(rom, zones, hidden=hidden)
        if hidden: print(f'Story state: {len(hidden)} flags set (their NPCs hidden)')
    print(report(rows, bad, fn, verbose=a.verbose))
    return 1 if bad and a.strict else 0

def apply(files):
    """As a build step (b2tools/patches/npc_check.py, last in the patch list): report, change nothing."""
    rom = Rom(files)
    rows, bad = check(rom, hoenn_zones())
    top = sorted(rows, key=lambda r: -r['worst']['entries'])[:3]
    return (f"{len(rows)} zones, {len(bad)} over a limit" + (': ' + ', '.join(f"{r['name']} ({', '.join(r['worst']['over'])})" for r in bad) if bad else '')
            + '; fullest: ' + ', '.join(f"{r['name']} {r['worst']['entries']}/{MAT_CACHE} materials" for r in top))

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
