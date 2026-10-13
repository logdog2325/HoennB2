// Lilycove City's story (Sapphire data/maps/LilycoveCity/scripts.inc; chapter Ch8, part 8a, ch8a agent 2026-10-07).
// converter/gen_map_content.py includes this file twice in 0192_auto_LilycoveCity.s: the entries below are scripts
// 1-14, the generated signs/people follow. Text: src/text/scenes/LilycoveCity.txt (lines T_* below). People and the
// Wailmer: data/story/ch8a.json (outdoor uid = 100 + Sapphire local id). Map scripts: scenes/LilycoveCity_init.inc
// (zone init = script 1). The rival's room in Littleroot after this battle: scenes/players_house_2f_ch8.inc.
// RUBY (ruby_scenes, 2026-10-08; pokeruby LilycoveCity_OnLoad .ifndef SAPPHIRE: 12 metatiles at x 69-72, y 4-6 redrawn one tile east, warp (71,5) to
// MagmaHideout_1F instead of (70,5) to AquaHideout_1F): the evil team here is Team Magma (the cove grunts' art is sprite codes 293/294, swapped by
// src/sprites/overworld/ruby/; the lines are the Ruby text layer's). Nothing in this file changes: the cave mouth is terrain, shared by both
// versions, and its door is the same world.json door (LC_HIDEOUT_WARP 27); b2tools/patches/hoenn_world.py retargets it to MagmaHideout_1F
// (zone 228) in a Ruby build (data/versions.json "doors"). The Mind Badge closes it in both versions (RemoveEvilTeamBaseEntrance, below).
#ifdef SCENE_ENTRIES
    ScriptEntry Story_Init              // 1: LilycoveCity_OnTransition + OnLoad (zone init)
    ScriptEntry LC_Rival                // 2: object 17 (the rival outside the Department Store)
    ScriptEntry LC_WailmerGrunt         // 3: object 10 (the Aqua grunt at the cove)
    ScriptEntry LC_Grunt1               // 4: object 13
    ScriptEntry LC_Grunt2               // 5: object 14
    ScriptEntry LC_Grunt3               // 6: object 15
    ScriptEntry LC_Grunt4               // 7: object 12
    ScriptEntry LC_Sailor2              // 8: object 1
    ScriptEntry LC_Girl                 // 9: object 2
    ScriptEntry LC_Woman2               // 10: object 6
    ScriptEntry LC_ExpertM2             // 11: object 9
    ScriptEntry LC_BerryGentleman       // 12: object 16
    ScriptEntry LC_MuseumSign           // 13: LilycoveCity_EventScript_MuseumSign sign (19,7)
    ScriptEntry LC_HarborSign           // 14: LilycoveCity_EventScript_HarborSign sign (6,30)
#else
#include "hoenn_key_items.h"
#include "scenes/ch8a_lib.inc"

// text lines (src/text/scenes/LilycoveCity.txt)
#define T_MayShopping 0
#define T_MayBattleMe 1
#define T_MayNotRaising 2
#define T_MayWontBeBeaten 3
#define T_MayGoingBack 4
#define T_MayBadges 5
#define T_MayLeague 6
#define T_MayTower 7
#define T_BrendanShopping 8
#define T_BrendanBattleMe 9
#define T_BrendanNoConfidence 10
#define T_BrendanWontBeBeaten 11
#define T_BrendanGoingBack 12
#define T_BrendanBadges 13
#define T_BrendanLeague 14
#define T_BrendanTower 15
#define T_MovedLoot 16
#define T_BigThings 17
#define T_DontGoNear 18
#define T_IfWorldOurs 19
#define T_WailmerLeap 20
#define T_GetLost 21
#define T_StrangeCave 22
#define T_MoveDeleterHMs 23
#define T_TrainingWailmer 24
#define T_SomeonePunted 25
#define T_SomeoneStole 26
#define T_MissingCameBack 27
#define T_Renovated 28
#define T_GoneForGood 29
#define T_BerrySuitsYou 30
#define T_BecauseTrainer 31
#define T_PokeblocksSuit 32
#define T_BagFull 33
#define T_MuseumSign 34
#define T_MuseumSignPlayers 35
#define T_HarborUnderConstruction 36
#define T_HarborSign 37

#define LC_RIVAL 117                    // object 17, RIVAL_GFX (FLAG_HIDE_RIVAL_LILYCOVE_MART)
#define LC_WAILMER_GRUNT 110            // object 10 (FLAG_HIDE_GRUNTS_LILYCOVE)
// The Aqua Hideout door: Black 2 keeps zone 96's 14 own warps (parked) before world.json's doors
// (b2tools/patches/hoenn_world.py), and the hideout door is the 14th door: warp 27 (checked in the built ROM).
#define LC_HIDEOUT_WARP 27

Story_Init:                             // LilycoveCity_OnTransition (SetupEvilTeamGfxIds: Aqua models are placed directly)
    h_setflag FLAG_VISITED_LILYCOVE_CITY
    h_setvar VAR_LINK_CONTEST_ROOM_STATE, 0
    h_setflag FLAG_HIDE_LILYCOVE_CONTEST_HALL_REPORTER
#if __has_include("common/legendary_weather.inc")
    h_call_if_set FLAG_SYS_WEATHER_CTRL, Common_SetLegendaryWeather     // chapter Ch10's (Kyogre's rain)
#endif
    h_setup_rival_gfx
#ifdef HOENN_TEST_CH8A
    VMCall Test_Ch8aStart
#endif
    // LilycoveCity_OnLoad: SetWailmerMetatiles = the three Wailmer in the cove (Black 2's Wailmer objects in
    // data/story/ch8a.json, hidden by FLAG_EVIL_TEAM_ESCAPED_IN_SUBMARINE). RemoveEvilTeamBaseEntrance (Mind Badge):
    // Sapphire walls the cave mouth up; the mouth is terrain here, so its door is moved off the map (Black 2's way to
    // switch a warp off in a zone init, 0240.s ObjInitWarpGPos n, 0, 0, 0)
    h_goto_if_no_badge 7, L_LC_InitDone
    ObjInitWarpGPos LC_HIDEOUT_WARP, 0, 0, 0
L_LC_InitDone:
    VMHalt

// ---- the rival outside the Department Store (LilycoveCity_EventScript_Rival) ----------------------------------------
LC_Rival:
    c3_talk
    h_buffer_player
    h_goto_if_girl L_LC_Brendan
    h_playbgm MUS_ENCOUNTER_MAY                         // playbgm MUS_ENCOUNTER_MAY, TRUE
    h_goto_if_set FLAG_DECLINED_RIVAL_BATTLE_LILYCOVE, L_LC_MayAskAgain
    h_yesno T_MayShopping, C8_A                         // May: Oh, hey? <player>, are you shopping, too? ...
    VMJump L_LC_MayAnswer
L_LC_MayAskAgain:
    h_yesno T_MayBattleMe, C8_A                         // May: Come on, battle with me, ...
L_LC_MayAnswer:
    h_goto_if_no C8_A, L_LC_MayDecline
    h_msgbox T_MayWontBeBeaten
    h_closemessage
    h_goto_if_eq VAR_STARTER_MON, 1, L_LC_MayTorchic
    h_goto_if_eq VAR_STARTER_MON, 2, L_LC_MayMudkip
    h_trainerbattle TRAINER_MAY_LILYCOVE_TREECKO        // (in battle: LilycoveCity_Text_MayDefeat)
    VMJump L_LC_MayWon
L_LC_MayTorchic:
    h_trainerbattle TRAINER_MAY_LILYCOVE_TORCHIC
    VMJump L_LC_MayWon
L_LC_MayMudkip:
    h_trainerbattle TRAINER_MAY_LILYCOVE_MUDKIP
L_LC_MayWon:                                            // LilycoveCity_EventScript_DefeatedMay
    h_buffer_player
    h_msgbox_actor T_MayGoingBack, LC_RIVAL
    VMCall Sub_LC_CheckFinalBadge
    h_goto_if_eq C8_A, 1, L_LC_MayLeague
    h_msgbox_actor T_MayBadges, LC_RIVAL                // MayCollectBadges
    VMJump L_LC_MayDone
L_LC_MayLeague:                                         // MayPokemonLeague
    h_goto_if_set FLAG_SYS_GAME_CLEAR, L_LC_MayTower
    h_msgbox_actor T_MayLeague, LC_RIVAL
    VMJump L_LC_MayDone
L_LC_MayTower:
    h_msgbox_actor T_MayTower, LC_RIVAL
L_LC_MayDone:
    h_clearflag FLAG_HIDE_MAY_UPSTAIRS
    h_clearflag FLAG_HIDE_MAY_PICHU_DOLL
    VMJump L_LC_RivalFlyAway
L_LC_MayDecline:                                        // LilycoveCity_EventScript_DeclineMayBattle
    h_setflag FLAG_DECLINED_RIVAL_BATTLE_LILYCOVE
    h_msgbox T_MayNotRaising
    h_fadedefaultbgm                                    // savebgm 0, fadedefaultbgm
    h_release

L_LC_Brendan:
    h_playbgm MUS_ENCOUNTER_BRENDAN
    h_goto_if_set FLAG_DECLINED_RIVAL_BATTLE_LILYCOVE, L_LC_BrendanAskAgain
    h_yesno T_BrendanShopping, C8_A                     // Brendan: Oh, hey, it's <player>. ...
    VMJump L_LC_BrendanAnswer
L_LC_BrendanAskAgain:
    h_yesno T_BrendanBattleMe, C8_A
L_LC_BrendanAnswer:
    h_goto_if_no C8_A, L_LC_BrendanDecline
    h_msgbox T_BrendanWontBeBeaten
    h_closemessage
    h_goto_if_eq VAR_STARTER_MON, 1, L_LC_BrendanTorchic
    h_goto_if_eq VAR_STARTER_MON, 2, L_LC_BrendanMudkip
    h_trainerbattle TRAINER_BRENDAN_LILYCOVE_TREECKO    // (in battle: LilycoveCity_Text_BrendanDefeat)
    VMJump L_LC_BrendanWon
L_LC_BrendanTorchic:
    h_trainerbattle TRAINER_BRENDAN_LILYCOVE_TORCHIC
    VMJump L_LC_BrendanWon
L_LC_BrendanMudkip:
    h_trainerbattle TRAINER_BRENDAN_LILYCOVE_MUDKIP
L_LC_BrendanWon:                                        // LilycoveCity_EventScript_DefeatedBrendan
    h_buffer_player
    h_msgbox_actor T_BrendanGoingBack, LC_RIVAL
    VMCall Sub_LC_CheckFinalBadge
    h_goto_if_eq C8_A, 1, L_LC_BrendanLeague
    h_msgbox_actor T_BrendanBadges, LC_RIVAL
    VMJump L_LC_BrendanDone
L_LC_BrendanLeague:
    h_goto_if_set FLAG_SYS_GAME_CLEAR, L_LC_BrendanTower
    h_msgbox_actor T_BrendanLeague, LC_RIVAL
    VMJump L_LC_BrendanDone
L_LC_BrendanTower:
    h_msgbox_actor T_BrendanTower, LC_RIVAL
L_LC_BrendanDone:
    h_clearflag FLAG_HIDE_BRENDAN_UPSTAIRS
    VMJump L_LC_RivalFlyAway
L_LC_BrendanDecline:                                    // LilycoveCity_EventScript_DeclineBrendanBattle
    h_setflag FLAG_DECLINED_RIVAL_BATTLE_LILYCOVE
    h_msgbox T_BrendanNoConfidence
    h_fadedefaultbgm
    h_release

L_LC_RivalFlyAway:                                      // LilycoveCity_EventScript_RivalFlyAway
    h_closemessage
    h_move LC_RIVAL, 41                                 // walk_in_place_fastest_down
    h_delay 50
    c8_npc_fly_out LC_RIVAL, FLAG_HIDE_RIVAL_LILYCOVE_MART   // dofieldeffect FLDEFF_NPCFLY_OUT, removeobject
    h_fadedefaultbgm
    h_setflag FLAG_MET_RIVAL_LILYCOVE
    h_release

Sub_LC_CheckFinalBadge:                                 // C8_A = 1 with the Feather Badge and the Rain Badge
    h_setvar C8_A, 0                                    // (LilycoveCity_EventScript_CheckFinalBadge), else 0
    h_goto_if_no_badge 6, L_LC_CheckDone
    h_goto_if_no_badge 8, L_LC_CheckDone
    h_setvar C8_A, 1
L_LC_CheckDone:
    VMReturn

// ---- Team Aqua ---------------------------------------------------------------------------------------------------
LC_WailmerGrunt:                                        // LilycoveCity_EventScript_WailmerTrainerGrunt (lockall: he
    h_lock                                              // calls to his Wailmer first, then turns)
    SEPlay SEQ_SE_MESSAGE
    h_goto_if_set FLAG_MET_WAILMER_TRAINER, L_LC_MetWailmerTrainer
    h_msgbox_actor T_WailmerLeap, LC_WAILMER_GRUNT      // There! Wailmer! Leap out of the water now!
    h_closemessage
    h_faceplayer                                        // Common_Movement_FacePlayer
    h_msgbox_actor T_GetLost, LC_WAILMER_GRUNT
    h_closemessage
    h_turnobject LC_WAILMER_GRUNT, 3                    // Common_Movement_FaceOriginalDirection (FACE_RIGHT)
    h_setflag FLAG_MET_WAILMER_TRAINER
    h_release
L_LC_MetWailmerTrainer:
    h_msgbox_actor T_WailmerLeap, LC_WAILMER_GRUNT
    h_release
LC_Grunt1:
    h_msgbox_npc T_MovedLoot
LC_Grunt2:
    h_msgbox_npc T_BigThings
LC_Grunt3:
    h_msgbox_npc T_DontGoNear
LC_Grunt4:
    h_msgbox_npc T_IfWorldOurs

// ---- townspeople -------------------------------------------------------------------------------------------------
LC_Sailor2:                                             // LilycoveCity_EventScript_Sailor2
    c8_say_if_set FLAG_EVIL_TEAM_ESCAPED_IN_SUBMARINE, T_SomeonePunted, T_TrainingWailmer
LC_Girl:                                                // LilycoveCity_EventScript_Girl
    c8_say_if_badge 7, T_MoveDeleterHMs, T_StrangeCave
LC_Woman2:                                              // LilycoveCity_EventScript_Woman2
    c8_say_if_set FLAG_EVIL_TEAM_ESCAPED_IN_SUBMARINE, T_MissingCameBack, T_SomeoneStole
LC_ExpertM2:                                            // LilycoveCity_EventScript_ExpertM2
    c8_say_if_badge 7, T_GoneForGood, T_Renovated

LC_BerryGentleman:                                      // LilycoveCity_EventScript_BerryGentleman (dotimebasedevents:
    c3_talk                                             // Black 2 resets FLAG_DAILY_* at midnight itself)
    h_goto_if_set FLAG_DAILY_RECEIVED_BERRY_LILYCOVE, L_LC_ReceivedBerry
    h_msgbox T_BerrySuitsYou
    h_closemessage
    h_random C8_A, 10                                   // random 10, addvar VAR_RESULT, ITEM_CHERI_BERRY: Cheri ...
    h_addvar C8_A, ITEM_CHERI_BERRY                     // Sitrus Berry (Black 2 keeps Gen 3's Berry order, 149-158)
    c8_giveitem_var C8_A
    h_goto_if_eq HLIB_RESULT, 0, L_LC_BagFull
    h_setflag FLAG_DAILY_RECEIVED_BERRY_LILYCOVE
    h_msgbox T_BecauseTrainer
    h_release
L_LC_ReceivedBerry:
    h_msgbox T_PokeblocksSuit
    h_release
L_LC_BagFull:                                           // Common_EventScript_ShowBagIsFull
    h_bag_is_full T_BagFull
    h_release

// ---- signs -------------------------------------------------------------------------------------------------------
LC_MuseumSign:                                          // LilycoveCity_EventScript_MuseumSign: CountPlayerMuseumPaintings
    h_lock                                              // = the contest painting flags (Contests: decided later, so
    SEPlay SEQ_SE_MESSAGE                               // 0 until then)
    h_buffer_player
    h_goto_if_set FLAG_COOL_PAINTING_MADE, L_LC_PlayersExhibit
    h_goto_if_set FLAG_BEAUTY_PAINTING_MADE, L_LC_PlayersExhibit
    h_goto_if_set FLAG_CUTE_PAINTING_MADE, L_LC_PlayersExhibit
    h_goto_if_set FLAG_SMART_PAINTING_MADE, L_LC_PlayersExhibit
    h_goto_if_set FLAG_TOUGH_PAINTING_MADE, L_LC_PlayersExhibit
    MsgPlaceSign T_MuseumSign, 2
    VMJump L_LC_SignEnd
L_LC_PlayersExhibit:
    MsgPlaceSign T_MuseumSignPlayers, 2
L_LC_SignEnd:
    MsgPlaceSignClose
    h_release

LC_HarborSign:                                          // LilycoveCity_EventScript_HarborSign
    h_lock
    SEPlay SEQ_SE_MESSAGE
    h_goto_if_set FLAG_SYS_GAME_CLEAR, L_LC_HarborFerryReady
    MsgPlaceSign T_HarborUnderConstruction, 2
    VMJump L_LC_SignEnd
L_LC_HarborFerryReady:
    MsgPlaceSign T_HarborSign, 2
    VMJump L_LC_SignEnd

#if __has_include("common/legendary_weather.inc")
#include "common/legendary_weather.inc"
#endif

#ifdef HOENN_TEST_CH8A
#include "scenes/ch8a_test.inc"
#endif
#endif
