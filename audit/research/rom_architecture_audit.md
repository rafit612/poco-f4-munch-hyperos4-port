# POCO F4 (munch) Full Global port: architecture audit

Date: 2026-10-23. This audit was read-only: no images were built and nothing was flashed.

What was compared:
- **Our images:** `out_global` system, system_ext and mi_ext, plus vendor (mounted at `$S/ourv`). `product` was being rebuilt, so the product payload and the original port product (`mnt_prod`) were used instead.
- **Official munch:** HyperOS 1 V816.0.9.0.ULMMIXM (`stock_rom_1.0.9`).
- **Original port vendor:** `audit/port/vendor.img` (mounted at `$S/opv`).
- **Xiaomi 17 Global:** OS4.0.0.9 (`g17_*`).
- **Logs:** `scratchpad/logs/*.log` (`full.log`, `after_flash.log`, `now*.log`, `tp.log`).

## 1. Partitions and versions

| Partition | Fingerprint / build | Android / SDK | Security patch |
|---|---|---|---|
| system | Android/generic_system/generic:17/CP2A.260605.016/17OS4.0.260822.110918348.QCPECN.S | 17 / 37 | 2026-08-01 |
| system_ext | Xiaomi/missi/missi:17/... (same build as system) | 17 / 37 | - |
| product | Xiaomi/munch/miproduct:17/CP2A.260605.016/OS4.0.0.24.XPKCNXM | 17 / 37 | 2026-08-01 |
| mi_ext | Xiaomi 17 Global (pudding) mi_ext, cleaned, with a munch build.prop | - | - |
| vendor | Redmi/munch/munch:13/RKQ1.211001.001/V816.0.9.0.ULMMIXM (official, plus our edits and the porter's libraries) | 13 / vendor SDK 30 | 2025-04-01 |
| odm | Redmi/munch/munch:13/RKQ1.211001.001/**V816.0.5.0.ULMCNXM** (China, older than vendor 0.9 MIXM) | 13 | - |
| boot | POCO/munch_global/munch:13/.../V816.0.9.0.ULMMIXM; kernel **4.19.325-zyndong-perf** (porter kernel) | - | - |
| Official HyperOS 1 for comparison | system and product missi_phone_global:14/UKQ1.231207.002/V816.0.9.0.ULMMIXM | 14 / 34 | 2025-04-01 |

- `ro.vndk.version` = 30.
- `ro.board.api_level` and `ro.board.first_api_level` = 30; `ro.product.first_api_level` = 31.
- Platform `kona`; verified boot state `orange` (unlocked).
- So a **SDK 37 framework runs on an SDK 30 (R-frozen) vendor**. Every new HyperOS 4 hardware interface (AIDL touchfeature, perf2, Uniperf, the Rust runtime 3.9 apps) falls back or fails.

## 2. Mismatches between HyperOS 4 and the HyperOS 1 vendor

### 2.1 Camera (the cause of purple night, magenta colour cast, portrait crashes and the "Xiaomi 17" watermark)

**Camera app**
- The port uses MiuiCamera **6.7.000070.0**, signed with a non-platform certificate (`16:40:AA…`).
- Official munch ships **5.1.001140.0**, signed with the platform key (`C9:00:9D…`).
- Portrait crashes abort inside vendor `libanc_dc_base.so` / `libwa_depth.so` with `base_exceptions::DNNError assertion layout.shape…` (see `crash2.txt`).
- Night photos are purple: average RGB (142, 52, 155).
- Normal photos carry a magenta cast, with red about 20 above green.

**Vendor camera stack**
- The porter replaced it: 50+ files differ from official and are identical to the original port vendor (`opv`), so this isn't from our build.
  - `lib{,64}/hw/camera.qcom.so`
  - all 3A libraries: `com.qtistatic.stats.{aec,af,awb,pdlib}.so` and `com.qti.stats.{aec,af,awb}wrapper.so`
  - `com.vidhance.stats.aec_dmbr.so`
  - EIS nodes `eisv2` and `eisv3`
  - Xiaomi nodes `AIIE`, `mimovie`, `rearvideo`, `watermark`, `misegment` and `facepp siq`
  - tuning (chromatix) binaries:

| Tuning file | Official H1 | Port | MIUI 14 |
|---|---|---|---|
| `com.qti.tuned.munch_sunny_ov64b40_wide.bin` (**this phone's main sensor**) | 1574c378 | b8d74a8b | 8b0e69f7 |
| `com.qti.tuned.default.bin` | 39.6 MB | 67 MB | - |
| `tuned.munch_aac_ov8856_ultra.bin` (this phone's ultrawide) | differs from port | differs | - |
| `tuned.munch_sunny_gc02m1_macro.bin` | differs from port | differs | - |
| `tuned.munch_sunny_imx596_front.bin` | differs from port | differs | - |

  - The only identical tuning for this phone's modules is the `ofilm_imx596` front.
  - Sensor module binaries are identical to official.
  - Our own vendor edit is `etc/camera/camxoverridesettings.txt`: debug and metadata lines removed, `HighQualityQuickShotSupportMask=0x000000` added.

**This phone's modules** (`persist.vendor.camera.mi.module.info`):
- back_main **Sunny OV64B40**
- back_ultra **AAC OV8856**
- back_macro **Sunny GC02M1**
- front **OFilm IMX596**
- So this unit has the OmniVision main sensor, not the Sony IMX582.

**Fix:** use official camera 5.1 (`product`, staged) **plus** restore the whole official HyperOS 1 camera vendor set:
- `lib/` and `lib64/` `camera/**`
- `lib{,64}/hw/camera.qcom.so`
- `lib64/libanc*`, `libwa_depth*` and related, if they differ
- keep our `camxoverridesettings` edit only if needed

The app and the HAL must come from the same build. This needs a **vendor rebuild**; risk is medium, and only the camera is affected, with a rollback image available.

**Extra benefit:** camera 5.1 is platform-signed, so it runs as `platform_app`. Vendor policy allows `platform_app` to find `hal_touchfeature_xiaomi_hwservice`. Camera 6.7 ran as `priv_app_36` and was denied (`tp.log`: 34 times `find interface=vendor.xiaomi.hardware.touchfeature::ITouchFeature`, plus `vendor_display_prop`/`vendor_frc_prop` read denials).

### 2.2 Rust runtime (HyperOS "RustProcess")

- The port's `system_ext` has runtime **3.1.0** (`init.hyos_spawner.rc`, `libhyper_os_shell.so` 86,896 bytes).
- Xiaomi 17 Global has **3.9.0** (`libhyper_os_shell.so` 103,600 bytes, with the new `--app-lib-search-paths` and "app-owned sonames").
- Global Gallery 5.4.2.10 (`hyperos.rustruntime.v3`) crashed with SIGSEGV in `HyosSignalCatch` after `Failed to link namespace(default) to rust_app_libs`. This is already fixed by going back to Gallery 4.3.1.6-global.
- Weather Global declares `hyperos.app.rust_runtime_version=3.1.0`, so it's compatible.
- MiuiHome (the port's) is fine.
- **Rule:** any HyperOS 4 Global app that declares runtime above 3.1 must not be added. Check with `aapt2 dump xmltree AndroidManifest.xml | grep rust_runtime_version`.

### 2.3 TouchFeature (double-tap to wake, edge, game mode)

- The vendor provides only HIDL `vendor.xiaomi.hardware.touchfeature@1.0::ITouchFeature/default` (`lshal`: pid 1430), labelled `hal_touchfeature_xiaomi_hwservice`, the same as official.
- HyperOS 4 clients first look for AIDL `vendor.xiaomi.hw.touchfeature.ITouchFeature/default` and the new HIDL `vendor.xiaomi.hw.touchfeature::ITouchFeature`. Neither exists, so apps get `NoSuchElementException` and "v1/v2 HIDL service and v1 AIDL service not found", seen from the camera (pid 30660).
- `system_server` falls back to HIDL v1 and works.
  - A live test of switching `gesture_wakeup` gave `TouchWakeUpFeatureManager: Update state … mode = 14, newState = 1`, then `TouchFeature: setModeValue mode:14`.
  - Mode 7 (edge) and mode 8 (game) are also applied.
- **Double-tap to wake is correct in the ROM.** The remaining failure is in the panel's touch IC firmware (aftermarket screen, `fts_ts`). There's nothing to fix in the ROM.
- Home-screen double-tap to lock was off (`flutter … canDoubleTapLock=false`). `secure.double_tap_to_sleep` has now been set to 1.

### 2.4 Fingerprint (Goodix, in-display)

- `vendor/lib64/libgf_hal.so` differs: port `cace4777` (same as original port) vs official `820bdfc0`.
- `etc/permissions/android.hardware.fingerprint.xml` was changed by us (feature hidden or adjusted earlier).
- **Fix option (vendor rebuild, low to medium risk):** restore the official `libgf_hal.so` as a test. Weak response can also come from the aftermarket panel's lower light transmittance. Re-enrolling the fingerprint after a library change is required.

### 2.5 Audio and ultrasonic proximity (Elliptic)

- `audio.primary.kona.so`: port `2e3a0e69` vs official `e4b29429`.
- `sound_trigger.primary.kona.so`: port `792fd3d8` vs official `b609af26`.
- `audio_effects` has the porter's V4A additions.
- With the screen on, ultrasound proximity is active (`ultrasound-proximity=1`), and low-latency speaker playback fails 5,550 of 5,552 times: `pcm_prepare returned -1`, `record_playback_fail -5`, AudioFlinger blocked about 165 ms per write. It works with the sensor off.
- **Fix option (vendor rebuild, medium risk):** restore the official `audio.primary.kona.so` and `sound_trigger.primary.kona.so` (32- and 64-bit). Then test speaker, earpiece, calls, Bluetooth and the proximity sensor during calls, and roll back if audio breaks.

**Update 2026-10-25:** the official audio HAL and sound trigger are in the image. The remaining audio fault was a DSP
restart loop caused by Google's hotword DSP model with the port kernel's built-in audio drivers; worked around in
vendor + system (see `hardware_subsystems_audit.md` section 4 update and `port_fixes/soundtrigger_fix/README.md`).

### 2.6 Display

- `displayfeature.default.so` differs: port `af9c06f8` vs official `f35aa3bf`.
- The display HAL logs look healthy: IGC, DC and LTM messages, and brightness ramps correctly.
- The brightness swings seen earlier were caused by the restored setting `screen_auto_brightness_adj=0.49`, not by the HAL.
- Keep as is, unless DC dimming or colour problems appear.

### 2.7 Thermal

- The official vendor has `etc/thermal-hp-mgame.conf` and `thermal-hp-normal.conf` (the high-performance mode profiles). **Both are missing from ours and from the original port.**
- Ours adds `thermal.current.ini`.
- `powerkeeper` logs `thermalPerfStatus open failed` 31 times.
- `system_app` (`ThermalCollector`) is denied reading `vendor_sysfs_kgsl_gpuclk`, which is telemetry only.
- **Fix:** restore the two official `thermal-hp-*` files (vendor, low risk). Performance mode then gets its proper profile.

### 2.8 Perf and Uniperf

- `UniperfJavaClient: Failed to get Uniperf service` 76 times, and `UniperfService is invalid`. The HyperOS 4 Uniperf HAL doesn't exist on the SD870 vendor.
- `libbinder: Failed to get isDeclared for vendor.qti.hardware.perf2.IPerf/default … SELinux denied`. The client falls back to HIDL `vendor.qti.hardware.perf@2.2`, which logs `Unknown params` 12 times for HyperOS 4 opcodes it doesn't support.
- **Impact:** some newer frame and boost hints are ignored. Basic perf boosts work.
- **No safe fix.** The Uniperf HAL can't be backported, and the perf2 AIDL doesn't exist on this vendor.

### 2.9 PowerInsight "calculateCpuCurrentPower, NO processorPower"

- About 4,290 times in roughly 20 minutes.
- `power_profile` comes from `vendor/overlay/FrameworksResTarget.apk`, which is **identical to official** (`90fffc52`).
- It uses the legacy cluster format: `cpu.clusters.cores` = 4, 3, 1, with `cpu.core_speeds.cluster0..2` / `cpu.core_power.cluster0..2`.
- Its frequencies exactly match the live kernel tables:
  - policy0: 300 MHz to 1.8048 GHz
  - policy4: 710.4 MHz to 2.4192 GHz
  - policy7: 844.8 MHz to 3.1872 GHz
- PowerInsight (HyperOS 4 `system_ext`) reads PowerProfile per cpufreq policy and evidently wants the newer per-policy keys (`cpu.scaling_policy` / `cpu.scaling_step_power.policyN`).
- **Impact:** only log spam and missing per-app CPU power statistics. No functional effect.
- **Fix option (low priority):** add the per-policy entries to a product RRO overlay targeting android, or ignore.

### 2.10 Joyose, MiSight and game services

- Joyose's `vendor_dpmtcm_socket` write denials (101) also happen with official policy, since the vendor CIL is identical. Harmless.
- MiSight Global `nativeSendEvent fail` (225) is telemetry, and the MiSight daemon interface is missing on the vendor. Harmless.
- `com.xiaomi.migameservice` isn't installed; Game Turbo uses Joyose and SecurityCenter. Fine.

### 2.11 Other vendor differences (porter, kept)

- **Adreno GPU driver:**
  - `lib{,64}/egl/*adreno*`, `vulkan.adreno.so`, `libgsl`, `libllvm-*`, `libCB`, `libOpenCL`
  - a650 firmware `a650_sqe` / `a650_zap`
  - added `libllvm-qgl`, `libOpenCL_adreno`, `libadreno_compiler_cl`, `libdmabufheap` and `android.hardware.vulkan.version-1_3.xml`
  - Driver version 0805.0. This is most likely needed for the Android 17 framework, so keep it.
- **IPA firmware, `libril-qc-hal-qmi.so`, `libmt@1.3.so`, `libssccalapi.so`:** porter changes. Keep, because calls, data and sensors work.
- **Missing vs official:** `etc/permissions/com.google.android.feature.PREMIER_TIER.xml` (Google premier-tier device flag). Optional to restore (vendor, low risk).
- **Added by the porter:** an IR HAL (`android.hardware.ir-service`), a `vibrator-bridge`, Xiaomi OTRP agent, Qualcomm SLA, a Rongcard eID service, and `libkernelmanager`.

## 3. Ranked fix candidates

| # | Fix | Impact | Risk | Partition |
|---|---|---|---|---|
| 1 | Official camera 5.1 (staged) **plus** official HyperOS 1 vendor camera stack (camera.qcom.so, 3A/EIS/Xiaomi nodes, all tuned bins) | Purple night, magenta cast, portrait crash, watermark | Med | product + **vendor** |
| 2 | Official `audio.primary.kona.so` + `sound_trigger.primary.kona.so` (32/64-bit), as a test | Speaker system sounds fail with the screen on | Med | vendor |
| 3 | Official `libgf_hal.so`, as a test (re-enrol the fingerprint) | Weak fingerprint (the panel may still limit it) | Low-Med | vendor |
| 4 | Restore `thermal-hp-mgame.conf` / `thermal-hp-normal.conf` | Performance mode profile | Low | vendor |
| 5 | Keep `secure.double_tap_to_sleep=1` as the default (product `settings` default or setup script) | Double-tap to lock | Low | product (or settings) |
| 6 | Auto-brightness: reset `screen_auto_brightness_adj` to 0 (restored from the old phone) | Brightness swings | None | settings only |
| 7 | Restore `com.google.android.feature.PREMIER_TIER.xml` | Google feature parity | Low | vendor |
| 8 | PowerInsight per-policy power_profile keys (RRO) or ignore | Log spam, battery stats | Low | product |
| 9 | Pin the rule: no Global apps with Rust runtime above 3.1 | Prevents Gallery-type crashes | None | process |
| 10 | Keep the porter's Adreno driver and firmware | Graphics stability on Android 17 | - | none |
| 11 | ODM is V816.0.5.0 CN while vendor is 0.9 MIXM: check odm contents against official odm (only `munchg` build.prop edited) | Possible mixed calibration | Low | odm |
| 12 | Uniperf / perf2 AIDL: no backport; leave | Minor boost hints lost | - | none |
| 13 | Joyose / MiSight denials: same as official; leave | None | - | none |
| 14 | Double-tap to wake: ROM path verified; panel touch IC limitation | DT2W | - | hardware |
| 15 | VoLTE on Banglalink: no 470-xx entries in official carrier overlay; add only if the user confirms it worked on official | Calls quality | Low | product overlay |

Items 1–4 and 7 can all go into **one vendor rebuild** (method: `erofs_tar_rebuild` + `mkfs.erofs -U e0addc37-…`), flashed together with `product`, no wipe. The previous vendor image is kept for rollback.
