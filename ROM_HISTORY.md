# POCO F4 5G (munch) — ROM history: from the original port to the Full Global build

Device: POCO F4 5G (codename munch, also sold as Redmi K40S), Snapdragon 870 (SM8250-AC), 8 GB LPDDR5 / 256 GB UFS 3.1.
This phone: OV64B40 main camera (Sunny), OV8856 ultrawide (AAC), IMX596 front (OFilm), GC02M1 macro (Sunny),
an aftermarket 60 Hz replacement display (FocalTech touch), and a damaged power-key flex (power button + side fingerprint).

Sources: `audit/research/*.md`, `audit/agents/security/SECURITY_REPORT.md`, `audit/agents/hardware/HARDWARE_REPORT.md`,
and the build/flash logs in `secure_build/`. Facts marked *(unverified)* were not confirmed on the phone.

---

## 1. The original custom ROM (as installed)

A third-party HyperOS 4 / Android 17 port: build `OS4.0.0.24.XPKCNXM` (China HyperOS 4 base), porter @jnt100,
custom kernel `4.19.325-zyndong-perf` (ReSukiSU/KernelSU built in), China-region apps, porter-modified vendor.

### Features it had
- HyperOS 4 UI, animations, HyperIsland, the HyperOS 4 launcher, Android 17 framework.
- China HyperOS 4 apps: XiaoAi, China AI services, China camera 6.7, China Gallery, China security apps.
- Root (ReSukiSU / KernelSU) with SUSFS hiding; Kaorios toolbox (attestation/keybox spoofing).

### Bugs we found
| Bug | Cause |
|---|---|
| Purple night photos, red cast, portrait crash, "Xiaomi 17" watermark | Porter replaced the whole vendor camera stack with IMX582 tuning; this phone has an OV64B40 |
| Speaker short sounds failing (5,550 of 5,552) while the screen was on | Porter's audio HAL vs the ultrasonic proximity path |
| Phone slow and hot | Dead fingerprint sensor → fps_hal retry loop (~1.3 CPU cores) |
| Gallery crash (after adding the Global 5.4) | Global Gallery needs HyperOS Rust runtime 3.9; the port has 3.1 |
| System update missing; "Update apps" crash in Settings | Porter removed Updater and System apps updater |
| Setup language loop, "Provision keeps stopping", Xiaomi Account crash | China Provision/Account builds in a Global setup |
| Boot falls back to fastboot | The port never marked boots successful (A/B retries ran out) |
| Crash loops: traced, vendor.atfwd | vsock relay prop without kernel vsock; vendor seccomp missing gettid |
| Thermal profiles empty, ConfigUpdater crash at boot, MGC camera crash | Missing/mismatched files |

### Security threats
| Level | Threat |
|---|---|
| Critical | User data stored unencrypted |
| Critical | Framework signature-verification / downgrade bypass (porter patch) |
| Critical | Verified boot disabled, lock state spoofed |
| High | Kaorios hook: attestation spoofing, software keys, anti-detection |
| High | Kernel root with hiding (SUSFS) |
| High | Privileged-permission allowlist disabled |
| High | Old security base (vendor/firmware patch 2025-04-01; munch is end of life) |
| Medium | FRP disabled; hidden porter reboot kill-switch (`vendor_security`); permissive SELinux domains (vibrator, IR); spoofed integrity props; ADB open without authorisation |

### Missing
Global region and Google setup flow, Google Restore/"Copy apps & data", Circle to Search, Global Xiaomi apps, Updater,
correct device name (showed "Redmi K40S"), official camera tuning, thermal profiles, schedtune boost (kernel has it, Android never mounted it).

---

## 2. Official reference ROMs for munch

| ROM | Android | Notes |
|---|---|---|
| MIUI 13 (launch) | 12 | Launch firmware |
| MIUI 14 (V14.0.4.0.TLMMIXM) | 13 | Used as an extra vendor reference |
| HyperOS 1 (OS1.0.9.0.ULMMIXM, vendor V816.0.9.0) | 14 (vendor base 13) | Last major update; official camera 5.1.001140.0; final firmware |
| HyperOS 1 OS1.0.12.0 (last Global build, 2026-04-17) | 14 | Firmware byte-identical to 1.0.9; small boot/vendor/odm changes |
| HyperOS 2 / 3 | — | Never released for munch (only the POCO F4 GT got HyperOS 2) |

---

## 3. HyperOS 4 references used

| ROM | Used for |
|---|---|
| Xiaomi 17 Global (pudding) OS4.0.0.9.XPCMIXM, Android 17 | Global apps, Google integration (sysconfig flags, Circle to Search, Gemini), Global mi_ext, cust regions, Updater, overlays |
| Redmi K90 / POCO F8 Pro (annibale) China OS4.0.0.34 | China HyperOS 4 AI apps reference (later replaced by Global) |
| HyperOS 4 China base of the port (OS4.0.0.24.XPKCNXM) | The system/product the port is built on |

HyperOS 4 features and SD870 fit: cloud features (Gemini app, Circle to Search, cloud HyperAI, HyperIsland, animations,
HyperConnect) work; Soft-Light Glass is partial; Gemini Nano, UWB, satellite, LE Audio and Leica cannot work on this hardware.

---

## 4. What we changed, fixed and added (and why)

All changes are baked into the partition images (no root needed after a reset). Layers 0–4 (hardware, bootloader,
firmware, kernel, kernel modules) were not changed; see section 6.

### Vendor (hardware abstraction)
| Change | Why / benefit |
|---|---|
| Official HyperOS 1 camera HAL + 3A libs + OV64B40/OV8856/IMX596/GC02M1 tuning (47 files) | Correct colours; no purple night; portrait stable |
| `HighQualityQuickShotSupportMask=0x000000`, official `enableSensorHWSync=1`, `numConsecutiveRecovery=10` | Camera 6.7 requests fit the HyperOS 1 camera stack; recovery from camera errors |
| Official audio HAL + sound trigger | Speaker failures 5,550 → 0 |
| Official fingerprint HAL; feature enabled | Ready for the new sensor |
| Thermal profiles restored (incl. hp-mgame, hp-normal) | Proper thermal control in performance/game modes |
| fstab: file-based + metadata encryption; FRP back on | Data encrypted at rest; anti-theft |
| `vendor_security` kill-switch removed; permissive SELinux domains removed; atfwd seccomp fix | No hidden reboot trigger; SELinux confines all HALs; one crash loop gone |
| Google PREMIER_TIER feature; mi_ext overlay lines in fstab | Global Google features; Global mi_ext overlay works |
| Prepared for Sunday: schedtune mount + 11 merged task profiles (Xiaomi SD870 design) | Foreground app CPU priority on the existing kernel |

### System / system_ext / product / mi_ext (OS)
| Change | Why / benefit |
|---|---|
| Full Global: Global Provision + Google SetupWizard/Restore/PartnerSetup, 226 Global cust regions, region chosen in setup, Global zone `ro.rom.zone=2`, no China timezone default | Proper Global setup, "Copy apps & data", user picks region |
| China app copies → Global (Messages, Clock, Calculator, Compass, Recorder, MiLink, XMSF, MiSight, Barrage, Notes, clipboard, Screenshot, Screen Recorder, Wallpaper, DeviceInfoQR, Mi Ditto, Security parts, APN database 23.0.0) | Global services, BD carrier data, fewer China cloud calls |
| Removed China-only apps (Taplus, ContentCatcher, MiMacro, Toolbox, SecurityOnetrack, NewCall, digitalkey), ConfigUpdater, Google Messages/Contacts/Phone (user choice) | No duplicates, less background work |
| Added Updater + System apps updater, Mi Music, Mi Share, Google Calendar sync, aptX Adaptive, DocumentsUI overlay, VelvetCtS (Circle to Search) | Missing Global features |
| Kept on purpose: China MIUI Phone/Contacts/InCallUI (user), Gallery 4.3.1.6-global (Rust 3.1), HyperOS 4 camera 6.7, LMC 8.4 + 13 configs | Stability on this hardware |
| Device name POCO F4 5G / brand POCO | Correct name in Google, Bluetooth, setup |
| Tuning: official heap values, USAP pool, background dexopt on little cores | Fewer GC pauses, faster launches, cooler installs |
| Security: privapp allowlist **enforce**, Kaorios disabled, `ro.adb.secure=1` (the build PC's key was pre-authorised until the public release; removed 2026-10-26) | Privileged apps limited to their allowlist; ADB needs a trusted key |

### Telephony, audio and privacy build (2026-10-24/25, `secure_build/payload_tele` → `out_tele`)
After the pure 64-bit Global build failed to boot, the phone went back to the 32-bit port images and this layer was
added on top. Each change was traced in the code first (dexdump of TeleService, CarrierConfig, CarrierStudio,
TelephonyProvider, miui-services) and compared with Xiaomi 17 Global HyperOS 4 and official munch HyperOS 1.0.9.

| Change | Why / benefit |
|---|---|
| `/mi_ext/product/etc/cust_features/device_features.xml` added | Without it HyperOSCustFeatureResolve returns an empty list for unknown keys and TeleService builds an empty "Preferred network type" page; now the built-in Global page (5G/LTE/3G/2G) shows for every operator |
| `persist.dbg.volte_avail_ovr=0`, `vt_avail_ovr=0` (product) | The porter appended `=1` to vendor build.prop (commented out in official HyperOS 1); with 1, TeleService hides the VoLTE switch outside a short region list |
| ~~Global TeleService~~ **reverted 2026-10-26** (parked in `secure_build/parked/teleservice_global_2026-10-24/`) | It references `android.telecom.ConnectionService$VendorExt`, a Xiaomi 17 framework class this port's framework does not have. Every outgoing call crashed `TelephonyConnectionService.onCreate` (NoClassDefFoundError) → phone process died → mobile network down, repeating until a reboot. The port's own TeleService has the same VoLTE/VoWiFi logic (`volte_avail_ovr`, `region_support_volte`, `shouldHideEnhanced4gLteSettings`, `isSupportVoWifi`), so the network-type page and VoLTE switch fixes still apply |
| `MunchVolteOverlay` on com.android.carrierconfig (built with `aapt2 --keep-raw-values`) | Global common carrier rules + VoLTE switch for every operator; raw values keep mnc "03" (without them every two-digit mnc rule never matched) |
| `/mi_ext/product/etc/vendor_device.xml` (Xiaomi CarrierStudio layer, read last) | Xiaomi's base turns VoLTE/VT/Wi-Fi calling off for all; this adds Xiaomi's shared defaults, every Xiaomi device's operator list (majority vote), the Xiaomi 17 Global list and Bangladesh: VoLTE on, video call, Wi-Fi calling (off by default, cellular preferred). 625 VoLTE / 532 Wi-Fi calling / 233 video-call operator entries, ~118 countries |
| APNs: `MunchApnOverlay` + merged `/product/etc/apns-conf.xml` (Xiaomi 4905 + Global extras) + Xiaomi 5G/XCAP lists | TelephonyProvider used CarrierStudioApn's built-in list, which has no IMS APN for Banglalink/Teletalk; now the product files are used |
| `ro.build.fingerprint` with a release tag (product) | TeleService keeps carrier config cached until the fingerprint changes; a new tag per release refreshes it |
| `pangu/system/priv-app/SystemHelper` removed | `com.mobiletools.systemhelper`: China carrier self-registration + Baidu location SDK sending IMEI/IMSI/cell/location to China Unicom and Baidu; not in any Global or official munch ROM |
| Google hotword engines removed from `vendor/etc/sound_trigger_platform_info.xml`; `audioserver.rc` no longer restarts the audio HAL on `sys.audio.restart.hal` | Google's "Hey Google" DSP model crash-looped the audio DSP about once a second (no sound on speaker or Bluetooth); Android 17 then restarted the whole audio HAL after every rejected model. Now 0 DSP restarts, 0 HAL restarts; "Hey Google" uses software detection |

| Official HyperOS 1 IMS app (`system_ext/priv-app/ims`, with its JNI libs; the China-base copy, its extra lib and oat removed) | The IMS client that matches the HyperOS 1 vendor IMS daemons; checked first: same platform key, permissions a subset, JNI symbols present on Android 17 |
| Global apps, group 1 (2026-10-25): Photo Screensavers, Bookmark Provider, Wallpaper Carousel and Mi Mover (as system apps; Mi Mover libs extracted), Global home layout, Health Connect framework overlay, Settings Safety Center sources overlay | Global HyperOS 4 parts that fit the port without a privapp allowlist |
| Global apps, group 2 (2026-10-25): Link to Windows (DeviceIntegrationService + CrossDeviceServiceBroker + `privapp-permissions-deviceintegrationservice.xml`), ANGLE, Google Feedback | Privileged; allowlists checked with `tools/privcheck.py` (142 priv-apps, no new gap) before flashing |
| Stale boot image removed: `system/framework/arm`, `arm64` and the 60 `boot*.vdex` (system, 2026-10-25) | The porter's `framework.jar` has 7 dex files but the boot image was built for 6 (`expected 6 uncompressed dex files, but found 7`). ART rejected it every boot, zygote rebuilt the whole boot classpath in RAM (29 s, 64- and 32-bit) and odrefresh deleted the good copy because it does not check dex counts. Now odrefresh builds a valid image once on /data (~12 s on the first boot) and keeps it: **screen at 41 s instead of 71 s** |
| LMC configs reach `/sdcard/LMC8.4` (product: `bin/munch_gcam_configs.sh`, `etc/init/munch_gcam_configs.rc`, SELinux domain `munch_gcam_configs` in `product_sepolicy.cil` + `product_file_contexts`, new policy hash) | LMC reads configs only from `/storage/emulated/0/LMC8.4/`; the 12 configs in `/product/etc/gcam` were never copied there, so after a clean install LMC had none. Runs after user 0 unlocks, never overwrites. init may not write shared storage, so the script has its own domain (modelled on AOSP `preloads_copy`); checked offline with `secilc` (same `-N` compile as init; neverallow results identical to the old policy) |
| About phone "Maintainer" row: **Hakuna Matata**, opens the project's GitHub page (system_ext `priv-app/Settings/Settings.apk`, 2026-10-26) | The porter had added this row to Settings (`res/xml/my_device_settings.xml`: summary "ZynDong", link t.me/munch_hyperOs). Only those two attribute values were changed with `tools/axml.py set-attr`; the porter's Settings.apk already fails signature verification and the ROM accepts it, so editing in place adds no new risk. Tried first: a static RRO replacing that page — the page's own 0x7f references then resolve against the overlay, and every other row showed raw IDs (`@5718…`); removed |
| LMC configs fixed (2026-10-25, all 12 + 1 test config) | Sensor-matched: macro button named "Macro" (was "Wide"), noise models GC02M1 (10) on macro and OV8856 (39) on ultrawide (were IMX363/OV60A), AWB presets GC02M1 (58) / OV8856 (50) (were Samsung HMX). Main camera untouched. `POCO-F4-FINAL-XiaomiNight-test.xml` = FINAL with Xiaomi op-modes for an A/B photo test |
| `persist.traced.enable=0` (system build.prop) | Play Services ran an always-on pre-release Perfetto session (atrace in Chrome, GMS, YouTube, Maps …, ~3 % CPU in `traced_probes`) |
| Images built with a patched mkfs.erofs (`tools/erofs/munch/`, patch in `tools/erofs_patch/`) + `tools/erofs_symlink_check.py` in `build_tele.sh` | erofs-utils 1.9.1 puts inline symlink data across 4 KB blocks, and the 4.19 kernel cannot read those links (`erofs_fill_symlink: inline data cross block boundary`). Earlier images silently had 2–4 dead links each (`/vendor/bin/find`, `ulimit`, `setup_backmic2headphone.sh`, CDSP firmware link, `/system/bin/fgrep`, `losetup`, `ndc-wrapper-1.0`); the first boot-image build lost `/system/bin/getprop` and `rm` and did not boot. The patched tool stores symlinks out of line; every image is checked for 0 such links |

Tried and reverted: removing only Google's LPI usecase (audio HAL aborted), `platform_lpi_enable=false` (DSP still
crashed), removing the sound trigger HAL from the vendor VINTF manifest (QTI audio HAL needs it; boot never completed —
restored from `out_sunday_plus/vendor.img`). Details: `port_fixes/soundtrigger_fix/README.md`.

Checked and left out on purpose (2026-10-25, details in `audit/research/firmware_driver_layer_audit.md`):
- Google overlays that point the framework at Google packages the port does not have (PermissionController,
  ExtServices, CaptivePortalLogin, ModuleMetadata) and the POCO launcher overlay (the port uses the Xiaomi launcher):
  they would break permissions, the notification assistant, Wi-Fi sign-in pages or recents.
- AOSP Calendar and DeskClock resources (the Xiaomi Global versions are already installed), Gallery 5.x plugin (Gallery
  4.3.1.6 kept), region lock-screen overlays.
- Private Space: already in the port; like Global it installs only inside the private profile (`install-in-user-type`).
- Google NetworkStack / PackageInstaller / CaptivePortalLogin / ModuleMetadata ("group 3"): they belong to Google's
  mainline module set (Global: 29 of 37 APEX modules are `com.google.android.*`); the port runs the AOSP set (36 modules,
  none Google). Swapping single apps would mix the two; only a full mainline-module swap would be consistent.
- Dialer AI features (2026-10-26): Global/Google add nothing usable beyond what is installed (AI Interpreter call
  translation is in). Xiaomi call recorder stays off (Global overlay `MiuiTelephonyResCustOverlay`); enabling it is a
  one-line `mi_ext.remove` change, not applied. XiaoAI Call Assistant is China-only. Details:
  `audit/research/hyperos4_features_and_tuning.md` section D.
- Banglalink VoLTE: the network answers "VoPS not supported" (likely a handset whitelist). Newer Xiaomi software works
  around it with modem NV71527 via a hook command (118) that the 2021 vendor RIL does not have; writing modem NV directly
  was not pursued.

---

### Kernel and Settings experiments (2026-10-23/24, not part of the images)
- Custom kernels v1–v4 from `rohmanurip/kernel_munch` (CASS + uclamp, BBR, zram writeback): v1 reached Android but
  boot-looped (`bpfloader-failed`, no tracing support); v2 and v3 hung before any log. The phone was restored to the port's
  kernel each time. v4 is a crash-safe diagnostic build, packed but not tested. Full account: `secure_build/KERNEL.md`.
- Settings: the port ships the China Settings (16 languages, no Bengali). The Xiaomi 17 Global Settings (108 languages,
  same platform signature and libraries) is installed on the phone as a **system-app update for testing only**
  (undo: `adb shell pm uninstall-system-updates com.android.settings`). The About-phone "Maintainer: Hakuna Matata" row is in the image since 2026-10-26 (see the table above).
- KernelSU metamodule `meta-overlayfs` is installed; on this device it does not overlay `/system_ext` (bind mounts do).

## 5. Security now
- Encrypted data (FBE + metadata), SELinux enforcing with no permissive vendor domains, FRP on.
- Privileged-permission allowlist enforced; Kaorios spoofing off; ADB requires an authorised key.
- Kill-switch removed; release build (`user`, `release-keys`, not debuggable).
- China carrier self-registration tracker (SystemHelper, Baidu location SDK) removed (2026-10-25).
- Still open (see section 7): unlocked bootloader / orange verified boot, the porter's framework signature bypass,
  kernel root (KernelSU built into the port kernel; ReSukiSU manager installed 2026-10-25 with Shell root, for diagnostics), 2025-04 vendor/firmware patch level.

---

## 6. What was not changed (and why)
| Layer | Reason |
|---|---|
| Bootloader | Must stay unlocked for a port; relocking with a custom ROM bricks the phone |
| Firmware (modem, DSP, Wi-Fi/BT, GPU, TrustZone) | Already the final official version (1.0.12 is byte-identical) |
| Kernel + modules | Four rebuild attempts failed on the phone (see `secure_build/KERNEL.md`); the port's kernel stays until a build passes a RAM-only test |
| Nothing was compiled | Images are repackaged official/port binaries with correct SELinux labels |

---

## 7. Disadvantages and limits
- Unlocked bootloader: some banking/DRM apps may refuse to run; Widevine may drop to L3 *(unverified on this phone)*.
- End of life: vendor/firmware/kernel security patches stop at 2025-04-01.
- Port framework keeps the porter's signature-verification bypass (needs a framework rebuild to remove).
- Root is active again for diagnostics (ReSukiSU manager, Shell granted, 2026-10-25): revoke Shell or uninstall the manager when finished.
- Banglalink: VoLTE switch, IMS APN, carrier config and the official IMS app are in place, but the network answers
  "VoPS not supported" (`CODE_REGISTRATION_ERROR 5001`); the same SIM has VoLTE in another phone, so Banglalink most
  likely allows it per handset model. Ask Banglalink (121) to enable VoLTE for the IMEI. No Gemini Nano/UWB/LE Audio/Leica (hardware).
- Kernel: no binder freeze (app freezer limited) and no KVM (no Android Virtualization Framework); all drivers built in.
- "Hey Google" does not work: the Google app only uses the DSP detector (`DetectorType=trusted_hotword_dsp`, checked
  2026-10-26) and its DSP engine had to be removed (kernel/DSP crash above). The earlier note "software detection" was wrong.
- APN Reset only reloads the inserted SIM's operator; the whole APN list reloads on a clean install or when
  `ro.build.version.incremental` changes.
- Kernel lacks uclamp; until Sunday's schedtune package, foreground boost is limited.
- 60 Hz replacement panel; double-tap-to-wake depends on its touch firmware; auto-brightness calibration is off.
- Two older apps by necessity: Gallery 4.3.1.6 (Rust runtime) — and camera 5.1 kept as a fallback image.

---

## 8. Future plan
1. **Sunday:** power-key flex (power button + fingerprint) → schedtune boost vendor → camera decision (6.7 vs 5.1)
   → before/after benchmark report (`tools/bench.sh`, `tools/bench_compare.py`).
2. Medium-risk Global apps one at a time: AOD, Notification center, cross-device apps (Mirror, Mi Connect).
3. Kernel v4 (crash-safe build): RAM-only `fastboot boot` test; if it fails, read the pstore crash log and fix that cause.
4. Remove the framework signature bypass if a clean framework build becomes possible.
5. Turn off developer options when work is finished.
6. VoLTE/VoWiFi test with a GP or Robi SIM (no handset question there); Banglalink after the IMEI is enabled.
7. Global apps: groups 1 and 2 are in (2026-10-25). Google mainline modules only as one complete swap of all APEX
   modules, as a separate high-risk build with full rollback images.
8. With a working kernel build: give "Hey Google" the DSP back (official kernel drivers do not crash).
9. Remove root again when the work is done (ReSukiSU manager installed 2026-10-25 for diagnostics; Shell granted).

---

## 9. Public release T20261026 (2026-10-26)
- Build PC's ADB key removed (`product/etc/security/adb_keys` and the `/system/adb_keys` link): every user authorises
  USB debugging themselves.
- Release tag `T20261026` in `ro.build.fingerprint` (refreshes cached carrier config on update).
- Release package: firmware/kernel/vbmeta from the port package (final official munch firmware) + the six system
  images; `release/flash_linux.sh` and `release/flash_windows.bat` refuse non-`munch` phones and locked bootloaders,
  check SHA256 before flashing; `update` mode tested on the phone.
- Checked on the phone: camera/microphone privacy indicator (green dot) works; "Hey Google" cannot work (above).
- Repo made public with one clean commit: shelved builds, personal scripts and old KernelSU modules removed; scripts
  use repo-relative paths; README / INSTALL / docs/BUILD.md / AGENTS.md written for public use.

## 10. Phones without a fingerprint sensor (2026-10-27)
The developer's phone now has a plain power key (no sensor). The fingerprint HAL records
`persist.vendor.sys.fp.vendor=none`, but system_server's biometric scheduler kept restarting its "update active user"
job (`HidlToAidlSensorAdapter$2.getStartUserClient` → `FingerprintUpdateActiveUserClient` → "HIDL daemon is null")
about 1000 times a second: hwservicemanager 21 %, system_server 22 %, HAL 4 %, 674 000 jobs per boot. Xiaomi's
`isFpHardwareDetected()` knows (it reads the same property) but the scheduler never asks it.
Fix (product, automatic for everyone): `etc/init/munch_fp_absent.rc` bind-mounts `etc/fingerprint_absent.xml` (empty
feature list) over `/vendor/etc/permissions/android.hardware.fingerprint.xml` only when the property is `none`, so the
fingerprint service is not started; one SELinux rule `(allow init vendor_configs_file (file (mounton)))` + new policy
hash, checked offline (`secilc -N`, neverallow count unchanged at 321). Phones with a sensor report fpc/goodix and are
unchanged; a sensor fitted later returns after one reboot. Result: whole-phone idle CPU 18 % → 4 %, loop gone,
boot 40.9 s.

## 11. Google Phone + Contacts as the ROM default, camera 6.7 v13 baked in (2026-10-30, built from `payload_tele`, FLASHED no-wipe)
Owner request (reverses the 2026-10-24 choice of the China MIUI "Call" app). The shipped ROM is the **tele** build (port images
`out_sunday_plus` + `payload_tele`); the pure 64-bit Global build (`payload_g64`) failed to boot earlier and is shelved, so it was
NOT used. State before: Google Dialer 243 / Contacts 4.90 were Play-Store user apps; MIUI `MIUIContactsT` shipped but was never
started; two contacts handlers made `VIEW contacts` open a chooser.
Change (product partition only): `priv-app/GoogleDialer` and `priv-app/GoogleContacts` (base + arm64/en/xxhdpi splits) added;
`priv-app/MIUIContactsT` dropped through `product.remove`; `priv-app/MiuiCamera` = camera v13 (sha 3a76a1e3: watermark, Leica set,
bitrates, 20 MP front, ultra-wide LDC off, zoom SR off). `InCallUI` kept (the port's `MiuiTelecomResOverlay`, priority 45, still names
it). The privapp allowlist for both Google apps already exists in the base (`privapp-permissions-gms-international-product.xml`, and
`GoogleDialer-...xml` shipped in mi_ext): `privcheck.py` 44 priv-apps, 0 missing; verify_img errors 0; erofs_symlink_check crossing 0.
Flash: `secure_build/flash_product_nowipe.sh` (fastbootd, `fastboot flash product`, no erase), 2 min; boot 25 s; SELinux enforcing; crash
buffer empty; contacts 1387 and call log intact; both apps are SYSTEM + UPDATED_SYSTEM_APP; DIAL, VIEW contacts and PICK resolve to
Google Dialer / Google Contacts / contacts picker without a chooser; cold start Dialer 1.1 s, Contacts 0.68 s (warm 0.22 / 0.16 s).
Open: a real call (place + receive, SIM 1 and SIM 2) must be tested by the owner; `VIEW calls` resolves to Truecaller (user app).
Rollback: `bash secure_build/flash_product_nowipe.sh secure_build/out_tele_T20261026_prev "rollback"` (that image is byte-identical to the
product partition that was on the phone before; checksums verified). Build note: the product image step needs ~14 GB free
(tar 4.4 GB + about 8 GB of working output); at 12 GB it ran out of disk and aborted.

## 12. Camera v15 + PhotoStage app, release tag T20261031b (2026-10-31, built from `payload_tele`, FLASHED no-wipe)
Owner approved. Product partition only (`flash_product_nowipe.sh`, fastbootd, no erase). Flashed in steps the same night: T20261031 (camera v14 + first PhotoStage), then T20261031b rebuilt three times while testing the ROM copy exposed PhotoStage defects; the last image is the one on the phone.
`priv-app/MiuiCamera` = **v15**, sha b2e51dfb: v13 + `tools/re/hide_modes.sh` (Sticker avatars/Mimoji, Mimoji video, Clone, Movie effects hidden; they crashed) + `tools/re/video_keep_fix.sh` (finished videos no longer deleted when the app reads duration 0). New `app/PhotoStage`, sha 8f66f269 (`docs/camera/08_PHOTO_STAGE.md`).
Image `secure_build/out_tele/product.img`, sha256 fbc668b2...: verify_img errors 0, erofs_symlink_check crossing 0, privcheck 44 priv-apps 0 missing.
On the phone: boot ~60 s, SELinux enforcing, crash buffer empty, camera and PhotoStage run from /product; 19-entry mode sweep 0 crashes; native photo copied with the camera open; LMC photo skipped; 6 min 50 s 4K60 clip saved (5.14 GB). LMC photo, Portrait and video were checked on the T20261031 image (0 crashes), photo again on the final image. A Facebook startup crash appeared once after one reboot (`Liger initialization failed`), not again in later use or boots.
Rollback: `bash secure_build/flash_product_nowipe.sh secure_build/out_tele_T20261031_v14 "rollback to v14"`; older: `out_tele_T20261030_v13`, `out_tele_T20261026_prev`.
Build notes: `build_tele.sh` stops at its final `fusermount -u` (busy) before writing SHA256SUMS: run `fusermount -uz` and write the sums by hand; the image itself is complete. Never `rm -rf` the work dir before checking `mount | grep work_tele`.
Still to do by the owner: a real call on both SIMs.
