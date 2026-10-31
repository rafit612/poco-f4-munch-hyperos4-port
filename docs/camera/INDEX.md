# Camera project — index (POCO F4 5G "munch", HyperOS 4 / Android 17 port)

One entry point for every camera document. Large data (photos, ROM images, vendor configs, kernel notes) lives on the pendrive
`poco_f4_munch_archive/` (`camera_project/`, `kernel_for_future/`), never in this public repo.

## Plan and status
* [MASTER_PLAN.md](MASTER_PLAN.md) — phases P0–P9, owner decisions, steps 1–17, added steps N1–N14, candidates C1–C5.
* [PLAN_STATUS.md](PLAN_STATUS.md) — done / partly done / to do per phase (generated from the live dashboard checklist).
* `re/hide_modes.sh` — hides Mimoji / Clone / Movie effects (crash on this phone) by making their `support()` false.
* `re/video_keep_fix.sh` + `re/VideoDur.java` — finished videos are not deleted when the app reads duration 0 (v15). `re/video_maxsize.sh` — disproved idea, kept as a record.
* [RELEASE_NOTES_DRAFT.md](RELEASE_NOTES_DRAFT.md) — release notes, tag, rollback (no new public package yet).
* [OWNER_TESTS_2026-10-30.md](OWNER_TESTS_2026-10-30.md) — results of the owner test session (native vs LMC numbers, modes, crashes, video probe).
* [OWNER_HELP_NEEDED.md](OWNER_HELP_NEEDED.md) — everything only the owner can do (outdoor/indoor test shots, calls, router, decisions), with what each one decides.
* [G2_REVIEW.md](G2_REVIEW.md) — gate G2 review: maps complete?, open items, owner decisions D1/D2.
* [CAMERA_PROJECT.md](CAMERA_PROJECT.md) — running log since 2026-10-27 (watermark, Leica looks, Portrait history).

## Layers, top to bottom
| Layer | Document | Main content |
|---|---|---|
| App + Android | [01_APP_OS_LAYER.md](01_APP_OS_LAYER.md) | chain button → module → opmode → camera id → HAL → MIA engine; camera ids 0–6; 55 modes; opmode per mode; vendor tags; services/SELinux |
| — generated | [p2_modes_generated.md](p2_modes_generated.md), [p2_mode_sweep_generated.md](p2_mode_sweep_generated.md), [p2_vendor_tags_generated.md](p2_vendor_tags_generated.md) | mode registry, logged sweep, app vs HAL tag lists |
| Vendor HAL + firmware | [03_FIRMWARE_HAL.md](03_FIRMWARE_HAL.md) | modules on this unit, CamX/CHI files, `camxoverridesettings.txt`, main-camera Chromatix tuning blocks, HDR/bokeh configs, 133 pipelines |
| Pipelines per use case | [04_PIPELINES.md](04_PIPELINES.md) | shot path per mode: app module, session opmode, HAL processing, app MIA nodes (AIIE/HDR/SkinBeautifier/MiSegment/GPU/bokeh), output size, state |
| P9 release plan | [P9_RELEASE_PLAN.md](P9_RELEASE_PLAN.md) | bake final camera into the ROM: done (v15, T20261031b), space, build, flash, regression, release |
| Final report | [FINAL_REPORT.md](FINAL_REPORT.md) | what changed (v1-v15), measured state, open issues, daily-use advice, rollback, where the project is paused |
| Kernel | [02_KERNEL_CAMERA_VIDEO.md](02_KERNEL_CAMERA_VIDEO.md) | camera driver tree, active devices, Venus encoder limits, who uses CVP/NPU/DSP/GPU, port vs stock kernel, stage ↔ tuning-block map |
| Hardware: sensors + lenses | [06_SENSORS_LENS.md](06_SENSORS_LENS.md) | per-camera limits (ISO, exposure, focus, OIS, fps), calibration, module variants |
| Hardware: unused capability | [06b_UNUSED_CAPABILITY.md](06b_UNUSED_CAPABILITY.md) | U1–U15: HDR10, DSP HDR, RAW HDR, 60 fps/ISO for apps, NPU, CVP, GPU, hidden modes, bitrate |

## Improvement plan (P7)
* [07_IMPROVEMENT_PLAN.md](07_IMPROVEMENT_PLAN.md) — 15 ranked items (gain / risk / effort / layer), recommended order, gate G3 decisions.

## Knowledge graph (P6)
* (local only, not in this repo) `graphify-out/graph.html` — interactive map of all documents (open in a browser), `graph.svg`,
  `GRAPH_REPORT.md`. 699 concepts, 1464 links, 42 groups (updated 2026-10-30). Rebuild after doc changes: graphify skill `--update`.

## Photo stage
* [08_PHOTO_STAGE.md](08_PHOTO_STAGE.md) — post-capture stage (detail / tone / colour / NLM denoise): laptop prototype, measured results, on-device PhotoStage app (`tools/camera_lab/photo_stage_app`).

## Tests and evidence
* [MODE_TEST_RESULTS.md](MODE_TEST_RESULTS.md) — every mode, fixes (Short video v5/v6, VLOG v7), Portrait investigation with native trace.
* [REFERENCE_LIBRARY.md](REFERENCE_LIBRARY.md) — reference photo sets A/B/C and comparison method.

## Tools (`tools/`)
* `re/camera_watermark_patch.sh` — builds the patched camera (Marble profile values, Short video generation + label, VLOG fallback).
* `re/hidden_modes_test.sh` — test build with hidden modes switched on (`support()` → true).
* `re/smali_trace.py` — adds `MunchNight`-tagged logs at every branch label / fall-through of chosen methods (used to find the auto-night gate).
* `re/Decomp.java`, `re/Smali.java` — decompile chosen classes / disassemble + assemble a dex.
* `camera_lab/ab_shot.py` — one stand test shot (native or `--lmc`), copies it and deletes only its own file; refuses to tap if the camera is not in front.
* `camera_lab/tile_detail.py` — detail per 3x3 tile (Laplacian variance) for stand A/B shots.
* `camera_lab/measure_photos.py` — sharpness, noise, clipping, L*, chroma, white balance per photo.
* `camera_lab/nnapi_probe/` — lists NNAPI devices as seen by an ordinary process.
* `camera_lab/nr_probe/` — tiny Camera2 test app (built with plain SDK tools): same scene with different noise-reduction / edge modes; `re/nr_variant.sh` — the same lever inside the native app (test build, 29 s).
* `camera_lab/photo_stage.py` — the stage on the laptop; `camera_lab/photo_stage_app/` — the same stage as an Android app (OpenCV, JobScheduler watcher, plain SDK build).
* `camera_lab/map_modes.py`, `camera_lab/mode_sweep.py`, `camera_lab/build_reference_index.py`, `payload_extract_remote.py`, `kallsyms_dump.py`.
* Test builds go in as **app updates** (`adb install -r`, same debug key) and roll back with `pm uninstall-system-updates com.android.camera`
  — no reboot, no module change (2026-10-30).

## Camera builds
v3 (watermark, Leica set, bokeh width) → v5 (Short video buttons) → v6 (Short video names) → v7 (VLOG fix) → v8 (placeholder trim)
→ v9 (video bitrates) → v11 (front 20 MP fix) → v12 (ultra-wide photos fixed) → v13 (zoom 2x+ fixed: SR off, sha 3a76a1e3) → v14 (crashing modes hidden) → **v15 (finished videos not deleted, sha b2e51dfb; in the ROM)**. Rollback build: v11 (c8eb90f4).
Builds in `~/camera_builds` and on the pendrive `camera_project/camera_builds/`; rollback = `ksud module disable`.
