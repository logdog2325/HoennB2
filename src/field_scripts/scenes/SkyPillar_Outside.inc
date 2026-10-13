// Sky Pillar's outside (pokeemerald data/maps/SkyPillar_Outside/scripts.inc): Pokémon Emerald NDS only (emerald_ch10,
// 2026-10-12); Sapphire and Ruby have no story here (no entry: converter/gen_map_content.py counts none for them). The
// Emerald run of the generator makes these scripts 1-3 of zone 98 (a warp-only map: its group's matrix, the map at (18,22)).
// Text: src/text/scenes/emerald/SkyPillar_Outside.txt. People / signs: data/story/emerald/e_ch10.json (Wallace uid 101 =
// 100 + local id 1, hidden by FLAG_HIDE_SKY_PILLAR_WALLACE until the Cave of Origin; the door sign (14,5)). Map scripts:
// scenes/SkyPillar_Outside_init.inc (zone init 1, the scene condition VAR_SOOTOPOLIS_CITY_STATE 3 = script 2).
// The door: Emerald draws it shut until FLAG_WALLACE_GOES_TO_SKY_PILLAR (OnLoad: setmetatile ... DoorOpen); here its warp
// (door slot 2 = 1 + pokeemerald warp 1) is moved off the map until then and a sign on the door tile says it is closed.
// The earthquakes are Black 2's camera shake; the weather turns abnormal (patches/emerald_mech.c, from state 4 here).
#ifdef SCENE_ENTRIES
#ifdef HOENN_EMERALD
    ScriptEntry SPO_Init                // 1: SkyPillar_Outside_OnTransition / _OnLoad (zone init)
    ScriptEntry SPO_WallaceScene        // 2: OnFrame VAR_SOOTOPOLIS_CITY_STATE 3 (SkyPillar_Outside_EventScript_WallaceScene)
    ScriptEntry SPO_ClosedDoor          // 3: the door (14,5) (SkyPillar_Outside_EventScript_ClosedDoor)
#endif
#else
#ifdef HOENN_EMERALD
#include "scenes/ch10_lib.inc"
#include "scenes/emerald/em_ch10_lib.inc"
#define T_OpenedDoorToSkyPillar 0
#define T_EarthquakeNotMomentToWaste 1
#define T_SituationGettingWorse 2
#define T_GotToGoBackForSootopolis 3
#define T_DoorIsClosed 4
#define SPO_WALLACE 101
#define SPO_WARP_DOOR 2
#define SPO_Z(z) (22+(z))               // pokeemerald tile -> tile of the warp-only map's own matrix (b2tools/world.py)

SPO_Init:                               // SkyPillar_Outside_OnLoad (the weather of OnTransition: patches/emerald_mech.c)
#ifdef HOENN_TEST_CH10
    VMCall Test_Ch10Start               // test builds only (scenes/ch10_test.inc)
#endif
    h_goto_if_set FLAG_WALLACE_GOES_TO_SKY_PILLAR, L_SPO_Open
    ObjInitWarpGPos SPO_WARP_DOOR, 0, 0, 0
L_SPO_Open:
    VMHalt

SPO_WallaceScene:                       // SkyPillar_Outside_EventScript_WallaceScene
    c10_lock
    PlayerGetGPos C10_A, C10_B          // (Emerald's player has stepped out of the cave mouth (17,13) onto (17,14) when the
    h_goto_if_ne C10_B, SPO_Z(13), L_SPO_Out   // scene starts; Black 2 leaves him on the door tile: one step down first)
    h_applymovement 255, Mv_SPO_StepOut
    h_waitmovement
L_SPO_Out:
    h_applymovement SPO_WALLACE, Mv_SPO_WallaceApproach
    h_waitmovement
    h_applymovement 255, Common_Movement_WalkInPlaceFastestLeft
    h_waitmovement
    h_msgbox_actor T_OpenedDoorToSkyPillar, SPO_WALLACE     // Wallace: Oh, my, I'm terribly sorry! ... let's be on our way!
    h_closemessage
    h_delay 30
    em_shake 4, 8                       // ShakeCamera 1, 1, 8 shakes, delay 3
    h_delay 40
    h_msgbox_actor T_EarthquakeNotMomentToWaste, SPO_WALLACE    // Wallace: It's an earthquake! ...
    h_closemessage
    h_applymovement 255, Mv_SPO_PlayerClimb
    h_applymovement SPO_WALLACE, Mv_SPO_WallaceClimb
    h_waitmovement
    em_shake 12, 20                     // ShakeCamera 1, 3, 20 shakes, delay 5
    h_delay 20
    h_applymovement SPO_WALLACE, Common_Movement_WalkInPlaceFastestLeft
    h_waitmovement
    h_delay 10
    h_applymovement SPO_WALLACE, Common_Movement_WalkInPlaceFastestRight
    h_waitmovement
    h_delay 20
    h_applymovement SPO_WALLACE, Common_Movement_WalkInPlaceFastestDown
    h_waitmovement
    h_delay 30
    h_msgbox_actor T_SituationGettingWorse, SPO_WALLACE     // Wallace: Hmm... The situation is getting worse...
    h_closemessage
    h_setflag FLAG_SYS_WEATHER_CTRL
    h_setvar VAR_SOOTOPOLIS_STATE, 4    // (pokeemerald sets VAR_SOOTOPOLIS_CITY_STATE 4 at the end: here first, so the
    em_weather_zone                     // weather rule of this place applies) setweather WEATHER_ABNORMAL, doweather
    h_delay 60                          // special WaitWeather
    h_delay 30
    h_msgbox_actor T_GotToGoBackForSootopolis, SPO_WALLACE  // Wallace: This isn't good... I've got to go back. ...
    h_closemessage
    SEPlay SE_EXIT
    FadeOutBlack                        // fadescreenswapbuffers FADE_TO_BLACK
    FadeWait
    h_removeobject SPO_WALLACE, FLAG_HIDE_SKY_PILLAR_WALLACE
    h_clearflag FLAG_HIDE_WALLACE_SOOTOPOLIS       // FLAG_HIDE_SOOTOPOLIS_CITY_WALLACE
    FadeInBlack
    FadeWait
    h_release

SPO_ClosedDoor:                         // SkyPillar_Outside_EventScript_ClosedDoor (MSGBOX_SIGN)
    c10_lock
    h_goto_if_set FLAG_WALLACE_GOES_TO_SKY_PILLAR, L_SPO_DoorOpen
    h_msgbox_info T_DoorIsClosed        // The door is closed.
    h_closemessage
L_SPO_DoorOpen:
    h_release

    .balign 4, 0
Mv_SPO_StepOut:
    walk_down
    step_end
    .balign 4, 0
Mv_SPO_WallaceApproach:                 // SkyPillar_Outside_Movement_WallaceApproachPlayer
    walk_down 7
    walk_right 3
    step_end
    .balign 4, 0
Mv_SPO_WallaceClimb:                    // SkyPillar_Outside_Movement_WallaceClimbSkyPillar
    walk_left 3
    walk_up 4
    walk_right
    walk_up 4
    step_end
    .balign 4, 0
Mv_SPO_PlayerClimb:                     // SkyPillar_Outside_Movement_PlayerClimbSkyPillar
    walk_left 4
    walk_up 4
    walk_right
    walk_up 3
    step_end

#include "common/movement.inc"
#ifdef HOENN_TEST_CH10
#include "scenes/ch10_test.inc"
#endif
#endif
#endif
