// Emerald helpers for the Team Magma chapters (emerald_ch45_magma 2026-10-12; notes/EMERALD_STORY.md Ch4, Ch5, Ch8).
// Include after "hoenn_story.inc" (and only under #ifdef HOENN_EMERALD: nothing here is for Sapphire or Ruby).
#ifndef EM_MAGMA_LIB_INC
#define EM_MAGMA_LIB_INC

// playbgm MUS_ENCOUNTER_MAGMA, FALSE (pokeemerald plays it at Meteor Falls, Mt. Chimney, the Magma Hideout): Hoenn music
// plays mus_encounter_magma (slot SEQ_SE_SW_KYUREON_01_02b, data/hoenn_music.json); with Birch's Unova answer Black 2's
// Plasma theme plays, as MUS_EVIL_TEAM does for Team Aqua (hoenn_music redirects it to mus_encounter_aqua).
    .macro em_bgm_magma
    h_goto_if_hoenn_music .Lemm_hoenn\@
    BGMPlay MUS_EVIL_TEAM
    VMJump .Lemm_done\@
.Lemm_hoenn\@:
    BGMPlay SEQ_SE_SW_KYUREON_01_02b
.Lemm_done\@:
    .endm

// playbgm MUS_ENCOUNTER_AQUA, FALSE
    .macro em_bgm_aqua
    BGMPlay MUS_EVIL_TEAM
    .endm

#endif
