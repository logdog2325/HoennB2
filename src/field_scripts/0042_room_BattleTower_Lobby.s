// BattleTower_Lobby (zone 21): Sapphire's simple people and signs (as converter/gen_interiors.py makes them),
// plus people that turn back after their message (Common_Movement_FaceOriginalDirection), by the specials agent
// (b2tools/specials.py people). Messages: src/text/script/0027_room_BattleTower_Lobby.txt
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_story.inc"
#include "scenes/battle_tower_lib.inc"
#ifdef HOENN_EMERALD
// Pokémon Emerald NDS (frontier_core, 2026-10-12; notes/FRONTIER.md): the receptionist runs the Battle Frontier's
// lobby flow (Emerald's lines: LV. 50 / OPEN LEVEL, Emerald's eligibility rules) and seven wins pay Emerald's Battle
// Points instead of Sapphire's prize. The lines are appended to this zone's text in Emerald builds
// (src/text/emerald/overrides_frontier_core.json, written by b2tools/frontier_text.py install).
#include "hoenn_emerald.inc"
#include "hoenn_frontier.inc"
#define BTL_FR_TB 68                    // the Emerald lobby text block: lines 68-90 (hoenn_frontier.inc FRT_*)
#define BTL_FR_STREAK_49 91             // "You're about to face the 50th Trainer..." (Emerald's AboutToFace50thTrainer)
#endif

    ScriptEntry Script_1
    ScriptEntry Script_2
    ScriptEntry BTL_Receptionist        // 3: BattleTower_Lobby_EventScript_16049E (object 1, TEALA)
    ScriptEntry BTL_Interviewer         // 4: _1606A5 (object 2, MAN_5)
    ScriptEntry BTL_Reporter            // 5: _1AE1FF (object 5, the Bravo Trainer reporter: hidden, see below)
    ScriptEntry BTL_AwardMan            // 6: _160733 (object 6, MAN_2)
    ScriptEntry BTL_Records             // 7: _160727 (sign (3,5), read facing north)
    ScriptEntry BTL_State               // 8: ON_FRAME_TABLE (map-script condition BT_STATE 0, 0043_..._init.s)
    ScriptEntry BTL_Init                // 9: ON_RESUME / ON_TRANSITION (zone init, 0043_..._init.s)
    ScriptEntriesEnd

Script_1:
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    ActorSetEyeToEye
    ParentActorMsg MSGFILE_SCRIPT, 0, 0, 0
    LastKeyWait
    ActorMsgClose
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

Script_2:
    ActorsPauseAll
    WordSetPlayerName 0
    SEPlay SEQ_SE_MESSAGE
    ActorSetEyeToEye
    ParentActorMsg MSGFILE_SCRIPT, 1, 0, 0
    LastKeyWait
    ActorMsgClose
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt
    .balign 4, 0

// ---- story (battle_tower 2026-10-08: Sapphire's Battle Tower lobby, data/maps/BattleTower_Lobby/scripts.inc;
// notes/BATTLE_TOWER.md). Text lines 2-67 of 0027_room_BattleTower_Lobby.txt. Black 2's Battle Subway plugin (plugin 1,
// b2tools/patches/battle_tower.py) chooses the party and keeps the streak: play mode 0 = Lv. 50, 5 = Lv. 100.
#include "scenes/battle_tower_eligible.inc"
#include "scenes/battle_tower_test.inc"

    .macro bt_say n                     // msgbox said by the receptionist (window stays open)
    ActorMsg MSGFILE_SCRIPT, \n, BT_RECEPTIONIST, 0, 0
    LastKeyWait
    .endm
    .macro bt_print n                   // message + waitmessage by the receptionist (no key wait at its end)
    ActorMsg MSGFILE_SCRIPT, \n, BT_RECEPTIONIST, 0, 0
    .endm
    .macro bt_mode dst                  // the Battle Subway play mode of VAR_BT_LEVEL_TYPE
    WorkSetConst \dst, BT_MODE_LV50
    WorkCmpConst VAR_BT_LEVEL_TYPE, 0
    VMJumpIf CMP_EQ, .Lbtm\@
    WorkSetConst \dst, BT_MODE_LV100
.Lbtm\@:
    .endm
    .macro bt_get_status dst            // Sapphire's var_4AE[battleTowerLevelType]
    WorkSet \dst, VAR_BT_STATUS_LV50
    WorkCmpConst VAR_BT_LEVEL_TYPE, 0
    VMJumpIf CMP_EQ, .Lbgs\@
    WorkSet \dst, VAR_BT_STATUS_LV100
.Lbgs\@:
    .endm
    .macro bt_set_status value          // SetBattleTowerProperty 0: var_4AE[battleTowerLevelType] = value
    WorkCmpConst VAR_BT_LEVEL_TYPE, 0
    VMJumpIf CMP_NE, .Lbss\@
    WorkSetConst VAR_BT_STATUS_LV50, \value
    VMJump .Lbss2\@
.Lbss\@:
    WorkSetConst VAR_BT_STATUS_LV100, \value
.Lbss2\@:
    .endm
    .macro bt_set_status_var var
    WorkCmpConst VAR_BT_LEVEL_TYPE, 0
    VMJumpIf CMP_NE, .Lbsv\@
    WorkSet VAR_BT_STATUS_LV50, \var
    VMJump .Lbsv2\@
.Lbsv\@:
    WorkSet VAR_BT_STATUS_LV100, \var
.Lbsv2\@:
    .endm

BTL_Init:                               // ON_RESUME (TryEnableBravoTrainerBattleTower, 16029C) and ON_TRANSITION (1AE2ED)
#ifdef HOENN_TEST_CHBT
    VMCall Test_BT_Party                // (test builds: scenes/battle_tower_test.inc)
#endif
    // The award man (object 6) shows once the best streak (GAME_STAT_BATTLE_TOWER_BEST_STREAK = the better record)
    // reaches 50 (the Silver Shield), then 100 (the Gold Shield)
    WorkSet BT_T1, VAR_BT_RECORD_LV50
    VMStackPush VAR_BT_RECORD_LV100
    VMStackPush BT_T1
    VMStackCmp CMP_GT
    VMJumpIf CMP_STACK, L_BTL_InitBest
    WorkSet BT_T1, VAR_BT_RECORD_LV100
L_BTL_InitBest:
    h_goto_if_set FLAG_RECEIVED_GOLD_SHIELD, L_BTL_InitHide
    WorkSetConst BT_T2, 50
    h_goto_if_unset FLAG_RECEIVED_SILVER_SHIELD, L_BTL_InitCmp
    WorkSetConst BT_T2, 100
L_BTL_InitCmp:
    VMStackPush BT_T1
    VMStackPush BT_T2
    VMStackCmp CMP_GE
    VMJumpIf CMP_STACK, L_BTL_InitHide
    FlagReset FLAG_HIDE_AWARD_MAN_BATTLE_TOWER
    VMHalt
L_BTL_InitHide:
    FlagSet FLAG_HIDE_AWARD_MAN_BATTLE_TOWER
    VMHalt

// ON_FRAME_TABLE: VAR_TEMP_0 0 -> sub_8134548 (each level's status), then 1 disqualified / 2 won seven / 3 lost /
// 4 back after a rest. BT_STATE (map-local 0x4000) is 0 after every zone init and in every save the tower makes.
BTL_State:
    ActorsPauseAll
    WorkSetConst BT_T4, 0               // var1: a level with something to tell
    WorkSetConst BT_STATE, 5
    WorkSet BT_T1, VAR_BT_STATUS_LV50
    WorkSetConst BT_T2, 0
    VMCall Sub_BTL_LevelState
    WorkSet BT_T1, VAR_BT_STATUS_LV100
    WorkSetConst BT_T2, 1
    VMCall Sub_BTL_LevelState
    h_goto_if_eq BT_STATE, 1, L_BTL_Disqualified
    h_goto_if_eq BT_STATE, 2, L_BTL_Won
    h_goto_if_eq BT_STATE, 3, L_BTL_Lost
    h_goto_if_eq BT_STATE, 4, L_BTL_Resume
    h_release

Sub_BTL_LevelState:                     // sub_8134548 for one level: BT_T1 = its status, BT_T2 = the level
    h_goto_if_eq BT_T1, BT_ST_ENTERED, L_BTL_LS1
    h_goto_if_eq BT_T1, BT_ST_WON, L_BTL_LS4
    h_goto_if_eq BT_T1, BT_ST_LOST, L_BTL_LS5
    h_goto_if_eq BT_T1, BT_ST_RESTED, L_BTL_LS2
    h_goto_if_eq BT_T1, BT_ST_WON_SAVED, L_BTL_LSDone
    h_goto_if_eq BT_T1, BT_ST_PRIZE, L_BTL_LSDone
    VMCall Sub_BTL_ResetLevel           // 0 / default: ResetBattleTowerStreak (Black 2 ended the streak already)
    VMReturn
L_BTL_LS1:                              // quit without saving: ResetBattleTowerStreak, the challenge so far is lost
    VMCall Sub_BTL_ResetLevel
    BSubwayCmd_Tool 7, 0, 0, BT_T3      // Black 2: the play block's mode (this challenge's) streak ends, round 0
    WorkSetConst BT_STATE, 1
    VMJump L_BTL_LSVar
L_BTL_LS4:
    WorkSetConst BT_STATE, 2
    VMJump L_BTL_LSVar
L_BTL_LS5:
    WorkSetConst BT_STATE, 3
    VMJump L_BTL_LSVar
L_BTL_LS2:
    WorkSetConst BT_STATE, 4
L_BTL_LSVar:
    WorkSet VAR_BT_LEVEL_TYPE, BT_T2    // (the status of this level is the one being dealt with)
    WorkAdd BT_T4, 1
L_BTL_LSDone:
    VMReturn
Sub_BTL_ResetLevel:                     // var_4AE[level] = 0 (curChallengeBattleNum / curStreakChallengesNum: Black 2's)
    h_goto_if_eq BT_T2, 1, L_BTL_RL100
    WorkSetConst VAR_BT_STATUS_LV50, BT_ST_NONE
    VMReturn
L_BTL_RL100:
    WorkSetConst VAR_BT_STATUS_LV100, BT_ST_NONE
    VMReturn

L_BTL_Disqualified:                     // 160330
#ifdef HOENN_EMERALD
    fr_gambler_settle 0                 // the Frontier Gambler's bet on this challenge (Lounge3): lost (quit unsaved)
#endif
    bt_say 12                           // Excuse me! You didn't save before you quit your challenge last time ...
    h_closemessage
    WorkSetConst BT_STATE, 5
    h_release

L_BTL_Lost:                             // 160419
#ifdef HOENN_EMERALD
    fr_gambler_settle 0                 // the Frontier Gambler's bet on this challenge (Lounge3): lost
#endif
    bt_print 17                         // Thank you for playing!
    bt_print 18                         // Your record will be saved. Please wait.
    VMCall Sub_BTL_LastStreak           // SetBattleTowerProperty 13
    Plugin1_Cmd1002                     // (the Battle Subway work of the challenge, kept from the Battle Room)
    bt_set_status BT_ST_NONE            // SaveBattleTowerProgress 0
    VMCall Sub_BTL_SaveRecord
    bt_say 4                            // We'll be looking forward to your next challenge.
    h_closemessage
    WorkSetConst BT_STATE, 5
    h_release

Sub_BTL_LastStreak:                     // currentWinStreaks[level] = GetCurrentBattleTowerWinStreak: Black 2's stored
    bt_mode BT_T1                       // streak of the mode (written by command 304 / 305 in the Battle Room)
    BSubwayCmd_Tool 6, BT_T1, 0, BT_T2
    WorkCmpConst VAR_BT_LEVEL_TYPE, 0
    VMJumpIf CMP_NE, L_BTL_LS100
    WorkSet VAR_BT_LAST_STREAK_LV50, BT_T2
    VMReturn
L_BTL_LS100:
    WorkSet VAR_BT_LAST_STREAK_LV100, BT_T2
    VMReturn

Sub_BTL_SaveRecord:                     // SaveBattleTowerProgress: VAR_TEMP_0 = 0, the save, SE_SAVE
    WorkSetConst BT_STATE, 0
    SaveDataWrite BT_T1
    WorkSetConst BT_STATE, 5
    SEPlay SEQ_SE_SAVE
    SEWait
    VMReturn

L_BTL_Won:                              // 160342 (also the receptionist with a prize still to give)
#ifdef HOENN_EMERALD
    fr_gambler_settle 1                 // the Frontier Gambler's bet on this challenge (Lounge3): won
    fr_get FR_BRAIN_BEATEN, BT_T1       // the set ended with the Salon Maiden (0030_room_BattleTower_BattleRoom.s):
    h_goto_if_eq BT_T1, 0, L_BTL_WonTrainers    // Emerald's frontier_isbrain -> DefeatedMaiden
    bt_print BTL_FR_TB + FRT_WON_BRAIN  // Congratulations! You have defeated the Salon Maiden and swept seven Trainers!
    VMJump L_BTL_WonSaid
L_BTL_WonTrainers:
#endif
    bt_print 13                         // Congratulations! You've beaten all seven Trainers!
#ifdef HOENN_EMERALD
L_BTL_WonSaid:
#endif
    bt_get_status BT_T1
    h_goto_if_eq BT_T1, BT_ST_PRIZE, L_BTL_Record
    VMCall Sub_BTL_Ribbons              // AwardBattleTowerRibbons
    h_goto_if_eq HLIB_RESULT, 0, L_BTL_Record
    h_buffer_player
    bt_print 22                         // Here are some Ribbons for beating seven tough Trainers in a row. <player> received some Ribbons!
    MEPlay MUS_OBTAIN_ITEM
    MEWait
    bt_say 23                           // <player> put the Ribbons on the challenger Pokémon.
L_BTL_Record:                           // 16037D
#ifdef HOENN_EMERALD
    // Emerald (BattleFrontier_BattleTowerLobby_EventScript_GiveBattlePoints): Battle Points for the seven wins, from
    // pokeemerald's sBattlePointAwards by the streak (Black 2's stored streak of this mode, Emerald's
    // towerWinStreaks), then the record save; no Sapphire prize
    bt_say BTL_FR_TB + FRT_AWARD        // In recognition of your infinite talent, we award you these Battle Point(s).
    bt_mode BT_T1
    BSubwayCmd_Tool 6, BT_T1, 0, BT_T2
    fr_get FR_BRAIN_BEATEN, BT_T1
    h_goto_if_ne BT_T1, 0, L_BTL_FrBrainBP
    fr_give_points_for BT_T2, 0
    VMJump L_BTL_FrGotBP
L_BTL_FrBrainBP:                        // +10 after the Brain (GiveBattlePoints: TRAINER_FRONTIER_BRAIN)
    fr_give_points_for BT_T2, 1
    fr_set FR_BRAIN_BEATEN, 0
L_BTL_FrGotBP:
    h_buffer_player
    MEPlay FR_ME_OBTAIN_BP              // Emerald's mus_obtain_b_points (MSGBOX_GETPOINTS)
    bt_say BTL_FR_TB + FRT_OBTAINED_BP  // <player> obtained N Battle Point(s).
    MEWait
    bt_print 18                         // Your record will be saved. Please wait.
    VMCall Sub_BTL_LastStreak
    Plugin1_Cmd1002
    bt_set_status BT_ST_WON_SAVED
    VMCall Sub_BTL_SaveRecord
    bt_mode BT_T1
    BSubwayCmd_Tool 6, BT_T1, 0, BT_T2
    h_goto_if_ne BT_T2, 49, L_BTL_FrBye
    bt_say BTL_FR_STREAK_49
L_BTL_FrBye:
    bt_say BTL_FR_TB + FRT_GOODBYE      // We look forward to seeing you on another challenge!
    h_closemessage
    WorkSetConst BT_STATE, 5
    h_release
#endif
    bt_get_status BT_T1
    h_goto_if_eq BT_T1, BT_ST_PRIZE, L_BTL_Prize    // BattleTowerUtil 8 (unk_554): the record is saved already
    bt_print 18                         // Your record will be saved. Please wait.
    VMCall Sub_BTL_LastStreak           // SetBattleTowerProperty 13
    VMCall Sub_BTL_DeterminePrize       // DetermineBattleTowerPrize
    Plugin1_Cmd1002
    bt_set_status BT_ST_PRIZE           // (saved with the prize to give: a reset before it is given keeps it)
    VMCall Sub_BTL_SaveRecord           // SaveBattleTowerProgress 3
L_BTL_Prize:                            // 1603AD
    bt_set_status BT_ST_WON_SAVED       // SetBattleTowerProperty 0 = 3
    bt_print 14                         // For beating seven Trainers in a row, you have earned this fabulous prize!
    ItemCheckSpace VAR_BT_PRIZE, 1, BT_T1           // GiveBattleTowerPrize
    h_goto_if_eq BT_T1, 0, L_BTL_BagFull
    ItemAdd VAR_BT_PRIZE, 1, BT_T1
    h_buffer_player
    WordSetItemName 1, VAR_BT_PRIZE
    bt_print 15                         // <player> received the prize <item>.
    MEPlay MUS_OBTAIN_ITEM
    MEWait
    WorkSetConst VAR_BT_PRIZE, 0
    bt_mode BT_T1                       // BattleTowerUtil 9 == 49: the next one is the 50th trainer
    BSubwayCmd_Tool 6, BT_T1, 0, BT_T2
    h_goto_if_ne BT_T2, 49, L_BTL_PrizeEnd
    bt_say 21                           // You're finally about to face the 50th Trainer ...
L_BTL_PrizeEnd:                         // 1603F8
    bt_say 4                            // We'll be looking forward to your next challenge.
    h_closemessage
    WorkSetConst BT_STATE, 5
    h_release
L_BTL_BagFull:                          // 160408
    bt_set_status BT_ST_PRIZE           // var_4AE = 6
    bt_say 16                           // Oh, your Bag appears to be full ...
    h_closemessage
    WorkSetConst BT_STATE, 5
    h_release

Sub_BTL_Ribbons:                        // AwardBattleTowerRibbons: streak > 55 -> Winning (Lv. 50) / Victory (Lv. 100)
    WorkSetConst HLIB_RESULT, 0         // Ribbon on each of the three challengers that lacks it
    bt_mode BT_T1
    BSubwayCmd_Tool 6, BT_T1, 0, BT_T2
    WorkCmpConst BT_T2, 55
    VMJumpIf CMP_LE, L_BTL_RibDone
    WorkSetConst BT_T3, 0
L_BTL_RibLoop:
    BSubwayCmd_Tool 317, BT_T3, 0, BT_T4        // the challenger's party slot (selectedPartyMons[i] - 1)
    WorkCmpConst VAR_BT_LEVEL_TYPE, 0
    VMJumpIf CMP_NE, L_BTL_Rib100
    h_check_ribbon BT_T1, BT_T4, RIBBON_WINNING
    h_goto_if_ne BT_T1, 0, L_BTL_RibNext
    h_give_ribbon BT_T4, RIBBON_WINNING
    WorkSetConst HLIB_RESULT, 1
    VMJump L_BTL_RibNext
L_BTL_Rib100:
    h_check_ribbon BT_T1, BT_T4, RIBBON_VICTORY
    h_goto_if_ne BT_T1, 0, L_BTL_RibNext
    h_give_ribbon BT_T4, RIBBON_VICTORY
    WorkSetConst HLIB_RESULT, 1
L_BTL_RibNext:
    WorkAdd BT_T3, 1
    h_goto_if_lt BT_T3, 3, L_BTL_RibLoop
    h_goto_if_eq HLIB_RESULT, 0, L_BTL_RibDone
    h_setflag FLAG_SYS_RIBBON_GET       // (Sapphire's specials set it; IncrementGameStat RECEIVED_RIBBONS: no stat)
L_BTL_RibDone:
    VMReturn

Sub_BTL_DeterminePrize:                 // sets won - 1 > 5 (curStreakChallengesNum - 1 > 5): a held item, else a vitamin
    bt_mode BT_T1
    BSubwayCmd_Tool 30, BT_T1, 0, BT_T2         // completed sets of the streak (score set counter - 1)
    h_goto_if_gt BT_T2, 5, L_BTL_LongPrize
    Random BT_T3, 6                     // sShortStreakPrizes[Random() % 6]
    WorkSetConst VAR_BT_PRIZE, ITEM_HP_UP
    h_goto_if_eq BT_T3, 0, L_BTL_PrizeSet
    WorkSetConst VAR_BT_PRIZE, ITEM_PROTEIN
    h_goto_if_eq BT_T3, 1, L_BTL_PrizeSet
    WorkSetConst VAR_BT_PRIZE, ITEM_IRON
    h_goto_if_eq BT_T3, 2, L_BTL_PrizeSet
    WorkSetConst VAR_BT_PRIZE, ITEM_CALCIUM
    h_goto_if_eq BT_T3, 3, L_BTL_PrizeSet
    WorkSetConst VAR_BT_PRIZE, ITEM_CARBOS
    h_goto_if_eq BT_T3, 4, L_BTL_PrizeSet
    WorkSetConst VAR_BT_PRIZE, ITEM_ZINC
    VMReturn
L_BTL_LongPrize:
    Random BT_T3, 9                     // sLongStreakPrizes[Random() % 9]
    WorkSetConst VAR_BT_PRIZE, ITEM_BRIGHT_POWDER
    h_goto_if_eq BT_T3, 0, L_BTL_PrizeSet
    WorkSetConst VAR_BT_PRIZE, ITEM_WHITE_HERB
    h_goto_if_eq BT_T3, 1, L_BTL_PrizeSet
    WorkSetConst VAR_BT_PRIZE, ITEM_QUICK_CLAW
    h_goto_if_eq BT_T3, 2, L_BTL_PrizeSet
    WorkSetConst VAR_BT_PRIZE, ITEM_LEFTOVERS
    h_goto_if_eq BT_T3, 3, L_BTL_PrizeSet
    WorkSetConst VAR_BT_PRIZE, ITEM_MENTAL_HERB
    h_goto_if_eq BT_T3, 4, L_BTL_PrizeSet
    WorkSetConst VAR_BT_PRIZE, ITEM_KINGS_ROCK
    h_goto_if_eq BT_T3, 5, L_BTL_PrizeSet
    WorkSetConst VAR_BT_PRIZE, ITEM_FOCUS_BAND
    h_goto_if_eq BT_T3, 6, L_BTL_PrizeSet
    WorkSetConst VAR_BT_PRIZE, ITEM_SCOPE_LENS
    h_goto_if_eq BT_T3, 7, L_BTL_PrizeSet
    WorkSetConst VAR_BT_PRIZE, ITEM_CHOICE_BAND
L_BTL_PrizeSet:
    VMReturn

L_BTL_Resume:                           // 16044B: back after "save and quit"
    h_setvar VAR_BRAVO_TRAINER_BATTLE_TOWER_ON, 1
    bt_mode BT_T1
    Plugin1_Cmd1001 1, BT_T1            // Black 2 resumes the challenge from the play block (mode, party, trainers)
    bt_print 19                         // We've been waiting for you!
    bt_print 20                         // Before entering a Battle Room, your progress will be saved. Please wait.
    bt_set_status BT_ST_ENTERED         // SaveBattleTowerProgress 1
    VMCall Sub_BTL_SaveRecord
    WorkSetConst BT_STATE, 5
    bt_say 8                            // I'll direct you to your Battle Room now.
    h_closemessage
    VMJump L_BTL_ToRoom

BTL_Receptionist:                       // 16049E
#ifdef HOENN_EMERALD
    // Emerald: the Frontier's lobby flow (hoenn_frontier.inc) with the tower's Black 2 Subway steps as its hooks
    fr_lobby_attendant FRONTIER_FACILITY_TOWER, FRONTIER_MODE_SINGLES, BTL_FR_TB, L_BTL_FrEnter, 3, Sub_BTL_FrPick, Sub_BTL_FrUnpick, Sub_BTL_FrSave, 0
Sub_BTL_FrPick:                         // FR_T0 = the level mode: Lv. 50 = the Lv. 50 room, Open Level = the Lv. 100 room
    WorkSet VAR_BT_LEVEL_TYPE, FR_T0
    WorkSetConst BT_T4, 0               // (the save not reached yet)
    bt_say BTL_FR_TB + FRT_CHOOSE       // Now please select the three Pokémon that are to be entered.
    h_closemessage
    bt_mode BT_T1
    Plugin1_Cmd1001 0, BT_T1            // as below: Black 2's Battle Subway work and its party list
    BSubwayCmd_Tool 300, 0, 0, 0
    BSubwayCmd_Tool 301, 0, 0, FR_T1
    h_goto_if_ne FR_T1, 0, L_BTL_FrPicked
    Plugin1_Cmd1002
L_BTL_FrPicked:
    VMReturn
Sub_BTL_FrSave:                         // 160587, just before the save (the library saves)
    bt_get_status BT_T1
    WorkSet BT_T3, BT_T1
    WorkSetConst BT_T4, 1
    h_goto_if_eq BT_T1, BT_ST_WON_SAVED, L_BTL_FrKeep
    BSubwayCmd_Tool 349, 0, 0, 0
L_BTL_FrKeep:
    BSubwayCmd_Tool 359, 0, 0, 0
    bt_set_status BT_ST_ENTERED
    WorkSetConst BT_STATE, 0
    VMReturn
Sub_BTL_FrUnpick:                       // NO to the save, or the save refused: 16064F / 160642
    WorkSetConst BT_STATE, 5
    h_goto_if_eq BT_T4, 0, L_BTL_FrUnpicked
    bt_set_status_var BT_T3
L_BTL_FrUnpicked:
    Plugin1_Cmd1002
    VMReturn
L_BTL_FrEnter:                          // saved: "I will now show you to the Single Battle Room."
    WorkSetConst BT_STATE, 5
    BSubwayCmd_Tool 316, 0, 0, 0
    h_setvar VAR_BRAVO_TRAINER_BATTLE_TOWER_ON, 1
    VMJump L_BTL_ToRoom
#endif
    h_lock
    SEPlay SEQ_SE_MESSAGE
    h_faceplayer
    bt_get_status BT_T1
    h_goto_if_eq BT_T1, BT_ST_PRIZE, L_BTL_Won      // BattleTowerUtil 0 == 6
    bt_say 2                            // Welcome to the Battle Tower! Please register with me to enter a Battle Room.
L_BTL_Menu:                             // 1604BE
    bt_print 3                          // Would you like to make a Battle Room challenge?
    ListMenu_AnchorTopRight 31, 6, 0, 1, BT_T1      // multichoice 15, 6, 23 (MAKE A CHALLENGE / OBTAIN INFORMATION / CANCEL)
    ListMenuAdd 34, 65535, 0
    ListMenuAdd 35, 65535, 1
    ListMenuAdd 36, 65535, 2
    ListMenuShow
    h_goto_if_eq BT_T1, 0, L_BTL_Challenge
    h_goto_if_eq BT_T1, 1, L_BTL_Info
    VMJump L_BTL_Cancel
L_BTL_Info:                             // 160600
    bt_say 9                            // The Battle Tower is a facility made especially for Pokémon battles ...
    VMJump L_BTL_Menu
L_BTL_Challenge:                        // 1604FA
    bt_print 6                          // There are two Battle Rooms, Level 50 and Level 100. Which would you like to challenge?
    ListMenu_AnchorTopRight 31, 6, 0, 1, BT_T1      // multichoice 18, 6, 24 (LV. 50 / LV. 100 / CANCEL)
    ListMenuAdd 37, 65535, 0
    ListMenuAdd 38, 65535, 1
    ListMenuAdd 36, 65535, 2
    ListMenuShow
    h_goto_if_gt BT_T1, 1, L_BTL_Cancel
    VMCall Sub_BT_CheckParty            // CheckPartyBattleTowerBanlist (level type in BT_T1)
    h_goto_if_lt BT_T2, 3, L_BTL_Ineligible
    WorkSet VAR_BT_LEVEL_TYPE, BT_T1    // SetBattleTowerProperty 1 (battleTowerLevelType)
    bt_say 7                            // Please select the Pokémon you wish to enter.
    h_closemessage
    bt_mode BT_T1
    Plugin1_Cmd1001 0, BT_T1            // Black 2's Battle Subway work for this play mode (the streak goes on if
    BSubwayCmd_Tool 300, 0, 0, 0        // the score says so); ChooseBattleTowerPlayerParty: Black 2's party list
    BSubwayCmd_Tool 301, 0, 0, BT_T1    // (3 Pokémon, regulation: Lv. 50 or less / any level), 1 = chosen
    h_goto_if_eq BT_T1, 0, L_BTL_NotChosen
    h_yesno 5, BT_T1                    // Before entering a Battle Room, your progress must be saved. Is that okay?
    h_goto_if_no BT_T1, L_BTL_NotChosen
    // 160587: SetBattleTowerProperty 5 (the chosen Pokémon: Black 2's work), 11 (ResetBattleTowerStreak unless the
    // last challenge was won and saved), 0 = 1 (entered), 8 = 0; the save
    bt_get_status BT_T1
    WorkSet BT_T3, BT_T1                // (SetBattleTowerProperty 12 puts it back when the save is refused)
    h_goto_if_eq BT_T1, BT_ST_WON_SAVED, L_BTL_KeepStreak
    BSubwayCmd_Tool 349, 0, 0, 0        // Black 2: this mode's streak ends, round 0
L_BTL_KeepStreak:
    BSubwayCmd_Tool 359, 0, 0, 0        // Black 2: a streak starts here when none goes on (wins 0)
    bt_set_status BT_ST_ENTERED
    h_closemessage
    WorkSetConst BT_STATE, 0            // (VAR_TEMP_0 = 0 in the save: a Continue without the tower's own save shows
    VMStackPush 0x8000                  //  "you didn't save before you quit")
    VMStackPush 0x8001
    VMStackPush 0x8002
    VMStackPush 0x8003
    VMStackPush 0x8004
    VMStackPush 0x8005
    RTCallGlobal 2003                   // Common_EventScript_SaveGame: Black 2's save dialog; 0x8000 = 0 saved
    WorkSet BT_T1, 0x8000
    VMStackPop 0x8005
    VMStackPop 0x8004
    VMStackPop 0x8003
    VMStackPop 0x8002
    VMStackPop 0x8001
    VMStackPop 0x8000
    WorkSetConst BT_STATE, 5
    h_goto_if_ne BT_T1, 0, L_BTL_NotSaved
    BSubwayCmd_Tool 316, 0, 0, 0        // ChooseNextBattleTowerTrainer for the seven battles (Sapphire's rule:
    h_setvar VAR_BRAVO_TRAINER_BATTLE_TOWER_ON, 1   // b2tools/patches/battle_tower.py)
    bt_say 8                            // I'll direct you to your Battle Room now.
    h_closemessage
L_BTL_ToRoom:                           // 160664
    h_applymovement BT_RECEPTIONIST, BTL_MvUp3
    h_applymovement BT_PLAYER, BTL_MvUp3
    h_waitmovement
    bt_door_open 6 + BT_LOBBY_OX, 1 + BT_LOBBY_OZ   // opendoor 6, 1
    h_applymovement BT_RECEPTIONIST, BTL_MvRecepIn
    h_applymovement BT_PLAYER, BTL_MvPlayerIn
    h_waitmovement
    bt_door_close                       // closedoor 6, 1
    h_warp_scene BT_ELEVATOR_ZONE, 1 + BT_ELEVATOR_OX, 6 + BT_ELEVATOR_OZ, 0, 1     // warp MAP_BATTLE_TOWER_ELEVATOR, 255, 1, 6
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt
L_BTL_NotSaved:                         // 160642: SetBattleTowerProperty 12
    bt_set_status_var BT_T3
    Plugin1_Cmd1002
    VMJump L_BTL_Cancel
L_BTL_NotChosen:                        // 16064F: LoadPlayerParty
    Plugin1_Cmd1002
L_BTL_Cancel:                           // 160652
    bt_say 4                            // We'll be looking forward to your next challenge.
    VMCall Sub_BTL_ResetUnlessWon       // SetBattleTowerProperty 11
    h_closemessage
    h_release
L_BTL_Ineligible:                       // 16060D: 160628 / 160635
    ActorMsg MSGFILE_SCRIPT, BT_T3, BT_RECEPTIONIST, 0, 0   // Excuse me! You don't have three eligible Pokémon ...
    LastKeyWait
    h_closemessage
    h_release

Sub_BTL_ResetUnlessWon:                 // SetBattleTowerProperty 11: ResetBattleTowerStreak unless var_4AE == 3; the
    bt_get_status BT_T1                 // level is the last one chosen (Black 2's streak ends only when a new
    h_goto_if_eq BT_T1, BT_ST_WON_SAVED, L_BTL_RUW   // challenge starts, command 349 above)
    bt_set_status BT_ST_NONE
L_BTL_RUW:
    VMReturn

BTL_Interviewer:                        // 1606A5 (Sapphire: the player's Battle Tower greeting, easy-chat words)
    h_lock
    SEPlay SEQ_SE_MESSAGE
    h_faceplayer
    h_yesno 24, BT_T1                   // Hello, hello! ... Can you tell me what's going through your mind ...?
    h_goto_if_no BT_T1, L_BTL_IntNo
    h_msgbox 25                         // Oh, wow, you'll tell me? Great! Then, what's your answer?
    MsgWinCloseAll                      // Common_EventScript_ShowEasyChatScreen: Black 2 has no easy-chat sentences;
    FadeOutBlackQ                       // its word picker (CallPhraseSelect 4, as ch3_lib.inc's c3_easy_chat), which
    FadeWait                            // stores nothing
    FieldClose
    CallPhraseSelect 4, BT_T2, BT_T3, BT_T1
    FieldOpen
    FadeInBlackQ
    FadeWait
    h_lock
    h_faceplayer
    h_goto_if_eq BT_T1, 1, L_BTL_IntOk
    h_msgbox 27                         // Hunh? You changed your mind? I guess you're fickle.
    h_release
L_BTL_IntOk:
    h_msgbox 28                         // Okay, so that's how you feel? That's quite original. Thanks!
    h_release
L_BTL_IntNo:
    h_msgbox 26                         // Oh, so you don't think much about it? You're one cool customer.
    h_release

BTL_Reporter:                           // the Bravo Trainer interview (TV) is not ported: Black 2 has no TV shows; the
    h_release                           // reporter stays hidden (FLAG_HIDE_REPORTER_BATTLE_TOWER, the island sets it)

BTL_AwardMan:                           // 160733
    h_lock
    SEPlay SEQ_SE_MESSAGE
    h_faceplayer
    h_goto_if_set FLAG_RECEIVED_GOLD_SHIELD, L_BTL_AwardDone
    h_goto_if_set FLAG_RECEIVED_SILVER_SHIELD, L_BTL_Award100
    h_msgbox 29                         // Hahahaha! Pure magnificence! ... You've beaten 50 Trainers in a row! ...
    h_setflag FLAG_RECEIVED_SILVER_SHIELD   // givedecoration DECOR_SILVER_SHIELD: Black 2 has no decorations
    h_msgbox 31                         // I suggest you keep it displayed. It will surely attract attention.
    h_release
L_BTL_Award100:                         // 160773
    WorkSet BT_T1, VAR_BT_RECORD_LV50
    VMStackPush VAR_BT_RECORD_LV100
    VMStackPush BT_T1
    VMStackCmp CMP_GT
    VMJumpIf CMP_STACK, L_BTL_AwardBest
    WorkSet BT_T1, VAR_BT_RECORD_LV100
L_BTL_AwardBest:
    h_goto_if_lt BT_T1, 100, L_BTL_AwardDone
    h_msgbox 30                         // Wahahaha! ... You've beaten 100 Trainers in a row! ...
    h_setflag FLAG_RECEIVED_GOLD_SHIELD     // givedecoration DECOR_GOLD_SHIELD
    h_msgbox 31
    h_release
L_BTL_AwardDone:                        // 1607C5
    h_msgbox 33                         // I'm overwhelmed with satisfaction after seeing your magnificent performance ...
    h_release

BTL_Records:                            // 160727: ShowBattleTowerRecords (Sapphire's window, as three pages)
    h_lock
    SEPlay SEQ_SE_MESSAGE
    h_buffer_player
    SystemMsg 41, 2                     // <player>'s Battle Tower Results
    LastKeyWait
    WordSetNumber 1, VAR_BT_LAST_STREAK_LV50, 4
    WordSetNumber 2, VAR_BT_RECORD_LV50, 4
    WorkSet BT_T1, VAR_BT_STATUS_LV50
    WorkSetConst BT_T2, 42              // CURRENT while a challenge goes on (status 2, 3, 6), else PREV.
    VMCall Sub_BTL_RecordLine
    WordSetNumber 1, VAR_BT_LAST_STREAK_LV100, 4
    WordSetNumber 2, VAR_BT_RECORD_LV100, 4
    WorkSet BT_T1, VAR_BT_STATUS_LV100
    WorkSetConst BT_T2, 44
    VMCall Sub_BTL_RecordLine
    InfoMsgClose
    h_release
Sub_BTL_RecordLine:
    h_goto_if_eq BT_T1, BT_ST_RESTED, L_BTL_RLShow
    h_goto_if_eq BT_T1, BT_ST_WON_SAVED, L_BTL_RLShow
    h_goto_if_eq BT_T1, BT_ST_PRIZE, L_BTL_RLShow
    WorkAdd BT_T2, 1
L_BTL_RLShow:
    SystemMsg BT_T2, 2
    LastKeyWait
    VMReturn

    .balign 4, 0
BTL_MvUp3:                              // BattleTower_Lobby_Movement_160693
    walk_up 3
    step_end
BTL_MvRecepIn:                          // _160697
    walk_up
    set_invisible
    step_end
BTL_MvPlayerIn:                         // _16069A
    walk_up 2
    set_invisible
    step_end
