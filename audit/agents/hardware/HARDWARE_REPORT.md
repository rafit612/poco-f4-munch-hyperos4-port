# POCO F4 5G (munch) - Hardware Inventory and Health Report

- Device: Xiaomi POCO F4 5G, model 22021211RG, board `munch`, SKU `munchg`, hwversion F.19.0, hwlevel MP, region GLOBAL
- SoC: Qualcomm SM8250 family ("kona"), Snapdragon 870 bin (soc_id 356, revision 2.1, foundry 1)
- OS: HyperOS OS4.0.0.24.XPKCNXM (beta, CN build, `ro.mi.os.version.beta=true`), Android 17 (SDK 37), build CP2A.260605.016; `ro.product.mod_device=annibale` (port donor)
- Vendor: POCO munch_global Android 13 V816.0.9.0.ULMMIXM, vendor patch 2025-04-01, VNDK 30, board/vendor API level 30, first API 31
- Kernel: `4.19.325-zyndong-perf-g7e817c4ca270 #1 SMP PREEMPT` (built 2026-09-10), clang, HZ=250
- SELinux: Enforcing. Root: a KernelSU-family framework is active (overlay mount source `KSU`, `/data/adb/modules/meta-overlayfs`)
- Audit date: 2026-10-23, uptime about 31 min at sampling, screen off/doze for most dumps, charger + USB connected, battery 100%
- Method: read-only adb (getprop, /proc, /sys, dumpsys, lshal, service list, pm list features). No root. Privacy-sensitive identifiers (IMEI, serial, MACs, SSIDs, phone numbers, account names, coordinates, cell IDs) were not recorded.

Legend: **[V]** verified on device - **[I]** inference (spec knowledge or indirect evidence) - **[R]** needs root to read

---

## 0. Executive summary - problems and anomalies (ranked)

| # | Severity | Finding | Evidence |
|---|---|---|---|
| 1 | High (battery/perf) | **hwservicemanager uses about 55% of a core continuously, system_server about 35%, fingerprint HAL about 10%.** Most likely a polling/retry loop around the dead Goodix fingerprint sensor (flex cut) [I]. This drains battery and keeps the little cluster at 1.8 GHz. | `dumpsys cpuinfo`: `55% 716/hwservicemanager`, `35% 2900/system_server`, `9.5% 2115/android.hardware.biometrics.fingerprint@2.1-service`; `top` agrees |
| 2 | High (function) | Fingerprint: HAL process is up (HAL deaths 0) but the sensor is not detected (`persist.vendor.sys.fp.vendor=none`). The BiometricScheduler is stuck on `FingerprintUpdateActiveUserClient` (State 2) with 2 operations queued behind it. One stale template is still enrolled. | `dumpsys fingerprint`, `dumpsys biometric`, getprop |
| 3 | Medium | Display is forced to 60 Hz even though the panel exposes 60/90/120 modes: `persist.vendor.dfps.level=60`, `ro.vendor.display.default_fps=60`, `defaultPeakRefreshRate: 60`, SF render range 0-60 Hz. SF reports `HWC missed frame count: 3087`. | `dumpsys SurfaceFlinger`, `dumpsys display`, getprop |
| 4 | Medium | Thermal HAL 2.0 returns **no current temperatures** and no SKIN sensor. Thermal headroom is NaN, and ADPF says `Hint Session Support: false`, `CPU/GPU Headroom Supported: false`. Android thermal and performance APIs give apps no data. Xiaomi's `mi_thermald` does the actual throttling. | `dumpsys thermalservice`, `dumpsys performance_hint`, `dumpsys hardware_properties` (Skin temperatures: []) |
| 5 | Medium | GNSS raw measurements are unavailable. The capabilities list has no MEASUREMENTS, NAV_MESSAGES, CORRECTIONS or ANTENNA_INFO, and `Measurements Provider: service: unregistered`. Apps like GnssLogger and precision/dual-frequency tools cannot get raw data. | `dumpsys location` |
| 6 | Medium | Two init services are crash-looping in `[restarting]`: `traced` (Perfetto tracing daemon) and `vendor_security`. | `getprop init.svc.*` |
| 7 | Medium | Feature-flag mismatches: `android.software.virtualization_framework` is declared, but the kernel has `# CONFIG_VIRTUALIZATION is not set` (no KVM/pKVM, so AVF/Microdroid cannot run). `config_wifi6ghzSupport=true` and `Ieee80211beEnabled=true`, but QCA6390 has no 6 GHz and no Wi-Fi 7 [I]. The Wi-Fi driver reports `WIFI_FEATURE_AWARE`, but `android.hardware.wifi.aware` is not declared. | `pm list features`, `/proc/config.gz`, `dumpsys wifi` |
| 8 | Low-Med | Bluetooth LE Audio is not usable. Controller ISO buffers are `iso_data_packet_length: 0`, `total_num_iso_data_packets: 0`, and the unicast `LE_AUDIO` profile is not in Enabled Profile Services, even though props enable BAP. Only the broadcast assistant and HAP client are running. | `dumpsys bluetooth_manager` |
| 9 | Low-Med | Camera2 limits for third-party apps: every AE target FPS range tops out at 30 fps, no 60 fps stream config at any size, the main sensor is exposed only at 16 MP binned (4624x3472, no max-resolution / 64 MP keys), and no 10-bit dynamic-range profiles. 4K60 and 1080p60 exist only inside the Xiaomi camera app through vendor tags [I]. | `dumpsys media.camera` |
| 10 | Low | Security/attestation stack is legacy: Keymaster 4.0 (feature `hardware_keystore=41`), no KeyMint, no StrongBox, no RKP `IRemotelyProvisionedComponent`. Boot props are inconsistent: `ro.boot.verifiedbootstate=orange` (unlocked) alongside `flash.locked=1` and `vbmeta.device_state=locked`, which suggests prop spoofing [I]. | getprop, `pm list features`, lshal |
| 11 | Low | Encryption state disagrees with the stated baseline ("encryption off"): `ro.crypto.state=encrypted`, `filenames_mode=aes-256-cts`. The `/data` mount options show no `inlinecrypt`. Actual FBE status needs root to confirm [R]. | getprop, `mount` |
| 12 | Low | `/proc/config.gz` header says `4.19.113` while the running kernel is `4.19.325`, so the embedded config may be stale. It also lacks any KSU symbol although KSU is active. Treat config-derived items as indicative. | `zcat /proc/config.gz`, `uname -a` |
| 13 | Low | Haptics HAL exposes only effect IDs and amplitude control. It has no composition primitives, PWLE/envelope or frequency profile, so Android 12-17 rich haptics (`VibrationEffect.Composition`, Android 16+ envelope effects) are unsupported [V], although the awinic LRA could do more [I]. | `dumpsys vibrator_manager` |
| 14 | Info | Little-cluster scaling_min is 691.2 MHz (300-614 MHz steps never used), so idle floors are raised. The big and prime cores idle at their minimum. | cpufreq sysfs, `time_in_state` |
| 15 | Info | `Lost RAM: 826,555K` in meminfo, probably kgsl/ion/carveouts [I]. | `dumpsys meminfo` |
| 16 | Info | No Android Spatializer effect (`mHasSpatializerEffect:false`), so Android head-tracked spatial audio is unavailable. Dolby Atmos (DAP offload) and MiSound are present instead. | `dumpsys audio`, `dumpsys media.audio_flinger` |
| 17 | Info | Battery learned capacity 4400 mAh against a 4500 mAh design (about 98%) [V, Android estimate]. Charge counter is exactly 4,400,000 uAh, which may be a HAL-clamped value [I]. Cycle count needs root [R]. | `dumpsys battery`, `dumpsys batterystats` |

---

## 1. SoC / CPU

| Item | Value | Evidence |
|---|---|---|
| SoC | Qualcomm SM8250 "kona", SD870 speed bin (prime 3.187 GHz), soc_id 356 rev 2.1 | `/sys/devices/soc0/*`, `/proc/cpuinfo` `Hardware: Qualcomm Technologies, Inc SM8250` [V] |
| Cores | 4x Kryo 585 Silver (part 0x805, Cortex-A55-derived) + 4x Kryo 585 Gold/Prime (part 0xd0d, Cortex-A77) | `/proc/cpuinfo` CPU part counts 4x0x805, 4x0xd0d [V] |
| Online | 0-7 all online | `/sys/devices/system/cpu/online` [V] |
| CPU features | fp asimd evtstrm aes pmull sha1 sha2 crc32 atomics fphp asimdhp cpuid asimdrdm lrcpc dcpop asimddp (ARMv8.2; no SVE, no BF16/I8MM, no MTE, no PAC) | `/proc/cpuinfo` [V] |
| Caches | L1D/L1I/L2/L3 indexes exist but size files are absent. Spec: 32/64 KB L1 per core, 128 KB L2 (silver), 256 KB L2 (gold), 512 KB L2 (prime), 4 MB L3 | `/sys/.../cache/index*/size` missing [V/I] |

### Frequency policies (governor schedutil on all three)

| Policy | CPUs | HW min-max | scaling min/max | Current (sample) | Steps |
|---|---|---|---|---|---|
| policy0 | 0-3 | 300 MHz - 1.8048 GHz | **691.2 MHz** / 1.8048 GHz | 1.8048 GHz (all 4, under load) | 300, 403.2, 518.4, 614.4, 691.2, 787.2, 883.2, 979.2, 1075.2, 1171.2, 1248, 1344, 1420.8, 1516.8, 1612.8, 1708.8, 1804.8 MHz (17) |
| policy4 | 4-6 | 710.4 MHz - 2.4192 GHz | 710.4 / 2419.2 MHz | 710-2419 MHz | 710.4 ... 2419.2 MHz (18 steps) |
| policy7 | 7 | 844.8 MHz - 3.1872 GHz | 844.8 / 3187.2 MHz | 844.8 MHz | 844.8 ... 2841.6, 3187.2 MHz (21 steps) |

schedutil tunables (each policy): `up_rate_limit_us=500`, `down_rate_limit_us=20000`, `hispeed_load=90`, `hispeed_freq` = 1248000 / 1574400 / 1632000 kHz, `pl=1` (WALT predictive load), `rtg_boost_freq` = 1000000 (policy0) / 0. Available governors: userspace, powersave, performance, schedutil. `CONFIG_CPU_FREQ_DEFAULT_GOV_PERFORMANCE=y`; userspace switches to schedutil at boot.

`time_in_state` for policy0 shows heavy residence at 1804.8 MHz (49,558 ticks) and 691.2 MHz (48,877 ticks), with zero time at 300-614 MHz. That matches the raised floor and the background CPU load (finding #1). Prime core: mostly 844.8 MHz (175,502), 3187.2 MHz for 14,447 ticks, so boost works.

Idle states (cpuidle, all cores): `C0` (WFI, latency 43 us), `C1` (power collapse, latency 531 us), both enabled. Deeper cluster/LLCC states are not exposed per-CPU [V].

Thermal throttling: cooling devices `thermal-cpufreq-0/4/7`, `cpufreq-hw-7`, `cpu-isolate0..7` all `cur_state 0` = **no throttling** [V]. CPU temperatures 36-40 C.

Load snapshot: loadavg 2.75/1.83/1.84, 886 tasks, top consumers hwservicemanager 55%, system_server 34%, fingerprint HAL 10%, logd 7-9%.

### Kernel config highlights (`/proc/config.gz`, header says 4.19.113, see finding #12)

| Area | Setting |
|---|---|
| Scheduler | `CONFIG_SCHED_WALT=y`, `CONFIG_SCHED_TUNE=y`, `CONFIG_SCHED_MC=y`, `CONFIG_ENERGY_MODEL=y`, `CONFIG_MIGT_ENERGY_MODEL=y` (Xiaomi), **`# CONFIG_UCLAMP_TASK is not set`**, `CONFIG_PREEMPT=y`, HZ=250 |
| cpufreq | schedutil, performance, powersave, userspace, ondemand, conservative built |
| PSI | `CONFIG_PSI=y` (`/proc/pressure/io` readable; memory/cpu pressure needs root) |
| Memory | `CONFIG_ZRAM=y`, `CONFIG_ZRAM_WRITEBACK=y`, `CONFIG_ZSMALLOC=y`, `CONFIG_CRYPTO_LZO=y`, **no `CRYPTO_LZ4`/`LZ4HC`/`ZSTD`**, no ZRAM_DEDUP, no LRU_GEN (MGLRU), **no USERFAULTFD**, MEMCG + MEMCG_SWAP |
| Pages / VA | `CONFIG_ARM64_4K_PAGES=y`, 39-bit VA, no 16K pages |
| Virtualization | `# CONFIG_VIRTUALIZATION is not set` (no KVM) |
| I/O | MQ deadline, kyber (+ legacy noop/deadline/cfq); no BFQ; no io_uring |
| FS / crypto | ext4, f2fs, overlayfs, incremental-fs, FS_ENCRYPTION + INLINE_CRYPT, BLK_INLINE_ENCRYPTION, DM_DEFAULT_KEY, DM_VERITY (+FEC); no NTFS/exFAT in config |
| BPF | BPF_SYSCALL, BPF_JIT (ALWAYS_ON), CGROUP_BPF |
| Hardening | STACKPROTECTOR_STRONG, HARDENED_USERCOPY, PAN; no ShadowCallStack, no CFI, no LTO (`CONFIG_LTO_NONE=y`), no KPROBES |
| Root | No `CONFIG_KSU*` symbol, yet a KSU overlay is mounted (LKM-style or config not matching) [I] |
| TCP | cubic default (no BBR) |

---

## 2. GPU

| Item | Value | Evidence |
|---|---|---|
| Model | Adreno 650 v3 (`gpu_model=Adreno650v3`) | `/sys/class/kgsl/kgsl-3d0/gpu_model` [V] |
| Max clock | 670 MHz (`max_gpuclk=670000000`) | kgsl [V] |
| Power levels | 7 levels (devfreq cooling `thermal-devfreq-0` max_state 6). Typical kona v3 table is 670/587/525/490/441/400/305 MHz [I]. Frequency table, governor (msm-adreno-tz expected), current clock, busy % [R] | cooling_device, kgsl files permission denied |
| gpubusy | `37395 / 1014691` (about 3.7% busy, screen off) | `/sys/class/kgsl/kgsl-3d0/gpubusy` [V] |
| GLES | OpenGL ES 3.2, driver **V@0805.0** (GIT@d4f1d5539c, Iad64dfeba7, build date 11/07/24) | `dumpsys SurfaceFlinger` `GLES:` line [V]; `glesVersion=196610` (0x30002) |
| Vulkan | API **1.3.0** (`vulkanVersion=4206592` = 0x403000), feature `vulkan.level=1`, `vulkan.compute`, dEQP level 132383489 (2022-03-01) | `dumpsys gpu`, `pm list features` [V] |
| Updatable driver | Pre-release Game Driver package `com.qualcomm.qti.gpudrivers.kona.api30`; Stable Game Driver unsupported | `dumpsys gpu` [V] |
| ANGLE | not in use (angleLoadingCount 0) | `dumpsys gpu` |
| RenderEngine | Skia GL, protected context supported, blur algorithm KawaseDualFilterV2 | SF dump |
| Thermal | GPU0/GPU1 throttle at 95 C, shutdown at 115 C; current 34.9/36.2 C; no throttling | `dumpsys hardware_properties`, thermalservice |
| Extras | `opengles.aep` feature present; no `opengles.deqp.level` feature | `pm list features` |

---

## 3. Memory

| Item | Value | Evidence |
|---|---|---|
| Physical | MemTotal 7,776,688 kB (7.42 GiB visible out of 8 GB LPDDR5; spec LPDDR5-2750 [I]) | `/proc/meminfo` [V] |
| Available | MemAvailable 2.79 GB at sample; dumpsys: Free 5.26 GB (cached), Used 3.80 GB, **Lost 826 MB** | `/proc/meminfo`, `dumpsys meminfo` [V] |
| Swap | zram 8,388,604 kB (8 GiB); 1.11 GB swapped, 430.8 MB physical (about 2.6:1 ratio) | `/proc/meminfo`, `dumpsys meminfo` [V] |
| zram algorithm | [R] (`/sys/block/zram0/comp_algorithm` denied). The kernel config only builds LZO, so it is **lzo or lzo-rle** [I] | config.gz |
| swappiness | [R]; framework props `sys.mem.swappiness_on_launcher=100`, `sys.mem.swappiness_on_start=100` | getprop |
| LMK | userspace lmkd running; `ro.lmk.use_minfree_levels=true`, `kill_heaviest_task=true`, `kill_timeout_ms=15`, `ro.config.low_ram=false`; Xiaomi `persist.sys.mms.write_lmkd=true`, `mi_reclaim` kernel interface present | getprop, `/sys/kernel/mi_reclaim` [V] |
| Memory type | LPDDR5 (spec) [I]; DDR info not exposed [R] | - |
| Pressure | `/proc/pressure/io`: some avg300=0.04, full 0 (no I/O pressure) | [V] |

---

## 4. Storage

| Item | Value | Evidence |
|---|---|---|
| Interface | UFS host `1d84000.ufshc` (Qualcomm), LUNs sda-sdf | `ro.boot.bootdevice`, `/sys/devices/platform/soc/1d84000.ufshc` [V] |
| Device vendor/model/version | [R]. All `string_descriptors/*`, `device_descriptor/*` and SCSI vendor/model are permission denied. POCO F4 ships UFS 3.1 [I] | - |
| Health (life_time_estimation_a/b, eol_info) | **[R]** (permission denied) | `health_descriptor/*` |
| Capacity | /data 225 GiB usable (235,722,732 K total), 31 GB used, 194 GB free (86% free) | `df -h`, `dumpsys diskstats` [V] |
| Write latency | 1 ms (512 B data write) | `dumpsys diskstats` [V] |
| /data | **f2fs** on sda34: `rw,lazytime,noatime,background_gc=on,discard,inline_xattr,inline_data,inline_dentry,flush_merge,barrier,extent_cache,mode=adaptive,active_logs=6,alloc_mode=default,checkpoint_merge,fsync_mode=nobarrier,discard_unit=block,memory=normal` (no `inlinecrypt`, no compression) | `mount` [V] |
| /metadata | ext4 on sda18 | `mount` |
| System partitions | `/` ext4 (dm-3), `/system_ext` ext4, `/product` ext4, `/odm` ext4, **`/vendor` erofs** (1.0 G, 100% full, ro), `/system` overlay from KSU meta-overlayfs | `mount`, `df` |
| Special | `/data` file bind-mounted over `/vendor/etc/camera/camxoverridesettings.txt` (camera override from port/module) | `df` output [V] |
| Encryption | `ro.crypto.state=encrypted`, `ro.crypto.volume.filenames_mode=aes-256-cts`. This conflicts with the stated baseline "encryption off"; needs root to confirm [R] | getprop |
| I/O scheduler | [R] (`/sys/block/sda/queue/scheduler` denied); kernel builds mq-deadline + kyber | config.gz |
| Last idle maintenance (fstrim) | 2026-10-07 11:31:17 | `dumpsys mount` |
| A/B | Virtual A/B enabled, slot `_a` | getprop |

---

## 5. Display and touch

| Item | Value | Evidence |
|---|---|---|
| Panel | L11R AMOLED (`ro.vendor.mi_sf.project_l11r=true`, `ro.vendor.display.type=oled`), replacement clone panel per owner; DSI-1 on `card0`, HWC display 0 port 129. EDID-style info is a placeholder (`pnpId=QCM`, productId 1, week 27/2006), so there is no panel vendor string. `panel_info` [R] | SF, `dumpsys display`, `/sys/class/drm` [V] |
| Resolution / density | 1080x2400, 394.7x394.3 dpi physical, `ro.sf.lcd_density=440` (2.75x), cutout 56x94 px punch hole at top centre, rounded corners r=70 | `dumpsys display` [V] |
| Refresh modes | 60 / 90 / 120 Hz (ids 0/2/1 in SF). **Active 60 Hz**; policy render range 0-60 Hz; `defaultPeakRefreshRate: 60`; `persist.vendor.dfps.level=60`; `ro.vendor.display.default_fps=60`; `ro.vendor.dfps.enable=false`; no ARR/VRR (`hasArrSupport false`, `vrrConfig=N/A`) | SF, `dumpsys display`, getprop [V] |
| HDR | HDR10 (2), HLG (3), HDR10+ (4); **no Dolby Vision (1)**. HWC luminance max 420 nits, max-average 210 nits, min 0.323 nits. HDR/SDR ratio up to 2.25 | `hdrCapabilities` [V] |
| Brightness | float range 0.000977-1.0; backlight-to-nits map 2 / 500 / 900 nits (HBM above 0.4998, minLux 6001); auto-brightness curve up to 1000 nits; panel0-backlight max level 2047 (cooling device max_state), clone 4095; default 0.0747 | `dumpsys display`, cooling devices [V] |
| Color | modes NATIVE, SRGB, DISPLAY_P3; current SRGB; wide colour supported; `persist.sys.sf.native_mode=258` (Xiaomi), saturation 1.0 | SF [V] |
| Composition stats | `HWC missed frame count: 3087` (since boot) | SF [V] |
| Touch | FocalTech `fts_ts` (bus 0x1c), plus `xiaomi-touch` virtual device. Coordinate space 10799x23999 (10x oversampled). `touchfeature-hal-1-0` running, `ro.vendor.touchfeature.type=59`, touchboost enabled. **Touch sample rate not exposed** [R] (spec 360 Hz [I]) | `dumpsys input` [V] |
| Display HALs | composer 2.1-2.4 + vendor.qti composer 3.0 (HIDL), display.color 1.0-1.5, postproc, Xiaomi displayfeature | lshal [V] |

---

## 6. Cameras

Provider: HIDL `android.hardware.camera.provider@2.4` (legacy/0), devices `device@3.5`. 7 camera IDs, 5 visible to API1. Camera service `persist.vendor.camera.provider.pid=14620`, a high PID that may mean the provider restarted after boot [I]. Installed modules (`persist.vendor.camera.mi.module.info*`): **back_main = OV64B40 (Sunny), back_ultra = OV8856 (AAC), back_macro = GC02M1 (Sunny), front_main = IMX596 (OFILM)**. The vendor also carries unused IMX582 (alt main), IMX563, S5K5E8 and CMB433 drivers. OIS calibration state 2, `oisAlgoParam=12500,12687,15,15`.

| ID | Role [I from params] | Facing | Hardware level | Pixel array (Camera2) | Sensor size (mm) | f/ | Focal (mm) | OIS | AF modes | Flash | Min focus |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | Main OV64B40 (64 MP, 4-in-1 binned to 16 MP) | Back, 90 deg | LEVEL_3 | 4624x3472 | 6.49x4.87 (1/2.0") | 1.79 | 4.71 | **Yes** (modes 0,1) | OFF, AUTO, MACRO, CONT_VIDEO, CONT_PICTURE | Yes | 10 diopters (10 cm) |
| 1 | Front IMX596 (20 MP, binned 5 MP) | Front, 270 deg | LEVEL_3 | 2592x1952 | 4.15x3.12 | 2.45 | 2.84 | No | Fixed focus | No | fixed |
| 2 | Ultra-wide OV8856 (8 MP) | Back | LEVEL_3 | 3264x2448 | 3.66x2.74 | 2.2 | 1.65 | No | Fixed | Yes | fixed |
| 3 | Macro GC02M1 (2 MP) | Back | LEVEL_3 | 1600x1200 | 2.80x2.10 | 2.4 | 1.94 | No | Fixed | Yes | fixed |
| 4 | Logical multi-camera (physical 0 + 2) | Back | LEVEL_3 | 4624x3472 | = main | 1.79 | 4.71 | Yes | full | Yes | 10 |
| 5 | Main-sensor alias (exposure range differs from ID 0; Xiaomi auxiliary) | Back | LEVEL_3 | 4624x3472 | = main | 1.79 | 4.71 | Yes | full | Yes | 10 |
| 6 | Front alias | Front | LEVEL_3 | 2592x1952 | = front | 2.45 | 2.84 | No | fixed | No | fixed |

Capabilities (all IDs): BACKWARD_COMPATIBLE, RAW, YUV_REPROCESSING, PRIVATE_REPROCESSING, READ_SENSOR_SETTINGS, MANUAL_SENSOR, BURST_CAPTURE, MANUAL_POST_PROCESSING; plus CONSTRAINED_HIGH_SPEED_VIDEO on 0/1/4/5/6 and LOGICAL_MULTI_CAMERA on 4. RAW formats: RAW16 (32), RAW_OPAQUE (36), RAW10 (37) at full array. Digital zoom up to 10x on all. EIS on all (videoStabilizationModes 0,1).

ISO ranges: main 50-877 (exposure 73 us - 32.1 s), front 50-3200 (to 0.35 s), UW 50-853 (to 9.99 s), macro 50-600 (to 0.43 s). CFA: main/UW BGGR, front/macro RGGB.

Frame-rate limits through Camera2 (public API):
- `aeAvailableTargetFpsRanges` max **[30,30]** on every camera, and min frame duration gives 30 fps at 4624x3472, 3840x2160, 1920x1080 and 1280x720. **No public 60 fps.**
- Constrained high-speed: main 1920x1080 @120, 1280x720 @240, 720x480 @240, 640x480 @240; front 1280x720 @120, 720x480 @120. UW and macro have no high-speed modes.
- 4K: 3840x2160 output available (30 fps public). Xiaomi app 4K60 is through vendor tags only [I].
- No `availableDynamicRangeProfilesMap` (no 10-bit HLG/HDR10 capture), no `*MaximumResolution` keys (64 MP not exposed), no Ultra HDR/JPEG_R output.
- Vendor tags: 80-93 per camera.

Other: `camera.disable_zsl_mode=true`. Aux-camera allowlist includes `org.codeaurora.snapcam`, Xiaomi factory apps. HEIC hardware encoder present (`c2.qti.heic.encoder`).

---

## 7. Sensors (Sensors HAL 1.0 HIDL, Qualcomm SEE/SSC on SLPI)

57 hardware sensors plus 8 AOSP virtual = 65 in the list. The baseline said 71; `dumpsys sensorservice` here lists 57 h/w ("57 running"). Mode NORMAL, sensor privacy disabled.

| Handle | Name | Vendor | Type | Wake |
|---|---|---|---|---|
| 0x01 | Elliptic Proximity (ultrasonic, uses earpiece/mic, **no IR proximity**) | Elliptic Labs | proximity | - |
| 0x02/03 | step_detector | Xiaomi | step_detector | W / NW |
| 0x04/05 | pedometer | Qualcomm | step_counter | W / NW |
| 0x06/07 | stationary_detect | Qualcomm | stationary_detect | W / NW |
| 0x08 | sns_smd | Qualcomm | significant_motion | W |
| 0x09/0a | screen_down | Xiaomi | xiaomi.screen_down | W / NW |
| 0x0b | semtech_sx933x_0 | Semtech | xiaomi.sar_secondary | NW |
| 0x0c/0d | sar_detector_1 | Xiaomi | sar_algo_1 | W / NW |
| 0x0e | ccd_tilt | Qualcomm | tilt_detector | W |
| 0x0f | semtech_sx932x_0 | Semtech | xiaomi.sar | NW |
| 0x10 | Rotation Vector | Qualcomm | rotation_vector | NW |
| 0x11 | orientation | Xiaomi | orientation | NW |
| 0x12/13 | tcs3701 Ambient Light | ams AG | light | W / NW |
| 0x14/15 | pocket_mode | Xiaomi | oem_pocket | W / NW |
| 0x16/17 | NonUi | Xiaomi | nonui | W / NW |
| 0x18/19 | pickup | Xiaomi | pickup | W / NW |
| 0x1a/1b | oem13_light_smd | Xiaomi | oem13 | W / NW |
| 0x1c/1d | motion_detect | Qualcomm | motion_detect | W / NW |
| 0x1e | tcs3701 (factory ALS) | ams AG | ambientlight.factory | NW |
| 0x1f | ak0991x Magnetometer-Uncalibrated | AKM | mag_uncal | NW |
| 0x20/21 | ois_manager | Xiaomi | ois_sensor | W / NW |
| 0x22 | ak0991x Magnetometer | AKM | magnetic_field | NW |
| 0x23 | linear_acceleration | Qualcomm | linear_accel | - |
| 0x24/25 | har (human activity recognition) | Xiaomi | har | W / NW |
| 0x26 | gravity | Qualcomm | gravity | NW |
| 0x27 | sns_geomag_rv | Qualcomm | geomag_rotation_vector | NW |
| 0x28 | Game Rotation Vector | Qualcomm | game_rotation_vector | NW |
| 0x29 | lsm6dso Gyroscope | STMicro | gyroscope | NW |
| 0x2a/2b | Aod | Xiaomi | aod | W / NW |
| 0x2c/2d | device_orient | Xiaomi | device_orientation | W / NW |
| 0x2e | tcs3701 front CCT stream | ams AG | front_cct_strm | NW |
| 0x2f/30 | tcs3701 front CCT | ams AG | front_cct | W / NW |
| 0x31/32 | rohm_bu27030_back (rear light sensor) | Rohm | back_lux | W / NW |
| 0x33 | rohm_bu27030_back stream | Rohm | back_lux_strm | NW |
| 0x34/35 | sar_detector | Xiaomi | sar_algo | W / NW |
| 0x36 | lsm6dso Accelerometer-Uncalibrated | STMicro | accel_uncal | NW |
| 0x37 | lsm6dso Gyroscope-Uncalibrated | STMicro | gyro_uncal | NW |
| 0x38 | lsm6dso Accelerometer | STMicro | accelerometer | NW |
| 0x39 | Touch Sensor | Xiaomi | qti.sensor.touch | - |
| virtual | Corrected Gyro, Game RV, Gyro Bias (debug), GeoMag RV, Gravity, Linear Accel, Rotation Vector, Orientation | AOSP | fusion | - |

Absent hardware: barometer, hall sensor, heart-rate, hinge, ambient temperature/humidity, hifi-sensors feature.

Active at sampling (screen off): step_detector W+NW (200 ms), tcs3701 ALS NW (1 ms), pickup W (200 ms), **lsm6dso Gyroscope (200 ms)**, rohm back ALS (1 ms), lsm6dso Accelerometer (200 ms). The gyroscope stays active while the screen is off, a small battery cost [I].

---

## 8. Audio

| Item | Value | Evidence |
|---|---|---|
| HAL | audio@6.0 + effect@6.0 HIDL (QTI), audiohalext, Dolby DMS 2.0 | lshal [V] |
| Speakers | Earpiece + bottom speaker outputs (stereo pair through Cirrus cs35l41 smart amps, `/dev/msm_cirrus_playback`) [V device node; stereo per spec I] | `dumpsys media.audio_policy` |
| Microphones | 2 built-in endpoints: "Built-In Mic" (bottom) and "Built-In Back Mic" (back) | audio_policy [V] |
| Jack | No 3.5 mm. `kona-mtp-snd-card USB_3_5 Jack` is USB-C analog/digital adapter detection | `dumpsys input` |
| Mix ports | primary (24-bit packed), deep_buffer, mmap_no_irq (AAudio MMAP, policy 2), virtual_deep_buffer, hifi_playback (USB), compress_offload/passthrough, **direct_pcm up to 384 kHz / 32-bit (and 24-bit, 8_24)** | audio_policy [V] |
| Hi-Res | Yes over USB/wired: direct_pcm 44.1-384 kHz, PCM 24/32-bit; `ro.audio.hifi=true` | [V] |
| Effects | **Dolby Atmos (DAP_offload, Dolby Laboratories, tunneled/offloadable)**, **MiSound** (`com.miui.misound`); Dolby AC-3/E-AC-3/E-AC-3-JOC/AC-4 decoders; **ViPER4Android not present**; no Android Spatializer effect | audio_flinger, media_codecs [V] |
| Offload | `audio.offload.enable=true`, PCM 16/24-bit offload, video offload | getprop |
| Other inputs | Telephony Rx, Remote Submix, "FM Tuner". POCO F4 has no FM receiver [I], so this is the generic QTI policy entry | audio_policy |
| SoundTrigger | soundtrigger 2.0-2.3 HAL (hotword on ADSP) | lshal |

---

## 9. Connectivity

### Cellular
| Item | Value |
|---|---|
| Modem | Snapdragon X55 (SM8250 external MDM, `ro.boot.baseband=mdm`) [V/I] |
| Baseband | `2.5.1.c1-14.1-0324_0657_6488b87c` (both slots) [V] |
| RIL | Qualcomm RIL 1.0, radio HAL 1.0-1.5 + QTI radio 2.4, IMS radio 1.0-1.7 |
| SIM | DSDS (`persist.radio.multisim.config=dsds`). Slot 1 **ABSENT**, slot 2 **LOADED** |
| Network | Slot 2: LTE in service, EARFCN 100 = **Band 1 (2100 FDD)**, 10 MHz bandwidth, RSRP -99 dBm, RSRQ -12, SNR 13 dB, level 3/4, no CA, NR not active. Preferred network mode 22 on both slots (NR/LTE/GSM/WCDMA family) |
| Features | telephony gsm/cdma/ims/calling/data/messaging; `persist.dbg.volte_avail_ovr=1`; SAP |

### Wi-Fi
| Item | Value |
|---|---|
| Chip | Qualcomm QCA6390 (FastConnect 6800) through `cnss-daemon` [I name; V driver] |
| Driver / FW | WLAN driver **5.2.022.12B**, FW **1.0.1.0.1235.10** (`HW_VERSION=ffffffff`) |
| Wi-Fi HAL | wifi@1.0-1.4 HIDL, supplicant 1.0-1.3 + vendor 2.2 |
| Current link | 802.11ac, 5 GHz (5745 MHz, ch 149), RSSI -50 dBm, 866 Mbps TX/RX (2x2 VHT80); AP-limited (AP is not 11ax) |
| Standards | 11a/b/g/n/ac/ax (Wi-Fi 6, 2.4 + 5 GHz) [I spec]. `Ieee80211axEnabled=true`. `Ieee80211beEnabled=true` and `config_wifi6ghzSupport=true` are framework flags with no hardware behind them [I] |
| Features | INFRA, PASSPOINT, P2P, HOTSPOT, AWARE (driver), PNO, TDLS (+offchannel), AP_STA concurrency, LLStats, RSSI monitor, NDO, roaming control, TX power limit, WPA3-SAE, WPA3 Suite-B, SAE-H2E, OWE, DPP, low latency, MAC randomisation (STA/AP), MBO, OCE, WAPI, FILS-SHA256/384, multi-internet STA+STA |
| Chip combos | {STA+AP}, {STA+P2P/NAN}, {2xSTA}; DBS currently false |
| SoftAP | max 32 clients; 2.4 GHz ch 1-13; 5 GHz ch 149-165 only (BD regulatory); no 6 GHz SoftAP |
| Declared features | wifi, wifi.direct, wifi.passpoint. **No wifi.aware, no wifi.rtt** |

### Bluetooth
| Item | Value |
|---|---|
| Controller | QCA6390 BT, **LMP/HCI 5.2** (0x0b), subversion 0x4089 |
| HAL | bluetooth@1.0 HCI HIDL + bluetooth.audio@2.0 + QTI bluetooth_audio 2.0, BT SAR |
| A2DP codecs | SBC, AAC, aptX, aptX HD, **LDAC**, aptX Adaptive, Opus, LHDC V2/V3/V5 listed; A2DP offload enabled (`mA2dpOffloadEnabled: true`); aptX voice for HFP |
| Profiles enabled | GATT, A2DP src, AVRCP TG 1.6, HFP AG, HID host/device, MAP, OPP, PAN (NAP/PANU), PBAP, SAP, Hearing Aid (ASHA), HAP client, Battery, LE Audio broadcast assistant |
| LE features | extended scan supported, periodic advertiser list 3, max adv data 1650 B; **ISO: 0 packets / length 0, so no CIS/BIS, LE Audio unicast and Auracast source unsupported** |

### NFC
| Item | Value |
|---|---|
| Chip | NXP NQ-series over I2C (`/dev/nq-nci`, `vendor.nxp.hardware.nfc@2.0`, `ro.nfc.port=I2C`); exact model [R] (`nqnfcinfo` stopped) |
| State | NFC **on**, Secure NFC off, reader mode off |
| Features | nfc, nfc.any, HCE, HCE-F, UICC, **eSE** (`se.omapi.ese`, `se.omapi.uicc`, `com.nxp.mifare`); secure_element 1.0-1.2, eSE power manager |
| HCE services | Google Pay, Nearby |

### GNSS
| Item | Value |
|---|---|
| HAL | gnss@1.0-2.1 HIDL + vendor.qti gnss up to 4.0 (`loc_launcher`, `gnss_service` running); model name "qcom" |
| Capabilities | SCHEDULING, MSB, MSA, GEOFENCING, LOW_POWER_MODE, SATELLITE_BLOCKLIST, ACCUMULATED_DELTA_RANGE(unknown) |
| Missing | **MEASUREMENTS** (Measurements Provider unregistered), NAV_MESSAGES, MEASUREMENT_CORRECTIONS, ANTENNA_INFO |
| Constellations | Chip supports GPS L1+L5, GLONASS, BeiDou, Galileo E1+E5a, QZSS, NavIC (SD870 spec) [I]; not verifiable without a fix and measurements |

### IR blaster
`/dev/ir_spi`, AIDL `android.hardware.ir.IConsumerIr/default` registered, feature `android.hardware.consumerir` [V]. Carrier frequency list [R].

---

## 10. Power / battery / charging

| Item | Value | Evidence |
|---|---|---|
| Battery | Li-poly, design 4500 mAh [I spec]; Android learned capacity **4400 mAh** (min=max=last=4400) | `dumpsys batterystats` [V] |
| State | level 100%, status FULL (5), health GOOD (2), present, **4.431 V**, **31.4 C**; charge counter 4,400,000 uAh | `dumpsys battery` [V] |
| Cycle count | [R] (`/sys/class/power_supply/*` all denied; Health HAL is HIDL 2.1, so there is no AIDL battery-health/cycle API) | - |
| Charger | AC powered (plugType 1), reported max 1.35 A @ 5.0 V at the moment of sampling (battery full, taper) | `dumpsys battery` |
| Max capability | 67 W (11 V / 6 A) through dual TI **bq2597x** charge pumps (master + slave power_supply nodes present) on PM8150B [I spec; V nodes] | `/sys/class/power_supply` listing |
| Charging features | `persist.vendor.accelerate.charge=true`, `persist.vendor.night.charge=true` (smart overnight), `persist.vendor.battery.health=true`; Xiaomi MiCharge HAL 1.0 + `charge_logger` running | getprop, init.svc |
| PMIC | PM8150 (39.8 C), PM8150B (35.6 C), PM8150L (39.3 C); BCL levels 0 (no brownout events) | thermal zones |
| Power modes | Battery saver **off** (`low_power=0`, `mIsPowerSaveModeEnabled: false`); Xiaomi `persist.sys.power.default.powermode=enhance`, performance features enabled | `dumpsys power`, getprop |
| Power HAL | AIDL `android.hardware.power.IPower/default` registered, but its dump returns FAILED_TRANSACTION; QTI perf HAL 2.2 + Xiaomi MiPerf drive boosting; **ADPF hint sessions unsupported** | `dumpsys performance_hint` |

---

## 11. Thermal

Thermal HAL: `android.hardware.thermal@2.0` (connected) + vendor.qti limits 1.0; Xiaomi `mi_thermald` running; `ro.vendor.fps.switch.thermal=true` (refresh-rate thermal switch). Thermal status 0 (NONE). Cooling devices all at 0 (no active mitigation).

HAL static thresholds: CPU0-7 / GPU0-1 / NPU hot 95 C (SEVERE), shutdown 115 C; battery 80 / 90 C; ibat 4.5 / 5.0 A; vbat cold 3.2 / 3.0 V; soc cold 10 / 2. **Current temperatures from HAL: empty**; headroom thresholds all NaN; no SKIN type.

Thermal zones (milli-C, sample, screen off, charging at full):

| Group | Values |
|---|---|
| CPU silver | cpu-0-0..0-3: 38.7 / 40.3 / 38.7 / 39.1 |
| CPU gold/prime | cpu-1-0..1-7: 38.7, 38.4, 38.0, 36.8, 37.6, 38.4, 37.2, 37.2; cpuss-0/1 39.5 |
| GPU | gpuss-0 35.2, gpuss-1 37.0 |
| Other SoC | aoss0 36.4, aoss1 36.2, cwlan 35.8, video 36.6, ddr 36.2, q6-hvx 37.0, camera 35.8, cmpss 37.0, npu 36.6 |
| Modem | modem-0/1/streamer 27.0, mmw0-2 27.0 (mmW not fitted on this model; values are placeholders [I]), modem1_xo 42.0, PA/wifi/quiet -40 (sensor not populated) |
| Board | conn_therm 33.6, cpu_therm 37.0, quiet_therm 35.3, flash_therm 34.9, pa_therm0/1 36.3/35.9, wifi_therm 36.0, charger_therm0 36.9 |
| Battery | battery / bms 31.4 |
| PMIC | pm8150_tz 39.8, pm8150b_tz 35.6, pm8150l_tz 39.3; vbat 4434 mV; ibat -78 mA |

Cooling devices: thermal-cpufreq-0 (0/16), -4 (0/17), -7 (0/20), cpufreq-hw-7 (0/1), cpu-isolate0..7 (0/1), thermal-devfreq-0 = GPU (0/6), panel0-backlight (0/2047), brightness0-clone (0/4095), battery (0/16), cdsp (0/10), hvx (0/10), npu (0/5), modem_pa/pa_fr1/tj/current/bcl/charge_state/skin/mmw0-3/mmw_skin0-3 (0/3).

Health: thermally healthy; no throttling, no BCL events.

---

## 12. Haptics, IR, fingerprint, FM, USB, buttons

| Block | Identity / state | Evidence |
|---|---|---|
| Haptics | Awinic X-axis linear motor (spec) [I]; AIDL `IVibrator/default` + `IVibrator/vibratorfeature` (Xiaomi), `vibrator-bridge` + `vibratorfeature-hal-service` running. Capabilities ON_CALLBACK, PERFORM_CALLBACK, AMPLITUDE_CONTROL; about 180 predefined effect IDs (Xiaomi haptic library); **primitives [], no frequency profile, no envelope** | `dumpsys vibrator_manager` [V] |
| IR | ir_spi + IConsumerIr AIDL | [V] |
| Fingerprint | Side-mounted capacitive (power key), Goodix/FPC driver set (`ro.hardware.fp.vendor=fpc,goodix`, module ofilm). HIDL `biometrics.fingerprint@2.1` service up (pid 2115) but `persist.vendor.sys.fp.vendor=none` (sensor not detected, flex cable cut). Scheduler stuck, about 10% CPU. `uinput-goodix` input device still exists | `dumpsys fingerprint/biometric`, getprop, top [V] |
| Face | Only `miui.face.FaceService` (2D camera software face unlock); no biometrics.face HAL/feature | service list |
| FM radio | No FM hardware on POCO F4 [I]; the audio policy lists an FM Tuner port only from the generic QTI config | audio_policy |
| USB | Type-C, DWC3 controller `a600000.dwc3`, USB HAL 1.0-1.2 (HIDL; dumpsys `usb_hal_version=12`). Supported modes: dual-role + audio accessory; role combos source/host and sink/device (**OTG/host supported**, feature `usb.host`, `usb.accessory`). Current: UFP / sink / device, functions `adb`, configured. **Negotiated High-Speed 480 Mbit/s (USB 2.0)** per host `lsusb -t`; contaminant detection: not detected; no DisplayPort alt-mode | `dumpsys usb`, host sysfs [V] |
| Buttons | `gpio-keys` (volume up/down), `qpnp_pon` (power, PMIC), side power key doubles as fingerprint | `dumpsys input` [V] |
| LEDs | `/sys/class/leds` [R]; ILights AIDL registered (no notification LED on this model [I]) | service list |

---

## 13. HALs

### Registered HIDL (hwservicemanager) - hardware-relevant
atrace 1.0; audio 6.0 + effect 6.0; biometrics.fingerprint 2.1; bluetooth 1.0 + bluetooth.audio 2.0; boot 1.1; camera.provider 2.4; cas 1.2; drm 1.3 (Widevine/ClearKey); dumpstate 1.1; gatekeeper 1.0; gnss 2.1; graphics.allocator 3.0/4.0, composer 2.4; **health 2.1**; **keymaster 4.0**; media.c2 1.2, omx 1.0; memtrack 1.0; **neuralnetworks 1.3** (Hexagon NNAPI); nfc 1.2; radio 1.5 + config 1.1 + SAP; secure_element 1.2; **sensors 1.0**; soundtrigger 2.3; tetheroffload 1.0; **thermal 2.0**; usb 1.2; wifi 1.4 + supplicant 1.3. Vendor: QTI display color/config/postproc, Dolby DMS 2.0, NXP NQ NFC 2.0, QTI gnss 4.0, data, eSE PM, audiohalext, BT audio/SAR/btconfigstore, camera postproc, capabilityconfigstore, DSP service, IOP 2.0, limits 1.0, perf 2.2, qseecom, qteeconnector, radio (ims 1.7, qtiradio 2.4, uim, lpa), sensorscalibrate, servicetracker, soter, tui_comm, VPP 1.3, wifidisplay; Xiaomi antdtx, cit*, displayfeature, mfidoca, **micharge**, midevauth, mimd, mioob, miperf, misys 4.0, mlipay, mtdservice, otrpagent, tidaservice, **touchfeature**, vsimapp, sensor.communicate; rongcard eid.

### Registered AIDL (servicemanager) - hardware
`android.hardware.ir.IConsumerIr/default`, `android.hardware.light.ILights/default`, `android.hardware.power.IPower/default`, `android.hardware.vibrator.IVibrator/default` + `/vibratorfeature`, `android.hardware.media.c2.IComponentStore/software`, keystore2, Xiaomi misight/mrm.

### Flags
| HAL / service | Status | Note |
|---|---|---|
| biometrics.fingerprint@2.1 | Registered, process alive, **non-functional** | Sensor absent (expected, cable cut). Stuck client and CPU burn: consider disabling the HAL/feature at the port level (owner decision; nothing changed here) |
| traced | **restarting** (crash loop) | Perfetto/system tracing broken |
| vendor_security | **restarting** (crash loop) | Xiaomi vendor security daemon; impact unclear [I] |
| thermal@2.0 | Running but returns no current temps | Breaks Android thermal headroom/status APIs |
| IPower (AIDL) | dump FAILED_TRANSACTION; ADPF hint sessions unsupported | Likely an Android 17 IPower version mismatch with the old vendor [I] |
| GNSS measurements | Not provided | HAL is up; feature missing in this vendor/framework combination |
| camera.provider@2.4 | Running (HIDL legacy) | No AIDL camera HAL, so newer camera framework features that need AIDL are unavailable |
| health@2.1 (HIDL) | Running | No AIDL health, so no battery state-of-health, cycle count or manufacturing date through the Android 14+ API |
| keymaster@4.0 | Running | No KeyMint and no RKP; attestation limited to KM4 |
| sensors@1.0 | Running | Old HIDL sensors (no direct channel / 2.x multi-HAL) |
| lshal | 270 "cannot be fetched" warnings | Shell SELinux limits on getService, not necessarily dead services |
| Vendor init.svc props | Many vendor HAL services (camera provider, audio HAL, sensors, Wi-Fi HAL) do not appear in shell-readable `init.svc.*` | Running/crash state for those [R]; the hwbinder registration above shows they are up |

Missing for this hardware (expected but absent): AIDL KeyMint/StrongBox (no StrongBox hardware on SD870 anyway [I]), wifi.aware/rtt feature declarations, GNSS measurements, a Spatializer effect, LE Audio ISO, and an AIDL thermal skin sensor.

---

## 14. Feature map - Android 17 / HyperOS 4 vs this hardware

Legend: CAN = works or can work on this hardware; CANNOT = hardware missing; NOT ENABLED = chip capable but disabled or not exposed by Xiaomi/port; [I] = inference

| Hardware block | CAN support | CANNOT support (hardware missing) | Chip-capable but not enabled / broken here |
|---|---|---|---|
| CPU (Kryo 585, ARMv8.2) | Full Android 17 / HyperOS 4 UI; ART AOT/JIT; WALT/SchedTune boosting | ARMv9 features (SVE2, MTE memory tagging, PAC/BTI), so Android MTE hardening is unavailable | 16 KB page-size mode (needs a 16K kernel, impossible on 4.19 [I]); uclamp-based perf hints (UCLAMP_TASK off); ADPF hint sessions / CPU headroom API (HAL); userfaultfd for ART's CMC GC (config off, falls back [I]); MGLRU, io_uring, zstd/lz4 zram (kernel config) |
| GPU (Adreno 650) | Vulkan 1.3 (port driver V@0805), GLES 3.2 + AEP, Skia GL RenderEngine, HyperOS blur (real blur props on), game driver package | Hardware ray tracing, mesh shaders, AV1 decode | GPU headroom API; Vulkan level 1 only (no `vulkan.level=2` profile [I]); SkiaVK/Vulkan RenderEngine not used (GL) |
| NPU (Hexagon 698, 15 TOPS) | NNAPI 1.3 HAL, QNN/SNPE vendor AI, Xiaomi camera AI | On-device LLM tier (Gemini Nano/AICore) and HyperOS 4 large on-device AI models need newer NPUs and 12 GB+ RAM [I]; these fall back to cloud | NNAPI is deprecated in recent Android; no AIDL NN HAL [I] |
| Memory (8 GB LPDDR5) | 8 GB zram, Xiaomi mi_reclaim, lmkd | Memory extension beyond physical is software only | zram limited to lzo (no zstd/lz4 in kernel) |
| Storage (UFS 3.1 [I]) | f2fs /data, Virtual A/B, erofs vendor | - | Health/life-time reporting through the storage health API [R/HAL]; f2fs compression not used; encryption state unclear |
| Display (L11R AMOLED, 120 Hz capable) | HDR10/HLG/HDR10+, P3 wide colour, HDR/SDR ratio 2.25, adaptive brightness, AOD, 60/90/120 modes | Dolby Vision; LTPO/VRR (ARR off, no `hasArrSupport`), so Android 15+ adaptive refresh / frame-rate-category VRR (1-10 Hz) cannot work | **90/120 Hz forced off** (dfps level 60, peak 60), so user-selectable 120 Hz is not enabled; HDR via clone panel limited to 420 nits reported |
| Touch (FocalTech) | Multitouch, Xiaomi touchfeature (game mode, palm) | Stylus/pressure | Touch sample-rate switching visible only to Xiaomi HAL [R] |
| Cameras | Camera2 LEVEL_3, RAW/DNG, manual controls, 1080p120/720p240 slow-mo, OIS + EIS, HEIC, logical multi-cam zoom 1-10x | Telephoto/optical zoom, ToF/depth, 8K30 (sensor/ISP path not enabled by Xiaomi, and the 64 MP sensor cannot do 8K readout at the required speed [I]) | Public 60 fps; 10-bit HLG/HDR10 video and Ultra HDR capture (DynamicRangeProfiles absent); 64 MP max-resolution mode for third-party apps; camera extensions/night mode through AIDL camera HAL (HIDL 2.4 only) |
| Sensors | Full motion stack, step counter, significant motion, rear + front ALS/CCT, SAR, pocket, pickup, AOD triggers | Barometer (no floor-level / fused altitude), hall sensor (no flip-cover), IR proximity (ultrasonic only), hinge | hifi_sensors feature not declared; direct-channel sensors (HAL 1.0) |
| Audio | Dolby Atmos, MiSound, hi-res USB up to 384 kHz/32-bit, AAudio MMAP low latency, stereo speakers | 3.5 mm jack, FM radio | Android Spatializer + head tracking (no spatializer effect); LE Audio (ISO missing) |
| Bluetooth (5.2) | LDAC, aptX/HD/Adaptive, AAC, Opus/LHDC, A2DP offload, ASHA + HAP client | Bluetooth 5.3/5.4-only features; Channel Sounding (BT 6.0) for Android ranging [I] | **LE Audio unicast / Auracast broadcast source** (controller reports no ISO buffers; QCA6390 silicon supports BT 5.2 LE Audio [I], so vendor firmware/HAL support is missing) |
| Wi-Fi (QCA6390, Wi-Fi 6) | 11ax 2x2, WPA3/SAE-H2E/OWE/DPP, STA+AP and dual-STA multi-internet, Passpoint, TDLS, low-latency mode | Wi-Fi 6E (6 GHz), Wi-Fi 7/MLO, 60 GHz | **Wi-Fi Aware (NAN)**: driver advertises it but the feature is not declared; Wi-Fi RTT (802.11mc/az) not declared [I chip-capable] |
| Cellular (X55) | 5G NSA/SA sub-6, LTE CA, VoLTE (override on), DSDS | mmWave (not fitted on this model [I]), NTN/satellite messaging (Android 15+ satellite APIs need NTN modem) | VoNR / 5G SA depend on the carrier config of the old vendor RIL [I]; NR not active in sample |
| GNSS | Location, geofencing, low-power mode, multi-constellation [I] | - | **Raw GNSS measurements / nav messages / corrections** (needed for precision and dual-frequency app use) |
| NFC (NXP) | NFC payments, HCE/HCE-F, eSE + UICC OMAPI, MIFARE | - | NFC observe mode / polling-loop filters (Android 15+) depend on chip/HAL [I] |
| UWB / Thread | - | UWB (no chip), Thread radio | - |
| Biometrics | PIN/pattern; software 2D face unlock (MiFace, convenience class) | Class-3 face (no 3D/IR) | **Fingerprint dead** (hardware cut; HAL still running and wasting CPU) |
| Haptics (awinic LRA) | Predefined effects + amplitude, Xiaomi haptic library | - | Composition primitives, PWLE/envelope effects, frequency profiles (HAL exposes none) |
| Power / charging | 67 W (dual bq2597x + PD/QC), night charging, battery saver | Wireless charging, reverse wireless | Android battery health / cycle-count API (HIDL health 2.1); thermal headroom (no skin sensor in HAL) |
| Security / virtualization | Verified boot chain (spoofed state), FBE-capable, Keymaster 4 TEE, eSE | StrongBox (no dedicated SE for keys [I]) | **AVF / Microdroid / pKVM** (feature declared, kernel has no virtualization); KeyMint, RKP, so Play Integrity "strong" depends on spoofing [I] |
| USB | Type-C OTG host, accessory, audio accessory, 480 Mbit/s | DisplayPort alt-mode / desktop mode output (no DP alt on this model [I]) | USB 3.x (controller-capable [I], port runs at 2.0) |

---

## Appendix A - Evidence commands (all read-only)

```
adb devices
adb shell uname -a; getprop (model, release, security patch, display id, many filtered greps); getenforce
adb shell cat /sys/devices/system/cpu/online
adb shell cat /sys/devices/system/cpu/cpu{0..7}/{online,cpufreq/scaling_cur_freq,scaling_min_freq,scaling_max_freq,cpuinfo_max_freq,scaling_governor}
adb shell cat /sys/devices/system/cpu/cpufreq/policy{0,4,7}/{related_cpus,scaling_available_frequencies,scaling_available_governors,schedutil/*}
adb shell cat /sys/devices/system/cpu/cpu{0,7}/cpuidle/state*/{name,latency,disable}
adb shell cat /sys/devices/system/cpu/cpu*/cache/index*/{level,type,size}
adb shell cat /sys/devices/system/cpu/cpu{0,7}/cpufreq/stats/time_in_state
adb shell cat /proc/cpuinfo; cat /proc/loadavg; top -b -n1 -m 8; dumpsys cpuinfo
adb shell ls -l /proc/config.gz; zcat /proc/config.gz   (grep'd locally)
adb shell cat /proc/meminfo; dumpsys meminfo (summary lines); cat /proc/pressure/{memory,cpu,io}
adb shell cat /sys/block/zram0/* /proc/swaps /proc/sys/vm/*        -> permission denied [R]
adb shell ls/cat /sys/devices/platform/soc/1d84000.ufshc/{health_descriptor,device_descriptor,string_descriptors}/*  -> denied [R]
adb shell mount; df -h /data /system /vendor; dumpsys diskstats; dumpsys storaged; dumpsys mount
adb shell cat /sys/class/kgsl/kgsl-3d0/{gpu_model,max_gpuclk,gpubusy,...}   (most denied)
adb shell dumpsys gpu; dumpsys SurfaceFlinger; dumpsys display
adb shell ls /sys/class/drm; cat /sys/class/drm/card0-DSI-1/*  (denied)
adb shell dumpsys input
adb shell dumpsys media.camera   (parsed locally with a Python script)
adb shell ls /vendor/lib64/camera
adb shell dumpsys sensorservice
adb shell dumpsys media.audio_policy; dumpsys media.audio_flinger; dumpsys audio (spatializer lines)
adb shell dumpsys telephony.registry (identifiers redacted)
adb shell dumpsys wifi (SSID/BSSID/MAC excluded)
adb shell dumpsys bluetooth_manager (addresses excluded)
adb shell dumpsys nfc; ls /dev
adb shell pm list features
adb shell dumpsys location (GNSS Manager section only; no coordinates recorded)
adb shell dumpsys battery; dumpsys batterystats (capacity lines); dumpsys power; settings get global low_power (read)
adb shell ls /sys/class/power_supply; cat .../*   (values denied)
adb shell dumpsys thermalservice; cat /sys/class/thermal/thermal_zone*/{type,temp}; cat /sys/class/thermal/cooling_device*/{type,cur_state,max_state}
adb shell dumpsys hardware_properties; dumpsys performance_hint
adb shell dumpsys vibrator_manager; dumpsys usb; dumpsys fingerprint; dumpsys biometric
adb shell lshal -itrpe; service list; getprop | grep init.svc.
adb shell cat /sys/devices/soc0/{soc_id,revision,machine,family,foundry_id}
adb shell grep MediaCodec /vendor/etc/media_codecs_c2.xml /vendor/etc/media_codecs_kona*.xml /vendor/etc/media_codecs_dolby_audio.xml
host: lsusb -t; /sys/bus/usb/devices/*/speed (negotiated link speed)
```

## Appendix B - Key raw values

- `vulkanVersion = 4206592` (0x403000 = 1.3.0); `glesVersion = 196610` (3.2)
- `GLES: Qualcomm, Adreno (TM) 650, OpenGL ES 3.2 V@0805.0 (GIT@d4f1d5539c, Iad64dfeba7, 1731002436) (Date:11/07/24)`
- `hdrCapabilities HdrCapabilities{mSupportedHdrTypes=[2, 3, 4], mMaxLuminance=420.0, mMaxAverageLuminance=210.1615, mMinLuminance=0.323}`
- `mBacklight=[9.7704E-4, 0.49975574, 1.0], mNits=[2.0, 500.0, 900.0]`
- `displayManagerPolicy={defaultModeId=0, ... render=[0.00 Hz, 60.00 Hz]}`; `HWC missed frame count: 3087`
- `Wifi driver version: 5.2.022.12B Wifi firmware version: FW:1.0.1.0.1235.10`
- `lmp_version: V_5_2(0x0b)`, `iso_data_packet_length: 0`, `total_num_iso_data_packets: 0`
- `GNSS Capabilities: [SCHEDULING MSB MSA GEOFENCING LOW_POWER_MODE SATELLITE_BLOCKLIST ACCUMULATED_DELTA_RANGE(unknown)]`, `Measurements Provider: service: unregistered`
- `Hint Session Support: false`, `CPU Headroom Supported: false`, `GPU Headroom Supported: false`
- `Estimated battery capacity: 4400 mAh`, `voltage: 4431`, `temperature: 314`, `health: 2`
- `55% 716/hwservicemanager`, `35% 2900/system_server`, `9.5% 2115/android.hardware.biometrics.fingerprint@2.1-service`
- `persist.vendor.sys.fp.vendor=none`, `init.svc.traced=restarting`, `init.svc.vendor_security=restarting`
- `# CONFIG_VIRTUALIZATION is not set` vs `feature:android.software.virtualization_framework`
- `ro.crypto.state=encrypted`; `ro.boot.verifiedbootstate=orange` with `ro.boot.flash.locked=1`
