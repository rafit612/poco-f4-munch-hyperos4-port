# Gate G2 — layer maps complete? (MASTER_PLAN P6 → P7)

Prepared 2026-10-28 for the owner's review. Question for G2: *are the maps of app → Android → HAL → kernel → firmware → hardware complete
enough to design improvements (P7)?*

## 1. What is mapped
| Layer | Document | Status | Key results |
|---|---|---|---|
| App + Android (P2) | `01_APP_OS_LAYER.md` | 6/7 done | 55 modes (41 on / 13 off / 1 conditional), opmode + camera id for 17/19 visible modes, MIA engine chain, 729 HAL vendor tags vs 263 missing for the app, services + SELinux (all denials explained) |
| Kernel (P3) | `02_KERNEL_CAMERA_VIDEO.md` | **done** | 15 camera driver groups, active devices, Venus (HEVC Main10, HDR10+, 160 Mbit/s), NPU/CVP/DSP/GPU users, port vs stock drivers, stage ↔ tuning map, **OIS = sensor hub** |
| Vendor HAL + firmware (P4) | `03_FIRMWARE_HAL.md` | 1 done + 4 partly | modules on this unit, CamX/CHI files, `camxoverridesettings.txt`, main-camera Chromatix blocks, HDR/PSN/bokeh configs, 133 pipelines |
| Sensors + lenses (P5) | `06_SENSORS_LENS.md` | 2 done + 4 partly | limits of all 4 cameras, calibration, K40S vs POCO F4 variants, ultra-wide fixed focus (N11 settled) |
| Unused hardware (P5) | `06b_UNUSED_CAPABILITY.md` | first list | 15 items (U1–U15); owner-approved C1–C5 in the plan |
| Map (P6) | `INDEX.md`, `graphify-out/graph.html` | 3/4 | 83 concepts, 155 links, 8 groups, health OK |

## 2. Open items carried forward (do not block P7)
| Item | Why open | Where it goes |
|---|---|---|
| Which CHI usecase each opmode selects; front/macro module maker | HAL logging is off (`logInfoMask=0`) | needs the test-logging decision (§3 D2) |
| Marble vs Munch profile values | profile code is obfuscated | traced per value in P8 when a feature needs it |
| Firmware images MIUI 13/14 vs HyperOS 1 | not compared yet (images on pendrive) | P7 background task |
| Sensor RAW HDR, DSP HDR (`hdsr`), NNAPI device list, GPU/DSP load budget, OIS really active | need on-phone tests | P7 rating → P8 tests (C1, C2, C4, OIS test) |
| HDR10 encoder profile at runtime | needs a runtime codec query | P8 with U1 |
| Back Portrait crash | engine contract / Android 17 under OpenCL; needs native tracing | stays in P1; LMC is the workaround |

## 3. Decisions for the owner
* **D1 — Pass G2 and start P7?** P7 = rank every candidate (C1–C5, U1–U15, colour/tone tuning against the reference library, third-party
  app fixes) by gain / risk / effort; output `07_IMPROVEMENT_PLAN.md` → gate G3.
* **D2 — Allow a test-only HAL logging overlay?** A KSU test module that bind-mounts a copy of `camxoverridesettings.txt` with
  `logInfoMask` and `enable3ADebugData` / `enableTuningMetadata` raised. Read-only for the phone's partitions (no flashing), removed with
  `ksud module disable`. Unlocks: usecase per mode, module maker, and the AE/AWB data per photo that colour tuning in P8 needs.
  Risk: more log output and slightly slower capture while the module is on; SELinux stays enforcing.

## 4. Owner answers (2026-10-28)
* D1: **Pass G2, start P7.**
* D2: **Yes, allow test logging** (test-only module, removed afterwards).
