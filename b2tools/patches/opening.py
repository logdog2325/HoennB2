"""Sapphire's opening (notes/OPENING.md): a new game starts in the moving truck instead of Aspertia City.

Black 2 picks the first map in code: EventFieldFirst_Create -> LoadAspertiaCitySpawnInfo, whose zone number is the
literal word at arm9.bin offset 0x15130 (427 = Aspertia; notes/RESEARCH_STORY_SPRITES.md section 2). The game loads
that zone at its header's fly position, then runs the zone's scripts 29 and 30. The truck is zone 394 (a spare
interior of Nuvema Town: its own matrix 35, scripts 788/789, text 623, entities 571; Littleroot does not use it)."""
import os

NEW_GAME_ZONE = 0x15130          # arm9.bin offset of the literal 0x1ab
VANILLA, TRUCK, LITTLEROOT = 427, 394, 389
START = TRUCK             # zone 394, the moving truck (src/field_scripts/scenes/truck.inc)

def apply_code(code):
    path = os.path.join(code, 'arm9.bin')
    data = bytearray(open(path, 'rb').read())
    old = int.from_bytes(data[NEW_GAME_ZONE:NEW_GAME_ZONE + 4], 'little')
    assert old in (VANILLA, TRUCK, LITTLEROOT), f'unexpected new-game zone literal {old}'
    data[NEW_GAME_ZONE:NEW_GAME_ZONE + 4] = START.to_bytes(4, 'little')
    if os.path.islink(path): os.unlink(path)
    open(path, 'wb').write(data)
    return f'new game starts in zone {START} (was {old})'
