// Slateport City's story (Sapphire data/maps/SlateportCity/scripts.inc; chapter Ch3, part 3a, ch3a agent 2026-10-07).
// converter/gen_map_content.py includes this file twice in 0896_auto_SlateportCity.s: the entries below are scripts
// 1-28, the generated signs/people follow. Text: src/text/scenes/SlateportCity.txt (lines T_* below; other chapters
// append theirs after line 47). People and signs: data/story/ch3a.json (outdoor uid = 100 + Sapphire local id).
// Map scripts: scenes/SlateportCity_init.inc (zone init = script 1).
// Other chapters' beats in this file (notes/STORY_CHAPTERS.md): Ch8 (Capt. Stern's TV interview, Gabby and Ty) gets
// scripts 26-28: write them in scenes/SlateportCity_Ch8.inc (labels Ch8_CaptStern, Ch8_Ty, Ch8_Gabby), it is picked
// up automatically; until it exists, Ty and Gabby say Sapphire's lines and Stern does nothing. Their objects are in
// data/story/ch3a.json already (hidden by FLAG_HIDE_STERN_SLATEPORT / FLAG_HIDE_GABBY_AND_TY_SLATEPORT).
#ifdef SCENE_ENTRIES
    ScriptEntry Story_Init              // 1: SlateportCity_OnTransition (zone init)
    ScriptEntry Story_EnergyGuru        // 2: object 26
    ScriptEntry Story_EffortRibbonWoman // 3: object 24
    ScriptEntry Story_Cook              // 4: object 6
    ScriptEntry Story_OldWoman          // 5: object 7
    ScriptEntry Story_Girl              // 6: object 8
    ScriptEntry Story_RichBoy           // 7: object 3
    ScriptEntry Story_FatMan            // 8: object 1
    ScriptEntry Story_Man1              // 9: object 2
    ScriptEntry Story_Woman1            // 10: object 4
    ScriptEntry Story_ShipyardSign      // 11: sign (23,38)
    ScriptEntry Story_HarborSign        // 12: sign (24,12)
    ScriptEntry Story_Maniac            // 13: object 17
    ScriptEntry Story_SchoolKid         // 14: object 16
    ScriptEntry Story_Grunt1            // 15: object 5
    ScriptEntry Story_Grunt2            // 16: object 19
    ScriptEntry Story_Grunt3            // 17: object 20
    ScriptEntry Story_Grunt4            // 18: object 27
    ScriptEntry Story_Grunt5            // 19: object 28
    ScriptEntry Story_Grunt6            // 20: object 29
    ScriptEntry Story_Grunt7            // 21: object 30
    ScriptEntry Story_Grunt8            // 22: object 31
    ScriptEntry Story_DollClerk         // 23: object 22
    ScriptEntry Story_DecorClerk        // 24: object 21
    ScriptEntry Story_PowerTMClerk      // 25: object 25
    ScriptEntry Ch8_CaptStern           // 26: object 11 (Ch8)
    ScriptEntry Ch8_Ty                  // 27: object 9 (Ch8)
    ScriptEntry Ch8_Gabby               // 28: object 10 (Ch8)
#ifdef HOENN_EMERALD                // Emerald-only entries go last (notes/EMERALD_STORY.md 2.4.1); bodies: scenes/emerald/SlateportCity.inc
    ScriptEntry Em_SC_ScottScene        // 29: OnFrame VAR_SLATEPORT_OUTSIDE_MUSEUM_STATE 1: Scott outside the Museum (Ch3)
    ScriptEntry Em_SC_Grunt9            // 30: queue grunt 9 (26, 27): reads the sign for you
    ScriptEntry Em_SC_Grunt10           // 31: queue grunt 10 (28, 27)
    ScriptEntry Em_SC_Grunt11           // 32: queue grunt 11 (25, 27)
#endif
#else
#include "scenes/ch3_lib.inc"

// text lines (src/text/scenes/SlateportCity.txt)
#define T_EnergyGuru 0
#define T_MartBuy 1
#define T_MartSell 2
#define T_MartQuit 3
#define T_MartAnythingElse 4
#define T_PleaseComeAgain 5
#define T_HowMayIServeYou 6
#define T_OhYourPokemon 7
#define T_EffortRibbonLooksGood 8
#define T_GoForItLittleHarder 9
#define T_PleaseGiveEffortRibbon 10
#define T_ReceivedEffortRibbon 11
#define T_PutEffortRibbon 12
#define T_SeaweedFullOfLife 13
#define T_CaptainBigFish 14
#define T_HowTownIsBorn 15
#define T_SternBeingInterviewed 16
#define T_WonderfulPlace 17
#define T_InterviewerSoCool 18
#define T_BuyBricks 19
#define T_GoingToCompete 20
#define T_SternDiscovered 21
#define T_Bushed 22
#define T_AmIOnTV 23
#define T_CaptStern 24
#define T_CaptainCelebrity 25
#define T_LongLine 26
#define T_VisitedMuseum 27
#define T_ShipyardWanted 28
#define T_ShipyardNears 29
#define T_ShipyardComplete 30
#define T_HarborUnderConstruction 31
#define T_HarborSign 32
#define T_NameRater 33
#define T_BerryBlender 34
#define T_FasterSpin 35
#define T_ExplainBlender 36
#define T_QuitPushing 37
#define T_HasPolicy 38
#define T_BossBrilliant 39
#define T_NewScheme 40
#define T_TakeItAll 41
#define T_DontButtIn 42
#define T_LongLineGames 43
#define T_WhyLiningUp 44
#define T_ComeBackSecretPower 45
#define T_BigSmile 46
#define T_Invaluable 47

// shop lists (data/hoenn_shops.json, b2tools/shops_data.py)
#define SHOP_ENERGY_GURU 18                 // SlateportCity_Pokemart_EnergyGuru
#define SHOP_POWER_TMS 19                   // SlateportCity_Pokemart_PowerTMs

// Sapphire's MovePeopleForSternInterview moves people by local id; Black 2's ObjInitNPCGPos takes their index in
// zone 448's NPC list: the 6 generated people (world.json) come first, then data/story/ch3a.json's outdoor people
// in their order there (8 grunts, 5 Market people, then Cook, Old Woman, Girl, Rich Boy, Fat Man, Man 1, Stern, ...:
// indices 6 + 13..19). Checked in the built ROM (work/agents/ch3a/tests/lib.py zone_npcs).
#define SLATEPORT_STORY_NPC0 6
#define SLATEPORT_X(x) (248+(x))          // Sapphire tile -> world tile (b2tools/world.py offset of SlateportCity)
#define SLATEPORT_Z(z) (320+(z))

Story_Init:                                 // SlateportCity_OnTransition (the Aqua sprites are placed directly)
    h_setvar VAR_SLATEPORT_MUSEUM_1F_STATE, 0
    h_setflag FLAG_VISITED_SLATEPORT_CITY   // SlateportCity_EventScript_EnterSlateport
    h_setvar VAR_LINK_CONTEST_ROOM_STATE, 0
    h_setflag FLAG_HIDE_CONTEST_REPORTER_SLATEPORT
    h_goto_if_ne VAR_SLATEPORT_STATE, 1, L_SC_InitDone
    // SlateportCity_EventScript_MovePeopleForSternInterview (setobjectxyperm + setobjectmovementtype: Black 2 sets
    // the place and the facing; the people keep their own movement)
    ObjInitNPCGPos (SLATEPORT_STORY_NPC0+19), 1, SLATEPORT_X(28), 0, SLATEPORT_Z(13)   // Capt. Stern, FACE_DOWN
    ObjInitNPCGPos (SLATEPORT_STORY_NPC0+14), 1, SLATEPORT_X(25), 0, SLATEPORT_Z(13)   // old woman, FACE_DOWN_AND_RIGHT
    ObjInitNPCGPos (SLATEPORT_STORY_NPC0+16), 0, SLATEPORT_X(25), 0, SLATEPORT_Z(14)   // rich boy, FACE_UP_AND_RIGHT
    ObjInitNPCGPos (SLATEPORT_STORY_NPC0+13), 0, SLATEPORT_X(27), 0, SLATEPORT_Z(16)   // cook, FACE_UP
    ObjInitNPCGPos (SLATEPORT_STORY_NPC0+15), 0, SLATEPORT_X(28), 0, SLATEPORT_Z(16)   // girl, FACE_UP
    ObjInitNPCGPos (SLATEPORT_STORY_NPC0+17), 0, SLATEPORT_X(29), 0, SLATEPORT_Z(16)   // fat man, FACE_UP
    ObjInitNPCGPos (SLATEPORT_STORY_NPC0+18), 2, SLATEPORT_X(31), 0, SLATEPORT_Z(14)   // man 1, FACE_LEFT
L_SC_InitDone:
#ifdef HOENN_TEST_CH3A
    VMCall Test_Ch3aStart
#endif
    VMHalt

Story_EnergyGuru:                           // SlateportCity_EventScript_EnergyGuru
    c3_talk
    ParentActorMsg MSGFILE_SCRIPT, T_EnergyGuru, 0, 0   // message + waitmessage: the menu opens under it
    WorkSetConst C3_SHOP, SHOP_ENERGY_GURU
    VMCall Sub_SC_Mart
    h_msgbox T_PleaseComeAgain
    h_release

Story_EffortRibbonWoman:                    // SlateportCity_EventScript_EffortRibbonWoman
    c3_talk
    c3_lead_mon
    WordSetPartyPokeSpecies 1, C3_LEAD      // bufferleadmonspeciesname 0
    h_msgbox T_OhYourPokemon
    h_check_ribbon C3_TMP, C3_LEAD, RIBBON_EFFORT    // LeadMonHasEffortRibbon (story_infra's ribbon macros, 2026-10-07)
    h_goto_if_eq C3_TMP, 1, L_SC_HasEffortRibbon
    PokePartyGetEVTotal C3_TMP, C3_LEAD     // ScrSpecial_AreLeadMonEVsMaxedOut: EV total >= 510
    WorkCmpConst C3_TMP, 510
    VMJumpIf CMP_LT, L_SC_EVsNotMaxed
    h_msgbox T_PleaseGiveEffortRibbon
    h_closemessage
    h_playfanfare MUS_OBTAIN_ITEM
    WordSetPlayerName 0
    SystemMsg T_ReceivedEffortRibbon, 2     // message ReceivedEffortRibbon (nobody says it)
    h_waitfanfare
    LastKeyWait
    MsgWinCloseAll
    h_msgbox_info T_PutEffortRibbon
    h_give_ribbon C3_LEAD, RIBBON_EFFORT            // special GivLeadMonEffortRibbon (+ FLAG_SYS_RIBBON_GET)
    h_setflag FLAG_SYS_RIBBON_GET
    h_release
L_SC_HasEffortRibbon:                           // SlateportCity_EventScript_MonHasEffortRibbon
    h_msgbox T_EffortRibbonLooksGood
    h_release
L_SC_EVsNotMaxed:
    h_msgbox T_GoForItLittleHarder
    h_release

Story_Cook:                                 // SlateportCity_EventScript_Cook
    c3_talk
    h_goto_if_eq VAR_SLATEPORT_STATE, 1, L_SC_CookInterview
    h_msgbox T_SeaweedFullOfLife
    h_release
L_SC_CookInterview:
    h_msgbox T_CaptainBigFish
    h_release

Story_OldWoman:                             // SlateportCity_EventScript_OldWoman
    c3_talk
    h_goto_if_eq VAR_SLATEPORT_STATE, 1, L_SC_OldWomanInterview
    h_msgbox T_HowTownIsBorn
    h_release
L_SC_OldWomanInterview:
    h_msgbox T_SternBeingInterviewed
    h_release

Story_Girl:                                 // SlateportCity_EventScript_Girl
    c3_talk
    h_goto_if_eq VAR_SLATEPORT_STATE, 1, L_SC_GirlInterview
    h_goto_if_set FLAG_RECEIVED_SECRET_POWER, L_SC_GirlSecretBase
    h_msgbox T_WonderfulPlace
    h_release
L_SC_GirlInterview:
    h_msgbox T_InterviewerSoCool
    h_release
L_SC_GirlSecretBase:
    h_msgbox T_BuyBricks
    h_release

Story_RichBoy:                              // SlateportCity_EventScript_RichBoy
    c3_talk
    h_goto_if_eq VAR_SLATEPORT_STATE, 1, L_SC_RichBoyInterview
    h_msgbox T_GoingToCompete
    h_release
L_SC_RichBoyInterview:
    h_msgbox T_SternDiscovered
    h_release

Story_FatMan:                               // SlateportCity_EventScript_FatMan
    h_goto_if_eq VAR_SLATEPORT_STATE, 1, L_SC_FatManInterview
    h_msgbox_npc T_Bushed
L_SC_FatManInterview:
    h_msgbox_sign T_AmIOnTV                 // MSGBOX_SIGN: he doesn't turn to the player

Story_Man1:                                 // SlateportCity_EventScript_Man1
    c3_talk
    h_goto_if_eq VAR_SLATEPORT_STATE, 1, L_SC_Man1Interview
    h_msgbox T_CaptStern
    h_release
L_SC_Man1Interview:
    h_msgbox T_CaptainCelebrity
    h_release

Story_Woman1:                               // SlateportCity_EventScript_Woman1
    c3_talk
    h_goto_if_set FLAG_DOCK_REJECTED_DEVON_GOODS, L_SC_Woman1EvilTeamGone
    h_msgbox T_LongLine
    h_release
L_SC_Woman1EvilTeamGone:
    h_msgbox T_VisitedMuseum
    h_release

Story_ShipyardSign:                         // SlateportCity_EventScript_SternsShipyardSign
    ActorsPauseAll
    SEPlay SEQ_SE_MESSAGE
    h_goto_if_set FLAG_SYS_GAME_CLEAR, L_SC_ShipyardFerryComplete
    h_goto_if_badge 7, L_SC_ShipyardNearsCompletion
    MsgPlaceSign T_ShipyardWanted, 2
    VMJump L_SC_SignEnd
L_SC_ShipyardNearsCompletion:
    MsgPlaceSign T_ShipyardNears, 2
    VMJump L_SC_SignEnd
L_SC_ShipyardFerryComplete:
    MsgPlaceSign T_ShipyardComplete, 2
L_SC_SignEnd:
    MsgPlaceSignClose
    h_release

Story_HarborSign:                           // SlateportCity_EventScript_HarborSign
    ActorsPauseAll
    SEPlay SEQ_SE_MESSAGE
    h_goto_if_set FLAG_SYS_GAME_CLEAR, L_SC_HarborSignFerryComplete
    MsgPlaceSign T_HarborUnderConstruction, 2
    VMJump L_SC_SignEnd
L_SC_HarborSignFerryComplete:
    MsgPlaceSign T_HarborSign, 2
    VMJump L_SC_SignEnd

Story_Maniac:                               // SlateportCity_EventScript_Maniac (the same line in both states)
    h_msgbox_npc T_NameRater

Story_SchoolKid:                            // SlateportCity_EventScript_SchoolKid
    c3_talk
    h_yesno T_BerryBlender, C3_TMP
    h_goto_if_no C3_TMP, L_SC_ExplainPokeblock
    h_msgbox T_FasterSpin                   // SlateportCity_EventScript_ExplainBerryBlender
    h_release
L_SC_ExplainPokeblock:
    h_msgbox T_ExplainBlender
    h_release

// the Team Aqua line in front of the Museum (they turn back to the queue: Common_Movement_FaceOriginalDirection)
Story_Grunt1:
    c3_say_turn_back T_QuitPushing, 105, 0          // FACE_UP
Story_Grunt2:
    c3_say_turn_back T_HasPolicy, 119, 3            // FACE_RIGHT
Story_Grunt3:
    c3_say_turn_back T_BossBrilliant, 120, 3
Story_Grunt4:
    c3_say_turn_back T_NewScheme, 127, 3
Story_Grunt5:
    c3_say_turn_back T_TakeItAll, 128, 0            // FACE_UP
Story_Grunt6:
    c3_say_turn_back T_DontButtIn, 129, 3
Story_Grunt7:
    c3_say_turn_back T_LongLineGames, 130, 3
Story_Grunt8:
    c3_say_turn_back T_WhyLiningUp, 131, 3

// Slateport Market. Dolls and Secret Base goods: Black 2 has no decorations, so these clerks greet and say goodbye
// selling nothing (decision 2026-10-06, as Lilycove's decoration clerks)
Story_DollClerk:                            // SlateportCity_EventScript_DollClerk (pokemartdecoration: dolls)
    c3_talk
    h_msgbox T_HowMayIServeYou
    h_msgbox T_PleaseComeAgain
    h_release

Story_DecorClerk:                           // SlateportCity_EventScript_DecorClerk (pokemartdecoration: bricks, mats)
    c3_talk
    h_goto_if_unset FLAG_RECEIVED_SECRET_POWER, L_SC_ComeBackWithSecretPower
    h_msgbox T_HowMayIServeYou
    h_msgbox T_PleaseComeAgain
    h_release
L_SC_ComeBackWithSecretPower:
    h_msgbox T_ComeBackSecretPower
    h_release

Story_PowerTMClerk:                         // SlateportCity_EventScript_PowerTMClerk (shown once Secret Power is had)
    c3_talk
    ParentActorMsg MSGFILE_SCRIPT, T_HowMayIServeYou, 0, 0
    WorkSetConst C3_SHOP, SHOP_POWER_TMS
    VMCall Sub_SC_Mart
    h_msgbox T_PleaseComeAgain
    h_release

    c3_mart_sub Sub_SC_Mart, T_MartBuy, T_MartSell, T_MartQuit, T_MartAnythingElse

#if __has_include("scenes/SlateportCity_Ch8.inc")
#include "scenes/SlateportCity_Ch8.inc"
#else
Ch8_CaptStern:                              // SlateportCity_EventScript_CaptStern: Ch8's TV-interview scene
    h_lock
    h_release
Ch8_Ty:                                     // SlateportCity_EventScript_Ty
    h_msgbox_sign T_BigSmile
Ch8_Gabby:                                  // SlateportCity_EventScript_Gabby
    h_msgbox_sign T_Invaluable
#endif

#ifdef HOENN_TEST_CH3A
// TEST ONLY (HOENN_TEST_CH3A=1): Chapter 2's end state on the first arrival in Slateport (with HOENN_TEST_WARP from
// Littleroot's sign and HOENN_TEST_PARTY): badges 1-2, the Devon Goods and Mr. Stone's other story flags, money.
Test_Ch3aStart:
    h_goto_if_set FLAG_DELIVERED_STEVEN_LETTER, L_SC_TestDone
    TrainerCardAddBadge 0
    TrainerCardAddBadge 1
    FlagSet 2414
    FlagSet 2415
    FlagSet FLAG_RECEIVED_POKENAV
    FlagSet FLAG_RECOVERED_DEVON_GOODS
    FlagSet FLAG_RETURNED_DEVON_GOODS
    FlagSet FLAG_DELIVERED_STEVEN_LETTER
    ItemAdd ITEM_DEVON_GOODS, 1, C3_TMP
    MoneyAdd 3000
#if defined(HOENN_EMERALD) && (HOENN_TEST_CH3A + 0) >= 2     // Emerald (emerald_ch0_3): stage 2 = the Museum done, Scott waits outside
    h_setvar VAR_SLATEPORT_OUTSIDE_MUSEUM_STATE, 1
    h_setflag FLAG_DELIVERED_DEVON_GOODS
#endif
L_SC_TestDone:
    VMReturn
#endif
#ifdef HOENN_EMERALD
#include "scenes/emerald/SlateportCity.inc"
#endif
#endif
