// Route114_FossilManiacsTunnel (zone 558): Sapphire's simple people and signs (as converter/gen_interiors.py makes them),
// plus people that turn back after their message (Common_Movement_FaceOriginalDirection), by the specials agent
// (b2tools/specials.py people). Messages: src/text/script/0359_room_Route114_FossilManiacsTunnel.txt
#include "asm/field_script.inc"
#include "hoenn.h"  // ch4
#include "hoenn_trainers.h"  // ch4
#include "hoenn_story.inc"  // ch4
#include "scenes/ch4_lib.inc"  // ch4

    ScriptEntry Script_None
    ScriptEntry FMT_FossilManiac        // 2: object 1 (Route114_FossilManiacsTunnel_EventScript_15C20F)  // story:
    ScriptEntriesEnd

Script_None:
    VMHalt
    .balign 4, 0

// ---- story (chapter Ch4, ch4 agent 2026-10-07: Sapphire data/maps/Route114_FossilManiacsTunnel/scripts.inc; generators keep
// everything from this line on; entries above marked "// story:"). The Fossil Maniac: data/story/ch4.json uid 1.
// Text lines 1-3 (line 0 is the generator's placeholder).
#define T_NoneForYou 1          // Route114_FossilManiacsTunnel_Text_192795
#define T_FoundFossil 2         // Route114_FossilManiacsTunnel_Text_1928DE
#define T_Dreamy 3              // Route114_FossilManiacsTunnel_Text_1929DC

FMT_FossilManiac:
    c4_talk
    h_goto_if_set FLAG_RECEIVED_FOSSIL_MON, L_FMT_Dreamy
    h_checkitem ITEM_ROOT_FOSSIL, 1, C4_TMP
    h_goto_if_eq C4_TMP, 1, L_FMT_Found
    h_checkitem ITEM_CLAW_FOSSIL, 1, C4_TMP
    h_goto_if_eq C4_TMP, 1, L_FMT_Found
    h_msgbox T_NoneForYou
    h_release
L_FMT_Found:
    h_msgbox T_FoundFossil
    h_release
L_FMT_Dreamy:
    h_msgbox T_Dreamy
    h_release
    .balign 4, 0
