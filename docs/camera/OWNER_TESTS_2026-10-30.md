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
Open-bug list therefore: Night purple, back Portrait, movielens/SNPE effect mode, protocol NPE (mode not yet identified), Photo auto-night.

## Video (native 1080p/4K, HSR, LMC)
Native: 4K60 HEVC 103 Mbit, 4K30 84 Mbit, 1080p60 42 Mbit, 1080p120 21-51 Mbit, HSR 720p120/240 (25-49 Mbit), all with audio and constant frame rate; one 1080p30 clip (2.4 s) and one LMC 4K clip have no audio track; a short-video clip reports a 90000 fps timebase (container quirk, plays). LMC video: HEVC, 4K ~80 Mbit but **variable frame rate** (25/33 fps), 720p clips 9-10 Mbit.
Not judged here: stabilisation/OIS and Bokeh quality (need eyes on the clips).

## Still needed from the owner
Daylight outside (native vs LMC vs PhotoStage), backlit portrait, judge the stage copies, real call on both SIMs, walking video for OIS: `OWNER_HELP_NEEDED.md`.
