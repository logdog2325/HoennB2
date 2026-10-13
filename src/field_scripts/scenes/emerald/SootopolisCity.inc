// Sootopolis City's story in Pokémon Emerald NDS (pokeemerald data/maps/SootopolisCity/scripts.inc; emerald_ch10, 2026-10-12).
// Included by scenes/SootopolisCity.inc in an Emerald build in place of Sapphire's scene: its ScriptEntry list (scripts
// 1-21 of the zone, the generated signs follow: the Emerald run of converter/gen_map_content.py) and its bodies. Text:
// src/text/scenes/emerald/SootopolisCity.txt (T_* below; work/agents/emerald_ch10/tools/gen_text.py writes it).
// People (data/story/emerald/e_ch10.json; uid = 100 + pokeemerald local id; Sapphire's eleven are skip_emerald): the zone's NPC
// list is exactly that file's order (no generated people here), so SE_IDX_* = local id - 1.
// Door slots of the zone (as Sapphire's: 0 Black 2's own, 1 + pokeemerald warp id): 1 Center, 2 Mart, 3 Gym, 4 Cave of
// Origin, 5-11 Houses 1-7, 12 the Lotad and Seedot house (Sapphire's House 8), 13 the Mystery Events House (closed: decision 5).
//
// VAR_SOOTOPOLIS_CITY_STATE (= this port's VAR_SOOTOPOLIS_STATE, Emerald's meaning): 0 before Kyogre wakes; 1 Seafloor
// Cavern's end (the legends arrive: scene on arrival); 2 after it; 3 Wallace goes to the Sky Pillar (Cave of Origin B1F);
// 4 Wallace back here (Sky Pillar outside); 5 Rayquaza woke (Sky Pillar top); 6 Juan beaten. VAR_SKY_PILLAR_STATE: 1 Rayquaza
// on its way (scene on arrival), 3 after it (pokeemerald's 2 = arrived by Dive, turned into 3 by OnWarp: one step here).
// Script_DoRayquazaScene is Emerald's own cutscene (src/include/em_rayquaza_scene.inc, emerald_art). Black 2 gaps: the
// camera object is Black 2's event camera (scenes/emerald/em_ch10_lib.inc); setmetatile door locks are
// door warps moved off the map (ObjInitWarpGPos) + a "The door is closed." sign on the door tile; setobjectmovementtype of
// the spectators needs actors (a zone init has none): they stand at Emerald's places with their own movement; the rough
// water patches under Groudon and Kyogre (SetRoughWater) are part of the legends' layout (map replace event SE_EVENT).
#ifdef SCENE_ENTRIES
    ScriptEntry SE_Init                 // 1: SootopolisCity_OnLoad + _OnTransition (zone init)
    ScriptEntry SE_Expert               // 2: object 1 (SootopolisCity_EventScript_CaveOfOriginExpert)
    ScriptEntry SE_Kiri                 // 3: object 3 (SootopolisCity_EventScript_Kiri)
    ScriptEntry SE_Woman2               // 4: object 2 (SootopolisCity_EventScript_Woman2)
    ScriptEntry SE_NinjaBoy             // 5: object 4 (SootopolisCity_EventScript_NinjaBoy)
    ScriptEntry SE_Boy1                 // 6: object 5 (SootopolisCity_EventScript_Boy1)
    ScriptEntry SE_Man                  // 7: object 6 (SootopolisCity_EventScript_Man)
    ScriptEntry SE_Steven               // 8: object 7 (SootopolisCity_EventScript_Steven)
    ScriptEntry SE_Woman1               // 9: object 8 (SootopolisCity_EventScript_Woman1)
    ScriptEntry SE_Maniac               // 10: object 12 (SootopolisCity_EventScript_Maniac)
    ScriptEntry SE_Girl                 // 11: object 13 (SootopolisCity_EventScript_Girl)
    ScriptEntry SE_BlackBelt            // 12: object 14 (SootopolisCity_EventScript_BlackBelt)
    ScriptEntry SE_Boy2                 // 13: object 15 (SootopolisCity_EventScript_Boy2)
    ScriptEntry SE_Maxie                // 14: object 16 (SootopolisCity_EventScript_Maxie)
    ScriptEntry SE_Archie               // 15: object 17 (SootopolisCity_EventScript_Archie)
    ScriptEntry SE_Wallace              // 16: object 18 (SootopolisCity_EventScript_Wallace)
    ScriptEntry SE_ClosedDoor           // 17: the houses' doors (EventScript_ClosedSootopolisDoor; data/story/emerald/e_ch10.json)
    ScriptEntry SE_ClosedGymDoor        // 18: the Gym's door until Archie and Maxie leave (SootopolisCity_EventScript_LockGymDoor)
    ScriptEntry SE_LegendsScene         // 19: OnFrame VAR_SOOTOPOLIS_CITY_STATE 1 (SootopolisCity_EventScript_StartLegendariesScene)
    ScriptEntry SE_RayquazaScene        // 20: OnFrame VAR_SKY_PILLAR_STATE 1 (SootopolisCity_EventScript_StartRayquazaScene)
    ScriptEntry SE_WhiteIn              // 21: the Rayquaza scene's white warp arrives (warpwhitefade)
#else
#include "scenes/ch10_lib.inc"
#include "scenes/emerald/em_ch10_lib.inc"
#include "hoenn_music.inc"
#include "em_rayquaza_scene.inc"           // em_rayquaza_scene (Emerald's Script_DoRayquazaScene, emerald_art)

#define VAR_SOOTOPOLIS_CITY_STATE VAR_SOOTOPOLIS_STATE      // pokeemerald's names of this port's ids
#define FLAG_KYOGRE_ESCAPED_SEAFLOOR_CAVERN FLAG_LEGEND_ESCAPED_SEAFLOOR_CAVERN
#define FLAG_HIDE_SOOTOPOLIS_CITY_STEVEN FLAG_HIDE_STEVEN_SOOTOPOLIS
#define FLAG_HIDE_SOOTOPOLIS_CITY_WALLACE FLAG_HIDE_WALLACE_SOOTOPOLIS
#define FLAG_HIDE_MT_PYRE_SUMMIT_ARCHIE FLAG_HIDE_LEADER_MT_PYRE_SUMMIT

#define T_CaveOfOriginPleaseLeave 0
#define T_LeadSuperiorTrainerToCave 1
#define T_CaveOfOriginSleepsToo 2
#define T_AwakenedPokemonClash 3
#define T_BigPokemonFighting 4
#define T_PrettyMonCameFromSky 5
#define T_NameIsKiriHaveOneOfThese 6
#define T_GiveYouThisBerryToo 7
#define T_WhatKindOfWishInYourName 8
#define T_LikeSeasonBornIn 9
#define T_OhDoesntMatter 10
#define T_ThenILoveAutumn 11
#define T_WeatherWentWild 12
#define T_YouBroughtFlyingMon 13
#define T_NoOrdinaryTourist 14
#define T_CityRegainedCalm 15
#define T_SootopolisSkyBeautiful 16
#define T_GiganticPokemonFight 17
#define T_NightSkyFavoriteScenery 18
#define T_FearedWorstWhenPokemonFlewDown 19
#define T_ThisIsWicked 20
#define T_WonderWhatWorldIsLike 21
#define T_ThatWasWicked 22
#define T_GiantPokemonSuddenlyAppeared 23
#define T_WhatIsThatGreenPokemon 24
#define T_WhereDidLegendariesGo 25
#define T_PhysicallyFitLivingHere 26
#define T_SoThatsRayquaza 27
#define T_KnowWhatsNeededToHelpHim 28
#define T_MaxieArchieLeft 29
#define T_NeverBeenToSkyPillar 30
#define T_InvolvedWithCrisisComeWithMe 31
#define T_DoesThisMakeYourFearPokemon 32
#define T_HereWereAreHelpWallace 33
#define T_TwoPokemonArentAngry 34
#define T_FlyingMonStoppedRampage 35
#define T_GoRedAndBlueMon 36
#define T_DoYouKnowMonNames 37
#define T_GreenOneSettlesThings 38
#define T_SootopolisWillBeWrecked 39
#define T_SootopolisDidntGetWrecked 40
#define T_SeeingLegendWithOwnEyes 41
#define T_SawLegendWithOwnEyes 42
#define T_HaventYouScaledSkyPillar 43
#define T_DazzledByMentor 44
#define T_AquaMagmaDidntMeanHarm 45
#define T_ThankYouForHelpAcceptThis 46
#define T_ExplainWaterfallGoToGym 47
#define T_GroudonPleaseStop 48
#define T_AfterAllOurScheming 49
#define T_KyogreCalmDown 50
#define T_TryingMeaninglessToPokemon 51
#define T_DoorIsClosed 52
#define T_BagFull 53

#define SC_X(x) (18+(x))                // pokeemerald tile -> tile of the standalone group's matrix (b2tools/world.py)
#define SC_Z(z) (21+(z))
#define SE_LAKE_Y (-8)                  // the lake's height (units), where the legends stand
#define SE_EVENT 1                      // map replace event of the legends' layout (LAYOUT_SOOTOPOLIS_CITY_LEGENDS_BATTLE):
                                        // shared with Jagged Pass (its zone init sets it at VAR_JAGGED_PASS_STATE 2, this one
                                        // sets / clears it on every entry: each zone's entries patch only its own matrix)
// zone NPC list indices (ObjInitNPCGPos) = pokeemerald local id - 1; uids = 100 + local id
#define SE_IDX_EXPERT 0
#define SE_IDX_KIRI 2
#define SE_IDX_NINJA_BOY 3
#define SE_IDX_BOY_1 4
#define SE_IDX_STEVEN 6
#define SE_IDX_WOMAN_1 7
#define SE_IDX_MAXIE 15
#define SE_IDX_ARCHIE 16
#define SE_IDX_WALLACE 17
#define SE_EXPERT 101
#define SE_WOMAN_2 102
#define SE_KIRI 103
#define SE_NINJA_BOY 104
#define SE_BOY_1 105
#define SE_STEVEN 107
#define SE_WOMAN_1 108
#define SE_GROUDON 109
#define SE_KYOGRE 110
#define SE_RAYQUAZA 111
#define SE_MANIAC 112
#define SE_GIRL 113
#define SE_BLACK_BELT 114
#define SE_BOY_2 115
#define SE_MAXIE 116
#define SE_ARCHIE 117
#define SE_WALLACE 118
#define SE_WARP_GYM 3                   // door slots (1 + pokeemerald warp id)
#define SE_WARP_HOUSE1 5                // Houses 1-7: 5-11, the Lotad and Seedot house: 12
#define SE_ZONE 319
#define SE_FADE_IN 21                   // SE_WhiteIn's script number (the reserved arrival script of the white warp)

SE_Init:                                // SootopolisCity_OnLoad + SootopolisCity_OnTransition
#ifdef HOENN_TEST_CH10
    VMCall Test_Ch10Start               // test builds only (scenes/ch10_test.inc; its Emerald stages: HOENN_TEST_CH10E)
#endif
    h_setflag FLAG_VISITED_SOOTOPOLIS_CITY
    // OnLoad: the Gym is shut until Archie and Maxie leave; the houses while the legends are here
    h_call_if_unset FLAG_SOOTOPOLIS_ARCHIE_MAXIE_LEAVE, Sub_SE_LockGymDoor
    h_goto_if_unset FLAG_KYOGRE_ESCAPED_SEAFLOOR_CAVERN, L_SE_Layout
    h_call_if_unset FLAG_SOOTOPOLIS_ARCHIE_MAXIE_LEAVE, Sub_SE_LockHouseDoors
L_SE_Layout:                            // SootopolisCity_EventScript_SetLayout (the weather of SetWeather: patches/emerald_mech.c)
    h_goto_if_eq VAR_SOOTOPOLIS_CITY_STATE, 0, L_SE_NormalLayout
    h_goto_if_ge VAR_SOOTOPOLIS_CITY_STATE, 6, L_SE_NormalLayout
    h_goto_if_le VAR_SOOTOPOLIS_CITY_STATE, 4, L_SE_LegendsLayout
    h_goto_if_le VAR_SKY_PILLAR_STATE, 1, L_SE_LegendsLayout
L_SE_NormalLayout:
    MapReplaceIsEventSet SE_EVENT, C10_A
    h_goto_if_eq C10_A, 0, L_SE_LayoutDone
    MapReplaceSetEvent SE_EVENT, 0, 1   // (the zone's matrix is already loaded: reload it, as Route 131's / Jagged Pass's)
    VMJump L_SE_LayoutDone
L_SE_LegendsLayout:                     // setmaplayoutindex LAYOUT_SOOTOPOLIS_CITY_LEGENDS_BATTLE
    MapReplaceIsEventSet SE_EVENT, C10_A
    h_goto_if_eq C10_A, 1, L_SE_LayoutDone
    MapReplaceSetEvent SE_EVENT, 1, 1
L_SE_LayoutDone:
    h_goto_if_eq VAR_SOOTOPOLIS_CITY_STATE, 0, L_SE_Objects
    h_goto_if_ge VAR_SOOTOPOLIS_CITY_STATE, 6, L_SE_Objects
    // SootopolisCity_EventScript_SetBattleSpectators (states 1-5)
    ObjInitNPCGPos SE_IDX_KIRI, 0, SC_X(13), 0, SC_Z(48)
    ObjInitNPCGPos SE_IDX_BOY_1, 2, SC_X(46), 0, SC_Z(32)
    ObjInitNPCGPos SE_IDX_NINJA_BOY, 2, SC_X(48), 0, SC_Z(41)
    ObjInitNPCGPos SE_IDX_WOMAN_1, 2, SC_X(45), 0, SC_Z(43)
L_SE_Objects:
    h_goto_if_eq VAR_SOOTOPOLIS_CITY_STATE, 2, L_SE_CheckGuide
    h_goto_if_eq VAR_SOOTOPOLIS_CITY_STATE, 3, L_SE_CheckGuide
    h_goto_if_eq VAR_SOOTOPOLIS_CITY_STATE, 4, L_SE_ExitCave
    h_goto_if_eq VAR_SOOTOPOLIS_CITY_STATE, 5, L_SE_OutsideGym
    VMHalt                              // (states 0 and 6: the expert at (31,18), his own place)
L_SE_CheckGuide:                        // SootopolisCity_EventScript_CheckSetEnterCaveOfOriginObjPos
    h_goto_if_unset FLAG_STEVEN_GUIDES_TO_CAVE_OF_ORIGIN, L_SE_InitDone
    ObjInitNPCGPos SE_IDX_EXPERT, 3, SC_X(30), 0, SC_Z(18)
    ObjInitNPCGPos SE_IDX_STEVEN, 2, SC_X(32), 0, SC_Z(18)
    VMHalt
L_SE_ExitCave:                          // SootopolisCity_EventScript_SetExitCaveOfOriginObjPos
    ObjInitNPCGPos SE_IDX_EXPERT, 3, SC_X(30), 0, SC_Z(18)
    ObjInitNPCGPos SE_IDX_WALLACE, 1, SC_X(31), 0, SC_Z(18)
    ObjInitNPCGPos SE_IDX_STEVEN, 2, SC_X(32), 0, SC_Z(18)
    VMHalt
L_SE_OutsideGym:                        // SootopolisCity_EventScript_SetOutsideGymObjPos
    ObjInitNPCGPos SE_IDX_EXPERT, 1, SC_X(31), 0, SC_Z(18)
    ObjInitNPCGPos SE_IDX_STEVEN, 1, SC_X(29), 0, SC_Z(33)
    ObjInitNPCGPos SE_IDX_MAXIE, 1, SC_X(33), 0, SC_Z(35)
    ObjInitNPCGPos SE_IDX_ARCHIE, 1, SC_X(34), 0, SC_Z(35)
    h_goto_if_eq VAR_SOOTOPOLIS_WALLACE_STATE, 1, L_SE_WallaceRight
    h_goto_if_eq VAR_SOOTOPOLIS_WALLACE_STATE, 2, L_SE_WallaceLeft
    ObjInitNPCGPos SE_IDX_WALLACE, 1, SC_X(31), 0, SC_Z(33)
    VMHalt
L_SE_WallaceRight:
    ObjInitNPCGPos SE_IDX_WALLACE, 1, SC_X(32), 0, SC_Z(33)
    VMHalt
L_SE_WallaceLeft:
    ObjInitNPCGPos SE_IDX_WALLACE, 1, SC_X(30), 0, SC_Z(33)
L_SE_InitDone:
    VMHalt

Sub_SE_LockGymDoor:                     // setmetatile 31, 32, METATILE_Sootopolis_GymDoor_Closed
    ObjInitWarpGPos SE_WARP_GYM, 0, 0, 0
    VMReturn
Sub_SE_LockHouseDoors:                  // the nine houses (the Mystery Events House is closed anyway)
    ObjInitWarpGPos SE_WARP_HOUSE1+0, 0, 0, 0
    ObjInitWarpGPos SE_WARP_HOUSE1+1, 0, 0, 0
    ObjInitWarpGPos SE_WARP_HOUSE1+2, 0, 0, 0
    ObjInitWarpGPos SE_WARP_HOUSE1+3, 0, 0, 0
    ObjInitWarpGPos SE_WARP_HOUSE1+4, 0, 0, 0
    ObjInitWarpGPos SE_WARP_HOUSE1+5, 0, 0, 0
    ObjInitWarpGPos SE_WARP_HOUSE1+6, 0, 0, 0
    ObjInitWarpGPos SE_WARP_HOUSE1+7, 0, 0, 0
    VMReturn

// ---- the legends arrive (state 1): the camera pans to the lake, the fight, back to the player --------------------
SE_LegendsScene:                        // SootopolisCity_EventScript_StartLegendariesScene (from the Pokémon Center door
    c10_lock                            // after Fly, else from the dive spot: the camera pans to the same place, the lake)
    h_delay 60
    em_camera_start
    VMCall Sub_SE_PanToLake
    h_delay 60
    FadeOutBlack                        // fadescreenspeed FADE_TO_BLACK, 8
    FadeWait
    h_setvar VAR_SOOTOPOLIS_CITY_STATE, 2   // (pokeemerald sets it at the end: here first, so the weather rule is the
    em_weather_zone 1                   // abnormal one) setweather WEATHER_ABNORMAL, doweather
    EvCameraRebind                      // (the field closes for the scene: the event camera ends here and starts again
    EvCameraEnd                         // after it, at the lake, where Emerald's view still is)
    em_rayquaza_scene 0                 // special Script_DoRayquazaScene, VAR_0x8004 FALSE: Groudon and Kyogre's fight
    em_camera_start
    em_camera_to SC_X(31), SC_Z(44), SE_LAKE_Y, 1
    FadeInBlack
    FadeWait
    h_applymovement SE_KYOGRE, Common_Movement_WalkInPlaceFastestLeft
    h_applymovement SE_GROUDON, Common_Movement_WalkInPlaceFastestRight
    h_waitmovement
    h_delay 60
    h_waitse
    h_playmoncry SPECIES_KYOGRE
    h_applymovement SE_KYOGRE, Mv_SE_KyogreAttack
    h_applymovement SE_GROUDON, Mv_SE_GroudonDefend
    h_waitmovement
    em_shake_at SC_X(31), SC_Z(44), SE_LAKE_Y, 8, 2     // ShakeCamera 1, 1, 8 shakes, delay 5
    h_applymovement SE_KYOGRE, Mv_SE_KyogreMoveBack
    h_applymovement SE_GROUDON, Mv_SE_GroudonMoveBack
    h_waitmovement
    h_waitse
    h_playmoncry SPECIES_GROUDON
    h_applymovement SE_KYOGRE, Mv_SE_KyogreDefend
    h_applymovement SE_GROUDON, Mv_SE_GroudonAttack
    h_waitmovement
    em_shake_at SC_X(31), SC_Z(44), SE_LAKE_Y, 8, 2     // ShakeCamera 1, 1, 8 shakes, delay 5
    h_applymovement SE_KYOGRE, Mv_SE_KyogreMoveBack
    h_applymovement SE_GROUDON, Mv_SE_GroudonMoveBack
    h_waitmovement
    h_waitse
    h_playmoncry SPECIES_KYOGRE
    h_applymovement SE_KYOGRE, Mv_SE_KyogreAttack
    h_applymovement SE_GROUDON, Mv_SE_GroudonDefend
    h_waitmovement
    em_shake_at SC_X(31), SC_Z(44), SE_LAKE_Y, 8, 2     // ShakeCamera 1, 1, 8 shakes, delay 5
    h_applymovement SE_KYOGRE, Mv_SE_KyogreMoveBack
    h_applymovement SE_GROUDON, Mv_SE_GroudonMoveBack
    h_waitmovement
    h_applymovement SE_KYOGRE, Mv_SE_KyogreIdle
    h_applymovement SE_GROUDON, Mv_SE_GroudonIdle
    VMCall Sub_SE_PanBack
    h_waitmovement
    h_release

Sub_SE_PanToLake:                       // _Movement_PanToActionFromPokeCenter (12 slow diagonal tiles) or _PanToActionFromDive
    PlayerGetGPos C10_A, C10_B          // (StorePlayerCoordsInVars: the Pokémon Center door (43,32) after Fly, else Dive)
    h_goto_if_ne C10_A, SC_X(43), L_SE_PanFromDive
    h_goto_if_ne C10_B, SC_Z(32), L_SE_PanFromDive
    em_camera_to SC_X(31), SC_Z(44), SE_LAKE_Y, 192
    VMReturn
L_SE_PanFromDive:
    em_camera_to SC_X(31), SC_Z(44), SE_LAKE_Y, 88
    VMReturn
Sub_SE_PanBack:                         // _Movement_PanBackToPokeCenter / _PanBackToDive, RemoveCameraObject
    h_goto_if_ne C10_A, SC_X(43), L_SE_PanBackDive
    h_goto_if_ne C10_B, SC_Z(32), L_SE_PanBackDive
    em_camera_back SC_X(43), SC_Z(32), 32, 192
    VMReturn
L_SE_PanBackDive:
    em_camera_end 88
    VMReturn

// ---- Rayquaza ends the fight (VAR_SKY_PILLAR_STATE 1, the player back from the Sky Pillar) ------------------------
SE_RayquazaScene:                       // SootopolisCity_EventScript_StartRayquazaScene
    c10_lock
    h_delay 60
    em_camera_start
    VMCall Sub_SE_PanToLake
    h_delay 60
    FadeOutBlack
    FadeWait
    h_removeobject SE_GROUDON, FLAG_HIDE_SOOTOPOLIS_CITY_GROUDON    // (SetRoughWater: the legends' layout has it)
    h_removeobject SE_KYOGRE, FLAG_HIDE_SOOTOPOLIS_CITY_KYOGRE
    h_addobject SE_RAYQUAZA, FLAG_HIDE_SOOTOPOLIS_CITY_RAYQUAZA
    EvCameraRebind                      // (as in SE_LegendsScene: the camera again at the lake after the scene)
    EvCameraEnd
    em_rayquaza_scene 1                 // special Script_DoRayquazaScene, VAR_0x8004 TRUE: the fight, Rayquaza comes
                                        // down and chases them away (the scene plays mus_rayquaza_appears itself)
    em_camera_start
    em_camera_to SC_X(31), SC_Z(44), SE_LAKE_Y, 1
    FadeInBlack
    FadeWait
    h_goto_if_ne C10_A, SC_X(43), L_SE_RayFromDive
    h_goto_if_ne C10_B, SC_Z(32), L_SE_RayFromDive
    em_camera_to SC_X(31), SC_Z(40), SE_LAKE_Y, 32     // _Movement_PanUp (4 tiles)
    VMJump L_SE_RayCries
L_SE_RayFromDive:
    h_applymovement 255, Mv_SE_PlayerApproach   // _PlayerApproachLegendaries, with the camera going up
    em_camera_to SC_X(31), SC_Z(40), SE_LAKE_Y, 32
    h_waitmovement
L_SE_RayCries:
    h_waitse
    h_playmoncry SPECIES_RAYQUAZA
    em_shake_at SC_X(31), SC_Z(40), SE_LAKE_Y, 8, 2    // ShakeCamera 1, 1, 8 shakes, delay 3
    h_waitse
    h_playmoncry SPECIES_RAYQUAZA
    em_shake_at SC_X(31), SC_Z(40), SE_LAKE_Y, 8, 4    // ShakeCamera 1, 2, 8 shakes, delay 5
    h_waitmoncry
    em_weather_none                     // setweather WEATHER_NONE, doweather
    h_applymovement SE_RAYQUAZA, Mv_SE_RayquazaFlyOff
    h_waitmovement
    h_removeobject SE_RAYQUAZA, FLAG_HIDE_SOOTOPOLIS_CITY_RAYQUAZA
    h_delay 30                          // (special WaitWeather)
    h_clearflag FLAG_SYS_WEATHER_CTRL
    h_setvar VAR_SKY_PILLAR_STATE, 3
    h_clearflag FLAG_LEGENDARIES_IN_SOOTOPOLIS
    h_setflag FLAG_LEGENDARY_BATTLE_COMPLETED   // (this port's "the crisis is over" flag: the shared Mart / Center lines,
    BGMChangeMap                        // pokeemerald's VAR_SKY_PILLAR_STATE >= 2) fadenewbgm MUS_SOOTOPOLIS / MUS_SURF
    h_delay 120
    EvCameraRebind
    EvCameraEnd
    FadeOutWhite                        // warpwhitefade MAP_SOOTOPOLIS_CITY, 43, 32 (from Dive: 29, 53)
    RTReserveScript SE_FADE_IN
    FadeWait
    h_goto_if_ne C10_A, SC_X(43), L_SE_RayWarpDive
    h_goto_if_ne C10_B, SC_Z(32), L_SE_RayWarpDive
    MapChangeCore SE_ZONE, SC_X(43), 0, SC_Z(32), 0     // (OnWarp: the player faces the lake)
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt
L_SE_RayWarpDive:
    MapChangeCore SE_ZONE, SC_X(29), 0, SC_Z(53), 0
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt
SE_WhiteIn:                             // (the white warp's arrival: a scripted map change waits for the caller's fade-in)
    FadeInWhite
    FadeWait
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

// ---- the Cave of Origin's keeper ----------------------------------------------------------------------------------
SE_Expert:                              // SootopolisCity_EventScript_CaveOfOriginExpert
    c10_talk
    h_goto_if_ge VAR_SOOTOPOLIS_CITY_STATE, 6, L_SE_ExpertAfter
    h_goto_if_eq VAR_SOOTOPOLIS_CITY_STATE, 5, L_SE_ExpertLegends
    h_goto_if_ge VAR_SOOTOPOLIS_CITY_STATE, 2, L_SE_ExpertLead
    h_msgbox T_CaveOfOriginPleaseLeave
    h_release
L_SE_ExpertLead:
    h_msgbox T_LeadSuperiorTrainerToCave
    h_release
L_SE_ExpertAfter:
    h_msgbox T_CaveOfOriginSleepsToo
    h_release
L_SE_ExpertLegends:
    h_msgbox T_AwakenedPokemonClash
    h_release

// ---- Kiri: two Berries a day (and a spectator during the fight) --------------------------------------------------
SE_Kiri:                                // SootopolisCity_EventScript_Kiri
    c10_talk
    h_goto_if_le VAR_SOOTOPOLIS_CITY_STATE, 1, L_SE_KiriBerry
    h_goto_if_ge VAR_SOOTOPOLIS_CITY_STATE, 6, L_SE_KiriBerry
    h_goto_if_eq VAR_SOOTOPOLIS_CITY_STATE, 5, L_SE_KiriRayquaza
    h_msgbox T_BigPokemonFighting
    h_closemessage
    h_turnobject SE_KIRI, 0             // Common_Movement_FaceOriginalDirection (she watches the lake)
    h_release
L_SE_KiriRayquaza:
    h_msgbox T_PrettyMonCameFromSky
    h_release
L_SE_KiriBerry:                         // SootopolisCity_EventScript_KiriGiveBerry (dotimebasedevents: Black 2 resets the
    h_goto_if_set FLAG_DAILY_RECEIVED_BERRY_SOOTOPOLIS, L_SE_KiriReceived   // daily flag at midnight)
    h_msgbox T_NameIsKiriHaveOneOfThese
    h_closemessage
    h_random C10_A, 10                  // NUM_KIRI_BERRIES, + NUM_KIRI_BERRIES_SKIPPED + FIRST_BERRY_INDEX
    h_addvar C10_A, 20
    h_addvar C10_A, ITEM_CHERI_BERRY
    c10_giveitem_var C10_A
    h_goto_if_eq HLIB_RESULT, 0, L_SE_BagFull
    h_setflag FLAG_DAILY_RECEIVED_BERRY_SOOTOPOLIS
    h_msgbox T_GiveYouThisBerryToo
    h_closemessage
    h_random C10_B, 2
    h_goto_if_eq C10_B, 0, L_SE_KiriFigy
    h_giveitem ITEM_IAPAPA_BERRY
    h_goto_if_eq HLIB_RESULT, 0, L_SE_BagFull
    VMJump L_SE_KiriWish
L_SE_KiriFigy:
    h_giveitem ITEM_FIGY_BERRY
    h_goto_if_eq HLIB_RESULT, 0, L_SE_BagFull
L_SE_KiriWish:
    h_msgbox T_WhatKindOfWishInYourName
    h_release
L_SE_KiriReceived:
    h_yesno T_LikeSeasonBornIn, C10_SEL
    h_goto_if_yes C10_SEL, L_SE_KiriAutumn
    h_msgbox T_OhDoesntMatter
    h_release
L_SE_KiriAutumn:
    h_msgbox T_ThenILoveAutumn
    h_release
L_SE_BagFull:
    h_bag_is_full T_BagFull
    h_release

// ---- the town's people ---------------------------------------------------------------------------------------------
SE_Woman2:                              // SootopolisCity_EventScript_Woman2 (a spectator: FLAG_HIDE_SOOTOPOLIS_CITY_RESIDENTS)
    c10_talk
    h_goto_if_eq VAR_SOOTOPOLIS_CITY_STATE, 5, L_SE_Woman2Rayquaza
    h_msgbox T_WeatherWentWild
    h_closemessage
    h_turnobject SE_WOMAN_2, 2
    h_release
L_SE_Woman2Rayquaza:
    h_msgbox T_YouBroughtFlyingMon
    h_release

SE_Man:                                 // SootopolisCity_EventScript_Man
    c10_talk
    h_goto_if_ge VAR_SOOTOPOLIS_CITY_STATE, 6, L_SE_ManAfter
    h_msgbox T_NoOrdinaryTourist
    h_release
L_SE_ManAfter:
    h_msgbox T_CityRegainedCalm
    h_release

SE_Woman1:                              // SootopolisCity_EventScript_Woman1
    c10_talk
    h_goto_if_ge VAR_SOOTOPOLIS_CITY_STATE, 6, L_SE_Woman1After
    h_goto_if_eq VAR_SOOTOPOLIS_CITY_STATE, 5, L_SE_Woman1Rayquaza
    h_goto_if_ge VAR_SOOTOPOLIS_CITY_STATE, 2, L_SE_Woman1Legends
    h_msgbox T_SootopolisSkyBeautiful
    h_release
L_SE_Woman1Legends:
    h_msgbox T_GiganticPokemonFight
    h_closemessage
    h_turnobject SE_WOMAN_1, 2
    h_release
L_SE_Woman1After:
    h_msgbox T_NightSkyFavoriteScenery
    h_release
L_SE_Woman1Rayquaza:
    h_msgbox T_FearedWorstWhenPokemonFlewDown
    h_release

SE_NinjaBoy:                            // SootopolisCity_EventScript_NinjaBoy
    c10_talk
    h_goto_if_eq VAR_SOOTOPOLIS_CITY_STATE, 5, L_SE_NinjaRayquaza
    h_goto_if_ge VAR_SOOTOPOLIS_CITY_STATE, 6, L_SE_NinjaNormal
    h_goto_if_le VAR_SOOTOPOLIS_CITY_STATE, 1, L_SE_NinjaNormal
    h_msgbox T_ThisIsWicked
    h_closemessage
    h_turnobject SE_NINJA_BOY, 2
    h_release
L_SE_NinjaNormal:
    h_msgbox T_WonderWhatWorldIsLike
    h_release
L_SE_NinjaRayquaza:
    h_msgbox T_ThatWasWicked
    h_release

SE_Boy1:                                // SootopolisCity_EventScript_Boy1
    c10_talk
    h_goto_if_eq VAR_SOOTOPOLIS_CITY_STATE, 5, L_SE_Boy1Rayquaza
    h_goto_if_set FLAG_SYS_GAME_CLEAR, L_SE_Boy1GameClear
    h_goto_if_ge VAR_SOOTOPOLIS_CITY_STATE, 6, L_SE_Boy1Normal
    h_goto_if_le VAR_SOOTOPOLIS_CITY_STATE, 1, L_SE_Boy1Normal
    h_msgbox T_GiantPokemonSuddenlyAppeared
    h_closemessage
    h_turnobject SE_BOY_1, 2
    h_release
L_SE_Boy1Rayquaza:
    h_msgbox T_WhatIsThatGreenPokemon
    h_release
L_SE_Boy1GameClear:
    h_msgbox T_WhereDidLegendariesGo
    h_release
L_SE_Boy1Normal:
    h_msgbox T_PhysicallyFitLivingHere
    h_release

SE_Boy2:                                // SootopolisCity_EventScript_Boy2
    c10_talk
    h_goto_if_eq VAR_SOOTOPOLIS_CITY_STATE, 5, L_SE_Boy2Rayquaza
    h_msgbox T_TwoPokemonArentAngry
    h_closemessage
    h_turnobject SE_BOY_2, 1
    h_release
L_SE_Boy2Rayquaza:
    h_msgbox T_FlyingMonStoppedRampage
    h_release

SE_BlackBelt:                           // SootopolisCity_EventScript_BlackBelt (cheers before turning to you)
    c10_lock
    h_goto_if_eq VAR_SOOTOPOLIS_CITY_STATE, 5, L_SE_BlackBeltRayquaza
    h_msgbox_actor T_GoRedAndBlueMon, SE_BLACK_BELT
    h_closemessage
    ActorSetEyeToEye
    h_msgbox_actor T_DoYouKnowMonNames, SE_BLACK_BELT
    h_closemessage
    h_turnobject SE_BLACK_BELT, 3
    h_release
L_SE_BlackBeltRayquaza:
    ActorSetEyeToEye
    h_msgbox_actor T_GreenOneSettlesThings, SE_BLACK_BELT
    h_release

SE_Girl:                                // SootopolisCity_EventScript_Girl
    c10_talk
    h_goto_if_eq VAR_SOOTOPOLIS_CITY_STATE, 5, L_SE_GirlRayquaza
    h_msgbox T_SootopolisWillBeWrecked
    h_closemessage
    h_turnobject SE_GIRL, 3
    h_release
L_SE_GirlRayquaza:
    h_msgbox T_SootopolisDidntGetWrecked
    h_release

SE_Maniac:                              // SootopolisCity_EventScript_Maniac
    c10_talk
    h_goto_if_eq VAR_SOOTOPOLIS_CITY_STATE, 5, L_SE_ManiacRayquaza
    h_msgbox T_SeeingLegendWithOwnEyes
    h_closemessage
    h_turnobject SE_MANIAC, 3
    h_release
L_SE_ManiacRayquaza:
    h_msgbox T_SawLegendWithOwnEyes
    h_release

// ---- Steven: the way to the Cave of Origin -------------------------------------------------------------------------
SE_Steven:                              // SootopolisCity_EventScript_Steven
    c10_talk
    h_goto_if_unset FLAG_STEVEN_GUIDES_TO_CAVE_OF_ORIGIN, L_SE_StevenLead
    h_goto_if_eq VAR_SOOTOPOLIS_CITY_STATE, 2, L_SE_StevenHelpWallace
    h_goto_if_eq VAR_SOOTOPOLIS_CITY_STATE, 3, L_SE_StevenHelpedWallace
    h_goto_if_eq VAR_SOOTOPOLIS_CITY_STATE, 4, L_SE_StevenHelpedWallace
    h_goto_if_set FLAG_SOOTOPOLIS_ARCHIE_MAXIE_LEAVE, L_SE_StevenLeft
    h_msgbox T_SoThatsRayquaza
    h_release
L_SE_StevenHelpWallace:
    h_msgbox T_KnowWhatsNeededToHelpHim
    h_release
L_SE_StevenLeft:
    h_msgbox T_MaxieArchieLeft
    h_release
L_SE_StevenHelpedWallace:
    h_msgbox T_NeverBeenToSkyPillar
    h_release
L_SE_StevenLead:                        // SootopolisCity_EventScript_StevenLeadPlayerCaveOfOrigin
    h_msgbox T_InvolvedWithCrisisComeWithMe
    h_closemessage
    h_getplayerfacing C10_A             // (VAR_FACING: west = you stand east of him, north = below him)
    h_goto_if_eq C10_A, 2, L_SE_StartWest
    h_goto_if_ne C10_A, 0, L_SE_Started
    h_applymovement SE_STEVEN, Mv_SE_StevenStartWalk
    h_applymovement 255, Mv_SE_PlayerStartWalkNorth
    h_waitmovement
    VMJump L_SE_Started
L_SE_StartWest:
    h_applymovement SE_STEVEN, Mv_SE_StevenStartWalk
    h_applymovement 255, Mv_SE_PlayerStartWalkWest
    h_waitmovement
L_SE_Started:
    h_msgbox_actor T_DoesThisMakeYourFearPokemon, SE_STEVEN
    h_closemessage
    h_applymovement SE_STEVEN, Mv_SE_StevenWalkToCave
    h_applymovement 255, Mv_SE_PlayerWalkToCave
    h_waitmovement
    h_delay 120
    h_applymovement SE_EXPERT, Mv_SE_ExpertMoveAside
    h_waitmovement
    h_applymovement SE_STEVEN, Mv_SE_StevenArrive
    h_applymovement 255, Mv_SE_PlayerArrive
    h_waitmovement
    h_msgbox_actor T_HereWereAreHelpWallace, SE_STEVEN
    h_closemessage
    h_setflag FLAG_STEVEN_GUIDES_TO_CAVE_OF_ORIGIN
    h_applymovement 255, Mv_SE_PlayerEnterCave
    h_waitmovement
    SEPlay SE_EXIT
    h_warp_arrive 110, 9, 20, 0         // warp MAP_CAVE_OF_ORIGIN_ENTRANCE, 9, 20 (zone 110, room origin (0, 0))
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

// ---- Wallace, Maxie and Archie after Rayquaza ------------------------------------------------------------------------
SE_Wallace:                             // SootopolisCity_EventScript_Wallace
    c10_talk
    h_goto_if_eq VAR_SOOTOPOLIS_CITY_STATE, 4, L_SE_WallaceSkyPillar
    h_goto_if_set FLAG_RECEIVED_HM_WATERFALL, L_SE_WallaceGym
    h_goto_if_set FLAG_SOOTOPOLIS_ARCHIE_MAXIE_LEAVE, L_SE_WallaceWaterfall
    h_msgbox T_AquaMagmaDidntMeanHarm
    h_release
L_SE_WallaceSkyPillar:
    h_msgbox T_HaventYouScaledSkyPillar
    h_release
L_SE_WallaceGym:
    h_msgbox T_DazzledByMentor
    h_release
L_SE_WallaceWaterfall:                  // SootopolisCity_EventScript_GiveWaterfall
    h_msgbox T_ThankYouForHelpAcceptThis
    h_closemessage
    h_giveitem ITEM_HM05                // ITEM_HM_WATERFALL: Black 2's HM05 is Waterfall (data/hoenn_items.json)
    h_setflag FLAG_RECEIVED_HM_WATERFALL
    h_msgbox T_ExplainWaterfallGoToGym
    h_closemessage
    h_getplayerfacing C10_A
    h_goto_if_eq C10_A, 2, L_SE_WallaceMoveWest    // you face west: he steps left; north or east: right
    h_goto_if_eq C10_A, 1, L_SE_WallaceDone
    h_applymovement SE_WALLACE, Mv_SE_WallaceMoveFromGym
    h_waitmovement
    h_setvar VAR_SOOTOPOLIS_WALLACE_STATE, 1   // (copyobjectxytoperm: the zone init puts him there)
    h_release
L_SE_WallaceMoveWest:
    h_applymovement SE_WALLACE, Mv_SE_WallaceMoveFromGymWest
    h_waitmovement
    h_setvar VAR_SOOTOPOLIS_WALLACE_STATE, 2
L_SE_WallaceDone:
    h_release

SE_Maxie:                               // SootopolisCity_EventScript_Maxie (lockall, no faceplayer)
    c10_lock
    h_goto_if_eq VAR_SOOTOPOLIS_CITY_STATE, 5, L_SE_MaxieRayquaza
    h_msgbox_actor T_GroudonPleaseStop, SE_MAXIE
    h_release
L_SE_MaxieRayquaza:
    h_msgbox_actor T_AfterAllOurScheming, SE_MAXIE
    h_setflag FLAG_MET_MAXIE_SOOTOPOLIS
    h_goto_if_set FLAG_MET_ARCHIE_SOOTOPOLIS, L_SE_MaxieArchieLeave
    h_release

SE_Archie:                              // SootopolisCity_EventScript_Archie
    c10_lock
    h_goto_if_eq VAR_SOOTOPOLIS_CITY_STATE, 5, L_SE_ArchieRayquaza
    h_msgbox_actor T_KyogreCalmDown, SE_ARCHIE
    h_release
L_SE_ArchieRayquaza:
    h_msgbox_actor T_TryingMeaninglessToPokemon, SE_ARCHIE
    h_setflag FLAG_MET_ARCHIE_SOOTOPOLIS
    h_goto_if_set FLAG_MET_MAXIE_SOOTOPOLIS, L_SE_MaxieArchieLeave
    h_release
L_SE_MaxieArchieLeave:                  // SootopolisCity_EventScript_MaxieArchieLeave: both go back to Mt. Pyre's summit
    h_closemessage
    h_setflag FLAG_HIDE_SOOTOPOLIS_CITY_MAXIE
    h_setflag FLAG_HIDE_SOOTOPOLIS_CITY_ARCHIE
    h_setflag FLAG_SOOTOPOLIS_ARCHIE_MAXIE_LEAVE
    h_clearflag FLAG_HIDE_MT_PYRE_SUMMIT_MAXIE
    h_clearflag FLAG_HIDE_MT_PYRE_SUMMIT_ARCHIE
    h_setvar VAR_MT_PYRE_STATE, 2
    h_warp_arrive SE_ZONE, SC_X(31), SC_Z(34), 0   // warpsilent MAP_SOOTOPOLIS_CITY, 31, 34 (the Gym door opens: zone init)
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

// ---- closed doors -------------------------------------------------------------------------------------------------
SE_ClosedDoor:                          // EventScript_ClosedSootopolisDoor: a house door while the legends are here
    c10_lock
    h_goto_if_unset FLAG_KYOGRE_ESCAPED_SEAFLOOR_CAVERN, L_SE_DoorOpen
    h_goto_if_set FLAG_SOOTOPOLIS_ARCHIE_MAXIE_LEAVE, L_SE_DoorOpen
    h_msgbox_info T_DoorIsClosed
    h_closemessage
L_SE_DoorOpen:
    h_release
SE_ClosedGymDoor:                       // the Gym door (SootopolisCity_EventScript_LockGymDoor's closed door)
    c10_lock
    h_goto_if_set FLAG_SOOTOPOLIS_ARCHIE_MAXIE_LEAVE, L_SE_GymOpen
    h_msgbox_info T_DoorIsClosed
    h_closemessage
L_SE_GymOpen:
    h_release

    .balign 4, 0
Mv_SE_StevenStartWalk:                  // SootopolisCity_Movement_StevenStartWalkToCaveOfOrigin
    walk_up 3
    walk_right
    walk_up 11
    walk_left
    walk_up 4
    walk_left 4
    walk_up 11
    walk_in_place_fastest_down
    step_end
    .balign 4, 0
Mv_SE_PlayerStartWalkWest:              // SootopolisCity_Movement_PlayerStartWalkToCaveOfOriginWest
    walk_left
    walk_up 3
    walk_right
    walk_up 11
    walk_left
    walk_up 4
    walk_left 4
    walk_up 10
    step_end
    .balign 4, 0
Mv_SE_PlayerStartWalkNorth:             // SootopolisCity_Movement_PlayerStartWalkToCaveOfOriginNorth
    walk_up 4
    walk_right
    walk_up 11
    walk_left
    walk_up 4
    walk_left 4
    walk_up 10
    step_end
    .balign 4, 0
Mv_SE_StevenWalkToCave:                 // SootopolisCity_Movement_StevenWalkToCaveOfOrigin
    walk_up 2
    walk_right 4
    walk_down 2
    walk_right 5
    walk_up
    walk_right 4
    walk_down 3
    walk_right 5
    walk_down 4
    walk_left 8
    walk_down 8
    walk_right 4
    delay_4
    walk_in_place_fastest_left
    delay_16 2
    walk_right
    walk_up 2
    step_end
    .balign 4, 0
Mv_SE_PlayerWalkToCave:                 // SootopolisCity_Movement_PlayerWalkToCaveOfOrigin
    walk_up 3
    walk_right 4
    walk_down 2
    walk_right 5
    walk_up
    walk_right 4
    walk_down 3
    walk_right 5
    walk_down 4
    walk_left 8
    walk_down 8
    walk_right 3
    step_end
    .balign 4, 0
Mv_SE_ExpertMoveAside:                  // SootopolisCity_Movement_ExpertMoveAside
    walk_slow_left
    walk_in_place_fastest_right
    step_end
    .balign 4, 0
Mv_SE_StevenArrive:                     // SootopolisCity_Movement_StevenArriveCaveEntrance
    walk_down 2
    walk_left
    delay_8
    walk_right
    walk_up 3
    walk_right
    walk_in_place_fastest_left
    step_end
    .balign 4, 0
Mv_SE_PlayerArrive:                     // SootopolisCity_Movement_PlayerArriveCaveEntrance
    delay_16 3
    delay_8
    walk_right 2
    walk_up 3
    walk_in_place_fastest_right
    step_end
    .balign 4, 0
Mv_SE_PlayerEnterCave:                  // SootopolisCity_Movement_PlayerEnterCaveOfOrigin
    walk_up 2
    step_end
    .balign 4, 0
Mv_SE_KyogreAttack:                     // SootopolisCity_Movement_KyogreAttack (walk_left_affine: a plain step here)
    walk_in_place_slow_left 3
    delay_16 3
    walk_left
    step_end
    .balign 4, 0
Mv_SE_KyogreDefend:                     // SootopolisCity_Movement_KyogreDefend
    delay_16 9
    walk_left
    step_end
    .balign 4, 0
Mv_SE_KyogreMoveBack:                   // SootopolisCity_Movement_KyogreMoveBack
    lock_facing_direction
    walk_right
    delay_16 3
    unlock_facing_direction
    step_end
    .balign 4, 0
Mv_SE_KyogreIdle:                       // SootopolisCity_Movement_KyogreIdle
    walk_in_place_slow_left 6
    step_end
    .balign 4, 0
Mv_SE_GroudonAttack:                    // SootopolisCity_Movement_GroudonAttack
    walk_in_place_slow_right 3
    delay_16 3
    walk_fast_right
    step_end
    .balign 4, 0
Mv_SE_GroudonDefend:                    // SootopolisCity_Movement_GroudonDefend
    delay_16 9
    walk_fast_right
    step_end
    .balign 4, 0
Mv_SE_GroudonMoveBack:                  // SootopolisCity_Movement_GroudonMoveBack
    lock_facing_direction
    walk_left
    delay_16 3
    unlock_facing_direction
    step_end
    .balign 4, 0
Mv_SE_GroudonIdle:                      // SootopolisCity_Movement_GroudonIdle
    walk_in_place_slow_right 6
    step_end
    .balign 4, 0
Mv_SE_RayquazaFlyOff:                   // SootopolisCity_Movement_RayquazaFlyOff
    walk_fast_up
    walk_fastest_up 6
    step_end
    .balign 4, 0
Mv_SE_PlayerApproach:                   // SootopolisCity_Movement_PlayerApproachLegendaries
    walk_up 4
    step_end
    .balign 4, 0
Mv_SE_WallaceMoveFromGym:               // SootopolisCity_Movement_WallaceMoveFromGym
    walk_right
    walk_in_place_fastest_down
    step_end
    .balign 4, 0
Mv_SE_WallaceMoveFromGymWest:           // SootopolisCity_Movement_WallaceMoveFromGymWest
    walk_left
    walk_in_place_fastest_down
    step_end

#include "common/movement.inc"
#ifdef HOENN_TEST_CH10
#include "scenes/ch10_test.inc"
#endif
#endif
