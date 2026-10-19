# Decisions made while the user was away (2026-10-18 evening)

The user: "make decisions if you have to but when I'm back tell me what you decided and I'll let you know if I want
anything changed". Each entry: what was decided, why, and how to change it.

1. **Version names:** Sapphire/Ruby NDS v18.0 + Emerald NDS v1.1. All three ship together (link play doesn't meet older
   versions). (The user left it to the lead before dinner.)
2. **Location evolutions** (special zones): the Ruby/Sapphire remakes' places.
   - Magnezone/Probopass in New Mauville.
   - Leafeon in Petalburg Woods.
   - Glaceon in Shoal Cave's ice room.
   - Change: b2tools/patches/special_zones.py EVO_PLACES (one line each), or turn them off.
3. **"You defeated..."** after trainer battles in all three versions (was "Player defeated..."). Change:
   src/text/overrides_battle_you.json.
4. **Ruby's Magma Hideout** shows "Magma Hideout" in every version after a trade (Emerald's place line 91). Gen 3 Ruby
   shared Sapphire's "Aqua Hideout" line. Change: b2tools/ship_hideouts_rooms.py PLACE['magma'] = 69.
5. **Emerald rematches (user-tested):**
   - route trainers' tier follows the badge count (5 badges -> tier 2 ... 8 -> tier 5);
   - available once a day;
   - offered right after a first battle when you have 5+ badges.
   Emerald itself steps up one tier per rematch won and calls you at random (Match Call). Change: notes/EMERALD_REMATCH.md.
6. **Wally's first Victory Road battle:** Sapphire/Ruby keep it where pokeruby has it; Emerald gets pokeemerald's spot
   near the entrance (the user's faithful-remake rule; helper running).
7. **Tree vs cliff flicker:** trees standing < 2 units in front of a cliff face are moved forward until they are 2 units clear (helper
   running).
8. **Battle Tents** follow pokeemerald (src/battle_tent.c): Verdanturf Palace rules, Fallarbor Arena rules, Slateport
   Factory rentals at Lv 30. 3 battles per challenge; prizes Nest Ball / Hyper Potion / Full Heal.
   **Trainer Hill:** the four base modes, opens after the Hall of Fame. The e-Reader/Japanese-only floor sets are left
   out (Japanese e-Card data only). The timer shows whole seconds (Black 2's play time), and the time board is a message.
9. **Shop archive** a/2/8/2 grows 40 B for the Trainer Hill Mart (Emerald's item order kept). Only old savestates are
   affected.
10. **Pearl <-> Hoenn trading** (the Pearl session asked; the user told Pearl to "follow what the Hoenn project did"):
   - Hoenn keeps place-name lines 4-89, 91, 106, 107, 109-112.
   - Pearl moves Sinnoh's names after line 153, if the summary screen accepts ids that high (Pearl tests it).
   - Each game then carries the other's names.
   - TM item ids stay apart: Hoenn 120-128, Pearl 115/129-133/426/427/622. Fairy items 113/114 are shared.
   - Same link id 0x4842.
   - To do in HoennB2 later: append Pearl's Sinnoh place lines to 0109 when Pearl sends the list.
11. **Berry planting** (all 3 versions, behind HOENN_BERRY_PLANTING=1 until self-tested; then on by default):
   - all 88 Gen 3 trees per version, pokeemerald berry.c growth/watering/yield/regrowth;
   - stored in Black 2's Pokéstar Studios save block (unreachable in Hoenn; checksums and PKHeX unaffected);
   - old saves start with today's 80 grown trees (= Gen 3's new-game set);
   - DS clock in real minutes; moving the clock back freezes growth (Gen 3's rule).
   Soft soil keeps Black 2's soil tile look for now; Gen 3's soil look can be a later polish.
   Left out: sway/sparkle/watering animations, using the Pail or a berry from the Bag on a tree (you talk to the tree),
   live growth while you stand there.
12. **Mirage Tower (Emerald):** walking in from Route 112 or from the desert keeps the tower as it is already drawn,
    instead of Emerald's 50% roll. The roll still happens on entries where the tower isn't on screen yet (from Route 113,
    Mauville, or through doors). Emerald's small screen never shows the tower from the Route 112 seam, so you can't see
    the difference.
13. **Berry planting:** ON by default after its self-test passed (your rule). HOENN_BERRY_PLANTING=0 builds the old daily
    trees.
14. **Surf-under plank bridges** (Routes 119/120, all versions):
   - the decks are raised at least 32 units over the water, with 16-unit steps from the banks;
   - Route 120 south's river is one body of water again, as in Gen 3;
   - the surfer shows in the gap under the deck from the south camera, as with any raised 3D bridge, and is never drawn
     through the planks.
   Walk-under (not surf-under) bridges are unchanged.
15. **Chunk size vs the cracks fix:** Black 2 copies each map chunk into a fixed 110,600-byte buffer with no size check.
   The cracks fix had pushed a few chunks over it (Sapphire: 3, including Sootopolis; Emerald: about 5), which would hang
   there. Every chunk is now measured, and an oversized one gets the cracks fix back (first the edge splits, then the
   under-floor) in that chunk only. The purple lines may still show in those few chunks. Lines there are the price of
   no hang.
16. **Tree flicker:** tree cards are moved 2 units clear of cliff faces; the palm tops of Black 2's Humilau palms are
   raised by 0.9-1.4 units.
17. **Sinnoh met locations** (from the Pearl session): all three Hoenn versions show Pearl NDS's Sinnoh place names
   for Pokémon traded from Pearl, on lines 154-264. Black 2 showed "Faraway place" for every location above 153; a
   4-byte fix that Pearl tested in game makes locations up to 511 show their own name. Unknown ones still read
   "Faraway place".
