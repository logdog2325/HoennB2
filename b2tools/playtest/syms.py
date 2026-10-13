import os, re, glob
ROOT = os.path.expanduser('~/Documents/GitHub/HoennB2/external/pokebw2/config/b2_us/arm9')
_S = None
def load():
    global _S
    if _S is None:
        _S = []
        for f in [os.path.join(ROOT, 'symbols.txt')] + glob.glob(os.path.join(ROOT, 'overlays', '*', 'symbols.txt')):
            ov = os.path.basename(os.path.dirname(f)) if 'overlays' in f else 'arm9'
            for line in open(f):
                m = re.match(r'(\S+) kind:function\S* addr:(0x[0-9a-f]+)', line)
                if m: _S.append((int(m.group(2), 16), m.group(1), ov))
    return _S
def name(addr):
    a = addr & ~1
    return [f'{ov}:{n}' for (x, n, ov) in load() if x == a]
