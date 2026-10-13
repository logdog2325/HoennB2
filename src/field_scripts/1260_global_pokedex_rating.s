// Global scripts 10380-10382 (a/0/5/6 entry 1260, text file 434 = src/text/script/0434.txt): Black 2's data/field_scripts/1260.s is
// Professor Juniper's Pokédex rating (Script_1 10380 her lab, Script_2 10381 her father, Script_3 10382 her PC, which the
// Pokémon Center PC's "Professor's PC" calls: global 10090 = file 1244 L_05B2). Rewritten for Hoenn (room_pc, 2026-10-09).
//   Black 2's rating counts the species of its own regional dex (PML_PersonalLoadRegionalDexTable, personal file 709: the 300
//   Unova species, PokeDex_GetCaughtNoUnova): a Mudkip or Treecko is not in it, so the PC would rate Hoenn by Unova numbers.
//   This is Sapphire's ProfBirch_EventScript_RatePokedex instead (pokeruby data/scripts/prof_birch.inc, data/text/
//   pokedex_rating.inc, src/birch_pc.c), the same port as chapter Ch11's in the Champion's room (0068): the Hoenn counts of the
//   202 Hoenn species (scenes/ch11_dexcount.inc: Sub_C11_CountDex), "Hmhm... So, you've seen N Pokémon, and you've caught N
//   Pokémon...", then Sapphire's line for the caught count (one line per 10 species, 200 or more = complete), then, once
//   the National Dex is on, "On a nationwide basis..." with the National counts. Black 2's windows (the PC's system
//   windows: SystemMsg + MsgWaitAdvance) and its rating jingle (SEQ_ME_HYOUKA1-6: Black 2's tiers 39/99/159/229/296 of 296
//   scaled to the 202 species = 26/67/108/156/201, 6 = complete). Not Hoenn: Juniper's lab / her father's script
//   (10380, 10381: Black 2's zone 792 is Birch's Lab here and never calls them) and the Permit / Oval Charm / Shiny Charm gifts.
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_story.inc"

#define RP_SEEN 0x8040
#define RP_CAUGHT 0x8041
#define RP_TMP 0x8042
#define RP_NAT_SEEN 0x8043
#define RP_NAT_CAUGHT 0x8044
#define RP_NAT 0x8045
// scenes/ch11_dexcount.inc (guarded: it is another chapter's file; the same names and works)
#define C11_DEXKIND 0x8062
#define C11_DEXCOUNT 0x8063
#define C11_DEXTMP 0x8064
#define T_SoYouveSeen 0
#define T_Rating10 1                      /* lines 1-20: the rating for the caught count / 10 (0-19) */
#define T_DexCompleted 21
#define T_OnANationwideBasis 22

    ScriptEntry Script_1
    ScriptEntry Script_2
    ScriptEntry Script_3
    ScriptEntriesEnd

Script_1:                                        // 10380: Black 2's Juniper in her lab (not used in Hoenn)
    RTEndGlobal

Script_2:                                        // 10381: Black 2's Juniper's father (not used in Hoenn)
    RTEndGlobal

Script_3:                                        // 10382: the PC's rating (after "Accessed Prof. Birch's PC.")
    WorkSetConst C11_DEXKIND, 0
    VMCall Sub_C11_CountDex
    WorkSet RP_SEEN, C11_DEXCOUNT                // Hoenn species seen
    WorkSetConst C11_DEXKIND, 1
    VMCall Sub_C11_CountDex
    WorkSet RP_CAUGHT, C11_DEXCOUNT              // Hoenn species caught
    WordSetNumber 0, RP_SEEN, 3                  // buffernumberstring 0 / 1
    WordSetNumber 1, RP_CAUGHT, 3
    SystemMsg T_SoYouveSeen, 2                   // Hmhm... So, you've seen N Pokémon, and you've caught N Pokémon...
    h_goto_if_ge RP_CAUGHT, 200, L_RP_Me6
    h_goto_if_ge RP_CAUGHT, 157, L_RP_Me5
    h_goto_if_ge RP_CAUGHT, 109, L_RP_Me4
    h_goto_if_ge RP_CAUGHT, 68, L_RP_Me3
    h_goto_if_ge RP_CAUGHT, 27, L_RP_Me2
    MEPlay SEQ_ME_HYOUKA1
    VMJump L_RP_MeDone
L_RP_Me2:
    MEPlay SEQ_ME_HYOUKA2
    VMJump L_RP_MeDone
L_RP_Me3:
    MEPlay SEQ_ME_HYOUKA3
    VMJump L_RP_MeDone
L_RP_Me4:
    MEPlay SEQ_ME_HYOUKA4
    VMJump L_RP_MeDone
L_RP_Me5:
    MEPlay SEQ_ME_HYOUKA5
    VMJump L_RP_MeDone
L_RP_Me6:
    MEPlay SEQ_ME_HYOUKA6
L_RP_MeDone:
    MEWait
    MsgWaitAdvance
    h_goto_if_ge RP_CAUGHT, 200, L_RP_Complete   // (Sapphire: 200 and 201 are "complete" unless Jirachi / Deoxys are
    WorkSet RP_TMP, RP_CAUGHT                    //  counted; the same simplification as chapter Ch11's)
    WorkDiv RP_TMP, 10
    WorkAdd RP_TMP, T_Rating10
    SystemMsg RP_TMP, 2                          // the rating line for the caught count
    MsgWaitAdvance
    VMJump L_RP_National
L_RP_Complete:
    SystemMsg T_DexCompleted, 2                  // Congratulations! Your Pokédex is complete!
    MsgWaitAdvance
L_RP_National:
    PokeDexHaveNational RP_NAT                   // Sapphire: only when the National Dex is enabled
    h_goto_if_eq RP_NAT, 0, L_RP_Done
    PokeDexGetCount 0, RP_NAT_SEEN               // National seen / caught
    PokeDexGetCount 1, RP_NAT_CAUGHT
    WordSetNumber 0, RP_NAT_SEEN, 3
    WordSetNumber 1, RP_NAT_CAUGHT, 3
    SystemMsg T_OnANationwideBasis, 2            // Hmhm... On a nationwide basis... You've seen N Pokémon, and you've caught N ...
    MsgWaitAdvance
L_RP_Done:
    RTEndGlobal

#if __has_include("scenes/ch11_dexcount.inc")
#include "scenes/ch11_dexcount.inc"              // Sub_C11_CountDex: C11_DEXKIND (0 seen, 1 caught) -> C11_DEXCOUNT
#else
Sub_C11_CountDex:                                // fallback without chapter Ch11's file: counts nothing
    WorkSetConst C11_DEXCOUNT, 0
    VMReturn
#endif
    .balign 4, 0
