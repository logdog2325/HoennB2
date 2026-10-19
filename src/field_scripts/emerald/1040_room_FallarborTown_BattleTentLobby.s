// FallarborTown_BattleTentLobby (zone 520; Emerald only): the Battle Tent Fallarbor Site's lobby, the Set KO Tourney
// (pokeemerald data/maps/FallarborTown_BattleTentLobby/scripts.inc; battle_tents, 2026-10-18, notes/BATTLE_TENTS.md).
// The attendant is battle_tents_lib.inc's tent flow (three Pokémon picked in the order they will battle, at Open Level;
// the save; the walk through the door (6,1)); the battles are the Battle Arena's rules on the tent's own trainers
// (frontier_palace_arena.c, tent mode); the prize (a Hyper Potion: pokeemerald sFallarborTentRewards) waits in record key
// 15 until there is room for it. Room origin (1,0). Text: src/text/script/emerald/0529_room_FallarborTown_BattleTentLobby.txt.
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_story.inc"
#include "hoenn_emerald.inc"
#include "hoenn_frontier.inc"
#include "scenes/battle_tents_lib.inc"

    ScriptEntry FL_Attendant            // 1: the attendant (Emerald object 1, BLACK_BELT)
    ScriptEntry FL_Hiker                // 2: HIKER
    ScriptEntry FL_LittleBoy            // 3: LITTLE_BOY
    ScriptEntry FL_Lass                 // 4: LASS
    ScriptEntry FL_Scott                // 5: Scott (map-local flag 0x10: script 9 hides him)
    ScriptEntry FL_None                 // 6: (no sixth object here)
    ScriptEntry FL_Rules                // 7: the rules board (4,5)
    ScriptEntry FL_Returned             // 8: map-script condition TT_STATE 0 (Emerald's ON_FRAME table)
    ScriptEntry FL_Init                 // 9: zone init (Scott's visibility)
    ScriptEntriesEnd

FL_None:
    VMHalt

FL_Attendant:
    tent_attendant TENT_FAC_FALLARBOR, L_FL_Enter, Sub_FL_Init, L_FL_Prize, 3
Sub_FL_Init:                            // fallarbortent_init: nobody met yet
    FrontierPA PA_INIT, TT_PA_FALLARBOR
    VMReturn
L_FL_Enter:                             // EnterChallenge: WalkToDoor, then the corridor
    h_applymovement 1, FL_MvToDoor
    h_applymovement TT_PLAYER, FL_MvToDoor
    h_waitmovement
    bt_door_open TT_LX(6), TT_LZ(1)     // opendoor 6, 1
    h_applymovement 1, FL_MvAttendantIn
    h_applymovement TT_PLAYER, FL_MvPlayerIn
    h_waitmovement
    fd_to_room TT_F_CORR, TT_CX(2), TT_CZ(7), 0, 1, 1      // warp MAP_FALLARBOR_TOWN_BATTLE_TENT_CORRIDOR, 2, 7
L_FL_Prize:                             // GivePrize
    tent_give_prize TENT_FAC_FALLARBOR, 1, BT_PRIZE_FALLARBOR

FL_Returned:
    tent_returned TENT_FAC_FALLARBOR, 1, L_FL_Enter, L_FL_Prize, 0

FL_Hiker:
    h_msgbox_npc BT_F_LOBBY_HIKER
FL_LittleBoy:
    h_msgbox_npc BT_F_LOBBY_LITTLE_BOY
FL_Lass:
    h_msgbox_npc BT_F_LOBBY_LASS

FL_Scott:                               // Scott: the first talk counts (VAR_SCOTT_STATE + 1, key 15 bit 9)
    h_lock
    SEPlay SEQ_SE_MESSAGE
    h_faceplayer
    tt_key_test TENT_SCOTT_F, FR_T0
    h_goto_if_ne FR_T0, 0, L_FL_ScottAgain
    h_buffer_player
    h_msgbox BT_F_LOBBY_SCOTT
    h_addvar VAR_SCOTT_STATE, 1
    tt_key_set TENT_SCOTT_F
    h_closemessage
    h_release
L_FL_ScottAgain:
    h_buffer_player
    h_msgbox BT_F_LOBBY_SCOTT_AFTER
    h_closemessage
    h_release

FL_Init:                                // Scott stands here from the first visit of the Fiery Path (FieryPath_OnTransition
    h_goto_if_unset FLAG_LANDMARK_FIERY_PATH, L_FL_HideScott      // clears FLAG_HIDE_FALLARBOR_TOWN_BATTLE_TENT_SCOTT)
    h_goto_if_ne VAR_METEOR_FALLS_STATE, 0, L_FL_HideScott          // until Meteor Falls' Team Magma scene (it sets it)
    VMHalt
L_FL_HideScott:
    FlagSet TT_FLAG_SCOTT
    VMHalt

FL_Rules:                               // RulesBoard: the headings until EXIT (MULTI_FALLARBOR_TENT_RULES)
    h_lock
    h_msgbox_info BT_F_LOBBY_RULES
L_FL_RulesAsk:
    SystemMsg BT_F_LOBBY_RULES_WHICH, 2
    ListMenu_AnchorTopRight 31, 0, 0, 1, FD_T0
    ListMenuAdd BT_F_LOBBY_MENU_TRAINERS, 65535, 0
    ListMenuAdd BT_F_LOBBY_MENU_BATTLE, 65535, 1
    ListMenuAdd BT_F_LOBBY_MENU_MIND, 65535, 2
    ListMenuAdd BT_F_LOBBY_MENU_SKILL, 65535, 3
    ListMenuAdd BT_F_LOBBY_MENU_BODY, 65535, 4
    ListMenuAdd BT_F_LOBBY_MENU_EXIT, 65535, 5
    ListMenuShow
    WorkCmpConst FD_T0, 4
    VMJumpIf CMP_GT, L_FL_RulesEnd
    WorkAdd FD_T0, BT_F_LOBBY_RULES_LEVEL
    SystemMsg FD_T0, 2
    LastKeyWait
    VMJump L_FL_RulesAsk
L_FL_RulesEnd:
    h_release

    .balign 4, 0
FL_MvToDoor:                            // Movement_AttendantWalkToDoor / PlayerWalkToDoor
    walk_up 3
    step_end
FL_MvAttendantIn:                       // Movement_AttendantEnterDoor
    walk_up
    set_invisible
    step_end
FL_MvPlayerIn:                          // Movement_PlayerEnterDoor
    walk_up 2
    set_invisible
    step_end
