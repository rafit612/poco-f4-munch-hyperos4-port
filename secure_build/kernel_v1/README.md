# Kernel v1 (test candidate) — POCO F4 (munch) HyperOS 4 port

**Status (2026-10-24): failed on the phone, do not use.** It reached Android, then rebooted every time with
`reboot,bpfloader-failed` (no FTRACE/TRACEPOINTS/BPF_EVENTS) until slot A was marked unbootable. Superseded by v3/v4;
see `secure_build/KERNEL.md` for all versions, what was found and the recovery steps.

## What it is
| | Running kernel (porter) | Kernel v1 |
|---|---|---|
| Version | 4.19.325-zyndong-perf (ZyC clang 16) | 4.19.325-perf+ (AOSP clang 20, r547379, LTO) |
| Source | not public | `rohmanurip/kernel_munch` branch `base` (see `SOURCE.txt`) |
| Scheduler | WALT + schedtune | **CASS + uclamp** (Android 17 task profiles work natively) |
| Memory | PSI | PSI (kept for lmkd) |
| Network | cubic | **BBR** (default) |
| zram | — | LZ4 available |
| Drivers | audio, Wi-Fi, fingerprint, exFAT as vendor modules | audio, Wi-Fi (qca6390), fingerprint, exFAT, sla **built in** |
| Root | ReSukiSU (KernelSU fork) | **RKSU** (`rsuntk/KernelSU`): a different KernelSU fork |

Files: `boot_v1.img` (new kernel + the port's unchanged ramdisk; header identical to the port's), `vendor_boot_v1.img`
(new dtb + the port's vendor ramdisk and cmdline), `dtbo_v1.img`, `kernel_v1.config`, `SOURCE.txt`, `SHA256SUMS`.
Packing was self-tested: repacking the original kernel/dtb with the same tools gives byte-identical boot and vendor_boot.

## Known limits
- Vendor modules are official 4.19.157 builds: with v1 they will not load (vermagic). Audio, Wi-Fi, fingerprint and
  exFAT are built in, so this is harmless; `rmnet_shs`/`rmnet_perf` (mobile-data steering) and debug/TV/webcam modules
  are not available → mobile data works, slightly more CPU at high speed.
- Qualcomm perf HAL boost knobs that need WALT are absent (CASS instead).
- `fastboot boot` uses the dtb from the flashed vendor_boot (the porter's, 4 blobs) — the full install uses v1's dtb.
- Root manager: RKSU instead of ReSukiSU; KernelSU modules in /data/adb usually keep working, but the manager app and
  root hiding for banking apps must be re-checked.

## Sunday test (only after the power-key flex is fitted, so a hang can be power-cycled)
```sh
adb reboot bootloader                 # Mi fastboot
fastboot boot boot_v1.img             # temporary: nothing is written; a reboot returns to the old kernel
```
Check, in this order: boots to the lock screen → `uname -r` shows 4.19.325-perf+ → touch, display, Wi-Fi,
mobile data + calls, speaker/earpiece/mic, Bluetooth audio, camera (all lenses), fingerprint, NFC, charging,
`cat /proc/sys/net/ipv4/tcp_congestion_control` = bbr, uclamp files under `/dev/cpuctl/top-app/`, banking apps, root.
Then `bash tools/bench.sh after_kernel_v1` and compare.

## Permanent install (only if every check passed)
```sh
adb reboot bootloader
fastboot flash boot boot_v1.img
fastboot flash vendor_boot vendor_boot_v1.img
fastboot flash dtbo dtbo_v1.img
fastboot reboot
```
Rollback: flash the port's `boot.img`, `vendor_boot.img`, `dtbo.img` from `rom_extract/images/` the same way.
