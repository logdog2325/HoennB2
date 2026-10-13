// MauvilleCity_BikeShop (zone 236): Sapphire's simple people and signs (as converter/gen_interiors.py makes them),
// plus people that turn back after their message (Common_Movement_FaceOriginalDirection), by the specials agent
// (b2tools/specials.py people). Messages: src/text/script/0301_room_MauvilleCity_BikeShop.txt
#include "asm/field_script.inc"
#include "hoenn.h"  // ch3b
#include "hoenn_trainers.h"  // ch3b
#include "hoenn_story.inc"  // ch3b
#include "scenes/ch3b_lib.inc"  // ch3b

    ScriptEntry Script_1
    ScriptEntry BS_Rydel            // 2: MauvilleCity_BikeShop_EventScript_Rydel  // story:
    ScriptEntry BS_MachHandbook     // 3: sign (8,1)  // story:
    ScriptEntry BS_AcroHandbook     // 4: sign (11,1)  // story:
    ScriptEntriesEnd

Script_1:
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    ActorSetEyeToEye
    ParentActorMsg MSGFILE_SCRIPT, 0, 0, 0
    LastKeyWait
    ActorMsgClose
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt
    .balign 4, 0

// ---- story (chapter Ch3 part 3b, ch3b agent 2026-10-07: Sapphire data/maps/MauvilleCity_BikeShop/scripts.inc;
// generators must keep everything from this line on; entries above marked "// story:"). Rydel (uid 1) and the two
// handbooks are in data/story/ch3b.json; text lines 1-22 of 0301 (line 0 is the assistant's).
// One bike (user decision 2026-10-06): Rydel gives the Mach Bike (= Black 2's Bicycle, ITEM_MACH_BIKE). His
// explanation of the two kinds is Sapphire's own line; the choice that follows offers the Mach Bike only, and the
// switching (MauvilleCity_BikeShop_EventScript_ComeBackToSwitchBikes, AskSwitchBikes, SwapRegisteredBike) is left out:
// with the bike he answers as Sapphire does when you keep yours ("Good, good! I'm happy that you like it!").
#define T_RydelGreeting 1
#define T_FarAway 2
#define T_NoNeedBike 3
#define T_ExplainBikes 4
#define T_Mach 5
#define T_ChoseMach 6
#define T_HappyYouLikeIt 7
#define T_MachWhichPage 8
#define T_HowToRide 9
#define T_HowToTurn 10
#define T_SandySlopes 11
#define T_Cancel 12
#define T_RidePage 13
#define T_TurnPage 14
#define T_SlopesPage 15
#define T_AcroWhichPage 16
#define T_Wheelies 17
#define T_BunnyHops 18
#define T_Jumping 19
#define T_WheeliesPage 20
#define T_BunnyHopsPage 21
#define T_JumpsPage 22

BS_Rydel:                           // MauvilleCity_BikeShop_EventScript_Rydel
    c3_talk
    h_goto_if_set FLAG_RECEIVED_BIKE, L_BS_KeepBike
    h_goto_if_set FLAG_DECLINED_BIKE, L_BS_SkipGreeting
    h_msgbox T_RydelGreeting        // Well, well, what have we here? A most energetic customer! ...
L_BS_SkipGreeting:
    h_yesno T_FarAway, C3B_A        // Rydel: Your Running Shoes... They're awfully filthy. Did you come from far away?
    h_goto_if_yes C3B_A, L_BS_YesFar
    h_setflag FLAG_DECLINED_BIKE    // MauvilleCity_BikeShop_EventScript_NotFar
    h_msgbox T_NoNeedBike           // Rydel: Is that right? Then, I guess you have no need for any of my Bikes.
    h_release
L_BS_YesFar:                        // MauvilleCity_BikeShop_EventScript_YesFar
    h_setflag FLAG_RECEIVED_BIKE
    ParentActorMsg MSGFILE_SCRIPT, T_ExplainBikes, 0, 0     // message + waitmessage: the choice opens under it
    ListMenu_AnchorTopRight 31, 9, 0, 0, C3B_SEL            // multichoice 21, 8, 12, 1 (B does nothing)
    ListMenuAdd T_Mach, 65535, 0
    ListMenuShow
    h_buffer_player
    h_msgbox T_ChoseMach            // <player> chose the Mach Bike. (MauvilleCity_BikeShop_EventScript_GetMachBike)
    h_closemessage
    h_giveitem ITEM_MACH_BIKE
    h_release
L_BS_KeepBike:                      // MauvilleCity_BikeShop_EventScript_KeepBike
    h_msgbox T_HappyYouLikeIt
    h_release

BS_MachHandbook:                    // MauvilleCity_BikeShop_EventScript_MachBikeHandbook (no lock: a sign)
    h_lock
    SEPlay SEQ_SE_MESSAGE
    SystemMsg T_MachWhichPage, 2    // It's a handbook on the Mach Bike. Which page do you want to read?
L_BS_MachMenu:                      // multichoice 0, 0, 43, 0 (B = Cancel)
    ListMenu_AnchorTopRight 31, 1, 0, 1, C3B_SEL
    ListMenuAdd T_HowToRide, 65535, 0
    ListMenuAdd T_HowToTurn, 65535, 1
    ListMenuAdd T_SandySlopes, 65535, 2
    ListMenuAdd T_Cancel, 65535, 3
    ListMenuShow
    h_goto_if_eq C3B_SEL, 0, L_BS_HowToRide
    h_goto_if_eq C3B_SEL, 1, L_BS_HowToTurn
    h_goto_if_eq C3B_SEL, 2, L_BS_SandySlopes
    h_release
L_BS_HowToRide:
    SystemMsg T_RidePage, 2         // ... Want to read a different page?
    VMJump L_BS_MachMenu
L_BS_HowToTurn:
    SystemMsg T_TurnPage, 2
    VMJump L_BS_MachMenu
L_BS_SandySlopes:
    SystemMsg T_SlopesPage, 2
    VMJump L_BS_MachMenu

BS_AcroHandbook:                    // MauvilleCity_BikeShop_EventScript_AcroBikeHandbook
    h_lock
    SEPlay SEQ_SE_MESSAGE
    SystemMsg T_AcroWhichPage, 2    // It's a handbook on the Acro Bike. Which page do you want to read?
L_BS_AcroMenu:                      // multichoice 0, 0, 44, 0
    ListMenu_AnchorTopRight 31, 1, 0, 1, C3B_SEL
    ListMenuAdd T_Wheelies, 65535, 0
    ListMenuAdd T_BunnyHops, 65535, 1
    ListMenuAdd T_Jumping, 65535, 2
    ListMenuAdd T_Cancel, 65535, 3
    ListMenuShow
    h_goto_if_eq C3B_SEL, 0, L_BS_Wheelies
    h_goto_if_eq C3B_SEL, 1, L_BS_BunnyHops
    h_goto_if_eq C3B_SEL, 2, L_BS_Jumps
    h_release
L_BS_Wheelies:
    SystemMsg T_WheeliesPage, 2
    VMJump L_BS_AcroMenu
L_BS_BunnyHops:
    SystemMsg T_BunnyHopsPage, 2
    VMJump L_BS_AcroMenu
L_BS_Jumps:
    SystemMsg T_JumpsPage, 2
    VMJump L_BS_AcroMenu
    .balign 4, 0
