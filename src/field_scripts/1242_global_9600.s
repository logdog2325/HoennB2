// Global scripts 9600-9602 (a/0/5/6 entry 1242): Black 2's data/field_scripts/1242.s with 9601 (Script_2) rewritten for
// Hoenn by the halloffame agent (2026-10-07). Script_1 (9600, the new-game setup) and Script_3 (9602) are Black 2's, unchanged.
// 9601 = FieldScript_CallPlayerPostHOFSetup: Black 2's EventGameClear runs it (state 10) right before the game-clear save
// (ov295), after the Hall of Fame record screen. Black 2's: heal, respawn at Aspertia's Center, the place Continue loads =
// the player's house in Aspertia (FieldSetNextZone 428 + flag 2405 EVENT_FLAG_CONTINUE_SCRIPT: EventFieldContinue loads
// GameData's next zone instead of the saved position), and on the first clear (flag 2400 unset) ~40 Unova post-game flags,
// works and map replacements (L_06DD) -- not wanted in Hoenn (they would clobber Hoenn story ids and swap Hoenn chunks).
// Hoenn (Sapphire's GameClear special + the Hall of Fame's setrespawn): flag 2400 (FLAG_SYS_GAME_CLEAR, kept: the PWT's right
// desk and our post-game read it), heal, respawn = the player's house, Continue = the player's room (Sapphire's heal
// location of Brendan's / May's 2F (4,2) = room tile (5,3), zones 391 / 393), the player looking down.
#include "asm/field_script.inc"
#include "hoenn.h"
#include "hoenn_story.inc"

    ScriptEntry Script_1
    ScriptEntry Script_2
    ScriptEntry Script_3
    ScriptEntriesEnd

Script_1:
    VMCall L_0024
    VMCall L_0324
    FieldSetTeleportZone 18
    MoneyAdd 3000
    VMHalt

L_0024:
    FlagSet 989
    FlagSet 607
    FlagSet 613
    FlagSet 604
    FlagSet 605
    FlagSet 615
    FlagSet 767
    FlagSet 768
    FlagSet 769
    FlagSet 621
    FlagSet 614
    FlagSet 660
    FlagSet 667
    FlagSet 645
    WorkSetConst 0x4165, 1
    FlagSet 740
    FlagSet 739
    FlagSet 965
    FlagSet 702
    FlagSet 770
    FlagSet 771
    FlagSet 1014
    FlagSet 761
    FlagSet 762
    FlagSet 733
    FlagSet 734
    FlagSet 735
    FlagSet 736
    FlagSet 737
    FlagSet 727
    FlagSet 743
    FlagSet 741
    FlagSet 2430
    FlagSet 730
    FlagSet 996
    FlagSet 724
    FlagSet 723
    FlagSet 722
    FlagSet 721
    FlagSet 746
    FlagSet 751
    FlagSet 1030
    FlagSet 753
    FlagSet 754
    FlagSet 756
    FlagSet 758
    FlagSet 717
    FlagSet 716
    FlagSet 697
    FlagSet 712
    FlagSet 710
    FlagSet 894
    FlagSet 891
    FlagSet 890
    FlagSet 772
    FlagSet 773
    FlagSet 774
    FlagSet 775
    FlagSet 782
    FlagSet 784
    FlagSet 785
    FlagSet 794
    FlagSet 795
    FlagSet 796
    FlagSet 797
    FlagSet 798
    FlagSet 800
    FlagSet 1034
    FlagSet 1010
    FlagSet 792
    FlagSet 805
    FlagSet 808
    FlagSet 985
    FlagSet 1008
    FlagSet 811
    FlagSet 810
    FlagSet 814
    FlagSet 821
    FlagSet 822
    FlagSet 823
    FlagSet 824
    FlagSet 825
    FlagSet 826
    FlagSet 828
    FlagSet 853
    FlagSet 832
    FlagSet 833
    FlagSet 834
    FlagSet 839
    FlagSet 848
    FlagSet 854
    FlagSet 842
    FlagSet 843
    FlagSet 977
    FlagSet 1029
    FlagSet 2560
    FlagSet 855
    FlagSet 857
    FlagSet 856
    FlagSet 859
    FlagSet 860
    FlagSet 861
    FlagSet 862
    FlagSet 863
    FlagSet 864
    FlagSet 865
    FlagSet 866
    FlagSet 895
    FlagSet 896
    FlagSet 878
    FlagSet 880
    FlagSet 886
    FlagSet 888
    FlagSet 889
    FlagSet 968
    FlagSet 969
    FlagSet 1031
    FlagSet 882
    FlagSet 1004
    FlagSet 1003
    FlagSet 1011
    FlagSet 900
    FlagSet 898
    FlagSet 897
    FlagSet 917
    FlagSet 916
    FlagSet 918
    FlagSet 919
    FlagSet 920
    FlagSet 912
    FlagSet 941
    FlagSet 913
    FlagSet 1035
    FlagSet 925
    FlagSet 926
    FlagSet 927
    FlagSet 695
    FlagSet 944
    FlagSet 942
    FlagSet 945
    FlagSet 960
    FlagSet 950
    FlagSet 951
    FlagSet 953
    FlagSet 955
    FlagSet 957
    FlagSet 683
    FlagSet 970
    FlagSet 971
    FlagSet 972
    FlagSet 973
    FlagSet 974
    FlagSet 978
    FlagSet 979
    FlagSet 986
    FlagSet 627
    FlagSet 628
    FlagSet 629
    FlagSet 630
    FlagSet 631
    FlagSet 991
    FlagSet 992
    FlagSet 994
    FlagSet 995
    FlagSet 691
    FlagSet 692
    FlagSet 693
    FlagSet 694
    FlagSet 1007
    FlagSet 1016
    FlagSet 1017
    FlagSet 1018
    FlagSet 1019
    FlagSet 1020
    FlagSet 1021
    FlagSet 1022
    FlagSet 1023
    FlagSet 1028
    FlagSet 1032
    FlagSet 1033
    FlagSet 1037
    FlagSet 1041
    FlagSet 1042
    FlagSet 1043
    FlagSet 1044
    FlagSet 1045
    FlagSet 1046
    FlagSet 1047
    FlagSet 1048
    FlagSet 1049
    FlagSet 1050
    VMReturn

L_0324:
    GameGetVersion 0x8010
    WorkCmpConst 0x8010, 23
    VMJumpIf CMP_EQ, L_033B
    VMJump L_0347

L_033B:
    Cmd_0209 0, 1
    VMJump L_0366

L_0347:
    WorkCmpConst 0x8010, 22
    VMJumpIf CMP_EQ, L_035A
    VMJump L_0366

L_035A:
    Cmd_0209 0, 2
    VMJump L_0366

L_0366:
    TrainerCardGetSex 0x8010
    WorkCmpConst 0x8010, 0
    VMJumpIf CMP_EQ, L_037D
    VMJump L_0389

L_037D:
    Cmd_0209 1, 1
    VMJump L_03A8

L_0389:
    WorkCmpConst 0x8010, 1
    VMJumpIf CMP_EQ, L_039C
    VMJump L_03A8

L_039C:
    Cmd_0209 1, 2
    VMJump L_03A8

L_03A8:
    Cmd_0209 29, 1
    VMReturn

Script_3:
    VMCall L_0024
    FieldSetTeleportZone 3
    FlagSet 106
    FlagSet 2401
    FlagSet 2402
    GiveRunningShoes
    VMHalt

Script_2:
    FlagSet FLAG_SYS_GAME_CLEAR                   // (the Hall of Fame already set it; Black 2's L_06DD sets it on the first clear)
    PokePartyRecoverAll
    FieldSetTeleportZone 1                        // setrespawn: the player's house (Black 2: 18, Aspertia's Pokémon Center)
    h_goto_if_girl L_HOF_May
    FieldSetNextZone 391, 2, 5, 0, 3              // Continue: Brendan's room, looking down (warp direction 2: ConvDirToWarpDir(down))
    VMJump L_HOF_Next
L_HOF_May:
    FieldSetNextZone 393, 2, 5, 0, 3              // Continue: May's room
L_HOF_Next:
    FlagSet 2405                                  // EVENT_FLAG_CONTINUE_SCRIPT: the save keeps that place (ov035 EventFieldContinue)
    VMHalt
    .balign 4, 0
