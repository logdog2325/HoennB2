// Jagged Pass's story, EMERALD ONLY (emerald_ch45_magma 2026-10-12; pokeemerald data/maps/JaggedPass/scripts.inc; chapter Ch5 +
// Ch8). Sapphire and Ruby have no scene here (every line is under #ifdef HOENN_EMERALD, so their ScriptEntry list stays empty and
// converter/gen_map_content.py leaves 0036_auto_JaggedPass.s without an include there). converter/gen_map_content.py (Emerald run)
// includes this file twice in src/field_scripts/emerald/0036_auto_JaggedPass.s: the entries below are scripts 1-3. Text:
// src/text/scenes/emerald/JaggedPass.txt (JP_T_*). People and triggers: data/story/emerald/e_ch5.json (uid 105 = the Magma guard,
// five triggers at VAR_JAGGED_PASS_STATE 1). Map scripts: scenes/JaggedPass_init.inc (zone init = script 1).
// The story: the guard stands in front of the cave mouth at (16,18) until you beat him (FLAG_BEAT_MAGMA_GRUNT_JAGGED_PASS); the
// mouth is sealed until you own the Magma Emblem (the old woman on Mt. Pyre's summit gives it: scenes/MtPyre_Summit.inc), then the
// next step on a trigger tile makes the boulder shake and opens it (VAR_JAGGED_PASS_STATE 0 -> 1 on entering with the Emblem ->
// 2). The door behind it is the Magma Hideout 1F (builder B4 / emerald_world): until that map exists nothing is behind the
// opening scene. The cave mouth (emerald_integrate 2026-10-12): pokeemerald's layout has it open at (16,17)-(16,18) and its
// OnLoad covers it with rock wall while the state is below 2; here the map's own layout is the sealed one
// (data/emerald/hoenn_map_additions.json LAYOUT_JAGGED_PASS) and the open one (LAYOUT_JAGGED_PASS_HIDEOUT_OPEN) swaps in while
// map replace event JP_EVENT is set (data/emerald/hoenn_world.json alt_layouts JaggedPass; b2tools/world.py group_alts: the
// warp-only map's own matrix). The door (16,18) -> MagmaHideout_1F is moved off the map until state 2 (JP_HIDEOUT_WARP, as
// scenes/LilycoveCity.inc does for the Aqua Hideout door); while the hideout is not built it is parked anyway.
#ifdef SCENE_ENTRIES
#ifdef HOENN_EMERALD
    ScriptEntry JP_Init                 // 1: JaggedPass_OnResume (zone init)
    ScriptEntry JP_Guard                // 2: object 5 (JaggedPass_EventScript_MagmaHideoutGuard)
    ScriptEntry JP_OpenHideout          // 3: triggers (13,15) (14,15) (21,15) (21,20) (22,20) VAR_JAGGED_PASS_STATE 1
    ScriptEntry JP_FadeIn               // 4: after Sub_JP_Redraw's map change (RTReserveScript)
#endif
#else
#ifdef HOENN_EMERALD
#include "hoenn_key_items.h"
#include "hoenn_version.inc"             // ITEM_MAGMA_EMBLEM, TRAINER_GRUNT_JAGGED_PASS
#define JP_T_Boulder 0
#define JP_T_GruntIntro 1
#define JP_T_GoWherever 2
#define JP_GUARD 105                    // uid (100 + pokeemerald's object 5)
#define JP_SE_RUMBLE SEQ_SE_FLD_126     // [guess] Black 2's rumble (the Sealed Chamber's shaking)
#define JP_SE_THUD SEQ_SE_FLD_154       // [guess] SE_EFFECTIVE: Black 2's dull thud of its cave scenes
#define JP_HIDEOUT_WARP 6               // the hideout door's warp: zone 18's 2 Black 2 warps, then world.json's doors 0-3 (Route 112,
                                        // Mt. Chimney) and door 4 = pokeemerald warp 4 (16,18) (patches/hoenn_world.py order)
#define JP_EVENT 1                      // map replace event 1 (work 0x4032 == 0x224): the open mouth (alt_layouts JaggedPass)
#define JP_ZONE 18
#define JP_X(x) ((x) + 17)              // zone tiles = map tiles + the group's origin (work/world_emerald world.json
#define JP_Z(z) ((z) + 12)              // standalone JaggedPass origins [17, 12])
#define JP_PX 0x8050                    // scratch works of Sub_JP_Redraw (0478_room_MauvilleCity_Gym.s's Sub_MG_Redraw uses them so)
#define JP_PZ 0x8051
#define JP_DIR 0x8052

#ifdef HOENN_TEST_CH5
#include "scenes/ch5_test.inc"          // test builds only: the chapter's start state (a party)
#endif
#ifdef HOENN_TEST_CH8B
#include "scenes/ch8b_test.inc"         // test builds only: Ch8b's start state (six badges, HM01-04, the Magma Emblem at stage 2): the Magma
#endif                                  // Hideout's 1F boulders need Strength (emerald_ch8_hideout 2026-10-12)
JP_Init:                                // JaggedPass_OnResume: owning the Magma Emblem makes the boulder ready to open
#ifdef HOENN_TEST_CH5
    VMCall Test_Ch5Start
#endif
#ifdef HOENN_TEST_CH8B
    VMCall Test_Ch8bStart
#endif
#ifdef HOENN_TEST_CH5_EMBLEM            // test builds only: the old woman's Emblem in the Bag
    ItemAdd ITEM_MAGMA_EMBLEM, 1, HLIB_TMP
    h_setflag FLAG_HIDE_JAGGED_PASS_MAGMA_GUARD
#endif
    h_goto_if_ne VAR_JAGGED_PASS_STATE, 0, L_JP_InitState
    h_checkitem ITEM_MAGMA_EMBLEM, 1, HLIB_TMP
    h_goto_if_ne HLIB_TMP, 1, L_JP_InitState
    h_setvar VAR_JAGGED_PASS_STATE, 1
L_JP_InitState:
    h_goto_if_ge VAR_JAGGED_PASS_STATE, 2, L_JP_InitOpen   // OnLoad: below state 2 the cave mouth is sealed (door off the map)
#ifdef JP_HIDEOUT_WARP
    ObjInitWarpGPos JP_HIDEOUT_WARP, 0, 0, 0
#endif
    VMHalt
L_JP_InitOpen:                          // the open layout (set by the scene; again here for a state reached otherwise: a
    MapReplaceIsEventSet JP_EVENT, 0x8000   // test kit), reloaded as Route 131's zone init does
    WorkCmpConst 0x8000, 1
    VMJumpIf CMP_EQ, L_JP_InitDone
    MapReplaceSetEvent JP_EVENT, 1, 1
L_JP_InitDone:
    VMHalt

JP_Guard:                               // JaggedPass_EventScript_MagmaHideoutGuard (lockall, no faceplayer first)
    h_lock
    h_goto_if_set FLAG_BEAT_MAGMA_GRUNT_JAGGED_PASS, L_JP_GuardDefeated
    h_applymovement JP_GUARD, Common_Movement_ExclamationMark   // the "!" plays its own sound
    h_waitmovement
    h_applymovement JP_GUARD, Common_Movement_Delay48
    h_waitmovement
    h_faceplayer                        // Common_Movement_FacePlayer
    h_msgbox JP_T_GruntIntro            // Wah! What are you doing here? What am I doing in a place like this? ...
    h_closemessage
    h_trainerbattle TRAINER_GRUNT_JAGGED_PASS   // trainerbattle_no_intro; the defeat line is the trainer's own
    h_setflag FLAG_BEAT_MAGMA_GRUNT_JAGGED_PASS
    h_turnobject JP_GUARD, 0            // Common_Movement_FaceOriginalDirection (FACE_UP)
    h_release
L_JP_GuardDefeated:                     // JaggedPass_EventScript_GuardDefeated
    h_faceplayer
    h_msgbox JP_T_GoWherever            // Okay, oh-kay! I admit it--you're strong! Don't worry about me. Go wherever you want!
    h_closemessage
    h_turnobject JP_GUARD, 0
    h_release

JP_OpenHideout:                         // JaggedPass_EventScript_OpenMagmaHideout (the five coord events)
    h_lock
    SEPlay JP_SE_RUMBLE
    EvCameraShake 3, 0, 4, 8, 1, 0, 1, 5    // setvar 8004 1 / 8005 1 / 8006 8 / 8007 5, special ShakeCamera
    VMSleep 20
    h_msgbox_info JP_T_Boulder          // Oh! This boulder is shaking in response to the Magma Emblem!
    h_closemessage
    SEPlay JP_SE_RUMBLE
    EvCameraShake 4, 0, 4, 16, 1, 0, 1, 3   // 16 shakes, delay 3
    VMSleep 24
    SEPlay JP_SE_THUD                   // playse SE_EFFECTIVE; setmetatile 16,17 / 16,18 = the cave entrance
    h_delay 30
    h_setvar VAR_JAGGED_PASS_STATE, 2
    MapReplaceSetEvent JP_EVENT, 1, 0   // the open layout; drawn by the map change below, which also runs JP_Init again
    VMCall Sub_JP_Redraw                // (state 2: the door stays a warp)
    h_release

// Black 2 draws a map replacement only when the matrix loads (0478_room_MauvilleCity_Gym.s Sub_MG_Redraw: a fade and a
// map change to the player's own tile and facing; MapChangeCore takes constants, so one per trigger tile)
    .macro JP_WARP_HERE x, z            // map tile; facing from JP_DIR (0 up, 1 down, 2 left, 3 right)
    RTReserveScript 4                   // JP_FadeIn on arrival
    h_goto_if_ne JP_DIR, 0, .Ljw1\@
    MapChangeCore JP_ZONE, JP_X(\x), 0, JP_Z(\z), 0
    VMReturn
.Ljw1\@:
    h_goto_if_ne JP_DIR, 1, .Ljw2\@
    MapChangeCore JP_ZONE, JP_X(\x), 0, JP_Z(\z), 1
    VMReturn
.Ljw2\@:
    h_goto_if_ne JP_DIR, 2, .Ljw3\@
    MapChangeCore JP_ZONE, JP_X(\x), 0, JP_Z(\z), 2
    VMReturn
.Ljw3\@:
    MapChangeCore JP_ZONE, JP_X(\x), 0, JP_Z(\z), 3
    VMReturn
    .endm

    .macro JP_IF_AT x, z, label
    WorkCmpConst JP_PX, JP_X(\x)
    VMJumpIf CMP_NE, .Lji\@
    h_goto_if_eq JP_PZ, JP_Z(\z), \label
.Lji\@:
    .endm

JP_FadeIn:
    FadeInBlack
    FadeWait
    VMHalt

Sub_JP_Redraw:
    PlayerGetGPos JP_PX, JP_PZ
    PlayerGetDir JP_DIR
    FadeOutBlack
    FadeWait
    JP_IF_AT 13, 15, L_JP_At0           // the five trigger tiles (data/story/emerald/e_ch5.json)
    JP_IF_AT 14, 15, L_JP_At1
    JP_IF_AT 21, 15, L_JP_At2
    JP_IF_AT 21, 20, L_JP_At3
    JP_IF_AT 22, 20, L_JP_At4
    FadeInBlack                         // elsewhere: the open mouth shows on the next visit
    FadeWait
    VMReturn
L_JP_At0:
    JP_WARP_HERE 13, 15
L_JP_At1:
    JP_WARP_HERE 14, 15
L_JP_At2:
    JP_WARP_HERE 21, 15
L_JP_At3:
    JP_WARP_HERE 21, 20
L_JP_At4:
    JP_WARP_HERE 22, 20
    .balign 4, 0
#include "common/movement.inc"
#endif
#endif
