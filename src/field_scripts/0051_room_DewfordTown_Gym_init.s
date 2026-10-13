// Map scripts of DewfordTown_Gym (zone 25; Sapphire DewfordTown_Gym_OnTransition = SetFlashLevel): every field load
// (MapScript 4 after a warp, 3 back from a battle or a menu; the field exists then and the screen is still dark) =
// script 4 of 0050_room_DewfordTown_Gym.s (the darkness circle; a zone init runs before the field). ---- story
// b2tools/patches/interiors.py installs this table.
#include "asm/field_script.inc"
#include "hoenn.h"

    MapScript 3, 4
    MapScript 4, 4
    MapScriptsEnd
    .balign 4, 0
