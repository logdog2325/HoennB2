// GraniteCave_StevensRoom (zone 126): cave_builder (converter/gen_caves.py): ladders and cracked floors as step triggers
// (Sapphire's step-on warps), simple people/signs. Story scripts: add them after a line "// ---- story" (this
// generator keeps everything from that line on and the entries you add: b2tools/story_merge.py) and number them
// after these entries.
// (Sapphire's step-on warps), simple people/signs. Story scripts: add them after a line "// ---- story" (then this
// generator leaves the file alone) and number them after these entries.
// Story (chapter Ch2, Sapphire data/maps/GraniteCave_StevensRoom/scripts.inc): script 1 (Steven, uid 1 in
// data/story/ch2.json), text 0145 lines 0-4. Room origin (0,0).
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_trainers.h"
#include "hoenn_key_items.h"
#include "hoenn_story.inc"

    ScriptEntry GCS_Steven          // 1: GraniteCave_StevensRoom_EventScript_15CBFA
    ScriptEntriesEnd

Script_None:
    VMHalt
    .balign 4, 0

// ---- story
#define GCS_STEVEN 1

GCS_Steven:
    h_lock
    SEPlay SEQ_SE_MESSAGE
    h_faceplayer
    h_msgbox 0                      // That device you have there... It's a PokéNav. ...My name is Steven...
    h_closemessage
    h_handover_item ITEM_LETTER, 1  // Common_EventScript_PlayerHandedOverTheItem: {PLAYER} handed over the Letter.
    h_setflag FLAG_DELIVERED_STEVEN_LETTER
    h_msgbox 2                      // Steven: Okay, thank you. ...It contains my favorite move, Steel Wing.
    h_closemessage                  // (Black 2: the item script opens its own window)
    h_giveitem ITEM_TM47            // TM47 Steel Wing: no Gen 5 TM teaches it; TM47 kept as the stand-in (converter/gen_items.py rule)
    h_goto_if_ne HLIB_RESULT, 0, L_GCS_Given
    h_msgbox 4                      // Oh, your Bag is full... That's too bad, then.
L_GCS_Given:
    h_msgbox 3                      // Steven: Your Pokémon appear quite capable. ...Now, I've got to hurry along.
    h_closemessage
#ifdef HOENN_EMERALD                // Emerald (emerald_ch0_3): line 3 ends with "let's register one another in our PokéNavs"; a plain
#include "scenes/emerald/b1_common.inc"   // message + jingle (decision 3A), then "I've got to hurry along" (lines 5 and 6 of the overlay)
    h_delay 30
    h_playfanfare MUS_REGISTER_MATCH_CALL
    h_msgbox 5                      // Registered Steven in the PokéNav.
    h_waitfanfare
    h_closemessage
    h_delay 30
    h_msgbox 6                      // Steven: I've got to hurry along.
    h_closemessage
#endif
    h_getplayerfacing HLIB_TMP      // VAR_FACING 1 (the player faces south, Steven below): around the player
    h_goto_if_eq HLIB_TMP, 1, L_GCS_LeaveAround
    h_applymovement GCS_STEVEN, Mv_GCS_Leave
    h_waitmovement
    VMJump L_GCS_Gone
L_GCS_LeaveAround:
    h_applymovement GCS_STEVEN, Mv_GCS_LeaveAround
    h_waitmovement
L_GCS_Gone:
    h_playse SE_EXIT
    h_removeobject GCS_STEVEN, FLAG_HIDE_STEVEN_GRANITE_CAVE
    h_release

    .balign 4, 0
Mv_GCS_Leave:                       // GraniteCave_StevensRoom_Movement_15CC8C
    walk_up 5
    delay_8
    step_end
Mv_GCS_LeaveAround:                 // GraniteCave_StevensRoom_Movement_15CC93
    walk_left
    walk_up 3
    walk_right
    walk_up 2
    delay_8
    step_end
