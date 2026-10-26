# POCO F4 (munch) port: combined fix plan

Status: approved by the user; build and flash once the app audit is merged.
All flashes are no-wipe; the current images stay in `secure_build/parked/` for rollback.

**Update 2026-10-25:** the pure 64-bit Global build (`payload_g64`) did not boot and is shelved. The phone runs the
32-bit port images (`out_sunday_plus`) + `secure_build/payload_tele` → `out_tele` (vendor, system, product, mi_ext).
New changes go into `payload_tele`; details in `ROM_HISTORY.md` ("Telephony, audio and privacy build").

## Done 2026-10-24/25 (flashed, checked on the phone)
- Preferred network type page (device_features.xml), VoLTE switch (volte_avail_ovr=0). The Global TeleService added
  then was reverted on 2026-10-26 (it crashed every outgoing call); the port's TeleService is used.
- Carrier config for every operator: AOSP overlay (raw mnc values) + Xiaomi CarrierStudio layer (all devices + Xiaomi 17
  Global + Bangladesh). SIM 2 (Banglalink/Ryze): VoLTE on by default, VT, Wi-Fi calling switch shown.
- APNs from `/product/etc` (overlay + merged list); Banglalink IMS APN loaded after APN Reset.
- Release tag in `ro.build.fingerprint` (carrier config cache refresh).
- SystemHelper tracker removed.
- Audio: Google hotword engines out of the DSP config + no audio HAL restart on `sys.audio.restart.hal`.
  60 s check: 0 DSP restarts, 0 HAL restarts; A2DP AAC to QCY MeloBuds N20 Pro plays.

- Official HyperOS 1 IMS app in system_ext (matches the vendor IMS daemons).
- Global apps group 1 (Photo Screensavers, Bookmark Provider, Wallpaper Carousel, Mi Mover, home layout, Health Connect
  and Safety Center overlays) and group 2 (Link to Windows, ANGLE, Google Feedback); `tools/privcheck.py` clean.

## Done 2026-10-25/26 (flashed, checked on the phone)
- Boot 70.7 s → 41.3 s (stale /system boot image removed), Perfetto background tracing off, patched mkfs.erofs
  (no dead symlinks).
- Calls work again (port TeleService). Robi: VoLTE IMS-registered, Wi-Fi calling registered on IWLAN.
- LMC 8.4: 13 configs copied to `/sdcard/LMC8.4` after the first unlock (own SELinux domain); sensor-matched fixes.
- About phone: "Maintainer – Hakuna Matata", opens the GitHub project page.
- Play Protect: GSF ID registered with Google (per-install step in INSTALL.md); root removed again.

## Open (2026-10-26)
- Banglalink: network answers "VoPS not supported" (`CODE_REGISTRATION_ERROR 5001`); likely a handset whitelist →
  user asks Banglalink (121) to enable VoLTE for the IMEI. The Xiaomi NV71527 workaround needs a newer vendor RIL.
- Earbud microphone (HFP/SCO) test during a call.
- Google mainline modules (NetworkStack, PackageInstaller, CaptivePortalLogin, ModuleMetadata): only as one full
  swap of all 29 Google APEX modules, never single apps (the port runs the AOSP module set).
- Root: removed 2026-10-25 (ReSukiSU uninstalled, Shell allowlist deleted).
- Optional: Xiaomi dialer call recorder (remove `MiuiTelephonyResCustOverlay` from mi_ext) — user decides.

## Already done (on the phone, no flash)
- Both dialers kept (2026-10-26): Xiaomi Phone/Contacts (ROM) + Google Phone (Play Store); Xiaomi Messages default SMS.
- LMC 8.4 R16 installed; 13 configs in `/sdcard/LMC8.4/`, copied by the ROM (best: POCO-F4-FINAL.xml).
- double_tap_to_sleep=1, gesture_wakeup=1, SIM activation permissions granted.
- Refresh rate kept at 60 Hz (the replacement panel is a 60 Hz part; do not change).

## Already flashed today
- product: official MiuiCamera 5.1.001140.0, Gallery 4.3.1.6-global, Global apps instead of China copies,
  Updater + System apps updater, Mi Music, Mi Share, LMC 8.4 + configs.
- vendor: official HyperOS 1 camera HAL + OV64B40/OV8856/IMX596/GC02M1 tuning, audio HAL, fingerprint HAL,
  thermal-hp-mgame/normal, PREMIER_TIER feature.

## Next build (one flash)
### Apps (mi_ext / product)
- ~~Remove Google Messages / Google Contacts~~ superseded 2026-10-26: the user keeps Google Phone/Messages next to the
  Xiaomi apps (they are Play Store installs; Google's default-app overlay in mi_ext stays).
- Remove China-only apps: product Taplus (MIUIContentExtension), ContentCatcherOS4, com.xiaomi.macro, Toolbox,
  SecurityOnetrackService, MiuiNewCallSdkResOverlay; system_ext digitalkey.
- Add Global apps (no Rust runtime needed): Google Calendar sync adapter, Smart app assistant (ThirdAppAssistantGlobal),
  Mi Ditto Global, Global Notes / clipboard / Screenshot / Screen Recorder / Quick ball / MiWallpaper / DeviceInfoQR,
  aptX Adaptive service (system_ext aptxals).
- Match the Global Security app: Global SecurityAdd and SecurityCore; Global APN database 23.0.0 (Bangladesh carriers).
- ~~Remove Google Phone~~ superseded: keep both dialers.
- Each added app gets the usual checks: Rust runtime, privapp allowlist, platform key, native-library packaging.
- Later, medium risk, one at a time with a boot test: Global AOD + Notification center, Global cross-device apps
  (Mirror, Mi Connect, continuity), xdivert, dpmserviceapp.
- Never touch: MiuiCamera 5.1, Gallery 4.3.1.6, MiuiHome, SystemUI plugin, MiSound, NQNfcNci, vendor apps.

### HyperOS tuning (system_ext / product build.prop)
| Change | Partition | Risk |
|---|---|---|
| `ro.rom.zone=2` (Global; currently 1 = China) | system_ext | low |
| remove `persist.sys.timezone=Asia/Shanghai` | system_ext | low |
| `dalvik.vm.heaptargetutilization=0.5`, `dalvik.vm.heapminfree=2m` (official munch values) | product | low |
| `persist.sys.usap_pool_enabled=true`, `dalvik.vm.usap_pool_size_max=2` | product | low |
| `dalvik.vm.background-dex2oat-threads=4`, `dalvik.vm.background-dex2oat-cpu-set=0,1,2,3` | product | low |
| add `overlay/GoogleDocumentsUIOverlay.apk` (Xiaomi 17 Global) | product | low |
| drop `com.android.MGC_9_8_102` from `vendor.camera.aux.packagelistext` | system | low |
| `ro.adb.secure=1`; remove `persist.service.adb.enable=1`, `persist.sys.usb.config=mtp,adb` (user taps "Allow" once) | product | medium |
| ConfigUpdater boot crash: align DownloadProvider with Global or drop ConfigUpdater | product | low |

### Leave unchanged
Feature flags, device level 4, LMKD/minfree, perf HAL, thermal configs, Adreno driver, kernel (no schedtune/uclamp; replacing it is high risk).

## Sunday: schedtune boost (prepared, not installed)
The running kernel (4.19.325-zyndong-perf) has schedtune built in (`/proc/cgroups`: schedtune enabled=1) but Android 17
never mounts it, and its task profiles only use the `cpu` controller + uclamp (which this kernel lacks). So foreground
apps currently get no scheduler boost. Official HyperOS 1 shipped SD870-specific files for this
(`cgroups_8250_u_stune.json`, `task_profiles_8250_u_stune.json`).

Prepared in `secure_build/staging_sunday/` (kept out of the payload until Sunday):
- `vendor/etc/cgroups.json`: mounts `schedtune` at `/dev/stune` (system:system 0755).
- `vendor/etc/task_profiles.json`: attributes STuneBoost/STunePreferIdle; the 11 official profiles merged — each keeps
  Android 17's own `cpu` action and adds Xiaomi's schedtune action (copying the official file alone would drop the cpu grouping).
- `vendor/etc/init/munch_stune.rc`: creates foreground, background, top-app, rt, audio-app, camera-daemon, nnapi-hal,
  system-background like official init.rc; prefer_idle=1 for top-app/foreground (AOSP default). The official vendor
  init.target.rc already writes colocate / sched_boost_no_override into these groups once they exist.
- `official_h1/`: the untouched official files for reference.

Sunday order:
1. Fit the power-key flex with the fingerprint sensor (fixes power button + fingerprint). Re-enrol the fingerprint;
   check the fps_hal retry loop is gone (hwservicemanager CPU back to ~0).
2. Confirm Power + Volume down opens Mi fastboot (recovery path for anything that goes wrong).
3. Copy `staging_sunday/vendor/` into `payload_tele/vendor/` (was `payload_global`), rebuild vendor, verify, flash no-wipe.
4. Check: `/dev/stune` mounted, tasks listed in `/dev/stune/top-app/tasks`, no libprocessgroup / init errors in logcat,
   then compare app-launch time, frame drops and temperature with the numbers from today.
5. Rollback if needed: `secure_build/parked/prev_out/` vendor image, one flash.
6. Only after that, if still wanted: a rebuilt kernel. Status 2026-10-24: v1–v3 failed, v4 waits for a RAM-only test (`secure_build/KERNEL.md`).

## Sunday: fingerprint sensor replacement
- Hardware: power-key flex with the side fingerprint sensor (also fixes the power button).
- After fitting: re-enrol the fingerprint. The feature and the official driver are already in the image; the
  fps_hal retry loop (about 212/s, about one CPU core) stops on its own once the sensor answers.

## User checks after the next flash
- Native camera: normal, night, portrait.
- Speaker with the screen on (notification sound, keyboard click).
- Charge with the original 67 W charger.
- Turn off developer options / ADB when the work is finished.
