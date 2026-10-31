# Owner test session 2026-10-30, 23:40-00:00 (indoor, evening)

Data: the owner shot with the native camera (v13) and LMC (`POCO-F4-ONE.xml`), photos and videos. All shots were **indoor, low-to-normal room light, no daylight**, so the daylight A/B for camera v14 is still open.
Pulled from the phone to `~/camera_builds/owner_20261030/` (photos, logs, `tonight.csv` with the measurements; videos deleted from the laptop after probing, they stay on the phone).
Measured with `tools/camera_lab/measure_photos.py` and `photo_stage.py` metrics; crash data from `logcat -b crash`, `-b events` and tombstones 25-29.

## Photos: native vs LMC (12 MP, same room, same objects)
| | files | sharpness (Laplacian var., median) | noise | chroma |
|---|---|---|---|---|
| native v13 | 27 | **11.7** | 0.44 | 11.0 |
| LMC 8.4 | 14 | **250.6** | 2.76 | 10.7 |
Native shots are ~20x softer; this is the HAL noise-reduction finding again (`REFERENCE_LIBRARY.md`) and it holds for the 64 MP mode (sharpness 8-19) as well. LMC keeps the detail. Colour is about the same.

## PhotoStage on 12 real native shots (before -> after, means)
Laplacian 1.9 -> 4.5, edge slope 2.23 -> 2.51, chroma 11.3 -> 13.2, brightness L 44.7 -> 45.8, blown highlights 0.61 -> 0.42 %. The stage helps a little (colour, brightness, highlights) but **cannot recover what the HAL smeared**: at 100 % the face crop stays soft. So the stage is a finishing step, not a replacement for turning HAL noise reduction down (v14, still needs a daylight A/B).
Problems found and fixed in the app the same night: the watcher stalled on a 76 MP native panorama (out of memory) and, being content-triggered, missed photos taken while a batch ran. Now: images over 24 MP are skipped (64 MP shots are skipped on purpose), it re-checks until nothing is new, and opening the app re-schedules the job (an app update drops it). Verified: 24 copies, new photos picked up.

## Modes
| Mode | Result |
|---|---|
| Panorama (native) | saves: 18104x4224, 28 MB. LMC pano 5502x1602. **P1 owner item done.** |
| Photosphere (LMC) | saved (8084x5128) |
| Night, native | **purple/over-saturated** (chroma 46 vs 11, L 32): bug confirmed on a real scene. LMC Night: sharp (506), natural colour. Use LMC. |
| Portrait, native back | **crashes again** (tombstones 25-27: `libwa_depth.so` / MegEngine DNNError in MiaNodeJiiGANCapBokeh). LMC Portrait works. |
| Native crash 23:48 x2 | SIGSEGV in `PreviewRenderEn`, `libSNPE.so`, with the on-demand `movielens` module (`libfenshen_snpe.so`): an AI effect mode on the Hexagon runtime. New open bug, not analysed further. |
| Native crash 23:49 x2 | `NullPointerException ht.d.initView -> vt.a.registerProtocol()` (a mode screen whose protocol is not registered). New open bug; the owner switched to LMC right after. |
Open-bug list therefore: Night purple, back Portrait, Photo auto-night (the two new crashes are fixed by hiding Mimoji/Clone/Movie effects, see Follow-up).

## Video (native 1080p/4K, HSR, LMC)
Native: 4K60 HEVC 103 Mbit, 4K30 84 Mbit, 1080p60 42 Mbit, 1080p120 21-51 Mbit, HSR 720p120/240 (25-49 Mbit), all with audio and constant frame rate; one 1080p30 clip (2.4 s) and one LMC 4K clip have no audio track; a short-video clip reports a 90000 fps timebase (container quirk, plays). LMC video: HEVC, 4K ~80 Mbit but **variable frame rate** (25/33 fps), 720p clips 9-10 Mbit.
Not judged here: stabilisation/OIS and Bokeh quality (need eyes on the clips).

## Still needed from the owner
Daylight outside (native vs LMC vs PhotoStage), backlit portrait, judge the stage copies, real call on both SIMs, walking video for OIS: `OWNER_HELP_NEEDED.md`.

## Follow-up (2026-10-31): both new crashes are modes this phone cannot run
* **Null protocol NPE** = the **Mimoji** (Sticker avatars) mode screen: `ht.d` only creates its protocol when the prop `camera.support.mimoji.version` is 4 or more (or the device layout class is 4); on this phone the prop is unset (-1), so opening Mimoji crashes the app.
* **SNPE SIGSEGV** (`libSNPE.so` / `libfenshen_snpe.so`, `movielens` module) = the **Clone** / **Movie effects** modes (both run in FunModule); the Hexagon/SNPE runtime of the port does not work for them (same family as the Portrait failures).
* All four entries (Mimoji, Mimoji video, Clone, Movie effects) answer `support() = true` unconditionally, so the mode bar offers them. Fix prepared: `tools/re/hide_modes.sh` sets `support()` to false for them. Test build `~/camera_builds/MiuiCamera_v14test_hide_modes.apk` (v13 + the four hidden). **Installed as an app update and swept 2026-10-31 01:25**: the mode bar and the More panel no longer list Sticker avatars, Clone or Movie effects; 18 modes opened, 0 crashes (Pro, Video, Photo, Documents, Night, Ultra HD, ID photo, Slow motion, Time-lapse, Movie, Long exposure, Dual video, Panorama, both Short videos, VLOG, Short film, Pocket mirror). Rollback: `pm uninstall-system-updates com.android.camera` (back to the ROM's v13). The ROM payload still holds v13; this build goes into the next product build as part of v14 (the noise-reduction part is still undecided).
* Setting the prop instead would enable a mode whose AI runtime then crashes in SNPE, so hiding is the safer fix.

## 2026-10-31: long 4K60 recordings: three were deleted by the camera; safety net added (camera v15)
Native camera, 4K 60 fps (100 Mbit/s). Build = what was installed.
| Build | Length | File | Result |
|---|---|---|---|
| v14 | 12 s | 0.15 GB | saved |
| v14 | 6 min 22 s | 4.79 GB | **deleted** |
| test (cap raised) | 11 min 42 s | 8.78 GB | **deleted** |
| test (cap raised) | 5 min 56 s | 4.46 GB | **deleted** |
| test (cap raised) | 70 s, 3 min 38 s | 0.87, 2.73 GB | saved |
| test (cap raised) | 6 min 17 s | 4.73 GB | saved |
| v15 app update | 6 min 13 s, 6 min 33 s, 6 min 54 s, 6 min 3 s, 3 min 27 s | 4.68, 4.93, 5.19, 4.55, 2.59 GB | saved |
| **v15 in the ROM** | 6 min 50 s | 5.14 GB | saved |
What happened to the deleted ones: the muxer finishes normally, then the save step (`n7.Q.a`) reads duration 0 (`save video ... duration -> 0`), and `VideoModule.videoFileDurationInvalid` deletes the file (`delete invalid video .pending-...mp4`).
**The root cause of the duration 0 is still unknown, and the failure has not come back since 03:30**, so none of the later runs exercised the fix by chance. Ruled out by test: the 3,670,016,000-byte cap (`tools/re/video_maxsize.sh`, not shipped; a 4.79 GB file was written with the cap in place, and clips were lost with it raised), auto hibernation, a 4 GiB limit, and waking the sleeping preview with a tap on the shutter area.
**Fix in v15 (`tools/re/video_keep_fix.sh`, `VideoDur.java`):** after the app's two reads, if the duration is 0 and the file holds at least 1 MB, the length is read from the MP4 header (`mvhd`), so the app no longer deletes it; a file without a readable header is kept too, with a nominal 1 s length. Verified by a one-off test build that forced duration 0 on every save: the file was kept, length correct (31.95 s, log `MunchVideoDur`), normal 4K60 file. Parser also checked on the laptop: moov at end, 64-bit moov header, version-1 mvhd, no moov, under-1 MB file.
If it fires in real use, the log tag `MunchVideoDur` records what the framework reports, which should finally show the cause.
Auto hibernation note: ~175 s after the last touch the preview goes black and the first tap only wakes it. Recording continues. A real user may think the button did nothing.

### 4K60 heat
Separate recordings, on the charger, phone on a stand, screen on: 5.5 min from cool: battery 35.7 -> 35.9 C (peak 36.0), hottest zone 64-74 C. About 10 min from warm, two runs: battery 38.1 -> 38.9 C and 38.6 -> 38.7 C (peak 39.2), hottest zone 71-80 C. ROM v15, 6 min 50 s right after the mode sweep: battery 37.4 -> 38.3 C. Recording kept running, crash buffer empty. **Not checked:** dropped frames, throttling, heat on battery, in daylight or in the hand.

## 2026-10-31 midday: owner daylight session on the final ROM (T20261031b), overcast, outdoors, same scene
**Stability:** no crash in either camera, crash buffer empty. PhotoStage made all 15 copies of the 16 MP native shots without being killed; LMC shots were skipped. Photos stay local (neighbouring buildings).

**Native vs LMC, daylight, ISO 50.** Native shots aligned onto the LMC frame (SIFT homography, 669-873 inliers), identical region:
| | Laplacian variance | Look at 100 % |
|---|---|---|
| LMC | 105.6 | fine wall texture and thin lines kept |
| native v15 (two shots) | 55.1, 51.2 | clean but smooth; wall texture gone |
| PhotoStage copy | 135.6, 127.3 | crisp edges, texture **not** restored; saturated blue and red pushed too far |
The gap is about 2x in daylight (about 20x in the indoor evening set). The PhotoStage number is higher than LMC only because sharpening raises this metric; it is not more real detail.
**Reading:** native softness is present at ISO 50 too, where there is little noise to remove, so a camera build with the HAL noise reduction off is worth a daylight test: `~/camera_builds/MiuiCamera_v15_NRoff.apk` (v15 + NR off + edge off on STILL), built, not installed. PhotoStage colour: the chroma gain is too strong on already saturated colours; the owner has not given a verdict yet.

**Video.** All four clips have audio and no dropped frames by count: native 4K60 16.8 s, 101 Mbit/s, 1006 frames; LMC 4K60 9.6 s, 80 Mbit/s, 579 frames; LMC 4K30 and 1080p30 also fine. Stabilisation not judged.

**Calls on the final ROM (from the telecom log).** First round at 12:42: SIM 2 and SIM 1 both dialled and were ended locally without an answer. Second round at 12:47, answered: SIM 2 outgoing 6 s (VoLTE call, active, ended by the far side), SIM 2 incoming 3 s, SIM 1 incoming 13 s (circuit-switched). Ringer, answer, earpiece route and in-call audio mode all normal, no crash. **Not yet shown:** an answered outgoing call on SIM 1. The log cannot show whether voice was heard both ways; that is the owner's to confirm.

## 2026-10-31 13:00: noise reduction off, A/B from one fixed position (phone on its stand, indoors, ISO ~800)
Three shots each, same spot, aligned; region means (Laplacian variance) and flat-wall noise:
| | ROM v15 | NR off (+ edge off) | NR off + PhotoStage | LMC |
|---|---|---|---|---|
| shelf objects | 32 | 228 | 281 | 165 |
| bag and basket | 32 | 323 | 303 | 202 |
| wood grain | 17 | 368 | 1080 | 200 |
| flat-wall noise | 1.10 | 6.45 | 2.71 | 2.41 |
At 100 % (the numbers mislead here, grain and sharpening inflate them): LMC is the best by eye: thin flower outlines, clean surfaces. ROM v15 is clean and soft. NR off shows more structure than ROM but with heavy grain. **NR off + PhotoStage is the worst to look at:** the denoise melts the thin lines into blobs and leaves colour blotches.
**Decision: do not ship NR off.** The test build was removed; the phone runs ROM v15. Not tested: NR off in daylight at ISO 50, where grain would be far lower. That needs the phone pointed at the same outdoor scene.

## 2026-10-31: AI denoise sample test: not run
The on-phone AI stage (C4) was dropped by the owner; a laptop sample was wanted for information. SCUNet on the laptop: blocked by the session's permission check (downloaded code). Gemini image models: all keys on the free tier, `limit: 0`, billing needed. No AI result exists.

## 2026-10-31: phone cleared at the owner's request
All photos and videos from the native camera and LMC, and all PhotoStage copies, were deleted from the phone (Camera folder 5.2 GB to 53 MB). Kept: 17 photos of 22-23 Oct restored by Google during phone setup. The daylight and noise-reduction test shots of 31 Oct are on the pendrive (`camera_project/owner_tests_2026-10-31/`).

