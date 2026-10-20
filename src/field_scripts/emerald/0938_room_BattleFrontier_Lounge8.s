// BattleFrontier_Lounge8 (zone 469; header scripts 938 -> its own file), Pokémon Emerald NDS only (frontier_sp,
// 2026-10-20). pokeemerald data/maps/BattleFrontier_Lounge8/scripts.inc: three people with one line each (MSGBOX_NPC). The room:
// data/interior_layouts/BattleFrontier_Lounge8.json, people data/interiors/emerald/469.json (uid = script = Emerald's local id).
// Messages: src/text/script/emerald/0195_room_BattleFrontier_Lounge8.txt (pokeemerald's words, converter/gen3text.py).
// Written by work/agents/frontier_sp/tools/frontier_rooms.py.
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_story.inc"

    ScriptEntry Script_1                   // 1: BattleFrontier_Lounge8_EventScript_NinjaBoy
    ScriptEntry Script_2                   // 2: BattleFrontier_Lounge8_EventScript_Man
    ScriptEntry Script_3                   // 3: BattleFrontier_Lounge8_EventScript_Woman
    ScriptEntriesEnd

Script_1:                               // NINJA_BOY (4,5): ToldMeIHaveTalentForBattling
    h_msgbox_npc 0

Script_2:                               // MAN_3 (8,7): WhatATrainerNeeds
    h_msgbox_npc 1

Script_3:                               // WOMAN_5 (8,4): KnowAboutFrontierBrains
    h_msgbox_npc 2

    .balign 4, 0
