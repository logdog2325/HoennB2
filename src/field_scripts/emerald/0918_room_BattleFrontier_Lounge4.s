// BattleFrontier_Lounge4 (zone 459; header scripts 918 -> its own file), Pokémon Emerald NDS only (frontier_sp,
// 2026-10-20). pokeemerald data/maps/BattleFrontier_Lounge4/scripts.inc: three people with one line each (MSGBOX_NPC). The room:
// data/interior_layouts/BattleFrontier_Lounge4.json, people data/interiors/emerald/459.json (uid = script = Emerald's local id).
// Messages: src/text/script/emerald/0659_room_BattleFrontier_Lounge4.txt (pokeemerald's words, converter/gen3text.py).
// Written by work/agents/frontier_sp/tools/frontier_rooms.py.
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_story.inc"

    ScriptEntry Script_1                   // 1: BattleFrontier_Lounge4_EventScript_Woman
    ScriptEntry Script_2                   // 2: BattleFrontier_Lounge4_EventScript_Cook
    ScriptEntry Script_3                   // 3: BattleFrontier_Lounge4_EventScript_Man
    ScriptEntriesEnd

Script_1:                               // WOMAN_3 (4,4): WonderIfInterviewsAiring
    h_msgbox_npc 0

Script_2:                               // COOK (6,6): IfIOpenedRestaurantHere
    h_msgbox_npc 1

Script_3:                               // MAN_3 (0,5): NeedBreatherAfterBattles
    h_msgbox_npc 2

    .balign 4, 0
