"""Emerald's music from the user's own Emerald dump (roms/emerald_original.gba, BPEE, SHA-1 f3ae0881...; notes/MUSIC.md,
notes/EMERALD_PLAN.md 1.6) for the same converter as Sapphire's (b2tools/m4a_to_sseq.py). Nothing here changes m4a.py or
m4a_to_sseq.py: EmeraldRom is an m4a.GbaRom that knows Emerald's song table and names Emerald's samples with Sapphire's
(pokeruby's) names, so data/hoenn_music.json "defaults" apply as they are.

    python3 m4a_emerald.py samples                 every DirectSound sample Emerald's songs play: its Sapphire twin (same
                                                   WaveData header + data bytes) or none
    python3 m4a_emerald.py compare [SONG ...]      every song both games have (name map below): notes / tempo / volume /
                                                   pan / loop per track (m4a.parse_track) and the instruments (sample
                                                   bytes, envelope) behind each voice; which differ and how
    python3 m4a_emerald.py convert SONG ... [--out DIR]   convert from Emerald (m4a_to_sseq.Song with an EmeraldRom and
                                                   data/hoenn_music.json deep-merged with data/emerald/hoenn_music.json)
    python3 m4a_emerald.py gains SONG ...          the whole-part balance of music_calib.py --gains for Emerald songs
                                                   (GBA part levels rendered from the Emerald dump, the same "ref")

Song table: gSongTable is found by the player pattern of pokeemerald's sound/song_table.inc (610 songs; the `song` macro
of asm/macros/m4a.inc: .4byte header, .2byte music player, .2byte unknown), as m4a.py finds Sapphire's with pokeruby's.
Samples: pokeemerald's data/sound_data.s puts sound/direct_sound_data.inc right after the song table; its 156 labels are
walked in order from the first WaveData header after it (BPEE: 4 bytes after the table; each WaveData: 16-byte header +
data, .align 2; the data length per type: EmeraldRom.data_len), so every Emerald sample has its pokeemerald label; a
sample whose header + size data bytes equal a Sapphire sample's takes Sapphire's pokeruby name (m4a_to_sseq.voice_key
then finds data/hoenn_music.json "defaults"). Samples the songs play from outside that list (BPEE 0x088D8418, Sapphire's
sc88pro_nylon_str_guitar) are named by the same byte match.

convert_all(mp) is what an Emerald build's patches/hoenn_music.convert_all needs: each song from the ROM its data names
(data/emerald/hoenn_music.json songs.<song>.rom), the overlay's "gains" over the calibrated gains table.

Emerald's own instruments (frontier_core_music, 2026-10-12): a GBA voice whose sample has a "defaults" entry
{"gba": true} is played by its own sample, not by a Black 2 library program (the Battle Frontier's choir, female voice,
gamelan, electric piano, guitars, shakuhachi and koto: Black 2 has no counterpart). EmeraldSong gives each such voice a
program of the song's bank (GBA_PROG0 and up, above the library's 0-108) whose wave is the GBA sample's own bytes as an
NDS PCM8 wave (gba_swav: rate = WaveData freq / 1024 at base key 60, pokeemerald m4a.c MidiKeyToFreq: key 60 gives
gFreqTable[0] >> 9 = 2^22, so freq * 2^22 / 2^32), and whose envelope is the voice's GBA envelope in NDS terms
(gba_adsr). The NDS envelope rules are Black 2's own ARM7 code (external/pokebw2/extract/b2_us/arm7/arm7.bin, read at
run time: the attack table at file 0x115a0 and the decibel table at 0x1148c, autoloaded to 0x03808f5c / 0x03808e48; the
envelope step at 0x03800ea0 and the decay/release rate at 0x038014d4, disassembled): attack multiplies the level (from
-92544, 1/1280 dB units) by table/256 each update, decay and release subtract a rate (127: 0xFFFF, 126: 15360, < 50:
2v+1, else 7680 / (126 - v)), sustain is decibel_table[s] << 7. The balance of such a part (auto_gain, music_calib
--gains) needs its Black 2 level: nds_note_rms renders one note of the wave with that envelope, and the calibration
constant data "gba_instruments.level_k" (Black 2 level / rendered level, the median over the library programs measured
in game, data/hoenn_music_levels.json) turns it into the same units (EmeraldSong._levels).

Name map (song_table.inc order / ids, include/constants/songs.h): every pokeruby `mus_*` keeps its name in pokeemerald
except mus_b_tower (pokeruby id 384) = pokeemerald mus_b_tower_rs (id 384; Emerald's mus_b_tower is the Frontier's new
tower song, id 465) and mus_weather_kyogre (id 443) whose id pokeemerald gives to mus_abnormal_weather ("Replaces
MUS_WEATHER_KYOGRE from R/S"); mus_radio_tower_takeover (unused) is gone. The battle songs moved (457-466 -> 474-483).
"""
import hashlib, json, os, re, struct, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
import m4a  # noqa: E402

EM_ROM = os.path.join(ROOT, 'roms', 'emerald_original.gba')
EM_SHA1 = 'f3ae088181bf583e55daf962a92bb46f4f1d07b7'
PEM = os.path.join(ROOT, 'external', 'pokeemerald')
OVERLAY = os.path.join(ROOT, 'data', 'emerald', 'hoenn_music.json')
OUT = os.path.join(ROOT, 'work', 'agents', 'emerald_art', 'music', 'out')

# pokeruby name -> pokeemerald name where they differ (see the docstring); everything else is the same name
RENAMED = {'mus_b_tower': 'mus_b_tower_rs'}
# Emerald songs that take a pokeruby song's id with other music (compared to check, not a rename)
SAME_ID = {'mus_weather_kyogre': 'mus_abnormal_weather'}
NEW_STORY = ['mus_abnormal_weather', 'mus_rayquaza_appears', 'mus_vs_rayquaza', 'mus_vs_mew', 'mus_register_match_call']


class EmeraldRom(m4a.GbaRom):
    """Emerald's songs, read like Sapphire's (m4a.GbaRom), with pokeemerald's song table and Sapphire-named samples."""
    def __init__(self, path=EM_ROM, sapphire=None, check=True):
        self.d = open(path, 'rb').read()
        if check:
            assert self.d[0xAC:0xB0] == b'BPEE', f'{path}: not Emerald (game code {self.d[0xAC:0xB0]})'
            sha = hashlib.sha1(self.d).hexdigest()
            assert sha == EM_SHA1, f'{path}: SHA-1 {sha}, not the user\'s dump {EM_SHA1}'
        self.song_table = self._find_song_table()
        self.sample_names = None
        self._sapphire = sapphire
        self.em_labels, self.twins, self.no_twin = {}, {}, {}

    def _find_song_table(self):
        txt = open(os.path.join(PEM, 'sound', 'song_table.inc')).read()
        players = {k: int(v) for k, v in re.findall(r'\.equiv\s+(\w+),\s*(\d+)', txt)}
        ents = re.findall(r'^\s*song\s+(\w+),\s*(\w+),\s*(\w+)', txt, re.M)
        self.song_names = [n for n, _, _ in ents]
        pat = [(players.get(a, None) if not a.isdigit() else int(a), int(b) if b.isdigit() else players[b]) for _, a, b in ents]
        d = self.d
        for off in range(0, len(d) - 8 * len(pat), 4):
            if all(struct.unpack_from('<HH', d, off + 8 * i + 4) == pat[i] and
                   0x08000000 <= struct.unpack_from('<I', d, off + 8 * i)[0] < 0x0A000000 for i in range(40)):
                assert all(struct.unpack_from('<HH', d, off + 8 * i + 4) == pat[i] for i in range(len(pat))), \
                    'song table: the first 40 players match, not all'
                return 0x08000000 + off
        raise SystemExit('Emerald song table not found')

    @property
    def sapphire(self):
        if self._sapphire is None: self._sapphire = m4a.GbaRom()
        return self._sapphire

    def _name_samples(self):
        """Walk pokeemerald's direct_sound_data.inc from the end of the song table (data/sound_data.s order); name each
        sample by its Sapphire twin (header + data bytes equal) or by its pokeemerald label."""
        labels = re.findall(r'^DirectSoundWaveData_(\w+)::', open(os.path.join(PEM, 'sound', 'direct_sound_data.inc')).read(), re.M)
        def ok(a):
            typ, status, freq, loop, size = struct.unpack_from('<HHIII', self.d, a & 0x1FFFFFF)
            return typ in (0, 1) and status in (0, 0x4000) and 0 < size < 0x100000 and 0 < freq and loop <= size
        # the first sample: the first WaveData header after the table (BPEE: 4 zero bytes after it, 0x086B5D04)
        a = next(x for x in range(self.song_table + 8 * len(self.song_names), self.song_table + 8 * len(self.song_names) + 64, 4)
                 if ok(x))
        for lab in labels:
            assert ok(a), f'sample {lab} at {a:08X}: bad header'
            self.em_labels[a] = lab
            a = (a + 16 + self.data_len(self, a) + 3) & ~3
        sap = self.sapphire
        sap.sample_name(0)                                # fills sap.sample_names
        by_bytes = {}
        for addr, name in sap.sample_names.items():
            by_bytes.setdefault(self.wave_bytes(sap, addr), []).append(name)
        self._by_bytes = by_bytes
        self.sample_names = {}
        for addr, lab in self.em_labels.items():
            names = by_bytes.get(self.wave_bytes(self, addr))
            if names:
                self.twins[addr] = names
                self.sample_names[addr] = names[0]
            else:
                self.no_twin[addr] = lab
                self.sample_names[addr] = lab

    @staticmethod
    def data_len(rom, addr):
        """Bytes after a WaveData header, as both dumps store them: type 0 (8-bit PCM): size + 1 (the sample after the
        end that the mixer reads), type 1 (compressed, pokeemerald tools/wav2agb convert_dpcm_impl: blocks of 64
        samples, each an initial byte, then a byte with sample 1's 4-bit delta, then two deltas per byte; the last
        block unpadded: 2 + (n - 1) // 2 bytes for n samples, 33 for 64). Checked by walking all 156 of Emerald's
        samples header to header."""
        typ, size = struct.unpack_from('<H', rom.d, addr & 0x1FFFFFF)[0], struct.unpack_from('<I', rom.d, (addr & 0x1FFFFFF) + 12)[0]
        if typ == 1:
            n = size % 64
            return size // 64 * 33 + (0 if n == 0 else 1 if n == 1 else 2 + (n - 1) // 2)
        return size + 1

    @staticmethod
    def wave_bytes(rom, addr):
        """SHA-1 of a sample's WaveData header + its size bytes of data (m4a.GbaRom.wave's extent)."""
        o = addr & 0x1FFFFFF
        size = struct.unpack_from('<I', rom.d, o + 12)[0]
        return hashlib.sha1(rom.d[o:o + 16 + size]).hexdigest()

    def sample_name(self, addr):
        if self.sample_names is None: self._name_samples()
        if addr not in self.sample_names and 0x08000000 <= addr < 0x09000000:     # outside direct_sound_data.inc
            names = self._by_bytes.get(self.wave_bytes(self, addr))
            if names: self.twins[addr] = names
            self.sample_names[addr] = names[0] if names else f'{addr:08X}'
        return self.sample_names.get(addr, f'{addr:08X}')


def emerald_name(song):
    return RENAMED.get(song, song)


# ---- comparing a song of both games --------------------------------------------------------------------------------
def tone_sig(rom, t):
    """A ToneData by content: every field, the pointer replaced by what it points to (sample bytes, the wave's 16 bytes,
    a square's duty, noise period)."""
    k = t['type']
    base = (k, t['key'], t['length'], t['pan_sweep'], t['attack'], t['decay'], t['sustain'], t['release'])
    if k & 0xC0: return base
    if k & 7 == 0: return base + ('pcm', EmeraldRom.wave_bytes(rom, t['wav']))
    if k & 7 == 3: return base + ('wave', rom.d[t['wav'] & 0x1FFFFFF:(t['wav'] & 0x1FFFFFF) + 16].hex())
    return base + ('cgb', t['wav'])


def voice_sig(rom, vg, v, keys):
    """A voice by content for the keys it plays: key splits by the sub-voice each key picks, drum kits key by key."""
    t = rom.voice(vg, v)
    if t['type'] & 0x80:
        return ('drums', tuple((k, tone_sig(rom, rom.tone(t['wav'] + 12 * k))) for k in sorted(keys)))
    if t['type'] & 0x40:
        return ('split', tuple((k, tone_sig(rom, rom.tone(t['wav'] + 12 * rom.d[(t['keysplit'] + k) & 0x1FFFFFF])))
                               for k in sorted(keys)))
    return tone_sig(rom, t)


def song_events(rom, name):
    """Per track: the parsed events with each voice index replaced by its content, the loop and the end."""
    h, trs = m4a.parse_song(rom, rom.song_index(name))
    keys = {}
    for tr in trs:
        v = 0
        for e in tr.events:
            if e[0] == 'voice': v = e[2]
            elif e[0] == 'note': keys.setdefault(v, set()).add(e[2])
    out = []
    for tr in trs:
        ev = [('voice', e[1], voice_sig(rom, h['voicegroup'], e[2], keys.get(e[2], ()))) if e[0] == 'voice' else e
              for e in tr.events]
        out.append(dict(events=ev, loop=(tr.loop_event, tr.loop_tick), end=tr.end_tick))
    return h, trs, out


def compare(sap, em, name, em_name=None):
    """What differs between Sapphire's song `name` and Emerald's `em_name`: a list of plain-words findings ([] = same
    music, only the data layout may differ)."""
    h1, t1, a = song_events(sap, name)
    h2, t2, b = song_events(em, em_name or name)
    out = []
    if (h1['tracks'], h1['priority'], h1['reverb']) != (h2['tracks'], h2['priority'], h2['reverb']):
        out.append(f'header {h1["tracks"]}/{h1["priority"]}/{h1["reverb"]:#x} -> {h2["tracks"]}/{h2["priority"]}/{h2["reverb"]:#x}'
                   ' (tracks/priority/reverb)')
    for i in range(min(len(a), len(b))):
        x, y = a[i], b[i]
        if x == y: continue
        kinds = {}
        for k in ('note', 'tempo', 'vol', 'pan', 'voice', 'keysh', 'bend', 'bendr', 'mod', 'lfos', 'lfodl', 'modt',
                  'tune', 'xcmd', 'prio', 'eot'):
            ex = [e for e in x['events'] if e[0] == k]; ey = [e for e in y['events'] if e[0] == k]
            if ex != ey: kinds[k] = (len(ex), len(ey))
        if x['loop'] != y['loop'] or x['end'] != y['end']:
            kinds['loop'] = (x['loop'][1], x['end'], y['loop'][1], y['end'])
        if 'voice' in kinds:
            vx = {e[2] for e in x['events'] if e[0] == 'voice'}; vy = {e[2] for e in y['events'] if e[0] == 'voice'}
            why = []
            for s in vy - vx:
                near = [o for o in vx if o[:1] == s[:1]]
                if s[-2:-1] == ('pcm',) and any(o[-1] != s[-1] for o in vx): why.append('sample')
                elif near: why.append('envelope/settings')
                else: why.append('other voice')
            kinds['voice'] = sorted(set(why)) or ['order']
        out.append(f'track {i}: ' + ', '.join(f'{k} {v}' for k, v in kinds.items()))
    if len(a) != len(b): out.append(f'{len(a)} tracks -> {len(b)}')
    return out


# ---- Emerald's own instruments: GBA samples as NDS waves (see the docstring) -------------------------------------------
ARM7 = os.path.join(ROOT, 'external', 'pokebw2', 'extract', 'b2_us', 'arm7', 'arm7.bin')
ATTACK_TABLE = bytes([0x00, 0x01, 0x05, 0x0E, 0x1A, 0x26, 0x33, 0x3F, 0x49, 0x54, 0x5C, 0x64, 0x6D, 0x74, 0x7B, 0x7F,
                      0x84, 0x89, 0x8F])
SND_TIMER_CLOCK = 16756991          # NDS sound timer clock (Black 2's waves: timer = clock / rate)
GBA_PROG0 = 110                     # the first program of a GBA-sample instrument in a song's bank (library: 0-108)
NDS_START = -92544                  # the envelope's start level (-723 << 7: -72.3 dB)
_DB = None


def db_table():
    """Black 2's decibel table (128 s16, 0.1 dB: velocity / volume / sustain -> level), read from its ARM7 binary; the
    attack table is checked in the same file."""
    global _DB
    if _DB is None:
        d = open(ARM7, 'rb').read()
        assert d[0x115a0:0x115a0 + len(ATTACK_TABLE)] == ATTACK_TABLE, 'arm7.bin: the attack table moved'
        _DB = struct.unpack_from('<128h', d, 0x1148c)
        assert _DB[127] == 0 and _DB[64] == -119, 'arm7.bin: not the decibel table'
    return _DB


def nds_attack_mul(a):
    return 255 - a if a < 109 else ATTACK_TABLE[127 - a]


def nds_fall_rate(v):
    return 0xFFFF if v == 127 else 15360 if v == 126 else 2 * v + 1 if v < 50 else (7680 // (126 - v)) & 0xFFFF


def nds_envelope(adsr, gate_s, dur_s, ups=None):
    """The NDS envelope (level per update, 1/1280 dB) of one note held gate_s seconds, over dur_s seconds."""
    import m4a_to_sseq as conv
    ups = ups or conv.NDS_UPDATES_PER_SEC
    a, d, s, r = adsr
    m, dr, rr, sl = nds_attack_mul(a), nds_fall_rate(d), nds_fall_rate(r), db_table()[s] << 7
    lv, state, out = NDS_START, 0, []
    for n in range(int(dur_s * ups) + 1):
        if n >= gate_s * ups and state < 3: state = 3
        if state == 0:
            lv = -((-lv * m) >> 8)
            if lv == 0: state = 1
        elif state == 1:
            lv -= dr
            if lv <= sl: lv, state = sl, 2
        elif state == 3:
            lv = max(lv - rr, -(1 << 23))
        out.append(lv)
    return out


def gba_adsr(attack, decay, sustain, release):
    """The NDS (attack, decay, sustain, release) closest to a GBA DirectSound envelope (m4a: per frame, attack adds to
    the level 0-255, decay and release multiply it by x/256, sustain is a level; m4a_render.py): the attack by the time
    to reach -1 dB, decay and release by their slope in dB per second (both systems fall linearly in dB), sustain by its
    level in dB."""
    import math
    import m4a_to_sseq as conv
    fg, fn = m4a.FRAME_HZ, conv.NDS_UPDATES_PER_SEC
    db = db_table()
    # attack: GBA frames until the level reaches 0.891 (-1 dB) after the first frame; NDS updates until -1 dB
    f, env = 0, attack
    while 0 < env < 227: env += attack; f += 1
    t_gba = f / fg

    def t_nds(a):
        lv, n, m = NDS_START, 0, nds_attack_mul(a)
        while lv < -1280 and n < 10000: lv = -((-lv * m) >> 8); n += 1
        return (n - 1) / fn
    a_nds = 127 if attack >= 255 else 0 if attack == 0 else min(range(128), key=lambda a: (abs(t_nds(a) - t_gba), -a))

    def fall(x):
        if x == 0: return 127                                   # GBA x 0: gone in one frame
        target = -20 * math.log10(x / 256) * fg * 1280 / fn      # NDS units per update for the same dB per second
        return min(range(127), key=lambda v: abs(math.log(nds_fall_rate(v)) - math.log(target)))
    if sustain >= 255: s_nds = 127
    elif sustain == 0: s_nds = 0
    else:
        want = 200 * math.log10(sustain / 255)                  # 0.1 dB
        s_nds = min(range(1, 128), key=lambda v: abs(db[v] - want))
    d_nds = 127 if sustain >= 255 else fall(decay)
    return a_nds, d_nds, s_nds, fall(release)


def gba_swav(rom, addr):
    """A GBA DirectSound sample (uncompressed WaveData) as an NDS PCM8 wave (SWAR entry: u8 encoding 0, u8 loop, u16
    rate, u16 timer, u16 loop start, u32 loop length, both in words; signed 8-bit samples, as the GBA's). The loop start
    is word-aligned by 0-3 silent samples before the attack, and the loop (GBA: loop start to the end) is repeated until
    its length is whole words, so it keeps its exact length and pitch."""
    import math
    w = rom.wave(addr)
    assert w['type'] == 0, f'{addr:08X}: compressed sample (type {w["type"]})'
    data, n, rate = w['data'], w['size'], w['freq']
    timer = round(SND_TIMER_CLOCK / rate)
    if w['loop']:
        ls = w['loop_start']; pad = (-ls) % 4
        loop = data[ls:n]
        body = bytes(pad) + data[:ls] + loop * (4 // math.gcd(len(loop), 4))
        return struct.pack('<BBHHHI', 0, 1, round(rate), timer, (ls + pad) // 4, (len(body) - ls - pad) // 4) + body
    body = data + bytes((-n) % 4)
    return struct.pack('<BBHHHI', 0, 0, round(rate), timer, 0, len(body) // 4) + body


def nds_note_rms(wave, base_key, adsr, key, gate_s, dur_s=1.2, fs=32768):
    """RMS (wave units, velocity / volume / pan left out) of one NDS note: the wave played at key (pitch from its timer and
    base key, nearest sample, looped as the hardware loops) under nds_envelope, over dur_s seconds (music_calib's
    window)."""
    import numpy as np
    import m4a_to_sseq as conv
    from sdat import decode_wave, wave_info
    x, _, ls = decode_wave(wave)
    i = wave_info(wave)
    rate = SND_TIMER_CLOCK / i['timer'] * 2 ** ((key - base_key) / 12)
    pos = (np.arange(int(dur_s * fs)) * rate / fs).astype(np.int64)
    if ls is not None and len(x) > ls:
        over = pos >= len(x)
        pos[over] = ls + (pos[over] - ls) % (len(x) - ls)
        y = x[pos]
    else:
        y = np.where(pos < len(x), x[np.minimum(pos, len(x) - 1)], 0.0)
    ups = conv.NDS_UPDATES_PER_SEC
    env = np.array(nds_envelope(adsr, gate_s, dur_s, ups), dtype=np.float64)
    amp = 10 ** ((np.floor(env / 128)) / 200)
    amp[env <= NDS_START] = 0.0
    g = amp[np.minimum((np.arange(len(y)) / fs * ups).astype(np.int64), len(amp) - 1)]
    return float(np.sqrt(((y * g) ** 2).mean()))


def _conv_song():
    import m4a_to_sseq as conv
    return conv.Song


class EmeraldSong(_conv_song()):
    """m4a_to_sseq.Song for an Emerald build: the same conversion, plus the voices whose sample's "defaults" entry is
    {"gba": true} (Emerald's own instruments, the docstring). A song without such a voice converts byte for byte as
    m4a_to_sseq.Song does."""
    def __init__(self, name, key=None, **kw):
        super().__init__(name, **kw)
        import music_roles
        if key and key != name:          # a mapping key other than the ROM's name (mus_b_tower_frontier: Emerald's
            self.name = key              # mus_b_tower): gains, config and context by the key
            self.cfg = self.map['songs'].get(key, {})
            self.context = self.cfg.get('context') or music_roles.song_context(key)
        self.map = dict(self.map, defaults=dict(self.map['defaults']))         # per song: part_map swaps entries
        if self.levels and self.levels.get('programs') is not None:
            self.levels = dict(self.levels, programs=dict(self.levels['programs']))
        self.gba_inst = {}               # program -> dict(wav, tone, adsr, sample)
        self._gba_prog = {}              # GBA voice -> program

    def part_map(self, track, v):
        import m4a_to_sseq as conv
        if (track, v) in self.decisions: return self.decisions[(track, v)]
        vg = self.header['voicegroup']
        vk = conv.voice_key(self.rom, vg, v)
        if not (self.map['defaults'].get(vk) or {}).get('gba'):
            return super().part_map(track, v)
        t = self.rom.voice(vg, v)
        assert not t['type'] & 0xC0 and t['type'] & 7 == 0 and not t['type'] & 8, \
            f'{self.name}: voice {v} ({vk}) is not a plain DirectSound voice'
        if v not in self._gba_prog:
            prog = GBA_PROG0 + len(self._gba_prog)
            assert prog < 128, f'{self.name}: too many Emerald instruments'
            adsr = gba_adsr(t['attack'], t['decay'], t['sustain'], t['release'])
            self._gba_prog[v] = prog
            self.gba_inst[prog] = dict(wav=t['wav'], adsr=adsr, sample=vk, swav=gba_swav(self.rom, t['wav']),
                                       gba=(t['attack'], t['decay'], t['sustain'], t['release']))
            self._levels(prog)
        prog = self._gba_prog[v]
        old = self.map['defaults'][vk]
        self.map['defaults'][vk] = {'program': prog}
        try:
            m = super().part_map(track, v)
        finally:
            self.map['defaults'][vk] = old
        g, n = self.gba_inst[prog]['gba'], self.gba_inst[prog]['adsr']
        m['why'] = f'Emerald\'s own sample, GBA envelope {g} -> NDS {n}'
        m['gba'] = True
        return m

    def _levels(self, prog):
        """Black 2 levels of a GBA-sample program on music_calib's grid (keys 36-96, gates 6/24/96 GBA ticks at 120
        bpm): nds_note_rms x data gba_instruments.level_k, x the library's calibration velocity / volume (in level_k)."""
        k = (self.map.get('gba_instruments') or {}).get('level_k')
        if not k or not self.levels or self.levels.get('programs') is None: return
        inst = self.gba_inst[prog]
        tab = {}
        for key in (36, 48, 60, 72, 84, 96):
            for gate, secs in ((6, 0.125), (24, 0.5), (96, 2.0)):
                tab[f'{key},{gate}'] = round(k * nds_note_rms(inst['swav'], 60, inst['adsr'], key, secs), 2)
        self.levels['programs'][str(prog)] = tab

    def build_bank(self, budget=None):
        """The library part as m4a_to_sseq.Song.build_bank (its budget less the GBA waves), then one PCM program per
        GBA-sample voice: the wave appended to the song's wave archive, base key 60, the converted envelope, centre pan."""
        from sdat import parse_sbnk, build_sbnk, parse_swar, build_swar
        gba = {p: self.notes_used.pop(p) for p in list(self.notes_used) if p in self.gba_inst}
        if not gba: return super().build_bank(budget)
        extra = sum((len(self.gba_inst[p]['swav']) + 3) & ~3 for p in gba) + 64 * len(gba)
        budget = (budget or self.cfg.get('budget', self.map.get('budget', 242000))) - extra
        try:
            sbnk, swar, used = super().build_bank(budget)
        finally:
            self.notes_used.update(gba)
        inst, waves = parse_sbnk(sbnk), parse_swar(swar)
        for p in sorted(gba):
            gi = self.gba_inst[p]
            waves.append(gi['swav'])
            inst[p] = (1, [(0, 127, 1, len(waves) - 1, 0, 60) + tuple(gi['adsr']) + (64,)])
        return build_sbnk(inst), build_swar(waves), list(used) + [gi['sample'] for gi in self.gba_inst.values()]


# ---- mapping (base + Emerald overlay) and conversion ---------------------------------------------------------------
def merge(base, over):
    """version.merge (b2tools/version.py load_json's deep merge): dicts key by key, anything else replaced."""
    if isinstance(base, dict) and isinstance(over, dict):
        out = dict(base)
        for k, v in over.items(): out[k] = merge(base[k], v) if k in base else v
        return out
    return over


def load_mapping():
    import m4a_to_sseq as conv
    mp = conv.load_mapping()
    if os.path.exists(OVERLAY): mp = merge(mp, json.load(open(OVERLAY)))
    return mp


def convert(names, out=OUT):
    """Convert songs as an Emerald build would (convert_all: the ROM each song's data names, Emerald's gains) and
    write OUT/<song>.{sseq,sbnk,swar,txt}."""
    mp = load_mapping()
    os.makedirs(out, exist_ok=True)
    songs, objs = convert_all(mp, names)
    for name, (data, bank, swar, vol) in songs.items():
        for ext, b in (('sseq', data), ('sbnk', bank), ('swar', swar)):
            open(os.path.join(out, f'{name}.{ext}'), 'wb').write(b)
        song = objs[name]
        rep = [song.report[0].replace(f'{name} (', f'{name} ({"Emerald" if song.rom.d[0xAC:0xB0] == b"BPEE" else "Sapphire"} dump, ', 1)] + song.report[1:]
        open(os.path.join(out, f'{name}.txt'), 'w').write('\n'.join(rep) + '\n')
        print('\n'.join(rep))
    return objs


def convert_all(mp, names=None, sapphire=None, emerald=None, levels=None, sdat=None):
    """What an Emerald build's patches/hoenn_music.convert_all needs to do (the proposal): every song of mp['slots'],
    each from the ROM its data names (songs.<song>.rom == 'emerald': the Emerald dump, under its pokeemerald name;
    else Sapphire's), with mp['gains'] over the levels' gains_table. Returns {song: (sseq, sbnk, swar, INFO volume)}
    and {song: Song}."""
    import m4a_to_sseq as conv
    from sdat import SDAT, DEFAULT
    sapphire = sapphire or m4a.GbaRom()
    sd = sdat or SDAT(open(DEFAULT, 'rb').read())
    lv = dict(levels or conv.load_levels())
    lv['gains_table'] = {**lv.get('gains_table', {}), **mp.get('gains', {})}
    out, objs = {}, {}
    for song in (names or mp['slots']):
        cfg = mp['songs'].get(song, {})
        if cfg.get('rom') == 'emerald':
            emerald = emerald or EmeraldRom(sapphire=sapphire)
            rom, rn = emerald, cfg.get('rom_name', emerald_name(song))
        else:
            rom, rn = sapphire, song
        sg = EmeraldSong(rn, key=song, rom=rom, mapping=mp, sdat=sd, levels=lv)   # (mus_b_tower_rs, Emerald's
        q, b, w = sg.convert()                    # mus_b_tower as mus_b_tower_frontier: gains/config by the key)
        out[song] = (q, b, w, sg.info_volume)
        objs[song] = sg
    return out, objs


def gains(names, rom=None):
    """music_calib.py's whole-part gains (its --gba and --gains steps) for Emerald songs: {song:tTvV: gain}, the same ref
    as data/hoenn_music_gains.json so the balance matches Sapphire's songs."""
    import m4a_to_sseq as conv
    import music_calib as mc
    from sdat import SDAT, DEFAULT
    rom = rom or EmeraldRom()
    mp, sd = load_mapping(), SDAT(open(DEFAULT, 'rb').read())
    lv = conv.load_levels()
    ref = json.load(open(conv.GAINS))['ref']
    lv0 = {k: x for k, x in lv.items() if k != 'gains_table'}
    conv._GBA_LEVEL.clear()
    out = {}
    for name in names:
        rn = mp['songs'].get(name, {}).get('rom_name', emerald_name(name))    # (mus_b_tower_frontier: mus_b_tower)
        s = EmeraldSong(rn, key=name, rom=rom, mapping=mp, sdat=sd, levels=lv0)
        s.convert()
        for (t, v), (g, b) in mc.part_levels(s).items():
            if g > 1e-3 and b > 1e-3: out[f'{name}:t{t}v{v}'] = round(max(0.1, min(4.0, ref / (b / g))), 3)
        print(name, {k: x for k, x in out.items() if k.startswith(name + ':')}, flush=True)
    return out


def main(argv):
    cmd = argv[0] if argv else 'samples'
    if cmd == 'samples':
        import m4a_to_sseq as conv
        em = EmeraldRom()
        em.sample_name(0)
        mp = load_mapping()
        songs = argv[1:] or [n for n in em.song_names if n.startswith('mus_') and not n.startswith('mus_rg_')]
        played, keys_of = {}, {}            # sample address -> songs (notes really played); voice keys -> songs
        for n in songs:
            h, trs = m4a.parse_song(em, em.song_index(n))
            vg = h['voicegroup']
            for tr in trs:
                v = 0
                for e in tr.events:
                    if e[0] == 'voice': v = e[2]
                    elif e[0] == 'note':
                        t, _ = em.resolve(vg, v, e[2])
                        if t['type'] & 7 == 0 and not t['type'] & 0xC0: played.setdefault(t['wav'], set()).add(n)
                        vt = em.voice(vg, v)
                        vk = conv.voice_key(em, vg, v)
                        kind = 'drum kit' if vt['type'] & 0x80 else 'voice'
                        keys_of.setdefault((kind, vk), set()).add(n)
        print(f'song table {em.song_table:08X}, {len(em.song_names)} songs; {len(em.em_labels)} samples walked '
              f'({len(em.twins)} with a Sapphire twin, {len(em.no_twin)} without); {len(songs)} songs, '
              f'{len(played)} samples played by their notes')
        for a in sorted(played):
            tw = 'twin ' + '/'.join(em.twins[a]) if a in em.twins else 'NO TWIN'
            print(f'  {a:08X} {em.em_labels.get(a, "?"):40s} {tw:42s} {len(played[a]):3d} songs: {", ".join(sorted(played[a]))[:110]}')
        print('converter voice keys (m4a_to_sseq.voice_key: key-60 sample of a key split) with no "defaults" entry:')
        for (kind, vk), ss in sorted(keys_of.items()):
            if kind == 'voice' and vk not in ('square', 'wave', 'noise', 'drums') and vk not in mp['defaults']:
                print(f'  {vk:40s} songs: {", ".join(sorted(ss))}')
    elif cmd == 'compare':
        import m4a_to_sseq as conv
        sap = m4a.GbaRom(); em = EmeraldRom(sapphire=sap)
        names = argv[1:] or conv.SONGS
        same, diff = [], {}
        for n in names:
            en = emerald_name(n)
            if en not in em.song_names:
                print(f'{n}: not in Emerald' + (f' (its id plays {SAME_ID[n]})' if n in SAME_ID else '')); continue
            r = compare(sap, em, n, en)
            if r: diff[n] = r
            else: same.append(n)
        for n in [x for x in SAME_ID if x in names]:
            r = compare(sap, em, n, SAME_ID[n])
            print(f'{n} vs Emerald {SAME_ID[n]} (same id): ' + ('; '.join(r) if r else 'same music'))
        print(f'{len(same)} songs the same music (only data layout may differ), {len(diff)} differ:')
        for n, r in diff.items():
            print(f'  {n}' + (f' (Emerald {emerald_name(n)})' if emerald_name(n) != n else '') + ':')
            for x in r: print('     ', x)
    elif cmd == 'convert':
        out = OUT
        if '--out' in argv: out = argv[argv.index('--out') + 1]; argv = argv[:argv.index('--out')]
        convert(argv[1:], out)
    elif cmd == 'gains':
        print(json.dumps(gains(argv[1:]), indent=1))


if __name__ == '__main__':
    main(sys.argv[1:])
