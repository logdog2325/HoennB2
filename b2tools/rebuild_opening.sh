#!/bin/zsh
# Build the opening's assets (notes/OPENING.md): the truck interior chunk, its rear-door building, and the texture
# sets they need, merged losslessly by nsbtx.py (map texture set 284 + Plasma Frigate metal from set 379; interior building textures 2 + the door's).
# Output in work/interiors/truck; installed by b2tools/patches/opening.py.
set -e -o pipefail
cd ~/Documents/GitHub/HoennB2 && source env.sh
CP="work/java:tools/CTRMap.jar:tools/ctrmap-plugins/CTRMapV-1.4.1.jar"
mkdir -p work/java && javac -cp "$CP" -d work/java b2tools/java/*.java
O=work/interiors/truck
(cd b2tools && python3 models_truck.py ../$O && python3 -c "
import b2files as b
F = '../external/pokebw2/build/b2_us/files'
for ts in (284, 379): open(f'../work/tex/map{ts}.nsbtx', 'wb').write(b.map_textures(F, ts))
open('../work/tex/ipack02.nsbtx', 'wb').write(b.building_textures(F, 2, exterior=False))
import nsbtx
pairs = set().union(*(nsbtx.material_pairs(x['bmd']) for x in b.building_pack(F, 2, exterior=False)))
open('../work/tex/ipal02.txt', 'w').write(''.join(f'{t} {p}\\n' for t, p in sorted(pairs) if p))")
for m in terrain door; do java -Djava.awt.headless=true -cp "$CP" ToNsbmd $O/$m.dae $O/$m.nsbmd $O/palettes.txt > /dev/null; done
python3 b2tools/nsbtx.py merge work/tex/map284.nsbtx $O/texset284.nsbtx \
  $(python3 -c "import json; print(' '.join(f'work/tex/map{s}.nsbtx:{t}' for t, s in json.load(open('$O/truck.json'))['textures'].items()))") > /dev/null
python3 b2tools/nsbtx.py merge work/tex/ipack02.nsbtx $O/ipack02.nsbtx work/tex/ipal02.txt \
  $(python3 -c "import json; print(' '.join(f'work/tex/map379.nsbtx:{t}' for t in json.load(open('$O/truck.json'))['door_textures']))") > /dev/null
ls -la $O/*.nsbmd $O/*.nsbtx
