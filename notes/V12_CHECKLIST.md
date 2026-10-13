# v12 build checklist (lead, 2026-10-06)

**Done 2026-10-06 (v12 = builds/hoenn_overworld_v12.nds, commit aaa9a77):** reserves, patch lists, standalone on, rebuild, ledge_check 0 culled/0 gaps, rooms_check 4 findings, states remade (screenshots/v12_opening_check.png). Left: the polish items below, the user's melonDS checks.

Apply together, then rebuild everything and remake the base savestates (all change the ROM layout):
- build_rom.py RESERVE: [8] +~6 MB (45 caves + standalone maps; cave_builder measured ~1.1 MB left with 6 caves),
  [92] = 32 << 10 (trainer parties, Sapphire movesets), [89] = 16 << 10 (story_infra).
- rebuild_slice.sh / agent_build_rooms.sh: add `trainers story` after `centers`.
- Commit the standalone agent's world.py (incl. the ledge-corner lines and cave_builder's foreign_doors),
  gen_map_content.py (standalone frames + story scenes), gen_encounters.py, hoenn_content.json together.
- rebuild_slice.sh (world, towns, rooms, caves) -> ledge_check.py work/world (exit 0) -> rooms_check.py --summary.
- make_states.py on the new ROM; check make_states_check.png.
- Polish pass: (keep "SUMMER" in banners: user wants seasons later); Granite Cave exit shows "Dewford Town"
  (Route 106 in Sapphire); a/0/6/3 still holds Nate/Rosa back sprites (trace use); harbour water darker blue,
  Mt. Pyre grey, Dept Store 5F clerks with lines (verify done).
- User checks in melonDS: all passed (2026-10-06: lab mat, truck door, starter screen, stairs, May's mom, ledges; sprites approved).

## For the next build (v13)
- world.py: outdoor door height = its approach tile's height (Route 125 -> Shoal Cave door is at 0, the water at -8:
  Black 2 fires warps only within 2 units; caves_misc). Done (world_fixes, notes/WORLD.md "World fixes").
- Route 131 -> Sky Pillar door: Sapphire's post-game layout 320 (map replacement once the game is cleared). Done
  (world_fixes): the game-clear scene must also run `MapReplaceSetEvent 7, 1, 0`.
- Patch lists: add caves_east's `boulder_1x1` (Shoal lower room boulder uses model 0x2004).
- Cave/interior chunks must stay under 110,600 bytes (fixed buffer; caves_misc tools/chunksize.py).
- New Mauville barriers stay closed (Sapphire) until the story scripts the switches; Sky Pillar uses Dragonspiral's tan stone.
- Shoal Cave exit warp height fix (caves_misc, approach_y in models_cave_misc.py/models_cave.py/gen_caves.py): uncommitted, mixed with the dive agent's edits in the same files: commit with the dive work.
- DONE (v13): run `python3 converter/gen_key_items.py --install` in the same build (item names/descriptions shift a/0/0/2's file table; old states black-screen at the nickname screen).
- DONE (v13): make HOENN_STORY_CODE=1 the default in patches/story.py (hidden-item table, no Xtransceiver in the new-game Bag) together with gen_key_items.py --install.

## Final map sweep (user request 2026-10-07; after the story)
Comb every map not combed before (the 2026-10-06 rooms sweep fixed 1,323 findings in 196 rooms):
- all 45+ caves (Granite Cave .. Victory Road, Shoal Cave both tides, Sky Pillar, New Mauville, Seafloor Cavern, Sealed Chamber),
  the Dive/underwater maps, the Abandoned Ship (incl. hidden floor) and the Aqua Hideout;
- the 15 standalone outdoor maps (Petalburg Woods .. Sootopolis, Safari Zone, Battle Tower island);
- the connected outdoor world again (the earlier exterior sweep was stopped early), cave mouths, the Route 108 wreck,
  the Route 131 islet, Acro paths, red Route 112 rock, ash areas;
- rooms touched since the sweep (stairs, black partition walls like Dewford Hall / Rustboro Flat 2).
Method: extend the checkers (b2tools/rooms_check.py, ledge_check.py, npc_check.py, check_exits.py, chunk-size,
close surfaces <2 units, back-face culling, warp heights vs approach tiles, collision vs Sapphire walkability) to caves,
underwater and outdoor maps; fix in the generators; then one emulator look per map family.
- DONE (sweep_caves 2026-10-07): the 52 caves and underwater maps (b2tools/caves_check.py, notes/CAVES.md "Cave checks"):
  4,677 findings -> 48 (13 specks of <= 52 px, 22 rim fades = Black 2's own, 13 mildly stretched cliff faces); Navel Rock
  checked too; every family walked in DeSmuME (screenshots/sweep_caves/).
- OUTDOOR PART DONE (sweep_outdoor 2026-10-07, notes/WORLD.md "Outdoor checks and fixes"): b2tools/outdoor_check.py in
  rebuild_slice.sh; towns5 enabled (every route building incl. Winstrate, Rest Stop, Briney, League); waterfalls, water
  levels, bridges, Safari slope, Lavaridge/Weather Institute doors, roofs over water, walls on cliff faces, trainer NPCs
  regenerated in rebuild_slice. The lead: rebuild_slice + remake the savestates (pack 0, chunks changed). Open decision:
  zone rectangles for every map (banners at Sapphire's map edges) need the chapters' cell-zone scripts moved first.
- From ch4: the Winstrate house and the Old Lady's Rest Stop (Route 111) have no building in work/world; a desert zone
  (zone rectangle) would let the desert have Sapphire's sandstorm + desert music (user to decide).
- Rooms (sweep_rooms, 2026-10-07): done for all built rooms (notes/INTERIORS.md "Room sweep 2"): Mt. Pyre's grey gravestones, the Weather Institute's/hideouts'/ship's black slabs (inner_walls), hideout desks, ship desk, Sootopolis statues; rooms_check.py a-l runs in rebuild_slice.sh. Mt. Pyre 1F (20,8) walks fine. Still outdoor: the Winstrate house and the Old Lady's Rest Stop have no building on Route 111.
- From ch8b: Mt. Pyre 1F-6F show pale blue slabs, not the grey gravestones the user chose; Mt. Pyre 1F (20,8) blocks though
  collision.per says walkable; Safari Southeast/Southwest/Rest House people with {POKEBLOCK} text aren't generated (ch8b
  placed them; gen3text should convert the code).
- v14: remake the shared savestates after ch7/ch10/ch11/fixups2/weather/events land (HEAD's ov012 grew to 95048 B vs v13.1's 94584 B; old states never reload ov012, so new ov012 commands like Dewford's 0x1c9 hang on them).
- Text pass: the Secret Power man (Route 111, ch4) and the Slateport Fan Club line talk about Secret Power; his TM43 is Flame Charge: reword to Flame Charge (user rule: name the TM you get). Black 2 TMs are reusable: 'a TM can be used only once' lines were reworded (fixups2).
- Polish leftovers (room sweep 2): Steven's two Poké Balls (Beldum/Dive) stand inside his green table (ch9/ch13 objects: raise
  onto the table); Hall of Fame room has four one-tile black notches in the side walls (Sapphire (1,6), (1,11), (13,6),
  (13,11)); Weather Institute 1F's long wall is now a low white wall (user to judge).
- Events (islands) are DONE but uncommitted: their files are mixed with sweep_caves/sweep_outdoor's in-progress edits
  (world.py, terrain/water.py, models_cave*.py). Commit them together when the sweeps finish; then set
  data/hoenn_standalone.json "build" back to "all", rebuild the Navel Rock caves (gen_caves + rebuild_interiors), run
  gen_map_content, and grow RESERVE[8] (+8 MB) before more legendary islands. notes/EVENTS.md explains adding islands.
- Steven's Route 120 fly-away: with the larger field heap (save fix) Black 2's fly cut-in may now play there (it was skipped under 0xa478 free); retest and restore c7_npc_fly_out if so.
