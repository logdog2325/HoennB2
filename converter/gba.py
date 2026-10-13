"""Read pokeruby map/tileset data and render GBA metatiles."""
import json, struct, os, re
import numpy as np
from PIL import Image

# Maps of other pret decomps read as if they were pokeruby's (data/hoenn_event_maps.json: Emerald's event islands,
# events agent 2026-10-07). Repo(pokeruby).map_json(name) falls back to the decomp listed for `name`; that map's layout
# is registered in repo.layouts under its own id (paths absolute), its tilesets are namespaced '<tag>:gTileset_X'
# ('emerald:gTileset_General': Emerald's General differs from Ruby's at some metatiles). Everything else is unchanged.
_EVENT_JSON = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'hoenn_event_maps.json')
_EVENT = {}
def event_maps():
    """{map folder: decomp folder} of data/hoenn_event_maps.json ({} without it)."""
    if 'maps' not in _EVENT:
        d = json.load(open(_EVENT_JSON)) if os.path.exists(_EVENT_JSON) else {}
        _EVENT['maps'], _EVENT['tags'] = d.get('maps', {}), d.get('decomps', {})
    return _EVENT['maps']

def event_tag(decomp):
    event_maps(); return _EVENT['tags'].get(decomp, decomp)

def decomp_root(root, name):
    """Root of the decomp that holds map `name`: `root` itself, or the event map's decomp next to it."""
    if os.path.isdir(os.path.join(root, 'data', 'maps', name)) or name not in event_maps(): return root
    return os.path.join(os.path.dirname(os.path.abspath(root)), event_maps()[name])

def map_json_path(root, name):
    return os.path.join(decomp_root(root, name), 'data', 'maps', name, 'map.json')

# Additions to pokeruby's own maps (data/hoenn_map_additions.json, postgame_maps agent 2026-10-07): "layouts" = other
# layouts of a map made from one of its layouts plus metatile edits (Emerald's setmetatile changes: the Altering Cave
# mouth on Route 103), registered in every Repo's layouts; "events" = event lists appended to a pokeruby map's own
# (Route 103's warp to Emerald's Altering Cave). Every reader through Repo (plan_map.py, world.py, the terrain modules,
# outdoor_check.py) sees them; nothing else changes.
_ADD_JSON = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'hoenn_map_additions.json')
_ADD = {}
def map_additions():
    """data/hoenn_map_additions.json ({'layouts': {}, 'events': {}} without it)."""
    if 'd' not in _ADD:
        d = json.load(open(_ADD_JSON)) if os.path.exists(_ADD_JSON) else {}
        _ADD['d'] = dict(layouts={k: v for k, v in d.get('layouts', {}).items() if not k.startswith('_')},
                         events={k: v for k, v in d.get('events', {}).items() if not k.startswith('_')})
    return _ADD['d']

def map_folders(root):
    """{MAP_ id: folder} of every map of `root` plus the event maps (+ in an Emerald world run, world_map_folders)."""
    out = {}
    base = os.path.join(root, 'data', 'maps')
    for d in os.listdir(base):
        p = os.path.join(base, d, 'map.json')
        if os.path.exists(p): out[json.load(open(p))['id']] = d
    for name in event_maps():
        p = map_json_path(root, name)
        if os.path.exists(p): out.setdefault(json.load(open(p))['id'], name)
    return out

# ---- Emerald's world (emerald_world 2026-10-12, notes/EMERALD.md "Emerald's world") ---------------------------------
# HOENN_VERSION=emerald: the world builders (converter/plan_map.py, b2tools/world.py, the terrain modules, outdoor_check,
# walk_diff) read their maps through world_repo(), which is Repo(pokeruby) for Sapphire and Ruby and, for Emerald, the
# Emerald view of it (Repo(root, emerald=True)). HoennB2 keeps Sapphire's map names: the view reads name as pokeemerald's
# map folder version.decomp_map(name) (data/versions.json "maps" -> "emerald": Emerald's renames), an Emerald-only map
# whose folder is another Sapphire map's name as '<folder>_Emerald' ("name_clash": SafariZone_Northeast_Emerald), and
# gives every MAP_ id in a map.json (its id, warps, connections) as HoennB2 knows it: Sapphire's id for a map Sapphire has
# (MAP_BATTLE_FRONTIER_BATTLE_TOWER_LOBBY -> MAP_BATTLE_TOWER_LOBBY), MAP_<FOLDER>_EMERALD for a name clash, else Emerald's.
# Its layouts and tilesets are pokeemerald's under their own (plain) names, with data/emerald/hoenn_map_additions.json in
# place of data/hoenn_map_additions.json ("layouts", "events" as there; "crop": {layout: [w, h]} reads only the first
# h rows and w columns: Route 103's 2 extra south rows, the seam) and "warps": {map: {index: {key: value}}} (a warp's
# destination replaced). The event maps (data/hoenn_event_maps.json) stay as in Sapphire's world (namespaced tilesets).
# Nothing here runs for Sapphire or Ruby: Repo(root) is unchanged.
_ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

def _version():
    """b2tools/version.py, the only reader of HOENN_VERSION."""
    import sys
    p = os.path.join(_ROOT, 'b2tools')
    if not any(os.path.abspath(q) == p for q in sys.path): sys.path.append(p)     # (appended: shadows nothing)
    import version
    return version

def world_repo(root=None):
    """The Repo the world builders read: Repo(root or external/pokeruby); with HOENN_VERSION=emerald (and root pokeruby's)
    the Emerald view of it."""
    root = root or os.path.join(_ROOT, 'external', 'pokeruby')
    if _version().is_emerald() and os.path.basename(os.path.normpath(root)) == 'pokeruby':
        return Repo(root, emerald=True)
    return Repo(root)

_EADD = {}
def emerald_additions():
    """data/emerald/hoenn_map_additions.json (empty without it): Emerald's own additions, in place of Sapphire's."""
    if 'd' not in _EADD:
        p = os.path.join(_ROOT, 'data', 'emerald', 'hoenn_map_additions.json')
        d = json.load(open(p)) if os.path.exists(p) else {}
        _EADD['d'] = {k: {n: v for n, v in d.get(k, {}).items() if not n.startswith('_')}
                      for k in ('layouts', 'events', 'crop', 'warps')}
    return _EADD['d']

def emerald_names():
    """(HoennB2 name -> Emerald folder, Emerald folder -> HoennB2 name, Sapphire maps Emerald dropped)."""
    if 'names' not in _EADD:
        m = _version().versions_json().get('maps', {}).get('emerald', {})
        fwd = dict(m.get('alias', {}))
        for n in m.get('name_clash', []): fwd[n + '_Emerald'] = n
        _EADD['names'] = (fwd, {v: k for k, v in fwd.items()}, set(m.get('gone', [])))
    return _EADD['names']

def world_map_folders():
    """{MAP_ id: HoennB2 map name} of the version's world maps: map_folders(pokeruby) (Sapphire, Ruby), plus every
    pokeemerald map by the id the Emerald view gives it (Emerald)."""
    R = os.path.join(_ROOT, 'external', 'pokeruby')
    out = map_folders(R)
    if _version().is_emerald():
        v = Repo(R, emerald=True)
        for eid, folder in map_folders(v.root).items(): out.setdefault(v.hoenn_id(eid), v.hoenn_name(folder))
    return out

class Repo:
    def __init__(self, root, emerald=False):
        self.root = root
        self.emerald = emerald
        if emerald: self._emerald_init(root); return
        self.layouts = {l['id']: l for l in json.load(open(f'{root}/data/layouts/layouts.json'))['layouts'] if 'id' in l}
        for lid, a in map_additions()['layouts'].items():     # (data/hoenn_map_additions.json: a layout + edits)
            if a['base'] in self.layouts: self.layouts[lid] = dict(self.layouts[a['base']], id=lid, _edits=a['edits'])
        self._ts = {}
        self._event_lay = {}          # event map -> (decomp root, tag, layout id in self.layouts)

    def _emerald_init(self, root):
        """The Emerald view (world_repo): pokeemerald's layouts (paths absolute) + Emerald's own additions."""
        self.sapphire_root = root
        self.root = _version().decomp('emerald')
        self.layouts = {}
        for l in json.load(open(os.path.join(self.root, 'data', 'layouts', 'layouts.json')))['layouts']:
            if 'id' not in l: continue
            l = dict(l)
            for k in ('blockdata_filepath', 'border_filepath'): l[k] = os.path.join(self.root, l[k])
            self.layouts[l['id']] = l
        add = emerald_additions()
        for lid, (w, h) in add['crop'].items():          # (before the additions: an alt layout of it is cropped too)
            l = self.layouts[lid]
            assert w <= l['width'] and h <= l['height'], (lid, w, h)
            l['_full'] = (l['width'], l['height']); l['width'], l['height'] = w, h
        for lid, a in add['layouts'].items():
            if a['base'] in self.layouts: self.layouts[lid] = dict(self.layouts[a['base']], id=lid, _edits=a['edits'])
        self._ts = {}
        self._event_lay = {}
        self._fwd, self._back, self._gone = emerald_names()
        self._ids = None

    def emerald_folder(self, name):
        """pokeemerald's folder of HoennB2 map `name` (None for a map Emerald dropped)."""
        if name in self._gone: return None
        return self._fwd.get(name, name)

    def hoenn_name(self, folder):
        """HoennB2's name of pokeemerald map folder `folder`."""
        return self._back.get(folder, folder)

    def hoenn_id(self, eid):
        """HoennB2's MAP_ id of pokeemerald's MAP_ id `eid` (see world_repo); other values (MAP_NONE, B2_ZONE_n) as given."""
        if self._ids is None:
            self._ids = {}
            sap = {v: k for k, v in map_folders(self.sapphire_root).items()}       # Sapphire name -> Sapphire id
            clash = set(_version().versions_json().get('maps', {}).get('emerald', {}).get('name_clash', []))
            for e_id, folder in map_folders(self.root).items():
                name = self.hoenn_name(folder)
                self._ids[e_id] = sap.get(name) or (e_id + '_EMERALD' if folder in clash else e_id)
        return self._ids.get(eid, eid)

    def _event(self, name):
        """(decomp root, tag, layout id) of an event map this root lacks, registering its layout; else None."""
        if name in self._event_lay: return self._event_lay[name]
        base = getattr(self, 'sapphire_root', self.root)     # (the Emerald view: event maps as in Sapphire's world)
        if self.emerald and name not in event_maps(): return None
        r = decomp_root(base, name)
        if r == base: return None
        tag = event_tag(os.path.basename(r))
        lid = json.load(open(os.path.join(r, 'data', 'maps', name, 'map.json')))['layout']
        if lid not in self.layouts or self.layouts[lid].get('_decomp') != tag:
            lays = {l['id']: l for l in json.load(open(os.path.join(r, 'data', 'layouts', 'layouts.json')))['layouts'] if 'id' in l}
            l = dict(lays[lid], _decomp=tag)
            for k in ('blockdata_filepath', 'border_filepath'): l[k] = os.path.join(r, l[k])
            for k in ('primary_tileset', 'secondary_tileset'): l[k] = f'{tag}:{l[k]}'
            if lid in self.layouts: lid = f'{tag}:{lid}'
            self.layouts[lid] = l
        self._event_lay[name] = (r, tag, lid)
        return self._event_lay[name]

    def tileset_dir(self, sym):
        # gTileset_General -> primary/general ; gTileset_Petalburg -> secondary/petalburg
        root = self.root
        if ':' in sym:                # an event map's tileset ('emerald:gTileset_General'): that decomp's
            tag, sym = sym.split(':', 1)
            event_maps()
            dec = next((d for d, t in _EVENT['tags'].items() if t == tag), tag)
            root = os.path.join(os.path.dirname(os.path.abspath(self.root)), dec)
        name = re.sub(r'(?<!^)(?=[A-Z])', '_', sym.replace('gTileset_', '')).lower()
        for kind in ('primary', 'secondary'):
            p = f'{root}/data/tilesets/{kind}/{name}'
            if os.path.isdir(p):
                return p
        raise FileNotFoundError(sym)

    def load_tileset(self, sym):
        if sym in self._ts:
            return self._ts[sym]
        d = self.tileset_dir(sym)
        img = Image.open(f'{d}/tiles.png')
        idx = np.array(img)  # palette indices
        if idx.max() > 15:
            idx = idx & 15
        tiles = []
        h, w = idx.shape
        for ty in range(h // 8):
            for tx in range(w // 8):
                tiles.append(idx[ty*8:ty*8+8, tx*8:tx*8+8])
        pals = []
        for i in range(16):
            lines = open(f'{d}/palettes/{i:02d}.pal').read().split('\n')[3:19]
            pals.append(np.array([[int(v) for v in l.split()] for l in lines if l.strip()], dtype=np.uint8))
        mt = np.frombuffer(open(f'{d}/metatiles.bin', 'rb').read(), dtype='<u2').reshape(-1, 8)
        attr = np.frombuffer(open(f'{d}/metatile_attributes.bin', 'rb').read(), dtype='<u2')
        ts = dict(tiles=tiles, pals=pals, mt=mt, attr=attr)
        self._ts[sym] = ts
        return ts

    def map_json(self, name):
        if self.emerald: return self._emerald_map_json(name)
        ev = self._event(name) if not os.path.exists(f'{self.root}/data/maps/{name}/map.json') else None
        if ev:                        # an event map of another decomp: its layout as registered by _event
            return dict(json.load(open(os.path.join(ev[0], 'data', 'maps', name, 'map.json'))), layout=ev[2], _decomp=ev[1])
        mj = json.load(open(f'{self.root}/data/maps/{name}/map.json'))
        for k, extra in map_additions()['events'].get(name, {}).items():   # (data/hoenn_map_additions.json)
            if k.endswith('_events'): mj[k] = list(mj.get(k) or []) + [dict(e) for e in extra]
        return mj

    def _emerald_map_json(self, name):
        """The Emerald view's map.json of HoennB2 map `name` (see world_repo)."""
        ev = self._event(name)
        if ev:
            return dict(json.load(open(os.path.join(ev[0], 'data', 'maps', name, 'map.json'))), layout=ev[2], _decomp=ev[1])
        folder = self.emerald_folder(name)
        p = os.path.join(self.root, 'data', 'maps', folder or name, 'map.json')
        if folder is None or not os.path.exists(p): raise FileNotFoundError(f'{name}: no map in pokeemerald ({folder})')
        mj = json.load(open(p))
        mj['id'] = self.hoenn_id(mj['id'])
        mj['_emerald'] = folder
        if mj.get('warp_events'): mj['warp_events'] = [dict(w, dest_map=self.hoenn_id(w['dest_map'])) for w in mj['warp_events']]
        if mj.get('connections'): mj['connections'] = [dict(c, map=self.hoenn_id(c['map'])) for c in mj['connections']]
        add = emerald_additions()
        for i, over in add['warps'].get(name, {}).items():                # (a warp's destination replaced)
            mj['warp_events'][int(i)] = dict(mj['warp_events'][int(i)], **{k: v for k, v in over.items() if not k.startswith('_')})
        for k, extra in add['events'].get(name, {}).items():
            if k.endswith('_events'): mj[k] = list(mj.get(k) or []) + [dict(e) for e in extra]
        return mj

    def layout_grid(self, layout_id):
        l = self.layouts[layout_id]
        raw = np.frombuffer(open(os.path.join(self.root, l['blockdata_filepath']), 'rb').read(), dtype='<u2')
        # pokeruby's UnknownMap_082FF894 (Ruby's Cave of Origin B4F) has one extra trailing block; the game reads
        # width * height blocks from the start (mapLayout->map), so the rest is ignored
        if '_full' in l:              # (the Emerald view's "crop": the first rows and columns of the full layout)
            fw, fh = l['_full']
            g = raw[:fh * fw].reshape(fh, fw)[:l['height'], :l['width']]
        else:
            g = raw[:l['height'] * l['width']].reshape(l['height'], l['width'])
        if l.get('_edits'):           # a layout of data/hoenn_map_additions.json: the base's blocks + setmetatile edits
            g = g.copy()              # (metatile id, collision bits 10-11, elevation bits 12-15; unnamed ones kept)
            for e in l['_edits']:
                x, y = e['at']; v = int(g[y, x])
                g[y, x] = (int(str(e['metatile']), 0) & 0x3FF) | (e.get('collision', (v >> 10) & 3) << 10) \
                    | (e.get('elevation', v >> 12) << 12)
        return g, l

class MetatileRenderer:
    def __init__(self, repo, prim, sec):
        self.p = repo.load_tileset(prim)
        self.s = repo.load_tileset(sec)
        self.pals = self.p['pals'][:6] + self.s['pals'][6:13] + self.p['pals'][13:]
        self.cache = {}

    def behavior(self, m):
        a = self.p['attr'] if m < 512 else self.s['attr']
        i = m if m < 512 else m - 512
        return int(a[i] & 0xFF) if i < len(a) else 0

    def tile(self, t):
        return self.p['tiles'][t] if t < 512 else self.s['tiles'][t - 512] if t - 512 < len(self.s['tiles']) else np.zeros((8, 8), np.uint8)

    def render(self, m):
        """Return (16,16,4) RGBA for metatile m (bottom+top layer)."""
        if m in self.cache:
            return self.cache[m]
        src = self.p['mt'] if m < 512 else self.s['mt']
        i = m if m < 512 else m - 512
        out = np.zeros((16, 16, 4), np.uint8)
        if i < len(src):
            for layer in range(2):
                for q in range(4):
                    e = int(src[i][layer*4+q])
                    t, hf, vf, pal = e & 0x3FF, (e >> 10) & 1, (e >> 11) & 1, (e >> 12) & 0xF
                    px = self.tile(t)
                    if hf: px = px[:, ::-1]
                    if vf: px = px[::-1, :]
                    rgb = self.pals[pal][px]
                    mask = px != 0
                    if layer == 0:
                        mask = np.ones_like(mask)
                    oy, ox = (q // 2) * 8, (q % 2) * 8
                    reg = out[oy:oy+8, ox:ox+8]
                    reg[mask, :3] = rgb[mask]
                    reg[mask, 3] = 255
        self.cache[m] = out
        return out
