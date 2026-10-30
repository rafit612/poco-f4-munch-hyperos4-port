# 06 — Sensors and lenses (MASTER_PLAN P5)

Status: **in progress** (started 2026-10-28). Sources: HAL static metadata (`dumpsys media.camera`), `persist.vendor.camera.mi.module.info*`,
loaded vendor drivers, sensor-module / tuning files (kept off the repo). Tags: [Observed] / [Inferred].

## 1. Modules on this unit [Observed]
| Camera id | Sensor | Module | Focal / aperture | Pixel array | Notes |
|---|---|---|---|---|---|
| 0 main | OV64B40 64 MP (4-cell) | Sunny, actuator DW9800V, OIS via sensor hub (`02_KERNEL_CAMERA_VIDEO.md` §7) | 4.71 mm f/1.79 | 4624×3472 | min focus 10 cm |
| 2 ultra-wide | OV8856 8 MP | **AAC** | 1.65 mm f/2.2 | 3264×2448 | stereo partner for Portrait |
| 1 front | IMX596 20 MP (4-cell) | **OFilm** | 2.84 mm f/2.45 | 5184×3904 full (quad CFA), 2592×1952 binned | native camera saves 5184×3904 since v11 |
| 3 macro | GC02M1 2 MP | Sunny or OFilm (open) | 1.94 mm f/2.4 | 1600×1200 | fixed focus |
Other build variant in the vendor (not this unit): OFilm IMX582 48 MP main = **Redmi K40S** (China twin; same vendor software).
Public sources (2026-10-28 search): POCO F4 = OmniVision OV64B 64 MP (1/2", 0.7 µm, f/1.79), OV8856 8 MP ultra-wide, GC02M1 2 MP macro
(fixed focus ≈ 4 cm), Sony IMX596 20 MP front; K40S = Sony IMX582 48 MP main, same UW/macro. No public source names the module makers
(Sunny/OFilm/AAC). Front/macro maker on this unit stays open — same sensors either way; it only selects which tuning file is used.
Way to settle it later (with approval): raise CamX `logInfoMask` in a test overlay and read the module-probe line at provider start.

## 2. Main camera (OV64B40) limits exposed to apps [Observed]
* Hardware level 3 (FULL), OIS on/off available.
* ISO (sensitivity) **50–877** (max analog 796); exposure 73 µs – **32 s**.
* AE target fps ranges: 14–15, 14–30, 15, 24, 25, 30 → **no 60 fps range for Camera2 apps** (Xiaomi's camera records 60 fps through its own
  vendor path) → item for P8 step 10 (third-party apps).
* High-speed video: 240 fps at 640×480 / 720×480 / 1280×720, 120 fps up to 1920×1080. 960 fps slow motion (Munch profile) is Xiaomi's own path.
* Sensor-module file (`com.qti.sensormodule.munch_sunny_ov64b40_wide.bin`, 966 KB): 6 mode entries with `RemosaicTypeInfo`,
  `HDR3ExposureInfo` and `ZZHDRInfo` (sensor 3-exposure / zig-zag HDR support), PDAF (`ov64b40_pdaf`), OIS register block,
  separate still / movie / zoom-on / zoom-off settings.

## 2b. Other cameras, limits exposed to apps [Observed]
| Camera | ISO | Longest exposure | Focus | OIS | AE fps ranges | High-speed |
|---|---|---|---|---|---|---|
| Front IMX596 (id 1) | 50–3200 | 0.35 s | fixed | no | 11–30, 15, 24, 25, 30 | 120 fps up to 1280×720 |
| Ultra-wide OV8856 (id 2) | 50–853 | 10 s | **fixed** | no | 14–30, 15, 24, 25, 30 | none |
| Macro GC02M1 (id 3) | 50–600 | 0.43 s | fixed | no | 14–30, 15, 24, 25, 30 | none |
* **Plan step N11 settled:** the ultra-wide has no autofocus, so "macro through the ultra-wide AF" is not possible on this phone; macro stays on
  the 2 MP GC02M1 (or main-camera close focus at 10 cm + crop — to test in P8).
* Main camera ISO is capped at 877 for Camera2 apps while the front goes to 3200 → third-party low-light on the main camera is limited
  (GCam/LMC work around it with multi-frame).

## 2c. CamX module probe with test logging (2026-10-28, D2 test module, removed afterwards) [Observed]
| Camera | EEPROM / module | Checksums | Calibration data available |
|---|---|---|---|
| Main | `munch_sunny_ov64b40_gt24p128e_wide_eeprom` | all OK (0) | AF, WB, LSC, SPC, crosstalk, PDAF 2D; OIS gain (x 0x30d4, y 0x318f, delay 0x0f); dual-camera cal not in EEPROM (comes from `/persist`) |
| Front | `munch_ofilm_imx596_gt24p64e_front_eeprom` | OK | WB, LSC |
| Ultra-wide | `munch_aac_ov8856_gt24p64e_ultra_eeprom` | OK | WB, LSC |
| Macro | `munch_sunny_gc02m1_gt24p64e_macro_eeprom` | OK | WB, LSC |
Tuning files loaded: `com.qti.tuned.munch_aac_ov8856_ultra.bin` (index 2), `com.qti.tuned.munch_sunny_gc02m1_macro.bin` (index 3), main/front per module.
OIS: `OIS device found on camera 0` (only the main camera); sensor hub `ois_manager init`.

## 2d. Sensor modes seen by CamX (2026-10-29, CamX verbose init log, runtime override reverted) [Observed]
| Camera | Modes (max fps per mode) | Quad CFA raw | In-sensor HDR | Notes |
|---|---|---|---|---|
| Main OV64B40 | 6: 15, 30, 30, **60**, 120, 240 | 9248×6944 | IHDR supported | the 60 fps mode is classed as HFR: apps are not told about it, but a plain Camera2 request for [60,60] gets 60.03 fps (C3) |
| Front IMX596 | 4: 30, 30, 30, 120.07 | 5184×3904 | IHDR supported | full 20 MP and binned 2592×1952 both offered; min fps 11.1 |
* `InitializeScalerStaticCaps` limits each output size to the *normal* modes (max 30 fps) for the advertised capabilities.
* Both main and front report in-sensor HDR (IHDR); the app's video/photo HDR paths do not use it today (candidate for C1/U3).

## 2e. Macro / ultra-wide policy (plan item, 2026-10-30) [Observed numbers, Inferred image quality]
Static lens data (`dumpsys media.camera`): main id 0 min focus **10 cm** (10 dioptres), hyperfocal 0.11 dpt; ultra-wide id 2 and macro id 3
fixed focus (min focus 0), hyperfocal UW 1.81 dpt (≈ 55 cm → sharp from ≈ 28 cm to infinity), macro 2.23 dpt.
Close-up geometry (thin-lens estimate, circle of confusion = sensor diagonal / 1500):

| Camera at its closest distance | Frame width | Detail | Depth of field |
|---|---|---|---|
| Main, Photo 16 MP, 10 cm | 131 mm | 35 px/mm | ≈ 8.7 mm |
| Main, Photo + 2x (crop), 10 cm | 66 mm | 35 px/mm | ≈ 8.7 mm |
| Main, Ultra HD 64 MP, 10 cm | 131 mm | 70 px/mm | ≈ 8.7 mm |
| Macro GC02M1 2 MP, ≈ 4 cm | 55 mm | 29 px/mm | ≈ 4.8 mm |

Policy:
* **Close-ups: main camera first.** At 10–12 cm with 2x it frames almost the same area as the macro, with more detail, about twice the depth
  of field, OIS, autofocus and the full MFNR/HDR path; Ultra HD at 10 cm doubles the detail again. No camera change is needed for this.
* **Macro (id 3) only for subjects smaller than ≈ 6 cm** that must fill the frame; it is fixed focus, so the phone has to be moved to ≈ 4 cm.
  It stays available as it is (native "Macro" toggle, LMC back slot 2 = id 3). No tuning work on it: lowest priority in MASTER_PLAN and the
  2 MP sensor sets the ceiling.
* **Ultra-wide (id 2): daylight scenes only** (landscape, buildings, groups, ≥ 30 cm away). No OIS, no AF, ISO ≤ 853 → in low light prefer the
  main camera / Night mode. LDC (distortion correction) stays on (`eisoverridesettings.txt` LDC grid). It is also the Portrait depth partner, so
  its dual calibration (§3) must never be changed. LMC back slot 3 = id 2.
* **Not doing:** macro through ultra-wide AF (UW has no AF, N11 settled), extra macro/UW tuning modules.
* Open (owner, quick, indoor): one A/B of the same small object — Macro at 4 cm vs Photo 2x at 10 cm vs Ultra HD at 10 cm — to confirm the
  estimate in real photos (`MODE_TEST_RESULTS.md` will get the result).

## 3. Calibration [Observed]
* Dual-camera (main + ultra-wide) calibration: 455-byte factory file in `/persist` (2022) → 419-byte data used by HAL and app
  (`com.xiaomi.camera.algoup.dualCalibrationData`, `xiaomi.dualcal.streamsize` 4624×3472 + 3264×2448).
* AF calibration hint: `persist.vendor.camera.sensor.w.afInfo = 10:714,1000:403` (10 cm and 10 m lens positions) [Inferred].
* Per-module EEPROM drivers exist for every module (gt24p128e / gt24p64e / bl24sa64 / p24c64).
* **Unit calibration audit (N2, 2026-10-30, read-only) — result: calibration of this phone is intact.**
  * EEPROM of all four modules read by CamX with every checksum OK (§2c); main module carries AF, WB, LSC, SPC, crosstalk, PDAF 2D and OIS
    gain data; front / UW / macro carry WB + LSC.
  * `/mnt/vendor/persist/camera`: `com.xiaomi.dcal.wu.bin` and `.bak` (455 B each, **identical hash**, factory date 2022-06-28) and
    `com.xiami.camera.checksum.bin` = `camera:wu,result:1` (factory dual-camera calibration passed). Nothing written there (persist rule).
  * Module makers match this model's supplier set (Sunny main/macro, OFilm front, AAC UW, §2c) and the factory files predate the panel /
    power-key repair → no sign of a replaced camera module.
  * AF: `afInfo 10:714,1000:403` (DAC at 10 cm / 10 m) fits the 10 cm minimum focus distance (§2e). OIS found on the main camera only.
  * Back Portrait's preview depth works with this calibration; its crash is in the GPU engine, not calibration (`MODE_TEST_RESULTS.md`).

## 4. Still to do in P5
- [x] Limits for ultra-wide, front and macro (§2b). Sensor mode per camera mode: `03_FIRMWARE_HAL.md` §6b (binned mode 1 for Photo/Night,
  mode 3 4K video, mode 2 Pro, mode 4 HFR, 64 MP remosaic only in Ultra HD).
- [x] Module makers: main Sunny, front OFilm, ultra-wide AAC, macro Sunny (§2c).
- [x] Sensor HDR (3-exposure / zig-zag): tested as C1 (test module, `MODE_TEST_RESULTS.md`), closed.
- [x] Macro / ultra-wide policy (§2e).
- [x] Unused-capability audit (`06b_UNUSED_CAPABILITY.md`): HDR10 closed (HAL has no 10-bit streams), DSP HDR = C2 (kit verified,
  window test open), 60 fps for apps = C3 (closed, out of scope), sensor HDR = C1 (closed), NNAPI U7 + GPU budget done.
