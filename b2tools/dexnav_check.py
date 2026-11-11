"""The DexNav's hardware budgets (notes/DEXNAV.md "Budgets"), for every wild table of the version: patches/dexnav.py runs
check() in each build (the build stops on a miss); standalone, without a build (the tables from src/encounters):
    HOENN_VERSION=... python3 b2tools/dexnav_check.py

- characters: bank H's 768 (0x6000 / 32) hold a view's art and pieces from character 1, in the area view every zone's
  snapshot after them, then the view's text windows (dexnav_art.py WINDOWS);
- palette lines: a view's lines (and the area view's snapshot's after them) in 0-14; 15 is the windows';
- sprites (sub OBJ, 16 KB of VRAM bank I, 128 OAM entries, 32 affine sets, 16 palettes): the zone's icons (1 KB each:
  two 32 x 32 frames), the ring and the cursor (1 KB each), the Found view's double-size icon (the zone's characters),
  two type icons (256 B each), Found's / Hidden's own copy of the species' icon (1 KB);
- HEAPID_FIELD_MENU (61,384 B; the screen's peak must stay under NEED_MENU_HEAP, what it asks for before it starts):
  the screen without windows (SCREEN_BASE, measured), the windows (32 B a character), the front map's copy, the pieces,
  the 2 KB read buffer.
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import version  # noqa: E402

CHARS = 0x6000 // 32
ART_LINES = 15
OBJ_VRAM = 16 << 10
OAM = 128
OBJ_PALETTES = 16
MENU_HEAP = 61384
SCREEN_BASE = 39220 - 4224 - 1536 - 492 - 2048   # the screen's own (font, texts, work, sprites' bookkeeping): the area
# view measured 39,220 B held (combined Emerald ROM b8add5e3, 2026-11-09, Granite Cave), less its windows, front copy,
# pieces and read buffer
PRINT_QUEUE = 0x200 + 0x60                        # the place name's print queue (dexnav_screen.c QUEUE_SIZE), since then
FRONT_COPY = 32 * 24 * 2
READ_BUFFER = 2048
NEED_MENU_HEAP = 0xA000                    # dexnav.c: the free menu heap the screen asks for before it starts
ICON_CHARS = 0x400
UI_CHARS = 2 * 0x400                       # the ring and the cursor
TYPE_CHARS = 2 * 0x100


def check(views, snaps, counts):
    """views: {name: dexnav_art.pack_view()}; snaps: dexnav_snapshots.build()'s list; counts: {file: (land, water)}.
    Returns (report lines, problems)."""
    problems, report = [], []
    snap_tiles = max(r['tiles'] for _, _, r in snaps)
    snap_lines = max(r['lines'] for _, _, r in snaps)
    for name, v in views.items():
        chars = 1 + v['tiles'] + (snap_tiles if name == 'area' else 0) + v['windows']
        lines = v['lines'] + (snap_lines if name == 'area' else 0)
        pieces = sum(8 + 2 * w * h for _, w, h, _, _, _ in v['pieces'])
        heap = SCREEN_BASE + 32 * v['windows'] + FRONT_COPY + pieces + READ_BUFFER + PRINT_QUEUE
        report.append(f'{name}: {chars} of {CHARS} characters ({v["tiles"]} art'
                      + (f', {snap_tiles} the largest snapshot' if name == 'area' else '') + f', {v["windows"]} windows), '
                      f'{lines} of {ART_LINES} palette lines, menu heap ~{heap} B at its peak')
        if chars > CHARS:
            problems.append(f'{name}: {chars} characters > {CHARS}')
        if lines > ART_LINES:
            problems.append(f'{name}: {lines} palette lines > {ART_LINES}')
        if heap > NEED_MENU_HEAP:
            problems.append(f'{name}: ~{heap} B of menu heap > the {NEED_MENU_HEAP} B the screen asks for')
    worst = max(counts.items(), key=lambda kv: sum(kv[1]))
    n = sum(worst[1])
    vram = (n + 1) * ICON_CHARS + UI_CHARS + TYPE_CHARS        # (+1: Found's and Hidden's big icon)
    oam = n + 2 + 1 + 2
    report.append(f'sprites: {n} icons at most (file {worst[0]}): {vram} of {OBJ_VRAM} B of sub OBJ VRAM, {oam} of {OAM} '
                  f'OAM entries, 2 affine sets, 8 of {OBJ_PALETTES} palettes')
    if vram > OBJ_VRAM:
        problems.append(f'sprites: {vram} B of sub OBJ VRAM > {OBJ_VRAM} (file {worst[0]}: {n} icons)')
    for f, data, r in snaps:
        if r['tiles'] + 1 + views['area']['tiles'] > CHARS - views['area']['windows']:
            problems.append(f'snapshot {r["map"]}: {r["tiles"]} characters')
    report.append(f'snapshots: {len(snaps)} ({sum(len(d) for _, d, _ in snaps)} B), {snap_tiles} characters and '
                  f'{snap_lines} palette lines at most')
    return report, problems


def main():
    import dexnav_art as DA, dexnav_snapshots as DS
    views = {n: DA.pack_view(n) for n in DA.VIEWS}
    counts = DS.counts_source()
    snaps = DS.build(1 + views['area']['tiles'], views['area']['lines'], counts)
    report, problems = check(views, snaps, counts)
    print(version.NAME)
    print('\n'.join('  ' + r for r in report))
    if problems:
        sys.exit('dexnav_check: ' + '; '.join(problems))
    print('  ok')


if __name__ == '__main__':
    main()
