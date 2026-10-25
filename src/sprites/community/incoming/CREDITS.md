# Community sprites (given by the user, 2026-10-11; free to use with credit)

| File | What | Author (credit) |
|---|---|---|
| brendan_sheet_hyo-oppa.png | Brendan: overworld (walk/run/bike/surf/fish...), front, 5-frame back throw | hyo-oppa |
| brendan_front_hyo-oppa.gif | Brendan battle front | hyo-oppa |
| may_oras_sheet_Luckygirl88.png | May (ORAS outfit): overworld, front, back throw | Luckygirl88 ("Please credit me if used or edited") |
| maxie_sheet_joojishibuki.png | Maxie: front + overworld | joojishibuki |
| archie_sheet_PurpleZaffre.png | Archie: overworld (4 directions x 4 frames) | PurpleZaffre |
| aqua_magma_grunts_Kimmylube_AzureAquarian.jpg | Team Aqua/Magma grunt overworlds (male/female) | Kimmylube; the user says the Aqua/Magma sprites are by AzureAquarian: credit both |
| may_oras_DiegoWT/ (7 sheets: walk, run, bike, bike idle, surf, fish, use HM) | May (ORAS) overworld | DiegoWT (spriter), Zailens (commissioned): "Please, give the proper credits if using" (deviantart.com/diegowt, Sprite Pack - ORAS May) |
| archie_oras_DiegoWT.png | Archie overworld (4x4) | DiegoWT (spriter), Kyledove (commissioned): "Please, give the proper credits" (deviantart.com/diegowt, GEN 6 ORAS - Team Aqua Leader Archie) |
| trainer_collection_hyo-oppa.png (user, 2026-10-12) | DS-style Gen III trainer battle fronts (15 figures, 1x); used: Wally's front only (top row, third figure) | hyo-oppa: "give credit if used" on the sheet; the DeviantArt page (deviantart.com/hyo-oppa/art/DS-Style-Gen-III-Pokemon-Trainer-Battle-Sprites-878566572) allows use in ROM hacks with credit and edits with credit (no "do not edit"). Wally has 19 colours: 3 pairs merged for the DS's 15 (b2tools/sprite_community.py FRONT_MERGES; screenshots/wally_sprite/wally_front_merges.png) |
| wally_sheet_CalculusNova.png (user, 2026-10-12; NO LONGER USED since 2026-10-17) | Wally overworld: walk, run, watering, bike, each with and without a backpack (Gen 3-sized 16x32 cells); used: the walking frames without the backpack, unchanged | CalculusNova, CC BY-NC-SA 3.0 (deviantart.com/calculusnova/art/Wally-Multiple-Sprites-167000415) |
| birch_sheet_Wolfang62.png (user, 2026-10-12) | Professor Birch overworld (walking, 4 directions x 4 frames; Pokémon Essentials sheet at 2x); used as Birch's NEW overworld (every Birch object) | Wolfang62 (DeviantArt, published 2021-07-16): free to use with credit, edits allowed (the user checked). 16 colours: one pair merged for the DS's 15, a 6-pixel brown into the hair's (b2tools/sprite_community.py EXTRA_MERGES[104]; screenshots/birch_sprite/birch_overworld_review.png). Credit line: "Wolfang62: Professor Birch (overworld)" |
| wally_sheet_Kymotonian_KleinStudio.png (user, 2026-10-17) | Wally overworld (Pokémon Essentials walking sheet at 2x, 4 directions x 4 frames); used as Wally's NEW overworld (code 87), replacing CalculusNova's | Kymotonian and Klein Studio: credit both; edits allowed (the user checked). 23 colours: the 8 closest pairs merged for the DS's 15 (b2tools/sprite_community.py EXTRA_MERGES[87]; review work/agents/wally_new/wally_merge_review.png) |

The grunt sheet exists only as a JPEG (the user checked): the user approved converting it ("we may have to convert").
Snap each pixel to the sheet's real colours (never redraw) and show the user a zoomed before/after.
Credit every author used in release/CREDITS.md, the public README's Credits and the Hackdex credits.

## Emerald (for the coming Pokémon Emerald NDS; HOENN_VERSION=emerald)

| File | What | Author (credit) |
|---|---|---|
| emerald/brendan_emerald_hyo-oppa.png | Brendan, Emerald outfit: overworld walk/run/bike/surf, item, front, 5-frame back throw (no fishing) | hyo-oppa: "give credit if used" on the sheet; the DeviantArt page also says "DO NOT EDIT!": no colour merges or other edits without asking |

## hoenn_npcs_141/ (a Discord member, 2026-10-23; installed 2026-10-25, NEW set only)

141 Gen 5-style NPC overworld sheets (32x384, 12 frames). Installed by b2tools/sprite_community_npcs.py (frames
reordered for Black 2 and shifted down one row, never redrawn or recoloured); `python3 b2tools/sprite_community_npcs.py
plan` lists every sheet's use or why it is not used. The artist is the name in the file name:

| Artist | Sheets in the folder | Used (NEW set) |
|---|---|---|
| PurpleZaffre | 72 (NPC_0xx, NPC_1xx, NPC_2xx, NPC_Zxx, Birdkeeper) | Youngster, Twins, School Kids, Picnicker, Swimmers, Tubers, Gentleman, Black Belt, Running Triathletes, Fisherman, Hiker, Scientist, Mart clerk, Psychics, Sailor, Mom, Gabby, Ty, Maxie, Ace Trainers, Beauty, Bird Keeper, Battle Girl, Camper, Ninja Boy, Bug Catcher, Bug Maniac, Parasol Lady, Lady, Poké Maniac, Pokémon Breeders, Collector |
| DiegoWT | 38 (NPCxx, trXxx, Aqua, Archie, Shelly, Wallace, Lisia, Aroma Lady, Backpacker) | Cycling Triathletes, Devon staff, cook, Pokémon Center nurse, Shelly, Rich Boy, Aroma Lady, Pokémon Ranger (M) |
| izzyvicious | 17 (Leader_*) | Drake, Phoebe, Sidney, Courtney (Ruby), the seven Frontier Brains (Emerald) |
| brawlzilla | 4 | Dragon Tamer, Kindler, Experts (M, F) |
| pokelustcompany | 1 | Hex Maniac |
| KleinStudio | 3 (Mom, Rival Mom, Wally) + 1 with Kymotonian (Birch) | none (Wally/Birch already in NEW; the Moms draw a shadow under the side frames) |
| lime029 | 1 (Hoenn Delinquent) | none (not a Gen 3 class) |

Ask the user who made these (credit pending):
- 4 sheets without an artist in the name: Leader_Wally.png (not used), NPC_026__Lass.png (Lass), trPokeFan_F.png
  (Poké Fan F), trPokeFan_M_2.png (Poké Fan M).
- 15 recolours ("_Recolour" in the name; base artist in the name, recolourist unknown): Aromalady (DiegoWT),
  Birdkeeper, NPC_009 Battle Girl, NPC_022 Reporter (Gabby), NPC_043 Lady, NPC_053 Bug Maniac, NPC_060 Ninja Boy,
  NPC_083 Parasol Lady, NPC_084 Poké Maniac, NPC_205 / NPC_208 athletes (PurpleZaffre), Leader_Courtney (izzyvicious),
  trRichBoy (DiegoWT): used; Leader_Tabitha (izzyvicious, 29 colours) and trGuitarist_2 (DiegoWT, 24 colours): not
  used (over Black 2's 15 colours; a 15-colour version from the artist would fit).
