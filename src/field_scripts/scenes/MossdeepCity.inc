// Mossdeep City's story (Sapphire data/maps/MossdeepCity/scripts.inc; chapter Ch9, ch9 agent 2026-10-07).
// converter/gen_map_content.py includes this file twice in 0214_auto_MossdeepCity.s: the entries below are scripts
// 1-3, the generated signs/people follow. Text: src/text/scenes/MossdeepCity.txt (T_* below).
// People: data/story/ch9.json (uid 200 + Sapphire local id here, 100 + elsewhere: the man on the north shore 207, the boy
// with the King's Rock 209). The other people and the signs are the generator's (Sapphire's one-message scripts).
// Zone init (scenes/MossdeepCity_init.inc) = script 1: Sapphire's MossdeepCity_OnTransition (the four Gym switch flags
// clear, Kyogre's weather) and MossdeepCity_EventScript_VisitedMossdeep. The latter is a coord event on the four
// tiles of the south entrance ((25,25), (26,25), (32,27), (33,27)) that only sets FLAG_VISITED_MOSSDEEP_CITY (the fly
// point) and VAR_TEMP_1; every other chapter's town sets its flag in the zone init (scenes/SlateportCity.inc), so
// does this one.
// Also here: the start day for the Space Center's launch counter (see MossdeepCity_SpaceCenter_1F's file).
#ifdef SCENE_ENTRIES
    ScriptEntry MD_Init                 // 1: MossdeepCity_OnTransition (zone init)
    ScriptEntry MD_Man                  // 2: object 7 (MossdeepCity_EventScript_Man)
    ScriptEntry MD_KingsRockBoy         // 3: object 9 (MossdeepCity_EventScript_KingsRockBoy)
#ifdef HOENN_EMERALD
    ScriptEntry MD_EmMagmaEnter         // 4: the six coord events (VAR_MOSSDEEP_CITY_STATE 1): Maxie and the grunts walk off to the Space Center
    ScriptEntry MD_EmScott              // 5: Scott (MossdeepCity_EventScript_Scott)
    ScriptEntry MD_EmSailor             // 6: the Sailor (MossdeepCity_EventScript_Sailor)
    ScriptEntry MD_EmPokefanF           // 7: the Pokefan F (MossdeepCity_EventScript_PokefanF)
#endif
#else
#define C9_DAYS
#include "scenes/ch9_lib.inc"

// text lines (src/text/scenes/MossdeepCity.txt)
#define T_SurfExhilarating 0
#define T_WantKingsRock 1
#define T_YouCanKeepIt 2
#define T_CollectingRocks 3
#define T_WhatToDoWithWeirdRock 4
#define T_BagFull 5

#define MD_MAN 207                      // object 7 (FACE_UP); uid 207: the trainers patch holds uid 107 in this zone
#define MD_MAN_DIR 0

MD_Init:                                // MossdeepCity_OnTransition
#ifdef HOENN_TEST_CH9
    VMCall Test_Ch9Start                // test builds only (scenes/ch9_test.inc)
#endif
    h_setflag FLAG_VISITED_MOSSDEEP_CITY    // MossdeepCity_EventScript_VisitedMossdeep
    h_clearflag FLAG_MOSSDEEP_GYM_SWITCH_1
    h_clearflag FLAG_MOSSDEEP_GYM_SWITCH_2
    h_clearflag FLAG_MOSSDEEP_GYM_SWITCH_3
    h_clearflag FLAG_MOSSDEEP_GYM_SWITCH_4
#if __has_include("common/legendary_weather.inc")
    h_call_if_set FLAG_SYS_WEATHER_CTRL, Common_SetLegendaryWeather     // chapter Ch10's (Kyogre's rain)
#endif
    // GetWeekCount (the Space Center's rocket counter, Sapphire: weeks since the clock was set) starts counting at the
    // first visit here: Black 2's scripts can read the date but the new game did not store one
    h_goto_if_ne VAR_MOSSDEEP_SPACE_CENTER_START_DAY, 0, L_MD_DayKnown
    VMCall C9_TodayOfYear
    h_copyvar VAR_MOSSDEEP_SPACE_CENTER_START_DAY, C9_TODAY
L_MD_DayKnown:
    VMHalt

MD_Man:                                 // MossdeepCity_EventScript_Man
    c9_talk
    h_msgbox T_SurfExhilarating
    h_closemessage
    h_turnobject MD_MAN, MD_MAN_DIR     // Common_Movement_FaceOriginalDirection
    h_release

MD_KingsRockBoy:                        // MossdeepCity_EventScript_KingsRockBoy
    c9_talk
    h_goto_if_set FLAG_RECEIVED_KINGS_ROCK, L_MD_ReceivedKingsRock
    h_yesno T_WantKingsRock, C9_A       // I got this from Steven, but I don't know what it's good for. ...
    h_goto_if_no C9_A, L_MD_DeclineKingsRock
    h_msgbox T_YouCanKeepIt             // Why would you want it? You're weird. ...
    h_closemessage                      // (Black 2: the item script opens its own window)
    h_giveitem ITEM_KINGS_ROCK
    h_goto_if_eq HLIB_RESULT, 0, L_MD_BagFull
    h_setflag FLAG_RECEIVED_KINGS_ROCK
    h_release
L_MD_ReceivedKingsRock:
    h_msgbox T_CollectingRocks          // Is it really that fun collecting rocks? I don't get it.
    h_release
L_MD_DeclineKingsRock:
    h_msgbox T_WhatToDoWithWeirdRock    // Yeah, you think so, too! What are you supposed to do with some weird rock?
    h_release
L_MD_BagFull:                           // Common_EventScript_ShowBagIsFull
    h_bag_is_full T_BagFull
    h_release

#ifdef HOENN_EMERALD
#include "scenes/emerald/MossdeepCity_Magma.inc"     // Emerald's Space Center story outside (emerald_ch9_mirage): scripts 4-7 above
#endif
#if __has_include("common/legendary_weather.inc")
#include "common/legendary_weather.inc"          // Common_SetLegendaryWeather (chapter Ch10's; the call in MD_Init needs its label)
#endif
#ifdef HOENN_TEST_CH9
#include "scenes/ch9_test.inc"
#endif
#if __has_include("common/legendary_weather.inc")
#include "common/legendary_weather.inc"
#endif
#endif
