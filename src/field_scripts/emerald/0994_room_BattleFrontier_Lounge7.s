// BattleFrontier_Lounge7 (zone 497; header scripts 994 -> own file 2094), Pokémon Emerald NDS only (frontier_lounges,
// 2026-10-20). pokeemerald data/maps/BattleFrontier_Lounge7/scripts.inc: the two BP move tutors (frontier_core's
// fr_bp_tutor: Emerald's flow and prices, emerald_mech's tutor global; their "met" bits stay FR_TUTOR_MET), a sailor and
// a gentleman. The tutors stood in the Exchange Service Corner until now (frontier_core, 2026-10-12); they are back in
// Emerald's lounge, and the Exchange Corner keeps only its own people.
// The room: data/interior_layouts/BattleFrontier_Lounge7.json, people data/interiors/emerald/497.json (uid = script =
// Emerald's local id). Messages: src/text/script/emerald/0297_room_BattleFrontier_Lounge7.txt (lounge_rooms.py): 0-1 the
// sailor and the gentleman, 2-20 / 21-39 the left / right tutor's block (b2tools/frontier_text.py tutor 0|1).
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_story.inc"
#include "hoenn_emerald.inc"
#include "hoenn_frontier.inc"

#define T_TUTOR_LEFT 2
#define T_TUTOR_RIGHT 21

    ScriptEntry L7_Sailor               // 1: BattleFrontier_Lounge7_EventScript_Sailor
    ScriptEntry L7_LeftMoveTutor        // 2: _LeftMoveTutor (EXPERT_F (2,5)): Softboiled 16 ... Swords Dance 48 BP
    ScriptEntry L7_RightMoveTutor       // 3: _RightMoveTutor (EXPERT_F (6,5)): Defense Curl 16 ... Fire Punch 48 BP
    ScriptEntry L7_Gentleman            // 4: _Gentleman
    ScriptEntriesEnd

L7_Sailor:
    h_msgbox_npc 0

L7_LeftMoveTutor:
    fr_bp_tutor 0, T_TUTOR_LEFT

L7_RightMoveTutor:
    fr_bp_tutor 1, T_TUTOR_RIGHT

L7_Gentleman:
    h_msgbox_npc 1

    .balign 4, 0
