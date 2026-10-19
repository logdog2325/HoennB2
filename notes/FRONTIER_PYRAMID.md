# Battle Pyramid (frontier_pyramid, Emerald only)

Status 2026-10-12: the core works in game (tested on an Emerald build, muted). Brandon, Rest/Continue and a real
battle loss were not tested (the lead scoped the work down). Claims and code space: notes/FRONTIER.md section 6.

## How it is built
- Rooms: lobby (zone 347) and top (zone 420) are built rooms (data/interior_layouts/BattleFrontier_BattlePyramid{Lobby,Top}.json,
  style `_styles_frontier_pyramid.json`: Relic Castle textures of map set 291). The writer is
  work/agents/frontier_pyramid/tools/rooms.py (also data/interiors/emerald/347, 388, 420.json).
- Floor (zone 388): no room. b2tools/pyramid_models.py makes a 32x32 base model, Emerald's 16 square wall models and the exit
  panel; the frontier_pyramid patch installs them as an RD chunk (matrix 1x1, area 291). At load the engine
  (b2tools/patches/frontier_pyramid.c) rewrites the floor's collision and places the 16 squares as props, from Emerald's
  algorithm (templates, layout offsets, entrance/exit, object placement), seeded by the save's randoms.
- Darkness: Black 2's Flash circle (zone_effects' `h_flash_scale`, script command 0x1C9) at Emerald's radius: 32 px on
  arrival, +4 per battle won, up to 120. Tested: the circle shows on arrival and grows after battles (light 32 -> 36).
- Trainers: the floor's people 1-8 get places, sprites and scripts at zone init; sight is checked each step
  (EventTrainerEye_CalcLineOfSight); battles use trainer slot 532 filled with Emerald's Frontier trainer and party
  (frontier_pike's data file). After a win, talking to the trainer gives Emerald's hint.
- Wild Pokemon: Emerald's per-floor tables, rate and level rules (Lv. 50: table level -5..+5).
- Items: Emerald's pickup tables; found items go into the Battle Bag.
- Battle Bag: while in the Pyramid, the game's bag pointer (gd+0x190) points at a heap bag built from the Pyramid's
  own store (10 items x 2 level modes in save block 0x3e). The player's own bag (save block 0x19) is never touched; the
  pointer is put back when the challenge ends. Save block 0x3e grows 16 -> 112 B inside its 256-byte slot.
- Start menu Save on a floor or the top = Emerald's Rest / Retire menu.
- Code: engine ~11.8 KB + 2.8 KB RAM loaded into heap 4 on demand; 4 B ITCM; hooks in ov012 / ov036 dead code.
  Script command 530 `EmPyr var, op, a`; its permission byte is 7 so map scripts may run it (with Black 2's 1 the
  floor's zone init stopped the script VM: a black screen).

## Tested (screenshots/frontier_pyramid/)
Lobby menus and the 3 picks (01-02); floor 1 dark arrival (03); a trainer spots the player, battle, Hyper Potion from
the Battle Bag used in battle (04-09); hint after the battle (10); an item ball into the Battle Bag (11-12); the exit
panel to floor 2 with the quiet save (13); a wild battle (Minun Lv. 40) and the light growing after it (14-15); the
Rest/Retire menu, Retire -> lobby, the Battle Bag cleared and the player's own Bag (with a Potion put there for the
test) back (16-19). Retire runs the same script path as a battle loss (L_PYF_Lost).

## Left to do
- Test Rest -> Continue -> resume on the rested tile; a real battle loss; floors 3-7; the top and Brandon (slot 533,
  Emerald's streaks 21/70/35); Open Level.
- The battle's "X defeated Y" line shows "Player" instead of the player's name (seen once; not looked into).
- (Done 2026-10-18) The field Bag opened on the Items pocket, empty in the Battle Bag (its items are Medicine / Berries).
  Now the Battle Bag has its own position (pokeemerald's Pyramid Bag keeps its own): the player's Bag cursor (GameData +
  0x18C: scroll[6], index[6], pocket at 0x18) is put aside at bag_swap and back at bag_unswap; the Battle Bag starts on its
  first pocket with items, and when its pocket is empty the Bag opens on the first one with items: frontier_pyramid.c
  bag_pocket, run when the field Bag opens (ov012's launcher func_ov012_0215bd48: its func_02034ad0 / func_020088a4 calls
  -> frontier_pyramid_stub.c PY_I_BagNew / PY_I_BagPocket -> engine entry PY_BagOpen) and on every field frame of a floor.
  Tested in DeSmuME (screenshots/emerald_fidelity/py_*): floor 1 opens on Medicine (Hyper Potion, Ether); the player's
  own pocket (Berries, set before the challenge) is back in the lobby.
- (Done 2026-10-18) The lobby's "{0100:0} got the Bag back." (the lost and didn't-save lines) showed no name: the
  library's lines read word buffer 0, which Sub_PYL_Lost / Sub_PYL_Quit never set. Both now end with WordSetPlayerName 0
  (0694_room_BattleFrontier_BattlePyramidLobby.s), as Sub_PYL_Won already did.
- Self-test 2026-10-18 (work/agents/emerald_fidelity/tests/pyramid_floors.py, log/pyramid_floors*.txt): streak 14 (floors
  15-21), floors 1-7: each layout as pyr.py recomputes it, exits to the next floor, an item ball, trainers that see the
  player, wild battles; the top, Brandon (Regirock / Registeel / Regice, silver) and the lost path back to the lobby.
- Area 291 is shared with zones 526-530 (not checked whether any is a Hoenn zone; check before changing its textures).
- The lead's world needs a rebuild (with the claim, world.py opens zone 17's door 3 to the lobby) and
  rebuild_interiors must build the two rooms. Add `frontier_pyramid` after `rods` in the Emerald build lists.

## Testing
work/agents/frontier_pyramid/tools: build.sh (env HOENN_TEST_WARP=347,7,13 puts a test door at Littleroot (183,366));
boot.py, drive.py (Q state, F floor map, Ox,z / In walking on the floor), pyr.py (reads the challenge from RAM and
recomputes the floor). The test party switch was removed; a test now needs three Pokemon in the party.
