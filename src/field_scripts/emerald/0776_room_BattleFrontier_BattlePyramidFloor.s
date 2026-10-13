// BattleFrontier_BattlePyramidFloor (zone 388, Emerald only): a floor of the Battle Pyramid (pokeemerald
// data/maps/BattleFrontier_BattlePyramidFloor + src/battle_pyramid.c; frontier_pyramid 2026-10-12,
// notes/FRONTIER_PYRAMID.md). The maze is built from Emerald's 16 squares as the floor's chunk loads (frontier_pyramid.c
// PY_RDHook); the zone init places Emerald's objects (NPCs 0-15: trainers first, then item balls) and gives the player
// the Battle Bag; every step, frontier_pyramid.c checks the exit panel (script 18), the trainers' eyes (17) and the wild
// Pokemon (19); the Start menu's Save runs script 20 (Emerald's REST / RETIRE). Darkness: h_flash_scale with Emerald's
// light radius (32 pixels on arrival, +4 after every battle won).
// Messages: src/text/script/emerald/0600_room_BattleFrontier_BattlePyramidFloor.txt (converter/gen_frontier_pyramid.py).
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_story.inc"
#include "hoenn_emerald.inc"
#include "hoenn_frontier.inc"
#include "scenes/frontier_pyramid_lib.inc"

    ScriptEntry PYF_Obj1                // 1-16: the objects (frontier_pyramid.c setup_people gives NPC i script i + 1)
    ScriptEntry PYF_Obj2
    ScriptEntry PYF_Obj3
    ScriptEntry PYF_Obj4
    ScriptEntry PYF_Obj5
    ScriptEntry PYF_Obj6
    ScriptEntry PYF_Obj7
    ScriptEntry PYF_Obj8
    ScriptEntry PYF_Obj9
    ScriptEntry PYF_Obj10
    ScriptEntry PYF_Obj11
    ScriptEntry PYF_Obj12
    ScriptEntry PYF_Obj13
    ScriptEntry PYF_Obj14
    ScriptEntry PYF_Obj15
    ScriptEntry PYF_Obj16
    ScriptEntry PYF_Spotted             // 17: a trainer saw the player (PY_W_SLOT, PY_W_STEPS, PY_W_DIR)
    ScriptEntry PYF_Exit                // 18: the exit panel (BattlePyramid_WarpToNextFloor)
    ScriptEntry PYF_Wild                // 19: a wild Pokemon (StandardWildEncounter's Pyramid branch)
    ScriptEntry PYF_Menu                // 20: the Start menu's Save (REST / RETIRE)
    ScriptEntry PYF_Init                // 21: zone init (MapScript 2)
    ScriptEntry PYF_LoadWarp            // 22: field load after a warp (MapScript 4): darkness, the entrance
    ScriptEntry PYF_LoadBack            // 23: field load back from a battle or a menu (MapScript 3): darkness
    ScriptEntry PYF_Ready               // 24: condition PY_W_STATE 0 (Emerald's ON_RESUME)
    ScriptEntriesEnd

PYF_Obj1:
    WorkSetConst PY_W_SLOT, 0
    VMJump L_PYF_Obj
PYF_Obj2:
    WorkSetConst PY_W_SLOT, 1
    VMJump L_PYF_Obj
PYF_Obj3:
    WorkSetConst PY_W_SLOT, 2
    VMJump L_PYF_Obj
PYF_Obj4:
    WorkSetConst PY_W_SLOT, 3
    VMJump L_PYF_Obj
PYF_Obj5:
    WorkSetConst PY_W_SLOT, 4
    VMJump L_PYF_Obj
PYF_Obj6:
    WorkSetConst PY_W_SLOT, 5
    VMJump L_PYF_Obj
PYF_Obj7:
    WorkSetConst PY_W_SLOT, 6
    VMJump L_PYF_Obj
PYF_Obj8:
    WorkSetConst PY_W_SLOT, 7
    VMJump L_PYF_Obj
PYF_Obj9:
    WorkSetConst PY_W_SLOT, 8
    VMJump L_PYF_Obj
PYF_Obj10:
    WorkSetConst PY_W_SLOT, 9
    VMJump L_PYF_Obj
PYF_Obj11:
    WorkSetConst PY_W_SLOT, 10
    VMJump L_PYF_Obj
PYF_Obj12:
    WorkSetConst PY_W_SLOT, 11
    VMJump L_PYF_Obj
PYF_Obj13:
    WorkSetConst PY_W_SLOT, 12
    VMJump L_PYF_Obj
PYF_Obj14:
    WorkSetConst PY_W_SLOT, 13
    VMJump L_PYF_Obj
PYF_Obj15:
    WorkSetConst PY_W_SLOT, 14
    VMJump L_PYF_Obj
PYF_Obj16:
    WorkSetConst PY_W_SLOT, 15
L_PYF_Obj:
    WorkSet PY_W_ACTOR, PY_W_SLOT
    WorkAdd PY_W_ACTOR, 1
    EmPyr PY_T0, PY_SLOT_KIND, PY_W_SLOT
    h_goto_if_eq PY_T0, PYK_ITEM, L_PYF_Item
    h_goto_if_eq PY_T0, PYK_BEATEN, L_PYF_Beaten
    h_goto_if_eq PY_T0, PYK_NONE, L_PYF_None
    h_lock                              // an unbeaten trainer talked to: it turns and battles (trainerbattle)
    h_faceplayer
    VMJump L_PYF_Battle
L_PYF_None:
    VMHalt
L_PYF_Beaten:                           // BattlePyramid_TrainerBattle on a beaten trainer: pyramid_showhint
    h_lock
    h_faceplayer
    EmPyr PY_T1, PY_HINT, PY_W_SLOT
    h_msgbox PY_T1
    h_closemessage
    h_release

// ---- a trainer: Emerald's TRAINER_BATTLE_PYRAMID (CheckForTrainersWantingBattle: "!", the walk up, the greeting)
PYF_Spotted:
    ActorsPauseAll
    WorkSet PY_W_ACTOR, PY_W_SLOT
    WorkAdd PY_W_ACTOR, 1
    h_applymovement PY_W_ACTOR, PYF_MvExclaim
    h_waitmovement
L_PYF_Approach:
    h_goto_if_eq PY_W_STEPS, 0, L_PYF_Faced
    h_call_if_eq PY_W_DIR, 0, Sub_PYF_StepUp
    h_call_if_eq PY_W_DIR, 1, Sub_PYF_StepDown
    h_call_if_eq PY_W_DIR, 2, Sub_PYF_StepLeft
    h_call_if_eq PY_W_DIR, 3, Sub_PYF_StepRight
    WorkSub PY_W_STEPS, 1
    VMJump L_PYF_Approach
L_PYF_Faced:                            // the player turns to the trainer (the opposite of its facing)
    h_call_if_eq PY_W_DIR, 0, Sub_PYF_FaceDown
    h_call_if_eq PY_W_DIR, 1, Sub_PYF_FaceUp
    h_call_if_eq PY_W_DIR, 2, Sub_PYF_FaceRight
    h_call_if_eq PY_W_DIR, 3, Sub_PYF_FaceLeft
L_PYF_Battle:
    EmPyr PY_T1, PY_TRAINER_PREP, PY_W_SLOT     // the Frontier trainer's greeting (speechBefore)
    ActorMsg MSGFILE_SCRIPT, PY_T1, PY_W_ACTOR, 0, 0
    LastKeyWait
    h_closemessage
    CallTrainerBattle PY_TR, 0, 1               // (frontier_pyramid.c fills the trainer and its three; goes on after a loss)
    CallTrainerBattleEnd
    TrainerBattleIsVictory PY_T0
    EmPyr PY_T1, PY_SYNC
    EmPyr PY_T1, PY_ALL_FAINTED
    h_goto_if_ne PY_T1, 0, L_PYF_Lost
    EmPyr PY_T1, PY_TRAINER_WON, PY_W_SLOT      // MarkPyramidTrainerAsBattled
    ActorSetMoveCode PY_W_ACTOR, 3              // (it wanders from now on, as Emerald's)
    VMCall Sub_PYF_LightUp
    EmPyr PY_T1, PY_HINT, PY_W_SLOT             // pyramid_showhint
    ActorMsg MSGFILE_SCRIPT, PY_T1, PY_W_ACTOR, 0, 0
    LastKeyWait
    h_closemessage
    h_release
Sub_PYF_StepUp:
    h_applymovement PY_W_ACTOR, PYF_MvUp
    h_waitmovement
    VMReturn
Sub_PYF_StepDown:
    h_applymovement PY_W_ACTOR, PYF_MvDown
    h_waitmovement
    VMReturn
Sub_PYF_StepLeft:
    h_applymovement PY_W_ACTOR, PYF_MvLeft
    h_waitmovement
    VMReturn
Sub_PYF_StepRight:
    h_applymovement PY_W_ACTOR, PYF_MvRight
    h_waitmovement
    VMReturn
Sub_PYF_FaceUp:
    h_turnobject PY_PLAYER, 0
    VMReturn
Sub_PYF_FaceDown:
    h_turnobject PY_PLAYER, 1
    VMReturn
Sub_PYF_FaceLeft:
    h_turnobject PY_PLAYER, 2
    VMReturn
Sub_PYF_FaceRight:
    h_turnobject PY_PLAYER, 3
    VMReturn

// UpdatePyramidLightRadius (PYRAMID_LIGHT_INCR_RADIUS, 4 pixels, SE_SAVE): after every battle won
Sub_PYF_LightUp:
    EmPyr PY_T2, PY_LIGHT_ADD, 4
    SEPlay SEQ_SE_SAVE
    h_flash_scale PY_T2, 8
    h_delay 16
    VMReturn

// ---- an item ball: BattlePyramid_FindItemBall (pyramid_setitem, Std_FindItem into the Battle Bag, pyramid_hideitem)
L_PYF_Item:
    h_lock
    EmPyr PY_T1, PY_ITEM, PY_W_SLOT             // SetPickupItem: the item
    WordSetPlayerName 0
    WordSetItemName 2, PY_T1
    WorkSet PY_T0, PY_T1
    EmPyr PY_T0, PY_ITEM_TAKEN, PY_W_SLOT       // AddPyramidBagItem: 1 put away, 0 the Bag is full
    h_goto_if_eq PY_T0, 0, L_PYF_ItemFull
    ActorDelete PY_W_ACTOR                      // (removeobject; its flag 0x40 + slot stays set by PY_SETUP)
    MEPlay MUS_OBTAIN_ITEM
    SystemMsg PYL_FLOOR_FOUND, 2
    MEWait
    LastKeyWait
    SystemMsg PYL_FLOOR_PUT_AWAY, 2
    LastKeyWait
    h_closemessage
    h_release
L_PYF_ItemFull:                                 // EventScript_NoRoomToPickUpItem
    SystemMsg PYL_FLOOR_OBTAINED, 2
    LastKeyWait
    SystemMsg PYL_FLOOR_BAG_FULL, 2
    LastKeyWait
    h_closemessage
    h_release

// ---- the exit panel: BattlePyramid_WarpToNextFloor (streak + 1, floor + 1, the 7th leads to the top)
PYF_Exit:
    ActorsPauseAll
    fr_streak_win FRONTIER_FACILITY_PYRAMID, 0
    EmPyr PY_T0, PY_GET, PYF_FLOOR
    WorkAdd PY_T0, 1
    EmPyr PY_T0, PY_SET, PYF_FLOOR
    h_goto_if_eq PY_T0, 7, L_PYF_ToTop
    EmPyr PY_T1, PY_SEED                        // pyramid_seedfloor (and the new floor's trainers)
    fr_set FR_STATUS, PY_ST_IN_CHALLENGE
    h_warp_arrive PY_FLOOR_ZONE, 1, 1, 1        // (the floor's map script puts the player on its entrance)
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt
L_PYF_ToTop:
    h_warp_arrive PY_TOP_ZONE, 17 + PY_TOP_OX, 17 + PY_TOP_OZ, 0
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

// ---- a wild Pokemon (the step check chose it): GenerateBattlePyramidWildMon, BattleSetup_StartWildBattle
PYF_Wild:
    ActorsPauseAll
    EmPyr PY_T0, PY_WILD                        // the species; the level in PY_W_WILD_LV
    CallWildBattle PY_T0, PY_W_WILD_LV, 0x100   // (0x100: no experience; goes on after a loss)
    CallWildBattleEnd
    EmPyr PY_T1, PY_SYNC
    EmPyr PY_T1, PY_ALL_FAINTED
    h_goto_if_ne PY_T1, 0, L_PYF_Lost
    WildBattleIsVictory PY_T1                   // (won or caught: the light grows; fled: not)
    h_call_if_eq PY_T1, 1, Sub_PYF_LightUp
    h_release

// ---- lost, or retired: BattleFrontier_BattlePyramid_EventScript_WarpToLobbyLost
L_PYF_Lost:
    fr_set FR_STATUS, FR_ST_LOST
    h_warp_arrive PY_LOBBY_ZONE, 7 + PY_LOBBY_OX, 13 + PY_LOBBY_OZ, 0
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

// ---- the Start menu's Save: Emerald's REST (save and quit) / RETIRE
PYF_Menu:
    ActorsPauseAll
    ListMenu_AnchorTopRight 31, 6, 0, 1, PY_T0
    ListMenuAdd PYL_FLOOR_M_REST, 65535, 0
    ListMenuAdd PYL_FLOOR_M_RETIRE, 65535, 1
    ListMenuAdd PYL_FLOOR_M_CANCEL, 65535, 2
    ListMenuShow
    h_goto_if_eq PY_T0, 0, L_PYF_Rest
    h_goto_if_eq PY_T0, 1, L_PYF_Retire
    h_release
L_PYF_Rest:                                     // gText_BattlePyramidConfirmRest
    SystemMsg PYL_FLOOR_CONFIRM_REST, 2
    YesNoWin PY_T0
    h_goto_if_ne PY_T0, 0, L_PYF_MenuEnd
    PlayerGetGPos PY_T1, PY_T2
    EmPyr PY_T1, PY_REST_POS, PY_T2             // Continue brings the player back here (through the lobby)
    EmPyr PY_T3, PY_SYNC
    fr_rest_and_quit PY_LOBBY_ZONE, 7 + PY_LOBBY_OX, 13 + PY_LOBBY_OZ, 0, PYL_FLOOR_SAVING, PY_PLAYER
L_PYF_Retire:                                   // gText_BattlePyramidConfirmRetire -> BattlePyramid_Retire
    SystemMsg PYL_FLOOR_CONFIRM_RETIRE, 2
    YesNoWin PY_T0
    h_goto_if_ne PY_T0, 0, L_PYF_MenuEnd
    h_closemessage
    VMJump L_PYF_Lost
L_PYF_MenuEnd:
    h_closemessage
    h_release

// ---- map scripts
PYF_Init:                               // zone init: the objects of this floor, the Battle Bag
    EmPyr PY_T0, PY_SETUP, 0
    VMHalt
PYF_LoadWarp:                           // after a warp: the darkness, the player on the entrance (or where he rested)
    EmPyr PY_T0, PY_LIGHT
    h_flash_scale PY_T0
    h_goto_if_ne PY_W_ARRIVED, 0, L_PYF_LoadEnd
    WorkSetConst PY_W_ARRIVED, 1
    EmPyr PY_T1, PY_START_X
    EmPyr PY_T2, PY_START_Z
    ActorSetGPos PY_PLAYER, PY_T1, 0, PY_T2, 0
    EmPyr PY_T3, PY_ARRIVAL, 0
L_PYF_LoadEnd:
    VMHalt
PYF_LoadBack:                           // back from a battle or a menu: the darkness again
    EmPyr PY_T0, PY_LIGHT
    h_flash_scale PY_T0
    VMHalt
PYF_Ready:                              // ON_RESUME: quit without saving -> the lobby; else ReadyChallenge
    fr_get FR_STATUS, PY_T0
    h_goto_if_eq PY_T0, FR_ST_SAVING, L_PYF_Quit
    EmPyr PY_T1, PY_SYNC                // pyramid_save CHALLENGE_STATUS_SAVING (a quiet save, as Emerald's)
    fr_set FR_STATUS, FR_ST_SAVING
    fr_save_quiet
    fr_set FR_STATUS, PY_ST_IN_CHALLENGE
    WorkSetConst PY_W_STATE, 1
    VMHalt
L_PYF_Quit:                             // BattleFrontier_BattlePyramid_EventScript_WarpToLobby (the lobby says it)
    WorkSetConst PY_W_STATE, 1
    ActorsPauseAll
    h_warp_arrive PY_LOBBY_ZONE, 7 + PY_LOBBY_OX, 13 + PY_LOBBY_OZ, 0
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

    .balign 4, 0
PYF_MvExclaim:
    emote_exclamation_mark
    step_end
    .balign 4, 0
PYF_MvUp:
    walk_up
    step_end
    .balign 4, 0
PYF_MvDown:
    walk_down
    step_end
    .balign 4, 0
PYF_MvLeft:
    walk_left
    step_end
    .balign 4, 0
PYF_MvRight:
    walk_right
    step_end
