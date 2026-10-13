// Route 111's map scripts (Sapphire Route111_MapScripts: ON_TRANSITION; its ON_LOAD = the Desert Ruins wall, Ch12's
// room, not built): zone init = story script 1 (scenes/Route111.inc R111_Init). ch4, 2026-10-07.
    MapScript 2, 1
#ifdef HOENN_EMERALD
    MapScriptConditions R111_Conditions     // Emerald: the Mirage Tower's collapse scene (emerald_ch9_mirage, scenes/emerald/Route111_Mirage.inc)
#endif
    MapScriptsEnd
#ifdef HOENN_EMERALD
R111_Conditions:
    MapScriptCondition VAR_MIRAGE_TOWER_STATE, 1, 15
    MapScriptConditionsEnd
    .balign 4, 0
#endif
