"""Sapphire's and Ruby's own Pokédex text in Black 2's Pokédex (hoenn_pokedex, v16; notes/POKEDEX.md).

    python3 gen_dex_text.py            check only (prints the report)
    python3 gen_dex_text.py --install  writes the files below (the text patch packs them)

Source: pokeruby src/data/pokedex_entries_en.h (gPokedexEntries, national order 1-386), resolved for SAPPHIRE and for
RUBY with REVISION 1 (the user's Sapphire is rev 1, notes/SETUP.md; rev 1 fixes Paras's type and Mawile's spelling).
Text through gen3text.convert (Sapphire's words, Gen 5 capitals; IQ and DNA stay capitals).

Black 2's Pokédex fields (system text, read in ov296 func_ov296_0219e34c, the English INFO page; the files come from
the table data_ov296_0219fb3c) and what goes in them:
  0442  entry text, 733 lines (species, then forms 650-732)  <- Sapphire's page 1 (lines 1-386 and the form lines of
        Unown 651-677, Castform 678-680, Deoxys 681-683). The window holds 3 lines of 222 px (Black 2's own longest
        line measures 222 px in font 0), and a Gen 3 page is 3 lines, so a page fits as Sapphire wrote it.
  0443  733 lines, all blank in the US game (never loaded: no code or table names file 443)  <- Sapphire's page 2, same
        indexing. Shown by the A-button page flip (b2tools/patches/hoenn_pokedex.py), as Sapphire's A flips pages.
  0464  category, 651 lines by species  <- "<Sapphire's category> Pokémon" (Wood Gecko Pokémon)
  0451  height, 733 lines  <- Sapphire's (pokedex.c sub_8091458: tenths of an inch, rounded, feet'inches")
  0471  weight, 733 lines  <- Sapphire's (sub_8091564: tenths of a pound, rounded, "N.N lbs.")
        Checked: all three equal Black 2's lines for 1-386 already (Gen 5 kept Gen 3's categories and measures; the
        camel-case FlyScorpion / TinyRaccoon / TinySwallow are Gen 5's spelling of Sapphire's words), so only lines
        that differ are written: none.
  Not replaced: 0444-0449 / 0452-0477 / 0490-0494 (the other languages' fields: only for Pokémon registered in another
  language) and species 387-649 (not in Sapphire's Pokédex; Black 2's text stays).
Every file keeps its fixed slot (HOENN_TEXT_SLOTS): the report prints each file's packed size against its slot.

Also: 0478 line 0 "UNOVA POKÉDEX" (the list's header, text in Black 2's font) -> HOENN POKÉDEX, line 10 UNOVA -> HOENN;
0479 line 17 "Unova Pokédex: Search Mode"; 0362 lines 53 / 57 (the Habitat list's UNOVA tab and stamp line).

Writes:
  src/text/overrides_hoenn_dex.json         Sapphire (both versions read it)
  src/text/ruby/overrides_hoenn_dex.json    Ruby's lines that differ (page 1 of the 203 switched entries)
  src/text/system/0443_dex_page2.txt        Sapphire's page 2
  src/text/system/ruby/0443_dex_page2.txt   Ruby's page 2
"""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, 'b2tools'))
import gen3text  # noqa: E402
import b2font  # noqa: E402

ENTRIES = os.path.join(ROOT, 'external', 'pokeruby', 'src', 'data', 'pokedex_entries_en.h')
B2TEXT = os.path.join(ROOT, 'external', 'pokebw2', 'data', 'text', 'system')
TEXT = os.path.join(ROOT, 'src', 'text')
REVISION = 1
N_SPECIES = 386
FORMS = {201: range(651, 678), 351: range(678, 681), 386: range(681, 684)}   # Unown, Castform, Deoxys form lines
MAX_W, MAX_LINES = 222, 3
gen3text.KEEP |= {'IQ', 'DNA'}
gen3text.SPECIAL.update({'FARFETCH’D': 'Farfetch’d',                         # Gen 5's spellings of Sapphire's words
                         'FLYSCORPION': 'FlyScorpion', 'TINYRACCOON': 'TinyRaccoon', 'TINYSWALLOW': 'TinySwallow'})


def resolve(text, ver):
    """pokeruby's #ifdef SAPPHIRE / #else / #endif and #if REVISION >= 1 for one version."""
    out, stack = [], []
    for line in text.split('\n'):
        s = line.strip()
        if s.startswith('#ifdef '): stack.append(s.split()[1] == ver); continue
        if s.startswith('#if REVISION >= 1'): stack.append(REVISION >= 1); continue
        if s.startswith('#if'): raise SystemExit(f'unknown switch {s!r}')
        if s.startswith('#else'): stack[-1] = not stack[-1]; continue
        if s.startswith('#endif'): stack.pop(); continue
        if all(stack): out.append(line)
    assert not stack
    return '\n'.join(out)


def entries(ver):
    """[(category, height dm, weight hg, page1, page2)] by national number 0-386, in pokeruby's text."""
    t = resolve(open(ENTRIES, encoding='utf-8').read(), ver)
    descs = {m.group(1): ''.join(re.findall(r'"((?:[^"\\]|\\.)*)"', m.group(2)))
             for m in re.finditer(r'static const u8 (DexDescription_\w+)\[\] = _\((.*?)\);', t, re.S)}
    arr = t[t.index('gPokedexEntries[] ='):]
    out = [(c, int(h), int(w), descs[p1], descs[p2]) for c, h, w, p1, p2 in re.findall(
        r'\.categoryName = _\("([^"]*)"\),\s*\.height = (\d+),\s*\.weight = (\d+),\s*'
        r'\.descriptionPage1 = (\w+),\s*\.descriptionPage2 = (\w+),', arr)]
    assert len(out) == N_SPECIES + 1, len(out)
    return out


def height(dm):
    """pokeruby pokedex.c sub_8091458 (UNITS_IMPERIAL)."""
    inches = dm * 10000 // 254
    if inches % 10 >= 5: inches += 10
    feet = inches // 120
    inches = (inches - feet * 120) // 10
    return f"{feet}'{inches:02d}\""


def weight(hg):
    """pokeruby pokedex.c sub_8091564 (UNITS_IMPERIAL), without its leading pad spaces (Black 2 right-aligns)."""
    lbs = hg * 100000 // 4536
    if lbs % 10 >= 5: lbs += 10
    return f'{lbs // 100}.{lbs % 100 // 10} lbs.'


def text(s):
    out, unknown = gen3text.convert(s)
    assert not unknown, (s, unknown)
    return out


def category(c):
    return text(c) + ' Pokémon'


def check_page(font, species, page, s, problems):
    lines = s.split('\\n')
    if len(lines) > MAX_LINES: problems.append(f'#{species} page {page}: {len(lines)} lines')
    for l in lines:
        w = font.width(l)
        if w > MAX_W: problems.append(f'#{species} page {page}: {w} px > {MAX_W}: {l!r}')
        bad = sorted({c for c in l if not font.has(c)})
        if bad: problems.append(f'#{species} page {page}: characters not in font 0: {bad}')


def build(ver):
    font = b2font.load(0)
    problems = []
    lines = {'system/0442.txt': {}, 'system/0464.txt': {}, 'system/0451.txt': {}, 'system/0471.txt': {}}
    page2 = [''] * 733
    for n, (c, h, w, p1, p2) in enumerate(entries(ver)):
        if n == 0: continue
        p1, p2 = text(p1), text(p2)
        check_page(font, n, 1, p1, problems)
        check_page(font, n, 2, p2, problems)
        for i in [n, *FORMS.get(n, ())]:
            lines['system/0442.txt'][str(i)] = p1
            lines['system/0451.txt'][str(i)] = height(h)
            lines['system/0471.txt'][str(i)] = weight(w)
            page2[i] = p2
        lines['system/0464.txt'][str(n)] = category(c)
    return lines, page2, problems


def b2_lines(name):
    return open(os.path.join(B2TEXT, name), encoding='utf-8').read().split('\n')


def packed_size(lines):
    """Size of a message file as tools/scripts/text_data.py pack_file writes it (no compressed lines here)."""
    chars = sum(len(l.replace('\\n', '\n')) + 1 for l in lines)
    return (16 + 4 + 8 * len(lines) + 2 * chars + 3) & ~3


def slot(name):
    import narcio
    v = len(narcio.load(b2font.VANILLA, 2)[int(name[:4])])
    return (v + 64 + v // 16 + 3) & ~3


SHARED = {
    'system/0478_game_start.txt': {'0': 'HOENN POKÉDEX', '10': 'HOENN'},
    'system/0479.txt': {'17': 'Hoenn Pokédex: Search Mode'},
    'system/0362.txt': {'53': 'HOENN', '57': "When all the Pokémon in that Habitat\\nhave been encountered,\\nyou'll receive "
                                               "a stamp.\\nExplore all of the Hoenn region!{be01}"},
}


def main():
    install = '--install' in sys.argv
    sap, sap2, prob_s = build('SAPPHIRE')
    rub, rub2, prob_r = build('RUBY')
    for name, p in (('Sapphire', prob_s), ('Ruby', prob_r)):
        print(f'{name}: {len(p)} problems'); [print('  ', x) for x in p]
    ruby_diff = {f: {k: v for k, v in d.items() if sap[f].get(k) != v} for f, d in rub.items()}
    ruby_diff = {f: d for f, d in ruby_diff.items() if d}
    print('Ruby lines that differ:', {f: len(d) for f, d in ruby_diff.items()},
          'page 2 differs on', sum(a != b for a, b in zip(sap2, rub2)), 'lines')
    # Sapphire's measures against Black 2's (Gen 5 data)
    for f in ('0451.txt', '0471.txt', '0464.txt'):
        b2 = b2_lines(f)
        diff = [(int(k), b2[int(k)], v) for k, v in sap['system/' + f].items() if b2[int(k)] != v and int(k) <= N_SPECIES]
        print(f'{f}: {len(diff)} of {N_SPECIES} differ from Black 2', diff[:8])
    # fixed slots
    for ver, lines, p2 in (('Sapphire', sap, sap2), ('Ruby', {f: {**sap[f], **ruby_diff.get(f, {})} for f in sap}, rub2)):
        for name in ('0442.txt', '0464.txt', '0451.txt', '0471.txt'):
            b2 = b2_lines(name)
            body = b2[:-1] if b2[-1] == '' else b2
            pad = body[-1] if body[-1].startswith('\\pad{') else None
            if pad: body = body[:-1]
            for k, v in lines['system/' + name].items(): body[int(k)] = v
            print(f'{ver} {name}: {packed_size(body):,} B, slot {slot(name):,} B')
            assert packed_size(body) <= slot(name), name
        print(f'{ver} 0443 (page 2): {packed_size(p2):,} B, slot {slot("0443"):,} B')
        assert packed_size(p2) <= slot('0443')
    if prob_s or prob_r: raise SystemExit('fix the problems first')
    if not install: return
    doc = ('gen_dex_text.py (hoenn_pokedex): Sapphire\'s Pokédex text (page 1, categories, heights, weights) for '
           'species 1-386 + form lines; the Hoenn header / search / Habitat list lines. Page 2: system/0443_dex_page2.txt')
    # categories, heights and weights: only lines that differ from Black 2's (none: Gen 5 kept Gen 3's data, checked)
    same = {f: {k: v for k, v in d.items() if f == 'system/0442.txt' or b2_lines(f.split('/')[1])[int(k)] != v}
            for f, d in sap.items()}
    out = {'_doc': doc, **SHARED, **{f: d for f, d in same.items() if d}}
    json.dump(out, open(os.path.join(TEXT, 'overrides_hoenn_dex.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    rdoc = 'gen_dex_text.py (hoenn_pokedex): Ruby\'s Pokédex entries where they differ from Sapphire\'s (page 1)'
    json.dump({'_doc': rdoc, **ruby_diff}, open(os.path.join(TEXT, 'ruby', 'overrides_hoenn_dex.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    for d, p2 in ((os.path.join(TEXT, 'system'), sap2), (os.path.join(TEXT, 'system', 'ruby'), rub2)):
        open(os.path.join(d, '0443_dex_page2.txt'), 'w', encoding='utf-8').write('\n'.join(p2) + '\n')
    print('installed')


# ---- Emerald (HOENN_VERSION=emerald python3 gen_dex_text.py [--install]; emerald_data 2026-10-12, EMERALD-1) ----
# pokeemerald src/data/pokemon/pokedex_text.h + pokedex_entries.h: one entry text per species (Emerald's Pokédex shows
# one page of up to 4 lines, in a wider window than Ruby/Sapphire's 3-line pages), category, height, weight.
# Black 2's window holds 3 lines of 222 px (font 0, MAX_W); an Emerald entry is 4 Gen 3 lines (up to 6 at 222 px), so it
# is wrapped again and split in two pages like Sapphire's (pages_emerald: between two sentences where possible, the most
# even split): page 1 in system 0442, page 2 in 0443 (Sapphire's A-button page; hoenn_pokedex flips on every owned Hoenn
# species). Three full lines on page 1 for every species would not fit 0442's fixed slot (167 KB > 159 KB: HOENN_TEXT_SLOTS).
# Writes src/text/emerald/overrides_hoenn_dex.json (Emerald's lines where they differ from Sapphire's shared file:
# entry page 1, and category / height / weight where Emerald's differ) and src/text/system/emerald/0443_dex_page2.txt.
EM = os.path.join(ROOT, 'external', 'pokeemerald', 'src', 'data', 'pokemon')


def entries_emerald():
    """[(category, height dm, weight hg, [Gen 3 lines])] by national number 0-386, pokeemerald's."""
    texts = {m.group(1): re.findall(r'"((?:[^"\\]|\\.)*)"', m.group(2))
             for m in re.finditer(r'const u8 (g\w+PokedexText)\[\] = _\((.*?)\);', open(os.path.join(EM, 'pokedex_text.h'), encoding='utf-8').read(), re.S)}
    src = open(os.path.join(EM, 'pokedex_entries.h'), encoding='utf-8').read()
    out = [(c, int(h), int(w), [l[:-2] if l.endswith('\\n') else l for l in texts[d]]) for c, h, w, d in re.findall(
        r'\.categoryName = _\("([^"]*)"\),\s*\.height = (\d+),\s*\.weight = (\d+),\s*\.description = (\w+),', src)]
    assert len(out) == N_SPECIES + 1, len(out)
    return out


def wrap(font, words):
    lines, cur = [], ''
    for w in words:
        t = (cur + ' ' + w) if cur else w
        if cur and font.width(t) > MAX_W: lines.append(cur); cur = w
        else: cur = t
    return lines + ([cur] if cur else [])


ABBR = {'Mr.', 'Mt.', 'Dr.', 'St.', 'Ms.', 'Mrs.'}


def pages_emerald(font, gen3_lines):
    """Emerald's one-page text (4 Gen 3 lines, longer than Black 2's 3-line window) as two pages of at most 3 lines of
    MAX_W px: split between two sentences, the split that balances the pages best (by width); each page wrapped at word
    ends. A text whose sentences cannot be split so (one long sentence) is wrapped whole and cut in the middle line."""
    ls = [text(l) for l in gen3_lines]
    full = ''
    for l in ls: full = full + l if full.endswith('-') else (full + ' ' + l if full else l)
    words = full.split(' ')
    ends = [i for i, w in enumerate(words[:-1], 1) if w[-1:] in '.!?' and w not in ABBR]
    best = None
    for i in ends:
        p1, p2 = wrap(font, words[:i]), wrap(font, words[i:])
        if len(p1) <= MAX_LINES and len(p2) <= MAX_LINES:
            d = abs(font.width(' '.join(words[:i])) - font.width(' '.join(words[i:])))
            if best is None or d < best[0]: best = (d, p1, p2)
    if best: return best[1], best[2], 'sentences'
    whole = wrap(font, words)
    if len(whole) <= MAX_LINES: return whole, [], 'one page'
    k = (len(whole) + 1) // 2
    return whole[:k], whole[k:], 'lines'


def build_emerald():
    font = b2font.load(0)
    problems, how = [], {}
    lines = {'system/0442.txt': {}, 'system/0464.txt': {}, 'system/0451.txt': {}, 'system/0471.txt': {}}
    page2 = [''] * 733
    for n, (c, h, w, gl) in enumerate(entries_emerald()):
        if n == 0: continue
        l1, l2, how[n] = pages_emerald(font, gl)
        if len(l1) > MAX_LINES or len(l2) > MAX_LINES: problems.append(f'#{n}: pages of {len(l1)} + {len(l2)} lines')
        p1, p2 = '\\n'.join(l1), '\\n'.join(l2)
        check_page(font, n, 1, p1, problems)
        if p2: check_page(font, n, 2, p2, problems)
        for i in [n, *FORMS.get(n, ())]:
            lines['system/0442.txt'][str(i)] = p1
            lines['system/0451.txt'][str(i)] = height(h)
            lines['system/0471.txt'][str(i)] = weight(w)
            page2[i] = p2
        lines['system/0464.txt'][str(n)] = category(c)
    return lines, page2, problems, how


def main_emerald():
    install = '--install' in sys.argv
    sap, sap2, _ = build('SAPPHIRE')
    em, em2, prob, how = build_emerald()
    import collections
    print(f'Emerald: {len(prob)} problems'); [print('  ', x) for x in prob]
    print(f'  {N_SPECIES} entries, each one Emerald page of 4 Gen 3 lines: none fits Black 2\'s 3-line window, so each is '
          f'wrapped to {MAX_W} px and split in two pages: {dict(collections.Counter(how.values()))} '
          f'(sentences: split between two sentences; lines: one long sentence cut at a line end; one page: fits in 3 lines)')
    diff = {f: {k: v for k, v in d.items() if sap[f].get(k) != v} for f, d in em.items()}
    print('  Emerald lines that differ from Sapphire\'s:', {f: len(d) for f, d in diff.items()})
    for name in ('0442.txt', '0464.txt', '0451.txt', '0471.txt'):
        b2 = b2_lines(name)
        body = b2[:-1] if b2[-1] == '' else b2
        if body[-1].startswith('\\pad{'): body = body[:-1]
        for k, v in {**sap['system/' + name], **diff['system/' + name]}.items(): body[int(k)] = v
        print(f'  Emerald {name}: {packed_size(body):,} B, slot {slot(name):,} B')
        assert packed_size(body) <= slot(name), name
    print(f'  Emerald 0443 (page 2): {packed_size(em2):,} B, slot {slot("0443"):,} B')
    assert packed_size(em2) <= slot('0443')
    if prob: raise SystemExit('fix the problems first')
    if not install: return
    doc = ('gen_dex_text.py (hoenn_pokedex), HOENN_VERSION=emerald: Emerald\'s Pokédex entries (pokeemerald pokedex_text.h, '
           'page 1 = the first 3 lines in Black 2\'s window) where they differ from Sapphire\'s, and Emerald\'s categories, '
           'heights and weights where they differ. Page 2: system/emerald/0443_dex_page2.txt')
    out = {'_doc': doc, **{f: d for f, d in diff.items() if d}}
    os.makedirs(os.path.join(TEXT, 'emerald'), exist_ok=True)
    os.makedirs(os.path.join(TEXT, 'system', 'emerald'), exist_ok=True)
    json.dump(out, open(os.path.join(TEXT, 'emerald', 'overrides_hoenn_dex.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    open(os.path.join(TEXT, 'system', 'emerald', '0443_dex_page2.txt'), 'w', encoding='utf-8').write('\n'.join(em2) + '\n')
    print('installed')


if __name__ == '__main__':
    import version
    main_emerald() if version.is_emerald() else main()
