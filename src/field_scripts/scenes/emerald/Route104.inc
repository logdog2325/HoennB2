// Emerald's Route 104: the rival outside Mr. Briney's cottage (emerald_ch0_3, 2026-10-12; notes/EMERALD_STORY.md Ch2). Bodies included
// at the end of the bodies of scenes/Route104.inc in an Emerald build only; the entries 9 and 10 (last, under #ifdef HOENN_EMERALD in
// the entry part) exist in the Emerald build once converter/gen_map_content.py has been run in Emerald mode (S0-1).
// Source: pokeemerald data/maps/Route104/scripts.inc (RivalTrigger, Rival, RivalEncounter, TrySetRivalPos).
//
// The other place to meet the rival: if the player gets past Rustboro's trigger row without meeting the rival (Mr. Stone's scene sets
// VAR_ROUTE104_STATE 1 and VAR_RUSTBORO_STATE 7 together), stepping on (17, 51) in front of the cottage while VAR_ROUTE104_STATE is 1
// makes the rival come out of the cottage (Em_R104_RivalTrigger, entry 9): she/he takes Rustboro's place (FLAG_HIDE_RIVAL_RUSTBORO set,
// VAR_RUSTBORO_STATE 8, VAR_ROUTE104_STATE 2), "We should register each other" (plain message), "How's your Pokédex coming along?", and
// the same battle as in Rustboro (FLAG_DEFEATED_RIVAL_ROUTE_104). The rival then stays at (16, 52) and can be talked to
// (Em_R104_Rival, entry 10: the battle again until it is won, then the after-battle line). A loss whites out; no softlock.
// Object: data/story/emerald/e_ch2.json (uid 150, RIVAL_GFX 162, hidden by FLAG_HIDE_ROUTE_104_RIVAL, standing at (16, 52) facing right,
// where pokeemerald's copyobjectxytoperm leaves her/him; the scene starts her/him at the cottage door (17, 50)).
// Zone tiles = pokeemerald tiles + (48, 240). Text (src/text/scenes/emerald/Route104.txt): 8 / 9 WeShouldRegister (May / Brendan),
// 10 / 11 Registered, 12 / 13 HowsYourPokedex, 14 / 15 MinesDecent / DoingGreat LetsBattle, 16 / 17 HaventRaised / NoConfidence,
// 18 / 19 LetsBattle, 20 / 21 Intro, 22 / 23 PostBattle.
#include "scenes/emerald/b1_common.inc"
#include "hoenn_trainers_emerald.h"

#define EM_R104_RIVAL 150
#define EM_R104_X 48
#define EM_R104_Z 240

Em_R104_RivalTrigger:                            // Route104_EventScript_RivalTrigger
    h_lock
    h_setflag FLAG_HIDE_RIVAL_RUSTBORO
    h_setvar VAR_RUSTBORO_STATE, 8
    h_setvar VAR_ROUTE104_STATE, 2
    h_applymovement 255, Common_Movement_WalkInPlaceFastestUp
    h_waitmovement
    h_delay 10
    h_applymovement 255, Mv_Em_R104_PlayerBackUp
    h_waitmovement
    h_playse SE_EXIT                             // the cottage door: the rival is out on the tile in front of it (pokeemerald walks
    h_delay 10                                   // out of the door onto it; the door tile itself is solid here, so no one stands on it)
    h_addobject EM_R104_RIVAL, FLAG_HIDE_ROUTE_104_RIVAL
    ActorSetGPos EM_R104_RIVAL, EM_R104_X + 17, 1, EM_R104_Z + 51, 1      // (y: 16-unit levels: this ground is 16 units high)
    h_delay 20
    h_setvar 0x8009, 0                           // VAR_0x8008 of pokeemerald: 0 = the scene started the music
    h_goto_if_girl L_Em_R104_MusicBrendan
    h_playbgm MUS_ENCOUNTER_MAY
    VMJump L_Em_R104_Noticed
L_Em_R104_MusicBrendan:
    h_playbgm MUS_ENCOUNTER_BRENDAN
L_Em_R104_Noticed:
    h_applymovement EM_R104_RIVAL, Mv_Em_R104_Notice     // playse SE_PIN + "!" + Delay48
    h_waitmovement
    VMJump L_Em_R104_Encounter

Em_R104_Rival:                                   // Route104_EventScript_Rival (talked to)
    h_lock
    SEPlay SEQ_SE_MESSAGE
    h_faceplayer
    h_setvar 0x8009, 1
L_Em_R104_Encounter:                             // Route104_EventScript_RivalEncounter
    h_buffer_player
    h_goto_if_set FLAG_DEFEATED_RIVAL_ROUTE_104, L_Em_R104_Defeated
    h_goto_if_set FLAG_REGISTER_RIVAL_POKENAV, L_Em_R104_AskToBattle
    h_setflag FLAG_REGISTER_RIVAL_POKENAV
    h_msgbox_gendered 8, 9, EM_R104_RIVAL        // May: Oh, hi, <player>! Devon upgraded your PokéNav with the Match Call system, huh? ...
    h_closemessage
    h_delay 30
    h_playfanfare MUS_REGISTER_MATCH_CALL
    h_msgbox_gendered 10, 11, EM_R104_RIVAL      // Registered <rival> in the PokéNav.
    h_waitfanfare
    h_closemessage
    h_delay 30
    h_applymovement 255, Mv_Em_R104_PlayerFaceRival
    h_applymovement EM_R104_RIVAL, Mv_Em_R104_WalkSlowLeft
    h_msgbox_gendered 12, 13, EM_R104_RIVAL      // Oh, by the way, <player>, how's your Pokédex coming along?
    h_closemessage
    h_waitmovement
    h_applymovement EM_R104_RIVAL, Mv_Em_R104_ApproachPlayer
    h_waitmovement
    em_yesno_gendered 14, 15, EM_R104_RIVAL, HLIB_TMP     // Mine's looking pretty decent. So... How about a little battle?
    h_goto_if_yes HLIB_TMP, L_Em_R104_Battle
    h_msgbox_gendered 16, 17, EM_R104_RIVAL      // Oh, what's the matter? Haven't you caught or raised your Pokémon very much? ...
    h_fadedefaultbgm
    h_release
L_Em_R104_AskToBattle:
    em_yesno_gendered 18, 19, EM_R104_RIVAL, HLIB_TMP     // So, what do you think? How about a little battle here?
    h_goto_if_yes HLIB_TMP, L_Em_R104_Battle
    h_msgbox_gendered 16, 17, EM_R104_RIVAL
    h_release
L_Em_R104_Battle:
    h_msgbox_gendered 20, 21, EM_R104_RIVAL      // You just became a Trainer, <player>. I'm not going to lose!
    h_closemessage
#ifdef HOENN_TEST_CHRLOSE                        // test builds only: the first battle is against Steven (a sure loss), the next is the real one
    h_goto_if_set FLAG_DEFEATED_ELITE_4_PHOEBE, L_Em_R104_RealBattle
    h_setflag FLAG_DEFEATED_ELITE_4_PHOEBE
    h_trainerbattle TRAINER_STEVEN
    VMJump L_Em_R104_Won
L_Em_R104_RealBattle:
#endif
    h_goto_if_girl L_Em_R104_BrendanBattle
    h_goto_if_eq VAR_STARTER_MON, 0, L_Em_R104_MayTreecko
    h_goto_if_eq VAR_STARTER_MON, 1, L_Em_R104_MayTorchic
    h_trainerbattle TRAINER_MAY_RUSTBORO_MUDKIP
    VMJump L_Em_R104_Won
L_Em_R104_MayTreecko:
    h_trainerbattle TRAINER_MAY_RUSTBORO_TREECKO
    VMJump L_Em_R104_Won
L_Em_R104_MayTorchic:
    h_trainerbattle TRAINER_MAY_RUSTBORO_TORCHIC
    VMJump L_Em_R104_Won
L_Em_R104_BrendanBattle:
    h_goto_if_eq VAR_STARTER_MON, 0, L_Em_R104_BrendanTreecko
    h_goto_if_eq VAR_STARTER_MON, 1, L_Em_R104_BrendanTorchic
    h_trainerbattle TRAINER_BRENDAN_RUSTBORO_MUDKIP
    VMJump L_Em_R104_Won
L_Em_R104_BrendanTreecko:
    h_trainerbattle TRAINER_BRENDAN_RUSTBORO_TREECKO
    VMJump L_Em_R104_Won
L_Em_R104_BrendanTorchic:
    h_trainerbattle TRAINER_BRENDAN_RUSTBORO_TORCHIC
L_Em_R104_Won:
    h_setflag FLAG_DEFEATED_RIVAL_ROUTE_104
L_Em_R104_Defeated:                              // ..._MayDefeated / BrendanDefeated
    h_buffer_player
    h_msgbox_gendered 22, 23, EM_R104_RIVAL      // I can tell you've gotten pretty good with the way you handle Pokémon. ...
    h_goto_if_ne 0x8009, 0, L_Em_R104_Done
    h_fadedefaultbgm
L_Em_R104_Done:
    h_release

    .balign 4, 0
Mv_Em_R104_PlayerBackUp:                         // Route104_Movement_PlayerBackUp
    lock_facing_direction
    walk_down
    unlock_facing_direction
    step_end
Mv_Em_R104_Notice:
    emote_exclamation_mark
    delay_16 3
    step_end
Mv_Em_R104_PlayerFaceRival:
    delay_4
    walk_in_place_fastest_left
    step_end
Mv_Em_R104_WalkSlowLeft:
    walk_slow_left
    step_end
Mv_Em_R104_ApproachPlayer:                       // ..._RivalApproachPlayer (then the object stays here: json position (16, 52))
    walk_down
    face_right
    step_end
    .balign 4, 0
#include "common/movement.inc"
