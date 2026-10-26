# Kernel v2 — failed, do not use

Built from the porter's `/proc/config.gz` (which turned out to be the source's `stock_defconfig`, not the running config)
plus FTRACE/BPF events, CASS, BBR and zram writeback. In-memory size 64.2 MiB.
On the phone (2026-10-24) it hung before any log, with no USB. Details and recovery: `../KERNEL.md`.
