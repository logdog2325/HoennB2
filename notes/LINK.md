# Link play: trades and battles between Sapphire, Ruby and Emerald NDS (link, 2026-10-18)

Goal (user, 2026-10-18; RESUME "Trading and battles between versions"): friend-to-friend trades and battles between
the three versions, over local wireless and with Wiimmfi friends, so players can complete the Hoenn Pokédex. Not the
GTS. Nothing here was tested online (rule: never connect to Wiimmfi or any online service); the Wi-Fi part is read from
the code. Local wireless: the user's melonDS test (two windows, "Test" below).

## 1. What players get

- **Every Pokémon Center 2F** (Sapphire's Cable Club desks), once the player has the Pokédex (Sapphire's own gate,
  `FLAG_SYS_POKEDEX_GET`; before it the desks keep Sapphire's "undergoing adjustments" apology):
  - **left desk (Colosseum attendant): Black 2's Union Room** (local wireless: trade, single/double/triple/rotation
    battles, multi battles for four, Black 2's own words: "Welcome to the Pokémon Wireless Club Union Room ...");
  - **middle desk (Trade Center attendant): Black 2's Wi-Fi Club** (Nintendo WFC = Wiimmfi today: trades and battles
    with friends registered in the **Pal Pad**, which is in the Key Items from the start of the game);
  - right desk (Record Corner): Sapphire's apology (record mixing has no Black 2 counterpart).
- **One rule set per link battle:** the battle uses the Fairy / physical-special split answers of the machine that
  runs the battle (the "server", picked by Black 2), on both DSes. Seasons, music and sprite style don't affect battles.
- **Only HoennB2 builds of this link version meet:** an unmodified Black 2 / White 2, or a HoennB2 release from before
  link, never shows up in our Union Room or Wi-Fi Club, and never sees ours.
- After a trade the Pokémon is registered in the Hoenn Pokédex (Black 2 registers every received Pokémon by national
  number), keeps its met location (named right in every version, see 3), and evolves if it is a trade evolution (3).

## 2. Findings

### 2.1 Where Black 2 links, and what a player of our builds could reach before

| Black 2 | How it starts | In our builds before link |
|---|---|---|
| Union Room (local wireless) | global script 2101 (data/field_scripts/1231.s Script_2), talked to at the Center's left counter; `MapChangeUnionRoom` -> zone 422 (`ZONE_UNION_ROOM`) | not reachable: no counter runs 2101. Zone 422, its map (matrix 88, chunk 871), scripts 844/845, text 663, entities 609 and building pack 42 are byte-identical to Black 2 in Sapphire v17.0.1 and Emerald v1.0.4 (allocate_zones keeps 422 out) |
| Wi-Fi Club (friends over Nintendo WFC) | global script 10100 (1245.s), the Center's Wi-Fi counter; `NetConnectWiFiClub` | not reachable |
| Global Terminal (GTS, Random Matchup, Battle Videos) | global 10105 (1246.s) | not reachable (and stays so: the user doesn't want the GTS) |
| C-Gear (wireless/IR/Wi-Fi bottom screen) | `CGearPowerOn` after Bianca gives it (0854.s, flag 106) | never turned on. It can't simply be turned on: area2_buildings' save fix gives HEAPID_USER's free space (the C-Gear's comm memory) to the outdoor field heap (notes/TESTING.md "Saving and the field heap") |
| Pokémon Center 2F | (Gen 3 Cable Club) | 15 Hoenn 2F rooms, attendants apologise (centers_rooms.py) |

Black 2's counters also run Black 2's Center lift: global 2105 (L_09CD) walks the player onto building-model props
of types 5/6 three tiles north of the player (`BMCreateHandleByGPos`) and sinks them; 2106/2107 (L_0ADA) raise them
on the way back and end with plugin-13 commands (Black 2's Center zones only). Hoenn's Centers have neither: that is
why the centers agent left the desks apologising.

How the way back works (src/ov035/event_mapchange.c): the counter saves the spot (`FieldSetNextZoneHere`, flag 2405
`EVENT_FLAG_CONTINUE_SCRIPT`, work 0x4041); leaving the Union Room (`EventMapChangeUnionRoomExit`) warps there and
runs global 2106 (0x83a); Continue on a save made in the Union Room (`EventFieldContinue`) loads that spot and runs
2107 (0x83b); the Wi-Fi Club calls 2105 before and 2106 after itself.

### 2.2 Version checks and the handshake

- All three versions keep Black 2's header (`POKEMON B2`, game code IREO, US): build_rom.py takes header and DSi parts
  from the decomp (checked on the release ROMs; only the header CRC differs, which is antipiracy.py's business, not
  the link's). The antipiracy patch only redirects the "tampered" callbacks; nothing in the link code reads it.
- Nothing in the Union Room or the Wi-Fi Club compares versions or languages (the Union Room beacon carries the ROM
  version 0x17 and language 2 at +8/+9, func_ov028_021709e0; the Wi-Fi status data +0x15/+0x16; PlayerInfo +0x1a/+0x1b;
  none of them is checked). So **without link.py, our builds connect to any Black 2 / White 2** (and to old HoennB2
  releases), and nothing would stop our Fairy moves and items from reaching them.
- Local wireless filters on the GGID: GFLNetInitData +0x50 (0x1380 in Black 2's tables); ov030 puts it in each
  beacon's GFL header and drops beacons whose id differs (func_ov030_021733dc, after a CRC16). Wi-Fi does not use it.
- The Wi-Fi Club (ov173; ov190 login; ov011 DWC + Game Freak's wrapper: gamename "syachi2ds", product id 0x2fc6)
  lists a Pal Pad friend only when the friend's 32-byte GameSpy status says "in the club" (+0x18 = 1-5,
  func_ov173_021a2124), and the host drops a client whose game type (+0x17) differs from its own
  (func_ov173_021a2800). GFL's negotiation after connecting compares only gameCommandBase/unk6E; a rejected
  negotiation makes ov173 poll forever (a soft lock), so it is not used as a gate.

### 2.3 After a trade

(Trade research, see 2.6.) Black 2's trade app registers the received Pokémon in the Pokédex by national number (the
Hoenn Pokédex is the same save flags with Hoenn's numbering, hoenn_dex.py), keeps the original trainer's met location
and date, and runs the trade-evolution check (`CheckEvolveSpecies` mode 1).

- **Trade evolutions:** trade_evos.py had replaced every trade method (`EVO_METHOD_TRADE` 5, `TRADE_WITH_ITEM` 6,
  `TRADE_WITH_SPECIES` 7) by level / item / species-in-party methods; mode 1 only looks at methods 5-7, so a real trade
  evolved nothing and broke nothing. link keeps Black 2's own trade entries after the new ones (data/trade_evos.json
  `keep_trade_methods`): a link trade now evolves Kadabra, Machoke, Graveler, Haunter, Boldore, Gurdurr, Onix/Scyther
  with a Metal Coat, Seadra with a Dragon Scale, Poliwhirl/Slowpoke with a King's Rock, Porygon(2), Rhydon,
  Electabuzz, Magmar, Dusclops with their items, Feebas with a Prism Scale, Clamperl with a Deep Sea Tooth/Scale and
  Karrablast for Shelmet, as in Black 2; levels and Bag items still work as before (the other modes never read 5-7).
- **Met location:** a Pokémon's met location is a line of the place-name file (system 0109); the receiving game names
  it from its own file. Sapphire and Ruby used to show Unova leftovers on the six lines Emerald gave its new places
  (91 Magma Hideout, 106 Marine Cave, 107 Mirage Tower, 110 Artisan Cave, 111 Desert Underpass, 112 Terra Cave): now
  every version has them (src/text/overrides_link.json; no Sapphire/Ruby zone shows those lines, checked on v17.0.1).
  Left as it is, as in Gen 3: line 69 is "Aqua Hideout" in Sapphire/Emerald and "Magma Hideout" in Ruby (the same map
  section), so a Pokémon met in Ruby's hideout says "Aqua Hideout" in the other two. Emerald's Magma Hideout is 91.

### 2.4 Link battles

- Black 2 runs the battle on every machine: the server machine has the server; each client keeps its own server copy
  (BtlMainModule unk0C) and they must compute the same results. Our builds read two battle options from the save,
  options u16 bit 11 (Fairy: Gen 6 chart, retyped species, Fairy moves' type) and bit 12 (classic split); with
  different answers the two DSes would disagree (Fairy type chart, Moonblast's type, physical/special) = desync.
  Bits 13 (music), 14 (sprites), 15 (seasons) don't touch battles. No other option or version difference reaches a
  link battle: Sapphire v17.0.1 and Emerald v1.0.4's ov167 differ only by fairy.c's ITCM addresses and Emerald's
  Palace/Arena hooks, which act only while a Palace/Arena battle's rule is set (frontier_palace_arena.c `ST->rule`,
  reset to none after each such battle); level scaling is trainer/wild data.
- Before the parties, every link battle style (single, double, triple, rotation, multi; Union Room and Wi-Fi Club)
  goes through func_ov167_0219ada0: the server sends one 32-byte BtlMainSyncData (random state, ...) to all machines
  and each copies it (func_ov167_021b9bb8 send / func_ov167_021b9c0c receive). Its byte 0x1f has 4 spare bits
  (unk1F_4): written by nobody, read by nobody, and 0 (the main module is zeroed).
- Known limit: a recorded link battle (Black 2's Vs. Recorder battle videos; Hoenn never gives the Vs. Recorder) is
  replayed as a local battle without the sync, so it would replay with the viewer's own options.

### 2.5 Things only our builds have

The Fairy moves 560-565 (Black 2's move table has 0-559), the Pixie Plate / Fairy Gem (items 113/114, "???" in Black 2)
and TM96-TM104 (items 120-128, "???" in Black 2). With link.py no unmodified game can meet ours, so none of them can
reach one (see 2.6 for what an unmodified game would have done).

### 2.6 Trade research (read from the code; the trade app is ov194, base 0x021b76e0)

- The same app serves infrared, the Union Room and the Wi-Fi Club (work+0x118c: 0 IR, 1 Union Room, 2 Wi-Fi Club,
  3 GTS Negotiation). After the swap the receiving game: puts the Pokémon in the slot the sent one left; restores HP/PP
  (`PokeParty_Recover`); sets friendship 70 (an Egg: met location 30003 "Link Trade" and today's date); otherwise keeps
  everything (original trainer, met location, date, level, Ball); registers it caught (and seen) by national number
  (`addPkmToDex` arm9 0x0200d568, at ov194 0x021bf5d4: the Hoenn Pokédex works); adds the trade record; then runs the
  trade evolution (`CheckEvolveSpecies(NULL, received, 1, sent, season, ...)` at 0x021bf8ce: method 5 plain trade, 6
  holding the item, 7 Karrablast/Shelmet; an Everstone blocks it except for Kadabra, as in Black 2); the evolution
  scene removes a TRADE_WITH_ITEM item and registers the new species; then a save synchronised with the partner
  (backups restored if it fails).
- Checks before a trade: only "last Pokémon able to battle", Bad Eggs / species above 686, Mail, and five Unova
  legendaries' alternate forms (BW1 compatibility). No check of move ids, items, abilities or the partner's version.
- An unmodified Black 2 receiving a Pokémon with a Fairy move would accept it, show a blank move name, then stop with
  "An error has occurred" while committing the trade (`PokeParty_Recover` -> `PML_MoveGetMaxPP` -> the move archive's
  file 560 does not exist -> GFL's assert). Its save would be untouched; ours would restore its backup. A link battle
  would hit the same assert. Items 113/114 show "???" and do nothing there; items 120-128 can't be held. link.py's
  isolation keeps all of this from happening: such a game never finds ours.
- A second layer was considered and left out (one is enough, and it needs a marker in the partner's PlayerInfo, whose
  spare bytes +0x1e/+0x1f were not swept): refuse at the "Trade?" confirm (`func_ov194_021b8330`'s check, result code 7:
  Black 2's own "There is a Pokémon that cannot be traded in your party." on our side, the matching message on theirs)
  when the partner lacks the marker and the Pokémon knows a move >= 560 or holds item 113/114/120-128.

## 3. Design (what link changes)

1. **The desks** (b2tools/centers_rooms.py `LINK_COUNTER`, the 15 regenerated `*_PokemonCenter_2F.s`): after the
   Pokédex, the Colosseum attendant sets flag 106 (Black 2's "Center link counters open", read only by the counters
   1231/1245/1246; not a Hoenn id) and calls global 2101; the Trade Center attendant does the same with global 10100.
   Black 2's own scripts and words do the rest (menu, Trainer Card title, the save before connecting, the comm checks).
2. **The lift** (src/field_scripts/1231_global_2100.s: Black 2's 1231.s with four calls changed): 2101 and 2105 fade
   out where the player stands (setting 0x4041 = 1 as Black 2 does); 2106/2107 fade in (2107: Black 2's season card,
   as on any Continue) and clear 2405/0x4041. The Random Matchup penalty / BP award (plugin 13) is left out: no
   Global Terminal in Hoenn.
3. **Battle rules** (fairy.c "Link battles", fairy.py CALLS): the server writes `8 | Fairy | classic << 1` into the
   spare nibble before sending the sync (Link_SyncSend); every machine, server included, takes the received nibble as
   the battle's rules (Link_SyncRecv); config() answers them instead of the save's bits 11-12 until the battle proc
   ends; every battle proc start and end clears them (Link_BattleInit/Exit, wrapped around its first and last calls).
   No marker (an unmodified server) means Black 2's rules. Chosen over "refuse when the options differ" (a refusal
   mid-setup is a comm error with no explanation) and over "fixed rules for link battles" (ignores both players'
   choice): when both picked the same, they get it; when they differ, both get the server's.
4. **Only us** (b2tools/patches/link.py): the Union Room's GGID 0x1380 -> 0x4842 (ov028 0x02172ce4); the Wi-Fi Club's
   two status bytes moved to bytes Black 2 never uses (ov173 accessors 0x021a61c0-0x021a61cc: +0x18 -> +0x1d,
   +0x17 -> +0x1e). Effect: unmodified games and pre-link HoennB2 releases are invisible both ways (not listed / no
   beacon), with no new message and no soft lock. The id is the link protocol's version: a later change that breaks
   compatibility takes 0x4843 (and the status bytes move again, e.g. to +0x1f).
5. **Met locations** (src/text/overrides_link.json): Emerald's six place lines in every version.
6. **Trade evolutions** (data/trade_evos.json `keep_trade_methods`, trade_evos.py): Black 2's trade entries kept.

## 4. Files

Main tree (not committed): b2tools/centers_rooms.py, src/field_scripts/{0024,0064,0112,0132,0138,0212,0288,0312,0426,
0548,0668,0770,0900,0988,1180}_room_*_PokemonCenter_2F.s (regenerated; Dewford 1F's hand-made rescue lines were NOT
regenerated: centers_rooms.py doesn't know them), src/field_scripts/1231_global_2100.s (new),
b2tools/patches/fairy.c, fairy.py, b2tools/patches/link.py (new), src/text/overrides_link.json (new),
b2tools/patches/trade_evos.py, data/trade_evos.json, b2tools/story_build.sh and rebuild_slice.sh (`link` after
escape_rope; a shared line), notes/LINK.md.
Sapphire/Ruby: b2tools/release_kit/next/link.patch (made on sapphire-ruby 2e2ae86; `git apply --check` passes on
8871205, whose two new commits, ground cracks and dark doorways, touch none of these files).

## 5. Test (melonDS, two windows on one Mac)

ROMs (test kit in Littleroot's town sign; nothing else differs from the release lists + link):
- `~/Desktop/Sapphire_LINK_TEST.nds`: sapphire-ruby 2e2ae86 + link.patch; sign gives Groudon Lv100, Gardevoir Lv50
  (first move Moonblast), Kadabra Lv30, Lotad Lv12, the Pokédex (Black 2's and Sapphire's flags), the X menu's POKéMON.
- `~/Desktop/Emerald_LINK_TEST.nds`: main b1ef517 + link (without the other helpers' unfinished edits); sign gives
  Groudon Lv100, Salamence Lv50, Machoke Lv30, Seedot Lv12, the same flags.
Littleroot's town sign (by the path south-east of the player's house: stand below it, face up, A) warps into
**Oldale's Pokémon Center 2F**: Sapphire right in front of the left desk (press Up); Emerald, whose 2F has Emerald's
own layout (desks at x 3 / 7 / 11, emerald_rooms), two steps right of it (walk 2 left, press Up). The steps are also
item 18 of ~/Desktop/HoennB2_TESTS.txt.

Steps:
1. melonDS: open Sapphire_LINK_TEST.nds. System -> Multiplayer -> Launch new instance; in the new window open
   Emerald_LINK_TEST.nds. (Local wireless between instances needs no other setting; each ROM keeps its own save.)
2. New game in both. Answer Birch differently on purpose: Sapphire Fairy YES + modern split YES, Emerald Fairy NO +
   classic split (NO). Walk out of the house, read the town sign in both.
3. Both: face the left attendant, A: "Enter the Union Room" -> (title) -> DS Wireless Communications YES -> save YES.
   Expected: the Union Room; after a few seconds each player sees the other's avatar.
4. Trade (talk to the other avatar -> Trade): Sapphire's Kadabra for Emerald's Machoke. Expected: both evolve right
   after the trade (Alakazam, Machamp); the game saves. Then Lotad for Seedot.
   Check afterwards (X menu): Pokédex (Hoenn) shows Seedot / Lotad and Alakazam / Machamp caught; their summary shows
   the other game's trainer and "Littleroot Town" as the met place.
5. Battle (talk -> Battle, single): Sapphire sends Gardevoir, Emerald Salamence; Gardevoir uses Moonblast.
   Expected: both screens show the same message and HP: "It's super effective!" when the Sapphire DS runs the battle
   (its Fairy rules), a neutral hit when the Emerald DS does (no Fairy); never "communication error" / different HP.
   Do a second battle started from the other side. (Who runs it is Black 2's choice: the parent of the connection.)
6. Leave: step back on the green ring where you arrived -> back at Oldale's 2F desk, screen fades in, you can walk.
7. Continue: after a trade in the Union Room (it saved), close the window (or System -> Reset) without leaving -> Continue
   -> you are at the 2F desk (Black 2's season card, then the room). 
8. Wi-Fi Club (middle desk): only check that it talks ("Welcome to the Pokémon Wi-Fi Club!" ... "no friends in your Pal
   Pad"); answer NO to "launch Nintendo WFC". The real Wi-Fi test is for players with friend codes (README).
9. Optional: an unmodified Black 2 in the second window, in its own Union Room: neither player sees the other.

Already checked here (DeSmuME, muted, both test ROMs, single machine: no partner): sign -> 2F; left desk: Black 2's
Union Room dialogue, title, save, "I hope you enjoy..." -> Union Room ("I've entered the Union Room."); stepping on the
ring -> back at the desk, fade in, walking and talking work; middle desk: Wi-Fi Club dialogue up to "launch Nintendo
WFC?" (answered NO, nothing connected; DeSmuME's Wi-Fi emulation is off anyway); wild battles on Route 101 (run;
Earth Power: KO, "not very effective" on Wurmple) -> back to the field (the new battle start/end hooks). The evolution
table of the ROM has Black 2's trade entries next to the level/item ones (Kadabra: Lv 36 + trade; Onix: Metal Coat
from the Bag + trade holding it). Emerald the same (Union Room in and out from Emerald's 2F, the Wi-Fi Club desk, a
wild Poochyena on Route 101 fought and won). Not checkable alone: two DSes meeting, trades, link battles, Continue
after a save in the Union Room.

## 6. README draft (for players)

### Trading and battling with friends (Pokémon Sapphire, Ruby and Emerald NDS)

Every Pokémon Center has the Cable Club upstairs. Once you have your Pokédex:
- **Left desk - Union Room (local wireless):** trade and battle with players near you (or in another emulator window).
- **Middle desk - Wi-Fi Club (online):** trade and battle with friends registered in your **Pal Pad** (Key Items).
  Online play needs a Wiimmfi-patched ROM, as for Black 2; add each other's Friend Code in the Pal Pad first (the
  desk can show you yours).

Sapphire, Ruby and Emerald NDS all meet each other, so you can complete the Hoenn Pokédex by trading. Notes:
- Everyone needs **the update with link play or later** (version names: the user's call). Older versions and the
  original Black 2 / White 2 don't show up: they can't read the Fairy moves and new items safely.
- **Trade evolutions work** both ways: trade them (Kadabra, Machoke, Onix holding a Metal Coat ...) or use the in-game
  ways (levels, items from the Bag).
- **Link battles use one set of rules:** the Fairy type and the physical/special split as chosen by the player whose
  game hosts the battle. Pick the same answers if you always want your own.
- A traded Pokémon keeps where it was met; every version names Emerald's new places.
- Emulators: melonDS supports local wireless between two windows (System -> Multiplayer -> Launch new instance).

## 7. Open questions for the user

- Which desk should be which: left = Union Room, middle = Wi-Fi Club now (both offer trades and battles; the Record
  Corner desk still apologises). OK, or a menu at one desk?
- Battle rules: the host's options (done). Alternatives: always Gen 6 rules in link battles, or refuse when they differ.
- Ruby's hideout is place line 69 like Sapphire's Aqua Hideout (Gen 3 did the same); moving Ruby's Magma Hideout to
  Emerald's line 91 would name it right everywhere but changes Ruby's zone data (and old Ruby catches keep 69).
- Version names for the release: link play is a compatibility break (older releases can't meet the new ones).
- Wiimmfi: never tested here. The Wi-Fi Club isolation (status bytes) is read from the code only; a test with two
  real players is needed before saying "online works" in the README.
