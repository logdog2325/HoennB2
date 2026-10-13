"""Sort one pokeruby metatile into a class letter (moved out of export.py so other scripts can use it)."""

def classify(mr, v):
    m, col = int(v & 0x3FF), (int(v) >> 10) & 3
    b = mr.behavior(m)
    px = mr.render(m)[..., :3].astype(int)
    mean = px.reshape(-1, 3).mean(0)
    red = ((px[..., 0] > 190) & (px[..., 1] < 130)).sum()
    if b == 0x02: return 'T'
    if 0x10 <= b <= 0x17: return 'W'
    if 0x38 <= b <= 0x3B: return 'L'
    if b == 0x21: return 'S'
    rr, gg, bb = mean
    if col:
        if gg > rr + 35 and gg > bb + 25: return 'X'   # tree canopy
        return 'B'                                     # building / prop, split later
    if red > 12: return 'F'
    if gg > 200 and rr > 135: return 'P'               # pale mint GBA path
    if rr > 160 and gg < 215 and abs(rr - gg) < 50 and rr > bb: return 'P'  # sandy yard
    return 'G'
