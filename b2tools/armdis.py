"""Disassemble Thumb code from the decomp's built binaries with llvm-mc, resolving pc-relative literals.

    python3 armdis.py arm9 0x02018a54 0x02018ef0          (or ov036 0x021ab92c 0x021ab974)
Binary bases: arm9 0x02004000 (arm9.bin offset 0x15130 = 0x02019130); overlays from the decomp's overlay table."""
import sys, os, re, struct, subprocess, yaml
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
BUILD = os.path.join(ROOT, 'external', 'pokebw2', 'build', 'b2_us', 'build')
LLVM = '/opt/homebrew/opt/llvm/bin/llvm-mc'

def image(name):
    if name == 'arm9':
        return open(os.path.join(BUILD, 'arm9.bin'), 'rb').read(), 0x02004000
    n = int(name[2:])
    table = os.path.join(ROOT, 'external', 'pokebw2', 'extract', 'b2_us', 'arm9_overlays', 'overlays.yaml')
    base, cur = None, None
    for line in open(table):                      # "- id: N" then "base_address: <decimal>"
        m = re.match(r'\s*-\s*id:\s*(\d+)', line)
        if m: cur = int(m.group(1)); continue
        m = re.match(r'\s*base_address:\s*(\d+)', line)
        if m and cur == n: base = int(m.group(1)); break
    return open(os.path.join(BUILD, f'arm9_ov{n:03d}.bin'), 'rb').read(), base

def symbols(name):
    p = os.path.join(ROOT, 'external', 'pokebw2', 'config', 'b2_us', 'arm9',
                     'symbols.txt' if name == 'arm9' else f'overlays/ov{int(name[2:]):03d}/symbols.txt')
    out = {}
    for line in open(p):
        m = re.match(r'(\S+) kind:(\w+)\S* addr:(0x[0-9a-f]+)', line)
        if m: out[int(m.group(3), 16)] = m.group(1)
    return out

def dis(name, start, end):
    data, base = image(name)
    sy = symbols(name)
    code = data[start - base:end - base]
    r = subprocess.run([LLVM, '--disassemble', '-triple=thumbv5te-none-eabi'], input=' '.join(f'0x{b:02x}' for b in code),
                       capture_output=True, text=True)
    lines = [l.strip() for l in r.stdout.splitlines() if l.strip() and not l.strip().startswith('.')]
    addr = start; out = []
    for l in lines:
        if addr in sy: out.append(f'{sy[addr]}:')
        size = 4 if l.startswith(('bl\t', 'blx\t')) and not l.startswith('blx\tr') else 2
        note = ''
        m = re.match(r'ldr\s+r\d+, \[pc, #(\d+)\]', l)
        if m:
            lit = ((addr + 4) & ~3) + int(m.group(1))
            if base <= lit < base + len(data) - 3:
                v = struct.unpack_from('<I', data, lit - base)[0]
                note = f'   ; ={v:#x} ({v})' + (f' {sy[v & ~1]}' if (v & ~1) in sy else '')
        m = re.match(r'bl\s+#(-?\d+)', l)
        if m:
            tgt = addr + 4 + int(m.group(1))
            note = f'   ; -> {sy.get(tgt, sy.get(tgt & ~1, hex(tgt)))}'
        out.append(f'  {addr:08x}  {l}{note}')
        addr += size
    return '\n'.join(out)

if __name__ == '__main__':
    print(dis(sys.argv[1], int(sys.argv[2], 16), int(sys.argv[3], 16)))
