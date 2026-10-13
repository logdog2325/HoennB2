// Route 103's story (Sapphire data/maps/Route103/scripts.inc; chapter Ch1, the worked example of
// notes/STORY_PORTING.md). converter/gen_map_content.py includes this file twice in the generated zone file
// 0652_auto_Route103.s: the entries below become scripts 1-2, the generated signs/people follow.
// Text: src/text/scenes/Route103.txt, lines 0-5 (the generated lines follow). Rival NPC (uid 102, Sapphire object 2,
// code RIVAL_GFX = work 0x4020): data/story/ch1.json. Map scripts: scenes/Route103_init.inc.
#ifdef SCENE_ENTRIES
    ScriptEntry Story_Rival         // 1: Route103_EventScript_14EB92 (talk to the rival)
    ScriptEntry Story_Init          // 2: Route103_OnTransition (zone init)
#else
#define R103_RIVAL 102

Story_Init:                         // Common_EventScript_SetupRivalGfxId (ProfBirch_EventScript_UpdateLocation: later,
    RTCallGlobal 8297                       // the berry trees' new-day reset (converter/gen_hidden_items.py; missing_objects)
    h_setup_rival_gfx               // with Birch's Pokedex rating on Route 101/103)
#if __has_include("scenes/Route103_AlteringCave.inc")
    VMCall Sub_AC_Door              // (postgame_maps) Emerald's Altering Cave: its mouth, the door's zone of the day
#endif
    VMHalt

Story_Rival:
    h_lock
    h_goto_if_girl L_R103_BrendanTalk
    h_msgbox 0                                   // May: Let's see... The Pokemon found on Route 103 include...
    h_closemessage
    h_playbgm MUS_ENCOUNTER_MAY
    VMJump L_R103_Notice
L_R103_BrendanTalk:
    h_msgbox 3                                   // Brendan: Okay, so it's this one and that one...
    h_closemessage
    h_playbgm MUS_ENCOUNTER_BRENDAN
L_R103_Notice:
    h_faceplayer                                 // Common_Movement_FacePlayer
    h_applymovement R103_RIVAL, Mv_R103_Notice   // Common_Movement_ExclamationMark, Common_Movement_Delay48
    h_waitmovement
    h_buffer_player
    h_goto_if_girl L_R103_BrendanChallenge
    h_msgbox 1                                   // Oh, hi, <player>! ... let's have a quick battle!
    h_closemessage
    h_goto_if_eq VAR_STARTER_MON, 0, L_R103_May4
    h_goto_if_eq VAR_STARTER_MON, 1, L_R103_May7
    h_trainerbattle TRAINER_MAY_1                // Mudkip: May has Treecko
    VMJump L_R103_MayAfter
L_R103_May4:
    h_trainerbattle TRAINER_MAY_4
    VMJump L_R103_MayAfter
L_R103_May7:
    h_trainerbattle TRAINER_MAY_7
L_R103_MayAfter:
    h_msgbox 2                                   // May: I think I know why my dad has an eye out for you now...
    VMJump L_R103_Leave
L_R103_BrendanChallenge:
    h_msgbox 4                                   // Hey, it's <player>! ... how about a little battle?
    h_closemessage
    h_goto_if_eq VAR_STARTER_MON, 0, L_R103_Brendan4
    h_goto_if_eq VAR_STARTER_MON, 1, L_R103_Brendan7
    h_trainerbattle TRAINER_BRENDAN_1
    VMJump L_R103_BrendanAfter
L_R103_Brendan4:
    h_trainerbattle TRAINER_BRENDAN_4
    VMJump L_R103_BrendanAfter
L_R103_Brendan7:
    h_trainerbattle TRAINER_BRENDAN_7
L_R103_BrendanAfter:
    h_msgbox 5                                   // Brendan: I think I get it...
L_R103_Leave:                                    // Route103_EventScript_14ECD9
    h_closemessage
    h_getplayerfacing HLIB_TMP                   // Sapphire VAR_FACING 2 (north) = Black 2 0: go around the player
    h_goto_if_eq HLIB_TMP, 0, L_R103_AroundPlayer
    h_applymovement R103_RIVAL, Mv_R103_DownToLedge
    h_waitmovement
    h_playse SE_LEDGE
    h_applymovement R103_RIVAL, Mv_R103_JumpAway2
    h_waitmovement
    VMJump L_R103_Gone
L_R103_AroundPlayer:
    h_applymovement R103_RIVAL, Mv_R103_AroundPlayer
    h_waitmovement
    h_playse SE_LEDGE
    h_applymovement R103_RIVAL, Mv_R103_JumpAway3
    h_waitmovement
L_R103_Gone:                                     // Route103_EventScript_14ED46
    h_removeobject R103_RIVAL, FLAG_HIDE_RIVAL_ROUTE103
    h_setvar VAR_ROUTE103_STATE, 1
    h_setvar VAR_BIRCH_LAB_STATE, 4
    h_clearflag FLAG_HIDE_RIVAL_BIRCH_LAB
    h_setflag FLAG_DEFEATED_RIVAL_ROUTE103
    h_setvar VAR_OLDALE_STATE, 1
    h_clearflag FLAG_HIDE_RIVAL_OLDALE_TOWN
    h_fadedefaultbgm                             // savebgm 0 + fadedefaultbgm
    h_release

    .balign 4, 0
Mv_R103_Notice:
    emote_exclamation_mark
    delay_16 3
    step_end
Mv_R103_AroundPlayer:                            // Route103_Movement_14ED67
    walk_left
    walk_down
    walk_down
    step_end
Mv_R103_JumpAway3:                               // Route103_Movement_14ED6B
    jump_2_down
    delay_16
    walk_down
    walk_down
    walk_down
    step_end
Mv_R103_DownToLedge:                             // Route103_Movement_14ED71
    walk_down
    walk_down
    step_end
Mv_R103_JumpAway2:                               // Route103_Movement_14ED74
    jump_2_down
    delay_16
    walk_down
    walk_down
    step_end
#if __has_include("scenes/Route103_AlteringCave.inc")
#include "scenes/Route103_AlteringCave.inc"     // (postgame_maps: Sub_AC_Door)
#endif
#endif
