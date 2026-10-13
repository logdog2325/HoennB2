/* Pokémon Emerald NDS: the abnormal weather of the post-game (emerald_ch12_13, 2026-10-12). Emerald builds only:
 * b2tools/patches/emerald_postgame.py compiles this file twice and places the two parts over Black 2 code no Hoenn zone
 * reaches (findings in the .py), so it takes no ITCM.
 *
 * pokeemerald (src/field_specials.c CreateAbnormalWeatherEvent, data/scripts/abnormal_weather.inc):
 * VAR_ABNORMAL_WEATHER_LOCATION 1-8 = a Terra Cave spot (Routes 114, 115, 116, 118: drought, a cave mouth in the rock),
 * 9-16 = a Marine Cave spot (Routes 105, 125, 127, 129: downpour, rough water to dive in), 0 = none. Everything here
 * reads that work only; the scripts end the event (1000 steps, Kyogre / Groudon caught or beaten) by setting it to 0
 * (src/field_scripts/scenes/emerald/abnormal_weather.inc).
 *
 * PART_A (arm9, over GetRoute7WeatherIfApplicable + GetBirthdayZoneWeather):
 *   EM_AbnormalWeather(gsys, gd, zone): GetWeatherAll's third question (where Black 2 asked Route 7's weather): the
 *       spot's route gets Sapphire NDS's Kyogre rainstorm (Marine spots) or Ruby NDS's Groudon drought (Terra spots),
 *       the looks the user chose for Emerald's abnormal weather; else 0xFFFF (ask on).
 * PART_B (ov012, over MapReplace_ResolvePatch + MapReplace_GetEventByCond, the same entry address):
 *   EM_ResolvePatch: Black 2's own rule (season, version, the ten map replace events), plus conditions 0x81-0x90: the
 *       entry's other chunk while the abnormal weather is at spot (condition & 0x7F): the open Terra Cave mouth or
 *       the rough water, swapped in when the matrix loads (world.py build_alts, data/emerald/hoenn_world.json). */
typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;

#include "emerald_postgame_data.h"     /* W_LOC, RAIN, DROUGHT, kAwZone, EVENT_TABLE */

/* Black 2's accessors written out (to fit): GameData_GetEventWork = gd +0x1AC, EventWork_GetWkPtr(ew, id) =
   ew + (id - 0x4000) * 2 (arm9 0x02017394, 0x02019294); the GameData = g_GameSystem (arm9 0x021410f4) +28 */
#define LOCATION(gd) (*(const u16 *)(*(u8 **)((u8 *)(gd) + 0x1ac) + (W_LOC - 0x4000) * 2))

#ifdef PART_A
u32 EM_AbnormalWeather(void *gsys, void *gd, u32 zone) {
    u32 s = LOCATION(gd);
    if (s && kAwZone[(s - 1) >> 1] == (zone & 0xffff)) return s > 8 ? RAIN : DROUGHT;
    return 0xffff;
}
#endif

#ifdef PART_B
u32 EM_ResolvePatch(u8 *r, u32 *old, u32 *nw) {
    /* MapReplace (decomp include/field/field_map.h): +12 variables (season, version, versionSeason, events[10]),
       +25 a padding byte (the struct is allocated cleared: 0), +26 the entry (u16 id, u8 kind, u8 condition, u16 values[6]) */
    const u16 *vals = (const u16 *)(r + 30);
    const u8 *t = (const u8 *)EVENT_TABLE;
    u32 cond = r[29], idx;
    *old = vals[0];
    if (cond & 0x80) idx = LOCATION(*(u8 **)(*(u8 **)0x021410f4 + 28)) == (cond & 0x7f);
    else if (cond < 3) idx = r[12 + cond];
    else {
        for (idx = 0; idx < 10 && t[6 * idx] != cond; idx++) ;
        idx = r[15 + idx];                              /* (not found: the padding, 0 = no change; Black 2 read
                                                           events[-1]; every entry of a/0/1/0 has a known event) */
    }
    *nw = vals[idx];
    if (vals[0] == vals[idx]) return 0;
    if (r[28] == 1) return 2;
    return r[28] == 0;
}
#endif
