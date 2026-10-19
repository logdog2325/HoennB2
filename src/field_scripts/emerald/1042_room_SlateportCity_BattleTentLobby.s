// SlateportCity_BattleTentLobby (zone 521; Emerald only): the Battle Tent Slateport Site's lobby, the Battle Swap
// Tournament (pokeemerald data/maps/SlateportCity_BattleTentLobby/scripts.inc; battle_tents, 2026-10-18,
// notes/BATTLE_TENTS.md). The attendant is battle_tents_lib.inc's tent flow with no pick (the rentals are handed out in
// the corridor: frontier_factory_dome.c's Slateport tent mode), the save, the walk through the door (6,1); the prize (a
// Full Heal: pokeemerald sSlateportTentRewards) waits in record key 15 until there is room for it. Room origin (1,0).
// Text: src/text/script/emerald/0530_room_SlateportCity_BattleTentLobby.txt.
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_story.inc"
#include "hoenn_emerald.inc"
#include "hoenn_frontier.inc"
#include "scenes/battle_tents_lib.inc"

    ScriptEntry SL_Attendant            // 1: the attendant (Emerald object 1, SCIENTIST_1)
    ScriptEntry SL_TormentGiver         // 2: SAILOR (TM41 Torment: Sapphire's flag, the giver moved here from the Contest Hall)
    ScriptEntry SL_Man                  // 3: MAN_3
    ScriptEntry SL_Girl                 // 4: GIRL_1
    ScriptEntry SL_Woman                // 5: WOMAN_2
    ScriptEntry SL_None                 // 6: (no sixth object here)
    ScriptEntry SL_Rules                // 7: the rules board (4,5)
    ScriptEntry SL_Returned             // 8: map-script condition TT_STATE 0 (Emerald's ON_FRAME table)
    ScriptEntriesEnd

SL_None:
    VMHalt

SL_Attendant:
    tent_attendant TENT_FAC_SLATEPORT, L_SL_Enter, Sub_SL_Init, L_SL_Prize, 0
Sub_SL_Init:                            // slateporttent_init: the rentals and the opponents of a new challenge
    FrontierCmd TC_T_INIT
    VMReturn
L_SL_Enter:                             // EnterChallenge: WalkToDoor, then the corridor (a new challenge: script 1)
    VMCall Sub_SL_Walk
    fd_to_room TT_S_CORR, TT_CX(2), TT_CZ(7), 0, 1, 1      // warp MAP_SLATEPORT_CITY_BATTLE_TENT_CORRIDOR, 2, 7
L_SL_Resume:                            // ResumeChallenge: the walk in again (the corridor's script 4)
    VMCall Sub_SL_Walk
    fd_to_room TT_S_CORR, TT_CX(2), TT_CZ(7), 0, 4, 1
Sub_SL_Walk:
    h_applymovement 1, SL_MvToDoor
    h_applymovement TT_PLAYER, SL_MvToDoor
    h_waitmovement
    bt_door_open TT_LX(6), TT_LZ(1)     // opendoor 6, 1
    h_applymovement 1, SL_MvAttendantIn
    h_applymovement TT_PLAYER, SL_MvPlayerIn
    h_waitmovement
    VMReturn
L_SL_Prize:                             // GivePrize
    tent_give_prize TENT_FAC_SLATEPORT, 1, BT_PRIZE_SLATEPORT

SL_Returned:
    tent_returned TENT_FAC_SLATEPORT, 1, L_SL_Resume, L_SL_Prize, 0

SL_TormentGiver:                        // TormentGiver: TM41 Torment once (FLAG_RECEIVED_TM41, Emerald FLAG_RECEIVED_TM_TORMENT)
    h_lock
    SEPlay SEQ_SE_MESSAGE
    h_faceplayer
    h_goto_if_set FLAG_RECEIVED_TM41, L_SL_TormentAfter
    h_msgbox BT_S_LOBBY_TORMENT
    h_closemessage
    h_giveitem ITEM_TM41
    h_goto_if_eq HLIB_RESULT, 0, L_SL_BagFull
    h_setflag FLAG_RECEIVED_TM41
    h_msgbox BT_S_LOBBY_TORMENT_AFTER
    h_closemessage
    h_release
L_SL_BagFull:                           // Common_EventScript_ShowBagIsFull
    h_bag_is_full BT_S_LOBBY_BAG_FULL
    h_release
L_SL_TormentAfter:
    h_msgbox BT_S_LOBBY_TORMENT_AFTER
    h_closemessage
    h_release

SL_Man:
    h_msgbox_npc BT_S_LOBBY_MAN
SL_Girl:
    h_msgbox_npc BT_S_LOBBY_GIRL
SL_Woman:
    h_msgbox_npc BT_S_LOBBY_WOMAN

SL_Rules:                               // RulesBoard: the headings until EXIT (MULTI_SLATEPORT_TENT_RULES)
    h_lock
    h_msgbox_info BT_S_LOBBY_RULES
L_SL_RulesAsk:
    SystemMsg BT_S_LOBBY_RULES_WHICH, 2
    ListMenu_AnchorTopRight 31, 0, 0, 1, FD_T0
    ListMenuAdd BT_S_LOBBY_MENU_BASICS, 65535, 0
    ListMenuAdd BT_S_LOBBY_MENU_SWAP_PARTNER, 65535, 1
    ListMenuAdd BT_S_LOBBY_MENU_SWAP_NUMBER, 65535, 2
    ListMenuAdd BT_S_LOBBY_MENU_SWAP_NOTES, 65535, 3
    ListMenuAdd BT_S_LOBBY_MENU_MONS, 65535, 4
    ListMenuAdd BT_S_LOBBY_MENU_EXIT, 65535, 5
    ListMenuShow
    WorkCmpConst FD_T0, 4
    VMJumpIf CMP_GT, L_SL_RulesEnd
    WorkAdd FD_T0, BT_S_LOBBY_RULES_BASICS
    SystemMsg FD_T0, 2
    LastKeyWait
    VMJump L_SL_RulesAsk
L_SL_RulesEnd:
    h_release

    .balign 4, 0
SL_MvToDoor:                            // Movement_AttendantWalkToDoor / PlayerWalkToDoor
    walk_up 3
    step_end
SL_MvAttendantIn:                       // Movement_AttendantEnterDoor
    walk_up
    set_invisible
    step_end
SL_MvPlayerIn:                          // Movement_PlayerEnterDoor
    walk_up 2
    set_invisible
    step_end
