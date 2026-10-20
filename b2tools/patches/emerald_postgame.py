"""Pokémon Emerald NDS post-game: the abnormal weather's look (emerald_ch12_13, 2026-10-12; notes/EMERALD_STORY.md
"Ch12-13 built"). HOENN_VERSION=emerald only: Sapphire and Ruby builds return before touching anything. List it after
`weather` and `emerald_mech` (story_build.sh / rebuild_slice.sh: after emerald_mech).

Emerald's Weather Institute scientist picks one of 16 route spots (CreateAbnormalWeatherEvent): the route gets a
drought (8 Terra Cave spots: Routes 114, 115, 116, 118, a cave mouth opens in the rock) or a downpour (8 Marine Cave
spots: Routes 105, 125, 127, 129, rough water to dive in) until 1000 steps were taken or Kyogre / Groudon is caught or
beaten. The scripts are src/field_scripts/scenes/emerald/abnormal_weather.inc (+ the Weather Institute, the caves and the
routes' map scripts); this patch gives the engine side, emerald_postgame.c compiled twice:

  A. arm9 0x02033048-0x020330C8 = GetRoute7WeatherIfApplicable + GetBirthdayZoneWeather (128 B). GetWeatherAll (arm9
     0x02032e94) asks, in order: GetDefaultWeatherValue (a stub), GetEntralinkWeatherIfApplicable (Sapphire / Ruby:
     patches/weather.py; Emerald: emerald_mech.c EM_ZoneWeather, the crisis), Route 7's weather, the birthday weather,
     then the calendar / zone header; 0xFFFF = ask on. Route 7's question (bl at 0x02032ed6, its only caller) now goes
     to EM_AbnormalWeather; the birthday question (bl at 0x02032eea, its only caller) becomes `adds r0, r7, #0` (r7 is
     0xFFFF there: "no answer"). Both answered only for Unova zones (Route 7's own zone; the player's birthday zone),
     which no Hoenn build reaches.
  B. ov012 0x02154d10-0x02154d9c = MapReplace_ResolvePatch + MapReplace_GetEventByCond (140 B, GetEventByCond's only
     caller is ResolvePatch, ResolvePatch's only caller MapReplace_Patch at 0x02154b72, whose bl keeps the entry address):
     EM_ResolvePatch = Black 2's rule (decomp ov012/map_replace.c) plus conditions 0x81-0x90: the entry's second chunk
     while VAR_ABNORMAL_WEATHER_LOCATION is spot (condition & 0x7F). b2tools/world.py builds each spot's cells from that
     spot's layout (data/emerald/hoenn_world.json alt_layouts "RouteNNN_AWk", data/emerald/hoenn_map_additions.json
     LAYOUT_ROUTENNN_AW_k = Emerald's setmetatile edits of data/scripts/abnormal_weather.inc), patches/hoenn_world.py
     writes the a/0/1/0 entries with the alt's "cond". Map replacements are applied when a matrix loads (warps, fly, a
     map change), so the mouth / rough water shows from the next map load (Emerald draws it on the route's load too).
Both read only VAR_ABNORMAL_WEATHER_LOCATION; the scripts end the event by clearing it (1000 steps, Kyogre / Groudon:
src/field_scripts/scenes/emerald/abnormal_weather.inc). patches/dive.py's Emerald records of the Marine spots read it too.
Main arm9 and ov012 code: savestates made before need a cold boot.
(The 1000 steps: the scripts' AW_STEPS; HOENN_TEST_AW_STEPS=<n> in a test build.)"""
import os, re, sys, json, struct, subprocess, tempfile, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, os.path.dirname(HERE))
import version  # noqa: E402

LLVM = '/opt/homebrew/opt/llvm/bin'
ARM9, OV012 = 0x02004000, 0x021503C0
PART_A = (0x02033048, 0x020330C8)              # GetRoute7WeatherIfApplicable, GetBirthdayZoneWeather
PART_B = (0x02154D10, 0x02154D9C)              # MapReplace_ResolvePatch, MapReplace_GetEventByCond
ROUTE7_CALL, BIRTHDAY_CALL = 0x02032ED6, 0x02032EEA   # GetWeatherAll's calls
EVENT_TABLE = 0x0216C300                       # ov012 EVENT_MAP_REPLACE_TABLE (6-byte entries, condition first)
# the 16 spots in pokeemerald's order (include/constants/weather.h ABNORMAL_WEATHER_*): spot k = 1..16 is route
# ROUTES[(k - 1) // 2]; 1-8 Terra Cave (drought), 9-16 Marine Cave (downpour)
ROUTES = ['Route114', 'Route115', 'Route116', 'Route118', 'Route105', 'Route125', 'Route127', 'Route129']

def _roamers():
    spec = importlib.util.spec_from_file_location('roamers_', os.path.join(HERE, 'roamers.py'))
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod

def _hoenn_h(name):
    m = re.search(rf'^#define {name}\s+(\w+)', open(os.path.join(ROOT, 'src', 'include', 'hoenn.h')).read(), re.M)
    return int(m.group(1), 0)

def route_zones():
    """The zone of each of the 8 routes in the world (HOENN_WORLD_DIR or the Emerald world): one each (the weather
    rule compares one zone per route; a route split into more zones would need the table back)."""
    wd = os.environ.get('HOENN_WORLD_DIR') or version.world_dir()
    zones = json.load(open(os.path.join(wd, 'world.json')))['zones']
    out = []
    for m in ROUTES:
        zs = sorted(int(z) for z, v in zones.items() if m in v.get('maps', []))
        assert len(zs) == 1, f'{m}: zones {zs} (emerald_postgame.c kAwZone holds one per route)'
        out += zs
    return out

def data_header():
    loc = _hoenn_h('VAR_ABNORMAL_WEATHER_LOCATION')
    zt = route_zones()
    return '\n'.join([f'#define W_LOC {loc:#x}',
                      f'#define RAIN {version.table("weather", "sapphire")}      /* Sapphire NDS\'s Kyogre rainstorm */',
                      f'#define DROUGHT {version.table("weather", "ruby")}   /* Ruby NDS\'s Groudon drought */',
                      f'#define EVENT_TABLE {EVENT_TABLE:#x}',
                      'static const u16 kAwZone[8] = {' + ', '.join(map(str, zt)) + '};']) + '\n', zt

def build(part, base, workdir):
    header, zt = data_header()
    open(os.path.join(workdir, 'emerald_postgame_data.h'), 'w').write(header)
    obj = os.path.join(workdir, f'emerald_postgame_{part}.o')
    subprocess.run([f'{LLVM}/clang', '--target=thumbv5te-none-eabi', '-mthumb', '-march=armv5te', '-Os', '-ffreestanding',
                    '-fno-builtin', '-fno-jump-tables', '-fno-pic', '-fno-unwind-tables', '-fno-asynchronous-unwind-tables',
                    '-fno-exceptions', '-fno-common', '-mno-unaligned-access', '-Wall', '-Werror', f'-DPART_{part}',
                    '-I', workdir, '-c', os.path.join(HERE, 'emerald_postgame.c'), '-o', obj], check=True)
    und = subprocess.run([f'{LLVM}/llvm-nm', '--undefined-only', obj], capture_output=True, text=True, check=True).stdout.split()
    assert not und, f'emerald_postgame.c needs {und}: call Black 2 functions by address only'
    blob, sym = _roamers().link(obj, base)
    return blob, sym, zt

def _load(code, name):
    p = os.path.join(code, name); return p, bytearray(open(p, 'rb').read())

def _save(p, d):
    if os.path.islink(p): os.unlink(p)
    open(p + '.tmp', 'wb').write(d); os.replace(p + '.tmp', p)

def _vanilla(name, base, a, b):
    return open(os.path.join(ROOT, 'external', 'pokebw2', 'build', 'b2_us', 'build', name), 'rb').read()[a - base:b - base]

def _fairy_symbol(code, name):
    """An ITCM function of fairy.py (<code>/fairy_symbols.json, Thumb address | 1), or None without fairy."""
    p = os.path.join(code, 'fairy_symbols.json')
    return json.load(open(p)).get(name) if os.path.exists(p) else None

def apply_code(code):
    if not version.is_emerald():
        return f'{version.NAME}: nothing (Emerald only)'
    bl = _roamers()._bl
    with tempfile.TemporaryDirectory(dir=code) as tmp:
        a, sa, zt = build('A', PART_A[0], tmp)
        b, sb, _ = build('B', PART_B[0], tmp)
    assert len(a) <= PART_A[1] - PART_A[0], f'part A {len(a)} B > {PART_A[1] - PART_A[0]}'
    assert len(b) <= PART_B[1] - PART_B[0], f'part B {len(b)} B > {PART_B[1] - PART_B[0]}'
    assert sb['EM_ResolvePatch'] & ~1 == PART_B[0], 'EM_ResolvePatch must start part B (MapReplace_Patch calls it there)'
    p9, arm9 = _load(code, 'arm9.bin')
    assert bytes(arm9[PART_A[0] - ARM9:PART_A[1] - ARM9]) == _vanilla('arm9.bin', ARM9, *PART_A), 'arm9 part A: not Black 2\'s code'
    assert bytes(arm9[ROUTE7_CALL - ARM9:ROUTE7_CALL - ARM9 + 4]) == bl(ROUTE7_CALL, PART_A[0]), 'GetWeatherAll: not Black 2\'s Route 7 call'
    # (seasons2) the birthday call is Black 2's, or fairy.py's Season_Snow (the winter snowfall; it answers no birthday
    # weather in Emerald: SNOW_CHAIN 0), which stays
    snow = _fairy_symbol(code, 'Season_Snow')
    cur = bytes(arm9[BIRTHDAY_CALL - ARM9:BIRTHDAY_CALL - ARM9 + 4])
    assert cur == bl(BIRTHDAY_CALL, 0x02033084) or (snow and cur == bl(BIRTHDAY_CALL, snow & ~1)), \
        'GetWeatherAll: not Black 2\'s birthday call (nor fairy.py\'s Season_Snow)'
    arm9[PART_A[0] - ARM9:PART_A[1] - ARM9] = a + bytes(PART_A[1] - PART_A[0] - len(a))
    arm9[ROUTE7_CALL - ARM9:ROUTE7_CALL - ARM9 + 4] = bl(ROUTE7_CALL, sa['EM_AbnormalWeather'] & ~1)
    if cur == bl(BIRTHDAY_CALL, 0x02033084):
        arm9[BIRTHDAY_CALL - ARM9:BIRTHDAY_CALL - ARM9 + 4] = bytes.fromhex('381cc046')    # adds r0, r7, #0; nop
    _save(p9, arm9)
    p12, ov12 = _load(code, 'arm9_ov012.bin')
    assert bytes(ov12[PART_B[0] - OV012:PART_B[1] - OV012]) == _vanilla('arm9_ov012.bin', OV012, *PART_B), 'ov012 part B: not Black 2\'s code'
    ov12[PART_B[0] - OV012:PART_B[1] - OV012] = b + bytes(PART_B[1] - PART_B[0] - len(b))
    _save(p12, ov12)
    return (f'emerald_postgame: abnormal weather {len(a)} of {PART_A[1] - PART_A[0]} B at arm9 {PART_A[0]:#x} (route zones '
            f'{zt}, rain {version.table("weather", "sapphire")}, drought {version.table("weather", "ruby")}), map replace '
            f'conditions 0x81-0x90: {len(b)} of {PART_B[1] - PART_B[0]} B at ov012 {PART_B[0]:#x}')

if __name__ == '__main__':          # python3 emerald_postgame.py: the two parts' sizes (needs a world.json)
    with tempfile.TemporaryDirectory() as tmp:
        for part, (lo, hi) in (('A', PART_A), ('B', PART_B)):
            blob, sym, _ = build(part, lo, tmp)
            print(part, len(blob), 'of', hi - lo, {k: hex(v) for k, v in sym.items() if k.startswith('EM_')})
