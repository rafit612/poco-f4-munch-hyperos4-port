# 04 Camera pipelines per use case (P4)

How a shot travels through the native camera (MiuiCamera 6.7, build v11) on this port: app module → HAL session
(operating mode) → CamX/CHI processing → the app's MIA post-processing graph (`libmialgoengine`, runs inside the camera
app) → saved file. Built from the mode sweep (`p2_mode_sweep_generated.md`), today's shot logs and earlier findings.
[Observed] = seen in logs on this phone; [Inferred] = from code/config, not traced end to end.

## Overview

```
 shutter
   │
   ▼
 App module (Camera2Module / NightModule / PortraitModule / VideoModule …)
   │  picks picture size (F1.n3, Marble profile limits, size cache), session opmode, burst
   ▼
 HAL session (CamX + CHI override, opmode e.g. 0x9005 photo, 0x800a night, 0x803c video)
   │  IFE → BPS → IPE realtime; offline MFNR / HDR / bokeh features (chxadvancedcamerausecase)
   ▼
 "Parallel" capture: the app saves a preview-size placeholder first (PlaceholderTrim, v8),
   │  then the YUV frames go to the MIA graph
   ▼
 MIA graph in the app (libmialgoengine nodes, chosen by opmode/camera_mode)
   │  e.g. AIIE (AI enhance), HDR, SkinBeautifier (ASBF), MiSegment, GPU (flip/rotate), JiiGAN bokeh
   ▼
 JPEG encode + EXIF + watermark → DCIM/Camera (placeholder overwritten)
```

## Per use case

| Use case | App module | Camera | Session opmode | HAL side | App MIA nodes | Output | State |
|---|---|---|---|---|---|---|---|
| Photo (back) | CaptureModule (163) | 0 (OV64B40) | 0x9005 | MFNR, 5-frame burst (algoType 7) [Observed] | AIIE, HDR, SkinBeautifier (fast without a face: 7-108 ms/frame) [Observed] | 4624x3472 JPEG | works; night shots soft, highlights bloom (open) |
| Photo (front) | CaptureModule (163) | 1 (IMX596) | 0x9005 [Inferred: same module] | MFNR, 5-frame burst [Observed] | HDR, MiSegment, SkinBeautifier (700-1220 ms/frame), GPU flip [Observed] | 5184x3904 JPEG (v11) | fixed in v11 (was 1600x1200 / 800x600, colour swap); base beauty always on |
| Ultra HD | PixelModule | 0 | 0x9004 | full-res 64 MP path [Observed graph 0x80f3] | node type 1 [Observed] | 9248x6944 | works |
| Night | NightModule | 0 | 0x800a | SuperNight capture [Observed graph 0x800a] | node type 1 [Observed] | 4624x3472 | works as a mode; auto night in Photo did not trigger in owner's street shots |
| Portrait (back) | PortraitModule (171) | 4 (logical main+UW) | ALGO_UP_DUAL_BOKEH (32770) | dual stream main 4624x3472 + UW 3264x2448 [Observed] | JiiGANCapBokeh → libwa_depth → libanc_dc_base (MegEngine, OpenCL) [Observed] | crash | **parked**: load-time GPU-format conversion builds a 0x0 tensor on the port's Adreno driver; LMC Portrait works |
| Portrait (front) | PortraitModule | 1 | [not traced] | [not traced] | [not traced] | [not traced] | owner test pending |
| Video | VideoModule | 0 | 0x803c | EIS only at 720p/1080p 30 fps, OIS always [Observed] | none (encoder path) | HEVC/H.264, v9 bitrate table (4K60 100 Mbit/s) | works |
| Slow motion | SlowMotionModule | 0 | 0x1 (constrained high speed) | 120/240 fps sensor modes [Observed modes] | none | HFR video | works |
| Time-lapse / Short video / VLOG | FastMotion / FunModule | 0 | 0x8004 | normal video | none | video | works (Short video fixed v5, VLOG v7) |
| Movie | CinematicModule | 0 | 0x8032 | `PreviewVideo` pipeline, 4624×3472 [Observed] | [not traced] | video | opens |
| Long exposure | AmbilightModule | 0 | 0x9300 | [not traced] | [not traced] | photo | opens |
| Pro (video) | ProRecModule | 0 | 0xf010 | manual controls | none | video | opens |
| Panorama | PanoramaModule | 0 | 0x8008 | `Snapshot` pipeline, 4624×3472, tuning feature2 11 [Observed] | [not traced] | photo | owner hand sweep pending |
| Documents / ID photo | DocModule / IdPhotoModule | 0 | 0x9005 | MFNR | AIIE, HDR, ASBF (types 7, 10, 2) [Observed] | photo | works |

## Notes
* MIA node types in the mode sweep (01_APP_OS_LAYER.md §4): 7 = HDR, 10 = SkinBeautifier, 2 = AIIE (graph order
  HDR → SkinBeautifier → AIIE); type 1 in Night / Ultra HD is their single main algorithm node; 24 = JiiGAN bokeh.
  Back Portrait's session opmode in the sweep is 0x9001 (the app logs it as ALGO_UP_DUAL_BOKEH, value 32770 in the session config).
* The skin beautifier runs on every back and front photo; it only does real work when it finds a face. On the front
  camera it is the most expensive step (~0.7-1.2 s per burst frame) and the reason for the smooth skin.
* The HAL reports `WaitOfflineFeatureCompleted failed` on front shots without visible effect on the result [Observed].
* Session opmodes and the HAL usecase each one selects in CHI are still only partly mapped (needs a CamX log run per mode,
  see 03_FIRMWARE_HAL.md §6).

* HAL pipeline, sensor mode and Chromatix branch of every main mode: `03_FIRMWARE_HAL.md` §6b (CamX-logged sweep, 2026-10-30).
