"""Sapphire (pokeruby .string) text -> Black 2 text-file lines, word for word (decision 2026-10-06: Sapphire dialogue
verbatim, Gen 5 capitalisation).

- Line breaks: Gen 3 \\n -> \\n, \\l (scroll) -> {be00}\\n, \\p (new page) -> {be01}\\n (Black 2's own texts use these
  forms, notes/OPENING.md), $ (end) removed.
- {PLAYER} -> {0100:0} (word buffer 0: the script runs WordSetPlayerName 0 first); arrows -> ← ↑ → ↓ (in Black 2's
  font). Other {CODES} are reported in `unknown` and dropped, so a script that needs them must be written by hand.
- Sapphire's signs write "ROUTE 1O4" with a letter O, which its font draws like a zero: written 104.
- Capitalisation: Gen 3 writes names in capitals (POKéMON, PROF. BIRCH, OLDALE TOWN, POTION); Gen 5 writes them in
  title case (Pokémon, Prof. Birch, Oldale Town, Potion). A run of 2+ capital letters becomes title case, except the
  abbreviations Gen 5 keeps (HP, PP, TM, HM, PC, TV, OK, S.S.). Fixed spellings in SPECIAL win.
- Apostrophes and quotes become Black 2's typographic ones (’ “ ”).
"""
import os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'b2tools'))
import version  # noqa: E402  (HOENN_VERSION: the 7 version placeholders, b2tools/version.py)

KEEP = {'HP', 'PP', 'TM', 'HM', 'PC', 'TV', 'OK', 'S.S.', 'SS', 'HQ', 'KO', 'CD', 'DJ', 'TMS', 'HMS'}
SPECIAL = {
    'POKéMON': 'Pokémon', 'POKéDEX': 'Pokédex', 'POKéNAV': 'PokéNav', 'POKéBLOCK': 'Pokéblock', 'POKéBLOCKS': 'Pokéblocks',
    'POKé': 'Poké', 'POKéMART': 'Poké Mart', 'TMS': 'TMs', 'HMS': 'HMs', 'TMs': 'TMs', 'HMs': 'HMs',
    'PC’S': 'PC’s', 'MT.': 'Mt.', 'MR.': 'Mr.', 'MRS.': 'Mrs.', 'MS.': 'Ms.', 'DR.': 'Dr.', 'PROF.': 'Prof.',
    'S.S.': 'S.S.', 'TV': 'TV', 'EXP.': 'Exp.', 'EXP': 'Exp.',
}
CODE = re.compile(r'\{([A-Za-z_0-9 ]+)\}')
ARROWS = {'UP_ARROW': '↑', 'DOWN_ARROW': '↓', 'LEFT_ARROW': '←', 'RIGHT_ARROW': '→',      # pokeruby charmap.txt 79-7C;
          '0x79': '↑', '0x7A': '↓', '0x7B': '←', '0x7C': '→'}                              # Black 2's font has U+2190-2193
CAPS = re.compile(r"[A-Zé][A-Zé.’'\-]*[A-Zé.]|[A-Z]")

def _title(word):
    if word in SPECIAL: return SPECIAL[word]
    core = word.rstrip('.')
    if core in KEEP or word in KEEP: return word
    if len(re.sub(r'[^A-Zé]', '', word)) < 2: return word
    parts = re.split(r'([\-’])', word)
    out = []
    for p in parts:
        if p in ('-', '’') or not p: out.append(p); continue
        if p in SPECIAL: out.append(SPECIAL[p]); continue
        out.append(p[0] + p[1:].lower())
    s = ''.join(out)
    return re.sub(r'’S\b', '’s', s.replace('’S', '’s'))

# expand=True (story scripts and trainers, converter/gen_trainers.py; notes/STORY_PORTING.md): Sapphire's version
# placeholders as Sapphire shows them (pokeruby src/string_util.c GetExpandedPlaceholder, strings.c: {KUN} is ""
# in English), {POKEBLOCK} as the word, and the string variables as Black 2 word buffers: {STR_VAR_n} -> {0100:n}
# (the script fills buffer n with WordSet*), {RIVAL} -> {0100:4} (the script puts May/Brendan in buffer 4).
# The 7 version placeholders come from b2tools/version.py (Sapphire: VERSION SAPPHIRE, EVIL_TEAM AQUA, GOOD_TEAM MAGMA,
# EVIL_LEADER ARCHIE, GOOD_LEADER MAXIE, EVIL_LEGENDARY KYOGRE, GOOD_LEGENDARY GROUDON; Ruby the mirror).
def expand_table(version_=None):
    """The expansion table of the build's version, or of version_ ('sapphire'/'ruby': converter/gen_ruby_text.py makes
    Ruby's lines from the same sources as Sapphire's)."""
    return {**(version.expand_for(version_) if version_ else version.EXPAND_VERSION), 'KUN': '',
            'POKEBLOCK': 'POKéBLOCK', 'STR_VAR_1': '\x00\x02\x01', 'STR_VAR_2': '\x00\x02\x02',
            'STR_VAR_3': '\x00\x02\x03', 'RIVAL': '\x00\x02\x04'}

EXPAND = expand_table()

def convert(s, expand=False, version_=None):
    """Returns (black2_line, unknown_codes). version_: expand the version placeholders for that version instead of
    the build's (HOENN_VERSION)."""
    unknown = []
    table = EXPAND if version_ is None else expand_table(version_)
    def code(m):
        c = m.group(1)
        if c == 'PLAYER': return '\x00\x01\x00'
        if c in ARROWS: return ARROWS[c]
        if expand and c in table: return table[c]
        unknown.append(c); return ''
    s = s.replace('$', '')
    s = s.replace('¥', '$')                       # Sapphire's money sign -> Black 2's ($ draws the Pokédollar)
    s = CODE.sub(code, s)
    s = s.replace("'", '’')
    q = [0]
    def quote(m):
        q[0] ^= 1
        return '“' if q[0] else '”'
    s = re.sub(r'\\"|"', quote, s)
    s = re.sub(r'POKé ?BALL(S?)', lambda m: 'Poké Ball' + m.group(1).lower(), s)
    s = re.sub(r'POKéMON CENTER', 'Pokémon Center', s)
    s = re.sub(r'POKé MART', 'Poké Mart', s)
    s = re.sub(r'(?<=\d)O(?=\d)|(?<=[\s])1O(?=\d)', lambda m: m.group(0).replace('O', '0'), s)   # "ROUTE 1O4": Sapphire's
    s = CAPS.sub(lambda m: _title(m.group(0)), s)                         # letter O looks like 0 in its font
    s = s.replace('\\p', '{be01}\\n').replace('\\l', '{be00}\\n')
    s = s.replace('\x00\x01\x00', '{0100:0}')
    s = re.sub('\x00\x02(.)', lambda m: '{0100:%d}' % ord(m.group(1)), s)
    return s, unknown

if __name__ == '__main__':
    tests = ["Hi! I'm PROF. BIRCH's assistant.\\pPOKéMON are in the tall grass\\nof ROUTE 101!$",
             "{PLAYER}'s HOUSE$", "OLDALE TOWN\\n\"Where things start off scarce.\"$",
             "You can buy POKé BALLS at the POKé MART. HP and PP restore at the POKéMON CENTER.$",
             "The WATER-type MUDKIP uses HM01 CUT? No, that's TM28!$"]
    for t in tests: print(convert(t))
