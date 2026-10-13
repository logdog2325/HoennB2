// Route 113's story (Sapphire data/maps/Route113/scripts.inc; chapter Ch4, ch4 agent 2026-10-07). Script 1 of the
// zone's generated script file (zone 378). The buried trainers Lao and Lung (MOVEMENT_TYPE_HIDDEN: they jump out of the
// ash) are placed as plain eye-contact trainers (data/story/ch4.json, sight 1; Black 2 has no buried trainers).
// Ash for the Glass Workshop (Sapphire: the C engine adds 1 to VAR_ASH_GATHER_COUNT for each step on ash-covered grass
// while the Soot Sack is in the Bag, max 9999; Route113 ON_RESUME setstepcallback 1): Black 2 has no step hook a script
// can use, so 14 step-trigger columns cross the ashen part of the route (Sapphire x 20, 25 ... 85, the whole height),
// each worth 5 steps of ash (about one ash per step when crossing the route). The ash weather is the zone's.
#ifdef SCENE_ENTRIES
    ScriptEntry R113_Ash                    // 1: triggers (x,0) w1 h20 (the Soot Sack's ash)
#else
#include "scenes/ch4_lib.inc"
R113_Ash:
    h_checkitem ITEM_SOOT_SACK, 1, C4_TMP
    h_goto_if_eq C4_TMP, 0, L_R113_AshDone
    h_goto_if_ge VAR_ASH_GATHER_COUNT, 9995, L_R113_AshFull
    h_addvar VAR_ASH_GATHER_COUNT, 5
    VMHalt
L_R113_AshFull:
    h_setvar VAR_ASH_GATHER_COUNT, 9999
L_R113_AshDone:
    VMHalt
    .balign 4, 0
#endif
