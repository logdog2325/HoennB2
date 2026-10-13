// Chapter 10 helpers (ch10 agent, 2026-10-07): Seafloor Cavern, Route 128, Sootopolis City, the Cave of Origin, the
// Sootopolis Gym. Macros and script works only (no code until used). Include after "hoenn_story.inc" in the BODY part
// of a scene file (or after the ScriptEntry table of a room file).
#ifndef CH10_LIB_INC
#define CH10_LIB_INC
#include "hoenn_key_items.h"

// script works of these helpers (HLIB_* 0x8030/31, ch3 0x8032-36, ch4 0x8037-39, ch7 0x803A-3D, ch8a 0x8037-3F, ch9
// 0x8040-47): 0x8050-0x8057
#define C10_A 0x8050
#define C10_B 0x8051
#define C10_C 0x8052
#define C10_D 0x8053
#define C10_SEL 0x8054
#define C10_POS 0x8055

// Black 2's temporary works / flags (wiped on a map change: Sapphire's VAR_TEMP_n / FLAG_TEMP_n)
#define C10_TEMP_1 0x4001
#define C10_TEMP_2 0x4002
#define C10_TEMP_3 0x4003
#define C10_TEMP_4 0x4004
#define C10_TEMP_5 0x4005

// lock + faceplayer of a talked-to person (Black 2's NPC script start; {0100:0} = the player's name in the lines)
    .macro c10_talk
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    ActorSetEyeToEye
    .endm

// lock without facing (objects, signs, scenes): the message sound as every Black 2 NPC script
    .macro c10_lock
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    .endm

// a Pokémon that cries and says its line (lock, faceplayer, waitse, playmoncry, msgbox, waitmoncry, release)
    .macro c10_mon_cry species, n
    c10_talk
    h_playmoncry \species
    h_msgbox \n
    h_waitmoncry
    h_release
    .endm

// giveitem VAR (the item is in a work: Kiri's Berry): HLIB_RESULT 1 given, 0 no room (h_giveitem takes a constant only)
    .macro c10_giveitem_var var
    ItemCheckSpace \var, 1, HLIB_RESULT
    WorkCmpConst HLIB_RESULT, 0
    VMJumpIf CMP_EQ, .Lc10giv\@
    VMStackPush 0x8000
    VMStackPush 0x8001
    WorkSet 0x8000, \var
    WorkSetConst 0x8001, 1
    RTCallGlobal 2805
    VMStackPop 0x8001
    VMStackPop 0x8000
.Lc10giv\@:
    .endm

// Sapphire's "NPC walks away in a Skarmory flight" (FLDEFF_NPCFLY_OUT): Black 2 has no such field effect, the person
// just fades out of sight behind a short delay (a person that leaves the screen by walking is not this: use movement)
    .macro c10_fly_out uid, flag
    h_delay 15
    h_removeobject \uid, \flag
    .endm

// sounds (Sapphire's SE_* have no Black 2 twin: guesses, picked by name/situation; the user chooses by ear)
#define C10_SE_SHAKE SEQ_SE_FLD_126             // the cave shakes (SE_M_STRENGTH): the truck / ground-rumble effect other scenes use
#define C10_SE_DETECT SEQ_SE_FLD_28             // SE_M_DETECT: the Orb stirs [guess]
#define C10_SE_ORB SEQ_SE_FLD_29                // SE_ORB: the Orb's glow [guess]
#define C10_SE_ICE_CRACK SEQ_SE_FLD_30          // SE_ICE_CRACK [guess]
#define C10_SE_ICE_BREAK SEQ_SE_FLD_31          // SE_ICE_BREAK [guess]
#define C10_SE_ICE_STAIRS SEQ_SE_FLD_32         // SE_ICE_STAIRS [guess]
#define C10_SE_FALL SEQ_SE_FLD_33               // SE_FALL (a hole / cracked ice) [guess]

// special ShakeCamera (the camera quakes, amplitude n) with its sound; Black 2: EvCameraShake as the Sealed Chamber's
    .macro c10_shake amp
    SEPlay C10_SE_SHAKE
    EvCameraShake \amp, 0, 3, 8, 1, 0, 1, 5
    VMSleep 24
    .endm

// a scripted trainer battle; test builds with HOENN_TEST_CH10_SKIP=1 skip the fight (the trainer counts as beaten) to test what follows
    .macro c10_trainerbattle id
#ifdef HOENN_TEST_CH10_SKIP
    h_settrainerflag \id
#else
    h_trainerbattle \id
#endif
    .endm
#endif
