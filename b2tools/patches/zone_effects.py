"""Switch off Black 2's zone-keyed engine effects on every zone Hoenn uses (found 2026-10-06 by the specials agent in
the emulator and by the PWT research, notes/RESEARCH_PWT.md §8).

Black 2 keys these on the zone id, so a Unova zone reused for a Hoenn map or room kept them:
- a/1/0/2 file 0 (ARCID_GIMMICK_TBL): u32 zone, u32 gimmick pairs. Seen: zone 563 (Weather Institute) drew Plasma
  Frigate floor panels and beams.
- a/1/4/9 file 0 (ARCID_MAPEFF_SKILL_TBL): u16 zone, u16 value pairs. Seen: zone 591 (Pokémon School) pitch dark
  with a small lit circle (Flash darkness).
- a/0/8/0 file 29: u16 zone, u16 id pairs (meaning not settled; Unova-specific per zone, so off for Hoenn zones).
- a/1/3/3 (ISS city sound units): u32 zone at offset 0 (Unova city crowd noise; Fortree, Rustboro, Verdanturf...).
- arm9 ZONE_CAMERA_ASSIGNMENTS (0x020900ac): 9 u16 = zone:11 | camera:5 (forced cameras: Route 103, Route 122, ...).
- arm9 VERSION_SPECIFIC_ZONES (0x0209a348): 3 u16 pairs swapped by version (326 <-> 551 = Route 103 <-> Route 122).
- ov012 script plugins (src/ov012/script_plugin.c): per-zone lists that load extra script-command overlays (Plasma
  Frigate, Pokémon League, Battle Subway, Pal Park ...). The Pokémon Center list is kept for our Centers' 1F zones
  (Black 2's own Center zones: the nurse and PC need it).
Every entry naming one of our zones gets an id no zone has (0xFFFF; 0x7FF in the 11-bit camera field). File sizes
never change (savestates depend on the ROM layout). PWT zones 191-193 are not ours yet (notes/DECISIONS.md)."""
import os, sys, json, struct, glob
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import narcio, version

ROOT = os.path.join(os.path.dirname(__file__), '..', '..')
NONE16 = 0xFFFF
OV012 = 0x021503c0      # ov012 base address (extract/b2_us/arm9_overlays/overlays.yaml)
PLUGIN_TABLE, PLUGINS = 0x0216c1ac, 17   # SCRIPT_PLUGIN_TABLE: {commands, u16 *zones, u32 count, s32 ov0, s32 ov1}
OV_POKEMON_CENTER = 65                  # the Pokémon Center plugin's overlay (script_plugin.c)

def our_zones():
    # (emerald_caves 2026-10-12: version.load_json, so an Emerald build also clears Black 2's entries of the zones Emerald's
    # own maps and rooms took (data/emerald/: Challenger's Cave 352-354 are dark in Black 2's table); Sapphire and Ruby
    # have no such overlay: the same zones as before)
    z = {m['zone'] for m in version.load_json(os.path.join(ROOT, 'data', 'hoenn_zones.json'))['maps'].values()}
    rooms = version.load_json(os.path.join(ROOT, 'data', 'hoenn_interiors.json'))['rooms']
    z |= {r['zone'] for r in rooms.values() if 'zone' in r} | set(range(389, 397))
    for f in version.overlay(os.path.join(ROOT, 'data', 'interiors'), '*.json'):   # zone copies of a cave (gen_caves
        z |= {v['zone'] for v in json.load(open(f)).get('variants', [])}      # "variants": Altering Cave's tables)
    centers_1f = {r['zone'] for n, r in rooms.items() if n.endswith('_PokemonCenter_1F') and 'zone' in r}
    return z - {191, 192, 193}, centers_1f

def _pairs(data, fmt, ours, done, what):
    data = bytearray(data); size = struct.calcsize(fmt)
    for o in range(0, len(data) - size + 1, size):
        zone, val = struct.unpack_from(fmt, data, o)
        if zone in ours:
            struct.pack_into(fmt, data, o, NONE16, val); done.append(f'{what} {zone}')
    return bytes(data)

DARK = 1                # a/1/4/9 value: bit 0 = dark, Flash allowed (FLD_FLASH_ALLOW; GetZoneFlashFlags, ov012 zone_change.c)

def dark_zones():
    """Hoenn zones that are dark in Sapphire (map header requires_flash): data/interiors/<zone>.json "dark": true
    (converter/gen_caves.py). Opt-in: a zone is only dark when its json says so."""
    out = []
    for f in version.overlay(os.path.join(ROOT, 'data', 'interiors'), '*.json'):     # (+ data/interiors/ruby/ in Ruby)
        j = json.load(open(f))
        if j.get('dark'): out.append(j['zone'])
    return out

def _dark(data, ours, done):
    """Write a dark entry for every Hoenn dark zone into the table, keeping its size (the game reads it once at boot
    into g_ZoneDataSystem: count = entries, GetZoneFlashFlags scans them): first the entries cleared above (Unova zones
    now used by Hoenn), then entries of Unova zones Hoenn doesn't use."""
    data = bytearray(data)
    want = dark_zones()
    n = len(data) // 4
    free = [i for i in range(n) if struct.unpack_from('<H', data, 4 * i)[0] == NONE16]
    free += [i for i in range(n) if i not in free and struct.unpack_from('<H', data, 4 * i)[0] not in ours]
    assert len(want) <= len(free), f'a/1/4/9 holds {n} dark zones, {len(want)} wanted: the file would have to grow'
    for z, i in zip(want, free):
        struct.pack_into('<HH', data, 4 * i, z, DARK); done.append(f'dark Hoenn zone {z} (entry {i})')
    return bytes(data)

def apply(files):
    ours, _ = our_zones(); done = []
    g = narcio.load(files, 102); g[0] = _pairs(g[0], '<II', ours, done, 'gimmick'); narcio.save(files, 102, g)
    m = narcio.load(files, 149); m[0] = _pairs(m[0], '<HH', ours, done, 'dark'); m[0] = _dark(m[0], ours, done)
    narcio.save(files, 149, m)
    f = narcio.load(files, 80); f[29] = _pairs(f[29], '<HH', ours, done, 'a/0/8/0#29'); narcio.save(files, 80, f)
    c = narcio.load(files, 133)
    for i, u in enumerate(c):
        if struct.unpack_from('<I', u, 0)[0] in ours:
            done.append(f'city sound {struct.unpack_from("<I", u, 0)[0]}'); c[i] = struct.pack('<I', NONE16) + u[4:]
    narcio.save(files, 133, c)
    return f'{len(done)} entries off: ' + ', '.join(done)

def apply_code(code):
    ours, centers_1f = our_zones(); done = []
    # arm9 tables
    p = os.path.join(code, 'arm9.bin'); a = bytearray(open(p, 'rb').read()); base = 0x02004000
    o = 0x020900ac - base
    for i in range(9):
        v = struct.unpack_from('<H', a, o + 2 * i)[0]
        if (v & 0x7FF) in ours:
            done.append(f'camera {v & 0x7FF}'); struct.pack_into('<H', a, o + 2 * i, (v & 0xF800) | 0x7FF)
    o = 0x0209a348 - base
    assert struct.unpack_from('<6H', a, o) == (0, 424, 294, 295, 326, 551), 'VERSION_SPECIFIC_ZONES moved?'
    for i in range(3):
        x, y = struct.unpack_from('<HH', a, o + 4 * i)
        if x in ours or y in ours:
            done.append(f'version swap {x}<->{y}'); struct.pack_into('<HH', a, o + 4 * i, NONE16, NONE16)
    if os.path.islink(p): os.unlink(p)
    open(p, 'wb').write(a)
    # ov012 plugin zone lists, through SCRIPT_PLUGIN_TABLE's own pointers (entry 0 is empty)
    p = os.path.join(code, 'arm9_ov012.bin'); ov = bytearray(open(p, 'rb').read())
    for e in range(1, PLUGINS):
        _, zp, n, ov0, _ = struct.unpack_from('<IIIii', ov, PLUGIN_TABLE - OV012 + 20 * e)
        assert OV012 <= zp < OV012 + len(ov) and 0 < n < 64, f'plugin table entry {e} unexpected'
        for i in range(n):
            at = zp - OV012 + 2 * i; z = struct.unpack_from('<H', ov, at)[0]
            if z in ours and not (ov0 == OV_POKEMON_CENTER and z in centers_1f):
                struct.pack_into('<H', ov, at, NONE16); done.append(f'plugin(ov{ov0}) {z}')
    flash = flash_command(ov)
    banner = keep_banner(ov, code)
    if os.path.islink(p): os.unlink(p)
    open(p, 'wb').write(ov)
    return f'{len(done)} off: ' + ', '.join(done) + '; ' + flash + '; ' + banner

# ---- script darkness: Sapphire's flash levels (setflashradius / animateflash, Dewford Gym) -------------------------
# Black 2's darkness is ov036's FieldFlash (field->skillMapEff->flash, 32 bytes: +0 G3D mask model drawn at the camera,
# +4 FieldFlashAnimation {fx32 scale, u8 alpha, u16 frame, u16 frames, fx32 start, fx32 delta, s16 alpha start,
# s16 alpha delta}, +28 state (1 dark, 2 animating, 3 done), +30 request (4 = none)). The field creates it only for an
# a/1/4/9 zone (FieldSkillMapEff_SetupFlash) and only sets two sizes: dark 3.0 (func_ov036_021c1d14) and Flash 10.625
# (func_ov036_021c1d30, 15 frames); no script command touches it (ov012 hiden_event.c EventFlash_Callback is its only
# user). The mask's on-screen size is proportional to the scale (FieldFlashG3D_Draw: model at the camera, scaled
# (s, s*|view dir y|, 4)); scale 0 draws nothing.
# New command 0x1C9 = HoennFlashScale scale, frames (both "any": constant or work; src/include/hoenn_story.inc
# h_flash_scale): scale in 1/256 (768 = Black 2's dark cave, 0 = no darkness), at once (frames 0) or grown over
# `frames` field frames by Black 2's own FieldFlashAnimation. A zone outside a/1/4/9 gets a FieldFlash created on the
# first nonzero call (FieldFlash_Create with the field's heap; FieldSkillMapEff_Free frees it with the field), so a
# script-dark room needs no table entry and the other dark caves stay exactly as they were. It needs the field: call
# it from MapScript 3/4 (field load) or a normal script, never from a zone init (MapScript 2 runs before the field).
# Where: the body of s01C9_NDemoStart (ov012 0x0215F440, 104 bytes), which no script uses (Black 2's a/0/5/6 and
# ours: checked with the decomp's macro names; its table entry stays). EVCMD_PERM_TABLE[0x1C9] 1 -> 3 so map scripts
# (feature level 1) may call it. ov012 keeps its compressed size (below), so no ROM file moves; but ov012 stays resident,
# so a savestate made from an older ROM keeps the old NDemoStart: Dewford Gym hangs at its door there (cold-boot states
# of the new ROM work; notes/TESTING.md "Overlays and old savestates").
NDEMO_START, NDEMO_END = 0x0215F440, 0x0215F4A8
NDEMO_VANILLA = bytes.fromhex('f0b583b00c1c051c201cf5f79bfe0190201cf5f78bfe0290281cb6f6c5fa0006070e281cb6f6c0fa0006060e281cb6f6bbfa051c0720f4f705fe0a48ddf6c6fc029b381c311c2a1c009496f0a9fa011c02d103b00120f0bd0198f4f7f1f9012003b0f0bd9b000000')
EVCMD_PERM_TABLE, FLASH_CMD = 0x0216B1F0, 0x1C9
ScriptReadAny = 0x02154910                                 # ov012
FieldFlash_Create, FieldFlashAnimation_Set = 0x021C1BC4, 0x021C1C88   # ov036 (loaded whenever a field exists)

def flash_command_code():
    import importlib.util
    spec = importlib.util.spec_from_file_location('exp_share_', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'exp_share.py'))
    es = importlib.util.module_from_spec(spec); spec.loader.exec_module(es)
    t = es.Thumb(NDEMO_START)
    str_off = lambda rd, rn, off: t.h(0x6000 | off >> 2 << 6 | rn << 3 | rd)
    strh_off = lambda rd, rn, off: t.h(0x8000 | off >> 1 << 6 | rn << 3 | rd)
    t.push([4, 5, 6, 7]); t.h(0xB083)                       # sub sp, #12 (stack 8-aligned)
    t.mov(5, 0); t.mov(4, 1)                                # r5 vm, r4 env
    t.bl(ScriptReadAny); t.mov(6, 0)                        # r6 scale (1/256)
    t.mov(0, 5); t.mov(1, 4); t.bl(ScriptReadAny); t.mov(7, 0)   # r7 frames
    t.ldr_off(0, 4, 32); t.ldr_off(0, 0, 4)                 # FieldScriptEnv_GetGameSystem
    t.ldr_off(5, 0, 32)                                     # GSYS_GetField
    t.cmp(5, 0); t.beq('end')
    t.mov(4, 5); t.addi(4, 176); t.ldr_off(4, 4, 0)         # Field_GetSkillMapEff
    t.ldr_off(0, 4, 0)                                      # FieldSkillMapEff_GetFlash
    t.cmp(0, 0); t.bne('have')
    t.cmp(6, 0); t.beq('end')                               # no darkness wanted and none there
    t.ldrh_off(0, 5, 0)                                     # Field_GetHeapID
    t.bl(FieldFlash_Create); str_off(0, 4, 0)               # (state 0, request 4, scale 0)
    t.label('have'); t.mov(4, 0)
    t.adds(0, 4, 4); t.ldr_off(1, 4, 4); t.lsls(2, 6, 4); t.movs(3, 31)
    t.str_sp(3, 0); t.str_sp(7, 4)
    t.bl(FieldFlashAnimation_Set)                           # (anim, from = now, to, alpha 31, 31, frames)
    t.movs(0, 2); t.cmp(7, 0); t.bne('state')
    t.lsls(1, 6, 4); str_off(1, 4, 4); t.movs(0, 1)         # frames 0: the new scale at once, state dark
    t.label('state'); strh_off(0, 4, 28)
    t.movs(0, 4); strh_off(0, 4, 30)                        # no pending request (a field load's dark/lit init)
    t.label("end"); t.movs(0, 0); t.h(0xB003); t.pop([4, 5, 6, 7])
    code = t.assemble()
    assert len(code) <= NDEMO_END - NDEMO_START, len(code)
    return code + bytes(NDEMO_END - NDEMO_START - len(code))

# s01CB_NDemoReadyTalkMotion (0x0215F4A8, 28 bytes, also used by no script) becomes `return FALSE`: with it, ov012
# compresses to exactly the v13.1 size (dsd: 94584 bytes, measured 2026-10-07; the command alone made it 94596), so
# the ROM's file table and overlay table stay those of the shared savestates.
NDEMO_TALK, NDEMO_TALK_VANILLA = 0x0215F4A8, bytes.fromhex('10b50c1c201cf5f769fe201cf5f75afeb7f61afb96f026fc002010bd')

def flash_command(ov):
    o = NDEMO_START - OV012
    new = flash_command_code()
    assert bytes(ov[o:o + len(new)]) in (NDEMO_VANILLA, new), 's01C9_NDemoStart is not Black 2\'s'
    ov[o:o + len(new)] = new
    ov[EVCMD_PERM_TABLE - OV012 + FLASH_CMD] = 3
    o, n = NDEMO_TALK - OV012, len(NDEMO_TALK_VANILLA)
    stub = bytes.fromhex('00207047') + bytes(n - 4)                  # movs r0, #0; bx lr
    assert bytes(ov[o:o + n]) in (NDEMO_TALK_VANILLA, stub), 's01CB_NDemoReadyTalkMotion is not Black 2\'s'
    ov[o:o + n] = stub                                               # (its last 24 bytes: keep_banner's hook)
    return f'HoennFlashScale = command {FLASH_CMD:#x} ({len(new.rstrip(bytes(1)))} B at {NDEMO_START:#x}, map scripts allowed; 0x1cb a no-op)'

# ---- the place-name banner through a zone-entry scene (fixes_v151, 2026-10-08) -------------------------------------
# Black 2 closes the banner whenever the field's event check starts ANY event: ov036 FieldEventProvider_Grid
# (0x0218185c) calls func_ov036_021b5168(Field_GetPlaceName(field)) as soon as FieldEventProvider_Grid_CheckForEvent
# returns one (talk, trigger, scene condition, reserved script ...); 021b5168 resets the banner's state and clears its
# two show requests (+80 walking-in, +84 map change / Fly). So a scene condition that runs on every zone entry (ch7's
# invisible Kecleons on Routes 119/120 and in Fortree: they have to be hidden each time the people are spawned) closed
# the banner before it showed, also after Fly. No script command avoids it (the script runs as an event either way).
# The hide call becomes KeepBannerHide: it skips the hide while map-local flag FLAG_KEEP_BANNER (0x61; 0-0x63 are
# cleared by every zone init: FieldScript_CallOnZoneInit -> FieldScript_ResetMapLocalEvents) is set, else hides as
# before. A zone sets it in its zone init (src/include/hoenn_story.inc h_keep_banner) and its entry scene clears it
# first thing (h_keep_banner_end), so every later script closes the banner as in Black 2.
# Call site (FieldEventProvider_Grid, r5 = the GameSystem, r4 = the field; 10 bytes):
#   adds r0, r4, #0; bl Field_GetPlaceName; bl func_ov036_021b5168
#   -> ldr r0, [r5, #28] (GSYS_GetGameData); bl KeepBannerHide; nop; nop
# KeepBannerHide (24 bytes): the tail of s01CB_NDemoReadyTalkMotion after flash_command's 4-byte `return FALSE` stub
# (ov012, resident while a field exists; no script uses the command). FieldEventProvider_NoGrid (rail maps) and
# _UnionRoom are left alone: Hoenn has neither.
OV036 = 0x0217F600
KEEP_CALL, KEEP_CALL_VANILLA = 0x02181890, bytes.fromhex('201cfef763fe33f067fc')
KEEP_HOOK = NDEMO_TALK + 4
FLAG_KEEP_BANNER = 0x61
GameData_GetEventWork, EventWork_FlagGet, PlaceName_Hide = 0x02017394, 0x020191AC, 0x021B5168   # arm9, arm9, ov036

def keep_banner(ov, code):
    import importlib.util
    spec = importlib.util.spec_from_file_location('exp_share_', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'exp_share.py'))
    es = importlib.util.module_from_spec(spec); spec.loader.exec_module(es)
    t = es.Thumb(KEEP_HOOK)                       # in: r0 = GameData; the caller's r4 = Field (callee-saved)
    t.push([3])                                   # push {r3, lr}: the stack stays 8-aligned
    t.bl(GameData_GetEventWork)
    t.movs(1, FLAG_KEEP_BANNER); t.bl(EventWork_FlagGet)
    t.cmp(0, 0); t.bne('keep')
    t.ldr_off(0, 4, 48)                           # Field_GetPlaceName: field->placeName (+48)
    t.bl(PlaceName_Hide)
    t.label('keep'); t.pop([3])
    hook = t.assemble()
    o, n = KEEP_HOOK - OV012, NDEMO_TALK + len(NDEMO_TALK_VANILLA) - KEEP_HOOK
    assert len(hook) <= n, len(hook)
    hook += bytes(n - len(hook))
    assert bytes(ov[o:o + n]) in (bytes(n), hook), 'the tail of s01CB_NDemoReadyTalkMotion is in use'
    ov[o:o + n] = hook
    c = es.Thumb(KEEP_CALL)
    c.ldr_off(0, 5, 28); c.bl(KEEP_HOOK); c.nop(); c.nop()
    call = c.assemble()
    p = os.path.join(code, 'arm9_ov036.bin'); d = bytearray(open(p, 'rb').read())
    at = KEEP_CALL - OV036
    assert bytes(d[at:at + len(call)]) in (KEEP_CALL_VANILLA, call), f'FieldEventProvider_Grid {KEEP_CALL:#x}: unexpected {bytes(d[at:at + 10]).hex()}'
    d[at:at + len(call)] = call
    if os.path.islink(p): os.unlink(p)
    open(p + '.tmp', 'wb').write(d); os.replace(p + '.tmp', p)
    return f'banner kept through zone-entry scenes while flag {FLAG_KEEP_BANNER:#x} is set (KeepBannerHide {len(t.out)} B at {KEEP_HOOK:#x})'
