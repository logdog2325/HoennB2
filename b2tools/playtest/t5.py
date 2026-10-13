import sys, ctypes; sys.path.insert(0, sys.path[0])
from pt import *
from desmume.controls import keymask
import emu as EM
g = G('intro3.dst')
lib = g.e.d.lib
MAIN = ctypes.addressof(ctypes.c_ubyte.in_dll(lib, 'MMU')) + 0xC000
def u32(a): return ctypes.c_uint32.from_address(MAIN + a - 0x02000000).value
def u16(a): return ctypes.c_uint16.from_address(MAIN + a - 0x02000000).value
def player():
    mm = u32(g.gdata() + 0x1a8); heap = u32(mm + 0x1c)
    for k in range(u16(mm + 4)):
        a = heap + k * 0x100
        if u32(a) & 1 and u16(a + 8) == 255:
            gp = struct.unpack('<3h', ctypes.string_at(MAIN + a + 0x3c - 0x02000000, 6))
            wp = struct.unpack('<3i', ctypes.string_at(MAIN + a + 0x44 - 0x02000000, 12))
            return gp, (wp[0] / 4096, wp[1] / 4096, wp[2] / 4096), u16(a + 0x18)
# in truck at (10,10): walk left (inside truck) holding
g.e.d.input.keypad_add_key(keymask(EM.KEYS['LEFT']))
for f in range(40):
    g.run(1); print(f, player())
g.e.d.input.keypad_rm_key(keymask(EM.KEYS['LEFT']))
for f in range(20):
    g.run(1); print('rel', f, player())
