# Camera project — final report (DRAFT, 2026-10-30)

Status: **draft before flashing.** Camera v13 runs on the phone (app update + module copy for the next boot) and is in the ROM
payload. To finish: P9 build (needs ~1 GB more laptop space), flash (owner approval), regression after flashing, release notes.

## 1. What changed for the owner (native camera, MiuiCamera 6.7 on the Marble profile)

| Area | Before (port as received) | Now (camera v13) | Build |
|---|---|---|---|
| Watermark | "XIAOMI 17 PRO" | "POCO F4 5G" | v1 |
| Filters | no Leica looks | Leica Vivid / Natural / Chrome / … | v3 |
| Short video | clips could not be finished or saved | saves; the two "Short video" modes have distinct names | v5, v6 |
| VLOG | app crash (illegal config item 172) | works | v7 |
| Night shots left as 16 MB grey files | yes (abandoned parallel shots) | trimmed to a normal preview | v8 |
| Video bitrate | 4K60 50 Mbit/s, 60 fps used 30 fps values | 4K60 100 Mbit/s, 1080p60 40 Mbit/s HEVC | v9 |
| Selfies | 1600x1200, processed at 800x600, wrong colours | 20 MP 5184x3904, correct colours | v11 |
| **Ultra-wide (0.6x) photos** | **never saved** (app crashed in distortion correction; 16 MB placeholder kept) | save at 3264x2448 (distortion correction off by default) | v12 |
| **Zoom photos 2x / 5x** | **not zoomed** (1x framing, noisy, unmerged SR frame) | correctly cropped, normal colour | v13 |

All patches: `tools/re/camera_watermark_patch.sh` (rebuilds every version from the stock app). Profile values: `01_APP_OS_LAYER.md` §7.

## 2. Measured state (stand, indoor window light, 2026-10-30)
* Back camera sheet (0.6x, 1x, 2x, 5x, Ultra HD, LMC): `MODE_TEST_RESULTS.md` "P0 baseline sheet".
* Pre-flash regression v13: 16 modes open, 0 crashes; front 20 MP; 1080p60 HEVC 39.8 Mbit/s (`MODE_TEST_RESULTS.md`).
* Heat (10 min, charging): 1080p30 flat, 1080p60 +1 °C, 4K30 +2/+4 °C, 4K60 +5/+8 °C (battery/board), no throttling.
* Camera load: GPU 3-4 % (max 12 %), CPU 28-45 % → room for our own processing stage.
* Calibration of this unit: intact (EEPROM checksums OK, factory dual-camera file + backup identical).

## 3. Still open (honest list)
| Issue | Cause found | Workaround | Next step |
|---|---|---|---|
| **Night mode photos are purple** | HAL SuperNight pipeline gives no output buffer; app graph only copies → unprocessed frame saved | use **LMC** in the dark | HAL-level (CHI SuperNight node) |
| Photo mode never switches to night by itself | `o.h0()` hard-wired; HAL lacks in-Photo night; forcing it gives streaks | LMC / Night mode after fix | depends on the Night fix |
| Back Portrait crashes | MegEngine GPU engine vs the port's Adreno driver (same engine as the UW crash) | **LMC Portrait** | driver-level |
| Native photos softer than LMC (4-6x less detail) | not AIIE, not MFNR, not snapshot ANR (tested); ISP NR/sharpening strength | **LMC** for detail | own sharpening stage (L3) or Chromatix field mapping |
| HDR super-resolution (hdsr) | app needs a HAL vendor tag that does not exist | — | closed |
| HDR10 video | HAL offers no 10-bit streams | — | closed |

## 4. Recommended daily use
* **LMC 8.4 (`POCO-F4-ONE.xml`)**: default for photos, especially low light and Portrait.
* **Native camera v13**: video (4K60 100 Mbit/s, OIS), 0.6x / 2x / 5x, selfies, filters, Short video / VLOG.
* Native Night mode: avoid until fixed.

## 5. Rollback
* Camera: `pm uninstall-system-updates com.android.camera` removes the v13 app update; the module copy can be replaced with v11
  (`~/camera_builds/MiuiCamera_v11.apk`, pendrive `camera_project/camera_builds/`) and the module disabled with `ksud module disable`.
* ROM payload: previous product image kept on the pendrive before flashing (P9 plan).

## 6. To complete this report after flashing
- [ ] P9 build + EROFS symlink check + sha256
- [ ] Flash (owner approval), module disabled at flash
- [ ] Regression after flash (modes, back/front, 4K60/1080p, LMC, heat, crash buffer, SELinux)
- [ ] Release notes with the table in §1
