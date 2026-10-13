// Pokémon Emerald NDS, Chapter 10 helpers (emerald_ch10, 2026-10-12): the camera, the crisis weather, the legends' songs.
// Reusable by any Emerald scene (Magma Hideout's Groudon, Marine / Terra Cave ...). Emerald builds only; include after
// "hoenn_story.inc" (and "scenes/ch10_lib.inc" for c10_lock / c10_shake). Emits no code by itself.
#ifndef EM_CH10_LIB_INC
#define EM_CH10_LIB_INC

// ---- the camera (pokeemerald special SpawnCameraObject + applymovement LOCALID_CAMERA ... + RemoveCameraObject) ------
// Black 2's own event camera (0240.s, 0382.s): EvCameraInit, EvCameraUnbind, then EvCameraMoveTo pitch, yaw, distance,
// x, y, z, frames (fx32 world position of the point looked at; 9688 / 0 / 0xed000 = the field camera's own angle and
// distance, 96 of Black 2's 120 uses), EvCameraWait; back with EvCameraMoveToDefault frames, EvCameraWait, EvCameraRebind,
// EvCameraEnd. Emerald's camera object walks (walk_slow_* = 32 Gen 3 frames a tile, walk_* 16): one Black 2 field frame
// is two Gen 3 frames, so a pan of n slow tiles takes 16 n frames here.
// x, z: tiles of the zone's matrix (a warp-only map: its group's matrix, b2tools/world.py); h: the ground height in units.
    .macro em_camera_start
    EvCameraInit
    EvCameraUnbind
    .endm
    .macro em_camera_to x, z, h, frames
    EvCameraMoveTo 9688, 0, 0xed000, (((\x) * 16 + 8) << 12), ((\h) << 12), (((\z) * 16 + 8) << 12), \frames
    EvCameraWait
    .endm
    .macro em_camera_end frames               // back to the player (RemoveCameraObject at the player's place)
    EvCameraReturn \frames
    EvCameraWait
    EvCameraRebind
    EvCameraEnd
    .endm
    .macro em_camera_back x, z, h, frames     // back to the player's tile (x, z, h as em_camera_to), then bound to him again
    EvCameraMoveTo 9688, 0, 0xed000, (((\x) * 16 + 8) << 12), ((\h) << 12), (((\z) * 16 + 8) << 12), \frames
    EvCameraWait
    EvCameraRebind
    EvCameraEnd
    .endm

// ---- the camera shakes (special ShakeCamera: VAR_0x8004 vertical pan, 0x8005 horizontal pan, 0x8006 shakes, 0x8007
// delay) as Black 2's EvCameraShake (the Sealed Chamber's, STORY_SPECIALS 54/55) with Emerald's strength sound
// (ShakeCamera plays SE_M_STRENGTH: scenes/ch10_lib.inc C10_SE_SHAKE); amp ~ 4 x the larger pan, n = the shakes
    .macro em_shake amp, n
    SEPlay C10_SE_SHAKE
    EvCameraShake \amp, 0, 3, \n, 1, 0, 1, 5
    VMSleep ((\n) * 3)
    .endm
// The same while the camera is moved away from the player (em_camera_start ... em_camera_end): Black 2's EvCameraShake
// works on the bound camera only (no Black 2 script shakes an unbound one; tried here: the view lost the map for good), so
// the shake is the camera's own point moved up and down by amp units, n times (one field frame each)
    .macro em_shake_at x, z, h, n, amp=3
    SEPlay C10_SE_SHAKE
    .rept \n
    EvCameraMoveTo 9688, 0, 0xed000, (((\x) * 16 + 8) << 12), ((\h) << 12), (((\z) * 16 + 8 + (\amp)) << 12), 1
    EvCameraWait
    EvCameraMoveTo 9688, 0, 0xed000, (((\x) * 16 + 8) << 12), ((\h) << 12), (((\z) * 16 + 8 - (\amp)) << 12), 1
    EvCameraWait
    .endr
    EvCameraMoveTo 9688, 0, 0xed000, (((\x) * 16 + 8) << 12), ((\h) << 12), (((\z) * 16 + 8) << 12), 1
    EvCameraWait
    .endm

// ---- the crisis weather (b2tools/patches/emerald_mech.c EM_ZoneWeather): FieldSetWeather 0xFFFF asks the zone's weather
// again, which the crisis rule answers from FLAG_SYS_WEATHER_CTRL, VAR_SOOTOPOLIS_STATE and VAR_SKY_PILLAR_STATE (Emerald's
// setweather WEATHER_ABNORMAL / WEATHER_DOWNPOUR + doweather after the script changed them); fade 0, at once 1
    .macro em_weather_zone fast=0
    FieldSetWeather 0xFFFF, \fast
    .endm
    .macro em_weather_none                    // setweather WEATHER_NONE, doweather
    FieldSetWeather 0, 0
    .endm

// ---- songs (data/emerald/hoenn_music.json slots; Hoenn music answer only, as h_playbgm_hoenn) -------------------------
#define MUS_EM_RAYQUAZA_APPEARS SEQ_SE_SW_KYUREON_03_01 // mus_rayquaza_appears
#define MUS_EM_ABNORMAL_WEATHER SEQ_SE_SW_KYUREON_02_09 // mus_abnormal_weather

// ---- species ------------------------------------------------------------------------------------------------------
#define EM_RAYQUAZA_LEVEL 78                    // Emerald 70 on the scaled curve (scenes/SkyPillar_Top.inc SP_RAYQUAZA_LEVEL)
#endif
