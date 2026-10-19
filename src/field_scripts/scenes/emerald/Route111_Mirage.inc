// Route 111's Mirage Tower, EMERALD ONLY (emerald_ch9_mirage 2026-10-12, builder B6; pokeemerald data/maps/Route111/scripts.inc, src/mirage_tower.c).
// Included by scenes/Route111.inc under #ifdef HOENN_EMERALD (body part): R111_EmMirage is called by the zone init (R111_Init), R111_EmCollapse
// (script 15) is the map-script condition VAR_MIRAGE_TOWER_STATE 1 (scenes/Route111_init.inc), R111_EmRedraw (script 16) is the seam trigger below.
// Text: src/text/scenes/emerald/Route111.txt lines 37-38 (converter/gen_emerald_ch9_text.py).
// Emerald: SetMirageTowerVisibility on every entry of the map: never once VAR_MIRAGE_TOWER_STATE is set; always once FLAG_FORCE_MIRAGE_TOWER_VISIBLE
// is (the tower's 1F sets it; Route 112's zone init clears it); else Random() & 1. Not visible = LAYOUT_ROUTE111_NO_MIRAGE_TOWER (the plain sand).
// Here: the tower is part of the world matrix's cells (a stand-in rock mound with a door, data/emerald/hoenn_world.json alt_layouts Route111), and
// the plain-sand cells are Black 2 map replace event 0 (R111M_EVENT; work 0x4031 == 0x1220, no other user). The zone init decides, sets FLAG_MIRAGE_TOWER_VISIBLE
// (pokeemerald's own flag), the event (MapReplaceSetEvent with reload: the matrix the cells are loaded from) and parks the door while the tower is hidden
// (ObjInitWarpGPos: no warp on a sand tile). Cells already drawn keep their picture until they are loaded again (Black 2's ov036 field_g3d_mapper.c
// keeps a loaded chunk while its matrix cell stays in the 2x2 window; MapReplaceSetEvent's reload only re-reads the matrix ids), and a SEAMLESS zone
// change runs the zone init with the field up (ov036 Field_SwapZoneByMatrix -> FieldScript_CallOnZoneInit). Route 112's seam (world x 247/248, z 88-91)
// already has the tower's cell (8,3) loaded (x >= 240: columns 7-8; z >= 80: rows 2-3), so a new roll there showed the old picture for the visit: a
// tower with its door parked, or plain sand with the door warp working on an invisible door (reproduced 2026-10-18 in DeSmuME: cell (8,3) still the
// tower's chunk after the roll said "gone"; work/agents/emerald_fidelity/tests/mirage.py reads the loaded chunks).
// The same happened inside Route 111: its desert is Black 2 zone 610 (fixed_weather's sandstorm part, a copy of zone 370's header and init), so
// every step between the north part and the desert (world z 93-106, the tower's cell loaded) rolled again. Emerald has one map there: no roll.
// FIX (2026-10-18, no redraw): this zone init KEEPS the tower as its cells are drawn (visible = map replace event 0 clear), instead of rolling,
//  - always in the desert part (zone 610, RTGetZoneID), which also sets FLAG_EM_MIRAGE_TOWER_KEEP so the next step back into zone 370 keeps;
//  - in zone 370 when FLAG_EM_MIRAGE_TOWER_KEEP is set: by the desert part, or by Route 112's zone init (the seam); it is cleared here and by
//    Mauville's zone init.
// It rolls as Emerald on the other entries, where the tower's cell is not drawn yet: from Route 113 (rows 1-2 loaded), from Mauville, by a warp
// into zone 370 (the field is not built yet). Differences from Emerald: a walk in from Route 112 (Emerald rolls, but its 15x10-tile screen never
// shows the tower from the seam) and the doors that lead into the desert part (the Desert Ruins; the Mirage Tower's own door shows it anyway:
// FLAG_FORCE_MIRAGE_TOWER_VISIBLE) keep the tower as it was. A fade + field rebuild (R111_EmRedraw below) is the melonDS-risky kind
// (notes/RESUME.md item 8): it stays unused, no trigger runs it.
// The collapse (pokeemerald Route111_EventScript_MirageTowerDisappear + the tower's 4F script): after the fossil is taken the tower's 4F warps you to the
// foot of the tower with VAR_MIRAGE_TOWER_STATE 1; this zone shows it once more (the zone init at state 1), the scene shakes the camera, flashes white, swaps
// in the plain sand (the disintegration), makes the other fossil fall from the top and sink (Sapphire's sinking blink), sets state 2 (-> 3 on the next entry:
// gone for good), shows the Desert Underpass's fossil and says which fossil disappeared.
// Black 2 gaps: pokeemerald's shimmering pulse of the tower's colors, the falling player sprite and the pixel disintegration are not built (a camera shake and
// one white flash take their place); the player stays visible at the tower's foot.
#define R111M_EVENT 0                   // map replace event 0 (work 0x4031 == 0x1220): Route 111 without the Mirage Tower
#define R111M_TOWER_WARP 6              // the tower's door warp in Route 111's zone (MirageTower_1F's warp 0 leads back to "Route111 3" = zone 370 warp 6)
#define R111M_TMP 0x8050                // scratch works
#define R111M_B 0x8051
#define R111M_KEEP 0x8052               // 1 = keep the tower as drawn (FLAG_EM_MIRAGE_TOWER_KEEP was set, or the desert part)
#define R111M_DESERT_ZONE 610           // Route 111's desert: a part zone with its own weather (data/hoenn_weather.json "Route111_Desert",
                                        // b2tools/patches/fixed_weather.py): a copy of zone 370's header, so this zone init runs on every
                                        // step across its edge too
#define R111M_REDRAW 0x4004             // map-local: 1 = the cells on screen are not the matrix's (the seam trigger fires)
#define R111M_WANT 0x4005               // map-local: 1 = the zone init wanted the tower gone
#define R111M_FOSSIL 190                // uid of the fossil that falls and sinks (data/story/emerald/e_ch9_mirage.json)
#define R111M_T_ClawGone 37             // Route111_Text_ClawFossilDisappeared
#define R111M_T_RootGone 38             // Route111_Text_RootFossilDisappeared

R111_EmMirage:                          // Route111_OnTransition: SetMirageTowerVisibility, the layout, SetMirageTowerGone
    WorkSetConst R111M_KEEP, 0
    RTGetZoneID R111M_TMP
    WorkCmpConst R111M_TMP, R111M_DESERT_ZONE
    VMJumpIf CMP_NE, L_R111M_MainZone
    WorkSetConst R111M_KEEP, 1                            // the desert part: never a roll (one map in Emerald: no OnTransition)
    h_setflag FLAG_EM_MIRAGE_TOWER_KEEP                   // and a walk out of it into zone 370 keeps too
    VMJump L_R111M_KeepRead
L_R111M_MainZone:                                         // zone 370: a walk in from Route 112 or from the desert part keeps
    h_goto_if_unset FLAG_EM_MIRAGE_TOWER_KEEP, L_R111M_KeepRead
    WorkSetConst R111M_KEEP, 1
    h_clearflag FLAG_EM_MIRAGE_TOWER_KEEP
L_R111M_KeepRead:
    h_goto_if_ne VAR_MIRAGE_TOWER_STATE, 2, L_R111M_StateOk
    h_setvar VAR_MIRAGE_TOWER_STATE, 3                    // Route111_EventScript_SetMirageTowerGone: the collapse is over for good
L_R111M_StateOk:
    h_goto_if_ne VAR_MIRAGE_TOWER_STATE, 0, L_R111M_NotVisible   // done: hidden (state 1: shown below, for the scene)
    h_goto_if_eq R111M_KEEP, 1, L_R111M_Keep
    h_goto_if_set FLAG_FORCE_MIRAGE_TOWER_VISIBLE, L_R111M_Visible
    h_random R111M_TMP, 2                                 // visible = Random() & 1
    h_goto_if_eq R111M_TMP, 1, L_R111M_Visible
L_R111M_NotVisible:
    h_clearflag FLAG_MIRAGE_TOWER_VISIBLE
    WorkSetConst R111M_TMP, 1                             // the layout without the tower
    h_goto_if_ne VAR_MIRAGE_TOWER_STATE, 1, L_R111M_Layout
    WorkSetConst R111M_TMP, 0                             // (state 1: ShowTemporaryMirageTower: the tower is drawn for the scene)
    VMJump L_R111M_Layout
L_R111M_Keep:                                             // as drawn: visible = map replace event 0 clear
    MapReplaceIsEventSet R111M_EVENT, R111M_B
    h_goto_if_ne R111M_B, 0, L_R111M_NotVisible
L_R111M_Visible:
    h_setflag FLAG_MIRAGE_TOWER_VISIBLE
    WorkSetConst R111M_TMP, 0
L_R111M_Layout:
    WorkSet R111M_WANT, R111M_TMP
    MapReplaceIsEventSet R111M_EVENT, R111M_B
    WorkCmpWork R111M_B, R111M_TMP
    VMJumpIf CMP_EQ, L_R111M_Parked                       // already as it should be
    WorkSetConst R111M_REDRAW, 1                          // (only the seam trigger acts on this)
    h_goto_if_eq R111M_TMP, 0, L_R111M_EventOff
    MapReplaceSetEvent R111M_EVENT, 1, 1                  // the matrix is reloaded now: cells drawn from here on come without the tower
    VMJump L_R111M_Parked
L_R111M_EventOff:
    MapReplaceSetEvent R111M_EVENT, 0, 1
L_R111M_Parked:
    h_goto_if_set FLAG_MIRAGE_TOWER_VISIBLE, L_R111M_Done
    ObjInitWarpGPos R111M_TOWER_WARP, 0, 0, 0             // no door where the tower is not (as Jagged Pass's hideout door)
L_R111M_Done:
    VMReturn

R111_EmRedraw:                          // the seam trigger: the zone init changed the matrix after the cells were drawn (a walk in from Route 112)
    h_lock
    FadeOutBlackQ
    FadeWait
    h_goto_if_eq R111M_WANT, 0, L_R111M_RedrawShow
    MapReplaceSetEvent R111M_EVENT, 1, 1
    VMJump L_R111M_Redrawn
L_R111M_RedrawShow:
    MapReplaceSetEvent R111M_EVENT, 0, 1
L_R111M_Redrawn:
    WorkSetConst R111M_REDRAW, 0
    FieldClose
    FieldOpen
    FadeInBlackQ
    FadeWait
    h_release

R111_EmCollapse:                        // Route111_EventScript_MirageTowerDisappear (lockall; VAR_MIRAGE_TOWER_STATE 1)
    h_lock
    SEPlay SEQ_SE_FLD_126               // special StartMirageTowerShake: the tower quakes [guess: Black 2's ground rumble]
    EvCameraShake 4, 0, 3, 16, 1, 0, 1, 4
    VMSleep 36
    h_delay 24
    SEPlay SEQ_SE_FLD_33                // playse SE_FALL [guess]
    h_delay 16
    h_applymovement 255, Common_Movement_WalkInPlaceFastestUp      // turnobject PLAYER, DIR_NORTH
    h_waitmovement
    h_delay 16
    FadeOutWhiteQ                       // special StartMirageTowerDisintegration: the tower crumbles away: one white flash, then the plain sand
    FadeWait
    MapReplaceSetEvent R111M_EVENT, 1, 1
    FieldClose
    FieldOpen
    FadeInWhiteQ
    FadeWait
    h_addobject R111M_FOSSIL, FLAG_HIDE_ROUTE_111_DESERT_FOSSIL   // special StartMirageTowerFossilFallAndSink: the other fossil falls from the top and sinks
    h_applymovement R111M_FOSSIL, Mv_R111M_FossilFall
    h_waitmovement
    h_applymovement R111M_FOSSIL, Mv_R111_FossilSinks              // (Sapphire's sinking blink)
    h_waitmovement
    h_removeobject R111M_FOSSIL, FLAG_HIDE_ROUTE_111_DESERT_FOSSIL
    h_setvar VAR_MIRAGE_TOWER_STATE, 2
    h_clearflag FLAG_HIDE_DESERT_UNDERPASS_FOSSIL    // the fossil you did not take is waiting in the Desert Underpass
    h_goto_if_set FLAG_CHOSE_CLAW_FOSSIL, L_R111M_RootGone
    h_msgbox_info R111M_T_ClawGone      // The Claw Fossil disappeared into the sand...
    h_closemessage
    h_release
L_R111M_RootGone:
    h_msgbox_info R111M_T_RootGone      // The Root Fossil disappeared into the sand...
    h_closemessage
    h_release

    .balign 4, 0
Mv_R111M_FossilFall:                    // the fossil drops from the tower's top (20,53) to the sand (20,58)
    walk_fast_down 5
    step_end
    .balign 4, 0
