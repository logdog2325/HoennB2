"""The sound archive room for Hoenn's songs (notes/MUSIC.md "Slots"): which Black 2 sequence entries and file bytes the
Hoenn game never uses under either music option, and which Hoenn song gets which entry. Writes data/hoenn_music.json
"pool" and "slots"; run once, then the slots stay fixed (scripts name some of them: src/include/hoenn_music.inc).

    python3 music_slots.py [--check]

Pool (every name checked against the pristine archive, swan_sound_data.sdat, by b2tools/patches/hoenn_music.py):
  bgm_slots: BGM sequences whose bank and wave archive are their own, of Unova-only content: Pokestar Studios (PW_*),
             the Musical (MSL_*), Unova cutscenes (E_*, SW_DEMO_*, EV_*), and Unova places no Hoenn zone header plays
             (v15.2: 63 BGM ids in Hoenn's zones). Not taken: anything src/ names, anything in the track-muting table
             a/0/8/6, Black 2's fixed-use ids (battles, jingles, title, ending, surf, bike, dive), battle_tower's
             (WBT_*, VS_WBT, WIN_WBT, VS_SUBWAY_TRAINER, PWT VS_*_LEADER/CHAMP) and the Subway's (GATE, GEAR_STATION,
             BATTLE_SUBWAY).
  se_groups: sound effects of Unova-only scenes (Kyurem, the Plasma Frigate, Opelucid, Pokestar's audience, ...) whose
             banks and wave archives no other sequence uses: their sequence entries become BGM slots (player 0) and
             their files free bytes.
  bytes_only: files no sequence plays (the instrument library's own wave archive, 2.5 MB: the converter reads the
             decomp's pristine copy).
"""
import glob, json, os, re, sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
from sdat import SDAT, DEFAULT  # noqa: E402
import m4a_to_sseq as conv  # noqa: E402

BGM_SLOTS = [
    # Unova cutscenes / Musical / Pokestar Studios (work/agents/music_check/full/freepool.py: no zone, no src, own files)
    'SEQ_BGM_E_CHEREN', 'SEQ_BGM_E_BERU', 'SEQ_BGM_E_DOCTOR', 'SEQ_BGM_E_DOCTOR2', 'SEQ_BGM_E_N_SWAN', 'SEQ_BGM_E_SAGE',
    'SEQ_BGM_E_NEW_G_CIS', 'SEQ_BGM_E_INISHIE', 'SEQ_BGM_SW_DEMO_OPENING', 'SEQ_BGM_E_KANRANSYA', 'SEQ_BGM_MSL_DRESSUP',
    'SEQ_BGM_MSL_BEFORE', 'SEQ_BGM_MSL_01', 'SEQ_BGM_MSL_02', 'SEQ_BGM_MSL_03', 'SEQ_BGM_MSL_04', 'SEQ_BGM_E_SHIRONA',
    'SEQ_BGM_E_LEGEND_BORN_W', 'SEQ_BGM_E_EPIROGUE', 'SEQ_BGM_E_EPIROGUE_W', 'SEQ_BGM_MSL_DL_01', 'SEQ_BGM_MSL_DL_02',
    'SEQ_BGM_MSL_DL_03', 'SEQ_BGM_MSL_DL_04', 'SEQ_BGM_PW_FILMING', 'SEQ_BGM_PW_SCENARIO_01_F', 'SEQ_BGM_PW_SCENARIO_01_L',
    'SEQ_BGM_PW_SCENARIO_02_F', 'SEQ_BGM_PW_SCENARIO_02_L', 'SEQ_BGM_PW_SCENARIO_03_F', 'SEQ_BGM_PW_SCENARIO_03_L',
    'SEQ_BGM_PW_SCENARIO_04_F', 'SEQ_BGM_PW_SCENARIO_04_L', 'SEQ_BGM_PW_SCENARIO_05_F', 'SEQ_BGM_PW_SCENARIO_05_L',
    'SEQ_BGM_PW_SCENARIO_06_F', 'SEQ_BGM_PW_SCENARIO_06_L', 'SEQ_BGM_PW_SCENARIO_07_F', 'SEQ_BGM_PW_SCENARIO_07_L',
    'SEQ_BGM_PW_SCENARIO_08_F', 'SEQ_BGM_SW_DEMO_FLIGHT', 'SEQ_BGM_SW_DEMO_UNION_00', 'SEQ_BGM_SW_DEMO_UNION_01',
    'SEQ_BGM_SW_DEMO_UNION_02', 'SEQ_BGM_SW_DEMO_UNION_03B', 'SEQ_BGM_SW_DEMO_UNION_03W', 'SEQ_BGM_SW_DEMO_AJITO_SHIP',
    'SEQ_BGM_SW_DEMO_FRIGATE', 'SEQ_BGM_E_ACHROMA', 'SEQ_BGM_E_7_SAGE', 'SEQ_BGM_E_C08_ICE', 'SEQ_BGM_E_EPILOGUE',
    'SEQ_BGM_EV_GIANTHOLE_01', 'SEQ_BGM_EV_GIANTHOLE_02',
    # Unova places only Unova zone headers play (not in a/0/8/6)
    'SEQ_BGM_C_03', 'SEQ_BGM_C_10_B', 'SEQ_BGM_C_10_W', 'SEQ_BGM_H_02', 'SEQ_BGM_H_05', 'SEQ_BGM_PLEASURE_BOAT',
    'SEQ_BGM_PALACE', 'SEQ_BGM_INSECT_GYM_01', 'SEQ_BGM_SW_C_12', 'SEQ_BGM_MSL_FIELD', 'SEQ_BGM_SW_D_23', 'SEQ_BGM_SW_D_GESUI',
    'SEQ_BGM_SW_D_24_B', 'SEQ_BGM_SW_D_REGI', 'SEQ_BGM_SW_D_UMA', 'SEQ_BGM_WATER_GYM_01', 'SEQ_BGM_REZO_RIZO',
    'SEQ_BGM_KEMONOMICHI']
SE_GROUPS = ['KYUREON', 'FRIGATE', 'SOURYUCITY', 'PKWOOD_AUD', 'KYUREM', 'GEEMA', 'KUSABI_IN']
BYTES_ONLY = ['BANK_MUS_WB_SOUNDLIST', 'WAVE_MUS_WB_SOUNDLIST',
              # Unova places only Unova zone headers play, but in a/0/8/6: their ids stay, their bytes are free
              'SEQ_BGM_T_03', 'SEQ_BGM_H_01', 'SEQ_BGM_H_03', 'SEQ_BGM_H_04', 'SEQ_BGM_D_CHAMPROAD', 'SEQ_BGM_ERECTRIC_GYM_01']
# songs scripts name (src/include/hoenn_music.inc): fixed to these slots
SCRIPT_SLOTS = {'mus_encounter_may': 'SEQ_BGM_E_CHEREN', 'mus_encounter_brendan': 'SEQ_BGM_E_BERU',
                'mus_sailing': 'SEQ_BGM_E_DOCTOR',
                # src/include/hoenn_music.inc (music_more 2026-10-11): their slots as first assigned
                'mus_help': 'SEQ_BGM_C_03', 'mus_cable_car': 'SEQ_BGM_SW_D_REGI',
                'mus_encounter_elite_four': 'SEQ_SE_SW_KYUREON_01_10'}


def se_group_seqs(s, g):
    return [i for i, e in enumerate(s.info['seq']) if e and (f'_{g}' in s.name('bank', e['bank']) or f'_{g}_' in s.name('seq', i))]


def pool(s):
    """(slots: [(seq id, name, bank id, wavearc id)], free file ids) from the pristine archive; every file checked."""
    slots, files = [], set()
    bank_users = Counter(e['bank'] for e in s.info['seq'] if e)
    file_users = Counter(e['file'] for e in s.info['seq'] if e)
    wa_users = Counter(w for e in s.info['bank'] if e for w in e['wavearcs'])
    seqs = [s.index('seq', n) for n in BGM_SLOTS]
    for g in SE_GROUPS: seqs += se_group_seqs(s, g)
    for i in seqs:
        e = s.info['seq'][i]; b = s.info['bank'][e['bank']]
        assert bank_users[e['bank']] == 1 and file_users[e['file']] == 1, s.name('seq', i)
        assert len(b['wavearcs']) == 1 and wa_users[b['wavearcs'][0]] == 1, s.name('seq', i)
        w = b['wavearcs'][0]
        slots.append((i, s.name('seq', i), e['bank'], w))
        files |= {e['file'], b['file'], s.info['wavearc'][w]['file']}
    taken_seq = {x[0] for x in slots}
    taken_bank = {x[2] for x in slots}
    taken_wa = {x[3] for x in slots}
    for n in BYTES_ONLY:                  # (their entries stay as they are, pointing at bytes nothing loads)
        if n.startswith('SEQ'):
            i = s.index('seq', n); e = s.info['seq'][i]; b = s.info['bank'][e['bank']]
            assert bank_users[e['bank']] == 1 and file_users[e['file']] == 1 and len(b['wavearcs']) == 1
            files |= {e['file'], b['file'], s.info['wavearc'][b['wavearcs'][0]]['file']}
            taken_seq.add(i); taken_bank.add(e['bank']); taken_wa.add(b['wavearcs'][0])
        else:
            kind = 'bank' if n.startswith('BANK') else 'wavearc'
            j = s.index(kind, n)
            files.add(s.info[kind][j]['file'])
            (taken_bank if kind == 'bank' else taken_wa).add(j)
    # no file of the pool may be used by any entry left alone
    for i, e in enumerate(s.info['seq']):
        if e and i not in taken_seq: assert e['file'] not in files, f'seq {s.name("seq", i)} uses a pool file'
    for i, e in enumerate(s.info['bank']):
        if e and i not in taken_bank:
            assert e['file'] not in files, f'bank {s.name("bank", i)} uses a pool file'
            assert not set(e['wavearcs']) & taken_wa, f'bank {s.name("bank", i)} uses a pool wave archive'
    for i, e in enumerate(s.info['wavearc']):
        if e and i not in taken_wa: assert e['file'] not in files, f'wavearc {s.name("wavearc", i)} uses a pool file'
    return slots, files


def main(argv):
    s = SDAT(open(DEFAULT, 'rb').read())
    slots, files = pool(s)
    total = sum(s.fat[f][1] for f in files)
    print(f'{len(slots)} slots ({len(BGM_SLOTS)} BGM, {len(slots) - len(BGM_SLOTS)} SE), {len(files)} files, {total:,} B free')
    mp = json.load(open(conv.MAPPING))
    if '--check' in argv:
        return
    assign = dict(mp.get('slots', {}))
    taken = set(assign.values())
    for p in sorted(glob.glob(os.path.join(ROOT, 'data', '*', 'hoenn_music.json'))):   # a version's own songs
        taken |= set(json.load(open(p)).get('slots', {}).values())                       # (data/emerald/: 5 slots)
    names = [x[1] for x in slots]
    for song, slot in SCRIPT_SLOTS.items():
        assert assign.get(song, slot) == slot
        assign[song] = slot; taken.add(slot)
    free = [n for n in names if n not in taken]
    for song in conv.SONGS:
        if song not in assign: assign[song] = free.pop(0)
    mp['pool'] = dict(_doc='b2tools/music_slots.py: the sequence entries and file bytes the Hoenn songs use (never played '
                           'by the game under either option); checked against the pristine archive by the patch.',
                      bgm_slots=BGM_SLOTS, se_groups=SE_GROUPS, bytes_only=BYTES_ONLY)
    mp['slots'] = {k: assign[k] for k in conv.SONGS}
    txt = json.dumps(mp, indent=2, ensure_ascii=False)
    txt = re.sub(r'\{\s+"program": (\d+)\s+\}', r'{"program": \1}', txt)
    txt = re.sub(r'\{\s+"program": (\d+),\s+"drum_key": (\d+)\s+\}', r'{"program": \1, "drum_key": \2}', txt)
    txt = re.sub(r'\[\s+(\d+),\s+(\d+)\s+\]', r'[\1, \2]', txt)
    txt = re.sub(r'\[\s+(\d+)\s+\]', r'[\1]', txt)
    open(conv.MAPPING, 'w').write(txt + '\n')
    print(f'{len(conv.SONGS)} songs assigned; {len(free)} slots left')


if __name__ == '__main__':
    main(sys.argv[1:])
