# Camera project — final report (2026-10-31)

Status: **v14 (v13 + Mimoji/Clone/Movie effects hidden) and the PhotoStage app were flashed 2026-10-31 (product only, no wipe; `ROM_HISTORY.md` §12); v13 was flashed 2026-10-30.** It boots in 25 s, 0 crashes, camera works, contacts and call log
intact. Built from `payload_tele` (the shipped 32-bit-capable build; the pure 64-bit Global build failed to boot and is shelved).
Open: owner real-call test (both SIMs), owner look decision, daylight A/B for v14, release tag (see `RELEASE_NOTES_DRAFT.md`), crash analysis of two new mode crashes (`OWNER_TESTS_2026-10-30.md`).
Rollback: `bash secure_build/flash_product_nowipe.sh secure_build/out_tele_T20261026_prev "rollback"` (byte-identical to the previous product).

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
| Native photos softer than LMC (4-6x less detail) | **HAL high-strength noise reduction** (not AF, AIIE, MFNR or ANR); NR off gives LMC-like edges but grain | **LMC** for detail, or the **PhotoStage app** (copy with sharper detail, better tone and colour) | camera v14 = NR off + PhotoStage denoise, after a daylight A/B (owner shots, `OWNER_HELP_NEEDED.md`) |
| HDR super-resolution (hdsr) | app needs a HAL vendor tag that does not exist | — | closed |
| HDR10 video | HAL offers no 10-bit streams | — | closed |
| **Long native 4K60 clips (over ~5 min) are sometimes deleted** (3 of 4 tests) | the save step reads duration 0 and deletes the file; intermittent, not size (see `OWNER_TESTS_2026-10-30.md`) | record long clips in LMC or keep native 4K60 under ~4 min | find why the duration read fails (MediaMetadataRetriever on the pending file) |

## 4. Recommended daily use
* **LMC 8.4 (`POCO-F4-ONE.xml`)**: default for photos, especially low light and Portrait.
* **Native camera v13**: video (4K60 100 Mbit/s, OIS), 0.6x / 2x / 5x, selfies, filters, Short video / VLOG.
* Native Night mode: avoid until fixed.

## 5. Rollback
* Camera: `pm uninstall-system-updates com.android.camera` removes the v13 app update; the module copy can be replaced with v11
  (`~/camera_builds/MiuiCamera_v11.apk`, pendrive `camera_project/camera_builds/`) and the module disabled with `ksud module disable`.
* ROM payload: previous product image kept on the pendrive before flashing (P9 plan).

## 6. Also done on 2026-10-30
* **Google Phone + Contacts are the ROM default** (system priv-apps, MIUI Call removed, no chooser, Dialer cold start 1.1 s, Contacts 0.68 s): `ROM_HISTORY.md` §11.
* **Photo stage prototype** (`08_PHOTO_STAGE.md`): blown highlights 4-10x lower, pale colour C* 8.5 -> 11.5, noise unchanged, in-focus fine detail 2-4x; cannot restore smeared or blurred detail; not for LMC photos; **phone app built and tested on one photo** (see below).
* **Network and lock-screen findings** (`docs/system/PHONE_CHECKS_2026-10-30.md`): Wi-Fi drops every 85 s come from the router/channel (hit the laptop too, also with the phone's Wi-Fi off); mobile data is off on both SIMs; the lock-screen toggle is a third-party accessibility service with autostart denied.

* **PhotoStage app** (`tools/camera_lab/photo_stage_app`, `08_PHOTO_STAGE.md`): background job; every new native-camera photo (DCIM/Camera, owner com.android.camera) gets a processed copy in Pictures/PhotoStage ~30 s later, original untouched, EXIF kept; non-local-means denoise only when the photo is grainy. 16 MP takes 22-26 s on the SD870; six photos back to back raised the battery temperature from 34.0 to 35.2 °C (phone charging; hottest thermal zone 64 °C on the first run, then ~56 °C; no slowdown, runs 3-6 were even faster at 22 s).
* Plan status and what only the owner can do: `PLAN_STATUS.md`, `OWNER_HELP_NEEDED.md`.

## 7. To complete this report
- [x] Product image built (verify_img errors 0, symlink check 0, privcheck 0 missing), flashed no-wipe, boot + data + camera verified
- [ ] Owner real-call test (place + receive, SIM 1 and SIM 2), contacts and call log
- [x] Heat: PhotoStage batch (+1.2 C) and 12 min of native 4K60 recording (battery 35.7 -> 39.2 C, hottest zone 64-79 C, no throttling); LMC photo, Portrait and video regression on the flashed ROM: 0 crashes, PhotoStage ignores LMC photos
- [x] Release tag T20261031 in the fingerprint (flashed); release notes: `RELEASE_NOTES_DRAFT.md`; public package not made (owner decision to publish)
- [ ] Owner decisions: photo-stage look (`OWNER_HELP_NEEDED.md` #7), then PhotoStage as ROM app (release APK is built; ROM packaging needs one more product build + flash)
