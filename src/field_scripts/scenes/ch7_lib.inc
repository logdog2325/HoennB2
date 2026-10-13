// Chapter 7 helpers (ch7 agent, 2026-10-07): Routes 118-120, the Weather Institute, Fortree. Macros only (no code
// until used); the code labels at the end are assembled once per file (include guard). Include after
// "hoenn_story.inc" in the BODY part of a scene file (or after the ScriptEntry table of a room file).
#ifndef CH7_LIB_INC
#define CH7_LIB_INC
#include "hoenn_key_items.h"            // ITEM_DEVON_SCOPE (= Black 2's Poké Radar, renamed: converter/gen_key_items.py)

// script works of these helpers (HLIB_* 0x8030/31, ch3 0x8032-36, ch4 0x8037-39)
#define C7_TMP 0x803A
#define C7_TMP2 0x803B
#define C7_POS 0x803C                   // Sapphire VAR_0x8008 / VAR_TEMP_1 of the trigger scenes (which tile)
#define C7_SEL 0x803D
// map-local work (Black 2 clears 0x4000-0x401F at every zone init, as Sapphire's VAR_TEMP_*): 0 = the invisible
// Kecleons of this zone still have to be hidden (the zone's MapScriptConditions run c7's hide script, which sets it 1)
#define C7_KECLEON_HIDDEN 0x4010

// Common_EventScript_SetupRivalOnBikeGfxId with the bike sprites the sprites agents drew (src/sprites/overworld
// 002-rival-brendan-bike, 005-rival-may-bike): an NPC with model 165 (WKOBJCODE 3) shows the object code in work
// 0x4023 (GetWKOBJCODENPCOBJCODE, as model 162 reads 0x4020): boy -> May on her bike (5), girl -> Brendan (2).
#define RIVAL_BIKE_GFX 165
    .macro c7_setup_rival_bike_gfx
    TrainerCardGetSex HLIB_TMP
    WorkSetConst 0x4023, 5
    WorkCmpConst HLIB_TMP, 0
    VMJumpIf CMP_EQ, .Lc7rb\@
    WorkSetConst 0x4023, 2
.Lc7rb\@:
    .endm

// lock + faceplayer of a talked-to person (Black 2's NPC script start)
    .macro c7_talk
    ActorsPauseAll
    WordSetPlayerName 0                 // ({0100:0} in the lines)
    SEPlay SEQ_SE_MESSAGE
    ActorSetEyeToEye
    .endm

// a Pokémon that cries and says its line (lock, faceplayer, waitse, playmoncry, msgbox, waitmoncry, release)
    .macro c7_mon_cry species, n
    c7_talk
    h_playmoncry \species
    h_msgbox \n
    h_waitmoncry
    h_release
    .endm

// giveitem VAR_0x8004 (the item id in a work): HLIB_RESULT 1 given, 0 no room (h_giveitem takes a constant only)
    .macro c7_giveitem_var var
    ItemCheckSpace \var, 1, HLIB_RESULT
    WorkCmpConst HLIB_RESULT, 0
    VMJumpIf CMP_EQ, .Lc7giv\@
    VMStackPush 0x8000
    VMStackPush 0x8001
    WorkSet 0x8000, \var
    WorkSetConst 0x8001, 1
    RTCallGlobal 2805
    VMStackPop 0x8001
    VMStackPop 0x8000
.Lc7giv\@:
    .endm

// ---- the invisible Kecleons (Sapphire MOVEMENT_TYPE_INVISIBLE, data/scripts/static_pokemon.inc) -------------------
// Black 2 has no invisible movement type and no map-script command that hides an actor at load (ActorCmdExec is
// allowed at feature level 0 only: ov012 EVCMD_PERM_TABLE). So each zone with Kecleons lists a scene condition
// (MapScriptConditions: C7_KECLEON_HIDDEN == 0 -> its hide script) that runs once the field is up after every zone
// entry, and resets C7_KECLEON_HIDDEN to 0 in its field load / return scripts (MapScript 3/4, after battles and
// menus) so the Kecleons are hidden again whenever the field is rebuilt. Hiding = movement action 69 (set_invisible:
// ov036 action 69 -> SetActorFlag(actor, 4), the flag Black 2's own map change uses to hide the player).
// The place-name banner: Black 2 closes it as soon as the field starts any script, so the zone init sets h_keep_banner
// and the hide script clears it first (h_keep_banner_end, src/include/hoenn_story.inc; fixes_v151 2026-10-08).
    .macro c7_hide_kecleon uid, flag    // in the hide script: hide this Kecleon if it is still there
    h_goto_if_set \flag, .Lc7hk\@
    ActorCmdExec \uid, Mv_C7_Invisible
.Lc7hk\@:
    .endm

// EventScript_Kecleon (talked to): "Something unseeable is in the way." / with the Devon Scope: use it, the Kecleon
// shows itself (Movement_KecleonAppears), cries and attacks (a Lv 30 wild battle; it is gone afterwards whatever
// happened: FLAG_SYS_CTRL_OBJ_DELETE + the hide flag = h_static_battle). tunseen / task / tused = the zone's lines
// Text_SomethingUnseeable, Text_WantToUseDevonScope, Text_UseDevonScopeMonAttacked.
    .macro c7_kecleon uid, flag, tunseen, task, tused
    c7_talk
    h_checkitem ITEM_DEVON_SCOPE, 1, C7_TMP     // (nobody says these lines: info windows, not a balloon from the
    h_goto_if_eq C7_TMP, 1, .Lc7kscope\@       // invisible Kecleon)
    h_msgbox \tunseen                           // (the line comes out of the invisible Kecleon's balloon)
    h_release
.Lc7kscope\@:
    h_yesno \task, C7_TMP
    h_goto_if_yes C7_TMP, .Lc7kuse\@
    h_release
.Lc7kuse\@:
    h_buffer_player
    h_msgbox \tused
    h_closemessage
    h_applymovement \uid, Mv_C7_KecleonAppears    // (Common_Movement_FacePlayer: it faces the player already)
    h_waitmovement
    h_playmoncry SPECIES_KECLEON               // waitse, playmoncry SPECIES_KECLEON, 2, delay 40, waitmoncry
    h_delay 40
    h_waitmoncry
    h_static_battle SPECIES_KECLEON, 30, \flag, \uid
    h_release
    .endm

// Steven's exit (Sapphire setfieldeffectargument 0, 1 + dofieldeffect FLDEFF_NPCFLY_OUT: he calls a bird Pokémon and
// flies off): Black 2's "Alder flies off" cut-in (ov036 s019D_PlayAlderFlyEffect, FieldCommand 413), ch8a's
// c8_npc_fly_out pattern (the uid through a work). Black 2 skips the cut-in when the field heap has under 0xa478 free:
// it did on Route 120 in v14/v15 (story_finish), so this was a fade; since the save fix (ed03393, map type 0 field
// heap +80 KB) it plays there (fixes_v151, 2026-10-08, tested). The cut-in is Black 2's fixed Alder animation (his
// sprite on a Braviary at the screen centre, Steven and the player hidden meanwhile), as for ch8a's rival in Lilycove.
    .macro c7_npc_fly_out uid, flag
    FadeOutBlack                        // Black 2's only NPC fly-off (ov036 s019D) is its fixed "Alder flies off" cut-in:
    FadeWait                            // the red-haired Alder rides a Braviary across the screen (fixes_v151 test), an
    h_removeobject \uid, \flag           // Unova character in a Hoenn scene, so the leaver fades out instead (lead,
    FadeInBlack                         // 2026-10-08)
    FadeWait
    .endm

// ---- shared code and movement lists (once per file) --------------------------------------------------------------
    VMJump .Lc7_lib_end
    .balign 4, 0
Mv_C7_Invisible:
    set_invisible
    step_end
Mv_C7_KecleonAppears:                   // Movement_KecleonAppears
    set_visible
    delay_4
    set_invisible
    delay_4
    set_visible
    delay_4
    set_invisible
    delay_4
    set_visible
    delay_8
    set_invisible
    delay_8
    set_visible
    delay_8
    set_invisible
    delay_8
    set_visible
    delay_16
    set_invisible
    delay_16
    set_visible
    step_end
.Lc7_lib_end:
#endif
