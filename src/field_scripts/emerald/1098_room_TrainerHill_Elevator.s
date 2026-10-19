// TrainerHill_Elevator (zone 549; Emerald only): the roof's elevator back to the reception (pokeemerald
// data/maps/TrainerHill_Elevator/scripts.inc; battle_tents, 2026-10-18, notes/BATTLE_TENTS.md). The room is the Battle
// Tower's elevator car (BattleTower_Elevator_Emerald, origin (1,1)); the ride is its rumble (0686_room_BattleTower_
// Elevator.s). The car's door leads to the reception's (17,11) (Emerald (17,8) and two steps down through the counter
// gate, which cannot open here). Text: src/text/script/emerald/0121_room_TrainerHill_Elevator.txt.
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_story.inc"
#include "hoenn_emerald.inc"
#include "hoenn_frontier.inc"
#include "scenes/trainer_hill_lib.inc"

#define TV_ATT 1                        // Teala (Emerald LOCALID_TRAINER_HILL_ELEVATOR_ATTENDANT)

    ScriptEntry TV_Attendant            // 1: the attendant (Emerald: end)
    ScriptEntry TV_Enter                // 2: condition work 0x4000 0 (Emerald's ON_FRAME VAR_TEMP_4 0: EnterElevator)
    ScriptEntriesEnd

TV_Attendant:
    VMHalt

TV_Enter:
    WorkSetConst 0x4000, 1
    h_lock
    h_applymovement TH_PLAYER, TV_MvApproach
    h_waitmovement
    h_applymovement TV_ATT, TV_MvFaceRight
    h_waitmovement
    h_yesno_actor TH_ELEVATOR_RETURN, TV_ATT, TH_T0
    h_closemessage
    h_goto_if_ne TH_T0, 0, L_TV_Roof
    h_applymovement TV_ATT, TV_MvFaceDown
    h_waitmovement
    h_applymovement TH_PLAYER, TV_MvCenter
    h_waitmovement
    SEPlay SEQ_SE_FLD_23                // special MoveElevator: Black 2's elevator rumble and shake
    EvCameraShake 4, 0, 4, 5, 1, 0, 1, 3
    h_delay 64
    SEStop
    h_delay 25
    h_applymovement TH_PLAYER, TV_MvExit
    h_waitmovement
    h_warp_arrive TH_Z_ENTRANCE, TH_EX(17), TH_EZ(11), 1    // warp MAP_TRAINER_HILL_ENTRANCE, 17, 8 (+ ExitElevator)
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt
L_TV_Roof:                              // ExitToRoof
    h_applymovement TH_PLAYER, TV_MvFaceDown
    h_waitmovement
    h_warp_arrive TH_Z_ROOF, 15 + TH_ROOF_OX, 5 + TH_ROOF_OZ, 1     // warp MAP_TRAINER_HILL_ROOF, 15, 5
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

    .balign 4, 0
TV_MvApproach:                          // PlayerApproachAttendant
    delay_16
    walk_left
    step_end
TV_MvFaceRight:                         // AttendantFacePlayer
    face_right
    step_end
TV_MvFaceDown:                          // AttendantFaceDown / PlayerExitElevatorToRoof
    face_down
    step_end
TV_MvCenter:                            // PlayerMoveToCenterOfElevator
    walk_up
    walk_up
    walk_right
    face_down
    step_end
TV_MvExit:                              // PlayerExitElevator
    delay_16
    walk_down
    walk_down
    step_end
