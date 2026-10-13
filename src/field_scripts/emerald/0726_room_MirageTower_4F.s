// MirageTower_4F (zone 363, Emerald): converter/gen_caves_emerald.py from emerald/MirageTower_4F (emerald_caves): ladders and
// cracked floors as step triggers, simple people/signs. Story scripts: add them after a line "// ---- story" (this
// generator keeps everything from that line on and the entries you add: b2tools/story_merge.py) and number them
// after these entries.
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_key_items.h"  // emerald_ch9_mirage
#include "hoenn_story.inc"  // emerald_ch9_mirage

    ScriptEntry Script_1
    ScriptEntry MT4_RootFossil  // 2: object 1, the Root Fossil (MirageTower_4F_EventScript_RootFossil)  // story:
    ScriptEntry MT4_ClawFossil  // 3: object 2, the Claw Fossil  // story:
    ScriptEntriesEnd

Script_1:                                      // ladder down (1,4) -> MirageTower_3F warp 1 (2,4)
    ActorsPauseAll
    SEPlay SEQ_SE_KAIDAN
    FadeOutBlack
    RTReserveScript 10017
    FadeWait
    MapChangeCore 362, 2, 0, 4, 1
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt
    .balign 4, 0

// ---- story (builder B6 emerald_ch9_mirage 2026-10-12; pokeemerald data/maps/MirageTower_4F/scripts.inc; generators keep everything from this line on; entries
// above marked "// story:"). Text: src/text/script/emerald/0575_room_MirageTower_4F.txt (converter/gen_emerald_ch9_text.py): 0 take the Root Fossil?, 1 left it,
// 2 take the Claw Fossil?, 3 left it, 4 bag full. People: the two fossils (data/story/emerald/e_ch9_mirage.json uids 1 and 2, hidden by FLAG_HIDE_MIRAGE_TOWER_*_FOSSIL;
// the breakable rock is the zone's own, uid 3).
// You may take one: the other is gone (both hide flags set, FLAG_CHOSE_*_FOSSIL says which you took) and the tower collapses: the camera shakes, VAR_MIRAGE_TOWER_STATE
// 1, and you are put at the tower's foot on Route 111 where the rest happens (scenes/emerald/Route111_Mirage.inc). The unchosen fossil waits in the Desert
// Underpass (0750). pokeemerald gives the fossil without looking at the bag; a full bag here leaves the fossil and the tower alone.
// Black 2 gaps: special DoMirageTowerCeilingCrumble (the falling pieces over the screen) is the camera shake only.
#define T_TakeRoot 0
#define T_LeftRoot 1
#define T_TakeClaw 2
#define T_LeftClaw 3
#define T_BagFull 4
#define MT4_ROOT 1                      // uids
#define MT4_CLAW 2
#define MT4_SE_SHAKE SEQ_SE_FLD_126     // [guess] Black 2's ground rumble (Jagged Pass, the Sealed Chamber)
#define MT4_R111_ZONE 370               // Route 111 (data/interiors/emerald/360.json: the tower's door leads to zone 370)

    .macro mt4_talk
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    ActorSetEyeToEye
    .endm

MT4_RootFossil:                         // MirageTower_4F_EventScript_RootFossil (lock, faceplayer)
    mt4_talk
    h_yesno T_TakeRoot, HLIB_TMP        // You found the Root Fossil. If this Fossil is taken, the ground around it will likely crumble away... Take the Root Fossil anyway?
    h_goto_if_no HLIB_TMP, L_MT4_LeaveRoot
    h_closemessage                      // (Black 2: the item script opens its own window)
    h_giveitem ITEM_ROOT_FOSSIL
    h_goto_if_eq HLIB_RESULT, 0, L_MT4_BagFull
    h_closemessage
    h_setflag FLAG_HIDE_MIRAGE_TOWER_ROOT_FOSSIL
    h_setflag FLAG_HIDE_MIRAGE_TOWER_CLAW_FOSSIL
    h_removeobject MT4_ROOT, FLAG_HIDE_MIRAGE_TOWER_ROOT_FOSSIL
    h_delay 30
    h_setflag FLAG_CHOSE_ROOT_FOSSIL
    VMJump MT4_Collapse
L_MT4_LeaveRoot:                        // MirageTower_4F_EventScript_LeaveRootFossil
    h_msgbox T_LeftRoot                 // <player> left the Root Fossil alone.
    h_release

MT4_ClawFossil:                         // MirageTower_4F_EventScript_ClawFossil (lock, faceplayer)
    mt4_talk
    h_yesno T_TakeClaw, HLIB_TMP        // You found the Claw Fossil. If this Fossil is taken, the ground around it will likely crumble away... Take the Claw Fossil anyway?
    h_goto_if_no HLIB_TMP, L_MT4_LeaveClaw
    h_closemessage
    h_giveitem ITEM_CLAW_FOSSIL
    h_goto_if_eq HLIB_RESULT, 0, L_MT4_BagFull
    h_closemessage
    h_setflag FLAG_HIDE_MIRAGE_TOWER_CLAW_FOSSIL
    h_setflag FLAG_HIDE_MIRAGE_TOWER_ROOT_FOSSIL
    h_removeobject MT4_CLAW, FLAG_HIDE_MIRAGE_TOWER_CLAW_FOSSIL
    h_delay 30
    h_setflag FLAG_CHOSE_CLAW_FOSSIL
    VMJump MT4_Collapse
L_MT4_LeaveClaw:                        // MirageTower_4F_EventScript_LeaveClawFossil
    h_msgbox T_LeftClaw                 // <player> left the Claw Fossil alone.
    h_release

L_MT4_BagFull:                          // (not in pokeemerald: see above)
    h_bag_is_full T_BagFull
    h_release

MT4_Collapse:                           // MirageTower_4F_EventScript_CollapseMirageTower
    SEPlay MT4_SE_SHAKE
    EvCameraShake 4, 0, 3, 32, 1, 0, 1, 2   // setvar 8004 1 / 8005 1 / 8006 32 / 8007 2; special ShakeCamera (32 shakes, delay 2)
    VMSleep 40
    h_setvar VAR_MIRAGE_TOWER_STATE, 1  // (special DoMirageTowerCeilingCrumble: the camera shake only)
    h_warp_arrive MT4_R111_ZONE, 267, 119, 0, 2  // warp MAP_ROUTE111, 19, 59 (world tile = Route 111's origin (248,60) + (19,59); the desert is level 2 = 32 units)
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt
    .balign 4, 0
