"""Encounter rate rules for Hoenn (decision 2026-10-06; notes/RESEARCH_ENCOUNTERS.md).

Black 2's grass/surf rate byte picks one of 12 rules in ENCOUNT_RATE_CONFIGS (overlay 36 .rodata, offset 0x50C94 in
the decompressed arm9_ov036.bin; 12 x {inc, period, max, min}). Per step the chance is (R+1)/100, where R grows by
inc every period steps from min up to max after entering grass or a battle. Rules 8 and 11 are unused by Black 2.
Rule 8 becomes {9, 1, 10, 2}: no battle on the first 2 grass steps, then a flat 11 % (Sapphire's rate 20 = 11.23 %).
The same recipe {R, 1, R, 2} (flat (R+1) % after 2 safe steps) for every other Sapphire rate, p = 23*rate/4096
rounded to whole percents; the ids are the ones Black 2 only uses for Unova tables we replace (dark grass, Desert
Resort, Route 7/8, unused 11). converter/gen_encounters.py picks the rule from the Sapphire rate:
  land 4 -> 12 (2 %), land 10 -> 11 (6 %), land 15 -> 4 (8 %), land 20 -> 8 (11 %), land 25 -> 9 (14 %),
  water 1 -> 3 (1 %: max 0), water 4 -> 12 (2 %), water 9 -> 5 (5 %)."""
import os

TABLE = 0x50C94
RULES = {                                   # rule id: (vanilla bytes, Hoenn bytes)
    3: (bytes([2, 3, 13, 3]), bytes([0, 1, 0, 2])),
    4: (bytes([2, 2, 19, 2]), bytes([7, 1, 7, 2])),
    5: (bytes([5, 1, 31, 2]), bytes([4, 1, 4, 2])),
    8: (bytes([2, 9, 7, 4]), bytes([9, 1, 10, 2])),
    9: (bytes([2, 3, 13, 3]), bytes([13, 1, 13, 2])),
    11: (bytes([1, 9, 7, 3]), bytes([5, 1, 5, 2])),
    12: (bytes([2, 3, 13, 3]), bytes([1, 1, 1, 2])),
}

def apply_code(code):
    path = os.path.join(code, 'arm9_ov036.bin')
    data = bytearray(open(path, 'rb').read())
    done = []
    for rule, (old, new) in RULES.items():
        at = TABLE + 4 * (rule - 1)
        assert data[at:at + 4] in (old, new), f'rule {rule}: unexpected bytes {data[at:at + 4].hex()}'
        data[at:at + 4] = new
        done.append(f'rule {rule} = {list(new)}')
    if os.path.islink(path): os.unlink(path)
    open(path, 'wb').write(data)
    return ', '.join(done)
