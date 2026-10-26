# POCO F4 (munch) port — final system audit (2026-10-25)

Read-only checks on the running phone (port images + `out_tele`, root via ReSukiSU for reading only), 27 minutes after
a clean boot, screen off for the idle measurements. Nothing was changed by this audit.

## Summary
| Area | Result |
|---|---|
| CPU | OK — 8 cores online, schedutil, full clocks allowed (1.80 / 2.42 / **3.19 GHz**), 40–41 °C |
| GPU | OK — Adreno 650, msm-adreno-tz, 305–670 MHz (full range) |
| Memory | OK — 7.4 GB, ~1.9 GB available, 8 GB zram (lz4), lmkd running |
| Storage | OK — UFS life estimate 1/10, EOL normal, 196 GB free |
| Display | OK — 60/90/120 Hz modes offered |
| Sensors | OK — 69 sensors (LSM6DSO accel/gyro, AK0991x mag, TCS3701 light/CCT, Elliptic ultrasonic proximity, Semtech SX933x/SX932x SAR, Xiaomi virtual sensors); accel and light deliver data |
| Camera / GPS / NFC / IR / vibration | OK — 7 camera devices, GNSS enabled, NFC on, consumer IR present, vibrator with amplitude control |
| Audio / Bluetooth | OK — no DSP or HAL restarts; A2DP offload with every codec (see audio fix) |
| Apps | OK — no app crashes, no ANRs since boot |
| Security | OK for a port — SELinux enforcing, FBE encrypted, `ro.debuggable=0`, ADB secured; bootloader unlocked (orange) |
| Tools | OK — 18 Python tools compile, build scripts parse, EROFS toolchain present |
| **Battery fuel gauge** | **FAULT (hardware)** — see 1 |
| **Idle CPU** | **~1.1 cores wasted** — dead fingerprint sensor loop, see 2 |
| **Boot time** | **70.7 s to screen** — 29 s zygote stall, see 3 → **fixed: 41.3 s** |
| **Background tracing** | **Always-on Google pre-release trace running**, see 4 → **fixed: tracing off** |
| **Image builder** | **Dead symlinks in every image** (found while fixing 3), see 7 → **fixed** |

## 1. Battery fuel gauge not responding (hardware)
The TI **bq27z561** gauge on the battery's protection board fails every read with error −107 from the first second of
boot (`fg_read_rsoc/volt/current/temperature: ... ret = -107`, `Can not get MI battery data`). The kernel then reports
fixed fallback values: 15 %, 3.700 V, −0.5 mA, 25.0 °C, cycle count 1. This is why the battery percentage is wrong.
It is not a ROM issue; likely a replacement battery without a matching gauge or a loose battery connector/flex.
**Risk:** charging thermal protection cannot see the real battery temperature. Until the battery/connector is
checked: no fast charging, no unattended charging.

## 2. Idle CPU (screen off)
`hwservicemanager` 50 %, `system_server` 36 %, fingerprint HAL 11 %, `logd` 9 % — the system keeps retrying the dead
fingerprint sensor (power-key flex damage), ~385,000 log lines in 27 min. Phone-specific: hide the fingerprint feature
on this phone only (root module bind-mounting an empty `android.hardware.fingerprint.xml`, as before) until the flex
is repaired; never in the ROM. Also seen: `com.ppstrong.weeye` (user IP-camera app) ~11 % in the background.

## 3. Boot
Timeline: kernel → init 3.6 s → zygote 27.7 s → **preload 57.3 s** → system_server 60.1 s → PMS 64.2 s → AMS 67.3 s →
screen 70.7 s. Zygote logs nothing between 27.97 s and 57.3 s (29 s); normally under 1 s. Also two init children abort
(SIGABRT before exec) at 29.65 s and 31.04 s; nearby services: batteryd, mi_thermald, poweroffm64.
`zygote_next` is not the cause (identical to Global HyperOS 4).

**Cause (found 2026-10-25):** zygote stacks during the stall were in `ImageSpace::BootImageLayout::CompileBootclasspathElements`
→ waiting for `dex2oat64`/`dex2oat32`, which were compiling the whole primary boot classpath (ART core + framework + Xiaomi
jars) into memory. ART's log said why:
`boot-framework.oat: expected 6 uncompressed dex files, but found 7 in '/system/framework/framework.jar'` — the porter
added a 7th dex to `framework.jar` without rebuilding the boot image. odrefresh only checks that the files exist
("Boot images on /system OK"), so it also deleted every correct copy built on /data. Side effect: app runtime images
built against the in-memory image were rejected at each boot (`Boot image checksum mismatch`).

**Fix:** remove the stale image from system (`system/framework/arm`, `arm64`, 60 `boot*.vdex`; `payload_tele/system.remove`).
odrefresh then builds a valid primary image + mainline extension on /data once (signed by odsign) and keeps it.
Tested first with the image hidden by a bind mount (zygote start → preload 29.0 s → 0.15 s), then flashed:

| | Before | First boot after flash | Later boots |
|---|---|---|---|
| zygote start | 27.7 s | 40.0 s (one-time compile) | 27.8 s |
| zygote start → preload | 29.5 s | 0.4 s | 0.8 s |
| screen on | 70.7 s | 52.1 s | **41.3 s** |

system_server still loads `/system/framework/oat/arm64/services.odex` (accepted). The two init children that abort
before exec are unchanged (still open).

## 4. Background tracing
Perfetto session `perfetto_aot_xiaomi_external_prerelease` (started by statsd, 30-min buffers, repeating) with atrace on
for Google apps (Chrome, GMS, YouTube, Maps, Pay, Messages, Calendar, Dialer). This is Google's always-on tracing for
pre-release builds, delivered by Play Services, not stored in the ROM. Costs `traced_probes` ~3 % CPU plus trace writes
in every traced app. Options: `persist.traced.enable=0` (turns Android tracing off), or make the build identify as a
stable release.

**Fix:** `persist.traced.enable=0` in `system/build.prop` (the port sets 1 there; system is where it is defined, so
the payload copy of that file was changed). After flashing: `traced` and `traced_probes` stopped. Cost: developer
"System tracing" and app profiling through Perfetto no longer work.

## 5. SELinux and logs
Enforcing; denials are moderate background (radio 125, system_server 82, Xiaomi CIT sensor service 74, priv_app 56 in
27 min). Top log tags are all the fingerprint loop (HwBinder, HidlToAidl*, BiometricScheduler).

## 6. Recommendations (in order)
1. Battery/connector check by a technician (fuel gauge); careful charging until then.
2. Phone-only fingerprint-hide module until the flex repair (saves ~1 core and log spam).
3. ~~Stop the pre-release trace~~ — done (section 4).
4. ~~Find the 29 s zygote stall~~ — fixed (section 3). Still open: the two init children that abort before exec.
5. Remove root (ReSukiSU / Shell) when the work is done.

## 7. Image builder: dead symlinks (found and fixed 2026-10-25)
The first boot-image build did not finish booting: `/system/bin/getprop` and `rm` could not be read (`Structure needs
cleaning`; kernel: `erofs_fill_symlink: inline data cross block boundary`). The 4.19 kernel's EROFS driver only reads an
inline ("fast") symlink whose target ends inside the inode's 4 KB block; erofs-utils 1.9.1 does not keep to that, and
its `noinline_data` option applies only to regular files. Which links break depends on the layout, so every earlier
image had a few dead ones without anyone noticing:

| Image | Dead links |
|---|---|
| `out_sunday_plus/vendor` | `/vendor/rfs/msm/cdsp/readonly/firmware`, `bin/find`, `bin/setup_backmic2headphone.sh`, `bin/ulimit` |
| `out_tele/vendor` (until today) | `bin/find`, `bin/setup_backmic2headphone.sh`, `bin/ulimit` |
| `out_sunday_plus/system` | `/system/bin/fgrep`, one boot-image `fsv_meta` |
| `out_tele/system` (morning) | `losetup`, `ndc-wrapper-1.0`, `uuidgen`, one boot-image `fsv_meta` |

Fix: `tools/erofs/munch/mkfs.erofs` (erofs-utils 1.9.1 with `noinline_data` applied to symlinks too, see
`tools/erofs_patch/`), used by `build_tele.sh` with `-E noinline_data`; `tools/erofs_symlink_check.py` runs on each
image (result must be 0). system and vendor were rebuilt and flashed: 0 dead links, all of the above readable. product,
system_ext and mi_ext had 0 already.

## 8. Found after this audit (2026-10-26)
Outgoing calls failed: every call crashed the phone process (`NoClassDefFoundError: android.telecom.ConnectionService$VendorExt`
in `TelephonyConnectionService.onCreate`), the mobile network went down and stayed down until a reboot. Cause: the
Global (Xiaomi 17) TeleService added on 2026-10-24 needs a framework class this port does not have. Fixed by going back
to the port's TeleService (same VoLTE/VoWiFi logic); calls checked by the user, Robi VoLTE IMS-registered afterwards.
This audit did not place a call, so it missed it: a real call is now part of every telephony check.
