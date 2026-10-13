// Route 111's Mirage Tower, EMERALD ONLY (emerald_ch9_mirage 2026-10-12, builder B6; pokeemerald data/maps/Route111/scripts.inc, src/mirage_tower.c).
// Included by scenes/Route111.inc under #ifdef HOENN_EMERALD (body part): R111_EmMirage is called by the zone init (R111_Init), R111_EmCollapse
// (script 15) is the map-script condition VAR_MIRAGE_TOWER_STATE 1 (scenes/Route111_init.inc), R111_EmRedraw (script 16) is the seam trigger below.
// Text: src/text/scenes/emerald/Route111.txt lines 37-38 (converter/gen_emerald_ch9_text.py).
// Emerald: SetMirageTowerVisibility on every entry of the map: never once VAR_MIRAGE_TOWER_STATE is set; always once FLAG_FORCE_MIRAGE_TOWER_VISIBLE
// is (the tower's 1F sets it; Route 112's zone init clears it); else Random() & 1. Not visible = LAYOUT_ROUTE111_NO_MIRAGE_TOWER (the plain sand).
// Here: the tower is part of the world matrix's cells (a stand-in rock mound with a door, data/emerald/hoenn_world.json alt_layouts Route111), and
// the plain-sand cells are Black 2 map replace event 0 (R111M_EVENT; work 0x4031 == 0x1220, no other user). The zone init decides, sets FLAG_MIRAGE_TOWER_VISIBLE
// (pokeemerald's own flag), the event (MapReplaceSetEvent with reload: the matrix the cells are loaded from) and parks the door while the tower is hidden
// (ObjInitWarpGPos: no warp on a sand tile). Cells already drawn keep their picture until they are loaded again: the tower is 18 tiles from Route 112's
// seam, so a walk in from Route 112 can have the tower's cell on screen already (stale picture for that visit: a tower with no door, or a hidden door).
// R111_EmRedraw (script 16) is the cure, as Route 130's Mirage Island: fade out, reload the field from the new matrix, fade in; it runs from a trigger on
// work 0x4004 == 1 that is NOT placed yet (a 2 x 60 trigger along Route 111's x 0-1, z 20-79 in data/story/emerald/e_ch9_mirage.json; untested: add it if
// the stale tower shows). Entering from the north,
// the south or by a warp needs nothing: the tower's cell is not loaded yet or the field is not built yet.
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
#define R111M_REDRAW 0x4004             // map-local: 1 = the cells on screen are not the matrix's (the seam trigger fires)
#define R111M_WANT 0x4005               // map-local: 1 = the zone init wanted the tower gone
#define R111M_FOSSIL 190                // uid of the fossil that falls and sinks (data/story/emerald/e_ch9_mirage.json)
#define R111M_T_ClawGone 37             // Route111_Text_ClawFossilDisappeared
#define R111M_T_RootGone 38             // Route111_Text_RootFossilDisappeared

R111_EmMirage:                          // Route111_OnTransition: SetMirageTowerVisibility, the layout, SetMirageTowerGone
    h_goto_if_ne VAR_MIRAGE_TOWER_STATE, 2, L_R111M_StateOk
    h_setvar VAR_MIRAGE_TOWER_STATE, 3                    // Route111_EventScript_SetMirageTowerGone: the collapse is over for good
L_R111M_StateOk:
    h_goto_if_ne VAR_MIRAGE_TOWER_STATE, 0, L_R111M_NotVisible   // done: hidden (state 1: shown below, for the scene)
    h_goto_if_set FLAG_FORCE_MIRAGE_TOWER_VISIBLE, L_R111M_Visible
    h_random R111M_TMP, 2                                 // visible = Random() & 1
    h_goto_if_eq R111M_TMP, 1, L_R111M_Visible
L_R111M_NotVisible:
    h_clearflag FLAG_MIRAGE_TOWER_VISIBLE
    WorkSetConst R111M_TMP, 1                             // the layout without the tower
    h_goto_if_ne VAR_MIRAGE_TOWER_STATE, 1, L_R111M_Layout
    WorkSetConst R111M_TMP, 0                             // (state 1: ShowTemporaryMirageTower: the tower is drawn for the scene)
    VMJump L_R111M_Layout
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
