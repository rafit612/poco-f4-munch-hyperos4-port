# POCO F4 (munch) port: log and performance audit

The audit was read-only, run on 2026-10-23 between 20:50 and 21:00, about 1.6 h after the last vendor flash.

Evidence lives in `/tmp/claude-1000/-home-odoo-dbsl-poco-f4-5g-8gb-256gb-munch/155acf9c-1946-41a4-8e72-96ea9676041c/scratchpad/pa/`:
- `boot_buffer.log` is the log buffer.
- `live.log` is the live capture from 20:50:30 onward.
- The dumpsys snapshots are `meminfo`, `procstats`, `cpuinfo`, `top1-4`, `thermal`, `gfx_*`, `sf`, `dexopt`, `diskstats` and `dropbox`.

## Scorecard

| Area | State | Notes |
|---|---|---|
| CPU | **Bad** | The broken fingerprint loop costs about 1 core continuously: hwservicemanager 51 %, system_server 22–43 %, logd 24 % and fps HAL 9 %. |
| Memory | OK | 7.6 GB total, 1.7 GB available, 3.5 GB free incl. cache. ZRAM holds 2.1 GB at 0.8 GB physical, with 8 GB swap configured. No lmkd kills. |
| Multitasking | OK | 90 cached processes; CUR_MAX_CACHED_PROCESSES is 1000. The 51 `umms1_app_launch` kills are all cached/service processes at adj 700–985, not user apps. |
| GPU / jank | OK–fair | SystemUI shows 4.1 % janky frames (17.5 % legacy), p90 27 ms and p99 150 ms. |
| Display | **Locked at 60 Hz** | `peak_refresh_rate=60`, `user_refresh_rate=60` and `miui_refresh_rate=60` give a MIUI vote with max 60. The panel supports 60/90/120. |
| Thermal | OK | Thermal status 0, all cooling devices at 0, battery 32.9 °C while charging. The thermal HAL and mi_thermald are running. |
| Battery | n/a | The phone has been charging the whole time. The fingerprint loop will drain it once it's on battery. |
| Storage | OK | /data is 37 GB used of 225 GB (17 %). FBE is on. |
| App compilation | Fair | 331 apps are only at `verify` (JIT) and 65 at `speed-profile`. Background dexopt hasn't run yet after the many updates. |

## Top issues (ranked)

1. **Fingerprint HAL retry storm (broken sensor).**
   - The fps_hal tombstone shows a SIGSEGV at fault address 0xc0.
   - After that, system_server loops on "Failed to setActiveGroup: HIDL daemon is null" and "Unable to set HIDL callback", with 2 "AidlIsGetHalId false" per iteration.
   - That's about 212 iterations/s: 40,867 iterations, about 163k lines, in 3.2 min.
   - 99 % of all log lines come from pid 2845. Since the flash, hwservicemanager has used 49 min of CPU and logd 10 min.
   - Fix: re-hide `android.hardware.fingerprint` (vendor `etc/permissions/android.hardware.fingerprint.xml`, the hidden variant is parked) until the new sensor is fitted. Alternatively, disable `vendor.fps_hal` via its rc. Low risk; vendor rebuild needed. The user chose "keep on", but this is the #1 heat and battery cost.
2. **Refresh rate pinned to 60 Hz.**
   - Fix: Settings → Display → Refresh rate 120 Hz, or `settings put secure user_refresh_rate 120` / `miui_refresh_rate 120` and `system peak_refresh_rate 120`. Settings only, no risk.
3. **Gallery 4.3.1.6 first-run media scan.**
   - pid 22212 runs at 93–125 % CPU, and its PSS grew from 81 MB to 313 MB in about 8 min.
   - This is AI/face indexing after the reinstall. It should be transient; recheck that it settles.
   - The earlier ANR and "Long monitor contention" were in the same app.
4. **ConfigUpdater crash on every boot.**
   - Error: `IllegalArgumentException: column local_filename is not allowed in queries` from DownloadManager.query, raised in the ConversationActions/LangId receivers. Each boot logs 2 system_app_crash.
   - Cause: our DownloadProvider (Global DownloadProviderUi plus the platform provider) rejects that legacy column for this caller.
   - Fix options: compare the provider with Global17's `com.android.providers.downloads`, or disable `com.google.android.configupdater` (low value). Low risk.
5. **QTI GNSS AIDL retry.**
   - system_server and servicemanager keep trying `ctl.interface_start aidl/vendor.qti.gnss.ILocAidlGnss/default`: 192 failures in 3 min (PROP_ERROR_HANDLE_CONTROL_MESSAGE).
   - The munch vendor only has the HIDL QTI loc service. GNSS itself still works (model qcom).
   - Fix: remove or neutralise the vendor.qti.gnss AIDL client in system_ext (LocationService/izat jar), or add a vintf "not present" hint. Medium risk; low priority.
6. **WRITE_SECURE_SETTINGS denial loop.**
   - Still about 75/min: 236 in 3.2 min, `insertGlobalSetting` from an unprivileged caller. It peaked at 13k/min during the restore.
   - The caller is unknown; it needs root or binder tracing. Low impact now.
7. **Google Photos native crash.**
   - Four crashes, in system `libhwui` crabbyavif `Decoder::next_image` (SEGV in memcpy) while decoding an AVIF thumbnail.
   - This is an Android 17 platform codec bug with a specific file. Workaround: update Photos or delete the offending AVIF. Can't be fixed in the ROM without changing the system libhwui.
8. **Camera history (already addressed by the flashes).**
   - MGC 9.8 Aion aborts, six of them.
   - MiuiCamera 6.7 portrait DNN aborts (libanc_dc_base / libwa_depth shape errors), three of them.
   - Neither has recurred since the official camera 5.1 and the vendor restore.
9. **AM WTF "Unexpected non-cached process may get frozen soon".**
   - For securitycenter, securitycore and settings: about 7 each per 3 min, each with a full stack.
   - HyperOS 4 freezer noise; harmless, but log and CPU churn.
10. **OEM HAL interface gaps (expected, HyperOS 1 vendor).**
    - unfairmem_jni can't write `/proc/mi_mem_engine/scene_tid`; the kernel lacks it.
    - JNI_GREEZE can't create its socket.
    - `vendor.xiaomi.hw.touchfeature` AIDL is not found (apps fall back or fail; system_server uses HIDL @1.0 OK).
    - Uniperf service is missing; PowerInsight logs "NO processorPower".
    - None of these crash; they cost features (smart memory scenes, some game-turbo hints).
11. **Codec2 noise.**
    - `QC2Interface: Failed to query parameters` 782 times and `HeifDecoderImpl getSize not supported` 286 times, while thumbnailing.
    - This is the HyperOS 1 vendor codec on Android 17 media; harmless warnings.
12. **SELinux denials.**
    - system_server is denied reading vendor_sysfs_devfreq and kgsl gpuclk (GPU/DDR stats: 943+ reads).
    - Apps are denied reading vendor display/frc/default props.
    - These only affect stats and debug features; no functional break was observed.
13. **Outlook ANR.** TokenSharingService waited 200 s at 17:22, during the restore. One-off.
14. **dex2oat state.**
    - Most apps are verify-only, so the first launch of each app is slower and the phone runs warmer until bg-dexopt runs: idle and charging, `pm.dexopt.bg-dexopt=speed-profile`.
    - Optional: `adb shell pm compile -a -m speed-profile` or `cmd package bg-dexopt-job` once. That raises CPU and heat for 10–20 min.
15. **`init` child SIGABRT at every boot.** Three `init` forks per boot abort with SI_QUEUE ("crash_dump helper failed"). Pre-existing, boot completes; it needs dmesg (root) to identify.

## Memory / multitasking detail
- Top PSS: system_server 447 MB, Messenger 263 MB, SystemUI 242 MB, GMS 198 MB, Edge 183 MB, Home 146 MB, Google app 138 MB.
- Between snapshots 8 min apart, no leak trend except Gallery (indexing). system_server went +5.7 MB and GMS +10 MB.
- LMK: `ro.lmk.use_minfree_levels=true`, `kill_heaviest_task`, `ro.sys.fw.bg_apps_limit=40`. MIUI MMS compaction and swap are enabled. Zero lmkd kills in the window, so multitasking is healthy.

## Recommended fix order
1. Hide fingerprint until repair (vendor xml), or accept the cost knowingly.
2. Set refresh to 120 Hz (settings).
3. Let Gallery finish indexing and run bg-dexopt once while charging.
4. Optional ROM changes: the ConfigUpdater / DownloadProvider mismatch, and the vendor.qti.gnss AIDL client retries.
