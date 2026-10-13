"""Kyogre's weather (chapter Ch10, ch10 agent 2026-10-07; src/field_scripts/common/legendary_weather.inc has the findings).

Sapphire: once Archie has woken Kyogre (FLAG_SYS_WEATHER_CTRL, set in the Seafloor Cavern, cleared when Kyogre is calmed in
the Cave of Origin) every map from Lilycove to Sootopolis calls `setweather WEATHER_RAIN_HEAVY` in its map script.
Black 2: FieldSetWeather (script command 310) stores a weather id as the save's "now weather" and starts it, but it is
forbidden in a zone init (EVCMD_PERM_TABLE: levels 0-1 only) and every zone change runs ResetWeather (arm9 0x02032f3c),
which writes the weather of GetWeatherAll(zone) (arm9 0x02032e94) over it. So the weather has to come out of
GetWeatherAll itself. It asks, in order: GetDefaultWeatherValue (a stub: 0xFFFF), GetEntralinkWeatherIfApplicable (arm9
0x02032fb8, 144 bytes: the Entralink's own weather for zones only Unova has, never reached by a Hoenn zone), the Route 7
and birthday weathers, then the calendar / the zone header; a result other than 0xFFFF ends the search. This patch replaces
the Entralink function (same signature: gsys r0, gamedata r1, zone r2 -> weather id or 0xFFFF) with one that returns
the thunderstorm (id 6: rain, dark sky, lightning; tested: ov036's table 0x021cfb6c, ids 0 sunny, 1 snow, 2 rain, 3
sandstorm, 6 thunderstorm, 7 heavy rain, 8 diamond dust, ...) for the zones of the crisis maps while the flag is set.
Main arm9 code: savestates made before need the bytes poked into RAM (or a cold boot).

Zones: the zone of every Sapphire map that calls Common_EventScript_SetLegendaryWeather (Route 124-128, Lilycove,
Mossdeep, Sootopolis, Ever Grande), read from the world (work/world/world.json, HOENN_WORLD_DIR) by map name.
HOENN_KYOGRE_WEATHER=<id> picks another weather (default 6).
Versions (b2tools/version.py TABLE['weather']): Sapphire 6 (thunderstorm, Kyogre's heavy rain); Ruby: Groudon's drought,
which Black 2 has no weather for: the user picks a stand-in (screenshots/ruby_infra/weather_*), 0 (sunny) until then.
Same maps and flag in both (pokeruby Common_EventScript_SetLegendaryWeather only changes the weather id).
HOENN_LEGEND_WEATHER=<id> overrides either version's (HOENN_KYOGRE_WEATHER still works).

Route 119's and Route 123's day-by-day weather (v166_fixes 2026-10-12; data/hoenn_weather.json 'cycles'): the same hook
first gives those maps' zones Sapphire's cycle (pokeruby sWeatherCycleRoute119 sunny/light rain/medium rain/light rain ->
0/2/6/2, sWeatherCycleRoute123 sunny/sunny/light rain/sunny -> 0/0/2/0) by the DS clock's day: RTC_GetCachedDate +
RTC_ConvertDateToDay (days since 2000), & 3. Their ends that Sapphire keeps sunny are fixed-weather 'parts' (zones 550,
586, 608, 609; patches/fixed_weather.py). Black 2 takes a zone's weather on entering it (zone change, warp); Continue
keeps the saved weather (ov035 event_mapchange.c: no UpdateWeatherToDefault on the continue path) until the next zone
change. Tested: screenshots/v166/03_*."""
import os, sys, json, struct, importlib.util

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import version  # noqa: E402
_spec = importlib.util.spec_from_file_location('exp_share_', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'exp_share.py'))
_es = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_es)
Thumb, _patch, _load, _save, _vanilla = _es.Thumb, _es._patch, _es._load, _es._save, _es._vanilla

ARM9 = 0x02004000
HOOK = (0x02032FB8, 0x02033048)                 # GetEntralinkWeatherIfApplicable
GameData_GetEventWork, EventWork_FlagGet = 0x02017394, 0x020191AC
FLAG_SYS_WEATHER_CTRL = 903                     # data/story_ids.json
CRISIS_MAPS = ('Route124', 'Route125', 'Route126', 'Route127', 'Route128', 'LilycoveCity', 'MossdeepCity', 'SootopolisCity',
               'EverGrandeCity')
THUNDERSTORM = 6                                # Sapphire's (version.py _TABLE['sapphire']['weather'])

def crisis_zones():
    wd = os.environ.get('HOENN_WORLD_DIR') or os.path.join(ROOT, 'work', 'world')
    w = json.load(open(os.path.join(wd, 'world.json')))
    return sorted(int(z) for z, v in w['zones'].items() if any(m in CRISIS_MAPS for m in v.get('maps', [])))

RTC_GetCachedDate, RTC_ConvertDateToDay = 0x0204424C, 0x0207D0B4   # gfl/rtc_cache.c; SDK RTC_ConvertDateToDay
                                                                # (func_0207d0b4: days since 2000-01-01, -1 if invalid)

def cycle_zones():
    """[(zone, [4 Black 2 weathers])] of Sapphire's day-by-day weather cycles (data/hoenn_weather.json 'cycles'): the
    map's own zone; its 'parts' (the ends Sapphire keeps sunny) have zones of their own and keep their header's."""
    wd = os.environ.get('HOENN_WORLD_DIR') or os.path.join(ROOT, 'work', 'world')
    w = json.load(open(os.path.join(wd, 'world.json')))
    cyc = json.load(open(os.path.join(ROOT, 'data', 'hoenn_weather.json'))).get('cycles', {})
    out = []
    for m, c in cyc.items():
        if m.startswith('_'): continue
        zs = [int(z) for z, v in w['zones'].items() if m in v.get('maps', [])]
        if zs: assert len(zs) == 1, (m, zs); out.append((zs[0], c['weathers']))
    return sorted(out)

def hook(zones, weather, cycles=()):
    """GetEntralinkWeatherIfApplicable(gsys r0, gamedata r1, zone r2) -> weather or 0xFFFF:
    1. a cycling zone (Route 119/123): its weather of the day, by the clock's day (days since 2000 & 3: one step a day,
       Sapphire's UpdateWeatherPerDay adds the days passed to a 4-day counter);
    2. a crisis zone while FLAG_SYS_WEATHER_CTRL is set: the legendary's weather."""
    t = Thumb(HOOK[0])
    t.push([4, 5, 6])                                        # (16 bytes, then 16: the stack stays 8-aligned)
    t.h(0xB084)                                              # sub sp, #16 (an RTCDate)
    t.mov(4, 2); t.lsls(4, 4, 16); t.lsrs(4, 4, 16)          # r4 = the zone (a u16)
    t.mov(5, 1)                                              # r5 = gamedata
    t.ldr_lit(1, 'cyc')
    t.label('cloop')                                         # entries: u16 zone, u8 weather[4] (6 bytes), zone 0 ends
    t.ldrh_off(0, 1, 0)
    t.cmp(0, 0); t.beq('legend')
    t.cmpr(0, 4); t.beq('cycle')
    t.addi(1, 6); t.b('cloop')
    t.label('cycle')
    t.mov(5, 1)                                              # r5 = the entry
    t.h(0xA800)                                              # add r0, sp, #0
    t.bl(RTC_GetCachedDate)
    t.h(0xA800)
    t.bl(RTC_ConvertDateToDay)
    t.movs(1, 3); t.ands(0, 1)                               # the day's step 0-3
    t.addi(0, 2); t.ldrb_rr(0, 5, 0)                         # entry.weather[step]
    t.b('out')
    t.label('legend')
    t.mov(0, 5)                                              # r0 = gamedata
    t.bl(GameData_GetEventWork)
    t.ldr_lit(1, 'flag')
    t.bl(EventWork_FlagGet)
    t.cmp(0, 0); t.beq('none')
    t.ldr_lit(1, 'tab')
    t.label('loop')
    t.ldrh_off(0, 1, 0)
    t.cmp(0, 0); t.beq('none')
    t.addi(1, 2)
    t.cmpr(0, 4); t.bne('loop')
    t.movs(0, weather)
    t.b('out')
    t.label('none')
    t.ldr_lit(0, 'none_val')
    t.label('out')
    t.h(0xB004)                                              # add sp, #16
    t.pop([4, 5, 6])
    t.word('flag', FLAG_SYS_WEATHER_CTRL)
    t.word('none_val', 0xFFFF)
    t.word('tab', 0)                                         # patched below: the tables follow the literals
    t.word('cyc', 0)
    tab_at = len(t.out)
    for z in zones: t.out += struct.pack('<H', z)
    t.out += struct.pack('<H', 0)
    cyc_at = len(t.out)
    for z, ws in cycles:
        assert len(ws) == 4 and all(0 <= w < 16 for w in ws), ws
        t.out += struct.pack('<H4B', z, *ws)
    t.out += struct.pack('<H', 0)
    code = bytearray(t.assemble())
    struct.pack_into('<I', code, t.labels['tab'] - HOOK[0], HOOK[0] + tab_at)
    struct.pack_into('<I', code, t.labels['cyc'] - HOOK[0], HOOK[0] + cyc_at)
    assert len(code) <= HOOK[1] - HOOK[0], (len(code), HOOK[1] - HOOK[0])
    return bytes(code) + bytes(HOOK[1] - HOOK[0] - len(code))

def apply_code(code):
    path, d = _load(code, 'arm9.bin')
    zones = crisis_zones()
    weather = int(os.environ.get('HOENN_LEGEND_WEATHER') or os.environ.get('HOENN_KYOGRE_WEATHER') or version.TABLE['weather'])
    cycles = cycle_zones()
    blob = hook(zones, weather, cycles)
    old = _vanilla('arm9.bin', ARM9, HOOK[0], HOOK[1] - HOOK[0])
    assert old[:2] == bytes.fromhex('70b5'), old[:4].hex()    # push {r4, r5, r6, lr}: GetEntralinkWeatherIfApplicable
    _patch(d, ARM9, HOOK[0], old, blob, f'GetEntralinkWeatherIfApplicable -> {version.TABLE["legendary"].capitalize()} weather')
    _save(path, d)
    used = len(blob.rstrip(b'\0'))
    return (f'GetEntralinkWeatherIfApplicable (arm9 {HOOK[0]:#x}) -> weather {weather} while flag {FLAG_SYS_WEATHER_CTRL} is set, '
            f'zones {zones}; day-by-day cycles {cycles} ({used} of {len(blob)} B)')
