// Map scripts of LilycoveCity_DepartmentStoreElevator (discord_fixes 2026-11-10): script 3 of
// 0362_room_LilycoveCity_DepartmentStoreElevator.s (EL_Init) points the exit's dynamic warp back at the floor the player
// got on at (Gen 3's SetupWarp does it on the warp in; Black 2's arrival never does). As the zone init (MapScript 2: every
// warp in) and at a field load without a map change (MapScript 3: Continue, back from a battle or a menu), so a save
// made in here by an older version (its next zone still Black City's or the last ride's) leads out right too: a normal
// Continue runs no zone init (ov035 EventFieldContinue_Callback). b2tools/patches/interiors.py installs this table.
#include "asm/field_script.inc"
#include "hoenn.h"

    MapScript 2, 3
    MapScript 3, 3
    MapScriptsEnd
    .balign 4, 0
