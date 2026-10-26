# POCO F4 (munch) port: firmware, driver, kernel and OS-layer audit (2026-10-25)

Read-only research on the running phone (root via ReSukiSU for this audit), the phone partition snapshot
(`~/kernel_build/phone_snapshot/`), official HyperOS 1.0.9 Global (`stock_rom_1.0.9`) and Xiaomi 17 Global HyperOS 4
(`stock_rom_global17`). Nothing was changed by this audit.

## 1. Firmware (both slots identical)
| Part | Version | Notes |
|---|---|---|
| Modem (SDX55) | MPSS.HI.2.5.1.c1-00068 (built 2023-11-14), baseband 2.5.1.c1-14.1-0324 | 105 carrier MBNs; no Bangladesh MBN, BD SIMs use `common/ROW` |
| Audio DSP | ADSP.HT.5.3-00614 (2021-08-22) | Same as the porter's package |
| Bluetooth | BTFM.HST.1.0.0-00218 | QCA6390 "hastings" |
| Wi-Fi | WLAN.HST.1.0.1.r1-01235 | QCA6390, PCI 17cb:1101 |
| Boot / AOP / TrustZone | BOOT.XF.3.2-00354 / AOP.HO.2.0-00194 / TZ.XF.5.8-00274 | |
| Vendor | HyperOS 1.0.9 Global `V816.0.9.0.ULMMIXM`, security patch 2025-04-01 | Final official munch release (1.0.12 byte-identical) |
There is no official HyperOS 4 for munch, so no newer firmware exists. Nothing to update.

## 2. Kernel and drivers
- Running kernel: `4.19.325-zyndong-perf` (porter, clang 16). It is **monolithic**: `/proc/modules` is empty, none of the
  44 official vendor modules (built for official `4.19.157-perf`) are loaded.
- Built-in equivalents exist for: audio (q6/LSM, WCD938x, TFA98xx, WSA881x, MBHC, USF), Wi-Fi qca_cld3 (QCA6390/6490),
  fingerprint (FPC1540, Goodix gf_spi), exFAT, rmnet_shs/perf.
- Not in the kernel (not needed on munch): llcc_perfmon, mpq demux, gspca, sla, rdbg, fragmentize, generic `lcd` class.
- Hardware detected at boot: speaker amp **NXP TFA9874** (driver v6.7.3, I2C 1-0034), haptics **AW86927** (driver reads
  MediaTek-style `mtk,*` waveform properties that the munch DT does not have, so it uses defaults), Wi-Fi/BT QCA6390 OK.
  PM8009 (camera PMIC) is not fitted on this board; its probe errors are harmless (rails come from PM8150).
- Known kernel-caused faults: the built-in audio LSM driver crash-loops the ADSP with Google's hotword model
  (worked around, see `port_fixes/soundtrigger_fix/README.md`).
- Kernel features: USB UVC gadget **yes** (`uvc.0` configured), configfs, fs-verity, dm-verity, BPF, incremental FS, PSI,
  seccomp **yes**; **no** binder freeze (Android app freezer is limited; Xiaomi millet covers part) and **no** KVM
  (no Android Virtualization Framework / Terminal app).

## 3. Modem-side IMS (VoLTE)
- IMS stack: official HyperOS 1 `org.codeaurora.ims` now in system_ext (matches the vendor IMS daemons).
- Banglalink attach: network VoPS = NOT_SUPPORTED (LteVopsSupportInfo 3) → `CODE_REGISTRATION_ERROR 5001 vops not support`.
  The same SIM gets VoLTE in another phone, so Banglalink most likely allows VoLTE per handset model (IMEI/TAC list).
- Newer Xiaomi software works around this with MiRilHook `EVENT_OEMHOOK_NV_CMD` (118) / `NV71527_ADD_NO_VOPS_RAT`;
  the 2021 vendor RIL (`libril-qc-hal-qmi.so`) does not implement command 118, and official HyperOS 1 never had it.
  Writing modem NV directly was not pursued. User option: ask Banglalink (121) to enable VoLTE for the IMEI.

## 4. Global HyperOS 4 apps missing on the phone (62; table: `global_only_apps.tsv`)
Privileged apps need their permission allowlist (`ro.control_privapp_permissions=enforce`; a gap stops boot).

**Group 1 – low risk (normal apps / overlays, no allowlist):** Xiaomi Calendar Global, PhotoTable screensaver,
BookmarkProvider, DeskClock resources, Wallpaper Carousel (MiGalleryLockScreenGlobalOs4) + lockscreen overlays,
HyperGallery Global plugin, MIUIGlobalLayout, Mi Mover Global (huanji), CrossDeviceServiceBroker (Link to Windows broker),
POCO launcher resource overlay, Google mainline config overlays (PermissionController, ExtServices, HealthFitness,
CaptivePortal, ModuleMetadata, DeviceLock, SafetyCenter), fs-verity build manifests (system, system_ext).

**Group 2 – privileged, small allowlists, useful:** Private Space (2 perms), Link to Windows DeviceIntegrationService (7),
ANGLE (1), Google Feedback (3).

**Group 3 – replace an existing core component (one at a time, highest risk):** Google NetworkStack (18 perms, replaces
AOSP NetworkStack), Google PackageInstaller (9, replaces AOSP PackageInstaller), Google CaptivePortalLogin and
ModuleMetadata (replace the AOSP ones; never keep both).

**Not recommended:** AICore + overlay (Gemini Nano not supported on SD870), eSIM apps + transfer overlay (munch has no
eSIM), Google Dialer (user excluded), ConfigUpdater (crashed at boot before), carrier-specific apps (dti aone/millicom,
O2 Entitlement, WDS Kryten, H3G/Vodafone COTA overlays), Facebook preinstall services, MSA/AnalyticsCore (ads and
telemetry), PlayAutoInstall stub, FrameworksResNonModem overlay (for devices without a modem), CameraTools beta,
YT Music / Mi Community / Mi Store (install from the store if wanted).

## 5. Result (2026-10-25)
- **Group 1 flashed:** Photo Screensavers, Bookmark Provider, Wallpaper Carousel (system app), Global home layout,
  Mi Mover (system app, native libs extracted), Health Connect framework overlay, Settings Safety Center overlay.
  Left out after checking: POCO launcher overlay (would break recents; Xiaomi launcher in use), Google PermissionController /
  ExtServices / CaptivePortal / ModuleMetadata framework overlays (point at packages the port does not have), AOSP
  Calendar and DeskClock resources (Xiaomi Global versions installed), Gallery 5.x plugin (Gallery 4.3.1.6 kept),
  region lock-screen overlays.
- **Group 2 flashed:** Link to Windows (+ its allowlist file), ANGLE, Google Feedback. Private Space was already in the
  port; by design (same as Global) it installs only inside the private profile.
- **Group 3 not applied:** the four apps are part of Google's mainline set (Global: 29 of 37 APEX modules Google-named);
  the port runs the AOSP set (36 modules, none Google). Only a complete module swap would be consistent.
