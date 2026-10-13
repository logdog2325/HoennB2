"""gyms_league agent: compose proof images (Sapphire's map next to the emulator's frames) from walk.py sheets.

    python3 gyms_league_proof.py SHEET_DIR        -> screenshots/gyms_league/*.png

A sheet is walk.py's output (256x192 frames, 4 per row). Each row of a proof: Sapphire's render
(screenshots/sapphire/<Map>.png, left half) scaled to the frame height, then the chosen frames.
"""
import os, sys
from PIL import Image, ImageDraw

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
OUT = os.path.join(ROOT, 'screenshots', 'gyms_league')
FW, FH = 256, 192

def frames(sheet):
    im = Image.open(sheet).convert('RGB')
    out = []
    for r in range(im.height // FH):
        for c in range(im.width // FW):
            f = im.crop((c * FW, r * FH, (c + 1) * FW, (r + 1) * FH))
            if f.getbbox() is None or max(f.convert('L').getextrema()) < 8: continue      # empty sheet cell
            out.append(f)
    return out

def sapphire(name, h=FH):
    im = Image.open(os.path.join(ROOT, 'screenshots', 'sapphire', name + '.png')).convert('RGB')
    im = im.crop((0, 0, im.width // 2 - 16, im.height))
    k = h / im.height
    return im.resize((max(1, int(im.width * k)), h), Image.LANCZOS)

def row(label, saps, shots):
    parts = [sapphire(s) for s in saps] + shots
    w = sum(p.width for p in parts) + 6 * (len(parts) - 1)
    im = Image.new('RGB', (w, FH + 14), (24, 24, 32))
    x = 0
    for p in parts: im.paste(p, (x, 14)); x += p.width + 6
    ImageDraw.Draw(im).text((4, 1), label, fill=(255, 255, 255))
    return im

def stack(rows, path):
    w = max(r.width for r in rows); h = sum(r.height for r in rows) + 6 * (len(rows) - 1)
    im = Image.new('RGB', (w, h), (0, 0, 0))
    y = 0
    for r in rows: im.paste(r, (0, y)); y += r.height + 6
    os.makedirs(OUT, exist_ok=True)
    im.save(path); print(path, im.size)

def main(d):
    f = {n: frames(os.path.join(d, n + '.png')) for n in ('rustboro', 'dewford', 'mauville', 'lavaridge', 'fortree',
         'petalburg', 'mossdeep', 'sootopolis', 'sootopolis_b1', 'league') if os.path.exists(os.path.join(d, n + '.png'))}
    pick = lambda n, idx: [f[n][i] for i in idx if i < len(f[n])]
    stack([row('Rustboro Gym: Sapphire | town door | entrance | maze | dais', ['RustboroCity_Gym'], pick('rustboro', [0, 1, 2, 3])),
           row('Dewford Gym: Sapphire | town door | entrance | maze', ['DewfordTown_Gym'], pick('dewford', [0, 1, 2, 3])),
           row('Mauville Gym: Sapphire | town door | entrance | barriers | poles', ['MauvilleCity_Gym'], pick('mauville', [0, 1, 2, 3]))],
          os.path.join(OUT, 'gyms_1_rustboro_dewford_mauville.png'))
    stack([row('Lavaridge Gym: Sapphire 1F, B1F | town door | 1F | hole -> B1F', ['LavaridgeTown_Gym_1F', 'LavaridgeTown_Gym_B1F'],
               pick('lavaridge', [0, 1, 3])),
           row('Fortree Gym: Sapphire | town door | entrance | posts', ['FortreeCity_Gym'], pick('fortree', [0, 1, 2, 3])),
           row('Petalburg Gym (1x4 chunks): Sapphire | town door | entrance | through a door | next room', ['PetalburgCity_Gym'],
               pick('petalburg', [0, 1, 2, 3]))],
          os.path.join(OUT, 'gyms_2_lavaridge_fortree_petalburg.png'))
    stack([row('Mossdeep Gym: Sapphire | town door | entrance | spin tiles | maze', ['MossdeepCity_Gym'], pick('mossdeep', [0, 1, 2, 3])),
           row('Sootopolis Gym: Sapphire 1F, B1F | entrance | ice rooms | ladder -> B1F', ['SootopolisCity_Gym_1F', 'SootopolisCity_Gym_B1F'],
               pick('sootopolis', [0, 2, 3]) + pick('sootopolis_b1', [1]))],
          os.path.join(OUT, 'gyms_3_mossdeep_sootopolis.png'))
    L = f.get('league', [])
    stack([row('League: Sapphire corridor, Sidney | town | lobby | Corridor 5 | Sidney', ['EverGrandeCity_Corridor5', 'EverGrandeCity_SidneysRoom'],
               [L[i] for i in (0, 1, 2, 4) if i < len(L)]),
           row('Sapphire Phoebe, Glacia | Corridor 1 | Phoebe | Glacia | Drake', ['EverGrandeCity_PhoebesRoom', 'EverGrandeCity_GlaciasRoom'],
               [L[i] for i in (5, 7, 10, 13) if i < len(L)]),
           row('Sapphire Drake, Corridor 4, Champion | Corridor 4 (1x2 chunks) foot, middle | Champion', ['EverGrandeCity_DrakesRoom',
               'EverGrandeCity_Corridor4', 'EverGrandeCity_ChampionsRoom'], [L[i] for i in (14, 15, 17) if i < len(L)])],
          os.path.join(OUT, 'league_e4_champion.png'))

if __name__ == '__main__':
    main(sys.argv[1])
