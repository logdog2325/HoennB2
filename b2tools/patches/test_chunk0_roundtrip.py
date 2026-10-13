"""TEST ONLY: Nuvema's terrain (chunk 0 model) replaced by the same terrain re-written through apicula (DAE) and
CTRMapV's NSBMDWriter (work/t1/rt.nsbmd). Collision and buildings untouched. Proves the game accepts our models."""
import os
import narcio
from b2files import gf_container, gf_container_build

def apply(files):
    model = open(os.path.join(os.path.dirname(__file__), '..', '..', 'work', 't1', 'rt.nsbmd'), 'rb').read()
    chunks = narcio.load(files, 8)
    magic, secs = gf_container(chunks[0])
    old = len(secs[0]); secs[0] = model
    chunks[0] = gf_container_build(magic, secs)
    narcio.save(files, 8, chunks)
    return f'chunk 0 model {old} -> {len(model)} bytes'
