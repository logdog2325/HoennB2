"""Building models' texture-pattern animations vs their pack's texture set (museum_freeze, 2026-10-12).

    python3 anim_tex_check.py ROM.nds|files_dir [--all]

A building model's info record (building packs a/2/2/5 exterior, a/2/2/6 interior; notes/GEN5_MAPS.md) may embed a
BTP0 texture-pattern animation that swaps the model's texture by NAME, frame by frame, from the pack's texture set
(a/1/7/4 exterior, a/1/7/5 interior, same index as the pack). When one of those names is missing from the set, NNS's
lookup (NNS_G3dGetResDataByIdx, arm9 0x02068458) returns NULL and the pattern code (func_02069dc0) reads through it:
DeSmuME has no memory protection and reads the ITCM mirror at 0 (at most a wrong texture for a frame), real hardware
and melonDS take a data abort and the game freezes (v16.6/v16.7: entering the Slateport Museum, Black 2's machine02
copied without its frames machin0.2 / machin0.3). Lists every (pack, model, animation) whose texture or palette names
are missing; exit status 1 if any. --all also lists the complete ones."""
import os, sys, struct
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import nsbtx



def gf_container(d):
    n = struct.unpack_from('<H', d, 2)[0]
    offs = struct.unpack_from('<%dI' % (n + 1), d, 4)
    return [d[offs[i]:offs[i + 1]] for i in range(n)]


def narc(src, n):
    if os.path.isdir(src):
        sys.path.insert(0, HERE); import narcio
        return narcio.load(src, n)
    from npc_check import Files
    return Files(src).narc(n)


def btp_names(info):
    """[(anim name, texture names, palette names)] of every BTP0 embedded in an info record."""
    out = []
    k = info.find(b'BTP0')
    while k >= 0:
        f = info[k:]
        nb = struct.unpack_from('<H', f, 0xE)[0]
        for b in range(nb):
            bo = struct.unpack_from('<I', f, 0x10 + 4 * b)[0]
            if f[bo:bo + 4] != b'PAT0': continue
            for name, ent in nsbtx._dict(f, bo + 8):
                a = bo + struct.unpack_from('<I', ent, 0)[0]
                _, ntex, npal, otex, opal = struct.unpack_from('<HBBHH', f, a + 4)
                rd = lambda o, i: f[a + o + 16 * i:a + o + 16 * i + 16].rstrip(b'\0').decode('ascii', 'replace')
                out.append((name, [rd(otex, i) for i in range(ntex)], [rd(opal, i) for i in range(npal)]))
        k = info.find(b'BTP0', k + 4)
    return out


def set_names(btx):
    t = nsbtx.tex0(btx)
    texs = {n for n, _ in nsbtx._dict(t, struct.unpack_from('<H', t, 0xE)[0])}
    pals = {n for n, _ in nsbtx._dict(t, struct.unpack_from('<H', t, 0x34)[0])}
    return texs, pals


def check(src, show_all=False):
    bad = 0
    for kind, pa, ta in (('exterior', 225, 174), ('interior', 226, 175)):
        packs, texsets = narc(src, pa), narc(src, ta)
        for p, pk in enumerate(packs):
            if pk[:2] != b'AB' or p >= len(texsets) or not texsets[p]: continue
            secs = gf_container(pk); n = len(secs) // 2
            have = None
            for info in secs[:n]:
                for anim, texs, pals in btp_names(info):
                    if have is None: have = set_names(texsets[p])
                    mt, mp = [t for t in texs if t not in have[0]], [q for q in pals if q not in have[1]]
                    res = struct.unpack_from('<H', info, 0)[0]
                    if mt or mp:
                        bad += 1
                        print(f'{kind} pack {p} model res {res} anim {anim}: MISSING textures {mt} palettes {mp}')
                    elif show_all:
                        print(f'{kind} pack {p} model res {res} anim {anim}: ok ({len(texs)} textures)')
    print(f'{bad} animation(s) with missing textures' if bad else 'all texture-pattern animations complete')
    return bad


if __name__ == '__main__':
    sys.exit(1 if check(sys.argv[1], '--all' in sys.argv) else 0)
