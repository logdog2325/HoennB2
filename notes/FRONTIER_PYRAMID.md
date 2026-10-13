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
- The field Bag opens on the Items pocket, which is empty in the Battle Bag (items are in Medicine / Berries).
- Area 291 is shared with zones 526-530 (not checked whether any is a Hoenn zone; check before changing its textures).
- The lead's world needs a rebuild (with the claim, world.py opens zone 17's door 3 to the lobby) and
  rebuild_interiors must build the two rooms. Add `frontier_pyramid` after `rods` in the Emerald build lists.

## Testing
work/agents/frontier_pyramid/tools: build.sh (env HOENN_TEST_WARP=347,7,13 puts a test door at Littleroot (183,366));
boot.py, drive.py (Q state, F floor map, Ox,z / In walking on the floor), pyr.py (reads the challenge from RAM and
recomputes the floor). The test party switch was removed; a test now needs three Pokemon in the party.
