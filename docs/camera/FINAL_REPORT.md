# Camera project — final report (2026-10-31)

Status: **camera v15 (v13 + Mimoji/Clone/Movie effects hidden + finished videos no longer deleted) and the PhotoStage app were flashed 2026-10-31 (product only, no wipe; tag T20261031b; `ROM_HISTORY.md` §12).** It boots in 25 s, 0 crashes, camera works, contacts and call log
intact. Built from `payload_tele` (the shipped 32-bit-capable build; the pure 64-bit Global build failed to boot and is shelved).
Paused by the owner on 2026-10-31 after this state; work resumes after the owner has taken more photos and videos (section 8).
Rollback: `bash secure_build/flash_product_nowipe.sh secure_build/out_tele_T20261031_v14 "rollback"` (v14), or `out_tele_T20261030_v13`, `out_tele_T20261026_prev`.

## 1. What changed for the owner (native camera, MiuiCamera 6.7 on the Marble profile)

| Area | Before (port as received) | Now (camera v15) | Build |
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
| Crashing modes (Sticker avatars, Mimoji video, Clone, Movie effects) | app crash | hidden | v14 |
| **Long 4K60 clips** | sometimes deleted after recording | a file with data is no longer deleted | v15 |

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
| Native photos softer than LMC (~20x less on the owner's indoor set) | **HAL high-strength noise reduction** (not AF, AIIE, MFNR or ANR); NR off gives LMC-like edges but grain | **LMC** for detail, or the **PhotoStage app** (copy with sharper detail, better tone and colour) | camera v14 = NR off + PhotoStage denoise, after a daylight A/B (owner shots, `OWNER_HELP_NEEDED.md`) |
| HDR super-resolution (hdsr) | app needs a HAL vendor tag that does not exist | — | closed |
| HDR10 video | HAL offers no 10-bit streams | — | closed |
| Long 4K60 clips were sometimes deleted | app read duration 0; **root cause unknown**, not seen again since 2026-10-31 03:30 | v15 keeps such files (rescue path tested with a forced 0) | if the log tag `MunchVideoDur` ever appears, it shows the cause |

## 4. Recommended daily use
* **LMC 8.4 (`POCO-F4-ONE.xml`)**: default for photos, especially low light and Portrait.
* **Native camera v15**: video (4K60 100 Mbit/s, OIS), 0.6x / 2x / 5x, selfies, filters, Short video / VLOG.
* Native Night mode: avoid until fixed.

## 5. Rollback
* Camera: the ROM holds v15; any test build goes in as an app update and `pm uninstall-system-updates com.android.camera` returns to the ROM copy.
* ROM: `bash secure_build/flash_product_nowipe.sh secure_build/out_tele_T20261031_v14 "rollback"` (older: `out_tele_T20261030_v13`, `out_tele_T20261026_prev`).

## 6. Also done on 2026-10-30 and 2026-10-31
* **Google Phone + Contacts are the ROM default** (system priv-apps, MIUI Call removed, no chooser, Dialer cold start 1.1 s, Contacts 0.68 s): `ROM_HISTORY.md` §11.
* **Photo stage prototype** (`08_PHOTO_STAGE.md`): blown highlights 4-10x lower, pale colour C* 8.5 -> 11.5, noise unchanged, in-focus fine detail 2-4x; cannot restore smeared or blurred detail; not for LMC photos; **phone app built and tested on one photo** (see below).
* **Network and lock-screen findings** (`docs/system/PHONE_CHECKS_2026-10-30.md`): Wi-Fi drops every 85 s come from the router/channel (hit the laptop too, also with the phone's Wi-Fi off); mobile data is off on both SIMs; the lock-screen toggle is a third-party accessibility service with autostart denied.

* **PhotoStage app** (`tools/camera_lab/photo_stage_app`, `08_PHOTO_STAGE.md`): background job; every new native-camera photo (DCIM/Camera, owner com.android.camera) gets a processed copy in Pictures/PhotoStage ~30 s later, original untouched, EXIF kept; non-local-means denoise only when the photo is grainy. 16 MP takes 22-26 s on the SD870; six photos back to back raised the battery temperature from 34.0 to 35.2 °C (phone charging; hottest thermal zone 64 °C on the first run, then ~56 °C; no slowdown, runs 3-6 were even faster at 22 s).
* Plan status and what only the owner can do: `PLAN_STATUS.md`, `OWNER_HELP_NEEDED.md`.

## 7. State of the checks
- [x] Product image built (verify_img errors 0, symlink check 0, privcheck 0 missing), flashed no-wipe, boot + camera verified on tag T20261031b
- [~] Calls on this ROM: SIM 2 outgoing and incoming and SIM 1 incoming connected; SIM 1 outgoing answered and voice both ways still to be confirmed by the owner
- [x] Heat: PhotoStage batch; native 4K60 recordings on the charger (battery up to 39.2 C, hottest zone up to 80 C). Dropped frames, throttling and heat on battery not checked
- [x] LMC photo, Portrait and video on the flashed ROM: 0 crashes; PhotoStage ignores LMC photos
- [x] Release tag in the fingerprint, release notes written. **No new public ROM package:** the public download is still T20261026
- [ ] Owner sign-off G1 and the PhotoStage look verdict

## 8. Where the project is paused (2026-10-31)
First batch of the owner's shots (evening of 2026-10-31) is analysed in `SHOTS_2026-10-31_BATCH1.md`: back Portrait still crashes and leaves low-resolution stubs, native foliage is still smeared compared with LMC, 6 videos kept, PhotoStage verdict still open.
On the phone: ROM T20261031b, camera v15 from `/product`, PhotoStage app update with the gentler colour (the ROM copy has the old colour values; the new APK is staged in `payload_tele`).
Tests made after the flash, details in `OWNER_TESTS_2026-10-30.md`: daylight native vs LMC vs PhotoStage (native about 2x softer than LMC at ISO 50); noise reduction off indoors (worse, not shipped); on-phone AI stage dropped, and no AI sample result exists.
Known limits, use LMC: back Portrait, Night purple, Photo auto-night, softer native photos. Long 4K60 clips were sometimes deleted; v15 keeps them, cause unknown.
**To resume:** the owner brings new photos and videos (walking video, bokeh video, backlit, evening shot) and a verdict on the PhotoStage copies, listed in `OWNER_HELP_NEEDED.md`. The next ROM build needs about 14 GB free on the laptop.
