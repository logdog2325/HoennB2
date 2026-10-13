// Lavaridge Town's story (Sapphire data/maps/LavaridgeTown/scripts.inc; chapter Ch5, ch5 agent 2026-10-07).
// converter/gen_map_content.py includes this file twice in 0124_auto_LavaridgeTown.s: the entries below are scripts
// 1-5, the generated signs/people follow. Text: src/text/scenes/LavaridgeTown.txt (lines LV_T_* below). People:
// data/story/ch5.json (uid = 100 + Sapphire local id: the rival 108, the rival on the bike 107, the Egg woman 109).
// Map scripts: scenes/LavaridgeTown_init.inc (zone init = script 1, VAR_LAVARIDGE_RIVAL_STATE 1 -> script 2).
// Not ported: LavaridgeTown_EventScript_HotSpringsTrigger (incrementgamestat GAME_STAT_ENTERED_HOT_SPRINGS: no
// Black 2 record for it, nothing shows). Sapphire's whiteout hook EventScript_TryReadyRivalForGoGoggles (rival
// waiting at (11,9) after a blackout) has no Black 2 hook: script 2 does it when the player is not at the Gym door.
#ifdef SCENE_ENTRIES
    ScriptEntry LV_Init                 // 1: LavaridgeTown_OnTransition (zone init)
    ScriptEntry LV_RivalGiveGoGoggles   // 2: LavaridgeTown_OnFrame (VAR_LAVARIDGE_RIVAL_STATE 1)
    ScriptEntry LV_Rival                // 3: object 8 (LavaridgeTown_EventScript_14E575)
    ScriptEntry LV_EggWoman             // 4: object 9 (LavaridgeTown_EventScript_EggWoman)
    ScriptEntry LV_GymSign              // 5: LavaridgeTown_EventScript_GymSign sign (7,15)
#else
#include "hoenn_key_items.h"
#define LV_T_MayNice 0
#define LV_T_BrendanNice 1
#define LV_T_MayExplain 2
#define LV_T_BrendanExplain 3
#define LV_T_HaveEgg 4
#define LV_T_HopeWalk 5
#define LV_T_ReceivedEgg 6
#define LV_T_NoRoom 7
#define LV_T_AsYouWish 8
#define LV_T_EverySoOften 9
#define LV_T_GymSign 10
#define LV_RIVAL 108                    // object 8 (walking rival)
#define LV_RIVAL_BIKE 107               // object 7 (Sapphire: on the bike; the walking sprite stands in)
#define LV_X(x) (188+(x))               // Sapphire tile -> world tile (b2tools/world.py offset of LavaridgeTown)
#define LV_Z(z) (120+(z))
#define LV_GY 2                         // (ActorSetGPos' y is the grid height: Lavaridge's ground is 32 units = 2, as Littleroot's 16 = 1)
#define LV_STORY_NPC0 6                 // zone 62's NPC list: 6 generated people, then data/story/ch5.json's 108, 107, 109
#define LV_FROM_SHOP 0x8024             // VAR_0x8008: 1 = the rival came out of the Herb Shop, 0 = talked to
#define LV_FACING 0x8025                // VAR_FACING (Black 2 directions: 0 up, 1 down, 2 left, 3 right)
#define LV_PX 0x8026
#define LV_PZ 0x8027

LV_Init:                                // LavaridgeTown_OnTransition
    h_setflag FLAG_VISITED_LAVARIDGE_TOWN
    h_goto_if_unset FLAG_DEFEATED_EVIL_TEAM_MT_CHIMNEY, L_LV_Init1
    h_clearflag FLAG_HIDE_MT_CHIMNEY_PEOPLE     // LavaridgeTown_EventScript_ShowMtChimneyTrainers
L_LV_Init1:
    h_setup_rival_gfx                   // Common_EventScript_SetupRivalGfxId
    h_setup_rival_bike_gfx              // Common_EventScript_SetupRivalOnBikeGfxId (the walking rival for now)
    h_goto_if_ne VAR_LAVARIDGE_RIVAL_STATE, 2, L_LV_Init2
    ObjInitNPCGPos (LV_STORY_NPC0+0), 1, LV_X(11), 0, LV_Z(9)   // LavaridgeTown_EventScript_SetRivalPos: objects 8, 7
    ObjInitNPCGPos (LV_STORY_NPC0+1), 2, LV_X(11), 0, LV_Z(9)
L_LV_Init2:
#ifdef HOENN_TEST_CH5
    VMCall Test_Ch5Start
#endif
    VMHalt

LV_RivalGiveGoGoggles:                  // LavaridgeTown_EventScript_RivalGiveGoGoggles (after Flannery, out of the Gym)
    h_lock
    PlayerGetGPos LV_PX, LV_PZ
    WorkCmpConst LV_PX, LV_X(5)         // (not at the Gym door: Sapphire's blackout case, see the header)
    VMJumpIf CMP_NE, L_LV_NotFromGym
    WorkCmpConst LV_PZ, LV_Z(16)
    VMJumpIf CMP_NE, L_LV_NotFromGym
    h_setvar LV_FROM_SHOP, 1
    BMCreateHandleByGPos 0x8020, 1, LV_X(12), LV_Z(15)  // opendoor 12, 15 (the Herb Shop's door)
    BMHndAudioVisualAnmPlay 0x8020, 0
    BMHndAnmWait 0x8020
    h_addobject LV_RIVAL, FLAG_HIDE_RIVAL_LAVARIDGE_1
    h_applymovement LV_RIVAL, Mv_LV_RivalExitHerbShop
    h_waitmovement
    BMHndAudioVisualAnmPlay 0x8020, 1   // closedoor
    BMHndAnmWait 0x8020
    BMReleaseHandle 0x8020
    h_applymovement LV_RIVAL, Common_Movement_WalkInPlaceFastestLeft
    h_waitmovement
    h_applymovement 255, Common_Movement_WalkInPlaceFastestRight
    h_applymovement LV_RIVAL, Common_Movement_ExclamationMark
    h_waitmovement
    h_applymovement LV_RIVAL, Common_Movement_Delay48
    h_waitmovement
    h_goto_if_girl L_LV_MusicBrendan1   // PlayMayMusic / PlayBrendanMusic (music_fix: was May's for both)
    h_playbgm MUS_ENCOUNTER_MAY
    VMJump L_LV_Music1
L_LV_MusicBrendan1:
    h_playbgm MUS_ENCOUNTER_BRENDAN
L_LV_Music1:
    h_applymovement LV_RIVAL, Mv_LV_RivalApproachPlayer2
    h_waitmovement
    VMJump L_LV_GiveGoGoggles

LV_Rival:                               // LavaridgeTown_EventScript_14E575 (state 2: the rival waits at (11,9))
    h_lock
    SEPlay SEQ_SE_MESSAGE
    h_faceplayer
    h_setvar LV_FROM_SHOP, 0
    h_goto_if_girl L_LV_MusicBrendan2
    h_playbgm MUS_ENCOUNTER_MAY
    VMJump L_LV_GiveGoGoggles
L_LV_MusicBrendan2:
    h_playbgm MUS_ENCOUNTER_BRENDAN
L_LV_GiveGoGoggles:                     // LavaridgeTown_EventScript_MayGiveGoGoggles / BrendanGiveGoGoggles
    h_buffer_player
    h_msgbox_gendered LV_T_MayNice, LV_T_BrendanNice, LV_RIVAL      // ... I guess it would be okay for you to have this.
    h_closemessage
    h_giveitem ITEM_GO_GOGGLES
    h_setflag FLAG_RECEIVED_GO_GOGGLES
    h_buffer_player
    h_msgbox_gendered LV_T_MayExplain, LV_T_BrendanExplain, LV_RIVAL  // With those Go-Goggles, ... see you again!
    h_closemessage                      // LavaridgeTown_EventScript_RivalExit
    h_getplayerfacing LV_FACING
    h_removeobject LV_RIVAL, FLAG_HIDE_RIVAL_LAVARIDGE_1
    h_addobject LV_RIVAL_BIKE, FLAG_HIDE_RIVAL_LAVARIDGE_2
    h_goto_if_eq LV_FROM_SHOP, 0, L_LV_BikeAtTalk
    ActorSetGPos LV_RIVAL_BIKE, LV_X(6), LV_GY, LV_Z(16), 2  // LavaridgeTown_EventScript_14E646: setobjectxyperm 7, 6, 16
    VMJump L_LV_BikeSet
L_LV_BikeAtTalk:                        // LavaridgeTown_EventScript_14E64E: at (11,9), facing the player
    h_call_if_eq LV_FACING, 0, Sub_LV_BikeFaceDown
    h_call_if_eq LV_FACING, 1, Sub_LV_BikeFaceUp
    h_call_if_eq LV_FACING, 2, Sub_LV_BikeFaceRight
    h_call_if_eq LV_FACING, 3, Sub_LV_BikeFaceLeft
L_LV_BikeSet:
    h_delay 30
    h_goto_if_eq LV_FROM_SHOP, 0, L_LV_ExitTalk
    h_applymovement LV_RIVAL_BIKE, Mv_LV_RivalExit2     // LavaridgeTown_EventScript_RivalExit2
    h_waitmovement
    VMJump L_LV_Gone
L_LV_ExitTalk:                          // LavaridgeTown_EventScript_14E6A5
    h_goto_if_eq LV_FACING, 2, L_LV_ExitDown
    h_applymovement LV_RIVAL_BIKE, Mv_LV_14E6FA
    h_waitmovement
    VMJump L_LV_Gone
L_LV_ExitDown:                          // (player facing west) LavaridgeTown_EventScript_RivalExit1
    h_applymovement LV_RIVAL_BIKE, Mv_LV_RivalExit1
    h_waitmovement
L_LV_Gone:
    h_removeobject LV_RIVAL_BIKE, FLAG_HIDE_RIVAL_LAVARIDGE_2
    h_setvar VAR_LAVARIDGE_RIVAL_STATE, 2
    h_fadedefaultbgm                    // savebgm 0 + fadedefaultbgm
    h_release

L_LV_NotFromGym:                        // EventScript_TryReadyRivalForGoGoggles: the rival waits at (11,9)
    h_setvar VAR_LAVARIDGE_RIVAL_STATE, 2
    h_addobject LV_RIVAL, FLAG_HIDE_RIVAL_LAVARIDGE_1
    ActorSetGPos LV_RIVAL, LV_X(11), LV_GY, LV_Z(9), 1
    h_release

Sub_LV_BikeFaceDown:                    // setobjectmovementtype 7, FACE_DOWN (player above)
    ActorSetGPos LV_RIVAL_BIKE, LV_X(11), LV_GY, LV_Z(9), 1
    VMReturn
Sub_LV_BikeFaceUp:
    ActorSetGPos LV_RIVAL_BIKE, LV_X(11), LV_GY, LV_Z(9), 0
    VMReturn
Sub_LV_BikeFaceRight:
    ActorSetGPos LV_RIVAL_BIKE, LV_X(11), LV_GY, LV_Z(9), 3
    VMReturn
Sub_LV_BikeFaceLeft:
    ActorSetGPos LV_RIVAL_BIKE, LV_X(11), LV_GY, LV_Z(9), 2
    VMReturn

LV_EggWoman:                            // LavaridgeTown_EventScript_EggWoman
    h_lock
    SEPlay SEQ_SE_MESSAGE
    h_faceplayer
    h_goto_if_set FLAG_RECEIVED_LAVARIDGE_EGG, L_LV_ReceivedEgg
    h_yesno LV_T_HaveEgg, HLIB_TMP      // I have here an Egg. ... Will you take this Egg to hatch?
    h_goto_if_no HLIB_TMP, L_LV_DeclineEgg
    h_getpartysize HLIB_TMP
    h_goto_if_eq HLIB_TMP, 6, L_LV_NoRoom
    h_msgbox LV_T_HopeWalk              // Good! I hope you'll walk plenty with this here Egg!
    h_closemessage
    h_setflag FLAG_RECEIVED_LAVARIDGE_EGG
    h_playfanfare MUS_OBTAIN_ITEM
    h_buffer_player
    SystemMsg LV_T_ReceivedEgg, 1       // <player> received the Egg.
    h_waitfanfare
    MsgWaitAdvance
    InfoMsgClose
    PokePartyAddEgg HLIB_TMP, SPECIES_WYNAUT, 0     // giveegg SPECIES_WYNAUT
    h_release
L_LV_ReceivedEgg:
    h_msgbox LV_T_EverySoOften          // Every so often, an Egg will be found at the Pokémon Day Care. ...
    h_release
L_LV_NoRoom:
    h_msgbox LV_T_NoRoom                // Oh? You've too many Pokémon. There's no room for this Egg...
    h_release
L_LV_DeclineEgg:
    h_msgbox LV_T_AsYouWish             // As you wish, then... ...
    h_release

LV_GymSign:                             // LavaridgeTown_EventScript_GymSign
    h_msgbox_sign LV_T_GymSign

    .balign 4, 0
Mv_LV_RivalExitHerbShop:
    walk_down
    step_end
Mv_LV_RivalApproachPlayer2:
    walk_left 6
    step_end
Mv_LV_RivalExit2:
    walk_fast_right 3
    walk_fast_up 7
    step_end
Mv_LV_14E6FA:
    walk_fast_right 8
    step_end
Mv_LV_RivalExit1:
    walk_fast_down
    walk_fast_right 9
    step_end
#include "common/movement.inc"
#ifdef HOENN_TEST_CH5
#include "scenes/ch5_test.inc"
#endif
#endif
