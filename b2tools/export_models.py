"""Convert chosen Black 2 building packs and map chunks to .glb (via apicula) plus a viewer manifest.

Usage: python3 export_models.py <group-name> pack:53 pack:0 chunk:283:214 ...
  pack:<id>              every model in exterior building pack <id>, with that pack's textures
  ipack:<id>             same for interior pack <id>
  chunk:<id>:<area>      terrain model of map chunk <id>, textured with <area>'s texture set
Output: ../work/models/<group>/*.glb and manifest.json (open viewer/index.html?manifest=...).
Everything comes from the extracted ROM; nothing is written back to it.
"""
import os, sys, json, subprocess, shutil, tempfile
from b2files import *

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..')
F = os.path.join(ROOT, 'external/pokebw2/extract/b2_us/files')
APICULA = os.path.join(ROOT, 'tools/apicula/bin/apicula')

def convert(bmd, btx, out_dir, stem):
    """Run apicula on one model + one texture file; return the .glb path or None."""
    with tempfile.TemporaryDirectory() as t:
        open(f'{t}/{stem}.nsbmd', 'wb').write(bmd)
        open(f'{t}/{stem}_tex.nsbtx', 'wb').write(btx)
        o = f'{t}/out'
        r = subprocess.run([APICULA, 'convert', f'{t}/{stem}.nsbmd', f'{t}/{stem}_tex.nsbtx', '-o', o, '-f', 'glb'],
                           capture_output=True, text=True)
        glbs = [f for f in os.listdir(o) if f.endswith('.glb')] if os.path.isdir(o) else []
        if not glbs:
            print('  apicula failed for', stem, r.stderr.strip()[-200:])
            return None
        dst = f'{out_dir}/{stem}'  # keep the .glb with its texture .pngs (apicula writes images beside it)
        shutil.rmtree(dst, ignore_errors=True)
        shutil.move(o, dst)
        return f'{stem}/{glbs[0]}'

def main(group, specs):
    out_dir = os.path.join(ROOT, 'work/models', group)
    os.makedirs(out_dir, exist_ok=True)
    models = []
    for spec in specs:
        kind, *args = spec.split(':')
        if kind in ('pack', 'ipack'):
            pid, ext = int(args[0]), kind == 'pack'
            btx = building_textures(F, pid, ext)
            for b in building_pack(F, pid, ext):
                stem = f"{kind}{pid}_{b['res_id']:03d}_{b['name']}"
                path = convert(b['bmd'], btx, out_dir, stem)
                if path:
                    models.append(dict(path=path, label=b['name'],
                                       note=f"{'ext' if ext else 'int'} pack {pid}, res {b['res_id']}"))
        elif kind == 'chunk':
            cid, area_id = int(args[0]), int(args[1])
            magic, secs = chunk(F, cid)
            a = area(F, area_id)
            stem = f'chunk{cid:04d}_area{area_id}'
            path = convert(secs[0], map_textures(F, a['texset']), out_dir, stem)
            if path:
                models.append(dict(path=path, label=f'chunk {cid}',
                                   note=f"{magic}, area {area_id}, {len(chunk_buildings(F, cid))} buildings"))
    json.dump(dict(title=group, models=models), open(f'{out_dir}/manifest.json', 'w'), indent=1)
    print(f'{group}: {len(models)} models -> {out_dir}')

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2:])
