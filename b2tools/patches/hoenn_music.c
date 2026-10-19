/* Hoenn or Unova music, Birch's third question (notes/MUSIC.md): code in ITCM, compiled and linked by
 * b2tools/patches/hoenn_music.py (which has the hook sites and writes hoenn_music_data.h).
 *
 * The choice: the options u16 at the start of the trainer-data save block (SaveControl block 27), bit 13 (fairy_core's
 * Intro_SetConfigBit writes it in the intro; 0 for a new game and every older save). 1 = Hoenn's songs:
 *   - zones: GetRegularZoneBGMID (arm9 0x020300b0) asks Music_ZoneBGM instead of DecideZoneHeaderBGMID: the zone
 *     header's third BGM field (autumn: free, because the Unova option always takes the second, summer field: the
 *     season is summer unless Birch's seasons answer was YES, patches/hoenn_season.py) holds the zone's Hoenn song;
 *   - every other BGM and jingle: GFL_SndBGMPlayCore (0x02005d98) passes its sequence through Music_Redirect, a
 *     Unova -> Hoenn table (battles, victories, surf, bike, jingles, Hall of Fame, credits, the stand-ins the story
 *     scripts play); with the Unova option a Hoenn -> stand-in table (for the few songs scripts name directly);
 *   - trainers: GetTrainerClassEyeBGMID (0x02030794: the music when a trainer spots you) and the trainer and wild
 *     battle music (ov036 EventBattleCall_DecideEnvTrainer / _DecideEnvWild, called from ov012) per trainer class and
 *     per species (Ruby/Sapphire rules: pokeruby battle_setup.c, pokemon_3.c GetMUS_ForBattle);
 *   - victories: the class of the last trainer battle picks the victory theme (Black 2 gives gym leaders and the
 *     Elite Four the same one); after a capture (the capture jingle, then SEQ_BGM_WIN1) Sapphire's mus_caught;
 *   - the evolution / egg-hatching scenes and the field's faded BGM changes load their songs through func_02006424
 *     (arm9, a threaded load that bypasses GFL_SndBGMPlayCore): the same redirect at its entry (Music_LoadShim); so do
 *     GFL's BGM2 play (the credits, the Game Freak logo) and its faded change request (func_02005e08);
 *   - zones with Sapphire's own rules (pokeruby overworld.c GetLocationMusic): the Kyogre / Groudon weather song in the
 *     crisis zones while FLAG_SYS_WEATHER_CTRL is set, Mt. Chimney's song in the Weather Institute while the team holds
 *     it (VAR_WEATHER_INSTITUTE_STATE 0);
 *   - the title: Black 2 plays its title song as a stream (GFL_SndStream*, used by the title alone): with the Hoenn
 *     option the stream calls play Sapphire's title song on the BGM player instead (Init decides, Stop ends it);
 *   - scripts: BGMIsPlaying (s009B) ignores its BGM argument in Black 2; with MUSIC_QUERY it answers the music option
 *     (src/include/hoenn_music.inc h_playbgm_hoenn: Sapphire's songs that Black 2 has no stand-in for).
 * Nothing here runs with the Unova option except the table lookups (no change of Black 2's behaviour). */
typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef int s32;

#define FN(type, addr) ((type)((addr) | 1))
#define SaveControl_GetBlockPtr          FN(u8 *(*)(void *, u32), 0x02007448)
#define DecideZoneHeaderBGMID            FN(u32 (*)(u32, u32), 0x02018968)
#define TrainerData_GetParam             FN(u32 (*)(u32, u32), 0x020304e0)
#define EventBattleCall_DecideEnvWild    FN(void (*)(u32, u32, u32, u32, u32, u32 *, u16 *), 0x021c5ef8)
#define EventBattleCall_DecideEnvTrainer FN(void (*)(u32, u32, u32 *, u16 *), 0x021c618c)
#define GameData_GetEventWork            FN(void *(*)(void *), 0x02017394)
#define EventWork_FlagGet                FN(u32 (*)(void *, u32), 0x020191ac)
#define EventWork_GetWkPtr               FN(u16 *(*)(void *, u32), 0x02019294)
#define GFL_SndBGMPlay                   FN(void (*)(u32, u32), 0x02005df4)
#define GFL_SndBGMFadeOut                FN(void (*)(u32), 0x02005ea0)
#define GFL_SndBGMIsFading               FN(u32 (*)(void), 0x02005ec0)
#define GFL_SndBGMIsPlaying              FN(u32 (*)(void), 0x02005fa8)
#define GFL_SndBGMStopNow                FN(void (*)(void), 0x02005d8c)     /* ResetBGMChange + StopBGM (+ unload) */
#define VM_Read16                        FN(u32 (*)(void *), 0x020159e8)
#define ResetBGMChange                   FN(void (*)(void), 0x02006000)
#define RequestBGMChange                 FN(void (*)(u32, u32, s32, s32), 0x02005fe0)
#define SndStrm_FadeStop                 FN(void (*)(void *, u32), 0x0206dd00)  /* GFL_SndStreamStop/FadeStop's call */
#define SndStrm_IsPlaying                FN(u32 (*)(void *), 0x0206dd2c)
#define g_SndStream                      (*(void **)0x02140f5c)               /* GFL's stream work (0 when none) */
#define g_SaveControlWork                (*(void **)0x02140f60)
#define TRAINER_CLASS_EYE_BGM            ((const u8 *)0x02092396)   /* TRAINER_CLASS_RESOURCES + 2, 4 bytes per class */
#define CFG_HOENN_MUSIC                  (1u << 13)

#include "hoenn_music_data.h"   /* kRedirect, kReverse, kEye, kBattle, kVictory, kWild, kWin, N_CLASSES, the zone rules,
                                   TITLE_SONG, AFTER_CATCH_SONG, SEQ_POKEGET, SEQ_WIN1, MUSIC_QUERY */

/* the last trainer battle's class (0xffff after a wild battle): a word in the code's own ITCM, written at runtime */
__asm__(".text\n\t.align 2\n\t.global gMusicLastClass\ngMusicLastClass:\n\t.word 0xffff\n");
extern volatile u32 gMusicLastClass;
/* 1 after the capture jingle (the next SEQ_BGM_WIN1 is the capture's), the title song on the BGM player, the last
 * BGMIsPlaying argument */
__asm__(".text\n\t.align 2\n\t.global gMusicCaught\ngMusicCaught:\n\t.word 0\n\t.global gMusicTitle\ngMusicTitle:\n\t.word 0\n"
        "\t.global gMusicQuery\ngMusicQuery:\n\t.word 0\n");
extern volatile u32 gMusicCaught, gMusicTitle, gMusicQuery;

u32 Music_IsHoenn(void) {
#ifdef MUSIC_FORCE
    return MUSIC_FORCE;
#else
    void *sc = g_SaveControlWork;
    if (!sc) return 0;
    return (*(const u16 *)SaveControl_GetBlockPtr(sc, 27) & CFG_HOENN_MUSIC) ? 1 : 0;
#endif
}

static u32 in_list(const u16 *t, u32 n, u32 v) {
    u32 i;
    for (i = 0; i < n; i++)
        if (t[i] == v) return 1;
    return 0;
}

/* Sapphire's zone rules (pokeruby overworld.c GetLocationMusic); 0 = the zone's own song */
static u32 zone_rule(void *gd, u32 zone) {
    void *ew;
    if (!gd) return 0;
    ew = GameData_GetEventWork(gd);
    if (CRISIS_SONG != 0 && in_list(kCrisisZones, N_CRISIS, zone) && EventWork_FlagGet(ew, CRISIS_FLAG)) return CRISIS_SONG;
    if (INSTITUTE_SONG != 0 && in_list(kInstituteZones, N_INSTITUTE, zone) && *EventWork_GetWkPtr(ew, INSTITUTE_VAR) == 0)
        return INSTITUTE_SONG;
#ifdef EM_ZONE_RULES
    /* Emerald (emerald_ch10, 2026-10-12; pokeemerald overworld.c ShouldLegendaryMusicPlayAtLocation and
     * NoMusicInSootopolisWithLegendaries): Routes 129-131 join the crisis song from VAR_SOOTOPOLIS_CITY_STATE 4, and
     * Sootopolis is silent while VAR_SKY_PILLAR_STATE is 1 (Rayquaza on its way) */
    if (CRISIS_SONG != 0 && in_list(kLateCrisisZones, N_LATE_CRISIS, zone) && EventWork_FlagGet(ew, CRISIS_FLAG)
        && *EventWork_GetWkPtr(ew, LATE_CRISIS_VAR) >= 4) return CRISIS_SONG;
    if (in_list(kSilentZones, N_SILENT, zone) && *EventWork_GetWkPtr(ew, SILENT_VAR) == 1) return SILENT_SONG;
#endif
#ifdef EM_MAGMA_RULE
    /* Emerald (emerald_ch9_mirage, 2026-10-12; pokeemerald overworld.c IsInflitratedSpaceCenter): Mossdeep's Space Center 1F and
     * 2F play mus_encounter_magma while VAR_MOSSDEEP_CITY_STATE is 1 or 2 (Team Magma holds it) */
    if (in_list(kMagmaZones, N_MAGMA, zone)) {
        u32 v = *EventWork_GetWkPtr(ew, MAGMA_VAR);
        if (v == 1 || v == 2) return MAGMA_SONG;
    }
#endif
    return 0;
}

/* replaces GetRegularZoneBGMID (gamedata, zone, season): its entry jumps here */
u32 Music_ZoneBGM(void *gd, u32 zone, u32 season) {
    u32 bgm;
    zone &= 0xffff;
    if (Music_IsHoenn()) {
        bgm = zone_rule(gd, zone);
        if (!bgm) bgm = DecideZoneHeaderBGMID(zone, 2);
        if (bgm) return bgm;
    }
    /* the summer field in every season (Birch's seasons question, notes/SEASONS.md): the autumn field holds the Hoenn
     * song, the spring and winter fields the reused Unova zone's own; with the summer lock season is 1 anyway */
    (void)season;
    return DecideZoneHeaderBGMID(zone, 1);
}

static u32 lookup(const u16 *t, u32 n, u32 seq) {
    u32 i;
    for (i = 0; i < n; i++)
        if (t[2 * i] == seq) return t[2 * i + 1];
    return seq;
}

u32 Music_Redirect(u32 seq) {
    u32 i, cls, caught;
    if (!Music_IsHoenn()) return lookup(kReverse, N_REVERSE, seq);
    caught = gMusicCaught;
    gMusicCaught = seq == SEQ_POKEGET;
    if (AFTER_CATCH_SONG != 0 && seq == SEQ_WIN1 && caught) return AFTER_CATCH_SONG;
    for (i = 0; i < N_WIN; i++) {
        if (kWin[i] == seq) {
            cls = gMusicLastClass;
            if (cls < N_CLASSES && kVictory[cls]) return kVictory[cls];
            break;
        }
    }
    return lookup(kRedirect, N_REDIRECT, seq);
}

/* GFL_SndBGMPlayCore: `adds r4, r0, #0; adds r5, r1, #0` (the sequence and the channel mask) -> bl here */
__attribute__((naked)) void Music_PlayCoreShim(void) {
    __asm__ volatile("push {r1, lr}\n\tbl Music_Redirect\n\tadds r4, r0, #0\n\tpop {r1}\n\tadds r5, r1, #0\n\tpop {pc}\n");
}

/* func_02006424 (seq, step, start), the threaded BGM load of the evolution and egg scenes and of the field's faded BGM
 * changes: `adds r5, r0, #0; adds r4, r1, #0` -> bl here (r2, the start flag, is read after) */
__attribute__((naked)) void Music_LoadShim(void) {
    __asm__ volatile("push {r1, r2, r3, lr}\n\tbl Music_Redirect\n\tadds r5, r0, #0\n\tpop {r1, r2, r3}\n\tadds r4, r1, #0\n"
                     "\tpop {pc}\n");
}

/* GFL's BGM2 play (arm9 0x02005e10, named GFL_SndBGMStop in the decomp: the credits' SEQ_BGM_ENDING from ov012's game
 * clear, the Game Freak logo's SEQ_BGM_GF_LOGO from ov264): `adds r4, r0, #0; bl ResetBGMChange` -> `bl here;
 * adds r4, r0, #0` */
u32 Music_Bgm2Redirect(u32 seq) {
    ResetBGMChange();
    return Music_Redirect(seq);
}

/* func_02005e08 (a faded BGM change, ov028 / ov324): its `bl RequestBGMChange` -> here */
void Music_RequestChange(u32 seq, u32 mask, s32 fade_out, s32 fade_in) {
    RequestBGMChange(Music_Redirect(seq), mask, fade_out, fade_in);
}

/* ---- the title (ov162 is the only user of GFL's stream): each GFL_SndStream* entry jumps to its Music_Stream* */
/* the original first instructions of GFL_SndStreamInit / GFL_SndStreamPlay, then back into them */
__attribute__((naked)) void Music_StreamInitOrig(u32 heap) {
    __asm__ volatile("push {r3, r4, lr}\n\tsub sp, #4\n\tmovs r1, #0x41\n\tstr r1, [sp]\n\tldr r3, 1f\n\tbx r3\n"
                     "\t.p2align 2\n1:\t.word 0x02006fd1\n");
}
__attribute__((naked)) void Music_StreamPlayOrig(u32 stream) {
    __asm__ volatile("push {r4, r5, r6, lr}\n\tadds r5, r0, #0\n\tldr r0, 1f\n\tldr r0, [r0]\n\tldr r1, 2f\n\tbx r1\n"
                     "\t.p2align 2\n1:\t.word 0x02140f5c\n2:\t.word 0x0200705d\n");
}

void Music_StreamInit(u32 heap) {
    gMusicTitle = (TITLE_SONG != 0 && Music_IsHoenn()) ? 1 : 0;
    if (!gMusicTitle) Music_StreamInitOrig(heap);       /* Hoenn: no stream at all (g_SndStream stays 0) */
}

void Music_StreamPlay(u32 stream) {
    if (gMusicTitle) { GFL_SndBGMPlay(TITLE_SONG, 0xffff); return; }
    Music_StreamPlayOrig(stream);
}

void Music_StreamFadeStop(u32 frames) {
    if (gMusicTitle) { GFL_SndBGMFadeOut(frames); return; }
    SndStrm_FadeStop(g_SndStream, frames);
}

void Music_StreamStop(void) {
    if (gMusicTitle) { GFL_SndBGMStopNow(); gMusicTitle = 0; return; }
    SndStrm_FadeStop(g_SndStream, 0);
}

u32 Music_StreamIsPlaying(void) {
    if (gMusicTitle) return GFL_SndBGMIsFading() ? 1 : 0;
    return SndStrm_IsPlaying(g_SndStream) ? 1 : 0;
}

/* ---- scripts: s009B_BGMIsPlaying (ov036) reads a BGM it never uses; MUSIC_QUERY asks for the music option */
u32 Music_ScrRead16(void *vm) {
    u32 v = VM_Read16(vm);
    gMusicQuery = v;
    return v;
}

u32 Music_ScrBGMIsPlaying(void) {
    if (gMusicQuery == MUSIC_QUERY) { gMusicQuery = 0; return Music_IsHoenn(); }
    return GFL_SndBGMIsPlaying();
}

/* replaces GetTrainerClassEyeBGMID */
u32 Music_EyeBGM(u32 cls) {
    if (Music_IsHoenn() && cls < N_CLASSES && kEye[cls]) return kEye[cls];
    return *(const u16 *)(TRAINER_CLASS_EYE_BGM + 4 * cls);
}

/* the two calls of EventBattleCall_DecideEnvWild in ov012 */
void Music_DecideEnvWild(u32 species, u32 form, u32 a2, u32 a3, u32 a4, u32 *enceff, u16 *bgm) {
    u32 i;
    EventBattleCall_DecideEnvWild(species, form, a2, a3, a4, enceff, bgm);
    gMusicLastClass = 0xffff;
    if (!Music_IsHoenn()) return;
    for (i = 0; i < N_WILD; i++)
        if (kWild[2 * i] == species) { *bgm = kWild[2 * i + 1]; return; }
}

/* the call of EventBattleCall_DecideEnvTrainer in ov012 */
void Music_DecideEnvTrainer(u32 trainer, u32 field, u32 *enceff, u16 *bgm) {
    u32 cls;
    EventBattleCall_DecideEnvTrainer(trainer, field, enceff, bgm);
    cls = TrainerData_GetParam(trainer, 1);
    gMusicLastClass = cls;
    if (Music_IsHoenn() && cls < N_CLASSES && kBattle[cls]) *bgm = kBattle[cls];
}
