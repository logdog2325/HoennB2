// Map scripts of MossdeepCity_GameCorner_1F (zone 277; installed by b2tools/patches/interiors.py), chapter Ch9: Sapphire
// ON_LOAD / ON_TRANSITION without an e-Reader trainer = zone init = script 4 of 0554_room_MossdeepCity_GameCorner_1F.s (the
// doorway to the basement stays closed). ON_FRAME VAR_GAME_CORNER_STATE 1-3 (back from the e-Reader match) is not built.
#include "asm/field_script.inc"
#include "hoenn.h"

    MapScript 2, 4
    MapScriptsEnd
    .balign 4, 0
