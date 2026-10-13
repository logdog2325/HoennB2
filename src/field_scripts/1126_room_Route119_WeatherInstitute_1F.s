// Route119_WeatherInstitute_1F (zone 563): Sapphire's simple people and signs (as converter/gen_interiors.py makes them),
// plus people that turn back after their message (Common_Movement_FaceOriginalDirection), by the specials agent
// (b2tools/specials.py people). Messages: src/text/script/0364_room_Route119_WeatherInstitute_1F.txt
#include "asm/field_script.inc"
#include "hoenn.h"  // ch7
#include "hoenn_trainers.h"  // ch7
#include "hoenn_story.inc"  // ch7

    ScriptEntry Script_None
    ScriptEntry WI1_WorkerSaved  // 2: Route119_WeatherInstitute_1F_EventScript_163C7A  // story:
    ScriptEntry WI1_WorkerProfessor  // 3: Route119_WeatherInstitute_1F_EventScript_163C71  // story:
    ScriptEntry WI1_Boy  // 4: Route119_WeatherInstitute_1F_EventScript_163C4D  // story:
    ScriptEntry WI1_Bed  // 5: Route119_WeatherInstitute_1F_EventScript_163C83 (the four bed tiles)  // story:
    ScriptEntry WI1_Init  // 6: Route119_WeatherInstitute_1F_MapScript1_163C30 (zone init)  // story:
    ScriptEntriesEnd

Script_None:
    VMHalt
    .balign 4, 0

// ---- story (chapter Ch7, ch7 agent 2026-10-07; Sapphire data/maps/Route119_WeatherInstitute_1F/scripts.inc; generators must
// keep everything from this line on). Scripts 2-6, text lines 1-5 (line 0 is the generator's). People, the bed
// tiles and the two Team Aqua grunts (uids 1 and 2: Black 2's eye-contact trainer script 3000 + id; hidden by
// FLAG_HIDE_EVIL_TEAM_WEATHER_INSTITUTE) are in data/story/ch7.json; the map script (zone init) is
// 1127_room_Route119_WeatherInstitute_1F_init.s. Room tiles = Sapphire tiles + (1,1).
// The boy: Sapphire moves object 5 to the bed ((0,5), face right) while VAR_WEATHER_INSTITUTE_STATE is 0 and lets him
// wander otherwise; Black 2 cannot change an NPC's movement, so there are two boys (uid 5 wanders, uid 15 sleeps) and
// the zone init hides the one that does not belong: FLAG_HIDE_WEATHER_INSTITUTE_BOY (new, ch7) hides the wanderer.
#include "scenes/ch7_lib.inc"
#include "scenes/ch7_test.inc"        // (test builds only: HOENN_TEST_CH7)
#define T_Saved 1
#define T_Professor 2
#define T_BoyAsleep 3
#define T_BoyStrong 4
#define T_Bed 5

WI1_Init:                           // Route119_WeatherInstitute_1F_MapScript1_163C30 (SetupEvilTeamGfxIds: nothing to do)
#ifdef HOENN_TEST_CH7
    VMCall Test_Ch7Start
#endif
    h_goto_if_eq VAR_WEATHER_INSTITUTE_STATE, 0, L_WI1_AquaHere
    h_clearflag FLAG_HIDE_WEATHER_INSTITUTE_BOY
    VMHalt
L_WI1_AquaHere:
    h_setflag FLAG_HIDE_WEATHER_INSTITUTE_BOY
    VMHalt

WI1_WorkerSaved:                    // Route119_WeatherInstitute_1F_EventScript_163C7A (MSGBOX_NPC)
    h_msgbox_npc T_Saved            // Hello! We've been saved by your actions! ...
WI1_WorkerProfessor:                // Route119_WeatherInstitute_1F_EventScript_163C71 (MSGBOX_NPC)
    h_msgbox_npc T_Professor        // The Professor loves rain. That's a fact. ...

WI1_Boy:                            // Route119_WeatherInstitute_1F_EventScript_163C4D
    c7_talk
    h_goto_if_eq VAR_WEATHER_INSTITUTE_STATE, 0, L_WI1_BoyAsleep
    h_msgbox T_BoyStrong            // Wow, you're really strong! I wish I could be a Pokémon Trainer like you!
    h_release
L_WI1_BoyAsleep:
    h_msgbox T_BoyAsleep            // While I was sleeping, everyone went upstairs!
    h_release

WI1_Bed:                            // Route119_WeatherInstitute_1F_EventScript_163C83 (lockall)
    h_lock
    SEPlay SEQ_SE_MESSAGE
    MsgPlaceSign T_Bed, 2           // There's a bed... Let's take a rest. (a signboard window)
    MsgPlaceSignClose
    h_heal_party_fade               // Common_EventScript_OutOfCenterPartyHeal
    h_release
    .balign 4, 0
