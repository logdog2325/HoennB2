// EverGrandeCity_PokemonLeague (zone 77): Sapphire's simple people and signs (as converter/gen_interiors.py makes them),
// plus people that turn back after their message (Common_Movement_FaceOriginalDirection), by the specials agent
// (b2tools/specials.py people). Messages: src/text/script/0087_room_EverGrandeCity_PokemonLeague.txt
#include "asm/field_script.inc"
#include "hoenn.h"  // ch11
#include "hoenn_trainers.h"  // ch11 (before hoenn_story.inc: its macros name trainers)
#include "hoenn_story.inc"  // ch11

    ScriptEntry Script_None
    ScriptEntry EL_Nurse            // 2: object 1 (the nurse): EverGrandeCity_PokemonLeague_1F_EventScript_Nurse  // story:
    ScriptEntry EL_Clerk            // 3: object 2 (the clerk): ..._EventScript_Clerk  // story:
    ScriptEntry EL_DoorGuard        // 4: objects 3 and 4 (the door guards): ..._EventScript_DoorGuard  // story:
    ScriptEntry EL_Init             // 5: zone init (1F's OnTransition)  // story:
    ScriptEntriesEnd

Script_None:
    VMHalt
    .balign 4, 0

// ---- story (chapter Ch11, ch11 agent 2026-10-07; Sapphire data/maps/EverGrandeCity_PokemonLeague/scripts.inc; generators
// must keep everything from this line on; entries above marked "// story:")
// Scripts 2-5, text lines 1-8 (line 0 is the generator's: nurse lines 1-5, the guards' 6-8). Room tiles = Sapphire tiles + (1,1).
// People (data/story/ch11.json, uid = Sapphire local id, NPC list order = indices 0-3): nurse 1 (3,2), clerk 2 (16,2), door
// guards 3 (8,2) and 4 (11,2).
// Black 2 differences:
// - Sapphire's check is FLAG_BADGE06_GET only (pokeruby; the text says "all the Gym Badges"); this checks all eight Badges.
// - setrespawn HEAL_LOCATION_EVER_GRANDE_CITY_POKEMON_LEAGUE / the League as a Fly point: Black 2 respawns at the last Center
//   zone entered (Ever Grande's Center); FLAG_SYS_POKEMON_LEAGUE_FLY is set as Sapphire.
// - Sapphire's whiteout runs EverGrandeCity_HallOfFame_EventScript_ResetEliteFour; Black 2 has no whiteout hook: the battles of
//   the Elite Four and the Champion set FLAG_E4_BATTLE_PENDING (cleared when won), and this zone init resets the Elite Four
//   (the four defeat flags, VAR_ELITE_4_STATE 0) when the flag is still set.
// - The clerk sells Sapphire's list (shop id 20 of data/hoenn_shops.json).
#define EL_NURSE_TEXT 1
#define T_MustHaveAllGymBadges 6
#define T_HaventObtainedAllBadges 7
#define T_GoForth 8
#define EL_GUARD_L 3
#define EL_GUARD_R 4
#define EL_GUARD_L_INDEX 2
#define EL_GUARD_R_INDEX 3
#define EL_X 0x8060
#define EL_Z 0x8061

EL_Init:                                         // EverGrandeCity_PokemonLeague_1F_OnTransition
#ifdef HOENN_TEST_CH11
    VMCall Test_Ch11Start                        // test builds only (scenes/ch11_test.inc)
#endif
    h_setflag FLAG_SYS_POKEMON_LEAGUE_FLY
    h_call_if_set FLAG_E4_BATTLE_PENDING, EL_ResetEliteFour
    h_call_if_unset FLAG_ENTERED_ELITE_FOUR, EL_GuardsBlockDoor
    VMHalt
EL_GuardsBlockDoor:                              // ..._EventScript_GuardsBlockDoor: setobjectxyperm 3, 9, 2 / 4, 10, 2
    ObjInitNPCGPos EL_GUARD_L_INDEX, 1, 10, 0, 3
    ObjInitNPCGPos EL_GUARD_R_INDEX, 1, 11, 0, 3
    VMReturn
EL_ResetEliteFour:                               // EverGrandeCity_HallOfFame_EventScript_ResetEliteFour (Sapphire's whiteout)
    h_clearflag FLAG_DEFEATED_ELITE_4_SYDNEY
    h_clearflag FLAG_DEFEATED_ELITE_4_PHOEBE
    h_clearflag FLAG_DEFEATED_ELITE_4_GLACIA
    h_clearflag FLAG_DEFEATED_ELITE_4_DRAKE
    h_setvar VAR_ELITE_4_STATE, 0
    h_clearflag FLAG_E4_BATTLE_PENDING
    VMReturn

EL_Nurse:                                        // ..._1F_EventScript_Nurse (Common_EventScript_PkmnCenterNurse: centers/nurse.inc
                                                 // with the five nurse lines at EL_NURSE_TEXT + 0-4)
    ActorsPauseAll
    SEPlay SEQ_SE_MESSAGE
    ActorSetEyeToEye
    ParentActorMsg MSGFILE_SCRIPT, EL_NURSE_TEXT + 0, 0, 0       // welcome, rest your Pokémon?
    YesNoWin 0x8000
    WorkCmpConst 0x8000, 0                       // 0 = yes
    VMJumpIf CMP_EQ, L_NurseHeal
    ParentActorMsg MSGFILE_SCRIPT, EL_NURSE_TEXT + 3, 0, 0       // no: "We hope to see you again!"
    LastKeyWait
    ActorMsgClose
    VMJump L_NurseEnd

L_NurseHeal:
    ActorMsgClose
    PlayerSetSpecialSequence 64                  // the player hands the Balls over (Black 2)
    ActorCmdExec 255, Movement_NursePlayerGive
    ActorCmdWait
    PlayerSetSpecialSequence 8
    ActorCmdExec 255, Movement_NursePlayerFaceUp
    ActorCmdWait
    ParentActorMsg MSGFILE_SCRIPT, EL_NURSE_TEXT + 1, 0, 0       // "Okay, I'll take your Pokémon for a few seconds."
    ActorCmdExec 0x8011, Movement_NurseFaceMachine
    ActorCmdWait
    PokePartyGetCount 0x8001, 1
    PokecenPlayHealingSequence 0x8001
    ActorCmdExec 0x8011, Movement_NurseFaceDown
    ActorCmdWait
    PokePartyRecoverAll
    RecordAdd 11, 1                              // Black 2's "Pokémon Center used" record (Sapphire GAME_STAT_USED_POKECENTER)
    ActorMsgClose
    PlayerSetSpecialSequence 64                  // the Balls come back
    ActorCmdExec 255, Movement_NursePlayerTake
    ActorCmdWait
    PlayerSetSpecialSequence 8
    PokePartyCheckPokerus 0x8002
    WorkCmpConst 0x8002, 1
    VMJumpIf CMP_NE, L_NurseReturn
    FlagGet 101, 0x8003
    WorkCmpConst 0x8003, 0
    VMJumpIf CMP_NE, L_NurseReturn
    FlagSet 101
    ParentActorMsg MSGFILE_SCRIPT, EL_NURSE_TEXT + 4, 0, 0       // Pokérus (instead of the thanks, as Sapphire)
    LastKeyWait
    ActorMsgClose
    VMJump L_NurseEnd

L_NurseReturn:
    ParentActorMsg MSGFILE_SCRIPT, EL_NURSE_TEXT + 2, 0, 0       // "Thank you for waiting..."
    ActorCmdExec 0x8011, Movement_NurseBow
    ActorCmdWait
    ParentActorMsg MSGFILE_SCRIPT, EL_NURSE_TEXT + 3, 0, 0       // "We hope to see you again!"
    LastKeyWait
    ActorMsgClose

L_NurseEnd:
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

EL_Clerk:                                        // ..._1F_EventScript_Clerk: pokemart EverGrandeCity_PokemonLeague_Items
    ActorsPauseAll
    SEPlay SEQ_SE_MESSAGE
    ActorSetEyeToEye
    VMStackPush 0x8000
    VMStackPush 0x8001
    WorkSet 0x8000, 20                           // EverGrandeCity_PokemonLeague_Items (b2tools/shops_data.py)
    WorkSet 0x8001, 1
    RTCallGlobal 10110
    VMStackPop 0x8001
    VMStackPop 0x8000
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

EL_DoorGuard:                                    // ..._1F_EventScript_DoorGuard (lockall)
    ActorsPauseAll
    h_goto_if_set FLAG_ENTERED_ELITE_FOUR, L_EL_GoForth
    PlayerGetGPos EL_X, EL_Z
    h_goto_if_lt EL_X, 12, L_EL_NotRight         // Sapphire x >= 11: PlayerMoveToFrontFromRight
    VMCall EL_PlayerMoveToFrontFromRight
L_EL_NotRight:
    h_goto_if_gt EL_X, 9, L_EL_NotLeft           // Sapphire x <= 8: PlayerMoveToFrontFromLeft
    VMCall EL_PlayerMoveToFrontFromLeft
L_EL_NotLeft:
    ParentActorMsg MSGFILE_SCRIPT, T_MustHaveAllGymBadges, 0, 0   // Beyond this point, only those Trainers who have collected all ...
    VMSleep 38                                   // delay 75 (the window stays open)
    h_goto_if_no_badge 1, L_EL_NotAllBadges
    h_goto_if_no_badge 2, L_EL_NotAllBadges
    h_goto_if_no_badge 3, L_EL_NotAllBadges
    h_goto_if_no_badge 4, L_EL_NotAllBadges
    h_goto_if_no_badge 5, L_EL_NotAllBadges
    h_goto_if_no_badge 6, L_EL_NotAllBadges
    h_goto_if_no_badge 7, L_EL_NotAllBadges
    h_goto_if_no_badge 8, L_EL_NotAllBadges
    MsgWinCloseAll
    h_applymovement EL_GUARD_L, Mv_EL_LeftGuardOutOfWay
    h_applymovement EL_GUARD_R, Mv_EL_RightGuardOutOfWay
    h_waitmovement
    VMSleep 5                                    // delay 10
    MEPlay SEQ_ME_BADGE                          // MUS_OBTAIN_BADGE
    ParentActorMsg MSGFILE_SCRIPT, T_GoForth, 0, 0    // Trainer! Believe in yourself and your Pokémon, and go forth!
    MEWait
    MsgWinCloseAll
    ActorDelete EL_GUARD_L                       // moveobjectoffscreen 3 / 4
    ActorDelete EL_GUARD_R
    h_setflag FLAG_ENTERED_ELITE_FOUR
    h_release
L_EL_NotAllBadges:                               // ..._EventScript_NotAllBadges
    SEPlay SEQ_SE_BEEP                           // SE_FAILURE [guess]
    MsgWinCloseAll
    h_msgbox T_HaventObtainedAllBadges           // You haven't obtained all the Badges. If you're bound for the Pokémon League ...
    h_release
L_EL_GoForth:                                    // ..._EventScript_GoForth
    ActorSetEyeToEye
    h_msgbox T_GoForth
    h_closemessage
    h_turnobject EL_GUARD_L, 1                   // FaceOriginalDirection (both guards face down)
    h_turnobject EL_GUARD_R, 1
    h_release

EL_PlayerMoveToFrontFromRight:
    h_applymovement 255, Mv_EL_MoveToFrontFromRight
    h_waitmovement
    VMReturn
EL_PlayerMoveToFrontFromLeft:
    h_applymovement 255, Mv_EL_MoveToFrontFromLeft
    h_waitmovement
    VMReturn

    .balign 4, 0
Mv_EL_MoveToFrontFromRight:                      // ..._Movement_MoveToFrontFromRight
    walk_down
    walk_left
    walk_in_place_fastest_up
    step_end
Mv_EL_MoveToFrontFromLeft:
    walk_down
    walk_right
    walk_in_place_fastest_up
    step_end
Mv_EL_LeftGuardOutOfWay:
    walk_left
    walk_in_place_fastest_down
    step_end
Mv_EL_RightGuardOutOfWay:
    walk_right
    walk_in_place_fastest_down
    step_end
Movement_NurseBow:                               // Black 2's bow (1231.s Movement_0594)
    Move 100, 1
    Move 62, 1
    MoveEnd
Movement_NursePlayerGive:                        // 1231.s Movement_05A0
    Move 102, 1
    MoveEnd
Movement_NursePlayerFaceUp:                      // 1231.s Movement_05A8
    Move 0, 1
    MoveEnd
Movement_NursePlayerTake:                        // 1231.s Movement_05B0
    Move 104, 1
    MoveEnd
Movement_NurseFaceMachine:                       // face left: the machine is on her left (Sapphire)
    Move 2, 1
    MoveEnd
Movement_NurseFaceDown:
    Move 1, 1
    MoveEnd

#include "common/movement.inc"
#include "scenes/ch11_test.inc"
