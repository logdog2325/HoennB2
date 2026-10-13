// MossdeepCity_SpaceCenter_1F (zone 335), EMERALD ONLY (emerald_ch9_mirage 2026-10-12, builder B5; pokeemerald data/maps/MossdeepCity_SpaceCenter_1F/
// scripts.inc): replaces src/field_scripts/0670_room_MossdeepCity_SpaceCenter_1F.s in an Emerald build (the same scripts 1-5 for the same people,
// Emerald's lines and Magma branches, then new ones). Sapphire's file keeps its own scripts.
// Text: src/text/script/emerald/0547_room_MossdeepCity_SpaceCenter_1F.txt (converter/gen_emerald_ch9_text.py): lines 0-7 are the people's
// (Sapphire's indices), 8-11 the post-game Jirachi gift, 12-22 Magma's. People: the generated three (data/interiors/335.json: scientist (2,2) = uid 2,
// woman (14,7) = uid 5, old man (10,2) = uid 4), Sapphire's two story objects (data/story/ch9.json: the launch counter's scientist uid 1, the Sun Stone
// man uid 3) and Emerald's (data/story/emerald/e_ch9_mirage.json, uid = pokeemerald's local id): the three grunts that see you (uids 6, 7, 8: Black 2's
// own trainer scripts 3000 + id), the stair guard 9, Steven 11, and the Magma note (a sign at (2,5), pokeemerald's invisible object 10). They stand in
// the zone's NPC list as: scientist 0, woman 1, old man 2, counter 3, Sun Stone man 4, grunts 5-7, stair guard 8, Steven 9 (the zone init's indices).
// Room tiles = pokeemerald tiles + (1, 1).
// The Magma state (VAR_MOSSDEEP_CITY_STATE: 1 = Tate & Liza beaten, 2 = Magma took the Space Center, 3 = beaten): at 2 the zone init moves five people
// to the walls and the grunts show (the Gym's win cleared FLAG_HIDE_MOSSDEEP_CITY_SPACE_CENTER_1F_TEAM_MAGMA). The stair guard (uid 9) blocks the
// stairs (13,1) until you beat him: he steps one tile aside (VAR_MOSSDEEP_SPACE_CENTER_STAIR_GUARD_STATE 1 = left, 2 = right/down).
// Black 2 gaps: pokeemerald's OnLoad puts the Magma notice's data pad on the table (setmetatile): the notice is only readable here.
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_trainers.h"
#include "hoenn_key_items.h"
#include "hoenn_story.inc"
#include "hoenn_version.inc"               // TRAINER_GRUNT_SPACE_CENTER_2

    ScriptEntry PG_SC_Scientist            // 1: scientist (2,2) (before the Hall of Fame: Script_1; after it: Jirachi, scenes/MossdeepCity_SpaceCenter_1F_Postgame.inc)
    ScriptEntry SC_Woman                   // 2: woman (14,7), uid 5
    ScriptEntry SC_OldMan                  // 3: old man (10,2), uid 4
    ScriptEntry SC_LaunchCounter           // 4: object 1 (the scientist at the launch counter)
    ScriptEntry SC_SunStoneMan             // 5: object 3 (the Sun Stone man)
    ScriptEntry SC_Steven                  // 6: Steven (1,4), uid 11
    ScriptEntry SC_MagmaNote               // 7: the notice on the table (sign (2,5))
    ScriptEntry SC_StairGrunt              // 8: the grunt in front of the stairs, uid 9
    ScriptEntry SC_Init                    // 9: zone init (MossdeepCity_SpaceCenter_1F_OnTransition)
    ScriptEntriesEnd

#define C9_DAYS
#include "scenes/ch9_lib.inc"
#define T_Perfection 0                     // MossdeepCity_SpaceCenter_1F_Text_RocketLaunchDemandsPerfection
#define T_DidPokemonComeFromSpace 1
#define T_RocketsBoggleMyMind 2
#define T_RocketLaunchImminent 3
#define T_SuccessfulLaunch 4
#define T_FoundThis 5
#define T_MeteorShowers 6
#define T_BagFull 7
#define T_HaywireImminent 12               // ...HaywireButRocketLaunchImminent
#define T_HaywireSuccessful 13
#define T_MagmaSights 14                   // ...MagmaHaveSightsOnSpaceCenter
#define T_MagmaCantSteal 15                // ...MagmaCantStealFuelTakeThis
#define T_CantStroll 16
#define T_AquaShouldBeat 17
#define T_MagmaSpoilMyDream 18
#define T_StevenCantTakeFuel 19
#define T_MagmaNotice 20
#define T_Grunt2Intro 21
#define T_Grunt2Post 22
#define SC_COUNTER 1                       // uids
#define SC_SCIENTIST2 2
#define SC_SUN_MAN 3
#define SC_OLD_MAN 4
#define SC_WOMAN 5
#define SC_STAIR_GRUNT 9
#define SC_STEVEN 11
#define SC_FACE_RIGHT 3
#define SC_X(x) ((x) + 1)                  // pokeemerald tile -> zone tile (the room's origin)
#define SC_Z(z) ((z) + 1)
#define SC_I_SCIENTIST2 0                  // positions in the zone's NPC list (ObjInitNPCGPos)
#define SC_I_WOMAN 1
#define SC_I_OLD_MAN 2
#define SC_I_COUNTER 3
#define SC_I_SUN_MAN 4
#define SC_I_STAIR_GRUNT 8

Script_1:                               // MossdeepCity_SpaceCenter_1F_EventScript_Scientist (lock, faceplayer)
    c9_talk
    h_goto_if_eq VAR_MOSSDEEP_CITY_STATE, 2, L_SC_ScientistMagma
    h_msgbox T_Perfection               // A rocket launch demands perfection. ... Despite that, we never stop trying. ...
    h_release
L_SC_ScientistMagma:
    h_msgbox T_MagmaSights              // Those Magma thugs have their sights set on our Space Center. ...
    h_closemessage
    h_turnobject SC_SCIENTIST2, SC_FACE_RIGHT   // applywaitmovement VAR_LAST_TALKED, Common_Movement_WalkInPlaceFasterRight
    h_release

SC_Woman:                               // MossdeepCity_SpaceCenter_1F_EventScript_Woman (lock, faceplayer)
    c9_talk
    h_goto_if_set FLAG_SYS_GAME_CLEAR, L_SC_WomanNormal
    h_goto_if_eq VAR_MOSSDEEP_CITY_STATE, 2, L_SC_WomanMagma
    h_goto_if_lt VAR_MOSSDEEP_CITY_STATE, 2, L_SC_WomanNormal
L_SC_WomanMagma:                        // (state 3 too, until the game is cleared: pokeemerald's own order of tests)
    h_msgbox T_AquaShouldBeat           // Team Aqua should take care of Team Magma! But if they did that, Team Aqua will become bold and brazen, ...
    h_release
L_SC_WomanNormal:
    h_msgbox T_DidPokemonComeFromSpace  // Some people claim that Pokémon came from space. Could it be true?
    h_release

SC_OldMan:                              // MossdeepCity_SpaceCenter_1F_EventScript_OldMan (lock, faceplayer)
    c9_talk
    h_goto_if_set FLAG_SYS_GAME_CLEAR, L_SC_OldManNormal
    h_goto_if_eq VAR_MOSSDEEP_CITY_STATE, 2, L_SC_OldManMagma
    h_goto_if_lt VAR_MOSSDEEP_CITY_STATE, 2, L_SC_OldManNormal
L_SC_OldManMagma:
    h_msgbox T_MagmaSpoilMyDream        // A giant chunk of metal bursts through the skies and flies into space... But Team Magma wants to spoil that dream of mine! ...
    VMJump L_SC_OldManTurn
L_SC_OldManNormal:
    h_msgbox T_RocketsBoggleMyMind      // A giant chunk of metal bursts through the skies and flies into space... It boggles my mind!
L_SC_OldManTurn:
    h_closemessage
    h_goto_if_eq VAR_MOSSDEEP_CITY_STATE, 2, L_SC_OldManFaceRight   // Common_Movement_FaceOriginalDirection: where the zone init stood him
    h_turnobject SC_OLD_MAN, 0
    h_release
L_SC_OldManFaceRight:
    h_turnobject SC_OLD_MAN, SC_FACE_RIGHT
    h_release

// The rocket launch counter: pokeemerald counts weeks since the clock was set (GetWeekCount); Black 2's scripts read only the date, so the weeks
// run from the first visit to Mossdeep (VAR_MOSSDEEP_SPACE_CENTER_START_DAY, set by Mossdeep's zone init; notes/STORY_HANDOFFS.md), as Sapphire's
SC_LaunchCounter:                       // MossdeepCity_SpaceCenter_1F_EventScript_RocketLaunchCounter (lock, faceplayer)
    c9_talk
    VMCall C9_TodayOfYear               // dotimebasedevents + specialvar GetWeekCount
    WorkSet C9_ELAPSED, C9_TODAY
    WorkCmpWork C9_TODAY, VAR_MOSSDEEP_SPACE_CENTER_START_DAY
    VMJumpIf CMP_LT, L_SC_YearTurned
    WorkSub C9_ELAPSED, VAR_MOSSDEEP_SPACE_CENTER_START_DAY
    VMJump L_SC_Weeks
L_SC_YearTurned:                        // the year turned over since the first visit
    WorkAdd C9_ELAPSED, 365
    WorkSub C9_ELAPSED, VAR_MOSSDEEP_SPACE_CENTER_START_DAY
L_SC_Weeks:
    WorkDiv C9_ELAPSED, 7               // the week count (pokeemerald caps it at 9999)
    WordSetNumber 1, C9_ELAPSED, 4      // buffernumberstring STR_VAR_1
    h_goto_if_eq VAR_MOSSDEEP_CITY_STATE, 2, L_SC_CounterMagma
    h_goto_if_ge C9_ELAPSED, 1, L_SC_ShowLaunchNumber
    h_msgbox T_RocketLaunchImminent     // The rocket's launch is imminent!
    VMJump L_SC_CounterDone
L_SC_ShowLaunchNumber:
    h_msgbox T_SuccessfulLaunch         // The rocket launched safely! That's successful launch no. {STR_VAR_1}!
L_SC_CounterDone:
    h_closemessage
    h_turnobject SC_COUNTER, 0          // Common_Movement_FaceOriginalDirection (FACE_UP)
    h_release
L_SC_CounterMagma:                      // ..._RocketLaunchCounterMagma
    h_goto_if_ge C9_ELAPSED, 1, L_SC_ShowLaunchNumberMagma
    h_msgbox T_HaywireImminent          // I know that things are a little haywire right now, but... The rocket's launch is imminent!
    VMJump L_SC_CounterMagmaDone
L_SC_ShowLaunchNumberMagma:
    h_msgbox T_HaywireSuccessful        // I know that things are a little haywire right now, but... The rocket launched safely! ...
L_SC_CounterMagmaDone:
    h_closemessage
    h_turnobject SC_COUNTER, SC_FACE_RIGHT      // Common_Movement_WalkInPlaceFasterRight
    h_release

SC_SunStoneMan:                         // MossdeepCity_SpaceCenter_1F_EventScript_SunStoneMan (lock, faceplayer)
    c9_talk
    h_goto_if_eq VAR_MOSSDEEP_CITY_STATE, 2, L_SC_SunStoneMagma
    h_goto_if_set FLAG_RECEIVED_SUN_STONE_MOSSDEEP, L_SC_GaveSunStone
    h_msgbox T_FoundThis                // I was taking a stroll down the beach when I found this. ...
    h_closemessage                      // (Black 2: the item script opens its own window)
    h_giveitem ITEM_SUN_STONE
    h_goto_if_eq HLIB_RESULT, 0, L_SC_BagFull
    h_setflag FLAG_RECEIVED_SUN_STONE_MOSSDEEP
    h_msgbox T_MeteorShowers            // The Hoenn region has been famous for its meteor showers for a long time.
    h_release
L_SC_GaveSunStone:
    h_msgbox T_MeteorShowers
    h_release
L_SC_SunStoneMagma:                     // ..._EventScript_SunStoneManMagma
    h_goto_if_set FLAG_RECEIVED_SUN_STONE_MOSSDEEP, L_SC_GaveSunStoneMagma
    h_msgbox T_MagmaCantSteal           // Team Magma can't be allowed to steal the rocket fuel. Oh, by the way, you can have this stone I found on the beach.
    h_closemessage
    h_giveitem ITEM_SUN_STONE
    h_goto_if_eq HLIB_RESULT, 0, L_SC_BagFull
    h_setflag FLAG_RECEIVED_SUN_STONE_MOSSDEEP
    h_msgbox T_CantStroll               // With Team Magma around, I guess strolls on the beach aren't safe.
    h_closemessage
    h_turnobject SC_SUN_MAN, SC_FACE_RIGHT
    h_release
L_SC_GaveSunStoneMagma:
    h_msgbox T_CantStroll
    h_closemessage
    h_turnobject SC_SUN_MAN, SC_FACE_RIGHT
    h_release
L_SC_BagFull:                           // Common_EventScript_ShowBagIsFull
    h_bag_is_full T_BagFull
    h_release

SC_Steven:                              // MossdeepCity_SpaceCenter_1F_EventScript_Steven (lock, faceplayer; he is hidden once the Gym is won)
    c9_talk
    h_msgbox T_StevenCantTakeFuel       // Steven: <player>, have you read that proclamation already? Team Magma is coming after the rocket fuel ...
    h_closemessage
    h_turnobject SC_STEVEN, 1           // Common_Movement_FaceOriginalDirection (FACE_DOWN)
    h_release

SC_MagmaNote:                           // MossdeepCity_SpaceCenter_1F_EventScript_MagmaNote (lockall)
    c9_lock
    h_goto_if_set FLAG_HIDE_MOSSDEEP_CITY_SPACE_CENTER_MAGMA_NOTE, L_SC_NoNote  // pokeemerald's object is hidden by this flag
    h_msgbox_info T_MagmaNotice         // This is... An intent-to-steal notice? "To the staff of the Space Center: ... Let there be more land! Team Magma"
    h_closemessage
L_SC_NoNote:
    h_release

SC_StairGrunt:                          // MossdeepCity_SpaceCenter_1F_EventScript_Grunt2 (lock, faceplayer)
    c9_talk
    h_goto_if_set FLAG_DEFEATED_GRUNT_SPACE_CENTER_1F, L_SC_Grunt2Defeated
    h_msgbox T_Grunt2Intro              // Our leader said no one, but no one, gets past me!
    h_closemessage
    h_getplayerfacing C9_B              // pokeemerald's switch VAR_FACING: only DIR_WEST sends him left (its east case is a typo that never runs)
    h_trainerbattle TRAINER_GRUNT_SPACE_CENTER_2    // trainerbattle_no_intro (the defeat line is the trainer's: "Ack! Ack! Aaack!")
    h_setflag FLAG_DEFEATED_GRUNT_SPACE_CENTER_1F
    h_goto_if_eq C9_B, 2, L_SC_GruntLeft
    h_applymovement SC_STAIR_GRUNT, Mv_SC_MoveGruntFromStairs
    h_waitmovement
    h_setvar VAR_MOSSDEEP_SPACE_CENTER_STAIR_GUARD_STATE, 2
    h_release
L_SC_GruntLeft:                         // ..._EventScript_MoveGruntFromStairsWest
    h_applymovement SC_STAIR_GRUNT, Mv_SC_MoveGruntFromStairsWest
    h_waitmovement
    h_setvar VAR_MOSSDEEP_SPACE_CENTER_STAIR_GUARD_STATE, 1
    h_release
L_SC_Grunt2Defeated:
    h_msgbox T_Grunt2Post               // Please, tell our leader that I never abandoned my post. That I stayed to the bitter end...
    h_release

SC_Init:                                // MossdeepCity_SpaceCenter_1F_OnTransition: MoveObjectsForTeamMagma (setobjectxyperm + movement type FACE_RIGHT)
    h_goto_if_ne VAR_MOSSDEEP_CITY_STATE, 2, L_SCI_Done
    h_setobjectxyperm SC_I_SUN_MAN, SC_X(1), SC_Z(9), SC_FACE_RIGHT          // the Sailor
    h_setobjectxyperm SC_I_WOMAN, SC_X(0), SC_Z(8), SC_FACE_RIGHT
    h_setobjectxyperm SC_I_OLD_MAN, SC_X(1), SC_Z(6), SC_FACE_RIGHT
    h_setobjectxyperm SC_I_COUNTER, SC_X(3), SC_Z(4), SC_FACE_RIGHT         // scientist 1
    h_setobjectxyperm SC_I_SCIENTIST2, SC_X(2), SC_Z(2), SC_FACE_RIGHT      // scientist 2: faces right where he stands
    h_goto_if_eq VAR_MOSSDEEP_SPACE_CENTER_STAIR_GUARD_STATE, 1, L_SCI_GuardLeft
    h_goto_if_eq VAR_MOSSDEEP_SPACE_CENTER_STAIR_GUARD_STATE, 2, L_SCI_GuardDown
L_SCI_Done:
    VMHalt
L_SCI_GuardLeft:                        // ..._EventScript_MoveStairGuardLeft
    h_setobjectxyperm SC_I_STAIR_GRUNT, SC_X(12), SC_Z(2), 1
    VMHalt
L_SCI_GuardDown:                        // ..._EventScript_MoveStairGuardDown (the state 3 case is functionally unused in pokeemerald)
    h_setobjectxyperm SC_I_STAIR_GRUNT, SC_X(13), SC_Z(3), 1
    VMHalt

    .balign 4, 0
Mv_SC_MoveGruntFromStairsWest:          // MossdeepCity_SpaceCenter_1F_Movement_MoveGruntFromStairsWest
    lock_facing_direction
    walk_left
    unlock_facing_direction
    step_end
    .balign 4, 0
Mv_SC_MoveGruntFromStairs:              // MossdeepCity_SpaceCenter_1F_Movement_MoveGruntFromStairs (north and east, and the player's other sides)
    face_left
    lock_facing_direction
    walk_right
    unlock_facing_direction
    step_end
    .balign 4, 0

// post-game (postgame_scripts, 2026-10-07): script 1 = the scientist's Jirachi gift after the Hall of Fame, text lines 8-11
#include "scenes/MossdeepCity_SpaceCenter_1F_Postgame.inc"
