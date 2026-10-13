"""The trainer card's 3D badges (top screen, when a badge is touched) for Hoenn: src/trainer_card/badge3d_N.nsbmd, N = 0..7
in Sapphire's badge order (v165_fixes 2026-10-11; installed by b2tools/patches/trainer_card.py as a/0/3/9 files 56-63).

    python3 b2tools/trainer_card_models.py          (needs Java: b2tools/java/ToNsbmd.java --vcol --tex)

Black 2's are Unova-shaped models (gym01-gym08: one mesh in the XZ plane, 16-40 units wide, 55-66 long, ~3 thick,
two 32x64 textures, vertex colours). Each Hoenn one is Sapphire's own trainer-card badge (graphics/trainer_card/
badges.png, 16x16) at 2x as a 32x32 texture with its outline cut out (colour 0 clear), on a plate the size of Black 2's
badges: the face on both sides (the back mirrored, so it reads the right way round when the badge turns) and four inner
layers in a darker shade, which show as the badge's edge when it turns side-on. No new drawing: the picture is
Sapphire's, the plate only carries it.
"""
import os, sys, subprocess
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
from dae import Model                                                    # noqa: E402

SRC = os.path.join(ROOT, 'external', 'pokeruby', 'graphics', 'trainer_card', 'badges.png')
OUT = os.path.join(ROOT, 'src', 'trainer_card')
WORK = os.path.join(os.environ.get('HOENN_TRAINER_CARD_WORK') or os.path.join(ROOT, 'work', 'trainer_card'))
HALF = 24.0              # half the plate's side, units (Black 2's badges: 16-40 wide, 55-66 long)
THICK = 1.5              # half its thickness
EDGE = (0.55, 0.55, 0.6)


def badge_png(k, path):
    im = Image.open(SRC)
    pal = im.getpalette()[:48]
    px = list(im.getdata())
    out = Image.new('RGBA', (32, 32))
    for y in range(32):
        for x in range(32):
            v = px[(y // 2) * 128 + 16 * k + x // 2]
            out.putpixel((x, y), (0, 0, 0, 0) if v == 0 else (*pal[3 * v:3 * v + 3], 255))
    out.save(path)


def plate(name):
    m = Model(name)
    h, t = HALF, THICK
    # (z grows toward the bottom of the picture: v = 0 at z = -h)
    def layer(y, up, col, mirror=False):
        u0, u1 = (1, 0) if mirror else (0, 1)
        a = (-h, y, -h, u0, 0); b = (h, y, -h, u1, 0); c = (h, y, h, u1, 1); d = (-h, y, h, u0, 1)
        m.quad(name, [a, d, c, b] if up else [a, b, c, d], col)
    layer(t, True, (1.0, 1.0, 1.0))                      # face (+y)
    layer(-t, False, (1.0, 1.0, 1.0), mirror=True)       # back (-y), mirrored
    for i in range(1, 5):                                # the edge: inner layers, both ways
        y = -t + 2 * t * i / 5
        layer(y, True, EDGE); layer(y, False, EDGE, mirror=True)
    return m


def main():
    os.makedirs(WORK, exist_ok=True); os.makedirs(OUT, exist_ok=True)
    J = os.environ.get('HOENN_JAVA_DIR') or os.path.join(ROOT, 'work', 'java')
    CP = f"{J}:{ROOT}/tools/CTRMap.jar:{ROOT}/tools/ctrmap-plugins/CTRMapV-1.4.1.jar"
    os.makedirs(J, exist_ok=True)
    subprocess.run(['javac', '-cp', CP, '-d', J] + [os.path.join(HERE, 'java', f) for f in os.listdir(os.path.join(HERE, 'java'))], check=True)
    for k in range(8):
        name = f'hbadge{k}'
        badge_png(k, os.path.join(WORK, name + '.png'))
        plate(name).write(os.path.join(WORK, name + '.dae'), wrap={name: ('CLAMP', 'CLAMP')})
        open(os.path.join(WORK, 'palettes.txt'), 'a' if k else 'w').write(f'{name} {name}_pl\n')
    for k in range(8):
        name = f'hbadge{k}'
        r = subprocess.run(['java', '-Djava.awt.headless=true', '-cp', CP, 'ToNsbmd', '--vcol', '--tex',
                            os.path.join(WORK, name + '.dae'), os.path.join(OUT, f'badge3d_{k}.nsbmd'),
                            os.path.join(WORK, 'palettes.txt')], capture_output=True, text=True)
        print(r.stdout.strip(), r.stderr.strip()[:300])


if __name__ == '__main__':
    main()
