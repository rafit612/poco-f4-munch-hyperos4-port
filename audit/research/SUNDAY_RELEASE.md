# Sunday release — POCO F4 (munch) HyperOS 4 port

Goal: a smoother, cooler, longer-lasting phone with a better camera, proven with numbers.
Method: `tools/bench.sh before_2026-10-23` (today) → install → `tools/bench.sh after_sunday` →
`python3 tools/bench_compare.py before_2026-10-23 after_sunday` gives the release-notes table.
Only measured numbers go into the release notes; nothing is estimated.

## What goes in
| # | Change | Layer | Expected effect | Measured by |
|---|---|---|---|---|
| 1 | New power-key flex (power button + side fingerprint) | hardware | Fingerprint and power button work; the fps_hal retry loop (~1.3 CPU cores) stops | `idle_cpu_pct`, `battery_current_ma`, `battery_temp_c`, top idle processes |
| 2 | Schedtune boost (`staging_sunday/`): `/dev/stune` mounted, 11 task profiles = Android 17 cpu action + Xiaomi SD870 schedtune action | vendor config | Foreground app gets CPU priority: faster launches, fewer dropped frames under load | `launch_*_ms`, `jank_*_pct`, `frame_p90_launcher_ms` |
| 3 | Camera app decision: keep 6.7 (HyperOS 4) if night + portrait pass, otherwise back to 5.1 | product | Best camera that is stable on the official OV64B40 tuning | night/portrait photos + crash log, `launch_camera_ms` |
| 4 | Clean-up: drop `com.android.MGC_9_8_102` from the vendor aux camera list | vendor | Cosmetic | — |

## Already in the phone (since today, part of the baseline)
Official OV64B40/OV8856/IMX596/GC02M1 camera tuning, official audio and fingerprint HALs, thermal profiles,
quick-shot mask, Global apps instead of China copies, Google Messages/Contacts/Phone removed, heap/USAP/dexopt
tuning, Global zone, ADB secure (no pre-authorised key since the public release), LMC 8.4 + 13 configs (copied to /sdcard/LMC8.4 by the ROM since 2026-10-25).
Added 2026-10-24/25 (`out_tele`): Global SIM settings (network type, VoLTE, Wi-Fi calling), carrier config and APNs
for every operator, SystemHelper tracker removed, audio DSP crash loop fixed (Bluetooth and speaker sound),
Global apps groups 1-2 (Wallpaper Carousel, Mi Mover, Link to Windows, ANGLE, Feedback, Photo Screensavers ...).
Later on 2026-10-25: boot 70.7 s → 41.3 s (stale boot image removed), Perfetto background tracing off, and images
built with the patched mkfs.erofs (no more dead symlinks in system/vendor). The "before" benchmark baseline was taken
before these; boot time and app start numbers will differ for this reason too.
2026-10-26: outgoing calls fixed (Global TeleService reverted), About-phone Maintainer row, both dialers kept.

## Not in this release (and why)
- New kernel: three builds failed on the phone (2026-10-24); v4 is a crash-safe test build, not ready for release (`secure_build/KERNEL.md`).
- VoLTE on Banglalink: switch, carrier config, IMS APN and official IMS app are in place (2026-10-25); the network
  answers "VoPS not supported" (handset whitelist) → ask Banglalink (121) to enable the IMEI.
- Gemini Nano, UWB, LE Audio, Leica: missing certification / hardware / Bluetooth firmware support.
- 120 Hz: the replacement panel is 60 Hz.

## Sunday checklist
1. Fit the power-key flex; boot; enrol the fingerprint; check hwservicemanager CPU is near 0.
2. Check Power + Volume down opens Mi fastboot.
3. Camera test (night + portrait) → decide 6.7 or 5.1.
4. Copy `staging_sunday/vendor/` into `payload_tele/vendor/`, apply #3/#4, rebuild (`build_tele.sh`), verify, flash no-wipe.
5. Check `/dev/stune` + `/dev/stune/top-app/tasks`, no libprocessgroup/init errors.
6. Leave the phone idle 15 min (dexopt), then `bench.sh after_sunday` and the comparison table.
7. Rollback images: `secure_build/parked/prev_out/` (`vendor.img.before_stune`, `product.img.cam51`).
