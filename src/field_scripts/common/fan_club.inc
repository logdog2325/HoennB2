// The Lilycove Pokémon Trainer Fan Club's state (pokeruby src/field_specials.c:1949-2212, ch8a agent 2026-10-07).
// Include at the END of your zone script (after the scripts); call with VMCall. notes/STORY_COMMON.md.
// Sapphire keeps it in VAR_FANCLUB_UNKNOWN_1 (bits 0-6 counter, bit 7 "started", bits 8-15 the eight fans who moved to
// the player) and VAR_FANCLUB_UNKNOWN_2 (play-time hours of the last update). Here: FC_COUNT = VAR_FANCLUB_UNKNOWN_1
// keeps the counter and bit 7; FC_MOVED = VAR_FANCLUB_UNKNOWN_2 is the byte of the eight fans (bit k = the fan whose
// Sapphire specialvar 0x8004 is 8 + k: 0 Lass, 1 Pokéfan M, 2 Little Girl, 3 Ninja Boy, 4 Boy, 5 Man, 6 Woman,
// 7 Old Lady). Black 2's script constants cannot be 0x4000 or more, so Sapphire's 16-bit mask does not fit one work.
//   Sub_FanClub_GameClear   UpdateTrainerFanClubGameClear: the Hall of Fame (Ch11) calls it once the game is cleared:
//                           the four hidden fans appear, three fans (Lass, Little Girl, Man) are the player's,
//                           VAR_LILYCOVE_FAN_CLUB_STATE = 1 (the Fan Club scene). Does nothing the second time.
//   Sub_FanClub_CountWin    sub_810FF60 (special): a won Elite Four / Battle Tower battle; 0x8004 = which battle
//                           (0..3: Sapphire's table {2,1,2,1} of counter points; Drake's room, Battle Tower rooms).
//                           Only while VAR_LILYCOVE_FAN_CLUB_STATE is 2.
//   Sub_FanClub_NumMoved    GetNumMovedLilycoveFanClubMembers -> FC_T1
//   Sub_FanClub_AddFan / Sub_FanClub_RemoveFan   sub_810FB9C / sub_810FC18 (a random fan joins / leaves)
// Not ported: UpdateMovedLilycoveFanClubMembers' decay by play time (12 play hours per fan once more than 4 fans moved:
// Black 2 scripts cannot read the play time) and the link-battle result updates (sub_810FEFC: no link battles).
#ifndef COMMON_FAN_CLUB_INC
#define COMMON_FAN_CLUB_INC
#define FC_COUNT VAR_FANCLUB_UNKNOWN_1
#define FC_MOVED VAR_FANCLUB_UNKNOWN_2
#define FC_T1 0x803C
#define FC_T2 0x803D
#define FC_T3 0x803E

    .macro fc_get_bit k, dst            // dst = 1 when fan k (0-7) has moved to the player's table
    WorkSet \dst, FC_MOVED
    .if \k > 0
    WorkDiv \dst, (1 << \k)
    .endif
    WorkAnd \dst, 1
    .endm
    .macro fc_set_bit k
    WorkOr FC_MOVED, (1 << \k)
    .endm
    .macro fc_clear_bit k
    fc_get_bit \k, FC_T3
    WorkCmpConst FC_T3, 0
    VMJumpIf CMP_EQ, .Lfccb\@
    WorkSub FC_MOVED, (1 << \k)
.Lfccb\@:
    .endm

Sub_FanClub_GameClear:
    WorkSet FC_T1, FC_COUNT
    WorkAnd FC_T1, 128
    WorkCmpConst FC_T1, 0
    VMJumpIf CMP_NE, L_FanClub_GCDone   // bit 7 set: already started
    WorkOr FC_COUNT, 128                // sub_810FF48
    WorkOr FC_MOVED, 0x25               // sub_810FD80: Lass (bit 0), Little Girl (bit 2), Man (bit 5)
    FlagReset FLAG_HIDE_FANCLUB_OLD_LADY
    FlagReset FLAG_HIDE_FANCLUB_BOY
    FlagReset FLAG_HIDE_FANCLUB_LITTLE_BOY
    FlagReset FLAG_HIDE_FANCLUB_LADY
    WorkSetConst VAR_LILYCOVE_FAN_CLUB_STATE, 1
L_FanClub_GCDone:
    VMReturn

Sub_FanClub_NumMoved:                   // FC_T1 = how many of the eight fans are the player's
    WorkSetConst FC_T1, 0
    WorkSet FC_T2, FC_MOVED
    .rept 8
    WorkSet FC_T3, FC_T2
    WorkAnd FC_T3, 1
    WorkAdd FC_T1, FC_T3
    WorkDiv FC_T2, 2
    .endr
    VMReturn

Sub_FanClub_AddFan:                     // sub_810FB9C: walk the fans in order; each one not yet the player's joins on a coin flip
    WorkSetConst FC_T2, 0               // retval (the last fan not yet the player's)
    .irp k, 0, 1, 2, 3, 4, 5, 6, 7
    fc_get_bit \k, FC_T3
    WorkCmpConst FC_T3, 0
    VMJumpIf CMP_NE, .Lfcadd_\k
    WorkSetConst FC_T2, \k
    Random FC_T3, 2
    WorkCmpConst FC_T3, 0
    VMJumpIf CMP_EQ, .Lfcadd_\k
    fc_set_bit \k
    VMReturn
.Lfcadd_\k:
    .endr
    .irp k, 0, 1, 2, 3, 4, 5, 6, 7      // nobody joined on a flip: the last candidate does
    WorkCmpConst FC_T2, \k
    VMJumpIf CMP_NE, .Lfcaddfin_\k
    fc_set_bit \k
.Lfcaddfin_\k:
    .endr
    VMReturn

Sub_FanClub_RemoveFan:                  // sub_810FC18: Sapphire's order Lass, Man, Woman, Ninja Boy, Little Girl, Boy, Old Lady, Pokéfan M
    VMCall Sub_FanClub_NumMoved
    WorkCmpConst FC_T1, 1
    VMJumpIf CMP_EQ, L_FanClub_RFDone   // one fan is always left
    WorkSetConst FC_T2, 0
    .irp k, 0, 5, 6, 3, 2, 4, 7, 1
    fc_get_bit \k, FC_T3
    WorkCmpConst FC_T3, 0
    VMJumpIf CMP_EQ, .Lfcrem_\k
    WorkSetConst FC_T2, \k
    Random FC_T3, 2
    WorkCmpConst FC_T3, 0
    VMJumpIf CMP_EQ, .Lfcrem_\k
    fc_clear_bit \k
    VMReturn
.Lfcrem_\k:
    .endr
    .irp k, 0, 1, 2, 3, 4, 5, 6, 7
    WorkCmpConst FC_T2, \k
    VMJumpIf CMP_NE, .Lfcremfin_\k
    fc_clear_bit \k
.Lfcremfin_\k:
    .endr
L_FanClub_RFDone:
    VMReturn

Sub_FanClub_CountWin:                   // sub_810FB10 (0x8004 = 0..3)
    WorkCmpConst VAR_LILYCOVE_FAN_CLUB_STATE, 2
    VMJumpIf CMP_NE, L_FanClub_CWDone
    WorkSetConst FC_T2, 2               // gUnknown_083F8404 = {2, 1, 2, 1}
    WorkCmpConst 0x8004, 1
    VMJumpIf CMP_EQ, L_FanClub_CWOne
    WorkCmpConst 0x8004, 3
    VMJumpIf CMP_NE, L_FanClub_CWAdd
L_FanClub_CWOne:
    WorkSetConst FC_T2, 1
L_FanClub_CWAdd:
    WorkSet FC_T1, FC_COUNT
    WorkAnd FC_T1, 127
    WorkAdd FC_T1, FC_T2                // counter + points
    WorkCmpConst FC_T1, 20
    VMJumpIf CMP_LT, L_FanClub_CWSmall
    VMCall Sub_FanClub_NumMoved         // FC_T1 = fans so far
    WorkCmpConst FC_T1, 3
    VMJumpIf CMP_GE, L_FanClub_CWKeep
    VMCall Sub_FanClub_AddFan           // fewer than 3 fans: one joins, the counter starts again
    WorkAnd FC_COUNT, 128
    VMReturn
L_FanClub_CWKeep:                       // 3 or more fans: the counter stays at 20
    WorkAnd FC_COUNT, 128
    WorkOr FC_COUNT, 20
    VMReturn
L_FanClub_CWSmall:
    WorkAdd FC_COUNT, FC_T2
L_FanClub_CWDone:
    VMReturn
#endif
