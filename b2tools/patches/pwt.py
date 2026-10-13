"""Black 2's Pokémon World Tournament (zones 192 lobby / 193 stadium) on the Battle Tower island (battle_tower agent,
2026-10-08; notes/RESEARCH_PWT.md, notes/BATTLE_TOWER.md "The PWT"). Runs after hoenn_world (the island's doors) and
scripts (src/field_scripts/0384_pwt_lobby.s, the lobby's scripts with the Unova story scenes switched off).

The engine keys the PWT on the zone ids 192/193 (script plugins 6/7, gimmicks 51/36, the stadium subscreen): they stay
Black 2's rooms. This patch only:
  - points the lobby's exit mat (entity file 241, warp 0, Black 2's -> zone 191 warp 0, Unova's plaza) at the PWT
    building's door on the Battle Tower island (zone 17: its warp whose destination is zone 192, world.py's door from
    data/hoenn_map_additions.json); without that door (an older world) the exit is left as it is and reported;
  - installs the lobby's map scripts (the tail of entity file 241) from src/field_scripts/0385_pwt_lobby_init.s: Black 2's
    three plus our zone init (0384 entry 19: hide the five Unova story people, flags 890-894, which only Black 2's story
    scenes set; clear the PWT fly flag 2471, whose town-map record 23 flies to zone 191);
  - gives the lobby and the stadium the island's place name (zone headers 192/193 place 36 -> the Battle Tower's line of
    data/hoenn_zones.json: line 36 is Route 117 now, and the rental Pokémon's met location reads the lobby's place);
  - stops the lobby camera before it shows the black below the entrance (camera box 265: z max 440 -> 365; pwt_tower).

apply_code (pwt_tower, 2026-10-11; notes/BATTLE_TOWER.md "PWT tournaments"): which tournaments the desks offer.
Black 2 decides it in ov055 func_ov055_021e65e8 (src/ov055/wbt_tool.c: a switch on the tournament id over the save's 29
win counters and flag 2400), a 16-entry Thumb jump table at 0x021e663e (halfword offsets from 0x021e6640). Only table
entries change (same size, no new code), each pointed at a return that already exists in the function:
  - 8 Hoenn Leaders: Black 2 opens it with Kanto/Johto/Sinnoh (6/7/9) once the Unova Leaders tournament is won
    (counts[19] != 0); here it opens with flag 2400 (FLAG_SYS_GAME_CLEAR, set by Hoenn's Hall of Fame), the case-5 code.
    The island and the right desk (global 10657, `1277.s`) already need the Hall of Fame, so the eighth badge alone can
    never reach it. Kanto/Johto/Sinnoh, World Leaders, Type Expert and the Champions stay Black 2's.
  - 11 the first Driftveil tournament (Black 2's story tournament: the player's Unova rival, nameless here, Cheren and
    Colress, arc 247 records 55-57, byte 5 bit 0): never offered (the `return FALSE` at 0x021e66d8);
  - 4 Driftveil, 3 Download, 12 Rental, 14 Mix: offered from the start (`return TRUE` at 0x021e6664), as Black 2 offers
    them after its story tournament (counts[18] != 0, which only that story win made true at that point)."""
import os, sys, json, struct
import narcio, zoneheaders
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))                     # patches/ (scripts)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))    # b2tools/ (zones)
from zones import parse_entities, build_entities  # noqa: E402

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
LOBBY, STADIUM, ISLAND = 192, 193, 17
LOBBY_CAM_ZMAX = 365                                # see apply(): no black below the entrance
OV055 = 0x021e5800                                  # arm9_ov055.bin load address (overlays.yaml)
UNLOCK_TABLE, UNLOCK_PC = 0x021e663e, 0x021e6640    # func_ov055_021e65e8's jump table; offsets are from this pc
RET_TRUE, RET_FALSE, RET_FLAG_2400 = 0x021e6664, 0x021e66d8, 0x021e669a   # movs r0,#1 / movs r0,#0 (pop) / case 5
UNLOCK = {8: RET_FLAG_2400, 11: RET_FALSE, 3: RET_TRUE, 4: RET_TRUE, 12: RET_TRUE, 14: RET_TRUE}
UNLOCK_B2 = [152, 30, 44, 48, 76, 90, 102, 102, 102, 102, 148, 62, 76, 112, 76, 130]   # Black 2's table (cases 0-15)

def apply_code(code):
    path = os.path.join(code, 'arm9_ov055.bin')
    d = bytearray(open(path, 'rb').read())
    o = UNLOCK_TABLE - OV055
    assert d[RET_TRUE - OV055:RET_TRUE - OV055 + 4] == bytes.fromhex('0120f8bd'), 'ov055: return TRUE not at 0x021e6664'
    assert d[RET_FALSE - OV055:RET_FALSE - OV055 + 4] == bytes.fromhex('0020f8bd'), 'ov055: return FALSE not at 0x021e66d8'
    assert d[RET_FLAG_2400 - OV055:RET_FLAG_2400 - OV055 + 6] == bytes.fromhex('962160460901'), 'ov055: case 5 moved'
    new = [UNLOCK.get(i, None) for i in range(16)]
    new = [UNLOCK_B2[i] if t is None else t - UNLOCK_PC for i, t in enumerate(new)]
    have = list(struct.unpack_from('<16h', d, o))
    assert have in (UNLOCK_B2, new), f'ov055 tournament table is not Black 2\'s: {have}'
    struct.pack_into('<16h', d, o, *new)
    if os.path.islink(path): os.unlink(path)
    open(path + '.tmp', 'wb').write(d); os.replace(path + '.tmp', path)
    return ('PWT tournaments: Hoenn Leaders open with the Hall of Fame (flag 2400); the first (story) Driftveil '
            'tournament never; Driftveil, Download, Rental, Mix from the start (ov055 0x021e663e table)')

def apply(files):
    from scripts import assemble, source_for
    headers, hentries = zoneheaders.load(files)
    place = json.load(open(os.path.join(ROOT, 'data', 'hoenn_zones.json')))['places']['MAPSEC_BATTLE_TOWER']['line']
    for z in (LOBBY, STADIUM):
        headers[z]['place'] = place
    zoneheaders.save(files, headers, hentries)
    ents = narcio.load(files, 126)
    island, _ = parse_entities(ents[headers[ISLAND]['entities']])
    door = next((i for i, w in enumerate(island['warps']) if w['dest_zone'] == LOBBY), None)
    idx = headers[LOBBY]['entities']
    e, _ = parse_entities(ents[idx])
    assert e['warps'][0]['type'] == 1 and e['warps'][0]['dest_zone'] in (191, ISLAND), e['warps'][0]
    done = [f'zones {LOBBY}/{STADIUM}: place {place}']
    if door is None:
        done.append(f'no door to zone {LOBBY} on the island (zone {ISLAND}): the lobby exit is left -> zone '
                    f'{e["warps"][0]["dest_zone"]} warp {e["warps"][0]["dest_warp"]}')
    else:
        e['warps'][0]['dest_zone'], e['warps'][0]['dest_warp'] = ISLAND, door
        done.append(f'lobby exit -> zone {ISLAND} warp {door}')
    init = source_for(headers[LOBBY]['init_scripts'])
    assert init and init.endswith('_pwt_lobby_init.s'), init
    ents[idx] = build_entities(e, ents[idx], assemble(init))
    narcio.save(files, 126, ents)
    done.append(f'lobby map scripts from {os.path.basename(init)}')
    # camera box (a/1/0/9, Black 2's format: u32 1; u32 1, 0; s32 xmin, xmax, zmin, zmax, local units): Black 2 lets the
    # lobby's camera follow the player onto the entrance mat, so the black south of the room's geometry (it ends about a
    # row past the mat, local z 447) fills the bottom of the screen there (vanilla Black 2 looks the same; the user chose
    # to hide it, 2026-10-11). Camera 0 shows the floor 82 units south of its target at the screen's bottom edge, so the
    # target stops at 447 - 82 = 365: no black row on any screen (tested), the player stays in view at the mat.
    cams = narcio.load(files, 109)
    box = headers[LOBBY]['cam_bound']
    assert sum(h['cam_bound'] == box for h in headers) == 1, f'camera box {box} is shared'
    vals = list(struct.unpack('<7i', cams[box]))
    assert vals[3:] in ([72, 424, 24, 440], [72, 424, 24, LOBBY_CAM_ZMAX]), vals
    vals[6] = LOBBY_CAM_ZMAX
    cams[box] = struct.pack('<7i', *vals)
    narcio.save(files, 109, cams)
    done.append(f'lobby camera box {box}: z max 440 -> {LOBBY_CAM_ZMAX}')
    return '; '.join(done)
