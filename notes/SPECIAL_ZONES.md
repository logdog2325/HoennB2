# Zones Black 2's code treats specially (special_zones, 2026-10-18)

The Pearl session (PearlB2, read-only here) listed every zone id that pokebw2's decompiled C names
(PearlB2 `data/b2_special_zones.json`, made by its `b2tools/b2_special_zones.py`: "avoid" = named in code with behaviour,
"harmless" = named only in Pokédex habitat, Xtransceiver, 3D-demo, roamer and town-map data). **50 Hoenn maps and rooms
sit on "avoid" ids.** Zone ids are fixed (saves store the player's zone), so nothing moved: each piece of code was read
(decomp source; arm9 compare sites with `b2tools/armdis.py`) and what matters in a Hoenn build was switched off in the
code's or table's zone lists.

Recompute the list: `python3 b2tools/special_zones_check.py --list [zone ...]` (the json's "avoid" against every zone of
`data/hoenn_zones.json`, `data/hoenn_interiors.json`, `data/emerald/hoenn_{zones,interiors}.json` and the worlds'
`world.json` "zones": `~/HoennB2_lead/work/world_rel`, `work/agents/rustboro_em/world`). Sapphire, Ruby and Emerald
share all 50 (Emerald's own maps and rooms add none).

## What was wrong, and the fixes (b2tools/patches/special_zones.py; all versions)

| What | Code | In Hoenn before | Fix |
|---|---|---|---|
| **Location evolutions** | arm9 shinka_check.c `CheckEvolveSpecies` 0x02020788 compares the player's zone (field `playerState->zoneId`, the battle's zone, the party screen's zone for a Rare Candy) with four u16 lists in .data | Magneton / Nosepass evolved on a level-up at **Birth Island (195)** or in **Lilycove Dept. Store 1F/2F (196/197)**; Eevee became **Glaceon at Lilycove Harbor (203)**; **Leafeon was impossible** (Pinwheel Forest 155 is no Hoenn zone) | lists rewritten (ORAS's places): ICEROCK 0x0209a3e4 [203] -> **Shoal Cave ice room 139**; MOSSROCK 0x0209a3e6 [155] -> **Petalburg Woods 37**; ELEC 0x0209a3e8 [195,196,197] -> **New Mauville 132, 133, 133**; ELEC2 0x0209a3ee (method 28, no species) the same |
| **Rails** | arm9 zonedata.c `ZONE_RAIL_ASSIGNMENTS` 0x020900e8 (28 u16, zone:11 rail:5; `GetRailIDForZone` 0x02018a28) and `ZONES_WITH_RAILS` 0x020900d0 (12 u16) | 22 rooms loaded a Unova rail file + its tile attributes onto the field heap on every entry (ov036 fieldmap.c `FieldNoGridMapper_LoadByHeader`); 6 of them (36, 66, 209, 211, 214, 464) had a rail Fly-position spawn (`LoadZoneSpawnInfoCheckRail`: script `MapChangeFlyWarp`, the warp fallback, blackout, Dive). Nothing visible (no rail camera parent on the grid; only Castelia's rail file has camera areas), but dead weight and a latent wrong-spawn path | entries of Hoenn zones -> zone 0x7FF (no zone has it), as zone_effects.py does for the camera table next to it |
| **Calendar weather** (not in the decomp list: a NARC) | a/0/9/6 file 1 (24 zones; ov012 calender.c), asked by `GetWeatherAll` whenever the save's season is the real one: always, with hoenn_season's summer lock or the seasons option | hoenn_world.py drops the world's outdoor zones, but rooms kept theirs: **Lilycove Dept. Store 3F (199), Lilycove House 1 (206), Slateport House 1 (614)** had Unova's rain / snow / (4, 5) on ~170, ~210 and 65 days of the year, indoors (ov036 weather.c `SetWeatherInit` has no indoor check) | every Hoenn zone's entry -> 0xFFFF (file size kept) |

Checker: `python3 b2tools/special_zones_check.py <build dir>` (code/ and files/ of a HOENN_BUILD_DIR before its
intermediates go): no camera, rail, version-swap, gimmick, a/0/8/0#29 or calendar entry names a Hoenn zone, and the
evolution lists are the new places.

**Location evolutions, the choice:** ORAS's own places (Moss Rock in Petalburg Woods, Ice Rock in Shoal Cave, New
Mauville's magnetic field); the whole zone counts, as in Black 2. Other choices are one line in special_zones.py
(EVO_PLACES): e.g. Glaceon on Shoal Cave's other rooms, Magnezone also in Mt. Chimney, or a list set to an unused id
(no location evolution at all).

## All 50 zones

"zone_effects" = already switched off by b2tools/patches/zone_effects.py (gimmick table a/1/0/2, a/0/8/0#29, ISS city
sounds, arm9 `ZONE_CAMERA_ASSIGNMENTS` 0x020900ac and `VERSION_SPECIFIC_ZONES` 0x0209a348, ov012 script plugins).
"Dead" = a table no code of the ROM reads (decomp comment: "read by the functions the original link dropped").
zonedata.c names every id in `ZONE_COUNT` = Pledge Grove + 1 (615 zones): not listed again below.

| Zone | Black 2 | Hoenn map / room | Code that names it | In Hoenn | Verdict |
|---|---|---|---|---|---|
| 1 | Black City PC | DewfordTown_PokemonCenter_1F | zonedata.c `BC_WF_ZONES` | dead table | harmless |
| 2 | Black City 2 | AquaHideout_1F | `BC_WF_ZONES` | dead | harmless |
| 3 | Black City 3 | SlateportCity_House2 | `BC_WF_ZONES` | dead | harmless |
| 4 | Black City 4 | SlateportCity_Mart | `BC_WF_ZONES` | dead | harmless |
| 5 | Black City 5 | AquaHideout_B1F | `BC_WF_ZONES` | dead | harmless |
| 30 | Castelia City 2 | DewfordTown_House1 | `ZONE_RAIL_ASSIGNMENTS` (rail 2) | rails loaded | **fixed** (rails) |
| 36 | Castelia City 8 | EverGrandeCity_Corridor2 | `ZONES_WITH_RAILS`, rail 3; demo3d_data.c (demo 10's light zone) | rails; demo 10 never plays (Hoenn plays demos 4 and 26) | **fixed** (rails); demo harmless |
| 40 | Castelia City 12 | SafariZone_Southeast (Emerald: + _Emerald) | event_mapchange.c `GameData_UpdateEscapeRopeZone`: a warp from 40 into Castelia Sewers 495 stores the rope exit; demo3d_data.c (demo 2) | no Hoenn zone 495 (now AVOID); demo 2 never plays | harmless |
| 66 | Gear Station | EverGrandeCity_PokemonCenter_2F | `ZONES_WITH_RAILS`, rail 4 | rails | **fixed** (rails) |
| 67-73 | Gear Station 2-8 | VerdanturfTown_House, _Mart, _PokemonCenter_2F, _WandasHouse, AbandonedShip_CaptainsOffice, _Corridors_1F, _Corridors_B1F | `GEAR_STATION_PLATFORM_ZONES` | dead; their gimmick entries (16-22): zone_effects | harmless |
| 114 | Icirrus City 2 | FortreeCity_DecorationShop | rail 5; gimmick 9; a/0/8/0#29 | rails | **fixed** (rails); rest zone_effects |
| 121 | Opelucid Gym | FortreeCity_House1 | rail 6; gimmick 10 | rails | **fixed** (rails) |
| 137 | Pokémon League 2 | FortreeCity_House2 | rail 7; gimmick 14 | rails | **fixed** (rails) |
| 138 | Pokémon League 3 | ShoalCave_LowTideEntranceRoom | `ZONE_CAMERA_ASSIGNMENTS` (camera 0); gimmick 15 | zone_effects | harmless (handled) |
| 140-144 | Pokémon League 5-9 | FortreeCity_House3, _House4, _House5, _Mart, _PokemonCenter_2F | rails 8-12; gimmicks 39-42, 46; 140 a/0/8/0#29 | rails | **fixed** (rails) |
| 157 | Desert Resort | Route124 | zonedata.c area swap `#ifdef WHITE2` (not in Black 2); zukan habitat key (data); gimmick 25 | - | harmless |
| 158 | Desert Resort 2 | FarawayIsland_Entrance | event_mapchange.c: a warp or Fly from 158 into a zone where Escape Rope works stores the rope exit | 158 leads only to FarawayIsland_Interior (159, rope off); no Hoenn outdoor zone allows the rope; the boat home is a script warp | harmless (never fires) |
| 195 | Chargestone Cave 2 | BirthIsland_Exterior | field_gimmick_d06.c (floating stones: ov107, only as the zone's gimmick, entry 13: zone_effects); shinka_check.c ELEC | Magnezone/Probopass here | **fixed** (evolutions) |
| 196 | Chargestone Cave 3 | LilycoveCity_DepartmentStore_1F | same | same | **fixed** (evolutions) |
| 197 | Chargestone Cave 4 | LilycoveCity_DepartmentStore_2F | same | same | **fixed** (evolutions) |
| 203 | Twist Mountain 6 | LilycoveCity_Harbor | shinka_check.c ICEROCK; a/0/8/0#29 | Glaceon here | **fixed** (evolutions) |
| 209 | Dragonspiral Tower 5 | LilycoveCity_House4 | `ZONES_WITH_RAILS`, rail 13 | rails | **fixed** (rails) |
| 211 | Dragonspiral Tower 7 | LilycoveCity_LilycoveMuseum_2F | `ZONES_WITH_RAILS`, rail 14 | rails | **fixed** (rails) |
| 214 | Victory Road 2 | LilycoveCity_PokemonTrainerFanClub | `ZONES_WITH_RAILS`, rail 15; a/0/8/0#29 | rails | **fixed** (rails) |
| 317 | Route 1 | Route101 | ov308 beacon_detail_sub.c: a received C-Gear beacon with a zone >= 615 shows Route 1's place name (= "Route 101" here); zukan key; gimmick 32 | text only | harmless |
| 326 | Route 4 | Route103 | dowsing.c (`ZONE_OTHER_ROUTE_4` is 326 in White 2 only); field_encount_st.c roamer route list; townmap.c (Fly to Join Avenue 489 lands on Route 4); camera 4 + version swap 326<->551; zukan; gimmick 25 | roamer list read only by the gated gate news board (roamers.py); 489 is DENY; camera/swap/gimmick: zone_effects | harmless (handled) |
| 337 | Route 7 | Route106 | zone_weather.c `GetRoute7WeatherIfApplicable` (0x02033048): weather 7 while flag 0x96D (2413) is set; roamer list; Xtransceiver secret-call zones; zukan | nothing sets 2413 (badges use 2414-2421; 2413 is not in story_ids' free pool); Emerald replaces the function (emerald_postgame part A); the secret call needs Black 2's call progress | dormant |
| 338 | Celestial Tower 2 | MossdeepCity_SpaceCenter_2F | rail 20; zukan | rails | **fixed** (rails) |
| 339 | Celestial Tower 3 | MossdeepCity_StevensHouse | rail 21 | rails | **fixed** (rails) |
| 340 | Celestial Tower 4 | MtChimney_CableCarStation | rail 22 | rails | **fixed** (rails) |
| 341 | Celestial Tower 5 | MtPyre_1F | rail 23 | rails | **fixed** (rails) |
| 374 | Route 14 | Route112 | zonedata.c `GetIsZoneRoute14Or15` 0x02018ea8 -> zone_weather.c `GetBirthdayZoneWeather`: weather 0 on the DS owner's birthday; roamer list; secret-call zones; zukan | Route 112's weather is 0 anyway (header 0, calendar entry dropped by hoenn_world, no weather.py / fixed_weather rule); Emerald skips the call | dormant |
| 378 | Route 15 | Route113 | same birthday rule; roamer list; zukan | Route 113's ash is its part zone 611 + hoenn_ash, not 378's weather | dormant |
| 418 | Anville Town | PacifidlogTown_House3 | camera 6 | zone_effects | harmless (handled) |
| 425 | White Forest PC | RustboroCity_PokemonCenter_1F | `BC_WF_ZONES` | dead | harmless |
| 464 | Marine Tube | PetalburgCity_House2 | `ZONES_WITH_RAILS`, rail 19; gimmick 50; a/0/8/0#29 | rails | **fixed** (rails) |
| 551 | Route 4 (W2) | Route122 | dowsing.c: hidden items of 551 are not dowsed from another zone; camera 5 + version swap; gimmick 25 | Route 122 has no hidden items (any version); the rest: zone_effects | harmless (handled) |
| 561 | Plasma Frigate 10 | Route117_PokemonDayCare | camera 7; gimmick 43 | zone_effects | harmless (handled) |
| 564 | Plasma Frigate 13 | Route119_WeatherInstitute_2F | camera 7; gimmick 43 | zone_effects | harmless (handled) |
| 614 | Pledge Grove | SlateportCity_House1 | game_beacon_accessor.c `BEACON_ZONE_COUNT` (= 615: 614 is valid); gimmick 57; **calendar** | calendar rain/snow indoors | **fixed** (calendar) |

Also fixed, though no decomp name: **199** LilycoveCity_DepartmentStore_3F and **206** LilycoveCity_House1 (calendar).

Harmless-data files (PearlB2's list): zukan_common.c / zukan_habitat.c (ov302/ov303: the Habitat list's areas, keyed by
Black 2's own "arrived" flags; the zone is only the area's id in the list and the save), local_tvt_calldata.c,
demo3d_data.c, field_encount_st.c (`ROAMING_POKEMON_ZONES`), townmap.c.

## Dormant rules (watch when changing these maps)

- **Route 106 (337)**: give flag 2413 a meaning and Sapphire/Ruby's Route 106 turns to heavy rain (Black 2's Route 7
  weather; `GetRoute7WeatherIfApplicable` compares 0x151 at 0x02033052's literal). Not patched: the flag is never set,
  and in Emerald emerald_postgame.py asserts those bytes are Black 2's before it replaces them.
- **Routes 112/113 (374/378)**: in Sapphire/Ruby a weather given to these zones (header, weather.py, calendar) is
  replaced by weather 0 on the DS owner's birthday (`GetIsZoneRoute14Or15`, literal 378 at 0x02018ebc, 374 = 378 - 4).
- **Future maps and rooms**: allocate_zones.py's AVOID now also holds the 6 decomp-named ids no Hoenn zone had (155, 426,
  455, 495, 502, 566), so every id the decompiled code names is either one of these 50 or in DENY/AVOID.
  special_zones.py and zone_effects.py work from `zone_effects.our_zones()`, so a new room on a rail, calendar,
  camera or gimmick id is switched off by itself.
- The decomp is ~87% decompiled: code not yet decompiled may name more zones (HoennB2's own DENY list came from the arm9
  checks at 0x02018a54-0x02018ee4; the rail tables sit just before that range, which is why they were missed).
