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

### Step 2: munch vendor camera stack (official HyperOS 1.0.9, in `out_tele/vendor.img`) [Observed]
- Sensor modules + tuning (`lib64/camera/`): OV64B40 (Sunny) and IMX582 (OFilm) main, OV8856 UW, IMX596 front (Sunny/OFilm),
  GC02M1 macro (Sunny/OFilm): `com.qti.sensormodule.*.bin`, `com.qti.tuned.*.bin`, EEPROM and actuator drivers.
- CamX/CHI core + 57 CHI nodes: Xiaomi HDR, `superlowlightraw` (night), `mibokeh`/`realtimebokeh`/`videobokeh`, `mifilter`,
  `misegment`, skin beautifier, AIIE, ASD, EIS v2/v3, LDC, remosaic (64 MP), SW registration, watermark, Vidhance AEC.
- Algorithms: ArcSoft (super-night RAW, HDR, MF super-resolution, portrait lighting, beauty), Xiaomi `libmialgo*` (AI vision,
  image enhance capture/preview, colour keeping, video enhance/segmentation), Almalence SR, Vidhance, SNPE + HTA runtime,
  `.dlc` models in `etc/camera/` (segmentation, front/back bokeh, AI enhance, tracking), 20+ filter LUTs.

### App profile [Observed]
The camera app contains only `com.mi.device.Marble`, `Marble_pre`, `Marble_pro` (POCO F5); no munch profile. Readable values:
`b1="2:9248x6944"` (OV64B40 full size), `p="true:4000x3000"`, `z8="ultra_wide:wide"`, `n="mfnr:1"`, DDF family 8781825.
126 obfuscated getters; meanings are confirmed only through behaviour on the phone.

### Step 3: classification [Inferred]
| Class | Items |
|---|---|
| Portable / native to SD870 | the whole official munch vendor stack above (made for this SoC) |
| Needs newer NPU/ISP | Xiaomi 17 vendor algorithms (`libmialgo*` for SM8850, QNN models, MIVI) — not present, not portable |
| Tied to source HAL | `quickcamera` service; laser AF (`sensor type 6`) and OIS link expected by the Marble profile |

### Problems seen in the log (2026-10-27, photo mode) [Observed]
| Log | Meaning | Priority |
|---|---|---|
| `FindBestSensorMode() FORCING SENSOR MODE 1 (4624x3472)` ×71, `MODE 0 (3264x2448)` ×20 | requested sizes do not match sensor mode tables; CamX overrides | check (quality/speed) |
| `DoStreamNegotiation() Could not extract snapshot stream (type -1)` | a feature graph got no snapshot stream | high |
| `WaitOfflineFeatureCompleted failed` | offline HDR/night processing not finished | high |
| `OIS_MANAGER: Sensor type does not match` | OIS data link mismatch | check (stabilisation) |
| `Laser … Sensor 6 probe failed` | profile expects laser AF; munch has none | low, disable cleanly |
| `GetInterpZoneDataGeneric did not find an appropriate zone` | AEC tuning table edge case | L4 tuning |
| beauty items FAIL, cloud-config JSON missing, shutter sound 6 missing | app-side mismatches | L1 |

### Next steps
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
- [x] **Watermark said "XIAOMI 17 PRO"** — fixed 2026-10-27. [Observed] The port's camera 6.7 is patched by the porter
      to always load a fixed `com.mi.device.Marble` device profile (log "Loaded direct 6.7 marble device profile"; marble =
      POCO F5). Its watermark table `Marble.d()` was hard-coded `{"XIAOMI", "17 PRO"}`; the system properties were
      already "POCO F4 5G". Patched to `{"POCO", "F4 5G"}` (only those 4 strings; dex 035, stored like the original),
      re-signed. Tested as KSU module `munch_cam_watermark`: photo watermark reads "POCO F4 5G". Reproducible with
      `tools/re/camera_watermark_patch.sh`; patched APK in `payload_tele/product/priv-app/MiuiCamera/` for the next release.
- [x] Analysis tools: Ghidra 12.1.4 (`~/re_tools/ghidra_12.1.4_PUBLIC`) and jadx-headless-mcp 0.7.1 (`~/re_tools/jadx/`),
      both checked against their published SHA-256. Helpers: `tools/re/Decomp.java` (JADX library: decompile chosen
      classes) and `tools/re/Smali.java` (dexlib2: disassemble/assemble a dex). REA's MCP registration still to do.
- [ ] Note: the camera app runs on the **Marble (POCO F5) device profile**; check which of its camera features/limits
      fit munch (Part B step 2) — this profile is the main L1 tuning lever.
- [ ] Part B step 2–4.

## Repository rule
Only our own scripts, patches, configs and docs go into git — no Xiaomi binaries, no backups.
