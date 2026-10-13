// Pokémon Emerald NDS mechanics for story and world scripts (emerald_mech, 2026-10-12; notes/EMERALD.md "Phase 4").
// Emerald builds only (HOENN_VERSION=emerald): the globals below live in src/field_scripts/emerald/1236_global_2280.s
// and the two script commands in b2tools/patches/emerald_mech.c, neither of which a Sapphire or Ruby build has.
// Include after "asm/field_script.inc", "hoenn.h" and "hoenn_story.inc". Emits no code by itself.
//
// Works: the globals take their input in 0x8000-0x8002 and answer in 0x8010 (Black 2's convention for RTCallGlobal;
// those works are shared with the caller), and use 0x8020-0x8028 as scratch. HLIB_TMP / HLIB_RESULT are left alone.

#ifndef HOENN_EMERALD_INC
#define HOENN_EMERALD_INC

// ---- global scripts (file 1236 = globals 2280-2299; 2280-2288 are Black 2's own tutors, kept) --------------------
#define EM_GLOBAL_MOVE_TUTOR   2289     // in 0x8000 tutor (EM_TUTOR_*), 0x8001 move -> 0x8010 1 taught, 0 not
#define EM_GLOBAL_TAG_BATTLE   2290     // in 0x8000 partner, 0x8001/0x8002 foes -> 0x8010 0 cancelled, 1 won, 2 lost
#define EM_GLOBAL_CLOSED_DOOR  2291     // a door's (or sign's) script id: "still under construction", nothing opens
#define EM_GLOBAL_CLOSED_DOOR_MSG 2292  // the same message for RTCallGlobal from a zone script (em_closed_door)

// ---- the tag battle partner ---------------------------------------------------------------------------------------
// TRAINER_STEVEN_PARTNER, TRAINER_MAXIE_MOSSDEEP, TRAINER_TABITHA_MOSSDEEP: src/include/hoenn_trainers_emerald.h
// (emerald_data, converter/gen_trainers.py). Steven's partner team is pokeemerald's battle_tower.c sStevenMons; his
// class's back sprite is set to 5 (Steven's back from Emerald) by b2tools/patches/emerald_mech.py.

// ---- Emerald's move tutors: pokeemerald include/constants/party_menu.h TUTOR_MOVE_* -------------------------------
// The ten Hoenn town tutors (data/scripts/move_tutors.inc) are in the compatibility table; the Frontier's twenty are
// listed for later (EmTutorCheck answers "cannot learn" for them until emerald_mech.py's TOWN_TUTORS has them).
// (assembler symbols, so em_move_tutor can build EM_TUTOR_<name> / EM_TUTOR_MOVE_<name> from one name)
    .set EM_TUTOR_MEGA_PUNCH, 0
    .set EM_TUTOR_MOVE_MEGA_PUNCH, MOVE_MEGA_PUNCH
    .set EM_TUTOR_SWORDS_DANCE, 1
    .set EM_TUTOR_MOVE_SWORDS_DANCE, MOVE_SWORDS_DANCE
    .set EM_TUTOR_MEGA_KICK, 2
    .set EM_TUTOR_MOVE_MEGA_KICK, MOVE_MEGA_KICK
    .set EM_TUTOR_BODY_SLAM, 3
    .set EM_TUTOR_MOVE_BODY_SLAM, MOVE_BODY_SLAM
    .set EM_TUTOR_DOUBLE_EDGE, 4
    .set EM_TUTOR_MOVE_DOUBLE_EDGE, MOVE_DOUBLE_EDGE
    .set EM_TUTOR_COUNTER, 5
    .set EM_TUTOR_MOVE_COUNTER, MOVE_COUNTER
    .set EM_TUTOR_SEISMIC_TOSS, 6
    .set EM_TUTOR_MOVE_SEISMIC_TOSS, MOVE_SEISMIC_TOSS
    .set EM_TUTOR_MIMIC, 7
    .set EM_TUTOR_MOVE_MIMIC, MOVE_MIMIC
    .set EM_TUTOR_METRONOME, 8
    .set EM_TUTOR_MOVE_METRONOME, MOVE_METRONOME
    .set EM_TUTOR_SOFT_BOILED, 9
    .set EM_TUTOR_MOVE_SOFT_BOILED, MOVE_SOFTBOILED
    .set EM_TUTOR_DREAM_EATER, 10
    .set EM_TUTOR_MOVE_DREAM_EATER, MOVE_DREAM_EATER
    .set EM_TUTOR_THUNDER_WAVE, 11
    .set EM_TUTOR_MOVE_THUNDER_WAVE, MOVE_THUNDER_WAVE
    .set EM_TUTOR_EXPLOSION, 12
    .set EM_TUTOR_MOVE_EXPLOSION, MOVE_EXPLOSION
    .set EM_TUTOR_ROCK_SLIDE, 13
    .set EM_TUTOR_MOVE_ROCK_SLIDE, MOVE_ROCK_SLIDE
    .set EM_TUTOR_SUBSTITUTE, 14
    .set EM_TUTOR_MOVE_SUBSTITUTE, MOVE_SUBSTITUTE
    .set EM_TUTOR_DYNAMIC_PUNCH, 15
    .set EM_TUTOR_MOVE_DYNAMIC_PUNCH, MOVE_DYNAMIC_PUNCH
    .set EM_TUTOR_ROLLOUT, 16
    .set EM_TUTOR_MOVE_ROLLOUT, MOVE_ROLLOUT
    .set EM_TUTOR_PSYCH_UP, 17
    .set EM_TUTOR_MOVE_PSYCH_UP, MOVE_PSYCH_UP
    .set EM_TUTOR_SNORE, 18
    .set EM_TUTOR_MOVE_SNORE, MOVE_SNORE
    .set EM_TUTOR_ICY_WIND, 19
    .set EM_TUTOR_MOVE_ICY_WIND, MOVE_ICY_WIND
    .set EM_TUTOR_ENDURE, 20
    .set EM_TUTOR_MOVE_ENDURE, MOVE_ENDURE
    .set EM_TUTOR_MUD_SLAP, 21
    .set EM_TUTOR_MOVE_MUD_SLAP, MOVE_MUD_SLAP
    .set EM_TUTOR_ICE_PUNCH, 22
    .set EM_TUTOR_MOVE_ICE_PUNCH, MOVE_ICE_PUNCH
    .set EM_TUTOR_SWAGGER, 23
    .set EM_TUTOR_MOVE_SWAGGER, MOVE_SWAGGER
    .set EM_TUTOR_SLEEP_TALK, 24
    .set EM_TUTOR_MOVE_SLEEP_TALK, MOVE_SLEEP_TALK
    .set EM_TUTOR_SWIFT, 25
    .set EM_TUTOR_MOVE_SWIFT, MOVE_SWIFT
    .set EM_TUTOR_DEFENSE_CURL, 26
    .set EM_TUTOR_MOVE_DEFENSE_CURL, MOVE_DEFENSE_CURL
    .set EM_TUTOR_THUNDER_PUNCH, 27
    .set EM_TUTOR_MOVE_THUNDER_PUNCH, MOVE_THUNDER_PUNCH
    .set EM_TUTOR_FIRE_PUNCH, 28
    .set EM_TUTOR_MOVE_FIRE_PUNCH, MOVE_FIRE_PUNCH
    .set EM_TUTOR_FURY_CUTTER, 29
    .set EM_TUTOR_MOVE_FURY_CUTTER, MOVE_FURY_CUTTER

// ---- the two script commands (b2tools/patches/emerald_mech.c; only the globals above need them) -------------------
    .macro EmPartySwap a, b                // swap party slots a and b (numbers or works); slots past the end: nothing
    FieldCommand 533
    .2byte \a
    .2byte \b
    .endm
    .macro EmPickParty var                 // one battle-entry party menu, 1-3 picks: var = how many (0 = cancelled),
    FieldCommand 686                       // var+1 .. var+3 = the party slots picked, in order (255 = none)
    .2byte \var
    .endm
    .macro EmTutorCheck var, slot, tutor   // var = 0 can learn, 1 cannot (or an Egg), 2 already knows the move
    FieldCommand 281
    .2byte \var
    .2byte \slot
    .2byte \tutor
    .endm

// ---- macros for story scripts ------------------------------------------------------------------------------------
// The Space Center tag battle (pokeemerald MossdeepCity_SpaceCenter_2F_EventScript_ChoosePartyForMultiBattle +
// DoStevenMultiBattle; SPECIAL_BATTLE_STEVEN). One party menu, as Emerald's ChooseHalfPartyForBattle: Black 2's
// battle-entry screen (the Battle Subway's), 1 to 3 Pokémon numbered in the order picked, a pick tapped again is
// unmarked, then confirm; an Egg or a fainted Pokémon "can't participate" (the menu opens again). They lead in that
// order beside the partner against foe1 and foe2 (Black 2's CallTrainerMultiBattle; only those three are in the
// battle), then the party is put back in its old order. Won: falls through (both foes' trainer flags set). The menu
// left without a pick: jumps to `cancel` with the party unchanged (Emerald: back to "Are you ready?"). Lost: the
// whiteout (Emerald's SetCB2WhiteOut). Close the NPC's message window first (h_closemessage).
//     em_tag_battle TRAINER_STEVEN_PARTNER, TRAINER_MAXIE_MOSSDEEP, TRAINER_TABITHA_MOSSDEEP, L_NotReady
    .macro em_tag_battle partner, foe1, foe2, cancel
    WorkSetConst 0x8000, \partner
    WorkSetConst 0x8001, \foe1
    WorkSetConst 0x8002, \foe2
    RTCallGlobal EM_GLOBAL_TAG_BATTLE
    WorkCmpConst 0x8010, 0
    VMJumpIf CMP_EQ, \cancel
    WorkCmpConst 0x8010, 1
    VMJumpIf CMP_EQ, .Lemtag_won\@
    CallTrainerLose
    VMHalt
.Lemtag_won\@:
    .endm

// A whole move tutor NPC script, Emerald's flow (pokeemerald data/scripts/move_tutors.inc, e.g.
// SlateportCity_PokemonFanClub_EventScript_SwaggerTutor): taught already -> t_taught; t_teach (YES/NO), t_once
// (MoveTutor_Text_ThisMoveCanOnlyBeLearnedOnce, YES/NO), t_which, then the party menu (B = declined), Emerald's
// compatibility ("X and Y are not compatible." / "X already knows Y."), Black 2's learning sequence (forget a move
// if it knows four); taught -> flag set + t_taught, else t_declined. The t_* are lines of the zone's own text file
// (Emerald's MoveTutor_Text_*: copy them there). tutor = the name after EM_TUTOR_ / MOVE_ (SWAGGER, ROLLOUT, ...).
//     ScriptEntry Script_7      // the Swagger tutor
//     Script_7: em_move_tutor SWAGGER, FLAG_MOVE_TUTOR_TAUGHT_SWAGGER, 10, 11, 12, 13, 14
    .macro em_move_tutor tutor, flag, t_teach, t_once, t_which, t_declined, t_taught
    ActorsPauseAll
    SEPlay SEQ_SE_MESSAGE
    ActorSetEyeToEye
    h_goto_if_set \flag, .Lemtut_taught\@
    h_yesno \t_teach, HLIB_TMP
    h_goto_if_no HLIB_TMP, .Lemtut_declined\@
    h_yesno \t_once, HLIB_TMP
    h_goto_if_no HLIB_TMP, .Lemtut_declined\@
    h_msgbox \t_which
    ActorMsgClose
    WorkSetConst 0x8000, EM_TUTOR_\tutor
    WorkSetConst 0x8001, EM_TUTOR_MOVE_\tutor
    RTCallGlobal EM_GLOBAL_MOVE_TUTOR
    WorkCmpConst 0x8010, 1
    VMJumpIf CMP_NE, .Lemtut_declined\@
    FlagSet \flag
.Lemtut_taught\@:
    h_msgbox \t_taught
    h_release
.Lemtut_declined\@:
    h_msgbox \t_declined
    h_release
    .endm

// A closed door (decision 2026-10-11, EMERALD_PLAN.md section 4: the six closed Battle Frontier facilities, the three
// Battle Tents and Trainer Hill stand but are closed). Easiest: give the door tile no warp and put a sign there whose
// script is EM_GLOBAL_CLOSED_DOOR (2291; story json {"kind": "sign", "map": ..., "at": [x, y], "script": 2291,
// "dir": 0}): "This building is still under construction. Please come back when the work is completed." (Emerald's
// own words for its unfinished Battle Tower rooms, BattleFrontier_BattleTowerLobby_Text_DoubleBattleRoomConstruction),
// no zone script or text needed. From a zone script (e.g. a door that opens later, under a flag test): em_closed_door
// shows the same message (lock and release are the caller's: h_lock ... em_closed_door ... h_release).
    .macro em_closed_door
    RTCallGlobal EM_GLOBAL_CLOSED_DOOR_MSG
    .endm

#endif
