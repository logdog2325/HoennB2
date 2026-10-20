// NewMauville_Inside (zone 133): cave_builder (converter/gen_caves.py): ladders and cracked floors as step triggers
// (Sapphire's step-on warps), simple people/signs. Story scripts: add them after a line "// ---- story" (this
// generator keeps everything from that line on and the entries you add: b2tools/story_merge.py) and number them
// after these entries.
// (Sapphire's step-on warps), simple people/signs. Story scripts: add them after a line "// ---- story" (then this
// generator leaves the file alone) and number them after these entries.
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_trainers.h"  // ch6 (before hoenn_story.inc: its macros name trainers)
#include "hoenn_story.inc"  // ch6

    ScriptEntry Script_None
    ScriptEntry Story_NI_BlueSwitch   // 2: step triggers on the blue switches (while work 0x4036 == 0: blue not down)  // story:
    ScriptEntry Story_NI_GreenSwitch   // 3: step triggers on the green switches (while work 0x4037 == 0: green not down)  // story:
    ScriptEntry Story_NI_GeneratorSwitch   // 4: step trigger (33,6) VAR_NEW_MAUVILLE_STATE 1  // story:
    ScriptEntry Story_NI_Generator   // 5: the generator (8 signs)  // story:
    ScriptEntry Story_NI_Voltorb1   // 6: object 6  // story:
    ScriptEntry Story_NI_Voltorb2   // 7: object 7  // story:
    ScriptEntry Story_NI_Voltorb3   // 8: object 8  // story:
    ScriptEntry Story_NI_Init   // 9: zone init (0267)  // story:
    ScriptEntry Story_NI_CrossBlueE   // 10: (unused since the layouts exist)  // story:
    ScriptEntry Story_NI_CrossBlueW   // 11: (unused)  // story:
    ScriptEntry Story_NI_CrossGreenE   // 12: (unused)  // story:
    ScriptEntry Story_NI_CrossGreenW   // 13: (unused)  // story:
    ScriptEntry NI_FadeIn   // 14: after Sub_NI_Redraw's map change (fixups2)  // story:
    ScriptEntriesEnd

Script_None:
    VMHalt
    .balign 4, 0

// ---- story (chapter Ch6, ch6 agent: Sapphire data/maps/NewMauville_Inside/scripts.inc; generators keep everything
// from this line on). Objects (data/story/ch6.json): the three Voltorbs (Sapphire draws them as item balls: uid 6-8),
// the switch triggers, the generator signs. Text: src/text/script/0152_room_NewMauville_Inside.txt lines 0-2.
// THE BARRIERS: Sapphire swaps metatiles (blue switch: the blue barriers down and the green ones up; green switch:
// the reverse) and their collision with them. Black 2 maps are baked models with baked collision, so the room has three
// layouts (b2tools/caves_misc_newmauville.py; fixups2 2026-10-07): NewMauville_Inside = Sapphire's map (every barrier up),
// NewMauville_Inside_BlueDown (blue lowered, green up: Sapphire's EventScript_15E5DA) and NewMauville_Inside_GreenDown
// (EventScript_15E728). data/interiors/133.json "alt_rooms" loads the second or third matrix instead of the first while
// map replace event 5 / 6 is set (works 0x4036 / 0x4037: data/story_ids.json WORK_MAP_REPLACE_5/6). Black 2 draws a
// swapped matrix only on a map change, so a switch ends with a fade and a map change to the player's own tile
// (Sub_NI_Redraw, like the Mauville Gym's Sub_MG_Redraw). Sapphire's VAR_TEMP_1/2 (wiped by every map change here) are
// the two event works themselves: a switch's step trigger fires while its colour is not down (data/story/ch6.json
// "var" 0x4036 / 0x4037, value 0). Sapphire's OnTransition clears them on every entry: the zone init resets the events,
// except after a switch's own map change (FLAG_NEW_MAUVILLE_REDRAW). The buttons' pressed/unpressed pictures are not
// drawn (the electric floor on the passage tiles is the barrier).
#define NM_EVENT_BLUE_DOWN 5            /* map replace event 5 (work 0x4036 == 0x1227): blue barriers lowered, green up */
#define NM_EVENT_GREEN_DOWN 6           /* map replace event 6 (work 0x4037 == 0x830): green lowered, blue up */
#define NI_X 0x8051                     /* scratch works of Sub_NI_Redraw */
#define NI_Z 0x8052
#define NI_DIR 0x8053
Story_NI_Init:                              // NewMauville_Inside OnTransition (VAR_TEMP_1/2 = 0: both colours up)
#if defined(HOENN_TEST_CH6) || defined(HOENN_TEST_CH12)
    VMCall Test_Ch6Start                    // test builds only (scenes/ch6_test.inc)
#endif
    h_goto_if_set FLAG_NEW_MAUVILLE_REDRAW, L_NI_Redrawn
    MapReplaceSetEvent NM_EVENT_BLUE_DOWN, 0, 0      // a normal entry: every barrier up again; the second call reloads
    MapReplaceSetEvent NM_EVENT_GREEN_DOWN, 0, 1     // the matrix (the zone's is already loaded when its init runs)
    VMHalt
L_NI_Redrawn:                               // the map change of a switch (Sub_NI_Redraw): keep the layout it chose
    h_clearflag FLAG_NEW_MAUVILLE_REDRAW
    VMHalt

Story_NI_BlueSwitch:                        // NewMauville_Inside_EventScript_15E5AA
    h_lock
    h_playse SEQ_SE_DECIDE1                 // SE_PIN [guess]
    MapReplaceSetEvent NM_EVENT_GREEN_DOWN, 0, 0
    MapReplaceSetEvent NM_EVENT_BLUE_DOWN, 1, 0
    VMCall Sub_NI_Redraw
    h_release

Story_NI_GreenSwitch:                       // NewMauville_Inside_EventScript_15E5C2
    h_lock
    h_playse SEQ_SE_DECIDE1                 // SE_PIN [guess]
    MapReplaceSetEvent NM_EVENT_BLUE_DOWN, 0, 0
    MapReplaceSetEvent NM_EVENT_GREEN_DOWN, 1, 0
    VMCall Sub_NI_Redraw
    h_release

Story_NI_GeneratorSwitch:                   // NewMauville_Inside_EventScript_15E876
    h_lock
    h_buffer_player
    h_msgbox_info 2                         // <player> stepped on the switch. Click... ... The generator appears to have stopped...
    h_closemessage
    h_setvar VAR_NEW_MAUVILLE_STATE, 2
    h_release

Story_NI_Generator:                         // NewMauville_Inside_EventScript_15E8E0
    h_lock
    SEPlay SEQ_SE_MESSAGE
    h_goto_if_eq VAR_NEW_MAUVILLE_STATE, 2, L_NI_Quiet
    h_msgbox_info 0                         // The generator is radiating heat ...
    h_closemessage
    h_release
L_NI_Quiet:
    h_msgbox_info 1                         // The generator quieted down.
    h_closemessage
    h_release

#define NI_VOLTORB_LEVEL 26                     // Sapphire/Ruby/Emerald 25 on the scaled curve (data/level_scaling.json;
                                                //   user decision 2026-10-19: the static battles follow the curve)
    .macro ni_voltorb flag, uid             // NewMauville_Inside_EventScript_15E900 / 15E91E / 15E93C
    h_lock
    h_faceplayer
    h_playmoncry SPECIES_VOLTORB
    h_delay 40
    h_waitmoncry
    h_static_battle SPECIES_VOLTORB, NI_VOLTORB_LEVEL, \flag, \uid   // setwildbattle VOLTORB 25 + dowildbattle; gone afterwards
    h_release
    .endm
Story_NI_Voltorb1:
    ni_voltorb FLAG_HIDE_VOLTORB_1_NEW_MAUVILLE, 6
Story_NI_Voltorb2:
    ni_voltorb FLAG_HIDE_VOLTORB_2_NEW_MAUVILLE, 7
Story_NI_Voltorb3:
    ni_voltorb FLAG_HIDE_VOLTORB_3_NEW_MAUVILLE, 8
    .balign 4, 0

// ---- the redraw after a switch (fixups2 2026-10-07) ------------------------------------------------------------------
// Black 2 shows a map-replace matrix only after a map change, and MapChangeCore takes constants only: fade out, then a
// map change to the player's own tile and facing (the switch's tile, zone tile = Sapphire tile + (12,12)); the reserved
// NI_FadeIn (script 14) fades the screen back in once the zone init has run (it keeps the layout: FLAG_NEW_MAUVILLE_REDRAW).
// Tiles: blue switches (6,11) (13,10) (16,22) (4,26) (30,38), green switches (2,11) (17,10) (25,18) (18,36).
    .macro NI_WARP_HERE x, z            // facing from NI_DIR (0 up, 1 down, 2 left, 3 right)
    RTReserveScript 14
    h_goto_if_ne NI_DIR, 0, .Lnw1\@
    MapChangeCore 133, \x, 0, \z, 0
    VMReturn
.Lnw1\@:
    h_goto_if_ne NI_DIR, 1, .Lnw2\@
    MapChangeCore 133, \x, 0, \z, 1
    VMReturn
.Lnw2\@:
    h_goto_if_ne NI_DIR, 2, .Lnw3\@
    MapChangeCore 133, \x, 0, \z, 2
    VMReturn
.Lnw3\@:
    MapChangeCore 133, \x, 0, \z, 3
    VMReturn
    .endm
    .macro NI_IF_AT x, z, label
    WorkCmpConst NI_X, \x
    VMJumpIf CMP_NE, .Lni\@
    h_goto_if_eq NI_Z, \z, \label
.Lni\@:
    .endm

NI_FadeIn:                                  // 14: reserved by Sub_NI_Redraw
    FadeInBlack
    FadeWait
    VMHalt

Sub_NI_Redraw:
    PlayerGetGPos NI_X, NI_Z
    PlayerGetDir NI_DIR
    FlagSet FLAG_NEW_MAUVILLE_REDRAW
    FadeOutBlack
    FadeWait
    NI_IF_AT 18, 23, L_NI_At_6_11
    NI_IF_AT 25, 22, L_NI_At_13_10
    NI_IF_AT 28, 34, L_NI_At_16_22
    NI_IF_AT 16, 38, L_NI_At_4_26
    NI_IF_AT 42, 50, L_NI_At_30_38
    NI_IF_AT 14, 23, L_NI_At_2_11
    NI_IF_AT 29, 22, L_NI_At_17_10
    NI_IF_AT 37, 30, L_NI_At_25_18
    NI_IF_AT 30, 48, L_NI_At_18_36
    FlagReset FLAG_NEW_MAUVILLE_REDRAW     // elsewhere (cannot happen): the new layout shows on the next visit
    FadeInBlack
    FadeWait
    VMReturn
L_NI_At_6_11:
    NI_WARP_HERE 18, 23
L_NI_At_13_10:
    NI_WARP_HERE 25, 22
L_NI_At_16_22:
    NI_WARP_HERE 28, 34
L_NI_At_4_26:
    NI_WARP_HERE 16, 38
L_NI_At_30_38:
    NI_WARP_HERE 42, 50
L_NI_At_2_11:
    NI_WARP_HERE 14, 23
L_NI_At_17_10:
    NI_WARP_HERE 29, 22
L_NI_At_25_18:
    NI_WARP_HERE 37, 30
L_NI_At_18_36:
    NI_WARP_HERE 30, 48

// Scripts 10-13 were the stand-in that walked you through a lowered barrier (before the layouts existed): the triggers
// are gone from data/story/ch6.json; the entries stay so that the numbers do not move.
Story_NI_CrossBlueE:
Story_NI_CrossBlueW:
Story_NI_CrossGreenE:
Story_NI_CrossGreenW:
    VMHalt
    .balign 4, 0
#include "scenes/ch6_test.inc"
