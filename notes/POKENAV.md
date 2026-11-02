# The PokéNav (pokenav, v18.4 / Emerald v1.5)

A real app in place of Black 2's Xtransceiver. Item 621/626 is still the item; only what it opens changed.

## How it runs
- It is a mode of the field's touch screen, as the X menu and the Pokétch are: the overworld stays drawn on top and an event holds the
  player (and the NPCs, `DisableAllActorsMovement`) until it closes. User's decision, 2026-11-01.
- Screen: decomp `src/ov036/field_subscreen.c`, the `FLD_SUBSCREEN_ID_CGEAR_POWEROFF` row (no Hoenn script starts the C-Gear's power
  animation; its functions stay compiled, `HOENNB2_STATIC`) calls `src/hoennb2/resident/pokenav_event.c`, which loads overlay 345 while
  the screen shows. The overlay (`src/hoennb2/pokenav/`, 6.6 KB, `APP_OVERLAYS` in `tools/hoennb2/link_overlays.py`) sits after the
  resident section, clear of everything the field loads.
- Start: the registered Key Item goes through `FIELD_PROC_LINK_LIST`'s Xtransceiver row, whose `call` chains the event (as the save).
  The Bag's `sItemMenuFieldUses` row sets a pending flag and asks for common event 1 (the Pokéblock Case's way; `contest_cmd.c` asks
  `HoennB2_PokenavTakePending` first), so the field comes back, then the event starts. Black 2's scripted Xtransceiver calls
  (`scrcmd_proc_fld.c`) still open overlay 259.
- End: the event asks for `FLD_SUBSCREEN_ID_DEFAULT` (Black 2's bottom-screen wipe to the normal screen), then lets the player go.
- Hoenn Map: the town map's overlay 144 overlaps the field's overlay 36, so it can't run beside the field. It goes full-screen through
  `EventFieldSubprocessTransition` (it fades, and brings the field's 3D surface back: a bare `EventFieldSubprocessCall` leaves both to its caller); `GameData_SetLastSubscreen` makes the field come back with the PokéNav's menu, at its cursor.
- Data: `b2tools/patches/pokenav.py` (after `text`, last in the patch lists) appends 8 files to a/0/0/2: one LZ10 file per view, the
  contacts, the text (`b2tools/pokenav_art.py`). Numbers are taken at build time, and go in `gHoennB2Pokenav` (resident section).
- Save: nothing new. Registered = a story flag or Black 2's defeat flag (id + 0x5F0). Flags 2569-2572 and works 0x4196-0x4199 are unused.

## Memory and VRAM
- Measured on the combined Sapphire ROM (2026-11-01; DeSmuME; outdoors, follower out where it showed: Route 104, Fortree, Lilycove, Slateport,
  Mauville, Route 120 with 44 actors): field heap 100,988-101,020 B free, largest block at least 93 KB; `HEAPID_FIELD_MENU` 61,368 B free;
  `HEAPID_USER` 28,776 B free, not used. Emerald still to read (its v1.4 log has the same pack 0 figure).
- Use: `HEAPID_FIELD_MENU` about 32 KB (work, font, text, tables); the field heap about 60 KB at its peak (the view's file while it unpacks, BG
  maps, windows, the sprite's buffers). No save can run while it is open.
- `pokenav_event.c` checks first: under `NEED_FIELD_HEAP` (64 KB) or `NEED_MENU_HEAP` (36 KB) free, the game's own can't-use line shows and it
  doesn't open.
- VRAM: bank H, 32 KB: four maps from 0x6000, then 768 tiles from 0 for art + windows (`CHAR_LIMIT`; `pokenav_art.py` stops the build over it).
  OBJ: none.

## Screens (all on the touch screen)
| Screen | What |
|---|---|
| Menu | Gen 3's buttons, description box, device outline |
| Hoenn Map | full-screen, as above; back to the menu |
| Condition | party, no eggs (Gen 3); Up and Down: sprite, heading, "1/6", five-sided graph, sheen sparkles |
| Trainer's Eyes / Match Call | registered contacts; A: name, class, place, Gen 3's strategy / Pokémon / introduction lines |
| Ribbons | Pokémon with ribbons, with counts (party, then 24 boxes, one box a frame while black) |
| A Pokémon's ribbons | sprite, Gen 3's grid (nine to a row), big icon; Black 2's name and description in a wider box |

Ribbons is hidden until `FLAG_SYS_RIBBON_GET`, as Gen 3. Names and descriptions come from Black 2's ribbon text (bank 361), in the order
of `src/ov207/ribbon.c`.

## Per version
- Sapphire, Ruby: pokeruby's art; pokeruby's 56 `gTrainerEyeTrainers`, registered by the first battle's defeat flag. **No rematch mark:
  these versions have no rematch system.** The mark would appear if a contact row ever gets a rematch row.
- Emerald: pokeemerald's art; Match Call: Mr. Stone, Birch, the rival by the player's sex, Wally, Dad, Mom, Steven, Scott, 7 other Leaders,
  the Elite Four, Wallace, then the 64 route trainers. The rematch mark follows `emerald_rematch.c` `tier_now`, read only.
- Emerald's FLAG_ENABLE_*_MATCH_CALL do not exist in this port, so these use the nearest story flag: Mr. Stone, Mom = received the PokéNav;
  Birch, Scott = delivered the Devon Goods; rival = FLAG_REGISTER_RIVAL_POKENAV; Dad = beat the rival on Route 104; Steven = delivered his letter;
  Wally = beat him in Mauville; Leaders and Elite Four = beat them.

## Left out, or different from Gen 3
- Incoming and outgoing calls (Emerald's Call option and its messages), the trainer's picture on the check page.
- Condition: Search (all boxes by stat), markings, the graph's slide between Pokémon.
- Everything is BG tiles, so a selected button moves 8 pixels (Gen 3: 10), and nothing animates: no spinning device, sliding lists, sparkle
  twinkling or glowing light. Emerald's "Pokémon Navigator" band has no room.
- Ribbon grid: gift ribbons follow the others instead of starting a new row. Black 2's ribbons that Gen 3 lacks (never given in Hoenn) use the
  first gift picture. At most 36 are listed.
- Keys only, no touch.

## Checks
`python3 b2tools/pokenav_check.py FILES_DIR` or `--built BUILD` for each `HOENN_VERSION` (data in bounds, tiles fit, contacts, rematch rows). `HOENN_VERSION=x python3
b2tools/pokenav_art.py DIR` writes a preview PNG of every view.
