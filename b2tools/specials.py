"""Helpers of the "specials" interiors agent (notes/INTERIORS_PLAN.md): previews into the agent's own room folder,
side-by-side checks against Sapphire, catalogues of Black 2's interior models and map textures, and pack sizes.

    python3 specials.py preview NAME ...       work/agents/specials/interiors/NAME/compare.png (Sapphire | game view | top)
    python3 specials.py models OUT.png [PACK ...]    contact sheet of the interior building models (front view)
    python3 specials.py tex OUT.png SET ...    contact sheet of map texture sets (a/0/1/4)
    python3 specials.py packs [ZONE ...]       interior pack + texture sizes of the areas the rooms use (after a build)
    python3 specials.py grid MAP ...           Sapphire collision / elevation / events as text

Never writes work/interiors (the lead's): everything goes to HOENN_INTERIORS_DIR (default: this agent's copy).
"""
import os, sys, json, math, struct
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(ROOT, 'converter'))
AGENT = os.path.join(ROOT, 'work', 'agents', 'specials')
os.environ.setdefault('HOENN_INTERIORS_DIR', os.path.join(AGENT, 'interiors'))
OUT = os.environ['HOENN_INTERIORS_DIR']
import preview_interior as pv                                   # noqa: E402
pv.OUT = OUT                                                    # its model cache and previews go to our copy
FILES = os.path.join(ROOT, 'external', 'pokebw2', 'build', 'b2_us', 'files')

def sapphire_image(name):
    from gba import Repo, MetatileRenderer
    from PIL import Image
    import numpy as np
    r = Repo(os.path.join(ROOT, 'external', 'pokeruby'))
    mj = r.map_json(name)
    g, l = r.layout_grid(mj['layout'])
    mr = MetatileRenderer(r, l['primary_tileset'], l['secondary_tileset'])
    H, W = g.shape
    img = np.zeros((H * 16, W * 16, 3), np.uint8)
    for y in range(H):
        for x in range(W):
            img[y * 16:y * 16 + 16, x * 16:x * 16 + 16] = mr.render(int(g[y, x]) & 0x3FF)[..., :3]
    im = Image.fromarray(img)
    from PIL import ImageDraw
    d = ImageDraw.Draw(im)
    for o in mj.get('object_events', []):
        d.rectangle((o['x'] * 16 + 2, o['y'] * 16 + 2, o['x'] * 16 + 13, o['y'] * 16 + 13), outline=(255, 0, 0))
    return im

def top_view(name, scale=2):
    """Straight top-down orthographic-ish render of the built room, cropped to Sapphire's map, 16*scale px per tile."""
    meta, parts = room_parts(name)
    ox, oz = meta['origin']; w, h = meta['size']
    cx = (ox + w / 2) * 16 - 256; cz = (oz + h / 2) * 16 - 256
    span = max(w, h) * 16
    dist = span * 12
    fov = 2 * math.degrees(math.atan((h * 16 / 2) / dist))
    W, H = int(w * 16 * scale), int(h * 16 * scale)
    return pv.render(parts, eye=(cx, dist, cz + 0.01), target=(cx, 0, cz), fov=fov, W=W, H=H)

def room_parts(name):
    meta = json.load(open(os.path.join(OUT, name, 'room.json')))
    parts = pv.parse(os.path.join(OUT, name, 'terrain.dae'))
    packs = {m['res']: m['pack'] for m in meta['models']}
    names = {m['name']: m['res'] for m in meta['models']}
    for f in meta['furniture']:
        res = f['m'] if isinstance(f['m'], int) else names[f['m']]
        parts += pv.placed(pv.furniture_parts(res, packs[res]), f['pos'], f['rot'])
    return meta, parts

def game_view(name, W=512, H=384):
    """The room from the south, at about Black 2's interior camera pitch, framed to fill the image."""
    meta, parts = room_parts(name)
    ox, oz = meta['origin']; w, h = meta['size']
    cx = (ox + w / 2) * 16 - 256; cz = (oz + h / 2) * 16 - 256
    span = max(w * 16 * 0.75, h * 16)
    return pv.render(parts, eye=(cx, span * 1.05, cz + span * 1.25), target=(cx, 0, cz + span * 0.04), fov=42, W=W, H=H)

def preview(name):
    from PIL import Image
    game = game_view(name)
    sap = sapphire_image(json.load(open(os.path.join(OUT, name, 'room.json')))['map'])
    top = top_view(name, 1)
    k = 384 / max(sap.height, 1)
    sap = sap.resize((int(sap.width * k), 384), Image.NEAREST)
    top = top.resize((sap.width, 384), Image.NEAREST)
    im = Image.new('RGB', (sap.width * 2 + 512, 384))
    im.paste(sap, (0, 0)); im.paste(top, (sap.width, 0)); im.paste(game, (sap.width * 2, 0))
    out = os.path.join(OUT, name, 'compare.png')
    im.save(out)
    return out

def model_sheet(out, packs=None, cell=128, cols=10):
    """Every interior model of the given packs (default all), seen from the game's camera angle, with name/res/size."""
    from PIL import Image, ImageDraw
    import b2files, models_interior as mi
    by_name, by_res = mi.interior_models()
    items = [(res, name, p, bmd) for res, (name, p, bmd) in sorted(by_res.items())
             if (packs is None or p in packs)]
    rows = (len(items) + cols - 1) // cols
    sheet = Image.new('RGB', (cell * cols, (cell + 12) * rows), (40, 40, 60))
    d = ImageDraw.Draw(sheet)
    for i, (res, name, p, bmd) in enumerate(items):
        parts = pv.furniture_parts(res, p)
        x0, x1, y0, y1, z0, z1 = mi.bmd_box(bmd)
        if parts:
            size = max(x1 - x0, z1 - z0, y1 - y0, 8)
            cxm, cym, czm = (x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2
            img = pv.render(parts, eye=(cxm, cym + size * 1.6, czm + size * 1.9), target=(cxm, cym, czm), fov=40,
                            W=cell, H=cell, bg=(40, 40, 60))
            sheet.paste(img, (cell * (i % cols), (cell + 12) * (i // cols)))
        X, Y = cell * (i % cols), (cell + 12) * (i // cols) + cell
        d.text((X + 2, Y), f'{name[:13]} {res} {x1 - x0:.0f}x{z1 - z0:.0f}', fill=(255, 255, 255))
    sheet.save(out)
    return out

def tex_sheet(out, sets, common=False):
    """Map texture sets as one sheet (96 px cells, full names); the textures every interior set shares (chip_*, d0*,
    d_*) only with common=True."""
    from PIL import Image, ImageDraw
    import b2files, nsbtx
    sheets = []
    for s in sets:
        t = [(n, img, f) for n, img, f in nsbtx.decode(b2files.map_textures(FILES, s))
             if common or not n.startswith(('chip_', 'd0', 'd_', 'grid'))]
        cell, cols = 96, 8
        rows = (len(t) + cols - 1) // cols
        sh = Image.new('RGBA', (cell * cols, (cell + 12) * rows), (255, 0, 255, 255))
        d = ImageDraw.Draw(sh)
        for i, (n, img, f) in enumerate(t):
            x, y = cell * (i % cols), (cell + 12) * (i // cols)
            k = cell / max(img.size)
            im = img.resize((max(1, int(img.width * k)), max(1, int(img.height * k))), Image.NEAREST)
            sh.alpha_composite(im, (x, y))
            d.rectangle((x, y + cell, x + cell, y + cell + 12), fill=(0, 0, 0, 255))
            d.text((x + 1, y + cell), f'{s}:{n}'[:16], fill=(255, 255, 255, 255))
        sheets.append(sh)
    W = max(s.width for s in sheets); H = sum(s.height for s in sheets)
    im = Image.new('RGBA', (W, H)); y = 0
    for s in sheets: im.paste(s, (0, y)); y += s.height
    im.save(out)
    return out

def tex_pick(out, picks, cell=96, cols=8):
    """Contact sheet of chosen textures: picks = ['SET:prefix', ...] (every texture of SET whose name starts with
    prefix)."""
    from PIL import Image, ImageDraw
    import b2files, nsbtx
    items = []
    for p in picks:
        s, pre = p.split(':', 1)
        items += [(f'{s}:{n}', img) for n, img, f in nsbtx.decode(b2files.map_textures(FILES, int(s))) if n.startswith(pre)]
    rows = (len(items) + cols - 1) // cols
    sh = Image.new('RGBA', (cell * cols, (cell + 12) * rows), (255, 0, 255, 255))
    d = ImageDraw.Draw(sh)
    for i, (n, img) in enumerate(items):
        x, y = cell * (i % cols), (cell + 12) * (i // cols)
        k = cell / max(img.size)
        im = img.resize((max(1, int(img.width * k)), max(1, int(img.height * k))), Image.NEAREST)
        sh.alpha_composite(im, (x, y))
        d.rectangle((x, y + cell, x + cell, y + cell + 12), fill=(0, 0, 0, 255))
        d.text((x + 1, y + cell), n[:16] + f' {img.width}x{img.height}'[:0], fill=(255, 255, 255, 255))
    sh.save(out)
    return out

def pack_sizes(zones=None):
    """Bytes of the interior building pack (a/2/2/6) and its texture set (a/1/7/5) per area, in the agent's ROM
    build (work/agents/specials/rom/files is deleted after a build, so this rebuilds nothing: it applies our rooms'
    model lists to Black 2's packs the way patches/interiors.py does and sums the sizes)."""
    import glob, b2files, nsbtx, models_interior as mi
    from patches.interiors import _area_record, _pack_sections
    by_name, by_res = mi.interior_models()
    cfgs = [json.load(open(f)) for f in sorted(glob.glob(os.path.join(ROOT, 'data', 'interiors', '*.json')))]
    per_area = {}
    for c in cfgs:
        if not c.get('room') or (zones and c['zone'] not in zones and c.get('area') not in zones): continue
        meta_p = os.path.join(OUT, c['room'], 'room.json')
        if not os.path.exists(meta_p): continue
        meta = json.load(open(meta_p))
        area = c.get('area')
        if area is None:
            from zones import zone_headers
            area = zone_headers()[c['zone']].get('area')
        per_area.setdefault(area, {})
        for m in meta['models']: per_area[area][m['res']] = m
    packs = b2files.narc_entries(b2files.arc_path(FILES, 226))
    btex = b2files.narc_entries(b2files.arc_path(FILES, 175))
    out = []
    for area, models in sorted(per_area.items()):
        pack, sets, _ = _area_record(FILES, area)
        infos, bmds = _pack_sections(packs[pack])
        have = {struct.unpack_from('<H', i, 0)[0] for i in infos}
        add = [m for r, m in models.items() if r not in have]
        add_bmd = sum(len(by_res[m['res']][2]) for m in add)
        # textures: each added model's texture/palette pairs come from its own pack's texture set (upper bound: the
        # merged set adds only names it lacks)
        names_have = {n for n, _, _ in nsbtx.decode(btex[pack])}
        add_tex = 0
        for m in add:
            src = nsbtx.decode(btex[m['pack']])
            pairs = [t for t, _ in nsbtx.material_pairs(by_res[m['res']][2]) if t]
            for n, img, f in src:
                if n in pairs and n not in names_have:
                    names_have.add(n); add_tex += img.width * img.height * {1: 1, 2: 0.25, 3: 0.5, 4: 1, 5: 0.25, 6: 1, 7: 2}.get(f, 1)
        base = len(packs[pack]) + len(btex[pack])
        out.append(dict(area=area, pack=pack, base_kb=round(base / 1024, 1), added_models=sorted(m['name'] for m in add),
                        added_kb=round((add_bmd + add_tex) / 1024, 1), total_kb=round((base + add_bmd + add_tex) / 1024, 1)))
    return out

def zone_chunks(zone):
    """Chunk ids of a Black 2 zone's matrix (from the unmodified files)."""
    import zoneheaders, b2files
    headers, _ = zoneheaders.load(FILES)
    m = headers[zone]['matrix']
    raw = b2files.narc_entries(b2files.arc_path(FILES, 9))[m]
    fmt, _, w, h = struct.unpack_from('<HHHH', raw, 0)
    ids = struct.unpack_from(f'<{w * h}I', raw, 8)
    return headers[zone], w, h, ids

def chunk_view(zone, out, W=768, H=576, top=False):
    """Render a Black 2 zone's own room (chunk terrain with its area's map textures + its building placements), for
    reference (how Black 2 uses a texture set)."""
    import subprocess, b2files
    from patches.interiors import _area_record
    hd, w, h, ids = zone_chunks(zone)
    pack, sets, _ = _area_record(FILES, hd['area'])
    parts = []
    for k, cid in enumerate(ids):
        if cid == 0xFFFFFFFF: continue
        d = os.path.join(OUT, '_chunks', f'{cid}_{sets[0]}')
        if not os.path.isdir(os.path.join(d, 'dae')):
            os.makedirs(d, exist_ok=True)
            magic, secs = b2files.chunk(FILES, cid)
            open(os.path.join(d, 'm.nsbmd'), 'wb').write(secs[0])
            open(os.path.join(d, 't.nsbtx'), 'wb').write(b2files.map_textures(FILES, sets[0]))
            subprocess.run([pv.APICULA, 'convert', os.path.join(d, 'm.nsbmd'), os.path.join(d, 't.nsbtx'), '-o',
                            os.path.join(d, 'dae'), '-f', 'dae'], capture_output=True)
        daes = [os.path.join(d, 'dae', f) for f in os.listdir(os.path.join(d, 'dae')) if f.endswith('.dae')]
        cx, cz = (k % w) * 512, (k // w) * 512
        for tp, P, UV, C in (pv.parse(daes[0]) if daes else []):
            parts.append((tp, P + [cx, 0, cz], UV, C))
        for b in b2files.chunk_buildings(FILES, cid):
            try: parts += pv.placed(pv.furniture_parts(b['res_id'], pack), [b['x'] + cx, b['y'], b['z'] + cz], b['rot'])
            except StopIteration: pass
    import numpy as np
    allp = np.concatenate([p[1].reshape(-1, 3) for p in parts])
    lo, hi = allp.min(0), allp.max(0)
    c = (lo + hi) / 2; span = max(hi[0] - lo[0], hi[2] - lo[2])
    if top: img = pv.render(parts, eye=(c[0], span * 2.4, c[2] + 0.01), target=(c[0], 0, c[2]), fov=40, W=W, H=H)
    else: img = pv.render(parts, eye=(c[0], span * 0.9, c[2] + span * 0.85), target=(c[0], 0, c[2] + span * 0.05), fov=45, W=W, H=H)
    img.save(out)
    return out, [hex(i) for i in ids], hd['area'], pack, sets

def missing_rooms():
    """Rooms named by data/interiors/*.json that this agent's copy of the interiors lacks (other agents' new rooms):
    the interiors patch needs every one of them built."""
    import glob
    out = set()
    for f in glob.glob(os.path.join(ROOT, 'data', 'interiors', '*.json')):
        r = json.load(open(f)).get('room')
        if r and not os.path.exists(os.path.join(OUT, r, 'room.json')): out.add(r)
    return sorted(out)


# ------------------------------------------------------------------------------------------------ people and signs
import move_codes as MOVE_CODES                       # noqa: E402  (v165_fixes)
FACE = {'MOVEMENT_TYPE_FACE_UP': 0, 'MOVEMENT_TYPE_FACE_DOWN': 1, 'MOVEMENT_TYPE_FACE_LEFT': 2, 'MOVEMENT_TYPE_FACE_RIGHT': 3}
FACE_NAME = ['Up', 'Down', 'Left', 'Right']

def turnback_message(name, text, scripts):
    """Text label of a Sapphire person script that shows one message and then turns the person back
    (msgbox X, MSGBOX_NPC; lockall; applymovement N, Common_Movement_FaceOriginalDirection; waitmovement 0; releaseall;
    end), else None."""
    body = [l for l in scripts.get(name, []) if l]
    want = ['msgbox', 'lockall', 'applymovement', 'waitmovement', 'releaseall', 'end']
    if [l.split()[0].rstrip(',') for l in body] != want: return None
    if 'Common_Movement_FaceOriginalDirection' not in body[2] or 'MSGBOX_NPC' not in body[0]: return None
    label = body[0].split()[1].rstrip(',')
    return label if label in text else None

def people(name):
    """Rewrite a specials room's people and signs: Sapphire's one-message people and signs exactly as
    converter/gen_interiors.py makes them (item balls too), plus people whose script is one message followed by
    Common_Movement_FaceOriginalDirection (they turn back afterwards, as in Sapphire). Writes the room's script and text
    files (numbers in data/hoenn_interiors.json) and the "npcs"/"signs" of data/interiors/<zone>.json (other keys kept)."""
    import collections
    sys.path.insert(0, os.path.join(HERE, 'patches'))
    from gen3text import convert
    from gen_map_content import ruby_scripts, simple_message
    from gen_interiors import npc_block, sign_block
    r = json.load(open(os.path.join(ROOT, 'data', 'hoenn_interiors.json')))['rooms'][name]
    j = json.load(open(os.path.join(ROOT, 'external', 'pokeruby', 'data', 'maps', name, 'map.json')))
    text, scripts = ruby_scripts()
    sprites = json.load(open(os.path.join(ROOT, 'data', 'sprite_map.json')))
    balls = json.load(open(os.path.join(ROOT, 'data', 'hoenn_items.json')))['balls']
    msgs, blocks, npcs, signs, moves, report = [], [], [], [], set(), collections.Counter()
    for lid, o in enumerate(j.get('object_events', []), 1):
        if o['graphics_id'] == 'OBJ_EVENT_GFX_ITEM_BALL':
            b = balls.get(o['script'])
            if b: npcs.append(dict(uid=lid, model=110, script=b['script'], flag=b['flag'], dir=1, at=[o['x'], o['y']])); report['item ball'] += 1
            continue
        if o.get('trainer_type', 'TRAINER_TYPE_NONE') not in ('TRAINER_TYPE_NONE', '0', 0): report['left out: trainer'] += 1; continue
        if str(o.get('flag', '0')) not in ('0', ''): report['left out: story person (hide flag)'] += 1; continue
        code = (sprites.get(o['graphics_id']) or {}).get('code')
        face = FACE.get(o['movement_type'], 1)
        label = simple_message(o['script'], text, scripts) if code else None
        turn = False
        if not label and code:
            label = turnback_message(o['script'], text, scripts); turn = bool(label)
        if not label or convert(text[label])[1]: report['left out: story/complex script or no sprite'] += 1; continue
        msgs.append(convert(text[label])[0])
        b = npc_block(len(blocks) + 1, len(msgs) - 1)
        if turn:                       # Sapphire: Common_Movement_FaceOriginalDirection after the message
            b = b.replace('    ActorMsgClose\n', f'    ActorMsgClose\n    ActorCmdExec {lid}, Movement_Face{FACE_NAME[face]}\n    ActorCmdWait\n')
            moves.add(face); report['person (turns back)'] += 1
        else: report['person'] += 1
        blocks.append(b)
        n = dict(uid=lid, model=code, script=len(blocks), dir=face, at=[o['x'], o['y']])
        n.update(MOVE_CODES.room_npc(o))     # Sapphire's movement type as Black 2's code (b2tools/move_codes.py)
        npcs.append(n)
    for b in j.get('bg_events', []):
        if b.get('type') != 'sign' or not b.get('script'): continue
        label = simple_message(b['script'], text, scripts)
        if not label or convert(text[label])[1]: report['left out: sign with a story/complex script'] += 1; continue
        msgs.append(convert(text[label])[0]); blocks.append(sign_block(len(blocks) + 1, len(msgs) - 1))
        facing = b.get('player_facing_dir', 'BG_EVENT_PLAYER_FACING_ANY')
        signs.append(dict(script=len(blocks), at=[b['x'], b['y']], dir=0 if facing.endswith('NORTH') else 4)); report['sign'] += 1
    entries = '\n'.join(f'    ScriptEntry Script_{i}' for i in range(1, len(blocks) + 1))
    mv = ''.join(f'Movement_Face{FACE_NAME[f]}:\n    Move {f}, 1\n    MoveEnd\n' for f in sorted(moves))
    src = (f"// {name} (zone {r['zone']}): Sapphire's simple people and signs (as converter/gen_interiors.py makes them),\n"
           f"// plus people that turn back after their message (Common_Movement_FaceOriginalDirection), by the specials agent\n"
           f"// (b2tools/specials.py people). Messages: src/text/script/{r['text']:04d}_room_{name}.txt\n"
           '#include "asm/field_script.inc"\n\n' + (entries + '\n' if blocks else '    ScriptEntry Script_None\n')
           + '    ScriptEntriesEnd\n\n' + '\n'.join(blocks) + ('' if blocks else 'Script_None:\n    VMHalt\n')
           + '    .balign 4, 0\n' + (mv + '    .balign 4, 0\n' if mv else ''))
    from story_merge import write_room_script, write_room_text      # a story agent's part (after "// ---- story") stays
    sp = os.path.join(ROOT, 'src', 'field_scripts', f"{r['scripts']:04d}_room_{name}.s")
    write_room_text(os.path.join(ROOT, 'src', 'text', 'script', f"{r['text']:04d}_room_{name}.txt"), msgs or ['…'], sp)
    write_room_script(sp, src)
    jp = os.path.join(ROOT, 'data', 'interiors', f"{r['zone']}.json")
    cfg = json.load(open(jp))
    cfg['npcs'], cfg['signs'] = npcs, signs
    json.dump(cfg, open(jp, 'w'), indent=1, ensure_ascii=False)
    return dict(report)

def _main():
    cmd, args = sys.argv[1], sys.argv[2:]
    if cmd == 'people':
        for n in args: print(n, people(n))
    elif cmd == 'missing':
        print(' '.join(missing_rooms()))
    elif cmd == 'preview':
        for n in args: print(preview(n))
    elif cmd == 'models':
        print(model_sheet(args[0], [int(a) for a in args[1:]] or None))
    elif cmd == 'tex':
        print(tex_sheet(args[0], [int(a) for a in args[1:]]))
    elif cmd == 'packs':
        for r in pack_sizes([int(a) for a in args] or None): print(r)
    elif cmd == 'grid':
        import subprocess
        from gba import Repo, MetatileRenderer
        repo = Repo(os.path.join(ROOT, 'external', 'pokeruby'))
        for name in args:
            mj = repo.map_json(name)
            g, l = repo.layout_grid(mj['layout'])
            mr = MetatileRenderer(repo, l['primary_tileset'], l['secondary_tileset'])
            H, W = g.shape
            print(name, W, H, l['primary_tileset'], l['secondary_tileset'])
            print('    ' + ''.join(f'{x % 10}' for x in range(W)))
            for z in range(H):
                row = ''.join('.' if (int(g[z, x]) >> 10) & 3 == 0 else '#' for x in range(W))
                beh = ' '.join('%02x' % mr.behavior(int(g[z, x]) & 0x3FF) for x in range(W))
                print(f'{z:3d} {row}   {beh}')
            for w in mj.get('warp_events', []): print('  warp', w['x'], w['y'], w['dest_map'], w['dest_warp_id'])
            for o in mj.get('object_events', []):
                print('  obj', o['graphics_id'], o['x'], o['y'], o['movement_type'], o.get('flag'), o['script'], o.get('trainer_type'))
            for b in mj.get('bg_events', []): print('  bg', b.get('type'), b['x'], b['y'], b.get('script'), b.get('player_facing_dir'))
            for c in mj.get('coord_events', []): print('  coord', c['x'], c['y'], c.get('script'), c.get('var'), c.get('var_value'))
    elif cmd == 'pick':
        print(tex_pick(args[0], args[1:]))
    elif cmd == 'chunk':
        print(chunk_view(int(args[0]), args[1], top=len(args) > 2))

if __name__ == '__main__':
    _main()

def chunk_materials(zone):
    """Which textures a Black 2 room uses for floors (up-facing), back walls (south-facing) and side walls, by area."""
    import numpy as np, collections
    hd, w, h, ids = zone_chunks(zone)
    from patches.interiors import _area_record
    pack, sets, _ = _area_record(FILES, hd['area'])
    chunk_view(zone, os.path.join(OUT, '_chunks', f'z{zone}.png'), W=64, H=48)      # converts the chunk if needed
    stats = collections.defaultdict(lambda: collections.Counter())
    for cid in ids:
        d = os.path.join(OUT, '_chunks', f'{cid}_{sets[0]}', 'dae')
        for f in os.listdir(d):
            if not f.endswith('.dae'): continue
            for tp, P, UV, C in pv.parse(os.path.join(d, f)):
                n = np.cross(P[:, 1] - P[:, 0], P[:, 2] - P[:, 0])
                area = np.linalg.norm(n, axis=1) / 2
                nn = n / np.maximum(np.linalg.norm(n, axis=1, keepdims=True), 1e-9)
                name = os.path.basename(tp or '?').rsplit('.', 1)[0]
                for k in range(len(P)):
                    kind = 'floor' if nn[k, 1] > 0.7 else ('ceil' if nn[k, 1] < -0.7 else
                           ('back' if abs(nn[k, 2]) > 0.7 else 'side'))
                    stats[name][kind] += area[k]
    return {n: {k: round(v) for k, v in c.most_common()} for n, c in sorted(stats.items(), key=lambda kv: -sum(kv[1].values()))}

def wall_uv(zone, names):
    """For textures on vertical faces of a Black 2 room: world units per texture repeat along u (horizontal) and v
    (vertical), and the y range they cover — how Black 2 scales its wall textures."""
    import numpy as np
    hd, w, h, ids = zone_chunks(zone)
    from patches.interiors import _area_record
    pack, sets, _ = _area_record(FILES, hd['area'])
    out = {}
    for cid in ids:
        d = os.path.join(OUT, '_chunks', f'{cid}_{sets[0]}', 'dae')
        for f in os.listdir(d):
            if not f.endswith('.dae'): continue
            for tp, P, UV, C in pv.parse(os.path.join(d, f)):
                name = os.path.basename(tp or '?').rsplit('.', 1)[0]
                if name not in names: continue
                for k in range(len(P)):
                    n = np.cross(P[k, 1] - P[k, 0], P[k, 2] - P[k, 0])
                    if abs(n[1]) > 0.3 * np.linalg.norm(n): 
                        # floor-ish: units per repeat in x/z
                        dx = np.ptp(P[k, :, 0]); du = np.ptp(UV[k, :, 0]); dz = np.ptp(P[k, :, 2]); dv = np.ptp(UV[k, :, 1])
                        if du > 1e-3 and dv > 1e-3: out.setdefault((name, 'floor'), []).append((round(dx / du, 1), round(dz / dv, 1)))
                        continue
                    dy = np.ptp(P[k, :, 1]); dv = np.ptp(UV[k, :, 1])
                    dh = max(np.ptp(P[k, :, 0]), np.ptp(P[k, :, 2])); du = np.ptp(UV[k, :, 0])
                    if dv > 1e-3 and du > 1e-3:
                        out.setdefault((name, 'wall'), []).append((round(dh / du, 1), round(dy / dv, 1), round(P[k, :, 1].min()), round(P[k, :, 1].max())))
    import collections
    return {k: collections.Counter(v).most_common(4) for k, v in out.items()}
