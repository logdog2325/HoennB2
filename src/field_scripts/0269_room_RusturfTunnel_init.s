// RusturfTunnel's map scripts (Sapphire RusturfTunnel_MapScripts; chapter Ch2): zone init = script 8, every field
// load and return = script 1 (the OnTransition positions of the grunt and Peeko) of 0268_room_RusturfTunnel.s.
// Chapter Ch3 adds its OnFrame table through scenes/RusturfTunnel_Ch3_init.inc. b2tools/patches/interiors.py
// installs this table.
#include "asm/field_script.inc"
#include "hoenn.h"

    MapScript 2, 8
    MapScript 3, 1
    MapScript 4, 1
#include "scenes/RusturfTunnel_Ch3_init.inc"
    MapScriptsEnd
#define RT_CH3_TABLES
#include "scenes/RusturfTunnel_Ch3_init.inc"
    .balign 4, 0
