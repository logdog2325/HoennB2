// Oldale Town's scripts (replaces Accumula Town's script file 0794, zone 397; no map-load scripts).
// Messages: src/text/script/0626_oldale_town.txt (the zone's text file, 626).
// Story (chapter Ch1, notes/STORY_PORTING.md): 5 footprints man, 6 Mart employee (walks you to the Mart, Potion),
// 7-10 the rival after Route 103, 11 zone init (OldaleTown_OnTransition), 12 the blocked path to Route 102; map
// scripts 0795; the rival NPC (uid 104) and the triggers come from data/story/ch1.json. Zone tiles = Sapphire +
// (168, 300); the zone's NPCs (data/hoenn_world.json, uid = index): 0 girl, 1 Mart employee, 2 footprints man.
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_story.inc"

    ScriptEntry Script_1    // sign: Oldale Town
    ScriptEntry Script_2    // sign: Pokémon Center
    ScriptEntry Script_3    // sign: Pokémon Mart
    ScriptEntry Script_4    // NPC: girl (OldaleTown_EventScript_Girl)
    ScriptEntry Script_5    // NPC: footprints man (OldaleTown_EventScript_FootprintsMan)
    ScriptEntry Script_6    // NPC: Mart employee (OldaleTown_EventScript_MartEmployee)
    ScriptEntry Script_7    // NPC: the rival (OldaleTown_EventScript_Rival)
    ScriptEntry Script_8    // trigger (8,19): OldaleTown_EventScript_RivalTrigger1
    ScriptEntry Script_9    // trigger (9,19): RivalTrigger2
    ScriptEntry Script_10    // trigger (10,19): RivalTrigger3
    ScriptEntry Script_11    // zone init (0795): OldaleTown_OnTransition
    ScriptEntry Script_12    // trigger (0,10): OldaleTown_EventScript_BlockedPath (VAR_ROUTE102_ACCESSIBLE 0)
    ScriptEntriesEnd

Script_1:
    ActorsPauseAll
    SEPlay SEQ_SE_MESSAGE
    MsgPlaceSign 0, 1
    MsgPlaceSignClose
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_2:
    ActorsPauseAll
    SEPlay SEQ_SE_MESSAGE
    MsgPlaceSign 1, 2
    MsgPlaceSignClose
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_3:
    ActorsPauseAll
    SEPlay SEQ_SE_MESSAGE
    MsgPlaceSign 2, 2
    MsgPlaceSignClose
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_4:
    ActorsPauseAll
    SEPlay SEQ_SE_MESSAGE
    ActorSetEyeToEye
    ParentActorMsg MSGFILE_SCRIPT, 3, 0, 0
    LastKeyWait
    ActorMsgClose
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

#define OLDALE_EMPLOYEE 1
#define OLDALE_MANIAC 2
#define OLDALE_TEMP_1 1                          // Sapphire FLAG_TEMP_1 (Black 2 flags 0-0x63 are map-local too)

Script_5:                                        // OldaleTown_EventScript_FootprintsMan
    h_lock
    SEPlay SEQ_SE_MESSAGE
    h_faceplayer
    h_goto_if_set FLAG_ADVENTURE_STARTED, L_OldaleNotBlocking
    h_msgbox 4                                   // I just discovered the footprints of a rare Pokémon! ...
    h_closemessage
    h_turnobject OLDALE_MANIAC, 2                // Common_Movement_FaceOriginalDirection: west, guarding the path
    h_release
L_OldaleNotBlocking:
    h_msgbox 10                                  // I finished sketching the footprints of a rare Pokémon. ...
    h_release

Script_12:                                       // OldaleTown_EventScript_BlockedPath
    h_lock
    h_applymovement 255, Mv_OldalePlayerStepBack
    h_applymovement OLDALE_MANIAC, Mv_OldaleManiacBackUp
    h_waitmovement
    h_msgbox_actor 11, OLDALE_MANIAC             // Aaaaah! Wait! Please don't come in here. ...
    h_closemessage
    h_applymovement OLDALE_MANIAC, Mv_OldaleManiacReturn
    h_waitmovement
    h_release

Script_6:                                        // OldaleTown_EventScript_MartEmployee
    h_lock
    SEPlay SEQ_SE_MESSAGE
    h_faceplayer
    h_goto_if_set FLAG_RECEIVED_POTION_OLDALE, L_OldaleExplainPotion
    h_goto_if_set OLDALE_TEMP_1, L_OldaleExplainPotion
    h_setflag OLDALE_TEMP_1
    h_playbgm MUS_FOLLOW_ME
    h_msgbox 8                                   // Hi! I work at a Pokémon Mart. ... Can I get you to come with me?
    h_closemessage
    h_getplayerfacing HLIB_TMP                   // Sapphire VAR_FACING 1 south / 2 north / 4 east = Black 2 1 / 0 / 3
    h_goto_if_eq HLIB_TMP, 1, L_OldaleGoSouth
    h_goto_if_eq HLIB_TMP, 0, L_OldaleGoNorth
    h_goto_if_eq HLIB_TMP, 3, L_OldaleGoEast
    h_release                                    // (Sapphire has no case for west: the script just ends)
L_OldaleGoSouth:                                 // the player stands north of him: he walks around
    h_applymovement OLDALE_EMPLOYEE, Mv_OldaleEmployeeSouth
    h_applymovement 255, Mv_OldalePlayerSouth
    VMJump L_OldaleToMart
L_OldaleGoNorth:
    h_applymovement OLDALE_EMPLOYEE, Mv_OldaleEmployeeNorth
    h_applymovement 255, Mv_OldalePlayerNorth
    VMJump L_OldaleToMart
L_OldaleGoEast:
    h_applymovement 255, Mv_OldalePlayerEast
    h_applymovement OLDALE_EMPLOYEE, Mv_OldaleEmployeeEast
L_OldaleToMart:
    h_waitmovement
    h_msgbox 9                                   // This is a Pokémon Mart. ... I'd like you to have this as a promotional item.
    h_closemessage
    h_giveitem ITEM_POTION
    h_goto_if_eq HLIB_RESULT, 0, L_OldaleBagFull // (Black 2's item script has said the Bag is full)
    h_msgbox 5                                   // A Potion can be used anytime ...
    h_setflag FLAG_RECEIVED_POTION_OLDALE
L_OldaleBagFull:
    h_fadedefaultbgm
    h_release
L_OldaleExplainPotion:
    h_msgbox 5
    h_release

#define OLDALE_RIVAL 104

Script_7:                                        // OldaleTown_EventScript_Rival
    h_lock
    h_faceplayer
    VMJump L_OldaleRivalMessage

Script_8:                                        // RivalTrigger1: the rival comes two steps left
    h_lock
    h_applymovement OLDALE_RIVAL, Mv_OldaleRivalApproach1
    h_waitmovement
    VMJump L_OldaleFaceRival
Script_9:                                        // RivalTrigger2: one step
    h_lock
    h_applymovement OLDALE_RIVAL, Mv_OldaleRivalApproach2
    h_waitmovement
    VMJump L_OldaleFaceRival
Script_10:                                       // RivalTrigger3: faces left
    h_lock
    h_applymovement OLDALE_RIVAL, Mv_OldaleRivalApproach3
    h_waitmovement
L_OldaleFaceRival:
    h_applymovement 255, Mv_OldaleFaceRight      // Common_Movement_WalkInPlaceFastestRight
    h_waitmovement
L_OldaleRivalMessage:                            // OldaleTown_EventScript_ShowRivalMessage
    h_buffer_player
    h_msgbox_gendered 6, 7, OLDALE_RIVAL         // May: <player>! Over here! / Brendan: I'm heading back...
    h_closemessage                               // OldaleTown_EventScript_RivalFinish
    h_applymovement OLDALE_RIVAL, Mv_OldaleRivalExit
    h_waitmovement
    h_removeobject OLDALE_RIVAL, FLAG_HIDE_RIVAL_OLDALE_TOWN
    h_setvar VAR_OLDALE_STATE, 2
    h_release

Script_11:                                       // OldaleTown_OnTransition
    h_setup_rival_gfx
    h_setflag FLAG_VISITED_OLDALE_TOWN
    h_goto_if_set FLAG_ADVENTURE_STARTED, L_OldaleInitPath
    ObjInitNPCGPos OLDALE_MANIAC, 2, 169, 0, 311   // BlockWestEntrance: (1,11), facing west
L_OldaleInitPath:
    h_goto_if_set FLAG_RECEIVED_POTION_OLDALE, L_OldaleInitEmployee
    ObjInitNPCGPos OLDALE_EMPLOYEE, 1, 181, 0, 314 // MoveMartEmployee: (13,14), facing down
L_OldaleInitEmployee:
    h_goto_if_unset FLAG_ADVENTURE_STARTED, L_OldaleInitDone
    h_setvar VAR_ROUTE102_ACCESSIBLE, 1            // SetOldaleState
L_OldaleInitDone:
    VMHalt

    .balign 4, 0
Mv_OldaleRivalApproach1:
    walk_left 2
    step_end
Mv_OldaleRivalApproach2:
    walk_left
    step_end
Mv_OldaleRivalApproach3:
    face_left
    step_end
Mv_OldaleFaceRight:
    walk_in_place_fastest_right
    step_end
Mv_OldaleRivalExit:
    walk_down 6
    step_end
Mv_OldaleEmployeeEast:                           // OldaleTown_Movement_EmployeeEast
    walk_up 7
    walk_in_place_fastest_down
    step_end
Mv_OldaleEmployeeSouth:
    walk_left
    walk_up 2
    walk_right
    walk_up 5
    walk_in_place_fastest_down
    step_end
Mv_OldaleEmployeeNorth:
    walk_up 7
    walk_in_place_fastest_down
    step_end
Mv_OldalePlayerEast:
    walk_right
    walk_up 6
    step_end
Mv_OldalePlayerSouth:
    delay_16 4
    walk_up 5
    step_end
Mv_OldalePlayerNorth:
    walk_up 7
    step_end
Mv_OldalePlayerStepBack:                         // OldaleTown_Movement_PlayerStepBack
    delay_8
    walk_right
    step_end
Mv_OldaleManiacBackUp:                           // OldaleTown_Movement_BackUp
    walk_fast_up
    walk_in_place_fastest_left
    lock_facing_direction
    walk_right
    unlock_facing_direction
    step_end
Mv_OldaleManiacReturn:                           // OldaleTown_Movement_ReturnToOriginalPosition
    walk_down
    walk_left
    step_end
    .balign 4, 0
