// Route114_FossilManiacsTunnel (zone 558), Emerald build only (emerald_ch12_13, 2026-10-12): the Sapphire room's scripts
// (src/field_scripts/1116_room_Route114_FossilManiacsTunnel.s: the specials agent's head, ch4's Fossil Maniac) with Emerald's
// post-game: the Fossil Maniac moved aside and his warning at the Desert Underpass. Emerald's tunnel (emerald_caves' room
// variant Route114_FossilManiacsTunnel_Emerald, data/interiors/emerald/558.json: the north wall open after the game).
// Messages: src/text/script/emerald/0359_room_Route114_FossilManiacsTunnel.txt
#include "asm/field_script.inc"
#include "hoenn.h"  // ch4
#include "hoenn_trainers.h"  // ch4
#include "hoenn_story.inc"  // ch4
#include "scenes/ch4_lib.inc"  // ch4

    ScriptEntry Script_None
    ScriptEntry FMT_FossilManiac        // 2: object 1 (Route114_FossilManiacsTunnel_EventScript_FossilManiac)  // story:
    ScriptEntry FMT_MentionCaveIn       // 3: step trigger (5..6,4) while VAR_FOSSIL_MANIAC_STATE is 1  // story:
    ScriptEntry FMT_Init                // 4: zone init (1117: Route114_FossilManiacsTunnel_OnTransition)  // story:
    ScriptEntriesEnd

Script_None:
    VMHalt
    .balign 4, 0

// ---- story (chapter Ch4 (ch4 agent) + Emerald's post-game (B8 emerald_ch12_13); pokeemerald data/maps/
// Route114_FossilManiacsTunnel/scripts.inc; generators keep everything from this line on; entries above marked "// story:").
// The Fossil Maniac: data/story/ch4.json uid 1 at (5,3) facing up; after the game (Route114_FossilManiacsTunnel_OnTransition)
// at (6,5) facing down, beside the way into the Desert Underpass (its door: emerald_caves, open after the game). The
// Hall of Fame sets VAR_FOSSIL_MANIAC_STATE 1 (0114 HF_EmeraldFlags); the first step on (5,4) or (6,4) after it runs his
// warning (ManiacMentionCaveIn; data/story/emerald/e_ch13.json), state 2. Text lines 1-4 (line 0 is the generator's).
#define T_LookInDesertForFossils 1      // Route114_FossilManiacsTunnel_Text_LookInDesertForFossils
#define T_DevonCorpRevivingFossils 2    // Route114_FossilManiacsTunnel_Text_DevonCorpRevivingFossils
#define T_FossilsAreWonderful 3         // Route114_FossilManiacsTunnel_Text_FossilsAreWonderful
#define T_NotSafeThatWay 4              // Route114_FossilManiacsTunnel_Text_NotSafeThatWay
#define FMT_MANIAC 1                    // LOCALID_FOSSIL_MANIAC
#define FMT_MANIAC_INDEX 1              // his place in the zone's NPC list (ObjInitNPCGPos): the zone json's boulder, then him
#define FMT_OX 1                        // the room's origin (interiors/Route114_FossilManiacsTunnel*/room.json): (1, -1)
#define FMT_OZ (-1)

FMT_Init:                               // Route114_FossilManiacsTunnel_OnTransition: call_if_set FLAG_SYS_GAME_CLEAR, ..._MoveFossilManiac
    h_goto_if_unset FLAG_SYS_GAME_CLEAR, L_FMT_InitDone
    ObjInitNPCGPos FMT_MANIAC_INDEX, 1, 6 + FMT_OX, 0, 5 + FMT_OZ   // setobjectxyperm 6, 5; setobjectmovementtype FACE_DOWN
L_FMT_InitDone:
    VMHalt

FMT_MentionCaveIn:                      // Route114_FossilManiacsTunnel_EventScript_ManiacMentionCaveIn
    h_lock
    h_applymovement FMT_MANIAC, Mv_FMT_FaceUp      // Common_Movement_WalkInPlaceFasterUp
    h_applymovement 255, Mv_FMT_FaceDown           // Common_Movement_WalkInPlaceFasterDown
    h_waitmovement
    h_msgbox_actor T_NotSafeThatWay, FMT_MANIAC    // Oh... It's not safe that way... I think there's a giant cavern underneath now...
    h_setvar VAR_FOSSIL_MANIAC_STATE, 2
    h_release

FMT_FossilManiac:                       // Route114_FossilManiacsTunnel_EventScript_FossilManiac
    c4_talk
    h_goto_if_set FLAG_RECEIVED_FOSSIL_MON, L_FMT_Dreamy     // FLAG_RECEIVED_REVIVED_FOSSIL_MON
    h_checkitem ITEM_ROOT_FOSSIL, 1, C4_TMP
    h_goto_if_eq C4_TMP, 1, L_FMT_Found
    h_checkitem ITEM_CLAW_FOSSIL, 1, C4_TMP
    h_goto_if_eq C4_TMP, 1, L_FMT_Found
    h_msgbox T_LookInDesertForFossils
    h_release
L_FMT_Found:
    h_msgbox T_DevonCorpRevivingFossils
    h_release
L_FMT_Dreamy:
    h_msgbox T_FossilsAreWonderful
    h_release
    .balign 4, 0
Mv_FMT_FaceUp:
    walk_in_place_fast_up
    step_end
Mv_FMT_FaceDown:
    walk_in_place_fast_down
    step_end
