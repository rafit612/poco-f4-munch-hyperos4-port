# Camera project — Xiaomi 17 (HyperOS 4) camera on POCO F4 5G + complete re-tuning

Goal: the best possible output on munch: Xiaomi 17 camera software where it can run on SD870, and complete tuning of
every image parameter for this phone's sensors. Results will not equal Xiaomi 17 hardware.
Findings are tagged **[Observed]** (seen on the phone or in the images) or **[Inferred]** (reasoned, not yet proven).

## Hardware (corrected)
| Camera | Sensor | Camera2 ID | Notes |
|---|---|---|---|
| Main | **OV64B40** 64 MP (Sunny), OIS, f/1.79 | 0 | [Observed] — not IMX582 (that was the original port's wrong tuning) |
| Ultrawide | OV8856 8 MP (AAC) | 2 | [Observed] |
| Macro | GC02M1 2 MP (Sunny) | 3 | [Observed] |
| Front | IMX596 20 MP (OFilm) | 1 | [Observed] |
| Logical/aux | IDs 4, 5, 6 | | [Observed] 7 camera devices |

ISP: Spectra 480; DSP: Hexagon 698 (HVX, no HTP tensor accelerator). [Observed]

## Part A — Safety (done 2026-10-27)
| Item | Result |
|---|---|
| boot, vendor_boot, dtbo, vbmeta | fastboot images in `rom_extract/images` [Observed] |
| vendor, system, system_ext, product, mi_ext, odm | fastboot images `secure_build/out_tele`, `out_sunday_plus/odm.img` [Observed] |
| TWRP / OrangeFox | not available for this Android 17 build; rollback = fastboot flash of the images above |
| `/persist` + EFS (modemst1, modemst2, fsg, fsc) | backed up read-only, SHA-256 matched on phone and PC; kept **outside git** in `~/poco_f4_private_backup/2026-10-27/` (contains IMEI) [Observed] |
| Rule | `/persist` and EFS are never written or wiped by this project |
| Module method | KernelSU module, changes applied with `post-fs-data.sh` bind mounts (`ksud` module file-overlay mounting is not active on this phone) |
| One-command rollback | tested: `su -c "ksud module disable <id>"` + reboot removed the test module's property and bind mount [Observed] |
| Flashing / partition writes | only after the user says yes |

## Part B — Port
### Step 1: inventory of the source (official Xiaomi 17 Global HyperOS 4, `stock_rom_global17`, OS4.0.0.9)
Available partitions: system, system_ext, product, mi_ext. **Not available: vendor, odm** (where Xiaomi 17's CamX/CHI,
`libmialgo*`, MIVI and AI model files live). [Observed]

| Source component | In our ROM? |
|---|---|
| MiuiCamera (Global 6.6.000570.5) | ours is **6.7.000070.0** (Xiaomi 17 China base, newer) [Observed] |
| `libcamera_algoup_jni`, `libcamera_mianode_jni`, `libMiVideoFilter`, `libcameramindmsger`, `libvirtualcamera_*` | identical files [Observed] |
| `libcameraimpl`, `libcameraopt(_jni)`, `libcameramind`, `libmivideo`, `libcameradngimpl`, deferred camera service | present, different (newer China-base) builds [Observed] |
| `vendor.xiaomi.hardware.quickcamera-V1-ndk.so` | missing; it talks to a Xiaomi 17 vendor service munch does not have [Inferred] |
| CameraTools_beta, CameraMind, `cameraopt*.json`, `camerascene.json`, `cameracustomize.json` | CameraMind present; configs to compare in step 2 |
| `libmialgo*`, MIVI, `*.dlc/*.qnn` AI models, CHI nodes | not in the available partitions; built for the Snapdragon 8 Elite-class NPU/ISP → **class "Needs newer NPU/ISP"** [Inferred] |

Conclusion: the app-level Xiaomi 17 camera is already ported; the work is mainly **tuning** (Part C) on the official
OV64B40/OV8856/IMX596/GC02M1 HAL tuning.

### Next steps
- Step 2: inventory munch's vendor camera HAL (CamX/CHI), sensor modules, tuning binaries, `device_features`, `dumpsys media.camera`.
- Step 3: classify every library (portable CPU/GPU, needs newer NPU/ISP, tied to source HAL).
- Step 4: module with app-config fixes, correct camera-ID mapping, unsupported features disabled cleanly.

## Part C — Tuning (main focus)
Layer order: L1 app config / feature flags → L2 Camera2 request params + Xiaomi vendor tags → L3 app post-processing
(LUT / shader / tone curve) → L4 HAL tuning binaries (only with approval per change).
Per camera (main, UW, macro, front) and mode (photo, night, portrait, HDR, pro, video): colour/AWB (tube light, sodium,
warm LED; natural South Asian skin tones; Leica Authentic/Vibrant as 3D LUTs; cross-camera match), sharpness, per-ISO
noise, exposure/local tone mapping, focus, portrait edges/bokeh, video (4K30/60, 1080p60, HEVC, EIS+OIS, no 50 Hz
flicker), performance (shutter lag, night time, 10-min 4K thermals).

## Part D — Workflow
Named profile per change (git), fixed test scenes, comparison scripts (SNR, Laplacian sharpness, clipped highlights,
ΔE on a colour chart, skin hue), one comparison sheet + recommendation per round.

## To-do
- [ ] **Watermark still says "Xiaomi 17"** — find where the camera app takes the device name for the watermark (app
      config / device features / build props) and make it "POCO F4 5G". (reported 2026-10-27)
- [ ] REA analysis engines: REA (rea-agents 6.8.0) needs Ghidra 12.1 and/or a jadx-headless-mcp 0.7.1 JAR supplied
      separately; decide whether to download them.
- [ ] Part B step 2–4.

## Repository rule
Only our own scripts, patches, configs and docs go into git — no Xiaomi binaries, no backups.
