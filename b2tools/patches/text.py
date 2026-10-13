"""Rebuild the text archives (a/0/0/2 system, a/0/0/3 script messages) from the decomp's text sources with ours on top:
  - src/text/<kind>/NNNN_*.txt replaces the decomp's file with the same number NNNN
  - src/text/overrides.json replaces single lines: {"system/0109_place_names.txt": {"4": "Littleroot Town"}}, and so do
    the generated src/text/overrides_*.json (same format)
Packed with the decomp's own tools/scripts/text_data.py (handles the game's text encryption)."""
import os, json, glob, shutil, subprocess, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import version  # noqa: E402  (Ruby/Emerald: src/text/<kind>/<version>/NNNN_*.txt replace files, src/text/<version>/overrides*.json lines)
ROOT = os.path.join(os.path.dirname(__file__), '..', '..')
DECOMP = os.path.join(ROOT, 'external', 'pokebw2')
OURS = os.path.join(ROOT, 'src', 'text')

def room_text_numbers():
    """Black 2 text-file number of a Hoenn room -> the room's own number (data/hoenn_interiors.json own_text)."""
    p = os.path.join(ROOT, 'data', 'hoenn_interiors.json')
    rooms = version.load_json(p)['rooms'].values() if os.path.exists(p) else []   # (+ Emerald's claimed rooms, as scripts.py)
    return {r['text']: r['own_text'] for r in rooms if 'own_text' in r}

def apply(files):
    overrides = json.load(open(os.path.join(OURS, 'overrides.json')))
    extras = sorted(glob.glob(os.path.join(OURS, 'overrides_*.json')))       # generated line sets (overrides_key_items.json:
    if version.has_overlay():                                                 # Ruby's/Emerald's own lines after the shared ones
        extras += sorted(glob.glob(os.path.join(OURS, version.OVERLAY, 'overrides*.json')))
    extras += [p for p in os.environ.get('HOENN_EXTRA_TEXT', '').split(':') if p]   # converter/gen_key_items.py
    for extra in extras:                                                      # --install); HOENN_EXTRA_TEXT=a.json:b.json
        for name, lines in json.load(open(extra, encoding='utf-8')).items():  # adds files for a test build
            if name != '_doc': overrides.setdefault(name, {}).update(lines)
    # Hoenn place names (converter/allocate_zones.py) on their lines of the place-name file
    zones = json.load(open(os.path.join(ROOT, 'data', 'hoenn_zones.json')))
    places = overrides.setdefault('system/0109_place_names.txt', {})
    for p in zones['places'].values(): places.setdefault(str(p['line']), p['name'])
    done = []
    for kind, arc in (('system', 'a/0/0/2'), ('script', 'a/0/0/3')):
        with tempfile.TemporaryDirectory() as t:
            d = os.path.join(t, kind)
            shutil.copytree(os.path.join(DECOMP, 'data', 'text', kind), d)
            moved = room_text_numbers() if kind == 'script' else {}
            for f in version.overlay(os.path.join(OURS, kind), '*.txt'):
                num = os.path.basename(f)[:4]
                if int(num) in moved:                     # a room's text: at the room's own number after Black 2's
                    num = f'{moved[int(num)]:04d}'        # files, Black 2's file stays (code reads some directly)
                old = glob.glob(os.path.join(d, num + '*.txt'))
                assert len(old) <= 1, (f, old)
                if old: os.remove(old[0])                 # replaces Black 2's file NNNN, or adds a new one after them
                shutil.copy(f, os.path.join(d, num + os.path.basename(f)[4:]))
            if moved:                                     # rooms without a text file yet: placeholders (no gaps)
                have = {int(os.path.basename(p)[:4]) for p in glob.glob(os.path.join(d, '*.txt'))}
                # up to the highest room number too: a zone whose text number lies past the last file had no file
                # at all, and any script there (a cave ladder) stopped the game ("An error has occurred"; caves_east)
                for n in range(max(have | set(moved.values())) + 1):
                    if n not in have: open(os.path.join(d, f'{n:04d}_room_placeholder.txt'), 'w', encoding='utf-8').write('…\n')
                done.append(f'{kind}/{os.path.basename(f)}')
            for name, lines in overrides.items():
                if not name.startswith(kind + '/'): continue
                p = os.path.join(d, name.split('/', 1)[1])
                text = open(p, encoding='utf-8').read().split('\n')
                # a line at the file's end appends (fairy_core 2026-10-08: new moves past 559): before the closing
                # \pad{..} line (the packer's padding) and the trailing empty element, one new line after another
                end = next((k for k in range(len(text) - 1, -1, -1) if text[k].startswith('\\pad{')), None)
                if end is None: end = len(text) - 1 if text and text[-1] == '' else len(text)
                for i in sorted(lines, key=int):
                    if int(i) >= end:
                        assert int(i) == end, f'{name}: line {i} would leave a gap after line {end - 1}'
                        text.insert(end, lines[i]); end += 1
                    else:
                        text[int(i)] = lines[i]
                open(p, 'w', encoding='utf-8').write('\n'.join(text))
                done.append(f'{name} lines {sorted(lines, key=int)}')
            out = os.path.join(files, *arc.split('/'))
            if os.path.islink(out): os.unlink(out)
            subprocess.run([sys.executable, os.path.join(DECOMP, 'tools', 'scripts', 'text_data.py'), 'pack', d, out],
                           check=True, cwd=DECOMP)
            if kind == 'system' and os.environ.get('HOENN_TEXT_SLOTS', '1') == '1':
                done.append(fixed_slots(files))
    return ', '.join(done)

# ---- fixed slots in a/0/0/2 (story_fixups 2026-10-07) ------------------------------------------------------------------
# The game opens some system texts once at boot and keeps reading them through that handle: the species names (file 90:
# PML_CreatePkm names every new Pokémon from it) at the offset a/0/0/2's file table gave at boot. A savestate keeps that
# handle, so after any size change of an earlier system file (ch1's lines in 0023 and 0037) the states made before it
# named every Pokémon created afterwards "????" (trainers' and gift Pokémon; tested: Youngster Calvin's Zigzagoon from
# work/emu/base_littleroot.dst, right on a cold boot). With HOENN_TEXT_SLOTS=1 every system file sits in a fixed slot
# (vanilla size + 1/16 + 64 bytes, zero-padded; the message reader goes by the file's own offset table), so editing a
# line no longer moves the files after it. On by default since the v13.1 savestate remake (HOENN_TEXT_SLOTS=0 turns it off).
def fixed_slots(files):
    import narcio
    vanilla = narcio.load(os.path.join(DECOMP, 'build', 'b2_us', 'files'), 2)
    entries = narcio.load(files, 2)
    assert len(entries) == len(vanilla), (len(entries), len(vanilla))
    over = []
    for i, (e, v) in enumerate(zip(entries, vanilla)):
        slot = (len(v) + 64 + len(v) // 16 + 3) & ~3
        if len(e) > slot: over.append(f'{i:04d}: {len(e)} B > slot {slot}')
        else: entries[i] = e + bytes(slot - len(e))
    if over:
        raise SystemExit('system text over its fixed slot (shorten it, or raise the slot formula and remake the base '
                         'savestates): ' + ', '.join(over))
    narcio.save(files, 2, entries)
    return f'system text: {len(entries)} files in fixed slots'
