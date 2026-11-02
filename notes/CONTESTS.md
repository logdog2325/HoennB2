# Pokémon Contests, Pokéblocks and the Berry Blender (v18.4 / Emerald v1.5)

Real Gen 3 Contests in Black 2, in C on the decomp, single-player. They take over the Contest Hall counters from Black 2's Musical.

**The Musical stays** (user, 2026-11-01: players already have it): one person in Lilycove's Contest Lobby, all three versions, runs its
old flow and lines (`LB_MusicalHost`, common/musical.inc, patches/musical.py). Not in Sapphire: Gen 3 has no such person. A new object,
uid 30, model 16 (the Girl already in this zone, so no new sprite): Sapphire/Ruby at (12,4), Emerald at (20,4), Gen 3's collision free and off the routes to
every warp. Text: the 14 lines after CL_* in the lobby's file, lines 63-76 (Emerald 65-78); script text has no fixed slot (only system
text has: text.py fixed_slots), and a/0/0/3 and a/0/5/6 have 1 MB of reserve each. People limit: the zone has at most 14 (S/R) or 25 (E)
Gen 3 objects, so + this one + the player's two is at most 17/32 and 28/40, whatever is placed; npc_check.py reads a built ROM: see
the lead's build. Its first line still says Contests are on hold, as asked (original lines); line 63 / 65 is the one to change.

## What runs where
| Part | File | Size |
|---|---|---|
| Rules, turn order, scores | decomp `src/hoennb2/contest/contest_logic.c` (pokeemerald contest.c's functions, Gen 3 names) | overlay 346: 36,032 B + 352 B of BSS, in all |
| Move effects | `src/hoennb2/contest/contest_effect.c` (pokeemerald contest_effect.c, token-for-token the same as pokeruby's) | |
| AI VM | `src/hoennb2/contest/contest_ai.c` (pokeemerald contest_ai.c) | |
| Stage screen | `src/hoennb2/contest/contest_app.c`, `contest_ui.h` (pokeemerald's tasks as one state machine) | |
| Results | `src/hoennb2/contest/contest_results.c` | |
| Blender, Case, feeding | `src/hoennb2/pokeblock/` (blender_app.c, case_app.c, pokeblock_logic.c) | overlay 347: 8,256 B + 32 B of BSS |
| Script commands, save, ribbons, Bag hook | `src/hoennb2/resident/contest_cmd.c`, `ext_cmd.c` | the resident section |
| Hooks (one pointer or row each) | ov012 scrcmd_vm.c (command 0x15F), ov012 itemuse_event.c (Entralink's row), ov142 itemmenu.c (Bicycle's row covers the Case) | |
| Per-version data | archive 271 (Pokéstar's): `b2tools/contest_data.py`, `contest_blend_data.py`, `patches/contests.py` | 111 KB (S/R), 114 KB (E) of 516 KB |
| Reception | `src/field_scripts/common/contests.inc`, the lobby scripts, `b2tools/gen_contest_text.py` | about 1 KB of script + 37 lines per lobby |
| Checks | `b2tools/contest_check.py`, `b2tools/contest_host/` | |

Both overlays load at Black 2's app address (0x021998C0, after overlay 29, where the Bag and Battle load), so they cost
the arena nothing. `tools/hoennb2/link_overlays.py` APP_OVERLAYS + APP_ADDRESS_OVERLAYS say so. The field closes (overlay 36
unloads) before EventFieldSubprocessCall queues the screen, as for the Bag and the Box, so nothing else is there.

## Save
Block 0x47 (Pokéstar's, 996 B) from +552: `PokeblockSave`, 292 B (magic "PLB3", 3 blender records, 40 x 7 B Pokéblocks), +552 to
+844. berries.c now stops at Gen 3's 90 tree ids (N_TREES 90; every loop, the set-up, the tables), ending at +552: `struct
BerrySave` = 552 B, checked when compiled. An existing save has zeros from +552 to +780 (the old set-up) and Pokéstar's bytes
from +780 on, or Pokéstar's throughout: no magic, so the Case starts empty. contest_check.py runs berries.c's own growth code
on such a block with Contest data at +552: unchanged after updates of up to 2,000,000 minutes, and the trees come out the same as with the old 128-tree bound.
Conditions and ribbons are Black 2's own PKM fields (PKM_PARAM_CONTEST_COOL..SHEEN, PKM_PARAM_RIBBON_G3_COOL + 4 x category + rank).
Flag: FLAG_RECEIVED_CONTEST_PASS 2573. Work: VAR_CONTEST_PRIZE_PICKUP 0x419A. Both named in common/contests.inc for the lead to register.

## Per version
Sapphire/Ruby (pokeruby): Verdanturf Normal, Fallarbor Super, Slateport Hyper, Lilycove Master; Contest Pass from Verdanturf's
receptionist, needed everywhere. 60 opponents. Emerald (pokeemerald): Lilycove only, every rank from a menu, no pass, 96 opponents, 36 of
them filtered by the Hall of Fame (`filter`), Pokéblock Case from the receptionist. Moves and effects are the same in both decomps (compared);
AI scripts differ slightly: each version carries its own (2,524 / 2,551 B). Art and contest-screen lines are pokeemerald's for all three (the same
pictures; pokeruby's wording matches but for capitalisation). The lobbies' lines come from each version's decomp.

## Left out or approximated (for the release notes)
- No Gen 3 battle animations in a Contest: the Pokémon hops and cries instead. Black 2's animations are tied to its 3D battle.
- The stage intro and the award are on the Contest screen (a greeting, each entry's picture, the results, the ribbon lines), not Gen 3's walking scene in a separate room.
- No link Contests, no TV or Contest Live Updates, no Lilycove Art Museum paintings or winners' pictures in the Hall.
- Results: no sliding text boxes or confetti; the bars and stars are Gen 3's tiles.
- The sliding heart's spin (an affine animation) is a plain hide and show; the contestant box's blink is a palette flash.
- Berry Blender: the rules are Gen 3's (speed, hits, opponents' presses, RPM, the Pokéblock's formula), with the disc turning on an affine BG as Gen 3's. No Blend Master set (Lilycove's expert in Emerald); Emerald's Blender people are at the existing spots only.
- Pokéblock Case: a text list in Black 2's windows over Gen 3's menu art (the list in the big panel, the chosen one's flavors as words and its feel in the left box); no condition graph (that is the PokéNav's), no feeding animation: the condition rises and a line says so.
- Safari Zone Pokéblock feeders: not built (HoennB2's Safari has no bait or feeders; they would need the Case's choice, objects and a hook in the wild-Pokémon generator).
- The art of the Blender machines is not placed: people stand for them, as in Sapphire's Blend Master.

## Black 2's moves after Gen 3's 354
Gen 3's table covers 1-354. Each later move takes the contest effect of the closest Gen 3 move (`b2tools/contest_data.py`
NEW_MOVES); moves up to 467 keep their category from Pearl's own data (PearlB2 pokeplatinum res/moves), later ones the clone's.
No combos. Lead: please read this over.

| id | move | as | category (source) |
|---|---|---|---|
| 355 | ROOST | RECOVER | Cool (pearl) |
| 356 | GRAVITY | RAIN_DANCE | Beauty (pearl) |
| 357 | MIRACLE_EYE | FORESIGHT | Cute (pearl) |
| 358 | WAKE_UP_SLAP | SMELLING_SALT | Smart (pearl) |
| 359 | HAMMER_ARM | CRABHAMMER | Cool (pearl) |
| 360 | GYRO_BALL | RAPID_SPIN | Beauty (pearl) |
| 361 | HEALING_WISH | MEMENTO | Cute (pearl) |
| 362 | BRINE | SURF | Smart (pearl) |
| 363 | NATURAL_GIFT | SECRET_POWER | Cool (pearl) |
| 364 | FEINT | FAKE_OUT | Beauty (pearl) |
| 365 | PLUCK | THIEF | Cute (pearl) |
| 366 | TAILWIND | AGILITY | Smart (pearl) |
| 367 | ACUPRESSURE | DEFENSE_CURL | Cool (pearl) |
| 368 | METAL_BURST | METAL_CLAW | Beauty (pearl) |
| 369 | U_TURN | BATON_PASS | Cute (pearl) |
| 370 | CLOSE_COMBAT | CROSS_CHOP | Smart (pearl) |
| 371 | PAYBACK | REVENGE | Cool (pearl) |
| 372 | ASSURANCE | PURSUIT | Beauty (pearl) |
| 373 | EMBARGO | TORMENT | Cute (pearl) |
| 374 | FLING | THIEF | Tough (pearl) |
| 375 | PSYCHO_SHIFT | HEAL_BELL | Cool (pearl) |
| 376 | TRUMP_CARD | SWIFT | Cool (pearl) |
| 377 | HEAL_BLOCK | IMPRISON | Cute (pearl) |
| 378 | WRING_OUT | CRUSH_CLAW | Smart (pearl) |
| 379 | POWER_TRICK | BULK_UP | Cool (pearl) |
| 380 | GASTRO_ACID | ACID_ARMOR | Beauty (pearl) |
| 381 | LUCKY_CHANT | SAFEGUARD | Cute (pearl) |
| 382 | ME_FIRST | MIMIC | Cute (pearl) |
| 383 | COPYCAT | MIMIC | Cool (pearl) |
| 384 | POWER_SWAP | SKILL_SWAP | Beauty (pearl) |
| 385 | GUARD_SWAP | SKILL_SWAP | Cute (pearl) |
| 386 | PUNISHMENT | REVERSAL | Smart (pearl) |
| 387 | LAST_RESORT | DOUBLE_EDGE | Cute (pearl) |
| 388 | WORRY_SEED | SPORE | Beauty (pearl) |
| 389 | SUCKER_PUNCH | QUICK_ATTACK | Smart (pearl) |
| 390 | TOXIC_SPIKES | SPIKES | Smart (pearl) |
| 391 | HEART_SWAP | SKILL_SWAP | Cool (pearl) |
| 392 | AQUA_RING | INGRAIN | Beauty (pearl) |
| 393 | MAGNET_RISE | BOUNCE | Cute (pearl) |
| 394 | FLARE_BLITZ | BLAST_BURN | Smart (pearl) |
| 395 | FORCE_PALM | ARM_THRUST | Cool (pearl) |
| 396 | AURA_SPHERE | AEROBLAST | Beauty (pearl) |
| 397 | ROCK_POLISH | AGILITY | Tough (pearl) |
| 398 | POISON_JAB | POISON_TAIL | Smart (pearl) |
| 399 | DARK_PULSE | CRUNCH | Cool (pearl) |
| 400 | NIGHT_SLASH | SLASH | Beauty (pearl) |
| 401 | AQUA_TAIL | IRON_TAIL | Cute (pearl) |
| 402 | SEED_BOMB | SLUDGE_BOMB | Smart (pearl) |
| 403 | AIR_SLASH | AIR_CUTTER | Cool (pearl) |
| 404 | X_SCISSOR | SLASH | Beauty (pearl) |
| 405 | BUG_BUZZ | SIGNAL_BEAM | Cute (pearl) |
| 406 | DRAGON_PULSE | DRAGON_BREATH | Smart (pearl) |
| 407 | DRAGON_RUSH | DRAGON_CLAW | Cool (pearl) |
| 408 | POWER_GEM | ANCIENT_POWER | Beauty (pearl) |
| 409 | DRAIN_PUNCH | GIGA_DRAIN | Beauty (pearl) |
| 410 | VACUUM_WAVE | MACH_PUNCH | Smart (pearl) |
| 411 | FOCUS_BLAST | FOCUS_PUNCH | Cool (pearl) |
| 412 | ENERGY_BALL | SOLAR_BEAM | Beauty (pearl) |
| 413 | BRAVE_BIRD | SKY_ATTACK | Cute (pearl) |
| 414 | EARTH_POWER | EARTHQUAKE | Smart (pearl) |
| 415 | SWITCHEROO | TRICK | Cool (pearl) |
| 416 | GIGA_IMPACT | HYPER_BEAM | Beauty (pearl) |
| 417 | NASTY_PLOT | AMNESIA | Cute (pearl) |
| 418 | BULLET_PUNCH | MACH_PUNCH | Smart (pearl) |
| 419 | AVALANCHE | REVENGE | Cool (pearl) |
| 420 | ICE_SHARD | QUICK_ATTACK | Beauty (pearl) |
| 421 | SHADOW_CLAW | SLASH | Cute (pearl) |
| 422 | THUNDER_FANG | THUNDER_PUNCH | Smart (pearl) |
| 423 | ICE_FANG | ICE_PUNCH | Cool (pearl) |
| 424 | FIRE_FANG | FIRE_PUNCH | Beauty (pearl) |
| 425 | SHADOW_SNEAK | QUICK_ATTACK | Smart (pearl) |
| 426 | MUD_BOMB | MUD_SHOT | Smart (pearl) |
| 427 | PSYCHO_CUT | SLASH | Cool (pearl) |
| 428 | ZEN_HEADBUTT | HEADBUTT | Beauty (pearl) |
| 429 | MIRROR_SHOT | MIST_BALL | Cute (pearl) |
| 430 | FLASH_CANNON | STEEL_WING | Smart (pearl) |
| 431 | ROCK_CLIMB | ROCK_SLIDE | Cool (pearl) |
| 432 | DEFOG | HAZE | Beauty (pearl) |
| 433 | TRICK_ROOM | SKILL_SWAP | Cute (pearl) |
| 434 | DRACO_METEOR | OVERHEAT | Smart (pearl) |
| 435 | DISCHARGE | THUNDERBOLT | Cool (pearl) |
| 436 | LAVA_PLUME | ERUPTION | Tough (pearl) |
| 437 | LEAF_STORM | OVERHEAT | Cute (pearl) |
| 438 | POWER_WHIP | VINE_WHIP | Beauty (pearl) |
| 439 | ROCK_WRECKER | ROCK_THROW | Tough (pearl) |
| 440 | CROSS_POISON | SLASH | Cool (pearl) |
| 441 | GUNK_SHOT | SLUDGE_BOMB | Cool (pearl) |
| 442 | IRON_HEAD | HEADBUTT | Tough (pearl) |
| 443 | MAGNET_BOMB | SWIFT | Cool (pearl) |
| 444 | STONE_EDGE | ROCK_SLIDE | Tough (pearl) |
| 445 | CAPTIVATE | ATTRACT | Beauty (pearl) |
| 446 | STEALTH_ROCK | SPIKES | Cool (pearl) |
| 447 | GRASS_KNOT | LOW_KICK | Smart (pearl) |
| 448 | CHATTER | SING | Smart (pearl) |
| 449 | JUDGMENT | EXTREME_SPEED | Smart (pearl) |
| 450 | BUG_BITE | THIEF | Tough (pearl) |
| 451 | CHARGE_BEAM | CHARGE | Beauty (pearl) |
| 452 | WOOD_HAMMER | DOUBLE_EDGE | Tough (pearl) |
| 453 | AQUA_JET | QUICK_ATTACK | Beauty (pearl) |
| 454 | ATTACK_ORDER | FURY_CUTTER | Smart (pearl) |
| 455 | DEFEND_ORDER | IRON_DEFENSE | Smart (pearl) |
| 456 | HEAL_ORDER | RECOVER | Smart (pearl) |
| 457 | HEAD_SMASH | DOUBLE_EDGE | Tough (pearl) |
| 458 | DOUBLE_HIT | DOUBLE_KICK | Smart (pearl) |
| 459 | ROAR_OF_TIME | HYPER_BEAM | Cool (pearl) |
| 460 | SPACIAL_REND | AEROBLAST | Tough (pearl) |
| 461 | LUNAR_DANCE | MEMENTO | Beauty (pearl) |
| 462 | CRUSH_GRIP | CRUSH_CLAW | Tough (pearl) |
| 463 | MAGMA_STORM | FIRE_SPIN | Tough (pearl) |
| 464 | DARK_VOID | GRASS_WHISTLE | Smart (pearl) |
| 465 | SEED_FLARE | SOLAR_BEAM | Cool (pearl) |
| 466 | OMINOUS_WIND | ANCIENT_POWER | Smart (pearl) |
| 467 | SHADOW_FORCE | DIG | Smart (pearl) |
| 468 | HONE_CLAWS | SHARPEN | Cute (clone) |
| 469 | WIDE_GUARD | PROTECT | Cute (clone) |
| 470 | GUARD_SPLIT | PAIN_SPLIT | Smart (clone) |
| 471 | POWER_SPLIT | PAIN_SPLIT | Smart (clone) |
| 472 | WONDER_ROOM | IMPRISON | Smart (clone) |
| 473 | PSYSHOCK | PSYCHIC | Smart (clone) |
| 474 | VENOSHOCK | SLUDGE_BOMB | Tough (clone) |
| 475 | AUTOTOMIZE | AGILITY | Cool (clone) |
| 476 | RAGE_POWDER | FOLLOW_ME | Cute (clone) |
| 477 | TELEKINESIS | CONFUSION | Smart (clone) |
| 478 | MAGIC_ROOM | IMPRISON | Smart (clone) |
| 479 | SMACK_DOWN | ROCK_THROW | Tough (clone) |
| 480 | STORM_THROW | SEISMIC_TOSS | Tough (clone) |
| 481 | FLAME_BURST | EMBER | Beauty (clone) |
| 482 | SLUDGE_WAVE | SLUDGE | Tough (clone) |
| 483 | QUIVER_DANCE | DRAGON_DANCE | Cool (clone) |
| 484 | HEAVY_SLAM | BODY_SLAM | Tough (clone) |
| 485 | SYNCHRONOISE | PSYWAVE | Smart (clone) |
| 486 | ELECTRO_BALL | SHOCK_WAVE | Cool (clone) |
| 487 | SOAK | WATER_SPORT | Cute (clone) |
| 488 | FLAME_CHARGE | FLAME_WHEEL | Beauty (clone) |
| 489 | COIL | BULK_UP | Beauty (clone) |
| 490 | LOW_SWEEP | ROCK_SMASH | Tough (clone) |
| 491 | ACID_SPRAY | ACID | Smart (clone) |
| 492 | FOUL_PLAY | FAINT_ATTACK | Smart (clone) |
| 493 | SIMPLE_BEAM | CONVERSION | Beauty (clone) |
| 494 | ENTRAINMENT | ROLE_PLAY | Cute (clone) |
| 495 | AFTER_YOU | FOLLOW_ME | Cute (clone) |
| 496 | ROUND | SING | Cute (clone) |
| 497 | ECHOED_VOICE | UPROAR | Cute (clone) |
| 498 | CHIP_AWAY | FALSE_SWIPE | Cool (clone) |
| 499 | CLEAR_SMOG | HAZE | Beauty (clone) |
| 500 | STORED_POWER | PSYCH_UP | Smart (clone) |
| 501 | QUICK_GUARD | DETECT | Cool (clone) |
| 502 | ALLY_SWITCH | BATON_PASS | Cute (clone) |
| 503 | SCALD | SURF | Beauty (clone) |
| 504 | SHELL_SMASH | BELLY_DRUM | Cute (clone) |
| 505 | HEAL_PULSE | HEAL_BELL | Beauty (clone) |
| 506 | HEX | SHADOW_PUNCH | Smart (clone) |
| 507 | SKY_DROP | FLY | Smart (clone) |
| 508 | SHIFT_GEAR | DRAGON_DANCE | Cool (clone) |
| 509 | CIRCLE_THROW | SEISMIC_TOSS | Tough (clone) |
| 510 | INCINERATE | FLAMETHROWER | Beauty (clone) |
| 511 | QUASH | TAUNT | Smart (clone) |
| 512 | ACROBATICS | AERIAL_ACE | Cool (clone) |
| 513 | REFLECT_TYPE | CONVERSION_2 | Beauty (clone) |
| 514 | RETALIATE | REVENGE | Tough (clone) |
| 515 | FINAL_GAMBIT | MEMENTO | Tough (clone) |
| 516 | BESTOW | TRICK | Smart (clone) |
| 517 | INFERNO | FLAMETHROWER | Beauty (clone) |
| 518 | WATER_PLEDGE | WATER_PULSE | Beauty (clone) |
| 519 | FIRE_PLEDGE | FLAMETHROWER | Beauty (clone) |
| 520 | GRASS_PLEDGE | PETAL_DANCE | Beauty (clone) |
| 521 | VOLT_SWITCH | THUNDERBOLT | Cool (clone) |
| 522 | STRUGGLE_BUG | SIGNAL_BEAM | Beauty (clone) |
| 523 | BULLDOZE | MAGNITUDE | Tough (clone) |
| 524 | FROST_BREATH | ICY_WIND | Beauty (clone) |
| 525 | DRAGON_TAIL | ROAR | Cool (clone) |
| 526 | WORK_UP | GROWTH | Beauty (clone) |
| 527 | ELECTROWEB | THUNDER_WAVE | Cool (clone) |
| 528 | WILD_CHARGE | VOLT_TACKLE | Cool (clone) |
| 529 | DRILL_RUN | HORN_DRILL | Cool (clone) |
| 530 | DUAL_CHOP | DOUBLE_KICK | Cool (clone) |
| 531 | HEART_STAMP | STOMP | Tough (clone) |
| 532 | HORN_LEECH | MEGA_DRAIN | Smart (clone) |
| 533 | SACRED_SWORD | SLASH | Cool (clone) |
| 534 | RAZOR_SHELL | CRABHAMMER | Tough (clone) |
| 535 | HEAT_CRASH | BODY_SLAM | Tough (clone) |
| 536 | LEAF_TORNADO | RAZOR_LEAF | Cool (clone) |
| 537 | STEAMROLLER | STOMP | Tough (clone) |
| 538 | COTTON_GUARD | COTTON_SPORE | Beauty (clone) |
| 539 | NIGHT_DAZE | CRUNCH | Tough (clone) |
| 540 | PSYSTRIKE | PSYCHIC | Smart (clone) |
| 541 | TAIL_SLAP | TAIL_WHIP | Cute (clone) |
| 542 | HURRICANE | THUNDER | Cool (clone) |
| 543 | HEAD_CHARGE | TAKE_DOWN | Tough (clone) |
| 544 | GEAR_GRIND | DOUBLE_KICK | Cool (clone) |
| 545 | SEARING_SHOT | FLAMETHROWER | Beauty (clone) |
| 546 | TECHNO_BLAST | TRI_ATTACK | Beauty (clone) |
| 547 | RELIC_SONG | PERISH_SONG | Beauty (clone) |
| 548 | SECRET_SWORD | SLASH | Cool (clone) |
| 549 | GLACIATE | ICY_WIND | Beauty (clone) |
| 550 | BOLT_STRIKE | THUNDER | Cool (clone) |
| 551 | BLUE_FLARE | SACRED_FIRE | Beauty (clone) |
| 552 | FIERY_DANCE | TEETER_DANCE | Cute (clone) |
| 553 | FREEZE_SHOCK | THUNDERBOLT | Cool (clone) |
| 554 | ICE_BURN | ICE_BEAM | Beauty (clone) |
| 555 | SNARL | SCREECH | Smart (clone) |
| 556 | ICICLE_CRASH | ICICLE_SPEAR | Beauty (clone) |
| 557 | V_CREATE | OVERHEAT | Beauty (clone) |
| 558 | FUSION_FLARE | FLAMETHROWER | Beauty (clone) |
| 559 | FUSION_BOLT | THUNDERBOLT | Cool (clone) |
| 560 | FAIRY_WIND | GUST | Smart (clone) |
| 561 | DISARMING_VOICE | SWIFT | Cool (clone) |
| 562 | DRAINING_KISS | SWEET_KISS | Cute (clone) |
| 563 | DAZZLING_GLEAM | FLASH | Beauty (clone) |
| 564 | PLAY_ROUGH | FLAIL | Cute (clone) |
| 565 | MOONBLAST | MOONLIGHT | Beauty (clone) |

## First emulator run (combined Sapphire ROM, 2026-11-01)

Found in the game, fixed on feat/contests; `contest_check.py` keeps the first three:
- Field music: the Contest plays its own BGM with `GFL_SndBGMPlay`, so without a push the lobby kept `mus_contest_winner` for good. `contests.inc` now wraps `con_run` in `BGMPush 30` / `BGMPop 0, 60`, as Black 2's Musical does.
- `CL_RIBBON_PUT` printed the player's name twice: the script's word 0 is the player, word 1 the Pokémon.
- `GFL_BGSysLoadChar`'s offset is in tiles, not bytes: results icons were garbled, the crowd's second frame went out of range.
- Results: the three other rows' names were colour 2 on nothing (invisible); Gen 3's printer uses 1 with shadow 8.
- Sub screen: lavender behind Contest, Blender and Case (an uninitialised backdrop); now black.
- Blender: Gen 3's four name boxes were empty, the RPM was a clipped text line below the picture while the picture's own 000.00 box stayed 000.00 (now tiles `RPM_DIGIT + digit`, as UpdateRPM), the message had no window. NPC names are StartBerryBlender's Mister / Dude, Lassie / Miss, Laddie, Lassie.
- Case: the windows ignored the art (list across the title box, Feel off the panel, message clipped). All in stage coordinates now, the message above the list on a white window.
- The Bag opened on its last pocket for the Berry; `con_has_berries` now points it at Berries, as Gen 3.

Second run (round 2 ROMs): `BmpWin_CreateStatic` returns NULL when its characters overlap another window's, and the results rows 0-2 overlapped the stage's `descWin` (a NULL bitmap, bad reads on hardware): the rows now start at 0x340. The Blender's disc was 48 px too high, because its map's centre is (120, 80), not (128, 128); it now turns with the arrow on BG 3 (mode 1, 8bpp tiles, Gen 3's byte map), and the marker is gone. The script's list menus start below the speech bubble (row 6), including the Musical's show menu.
