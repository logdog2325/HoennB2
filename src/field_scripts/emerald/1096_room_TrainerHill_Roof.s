// TrainerHill_Roof (zone 548; Emerald only): the Trainer Hill's owner (pokeemerald data/maps/TrainerHill_Roof/scripts.inc
// + src/trainer_hill.c GetOwnerState / GiveChallengePrize / CheckFinalTime; battle_tents, 2026-10-18,
// notes/BATTLE_TENTS.md). The first talk stops the timer and marks every floor trainer battled; the prize is the mode's
// list's item for the time (under 12 / 13 / 14 / 16 / 18 minutes, else the last: data/emerald/trainer_hill.json
// prize_ids), once per challenge (a full Bag keeps it for later); a faster time than the mode's best is the new record
// (the time board). Room origin (1,-3): Emerald (x, y) = zone (x + 1, y - 3). The elevator door (15,5) leads to the car.
// Text: src/text/script/emerald/0119_room_TrainerHill_Roof.txt.
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_story.inc"
#include "hoenn_emerald.inc"
#include "hoenn_frontier.inc"
#include "scenes/trainer_hill_lib.inc"

    ScriptEntry TR_Owner                // 1: the owner (Emerald object 1, GENTLEMAN)
    ScriptEntriesEnd

TR_Owner:
    h_lock
    SEPlay SEQ_SE_MESSAGE
    h_faceplayer
    ThHill TH_OP_OWNER, TH_T0           // trainerhill_settrainerflags + trainerhill_getownerstate (the timer stops)
    h_goto_if_eq TH_T0, 2, L_TR_Already
    h_goto_if_eq TH_T0, 1, L_TR_Give
    h_msgbox TH_ROOF_OWNER_CAME
L_TR_Give:                              // trainerhill_giveprize
    ThHill TH_OP_PRIZE, TH_T1           // the item (0: received already)
    h_goto_if_eq TH_T1, 0, L_TR_Check
    h_msgbox TH_ROOF_OWNER_GIFT
    ItemCheckSpace TH_T1, 1, TH_T2
    h_goto_if_eq TH_T2, 0, L_TR_Full
    ItemAdd TH_T1, 1, TH_T2
    ThHill TH_OP_FLAG_SET | TH_BIT_PRIZE, TH_T0
    WordSetItemName 2, TH_T1
    MEPlay MUS_LEVEL_UP                 // playfanfare MUS_LEVEL_UP
    h_msgbox TH_ROOF_OBTAINED
    MEWait
    VMJump L_TR_Check
L_TR_Full:                              // NoRoomForPrize
    h_msgbox TH_ROOF_BAG_FULL
    h_msgbox TH_ROOF_OWNER_FULL
L_TR_Check:                             // trainerhill_finaltime
    ThHill TH_OP_FINAL_TIME, TH_T0
    h_goto_if_eq TH_T0, 2, L_TR_End
    h_goto_if_eq TH_T0, 1, L_TR_Slow
    h_msgbox TH_ROOF_OWNER_QUICK        // NewRecord
    VMJump L_TR_End
L_TR_Slow:
    h_msgbox TH_ROOF_OWNER_SLOW
L_TR_End:
    h_msgbox TH_ROOF_OWNER_ZIPPIER
    h_closemessage
    h_release
L_TR_Already:
    h_msgbox TH_ROOF_OWNER_ZIPPIER
    h_closemessage
    h_release
