"""Terrain feature modules for b2tools/world.py (notes/OVERWORLD_PLAN.md, stage O2).

Each module in this folder handles some plan classes (converter/plan_map.py tile classes, notes/LABELS.md) and
defines:

    CLASSES = {'water', 'deep_water'}            # tile classes it draws and/or gives collision to
    TEXTURES = {'sea_mizu': 14}                   # textures it uses: name -> Black 2 map texture set (a/0/1/4 id) to
                                                  # copy it from (merged losslessly into Hoenn's set, patches/hoenn_textures.py)
    PALETTES = {'sea_mizu': 'sea_mizu_pl'}        # optional: palette name when it isn't <texture>_pl
    WRAP = {'sea_mizu': ('WRAP', 'CLAMP')}        # optional: texture wrap modes for the DAE

    def draw(m, cell):                            # add geometry for this cell's tiles of CLASSES to dae.Model m
        ...
    def collision(cls, tile, cell):               # -> (record, map_char) for a tile of CLASSES, or None (default)
        ...

`cell` (world.py Cell): .cx, .cz, .get(tx, tz) -> (map, class, walkable) or None for cell-local tile coords (may
be outside 0..31: neighbours), .X/.Z global tile origin, .bc (build_chunk helpers: ux/uz, ground, flat_decal ...),
.world (global dict). Geometry is in chunk model units: tile t spans t*16-256 .. t*16-240 (bc.ux/bc.uz).
Collision records are 4 u16 (see build_chunk.py WALK/SOLID/... and notes/GEN5_TERRAIN.md).
Recipes must copy how Black 2's own chunks build the same thing, with evidence in notes/GEN5_TERRAIN.md.
"""
import importlib, os, pkgutil

def enabled():
    """Module names in use: HOENN_TERRAIN (comma list; an agent testing its own module) or
    data/terrain_modules.json (normal builds; a module is listed there once reviewed)."""
    import json
    env = os.environ.get('HOENN_TERRAIN')
    if env is not None: return [m for m in env.split(',') if m]
    path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'terrain_modules.json')
    return json.load(open(path))['modules']

def modules():
    return [importlib.import_module(f'terrain.{name}') for name in enabled()]
