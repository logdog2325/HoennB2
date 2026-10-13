import sys, ctypes, time; sys.path.insert(0, sys.path[0])
from pt import *
g = G('intro3.dst')
lib = g.e.d.lib
base = ctypes.addressof(ctypes.c_ubyte.in_dll(lib, 'MMU'))
t = time.time(); ref = g.raw(0x02140000, 0x2000); print('slow read', time.time() - t)
for off in (0xC000, 0x8000 + 0x4000, 0x10000, 0xC000 + 0x10):
    buf = ctypes.string_at(base + off + 0x140000, 0x2000)
    print(hex(off), buf == ref)
t = time.time(); full = ctypes.string_at(base + 0xC000, 0x400000); print('fast full read', time.time() - t)
