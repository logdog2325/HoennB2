// The Safari Zone's south-west area (Sapphire data/maps/SafariZone_Southwest/scripts.inc; chapter Ch8 part 8b, ch8b
// agent 2026-10-07). Script 1 below; the generated rest-house sign and item ball follow. The woman at (22,9) (uid 101)
// says a line with the {POKEBLOCK} text code, which converter/gen_map_content.py cannot write, so she is here.
// Text: src/text/scenes/SafariZone_Southwest.txt.
#ifdef SCENE_ENTRIES
    ScriptEntry SZSW_Woman              // 1: object 1 (EventScript_160024)
#else
#define T_WomanBlock 0

SZSW_Woman:
    h_msgbox_npc T_WomanBlock
#endif
