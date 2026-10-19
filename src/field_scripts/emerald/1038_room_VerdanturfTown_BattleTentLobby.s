// VerdanturfTown_BattleTentLobby (zone 519; Emerald only): the Battle Tent Verdanturf Site's lobby (pokeemerald
// data/maps/VerdanturfTown_BattleTentLobby/scripts.inc; battle_tents, 2026-10-18, notes/BATTLE_TENTS.md). The attendant
// is battle_tents_lib.inc's tent flow (three Pokémon picked at Open Level, the save, the walk through the door (6,1));
// the battles are the Battle Palace's rules on the tent's own trainers (frontier_palace_arena.c, tent mode); the prize
// (a Nest Ball: pokeemerald sVerdanturfTentRewards) waits in record key 15 until there is room for it. Room origin (1,0):
// Emerald (x, y) = zone (x + 1, y). Text: src/text/script/emerald/0527_room_VerdanturfTown_BattleTentLobby.txt.
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_story.inc"
#include "hoenn_emerald.inc"
#include "hoenn_frontier.inc"
#include "scenes/battle_tents_lib.inc"

    ScriptEntry VL_Attendant            // 1: the attendant (Emerald object 1, EXPERT_M)
    ScriptEntry VL_AttractGiver         // 2: GIRL_1 (TM45 Attract: Sapphire's flag, the giver moved here from the Contest Hall)
    ScriptEntry VL_Boy1                 // 3: BOY_3
    ScriptEntry VL_Boy2                 // 4: BOY_2
    ScriptEntry VL_Scott                // 5: Scott (map-local flag 0x10: script 9 hides him)
    ScriptEntry VL_LittleBoy            // 6: LITTLE_BOY
    ScriptEntry VL_Rules                // 7: the rules board (4,5)
    ScriptEntry VL_Returned             // 8: map-script condition TT_STATE 0 (Emerald's ON_FRAME table)
    ScriptEntry VL_Init                 // 9: zone init (Scott's visibility)
    ScriptEntriesEnd

VL_Attendant:
    tent_attendant TENT_FAC_VERDANTURF, L_VL_Enter, Sub_VL_Init, L_VL_Prize, 3
Sub_VL_Init:                            // verdanturftent_init: nobody met yet
    FrontierPA PA_INIT, TT_PA_VERDANTURF
    VMReturn
L_VL_Enter:                             // EnterChallenge: WalkToDoor, then the corridor
    h_applymovement 1, VL_MvToDoor
    h_applymovement TT_PLAYER, VL_MvToDoor
    h_waitmovement
    bt_door_open TT_LX(6), TT_LZ(1)     // opendoor 6, 1
    h_applymovement 1, VL_MvAttendantIn
    h_applymovement TT_PLAYER, VL_MvPlayerIn
    h_waitmovement
    fd_to_room TT_V_CORR, TT_CX(2), TT_CZ(7), 0, 1, 1      // warp MAP_VERDANTURF_TOWN_BATTLE_TENT_CORRIDOR, 2, 7
L_VL_Prize:                             // GivePrize
    tent_give_prize TENT_FAC_VERDANTURF, 1, BT_PRIZE_VERDANTURF

VL_Returned:
    tent_returned TENT_FAC_VERDANTURF, 1, L_VL_Enter, L_VL_Prize, 1

VL_AttractGiver:                        // AttractGiver: TM45 Attract once (FLAG_RECEIVED_TM45, Emerald FLAG_RECEIVED_TM_ATTRACT)
    h_lock
    SEPlay SEQ_SE_MESSAGE
    h_faceplayer
    h_goto_if_set FLAG_RECEIVED_TM45, L_VL_AttractAfter
    h_msgbox BT_V_LOBBY_ATTRACT
    h_closemessage
    h_giveitem ITEM_TM45
    h_goto_if_eq HLIB_RESULT, 0, L_VL_BagFull
    h_setflag FLAG_RECEIVED_TM45
    h_msgbox BT_V_LOBBY_ATTRACT_AFTER
    h_closemessage
    h_release
L_VL_BagFull:                           // Common_EventScript_ShowBagIsFull
    h_bag_is_full BT_V_LOBBY_BAG_FULL
    h_release
L_VL_AttractAfter:
    h_msgbox BT_V_LOBBY_ATTRACT_AFTER
    h_closemessage
    h_release

VL_Boy1:
    h_msgbox_npc BT_V_LOBBY_BOY1
VL_Boy2:                                // (Emerald: lock, no faceplayer)
    h_lock
    SEPlay SEQ_SE_MESSAGE
    h_msgbox BT_V_LOBBY_BOY2
    h_closemessage
    h_release
VL_LittleBoy:
    h_lock
    SEPlay SEQ_SE_MESSAGE
    h_msgbox BT_V_LOBBY_LITTLE_BOY
    h_closemessage
    h_release

VL_Scott:                               // Scott: the first talk counts (VAR_SCOTT_STATE + 1, key 15 bit 8)
    h_lock
    SEPlay SEQ_SE_MESSAGE
    h_faceplayer
    tt_key_test TENT_SCOTT_V, FR_T0
    h_goto_if_ne FR_T0, 0, L_VL_ScottAgain
    h_buffer_player
    h_msgbox BT_V_LOBBY_SCOTT
    h_addvar VAR_SCOTT_STATE, 1
    tt_key_set TENT_SCOTT_V
    h_closemessage
    h_release
L_VL_ScottAgain:
    h_msgbox BT_V_LOBBY_SCOTT_AFTER
    h_closemessage
    h_release

VL_Init:                                // Scott stands here from Wattson's defeat (Emerald: MauvilleCity_Gym clears
    TrainerCardHasBadge FR_T0, 2        // FLAG_HIDE_VERDANTURF_TOWN_SCOTT) until the first visit of the Fiery Path
    h_goto_if_eq FR_T0, 0, L_VL_HideScott   // (FieryPath_OnTransition, FLAG_LANDMARK_FIERY_PATH)
    h_goto_if_set FLAG_LANDMARK_FIERY_PATH, L_VL_HideScott
    VMHalt
L_VL_HideScott:
    FlagSet TT_FLAG_SCOTT
    VMHalt

VL_Rules:                               // RulesBoard: the headings until EXIT (SCROLL_MULTI_BATTLE_TENT_RULES)
    h_lock
    h_msgbox_info BT_V_LOBBY_RULES
L_VL_RulesAsk:
    SystemMsg BT_V_LOBBY_RULES_WHICH, 2
    ListMenu_AnchorTopRight 31, 0, 0, 1, FD_T0
    ListMenuAdd BT_V_LOBBY_MENU_TRAINERS, 65535, 0
    ListMenuAdd BT_V_LOBBY_MENU_BASICS, 65535, 1
    ListMenuAdd BT_V_LOBBY_MENU_NATURE, 65535, 2
    ListMenuAdd BT_V_LOBBY_MENU_MOVES, 65535, 3
    ListMenuAdd BT_V_LOBBY_MENU_UNDERPOWERED, 65535, 4
    ListMenuAdd BT_V_LOBBY_MENU_DANGER, 65535, 5
    ListMenuAdd BT_V_LOBBY_MENU_EXIT, 65535, 6
    ListMenuShow
    WorkCmpConst FD_T0, 5
    VMJumpIf CMP_GT, L_VL_RulesEnd
    WorkAdd FD_T0, BT_V_LOBBY_RULES_LEVEL
    SystemMsg FD_T0, 2
    LastKeyWait
    VMJump L_VL_RulesAsk
L_VL_RulesEnd:
    h_release

    .balign 4, 0
VL_MvToDoor:                            // Movement_WalkToDoor
    walk_up 3
    step_end
VL_MvAttendantIn:                       // Movement_AttendantEnterDoor
    walk_up
    set_invisible
    step_end
VL_MvPlayerIn:                          // Movement_PlayerEnterDoor
    walk_up 2
    set_invisible
    step_end
