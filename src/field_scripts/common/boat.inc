// Boat and ship trips and the cable car (boats agent, 2026-10-07): Black 2's own 3D boat cutscenes ("3D demos",
// Call3DDemo) for every crossing of the story; the cable car ride at the end. Macros only (no code, no labels);
// included by src/include/hoenn_story.inc, so every script has them. The trip scripts call h_sail_briney /
// h_sail_ferry / h_ride_cable_car (hoenn_story.inc), which use the macros below.
//
// What Black 2 has (read in the decomp and its data, then played in the emulator: screenshots/boats/):
// - Boats and ships move only in the 3D demos of overlay 293 (Call3DDemo id, param = field command 340,
//   ov012 s0154_Call3DDemo -> Event3DDemo_Create; models in a/1/5/8). The field has no moving ship: docked ships are
//   map buildings shown/hidden with BMSetVisible (Castelia harbor 0076.s) or MapReplaceSetEvent (Virbank 0904.s), the
//   Royal Unova is one interior zone (52) with no scrolling sea, and no field effect moves a ship model.
// - The demo table (ov293 0x021a6e4c, 27 entries of 20 bytes: shots, command list, actors, ...; command 6 = BGM,
//   1 = sound effect, 10 = fade, 19 = end; frames at 30 fps) and the scripts that play them:
//     2  Royal Unova departs (0104.s, after boarding): over the liner's deck, then the liner leaving a pier under a
//        fixed sunset sky; 9 s; no BGM of its own (SE VDEMO_01/03, FLD_78)
//     4  Castelia -> Unity Tower boat (0074.s): a small white-and-blue motorboat pulls away from a stone pier (lamps,
//        planters, two passers-by), top-down camera, the wake; 4.3 s; light follows the time of day; no BGM (SE
//        VDEMO_01 engine, VDEMO_02 speeding off)
//     10 Castelia -> Liberty Garden boat (0072.s): a small yellow motorboat leaves a concrete pier and speeds off;
//        7 s; fixed light; no BGM (same engine SEs)
//     23 Virbank -> Castelia ferry, first trip (0904.s with Hugh): demo 26, then the ferry arriving under Castelia's
//        skyscrapers (a Unova landmark: not used)
//     26 Virbank -> Castelia ferry (0904.s): the ferry (two funnels) crossing the open sea toward the camera, sky and
//        water only, no land; 8 s; sky follows the time of day; its own BGM SEQ_BGM_SW_DEMO_SHIP + engine/wave SEs
//     13 Plasma Frigate takes off (Plasma's flying ship), 3 Nimbasa Ferris wheel (Nate/Rosa with a partner, Nimbasa
//        around), 5 the opening, 6/7 the ending, 8/9 Dragonspiral, 11/12 Black/White Kyurem, 14/15 Opelucid frozen,
//        16-22 Giant Chasm, 24/25 Mistralton's cargo plane, 1 (no script plays it; not seen), 0 empty: no boats.
//   Black 2 plays one demo per trip, at the departure, on a closed field: FadeOutBlackQ (+ BGMFadeOut 30 when the
//   demo has its own music), FadeWait, FieldClose, Call3DDemo, FieldOpen (the screen stays black), then
//   RTReserveScript + MapChangeCore; the destination's reserved script fades in (0904.s Script_3/4, 0072.s, 0074.s).
// - Chosen (the user: no Unova landmark may show in any trip; every trip's frames checked, screenshots/boats/):
//     Mr. Briney's small boat (Sapphire's white boat): demo 4, Black 2's white motorboat, WITHOUT Castelia's pier:
//       b2tools/patches/boat_demos.py hides the pier, its street lamps, flags and people in a/1/5/8 (same file sizes),
//       so the boat pulls away and speeds off on the open sea; Sapphire's boat music (h_play_briney_boat_music, a
//       stand-in) plays under the demo's engine sounds. The boarding (the real dock) and the landing are on the field.
//     the S.S. Tidal and the other ferries (Battle Tower, Southern Island, the event islands): demo 26 as it is, Black
//       2's ferry on the open sea (no land at all) with Black 2's ship music.
//   Not usable without the same kind of edit: demo 2 (a big liner, closer to the S.S. Tidal's size, but Castelia's
//   pier under a fixed sunset), demo 10 (the yellow boat at another Castelia pier), demo 23 (Castelia's skyline).
// - The lead's work/emu savestates made on another file layout cannot play a demo (black screen: the demo's files
//   are read through the state's file table); test from a cold-boot state of the ROM under test.
#ifndef COMMON_BOAT_INC
#define COMMON_BOAT_INC

#define BOAT_DEMO_BRINEY 4              /* Mr. Briney's boat: Black 2's Unity Tower motorboat (pier hidden: boat_demos) */
#define BOAT_DEMO_FERRY 26              /* S.S. Tidal and the ferries: Black 2's Virbank ferry at sea */

// the ride: the field fades out and closes, Black 2's demo plays, the field opens again on a black screen (the
// caller then changes the map; its arrival script fades in). own_bgm 1 = the demo plays its own music (Black 2 fades
// the field's out first), 0 = whatever plays now goes on under the demo's sounds
    .macro boat_ride demo, own_bgm
    FadeOutBlackQ
    .if \own_bgm
    BGMFadeOut 30
    .endif
    FadeWait
    FieldClose
    Call3DDemo \demo, 0
    FieldOpen
    .endm

// a whole trip after the boarding: the ride, then the map change; script = the destination zone's arrival script,
// reserved after FieldOpen as Black 2 does (it starts on the black screen: begin it with FadeInBlack, ch2_land)
    .macro boat_trip demo, own_bgm, zone, x, z, dir, script
    boat_ride \demo, \own_bgm
    RTReserveScript \script
    MapChangeCore \zone, \x, 0, \z, \dir
    .endm

// The cable car (Route 112 <-> Mt. Chimney, ch5's station rooms 1110 / 0680): Black 2 has no cable car, lift or gondola
// ride: no demo (the list above; its only gondola is demo 3, the Nimbasa Ferris wheel seen from inside the cabin with
// Nate/Rosa and a talking partner, Nimbasa around) and no field effect; its actors move in whole tiles on the ground and
// no script command moves a 3D model along a path, and our Route 112 has no cable between the stations (Sapphire draws
// the car and the cable only on the cable car screen, cable_car.c). A new demo (a car model, a mountain, a camera path in
// ov293's tables, new a/1/5/8 files) is a separate art job, so the ride stays ch5's: the screen fades to black, Black
// 2's elevator hum (SEQ_SE_FLD_23) plays for 3 s, then the map changes and the other station's arrival script fades in.
    .macro cable_car_ride zone, x, z, dir, script
    FadeOutBlack
    FadeWait
    SEPlay SEQ_SE_FLD_23
    h_goto_if_hoenn_music .Lcc_hoenn\@          // Hoenn music: Sapphire's cable car song (cable_car.c) over a
    VMSleep 90                                  // longer ride (5 s); the arrival zone's song follows
    VMJump .Lcc_go\@
.Lcc_hoenn\@:
    BGMPlay MUS_HOENN_CABLE_CAR
    VMSleep 300
.Lcc_go\@:
    SEStop
    RTReserveScript \script
    MapChangeCore \zone, \x, 0, \z, \dir
    .endm
#endif
