"""Black 2 code and tables that name Unova zone ids which Hoenn's maps and rooms now use (special_zones, 2026-10-18;
notes/SPECIAL_ZONES.md has all 50 Hoenn zones on such ids, what each piece of code does there and why the rest is
harmless). Zone ids are FIXED (saves keep the player's zone), so the code's lists change, never a map's zone.

1. Location evolutions (arm9 shinka_check.c: CheckEvolveSpecies 0x02020788 compares the player's zone, passed by the
   field (ov012 event_field_proclink.c: playerState->zoneId), the battle's end (ov166: the battle's zone) and the
   party screen's Rare Candy (ov165), with four u16 lists in arm9 .data; read with armdis.py, `ldr r2, =list` then
   `ldrh r1, [r2, r1]; cmp r4, r1`, so only the data changes):
     list (address)                 Black 2's zones                     Hoenn before                         now
     EVOLVE_ICEROCK_ZONES 0x0209a3e4  203 Twist Mountain (Glaceon)      LilycoveCity_Harbor                  ShoalCave_LowTideIceRoom
     EVOLVE_MOSSROCK_ZONES 0x0209a3e6 155 Pinwheel Forest (Leafeon)     (no Hoenn zone: Leafeon impossible)  PetalburgWoods
     EVOLVE_ELEC_ZONES 0x0209a3e8     195-197 Chargestone Cave          BirthIsland_Exterior, LilycoveCity_  NewMauville_Entrance,
                                      (Magnezone, Probopass)            DepartmentStore_1F / _2F             NewMauville_Inside (x2)
     EVOLVE_ELEC2_ZONES 0x0209a3ee    the same (method 28, no species)  the same                             the same as ELEC
   The places are ORAS's (Moss Rock in Petalburg Woods, Ice Rock in Shoal Cave's ice room, New Mauville's magnetic
   field); the user can pick others (notes/SPECIAL_ZONES.md). ELEC's third slot repeats New Mauville's inside rather
   than an id no zone has, so a caller that passes "no zone" can never match it.
2. Rails (arm9 zonedata.c): ZONE_RAIL_ASSIGNMENTS (0x020900e8, 28 u16 = zone:11 | rail:5; GetRailIDForZone 0x02018a28)
   made 22 Hoenn rooms load a Unova rail file and its tile attributes onto the field heap on every entry (ov036
   fieldmap.c: FieldNoGridMapper_LoadByHeader), and ZONES_WITH_RAILS (0x020900d0, 12 u16) made the Fly-position spawn
   of 6 of them a rail spawn (zone_spawn.c LoadZoneSpawnInfoCheckRail: script MapChangeFlyWarp, the warp fallback of
   SetupZoneChangeSpawn, blackout, Dive). Hoenn has no rails: each entry of a zone Hoenn uses gets zone 0x7FF (no zone
   has it; the rail number is kept), as zone_effects.py does for the camera table next to it. Grid movement never reads
   the rails (no rail camera parent), so nothing visible changes; the rooms just stop loading Unova's rails.
3. Calendar weather (a/0/9/6 file 1: u16 count, {u16 zone, u16 offset} x 24; ov012 calender.c): GetWeatherAll (arm9
   0x02032e94) gives its zones the day's weather whenever the save's season is the real one, which hoenn_season's
   summer lock (and the seasons option) make always. hoenn_world.py drops the world's outdoor zones; rooms kept
   theirs, so LilycoveCity_DepartmentStore_3F (199), LilycoveCity_House1 (206) and SlateportCity_House1 (614) had
   Unova's rain / snow on about 170, 210 and 65 days of the year, indoors (ov036 weather.c SetWeatherInit has no indoor
   check). Every zone Hoenn uses leaves the table here (entry zone 0xFFFF, as hoenn_world does; the file keeps its size).

Zones Hoenn uses: zone_effects.our_zones() (data/hoenn_zones.json + hoenn_interiors.json through version.load_json,
Littleroot's 389-396, cave variants). All versions: Sapphire, Ruby and Emerald share these zones (data/emerald/ adds
only Emerald's own maps and rooms, none on these lists). Runs anywhere after zone_effects' inputs exist (no other patch
touches these bytes); main arm9 code, so savestates made before need a cold boot for 1 and 2.
Check a build: b2tools/special_zones_check.py <HOENN_BUILD_DIR> (before its code/ and files/ go)."""
import os, sys, struct, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, os.path.dirname(HERE))
import narcio, version  # noqa: E402

_spec = importlib.util.spec_from_file_location('zone_effects_', os.path.join(HERE, 'zone_effects.py'))
_ze = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_ze)

ARM9 = 0x02004000
EVO_LISTS = 0x0209a3e4                      # ICEROCK[1], MOSSROCK[1], ELEC[3], ELEC2[3] (shinka_check.c .data)
EVO_VANILLA = (203, 155, 195, 196, 197, 195, 196, 197)
EVO_PLACES = (('ICEROCK', 'ShoalCave_LowTideIceRoom'), ('MOSSROCK', 'PetalburgWoods'),
              ('ELEC', 'NewMauville_Entrance'), ('ELEC', 'NewMauville_Inside'), ('ELEC', 'NewMauville_Inside'),
              ('ELEC2', 'NewMauville_Entrance'), ('ELEC2', 'NewMauville_Inside'), ('ELEC2', 'NewMauville_Inside'))
ZONES_WITH_RAILS, RAILS_N = 0x020900d0, 12
ZONE_RAIL_ASSIGNMENTS, ASSIGN_N = 0x020900e8, 28
NO_ZONE = 0x7FF                             # 11-bit zone field all ones: no zone has it (615 zones)
ARC_CALENDAR = 96


def zone_of(name):
    """A Hoenn map's or room's zone, as this version's data gives it."""
    m = version.load_json(os.path.join(ROOT, 'data', 'hoenn_zones.json'))['maps'].get(name)
    if m: return m['zone']
    r = version.load_json(os.path.join(ROOT, 'data', 'hoenn_interiors.json'))['rooms'].get(name)
    assert r and 'zone' in r, f'special_zones: no zone for {name}'
    return r['zone']


def apply(files):
    """3. the calendar: no entry for a zone Hoenn uses."""
    ours, _ = _ze.our_zones()
    cal = narcio.load(files, ARC_CALENDAR)
    t = bytearray(cal[1]); n = struct.unpack_from('<H', t, 0)[0]
    assert len(t) >= 2 + 4 * n and n == 24, f'special_zones: a/0/9/6 file 1 has {n} entries, Black 2 has 24'
    dropped = []
    for i in range(n):
        z = struct.unpack_from('<H', t, 2 + 4 * i)[0]
        if z in ours:
            dropped.append(z); struct.pack_into('<H', t, 2 + 4 * i, 0xFFFF)
    if dropped:
        cal[1] = bytes(t); narcio.save(files, ARC_CALENDAR, cal)
    return f'special_zones: calendar weather removed for zones {dropped} (hoenn_world drops the outdoor ones first)'


def apply_code(code):
    ours, _ = _ze.our_zones()
    p = os.path.join(code, 'arm9.bin')
    a = bytearray(open(p, 'rb').read())
    done = []
    # 1. location evolutions
    o = EVO_LISTS - ARM9
    new = tuple(zone_of(n) for _, n in EVO_PLACES)
    have = struct.unpack_from('<8H', a, o)
    if have != new:
        assert have == EVO_VANILLA, f'special_zones: evolution zone lists at {EVO_LISTS:#x} are {have}, not Black 2\'s'
        struct.pack_into('<8H', a, o, *new)
    done.append('evolution places ' + ', '.join(f'{k} {z}' for (k, _), z in zip(EVO_PLACES, new)))
    # 2. rails
    o = ZONES_WITH_RAILS - ARM9
    for i in range(RAILS_N):
        z = struct.unpack_from('<H', a, o + 2 * i)[0]
        if z in ours:
            struct.pack_into('<H', a, o + 2 * i, NO_ZONE); done.append(f'rail spawn {z}')
    o = ZONE_RAIL_ASSIGNMENTS - ARM9
    for i in range(ASSIGN_N):
        v = struct.unpack_from('<H', a, o + 2 * i)[0]
        if (v & 0x7FF) in ours:
            struct.pack_into('<H', a, o + 2 * i, (v & 0xF800) | NO_ZONE); done.append(f'rail {v >> 11} of {v & 0x7FF}')
    if os.path.islink(p): os.unlink(p)
    open(p + '.tmp', 'wb').write(a); os.replace(p + '.tmp', p)
    return 'special_zones: ' + '; '.join(done)
