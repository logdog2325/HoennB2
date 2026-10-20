// BattleFrontier_ReceptionGate (zone 453; header scripts 906 -> own file 2080), Pokémon Emerald NDS only (frontier_sp,
// 2026-10-20). pokeemerald data/maps/BattleFrontier_ReceptionGate/scripts.inc: the gate between the ferry dock (south,
// exit mat (4,13)) and the Battle Frontier (north, the glass door (4,1)). The greeter, the facility / rules / Frontier
// Pass guides and their menus, and the first visit's scene with Scott. The room: data/interior_layouts/
// BattleFrontier_ReceptionGate.json, people data/interiors/emerald/453.json (uid = script = Emerald's local id; Scott =
// uid 4, hidden by FLAG_HIDE_BATTLE_FRONTIER_RECEPTION_GATE_SCOTT). Messages: src/text/script/emerald/
// 0188_room_BattleFrontier_ReceptionGate.txt (pokeemerald's words in work/agents/frontier_sp/tools/frontier_rooms.py's
// GATE_TEXTS order; lines 32-49 the menu items of src/strings.c).
// Not ported: the Frontier Pass itself (no item in this port: the scene says its lines, the BP and symbols live in
// Black 2's own records, notes/FRONTIER.md) and FLAG_LANDMARK_BATTLE_FRONTIER (no Pokénav landmarks).
// VAR_HAS_ENTERED_BATTLE_FRONTIER (set together with Scott's removeobject) = FLAG_HIDE_..._SCOTT here.
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_story.inc"

#define RG_GREETER 1                        // LOCALID_FRONTIER_RECEPTION_GREETER (0,11)
#define RG_GUIDE 2                          // LOCALID_FRONTIER_RECEPTION_GUIDE (8,11)
#define RG_SCOTT 4                          // LOCALID_FRONTIER_RECEPTION_SCOTT (4,5)
#define RG_PLAYER 255
#define RG_OZ 0                             // room origin (1,0): zone tile = Emerald tile + (1, 0) (built room.json)
#define RG_W_STATE 0x4000                   // map-local work (0 after every map change): the ON_FRAME table runs once
#define RG_SEL 0x8020                       // the menus' choice
#define RG_PX 0x8021
#define RG_PZ 0x8022

#define T_FirstTimeHereThisWay 0
#define T_WelcomeToBattleFrontier 1
#define T_IssueFrontierPass 2
#define T_ObtainedFrontierPass 3
#define T_PlacedTrainerCardInFrontierPass 4
#define T_EnjoyBattleFrontier 5
#define T_IfItIsntPlayerYouCame 6
#define T_OhMrScottGoodDay 7
#define T_ScottGreatToSeeYouHere 8
#define T_YourGuideToFacilities 9
#define T_LearnAboutWhich2 10
#define T_BattleTowerInfo 11                // 11-19: the nine facilities' lines, in the menu's order
#define T_YourGuideToRules 20
#define T_LearnAboutWhat 21
#define T_LevelModeInfo 22                  // 22-26: the five rules
#define T_YourGuideToFrontierPass 27
#define T_LearnAboutWhich1 28
#define T_SymbolsInfo 29                    // 29-31: symbols, recorded battle, Battle Points
#define M_BattleTower 32                    // 32-40: SCROLL_MULTI_BF_RECEPTIONIST's nine places
#define M_Exit 41
#define M_TwoStyles 42                      // 42-46: MULTI_FRONTIER_RULES
#define M_Symbols 47                        // 47-49: MULTI_FRONTIER_PASS_INFO

    ScriptEntry RG_Greeter                  // 1: BattleFrontier_ReceptionGate_EventScript_Greeter
    ScriptEntry RG_FacilityGuide            // 2: _FacilityGuide
    ScriptEntry RG_RulesGuide               // 3: _RulesGuide
    ScriptEntry RG_Scott                    // 4: Scott (no script in Emerald)
    ScriptEntry RG_PassGuide                // 5: _FrontierPassGuide
    ScriptEntry RG_OnFrame                  // 6: ON_FRAME (map-script condition RG_W_STATE 0): _FirstTimeEntering
    ScriptEntriesEnd

RG_Greeter:
    h_lock
    SEPlay SEQ_SE_MESSAGE
    h_faceplayer
    h_msgbox T_WelcomeToBattleFrontier
    h_msgbox T_EnjoyBattleFrontier
    h_release

RG_FacilityGuide:
    h_lock
    SEPlay SEQ_SE_MESSAGE
    h_faceplayer
    h_msgbox T_YourGuideToFacilities
L_RG_Facilities:                            // _ChooseFacilityToLearnAbout: message + ShowScrollableMultichoice
    ParentActorMsg MSGFILE_SCRIPT, T_LearnAboutWhich2, 0, 0
    ListMenu_AnchorTopRight 31, 1, 0, 1, RG_SEL
    ListMenuAdd M_BattleTower + 0, 65535, 0
    ListMenuAdd M_BattleTower + 1, 65535, 1
    ListMenuAdd M_BattleTower + 2, 65535, 2
    ListMenuAdd M_BattleTower + 3, 65535, 3
    ListMenuAdd M_BattleTower + 4, 65535, 4
    ListMenuAdd M_BattleTower + 5, 65535, 5
    ListMenuAdd M_BattleTower + 6, 65535, 6
    ListMenuAdd M_BattleTower + 7, 65535, 7
    ListMenuAdd M_BattleTower + 8, 65535, 8
    ListMenuAdd M_Exit, 65535, 9
    ListMenuShow
    h_goto_if_ge RG_SEL, 9, L_RG_Bye        // EXIT, B (65534)
    WorkSet RG_PX, RG_SEL
    WorkAdd RG_PX, T_BattleTowerInfo
    ParentActorMsg MSGFILE_SCRIPT, RG_PX, 0, 0     // (a work as the line: as the Pike's three-path room)
    LastKeyWait
    VMJump L_RG_Facilities

RG_RulesGuide:
    h_lock
    SEPlay SEQ_SE_MESSAGE
    h_faceplayer
    h_msgbox T_YourGuideToRules
L_RG_Rules:                                 // _ChooseRuleToLearnAbout: multichoice 15, 0, MULTI_FRONTIER_RULES
    ParentActorMsg MSGFILE_SCRIPT, T_LearnAboutWhat, 0, 0
    ListMenu_AnchorTopRight 31, 1, 0, 1, RG_SEL
    ListMenuAdd M_TwoStyles + 0, 65535, 0
    ListMenuAdd M_TwoStyles + 1, 65535, 1
    ListMenuAdd M_TwoStyles + 2, 65535, 2
    ListMenuAdd M_TwoStyles + 3, 65535, 3
    ListMenuAdd M_TwoStyles + 4, 65535, 4
    ListMenuAdd M_Exit, 65535, 5
    ListMenuShow
    h_goto_if_ge RG_SEL, 5, L_RG_Bye
    WorkSet RG_PX, RG_SEL
    WorkAdd RG_PX, T_LevelModeInfo
    ParentActorMsg MSGFILE_SCRIPT, RG_PX, 0, 0     // (a work as the line: as the Pike's three-path room)
    LastKeyWait
    VMJump L_RG_Rules

RG_PassGuide:
    h_lock
    SEPlay SEQ_SE_MESSAGE
    h_faceplayer
    h_msgbox T_YourGuideToFrontierPass
L_RG_Pass:                                  // _ChooseFrontierPassInfoToLearnAbout: multichoice 16, 4, MULTI_FRONTIER_PASS_INFO
    ParentActorMsg MSGFILE_SCRIPT, T_LearnAboutWhich1, 0, 0
    ListMenu_AnchorTopRight 31, 7, 0, 1, RG_SEL
    ListMenuAdd M_Symbols + 0, 65535, 0
    ListMenuAdd M_Symbols + 1, 65535, 1
    ListMenuAdd M_Symbols + 2, 65535, 2
    ListMenuAdd M_Exit, 65535, 3
    ListMenuShow
    h_goto_if_ge RG_SEL, 3, L_RG_Bye
    WorkSet RG_PX, RG_SEL
    WorkAdd RG_PX, T_SymbolsInfo
    ParentActorMsg MSGFILE_SCRIPT, RG_PX, 0, 0     // (a work as the line: as the Pike's three-path room)
    LastKeyWait
    VMJump L_RG_Pass

L_RG_Bye:                                   // _Exit*Guide: "We hope you enjoy..."
    h_msgbox T_EnjoyBattleFrontier
    h_release

RG_Scott:                                   // (Emerald's Scott object has no script; he is here only before the scene)
    VMHalt

// _FirstTimeEntering (ON_FRAME VAR_HAS_ENTERED_BATTLE_FRONTIER 0): the greeter calls the player over, the Frontier Pass,
// then Scott comes down from the door, greets the player and leaves. Played on the first entry from the dock (Emerald's
// first visit always is: the ferry lands there); a player who came in through the north door first (a v1.1 save, landed
// inside the Frontier) sees it the first time they come in from the dock.
RG_OnFrame:
    WorkSetConst RG_W_STATE, 1
    h_goto_if_set FLAG_HIDE_BATTLE_FRONTIER_RECEPTION_GATE_SCOTT, L_RG_NoScene
    PlayerGetGPos RG_PX, RG_PZ
    h_goto_if_ne RG_PZ, 13 + RG_OZ, L_RG_NoScene
    h_lock
    WordSetPlayerName 0
    h_applymovement RG_GREETER, RG_MvExclaim            // playse SE_PIN, Common_Movement_ExclamationMark
    h_waitmovement
    h_delay 48                                          // Common_Movement_Delay48
    SEPlay SEQ_SE_MESSAGE
    h_msgbox_actor T_FirstTimeHereThisWay, RG_GREETER
    h_closemessage
    h_applymovement RG_PLAYER, RG_MvPlayerApproach      // walk_up, walk_up, walk_left, walk_left: to (2,11)
    h_waitmovement
    h_msgbox_actor T_WelcomeToBattleFrontier, RG_GREETER
    h_msgbox_actor T_IssueFrontierPass, RG_GREETER
    h_closemessage
    h_playfanfare MUS_OBTAIN_ITEM
    SystemMsg T_ObtainedFrontierPass, 2
    h_waitfanfare
    LastKeyWait
    h_msgbox_info T_PlacedTrainerCardInFrontierPass
    h_closemessage
    h_msgbox_actor T_EnjoyBattleFrontier, RG_GREETER
    h_msgbox_actor T_IfItIsntPlayerYouCame, RG_SCOTT
    h_closemessage
    h_applymovement RG_GREETER, RG_MvFaceUp
    h_applymovement RG_GUIDE, RG_MvFaceUp
    h_applymovement RG_PLAYER, RG_MvFaceUp
    h_waitmovement
    h_applymovement RG_GREETER, RG_MvExclaim
    h_applymovement RG_GUIDE, RG_MvExclaim
    h_applymovement RG_PLAYER, RG_MvExclaim
    h_waitmovement
    h_msgbox_actor T_OhMrScottGoodDay, RG_GREETER
    h_closemessage
    h_applymovement RG_GREETER, RG_MvLateFaceRight     // _GreeterFaceScott
    h_applymovement RG_GUIDE, RG_MvLateFaceLeft        // _FacilityGuideFaceScott
    h_applymovement RG_PLAYER, RG_MvLateFaceRight      // _PlayerFaceScott
    h_applymovement RG_SCOTT, RG_MvScottEnter          // walk_down x6, walk_left: to (3,11)
    h_waitmovement
    h_msgbox_actor T_ScottGreatToSeeYouHere, RG_SCOTT
    h_closemessage
    h_applymovement RG_SCOTT, RG_MvScottExit           // walk_right, walk_up x6
    h_waitmovement
    h_removeobject RG_SCOTT, FLAG_HIDE_BATTLE_FRONTIER_RECEPTION_GATE_SCOTT
    h_release
L_RG_NoScene:
    VMHalt

    .balign 4, 0
RG_MvExclaim:
    emote_exclamation_mark
    step_end
RG_MvPlayerApproach:
    walk_up 2
    walk_left 2
    step_end
RG_MvFaceUp:
    walk_in_place_fastest_up
    step_end
RG_MvLateFaceRight:
    delay_16 3
    delay_8
    walk_in_place_fastest_right
    step_end
RG_MvLateFaceLeft:
    delay_16 3
    delay_8
    walk_in_place_fastest_left
    step_end
RG_MvScottEnter:
    walk_down 6
    walk_left
    step_end
RG_MvScottExit:
    walk_right
    walk_up 6
    step_end
