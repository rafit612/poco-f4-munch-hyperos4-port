# Custom kernel work — POCO F4 (munch) HyperOS 4 port

**Status (2026-10-24): the phone runs the porter's kernel `4.19.325-zyndong-perf`. No custom kernel is installed.**
v1–v3 failed on the phone. v4 is built and packed but not tested; the next step is a RAM-only `fastboot boot` test.

Source: `rohmanurip/kernel_munch` branch `base` + `rsuntk/KernelSU`, AOSP clang 20 (r547379), full LTO.
Build tree: `~/kernel_build/src` (`out/` phone build, `out_qemu/` QEMU test build). Packing: `~/kernel_build/pack_kernel.sh <tag>`
(takes the port's boot ramdisk, vendor ramdisk and vendor cmdline unchanged; only kernel, dtb and dtbo change).

## Versions
| | Config | In-memory size | Result on the phone |
|---|---|---|---|
| porter (running) | not public | 57.7 MiB | boots |
| v1 | source `munch_defconfig` | 49.3 MiB | reached Android, then rebooted every time with `reboot,bpfloader-failed` until slot A was marked unbootable |
| v2 | porter's `/proc/config.gz` + extras | 64.2 MiB | hung before any log, no USB |
| v3 | v1 + tracing/BPF events, MEMCG, zram writeback, AUDIT, hardening | 52.4 MiB | hung before any log, no USB |
| v4 | v3 + crash safety (below) | 53.5 MiB | **not tested** |

All versions share the same `vendor_boot` (dtb) and `dtbo`; v1 booted Android with them, so the dtb is not the cause.

## What was found
- **v1:** Android 17's bpfloader needs `FTRACE`/`TRACEPOINTS`/`BPF_EVENTS`; without them it exits and init reboots.
- **`/proc/config.gz` is not the running config** on either kernel: `kernel/Makefile` embeds `arch/arm64/configs/stock_defconfig`.
  Check real features with symbols instead (`tools/kallsyms_dump.py` on an Image, or `/proc/kallsyms` on the phone).
- **The porter's kernel already runs every option v3 added** (MEMCG, AUDIT, stack protector, VMAP_STACK, hardened usercopy,
  tracing, uprobes), read from its live symbol table. Those options are not the cause by themselves.
- **v3 boots cleanly in QEMU**, like v1: all initcalls run, it stops only at "no root filesystem".
- **Why v2/v3 failed silently:** `PANIC_ON_OOPS` was off (the porter runs with `panic_on_oops=1`), so a crash left the
  kernel half-alive instead of rebooting, and this source's `ramoops_memreserve` keeps 0 bytes for oops records,
  so pstore was empty. The real crash reason is still unknown.
- Source bugs fixed on the way (patches in each `kernel_vN/` folder): zram writeback block API for 4.19 (0002),
  sched tracepoints for CASS/PELT (0003), kgsl stub trace (0004), UFS trace guard (0005), `nf_log.h` missing `;` (0006),
  `mm/Makefile` `$(DEBUG_KERNEL)` typo (0007). This source only builds the Wi-Fi/USB/IOMMU/SCSI tracepoint files with
  `DEBUG_KERNEL=y`; v3/v4 turn it on and turn its debug extras (SCHED_DEBUG, DEBUG_PREEMPT, RCU_TRACE) off.
- **Audio drivers are built into the porter's kernel** (`q6lsm_open`, `msm_lsm_ioctl` are core symbols in kallsyms),
  while the official vendor ships modules for kernel 4.19.157 (`vermagic=4.19.157-perf-g045c5942d886`). With this
  kernel, Google's "Hey Google" DSP model crash-loops the ADSP; official HyperOS 1 (official kernel + modules) does not.
  The image build works around it (`port_fixes/soundtrigger_fix/`); a future kernel should use the vendor's audio modules.
- Required settings learned the hard way: `QCA_CLD_WLAN_PROFILE="qca6390"`, only the `_munch` vibrator driver
  (`INPUT_AW8697_HAPTIC_MUNCH`), `MODVERSIONS` off (LTO link fails), `FRAME_WARN=0` (LTO linker flag), CPU masks
  little 15 / big 112 / prime 128.

## v4: crash-safe diagnostic build (`kernel_v4/`)
- `PANIC_ON_OOPS=y`, `PANIC_TIMEOUT=-1`: any kernel error reboots at once; with `reboot=panic_warm` the RAM survives.
- Soft-lockup detector with panic: a stuck CPU also reboots.
- Patch 0008: ramoops keeps 1 MB for oops/panic records (1 MB record, 2 MB console, 1 MB pmsg).
- If it keeps failing, the bootloader's retry counter runs out and it stops in fastboot by itself.
- After a failure: restore the port's kernel (below), boot, then read `/sys/fs/pstore/` for the exact crash.

Test plan (RAM only, nothing written to storage):
```sh
adb reboot bootloader
fastboot boot secure_build/kernel_v4/boot_v4.img   # uses the flashed vendor_boot/dtbo (the port's)
```

## Testing on the PC first (QEMU)
```sh
qemu-system-aarch64 -M virt,gic-version=3,virtualization=on -cpu cortex-a76 -smp 8 -m 2048 -nographic -no-reboot \
  -kernel ~/kernel_build/src/out_qemu/arch/arm64/boot/Image \
  -append "console=ttyAMA0 earlycon=pl011,0x9000000 loglevel=8 nokaslr initcall_debug"
```
The QEMU build is the same config plus `SERIAL_AMBA_PL011(_CONSOLE)` and `SERIAL_EARLYCON`. `virtualization=on` is required:
without it QEMU has no secure firmware and the first Qualcomm TrustZone call (`smc`) crashes. A clean run ends with
"VFS: Unable to mount root fs". The harmless "Unknown SOC ID" warning appears on every build.
QEMU cannot test Qualcomm hardware (UFS, SMMU, TrustZone services, display), so it finds generic bugs only.

## Phone snapshot (read-only copy, `~/kernel_build/phone_snapshot/`)
Taken 2026-10-24 from the running porter kernel: `/proc/kallsyms` (142,634 symbols), the live dtb (`/sys/firmware/fdt`),
dmesg, cmdline, iomem, sysctl, all 413 drivers on all buses, `partitions/` (72 kernel, boot-chain and firmware
partitions, both slots, each checked by SHA-256 on phone and PC; `verify.txt`) and `files/` (vendor firmware, modem/DSP/BT
firmware, 48 vendor modules, init/fstab/ueventd). Not copied on purpose: super, userdata, persist, modemst, fsg, keystore, frp.

Inventory (drivers, modules, firmware, subsystems: porter vs v4): `PHONE_KERNEL_INVENTORY.md`.

## Recovery (tested)
1. Mi fastboot: Volume Down + Power, **release both keys** when the fastboot screen shows (a held key keeps it there).
2. Flash the port's images; the 100 MB `vendor_boot.img` fails on this PC's USB link, so use the 1.6 MB copy without
   zero padding (`~/kernel_build/selftest_vboot.img`, byte-identical to the original's content):
```sh
fastboot flash boot rom_extract/images/boot.img
fastboot flash dtbo rom_extract/images/dtbo.img
fastboot flash vendor_boot ~/kernel_build/selftest_vboot.img
fastboot set_active a
fastboot reboot
```
3. The USB link drops mid-transfer on this port/cable (repeated disconnects in `journalctl -k`); a cut transfer leaves a
   half-written partition that fails to boot even with original images. Retry until each line says OKAY, use another
   port/cable, or `fastboot -S 16M`.
