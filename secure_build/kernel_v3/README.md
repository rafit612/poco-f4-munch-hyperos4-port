# Kernel v3 — failed, do not use

v1's config plus tracing/BPF events, MEMCG, zram writeback, AUDIT and hardening (52.4 MiB in memory).
On the phone (2026-10-24) it hung before any log, with no USB; in QEMU it boots cleanly. Because `PANIC_ON_OOPS` was off
and ramoops kept no oops records, the crash left no trace. Superseded by v4 (`../kernel_v4/README.md`, `../KERNEL.md`).
