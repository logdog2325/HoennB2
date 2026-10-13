"""Black 2's palm tree (Humilau City) for Mossdeep City's trees (user decision 2026-10-11, b2_trees: Sapphire's Mossdeep
trees are broadleaf island trees; Black 2's only tropical tree is Humilau's palm).

Read from Black 2's Humilau chunk 300 (texture set 230) with apicula: one palm is 16 triangles, every normal (0, 1, 0)
(as Black 2's round tree), materials with diffuse 25/31, "diffuse = vertex colour", ambient 31 and the trunk ki04ax
drawn from both sides (nsbmd_fix.TREE_MATS / TWO_SIDED):
  - trunk: two crossed ki04ax cards (16x64 image), 11.7 wide, from the base to 38.6;
  - crown: two ki04bx fans (a square and the same square turned 45 degrees, rising from about 29-33 at the rim to
    37.5-38.4 at the middle) under one ki04dx fan (35-39.5): a drooping umbrella about 30 across;
  - shadow: ki04c (A3I5), one 32x32 square per palm (Humilau: one quad for a row of four, the image once per palm).
The base stands 3 above the ground (Humilau: sand at -80, trunk and shadow at -77); the shadow is drawn at 4 here, as
build_chunk.tree_row's (2 clear of the tall-grass layers). A palm covers 2x2 tiles, as a Sapphire tree.
This module draws nothing by itself (world.py build_cell and ground.py draw_trees call palm() for Mossdeep's trees);
it lists the four textures, which patches/hoenn_textures.py copies from set 230 into Hoenn's set (about 2.7 KB)."""

CLASSES = set()
TEXTURES = {'ki04ax': 230, 'ki04bx': 230, 'ki04c': 230, 'ki04dx': 230}
PALM_MAPS = {'MossdeepCity'}

# (material, three (x, y, z, u, v) corners): Humilau chunk 300's palm at chunk (48, 240), relative to its trunk's foot
TEMPLATE = (
    ('ki04ax', ((0.0, 0.0, 5.578, 0.0, 0.0), (0.0, 0.0, -6.094, 1.0, 0.0), (0.0, 38.609, -6.094, 1.0, 0.991))),
    ('ki04ax', ((0.0, 0.0, 5.578, 0.0, 0.0), (0.0, 38.609, -6.094, 1.0, 0.991), (0.0, 38.609, 5.578, 0.0, 0.991))),
    ('ki04ax', ((-5.844, 0.0, -0.266, 0.0, 0.0), (5.844, 0.0, -0.266, 1.0, 0.0), (5.844, 38.609, -0.266, 1.0, 0.991))),
    ('ki04ax', ((-5.844, 0.0, -0.266, 0.0, 0.0), (5.844, 38.609, -0.266, 1.0, 0.991), (-5.844, 38.609, -0.266, 0.0, 0.991))),
    ('ki04dx', ((-13.484, 35.031, 12.875, -0.002, -0.002), (13.484, 35.031, 12.875, 1.002, -0.002), (0.0, 39.531, 0.062, 0.5, 0.5))),
    ('ki04dx', ((13.484, 35.031, 12.875, 1.002, -0.002), (13.484, 38.172, -13.953, 1.002, 1.002), (0.0, 39.531, 0.062, 0.5, 0.5))),
    ('ki04dx', ((0.0, 39.531, 0.062, 0.5, 0.5), (13.484, 38.172, -13.953, 1.002, 1.002), (-13.484, 38.172, -13.953, -0.002, 1.002))),
    ('ki04dx', ((-13.484, 35.031, 12.875, -0.002, -0.002), (0.0, 39.531, 0.062, 0.5, 0.5), (-13.484, 38.172, -13.953, -0.002, 1.002))),
    ('ki04bx', ((0.0, 29.172, 16.266, 1.002, -0.002), (15.516, 30.641, 0.812, 1.002, 1.002), (0.0, 37.547, 1.609, 0.5, 0.5))),
    ('ki04bx', ((15.516, 30.641, 0.812, 1.002, 1.002), (0.0, 32.047, -14.625, -0.002, 1.002), (0.0, 37.547, 1.609, 0.5, 0.5))),
    ('ki04bx', ((0.0, 37.547, 1.609, 0.5, 0.5), (0.0, 32.047, -14.625, -0.002, 1.002), (-15.516, 30.594, 0.812, -0.002, -0.002))),
    ('ki04bx', ((-14.453, 31.609, 13.719, -0.002, -0.002), (14.453, 31.609, 13.719, 1.002, -0.002), (0.0, 38.406, 0.094, 0.5, 0.5))),
    ('ki04bx', ((14.453, 31.609, 13.719, 1.002, -0.002), (14.453, 32.938, -15.203, 1.002, 1.002), (0.0, 38.406, 0.094, 0.5, 0.5))),
    ('ki04bx', ((0.0, 38.406, 0.094, 0.5, 0.5), (14.453, 32.938, -15.203, 1.002, 1.002), (-14.453, 32.938, -15.203, -0.002, 1.002))),
    ('ki04bx', ((0.0, 29.172, 16.266, 1.002, -0.002), (0.0, 37.547, 1.609, 0.5, 0.5), (-15.516, 30.594, 0.812, -0.002, -0.002))),
    ('ki04bx', ((-14.453, 31.609, 13.719, -0.002, -0.002), (0.0, 38.406, 0.094, 0.5, 0.5), (-14.453, 32.938, -15.203, -0.002, 1.002))),
)

def palm(m, cx, cz, s=1.0, lift=0.0, shadow=True):
    """One palm on dae.Model m, its trunk's foot at model (cx, 3, cz), scaled evenly by s (0.5 on one tile, 1.5 for
    Sapphire's 3x3 trees); lift raises it (world.overlap_fill's overlapping trees); shadow: its 32x32 ki04c square."""
    for mat, tri in TEMPLATE:
        m.tri(mat, [(cx + x * s, 3 + y * s + lift, cz + z * s, u, v) for x, y, z, u, v in tri])
    if shadow:
        h = 16 * s
        m.quad('ki04c', [(cx - h, 4, cz + h, 0, 0), (cx + h, 4, cz + h, 1, 0), (cx + h, 4, cz - h, 1, 1),
                         (cx - h, 4, cz - h, 0, 1)])

def is_palm(world, wx, wz):
    """A tree on this world tile is a palm (its map is one of PALM_MAPS)."""
    e = world.get((wx, wz))
    return bool(e) and e[0] in PALM_MAPS

def draw(m, cell):
    return None
