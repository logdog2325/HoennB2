// Sapphire's Common_EventScript_SetLegendaryWeather (data/event_scripts.s: `setweather WEATHER_RAIN_HEAVY` for Sapphire,
// WEATHER_DROUGHT for Ruby), called by the zone init (ON_TRANSITION) of every outdoor map the Kyogre / Groudon crisis
// reaches (Lilycove, Mossdeep, Routes 124-128, Sootopolis, Ever Grande) while FLAG_SYS_WEATHER_CTRL is set.
//
// What Black 2 can do (chapter Ch10, ch10 agent 2026-10-07; read from the decomp and tested in the emulator):
//   - FieldSetWeather a0, a1 (field command 310, ov012 s0136_FieldSetWeather 0x021611e0, no Black 2 script uses it):
//     a0 = weather id (0xFFFF = the zone's own), a1 = 1: at once / 0: fading. It stores the id as the save's "now
//     weather" and tells the weather system to change. Weather ids (ov036 table 0x021cfb6c, tested on Littleroot):
//     0 sunny, 1 snow, 2 rain, 3 sandstorm, 4/5 snow variants, 6 THUNDERSTORM (rain, dark sky, lightning), 7 heavy rain,
//     8 diamond dust, 9-14 fog/haze/cloud kinds.
//   - BUT it is not allowed in a zone init (EVCMD_PERM_TABLE 0x0216b1f0 byte 3 = levels 0-1 only: a forbidden command in
//     a zone init hangs the game), and every zone change resets the saved weather to the zone's own (ResetWeather,
//     arm9 0x02032f3c, after the zone init). So a script cannot keep a weather over a region.
//   - Done instead: the `weather` patch (b2tools/patches/weather.py) makes Black 2's weather lookup of a zone return the
//     thunderstorm (id 6) for the crisis zones while FLAG_SYS_WEATHER_CTRL is set. The flag is Sapphire's own: Seafloor
//     Cavern Room 9 sets it (Kyogre wakes), the Cave of Origin B4F clears it (Kyogre calmed). Nothing is left for a
//     script to do, so this is Sapphire's call kept as a harmless no-op: a zone init may call it at its level.
#ifndef COMMON_LEGENDARY_WEATHER_INC
#define COMMON_LEGENDARY_WEATHER_INC
Common_SetLegendaryWeather:
    VMReturn
#endif
