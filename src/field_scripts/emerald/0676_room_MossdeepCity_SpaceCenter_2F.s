// MossdeepCity_SpaceCenter_2F (zone 338), EMERALD ONLY (emerald_ch9_mirage 2026-10-12, builder B5; pokeemerald data/maps/MossdeepCity_SpaceCenter_2F/
// scripts.inc): replaces src/field_scripts/0676_room_MossdeepCity_SpaceCenter_2F.s in an Emerald build. Scripts 1-3 are the three generated people
// (data/interiors/338.json: rich boy (6,2) = uid 1, gentleman (11,8) = uid 2, scientist (5,6) = uid 3) with Emerald's two lines each; 4-9 the Magma story
// (data/story/emerald/e_ch9_mirage.json, uid = pokeemerald's local id: Steven 4, grunt 6 = 5, grunt 5 = 6, grunt 7 = 7, Tabitha 8, Maxie 9); 10 the
// zone init, 11 the scene that starts when you come up the stairs (map-script condition VAR_MOSSDEEP_SPACE_CENTER_STATE 1, 0677 init).
// Text: src/text/script/emerald/0550_room_MossdeepCity_SpaceCenter_2F.txt (converter/gen_emerald_ch9_text.py). Room tiles = pokeemerald tiles + (1, 1).
// The story: three Magma grunts wait at the top of the stairs ("You're outnumbered three to one"): YES = battle them one after the other (their
// intros are lines of this scene, their defeat lines the trainers'), NO = back down the stairs. Beaten (VAR_MOSSDEEP_SPACE_CENTER_STATE 2) the
// grunts stand aside and Maxie, Tabitha and Steven are free to talk to: Steven first tells Maxie off (Maxie: they will make Mt. Chimney erupt with
// the rocket fuel; the first talk only), then asks "Are you ready?": YES = em_tag_battle (the one party menu, 1 to 3 Pokémon, Steven's own three beside
// them, against Maxie and Tabitha; a loss whites out as Emerald's SetCB2WhiteOut; B = back to the question). Won: Maxie gives up, everyone leaves,
// Steven thanks you and goes home (his house shows him, the Dive is due: VAR_STEVENS_HOUSE_STATE 1), Scott in town is gone.
// Black 2 gaps: pokeemerald's Rayquaza call from the rival (250 steps after the fight, a PokéNav message) is not built (no step hook; EMERALD_STORY Ch9);
// SE_NOT_EFFECTIVE (Steven pushed back) is Black 2's dull thud, a guess.
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_trainers.h"
#include "hoenn_story.inc"
#include "hoenn_emerald.inc"                // em_tag_battle
#include "hoenn_version.inc"                // TRAINER_STEVEN_PARTNER, TRAINER_MAXIE_MOSSDEEP, TRAINER_TABITHA_MOSSDEEP, TRAINER_GRUNT_SPACE_CENTER_5-7

    ScriptEntry SC2_RichBoy                 // 1: rich boy (6,2), uid 1
    ScriptEntry SC2_Gentleman               // 2: gentleman (11,8), uid 2
    ScriptEntry SC2_Scientist               // 3: scientist (5,6), uid 3
    ScriptEntry SC2_Steven                  // 4: Steven (1,8), uid 4
    ScriptEntry SC2_Grunt6                  // 5: grunt 6 (12,2), uid 5
    ScriptEntry SC2_Grunt5                  // 6: grunt 5 (13,3), uid 6
    ScriptEntry SC2_Grunt7                  // 7: grunt 7 (14,2), uid 7
    ScriptEntry SC2_Tabitha                 // 8: Tabitha (0,8), uid 8
    ScriptEntry SC2_Maxie                   // 9: Maxie (1,9), uid 9
    ScriptEntry SC2_Init                    // 10: zone init (MossdeepCity_SpaceCenter_2F_OnTransition)
    ScriptEntry SC2_ThreeGrunts             // 11: OnFrame VAR_MOSSDEEP_SPACE_CENTER_STATE 1 (MossdeepCity_SpaceCenter_2F_EventScript_ThreeMagmaGrunts)
    ScriptEntriesEnd

#include "scenes/ch9_lib.inc"
#define T_RichBoyNormal 0                   // text lines (0550): the three people's Sapphire-indexed lines, then Magma's
#define T_GentlemanNormal 1
#define T_ScientistNormal 2
#define T_ScientistMagma 3
#define T_GentlemanMagma 4
#define T_RichBoyMagma 5
#define T_Outnumbered 6
#define T_GoodAnswer 7
#define T_Grunt5Intro 8
#define T_Grunt6Intro 9
#define T_Grunt7Intro 10
#define T_Grunt6Post 11
#define T_Grunt7Post 12
#define T_Grunt5Post 13
#define T_WellTakeCare 14
#define T_MaxieDontInterfere 15
#define T_StevenWhyStealFuel 16
#define T_MaxieEruptVolcano 17
#define T_StevenAreYouReady 18
#define T_StevenHurry 19
#define T_MaxieWeFailed 20
#define T_MaxieGiveUp 21
#define T_StevenThankYou 22
#define SC2_RICH_BOY 1                      // uids
#define SC2_GENTLEMAN 2
#define SC2_SCIENTIST 3
#define SC2_STEVEN 4
#define SC2_GRUNT_6 5
#define SC2_GRUNT_5 6
#define SC2_GRUNT_7 7
#define SC2_TABITHA 8
#define SC2_MAXIE 9
#define SC2_X(x) ((x) + 1)                  // pokeemerald tile -> zone tile (the room's origin)
#define SC2_Z(z) ((z) + 1)
#define SC2_I_RICH_BOY 0                    // positions in the zone's NPC list (ObjInitNPCGPos): the three generated people, then Steven 3, grunt 6 = 4,
#define SC2_I_GENTLEMAN 1                   // grunt 5 = 5, grunt 7 = 6 (the json's order)
#define SC2_I_SCIENTIST 2
#define SC2_I_GRUNT_6 4
#define SC2_I_GRUNT_5 5
#define SC2_I_GRUNT_7 6
#define SC2_SE_THUD SEQ_SE_FLD_154          // [guess] SE_NOT_EFFECTIVE: Black 2's dull thud of its cave scenes (JaggedPass.inc JP_SE_THUD)

SC2_RichBoy:                                // MossdeepCity_SpaceCenter_2F_EventScript_RichBoy (lock, faceplayer)
    c9_talk
    h_goto_if_set FLAG_SYS_GAME_CLEAR, L_SC2_RichBoyNormal
    h_goto_if_eq VAR_MOSSDEEP_CITY_STATE, 2, L_SC2_RichBoyMagma
    h_goto_if_lt VAR_MOSSDEEP_CITY_STATE, 2, L_SC2_RichBoyNormal
L_SC2_RichBoyMagma:
    h_msgbox T_RichBoyMagma             // Team Magma... Do they want to go to space, too?
    h_release
L_SC2_RichBoyNormal:
    h_msgbox T_RichBoyNormal            // I wish ordinary people could go into space one day...
    h_release

SC2_Gentleman:                              // MossdeepCity_SpaceCenter_2F_EventScript_Gentleman
    c9_talk
    h_goto_if_set FLAG_SYS_GAME_CLEAR, L_SC2_GentlemanNormal
    h_goto_if_eq VAR_MOSSDEEP_CITY_STATE, 2, L_SC2_GentlemanMagma
    h_goto_if_lt VAR_MOSSDEEP_CITY_STATE, 2, L_SC2_GentlemanNormal
L_SC2_GentlemanMagma:
    h_msgbox T_GentlemanMagma           // If Team Magma takes the rocket fuel, I won't be able to go to space! ...
    h_release
L_SC2_GentlemanNormal:
    h_msgbox T_GentlemanNormal          // If only I was a little younger, I would have liked being an astronaut... ...
    h_release

SC2_Scientist:                              // MossdeepCity_SpaceCenter_2F_EventScript_Scientist
    c9_talk
    h_goto_if_set FLAG_SYS_GAME_CLEAR, L_SC2_ScientistNormal
    h_goto_if_eq VAR_MOSSDEEP_CITY_STATE, 2, L_SC2_ScientistMagma
    h_goto_if_lt VAR_MOSSDEEP_CITY_STATE, 2, L_SC2_ScientistNormal
L_SC2_ScientistMagma:
    h_msgbox T_ScientistMagma           // Why would Team Magma want to steal our rocket fuel in the first place?
    h_release
L_SC2_ScientistNormal:
    h_msgbox T_ScientistNormal          // Mossdeep has mainly sunny weather, and its winds are stable. ...
    h_release

SC2_Grunt6:                                 // ..._EventScript_Grunt6 (MSGBOX_NPC: the line after the fight)
    h_msgbox_npc T_Grunt6Post           // Three of us here, and look at the sorry mess we got ourselves into.
SC2_Grunt7:
    h_msgbox_npc T_Grunt7Post           // We three losing like this... We look worse than usual by triple!
SC2_Grunt5:
    h_msgbox_npc T_Grunt5Post           // Are we being useful to our leader at all?

SC2_Tabitha:                                // ..._EventScript_Tabitha (lock, faceplayer)
    c9_talk
    h_msgbox T_WellTakeCare             // Hehehe! We come all the way here to get some fuel, and we're interfered with again! ...
    h_closemessage
    h_turnobject SC2_TABITHA, 3         // Common_Movement_FaceOriginalDirection (FACE_RIGHT)
    h_release

SC2_Maxie:                                  // ..._EventScript_Maxie (lockall: he does not turn to you)
    c9_lock
    h_msgbox_actor T_MaxieDontInterfere, SC2_MAXIE     // Maxie: Clear out of the way! Don't you dare interfere!
    h_closemessage
    h_release

SC2_Steven:                                 // ..._EventScript_Steven (lockall)
    c9_lock
    h_goto_if_set FLAG_INTERACTED_WITH_STEVEN_SPACE_CENTER, L_SC2_ReadyPrompt
    h_setflag FLAG_INTERACTED_WITH_STEVEN_SPACE_CENTER
    h_msgbox_actor T_StevenWhyStealFuel, SC2_STEVEN   // Steven: Team Magma... What's the point of stealing rocket fuel?
    h_msgbox_actor T_MaxieEruptVolcano, SC2_MAXIE     // Maxie: Fufufu... Since you're so curious, you deserve an explanation. We're going to jettison the entire load into Mt. Chimney! ...
    h_closemessage
    h_delay 30
    SEPlay SC2_SE_THUD                  // playse SE_NOT_EFFECTIVE
    h_getplayerfacing C9_A              // VAR_FACING: DIR_SOUTH (the player faces down) has Steven pushed aside instead of back
    h_goto_if_eq C9_A, 1, L_SC2_StevenFightSouth
    h_applymovement SC2_STEVEN, Mv_SC2_StevenFight
    h_waitmovement
    h_release
L_SC2_StevenFightSouth:                     // ..._EventScript_StevenFightMovementSouth
    h_applymovement SC2_STEVEN, Mv_SC2_StevenFightSouth
    h_waitmovement
    h_release
L_SC2_ReadyPrompt:                          // ..._EventScript_ReadyForBattlePrompt
    h_faceplayer                            // applywaitmovement VAR_LAST_TALKED, Common_Movement_FacePlayer
    h_yesno_actor T_StevenAreYouReady, SC2_STEVEN, C9_A      // Steven: <player>! You're going to help me? Let's go into battle together! Are you ready?
    h_goto_if_yes C9_A, L_SC2_Choose
    h_msgbox_actor T_StevenHurry, SC2_STEVEN         // Steven: Then, hurry! Get ready quickly!
    h_closemessage
    h_turnobject SC2_STEVEN, 1              // Common_Movement_WalkInPlaceFasterDown
    h_release
L_SC2_Choose:                               // ..._EventScript_ChoosePartyForMultiBattle + DoStevenMultiBattle
    h_closemessage
    h_turnobject SC2_STEVEN, 1
    em_tag_battle TRAINER_STEVEN_PARTNER, TRAINER_MAXIE_MOSSDEEP, TRAINER_TABITHA_MOSSDEEP, L_SC2_ReadyPrompt
    // won (a loss whites out, the menu left with B goes back to "Are you ready?"): ..._EventScript_DefeatedMaxieTabitha
    h_msgbox_actor T_MaxieWeFailed, SC2_MAXIE        // Maxie: We failed to make the volcano erupt... Is our goal to expand the land misguided? ...
    h_closemessage
    h_delay 20
    h_applymovement SC2_MAXIE, Common_Movement_WalkInPlaceFastestLeft
    h_applymovement SC2_TABITHA, Common_Movement_WalkInPlaceFastestDown
    h_waitmovement
    h_delay 60
    h_applymovement SC2_MAXIE, Common_Movement_WalkInPlaceFastestUp
    h_applymovement SC2_TABITHA, Common_Movement_WalkInPlaceFastestRight
    h_waitmovement
    h_delay 20
    h_msgbox_actor T_MaxieGiveUp, SC2_MAXIE          // Maxie: All right... We will give up on the fuel... There appear to be more important matters that I must examine...
    h_closemessage
    h_setvar VAR_MOSSDEEP_CITY_STATE, 3
    h_fadedefaultbgm
    h_fadescreen_black
    h_setvar VAR_MOSSDEEP_SPACE_CENTER_STATE, 3
    h_setflag FLAG_HIDE_MOSSDEEP_CITY_SPACE_CENTER_1F_TEAM_MAGMA
    h_setflag FLAG_HIDE_MOSSDEEP_CITY_SPACE_CENTER_2F_TEAM_MAGMA
    h_setflag FLAG_HIDE_MOSSDEEP_CITY_TEAM_MAGMA
    h_removeobject SC2_GRUNT_6, FLAG_HIDE_MOSSDEEP_CITY_SPACE_CENTER_2F_TEAM_MAGMA
    h_removeobject SC2_GRUNT_7, FLAG_HIDE_MOSSDEEP_CITY_SPACE_CENTER_2F_TEAM_MAGMA
    h_removeobject SC2_GRUNT_5, FLAG_HIDE_MOSSDEEP_CITY_SPACE_CENTER_2F_TEAM_MAGMA
    h_removeobject SC2_TABITHA, FLAG_HIDE_MOSSDEEP_CITY_SPACE_CENTER_2F_TEAM_MAGMA
    h_removeobject SC2_MAXIE, FLAG_HIDE_MOSSDEEP_CITY_SPACE_CENTER_2F_TEAM_MAGMA
    ActorSetGPos SC2_SCIENTIST, SC2_X(5), 0, SC2_Z(6), 1      // setobjectxy SCIENTIST 5,6 + turnobject SOUTH
    ActorSetGPos SC2_GENTLEMAN, SC2_X(11), 0, SC2_Z(8), 0     // 11,8 NORTH
    ActorSetGPos SC2_RICH_BOY, SC2_X(6), 0, SC2_Z(2), 0       // 6,2 NORTH
    h_getplayerfacing C9_A                  // ..._EventScript_StevenFacePlayer: DIR_SOUTH -> Steven turns north, DIR_WEST -> east
    h_goto_if_eq C9_A, 1, L_SC2_StevenFaceNorth
    h_goto_if_ne C9_A, 2, L_SC2_StevenFaced
    h_turnobject SC2_STEVEN, 3
    VMJump L_SC2_StevenFaced
L_SC2_StevenFaceNorth:
    h_turnobject SC2_STEVEN, 0
L_SC2_StevenFaced:
    h_fadescreen_from_black
    h_msgbox_actor T_StevenThankYou, SC2_STEVEN      // Steven: Whew, that was too tense. <player>, thank you. I have something to give you as thanks ... Please come see me at home ...
    h_closemessage
    h_fadescreen_black
    h_setflag FLAG_DEFEATED_MAGMA_SPACE_CENTER
    h_setflag FLAG_HIDE_MOSSDEEP_CITY_STEVENS_HOUSE_STEVEN
    h_removeobject SC2_STEVEN, FLAG_HIDE_MOSSDEEP_CITY_SPACE_CENTER_2F_STEVEN
    h_setflag FLAG_HIDE_MOSSDEEP_CITY_SPACE_CENTER_MAGMA_NOTE
    h_clearflag FLAG_HIDE_MOSSDEEP_CITY_STEVENS_HOUSE_STEVEN   // Steven is at home (his house, 0678)
    h_setvar VAR_STEVENS_HOUSE_STATE, 1                        // 1 = the Dive is due (Emerald's numbering; 2 = given)
    h_setflag FLAG_HIDE_MOSSDEEP_CITY_SCOTT
    h_fadescreen_from_black
    h_release

SC2_Init:                                   // MossdeepCity_SpaceCenter_2F_OnTransition
    h_goto_if_ne VAR_MOSSDEEP_CITY_STATE, 2, L_SC2I_Defeated
    h_clearflag FLAG_INTERACTED_WITH_STEVEN_SPACE_CENTER     // ..._EventScript_MoveCivilians
    h_setobjectxyperm SC2_I_SCIENTIST, SC2_X(5), SC2_Z(3), 3
    h_setobjectxyperm SC2_I_RICH_BOY, SC2_X(3), SC2_Z(2), 3
    h_setobjectxyperm SC2_I_GENTLEMAN, SC2_X(1), SC2_Z(3), 3
L_SC2I_Defeated:
    h_goto_if_ne VAR_MOSSDEEP_SPACE_CENTER_STATE, 2, L_SC2I_Done
    h_setobjectxyperm SC2_I_GRUNT_6, SC2_X(11), SC2_Z(2), 3  // ..._EventScript_MoveDefeatedGrunts (their way after the three battles)
    h_setobjectxyperm SC2_I_GRUNT_7, SC2_X(15), SC2_Z(2), 2
    h_setobjectxyperm SC2_I_GRUNT_5, SC2_X(13), SC2_Z(4), 0
L_SC2I_Done:
    VMHalt

SC2_ThreeGrunts:                            // MossdeepCity_SpaceCenter_2F_EventScript_ThreeMagmaGrunts
    c9_lock
    h_applymovement 255, Common_Movement_ExclamationMark    // (playse SE_PIN: the "!" plays its own sound)
    h_waitmovement
    h_applymovement 255, Common_Movement_Delay48
    h_waitmovement
    h_yesno_actor T_Outnumbered, SC2_GRUNT_6, C9_A         // What's wrong with you? You're outnumbered three to one, but you still want to take us on?
    h_goto_if_yes C9_A, L_SC2_BattleGrunts
    h_msgbox_actor T_GoodAnswer, SC2_GRUNT_6               // Good answer! That's what a smart person'll do!
    h_closemessage
    h_applymovement 255, Mv_SC2_PlayerExit
    h_waitmovement
    h_warp_arrive 335, SC2_X(13), SC2_Z(2), 1              // warp MAP_MOSSDEEP_CITY_SPACE_CENTER_1F, 13, 1 (the tile below the stairs; players walk onto it)
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt
L_SC2_BattleGrunts:                         // ..._EventScript_BattleThreeMagmaGrunts
    h_msgbox_actor T_Grunt5Intro, SC2_GRUNT_5      // A reckless go-getter, are you? Okay, I'll go first!
    h_closemessage
    h_trainerbattle TRAINER_GRUNT_SPACE_CENTER_5   // trainerbattle_no_intro (defeat: "I lost! But!")
    h_applymovement SC2_GRUNT_5, Mv_SC2_Grunt5Defeated
    h_waitmovement
    h_applymovement 255, Common_Movement_WalkInPlaceFastestLeft
    h_waitmovement
    h_msgbox_actor T_Grunt6Intro, SC2_GRUNT_6      // It's too soon to be relieved! I'm up next!
    h_closemessage
    h_trainerbattle TRAINER_GRUNT_SPACE_CENTER_6
    h_applymovement SC2_GRUNT_6, Mv_SC2_Grunt6Defeated
    h_waitmovement
    h_applymovement 255, Common_Movement_WalkInPlaceFastestRight
    h_waitmovement
    h_msgbox_actor T_Grunt7Intro, SC2_GRUNT_7      // I bet you want to take a break. But I'm not about to let you do that!
    h_closemessage
    h_trainerbattle TRAINER_GRUNT_SPACE_CENTER_7
    h_applymovement SC2_GRUNT_7, Mv_SC2_Grunt7Defeated
    h_waitmovement
    h_setvar VAR_MOSSDEEP_SPACE_CENTER_STATE, 2    // (copyobjectxytoperm x3: the zone init stands them where they are now)
    h_release

    .balign 4, 0
Mv_SC2_PlayerExit:                          // MossdeepCity_SpaceCenter_2F_Movement_PlayerExit
    walk_up
    step_end
    .balign 4, 0
Mv_SC2_Grunt6Defeated:                      // ..._Movement_Grunt6Defeated
    lock_facing_direction
    walk_left
    unlock_facing_direction
    step_end
    .balign 4, 0
Mv_SC2_Grunt5Defeated:
    lock_facing_direction
    walk_down
    unlock_facing_direction
    step_end
    .balign 4, 0
Mv_SC2_Grunt7Defeated:
    lock_facing_direction
    walk_right
    unlock_facing_direction
    step_end
    .balign 4, 0
Mv_SC2_StevenFight:                         // ..._Movement_StevenFight
    lock_facing_direction
    walk_fast_up 2
    unlock_facing_direction
    delay_16 2
    walk_slow_down 2
    step_end
    .balign 4, 0
Mv_SC2_StevenFightSouth:                    // ..._Movement_StevenFightSouth
    face_left
    lock_facing_direction
    walk_fast_right 2
    unlock_facing_direction
    delay_16 2
    walk_slow_left 2
    face_down
    step_end
    .balign 4, 0
#include "common/movement.inc"
