"""The Battle Pyramid floor's models (frontier_pyramid, 2026-10-12; notes/FRONTIER_PYRAMID.md): Emerald builds a
floor from 16 of its 8x8 "squares" picked at random (pokeemerald src/battle_pyramid.c); Black 2 draws maps from fixed
models, so the floor is drawn from props: one model per square layout (its walls), placed by the Pyramid's engine as the
floor's chunk loads (b2tools/patches/frontier_pyramid.c PY_RDHook), on a base model that is the whole 32x32 floor.

    python3 pyramid_models.py [OUT]     (default: $HOENN_INTERIORS_DIR or work/interiors, + /BattleFrontier_BattlePyramidFloor)

Writes base.nsbmd (the chunk model: 32x32 floor + a wall ring outside it), sq00..sq15.nsbmd (square layout k's walls,
centred on the square), stairs.nsbmd (the exit panel, centred on its tile), their DAE + textures, and models.json
(model -> textures and their map texture set). Converted with CTRMapV's writer (ToNsbmd --vcol: shading baked into
vertex colours, as Black 2's interiors). Black 2's own art only: Relic Castle's map textures (set 291, the Desert
Resort's buried castle): stone floor tiles for Emerald's grey floor, sandstone for its raised sand-coloured walls."""
import os, sys, json, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import b2files, nsbtx
from dae import Model

FILES = os.path.join(ROOT, 'external', 'pokebw2', 'build', 'b2_us', 'files')
DATA = os.path.join(ROOT, 'data', 'emerald', 'frontier_pyramid.json')
TEXSET = 291                         # Relic Castle (zones 160-182: area 291, interior pack 9)
FLOOR = 'in10_tile04'                # grey-beige stone tiles (32x32)
WALL_TOP = 'in10_tile05'             # sandstone slab top
WALL_SIDE = 'in10_kabe01'            # sandstone brick face with a band
PANEL = 'd0_miz'                     # the exit panel: Emerald's blue warp square
PANEL_SIDE = 'in10_tile07'
H = 24                               # wall height (units; a tile is 16)
SHADE = dict(top=(1.0, 1.0, 1.0), south=(0.78, 0.78, 0.78), side=(0.6, 0.6, 0.6), north=(0.5, 0.5, 0.5))

def box(m, x0, z0, x1, z1, y0, y1, top, side, faces=('top', 'south', 'west', 'east', 'north'), ts=32):
    """A box from (x0, z0) to (x1, z1) (model units, z south), y0..y1; the faces listed (seen from outside)."""
    if 'top' in faces:
        m.quad(top, [(x0, y1, z1, x0 / ts, -z1 / ts), (x1, y1, z1, x1 / ts, -z1 / ts), (x1, y1, z0, x1 / ts, -z0 / ts),
                     (x0, y1, z0, x0 / ts, -z0 / ts)], SHADE['top'])
    vy = lambda y: (y - y0) / 32
    if 'south' in faces:
        m.quad(side, [(x0, y0, z1, x0 / 32, vy(y0)), (x1, y0, z1, x1 / 32, vy(y0)), (x1, y1, z1, x1 / 32, vy(y1)),
                      (x0, y1, z1, x0 / 32, vy(y1))], SHADE['south'])
    if 'north' in faces:
        m.quad(side, [(x1, y0, z0, x1 / 32, vy(y0)), (x0, y0, z0, x0 / 32, vy(y0)), (x0, y1, z0, x0 / 32, vy(y1)),
                      (x1, y1, z0, x1 / 32, vy(y1))], SHADE['north'])
    if 'west' in faces:
        m.quad(side, [(x0, y0, z0, z0 / 32, vy(y0)), (x0, y0, z1, z1 / 32, vy(y0)), (x0, y1, z1, z1 / 32, vy(y1)),
                      (x0, y1, z0, z0 / 32, vy(y1))], SHADE['side'])
    if 'east' in faces:
        m.quad(side, [(x1, y0, z1, z1 / 32, vy(y0)), (x1, y0, z0, z0 / 32, vy(y0)), (x1, y1, z0, z0 / 32, vy(y1)),
                      (x1, y1, z1, z1 / 32, vy(y1))], SHADE['side'])

def square_model(k, walls):
    """Square layout k's walls: a box per wall tile, its faces toward floor tiles of the square (and the square's
    edges: the neighbour square may be floor there)."""
    m = Model(f'pyr_sq{k:02d}')
    wall = lambda x, y: 0 <= x < 8 and 0 <= y < 8 and walls[y][x] == '#'
    for y in range(8):
        for x in range(8):
            if not wall(x, y): continue
            x0, z0 = x * 16 - 64, y * 16 - 64
            faces = ['top'] + [f for f, (dx, dy) in (('south', (0, 1)), ('north', (0, -1)), ('west', (-1, 0)), ('east', (1, 0)))
                               if not wall(x + dx, y + dy)]
            box(m, x0, z0, x0 + 16, z0 + 16, 0, H, WALL_TOP, WALL_SIDE, faces)
    if not m.tris:                    # (every square has walls; a model needs at least one triangle)
        m.quad(FLOOR, [(-1, 0.1, 1, 0, 0), (1, 0.1, 1, 1, 0), (1, 0.1, -1, 1, 1), (-1, 0.1, -1, 0, 1)])
    return m

def base_model():
    """The floor's chunk: the 32x32 floor (y 0) and a ring of wall outside it (Emerald's border metatile is wall)."""
    m = Model('pyr_floor')
    for z in range(0, 32, 8):          # floor in 8x8 tile quads (uv repeats: 32 units a texture)
        for x in range(0, 32, 8):
            x0, z0, x1, z1 = x * 16 - 256, z * 16 - 256, (x + 8) * 16 - 256, (z + 8) * 16 - 256
            m.quad(FLOOR, [(x0, 0, z1, x0 / 32, -z1 / 32), (x1, 0, z1, x1 / 32, -z1 / 32), (x1, 0, z0, x1 / 32, -z0 / 32),
                           (x0, 0, z0, x0 / 32, -z0 / 32)], SHADE['top'])
    for i in range(-1, 33):            # the ring: one tile wide, faces toward the floor
        for (x, y) in ((i, -1), (i, 32), (-1, i), (32, i)):
            if (x, y) in ((-1, -1), (32, -1), (-1, 32), (32, 32)) and i not in (-1, 32): continue
            x0, z0 = x * 16 - 256, y * 16 - 256
            faces = ['top'] + (['south'] if y == -1 and 0 <= x < 32 else []) + (['north'] if y == 32 and 0 <= x < 32 else []) \
                + (['east'] if x == -1 and 0 <= y < 32 else []) + (['west'] if x == 32 and 0 <= y < 32 else [])
            box(m, x0, z0, x0 + 16, z0 + 16, 0, H, WALL_TOP, WALL_SIDE, faces)
    return m

def stairs_model():
    """Emerald's exit panel (METATILE_BattlePyramid_Exit, a blue square): a low blue slab on its tile."""
    m = Model('pyr_exit')
    box(m, -7, -7, 7, 7, 0, 2, PANEL, PANEL_SIDE, ('top', 'south', 'west', 'east'), ts=16)
    return m

def build(out):
    os.makedirs(out, exist_ok=True)
    d = json.load(open(DATA, encoding='utf-8'))
    models = {'base': base_model(), 'stairs': stairs_model()}
    for k, sq in enumerate(d['squares']): models[f'sq{k:02d}'] = square_model(k, sq['walls'])
    used = sorted({t for m in models.values() for t in m.tris})
    images = {n: img for n, img, _ in nsbtx.decode(b2files.map_textures(FILES, TEXSET)) if n in used}
    missing = [t for t in used if t not in images]
    assert not missing, f'not in map texture set {TEXSET}: {missing}'
    for t in used: images[t].save(os.path.join(out, t + '.png'))
    open(os.path.join(out, 'palettes.txt'), 'w').write(''.join(f'{t} {t}_pl\n' for t in used))
    batch = []
    for name, m in models.items():
        m.write(os.path.join(out, name + '.dae'))
        batch.append(f'{os.path.join(out, name)}.dae {os.path.join(out, name)}.nsbmd\n')
    open(os.path.join(out, 'batch.txt'), 'w').write(''.join(batch))
    J = os.environ.get('HOENN_JAVA_DIR') or os.path.join(ROOT, 'work', 'java')
    cp = ':'.join([J, os.path.join(ROOT, 'tools', 'CTRMap.jar'), os.path.join(ROOT, 'tools', 'ctrmap-plugins', 'CTRMapV-1.4.1.jar')])
    if not os.path.exists(os.path.join(J, 'ToNsbmd.class')):
        os.makedirs(J, exist_ok=True)
        subprocess.run(['javac', '-cp', cp, '-d', J] + [os.path.join(HERE, 'java', f) for f in os.listdir(os.path.join(HERE, 'java'))
                                                         if f.endswith('.java')], check=True)
    r = subprocess.run(['java', '-Djava.awt.headless=true', '-cp', cp, 'ToNsbmd', '--vcol', '--batch',
                        os.path.join(out, 'batch.txt'), os.path.join(out, 'palettes.txt')], capture_output=True, text=True)
    if r.returncode: raise SystemExit(f'ToNsbmd failed: {r.stderr[-800:]}')
    meta = {name: dict(file=name + '.nsbmd', textures={t: TEXSET for t in m.tris}, tris=sum(len(x) for x in m.tris.values()))
            for name, m in models.items()}
    json.dump(dict(texset=TEXSET, models=meta), open(os.path.join(out, 'models.json'), 'w'), indent=1)
    return meta

def out_dir():
    rooms = os.environ.get('HOENN_INTERIORS_DIR') or os.path.join(ROOT, 'work', 'interiors')
    return os.path.join(rooms, 'BattleFrontier_BattlePyramidFloor')

if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else out_dir()
    meta = build(out)
    print(f'{len(meta)} models -> {out}:', ', '.join(f'{k} {v["tris"]} tris' for k, v in meta.items()))
