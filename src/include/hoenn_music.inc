// Hoenn music in field scripts (music_more 2026-10-11; notes/MUSIC.md section 7, b2tools/patches/hoenn_music.c).
//
// Birch's third question picks the soundtrack (options bit 13). Scripts play Black 2 sequence ids; with the Hoenn
// answer GFL_SndBGMPlayCore / func_02006424 send them through Music_Redirect's table. Sapphire's own script songs sit in
// slots (data/hoenn_music.json "slots", kept fixed by b2tools/music_slots.py SCRIPT_SLOTS; the build checks every
// `#define MUS_HOENN_X SEQ_... // mus_x` line below against the slots):
//   - the ones with a Black 2 stand-in play directly; with the Unova answer Music_Redirect's reverse table plays the
//     stand-in (data/hoenn_music.json "reverse"): rival encounters -> SEQ_BGM_E_HUE, Mr. Briney's boat -> NAMINORI;
//   - the ones Black 2 has nothing for (h_playbgm_hoenn): played only with the Hoenn answer, so the Unova answer keeps
//     whatever Black 2 played there.
// The option test: BGMIsPlaying (s009B) ignores its BGM argument in Black 2; hoenn_music.c answers the option when the
// argument is MUSIC_QUERY_HOENN (1 = Hoenn music).
#ifndef HOENN_MUSIC_INC
#define HOENN_MUSIC_INC

#define MUSIC_QUERY_HOENN 0xFFF0

#define MUS_HOENN_ENCOUNTER_MAY SEQ_BGM_E_CHEREN                // mus_encounter_may (Unova: SEQ_BGM_E_HUE)
#define MUS_HOENN_ENCOUNTER_BRENDAN SEQ_BGM_E_BERU              // mus_encounter_brendan (Unova: SEQ_BGM_E_HUE)
#define MUS_HOENN_SAILING SEQ_BGM_E_DOCTOR                      // mus_sailing (Unova: SEQ_BGM_NAMINORI)
#define MUS_HOENN_HELP SEQ_BGM_C_03                             // mus_help (Hoenn answer only)
#define MUS_HOENN_CABLE_CAR SEQ_BGM_SW_D_REGI                   // mus_cable_car (Hoenn answer only)
#define MUS_HOENN_ENCOUNTER_ELITE_FOUR SEQ_SE_SW_KYUREON_01_10  // mus_encounter_elite_four (Hoenn answer only)

    .macro h_goto_if_hoenn_music label         // jumps with Birch's "Hoenn music" answer (work 0x8007 is kept)
    VMStackPush 0x8007
    BGMIsPlaying MUSIC_QUERY_HOENN, 0x8007
    WorkCmpConst 0x8007, 1
    VMJumpIf CMP_EQ, .Lhm_yes\@
    VMStackPop 0x8007
    VMJump .Lhm_end\@
.Lhm_yes\@:
    VMStackPop 0x8007
    VMJump \label
.Lhm_end\@:
    .endm
    .macro h_playbgm_hoenn bgm                 // BGMPlay a Sapphire song only with the Hoenn answer (Unova: nothing)
    h_goto_if_hoenn_music .Lhm_play\@
    VMJump .Lhm_done\@
.Lhm_play\@:
    BGMPlay \bgm
.Lhm_done\@:
    .endm

#endif
