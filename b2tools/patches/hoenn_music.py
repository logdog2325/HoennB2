"""Hoenn's soundtrack on Black 2's instruments, chosen in the intro: Birch's third question, Hoenn or Unova music
(notes/MUSIC.md; data/hoenn_music.json; code hoenn_music.c). Both soundtracks stay in the game.

apply (files): every song of data/hoenn_music.json "slots" is converted from the GBA ROM (b2tools/m4a_to_sseq.py)
and installed into its slot of swan_sound_data.sdat in place (b2tools/music_slots.py chose sequence entries and file
bytes the game never plays under either option: Unova-only cutscenes, the Musical, Pokestar Studios, Unova places'
songs, Unova-only sound effects, the instrument library's own samples). The slot's sequence, bank and wave archive
entries keep their places in INFO and the FAT: only their values change, and the new files go into the free bytes, so
the archive keeps its size and every other file its offset (the ROM layout is unchanged; savestates keep working, with
the new songs after a cold boot; Emerald alone grows its archive once by data "archive_reserve": archive_reserve()).
Then each Hoenn zone's header gets its Hoenn song in its third BGM field (bgm2,
autumn: patches/hoenn_season keeps Hoenn in summer, bgm1, which keeps the Black 2 song).

apply_code (code): hoenn_music.c, linked into ITCM after the code already there (hoenn_world, roamers, fairy, fairy_ui:
the arena literal protocol), with the tables (Unova -> Hoenn redirects, the trainer classes' encounter, battle and
victory songs, legendary species) and the hooks:
  arm9 0x020300bc  GetRegularZoneBGMID's literal DecideZoneHeaderBGMID -> Music_ZoneBGM
  arm9 0x02005d9c  GFL_SndBGMPlayCore `adds r4, r0, #0; adds r5, r1, #0` -> bl Music_PlayCoreShim
  arm9 0x02030794  GetTrainerClassEyeBGMID -> jump to Music_EyeBGM
  ov012 0x02168558, 0x02168aa2  bl EventBattleCall_DecideEnvWild -> bl Music_DecideEnvWild
  ov012 0x02168804  bl EventBattleCall_DecideEnvTrainer -> bl Music_DecideEnvTrainer
  arm9 0x020300b0  GetRegularZoneBGMID's entry -> `ldr r3, [pc, #8]; bx r3` (its literal: Music_ZoneBGM gets the game
                   data too, for Sapphire's zone rules: the Kyogre / Groudon weather song, the occupied Weather Institute)
  arm9 0x02006428  func_02006424 (the evolution / egg scenes' and the field's threaded BGM load) `adds r5, r0, #0;
                   adds r4, r1, #0` -> bl Music_LoadShim (the same redirect as GFL_SndBGMPlayCore)
  arm9 0x02005e14  BGM2 play 0x02005e10 (the credits, the Game Freak logo) `adds r4, r0, #0; bl ResetBGMChange` ->
                   `bl Music_Bgm2Redirect; adds r4, r0, #0`
  arm9 0x02005e0a  func_02005e08 (faded BGM change) `bl RequestBGMChange` -> bl Music_RequestChange
  arm9 0x02006fc8, 0x02007054, 0x020070c0, 0x02007090, 0x020070a4  GFL_SndStreamInit / Play / FadeStop / Stop / IsPlaying
                   -> jump to Music_Stream* (the title's stream: Sapphire's title song with the Hoenn option)
  ov036 0x021a6e2a, 0x021a6e38  s009B_BGMIsPlaying's bl VM_Read16 / bl GFL_SndBGMIsPlaying -> Music_ScrRead16 /
                   Music_ScrBGMIsPlaying (BGMIsPlaying MUSIC_QUERY answers the option: src/include/hoenn_music.inc)
Every site is checked against Black 2's bytes. check_waits refuses a redirect from a sequence that ends (jingles, the
evolution intro: Black 2 waits for them) to a song that loops (v16's freeze at the starter). HOENN_MUSIC=off skips the patch (build_rom adds it when HOENN_MUSIC is
set; the release list names it). Test switch: HOENN_TEST_MUSIC=hoenn|unova forces the option (the question then
changes nothing).
"""
import glob, json, os, re, struct, sys, tempfile, subprocess, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
B2T = os.path.dirname(HERE)
ROOT = os.path.dirname(B2T)
sys.path.insert(0, B2T)
SDAT_NAME = 'swan_sound_data.sdat'
LLVM = '/opt/homebrew/opt/llvm/bin'
ITCM_BASE, ARENA_ITCM_LIT, ARM9 = 0x01FF8000, 0x0207B400, 0x02004000
OV012, OV036 = 0x021503C0, 0x0217F600
SCRIPT_INC = os.path.join(ROOT, 'src', 'include', 'hoenn_music.inc')
VANILLA_CODE = os.path.join(ROOT, 'external', 'pokebw2', 'build', 'b2_us', 'build')
VANILLA_FILES = os.path.join(ROOT, 'external', 'pokebw2', 'build', 'b2_us', 'files')
PRUBY = os.path.join(ROOT, 'external', 'pokeruby')


def enabled():
    return os.environ.get('HOENN_MUSIC', '').lower() != 'off'


# ---- data --------------------------------------------------------------------------------------------------------
def _mapping():
    """data/hoenn_music.json; in a Ruby or Emerald build deep-merged with data/<version>/hoenn_music.json when there is
    one (version.load_json: only the keys that differ). Emerald's (emerald_art): its 5 new story songs and their slots,
    the songs taken from Emerald's dump (songs.<song>.rom), Rayquaza's and Mew's battle songs, the crisis song
    (zone_rules.crisis_song.emerald), the Unova stand-ins of the 2 songs that end, the church organ, the part gains.
    Sapphire reads the base file only (as before); Ruby has no overlay."""
    import m4a_to_sseq as conv, version
    return version.load_json(conv.MAPPING)


def seq_ids(sdat, mp):
    """song -> its slot's sequence id (data/hoenn_music.json "slots")."""
    return {song: sdat.index('seq', slot) for song, slot in mp['slots'].items()}


def map_song(m, mp=None):
    """A map's song: pokeruby data/maps/<map>/map.json; Emerald-only maps (event islands, Altering Cave) from
    pokeemerald's through data "emerald_music". None = silence (MUS_DUMMY), 'missing' = no such map."""
    p = os.path.join(PRUBY, 'data', 'maps', m, 'map.json')
    if not os.path.exists(p):
        q = os.path.join(ROOT, 'external', 'pokeemerald', 'data', 'maps', m, 'map.json')
        if not os.path.exists(q): return 'missing'
        mus = json.load(open(q)).get('music', '')
        em = (mp or {}).get('emerald_music', {})
        return em.get(m, em.get(mus, mus.lower()))
    mus = json.load(open(p)).get('music', '').lower()
    if mus == 'mus_route_118': return 'mus_route119'     # pokeruby GetCurrLocationDefaultMusic: x >= 24 (most of it)
    if mus == 'mus_dummy': return None
    return mus


def emerald_map_song(folder, mp=None):
    """An Emerald-only room's song: pokeemerald data/maps/<folder>/map.json (its own folder name: Emerald's Magma Hideout
    1F is "MagmaHideout_1F", whose name pokeruby's map has too), through data "emerald_music" (emerald_caves 2026-10-12)."""
    q = os.path.join(ROOT, 'external', 'pokeemerald', 'data', 'maps', folder, 'map.json')
    if not os.path.exists(q): return 'missing'
    mus = json.load(open(q)).get('music', '')
    em = (mp or {}).get('emerald_music', {})
    return em.get(folder, em.get(mus, mus.lower()))


def zone_songs(headers, mp):
    """{zone id: song or None (silence)} for every zone of the Hoenn game."""
    import version
    spec = importlib.util.spec_from_file_location('fixed_weather_music', os.path.join(HERE, 'fixed_weather.py'))
    fw = importlib.util.module_from_spec(spec); spec.loader.exec_module(fw)
    W = os.environ.get('HOENN_WORLD_DIR') or os.path.join(ROOT, 'work', 'world')
    world = json.load(open(os.path.join(W, 'world.json')))
    out, src = {}, {}
    for m, v in json.load(open(os.path.join(ROOT, 'data', 'hoenn_zones.json')))['maps'].items():
        out.setdefault(v['zone'], map_song(m, mp)); src.setdefault(v['zone'], m)
    rooms = json.load(open(os.path.join(ROOT, 'data', 'hoenn_interiors.json')))['rooms']
    for m, v in rooms.items():
        if 'zone' not in v or not version.room_in_version(m): continue
        out[v['zone']] = map_song(m, mp); src[v['zone']] = m
    if version.is_emerald():       # (emerald_caves 2026-10-12) Emerald's own rooms (data/emerald/hoenn_interiors.json, a
        em = os.path.join(ROOT, 'data', 'emerald', 'hoenn_interiors.json')    # zone claimed): their pokeemerald map's song
        for m, v in (json.load(open(em))['rooms'].items() if os.path.exists(em) else []):
            if 'zone' in v and v.get('emerald'):
                out[v['zone']] = emerald_map_song(v['emerald'], mp); src[v['zone']] = m
    for f in sorted(glob.glob(os.path.join(ROOT, 'data', 'cave_layouts', '*.json'))):
        c = json.load(open(f))
        m = c.get('map') or os.path.splitext(os.path.basename(f))[0]
        for z in [c.get('header_zone')] + [x.get('zone') for x in c.get('variants', [])]:
            if z is not None and z not in out: out[z] = map_song(m, mp); src[z] = m
    for z, v in world['zones'].items():
        for m in v.get('maps', []):
            if int(z) not in out: out[int(z)] = map_song(m, mp); src[int(z)] = m
    for name, p, s, matrix, rects in fw.parts(world):
        out[p['zone']] = mp.get('part_songs', {}).get(name, out.get(s)); src[p['zone']] = name
    for z, song in mp.get('zone_songs', {}).items():
        out[int(z)] = song; src[int(z)] = 'zone_songs'
    # zones made by Hoenn patches that none of the above names: their parent's song
    van = _vanilla_headers()
    for z, h in enumerate(headers):
        if z in out or h == van[z]: continue
        if h['parent'] in out and h['parent'] != z: out[z] = out[h['parent']]; src[z] = f'parent {h["parent"]}'
    out = {z: s for z, s in out.items() if s != 'missing'}
    return out, src


def _vanilla_headers():
    import narcio, zoneheaders
    return zoneheaders.parse(narcio.load(VANILLA_FILES, 12)[0])


TRAINER_MUSIC = {'MALE': 'mus_encounter_male', 'FEMALE': 'mus_encounter_female', 'GIRL': 'mus_encounter_girl',
                 'SUSPICIOUS': 'mus_encounter_suspicious', 'INTENSE': 'mus_encounter_intense', 'COOL': 'mus_encounter_cool',
                 'AQUA': 'mus_encounter_aqua', 'MAGMA': 'mus_encounter_magma', 'SWIMMER': 'mus_encounter_swimmer',
                 'TWINS': 'mus_encounter_twins', 'ELITE_FOUR': 'mus_encounter_elite_four', 'HIKER': 'mus_encounter_hiker',
                 'INTERVIEWER': 'mus_encounter_interviewer', 'RICH': 'mus_encounter_rich'}


def class_songs():
    """{Black 2 class: dict(eye, battle, victory)} from Sapphire's trainers (pokeruby src/data/trainers_en.h: class,
    encounter music, picture) through data/hoenn_trainer_classes.json "review" (picture -> Black 2 class), with Ruby
    and Sapphire's rules: pokeruby battle_setup.c PlayTrainerEncounterMusic and pokemon_3.c GetMUS_ForBattle."""
    import version
    from collections import Counter
    review = version.load_json(os.path.join(ROOT, 'data', 'hoenn_trainer_classes.json'))['review']
    pic_class = {r['sapphire_pic']: r['b2_class'] for r in review}
    # Emerald (data/emerald/hoenn_trainer_classes.json): a picture pokeruby lacks names the pokeruby picture whose songs its
    # class takes ("music_pic": Juan a leader's, Champion Wallace the Champion's, Steven the rival's; gen_trainers.py)
    also = {r['music_pic']: r['b2_class'] for r in review if 'music_pic' in r}
    src = open(os.path.join(PRUBY, 'src', 'data', 'trainers_en.h'), encoding='utf-8').read()
    eye, battle, victory = {}, {}, {}
    for blk in re.findall(r'\{(.*?)\n    \}', src, re.S):
        c = re.search(r'\.trainerClass = TRAINER_CLASS_(\w+)', blk)
        mu = re.search(r'\.encounterMusic_gender = (?:F_TRAINER_FEMALE \| )?TRAINER_ENCOUNTER_MUSIC_(\w+)', blk)
        pic = re.search(r'\.trainerPic = TRAINER_PIC_(\w+)', blk)
        name = re.search(r'\.trainerName = _\("([^"]*)"\)', blk)
        if not (c and pic) or (pic.group(1) not in pic_class and pic.group(1) not in also): continue
        b2s = [pic_class[pic.group(1)]] if pic.group(1) in pic_class else []
        if pic.group(1) in also: b2s.append(also[pic.group(1)])
        cls = c.group(1)
        if cls in ('AQUA_LEADER', 'MAGMA_LEADER'): b, v = 'mus_vs_aqua_magma_leader', 'mus_victory_aqua_magma'
        elif cls in ('TEAM_AQUA', 'AQUA_ADMIN', 'TEAM_MAGMA', 'MAGMA_ADMIN'): b, v = 'mus_vs_aqua_magma', 'mus_victory_aqua_magma'
        elif cls == 'LEADER': b, v = 'mus_vs_gym_leader', 'mus_victory_gym_leader'
        elif cls == 'CHAMPION': b, v = 'mus_vs_champion', 'mus_victory_league'
        elif cls == 'ELITE_FOUR': b, v = 'mus_vs_elite_four', 'mus_victory_league'
        elif cls == 'POKEMON_TRAINER_3' and name and name.group(1) != 'WALLY': b, v = 'mus_vs_rival', 'mus_victory_trainer'
        else: b, v = 'mus_vs_trainer', 'mus_victory_trainer'
        for b2 in b2s:
            if mu: eye.setdefault(b2, Counter())[TRAINER_MUSIC.get(mu.group(1), 'mus_encounter_suspicious')] += 1
            battle.setdefault(b2, Counter())[b] += 1
            victory.setdefault(b2, Counter())[v] += 1
    out = {}
    for b2 in set(eye) | set(battle):
        out[b2] = dict(eye=eye[b2].most_common(1)[0][0] if b2 in eye else None,
                       battle=battle[b2].most_common(1)[0][0] if b2 in battle else None,
                       victory=victory[b2].most_common(1)[0][0] if b2 in victory else None)
    return out


# ---- the sound archive --------------------------------------------------------------------------------------------
def free_chunks(s, files):
    """The free byte ranges: the pool files' extents, merged where they touch (32-byte aligned)."""
    ext = sorted((s.fat[f][0], s.fat[f][0] + s.fat[f][1]) for f in files if s.fat[f][1])
    chunks = []
    for a, b in ext:
        b = (b + 31) & ~31
        if chunks and a <= chunks[-1][1]: chunks[-1][1] = max(chunks[-1][1], b)
        else: chunks.append([a, b])
    return [(a, b - a) for a, b in chunks]


def archive_reserve(mp):
    """Emerald only (frontier_core_music, 2026-10-12): bytes added after the sound archive's last file, data
    "archive_reserve" in data/emerald/hoenn_music.json. Emerald's songs (112 + the Battle Frontier's 13) need more than
    the pool's free bytes, so its archive grows by a fixed amount (one ROM layout change: every later NitroFS file moves,
    Emerald's savestates are remade; fixed so that later songs fit without another). The new files go there through
    the pool slots' own FAT entries, so INFO and the FAT keep their sizes (no sound-heap cost); the header's archive and
    FILE block sizes grow with it. Sapphire and Ruby: 0 (their archive keeps its size, byte for byte)."""
    import version
    if not version.is_emerald(): return 0
    n = int(mp.get('archive_reserve', 0))
    assert n % 32 == 0 and n >= 0, f'archive_reserve {n}: a multiple of 32'
    return n


def install_all(data, songs, mp):
    """Put every converted song into its slot. songs: {song: (sseq, sbnk, swar, volume)}. Returns the new archive."""
    from sdat import SDAT
    import music_slots
    s = SDAT(data)
    slots, files = music_slots.pool(s)
    by_name = {x[1]: x for x in slots}
    chunks = [[a, n, a] for a, n in free_chunks(s, files)]       # [start, size, cursor]
    out = bytearray(data)
    for a, n, _ in chunks: out[a:a + n] = bytes(n)
    grow = archive_reserve(mp)                # Emerald only: room after the archive's last file (the pool is full)
    if grow:
        chunks.append([len(data), grow, len(data)])
        out += bytes(grow)
        struct.pack_into('<I', out, 8, len(out))                                   # the archive's size,
        struct.pack_into('<I', out, 0x2C, s.file_size + grow)                       # the FILE block's in the header
        struct.pack_into('<I', out, s.file_off + 4, s.file_size + grow)             # and in the block
    blobs = []
    for song, (q, b, w, vol) in songs.items():
        i, name, bank, wa = by_name[mp['slots'][song]]
        e = s.info['seq'][i]; bk = s.info['bank'][bank]
        f_seq, f_bank, f_wave = e['file'], bk['file'], s.info['wavearc'][wa]['file']
        blobs += [(len(w), f_wave, w), (len(b), f_bank, b), (len(q), f_seq, q)]
        struct.pack_into('<IHBBBBH', out, e['_at'], f_seq, bank, vol, 30, 64, 0, 0)
        struct.pack_into('<I4H', out, bk['_at'], f_bank, wa, 0xFFFF, 0xFFFF, 0xFFFF)
        struct.pack_into('<I', out, s.info['wavearc'][wa]['_at'], f_wave)
    placed = {}
    for size, f, blob in sorted(blobs, key=lambda x: -x[0]):      # first fit, largest first
        c = next((c for c in chunks if c[0] + c[1] - c[2] >= size), None)
        if c is None:
            raise SystemExit(f'hoenn_music: {size} B for file {f} do not fit the free bytes '
                             f'(largest gap {max(c[0] + c[1] - c[2] for c in chunks)})')
        out[c[2]:c[2] + size] = blob
        struct.pack_into('<II', out, s.fat_off + 12 + 16 * f, c[2], size)
        placed[f] = c[2]
        c[2] = (c[2] + size + 31) & ~31
    assert len(out) == len(data) + grow
    used = sum(x[0] for x in blobs)
    return bytes(out), used, sum(n for _, n, _ in chunks)


def convert_all(mp):
    import version
    if version.is_emerald():          # each song from the dump its data names, the overlay's gains (b2tools/m4a_emerald.py)
        import m4a_emerald
        songs, objs = m4a_emerald.convert_all(mp)
        return songs, sum(o.size for o in objs.values())
    import m4a, m4a_to_sseq as conv
    from sdat import SDAT, DEFAULT
    rom, sd, lv = m4a.GbaRom(), SDAT(open(DEFAULT, 'rb').read()), conv.load_levels()
    songs, report = {}, []
    for song in mp['slots']:
        sg = conv.Song(song, rom=rom, mapping=mp, sdat=sd, levels=lv)
        q, b, w = sg.convert()
        songs[song] = (q, b, w, sg.info_volume)
        report.append(sg.size)
    return songs, sum(report)


def _loops(sseq_bytes):
    import sseq
    return any(t['loop_tick'] is not None for t in sseq.decode(sseq_bytes).values())


def check_waits(mp, songs):
    """Refuse a redirect (either version, and the Unova option's reverse table) that sends a sequence that ends to a
    song that loops. Black 2 waits for its jingles and short songs to end (field scripts' MEWait, the evolution demo's
    SEQ_BGM_SHINKA, the battle's capture jingle: GFL_SndBGMIsPlaying), so a looping stand-in never ends and the game
    waits forever (v16: SEQ_ME_POKEGET -> mus_caught froze the lab at "received the Mudkip!").
    songs: {song: (sseq, ...)} as converted. Returns the number of pairs checked."""
    from sdat import SDAT, DEFAULT
    sd = SDAT(open(DEFAULT, 'rb').read())
    def vloops(name): return _loops(sd.seq(sd.index('seq', name)))
    hoenn = {s: _loops(v[0]) for s, v in songs.items()}
    pairs = list(mp['redirect'].items()) + list(mp.get('redirect_ruby', {}).items())
    if mp.get('after_catch'): pairs.append(('SEQ_BGM_WIN1', mp['after_catch']))    # Music_Redirect after a capture
    free = set(mp.get('not_waited', []))      # ended by the game itself, never waited for (the credits: frame-timed,
    bad = [(a, b) for a, b in pairs if not vloops(a) and hoenn[b] and a not in free]   # ov012 fades them out)
    bad += [(a, b) for a, b in mp['reverse'].items() if not hoenn[a] and vloops(b)]
    if bad:
        raise SystemExit('hoenn_music: these sequences end (the game waits for them) but their stand-in loops: '
                         + ', '.join(f'{a} -> {b}' for a, b in bad)
                         + ' (pick a song that ends, e.g. Sapphire\'s own jingle, or give it "once": true)')
    return len(pairs) + len(mp['reverse'])


def check_script_slots(mp):
    """src/include/hoenn_music.inc names the slots of the songs scripts play (`#define MUS_HOENN_X SEQ_... // mus_x`):
    each must be that song's slot in data/hoenn_music.json (music_slots.SCRIPT_SLOTS keeps them fixed)."""
    n = 0
    for name, slot, song in re.findall(r'^#define (MUS_HOENN_\w+)\s+(SEQ_\w+)\s*//\s*(mus_\w+)', open(SCRIPT_INC).read(), re.M):
        assert mp['slots'].get(song) == slot, f'hoenn_music.inc: {name} = {slot}, but {song} is in {mp["slots"].get(song)}'
        n += 1
    return n


def apply(files):
    if not enabled(): return 'off (HOENN_MUSIC=off)'
    import zoneheaders
    from sdat import SDAT
    mp = _mapping()
    path = os.path.join(files, SDAT_NAME)
    data = open(path, 'rb').read()
    songs, total = convert_all(mp)
    check_waits(mp, songs)
    check_script_slots(mp)
    data, used, room = install_all(data, songs, mp)
    if os.path.islink(path): os.unlink(path)
    open(path + '.tmp', 'wb').write(data); os.replace(path + '.tmp', path)
    ids = seq_ids(SDAT(data), mp)
    headers, entries = zoneheaders.load(files)
    zs, src = zone_songs(headers, mp)
    silence = SDAT(data).index('seq', mp.get('silence', 'SEQ_BGM_SILENCE_FIELD'))
    n = 0
    for z, song in zs.items():
        if z >= len(headers): continue
        if song is not None and song not in ids:
            continue
        headers[z]['bgm2'] = ids[song] if song else silence
        n += 1
    zoneheaders.save(files, headers, entries)
    grow = archive_reserve(mp)
    return (f'{len(songs)} songs, {used:,} of {room:,} free bytes; bgm2 of {n} zones '
            f'({len(set(s for s in zs.values() if s))} songs)'
            + (f'; archive grown by {grow:,} B to {len(data):,} B (archive_reserve)' if grow else ''))


# ---- code ---------------------------------------------------------------------------------------------------------
def _roamers():
    spec = importlib.util.spec_from_file_location('roamers_link', os.path.join(HERE, 'roamers.py'))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


def _bl(src, dst):
    off = dst - (src + 4)
    assert -(1 << 22) <= off < (1 << 22) and not off & 1, hex(off)
    return struct.pack('<HH', 0xF000 | (off >> 12) & 0x7FF, 0xF800 | (off >> 1) & 0x7FF)


def tables(mp):
    """The C header: redirects (Unova -> Hoenn, Hoenn -> stand-in), per trainer class and per species."""
    from sdat import SDAT, DEFAULT
    sd = SDAT(open(DEFAULT, 'rb').read())
    ids = seq_ids(sd, mp)
    def sid(x): return ids[x] if x.startswith('mus_') else sd.index('seq', x)
    import version
    redirect = dict(mp['redirect'])
    if version.RUBY: redirect.update(mp.get('redirect_ruby', {}))
    red = [(sid(a), sid(b)) for a, b in redirect.items()]
    rev = [(sid(a), sid(b)) for a, b in mp['reverse'].items()]
    cs = class_songs()
    if version.RUBY:      # Ruby's team is Magma: the same classes (data/ruby/hoenn_trainer_classes.json) get Magma's theme
        for v in cs.values():
            if v.get('eye') == 'mus_encounter_aqua': v['eye'] = 'mus_encounter_magma'
    for c, v in mp.get('classes', {}).items(): cs.setdefault(int(c), {}).update(v)
    n = max(cs) + 1
    eye, bat, vic = [0] * n, [0] * n, [0] * n
    for c, v in cs.items():
        if v.get('eye'): eye[c] = ids[v['eye']]
        if v.get('battle'): bat[c] = ids[v['battle']]
        if v.get('victory') == 'mus_victory_league': vic[c] = ids['mus_victory_league']   # WIN3 is shared with leaders
    wild = [(int(sp), ids[x]) for sp, x in mp['wild'].items()]
    win = [sd.index('seq', x) for x in mp['win_by_class']]
    rules = zone_rules(mp)
    def arr(name, xs): return f'static const u16 {name}[] = {{{", ".join(map(str, xs)) or "0"}}};\n'
    def song(x): return ids[x] if x else 0
    h = (f'#define N_REDIRECT {len(red)}\n#define N_REVERSE {len(rev)}\n#define N_CLASSES {n}\n#define N_WILD {len(wild)}\n'
         f'#define N_WIN {len(win)}\n'
         + arr('kRedirect', [x for p in red for x in p]) + arr('kReverse', [x for p in rev for x in p])
         + arr('kEye', eye) + arr('kBattle', bat) + arr('kVictory', vic) + arr('kWild', [x for p in wild for x in p])
         + arr('kWin', win)
         + f'#define N_CRISIS {len(rules["crisis_zones"])}\n#define CRISIS_SONG {song(rules["crisis_song"])}\n'
           f'#define CRISIS_FLAG {rules["crisis_flag"]}\n' + arr('kCrisisZones', rules['crisis_zones'])
         + f'#define N_INSTITUTE {len(rules["institute_zones"])}\n#define INSTITUTE_SONG {song(rules["institute_song"])}\n'
           f'#define INSTITUTE_VAR {rules["institute_var"]}\n' + arr('kInstituteZones', rules['institute_zones'])
         + (f'#define EM_ZONE_RULES 1\n#define N_LATE_CRISIS {len(rules["late_crisis_zones"])}\n'      # (Emerald only)
            f'#define LATE_CRISIS_VAR {rules["late_crisis_var"]}\n' + arr('kLateCrisisZones', rules['late_crisis_zones'])
            + f'#define N_SILENT {len(rules["silent_zones"])}\n#define SILENT_VAR {rules["silent_var"]}\n'
            f'#define SILENT_SONG {sd.index("seq", mp.get("silence", "SEQ_BGM_SILENCE_FIELD"))}\n'
            + arr('kSilentZones', rules['silent_zones']) if 'late_crisis_zones' in rules else '')
         + (f'#define EM_MAGMA_RULE 1\n#define N_MAGMA {len(rules["magma_zones"])}\n#define MAGMA_VAR {rules["magma_var"]}\n'      # (Emerald only)
            f'#define MAGMA_SONG {song(rules["magma_song"])}\n' + arr('kMagmaZones', rules['magma_zones']) if 'magma_zones' in rules else '')
         + f'#define TITLE_SONG {song(mp.get("title"))}\n#define AFTER_CATCH_SONG {song(mp.get("after_catch"))}\n'
           f'#define SEQ_POKEGET {sd.index("seq", "SEQ_ME_POKEGET")}\n#define SEQ_WIN1 {sd.index("seq", "SEQ_BGM_WIN1")}\n'
           f'#define MUSIC_QUERY {music_query()}\n')
    return h, dict(redirect=len(red), reverse=len(rev), classes=sum(1 for x in bat if x), eye=sum(1 for x in eye if x),
                   crisis=len(rules['crisis_zones']), institute=len(rules['institute_zones']))


def _hoenn_h(name):
    m = re.search(rf'^#define {name}\s+(\w+)', open(os.path.join(ROOT, 'src', 'include', 'hoenn.h')).read(), re.M)
    return int(m.group(1), 0)


def music_query():
    """BGMIsPlaying's argument that asks for the option (src/include/hoenn_music.inc MUSIC_QUERY_HOENN)."""
    return int(re.search(r'^#define MUSIC_QUERY_HOENN\s+(\w+)', open(SCRIPT_INC).read(), re.M).group(1), 0)


def zone_rules(mp):
    """Sapphire's zone rules (pokeruby overworld.c GetLocationMusic): ShouldLegendaryMusicPlayAtLocation (the weather
    song of the version in the crisis maps' zones: patches/weather.py crisis_zones, FLAG_SYS_WEATHER_CTRL) and
    IsInfiltratedWeatherInstitute (Mt. Chimney's song in the Weather Institute 1F/2F while VAR_WEATHER_INSTITUTE_STATE
    is 0). data/hoenn_music.json "zone_rules"."""
    import version
    zr = mp.get('zone_rules', {})
    spec = importlib.util.spec_from_file_location('weather_music', os.path.join(HERE, 'weather.py'))
    wm = importlib.util.module_from_spec(spec); spec.loader.exec_module(wm)
    rooms = json.load(open(os.path.join(ROOT, 'data', 'hoenn_interiors.json')))['rooms']
    inst = sorted({rooms[m]['zone'] for m in zr.get('institute_maps', []) if m in rooms and 'zone' in rooms[m]})
    out = dict(crisis_zones=wm.crisis_zones(), crisis_flag=_hoenn_h('FLAG_SYS_WEATHER_CTRL'),
               crisis_song=zr.get('crisis_song', {}).get(version.VERSION, zr.get('crisis_song', {}).get('sapphire')),   # (Emerald: Sapphire's until its own, notes/EMERALD.md)
               institute_zones=inst, institute_var=_hoenn_h('VAR_WEATHER_INSTITUTE_STATE'),
               institute_song=zr.get('institute_song'))
    if version.is_emerald():     # Emerald's two other zone rules (emerald_ch10, 2026-10-12; notes/EMERALD.md TODO EMERALD-3/4):
        # pokeemerald overworld.c ShouldLegendaryMusicPlayAtLocation (Routes 129-131 from VAR_SOOTOPOLIS_CITY_STATE 4) and
        # NoMusicInSootopolisWithLegendaries (Sootopolis City silent while VAR_SKY_PILLAR_STATE is 1)
        wj = json.load(open(os.path.join(os.environ.get('HOENN_WORLD_DIR') or version.world_dir(), 'world.json')))['zones']
        def of(maps): return sorted({int(z) for z, v in wj.items() if any(m in maps for m in v.get('maps', []))})
        out.update(late_crisis_zones=of(['Route129', 'Route130', 'Route131']), late_crisis_var=_hoenn_h('VAR_SOOTOPOLIS_STATE'),
                   silent_zones=of(['SootopolisCity']), silent_var=_hoenn_h('VAR_SKY_PILLAR_STATE'))
    if version.is_emerald():     # Emerald's third rule (emerald_ch9_mirage, 2026-10-12): pokeemerald overworld.c IsInflitratedSpaceCenter, Mossdeep's
        out.update(magma_zones=sorted(rooms[m]['zone'] for m in ('MossdeepCity_SpaceCenter_1F', 'MossdeepCity_SpaceCenter_2F')),   # Space Center 1F / 2F
                   magma_var=_hoenn_h('VAR_MOSSDEEP_CITY_STATE'), magma_song='mus_encounter_magma')    # play Magma's song while the state is 1 or 2
    return out


def build(base, workdir, header, force=None):
    with open(os.path.join(workdir, 'hoenn_music_data.h'), 'w') as f: f.write(header)
    obj = os.path.join(workdir, 'hoenn_music.o')
    defs = [f'-DMUSIC_FORCE={force}'] if force is not None else []
    subprocess.run([f'{LLVM}/clang', '--target=thumbv5te-none-eabi', '-mthumb', '-march=armv5te', '-Os', '-ffreestanding',
                    '-fno-builtin', '-fno-jump-tables', '-fno-pic', '-fno-unwind-tables', '-fno-asynchronous-unwind-tables',
                    '-fno-exceptions', '-fno-common', '-mno-unaligned-access', '-Wall', '-Werror', *defs,
                    '-I', workdir, '-c', os.path.join(HERE, 'hoenn_music.c'), '-o', obj], check=True)
    und = subprocess.run([f'{LLVM}/llvm-nm', '--undefined-only', obj], capture_output=True, text=True, check=True).stdout.split()
    assert not und, f'hoenn_music.c needs {und}: call Black 2 functions by address only'
    return _roamers().link(obj, base)


def _put(d, base, addr, old, new, what):
    o = addr - base
    cur = bytes(d[o:o + len(old)])
    assert cur == old, f'{what} at {addr:#x}: {cur.hex()} (expected {old.hex()})'
    d[o:o + len(new)] = new


def _load(code, name):
    p = os.path.join(code, name); return p, bytearray(open(p, 'rb').read())


def _save(p, d):
    if os.path.islink(p): os.unlink(p)
    open(p + '.tmp', 'wb').write(d); os.replace(p + '.tmp', p)


def apply_code(code):
    if not enabled(): return 'off'
    mp = _mapping()
    force = {'hoenn': 1, 'unova': 0}.get(os.environ.get('HOENN_TEST_MUSIC', '').lower())
    header, counts = tables(mp)
    yml = os.path.join(code, 'itcm.yaml')
    text = open(yml).read()
    size = int(re.search(r'^code_size: (\d+)$', text, re.M).group(1))
    assert re.search(r'^base_address: (\d+)$', text, re.M).group(1) == str(ITCM_BASE)
    base = ITCM_BASE + size
    p9, arm9 = _load(code, 'arm9.bin')
    lit = ARENA_ITCM_LIT - ARM9
    assert struct.unpack_from('<I', arm9, lit)[0] == base, 'the ITCM arena literal is not at the end of ITCM'
    with tempfile.TemporaryDirectory(dir=code) as tmp:
        blob, sym = build(base, tmp, header, force)
    end = (base + len(blob) + 31) & ~31
    assert end <= 0x02000000
    struct.pack_into('<I', arm9, lit, end)
    pi, itcm = _load(code, 'itcm.bin')
    assert len(itcm) == size
    _save(pi, bytes(itcm) + blob + bytes(end - base - len(blob)))
    open(yml, 'w').write(re.sub(r'^code_size: \d+$', f'code_size: {end - ITCM_BASE}', text, flags=re.M))
    p012, ov012 = _load(code, 'arm9_ov012.bin')
    # arm9
    _put(arm9, ARM9, 0x020300bc, struct.pack('<I', 0x02018969), struct.pack('<I', sym['Music_ZoneBGM'] | 1),
         'GetRegularZoneBGMID literal DecideZoneHeaderBGMID')
    _put(arm9, ARM9, 0x020300b0, bytes.fromhex('0804024b'), bytes.fromhex('024b1847'),
         'GetRegularZoneBGMID `lsls r0, r1, #16; ldr r3, [pc, #8]` -> `ldr r3, [pc, #8]; bx r3` (keeps the game data)')
    _put(arm9, ARM9, 0x02006428, bytes.fromhex('051c0c1c'), _bl(0x02006428, sym['Music_LoadShim'] & ~1),
         'func_02006424 adds r5, r0, #0; adds r4, r1, #0')
    _put(arm9, ARM9, 0x02005e14, bytes.fromhex('041c') + _bl(0x02005e16, 0x02006000),
         _bl(0x02005e14, sym['Music_Bgm2Redirect'] & ~1) + bytes.fromhex('041c'),
         'BGM2 play (0x02005e10) adds r4, r0, #0; bl ResetBGMChange')
    _put(arm9, ARM9, 0x02005e0a, _bl(0x02005e0a, 0x02005fe0), _bl(0x02005e0a, sym['Music_RequestChange'] & ~1),
         'func_02005e08 bl RequestBGMChange')
    # the stream (the title): `ldr rX, [pc, #0]; bx rX; .word Music_Stream*` over each function's first 8 bytes
    for addr, reg, old, name in ((0x02006fc8, 1, '18b581b041210091', 'Music_StreamInit'),
                                 (0x02007054, 1, '70b5051c0c480068', 'Music_StreamPlay'),
                                 (0x020070c0, 3, '011c0248024b0068', 'Music_StreamFadeStop'),
                                 (0x02007090, 3, '0248034b00680021', 'Music_StreamStop'),
                                 (0x020070a4, 3, '08b50548006866f0', 'Music_StreamIsPlaying')):
        assert addr % 4 == 0
        _put(arm9, ARM9, addr, bytes.fromhex(old), struct.pack('<HHI', 0x4800 | reg << 8, 0x4700 | reg << 3, sym[name] | 1),
             f'GFL stream function at {addr:#x} -> {name}')
    _put(arm9, ARM9, 0x02005d9c, bytes.fromhex('041c0d1c'), _bl(0x02005d9c, sym['Music_PlayCoreShim'] & ~1),
         'GFL_SndBGMPlayCore adds r4, r0, #0; adds r5, r1, #0')
    _put(arm9, ARM9, 0x02030794, bytes.fromhex('81000148405a704796230902'),
         struct.pack('<HHI', 0x4B00, 0x4718, sym['Music_EyeBGM'] | 1), 'GetTrainerClassEyeBGMID')
    # ov012
    for at in (0x02168558, 0x02168aa2):
        _put(ov012, OV012, at, _bl(at, 0x021c5ef8), _bl(at, sym['Music_DecideEnvWild'] & ~1),
             'bl EventBattleCall_DecideEnvWild')
    _put(ov012, OV012, 0x02168804, _bl(0x02168804, 0x021c618c), _bl(0x02168804, sym['Music_DecideEnvTrainer'] & ~1),
         'bl EventBattleCall_DecideEnvTrainer')
    # ov036 s009B_BGMIsPlaying
    p036, ov036 = _load(code, 'arm9_ov036.bin')
    _put(ov036, OV036, 0x021a6e2a, _bl(0x021a6e2a, 0x020159e8), _bl(0x021a6e2a, sym['Music_ScrRead16'] & ~1),
         's009B bl VM_Read16')
    _put(ov036, OV036, 0x021a6e38, _bl(0x021a6e38, 0x02005fa8), _bl(0x021a6e38, sym['Music_ScrBGMIsPlaying'] & ~1),
         's009B bl GFL_SndBGMIsPlaying')
    _save(p9, arm9); _save(p012, ov012); _save(p036, ov036)
    open(os.path.join(code, 'music_symbols.json'), 'w').write(json.dumps(
        {k: sym[k] | 1 for k in ('Music_IsHoenn', 'Music_Redirect', 'Music_ZoneBGM')} | {'itcm_start': base, 'itcm_end': end}
        | {k: v for k, v in sym.items() if k in ('gMusicLastClass', 'gMusicCaught', 'gMusicTitle', 'gMusicQuery')},
        indent=1))
    return (f'hoenn_music: {len(blob)} B of ITCM at {base:#x}; {counts["redirect"]} redirects, {counts["reverse"]} '
            f'reverse, {counts["classes"]} classes, {counts["eye"]} encounter themes, crisis zones {counts["crisis"]}, '
            f'institute zones {counts["institute"]}'
            + (f'; HOENN_TEST_MUSIC forces {force}' if force is not None else ''))
