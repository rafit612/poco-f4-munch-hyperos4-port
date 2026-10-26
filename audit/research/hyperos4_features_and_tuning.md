# HyperOS 4 feature completeness and CPU/GPU/memory tuning audit (munch, SD870)

Read-only audit, 2026-10-23. Compared the images currently flashed (`out_global`: system, system_ext,
product, mi_ext, vendor) with Xiaomi 17 Global HyperOS 4 (OS4.0.0.9 pudding: system, system_ext, product,
mi_ext) and official munch HyperOS 1 (V816.0.9.0). Live values come from the phone (adb getprop/dumpsys).

## A. HyperOS 4 completeness (non-app components)

### A1. Framework jars
| Only in Xiaomi 17 | Purpose | Verdict |
|---|---|---|
| system/framework/vendor.xiaomi.hardware.uniperf-V1-java.jar | Java stub for Uniperf HAL | Irrelevant: munch vendor has no Uniperf HAL. Adding it would only create more "service not found" retries. |
| system_ext/framework/vendor.qti.sla.service-V1-java.jar | QTI SLA client | Irrelevant: no matching vendor service. |
| system_ext/framework/vendor.xiaomi.aidl.minet / miwill | Xiaomi network accel / MiWill AIDL stubs | Irrelevant: no vendor HAL on munch. |
| videoservice-V12 (ours V9) | Xiaomi video HAL stub | Keep V9, which matches the vendor HAL generation. |

Only ours: `miui.car.server.jar` (car connectivity; harmless).
Conclusion: no needed framework jar is missing.

### A2. Feature flags (permissions/sysconfig)
Only in Xiaomi 17: `telephony.euicc(.mep)` (no eSIM on munch, correct), `android.software.virtualization_framework`
(needs pKVM and newer kernels; munch runs kernel 4.19, correct), `AICORE_QC` and `AICORE_QC_SM8850` (Gemini Nano on SM8850, correct to omit).
Ours additionally has `com.google.android.feature.PREMIER_TIER` (official munch HyperOS 1 flag, restored) and `com.nxp.mifare`.
Conclusion: the flag set is correct for SD870. The Google/Gemini cloud features, Circle to Search and Lens flags are present (see earlier work).

### A3. Overlays (RROs)
| Only in Xiaomi 17 | Target | Verdict |
|---|---|---|
| GoogleDocumentsUIOverlay | com.google.android.documentsui (installed on our phone) | **Missing and relevant.** Low-risk add (product/overlay). |
| GmsSettingsOverlaySafetyCenter | com.android.settings | Optional (Google Safety Center entry in Settings). Low to medium risk. |
| GooglePermissionController(Framework)Overlay, MiuiPermissionControllerOverlay, SafetyCenterMiuiOverlay, GoogleExtServicesConfigOverlay, ModuleMetadataGoogleOverlay, CaptivePortalLoginFrameworkOverlay, GoogleHealthFitnessFrameworkOverlay, GoogleDeviceLockControllerOverlay | com.google.android.* mainline modules or `android` pointing at them | **Do not add.** Our port runs AOSP `com.android.*` modules (permissioncontroller, captiveportallogin, healthconnect, devicelock). These overlays would point the framework at packages that don't exist. |
| MiuiGlobalWallpaperOverlay / MiuiGlobalLockscreenOverlay | Xiaomi 17 default wallpapers | Irrelevant (we keep the POCO wallpaper overlays). |
| EsimTransferOverlay, AICoreConfigOverlay, H3g/Vodafone Cota | eSIM, AICore SM8850, carriers | Irrelevant. |

### A4. Properties (system/system_ext/product/mi_ext build.prop)
Device classification. The live phone reports `persist.sys.computility.cpulevel=4`, `gpulevel=4` and
`persist.sys.computilityV2.devicelevel=4`; Xiaomi 17 is 6. Level 4 is the right "upper mid / previous flagship" class for SD870,
and it keeps heavy effects moderate. `ro.config.low_ram=false` is correct.
High-end visual props are on: `ro.miui.has_real_blur=1`, `persist.sys.background_blur_supported=true`,
`persist.sys.advanced_visual_release=4`, `ro.miui.backdrop_sampling_enabled=true`,
`ro.sf.blurs_are_expensive=1`, `ro.launcher.blur.appLaunch=1`. These are acceptable for Adreno 650, though
blur on app launch is the most expensive one. Keep it unless frame drops show in gfxinfo.

Problems found:
| Prop | Live value | Source | Problem | Fix |
|---|---|---|---|---|
| `ro.adb.secure` | **0** | product/etc/build.prop (porter) | ADB accepts any computer **without the RSA authorization prompt**. This is a security hole on a phone with a broken power key. | product: `ro.adb.secure=1`; remove `persist.service.adb.enable=1` and `persist.sys.usb.config=mtp,adb` (the Xiaomi 17 Global value is 1). Accept the prompt once from this PC. Medium risk: adb stays usable only after you tap "Allow". |
| `ro.rom.zone` | **1** (China) | system_ext/etc/build.prop (China base). Vendor says 2, but system_ext wins. | Region zone 1 = CN. Xiaomi apps (Account, Cloud, Security, Themes) use it to pick China services. Xiaomi 17 Global = 2. | system_ext: `ro.rom.zone=2`. Low risk. |
| `persist.sys.timezone` | Asia/Dhaka (live; user/network set) | system_ext sets `Asia/Shanghai` | The China default timezone applies only before the network sets one, e.g. after a reset. | Remove from system_ext (Global has none). Low risk. |
| `dalvik.vm.heaptargetutilization` / `heapminfree` | 0.75 / 512k | vendor only (product override missing) | Official munch HyperOS 1 product overrides these to **0.5 / 2m** (less frequent GC, smoother on 8 GB). Our product lost these lines. | product: add `dalvik.vm.heaptargetutilization=0.5`, `dalvik.vm.heapminfree=2m`. Low risk. |
| `ro.dalvik.vm.enable_uffd_gc` | false | system | Correct: the 4.19 kernel lacks userfaultfd minor-fault support, so keep it false. | none |
| `vendor.camera.aux.packagelistext` | contains `com.android.MGC_9_8_102` | system build.prop | Stale (MGC removed). Harmless. | Remove on the next system rebuild. LMC (`org.codeaurora.snapcam`) is already in the vendor aux list. |
| LE Audio (`bluetooth.profile.bap/csip/hap/vcp/...`) | false | system_ext | Correct for SD870/QCA6390 (no LE Audio offload). Keep. | none |
| Refresh rate | `secure user_refresh_rate=60`, `system peak_refresh_rate=60`, `min_refresh_rate=60.0`, `persist.vendor.dfps.level=60` | settings (data), not image | **The panel runs at 60 Hz.** The 120 Hz mode exists (supported 120/90/60, default mode id 2 = 120 Hz), but the user setting is 60 (restored, or the screen's "Standard" option). | User choice: Settings > Display > Refresh rate "High (120Hz)", or `settings put secure user_refresh_rate 120; settings put system peak_refresh_rate 120; settings put system min_refresh_rate 60`. Caution with the aftermarket panel: if flicker appears at 120, return to 60. |

Only in Xiaomi 17 (mostly flagship daemons or not applicable): `persist.sys.llm.*` (on-device LLM: SM8850 NPU, not for SD870),
`persist.sys.mimd.reclaim`, `persist.sys.memory_standard.*`, `persist.sys.umms.v2`, `persist.sys.spc.extra_free_*`,
`persist.sys.usap_pool_enabled=true`, `persist.sys.dynamic_usap_enabled=true`, `dalvik.vm.usap_pool_size_max=2` (ours 1),
`persist.sys.enable_perf_hint`, `persist.sys.touch_up_boost.enable`, `persist.sys.gl_thread.boost.enable`, `persist.sys.turbosched.preboost`,
`ro.display.enable_pwm_switch` (needs a PWM/DC switchable panel, no), `persist.sys.app_dexfile_preload.enable`.
The USAP pool (pre-forked app zygote processes) is safe and helps app launch time on 8 GB:
`persist.sys.usap_pool_enabled=true` plus `dalvik.vm.usap_pool_size_max=2` (product or system). Low risk, optional.
Touch, GL and turbosched boost props depend on Xiaomi's turbosched kernel and services. munch's 4.19 "zyndong-perf" kernel has no
uclamp, so their effect is unknown. Not recommended blind.

## B. CPU / GPU / scheduler / memory vs hardware

### B1. Kernel and cgroups (live)
- Kernel `4.19.325-zyndong-perf-g7e817c4ca270`. This is a **custom (porter) kernel**, not Xiaomi's stock 4.19.157.
- `/dev/stune` (schedtune) **does not exist**, and `/dev/cpuctl/*` has only `cpu.shares` / `cfs_*`, **with no `cpu.uclamp.*`**.
  Android 17's task_profiles boost actions (`UClampMin` / `UClampLatencySensitive`, plus the `schedtune` JoinCgroup for audio-app)
  therefore do nothing. Foreground and top-app are prioritised only by cpu.shares and cpusets. Frequency boosting relies on the
  **QTI perf HAL** (`perf-hal-2-2` running, configs byte-identical to official) and `IPower/default` (present). This is the
  Android 17 + 4.19 limitation the hardware report predicted. It can't be fixed without a kernel change (out of scope; risky).
- cpusets (live): top-app 0-7, foreground 0-2,4-7, background 0-2, system-background 0-3, **restricted 0-7**.
  The official QC layout gives restricted (background-restricted apps) 0-3, so restricted apps can currently use the prime core.
  Low-impact, low-risk fix via the vendor init `write /dev/cpuset/restricted/cpus 0-3` (vendor init.target.rc). Optional.
- task_profiles.json (system) is the original port's, with Xiaomi QCOM additions. It parses fine (jsoncpp allows comments).

### B2. Memory (8 GB: MemTotal 7.42 GiB)
- LMKD: `ro.lmk.use_minfree_levels=true`, `kill_heaviest_task=true`, `kill_timeout_ms=15` (identical to official munch).
  The MIUI minfree tables `persist.sys.minfree_8g=73728,92160,110592,387072,1105920,1451520` are present, and
  `persist.sys.mms.write_lmkd=true` lets Xiaomi's memory service drive them. That matches official.
- `ro.sys.fw.bg_apps_limit=40`: fine for 8 GB, and it suits multitasking.
- Dalvik heap: heapsize 512m / growthlimit 256m match official. **heaptargetutilization 0.75 and heapminfree 512k differ
  from official munch (0.5 / 2m)**. See A4 for the fix.
- zram/swappiness: unreadable without root (permission denied). The official vendor init is unchanged; no change proposed.
- ART: dex2oat threads 6 (foreground) and 8 (background/boot) across cpus 0-7, `image-dex2oat-filter=speed`. Fine for SD870.
  Background dexopt using all 8 cores heats the phone during app restores, which explains the restore-time heat seen earlier.
  Optional: `dalvik.vm.background-dex2oat-threads=4` plus `dalvik.vm.background-dex2oat-cpu-set=0,1,2,3` (system or product). Low risk.

### B3. GPU / graphics
- Adreno 650 GLES driver **V@0805.0 (11/07/24)**, newer than munch stock. It's the porter's updated driver and works
  (keep it; the architecture audit came to the same conclusion). An updatable driver package `com.qualcomm.qti.gpudrivers.kona.api30` is present.
- HWUI: launcher pipeline "Impeller (Vulkan)" (Flutter launcher). Global HWUI/RenderEngine use Android 17 defaults (no override props).
  HWUI cache props are bigger than Xiaomi 17's (layer 64, path 48, texture 96, text 2048x2048). That's fine with 8 GB.
- SurfaceFlinger: `max_frame_buffer_acquired_buffers=3`, idle/touch timer 1000 ms, content detection on, and frame-rate override
  off. OK. SF affinity `ro.miui.affinity.sfui/sfre=4-6` and `persist.sys.miui.sf_cores=4-7` (big cores) are correct for the
  1+3+4 layout (cpu7 = prime).

## Recommended changes (ranked)
1. product: `ro.adb.secure=1`; drop `persist.service.adb.enable=1` and `persist.sys.usb.config=mtp,adb`. Security, medium risk (needs one "Allow USB debugging" tap).
2. system_ext: `ro.rom.zone=2`. Global region services. Low risk.
3. system_ext: remove `persist.sys.timezone=Asia/Shanghai`. Low risk.
4. product: `dalvik.vm.heaptargetutilization=0.5`, `dalvik.vm.heapminfree=2m` (official munch values). Low risk.
5. Settings (no flash): refresh rate back to 120 Hz if the aftermarket panel tolerates it.
6. product: add `overlay/GoogleDocumentsUIOverlay.apk` from Xiaomi 17. Low risk.
7. Optional product/system: `persist.sys.usap_pool_enabled=true`, `dalvik.vm.usap_pool_size_max=2`. Low risk.
8. Optional system/product: `dalvik.vm.background-dex2oat-threads=4`, `dalvik.vm.background-dex2oat-cpu-set=0,1,2,3` (less heat during installs). Low risk.
9. Optional vendor: restricted cpuset 0-3. Low risk.
10. On the next system rebuild: drop `com.android.MGC_9_8_102` from `vendor.camera.aux.packagelistext`. Cosmetic.
Do NOT add: Uniperf/SLA/minet/miwill jars, Google-module framework overlays, AICore/LLM/eSIM/virtualization flags, PWM switch, LE Audio.
Kernel limitation (no uclamp/schedtune) means task-profile boosts are inert. Accept it, or change the kernel later (high risk).

## C. Package gap vs Xiaomi 17 Global HyperOS 4 (2026-10-25)
Phone vs Global images (system, system_ext, product, mi_ext; APEX modules not counted): 405 Global packages, 337 shared,
68 Global-only. Phone-only packages are user apps, APEX modules and vendor apps; no system duplicates found.
Notable Global-only: Private Space, Device-as-webcam, Microsoft Link to Windows (DeviceIntegrationService +
CrossDeviceServiceBroker), Google NetworkStack / CaptivePortalLogin / PackageInstaller / ConfigUpdater / Feedback /
mainline adservices + telemetry, AICore (Gemini Nano; not usable on SD870), Wallpaper Carousel, Mi Browser Global,
App Vault (Global minus screen), Mi Community / Mi Store, Global Calendar, Tag, PhotoTable, YT Music, Trichrome library,
eSIM apps (munch has no eSIM), Google Dialer (excluded by the user). Most are priv-apps: with
`ro.control_privapp_permissions=enforce` each needs its allowlist or the phone does not boot, so they go in one at a time.
Applied 2026-10-25: groups 1 and 2 (see `firmware_driver_layer_audit.md` section 5); Google mainline apps not applied.

## D. Dialer and AI call features (researched 2026-10-26, no ROM change)
Decision: keep both dialers — Xiaomi Phone/Contacts (China build 18.30.00.20 + InCallUI 40.01.05, in the ROM) and Google
Phone (Play Store; Google's default-app overlay `GmsConfigOverlayComms` in `/mi_ext` stays).

| Feature | Source | State on this ROM |
|---|---|---|
| Xiaomi call recorder | InCallUI `RecorderUtils.isSupportRecord`: China build always; international build asks TeleService `TelephonyCapabilities.supportsCallRecording` → off if region cust feature `unsupport_call_recording_gl` (bg cz de es fr gr it pl ro), else TeleService bool `config_call_recording` (default **true**), else only if Google Dialer is deleted | **Off**: `/mi_ext/product/overlay/MiuiTelephonyResCustOverlay.apk` sets only `config_call_recording=false`. Removing that overlay would enable it (BD not blocked); prepared, not applied (user's choice) |
| AI call translation ("Interpret call audio") | Xiaomi Global HyperAI, `com.xiaomi.aiasst.vision` | **Installed** (5.14.3.40, newer than Global 17's 5.12.10.60) |
| Recording transcription / speaker recognition / AI summary | Xiaomi Global HyperAI (Recorder) | Works on recordings; calls only if recorded |
| XiaoAI Call Assistant (AI answering, AI call log) | `com.xiaomi.aiasst.service` (K80/K90 China), XiaoAI speech, China cloud | Not installed; China-only (copy in `hyperai_apks/`, `port_fixes/hyperai_k90/`) |
| Google Phone call recording | Google | Needs Google Phone shipped as a system app + supported country; here it is a Play Store install |
| Call Screen / Hold for Me / Call Notes | Google | Mostly Pixel-only; Call Screen in few countries (not BD) |

Dialer code markers used: InCallUI references `com.xiaomi.aiasst.service` (`use_ai_call`, `aicall.provider`); Contacts references
`com.xiaomi.aiasst.service` and `com.xiaomi.aicr` (installed).
