// BattleTower_BattleRoom (zone 15): Sapphire's Battle Room (data/maps/BattleTower_BattleRoom/scripts.inc; battle_tower
// agent, 2026-10-08, notes/BATTLE_TOWER.md). Reached only from the Corridor (its map change reserves script 1); the
// battles are Black 2's Battle Subway (plugin 1, b2tools/patches/battle_tower.py): the trainer of each of the seven
// battles was chosen at registration with Sapphire's rule, command 307 builds its party, 309 the battle. Messages:
// src/text/script/0021_room_BattleTower_BattleRoom.txt; the trainers' greetings are system text 376 (Black 2's balloon).
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_story.inc"
#include "scenes/battle_tower_lib.inc"
#ifdef HOENN_EMERALD
// Pokémon Emerald NDS (2026-10-18): the Salon Maiden Anabel, the Battle Tower's Frontier Brain, as pokeemerald
// (data/maps/BattleFrontier_BattleTowerBattleRoom/scripts.inc; src/frontier_util.c GetFrontierBrainStatus with
// sFrontierBrainStreakAppearances[TOWER] = {35, 70, 35, 1}): she replaces the opponent of the 35th battle of a streak
// (the Silver Symbol), then of the 70th (the Gold Symbol), and with both symbols of the 35th, the 70th and every 35th
// after it. The streak is Black 2's Subway streak (command 358), the battle frontier_palace_arena.c's (FrontierPA
// PA_TOWER_*: her parties, Emerald's sFrontierBrainsMons[TOWER]), her walking sprite and battle picture frontier_core's
// (notes/FRONTIER.md 5). Her lines: src/text/emerald/overrides_frontier_tower.json (b2tools/frontier_text.py tower_room)
#include "hoenn_emerald.inc"
#include "hoenn_frontier.inc"
#include "scenes/frontier_pa_lib.inc"
#include "frontier_tower_lines.h"
#define BTB_ANABEL_SPRITE 56            // OBJ_EVENT_GFX_ANABEL (data/emerald/sprite_map.json)
#define BTB_BRAIN BT_T4                 // her status for the next battle (FRONTIER_BRAIN_*: 0 not ready)
#endif

    ScriptEntry BTB_Enter               // 1: ON_FRAME_TABLE VAR_TEMP_0 0 (BattleTower_BattleRoom_EventScript_1608EB)
    ScriptEntry Script_None             // 2: the opponent and the attendant (Sapphire: no script)
    ScriptEntriesEnd

Script_None:
    VMHalt

// ---- story (battle_tower)
    .macro bt_room_say n                // msgbox by the attendant (object 2)
    ActorMsg MSGFILE_SCRIPT, \n, BT_ROOM_ATTENDANT, 0, 0
    LastKeyWait
    .endm
    .macro bt_room_yesno n, var
    ActorMsg MSGFILE_SCRIPT, \n, BT_ROOM_ATTENDANT, 0, 0
    YesNoWin \var
    .endm

BTB_Enter:                              // the player arrives at Sapphire (4,8)
    ActorsPauseAll
    FadeInBlack
    FadeWait
    h_applymovement BT_PLAYER, BTB_MvPlayerIn       // BattleTower_BattleRoom_Movement_160AB7
    h_waitmovement
L_BTB_Next:                             // 1608FA
#ifdef HOENN_EMERALD
    VMCall Sub_BTB_BrainStatus          // frontier_getbrainstatus: the Salon Maiden instead of a trainer?
    h_goto_if_ne BTB_BRAIN, 0, L_BTB_Anabel
#endif
    BSubwayCmd_Tool 307, 0, 0, 0        // ChooseNextBattleTowerTrainer (chosen at registration) + FillBattleTowerTrainerParty
    BSubwayCmd_Tool 308, 0, 0, BT_OPPONENT_GFX      // SetBattleTowerTrainerGfxId (its class's sprite: battle_tower.py)
    h_addobject BT_OPPONENT, FLAG_HIDE_BATTLE_TOWER_OPPONENT
    h_applymovement BT_OPPONENT, BTB_MvOppIn        // _160AC0
    h_waitmovement
    BSubwayCmd_Tool 352, 0, BT_OPPONENT, 0          // PrintBattleTowerTrainerGreeting + msgbox gStringVar4
    h_heal                              // ScrSpecial_HealPlayerParty
    BSubwayCmd_Tool 309, 0, 0, 0        // StartSpecialBattle
    BSubwayCmd_Tool 332, 0, 0, BT_T1    // 1 = won (switch VAR_RESULT, case 1)
    BSubwayCmd_Tool 347, 0, 0, 0        // (Black 2: the battle setup freed)
    h_goto_if_eq BT_T1, 1, L_BTB_Won
#ifdef HOENN_EMERALD
L_BTB_Lost:
#endif
    // lost: LoadPlayerParty, SetBattleTowerProperty 0 = 5, 14; sub_810FF60 (0x8004 = 3); warp to the lobby
    BSubwayCmd_Tool 304, 0, 0, 0        // Black 2: the streak ends here (its length kept, best, round 0)
    WorkCmpConst VAR_BT_LEVEL_TYPE, 0
    VMJumpIf CMP_NE, L_BTB_Lost100
    WorkSetConst VAR_BT_STATUS_LV50, BT_ST_LOST
    VMJump L_BTB_ToLobby
L_BTB_Lost100:
    WorkSetConst VAR_BT_STATUS_LV100, BT_ST_LOST
L_BTB_ToLobby:
    WorkSetConst 0x8004, 3
    VMCall Sub_FanClub_CountWin
    h_warp_arrive BT_LOBBY_ZONE, 6 + BT_LOBBY_OX, 6 + BT_LOBBY_OZ, 0     // warp MAP_BATTLE_TOWER_LOBBY, 255, 6, 6
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

L_BTB_Won:                              // 160961: SetBattleTowerProperty 6 (battle number + 1, SaveCurrentWinStreak)
    BSubwayCmd_Tool 357, 0, 0, BT_T2    // Black 2: round + 1, wins + 1 -> the streak
#if defined(HOENN_TEST_CHBT) && HOENN_TEST_CHBT == 2
    BSubwayCmd_Tool 8, 0, 0, BT_T3      // (test build: the first win of a challenge counts as six)
    h_goto_if_ne BT_T3, 2, L_BTB_TestDone
    BSubwayCmd_Tool 357, 0, 0, BT_T2
    BSubwayCmd_Tool 357, 0, 0, BT_T2
    BSubwayCmd_Tool 357, 0, 0, BT_T2
    BSubwayCmd_Tool 357, 0, 0, BT_T2
    BSubwayCmd_Tool 357, 0, 0, BT_T2
L_BTB_TestDone:
#endif
    VMCall Sub_BTB_SaveStreak
    BSubwayCmd_Tool 303, 0, 0, BT_T3    // seven won (VAR_RESULT 8)?
    h_goto_if_eq BT_T3, 1, L_BTB_Seven
    h_applymovement BT_OPPONENT, BTB_MvOppOut       // _160AC6
    h_waitmovement
    h_removeobject BT_OPPONENT, FLAG_HIDE_BATTLE_TOWER_OPPONENT
    h_applymovement BT_ROOM_ATTENDANT, BTB_MvAttIn  // _160ACB
    h_waitmovement
    h_applymovement BT_PLAYER, BTB_MvFaceDown       // _160ABC
    h_waitmovement
    bt_room_say 0                       // We will restore your Pokémon to full health.
    MEPlay MUS_HEAL                     // (LoadPlayerParty, SavePlayerParty, SetBattleTowerParty: Black 2's battles
    MEWait                              //  use a copy of the three, the party itself is never changed)
    h_heal
L_BTB_Ask:                              // 1609B2
#ifdef HOENN_EMERALD
    VMCall Sub_BTB_BrainStatus          // AskReadyForOpponent: frontier_getbrainstatus -> MaidenUpNext
    h_goto_if_ne BTB_BRAIN, 0, L_BTB_MaidenNext
#endif
    BSubwayCmd_Tool 8, 0, 0, BT_T1      // the next battle's number
    WordSetNumber 1, BT_T1, 1
    bt_room_yesno 1, BT_T2              // You will be facing opponent no. <n>. Are you ready?
    h_goto_if_yes BT_T2, L_BTB_Continue
    bt_room_yesno 2, BT_T2              // Would you like to save and quit the game?
    h_goto_if_yes BT_T2, L_BTB_Rest
    bt_room_yesno 3, BT_T2              // Would you like to cancel your Battle Room challenge?
    h_goto_if_yes BT_T2, L_BTB_Retire
    VMJump L_BTB_Ask
L_BTB_Continue:                         // 160A3C
    h_closemessage
    h_applymovement BT_PLAYER, BTB_MvFaceRight      // _160ABE
    h_waitmovement
    h_applymovement BT_ROOM_ATTENDANT, BTB_MvAttOut // _160AD0
    h_waitmovement
    VMJump L_BTB_Next

L_BTB_Rest:                             // 160A94: SaveBattleTowerProgress 2, "SAVING...", the save, soft reset
    WorkCmpConst VAR_BT_LEVEL_TYPE, 0
    VMJumpIf CMP_NE, L_BTB_Rest100
    WorkSetConst VAR_BT_STATUS_LV50, BT_ST_RESTED
    VMJump L_BTB_RestSave
L_BTB_Rest100:
    WorkSetConst VAR_BT_STATUS_LV100, BT_ST_RESTED
L_BTB_RestSave:
    BSubwayCmd_Tool 306, 0, 0, 0        // Black 2: the play block keeps the mode, the party, the trainers (the round is
    Plugin1_Cmd1002                     // in it already)
    // Sapphire writes only gSaveBlock2 here, so its Continue starts where the challenge was saved: in the lobby in
    // front of the receptionist. Black 2: the next zone (Sapphire (6,6), facing up) + EVENT_FLAG_CONTINUE_SCRIPT 2405
    // make Continue load the lobby and run its zone init (ov035 EventFieldContinue_Callback)
    FieldSetNextZone BT_LOBBY_ZONE, 1, 6 + BT_LOBBY_OX, 0, 6 + BT_LOBBY_OZ
    FlagSet 2405
    ActorMsg MSGFILE_SCRIPT, 4, BT_ROOM_ATTENDANT, 0, 0     // SAVING... DON'T TURN OFF THE POWER.
    h_delay 60
    SaveDataWrite BT_T1
    SEPlay SEQ_SE_SAVE
    SEWait
    h_buffer_player
    bt_room_say 5                       // <player> saved the game.
L_BTB_Retire:                           // 160AB1: fadescreen FADE_TO_BLACK, BattleTower_SoftReset
    h_closemessage
    FadeOutBlack
    FadeWait
    BSubwayCmd_Tool 1, 0, 0, 0          // Black 2's Battle Subway reset (sys_reset)
    VMHalt

L_BTB_Seven:                            // 160A56: seven won: LoadPlayerParty, SetBattleTowerProperty 0 = 4, 2 = 1, 7, 14;
    BSubwayCmd_Tool 305, 0, 0, 0        // sub_810FF60; warp to the lobby. Black 2: the streak goes on (sets + 1, round 0)
    WorkCmpConst VAR_BT_LEVEL_TYPE, 0
    VMJumpIf CMP_NE, L_BTB_Seven100
    WorkSetConst VAR_BT_STATUS_LV50, BT_ST_WON
    VMJump L_BTB_ToLobby
L_BTB_Seven100:
    WorkSetConst VAR_BT_STATUS_LV100, BT_ST_WON
    VMJump L_BTB_ToLobby

#ifdef HOENN_EMERALD
Sub_BTB_BrainStatus:                    // BTB_BRAIN = GetFrontierBrainStatus with the Subway streak (wins so far)
    BSubwayCmd_Tool 358, 0, 0, BT_T1
    FrontierPA PA_TOWER_STATUS, BT_T1, 0, BTB_BRAIN
    VMReturn

L_BTB_MaidenNext:                       // MaidenUpNext (Emerald's second attendant, who runs in with the news, is not
    bt_room_say BTB_L_MAIDEN_ON_HER_WAY //  in this room: the attendant says it)
L_BTB_MaidenAsk:                        // AskReadyForMaiden (the tower's YES/NO questions in place of the menu)
    bt_room_yesno BTB_L_MAIDEN_READY, BT_T2     // You will be facing the Salon Maiden. Are you prepared?
    h_goto_if_yes BT_T2, L_BTB_Continue
    bt_room_yesno 2, BT_T2              // Would you like to save and quit the game?
    h_goto_if_yes BT_T2, L_BTB_Rest
    bt_room_yesno 3, BT_T2              // Would you like to cancel your Battle Room challenge?
    h_goto_if_yes BT_T2, L_BTB_Retire
    VMJump L_BTB_MaidenAsk

    .macro btb_anabel_say n             // a line Anabel says (the window closes)
    ActorMsg MSGFILE_SCRIPT, \n, BT_OPPONENT, 0, 0
    LastKeyWait
    MsgWinCloseAll
    .endm
L_BTB_Anabel:                           // BattleAnabel: frontier_setbrainobj, she walks in slowly
    WorkSetConst BT_OPPONENT_GFX, BTB_ANABEL_SPRITE
    h_addobject BT_OPPONENT, FLAG_HIDE_BATTLE_TOWER_OPPONENT
    h_applymovement BT_OPPONENT, BTB_MvAnabelIn
    h_waitmovement
    h_goto_if_eq BTB_BRAIN, 2, L_BTB_AnabelGoldIntro     // FRONTIER_BRAIN_GOLD
    h_goto_if_eq BTB_BRAIN, 3, L_BTB_AnabelSilver        // FRONTIER_BRAIN_STREAK
    h_goto_if_eq BTB_BRAIN, 4, L_BTB_AnabelGold          // FRONTIER_BRAIN_STREAK_LONG
    FrontierPA PA_TOWER_HEARD, 0, 1, BT_T1               // FRONTIER_DATA_HEARD_BRAIN_SPEECH (no symbol yet), now set
    h_goto_if_ne BT_T1, 0, L_BTB_AnabelSilver
    btb_anabel_say BTB_L_ANABEL_GREETINGS
L_BTB_AnabelSilver:
    btb_anabel_say BTB_L_ANABEL_LET_ME_SEE
    VMCall Sub_BTB_AnabelBattle
    fr_symbol_get FRONTIER_FACILITY_TOWER, BT_T1
    h_goto_if_ne BT_T1, 0, L_BTB_AnabelDone
    btb_anabel_say BTB_L_ANABEL_POST_SILVER
    MEPlay FR_ME_OBTAIN_SYMBOL          // playfanfare MUS_OBTAIN_SYMBOL
    h_msgbox_info BTB_L_GOT_SILVER      // The Ability Symbol was embossed on the Frontier Pass!
    MEWait
    MsgWinCloseAll
    fr_symbol_give FRONTIER_FACILITY_TOWER, 0
    btb_anabel_say BTB_L_ANABEL_UNTIL_NEXT
    VMJump L_BTB_AnabelDone
L_BTB_AnabelGoldIntro:                  // AnabelGoldIntro
    FrontierPA PA_TOWER_HEARD, 1, 1, BT_T1               // (the Silver Symbol held), now set
    h_goto_if_ne BT_T1, 0, L_BTB_AnabelGold
    btb_anabel_say BTB_L_ANABEL_CAME_BACK
L_BTB_AnabelGold:
    btb_anabel_say BTB_L_ANABEL_LETS_BEGIN
    VMCall Sub_BTB_AnabelBattle
    fr_symbol_get FRONTIER_FACILITY_TOWER, BT_T1
    h_goto_if_eq BT_T1, 2, L_BTB_AnabelDone
    btb_anabel_say BTB_L_ANABEL_POST_GOLD
    MEPlay FR_ME_OBTAIN_SYMBOL
    h_msgbox_info BTB_L_GOT_GOLD        // The Ability Symbol took on a golden shine!
    MEWait
    MsgWinCloseAll
    fr_symbol_give FRONTIER_FACILITY_TOWER, 1
    btb_anabel_say BTB_L_ANABEL_LAST
L_BTB_AnabelDone:                       // DefeatedAnabel*: the streak goes on as after any win (her battle is the 7th
    fr_set FR_BRAIN_BEATEN, 1           //  of its set: back to the lobby, which says the Brain line and pays +10 BP)
    VMJump L_BTB_Won
Sub_BTB_AnabelBattle:                   // DoTowerBattle against Anabel (lost: back to the lobby as any loss)
    h_heal
    FrontierPA PA_TOWER_BATTLE, BTB_BRAIN, 0, BT_T1
    h_heal
    h_goto_if_ne BT_T1, 1, L_BTB_Lost
    VMReturn
#endif

Sub_BTB_SaveStreak:                     // SaveCurrentWinStreak: recordWinStreaks[level] = max(it, the streak in BT_T2)
    WorkCmpConst VAR_BT_LEVEL_TYPE, 0
    VMJumpIf CMP_NE, L_BTB_SS100
    VMStackPush BT_T2
    VMStackPush VAR_BT_RECORD_LV50
    VMStackCmp CMP_GT
    VMJumpIf CMP_STACK, L_BTB_SSDone
    WorkSet VAR_BT_RECORD_LV50, BT_T2
    VMReturn
L_BTB_SS100:
    VMStackPush BT_T2
    VMStackPush VAR_BT_RECORD_LV100
    VMStackCmp CMP_GT
    VMJumpIf CMP_STACK, L_BTB_SSDone
    WorkSet VAR_BT_RECORD_LV100, BT_T2
L_BTB_SSDone:
    VMReturn

#include "common/fan_club.inc"

    .balign 4, 0
BTB_MvPlayerIn:                         // _160AB7
    walk_up 3
    face_right
    step_end
BTB_MvFaceDown:                         // _160ABC
    face_down
    step_end
BTB_MvFaceRight:                        // _160ABE
    face_right
    step_end
BTB_MvOppIn:                            // _160AC0
    walk_down 4
    face_left
    step_end
#ifdef HOENN_EMERALD
BTB_MvAnabelIn:                         // BattleFrontier_BattleTowerBattleRoom_Movement_AnabelEnter
    walk_slow_down 4
    face_left
    step_end
#endif
BTB_MvOppOut:                           // _160AC6
    walk_up 4
    step_end
BTB_MvAttIn:                            // _160ACB
    walk_right 3
    walk_up
    step_end
BTB_MvAttOut:                           // _160AD0
    walk_down
    walk_left 3
    face_right
    step_end
