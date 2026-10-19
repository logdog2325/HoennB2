"""Link play between Pokémon Sapphire, Ruby and Emerald NDS (link, 2026-10-18; notes/LINK.md): friend trades and
battles over local wireless (Black 2's Union Room) and Nintendo WFC (Black 2's Wi-Fi Club), reached from the Pokémon
Centers' 2F attendants (b2tools/centers_rooms.py, src/field_scripts/1231_global_2100.s). Battle rules: fairy.c
"Link battles" (the server machine's Fairy / split options for both machines). This patch keeps every other game out:
the local wireless id and the Wi-Fi Club's status bytes.

The wireless id (apply_code). Black 2's net library keeps a GGID in each connection setup (GFLNetInitData +0x50,
include/gfl/net.h unk4C[4..7]; 0x1380 in Black 2's tables). Overlay 30, the wireless device layer, passes it to the
DS wireless library (func_ov030_02173340 -> func_ov030_02174e28; func_ov030_02173d44 -> func_ov030_021755dc with each
beacon), writes its low half into every beacon's GFL header (+2, func_ov030_02173780: `ldr r0, [r7, #0x50]; strh r0,
[r4, #2]`) and drops every beacon whose +2 differs before the game sees it (func_ov030_021733dc: `ldr r0, [r6, #0x50]`
... `ldrh r0, [r4, #2]; cmp r0, r7`, after the header's CRC16).
The Union Room's setup (ov028 data 0x02172c94, gameCommandBase 0x14, 5 machines) gets LINK_GGID instead, so in the
Union Room HoennB2 builds see only each other: an unmodified Black 2 / White 2 (and a HoennB2 release before link,
whose battle rules and data differ) never shows up there, and never sees us. The other tables with 0x1380 (C-Gear,
infrared and friends) are out of Hoenn's reach and stay Black 2's. A later link change that makes builds incompatible
again takes the next id (0x4843...).

The Wi-Fi Club (apply_code; read from the code by the wifi research, 2026-10-18, never tested online). Nintendo WFC
(Wiimmfi today) does not use the GGID: the club (ov173 main code, ov203 its proc, ov190 the login, ov011 the DWC
library and Game Freak's wrapper) lists a Pal Pad friend only when the friend's 32-byte GameSpy status data, which
every club publishes (func_ov173_021a208c fills it, func_ov011_02151ab4 -> DWC_SetOwnStatusData), says "in the club":
its +0x18 (club status) is 1-5 (func_ov173_021a2124: friend index < count, DWC status != 0, +0x18 in 1..5); and the
host drops a client whose +0x17 (game type: single battle, trade...) differs from its own (func_ov173_021a2800 via the
matched callback func_ov011_02151cd4). Every access to those two bytes goes through four 4-byte accessors
(func_ov173_021a61c0/c4 +0x18, func_ov173_021a61c8/cc +0x17; ov173's own calls and two function pointers at
0x021a16e8/0x021a16f4). HoennB2 keeps them at +0x1d / +0x1e instead, bytes Black 2 allocates cleared and never writes
or reads: an unmodified Black 2 / White 2 (or a HoennB2 release before link) reads a HoennB2 friend's status as 0 and
does not list it, HoennB2 reads theirs as 0 and does not list them, and if a connection ever came about, the host's
game-type check drops the stranger (0 never matches a host's game type). HoennB2 with HoennB2 works as before. (A
later incompatible link change can move them again, to +0x1f.) Black / White 1's status layout was not checked.

Checked against Black 2's bytes (every site asserts the old value)."""
import os, struct

OV028 = 0x02170340                   # arm9_ov028.bin load address (extract/b2_us/arm9_overlays/overlays.yaml)
UNION_ROOM_NET_INIT = 0x02172C94     # ov028's GFLNetInitData (0x70 bytes): commands 0x02172d04 x 22, gameCommandBase 0x14
GGID_OFFSET = 0x50
BLACK2_GGID = 0x1380
LINK_GGID = 0x4842                   # 'HB': HoennB2 link protocol 1 (Sapphire, Ruby and Emerald NDS from link on)


def _load(code, name):
    p = os.path.join(code, name)
    return p, bytearray(open(p, 'rb').read())


def _save(p, d):
    if os.path.islink(p): os.unlink(p)
    open(p + '.tmp', 'wb').write(d); os.replace(p + '.tmp', p)


OV173 = 0x0219CE80                   # arm9_ov173.bin load address
CLUB_STATUS = [   # (accessor, Black 2's ldrb/strb, HoennB2's)
    (0x021A61C0, 0x7E00, 0x7F40, 'club status get: ldrb r0, [r0, #0x18] -> #0x1d'),
    (0x021A61C4, 0x7601, 0x7741, 'club status set: strb r1, [r0, #0x18] -> #0x1d'),
    (0x021A61C8, 0x7DC0, 0x7F80, 'game type get: ldrb r0, [r0, #0x17] -> #0x1e'),
    (0x021A61CC, 0x75C1, 0x7781, 'game type set: strb r1, [r0, #0x17] -> #0x1e'),
]
BX_LR = 0x4770


def apply_code(code):
    p173, ov173 = _load(code, 'arm9_ov173.bin')
    for at, old, new, what in CLUB_STATUS:
        o = at - OV173
        cur, ret = struct.unpack_from('<HH', ov173, o)
        assert ret == BX_LR and cur in (old, new), f'link: ov173 {at:#x} ({what}): {cur:#06x} {ret:#06x}'
        struct.pack_into('<H', ov173, o, new)
    _save(p173, ov173)
    p, ov028 = _load(code, 'arm9_ov028.bin')
    o = UNION_ROOM_NET_INIT - OV028
    cmds, ncmds = struct.unpack_from('<II', ov028, o)
    assert (cmds, ncmds, ov028[o + 0x67], ov028[o + 0x60]) == (0x02172D04, 22, 0x14, 5), \
        f'link: ov028 {UNION_ROOM_NET_INIT:#x} is not the Union Room\'s net setup ({cmds:#x}, {ncmds})'
    cur = struct.unpack_from('<I', ov028, o + GGID_OFFSET)[0]
    if cur != LINK_GGID:
        assert cur == BLACK2_GGID, f'link: Union Room GGID is {cur:#x}, expected Black 2\'s {BLACK2_GGID:#x}'
        struct.pack_into('<I', ov028, o + GGID_OFFSET, LINK_GGID)
        _save(p, ov028)
    return (f'link: Union Room GGID {BLACK2_GGID:#x} -> {LINK_GGID:#x} (ov028 {UNION_ROOM_NET_INIT + GGID_OFFSET:#x}); '
            f'Wi-Fi Club status +0x18/+0x17 -> +0x1d/+0x1e (ov173, {len(CLUB_STATUS)} accessors)')
