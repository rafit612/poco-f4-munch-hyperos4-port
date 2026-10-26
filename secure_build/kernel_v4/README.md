# Kernel v4 — crash-safe diagnostic build (not tested on the phone)

v3 plus: `PANIC_ON_OOPS=y`, `PANIC_TIMEOUT=-1`, soft-lockup panic, and patch 0008 (ramoops keeps 1 MB for oops/panic
records). If it fails it reboots by itself instead of freezing, keeps the crash log in RAM (`reboot=panic_warm`), and the
bootloader stops in fastboot once its retries run out. Features: CASS + uclamp, PSI, BBR, zram writeback, tracing/BPF
events (needed by Android 17 bpfloader), MEMCG, AUDIT, hardening, KernelSU (rsuntk). 53.5 MiB in memory.

Files: `boot_v4.img` (port's ramdisk unchanged), `vendor_boot_v4.img` and `dtbo_v4.img` (identical to v1's, which booted
Android), `kernel_v4.config`, patches 0002–0008, `SOURCE.txt`, `SHA256SUMS`.

First test is RAM only (nothing written): `fastboot boot boot_v4.img`. After a failure, restore the port's kernel and
read `/sys/fs/pstore/`. Full history, QEMU method and recovery: `../KERNEL.md`.
