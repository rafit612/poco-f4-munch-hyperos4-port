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

## 2026-10-31: long 4K60 recordings are sometimes deleted by the camera (heat test side finding)
Native camera, 4K 60 fps (100 Mbit/s), plain recording:
| Length | File | Result |
|---|---|---|
| 12 s, 70 s, 3 min 38 s | 0.15 / 0.87 / 2.73 GB | saved, duration correct |
| 6 min 22 s | 4.79 GB | **deleted** |
| 11 min 42 s | 8.78 GB | **deleted** |
| 5 min 56 s | 4.46 GB | **deleted** |
| 6 min 17 s | 4.73 GB | **saved** (duration 376 s) |
Log of the deleted ones: the muxer finishes (`MPEG4Writer: final fsync ... file size 4793557269`), the save step reads the duration as 0 (`VideoSaveRequest: save video: mVideoSaveCallback ... duration -> 0`, `getVideoExifFromFd: ParcelFileDescriptor is null`), then `VideoModule.videoFileDurationInvalid` -> `VideoUtil: delete invalid video .pending-...mp4`. The same lines appear in the run that was saved, but there the duration came back (376926 ms), so the failure is **intermittent and not a file-size rule**: three of four recordings over 5.5 min were lost, none under 4 min.
Ruled out: the 3,670,016,000-byte cap in `VideoUtil.getRecorderMaxFileSize` (raising it to 64 GB with `tools/re/video_maxsize.sh` did not help and the cap is not enforced on this port: a 4.79 GB file was written with the cap at 3.67 GB), auto hibernation (`keepAutoHibernation` 175 s: the preview goes black, recording continues), the 4 GiB boundary (a 4.73 GB file saved). **Not ruled out**: the reading of the duration right after the stop (MediaMetadataRetriever on the pending file) failing under load or timing. The patch is NOT shipped (the ROM keeps v14).
**Advice until fixed:** record long 4K60 clips in **LMC** (its 7 s, 4K clips saved, long ones not tested) or keep native 4K60 clips under ~4 minutes; 1080p60 / 4K30 would not hit the problem as soon but are untested for length.
Heat (same recordings): battery 35.7 -> 39.2 C over 12 min of recording while charging, hottest thermal zone 64-79 C, no throttling message, no crash, recording kept running.
