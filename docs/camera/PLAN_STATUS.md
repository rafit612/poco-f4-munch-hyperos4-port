# Camera plan status (generated)

Generated 2026-10-30 23:06 from the live dashboard checklist (`wlog task`). [x] done · [~] partly done · [ ] to do. Plan details: `MASTER_PLAN.md`.

## P0 — Lab, baseline & reference photo library (active, 8/9 done)

- [x] Measurement tools installed (numpy, OpenCV, scikit-image, colour-science, ImageMagick, exiftool)
- [x] Live work dashboard (browser + terminal)
- [x] Reference photo library indexed: 361 photos, sets A/B/C (REFERENCE_LIBRARY.md)
- [x] POCO F4 photos by others from Wikimedia Commons (all 103 on the pendrive, indexed 2026-10-30)
- [x] Daylight test shots by owner: Xiaomi camera + LMC, same scenes (outdoor, window, face, text)
- [x] Measurement scripts: noise, sharpness, colour error, skin hue, clipping, white balance
- [x] Baseline sheet per camera and mode (photo): back cameras done 2026-10-30 (MODE_TEST_RESULTS); found+fixed UW (v12) and zoom (v13), Night purple open
- [x] Video baseline: 4K/1080p, stabilisation, 10-min thermal, audio
- [ ] Gate G1: owner reviews baseline + stable camera

## P1 — Stop the crashes (Portrait, Night, modes) (active, 10/12 done)

- [x] Mode test of every mode (MODE_TEST_RESULTS.md)
- [x] Short video: save/delete buttons fixed (camera v5)
- [x] Short video: two entries named apart - 'Xiaomi Short Video' + 'Short video' (v6)
- [x] Short video audio-HAL crash analysed (rare vendor bug, not the cause)
- [x] Night works (log noise left for tuning)
- [x] Movie works
- [x] Front Portrait works
- [x] Leftover test setting forcenoncalib reset to normal
- [x] Stock kernel RAM-boot test (not possible on Android 17: bpfloader)
- [~] Back Portrait: crash point found (seg/human2 network), not fixed yet - LMC Portrait works meanwhile
- [x] VLOG mode crash (Illegal config item 172)
- [ ] OWNER (outside): Panorama - one real hand sweep, confirm it saves

## P2 — Read app + OS layer (done, 7/7 done)

- [x] Mode table: 55 modes (41 on, 13 off, 1 conditional) + tools/camera_lab/map_modes.py
- [x] Camera id table (0 main, 1 front, 2 UW, 3 macro, 4-6 logical)
- [x] App -> MIA engine -> vendor algorithm chain documented (01_APP_OS_LAYER.md)
- [x] Logged mode sweep: camera id + HAL opmode + algorithm graph per mode
- [x] Vendor tag list with meaning
- [x] Marble (POCO F5) vs Munch (POCO F4) profile value table
- [x] Framework/services: CameraMind, camera extensions, SELinux denials

## P3 — Read kernel camera/video layer (done, 5/5 done)

- [x] Kernel material collected: port + stock 1.0.9 boot images, Xiaomi 17 kernel source (pendrive)
- [x] Read camera kernel drivers (CAM-SS: ISP, CCI, CSIPHY, sensor/actuator/OIS/flash/EEPROM)
- [x] Read video (Venus), GPU (KGSL), DSP (FastRPC), memory (ION/dma-buf) drivers
- [x] Port 4.19.325 vs stock 4.19.157 differences
- [x] 02_KERNEL_CAMERA_VIDEO.md + kernel_for_future notes

## P4 — Read firmware + vendor HAL (done, 5/5 done)

- [x] Firmware compare HyperOS 1.0.9 vs 1.0.12 (16 of 22 images identical)
- [x] Read CamX/CHI, node libraries, usecase XML, sensor/tuning binaries (03 §2-6b; per-mode pipeline/sensor/tuning branch logged 2026-10-30)
- [x] Pipeline diagrams per usecase (04_PIPELINES.md + 03 §6b table for photo, night, video, slow-mo, Ultra HD, Pro, Panorama, Movie)
- [x] Tuning-parameter dictionary + algorithm list (module level: 02 §6, 03 §4-5; field-level ANR/ASF meanings not mapped)
- [x] 03_FIRMWARE_HAL.md (all P4 items closed 2026-10-30)

## P5 — Hardware, drivers, sensors, lens + unused capability (done, 6/6 done)

- [x] Hardware docs + datasheets collected (35 MB, 1152 devices mapped)
- [x] Per-camera datasheet pages: what hardware offers vs what software uses (06 §1-2e)
- [x] Sensors/lens: modes, binning/remosaic, HDR, PDAF, OIS, shading, flash (06 §2a-2e + 03 §6b sensor mode per mode)
- [x] Unit calibration audit: intact - EEPROM checksums OK, dual-cal bin==bak (2022 factory), factory check result 1 (06 §3)
- [x] Unused SoC capability audit (ISP, DSP, GPU, CPU, video) -> 06b: U1 HDR10 closed (no 10-bit HAL streams), U2/U7/GPU budget done; only DSP load unreadable
- [x] Installed modules: main Sunny OV64B40, UW OV8856 (AAC?), front IMX596, macro GC02M1 (maker open)

## P6 — Knowledge map (graphify) (done, 4/4 done)

- [x] One index of all layer documents
- [x] Knowledge graph (graphify) of app <-> framework <-> HAL <-> kernel <-> firmware <-> hardware
- [x] Architecture diagrams (PNG/SVG)
- [x] Gate G2: maps complete

## P7 — Improvement design (algorithms, AI, security) (done, 5/6 done)

- [x] Per pipeline stage: current vs best method, portable?, gain/risk/effort
- [x] AI candidates that fit SD870 (GPU/DSP)
- [~] Security checklist (indicators, permissions, no debug props, no identifiers) - re-checked 2026-10-30 on v11; open: GitHub purge, netmgrd listeners vs stock
- [x] Which of the 13 switched-off modes can work on SD870
- [x] 07_IMPROVEMENT_PLAN.md ranked + Gate G3
- [x] Rate owner-approved candidates C1-C5 (gain/risk/effort)

## P8 — Implement + tune (colour, video, apps, GCam xml) (active, 17/30 done)

- [x] Watermark POCO F4 5G
- [x] Leica looks filter set enabled (Marble E1 25)
- [~] Colour/tone tuning: first pass inside the photo stage (target C* 14, shadow lift, highlight shoulder); owner must judge the look (compare images)
- [~] Video quality (stabilisation, encode, HDR, 50 Hz flicker)
- [x] Front camera / selfie track
- [x] Macro / ultra-wide policy (06_SENSORS_LENS.md §2e: main camera first for close-ups; owner A/B optional)
- [x] Third-party app capability matrix + fixes (Camera2, extensions)
- [x] One GCam xml (13 files -> 1)
- [x] Xiaomi 17 portable parts: only the look is portable (HAL is AIDL/sm8x50, 07 §5)
- [~] Own processing stage: laptop prototype + on-device PhotoStage app (OpenCV NLM + detail/tone/colour, background job, copy to Pictures/PhotoStage) built and tested on 1 real photo 2026-10-30; ~25 s per 16 MP; owner must judge the look (OWNER_HELP_NEEDED.md #7); release build + ROM packaging open
- [x] C1 Sensor RAW HDR (3-exposure) - test module, quality check
- [x] C2 DSP stage of Xiaomi HDR (hdsr) - closed: app requests it via vendor tag xiaomi.hdr.sr.enabled, which the munch HAL lacks (VTNF) -> not usable
- [x] C3 60 fps + ISO above 877 for other apps
- [~] C4 Own AI stage on NNAPI/DSP/GPU: hardware reachable without root (U7), design in 07 §5
- [x] C5 Hidden camera modes (13) - which work on SD870
- [~] OIS check: handheld video/long exposure OIS on vs off (port)
- [x] Soft photos path 3: LMC daily camera + one tuned xml
- [x] Soft photos path 2: lighter photo path in Xiaomi app - closed: daylight A/B shows no-AIIE / no-MFNR add no detail (not the cause)
- [~] Soft photos path 1: ROOT CAUSE = HAL high-strength noise reduction (not AF/AIIE/MFNR); NR off gives LMC edges but grain; NLM on phone is the denoiser for it; camera v14 (NR off + stage) only after a daylight A/B (owner shots)
- [x] Fix: fast shots saved as 1440x1080 placeholders (v8 fix; dark re-test 2026-10-30: 14 dark shots all full-size processed)
- [~] Night: auto-night cause found (o.h0); NEW BUG: Night mode output has a purple cast (MIA MMCP 'no child node') - open; use LMC at night
- [x] U15 higher video bitrate
- [ ] OWNER (optional): window/backlit scene - normal HDR highlight look (C2 itself closed)
- [ ] OWNER (outside/evening): night - short dark test, night highlights + colour
- [ ] OWNER (indoor, quick): video Bokeh in native Video mode with a person in frame - is the blur good?
- [x] Lock-screen toggle: accessibility service 'Restart/PowerMenuService' was in Crashed list, autostart denied; toggle itself works (docs/system/PHONE_CHECKS)
- [x] Google Dialer + Contacts as ROM default: flashed, system apps, no chooser, data intact; owner real-call test pending
- [ ] OWNER (daylight, outside): same scene native vs LMC vs PhotoStage copy (decides v14)
- [ ] OWNER: judge 5-6 PhotoStage copies vs originals: better / same / too strong
- [ ] OWNER (outside): handheld video 1080p + 4K walking, stabilisation/OIS

## P9 — Ship + report (todo, 2/5 done)

- [x] Bake final camera into the ROM: camera v13 built from payload_tele and FLASHED no-wipe 2026-10-30 (boots, camera works)
- [~] Regression run: post-flash boot/crash/camera/data checks OK 2026-10-30; heat + LMC + owner call test still open
- [~] Release build + rollback plan: ROM rollback image exists (out_tele_T20261026_prev); PhotoStage release APK + ROM packaging in progress
- [~] Final report: updated 2026-10-30 after the flash (FINAL_REPORT.md); open items listed in section 7
- [x] Space: deleted verified duplicate port zip (4.7 GB) from Downloads; pendrive keeps it
