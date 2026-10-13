// Emerald's Rustboro City: the rival's battle (emerald_ch0_3, 2026-10-12; notes/EMERALD_STORY.md Ch2). Bodies included at the end of
// the bodies of scenes/RustboroCity.inc in an Emerald build only; the entry (25, last) is listed under #ifdef HOENN_EMERALD in the
// entry part, so it exists in the Emerald build once converter/gen_map_content.py has been run in Emerald mode (S0-1).
// Source: pokeemerald data/maps/RustboroCity/scripts.inc (RivalTrigger0-7, Rival, RivalEncounter, the May/Brendan encounters).
//
// Sapphire's rival in Rustboro (RB_Rival, script 21) only talks. In Emerald, Mr. Stone's scene (1154_room_...DevonCorp_3F.s) sets
// VAR_RUSTBORO_STATE 7 and clears the rival's hide flag; walking south over the row y = 53 (x 12-19: Em_RB_RivalTrigger, one 1x8
// trigger while the state is 7) or talking to the rival at (16, 50) starts her/his scene: "Registered <rival> in the PokéNav" (a
// plain message, decision 3A), "How about a little battle?" (YES/NO), the battle (the rival's starter by the player's:
// TRAINER_<MAY|BRENDAN>_RUSTBORO_<TREECKO|TORCHIC|MUDKIP>, src/include/hoenn_trainers_emerald.h), then Mr. Briney's hint.
// FLAG_DEFEATED_RIVAL_RUSTBORO is set by a win; a loss whites out (and the next talk asks again: no softlock).
// VAR_RUSTBORO_STATE 8, VAR_ROUTE104_STATE 2 at the first meeting (the rival is not on Route 104 then).
// The rival is Sapphire's story object uid 164 (model 162, FLAG_HIDE_RIVAL_RUSTBORO). Zone tiles = pokeemerald tiles + (48, 180).
// Text (src/text/scenes/emerald/RustboroCity.txt): 15 / 16 HiLetsRegister (May / Brendan), 17 / 18 MrBrineyHint, then appended
// 20 / 21 Registered, 22 / 23 PassedBrineyWantToBattle, 24 / 25 HaventRaised / NoConfidence, 26 / 27 WantToBattle,
// 28 / 29 ImNotGoingToLose / IWontGoEasy.
#include "scenes/emerald/b1_common.inc"
#include "hoenn_trainers_emerald.h"

#define EM_RB_T_HiLetsRegister 15
#define EM_RB_T_HiLetsRegister_G 16
#define EM_RB_T_Registered 20
#define EM_RB_T_Registered_G 21
#define EM_RB_T_PassedBriney 22
#define EM_RB_T_PassedBriney_G 23
#define EM_RB_T_NoBattle 24
#define EM_RB_T_NoBattle_G 25
#define EM_RB_T_WantToBattle 26
#define EM_RB_T_WantToBattle_G 27
#define EM_RB_T_ImNotGoingToLose 28
#define EM_RB_T_ImNotGoingToLose_G 29
#define EM_RB_T_BrineyHint 17
#define EM_RB_T_BrineyHint_G 18

Em_RB_RivalTrigger:                              // RustboroCity_EventScript_RivalTrigger0-7
    h_lock
    PlayerGetGPos 0x8020, 0x8021
    h_copyvar 0x8008, 0x8020
    h_subvar 0x8008, 60                          // 48 + 12: the trigger's x, 0-7
    VMCall Sub_Em_RB_RivalMusic
    h_applymovement RB_RIVAL, Common_Movement_WalkInPlaceFastestDown
    h_waitmovement
    h_applymovement RB_RIVAL, Mv_Em_RB_Notice    // playse SE_PIN + "!" + Delay48
    h_waitmovement
    h_goto_if_eq 0x8008, 1, L_Em_RB_Ap1
    h_goto_if_eq 0x8008, 2, L_Em_RB_Ap2
    h_goto_if_eq 0x8008, 3, L_Em_RB_Ap3
    h_goto_if_eq 0x8008, 4, L_Em_RB_Ap4
    h_goto_if_eq 0x8008, 5, L_Em_RB_Ap5
    h_goto_if_eq 0x8008, 6, L_Em_RB_Ap6
    h_goto_if_eq 0x8008, 7, L_Em_RB_Ap7
    h_applymovement RB_RIVAL, Mv_Em_RB_Approach0
    VMJump L_Em_RB_Approached
L_Em_RB_Ap1:
    h_applymovement RB_RIVAL, Mv_Em_RB_Approach1
    VMJump L_Em_RB_Approached
L_Em_RB_Ap2:
    h_applymovement RB_RIVAL, Mv_Em_RB_Approach2
    VMJump L_Em_RB_Approached
L_Em_RB_Ap3:
    h_applymovement RB_RIVAL, Mv_Em_RB_Approach3
    VMJump L_Em_RB_Approached
L_Em_RB_Ap4:
    h_applymovement RB_RIVAL, Mv_Em_RB_Approach4
    VMJump L_Em_RB_Approached
L_Em_RB_Ap5:
    h_applymovement RB_RIVAL, Mv_Em_RB_Approach5
    VMJump L_Em_RB_Approached
L_Em_RB_Ap6:
    h_applymovement RB_RIVAL, Mv_Em_RB_Approach6
    VMJump L_Em_RB_Approached
L_Em_RB_Ap7:
    h_applymovement RB_RIVAL, Mv_Em_RB_Approach7
L_Em_RB_Approached:
    h_waitmovement
    h_applymovement 255, Common_Movement_WalkInPlaceFastestUp
    h_waitmovement
    VMJump L_Em_RB_Encounter

RB_Rival:                                        // RustboroCity_EventScript_Rival (talked to)
    h_lock
    h_goto_if_set FLAG_MET_RIVAL_RUSTBORO, L_Em_RB_TalkFace
    VMCall Sub_Em_RB_RivalMusic
L_Em_RB_TalkFace:
    SEPlay SEQ_SE_MESSAGE
    h_faceplayer                                 // Common_Movement_FacePlayer
L_Em_RB_Encounter:                               // RustboroCity_EventScript_RivalEncounter (May for a boy, Brendan for a girl)
    h_buffer_player
    h_setvar 0x8009, 0                           // VAR_0x8008 of pokeemerald: 0 = first meeting (the music was changed)
    h_goto_if_set FLAG_DEFEATED_RIVAL_RUSTBORO, L_Em_RB_BrineyHint
    h_goto_if_set FLAG_MET_RIVAL_RUSTBORO, L_Em_RB_AskToBattle
    h_setflag FLAG_MET_RIVAL_RUSTBORO
    h_msgbox_gendered EM_RB_T_HiLetsRegister, EM_RB_T_HiLetsRegister_G, RB_RIVAL      // Oh, hi, <player>! You had a Match Call feature put on your PokéNav! ...
    h_closemessage
    h_delay 30
    h_playfanfare MUS_REGISTER_MATCH_CALL
    h_msgbox_gendered EM_RB_T_Registered, EM_RB_T_Registered_G, RB_RIVAL              // Registered <rival> in the PokéNav.
    h_waitfanfare
    h_closemessage
    h_delay 30
    h_setvar VAR_RUSTBORO_STATE, 8
    h_setvar VAR_ROUTE104_STATE, 2
    em_yesno_gendered EM_RB_T_PassedBriney, EM_RB_T_PassedBriney_G, RB_RIVAL, HLIB_TMP   // ... How about a little battle?
    h_goto_if_yes HLIB_TMP, L_Em_RB_Battle
    h_msgbox_gendered EM_RB_T_NoBattle, EM_RB_T_NoBattle_G, RB_RIVAL                  // Oh, what's the matter? Haven't you caught or raised your Pokémon very much? ...
    h_fadedefaultbgm
    h_release
L_Em_RB_AskToBattle:
    h_setvar 0x8009, 1
    em_yesno_gendered EM_RB_T_WantToBattle, EM_RB_T_WantToBattle_G, RB_RIVAL, HLIB_TMP   // So, what do you think? How about a little battle here?
    h_goto_if_yes HLIB_TMP, L_Em_RB_Battle
    h_msgbox_gendered EM_RB_T_NoBattle, EM_RB_T_NoBattle_G, RB_RIVAL
    h_release
L_Em_RB_Battle:                                  // ..._EventScript_BattleMay / BattleBrendan
    h_msgbox_gendered EM_RB_T_ImNotGoingToLose, EM_RB_T_ImNotGoingToLose_G, RB_RIVAL   // You just became a Trainer, <player>. I'm not going to lose!
    h_closemessage
#ifdef HOENN_TEST_CHRLOSE                        // test builds only: the first battle is against Steven (a sure loss), the next is the real one
    h_goto_if_set FLAG_DEFEATED_ELITE_4_PHOEBE, L_Em_RB_RealBattle
    h_setflag FLAG_DEFEATED_ELITE_4_PHOEBE
    h_trainerbattle TRAINER_STEVEN
    VMJump L_Em_RB_Defeated
L_Em_RB_RealBattle:
#endif
    h_goto_if_girl L_Em_RB_BrendanBattle
    h_goto_if_eq VAR_STARTER_MON, 0, L_Em_RB_MayTreecko
    h_goto_if_eq VAR_STARTER_MON, 1, L_Em_RB_MayTorchic
    h_trainerbattle TRAINER_MAY_RUSTBORO_MUDKIP
    VMJump L_Em_RB_Defeated
L_Em_RB_MayTreecko:
    h_trainerbattle TRAINER_MAY_RUSTBORO_TREECKO
    VMJump L_Em_RB_Defeated
L_Em_RB_MayTorchic:
    h_trainerbattle TRAINER_MAY_RUSTBORO_TORCHIC
    VMJump L_Em_RB_Defeated
L_Em_RB_BrendanBattle:
    h_goto_if_eq VAR_STARTER_MON, 0, L_Em_RB_BrendanTreecko
    h_goto_if_eq VAR_STARTER_MON, 1, L_Em_RB_BrendanTorchic
    h_trainerbattle TRAINER_BRENDAN_RUSTBORO_MUDKIP
    VMJump L_Em_RB_Defeated
L_Em_RB_BrendanTreecko:
    h_trainerbattle TRAINER_BRENDAN_RUSTBORO_TREECKO
    VMJump L_Em_RB_Defeated
L_Em_RB_BrendanTorchic:
    h_trainerbattle TRAINER_BRENDAN_RUSTBORO_TORCHIC
L_Em_RB_Defeated:
    h_setflag FLAG_DEFEATED_RIVAL_RUSTBORO
L_Em_RB_BrineyHint:                              // ..._MayBrineyHint / BrendanBrineyHint
    h_buffer_player
    h_msgbox_gendered EM_RB_T_BrineyHint, EM_RB_T_BrineyHint_G, RB_RIVAL    // Oh, by the way, Mr. Briney, who I just passed... was once a revered seafarer.
    h_goto_if_ne 0x8009, 0, L_Em_RB_HintDone
    h_fadedefaultbgm                             // savebgm MUS_DUMMY + fadedefaultbgm (only when the meeting started the music)
L_Em_RB_HintDone:
    h_release

Sub_Em_RB_RivalMusic:                            // RustboroCity_EventScript_PlayRivalMusic: the theme of the rival you meet
    h_goto_if_girl L_Em_RB_MusicBrendan
    h_playbgm MUS_ENCOUNTER_MAY
    VMReturn
L_Em_RB_MusicBrendan:
    h_playbgm MUS_ENCOUNTER_BRENDAN
    VMReturn

    .balign 4, 0
Mv_Em_RB_Notice:
    emote_exclamation_mark
    delay_16 3
    step_end
Mv_Em_RB_Approach0:                              // RustboroCity_Movement_RivalApproachPlayer0-7
    walk_down
    walk_left 4
    walk_down
    step_end
Mv_Em_RB_Approach1:
    walk_down
    walk_left 3
    walk_down
    step_end
Mv_Em_RB_Approach2:
    walk_down
    walk_left 2
    walk_down
    step_end
Mv_Em_RB_Approach3:
    walk_down
    walk_left
    walk_down
    step_end
Mv_Em_RB_Approach4:
    walk_down 2
    step_end
Mv_Em_RB_Approach5:
    walk_down
    walk_right
    walk_down
    step_end
Mv_Em_RB_Approach6:
    walk_down
    walk_right 2
    walk_down
    step_end
Mv_Em_RB_Approach7:
    walk_down
    walk_right 3
    walk_down
    step_end
    .balign 4, 0
