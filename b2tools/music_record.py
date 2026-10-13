"""Record the game's own sound (notes/MUSIC.md "Recording"): DeSmuME's WAV writer through py-desmume (libdesmume
exports WAV_Begin / WAV_End: the SPU core's mix at 44,100 Hz, 16-bit stereo, in emulated time) while the emulator's
volume stays 0 and SDL's audio driver is the dummy one (nothing plays aloud). Run with ../.venv/bin/python.

    music_record.py save ROM STATE SHOT.png             load STATE (a ROM with the same layout), save in game
    music_record.py boot ROM OUT.wav SECONDS SHOT.png   cold boot, Continue, record SECONDS of sound
    music_record.py state ROM STATE OUT.wav SECONDS      load STATE and record (what the state's RAM plays)

A cold boot reads the sound archive's INFO/FAT and the zone headers from the ROM under test; a savestate keeps the
old ones. The battery file is ~/.config/desmume/<ROM name>.dsv: give each test ROM a name of its own, and never load
a savestate on a ROM name whose battery you need (DeSmuME writes the state's battery back to the .dsv on exit).
"""
import ctypes, os, sys
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

WAVMODE_CORE = 0
SOUND_HEAP = 0x0209E278     # GFL_SndInit: NNS_FrmHeapCreate(0x0209e278, 0x9D000)
FPS = 59.8261               # DS frames per second (560190 cycles per frame at 33.51 MHz)


def wav_begin(emu, path):
    fn = getattr(emu.d.lib, '_Z9WAV_BeginPKc7WAVMode')
    fn.argtypes = [ctypes.c_char_p, ctypes.c_int]; fn.restype = ctypes.c_bool
    assert fn(path.encode(), WAVMODE_CORE), 'WAV_Begin failed'


def wav_end(emu):
    fn = getattr(emu.d.lib, '_Z7WAV_Endv'); fn.restype = None; fn()


def sound_heap(emu):
    """The sound frame heap: NNSiFndHeapHead ('FRMH', link, list, start, end, attribute) + head/tail allocators."""
    import struct
    raw = bytes(emu.d.memory.unsigned[SOUND_HEAP:SOUND_HEAP + 0x40])
    for off in range(0, 0x20, 4):
        if raw[off:off + 4] in (b'HMRF', b'FRMH'):
            start, end, attr, head, tail = struct.unpack_from('<IIIII', raw, off + 24)
            return dict(used=head - start, free=tail - head, size=end - start)


def boot_continue(emu, presses=8):
    emu.run(1200)
    for _ in range(presses): emu.press('A', 6, 60)


def record(emu, out, seconds, shots=None, every=600):
    wav_begin(emu, out)
    frames = int(seconds * FPS)
    done = 0
    while done < frames:
        n = min(every, frames - done); emu.run(n); done += n
        if shots is not None: shots.append(emu.d.screenshot())
    wav_end(emu)


def sheet(shots, path, n=8):
    from PIL import Image
    im = Image.new('RGB', (256 * min(len(shots), n), 384))
    for i, s in enumerate(shots[:n]): im.paste(s, (256 * i, 0))
    im.save(path)


def main(argv):
    from emu import Emu, fresh_battery
    mode = argv[0]
    if mode == 'save':
        rom, state, shot = argv[1:4]
        assert os.path.basename(rom) != 'hoenn.nds'
        fresh_battery(rom)
        e = Emu(rom); e.load_state(state); e.run(2)
        shots = [e.d.screenshot()]
        e.press('X', 6, 40); e.touch(60, 93, 6, 90)          # menu -> SAVE (touch), as opening_polish/save_continue.py
        e.press('A', 6, 60); e.run(400)
        for _ in range(3): e.press('A', 6, 40)
        e.run(900); shots.append(e.d.screenshot())
        e.press('A', 6, 60); e.run(60); shots.append(e.d.screenshot())
        sheet(shots, shot)
        p = os.path.expanduser(f'~/.config/desmume/{os.path.splitext(os.path.basename(rom))[0]}.dsv')
        print('battery', p, os.path.getsize(p) if os.path.exists(p) else 'MISSING')
    elif mode == 'boot':
        rom, out, secs, shot = argv[1], argv[2], float(argv[3]), argv[4]
        e = Emu(rom); boot_continue(e)
        shots = [e.d.screenshot()]
        record(e, out, secs, shots)
        sheet(shots, shot)
        print('recorded', out, 'heap', sound_heap(e))
    elif mode == 'state':
        rom, state, out, secs = argv[1], argv[2], argv[3], float(argv[4])
        e = Emu(rom); e.load_state(state); e.run(2)
        record(e, out, secs)
        print('recorded', out, 'heap', sound_heap(e))


if __name__ == '__main__':
    main(sys.argv[1:])
