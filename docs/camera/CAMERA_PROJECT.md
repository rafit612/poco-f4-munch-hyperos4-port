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

## Mode test, 2026-10-27 (camera 6.7 + Marble profile, automated: open mode, take one shot, read crash log) [Observed]
| Mode | Result |
|---|---|
| Photo, Pro, Video, Documents, ID photo, Time-lapse, Slow motion, Dual video, Ultra HD, Long exposure | no crash, file saved |
| Night | works, but ~870 error lines in the log (most of any mode) — to examine |
| Short video | opens, no file saved by the test (needs a manual check) |
| Movie, Panorama | not reached by the test script (panel position) — manual check |
| **Portrait (back)** | **crashes the app** on opening: depth engine (`libwa_depth` → `libanc_dc_base`) aborts on a zero-size tensor |

Portrait experiments (all rolled back; v3 = watermark + E1 25 + C 4625 is installed):
- force non-calibrated depth (`persist.vendor.camera.forcenoncalib=1`): same crash → calibration file is not the cause;
- bokeh picture width 4000 → 4625 (official `Munch_pro` value): depth stream is now 4624x3472, same crash;
- official 5.1 `libcamera_algoup_jni` instead of the port's: app dies at start (`init(String)` missing) → different JNI version;
- app opmode 0x9003 (single bokeh) or 0x9005 (normal): app survives but the **camera HAL crashes**
  (`CamX::Session::Initialize` null deref while creating an offline feature graph). Not fixable at app level.
Leica style button (top right) is only a two-way Leica Vibrant/Authentic switch; the 7 extra looks (E9.i table) are not in the
filter strip, which is built from `cloud_filter_*.json` (15 entries). `Marble.E1` 17→25 did not add them.
Official munch app 5.1 (`stock_rom_1.0.9` product) has the real `com.mi.device.Munch`/`Munch_pro` profile (K40S/F4 watermark,
zoom "capture:0.6:1.0:2.0", 960 fps slow-mo, `Oooo00o`=4625).

### Portrait crash — root-cause narrowing, 2026-10-27 [Observed]
- Crash = **dual-camera depth only**: back Portrait aborts, **front Portrait (single bokeh, same `libanc_dc_base` neural-network library) works**.
- The abort is on a worker thread of `libwa_depth` (`dc_nnstereo_helper`: loads the stereo model, prints model size, runs the first network
  pass); tensors have zero size (`WarpPerspective img={1,15,2,20,4} mat={1,0,0} out2d={0,0}`; other runs: `layout.shape[i]`, `bad input shape`).
- **Ruled out:** calibration file (also with `forcenoncalib=1`), depth size 4000→4625, `capture_cache/model/policy` (byte-identical to stock
  HyperOS 1.0.9), `dof_l11r_mecp.bin` present, `ro.hardware.chipname` (unset on stock too), ultra-wide-bokeh pref, app JNI bridge
  (official 5.1 bridge: `init(String)` unresolved), forcing single/normal opmode (HAL itself crashes: `CamX::Session::Initialize`).
- The official 5.1 app cannot be used as an A/B test: built for Android 13, its engine bridge does not load on this Android 17 system.
- Vendor engine files and models are identical to stock, so the remaining differences are the **port kernel (4.19.325 vs stock 4.19.157)**,
  the Android 17 runtime (bionic/libc++/linker namespaces/SELinux) and the 6.7 app's graph descriptor. Next: stock-kernel RAM boot (A/B),
  then trace `dc_nnstereo_helper` with Ghidra/strace.

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
- [ ] **Leica looks (Xiaomi 17)** — patched 2026-10-27, waiting for the phone test. [Observed] Photo filters are LUTs inside
      the app (275 `res/raw/lut_*`, rendered by the app, no HAL needed), including the 7 new Xiaomi 17 Leica looks
      (`lut_l_chr/cls/cnt/etn/brs/tel/ia`, app effects 248–254). The device profile's `E1()` picks the back-camera set:
      16 = L_CUSTOM_BACK (Leica Vivid/Natural + mono), **17 = NORMAL_CUSTOM_BACK (Marble's value, no Leica)**,
      25 = LC_CUSTOM_BACK (Vivid, Natural, Chrome, Classic, Contemporary, Eternal, Brass, Teal, IModelA). All E1 callers
      are filter code (EffectController, `Ii.i0`, `w2.S`). Patch: `Marble.E1()` 17 → 25, in `camera_watermark_patch.sh`.
      Video mode is different: the app sends a HAL ID in `xiaomi.videofilter.filterApplied` (table `E9.i`: Vivid 129,
      Natural 130, Chrome…Teal 169–174, IModelA 175 — same IDs as the Xiaomi 17 `odm/etc/camera/videofilter/*.png`), but
      munch's `com.xiaomi.node.mifilter.so` only knows IDs 102–128 → Leica in **video** needs a HAL table patch (later).
      Lesson: an APK copied in with `adb push` keeps owner `shell` and label `shell_data_file`; PackageManager then drops
      the app ("System package … no longer exists; its data will be wiped"). Always `chown root:root` +
      `chcon u:object_r:system_file:s0` before the reboot.
- [ ] Note: the camera app runs on the **Marble (POCO F5) device profile**; check which of its camera features/limits
      fit munch (Part B step 2) — this profile is the main L1 tuning lever.
- [ ] Part B step 2–4.

## Repository rule
Only our own scripts, patches, configs and docs go into git — no Xiaomi binaries, no backups.

## Log 2026-10-30 night: photo stage on the phone
- Soft native photos = HAL noise reduction; the answer for now is a post-capture stage, not a camera patch. PhotoStage app (`tools/camera_lab/photo_stage_app`): OpenCV NLM + detail/tone/colour, JobScheduler watcher, copy to Pictures/PhotoStage, originals untouched. Details and numbers: `08_PHOTO_STAGE.md`.
- Release APK built (not debuggable, project key outside the repo), installed on the phone, tested on a real native photo (copy in ~30 s). Staged for the next product build in `secure_build/payload_tele/product/app/PhotoStage/`.
- What only the owner can do is collected in `OWNER_HELP_NEEDED.md`; plan state in `PLAN_STATUS.md`.

## Imported 2026-10-31 from branch claude/sleepy-turing-kznnh7 (Portrait investigation of 2026-10-27)
### Portrait crash investigation (2026-10-27) [Observed unless marked]
Symptom: the camera aborts ~1 s after Portrait (back camera) opens, before any shot:
`libwa_depth.so → libanc_dc_base.so`, `DNNError: assertion layout.shape[i] && layout.stride[i] >= 0`, thread
`ParallelDataZip`, right after the depth runtime loads `/vendor/lib64/libOpenCL.so`. Same crash before and after the
Leica change, so it comes from the port, not from our patches.

Reference: official munch camera **5.1.001140.0** (HyperOS 1.0.9) has a real `com.mi.device.Munch` / `Munch_pro`
profile; `ro.boot.camera.config=0` selects `Munch_pro` (OV64B40). It uses dual bokeh on the back camera too
(`SESSION_OPERATION_MODE_ALGO_UP_DUAL_BOKEH`, 0x9000), writes the same calibration file from the same HAL tag, and
the same 7-function engine API (`MIAInit … MIAProcessFrameWithSync`).

| Tried | Result |
|---|---|
| Portrait max width 4000 → 4625 (Munch_pro value); sizes now native 4624×3472 | still crashes |
| `persist.vendor.camera.forcenoncalib=1` (non-calibrated depth) | still crashes → calibration ruled out (reverted) |
| Official 5.1 `libcamera_algoup_jni.xiaomi.so` (RAM bind mount) | app cannot start: `init(String)` missing (removed) |
| Back Portrait forced to single bokeh (0x9003) | camera HAL provider crashes (SIGSEGV) → reverted |
| Stream binding to physical cameras | same condition as 5.1 (MediaTek only) → not the cause |

**Strongest remaining lead [Inferred]: SELinux app domain.** 5.1 is platform-signed and runs as `platform_app`;
munch's vendor policy (v30, Android 11 era) grants its camera/GPU/DSP/property rules to `platform_app`/`priv_app`.
The re-signed 6.7 runs as **`priv_app_36`**, a domain that did not exist when the vendor policy was written, so none
of those vendor rules apply (already seen: touchfeature `find`, `vendor_display_prop`, `vendor_frc_prop`,
`vendor_camera_sensor_prop`, `ptrace` denials). A depth runtime that silently fails to open a backend or a file
(SNPE/CDSP, OpenCL cache) can end with zero-sized tensors. Some denials may be hidden by `dontaudit`.

Decisive, reversible test (phone + root): `tools/re/portrait_selinux_test.sh diag` (`setenforce 0` → Portrait →
`setenforce 1`, nothing written).

**Proposed fix (if `diag` shows no crash):** run the camera in the same domain as HyperOS 1, not new rules for every
`priv_app_36` app. One line in `product_seapp_contexts`:
`user=_app isPrivApp=true name=com.android.camera domain=platform_app type=app_data_file levelFrom=all`
(`name=` outranks `isPrivApp`/`minTargetSdkVersion` in seapp matching, so only the camera moves). PackageManager
relabels app data when the seapp hash changes. Test first as KSU module (`portrait_selinux_test.sh install`, reboot,
`check`; `remove` to undo), then bake into `payload_tele/product/etc/selinux/`.
Fallback if seapp is refused: `(typeattributeset platform_app_30_0 (priv_app_36))` in `product_sepolicy.cil` gives
every priv_app_36 app the vendor's platform_app rules — broader, needs the offline secilc compile (AGENTS rule 2).
- No crash with permissive → write the missing `priv_app_36` rules (copied from the vendor's `priv_app` /
  `platform_app` rules for camera) into `product_sepolicy.cil`, after `dontaudit` is lifted once
  (`semodule`-free: `auditallow`-style check via `dmesg` with permissive) and an offline `secilc` compile (AGENTS rule 2).
- Still crashes → the cause is in the app↔engine data (6.7 vs 2022 depth engine 2.5.3); then compare the
  MIA session parameters of 5.1 and 6.7 frame by frame, and fall back to hiding dual-camera Portrait cleanly.

**Second suspect [Observed in `audit/agents/camera/inventory.tsv`]:** every depth/bokeh engine file
(`libwa_depth`, `libanc_dc_base`, `libmialgoengine`, `libmibokeh_855`, `dof_l11r_mecp.bin`) is byte-identical in
MIUI 14, HyperOS 1.0.9 and the port, so the engine itself is not the difference. But the wide+ultra dual-camera
reference files `etc/camera/com.xiaomi.dcal.wu.golden` and `.golden2` are the same in MIUI 14 and HyperOS 1
(`c0e7e796…`) and **different in the port** (and different from each other). Whether today's vendor image still has
the porter's copies must be checked on the phone. Test: `portrait_selinux_test.sh golden <folder>` (RAM-only bind
mount of the official files). If that fixes Portrait, add both files to `payload_tele/vendor/etc/camera/`.
**Third suspect [Observed in `audit/agents/rom/*_system_ext.tsv`]:** official HyperOS 1 `system_ext` ships
`lib{,64}/libopencl-camera.so`; the port has none (both have `libOpenCL_system.so`, different builds, and different
`public.libraries-qti.txt`). The depth engine runs inside the camera app and aborts right after it loads OpenCL.
Test: `portrait_selinux_test.sh opencl <official system_ext root>` (KSU module, reboot; adds the two libraries and any
official public-library entries the phone lacks).
Other HyperOS 1-only camera files (no Portrait link seen yet): `vendor.xiaomi.hardware.quickcamera-V1-ndk_platform.so`,
`etc/camerabooster.json`, `CameraTools_beta`.
Order on the phone: `diag` first (one step, no change), then `golden`, then `opencl`, then `install`.

HyperOS 4 Portrait features that can come over afterwards [Inferred]: the 6.7 Portrait UI (bokeh strength, Leica
portrait looks, lens styles) is app-side and stays; anything that needs Xiaomi 17's MIVI/NPU bokeh models does not
exist on munch's vendor and runs on munch's own `mibokeh`/JiiGAN engines instead.

## Log 2026-10-31: v15 in the ROM, project paused
- Flashed T20261031b: camera v15 (crashing modes hidden, finished videos no longer deleted) + PhotoStage (`ROM_HISTORY.md` §12).
- PhotoStage: testing the `/product` copy exposed five defects, all fixed (`08_PHOTO_STAGE.md`); colour made gentler after the daylight shots.
- Noise reduction off: tested indoors, worse, not shipped. On-phone AI stage dropped by the owner. Back Portrait, Night purple and soft native photos are known limits: use LMC.
- Paused until the owner has taken more photos and videos: `FINAL_REPORT.md` section 8, `OWNER_HELP_NEEDED.md`.
