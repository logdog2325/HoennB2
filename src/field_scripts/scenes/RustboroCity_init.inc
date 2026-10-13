// Rustboro City's map scripts (Sapphire RustboroCity_MapScripts): zone init = story script 1 (scenes/RustboroCity.inc).
    MapScript 2, 1
#ifdef HOENN_TEST_CH2
    MapScriptConditions RB_TestConditions   // test builds only: Ch1's end state (script 24) on arriving
#endif
    MapScriptsEnd
#ifdef HOENN_TEST_CH2
RB_TestConditions:
    MapScriptCondition VAR_RUSTBORO_STATE, 0, 24
    MapScriptConditionsEnd
#endif
