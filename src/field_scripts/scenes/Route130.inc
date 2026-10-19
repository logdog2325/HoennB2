// Route 130's story: Mirage Island (Sapphire data/maps/Route130/scripts.inc Route130_MapScript1_1523C8; postgame_maps,
// 2026-10-07). converter/gen_map_content.py includes this file twice in the generated zone file 0480_auto_Route130.s: the
// entries below become scripts 1-2. Map scripts: scenes/Route130_init.inc.
//
// Sapphire (src/time_events.c, src/clock.c): VAR_MIRAGE_RND_H/L hold a 32-bit value that the clock advances once per day
// (UpdateMirageRnd: rnd = 1103515245 * rnd + 12345 per day passed); on every entry into Route 130 (OnTransition)
// IsMirageIslandPresent compares its upper 16 bits with the lower 16 bits of the personality of each Pokémon in the party
// (eggs too: species != 0) and swaps in layout 46 (LAYOUT_UNREFERENCED_MAP, the island) on a match, else layout 264.
// Here:
// - the day's value: Black 2 resets flags 2720-2819 at midnight; the first entry of a day (FLAG_DAILY_MIRAGE_RND clear)
//   draws a new 16-bit value (two Random 256). Sapphire's sequence needs its day counter (VAR_DAYS, from its RTC), which
//   Black 2's scripts can't read. ODDS (user decision 2026-10-07): only the low 7 bits of the value and of each
//   personality are compared (MI_MASK 0x7F): 1 in 128 per party Pokémon a day, about 1 in 22 days with six (Sapphire's
//   16 bits: 1 in 65,536 per Pokémon, practically never).
// - the personalities: PokePartyGetParam field 0 (the personality, returned as its lower 16 bits = Sapphire's
//   `& 0xFFFF`); Black 2's script whitelist lacks it, b2tools/patches/story.py swaps it in for field 0xa5 (Sp. Atk, read
//   by no script).
// - the layout: Black 2 map replacement event 2 (work 0x4033 == 0x206; data/hoenn_world.json alt_layouts Route130 =
//   the island's two cells, b2tools/world.py build_alts). A swapped matrix shows only when the field is built, and Route
//   130 is entered by surfing across a cell edge (no warp leads in), with the island's cells often already drawn: when
//   the zone init finds the island in the wrong state it sets VAR_MIRAGE_REDRAW (1 show, 2 hide), and the map-script
//   condition runs Story_MI_Redraw once the field is up: fade out, swap the event, rebuild the field in place (Black 2's
//   FieldClose/FieldOpen, as its scripts do around a demo), fade in. On most days nothing changes and nothing shows.
// - the Liechi Berry (Sapphire's berry tree 82, hidden with FLAG_TEMP_11 while the island is away): the daily berry spot
//   tree_82 (data/hoenn_berry_spots.json, a sign at (52,9)); b2tools/patches/story.py gives it the island's height, so
//   it can't be read from the sea when the island is away.
// - Wynaut: Route 130's wild table (encounter file of zone 240) has Sapphire's land slots; the island's tall grass has
//   encounter flags, the open sea none.
// Test switch (build with HOENN_TEST_CHPM_MIRAGE=1: scripts.py passes every HOENN_TEST_CH* variable): the day's value =
// the personality of the party's first Pokémon (the island is there); =2 also shows it at once on a warp straight into
// Route 130 (HOENN_TEST_WARP); =3: the day's value is party[0]'s personality + 1 (no match with a party of one).
#ifdef SCENE_ENTRIES
    ScriptEntry Story_MI_Init       // 1: Route130_MapScript1_1523C8 (zone init: IsMirageIslandPresent)
    ScriptEntry Story_MI_Redraw     // 2: the island's layout swapped in the field (map-script condition)
#else
#define MI_EVENT 2                  /* map replace event 2 (work 0x4033 == 0x206): the island's cells */
#define MI_A 0x8050                 /* scratch works of the zone init */
#define MI_B 0x8051
#define MI_N 0x8052
#define MI_I 0x8053
#define MI_P 0x8054
#define MI_R 0x8055
#define MI_MASK 0x7F                /* bits compared (user 2026-10-07): 1 in 128 per party Pokémon a day, a full party
                                       of six 1-(127/128)^6 = 4.6 % = about 1 in 22 days (0x3F: 9.0 %, 1 in 11) */

Story_MI_Init:
    RTCallGlobal 8297                       // the berry trees' new-day reset (converter/gen_hidden_items.py; missing_objects)
    h_goto_if_set FLAG_DAILY_MIRAGE_RND, L_MI_Rolled     // UpdateMirageRnd: a new value once a day
    FlagSet FLAG_DAILY_MIRAGE_RND
    Random MI_A, 256
    Random MI_B, 256
    WorkMul MI_A, 256
    WorkAdd MI_A, MI_B
    WorkSet VAR_MIRAGE_RND_H, MI_A
L_MI_Rolled:
#if defined(HOENN_TEST_CHPM_MIRAGE) && HOENN_TEST_CHPM_MIRAGE == 3
    PokePartyGetParam VAR_MIRAGE_RND_H, 0, 0             // TEST ONLY: the first Pokémon's personality + 1: its low bits
    WorkAdd VAR_MIRAGE_RND_H, 1                          // differ (a party of one doesn't match)
#elif defined(HOENN_TEST_CHPM_MIRAGE)
    PokePartyGetParam VAR_MIRAGE_RND_H, 0, 0             // TEST ONLY: the first Pokémon's personality matches
#endif
    PokePartyGetCount MI_N, 0                            // IsMirageIslandPresent: every Pokémon of the party (eggs too)
    WorkSetConst MI_I, 0
    WorkSetConst MI_P, 0
    WorkSet MI_R, VAR_MIRAGE_RND_H                       // (user 2026-10-07: ~1 in 20 days) only the low 7 bits are
    WorkAnd MI_R, MI_MASK                                // compared: Sapphire's 16 bits (1 in 65,536 per Pokémon)
L_MI_Loop:
    WorkCmpWork MI_I, MI_N
    VMJumpIf CMP_GE, L_MI_Checked
    PokePartyGetParam MI_A, MI_I, 0                      // personality & 0xFFFF
    WorkAnd MI_A, MI_MASK
    WorkCmpWork MI_A, MI_R
    VMJumpIf CMP_EQ, L_MI_Present
    WorkAdd MI_I, 1
    VMJump L_MI_Loop
L_MI_Present:
    WorkSetConst MI_P, 1
L_MI_Checked:
    // (missing_objects 2026-10-08) the Liechi Berry tree (daily berry spot 73, data/story/berry_spots.json) stands on the
    // island: hidden while the island is away, shown again when it is here unless picked today (VAR_BERRY_PICKED_5 bit 2)
    h_setflag FLAG_BERRY_TREE_PICKED_73
    h_goto_if_eq MI_P, 0, L_MI_TreeDone
#ifdef HOENN_BERRY_PLANTING
    h_clearflag FLAG_BERRY_TREE_PICKED_73       // (berry planting: tree 82 shows its own stage, picked or not)
    VMJump L_MI_TreeDone
#endif
    WorkSet MI_A, VAR_BERRY_PICKED_5
    WorkAnd MI_A, 4
    h_goto_if_ne MI_A, 0, L_MI_TreeDone
    h_clearflag FLAG_BERRY_TREE_PICKED_73
L_MI_TreeDone:
    MapReplaceIsEventSet MI_EVENT, MI_B
    WorkSetConst VAR_MIRAGE_REDRAW, 0
    WorkCmpWork MI_B, MI_P
    VMJumpIf CMP_EQ, L_MI_Done                           // already as it should be (setmaplayoutindex 46 / 264)
    WorkSetConst VAR_MIRAGE_REDRAW, 2
    h_goto_if_eq MI_P, 0, L_MI_Done
    WorkSetConst VAR_MIRAGE_REDRAW, 1
#ifdef HOENN_TEST_CHPM_MIRAGE
#if HOENN_TEST_CHPM_MIRAGE == 2
    MapReplaceSetEvent MI_EVENT, 1, 1                    // TEST ONLY (=2): a warp into Route 130 (the field not built yet)
    WorkSetConst VAR_MIRAGE_REDRAW, 0                    // shows the island at once
#endif
#endif
L_MI_Done:
    VMHalt

Story_MI_Redraw:                    // VAR_MIRAGE_REDRAW 1 (show the island) / 2 (hide it), set by the zone init
    h_lock
    FadeOutBlackQ
    FadeWait
    h_goto_if_eq VAR_MIRAGE_REDRAW, 2, L_MI_Hide
    MapReplaceSetEvent MI_EVENT, 1, 1
    VMJump L_MI_Swapped
L_MI_Hide:
    MapReplaceSetEvent MI_EVENT, 0, 1
L_MI_Swapped:
    WorkSetConst VAR_MIRAGE_REDRAW, 0
    FieldClose
    FieldOpen
    FadeInBlackQ
    FadeWait
    h_release
#endif
