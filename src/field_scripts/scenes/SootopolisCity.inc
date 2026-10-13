// Sootopolis City's story (Sapphire data/maps/SootopolisCity/scripts.inc; chapter Ch10, ch10 agent 2026-10-07).
// converter/gen_map_content.py includes this file twice in the generated zone file of zone 319: the entries below are
// scripts 1-15, the generated signs (Gym, Mart, Pokémon Center, city) follow. Text: src/text/scenes/SootopolisCity.txt.
// People: data/story/ch10.json (outdoor uid = 100 + Sapphire local id; the standalone group's own matrix, the map at
// (18,21)). The generator leaves all eleven out (every one has a hide flag or a branch), so the zone's NPC list is exactly
// the json's order: index 0-10 = Sapphire objects 1-11 (SC_IDX_* below; checked in the built ROM). The zone's warps: 0 is
// Black 2's own (parked), 1 + Sapphire's warp id = the doors (1 Pokémon Center, 2 Mart, 3 Gym, 4 Cave of Origin, 5-12
// Houses 1-8; checked in the built ROM).
//
// Sapphire's map scripts, all done by the zone init (SC_Init):
//   OnTransition: FLAG_VISITED_SOOTOPOLIS_CITY; after the Kyogre battle Steven stands outside the Gym; while FLAG_SYS_WEATHER_CTRL
//     (Kyogre's rain: the `weather` patch makes it rain, common/legendary_weather.inc) the two women at the Cave stand one
//     tile up and, in state 1 (VAR_SOOTOPOLIS_STATE), Steven and Wallace wait at (29,6) / (30,6).
//   OnLoad: before the legend escapes the old man (the Cave of Origin expert) blocks the cave stairs and the Gym door is
//     closed; during the crisis (FLAG_LEGEND_ESCAPED_SEAFLOOR_CAVERN set, FLAG_LEGENDARY_BATTLE_COMPLETED clear) every door
//     is closed (setmetatile ... Door_Closed). Black 2 has no metatile swap: a closed door is a door whose warp the zone init
//     moves off the map (ObjInitWarpGPos n, 0, 0, 0, as Lilycove's hideout door), plus a sign on the door tile that says
//     "The door is closed." (ClosedSootopolisDoorScript: bumping / A on the door).
//   OnResume: the dive spot (9,6) of Underwater_SootopolisCity is the dive agent's table (notes/DIVE.md).
// Black 2 gaps: Steven leaves on his Skarmory (FLDEFF_NPCFLY_OUT): he disappears after a pause (ch10_lib c10_fly_out);
// setobjectmovementtype of Steven and Wallace (they face each other / stand still): the entity's facing is set by
// ObjInitNPCGPos, and the scene turns them; `moveobjectoffscreen` is not needed (the lists end on the objects' own tiles).
#ifdef HOENN_EMERALD
// Pokémon Emerald NDS (emerald_ch10, 2026-10-12): Emerald's own Sootopolis (the legends' fight, Rayquaza, Wallace, Juan's
// Gym): its entries and bodies are scenes/emerald/SootopolisCity.inc (Sapphire and Ruby assemble the part below unchanged)
#include "scenes/emerald/SootopolisCity.inc"
#elif defined(SCENE_ENTRIES)
    ScriptEntry SC_Init                 // 1: SootopolisCity_OnTransition / _OnLoad (zone init)
    ScriptEntry SC_Expert               // 2: object 3 (SootopolisCity_EventScript_CaveOfOriginExpert)
    ScriptEntry SC_CaveWoman1           // 3: object 1 (EventScript_CaveEntranceWoman1)
    ScriptEntry SC_CaveWoman2           // 4: object 2 (EventScript_CaveEntranceWoman2)
    ScriptEntry SC_Kiri                 // 5: object 6 (EventScript_KiriGiveBerry)
    ScriptEntry SC_Woman2               // 6: object 4 (EventScript_Woman2)
    ScriptEntry SC_Man1                 // 7: object 9 (EventScript_Man1)
    ScriptEntry SC_Woman1               // 8: object 11 (EventScript_Woman1)
    ScriptEntry SC_Boy1                 // 9: object 7 (EventScript_Boy1)
    ScriptEntry SC_Boy1Normal           // 10: object 8 (EventScript_Boy1Normal)
    ScriptEntry SC_Wallace              // 11: object 5 (EventScript_YouMustGoWithOrb)
    ScriptEntry SC_Steven               // 12: object 10 (EventScript_YoullBeOkay)
    ScriptEntry SC_LeadPlayer           // 13: trigger (25,6) VAR_SOOTOPOLIS_STATE 1 (EventScript_LeadPlayerCaveOfOrigin)
    ScriptEntry SC_ClosedDoor           // 14: the ten closed doors (ClosedSootopolisDoorScript, signs in data/story/ch10.json)
    ScriptEntry SC_ClosedGymDoor        // 15: the Gym's door (closed until the legend is calmed)
#else
#include "scenes/ch10_lib.inc"

#define T_CaveOfOriginPleaseLeave 0
#define T_AllLifeStartsAtTheCave 1
#define T_TheLegendWasTrue 2
#define T_NaturalBalanceIsShifting 3
#define T_NameIsKiri 4
#define T_GiveYouThisBerryToo 5
#define T_WhatKindOfWish 6
#define T_KiriBornInSeasons 7
#define T_ThenILoveAutumn 8
#define T_OhDoesntMatter 9
#define T_YoureGoingToChallengeWallace 10
#define T_BecomeYourFan 11
#define T_NoOrdinaryTourist1 12
#define T_NoOrdinaryTourist2 13
#define T_SootopolisSkyBeautiful 14
#define T_NightSkyFavoriteScenery 15
#define T_WonderWhatWorldIsLike 16
#define T_WhereIsMyHouse 17
#define T_PhysicallyFit 18
#define T_YouCameInRainstorm 19
#define T_MyNameIsWallace 20
#define T_ThatIsTheBlueOrb 21
#define T_PeopleNeedRain 22
#define T_CaveOfOriginWithOrb 23
#define T_NeverExpectedOrb 24
#define T_YouMustGoWithOrb 25
#define T_YoullBeOkay 26
#define T_WeOweItAllToYou 27
#define T_DoorClosed 28
#define T_BagFull 29

#define SC_X(x) (18+(x))                // Sapphire tile -> tile of the standalone group's matrix (b2tools/world.py)
#define SC_Z(z) (21+(z))

// zone NPC list indices (ObjInitNPCGPos) and uids
#define SC_IDX_WOMAN_CAVE1 0
#define SC_IDX_WOMAN_CAVE2 1
#define SC_IDX_EXPERT 2
#define SC_IDX_WALLACE 4
#define SC_IDX_STEVEN 9
#define SC_WALLACE 105                  // object 5
#define SC_STEVEN 110                   // object 10
// warp slots of the doors (1 + Sapphire's warp id)
#define SC_WARP_CENTER 1
#define SC_WARP_MART 2
#define SC_WARP_GYM 3
#define SC_WARP_HOUSE1 5

SC_Init:                                // SootopolisCity_OnTransition + _OnLoad
#ifdef HOENN_TEST_CH10
    VMCall Test_Ch10Start               // test builds only (scenes/ch10_test.inc)
#endif
    h_setflag FLAG_VISITED_SOOTOPOLIS_CITY
    h_goto_if_unset FLAG_LEGEND_ESCAPED_SEAFLOOR_CAVERN, L_SC_BeforeLegend
    h_goto_if_set FLAG_LEGENDARY_BATTLE_COMPLETED, L_SC_AfterLegend
    // the crisis: SootopolisCity_EventScript_SetWeather (the women one tile up, Steven and Wallace in state 1) and
    // _LockCityDoors (every door closed)
    ObjInitNPCGPos SC_IDX_WOMAN_CAVE1, 1, SC_X(29), 0, SC_Z(19)    // setobjectxyperm 1, 29, 19
    ObjInitNPCGPos SC_IDX_WOMAN_CAVE2, 1, SC_X(33), 0, SC_Z(19)    // setobjectxyperm 2, 33, 19
    h_goto_if_ne VAR_SOOTOPOLIS_STATE, 1, L_SC_LockDoors
    ObjInitNPCGPos SC_IDX_STEVEN, 3, SC_X(29), 0, SC_Z(6)          // setobjectxyperm 10, 29, 6 (faces right)
    ObjInitNPCGPos SC_IDX_WALLACE, 2, SC_X(30), 0, SC_Z(6)         // setobjectxyperm 5, 30, 6 (faces left)
L_SC_LockDoors:
#ifdef HOENN_TEST_CH10_OPEN
    VMHalt                              // test builds only: the doors stay open (a test enters through a house and walks out)
#endif
    ObjInitWarpGPos SC_WARP_CENTER, 0, 0, 0
    ObjInitWarpGPos SC_WARP_MART, 0, 0, 0
    ObjInitWarpGPos SC_WARP_HOUSE1+0, 0, 0, 0
    ObjInitWarpGPos SC_WARP_HOUSE1+1, 0, 0, 0
    ObjInitWarpGPos SC_WARP_HOUSE1+2, 0, 0, 0
    ObjInitWarpGPos SC_WARP_HOUSE1+3, 0, 0, 0
    ObjInitWarpGPos SC_WARP_HOUSE1+4, 0, 0, 0
    ObjInitWarpGPos SC_WARP_HOUSE1+5, 0, 0, 0
    ObjInitWarpGPos SC_WARP_HOUSE1+6, 0, 0, 0
    ObjInitWarpGPos SC_WARP_HOUSE1+7, 0, 0, 0
    ObjInitWarpGPos SC_WARP_GYM, 0, 0, 0
    VMHalt
L_SC_BeforeLegend:                      // OnLoad: SootopolisCity_EventScript_ExpertBlockCaveOfOrigin
    ObjInitNPCGPos SC_IDX_EXPERT, 1, SC_X(31), 0, SC_Z(18)         // setobjectxyperm 3, 31, 18
    ObjInitWarpGPos SC_WARP_GYM, 0, 0, 0                           // setmetatile 31, 32, GymDoor_Closed
    VMHalt
L_SC_AfterLegend:                       // OnTransition: SootopolisCity_EventScript_SetStevenOutsideGymPostLegendary
    ObjInitNPCGPos SC_IDX_STEVEN, 1, SC_X(31), 0, SC_Z(33)         // setobjectxyperm 10, 31, 33 (faces down)
    VMHalt

// ---- the Cave of Origin's keeper and the people at the stairs ------------------------------------------------------
SC_Expert:                              // SootopolisCity_EventScript_CaveOfOriginExpert
    c10_talk
    h_goto_if_set FLAG_LEGENDARY_BATTLE_COMPLETED, L_SC_ExpertAfter
    h_msgbox T_CaveOfOriginPleaseLeave  // Who might you be? This is the Cave Of Origin. ... Please leave.
    h_release
L_SC_ExpertAfter:
    h_msgbox T_AllLifeStartsAtTheCave   // All life starts at the Cave Of Origin, and it all ends on Mt. Pyre...
    h_release

SC_CaveWoman1:                          // SootopolisCity_EventScript_CaveEntranceWoman1 (MSGBOX_NPC)
    h_msgbox_npc T_TheLegendWasTrue
SC_CaveWoman2:                          // SootopolisCity_EventScript_CaveEntranceWoman2
    h_msgbox_npc T_NaturalBalanceIsShifting

// ---- Kiri: a Berry once a day --------------------------------------------------------------------------------------
SC_Kiri:                                // SootopolisCity_EventScript_KiriGiveBerry
    c10_talk
    h_goto_if_set FLAG_DAILY_RECEIVED_BERRY_SOOTOPOLIS, L_SC_KiriReceived     // (dotimebasedevents: Black 2 resets the daily flag at midnight)
    h_msgbox T_NameIsKiri               // Hi, what's your name? ... My name is Kiri. ... You can have one of these.
    h_closemessage
    h_random C10_A, 10                  // a Pomeg ... Nomel Berry: ITEM_CHERI_BERRY + 20 + random(10)
    h_addvar C10_A, 20
    h_addvar C10_A, ITEM_CHERI_BERRY
    c10_giveitem_var C10_A
    h_goto_if_eq HLIB_RESULT, 0, L_SC_BagFull
    h_setflag FLAG_DAILY_RECEIVED_BERRY_SOOTOPOLIS
    h_msgbox T_GiveYouThisBerryToo      // Kiri will give you this Berry, too! I really like it lots!
    h_closemessage
    h_random C10_B, 2
    h_goto_if_eq C10_B, 0, L_SC_KiriFigy
    h_giveitem ITEM_IAPAPA_BERRY
    h_goto_if_eq HLIB_RESULT, 0, L_SC_BagFull
    VMJump L_SC_KiriWish
L_SC_KiriFigy:
    h_giveitem ITEM_FIGY_BERRY
    h_goto_if_eq HLIB_RESULT, 0, L_SC_BagFull
L_SC_KiriWish:
    h_msgbox T_WhatKindOfWish           // I wonder what kind of wish is included in your name.
    h_release
L_SC_KiriReceived:
    h_yesno T_KiriBornInSeasons, C10_SEL    // Spring, summer, autumn, and winter. If you're born in springtime, do you like the spring ...?
    h_goto_if_yes C10_SEL, L_SC_KiriSeason
    h_msgbox T_OhDoesntMatter           // Oh... It doesn't matter... There's so much that I want to know...
    h_release
L_SC_KiriSeason:
    h_msgbox T_ThenILoveAutumn          // Then Kiri was born in the autumn, so I love the autumn! Which season do you like?
    h_release
L_SC_BagFull:                           // Common_EventScript_ShowBagIsFull
    h_bag_is_full T_BagFull
    h_release

// ---- the town's people (the residents are hidden during the crisis by FLAG_HIDE_SOOTOPOLIS_RESIDENTS) ---------------
SC_Woman2:                              // SootopolisCity_EventScript_Woman2
    c10_talk
    h_goto_if_set FLAG_DEFEATED_SOOTOPOLIS_GYM, L_SC_Woman2Fan
    h_msgbox T_YoureGoingToChallengeWallace     // Let me guess, you're going to challenge Wallace? ...
    h_release
L_SC_Woman2Fan:
    h_msgbox T_BecomeYourFan            // Let me guess, you've beaten Wallace! Oh, you did, really? Maybe I'll become your fan!
    h_release

SC_Man1:                                // SootopolisCity_EventScript_Man1
    c10_talk
    h_goto_if_set FLAG_LEGENDARY_BATTLE_COMPLETED, L_SC_Man1After
    h_msgbox T_NoOrdinaryTourist1
    h_release
L_SC_Man1After:
    h_msgbox T_NoOrdinaryTourist2
    h_release

SC_Woman1:                              // SootopolisCity_EventScript_Woman1
    c10_talk
    h_goto_if_set FLAG_LEGENDARY_BATTLE_COMPLETED, L_SC_Woman1After
    h_msgbox T_SootopolisSkyBeautiful
    h_release
L_SC_Woman1After:
    h_msgbox T_NightSkyFavoriteScenery
    h_release

SC_Boy1:                                // SootopolisCity_EventScript_Boy1
    c10_talk
    h_goto_if_set FLAG_LEGENDARY_BATTLE_COMPLETED, L_SC_Boy1After
    h_msgbox T_WonderWhatWorldIsLike
    h_release
L_SC_Boy1After:
    h_msgbox T_WhereIsMyHouse
    h_release

SC_Boy1Normal:                          // SootopolisCity_EventScript_Boy1Normal (MSGBOX_NPC)
    h_msgbox_npc T_PhysicallyFit

// ---- Wallace and Steven at the Cave of Origin ------------------------------------------------------------------------
SC_Wallace:                             // SootopolisCity_EventScript_YouMustGoWithOrb (MSGBOX_NPC)
    h_msgbox_npc T_YouMustGoWithOrb

SC_Steven:                              // SootopolisCity_EventScript_YoullBeOkay
    c10_talk
    h_goto_if_set FLAG_LEGENDARY_BATTLE_COMPLETED, L_SC_StevenAfter
    h_msgbox T_YoullBeOkay              // Steven: You'll be okay. With your Pokémon, you'll get things done whatever happens. ...
    h_release
L_SC_StevenAfter:                       // SootopolisCity_EventScript_14D4AD
    h_msgbox T_WeOweItAllToYou          // Steven: <player>, we owe it all to you. ... Give it your best shot.
    h_closemessage
    h_applymovement SC_STEVEN, Common_Movement_WalkInPlaceFastestDown
    h_waitmovement
    h_delay 50
    c10_fly_out SC_STEVEN, FLAG_HIDE_STEVEN_SOOTOPOLIS   // flies off on his Skarmory
    h_release

// ---- closed doors -------------------------------------------------------------------------------------------------
SC_ClosedDoor:                          // ClosedSootopolisDoorScript (a closed door only during the crisis)
    c10_lock
    h_goto_if_unset FLAG_LEGEND_ESCAPED_SEAFLOOR_CAVERN, L_SC_DoorOpen
    h_goto_if_set FLAG_LEGENDARY_BATTLE_COMPLETED, L_SC_DoorOpen
    h_msgbox_info T_DoorClosed          // The door is closed.
    h_closemessage
L_SC_DoorOpen:
    h_release
SC_ClosedGymDoor:                       // the Gym's door is closed until the legend is calmed
    c10_lock
    h_goto_if_set FLAG_LEGENDARY_BATTLE_COMPLETED, L_SC_GymDoorOpen
    h_msgbox_info T_DoorClosed
    h_closemessage
L_SC_GymDoorOpen:
    h_release

// ---- Steven leads the player to Wallace, Wallace to the Cave of Origin ------------------------------------------------
SC_LeadPlayer:                          // SootopolisCity_EventScript_LeadPlayerCaveOfOrigin
    c10_lock
    h_applymovement SC_STEVEN, Common_Movement_WalkInPlaceFastestLeft
    h_applymovement 255, Common_Movement_WalkInPlaceFastestRight
    h_waitmovement
    h_applymovement SC_STEVEN, Common_Movement_ExclamationMark
    h_waitmovement
    h_applymovement SC_STEVEN, Common_Movement_Delay48
    h_waitmovement
    h_applymovement SC_STEVEN, Mv_SC_StevenApproach
    h_waitmovement
    h_msgbox_actor T_YouCameInRainstorm, SC_STEVEN      // Steven: <player>, you came, too? In this terrible rainstorm, yet... Oh, yes, can you hear out what my friend has to say?
    h_closemessage
    h_applymovement SC_STEVEN, Mv_SC_StevenLeadToWallace
    h_applymovement 255, Mv_SC_PlayerFollowToWallace
    h_waitmovement
    h_msgbox_actor T_MyNameIsWallace, SC_WALLACE        // My name is Wallace. I'm this town's Gym Leader. ... This downpour is caused by a power emanating from the Cave Of Origin.
    h_applymovement SC_WALLACE, Common_Movement_ExclamationMark
    h_waitmovement
    h_applymovement SC_WALLACE, Common_Movement_Delay48
    h_waitmovement
    h_msgbox_actor T_ThatIsTheBlueOrb, SC_WALLACE       // That... That is the Blue Orb. I see. Follow me.
    h_closemessage
    h_delay 30
    h_applymovement SC_WALLACE, Mv_SC_WallaceStartLead
    h_applymovement SC_STEVEN, Mv_SC_StevenStartFollow
    h_applymovement 255, Mv_SC_PlayerStartFollow
    h_waitmovement
    h_applymovement SC_WALLACE, Common_Movement_WalkInPlaceFastestRight
    h_applymovement 255, Common_Movement_WalkInPlaceFastestRight
    h_waitmovement
    h_delay 30
    h_applymovement SC_STEVEN, Common_Movement_WalkInPlaceFastestDown
    h_waitmovement
    h_msgbox_actor T_PeopleNeedRain, SC_STEVEN          // Steven: This rain... People and Pokémon need water to live... ... If that were to happen...
    h_closemessage
    h_delay 30
    h_applymovement SC_WALLACE, Mv_SC_WallaceContinueLead
    h_applymovement 255, Mv_SC_PlayerContinueFollow
    h_applymovement SC_STEVEN, Mv_SC_StevenContinueFollow
    h_waitmovement
    h_applymovement SC_WALLACE, Common_Movement_WalkInPlaceFastestLeft
    h_waitmovement
    h_msgbox_actor T_CaveOfOriginWithOrb, SC_WALLACE    // Wallace: The Cave Of Origin is ahead. ... You must go regardless of what awaits you inside the Cave...
    h_applymovement 255, Common_Movement_WalkInPlaceFastestLeft
    h_waitmovement
    h_msgbox_actor T_NeverExpectedOrb, SC_STEVEN        // Steven: <player>, I never expected you to be holding the Blue Orb. ... I'm convinced of it!
    h_closemessage
    h_setvar VAR_SOOTOPOLIS_STATE, 2
    h_release

    .balign 4, 0
Mv_SC_StevenApproach:                   // SootopolisCity_EventScript_StevenApproachYouCameToo
    walk_left 3
    step_end
    .balign 4, 0
Mv_SC_StevenLeadToWallace:              // _StevenLeadPlayerToWallace
    walk_right 3
    walk_up
    walk_in_place_fastest_down
    step_end
    .balign 4, 0
Mv_SC_PlayerFollowToWallace:            // _PlayerFollowStevenToWallace
    walk_right 4
    step_end
    .balign 4, 0
Mv_SC_StevenStartFollow:                // _StevenStartFollowPlayerToCave
    walk_down
    walk_right
    walk_down 3
    walk_right 4
    walk_down 4
    walk_left 2
    step_end
    .balign 4, 0
Mv_SC_StevenContinueFollow:             // _StevenContinueFollowPlayerToCave
    walk_left 6
    walk_down 8
    walk_right 4
    step_end
    .balign 4, 0
Mv_SC_PlayerStartFollow:                // _PlayerStartFollowWallaceToCave
    walk_right
    walk_down 3
    walk_right 4
    walk_down 4
    walk_left 5
    step_end
    .balign 4, 0
Mv_SC_PlayerContinueFollow:             // _PlayerContinueFollowWallaceToCave
    delay_16 2
    walk_left 3
    walk_down 8
    walk_right 5
    step_end
    .balign 4, 0
Mv_SC_WallaceStartLead:                 // _WallaceStartLeadPlayerToCave
    walk_down 3
    walk_right 4
    walk_down 4
    walk_left 6
    step_end
    .balign 4, 0
Mv_SC_WallaceContinueLead:              // _WallaceContinueLeadPlayerToCave
    delay_16 2
    walk_left 2
    walk_down 8
    walk_right 6
    step_end

#if __has_include("common/legendary_weather.inc")
#include "common/legendary_weather.inc"
#endif
#include "common/movement.inc"
#ifdef HOENN_TEST_CH10
#include "scenes/ch10_test.inc"
#endif
#endif
