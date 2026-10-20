// EverGrandeCity_HallOfFame (zone 57; its own script file after Black 2's: data/hoenn_interiors.json own_scripts): the
// halloffame agent, 2026-10-07. Sapphire data/maps/EverGrandeCity_HallOfFame/scripts.inc and data/scripts/hall_of_fame.inc
// (the game-clear flags, moved here from ch11's 0068 with the ribbons sub, unchanged).
// Messages: src/text/script/0066_room_EverGrandeCity_HallOfFame.txt. Room: data/interior_layouts/EverGrandeCity_HallOfFame.json,
// zone json data/interiors/57.json (Steven = uid 1 at Sapphire (6,16)). Room tiles = Sapphire tiles + (1, 0).
// Flow (Sapphire -> Black 2):
// - The Champion's room (0068) walks Steven and the player out through its door and warps here (h_warp_scene 57, 8, 16, 0, 2):
//   script 2 = Sapphire's EnterHallOfFame (OnFrame): both walk up 6, Steven's line, up 5, the record line, both face the
//   machine. Sapphire's FLDEFF_HALL_OF_FAME_RECORD = Black 2's BMPlayHOFMachineSeq (ov033 EventDendouMachine: a Poké Ball
//   for every party Pokémon on the c09_dendo machine, its light; the machine must be the first building model within 5
//   tiles of the player).
// - SetGameClearFlags, setrespawn (the player's house), Sapphire's GameClear special (heal, Champion ribbons), then
//   Sapphire's Hall of Fame screen + credits = Black 2's CallGameClear (ov012 EventGameClear, b2tools/patches/game_clear.py):
//   the record screen (ov265), the save (global script 9601 first: src/field_scripts/1242_global_9600.s sets the place
//   Continue loads, the player's room), the credits (ov266, Hoenn pictures: b2tools/patches/game_clear.py), THE END; Continue
//   then starts in the player's room (Sapphire: the credits end, the game restarts in the bedroom). CallGameClear 0 the
//   first time (as Black 2; its Challenge Mode key screen is patched out), 1 later (the credits can be skipped with START, as Black 2's).
// - Black 2's sequence visits two "ending" zones with a script each (patched to this room, scripts 1 and 3: nothing, the
//   screen stays black: Sapphire has no field scene between the record and the credits, nor after them).
// EMERALD (emerald_ch11_gameclear, 2026-10-12; pokeemerald EverGrandeCity_HallOfFame + data/scripts/hall_of_fame.inc): the Champion
// who walks the player in is WALLACE (data/interiors/emerald/57.json: his picture; src/text/script/emerald/0066_room_EverGrande
// City_HallOfFame.txt: his two lines, same rows). The flags are Sapphire's above plus HF_EmeraldFlags below (Emerald's own
// SetGameClearFlags lines: FLAG_IS_CHAMPION, the event legends fightable again, the Desert Underpass comment, Wally, the
// Safari Zone expansion, Steven's house ninja boy, the Lilycove rival gone, the Littleroot bedrooms, the dex upgrade armed).
// scenes/ch13_gameclear.inc has an Emerald branch too (the Lati news is Mom's scene in the house, not the TV).
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_story.inc"

    ScriptEntry Script_None         // 1: Steven (no script); the ending zone's script before the credits (game_clear.py)
    ScriptEntry HF_Enter            // 2: reserved by the Champion's room: EverGrandeCity_HallOfFame_EventScript_EnterHallOfFame
    ScriptEntry HF_AfterCredits     // 3: the ending zone's script after the credits (game_clear.py)
    ScriptEntriesEnd

#define T_HereWeHonor 0
#define T_LetsRecord 1
#define HF_STEVEN 1
#define HF_AGAIN 0x8060                          /* 1: the game was cleared before (Black 2's CallGameClear 1) */
#define HF_PARTY_SLOT 0x8065
#define HF_TMP 0x8066
#define HF_RIBBON_GET 0x8067

Script_None:
    VMHalt

HF_AfterCredits:                                 // (Black 2: the epilogue in Aspertia; Sapphire has none: THE END follows)
    VMHalt

HF_Enter:                                        // EverGrandeCity_HallOfFame_EventScript_EnterHallOfFame
    ActorsPauseAll                               // lockall
    FadeInBlack                                  // (the warp's fade in: the Champion's room reserved this script)
    FadeWait
    h_applymovement HF_STEVEN, Mv_HF_WalkIntoHallOfFame1
    h_applymovement 255, Mv_HF_WalkIntoHallOfFame1
    h_waitmovement
    h_applymovement HF_STEVEN, Common_Movement_WalkInPlaceFastestRight
    h_applymovement 255, Common_Movement_WalkInPlaceFastestLeft
    h_waitmovement
    h_msgbox_actor T_HereWeHonor, HF_STEVEN      // Steven: This room... This is where we keep records of Pokémon that prevailed...
    h_closemessage
    h_applymovement HF_STEVEN, Mv_HF_WalkIntoHallOfFame2
    h_applymovement 255, Mv_HF_WalkIntoHallOfFame2
    h_waitmovement
    h_delay 20
    h_applymovement HF_STEVEN, Common_Movement_WalkInPlaceFastestRight
    h_applymovement 255, Common_Movement_WalkInPlaceFastestLeft
    h_waitmovement
    h_msgbox_actor T_LetsRecord, HF_STEVEN       // Steven: Come on, let's record your name as a Trainer who triumphed...
    h_closemessage
    h_applymovement HF_STEVEN, Common_Movement_WalkInPlaceFastestUp
    h_applymovement 255, Common_Movement_WalkInPlaceFastestUp
    h_waitmovement
    h_delay 20
    BMPlayHOFMachineSeq                          // dofieldeffect / waitfieldeffect FLDEFF_HALL_OF_FAME_RECORD
    h_delay 40
    h_setvar 0x4001, 1                           // setvar VAR_TEMP_1, 1
    WorkSetConst HF_AGAIN, 0                     // (read before SetGameClearFlags sets it: Black 2's own check, 0290.s)
    h_goto_if_unset FLAG_SYS_GAME_CLEAR, L_HF_First
    WorkSetConst HF_AGAIN, 1
L_HF_First:
    VMCall HF_SetGameClearFlags                  // call EverGrandeCity_HallOfFame_EventScript_SetGameClearFlags
    h_setrespawn 1                               // setrespawn HEAL_LOCATION_LITTLEROOT_TOWN_BRENDANS_HOUSE_2F / MAYS_HOUSE_2F
    VMCall HF_GameClear                          // special GameClear: the heal, the Champion ribbons
    FadeEx 3, 0, 16, 4                           // fadescreenspeed 1, 24 (a slow fade to black)
    FadeExWait
    h_goto_if_eq HF_AGAIN, 1, L_HF_Again
    CallGameClear 0                              // waitstate: the record screen, the save, the credits (ends the script)
    VMHalt
L_HF_Again:
    CallGameClear 1
    VMHalt

HF_SetGameClearFlags:                            // EverGrandeCity_HallOfFame_EventScript_SetGameClearFlags
    h_clearflag FLAG_HIDE_LILYCOVE_MOTEL_PEOPLE
    VMCall HF_ResetEliteFour                     // call EverGrandeCity_HallOfFame_EventScript_ResetEliteFour
    h_setflag FLAG_HIDE_BRINEY_SLATEPORT_SHIPYARD
    h_clearflag FLAG_HIDE_BRINEY_AND_PEEKO_SS_TIDAL
    h_clearflag FLAG_HIDE_STEVENS_LETTER         // (chapter Ch9's hook: Steven's house)
    h_setvar VAR_STEVENS_HOUSE_STATE, 1
    h_clearflag FLAG_HIDE_WALLY_DEFEATED_VICTORY_ROAD
    h_clearflag FLAG_HIDE_SS_TIDAL_SLATEPORT_HARBOR
    h_clearflag FLAG_HIDE_SS_TIDAL_LILYCOVE_HARBOR
    h_clearflag FLAG_DEFEATED_MEW                // Emerald's ResetDefeatedEventLegendaries in every version (user decision
    h_clearflag FLAG_DEFEATED_DEOXYS             //   2026-10-19): an event legendary that was knocked out, not caught, is
    h_clearflag FLAG_DEFEATED_LUGIA              //   back after every Hall of Fame (its island's zone init shows it again
    h_clearflag FLAG_DEFEATED_HO_OH              //   when the flag is clear); Celebi (Petalburg Woods, not in Emerald)
    h_clearflag FLAG_DEFEATED_CELEBI             //   follows the same rule
#ifdef HOENN_EMERALD
    VMCall HF_EmeraldFlags                       // Emerald's own lines of SetGameClearFlags (below)
#endif
#if __has_include("common/fan_club.inc")
    VMCall Sub_FanClub_GameClear                 // special UpdateTrainerFanClubGameClear (chapter Ch8's hook: the Lilycove Fan Club)
#endif
#if __has_include("scenes/ch13_gameclear.inc")
    VMCall Sub_Ch13_GameClear                    // ReadyReceiveSSTicketEvent, ReadyLatiTVEvent, ShowStevensBeldum, ShowHM08 (chapter Ch13's)
#endif
    h_setflag FLAG_SYS_GAME_CLEAR                // (Sapphire: set by the GameClear special; Black 2's 9601 sets it too)
    VMReturn

#ifdef HOENN_EMERALD
HF_EmeraldFlags:                                 // the lines of Emerald's EverGrandeCity_HallOfFame_EventScript_SetGameClearFlags that Sapphire's lack
    h_setflag FLAG_IS_CHAMPION                   // setflag FLAG_IS_CHAMPION
    h_clearflag FLAG_DEFEATED_LATIAS_OR_LATIOS   // call ResetDefeatedEventLegendaries (Mew, Deoxys, Lugia, Ho-Oh: above, every
                                                 //   version): the Southern Island Lati is back (scenes/emerald/SouthernIsland_Interior.inc)
    h_goto_if_ne VAR_FOSSIL_MANIAC_STATE, 0, L_HF_E_Fossil
    h_setvar VAR_FOSSIL_MANIAC_STATE, 1          // call_if_eq VAR_FOSSIL_MANIAC_STATE, 0, SetDesertUnderpassCommentReady (the Fossil Maniac's tunnel hint)
L_HF_E_Fossil:
    h_setflag FLAG_HIDE_WALLY_BATTLE_VICTORY_ROAD   // setflag FLAG_HIDE_VICTORY_ROAD_ENTRANCE_WALLY (the exit one is cleared in HF_SetGameClearFlags)
    h_clearflag FLAG_HIDE_MOSSDEEP_CITY_STEVENS_HOUSE_INVISIBLE_NINJA_BOY    // Steven's house (a Mossdeep builder places him)
    h_setvar VAR_STEVENS_HOUSE_STATE, 2          // pokeemerald: 2 (given). The shared line above says Sapphire's 1; Emerald's 1 = the Dive is due (emerald_ch9_mirage)
    h_setflag FLAG_HIDE_SAFARI_ZONE_SOUTH_CONSTRUCTION_WORKERS               // the Safari Zone's new areas open (Safari builder)
    h_clearflag FLAG_HIDE_SAFARI_ZONE_SOUTH_EAST_EXPANSION
    h_setflag FLAG_HIDE_LILYCOVE_CITY_RIVAL
    h_setflag FLAG_HIDE_LITTLEROOT_TOWN_BRENDANS_HOUSE_RIVAL_BEDROOM         // the rival is not in the bedroom any more
    h_setflag FLAG_HIDE_LITTLEROOT_TOWN_MAYS_HOUSE_RIVAL_BEDROOM
    h_goto_if_ne VAR_DEX_UPGRADE_JOHTO_STARTER_STATE, 0, L_HF_E_Dex
    h_setvar VAR_DEX_UPGRADE_JOHTO_STARTER_STATE, 1                          // ReadyDexUpgradeEvent (Littleroot's zone init plays the scene)
L_HF_E_Dex:
    VMReturn
#endif

HF_ResetEliteFour:                               // EverGrandeCity_HallOfFame_EventScript_ResetEliteFour
    h_clearflag FLAG_DEFEATED_ELITE_4_SYDNEY
    h_clearflag FLAG_DEFEATED_ELITE_4_PHOEBE
    h_clearflag FLAG_DEFEATED_ELITE_4_GLACIA
    h_clearflag FLAG_DEFEATED_ELITE_4_DRAKE
    h_setvar VAR_ELITE_4_STATE, 0
    VMReturn

HF_GameClear:                                    // special GameClear (pokeruby src/post_battle_event_funcs.c)
    PokePartyRecoverAll                          // ScrSpecial_HealPlayerParty
    WorkSetConst HF_RIBBON_GET, 0
    WorkSetConst HF_PARTY_SLOT, 0
    PokePartyGetCount HF_TMP, 0                  // the party's size
L_HF_RibbonLoop:
    WorkCmpWork HF_PARTY_SLOT, HF_TMP
    VMJumpIf CMP_GE, L_HF_RibbonsDone
    PokePartyIsEgg 0x8068, HF_PARTY_SLOT
    h_goto_if_ne 0x8068, 0, L_HF_NextSlot        // (not an Egg)
    h_check_ribbon 0x8068, HF_PARTY_SLOT, RIBBON_CHAMPION
    h_goto_if_ne 0x8068, 0, L_HF_NextSlot        // (does not have it yet)
    h_give_ribbon HF_PARTY_SLOT, RIBBON_CHAMPION
    WorkSetConst HF_RIBBON_GET, 1
L_HF_NextSlot:
    WorkAdd HF_PARTY_SLOT, 1
    VMJump L_HF_RibbonLoop
L_HF_RibbonsDone:
    h_goto_if_eq HF_RIBBON_GET, 0, L_HF_NoRibbon
    h_setflag FLAG_SYS_RIBBON_GET
L_HF_NoRibbon:
    VMReturn

    .balign 4, 0
Mv_HF_WalkIntoHallOfFame1:                       // EverGrandeCity_HallOfFame_Movement_WalkIntoHallOfFame1
    walk_up 6
    step_end
Mv_HF_WalkIntoHallOfFame2:                       // EverGrandeCity_HallOfFame_Movement_WalkIntoHallOfFame2
    walk_up 5
    step_end

#include "common/movement.inc"
#if __has_include("common/fan_club.inc")
#include "common/fan_club.inc"
#endif
#if __has_include("scenes/ch13_gameclear.inc")
#include "scenes/ch13_gameclear.inc"
#endif
