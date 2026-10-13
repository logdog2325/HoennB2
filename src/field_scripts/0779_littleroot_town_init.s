// Littleroot's map scripts (init file 0779; installed into the zone's entity file by b2tools/patches/hoenn_world.py).
// 2: zone init = script 9 (Nuvema's table had only this). (Until 2026-10-08 3/4 = script 23 hid the moving trucks,
// building res 460, with BMSetVisible on field load / return; a chunk reload showed them again, so they are 3D objects
// with Sapphire's hide flags now: data/story/missing_objects.json, b2tools/models_objects.py 'truck'.)
#include "asm/field_script.inc"
#include "hoenn.h"

    MapScript 2, 9
#if __has_include("scenes/LittlerootTown_ch13.inc") || __has_include("scenes/LittlerootTown_Postgame.inc")
    MapScriptConditions Conditions
#endif
    MapScriptsEnd

#if __has_include("scenes/LittlerootTown_ch13.inc") || __has_include("scenes/LittlerootTown_Postgame.inc")
Conditions:
#if __has_include("scenes/LittlerootTown_ch13.inc")
    MapScriptCondition VAR_LITTLEROOT_INTRO_STATE, 7, 25   // chapter Ch13: LittlerootTown_EventScript_BeginDexUpgradeScene
#endif
#if __has_include("scenes/LittlerootTown_Postgame.inc")
    MapScriptCondition VAR_DEX_UPGRADE_JOHTO_STARTER_STATE, 1, 26   // post-game: Emerald's BeginDexUpgradeScene (OnFrame)
#endif
    MapScriptConditionsEnd
#endif
    .balign 4, 0
