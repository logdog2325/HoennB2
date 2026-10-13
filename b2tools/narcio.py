"""Edit NARC archives in a files/ tree using the decomp's own reader/writer (tools/scripts/narc.py)."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'external', 'pokebw2', 'tools', 'scripts'))
from narc import read_narc, write_narc  # noqa: E402
from b2files import arc_path  # noqa: E402

def load(files_dir, arc):
    return read_narc(open(arc_path(files_dir, arc), 'rb').read())

def save(files_dir, arc, entries):
    path = arc_path(files_dir, arc)
    if os.path.islink(path): os.unlink(path)
    tmp = path + '.tmp'
    open(tmp, 'wb').write(write_narc(entries))
    os.replace(tmp, path)  # never write through to the clone source
