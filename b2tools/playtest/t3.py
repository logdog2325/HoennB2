import sys, ctypes; sys.path.insert(0, sys.path[0])
from pt import *
g = G('intro3.dst')
g.press('RIGHT', 6, 30); g.run(500)
lib = g.e.d.lib
MAIN = ctypes.addressof(ctypes.c_ubyte.in_dll(lib, 'MMU')) + 0xC000
def u32(a): return ctypes.c_uint32.from_address(MAIN + a - 0x02000000).value
def u16(a): return ctypes.c_uint16.from_address(MAIN + a - 0x02000000).value
gd = g.gdata(); mm = u32(gd + 0x1a8)
print('mmsys', hex(mm), 'cap', u16(mm + 4), 'count', u16(mm + 6), 'heap', hex(u32(mm + 0x1c)))
heap = u32(mm + 0x1c)
for stride in range(0xe8, 0x200, 4):
    if sum(u32(heap + k * stride + 0x88) == mm for k in range(u16(mm + 6))) == u16(mm + 6):
        print('stride', hex(stride))
stride = 0x100
for k in range(u16(mm + 4)):
    a = heap + k * stride
    fl = u32(a)
    if not fl & 1: continue
    gp = struct.unpack('<3h', bytes(ctypes.string_at(MAIN + a + 0x3c - 0x02000000, 6)))
    print(k, hex(fl), 'uid', u16(a + 8), 'zone', u16(a + 0xa), 'model', u16(a + 0xc), 'move', u16(a + 0xe), 'scr', u16(a + 0x14), 'face', u16(a + 0x18), 'gpos', gp)
