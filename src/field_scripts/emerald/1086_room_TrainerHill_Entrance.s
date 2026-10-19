// TrainerHill_Entrance (zone 543; Emerald only): the Trainer Hill's reception (pokeemerald
// data/maps/TrainerHill_Entrance/scripts.inc + src/trainer_hill.c; battle_tents, 2026-10-18, notes/BATTLE_TENTS.md).
// Opens after the Hall of Fame (FLAG_SYS_GAME_CLEAR), as Emerald's. The counter trigger (9,6) asks for the save on the
// first visit, then the mode (Normal / Variety / Unique / Expert Tag Match: the base game's four, never the e-Reader's),
// heals the party and starts the timer (b2tools/patches/trainer_hill.c: Black 2's play time). Back here after a loss
// (condition script 8): "That was too bad", the push back, the heal. Leaving the building ends the challenge
// (trainer_hill.c's per-step check outside the Hill's zones = Route111_OnTransition). The time board (8,10) shows the four
// modes' best times. The clerk sells Emerald's two lists (shop ids 23 / 25, trainer_hill.py marts()).
// Room origin (1,1): Emerald (x, y) = zone (x + 1, y + 1). Text: src/text/script/emerald/0112_room_TrainerHill_Entrance.txt.
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_story.inc"
#include "hoenn_emerald.inc"
#include "hoenn_frontier.inc"
#include "scenes/trainer_hill_lib.inc"

#define TE_SHOP_BASIC 23                // trainer_hill.py MART_IDS
#define TE_SHOP_EXPANDED 25

    ScriptEntry TE_Attendant            // 1: Teala (Emerald object 1)
    ScriptEntry TE_Nurse                // 2: the nurse (object 2)
    ScriptEntry TE_Clerk                // 3: the Mart clerk (object 3)
    ScriptEntry TE_Girl                 // 4: GIRL_3 (object 4)
    ScriptEntry TE_Man                  // 5: MAN_3 (object 5)
    ScriptEntry TE_Records              // 6: the time board (bg (8,10))
    ScriptEntry TE_Entry                // 7: the counter trigger (9,6) while TH_ACTIVE (work 0x4001) is 0
    ScriptEntry TE_Returned             // 8: map-script condition TH_STATE 0 (Emerald's ON_FRAME ExitChallenge)
    ScriptEntry TE_Init                 // 9: zone init: TH_ACTIVE from the challenge's state
    ScriptEntriesEnd

TE_Nurse:                               // TrainerHill_Entrance_EventScript_Nurse (Common_EventScript_PkmnCenterNurse;
#include "centers/nurse.inc"            // lines 0-4; the healing machine (2-3,8-9) on her left)

TE_Init:
    th_flags_test TH_F_ACTIVE, TH_T0
    h_goto_if_eq TH_T0, 0, L_TE_InitEnd
    WorkSetConst TH_ACTIVE, 1
L_TE_InitEnd:
    VMHalt

TE_Attendant:                           // in a challenge (not yet at the owner): "I hope you give it your best."
    h_lock
    SEPlay SEQ_SE_MESSAGE
    h_faceplayer
    ThHill TH_OP_FLAGS, TH_T0
    WorkAnd TH_T0, TH_F_ACTIVE | 8
    h_goto_if_ne TH_T0, TH_F_ACTIVE, L_TE_Thanks
    h_msgbox TH_ENTRANCE_GIVE_YOUR_BEST
    h_closemessage
    h_release
L_TE_Thanks:
    h_msgbox TH_ENTRANCE_THANKS
    h_closemessage
    h_release

TE_Clerk:                               // the Mart: Basic list, or Expanded after the Hall of Fame
    h_lock
    SEPlay SEQ_SE_MESSAGE
    h_faceplayer
    VMStackPush 0x8000
    VMStackPush 0x8001
    WorkSetConst 0x8000, TE_SHOP_BASIC
    h_goto_if_unset FLAG_SYS_GAME_CLEAR, L_TE_Shop
    WorkSetConst 0x8000, TE_SHOP_EXPANDED
L_TE_Shop:
    WorkSetConst 0x8001, 1
    RTCallGlobal 10110
    VMStackPop 0x8001
    VMStackPop 0x8000
    h_release

TE_Girl:
    h_goto_if_unset FLAG_SYS_GAME_CLEAR, L_TE_GirlClosed
    h_msgbox_npc TH_ENTRANCE_GIRL
L_TE_GirlClosed:
    h_msgbox_npc TH_ENTRANCE_GIRL_CLOSED

TE_Man:
    h_goto_if_unset FLAG_SYS_GAME_CLEAR, L_TE_ManClosed
    h_msgbox_npc TH_ENTRANCE_MAN
L_TE_ManClosed:
    h_msgbox_npc TH_ENTRANCE_MAN_CLOSED

TE_Records:                             // ShowTrainerHillRecords: the four modes' best times (59:59.99 when none yet)
    h_lock
    SEPlay SEQ_SE_MESSAGE
    ThHill TH_OP_BOARD_WORDS | 1, TH_T0 // words 1-12
    h_msgbox_info TH_ENTRANCE_BOARD
    h_closemessage
    h_release

// ---- the counter (EntryTrigger)
TE_Entry:
    h_lock
    h_turnobject TH_PLAYER, 3           // PlayerFaceAttendant
    h_goto_if_unset FLAG_SYS_GAME_CLEAR, L_TE_Closed
    h_msgbox_actor TH_ENTRANCE_WELCOME, TH_TEALA
    th_flags_test TH_F_SAVED, TH_T0     // trainerhill_getsaved
    h_goto_if_ne TH_T0, 0, L_TE_Saved
    h_msgbox_actor TH_ENTRANCE_SAVE_FIRST, TH_TEALA
    h_closemessage
    ThHill TH_OP_FLAG_SET | TH_BIT_SAVED, TH_T0
    fr_save_game TH_T1
    h_goto_if_eq TH_T1, 0, L_TE_Saved
    ThHill TH_OP_FLAG_CLEAR | TH_BIT_SAVED, TH_T0     // SaveFailed
    VMJump L_TE_Cancel
L_TE_Saved:
    h_msgbox_actor TH_ENTRANCE_EVERY_ROOM, TH_TEALA   // (the base modes use all four floors)
L_TE_Ask:
    ActorMsg MSGFILE_SCRIPT, TH_ENTRANCE_LIKE_TO_CHALLENGE, TH_TEALA, 0, 0
    ListMenu_AnchorTopRight 31, 6, 0, 1, TH_T1        // MULTI_YESNOINFO
    ListMenuAdd TH_ENTRANCE_MENU_YES, 65535, 0
    ListMenuAdd TH_ENTRANCE_MENU_NO, 65535, 1
    ListMenuAdd TH_ENTRANCE_MENU_INFO, 65535, 2
    ListMenuShow
    h_goto_if_eq TH_T1, 0, L_TE_Choose
    h_goto_if_ne TH_T1, 2, L_TE_Cancel
    h_msgbox_actor TH_ENTRANCE_EXPLAIN, TH_TEALA
    VMJump L_TE_Ask
L_TE_Choose:                            // MULTI_TAG_MATCH_TYPE
    ListMenu_AnchorTopRight 31, 2, 0, 1, TH_T1
    ListMenuAdd TH_ENTRANCE_MENU_NORMAL, 65535, 0
    ListMenuAdd TH_ENTRANCE_MENU_VARIETY, 65535, 1
    ListMenuAdd TH_ENTRANCE_MENU_UNIQUE, 65535, 2
    ListMenuAdd TH_ENTRANCE_MENU_EXPERT, 65535, 3
    ListMenuAdd TH_ENTRANCE_MENU_EXIT, 65535, 4
    ListMenuShow
    h_goto_if_ge TH_T1, 4, L_TE_Cancel
    ThHill TH_OP_START, TH_T1           // trainerhill_setmode + trainerhill_start (the timer)
    WorkSetConst TH_ACTIVE, 1           // VAR_TRAINER_HILL_IS_ACTIVE
    h_heal
    h_msgbox_actor TH_ENTRANCE_GET_SET_GO, TH_TEALA
    h_closemessage
    h_release
L_TE_Cancel:
    h_msgbox_actor TH_ENTRANCE_VISIT_AGAIN, TH_TEALA
    h_closemessage
    h_applymovement TH_PLAYER, TE_MvPushBack
    h_waitmovement
    h_release
L_TE_Closed:                            // before the Hall of Fame
    h_msgbox_actor TH_ENTRANCE_STILL_GETTING_READY, TH_TEALA
    h_closemessage
    h_applymovement TH_PLAYER, TE_MvPushBack
    h_waitmovement
    h_release

// ---- back at the counter after a loss (TrainerHill_Entrance_EventScript_ExitChallengeLost)
TE_Returned:
    WorkSetConst TH_STATE, 1
    th_flags_test TH_F_LOST, TH_T0
    h_goto_if_ne TH_T0, 0, L_TE_Lost
    VMHalt
L_TE_Lost:
    h_lock
    h_turnobject TH_PLAYER, 3
    h_msgbox_actor TH_ENTRANCE_TOO_BAD, TH_TEALA
    h_closemessage
    h_applymovement TH_PLAYER, TE_MvPushBack
    h_waitmovement
    ThHill TH_OP_LEAVE, TH_T0           // VAR_TRAINER_HILL_IS_ACTIVE 0 (hasLost cleared)
    WorkSetConst TH_ACTIVE, 0
    h_heal
    h_release

    .balign 4, 0
TE_MvPushBack:                          // PushPlayerBackFromCounter
    walk_down
    step_end
