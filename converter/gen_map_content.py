"""Generate every built map's simple events from Sapphire: signs and townspeople whose script only shows one
message (with lock/faceplayer/release around it), dialogue word for word (converter/gen3text.py).

    python3 gen_map_content.py      (after b2tools/world.py; reads data/sapphire/<Map>.json, pokeruby scripts)

Writes, per zone that owns the events' cells (a zone covers whole 32x32 cells, world.py):
  src/field_scripts/NNNN_auto_<Map>.s       (the zone's script file: one script per sign / NPC)
  src/field_scripts/MMMM_auto_<Map>_init.s  (the zone's map-script file, emptied: Unova's would run our scripts)
  src/text/script/TTTT_auto_<Map>.txt       (the zone's message file)
  data/hoenn_content.json                   (per map: signs/NPCs -> script ids, sprites, sign models; world.py merges it)
Skipped (later work, listed in the report): story NPCs (other commands, or a hide flag), trainers, item balls, NPCs
whose Sapphire sprite has no Black 2 match (data/sprite_map.json null), events of hand-made zones (Littleroot,
Route 101, Oldale) and events landing in a hand-made zone's cell.
"""
import os, sys, re, json, glob, collections, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..')
sys.path.insert(0, os.path.join(ROOT, 'b2tools'))
from gen3text import convert

RUBY = os.path.join(ROOT, 'external', 'pokeruby')
HAND_MADE = {'LittlerootTown', 'Route101', 'OldaleTown'}
SIMPLE_CMDS = {'lock', 'lockall', 'faceplayer', 'msgbox', 'release', 'releaseall', 'end', 'waitmessage',
               'closemessage', 'message', 'waitbuttonpress'}
SIGN_MODEL_ROUTE, SIGN_MODEL_OTHER = 154, 152       # pack-0 sign models used for Littleroot's route/house signs
# hand fixes of generated NPCs, kept on every regeneration (world.py: a settings 'move' overrides Sapphire's type)
NPC_FIXES = {
    ('Route115', 'Route115_EventScript_15092E'): {'move': 3, '_move': "Sapphire's WANDER_AROUND 1x1 never takes a step "
        "(her elevation 3 on elevation-5 ground): code 3 with no area, she only turns (v165_fixes)"},
}

def ruby_scripts(root=RUBY):
    """label -> text and label -> script lines of every .inc/.s under the decomp's data/ (pokeruby; pokeemerald in an
    Emerald run: its map scripts use the same commands, `msgbox Text, MSGBOX_NPC` / `MSGBOX_SIGN`)."""
    text, scripts = {}, {}
    for path in sorted(glob.glob(f'{root}/data/**/*.inc', recursive=True) + glob.glob(f'{root}/data/**/*.s', recursive=True)):
        label = None; cur = None
        for line in open(path, encoding='utf-8', errors='replace'):
            m = re.match(r'^(\w+):{1,2}', line)
            if m:
                label = cur = m.group(1); scripts.setdefault(cur, []); continue
            m = re.match(r'\s*\.string\s+"(.*)"', line)
            if m and label:
                text[label] = text.get(label, '') + m.group(1)
                if m.group(1).endswith('$'): label = None        # a string ends at its terminator
                continue
            if cur and line.strip() and not line.strip().startswith('@'):
                scripts[cur].append(line.split('@')[0].strip())
    return text, scripts

def simple_message(name, text, scripts):
    """The text label of a script that only shows one message, else None."""
    body = [l for l in scripts.get(name, []) if l]
    if not body: return None
    cmds = [l.split()[0].rstrip(',') for l in body]
    if not set(cmds) <= SIMPLE_CMDS or cmds.count('msgbox') + cmds.count('message') != 1: return None
    line = next(l for l in body if l.split()[0] in ('msgbox', 'message'))
    label = line.split()[1].rstrip(',')
    return label if label in text else None

# Story scenes per version (S0-2, emerald_s0 2026-10-12; notes/EMERALD_STORY.md 2.3-2.4): a scene's ScriptEntry list is
# read through the same preprocessor the assembler uses (patches/scripts.py: clang, -D HOENN_<VERSION>), so entries
# under `#ifdef HOENN_EMERALD` count in Emerald only. Sapphire and Ruby assemble the same generated files, so their
# counts must agree (main() stops otherwise); Emerald's own run (S0-1) counts with -D HOENN_EMERALD.
LLVM = '/opt/homebrew/opt/llvm/bin'
VERSION_IDS = {'sapphire': 1, 'ruby': 2, 'emerald': 3}      # b2tools/version.py GAME_VERSION (ASM_DEFINES)
_ENTRIES = {}

def scene_entry_lines(name, ver='sapphire'):
    """The ScriptEntry lines (with their // comments) of src/field_scripts/scenes/<name>.inc's SCENE_ENTRIES part as
    version `ver` assembles them: `clang -E -P -C -x assembler-with-cpp -D SCENE_ENTRIES -D HOENN_<VER>
    -D HOENN_VERSION_ID=n` (the -I paths of patches/scripts.py), so #included scene files come inline and #if /
    __has_include blocks are resolved as in the ROM. [] when the map has no scene file."""
    key = (name, ver)
    if key not in _ENTRIES:
        inc = os.path.join(ROOT, 'src', 'field_scripts', 'scenes', f'{name}.inc')
        if not os.path.exists(inc):
            _ENTRIES[key] = []
        else:
            r = subprocess.run([f'{LLVM}/clang', '-E', '-P', '-C', '-x', 'assembler-with-cpp', '-D', 'SCENE_ENTRIES',
                                '-D', f'HOENN_{ver.upper()}', '-D', f'HOENN_VERSION_ID={VERSION_IDS[ver]}',
                                '-I', os.path.join(ROOT, 'src', 'include'), '-I', os.path.join(ROOT, 'src', 'field_scripts'),
                                inc], capture_output=True, text=True)
            if r.returncode:
                raise SystemExit(f'scenes/{name}.inc ({ver}): the preprocessor failed:\n{r.stderr}')
            _ENTRIES[key] = [l for l in r.stdout.split('\n') if re.match(r'^\s*ScriptEntry\s', l)]
    return _ENTRIES[key]

def scene_count(name, ver):
    """Number of story scripts of scenes/<name>.inc in version `ver` (scene_entry_lines)."""
    return len(scene_entry_lines(name, ver))

def scene_files(name, ver='sapphire'):
    """Story scenes of an auto map (notes/STORY_PORTING.md "Scenes"): (number of story scripts, story text lines,
    has map scripts). src/field_scripts/scenes/<Map>.inc lists its ScriptEntry lines between `#ifdef SCENE_ENTRIES`
    and `#else` (they become scripts 1..n, the generated ones follow; counted as version `ver` assembles them,
    scene_entry_lines); src/text/scenes/<Map>.txt holds its lines (0..t-1, the generated ones follow);
    src/field_scripts/scenes/<Map>_init.inc is the zone's map-script table."""
    n = scene_count(name, ver)
    txt = os.path.join(ROOT, 'src', 'text', 'scenes', f'{name}.txt')
    lines = open(txt, encoding='utf-8').read().rstrip('\n').split('\n') if os.path.exists(txt) else []
    return n, lines, os.path.exists(os.path.join(ROOT, 'src', 'field_scripts', 'scenes', f'{name}_init.inc'))

def scene_sign(name, ev, ver='sapphire'):
    """Script id of a Sapphire sign with a story script (one the generator can't write) that the map's scene file
    provides: the number of the SCENE_ENTRIES `ScriptEntry` whose comment names the sign's Sapphire script label or
    its tile, `sign (x,y)` (e.g. scenes/SlateportCity.inc `ScriptEntry Story_ShipyardSign // 11: sign (23,38)`).
    The sign then gets its event and signboard model here like a generated one (npc_limit, 2026-10-07: story signs
    in data/story/*.json have no model). Numbering as scene_files: in order, with #included scene files inline."""
    lines = scene_entry_lines(name, ver)
    if not lines: return None
    for i, line in enumerate(lines, 1):
        note = line.split('//', 1)[1] if '//' in line else ''
        m = re.search(r'\bsign \((\d+),\s*(\d+)\)', note)
        if re.search(r'\b' + re.escape(ev['script']) + r'\b', note) or (m and (int(m.group(1)), int(m.group(2))) == (ev['x'], ev['y'])):
            return i
    return None

def script_block(i, msg, kind):
    if kind == 'sign':
        return f"""Script_{i}:
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    MsgPlaceSign {msg}, 2
    MsgPlaceSignClose
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt
"""
    return f"""Script_{i}:
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    ActorSetEyeToEye
    ParentActorMsg MSGFILE_SCRIPT, {msg}, 0, 0
    LastKeyWait
    ActorMsgClose
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt
"""

def scene_text(name, ver):
    """src/text/scenes/<Map>.txt, or in Emerald src/text/scenes/emerald/<Map>.txt when there is one (notes/EMERALD_STORY.md 2.3:
    Sapphire's lines at their indices, reworded lines replaced, Emerald-only lines appended)."""
    d = os.path.join(ROOT, 'src', 'text', 'scenes')
    em = os.path.join(d, 'emerald', f'{name}.txt')
    txt = em if ver == 'emerald' and os.path.exists(em) else os.path.join(d, f'{name}.txt')
    return open(txt, encoding='utf-8').read().rstrip('\n').split('\n') if os.path.exists(txt) else []

def main():
    """Sapphire (and Ruby, which assembles the same files): the shared files above. Emerald (HOENN_VERSION=emerald; S0-1,
    emerald_s0 2026-10-12, notes/EMERALD_STORY.md 2.4): the same run on Emerald's world (version.world_dir(), its zones and
    maps through world.py) with pokeemerald's events and text: data/sapphire/emerald/<Map>.json (HOENN_VERSION=emerald
    python3 sapphire_data.py ../external/pokeemerald <Map> ...), pokeemerald's scripts, data/emerald/sprite_map.json over
    Sapphire's rows (+ its "_gfx_alias": a pokeemerald graphics id -> the Sapphire id with the same picture), the Emerald
    item balls (data/emerald/hoenn_items.json) and every scene's ScriptEntry list as an Emerald build assembles it (S0-2).
    Writes only Emerald's own files: src/field_scripts/emerald/NNNN_auto_<Map>.s and _init.s, src/text/script/emerald/
    NNNN_auto_<Map>.txt (a zone whose file would equal the shared one gets none: the overlay rule) and
    data/emerald/hoenn_content.json (whole: it replaces data/hoenn_content.json for Emerald's world.py, version.overlay_file;
    no deep merge, the event labels are pokeemerald's)."""
    import world as W, zoneheaders, version as V
    ver = 'emerald' if V.is_emerald() else 'sapphire'
    em = ver == 'emerald'
    wdir = os.environ.get('HOENN_WORLD_DIR') or os.path.join(ROOT, 'work', 'world')
    if em:
        wdir = V.world_dir()
        if not os.path.exists(os.path.join(wdir, 'world.json')):
            raise SystemExit(f'Emerald mode reads Emerald\'s world ({wdir}/world.json): not built yet (emerald_world, EMERALD-2)')
    files = os.path.join(ROOT, 'external', 'pokebw2', 'build', 'b2_us', 'files')
    headers, _ = zoneheaders.load(files)
    text, scripts = ruby_scripts(V.decomp() if em else RUBY)
    sprites = (V.load_json if em else lambda p: json.load(open(p)))(os.path.join(ROOT, 'data', 'sprite_map.json'))
    gfx_alias = sprites.get('_gfx_alias', {}) if em else {}
    def sprite_row(gfx):
        return sprites.get(gfx) or sprites.get(gfx_alias.get(gfx, '')) or {}
    cfg, lay = W.load()
    world, _, maps = W.compose(cfg, lay)
    wj = json.load(open(os.path.join(wdir, 'world.json')))
    owner = main_owner = {(c['cx'], c['cz']): c['zone'] for c in wj['cells']}     # (+ world.json zone_rects: W.zone_of)
    # a zone's file is named after (and takes the scenes of) its first map: Emerald's new maps share a zone with their
    # Sapphire neighbour (Safari Zone zones 38/40, the Frontier's east half in 17: data/emerald/hoenn_zones.json), whose
    # scenes/<Map>.inc must stay (emerald_integrate 2026-10-12; Sapphire and Ruby have one map per zone)
    zone_map = {}
    for n, mc in cfg['maps'].items():
        if n in maps: zone_map.setdefault(mc['zone'], n)
    # the main matrix, then every warp-only map's own matrix (b2tools/world.py standalone groups)
    frames = [(world, maps, owner)] + [(fw, fm, fo) for _, fw, fm, fo in W.standalone_frames(cfg)]
    frame_of = {n: f for f in frames for n in f[1]}
    for n, mc in cfg['standalone'].items():
        if n in frame_of: zone_map.setdefault(mc['zone'], n)
    hand_zones = {cfg['maps'][n]['zone'] for n in HAND_MADE if n in cfg['maps']}
    per_zone = collections.defaultdict(list)            # zone -> [(kind, map, event, message label)]
    story_signs = []                                    # [(map, sign event, scene script id)] (scene_sign)
    balls = (V.load_json if em else lambda p: json.load(open(p)))(os.path.join(ROOT, 'data', 'hoenn_items.json'))['balls']   # gen_items.py
    events_dir = os.path.join(ROOT, 'data', 'sapphire', *(['emerald'] if em else []))
    no_events = []
    content, n_balls = {}, 0
    skipped = collections.Counter()
    for name in frame_of:
        if name in HAND_MADE: continue
        sp = os.path.join(events_dir, f'{name}.json')
        if not os.path.exists(sp):
            no_events.append(name); continue
        world, maps, owner = frame_of[name]
        d = json.load(open(sp)); ox, oz = maps[name]['ox'], maps[name]['oz']
        for kind, events in (('sign', d['signs']), ('npc', d['npcs'])):
            for ev in events:
                if 'script' not in ev: skipped[f'{kind}: not a sign'] += 1; continue
                if kind == 'npc':
                    if ev['trainer_type'] != 'TRAINER_TYPE_NONE': skipped['trainer'] += 1; continue
                    if ev['gfx'] == 'OBJ_EVENT_GFX_ITEM_BALL':      # global item scripts work in any zone
                        ball = balls.get(ev['script'])
                        if not ball: skipped['item ball without a Black 2 item'] += 1; continue
                        content.setdefault(name, {'signs': {}, 'npcs': {}})['npcs'][ev['script']] = dict(
                            script=ball['script'], sprite=110, flag=ball['flag'])
                        n_balls += 1; continue
                    if str(ev['hide_flag']) not in ('0', ''): skipped['npc with a hide flag (story)'] += 1; continue
                    if not sprite_row(ev['gfx']).get('code'): skipped['no Black 2 sprite'] += 1; continue
                label = simple_message(ev['script'], text, scripts)
                # a story sign (the scene file names it): the scene's script, also when its Sapphire script is one
                # message the generator can't write ({EVIL_TEAM}: Route 110's "Team Aqua Rulez" sign, story_fixups)
                if kind == 'sign' and (not label or convert(text[label])[1]) and scene_sign(name, ev, ver):
                    home = (cfg['maps'].get(name) or cfg['standalone'].get(name) or {}).get('zone')
                    zone = W.zone_of(owner, ox + ev['x'], oz + ev['y'], wj.get('zone_rects', []) if owner is main_owner else ())
                    if zone == home: story_signs.append((name, ev, scene_sign(name, ev, ver))); continue
                if not label: skipped[f'{kind}: story script'] += 1; continue
                if convert(text[label])[1]: skipped[f'{kind}: text needs script values (STR_VAR...)'] += 1; continue
                zone = W.zone_of(owner, ox + ev['x'], oz + ev['y'], wj.get('zone_rects', []) if owner is main_owner else ())
                if zone in hand_zones or zone is None: skipped['in a hand-made zone'] += 1; continue
                per_zone[zone].append((kind, name, ev, label))
    def sign_entry(mapname, ev, sid, route):
        facing = ev.get('facing', 'BG_EVENT_PLAYER_FACING_ANY')
        world, maps, _ = frame_of[mapname]
        cls = (world.get((maps[mapname]['ox'] + ev['x'], maps[mapname]['oz'] + ev['y'])) or (0, ''))[1]
        entry = {'script': sid, 'dir': 0 if facing.endswith('NORTH') else 6}
        if cls == 'sign': entry['model'] = SIGN_MODEL_ROUTE if route else SIGN_MODEL_OTHER
        return entry
    shared_s = os.path.join(ROOT, 'src', 'field_scripts'); shared_t = os.path.join(ROOT, 'src', 'text', 'script')
    out_s, out_t = (os.path.join(shared_s, 'emerald'), os.path.join(shared_t, 'emerald')) if em else (shared_s, shared_t)
    os.makedirs(out_s, exist_ok=True); os.makedirs(out_t, exist_ok=True)
    for f in glob.glob(os.path.join(out_s, '*_auto_*.s')) + glob.glob(os.path.join(out_t, '*_auto_*.txt')): os.remove(f)
    def write(d, shared, fname, data):          # Emerald: a file equal to the shared one of that name (comment lines
        strip = lambda t: [l for l in t.split('\n') if not l.startswith('//')]       # aside) is not written
        if em and os.path.exists(os.path.join(shared, fname)) and \
                strip(open(os.path.join(shared, fname), encoding='utf-8').read()) == strip(data):
            return
        open(os.path.join(d, fname), 'w', encoding='utf-8').write(data)
    unknown_codes = collections.Counter()
    for zone in sorted(zone_map):
        if zone in hand_zones: continue
        name = zone_map[zone]; hd = headers[zone]
        evs = per_zone.get(zone, [])
        n_story, story_text, story_init = scene_files(name, ver)     # story scenes of this map come first (fixed ids)
        story_text = scene_text(name, ver)
        if not em and scene_count(name, 'ruby') != n_story:     # Ruby assembles this same file: its list must not differ (S0-2)
            raise SystemExit(f'scenes/{name}.inc: {n_story} story scripts in Sapphire but {scene_count(name, "ruby")} in '
                             'Ruby; both versions assemble the same generated file, so their ScriptEntry lists must match '
                             '(branch the bodies, not the list; Emerald-only entries go last under #ifdef HOENN_EMERALD)')
        msgs, ids, blocks = list(story_text), {}, []
        for kind, mapname, ev, label in evs:
            key = (mapname, ev['script'])
            if key in ids: continue
            line, unk = convert(text[label]); unknown_codes.update(unk)
            msgs.append(line); sid = n_story + len(blocks) + 1
            blocks.append(script_block(sid, len(msgs) - 1, kind)); ids[key] = sid
            mc = content.setdefault(mapname, {'signs': {}, 'npcs': {}})
            if kind == 'sign':
                route = bool(re.search(r'(Town|City|Route)Sign', ev['script'])) or text[label].upper().startswith('ROUTE')
                mc['signs'][ev['script']] = sign_entry(mapname, ev, sid, route)
            else:
                mc['npcs'][ev['script']] = {'script': sid, 'sprite': sprite_row(ev['gfx'])['code'],
                                            **({} if em else NPC_FIXES.get((mapname, ev['script']), {}))}
        entries = '\n'.join(f'    ScriptEntry Script_{i}' for i in range(n_story + 1, n_story + len(blocks) + 1))
        scene = (f'#define SCENE_ENTRIES\n#include "scenes/{name}.inc"\n#undef SCENE_ENTRIES\n', f'#include "scenes/{name}.inc"\n'
                 '    .balign 4, 0\n') if n_story else ('', '')
        src = (f'// {name} (zone {zone}): generated by converter/gen_map_content.py from {"Emerald" if em else "Sapphire"}\'s simple signs and '
               f'NPCs' + (f', after the story scripts 1-{n_story} of scenes/{name}.inc (their text: lines 0-{len(story_text) - 1}, '
               f'src/text/scenes/{name}.txt)' if n_story else '') + f'.\n// Messages: src/text/script/{hd["text"]:04d}_auto_{name}.txt\n'
               '#include "asm/field_script.inc"\n#include "hoenn.h"\n#include "hoenn_trainers.h"\n#include "hoenn_story.inc"\n\n'
               + scene[0] + (entries + '\n' if entries else '') + '    ScriptEntriesEnd\n\n' + scene[1]
               + '\n'.join(blocks) + ('    .balign 4, 0\n' if blocks else ''))
        if not blocks and not n_story:
            src += 'Script_None:\n    VMHalt\n    .balign 4, 0\n'
        write(out_s, shared_s, f'{hd["scripts"]:04d}_auto_{name}.s', src)
        write(out_s, shared_s, f'{hd["init_scripts"]:04d}_auto_{name}_init.s',
            f'// {name} (zone {zone}): map scripts of scenes/{name}_init.inc. converter/gen_map_content.py\n'
            '#include "asm/field_script.inc"\n#include "hoenn.h"\n#include "hoenn_story.inc"\n\n'
            f'#include "scenes/{name}_init.inc"\n    .balign 4, 0\n' if story_init else
            f'// {name} (zone {zone}): no map scripts yet (Unova\'s would run our scripts). converter/gen_map_content.py\n'
            '#include "asm/field_script.inc"\n\n    MapScriptsEnd\n    .byte 0x00\n    .byte 0x00\n')
        write(out_t, shared_t, f'{hd["text"]:04d}_auto_{name}.txt', '\n'.join(msgs or ['…']) + '\n')
    for mapname, ev, sid in story_signs:      # story signs: the scene's script, the event and model from here
        route = bool(re.search(r'(Town|City|Route)Sign', ev['script']))
        content.setdefault(mapname, {'signs': {}, 'npcs': {}})['signs'][ev['script']] = sign_entry(mapname, ev, sid, route)
    json.dump({'_doc': 'Generated by converter/gen_map_content.py; merged into the map settings by b2tools/world.py.' +
               (' Emerald (pokeemerald\'s events on Emerald\'s world): replaces data/hoenn_content.json in an Emerald '
                'build (not merged).' if em else ''),
               'maps': content}, open(os.path.join(ROOT, 'data', *(['emerald'] if em else []), 'hoenn_content.json'), 'w'),
              indent=1, ensure_ascii=False)
    if em and no_events:
        print(f'no data/sapphire/emerald/<Map>.json for {len(no_events)} maps (run sapphire_data.py in Emerald mode): '
              + ', '.join(no_events[:12]) + (' ...' if len(no_events) > 12 else ''))
    n = sum(len(v['signs']) + len(v['npcs']) for v in content.values())
    print(f'{n} events ({n_balls} item balls) in {len(content)} maps; skipped: {dict(skipped)}; unknown text codes: {dict(unknown_codes)}')

if __name__ == '__main__':
    main()
