// halloffame agent (2026-10-07), TEST BUILDS ONLY (HOENN_TEST_CHCREDITS=1): the shots for the credits pictures
// (b2tools/patches/game_clear.py, data/credits/). Littleroot's town sign (stand at (183,366) facing north, press A) visits
// every place of the credits: at each one the player is hidden and Brendan (object code 1), then May (4), stand on the
// player's tile facing down, then nobody; between the three pictures the script waits for A (ABKeyWait), so
// work/agents/halloffame/tools/credits_shots.py takes a screenshot, presses A, and so on. Never assembled into normal builds.
#ifdef HOENN_TEST_CHCREDITS
#ifndef HALLOFFAME_TEST_INC
#define HALLOFFAME_TEST_INC
    .macro hft_place zone, x, z, people=1, y=0
    FadeOutBlack
    FadeWait
    MapChangeCore \zone, \x, \y, \z, 1
    ActorsPauseAll
    ActorCmdExec 255, Mv_HFT_Hide
    ActorCmdWait
    FadeInBlack
    FadeWait
    VMSleep 100                                   // the place-name banner goes away
    .if \people
    ActorNew \x, \z, 1, 240, 1, 0                 // Brendan
    VMSleep 8
    ABKeyWait
    ActorDelete 240
    ActorNew \x, \z, 1, 240, 4, 0                 // May
    VMSleep 8
    ABKeyWait
    ActorDelete 240
    VMSleep 8
    .endif
    ABKeyWait                                     // nobody
    .endm

Test_CreditsShots:                                // credits photos 0-10, the colour picture, photo 11 (data/credits/credits.json)
    hft_place 317, 179, 342                       // 0 Route 101: Prof. Birch's bag and the Zigzagoon (Sapphire (11, 10))
    hft_place 397, 175, 318                       // 1 Oldale Town: the Pokémon Center (7, 18)
    hft_place 439, 103, 301                       // 2 Petalburg City: the Gym (15, 11)
    hft_place 113, 60, 198                        // 3 Rustboro City: Devon Corporation (12, 18)
    hft_place 465, 118, 431                       // 4 Dewford Town: Mr. Briney's dock (10, 11)
    hft_place 448, 260, 342                       // 5 Slateport City: the Mart (12, 22)
    hft_place 406, 263, 208                       // 6 Mauville City (15, 8)
    hft_place 62, 196, 131                        // 7 Lavaridge Town (8, 11)
    hft_place 16, 377, 68                         // 8 Fortree City: the tree houses (9, 8)
    hft_place 96, 555, 140                        // 9 Lilycove City: the Department Store (27, 10)
    hft_place 107, 752, 177                       // 10 Mossdeep City: the Space Center (64, 17)
    hft_place 319, 48, 40, 0                      // the colour picture (nobody): Sootopolis City, the Cave of Origin (30, 19)
    hft_place 389, 177, 363                       // 11 Littleroot Town: home (9, 11)
    FinishAllEvents
    ActorsUnpauseAll
    VMHalt

    .balign 4, 0
Mv_HFT_Hide:
    set_invisible
    step_end
#endif
#endif
